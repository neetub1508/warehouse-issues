# Functional conformance — R32 trade (warehouse-trade)
Contract: nine trade contracts' *R32 additions* (design commit `a244ff6`)   |   Mode: **audit (pre-build; no trade code exists)**
Files reviewed: 41 design files (scoped sections) + 9 classic code files   |   File set: derived from the workflow (p9-15…p9-21; R32 sections of p9-03/04/05/07/08/09/11/13/14; FRD-TRADE §4.15, §5 M35–M40, §12c CN-15…CN-20; DATA-MODEL §2.6.13; DECISIONS D-20 / OD-45; GLOBAL-SETTINGS OD-9; the p8-23/24/25, p8-30, p10-19/22/23/25 seams; PRD §4A/§5/§12/§13.1; the ledger)
Engines: Claude + GPT (gpt-6.1-sol, medium) — 7 both · 20 Claude only · 9 GPT only · 0 dropped

Paths: `D/` = `/Users/bbhushan/work/git/workspace/warehouse-issues/`, `C/` = `/Users/bbhushan/work/git/workspace/classic/`, `L` = the ledger `r32-ledger-trade.tsv`.

## Verdict
**36 findings (Critical 2 · High 15 · Medium 13 · Low 6).** The design is not ready to build. Three of the seams it depends on are wrong or missing:
- **Tax:** the provider p9-15 names does not compute tax.
- **Accounting hand-off:** two producers are designed for the same events.
- **Core / MFG SPIs:** six are owed and none has an owning task.

The PR → PO → receipt chain, direct-PO governance and SO closure also each carry guard or trigger defects.

## Status reachability (designed states touched by R32)
| Status | Authority | Contract row | Inbound | Outbound | UI reachable | Verdict |
|---|---|---|---|---|---|---|
| PR `HOD_APPROVED` (derived) | core steps | TPR-T1-11 | DEPARTMENT_HEAD level approved | final level | WS-286 filter | OK, but MR-origin PRs are refused before it (F-004) |
| PR line `ORDERED` with excess | TPR inventory (equality) | TPR-GRD-10 | allocation > qty | — | — | dead-end (F-018) |
| Core RMA `RECEIVED` | `C/warehouse/.../WhRma.java:53` has no such status | TSR-T4-06 | none | credit proposal | — | **unreachable** (F-003) |
| BoE `FILED → COSTED` | trade, unbuilt | TPO-T1-24 | Apply duties | Reverse | WS-317 | partial-receipt semantics undefined (F-015) |
| Feasibility `APPROVED` + `NOT_FEASIBLE` | trade | TSQ-T1-14 | approval | Regret | WS-314 | satisfies the quote guard (F-014) |
| Proposal `PROPOSED → HANDED_OVER → ACK/REJECTED` | trade | TSO-T4-16 | `demand_order.shipped` | ack / retry | WS-304 Billing | trigger never fires for BLANKET (F-010); duplicate producer (F-002) |
| SO display `INVOICED` / `CLOSED` | derived | TSO-T4-17/18 | ack | auto-close | WS-303/304 | never reached for SOs with replacements (F-011) |
| Unit `SOLD` (MFG) | p10-23 | PUR-T1-22 | invoice hand-off | — | WS-391 | no sender (F-017) |

## Findings

### F-R32TR-001 — Critical: GST "through the existing warehouse-india engine" — no such engine exists, and building one breaks OD-9
- Contract rows: TPO-T4-16, TRA-T4-05/-06, TSQ-T4-07, TSO-T4-15, TAM-GRD-13; CN-16 · Source: **Both**
- Evidence:
  - `D/docs/frd/FRD-TRADE.md:316` and `:852` and `D/issues/p9-15.md:12-16` say warehouse-india "implements it over its built `whin_hsn_tax_master`…".
  - That code holds reference data only:
    - `C/warehouse-india/.../V540110__Create_whin_gst_state_codes_hsn_tax_master_and_sac_master.sql:32-38`: "OD-9 - WAREHOUSE NEVER COMPUTES TAX … Nothing in warehouse multiplies a value by gst_rate_percent. WIN-13's V540111 (the six relational tax-engine tables) is RESERVED HISTORY".
    - The same file at `:136,:167-168`, and `WhinTransferIrnService.java:57` ("No tax is computed here (OD-9)").
    - `D/docs/GLOBAL-SETTINGS-DECISIONS.md:77`: OD-9 = "Warehouse does not implement its own tax calculation engine. PROVIDER uses a tested accounting/localisation provider".
  - The HSN master has no reverse-charge column, yet FR-761 says "reverse charge flagged per HSN".
  - The engine that does exist is accounting's tax determination: `accounting-base/.../AccTaxDeterminationRule*`, `accounting/.../AccDocumentTaxDetermination`, already used by `AccQuotationService` and `AccSalesDocumentLineBuilder`.
  - D-20 item 5 says "via the existing GST engine" and does not reverse OD-9.
- What a user experiences: either p9-15 ships with nothing behind it, so every document reads *Taxes extra*, or a third tax engine gets built in warehouse-india. That engine's PO/SO tax would then disagree with the invoice accounting computes from the p9-20 proposal.
- Fix: re-point CN-16 to accounting's tax determination, reached through the accounting-facing adapter (p8-23). warehouse-india keeps only its reference data. Alternatively, record an explicit reversal of OD-9 and own the engine — not both. Update DATA-MODEL §2.6.13, which calls the rows "from the india engine", and add the effective document date to `TaxPreviewRequest` (GPT note).

### F-R32TR-002 — Critical: two producers for one invoice / credit-note event, with different kind names
- Contract rows: TSO-T4-16, TSR-T4-06, CN-18; core AHO kinds · Source: **Both**
- Evidence:
  - Core side: `D/issues/p8-23.md:27-28` seeds `CREDIT_NOTE_PROPOSAL` (RMA receipt, SRA intent CREDIT) and `INVOICE_REQUEST` ("a despatch is posted"). `D/docs/contracts/accounting-handover.contract.md:111` says the same.
  - Trade side: `D/issues/p9-20.md:20-22` builds a `SALES_INVOICE` proposal on the same despatch, handed over as `SALES_DISPATCH`, and a `SALES_RETURN` proposal on the same return. `D/docs/frd/FRD-TRADE.md:854` (CN-18) asks base for `SALES_DISPATCH` / `SALES_RETURN` / `SERVICE_RECEIPT` / `BILL_OF_ENTRY`.
  - None of the CN-18 kinds is in p8-23's seed list. FRD-TRADE §5 M39 (`:379`) also gives credit-note proposals to trade.
- What a user experiences: one dispatch reaches accounting twice, as two invoice requests with different payloads (one with SO price and tax, one without), and the same happens for each return.
- Fix: one producer and one canonical kind per business event. Recommended: core emits the event identity; trade enriches it with commercial price and tax through a core-declared enrichment SPI. If instead trade's proposal is canonical, core's `INVOICE_REQUEST` / `CREDIT_NOTE_PROPOSAL` must stand down for trade-sourced demand. Reconcile p8-23, p8-25 and p9-20 together, plus receiver deduplication on the event id.

### F-R32TR-003 — High (rank 1, unreachable): credit-note proposal waits for an RMA status core does not have
- Contract row: TSR-T4-06 · Source: GPT
- Evidence: `D/issues/p9-20.md:27` and `D/docs/contracts/trade-sales-return-authorisation.contract.md:145` wait for "RMA `RECEIVED`". Core statuses are `OPEN` / `APPROVED` / `MATCHED` / `EXPIRED` / `CANCELLED` (`C/warehouse/.../entity/WhRma.java:53-56`; SRA contract `:63`).
- What a user experiences: a `CREDIT` return never produces its credit-note proposal; partial returns are also missed.
- Fix: trigger on SRA `RECEIVED` / `PARTIALLY_RECEIVED` (core `MATCHED` plus receipt quantities) together with QC disposition posted, and define the order in which those two events may arrive.

### F-R32TR-004 — High (rank 1): EXACT conditions plus a REFUSE default make MR-origin PRs, direct POs and price-changed SOs unapprovable by default
- Contract rows: TAM-GRD-14, TPR-T1-11, TPR-T1-02b · Source: Claude
- Evidence:
  - TRD-14 (`D/docs/frd/FRD-TRADE.md:683`): "a rule without conditions covers only a document without conditions".
  - Every trade type is REFUSE (`D/issues/p9-03.md:72`), and the zero-level seeds have empty condition sets (`:32`).
  - R32 attaches conditions to mainstream flows (`D/issues/p9-03.md:98`): `from_approved_mr` on every MR hand-off PR (FR-743), `direct_po`, `price_differs_from_quotation`, `exceeds_pr`.
  - No seed exists for any of these conditions, and condition sets with several members (for example a direct SAMPLE PO = {`direct_po`, `sample_from_unlisted_vendor`}) each need their own EXACT rule.
- What a user experiences: on a new install the one-press MR → PR hand-off (TPR-T1-02b, default on) fails `422 APPROVAL_NO_RULE`. That breaks the PR → PO → receipt chain at its first step, and the same refusal hits every direct PO and every SO whose price differs from the quotation.
- Fix: seed rules for each R32 condition (for example `from_approved_mr` → one Purchase level), or have these condition-bearing types use `INCLUDES` matching. Add an acceptance row that an MR hand-off PR is approvable on a clean install.

### F-R32TR-005 — High (rank 2, permission weaker): a manual RFQ award avoids direct-PO governance
- Contract row: TPO-GRD-21 · Source: GPT
- Evidence: a manual RFQ needs no PR (`D/docs/contracts/trade-rfq-award.contract.md:80,:99`). The award drafts the PO (`:147`). A line counts as direct only with "no PR allocation **and no award**" (`D/docs/contracts/trade-purchase-order.contract.md:273`; FRD `:301`). The PRD requires `po:create_without_pr` for any PO without a PR (`PRD:155`).
- What a user experiences: a buyer without `create_without_pr` raises a manual RFQ, awards it and gets a PO with no PR. The category restriction, mandatory reason, `direct_po` condition and Direct-PO report are all skipped.
- Fix: decide directness by approved PR coverage, including coverage inherited through the award. An award with no PR behind it stays direct.

### F-R32TR-006 — High (rank 3): CN-15…CN-20 have no owning core or MFG task, and the MFG port names already diverge
- Contract rows: CN-15…CN-20 · Source: Claude
- Evidence:
  - Searching every `D/issues/p8-*.md`, `D/docs/frd/FRD-STORES.md` and `D/docs/PORT-AND-ADAPTER-CONTRACT.md` finds none of `WhTaxPreviewProvider`, `WhCustomerCreditCheckProvider`, `WhLandedCostPort.applyReceiptCharge`, `WhReceiptExchangeRateProvider`, `WhDemandProductionProgressQuery` or `allocateImmediately`. They appear only in the trade consumers (p9-09/11/15/17/18/19/21) and in FRD-TRADE §12c (`:851-856`, all marked "owed").
  - MFG declares different ports: `CostEstimatePort.estimate(PortEnvelope, EstimateCommand…)` (`D/issues/p10-25.md:20`) and `SampleRequestPort.open(PortEnvelope, OpenSampleRequestCommand)` (`D/issues/p10-19.md:20`; FRD-MFG MD-51 `:674`). Trade calls `WhPreSaleCostingProvider.estimate` and `WhSampleRequestPort.request/status` (FRD-TRADE `:855`).
  - `WhDemandProductionProgressQuery` has no implementer in any p10 task.
  - Core p8-23 declares a different credit seam, `WhbCustomerCreditExposureProvider.exposure(company, counterparty)` (`D/issues/p8-23.md:34`), next to trade's CN-17 `WhCustomerCreditCheckProvider.check(...)`.
  - D-20 item 6 requires every R32 item to land in exactly one open issue.
- What a user experiences: p9-15, p9-17, p9-18, p9-19, p9-21 and the impact half of p9-11 are blocked on work nobody is building. The order book's produced / in-production columns and `IN_PRODUCTION` status never fill.
- Fix: open carrier tasks for CN-15, CN-16, CN-17 and CN-20 (core), CN-19 progress (core declare + p10 implement), and CN-18 kinds (p8-23). Rename trade's calls to MFG's `CostEstimatePort` / `SampleRequestPort`, or the other way round, and use one credit seam.

### F-R32TR-007 — High (rank 4): `AccCreditCheckService` cannot answer CN-17 as written, and the accounting entry point was never filed
- Contract rows: TSO-GRD-25, TSO-GRD-26, TSO-T1-18; CN-17 · Source: Claude
- Evidence:
  - `C/accounting/.../AccCreditCheckService.java:37-44`:
    - exposure = receivables + open orders + drafts − advances;
    - modes OFF/WARN/BLOCK/APPROVE;
    - "APPROVE - routed to `AccApprovalSubjects#CREDIT_LIMIT_OVERRIDE` (`acc_credit_control:override`)"; the routing is at `:186-190`, and a credit hold refuses like BLOCK.
  - `AccCreditExposureCalculator.java:82-87` has no overdue amount or days and no per-document advance. Advances are per party (reference_mode ADVANCE).
  - CN-17 nonetheless expects "overdue amount / days" and `advanceReceived(counterpartyId, salesOrderRef)` → amount, UTR, date (FRD `:853`). FR-767 then turns overdue into a trade-side BLOCK whatever accounting's mode is (`:322`) — rebuilding credit policy in trade, which D-20 item 3 forbids.
  - `D/issues/p9-17.md:14` says the entry point is filed in `neetub1508/accounting` with label `prd-r32`. `gh issue list --repo neetub1508/accounting --label prd-r32 --state all` returns zero issues.
- What a user experiences: under APPROVE mode an SO needs two overrides, accounting's and trade's `SO_CREDIT_OVERRIDE`. Overdue and advance checks have no data source, and the "reuse" is not specified on the accounting side.
- Fix: file the accounting entry point: a check-only call that returns figures and a decision without raising accounting's own approval, plus overdue ageing and SO-referenced receipts. Define how accounting's mode maps to trade's decision, including OFF and hold. Reconcile with p8-23's provider.

### F-R32TR-008 — High (rank 4): the release credit check counts an already-exposed order again
- Contract row: TSO-GRD-25 · Source: **Both**
- Evidence: candidate = the document's gross value, and extra exposure = trade's open SO value + shipped-not-invoiced (`D/issues/p9-17.md:20`; contract `:265`). At release approval the release is already inside the open SO value. Shipped-not-invoiced also overlaps accounting's `draftInvoices` once accounting drafts the invoice from the proposal (`AccCreditExposureCalculator.java:87`). Accounting itself avoids this kind of double count (`AccCreditCheckService.java:129`).
- What a user experiences: a customer within limit is refused `422 TRADE_CREDIT_LIMIT_EXCEEDED` at dispatch because the same 100 is counted twice.
- Fix: define exposure buckets that cannot overlap and an incremental candidate per checkpoint; exclude the current document; hand over shipped-not-invoiced only until accounting drafts the invoice.

### F-R32TR-009 — High (rank 4): FIXED SOs skip every dispatch-time check
- Contract rows: TSO-GRD-23…-26 · Source: GPT
- Evidence: FIXED schedule lines become `RELEASED` at SO approval (`D/docs/contracts/trade-sales-order.contract.md:104`), and releases exclude FIXED lines (`:111`). Transport, checklist, credit and advance checks all hang on release approval (`:261-265`). The PRD wants the check at dispatch (`PRD:313`).
- What a user experiences: a FIXED SO (the default type) ships without Dispatch In-charge approval, checklist, credit recheck or advance check.
- Fix: one dispatch-authorisation point covering FIXED as well as OPEN/BLANKET, immediately before the goods become eligible to ship.

### F-R32TR-010 — High (rank 4): the invoice proposal is triggered by a header event that never fires for schedule-driven SOs
- Contract row: TSO-T4-16 · Source: Claude
- Evidence: "on core `demand_order.shipped` … one proposal per shipment" (`D/issues/p9-20.md:20`; FRD `:328`). OD-45 (A) (`D/docs/DECISIONS.md:838`) says a schedule-driven demand order "returns to OPEN after each despatch and is never SHIPPED/DELIVERED while the source can still release". WH-SC-766 expects two shipments → two proposals.
- What a user experiences: BLANKET/OPEN SO dispatches produce no invoice proposal until the order closes, so nothing is billed.
- Fix: trigger on a shipment-level core event, one proposal per shipment id, and name it in CN-18.

### F-R32TR-011 — High (rank 4): replacement shipments are invoiced, credit-checked and keep the SO open
- Contract rows: TSO-T4-16, TSO-T4-17, TSO-GRD-25, TSR-GRD-07 · Source: Claude
- Evidence:
  - A replacement release goes to core as FIRM "at the original net price" (`D/docs/contracts/trade-sales-order.contract.md:122,:133`), and `WARRANTY_REPLACEMENT` "behaves as REPLACE for the replacement release" (`D/issues/p9-13.md:51`).
  - FR-773 proposes an invoice for every shipment, and FR-774 closes only when billed = shipped (`D/issues/p9-20.md:20,:24`).
  - Release credit and advance checks apply to every release (`D/issues/p9-17.md:20`).
- What a user experiences: a free warranty replacement either reaches accounting as an invoice, or is never billed, which leaves billed < shipped and the SO never closes under `SHIPPED_AND_INVOICED`. A customer over limit can also be blocked from receiving a warranty replacement.
- Fix: exclude `is_replacement` shipments from invoice proposals, from billed-versus-shipped closure and from release credit/advance checks; write the rule into TSO-T4-16/17 and TSO-GRD-25.

### F-R32TR-012 — High (rank 4): goods can leave the gate before the invoice exists
- Contract rows: TSO-T4-16/17; CN-18 · Source: Claude
- Evidence: PRD §12 "Gate out: gate pass against invoice" (`PRD:316`). For goods, CGST Act s.31(1)(a) requires the tax invoice at or before removal. Design: the proposal is built after `shipped`, and the gate-pass print only *shows* the invoice number (`D/issues/p9-20.md:24-25`). Nothing blocks gate-out until accounting acknowledges, and no CN asks core for a gate-out veto.
- What a user experiences: a vehicle leaves with a gate pass and an e-way bill but no invoice number, which is a statutory exposure.
- Fix: add a core gate-out guard (a SPI that trade or the accounting adapter answers) requiring an acknowledged invoice for trade sales when an accounting target is configured. Otherwise state the delivery-challan basis explicitly.

### F-R32TR-013 — High (rank 4): the place-of-supply rules give wrong or refused tax for import, bill-to-ship-to, export/SEZ and reverse charge
- Contract rows: TPO-T4-16, TSO-T4-15; FR-761 · Source: Claude
- Evidence:
  - FR-761 (`D/docs/frd/FRD-TRADE.md:316`): purchase = receiving site, sales = ship-to; unresolved → `422 TRADE_PLACE_OF_SUPPLY_UNRESOLVED` at submit.
  - An IMPORT PO (FR-768) has a foreign supplier and no GST; IGST is paid on the BoE. Neither p9-15 nor p9-18 exempts it, so import PO submit is refused.
  - FR-753 adds `bill_to_address_id`, but under IGST Act s.10(1)(b) the place of supply in a bill-to-ship-to sale is the bill-to party's state, not the ship-to state.
  - Export and SEZ supplies are zero-rated; M38 refuses the sales twin but an SO to a foreign or SEZ ship-to still goes through preview.
  - Reverse charge "per HSN" has no column (F-001). Ledger `purchase-inward:BEYOND-7` routes RCM to accounting, which contradicts p9-15's `is_reverse_charge`.
- What a user experiences: import POs cannot be submitted; bill-to-ship-to SOs show CGST+SGST where IGST applies (or the reverse), and the invoice proposal carries the error into accounting.
- Fix: supply kinds `DOMESTIC` / `IMPORT` (skip, BoE carries the tax) / `EXPORT` / `SEZ`; s.10(1)(b) rule; RCM decided by the provider from supplier registration plus SAC, not HSN; align the ledger row.

### F-R32TR-014 — High (rank 4): an approved `NOT_FEASIBLE` review satisfies the quotation gate
- Contract rows: TSQ-GRD-11, TSQ-T1-14 · Source: GPT
- Evidence: the guard requires an "`APPROVED` feasibility review" (`D/docs/contracts/trade-sales-enquiry-quotation.contract.md:176`), and `:177` allows an approved review whose outcome is `NOT_FEASIBLE`.
- What a user experiences: the Design Head approves "not feasible" and sales can still quote.
- Fix: require `APPROVED` with outcome `FEASIBLE` or `FEASIBLE_WITH_CHANGES`.

### F-R32TR-015 — High (rank 4): a BoE cannot be tied to one receipt when a PO line has several BoEs or GRNs
- Contract rows: TPO-GRD-24, TPO-T1-24, TPO-T4-17 · Source: **Both**
- Evidence: `rateFor(poLineId)` (FRD `:851`). A BoE line holds a single `grn_line_id` (`D/issues/p9-18.md:18`; `D/docs/DATA-MODEL.md:2082`). COSTED fires on `goods_receipt.posted` (`p9-18.md:21,:24`).
- What a user experiences: a PO line shipped in two consignments has two customs rates and no way to pick between them; a BoE received across two GRNs cannot record its second GRN line.
- Fix: a BoE-line ↔ GRN-line allocation table (qty, value), the BoE line identity passed to the SPI, partial costing, and COSTED once all lines are fully allocated.

### F-R32TR-016 — High (rank 4): "GRN valued at assessable value" cannot be met with a rate alone, and freight may be counted twice
- Contract rows: TPO-GRD-24, TPO-T4-17; CN-15 · Source: **Both**
- Evidence: the BoE stores foreign value + freight + insurance = assessable value (`p9-18.md:18`; FR-769 `:324`). The SPI returns only a rate (`:851`). Core receipt cost is PO price × rate (`C/warehouse/.../WhGoodsReceiptPostingService.java:1063`). On a FOB PO, freight and insurance paid separately would also reach cost through landed cost or a forwarder bill.
- What a user experiences: stock is valued at FOB × customs rate rather than the promised assessable value, or freight lands in cost twice.
- Fix: specify the valuation payload (BoE line, qty, base-currency unit value) and incoterm-driven treatment so each component enters cost once. Record that the customs rate used for duty is not necessarily the Ind AS 21 transaction rate the payable is booked at, and say where the difference goes.

### F-R32TR-017 — High (rank 4): an invoice acknowledgement never marks the manufacturer unit `SOLD`
- Contract rows: TSO-T4-17; MFG PUR-T1-22; ledger `crm:12-19` · Source: **Both**
- Evidence: `D/issues/p10-23.md:9,:20` relies on "the trade / accounting fold supplies invoice ref + date per shipped serial" to move `DISPATCHED → SOLD` and start the warranty. p9-20's ack effect writes only `wht_so_line_billings` (`D/issues/p9-20.md:24`). CN-18 has no unit-registry delivery.
- What a user experiences: warranty never starts from the sale date, and units stay `DISPATCHED`.
- Fix: on ack, call MFG's `UnitRegistryPort` per serial, idempotently. Ledger row 12-19's NO-CHANGE reason does not hold for the sender side: reclassify it as AMEND p9-20.

### F-R32TR-018 — Medium: a PR line with an approved excess can never reach `ORDERED`
- Contract rows: TPR-GRD-10, PR line inventory · Source: GPT
- Evidence: `ORDERED` requires Σ allocation **=** qty − closed_short (`D/docs/contracts/trade-purchase-requisition.contract.md:65`), while R32 allows Σ above it (`:172`). The defect is latent while tolerance stays at 0.
- Fix: `ORDERED` when Σ ≥ qty − closed_short; remaining balance never negative.

### F-R32TR-019 — Medium: `exceed_pr` does nothing at the default tolerance of 0
- Contract row: TPR-GRD-10 · Source: Claude
- Evidence: PRD `:164`: "cannot exceed PR balance unless the user holds po:exceed_pr (tolerance % configurable)". Design: Σ ≤ (qty − closed) × (1 + pct ÷ 100), default 0; "With the default 0 the behaviour is today's" (`D/issues/p9-04.md:66`). The permission is still seeded to purchase managers (p9-07).
- What a user experiences: the purchase manager holds `exceed_pr` but is still refused `422 TRADE_ALLOCATION_EXCEEDS_OPEN`.
- Fix: decide the semantics. Either holders exceed up to a separate holder cap, or a non-zero default. Write it into FR-745 and WH-SC-752.

### F-R32TR-020 — Medium: auto-drafted MRP PRs cannot carry a valid purpose reference
- Contract rows: TPR-T3-03, TPR-GRD-09 · Source: Claude
- Evidence: one PR per site × week, purpose `PRODUCTION_ORDER` with "the planned order's cost object" (FRD `:299`). TPR-GRD-09 needs the `PRODUCTION_ORDER` cost object (a header field), but MRP planned orders are not production orders yet, and one weekly PR covers many orders.
- What a user experiences: the buyer's submit of an auto-drafted MRP PR is refused `422 TRADE_PR_PURPOSE_REFERENCE_REQUIRED`.
- Fix: carry the purpose reference per line, or allow `STOCK` / an MRP purpose without a production order on auto-drafted PRs.

### F-R32TR-021 — Medium: UTGST has no column on proposal lines
- Contract row: TSO-T4-16 · Source: GPT
- Evidence: tax heads include UTGST (`p9-15.md:18`); proposal lines have only `cgst_*`, `sgst_*`, `igst_*`, `cess_*` (`p9-20.md:16`; DATA-MODEL `:2088`).
- Fix: typed tax-head child rows on proposal lines (also carrying the reverse-charge flag).

### F-R32TR-022 — Medium: whole-line BLANKET releases miss `allocateImmediately` and transport details
- Contract rows: TSO-T4-14, TSO-GRD-23; CN-20 · Source: GPT
- Evidence: a whole BLANKET release goes through `firmScheduleLine` (SO contract `:194`). CN-20 extends only `createDemand` / `releaseSchedule` (`:856`), and `DemandScheduleLineCommand.java:13` has neither field.
- Fix: extend `firmScheduleLine` the same way, or use one shared release command.

### F-R32TR-023 — Medium: refused credit checks lose their append-only result row
- Contract row: TSO-GRD-25 · Source: GPT
- Evidence: results are append-only (`p9-17.md:16`), but the check runs inside the approval transaction (`:45`), and a 422 rolls that transaction back. WH-SC-758 still expects two rows (`:50`).
- Fix: write the result in its own committed transaction keyed by attempt and document version.

### F-R32TR-024 — Medium: a custom enquiry can be costed before the Design Head approves feasibility
- Contract rows: TSQ-T4-06, TSQ-GRD-11 · Source: GPT
- Evidence: the PRD says "Approved by Design Head before costing" (`PRD:143`). The gate sits only at quotation submit (`p9-19.md:20,:25`).
- Fix: require approved feasibility before *Request costing* on CUSTOM lines, or record the deviation.

### F-R32TR-025 — Medium: OPEN and BLANKET lines with no quantity have no defined credit candidate, tax value or pending-to-produce
- Contract rows: TSO-GRD-25, TSO-T4-15, TRP-T4-04 · Source: Claude
- Evidence: an OPEN line goes to core with a null quantity (SO contract amendment 2026-10-22, CN-4). FR-765 candidate = "gross value", FR-762 taxes need taxable value, and FR-776 pending-to-produce needs the ordered quantity.
- Fix: define ceiling, firm-only or release-only bases per SO type, for credit, tax and order book.

### F-R32TR-026 — Medium: billing rows have no idempotency key
- Contract row: TSO-T4-17 · Source: Claude
- Evidence: `wht_so_line_billings` is append-only with only `idx(SO line)` (`D/docs/DATA-MODEL.md`, §2.6.13 last row). *Retry* re-hands the same proposal (`p9-20.md:22`).
- What a user experiences: a re-sent ack doubles the billed quantity, so the line shows `BILLED` early and the SO closes early.
- Fix: uk(proposal_id, so_line_id, accounting_document_no).

### F-R32TR-027 — Medium: part serials are missing from invoice lines
- Contract row: TSO-T4-16 · Source: Claude
- Evidence: PRD `:314` asks for "chassis/motor/controller/battery/charger serials per line". The proposal line has one `serial_no`, the shipped unit (`p9-20.md:17`); the bound part serials (p10-21) are not carried.
- Fix: carry the bound component serials per unit, read from MFG's unit registry.

### F-R32TR-028 — Medium: trade has no way to enforce the dispatch checklist guard
- Contract row: TSO-GRD-24 · Source: Claude
- Evidence: the checklist must be done "before the shipment hand-off" (`D/docs/contracts/trade-sales-order.contract.md:262`). Packing and serial picking are core's and happen after release (FR-756; the loading list reads core-picked serials). No CN gives trade a pre-ship veto.
- Fix: a core pre-ship guard SPI, or move the checklist onto core pack confirmation; add it as a new CN.

### F-R32TR-029 — Medium: LR number and vehicle are required at release approval
- Contract row: TSO-GRD-23 · Source: Claude
- Evidence: transporter, vehicle, LR no / date are required at approval (`SO contract:261`). In practice the LR is issued by the carrier at loading, and the vehicle is known at gate / e-way Part-B.
- Fix: require the transporter at approval, and vehicle / LR at shipment or gate-out.

### F-R32TR-030 — Medium: two sources for warranty start
- Contract row: TSR-GRD-07 · Source: Claude
- Evidence: trade uses the item `WARRANTY_DAYS` + core shipment date (`p9-13.md:50`), while MFG sets `warranty_start_date` = sale date (or dispatch) per unit (`p10-23.md:20`).
- Fix: read warranty validity from `UnitRegistryPort` for serial-tracked units.

### F-R32TR-031 — Low: no place of supply for prospect quotations
- Source: Claude · Evidence: a quotation may be on a prospect with only `prospect_state_code` (`p9-08.md` R32 section), but FR-761 sales uses the ship-to address. Fix: use the prospect state when there is no ship-to.

### F-R32TR-032 — Low: `sample_status` is stored as a cache
- Source: Claude · Evidence: `p9-19.md:18` stores the cache, which contradicts TRD-03 and p9-21's trap "nothing is cached in `wht_`". Fix: read it through the SPI.

### F-R32TR-033 — Low: the SO contract's out-of-scope table is stale
- Source: Claude · Evidence: §6 still says "Credit limit, invoice, credit note | refused (FRD §11 R1–R3)" (`D/docs/contracts/trade-sales-order.contract.md:277`), which TSO-GRD-25 and TSO-T4-16 supersede. Fix: amend the row.

### F-R32TR-034 — Low: check-point names do not match
- Source: Claude · Evidence: the table stores `SO_SUBMIT` / `SO_APPROVAL` / `RELEASE_APPROVAL` (`p9-17.md:17`), but the setting says `SO_APPROVAL,DISPATCH_RELEASE` (`:30`). Fix: one vocabulary.

### F-R32TR-035 — Low (ledger): NO-CHANGE row `crm:13.1-04` — reason does not hold
- Source: Claude · Evidence: the reason is "sample status report is P10". P10 has the WS-386 request list and a sample *cost* register tab (`p10-13.md:55`), but no sample-status report under *Trade Reports — Sales* (PRD `13.1`). Fix: reclassify as AMEND (a report leaf via `CN-19` read), or name WS-386 as the report explicitly.

### F-R32TR-036 — Low (ledger): NO-CHANGE row `purchase-inward` gap conflict 7 — wording
- Source: Both · Evidence: the gap file `R32-prd-gap-purchase-inward.md:251` says "Confirm with the client"; the ledger reason states industry practice instead. The behaviour is defensible under D-20 item 1, but the row should be recorded as a deliberate conflict decision with a client question, not as conformance.

## Dropped after verification
- None. Every GPT-only finding's citation was re-opened and held (WhRma statuses, PR inventory `:65`, RFQ `:80/:99`, SO `:104/:111`, TSQ `:176-177`, p9-20 tax columns, SO `:194`, p9-17 `:45`, PRD `:143`).

## Remediation backlog
All rows are design corrections before build. Migration "none" means no migration should be created now; where new DDL is implied, it goes in the owning task's band, `next free in V552000–V552999` (trade) or the core / MFG task's band. No number is invented here.

| Finding | Files to touch | Migration | Shared registries | Parity apply-to | Contract |
|---|---|---|---|---|---|
| 001 | `D/docs/frd/FRD-TRADE.md` (FR-761, CN-16), `D/issues/p9-15.md`, `D/issues/p8-23.md`, `D/docs/DATA-MODEL.md` §2.6.13, `D/docs/DECISIONS.md` (D-20 #5 vs OD-9) | none | accounting adapter port | purchase + sales (M35) | TPO-T4-16, TSQ-T4-07, TSO-T4-15, TRA-T4-05/06 |
| 002 | `D/issues/p8-23.md`, `D/issues/p8-25.md`, `D/issues/p9-20.md`, `D/docs/contracts/accounting-handover.contract.md`, FRD-TRADE CN-18 / M39 | none | `ACCOUNTING_ENVELOPE_KIND` code list | core dispatch / RMA + trade | TSO-T4-16, TSR-T4-06, AHO kinds |
| 003 | `D/issues/p9-20.md`, TSR contract | none | none | SRA ↔ core RMA | TSR-T4-06 |
| 004 | `D/issues/p9-03.md` (seeds), `D/issues/p9-04.md`, `p9-07.md`, `p9-09.md`, TAM contract | none (seed rows in p9-03's V551030) | core approval rules | PR, PO, SO | TAM-GRD-14, TPR-T1-02b |
| 005 | `D/issues/p9-07.md`, TPO + TRA contracts, FRD FR-746 | none | none | award-sourced POs, Direct-PO report (p9-14) | TPO-GRD-21, TRA-T4-03/04 |
| 006 | new core task(s) for CN-15/16/17/20; `D/issues/p10-25.md`, `p10-19.md` (+ an implementer for production progress); FRD-TRADE §12c; `p9-11/15/17/18/19/21.md` | core band, next free | core port registry R.3 | MFG, india, accounting adapter | CN-15…CN-20 |
| 007 | `D/issues/p9-17.md`, `p8-23.md`; file the entry point in `neetub1508/accounting` (label `prd-r32`) | none | credit seam (one) | accounting | TSO-GRD-25/26, TSO-T1-18 |
| 008 | `p9-17.md`, SO contract, FRD FR-765 | none | none | SO + release | TSO-GRD-25 |
| 009 | `p9-09.md`, `p9-17.md`, SO contract | none | none | FIXED / OPEN / BLANKET | TSO-GRD-23…26 |
| 010 | `p9-20.md`, FRD CN-18, core outbound event registry | none | `whb_event_types` | BLANKET / OPEN | TSO-T4-16 |
| 011 | `p9-20.md`, `p9-17.md`, `p9-13.md`, SO + SRA contracts | none | none | REPLACE, WARRANTY_REPLACEMENT | TSO-T4-16/17, TSO-GRD-25 |
| 012 | `p9-20.md`, core gate-out task, FRD §12c (new CN) | none | core gate SPI | india e-way bill | TSO-T4-17 (+ new GRD) |
| 013 | `p9-15.md`, `p9-18.md`, FRD FR-761, ledger BEYOND-7 | none | none | purchase + sales | TPO-T4-16, TSO-T4-15 |
| 014 | `p9-19.md`, TSQ contract | none | none | none (sales only) | TSQ-GRD-11 |
| 015 | `p9-18.md`, DATA-MODEL, TPO contract, CN-15 | next free in V552000–V552999 (allocation table) | none | core GRN | TPO-T1-24, TPO-T4-17 |
| 016 | `p9-18.md`, CN-15, TPO contract | none | none | core GRN costing | TPO-GRD-24, TPO-T4-17 |
| 017 | `p9-20.md`, `p10-23.md`, MFG unit-registry contract, ledger 12-19 | none | UnitRegistryPort | MFG | TSO-T4-17, PUR-T1-22 |
| 018 | `p9-04.md`, TPR contract | none | none | none | TPR inventory, TPR-GRD-10 |
| 019 | `p9-04.md`, `p9-07.md`, FRD FR-745 | none | none | none | TPR-GRD-10 |
| 020 | `p9-04.md`, FRD FR-744, TPR contract | none | none | none | TPR-T3-03, TPR-GRD-09 |
| 021 | `p9-20.md`, `p8-25.md`, DATA-MODEL | next free in V552000–V552999 | none | return proposals | TSO-T4-16 |
| 022 | `p9-09.md`, CN-20, SO contract | none | core demand port | BLANKET | TSO-T4-14 |
| 023 | `p9-17.md`, SO contract | none | none | none | TSO-GRD-25 |
| 024 | `p9-19.md`, TSQ contract | none | none | none | TSQ-T4-06 |
| 025 | `p9-15.md`, `p9-17.md`, `p9-21.md` | none | none | OPEN / BLANKET | TSO-GRD-25, TRP-T4-04 |
| 026 | `p9-20.md`, DATA-MODEL | next free in V552000–V552999 | none | none | TSO-T4-17 |
| 027 | `p9-20.md`, `p8-25.md` | none | none | MFG bindings | TSO-T4-16 |
| 028 | `p9-09.md`, FRD §12c (new CN) | none | core pre-ship SPI | none | TSO-GRD-24 |
| 029 | `p9-09.md`, SO contract | none | none | none | TSO-GRD-23 |
| 030 | `p9-13.md`, SRA contract | none | UnitRegistryPort | MFG | TSR-GRD-07 |
| 031–034 | `p9-15.md`, `p9-19.md`, SO contract, `p9-17.md` | none | none | none | as named |
| 035–036 | ledger `L` rows `crm:13.1-04`, `purchase-inward` gap conflict 7 | none | none | none | none |

## Parity (C10)
- Mobile: none — out of scope per D-20 item 5 (tracked as one `needs-client-decision` issue). Not a finding.
- Dealer vertical (dealer / automotive / services / accessories / insurance): fenced per D-20 item 4. No finding proposes reuse; the customer 360 and warranty rows respect the fence.
- Siblings sharing these seams: warehouse core (p8-23 / p8-25 / p8-30, outbound / RMA), warehouse-india (tax reference), warehouse-manufacturing (p10-19 / p10-23 / p10-25), the accounting adapter. F-002, F-006, F-007 and F-017 have to be fixed on both sides of each seam at once.

## In code, not in contract
- Accounting's APPROVE mode raises its own `CREDIT_LIMIT_OVERRIDE` approval (`AccCreditCheckService.java:186-190`), which no trade row describes (F-007).
- Accounting's exposure already includes open accounting SOs and draft invoices, and subtracts advances (`AccCreditExposureCalculator.java:87`). CN-17 must state which buckets trade adds (F-008).
- warehouse-india's HSN master is reference-only by design (`V540110:32-38`) (F-001).

## Contract quality
- WS-317, WS-318 and WS-319 have no T5 screen rows in any trade contract; WS-314/315/316 have only one-line rows. Grid, filter, export and tile conformance cannot be checked until they exist.
- R32 sections add no T2 rows for the new permissions (`approve_credit_override`, `wht_document_shares:send`, `wht_accounting_proposals:retry`, `wht_bills_of_entry:*`, `wht_feasibility_reviews:*`, `create_without_pr`, `exceed_pr`), so C5 could not be run.
- Could not verify:
  - whether rate-contract-sourced PO lines count as "awarded" for FR-746;
  - the margin formula basis (price or cost) for WH-SC-762's 10.3 %;
  - the timing of the `close_rule` default when an accounting target is added to a running install.
- Ledger: 18 NO-CHANGE rows reviewed. 12-19, 13.1-04 and purchase-inward gap conflict 7 are flagged above; BEYOND-8 holds (assets has `AssetPurchaseOrder`); the dealer / services / mobile fences hold. Purchase BEYOND-2…6 are absent from this ledger (inward / quality, presumably in the stores ledger — not verified).
- GitHub: #173, #174 and #175 are open but their bodies carry no R32 scope. R32 scope lives in the p8-23/24/25 files only.

## Referred to standards reviewer
- Trade money columns are specified as `DECIMAL(19,4)` (p9-15) where CLAUDE.md keeps non-accounting modules on `DECIMAL(15,2)`. This is a design-set precision decision (DATA-MODEL §5.1) for the standards gate to rule on.

## Fix record (2026-10-25)
Paths relative to `D/`; `L` = `r32-ledger-trade.tsv`. Core carriers (`P8-26`, `p8-23`, `p8-25`) and MFG tasks (`p10-*`) are edited by their own fixers; the trade side names the D-21 SPIs they declare. FRD-TRADE §12c `CN-15`…`CN-20` now name carrier `P8-26`; `CN-21` (gate-out guard) and `CN-22` (pre-ship guard) are new.

| Finding | Files changed | State |
|---|---|---|
| F-R32TR-001 | FRD-TRADE FR-761, CN-16, M35, R5, TRD-06; `issues/p9-15.md`; TPO / TRA / TSQ / TSO contracts (T4-16, T4-05, T4-07, T4-15); DATA-MODEL §2.6.13; GLOBAL-SETTINGS-DECISIONS OD-9; SCENARIO WH-SC-755; epic p9; L `purchase-inward:5.3-15` | done (`D-21` item 1: accounting tax determination via the adapter, `OD-9` stands; effective date in the request) |
| F-R32TR-002 | FRD FR-773, FR-775, CN-18, M39; `p9-20.md`; TSO-T4-16, TSR-T4-06; DATA-MODEL; SCENARIO WH-SC-766/767; L 12-09…12-11, 12-25 and the crm conflict row on SQ / SO ownership | done (`D-21` item 2: core sole producer, trade enriches; core kinds are `p8-23`'s) |
| F-R32TR-003 | FRD FR-775; `p9-20.md`; TSR-T4-06 | done (core `CREDIT_NOTE_PROPOSAL` per receipt + disposition) |
| F-R32TR-004 | FRD FR-740, FR-744; `p9-03.md`, `p9-04.md`; TAM-GRD-14, TPR-T1-02b; SCENARIO WH-SC-750 | done (`INCLUDES` default for PR/PO/SO/SQ install rules + seeded `from_approved_mr` rule; clean-install acceptance) |
| F-R32TR-005 | FRD FR-746; `p9-07.md`; TPO-GRD-21; TRA §7 | done |
| F-R32TR-006 | FRD CN-15…CN-20, FR-757, FR-772, M40; `p9-11/15/17/18/19/21.md`; TSQ contract | done (trade side: carrier `P8-26`, MFG names `CostEstimatePort` / `SampleRequestPort` adopted; progress-query implementer is MFG's fixer) |
| F-R32TR-007 | FRD FR-765, FR-767, CN-17; `p9-17.md`; TSO-GRD-25/26; L 4A-26 | done (one `WhbCustomerCreditProvider`, check-only entry point, mode mapping) — filing the `neetub1508/accounting` `prd-r32` issue is an owner action (no GitHub in this wave) |
| F-R32TR-008 | FRD FR-765; `p9-17.md`; TSO-GRD-25; L crm BEYOND-7 | done |
| F-R32TR-009 | FRD FR-755; `p9-09.md`, `p9-17.md`; TSO-GRD-27 (new) | done (`DISPATCH_ONLY` releases for FIXED + pre-ship veto `CN-22`) |
| F-R32TR-010 | FRD FR-773, CN-18; `p9-20.md`; TSO-T4-16; SCENARIO WH-SC-766 | done (shipment-level `INVOICE_REQUEST`) |
| F-R32TR-011 | FRD FR-758, FR-765, FR-773, FR-774; `p9-13.md`, `p9-17.md`, `p9-20.md`; TSO-GRD-25/26, TSO-T4-16/17, TSR-GRD-07 | done |
| F-R32TR-012 | FRD FR-773, CN-21 (new); `p9-20.md`; TSO-GRD-28 (new); SCENARIO WH-SC-766 | done |
| F-R32TR-013 | FRD FR-753, FR-761, CN-16; `p9-15.md`; TPO-T4-16, TSO-T4-15, TRA-T4-05; L `purchase-inward:BEYOND-7` | done |
| F-R32TR-014 | FRD FR-771; `p9-19.md`; TSQ-GRD-11; SCENARIO WH-SC-761 | done |
| F-R32TR-015 | FRD FR-768…FR-770, CN-15; `p9-18.md`; TPO-GRD-24, TPO-T1-24, TPO-T4-17; DATA-MODEL (`wht_bill_of_entry_line_receipts`, `V552030`); SCENARIO WH-SC-760 | done |
| F-R32TR-016 | FRD FR-768, CN-15; `p9-18.md`; TPO-GRD-24; SCENARIO WH-SC-760 | done (PO price × customs rate; freight / insurance once by incoterm; Ind AS 21 difference is accounting's) |
| F-R32TR-017 | FRD FR-774; `p9-20.md`; TSO-T4-17; L 12-19 → AMEND p9-20 | done on the trade side (`D-21` item 3: MFG consumes `INVOICE_ACKNOWLEDGED` itself; `p10-23` is MFG's fixer) |
| F-R32TR-018 | FRD FR-745; `p9-04.md`; TPR §1.1 line inventory | done |
| F-R32TR-019 | FRD FR-745; `p9-04.md`; TPR-GRD-10; SCENARIO WH-SC-752 | done (holder cap `warehouse.trade.pr.exceed_pr_max_pct`, default 10) |
| F-R32TR-020 | FRD FR-744; `p9-04.md`; TPR-GRD-09, TPR-T3-03 | done (`STOCK` + `mrp_planned_order_ref`) |
| F-R32TR-021 | `p9-20.md`; DATA-MODEL (`wht_accounting_proposal_line_taxes`, `V552050`) | done (trade side; `p8-25` return payload is core's fixer) |
| F-R32TR-022 | FRD FR-754, CN-20; `p9-09.md`; TSO-T4-14 | done |
| F-R32TR-023 | FRD FR-765; `p9-17.md`; TSO-GRD-25; DATA-MODEL; SCENARIO WH-SC-758 | done |
| F-R32TR-024 | FRD FR-771; `p9-19.md`; TSQ-GRD-11, TSQ-T4-06 | done |
| F-R32TR-025 | FRD FR-761, FR-765, FR-776; `p9-15.md`, `p9-17.md`, `p9-21.md`; TSO-GRD-25, TSO-T4-18, TRP-T4-04 | done |
| F-R32TR-026 | FRD FR-774; `p9-20.md`; TSO-T4-17; DATA-MODEL | done |
| F-R32TR-027 | FRD FR-773; `p9-20.md`; DATA-MODEL (`wht_accounting_proposal_line_part_serials`, `V552050`); L 12-02 | done (via core-declared `UnitRegistryPort`) |
| F-R32TR-028 | FRD FR-756, CN-22 (new); `p9-09.md`; TSO-GRD-24; SCENARIO WH-SC-765 | done |
| F-R32TR-029 | FRD FR-755; `p9-09.md`; TSO-GRD-23 | done |
| F-R32TR-030 | FRD FR-758; `p9-13.md`; TSR-GRD-07 | done (core serial warranty fields written by the MFG registry, `D-21` item 3) |
| F-R32TR-031 | FRD FR-761; `p9-15.md`; TSQ-T4-07 | done |
| F-R32TR-032 | FRD FR-772; `p9-19.md`; TSQ-GRD-13; DATA-MODEL §2.6.13 | done |
| F-R32TR-033 | TSO §6 | done |
| F-R32TR-034 | FRD FR-765; `p9-17.md` | done (`SO_SUBMIT` / `SO_APPROVAL` / `DISPATCH_RELEASE`) |
| F-R32TR-035 | `p9-21.md`; TRP-T4-05 (new); FRD FR-776; L 13.1-04 → AMEND p9-21 | done |
| F-R32TR-036 | L `purchase-inward` PO-numbering row reworded as a deliberate conflict decision with a client confirmation | done |

36 done · 0 superseded. Migrations: no new version — new DDL sits in versions the owning tasks already claim (`V552030` p9-18, `V552050` p9-20, `V550030` / `V551041` p9-04, `V550080` / `V551091` p9-09, `V551030` p9-03, `V552060` / `V552061` p9-21). DATA-MODEL inventory `wht_` 90 → 93, total 565 → 568.
