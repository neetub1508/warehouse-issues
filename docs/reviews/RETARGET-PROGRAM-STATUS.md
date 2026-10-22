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
1. **Core changes trade needs (CN-1…CN-7) — done 2026-10-22.** STORES made CN-1…CN-5 and adopted CN-6 (`STO-D19`) and CN-7 (`STO-D20`); the FRD-STORES port registry and `po-schedule-port` carry them.
   - **Trade alignment — done 2026-10-22.** FRD-TRADE §12a/§12c, `TRD-13`, R29 rows TP-F6/F14/F24, TS-F1; contracts `TPO-T4-01`/`-02`/`-09`, `TSO-T4-01`, `TOA-T4-02`, `TPO-OPEN-01`, `TSO-OPEN-01`; `p9-01` (seeds trade's service principal), `p9-07`, `p9-09`, `p9-10`, `p9-11`, `11-EPIC-p9`. Create carries tolerances, receiving location and ship-to; amend uses `newScheduleLines`; release cancel uses `unfirmScheduleLine`; whole-line release uses `firm(…, unitPrice)`; jobs call as the service principal. FRD-STORES OD-45 row updated. DATA-MODEL: rows for the three other `V510105` tables (`wh_order_edit_rule_actions`, `wh_order_amendments`, `wh_order_amendment_actions`), 475 → 478. Checker: 0 violations.
   - **Open for STORES:** the trade amendment change type `TOLERANCE` (PO line over/under tolerance) has no field on core `amendOrder` `lineChanges`, so an amended tolerance stays trade-side and core's receipt guard keeps the create-time value.
2. **SPINE integration — done 2026-10-22.** DATA-MODEL: P8 numbers renumbered (`V511310`…`V511323`, `V501230`…`V501235`); rows, §7 allocation, §8.1 inventory and §8.4 versions for `wh_port_operations`, `wht_price_list_categories`, `wht_rate_contract_amendment_changes`, the five `wht_so_*` mirror tables, `whm_staging_list_line_postings`, `whm_subcontract_reconciliation_actions`, `wh_fulfilment_policies` and five tables the P5 tasks built (`wh_recall_lots`, `wh_nrv_assessment_lines`, `wh_cogs_recognitions`, `wh_cogs_recognition_policies`, `wh3_billing_run_exclusions`): 459 → 475. IMPLEMENTATION-PLAN §2: renumbered; FR-654/655 → P10-07; FR-483 stays P7-03; P2-15 declares `warehouse-base` for `V500039`. DECISIONS: OD-45 (A) registered in §3.6 (still on the user's ratify list below); R27/R28/R29 in §6. Task exemptions the additions made unnecessary removed (p9-01, p9-06, p10-01, p10-06, p10-10). `FRD-TRADE` + trade contracts: `whb_uom_conversions` → `whb_item_uom_conversions`. The FRD-STORES OD-45 row was updated in the trade alignment (item 1).
3. **Checker to 0 repo-wide — done 2026-10-22** (69 → 0; 32 stale declarations removed). `V510105` also built `wh_order_edit_rule_actions`, `wh_order_amendments`, `wh_order_amendment_actions`, — added to DATA-MODEL in the trade alignment (item 1).
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
