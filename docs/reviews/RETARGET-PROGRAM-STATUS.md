# Re-target program (D-16) — status and remaining steps

**Read this first when resuming.** Updated 2026-10-22. All work happens on `main` only (user rule).

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
1. **STORES owes the core changes trade needs**, CN-1…CN-5 from FRD-TRADE §12c:
   - CN-1: the release price reaches core.
   - CN-2: `newScheduleLines` on `amendOrder`.
   - CN-3: ship-to on create/amend demand.
   - CN-4: an OPEN demand line with no schedule is schedule-driven.
   - CN-5: remove the duplicate overdue digest.
   - CN-6 and CN-7 are recommended only; decide them.

   Then update the FRD-STORES port registry. The trade files must still match afterwards.
2. **SPINE integration:**
   - IMPLEMENTATION-PLAN §2: move FR-654/655 to P10-07.
   - DATA-MODEL: add `whm_staging_list_line_postings` and the new p9-06 tables.
   - DATA-MODEL: new P8 numbers, `wh_port_operations`, `whm_subcontract_reconciliation_actions`, any new trade/mfg tables.
   - IMPLEMENTATION-PLAN §2: renumbered migrations; resolve the FR-483 owner (P7-03 vs P7-04).
   - Confirm OD-45, which sits outside the STORES OD range.
   - FRD-MFG, mfg-qc-rework, p10-01 and p10-02 still cite the old P8 migration numbers.
3. **Checker to 0 repo-wide**, including the 66 violations that predate D-16 (`CREATED.md`, p5 tasks, reference downloads, DESIGN-SET-DEFECTS).
4. **Second dual-engine functional review** of the changed areas, to confirm the R29 fixes. Fold anything new.
5. **File the GitHub issues:** `issues/create-issues.sh --file-tbd` (4 EPICs P7–P10, then the tasks). Write the numbers back, update `CREATED.md`, commit and push.
6. **BATCH files** in `classic/.claude/tasks/` via `/create-batch` (`BATCH-WAREHOUSE-P7…P10.md`, the same shape as `BATCH-WAREHOUSE-P*.md`, with the mandatory job text).
7. **Stop for the user's go** before `/run-batch`.

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
- `classic` `fix/issue-105` (dealer migration `V20819` collides): left for a separate dealer task.
