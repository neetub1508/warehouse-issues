**Summary.** I did not write `docs/reviews/R31-functional-review-trade.md`: this agent may not write report files, so the full report is below for you to save. There are **23 findings: 6 High, 11 Medium, 6 Low**. Both engines ran; GPT's 11 findings all held up when checked, so none were dropped.

**Top 5:**
1. A FIXED sales-order amendment sends its added schedule lines to core as FORECAST, so they never ship.
2. Replacement releases are refused on FIXED orders, after validity, and on closed sales orders.
3. A whole BLANKET dispatch release never gets its own release reference, so the release never closes and neither does the sales order.
4. The unreceived part of a partly received PO release cannot be cancelled.
5. Trade's reason codes have no mapping to the core reason ids that every port command and RMA requires.

---

# Functional conformance — warehouse-trade (P9), R31 second audit
Contract: `docs/frd/FRD-TRADE.md` + 11 `docs/contracts/trade-*.contract.md` (v0/v1) | Mode: audit (pre-build design; no trade code exists)
Files reviewed: 30 in scope (FRD-TRADE, 11 contracts, `issues/p9-01…14`, `11-EPIC-p9.md`, FRD-STORES registry R.1–R.4). I also read these to check specific claims: `po-schedule-port.contract.md`, FRD-STORES STO-D25 and the CN dispositions, `issues/p7-08.md`, `FRD-REM.md` REM-D21 / WH-SC-662, and core code `WhInsufficientStockLogService.java`, `WhInsufficientStockLogValidationService.java`, `WhLostSaleRequest`, `V500004`, `V510050`, `WhRmaValidationService.java`. | File set: derived from the workflow
Engines: Claude + GPT (gpt-6.1-sol, medium) — 7 both · 11 Claude only · 5 GPT only · 0 dropped

Paths: `docs/`, `issues/` are under `/Users/bbhushan/work/git/workspace/warehouse-issues`; code paths are under `/Users/bbhushan/work/git/workspace/classic`.

## Verdict
23 findings (6 High · 11 Medium · 6 Low).

**What is clean:**
- **Menu ownership after P7.** L1 `warehouse_purchase_sales` (`FRD-TRADE.md:310`, `:576`; `issues/p9-01.md:82-93`, `:128`) has six L2 sections. The leaf counts in `FRD-TRADE.md:350` match the WS table: 8/5/6/5/7/8. The retired `warehouse_trade` key is refused, consistent with `p7-08.md:45,63-65` and `FRD-REM.md:81,131`.
- **CN-8 on the core side.** It is carried by FRD-STORES R.2 `:420`, `STO-D25` `:362`, `POS-T1-07` and `p8-01.md:114`.

**R29 dispositions that are not fully fixed:**
- TP-F2 (F-TR-018)
- TP-F4 / CN-6 (inside F-TR-004)
- TP-F6 (F-TR-012)
- TS-F16 (F-TR-002)

## Status reachability
| Status | In CHECK | In contract T1 | Inbound | Outbound | UI reachable | Verdict |
|---|---|---|---|---|---|---|
| PO release `RELEASED` → `CANCELLED` (partly received) | none (D-10) | TPO-T1-10c | release approval | cancel of the unreceived part | WS-294 | **No port path** (F-TR-004) |
| SO dispatch release `RELEASED` → `CLOSED` (whole BLANKET line) | none | TSO-T1-12 | approval | match by releaseRef | system | **Never matches** (F-TR-003) |
| SO line `SHORT_CLOSED` (partly shipped) | none | TSO-T1-13a | request | `cancelScheduleLine` | WS-303 | **Core refuses** (F-TR-005) |
| SO `CLOSED` within under-tolerance | none | TSO-T3-03 | job | `closeDemand` | system | FIRM remainder left in core (F-TR-006) |
| Replacement release (FIXED SO / expired / closed SO) | none | TSO-T1-16 | SRA receipt | release | WS-313 | **Refused by TSO-GRD-06 / T2-06** (F-TR-002) |
| SRA `APPROVED` (RMA create) | core RMA | TSR-T1-03 | approval | `createRma` | WS-285 | Reason id undefined (F-TR-007) |
| AVL / profile block request `APPROVED` | none | TCE-T1-03, -04a | submit | TAM | WS-285 | No currency to match a rule (F-TR-013) |
| Enquiry line (new item) `REGRETTED` | none | TSQ-T1-03 | regret | — | WS-298 | Forbidden by TSQ §0, yet required by FR-680 (F-TR-010) |
| RFQ `BIDS_CLOSED` / `EVALUATION` → `CANCELLED` | none | TRA-T1-04 | cancel | — | WS-288 | T2 gate forbids it (F-TR-018) |
| Everything else (PR, CS, RC, PO / SO headers, SRA ladder, evaluation runs) | none by design | yes | yes | yes | yes | Specified |

## Findings

### F-TR-001 — High: an amendment to a FIXED SO pushes its added schedule lines as FORECAST, so they never ship
- **Location:** `docs/contracts/trade-order-amendment.contract.md:112` (TOA-T4-02 SO branch); `docs/frd/FRD-TRADE.md:668` (§12a "`releaseSchedule` (`FORECAST`) for added schedule lines").
- **Evidence:**
  - `trade-sales-order.contract.md:192`: TSO-T4-01 sends FIXED as FIRM.
  - `:132`: TSO-GRD-06 says "FIXED lines never released".
  - `TRD-12` (`FRD-TRADE.md:581`).
  - On the PO side `newScheduleLines` carries `kind`, so this is a mirror asymmetry.
- **Effect:** a quantity increase or schedule add on a FIXED SO creates a core FORECAST line. Core never allocates it, and trade cannot release it.
- **Fix:** on a FIXED SO, push added lines as `FIRM` entries; FORECAST only for BLANKET. Amend TOA-T4-02 and §12a.
- **Engines:** Claude.

### F-TR-002 — High: replacement releases are refused on FIXED orders, after validity, and on closed SOs (R29 TS-F16 not fixed)
- **Location:** `trade-sales-order.contract.md:132` (TSO-GRD-06), `:121` (TSO-T1-16), `:169` (TSO-T2-06); `trade-sales-return-authorisation.contract.md:86` (TSR-GRD-03).
- **Evidence:**
  - `FRD-TRADE.md:816` (TS-F16) says the replacement is "exempt from block / validity guards". TSO-GRD-06 exempts only the schedule and ceiling bounds, and still applies "dates ∈ validity" and "FIXED lines never released".
  - TSO-T2-06 allows releases only from SO `APPROVED` / `ISSUED`.
  - An SRA may be raised on a `CLOSED` SO, because only `CANCELLED` is excluded.
- **Effect:** `REPLACE` on the commonest order type (FIXED), on an expired BLANKET, or after the SO closed leaves the SRA stuck until it is declined.
- **Fix:** exempt `is_replacement` from the type, validity and SO-state gates. Define the path for a closed SO: reopen, or require a new SO.
- **Engines:** Both.

### F-TR-003 — High: a whole BLANKET dispatch release never carries its release number, so the release and the SO never close
- **Location:** `trade-sales-order.contract.md:193` (TSO-T4-02), `:116` (TSO-T1-12), `:202` (TSO-T4-11); `FRD-TRADE.md:240` (FR-607 "`firmScheduleLine` … `releaseRef` = release number"), `:493` (WH-SC-557 `…-D02`).
- **Evidence:**
  - TSO-T4-01 (`:192`) creates BLANKET forecasts with `releaseRef = <so>-S<n>`.
  - The registry's `firmScheduleLine` (`FRD-STORES.md:429`) takes only `scheduleLineId` or `(demandLineId, releaseRef)` and never re-stamps the ref (`po-schedule-port.contract.md:75`).
- **Effect:** release close matches "core lines carrying its releaseRef", which never happens. The release stays `RELEASED`, TSO-T3-03 ("no release open") never fires, and `closeDemand` is never called.
- **Fix:** either a registry change (a `releaseRef` on `firmScheduleLine`, asked of STORES), or close releases by the stored `core_schedule_line_id` throughout TSO-T1-12 / T4-11 and FR-607.
- **Engines:** Both.

### F-TR-004 — High: the unreceived part of a partly received PO release cannot be cancelled (R29 TP-F4 / CN-6 half-applied)
- **Location:** `trade-purchase-order.contract.md:116` (TPO-T1-10c), `:196` (TPO-T4-09); `issues/p9-07.md:37`.
- **Evidence:**
  - Core `unfirmScheduleLine` requires `received_quantity = 0` (`po-schedule-port.contract.md:66`).
  - `cancelScheduleLine` requires 0 received (`:72`).
  - TPO-T1-10c promises "cancel the unreceived part … `CLOSED` when part was received". It also still says `cancelScheduleLine` returns BLANKET quantity "to core as FORECAST", which contradicts TPO-T4-09 (unfirm).
- **Effect:** a release of 100 with 40 received cannot give back its 60.
- **Fix:** for a partly received line, reduce it with `amendOrder` `scheduleChanges.quantity` and restore the BLANKET forecast with `newScheduleLines`. Align T1-10c's side effects with T4-09.
- **Engines:** Both.

### F-TR-005 — High: short-closing a partly shipped SO schedule line is refused by core
- **Location:** `trade-sales-order.contract.md:118` (TSO-T1-13a), `:139` (TSO-GRD-13), `:197` (TSO-T4-06).
- **Evidence:** short-close uses `cancelScheduleLine` on "open unpicked" lines. Core POS-T1-11c (`po-schedule-port.contract.md:77`) refuses with `409 DEMAND_SCHEDULE_PICKED` when picked > 0, so a FIRM line with 320 shipped of 500 has no cancel path for its 180.
- **Effect:** a FIXED or firmed line backordered on stock cannot be short-closed. This also blocks FR-681 capture for that case.
- **Fix:** add a "cancel unpicked remainder" operation to the demand registry (STORES), or reduce through `amendDemand`. Name it in TSO-T4-06.
- **Engines:** GPT.

### F-TR-006 — Medium: SO auto-close within under-tolerance leaves the FIRM remainder live in core
- **Location:** `trade-sales-order.contract.md:183` (TSO-T3-03), `:201` (TSO-T4-10).
- **Evidence:** `closeDemand` cancels only open FORECAST lines (`po-schedule-port.contract.md:79`). The tolerated FIRM remainder (e.g. 3 of 100) stays allocatable and backordered, and the order never reaches `SHIPPED`. On the PO side, `closeOrder` closes every line.
- **Fix:** `cancelScheduleLine` (or the F-TR-005 operation) on tolerated FIRM remainders before `closeDemand`, in the same transaction.
- **Engines:** GPT.

### F-TR-007 — High: trade reason codes have no mapping to the core reason ids that port commands require
- **Location:** `trade-sales-return-authorisation.contract.md:36` (line `reason_code` from code list `trade_return_reason`), `:123` (TSR-T4-03 header `reasonCodeId`); `trade-purchase-order.contract.md:193` (TPO-T4-06 `reasonCodeId`); `trade-sales-order.contract.md:197`; FR-546 `FRD-TRADE.md:123` (trade reasons are `whb_code_lists`).
- **Evidence:**
  - Core RMA `fk_wh_rmas_reason → whb_reason_codes` (`warehouse/backend/src/main/resources/db/migration/V510050__Create_wh_rmas_return_receipts_and_rto_consignments.sql:153`).
  - A RETURN-context check (`warehouse/backend/src/main/java/ai/warehouse/service/whrma/WhRmaValidationService.java:34-37`).
  - Every registry write (`closeLine`, `closeOrder`, `cancelOrder`, `cancelScheduleLine`, `unfirmScheduleLine`, `cancelRma`, `releaseConversion`, `AUTO_CLOSE`) takes a `reasonCodeId`.
  - Only the lost-sale reason is seeded in `whb_reason_codes` (`issues/p9-08.md:39`). How to choose one header reason when SRA lines have different reasons is also undefined.
- **Fix:** seed trade-owned `whb_reason_codes` (`owning_module = 'warehouse-trade'`, the right context per op) mapped from each code-list value, or use `whb_reason_codes` directly. Define the SRA header-reason rule.
- **Engines:** GPT, extended by Claude to every port command.

### F-TR-008 — Medium: the FR-681 lost-sale trigger includes a release cancel and OPEN call-offs that have no schedule-line identity
- **Location:** `trade-sales-order.contract.md:204` (TSO-T4-13), `:114` (TSO-T1-10c), `:50` (release line `schedule_line_id` null for an OPEN call-off).
- **Evidence:**
  - TSO-T4-13 lists `TSO-T1-10c`, a direct dispatch-release cancel. It has no approval request (key `<scheduleLineId>:<approvalRequestId>`), and its quantity returns to the schedule, so nothing is lost.
  - OPEN call-offs have no `wht_so_schedule_lines` row on which to accumulate `lost_sale_quantity`.
  - "actor = last approver" is undefined for the seeded zero-level `SO_CANCEL` / `SO_SHORT_CLOSE` (`TRD-13`: the submitter).
  - "after the port's `cancelScheduleLine`" is wrong for a cancel, which calls `cancelDemand`.
- **Fix:** drop `-10c` from the trigger. Key and accumulate OPEN call-offs on the release line. Use the TRD-13 principal.
- **Engines:** Both (Claude: the -10c, principal and port-op points; GPT: OPEN identity).

### F-TR-009 — Medium: a stock loss on a quotation with no enquiry cannot be recorded
- **Location:** `trade-sales-enquiry-quotation.contract.md:140` (TSQ-T4-05 `warehouseId = dispatch_warehouse_id`). The quotation fields (`:34-37`) have no dispatch site; only the enquiry does (`:29`). `FRD-TRADE.md:276` (M5: a quotation may have no enquiry).
- **Evidence:** `WhLostSaleRequest.warehouseId` is `@NotNull`, and TSQ-T4-05 rolls the outcome back on refusal.
- **Effect:** marking such a quotation `LOST` with `NO_STOCK` fails.
- **Fix:** add `dispatch_warehouse_id` to the quotation, defaulted from the enquiry or `wht_customer_profiles.default_dispatch_warehouse_id`.
- **Engines:** Claude.

### F-TR-010 — Medium: a not-catalogued enquiry line cannot be regretted, which FR-680 / WH-SC-598 require
- **Location:** `trade-sales-enquiry-quotation.contract.md:30-31`: "such a line can be regretted or quoted only after an item exists".
- **Evidence:** this contradicts `FRD-TRADE.md:224` (FR-680 "item description … *not catalogued*"), `:539` (WH-SC-598) and the contract's own TSQ-T4-05 (`:140`, "itemId null ⇒ itemDescription").
- **Fix:** allow regret (not quote) on a new-item line. TSQ-GRD-04 already guards quoting.
- **Engines:** Claude.

### F-TR-011 — Medium: lost-sale capture calls a core service that is not in the port registry
- **Location:** `FRD-TRADE.md:54-57` (§1: core is reached "only through the ports and SPIs" of the registry), `:224`, `:245`; TSQ-T4-05, TSO-T4-13.
- **Evidence:**
  - `WhInsufficientStockLogService.captureLostSale` (`warehouse/backend/src/main/java/ai/warehouse/service/WhInsufficientStockLogService.java:146`) appears nowhere in FRD-STORES R.2 (`:413-449`). Grep finds no FRD-STORES hit.
  - It takes no `PortEnvelope` or idempotency key, and no `warehouse:orders:port` verb.
- **Fix:** register it in R.2 (an owning port with envelope and op key, asked of STORES), or record a written exception in §1 and §12a.
- **Engines:** Claude.

### F-TR-012 — Medium: the auto-close jobs still act as a person (R29 TP-F6 not fixed in the contracts)
- **Location:** `trade-purchase-order.contract.md:179` (TPO-T3-03 "acts as the PO's buyer"); `trade-sales-order.contract.md:183` (TSO-T3-03 "acts as the SO's sales executive").
- **Evidence:** this contradicts `TRD-13` (`FRD-TRADE.md:582`) and FRD-STORES R.1 (`:405`: "core never accepts a job call made under a person's id"). `issues/p9-10.md:34` is correct.
- **Effect:** built to the contract, core refuses every auto-close.
- **Fix:** use trade's service principal in both rows.
- **Engines:** Both.

### F-TR-013 — Medium: AVL and profile-block approval requests have no currency, yet every rule needs one
- **Location:** `trade-approval-matrix.contract.md:93` (TAM-GRD-01 "currency ="); `issues/p9-03.md:15` (`currency_code NOT NULL`), `:69`; `trade-counterparty-evaluation.contract.md:84`, `:86` (TCE-T1-02, -04 open `PROFILE_BLOCK` / `AVL`).
- **Effect:** no rule can match, so every block, unblock and AVL change is refused `TRADE_NO_APPROVAL_RULE`. This breaks WH-SC-484, -570 and -595.
- **Fix:** state that non-monetary types match on the company currency with value 0, or that rule currency is nullable for them.
- **Engines:** Claude.

### F-TR-014 — Medium: cancelling or rejecting a PO release does not release its PR allocation
- **Location:** `trade-purchase-order.contract.md:114-116` (TPO-T1-10a/-10b/-10c: no PR effect); `trade-purchase-requisition.contract.md:132` (TPR-T4-03 lists only RFQ line, PO line); junction `target_type PO_RELEASE_LINE` (`:37`).
- **Evidence:** FR-561 (`FRD-TRADE.md:148`) says "a target line's cancellation releases its allocation". PO cancel and short-close do release it (`:108`, `:120`).
- **Effect:** quantity added to a release with *Add to release* (WS-287) is stranded as `ORDERED`.
- **Fix:** add the release-line cases to TPR-T4-03 and to the TPO-T1-10a/b/c side effects.
- **Engines:** Claude.

### F-TR-015 — Medium: an expired SRA keeps consuming the shipped-quantity allowance
- **Location:** `trade-sales-return-authorisation.contract.md:84` (TSR-GRD-01 "Σ non-cancelled SRA qty"), `:77` (TSR-T1-07 expired → `CLOSED`, "customer may raise a new SRA").
- **Evidence:** core counts only live RMAs (`po-schedule-port.contract.md:195`). The same applies to the lapsed remainder of a `PARTIALLY_RECEIVED` SRA.
- **Fix:** count live authorisations plus matched quantity only.
- **Engines:** GPT.

### F-TR-016 — Medium: a TOLERANCE amendment is refused by core only at apply, after every approval level
- **Location:** `trade-order-amendment.contract.md:74`, `:78` (TOA-GRD-02, -06 check only quantity).
- **Evidence:** CN-8 core refuses `409 TOLERANCE_BELOW_RECEIVED` (`FRD-STORES.md:362`; `po-schedule-port.contract.md:175`). TOA has no matching submit guard, so the refusal arrives at apply and rolls back the final approval (TPO-T4-03 pattern).
- **Fix:** add a TOA guard at submit, re-checked at apply, mirroring STO-D25.
- **Engines:** Claude.

### F-TR-017 — Low: CN-8 still reads as "open" in two places
- **Location:** `FRD-TRADE.md:718-721` (§12c heading "`CN-8` open (R30)"); `issues/p9-11.md:39-40` ("`CN-8` is open on `p8-01` — until it lands the PO `TOLERANCE` change type is hidden on WS-296"). Both contradict `FRD-TRADE.md:732` (Resolved 2026-10-23) and `p9-11.md:34-35` in the same file.
- **Effect:** a builder following p9-11 would hide the change type.
- **Fix:** update the heading, intro and p9-11 text.
- **Engines:** Claude (GPT noted the leftover narrative).

### F-TR-018 — Medium: RFQ cancel permission states are narrower than its transition (R29 TP-F2 half-applied)
- **Location:** `trade-rfq-award.contract.md:126` (TRA-T2-03 `DRAFT`, `ISSUED`) vs `:83` (TRA-T1-04 adds `BIDS_CLOSED`, `EVALUATION`); `FRD-TRADE.md:767`; WH-SC-566.
- **Effect:** the row-action gate hides Cancel exactly where TP-F2 added it.
- **Fix:** align T2-03.
- **Engines:** Both.

### F-TR-019 — Low: rules without a Source FR
- **Location:**
  - `trade-purchase-order.contract.md:199` (TPO-T4-12 Source `§5 M19`).
  - `trade-purchase-requisition.contract.md:104` (TPR-UNR-05 Source `TRD-07`).
  - Every T2 table has `—` sources (e.g. `trade-approval-matrix.contract.md:117`, `trade-sales-order.contract.md:164`).
  - `trade-reports.contract.md:60-64` has no Source column.
- **Fix:** cite an FR (FR-540 / FR-617 / FR-575 etc.) on each.
- **Engines:** Both.

### F-TR-020 — Low: two answers on whether WhReplenishmentSuggestionPort is a hard start-up dependency
- **Location:** `FRD-TRADE.md:117` (FR-540) and `trade-purchase-requisition.contract.md:93` (TPR-GRD-07) require it at start-up. `issues/p9-01.md:28-31` and `p9-04.md:24` make it optional.
- **Fix:** ratify optional and fix FR-540 / TPR-GRD-07.
- **Engines:** GPT.

### F-TR-021 — Low: the epic and the data model miss recent rows
- **Location:**
  - `issues/11-EPIC-p9.md:28-30` lists 10 contracts, without `trade-reports`.
  - The settings list (`:122-131`) omits `warehouse.trade.sales.lost_sale_reason_codes`.
  - FRD §8 (`FRD-TRADE.md:558-559`) omits `lost_sale_log_id` on the enquiry and quotation lines and `wht_so_schedule_lines.lost_sale_quantity`, which the tasks rely on (`p9-08.md:36`, `p9-09.md:52`).
- **Fix:** add them.
- **Engines:** Claude.

### F-TR-022 — Low: the §1 "never writes `whb_`" exception list is incomplete
- **Location:** `FRD-TRADE.md:49-51` allows only code-list, doc-type, number-series and print-template-kind seeds.
- **Evidence:** trade also seeds `whb_reason_codes` (`p9-08.md:39`), `whb_source_systems` (`p9-01.md:92`) and `whb_task_types` (TCE-T4-05 `:145`, TCE-OPEN-01). F-TR-007's fix adds more.
- **Fix:** extend the list under the owning-module guard.
- **Engines:** Claude.

### F-TR-023 — Low: whether the RFQ due date closes bids is self-contradictory
- **Location:** `trade-rfq-award.contract.md:66` (BIDS_CLOSED reachable when "due date passed — `TRA-T3-02`") vs `:138` (TRA-T3-02 "RFQ stays `ISSUED`").
- **Effect:** `NO_RESPONSE` (FR-563) is set at close, so it is undefined when the due date passes.
- **Fix:** pick one.
- **Engines:** Claude.

## Dropped after verification
None. Every GPT-only claim was re-checked at the cited lines and held.

## Remediation backlog
| Finding | Files to touch | Migration | Shared registries | Parity apply-to | Contract |
|---|---|---|---|---|---|
| F-TR-001 | trade-order-amendment, FRD-TRADE §12a, issues/p9-11 | none | none | PO side already correct | TOA-T4-02 |
| F-TR-002 | trade-sales-order, trade-sales-return-authorisation, FRD-TRADE R29 table, p9-09, p9-13 | none | none | PO twin TPO-T4-07 (check closed PO) | TSO-GRD-06, TSO-T2-06, TSR-GRD-03 |
| F-TR-003 | FRD-STORES R.2 (if a registry change), po-schedule-port, trade-sales-order, FRD-TRADE FR-607 / WH-SC-557, p9-09 | none | demand firm command | MFG reads release refs? confirm | TSO-T4-02, T1-12, T4-11 |
| F-TR-004 | trade-purchase-order, FRD-TRADE §12a, p9-07 | none | none | SO TSO-T1-10c | TPO-T1-10c, T4-09 |
| F-TR-005 | FRD-STORES R.2, po-schedule-port POS-T1-11c, trade-sales-order, p9-10 | none | demand op registry | PO uses closeLine | TSO-T1-13a, T4-06 |
| F-TR-006 | trade-sales-order, p9-10 | none | none | PO closeOrder | TSO-T3-03, T4-10 |
| F-TR-007 | FRD-TRADE FR-546 / §1, trade-sales-return-authorisation, trade-purchase-order, trade-sales-order, p9-02, p9-13 | next free in V551xxx (trade seed) | `whb_reason_codes` (owning-module guard) | all port-calling contracts | TSR-T4-03, TPO-T4-06, TSO-T4-06 |
| F-TR-008 | trade-sales-order, FRD-TRADE FR-681, p9-09, p9-10 | amend planned V550080 | none | none | TSO-T4-13 |
| F-TR-009 | trade-sales-enquiry-quotation, FRD §8, p9-08 | amend planned V550070 | none | none | TSQ §0, TSQ-T4-05 |
| F-TR-010 | trade-sales-enquiry-quotation, p9-08 | none | none | none | TSQ §0 |
| F-TR-011 | FRD-STORES R.2 or FRD-TRADE §1 / §12a, p9-08, p9-09 | none | port registry | none | TSQ-T4-05, TSO-T4-13 |
| F-TR-012 | trade-purchase-order, trade-sales-order | none | none | both sides | TPO-T3-03, TSO-T3-03 |
| F-TR-013 | trade-approval-matrix, p9-02, p9-03 | none | none | both profile sides | TAM-GRD-01 |
| F-TR-014 | trade-purchase-order, trade-purchase-requisition, p9-04, p9-07 | none | none | none (no SO PR) | TPR-T4-03, TPO-T1-10a/b/c |
| F-TR-015 | trade-sales-return-authorisation, p9-13 | none | none | none | TSR-GRD-01 |
| F-TR-016 | trade-order-amendment, p9-11 | none | none | SO tolerance is trade-only | new TOA guard |
| F-TR-017 | FRD-TRADE §12c, p9-11 | none | none | none | none |
| F-TR-018 | trade-rfq-award | none | none | none | TRA-T2-03 |
| F-TR-019 | all trade contracts, trade-reports | none | none | none | Source cells |
| F-TR-020 | FRD-TRADE FR-540, trade-purchase-requisition | none | none | none | TPR-GRD-07 |
| F-TR-021 | 11-EPIC-p9, FRD-TRADE §8 | none | none | none | none |
| F-TR-022 | FRD-TRADE §1 | none | none | none | none |
| F-TR-023 | trade-rfq-award | none | none | none | TRA §1.1 / T3-02 |

## Parity (C10)
- **Mobile:** none. FRD-TRADE §6 / §11 R16 say web-only by user rule 2026-09-11; this is a decided gap, not a finding.
- **Siblings:** the mirror is within trade (purchase ↔ sales) plus the core seams (`p8-01`, `p8-02`, `p8-15`, `p8-16`).
  - F-TR-003 and F-TR-005 need STORES registry changes, which affect MFG's demand reads.
  - F-TR-007 touches every trade port caller.
  - No other vertical shares this workflow.

## In code, not in contract
Not applicable: no trade code exists. Core code was read only to check the integration (lost-sale request, RMA reason FK).

## Contract quality
- The open decisions are still open: TCE-OPEN-02 (when the T&C version freezes) and TPR-OPEN-03 (the stale-write code).
- TSO-T4-13 says "after `cancelScheduleLine`" for a cancel that uses `cancelDemand` (folded into F-TR-008).
- The mirror table §5 M1–M33 is otherwise consistent with the contracts.

## Referred to standards reviewer
None.
