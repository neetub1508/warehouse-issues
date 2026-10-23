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

## The contracts in this directory — 28

**Core (3)** — [`movement-post-reverse`](movement-post-reverse.contract.md) ·
[`receipt-qc-putaway`](receipt-qc-putaway.contract.md) ·
[`accounting-handover`](accounting-handover.contract.md) (accounting is deferred by `D-16` / `RN-054`;
the contract stays on record).

**Re-target (`DECISIONS.md` `D-16`)** — each set is specified by its area requirements file in
[`../frd/`](../frd/), which carries its `FR`, `WH-SC`, `WS` and `OD` rows and the R29 dispositions.
`FRD-REM` (P7, removal) has no workflow contract of its own.

| Area | Requirements | Contracts |
|---|---|---|
| **STORES** · core `warehouse`, P8 (7) | [`FRD-STORES.md`](../frd/FRD-STORES.md) — also the authoritative port & seam registry | [`gate-entry`](gate-entry.contract.md) · [`grn-bill-match`](grn-bill-match.contract.md) · [`incoming-inspection-sampling`](incoming-inspection-sampling.contract.md) · [`mrn-authorisation`](mrn-authorisation.contract.md) · [`material-requisition`](material-requisition.contract.md) · [`store-issue-return`](store-issue-return.contract.md) · [`po-schedule-port`](po-schedule-port.contract.md) |
| **TRADE** · `warehouse-trade`, P9 (10) | [`FRD-TRADE.md`](../frd/FRD-TRADE.md) | [`trade-purchase-requisition`](trade-purchase-requisition.contract.md) · [`trade-rfq-award`](trade-rfq-award.contract.md) · [`trade-rate-contract`](trade-rate-contract.contract.md) · [`trade-purchase-order`](trade-purchase-order.contract.md) · [`trade-sales-enquiry-quotation`](trade-sales-enquiry-quotation.contract.md) · [`trade-sales-order`](trade-sales-order.contract.md) · [`trade-sales-return-authorisation`](trade-sales-return-authorisation.contract.md) · [`trade-order-amendment`](trade-order-amendment.contract.md) · [`trade-approval-matrix`](trade-approval-matrix.contract.md) · [`trade-counterparty-evaluation`](trade-counterparty-evaluation.contract.md) |
| **MFG** · `warehouse-manufacturing`, P10 (8) | [`FRD-MFG.md`](../frd/FRD-MFG.md) | [`mfg-bom`](mfg-bom.contract.md) · [`mfg-production-order`](mfg-production-order.contract.md) · [`mfg-material-staging-issue`](mfg-material-staging-issue.contract.md) · [`mfg-production-receipt`](mfg-production-receipt.contract.md) · [`mfg-qc-rework`](mfg-qc-rework.contract.md) · [`mfg-subcontracting`](mfg-subcontracting.contract.md) · [`mfg-mrp`](mfg-mrp.contract.md) · [`mfg-costing-close`](mfg-costing-close.contract.md) |
| **REM** · P7 | [`FRD-REM.md`](../frd/FRD-REM.md) | — |
