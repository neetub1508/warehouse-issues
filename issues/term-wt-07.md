TITLE: [Warehouse] [Finding] Terminology WT-07 · Seed missing item types: spare, traded good, loose tool, scrap
LABELS: task,warehouse,gap-terminology,phase-p1,warehouse-base
issue: 802
---
Part of #4 · Module **`warehouse-base`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **BUILT-CHANGE** · Related: #729, #737, #579 · Source: terminology review 2026-11-03, lane WT

## Why this task exists

Item types are seeded and read-only: `WhbItemTypeController` exposes only `:view` endpoints, so an install cannot add one. Today a trader's goods must be typed "Stock", maintenance spares "Consumable" or "Tyre", and saleable scrap has no item type at all. Indian books report inventory per Schedule III class: raw materials, WIP, finished goods, stock-in-trade, stores and spares, loose tools. CARO 3(ii)(a) judges count discrepancies per class, and CRA-1 cost records list spares separately. Without these types an install cannot classify its items correctly, and the flow flags (purchasable, saleable, issuable to production) are wrong for them.

## Scope

Data and behaviour change.
- **New seeds:** a warehouse-base migration (next free in V500xxx, `WHERE NOT EXISTS`, RL-003 ownership guard) adds four `whb_item_types` rows, with flags:

  | Code | Label | Purchasable | Manufacturable | Saleable | Issuable to production | QC default | AVL default |
  |---|---|---|---|---|---|---|---|
  | `SPARE_PART` | Spare part (maintenance) | yes | no | yes | no | false | false |
  | `TRADED_GOOD` | Traded good (stock-in-trade) | yes | no | yes | no | false | false |
  | `LOOSE_TOOL` | Loose tool | yes | no | no | no | false | false |
  | `SCRAP` | Scrap / by-product | no | yes (as output) | yes | no | false | false |

  Each label ships in en, fr and hi, and each type has a description.
- **Schedule III default class:** if #729 lands its class list, the type gets a `statutory_class_code` default (VARCHAR(40), nullable, code-list backed, no CHECK). #729 uses it when an item's category maps no class.
  - Existing types map to: RAW_MATERIAL and BOUGHT_OUT → raw materials; SUB_ASSEMBLY → WIP; FINISHED_GOOD → finished goods; TRADED_GOOD → stock-in-trade; CONSUMABLE, PACKAGING and SPARE_PART → stores and spares; LOOSE_TOOL → loose tools; SCRAP → others.
- **Validation:** the existing type-flag guards apply. For example, a `TRADED_GOOD` cannot be put on a BOM output, and a `SCRAP` item cannot be bought on a PO.
- **Exports:** the item export "Type" / "Type Name" columns carry the new codes. The item-type export gains "Statutory Class" if the column is added.
- **Kept and not repurposed:** CORE and TYRE (CP-CODE-011). No existing type is renamed or removed, and no existing item's type changes.

## Acceptance

- On a fresh install the Item Types grid lists the four new codes with the flags above, in en, fr and hi.
- An item of type `SCRAP` is refused on a PO line and accepted on a demand-order line.
- An item of type `TRADED_GOOD` is refused as a BOM output (MFG) and as a production issue.
- With #729 present, an item with no category class reports under its type's default Schedule III class.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

- **Current seeds:** `B/resources/db/migration/V500008__Create_whb_item_types.sql:90-101` and `V500601__…:84-88`. 17 types, none of them spare, traded, tool or scrap.
- **Read-only master:** `B/java/ai/warehousebase/controller/WhbItemTypeController.java:68-137`, all `whb_item_types:view`.
- **Real-world sources:** Schedule III inventory heads (https://www.taxmann.com/post/blog/financial-statement-checklist-ind-as-schedule-iii-current-assets-presentation-and-disclosure); SAP HAWA / ERSA (https://help.sap.com/saphelp_me60/helpdata/en/9d/7cbd534f22b44ce10000000a174cb4/content.htm); spares under Ind AS 16 (https://www.taxmann.com/post/blog/accounting-of-rotables-under-ind-as-inventory-or-ppe).
