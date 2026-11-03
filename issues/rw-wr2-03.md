TITLE: [Warehouse] [Finding] Real-world WR2-03 · Control count sheets and tags as numbered, reconciled documents
LABELS: task,warehouse,gap-real-world,phase-p2
issue: 731
---
Part of #5 · Module **`warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **MISSING-TASK** · Related: #37, #84 · Source: real-world gap check 2026-11-03, lane WR2

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

At a wall-to-wall count, sheets and tags are pre-numbered, issued to teams, and every number is accounted for (used, void, unused) before the count closes; a missing sheet means uncounted stock or a hidden sheet. The auditor attending under SA 501 checks this control. The plan prints count sheets but has no numbering, issue or return reconciliation; the competitor audit row parked it as V2 with no task.

## Scope

Gapless sheet/tag numbers per count from the P1-09 counter; issue to team/counter; mark returned/void; block POST while any issued number is unreturned (or require a supervisor reason); manual entry from a paper sheet records its sheet number.

## Acceptance

- A count with sheets 1-50 issued and 49 returned cannot post without a recorded reason for the missing number.
- Voided numbers stay in the register with a reason.
- Numbers never repeat across counts in the same company.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

SA 501 attendance evaluates management's instructions for recording and controlling count results: https://kb.icai.org/pdfs/PDFFile5b3b56931ba5b3.25548018.pdf ; R2 audit docs/reviews/R2-tier1-wms-audit.md:340 row 163 "Count tag generation & reconciliation (find the missing tag)" = V2; grep "count tag" elsewhere = 0; p2-04.md:116 "Print count sheet" only.

## Depends on

#37, #84
