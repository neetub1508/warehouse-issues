# R24 — workflow contract completeness

<!-- check-design-set: screen-citations file WS-238 — the BUILD-SPEC-SCREENS.md §1 next-free allocation marker; no RJ finding allocates a screen id -->

**Date** 2026-09-10 · **Prefix** `RJ-` · **Branch** `docs/round-4-cardinality-and-gaps` · **Mode** gap report (no code exists): I derived the contracts from the design set rather than from code.

**File set read — 30 files.**

```bash
cd warehouse-issues
# docs/ (9): DECISIONS · WAREHOUSE-FUNCTIONAL-REQUIREMENTS · DATA-MODEL · SCENARIO-CATALOGUE
#            BUILD-SPEC-SCREENS · PORT-AND-ADAPTER-CONTRACT (transfer + virtual-location §§) · IRREVERSIBLE (branch row)
#            GAP-REGISTER-R2 · GAP-REGISTER-R3
# docs/reviews/ (read for exclusion): R10 R11 R16 R17 R18 R19 R20 R21 (+ R9 H-004 heading)
# issues/ (21): p0-09 p0-13 p1-05 p1-07 p1-12 p1-13 p1-14 p1-15 p1-17 p1-18 p2-01 p2-02 p2-03 p2-04
#               p2-05 p2-07 p2-08 p2-09 p2-12 p2-13 p2-17 p2-25 p2-26 (+ headers of all 143)
grep -rnoE "\bRJ-[0-9]{1,3}\b" docs issues tools | wc -l          # → 0  (prefix free)
grep -rn "whb_warehouse_branches" docs issues | grep -v reviews/R22 | wc -l   # → 0 outside R22 (specified in RG-001, not yet folded)
```

**Method.** For each of the 13 workflows I built the five contract tables from the set's own text:
- T1 states and transitions
- T2 actors and permissions
- T3 time-driven rules
- T4 cross-entity effects
- T5 screen elements

The sources were: DATA-MODEL for status values, BUILD-SPEC §0.11 for ladders and §10.2 for verb permissions, the screen blocks for actions, the task files for what actually gets built, and the scenarios for what must be observably true. Every missing row or disagreement between those five sources became a finding.

---

## §1 · Verdict

**The ledger is complete; the documents that drive it are not.** Every movement shape is specified exactly: three-leg transfer, pick to staging, status change at the same location, returns into `RETURNED`. But the **document lifecycles** that decide *when* each movement is posted, by whom, and what can be undone are mostly unwritten for v1:
- `H-004` was folded as BUILD-SPEC §0.11 with a completion rule (*"a task creating a `status` column ships its ladder rows in the same PR"*, §0.11:260-262).
- That rule never reached the v1 task files. Only `p2-13:17` and `p2-19:28` carry a ladder.
- 21 v1 workflow status columns have neither a vocabulary nor a ladder (`RJ-004`), and 11 v1 documents perform state changes gated by no verb permission (`RJ-005`).

**The transfer is the workflow that fails, and it fails three ways.**
1. It contradicts your branch↔warehouse decision (`RJ-001`).
2. Its in-transit stock is placed at two different sites by five documents, and the arrive leg is refused by P1-18's scope guard under either reading (`RJ-002`).
3. It runs on its own unreserved document, while P2-08's acceptance requires it to run through the one demand model (`RJ-003`).

WH-SC-058 is a v1 exit-criterion scenario, and none of the three is visible from a single document.

**Everything else is cheap.** Every proposal below is:
- a ladder table,
- a §10.2 row,
- a column, or
- one sentence in an existing task.

Only `RJ-001` lands before `PNR-1` (`V500012`), and it is cheap *because* it lands there.

## §1.1 · Coverage table

**Key:** `COMPLETE` = all of T1–T5 are resolvable from the set · `HOLED` = the workflow completes but has a named gap · `BROKEN` = a v1 acceptance scenario cannot pass as written.

| # | Workflow | Ver | Verdict | Findings (new) | Already owned by earlier rounds |
|---|---|---|---|---|---|
| 1 | Goods receipt (PO / blind) + QC / quarantine | v1 | HOLED | RJ-004 RJ-005 RJ-014 RJ-017 RJ-018 | U-004 · Y-005 · X-055 · RE-004 |
| 2 | Putaway | v1 | HOLED | RJ-017 | Y-004 |
| 3 | Replenishment | v1 | HOLED | RJ-004 RJ-014 | RA-006 |
| 4 | Allocation / reservation | v1 | **BROKEN** | **RJ-007** RJ-015 RJ-003 | Y-002 |
| 5 | Pick / pack / ship | v1 | HOLED | RJ-003 RJ-004 RJ-006 | U-001 · U-005 · Y-003 |
| 6 | Inter-branch / inter-site transfer (3 legs) | v1 | **BROKEN** | **RJ-001 RJ-002 RJ-003** RJ-006 RJ-012 | RE-002 (seed only) |
| 7 | Returns — customer RMA + vendor return | v1 | HOLED | RJ-005 RJ-006 RJ-010 RJ-014 | U-003 |
| 8 | Cycle / physical count + adjustment approval | v1 | HOLED | RJ-004 RJ-006 RJ-016 | RA-008 · RA-004 |
| 9 | Lot / serial / expiry (FEFO) | v1 | HOLED | RJ-008 RJ-009 RJ-012 | Y-002 |
| 10 | Kitting / assembly | v1.1 | HOLED | RJ-005 RJ-013 | — |
| 11 | Valuation posting to accounting | v1 | HOLED | RJ-010 RJ-011 | RF-001…RF-005 · RC-002 |
| 12 | 3PL owner billing | v2 | HOLED | RJ-011 | RF-007 · RF-008 · H-001 |
| 13 | Branch↔warehouse M:N (counter sales, transfers, scope) | v1 | **BROKEN** | **RJ-001** RJ-002 | RA-001 (warehouse grants — composes with RJ-001) |

---

## §2 · The findings

### `RJ-001` · The M:N branch↔warehouse decision (specified in R22 `RG-001`) is not yet folded, and four authorities explicitly refuse it — **BLOCKER**

- **What is missing or wrong.** The decision is `whb_warehouse_branches`: exactly one `REGISTERED` branch per warehouse, and `SERVING` branches that may draw stock. It is specified in R22 `RG-001` but not yet folded into FR-079, DATA-MODEL, IRREVERSIBLE or P1-05. Instead:
  - `FR-079` (FRD:219): *"A warehouse **belongs to exactly one branch** (`branch_id NOT NULL`) … the accessories many-to-many bridge is not copied"*.
  - `DATA-MODEL.md:452` makes `whb_warehouses.branch_id` a scalar, crossing FK `B1` at `:1411`.
  - `DATA-MODEL.md:3991` refuses the junction: *"`wms_warehouse_branches` — **dropped** — The M:N junction. **One branch, one GSTIN**"*.
  - `IRREVERSIBLE.md:555` freezes the scalar as a v1 irreversible row.
  - `issues/p1-05.md:56-57` builds `V500012` with `branch_id NOT NULL`, and `:130-132` says *"Do not repeat the accessories junction … exactly one branch"*.
  - WS-016 renders one `branchName` (BUILD-SPEC:807, :816).
- **Why it matters.** Every branch-aware rule in the set reads branch *through* `whb_warehouses.branch_id`. Under M:N, each of those reads becomes ambiguous:
  1. **Transfers.** `wh_transfer_orders.source_branch_id`/`destination_branch_id` (DATA-MODEL:1003) and FR-305's deemed-supply derivation assume one branch per warehouse. Nothing says the snapshot is the *registered* branch, or what a "transfer to a serving branch" means, given that a branch holds no stock.
  2. **Counter sale.** `whad_counter_sales` carries both `branch_id` and `warehouse_id` with no rule linking them (DATA-MODEL:1272). If a serving branch draws from a warehouse registered under a *different GSTIN*, it is invoicing goods that sit at another registration's premises. That is a deemed supply the design has no path for, which puts it on the same boundary as `U-003`/`OD-9`.
  3. **Branch-scoped visibility.** FR-404's view-branch tier (FRD:710), P1-18's predicate (`p1-18.md:88-92`) and WH-SC-242 need to know whether a serving branch sees, reserves, adjusts or counts a warehouse's stock. They cannot tell.
  4. **Numbering.** Per-branch series `whb_number_series.branch_id` (DATA-MODEL:910) and the per-branch challan series (FR-307, FRD:569) need to know whose series a warehouse's challan uses.
  5. **Accounting envelope.** It carries *"company, **branch**"* (FR-233, FRD:436), and the branch is no longer a scalar join.
  6. **Branch-split reports.** FR-162 (FRD:332) and the godown statement would double-count stock across serving branches if they join through the junction.
- **Where the junction is specified.** The junction itself is specified in R22 `RG-001`; `RJ-001`'s rules R1–R5 are the workflow reading of it — what transfers, counter sales, branch scope, numbering, the envelope's `branch` and branch-split reports must do once it exists.
- **Proposal.**
  1. Replace the scalar with `whb_warehouse_branches(warehouse_id, branch_id, role, effective_from, effective_to)`, where `role` ∈ `REGISTERED`/`SERVING`. It needs a partial unique index "one `REGISTERED` per warehouse per instant" and a service guard "every warehouse has one".
  2. **Effective-date it**, because changing the registered branch is a premises re-registration. Historical challans and branch reports must resolve the branch *as at* their date.
  3. State these rules:
     - **R1:** branch attribution of stock, the envelope's `branch`, and the per-branch series all resolve to the `REGISTERED` branch as at `posting_date`. They are never a serving branch.
     - **R2:** a transfer's two branch snapshots are the two warehouses' registered branches. A branch↔branch transfer is not an object.
     - **R3:** a serving branch may **view availability and reserve/issue** (counter sale, job issue) only where its GSTIN equals the registered branch's GSTIN. Across GSTINs, drawing stock *is* a transfer to one of the serving branch's own registered warehouses.
     - **R4:** only the registered branch's users may receive, count, adjust or close.
     - **R5:** branch-split reports attribute to the registered branch only.
  4. This composes with `RA-001`'s `whb_warehouse_grants`: grants give a person scope; the junction gives a branch scope.
  5. Amend FR-079, DATA-MODEL:452/:1411/:3991, IRREVERSIBLE:555, P1-05 `V500012` (same migration, before `PNR-1`), and give WS-016 a child `DataTable` rather than a new WS id.
- **Version** v1 · P1 · **Tasks** `P1-05` `P1-18` `P0-15` `P1-17` `P2-02` `P2-25` `P2-IN-03` `P2-18` `P2-20` `P2-21` `P5-18`.
- **Irreversibility.** Irreversible after `V500012` gains rows *and* the first challan or envelope carries a branch. Today it is free.
- **Relationship to prior rounds.** New. Every earlier round assumed FR-079. `RA-001` is the person-scope axis, not this.

### `RJ-002` · In-transit stock sits in two different places depending on the document, and under either reading the receiving storekeeper is refused by P1-18's scope guard — **BLOCKER**

- **What is wrong.**
  - FR-147 (FRD:317) and WS-090 (BUILD-SPEC:1609-1611) put the in-transit location *"**at the sending site**"*, and FR-148 (FRD:318) says the sender holds it.
  - WH-SC-058 (SCENARIO:229), WH-SC-120/122 (:311, :313), `p2-02.md:16-17` and PORT-AND-ADAPTER-CONTRACT:1594-1595/:1743 post the depart leg to **`TRANSIT-WH/IN_TRANSIT-<ref>`**, a separate non-physical `whb_warehouses` row.
  - P1-18's acceptance says *"A storekeeper scoped to site A **cannot post, adjust or reverse** a movement at site B"* (`p1-18.md:88`).
  - The arrive leg debits the transit location. That location is at SITE-A under reading 1 and at `TRANSIT-WH` under reading 2. Either way, a SITE-B storekeeper cannot post it, and the transit-loss adjustment (WH-SC-122) has the same problem.
- **Why it matters.**
  - WH-SC-058 (v1 exit criterion) and WH-SC-243 cannot both pass.
  - The two readings also value differently. Under FR-236 (FRD:439) the grain is site-level, so depart into `TRANSIT-WH` is itself an inter-site valuation event, and the sender's valuation omits stock FR-148 says it holds.
  - Under FR-079, `TRANSIT-WH` must belong to exactly one branch, so all in-transit stock company-wide reports under that one branch.
- **Proposal.**
  1. Adopt the FRD reading: the transit location is a child of the **source** warehouse, with a location type of `IN_TRANSIT`, one per transfer. Delete `TRANSIT-WH` from the port contract and the scenarios. `RE-002`'s seeding fold then shrinks to a location type.
  2. Add to P1-18: *"`wh_transfer_orders:receive` and the transit-loss adjustment authorise posting against **that transfer's** transit location regardless of site scope; they never authorise any other location at the source site."*
  3. Restate WH-SC-058/120/122/125 accordingly.
- **Version** v1 · P1/P2 · **Tasks** `P1-05` `P1-18` `P2-02` `P2-01` (+ PORT-AND-ADAPTER-CONTRACT §transfer, SCENARIO §3.6).
- **Irreversibility.** The transit location's `warehouse_id` is on every depart line forever, so decide before the first transfer.
- **Relationship to prior rounds.** Extends `RE-002`, which found only that `TRANSIT-WH` is seeded nowhere. The site contradiction and the scope refusal are new.

### `RJ-003` · Transfers and supplier returns run beside the one demand model, not through it, so their stock is never reserved and two tasks' acceptance criteria contradict each other — **BLOCKER**

- **What is wrong.**
  - FR-177 (FRD:357) and WH-SC-087 (SCENARIO:268) say an inter-site transfer is allocated, picked and shipped by the one demand model. `p2-08.md:97` makes that an acceptance line: *"Five demand types — sales, **transfer**, job issue, replenishment, scrap — allocate and ship through one code path"*.
  - But P2-02 and WS-090 build **Add · Pick · Dispatch · Receive** on `wh_transfer_orders` (BUILD-SPEC:1620), with verbs `wh_transfer_orders:dispatch`/`:receive` (§10.2:2228).
  - Neither table references the other: `wh_transfer_orders` has no `demand_order_id` (DATA-MODEL:1003), and `wh_pick_tasks` can only point at a `demand_order_line_id` (:1026).
  - Supplier returns repeat the pattern: WS-084 has its own **Pick · Dispatch** (`p2-13.md:45`), while FR-275 says *"return to vendor is an ordinary outbound"* (FRD:504). No demand type for a vendor return exists in FR-177's list.
- **Why it matters.**
  - Between a transfer being created and dispatched, nothing reserves its stock (P2-02 never mentions `whb_reservations`), so a customer order can allocate the same units.
  - WS-090's "Pick" has no pick-task mechanism behind it.
  - Whichever of P2-02 and P2-08 is built first, the other's acceptance fails.
- **Proposal.**
  1. A transfer and a supplier return each create one `wh_demand_orders` row: `demand_type` `TRANSFER`, or a new `VENDOR_RETURN`, as a catalogue row rather than a CHECK.
  2. Add a nullable `demand_order_id` to `wh_transfer_orders` (`P1-17`'s `V510031`) and to `wh_supplier_returns` (`P2-13`'s `V510020`).
  3. Reservation, pick and staging are the demand path (P2-07/P2-09). *Dispatch* is `wh_shipments:dispatch` posting `TRANSFER_DEPART` to the transit location instead of `VIRT-CUSTOMER`.
  4. Restate FR-189 as *"dispatch is the only relief event; for a transfer the relief is into transit"*.
  5. WS-090 keeps Receive, Report variance and the challan.
- **Version** v1 · P1/P2 · **Tasks** `P1-17` `P2-02` `P2-08` `P2-09` `P2-10` `P2-13`.
- **Irreversibility.** Reversible, but P1-17's migration is where the link column is free.
- **Relationship to prior rounds.** New. R10 walk 5 walked the legs, not the allocation.

### `RJ-004` · 21 v1 workflow status columns have no values and no ladder, and the §0.11 "still owed" list names only three of them — **BLOCKER**

- **What is missing.** DATA-MODEL declares a bare `status` with no values on the following v1 workflow documents:
  - `wh_receiving_sessions` (:972), `wh_goods_receipts` (:974), `wh_receipt_reversals` (:977), `wh_reconciliation_cases` (:986)
  - `wh_stock_adjustments` (:1001), `wh_transfer_orders` (:1003), `wh_counts` (:1009), `wh_reconciliation_exceptions` (:1015)
  - `wh_demand_orders` and `.line_status` (:1021-1022), `wh_purchase_order_lines.line_status` (:968), `wh_shipments` (:1031)
  - `wh_return_receipts` (:1072), `wh_rmas` (:1074), `wh_replenishment_runs`/`_suggestions` (:1093-1094)
  - `wh_landed_cost_documents` (:1106), `wh_revaluations` (:1108), `whad_counter_sales` (:1272), `whas_material_requests`/`_lines` (:1290-1291)

  §0.11 (BUILD-SPEC:234-376) draws ladders for periods, POs, handovers and 3PL. Its "still owed" list (:369-376) names only `wh_counts`, `wh_quality_inspections` and `wh_demand_orders`. The completion rule (:260-262) puts every other ladder on its creating task, and no v1 task carries one: `grep` for ladder syntax across `issues/` hits only `p2-13.md:17` and `p2-19.md:28`.
- **Why it matters.**
  - The statistics strips promise states that have no value: WS-089 *"awaiting approval"* (:1601), WS-094 *"counting · pending approval"* (`p2-04.md:61`), WS-099 *"picking · packed"* (:1699).
  - Every `status` multiselect filter needs an option list.
  - §0.11:251-253 states the consequence itself: *"A status value written by a build that guessed the ladder is in the customer's table forever."*
- **Proposal.** Fold Appendix A's ladders into the owning tasks in §0.11's column format. Add one acceptance line per task: *"no state without an inbound transition; no non-terminal state without an outbound one"*.
- **Version** v1 · **Tasks** `P1-13` `P1-16` `P1-12` `P2-01` `P1-17`/`P2-02` `P2-04` `P2-06` `P2-08` `P2-10` `P2-12` `P2-13` `P2-15` `P2-17` `P2-25` `P2-26`.
- **Relationship to prior rounds.** Extends `H-004`, which was scoped to 31 P3–P6 tables, into v1. It is not a re-raise: the v1 set was never enumerated.

### `RJ-005` · 11 v1 documents perform state changes gated by no verb permission — **MAJOR**

- **What is wrong.** §10.2:2204-2205 states the rule: *"A transition with no verb permission is a transition anybody with `:edit` can perform."* Against the action cells:

| Document | Action with no verb | Evidence |
|---|---|---|
| `wh_transfer_orders` | Approve (the columns `requires_approval`/`approved_by` exist; no action and no verb, so the columns are dead), Pick, Report variance, Cancel | DATA-MODEL:1003 · BUILD-SPEC:1620 · §10.2:2228 |
| `wh_supplier_returns` | **all of them**: Approve, Pick, Dispatch, Close, Cancel | `p2-13.md:45`; no §10.2 row |
| `wh_stock_adjustments` | Submit, Post, Cancel | BUILD-SPEC:1597 vs §10.2:2227 |
| `wh_counts` | Generate, Recount, Cancel | :1636 vs :2230 |
| `wh_rmas` | Approve, Expire, Match | :1780 |
| `wh_return_receipts` | Post, Match RMA, **approve a scrap disposition** (FR-273 *"an approver"*, WH-SC-201 `mgr1` approves) | `p2-12.md:66` vs :2235 |
| `wh_quality_inspections` | approve a scrap disposition (FR-164) | :2226 |
| `wh_receiving_sessions` | Complete, Cancel | `p1-13.md:51` |
| `wh_reconciliation_cases` / `_suggestions` | Resolve / Accept, Reject | :1570, :1785 |
| `wh_shipments` | Cancel, **Confirm delivery** (FR-447 names `wh_shipments:confirm_delivery`) | :1715 vs :2233 |
| `whas_material_requests` | Reserve, **Return unused** (FR-360's return-to-store), Cancel | :1915 vs :2240 |
| `wh_work_orders` (v1.1) | Release, Issue, Complete, Cancel | `p3-11.md:39` records the absence itself |

- **Proposal.** Add these rows to §10.2, seeded by `P1-20` (app) and `P0-15` (base), plus `permission_dependencies`. Scrap approval reuses `wh_stock_adjustments:approve` semantics with approver ≠ actor (FR-408).
- **Version** v1 (work orders v1.1) · **Tasks** `P1-20` `P0-15` `P1-13` `P1-14` `P2-01` `P2-02` `P2-04` `P2-10` `P2-12` `P2-13` `P2-15` `P2-26` `P3-11`.
- **Relationship to prior rounds.** New. `RA-007` concerns the PC-31↔§10.2 namespace; `H-001` concerns P5 verbs.

### `RJ-006` · Five v1 states have no way back out — **MAJOR**

- **What is missing.**
  1. **Transfer cancelled after dispatch.** Stock is in transit and Cancel is offered (BUILD-SPEC:1621), but there is no return-to-sender leg.
  2. **Count cancelled after Freeze.** Freeze sets the location to `COUNTING` (`p2-04.md:103`), but no document names the transition back. `FROZEN` has **no setter anywhere**: it is listed only at BUILD-SPEC:860 and DATA-MODEL:453, so it is unreachable. A cancelled count therefore leaves bins unpickable (WH-SC-192).
  3. **Supplier return cancelled after `PICKED`.** This is the staged-stock hole `FR-449` closed for orders only (`p2-13.md:17`).
  4. **Posted return receipt.** It has no reversal (WS-135 actions, `p2-12.md:66`). `P1-16` covers GRNs only.
  5. **Shipment "Cancel"** (:1715). No rule says whether it is valid after dispatch.
- **Proposal.**
  - Transfer: `IN_TRANSIT → CANCELLED` posts `TRANSFER_RETURN` from the transit location back to the source, with a reason code.
  - Locations: write the `whb_locations.status` ladder. Freeze sets `COUNTING`; Post or Cancel restores the prior status. Either give `FROZEN` a setter (the stocktake window, FR-157) or delete it.
  - Supplier return: `PICKED → CANCELLED` requires de-staging (`409 STAGED_STOCK`).
  - Return receipt: `POSTED → REVERSED` via L-3, allowed only before disposition.
  - Shipment: Cancel is legal only before `DISPATCHED`.
- **Version** v1 · **Tasks** `P2-02` `P2-04` `P1-05` `P2-13` `P2-12` `P2-10`.
- **Relationship to prior rounds.** New. `Y-003` is the order-staging case only.

### `RJ-007` · Hard reservations expire: the expiry job releases a released order's hold mid-pick — **MAJOR**

- **What is wrong.** Every reservation carries `expires_at` (`p0-09.md:12`, `:100`). The job releases expired rows with no exemption by type (FR-170, FRD:345; `p2-07.md:32`). After pick, *"the reservation stays open and is now attached to the staged stock"* (`p2-09.md:30`).
- **Why it matters.** A HARD row that expires mid-pick, or while stock is staged, releases the hold. This reaches `Y-003`'s orphaned-staging state through a job instead of a cancel.
- **Proposal.** `expires_at` applies to SOFT rows only. HARD rows are released only by consume, cancel or explicit release. Ageing shows stale HARD rows separately.
- **Version** v1 · **Tasks** `P0-09` `P2-07` `P2-09`.
- **Relationship to prior rounds.** New.

### `RJ-008` · A lot can be held three different ways — **MAJOR**

- **The three mechanisms.**
  - `whb_lots.status_code` plus `hold_reason_code_id` (DATA-MODEL:574; FR-096, FRD:241; `p1-07.md:70`, `:131`: *"blocks allocation everywhere at once, **with nothing moved**"*).
  - A `wh_holds` row with `hold_scope = LOT` (DATA-MODEL:1005-1006).
  - A mass hold that posts one status-change movement per position (`p2-03.md:95`).

  WH-SC-139 is closed by P2-03 but asserts P1-07's mechanism.
- **Why it matters.**
  - The allocator must consult three sources.
  - FR-448's reservation rule covers only the movement path.
  - The L-4 rebuild cannot reproduce a lot status.
  - Each mechanism releases differently.
- **Proposal.** A lot hold is a `wh_holds` row. `whb_lots.status_code` becomes derived or display-only. The status-change movement is reserved for physical segregation.
- **Version** v1 · **Tasks** `P1-07` `P2-03` `P2-07`.
- **Relationship to prior rounds.** New.

### `RJ-009` · The per-customer shelf-life-at-ship guard has no column — **MAJOR**

- **What is missing.** FR-161's point 3 is *"per customer or channel"* (FRD:331; `p2-05.md:30`). WH-SC-134 (v1·P2, SCENARIO:330) asserts a customer-specific 40% rule. The only column is `whb_items.min_shelf_life_ship_pct` (DATA-MODEL:529); no counterparty or channel column exists.
- **Proposal.** Add `whb_shelf_life_ship_rules(counterparty_id, channel_id, item_category_id, min_pct)`, resolved most-specific-first like `whb_negative_stock_policies`, with the item value as the fallback.
- **Version** v1 · **Tasks** `P1-08` `P1-03` `P2-05`.
- **Relationship to prior rounds.** New.

### `RJ-010` · Blind returns and returns to vendor have no rule for what cost they carry — **MAJOR**

- **What is missing.** FR-234 (FRD:437) restores *"the original layer"* by reversing the original consumption (WH-SC-152). But:
  - FR-269 (FRD:498) makes the blind return the majority case, and `original_shipment_id` is nullable (DATA-MODEL:1072), so there is no consumption to reverse.
  - The same applies to returns of stock issued before go-live.
  - A return to vendor (FR-275) never says whether it relieves the origin GRN's layer or the method's layer.
- **Proposal.**
  - Matched return: reverse the consumption.
  - Unmatched return: take the site's current method cost, flagged `cost_basis = RETURN_UNMATCHED`, and report it.
  - Return to vendor with `origin_grn_id`: relieve that receipt's layer (specific identification).
- **Version** v1 · **Tasks** `P2-12` `P2-13` `P2-16`.
- **Relationship to prior rounds.** New. R21 does not cover returns.

### `RJ-011` · A rejected handover can only be retried; one that never succeeds blocks period close and can strand a billing run — **MAJOR**

- **What is wrong.** `REJECTED`'s only exit is Retry→`PENDING` (§0.11:303-304), and the close guard requires *"no open handover"* (:273). Reversing a movement that was never posted emits a second envelope. On the 3PL side, `APPROVED → CANCELLED` is allowed *"only while no AR handover has left `PENDING`"* (:317), so an approved run whose AR handover is `REJECTED` can neither invoice nor cancel.
- **Proposal.**
  - Add `REJECTED → VOIDED` via `:void`, with approver ≠ requester, allowed only when the movement is reversed or reclassified `NOT_APPLICABLE`.
  - Reversing a never-posted movement voids both envelopes.
  - `VOIDED` is excluded from the close guard, and a billing run may be cancelled once its AR handover is `VOIDED`.
- **Version** v1 (3PL v2) · **Tasks** `P0-12` `P2-18` `P2-22` `P5-05`.
- **Relationship to prior rounds.** New. `RA-004` concerns approvals stranded by close.

### `RJ-012` · Five dated columns have no job (FR-165) — **MAJOR**

- **What is missing.** P0-13's register (`p0-13.md:52-61`) has eight rows. Missing are:
  - `wh_transfer_orders.expected_arrival_date`: a report (WS-220) but no job and no recipient.
  - `wh_rmas.expiry_date`: only a manual Expire action (:1780).
  - `whb_lots.retest_date` (`p1-07.md:36`).
  - `wh_count_programs.next_scheduled_date`/`schedule_cron`: the register names `count_frequency_class` instead of the operative column.
  - `wh_reconciliation_exceptions.age_days`: a stored age with nothing recomputing it.
- **Proposal.** Add a register row and a job for each, in the owning task.
- **Version** v1 · **Tasks** `P0-13` `P2-02` `P2-12` `P2-05` `P2-04` `P2-06`.
- **Relationship to prior rounds.** New. `RE-007` is the opposite direction (a job with no column).

### `RJ-013` · A v1·P1 acceptance scenario depends on v1.1 kitting — **MINOR**

- WH-SC-135 (SCENARIO:331, v1·P1) traces a lot *"consumed into two assembly work orders"*. It is closed by `p1-07.md:83`/`:142`.
- Work orders are v1.1 (DATA-MODEL:1097, `P3-11`), and FR-266 is v2.
- **Proposal.** Split the scenario: P1-07 keeps the trace across shipments and locations; the trace across a kit moves to `P3-11`/`P5-19`.
- **Version** v1/v1.1 · **Tasks** `P1-07` `P3-11` `P5-19`.

### `RJ-014` · Four vocabulary drifts — **MINOR**

- (a) `return_type` has ten values in FR-270 (FRD:499) and eight in DATA-MODEL:1072, `p2-12.md:69` and WS-135. WH-SC-057:228 writes `CUSTOMER_RETURN`, which appears in no list.
- (b) `suggested_source` is `TRANSFER` in FR-253 and WH-SC-281 but `SISTER_BRANCH_TRANSFER` in DATA-MODEL:1094. Separately, WS-141 (v1) cites FR-254, which is v2.
- (c) `ITEM_MISMATCH` was added by `p2-12.md:16` but is absent from DATA-MODEL:974, WS-076 and P1-13, the task that owns the column.
- (d) FR-133 says *"one inspection number per GRN"*, while WH-SC-301:592 requires a re-inspection *"with its own number"* against the same GRN.

`X-055` (CONDITIONAL vs PARTIAL) is not re-raised.
- **Tasks** `P2-12` `P1-13` `P2-15` `P1-14`.

### `RJ-015` · Re-attaching a reservation at pick is one sentence with no mechanism — **MINOR**

- What `p2-09.md:30` says about re-attaching versus the per-position CHECK `I-6` (`quantity_available >= 0`, DATA-MODEL:794): the pick debits the source position while its reservation still points there, so the CHECK fires unless the re-attach happens in the same transaction.
- **Proposal.** Release the row (`released_at`, reason `PICKED`) and create a new row at staging with the same holder quad, in the same writer transaction as the pick. State it in P0-09 and P2-09.
- **Tasks** `P0-09` `P2-09`.

### `RJ-016` · Counts with no programme have no tolerance to use — **MINOR**

- The stocktake (WH-SC-112), `SPOT` and `ZERO_STOCK` counts, and counts auto-created by a short pick (FR-185) have no programme. Tolerance lives only on `wh_count_programs` (DATA-MODEL:1007), and `RA-008`'s adjustment threshold has no home either.
- **Proposal.** An install default, which a count inherits when it has no programme.
- **Tasks** `P2-04`.

### `RJ-017` · When putaway happens for quarantined stock is not stated — **MINOR**

- Putaway tasks are created per GRN line (`p1-15.md:24`), and QC release is a status change at the same location (WH-SC-071). A grep across P1-13, P1-14, P1-15 and P2-13 finds no statement of whether putaway happens at post or at release.
- **Proposal.** The putaway task is created at release, for the released quantity.
- **Tasks** `P1-14` `P1-15`.

### `RJ-018` · A v1 PO-cancel guard reads the state of a v1.1 object that has no status values — **MINOR**

- FR-132 (FRD:297) and WH-SC-083 refuse cancellation when an *"ARRIVED ASN exists"*. But `wh_asns` is v1.1, with a bare `status` (DATA-MODEL:969).
- **Proposal.** In v1 the guard reads receiving-session arrival. The ASN clause activates in P3-05.
- **Tasks** `P1-12` `P3-05`.

---

## Appendix A · Proposed v1 status ladders (derived; every row is TBD until a person ratifies it)

These are proposed ladder rows for the "still owed" v1 tables. Every state and permission is proposed, and every guard is inferred from the source cited.

| Table | States (proposed) | Transitions · verb | Terminal |
|---|---|---|---|
| `wh_goods_receipts` | DRAFT · POSTED · REVERSED · CANCELLED | DRAFT→POSTED `:post` · DRAFT→CANCELLED `:cancel` · POSTED→REVERSED (effect of `wh_receipt_reversals` POSTED; guard FR-131 "not moved on") | REVERSED, CANCELLED |
| `wh_receipt_reversals` | REQUESTED · APPROVED · POSTED · REJECTED | `:approve` (approver ≠ requester) · `:post` | POSTED, REJECTED |
| `wh_stock_adjustments` | DRAFT · SUBMITTED · APPROVED · POSTED · REJECTED · CANCELLED | `:submit` (auto-approve below threshold, RA-008) · `:approve`/`:reject` (≠ actor) · `:post` · `:cancel` from DRAFT/SUBMITTED | POSTED, REJECTED, CANCELLED |
| `wh_transfer_orders` | DRAFT · APPROVED · ALLOCATED · IN_TRANSIT · PARTIALLY_RECEIVED · RECEIVED · CLOSED · CANCELLED | `:approve` where `requires_approval` · allocation via the demand order (RJ-003) · `:dispatch` · `:receive` · `:report_variance` → CLOSED when transit balance = 0 · `:cancel` (from IN_TRANSIT posts TRANSFER_RETURN, RJ-006) | CLOSED, CANCELLED |
| `wh_counts` | GENERATED · FROZEN · COUNTING · PENDING_APPROVAL · APPROVED · POSTED · CANCELLED | `:freeze` · submit · `:recount` (not after APPROVED — §0.11's open question, answered here) · `:approve` (≠ counter) · `:post` · `:cancel` (restores location status) | POSTED, CANCELLED |
| `whb_locations.status` | AVAILABLE · BLOCKED · COUNTING · DAMAGED · FROZEN | `:block`/unblock · count freeze→COUNTING→prior · stocktake window→FROZEN→prior | none |
| `wh_demand_orders` | OPEN · ALLOCATED · RELEASED · PICKING · PACKED · SHIPPED · DELIVERED · CANCELLED | `:allocate` · `:release` (zero open holds) · short pick → stays PICKING with a backorder (§0.11's question) · `wh_shipments:dispatch` · `:confirm_delivery` · `:cancel` (FR-449 de-stage) | DELIVERED, CANCELLED |
| `wh_shipments` | OPEN · LOADED · DISPATCHED · DELIVERED · CANCELLED | `:dispatch` · `:confirm_delivery` · `:cancel` only before DISPATCHED | DELIVERED, CANCELLED |
| `wh_return_receipts` | RECEIVED · POSTED · DISPOSITIONED · REVERSED | `:post` · `:disposition` (scrap needs an approver) · `:reverse` before disposition | DISPOSITIONED, REVERSED |
| `wh_rmas` | OPEN · APPROVED · MATCHED · EXPIRED · CANCELLED | `:approve` · `:match` · expiry job (RJ-012) | MATCHED, EXPIRED, CANCELLED |
| `wh_replenishment_suggestions` | PROPOSED · ACCEPTED · REJECTED · CONVERTED | `:accept` → PO/transfer (`resulting_document_*`) · `:reject` (reason) | CONVERTED, REJECTED |
| `whb_warehouse_branches` (RJ-001) | role REGISTERED / SERVING, effective-dated | a REGISTERED change is end-date plus insert, never an update | — |

**Ratify with `/functional-contract`** before building from any row in this appendix.
