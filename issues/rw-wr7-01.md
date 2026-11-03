TITLE: [Warehouse] [Finding] Real-world WR7-01 · Re-seed scrap TCS as s.394(1) at 2% from 1 April 2026
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-india
issue: 762
---
Part of #8 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **PLANNED-WRONG** · Related: #32 · Source: real-world gap check 2026-11-03, lane WR7

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Every scrap sale invoiced since 1 April 2026 collects TCS at half the statutory rate. The seller is liable for the shortfall plus interest, and the 27EQ return names a section the new Act no longer carries. A buyer who certifies use for manufacturing should not be charged at all, and today nothing records that declaration.

## Scope

A new forward migration closes the 206C(1) row with `effective_to = 2026-04-01` and inserts `394(1)` / `IN_STATUTORY_SCRAP` at 2.000000 from 2026-04-01. The scrap-sale handover carries `buyer_tcs_declaration` (form code, date, reference document) on the counterparty, effective-dated, and a valid declaration sets the TCS flag to false. Update the pack threshold register and the #32 statutory table.

## Acceptance

- A scrap sale dated 31 Mar 2026 resolves 206C(1) at 1%; one dated 1 Apr 2026 resolves 394(1) at 2%
- A scrap sale to a buyer holding a valid Form 127 declaration on the invoice date carries `tcs_applicable = false` and names the declaration
- No row has an open-ended 206C(1) range, and the overlap exclusion still holds
- The pack and #32 no longer state 1% or s.206C(1) as current

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

[TCS26]: s.394(1) Table Sl.4 sets 2% on scrap from 1 Apr 2026, replacing 206C(1), and Form 127 is the no-collection declaration. Code: `classic/warehouse-india/.../V540131__Create_whin_itc_reversals_and_whin_tcs_sections_and_seed_the_scrap_stock_status.sql` seeds `('206C(1)','IN_STATUTORY_SCRAP',…,1.000000,NULL,DATE '2017-07-01')` with no `effective_to`. Plan: pack l.63 and #32 l.56 say "1 %". grep `394|Form 127|27C` in the design set = 0.

## Depends on

#32
