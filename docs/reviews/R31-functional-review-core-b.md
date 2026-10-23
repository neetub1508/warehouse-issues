**Summary (≤120 words).** The report file was not written because this reviewer may not write report files. The full report is below and is ready to save as `docs/reviews/R31-functional-review-core-b.md`. I found 23 defects: 0 High, 13 Medium, 10 Low. Six were found by both engines, 8 by Claude only and 9 by GPT only; none were dropped. Top 5:
1. **F-CB-006:** `accounting-handover` is stale against the build, and the WS-219 → WS-209 drill is still not wired.
2. **F-CB-004:** the 3PL go-live guard has the wrong rule and error code, and the offboard guards and their effects are missing.
3. **F-CB-008:** the supplier-return lifecycle has no transitions in the contract.
4. **F-CB-010:** `india-movement-documents` does not carry the job-work seam rules that `mfg-subcontracting` depends on.
5. **F-CB-014:** NFR-15 says every page has a Help button, but no 3PL page has one.

---

# R31 functional review — core contracts, batch B

Contract: 12 contracts in `warehouse-issues/docs/contracts/` (v0 2026-10-23, `accounting-handover` v1 ratified 2026-09-19) | Mode: audit
Files reviewed: 14 contracts (the 12, plus `mfg-subcontracting` and `mfg-bonded-issue` for alignment), FRD §6.13–6.25, BUILD-SPEC-SCREENS §7 and the screen rows, the owning tasks, and spot-checks of the code by grep in `classic/warehouse*` | File set: derived from the brief
Engines: Claude + GPT (gpt-6.1-sol, medium) — 6 both · 8 Claude only · 9 GPT only · 0 dropped

Paths: `docs/…` and `issues/…` are under `/Users/bbhushan/work/git/workspace/warehouse-issues`. Code paths are under `/Users/bbhushan/work/git/workspace/classic`.

## Verdict
23 findings (0 High · 13 Medium · 10 Low).

What passed:
- **FR coverage:** every active FR in §6.13–6.25 is cited by at least one contract.
- **Error codes:** every full error code named in the 12 contracts exists in the code.
- **Task links:** every live owning task carries a `Functional contracts:` line naming its contract. The only task without one is `p6-02`, which is VOID.
- **Divergence rows:** the recorded divergences I spot-checked by grep hold, except the two false ones (F-CB-018, F-CB-019).
- **Dealer/retail vocabulary:** no new instance in the contracts. The remaining ones are already recorded as removals or divergences: the RTO/MARKETPLACE return-type seeds and the `wh_rpt_parts_kpis` route. F-CB-022 covers the one copy left in BUILD-SPEC.

## Status reachability (exceptions only)
| Status | In CHECK / vocabulary | In contract T1 | Inbound | Outbound | UI | Verdict |
|---|---|---|---|---|---|---|
| e-way bill `CLOSED`, challan `CLOSED` | yes | inventory only | none | terminal | no | unreachable (F-CB-001) |
| replenishment `ACCEPTED` | yes | "active" | inside Accept | same transaction | no | never committed (F-CB-002) |
| 3PL client `SUSPENDED → LIVE` | refused by the ladder trigger | §0 shows ⇄ | none | — | no | promised, not built (F-CB-005) |
| supplier return DRAFT…CLOSED/CANCELLED | yes | inventory only, no T1 rows | code only | code only | yes | not contracted (F-CB-008) |
| e-way bill `EXPIRED` | derived on read, never stored | divergence row | n/a | n/a | filter only | wrong divergence (F-CB-019) |

## Findings

### F-CB-001 — Medium: India `CLOSED` states have no inbound transition
- Contract row: `india-movement-documents` §1.1 (delivery challan, e-way bill) · Source: Both
- Evidence:
  - `docs/contracts/india-movement-documents.contract.md:55-56` lists `CLOSED`, and no transition in `:68-83` reaches it.
  - `warehouse-india/backend/src/main/resources/db/migration/V540030__Create_whin_eway_bills_lines_and_events.sql:110`: "wave 1 offers no screen action that reaches it".
  - `warehouse-india/backend/src/main/java/ai/warehouseindia/entity/WhinDeliveryChallan.java:62` defines the status, and no code sets it.
- What a user experiences: no challan or e-way bill can ever be closed.
- Fix: mark both values as reserved, add an IMD-DIV row, and name the task that owns a close transition.

### F-CB-002 — Low: replenishment `ACCEPTED` is described as a lasting state
- Contract row: `RPN` §1.1, `RPN-T1-05/-06`, `RPN-GRD-04` · Source: GPT
- Evidence:
  - `docs/contracts/replenishment.contract.md:53,65-66` calls it "active" and gives it an exit.
  - `warehouse/backend/src/main/java/ai/warehouse/entity/WhReplenishmentSuggestion.java:35-37`: "a committed row is never left ACCEPTED".
- What a user experiences: there is no queue of accepted-but-unconverted suggestions.
- Fix: describe the user action as `PROPOSED → CONVERTED`, with `ACCEPTED` as a step inside the same transaction.

### F-CB-003 — Medium: `3pl-billing` has no T2 table, so permissions cannot be checked
- Contract row: `3pl-billing` (the §T2 section is missing; T1's Actor column gives service method names) · Source: Claude
- Evidence:
  - `docs/contracts/3pl-billing.contract.md:62-88` names the actor as `onboard`, `goLive`, `suspend`, `reverse` and so on.
  - The 3PL controllers gate these differently:
    - `go-live` is gated by `wh3_clients:onboard`.
    - `offboard` is gated by `wh3_clients:terminate`.
    - billing-run `/{id}/reverse` is gated by `wh3_billing_runs:create`.
    - `/{id}/emit-ar-handover` is gated by `wh3_billing_runs:emit_ar_handover`.
    - rate-card `/{id}/expire` is gated by `wh3_rate_cards:expire`.
- What a user experiences: who may reverse a frozen billing run (`:create`) is decided nowhere. A role meant to create runs can also reverse approved ones.
- Fix: add a T2 table listing action × permission × state for every T1 row. Then decide whether reversing a run should keep `:create` or get its own verb.

### F-CB-004 — Medium: 3PL go-live guard is wrong, and offboard guards and effects are missing
- Contract row: `TPB-T1-03`, `TPB-T1-06`; no T4 row for offboarding · Source: Both (go-live), GPT (offboard)
- Evidence:
  - Go-live:
    - `docs/contracts/3pl-billing.contract.md:66` says "every onboarding task COMPLETED, else 409 CLIENT_NOT_ONBOARDING".
    - The code refuses only open *blocking* tasks, with `BLOCKING_TASKS_OPEN` (`warehouse-3pl/…/service/wh3plclient/Wh3plClientValidationService.java:275-279`). It also checks the go-live date (`GO_LIVE_DATE_INVALID`).
    - The task agrees with the code: `issues/p5-01.md:139`.
    - `CLIENT_NOT_ONBOARDING` is actually the refusal for reopening a task (`Wh3plOnboardingTaskValidationService.java:36-40`).
  - Offboard:
    - The contract (`:69`) states no guard.
    - The code refuses with `CONTRACT_END_NOT_REACHED` (`Wh3plClientValidationService.java:224`) and `OFFBOARD_REQUIRES_UNSCOPED` (`:237`, 403), and asks the owner-has-stock rule (`:242`).
    - On success it ends every live owner grant and retires the owner (`Wh3plClientService.java:375-395`).
- What a user experiences: a client with optional tasks still open can go live. Offboarding refuses for reasons that are not documented, and it removes access beyond the client record.
- Fix: correct the T1-03 predicate and error code, add the offboard guards to T1-06, and add a T4 row for the grant and owner effects.

### F-CB-005 — Low: 3PL lifecycle rows are wrong or missing
- Contract row: `3pl-billing` §0 workflow; T1 has no rate-card expire row · Source: Both (suspend), Claude (expire)
- Evidence:
  - Suspend:
    - `docs/contracts/3pl-billing.contract.md:22` shows `LIVE ⇄ SUSPENDED`.
    - `Wh3plClientService.java:62-63` records "No SUSPENDED → LIVE", and the trigger at `V530010…sql:114-115` refuses it.
  - Expire:
    - `TPB-T5-03` offers "expire", but T1 has no expire row.
    - In the code, `Wh3plRateCardService.java:255-258` keeps the card `ACTIVE` and moves `effective_to` earlier.
- What a user experiences: a suspended client can only be terminated. Expire does not change status.
- Fix: make the §0 ladder one-way, and add a T1 row for expire with its guard (`validateExpiry`).

### F-CB-006 — Medium: `accounting-handover` is stale against the build, and the WS-219 drill is still not wired
- Contract row: §0 Routes / Permission resources, `AHO-X-06`, `AHO-RPT-05`, `AHO-OPEN-06`, Contract version · Source: Claude
- Evidence:
  - WS-219 and its permissions:
    - The contract says WS-219 is "TO BUILD" and its permissions are "TBD, not seeded anywhere" (`docs/contracts/accounting-handover.contract.md:37-38`).
    - In fact `WhStockToGlController.java` exists, and `V511065__Seed_wh_rpt_stock_to_gl_permissions_menu_and_grid.sql` seeds the permissions.
  - WS-209:
    - The contract says WS-209 is "not built" (`:38`, `:305`).
    - `WhMovementRegisterController.java` exists, and `reports-kpis` `RKP-T5-02` treats it as built.
  - `AHO-X-06` (`:194`) says "`wh_transfer_orders` does not exist", but `V510031` creates it.
  - `AHO-OPEN-06` says "CLOSED 2026-09-20" while its Status column reads OPEN (`:337`).
  - Line 40 says "RATIFIED v1", but line 41 says the version is `v0`.
  - The drill:
    - `warehouse/frontend/src/components/whStockToGl/WhStockToGlManagementTable.tsx:52` says "The Difference drill (`AHO-RPT-05`) is not wired".
    - Its target now exists, so this is now a missing entry point.
  - The contract has no `D-16` / `RN-054` deferral note, although the README cites one.
- What a user experiences: finance cannot drill a variance to the movements behind it. The contract misstates what is built.
- Fix: amend the BUILT/TO BUILD cells and the version. Raise the wiring of `AHO-RPT-05` → WS-209 as a task, and check WS-209's period and item-group filters (`AHO-OPEN-07e`).

### F-CB-007 — Medium: the landed-cost Reverse guard is missing from the contract
- Contract row: `CVL-T1-03` (Guard "—"), `CVL-GRD-09` · Source: Claude
- Evidence:
  - `docs/contracts/costing-valuation.contract.md:68` states no guard.
  - `warehouse/…/service/whlandedcost/WhLandedCostValidationService.java:147` allows Reverse only from `APPLIED` (`409 LANDED_COST_STATUS`).
  - `WhLandedCostPostingService.java:330-339` refuses a reversal once any loaded layer has been issued since apply (`409 LANDED_COST_LAYER_CONSUMED`, "Correct it with a revaluation instead"). Apply uses the same code at `:320-325`.
  - `LANDED_COST_CHARGE_KIND_INVALID`, `_COUNTERPARTY_INVALID` (validation service `:54,69`) and `_LOCATION_MISSING` (`:380`) are not in any guard row either.
- What a user experiences: once any of the stock it loaded has been issued, a landed cost can no longer be reversed. The contract does not say so.
- Fix: add the reverse guard and the missing codes to `CVL-GRD-08/-09` and `CVL-T1-03`.

### F-CB-008 — Medium: the supplier-return lifecycle has no contract rows
- Contract row: `returns-rma` §0 status columns, `RMR-T4-03`, `RMR-T5-05`; no T1 or T2 rows · Source: Both
- Evidence:
  - `docs/contracts/returns-rma.contract.md:29` lists six statuses for the supplier return. §1.2 (`:67-86`) has no supplier-return transition, and T2 gives only `wh_supplier_returns:*`.
  - In code, `WhSupplierReturnController.java:48` lists the verbs `:create/:edit/:approve/:close/:cancel`, and `:256-257` is Close. `WhSupplierReturnService.java:281-295` takes the return from DISPATCHED to CLOSED and marks the demand order delivered.
  - Approval is maker ≠ checker, refused with `SUPPLIER_RETURN_SELF_APPROVAL` (`WhSupplierReturnValidationService.java:147`).
  - `WhSupplierReturn.java:184` defines which statuses can be cancelled.
- What a user experiences: approve, close and cancel have permissions, refusals and side effects that no contract row can check.
- Fix: add T1, T2 and guard rows for the supplier return, and a T4 row for the demand-order effect.

### F-CB-009 — Medium: manual e-way evidence is a lifecycle the contract does not cover
- Contract row: `IMD-GRD-07`, `IMD-GRD-15`, `IMD-T5-02` · Source: GPT
- Evidence:
  - The IMD e-way transitions (`:70-74`) cover only filing through the provider.
  - `warehouse-india/…/controller/WhinEwayBillEvidenceController.java:71-72` records evidence under `whin_delivery_challans:record_eway_bill`.
  - `:83-84` records "cancelled at portal" under `:cancel_recorded_eway_bill`.
  - `WhinEwayBillDispatchGuard` accepts recorded evidence at dispatch.
- What a user experiences: a standalone install records e-way bills by hand, with permissions and refusals that are not contracted.
- Fix: add T1, T2 and T4 rows for evidence (including expiry and cancellation) to IMD, kept separate from the provider path.

### F-CB-010 — Medium: `india-movement-documents` does not carry the job-work seam rules that `mfg-subcontracting` relies on
- Contract row: IMD §0 Alignment, `IMD-T1-08`, `IMD-T4-05`, `IMD-UNR-03` versus `SUB-GRD-13`, `SUB-T4-06`, `SUB-T4-10`, `SUB-OPEN-04` · Source: Claude
- Evidence:
  - `mfg-subcontracting.contract.md:94` (`SUB-GRD-13`) expects india to refuse a reversal against a filed ITC-04 period with `409 JOB_WORK_RETURN_FILED`. IMD has no such guard, and the code has no such error code (grep finds only the audit `WHIN_ITC04_RETURN_FILED`).
  - `SUB-T4-06/-10` and resolved `SUB-OPEN-04` add `registerReturn` (return in processed form plus waste), `registerLoss` and `reverseReturn`, written to `V540190`. IMD's registration ladder (`:58`, `:75`) and `IMD-T4-05` name none of these, and IMD's primary tables omit `V540190/V540191/V540192`.
  - `IMD-T1-08` cites `SUB-T4-11` (the bonded row) as the path MFG dispatch takes. The general dispatch row is `SUB-T4-03`.
  - `issues/p10-10.md:5,46` ships the india bean and migration, but its `Functional contracts:` line (`:7`) omits `india-movement-documents`.
  - Consistent: return periods (`V541053:115`), `INPUTS`/`CAPITAL_GOODS`, one challan per dispatch, and the owner-unchanged trigger (`V540120:221-236`).
- What a user experiences: once MFG is built, a reversal against a filed ITC-04 return, or a write-off, has no india-side rule to enforce it.
- Fix: add IMD rows for the ITC-04 filed freeze, return in processed form, loss and reverse-return. Fix the reference to `SUB-T4-03`, and link `p10-10` to IMD.

### F-CB-011 — Medium: the FR-298 scheduled monthly export has no time rule
- Contract row: `TPB-T5-10` cites FR-298; T3 has no row for it · Source: GPT
- Evidence:
  - `docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:579` asks for "a scheduled monthly export".
  - `docs/contracts/3pl-billing.contract.md:126-131` has no matching T3 row.
  - `issues/p5-08.md:172` records that it is not built (it needs platform report scheduling).
- What a user experiences: a promised recurring export that nothing runs.
- Fix: add a T3 row (cadence, recipients scoped to the client's own owner, job) and a divergence row.

### F-CB-012 — Medium: the promised WS-049 `costBasis` filter does not exist
- Contract row: `CVL-T5-01` · Source: GPT
- Evidence:
  - `docs/contracts/costing-valuation.contract.md:160` promises a `costBasis` filter listing `RETURN_UNMATCHED`/`ESTIMATED`.
  - `V501119…sql:254` seeds `costBasis` only as a grid column; no filter row exists.
  - `WhbCostLayerFilter.tsx` and the `WAREHOUSE_COST_LAYER` scope in `platform/frontend/src/utils/filterUtils.ts` have no `costBasis`.
- What a user experiences: estimated and unmatched-return layers cannot be isolated in the grid.
- Fix: add a divergence row, or build the filter (filter migration, allowlist, query binding, filter component).

### F-CB-013 — Medium: WS-217 columns contradict BUILD-SPEC
- Contract row: `RKP-T5-10` · Source: Both
- Evidence:
  - The contract (`reports-kpis.contract.md:103`) lists `fillRate`, `inventoryTurns`, `obsolescencePct`, `daysSupply`. The code agrees (`WhPartsKpiRepositoryCustomImpl.java:128-137`), and so does `issues/p2-21.md:31-34`.
  - `docs/BUILD-SPEC-SCREENS.md:3200` lists `fillRate`, `serviceLevel`, `stockTurn`, `obsolescencePct`.
  - No divergence row records the difference.
- Fix: amend the BUILD-SPEC WS-217 row, or add an RKP divergence row.

### F-CB-014 — Medium: NFR-15's help threshold is not met, and its verification claim is wrong
- Contract row: `NFR-15` · Source: Claude
- Evidence:
  - `docs/contracts/non-functional.contract.md:49` sets the threshold "every warehouse page carries `HelpButton`" and cites as evidence "HelpButton in 111 warehouse frontend files".
  - Grep of `page.tsx` files:
    - warehouse-3pl: 0 of 18 pages, and 0 files anywhere in `warehouse-3pl/frontend/src`.
    - warehouse-india: 0 of 27 pages (10 component files carry it).
    - warehouse-base: 73 of 75 (`platform/port-monitor`, `platform/port-rejected` lack it).
    - warehouse: 107 of 108.
- What a user experiences: 3PL and India screens have no in-product help.
- Fix: correct NFR-15's evidence, add an NFR-DIV row, and mechanise the check (a page scanner in the ratchets).

### F-CB-015 — Medium: the web halves of FR-430 and FR-431 are left uncovered
- Contract row: `non-functional` Status / Scope · Source: GPT
- Evidence:
  - `docs/contracts/non-functional.contract.md:10-12` excludes `FR-430`/`FR-431` entirely.
  - `docs/DECISIONS.md:558-564` (D-17 b) defers only the mobile half: "a `base`/`app`/`platform` half … stands".
  - The surviving obligations are the paper fallback and catch-up entry (FR-430) and three locales on every translation file (FR-431).
  - `issues/p3-04.md` has "Functional contracts: none", and `issues/p1-19.md`'s line omits `non-functional`.
- Fix: add NFR rows with a threshold and a place of verification for each web half, and link `p3-04` and `p1-19` to them.

### F-CB-016 — Low: outbox cursor assignment is not "at commit"
- Contract row: `OEV-T1-02`, §0 · Source: GPT
- Evidence:
  - `outbox-events.contract.md:22,58` says cursors are assigned at commit.
  - `warehouse-base/…/service/outbox/WhbOutboxSequencer.java:63` sequences in its own transaction (`REQUIRES_NEW`), run later by the publisher in batches (`batch-size 5000`).
- What a user experiences: a committed posting's events can sit in staging, with no cursor yet.
- Fix: state the producer-commit-then-sequencer boundary and the staging backlog.

### F-CB-017 — Low: validate and the stored dry run are run together
- Contract row: `IGL-T1-01`, `IGL-UNR-01` · Source: GPT
- Evidence:
  - `import-go-live.contract.md:58,88` treats them as one step.
  - `WhbImportBatchController.java:38-41`: `POST /validate` "persists nothing", while `POST /` "stores the dry run" that apply later uses.
- Fix: split them into two transitions, and state what each one persists.

### F-CB-018 — Low: false divergence — the purchase order does carry `ownership_transfer_point`
- Contract row: `costing-valuation` §10 row 6, `CVL-GRD-18` · Source: Both
- Evidence:
  - `costing-valuation.contract.md:203` says the column is absent.
  - `V510011__Create_wh_purchase_orders_and_lines.sql` creates it, and `WhPurchaseOrder.java:178` maps it.
  - `OEV-GRD-10` and `AHO-X-07` state it correctly.
- Fix: delete the row and correct `CVL-GRD-18`.

### F-CB-019 — Low: false divergence — e-way `EXPIRED` is derived on purpose
- Contract row: `IMD-DIV-05` · Source: GPT
- Evidence: `WhinEwayBill.java:68-74` says "DERIVED, never stored … must never join the WHIN_EWAY_BILL_STATUS list".
- Fix: replace the divergence with a rule saying `EXPIRED` is a derived display and filter value only.

### F-CB-020 — Low: NFR-17 names a column that does not exist
- Contract row: `NFR-17` · Source: GPT
- Evidence:
  - The contract names `whb_style_variant_axes.sort_order`. That table's column is `sequence` (`V500015…sql:412`).
  - Size values are ordered by `whb_item_variant_axis_values.sort_order` (`V500014…sql:82`).
- Fix: point the verification at the value-level `sort_order` and the code that sorts by it.

### F-CB-021 — Low: `reports-kpis` contradicts itself
- Contract row: `RKP-T5-15`, `RKP-OPEN-01`, `RKP-T3-02` · Source: Claude
- Evidence:
  - `reports-kpis.contract.md:108` says "the FRD row is not marked withdrawn". `RKP-OPEN-01` (`:131`) and the FRD (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:744`) both show FR-397 withdrawn.
  - `RKP-T3-02` contracts the WS-223 health signals (FR-398), while §6 (`:112`) puts WS-223 out of scope.
- Fix: update T5-15, and either move T3-02 to its owning contract or remove WS-223 from §6.

### F-CB-022 — Low: WS-135 in BUILD-SPEC still lists retail return types
- Contract row: `RMR-T5-01`, `RMR-GRD-01` · Source: Claude
- Evidence:
  - `docs/BUILD-SPEC-SCREENS.md:2735` lists `returnType` values including `RTO` and `MARKETPLACE`.
  - The contract removes them, but §10 row 1 cites only the seed (`V500010…sql:155,161`).
- Fix: amend BUILD-SPEC WS-135, or add it to §10 row 1.

### F-CB-023 — Low: wrong or missing refusal codes, and an internal contradiction in VWO
- Contract row: `IMD-T1-04`, `VWO-T1-03`, `VWO-T4-01` / `VWO-UNR-05` · Source: Claude
- Evidence:
  - `PART_B_EMPTY` is a Part-B *status* value (`WhinEwayBill.java:105` = `"EMPTY"`), not a refusal. The real refusals are `VEHICLE_NUMBER_REQUIRED`, `TRANSPORT_MODE_REQUIRED` and so on (`WhinEwayBillValidationService.java:71-77`).
  - The "at least one input issued" guard has the code `WORK_ORDER_NO_INPUT_ISSUED` (`WhWorkOrderValidationService.java:547`), which the contract leaves out.
  - `VWO-T4-01` posts +(A−S) for every OUTPUT line, but `VWO-UNR-05` and `WhWorkOrderPostingService.java:411-412` say a VAS OUTPUT posts nothing.
- Fix: correct the codes, and add the VAS exception to T4-01.

## Dropped after verification
- None. Every GPT-only finding was re-read at its cited file and line and held.

## Remediation backlog
All contract paths are under `docs/contracts/`.

| Finding | Files to touch | Migration | Shared registries | Parity apply-to | Contract |
|---|---|---|---|---|---|
| F-CB-001 | `india-movement-documents.contract.md` | none | none | none (desk only) | IMD §1.1, new DIV row |
| F-CB-002 | `replenishment.contract.md` | none | none | none | RPN §1.1, T1-05/06 |
| F-CB-003 | `3pl-billing.contract.md`; `Wh3plBillingRunController` reverse permission if changed | next free in V531000–V539999 if a new verb | `permission_dependencies` if a new verb | none | new T2 table |
| F-CB-004 | `3pl-billing.contract.md` | none | none | none | TPB-T1-03, T1-06, new T4 row |
| F-CB-005 | `3pl-billing.contract.md` | none | none | none | §0, new T1 row for expire |
| F-CB-006 | `accounting-handover.contract.md`; `WhStockToGlManagementTable.tsx` (drill) | none | none | none | §0, AHO-X-06, RPT-05, OPEN-06 |
| F-CB-007 | `costing-valuation.contract.md` | none | none | none | CVL-T1-03, GRD-08/09 |
| F-CB-008 | `returns-rma.contract.md`; `issues/p2-13.md` | none | none | none | new supplier-return T1/T2/T4 rows |
| F-CB-009 | `india-movement-documents.contract.md` | none | none | none | new IMD evidence T1/T2/T4 rows |
| F-CB-010 | `india-movement-documents.contract.md`; `issues/p10-10.md` line 7 | none | none | `mfg-subcontracting`, `mfg-bonded-issue` | new IMD guard and T4 rows |
| F-CB-011 | `3pl-billing.contract.md`; `issues/p5-07.md`, `p5-08.md` | none | platform scheduled reports | none | new T3 row and DIV row |
| F-CB-012 | `costing-valuation.contract.md`, or migration → `WhbCostLayerFilter.tsx` | next free in V501000–V509999 if built | `filterUtils.ts` `WAREHOUSE_COST_LAYER` | none | CVL-T5-01 |
| F-CB-013 | `docs/BUILD-SPEC-SCREENS.md` WS-217 | none | none | none | RKP-T5-10 or new DIV row |
| F-CB-014 | `non-functional.contract.md`; 3PL, India and two base `page.tsx` files if fixed | none | none | warehouse-3pl, warehouse-india, warehouse-base | NFR-15, new NFR-DIV row |
| F-CB-015 | `non-functional.contract.md`; `issues/p3-04.md`, `p1-19.md` | none | SafeTranslation (FR-431) | none | new NFR rows |
| F-CB-016 | `outbox-events.contract.md` | none | none | none | OEV-T1-02 |
| F-CB-017 | `import-go-live.contract.md` | none | none | none | IGL-T1-01, UNR-01 |
| F-CB-018 | `costing-valuation.contract.md` | none | none | none | §10 row 6, GRD-18 |
| F-CB-019 | `india-movement-documents.contract.md` | none | none | none | IMD-DIV-05 |
| F-CB-020 | `non-functional.contract.md` | none | none | none | NFR-17 |
| F-CB-021 | `reports-kpis.contract.md` | none | none | none | RKP-T5-15, T3-02, §6 |
| F-CB-022 | `docs/BUILD-SPEC-SCREENS.md` WS-135 | none | none | none | RMR §10 row 1 |
| F-CB-023 | `india-movement-documents.contract.md`, `vas-work-order.contract.md` | none | none | none | IMD-T1-04, VWO-T1-03, T4-01 |

## Parity (C10)
- **Mobile:** none. Every contract states "mobile: none" under D-16 item 7 / D-17, and that decision is recorded. F-CB-015 covers the web halves that survive the deferral.
- **Siblings:** warehouse-base, warehouse, warehouse-3pl, warehouse-india and warehouse-adapter-example. The F-CB-014 fix applies to all three page sets. The F-CB-010 seam also affects the future warehouse-manufacturing module.

## Contract quality
- The 11 contracts dated 2026-10-23 are unratified v0. `accounting-handover` is ratified, but its 2026-09-20 amendments were never folded back into its §0, T4 and §9 cells (F-CB-006).
- **Not verified:** the full four-link chain (endpoint → API client → handler → button) for every T1 row, i18n in every locale, export parity with the visible columns, and statistics tiles. No build or runtime run was done.

## Referred to standards reviewer
- None.