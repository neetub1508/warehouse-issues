TITLE: [Warehouse] [Finding] Real-world WR6-04 · Put an overdue client's outward releases on credit hold
LABELS: task,warehouse,gap-real-world,phase-p5,warehouse-3pl
issue: 754
---
Part of #10 · Module **`warehouse-3pl`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #17, #684, #258 · Source: real-world gap check 2026-11-03, lane WR6

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Holding the goods is a 3PL's main collection lever. It has a particular lien on goods for services rendered on them, and a general lien if the contract grants one. Today `credit_limit` is stored and never read, and SUSPENDED blocks no outward movement. A defaulting client keeps withdrawing stock until nothing is left to hold.

## Scope

Add an owner-level outward hold in base: a hold flag + reason + set-by, written by warehouse-3pl, read by the release/pick/dispatch guards. Set the hold from AR overdue days or exposure over the credit limit. Exposure = open approved runs + unbilled events, plus AR balance when accounting is installed. Add a supervisor override with a reason. Receipts and storage continue.

## Acceptance

- A client past the overdue threshold cannot release a new outward order. The refusal names the hold, and storage billing continues.
- A supervisor override with a reason lets one order through, and the override is audited.
- Clearing dues (an AR ack, or manual release where no accounting) lifts the hold. Portal users see "on hold".

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

s.170/171 Contract Act: https://www.casemine.com/in/column/an-analysis-of-section-171-of-the-indian-contract-act,-1872:-the-general-lien/view. Code: `Wh3plClient.creditLimit` is used only in the mapper and query sort. `SUSPENDED` appears only in 3PL repositories, and base `whb_owners` has no hold column. GDN-R31 asks for a decision on suspension, not a credit hold. The trade module has the pattern: p9-17 credit/overdue check with override (CN-17).

## Global setting

`WAREHOUSE_3PL_CREDIT_HOLD_MODE` default=BLOCK_WITH_OVERRIDE alternatives=WARN, OFF; `WAREHOUSE_3PL_CREDIT_HOLD_OVERDUE_DAYS` default=30

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#17
