TITLE: [Warehouse] [Finding] Real-world WR1-10 · Let an inward gate entry reference an assets-module PO receipt
LABELS: task,warehouse,gap-real-world,phase-p8
issue: 728
---
Part of #546 · Module **`warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **MISSING-TASK** · Related: #564 · Source: real-world gap check 2026-11-03, lane WR1

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Machines and other capital goods enter through the same factory gate. Security logs them as purpose `OTHER` with no link to the asset receipt, so the gate register cannot prove which asset arrived on which vehicle and bill. Auditors check that link when ITC on capital goods is taken.

## Scope

Purpose `CAPITAL_GOODS_IN` with a free reference to an assets PO / receipt number (read-only lookup if exposed, no edit of `assets`). The bill block works as for purchases. Shown on the gate register and the slip.

## Acceptance

- A `CAPITAL_GOODS_IN` entry requires the bill and an asset PO reference, and appears in the gate register filter.
- No stock movement and no GRN is created.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

Gate purposes are `PURCHASE_RECEIPT`, `RETURNABLE_IN`, `CUSTOMER_RETURN_IN`, `JOB_WORK_IN`, `SAMPLE_IN`, `FREE_OF_COST_IN`, `OTHER` (gate-entry.contract.md). FRD-TRADE R8 routes capex POs to `assets`, which has PO receipts (`classic/assets/backend/.../AssetPoReceiptResponse.java`).
