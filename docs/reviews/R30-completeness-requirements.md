# R30 — Completeness audit, part FR: requirements → task → functional contract

**Date** 2026-10-23 · **Mode** read-only (this file is the only write; nothing committed) · **Base** `main`
**Read first:** `DECISIONS.md` D-16, `reviews/RETARGET-PROGRAM-STATUS.md`.
**Inputs:** `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` (FR-001…471), `frd/FRD-{REM,STORES,TRADE,MFG}.md`
(FR-480…669), `IMPLEMENTATION-PLAN.md` §2 (`Closes` column, lines 415–730), `issues/p*.md`, the 28
`contracts/*.contract.md`, `SCENARIO-CATALOGUE.md` + the four area scenario sections, and
`classic/.claude/agents/functional-reviewer.md` (a contract must carry T1 state machine, guards, T3 time
rules, T4 cross-entity effects, T5 screen contract).

**Method.** Every `| **FR-nnn** |` row was parsed (id, module, withdrawn flag). Carrier = plan §2 `Closes`
(the authority, `IMPLEMENTATION-PLAN.md:432`), cross-checked against each task file's `## Closes`
section. Task state = header note (`> **VOID**`, `> **PARTIALLY VOID**`, `> **SUPERSEDED**`). Contract
coverage = an FR cited on a contract line, tagged by section; a citation only in §0 *Identity*, *Out of
scope*, *Amendments*, *Open/Resolved rows* or *Invariants and scenarios* is **weak** (names the FR, gives
the reviewer no rule to check). Scenarios = any `WH-SC` row whose FR column cites it. Ranges
(`FR-622…629`, `FR-556–561`) were expanded. Scripts are not committed.

---

## 1. Summary counts

| Measure | Count |
|---|---|
| FR ids that exist | **661** (FR-001…471 = 471; FR-480…669 = 190). **FR-472…479 do not exist** (CP-FR-006) — the brief's "669" is the top id, not the count |
| Withdrawn (`WITHDRAWN by D-16`) | **23** (all in the main FRD) |
| Active | **638** |
| Active, no plan owner | **0** |
| Active, more than one plan owner | **0** · a second closer in a task file's `## Closes`: **1** real (FR-312), 1 borderline (FR-326) |
| Active, owner task fully **VOID** | **9** (CP-FR-001) · owner **SUPERSEDED**: **1** (FR-268, CP-FR-002) |
| Active, **no contract** citation | **377** (59 %) — 357 of the 471 base FRs, 20 REM, 5 other area FRs |
| Active, **weak** contract citation only | **81** — 69 of them TRADE (CP-FR-008) |
| Active, rule-level contract citation | **180** |
| Active, **no scenario** | **65** |
| Withdrawn FR still referenced by a live / partially-void task (unmarked) | **7 FRs in 9 tasks** (FR-201, 205, 208, 368–370, 422; CP-FR-003, -004) · still owned in plan §2 Closes: **22 of 23** · cited by a **live** scenario: **7** FRs / 8 scenarios (CP-FR-003, -012) |
| Contract rule rows parsed (ID-keyed rows) | 1,707 · guard/transition/T3/T4/UNR rows 1,307 · rows naming no FR and no decision id: 1,030 |
| Trade contracts with a `Source` column on any guard/transition table | **0 of 10** |
| Active FRs with unflagged dealer/retail wording | **14** (+ 5 live dealer/retail scenarios) (CP-FR-012) |
| R29 dispositions spot-checked | **60** of 191 (REM 17/17, STORES 12, TRADE 17, MFG 14): **60 present**, 2 with a wrong / wildcard pointer |
| Decision / WS ids cited by no task **and** no contract | 8 (REM-D8, REM-D18, REM-D19, STO-D18, TRD-07, TRD-14, and the reserved WS-338/339) |
| `tools/check-design-set.py` | **0 violations across 13 checks**; 97 advisory version citations |

Verdict legend used in the matrix (§4): `OK` · `NC` no contract · `WC` weak contract only · `NS` no scenario ·
`VOID-OWNER` · `SUPERSEDED-OWNER` · `2ND-CLOSER` · `WD` withdrawn · `WD·REF <tasks>` withdrawn but still
mentioned by a non-VOID task.

---

## 2. Findings

### CP-FR-001 · BLOCKER · Nine active FRs are owned only by fully VOID tasks — nothing will build them, and the checker passes
| FR | Line | Owner (VOID) | What it is | Proposed disposition |
|---|---|---|---|---|
| FR-072 | `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:241` | p2-24 | supersession stock/demand treatment | **Re-home** — D-16 item 3 keeps *"item supersessions … as engineering change"* (`DECISIONS.md` D-16 §3). Carrier: p1-02/p1-03 (item master) or a P8 task |
| FR-073 | `:242` | p2-24 | interchange/alternates + availability by `REGISTERED` branch | Re-home with FR-072; drop the "counter enquiry" wording |
| FR-277 | `:540` | p5-15 | cores are inventory | **Withdraw** (dealer parts; p5-15 VOID) |
| FR-278 | `:541` | p5-15 | warranty scrap-and-hold | Withdraw, or restate for plant warranty returns to supplier and re-home to P8-15 |
| FR-352 | `:674` | p2-25 | "two adapters ship in v1" | **Restate** — only `warehouse-adapter-example` survives (D-16 item 2/D-1 amendment); re-home to P0-14 or withdraw |
| FR-361 | `:683` | p2-26 | parts issued to open jobs are WIP | Withdraw; the plant equivalent is FR-654 / `mfg-costing-close` |
| FR-362 | `:684` | p2-26 | serial fitted to a customer's vehicle | Withdraw (dealer) |
| FR-421 | `:774` | p6-11 | accessories-absorption path | Withdraw (accessories coexistence removed, `RN-023`) |
| FR-461 | `:861` | p2-25 | **serving-branch tax rule** (generic) | **Re-home** — it is D-14 core behaviour; p2-02, p2-08, p2in-03 already cite it. Carrier: P2-02 or P1-05 |

D-16 item 9 withdrew none of these. `check-10` passes because it never reads the VOID header (§7).

### CP-FR-002 · MAJOR · FR-268 is active, contradicts D-16, and its owner is SUPERSEDED
`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:519` says *"Multi-level BOM with routings is not built"*; `RN-032` reverses
that and FR-622…631 build BOM, work centres and operations. Owner `issues/p6-12.md:5` carries a third marker,
**SUPERSEDED**, which no checker or convention knows; `issues/p10-03.md:11` calls the same file **VOID**. The
p6-12 note also says *"Routings / work centres remain out of scope unless FRD-MFG says otherwise"*, while FR-630/631
put work centres and operations in scope. **Fix:** mark FR-268 `WITHDRAWN by D-16 (RN-032) — superseded by FR-622…631`;
use one marker word (VOID) in p6-12; reword its routing sentence.

### CP-FR-003 · MAJOR · Withdrawn FR-422 (performance targets) is still built and asserted by five live tasks
FR-422 is withdrawn (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:780`); FR-534 replaces it (`frd/FRD-STORES.md:226`).
It is still owned by live **P0-16** (`IMPLEMENTATION-PLAN.md:462`; `issues/p0-16.md:24-30,53,127`) and its numbers
are acceptance tests in `issues/p0-03.md:84,256` (200 lines/s), `p2-13.md:110,187` (10 counters),
`p3-01.md:25` and `p3-06.md:65`. Live scenarios `WH-SC-193` (`SCENARIO-CATALOGUE.md:426`), `-197` (`:430`),
`-228` (`:488`) and `-256` (`:526`) still cite it. **Fix:** move these numbers to FR-534 (or restate them in
FR-534 for plant stores), change P0-16's Closes to FR-534 (or record P0-16 → P8 follow-on), and re-cite the
four scenarios.

### CP-FR-004 · MAJOR · Withdrawn FRs are still listed as owned, unmarked, in plan §2 and in task Closes sections
Plan §2 `Closes` assigns 22 of the 23 withdrawn FRs with no marker, among them live or partially-void rows
P0-16 `FR-422` (`:462`), P1-04 `FR-368` (`:474`), P2-12 `FR-205` (`:511`), P3-18 `FR-419` (`:564`),
P5-08 `FR-464` (`:605`), P5-09 `FR-208…210` (`:606`), P5-11 `FR-200…202` (`:608`) and P5-13 `FR-276 FR-279` (`:610`).
In the task files themselves: `issues/p1-04.md:99` Closes `FR-368`, with sections *Mitigation 1/2* (`:47`, `:54`)
still specifying FR-368–370; `issues/p2-12.md:59,148` (`FR-205`, "the v1 columns"); `issues/p5-11.md:49`
(`FR-201` unmarked). **Fix:** suffix each with *(withdrawn D-16)* in §2 and in the task Closes; strike the
p1-04 mitigation sections; teach check-10 to treat withdrawn FRs as owned-by-none (§7).

### CP-FR-005 · MAJOR · D-16 withdraws 9 FRs; the FRD withdraws 23
`DECISIONS.md:527` (D-16 item 9) lists FR-074, 279, 358, 359, 360, 365, 419, 420, 422. The FRD header
(`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:28-29`) and the rows withdraw 14 more: FR-200–205, 208–210, 276,
368–370, 464. Those 14 withdrawals have no decision of record. **Fix:** amend D-16 item 9 (or R28 §8b) to
list all 23.

### CP-FR-006 · MINOR · FR-472…FR-479 were never allocated, which breaks the FRD's own numbering rule
`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:79` says ids run *"Contiguous from FR-001 … never reserved as a gap"*.
The main catalogue ends at FR-471 (`:916`), and D-16 item 8 (`DECISIONS.md` D-16 §8) starts REM at FR-480. No file
mentions 472–479. **Fix:** state the gap once (D-16 item 8 and FRD §7): *"FR-472…479 unallocated, never used"*.

### CP-FR-007 · MAJOR · 377 active FRs have no contract, so the functional reviewer cannot verify them
Grouped by workflow (FRD section), with the proposed carrier. Contract-shaped behaviour means a state machine, a
cross-entity guard, a time rule or an irreversible effect (`contracts/README.md` "When to write one").

| # | Workflow (FRD §) | Uncovered FRs | Owner tasks | Proposal |
|---|---|---|---|---|
| 1 | 6.1 ledger · 6.2 port | 006 012 018 021–024 026 030 031 · 042 043 046 047 | p0-02 p0-03 p0-04 p0-08 p6-01 | **extend `movement-post-reverse`** (T1/T4 rows; FR-042–047 belong in its port section) |
| 2 | 6.3 items, UoM, identification, packaging | 048–067 069–073 075–078 (29) | p1-01–p1-04 p3-10 p3-15 | **NEW `item-master.contract.md`**: item lifecycle, UoM conversion guards, supersession as engineering change (re-homed FR-072/073) |
| 3 | 6.4 identity and facility; 6.28 branch links | 079–083 086 088–093 · 460 461 462 465 | p1-05 p1-06 p2-02 p2-23 | **NEW `facility-branch-link.contract.md`**: D-14 dated links, one `REGISTERED` at every instant, serving-branch rule, transfer request ladder (FR-462), inter-company (FR-465) |
| 4 | 6.5 lots, serials, LPN, status, duty | 094–097 099–101 104 105 · 452–454 | p1-07 p2-05 p3-15 | **NEW `lot-serial-status.contract.md`** (expiry/retest/hold clocks = T3; status change = T4) |
| 5 | 6.6 owner of goods | 107–111 113–115 | p0-06 p5-08 | extend `movement-post-reverse` (owner segregation guard) |
| 6 | 6.7 counterparties · 455 | 116–118 121 455 | p1-08 p6-06 | extend `trade-counterparty-evaluation` §1 with the core master rows, or NEW `counterparty-master` |
| 7 | 6.8 inbound | 125 126 136 140 | p1-12 p1-13 p3-05 p5-10 | extend `receipt-qc-putaway` |
| 8 | 6.9 inventory control (count, adjust, transfer) · 463 | 145–149 151–163 165 463 (20) | p0-13 p2-01–p2-06 p3-14 | **NEW `cycle-count.contract.md`** + **NEW `stock-transfer.contract.md`** — the README names both (count lifecycle, transfer legs, in-transit ageing) as contract-required |
| 9 | 6.10 reservations | 166 167 169–173 175 176 | p0-03 p0-09 p2-07 | **NEW `reservation-allocation.contract.md`** (expiry = T3; README lists it) |
| 10 | 6.11 outbound · 447 449 467 | 177–194 196–199 206 207 · 447 449 467 (27) | p1-11 p2-08–p2-11 p3-06–p3-09 p3-13 p5-10 p5-11 | **NEW `outbound-despatch.contract.md`** (demand order → wave → pick → pack → ship → confirm delivery; edit-after-release matrix FR-183) |
| 11 | 6.12 execution, scanning, printing | 212–217 219–229 | p0-10 p2-14 p3-01–p3-03 p5-17 p5-21 p6-03 p6-04 | **NEW `task-execution-printing.contract.md`**; first settle the mobile scope (CP-FR-013) |
| 12 | 6.13 valuation | 230 234–241 243 245 250 | p0-12 p2-16 p2-17 p4-11 p5-16 | **NEW `costing-valuation.contract.md`** (cost layers, period close, revaluation); `accounting-handover` covers only the handover |
| 13 | 6.14 replenishment | 252–260 | p1-03 p2-15 p3-12 p5-18 p6-02 | **NEW `replenishment.contract.md`**; link `po-schedule-port` §8b (FR-528 MRP suggestions) |
| 14 | 6.15 kitting / VAS | 261–267 | p3-11 p5-19 | **NEW `vas-work-order.contract.md`** (MFG cites its posting shape, `WhWorkOrderPostingService`) |
| 15 | 6.16 returns · 459 | 269–275 280 · 459 | p0-05 p2-12 p5-13 p5-14 p5-23 | **NEW `returns-rma.contract.md`** (core RMA + return grading; `trade-sales-return-authorisation` covers only trade's side); the supplier claim register FR-459 joins it |
| 16 | 6.17 3PL | 281–303 (23) | p2-28 p4-10 p5-01–p5-08 p6-07 | **NEW `3pl-billing.contract.md`** (billing run freeze, storage anniversaries — README lists both) |
| 17 | 6.18 India | 304–312 314–329 (25) | p2in-01–04 p4-01–p4-09 | **NEW `india-movement-documents.contract.md`** (e-way lifecycle, job-work return window); align with `mfg-subcontracting` |
| 18 | 6.19 events, outbox, logistics seam · 458 | 330–348 · 458 | p0-11 p0-15 p1-11 p1-17 p2-28 p3-22 p6-08 | **NEW `outbox-events.contract.md`** (delivery, retry, dead-letter; API clients FR-458) |
| 19 | 6.20 adapters | 349 351 353–356 363 364 366 367 371–374 (+ void 352 361 362) | p0-01 p0-04 p0-14 p3-20 p3-21 | after CP-FR-001, **NEW `module-contract.contract.md`** against `warehouse-adapter-example`, or a declared *no contract: architecture tests* line in the epic |
| 20 | 6.21 registries · 469 | 375–379 381 382 469 | p0-01 p0-04 p0-16 p1-19 | extend `movement-post-reverse` §0, or declare *architecture tests* |
| 21 | 6.22 reports/KPIs · 470 471 | 384–394 396 397 399 470 471 | p2-20 p2-21 p3-17 p6-10 | screen-only. A T5-only contract (`reports-kpis`) or an explicit exemption |
| 22 | 6.23 permissions · 466 | 401–407 409 410 466 | p0-06 p0-13 p0-15 p1-18 | **NEW `access-scope.contract.md`** (branch scope, maker ≠ checker, approval levels FR-466) |
| 23 | 6.24 import / go-live | 411–418 (421 → CP-FR-001) | p1-10 p2-19 p3-18 | **NEW `import-go-live.contract.md`** (opening balance posting is irreversible) |
| 24 | 6.25 non-functional · 6.26 variants · 456 457 468 | 423–435 437 438 440–442 · 443–445 · 456 457 468 | many | Non-functional: no contract; carry to ci-gate / perf tags. FR-443–445 (style/variant, size/colour) and 456/457 (regulated goods, Schedule H1): **decide segment scope first** (CP-FR-012) |
| 25 | REM removal | 480–499 (20) | p7-02–p7-11 p7-13 | **NEW `rem-removal.contract.md`** with UNR rows only, one per absence (`WH-SC-660…679` already exist). The reviewer has nothing to run "must not exist" against today |
| 26 | Area leftovers | 539 (stores registers) · 540 (trade module) · 615 617 618 (trade print, permissions, concurrency) | p8-13 p9-01 p9-07 p9-14 | 539 → `store-issue-return` §5.4 (WS-277 is already there); 615/617/618 → T5/T2 rows in each trade contract; 540 → scenario-only (WH-SC-480/481) |

### CP-FR-008 · MAJOR · Trade contracts cite their FRs only in §0, so no trade rule traces to a requirement
69 TRADE FRs (FR-542–614 less those cited in rule rows) appear only in a contract's §0 *Domain baseline* range,
e.g. `trade-purchase-order.contract.md:27` "FRD-TRADE FR-575…FR-589". None of the 10 trade contracts has a
`Source` column on any T1/guard/T3/T4 table (e.g. `trade-purchase-order.contract.md:100,125,146`): 395
guard/transition/time/effect rows, of which at most 5 per contract name an FR. Every STORES and MFG contract has
the column (e.g. `store-issue-return.contract.md:70`). The reviewer cannot tell which rule proves which FR, so an
FR with no rule cannot be detected. Also weak-only: FR-007, 011, 045, 084, 150 (MPR §7/§9), 122, 137, 142,
174, 195, 218, 251, 450, 510, 515, 518, 519, 621, 669. **Fix:** add a `Source` column to every trade
guard/transition/T3/T4 table, filled from FRD-TRADE §4; then any FR left uncited is a contract gap.

### CP-FR-009 · MINOR · Contract rules with no FR, and error codes that are not ratified
- Guards whose `Source` cell is `—`: `PRO-GRD-21` (`mfg-production-order.contract.md:126`), `PRC-GRD-18`
  (`mfg-production-receipt.contract.md:110`), `PRC-UNR-06` (`:130`). All are concurrency rules. MFG has no
  concurrency FR (trade has FR-618). **Fix:** add an MFG concurrency clause (FR-620 or a new row in the MFG
  range) and cite it.
- 20 refusal codes are marked *(proposed)*: 14 in `mfg-production-order`, 6 in `mfg-production-receipt` (e.g.
  `PRO-GRD-23` `409 RELEASE_PENDING_APPROVAL *(proposed)*`, `:128`). The reviewer checks exact codes, so each one
  must be ratified or dropped before P10 starts.
- 1,030 of 1,707 ID-keyed rows cite neither an FR nor a decision. Most are T2 permission rows and T5 screen rows,
  which need no source. The real gap is the trade tables in CP-FR-008.
- Tasks cite no rule ids in `mfg-bom`, `mfg-production-receipt` or `mfg-subcontracting` (0 rule ids cited);
  `mfg-production-order` (1/84), `mfg-costing-close` (1/52) and `accounting-handover` (2/89) are close to it. Every
  contract is linked by at least one task file, so this is a traceability weakness, not an orphan.

### CP-FR-010 · MINOR · FR-312 has a second closer
`issues/p10-10.md:85-86` `## Closes` lists `FR-312` (processed-form return), which plan §2 assigns to P4-02. The
same pattern, weaker, is `issues/p4-12.md:70` → FR-326 (owner P2-IN-02). **Fix:** move both under a
*Consumes / honours* line.

### CP-FR-011 · MINOR · 65 active FRs have no scenario
001–471 range: 023 121 136 142 192 194 197 207 211 229 250 258 268 301–303 317 322–325 329 334 347 348 364 366
397 399 414 415 424 441 447–450 452–455 470 471 (plus the void-owned 277 278 421). Area range: 501 518 534 543
555 584 620–622 624 630–632 636 638 650 657 662 669. FRD-MFG §13 itself records *"— (none; operations are
exercised by 637 and 659)"* for FR-630/631. **Fix:** add one scenario per area FR (MFG `WH-SC-600…659` has spare
ids, STORES up to 479, TRADE up to 599). Base FRs: fold into the new contracts' §8.

### CP-FR-012 · MAJOR · Dealer/retail wording left in active FRs and live scenarios with no D-16 note
| Where | Residue | Proposed |
|---|---|---|
| FR-165 `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:369` | "core return deadline, warranty hold … RTO ageing, COD ageing" | drop the four; add "MRN pending age, gate-pass return due" |
| FR-183 `:397` | "the answer is a return or an RTO" | "a return" |
| FR-194 `:408`, FR-197 `:411` | "AWB list", "unused AWB … void call" | "consignment / tracking number"; the AWB-void rationale goes with FR-480 |
| FR-418 `:771` | "vehicle applications" import (fitment FR-074 is withdrawn) | delete |
| FR-447 `:833` | "an NDR has nothing to be an exception to" | "a delivery exception" |
| FR-459 `:845` | "for a dealership it is the OEM claim book" | delete the sentence |
| FR-347 `:654` | "dealer PDI vehicle movements" as a GPS model | keep as history, mark *(dealer module, out of scope D-16)* |
| FR-037 `:197`, FR-161 `:365`, FR-184 `:398`, FR-468 `:868` | "channel adapter", "counterparty → channel → item", "per channel" | B2B channel only (D-16 §2); say so, or use "customer / ship-to" |
| FR-443–445 `:814-816` | style/variant axes, size runs, assortment packs (apparel retail) | segment decision: keep for plant stores or withdraw |
| FR-456/457 `:842-843` | regulated-goods licence, Schedule H1 register (pharma) | `S-035` segment decision is still unowned (`DECISIONS.md` §3) |
| WH-SC-293 `SCENARIO-CATALOGUE.md:588`, WH-SC-303 `:612` | accessories dual inventory (FR-368–370 withdrawn) | mark WITHDRAWN |
| WH-SC-321 `:642` | trade-customer portal user (FR-464 withdrawn) | mark WITHDRAWN |
| WH-SC-331 `:670` | "`warehouse-adapter-dealer` installed", `whad_item_prices` | mark WITHDRAWN |
| WH-SC-309 `:630` | "counter clerk … sells" (FR-461) | restate as a store issue / despatch from a shared site |

FR-260 (`VOR` → line-stop), FR-270 (RTO/marketplace seed removed), FR-199 and FR-207 already carry the D-16 note
and are correct. The REM FRs FR-480–499 use the terms to name what is removed, which is correct.

### CP-FR-013 · MAJOR · Twelve active FRs are mobile, but D-16 item 7 says no mobile
FR-047, 192, 217–222, 382, 424, 430, 431 carry `mobile` in their module column. They are owned by live P3-01
(`mobile`), P3-04 (`mobile+app`) and P3-07 (`app+mobile`). D-16 item 7 (`DECISIONS.md` D-16 §7) and the user rule
of 2026-09-11 say warehouse ships no mobile app. **Fix:** mark the mobile half of each FR *deferred (D-16 §7)*,
or mark P3-01 VOID, and state the web scanning fallback.

### CP-FR-014 · MINOR · Decision ids not carried into the task or contract that needs them
| Id | Defined | Gap | Fix |
|---|---|---|---|
| **REM-D19** | `frd/FRD-REM.md:79` | The two allowed grep-gate exceptions (`V500200:75` `'ACCESSORIES'`, band-ratchet file) appear in **no** P7 task, and `issues/p7-13.md:54` says a gate failure is fixed *"never by an allowlist"*. P7-13 runs the full gate set (`:29`), so an executor who reads only the task fails the gate | name both exceptions in p7-13 acceptance |
| REM-D8 | `FRD-REM.md:68` | i18n-delete waiver not cited by id; only p7-02/p7-04 restate it | cite `REM-D8` in every removing task (p7-03, -05, -07, -09, -11 mention i18n but not the waiver) |
| REM-D18 | `FRD-REM.md:78` | content is in p7-13; id not cited | cite |
| STO-D18 | `FRD-STORES.md:357` | content is in p8-09/p8-10, MRQ and SIR; id never cited | cite in `SIR-T4-01`, `MRQ-T4-01` |
| TRD-07 · TRD-14 | `FRD-TRADE.md:571,578` | content is in p9-01/p9-03 and TAM; id never cited | cite |
| STO-D1 D2 D5 D7 D8 D10 · TRD-04 TRD-08 TRD-10 | FRD-STORES:338–347, FRD-TRADE:568–574 | cited by contracts, by no task | cite in the owning task (STO-D8 → p8-08; TRD-10 → p9-06) |
| MD-38 · TRD-02 · WS-312 | — | in tasks, not in contracts (WS-312 Trade Reports has no T5 screen contract) | add the T5 row |
| WS-338/339 | `FRD-MFG.md:447-448` | reserved, unused | none |

### CP-FR-015 · INFO · R29 dispositions: all 60 spot-checked fixes are present; two pointers are wrong
Checked against the named carrier file. **REM 17/17**: F1 (`p7-02:54`), F2 (`p7-02` `defaultConnectorOffersNothing`),
F3 (`p7-04:28`), F4 (`p7-10:63`), F5 (`p7-10:24-25`), F6 (`FRD-REM.md:79,160`), F7, F8 (`p7-08:31`), F9 (`p7-10`
GATE-6), F10 (descriptors grep in p7-02/03/04/05/07/09/11/12), F11 (`p7-03:26-31`, `p7-04:27`), F12 (`p7-04`
`FAIL_ON_UNKNOWN_PROPERTIES`), F13 (`IMPLEMENTATION-PLAN.md:658`), F14 (`IRREVERSIBLE.md` 6 D-16 notes), F15
(`WH-SC-666`), F16 (`p7-05` `list_code`), F17 (`p8-02:35`). **STORES 12**: F2, F3 (`POS-GRD-10:97` CHECK), F5
(`GBM-GRD-07`, `-UNR-04`, `-T4-01`), F8 (`GBM-GRD-08:80`), F16 (`MRQ-T1-03/04/06`), F26 (five `*_SELF_APPROVAL`
codes), F27 (`MRA-UNR-04:83`), F35 (`GTE-T1-02a`, `GTE-GRD-15`), F36 (`FRD-STORES.md:94`), TS-F2 (`POS-T1-12a/b`),
TS-F15 (`POS-T1-11a/c`), CN-4, CN-6 (`POS-T1-03a`). **TRADE 17**: TP-F4 (`TPO-T1-10a/b/c`, `-12`), F5
(`TPR-T1-09/10`), F7, F8 (`TAM-T1-10/11`), F9 (`TAM-GRD-03`), F12 (`TAM-GRD-05/08`), F17 (`TPO-GRD-15:141`), F19
(`TPO-GRD-03`, `TSO-GRD-03`), F20 (`TRC-T1-05`), F25 (`TRA-T4-04:146`), TS-F23 (`TRC-T1-07:90`, `-T3-04`), TS-F25,
MA-01, MA-03, MA-07, MA-14 (`TSO-T4-01/02/06`), MA-18 (`TSQ-T1-09`). **MFG 14**: F2, F3 (`SUB-T4-01`), F4
(`PRO-GRD-10:115`), F6 (`CST-T4-12`), F9 (`MRP-N-03:125`), F11 (`MSI-GRD-03`), F13 (`MRP-T3-04`), F14 (`PRC-T4-05`,
`MSI-T4-05`), F17, F19 (`PRC-T4-03`, FR-654), F21, F22 (`PRO-GRD-23`), F28, F29 (`PRO-T4-01`, `MRP-N-04`, `BOM-T1-14`).

Pointer defects:
- **TP-F7** (`FRD-TRADE.md:764`) points to `TPO-GRD-07`. The fix (*"open_unbounded … need an install rule"*) is
  actually in `TPO-T1-08` (`trade-purchase-order.contract.md:111`), FR-580 and `p9-07:23`.
- **TS-F25** (`FRD-TRADE.md:817`) points to the wildcards `TSO-T4-*` / `TSR-T4-*`, which a reviewer cannot resolve.

Still open, and recorded by the status file: the core `amendOrder` has no `TOLERANCE` field
(`RETARGET-PROGRAM-STATUS.md`, Remaining 1).

### CP-FR-016 · MINOR · The plan's stale counts
- `IMPLEMENTATION-PLAN.md:435` says *"51 of the 459 requirements"*.
- §8.1 `:1510-1512` expects `→ 459`. The real figure is 471 (main FRD) / 661 (all).
- §2 `:432` says *"Every FR is owned by exactly one task"*. That rule does not say how to treat a withdrawn FR,
  or one owned by a VOID task.

**Fix:** update the counts, and add the withdrawn/VOID rule.

---

## 3. What `tools/check-design-set.py` does not cover
Ran clean: **0 violations across 13 checks** (citations resolve; tables exist; Flyway ownership/bands; issue refs;
six sections; finding ids; plan↔issues; epics; FR owned once; id collisions; WS resolve; grid blocks), plus 97
advisory "version cited but unclaimed" lines (P7 removal tasks citing the files they delete, which is expected).

The checker does **not**:
1. read the task headers' **VOID / PARTIALLY VOID / SUPERSEDED** notes, so check-10 counts a VOID owner as a valid
   owner (CP-FR-001, -002);
2. know **WITHDRAWN**. A withdrawn FR still "owned" passes, and so does a live task asserting it (CP-FR-003, -004);
3. check **contracts** at all: FR→contract coverage, a `Source` column, rule ids that resolve, a rule with no FR,
   *(proposed)* codes (CP-FR-007…009);
4. check **FR→scenario** coverage (CP-FR-011), or live scenarios citing withdrawn FRs;
5. check FR **contiguity** (the FR-472…479 gap passes);
6. check consistency of the **D-16 withdrawal list** between DECISIONS and the FRD (CP-FR-005);
7. resolve **decision ids** (REM-D, STO-D, TRD, MD, OD, RN, RM) against a definition, or that each is carried into a
   task or contract (CP-FR-014);
8. verify **R29 disposition** "Where" pointers (CP-FR-015);
9. scan for **dealer/retail vocabulary** in live rows. The P7 grep gates cover classic code, not this design set
   (CP-FR-012);
10. check that a task file's `## Closes` agrees with plan §2. It checks the reverse direction only, so the second
    closers in CP-FR-010 pass.

**Proposed:** checks 14–18, in this order: VOID/WITHDRAWN-aware ownership; contract `Source` + FR coverage; FR→WH-SC
coverage; decision-id resolution; residue vocabulary allow-list.

---

## 4. Matrix (all 661 FRs)
Columns: **FR · st** (`act`/`wd`) **· mod · carrier task(s)** (plan §2 Closes) **· contract§** (abbrev + section;
in parentheses = weak citation only) **· scenarios** (count: first id, `WH-SC-` dropped) **· verdict**.
Contract abbreviations: MPR movement-post-reverse, RQP receipt-qc-putaway, AH accounting-handover, GTE gate-entry,
GBM grn-bill-match, IIS incoming-inspection-sampling, MRQ material-requisition, MRA mrn-authorisation, POS
po-schedule-port, SIR store-issue-return, BOM/CST/MSI/MRP/PRO/PRC/QRW/SUB mfg-*, TAM/TCE/TOA/TPO/TPR/TRC/TRA/TSQ/TSO/TSR
trade-*.

| FR | st | mod | task(s) | contract § | scenarios | verdict |
|---|---|---|---|---|---|---|
| FR-001 | act | base | p0-02 | MPR§1,1.3 | 6: 001… | OK |
| FR-002 | act | base | p0-02 | MPR§1.3 | 2: 001… | OK |
| FR-003 | act | base | p0-04 | MPR§1.3 | 173 | OK |
| FR-004 | act | base | p0-02 | MPR§1.4 | 5: 006… | OK |
| FR-005 | act | base | p0-02 | MPR§1.3 | 7: 010… | OK |
| FR-006 | act | base | p0-02 | — | 2: 033… | NC |
| FR-007 | act | base | p0-02 | (MPR§9) | 3: 030… | WC |
| FR-008 | act | base | p0-02 | MPR§1.3 | 031 | OK |
| FR-009 | act | base | p0-02 | MPR§1.3 | 4: 004… | OK |
| FR-010 | act | base | p0-02 | MPR§1.2 | 2: 034… | OK |
| FR-011 | act | base | p0-02 | (MPR§9) | 4: 016… | WC |
| FR-012 | act | base | p0-03 | — | 5: 014… | NC |
| FR-013 | act | base | p0-03 | MPR§1.2 | 4: 014… | OK |
| FR-014 | act | base | p0-03 | MPR§1.3 | 4: 017… | OK |
| FR-015 | act | app | p2-01 | MPR§1.3,4 | 2: 018… | OK |
| FR-016 | act | base | p0-03 | MPR§1.3 | 3: 190… | OK |
| FR-017 | act | base | p0-08 | MPR§1.3 | 5: 023… | OK |
| FR-018 | act | base | p0-02 | — | 3: 028… | NC |
| FR-019 | act | base | p0-04 | MPR§1.2,1.3 | 6: 013… | OK |
| FR-020 | act | base | p0-07 | MPR§1.3 | 3: 021… | OK |
| FR-021 | act | base | p0-02 | — | 2: 021… | NC |
| FR-022 | act | base | p0-02 | — | 043 | NC |
| FR-023 | act | base | p6-01 | — | — | NC NS |
| FR-024 | act | base | p0-02 | — | 3: 037… | NC |
| FR-025 | act | base | p0-02 | MPR§1.3 | 3: 038… | OK |
| FR-026 | act | base | p0-02 | — | 2: 042… | NC |
| FR-027 | act | base | p0-02 | MPR§1.2 | 2: 039… | OK |
| FR-028 | act | app | p2-01 | MPR§4 | 2: 170… | OK |
| FR-029 | act | base | p0-03 | MPR§1 | 2: 002… | OK |
| FR-030 | act | base | p0-02 | — | 004 | NC |
| FR-031 | act | base·app | p0-02 | — | 148 | NC |
| FR-032 | act | base | p0-08 | MPR§1.2 | 2: 024… | OK |
| FR-033 | act | base | p0-08 | MPR§1.3 | 4: 023… | OK |
| FR-034 | act | base | p0-08 | MPR§1.2 | 4: 167… | OK |
| FR-035 | act | base | p0-08 | MPR§1.2,1.3 RQP§1.3,1.4 | 3: 011… | OK |
| FR-036 | act | base | p0-08 | MPR§5.1 RQP§5.3 | 2: 028… | OK |
| FR-037 | act | base | p0-08 | MPR§1.2 | 2: 172… | OK |
| FR-038 | act | base | p1-13 | RQP§1.3 | 2: 175… | OK |
| FR-039 | act | base | p0-03 | RQP§1.3,3 | 6: 002… | OK |
| FR-040 | act | base | p0-03 | MPR§1,1.2 | 167 | OK |
| FR-041 | act | base | p0-08 | IIS§1.4 MPR§1.3 RQP§1.3 | 2: 178… | OK |
| FR-042 | act | base | p0-02 | — | 2: 026… | NC |
| FR-043 | act | base | p0-08 | — | 241 | NC |
| FR-044 | act | base | p0-08 | MPR§1.3,4 | 4: 023… | OK |
| FR-045 | act | base | p2-22 | (MPR§7) | 2: 158… | WC |
| FR-046 | act | base | p0-04 | — | 3: 034… | NC |
| FR-047 | act | base·mobile | p0-08 | — | 2: 169… | NC |
| FR-048 | act | base | p1-01 | — | 047 | NC |
| FR-049 | act | base | p1-01 | — | 2: 257… | NC |
| FR-050 | act | base | p1-01 | — | 2: 258… | NC |
| FR-051 | act | base | p1-01 | — | 259 | NC |
| FR-052 | act | base | p1-01 | — | 260 | NC |
| FR-053 | act | base | p1-03 | — | 280 | NC |
| FR-054 | act | base | p1-02 | — | 020 | NC |
| FR-055 | act | base | p1-02 | — | 019 | NC |
| FR-056 | act | base | p1-02 | — | 261 | NC |
| FR-057 | act | base | p1-02 | — | 2: 262… | NC |
| FR-058 | act | base | p1-02 | — | 263 | NC |
| FR-059 | act | base | p1-02 | — | 264 | NC |
| FR-060 | act | base | p1-01 | — | 3: 047… | NC |
| FR-061 | act | base | p1-04 | — | 2: 175… | NC |
| FR-062 | act | base | p1-02 | — | 2: 265… | NC |
| FR-063 | act | base | p3-15 | — | 2: 262… | NC |
| FR-064 | act | base | p1-02 | — | 203 | NC |
| FR-065 | act | base | p1-03 | — | 146 | NC |
| FR-066 | act | base | p1-03 | — | 2: 212… | NC |
| FR-067 | act | base | p1-03 | — | 267 | NC |
| FR-068 | act | base | p1-03 | RQP§1.3 | 075 | OK |
| FR-069 | act | base | p1-03 | — | 2: 130… | NC |
| FR-070 | act | base | p1-03 | — | 268 | NC |
| FR-071 | act | base | p1-03 | — | 3: 101… | NC |
| FR-072 | act | app | p2-24 | — | 2: 101… | VOID-OWNER NC |
| FR-073 | act | app | p2-24 | — | 2: 102… | VOID-OWNER NC |
| FR-074 | wd | adapter | p2-24 | — | 217 | WD |
| FR-075 | act | base | p3-10 | — | 287 | NC |
| FR-076 | act | base | p1-01 | — | 042 | NC |
| FR-077 | act | base | p1-04 | — | 269 | NC |
| FR-078 | act | base | p1-02 | — | 042 | NC |
| FR-079 | act | base | p1-05 | — | 045 | NC |
| FR-080 | act | base | p1-05 | — | 045 | NC |
| FR-081 | act | base | p1-05 | — | 045 | NC |
| FR-082 | act | base | p1-05 | — | 046 | NC |
| FR-083 | act | base | p1-05 | — | 3: 271… | NC |
| FR-084 | act | base | p1-05 | (MPR§9) | 001 | WC |
| FR-085 | act | base | p1-05 | MPR§1.3 | 3: 058… | OK |
| FR-086 | act | base·app | p1-05 | — | 075 | NC |
| FR-087 | act | base | p1-05 | RQP§1.3 | 076 | OK |
| FR-088 | act | base | p1-05 | — | 272 | NC |
| FR-089 | act | app | p1-06 | — | 2: 046… | NC |
| FR-090 | act | base | p1-05 | — | 273 | NC |
| FR-091 | act | base | p1-05 | — | 192 | NC |
| FR-092 | act | app | p1-06 | — | 274 | NC |
| FR-093 | act | base | p1-05 | — | 185 | NC |
| FR-094 | act | base | p1-07 | — | 142 | NC |
| FR-095 | act | base | p1-07 | — | 144 | NC |
| FR-096 | act | base | p2-05 | — | 139 | NC |
| FR-097 | act | base | p1-07 | — | 3: 080… | NC |
| FR-098 | act | base | p1-07 | RQP§1.3 | 079 | OK |
| FR-099 | act | base | p2-05 | — | 3: 107… | NC |
| FR-100 | act | base | p1-07 | — | 2: 145… | NC |
| FR-101 | act | base | p3-15 | — | 145 | NC |
| FR-102 | act | base | p0-05 | MPR§1.3,5.3 | 8: 016… | OK |
| FR-103 | act | base | p0-05 | IIS§1.2 MPR§1.2,1.3 RQP§1.2,1.3 | 5: 069… | OK |
| FR-104 | act | base | p0-02 | — | 4: 016… | NC |
| FR-105 | act | base | p1-07 | — | 5: 003… | NC |
| FR-106 | act | base | p1-07 | PRC§1.3 RQP§1.3 | 2: 080… | OK |
| FR-107 | act | base | p0-02 | — | 3: 001… | NC |
| FR-108 | act | base | p0-06 | — | 2: 275… | NC |
| FR-109 | act | app | p0-06 | — | 2: 001… | NC |
| FR-110 | act | base | p0-02 | — | 2: 026… | NC |
| FR-111 | act | base | p0-06 | — | 2: 026… | NC |
| FR-112 | act | base | p0-06 | AH§1.4 | 3: 032… | OK |
| FR-113 | act | base | p0-06 | — | 276 | NC |
| FR-114 | act | base | p0-06 | — | 3: 140… | NC |
| FR-115 | act | 3pl | p5-08 | — | 2: 032… | NC |
| FR-116 | act | base | p1-08 | — | 277 | NC |
| FR-117 | act | base | p1-08 | — | 277 | NC |
| FR-118 | act | base | p1-08 | — | 278 | NC |
| FR-119 | act | base | p1-08 | TRC§1.4 | 279 | OK |
| FR-120 | act | app | p1-13 | RQP§1.3 | 3: 051… | OK |
| FR-121 | act | base | p6-06 | — | — | NC NS |
| FR-122 | act | app | p1-12 | (GBM§0 POS§0) | 3: 051… | WC |
| FR-123 | act | app | p1-12 | RQP§5.3 | 2: 051… | OK |
| FR-124 | act | app | p1-13 | RQP§1.2 | 064 | OK |
| FR-125 | act | app | p1-12 | — | 065 | NC |
| FR-126 | act | app | p1-13 | — | 086 | NC |
| FR-127 | act | app | p1-13 | RQP§1 | 2: 064… | OK |
| FR-128 | act | app | p1-13 | RQP§1.2,1.3 | 063 | OK |
| FR-129 | act | app | p1-13 | MRA§1.3 RQP§1.3 | 4: 051… | OK |
| FR-130 | act | app | p1-13 | RQP§1.3 | 4: 066… | OK |
| FR-131 | act | app | p1-16 | RQP§1.3 | 2: 081… | OK |
| FR-132 | act | app | p1-12 | RQP§1.2,1.3 | 2: 068… | OK |
| FR-133 | act | app | p1-14 | RQP§1.2,1.3 | 2: 070… | OK |
| FR-134 | act | app | p2-13 | RQP§1.3 | 2: 071… | OK |
| FR-135 | act | app | p1-15 | RQP§1.2,1.3 | 2: 052… | OK |
| FR-136 | act | app | p3-05 | — | — | NC NS |
| FR-137 | act | app | p1-13 | (RQP§6) | 077 | WC |
| FR-138 | act | app | p2-13 | RQP§4 | 2: 067… | OK |
| FR-139 | act | app | p2-13 | IIS§1.4 | 2: 072… | OK |
| FR-140 | act | app | p5-10 | — | 399 | NC |
| FR-141 | act | app | p1-13 | RQP§4 | 2: 085… | OK |
| FR-142 | act | app | p6-05 | (TCE§0) | — | WC NS |
| FR-143 | act | app | p1-13 | BOM§1.3 PRO§1.3 RQP§1.3 | 078 | OK |
| FR-144 | act | app | p1-13 | RQP§1.3 | 079 | OK |
| FR-145 | act | app | p2-01 | — | 2: 108… | NC |
| FR-146 | act | base | p2-01 | — | 282 | NC |
| FR-147 | act | app | p2-02 | — | 6: 058… | NC |
| FR-148 | act | app | p2-02 | — | 058 | NC |
| FR-149 | act | app | p2-02 | — | 121 | NC |
| FR-150 | act | app | p2-02 | (MPR§7) | 285 | WC |
| FR-151 | act | app | p2-03 | — | 2: 098… | NC |
| FR-152 | act | app | p2-03 | — | 2: 137… | NC |
| FR-153 | act | app | p2-04 | — | 6: 059… | NC |
| FR-154 | act | app | p2-04 | — | 4: 059… | NC |
| FR-155 | act | app | p2-04 | — | 5: 059… | NC |
| FR-156 | act | app | p2-04 | — | 5: 059… | NC |
| FR-157 | act | app | p2-04 | — | 112 | NC |
| FR-158 | act | app | p3-14 | — | 2: 111… | NC |
| FR-159 | act | app | p2-04 | — | 3: 059… | NC |
| FR-160 | act | app | p2-05 | — | 2: 132… | NC |
| FR-161 | act | app | p2-05 | — | 5: 090… | NC |
| FR-162 | act | app | p2-05 | — | 286 | NC |
| FR-163 | act | app | p2-06 | — | 4: 015… | NC |
| FR-164 | act | app | p2-01 | MPR§1.3 RQP§1.2,1.3 | 3: 039… | OK |
| FR-165 | act | base·app | p0-13 | — | 10: 121… | NC |
| FR-166 | act | base | p0-09 | — | 6: 025… | NC |
| FR-167 | act | base | p0-09 | — | 8: 025… | NC |
| FR-168 | act | base | p0-09 | MPR§1.3 | 6: 017… | OK |
| FR-169 | act | app | p2-07 | — | 3: 099… | NC |
| FR-170 | act | app | p2-07 | — | 2: 184… | NC |
| FR-171 | act | app | p2-07 | — | 3: 025… | NC |
| FR-172 | act | base | p2-07 | — | 7: 053… | NC |
| FR-173 | act | base | p2-07 | — | 2: 053… | NC |
| FR-174 | act | base | p2-07 | (MRQ§0 MRA§0) | 2: 100… | WC |
| FR-175 | act | base | p0-03 | — | 4: 190… | NC |
| FR-176 | act | app | p2-07 | — | 101 | NC |
| FR-177 | act | app | p2-08 | — | 2: 058… | NC |
| FR-178 | act | app | p2-08 | — | 4: 053… | NC |
| FR-179 | act | app | p2-10 | — | 094 | NC |
| FR-180 | act | app | p2-08 | — | 104 | NC |
| FR-181 | act | app | p5-10 | — | 3: 333… | NC |
| FR-182 | act | app | p2-08 | — | 098 | NC |
| FR-183 | act | app | p3-13 | — | 095 | NC |
| FR-184 | act | app | p3-13 | — | 097 | NC |
| FR-185 | act | app | p2-09 | — | 093 | NC |
| FR-186 | act | app | p3-06 | — | 054 | NC |
| FR-187 | act | app | p2-09 | — | 2: 099… | NC |
| FR-188 | act | app | p2-09 | — | 2: 054… | NC |
| FR-189 | act | app | p2-09 | — | 3: 056… | NC |
| FR-190 | act | app | p3-07 | — | 232 | NC |
| FR-191 | act | base·app | p2-11 | — | 2: 106… | NC |
| FR-192 | act | app·mobile | p3-07 | — | — | NC NS |
| FR-193 | act | app | p2-10 | — | 094 | NC |
| FR-194 | act | app | p3-09 | — | — | NC NS |
| FR-195 | act | india·app | p2-in-04 | (GTE§0) | 2: 210… | WC |
| FR-196 | act | app | p2-10 | — | 103 | NC |
| FR-197 | act | app | p3-08 | — | — | NC NS |
| FR-198 | act | app | p5-11 | — | 401 | NC |
| FR-199 | act | app | p2-10 | — | 279 | NC |
| FR-200 | wd | app | p5-11 | — | 403 | WD·REF p5-11 |
| FR-201 | wd | app | p5-11 | — | 2: 402… | WD·REF p5-11 |
| FR-202 | wd | app·adapter | p5-11 | — | 404 | WD·REF p5-11 |
| FR-203 | wd | app·adapter | p5-12 | — | 3: 405… | WD |
| FR-204 | wd | app | p5-12 | — | 407 | WD |
| FR-205 | wd | app | p2-12 | — | 2: 105… | WD·REF p2-12 |
| FR-206 | act | app | p2-11 | — | 106 | NC |
| FR-207 | act | base·app·adapter | p1-11 | — | — | NC NS |
| FR-208 | wd | app | p5-09 | — | 2: 381… | WD·REF p3-05,p5-09 |
| FR-209 | wd | app | p5-09 | — | 383 | WD·REF p3-05,p5-09 |
| FR-210 | wd | app | p5-09 | — | 384 | WD·REF p3-05,p5-09 |
| FR-211 | act | app | p3-05 | RQP§1.2 | — | NS |
| FR-212 | act | base | p0-10 | — | 4: 052… | NC |
| FR-213 | act | base | p0-10 | — | 2: 052… | NC |
| FR-214 | act | app | p3-02 | — | 2: 228… | NC |
| FR-215 | act | base·app | p0-10 | — | 230 | NC |
| FR-216 | act | app | p3-02 | — | 249 | NC |
| FR-217 | act | mobile | p3-01 | — | 227 | NC |
| FR-218 | act | mobile | p0-16 | (AH§0,6) | 248 | WC |
| FR-219 | act | mobile | p3-01 | — | 229 | NC |
| FR-220 | act | mobile | p3-01 | — | 229 | NC |
| FR-221 | act | mobile·base | p0-16 | — | 2: 195… | NC |
| FR-222 | act | base·mobile | p3-03 | — | 231 | NC |
| FR-223 | act | app | p5-17 | — | 3: 349… | NC |
| FR-224 | act | base·app | p2-14 | — | 5: 055… | NC |
| FR-225 | act | app | p2-14 | — | 5: 055… | NC |
| FR-226 | act | app | p5-21 | — | 2: 361… | NC |
| FR-227 | act | app | p5-17 | — | 352 | NC |
| FR-228 | act | app | p6-03 | — | 352 | NC |
| FR-229 | act | base | p6-04 | — | — | NC NS |
| FR-230 | act | base | p0-12 | — | 4: 032… | NC |
| FR-231 | act | base | p0-12 | AH§1.4 | 162 | OK |
| FR-232 | act | base | p0-12 | AH§5.1 | 4: 156… | OK |
| FR-233 | act | base·app | p2-18 | AH§1.2,1.3,1.4,5.4 | 2: 156… | OK |
| FR-234 | act | base | p2-16 | — | 9: 049… | NC |
| FR-235 | act | base | p2-16 | — | 6: 062… | NC |
| FR-236 | act | base | p2-16 | — | 2: 058… | NC |
| FR-237 | act | base | p2-16 | — | 2: 148… | NC |
| FR-238 | act | base·app | p2-17 | — | 2: 153… | NC |
| FR-239 | act | app | p2-17 | — | 154 | NC |
| FR-240 | act | base·app | p2-17 | — | 155 | NC |
| FR-241 | act | app·base | p5-16 | — | 3: 345… | NC |
| FR-242 | act | app | p2-18 | AH§4 | 128 | OK |
| FR-243 | act | app·base | p5-16 | — | 348 | NC |
| FR-244 | act | app·india | p2-18 | AH§0 | 206 | OK |
| FR-245 | act | base | p2-16 | — | 160 | NC |
| FR-246 | act | base | p2-18 | AH§5.4 | 156 | OK |
| FR-247 | act | app | p2-18 | AH§5.2 | 159 | OK |
| FR-248 | act | base | p2-18 | AH§1.3,1.4 | 3: 156… | OK |
| FR-249 | act | app | p2-18 | AH§4,5.2 | 049 | OK |
| FR-250 | act | base·india | p4-11 | — | — | NC NS |
| FR-251 | act | base | p0-07 | (AH§7,9) | 2: 036… | WC |
| FR-252 | act | base | p1-03 | — | 2: 280… | NC |
| FR-253 | act | app | p2-15 | — | 3: 281… | NC |
| FR-254 | act | app | p5-18 | — | 353 | NC |
| FR-255 | act | app | p3-12 | — | 354 | NC |
| FR-256 | act | app | p2-15 | — | 2: 282… | NC |
| FR-257 | act | app | p2-15 | — | 2: 283… | NC |
| FR-258 | act | app | p6-02 | — | — | NC NS |
| FR-259 | act | app | p5-18 | — | 3: 354… | NC |
| FR-260 | act | app | p2-15 | — | 284 | NC |
| FR-261 | act | app | p3-11 | — | 287 | NC |
| FR-262 | act | app | p3-11 | — | 288 | NC |
| FR-263 | act | base·app | p3-11 | — | 288 | NC |
| FR-264 | act | app | p3-11 | — | 2: 289… | NC |
| FR-265 | act | app | p3-11 | — | 2: 289… | NC |
| FR-266 | act | base | p5-19 | — | 3: 135… | NC |
| FR-267 | act | app·3pl | p5-19 | — | 2: 358… | NC |
| FR-268 | act | — | p6-12 | BOM§0 | — | SUPERSEDED-OWNER NS |
| FR-269 | act | app | p2-12 | — | 3: 057… | NC |
| FR-270 | act | base | p0-05 | — | 3: 057… | NC |
| FR-271 | act | app | p2-12 | — | 057 | NC |
| FR-272 | act | app | p5-13 | — | 2: 341… | NC |
| FR-273 | act | base·app | p2-12 | — | 4: 057… | NC |
| FR-274 | act | app | p0-05 | — | 3: 057… | NC |
| FR-275 | act | app | p2-12 | — | 072 | NC |
| FR-276 | wd | app | p5-13 | — | 2: 343… | WD·REF p5-13,p5-23 |
| FR-277 | act | app·adapter | p5-15 | — | — | VOID-OWNER NC NS |
| FR-278 | act | app·adapter | p5-15 | — | — | VOID-OWNER NC NS |
| FR-279 | wd | adapter | p5-13 | — | 344 | WD·REF p5-13 |
| FR-280 | act | app | p5-14 | — | 2: 137… | NC |
| FR-281 | act | 3pl | p5-01 | — | 238 | NC |
| FR-282 | act | 3pl | p5-01 | — | 233 | NC |
| FR-283 | act | 3pl | p5-01 | — | 233 | NC |
| FR-284 | act | 3pl | p5-08 | — | 3: 244… | NC |
| FR-285 | act | 3pl | p5-03 | — | 5: 234… | NC |
| FR-286 | act | 3pl | p5-02 | — | 238 | NC |
| FR-287 | act | 3pl | p5-02 | — | 2: 234… | NC |
| FR-288 | act | 3pl | p5-04 | — | 4: 235… | NC |
| FR-289 | act | base·3pl | p2-28 | — | 2: 235… | NC |
| FR-290 | act | 3pl | p5-04 | — | 2: 237… | NC |
| FR-291 | act | 3pl | p5-05 | — | 237 | NC |
| FR-292 | act | 3pl | p5-05 | — | 3: 234… | NC |
| FR-293 | act | 3pl | p5-05 | — | 412 | NC |
| FR-294 | act | 3pl | p5-05 | — | 2: 238… | NC |
| FR-295 | act | 3pl | p5-06 | — | 4: 377… | NC |
| FR-296 | act | 3pl | p6-07 | — | 236 | NC |
| FR-297 | act | 3pl | p5-07 | — | 3: 333… | NC |
| FR-298 | act | 3pl | p5-07 | — | 2: 334… | NC |
| FR-299 | act | 3pl | p6-07 | — | 336 | NC |
| FR-300 | act | 3pl | p5-08 | — | 3: 140… | NC |
| FR-301 | act | 3pl·india | p4-10 | — | — | NC NS |
| FR-302 | act | 3pl | p6-07 | — | — | NC NS |
| FR-303 | act | 3pl | p5-01 | — | — | NC NS |
| FR-304 | act | india | p2-in-01 | — | 4: 213… | NC |
| FR-305 | act | base·india | p1-17 | — | 4: 124… | NC |
| FR-306 | act | app·india | p1-17 | — | 3: 124… | NC |
| FR-307 | act | india | p2-in-03 | — | 4: 206… | NC |
| FR-308 | act | base·india | p1-11 | — | 208 | NC |
| FR-309 | act | india | p2-in-04 | — | 3: 209… | NC |
| FR-310 | act | india | p2-in-02 | — | 2: 208… | NC |
| FR-311 | act | india | p4-01 | — | 214 | NC |
| FR-312 | act | india·app | p4-02 | — | 2: 207… | 2ND-CLOSER p10-10 NC |
| FR-313 | act | india | p2-in-03 | SUB§1.4 | 207 | OK |
| FR-314 | act | india | p4-03 | — | 3: 215… | NC |
| FR-315 | act | base·india | p0-04 | — | 3: 035… | NC |
| FR-316 | act | base·india | p4-04 | — | 215 | NC |
| FR-317 | act | india·app | p4-04 | — | — | NC NS |
| FR-318 | act | base | p0-02 | — | 212 | NC |
| FR-319 | act | base | p1-03 | — | 2: 206… | NC |
| FR-320 | act | base | p1-03 | — | 144 | NC |
| FR-321 | act | app·india | p4-05 | — | 144 | NC |
| FR-322 | act | app·india | p4-06 | — | — | NC NS |
| FR-323 | act | india | p4-07 | — | — | NC NS |
| FR-324 | act | india | p4-08 | — | — | NC NS |
| FR-325 | act | india | p4-01 | — | — | NC NS |
| FR-326 | act | india | p2-in-02 | — | 2: 209… | 2ND-CLOSER p4-12 NC |
| FR-327 | act | base | p1-03 | — | 247 | NC |
| FR-328 | act | app | p2-20 | — | 040 | NC |
| FR-329 | act | india·base | p4-09 | — | — | NC NS |
| FR-330 | act | base | p0-11 | — | 2: 252… | NC |
| FR-331 | act | base | p0-11 | — | 294 | NC |
| FR-332 | act | base | p0-11 | — | 252 | NC |
| FR-333 | act | base | p0-11 | — | 252 | NC |
| FR-334 | act | base | p3-22 | — | — | NC NS |
| FR-335 | act | base·app | p2-02 | — | 4: 058… | NC |
| FR-336 | act | base | p0-11 | — | 2: 226… | NC |
| FR-337 | act | base | p1-11 | — | 295 | NC |
| FR-338 | act | base·app | p5-21 | — | 363 | NC |
| FR-339 | act | base | p1-11 | — | 273 | NC |
| FR-340 | act | app | p5-21 | — | 296 | NC |
| FR-341 | act | base·app | p1-11 | — | 296 | NC |
| FR-342 | act | app | p2-02 | — | 2: 123… | NC |
| FR-343 | act | base·app | p5-21 | — | 364 | NC |
| FR-344 | act | app | p1-17 | — | 128 | NC |
| FR-345 | act | base | p2-28 | — | 2: 034… | NC |
| FR-346 | act | base·platform | p0-15 | — | 246 | NC |
| FR-347 | act | platform | p6-08 | — | — | NC NS |
| FR-348 | act | platform | p6-08 | — | — | NC NS |
| FR-349 | act | adapter | p0-14 | — | 4: 164… | NC |
| FR-350 | act | adapter | p0-14 | MPR§1.3 | 3: 179… | OK |
| FR-351 | act | adapter | p0-14 | — | 223 | NC |
| FR-352 | act | adapter | p2-25 | — | 2: 220… | VOID-OWNER NC |
| FR-353 | act | adapter | p0-14 | — | 224 | NC |
| FR-354 | act | base | p0-14 | — | 4: 044… | NC |
| FR-355 | act | base | p0-14 | — | 223 | NC |
| FR-356 | act | adapter | p0-14 | — | 292 | NC |
| FR-357 | act | base | p0-04 | AH§1.4 MPR§5.1 | 226 | OK |
| FR-358 | wd | adapter | p2-25 | — | 3: 216… | WD |
| FR-359 | wd | app·adapter | p2-25 | — | 3: 216… | WD |
| FR-360 | wd | adapter | p2-26 | — | 3: 218… | WD |
| FR-361 | act | adapter·app | p2-26 | — | 221 | VOID-OWNER NC |
| FR-362 | act | adapter | p2-26 | — | 222 | VOID-OWNER NC |
| FR-363 | act | adapter | p3-20 | — | 272 | NC |
| FR-364 | act | adapter | p3-21 | — | — | NC NS |
| FR-365 | wd | adapter | p6-09 | — | — | WD |
| FR-366 | act | — | p6-08 | — | — | NC NS |
| FR-367 | act | base | p0-04 | — | 2: 179… | NC |
| FR-368 | wd | base | p1-04 | — | 293 | WD·REF p1-04 |
| FR-369 | wd | app | p2-27 | — | 2: 293… | WD·REF p1-04 |
| FR-370 | wd | app | p2-27 | — | 2: 293… | WD·REF p1-04 |
| FR-371 | act | base·app | p0-01 | — | 2: 044… | NC |
| FR-372 | act | base·app | p0-01 | — | 292 | NC |
| FR-373 | act | base·platform | p0-01 | — | 044 | NC |
| FR-374 | act | all | p0-01 | — | 2: 246… | NC |
| FR-375 | act | base | p0-04 | — | 6: 147… | NC |
| FR-376 | act | base | p0-04 | — | 2: 257… | NC |
| FR-377 | act | base·platform | p0-01 | — | 291 | NC |
| FR-378 | act | base·platform | p0-01 | — | 291 | NC |
| FR-379 | act | base·platform | p0-01 | — | 291 | NC |
| FR-380 | act | app | p0-04 | RQP§5.4 | 147 | OK |
| FR-381 | act | app | p1-19 | — | 147 | NC |
| FR-382 | act | mobile | p0-16 | — | 147 | NC |
| FR-383 | act | base·app | p0-01 | IIS§1.4 RQP§1.2,1.4 | 042 | OK |
| FR-384 | act | app | p2-20 | — | 060 | NC |
| FR-385 | act | app | p2-20 | — | 3: 060… | NC |
| FR-386 | act | app | p2-20 | — | 060 | NC |
| FR-387 | act | app | p2-20 | — | 3: 040… | NC |
| FR-388 | act | app | p2-20 | — | 286 | NC |
| FR-389 | act | app | p2-21 | — | 119 | NC |
| FR-390 | act | app | p2-21 | — | 2: 113… | NC |
| FR-391 | act | app | p2-21 | — | 2: 018… | NC |
| FR-392 | act | app | p2-21 | — | 4: 052… | NC |
| FR-393 | act | app | p2-21 | — | 2: 283… | NC |
| FR-394 | act | app | p2-21 | — | 298 | NC |
| FR-395 | act | app | p2-29 | AH§5.2 RQP§5,5.6 | 298 | OK |
| FR-396 | act | app | p2-21 | — | 4: 029… | NC |
| FR-397 | act | app | p3-17 | — | — | NC NS |
| FR-398 | act | app | p3-16 | AH§3 | 2: 015… | OK |
| FR-399 | act | app | p6-10 | — | — | NC NS |
| FR-400 | act | app | p2-29 | AH§1.3 | 256 | OK |
| FR-401 | act | all | p0-15 | — | 2: 241… | NC |
| FR-402 | act | base·app | p0-15 | — | 246 | NC |
| FR-403 | act | base·app | p0-15 | — | 245 | NC |
| FR-404 | act | app | p0-15 | — | 3: 242… | NC |
| FR-405 | act | base·app | p1-18 | — | 3: 242… | NC |
| FR-406 | act | base | p0-06 | — | 4: 140… | NC |
| FR-407 | act | base·platform | p0-15 | — | 246 | NC |
| FR-408 | act | app | p2-23 | AH§1.2,1.3 GTE§1.2,1.4 GBM§1.2 MRQ§1.3 MPR§1.3 MRA§1.3 POS§1.2 RQP§1.3,1.4 | 6: 039… | OK |
| FR-409 | act | platform | p0-13 | — | 299 | NC |
| FR-410 | act | app | p0-15 | — | 2: 247… | NC |
| FR-411 | act | app | p2-19 | — | 2: 049… | NC |
| FR-412 | act | app | p2-19 | — | 050 | NC |
| FR-413 | act | app | p2-19 | — | 050 | NC |
| FR-414 | act | app | p3-18 | — | — | NC NS |
| FR-415 | act | app | p3-18 | — | — | NC NS |
| FR-416 | act | base | p1-10 | — | 3: 047… | NC |
| FR-417 | act | base | p1-10 | — | 048 | NC |
| FR-418 | act | app | p1-10 | — | 047 | NC |
| FR-419 | wd | app | p3-18 | — | — | WD·REF p3-18 |
| FR-420 | wd | adapter | p3-19 | — | — | WD |
| FR-421 | act | app | p6-11 | — | — | VOID-OWNER NC NS |
| FR-422 | wd | all | p0-16 | — | 4: 193… | WD·REF p0-03,p0-16,p2-13,p3-01,p3-06 |
| FR-423 | act | base | p0-02 | — | 043 | NC |
| FR-424 | act | mobile·app | p3-01 | — | — | NC NS |
| FR-425 | act | base·app | p3-02 | — | 2: 198… | NC |
| FR-426 | act | base | p1-09 | — | 4: 051… | NC |
| FR-427 | act | base·app | p0-13 | — | 3: 119… | NC |
| FR-428 | act | base | p1-11 | — | 300 | NC |
| FR-429 | act | platform | p0-16 | — | 253 | NC |
| FR-430 | act | app·mobile | p3-04 | — | 250 | NC |
| FR-431 | act | app·mobile | p1-19 | — | 247 | NC |
| FR-432 | act | app·platform | p1-20 | — | 247 | NC |
| FR-433 | act | app | p1-20 | — | 247 | NC |
| FR-434 | act | all | p0-01 | — | 248 | NC |
| FR-435 | act | all | p0-01 | — | 2: 241… | NC |
| FR-436 | act | base | p0-03 | MPR§1.2,1.4,4,5.1 RQP§1.3,1.4 | 4: 006… | OK |
| FR-437 | act | base | p0-03 | — | 3: 194… | NC |
| FR-438 | act | base·app | p1-20 | — | 255 | NC |
| FR-439 | act | base | p0-02 | RQP§3 TPO§3 | 2: 030… | OK |
| FR-440 | act | all | p0-01 | — | 300 | NC |
| FR-441 | act | base | p4-09 | — | — | NC NS |
| FR-442 | act | app | p3-23 | — | 254 | NC |
| FR-443 | act | base·app | p1-01 | — | 2: 270… | NC |
| FR-444 | act | base·app | p1-01 | — | 2: 270… | NC |
| FR-445 | act | app | p5-20 | — | 3: 385… | NC |
| FR-446 | act | base | p2-16 | AH§1.4,5.4 | 2: 062… | OK |
| FR-447 | act | app | p2-10 | — | — | NC NS |
| FR-448 | act | base | p0-05 | MPR§1.2 | — | NS |
| FR-449 | act | app | p2-09 | — | — | NC NS |
| FR-450 | act | base·app | p1-18 | (AH§7 RQP§7) | — | WC NS |
| FR-451 | act | base | p1-21 | MPR§1.3 | 3: 328… | OK |
| FR-452 | act | base | p3-24 | — | — | NC NS |
| FR-453 | act | base | p3-24 | — | — | NC NS |
| FR-454 | act | base | p3-24 | — | — | NC NS |
| FR-455 | act | base | p3-24 | — | — | NC NS |
| FR-456 | act | india | p4-13 | — | 3: 389… | NC |
| FR-457 | act | india | p4-13 | — | 392 | NC |
| FR-458 | act | base | p5-22 | — | 4: 337… | NC |
| FR-459 | act | app | p5-23 | — | 4: 365… | NC |
| FR-460 | act | base | p1-05 | — | 7: 045… | NC |
| FR-461 | act | adapter | p2-25 | — | 2: 308… | VOID-OWNER NC |
| FR-462 | act | app | p2-02 | — | 314 | NC |
| FR-463 | act | base·app | p1-03 | — | 320 | NC |
| FR-464 | wd | app | p5-08 | — | 2: 321… | WD·REF p5-08 |
| FR-465 | act | app | p1-17 | — | 322 | NC |
| FR-466 | act | app | p2-23 | — | 323 | NC |
| FR-467 | act | app | p5-09 | — | 326 | NC |
| FR-468 | act | base·app | p1-05 | — | 2: 324… | NC |
| FR-469 | act | base | p1-19 | — | 325 | NC |
| FR-470 | act | base·app | p2-21 | — | — | NC NS |
| FR-471 | act | app | p6-02 | — | — | NC NS |
| FR-480 | act | app | p7-02 | — | 3: 661… | NC |
| FR-481 | act | app | p7-02 | — | 3: 661… | NC |
| FR-482 | act | app | p7-03 | — | 3: 661… | NC |
| FR-483 | act | app | p7-03 | — | 4: 661… | NC |
| FR-484 | act | app · platform | p7-04 | — | 3: 661… | NC |
| FR-485 | act | app | p7-03 | — | 4: 661… | NC |
| FR-486 | act | app | p7-05 | — | 3: 661… | NC |
| FR-487 | act | app · base | p7-05 | — | 3: 661… | NC |
| FR-488 | act | app | p7-06 | — | 3: 661… | NC |
| FR-489 | act | app | p7-02 | — | 4: 661… | NC |
| FR-490 | act | app | p7-07 | — | 3: 661… | NC |
| FR-491 | act | app · base | p7-08 | — | 2: 661… | NC |
| FR-492 | act | base · app · india | p7-09 | — | 4: 661… | NC |
| FR-493 | act | base · app | p7-10 | — | 675 | NC |
| FR-494 | act | base · app | p7-10 | — | 2: 664… | NC |
| FR-495 | act | base · app | p7-10 | — | 3: 662… | NC |
| FR-496 | act | base · app · 3pl · india | p7-11 | — | 3: 664… | NC |
| FR-497 | act | app · platform | p7-11 | — | 4: 661… | NC |
| FR-498 | act | base · app · 3pl · india · platform | p7-13 | — | 4: 660… | NC |
| FR-499 | act | all | p7-13 | — | 3: 675… | NC |
| FR-500 | act | app | p8-01 | POS§0,1.3 | 420 | OK |
| FR-501 | act | app | p8-01 | POS§0,1.3 | — | NS |
| FR-502 | act | app | p8-01 | POS§0,1.3 | 2: 420… | OK |
| FR-503 | act | app | p8-01 | POS§0,1.3 | 3: 421… | OK |
| FR-504 | act | app | p8-01 | POS§0,1.3 | 3: 421… | OK |
| FR-505 | act | app | p8-02 | POS§0,1.3 | 426 | OK |
| FR-506 | act | app | p8-15 | POS§0,8a | 2: 478… | OK |
| FR-507 | act | app | p8-03 | GTE§1.2,1.3 | 427 | OK |
| FR-508 | act | app | p8-03 | GTE§1.3 | 2: 427… | OK |
| FR-509 | act | app | p8-03 | GTE§1.3,1.4 | 3: 427… | OK |
| FR-510 | act | app | p8-03 | (GTE§0) | 431 | WC |
| FR-511 | act | app | p8-03 | GTE§1.3 | 2: 441… | OK |
| FR-512 | act | app | p8-03 | GTE§1.3 | 432 | OK |
| FR-513 | act | app | p8-03 | GTE§1.3 | 2: 432… | OK |
| FR-514 | act | app | p8-03 | GTE§1.3,1.4 | 3: 432… | OK |
| FR-515 | act | app | p8-03 | (GTE§0) | 434 | WC |
| FR-516 | act | app | p8-04 | GBM§1.3 | 2: 437… | OK |
| FR-517 | act | app | p8-04 | GBM§1.3 | 438 | OK |
| FR-518 | act | app | p8-04 | (GBM§0) | — | WC NS |
| FR-519 | act | app | p8-04 | (GBM§0) | 438 | WC |
| FR-520 | act | app | p8-04 | GBM§1.3 | 4: 421… | OK |
| FR-521 | act | app | p8-05 | IIS§0,1.3 | 3: 442… | OK |
| FR-522 | act | app | p8-05 | IIS§0,1.3 | 4: 443… | OK |
| FR-523 | act | app | p8-05 | IIS§0,1.3 | 2: 447… | OK |
| FR-524 | act | app | p8-05 | IIS§0,1.3 | 2: 449… | OK |
| FR-525 | act | app | p8-06 | IIS§0,1.3 | 2: 451… | OK |
| FR-526 | act | app | p8-07 | IIS§0,1.3 | 2: 452… | OK |
| FR-527 | act | app | p8-08 | MRA§0,1.3 | 3: 454… | OK |
| FR-528 | act | app | p8-09 | MRQ§0,1.3 POS§8b | 2: 461… | OK |
| FR-529 | act | app | p8-09 | MRQ§0,1.3 MSI§0 | 2: 458… | OK |
| FR-530 | act | app | p8-09 | MRQ§0,1.3 MSI§0 | 5: 458… | OK |
| FR-531 | act | app | p8-09 | MRQ§0,1.3 MSI§0 | 3: 455… | OK |
| FR-532 | act | app | p8-09 | MRQ§0 MSI§0 | 461 | OK |
| FR-533 | act | app | p8-10 | MRQ§1.3 MSI§0,1.3 SIR§0,1.3 | 3: 450… | OK |
| FR-534 | act | app | p8-13 | SIR§0,5.4 | — | NS |
| FR-535 | act | app | p8-10 | MRQ§1.3 SIR§0,1.3 | 3: 463… | OK |
| FR-536 | act | app | p8-11 | SIR§0,1.3 | 3: 467… | OK |
| FR-537 | act | app | p8-11 | SIR§0 | 2: 467… | OK |
| FR-538 | act | app | p8-12 | MRA§0 | 456 | OK |
| FR-539 | act | app | p8-13 | — | 471 | NC |
| FR-540 | act | trade | p9-01 | — | 2: 480… | NC |
| FR-541 | act | trade | p9-02 | TCE§1.4 | 482 | OK |
| FR-542 | act | trade | p9-02 | (TCE§0 TPO§0) | 3: 483… | WC |
| FR-543 | act | trade | p9-02 | (TCE§0 TSO§0) | — | WC NS |
| FR-544 | act | REFUSE (default REFUSE) applies when the item has any effective AVL row: inviting, awarding or ordering from a supplier not APPROVED/PROVISIONAL for the date. SUSPENDED and DISQUALIFIED are refused under either setting | p9-02 | TCE§4 TPO§1.3 TRC§1.3 | 2: 485… | OK |
| FR-545 | act | trade | p9-02 | TCE§1.3,4 TSO§1.3 | 486 | OK |
| FR-546 | act | trade | p9-02 | (TCE§0) | 487 | WC |
| FR-547 | act | trade | p9-02 | TPR§1.2 | 2: 488… | OK |
| FR-548 | act | trade | p9-03 | (TAM§0) | 4: 489… | WC |
| FR-549 | act | trade | p9-03 | TAM§1.2 TRA§4 | 7: 484… | OK |
| FR-550 | act | trade | p9-03 | (TAM§0) | 3: 490… | WC |
| FR-551 | act | trade | p9-03 | TOA§1 | 492 | OK |
| FR-552 | act | trade | p9-03 | (TAM§0) | 2: 493… | WC |
| FR-553 | act | trade | p9-03 | (TAM§0 TOA§0) | 544 | WC |
| FR-554 | act | trade | p9-03 | (TAM§0) | 494 | WC |
| FR-555 | act | trade | p9-03 | (TAM§0) | — | WC NS |
| FR-556 | act | trade | p9-04 | (TPR§0) | 496 | WC |
| FR-557 | act | trade | p9-04 | MRP§4 POS§8b | 3: 497… | OK |
| FR-558 | act | trade | p9-04 | TPR§5.1 | 496 | OK |
| FR-559 | act | trade | p9-04 | (TPR§0) | 500 | WC |
| FR-560 | act | trade | p9-04 | TPR§4 | 2: 501… | OK |
| FR-561 | act | trade | p9-04 | (TPR§0) | 3: 503… | WC |
| FR-562 | act | trade | p9-05 | (TRA§0) | 2: 505… | WC |
| FR-563 | act | trade | p9-05 | (TRA§0) | 2: 505… | WC |
| FR-564 | act | trade | p9-05 | (TRA§0) | 3: 507… | WC |
| FR-565 | act | trade | p9-05 | (TRA§0) | 509 | WC |
| FR-566 | act | trade | p9-05 | (TRA§0) | 4: 490… | WC |
| FR-567 | act | trade | p9-05 | (TRA§0) | 4: 511… | WC |
| FR-568 | act | trade | p9-05 | (TRA§0) | 513 | WC |
| FR-569 | act | trade | p9-05 | (TRA§0) | 514 | WC |
| FR-570 | act | trade | p9-06 | (TRC§0) | 515 | WC |
| FR-571 | act | trade | p9-06 | (TRC§0) | 516 | WC |
| FR-572 | act | trade | p9-06 | (TRC§0) | 2: 517… | WC |
| FR-573 | act | trade | p9-06 | (TRC§0) | 4: 515… | WC |
| FR-574 | act | trade | p9-06 | (TRC§0) | 3: 519… | WC |
| FR-575 | act | trade | p9-07 | (TPO§0) | 524 | WC |
| FR-576 | act | trade | p9-07 | (TPO§0) | 572 | WC |
| FR-577 | act | trade | p9-07 | (TPO§0) | 3: 524… | WC |
| FR-578 | act | trade | p9-07 | (TPO§0) | 4: 527… | WC |
| FR-579 | act | trade | p9-07 | (TPO§0) | 3: 529… | WC |
| FR-580 | act | trade | p9-07 | (TPO§0) | 3: 491… | WC |
| FR-581 | act | trade | p9-07 | (TPO§0) | 532 | WC |
| FR-582 | act | trade | p9-07 | (TPO§0) | 533 | WC |
| FR-583 | act | trade | p9-07 | (TPO§0) | 3: 534… | WC |
| FR-584 | act | trade | p9-02 | (TPO§0) | — | WC NS |
| FR-585 | act | trade | p9-07 | (TPO§0) | 536 | WC |
| FR-586 | act | trade | p9-10 | (TPO§0) | 537 | WC |
| FR-587 | act | trade | p9-10 | (TPO§0) | 2: 538… | WC |
| FR-588 | act | trade | p9-10 | (TPO§0) | 539 | WC |
| FR-589 | act | trade | p9-10 | (TPO§0) | 3: 539… | WC |
| FR-590 | act | trade | p9-11 | (TOA§0) | 4: 537… | WC |
| FR-591 | act | trade | p9-11 | (TOA§0) | 3: 541… | WC |
| FR-592 | act | trade | p9-11 | (TOA§0) | 2: 542… | WC |
| FR-593 | act | trade | p9-11 | (TOA§0) | 545 | WC |
| FR-594 | act | trade | p9-12 | (TCE§0) | 2: 547… | WC |
| FR-595 | act | trade | p9-12 | (TCE§0) | 547 | WC |
| FR-596 | act | trade | p9-12 | TCE§1.4 | 549 | OK |
| FR-597 | act | trade | p9-12 | TPO§5.1 | 592 | OK |
| FR-598 | act | trade | p9-08 | (TSQ§0) | 3: 550… | WC |
| FR-599 | act | trade | p9-08 | (TSQ§0) | 2: 521… | WC |
| FR-600 | act | trade | p9-08 | (TSQ§0) | 3: 550… | WC |
| FR-601 | act | trade | p9-08 | (TSQ§0) | 4: 553… | WC |
| FR-602 | act | trade | p9-06 | (TRC§0) | 2: 520… | WC |
| FR-603 | act | trade | p9-06 | (TRC§0) | 588 | WC |
| FR-604 | act | trade | p9-06 | (TRC§0 TSQ§0) | 3: 520… | WC |
| FR-605 | act | trade | p9-09 | (TSO§0) | 4: 555… | WC |
| FR-606 | act | trade | p9-10 | (TSO§0) | 3: 556… | WC |
| FR-607 | act | trade | p9-09 | TSO§1.4 | 5: 557… | OK |
| FR-608 | act | trade | p9-09 | (TSO§0) | 559 | WC |
| FR-609 | act | trade | p9-09 | (TSO§0) | 2: 580… | WC |
| FR-610 | act | trade | p9-10 | (TSO§0) | 561 | WC |
| FR-611 | act | trade | p9-09 | (TOA§0 TSO§0) | 2: 560… | WC |
| FR-612 | act | trade | p9-13 | (TSR§0) | 4: 562… | WC |
| FR-613 | act | trade | p9-13 | (TSR§0) | 3: 564… | WC |
| FR-614 | act | trade | p9-12 | (TCE§0 TSR§0) | 2: 560… | WC |
| FR-615 | act | trade | p9-14 | — | 545 | NC |
| FR-616 | act | trade | p9-14 | TPO§5.1 TSQ§5.2 TSO§5.1 | 591 | OK |
| FR-617 | act | trade | p9-14 | — | 2: 565… | NC |
| FR-618 | act | trade | p9-07 | — | 2: 502… | NC |
| FR-619 | act | trade | p9-14 | TPR§3 | 591 | OK |
| FR-620 | act | mfg | p10-01 | BOM§1.4 SUB§0,1.4 | — | NS |
| FR-621 | act | mfg | p10-02 | (BOM§0 QRW§0) | — | WC NS |
| FR-622 | act | mfg | p10-03 | BOM§0,1.2,1.3,6 | — | NS |
| FR-623 | act | mfg | p10-03 | BOM§0,1.3,6,7 | 609 | OK |
| FR-624 | act | mfg | p10-03 | BOM§0,1.3,6 | — | NS |
| FR-625 | act | mfg | p10-03 | BOM§0,1.3,1.4,4,6,7 | 3: 600… | OK |
| FR-626 | act | mfg | p10-03 | BOM§0,1.2,1.3,6,7 MRP§1.3,4 PRO§1.3 | 2: 602… | OK |
| FR-627 | act | mfg | p10-03 | BOM§0,1.3,6,7 PRO§1.3 PRC§1.3 | 2: 604… | OK |
| FR-628 | act | mfg | p10-03 | BOM§0,1.2,7 CST§1.4 | 2: 606… | OK |
| FR-629 | act | mfg | p10-03 | BOM§0,1.2,7 | 608 | OK |
| FR-630 | act | mfg | p10-04 | BOM§0,1.3,6 | — | NS |
| FR-631 | act | mfg | p10-04 | BOM§0,1.3,6 | — | NS |
| FR-632 | act | mfg | p10-05 | PRO§0,1.3 SUB§1.3 | — | NS |
| FR-633 | act | mfg | p10-05 | BOM§1.2,1.4,7 MRP§4 PRO§0,1.3,1.4 QRW§1.1 | 2: 609… | OK |
| FR-634 | act | mfg | p10-05 | CST§1.4 MSI§1.3,6 PRO§0,1.3,1.4 PRC§1.3 QRW§1.3 SUB§1.3 | 4: 613… | OK |
| FR-635 | act | mfg | p10-05 | BOM§7 PRO§0,1.3 | 2: 610… | OK |
| FR-636 | act | mfg | p10-05 | PRO§0,1.4 | — | NS |
| FR-637 | act | mfg | p10-05 | MRP§1.6,4 PRO§0,1.3,1.4 | 2: 616… | OK |
| FR-638 | act | mfg | p10-06 | MSI§0 | — | NS |
| FR-639 | act | mfg | p10-06 | MSI§0,1.3,6,7 | 2: 618… | OK |
| FR-640 | act | mfg·app | p10-06 | CST§1.3 MSI§0,1.3,6,7 | 4: 615… | OK |
| FR-641 | act | mfg·app | p10-06 | MSI§0,1.3,6,7 | 622 | OK |
| FR-642 | act | mfg | p10-06 | MSI§0,1.3,6,7 | 623 | OK |
| FR-643 | act | mfg | p10-06 | MSI§0,1.3,4,6,7 PRC§1.3 SUB§1.3 | 2: 621… | OK |
| FR-644 | act | mfg | p10-07 | PRC§0,1.3 QRW§1.1 | 3: 625… | OK |
| FR-645 | act | mfg | p10-07 | PRC§0,1.3,1.4 | 3: 624… | OK |
| FR-646 | act | mfg | p10-07 | PRC§0,1.3 QRW§1.3 | 2: 630… | OK |
| FR-647 | act | mfg | p10-07 | PRO§1.3 PRC§0,1.3,1.4 | 3: 627… | OK |
| FR-648 | act | mfg·base | p10-07 | MSI§4 PRC§0 | 633 | OK |
| FR-649 | act | mfg | p10-07 | CST§1.3,4 PRC§0,1.3,1.4 QRW§1.3,4 SUB§1.2,1.3 | 2: 634… | OK |
| FR-650 | act | mfg | p10-07 | PRC§0 | — | NS |
| FR-651 | act | mfg | p10-08 | PRC§1.2 QRW§1.3,1.4,4 | 637 | OK |
| FR-652 | act | mfg·app | p10-08 | PRC§1.3 QRW§1.3 | 2: 636… | OK |
| FR-653 | act | mfg | p10-08 | QRW§1.3,1.4,4 | 2: 636… | OK |
| FR-654 | act | mfg | p10-07 | CST§1.3,1.4 PRC§0,1.3 | 4: 630… | OK |
| FR-655 | act | mfg | p10-07 | CST§1.3 PRC§0 | 640 | OK |
| FR-656 | act | mfg | p10-09 | CST§1.3,1.4 MSI§1.2,1.3,7 PRO§0,1.3 SUB§1.3 | 3: 641… | OK |
| FR-657 | act | mfg | p10-09 | CST§0,1.4 PRC§4 | — | NS |
| FR-658 | act | mfg | p10-10 | PRO§1.3 SUB§1.3,1.4 | 645 | OK |
| FR-659 | act | mfg | p10-10 | SUB§1.4 | 645 | OK |
| FR-660 | act | mfg·india | p10-10 | SUB§1.3,1.4 | 2: 646… | OK |
| FR-661 | act | mfg | p10-10 | CST§1.3 PRO§1.3 SUB§1.2,1.3 | 3: 647… | OK |
| FR-662 | act | mfg | p10-11 | MRP§1.3 | — | NS |
| FR-663 | act | mfg | p10-11 | MRP§1.3 | 653 | OK |
| FR-664 | act | mfg | p10-12 | MRP§1.3,1.5 SUB§1.4 | 4: 650… | OK |
| FR-665 | act | mfg | p10-12 | MRP§1.3 | 2: 650… | OK |
| FR-666 | act | mfg·app | p10-12 | MRP§1.3,1.4 | 4: 654… | OK |
| FR-667 | act | mfg | p10-12 | MRP§1.3,1.4 | 657 | OK |
| FR-668 | act | mfg | p10-13 | MRP§1.4 PRO§0,1.4 | 659 | OK |
| FR-669 | act | mfg | p10-01 | (BOM§0 SUB§9) | — | WC NS |

*End of R30 part FR.*
