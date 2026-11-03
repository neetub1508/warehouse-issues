TITLE: [Warehouse] [Finding] Real-world WR6-05 · Add a custody claim register for client goods lost or damaged in storage
LABELS: task,warehouse,gap-real-world,phase-p5,warehouse-3pl
issue: 755
---
Part of #10 · Module **`warehouse-3pl`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #48, #690, #123, #684 · Source: real-world gap check 2026-11-03, lane WR6

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Damage, pilferage and count shortfalls on client stock are the commonest 3PL dispute, and they come with money. The contract caps liability (declared value, per-unit or per-kg cap, or a multiple of fees), and the 3PL claims on its insurer. The settlement is compensation, not a supply (no GST). A billing dispute or a write-off adjustment records none of this, and the client's loss figure has no audit trail.

## Scope

Add `wh3_custody_claims`: client, source movement (damage status change / count variance / adjustment), qty, the client's declared value, the computed contractual cap, status ladder (raised → surveyed → accepted/rejected → settled), insurer claim ref, survey document, settlement amount. Settle as a payable proposal to accounting flagged NON_SUPPLY_COMPENSATION, never a negative billable event. Add an annual shrinkage allowance per client: variances within the allowance are not claimable.

## Acceptance

- Approving a damage adjustment on client stock offers to open a claim pre-filled with qty and lot.
- Settlement = min(declared value, contractual cap), with the arithmetic shown. It emits a compensation envelope, not a tax-coded AR line.
- Variances inside the client's shrinkage allowance for the contract year are marked within allowance, and no claim is raised.
- The portal shows the client its claims and their status.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

s.151/152 duty of care: https://vidhijudicial.com/section-151-of-the-indian-contract-act,-1872.html. Circular 178/10/2022-GST (compensation for damage to property is not consideration): EY alert URL in row 25. The plan names the liability only in prose (R4 F-010, `R4-fulfilment-3pl-audit.md:591`). P5-23 claims run against suppliers. grep `shrinkage allowance|loss claim|damage claim` in p5-0*.md, p6-07, finding-w64 returns nothing.

## Global setting

`WAREHOUSE_3PL_LIABILITY_BASIS` default=LOWER_OF_DECLARED_VALUE_AND_CAP alternatives=DECLARED_VALUE, MULTIPLE_OF_MONTHLY_FEES, PER_KG_CAP

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#690
