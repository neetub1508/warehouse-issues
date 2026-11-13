TITLE: [Warehouse] [Finding] Real-world WR3-05 · Allow job worker to job worker movement and supply from the job worker's premises
LABELS: task,warehouse,gap-real-world,phase-p10,warehouse-india
issue: 1025
---
Part of #548 · Module **`warehouse-india`** (+ the core outbound path from a `JOB_WORKER` location) · Migrations **next free in each module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #601, #656, #22 · Source: real-world gap check 2026-11-03, lane WR3; split from #601 by the R46 S1 DECISION (W, own task after P10-10 and P10-20; ITC-04 Tables 5B / 5C; `SUB-OPEN-07` → own task, v1.1)

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Multi-stage outside processing is the norm: machining at JW1, then plating at JW2, then heat treatment at JW3, with the goods never coming home. FG is often dispatched to the OEM or exported straight from the last job worker. ITC-04 has dedicated tables (5B, 5C) for both cases. Forcing every leg through our store means fake receipts and e-way bills, and an ITC-04 that does not match the job workers' records.

## Scope

(a) A JW→JW transfer under the principal's challan: one registration hop, clock unchanged from the original dispatch, Table 5B on receipt home. (b) Shipment from the JW location to a customer through the normal outbound path with an invoice request, closing the registration as "supplied from JW premises" (Table 5C), with an additional-place-of-business warning when the JW is unregistered. (c) Parent job-card stages may chain JW1→JW2.

## Acceptance

- 100 shafts JW1 → JW2 → home: ITC-04 shows Table 4 once, Table 5B for the return from JW2, and the clock is unchanged.
- 50 finished shafts shipped from JW2 to a customer close that quantity as 5C.
- The open job-work grid shows the current holder.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

GST portal ITC-04 manual: Table 5B "received back from a job worker other than the job worker to whom such goods were originally sent", Table 5C "sent to job worker and subsequently supplied from premises of job worker", https://tutorial.gst.gov.in/userguide/inputtaxcredit/Manual_itc04.htm. Plan: mfg-subcontracting §6 "job worker → job worker; supply from the job worker's premises — v1 not built". P10-20 stage job work assumes a return home.

## Global setting

none — the flow is chosen per document (the JW→JW transfer or the shipment from the JW), so no install-wide option is needed.

## Depends on

#601 (P10-10), #656 (P10-20)
