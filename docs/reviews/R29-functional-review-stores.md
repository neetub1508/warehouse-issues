# R29 — functional review (Claude + GPT dual engine), area STORES

**Date** 2026-10-22 · **Reviewer** functional-reviewer, pre-build audit mode · **Dispositions** recorded in the area FRD §"R29 dispositions"

## Summary

I did not write `/private/tmp/claude-501/-Users-bbhushan-work-git-workspace-classic/53f0e57a-69c7-42b1-a5aa-daa8c13be89a/scratchpad/FR-REVIEW-STORES.md`. My agent definition does not allow me to write report files, so the full report is below and can be posted or saved as it is.

**36 findings: 4 BLOCKER, 22 MAJOR, 10 MINOR.** By source: 7 found by both engines, 21 by Claude only, 8 by GPT only, none dropped.

**Top 5**
1. **F1 BLOCKER** — None of the new P8 resources gets the `:view:all`/`:view:branch` permission pair, so a non-admin user can see nothing. The requisition, issue and return contracts also give `view:all` a different, department-based meaning.
2. **F2 BLOCKER** — On a fresh or rebuilt database, `V510401` runs before `V511303`. It tries to widen a unique index on columns that do not exist yet, so the migration fails.
3. **F3 BLOCKER** — A demand line that has only forecast schedule lines gets ordered quantity 0. That breaks the existing CHECK `ordered_quantity > 0` (`V510040:319`).
4. **F4 BLOCKER** — Partial issue cannot consume its reservation. Passing `consumedReservationIds` only stops those holds counting against availability; it does not close them, and the reservation is one row covering the whole approved quantity.
5. **F5 MAJOR** — Redefining `billedQuantity()` silently changes two existing quantity helpers. The design also ignores the existing free (scheme) quantity and dock-rejected quantity.

Engines: Claude + GPT (gpt-6.1-sol, medium) — 7 both · 21 Claude only · 8 GPT only · 0 dropped

---

# Functional conformance — STORES (P8)
Contract: the 7 P8 contracts, all v0 2026-10-22 | Mode: audit, pre-build (design against the live code it extends)
Files reviewed: 27 design inputs + about 30 live-code files read for specific questions | File set: given design set + compatibility dependencies
Engines: Claude + GPT (gpt-6.1-sol, medium) — 7 both · 21 Claude only · 8 GPT only · 0 dropped

`D/` = `/Users/bbhushan/work/git/workspace/warehouse-issues/`, `C/` = `/Users/bbhushan/work/git/workspace/classic/`.

## Verdict
**36 findings (4 BLOCKER · 22 MAJOR · 10 MINOR).** Do not file P8-01, -02, -04, -08, -09, -10 or -16 until F1–F14 are fixed in the contracts.

## Status reachability
| Entity | States | Inbound/outbound | Verdict |
|---|---|---|---|
| Gate entry | OPEN, TURNED_BACK, CLOSED, CANCELLED | every state reachable; terminals explicit | OK (permission gap F15) |
| Gate pass | DRAFT, APPROVED, OUT, PARTIALLY_RETURNED, RETURNED, CLOSED_SHORT, CANCELLED | OK; NRGP terminal at OUT | OK |
| GRN line excess | none / undecided / decided | a receipt over the PO but not over the bill can never be decided | **dead end F8** |
| MRN + stock `MRN_PENDING` | DRAFT, SUBMITTED, AUTHORISED, CANCELLED | the only way out of `MRN_PENDING` is Authorise, which needs the site setting on | **dead end F10** |
| Requisition | 8 header states | all reachable | approval bypass F16 |
| Store issue / return | DRAFT, POSTED, CANCELLED / DRAFT, SUBMITTED, POSTED, REJECTED, CANCELLED | OK | item-identity guard missing F17 |
| PO schedule line | OPEN, PARTIALLY_RECEIVED, RECEIVED, CLOSED, CANCELLED | a core-only install cannot release new lines after approval | **F6** |
| Demand schedule line | OPEN, PARTIALLY_SHIPPED, SHIPPED, CANCELLED | a forecast-only line cannot be saved | **F3** |
| External suggestion | PROPOSED, ACCEPTED, CONVERTED, REJECTED | an EXTERNAL run breaks the existing CHECKs | **F12** |

## Findings

### F1 — BLOCKER · Unguarded access: new resources lack the warehouse scope pair; `view:all` reused with another meaning
- Contract rows: GTE §0, MRA §0, MRQ §0, SIR §0, IIS §0 · Source: Claude
- Evidence: `D/docs/contracts/material-requisition.contract.md:24` defines `view:all` = "every department"; `store-issue-return.contract.md:23`; `gate-entry.contract.md:27` and `mrn-authorisation.contract.md:25` list only `view`. In live code `:view:all`/`:view:branch` is the warehouse scope pair (`C/warehouse/backend/src/main/resources/db/migration/V511000__…sql:68-71`). With no pair, `WhbWarehouseScopeService.java:133-141` returns `NONE`. No P8 document mentions `view:branch`.
- What a user experiences: gate security, requesters and stores clerks see empty grids. Granting `view:all` to give department-wide visibility also opens every site.
- Fix required: seed the `:view:all`/`:view:branch` pair on every new resource. Give department scope its own verb, for example `view_all_departments`.

### F2 — BLOCKER · Migration order: `V510401` widens an index that `V511303` creates later
- Source: Claude
- Evidence: `D/issues/p8-02.md:16` says "widen its partial uk to (source_module, idempotency_key)". The columns and `uk_wh_demand_orders_idempotency_key` are created in `C/warehouse/.../V511303__…sql:41-52`. On a fresh database (the P7 rebuild and the exit criterion) Flyway runs versions in ascending order, so `V510401` meets missing columns and fails. The whole P8 app band `V510400`–`V510413` also sorts below the existing `V5105xx`–`V511308`, so a rebuilt database applies them in a different order than an upgraded one.
- Fix required: renumber the P8 schema migrations above the current high-water mark (next free in V510000–V519999 above `V511308`), or prove each one is safe in both orders.

### F3 — BLOCKER · Unreachable: a forecast-only demand line cannot be saved
- Rows: POS-T1-11, FR-505 · Source: Both
- Evidence: `D/issues/p8-02.md:25` sets ordered = Σ firm. `C/warehouse/.../V510040__…sql:319` has `CHECK (ordered_quantity > 0)` and p8-02 does not relax it. Cancelling the last firm line causes the same failure.
- Fix required: relax the CHECK, or define how a line with zero firm quantity is represented, including the partition CHECK at `V510040:328-329`.

### F4 — BLOCKER · Cross-entity: reservation is never consumed, or is consumed whole
- Rows: MRQ-T4-01/-02, SIR-T4-01 · Source: Both
- Evidence: `material-requisition.contract.md:129-130` and `store-issue-return.contract.md:120` say the issue consumes reservations "by `consumedReservationIds`". In live code that parameter only exempts the caller's holds from the availability check (`C/warehouse-base/.../WhbStockPositionWriter.java:201-202`, `WhbMovementPostCommand.java:23`). Consuming a hold is a separate call that closes the whole reservation (`WhbReservationStore.java:228-234`; despatch uses `WhbPickReservationService.java:223`). A reservation also requires a location and status (`WhbReservationService.java:138-139`), but the contract specifies one per line. Nothing says whether core or MFG consumes owner-held MFG reservations.
- What a user experiences: approve 8, issue 5 — either 8 stay reserved for ever, or the remaining 3 lose their protection.
- Fix required: reservations per grain, an explicit consume-and-split call inside the issue transaction, and a named owner for consuming MFG-held reservations.

### F5 — MAJOR · Live-code compatibility: GRN quantity semantics clash
- Rows: FR-517, GBM-T4-01, GBM-GRD-07 · Source: Claude
- Evidence: `C/warehouse/.../entity/WhGoodsReceiptLine.java:207-228`: `billedQuantity()` feeds `overReceivedQuantity()` and `shortQuantity()`, which compare against *expected* quantity. FR-517 (`D/docs/frd/FRD-STORES.md:170`) changes what it returns, so both helpers flip to billed − expected.
  - The posting service posts received + free − rejected (`WhGoodsReceiptPostingService.java:305-311`). The existing free (scheme) quantity (`:42-44`, `:108-111`) is missing from GBM-T4-01's "received − excess_refused" (`grn-bill-match.contract.md:113`) and from the excess maths.
  - The existing `rejected_quantity` means dock rejection, landed in REJECTED, but GBM calls it the QC reject.
- Fix required: add a new column and accessor and leave the helpers alone. Define the posting quantity as received + free − rejected − excess refused. State how free quantity counts toward excess over the bill (this overlaps OD-28).

### F6 — MAJOR · Unreachable: an OPEN PO cannot take new firm releases when trade is off
- Rows: POS-T1-02, POS-T2-02 · Source: Claude
- Evidence: `po-schedule-port.contract.md:64` and `:107` allow manual schedule edits only while the header is `DRAFT`. FRD §4 (`FRD-STORES.md:109-111`) says no row needs trade. An OPEN PO only exists to take call-offs over time.
- Fix required: allow manual release and firming on an approved OPEN or BLANKET PO when no `PurchaseOrderChangeGuard` refuses.

### F7 — MAJOR · Guard missing: PO line roll-up is undefined for a null ordered quantity
- Source: Claude
- Evidence: `WhPurchaseOrderLineStatusService.java:158-159` multiplies `getOrderedQuantity()`. The over-receipt check divides by it (`WhGoodsReceiptPostingService.java:455-458`). 21 files read it. The POS contract defines no RECEIVED rule for an OPEN line (the epic names this trap; the contract has no row for it).
- Fix required: a contract row saying OPEN lines roll up against Σ firm (`scheduled_quantity`), applied to every reader.

### F8 — MAJOR · Guard wrong: excess headroom maths and an over-PO dead end
- Rows: GBM-GRD-06, GBM-T1-04…-06 · Source: Both
- Evidence: `grn-bill-match.contract.md:78` compares excess (4) with the total headroom (102), so `WH-SC-439` (`FRD-STORES.md:275`, 2 inside tolerance + 2 needing approval) is auto-accepted. The partial inside/outside split is not defined.
  - Excess is computed only against the bill (`:50`). PO 100, bill 110, received 110 gives excess 0, so the line counts as "decided", yet GBM-GRD-08 (`:80`) still refuses over tolerance and no approve action exists. The GRN can never post.
- Fix required: define excess over the bill and excess over the PO or schedule separately, with the auto-accepted part and the decision part. Freeze the worked examples.

### F9 — MAJOR · Cross-entity: weighment variance cannot be evaluated
- Rows: GTE-T4-03, FR-510 · Source: Both
- Evidence: there is no bill-weight field anywhere (`D/issues/p8-03.md:19`, `gate-entry.contract.md:172`). The variance is computed "when a GRN is posted" (`:153`), but a weighing record holds gross, tare and net together (`V510213__…sql:127-133`). The tare is weighed at exit, after the session completes, and a session completes only with no draft GRN (`V510013__…sql:51`). So the net weight does not exist yet when the GRN posts.
- Fix required: add bill weight and its unit. Evaluate the variance when the weighing record is saved or at gate-out.

### F10 — MAJOR · Dead end: switching MRN off strands `MRN_PENDING` stock
- Rows: MRA-GRD-01, MRA-T4-04 · Source: Both
- Evidence: `mrn-authorisation.contract.md:51`, `:67`, `:111`.
- Fix required: refuse the setting change while pending stock or a live MRN exists, or keep the MRN flow available for that stock (grandfather it).

### F11 — MAJOR · Cross-entity: destructive-test issue uses an unregistered document type and has no cost-object storage
- Rows: IIS-T4-02, FR-524 · Source: Claude
- Evidence: `incoming-inspection-sampling.contract.md:117` sets `source_document_type = QUALITY_INSPECTION`. The live QC document type is `QCINSP` (`C/warehouse/.../WhQualityInspectionRepository.java:36`), and the source type is a whb_document_types FK. The ALTER list (`:23`) has no `cost_object_*` columns. The consumption register (`store-issue-return.contract.md:152`) reads issue lines, so QC destruction never appears in it.
- Fix required: use `QCINSP`, add cost-object columns to the inspection line, and say which source the register reads.

### F12 — MAJOR · Live-code compatibility: EXTERNAL replenishment runs break existing CHECKs
- Source: Claude
- Evidence: `V510070__…sql:120` CHECK pairs run_type with run_by as (MANUAL with a user, SCHEDULED with none). An EXTERNAL run with a user fails it. `:147` allows only one RUNNING run per site. `po-schedule-port.contract.md:196` only widens `:117`.
- Fix required: replace the pairing CHECK, and create EXTERNAL runs directly as completed.

### F13 — MAJOR · Guard unenforceable: RMA quantity ≤ shipped per demand line
- Rows: POS-GRD-21 · Source: Claude
- Evidence: `po-schedule-port.contract.md:174` and `D/issues/p8-15.md:27` need the demand line. `wh_rma_lines` has no demand-line column (`V510050__…sql:224-240`).
- Fix required: add `original_demand_order_line_id` to `wh_rma_lines`.

### F14 — MAJOR · Seam incomplete: port methods named but not contracted
- Source: Claude
- Evidence:
  - `getRmaPosition`: in `FRD-STORES.md:149` and `p8-15.md:29`, missing from contract §8a (`po-schedule-port.contract.md:161-178`).
  - `markConverted`: used at `:187` but missing from FR-528's method list (`FRD:191`).
  - `PurchaseRequisitionHandoff.status`: in `p8-09.md:30`, no contract row.
  - `WhMaterialRequisitionPort`: only named (`material-requisition.contract.md:173`, `p8-09.md:31`). It has no rows for idempotency, initial status, approver for an MFG-raised requisition, or a change guard, yet MFG relies on create, cancel and close (`mfg-material-staging-issue.contract.md:69,82`).
- Fix required: add T1 and guard rows for each method.

### F15 — MAJOR · Weaker permission: gate-out of an entry moves its passes to OUT
- Rows: GTE-T1-05 · Source: GPT
- Evidence: `gate-entry.contract.md:73` vs `:128` and `:132`.
- Fix required: also require `wh_gate_passes:gate_out`.

### F16 — MAJOR · Guard bypass: the second approval is optional
- Rows: MRQ-T1-03/-06 · Source: Both
- Evidence: `material-requisition.contract.md:68`, `:71`, `:87`. Recall (`:69`) does not clear the first-approval stamp.
- Fix required: make the two approval transitions mutually exclusive, and clear the stamp on recall.

### F17 — MAJOR · Guard missing: an issue line can differ from its requisition line in item or unit
- Rows: SIR-GRD-02 · Source: GPT
- Evidence: `store-issue-return.contract.md:76`; `p8-10.md:24`; `p8-09.md:22`.
- Fix required: the item must match, the line must belong to the header's requisition, and quantities are compared in base units.

### F18 — MAJOR · Guard incompatible: demand amend floor double-counts
- Rows: POS-GRD-09 · Source: GPT
- Evidence: `po-schedule-port.contract.md:89` uses "allocated+picked+shipped", but the existing quantities are cumulative (`V510040__…sql:324-329`).
- Fix required: the floor is allocated (cumulative), plus cancelled and backordered as the partition CHECK requires.

### F19 — MAJOR · Cross-entity: the short claim uses expected quantity, not billed
- Rows: GBM-T4-02 · Source: GPT
- Evidence: `grn-bill-match.contract.md:114`; `WhSupplierClaimValidationService.java:216-229`; `WhSupplierClaimQueryService.java:335`.
- Fix required: base SHORT_SHIPMENT prefill and its ceiling on billed − received.

### F20 — MAJOR · Guard targets the wrong action: Accept already converts to a PO
- Rows: POS-T1-32/-33 · Source: GPT
- Evidence: `WhReplenishmentSuggestionService.java:186`, `:197`, `:287`; controller accept endpoints. The contract names `:edit` (`po-schedule-port.contract.md:186`).
- Fix required: put the `SuggestionConversionOwner` check inside `acceptLocked`, and use the `:accept` authority.

### F21 — MAJOR · Idempotency has no per-operation record
- Rows: POS-GRD-07 · Source: GPT
- Evidence: `p8-01.md:25` vs `:41`; `p8-15.md:19` vs `:28`. A replayed release, amend or cancel cannot return its original result.
- Fix required: an operation registry recording key, fingerprint and result.

### F22 — MAJOR · Guard gap: Ac/Re pairs with a gap give no verdict
- Rows: IIS-GRD-03, IIS-T1-08 · Source: GPT
- Evidence: `incoming-inspection-sampling.contract.md:64`, `:74`. Ac 1 / Re 4 with 2 defectives matches neither verdict.
- Fix required: require Re = Ac + 1, or define what happens in between.

### F23 — MAJOR · Gate-pass source has no line identity
- Rows: GTE-GRD-12 · Source: GPT
- Evidence: `gate-entry.contract.md:102`; `p8-03.md:21` stores only document type, id and ref.
- Fix required: add `source_line_id`, resolved by `GatePassSourceResolver`.

### F24 — MAJOR · Cross-entity: one gate-entry bill copied to every GRN of the session trips the duplicate-bill guard
- Rows: GTE-T4-01, GBM-GRD-01 · Source: Claude
- Evidence: `gate-entry.contract.md:151`; `grn-bill-match.contract.md:73`. A session can have several GRNs (`V510014__…sql:128`, `session_id` is not unique), and FR-508 allows several POs on one entry.
- Fix required: the duplicate check ignores GRNs that share one gate entry, or the bill is copied to one GRN only.

### F25 — MAJOR · Ownership ambiguity: who posts PRODUCTION_RECEIPT dispositions
- Source: Claude
- Evidence: `incoming-inspection-sampling.contract.md:120` says MFG's `onDisposition` owns the effects. `D/docs/contracts/mfg-qc-rework.contract.md:77` says core posts the STATUS_CHANGE. This risks a double post or no post.
- Fix required: core posts; the resolver only reacts.

### F26 — MAJOR · Maker/checker codes inconsistent with core
- Source: Both
- Evidence: the design uses `403 APPROVER_IS_ACTOR` (`FRD-STORES.md:104-105`). Core uses a code per document, for example `SUPPLIER_RETURN_SELF_APPROVAL` 403 (`WhSupplierReturnValidationService.java:150`), and PO self-approval returns 409 `PO_APPROVER_IS_SUBMITTER` (`WhPurchaseOrderValidationService.java:297-299`). Several "≠ maker" guards name no code at all: gate pass extend and close-short (`gate-entry.contract.md:82-83`), approve excess (`grn-bill-match.contract.md:63`), store-return post (`store-issue-return.contract.md:66`), MRN reject.
- Fix required: one convention, and a code on every guard.

### MINOR
- **F27** (Claude) MRN routing (`mrn-authorisation.contract.md:108`) applies to blind and non-PO GRNs (`V510014:201-203`), while `:82` says MRN is for purchases only. State the scope.
- **F28** (Claude) A barrier ENTRY event stamps `entered_at` from the event's `occurredAt` (`gate-entry.contract.md:75`), against the server-stamp rule (`FRD:155`, IRR-23). The FRD calls the field `arrived_at`; the contract and FR-534 call it `entered_at`.
- **F29** (Claude) A GRN reversal leaves the `EXCESS_OVER_BILL` case and the weighment `QUANTITY` case open (`grn-bill-match.contract.md:115-117`).
- **F30** (Claude) A sampling scheme cannot be deactivated. The version is stored as `sampling_scheme_id` in the epic but `sampling_scheme_version_id` in IIS (`:23`, `:59`). How plans are re-pointed to a new version is unspecified.
- **F31** (Claude) FR-539's gate register is not a WS-277 tab (`FRD:235`). FR-534's frozen KPI rows are not planned in `p8-13.md:30`. OD-27 cites FR-534 where it means FR-533 (`FRD:342`).
- **F32** (Claude) SOFT vs HARD reservation is undefined, and a shortfall is never re-reserved when hand-off stock arrives (`material-requisition.contract.md:129`).
- **F33** (Claude) If close-short is applied to the last open line, the header could end CLOSED or ISSUED; the contract does not say which (`:73-74`). "Same company" cannot be checked for departments, which have no company column (`C/platform/.../V13__…sql`).
- **F34** (Claude) FR-533 lists three core resolvers; SIR-GRD-01 adds MACHINE and PROJECT (`FRD:201` vs `store-issue-return.contract.md:74`).
- **F35** (Claude) Linking outward documents to a gate entry is in `p8-03.md:19` but has no T1 row or guard (`gate-entry.contract.md:69`).
- **F36** (Claude) The gate-security persona permission is `:close` (`FRD:94`); the contract uses `:gate_out`.

## Dropped after verification
- None. Every GPT-only finding was re-checked at its cited file:line and held.

## R27 client steps — coverage
| Step | Covered by | Gap |
|---|---|---|
| 1–2 PR, quotation | P9 (TRADE) through the hand-off and suggestion ports | F14 |
| 3a/b/c fixed, open, blanket | FR-500–504 | F6, F7, F21 |
| 4 Gate entry (party, PO, bill no/date) | GTE | F9, F24, F28 |
| 5 Inward: short → claim, excess | GBM | F5, F8, F19 |
| 6 Lot-size sampling bands | IIS | F22, F30 |
| 7 QC reject → return | IIS-T1-10 | covered |
| 8 Authorised MRN | MRA | F10, F27 |
| 10–12 Requisition, issue, return | MRQ / SIR | F4, F16, F17 |

## Seams consumed by P9/P10
- `WhPurchaseOrderPort`: F6, F21.
- `PurchaseOrderChangeGuard`: present, but its interface is unspecified.
- `WhDemandOrderPort`: F3, F18.
- `WhRmaPort`: F13, F14.
- `WhReplenishmentSuggestionPort`: F12, F14, F20.
- `CostObjectResolver`: specified, but see F4.
- `QualityInspectionSourceResolver`: F25.
- `GatePassSourceResolver`: F23.
- `PurchaseRequisitionHandoff`: F14.

## Remediation backlog
| Finding | Files to touch | Migration | Shared registries | Contract |
|---|---|---|---|---|
| F1 | p8-03…p8-11 seed tasks | V5114xx seeds | permission_dependencies | every §0 permissions row |
| F2 | p8-02 (+ all P8 schema migrations) | next free above V511308 | none | epic migration table |
| F3, F18 | p8-02 | planned V510401 | none | POS-T1-11, POS-GRD-09 |
| F4, F32 | p8-09, p8-10 | V510408/9 | none | MRQ-T4-01/02, SIR-T4-01 |
| F5, F8, F19, F24 | p8-04 | V510403 | none | GBM-T1-02…-06, GBM-T4-01/02, GBM-GRD-01/06 |
| F6, F7 | p8-01 | V510400 | `COMMON_FILTER_CONFIGS.WAREHOUSE_PURCHASE_ORDER` | POS-T1-02, T2-02, new roll-up row |
| F9 | p8-03 | V510402 | `filterUtils.ts` `WAREHOUSE_GATE_ENTRY` | GTE-T4-03, T5 |
| F10, F27 | p8-08 | none | settings registry (p8-14) | MRA-GRD-01, T4-01 |
| F11 | p8-05 | V510404 | none | IIS-T4-02 |
| F12, F20 | p8-16 | V510413 | none | §8b |
| F13, F14 | p8-15, p8-09, p8-16 | V510412 | none | §8a, MRQ new port rows |
| F15–F17, F22, F23, F25, F26 | p8-03, p8-05, p8-06, p8-09, p8-10 | none | none | rows cited |

## Parity (C10)
- Mobile: none. FRD §4 and §12 row 12 (D-16 item 7) say there is no mobile, with a reason.
- Modules that consume these seams: `warehouse-trade`, `warehouse-manufacturing`, and `warehouse-india` (the DELIVERY_CHALLAN gate-pass resolver). Accessories and assets have separate stock stacks (R27 RM-033) and are not on the apply-to list.

## Contract quality
- I could not verify whether any route other than authorisation takes GRN-sourced stock out of `MRN_PENDING` into AVAILABLE. Recall quarantine release is the one to check (`WhRecallService`). The planner's single path is `StockStatusChangePlanner`.
- The current menu-section counts for P8-14's caps were not checked against the live database.

## Referred to standards reviewer
- None.