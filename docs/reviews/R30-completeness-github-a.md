# R30 — Completeness audit, GitHub part A (#1–#300)

Read-only audit, 2026-10-23. Repo `neetub1508/warehouse-issues` @ `main`; code `classic/{warehouse-base,warehouse,warehouse-3pl,warehouse-india}` @ `main` (`65b41be8a6`). Authority: `DECISIONS.md` D-16, `R28` §8b/§8c, `RETARGET-PROGRAM-STATUS.md`, `issues/CREATED.md`.

## Method

- `gh issue list --state all` → 295 issues in #1–#300. #2, #9, #155, #162, #164 are pull requests.
- `gh issue view` with comments for all 295. Every "Not included / remaining work", hand-off, `[!]`, "no owner" and "file it as its own" line was extracted and traced to a later issue or a P7–P10 task.
- (a) `issues/create-issues.sh --check`: 284 files checked, **42 drifted** (CP-GA-002). The `issue:` lines were mapped to CREATED.md: every task and finding file maps one to one.
- (c) Each closed task's declared migrations were checked against the classic migration folders (122 closed task files, 108 that declare migrations). All exist except the ones listed as v2/not built, plus one renumbered file (CP-GA-015). Retail/dealer tables in the code were matched to P7 tasks. Every creating migration (`V510050`, `V510204`–`V510210`, `V510215`, `V510221`, `V500053`, `V511262`, …) is named in a `p7-*.md`. R28 `RN-046`'s 25 files are all covered.
- (d) Open issues were checked against `classic/.claude/tasks/BATCH-WAREHOUSE-*.md`.

## Summary

| Bucket | Count |
|---|---|
| Issues checked | 295 (1 master + 8 phase epics + 144 tasks + 6 round-4 duplicates + 71 W-findings + 65 follow-up/bug reports) |
| Open | 23 · closed completed 252 · closed not planned 14 · closed duplicate 6 |
| D-16 status on task files | VOID 9 · partially VOID 9 · superseded 1 · partially superseded 1 · valid 124 |
| Verdict OK | 237 |
| Verdict GAP | 58 (42 of them only the body drift CP-GA-002) |
| Findings | 15 |

Notes judged **OK**, not gaps:
- `CREATED.md` has no rows for #266–#284 and #286–#300. Its §"existing GitHub reports" says it lists only the reports that the design docs cite.
- The open accounting follow-ups #173–#175 are deferred by `RN-054`.
- #75, #185, #227, #232, #240 and #241 are `[!]`-blocked on external owners in `BATCH-WAREHOUSE-P4.md:362` and `BATCH-WAREHOUSE-FINDINGS.md:246-333`.
- VOID #67, #81, #95, #134, #149, #150 and #151 are closed not planned, and no `whad_`/`whas_` objects exist in code (only comments).
- #152 (p2-27, VOID, built) is removed by P7-09.
- The sampling FIXED_QUANTITY/PERCENTAGE gap (#120) is carried by P8-05.
- The I-20 gap job (#120, #126) exists: `WhbDocumentNumberGapCheckJob`.
- GRN documents and grant `access_level` were settled as v1 boundaries by W71 #265.
- Bonded receiving (#51 item 1) is now built (`dutyStatus` on `WhGoodsReceiptLineRequest`).

## Findings

**CP-GA-001 · VOID/SUPERSEDED P6 tasks are still open and runnable (HIGH)**
- Evidence:
  - #142 (`p6-11.md:5`, VOID) and #144 (`p6-12.md:5`, SUPERSEDED by P10-03) are **OPEN**. CREATED.md says VOID tasks are closed not planned, and its list omits them.
  - `classic/.claude/tasks/BATCH-WAREHOUSE-P6.md:400` and `:404` still carry `- [ ] P6-11` and `- [ ] P6-12` as buildable lines. The file has 0 `D-16` mentions.
  - `p7-12.md:22` puts the superseded note on `BATCH-WAREHOUSE-{P5,FINDINGS,P2,P3,P2-IN,P01-CONTINUE}` but **not P6**.
  - `warehouse-base/INSTALL.md:1638` still lists "Manufacturing routings (P6-12 #144) accepted by decision (not built)".
- Gap: a P6 batch run would build the accessories absorption record and the BOM refusal. D-16 reverses both.
- Carrier:
  - P7-12: add `BATCH-WAREHOUSE-P6.md`, mark both lines `[!] VOID`, and fix INSTALL:1638.
  - Close #142 and #144 as not planned.

**CP-GA-002 · 42 GitHub bodies drift from their `.md`, including 13 D-16 headers (MEDIUM)**
- Evidence: `create-issues.sh --check` → "284 file(s) checked, 42 drifted".
- The D-16 header is absent on GitHub for 13 issues: #48, #52, #62, #67, #72, #81, #85, #90, #95, #123, #134, #142 and #144. For example, the #48 body contains no "D-16"; `p5-08.md:5` carries "PARTIALLY VOID".
- The other 29 drift for other reasons: #21, #26, #30, #35, #39, #44, #51, #58, #68, #74, #76, #80, #86, #88, #91, #94, #96, #99, #101, #103, #107, #109, #111, #112, #114, #119, #122, #131 and #138.
- Gap: (a)/(b) fail. GitHub readers do not see the VOID or partial-VOID scope.
- Carrier: `create-issues.sh --sync` (program step before the P7 batch), owned by P7-12.

**CP-GA-003 · Lost-sale capture has no producer left (MEDIUM)**
- Evidence:
  - The #106 close comment says: "There is no screen yet for recording a lost sale by hand; it is recorded through the integration (the dealer and services adapters, P2-25/P2-26)".
  - `p2-15.md:198` gives the guard half of lost sales to P2-25/P2-26, which are VOID. `p2-15.md` has no D-16 note.
  - The API exists, but no UI or in-process producer calls it: `WhInsufficientStockLogController.java:178`, `WhInsufficientStockLogService.java:146` `captureLostSale`.
  - P9-08 records `LOST`/`REGRETTED` enquiry lines (`p9-08.md:13-14`) but does not feed `wh_insufficient_stock_log` or demand history. A grep of p8/p9/p10 for "lost sale" returns nothing.
- Gap: `FR-257` and `WH-SC-283` are unreachable. Fill rate in WS-217 Parts→Stock KPIs (P7-11) counts lost-sale hits that nothing writes.
- Carrier:
  - P9-08: regretted or lost-on-stock lines call core `captureLostSale`. An alternative is a store-issue shortfall in P8-10.
  - Add a D-16 note to `p2-15.md`.

**CP-GA-004 · Master-merge open-document providers are missing for most documents, including every new P8–P10 document (MEDIUM)**
- Evidence:
  - The #148 close comment says: "every later open-document module (ASNs, goods receipts, demand orders, shipments) ships its own provider (functional C10; no task row)".
  - The code has only `WhPurchaseOrderMasterMergeDocumentProvider` and `WhbStockMovementMasterMergeDocumentProvider` (implementations of `WhbMasterMergeOpenDocumentProvider`).
  - A grep of `p8-*`, `p9-*` and `p10-*` for "master merge" / `MERGE_OPEN_DOCUMENTS` / "OpenDocument" returns 0 files.
- Gap: open GRNs, ASNs, demand orders, shipments, gate entries, MRNs, requisitions, store issues, production orders, BOMs, trade POs/SOs and rate contracts do not refuse an item or counterparty merge (WH-SC-330).
- Carrier: an acceptance row in every P8/P9/P10 document task. The cross-cutting part goes in P8-14. The four existing core documents need NEW work, or P8-14.

**CP-GA-005 · Rule 56 stock account cannot classify the new store and manufacturing movements (MEDIUM)**
- Evidence:
  - The #27 close comment says: "Whether consumption during assembly, repacking or value-added services needs its own head is left for a contract decision".
  - `V540130__Create_whin_stock_account_periods_and_lines.sql:63-64`: an unclassified reason code makes the period declare itself incomplete.
  - The categories are `RAW_MATERIAL/FINISHED_GOODS/SCRAP/WASTAGE` (`:208-209`).
  - A grep of p8-*, p9-*, p10-*, FRD-MFG and FRD-STORES for "Rule 56", `statutory_category` or `whin_stock_account` returns 0.
- Gap: after P8-10, P8-11 and P10-06 to P10-10 post, a manufacturer's Rule 56 period reports itself incomplete (store issue, production issue/receipt, backflush, scrap, job work).
- Carrier:
  - P10-02: seed `statutory_category` on every MFG reason.
  - P8-10 and P8-11: do the same for store issue and store return reasons.
  - Close the #27 contract decision.

**CP-GA-006 · Legal Metrology declarations are unowned, and they are now core for a manufacturer (MEDIUM)**
- Evidence:
  - #38 close comment: "The Legal Metrology declaration tables have no owning task".
  - `p4-05.md:118` acceptance: "absent and stated as unowned".
  - The `#38` body comment names `whin_packaged_commodity_declarations`, `whin_mrp_revisions` and `whin_instrument_verifications`. None exists (table scan of 365 warehouse tables).
  - `DECISIONS.md:675` still promises "MRP & Legal Metrology" in v2.
- Gap: packaged FG from P10-07 has no declaration (net quantity, MRP, month of manufacture, manufacturer).
- Carrier: NEW warehouse-india task, linked to P10-07 FG receipt and P8-12 labels.

**CP-GA-007 · SEZ / MOOWR returns are unowned; MOOWR job work is refused (MEDIUM)**
- Evidence:
  - #51 close comment: "SEZ and MOOWR returns have no owning task".
  - The #51 body (`p4-07.md:127`) says the MOOWR return, its lines and SEZ movements "have no owner".
  - #543 is OPEN: "MOOWR job work of licensed stock is refused everywhere". It sits only in `BATCH-WAREHOUSE-FINDINGS.md`.
  - A grep of p7–p10 for SEZ/MOOWR returns 0.
- Gap: MOOWR is manufacturing in a bonded warehouse, the target segment under D-16. P10-10 job work does not address it.
- Carrier: NEW warehouse-india task (MOOWR return and SEZ movements), plus a P10-10 acceptance row that settles #543.

**CP-GA-008 · No web bin-to-bin move, the basic storage operation (MEDIUM)**
- Evidence:
  - #176 and #208: `FR-150`/`WH-SC-285` "has no owning task anywhere in the design set".
  - #208 close comment: "A web Move action or a directed MOVE task would be new scope".
  - #211 close comment: "[!] RPF-W17-03: the stock return before Cancel uses `BIN_MOVE`, which is API-only; a web-only site cannot record it today. Owner: product owner".
  - The warehouse frontend has 0 files with `BIN_MOVE`. p8–p10 have 0 hits for `BIN_MOVE`/bin-to-bin/WS-231.
- Gap: a web-only stores site cannot re-bin stock or return replenishment stock. The program rule is no mobile app.
- Carrier: NEW P8 task (web Move action on WS-231 over the existing `BIN_MOVE` port). The other option is to fold it into P8-14.

**CP-GA-009 · Drop-ship code has no D-16 classification (LOW)**
- Evidence:
  - #52 close comment: "drop-ship per OD-18 (demand line + GRN ceiling linked)".
  - The code is `WhDropShipService.java:77`, `WhDropShipController`, `WhDropShipGuard`, and drop-ship wiring in `WhGoodsReceiptPostingService` and `WhDemandOrderService`.
  - INSTALL `:2102`/`:2213` gate it off as "v2".
  - FRD-REM, FRD-STORES and FRD-TRADE contain no drop-ship row, and no p7–p10 task names it.
- Gap: the code is neither marked for removal (retail) nor adopted by trade (B2B direct ship). It sits in core with no owner.
- Carrier: a decision row in FRD-REM. Then either P7-04 (remove) or P9-09 (SO direct-ship).

**CP-GA-010 · `wh_demand_order_lines.original_item_id` is read but never written; never filed (LOW)**
- Evidence:
  - The #244 comment (2026-10-13) says: "`wh_demand_order_lines.original_item_id` is read (`WhDemandOrderRepositoryCustomImpl:132`) but nothing writes it. File it as its own gap."
  - The #167 close comment says the same.
  - No issue title contains it. Only #150, #167 and #244 mention it.
  - Code: `WhDemandOrderLine.java:135-136`, with no setter caller.
- Gap: a dealer-era supersession "requested part" column survives with no writer.
- Carrier: P7-04 (drop it in the clean rewrite, `RN-052`), or P8-02 if SO lines need the customer's part number.

**CP-GA-011 · The "no planning/forecasting/routings" offer boundary contradicts P10, and P6-02 is unreviewed (MEDIUM)**
- Evidence:
  - #253 (W59) close: INSTALL §16 "Excluded (2026-09-30 ruling: planning, forecasting, optimisation incl. computed best stocking level…)".
  - Live text: `warehouse-base/INSTALL.md:2064` and `:2087`. `finding-w59.md:13` treats "manufacturing routings" as outside scope.
  - P10-04 builds work centres and routings. P10-11 builds demand plans (forecast/MPS) and `safety_stock_quantity` (`p10-11.md:13-15`). P10-12 builds MRP.
  - P7-12 edits INSTALL only for the removal grep, and no task file names INSTALL §16.
  - P6-02 #99 (OPEN, `BATCH-WAREHOUSE-P6.md:358`) builds a "computed best stocking level" framed for "a parts manager" (`p6-02.md:7,19`). It has no D-16 or ruling header and overlaps P10-11 planning parameters.
- Gap: the shipped docs and P10 contradict each other, and an open P6 task conflicts with both the 2026-09-30 ruling and P10.
- Carrier:
  - P7-12 or P10-01: amend INSTALL §16, the dated ruling and W59.
  - Re-header P6-02 as VOID or superseded by P10-11/P10-12.

**CP-GA-012 · MPR-OPEN-18: a rejected or withdrawn reversal still blocks a later reversal (LOW)**
- Evidence:
  - The #34 close comment says: "A rejected, withdrawn or pending reversal still counts against the one-reversal-per-movement rule … stays open under MPR-OPEN-18".
  - `docs/contracts/movement-post-reverse.contract.md:419` says "OPEN … Owner: a future migration".
  - The index is unchanged: `V500030__…ledger_invariants.sql:296-298` `uk_whb_stock_movements_one_reversal … WHERE reversal_of_movement_id IS NOT NULL`.
  - Only #34 mentions it.
- Gap: a ledger defect with no owner.
- Carrier: NEW warehouse-base task. The `RN-052` clean-rewrite window in P7-13 allows the index to be narrowed in place.

**CP-GA-013 · Stock on approval at the customer shows as available on enquiry (LOW)**
- Evidence:
  - The #45 close comment says: "The stock enquiry screen still shows goods at the customer as available".
  - `V540150__…approval_clocks.sql:60-62`: ON_APPROVAL is kept out of allocation only through location status.
  - No later issue or P7–P10 task carries it.
- Gap: enquiry overstates available stock.
- Carrier: NEW (warehouse-base enquiry reads the location type).

**CP-GA-014 · Task/finding headers miss D-16 although their scope touches removed features (LOW, item b)**
- Evidence:
  - `p2-10.md:63-66` ("Only carriers and RTO receipts exist in v1"; RTO is removed by P7-05).
  - `p2-15.md:116,198` (counter lost sale via VOID P2-25/P2-26).
  - `finding-w63.md:13` (#257: AWB auto-void and AWB-to-tracking mapping; AWB pools are removed by P7-02).
  - `finding-w59.md:13` (#253, see CP-GA-011).
  - Each has 0 `D-16` occurrences.
- Carrier: P7-12 design-set pass. Then add a one-line partial-VOID or superseded note to each and sync it (CP-GA-002).

**CP-GA-015 · Declared migration renumbered without a file update (LOW, item a/c)**
- Evidence:
  - `p0-13.md:5` declares **V500043**.
  - The code was renamed to `V501011__Create_whb_audit_events_hash_chain_and_whb_job_runs.sql` in `36e36ae827`. `V500043` no longer exists.
  - The #104 close record still says "Migrations applied: V500043".
- Carrier: P7-12 (header correction). P7-13 should prove history on the clean set.

## Coverage table

| Issue | Task file | State | D-16 status | Verdict |
|---|---|---|---|---|
| #1 | 00-EPIC-master.md | open | epic (lists VOID) | OK |
| #3 | 01-EPIC-p0.md | closed/completed | epic | OK |
| #4 | 02-EPIC-p1.md | closed/completed | epic | OK |
| #5 | 03-EPIC-p2.md | closed/completed | epic (lists VOID) | OK |
| #6 | 04-EPIC-p2in.md | closed/completed | epic | OK |
| #7 | 05-EPIC-p3.md | closed/completed | epic (lists VOID) | OK |
| #8 | 06-EPIC-p4.md | open | epic | OK |
| #10 | 07-EPIC-p5.md | closed/completed | epic (lists VOID) | OK |
| #11 | 08-EPIC-p6.md | open | epic (lists VOID) | GAP CP-GA-001 |
| #12 | p3-01.md | closed/completed | valid | OK |
| #13 | p1-01.md | closed/completed | valid | OK |
| #14 | p3-02.md | closed/completed | valid | OK |
| #15 | p0-01.md | closed/completed | valid | OK |
| #16 | p4-01.md | closed/completed | valid | OK |
| #17 | p5-01.md | closed/completed | valid | OK |
| #18 | p2-01.md | closed/completed | valid | OK |
| #19 | p3-03.md | closed/completed | valid | OK |
| #20 | p1-02.md | closed/completed | valid | OK |
| #21 | p5-02.md | closed/completed | valid | GAP CP-GA-002 |
| #22 | p4-02.md | closed/completed | valid | OK |
| #23 | p3-04.md | closed/completed | valid | OK |
| #24 | p2-02.md | closed/completed | valid | OK |
| #25 | p0-02.md | closed/completed | valid | OK |
| #26 | p5-03.md | closed/completed | valid | GAP CP-GA-002 |
| #27 | p4-03.md | closed/completed | valid | GAP CP-GA-005 |
| #28 | p3-05.md | closed/completed | valid | OK |
| #29 | p2-03.md | closed/completed | valid | OK |
| #30 | p5-04.md | closed/completed | valid | GAP CP-GA-002 |
| #31 | p3-06.md | closed/completed | valid | OK |
| #32 | p4-04.md | closed/completed | valid | OK |
| #33 | p1-03.md | closed/completed | valid | OK |
| #34 | p0-03.md | closed/completed | valid | GAP CP-GA-012 |
| #35 | p5-05.md | closed/completed | valid | GAP CP-GA-002 |
| #36 | p3-07.md | closed/completed | valid | OK |
| #37 | p2-04.md | closed/completed | valid | OK |
| #38 | p4-05.md | closed/completed | valid | GAP CP-GA-006 |
| #39 | p5-06.md | closed/completed | valid | GAP CP-GA-002 |
| #40 | p1-04.md | closed/completed | partially void | OK |
| #41 | p3-08.md | closed/completed | valid | OK |
| #42 | p2-05.md | closed/completed | valid | OK |
| #43 | p0-04.md | closed/completed | valid | OK |
| #44 | p5-07.md | closed/completed | valid | GAP CP-GA-002 |
| #45 | p4-06.md | closed/completed | valid | GAP CP-GA-013 |
| #46 | p3-09.md | closed/completed | valid | OK |
| #47 | p2-06.md | closed/completed | valid | OK |
| #48 | p5-08.md | closed/completed | partially void | GAP CP-GA-002 |
| #49 | p0-05.md | closed/completed | valid | OK |
| #50 | p3-10.md | closed/completed | valid | OK |
| #51 | p4-07.md | closed/completed | valid | GAP CP-GA-002,CP-GA-007 |
| #52 | p5-09.md | closed/completed | partially void | GAP CP-GA-002,CP-GA-009 |
| #53 | p2-07.md | closed/completed | valid | OK |
| #54 | p1-05.md | closed/completed | valid | OK |
| #55 | p4-08.md | closed/completed | valid | OK |
| #56 | p0-06.md | closed/completed | valid | OK |
| #57 | p3-11.md | closed/completed | valid | OK |
| #58 | p5-10.md | closed/completed | valid | GAP CP-GA-002 |
| #59 | p2-08.md | closed/completed | valid | OK |
| #60 | p1-06.md | closed/completed | valid | OK |
| #61 | p3-12.md | closed/completed | valid | OK |
| #62 | p5-11.md | closed/completed | partially void | GAP CP-GA-002 |
| #63 | p0-07.md | closed/completed | valid | OK |
| #64 | p4-09.md | closed/completed | valid | OK |
| #65 | p2-09.md | closed/completed | valid | OK |
| #66 | p3-13.md | closed/completed | valid | OK |
| #67 | p5-12.md | closed/not planned | void | GAP CP-GA-002 |
| #68 | p4-10.md | closed/completed | valid | GAP CP-GA-002 |
| #69 | p3-14.md | closed/completed | valid | OK |
| #70 | p1-07.md | closed/completed | valid | OK |
| #71 | p0-08.md | closed/completed | valid | OK |
| #72 | p5-13.md | closed/completed | partially void | GAP CP-GA-002 |
| #73 | p2-10.md | closed/completed | valid | GAP CP-GA-014 |
| #74 | p3-15.md | closed/completed | valid | GAP CP-GA-002 |
| #75 | p4-11.md | open | valid | OK |
| #76 | p5-14.md | closed/completed | valid | GAP CP-GA-002 |
| #77 | p0-09.md | closed/completed | valid | OK |
| #78 | p1-08.md | closed/completed | valid | OK |
| #79 | p2-11.md | closed/completed | valid | OK |
| #80 | p3-16.md | closed/completed | valid | GAP CP-GA-002 |
| #81 | p5-15.md | closed/not planned | void | GAP CP-GA-002 |
| #82 | p4-12.md | closed/completed | valid | OK |
| #83 | p0-10.md | closed/completed | valid | OK |
| #84 | p1-09.md | closed/completed | valid | OK |
| #85 | p3-17.md | closed/completed | partially void | GAP CP-GA-002 |
| #86 | p5-16.md | closed/completed | valid | GAP CP-GA-002 |
| #87 | p2-12.md | closed/completed | partially void | OK |
| #88 | p4-13.md | closed/completed | valid | GAP CP-GA-002 |
| #89 | p0-11.md | closed/completed | valid | OK |
| #90 | p3-18.md | closed/completed | partially void | GAP CP-GA-002 |
| #91 | p5-17.md | closed/completed | valid | GAP CP-GA-002 |
| #92 | p1-10.md | closed/completed | valid | OK |
| #93 | p2-13.md | closed/completed | valid | OK |
| #94 | p6-01.md | open | valid | GAP CP-GA-002 |
| #95 | p3-19.md | closed/not planned | void | GAP CP-GA-002 |
| #96 | p5-18.md | closed/completed | valid | GAP CP-GA-002 |
| #97 | p0-12.md | closed/completed | valid | OK |
| #98 | p1-11.md | closed/completed | valid | OK |
| #99 | p6-02.md | open | valid | GAP CP-GA-002,CP-GA-011 |
| #100 | p2-14.md | closed/completed | valid | OK |
| #101 | p5-19.md | closed/completed | valid | GAP CP-GA-002 |
| #102 | p3-20.md | closed/not planned | valid | OK |
| #103 | p6-03.md | open | valid | GAP CP-GA-002 |
| #104 | p0-13.md | closed/completed | valid | GAP CP-GA-015 |
| #105 | p1-12.md | closed/completed | valid | OK |
| #106 | p2-15.md | closed/completed | valid | GAP CP-GA-003,CP-GA-014 |
| #107 | p5-20.md | closed/completed | valid | GAP CP-GA-002 |
| #108 | p3-21.md | closed/not planned | valid | OK |
| #109 | p6-04.md | open | valid | GAP CP-GA-002 |
| #110 | p0-14.md | closed/completed | valid | OK |
| #111 | p3-22.md | closed/completed | valid | GAP CP-GA-002 |
| #112 | p6-05.md | open | valid | GAP CP-GA-002 |
| #113 | p1-13.md | closed/completed | valid | OK |
| #114 | p5-21.md | closed/completed | valid | GAP CP-GA-002 |
| #115 | p2-16.md | closed/completed | valid | OK |
| #116 | p3-23.md | closed/completed | valid | OK |
| #117 | p0-15.md | closed/completed | valid | OK |
| #118 | p6-06.md | open | valid | OK |
| #119 | p5-22.md | closed/completed | valid | GAP CP-GA-002 |
| #120 | p1-14.md | closed/completed | valid | OK |
| #121 | p3-24.md | closed/not planned | valid | OK |
| #122 | p6-07.md | open | valid | GAP CP-GA-002 |
| #123 | p5-23.md | closed/completed | partially void | GAP CP-GA-002 |
| #124 | p0-16.md | closed/completed | valid | OK |
| #125 | p2-17.md | closed/completed | valid | OK |
| #126 | p1-15.md | closed/completed | valid | OK |
| #127 | p0-17.md | closed/completed | valid | OK |
| #128 | p2-18.md | closed/completed | valid | OK |
| #129 | p1-16.md | closed/completed | valid | OK |
| #130 | p2in-01.md | closed/completed | valid | OK |
| #131 | p6-08.md | open | valid | GAP CP-GA-002 |
| #132 | p2-19.md | closed/completed | valid | OK |
| #133 | p1-17.md | closed/completed | valid | OK |
| #134 | p6-09.md | closed/not planned | void | GAP CP-GA-002 |
| #135 | p2in-02.md | closed/completed | valid | OK |
| #136 | p2-20.md | closed/completed | valid | OK |
| #137 | p1-18.md | closed/completed | valid | OK |
| #138 | p6-10.md | open | valid | GAP CP-GA-002 |
| #139 | p1-19.md | closed/completed | valid | OK |
| #140 | p2in-03.md | closed/completed | valid | OK |
| #141 | p2-21.md | closed/completed | partially superseded | OK |
| #142 | p6-11.md | open | void | GAP CP-GA-001,CP-GA-002 |
| #143 | p2-22.md | closed/completed | valid | OK |
| #144 | p6-12.md | open | superseded | GAP CP-GA-001,CP-GA-002 |
| #145 | p1-20.md | closed/completed | valid | OK |
| #146 | p2-23.md | closed/completed | valid | OK |
| #147 | p2in-04.md | closed/completed | valid | OK |
| #148 | p1-21.md | closed/completed | valid | GAP CP-GA-004 |
| #149 | p2-24.md | closed/not planned | void | OK |
| #150 | p2-25.md | closed/not planned | void | OK |
| #151 | p2-26.md | closed/not planned | void | OK |
| #152 | p2-27.md | closed/completed | void | OK |
| #153 | p2-28.md | closed/completed | valid | OK |
| #154 | p2-29.md | closed/completed | valid | OK |
| #156 | p3-25.md (no file, folded) | closed/duplicate | duplicate | OK |
| #157 | p5-24.md (no file, folded) | closed/duplicate | duplicate | OK |
| #158 | p5-25.md (no file, folded) | closed/duplicate | duplicate; VOID (trade portal) | OK |
| #159 | p5-26.md (no file, folded) | closed/duplicate | duplicate | OK |
| #160 | p5-27.md (no file, folded) | closed/duplicate | duplicate | OK |
| #161 | p5-28.md (no file, folded) | closed/duplicate | duplicate | OK |
| #163 | p1-22.md | closed/completed | valid | OK |
| #165 | — (report, CREATED row) | closed/completed | n/a | OK |
| #166 | — (report, CREATED row) | closed/completed | n/a | OK |
| #167 | — (report, CREATED row) | closed/completed | n/a | GAP CP-GA-010 |
| #168 | — (report, CREATED row) | closed/not planned | n/a | OK |
| #169 | — (report, CREATED row) | closed/completed | n/a | OK |
| #170 | — (report, CREATED row) | closed/completed | n/a | OK |
| #171 | — (report, CREATED row) | closed/completed | n/a | OK |
| #172 | — (report, CREATED row) | closed/completed | n/a | OK |
| #173 | — (report, CREATED row) | open | n/a | OK |
| #174 | — (report, CREATED row) | open | n/a | OK |
| #175 | — (report, CREATED row) | open | n/a | OK |
| #176 | — (report, CREATED row) | closed/completed | n/a | GAP CP-GA-008 |
| #177 | — (report, CREATED row) | closed/completed | n/a | OK |
| #178 | — (report, CREATED row) | closed/completed | n/a | OK |
| #179 | — (report, CREATED row) | closed/completed | n/a | OK |
| #180 | — (report, CREATED row) | closed/completed | n/a | OK |
| #181 | — (report, CREATED row) | closed/completed | n/a | OK |
| #182 | — (report, CREATED row) | closed/completed | n/a | OK |
| #183 | — (report, CREATED row) | closed/completed | n/a | OK |
| #184 | — (report, CREATED row) | closed/completed | n/a | OK |
| #185 | — (report, CREATED row) | open | n/a | OK |
| #186 | — (report, CREATED row) | closed/completed | n/a | OK |
| #187 | — (report, CREATED row) | closed/completed | n/a | OK |
| #188 | — (report, CREATED row) | closed/completed | n/a | OK |
| #189 | — (report, CREATED row) | closed/completed | n/a | OK |
| #190 | — (report, CREATED row) | closed/completed | n/a | OK |
| #191 | — (report, CREATED row) | closed/completed | n/a | OK |
| #192 | — (report, CREATED row) | closed/completed | n/a | OK |
| #193 | — (report, CREATED row) | closed/completed | n/a | OK |
| #194 | — (report, CREATED row) | closed/completed | n/a | OK |
| #195 | finding-w01.md | closed/completed | valid | OK |
| #196 | finding-w02.md | closed/completed | valid | OK |
| #197 | finding-w03.md | closed/completed | valid | OK |
| #198 | finding-w04.md | closed/completed | valid | OK |
| #199 | finding-w05.md | closed/completed | valid | OK |
| #200 | finding-w06.md | closed/completed | valid | OK |
| #201 | finding-w07.md | closed/completed | valid | OK |
| #202 | finding-w08.md | closed/completed | valid | OK |
| #203 | finding-w09.md | closed/completed | valid | OK |
| #204 | finding-w10.md | closed/completed | valid | OK |
| #205 | finding-w11.md | closed/completed | valid | OK |
| #206 | finding-w12.md | closed/completed | valid | OK |
| #207 | finding-w13.md | closed/completed | valid | OK |
| #208 | finding-w14.md | closed/completed | valid | GAP CP-GA-008 |
| #209 | finding-w15.md | closed/completed | valid | OK |
| #210 | finding-w16.md | closed/completed | valid | OK |
| #211 | finding-w17.md | closed/completed | valid | GAP CP-GA-008 |
| #212 | finding-w18.md | closed/completed | valid | OK |
| #213 | finding-w19.md | closed/completed | valid | OK |
| #214 | finding-w20.md | closed/completed | valid | OK |
| #215 | finding-w21.md | closed/completed | valid | OK |
| #216 | finding-w22.md | closed/completed | valid | OK |
| #217 | finding-w23.md | closed/completed | valid | OK |
| #218 | finding-w24.md | closed/completed | valid | OK |
| #219 | finding-w25.md | closed/completed | valid | OK |
| #220 | finding-w26.md | closed/completed | valid | OK |
| #221 | finding-w27.md | closed/completed | valid | OK |
| #222 | finding-w28.md | closed/completed | valid | OK |
| #223 | finding-w29.md | closed/completed | valid | OK |
| #224 | finding-w30.md | closed/completed | valid | OK |
| #225 | finding-w31.md | closed/completed | valid | OK |
| #226 | finding-w32.md | closed/completed | valid | OK |
| #227 | finding-w33.md | open | valid | OK |
| #228 | finding-w34.md | closed/completed | valid | OK |
| #229 | finding-w35.md | closed/completed | valid | OK |
| #230 | finding-w36.md | closed/completed | valid | OK |
| #231 | finding-w37.md | closed/completed | valid | OK |
| #232 | finding-w38.md | open | valid | OK |
| #233 | finding-w39.md | closed/completed | valid | OK |
| #234 | finding-w40.md | closed/completed | valid | OK |
| #235 | finding-w41.md | closed/completed | valid | OK |
| #236 | finding-w42.md | closed/completed | valid | OK |
| #237 | finding-w43.md | closed/completed | valid | OK |
| #238 | finding-w44.md | closed/completed | valid | OK |
| #239 | finding-w45.md | closed/completed | valid | OK |
| #240 | finding-w46.md | open | valid | OK |
| #241 | finding-w47.md | open | valid | OK |
| #242 | finding-w48.md | closed/completed | valid | OK |
| #243 | finding-w49.md | closed/completed | valid | OK |
| #244 | finding-w50.md | closed/completed | valid | GAP CP-GA-010 |
| #245 | finding-w51.md | closed/completed | valid | OK |
| #246 | finding-w52.md | closed/completed | valid | OK |
| #247 | finding-w53.md | closed/completed | valid | OK |
| #248 | finding-w54.md | closed/completed | valid | OK |
| #249 | finding-w55.md | closed/completed | valid | OK |
| #250 | finding-w56.md | closed/completed | valid | OK |
| #251 | finding-w57.md | closed/completed | valid | OK |
| #252 | finding-w58.md | closed/completed | valid | OK |
| #253 | finding-w59.md | closed/completed | valid | GAP CP-GA-011,CP-GA-014 |
| #254 | finding-w60.md | closed/completed | valid | OK |
| #255 | finding-w61.md | closed/completed | valid | OK |
| #256 | finding-w62.md | closed/completed | valid | OK |
| #257 | finding-w63.md | closed/completed | valid | GAP CP-GA-014 |
| #258 | finding-w64.md | closed/completed | valid | OK |
| #259 | finding-w65.md | closed/completed | valid | OK |
| #260 | finding-w66.md | closed/completed | valid | OK |
| #261 | finding-w67.md | closed/completed | valid | OK |
| #262 | finding-w68.md | closed/completed | valid | OK |
| #263 | finding-w69.md | closed/completed | valid | OK |
| #264 | finding-w70.md | closed/completed | valid | OK |
| #265 | finding-w71.md | closed/completed | valid | OK |
| #266 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #267 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #268 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #269 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #270 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #271 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #272 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #273 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #274 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #275 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #276 | — (report, no CREATED row) | closed/not planned | n/a | OK |
| #277 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #278 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #279 | — (report, no CREATED row) | closed/not planned | n/a | OK |
| #280 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #281 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #282 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #283 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #284 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #285 | — (report, CREATED row) | closed/completed | n/a | OK |
| #286 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #287 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #288 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #289 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #290 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #291 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #292 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #293 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #294 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #295 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #296 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #297 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #298 | — (report, no CREATED row) | closed/completed | n/a | OK |
| #299 | — (report, no CREATED row) | closed/not planned | n/a | OK |
| #300 | — (report, no CREATED row) | closed/completed | n/a | OK |
