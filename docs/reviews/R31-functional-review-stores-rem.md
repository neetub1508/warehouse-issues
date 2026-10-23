**Summary (≤120 words).** I did not write `docs/reviews/R31-functional-review-stores-rem.md`: my role does not allow report files, so the full report follows. **18 findings: 0 BLOCKER, 9 MAJOR, 9 MINOR.**

Top 5:
1. **F-SR-001**: once a gate pass is gated out from its own screen, the linked outward gate entry can never be closed.
2. **F-SR-004**: users and job accounts that call the ports get no site scope, so core site checks refuse them.
3. **F-SR-006**: `V511400` links the port authority to requisition permissions that `V511408` only creates later. On a fresh install the links are lost.
4. **F-SR-007**: a supplementary bill dated after the receipt is refused, which blocks the excess-over-bill ("credit note") handover.
5. **F-SR-009**: the absence checks in `rem-removal.contract.md` are written with `\|`. Run as written, they match nothing and always pass.

---

# Functional conformance — STORES (P8) + REM (P7), R31 second review
Contract: the 7 STORES contracts + `rem-removal.contract.md` (all v0, 2026-10-22/23) | Mode: audit, pre-build
Files reviewed: 41 design documents (FRD-STORES, FRD-REM, 8 contracts, `p8-01…16` + epic, `p7-01…13` + epic) plus about 40 targeted `classic` files at `74102d8d04` | File set: given scope, plus the code each claim cites
Engines: Claude + GPT (gpt-6.1-sol, medium) — 1 both · 9 Claude only · 8 GPT only · 0 dropped

`D/` = `/Users/bbhushan/work/git/workspace/warehouse-issues/`, `C/` = `/Users/bbhushan/work/git/workspace/classic/`.

## Verdict
**18 findings (0 BLOCKER · 9 MAJOR · 9 MINOR).** No build, database run or HTTP call was made.

**What holds:**
- **Client flow.** Every step of the client's flow has a requirement, a contract row and a task: gate entry (party, PO, bill no/date) → GRN with short (claim) and excess (case) → QC sampling bands → reject → manual supplier return → MRN → putaway → requisition / issue / return. The debit and credit notes stop at the stated handover points (FRD-STORES §8).
- **R29 dispositions.** The rows I checked are carried into the contracts and tasks. Their code citations are accurate, for example:
  - `WhGoodsReceiptLine.java:207-209`
  - `WhGoodsReceiptPostingService.java:133`
  - `WhSupplierClaimValidationService.java:216`
  - `WhbReservationStore.java:232`
  - `WhbPickReservationService.java:137`
  - `WhReplenishmentSuggestionService.java:186,287`
  - `WhRmaService.java:186,234`
  - `WhbWarehouseScopeService.java:133-136`
  - `QCINSP` at `WhQualityInspectionRepository.java:36`
- **R29 REM count floors (F4)** are right: `V500003:429,432` goes 18 → 17, and `V500002:461,464` goes 9 → 4 and 13 → 11.
- **Menu caps.**
  - New L1 `warehouse_stores` has 4 sections: 2, 7, 4 and 2 leaves.
  - WS-079/080 really are under *Putaway & Replenishment* today (`W/V511250:71-72`), so that section goes from 7 to 5.
  - After P7, `warehouse_shipping` has 1 section holding 4 leaves.
- **Migration numbering.** The live high-water marks are still `V511308` and `V501227`. Every P8 block sorts above them, and no `p9`/`p10` file claims a number in those blocks. Out-of-order is enforced `true` (`shared/docker/docker-compose.yml:96-99`, `.env:34`). The one real ordering defect is F-SR-006.
- **P7 vs P8–P10.** Neither engine found anything P8–P10 need among the P7 deletions.
  - I grepped `p8/p9/p10`, FRD-TRADE, FRD-MFG and the trade/mfg contracts for every removed artefact. The only hits are the retired `warehouse_trade` key, which trade explicitly avoids, and a `VOR` → `LINE_STOP` note.
  - Gate events, weighing records, `departed_at`, `is_reprint`, `statutory_category`, `LOSS_HEADS`, `WhQualityInspectionSampleSize`, `default_inspection_plan_id` and the `V511303` index all survive P7.
- **REM coverage against Appendix A and the code.**
  - All 478 Appendix A files exist.
  - 474 of them match a gate pattern. The other 4 are covered by GATE-7 or `RMV-UNR-07`, except `WhTrackingEventRequest.java` (F-SR-010).
  - Every kept file that matches a removal pattern today is named in FRD-REM or a P7 task.
  - The GATE-8 `jq` checks find all 17 sections today, so they are not vacuous.

## Status reachability (P8 lifecycles touched by findings)
| Entity / status | Inbound | Outbound | UI reachable | Verdict |
|---|---|---|---|---|
| Gate entry `OPEN → CLOSED` (outward, pass linked) | GTE-T1-01 | GTE-T1-05 | yes | dead end once the pass is `OUT` (F-SR-001) |
| Gate pass `APPROVED → OUT` via entry | GTE-T1-02a link | GTE-T1-12 | yes | link has no resolver (F-SR-002) |
| Demand schedule `PARTIALLY_SHIPPED` | despatch | none for the remainder | "Close short" promised | F-SR-003 |
| Stock `MRN_PENDING → AVAILABLE` | GRN post / QC release | MRA-T1-03 | yes | QC-released stock not found by the lookup (F-SR-005) |
| Excess-over-bill case `OPEN → RESOLVED` | GBM-T4-03 | GBM-T1-08 / -09 | yes | supplementary-bill path blocked (F-SR-007) |
| Store return `POSTED` (its movement) | SIR-T1-07 | reversal undefined | — | F-SR-008 |

## Findings

### F-SR-001 — MAJOR · Dead end: gating a pass out from its own screen blocks closing the entry
- Contract row: GTE-T1-05, GTE-T1-12, GTE-GRD-09
- Source: GPT
- Evidence:
  - `D/docs/contracts/gate-entry.contract.md:80`: the pass is gated out from WS-263 against an outward entry, and only the pass changes (`:157`).
  - `:100`: entry gate-out requires each linked pass to be `APPROVED`, then moves it to `OUT` itself (`:74`).
- What a user experiences: after security gates the pass out on WS-263, `409 GATE_OUT_DOCUMENT_NOT_DISPATCHED` stops the vehicle's entry from closing, permanently.
- Fix: GTE-GRD-09 also accepts a pass already `OUT` against this same entry. Alternatively, let only the entry gate-out move linked passes. Test both orders.

### F-SR-002 — MAJOR · Missing entry point: no resolver accepts a gate pass as an outward document
- Contract row: GTE-T1-02a, GTE-GRD-15
- Source: GPT
- Evidence:
  - `gate-entry.contract.md:71` allows linking a gate pass to an outward entry.
  - `:106` requires the link to resolve through `GatePassSourceResolver`.
  - The core resolvers listed are `SUPPLIER_RETURN`, `SHIPMENT` and `STORE_ISSUE` only (`D/docs/frd/FRD-STORES.md:462`, `D/issues/p8-03.md:36`).
- What a user experiences: linking the RGP to the vehicle's outward entry is refused `422 GATE_ENTRY_DOCUMENT_UNSUPPORTED`.
- Fix: register a core `GATE_PASS` outward-link handler (site, readiness = `APPROVED`) in registry R.3, GTE-GRD-15 and p8-03.

### F-SR-003 — MAJOR · Missing entry point: WS-276 "Close short" has no port verb
- Contract row: POS §5.3
- Source: GPT
- Evidence:
  - `D/docs/contracts/po-schedule-port.contract.md:162` and `D/issues/p8-02.md:69` require a **Close short** action that is "a demand-port verb".
  - The demand port has only firm, un-firm, cancel-one and `closeDemand` (`FRD-STORES.md:427-433`).
  - Cancel requires nothing picked (`po-schedule-port:77`), and `closeDemand` acts on the whole order (`:79`).
- What a user experiences: the remainder of a partly shipped customer schedule line cannot be closed from the screen the contract promises.
- Fix: add a `closeScheduleLineShort` row (shipped/picked floor, reservation release, `cancelled_quantity`, event), or drop the action and defer it.

### F-SR-004 — MAJOR · Guard incompatibility: port principals get no core site scope
- Contract row: POS-GRD-13, registry R.1 *Principal*
- Source: GPT
- Evidence:
  - `D/issues/p8-01.md:44` (and `po-schedule-port:28`) grant `warehouse:orders:port` dependencies to verbs, but not to `:view:all`/`:view:branch`.
  - Trade's service principal gets only `warehouse:orders:port` (`D/issues/p9-01.md:94-97`).
  - Core create checks site scope first: `C/warehouse/backend/src/main/java/ai/warehouse/service/WhPurchaseOrderService.java:244-245` (`queryService.requireReadableSite`). Without the pair the scope resolves `NONE` (`WhbWarehouseScopeService.java:133-141`).
- What a user experiences: trade's auto-close job, and any non-admin trade approver, is refused by core even though they hold every documented port authority.
- Fix: in registry R.1 / POS §0, state the core site scope a port caller needs. Seed `:view:all` (service principal) or `:view:branch` (bundles) for `wh_purchase_orders`, `wh_demand_orders`, `wh_rmas`, `wh_replenishment_suggestions` and `wh_material_requisitions` in the siblings' seeds.

### F-SR-005 — MAJOR · Cross-entity: the MRN lineage lookup names the wrong QC document type
- Contract row: MRA-GRD-05, MRA-T4-02
- Source: GPT
- Evidence:
  - `D/issues/p8-08.md:31` traces pending stock through `source_document_type ∈ {GRN, QUALITY_INSPECTION}`.
  - QC postings actually use `QCINSP` (`C/warehouse/backend/src/main/java/ai/warehouse/repository/WhQualityInspectionRepository.java:36`).
  - GRN postings use `GRN` (`WhGoodsReceiptPostingService.java:121`).
- What a user experiences: stock that QC released into `MRN_PENDING` is not found at authorise. The line authorises 0, and the MRN fails `409 MRN_PENDING_QUANTITY_CHANGED`.
- Fix: replace `QUALITY_INSPECTION` with `QCINSP`, state the inspection-line → GRN-line join, and test QC release → MRN authorise.

### F-SR-006 — MAJOR · Migration order: port dependencies are seeded before their target permissions
- Contract row: POS §0 principal
- Source: GPT
- Evidence:
  - `D/issues/p8-01.md:44` has `V511400` insert `warehouse:orders:port → wh_material_requisitions:{view,create,cancel,close}`.
  - Those permissions are first created by `V511408` (p8-09). Epic order: `D/issues/10-EPIC-p8.md:82`.
  - POS §0 (`po-schedule-port:28`) lists only `{view,create}`, while registry R.2 needs `:cancel` and `:close` (`FRD-STORES.md:446-447`).
- What a user experiences: on a fresh install, a lookup-join insert silently skips the rows (a strict insert would fail instead). MFG's planner can then create no requisition through the port.
- Fix: seed the requisition dependency rows in `V511408`, and align the POS §0 list to `{view,create,cancel,close}`.

### F-SR-007 — MAJOR · Guard wrong: a supplementary bill dated after the receipt is refused
- Contract row: GBM-T1-08, GBM-GRD-02
- Source: GPT
- Evidence:
  - `D/docs/contracts/grn-bill-match.contract.md:66` adds supplementary bills after posting under `GBM-GRD-01…-03`.
  - `:74` requires bill date ≤ GRN receipt date.
  - `D/issues/p8-04.md:61` repeats this.
- What a user experiences: excess received on 1 Nov, supplier invoices it on 5 Nov, and the bill is refused `422 SUPPLIER_BILL_DATE_AFTER_RECEIPT`. The `EXCESS_OVER_BILL` case can then only close as free-of-charge.
- Fix: keep the receipt-date ceiling for the primary bill. Supplementary bills get bill date ≥ the primary bill's date and ≤ today.

### F-SR-008 — MAJOR · Cross-entity: `ISSUE_RETURN` declares `ISSUE` as its reversal type
- Contract row: SIR-T4-03
- Source: Claude
- Evidence:
  - `D/docs/contracts/store-issue-return.contract.md:122` says `reversal_type_code = ISSUE`.
  - `D/issues/p8-11.md:19` says "per the `V500003` convention", which contradicts it.
  - The convention: a forward type points to a `*_REVERSAL` row whose own reversal code is NULL (`C/warehouse-base/.../V500003__Create_whb_movement_types.sql:71-73`). L-3 is enforced only in `WhbMovementTypeValidationService` (`:145-150`), which a seed bypasses.
  - `ISSUE` is itself reversible, to `ISSUE_REVERSAL` (`FRD-STORES.md:347`).
- What a user experiences: reversing a posted store return writes a bare `ISSUE`, which is itself reversible. This breaks L-3 and leaves an issue movement with no store issue behind it.
- Fix: seed `ISSUE_RETURN_REVERSAL` (reversal code NULL) in `V501235` and point `ISSUE_RETURN` at it. Alternatively, state that a posted store return is never reversed and seed NULL. Make the contract and p8-11 agree.

### F-SR-009 — MAJOR · REM absence checks pass vacuously when run as written
- Contract row: RMV-UNR-01…-13, -16, -17
- Source: Claude (GPT considered this and dropped it; I re-tested and kept it)
- Evidence:
  - Every `rem-removal.contract.md:50-70` pattern is written `A\|B` inside `grep -rIE`. In ERE (GNU grep and ugrep 7.8.4 here), `\|` is a literal pipe.
  - `echo WhAwbPool | grep -cE 'WhAwb\|AwbPool'` returns **0**.
  - RMV-UNR-01 as written matches **0** files under `warehouse/` today; unescaped it matches 47. The gate passes on "no match", so it passes while the feature is still present.
  - RMV-UNR-16's psql regex has the same `\|`, which PostgreSQL also reads as a literal pipe, so the count is always 0.
  - `:12` claims every pattern "matches today". That is only true after a markdown renderer decodes `\|`.
  - RMV-UNR-17 (`:66`) uses `<the 17>` placeholders and `{a,b}` shorthand, which is not SQL.
  - FRD-REM §6 (`:160-167`) writes the same gates unescaped, so the two documents differ. `p7-13.md` carries no literal commands of its own.
- What a user experiences: the P7 exit proof can report "absent" for a feature that is still in the tree.
- Fix: put the patterns in fenced blocks outside the table, unescaped (or reference FRD-REM §6 gate ids). Expand RMV-UNR-17 to the literal route list. Add an anti-vacuous step that runs each pattern on the pre-P7 tree and requires a match.

### F-SR-010 — MINOR · An Appendix A deletion target escapes every absence check
- Contract row: RMV-UNR-06, RMV-UNR-22
- Source: Both
- Evidence:
  - `D/docs/frd/FRD-REM.md:263` deletes `WhTrackingEventRequest.java`.
  - Its content (`C/warehouse/backend/src/main/java/ai/warehouse/dto/request/WhTrackingEventRequest.java:11-35`) matches no GATE-1…8 or RMV pattern; its only removed-feature word is an unquoted `NDR` in the Javadoc.
  - This is 1 of 478 Appendix A files.
- What a user experiences: nothing at runtime, but the absence proof passes if the dead DTO survives.
- Fix: add an exact-path absence check generated from Appendix A (`test ! -e` per path) alongside the semantic greps.

### F-SR-011 — MINOR · WH-SC-478 still expects the pre-fix RMA status
- Contract row: POS-T1-20
- Source: GPT
- Evidence: `FRD-STORES.md:331` expects "one RMA `OPEN`". The port defaults to `APPROVED` (`po-schedule-port.contract.md:185`, R29 TS-F21), and p8-15 tests for `APPROVED` (`D/issues/p8-15.md:57`).
- What a user experiences: the acceptance scenario fails the corrected build.
- Fix: WH-SC-478 should expect `APPROVED`.

### F-SR-012 — MINOR · CN-8 is not recorded consistently
- Contract row: STO-D25 / FRD-TRADE CN-8
- Source: Claude (GPT judged CN-8 consistent; that is true of the registry, POS and p8-01, but not of the documents below)
- Evidence:
  - `D/docs/frd/FRD-TRADE.md:718,721`: heading "`CN-8` open", while the row at `:732` says "Resolved 2026-10-23".
  - `D/issues/p9-11.md:39`: "`CN-8` is open on `p8-01` … the PO `TOLERANCE` change type is hidden on WS-296", contradicting `:37` "Both are resolved".
  - The FRD-STORES §12c table (`FRD-STORES.md:537-547`) lists CN-1…CN-7 only.
  - The epic invariant says "`CN-1`…`CN-7`" (`10-EPIC-p8.md:52`).
- What a user experiences: a P9 builder following p9-11 may hide the PO `TOLERANCE` amendment even though core supports it.
- Fix: add a CN-8 row to FRD-STORES §12c, retitle FRD-TRADE §12c, fix the p9-11 `:39` sentence and the epic line 52.

### F-SR-013 — MINOR · CN-8's "new band" is undefined once excess was approved, and trade has no handling for the refusal
- Contract row: POS-GRD-15, STO-D25
- Source: Claude
- Evidence:
  - `po-schedule-port.contract.md:102` refuses an amendment that "would leave already-received quantity outside" the band.
  - The receipt guard's band is `H + T + excess_approved` (`grn-bill-match.contract.md:80`). A line with approved excess sits above `H + T` by design, so any tolerance amendment on it reads as a refusal.
  - `TOLERANCE_BELOW_RECEIVED` appears nowhere on the trade side (only `p8-01.md:114`, `po-schedule-port:102,175`, `FRD-STORES.md:362`; `trade-order-amendment.contract.md:112` has no row for it).
  - `p9-11.md:69` expects "a later GRN over 2 % is refused by core's guard". Under FR-520 that GRN goes to excess approval, not refusal.
- What a user experiences: an approved trade tolerance amendment rolls back with a core 409 that no trade screen anticipates.
- Fix: define the band as `effective × (1 + T_new) + Σ excess_approved`. Add a TOA row for the refusal (pre-check, or a shown refusal). Reword p9-11:69 as "requires approval above 2 %".

### F-SR-014 — MINOR · The bill and PO are not mandatory at the gate
- Contract row: FR-508, GTE-GRD-01…-03, GBM-GRD-04
- Source: Claude
- Evidence:
  - FR-508 says an inward purchase entry "carries" bill no/date and links POs at creation (`FRD-STORES.md:172`).
  - GTE-GRD-01/-03 (`gate-entry.contract.md:91-94`) validate only what is present.
  - The only bill enforcement is at GRN post, behind `warehouse.receiving.bill_required_for_po_receipt` (`grn-bill-match:76`), and no task states its default (`D/issues/p8-14.md:26`).
- What a user experiences: a `PURCHASE_RECEIPT` entry can be saved with no PO and no bill, against the client's "PO, bill no/date on arrival".
- Fix: add GTE-GRD-03a (purchase receipt ⇒ ≥1 PO and a primary bill, or a setting), and state the `bill_required_for_po_receipt` default.

### F-SR-015 — MINOR · The gate-security persona cannot turn a vehicle back
- Contract row: GTE-T1-03, WH-SC-429
- Source: Claude
- Evidence: the persona's permissions exclude `wh_gate_entries:turn_back` (`FRD-STORES.md:94`), yet WH-SC-429 has `sec1` turn the vehicle back (`:281`). The action needs `:turn_back` (`gate-entry.contract.md:72`).
- What a user experiences: guards seeded per the persona cannot turn a vehicle back at the gate.
- Fix: add `:turn_back` to the persona and to the gate bundle in `V511402`, or change the scenario's actor.

### F-SR-016 — MINOR · The OD-26 default refers to a site type that does not exist
- Contract row: OD-26, MRA-OPEN-01
- Source: Claude
- Evidence:
  - The default is "true for site types production store / raw-material store" (`FRD-STORES.md:369`, `mrn-authorisation.contract.md:147`, `D/issues/p8-08.md:24`).
  - `WAREHOUSE_TYPE` has `GENERAL`, `DISTRIBUTION_CENTER`, `STORE`, `WORKSHOP`→`PRODUCTION_STORE` and `STOCK_POOL` only (`C/warehouse-base/.../V500012__…sql:196-200`). It is declared "a label, not a behaviour (P1-05)" (`:191`).
- What a user experiences: the builder must invent either a type or a behaviour switch.
- Fix: key the default to `PRODUCTION_STORE` (plus a seeded raw-material type if wanted), or default per site in the install wizard. Record the exception to "label, not behaviour".

### F-SR-017 — MINOR · The eight frozen KPI rows do not match FR-534
- Contract row: FR-534, SIR-T5-07
- Source: Claude
- Evidence:
  - FR-534 includes "issue → return elapsed" and a site target for every measure (`FRD-STORES.md:226`).
  - p8-13 freezes eight measures without issue→return elapsed (`D/issues/p8-13.md:21`).
  - Targets are seeded for 5 measures only, with none for dock-to-stock or fill rate (`:33`).
- What a user experiences: a measure the FR promises is missing, and two measures show no "% inside target".
- Fix: add `ISSUE_TO_RETURN` (making nine rows) or drop it from FR-534. Add `kpi_target_dock_to_stock_hours` and a fill-rate target.

### F-SR-018 — MINOR · The `createRma` port command lacks the required RMA date
- Contract row: registry R.2 `WhRmaPort.createRma`, POS-T1-20
- Source: Claude
- Evidence: the command's field list has no `rmaDate` (`FRD-STORES.md:436`), but `WhRmaService.create` takes a `WhRmaRequest` with `@NotNull rmaDate` (`C/warehouse/backend/src/main/java/ai/warehouse/dto/request/WhRmaRequest.java:32-33`).
- What a user experiences: the builder must invent a default.
- Fix: add `rmaDate` to the command, or state "core sets the site-local today".

## Dropped after verification
- None of the 18 was dropped in the merge.
- I overruled one GPT drop. GPT dropped the `\|` pattern escaping as "presentation syntax"; I re-ran the raw patterns (0 matches against 47) and kept it as F-SR-009.
- I agree with GPT's other self-drop: Rule 56 for reasonless `ISSUE` is already classified by movement type (`WhinStockAccountPeriodQueryService.java:275-281`).

## Remediation backlog
| Finding | Files to touch | Migration | Shared registries | Parity apply-to | Contract |
|---|---|---|---|---|---|
| F-SR-001 | `D/docs/contracts/gate-entry.contract.md`, `D/issues/p8-03.md` | none | none | none (core only) | GTE-T1-05, -12, GRD-09 |
| F-SR-002 | `D/docs/frd/FRD-STORES.md` R.3, gate-entry contract, `p8-03.md` | none | port/seam registry | warehouse-india, warehouse-manufacturing resolvers | GTE-GRD-15 |
| F-SR-003 | FRD-STORES R.2, `po-schedule-port.contract.md`, `p8-02.md` | none | registry R.2/R.4 | warehouse-trade sales | new POS-T1-11d |
| F-SR-004 | FRD-STORES R.1, POS §0, `p8-01.md`, `p9-01.md`, `p10-01.md` | sibling seeds (next free in V550000/V560000 band) | `permission_dependencies`, scope pair grants | warehouse-trade, warehouse-manufacturing | POS-GRD-13 |
| F-SR-005 | `p8-08.md` | none | none | none | MRA-GRD-05 |
| F-SR-006 | `p8-01.md`, `p8-09.md`, POS §0 | V511400 → V511408 | `permission_dependencies` | warehouse-manufacturing | POS §0 |
| F-SR-007 | `grn-bill-match.contract.md`, `p8-04.md`, FRD-STORES FR-516 | none | none | none | GBM-GRD-02 |
| F-SR-008 | `store-issue-return.contract.md`, `p8-11.md` | V501235 | none | none | SIR-T4-03 |
| F-SR-009 | `rem-removal.contract.md`, `p7-13.md` | none | none | all four warehouse modules | RMV-UNR-01…-17 |
| F-SR-010 | `rem-removal.contract.md`, `p7-13.md` | none | none | all four warehouse modules | new RMV-UNR-26 (exact paths) |
| F-SR-011 | FRD-STORES §9 | none | none | warehouse-trade | WH-SC-478 |
| F-SR-012 | `FRD-TRADE.md` §12c, `p9-11.md`, FRD-STORES §12c, `10-EPIC-p8.md` | none | none | warehouse-trade | CN-8 row |
| F-SR-013 | `po-schedule-port.contract.md`, `trade-order-amendment.contract.md`, `p9-11.md` | none | none | warehouse-trade | POS-GRD-15, new TOA row |
| F-SR-014 | gate-entry contract, `p8-03.md`, `p8-14.md` | none (V511402 / V511413) | settings registry | none | new GTE-GRD-03a |
| F-SR-015 | FRD-STORES §3, `p8-03.md` | none (V511402) | role bundle grants | none | GTE-T2-03 |
| F-SR-016 | FRD-STORES OD-26, MRA, `p8-08.md` | none (V511407) | settings registry | none | MRA-OPEN-01 |
| F-SR-017 | FRD-STORES FR-534, `p8-13.md` | none (V511412) | settings registry | none | SIR-T5-07 |
| F-SR-018 | FRD-STORES R.2, POS §8a, `p8-15.md` | none | none | warehouse-trade | POS-T1-20 |

## Parity (C10)
- Mobile: none. The contracts say so with a reason (`D-16` item 7; FRD-STORES §4, §12 row 12; FRD-REM §1).
- Siblings sharing these seams (apply-to): warehouse-trade (ports, guards, service principal, CN-8), warehouse-manufacturing (requisition port, cost-object and QC resolvers, `SUBCONTRACT_DISPATCH`), warehouse-india (`DELIVERY_CHALLAN` resolver, Rule 56). The REM fence (dealer, automotive, accessories, services, insurance, assets) holds.

## In code, not in contract
- Core PO/demand/RMA services check site scope before validation (`WhPurchaseOrderService.java:244-245`). The port principal rules do not mention this (F-SR-004).

## Contract quality
- All 8 contracts are v0 and unratified.
- SIR-OPEN-03 (register grid ids) is still open.
- MRA-OPEN-03 (recall release target) is deferred to build.
- FRD-STORES §4's claim that a rebuilt and an upgraded DB apply P8 "in the same order" is true only for the full set. Tasks landing one at a time interleave the base, schema and seed blocks. This is harmless while out-of-order is enforced and the only cross-block dependency is F-SR-006.
- Epic `10-EPIC-p8.md:97-98` is stale: it says DATA-MODEL, IMPLEMENTATION-PLAN, FRD-MFG and p10 still cite the old numbers, but the old numbers now occur only in the R29 reviews.

## Referred to standards reviewer
- None.