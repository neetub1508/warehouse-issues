TITLE: [Warehouse] [Finding] Terminology WT-08 · Add a label-only item noun setting: Item, Part or Material
LABELS: task,warehouse,gap-terminology,phase-p1,warehouse-base
issue: 803
---
Part of #4 · Module **`warehouse-base`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **MISSING-TASK** · Related: #139 · Source: terminology review 2026-11-03, lane WT

## Why this task exists

Installs legitimately differ:
- An auto-component maker's staff say "Part No.".
- A process plant says "Material Code".
- A trader or 3PL says "Item Code".

The item master is correct as "Item" (see the summary). Forcing every shop floor to read "Item Code", though, keeps the "where do I put the part number" confusion alive. Nothing in platform or warehouse can swap a label per install today: a grep for terminology or label-override finds 0.

## Scope

- **The setting:** one admin setting (Global Settings → Warehouse → General, SELECT).
- **The resolver:** a small warehouse-base frontend label resolver reads the setting and picks an alternate i18n key set (`terminology.PART.*`, `terminology.MATERIAL.*`, en/fr/hi) for a bounded list of labels:
  - the item master menu and page titles (Items, Item Types, Item Categories);
  - the item code and name labels (Item Code / Item Name become Part No. / Part Name, or Material Code / Material Name) on forms, grid headers and filters;
  - item picker placeholders.
- **Unchanged:**
  - codes, API fields, tables, permissions, routes and menu name keys;
  - export headers and print templates, which keep "Item Code" / "Item Name" for downstream mapping;
  - free-text sentences.
- **Behaviour:** none.

## Acceptance

- With the setting at PART, the item menu reads "Parts", the item form reads "Part No." / "Part Name", and line grids read "Part No.", in en, fr and hi.
- With the setting at ITEM, the UI is identical to before.
- With any value, exports still say "Item Code".
- Changing the setting needs no rebuild and no data change.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

- **Current labels:** `wb` en:1473 `item.fields.itemCode`="Item Code"; `item.title`="Items".
- **No override mechanism:** a grep for `terminology|labelOverride|translation_override` across platform and warehouse-base returns 0.
- **Real-world sources:** Epicor "Part" (https://www.hyperbots.com/glossary/epicor-kinetic-part-maintenance); SAP "Material" (https://help.sap.com/saphelp_me60/helpdata/en/9d/7cbd534f22b44ce10000000a174cb4/content.htm); Tally "Use Part Number for stock items" (https://help.tallysolutions.com/tally-prime/inventory/manage-stock-item-tally/).

## Global setting

`warehouse.terminology.item_noun` default=ITEM alternatives=PART,MATERIAL

The default is the recommendation; the alternatives are selectable per install through the settings page.
