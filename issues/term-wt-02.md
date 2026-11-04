TITLE: [Warehouse] [Finding] Terminology WT-02 · Call the facility "Warehouse" everywhere, not Site or Warehouse
LABELS: task,warehouse,gap-terminology,phase-p1,warehouse-base
issue: 797
---
Part of #4 · Module **`warehouse-base`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **BUILT-CHANGE** · Related: #684, #190 · Source: terminology review 2026-11-03, lane WT

## Why this task exists

The master and the module are called "Warehouses", but its grids mix words: 98 label the column "Site" and 14 "Warehouse", and filters and exports drift the same way. A user filtering "Site" on one screen and "Warehouse" on the next cannot tell they are the same thing. "Site" is also a location level inside a warehouse. Indian users say warehouse, godown or stores, and "site" usually means a construction or project site. In Hindi the same entity is गोदाम in 59 strings, वेयरहाउस in 39 and साइट elsewhere.

## Scope

Labels only.
- **Column, filter and export labels:**
  - Every `warehouseName` / `warehouseId` / `fromWarehouse*` / `toWarehouse*` label reads "Warehouse" / "From Warehouse" / "To Warehouse".
  - That covers grid_column_definitions, filter_definitions, i18n en/fr/hi and the `*ExportService` headers.
- **Kept as "Godown":** the Godown-wise Stock Statement and its Godown column. That is the statutory and Tally name for that report.
- **Location levels:**
  - SITE becomes "Warehouse (root)".
  - LEVEL becomes "Rack level", so the Level field no longer shows the value "Level".
  - The field label becomes "Location Level".
- **Menu labels:** L2 "Sites & Parties" becomes "Warehouses & Parties" (name key unchanged).
- **hi:** the entity is always "गोदाम". "वेयरहाउस" stays only in the module name, if at all.
- **Unchanged:** tables, columns, routes, permission names and the `SITE` code.

Installs that prefer "Godown" for the master can be served later by the WT-08 mechanism. This finding adds no setting, because within the product one consistent word is simply correct.

## Acceptance

- In en, no seeded grid, filter or export label says "Site" for a `whb_warehouses` reference. In en, no seeded grid, filter or export label says "Godown" outside the godown statement.
- The locations grid shows the level values Warehouse (root) / Building / Zone / Aisle / Rack / Rack level / Position.
- In hi, every warehouse-entity label uses one word, checked by a grep listing.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

- **Grid and filter counts:** seeded `'warehouseName','Site'` ≈ 113 rows vs `'Warehouse'` 14 vs `'Godown'` 1. `'warehouseId','Site'` ≈ 123 vs `'Warehouse'` 13 (grep over `warehouse*/backend/.../db/migration`).
- **Master and level names:** `wb` en `warehouse.title`="Warehouses"; en:2139 `location.levels.SITE`="Site".
- **Earlier fix went the other way:** #190 / #222 (closed 2026-10-03) relabelled the one "Warehouse" export header to "Site" to match the majority of grids. That was a consistency fix with no terminology decision behind it, and this finding reverses its direction.
- **Real-world sources:** Tally "Godown" as the location master (https://help.tallysolutions.com/tally-prime/inventory/); D365, Odoo and NetSuite use "Warehouse" (https://learn.microsoft.com/en-us/dynamics365/supply-chain/pim/product-information).
