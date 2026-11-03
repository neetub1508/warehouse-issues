TITLE: [Warehouse] [Finding] Real-world WR7-05 · Re-base goods on approval on s.31(7) and invoice at six months
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-india
issue: 766
---
Part of #8 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **PLANNED-WRONG** · Related: #45, #140 · Source: real-world gap check 2026-11-03, lane WR7

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Goods sent on approval are not a supply between distinct persons. They are a supply to the customer whose invoice falls due on acceptance or at six months from removal, whichever is earlier. Citing Schedule I and Rule 28 points valuation at open market value instead of the agreed price. "An obligation raised" at month six leaves no invoice, so output tax for that month is missed. Partial acceptance (keep 7, return 3) also needs a part invoice.

## Scope

Correct the citations in #45 and the pack. On acceptance, or when the 6-month clock (counted from the removal date) expires, emit an `INVOICE_REQUEST` handover at the challan line's agreed price for the quantity not yet returned. Support partial acceptance and return per line. A return after an invoice becomes a credit-note proposal, not a receipt against the challan.

## Acceptance

- On the day 6 months after removal, an un-returned approval line produces an `INVOICE_REQUEST` for its open quantity
- Accepting 7 of 10 invoices 7 and leaves 3 on the clock
- A return after invoicing raises a credit-note proposal
- No r.28 valuation is applied to an approval line

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

[S31] s.31(7); [C10] Circular 10/10/2017 (r.55(1)(c) challan, invoice on acceptance). Plan: #45 l.50 cites "Schedule I and r.28 (deemed supply between distinct persons and its valuation)" and l.23-25 "an obligation raised".

## Depends on

#45
