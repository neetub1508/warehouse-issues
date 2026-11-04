TITLE: [Warehouse] [Finding] Terminology WT-06 · Make part numbers searchable and print them on PO, GRN and dispatch
LABELS: task,warehouse,gap-terminology,phase-p1,warehouse-base
issue: 801
---
Part of #4 · Module **`warehouse-base`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **BUILT-CHANGE** · Related: #579 · Source: terminology review 2026-11-03, lane WT

## Why this task exists

An auto-component supplier works by part number. The supplier's number goes on the PO, and the OEM's customer part number must appear on the delivery challan, ASN and labels (PPAP). The product stores both numbers, but:
- The item search box and every item picker search only code, SKU and name.
- No PO, GRN, demand-order, shipment or challan line shows a part number.
- The supplier part number is kept twice, on the supplier source and as an identifier type, with nothing keeping the two copies in step. A storekeeper who types the supplier's number finds nothing, and a customer rejects a challan that carries no part number.

## Scope

Behaviour and data change. No new table.
- **Search and pickers:**
  - Item free-text search, and the item `/dropdown` given a new `search` parameter, also match active `whb_item_identifiers.normalised_value` / `identifier_value`, escaped with `StringUtils.escapeLikePattern`.
  - The same matching applies to the list, count, statistics and export queries.
- **One source for the supplier part number:**
  - Saving a supplier source upserts the SUPPLIER_PART_NUMBER identifier row for (item, supplier). Retiring the source retires the row.
  - A data migration in the base band backfills identifier rows from existing supplier sources and skips key collisions, logging them.
- **Supplier part number on documents:** resolved for the document's supplier, shown on PO and GRN lines (view and print).
- **Customer part number on documents:** resolved for the order's customer, shown on demand-order, shipment and delivery-challan lines (view and print).
- **Exports:** each of those line grids gains the column, with a `grid_column_definitions` row and the export column (grid↔export parity).
- **Validation:** none new. The existing identifier key already scopes by counterparty.

Unchanged: identifier types and permissions.

## Acceptance

- Typing a supplier's part number into the item grid search or into a PO-line item picker finds the item.
- A PO to supplier S prints S's part number on each line that has one. A delivery challan to customer C prints C's part number.
- After the backfill, every active supplier source with a part number has a matching active SUPPLIER_PART_NUMBER identifier, or a logged collision.
- PO, GRN and demand-order line exports include the part-number column whenever the grid shows it.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

- **Search scope:** `B/java/ai/warehousebase/repository/WhbItemRepositoryCustomImpl.java:61-65` (search = code, sku, name).
- **Picker endpoint:** `B/java/ai/warehousebase/controller/WhbItemController.java:145-153` (`/dropdown` has no search parameter).
- **Duplicate storage:**
  - `whb_item_supplier_sources.supplier_part_number` vs IDENTIFIER_TYPE SUPPLIER_PART_NUMBER (`V500010:195`).
  - There are 0 Java references to `SUPPLIER_PART_NUMBER`.
  - The identifier key is counterparty-scoped (`V500016:260-262`).
- **No part number on any document:** grep for `partNumber|Part No` in `w` and `warehouseIndia` en finds 0.
- **Real-world sources:** PPAP PSW "Customer Part Number" (https://inspectionxpert.com/blog/ppap-part-submission-warrant); ERPNext Supplier Items / Customer Items (https://docs.frappe.io/erpnext/user/manual/en/item).
