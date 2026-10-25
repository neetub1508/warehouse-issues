# Functional conformance — R32 manufacturing shop floor (`r32-mfg-shop`)
Contract: `mfg-shop-floor` v0, `mfg-pdi-unit-registry` v0 (2026-10-25); R32 §12 rows of `mfg-production-order`, `mfg-production-receipt`, `mfg-qc-rework`, `mfg-costing-close`, `mfg-subcontracting` | Mode: audit (pre-build design; no manufacturing code)
Files reviewed: ~45 | File set: derived from the brief — `issues/p10-07…14` (R32 sections), `p10-05` (R32), `p10-20…24`; 7 mfg contracts; `DATA-MODEL.md` §2.7.10; `DECISIONS.md` D-13, D-20; `FRD-MFG.md` MD-11/41/47/48/49, FR-817/818; core `p8-06`, `p8-17`, `p8-18`, `p8-19`, `p8-21`, `p8-23`, `p8-30`, `lot-serial-status.contract.md`; trade `p9-20`, `p9-21`; PRD §9, §10, §12, §13.1; gap analysis (production/quality/samples); the ledger (133 PQS rows). Paths are relative to `/Users/bbhushan/work/git/workspace/warehouse-issues` at a244ff6.
Engines: Claude + GPT (gpt-6.1-sol, medium) — 10 both · 12 Claude only · 7 GPT only · 0 dropped

## Verdict
29 findings: 2 Critical, 14 High, 9 Medium, 4 Low. The happy path is specified, but most failure and exit paths are not: per-unit state, QC hold release, rework/scrap of units, cancellation, returns, and the sale event. MD-47 ("a booking is a confirmation") was adopted without changing the R22 confirmation rules it contradicts.

## Status reachability
| Status | In CHECK (D-10: none) | In contract T1 | Inbound | Outbound | UI | Verdict |
|---|---|---|---|---|---|---|
| Order `APPROVED` | n/a | R32 §12 only (`mfg-production-order.contract.md:301`), not in inventory (`:56-66`) | PRO-T1-40 | Release refused by PRO-GRD-12, because PRO-T1-08 starts only from `PLANNED` (`:85`, `:117`) | Specified | **F-005** |
| Order `SHORT_CLOSED` | n/a | `:303` only | PRO-T1-41 | terminal | — | inventory stale (**F-005**) |
| Batch `IN_PROGRESS`/`COMPLETED`/`CANCELLED` | n/a | `shop-floor:28` lists them | none | none | — | **F-006** |
| Job card `HELD_QC` | n/a | `shop-floor:50` | SFL-T1-16 | none | `release_hold` verb only | **F-003 dead end** |
| Job card `CANCELLED` | n/a | `shop-floor:28` | none | — | — | **F-006 unreachable** |
| Unit `PLANNED` / `AWAITING_PDI` | no home table | PUR-T1-01, -10 | defined | defined | — | **F-001 not representable** |
| PDI `REWORK` | n/a | PUR-T1-12 | yes | no return to `AWAITING_PDI` | — | **F-007** |
| Registry `BUILT` | n/a | PUR-T1-20 | same transaction as `IN_STOCK` | — | — | transient (Low, F-029) |
| Registry `SOLD` | n/a | PUR-T1-22 | no producer | — | — | **F-002 unreachable** |
| Registry `RETURNED` | n/a | PUR-T1-23 | yes | none (PUR-T1-21 starts only from `IN_STOCK`) | — | **F-004 dead end** |
| Registry `SCRAPPED` | n/a | no T1 row (only EC-01) | none | — | — | **F-004 unreachable** |
| Daily plan `DRAFT`/`PUBLISHED` | n/a | SFL-T1-30 | yes | terminal | Specified | OK (actuals: F-024) |

## Findings

### F-R32MS-001 — Critical · Unreachable state: a unit not yet received into FG has no stored lifecycle
- Contract row: PUR-T1-01, PUR-T1-10, PUR-GRD-04, PRC-GRD-30 · Source: Both
- Evidence:
  - `issues/p10-21.md:21` creates base serials with status `PLANNED`, "not stock". But core serials are created "at its location" (`lot-serial-status.contract.md:55`), and `current_status_code` points at stock statuses (`DATA-MODEL.md:548`, `:860`). No core task seeds a `PLANNED` status; p10-02 seeds only `SAMPLE`.
  - `AWAITING_PDI` (`mfg-pdi-unit-registry.contract.md:38`) is stored in no table: `whm_pdi_records` holds `OPEN…SIGNED`, and registry rows start at receipt (`DATA-MODEL.md:2216`, `:2218`).
  - Job cards are per batch (`:2209`), and no unit × stage row exists. So "serials that completed the last stage" (`mfg-production-receipt.contract.md:286`) and "which unit was rejected at stage n" cannot be computed.
- What a user experiences: PDI eligibility, receipt serial checks and rework counts per unit are unanswerable before the unit is received.
- Fix: add an MFG unit WIP table (unit serial → order, batch, current stage, state `PLANNED / IN_PROCESS / AWAITING_PDI / REWORK / SCRAPPED / RECEIVED`, rework count). Keep it out of the core stock-status model, or have core register a non-stock serial state explicitly.

### F-R32MS-002 — Critical · Unreachable state: registry `SOLD`; the invoice hand-off has no consumer
- Contract row: PUR-T1-22, FR-817 · Source: Both
- Evidence:
  - `issues/p10-23.md:9` and `:20` expect "invoice ref + date per shipped serial through the core hand-off". The port methods (`p10-23.md:21`) are lookup and replacement only.
  - p9-20 writes the acknowledgement only to `wht_so_line_billings` (`issues/p9-20.md:24`). p8-23 returns the invoice number only as the acknowledgement's `externalDocumentRef` (`issues/p8-23.md:52`).
  - MFG may not read `wht_` tables (MD-08). Proposal lines carry `serial_no` but no bound-part snapshot (`p9-20.md:17`), while PRD §12 wants each invoice line to carry the chassis and part serials (`PRD…txt:313`).
- What a user experiences: an invoiced vehicle stays `DISPATCHED`. With the default `warranty_starts_at = SALE`, warranty never starts.
- Fix: in core, declare an invoice-acknowledgement event or port that carries a serial → invoice ref/date mapping. Make MFG an idempotent consumer of it and keep the `UNIT_NOT_DISPATCHED` retry. Name the producer (accounting adapter p8-23, or trade p9-20) and the consumer.

### F-R32MS-003 — High · Dead-end state: `HELD_QC`
- Contract row: SFL-T1-14/16/17, QRW-T1-20/21 · Source: Both
- Evidence: a booking enters `HELD_QC` (`mfg-shop-floor.contract.md:50`). Start/Resume accept only `READY`/`PAUSED` (`:48`), and Complete accepts only `STARTED` (`:51`). QRW-T1-21 releases quantities but never changes the card status (`mfg-qc-rework.contract.md:256`). `whm_job_cards:release_hold` (`issues/p10-20.md:38`) appears in no transition.
- What a user experiences: after the first-piece or patrol PQC is accepted, the rest of the batch cannot be booked or completed.
- Fix: add `HELD_QC → STARTED` on the inspection's final event, with an aggregate rule when several inspections are open. Define or remove `release_hold`.

### F-R32MS-004 — High · Dead end / unreachable: registry `RETURNED` and `SCRAPPED`
- Contract row: PUR-T1-21, -23, PUR-EC-01 · Source: Both (SCRAPPED found by Claude)
- Evidence:
  - `mfg-pdi-unit-registry.contract.md:44` dispatches only from `IN_STOCK`. `:46` sets `RETURNED` and promises "the next dispatch". No row leads from `RETURNED` back to stock or to scrap.
  - `SCRAPPED` has no T1 row. `:116` (EC-01, "unit scrapped after binding") assumes a registry row that does not exist before receipt.
  - PRD §12 sends returns "to Rework / FG / Scrap" (`PRD…txt:75`).
- What a user experiences: a returned vehicle can never be resold, and a scrapped vehicle never shows as scrapped.
- Fix: add `RETURNED → IN_STOCK` (customer return posted to FG, re-PDI required), `RETURNED/IN_STOCK → SCRAPPED` (scrap movement), and a pre-receipt scrap path through the F-001 table.

### F-R32MS-005 — High · Unguarded/unreachable: order `APPROVED` / `SHORT_CLOSED` not merged into the base ladder
- Contract row: PRO-T1-40/41, PRO-GRD-12, PRO-T1-08/20 · Source: Both
- Evidence:
  - The inventory (`mfg-production-order.contract.md:56-66`) and the identity row (`:32`) lack both statuses; the columns exist (`DATA-MODEL.md:2232`).
  - PRO-T1-08 starts only from `PLANNED` (`:85`), so PRO-GRD-12 (`:117`) refuses release of an `APPROVED` order.
  - Cancel (`:97`) does not list `APPROVED`. "An edit of an APPROVED order returns it to PLANNED" (`:301`) contradicts PRO-GRD-12, which allows edits only in `PLANNED`.
  - PRD flow: `PRD…txt:7`.
- What a user experiences: with the default `MTS_ONLY`, a make-to-stock order is approved and then cannot be released or cancelled.
- Fix: amend T1 1.1/1.2 — `From` of PRO-T1-08/09/20 includes `APPROVED`; edit while `APPROVED` per F-008; add `SHORT_CLOSED` to the inventory as terminal.

### F-R32MS-006 — High · Unreachable: batch and job-card exits; order cancel/unrelease leaves batches, cards and serials orphaned
- Contract row: SFL T1, PRO-T1-12/15/20, PRO-GRD-10 · Source: Both
- Evidence:
  - Batch `IN_PROGRESS`/`COMPLETED`/`CANCELLED` and card `CANCELLED` (`mfg-shop-floor.contract.md:28`) have no transitions.
  - Unrelease and Cancel (`mfg-production-order.contract.md:89`, `:97`) cancel MRQs but not batches, cards or `PLANNED` serials.
  - PRO-GRD-10 (`:115`) and PRO-T1-15 (`:92`) list `PRODUCTION_STAGE` but not the new `PRODUCTION_STAGE_CONSUMPTION`, and do not count a started job card or assigned serials as "postings".
- What a user experiences: an order with started cards can be unreleased. Its chassis numbers stay consumed but attached to nothing, and stage consumption never moves the order to `IN_PROGRESS`.
- Fix: add batch/card cancel effects on PRO-T1-12/20; refuse unrelease or cancel once any card has started or a serial is assigned; add `PRODUCTION_STAGE_CONSUMPTION` to PRO-T1-15 and PRO-GRD-10; define the batch rollup transitions.

### F-R32MS-007 — High · Dead end: no way back after PDI rework, and no scrap of a unit before receipt
- Contract row: PUR-T1-12, QRW-T1-22, PUR-GRD-04 · Source: Claude
- Evidence:
  - PDI `REWORK` (`mfg-pdi-unit-registry.contract.md:40`) creates a rework card "at the originating (or a named earlier) operation" (`mfg-qc-rework.contract.md:257`). Nothing returns the unit to `AWAITING_PDI` or reruns the later stages.
  - No void or release of the `PLANNED` serial of a rejected or scrapped unit (`issues/p10-21.md:22` covers spoiled plates only).
  - After `max_rework_cycles` (`REWORK_LIMIT_REACHED`) the unit has no exit.
- What a user experiences: a vehicle sent back from PDI never comes back to PDI, and a write-off unit blocks receipt of its batch.
- Fix: add rework card complete → re-run the following stages → `AWAITING_PDI` (attempt n+1); add a unit-scrap transition (and release of its bindings) for the limit-reached case.

### F-R32MS-008 — High · Permission/segregation weaker than core: approvals bypass the p8-30 engine
- Contract row: PRO-T1-40/42, PUR-T1-14 · Source: Both
- Evidence: `issues/p8-30.md:34` requires production order release and PDI clearance to use the engine. It enforces maker/submitter/prior-level exclusion, with ADMIN refused too (`:37`), and handles amendments as new revisions (`:39`). MFG uses direct `:approve` and `:approve_shortage_release` checks (`mfg-production-order.contract.md:301`, `:304`) and signer ≠ inspector only (`mfg-pdi-unit-registry.contract.md:42`). Routings do use the engine (`mfg-shop-floor.contract.md:41`). D-20 item 18 ("one approval engine for every document type") is `DECISIONS.md:704-705`.
- What a user experiences: configured approval levels and value bands do not apply to production orders or PDI, and an ADMIN can self-approve.
- Fix: register document types `WHM_PRODUCTION_ORDER`, `WHM_SHORTAGE_RELEASE` and `WHM_PDI` with the engine. Its final approval drives PRO-T1-40/42 and PUR-T1-14. Editing after approval becomes an amendment.

### F-R32MS-009 — High · Guard bypass: generic confirmations skip job-card controls
- Contract row: QRW-T1-01, SFL-GRD-06/08 · Source: GPT
- Evidence: WS-328 and WS-324 **Confirm** still record confirmations, with operator validity only (`mfg-qc-rework.contract.md:72`, `:95`). Job-card sequencing and crew authorisation are SFL-GRD-06/08 (`mfg-shop-floor.contract.md:71`, `:73`).
- What a user experiences: an unauthorised operator, or an out-of-sequence booking, goes in through the old screen.
- Fix: refuse a generic confirmation on a `uses_job_cards` order (`409`) and route all of them through the job-card booking service.

### F-R32MS-010 — High · Guard missing: QC completion acts before result approval
- Contract row: QRW-T1-21, PUR-T1-14 · Source: GPT
- Evidence: PQC transfers output "on completion" (`mfg-qc-rework.contract.md:256`). Core p8-19 sets `result_approval_status = PENDING` on Complete and refuses disposition until approval (`issues/p8-19.md:25`). PDI Sign has no approved-result guard (`mfg-pdi-unit-registry.contract.md:42`).
- What a user experiences: an unapproved PQC result releases the next stage, and an unapproved PDI result can be certified.
- Fix: drive transfer, receivability and signing from a single "result final" event (approved, or approval not required). Define what happens on Return.

### F-R32MS-011 — High · Guard/effect conflict: MD-47 adopted without changing the R22 confirmation rules
- Contract row: QRW-UNR-02, QRW-GRD-02, QRW-T4-02, QRW-GRD-07 vs SFL-T1-16/18 · Source: Claude
- Evidence:
  - QRW-UNR-02 says "a confirmation posting a movement" never happens (`mfg-qc-rework.contract.md:111`), while a booking (= a confirmation, `FRD-MFG.md:670`) posts stage consumption (`mfg-shop-floor.contract.md:114`).
  - QRW-GRD-02 refuses any booking on an order operation already `CONFIRMED` (`:91`): batch 1's final booking blocks batch 2.
  - The milestone rule QRW-T4-02 (`:153`) confirms earlier operations across all batches.
  - SFL-T1-18 cancel (`shop-floor:52`) omits QRW-GRD-07, "inspected confirmation" (`:96`).
- What a user experiences: the second batch of any order cannot be booked at an operation the first batch finished.
- Fix: amend QRW §1 so `is_final`/`CONFIRMED`/milestone apply per (order operation × batch) for job-card orders; remove or scope QRW-UNR-02; have SFL-T1-18 cite QRW-GRD-07.

### F-R32MS-012 — High · Guard missing: a failed stock re-PDI leaves the old certificate valid
- Contract row: PUR-GRD-05, PUR-T1-12/14, QRW-UNR-20 · Source: GPT
- Evidence: a certificate is superseded only on a new Sign (`mfg-pdi-unit-registry.contract.md:42`). The dispatch guard checks for a `VALID` certificate signed within N days (`:58`). Stock-unit `REWORK` uses a rework job card (`issues/p10-22.md:22`), while rework of received stock must use a rework order (`mfg-qc-rework.contract.md:262`).
- What a user experiences: a vehicle that just failed its stock re-PDI can still be dispatched on last month's certificate.
- Fix: suspend the certificate when a stock PDI opens or fails; send a stock-unit `REWORK` through a rework order, then a fresh PDI.

### F-R32MS-013 — High · Cross-entity effect missing: stage consumption is outside genealogy and the material pool
- Contract row: SFL-T4-02, PRC-T4-05, CST pool · Source: GPT
- Evidence: stage-consumed lines are excluded from the receipt backflush (`issues/p10-20.md:25`). Genealogy inputs are receipt-backflushed and store-issued lots only (`mfg-production-receipt.contract.md:176`). The pool `P_I` is store issues only, and `B_r` is the receipt's own backflush only (`mfg-costing-close.contract.md:106-110`).
- What a user experiences: a recall misses stage-backflushed lots, and FG cost understates material until the settlement dumps the difference.
- Fix: add stage-consumption movement values to the pool (as `B_stage`) and their lots to PRC-T4-05 inputs. Reverse both on cancel-booking.

### F-R32MS-014 — High · Cross-entity effect missing: a part replacement does not update the live binding
- Contract row: PUR-T1-24, PUR-GRD-07 · Source: GPT
- Evidence: the only effect is a `whm_unit_part_replacements` row (`mfg-pdi-unit-registry.contract.md:47`), holding text serials (`DATA-MODEL.md:2219`). PUR-GRD-07 requires the old serial to be currently bound (`:60`).
- What a user experiences: after replacing A with B, lookup still shows A, and a later B → C replacement is refused with `PART_NOT_BOUND`.
- Fix: replacement atomically unbinds the old serial and binds the new one (a `whm_unit_bindings` row, external serial allowed) and keeps the history.

### F-R32MS-015 — High · Guard missing: job-card receipt not bounded by last-stage output; PDI receipt status unstated
- Contract row: PRC-GRD-30, MD-49 · Source: Claude
- Evidence: PRC-GRD-30 (`mfg-production-receipt.contract.md:286`) checks the batch and serials but caps the quantity of a non-serial batch at nothing tied to the last card's transferred good output. MD-49 (`FRD-MFG.md:672`) and `issues/p10-22.md:24` say PDI'd units are "received allocatable — no second final QC", but PRC-T4-20 (`:288`) says "in the receipt status", and FR-644's `QC_HOLD` rule is not overridden.
- What a user experiences: FG can be received for stages never booked, and PDI'd vehicles may land in `QC_HOLD` and need a second QC.
- Fix: add `received ≤ last operation's good transferred out` for job-card orders; state receipt status `AVAILABLE` for `pdi_required` items.

### F-R32MS-016 — High · Data gap (Ind AS 2 ¶16): abnormal conversion time cannot be represented
- Contract row: CST-T4-22 · Source: Both
- Evidence: the rule is at `mfg-costing-close.contract.md:257`. `whm_order_conversion_costs` has no abnormal flag (`DATA-MODEL.md:2230`), and the booking has no time classification (`issues/p10-20.md:24`).
- What a user experiences: idle or downtime minutes are absorbed into FG stock, against the rule.
- Fix: add an `is_abnormal` / time-category column on conversion rows, derived from the reason code; exclude those rows from absorption and hand them over separately.

### F-R32MS-017 — Medium · Dead end: shortage-release request has no reject or withdraw, and runs as a second pending track
- Contract row: PRO-T1-42, PRO-T1-09/10/11 · Source: Claude
- Evidence: `mfg-production-order.contract.md:304` says it "waits". There is no reject or withdraw row, and it sits beside the release-approval pending state (`:86-88`) with no stated combined rule.
- Fix: one pending state per order with approve / reject / withdraw, through the engine (F-008).

### F-R32MS-018 — Medium · Effect missing: booked rework/rejected quantities and rejected WIP have no defined outcome
- Contract row: SFL-T1-16, SFL-GRD-07, QRW-T4-03/04 · Source: Claude
- Evidence:
  - PRD §9.2: "rejected units go to a rework job card" (`PRD…txt:17`). Only PQC/PDI `REWORK` creates one (`mfg-qc-rework.contract.md:257`).
  - SFL-GRD-07 (`shop-floor:72`) leaves `rework` out of the input bound.
  - A stage reject pre-fills the FG receipt's `REJECTED` quantity (`mfg-qc-rework.contract.md:154-155`): a half-built part would be received as rejected FG. PRD 10-27 says "scrap".
- Fix: define booking rework → rework card; rejected stage output → scrap or MRB disposition on the work-in-progress item, not an FG `REJECTED` pre-fill.

### F-R32MS-019 — Medium · Costing gaps: normal-capacity under-absorption missing, two absorption sources, stale R22 rows
- Contract row: CST-T4-20/21, CST-T4-10, A6 · Source: Claude
- Evidence:
  - `normal_capacity_minutes_per_month` (`DATA-MODEL.md:2232`) is used by no rule. Ind AS 2 ¶13 requires unabsorbed fixed overhead to be expensed; CST-UNR-20 (`:258`) names under-absorption but nothing computes it.
  - p8-23's `WhbProductionCostChargeProvider` supplies actual wages and overhead "for labour + overhead absorption" (`issues/p8-23.md:35`), alongside rate × minutes absorption (CST-T4-20, `:255`).
  - R22 CST-T4-10 (`:170`) and A6 (`:44`) still say "recorded, not absorbed".
- Fix: choose one absorption source; add a period under-absorption computation and hand-off; amend CST-T4-10 and A6.

### F-R32MS-020 — Medium · Two warranty truths: core serial vs MFG registry
- Contract row: PUR-T1-21/22 vs LSS-T4-01 · Source: Claude
- Evidence: core records `sold_to_counterparty_id` and warranty start/end on despatch (`lot-serial-status.contract.md:109`, `DATA-MODEL.md:860`). The registry defaults warranty start to the sale date (`FRD-MFG.md:487`, `:610`).
- Fix: state which one is authoritative; either the registry writes core's warranty fields, or core's are suppressed for unit-serial items.

### F-R32MS-021 — Medium · Guard missing: re-split after serials are assigned at release
- Contract row: SFL-T1-12, PUR-T1-01 · Source: Claude
- Evidence: re-split is guarded only by "no job card started" (`mfg-shop-floor.contract.md:46`). `assign_at = RELEASE` assigns serials at release (`issues/p10-21.md:21`).
- Fix: also refuse re-split once serials are assigned, or void and reassign them.

### F-R32MS-022 — Medium · Missing UI entry point: type-approval maintenance
- Contract row: PUR-T2-05, PUR-GRD-06 · Source: GPT
- Evidence: `whm_type_approvals:create,edit,delete` (`issues/p10-23.md:34`), but the screens are a read grid and a report (`:27-32`). Dispatch depends on a valid approval (`:23`).
- Fix: add a Type Approvals tab or screen (Department reference) with validity and certificate attachment.

### F-R32MS-023 — Medium · NCR / vendor-ppm integration; ledger 10-38 reason inaccurate
- Contract row: QRW-T4-20 · Source: Both
- Evidence:
  - p8-17 already auto-raises an NCR on any `IN_PROCESS` `REJECT` (`issues/p8-17.md:28`), so QRW-T4-20 (`mfg-qc-rework.contract.md:261`) duplicates it.
  - p8-21 line-ppm counts only store returns (`issues/p8-21.md:19`).
  - PDI has no NCR source, although PRD wants "NCR for every reject" (`PRD…txt:61`).
- Fix: QRW-T4-20 should cite NCR-T1-01 rather than raise its own NCR; add PQC NCR quantities to the ppm source; add a `PDI` NCR source.

### F-R32MS-024 — Medium · Screen drift: daily-plan actuals ignore order and batch
- Contract row: SFL-T1-30 · Source: GPT
- Evidence: plan lines may carry order and batch, but the actual is summed over work centre × item (× shift) only (`issues/p10-24.md:21`; `DATA-MODEL.md:2222`).
- Fix: match actuals to the plan line's own dimensions.

### F-R32MS-025 — Medium · Screen drift: traceability report misses PRD columns and filters
- Contract row: PUR-T5-03 · Source: Both
- Evidence: PRD wants "chassis → part serial → batch → MRN → PO → vendor" and filters by date, plant, item, vendor/customer (`PRD…txt:102-103`). WS-392 has no `batchNo`, `mrnNumber` or `poNumber` columns, and filters only `serialOrLot` and `direction` (`issues/p10-23.md:32-33`).
- Fix: add those columns and the PRD filters.

### F-R32MS-026 — Low · Screen drift: closure view
- Source: Claude
- Evidence: PRD §9.3 says closure shows planned vs actual quantity, material and time variance, rejection % and cost per unit (`PRD…txt:20`). The close modal and WS-329 show only the residual and variance % (`mfg-costing-close.contract.md:184`).
- Fix: add these to the close modal, read from the WS-337 registers.

### F-R32MS-027 — Low · Guard gaps at job-card start
- Source: Claude
- Evidence: SFL-T1-14 (`shop-floor:48`) checks neither the order hold flag (PRO-GRD-11) nor operator authorisation. Authorisation is checked only at booking (`:73`); PRD §9.2 says operators must be "authorised for that stage" (`PRD…txt:11`).
- Fix: cite PRO-GRD-11 and SFL-GRD-08 (on the starting user) at start.

### F-R32MS-028 — Low · Stale references and traceability debt
- Source: Claude
- Evidence:
  - p10-09 is "Blocked on … OD-43 (no absorption)" (`issues/p10-09.md:98`), and its Closes still says "C4d (recorded, not absorbed)" (`:74`). The p10-13 trap still cites OD-43 (`:73`).
  - The MD-41 row (`FRD-MFG.md:664`) lacks the MD-48 narrowing note.
  - D-13 "Mobile is not optional" (`DECISIONS.md:295`) is not marked superseded by D-20 item 5.
  - The reopened tasks' R32 sections do not list the PRD rows they close (D-20 item 6): p10-05 (9.1-02/03/09/18-21/24, C1, C12), p10-08 (9.2-18…20, 10-12/13/21/27/36, C6), p10-09 (9.3-08), p10-13 (9.3-06, 10-43, 13.1-Q2/Q3/P5/P7/P8), p10-22 (10-23, 10-29).
- Fix: amend the text only.

### F-R32MS-029 — Low · Data-model details
- Source: Claude
- Evidence:
  - `whm_production_batches` and `whm_pdi_certificates` declare uk(`warehouse_id`, …) without a `warehouse_id` column (`DATA-MODEL.md:2208`, `:2217`).
  - No last-return timestamp exists for PUR-GRD-05.
  - MD-47 (`FRD-MFG.md:670`) omits `rejection_reason_code_id`.
  - `BUILT` is never observable as a separate state.
- Fix: amend DATA-MODEL §2.7.10.

## Dropped after verification
- None. Every GPT-only claim was re-checked against its cited line and held: p8-30:34-39, p8-19:25, p8-21:19, receipt:176, costing:106-110, p10-23:21/27-34, p10-24:21.

## Remediation backlog
| Finding | Files to touch | Migration | Shared registries | Parity apply-to | Contract |
|---|---|---|---|---|---|
| 001 | DATA-MODEL §2.7.10; p10-21; p10-22; p10-07; core lot-serial-status | amend V562070 (new unit WIP table) | stock-status vs MFG state decision | core serials | PUR T1/T4, PRC-GRD-30 |
| 002 | p8-23; p9-20; p10-23; accounting-handover contract | amend V562090 | core ack event/port | trade, accounting adapter | PUR-T1-22, TSO-T4-17 |
| 003 | p10-20; p10-08 | none | `release_hold` verb | — | SFL T1, QRW-T1-21 |
| 004 | p10-23; mfg-pdi-unit-registry | none | — | core customer return (p8-11/RMA) | PUR T1 |
| 005 | p10-05; mfg-production-order | V562220 (status values) | — | — | PRO 1.1, PRO-T1-08/09/20 |
| 006 | p10-05; p10-20; p10-21 | none | movement-type list in PRO-GRD-10 | — | PRO-T1-12/15/20, GRD-10; SFL T1 |
| 007 | p10-22; p10-08; p10-21 | V562070/080 | — | — | PUR T1, QRW-T1-22 |
| 008 | p10-05; p10-22; p8-30 | V563220/V563080 seeds | approval doc types | core approval engine | PRO-T1-40/42, PUR-T1-14 |
| 009 | p10-08; p10-20 | none | — | WS-328, WS-324 | QRW-T1-01 |
| 010 | p8-19; p8-06; p10-08; p10-22 | none | result-final callback | core QC | QRW-T1-21, PUR-T1-14 |
| 011 | p10-08; p10-20; mfg-qc-rework | V562060 | — | — | QRW §1, QRW-UNR-02 |
| 012 | p10-22; p10-08 | V562080 | certificate status `SUSPENDED` | — | PUR-GRD-05, PUR T1 |
| 013 | p10-20; p10-07; p10-09 | V562260 | — | base genealogy | SFL-T4-02, PRC-T4-05, CST pool |
| 014 | p10-23; p10-21 | V562090 | — | — | PUR-T1-24 |
| 015 | p10-07 | none | — | — | PRC-GRD-30, PRC-T4-20 |
| 016 | p10-09; p10-20; p10-02 | V562260 | DOWNTIME / idle reason mapping | — | CST-T4-22 |
| 017 | p10-05 | V562220 | — | — | PRO-T1-42 |
| 018 | p10-20; p10-08 | none | `PRODUCTION_REJECTION` context | — | SFL-T1-16, QRW-T4-03/04 |
| 019 | p10-09; p8-23 | V562260 | — | accounting adapter | CST-T4-10/20/21, A6 |
| 020 | p10-23; lot-serial-status | none | — | core serials | PUR-T1-21/22 |
| 021 | p10-20 | none | — | — | SFL-T1-12 |
| 022 | p10-23 | V562090/V563090 (grid, menu, next free in V56xxxx) | filterUtils scope `WAREHOUSE_MFG_TYPE_APPROVAL` | — | PUR-T5-03 |
| 023 | p10-08; p8-17; p8-21; ledger | none | `NCR_SOURCE_TYPE` + `PDI` | core quality | QRW-T4-20, QRG-T5-01 |
| 024 | p10-24 | none | — | — | SFL-T5-04 |
| 025 | p10-23 | V562090 grid columns | WAREHOUSE_MFG_UNIT_TRACE scope | — | PUR-T5-03 |
| 026 | p10-09; p10-05 | none | — | — | PRO-T1-21 UI |
| 027 | p10-20 | none | — | — | SFL-T1-14 |
| 028 | p10-09; p10-13; FRD-MFG; DECISIONS; p10-05/08/22 | none | — | — | none |
| 029 | DATA-MODEL | V562060/080/090 | — | — | none |

No new migration versions are allocated; each amendment folds into the version the task already names.

## Ledger check (PQS, 133 rows: 80 NEW, 34 AMEND, 19 NO-CHANGE)
- Every non-COVERED PQS matrix row for §9, §10, §13.1 is either in the ledger or owned by a core p8 task (10-11, 10-19, 10-30, 10-37 are IQC rows owned by core). No orphan rows.
- **NO-CHANGE reason that does not hold: 10-38.** The reason "PQC supplier-caused reject raises it (QRW-T4-20)" is wrong: p8-17 auto-raises for every reject, and QRW-T4-20 is a duplicate. The reason is also incomplete, because PDI failures raise no NCR (F-023).
- 10-39 holds through p8-17.
- 9.4-06 and C11 hold under D-20 item 5, but D-13 is unamended (F-028).
- 9.1-15, 10-31, 10-32, 10-35 (p8-06 evidence store), 10-40, 10-42/44/45, 13.1-Q1/Q4/Q5/Q6 (p8-21), BEYOND 5 (p8-20), BEYOND 7 (p8-06 first-article) and BEYOND 8 (p8-17 `CUSTOMER_COMPLAINT`) hold. They establish who owns the work; F-010 and F-023 cover the integrations still missing.
- 19 AMEND/NEW rows name a task whose R32 section never lists the row ID (F-028).

## Parity (C10)
- Mobile: none — out of scope by the brief and D-20 item 5 (D-13 conflict noted in F-028).
- Apply-to: warehouse-manufacturing; core warehouse (p8-17/19/21/23/30, lot-serial-status, outbound despatch); warehouse-trade p9-20. The dealer vertical is fenced (D-20 item 4).

## In code, not in contract
- No MFG code exists yet. Two things in the design are not covered by the contracts: the core `whb_serials` warranty fields (F-020) and p8-23 `WhbProductionCostChargeProvider` (F-019).

## Contract quality
- RE-VERIFY items (VIN check digit, Form 22 fields, VAHAN layout) were not validated.
- Outside this area: p8-23 `INVOICE_REQUEST` on despatch post and p9-20 `SALES_INVOICE` proposal on `demand_order.shipped` may propose two invoices per dispatch when trade is installed. Refer this to the trade/accounting reviewer.

## Referred to standards reviewer
- None.
## Fix record (2026-10-25)

Applied under `D-20` and `D-21` (items 3, 6, 8 for this area). Contract amendment rows dated 2026-10-25 name each finding. Paths are relative to the repository root.

| Finding | Files changed | Outcome |
|---|---|---|
| F-R32MS-001 | `DATA-MODEL.md` §2.7.10 (`whm_unit_wip` new; bindings / PDI / certificates / registry / job-card events keyed by `unit_wip_id`), §7.9 `V562070`, §8.1, §8.2, §8.4; `mfg-pdi-unit-registry` (`PUR-T1-01`…`-10`, `-20`, `PUR-UNR-05`, status columns); `mfg-shop-floor` (`SFL-T1-16`, `SFL-GRD-14`); `mfg-production-receipt` (`PRC-GRD-30`, `PRC-T4-20`); `FRD-MFG` FR-811, MD-49; `p10-21`, `p10-22`, `p10-07`, `p10-20` | done (`D-21` item 8) |
| F-R32MS-002 | `mfg-pdi-unit-registry` (`PUR-T1-22`, `PUR-GRD-10`, `PUR-EC-02`, `PUR-T4-05`); `p10-23`; `FRD-MFG` FR-817 — core `INVOICE_ACKNOWLEDGED` already declared in `p8-23` / `AHO-T1-17` by the core fixer; `p9-20` left to the trade fixer | done (`D-21` item 3) |
| F-R32MS-003 | `mfg-shop-floor` (`SFL-T1-16a`, `SFL-UNR-05`); `mfg-qc-rework` (`QRW-T1-21`); `p10-20` (`release_hold` removed), `p10-08` | done |
| F-R32MS-004 | `mfg-pdi-unit-registry` (`PUR-T1-07`, `-23`, `-25`, `-26`, `PUR-EC-01`); `p10-23` | done |
| F-R32MS-005 | `mfg-production-order` (§0, §1.1 `APPROVED` / `SHORT_CLOSED` / order approval pending, `PRO-T1-08`, `-09`, `-20`, `PRO-GRD-12`, §12 `PRO-T1-41`, `-46`); `p10-05` | done |
| F-R32MS-006 | `mfg-production-order` (`PRO-T1-12`, `-15`, `-20`, `PRO-GRD-10`); `mfg-shop-floor` (`SFL-T1-10a`…`-10c`, `-22`); `mfg-pdi-unit-registry` (`PUR-T1-08`); `p10-05`, `p10-20`, `p10-21` | done |
| F-R32MS-007 | `mfg-pdi-unit-registry` (`PUR-T1-07`, `-16`, `PUR-GRD-09`, `PUR-UNR-08`); `mfg-qc-rework` (`QRW-T1-22`, `QRW-GRD-20`); `p10-21`, `p10-22`, `p10-08` | done |
| F-R32MS-008 | `mfg-production-order` (`PRO-T1-09`…`-11a`, `PRO-GRD-09`, §12 `PRO-T1-40`, `-40a`, `-46`, `-47`); `mfg-pdi-unit-registry` (`PUR-T1-14`, `PUR-T2-03`); `document-approval` §0.1(e) `WHM_SHORTAGE_RELEASE`, `WHM_PDI` rows aligned (rows added by the core-approvals fixer); `p10-05` (`V563220` registrations), `p10-22` (`V563080`) | done (`D-21` item 6) |
| F-R32MS-009 | `mfg-qc-rework` (`QRW-GRD-16`, `QRW-T1-01`); `mfg-shop-floor` (`SFL-GRD-15`); `p10-08`, `p10-20` | done |
| F-R32MS-010 | `mfg-qc-rework` (`QRW-T1-21`, `-23`); `mfg-pdi-unit-registry` (`PUR-T1-12`, `-14`); `p10-08`, `p10-22` — wording aligned to `p8-19` `QIC-T4-02` (once-only `onDisposition` at result final, added by the core-quality fixer) | done |
| F-R32MS-011 | `mfg-qc-rework` (`QRW-T1-01`, `QRW-GRD-02`, `QRW-T4-02`, `QRW-UNR-02`); `mfg-shop-floor` (`SFL-T1-18`, `SFL-T4-02`); `FRD-MFG` MD-47; `p10-08`, `p10-20` | done |
| F-R32MS-012 | `mfg-pdi-unit-registry` (`PUR-T1-11`, `-15`, `PUR-GRD-05`, `PUR-UNR-07`, certificate `SUSPENDED`); `mfg-qc-rework` (`QRW-UNR-20`); `DATA-MODEL` (`whm_pdi_certificates`); `p10-22` | done |
| F-R32MS-013 | `mfg-costing-close` §1.5 (`P_S`); `mfg-production-receipt` (`PRC-T4-05`); `mfg-shop-floor` (`SFL-T4-02`); `FRD-MFG` MD-41; `p10-07`, `p10-09`, `p10-20` | done |
| F-R32MS-014 | `mfg-pdi-unit-registry` (`PUR-T1-24`, `PUR-GRD-07`); `DATA-MODEL` (`whm_unit_bindings` `binding_source`, `external_serial_value`; `whm_unit_part_replacements` binding ids); `p10-21`, `p10-23` | done |
| F-R32MS-015 | `mfg-production-receipt` (`PRC-GRD-32`, `PRC-T4-20`); `FRD-MFG` MD-49; `p10-07`, `p10-22` | done |
| F-R32MS-016 | `mfg-costing-close` (`CST-T4-22`); `mfg-shop-floor` (`SFL-T1-16`); `DATA-MODEL` (`whm_order_conversion_costs.is_abnormal`, `time_reason_code_id`; confirmation `idle_minutes`, `idle_reason_code_id`); `p10-09`, `p10-20` — every `DOWNTIME` idle minute is abnormal, so `p10-02` needs no reason mapping | done |
| F-R32MS-017 | `mfg-production-order` (§1.1 one pending track, `PRO-T1-11`, `-11a`, §12 `PRO-T1-42`); `document-approval` §0.1(e); `p10-05` | done |
| F-R32MS-018 | `mfg-shop-floor` (`SFL-T1-16`, `-21`, `SFL-GRD-07`, `SFL-UNR-06`); `mfg-qc-rework` (`QRW-T4-03`, `-04`, `QRW-T1-21`, `-22`); `DATA-MODEL` (`rejected_open_quantity`); `p10-20`, `p10-08` | done |
| F-R32MS-019 | `mfg-costing-close` (A6, `CST-T4-10`, `-20`, `-23`, `CST-UNR-22`); `p8-23` (`WhbProductionCostChargeProvider` never an absorption source); `p10-09`, `p10-13` | done |
| F-R32MS-020 | `lot-serial-status` (`LSS-T4-01` + amendment); `mfg-pdi-unit-registry` (`PUR-T1-22`, `PUR-T4-04`, `PUR-UNR-06`); `FRD-MFG` FR-817; `p10-23` | done (`D-21` item 3) |
| F-R32MS-021 | `mfg-shop-floor` (`SFL-T1-12`); `p10-20` | done |
| F-R32MS-022 | `mfg-pdi-unit-registry` (`PUR-T2-05`, `PUR-T5-04`); `p10-23` (Type Approvals tab, scope `WAREHOUSE_MFG_TYPE_APPROVAL`, grid in `V562090`); `FRD-MFG` WS-391 row; `DATA-MODEL` (`whm_type_approvals.is_active`) | done (a WS-391 tab — no new menu leaf) |
| F-R32MS-023 | `mfg-qc-rework` (`QRW-T4-20`); `mfg-pdi-unit-registry` (`PUR-T1-12`); `p8-17` (`NCR_SOURCE_TYPE` + `PDI_INSPECTION`, raise mapping); `p8-21` (line ppm counts supplier PQC NCRs); `p10-08`, `p10-22`; ledger `r32-ledger-mfg.tsv` row PQS 10-38 | done |
| F-R32MS-024 | `p10-24`; `mfg-shop-floor` (`SFL-T5-04`) | done |
| F-R32MS-025 | `mfg-pdi-unit-registry` (`PUR-T5-03`); `p10-23` | done |
| F-R32MS-026 | `mfg-costing-close` (`CST-T5-10`); `mfg-production-order` (`PRO-T1-21` UI); `p10-05`, `p10-13` | done |
| F-R32MS-027 | `mfg-shop-floor` (`SFL-T1-14`); `p10-20` | done |
| F-R32MS-028 | `p10-09` (Closes, Blocked on), `p10-13` (trap), `FRD-MFG` MD-41, `DECISIONS.md` D-13 (superseded-in-part note), PRD row lists in `p10-05`, `p10-08`, `p10-09`, `p10-13`, `p10-22` | done |
| F-R32MS-029 | `DATA-MODEL` (`whm_production_batches.warehouse_id`, `whm_pdi_certificates.warehouse_id`, `whm_unit_registry.last_returned_at`, no stored `BUILT`); `FRD-MFG` MD-47 (`rejection_reason_code_id`); `mfg-pdi-unit-registry` (`PUR-T1-20`) | done |

29 done, 0 superseded. No new task files; no new migration versions (`whm_unit_wip` folds into `V562070`, the other columns into the versions their tasks already claim). Task Functional-contracts lines of `p10-05`, `-07`, `-08`, `-13`, `-20`, `-21`, `-22`, `-23` gained the contracts whose rows now cite their FRs (check-15).
