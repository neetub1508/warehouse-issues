TITLE: [Warehouse] [Finding] Terminology WT-01 · Fix item-master labels: name, category, item column, type names
LABELS: task,warehouse,gap-terminology,phase-p1,warehouse-base
issue: 796
---
Part of #4 · Module **`warehouse-base`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **BUILT-CHANGE** · Related: #787, #729 · Source: terminology review 2026-11-03, lane WT

## Why this task exists

The item's name is labelled "Description", and its real description is exported as "Notes". A storekeeper filling the form, or an accountant mapping the export to Tally ("Name") or BUSY ("Item Name"), puts the long text in the wrong field. One grid says "Category", the next says "Item Category" and a stock report says "Item Group", so users go looking for an Item Group master that does not exist. "Item" alone sometimes means the code and sometimes the name. Several seeded type names are wrong for Indian users:
- "Stock" reads as a quantity, not a kind of item.
- "Packaging" collides with "Packaging Levels".
- "Bought out" lacks "component", the word annual reports use.
- "Sub-assembly" hides that this is also the semi-finished type.

## Scope

Labels only, through i18n en/fr/hi (no key deleted) plus `grid_column_definitions` / `filter_definitions` display names and seeded `whb_item_types.name`. Export header strings change too.
- **Item name and description:**
  - `name` becomes "Item Name" on the form, grid, filter and export; `description` becomes "Description" (it was "Notes").
  - hi becomes "वस्तु का नाम". fr "Désignation" is the correct term: it only gets its accent.
- **The bare "Item" column:**
  - On `itemCode` columns it becomes "Item Code" in the 16 grids.
  - On `itemName` columns it becomes "Item Name" in the 24 grids.
- **Category:** "Item Category" everywhere.
  - That covers the item form, the grid and filter, and the 10 report filters, 3 report columns and 3 export headers that said "Item Group".
  - The design-set wording "item group" in FR-246, FR-247, FR-386 and P2-18 becomes "item category".
- **Seeded type names:**
  - STOCK becomes "General stock item" (fr "Article stocké", hi "सामान्य स्टॉक वस्तु").
  - PACKAGING becomes "Packing material".
  - BOUGHT_OUT becomes "Bought-out component".
  - SUB_ASSEMBLY becomes "Sub-assembly / semi-finished".
  - The india statutory categories are aligned to the same case: "Raw material", "Finished goods".
- **Form vs export:** hazmat labels are aligned to the form ("Hazardous", "UN Number").
- **UoM spelling:** "UoM" everywhere. The UOM, Unit and Base Unit variants go, including the 4 export headers.
- **Part number spelling:** "Supplier Part No.", "Manufacturer Part No.", "Customer Part No.".
- **Barcode filter:** renamed "Barcode / Part No.".
- **Menu labels** (keys, route_path and required_permission_prefix unchanged):
  - "Supersessions" becomes "Item Supersessions".
  - "Supplier Sources" becomes "Item Supplier Sources".
  - "Item Site Settings" becomes "Item × Warehouse Settings".

Unchanged: codes, columns, API field names, permission names and the menu structure.

## Acceptance

- On the item screen, form, grid and CSV/Excel export, `name` reads "Item Name" and `description` reads "Description" in en, fr and hi.
- `grep '"Item Group"'` across warehouse en/fr/hi i18n, `*ExportService.java` and the `grid_column_definitions` / `filter_definitions` rows returns 0.
- No grid has a column labelled plain "Item". Every `itemCode` column reads "Item Code" and every `itemName` column reads "Item Name".
- The item-type grid shows "General stock item", "Packing material", "Bought-out component" and "Sub-assembly / semi-finished", and their codes are unchanged.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

- **Item name labelled Description:** `wb` en:1476 `item.fields.name`="Description" (hi:1476 "विवरण" = description). Grid seed `B/resources/db/migration/V500015__…:701` `'whb_items','name','Description'`. Export `B/java/ai/warehousebase/service/WhbItemExportService.java:244` "Description","Notes".
- **Category drift:** en:1478 "Category". "Item Group" at `w` en:4796, 8750, 9024, 9727 and others. Export headers `W/java/ai/warehouse/service/WhStockToGlExportService.java:55`, `WhStockOnHandExportService.java:59`, `WhGodownStatementExportService.java:61`. There is no item-group entity: it is `whb_item_categories`.
- **Seeded type names:** en:829 STOCK "Stock", :836 "Packaging", :842 "Bought out".
- **Form vs export:** en:1508 "Hazardous" vs export "Hazmat"; :1509 "UN Number" vs "UN No.".
- **Misleading filter label:** en:1521 filter "Barcode", which actually matches every identifier, part numbers included (`B/java/ai/warehousebase/repository/WhbItemRepositoryCustomImpl.java:99-106`).
- **Real-world sources:** ERPNext Item Name vs Description (https://docs.frappe.io/erpnext/user/manual/en/item); Mahindra "bought-out components" (https://www.mahindra.com/annual-report-FY2020/332/).
