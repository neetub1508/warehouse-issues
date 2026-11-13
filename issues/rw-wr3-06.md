TITLE: [Warehouse] [Finding] Real-world WR3-06 · Build job work IN: process a customer's material as a job worker
LABELS: task,warehouse,gap-real-world,phase-p10,warehouse-manufacturing
issue: 736
---
Part of #548 · Module **`warehouse-manufacturing`** · Migrations **`V560130` · `V561130`** (MFG) + `warehouse-india` **`V540194`** (schema, only if the return allocation needs a column) · **`V541255`** (purpose seed, permission, leaf) — allocated by the R46 docs pass; india numbers re-checked at S2 (top on 2026-11-13: `V540184` / `V541254`) · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #596, #601, #22 · Source: real-world gap check 2026-11-03, lane WR3

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

A large share of Indian MSMEs (forging, plating, powder coating, textile processing, machining) are job workers. They receive the principal's goods on its challan, run production on them, return processed goods with their own challan, and invoice only the job charge (SAC 9988). That material must not enter their stock value or their GST stock account, but they must account for every kg in and out. The plan refuses a non-own owner on every production order (PRO-GRD-17, QRW-GRD-14), so such a factory cannot use P10 at all.

## Scope

Receive the principal's goods against its challan into owner = principal (core owner_id). Production orders with owner = principal: no value (CST-GRD-09 already anticipates this), a quantity-only pool, and output owned by the principal. Return dispatch under our challan referencing the principal's challan. Scrap and waste returned or retained per the principal's instruction. A per-principal material reconciliation (received / consumed / returned / scrap / balance). An invoice request for the job charge (accounting).

## Acceptance

- 1,000 kg of a principal's billets in → order owned by the principal → 940 kg forgings + 50 kg scrap returned + 10 kg process loss. The reconciliation balances to 0, and our valuation and stock account are unchanged.
- The return challan cites the principal's challan number and date.
- An invoice request for the job charge is emitted, and there is no stock invoice.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

Circular 38/2018, https://gstcouncil.gov.in/sites/default/files/2024-06/jobwork_circular_38_of_2018.pdf ; GST Council job-work flyer. Plan: mfg-production-order §"Non-own owner (job work in) refused in MFG v1.1 · OD-42 · v1.2"; mfg-subcontracting §6. `is_customer_supplied` exists on BOM lines (#594), but no issue in issue_titles.txt covers job work in.

## Global setting

`warehouse.manufacturing.job_work_in_enabled` default=false alternatives=true (R46 S1 DECISION: dotted key convention, as `quick_production_enabled`). With the setting off `PRO-GRD-17` refuses as today.

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#596, #597, #598, #599 (rework), #600 (close), #601 — and the ratified india `job-work` / `delivery-challan` contracts (R46). Batch: its own task after P10-10 (WAVE 10).

## R46 S1 amendments (2026-11-13, pre-build functional review, #736)
Verdict **BUILD (W confirmed) as its own task** after P10-10. OD-42's "v1.2" is superseded by the real-world rule, behind `warehouse.manufacturing.job_work_in_enabled` (default `false`).
- Scope: receipt = core non-PO receipt into owner = principal (core receipts accept a non-house owner), capturing the principal's challan number and date; production order with owner = principal when the setting is on, every component and output the principal's; quantity-only pool (`L-14` already enforced, `WhbMovementPostValidationService.java:1316-1324`); the job worker's own consumables go out by an ordinary core store issue to cost object `PRODUCTION_ORDER` (expensed as the cost of the service); return under our challan citing the principal's (F2); scrap returned, or retained on the principal's instruction; per-principal reconciliation grid; job-charge invoice request (F4). Mobile: none.
- **F1** quantity-only *Close* for a non-own order under `whm_production_orders:close`: open-staging and receipt guards kept, no settlement, no value, `PRO-T4-05` run directly (`PRO-T1-21`, `CST-T1-01`, `CST-GRD-09` amended).
- **F2** new india challan purpose `JOB_WORK_RETURN`: registers no job work, starts no ageing, no ITC-04 row; lines allocated to the principal's inbound challan (number and date printed), partial returns allowed; e-way sub-type mapping **RE-VERIFY** against the NIC list at build; *Return to principal* row action under its own verb (all four links).
- **F3** principal components move by MFG staging / backflush with the owner preserved (P10-06), never by a core requisition (core requisition rules stay house-only); `PRO-GRD-17` / `QRW-GRD-14` allow owner = principal when the setting is on and every component and output is that owner's; `SUB-GRD-04` stays refused (sub-contracting a principal's goods onward is a v1 refusal with its own code).
- **F4** posting a return-to-principal challan emits one `INVOICE_REQUEST` through the existing accounting handover: a **service** line (SAC 9988, job-charge rate × returned quantity from the order's job-charge field), no stock lines; idempotency key `JWI:<challanId>`; a cancelled challan sends a reversal.
- Acceptance arithmetic: reconciliation = received − returned as product − scrap returned − process loss − scrap retained (when instructed) = balance; consumption is detail, never subtracted twice: 1,000 − 940 − 50 − 10 = 0.
