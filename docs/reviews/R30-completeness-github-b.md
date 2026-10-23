# R30 — Completeness audit, GitHub part B (#301–#604)

**Date:** 2026-10-23 · **Mode:** read-only (no issue, task file or code edited; this report is the only file written) · **Repo:** `neetub1508/warehouse-issues` @ `main`, code `classic` @ `main` (`65b41be8a6`).
**Inputs:** `docs/DECISIONS.md` D-16 (`:466-525`), `docs/reviews/R28-manufacturing-storage-retarget-impact.md` §8b/§8c (`:158-190`), `docs/reviews/RETARGET-PROGRAM-STATUS.md`, `issues/CREATED.md`, `docs/frd/FRD-REM.md` Appendices A–C, every issue #301–#604 with comments (`gh issue view`, 304 issues), `classic/.claude/tasks/BATCH-WAREHOUSE-FINDINGS.md`.

## Summary

| Set | Count | State | OK | GAP |
|---|---|---|---|---|
| #301–#544 follow-up / finding reports (no task file) | 244 | 230 closed-completed · 7 closed-not-planned · 7 open | 219 | 25 |
| #545–#548 phase epics P7–P10 | 4 | open | 4 | 0 |
| #549–#604 tasks P7-01…P10-13 | 56 | open | 48 | 8 |
| **Total** | **304** | | **271** | **33** |

**Checks that passed in full**
- **(a) #545–#604:** all 60 map 1:1 to `issues/09…12-EPIC-p7…p10.md` and `issues/p7-01…p10-13.md` through `issue:` and `CREATED.md:323-382`. Titles and labels are identical. Bodies are identical after substituting `__P7__`…`__P10__` → `#545`…`#548`, `__MASTER__` → `#1` and `__TASKS__` → the checklist (script diff, 0 other differences).
- **(f) epics:** #545 lists exactly #549–#561 (13), #546 #562–#577 (16), #547 #578–#591 (14), #548 #592–#604 (13). Each code matches the linked title, and master #1 links all four epics.
- **(f) task bodies:** all 56 have `## Acceptance`, a `Migrations` and a `Screens` field in the header line, and a dependency statement (`Depends on` / `## Blocked on`). The two exceptions are in CP-GB-015.
- **(f) R29:** every task has exactly one "R29 functional review findings carried by this task" comment, 286 finding bullets in total, which matches `RETARGET-PROGRAM-STATUS.md`. P7-01 #549, P8-12 #573 and P8-14 #575 state "carries no R29 finding".
- **(f) coverage:** `ls issues/p{7,8,9,10}-*.md` = 56 = the 56 GitHub tasks, so no task file is missing on GitHub.
- **(c) code exists:** 228 of the 230 closed-completed issues cite at least one commit that `git merge-base --is-ancestor <sha> origin/main` confirms is on classic `main`. The other two close with no code by design: #458 is docs-only (design repo `ace9900`/`de54725`) and #469 is "verified, nothing to change". Every `V5xxxxx` cited in a close comment exists, except reservations released unused (#320/#331/#337 `V509999` placeholder, #379 `V501138` "unused and can be released").
- **(c) dealer/retail code → P7:** the 478 paths in FRD-REM Appendix A all exist in classic. Every warehouse-module file named for a removed feature (440 files: Awb/Ndr/Cod/Rto/Marketplace/TrackingLink/Channel*/Obsolescence/TradePortal/StockingOwnership/ExternalSnapshot/Serviceability/RateQuote/Dealer/Retail) is in Appendix A (`comm -23` = 0). The 95 kept files that still reference those identifiers are each named in FRD-REM or a `p7-*.md` file. The 4 exceptions are the Parts-KPI files, which P7-11 #559 renames (`p7-11.md:21-26`); the `OBSOLESCENCE` KPI stays (`p7-07.md:52`). The retail/dealer follow-ups #347, #355, #433, #468, #471, #474 and #487 are therefore covered by P7-02/03/04/07 (for example `V511304` is deleted by `p7-04.md:5`, and `WhCostBearingResponseContractTest:29,58,122-123` is cut by `p7-07.md:26`).
- **(d) open non-task issues:** #323, #324, #386, #519, #520, #539 and #543 are each a `[!] … FINAL [!]` line in `BATCH-WAREHOUSE-FINDINGS.md` (`:452,455,569/711,827,828,836,840`), owned outside the build. #539 and #543 also hit P10 (CP-GB-001).
- **(b):** #301–#544 have no task files, so there is no header to mark. Their D-16 status is in the table. Seven are wholly or partly VOID because their code is removed by P7.

## Findings (LEFT-BEHIND gaps first)

**CP-GB-001 — HIGH — Bonded / MOOWR stock cannot be issued to production or sent to a subcontractor. No P10 task carries this.**
- **Evidence:**
  - `warehouse-india/.../whinbondedloss/WhinBondedVirtualExitPostGuard.java:20-31,56-57,81` refuses `409 BONDED_EXIT_NOT_RECORDED` on any line that rises at a virtual-counterparty location in a duty status with `requires_licence`. Its only exemptions are `WhinBondedLossRecorder.LOSS_MOVEMENT_TYPES` and the VAS `WhWorkOrder.WORK_ORDER_TYPES`.
  - P10 posts exactly such lines: issue into the virtual `VIRT-PRODUCTION-<site>` (`p10-06.md:25`, `FRD-MFG.md:390` FR-638) and `SUBCONTRACT_DISPATCH` to the virtual `JOB_WORKER` location (`FRD-MFG.md:525` MD-28). Both base types are virtual counterparties (`WB V500006:131-132`).
  - The new P10 movement types (`p10-02.md:19-20`) are not in the exempt set.
  - `grep -n 'duty.status\|requires_licence\|BONDED_EXIT\|MOOWR\|bonded'` over `issues/p10-*.md` and `docs/frd/FRD-MFG.md` finds no rule for this. The one hit is the balance key `(…, duty status)` at `p10-07.md:100`.
  - Open #543 ("MOOWR job work of licensed stock is refused everywhere") and #539 ("is MOOWR work-order scrap a loss…") are not cited by any P7–P10 file.
- **Gap:** a manufacturing re-target that cannot consume MOOWR (in-bond manufacturing) stock. The guard also hard-codes a movement-type list rather than using a registry flag.
- **Carrier:** P10-02 #593 (a registry flag for "accounted bonded exit" on the new movement types), with P10-06 #597 and P10-10 #601 (acceptance: a BONDED issue and dispatch). The enablement decision stays with #543/#539 [!].

**CP-GB-002 — MEDIUM — An amended PO-line tolerance never reaches core's receipt guard.**
- **Evidence:**
  - `RETARGET-PROGRAM-STATUS.md:27` says: "Open for STORES: the trade amendment change type `TOLERANCE` has no field on core `amendOrder` `lineChanges`".
  - `docs/contracts/trade-order-amendment.contract.md:33` defines the `TOLERANCE` change type.
  - Core `lineChanges[]` = `poLineId, orderedQuantity?, unitPrice?, expectedDeliveryDate?, receivingLocationId?` (`FRD-STORES.md:415`).
  - `p8-01.md:64-65` carries tolerances on **create** only (CN-1/CN-2). `grep -i tolerance issues/p9-11.md` returns 0 lines.
- **Gap:** an approved trade amendment of the over/under tolerance leaves core enforcing the create-time value. Nobody owns the item.
- **Carrier:** P8-01 #562 (add `overTolerancePct`/`underTolerancePct` to `lineChanges`) and P9-11 #588 (send it). Mirror check on SO (#586).

**CP-GB-003 — MEDIUM — The 56 open tasks are in no phase batch yet, and the second R29 review is not done.**
- **Evidence:**
  - `ls classic/.claude/tasks | grep -E 'WAREHOUSE-P(7|8|9|10)'` returns nothing (no `BATCH-` and no `LANE-BRIEF-`).
  - `RETARGET-PROGRAM-STATUS.md:30,32` list "Second dual-engine functional review" and "BATCH files" as Remaining.
- **Gap:** (d) is unmet for #549–#604 until `/create-batch` runs. This is a known pending step, not a defect.
- **Carrier:** status step 6 (and step 4 before it).

**CP-GB-004 — MEDIUM — The PO, return-receipt and stock-adjustment item pickers are not scoped to the owner.**
- **Evidence:**
  - #467 close comment, "Not included: PO / return-receipt / stock-adjustment pickers (still unscoped, out of scope)".
  - `WhPurchaseOrderModal.tsx:251` `whPurchaseOrderApi.searchItems(query, limit)` passes no owner, although `ownerId` is on the form (`:62`). The GRN got the 4-arg owner overload (`a83d27f80f`).
  - No carrier: `grep '#467\|owner.*picker'` over `issues/p{7..10}-*.md` and FRD-STORES/TRADE returns nothing.
- **Gap:** P8-01 rebuilds PO lines (OPEN/BLANKET, schedules) on this modal and inherits the cross-owner picker.
- **Carrier:** P8-01 #562 for the PO, and **NEW** for return receipt and stock adjustment.

**CP-GB-005 — LOW — Exception Console: the non-TASK exception codes and the Status column print raw codes.**
- **Evidence:**
  - The #304 close comment lists, under "Not included", "The console's non-TASK branches and Status column are still raw ([!] owner)".
  - In the code: `WhExceptionConsoleManagementTable.tsx:112-114` (`: row.exceptionCode`) and `:128` (`textCell(row.status)`).
  - No later issue covers it (`gh issue list --search "Exception Console"` → only #304, #290, #14, #213, #259, #7, #19, #67, #551; none on this). `BATCH-WAREHOUSE-FINDINGS.md:480` is ticked `[x]`.
- **Gap:** the CLAUDE.md "Seeded Code Labels" rule is broken on a reference screen.
- **Carrier:** **NEW** (or P7-12 #560's sweep, if it is widened).

**CP-GB-006 — LOW — The consolidated e-way bill status labels do not go through `registryLabel`.**
- **Evidence:**
  - The #339 close comment says "Residual: the consolidated grid, its view modal and the member-status label still use t(...) || code labels".
  - Still in the code: `WhinEwayBillConsolidatedManagementTable.tsx:129`, `WhinEwayBillConsolidatedViewModal.tsx:142,248`.
  - Not filed (`BATCH-WAREHOUSE-FINDINGS.md:510` `[x]`).
- **Carrier:** **NEW** (warehouse-india).

**CP-GB-007 — LOW — The dated-obligation register test is not a required ci-gate report.**
- **Evidence:**
  - The #361 close comment says "`WhbDatedObligationRegisterTest` is not in the required-report list of `shared/scripts/ci-gate/20-warehouse.def`… reported to the gate owner, not changed".
  - `grep DatedObligation shared/scripts/ci-gate/*.def` returns nothing.
- **Gap:** P8/P9/P10 add dated jobs (schedule-line, MRP and contract-expiry), and a missing register row would ship silently, as #359 did.
- **Carrier:** P8-14 #575 (the P8 registry wave), or **NEW** in the CI gate.

**CP-GB-008 — MEDIUM — Contracts that P8/P10 build on are still unratified, and the [!] ratification lines are ticked closed.**
- **Evidence:**
  - `warehouse-india/docs/contracts/job-work.contract.md:11` and `delivery-challan.contract.md:13` read "Status: DERIVED — awaiting ratification [!] OWNER: product owner" (#446). P10-10 #601 builds on india job work and challans (`p10-10.md:7,41-44`) and cites neither contract.
  - `warehouse/docs/contracts/goods-receipt.contract.md:12` reads "`UNRATIFIED`" (#499), and P8-04/P8-05 extend the GRN.
  - Still open by close comment:
    - H1 contract (#465, #496)
    - regulated-items contract G7 (#498)
    - registration-change rows G4 (#507)
    - scan contract SCAN-T1/SC-DOC-01 (#502, #514, #521)
    - Lot/Serial have no contract (#365)
  - The FINDINGS lines are `[x]` (for example `:843` #530 and `:730` #407 were ratified, but these others were not re-carried).
- **Gap:** the S1 pre-review would run in DERIVED mode on the very seams P10 depends on.
- **Carrier:** **NEW** "ratify warehouse-india job-work / challan + GRN contracts", a prerequisite of #601 and #565/#566. The rest are a **NEW** ratification backlog item.

**CP-GB-009 — LOW — The dated live FIFO check (on or after 2026-11-01) has no carrier and collides with the P7 DB rebuild.**
- **Evidence:**
  - #411 and #453 close comments say "Live FIFO … dated follow-up check on/after 2026-11-01, owner MACHINE A-A1 driver".
  - `BATCH-WAREHOUSE-FINDINGS.md:1293` (the FIFO policy fixture starts 2026-11-01) and `:1301` ("live NOT-RUN").
  - P7-13 #561 drops and rebuilds the dev DB, and `grep 2026-11-01 issues/p7-13.md` returns nothing.
- **Carrier:** P7-13 #561 (re-create the fixture after the rebuild, or record the check as void), or **NEW**.

**CP-GB-010 — LOW — The platform object-storage fallback extension list lacks `.csv`.**
- **Evidence:** the #397 close comment reads "[!] platform owner … lacks .csv — platform module, not changed". `platform/.../ObjectStorageService.java:932` still lists `.pdf,…,.tif` with no `.csv`.
- **Gap:** a warehouse import breaks when the settings row is missing.
- **Carrier:** **NEW** (platform; outside the warehouse program).

**CP-GB-011 — LOW — Server refusal text and platform toasts stay in English in fr and hi.**
- **Evidence:**
  - #401 and #405 ("Server refusal text stays English in fr and hi; backend messages are not localised").
  - #404 (platform "Dismiss" / "Export Data").
  - #522 ("hard-coded English toasts that useExport already had … out of scope").
  - No carrier.
- **Carrier:** **NEW** (platform common).

**CP-GB-012 — LOW — The placeholder-less `Select` sweep covered warehouse-base only.**
- **Evidence:** the #470 close comment says "Not included: Other warehouse modules' modals (not scanned)". No later issue.
- **Carrier:** **NEW**, or fold into the P8/P9/P10 standards gate for new modals.

**CP-GB-013 — LOW — The posting-throughput ceiling (#386, open) is not considered by P10.**
- **Evidence:**
  - #386 is FINAL [!] "Concurrent posting near-serialised (10 posters ≈1.3× one; 50 exceed the 60 s socket timeout)" (`BATCH-WAREHOUSE-FINDINGS.md:569,711`).
  - P10 adds backflush and production-receipt posting volume. `grep '#386\|F380\|serialis'` over `issues/p10-*.md` and FRD-MFG finds only `p10-02.md:76` (number series).
- **Carrier:** a P10-07 #598 acceptance note (a measured backflush rate), or keep it under #386 [!].

**CP-GB-014 — LOW — `CREATED.md` is stale for this range.**
- **Evidence:**
  - The headline `CREATED.md:3-5` reads "159 issues … 144 tasks = 153", but `ls issues/p*.md` = **200** and `issues/*EPIC*.md` = **13**.
  - Of #301–#544, only #329, #389, #474 and #487 are listed (`CREATED.md:284`). The other 240 follow-up reports have no row.
- **Carrier:** **NEW** docs fix (CREATED regeneration).

**CP-GB-015 — LOW — Two P7 task bodies state no dependency.**
- **Evidence:**
  - `p7-02.md` (#550) and `p7-08.md` (#556) have no `Depends on` / `Blocked on`.
  - The order exists only in epic #545 (`09-EPIC-p7.md:63-68`: P7-02 after P7-01, P7-08 after P7-07).
  - Every other task states its dependency in its body.
- **Carrier:** P7-02 #550 / P7-08 #556 (add one line each).

**Informational (no carrier needed)**
- #474 and #487 re-keyed carrier references because carriers would relocate to `warehouse-retail` (R7 §2.6). D-16 item 2 keeps generic shipping and carriers in core, so the "record `fk_wh_shipments_carrier_account`" note in #487 is moot.
- #369, #538 and #544 accepted residuals ("accepted at S3", "accepted residual … maps to 409"). These were explicit decisions, not dropped work.

## Coverage table

| Issue | Task file | State | D-16 status | Verdict |
|---|---|---|---|---|
| #301 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #302 | — | closed/not planned | valid (kept core / 3PL / India) | OK |
| #303 | — | closed/not planned | valid (kept core / 3PL / India) | OK |
| #304 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-005) |
| #305 | — | closed/not planned | valid (kept core / 3PL / India) | OK |
| #306 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #307 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #308 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #309 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #310 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #311 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #312 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #313 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #314 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #315 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #316 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #317 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #318 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #319 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #320 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #321 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #322 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #323 | — | open | valid (kept core / 3PL / India); open FINAL [!] in BATCH-WAREHOUSE-FINDINGS | OK |
| #324 | — | open | valid (kept core / 3PL / India); open FINAL [!] in BATCH-WAREHOUSE-FINDINGS | OK |
| #325 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #326 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #327 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #328 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #329 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #330 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #331 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #332 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #333 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #334 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #335 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #336 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #337 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #338 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #339 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-006) |
| #340 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #341 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #342 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #343 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #344 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #345 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #346 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #347 | — | closed/completed | partly VOID — obsolescence-fee part (P7-07) | OK |
| #348 | — | closed/not planned | valid (kept core / 3PL / India) | OK |
| #349 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #350 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #351 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #352 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #353 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #354 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #355 | — | closed/completed | VOID — dealer (P7-07) | OK |
| #356 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #357 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #358 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #359 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #360 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #361 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-007) |
| #362 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #363 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #364 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #365 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-008) |
| #366 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #367 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #368 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #369 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #370 | — | closed/not planned | valid (kept core / 3PL / India) | OK |
| #371 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #372 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #373 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #374 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #375 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #376 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #377 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #378 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #379 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #380 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #381 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #382 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #383 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #384 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #385 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #386 | — | open | valid (kept core / 3PL / India); open FINAL [!] in BATCH-WAREHOUSE-FINDINGS | GAP (CP-GB-013) |
| #387 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #388 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #389 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #390 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #391 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #392 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #393 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #394 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #395 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #396 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #397 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-010) |
| #398 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #399 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #400 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #401 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-011) |
| #402 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #403 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #404 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-011) |
| #405 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-011) |
| #406 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #407 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #408 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #409 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #410 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #411 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-009) |
| #412 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #413 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #414 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #415 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #416 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #417 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #418 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #419 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #420 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #421 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #422 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #423 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #424 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #425 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #426 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #427 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #428 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #429 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #430 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #431 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #432 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #433 | — | closed/completed | VOID — retail (code deleted by P7-04) | OK |
| #434 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #435 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #436 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #437 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #438 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #439 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #440 | — | closed/not planned | valid (kept core / 3PL / India) | OK |
| #441 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #442 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #443 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #444 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #445 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #446 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-008) |
| #447 | — | closed/not planned | valid (kept core / 3PL / India) | OK |
| #448 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #449 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #450 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #451 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #452 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #453 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-009) |
| #454 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #455 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #456 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #457 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #458 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #459 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #460 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #461 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #462 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #463 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #464 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #465 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-008) |
| #466 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #467 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-004) |
| #468 | — | closed/completed | partly VOID — publish log/run part (P7-04) | OK |
| #469 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #470 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-012) |
| #471 | — | closed/completed | VOID — dealer (P7-07) | OK |
| #472 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #473 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #474 | — | closed/completed | partly VOID — NDR/COD/rate-quote part (P7-02/03); tracking events kept | OK |
| #475 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #476 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #477 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #478 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #479 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #480 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #481 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #482 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #483 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #484 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #485 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #486 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #487 | — | closed/completed | partly VOID — rate-quote part (P7-02); labels/pickups/manifests/handovers kept | OK |
| #488 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #489 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #490 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #491 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #492 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #493 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #494 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #495 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #496 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-008) |
| #497 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #498 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-008) |
| #499 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-008) |
| #500 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #501 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #502 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-008) |
| #503 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #504 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #505 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #506 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #507 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-008) |
| #508 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #509 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #510 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #511 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #512 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #513 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #514 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-008) |
| #515 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #516 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #517 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #518 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #519 | — | open | valid (kept core / 3PL / India); open FINAL [!] in BATCH-WAREHOUSE-FINDINGS | OK |
| #520 | — | open | valid (kept core / 3PL / India); open FINAL [!] in BATCH-WAREHOUSE-FINDINGS | OK |
| #521 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-008) |
| #522 | — | closed/completed | valid (kept core / 3PL / India) | GAP (CP-GB-011) |
| #523 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #524 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #525 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #526 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #527 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #528 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #529 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #530 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #531 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #532 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #533 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #534 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #535 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #536 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #537 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #538 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #539 | — | open | valid (kept core / 3PL / India); open FINAL [!] in BATCH-WAREHOUSE-FINDINGS | GAP (CP-GB-001) |
| #540 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #541 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #542 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #543 | — | open | valid (kept core / 3PL / India); open FINAL [!] in BATCH-WAREHOUSE-FINDINGS | GAP (CP-GB-001) |
| #544 | — | closed/completed | valid (kept core / 3PL / India) | OK |
| #545 | 09-EPIC-p7.md | open | valid (D-16 epic) | OK |
| #546 | 10-EPIC-p8.md | open | valid (D-16 epic) | OK |
| #547 | 11-EPIC-p9.md | open | valid (D-16 epic) | OK |
| #548 | 12-EPIC-p10.md | open | valid (D-16 epic) | OK |
| #549 | p7-01.md | open | valid (D-16 task) | OK |
| #550 | p7-02.md | open | valid (D-16 task) | GAP (CP-GB-015) |
| #551 | p7-03.md | open | valid (D-16 task) | OK |
| #552 | p7-04.md | open | valid (D-16 task) | OK |
| #553 | p7-05.md | open | valid (D-16 task) | OK |
| #554 | p7-06.md | open | valid (D-16 task) | OK |
| #555 | p7-07.md | open | valid (D-16 task) | OK |
| #556 | p7-08.md | open | valid (D-16 task) | GAP (CP-GB-015) |
| #557 | p7-09.md | open | valid (D-16 task) | OK |
| #558 | p7-10.md | open | valid (D-16 task) | OK |
| #559 | p7-11.md | open | valid (D-16 task) | OK |
| #560 | p7-12.md | open | valid (D-16 task) | OK |
| #561 | p7-13.md | open | valid (D-16 task) | OK |
| #562 | p8-01.md | open | valid (D-16 task) | GAP (CP-GB-002) |
| #563 | p8-02.md | open | valid (D-16 task) | OK |
| #564 | p8-03.md | open | valid (D-16 task) | OK |
| #565 | p8-04.md | open | valid (D-16 task) | OK |
| #566 | p8-05.md | open | valid (D-16 task) | OK |
| #567 | p8-06.md | open | valid (D-16 task) | OK |
| #568 | p8-07.md | open | valid (D-16 task) | OK |
| #569 | p8-08.md | open | valid (D-16 task) | OK |
| #570 | p8-09.md | open | valid (D-16 task) | OK |
| #571 | p8-10.md | open | valid (D-16 task) | OK |
| #572 | p8-11.md | open | valid (D-16 task) | OK |
| #573 | p8-12.md | open | valid (D-16 task) | OK |
| #574 | p8-13.md | open | valid (D-16 task) | OK |
| #575 | p8-14.md | open | valid (D-16 task) | OK |
| #576 | p8-15.md | open | valid (D-16 task) | OK |
| #577 | p8-16.md | open | valid (D-16 task) | OK |
| #578 | p9-01.md | open | valid (D-16 task) | OK |
| #579 | p9-02.md | open | valid (D-16 task) | OK |
| #580 | p9-03.md | open | valid (D-16 task) | OK |
| #581 | p9-04.md | open | valid (D-16 task) | OK |
| #582 | p9-05.md | open | valid (D-16 task) | OK |
| #583 | p9-06.md | open | valid (D-16 task) | OK |
| #584 | p9-07.md | open | valid (D-16 task) | GAP (CP-GB-002) |
| #585 | p9-08.md | open | valid (D-16 task) | OK |
| #586 | p9-09.md | open | valid (D-16 task) | OK |
| #587 | p9-10.md | open | valid (D-16 task) | OK |
| #588 | p9-11.md | open | valid (D-16 task) | GAP (CP-GB-002) |
| #589 | p9-12.md | open | valid (D-16 task) | OK |
| #590 | p9-13.md | open | valid (D-16 task) | OK |
| #591 | p9-14.md | open | valid (D-16 task) | OK |
| #592 | p10-01.md | open | valid (D-16 task) | OK |
| #593 | p10-02.md | open | valid (D-16 task) | GAP (CP-GB-001) |
| #594 | p10-03.md | open | valid (D-16 task) | OK |
| #595 | p10-04.md | open | valid (D-16 task) | OK |
| #596 | p10-05.md | open | valid (D-16 task) | OK |
| #597 | p10-06.md | open | valid (D-16 task) | GAP (CP-GB-001) |
| #598 | p10-07.md | open | valid (D-16 task) | OK |
| #599 | p10-08.md | open | valid (D-16 task) | OK |
| #600 | p10-09.md | open | valid (D-16 task) | OK |
| #601 | p10-10.md | open | valid (D-16 task) | GAP (CP-GB-001) |
| #602 | p10-11.md | open | valid (D-16 task) | OK |
| #603 | p10-12.md | open | valid (D-16 task) | OK |
| #604 | p10-13.md | open | valid (D-16 task) | OK |
