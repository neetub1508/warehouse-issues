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
- **(S1 R47l)** Post the GRN for 100 at JW1: JW1's premises shows +100; store and `RECEIVING` show no movement, and no putaway or QC task exists.
- **(S1 R47l)** The challan is dated the receipt date and the deemed-supply due date = receipt date + 1 year (INPUTS). Replaying the post leaves one challan and one registration.
- **(S1 R47l)** Under #601, a subcontract receipt can backflush those 100 without a `SUBCONTRACT_DISPATCH`.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

s.143(1)(b) and s.19 (CG: 3 years from receipt by JW), https://www.cggst.com/uploads/document/1756724526-section-19.pdf ; Circular 38/2018. Plan: mfg-subcontracting §3.1 "Direct-from-vendor … not supported in v1 (SUB-OPEN-07)" and §6 "v1 not built". There is no task.

## Global setting

none — the flow is chosen per document (the PO line ship-to), so no install-wide option is needed.

## Depends on

#601 (P10-10). Order (S1 R47l): #592 scaffold → P10-10 prerequisites → #601 (port + india bean + reconciliation) → **#1024**. Not on #656. #22 (P4-02) code is the base; its open E2E items do not block this.

## S1 adopted decisions (R47l, 2026-11-13 — ratified by the batch DECISION rule)

Verdict READY-WITH-DECISIONS; dispatch only after #601. Contract rows: `mfg-subcontracting` §13 `SUB-T1-30`, `SUB-GRD-30`, `SUB-T4-30`, `SUB-T4-31`; `india-movement-documents` `IMD-T1-08e`, `IMD-UNR-07`, `IMD-T3-01`, `IMD-T4-08` (Table 4). Statutory figures RE-VERIFY at build.

- **F1 (W) — clock from the JW receipt.** Posting a "received at job worker" GRN raises the `JOB_WORK` challan itself, in the same transaction (source document = the GRN), with `challan_date` = the JW receipt date; it also creates the registration and records the GRN movement as its `DISPATCH` line (`recordDispatch` already accepts any movement into the premises). The existing `challan_date` + period arithmetic gives the s.143 clock; the freeze trigger (`V541190`) is unchanged. Ship-from = the supplier's address, consignee = the JW. The e-way bill is the supplier's (bill-to / ship-to); we raise none. Replaying the post creates no second challan, registration or Table 4 quantity.
- **F2 (W) — PO-line destination at a job worker, and the P10-10 intake.** `wh_purchase_order_lines.receiving_location_id` may also name an active per-counterparty `JOB_WORKER` premises location of the PO's site (the `V501382` kind, never the shared `VIRT-JOB_WORKER`); no new column. The PO line may carry the subcontract order it feeds; P10-10's reconciliation then counts that GRN's accepted quantity and value as "sent" once, with no store dispatch posted. Ordinary receipts keep the `RECEIVING` rule (`422 RECEIVING_LOCATION_INVALID` unchanged).
- **F3 (R) — the GRN post must not treat JW stock as at our dock.** On a JW-destination line the stock lands at the PO line's premises location: no status-store redirect, no QC hold / first-article, no putaway task, no gate-entry requirement. The receipt is recorded from the JW's acknowledgement or the supplier's invoice.
- Dropped: separate challan / receipt / clock-origin dates (needs a freeze-trigger change; F1 reaches the same outcome).
- Below the bar (not filed): reversal after the ITC-04 period is filed (existing filed-period refusal applies).

## Migration bands (S1 R47l)

`warehouse` V510000–V519999 (PO-line validation only, likely no DDL) · `warehouse-india` V540000–V549999 (challan source kind = GRN) · `warehouse-manufacturing` V560000–V569999 (reconciliation intake reference). Next free in each band, allocated in `DATA-MODEL.md` at build. Global setting: none.

Parity: mobile none (Warehouse India is web-only); siblings none (warehouse-3pl client stock at a JW is out of scope).
