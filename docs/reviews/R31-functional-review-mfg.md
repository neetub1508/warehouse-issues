**Summary (≤120 words).** I could not write `docs/reviews/R31-functional-review-mfg.md`: this agent may not write report files. The full report is below for you to save. **23 findings: 5 High, 13 Medium, 5 Low.** Both engines ran. Top 5:
1. **F-MF-001**: any generic-port caller can post or reverse MFG movement types by naming MFG's source system and document type, which gets past MD-35's guard.
2. **F-MF-002**: the reservation recipes never close the holds they hand to the writer, and a partial dispatch leaves the rest of the hold unprotected. This means the R29 F3/F17 fixes are not complete.
3. **F-MF-003**: MRP plans subcontract components that are already at the job worker as a fresh shortage.
4. **F-MF-004**: bonded inputs can end up in output that is not in bond (late issue after outputs, or mixed duty statuses across dispatches).
5. **F-MF-005**: trade refuses subcontract/service POs and MFG relies on them, so no module owns the processing charge.

---

# Functional conformance — warehouse-manufacturing (P10), second review after R29/R30
Contract: 9 × `docs/contracts/mfg-*.contract.md` (all v0, unratified) | Mode: audit (design set, pre-build)
Files reviewed: 26 (FRD-MFG, 9 contracts, p10-01…p10-14, 12-EPIC-p10), plus targeted reads of FRD-STORES, FRD-TRADE, `store-issue-return` / `material-requisition` contracts, `IMPLEMENTATION-PLAN.md`, `SCENARIO-CATALOGUE.md` and classic code (`warehouse-base`, `warehouse-india`) | File set: given by the caller
Engines: Claude + GPT (gpt-6.1-sol, medium) — 6 both · 10 Claude only · 7 GPT only · 0 dropped

Paths are relative to `/Users/bbhushan/work/git/workspace/warehouse-issues`. `WB/` = `classic/warehouse-base/backend/src/main` and `WI/` = `classic/warehouse-india/backend/src/main`.

## Verdict
23 findings: 5 High, 13 Medium, 5 Low.

**What is already in order:**
- **Proposed error codes.** All 20 *(proposed)* codes are acceptance items: 14 at `issues/p10-05.md:100` and 6 at `issues/p10-07.md:116`. Their residue is F-MF-019.
- **FR-268.** It is withdrawn (`docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:527`) and `p6-12` is VOID. The residue is F-MF-022.
- **MD-42.** The per-location-type key is implemented in the p10-14 seed.
- **R29 dispositions.** F1, F2, F4, F6–F16 and F18–F32 are present where §R29 says they are. F3 and F17 (F-MF-002) and F5 (F-MF-001) are not fully fixed.

## Status reachability
| Document | In CHECK | In contract T1 | Inbound | Outbound | UI reachable | Verdict |
|---|---|---|---|---|---|---|
| BOM DRAFT/SUBMITTED/APPROVED/OBSOLETE | no (D-10) | yes | yes | yes | WS-320 | ok |
| Order PLANNED…CLOSED/CANCELLED | no | yes | yes | yes | WS-323/324 | the close guard conflicts (F-MF-006) |
| Staging list | no | yes | yes | yes | WS-325 | CLOSED can keep line-side stock (F-MF-006) |
| Receipt / reversal | no | yes | yes | yes | WS-326/327 | ok |
| Settlement | no | yes | yes | yes | WS-329 | ok |
| Dispatch / reconciliation action | no | yes | yes | yes | WS-330 | F-MF-002, F-MF-013 |
| Demand plan / MRP run / proposal | no | yes | yes | yes | WS-332…335 | F-MF-015, F-MF-016 |
| MOOWR return DRAFT/FILED | no | yes | yes | FILED is terminal | WS-339 | F-MF-009 |
| `JOB_WORK_OUT` *open* (derived) | — | yes | yes | **no path for a write-off** | — | F-MF-007 |

## Findings

### F-MF-001 — High (permission weaker than the contract): MD-35's ownership guard can be satisfied by anyone who names MFG's source fields
- Contract row: MD-35, SUB-UNR-02, MPR-GRD-35
- Source: GPT (verified)
- Location: `issues/p10-02.md:61-66`, `issues/p10-01.md:110`
- Evidence:
  - The guard passes a post as soon as `sourceSystem = WAREHOUSE_MANUFACTURING` and `sourceDocumentType` is the owning document type. It does not load the document or check its state (`issues/p10-02.md:63-65`).
  - p10-01 seeds `WAREHOUSE_MANUFACTURING` in `whb_source_systems` without `is_claimable = false` or a `post_permission`.
  - The column defaults are `is_claimable = true` and a null `post_permission` (`WB/resources/db/migration/V500002…sql:63-64`).
  - The movement port's only check on the source system is `WhbPortReferenceResolver.requireClaimable` (`WB/java/…/port/WhbPortReferenceResolver.java:~101-118`).
  - The precedent the task cites does load and validate its document (`WhCountAutoPostGuard`).
- What a user experiences: a holder of the generic movement-port post permission can post a `PRODUCTION_RECEIPT` or reverse a `SUBCONTRACT_DISPATCH` outside its document. The rollups, the cost pool and the reconciliation then drift.
- Fix: seed the source system unclaimable (or with a `post_permission` no human holds), and have the guard check that the document exists and is in a state that allows the post or reversal.

### F-MF-002 — High (guard / effect missing): the reservation recipes confuse the availability exemption with consuming the hold, and a partial dispatch drops the rest of the hold
- Contract row: MSI-T4-06, MSI-T4-07, MSI-T4-08, PRC-T4-01, SUB-T4-01; MD-31, MD-36 (R29 F3, F17)
- Source: GPT (verified)
- Evidence:
  - `WB/java/…/ledger/writer/WhbMovementPostCommand.java:23-25` says the caller must close each id passed in `consumedReservationIds` as CONSUMED. Passing them to the writer only exempts them from the availability check (`WhbStockPositionWriter.java:231`). Closing a hold is a separate call, `WhbReservationStore.consume` (`:232`).
  - `docs/contracts/mfg-material-staging-issue.contract.md:142` step (1) says "the movement consumes" the hold.
  - `docs/contracts/mfg-subcontracting.contract.md:154` passes the holds and says they are "**not** re-created", with no re-creation of the remainder at the source.
  - STORES spells out the caller-side consume-and-split (`store-issue-return.contract.md` SIR-T4-01, MRQ-T4-02). The MFG recipes do not.
- What a user experiences: the holds stay open until the order closes, and availability is understated. Or, once consuming is added, dispatching 40 against a 100-unit hold closes all 100 and leaves 60 unprotected.
- Fix: in every MFG posting recipe, require the caller to consume the hold explicitly, and re-create the source remainder for a partial stage, unstage, receipt or dispatch. Only the dispatched quantity gets no hold at the `JOB_WORKER` location.

### F-MF-003 — High (data diverges): MRP plans subcontract inputs already at the job worker as a new shortage
- Contract row: MRP-N-04, MRP-N-05, SUB-T4-04
- Source: Both
- Evidence:
  - Dependent demand is `required − consumed − staged-not-consumed` (`docs/contracts/mfg-mrp.contract.md:126`).
  - `consumed` is "backflushed + issued − returned" (`docs/frd/FRD-MFG.md:247-248`), so dispatched stock is in neither term.
  - `JOB_WORKER` stock is excluded from supply (`mfg-mrp.contract.md:127`).
  - A dispatch moves reconciliation `sent`, not `consumed` (`mfg-subcontracting.contract.md:68,157`).
- What a user experiences: after all 200 `SHAFT-03` are dispatched (WH-SC-645), MRP proposes buying or making 200 more.
- Fix: in MRP-N-04, subtract the open reconciliation quantity (sent − consumed − scrap retained − recalled − written off) for `SUBCONTRACT` orders.

### F-MF-004 — High (data diverges): the bonded regime freeze can be bypassed, so bonded inputs end up in output outside bond
- Contract row: BND-T4-03, BND-GRD-04, FR-673, MD-43, MSI-GRD-01
- Source: Both (the late-issue half from both engines; the dispatch half Claude only)
- Evidence:
  - The regime freezes on a store issue or a receipt backflush, and only later outputs inherit it (`docs/contracts/mfg-bonded-issue.contract.md:127`).
  - **Late issue:** a store issue is admitted on a `COMPLETED` order (`mfg-material-staging-issue.contract.md:88`, MD-14), but a `COMPLETED` order takes no receipt (`mfg-production-receipt.contract.md:93`). Earlier receipts may already have posted their output `DOMESTIC`. FR-673 requires every output of such an order to stay in bond (`FRD-MFG.md:426`).
  - **Dispatch:** a subcontract dispatch is not a freeze point. MOOWR and BONDED lines can go to the job worker for one order across two dispatches. The refusal `BONDED_REGIME_MIXED` arrives only at the subcontract receipt, when the stock is already out and can only be recalled.
- What a user experiences: MOOWR inputs are consumed into `DOMESTIC` output with no exit record. Or a subcontract receipt is refused for good after the goods are at the job worker.
- Fix: make the subcontract dispatch freeze and check the regime. Refuse the first licensed consumption on an order that is `COMPLETED` or has posted output outside that regime. Add scenarios for both cases.

### F-MF-005 — High (no owner): trade refuses the service / subcontract PO that MFG relies on
- Contract row: FR-658; SUB §6; SUB-OPEN-06
- Source: Both
- Evidence:
  - FRD-MFG: "optional frozen **service PO reference** (`p9-07`); the processing charge is trade's and accounting's" (`docs/frd/FRD-MFG.md:411`).
  - `issues/p10-10.md:9,34` depends on `p9-07` for this.
  - SUB says "trade (`p9-07` service PO)" (`mfg-subcontracting.contract.md:198`), and SUB-OPEN-06 gives trade the landed-cost path (`:231`).
  - FRD-TRADE §11 refuses **R8 "Service POs"** ("Stock items only") and **R9 "Subcontract / job-work PO"** (owner "`warehouse-india` + MFG") (`docs/frd/FRD-TRADE.md:612-613`). `p9-07` is a stock PO task.
- What a user experiences: a job worker can never be ordered or paid through the system. The processed item carries no processing charge, and each FRD names the other as the owner.
- Fix: pick one owner. Either trade lifts R8/R9 for a service-line PO linked to the subcontract order (and owns SUB-OPEN-06), or `service_po_ref` becomes a free external reference and both FRDs record the charge as accounting-only.

### F-MF-006 — Medium (guard missing / drift): the close guard is defined three ways, and closing a staging list gets around it
- Contract row: PRO-GRD-15, CST-GRD-02…-08, MSI-T1-07, MSI-T4-11, SUB-GRD-14
- Source: Both
- Evidence: each contract defines the close blockers differently.

  | Where | What blocks close | Code |
  |---|---|---|
  | PRO-GRD-15 (`mfg-production-order.contract.md:120`) | staging list `RELEASED` / `PARTIALLY_STAGED` | `ORDER_CLOSE_BLOCKED` *(proposed)* |
  | CST-GRD-02 (`mfg-costing-close.contract.md:79`) | non-terminal staging list with line-side stock | `ORDER_HAS_OPEN_STAGING` |
  | MSI-T4-11 (`mfg-material-staging-issue.contract.md:146`) | "any line-side balance" | — |

  - CST-GRD-03/-05/-07/-08 add four more codes that PRO-GRD-15 does not list.
  - SUB-GRD-14 blocks on a `DRAFT` dispatch; CST-GRD-04 does not.
  - MSI-T1-07 closes a `STAGED` list with no stock check, and CST-T4-07 then releases every order hold.
- What a user experiences: staged material sits at the line side with no HARD hold after close. The refusal code depends on which contract the builder followed.
- Fix: CST owns the close guard. Check the actual line-side balance whatever the staging-list status, and make PRO-GRD-15 cite CST. Drop `ORDER_CLOSE_BLOCKED` from p10-05's ratification list.

### F-MF-007 — Medium (effect missing): an approved write-off of bonded stock at the job worker never reduces the open job-work quantity
- Contract row: BND-T4-06, BND-T3-01, FR-672, FR-675
- Source: Claude
- Evidence:
  - The p10-14 rule seed has no `SUBCONTRACT_WRITE_OFF · JOB_WORKER · FALL` row; write-off appears only as `SCRAP · RISE → LOSS` (`issues/p10-14.md:40-49`).
  - Only `JOB_WORK_RETURN` rows reduce `open_quantity` (FR-672, `FRD-MFG.md:425`; `mfg-bonded-issue.contract.md:130`). FR-675 says "a write-off is FR-674".
  - The status inventory still lists "loss" as an exit (`mfg-bonded-issue.contract.md:58`).
- What a user experiences: after WH-SC-648's approved write-off on MOOWR stock, the bond register shows 2 still out, and the overdue compliance task (BND-T3-01) never closes.
- Fix: seed a `SUBCONTRACT_WRITE_OFF · JOB_WORKER · FALL` rule whose kind reduces the open quantity (or have the LOSS row carry `source_line_id`), and add a bonded write-off scenario.

### F-MF-008 — Medium (contradiction): the register's stored `open_quantity` contradicts its append-only rule, and reversal and matching are undefined
- Contract row: BND-UNR-03, BND-T4-02, BND-T4-06
- Source: Both
- Evidence:
  - The append-only table carries `open_quantity`, "derived on write", plus `source_line_id` (`issues/p10-14.md:53-57`).
  - BND-UNR-03 forbids updating a register line (`mfg-bonded-issue.contract.md:89`), but return rows must reduce the dispatch row's `open_quantity` (`:130`).
  - BND-T4-02 does not say that reversing a subcontract receipt (SUB-T1-07) re-opens the quantity and re-arms BND-T3-01. It only says a `JOB_WORK_OUT` mirror re-opens nothing (`:126`), and a dispatch is never reversed.
  - Nothing says how a backflush line picks *which* `JOB_WORK_OUT` row it reduces when an order has several dispatches, or which kind `*_REVERSAL` types (which have no rule row) map to.
- What a user experiences: either the append-only trigger refuses the return, or open quantities and overdue tasks go stale, especially after a receipt reversal.
- Fix: derive the open quantity from immutable out / return / loss / mirror rows (or keep it in a separate mutable projection). State the matching rule (FIFO by dispatch for the item and lot) and how reversals map to kinds.

### F-MF-009 — Medium (data diverges): the MOOWR return deducts an in-process loss twice
- Contract row: BND-T4-07, WH-SC-682, WH-SC-686
- Source: Claude
- Evidence:
  - WH-SC-680 issues 40 MOOWR `CASING-01` (supply `ISSUE`) into `VIRT-PRODUCTION`. WH-SC-682 then scraps 2 of them in the receipt, written as `LOSS` 2 (`FRD-MFG.md:653,655`).
  - For an issued component, PRC-T4-01(b) scraps from the issued pool (`mfg-production-receipt.contract.md:167`).
  - WH-SC-686 states the closing as 100 − 40 − 2 = **58** (`FRD-MFG.md:659`), while the store ledger still holds **60** MOOWR.
  - The job-work path counts retained scrap *inside* `JOB_WORK_RETURN` (WH-SC-683, `:656`), so the two paths are inconsistent.
- What a user experiences: the filed return disagrees with the bonded stock on hand by every unit lost in process.
- Fix: report loss of goods already issued to manufacture as process waste, not as a further deduction from bonded stock. Correct WH-SC-686 to 60.

### F-MF-010 — Medium (contract gap): the receipt contract and p10-07 carry no bonded output rule, although p10-14 changes the receipt post
- Contract row: PRC-T4-01, PRC-GRD-10; BND-T4-03
- Source: Claude
- Evidence:
  - `issues/p10-14.md:83-86`: "a change to … `p10-07`'s receipt post, made here".
  - `mfg-production-receipt.contract.md` mentions duty status only as a balance key (`:167`). MSI and SUB were amended (MSI-GRD-11, MSI-T4-12, SUB-GRD-17, SUB-T4-11); PRC was not.
  - The `**Functional contracts:**` line of p10-14 (`issues/p10-14.md:7`) omits `mfg-production-receipt`.
- What a user experiences: the receipt builder and its reviewer are never sent to the rule that outputs go into the frozen duty status (FR-673).
- Fix: add PRC rows for output duty status and `BONDED_REGIME_MIXED` at backflush, and link PRC from p10-14.

### F-MF-011 — Medium (guard missing): a store issue or staging list against a `SUBCONTRACT` order is not refused
- Contract row: MSI-GRD-01, MSI-T1-01, MSI-T1-02, SIR-GRD-01a; FR-661
- Source: Claude
- Evidence:
  - MSI-GRD-01 and SIR-GRD-01a check only status, hold and settlement (`mfg-material-staging-issue.contract.md:88`; `store-issue-return.contract.md:75`).
  - A subcontract receipt backflushes **every** component from the job-worker location whatever the supply method (FR-661; `mfg-subcontracting.contract.md:71`).
  - SUB-T1-00 keeps the BOM's supply method (`:65`).
- What a user experiences: a store issue to a subcontract order lands in `VIRT-PRODUCTION`, counts as consumed and enters the cost pool. The receipt then backflushes the same requirement again from the job worker, which double-consumes or refuses `BACKFLUSH_SHORTAGE`.
- Fix: have `assertIssuable`, Request materials and staging generation refuse `order_type = SUBCONTRACT`, and send the user to Dispatch instead.

### F-MF-012 — Medium (guard wrong): the STRICT issue formula ignores returns and unstaging and double-counts staged ISSUE lines
- Contract row: MSI-GRD-06
- Source: GPT (verified)
- Evidence:
  - The limit is "cumulative issued + staged + this ≤ required × (1 + tolerance)" (`mfg-material-staging-issue.contract.md:93`). It subtracts neither returned nor unstaged quantity.
  - `ISSUE` lines may also be staged (`:70`).
- What a user experiences: issue 100, return 20, re-issue 20 is refused. Staging and then issuing the same 100 counts as 200.
- Fix: use net, non-overlapping quantities, i.e. (issued − returned) + (staged − unstaged − consumed at line side) + this.

### F-MF-013 — Medium (guard wrong): a pending write-off is subtracted twice
- Contract row: SUB-GRD-15
- Source: GPT (verified)
- Evidence: `open_base_quantity` already subtracts pending write-off (`FRD-MFG.md:311`; `mfg-subcontracting.contract.md:56`), and SUB-GRD-15 subtracts it again (`:96`).
- What a user experiences: with 100 out and 40 pending write-off, a recall of 60 is refused above 20.
- Fix: compare against `open_base_quantity` alone.

### F-MF-014 — Medium (capability gap): MRP has no planning path for a subcontracted item
- Contract row: MRP-N-02, MRP-N-14, MRP-GRD-11, MRP-T4-03
- Source: Claude
- Evidence:
  - Low-level codes come from `PRODUCTION` BOMs only (`mfg-mrp.contract.md:124`).
  - A MAKE item without a `PRODUCTION` BOM gets `NO_BOM` (`:136`).
  - A MAKE convert always creates `order_type = STANDARD` (`:179`). There is no `SUBCONTRACT` proposal type, and a BUY would buy the processed item (`SHAFT-03P`) outright.
  - §1.1 claims C7 and C8 are covered (`FRD-MFG.md:62,65`).
- What a user experiences: a demand for `SHAFT-03P` raises `NO_BOM`, or a purchase of the finished part, never a subcontract order with its input demand.
- Fix: plan items whose selectable BOM has usage `SUBCONTRACT`. A MAKE convert then creates a `SUBCONTRACT` order, and the components explode as dependent demand.

### F-MF-015 — Medium (unreachable effect): a FIRMED parent loses its child conversion after a new run
- Contract row: MRP-GRD-12, MRP-GRD-09, MRP-N-04
- Source: GPT (verified)
- Evidence:
  - Children convert with the parent only when they are pegged "in the same run" (`mfg-mrp.contract.md:103`).
  - A new run supersedes the old `OPEN` children (`:77`), while the FIRMED parent stays convertible (`:100`) and explodes new children in the new run (`:126`).
- What a user experiences: firm a parent, run MRP again, then convert the parent. No linked child order is created.
- Fix: convert the live child proposals currently pegged to the parent, across runs, and exclude superseded ones.

### F-MF-016 — Medium (time-driven rule with no actor): the scheduled MRP run has no MFG service principal for the port
- Contract row: MRP-T3-01, MRP-T3-04, MRP-T1-08
- Source: GPT (verified)
- Evidence:
  - The scheduled run calls `withdrawExternal` (`mfg-mrp.contract.md:171`).
  - FRD-STORES requires a sibling's scheduled job to call as its seeded, non-interactive service principal holding `warehouse:orders:port` (`docs/frd/FRD-STORES.md:405`).
  - p10-12 grants the port permission to the planner only (`issues/p10-12.md:43`), and neither p10-01 nor p10-12 seeds a principal.
- What a user experiences: the nightly run fails `403 PORT_AUTHORITY_REQUIRED` when the cover window expires.
- Fix: seed an MFG service principal (port permission plus `whm_mrp_runs:run`, scoped to the site) in p10-01 or p10-12.

### F-MF-017 — Medium (module boundary / no FR): p10-07 builds warehouse-india Legal Metrology with no FR and no contract
- Contract row: none
- Source: Claude
- Evidence:
  - p10-07 adds `V540193` / `V541161` (`whin_packaged_commodity_declarations`, `whin_mrp_revisions`) plus a screen and a print provider (`issues/p10-07.md:5,29-40,124`).
  - Plan row P10-07 closes FR-644…650, FR-654 and FR-655 only (`docs/IMPLEMENTATION-PLAN.md:721`).
  - No FR in any FRD and no contract row names Legal Metrology; the grep found only FR-094 and the receipt FRs nearby. Checks 14 and 15 cannot see it.
- What a user experiences: an india compliance feature ships inside an MFG receipt task, and no functional reviewer can check it.
- Fix: add an india FR and contract rows, or move the work to an india task.

### F-MF-018 — Medium (traceability): about 339 rule rows carry no Source FR
- Contract row: all nine contracts
- Source: Both
- Evidence:
  - A scripted scan found no Source column on the T1 transitions, T2, T3 and T4 tables of BOM, PRO, MSI, CST, QRW, SUB and MRP, nor on the MRP netting rules (e.g. `mfg-production-order.contract.md:76`, `mfg-mrp.contract.md:121`).
  - PRC has the column but `—` in 40 rows (`mfg-production-receipt.contract.md:74-86,167-179`).
  - Some guard and unreachable rows cite only a decision or invariant, with no FR (e.g. SUB-GRD-07, PRO-GRD-22, BND-UNR-02, MRP-GRD-13).
  - Commit `6d7d229` claims "Source column on every rule row". Check 14 passes only because it needs one row per FR.
- What a user experiences: a reviewer cannot tell which requirement authorises a rule.
- Fix: add and fill a Source FR on every behavioural row, keeping MD / L / RN references beside the FR.

### F-MF-019 — Low (drift): proposed codes are used unmarked elsewhere, and some guards are duplicated with different codes
- Contract row: PRO-GRD-01/-04/-07/-13/-17; SUB-GRD-01…-04; CST-GRD-03
- Source: Claude
- Evidence:
  - `BOM_USAGE_MISMATCH` and `SUBCONTRACTOR_REQUIRED` appear unmarked in SUB-GRD-01/-02 (`mfg-subcontracting.contract.md:82-83`), and p10-10 has no ratification item for them.
  - `BOM_NOT_EFFECTIVE` appears as final in FR-635, MD-19, WH-SC-602 and BOM-EC-06; `OWNER_NOT_HOUSE` in WH-SC-693.
  - `ORDER_HAS_OPEN_RECEIPT` uses field `orderId` in CST-GRD-03 but `isFinal` in PRC-GRD-01.
  - SUB-GRD-04 `SUBCONTRACT_OWNER_INVALID` duplicates PRO-GRD-17 `OWNER_NOT_HOUSE`, and SUB-GRD-03 `SUBCONTRACT_LOCATION_INVALID` duplicates PRO-GRD-04 on `subcontractLocationId`.
- Fix: one code per predicate. Extend the p10-05 / p10-07 ratification items to every file that uses the code, and add one to p10-10.

### F-MF-020 — Low (arithmetic): rounding after the maximum-lot split can exceed the maximum lot
- Contract row: MRP-N-11, MRP-GRD-02
- Source: GPT (verified)
- Evidence: proposals are split to ≤ `max_lot` and then rounded up to `rounding_multiple` (`mfg-mrp.contract.md:133`), and nothing validates the two together (`:93`). For example: net 13, max 10, multiple 6 gives lots of 12 and 6.
- Fix: build lots that meet both limits, or refuse a max that is not a multiple of the rounding multiple.

### F-MF-021 — Low (contradiction): PRC-OPEN-05 says a base change is needed; FRD §R29 says none is owed
- Contract row: PRC-OPEN-05, FR-649
- Source: Claude (GPT noted the same open trace semantics)
- Evidence:
  - PRC-OPEN-05 says "base change needed — `p0` owner" (`mfg-production-receipt.contract.md:268`), against "No warehouse-base change is owed" (`FRD-MFG.md:699`).
  - The base table puts no CHECK on `transformation_type` (`WB/resources/db/migration/V500035…sql:24,64`) and needs positive quantities only (`:103,127`). So a `PRODUCTION_REVERSAL` row needs no schema change; only the trace semantics in `WhbGenealogyQueryService` would.
- Fix: record the reversal as additive (over-inclusion is safe for a recall) and close the open row, or log the trace change as a seam owed by base.

### F-MF-022 — Low (FR-268 residue): two files still treat multi-level BOM as refused
- Contract row: none
- Source: Claude
- Evidence:
  - `docs/IMPLEMENTATION-PLAN.md:641` still lists P6-12 as a live refusal row with no VOID marker.
  - `docs/SCENARIO-CATALOGUE.md:1051` still says multi-level BOM is "deliberately not built".
- Fix: mark the P6-12 row VOID and point the catalogue row at FR-622…631.

### F-MF-023 — Low (inventory / cross-references): several counts and references are stale
- Source: Claude
- Evidence:
  - The epic says "24 blocks in band + **one** `warehouse-india` block" (`issues/12-EPIC-p10.md:5`), but lists `V540190`, `V540191`, `V540192`, `V540193`, `V541160`, `V541161` (`:96,100,105`) and `V560120` (`:104`).
  - The FRD §3 migration map has no `V560120` and no p10-14 or `V540193` rows (`FRD-MFG.md:115-130`).
  - MSI-T2-01 allows Request extra only from `RELEASED`/`IN_PROGRESS` (`mfg-material-staging-issue.contract.md:116`), while MSI-T1-13 and MSI-GRD-01 also admit `COMPLETED` (`:81,88`).
  - BOM-T1-13 says it is called by `MRP-T1-03`, which is Create demand plan; it should be `MRP-T1-13` (`mfg-bom.contract.md:78`).
- Fix: correct the counts, the map and the cross-references.

## Dropped after verification
- None. Every single-engine claim held when the cited lines were re-opened.
- Severities the engines disagreed on, settled by reading the evidence:
  - F-MF-005: GPT Medium → **High**, because neither module owns it.
  - F-MF-018: GPT Low → **Medium**, because the commit claims it is done and the caller asked for this check.
  - GPT's High on F-MF-006 (close guard) and F-MF-015 (child conversion) → **Medium**, because the effect is lost protection or a lost convenience, not wrong stock.

## Remediation backlog
| Finding | Files to touch | Migration | Shared registries | Parity apply-to | Contract |
|---|---|---|---|---|---|
| F-MF-001 | `issues/p10-01.md`, `issues/p10-02.md`, `docs/frd/FRD-MFG.md` §3.2, MD-35 | amend the planned `V561000` source-system seed | `whb_source_systems` (`is_claimable`, `post_permission`) | trade and 3PL guards of the same shape | MD-35, SUB-UNR-02, MPR-GRD-35 |
| F-MF-002 | MSI, PRC and SUB contracts; `issues/p10-06.md`, `p10-07.md`, `p10-10.md`; FRD MD-31/MD-36 | none | none | trade shipments using `consumedReservationIds` | MSI-T4-06…-08, PRC-T4-01, SUB-T4-01 |
| F-MF-003 | `mfg-mrp.contract.md`, `issues/p10-12.md`, FRD FR-664 | none | none | none (MFG only) | MRP-N-04 |
| F-MF-004 | `mfg-bonded-issue`, MSI, SUB and PRC contracts; `issues/p10-14.md`; FRD FR-673, MD-43 | `V560120` (planned) unchanged | none | `warehouse-india` exit guard | BND-T4-03, BND-GRD-04 (+ a dispatch row) |
| F-MF-005 | FRD-MFG FR-658; FRD-TRADE §11 R8/R9; `issues/p9-07.md`, `issues/p10-10.md`; SUB §6, SUB-OPEN-06 | none, or next free in V-trade range if trade adopts it | none | warehouse-trade | FR-658; new trade FR or a refusal note |
| F-MF-006 | CST, PRO and MSI contracts; `issues/p10-05.md:100`, `p10-09.md` | none | none | none | CST-GRD-02 (owner); PRO-GRD-15 cites it |
| F-MF-007 | `issues/p10-14.md` seed table; `mfg-bonded-issue.contract.md`; FRD FR-672/FR-675 | amend planned `V540191` seed | india code list `WHIN_BONDED_OPERATION_KIND` | none | BND-T4-06 + new WH-SC |
| F-MF-008 | `issues/p10-14.md` data model; `mfg-bonded-issue.contract.md` | amend planned `V540191` | none | india compliance task closure | BND-T4-02, BND-T4-06, BND-UNR-03 |
| F-MF-009 | FRD WH-SC-686; `mfg-bonded-issue.contract.md` BND-T4-07; `issues/p10-14.md` | amend planned `V540192` CHECK definition | none | SEZ movement lines | BND-T4-07 |
| F-MF-010 | `mfg-production-receipt.contract.md`; `issues/p10-14.md:7`; `issues/p10-07.md` | none | none | none | new PRC row citing FR-673 |
| F-MF-011 | MSI contract; `store-issue-return.contract.md` SIR-GRD-01a; `issues/p10-06.md` | none | none | STORES resolver | MSI-GRD-01 |
| F-MF-012 | MSI contract; `issues/p10-06.md` | none | none | none | MSI-GRD-06 |
| F-MF-013 | SUB contract; `issues/p10-10.md` | none | none | none | SUB-GRD-15 |
| F-MF-014 | MRP contract; FRD FR-664/FR-666; `issues/p10-12.md` | none | none | none | MRP-N-02, MRP-N-14, MRP-T4-03 |
| F-MF-015 | MRP contract; `issues/p10-12.md` | none | none | none | MRP-GRD-12 |
| F-MF-016 | `issues/p10-01.md`, `p10-12.md`; MRP contract | amend planned `V561000` / `V561100` seed | principal + `warehouse:orders:port` grant | trade's scheduled jobs (`CN-7`) | MRP-T3-01, MRP-T3-04 |
| F-MF-017 | an india FR (or FRD-MFG); a new contract; `issues/p10-07.md`; plan §2 | `V540193` / `V541161` (planned) | `IndiaSafeTranslation` / scope registration | `warehouse-india` | new contract rows |
| F-MF-018 | all nine `mfg-*` contracts | none | none | other area contracts with the same gap | Source column on T1–T4 and N |
| F-MF-019 | PRO, PRC, SUB, CST contracts; FRD; `issues/p10-05.md`, `p10-07.md`, `p10-10.md` | none | none | none | the listed GRD rows |
| F-MF-020 | MRP contract; `issues/p10-11.md` | none | none | none | MRP-GRD-02, MRP-N-11 |
| F-MF-021 | PRC contract §9; FRD §R29 note | none | none | none | PRC-OPEN-05 |
| F-MF-022 | `docs/IMPLEMENTATION-PLAN.md:641`; `docs/SCENARIO-CATALOGUE.md:1051` | none | none | none | none |
| F-MF-023 | `issues/12-EPIC-p10.md:5`; FRD §3 map; MSI-T2-01; BOM-T1-13 | none | none | none | MSI-T2-01, BOM-T1-13 |

## Parity (C10)
- Mobile: none. FR-669 and R-13 rule it out (no warehouse mobile, user rule 2026-09-11). This is stated and is not a finding.
- Siblings sharing this pattern:
  - `warehouse` (STORES requisition / issue / return, replenishment, gate pass);
  - `warehouse-india` (job work, bonded, Legal Metrology);
  - `warehouse-trade` (service PO ownership, F-MF-005);
  - `warehouse-3pl` (claimable source systems, F-MF-001).
- Dealer, automotive, accessories, services, insurance, insurance-360 and assets are not affected.

## In code, not in contract
- The writer exempts `consumedReservationIds` from the availability check, and the caller must close each hold (`WB/java/…/ledger/writer/WhbMovementPostCommand.java:23-25`). Add this to MSI, PRC and SUB T4 (F-MF-002).
- `whb_source_systems.is_claimable` / `post_permission` is a separate port gate (`WhbPortReferenceResolver.java`). Add it to MD-35 (F-MF-001).
- `WhinBondedVirtualExitPostGuard.ExitLine` carries only `virtualLocation`, not the location base type (`WI/java/…/whinbondedloss/WhinBondedVirtualExitPostGuard.java`, `check`). p10-14 must resolve the base type to match MD-42 rules. This is implicit in p10-14 and should be stated.

## Contract quality
- All nine contracts are v0 and unratified. The statutory values (MOOWR, s.65, ITC-04 windows) are RE-VERIFY and were not checked against outside sources.
- Still open: PRO-OPEN-02, PRC-OPEN-05/06, CST-OPEN-05/06/07, QRW-OPEN-04/05/06/09, SUB-OPEN-06/07/08/09, MRP-OPEN-03/04/05/06/07/08/10, BND-OPEN-01/02.
- Runtime checks C3, C5 and C8 cannot run yet: no MFG code exists. Their absence is not reported as a defect.

## Referred to standards reviewer
- None.