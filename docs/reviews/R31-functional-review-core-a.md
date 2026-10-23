**Summary.** The audit found 21 defects: 2 High, 11 Medium and 8 Low. I did not write `docs/reviews/R31-functional-review-core-a.md`, because this reviewer role may not write report files. The full report is below and can be saved to that path as it stands.

Top 5:
1. **F-CA-001 (High):** the stock-transfer ladder leaves a `DRAFT` with no way forward and adds an Allocate step the code does not have. Its divergence table says "none found", which is false.
2. **F-CA-005 (High):** five actions name a different permission from the one the code checks. Two of them are weaker in the code than in the contract (Seal, Assign).
3. **F-CA-002:** the location contract says Block sets `COUNTING`/`FROZEN` and has no Unblock action.
4. **F-CA-020:** a withdrawn dealer error code, `CROSS_GSTIN_COUNTER_SALE`, is kept "for the wire", but no code uses it.
5. **F-CA-007:** divergence row 1 of `movement-post-reverse` §11 is out of date since migration `V501105`.

---

# Functional conformance — R30 CP-FR-007 core contracts (R31 core-a)
Contract: 12 contracts in `warehouse-issues/docs/contracts/` (all `v0 — 2026-10-23`, not ratified) | Mode: audit
Files reviewed: 12 contracts in full (movement-post-reverse §10–11 and receipt-qc-putaway §10–13 in full, the rest read selectively), FRD §6.1–6.12 and §6.23, BUILD-SPEC-SCREENS WS-090 / WS-092 / the §0 error register, DECISIONS D-16 / D-17, R28 RN-024, the owning `issues/*.md` "Functional contracts:" lines, and about 60 code and migration files in `classic/warehouse*` (spot-checks, listed inline) | File set: derived from the workflows
Engines: Claude + GPT (gpt-6.1-sol, medium) — 3 both · 8 Claude only · 10 GPT only · 0 dropped

Paths starting `docs/` or `issues/` are in `warehouse-issues`. All other paths are in `classic`.

## Verdict
21 findings: High 2 · Medium 11 · Low 8.

Things that are clean:
- **FR coverage.** Every active FR in §6.1–6.12 and §6.23 is cited by a rule row in at least one contract. The only FRs with no rule row are the WITHDRAWN and DEFERRED ones.
- **Design-set checker.** `tools/check-design-set.py` reports "0 violations across 15 checks".
- **Task links.** Every owning task named in the contracts' §0 carries a `**Functional contracts:**` line that names the contract.
- **Error codes.** Every refusal code cited in a guard row exists as a string in the code, except `LOT_NOT_ISSUABLE` (F-CA-011) and `CROSS_GSTIN_COUNTER_SALE` (F-CA-020).

## Status reachability (rows with a defect only)
| Status | In CHECK / ladder | In contract T1 | Inbound | Outbound | UI reachable | Verdict |
|---|---|---|---|---|---|---|
| Transfer `DRAFT` | `V510031:50-58` | yes | `STR-T1-01` | contract: Cancel only. Code: Approve / Allocate | yes | contract dead-end (F-CA-001) |
| Transfer `APPROVED` | ladder | yes | Approve | code goes on to `ALLOCATED` in the same request | no separate step | contract adds a step that does not exist (F-CA-001) |
| Location `BLOCKED` / `DAMAGED` | `V500013:132` | yes | Block | contract: none. Code: `/unblock` | yes | contract dead-end (F-CA-002) |
| Location `COUNTING` / `FROZEN` | `V500013:132` | via Block | contract: Block. Code: count freeze | count post / cancel | n/a | wrong actor (F-CA-002) |
| LPN `SHIPPED` / `CONSUMED` | `V500018:290` | no | dispatch / none | terminal | indirectly | not in the contract (F-CA-003) |
| Wave `PICKING`…`SHIPPED`, `CANCELLED` | `V510100:119-121` | listed | none in the contract (code: DB roll-up, `wh_waves:cancel`) | — | — | no inbound transition in the contract (F-CA-004) |

## Findings

### F-CA-001 — High — Unreachable state: the stock-transfer ladder strands `DRAFT`, adds an Allocate step the code does not have, and says no divergence exists
- Contract:row: `stock-transfer` §1.1, `STR-T1-03`, `-05`, `-09`, `STR-T2-02`, §8 "none found"
- Engines: Both
- Evidence: `docs/contracts/stock-transfer.contract.md:52` allows Approve only from `REQUESTED`, `:54` allows Allocate only from `APPROVED`, and `:135` claims "none found". The code ladder at `warehouse/backend/src/main/resources/db/migration/V510031__Create_wh_transfer_orders_and_lines.sql:52-54` is `REQUESTED | DRAFT -> APPROVED` and `DRAFT | APPROVED -> ALLOCATED`. Approve then raises and allocates the demand order in the same request (`WhTransferOrderService.java:329-330` → `raiseDemandOrder` sets `ALLOCATED`, around line 733). Allocate is only for a `DRAFT` that needs no approval (`WhTransferOrderValidationService.java:197-206`). Write-off is also allowed from `RECEIVED` (`:221-224`), but `STR-T1-09` omits it. `issues/p2-02.md:102`, `:176` and BUILD-SPEC-SCREENS WS-090 ("Approval creates the `TRANSFER` demand order") agree with the code.
- What a user experiences: under the contract, a source-created draft can only be cancelled, and an approved transfer waits for an Allocate action that the code refuses.
- Fix: rewrite `STR-T1-03` and `-05` as the two DRAFT branches plus approve → `APPROVED` → `ALLOCATED` in one request. Add `RECEIVED` to `STR-T1-09`. Replace the "none found" row.

### F-CA-002 — Medium — Dead-end and wrong actor: the location status ladder does not match the code
- Contract:row: `facility-branch-link` `FBL-T1-06`, `FBL-T2-02`, §1.1
- Engines: Claude
- Evidence: `docs/contracts/facility-branch-link.contract.md:59` says Block sets `BLOCKED` / `COUNTING` / `DAMAGED` / `FROZEN` from `AVAILABLE`, and no transition leaves those states. In the code, `/block` and `/unblock` (`WhbLocationController.java:320-337`, both `whb_locations:block`) cover only `BLOCKED` / `DAMAGED`. `WhbLocationService.java:399` says "Unblock: BLOCKED or DAMAGED back to AVAILABLE … COUNTING / FROZEN are never cleared here". `COUNTING` / `FROZEN` are set by the count freeze (`cycle-count` `CCT-T4-04`).
- What a user experiences: a blocked bin has no documented way back to `AVAILABLE`, and a builder could put count statuses on the Block action.
- Fix: limit `FBL-T1-06` to `BLOCKED` / `DAMAGED`, add an Unblock row, and point `COUNTING` / `FROZEN` at `CCT-T4-04`.

### F-CA-003 — Medium — Unreachable state: the LPN inventory leaves out two states the database allows
- Contract:row: `lot-serial-status` §1.1, `LSS-T4-03`
- Engines: GPT (verified)
- Evidence: `docs/contracts/lot-serial-status.contract.md:48` lists only open / closed. `V500018__…:290` allows `OPEN`, `CLOSED`, `SHIPPED`, `CONSUMED`. `WhbLpn.java:46` says shipment dispatch writes `SHIPPED` and "CONSUMED has no writer". `WhCartonService.java:565` sets `SHIPPED`.
- What a user experiences: shipped plates go into a state the contract does not describe, and `CONSUMED` is offered but nothing produces it.
- Fix: add `SHIPPED` with its dispatch effect. Mark `CONSUMED` as unreachable or deferred.

### F-CA-004 — Low — No inbound transition: wave statuses after `RELEASED`, and wave cancel
- Contract:row: `outbound-despatch` §1.1 Wave, `ODS-T1-10`, `-11`
- Engines: Claude
- Evidence: `docs/contracts/outbound-despatch.contract.md:46` lists `PICKING`…`SHIPPED` and `CANCELLED`, but only Create and Release have rows. The column comment at `V510100__…:119-121` says these are "rolled up from the member orders and pick tasks by wh_waves_roll_up()". The permission `wh_waves:cancel` exists in the code.
- Fix: add a roll-up row (a system effect) and a Cancel row with its guard.

### F-CA-005 — High — Actor mismatch: five actions name a different permission from the code, with no divergence rows
- Contract:row: `facility-branch-link` `FBL-T1-10`, `FBL-T2-03`, §0 permission list · `outbound-despatch` `ODS-T1-14`, `-17` · `task-execution-printing` `TEP-T1-02`
- Engines: Both (Reject) · GPT (the rest, verified)
- Evidence:
  - **Reject.** The contract uses `:approve` (`facility-branch-link.contract.md:63`, `:102`), but the code requires `wh_transfer_orders:reject` (`WhTransferOrderController.java:335`, "Its OWN verb, not :approve"). BUILD-SPEC-SCREENS WS-090 and `STR-T1-04` say `:reject`. The §0 resource list also leaves out `reject`, `report_variance` and `write_off_transit`.
  - **Seal, weaker than the contract.** The contract names `wh_cartons:seal`, but the pack-session `seal-carton` action needs only `wh_pack_sessions:create` (`WhPackSessionController.java:257-258`).
  - **Load.** The contract names `wh_shipments:edit`, but the code requires `:dispatch` (`WhShipmentController.java:262-263`).
  - **Assign, weaker than the contract.** The contract names `whb_tasks:assign`, but `/assign` requires `whb_tasks:edit` (`WhbTaskController.java:204-205`).
- What a user experiences: the contract predicts the wrong grant or refusal. Pack-session sealing and task assignment are reachable without the specific permission the contract names.
- Fix: correct each actor cell to the built permission, or record a divergence and send the permission decision to the owning task.

### F-CA-006 — Medium — Actor mismatch: the approval-policy permission does not exist
- Contract:row: `cycle-count` `CCT-T2-02`
- Engines: Claude
- Evidence: `docs/contracts/cycle-count.contract.md:125` names `wh_stock_adjustments:manage`. No such authority exists. The code uses `wh_adjustment_approval_policies:manage` and `:view` (grep of `warehouse/backend/src/main/java` `hasAuthority`).
- Fix: change the cell to `wh_adjustment_approval_policies:{view,manage}`.

### F-CA-007 — Medium — Wrong divergence row: `movement-post-reverse` §11 row 1 is out of date since `V501105`
- Contract:row: `movement-post-reverse` `MPR-GRD-01`, `MPR-GRD-42`, §11 row 1
- Engines: Both
- Evidence: `movement-post-reverse.contract.md:524` says the code "seeds `MUST_BALANCE_PER_MOVEMENT`" and "gates mixed owners on `is_ownership_transfer`". In fact:
  - `V500003:90` defaults `balance_rule` to `MUST_BALANCE_PER_OWNER_ITEM`.
  - `MUST_BALANCE_PER_ITEM` is in use (12 hits). `MUST_BALANCE_PER_MOVEMENT` is only on the value-only types (`:225-228`).
  - `V501105` (header and `:102`) admits a two-owner movement balanced per owner and item without the flag, and `WhbMovementPostValidationService.java:1265` mirrors it.
  The real gaps are: no `UNBALANCED_ALLOWED`, no movement-type `allows_mixed_owner` flag, and the extra `PER_MOVEMENT` value. The cited line `:94` is also wrong; `balance_rule` is at `:90`.
- Fix: rewrite row 1 and the "built shape" text in `MPR-GRD-01` to match those three gaps.

### F-CA-008 — Medium — Guard drift: Move is open to `CLOSED` and nested LPNs, but the contract forbids both
- Contract:row: `lot-serial-status` `LSS-T1-05`, `LSS-GRD-06`, `LSS-T2-02`
- Engines: GPT (verified)
- Evidence: the contract allows Move only from open and defers nested-LPN operations (`:58`, `:70`, `:91`). The code has `MOVABLE_STATUSES = {OPEN, CLOSED}` (`WhbLpnMovementService.java:94-95`) and "Move the whole plate - and everything nested inside it" (`:165-166`).
- Fix: separate Move eligibility from Split / Merge eligibility, and document the nested walk and its guards.

### F-CA-009 — Medium — Time rule missing: the use-by / best-before rules are delegated to a contract that does not state them, and expiry is split across two contracts
- Contract:row: `lot-serial-status` `LSS-GRD-02`, `LSS-T3-01`, `LSS-OPEN-01` · `cycle-count` `CCT-T3-02`, `CCT-T4-08`
- Engines: GPT (use-by) + Claude (split effect)
- Evidence:
  - `LSS-OPEN-01` (`:144`) delegates the use-by / best-before rules to `outbound-despatch`, which has no such row.
  - The code treats a lot as expired on `LEAST(expiry_date, use_by_date)` (`WhbShelfLifePolicyService.java:210-214`), with a best-before fallback in `WhbShelfLife.java:28-40`.
  - `LSS-T3-01` says the job changes only `whb_lots.status_code`. `CCT-T4-08` says it posts a `STATUS_CHANGE` on positions. `WhbLotExpiryJob.java:143-144` does both.
- Fix: state the hard-date rule, the best-before fallback and the refusal code in one contract, and cite it from the other. Make `LSS-T3-01` name both effects.

### F-CA-010 — Medium — Cross-entity conflict: the mass-hold effect contradicts FR-152, and the divergence row omits it
- Contract:row: `cycle-count` `CCT-T4-07`, `CCT-DIV-04`
- Engines: GPT (verified)
- Evidence: FRD `:364` (FR-152) says each mass hold or release posts "a balanced status-change movement". `WhHoldService.java:220-225` posts "no movement, and nothing written to whb_lots". FR-096 (FRD `:283`) requires movement-free holds. `CCT-DIV-04` records only the selector difference.
- Fix: add the effect difference to `CCT-DIV-04` and raise the FR-152 vs FR-096 conflict for an FRD amendment.

### F-CA-011 — Low — Holds are specified twice with conflicting details, and the holds task does not link one of the two contracts
- Contract:row: `lot-serial-status` `LSS-T1-03`, `LSS-T4-02`, §0 · `cycle-count` `CCT-T1-20`, `CCT-GRD-12`
- Engines: Claude
- Evidence:
  - `LSS-T4-02` names the refusal `LOT_NOT_ISSUABLE`, which exists nowhere in `warehouse*/src/main`. The allocator skips held subjects through `WhbAllocationHoldGate` (`ALLOCATION_HELD`, as `CCT-GRD-12` says).
  - LSS scopes a hold to lot / item / location. The code also has `ORDER` (`WhbAllocationHoldGate.java` `SUBJECT_ORDER`).
  - LSS owns `wh_holds` and WS-092 in its §0, but `issues/p2-03.md:7` (the holds task) names only `cycle-count`.
- Fix: make `cycle-count` the single owner of holds and have LSS cite it, or align both. Drop `LOT_NOT_ISSUABLE`.

### F-CA-012 — Medium — Guards missing: item edit and conversion refusals that the code enforces
- Contract:row: `item-master` `ITM-T1-02`, `ITM-T1-06`, §1.3
- Engines: GPT (verified)
- Evidence: the code refuses:
  - an owner change: `ITEM_OWNER_IMMUTABLE` (`WhbItemValidationService.java:219`);
  - a lot / serial control-mode change while stock exists: `validateControlModesUnchanged` (`:251-256`);
  - editing or deleting a conversion a posted line has used: `CONVERSION_IN_USE` (`WhbItemUomConversionService.java:39`, `:49`).
  None of these has a contract row.
- Fix: add three guard rows with their codes.

### F-CA-013 — Low — Wrong actor: a pickup request is completed by the handover, not by its own action
- Contract:row: `outbound-despatch` `ODS-T1-22`
- Engines: GPT (verified)
- Evidence: `WhPickupRequestService.java:30-35` says the request is "COMPLETED by the hand-over … there is no Complete verb". `WhHandoverService.java:293-294` calls `completeFromHandover`.
- Fix: split Confirm (`:confirm`) from completion, and add a T4 row for handover → pickup completed.

### F-CA-014 — Low — Screen drift: wrong grid keys on the Lots and Serials screens
- Contract:row: `lot-serial-status` `LSS-T5-01`, `-02`
- Engines: GPT (verified)
- Evidence: the contract uses `statusCode` and `soldToName`. BUILD-SPEC-SCREENS (`:1515`, `:1538`) and the built tables use `lotStatus` (`WhbLotManagementTable.tsx:82`) and `soldToCounterpartyName` (`WhbSerialManagementTable.tsx:72`).
- Fix: use the canonical keys.

### F-CA-015 — Medium — Screen drift: BUILD-SPEC-SCREENS WS-090 contradicts the contract and the code, with no divergence row
- Contract:row: `stock-transfer` `STR-T5-01`, `STR-GRD-06`, `STR-UNR-05`
- Engines: Claude
- Evidence:
  - BUILD-SPEC-SCREENS WS-090 lists `transferType (BIN_TO_BIN/INTRA_SITE/INTER_SITE)`. `STR-UNR-05` says `BIN_TO_BIN` is not a transfer type (`V511246__Narrow_wh_transfer_orders_type_check_to_two_values.sql`).
  - WS-090 says Receive "is authorised … regardless of site scope". `STR-GRD-06` and the code require destination scope (`WhTransferOrderService.java:492-493`, `TRANSFER_NOT_AT_DESTINATION`).
- Fix: amend WS-090 in BUILD-SPEC-SCREENS, or record both points as divergences in `stock-transfer` §8.

### F-CA-016 — Medium — Access rule not stated: what happens when a user has no warehouse grants, or their grant expires
- Contract:row: `access-scope` `ACS-GRD-04`, §0 routes
- Engines: GPT (verified)
- Evidence: `WhbWarehouseScopeService.java:155-162`. A user with no grant rows keeps branch-derived access. A user with any grant row, whatever its dates, gets only the grants current now intersected with the branch tier. So a user whose only grant expires loses access. `issues/p1-18.md:98` and `:103` assign WS-238, which is absent from the contract.
- Fix: state both cases and add WS-238 to the routes and T5.

### F-CA-017 — Low — Requirement missing: the core counterparty contract has no FR-119 exclusion row
- Contract:row: `counterparty-master` (none)
- Engines: GPT (verified)
- Evidence: FR-119 (no payment terms, credit, bank details, contacts or scorecard on the counterparty) is cited only by `trade-counterparty-evaluation`. The core §6.7 contract's guard and unreachable tables (`:52-65`) leave it out. `issues/p1-08.md:63` carries it.
- Fix: add a `CPM-UNR` row for FR-119, with the exception for dated addresses and tax registrations.

### F-CA-018 — Low — Reservation status inventory: wrong inbound list and wrong representation
- Contract:row: `reservation-allocation` §1.1
- Engines: GPT (inbound list) + Claude (representation)
- Evidence: `RELEASED` lists `RSA-T1-04` as an inbound transition, but that row is `OPEN/SOFT → OPEN/HARD` (`:39` against `:50`; `WhbAllocationService.java:847`). The column "Represented by `status`" is also wrong: `V500033:44` says "status is NOT stored", and OPEN / RELEASED / CONSUMED are derived from `released_at` and `consumed_by_movement_line_id`.
- Fix: remove `-04` from the inbound list and correct the representation column.

### F-CA-019 — Low — Wrong event name
- Contract:row: `receipt-qc-putaway` `RQP-T4-21`
- Engines: Claude
- Evidence: the contract names `RECEIPT_LINE_CONFIRMED`. The code uses `EVENT_RECEIPT_LINE_CONFIRMED = "receipt.line.confirmed"` (`WhGoodsReceiptPostingService.java:131`), seeded in `V500040:114`.
- Fix: use `receipt.line.confirmed`.

### F-CA-020 — Medium — D-16: a withdrawn dealer error code is adopted "for the wire" when no wire exists
- Contract:row: `facility-branch-link` `FBL-GRD-13`, §10 row 1 · task `issues/p8-10.md:67`
- Engines: Claude
- Evidence:
  - `FBL-GRD-13` and p8-10 refuse with `422 CROSS_GSTIN_COUNTER_SALE` "(code kept for the wire)".
  - The code comes from the dealer counter sale. FR-359 is WITHDRAWN by D-16 / RN-051 (FRD `:689`), and WS-194 Counter Sale is REMOVED (BUILD-SPEC-SCREENS `:3100`).
  - The string exists nowhere in `warehouse*` (grep), so no wire client depends on it.
  - BUILD-SPEC-SCREENS `:548` still describes it as "the counter-sale service … WS-194, WS-200".
- Fix: give the serving-branch refusal a neutral code (for example `CROSS_GSTIN_DIRECT_ISSUE`) in FBL, p8-10 and the BUILD-SPEC-SCREENS error register.

### F-CA-021 — Low — D-16: `RTO_RECEIPT → RTO` is stated as a live seed with no removal row
- Contract:row: `movement-post-reverse` `MPR-GRD-11`
- Engines: Claude
- Evidence: `movement-post-reverse.contract.md:112` lists `RTO_RECEIPT` → `RTO` among the seeded `reason_context` values. RTO is retail vocabulary that D-16 removes (RN-016 / RN-024). It is still seeded in `V500003:190` and `:224`. Unlike ODS-DIV-05, there is no divergence row recording that P7 removes it.
- Fix: add an §11 row for the P7 removal and mark the seed as residue.

## Dropped after verification
- None. All 13 GPT findings were confirmed at the cited `file:line`. GPT's F-CA-012 and Claude's representation point were merged into F-CA-018.

## Remediation backlog
None of these needs a migration; all are documentation fixes.

| Finding | Files to touch | Shared registries | Parity apply-to | Contract |
|---|---|---|---|---|
| F-CA-001 | `docs/contracts/stock-transfer.contract.md` | none | `facility-branch-link` FBL-T4-04 | STR-T1-03, -05, -09; §8 |
| F-CA-002 | `docs/contracts/facility-branch-link.contract.md` | none | `cycle-count` CCT-T4-04 | FBL-T1-06; new Unblock row |
| F-CA-003 | `docs/contracts/lot-serial-status.contract.md`; `issues/p1-07.md` | none | `outbound-despatch` (dispatch effect) | LSS §1.1; T4 |
| F-CA-004 | `docs/contracts/outbound-despatch.contract.md` | none | none | new wave roll-up and cancel rows |
| F-CA-005 | `facility-branch-link`, `outbound-despatch`, `task-execution-printing` contracts; `issues/p3-07.md`, `p0-10.md` if the permission policy changes | `permission_dependencies` if the policy changes | none | FBL-T1-10, T2-03, §0; ODS-T1-14, -17; TEP-T1-02 |
| F-CA-006 | `docs/contracts/cycle-count.contract.md` | none | none | CCT-T2-02 |
| F-CA-007 | `docs/contracts/movement-post-reverse.contract.md` | none | every writer consumer | MPR-GRD-01; §11 row 1 |
| F-CA-008 | `docs/contracts/lot-serial-status.contract.md` | none | `warehouse-3pl` commingled pallets | LSS-T1-05, GRD-06, T2-02 |
| F-CA-009 | `lot-serial-status` and `cycle-count` contracts | none | `outbound-despatch` | LSS-T3-01, OPEN-01; CCT-T3-02 |
| F-CA-010 | `docs/contracts/cycle-count.contract.md`; FRD FR-152 | none | none | CCT-T4-07, DIV-04 |
| F-CA-011 | `lot-serial-status` and `cycle-count` contracts; `issues/p2-03.md` | none | none | LSS-T4-02; CCT-GRD-12 |
| F-CA-012 | `docs/contracts/item-master.contract.md` | none | none | new ITM-GRD rows |
| F-CA-013 | `docs/contracts/outbound-despatch.contract.md` | none | none | ODS-T1-22; new T4 row |
| F-CA-014 | `docs/contracts/lot-serial-status.contract.md` | none | none | LSS-T5-01, -02 |
| F-CA-015 | `docs/BUILD-SPEC-SCREENS.md` WS-090, or `stock-transfer` §8 | none | none | STR-T5-01 |
| F-CA-016 | `docs/contracts/access-scope.contract.md` | none | `warehouse-3pl`, `warehouse-india` (they use the same resolver) | ACS-GRD-04; WS-238 |
| F-CA-017 | `docs/contracts/counterparty-master.contract.md` | none | none | new CPM-UNR row |
| F-CA-018 | `docs/contracts/reservation-allocation.contract.md` | none | none | §1.1 |
| F-CA-019 | `docs/contracts/receipt-qc-putaway.contract.md` | none | none | RQP-T4-21 |
| F-CA-020 | `facility-branch-link` contract; `issues/p8-10.md`; `docs/BUILD-SPEC-SCREENS.md:548` | error register | none | FBL-GRD-13 |
| F-CA-021 | `docs/contracts/movement-post-reverse.contract.md` | none | P7 tasks | new §11 row |

## Parity (C10)
- **Mobile:** none. D-17 item 2 and D-16 item 7 defer mobile, so it is not a finding.
- **Siblings sharing these rules:** `warehouse-base`, `warehouse`, `warehouse-3pl` (uses the LPN, owner and grant rules) and `warehouse-india`. The dealer, automotive and accessories modules are outside this scope (D-16 RN-054).

## Contract quality
- Code conformance was spot-checked by grep and targeted reads, not by a whole-file walk of every controller, export, modal and locale. Paths I did not read are not claimed as conformant.
- I checked BUILD-SPEC-SCREENS against T5 for WS-090 and WS-092 only, plus GPT's check of WS-036 and WS-037.

## Referred to standards reviewer
- None.