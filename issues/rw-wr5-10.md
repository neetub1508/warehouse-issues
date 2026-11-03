TITLE: [Warehouse] [Finding] Real-world WR5-10 · Correct the bonded interest rule: all clause (c) goods, from the s.60 order
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-india
issue: 749
---
Part of #8 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **PLANNED-WRONG** · Related: #51 · Source: real-world gap check 2026-11-03, lane WR5

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

The plan and seeds say interest after 90 days applies "for some categories" and leave `interest_applicable` a free per-line choice. Under s.61(2), interest runs on **every** clause (c) good (all goods other than EOU, s.65 and clause (a)/(b) capital goods) from day 91 after the warehousing order under s.60(1). A clerk who leaves the box unticked understates the duty-plus-interest liability shown at ex-bond.

## Scope

Default `interest_applicable` from the licence kind (BONDED or s.58 trading: true; MOOWR, EOU and capital goods: false), with an override that needs a reason. Anchor `interest_free_until` on the s.60(1) order date where captured. Correct the text in P4-07, the EPIC and the localisation pack.

## Acceptance

- A BONDED BoE line defaults to interest applicable, with free-until = order date + 90
- A MOOWR line defaults to not applicable
- An override is audited with its reason

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

[Rajasthan HC, Acme Aklera, Sept 2026](https://www.livelawbiz.com/customs/high-court/no-interest-on-customs-duty-for-capital-goods-kept-in-bonded-warehouse-549930): s.61(2) charges interest only on clause (c) goods, which form the residuary category. Plan text: issues/p4-07.md:73; V540140:40, V541113:40; `interest_applicable BOOLEAN` V540140:332.

## Depends on

#51
