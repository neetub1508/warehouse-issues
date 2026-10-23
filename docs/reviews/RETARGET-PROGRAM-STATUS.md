# Re-target program (D-16) — status and remaining steps

**Read this first when resuming.** Updated 2026-10-23 (R31 fix wave and tracking fix done). All work happens on `main` only (user rule).

## Done
1. R27 (client purchase-to-stores gap) and R28 (re-target impact, decisions `RN-050`…`RN-054`, plan §8c) recorded.
2. D-16 in DECISIONS.md. Spine docs rewritten; dealer/retail tasks VOID; historical files carry superseded notes.
3. Area requirements, contracts and tasks:
   - REM: `docs/frd/FRD-REM.md`, `issues/p7-01…13`, `09-EPIC-p7`
   - STORES: `FRD-STORES.md`, 7 contracts, `p8-01…16`, `10-EPIC-p8`
   - TRADE: `FRD-TRADE.md`, 10 `trade-*` contracts, `p9-01…14`, `11-EPIC-p9`
   - MFG: `FRD-MFG.md`, 8 `mfg-*` contracts, `p10-01…13`, `12-EPIC-p10`
4. MFG reconciled with STORES (MD-14…MD-29). Checker clean in the area files.
5. **R29 dual-engine functional review** (Claude + GPT): `docs/reviews/R29-functional-review-{rem,stores,trade-purchase,trade-sales,mfg}.md`, 145 findings.
6. **R29 fixes, wave 1, done:**
   - REM: 17 of 17 fixed (FRD-REM "R29 dispositions").
   - STORES: 36 of 36 fixed, plus 18 core-side items from the trade and mfg reviews (FRD-STORES "R29 dispositions"). FRD-STORES now holds the **"Port & seam registry (authoritative)"**.
   - The P8 schema migrations were renumbered to `V511310`–`V511323` (app) and `V501230`–`V501235` (base); seeds stay at `V511400`–`V511416`.

7. **R29 fixes, wave 2, done:**
   - TRADE: purchase 30/30, sales 29/29, mirror rows 18/18 (FRD-TRADE "R29 dispositions").
   - MFG: 33/33, with MD-30…MD-41 and no warehouse-base change needed (FRD-MFG "R29 dispositions").

## Remaining (in order)
1. **Core changes trade needs (CN-1…CN-7) — done 2026-10-22.** STORES made CN-1…CN-5 and adopted CN-6 (`STO-D19`) and CN-7 (`STO-D20`); the FRD-STORES port registry and `po-schedule-port` carry them.
   - **Trade alignment — done 2026-10-22.** FRD-TRADE §12a/§12c, `TRD-13`, R29 rows TP-F6/F14/F24, TS-F1; contracts `TPO-T4-01`/`-02`/`-09`, `TSO-T4-01`, `TOA-T4-02`, `TPO-OPEN-01`, `TSO-OPEN-01`; `p9-01` (seeds trade's service principal), `p9-07`, `p9-09`, `p9-10`, `p9-11`, `11-EPIC-p9`. Create carries tolerances, receiving location and ship-to; amend uses `newScheduleLines`; release cancel uses `unfirmScheduleLine`; whole-line release uses `firm(…, unitPrice)`; jobs call as the service principal. FRD-STORES OD-45 row updated. DATA-MODEL: rows for the three other `V510105` tables (`wh_order_edit_rule_actions`, `wh_order_amendments`, `wh_order_amendment_actions`), 475 → 478. Checker: 0 violations.
   - ~~**Open for STORES:** the trade amendment change type `TOLERANCE` has no field on core `amendOrder` `lineChanges`.~~ **Resolved 2026-10-23** (R30 `CP-GB-002`): `CN-8` / `STO-D25` — `lineChanges[]` carries `overTolerancePct?` / `underTolerancePct?` (FRD-STORES port registry R.2, `POS-T1-07`, `POS-GRD-15`, `p8-01`, `TOA-T4-02`, `p9-11`); the SO mirror pushes nothing by design (`TSO-T3-03`).
2. **SPINE integration — done 2026-10-22.** DATA-MODEL: P8 numbers renumbered (`V511310`…`V511323`, `V501230`…`V501235`); rows, §7 allocation, §8.1 inventory and §8.4 versions for `wh_port_operations`, `wht_price_list_categories`, `wht_rate_contract_amendment_changes`, the five `wht_so_*` mirror tables, `whm_staging_list_line_postings`, `whm_subcontract_reconciliation_actions`, `wh_fulfilment_policies` and five tables the P5 tasks built (`wh_recall_lots`, `wh_nrv_assessment_lines`, `wh_cogs_recognitions`, `wh_cogs_recognition_policies`, `wh3_billing_run_exclusions`): 459 → 475. IMPLEMENTATION-PLAN §2: renumbered; FR-654/655 → P10-07; FR-483 stays P7-03; P2-15 declares `warehouse-base` for `V500039`. DECISIONS: OD-45 (A) registered in §3.6 (still on the user's ratify list below); R27/R28/R29 in §6. Task exemptions the additions made unnecessary removed (p9-01, p9-06, p10-01, p10-06, p10-10). `FRD-TRADE` + trade contracts: `whb_uom_conversions` → `whb_item_uom_conversions`. The FRD-STORES OD-45 row was updated in the trade alignment (item 1).
3. **Checker to 0 repo-wide — done 2026-10-22** (69 → 0; 32 stale declarations removed). `V510105` also built `wh_order_edit_rule_actions`, `wh_order_amendments`, `wh_order_amendment_actions`, — added to DATA-MODEL in the trade alignment (item 1).
4. **Second dual-engine functional review** of the changed areas, to confirm the R29 fixes. Fold anything new.
5. **File the GitHub issues — done 2026-10-23:** EPICs #545–#548, tasks #549–#604 (see Execution plan step 2).
6. **BATCH files** in `classic/.claude/tasks/` via `/create-batch` (`BATCH-WAREHOUSE-P7…P10.md`, the same shape as `BATCH-WAREHOUSE-P*.md`, with the mandatory job text).
7. **Stop for the user's go** before `/run-batch`.
8. **Tracking — done 2026-10-23.** Every open warehouse work item now sits in exactly one open GitHub issue: 41 closed tasks reopened with a *Reopened scope — R30/R31 (2026-10-23)* section and the `reopened-r31` label; findings `W72` #606 and `W73` #607 filed (`issues/FINDINGS-2026-10-23.md`); the 103 contract-divergence rows triaged (49 FIX-CODE, 32 AMEND-SPEC, 14 CARRIED, 8 P7-REMOVES; 20 FRD rows and WS-144 amended). **Index: [`OPEN-WORK-INDEX.md`](OPEN-WORK-INDEX.md)** — 131 open issues, reconciled with `gh issue list --state open` (empty diff). Order: `P7` first, then the rest (*must run after P7* flag per row).

## Execution plan (user direction 2026-10-22) — identical to the earlier warehouse and accounting batches
Reference: `docs/reviews/BATCH-PATTERN-REFERENCE.md`, which summarises `classic/.claude/commands/{create-batch,run-batch}.md`, `classic/.claude/tasks/BATCH-DISPATCH-RULE.md`, `BATCH-STANDARD-PARITY-TEXT.md`, `BATCH-WAREHOUSE-P4.md`, `LANE-BRIEF-WAREHOUSE-P4.md` and `BATCH-ACCOUNTING-P1.md` / `-FR-GAPS.md`.

1. **Requirement completeness check before filing.**
   - Each area FRD's R29 dispositions table maps every review finding to the task that carries it.
   - Confirm that every FR and WH-SC in `docs/frd/*` is closed by exactly one `p7`…`p10` task (IMPLEMENTATION-PLAN §2; the checker's check-10 enforces this).
   - Run the second dual-engine review (Remaining item 4).
2. **GitHub issues first — done 2026-10-22**, in `neetub1508/warehouse-issues`:
   - **Filed:** EPICs P7 #545 · P8 #546 · P9 #547 · P10 #548; tasks **#549–#604** (P7 #549–#561, P8 #562–#577, P9 #578–#591, P10 #592–#604). Numbers written back to `issue:` and `CREATED.md`; the epic checklists and master #1 link them.
   - **R29 traceability:** one "R29 functional review findings carried by this task" comment on each of the 56 tasks (286 finding rows; P7-01, P8-12, P8-14 carry none).
   - **VOID (D-16, R28 §8b):** #149, #150, #151, #95, #67, #81, #134 closed as not planned. Commented with the void part and the superseding task: #90, #48, #52, #62, #72, #123, #144, #40, #87, #141, #152, #85, #142. `P2-27` #152 and `P6-11` #142 have wholly VOID headers but were kept open/comment-only, as directed.
   - **Verified:** `--check` no drift after `--sync`; checker 0 violations; `phase-p7`…`p10` labels 14 · 17 · 15 · 14 (tasks + epic).
   - **Findings are folded into tasks, not filed separately** (standing rule: never a duplicate task). Each task's R29 findings are on its issue as a comment.
3. **BATCH files** via `/create-batch`, one per phase: `classic/.claude/tasks/BATCH-WAREHOUSE-P7.md`, `-P8.md`, `-P9.md`, `-P10.md`.
   - Each has the mandatory job text, waves, `[P:lane]` / `[S]` / `[B]` markers, `#issue` on every task line, the OD BLOCKED-BY table, and a `## NEXT` line chaining P7 → P8 → {P9 ∥ P10}.
   - Each needs a lane brief, `LANE-BRIEF-WAREHOUSE-P7…P10.md`.
   - Phase order is a hard barrier: P7 (removal plus DB rebuild) must finish before P8.
4. **Run with `/run-batch` in its pipeline (loop) mode**, per `BATCH-DISPATCH-RULE.md`:
   - **S1 PRE-REVIEW:** the dual-engine functional-reviewer runs **before each task** and posts a PRE-BUILD FUNCTIONAL REVIEW gap list on the issue.
   - **S2 BUILD:** `--parallel 3`, file-disjoint lanes.
   - **S3 VERIFY:** reviewer plus functional-reviewer.
   - **S4 FIX.**
   - **S5 TEST:** tester, serialized.
   - **S6 CLOSE:** commit by name to `main`, then close the issue with the template.
   - Each round is one message: up to 4×S1, 3×S2, and every pending S3/S4.
   - Shared-registry barrier: lanes RETURN their lines for `filterUtils.ts`, `CacheConfiguration.java` and `*SafeTranslation.tsx`, and one writer applies them at wave end under `/tmp/claude-stack.lock`.
   - ci-gate is not run by the loop (manual).
   - Mobile: none (user rule).
5. **Stop for the user's go** before step 4 starts.

## R30 completeness audit (2026-10-23)
- **Audit — done.** `docs/reviews/R30-completeness-{github-a,github-b,requirements,screens,code}.md`.
- **User decisions — done.** `DECISIONS.md` **`D-17`** (contract rule per active FR; 12 mobile FRs DEFERRED; bonded/MOOWR issue = new `P10-14`, rule per location type `MD-42`; lost sale → trade sales; 7 VOID-owned FRs withdrawn, `FR-072`/`073` → `P7-11`, `FR-461` → `P8-10`; MFG ids `FR-670`…`679`, `WH-SC-680`…`699`; TRADE `FR-680`…`689`).
- **Fix wave 1 — done**, two agents plus a reconciler. Dispositions: `FRD-REM` §"R30 dispositions" (+ Appendix A.4), `FRD-STORES` §"R30 dispositions" (`STO-D21`…`STO-D25`), FRD-TRADE / FRD-MFG R30 tables. Reconciled: `P10-14` in plan §2 and the epic; DATA-MODEL 478 → **486** tables (`P10-14`'s five `whin_` tables, `whin_bonded_losses`, `P10-07`'s two Legal Metrology tables `V540193`/`V541161`; `bonded_duty_status`, `bond_permission_ref`, `expected_return_date`); `CN-8` resolved; Rule 56 classes owned once (store reasons `P8-10`/`P8-11`, MFG reasons `P10-02`, india classifier `P10-14`); `BATCH-WAREHOUSE-P6.md` `P6-02`/`P6-11`/`P6-12` marked `[!] VOID`. Checker 0.
- **Remaining, in order:**
  1. **Contract wave** — `CP-FR-007`: contracts for all **377** uncovered active FRs (+ 81 weak-only; the R30 26-row table names each contract), plus a checker check that **fails on an active FR with no contract rule** (R30 proposed checks 14–18). A live task's FRs are covered before its S1 pre-review.
  2. **Second dual-engine functional review** of the changed areas (R29 + R30 fixes). Also ratify or drop the 20 *(proposed)* MFG refusal codes (`CP-FR-009`; acceptance rows in `p10-05`, `p10-07`).
  3. **GitHub sync** — done 2026-10-23 (see R31 *Remaining* 1).
  4. **BATCH files** — `BATCH-WAREHOUSE-P7…P10.md` via `/create-batch` (Remaining 6 above), then stop for the user's go.
## R31 dual-engine functional review (2026-10-23)
- **Review — done.** `docs/reviews/R31-functional-review-{core-a,core-b,stores-rem,trade,mfg}.md`; decisions `docs/reviews/R31-decisions.md` (113 rows).
- **User decisions — done.** `DECISIONS.md` **`D-18`** (MOOWR loss + job work OFF, segments fenced / pharma declined, subcontract service PO lifts R9, 3PL freight tariff + true-up, putaway capacity block/warn, `FR-258` → `P10-11` and `FR-471` → `P8-13` restored).
- **Fix wave — done**, four agents plus a reconciler: **108 findings fixed, 113 decisions applied**. Reconciled: `CN-14` (b)/(c) defined as owed core changes (`WhCostObjectChargePort`, `CostObjectResolver.receivedOutput`, carrier `p8-09`, `V511324`); `ExternalPlanningOwner` / `RPN-GRD-11` (`MRP-OPEN-10`, `p8-16` + `p10-11`); TRADE scenario range `WH-SC-700`…`719` (`700`…`707` used, `p9-07`); `CROSS_GSTIN_DIRECT_ISSUE` on live rows; WS-096 manual lost-sale `POST` removed; `JOB_WORK_RETURN_FILED` carried by `p10-10`; DATA-MODEL 486 → **487** tables (`wht_po_service_confirmations`). Checker: 0 violations across 15 checks.
- **Remaining, in order:**
  1. **GitHub sync — done 2026-10-23.** `p10-14` filed as **#605** (CREATED.md, P10 epic #548 checklist); `--sync` pushed all 285 bodies (205 had drifted, incl. master #1 and epics #3–#11, #545–#548) — `--check` no drift; VOID closed not planned: #99 (P6-02), #142 (P6-11), #144 (P6-12), #152 (P2-27, was *completed*); D-16/D-18 reason comments on #102, #108 (VOID, already closed) and partial #73, #106, #124, #88; **102** "R30/R31 review findings carried by this task" comments (247 finding refs, 60 decision refs). Checker 0; no `issue: TBD`; phase labels match the files (GitHub-only #156–#161, #165–#177, #188 are the documented folded/follow-up issues).
  2. **BATCH files** — `BATCH-WAREHOUSE-P7…P10.md` via `/create-batch`.
  3. **Stop for the user's go.**

- Outside the program (platform): `CP-GB-010` (`ObjectStorageService.java:932` fallback list lacks `.csv`), `CP-GB-011` (server refusal text and platform toasts English in fr/hi).

## Pending user items (do not act without approval)
- `classic/CLAUDE.md`:
  - The SafeTranslation list names a non-existent `WarehouseAdapterDealerSafeTranslation.tsx`.
  - The MODULES table lacks `warehouse-trade` (V550000) and `warehouse-manufacturing` (V560000).
- Defaults to confirm:
  - REM-D15: new "Shipping" L1 menu.
  - OD-22: drop `supports_cod`.
  - OD-23: return types keep 3 and drop 2.
  - OD-45: (A), the demand header reopens to OPEN until `closeDemand`.
  - MD-25: no SCRAP stock status; scrap goes to VIRT-SCRAP.
  - The P7-13 DB drop only with an explicit go.
- R30 decisions for the user (defaults applied, confirm at the final review):
  - `REM-D20`: drop-ship stays in core as B2B direct ship (`CP-GA-009`).
  - `REM-D21` / `STO-D21`: `warehouse_trade` key retired; stores get their own L1 `warehouse_stores` (`CP-SC-001`, `-002`).
  - `CP-CODE-010`: logix outbound demo stays D2C — rename the `d2c` flag, or re-seed as B2B (new scope).
  - `CP-CODE-011`: keep `CORE`, `TYRE`, `JOB_ISSUE` (optionally reword `CORE`).
  - `CP-FR-012`: segment calls on `FR-443`–`FR-445` (style/variant) and `FR-456`/`FR-457` (pharma, `S-035`).
  - `CP-GB-008`: ratify `warehouse-india` job-work / delivery-challan contracts (before `P10-10`) and `goods-receipt.contract.md` (before `P8-04`/`P8-05`); the H1, regulated-items G7, registration-change G4, scan and lot/serial contracts are a ratification backlog.
- `classic` `fix/issue-105` (dealer migration `V20819` collides): left for a separate dealer task.
