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

## Design-set correction (done 2026-11-03, docs only)

**Statute, checked against the law in force today.** Customs Act 1962 s.61 (substituted by Finance Act 2016 s.128, in force 14 May 2016): s.61(1)(a) capital goods and (b) other goods of a 100% EOU, a specified STP/EHTP unit or a s.65 warehouse stay "till clearance" / "till consumption or clearance"; s.61(1)(c) *all other goods* stay one year from the proper officer's s.60(1) order, extendable by the Commissioner a year at a time. s.61(2): on clause (c) goods kept beyond ninety days from the s.60(1) order, interest runs from the end of those ninety days until duty is paid, at the rate the Central Government fixes under s.47, on the duty payable at clearance; the proviso lets the Board waive it in exceptional cases, exempt notified classes, or start it from the s.60(1) order date for specified classes. Sources: [courtbook.in s.61](https://courtbook.in/customs-act1962/section-61) (unofficial reproduction; confirm against indiacode.nic.in / CBIC), [Rajasthan HC, Acme Aklera, Sept 2026](https://www.livelawbiz.com/customs/high-court/no-interest-on-customs-duty-for-capital-goods-kept-in-bonded-warehouse-549930) (interest confined to clause (c)). The 1996-2003 text tied the 90-day rule to clause (b); the 2016 text is the one in force.

**Corrected in:** `issues/p4-07.md` (statutory table row), `issues/06-EPIC-p4.md` (row), `docs/INDIA-LOCALISATION-PACK.md` (two rows). The seeds `V540140:40` and `V541113:40` are classic files and are owed (below).

**Rule adopted (DECISION RULE: one right answer, no setting).** Interest applies to every clause (c) good. `interest_applicable` defaults from the licence kind: BONDED and s.58 trading licences true; MOOWR (s.65), EOU and clause (a)/(b) capital goods false. `interest_free_until` defaults to the s.60(1) order date + 90 days where the order date is captured. An override of either needs a reason and is audited. The rate and any Board waiver/class exemption stay data (admin setting), not code.

**Code owed (build, not done here)**
1. Migration (next free in the `warehouse-india` band): default of `interest_applicable` derived from the licence kind at BoE-line create; store `section_60_order_date`; `interest_free_until` = order date + 90; override reason column.
2. Correct the comments/seed text at `V540140:40` and `V541113:40` (text only; no edit of an applied migration - correct in a new migration or comment-only per the checksum rule).
3. BoE line service: apply the default, refuse an override without a reason, audit it; ex-bond duty-plus-interest preview uses the clause (c) rule.
4. Tests for the three acceptance cases.

## Depends on

#51
