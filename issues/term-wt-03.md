TITLE: [Warehouse] [Finding] Terminology WT-03 · Disambiguate document names: GRN vs MRN, work order, consignment, lot
LABELS: task,warehouse,gap-terminology,phase-p8
issue: 798
---
Part of #546 · Module **`warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **BUILT-CHANGE** · Related: #569, #570, #46, #575 · Source: terminology review 2026-11-03, lane WT

## Why this task exists

Indian users are confused by several document names:
- **GRN vs MRN.** In many Indian factories GRN and MRN mean the same thing, and some plants use MRN for "Material Requisition Note". The product has both "Goods Receipts" and "Material Receipt Notes", with no subtitle saying which comes first or why. Buttons say "Prepare MRN".
- **Work Orders.** The menu "Work Orders" is VAS repack and kitting. Indian and SAP users read "work order" as the production order, which MFG adds next as "Production Orders".
- **Consignments.** "Consignments" is the LR (lorry receipt) of a shipment, but the same word names consignment stock. In French it reads *Envois*, the same word used for Shipments.
- **Lot vs Batch.** Indian goods carry a "Batch No.", but the receiving screen asks for "Lot Code".
- **Small drifts.**
  - The cost-object `DEMAND_ORDER` is labelled "Sales order".
  - "Count Programs" (menu) vs "Count Programmes" (page).

## Scope

Labels only, in i18n en/fr/hi plus menu display names (keys, routes and permission prefixes unchanged) and seeded code-list names.
- **GRN / MRN:**
  - Menu and page titles become "Goods Receipts (GRN)" and "Material Receipt Notes (MRN)".
  - Each gets a one-line subtitle: "Goods counted in at the gate/dock against the PO or bill" and "Stock accepted into stores after QC and authorisation".
  - "Prepare MRN" becomes "Prepare Material Receipt Note".
- **Material Requisitions:** subtitle "Department indent for issue from stores".
- **Work Orders:** menu and page become "VAS Work Orders".
- **Consignments:** menu and page become "Consignment Notes (LR)"; fr *Lettres de voiture*, hi "लॉरी रसीद (LR)".
- **Lot:** the lot label on receipt and lot screens becomes "Lot / Batch No." (hi "लॉट / बैच नं.").
- **Cost object:** `DEMAND_ORDER` becomes "Demand order".
- **Count programmes:** "Count Programmes" on both menu and page. The Counts subtitle adds "(physical verification)".

Unchanged: document type codes, tables, numbering and print template codes. The placement of Consignments under L2 Returns is not moved here, because Outbound and Packing are both at the 8-leaf cap.

## Acceptance

- The Inbound and Stores menus show "Goods Receipts (GRN)" and "Material Receipt Notes (MRN)", and each page shows its subtitle in en, fr and hi.
- The VAS menu shows "VAS Work Orders" and `/vas/work-orders` still opens. The menu `name` key is unchanged.
- In fr, Consignments and Shipments have different labels.
- The GRN line form and the Lots grid show "Lot / Batch No.".

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

- **GRN / MRN:** `w` en `materialReceiptNote.title`="Material Receipt Notes" and `goodsReceipt.title`="Goods Receipts", with no subtitle key on either. en:889 "Prepare MRN".
- **Work orders and consignments:** en:10445 "Work Orders" (route `/vas/work-orders`, menu V511208:184). en:13254 "Consignments", with fields "LR No."/"LR Date". fr menu `W/resources/db/migration/V511265__…:211` 'Envois'.
- **Count programmes:** menu `V511248:159` vs en:3540 "Count Programmes".
- **Real-world sources:** GRN dominant and MRN ambiguous (https://themunim.com/goods-received-note/); batch as the Indian and SAP term (https://www.odoo.com/documentation/16.0/zh_CN/applications/inventory_and_mrp/inventory/product_management/product_tracking/differences.html).
