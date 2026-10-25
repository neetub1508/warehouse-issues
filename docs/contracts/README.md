# Functional contracts

A **functional contract** is the machine-checkable behaviour spec for one workflow. The
`functional-reviewer` agent reads these to prove that changed code does what the workflow says it does
— state-machine reachability, guards, time-driven rules, cross-entity effects, and the screen
contract. It is the complement to the `reviewer` agent, which proves *how* code is written; this
proves *what it does*.

**Requirements contracts are specified before implementation.** [Global settings and resolved behaviour](../GLOBAL-SETTINGS-DECISIONS.md) defines the current decisions and acceptance cases. Workflow contracts add machine-checkable detail as tasks land; implementation verifies the agreed answer instead of asking the same product question again.

## When to write one

Write `<workflow>.contract.md` here **as part of the task that builds the workflow**, not afterwards,
for any workflow that has:

- a state machine with more than two states (receipt lifecycle, count lifecycle, transfer legs, wave
  release, billing run, e-way bill lifecycle), or
- a guard that must hold across entities (allocation against available stock, period lock, negative
  stock policy, owner segregation, duty-status segregation), or
- a time-driven rule (reservation expiry, shelf life and FEFO, job-work return window, storage billing
  anniversaries, in-transit ageing), or
- an irreversible effect (posting a movement, closing a period, approving a count variance,
  handing over to accounting).

## What one contains

- The states, the legal transitions, and the ones that must be **unreachable** — with the guard that
  makes them so.
- Every guard, as a predicate over named columns, and what a violation returns to the user: **the
  field and the message shape**, not just "an error". This matters here more than usual — a deferred
  constraint trigger raises at `COMMIT`, outside every `@Transactional` boundary, so no service `catch`
  can translate it and the message never reaches a form field. The contract is where that obligation
  is written down per workflow.
- The cross-entity effects: what else moves when this moves, and what must not.
- The time rules, with the clock they read and what happens when it is crossed while the record is in
  each state.
- The screen contract: what each state shows, which actions it offers, and which permission gates each.
- The invariants (`L-1`…`L-15`) the workflow must not break, and the scenarios (`WH-SC-nnn`) that prove
  it.

## The first ones to write

In order, as their tasks land: the **movement post/reverse** contract (P0 — everything else writes
through it), **receipt → QC → putaway** (P1), **allocation → pick → pack → ship** (P2), **count →
variance → approval → adjustment** (P2), **the three-leg transfer** (P2), and **the accounting
handover** including the rejected-handover queue (P2).

## The contracts in this directory — 52

Each set is specified by its requirements file (`../WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` for core, `../frd/` for the
re-target areas of `DECISIONS.md` `D-16`), which carries its `FR`, `WH-SC`, `WS` and `OD` rows.
**Coverage rule (`tools/check-design-set.py` check 14, R30 `CP-FR-007` / `D-17` item a):** every active FR must be
cited in the `Source` (or an `FR-`) cell of at least one rule row here; a §0 baseline range, an out-of-scope line,
an amendment, an open row or the invariants section does not count.
**Linking rule (check 15):** every live (not VOID) task file carries a `**Functional contracts:**` line under its
`Part of` header naming every contract whose rule rows cite an FR the task closes in `IMPLEMENTATION-PLAN.md` §2, plus
the contracts that own its workflow. Open rows across all contracts are collected in
[`../reviews/R30-contract-open-items.md`](../reviews/R30-contract-open-items.md).

| Contract | Scope |
|---|---|
| **Core ledger** | |
| [`movement-post-reverse`](movement-post-reverse.contract.md) | the stock ledger's single writer: movement post / reverse, owner segregation, the movement port |
| [`receipt-qc-putaway`](receipt-qc-putaway.contract.md) | inbound receipt → QC → putaway, and receipt reversal; layered truth, receiving session, ASN, reconciliation cases, supplier return, free quantity, three-way match (§6.8) |
| [`accounting-handover`](accounting-handover.contract.md) | envelope → queue → Stock-to-GL reconciliation (accounting deferred by `D-16` / `RN-054`; kept on record) |
| **Core masters and control (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6, R30 `CP-FR-007`)** | |
| [`item-master`](item-master.contract.md) | item lifecycle, UoM conversion guards, identification, packaging, supersession as engineering change (§6.3) |
| [`facility-branch-link`](facility-branch-link.contract.md) | identity and facility model; dated branch links, serving-branch rule, transfer-request ladder, inter-company (§6.4, §6.28) |
| [`lot-serial-status`](lot-serial-status.contract.md) | lots, serials, LPNs, stock status and duty status; expiry / retest / hold clocks (§6.5) |
| [`counterparty-master`](counterparty-master.contract.md) | the core counterparty master and its roles (§6.7) |
| [`access-scope`](access-scope.contract.md) | permissions, branch / site scope, maker ≠ checker, approval levels, cost suppression by actor (§6.23) |
| [`cycle-count`](cycle-count.contract.md) | count → variance → approval → adjustment (§6.9) |
| [`stock-transfer`](stock-transfer.contract.md) | the three-leg transfer, in-transit ageing and the bin-to-bin move (§6.9) |
| [`reservation-allocation`](reservation-allocation.contract.md) | reservations, allocation against available stock, reservation expiry, the availability API (§6.10) |
| [`outbound-despatch`](outbound-despatch.contract.md) | demand order → wave → pick → pack → ship → confirm delivery; edit-after-release matrix; seals at load and unload (§6.11) |
| [`task-execution-printing`](task-execution-printing.contract.md) | task execution, scanning (web) and print jobs (§6.12) |
| [`costing-valuation`](costing-valuation.contract.md) | cost layers, valuation, revaluation and period close; handover posting status, cut-off columns, transfer price vs cost (§6.13) |
| [`replenishment`](replenishment.contract.md) | replenishment and reorder suggestions (§6.14) |
| [`vas-work-order`](vas-work-order.contract.md) | kitting, assembly and value-added-service work orders (§6.15) |
| [`returns-rma`](returns-rma.contract.md) | core RMA, return receipt and grading, supplier claim register (§6.16) |
| [`reports-kpis`](reports-kpis.contract.md) | report and KPI screens, frozen KPI definitions, uncached filter-aware strips, health signals (§6.22) |
| [`import-go-live`](import-go-live.contract.md) | imports, opening balances and go-live (§6.24) |
| [`outbox-events`](outbox-events.contract.md) | events, the outbox, delivery / retry / dead-letter, API clients (§6.19) |
| [`module-contract`](module-contract.contract.md) | the adapter / sibling-module contract against `warehouse-adapter-example`, open registries (§6.20, §6.21) |
| [`non-functional`](non-functional.contract.md) | non-functional requirements carried as checkable rules (§6.25) |
| **Core siblings (`warehouse-3pl`, `warehouse-india`)** | |
| [`3pl-billing`](3pl-billing.contract.md) | 3PL client, meter, rating and the billing run; storage anniversaries (§6.17) |
| [`india-movement-documents`](india-movement-documents.contract.md) | India movement documents: e-way bill lifecycle, e-way-conditional gate pass, job-work return window (§6.18) |
| **STORES · core `warehouse`, P8 — [`FRD-STORES.md`](../frd/FRD-STORES.md) (also the authoritative port & seam registry)** | |
| [`gate-entry`](gate-entry.contract.md) | gate entry register, weighment link, and RGP / NRGP gate passes with the overdue clock |
| [`grn-bill-match`](grn-bill-match.contract.md) | GRN against the supplier bill: billed vs received vs accepted, short claim and excess |
| [`incoming-inspection-sampling`](incoming-inspection-sampling.contract.md) | inspection sampling (bands, fixed, %, AQL), plan assignment, polymorphic QC source |
| [`mrn-authorisation`](mrn-authorisation.contract.md) | Material Receipt Note: authorisation into stores, availability, print |
| [`material-requisition`](material-requisition.contract.md) | material requisition (indent): approval, reservation, partial issue, closure, PR hand-off |
| [`store-issue-return`](store-issue-return.contract.md) | store issue to consumption with a cost object, store return, stores registers (WS-277) |
| [`po-schedule-port`](po-schedule-port.contract.md) | PO type and schedule lines, the purchase-order, demand-order and RMA-creation ports |
| [`document-approval`](document-approval.contract.md) | **R32 / `D-20` item 18:** the one approval engine for every document type — rules, levels, maker ≠ checker, append-only actions with band used, escalation, e-mail / WhatsApp, amendment re-approval, My Approvals (`p8-30`) |
| [`quality-ncr-capa-deviation`](quality-ncr-capa-deviation.contract.md) | **R32:** defect codes, NCR / CAPA with closure approval, deviation (accept under deviation) with usage cap, quality registers (`p8-17`, `p8-18`, `p8-21`) |
| [`qc-inspector-calibration`](qc-inspector-calibration.contract.md) | **R32:** inspector authorisation by item group / stage, inspector ≠ GRN maker or own producer, instrument calibration gating results (`p8-19`, `p8-20`) |
| [`status-stores`](status-stores.contract.md) | **R32 (`D-20` #16):** status kept as the control; optional dedicated location per non-allocatable status shown as a store (`p8-22`) |
| **TRADE · `warehouse-trade`, P9 — [`FRD-TRADE.md`](../frd/FRD-TRADE.md)** | |
| [`trade-purchase-requisition`](trade-purchase-requisition.contract.md) | purchase requisition → consolidation → conversion; also the trade module boundary (FR-540) |
| [`trade-rfq-award`](trade-rfq-award.contract.md) | RFQ → vendor quotation → comparative statement → award |
| [`trade-rate-contract`](trade-rate-contract.contract.md) | rate contracts and price lists, price resolution |
| [`trade-purchase-order`](trade-purchase-order.contract.md) | purchase order (FIXED / OPEN / BLANKET), schedules, releases, acknowledgement, hand-off to stores |
| [`trade-sales-enquiry-quotation`](trade-sales-enquiry-quotation.contract.md) | sales enquiry → customer quotation → won / lost / regretted |
| [`trade-sales-order`](trade-sales-order.contract.md) | sales order, delivery schedule, dispatch releases, acknowledgement, short-close |
| [`trade-sales-return-authorisation`](trade-sales-return-authorisation.contract.md) | sales return authorisation → core RMA, and the purchase-side replacement twin |
| [`trade-order-amendment`](trade-order-amendment.contract.md) | order amendment and versioning for POs and SOs |
| [`trade-approval-matrix`](trade-approval-matrix.contract.md) | maker–checker approval matrix and My Approvals for every trade document — since R32 (`D-20` item 18) the trade **consumer** of [`document-approval`](document-approval.contract.md) |
| [`trade-counterparty-evaluation`](trade-counterparty-evaluation.contract.md) | trade profiles, AVL, customer part approval, T&C templates, numbering, vendor / customer rating |
| [`trade-reports`](trade-reports.contract.md) | trade reports pack (WS-312, eight read-only grids) |
| **MFG · `warehouse-manufacturing`, P10 — [`FRD-MFG.md`](../frd/FRD-MFG.md)** | |
| [`mfg-bom`](mfg-bom.contract.md) | BOM versions, alternatives, phantoms, outputs, operations, explosion; MFG registries and screen standards |
| [`mfg-production-order`](mfg-production-order.contract.md) | production order lifecycle: create, release, hold, complete, reopen, close hand-off |
| [`mfg-material-staging-issue`](mfg-material-staging-issue.contract.md) | material to production: request, staging to line-side, issue / return through core, WIP models |
| [`mfg-production-receipt`](mfg-production-receipt.contract.md) | production receipt (backflush, outputs, scrap, genealogy) and its reversal |
| [`mfg-qc-rework`](mfg-qc-rework.contract.md) | operation confirmations, in-process and final QC, rework |
| [`mfg-subcontracting`](mfg-subcontracting.contract.md) | subcontracting / job work out |
| [`mfg-mrp`](mfg-mrp.contract.md) | planning masters, MRP runs, proposals, exceptions, capacity load |
| [`mfg-costing-close`](mfg-costing-close.contract.md) | production costing, settlement and close |
| [`mfg-bonded-issue`](mfg-bonded-issue.contract.md) | bonded / MOOWR stock issued to production and sent for job work (`warehouse-india` + MFG) |
| **REM · P7 — [`FRD-REM.md`](../frd/FRD-REM.md)** | |
| [`rem-removal`](rem-removal.contract.md) | what must not exist after P7 (absence checks per removed artefact class), the dual-use renames, and what must keep working |
