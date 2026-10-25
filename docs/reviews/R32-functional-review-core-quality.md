# Functional conformance — r32-core-quality
Contract: quality-ncr-capa-deviation, qc-inspector-calibration, status-stores (v0) + R32 rows of gate-entry, incoming-inspection-sampling, receipt-qc-putaway, mrn-authorisation, material-requisition, store-issue-return (v0) | Mode: **audit (pre-build design)**
Files reviewed: 34 (25 design files at warehouse-issues `a244ff6` + 9 classic code/migration files) | File set: derived from brief
Engines: Claude + GPT (gpt-6.1-sol, medium) — 6 both · 26 Claude only · 12 GPT only · 1 dropped

Design paths are relative to `/Users/bbhushan/work/git/workspace/warehouse-issues`; code paths are relative to `/Users/bbhushan/work/git/workspace/classic`. `LEDGER` = `/private/tmp/claude-501/-Users-bbhushan-work-git-workspace-classic/d8d47f73-78d6-4e9a-ba94-3c5238790e76/scratchpad/r32-ledger-core.tsv`. Mobile is out of scope (user rule; D-20 item 5).

## Verdict
44 findings. Completeness is good: every FR from FR-690 to FR-717 lands in exactly one task, and every PRD §6 / §7 / §10 IQC and common clause maps to a ledger row. The work is not build-ready. The blockers are one upgrade lock-out, four guard bypasses, two dead-end states and four conflicts between new tasks and built code.

## Status reachability
| Status | In CHECK | In contract T1 | Inbound | Outbound | UI reachable | Verdict |
|---|---|---|---|---|---|---|
| NCR OPEN…PENDING_CLOSURE | no CHECK (service whitelist) | yes | NCR-T1-01…05 | approve / return / cancel | WS-690/691 | closure guards incomplete (F-005, F-021) |
| NCR CANCELLED from ACTION_PENDING | — | no | — | — | — | NCR of a reversed disposition cannot be cancelled (F-039) |
| CAPA ladder | no CHECK | yes | NCR-T1-09…12 | defined | WS-691 | OK |
| Deviation ladder | no CHECK | yes | DEV-T1-01…09 | consume / expire / revoke | WS-693 | site, unit and pending-expiry gaps (F-012, F-017, F-036) |
| Instrument OUT_OF_SERVICE / OUT_FOR_CALIBRATION | no CHECK | yes | QIC-T1-08/09 | **none** | WS-695 | **dead end** (F-004) |
| Calibration FAILED after ADJUSTED_PASS | derived | yes | QIC-T1-08 | only a second PASS | — | dead end (F-013) |
| Store return DEPARTMENT_APPROVED / VERIFIED | not in §1.1 | transition rows only | SIR-T1-13/14 | SIR-T1-15/16 | not in WS-272 actions | inventory drift (F-033); old T1-07 bypass (F-003) |
| MR excess pending after partial issue | — | MRQ-T1-27 from APPROVED only | — | — | — | unreachable (F-006) |
| Status-store SCRAP | no SCRAP status | SST-T1-01 trigger | — | — | — | unreachable (F-014) |

## Findings

### F-R32CQ-001 — Critical — Rank 1: the R32 defaults lock every built IQC flow on deploy
- Contract row: QIC-GRD-01, QIC-T1-03 · Source: **Both** (GPT: defaults conflict; Claude: lock-out)
- Evidence: `issues/p8-19.md:20` seeds `inspector_authorisation_required=true` and `result_approval_mode=ALL`, and V511552 seeds no `wh_qc_inspector_authorisations` rows. `QIC-GRD-01` (`docs/contracts/qc-inspector-calibration.contract.md:70`) refuses Start / Record / Complete without a grant. `docs/frd/FRD-STORES.md:686` gives the default as `false` and `:688` as `NONE`.
- What a user experiences: right after the upgrade, every inspector gets `403 INSPECTOR_NOT_AUTHORISED` on every built P1-14 / P8-05 / P8-06 inspection. QC stops until an admin grants everyone.
- Fix: settle one default, recorded in the FRD, task and contract. Either seed `false` / `NONE` on upgrade with `true` / `ALL` on new installs, or have V511552 back-fill grants from the current holders of `wh_quality_inspections:edit` / `:disposition`. Add the upgrade case to the acceptance criteria.

### F-R32CQ-002 — High — Rank 1: a rejected lot can still be released with only a reason
- Contract row: IIS-T1-09; DEV-UNR-01 · Source: Claude
- Evidence: `docs/contracts/incoming-inspection-sampling.contract.md:67` ("MRB use-as-is … reason … no new guard"). `issues/p8-18.md:43` keeps the reason-only release "for a `REJECT_LOT` override that does not depart from specification" — a contradiction, since a `REJECT_LOT` verdict *is* a departure. Built code: `WhQualityInspectionValidationService.java:700` `requireReason`.
- What a user experiences: an inspector releases a failed lot to stock without the QC Manager / Plant Head deviation that PRD §6 requires.
- Fix: route a release against a `REJECT_LOT` verdict through `ACCEPT_UNDER_DEVIATION`, or give it its own second-person approval. Amend IIS-T1-09.

### F-R32CQ-003 — High — Rank 1: old store-return posting bypasses the new chain
- Contract row: SIR-T1-07 vs SIR-T1-13…15 · Source: **Both**
- Evidence: `docs/contracts/store-issue-return.contract.md:66` still allows `SUBMITTED → POSTED`, and `:50` / `:119` (T2-05) still allow Post from `SUBMITTED`. The new chain is at `:72-75`. `issues/p8-11.md:73`.
- What a user experiences: a return posts at the declared quantity, with no department approval and no physical verification.
- Fix: mark SIR-T1-07 superseded and give a single rule for when a return may post, driven by `return_approval_steps`, always at the verified quantity.

### F-R32CQ-004 — High — Rank 1: an instrument that goes out of service can never come back
- Contract row: QIC-T1-08…10, QIC-GRD-08 · Source: Claude
- Evidence: `docs/contracts/qc-inspector-calibration.contract.md:62` (a FAIL sets `OUT_OF_SERVICE`), `:63` (RGP sets `OUT_FOR_CALIBRATION`). No row ever sets `IN_SERVICE` again, and `:77` requires `IN_SERVICE` for any reading.
- What a user experiences: once a gauge is sent out or fails, it is unusable for good — even after a passing calibration.
- Fix: a PASS / ADJUSTED_PASS calibration record, or the RGP return, sets `IN_SERVICE`. Add the T1 rows.

### F-R32CQ-005 — High — Rank 2: the person who raised an NCR can approve its closure
- Contract row: NCR-GRD-03 · Source: GPT (verified)
- Evidence: `docs/frd/FRD-STORES.md:681` ("closer ≠ raiser"). `docs/contracts/quality-ncr-capa-deviation.contract.md:87` excludes only the owner and the submitter, and `issues/p8-17.md:28` lets the owner be reassigned.
- What a user experiences: the raiser reassigns the NCR, someone else submits it, and the raiser then approves the closure.
- Fix: also exclude the immutable `raised_by`.

### F-R32CQ-006 — High — Rank 1: excess approval is stranded once the standard part is issued
- Contract row: MRQ-T1-27, MRQ-GRD-23 · Source: GPT (verified); Claude adds the engine point
- Evidence: `docs/contracts/material-requisition.contract.md:82` allows excess approval only from `APPROVED`. `:103` lets the standard part be issued first, which moves the header to `PARTIALLY_ISSUED` / `ISSUED` (`:72-73`). The excess is described as "an extra level of the `MATERIAL_REQUISITION` request" after that request has already been approved.
- What a user experiences: stores issues 8 of 10 units, and the 2 excess units can never be approved.
- Fix: track excess approval separately from issue progress (allowed in `APPROVED` / `PARTIALLY_ISSUED`) as its own engine request. Define what happens to the pending excess on reservation, close-short and cancel.

### F-R32CQ-007 — High — Rank 2: deviation port lets a user with view rights consume a deviation
- Contract row: DEV-T1-06/07 · Source: GPT (verified)
- Evidence: `issues/p8-18.md:30` requires `warehouse:orders:port` + `wh_quality_deviations:view` for consume / reverse. The manual path needs `wh_quality_inspections:disposition` (`quality-ncr-capa-deviation.contract.md:76`). Port verbs need the mutating permission (`docs/DECISIONS.md:653`).
- What a user experiences: a manufacturing caller with only view rights draws down an approved concession.
- Fix: check a mutating verb on `actingUserId` for consume and reverse, and re-authorise on replay.

### F-R32CQ-008 — High — Rank 3: emergency issue cannot be used on the default setting
- Contract row: SIR-T1-10/12, SIR-GRD-03/11 · Source: **Both**
- Evidence: `issues/p8-10.md:79-80`; `docs/contracts/store-issue-return.contract.md:84`, `:92` (emergency needs `direct_issue_allowed`, default false). PRD `docs/reference/PRD-…txt` §7.2 ("no direct issue … except emergency issue … auto-creates the MR").
- What a user experiences: with the default, nobody can make an emergency issue. Switching it on also allows plain direct issues, which create no post-facto MR.
- Fix: add a separate `emergency_issue_allowed` setting (default true). When `direct_issue_allowed=false`, `EMERGENCY` is the only issue kind allowed without a requisition, and it always creates the post-facto MR.

### F-R32CQ-009 — High — Rank 3: under `DEDICATED_LOCATIONS`, MRN putaway hits the status-store transfer guard
- Contract row: SST-T1-01, SST-GRD-04, MRA-T4-02 · Source: **Both** (GPT flagged the missing leave rule under contract quality)
- Evidence: `docs/contracts/status-stores.contract.md:42` ("leaving … hands over to putaway") and `:54` (a transfer out that keeps its status is refused). `docs/contracts/mrn-authorisation.contract.md:111` changes status `MRN_PENDING → AVAILABLE` "at the location(s) holding it", then raises a putaway.
- What a user experiences: authorised stock is `AVAILABLE` and can be allocated or picked while it sits in the Quarantine Store. The putaway out of that location is the transfer `SST-GRD-04` refuses.
- Fix: the leaving `STATUS_CHANGE` carries its own location leg (to the receiving or putaway staging location). Scope `SST-GRD-04` to stock still in the store's bound status, and amend MRA-T4-02.

### F-R32CQ-010 — High — Rank 4: non-stock inspection outcomes reach production before result approval
- Contract row: QIC-T1-03…06, IIS-GRD-07a · Source: GPT (verified)
- Evidence: `WhQualityInspectionService.java:609-620` calls `onDisposition` when Complete runs, for non-stock sources. `issues/p8-19.md:25` blocks only Disposition.
- What a user experiences: an in-process reject or accept moves production on while the QC Manager approval is still pending.
- Fix: hold the callback until the result is `APPROVED` (call it immediately only when `NOT_REQUIRED`), and make it exactly-once across Return and re-complete.

### F-R32CQ-011 — High — Rank 4: a second reject on the same line is not added to the NCR
- Contract row: NCR-T1-01, NCR-GRD-01 · Source: GPT (verified)
- Evidence: `issues/p8-17.md:20` (one live NCR per line), `:28` (NCR quantity = the rejected quantity), `:54` (a second disposition raises none). A line can be dispositioned several times (`WhQualityInspectionLine.java:275-282`).
- What a user experiences: 12 units rejected, then 8 more, and the NCR still shows 12.
- Fix: the NCR quantity accumulates across dispositions through idempotent detail rows. Define what happens when the NCR is already `PENDING_CLOSURE` or `CLOSED`.

### F-R32CQ-012 — High — Rank 4: a site-restricted deviation can be used at another site
- Contract row: DEV-GRD-05 · Source: GPT (verified)
- Evidence: `issues/p8-18.md:19` (`warehouse_id` nullable = every site); `:30` (`findApplicable` has no site or company argument); `quality-ncr-capa-deviation.contract.md:95`.
- What a user experiences: a concession approved for plant A accepts material at plant B.
- Fix: add company and site to applicability and to the port signature, and re-check them under the lock.

### F-R32CQ-013 — High — Rank 4: the non-holding periodic re-test is refused by the built STOCK source
- Contract row: IIS-T1-15, IIS-T3-03 · Source: GPT (verified)
- Evidence: `issues/p8-06.md:80` (hold is optional, on `AVAILABLE` lots). `WhStockInspectionSource.java:117-120` refuses any status that is not QC-held.
- What a user experiences: with `retest_holds_stock=false`, the job opens inspections it then cannot start.
- Fix: specify a STOCK inspection path that does not hold the stock, or require the hold.

### F-R32CQ-014 — Medium — Rank 1: the "Scrap Store" cannot be reached from a QC disposition
- Contract row: SST-T1-01, SST-GRD-02 · Source: Claude
- Evidence: `docs/contracts/status-stores.contract.md:42` lists disposition `SCRAP` as a trigger. The built SCRAP disposition writes off to the virtual `SCRAP` location (`WhQualityInspectionDispositionService.java:225-251`). `SST-GRD-02` (`:52`) forbids virtual locations, and no `SCRAP` stock status exists (`V500005__…stock_statuses…sql:130-140`). Store-return SCRAP lands as `DAMAGED` (`store-issue-return.contract.md:137`).
- What a user experiences: QC-scrapped material never shows in a Scrap Store, and "Scrap Store" and "Damaged Store" can only be the same `DAMAGED` row.
- Fix: state that the Scrap Store is the `DAMAGED` row and that a QC `SCRAP` disposition is a write-off; remove `SCRAP` from the SST-T1-01 triggers. Or seed a SCRAP status (D-20 #16 decision).

### F-R32CQ-015 — Medium — Rank 1: an adjusted instrument stays FAILED
- Contract row: QIC-T1-07 · Source: Claude
- Evidence: `issues/p8-20.md:28`: FAILED is "`as_found_in_tolerance = false` and not followed by a PASS". An ADJUSTED_PASS record with as-found false (the normal adjust-and-return case) is itself the latest record.
- What a user experiences: a gauge that was found off, adjusted and certified is still refused until a second calibration.
- Fix: FAILED = latest result `FAIL`. As-found false drives only the QIC-T4-01 impact list.

### F-R32CQ-016 — Medium — Rank 2: Verify posts stock with only the `:verify` permission
- Contract row: SIR-T1-14 · Source: Claude
- Evidence: `docs/contracts/store-issue-return.contract.md:73` ("POSTED when STORE_APPROVAL is off", actor `:verify`).
- What a user experiences: a store keeper without `:post` writes an `ISSUE_RETURN` movement.
- Fix: posting at Verify requires `:post` as well.

### F-R32CQ-017 — Medium — Rank 4: deviation limits have no unit rule
- Contract row: DEV-GRD-04 · Source: **Both**
- Evidence: `issues/p8-18.md:19-20`, `:30` (the limit has a `uom_code`; usages and the port have none). IQC quantities are in receipt-line units (`WhQualityInspectionDispositionService.java:109`).
- Fix: use base-UoM limits and usages, converted and frozen on each usage.

### F-R32CQ-018 — Medium — Rank 4: turning off `defect_code_required` breaks automatic NCRs
- Contract row: NCR-GRD-01 · Source: GPT (verified)
- Evidence: `issues/p8-17.md:20` (`defect_code_id NOT NULL`), `:25`, `:29`.
- What a user experiences: the reject passes validation, then the NCR insert fails and the disposition rolls back.
- Fix: refuse that settings combination, or use a seeded `UNCLASSIFIED` defect code.

### F-R32CQ-019 — Medium — Rank 4: the line-rejection event needs a supplier the user has not picked yet
- Contract row: IIS-T4-07 vs IIS-GRD-16 · Source: Claude
- Evidence: `incoming-inspection-sampling.contract.md:141` (event carries the origin GRN / MRN / PO, written in the disposition transaction); `:98` (with two candidate GRNs the user picks one later, at *Raise supplier return*); `issues/p8-07.md:62`.
- Fix: when the trace is ambiguous, write the event at the user's pick, or pick at disposition. Apply the same rule to NCR-T4-02.

### F-R32CQ-020 — Medium — Rank 4: an NCR can close with no CAPA at all
- Contract row: NCR-GRD-02, NCR-T1-05 · Source: Claude
- Evidence: `quality-ncr-capa-deviation.contract.md:62` (submit from `UNDER_INVESTIGATION`), `:86` (blockers only cover existing actions). PRD §10: "NCR for every reject: … CAPA, owner, due date, closure". Also T2-02 (`:112`) lets submit happen only from `ACTION_PENDING`, which contradicts T1-05.
- Fix: add a setting `ncr_capa_required_severities` (default CRITICAL, MAJOR) and reconcile T1-05 with T2-02.

### F-R32CQ-021 — Medium — Rank 4: the status-store guard covers only manual transfers
- Contract row: SST-GRD-03/04 · Source: Claude
- Evidence: `docs/contracts/status-stores.contract.md:53-54` (manual transfer only); partial uniqueness per (site, status) at `:52`.
- What a user experiences: putaway or replenishment suggestions can place `AVAILABLE` stock in LOC-REJ. A single "Quarantine Store" location bound to `QC_HOLD` and `MRN_PENDING` makes "that store's status" ambiguous.
- Fix: the writer check applies to every movement and every putaway suggestion. Say whether one location can be bound to several statuses.

### F-R32CQ-022 — Medium — Rank 4: dangerous-goods segregation vs status-store relocation
- Contract row: RQP-GRD-46 vs SST-T1-01 · Source: Claude
- Evidence: `receipt-qc-putaway.contract.md:191` (DG items only into a DG store, for any transfer); `status-stores.contract.md:42` (relocation inside the posting).
- What a user experiences: rejecting a lithium-battery lot fails, because the Rejected Store is not a DG store.
- Fix: refuse a status-store binding to a non-DG location for DG items (SST-GRD-02), or define per-class status stores.

### F-R32CQ-023 — Medium — Rank 4: the approved-vendor check blocks samples from prospective suppliers
- Contract row: RQP-GRD-44 · Source: Claude
- Evidence: `issues/p1-13.md:280` (PO, blind **or non-PO** receipts); `issues/p8-03.md:90` (`SAMPLE_IN`); `issues/p8-06.md:79` (first article).
- What a user experiences: a new vendor's sample — the step that gets the vendor approved — is refused `SUPPLIER_NOT_APPROVED_FOR_ITEM`.
- Fix: exempt `SAMPLE_IN` (and optionally `FREE_OF_COST_IN`) and route them to `FIRST_ARTICLE`.

### F-R32CQ-024 — Medium — Rank 4: the periodic re-test holds reserved stock
- Contract row: IIS-T1-15 · Source: Claude
- Evidence: `issues/p8-06.md:80` (moves the lot's quantity to `QC_HOLD`); no rule for reserved quantity or open picks.
- Fix: hold only unreserved quantity, or say how reservations and picks are released.

### F-R32CQ-025 — Medium — Rank 4: automatic IQC skips QUARANTINE receipts
- Contract row: IIS-T1-11 · Source: GPT (verified)
- Evidence: `issues/p8-06.md:77` (only `QC_HOLD`); `WhQualityInspectionValidationService.java:151` (QC-held = `QC_HOLD` + `QUARANTINE`); FR-704 says "every QC-held line".
- Fix: use the shared `QC_HELD_STATUSES` set.

### F-R32CQ-026 — Medium — Rank 4: per-serial readings escape the calibration guards
- Contract row: QIC-GRD-07…09, QIC-T4-01 · Source: GPT (verified)
- Evidence: `issues/p8-06.md:78` (`instrument_id`, no frozen due date); `issues/p8-20.md:22`, `:31` (only `wh_quality_inspection_results`).
- Fix: apply the same guards and frozen columns to serial results, and include them in the impact list.

### F-R32CQ-027 — Medium — Rank 4: FRD says accept-under-deviation releases to AVAILABLE, bypassing the MRN
- Contract row: DEV-T4-01 · Source: Claude
- Evidence: `docs/frd/FRD-STORES.md:685` ("released `AVAILABLE`") vs `quality-ncr-capa-deviation.contract.md:134` (`MRN_PENDING` routing).
- Fix: amend FR-696 to the MRN routing.

### F-R32CQ-028 — Medium — Rank 4: result approval sits outside the one approval engine
- Contract row: QIC-T1-03…05 · Source: Claude
- Evidence: `issues/p8-19.md:25` ("a fact on the inspection"); D-20 item 2-18 ("one approval engine for every document type"); not listed in `document-approval.contract.md` §0.1 (`:36-49`).
- Fix: register an `INSPECTION_RESULT` type (`SINGLE_LEVEL`), or record the exemption in D-20.

### F-R32CQ-029 — Medium — Rank 4: P8-18 seeds an approval rule before the engine tables exist
- Contract row: DAP §0.1 · Source: Claude
- Evidence: `issues/p8-18.md:24` (V511551 "the engine's default rule"); the engine tables are created in V511600 (`issues/p8-30.md:5`). A fresh install runs V511551 first.
- Fix: `DOCUMENT_DEFINED` levels come from the bean (`issues/p8-30.md:30`), so drop the seed wording, or move the seed after V511600.

### F-R32CQ-030 — Medium — Rank 4: the overlap guard on inspector grants does not work
- Contract row: QIC-GRD-06 · Source: Claude
- Evidence: `issues/p8-19.md:16` uses single-argument `COALESCE(...)` (a no-op). NULL scope columns never compare equal in an exclusion constraint, so "every site" grants never collide. `daterange(valid_from, valid_to)` is half-open, while `validTo` is shown as an inclusive date. No `btree_gist` extension is noted.
- Fix: `COALESCE(col, sentinel)`, `daterange(..., '[]')`, `CREATE EXTENSION IF NOT EXISTS btree_gist`.

### F-R32CQ-031 — Medium — Rank 4: a post-facto MR may have no eligible approver
- Contract row: MRQ-T1-28, MRQ-GRD-05 · Source: Claude
- Evidence: `material-requisition.contract.md:83` (created `SUBMITTED` inside the issue transaction); `:94` (Submit is refused with no eligible head or deputy).
- What a user experiences: the emergency issue post fails, or the MR waits for ratification forever.
- Fix: the emergency issue checks for an approver before posting, or the MR escalates to the stores manager.

### F-R32CQ-032 — Medium — Rank 6: the gate-photo default conflicts between FRD and task
- Contract row: GTE-GRD-17 · Source: GPT (verified)
- Evidence: `docs/frd/FRD-STORES.md:701` (required by default) vs `issues/p8-03.md:89` (default `false`).
- Fix: pick one and align the FRD, task and contract.

### F-R32CQ-033 — Medium — Rank 6: screen and inventory drift for issues, returns and NCR
- Contract row: SIR §1.1, §5.1/5.2; NCR §1.1 · Source: **Both**
- Evidence: `store-issue-return.contract.md:49-53` (no `DEPARTMENT_APPROVED` / `VERIFIED`); `:159` (no Department approve / Verify actions); `:150-152` (still a *Direct issues* tile; no `issueKind`, `acknowledgementStatus`, or emergency tile). SIR-GRD-01 (`:81`) has no `DEMAND_ORDER` resolver. NCR `ACTION_PENDING` / `UNDERTERMINED` vs FRD `CAPA_IN_PROGRESS` / `UNKNOWN` (`FRD-STORES.md:679`). Stage vocabulary differs between FR-697 (STOCK, no RETURN) and QRG-T5-05 (RETURN, no STOCK).
- Fix: update the inventories, T2, T5 columns / filters / tiles / exports and the vocabularies together.

### F-R32CQ-034 — Low — Rank 3: "Move existing" has no entry point
- Contract row: SST-T1-04 · Source: Claude — `status-stores.contract.md:45`; actor "stores", with no permission, endpoint or WS-697 action. Fix: add the verb, endpoint and action.

### F-R32CQ-035 — Low — Rank 4: sample status store does not exist on a core-only install
- Contract row: GTE-T4-07 · Source: Claude — no core sample status (`V500005…sql:130-140`); `issues/p8-03.md:90`. Fix: say that `SAMPLE_IN` uses the resolved receiving status until a sibling seeds a sample status, and how a sample status is left.

### F-R32CQ-036 — Low — Rank 4: pending deviations never expire; reversal on EXPIRED / REVOKED is undefined
- Contract row: DEV-T1-07, DEV-T3-01 · Source: Claude — `quality-ncr-capa-deviation.contract.md:77`, `:124`. Fix: refuse approval after `valid_to` and expire `SUBMITTED` / `LEVEL1_APPROVED` deviations; a reversal writes a `REVERSAL` usage without changing the status.

### F-R32CQ-037 — Low — Rank 4: per-serial RTV / SCRAP is described as going to REJECTED
- Contract row: IIS-T1-12 · Source: Claude — `issues/p8-06.md:78`, `incoming-inspection-sampling.contract.md:70` vs built RTV → `BLOCKED` and SCRAP → virtual (`WhQualityInspectionDispositionService.java:43-44`, `:225`). Fix: "each serial takes the disposition's target".

### F-R32CQ-038 — Low — Rank 7: a second "deviation" approval type for manufacturing
- Contract row: DAP §0.1 · Source: Claude — `document-approval.contract.md:49`, `issues/p8-30.md:34` list a manufacturing "deviation" type, while P8-18's `QUALITY_DEVIATION` is the one deviation that MFG consumes through the port. Fix: remove it.

### F-R32CQ-039 — Low — Rank 1: an NCR whose disposition was reversed, once in ACTION_PENDING, cannot be cancelled
- Contract row: NCR-T1-08 · Source: Claude — `issues/p8-17.md:47` vs `quality-ncr-capa-deviation.contract.md:65`. Fix: allow cancel from `ACTION_PENDING` (cancelling its open CAPA).

### F-R32CQ-040 — Low — Rank 7: p8-12 has two R32 sections, the second after the Definition of done
- Contract row: none · Source: Claude — `issues/p8-12.md:49`, `:66`, `:68`. Fix: merge them before the Definition of done.

### F-R32CQ-041 — Low — Completeness: ledger 6.5-02 "built" is false for lot / serial labels
- Source: GPT (verified) — `LEDGER` row 6.5-02 vs `issues/p8-12.md:51-56` (FR-739). Fix: map it to P8-12 FR-739.

### F-R32CQ-042 — Low — Completeness: ledger 10-25 "built IQC engine" is false
- Source: Claude — MRN / `MRN_PENDING` is planned in P8-08 #569; there is no `MRN_PENDING` in the classic code (grep: none in `warehouse*/backend/src/main`). Fix: change the reason to "planned P8-08".

### F-R32CQ-043 — Low — Completeness: ledger 7.1-16 / 7.1-18 name the wrong owners
- Source: Claude — gap rows (`R32-prd-gap-mr-issue-return-bom.md:51`, `:53`): the reason code is MFG #597 plus P8-09 `MRQ-GRD-23`; one-click PR needs the P9-04 #581 trade bean. Fix: correct the reasons.

### F-R32CQ-044 — Low — Completeness: 10-32 and 10-43 are missing from the core ledger
- Source: Claude — P8-19 closes 10-32 (`issues/p8-19.md:36`); P8-21 QRG-T5-05 partly closes 10-43, but `issues/p8-21.md:34` omits it. Fix: add both rows (10-43 split core / P10-13).

## Dropped after verification
- Claude: V500500 / V500501 / V500502 / V500504… below the applied V501236 would crash Flyway → `shared/docker/.env:34` and `platform/backend/src/main/resources/application.yml:113` set `out-of-order: true`, which the backend asserts, so this does not crash.

## Remediation backlog
These are design amendments only: no classic code, and no migration numbers beyond those the tasks already own.

| Finding | Files to touch | Migration | Shared registries | Parity apply-to | Contract |
|---|---|---|---|---|---|
| 001 | `issues/p8-19.md`, `docs/frd/FRD-STORES.md` FR-697/699 | V511552 (owned) | settings registry (P8-14) | P10-08 inspections | QIC-GRD-01, T1-03 |
| 002 | `issues/p8-18.md`, incoming-inspection-sampling | none | none | P10-08 PQC pass-under-deviation | IIS-T1-09 |
| 003, 016, 033 | `issues/p8-11.md`, `issues/p8-10.md`, store-issue-return | V511320/V511410 (owned) | `COMMON_FILTER_CONFIGS.WAREHOUSE_STORE_RETURN/_ISSUE` | none | SIR §1.1, T1-07/14, T2, T5 |
| 004, 015, 026, 030 | `issues/p8-20.md`, `issues/p8-19.md`, `issues/p8-06.md`, qc-inspector-calibration | V511502/V511503/V511505 (owned) | none | none | QIC-T1-07…10, GRD-06…09 |
| 005, 011, 018, 020, 039 | `issues/p8-17.md`, quality-ncr-capa-deviation, FRD FR-690/692 | V511500/V511550 (owned) | `document-approval` §0.1 | P10-08 NCR sources | NCR-T1, GRD-01…03 |
| 006, 031 | `issues/p8-09.md`, material-requisition | V511508 (owned) | DAP §0.1 | P8-10 queue | MRQ-T1-27/28, GRD-05/23 |
| 007, 012, 017, 027, 036 | `issues/p8-18.md`, quality contract, FRD FR-696, FRD port registry | V511501 (owned) | none | P10-06/P10-08 port callers | DEV-GRD-04/05, T1-06/07, T3-01 |
| 008 | `issues/p8-10.md`, FRD FR-535/714 | V511409 (owned) | settings registry | P8-09 post-facto MR | SIR-GRD-03/11 |
| 009, 014, 021, 022, 034, 035 | `issues/p8-22.md`, status-stores, mrn-authorisation, `issues/p1-15.md` | V511504/V511555 (owned) | none | none | SST-T1-01/04, GRD-02…04; MRA-T4-02 |
| 010 | `issues/p8-19.md`, incoming-inspection-sampling | none | none | P10-08 outcome resolvers | IIS-GRD-07a, QIC-T1-03 |
| 013, 024, 025, 037 | `issues/p8-06.md`, incoming-inspection-sampling | V511505/V511556 (owned) | none | none | IIS-T1-11/12/15 |
| 019 | `issues/p8-07.md`, incoming-inspection-sampling | V511316 (owned) | none | P9-12 vendor rating | IIS-T4-06/07, GRD-16 |
| 023 | `issues/p1-13.md`, receipt-qc-putaway | V511557 (owned) | none | P9 AVL bean | RQP-GRD-44 |
| 028, 029, 038 | `issues/p8-19.md`, `issues/p8-18.md`, `issues/p8-30.md`, document-approval | none | DAP §0.1 | P10 types | DAP §0.1 |
| 032 | FRD FR-712, `issues/p8-03.md` | none | settings registry | none | GTE-GRD-17 |
| 040–044 | `issues/p8-12.md`, `issues/p8-21.md`, `LEDGER` | none | none | none | none |

## Parity (C10)
- Mobile: none — out of scope by user rule and D-20 item 5 (`docs/DECISIONS.md:728`); tracked in the `needs-client-decision` issue.
- Siblings: warehouse-manufacturing (P10-06 / P10-08: NCR sources, deviation port, `producedByUserIds`, PQC result approval), warehouse-trade (P9-04 PR hand-off, P9-12 vendor rating, `ApprovedSupplierPolicy`). Dealer vertical fenced (D-20 item 4).

## In code, not in contract
- Complete calls the non-stock `onDisposition` immediately → `WhQualityInspectionService.java:609-620` — add it to QIC as a T4 row (F-010).
- Repeated per-line dispositions → `WhQualityInspectionLine.java:275-282` — NCR T4 accumulation row (F-011).
- `QUARANTINE` counts as QC-held → `WhQualityInspectionValidationService.java:151` — IIS-T1-11 (F-025).
- STOCK source refuses non-held stock → `WhStockInspectionSource.java:117` — IIS-T1-15 (F-013).

## Contract quality
- All three new contracts are v0 and unratified; no build exists. The NCR-OPEN-01 and DEV-OPEN-01 defaults are reasonable.
- Ledger: 175 rows checked against the PRD §6 / §7 / §10 IQC and common gap rows. Every clause in scope lands; four NO-CHANGE reasons do not hold (F-041…044).
- Not verified: `whb_items.qc_required` and the AVL type flag (P1-03 R32, unbuilt) — these are dependencies, not defects.

## Referred to standards reviewer
- None.
## Fix record (2026-10-25)

Paths relative to the design repo; `LEDGER` as above. `QNC` = `quality-ncr-capa-deviation`, `QIC` = `qc-inspector-calibration`, `IIS` = `incoming-inspection-sampling`, `SIR` = `store-issue-return`, `MRQ` = `material-requisition`, `SST` = `status-stores`, `MRA` = `mrn-authorisation`, `RQP` = `receipt-qc-putaway`, `GTE` = `gate-entry` (all `docs/contracts/*.contract.md`).

| Finding | Files changed | Result |
|---|---|---|
| F-R32CQ-001 | `issues/p8-19.md`, QIC (`QIC-GRD-01`, `-T1-03`, §7), FRD FR-697 / FR-699, `GLOBAL-SETTINGS-DECISIONS.md` (rows added by the approvals fixer), FRD WH-SC-728 | done (`D-21` item 7) |
| F-R32CQ-002 | `issues/p8-18.md`, IIS `IIS-T1-09`, QNC `DEV-UNR-03`, FRD FR-696 | done |
| F-R32CQ-003 | `issues/p8-11.md`, SIR §1.1, `SIR-T1-07` (superseded), `SIR-T2-05`, FRD FR-715, WH-SC-739 | done (`D-21` item 8) |
| F-R32CQ-004 | `issues/p8-20.md`, QIC `QIC-T1-11`, `-12`, FRD FR-700 | done |
| F-R32CQ-005 | `issues/p8-17.md`, QNC `NCR-GRD-03`, `NCR-T1-05`, FRD FR-692 | done |
| F-R32CQ-006 | `issues/p8-09.md`, MRQ `MRQ-T1-08`, `-27`, `MRQ-GRD-23`, §7, `DATA-MODEL.md`, FRD FR-713, WH-SC-738 | done — excess runs as a second `MATERIAL_REQUISITION` request with condition `excess_over_standard`; DAP §0.1 wording is the approvals fixer's |
| F-R32CQ-007 | `issues/p8-18.md`, QNC §0 + `DEV-T1-06`, `-07`, FRD FR-695 | done |
| F-R32CQ-008 | `issues/p8-10.md`, SIR `SIR-GRD-03`, `-11`, `SIR-T1-10`, `-12`, FRD FR-714, `GLOBAL-SETTINGS-DECISIONS.md`, `DATA-MODEL.md`, WH-SC-738 | done (`D-21` item 8) |
| F-R32CQ-009 | `issues/p8-22.md`, SST `SST-T1-05`, `SST-GRD-04`, MRA `MRA-T4-02` + §7, `issues/p8-08.md`, FRD FR-703, WH-SC-732, LEDGER 10-25 | done |
| F-R32CQ-010 | `issues/p8-19.md`, QIC `QIC-T4-02`, IIS `IIS-GRD-07a`, `DATA-MODEL.md` | done |
| F-R32CQ-011 | `issues/p8-17.md`, QNC `NCR-T4-04`, `NCR-GRD-01`, `DATA-MODEL.md`, FRD FR-690, WH-SC-720 | done (same-transaction increment, no detail table) |
| F-R32CQ-012 | `issues/p8-18.md`, QNC `DEV-GRD-05`, FRD FR-695 | done |
| F-R32CQ-013 | `issues/p8-06.md`, IIS `IIS-T1-15`, `IIS-T3-03`, `DATA-MODEL.md`, FRD FR-707 | done (`retest_holds_stock` withdrawn — always hold) |
| F-R32CQ-014 | `issues/p8-22.md`, SST `SST-T1-01`, `SST-T5-02`, FRD FR-703 | done |
| F-R32CQ-015 | `issues/p8-20.md`, QIC §1.1, FRD FR-700 | done |
| F-R32CQ-016 | `issues/p8-11.md`, SIR `SIR-T1-14`, `SIR-T2-05`, FRD FR-715 | done |
| F-R32CQ-017 | `issues/p8-18.md`, QNC `DEV-GRD-04`, `DATA-MODEL.md`, FRD FR-695 | done |
| F-R32CQ-018 | `issues/p8-17.md`, QNC `NCR-GRD-01`, `-02`, `DATA-MODEL.md`, FRD FR-692 | done (NCR defect code nullable, required at closure) |
| F-R32CQ-019 | `issues/p8-07.md`, IIS `IIS-GRD-16`, `IIS-T4-07`, QNC `NCR-T4-02`, `DATA-MODEL.md`, FRD FR-716 | done (pick at disposition) |
| F-R32CQ-020 | `issues/p8-17.md`, QNC `NCR-T1-05`, `NCR-T2-02`, `NCR-GRD-02`, FRD FR-692, `GLOBAL-SETTINGS-DECISIONS.md` | done |
| F-R32CQ-021 | `issues/p8-22.md`, SST `SST-GRD-02`, `-03`, `DATA-MODEL.md`, FRD FR-703 | done (one status per location) |
| F-R32CQ-022 | `issues/p8-22.md`, SST `SST-GRD-05`, `issues/p1-15.md`, RQP `RQP-GRD-46`, `DATA-MODEL.md` | done |
| F-R32CQ-023 | `issues/p1-13.md`, RQP `RQP-GRD-44` + §7, IIS `IIS-T1-14`, `issues/p8-03.md`, GTE `GTE-T4-07` | done (`SAMPLE_IN` exempt; `FREE_OF_COST_IN` checked) |
| F-R32CQ-024 | `issues/p8-06.md`, IIS `IIS-T1-15`, FRD FR-707 | done |
| F-R32CQ-025 | `issues/p8-06.md`, IIS `IIS-T1-11` | done |
| F-R32CQ-026 | `issues/p8-06.md`, `issues/p8-20.md`, QIC `QIC-GRD-07`, `-08`, `QIC-T4-01`, `DATA-MODEL.md`, FRD FR-700 | done |
| F-R32CQ-027 | FRD FR-696 | done |
| F-R32CQ-028 | `issues/p8-19.md` (engine wiring `INSPECTION_RESULT`), QIC `QIC-T1-03`…`-05`, FRD FR-699 | done (`D-21` item 6; DAP §0.1 row is the approvals fixer's) |
| F-R32CQ-029 | `issues/p8-18.md` (`V511551` seeds no rule; bean levels) | done |
| F-R32CQ-030 | `issues/p8-19.md`, QIC `QIC-GRD-06`, §1.1, `DATA-MODEL.md` | done |
| F-R32CQ-031 | `issues/p8-09.md`, `issues/p8-10.md`, MRQ `MRQ-T1-28`, SIR `SIR-T1-10`, FRD FR-713 | done |
| F-R32CQ-032 | FRD FR-712, GTE `GTE-GRD-17` + §7, `issues/p8-03.md`, `GLOBAL-SETTINGS-DECISIONS.md` | done (default `false`) |
| F-R32CQ-033 | SIR §1.1, T2, §5.1, §5.2, `SIR-GRD-01`; `issues/p8-10.md`, `issues/p8-11.md`; FRD FR-690, FR-697; QNC `QRG-T5-05` | done |
| F-R32CQ-034 | `issues/p8-22.md`, SST §0, `SST-T1-04`, `SST-T5-01` | done |
| F-R32CQ-035 | SST `SST-T4-02`, GTE `GTE-T4-07`, `issues/p8-03.md`, `issues/p8-22.md` | done |
| F-R32CQ-036 | `issues/p8-18.md`, QNC `DEV-GRD-07`, `DEV-T3-01`, `DEV-T1-07`, FRD FR-695 | done |
| F-R32CQ-037 | `issues/p8-06.md`, IIS `IIS-T1-12` | done |
| F-R32CQ-038 | — | superseded-by-D-21 (item 6: DAP §0.1 lists the complete type set with no manufacturing "deviation" type; DAP §0.1 and `issues/p8-30.md` are the core-approvals fixer's) |
| F-R32CQ-039 | `issues/p8-17.md`, QNC `NCR-T1-08`, FRD FR-690 | done |
| F-R32CQ-040 | `issues/p8-12.md` | done (one R32 section before the Definition of done — merged state verified) |
| F-R32CQ-041 | LEDGER 6.5-02 | done |
| F-R32CQ-042 | LEDGER 10-25 | done |
| F-R32CQ-043 | LEDGER 7.1-16, 7.1-18 | done |
| F-R32CQ-044 | LEDGER 10-32, 10-43 (new rows); `issues/p8-21.md` Closes | done |

Engine wiring (`D-21` item 6) written in the consumer tasks: `p8-08` (`MRN`), `p8-11` (`STORE_RETURN`), `p8-17` (`NCR_CLOSURE`), `p8-18` (`QUALITY_DEVIATION`), `p8-19` (`INSPECTION_RESULT`); `p8-30` and DAP §0.1 untouched.
