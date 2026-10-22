# R29 — functional review (Claude + GPT dual engine), area MFG

**Date** 2026-10-22 · **Reviewer** functional-reviewer, pre-build audit mode · **Dispositions** recorded in the area FRD §"R29 dispositions"

**Summary (≤200 words)**

I found 33 findings: 1 Critical, 14 High, 11 Medium and 7 Low. 8 came from both engines, 15 from Claude only and 10 from GPT only. I dropped none.

I did not write `/private/tmp/claude-501/-Users-bbhushan-work-git-workspace-classic/53f0e57a-69c7-42b1-a5aa-daa8c13be89a/scratchpad/FR-REVIEW-MFG.md`. My agent definition forbids report files, so the full report is below for you to save.

**Verdict: the end-to-end manufacturer flow does not work as designed.**

Top 5:
1. **F6 (Critical).** Subcontracted output is valued at 0. `JOB_WORKER` is a virtual location and the costing engine skips virtual lines (`WhbCostingEngine.java:257`). So the dispatched value leaves inventory, and the job-worker backflush carries no value. `P_I` counts store issues only.
2. **F3.** Reservations cannot exist at a `JOB_WORKER` location (`WhbStockPositionWriter.java:360`). So SUB-T1-03 cannot dispatch.
3. **F2.** A rework order cannot run. `WhbReservationService.create` refuses `REJECTED` stock, PRC-GRD-13 refuses consuming non-allocatable stock, and release always shows a shortage.
4. **F1.** A FIRMED MRP proposal becomes stuck after the next run: MRP-GRD-09 refuses to convert or dismiss it, yet it keeps counting as supply.
5. **F4.** Any MRQ that is `REJECTED` or `CLOSED` blocks the order's Cancel and Unrelease forever (PRO-GRD-10).

Engines: Claude + GPT (gpt-6.1-sol, medium) — 8 both · 15 Claude only · 10 GPT only · 0 dropped

---

# Functional conformance — warehouse-manufacturing (P10, MFG)
Contract: `docs/contracts/mfg-{bom,production-order,material-staging-issue,production-receipt,qc-rework,costing-close,subcontracting,mrp}.contract.md` (all v0 2026-10-22, unratified) | Mode: audit (pre-build)
Files reviewed: 52. That is 24 design files (FRD-MFG, FRD-STORES, 8 MFG contracts, material-requisition, movement-post-reverse and po-schedule-port contracts, issues p10-01…13) and 28 core code/migration files. | File set: derived from workflow
Design repo: `/Users/bbhushan/work/git/workspace/warehouse-issues` @ `e14159a`. Code: `/Users/bbhushan/work/git/workspace/classic` @ `65b41be8a6`.
Engines: Claude + GPT (gpt-6.1-sol, medium) — 8 both · 15 Claude only · 10 GPT only · 0 dropped

## Verdict
33 findings: Critical 1 · High 14 · Medium 11 · Low 7.

There is no MFG code yet. These findings are about the design, and about whether the reused core code supports what the design assumes. They are not runtime failures.

## What the reused core actually supports

| Design assumption | Core reality | Verdict |
|---|---|---|
| `VIRT-PRODUCTION/SCRAP/JOB_WORKER/COST_OF_SALES-<site>` exist per site | Seeded by `V500013:37-38,353-360`, and `WhbVirtualLocationProvisioner` creates them for new sites | holds |
| Reservations are HARD or SOFT, SOFT needs `expires_at`, holder is a quad | `V500033` CHECKs; `holder_system` and `holder_document_type` are FKs | holds, but `WAREHOUSE_MANUFACTURING` must be seeded in `whb_source_systems` (p10-01:104 does this) |
| Reservation on a `REJECTED` position | `WhbReservationService.java:186` uses non-allocatable admission and refuses it. Only `WhbAllocationService.java:212-228` with `VENDOR_RETURN` may name a status | **fails (F2)** |
| Reservation at a `JOB_WORKER` location | `V500006:132` makes it virtual; `WhbStockPositionWriter.java:360` gives virtual ATP = 0 | **fails (F3)** |
| Re-dating a SOFT reservation on reschedule | `WhbReservationService.java:212` can only extend to a later time | **partly (F18)** |
| A reservation "moves" at staging | There is no transfer or partial release. `consumedReservationIds` consumes the whole hold (`WhbMovementPostCommand.java:23`) | **partly (F17)** |
| `WhbMovementPostCommand` fields | No cost-object field (correct, MSI-UNR-06). Has `consumedReservationIds`, `costSourceLineId`, `unitCost`/`extendedCost`/`costBasis` | holds |
| Value of the order's output is stated by the caller | Holds when the output is a different item (VAS precedent `WhWorkOrderPostingService.java:78-93`). When the output is the same item it is overridden (`WhbCostingEngine.java:278-289`) | **fails for rework (F7)** |
| Pool and WIP value "in `VIRT-PRODUCTION`" | Virtual lines are never valued or layered (`WhbCostingEngine.java:257,568`) | **WIP lives only in MFG; F6, F20** |
| Value-only settlement | `WhbValueOnlyMovementPoster` with a `VALUE_OFFSET` counter works (landed-cost "+layer/+cogs/−whole" shape). The caller must call `restateLayerValue` (`WhbCostingEngine.java:952`) | **F8; CST-OPEN-04 can be closed (F30)** |
| Owning-module guard (`V525000:99-122`) | Present; `owning_module VARCHAR(30)` fits "warehouse-manufacturing"; codes ≤ 40 chars | holds |
| `LINE_SIDE` is "not pickable" | `whb_location_types` has no pickable column; allocation takes any physical stock-holding location (`WhbAllocationRepository.java:38`) | **F16** |
| Phantom guard (`V500089`) and `WhbMovementPostGuard` SPI | Both exist (`WhbMovementPostGuard.java:15`) | holds, but the MFG guard is unassigned (F5) |
| `whb_transformations` for genealogy | `transformation_type` is free text; `work_order_ref_type` FKs to document types; quantity must be > 0 | holds; reversal semantics still OPEN (PRC-OPEN-05) |
| Seams p8-xx (`CostObjectResolver`, `WhMaterialRequisitionPort`, `GatePassSourceResolver`, `WhReplenishmentSuggestionPort`, `JobWorkDispatchPort`, `PurchaseRequisitionHandoff`, `WhDemandOrderPort`) | **None exist in code yet** | dependency (F24) |

## Status reachability

| Status | In CHECK | In contract T1 | Inbound | Outbound | UI reachable | Verdict |
|---|---|---|---|---|---|---|
| BOM DRAFT/SUBMITTED/APPROVED/OBSOLETE | none (D-10) | yes | BOM-T1-01…09 | ladder | specified | ok |
| Order PLANNED | none | yes | PRO-T1-01…05, -11, -12 | release, cancel | specified | rework orders cannot release (F2) |
| Order RELEASED | none | yes | PRO-T1-08, -10 | posting, unrelease, cancel | specified | **cancel/unrelease stuck behind a REJECTED/CLOSED MRQ (F4)** |
| Order IN_PROGRESS / COMPLETED | none | yes | first posting / final receipt / complete | complete, reopen, close | specified | ok |
| Order CLOSED / CANCELLED | none | yes | settlement / cancel | terminal | specified | ok |
| Staging DRAFT…CLOSED/CANCELLED | none | yes | MSI-T1-02…08 | ladder + close short | specified | quantity formula wrong (F11) |
| Receipt DRAFT/PENDING_APPROVAL/POSTED/REVERSED/CANCELLED | none | yes | PRC-T1-01…13 | ladder | specified | ok |
| Settlement DRAFT/APPROVED/POSTED/REJECTED | none | yes | CST-T1-01…05 | ladder | specified | layers not restated (F8) |
| Dispatch DRAFT/DISPATCHED/CANCELLED | none | yes | SUB-T1-01…04 | ladder | specified | **dispatch blocked (F3)** |
| Proposal OPEN/FIRMED/CONVERTED/DISMISSED/SUPERSEDED | none | yes | MRP-T1-08, -11, -13…16 | ladder | specified | **FIRMED stuck after the next run (F1)** |
| MRP run QUEUED…SUPERSEDED | none | yes | MRP-T1-07…10 | ladder | system | ok |

## Findings

### F1 — High · Rank 1 (unreachable exit): a FIRMED proposal cannot be acted on once a later run completes
- Contract row: MRP-T1-08, MRP-GRD-09, MRP-N-08
- Source: Both
- Evidence: `docs/contracts/mfg-mrp.contract.md:77` keeps FIRMED proposals when their run is superseded. `:100` (GRD-09) requires a proposal to belong to the latest COMPLETED run. `:130` keeps counting FIRMED proposals as supply.
- What a user experiences: the planner firms a proposal and the nightly run completes. After that, Convert and Dismiss both return `409 MRP_PROPOSAL_STALE`, and the proposal suppresses real demand forever.
- Fix: GRD-09 should require "OPEN proposal of the current run, or any live FIRMED proposal of this site".

### F2 — High · Rank 1 (unreachable): the rework order cannot reserve, release or consume its REJECTED component
- Contract row: QRW-T4-07, PRO-T1-04, PRO-GRD-08, PRC-GRD-13, PRO-T4-02
- Source: Both
- Evidence: `mfg-qc-rework.contract.md:157` wants a HARD reservation on the REJECTED position. `WhbReservationService.java:186` uses ordinary admission, so ATP = 0 for a non-allocatable status (`WhbStockPositionWriter.java:356-366`). Only `VENDOR_RETURN` may name a status (`WhbAllocationService.java:212-228`). `mfg-production-receipt.contract.md:105` (PRC-GRD-13) requires an allocatable consumption status. `mfg-production-order.contract.md:113` (GRD-08) counts allocatable stock only, so the order always shows a shortage and BLOCK can never release it. The reservation is also made at PLANNED (`:81`), but PRO-T4-02 (`:182`) makes reservations at release.
- What a user experiences: WH-SC-636/638 fail. The QC `REWORK` disposition is refused, or the rework order can never be released or received.
- Fix: drop the reservation (REJECTED stock is not allocatable to anyone else anyway), or add a base-sanctioned named-status path. Make GRD-08 and PRC-GRD-13 honour `supply_stock_status_code`. Make one reservation timing rule.

### F3 — High · Rank 1 (unreachable): subcontract dispatch cannot move reservations to the JOB_WORKER position
- Contract row: SUB-T1-03, SUB-T4-01
- Source: Both
- Evidence: `mfg-subcontracting.contract.md:68,153` re-create HARD reservations at the job-worker position. `V500006__Create_whb_location_types.sql:132` defines JOB_WORKER as a virtual counterparty. `WhbStockPositionWriter.java:360` gives virtual ATP = 0. GPT also cites `V500087:100`, which rejects virtual-location reservations.
- What a user experiences: every dispatch is refused with `INSUFFICIENT_STOCK`, so WH-SC-645…648 cannot run.
- Fix: consume the reservations at dispatch and do not re-reserve. Job-worker stock is already excluded from allocation and MRP, and is guarded by the reconciliation (SUB-GRD-10).

### F4 — High · Rank 1 (dead end): Cancel and Unrelease are blocked forever by a REJECTED or CLOSED MRQ, and the contract contradicts itself
- Contract row: PRO-GRD-10, MSI-T1-14
- Source: Claude
- Evidence: `mfg-production-order.contract.md:115` refuses while any MRQ is "not CANCELLED". `material-requisition.contract.md:70` (Reject → REJECTED) and `:74` (Close short → CLOSED, possible with nothing issued) are terminal states that are not CANCELLED. `mfg-material-staging-issue.contract.md:82` cancels the MRQ *as an effect of* order cancel, but that cannot happen because the guard refuses cancel first.
- What a user experiences: a RELEASED order whose material request was rejected can never be cancelled or unreleased. The only way out is to post something and then complete short.
- Fix: in GRD-10, block only on an MRQ with Σ issued > 0. The order Cancel/Unrelease should cancel open MRQs through the port, as MSI-T1-14 says.

### F5 — High · Rank 2 (permission): no MFG `WhbMovementPostGuard`, so MFG movement types can be posted or reversed through the generic port
- Contract row: MPR-GRD-35, CST-UNR-01, SUB-UNR-02
- Source: GPT
- Evidence: `movement-post-reverse.contract.md:136` makes the owning module implement the guard. `WhbMovementPostGuard.java:15` says that with no bean, nothing is restricted. `issues/p10-02.md:42` and the other tasks never assign it.
- What a user experiences: a user with `whb_*:post` can post a `PRODUCTION_RECEIPT` or `PRODUCTION_SETTLEMENT`, or reverse a dispatch, outside its document. The rollups, pool and reconciliation then drift.
- Fix: in p10-02, add a guard bean that refuses `PRODUCTION_*`/`SUBCONTRACT_*` posts and reversals not sourced by their MFG document.

### F6 — Critical · Rank 4 (cost layers): a subcontracted processed item is received at zero value, and stock at the job worker is unvalued
- Contract row: SUB-T4-07, SUB-T4-05, CST §1.5, SUB-T1-08
- Source: Claude
- Evidence: the dispatch real line is relieved at AVCO. The JOB_WORKER line is virtual, and virtual lines are skipped by costing (`WhbCostingEngine.java:257`), so no layer exists at the job worker. The receipt backflush from JOB_WORKER to VIRT-PRODUCTION has only virtual lines, so `B_r` = 0. `P_I` (`mfg-costing-close.contract.md:105`) counts store issues only and excludes dispatch value. SUB-T4-07 (`mfg-subcontracting.contract.md:161`) asserts "pool = carried value of the sent inputs" without any mechanism. A recall (JOB_WORKER → store) has nothing relieved in its own movement, so the engine values it at the site's current method cost (`WhbCostingEngine.java:445-470`), not the dispatched value.
- What a user experiences: in WH-SC-647 the 190 `SHAFT-03P` arrive at about ₹0. Inventory valuation drops by the dispatched value. A recall re-enters at a different value.
- Fix: put the dispatch movement's relieved value into `P_I` for SUBCONTRACT orders. Recall should state `costSourceLineId` = the dispatch line (or a stated cost). Also decide (core, L-11) whether JOB_WORKER stock must stay valued.

### F7 — High · Rank 4 (cost): a same-item rework receipt loses the value of the extra components
- Contract row: QRW-T4-08, CST-T4-01
- Source: GPT
- Evidence: `mfg-qc-rework.contract.md:158`. A grain whose quantity nets to zero is treated as an internal move and keeps its current average, whatever cost is stated (`WhbCostingEngine.java:278-289`; VAS comment F460 at `WhWorkOrderPostingService.java:83-86`).
- What a user experiences: in WH-SC-638 the gasket's value is relieved but never reaches `PUMP-100`.
- Fix: post the extras' value as a value-only movement onto the rework output lot, or design the rework input/output so the grain does not net to zero.

### F8 — High · Rank 4 (cost layers): the settlement does not restate the on-hand cost layers
- Contract row: CST-T4-05/-06
- Source: GPT
- Evidence: `mfg-costing-close.contract.md:163-164` uses zero-quantity lines only. Zero-quantity lines are skipped (`WhbCostingEngine.java:257`). `restateLayerValue` (`:952`) is a caller obligation, followed by `WhLandedCostPostingService`.
- What a user experiences: the residual (WH-SC-641, ₹800) appears in the ledger, but later issues of those lots still relieve the old value.
- Fix: CST-T4-06 must lock the layers and call `restateLayerValue` per on-hand layer, using the landed-cost path.

### F9 — High · Rank 4 (calculation): MRP counts safety stock twice
- Contract row: MRP-N-03(d), MRP-N-09
- Source: GPT
- Evidence: `mfg-mrp.contract.md:125` adds safety stock as a requirement, and `:131` also restores projected stock up to safety. WH-SC-650 (`FRD-MFG.md:614`) expects 45; applying both rules gives 50.
- Fix: keep only one rule (N-09).

### F10 — High · Rank 4 (dependent demand): components of FIRMED MAKE proposals from earlier runs are never planned
- Contract row: MRP-N-04, MRP-N-08
- Source: Both
- Evidence: `mfg-mrp.contract.md:126` explodes only MAKE proposals "of this run", while `:130` counts FIRMED proposals as supply.
- Fix: explode every live FIRMED MAKE proposal into dependent demand.

### F11 — High · Rank 4 (guard): the staging quantity subtracts consumed stock twice
- Contract row: MSI-T1-02, MSI-GRD-03
- Source: GPT
- Evidence: `mfg-material-staging-issue.contract.md:70,90` use `required − staged + unstaged − consumed`. `consumed` includes backflush of stock that was staged (`FRD-MFG.md:244-245`).
- What a user experiences: required 100, staged 60, consumed 40 should leave 40 to stage, but the formula gives 0 and refuses.
- Fix: open to stage = required − (staged − unstaged) − ISSUE-consumed. Use one formula for generation and for the guard.

### F12 — High · Rank 4 (cross-entity): MRQ reservations are suppressed only when `reservationsFor` is non-empty
- Contract row: MRQ-T4-01, MSI-T4-04
- Source: GPT
- Evidence: `material-requisition.contract.md:129` versus `mfg-production-order.contract.md:182` (NONE, shortage or expired SOFT gives an empty list).
- What a user experiences: an order released short gets MRQ-owned holds when stock arrives. That breaks MD-16, and the order's close does not release them.
- Fix: suppress MRQ reservations whenever the cost-object type is `PRODUCTION_ORDER`.

### F13 — High · Rank 4 (cross-entity): cover expiry cannot withdraw a suggestion that trade has already turned into a PR
- Contract row: MRP-T3-04, MRP-N-08, POS-T1-31
- Source: Both
- Evidence: `mfg-mrp.contract.md:171` re-plans after cover expiry. `po-schedule-port.contract.md:185` allows withdrawal only from PROPOSED, and trade marks the suggestion CONVERTED at PR stage.
- What a user experiences: MRP proposes to buy the same quantity again, so it is bought twice.
- Fix: re-plan only after `withdrawExternal` succeeds. Count ACCEPTED/CONVERTED-to-PR suggestions as supply until a PO line references them or the PR is cancelled (read with `getSuggestionStatus`).

### F14 — High · Rank 4 (genealogy L-12): partial receipts lose the links to lots issued earlier
- Contract row: PRC-T4-05, FR-648
- Source: GPT
- Evidence: `mfg-production-receipt.contract.md:171` links only lots issued "since the previous receipt". `mfg-costing-close.contract.md:108` absorbs the issued pool across all receipts.
- What a user experiences: a lot issued before receipt 1 is not traced to the output of receipts 2 and 3. Recall misses that output, which is the unsafe direction.
- Fix: link each receipt to every issued lot of the order not yet fully consumed (over-inclusion).

### F15 — High · Rank 4 (guard conflict): the MTO output reservation is made at receipt while the output is in QC_HOLD
- Contract row: PRC-T4-08 vs QRW-T4-10
- Source: Both
- Evidence: `mfg-production-receipt.contract.md:174` versus `mfg-qc-rework.contract.md:160`. QC_HOLD is not allocatable (`WhbStockPositionWriter.java:360`).
- What a user experiences: the receipt post fails, or the reservation is skipped.
- Fix: amend PRC-T4-08 to reserve only when the output lands in an allocatable status. Otherwise reserve at QC release.

### F16 — Medium · Rank 4: line-side protection depends only on a reservation whose type is not stated
- Contract row: FRD §3.1 LINE_SIDE, MSI-T4-07, MSI-UNR-03
- Source: Claude
- Evidence: `FRD-MFG.md:141` says "not pickable for outbound", but `whb_location_types` has no such column (`V500006`). Allocation takes any physical stock-holding location (`WhbAllocationRepository.java:38`). MSI-T4-07 (`mfg-material-staging-issue.contract.md:141`) does not say HARD, and a SOFT hold expires (MD-23).
- What a user experiences: once a SOFT hold expires, a sales pick can take line-side stock (WH-SC-619 broken).
- Fix: make the line-side reservation always HARD and remove the "not pickable" type claim. Otherwise this needs a base column change.

### F17 — Medium · Rank 4: core has no way to "move" a reservation at staging
- Contract row: MSI-T4-07/-08, MSI-T4-09
- Source: Claude
- Evidence: there is no transfer or partial-release API (`WhbReservationService` offers create, release, extend and `releaseByHolder`). `consumedReservationIds` consumes a hold whole (`WhbMovementPostCommand.java:23`; `WhbReservationStore.java:232`).
- Fix: specify the pattern: consume the source hold, re-create the remainder at the source and create the line-side hold, all in one transaction. Never store reservation ids; `reservationsFor` always queries by holder.

### F18 — Medium · Rank 4: a SOFT reservation cannot be re-dated earlier
- Contract row: PRO-T4-02 (MD-23)
- Source: Claude
- Evidence: `WhbReservationService.java:212` — "to a later instant only".
- Fix: when a reschedule moves the end date earlier, release and re-create the reservation.

### F19 — Medium · Rank 4: output cost stated as `unit_cost` with basis `PRODUCTION_ACTUAL` breaks the exact split
- Contract row: CST-T4-01, CST-GRD-01, FR-654/655
- Source: Claude
- Evidence: `mfg-costing-close.contract.md:110,159`. The VAS precedent states `extendedCost` with a null basis (`WhWorkOrderPostingService.java:78-93`), because unit cost × quantity re-rounds and breaks the largest-remainder total. `PRODUCTION_ACTUAL` is not in `KNOWN_COST_BASES` (`WhbMovementTypeValidationService.java:46`).
- Fix: state `extendedCost` per output line and leave the basis as the type default.

### F20 — Medium · Rank 4: the abnormal-scrap value "to VIRT-SCRAP" cannot be represented in the ledger
- Contract row: CST-T4-03, FR-654
- Source: Claude
- Evidence: a SCRAPPED output line pair is virtual-only (`mfg-production-receipt.contract.md:167` (d)), and virtual lines carry no value (`WhbCostingEngine.java:257`).
- What a user experiences: the accounting handover never sees the abnormal loss. It exists only in `scrap_value` and WS-337.
- Fix: restate CST-T4-03 as an MFG-side record, or design a real-line representation.

### F21 — Medium · Rank 4: several stage actions on one line have no durable posting model
- Contract row: MSI-T4-06, MSI-OPEN-02
- Source: GPT
- Evidence: `mfg-material-staging-issue.contract.md:140,195,219`; `issues/p10-06.md:15` has a single `movement_id`.
- Fix: add a child table `whm_staging_list_line_postings` in V560040.

### F22 — Medium · Rank 4: an order can be edited while its release awaits approval
- Contract row: PRO-T1-06, PRO-T1-10
- Source: Claude
- Evidence: `mfg-production-order.contract.md:83` allows any field to be edited in PLANNED, and "pending" is PLANNED + `released_at` (`:61`).
- What a user experiences: the approver approves a quantity or BOM that has changed since the request.
- Fix: refuse edits while pending, or clear the pending request on edit.

### F23 — Medium · Rank 4: p10-07 posts receipts before p10-09's absorption service exists
- Contract row: PRC-T4-03
- Source: Claude
- Evidence: `issues/p10-07.md:52-53` ("posts at the absorption service's contract interface (tests stub it)"); p10-09 depends on p10-07.
- What a user experiences: the immutable ledger receives outputs at the engine's fallback value.
- Fix: refuse posts when there is no absorption bean, or move absorption into p10-07.

### F24 — Medium · Rank 4: v1 requirements depend on v1.1 seams
- Contract row: FR-620…669 (all v1)
- Source: Claude
- Evidence: `FRD-MFG.md:366` onward tags every FR v1. `FRD-STORES.md:161` (FR-513) and every FR-500…539 are v1.1, and none of the p8 seams exist in code.
- Fix: retag MFG as v1.1+ or reorder the releases. p10-01 should keep asserting the p8 objects.

### F25 — Medium · Rank 6 (screen drift): two contracts define capacity load differently
- Contract row: PRO §5.3 vs MRP §5.1
- Source: Both
- Evidence: `mfg-production-order.contract.md:225-227` buckets on planned start and includes PLANNED orders only with `includePlanned`. `mfg-mrp.contract.md:198-202` includes PLANNED orders and spreads the load over working days. The column sets differ.
- Fix: make one owner (p10-13) with one rule and one column set.

### F26 — Medium · Rank 6: ACTIVE demand-plan lines are both editable and not editable
- Contract row: MRP-T2-02
- Source: GPT
- Evidence: `mfg-mrp.contract.md:157` allows it; `issues/p10-11.md:34` forbids it.
- Fix: decide one rule and align both documents.

### F27 — Low · Rank 6: one in-process QC receipt gate has two error codes and two predicates
- Source: Claude
- Evidence: `mfg-production-receipt.contract.md:106` (`INPROCESS_QC_OPEN`, open inspection) versus `mfg-qc-rework.contract.md:98` (`INPROCESS_INSPECTION_OPEN`, where an inspection not yet started also counts).
- Fix: use QRW-GRD-09's wording in both.

### F28 — Low · Rank 7: does an operation confirmation set IN_PROGRESS?
- Source: GPT
- Evidence: `issues/p10-08.md:22` says yes; `mfg-qc-rework.contract.md:72` and PRO-OPEN-06 say no.
- Fix: ratify "no" and fix p10-08.

### F29 — Low · Rank 7: `process_loss_percent` is stored but has no arithmetic
- Source: Both
- Evidence: FR-622 lists it, but the snapshot formula `mfg-production-order.contract.md:181` (PRO-T4-01) never applies it.
- Fix: define its effect in PRO-T4-01 and MRP-N-04, or remove the column.

### F30 — Low · Rank 7: the PRODUCTION_SETTLEMENT registry row does not match base value-only types
- Source: Claude
- Evidence: `FRD-MFG.md:139` gives MUST_BALANCE_PER_OWNER_ITEM / WEIGHTED_AVERAGE. Base value-only rows use MUST_BALANCE_PER_MOVEMENT / ACTUAL with not-stock-bearing flags (`V500003:225`). CST-OPEN-04 (`mfg-costing-close.contract.md:237`) can be closed: the VALUE_OFFSET counter from `WhbValueOnlyMovementPoster` works and no base change is needed.
- Fix: copy the `LANDED_COST_APPLY` row shape and close CST-OPEN-04.

### F31 — Low · Rank 7: wrong cross-references and a duplicate row id
- Source: Claude
- Evidence: `mfg-material-staging-issue.contract.md:73` cites PRO-T1-12 (should be -15). `mfg-bom.contract.md:71` cites PRO-GRD-03 (should be -07). `mfg-subcontracting.contract.md:160,162` use SUB-T4-08 twice.

### F32 — Low · Rank 7: a site created after V560001 has no number series
- Source: Claude
- Evidence: `WhbDocumentNumberIssuer.java:159-162` throws "not configured"; the seed covers only existing operator companies (the V510102:567-573 shape). Core WO has the same gap.
- Fix: state the admin step, or provision series on site creation.

### F33 — Low · Rank 7: CLAUDE.md MODULES table does not list warehouse-manufacturing (V560000–V569999)
- Source: Claude
- Evidence: `/Users/bbhushan/work/git/workspace/classic/CLAUDE.md` MODULES table. Band check: no file in `V560000+` exists; only platform `V560`–`V569` exist, and they do not collide.

## Dropped after verification
- none

## Remediation backlog

| Finding | Files to touch | Migration | Shared registries | Parity apply-to | Contract |
|---|---|---|---|---|---|
| F1, F10 | `docs/contracts/mfg-mrp.contract.md`, `issues/p10-12.md` | V560100 (allocated) | none | none (MFG only) | MRP-GRD-09, MRP-N-04 |
| F2 | `mfg-qc-rework.contract.md`, `mfg-production-order.contract.md`, `mfg-production-receipt.contract.md`; option: `warehouse-base/.../WhbAllocationService.java` | V560030/V560050; base: next free in V500000–V509999 (highest on disk V501227) if the base path is chosen | none | warehouse-base reservation owner | QRW-T4-07, PRO-GRD-08, PRC-GRD-13, PRO-T4-02 |
| F3 | `mfg-subcontracting.contract.md`, `issues/p10-10.md` | V560080 | none | warehouse-india job-work path | SUB-T1-03, SUB-T4-01 |
| F4 | `mfg-production-order.contract.md`, `mfg-material-staging-issue.contract.md`, `issues/p10-05.md` | none | none | STORES `material-requisition.contract.md` | PRO-GRD-10, MSI-T1-14 |
| F5 | `issues/p10-02.md`, `FRD-MFG.md` §3.2 | V560001 | none | warehouse-india precedent (P4-07) | new T4 row in each posting contract |
| F6 | `mfg-costing-close.contract.md`, `mfg-subcontracting.contract.md`, `FRD-MFG.md` FR-654/661; possibly a core decision on job-worker valuation | V560070/V560080 | none | warehouse-base costing; warehouse-india (same valuation gap today) | CST §1.5 `P_I`, SUB-T4-07, SUB-T1-08 |
| F7, F8, F19, F20 | `mfg-costing-close.contract.md`, `mfg-qc-rework.contract.md`, `issues/p10-09.md` | V560070 | none | warehouse landed-cost service pattern | CST-T4-01/-03/-06, QRW-T4-08 |
| F9, F13 | `mfg-mrp.contract.md`, `issues/p10-12.md` | none | none | STORES `po-schedule-port.contract.md` (POS-T1-31/-33) | MRP-N-03, N-08, T3-04 |
| F11, F16, F17, F21 | `mfg-material-staging-issue.contract.md`, `FRD-MFG.md` §3.1/§4, `issues/p10-06.md` | V560040 | `filterUtils.ts` scope `WAREHOUSE_MFG_STAGING_LIST` unchanged | none | MSI-T1-02, GRD-03, T4-06/-07 |
| F12 | `material-requisition.contract.md` (STORES), `issues/p8-09.md` | none | none | STORES p8-09 | MRQ-T4-01 |
| F14 | `mfg-production-receipt.contract.md`, `issues/p10-07.md` | none | none | none | PRC-T4-05 |
| F15, F27 | `mfg-production-receipt.contract.md`, `mfg-qc-rework.contract.md` | none | none | none | PRC-T4-08, PRC-GRD-14 |
| F18, F22 | `mfg-production-order.contract.md` | none | none | none | PRO-T4-02, PRO-T1-06 |
| F23 | `issues/p10-07.md`, `issues/p10-09.md` | none | none | none | PRC-T4-03 |
| F24 | `FRD-MFG.md` §6, `issues/12-EPIC-p10.md` | none | none | STORES / TRADE release plan | none |
| F25, F26 | `mfg-production-order.contract.md`, `mfg-mrp.contract.md`, `issues/p10-11.md`, `issues/p10-13.md` | V561110 / V560090 | `filterUtils.ts`: `WAREHOUSE_MFG_CAPACITY_LOAD`, `WAREHOUSE_MFG_DEMAND_PLAN` | none | PRO §5.3 / MRP §5.1, MRP-T2-02 |
| F28–F33 | `issues/p10-08.md`, `mfg-bom.contract.md`, `mfg-production-order.contract.md`, `mfg-subcontracting.contract.md`, `FRD-MFG.md` §3.1, `/Users/bbhushan/work/git/workspace/classic/CLAUDE.md` | V560001 (F30) | none | none | PRO-T4-01, CST-OPEN-04 |

## Parity (C10)
- Mobile: none. The contracts say none because of R-13 (`FRD-MFG.md:538`, user rule 2026-09-11, no warehouse mobile).
- Siblings sharing this pattern: core VAS work order (`warehouse`, V510102) must stay one movement per document. warehouse-india job work has the same job-worker valuation gap as F6. warehouse-base owns reservations, costing, the post guard and genealogy. warehouse optional `warehouse-trade` handles the PR conversion. Dealer, automotive, accessories, services, insurance, insurance-360 and assets have no manufacturing counterpart.

## In code, not in contract
- The named-status reservation overload exists → `WhbStockLedgerWriter.java:695`. Add a rework T4 row if it is used.
- Same-item grains that net to zero override stated cost → `WhbCostingEngine.java:278-289`. Add to the CST/QRW T4 rows.
- Layer restatement is a caller obligation → `WhbCostingEngine.java:952`. Add to CST-T4-06.
- The value-only poster adds the VALUE_OFFSET counter itself → `WhbValueOnlyMovementPoster.java:22-31`. Use it in CST-T4-06.
- `WhbMovementPostGuard` is opt-in → `WhbMovementPostGuard.java:15`. Add an MFG guard row.

## Contract quality
- All eight contracts are v0 and unratified.
- Still OPEN: PRO-OPEN-02/06, MSI-OPEN-02/05, PRC-OPEN-05/06, CST-OPEN-04…08, QRW-OPEN-02…09, SUB-OPEN-06…09, MRP-OPEN-*.
- T3 notification channels are "TBD DEFERRED" in CST-T3-01, SUB-T3-03, QRW-T3-01/02 and MRP-T3-02. The nightly MRP schedule has no setting (MRP-OPEN-08).
- C3/C5/C8 cannot be verified at runtime (no controllers, API clients, pages, grids, locales or filter scopes yet). Their absence is not reported as defects.
- Reversal genealogy has no cancel semantics; the recursive trace does not filter cancels (`WhbTransformationRepositoryCustomImpl.java:56`, cited by GPT).
- Statutory India values stay RE-VERIFY (SUB §3.1).

## Referred to standards reviewer
- none
