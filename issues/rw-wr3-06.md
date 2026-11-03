TITLE: [Warehouse] [Finding] Real-world WR3-06 · Build job work IN: process a customer's material as a job worker
LABELS: task,warehouse,gap-real-world,phase-p10,warehouse-manufacturing
issue: 736
---
Part of #548 · Module **`warehouse-manufacturing`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #596, #601, #22 · Source: real-world gap check 2026-11-03, lane WR3

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

`WAREHOUSE_MFG_JOB_WORK_IN_ENABLED` default=false alternatives=true

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#596
