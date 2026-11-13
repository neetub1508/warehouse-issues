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
- **(S1 R47l)** 100 to JW1, hop 40 to JW2: the grid shows Multiple (JW1 = 60, JW2 = 40), and each JW returns only its own balance.
- **(S1 R47l)** The 5C scenario is separate (or starts with 150): goods already returned home cannot also be supplied from JW2.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

GST portal ITC-04 manual: Table 5B "received back from a job worker other than the job worker to whom such goods were originally sent", Table 5C "sent to job worker and subsequently supplied from premises of job worker", https://tutorial.gst.gov.in/userguide/inputtaxcredit/Manual_itc04.htm. Plan: mfg-subcontracting §6 "job worker → job worker; supply from the job worker's premises — v1 not built". P10-20 stage job work assumes a return home.

## Global setting

none — the flow is chosen per document (the JW→JW transfer or the shipment from the JW), so no install-wide option is needed.

## Depends on

#601 (P10-10), #656 (P10-20). Order (S1 R47l): #592 → #601 (port, processed-form return, reconciliation) → #656 (job-work stage, `SUB-T1-20`) → **#1025**. #1024 is independent; when both ship, a direct-received registration keeps its receipt-based clock across hops.

## S1 adopted decisions (R47l, 2026-11-13 — ratified by the batch DECISION rule)

Verdict READY-WITH-DECISIONS; dispatch only after #601 and #656. Contract rows: `india-movement-documents` `IMD-T1-08f`, `IMD-T1-08g`, `IMD-GRD-25`, `IMD-GRD-26`, `IMD-T4-08`, `IMD-UNR-07`, `IMD-UNR-09`, `IMD-T5-03`; `mfg-subcontracting` §13 `SUB-T1-31`, `SUB-UNR-30`, `SUB-T4-20` (extended). Statutory figures RE-VERIFY at build.

- **F1 (W) — one registration, quantity at several job workers.** The registration and its original challan keep their clock. A hop is an INTERNAL ledger movement premises (JW1) → premises (JW2), owner unchanged, recorded on the registration as a new dispatch-line kind **`TRANSFER`** (one more value in `V540120`'s `line_kind` CHECK; no other vocabulary change), quantity-bearing so a partial hop (40 of 100) is allowed. The balance per holder is read from the ledger positions at the registration's premises locations; the grid shows the current holder or "Multiple" with the per-holder split in the view. Returns, onward hops and supplies are validated against that holder's balance (`422 RETURN_EXCEEDS_OUTSTANDING`). The hop carries the principal's challan (ship-from JW1, consignee JW2), linked to the registration, never a second registration, excluded from Table 4.
- **F2 (W) — ITC-04 5A / 5B / 5C.** Add `itc04_table` (`4` / `5A` / `5B` / `5C`) and the returning / supplying JW's identity to `whin_itc04_lines`, and the table to the builder's GROUP BY. Table 4 = the original `DISPATCH` only; a `TRANSFER` is reported nowhere; a `RETURN` whose holder ≠ the original JW → 5B, otherwise 5A; a supply from premises → 5C. Filed snapshots stay frozen; a return filed before this change keeps its stored figures.
- **F3 (W) — supply from JW premises without opening the allocator.** Reuse the premises → `VIRT-CUSTOMER` `ISSUE` pattern of the deemed sale (`WhinJobWorkDeemedSupplyService`) as a registration action "Supply from job-worker premises": the user enters the customer, the quantity per holder line and the principal's tax-invoice reference; it emits the same invoice request the despatch does and closes that quantity as 5C; refused above the holder's balance. A JW with no GSTIN gets a warning naming the additional-place-of-business requirement (not a refusal).
- **F4 (W) — processed output at JW1 feeds JW2 without a fake home receipt.** A subcontract receipt (P10-10) may name, as its receive-to location, the premises of the next stage's job worker. It completes the job card at the current stage and is the dispatch of the next stage's child order (`SUB-T1-20`); no store movement. The original inputs' registration closes through the processed-form return (`registerReturn`), and the new challan's clock starts for the processed goods. This delivers scope (c) and the "50 finished shafts at JW2" precondition.
- Dropped: refusing supply from JW premises unless an additional-place registration is recorded (needs new master data; typical ERPs warn).
- Below the bar (not filed): a hop reversed after a filed ITC-04 period (existing frozen-return refusal); lot genealogy across processed-form hops beyond `SUB-T4-*`.

## Migration bands (S1 R47l)

`warehouse-india` V540000–V549999 (the `TRANSFER` line kind, the ITC-04 table and holder columns, the hop challan link) · `warehouse-manufacturing` V560000–V569999 (receive-to-JW on the subcontract receipt) · `warehouse` V510000–V519999 only if the invoice-request emission needs DDL. Next free in each band, allocated in `DATA-MODEL.md` at build. Global setting: none.

Parity: mobile none (Warehouse India is web-only); siblings none carry job work (warehouse-3pl out of scope).
