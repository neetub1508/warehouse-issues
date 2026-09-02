# LENS R3 — ERP-embedded and mid-market inventory audit

**NetSuite · D365 SCM · SAP B1 · Odoo 18 · ERPNext · Acumatica · Sage · Epicor Kinetic ·
Zoho Inventory · Unleashed · Cin7 · Fishbowl · Katana · inFlow · Sortly · SkuVault · Ordoro ·
Finale · QuickBooks Commerce · Tally Prime · Busy · Marg · Vyapar · Increff · Unicommerce ·
EasyEcom · Vinculum · GoFrugal · Logic ERP · CDK · Reynolds · Tekion · Dealertrack · Autosoft ·
Karmak · Autologue · Indian OEM dealer DMS parts**

scored against the **proposed** `warehouse-base` / `warehouse` / `warehouse-adapter-<vertical>` /
`warehouse-3pl` design set.

Audit date 2026-09-01. No web access; scored from product knowledge. Anything I could not verify
carries `?` rather than a guess.

---

## 0. Read this before the matrix

### 0.1 The design set does not exist yet

`warehouse-issues/` is an **empty repository** — `docs/contracts/` and `issues/` contain nothing and
the branch has no commits. So unlike lens R7 on `accounting`, there is no FRD, no data model and no
task issues to score against. Every "Our v1 verdict" cell in §1 is therefore a **proposal**, not a
finding of coverage. Read the verdict column as *"where R3 says this belongs"*, and §2 as
*"what will be missing if the design set is written without this"*.

That is also an opportunity: every core-column gap that lens R7 had to raise as a BLOCKER against
113 already-specified tables can here be fixed for free, by writing the column into the first
migration.

### 0.2 The single most important finding, stated before the evidence

**We are about to build our third stock ledger, and the second one is already specified.**

| # | Stock ledger | Where | Status |
|---|---|---|---|
| 1 | `accessory_stock_levels` + `accessory_inventory_transactions` + transfers + adjustments + counts + receipts + issuance + 11 reports | `accessories` module, `V30130`–`V30380` | **shipped, in production, decision is it stays permanently separate** |
| 2 | `acc_items` · `acc_godowns` · `acc_batches` · `acc_stock_balances` · `acc_valuation_entries` · `acc_cost_layers` · `acc_cost_layer_consumptions` · `acc_stock_journals` · `acc_physical_stock_counts` · `acc_job_work_challans` | `accounting` / `accounting-base` design set, phase **P3**, migrations `V600136`–`V610143` | **specified, not built** |
| 3 | `warehouse-base` stock ledger engine + generic inbound movement port | this design set | **being designed now** |

Ledger 2 is not a stub. `accounting/docs/DATA-MODEL.md:436` specifies `acc_valuation_entries` as a
*valued stock ledger — every quantity move with its value* with `balance_quantity` and
`balance_value`; `:507` specifies `acc_stock_balances` as a quantity cache keyed
`(company_id, item_id, godown_id, batch_id, serial_number)`; `:434`–`:435` specify FIFO cost layers
and layer consumption with restore-on-credit-note. And `acc_source_documents` /
`acc_source_document_lines` / `acc_source_document_movements` (`:274`–`:277`) is **already a generic
inbound movement port** — `direction (RECEIPT·ISSUE)`, `item_external_id`, `godown_external_id`,
`quantity`, `unit_cost`, `movement_date`, materialised by a `StockMovementMaterialiser`.

That is, feature for feature, the thing `warehouse-base` is described as being.

Every ERP-embedded product in this audit — NetSuite, D365, SAP B1, Odoo, ERPNext, Acumatica, Sage,
Epicor — has exactly **one** item master and **one** stock ledger, and the financial value of stock
is a *projection of that ledger*, not a parallel one. Odoo's `stock.move` and its valuation layer
(`stock.valuation.layer`) are two views of one movement. ERPNext's `Stock Ledger Entry` carries
`qty_after_transaction`, `valuation_rate` and `stock_value_difference` in the same row that the GL
entry is derived from. Tally's stock item *is* the thing the Trading account values. The one product
in this audit that tried to run inventory as a separate truth alongside an accounting product —
**QuickBooks Commerce / TradeGecko** — was withdrawn from standalone sale, and its buyers were left
reconciling two stock figures by hand. That is the failure mode we are two design decisions away
from reproducing three times over.

The decision R3 asks for, before any table is written, is **E-001**: which module owns the
authoritative quantity ledger, and which owns value. My recommendation is stated there and assumed
throughout: **`warehouse-base` owns quantity and cost-layer mechanics; `accounting` owns value and
posts from movements handed to it through `acc_source_documents`; `accounting`'s P3 stock tables are
cut to the two it genuinely needs (`acc_valuation_entries`, `acc_cost_layers`) and
`acc_stock_balances` / `acc_godowns` / `acc_batches` / `acc_physical_stock_counts` /
`acc_stock_journals` are dropped in favour of the warehouse ones.** If that is refused, we ship two
stock truths inside one suite and no consolidated valuation is possible — see §5, which costs the
same problem for `accessories`.

### 0.3 Scoring convention

| Legend | Means |
|---|---|
| `●` | shipped and mature in the typical product of that group |
| `◐` | partial, tiered, add-on module, or weak |
| `○` | absent |
| `?` | I could not verify without web access — treat as unknown, not as absent |

Group columns are scored on the **typical/modal** product of the group, with named exceptions in
parentheses. The four groups and their anchors:

| Group | Column | Strong anchors | Weak anchors |
|---|---|---|---|
| ERP-embedded | **ERP** | NetSuite (+WMS), D365 SCM (+Advanced WMS), Odoo 18, Acumatica | Sage 200, SAP B1 without add-ons |
| Mid-market / SMB standalone | **SMB** | Cin7 Core, Unleashed, Finale, Fishbowl | Sortly (a catalogue, not a ledger), Katana (make-to-order, weak WMS), Ordoro (shipping-first) |
| India market | **IN** | Marg, Busy, Tally Prime, GoFrugal; Increff/Unicommerce/Vinculum/EasyEcom for e-comm WMS | Vyapar (mobile billing, thin stock) |
| Automotive DMS parts | **DMS** | CDK, Reynolds, Karmak, Autologue, Tekion | Indian OEM dealer DMS parts (`?` on most specifics) |

Severity: **BLOCKER** = we cannot be sold at all to the named segment · **MAJOR** = we reach the
shortlist and lose the comparison · **MINOR** = a checkbox.

Version column: `v1` · `v1.1` · `v2` · `v3` · `OUT`. **Nothing is dropped** — `OUT` appears only
where a capability belongs to another module by design, and says which.

---

## 1. CAPABILITY MATRIX

### 1.1 Item master, identity and units of measure

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 1 | Single item master shared by every module that moves stock | ● | ● | ● | ● | **v1** — `wh_items`; the whole point (E-001, E-007) |
| 2 | Item code + name + description + long description | ● | ● | ● | ● | v1 |
| 3 | Item type (STOCK · NON_STOCK · SERVICE · KIT · CORE · CONSUMABLE) | ● | ◐ (Sortly ○) | ● | ● | v1 — `wh_items.item_type` (E-007) |
| 4 | Stock UoM + purchase UoM + sales UoM, all different | ● | ◐ | ● (Tally compound units) | ● | **v1** — `wh_uom_conversions` (E-009) |
| 5 | UoM **conversion factor**, item-specific override (a "box" is 12 here, 24 there) | ● | ◐ | ● | ● | v1 (E-009) |
| 6 | Non-integer / decimal quantity with declared precision | ● | ● | ● | ◐ | v1 — `DECIMAL(18,4)` throughout (E-010) |
| 7 | Catch-weight / dual UoM (kg *and* pieces on the same move) | ◐ (D365 ●) | ◐ | ◐ | ○ | v2 (E-011) |
| 8 | Item group / category **tree**, N levels | ● | ● | ● (Tally stock groups) | ● | v1 — `wh_item_categories.parent_id` |
| 9 | Item **classification for tax** (HSN/SAC) on the item | ◐ (localised) | ○ | ● | ● | **v1** — schema, not seed (E-047) |
| 10 | Manufacturer part number distinct from our part number | ● | ◐ | ● (Marg ●) | ● | v1 — `wh_item_identifiers` (E-012) |
| 11 | Multiple barcodes / EANs per item, one primary | ● | ● | ● | ● | v1 — `wh_item_identifiers` (E-012) |
| 12 | Item **status lifecycle** (new/active/phase-out/obsolete/blocked) not just `is_active` | ● | ◐ | ◐ | ● | v1 — `wh_items.lifecycle_status` (E-008) |
| 13 | Per-warehouse item settings (stocking policy differs by godown) | ● | ◐ | ● | ● | v1 — `wh_item_locations` (E-013) |
| 14 | Item images, documents, spec attributes | ● | ● | ◐ | ● | v1.1 (reuse platform documents) |
| 15 | Variants / matrix items (size × colour) | ● | ● | ● (Busy parameterised) | ◐ | v2 (E-013) |

### 1.2 Catalogue depth — supersession, interchange, fitment

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 16 | **Supersession chain** (A → B → C) with automatic forward-resolution at order time | ◐ (Epicor ●) | ○ | ◐ (Marg `?`) | ● | **v1** — differentiator (E-055) |
| 17 | Backward traceability: "what did this part replace" for old stock | ◐ | ○ | ◐ | ● | v1 (E-055) |
| 18 | Supersession that **merges stock and demand history** of the old part | ○ | ○ | ○ | ● | v1.1 (E-056) |
| 19 | Interchange / substitute / alternate part (non-OEM equivalent) | ◐ | ○ | ◐ | ● | v1.1 (E-057) |
| 20 | Vehicle **fitment / application** (make · model · variant · year · engine) | ○ | ○ | ◐ | ● | **v1** — we already have `accessory_vehicle_compatibility` as precedent (E-058) |
| 21 | Industry catalogue standards ingest (ACES/PIES `?` for India) | ◐ (Epicor ●) | ○ | ○ | ● | v3 (E-059) |
| 22 | Kit / package definition (service package = oil + filter + gasket) | ● | ● | ● | ● | v1.1 (E-044) |
| 23 | Core / exchange part linked to its serviceable parent | ○ | ○ | ○ | ● | **v1.1** (E-063) |
| 24 | Item cross-reference to *customer's* part number | ● | ◐ | ◐ | ● | v2 |

### 1.3 Batch / lot, expiry, MRP

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 25 | Batch/lot as a **first-class row**, not a string on the balance | ● | ● | ● | ◐ | **v1** — `wh_batches` (E-014) |
| 26 | Batch attributes: mfg date, expiry date, supplier batch ref, MRP | ● | ◐ | ● | ◐ | v1 (E-014, E-016) |
| 27 | Batch-wise stock statement and batch-wise valuation | ● | ◐ | ● (Tally/Marg ●) | ◐ | v1 (E-015) |
| 28 | **FEFO** removal strategy (first-expiry-first-out) | ● (Odoo ●) | ● (Cin7 ●) | ● (Marg ●) | ○ | v1 (E-017) |
| 29 | Near-expiry alerting with configurable horizons | ◐ | ◐ | ● (Marg ●) | ○ | v1.1 (E-018) |
| 30 | Expired-stock quarantine — blocked from picking, not just flagged | ● | ◐ | ● | ○ | v1 (E-018) |
| 31 | **Expiry / breakage claim to the supplier** with claim status | ○ | ○ | ● (Marg ●) | ◐ (warranty) | v2 (E-081) |
| 32 | **MRP on the batch**, and MRP-wise stock (two MRPs, same item) | ○ | ○ | ● | ● | **v1** for schema (E-016) |
| 33 | Batch attribute inherited through assembly/repack | ● | ◐ | ◐ | ○ | v2 |
| 34 | Batch genealogy / traceability report (upstream + downstream) | ● (Odoo ●) | ◐ | ◐ | ○ | v2 (E-019) |

### 1.4 Serial numbers and unit-level traceability

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 35 | Serial as a first-class row with a status lifecycle | ● | ● | ◐ | ◐ | v1 — `wh_serials` (E-019) |
| 36 | Serial captured at receipt, validated at issue, unique per item | ● | ● | ◐ | ◐ | v1 |
| 37 | Serial → customer → warranty period, queryable after sale | ● | ◐ | ◐ | ● | v1.1 — the battery/tyre case (E-019) |
| 38 | Serialised **and** batched on the same item | ● | ◐ | ◐ | ○ | v1.1 |
| 39 | Serial history: every movement this unit ever made | ● | ◐ | ○ | ◐ | v1.1 |
| 40 | Licence plate / handling unit / pallet ID (a container of stock) | ● (D365 ●, NetSuite ●) | ◐ (SkuVault ●) | ◐ (Increff ●) | ○ | v2 (E-025) |
| 41 | Bulk serial capture by scan range | ● | ● | ◐ | ◐ | v1.1 |

### 1.5 Locations — warehouse / godown, bin, zone, ownership

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 42 | Multiple warehouses/godowns per branch, and per company | ● | ● | ● | ● | v1 — `wh_warehouses` |
| 43 | Warehouse **bound to a platform branch and its GSTIN** | ◐ | ○ | ● | ● | **v1** — `wh_warehouses.branch_id` (E-048) |
| 44 | Location **hierarchy/tree** (site → zone → aisle → rack → bin) | ● (Odoo ●, D365 ●) | ◐ (Cin7 ●) | ◐ (Increff ●) | ◐ | v1 — `wh_locations.parent_id` (E-020) |
| 45 | Location types: stock · receiving · staging · quarantine · scrap · transit · virtual | ● | ◐ | ○ | ◐ | **v1** (E-021) |
| 46 | Bin capacity / storage category / restriction rules | ● | ◐ | ◐ | ○ | v2 (E-022) |
| 47 | **Putaway rules** (item/category → destination location) | ● | ◐ (Cin7 ●) | ◐ | ○ | v2 (E-023) |
| 48 | Removal strategy per location/item (FIFO · LIFO · FEFO · closest) | ● | ◐ | ◐ | ○ | v1 FIFO/FEFO, v2 rest (E-017) |
| 49 | Multi-bin for one item; primary pick bin + overflow | ● | ◐ | ◐ | ● | v1 |
| 50 | **Stock ownership** — consignment stock we hold but do not own | ● (Odoo `owner_id` ●) | ◐ | ◐ | ● (OEM consignment `?`) | **v1 schema, v2 feature** (E-024) |
| 51 | Virtual/negative counterpart locations making every move two-sided | ● (Odoo ●) | ○ | ○ | ○ | v1 (E-026) |

### 1.6 Inbound — purchase order, receipt, putaway, inspection

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 52 | Purchase order with expected date, partial receipt, over/under tolerance | ● | ● | ● | ● | v1 — `wh_purchase_orders` (E-027) |
| 53 | Goods receipt note distinct from the supplier invoice | ● | ● | ● | ● | **v1** — `wh_goods_receipts` (E-027) |
| 54 | Three-way match PO ↔ GRN ↔ bill, variance surfaced | ● | ◐ | ● | ● | v1.1 — value leg is `accounting` (E-028) |
| 55 | Multi-step receipt (receive → inspect → putaway) configurable | ● | ◐ | ○ | ◐ | v2 (E-023) |
| 56 | Quality inspection / quarantine with accept-reject-rework | ● | ◐ | ◐ | ◐ | v2 (E-029) |
| 57 | ASN / inbound shipment notice from the supplier | ● | ◐ (SkuVault ●) | ◐ | ● (OEM ASN ●) | v2 (E-062) |
| 58 | Receive **against the OEM invoice file**, auto-match lines | ◐ | ○ | ◐ | ● | v1.1 (E-062) |
| 59 | Back-order tracking with supplier ETA and customer notification | ● | ● | ● | ● | v1.1 (E-061) |
| 60 | Blind receiving (quantities hidden from the receiver) | ● | ◐ | ○ | ● | v2 |
| 61 | Bulk-import receipts from a spreadsheet | ◐ | ● | ● | ◐ | v1 — precedent exists in `accessories` (`accessory_stock_receipt_import_staging`) |

### 1.7 Outbound — allocation, pick, pack, ship

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 62 | Sales order → allocation → pick → despatch, as distinct states | ● | ● | ◐ | ● | v1.1 (E-030) |
| 63 | Delivery note / delivery challan as a numbered document | ● | ● | ● | ● | **v1** (E-049) |
| 64 | Pick list generation, batch/wave/cluster picking | ● (NetSuite WMS ●, D365 ●) | ◐ (SkuVault ●) | ◐ (Increff ●) | ◐ | v2 (E-031) |
| 65 | Pack into cartons, packing slip, carton contents | ● | ● | ◐ | ○ | v2 |
| 66 | Shipping carrier integration, label and tracking | ◐ | ● (Ordoro ●) | ● (Unicommerce ●) | ○ | v3 (E-079) |
| 67 | Direct issue with no order (counter sale / workshop issue) | ● | ◐ | ● | ● | **v1** (E-064, E-065) |
| 68 | Drop-ship / direct-to-customer without touching stock | ● | ● | ◐ | ● | v2 |
| 69 | Partial despatch with the balance staying open | ● | ● | ● | ● | v1.1 |

### 1.8 Transfers and in-transit

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 70 | Transfer between warehouses of the **same** branch | ● | ● | ● | ● | v1 |
| 71 | Transfer between **branches**, i.e. between GSTINs | ● (localised) | ◐ | ● | ● | **v1** (E-050) |
| 72 | **In-transit as a real stock location**, not a status flag | ● | ◐ (Cin7 ●) | ◐ | ● | **v1** (E-032) |
| 73 | Ship qty ≠ receive qty → transit variance with a reason | ● | ◐ | ◐ | ● | v1 (E-032) |
| 74 | Transfer request → approval → issue → receipt workflow | ● | ◐ | ◐ | ● | v1 — `accessories` already has the 5-state ladder |
| 75 | **Tax invoice / delivery challan on the branch transfer** | ◐ (localised) | ○ | ● | ● | **v1 schema** (E-050) |
| 76 | **E-way bill for the transfer** | ○ | ○ | ● | ● | v1 hooks, v1.1 adapter (E-051) |
| 77 | Dealer-to-dealer trade (sell/lend a part to another dealership) | ○ | ○ | ◐ | ● | v2 (E-070) |
| 78 | Transfer costing: at cost, at transfer price, with a mark-up | ● | ◐ | ● | ● | v1.1 (E-036) |
| 79 | Intercompany transfer (two legal entities) | ● | ◐ | ◐ | ◐ | v3 |

### 1.9 Adjustments, scrap, write-off, reason codes

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 80 | Quantity adjustment up/down with a **mandatory reason code** | ● | ● | ◐ | ● | v1 — `wh_reason_codes` (E-033) |
| 81 | Reason code carries the **GL account** the write-off posts to | ● | ◐ | ◐ | ● | **v1** (E-033) |
| 82 | Adjustment approval threshold by value / by user | ● | ◐ | ◐ | ● | v1.1 (E-034) |
| 83 | Scrap as a distinct movement type, not a negative adjustment | ● | ◐ | ◐ | ● | v1 |
| 84 | Revaluation (value changes, quantity does not) | ● | ◐ | ● | ● | v1.1 — `accounting` posts (E-037) |
| 85 | Adjustment reversal that keeps both rows in the ledger | ● | ◐ | ◐ | ● | v1 (E-026) |
| 86 | Damage / shrinkage / theft split as separate reasons for reporting | ● | ◐ | ◐ | ● | v1 seed |

### 1.10 Physical count and cycle count

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 87 | Full physical count with freeze / snapshot of book quantity | ● | ● | ● | ● | v1 (E-038) |
| 88 | **Cycle counting by ABC class / count class with a schedule** | ● | ◐ (SkuVault ●) | ◐ | ● | v1.1 (E-039) |
| 89 | Count sheets by bin, blind count (book qty hidden) | ● | ● | ◐ | ● | v1 (E-038) |
| 90 | Variance review, recount, then a **posting step** with approval | ● | ◐ | ◐ | ● | v1 (E-038) |
| 91 | Count posts as a valued adjustment to the GL, not a silent overwrite | ● | ◐ | ● | ● | **v1** (E-038) |
| 92 | Counting while transactions continue (snapshot semantics) | ● | ◐ | ○ | ◐ | v2 |
| 93 | Scanner-driven counting on a mobile device | ● | ● | ◐ | ● | v1.1 (E-072) |

### 1.11 Replenishment and demand planning

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 94 | Min / max / reorder point **per item per warehouse** | ● | ● | ● | ● | **v1** — `wh_item_locations` (E-013, E-040) |
| 95 | Reorder report / low-stock alert | ● | ● | ● | ● | v1 |
| 96 | **Auto-generate the purchase order / stock order from the shortfall** | ● | ● | ◐ | ● | v1.1 (E-040) |
| 97 | Demand history driving a **computed** stocking level, not typed-in min/max | ● (NetSuite ●, D365 ●) | ◐ (Finale ●) | ○ | ● (best-stocking-level ●) | **v2 — the DMS-parts standard** (E-066) |
| 98 | Phase-in / phase-out control on a new or dying part | ◐ | ○ | ○ | ● | v2 (E-066) |
| 99 | Lost-sale capture feeding demand | ○ | ○ | ○ | ● | **v1.1** (E-067) |
| 100 | Seasonality / lead-time variability / safety stock formula | ● | ◐ | ○ | ◐ | v3 |
| 101 | Suggested transfer from a sister branch before buying | ● | ◐ | ◐ | ● | v2 (E-041) |
| 102 | Days-supply and months-supply as maintained columns | ● | ◐ | ○ | ● | v2 (E-077) |

### 1.12 Reservation, allocation, ATP

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 103 | Soft reservation (`quantity_reserved`) against an order | ● | ● | ◐ | ● | v1 (E-042) |
| 104 | **Hard allocation to a specific batch/serial/bin** | ● | ◐ | ○ | ◐ | v1.1 (E-042) |
| 105 | Reservation **expiry** — held stock released after N days | ● | ◐ | ○ | ● (special order ●) | v1.1 (E-043) |
| 106 | Available-to-promise = on hand − reserved + inbound by date | ● | ◐ | ○ | ◐ | v2 (E-042) |
| 107 | Reservation priority / order ranking when stock is short | ● | ◐ | ○ | ◐ | v2 |
| 108 | Reservation for a **workshop job card** that is not yet an order | ◐ | ○ | ○ | ● | **v1** (E-065) |

### 1.13 Kits, assembly, BOM, job work

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 109 | Kit / bundle sold as one line, stock relieved by components | ● | ● (Zoho composite ●) | ● | ● | v1.1 (E-044) |
| 110 | Assembly / disassembly building stock of a parent item | ● | ● | ● (Tally mfg journal ●) | ◐ | v1.1 (E-044) |
| 111 | Multi-level BOM with routings and WIP | ● | ◐ (Katana ●) | ◐ | ○ | v3 — `OUT of warehouse` if a manufacturing module appears |
| 112 | Repack / conversion (bulk drum → 1L bottles) | ● | ◐ | ● | ○ | v2 |
| 113 | **Job work / subcontracting: challan out, 4-year clock, ITC-04** | ◐ (localised) | ○ | ● | ◐ | v2 — schema in v1 (E-054) |
| 114 | Component substitution at assembly time | ● | ◐ | ◐ | ○ | v3 |

### 1.14 Costing, valuation, landed cost

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 115 | Valuation method **per item** (not one global setting) | ● | ◐ | ● | ● | v1 — `wh_items.valuation_method` (E-035) |
| 116 | Moving average (AVCO) with a maintained `average_cost` | ● | ● | ● | ● | v1 |
| 117 | **FIFO with real cost layers**, not a computed approximation | ● | ◐ | ● | ● | v1 (E-035) |
| 118 | Standard cost with purchase-price-variance posting | ● | ◐ | ● (Tally ●) | ◐ | v2 |
| 119 | Specific identification for serialised items | ● | ◐ | ◐ | ● | v1.1 |
| 120 | Return restores the **original** cost layer | ● | ◐ | ● | ● | v1.1 (E-035) |
| 121 | **Landed cost** apportioned by value / qty / weight / volume | ● | ● (Unleashed ●) | ● (Marg ●) | ◐ | **v1.1** (E-036) |
| 122 | Landed cost applied **after** the stock was issued (retro) | ● | ◐ | ◐ | ○ | v2 (E-036) |
| 123 | Valuation as at a **back date** (stock as on 31-Mar) | ● | ◐ | ● | ● | **v1** (E-053) |
| 124 | Inventory-to-GL reconciliation as a blocking close item | ● | ○ | ◐ | ◐ | v1.1 — owned by `accounting` (E-002) |
| 125 | Negative-cost / zero-cost issue policy and its alerting | ● | ◐ | ● | ● | v1 (E-045) |

### 1.15 Controls — negative stock, period lock, approvals, audit

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 126 | **Negative stock policy: block / warn / allow, per item + per warehouse** | ● | ● | ● | ● | **v1** (E-045) |
| 127 | Back-dated movement permitted only inside an open period | ● | ◐ | ● | ● | v1 (E-046) |
| 128 | Stock period lock independent of the accounting period lock | ● | ○ | ◐ | ◐ | v1.1 (E-046) |
| 129 | Immutable movement ledger — corrections by reversal, never update | ● | ◐ | ● | ● | **v1** (E-026) |
| 130 | Full audit trail of who moved what, when, from where | ● | ● | ● | ● | v1 — platform audit |
| 131 | Approval workflow on adjustment / write-off / return above a limit | ● | ◐ | ◐ | ● | v1.1 (E-034) |
| 132 | Branch-scoped and warehouse-scoped record access | ● | ◐ | ◐ | ● | **v1** — platform pattern exists (E-046) |

### 1.16 Barcode, labels, scanning, mobile

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 133 | Scan a barcode into a document line | ● | ● | ● | ● | v1 (E-071) |
| 134 | Item / bin / batch **label design and printing** | ● | ● | ● | ● | v1.1 (E-073) |
| 135 | Dedicated mobile scanning app for receive / pick / count / transfer | ● (NetSuite WMS ●, D365 ●) | ● (SkuVault ●, Cin7 ●) | ● (Increff ●) | ● | **v1.1** — `mobile/` counterpart is mandatory here (E-072) |
| 136 | Offline scanning with deferred sync | ◐ | ◐ | ◐ | ◐ | v3 (E-074) |
| 137 | GS1-128 / QR parsing (item + batch + expiry in one scan) | ● | ◐ | ◐ | ○ | v2 (E-071) |
| 138 | Print a bin label from the location record | ● | ● | ◐ | ● | v1.1 |

### 1.17 Pricing and price files

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 139 | Multiple price lists, by customer / channel / branch | ● | ● | ● | ● | v1.1 — `accounting` has `acc_price_lists` (E-078) |
| 140 | Cost-plus / margin-based pricing matrix by price band | ◐ | ◐ | ◐ | ● | v2 (E-069) |
| 141 | MRP-driven pricing with back-calculated taxable value | ○ | ○ | ● | ● | v1.1 (E-016) |
| 142 | **OEM price file / price tape load with effective dates** | ○ | ○ | ◐ | ● | **v1.1** (E-068) |
| 143 | **Price escalation: revalue on-hand stock when the OEM raises price** | ○ | ○ | ◐ | ● | v2 (E-068) |
| 144 | Price protection claim to the OEM on a price drop | ○ | ○ | ○ | ● | v2 (E-068) |
| 145 | Scheme / free-quantity (10+1) handling | ○ | ○ | ● (Marg ●) | ◐ | v2 (E-080) |
| 146 | Quantity-break and period discounts | ● | ● | ● | ● | v1.1 |

### 1.18 Returns — sales, purchase, RMA, claims

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 147 | Sales return restoring stock, with a reason and a restocking fee | ● | ● | ● | ● | v1.1 — `accessories` has a returns module already |
| 148 | Purchase return / debit note to the supplier | ● | ● | ● | ● | v1.1 |
| 149 | RMA authorisation number before the goods arrive | ● | ● | ◐ | ● | v2 |
| 150 | Return to a **quarantine** location pending inspection | ● | ◐ | ◐ | ● | v2 (E-029) |
| 151 | **OEM obsolescence return with an allowance window and %** | ○ | ○ | ○ | ● | **v1.1** (E-060) |
| 152 | **Core return / core bank** | ○ | ○ | ○ | ● | **v1.1** (E-063) |
| 153 | **Warranty parts scrap-and-hold with a retention clock** | ○ | ○ | ○ | ● | **v1.1** (E-064) |
| 154 | Supplier claim register (damage / shortage / expiry / price) | ◐ | ○ | ● (Marg ●) | ● | v2 (E-081) |

### 1.19 India statutory on stock — see §3

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 155 | HSN on the item, UQC on the line | ◐ (add-on) | ○ | ● | ● | **v1 schema** (E-047) |
| 156 | Branch = GSTIN; a transfer between GSTINs is a **taxable supply** | ◐ | ○ | ● | ● | **v1 schema** (E-048, E-050) |
| 157 | Delivery challan for a non-sale movement | ◐ | ○ | ● | ● | **v1** (E-049) |
| 158 | E-way bill Part A + Part B with transport attributes | ○ | ○ | ● | ● | v1 schema, v1.1 adapter (E-051) |
| 159 | Godown-wise stock statement (a bank/statutory deliverable) | ◐ | ○ | ● | ● | **v1** (E-052) |
| 160 | Stock as at a back date for 44AB / bank stock statements | ◐ | ○ | ● | ● | **v1** (E-053) |
| 161 | Job-work challan and the ITC-04 clock | ○ | ○ | ● | ◐ | v1 schema, v2 feature (E-054) |
| 162 | Batch + expiry + MRP as statutory-grade fields | ◐ | ◐ | ● | ◐ | **v1** (E-014, E-016) |

### 1.20 Reporting and KPIs

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 163 | Stock summary / stock on hand by item × warehouse × bin × batch | ● | ● | ● | ● | v1 |
| 164 | **Stock ledger / movement register — every move, drillable** | ● | ● | ● | ● | **v1** (E-075) |
| 165 | Valuation report with method, cost and value | ● | ◐ | ● | ● | v1 |
| 166 | Ageing / no-movement buckets (0-3-6-12-24 months) | ● | ◐ | ● | ● | **v1** (E-076) |
| 167 | **Fill rate / service level (off-shelf first-pick)** | ◐ | ○ | ○ | ● | **v1.1** (E-077) |
| 168 | **Inventory turns**, true turns, days supply | ● | ◐ | ◐ | ● | v1.1 (E-077) |
| 169 | **Obsolescence %** and idle-stock value | ◐ | ○ | ◐ | ● | v1.1 (E-077) |
| 170 | ABC / movement classification, recomputed on a schedule | ● | ◐ | ◐ | ● | v2 (E-066) |
| 171 | Stock reconciliation: physical vs book vs GL | ● | ○ | ◐ | ◐ | v1.1 (E-002) |
| 172 | Shortage / lost-sale report | ○ | ○ | ◐ | ● | v1.1 (E-067) |
| 173 | Supplier performance: OTIF, short-supply, lead-time actuals | ● | ◐ | ◐ | ● | v2 |
| 174 | Scheduled report delivery / subscriptions | ● | ● | ◐ | ● | v2 — platform |

### 1.21 Integration, API, marketplace, 3PL

| # | Capability | ERP | SMB | IN | DMS | Our v1 verdict |
|---|---|---|---|---|---|---|
| 175 | Documented REST API over every stock object | ● | ● | ◐ | ◐ | v1 |
| 176 | **Idempotent inbound movement port** with replay and dedupe | ● | ◐ | ○ | ◐ | **v1** — the adapter contract (E-003) |
| 177 | Outbound events on stock change (webhooks) | ● | ● | ◐ | ◐ | v1.1 (E-079) |
| 178 | Marketplace / e-commerce stock sync (Amazon, Flipkart, Shopify) | ◐ | ● (Cin7 ●) | ● (Unicommerce/EasyEcom/Vinculum ●) | ○ | v2/v3 (E-079) |
| 179 | 3PL: multi-owner stock, owner-segregated valuation | ◐ | ◐ | ● (Increff ●) | ○ | **v2** — `warehouse-3pl` (E-024, E-082) |
| 180 | 3PL billing: storage / handling / per-line charges | ○ | ○ | ● | ○ | v3 (E-082) |
| 181 | EDI with suppliers/OEM | ● | ◐ (Cin7 Omni ●) | ◐ | ● | v3 (E-062) |
| 182 | Bulk import / export on every master and document | ● | ● | ● | ● | v1 — platform pattern |

### 1.22 DMS-parts summary — the differentiator (detail in §4)

| # | Capability | Generic WMS (best of ERP+SMB) | IN generic | **DMS** | Our v1 verdict |
|---|---|---|---|---|---|
| 183 | Supersession chain resolved at order entry | ◐ | ◐ | ● | **v1** (E-055) |
| 184 | Best stocking level from demand history + phase-in/out | ◐ | ○ | ● | v2 (E-066) |
| 185 | Source / order type: stock · daily · **VOR/emergency** | ○ | ○ | ● | **v1.1** (E-061) |
| 186 | OEM order file out, acknowledgement/allocation in | ○ | ○ | ● | v1.1 (E-062) |
| 187 | Obsolescence return with allowance window | ○ | ○ | ● | v1.1 (E-060) |
| 188 | Core / exchange with a core bank | ○ | ○ | ● | v1.1 (E-063) |
| 189 | Warranty parts scrap-and-hold clock | ○ | ○ | ● | v1.1 (E-064) |
| 190 | Counter sale ticket, keyboard-first | ◐ | ● | ● | **v1** (E-065) |
| 191 | Workshop RO / job-card issue **and return of unused parts** | ◐ | ○ | ● | **v1** (E-065) |
| 192 | Open-RO parts WIP valuation | ○ | ○ | ● | v1.1 (E-065) |
| 193 | Price file load + price escalation + protection claim | ○ | ◐ | ● | v1.1/v2 (E-068) |
| 194 | Lost sale recording | ○ | ○ | ● | v1.1 (E-067) |
| 195 | Fill rate · turns · obsolescence % as first-class KPIs | ◐ | ○ | ● | v1.1 (E-077) |
| 196 | Dealer trade between dealerships | ○ | ◐ | ● | v2 (E-070) |

---

## 2. FINDINGS

Format: **`E-nnn` · title** — severity · module · **version**.
*Gap* → *Why it matters to an Indian multi-vertical buyer* → *Recommendation (tables, columns, screens)*.

### 2.1 Architecture and module boundary

---
**E-001 · Decide which module owns the authoritative quantity ledger, before the first migration** — **BLOCKER** · `warehouse-base` + `accounting` · **v1**

*Gap.* Two design sets specify the same engine. `accounting/docs/DATA-MODEL.md:436` gives
`acc_valuation_entries` a `balance_quantity`; `:507` gives `acc_stock_balances` a
`quantity_on_hand` and a `quantity_reserved`; `:434` gives `acc_cost_layers` a
`quantity_remaining`. `warehouse-base` is described as "the stock ledger engine". Both cannot be
authoritative for the same number.

*Why it matters.* Every ERP-embedded comparator has one. A buyer running dealership + workshop +
accessories will ask one question in the demo — *"what is my stock worth right now?"* — and if the
answer requires reconciling two tables, the demo is over. This is precisely the failure that killed
QuickBooks Commerce as a standalone SKU.

*Recommendation.* Write an **ownership statement** into the data model before any table:
`warehouse-base` owns **quantity, location, batch, serial, reservation and cost layers**;
`accounting` owns **value in the GL** and derives it from movements posted through
`acc_source_documents` / `acc_source_document_movements`. Concretely: keep
`acc_valuation_entries` and `acc_cost_layers` (they are the GL-side projection and the tax-basis
history), **delete `acc_stock_balances`, `acc_godowns`, `acc_batches`, `acc_stock_journals`,
`acc_physical_stock_counts` from the accounting P3 scope** and repoint their FKs at
`wh_warehouses` / `wh_batches`. `acc_items` survives as the *accounting view* of `wh_items`
(account defaults only), joined by `wh_items.accounting_item_id`.

---
**E-002 · Inventory-to-GL reconciliation must be a named, blocking deliverable owned by one side** — **MAJOR** · `warehouse` + `accounting` · **v1.1**

*Gap.* `accounting` already makes inventory-to-GL a blocking period-close precondition
(`DATA-MODEL.md:848`). Nothing in the warehouse design set is yet obliged to produce the number it
reconciles against.

*Why it matters.* NetSuite, D365 and Acumatica all ship this report and auditors ask for it at
every 44AB audit. A blocking close condition with no upstream producer will simply be disabled in
production, which is worse than not having it.

*Recommendation.* `warehouse` ships report **`stock-valuation-vs-gl`**: per company × branch ×
inventory account, book value from `wh_valuation_snapshots` vs GL balance from `accounting`, with a
variance column and a drill to `wh_stock_movements`. The `PeriodClosePrecondition` bean on the
accounting side reads it. Name the report in both design sets so neither can ship without it.

---
**E-003 · The inbound movement port already exists in `accounting`; do not design a second envelope** — **MAJOR** · `warehouse-base` · **v1**

*Gap.* `acc_source_documents` (`:274`) + `_lines` (`:275`) + `_movements` (`:277`) is a complete,
idempotent, replayable inbound port with `idempotency_key`, `payload_sha256`, `revision`,
`superseded_by_id`, retry columns and a `status` ladder. `warehouse-base`'s "generic inbound
movement port" is the same object under a different name.

*Why it matters.* Adapter authors (dealer, services, field-service, assets, future logistics) will
otherwise implement two envelope shapes with two idempotency schemes, and the first duplicate
delivery will double-count stock.

*Recommendation.* One envelope shape, one idempotency contract, defined once in
`warehouse-base` as `wh_inbound_documents` / `wh_inbound_movements` with **identical column names
and semantics** to the accounting pair, and an explicit statement that a movement accepted by
warehouse is forwarded to accounting as an `acc_source_document` with the same
`idempotency_key`. Adapter contract: `(source_module, source_doc_type, source_doc_id, revision)`
unique; replay is a no-op; supersession by revision, never by delete.

---
**E-004 · Name the adapter contract's *reverse* direction — warehouse must ask the vertical a question** — **MAJOR** · `warehouse-base` · **v1**

*Gap.* A port that only accepts movements cannot support reservation against a job card, a lost
sale against a counter enquiry, or "which RO consumed this part". Those need warehouse to hold a
back-reference to a document it does not own.

*Recommendation.* Every movement and reservation row carries a neutral triple
`(source_module, source_entity, source_entity_id)` plus `source_reference_number` for display —
**generic columns, deliberately not FKs**, exactly as `acc_source_documents.subledger_document_id`
is (`DATA-MODEL.md:274`). The adapter registers a display resolver so `wh_stock_movements` can
render "RO-2026-004512" without warehouse importing the services module.

---
**E-005 · One module list, one migration range, before anyone writes `V…`** — **MINOR** · all · **v1**

*Gap.* CLAUDE.md's MODULES table has no warehouse rows. Four modules need four ranges, and
`warehouse-base` must migrate strictly before `warehouse`, which must migrate before any adapter.

*Recommendation.* Reserve, e.g., `warehouse-base V900000-V909999`, `warehouse V910000-V919999`,
`warehouse-adapter-* V920000-V929999`, `warehouse-3pl V930000-V939999`, and record the ordering
rule. The `accounting` set already burned a round on platform↔client migration ordering; copy the
resolution rather than rediscovering it.

---
**E-006 · `warehouse-adapter-<vertical>` must be provably generic — prove it with two verticals in v1** — **MAJOR** · `warehouse-adapter-*` · **v1**

*Gap.* An adapter layer designed against one consumer becomes that consumer's API with an
abstraction tax. Dealer and services have genuinely different shapes: dealer issues parts to a
vehicle, services issues to a job card, assets issues to an asset, field-service issues from a van.

*Recommendation.* v1 ships **two** adapters — `warehouse-adapter-services` (workshop job issue and
return, the largest consumer) and `warehouse-adapter-dealer` (PDI and accessory fitment) — and the
port is accepted only if neither required a base-schema change the other did not want. `assets`
and `field-service` adapters are v2; a `logistics` adapter is v3.

### 2.2 Item master, identity and units

---
**E-007 · One item master, with an `item_type` that admits non-stock and core items** — **BLOCKER** · `warehouse-base` · **v1**

*Gap.* If `wh_items` is modelled as "a part", the workshop cannot bill a consumable, the parts
department cannot carry a core, and the assets module cannot draw a spare.

*Recommendation.* `wh_items(id, company_id, code, name, description, item_type, item_category_id,
lifecycle_status, stock_uom_id, valuation_method, is_batch_tracked, is_serial_tracked,
is_expiry_tracked, shelf_life_days, tax_classification_code, accounting_item_id, is_active,
uk(company_id, code))` with `item_type ∈ (STOCK, NON_STOCK, SERVICE, KIT, CORE, CONSUMABLE, ASSET)`.
`valuation_method` is **per item** (`AVCO·FIFO·STANDARD·SPECIFIC`), because a dealership values
parts AVCO and vehicles specific-identification in the same books.

---
**E-008 · Item lifecycle status, not `is_active`** — **MAJOR** · `warehouse-base` · **v1**

*Gap.* `is_active` cannot express "no longer orderable but still stocked", which is exactly the
state a superseded or phase-out part lives in for two years.

*Recommendation.* `wh_items.lifecycle_status ∈ (NEW, ACTIVE, PHASE_OUT, OBSOLETE, BLOCKED)` with
guards: `OBSOLETE` blocks purchase and reorder but permits issue and return; `BLOCKED` blocks all
movement except adjustment. `is_active` remains only as the platform grid convention.

---
**E-009 · Three UoMs and an item-specific conversion** — **MAJOR** · `warehouse-base` · **v1**

*Gap.* Tally's compound units, SAP B1's UoM groups and Odoo's UoM categories all exist because
purchasing in cartons and issuing in pieces is the normal case, not the exotic one. Oil in drums
issued in litres is the workshop's daily reality.

*Recommendation.* `wh_uoms(code, name, uom_category_id, is_base)` +
`wh_uom_conversions(item_id NULLABLE, from_uom_id, to_uom_id, factor DECIMAL(18,6), uk(item_id,
from_uom_id, to_uom_id))` — a null `item_id` is the global conversion, a non-null row overrides it.
`wh_items.purchase_uom_id` and `sales_uom_id` default document lines. **Every movement stores both
the entered UoM and the base-UoM quantity**: `quantity_entered`, `entered_uom_id`, `quantity_base`.

---
**E-010 · Quantity precision fixed once, in the design set** — **MINOR** · `warehouse-base` · **v1**

*Recommendation.* `DECIMAL(18,4)` for every quantity and `DECIMAL(18,4)` for unit cost, matching the
precedent already set at
`accessories/.../V30131__Create_accessory_inventory_transactions_table.sql:13,23,24` and adopted by
`accounting`. Value columns are `DECIMAL(19,4)`. State the rounding rule for base-UoM conversion
(round-half-up at 4dp, residual to the last line) or two modules will round differently.

---
**E-011 · Catch-weight / dual UoM** — **MINOR** · `warehouse-base` · **v2**

*Gap.* D365 ships it; nobody in our vertical set needs it today. It becomes real if a
logistics/3PL vertical takes on food or metals.

*Recommendation.* Do not build, but do not foreclose: keep `quantity_base` and a nullable
`secondary_quantity` + `secondary_uom_id` on movements from v1 so v2 is an additive change.

---
**E-012 · Item identifiers table — barcodes, OEM part numbers, supplier codes** — **MAJOR** · `warehouse-base` · **v1**

*Gap.* One `barcode VARCHAR(100)` column on the item is what `accessory_products` has
(`V30050:11`) and it is already insufficient: a part has a dealer part number, an OEM part number,
an EAN on the carton, a different EAN on the inner box and a supplier's own code.

*Recommendation.* `wh_item_identifiers(item_id, identifier_type, identifier_value, is_primary,
issued_by_party_id NULL, uk(company_id, identifier_type, identifier_value))` with
`identifier_type ∈ (BARCODE_EAN13, BARCODE_UPC, GS1_128, OEM_PART_NO, SUPPLIER_CODE,
CUSTOMER_CODE, LEGACY_CODE, QR)`. Scan lookup and import matching resolve through this table only —
never through `wh_items.code` alone.

---
**E-013 · Per-item-per-warehouse settings, or min/max is meaningless** — **MAJOR** · `warehouse-base` · **v1**

*Gap.* `accessory_products` puts `min_stock_level`, `max_stock_level`, `reorder_point`,
`reorder_quantity`, `lead_time_days` on the **item** (`V30050:32-36`). A part that turns weekly at
the city branch and annually at the district branch cannot share one reorder point. Every ERP
comparator holds these per location; ERPNext holds a reorder table per warehouse, NetSuite per
location.

*Recommendation.* `wh_item_locations(item_id, warehouse_id, min_quantity, max_quantity,
reorder_point, reorder_quantity, safety_stock, lead_time_days, primary_bin_id, abc_class,
movement_class, stocking_status, is_stocked, last_demand_recalc_at, uk(item_id, warehouse_id))`.
Item-level values become **defaults** used to seed this table, not the operative numbers.

### 2.3 Batch, expiry, MRP, serial

---
**E-014 · `wh_batches` as a row, not `batch_number VARCHAR(50)` on the balance** — **BLOCKER** · `warehouse-base` · **v1**

*Gap.* `accessory_stock_levels` carries `batch_number VARCHAR(50)`, `serial_number VARCHAR(100)`,
`expiry_date DATE` as **columns on the balance row** (`V30130:18-20`). So the same batch in two
bins has two expiry dates that can disagree, there is nowhere to put the supplier's batch reference
or the MRP, and a batch cannot be blocked.

*Why it matters.* Batch-wise stock is not a nicety in India — it is how lubricants, tyres,
batteries, paint and every FMCG/pharma line is bought, sold and recalled, and Tally, Busy and Marg
all model it as an entity.

*Recommendation.* `wh_batches(id, company_id, item_id, batch_number, supplier_batch_ref,
manufactured_date, expiry_date, best_before_date, mrp_amount, batch_status, received_at,
uk(company_id, item_id, batch_number))` with `batch_status ∈ (ACTIVE, QUARANTINE, EXPIRED,
BLOCKED, RECALLED)`. Balances and movements FK to `wh_batches.id`, never to a string.

---
**E-015 · Batch-wise valuation, not just batch-wise quantity** — **MAJOR** · `warehouse-base` · **v1**

*Gap.* Two batches of the same part bought six months apart at different landed costs are one
average cost if the batch is not a costing dimension.

*Recommendation.* `wh_cost_layers` is keyed `(item_id, warehouse_id, batch_id NULL, serial_number
NULL, receipt_date, unit_cost, quantity_in, quantity_remaining)`. For a batch-tracked item the layer
**is** the batch. Report `stock-valuation` groups by batch when the item is batch-tracked.

---
**E-016 · MRP on the batch, and MRP-wise stock** — **MAJOR** · `warehouse-base` + `warehouse` · **v1 (schema) / v1.1 (feature)**

*Gap.* Indian retail law prints an MRP on the pack; the same SKU legitimately sits in the godown
under two MRPs after a price revision, and they must be sold and reported separately. Only the India
group and DMS model this; no ERP-embedded or SMB comparator does natively.

*Recommendation.* `wh_batches.mrp_amount DECIMAL(19,4)` in v1. In v1.1, MRP becomes a balance
dimension for non-batch-tracked items too, via `wh_stock_balances.mrp_amount` participating in the
unique key, plus a `stock-by-mrp` report and MRP-inclusive back-calculation of the taxable value on
the issue document.

---
**E-017 · FEFO as a removal strategy, chosen per item/location** — **MAJOR** · `warehouse-base` · **v1**

*Gap.* Without FEFO an expiry-tracked item will be picked FIFO by receipt date and the near-expiry
stock will rot in the bin. Odoo, Cin7 and Marg all ship it.

*Recommendation.* `wh_item_locations.removal_strategy ∈ (FIFO, LIFO, FEFO, MANUAL)` defaulting from
`wh_items`; the allocation service orders candidate layers by `expiry_date` when `FEFO`. `LIFO`
and `CLOSEST_LOCATION` are v2.

---
**E-018 · Expiry quarantine is a state, not an alert** — **MAJOR** · `warehouse` · **v1**

*Gap.* An "expiry alert" that leaves the stock pickable does not prevent selling an expired part.

*Recommendation.* A `@Scheduled` job moves batches past `expiry_date` to `batch_status = EXPIRED`,
which the allocation service refuses to pick, and raises a notification at
`expiry_date − wh_items.near_expiry_days`. **This is a dated obligation: it needs the job, the
notification recipients and the report, or it is a promise nothing keeps.** Report
`near-expiry-stock` with configurable buckets (30/60/90 days).

---
**E-019 · Serial as a row with a lifecycle, and a post-sale query path** — **MAJOR** · `warehouse-base` · **v1 (schema) / v1.1 (history)**

*Gap.* `serial_number VARCHAR(100)` on the balance cannot answer "where is this battery now", "who
did we sell it to" or "is it in warranty" — the three questions a dealership asks about a serialised
part.

*Recommendation.* `wh_serials(id, company_id, item_id, serial_number, batch_id NULL,
current_warehouse_id, current_location_id, serial_status, received_at, issued_at,
sold_to_party_id, warranty_start_date, warranty_end_date, uk(company_id, item_id, serial_number))`
with `serial_status ∈ (IN_STOCK, RESERVED, ISSUED, SOLD, RETURNED, SCRAPPED, IN_TRANSIT)`. Genealogy
report (`wh_serial_movements`) is v1.1; assembly inheritance is v2.

### 2.4 Locations, bins, ownership

---
**E-020 · Location hierarchy, not a flat bin list** — **MAJOR** · `warehouse-base` · **v1**

*Gap.* `accessory_storage_bins` is flat. Odoo, D365 and NetSuite all model locations as a tree
because "count zone A", "block the mezzanine" and "report by aisle" are all tree operations.

*Recommendation.* `wh_locations(id, warehouse_id, parent_id, code, name, location_type, path,
is_pickable, is_countable, capacity_uom_id, capacity_quantity, storage_category_id, is_active,
uk(warehouse_id, code))`. Maintain a materialised `path` column for subtree queries — no recursive
CTE in the grid path.

---
**E-021 · Location types, including transit, quarantine and scrap** — **MAJOR** · `warehouse-base` · **v1**

*Gap.* Without typed locations, in-transit becomes a status flag (E-032), quarantine becomes a
comment, and scrap becomes a negative adjustment with no audit.

*Recommendation.* `location_type ∈ (STOCK, RECEIVING, STAGING, QUARANTINE, SCRAP, TRANSIT,
PRODUCTION, VAN, CUSTOMER, SUPPLIER, LOSS_GAIN, CORE_BANK, WARRANTY_HOLD)`. The last three are the
double-entry counterparts (E-026) and the two DMS ones (E-063, E-064). Seeded per warehouse at
creation.

---
**E-022 · Storage categories and capacity** — **MINOR** · `warehouse-base` · **v2**

*Recommendation.* `wh_storage_categories(code, name, max_weight, max_volume, allow_mixed_items,
allow_mixed_batches)`; `wh_locations.storage_category_id`. Needed before putaway rules are useful.

---
**E-023 · Putaway rules and multi-step receipt** — **MAJOR** · `warehouse` · **v2**

*Gap.* A one-step receipt writes stock straight to a bin the receiver types in. That is acceptable
for a 400-SKU parts store and unacceptable for a 3PL or a 20,000-SKU distribution godown.

*Recommendation.* `wh_putaway_rules(warehouse_id, item_id NULL, item_category_id NULL,
from_location_id, to_location_id, sequence)` and a configurable receipt route
(`RECEIVE → INSPECT → PUTAWAY`) on `wh_warehouses.receipt_steps`. Keep the v1 one-step path as the
default so the parts store is not taxed for the 3PL's needs.

---
**E-024 · Stock ownership — the column that makes `warehouse-3pl` possible at all** — **MAJOR** · `warehouse-base` · **v1 (column) / v2 (feature)**

*Gap.* Consignment stock (OEM-owned parts on our floor, our stock in a 3PL's building, a supplier's
van stock) is not ours to value. If `owner_party_id` is not on the balance and the movement from
day one, every valuation report is wrong the moment `warehouse-3pl` ships, and retrofitting it means
rewriting every valuation query.

*Recommendation.* `wh_stock_balances.owner_party_id` and `wh_stock_movements.owner_party_id`,
nullable, null meaning "owned by the operating company". Every valuation and GL projection filters
`owner_party_id IS NULL`. Odoo proves the shape (`owner_id` on quants). The 3PL feature set
(billing, owner portals) is v2/v3; **the column is v1**.

---
**E-025 · Handling unit / licence plate** — **MINOR** · `warehouse-base` · **v2**

*Recommendation.* `wh_handling_units(id, code, warehouse_id, location_id, parent_handling_unit_id,
status)` and a nullable `handling_unit_id` on balances/movements. Required for pallet-level 3PL and
for D365-grade WMS parity; not required by a parts store.

### 2.5 Movements and documents

---
**E-026 · The movement ledger is double-sided and immutable** — **BLOCKER** · `warehouse-base` · **v1**

*Gap.* `accessory_inventory_transactions` has `from_warehouse_id`/`to_warehouse_id` both nullable
(`V30131:17-20`), so a receipt has a null "from" and the ledger does not balance in the way a
double-entry stock ledger does. Odoo's whole model is that every move has a source and a
destination, even if one is a virtual vendor/customer/inventory-loss location; that is what makes
"where did 3 units go" answerable.

*Recommendation.* `wh_stock_movements(id, company_id, movement_number, movement_date, movement_type,
item_id, batch_id, serial_number, quantity_base, entered_quantity, entered_uom_id,
from_warehouse_id NOT NULL, from_location_id NOT NULL, to_warehouse_id NOT NULL, to_location_id NOT
NULL, owner_party_id, unit_cost, value_amount, reason_code_id, source_module, source_entity,
source_entity_id, source_reference_number, reversal_of_movement_id, posted_at, created_by)`.
Virtual locations (`SUPPLIER`, `CUSTOMER`, `LOSS_GAIN`, `PRODUCTION`, `SCRAP`) make both ends
non-null. **No UPDATE and no DELETE on a posted movement** — corrections are a reversal pair.

---
**E-027 · Purchase order and goods receipt as distinct documents** — **MAJOR** · `warehouse` · **v1**

*Gap.* `accessories` has "stock receipts" with no purchase order behind them. Every comparator in
every group separates order from receipt from bill, because the quantity event and the value event
are different events with different dates.

*Recommendation.* `wh_purchase_orders` + `wh_purchase_order_lines(ordered_quantity,
received_quantity, cancelled_quantity, expected_date, unit_price, tax_classification_code)`, and
`wh_goods_receipts` + `wh_goods_receipt_lines(purchase_order_line_id NULL, received_quantity,
accepted_quantity, rejected_quantity, batch_id, rejection_reason_code_id)`. Over/under-receipt
tolerance on `wh_purchase_orders.receipt_tolerance_percent`.

---
**E-028 · Three-way match, with the value leg in `accounting`** — **MAJOR** · `warehouse` + `accounting` · **v1.1**

*Recommendation.* Warehouse owns PO↔GRN; accounting owns GRN↔bill via the existing
`acc_source_documents` control totals. Report `grn-not-billed` (the GRNI accrual) and
`billed-not-received` are joint deliverables; name them in both sets so neither ships without the
other. This is also the account that reconciles the "goods received not invoiced" balance every
auditor asks for.

---
**E-029 · Quality inspection / quarantine on receipt** — **MINOR** · `warehouse` · **v2**

*Recommendation.* Receipt line writes to a `QUARANTINE` location; `wh_inspections(goods_receipt_line_id,
inspected_by, result, accepted_quantity, rejected_quantity, reason_code_id)` releases to stock or to
a supplier return. Required for pharma/FMCG verticals and for 3PL; not for a parts store in v1.

---
**E-030 · Outbound as states, not a single "issue"** — **MAJOR** · `warehouse` · **v1.1**

*Recommendation.* `wh_stock_issues` with `status ∈ (DRAFT, ALLOCATED, PICKED, DESPATCHED,
DELIVERED, CANCELLED)` and the allocation rows in `wh_allocations` (E-042). v1 may collapse
ALLOCATED→DESPATCHED for the counter-sale path, but the states must exist in the CHECK constraint
from v1 or the ladder is unreachable later.

---
**E-031 · Pick lists, wave and batch picking** — **MINOR** · `warehouse` · **v2**

*Recommendation.* `wh_pick_lists` + `wh_pick_list_lines(location_id, item_id, batch_id,
quantity_to_pick, quantity_picked, picked_by, picked_at)`, sequenced by `wh_locations.path`. This is
where SkuVault, Increff and NetSuite WMS win; it is not what a dealership parts counter buys.

---
**E-032 · In-transit is a location, and transit variance is a first-class event** — **MAJOR** · `warehouse-base` · **v1**

*Gap.* `accessory_stock_transfers` models transit as `status = 'IN_TRANSIT'` (`V30133:16`). Stock
in that state belongs to neither warehouse's balance and is invisible to valuation; and if 10 ship
and 9 arrive, there is no row for the missing one.

*Why it matters.* Between two branches with different GSTINs, goods in transit at 31-March are
**still the company's stock** and must appear in the stock statement and the balance sheet. Tally
and Marg both handle it; an SMB tool typically does not.

*Recommendation.* Each transfer creates a `TRANSIT` location owned by the *sending* warehouse.
Despatch moves stock `from stock → to transit`; receipt moves `from transit → to stock`. A
short-receipt leaves a residue in the transit location which must be cleared by an adjustment with
a reason code (`TRANSIT_SHORTAGE`, `TRANSIT_DAMAGE`). Report `stock-in-transit-ageing` with the
residue highlighted.

### 2.6 Adjustments, counts, valuation, controls

---
**E-033 · Reason codes with a GL account and a behaviour flag** — **MAJOR** · `warehouse-base` · **v1**

*Gap.* A reason code that is only a label produces a write-off report that cannot be posted.

*Recommendation.* `wh_reason_codes(id, company_id, code, name, applies_to, gl_account_ref,
requires_approval, requires_document, affects_demand_history, is_active)` where
`applies_to ∈ (ADJUSTMENT, SCRAP, RETURN, TRANSIT_VARIANCE, COUNT_VARIANCE, REVALUATION,
CANCELLATION)`. `gl_account_ref` is a neutral reference resolved by `accounting`'s account
determination, not an FK across the module boundary. `affects_demand_history` is what stops a
write-off from inflating the reorder point.

---
**E-034 · Approval threshold on adjustments and write-offs** — **MAJOR** · `warehouse` · **v1.1**

*Recommendation.* `wh_approval_thresholds(company_id, branch_id NULL, document_type, value_from,
value_to, approver_role_id)`; adjustments above the threshold enter `PENDING_APPROVAL`. The
platform already has an approval-config pattern in `services` and `accessories` — reuse it rather
than inventing a third.

---
**E-035 · Valuation per item, with real FIFO layers and layer restoration** — **BLOCKER** · `warehouse-base` · **v1**

*Gap.* `accessory_stock_levels` has `average_cost` and `last_cost` (`V30130:23-24`) and no layers,
so FIFO is not expressible and a sales return restores stock at today's average, not at the cost it
left with. `accounting` has already specified the right shape
(`acc_cost_layers` + `acc_cost_layer_consumptions`, `DATA-MODEL.md:434-435`).

*Recommendation.* `wh_cost_layers(id, company_id, item_id, warehouse_id, batch_id, serial_number,
receipt_date, quantity_in, quantity_remaining, unit_cost, layer_value, source_movement_id,
is_exhausted)` and `wh_cost_layer_consumptions(cost_layer_id, movement_id, quantity_consumed,
unit_cost, value_consumed, restored_at, restored_by_movement_id)`. A credit note / sales return
consumes in reverse and **restores the original layer**. AVCO items maintain
`wh_stock_balances.average_cost` in the same posting transaction.

---
**E-036 · Landed cost, apportioned four ways, and retro-applicable** — **MAJOR** · `warehouse` · **v1.1**

*Gap.* An imported or freight-heavy part costed at invoice value understates COGS by 5–15%. Every
group except the weakest SMB tools ships this; Marg and Unleashed both do it well.

*Recommendation.* `wh_landed_cost_vouchers(id, company_id, voucher_number, voucher_date, status,
total_cost_amount)` + `wh_landed_cost_charges(voucher_id, charge_type, party_id, amount,
apportion_basis)` + `wh_landed_cost_targets(voucher_id, goods_receipt_line_id, apportioned_amount)`
with `apportion_basis ∈ (VALUE, QUANTITY, WEIGHT, VOLUME, MANUAL)`. When the target stock is already
issued, the difference posts to a **price-variance** account rather than to stock — say so
explicitly, or the first retro voucher will silently corrupt the layer values.

---
**E-037 · Revaluation as a movement type with zero quantity** — **MINOR** · `warehouse-base` · **v1.1**

*Recommendation.* `movement_type = REVALUATION` with `quantity_base = 0` and a non-zero
`value_amount`, so the stock ledger and the GL stay in step through a price escalation (E-068) or a
year-end NRV write-down. Needed before E-068 can work.

---
**E-038 · Physical count as a document with freeze, blind entry, variance review and a posting step** — **MAJOR** · `warehouse` · **v1**

*Gap.* A count that overwrites `quantity_on_hand` destroys the ledger. `accessories` has counts;
the design must state that the count **posts adjustments**, it does not set balances.

*Recommendation.* `wh_stock_counts(id, count_number, warehouse_id, count_type, scope_filter,
status, frozen_at, posted_at)` with `status ∈ (DRAFT, IN_PROGRESS, COUNTED, UNDER_REVIEW,
POSTED, CANCELLED)` and `wh_stock_count_lines(count_id, item_id, batch_id, location_id,
book_quantity_frozen, counted_quantity, recount_quantity, variance_quantity, variance_value,
reason_code_id, counted_by, counted_at)`. `book_quantity_frozen` is captured at freeze; the
variance posts as adjustment movements at posting time with the layer-aware cost.

---
**E-039 · Cycle counting by class with a schedule** — **MAJOR** · `warehouse` · **v1.1**

*Gap.* Nobody stops a dealership parts store for a full physical count more than once a year, so a
product with only full counts has no accuracy mechanism for 364 days.

*Recommendation.* `wh_count_classes(code, name, counts_per_year, abc_class)` on
`wh_item_locations.count_class_id`; a scheduled job generates due count documents and reports
`count-accuracy` (lines counted correct / lines counted) and `count-coverage` per class. This is a
**dated obligation with a job**, not a report.

---
**E-040 · Replenishment run that produces a document, not a list** — **MAJOR** · `warehouse` · **v1.1**

*Recommendation.* A replenishment run reads `wh_item_locations` and the open-inbound quantity and
writes `wh_replenishment_suggestions(run_id, item_id, warehouse_id, suggested_quantity,
suggested_source ∈ (PURCHASE, TRANSFER), source_warehouse_id, supplier_party_id, reason)`. The
buyer edits and converts to `wh_purchase_orders` or `wh_stock_transfers` in one action. A low-stock
grid that the buyer must retype into a PO is what every SMB tool does and what every ERP does not.

---
**E-041 · Suggest a sister-branch transfer before buying** — **MINOR** · `warehouse` · **v2**

*Recommendation.* The replenishment run checks other branches' `quantity_available` above their own
`min_quantity` and proposes `suggested_source = TRANSFER`. For a multi-branch dealership this is
where the money is: the part is already in the group.

---
**E-042 · Reservation, allocation and ATP as three different things** — **MAJOR** · `warehouse-base` · **v1 (soft) / v1.1 (hard) / v2 (ATP)**

*Gap.* `accessory_stock_levels.quantity_reserved` (`V30130:14`) is a number with no rows behind it,
so nothing can say *what* reserved it, nothing releases it when the order is cancelled, and it can
drift permanently.

*Recommendation.* `wh_allocations(id, item_id, warehouse_id, location_id NULL, batch_id NULL,
serial_number NULL, quantity, allocation_type ∈ (SOFT, HARD), status ∈ (ACTIVE, PICKED, RELEASED,
EXPIRED), source_module, source_entity, source_entity_id, expires_at, created_by)`.
`wh_stock_balances.quantity_reserved` becomes a **derived cache** rebuilt nightly with a drift
alert, exactly as `accounting` disciplines its balance caches. ATP (v2) =
`on_hand − active_allocations + inbound_before(date)`.

---
**E-043 · Reservations expire** — **MAJOR** · `warehouse` · **v1.1**

*Gap.* A held part against an abandoned estimate is invisible dead stock. Every DMS ages special
orders and releases them.

*Recommendation.* `wh_allocations.expires_at` + a `@Scheduled` job that releases expired
allocations, notifies the owner, and writes a movement-free audit row. Report
`reservations-ageing`. Again: dated obligation, therefore job + recipients + report or nothing.

---
**E-044 · Kits and assembly** — **MAJOR** · `warehouse` · **v1.1**

*Recommendation.* `wh_kits(parent_item_id, kit_type ∈ (PHANTOM, ASSEMBLED))` +
`wh_kit_components(kit_id, component_item_id, quantity, is_optional, substitute_group)`. `PHANTOM`
relieves components at issue (the service package: oil + filter + washer); `ASSEMBLED` creates a
`wh_assembly_orders` document that consumes components and produces the parent with a computed cost.
Multi-level BOM with routings is **v3 and belongs to a manufacturing module**, not here.

---
**E-045 · Negative stock policy, three-valued, per item and per warehouse** — **BLOCKER** · `warehouse-base` · **v1**

*Gap.* If the system silently allows negative stock, valuation goes negative and the GL cannot be
reconciled; if it hard-blocks everywhere, the workshop cannot issue a part the storeman has not yet
receipted and users will invent workarounds. Every comparator makes this configurable. `accessories`
learned this the hard way and bolted on a stock-enforcement setting and an insufficient-stock log
(`V30282`, `V30290`).

*Recommendation.* `wh_items.negative_stock_policy ∈ (BLOCK, WARN, ALLOW)` overridden by
`wh_warehouses.negative_stock_policy`, resolved most-specific-first. Every `WARN`/`ALLOW` breach
writes `wh_insufficient_stock_log(item_id, warehouse_id, requested_quantity, available_quantity,
source_module, source_entity_id, user_id, occurred_at)` — copy the accessories precedent, it is a
good one — and a zero-cost issue raises a costing exception rather than a zero-value COGS line.

---
**E-046 · Stock period lock and warehouse-scoped access** — **MAJOR** · `warehouse-base` · **v1**

*Gap.* Back-dated movements into a closed period silently change a filed stock statement. And a
storeman at branch A must not adjust branch B's stock.

*Recommendation.* `wh_stock_periods(company_id, period_start, period_end, status ∈ (OPEN, CLOSED,
LOCKED))` — separate from the accounting period, because stock closes days before the books do —
and a guard that refuses any movement whose `movement_date` falls in a non-`OPEN` period. Access:
reuse the platform branch-scope record guard, extended by
`wh_user_warehouses(user_id, warehouse_id, access_level)`; `warehouse_id` participates in every
management query's WHERE clause, not just the UI filter.

### 2.7 India statutory — the core-schema set (argued in §3)

---
**E-047 · HSN on the item, UQC on the movement line** — **BLOCKER** · `warehouse-base` · **v1**

*Gap.* `accessory_products` has **no HSN column** — a grep across every module's migrations finds
`hsn_code` only on `accessory_quotation_pricing_components:37`, `dealer/V20350`,
`services/V40180` and `assets/V60160`. So HSN is captured on the *pricing line of a quotation* and
nowhere on the item, which means it is retyped per document and the GSTR-1 HSN summary cannot be
produced from stock at all.

*Why it matters.* The GSTR-1 HSN summary is HSN × UQC × quantity × taxable value. It is filed
monthly. Tally, Busy, Marg, Vyapar, Zoho and GoFrugal all key it off the stock item.

*Recommendation.* `wh_items.tax_classification_code VARCHAR(20)` (country-neutral name, HSN/SAC in
India) plus `wh_items.uqc_code VARCHAR(10)` mapping our UoM to the government's unit-quantity code
list. Every issue/receipt line copies both and **freezes** them. UQC is seed data; the columns are
schema.

---
**E-048 · Warehouse belongs to a branch, and the branch carries the GSTIN** — **BLOCKER** · `warehouse-base` · **v1**

*Gap.* If `wh_warehouses` has no `branch_id`, the tax registration under which stock is held is
unknowable, and every transfer's taxability is unanswerable.

*Why it matters.* `branches.gst_number` already exists (`platform/.../V182__Add_financial_columns_to_branches.sql:7`).
Registration in India is per state; a company with branches in three states has three GSTINs and
three separate sets of books for GST. Stock must be attributable to one of them at all times.

*Recommendation.* `wh_warehouses(id, company_id, branch_id NOT NULL, code, name, warehouse_type,
address block, is_bonded, is_third_party, operator_party_id NULL, negative_stock_policy,
receipt_steps, is_active, uk(company_id, code))`. The **GSTIN is read from the branch**, never
duplicated onto the warehouse. `accessory_warehouse_branch` is a many-to-many bridge; do not copy
that — a warehouse under two GSTINs is not a thing.

---
**E-049 · Delivery challan as a numbered document on every non-sale movement** — **BLOCKER** · `warehouse` · **v1**

*Gap.* Rule 55 requires a delivery challan for goods moved otherwise than by way of supply —
branch transfer, job work, goods on approval, exhibition stock, a part sent with a mobile technician.
Every India-group product has it; almost no SMB product does.

*Recommendation.* `wh_delivery_challans(id, company_id, branch_id, challan_number, challan_date,
challan_type ∈ (BRANCH_TRANSFER, JOB_WORK, APPROVAL, EXHIBITION, REPAIR, OTHER),
from_warehouse_id, to_warehouse_id NULL, to_party_id NULL, ship_from block, ship_to block,
declared_value, status, source_document_ref)` + `_lines(item_id, batch_id, quantity, uom_code,
tax_classification_code, unit_value, taxable_value)`. Its own number series, per branch.

---
**E-050 · A transfer between two GSTINs is a taxable supply, and the schema must admit it** — **BLOCKER** · `warehouse-base` + `accounting` · **v1 (schema) / v1.1 (tax)**

*Gap.* A stock transfer between branches of the *same* legal entity but *different* GSTINs is a
deemed supply under Schedule I: a tax invoice is raised, IGST/CGST+SGST is charged, and the
receiving branch takes ITC. A transfer within one GSTIN is not a supply at all. A transfer model
that only knows `from_warehouse_id`/`to_warehouse_id` cannot tell these apart.

*Why it matters.* This is the single most common India-specific inventory question in a
multi-branch dealership, and it is unbuildable as an afterthought because it changes the transfer's
document type, its numbering, its valuation (transfer at cost vs at the open-market/90%-of-price
valuation rule) and its GL posting.

*Recommendation.* `wh_stock_transfers` carries `from_branch_id`, `to_branch_id`,
`is_taxable_supply BOOLEAN` (derived at creation from the two branches' `gst_number` prefixes and
**frozen**), `transfer_valuation_method ∈ (COST, TRANSFER_PRICE, OPEN_MARKET_VALUE)`,
`transfer_price_amount`, and `tax_document_ref`. When `is_taxable_supply`, warehouse emits an
`acc_source_document` of kind `INTER_BRANCH_SUPPLY` and the accounting side raises the invoice; when
not, it emits a stock-only movement and a delivery challan. Both branches' stock statements must
show the goods correctly at every instant (E-032).

---
**E-051 · E-way bill needs transport attributes on the movement document, in v1** — **BLOCKER** · `warehouse` · **v1 (schema) / v1.1 (adapter)**

*Gap.* Lens R7 raised exactly this against `accounting` (`I-004`): a compliance-*reference* store
cannot hold a vehicle number. The warehouse side is worse, because the movement that most often
needs an e-way bill — the branch transfer and the job-work despatch — has **no invoice at all**, so
it cannot borrow the accounting document's attributes.

*Why it matters.* A goods movement above ₹50,000 without an e-way bill is liable to detention and
penalty. This is a licence to operate, not a feature.

*Recommendation.* `wh_transport_details(document_type, document_id, dispatch_from block,
deliver_to block, transport_mode ∈ (ROAD, RAIL, AIR, SHIP), transporter_party_id,
transporter_registration_number, vehicle_number, vehicle_type, consignment_note_number,
consignment_note_date, approximate_distance_km, transport_document_ref)` attached
polymorphically to a transfer, a challan or an issue. All columns optional at the core; a
localisation validation rule makes them mandatory. The e-way adapter reads **only** this table plus
the compliance-reference store; Part-B update, validity extension and cancellation are v1.1.

---
**E-052 · Godown-wise stock statement as a shipped report, not a grid filter** — **MAJOR** · `warehouse` · **v1**

*Gap.* "Stock as per godown" is a Tally screen every Indian accountant knows by name and a bank
asks for monthly against a cash-credit limit.

*Recommendation.* Report `godown-wise-stock-statement`: godown × item group × item, opening, inward,
outward, closing, value, with a branch filter and a period filter; exportable to Excel with the
export columns a superset of the grid (platform rule). A grid with a warehouse dropdown is not this
report — the opening/inward/outward/closing shape is the whole point.

---
**E-053 · Stock as at a back date** — **BLOCKER** · `warehouse` · **v1**

*Gap.* A balance table answers "now". Section 44AB audit, the bank stock statement, and the
31-March closing stock all ask "as at a date in the past, computed after the fact, including
back-dated entries made since".

*Why it matters.* Every India-group product does this natively because Tally's entire reporting
model is date-ranged over the ledger. An SMB tool that only knows current stock is unusable at
year-end.

*Recommendation.* Every "as at" report is computed **from `wh_stock_movements` by date**, never from
`wh_stock_balances`. Add `wh_valuation_snapshots(company_id, as_at_date, item_id, warehouse_id,
batch_id, quantity, value, created_at)` as a materialised month-end snapshot for performance, with
the rule that it is a **cache** and the ledger is authoritative — same L-9 discipline `accounting`
applies to its balance caches. Index `wh_stock_movements(item_id, warehouse_id, movement_date)`.

---
**E-054 · Job-work challan with the four-year clock** — **MAJOR** · `warehouse` + `accounting` · **v1 (schema) / v2 (ITC-04)**

*Gap.* `accounting` already specifies `acc_job_work_challans` and notes the clock is measured from
the challan date, so a movement predating the table has no clock and the liability is untracked
(`DATA-MODEL.md:489`). But the *goods* move in warehouse, not in accounting.

*Why it matters.* Body shop panels sent out for painting, engines sent for reboring, batteries sent
for refurbishment — all job work. Inputs not returned within one year (three for capital goods,
commonly stated as the "four-year" concern for moulds/dies `?`) are deemed supplied and tax becomes
payable.

*Recommendation.* Warehouse owns the movement: goods leave to a `SUPPLIER`-type virtual location
owned by the job worker (`owner_party_id` unchanged — still ours), under a `JOB_WORK` delivery
challan (E-049), with `expected_return_date`. A `@Scheduled` job ages open challan lines and raises
the obligation. `accounting` consumes it for ITC-04. Do not build two challan tables — warehouse's
`wh_delivery_challans` **is** the challan, and `acc_job_work_challans` should be reduced to a view
over it or deleted.

### 2.8 Automotive parts — the differentiator (argued in §4)

---
**E-055 · Supersession chain, resolved forward at order and enquiry time** — **BLOCKER (DMS segment)** · `warehouse-base` · **v1**

*Gap.* No generic WMS in this audit models supersession properly. Every DMS does, because OEM part
numbers change constantly and a counterman who orders the superseded number gets nothing.

*Recommendation.* `wh_item_supersessions(id, company_id, from_item_id, to_item_id, effective_date,
supersession_type ∈ (REPLACES, INTERCHANGE, PARTIAL), quantity_ratio DECIMAL(18,6),
is_bidirectional, source ∈ (OEM_FILE, MANUAL), notes, uk(company_id, from_item_id, to_item_id,
effective_date))`. A resolver walks the chain to the current terminal part (with cycle detection and
a max depth), and **every** lookup path — counter enquiry, workshop request, reorder, receipt
matching, barcode scan — goes through the resolver. `quantity_ratio` matters: three old washers
become one new kit.

---
**E-056 · Supersession must carry stock and demand history forward** — **MAJOR (DMS)** · `warehouse` · **v1.1**

*Gap.* If part A supersedes to B and A's twelve months of demand stay on A, B's computed stocking
level is zero and the part goes out of stock the day it is superseded.

*Recommendation.* A supersession action offers three treatments: `KEEP_SEPARATE`,
`MERGE_DEMAND` (B's demand history includes A's, weighted by `quantity_ratio`), `MERGE_STOCK`
(a movement transfers A's on-hand to B at A's cost layers, with an audit row). Record the treatment
on `wh_item_supersessions.stock_treatment` so it is reproducible.

---
**E-057 · Interchange / alternate part suggestion** — **MAJOR (DMS)** · `warehouse` · **v1.1**

*Recommendation.* Reuse `wh_item_supersessions` with `supersession_type = INTERCHANGE` and
`is_bidirectional = true`. Counter enquiry shows "not in stock — 2 available as <interchange>" with
the availability of every equivalent across every branch. This is the single most visible
counter-productivity feature in a DMS parts screen.

---
**E-058 · Vehicle fitment / application** — **MAJOR (DMS)** · `warehouse-base` · **v1**

*Gap.* A parts counter's most common enquiry is not "part number X" — it is "front brake pads for a
2019 Swift VDI". Only the DMS group answers that.

*Recommendation.* `wh_item_applications(item_id, make_id, model_id, variant_id NULL,
year_from, year_to, engine_code NULL, position ∈ (FRONT, REAR, LEFT, RIGHT, NA), notes,
uk(item_id, model_id, variant_id, year_from, engine_code))`, FK'd to the **existing automotive
master** (company/OEM/brand/model), not to a new vocabulary. Precedent exists:
`accessory_vehicle_compatibility` + `accessory_vehicle_compatibility_models` (`V30054`) — copy its
shape and lift it to warehouse so both modules speak the same fitment.

---
**E-059 · Bulk catalogue ingest from an OEM/aftermarket file** — **MINOR** · `warehouse` · **v3**

*Recommendation.* An import pipeline over `wh_items` + `wh_item_identifiers` +
`wh_item_supersessions` + `wh_item_applications` + price, with staging + validation + a dry-run
diff, following the `accessory_stock_receipt_import_staging` pattern. ACES/PIES is the US standard;
for India each OEM ships its own layout, so the pipeline must be **format-pluggable**. `?` on
whether any Indian OEM publishes a standard interchange format.

---
**E-060 · Obsolescence return to the OEM, with an allowance window** — **MAJOR (DMS)** · `warehouse` · **v1.1**

*Gap.* No generic product has this. OEMs typically permit an annual return of a percentage of the
year's purchases, within a window, of parts meeting eligibility rules; missing the window converts
inventory into a write-off.

*Recommendation.* `wh_return_authorisations(id, company_id, branch_id, ra_number, party_id,
ra_type ∈ (OBSOLESCENCE, DEFECTIVE, EXCESS, CORE, WARRANTY, PRICE_CLAIM), window_start, window_end,
allowance_amount, claimed_amount, status ∈ (DRAFT, SUBMITTED, AUTHORISED, SHIPPED, CREDITED,
REJECTED, EXPIRED))` + `_lines(item_id, quantity, unit_cost, restocking_fee_percent,
eligible BOOLEAN, ineligibility_reason)`. A `@Scheduled` job warns before `window_end`. Report
`obsolescence-return-candidates` = no movement in N months × OEM eligibility × remaining allowance.

---
**E-061 · Order source / order type, including VOR and emergency** — **MAJOR (DMS)** · `warehouse` · **v1.1**

*Gap.* A dealership does not place "a purchase order". It places a **weekly stock order** (cheap,
discounted, plannable), a **daily order**, and a **VOR / emergency order** (premium freight, a
vehicle is off the road and a customer is waiting). The mix of these three is a managed KPI.

*Recommendation.* `wh_purchase_orders.order_source ∈ (STOCK, DAILY, VOR, EMERGENCY, SPECIAL_ORDER,
BACK_ORDER, INITIAL_STOCK)` seeded and reportable, with `is_customer_waiting`, `linked_job_ref`,
`promised_date`. Report `order-mix` (% by source, by value) and `vor-fulfilment-time`. `order_source`
also excludes emergency purchases from lead-time statistics, or the reorder maths is poisoned.

---
**E-062 · OEM parts order interface — file out, acknowledgement in** — **MAJOR (DMS)** · `warehouse-adapter-dealer` · **v1.1**

*Gap.* Indian OEM dealers upload/download order and invoice files to the OEM's dealer portal. Doing
it by hand is a day of work a week and the source of most receipt discrepancies.

*Recommendation.* `wh_oem_order_transmissions(purchase_order_id, oem_party_id, direction ∈ (OUT,
IN), file_format, transmitted_at, acknowledgement_ref, status)` and a line-level
`wh_oem_order_responses(purchase_order_line_id, allocated_quantity, back_order_quantity,
oem_eta_date, oem_price, response_code)`. Receipt then matches against the OEM invoice file and
raises `wh_receipt_discrepancies(type ∈ (SHORT, EXCESS, PRICE, DAMAGE, WRONG_PART))` feeding the
claim register (E-081). Format-pluggable per OEM; `?` on which Indian OEMs offer a machine
interface versus a portal-only workflow.

---
**E-063 · Core / exchange parts and the core bank** — **MAJOR (DMS)** · `warehouse` · **v1.1**

*Gap.* Nothing in the ERP, SMB or India groups models cores. Selling a reconditioned starter adds a
refundable core charge; the customer returns the old unit; the dirty core is stocked separately and
returned to the OEM for credit. Uncontrolled, cores are pure leakage.

*Recommendation.* `wh_items.core_item_id` links a serviceable part to its core item;
`wh_items.core_charge_amount`. The core is a real item stocked in a `CORE_BANK` location (E-021)
with its own valuation. `wh_core_transactions(sale_movement_id, core_item_id, charge_amount,
status ∈ (CHARGED, RETURNED_BY_CUSTOMER, CREDITED_TO_CUSTOMER, SENT_TO_OEM, CREDITED_BY_OEM,
WRITTEN_OFF), due_date)` with an ageing job. Report `core-bank-ageing` and `uncredited-cores`.

---
**E-064 · Warranty parts scrap-and-hold, with a retention clock** — **MAJOR (DMS)** · `warehouse` · **v1.1**

*Gap.* A part replaced under warranty must be retained, tagged with the claim, for a retention
period, in case the OEM calls it in for inspection; scrapping it early forfeits the claim. No
generic product has any concept of this.

*Recommendation.* Parts issued to a warranty job move to a `WARRANTY_HOLD` location with
`wh_warranty_holds(movement_id, claim_reference, job_reference, hold_until_date, status ∈ (HELD,
RECALLED_BY_OEM, SHIPPED_TO_OEM, RELEASED, SCRAPPED), bin_location_id, tag_number)`. A
`@Scheduled` job flags holds past `hold_until_date` for scrap approval; releasing before the date
requires a permission. Report `warranty-parts-held` by claim, by age, by bin.

---
**E-065 · Counter sale and workshop job issue — including the return of unused parts** — **BLOCKER (our verticals)** · `warehouse` + `warehouse-adapter-services` · **v1**

*Gap.* **The `services` module has no parts inventory at all.** There is no spare-parts table
anywhere under `services/backend/.../db/migration/` and no parts entity in
`services/.../entity/`. A workshop that cannot issue a part to a job card is not a workshop system,
and the workshop is the largest inventory consumer in a dealership. `accessories` has an issuance
workflow (`accessory_issuance_records` / `_items`, `V30212`) but it is bound to an accessories
**sales order**, not to a job card, and it has **no return path** — `issuance_status` is only
`ISSUED · RECEIVED · CANCELLED`.

*Why it matters.* Parts go out to a job and some come back. Every DMS handles the return-to-store
of unused parts and credits the RO. Without it, the job is over-costed, the stock is short, and the
count variance appears three months later as shrinkage.

*Recommendation.* Two flows in v1:
(a) **Counter sale** — `wh_counter_sales` (keyboard-first screen, scan or part-number entry,
customer optional, price level, immediate issue movement, cash/credit, print). Sub-10-second bill is
the bar Marg/GoFrugal/Vyapar set.
(b) **Job issue** — `wh_material_requests(source_module='services', source_entity='service_entry',
source_entity_id, status ∈ (REQUESTED, RESERVED, ISSUED, PARTIALLY_RETURNED, CLOSED, CANCELLED))` +
`_lines(item_id, requested_quantity, issued_quantity, returned_quantity, batch_id, serial_number)`,
with reservation against the job card **before** it becomes an order (matrix row 108), a
`RETURN_TO_STORE` movement type, and open-request WIP valuation (`parts issued to open jobs`) as a
report. `warehouse-adapter-services` maps the job card; the base module never imports `services`.

---
**E-066 · Best stocking level computed from demand, with phase-in/phase-out** — **MAJOR (DMS)** · `warehouse` · **v2**

*Gap.* Typed-in min/max is what SMB tools do. Every DMS computes a stocking level from N months of
demand hits, and controls entry (`phase-in`: stock after k hits in m months) and exit
(`phase-out`: destock after no hits in n months). This is the mechanism that keeps obsolescence
under control, and it is the single biggest gap between "a stock system" and "a parts system".

*Recommendation.* `wh_demand_history(item_id, warehouse_id, period_month, hits, quantity_sold,
lost_sale_hits, lost_sale_quantity, source_breakdown)` maintained by movement posting; a scheduled
recalculation writes `wh_item_locations.{reorder_point, max_quantity, abc_class, movement_class,
stocking_status, last_demand_recalc_at}` under a named, parameterised policy
(`wh_stocking_policies(code, months_of_history, hits_to_phase_in, months_to_phase_out,
days_supply_target, exclude_reason_codes)`). Adjustments and warranty issues must be excludable via
`wh_reason_codes.affects_demand_history` (E-033).

---
**E-067 · Lost sale recording** — **MAJOR (DMS)** · `warehouse` · **v1.1**

*Gap.* The demand you could not fill is invisible to every product outside the DMS group, and it is
the input that makes the stocking level converge. It is also the honest denominator of fill rate.

*Recommendation.* `wh_lost_sales(id, company_id, branch_id, warehouse_id, item_id, requested_quantity,
available_quantity, occurred_at, lost_sale_type ∈ (NO_STOCK, PRICE, DELIVERY_TIME, CUSTOMER_CANCELLED,
NOT_CATALOGUED), source_module, source_entity_id, customer_party_id, recorded_by, resolution ∈
(EMERGENCY_ORDERED, SUBSTITUTED, TRANSFERRED_IN, LOST))`. Captured **automatically** by the
insufficient-stock guard (E-045) at the counter and at the job-issue screen, plus a manual entry for
"not catalogued". Feeds `wh_demand_history.lost_sale_hits`.

---
**E-068 · OEM price file load, price escalation and price protection** — **MAJOR (DMS)** · `warehouse` · **v1.1 (load) / v2 (escalation + claim)**

*Gap.* OEMs push periodic price files: new cost, new MRP, supersessions, new parts. Loading them by
hand is untenable at 30,000 part numbers. And when the cost rises, on-hand stock must be revalued
(that is the dealership's margin); when it falls, a price-protection claim may be raised. Only the
DMS group does any of this.

*Recommendation.* `wh_price_files(id, party_id, file_reference, effective_date, status, loaded_at,
loaded_by, line_count)` + `wh_price_file_lines(price_file_id, item_code, action ∈ (NEW, PRICE_CHANGE,
SUPERSESSION, DISCONTINUE), old_cost, new_cost, old_mrp, new_mrp, superseded_by_code, applied,
error_message)` with a **dry-run diff screen** before apply. Apply writes item/price rows,
supersessions (E-055) and, in v2, a `REVALUATION` movement (E-037) for the on-hand quantity plus a
`PRICE_CLAIM` return authorisation (E-060) when the direction favours a claim.

---
**E-069 · Pricing matrix by cost band / margin** — **MINOR (DMS)** · `warehouse` · **v2**

*Recommendation.* `wh_pricing_matrices(code, price_list_id, customer_class, from_cost, to_cost,
margin_percent | markup_percent | fixed_price)`; resolution most-specific-first with the resolved
row recorded on the sale line for auditability. This is how counter margin is actually managed in a
DMS; a single price list is not enough.

---
**E-070 · Dealer trade** — **MINOR (DMS)** · `warehouse` · **v2**

*Recommendation.* A trade is a sale to, or purchase from, another dealership at a trade price, and
frequently a *loan* to be returned. Model as `wh_stock_transfers` with an external counterparty
(`to_party_id` instead of `to_branch_id`) and `transfer_intent ∈ (SALE, LOAN)` with a return
expectation and an ageing job for unreturned loans.

### 2.9 Barcode, labels, mobile

---
**E-071 · Scanning is a resolver, not an input mask** — **MAJOR** · `warehouse` · **v1**

*Recommendation.* One scan endpoint resolves a scanned string against `wh_item_identifiers`,
`wh_locations.code`, `wh_batches.batch_number`, `wh_serials.serial_number` and document numbers, and
returns the object type. Every screen that accepts a scan calls it. GS1-128 parsing (AI 01 item,
10 batch, 17 expiry, 21 serial) in v2 — but the resolver's return shape must already admit a
composite result or v2 is a rewrite.

---
**E-072 · Mobile is not optional here, and CLAUDE.md already makes it mandatory** — **BLOCKER** · `mobile/` · **v1.1**

*Gap.* Receiving, picking, counting and transferring happen on the warehouse floor, not at a desk.
Every strong comparator in every group ships a scanner app; SkuVault, Increff and NetSuite WMS are
*sold* on it. Principle #3 of CLAUDE.md makes the web↔mobile mirror mandatory anyway, so a
warehouse module without a mobile counterpart violates our own standard as well as the market's.

*Recommendation.* v1.1 mobile screens: **receive**, **putaway**, **pick/issue**, **count**,
**transfer despatch/receipt**, **stock enquiry by scan**. Precedent for the camera path exists
(`mobile/src/screens/assets/AssetQrScannerScreen.tsx`). Respect the mobile module's divergences —
object-literal APIs, `EntityListScreen` dropdown-only filters — and mirror behaviour, not code.
Note also that `mobile/src/schemas/common.schemas.ts` is a third copy of every dropdown vocabulary:
every enum in this report (movement types, statuses, reason-code scopes) must be added there or the
mobile save silently fails validation.

---
**E-073 · Label design and printing** — **MAJOR** · `warehouse` · **v1.1**

*Recommendation.* `wh_label_templates(code, name, label_type ∈ (ITEM, BIN, BATCH, SERIAL, CARTON),
width_mm, height_mm, template_body, printer_type)` and a print action on the item, bin, batch and
receipt screens. Thermal/Zebra output matters in India: R7 already found thermal printing missing on
the accounting side (`I-…`, matrix rows 57–58) — do not repeat it here.

---
**E-074 · Offline scanning** — **MINOR** · `mobile/` · **v3**

*Gap.* Indian godown connectivity is unreliable; a scanner app that stops when the signal drops
gets abandoned. But offline stock movement means conflict resolution, which is a large design.

*Recommendation.* v3, and only for **count** and **enquiry** (idempotent, conflict-tolerant), never
for issue. State the exclusion explicitly so nobody promises it in a demo.

### 2.10 Reporting, pricing, claims, 3PL

---
**E-075 · Stock ledger / movement register, drillable, as report #1** — **MAJOR** · `warehouse` · **v1**

*Recommendation.* `stock-movement-register`: filter by item, warehouse, location, batch, serial,
movement type, reason, source module, date range; columns opening → in → out → closing per item;
drill to the movement, and from the movement to the source document via the display resolver
(E-004). This is the report auditors and storemen both live in. `accessories` has a "stock movement"
report (`V30168`, `V30365`); this one must additionally carry batch, serial, reason and source.

---
**E-076 · Ageing and no-movement buckets** — **MAJOR** · `warehouse` · **v1**

*Recommendation.* `stock-ageing` with buckets 0–3 / 3–6 / 6–12 / 12–24 / 24+ months measured from
**last outward movement**, not last receipt, with value per bucket and a branch/warehouse split.
This is the raw material for obsolescence % (E-077) and the obsolescence return (E-060), and it is
the report the OEM's field manager asks for.

---
**E-077 · The four parts KPIs, as first-class computed metrics** — **MAJOR (DMS)** · `warehouse` · **v1.1**

*Gap.* Fill rate, turns, obsolescence % and days supply are how a parts manager is measured. No
generic product computes them; every DMS does. Getting them right requires the definitions to be
written down, because each has three plausible ones.

*Recommendation.* Define and freeze, in the FRD:
- **Fill rate (off-shelf / first-pick)** = filled demand hits ÷ (filled + `wh_lost_sales` hits of
  type `NO_STOCK`), by warehouse, by month. Requires E-067.
- **Inventory turns** = annualised issue value at cost ÷ average inventory value; and **true turns**
  excluding non-stocked/special-order lines.
- **Obsolescence %** = value with no outward movement in ≥12 months ÷ total inventory value.
- **Days supply** = on hand ÷ average daily demand over the policy window.
Each becomes a stored metric on a dashboard tile *and* a report row, with the definition rendered in
the metric explainer — the platform already has that pattern.

---
**E-078 · Price lists — one home, and it is probably `accounting`** — **MINOR** · boundary · **v1.1**

*Gap.* `accounting` already specifies `acc_price_lists` / `acc_price_list_lines` (`V600138`), and
`accessories` has its own branch pricing (`accessory_branch_prices`, `accessory_price_types`,
`accessory_pricing_components`). A third price list in warehouse would be the fourth pricing model
in the suite.

*Recommendation.* Warehouse **reads** price lists, it does not own them. It owns only what is
stock-specific: the OEM price file loader (E-068) and the cost-band matrix (E-069), both of which
*write into* the owning price-list tables. Say which module owns pricing in the design set's
integration document or three will.

---
**E-079 · Outbound stock events and marketplace sync** — **MINOR** · `warehouse` · **v1.1 (events) / v3 (marketplace)**

*Gap.* Our buyers are dealerships, not e-tailers, so Unicommerce/EasyEcom/Vinculum/Cin7-grade
channel sync is not a v1 loss. But a stock-change event stream is cheap now and impossible to
retrofit into a batch-oriented posting design.

*Recommendation.* `wh_outbound_events(event_type, entity_type, entity_id, payload TEXT,
status, published_at, retry_count)` — same shape as `acc_outbound_events` — emitted on every posted
movement and balance change. Marketplace adapters are v3 and belong outside `warehouse-base`.

---
**E-080 · Scheme / free-quantity purchases** — **MINOR** · `warehouse` · **v2**

*Gap.* "10+1 free" is standard in Indian parts and lubricant distribution. Marg models it natively.
Receiving 11 against an invoice for 10 either breaks the three-way match or silently books free
stock at full cost, inflating COGS.

*Recommendation.* `wh_goods_receipt_lines.free_quantity` and `scheme_reference`; the landed value
spreads across billed + free quantity so the unit cost falls. Any three-way-match tolerance must
know about it.

---
**E-081 · Supplier claim register** — **MINOR** · `warehouse` · **v2**

*Recommendation.* Unify E-062's receipt discrepancies, expiry/breakage claims and price claims into
`wh_supplier_claims(party_id, claim_type, claim_reference, claim_date, claim_amount,
settled_amount, status, source_document_ref)` with an ageing report. Marg's strength here is a
genuine differentiator in pharma/FMCG-adjacent lines; for a dealership it is the OEM claim book.

---
**E-082 · `warehouse-3pl` needs three things in the base schema, and only three** — **MAJOR** · `warehouse-base` + `warehouse-3pl` · **v1 (columns) / v2 (module)**

*Gap.* A 3PL module retrofitted onto an owner-blind ledger cannot segregate stock, cannot value it
correctly, and cannot bill.

*Recommendation.* In `warehouse-base` v1: (1) `owner_party_id` on balances and movements (E-024);
(2) `wh_warehouses.is_third_party` + `operator_party_id`; (3) `wh_locations` ownership restriction
(`allowed_owner_party_id`) so one owner's stock cannot be put away into another's bay. Everything
else — storage/handling billing (`wh_3pl_rate_cards`, `wh_3pl_billing_runs`), owner portals,
owner-scoped reporting — is v2/v3 in `warehouse-3pl`. Increff and the e-comm WMS group set the bar;
we do not need to match it to sell to a dealership.

### 2.11 Coexistence with `accessories`, and go-live

---
**E-083 · Item cross-map registry between `accessories` and `warehouse`** — **MAJOR** · `warehouse-base` · **v1**

*Gap.* Two item masters means the same physical part exists as `accessory_products.sku` and
`wh_items.code` with no link, so no consolidated report can ever be produced and the same part is
counted twice at year end. See §5.

*Recommendation.* `wh_external_item_map(id, company_id, external_module, external_entity,
external_id, external_code, wh_item_id NULL, map_status ∈ (MAPPED, UNMAPPED, AMBIGUOUS,
DELIBERATELY_SEPARATE), mapped_by, mapped_at, uk(company_id, external_module, external_id))`.
A nightly job reports unmapped and ambiguous rows. This does **not** merge the modules; it makes the
duplication visible and reportable, which is the difference between a known cost and a silent one.

---
**E-084 · A consolidated valuation view that spans both inventories** — **MAJOR** · `warehouse` · **v1.1**

*Recommendation.* A read-only report `group-inventory-valuation` that UNIONs
`accessory_stock_levels` (valued at `average_cost`) with `wh_stock_balances` (valued from
`wh_cost_layers`), tagged by `source_system`, with a **stated caveat that the two use different
valuation methods** and therefore cannot be added without that caveat. Ugly, honest, and the only
way a CFO gets one number without a merge. See §5 for what it does *not* fix.

---
**E-085 · Shared vocabularies, even across separate ledgers** — **MINOR** · both · **v1.1**

*Recommendation.* UoM codes, reason codes, warehouse identity and movement-type names should be
**seeded from one list** even though the tables stay separate, so that the union report in E-084 and
any future migration are mechanical rather than interpretive. A one-page vocabulary appendix in the
design set, plus seed migrations on both sides referencing it.

---
**E-086 · State the double-count guard explicitly** — **MAJOR** · design set · **v1**

*Gap.* If an accessory is receipted in `accessories` and also in `warehouse` — which will happen the
first time a dealer's parts store stocks a floor mat — the group stock figure is wrong and nobody
will notice.

*Recommendation.* An **ownership rule written into the FRD**: an item category is served by exactly
one inventory system, declared in `wh_external_item_map` / an equivalent registry on the accessories
side, and a scheduled reconciliation report lists any part number present in both with stock in
both. It is a detective control, not a preventive one — but a named detective control beats an
unnamed hole.

---
**E-087 · Do not let the adapter layer become a back door into `accessories` stock** — **MINOR** · `warehouse-adapter-*` · **v1**

*Recommendation.* State that no adapter may write to `accessory_stock_levels` or read it as a source
of truth. If the accessories module needs warehouse stock, it goes through the same inbound port as
everyone else. Two ledgers is a cost; two ledgers with cross-writes is a corruption.

---
**E-088 · Opening stock and go-live is a first-class feature, not an import script** — **BLOCKER** · `warehouse` · **v1**

*Gap.* Every one of these products has a documented go-live path and it is the single most common
reason an implementation fails. Opening stock needs quantity **and cost** (and batch, expiry, MRP,
serial, bin, owner), it must post as an `OPENING` movement so the ledger starts balanced, it must
reconcile to an opening GL value, and it must be re-runnable after a failed attempt.

*Recommendation.* `wh_opening_stock_batches(id, company_id, warehouse_id, as_at_date, status ∈
(DRAFT, VALIDATED, POSTED, CANCELLED), total_quantity, total_value, posted_at)` +
`_lines(item_id, batch details, serial, location_id, quantity, unit_cost, owner_party_id,
error_message)`; a staging/validation/dry-run pipeline modelled on
`accessory_stock_receipt_import_staging` (`V30293`); a posting step that writes `OPENING` movements
and seeds the first cost layer; and a **cut-over checklist screen** (masters loaded, mappings
resolved, opening posted, GL value matched, period opened).

---
**E-089 · Migration in from Tally / Busy / a legacy DMS** — **MAJOR** · `warehouse` · **v1.1**

*Gap.* No Indian buyer starts empty. They arrive with a Tally company or an OEM DMS extract
containing items, godowns, batches, opening stock and, critically, **twelve months of demand
history** — without which E-066's stocking levels take a year to become useful.

*Recommendation.* Importers for: item master (with HSN, UoM, MRP), godowns, opening stock with
batch/expiry, supersession list, and a **historical demand file** loading straight into
`wh_demand_history` with `source = MIGRATED`. Document the Tally field mapping in the design set;
`?` on whether an XML/ODBC path or a CSV export is the realistic channel for a given buyer.

---
**E-090 · The platform touchpoint list, enumerated before build** — **MINOR** · all · **v1**

*Recommendation.* Warehouse touches: menus, permissions (`warehouse:*`, `stock:*` with
`permission_dependencies` rows), `grid_column_definitions` + `filter_definitions` +
`grid_preferences.default_filters`/`default_columns` for every grid, `COMMON_FILTER_CONFIGS`
scopes in `platform/frontend/src/utils/filterUtils.ts`, `CacheConfiguration.java` cache names
(`statistics.whItem`, `statistics.whStockBalance`, …), a `WarehouseSafeTranslation.tsx` with all
locales, `mobile/src/schemas/common.schemas.ts` enums, and the `all_activity_history` view. Missing
any one of these is a known crash-or-blank-screen class in this codebase.

---

## 3. THE INDIA SECTION — what must be in the core schema, and what is seed data

The test applied: **can this be added later by inserting rows, changing a config value, or writing a
report?** If yes, it is seed/config and can wait. If it requires a column, a foreign key, a new
document type, or a change to what a movement *means*, it is schema and must be in the first
migration — because every stock row written before it exists is permanently wrong.

### 3.1 SCHEMA — cannot wait, cannot be configuration

| # | Requirement | Why it is schema, not config | Finding | Version |
|---|---|---|---|---|
| S1 | **`wh_items.tax_classification_code` (HSN/SAC)** | The GSTR-1 HSN summary is HSN × UQC × qty × value. A document line must **freeze** the classification it was filed under; a later item edit must not rewrite history. That requires the column on the item *and* on the line. Today HSN exists in this codebase only on quotation pricing components (`accessory_quotation_pricing_components:37`) — nowhere on any item | E-047 | v1 |
| S2 | **`uqc_code` on the item and the line** | The return carries the government's unit code, not our UoM name. A line with no UoM cannot be summarised. R7 raised the identical gap against `acc_invoice_lines` | E-047 | v1 |
| S3 | **`wh_warehouses.branch_id NOT NULL`** | The GSTIN under which stock is held is the branch's (`branches.gst_number`, `platform/…/V182:7`). Without this FK, no movement's tax treatment is determinable, ever | E-048 | v1 |
| S4 | **`wh_stock_transfers.{from_branch_id, to_branch_id, is_taxable_supply}`, frozen at creation** | A transfer across GSTINs is a **deemed supply** (Schedule I) that raises a tax invoice, charges tax and creates ITC at the other end; a transfer within one GSTIN is not a supply. This changes the document type, the number series, the valuation and the GL posting — none of which is a setting | E-050 | v1 |
| S5 | **`transfer_valuation_method` + `transfer_price_amount`** | Rule 28 permits cost / open-market-value / 90%-of-onward-sale valuations for a deemed supply. Which one was used must be recorded on the transfer to defend it three years later | E-050 | v1 |
| S6 | **`wh_delivery_challans` as a numbered document with its own series** | Rule 55 movements (branch transfer, job work, approval, exhibition, repair) have **no invoice** to hang attributes on. A challan is a document, not a print template | E-049 | v1 |
| S7 | **`wh_transport_details`** — dispatch-from/deliver-to blocks, transport mode, transporter party + registration, vehicle number, LR number and date, distance | An e-way bill cannot be generated from a compliance-reference store; a reference store holds a number, not a vehicle. R7's `I-004` is the same finding on the accounting side. The movement that most needs it (branch transfer) has no invoice, so it cannot borrow accounting's block | E-051 | v1 |
| S8 | **`wh_batches` as an entity with `expiry_date`, `manufactured_date`, `mrp_amount`, `batch_status`** | Batch-wise stock is how lubricants, tyres, batteries, paint, pharma and FMCG are transacted in India. As strings on a balance row (the `accessory_stock_levels` model) the same batch in two bins can hold two expiry dates and cannot be blocked or recalled | E-014, E-016 | v1 |
| S9 | **MRP as a valued dimension** | Two MRPs of one SKU coexist legitimately after a revision and must be sold and reported separately. Retrofitting MRP into the balance unique key is a rewrite of every stock query | E-016 | v1 schema |
| S10 | **`wh_stock_movements` immutable, date-stamped, and queryable as-at** | Section 44AB stock records, the bank stock statement and the 31-March closing stock are all "as at a past date, recomputed including entries made since". A balance-only model cannot answer them — and no configuration turns a balance into a history | E-053 | v1 |
| S11 | **`wh_stock_periods` distinct from accounting periods** | Back-dating a movement into a period whose stock statement has been submitted to a bank must be refused. Stock closes before books close, so it needs its own lock | E-046 | v1 |
| S12 | **In-transit as a location** | Goods in transit at 31-March are the company's stock and must appear in the statement. A `status = 'IN_TRANSIT'` flag (the `accessory_stock_transfers` model) makes them belong to no balance and to no statement | E-032 | v1 |
| S13 | **Job-work movement to an owner-preserving external location, with `expected_return_date`** | The dated obligation (goods not returned within the statutory window are deemed supplied) is measured from the challan. A movement that predates the field has no clock and the liability is silently untracked — `accounting` already records exactly this reasoning at `DATA-MODEL.md:489` | E-054 | v1 schema |
| S14 | **`owner_party_id` on balances and movements** | Consignment stock (OEM-owned, 3PL-held, supplier van stock) is not ours to value or to include in a statutory stock statement. Adding it later invalidates every valuation query already written | E-024 | v1 |
| S15 | **`wh_reason_codes.gl_account_ref`** | A stock write-off is a GST-relevant event (ITC reversal on goods written off, s.17(5)(h)). The reason must carry the posting target, or the reversal cannot be automated | E-033 | v1 |
| S16 | **Free/scheme quantity on the receipt line** | 10+1 changes the unit cost and therefore the taxable base of the onward sale. Bolting it on later corrupts the cost layers already written | E-080 | v1 column, v2 feature |

### 3.2 SEED DATA / CONFIGURATION — safe to add later

| # | Item | Why it is only seed |
|---|---|---|
| D1 | The HSN code list itself, and HSN→rate mapping | Rows in a master. The **column** (S1) is what cannot wait |
| D2 | UQC code list (`NOS`, `KGS`, `LTR`, `MTR`, …) and the UoM→UQC mapping | Rows |
| D3 | The 36 state/UT jurisdiction rows and their codes | Rows. `accounting` already needs the master (R7 `I-007`); warehouse should FK to it, not build a second one |
| D4 | Tax rates, cess rates, effective dates | Owned by `accounting` entirely; warehouse never computes tax |
| D5 | Reason-code vocabulary (`EXPIRY`, `DAMAGE`, `SHRINKAGE`, `THEFT`, `TRANSIT_SHORTAGE`, `WRITE_OFF_ITC_REVERSAL`) | Rows in `wh_reason_codes`; the **columns** on that table (S15) are schema |
| D6 | E-way bill threshold (₹50,000), distance-to-validity table, exempt-goods list | Values in a localisation pack. The **attributes** (S7) are schema |
| D7 | Document-series formats for challans and transfers | Configuration, given S6 exists |
| D8 | Near-expiry alert horizons, obsolescence buckets, count-class frequencies | Configuration |
| D9 | E-invoice / e-way portal credentials and the adapter itself | An adapter over S7; deferrable to v1.1 |
| D10 | Print layouts for the challan and the transfer note, including bilingual and thermal | Templates over S6/S7 |
| D11 | GSTR-1 HSN summary **report** | A report over S1/S2, and it lives in `accounting`, not here |
| D12 | ITC-04 **return** | A report over S13; `accounting` owns it |

### 3.3 The one-line test of the split

If v1 ships **S1–S16** and *none* of D1–D12, an Indian buyer cannot file a return from the product —
but every row of stock ever written is correct, and D1–D12 are a quarter's work. If v1 ships D1–D12
and misses even S3, S4 or S7, the product looks compliant in a demo and every branch transfer ever
recorded is wrong in a way that cannot be repaired without re-keying the history.

That asymmetry is the whole argument for putting the schema in the first migration.

---

## 4. THE AUTOMOTIVE-PARTS SECTION — what a dealership parts department needs that a WMS does not

This is where we win or lose the actual buyer. A dealership evaluating us is not comparing us to
NetSuite; it is comparing us to the parts module of CDK, Reynolds, Tekion, Karmak, Autologue or the
OEM's own DMS — and, in India, to Marg or a spreadsheet. Everything in this section is `○` or `◐`
across the entire ERP and SMB columns of §1 and `●` in the DMS column. That gap **is** the product.

### 4.1 The catalogue is not a list of parts

| Need | What a WMS gives you | What a parts department needs |
|---|---|---|
| Part identity | one code, one barcode | dealer number + OEM number + supplier code + multiple barcodes + legacy code (**E-012**) |
| Part changed number | rename the item | a **supersession chain** A→B→C, resolved forward at every lookup, with a quantity ratio, and a decision about whether stock and demand history move with it (**E-055, E-056**) |
| Equivalent part | nothing | interchange / alternate, bidirectional, shown at the counter with cross-branch availability (**E-057**) |
| "What fits this car" | nothing | make × model × variant × year × engine × position (**E-058**) |
| Part sold as a set | a kit | a service package with menu pricing, plus a **core** relationship for exchange units (**E-044, E-063**) |

The fitment table is the one a generic WMS never has and the one a counterman uses fifty times a
day. We already have the shape in `accessory_vehicle_compatibility` and the automotive master to FK
it to — lifting it to `warehouse-base` is cheap and no competitor outside the DMS group has it.

### 4.2 Stocking is computed, not typed

A WMS asks the user for a reorder point. A parts system **derives** it, because no human maintains
30,000 reorder points. The DMS mechanism, in order:

1. Every issue writes a **demand hit** (`wh_demand_history`) — hits matter more than quantity,
   because two hits of one unit is a stocking case and one hit of two units is not.
2. Every unfilled request writes a **lost sale** (**E-067**), because the demand you refused is
   still demand. This is the single most-missed input; without it the stocking level converges on
   the stock you happen to have.
3. Adjustments, warranty issues and internal consumption are **excluded** from demand
   (`wh_reason_codes.affects_demand_history`, **E-033**), or a write-off inflates the reorder point.
4. A policy (**E-066**) computes: phase-in after *k* hits in *m* months; a best stocking level from
   the demand window and a days-supply target; phase-out after *n* months with no hits;
   an ABC/movement class.
5. The replenishment run (**E-040**) turns the shortfall into a **stock order document**, split by
   order source, not into a grid the buyer retypes.

Steps 2, 3 and 4 exist in no ERP-embedded or SMB product in this audit. Step 1 exists everywhere but
is usually not separable from adjustments, which quietly ruins it.

### 4.3 Ordering has three speeds and they are not the same document

| Source | Economics | What the system must do differently |
|---|---|---|
| **Stock order** (weekly) | best discount, planned, freight-efficient | generated from the replenishment run; consolidated; often has an OEM-imposed minimum |
| **Daily order** | normal terms | ad hoc, per-line |
| **VOR / emergency** | premium freight, sometimes airfreight; margin-destroying | flagged `is_customer_waiting`, linked to the job card, tracked to a promised date, **excluded from lead-time statistics**, and reported as a % of total — because rising VOR % is the symptom that the stocking policy is wrong |

Plus **special order** (a part bought for one named customer, reserved to them, with a deposit, and
aged so it does not become permanent dead stock — **E-043**) and **back order** (the OEM owes it,
with an ETA the customer can be told, **E-061**). A single `purchase_order` with no `order_source`
cannot report any of this, and "what % of my orders were emergencies" is a question every parts
manager is asked monthly.

### 4.4 The OEM is a system, not a supplier

The order goes out as a file or a portal upload; an acknowledgement comes back with **allocated**
and **back-ordered** quantities and an ETA; the goods arrive with an invoice file; the receipt is
matched line by line; discrepancies (short, excess, price, damage, wrong part) become claims
(**E-062, E-081**). A dealership doing this by hand loses a day a week and absorbs every
discrepancy silently. `?` on which Indian OEMs expose a machine interface versus portal-only —
design the transmission table format-pluggable and do not hard-code one OEM.

### 4.5 Returns are four different products

| Return | Trigger | What it needs |
|---|---|---|
| **Obsolescence return** | annual OEM allowance window, % of purchases | eligibility rules, allowance tracking, an RA number, a restocking fee, a **deadline job** (**E-060**) |
| **Core / exchange** | every reman part sold | core charge on the sale, customer core received, dirty-core stock in a `CORE_BANK` location, return to OEM, credit reconciliation, **ageing on uncredited cores** (**E-063**) |
| **Warranty scrap-and-hold** | part replaced under warranty | move to `WARRANTY_HOLD`, tagged with the claim, held until `hold_until_date`, released or scrapped **only** after the OEM's window, with a permission on early release (**E-064**) |
| **Defective / wrong-part** | receipt discrepancy or customer return | RMA, quarantine, supplier claim (**E-029, E-081**) |

None of the four exists in any ERP-embedded, SMB or India-generic product in this audit. Cores and
scrap-and-hold in particular are pure margin leakage when uncontrolled, and a parts manager will
recognise instantly whether we have modelled them.

### 4.6 The two counters: retail and workshop

**Counter sale** must be keyboard-first and fast — scan or part number, quantity, price level,
print, next. The bar is set by Marg and GoFrugal, not by NetSuite. Trade/wholesale customers need
price levels and a matrix (**E-069**); walk-in customers need a cash ticket.

**Workshop issue** is the harder one and is **completely absent from our suite today** — the
`services` module has no parts tables at all (**E-065**). It needs:

- a **material request** against a job card, before the job is an order;
- **reservation** of stock to that job, with expiry (**E-042, E-043**);
- issue in parts, over time, as the job progresses;
- **return to store** of unused parts, crediting the job — the flow `accessory_issuance_records`
  does not have;
- **open-RO WIP valuation**: parts issued to jobs not yet invoiced are neither stock nor COGS, and
  every month-end they must be reported;
- and the warranty split, because parts on a warranty job go to `WARRANTY_HOLD`, not to the bin.

### 4.7 The four numbers a parts manager is judged on

Fill rate, turns, obsolescence %, days supply (**E-077**). Each has multiple plausible definitions;
write ours down and render it in the metric explainer, because a KPI a manager cannot reproduce by
hand is a KPI they will not trust. Fill rate is the one that is impossible without lost-sale capture
— which is why **E-067 is upstream of the entire KPI set** and belongs no later than v1.1.

### 4.8 What this means for the module split

Almost everything in §4 is *dealership-specific* but *not vertical-adapter-specific*: supersession,
fitment, cores, obsolescence returns, VOR, price files and the KPIs all belong in **`warehouse`**
(the application), not in `warehouse-base` (the engine) and not in an adapter. `warehouse-base` gets
only the neutral hooks: identifiers, item relationships, location types, ownership, reason codes,
movement source references. Put supersession resolution in the base and every 3PL install carries a
parts feature it does not want; put it in an adapter and the services vertical cannot use it.

---

## 5. THE TWO-INVENTORY PROBLEM — costed honestly

**The decision is that `accessories` inventory stays permanently separate. This section does not
argue with it.** It prices it, and proposes mitigations that do not require a merge.

### 5.1 First, correct the premise: it is three, not two

§0.2 sets this out. `accounting`'s P3 scope already specifies `acc_items`, `acc_godowns`,
`acc_batches`, `acc_stock_balances`, `acc_valuation_entries`, `acc_cost_layers`,
`acc_physical_stock_counts` and `acc_stock_journals`. If `warehouse` is built alongside without
**E-001** being settled, the suite has:

- `accessories` — quantity + `average_cost`, no layers, batch/serial as strings;
- `accounting` — quantity + value + FIFO layers, godowns, batches;
- `warehouse` — quantity + value + layers + locations + everything in §1.

Two is a priced decision. Three is an accident. §5 costs the accessories separation as accepted;
**E-001 must delete the accounting one.**

### 5.2 What the buyer actually loses

| # | Cost | Concretely, in this codebase |
|---|---|---|
| C1 | **Duplicate item master** | A floor mat exists as `accessory_products` (`sku`, `barcode`, `uom_id`, `min_stock_level`…) and as `wh_items` (`code`, identifiers, `stock_uom_id`…). Two codes, two barcodes, two UoM vocabularies (`accessory_uom` vs `wh_uoms`), two category trees. Add a part once, maintain it twice, and every price change is two edits |
| C2 | **Two stock truths for one physical shelf** | If both systems can hold the same part, the group quantity is `accessory_stock_levels.quantity_on_hand + wh_stock_balances.quantity_on_hand` and nothing prevents the same physical unit being in both (**E-086**) |
| C3 | **No consolidated valuation** | `accessory_stock_levels.average_cost` is AVCO-only with no layers; `wh_cost_layers` supports FIFO/AVCO/specific per item. The two numbers are computed by different methods, so they cannot be summed without a caveat, and the caveat is exactly what an auditor will not accept |
| C4 | **Reports cannot be unified** | Accessories ships 11 report grids (`V30166`–`V30177`: stock summary, sales summary, stock movement, top selling, slow moving, inventory valuation, category performance, warehouse utilisation, return analysis, low stock, insufficient stock) with their own `grid_column_definitions`. Warehouse will ship its own. "Ageing across the whole business" means running two reports and pasting them together |
| C5 | **Two warehouse masters for one building** | `accessory_warehouses` + `accessory_warehouse_branch` (many-to-many) vs `wh_warehouses.branch_id` (one branch, one GSTIN — **E-048**). The same physical godown is two rows with different branch semantics, so a godown-wise stock statement (**E-052**) is not producible for the site |
| C6 | **No cross-system availability at the counter** | "Not in stock here — 2 at the other branch" (**E-057**) cannot see accessories stock, and the accessories screen cannot see parts stock. The counterman checks two screens, or does not check |
| C7 | **Two GST treatments of one transfer** | A branch transfer of mixed stock (parts + accessories) is one lorry, one e-way bill, one tax invoice — and two systems, neither of which can produce the combined document (**E-050, E-051**) |
| C8 | **Double the compliance surface** | HSN, UQC, batch/expiry, MRP, delivery challan and e-way must be built **twice**, or accessories stays non-compliant. Today `accessory_products` has no HSN column at all (**E-047**) — so the second build has not started |
| C9 | **Two remediation streams forever** | Every finding in §2 that is a schema gap is a gap in accessories too. `accessory_stock_levels` has strings for batch/serial (**E-014**), no cost layers (**E-035**), reservation with no rows behind it (**E-042**), transit as a status (**E-032**). Fixing warehouse does not fix accessories |
| C10 | **Two mobile surfaces** | A storeman scanning stock has two apps' worth of screens for one job (**E-072**) |
| C11 | **Migration debt compounds** | The longer both run, the more history exists in the losing schema, so the merge — if it is ever reconsidered — gets monotonically more expensive |

### 5.3 What is *not* lost, and should not be over-claimed

Accessories inventory works, it is in production, it has branch scope, guards, import, export and
reports, and it serves a genuinely different business (retail accessory sales with quotations,
orders, deliveries, discounting and fitment). Separation buys **zero migration risk to a live
module** and **zero regression risk to a working revenue flow** — which is a real, bankable benefit
and is presumably why the decision was taken. The costs above are the price of that, not evidence
the decision was wrong.

### 5.4 Mitigations that do not require a merge

| # | Mitigation | Addresses | Finding | Version |
|---|---|---|---|---|
| M1 | **Cross-map registry** `wh_external_item_map` — every accessories product mapped, unmapped or explicitly `DELIBERATELY_SEPARATE`, with a nightly exception report | C1, C2 | E-083 | v1 |
| M2 | **Category ownership rule** in the FRD: each item category is served by exactly one system, plus a detective reconciliation report listing any part with stock in both | C2 | E-086 | v1 |
| M3 | **Union valuation report** `group-inventory-valuation`, tagged by `source_system`, with the differing-valuation-method caveat rendered on the report itself | C3, C4 | E-084 | v1.1 |
| M4 | **Shared vocabularies**: UoM codes, reason codes, movement types, warehouse codes seeded from one list on both sides | C1, C4, C5 | E-085 | v1.1 |
| M5 | **Cross-system availability lookup**: a read-only endpoint that queries both balance tables and returns availability by branch, consumed by both counters | C6 | E-057 (extend) | v1.1 |
| M6 | **One document layer for statutory movements**: `wh_delivery_challans` + `wh_transport_details` accept lines sourced from *either* system, so one transfer produces one challan and one e-way bill even when the goods come from two ledgers | C7 | E-049, E-051 | v1.1 |
| M7 | **Backport the compliance columns to accessories**: `accessory_products.hsn_code`, `uqc_code`, MRP on the batch. A small migration, and it is required whether or not warehouse exists | C8 | E-047 (mirror) | v1 |
| M8 | **No cross-writes, ever**: adapters may not write to `accessory_stock_levels`; if accessories needs warehouse stock it uses the same inbound port | C2, C9 | E-087 | v1 |
| M9 | **One reporting scope**: register warehouse report grids under the same report-type registry accessories uses (`V30257__seed_accessories_report_types…`) so a user sees one Reports menu, even if the data comes from two engines | C4 | E-085 | v1.1 |

M1, M2, M7 and M8 are the load-bearing four. Without M1 and M2, C2 (the same unit counted twice) is
not merely unmitigated — it is undetectable.

---

## 6. THE MINIMUM CREDIBLE v1 — for a multi-branch Indian dealership group

The buyer: a dealership group with 3–8 branches across one or two states, running vehicle sales,
a workshop, an accessories counter and a parts store, on Tally plus the OEM's DMS plus spreadsheets.
They are not comparing us to NetSuite. They are comparing us to *the parts module they already have*
and to *the Tally company their accountant already runs*.

### 6.1 The cut

**In v1 — the product is not credible without any one of these:**

| Block | Contents | Findings |
|---|---|---|
| Engine | `wh_items` (with `item_type`, per-item valuation, lifecycle), `wh_item_identifiers`, `wh_uoms` + conversions, `wh_item_categories`, `wh_item_locations` (per-warehouse min/max), `wh_warehouses` (branch-bound), `wh_locations` (tree, typed), `wh_batches`, `wh_serials`, `wh_stock_movements` (double-sided, immutable), `wh_stock_balances` (cache), `wh_cost_layers` + consumptions, `wh_reason_codes`, `owner_party_id` throughout | E-007..E-014, E-019..E-021, E-024, E-026, E-033, E-035 |
| Controls | negative-stock policy 3-valued, insufficient-stock log, stock periods, warehouse-scoped access, immutable-ledger rule | E-045, E-046 |
| Documents | purchase order, goods receipt, stock issue, stock transfer with **in-transit as a location** and branch/GSTIN awareness, delivery challan, adjustment, physical count with freeze→variance→post | E-027, E-032, E-038, E-049, E-050 |
| India schema | HSN + UQC, branch/GSTIN binding, taxable-transfer flag + valuation method, challan series, `wh_transport_details`, as-at-date reporting, job-work challan fields | §3.1 S1–S16 |
| Parts differentiators | supersession chain with forward resolution, vehicle fitment, **counter sale**, **workshop material request → reserve → issue → return to store** | E-055, E-058, E-065 |
| Integration | one inbound movement port shared with `accounting`, neutral source references, two adapters (services, dealer) | E-003, E-004, E-006 |
| Go-live | opening stock with cost/batch/serial/bin, staged and re-runnable, plus a cut-over checklist | E-088 |
| Reports | stock summary, **stock movement register**, valuation, ageing, godown-wise stock statement, low stock, stock as at a date | E-052, E-053, E-075, E-076 |
| Coexistence | cross-map registry, category ownership rule, no cross-writes | E-083, E-086, E-087 |
| Platform | permissions + dependencies, grids + filter definitions + `filterUtils` scopes, cache registration, SafeTranslation all locales, mobile schema enums | E-090 |

**v1.1 — within one quarter of v1, or we start losing deals we had won:**
mobile scanner app (E-072), labels (E-073), landed cost (E-036), replenishment run producing
documents (E-040), hard allocation + reservation expiry (E-042, E-043), kits (E-044), cycle counting
(E-039), lost-sale capture (E-067), fill rate/turns/obsolescence KPIs (E-077), obsolescence returns
(E-060), cores (E-063), warranty scrap-and-hold (E-064), VOR/order source (E-061), OEM order
interface (E-062), price-file load (E-068), e-way adapter (E-051), union valuation report (E-084),
Tally/DMS migration importers (E-089).

**v2:** computed best stocking level with phase-in/out (E-066), putaway + multi-step receipt
(E-023), pick lists/waves (E-031), quality inspection (E-029), ATP (E-042), price escalation and
protection claims (E-068), pricing matrices (E-069), dealer trade (E-070), schemes (E-080), supplier
claims (E-081), job work ITC-04 (E-054), `warehouse-3pl` proper (E-082), handling units (E-025),
storage categories (E-022), catch-weight hooks (E-011).

**v3:** marketplace/channel sync (E-079), EDI (E-062), offline scanning (E-074), catalogue-standard
ingest (E-059), intercompany transfers, multi-level BOM/routings (which belong to a manufacturing
module, not here).

### 6.2 What we lose at this cut, and to whom

| We lose to | On what | Is it the right loss? |
|---|---|---|
| **SkuVault · Increff · Cin7 · NetSuite WMS · D365 Advanced WMS** | wave/cluster picking, putaway optimisation, handling units, cartonisation, offline RF | **Yes.** A 400–5,000 SKU parts store does not pick in waves. Losing the e-commerce 3PL segment in v1 is a deliberate, recoverable choice |
| **Unicommerce · EasyEcom · Vinculum · Ordoro · Cin7 Omni** | marketplace and courier integration | **Yes** — not our buyer. It becomes a real loss only if a logistics vertical is added |
| **Marg · GoFrugal · Busy** | schemes/free quantity, van sales, expiry-claim automation, decades of Indian distribution muscle memory, and a price point we cannot match | **Partly.** We must not lose them on *batch, expiry, MRP, godown statement, challan and as-at-date* — those are in the v1 cut for exactly this reason. Losing on schemes and van sales in v1 is acceptable |
| **Tally Prime** | ten valuation methods, instant back-dated everything, universal accountant familiarity, and the fact that the accountant already owns it | **Unavoidable, and not the fight.** We win by being the *operational* system the workshop and parts counter live in, feeding one GL. As-at-date reporting (E-053) is the minimum needed to stop losing on Tally's home ground |
| **CDK · Reynolds · Tekion · Karmak · Autologue** | computed stocking levels, mature OEM interfaces, decades of parts KPI tuning | **The dangerous one.** The v1 cut keeps supersession, fitment, counter sale and workshop issue-and-return — enough to be recognised as a parts system. But **E-066 (computed stocking) and E-067 (lost sales) are what a parts manager will test us on**, and every quarter they slip past v1.1 costs us the segment we are best positioned to win |
| **Odoo · ERPNext** | breadth for free, a large implementer pool, and no per-user cost | **Partly.** We beat them on the Indian dealership specifics of §3 and §4, which neither has; we lose on breadth and price. Do not compete on breadth |
| **Zoho Inventory · Unleashed · Katana · inFlow · Fishbowl · Finale · Sortly** | polish, onboarding speed, price | **Yes, and it does not matter** — none of them can issue a part to a job card, none models a core or a supersession, and none produces a godown-wise stock statement |

### 6.3 The single sentence

If v1 ships the engine of §6.1 with the India schema of §3.1 and the four parts differentiators
(supersession, fitment, counter sale, workshop issue-and-return), we are credible against every
product in this audit **for our buyer** — and the two things most likely to be cut for time,
**lost-sale capture (E-067)** and **computed stocking levels (E-066)**, are precisely the two that
separate "a stock system with a parts screen" from "a parts system". Protect them in the plan even
though they sit in v1.1 and v2.

---

*End of R3. `?` marks throughout indicate items I could not verify without web access — chiefly
Marg's auto-parts edition specifics, Sage 200 bin handling, Unleashed bin locations, Vyapar
multi-godown, and every Indian OEM DMS parts interface. Treat each as unknown, not as absent.*
