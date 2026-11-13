TITLE: [Warehouse] [Finding] Real-world WR3-04 · Support inputs shipped direct from the supplier to the job worker
LABELS: task,warehouse,gap-real-world,phase-p10,warehouse-india
issue: 1024
---
Part of #548 · Module **`warehouse-india`** (+ the core goods-receipt variant with ship-to = the job-worker location) · Migrations **next free in each module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #601, #22 · Source: real-world gap check 2026-11-03, lane WR3; split from #601 by the R46 S1 DECISION (W, own task after P10-10; `SUB-OPEN-07` → own task, v1.1)

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

In auto-component and fabrication clusters a steel mill or coil centre invoices the principal but delivers straight to the press or slitting job worker. The principal takes ITC, must issue the job-work challan, and the clock runs from the job worker's receipt. Refusing this flow forces a fake receipt into our store followed by a fake dispatch, so the stock register, e-way bills and ITC-04 all misstate the real movement.

## Scope

Add a GRN variant "received at job worker": a PO line whose ship-to is the job worker location. The receipt posts supplier → JOB_WORKER location (owner house), creates the job-work registration with the clock from the JW receipt date, links the supplier invoice, and puts the challan on ITC-04 Table 4. Later processing and return work as in P10-10.

## Acceptance

- A PO shipped to job worker JW1: posting the receipt creates on-hand stock at JW1's virtual location and a registration with clock start = receipt date.
- ITC-04 Table 4 lists it with the principal's challan.
- Store on-hand is never touched.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

s.143(1)(b) and s.19 (CG: 3 years from receipt by JW), https://www.cggst.com/uploads/document/1756724526-section-19.pdf ; Circular 38/2018. Plan: mfg-subcontracting §3.1 "Direct-from-vendor … not supported in v1 (SUB-OPEN-07)" and §6 "v1 not built". There is no task.

## Global setting

none — the flow is chosen per document (the PO line ship-to), so no install-wide option is needed.

## Depends on

#601 (P10-10)
