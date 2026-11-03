TITLE: [Warehouse] [Finding] Real-world WR7-04 · Build Rule 55(5) lot-wise despatch for SKD/CKD and part shipments
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-india
issue: 765
---
Part of #8 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #140, #147 · Source: real-world gap check 2026-11-03, lane WR7

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Machinery and plant makers despatch one order in several trucks. The law wants one complete tax invoice before the first truck, a challan per truck that references that invoice, and the original invoice copy with the last truck. With only a `SKD_CKD` label, staff raise a full invoice per truck (overstating supplies) or move trucks on bare challans with no invoice link (detention risk).

## Scope

An SKD/CKD challan series is linked to a parent invoice reference, which is required before the first challan. Each challan carries a lot sequence and its share of quantity and value. The last challan is flagged, and lot quantities may not exceed the invoice. Each lot's EWB uses the challan with the invoice reference.

## Acceptance

- The first SKD challan without a parent invoice reference is refused
- Lot quantities above the invoice quantity are refused
- The last lot prints "original invoice copy to accompany"
- Each lot's EWB payload references the parent invoice number

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

[C10]: subsequent consignments move under challans that reference the invoice (r.55(5) mechanics). Plan: #140 lists `SKD_CKD` as a challan type only. grep `last consignment|invoice_id` in p2in-03 = 0.

## Depends on

#140
