TITLE: [Warehouse] [Finding] Real-world WR7-08 · Complete the Rule 28 transfer-valuation bases
LABELS: task,warehouse,gap-real-world,phase-p2
issue: 769
---
Part of #5 · Module **`warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **PLANNED-WRONG** · Related: none · Source: real-world gap check 2026-11-03, lane WR7

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

The method stored on a cross-GSTIN transfer must be defensible at audit. Two of the bases branches actually use cannot be recorded today:
- the second proviso (invoice value is deemed open market value when the receiving branch gets full credit), which is the commonest;
- the first proviso, 90% of the recipient's onward price.
Staff will pick "COST" or "TRANSFER_PRICE", which misstates the legal basis.

## Scope

Add catalogue rows `R28_INVOICE_DEEMED_OMV_FULL_ITC` and `R28_NINETY_PCT_ONWARD_PRICE`, and label `COST_PLUS_PERCENT` as Rule 30 (cost + 10%), all through registryLabel. The 90% basis needs the reference onward price recorded.

## Acceptance

- A transfer can record the deemed-OMV basis and prints it on the transfer document
- The 90% basis refuses a save without a reference onward price
- The labels translate in en, fr and hi

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

[C210] confirms the second proviso. Code values found: `COST`, `COST_PLUS_FIXED`, `COST_PLUS_PERCENT`, `OPEN_MARKET_VALUE`, `TRANSFER_PRICE` (grep over warehouse migrations). There is no 90% or deemed-OMV value.
