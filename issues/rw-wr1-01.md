TITLE: [Warehouse] [Finding] Real-world WR1-01 · Accept one supplier invoice delivered in lots across gate entries
LABELS: task,warehouse,gap-real-world,phase-p8
issue: 722
---
Part of #546 · Module **`warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **PLANNED-WRONG** · Related: #565, #564, #174 · Source: real-world gap check 2026-11-03, lane WR1

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Machinery, structural steel and bulk inputs routinely arrive in several trucks under one tax invoice. GST prescribes exactly this: the full invoice first, a delivery challan for each lot, and the original invoice with the last lot. The plan refuses the second truck's GRN as a duplicate bill, so stores must falsify the bill number to receive goods. Credit is only available on the last lot, and accounting cannot know which lot that is.

## Scope

A bill flag `delivery_mode` = `SINGLE` / `LOTS` (Rule 55(5)) on `wh_goods_receipt_bills`. For `LOTS`, each later gate entry carries the supplier's per-lot delivery challan number + date and links to the same invoice. GBM-GRD-01 lets a `LOTS` bill span bill groups while the summed received quantity stays within the billed quantity. A "last lot received" event on the bill, set by the user or derived when billed = received. The MRN envelope (FR-718/719) carries `invoice_lot_status` (`PARTIAL` / `FINAL`) so accounting can hold the ITC until the final lot.

## Acceptance

- One invoice for 3 units of a machine received on 3 gate entries posts 3 GRNs without `SUPPLIER_BILL_DUPLICATE`. A 4th receipt beyond the billed quantity is refused.
- Each lot GRN shows the supplier's delivery-challan number. The duplicate guard still refuses the same bill on a `SINGLE` bill.
- The envelope for lots 1–2 says `PARTIAL` and for lot 3 says `FINAL`. Reversing lot 3 sends `PARTIAL` again.
- The print GRN shows "Lot n of invoice X".

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

Rule 55(5) CGST, with "batches or lots" added by Notfn 39/2018 ([gstzen](https://gstzen.in/a/transportation-of-goods-without-issue-of-invoice-cgst-rule-55.html)). s.16(2) proviso: ITC only on receipt of the last lot ([gsthero](https://gsthero.com/blog/itc-on-goods-received-in-lots-instalments-conditions-and-claims/)). Plan: grn-bill-match.contract.md GBM-GRD-01 refuses the same normalised bill number in another `bill_group_key` (= gate entry) with `409 SUPPLIER_BILL_DUPLICATE`, built in `classic/warehouse/.../V511635__...sql:136` (`bill_group_key WITH <>`). Grep of `SKD|CKD|knocked down|55\(5\)|batches or lots|last lot` in issues/FRD/contracts finds nothing.

## Global setting

`WAREHOUSE_RECEIVING_LOT_INVOICE_ALLOWED` default=true alternatives=false

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#565
