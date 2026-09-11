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
- The invariants (`L-1`…`L-14`) the workflow must not break, and the scenarios (`WH-SC-nnn`) that prove
  it.

## The first ones to write

In order, as their tasks land: the **movement post/reverse** contract (P0 — everything else writes
through it), **receipt → QC → putaway** (P1), **allocation → pick → pack → ship** (P2), **count →
variance → approval → adjustment** (P2), **the three-leg transfer** (P2), and **the accounting
handover** including the rejected-handover queue (P2).
