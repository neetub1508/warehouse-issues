# LENS R2 — Tier-1 / enterprise WMS feature-by-feature audit

<!-- check-design-set: issue-citations file #230 #263 #275 #303 #312 #314 #325 #334 #375 #388 — `#230` `#263` `#275` `#303` `#312` `#314` `#325` `#334` `#375` `#388` are **row numbers in R2's own feature tables** — *“the single most important row in this table is #263”*, *“Gap. #230.”* — not issue references. This lens numbers its rows and refers back to them by number throughout -->

**Audited:** the *proposed* four-module Warehouse / Inventory design set for the Classic platform —
`warehouse-base` · `warehouse` · `warehouse-adapter-<vertical>` · `warehouse-3pl` — as described in the
lens brief, 2026-09-01.

**Benchmarked against:** Manhattan Associates (Manhattan Active® Warehouse Management; Manhattan SCALE) ·
Blue Yonder WMS (JDA / RedPrairie DLx lineage) · SAP EWM (embedded and decentralised, with SAP WM/LE-WM
and SAP MM-IM held up for contrast) · Oracle Warehouse Management Cloud (ex-LogFire) and Oracle Fusion
Cloud Inventory Management · Körber Supply Chain Software (K.Motion Warehouse Advantage, ex-HighJump) ·
Infor WMS (Infor Supply Chain Execution, Provia/VIAWARE lineage) · Softeon · Tecsys (Elite / Streamline).

---

## Reading instructions — what this document is and is not

**There is no design set to score yet.** `warehouse-issues` is an empty repository: no commits, no FRD,
no data model, no issues. The accounting lenses (R5 etc.) could score `COVERED / DOC-ONLY / MISSING`
against 57 task issues. This lens cannot, and pretending otherwise would be fabricated coverage.

So the right-hand column of every matrix is **not a coverage score. It is a placement verdict** — the
version in which this lens says the capability must land, given the brief's rule that *v1 is a cut line,
not the scope limit*. Every capability enumerated here is placed. None is dropped except the fifteen in
§4, each with a reason.

**Legend, product columns:** `●` mature, shipping, referenceable · `◐` partial, tiered, an extra-cost
module, or weak relative to peers · `○` absent from the WMS product itself (may exist in a sibling
product of the same vendor — noted where I know it) · `?` I am not confident; treat as unverified.

**Legend, verdict column:**

| Token | Meaning |
|---|---|
| `V1` | Built and usable in v1 |
| `V1-M` | **Model-only in v1** — the tables, columns and keys land in v1; the screens and behaviour come later. This is the most important token in the document; see §3 |
| `V1.1` `V2` `V3` | Deferred to that version, with the schema hooks that version needs already stated |
| `PLAT` | The Classic platform already supplies it (grids, filters, export, import framework, documents, notifications, audit, dashboards, RBAC, multi-branch) |
| `NO` | Deliberately not built — §4 |

**Confidence discipline.** I have no web access. Every claim below is from product knowledge. Where I
am unsure of a specific module name, packaging boundary or maturity level I have written `?` rather
than a plausible-sounding fact. I have deliberately named **no version numbers and no pricing tiers**
for any competitor, because I cannot verify them.

**One piece of real ground truth I did check** — the Classic codebase already contains a naive inventory
implementation in the `accessories` module, and it is the single most useful artefact in this audit
because it is a working example of every structural mistake §3 warns about. It is cited by file and
line throughout:

- `accessories/backend/src/main/java/ai/accessories/entity/InventoryTransaction.java:47-138` —
  `accessory_inventory_transactions`, one row per movement carrying **both** `from_warehouse_id` /
  `from_bin_id` **and** `to_warehouse_id` / `to_bin_id`, with `batch_number VARCHAR(50)` and
  `serial_number VARCHAR(100)` as free strings, and a `status` column that means *record* status
  (`ACTIVE`), not *stock* status.
- `accessories/backend/src/main/java/ai/accessories/entity/StockLevel.java:46-91` —
  `accessory_stock_levels` keyed on product × warehouse × bin × batch string × serial string, with
  `quantity_reserved` as a **scalar counter** and `average_cost` / `last_cost` as columns on the balance.
- `accessories/backend/src/main/java/ai/accessories/entity/StorageBin.java:47-83` — zone / aisle / rack /
  level as four independent `VARCHAR` columns on the bin, not a location hierarchy.
- `accessories/backend/src/main/java/ai/accessories/entity/Uom.java:64-73` — conversion factor on the
  **UoM master**, global, not per item.
- `accessories/backend/src/main/java/ai/accessories/entity/Product.java:152-158` — `is_serialized` and
  `is_batch_tracked` as booleans, and `vehicle_compatibility` as a `jsonb` column in a codebase whose
  own standards forbid JSONB (CLAUDE.md, DATABASE CONVENTIONS).

None of that is a criticism of the accessories module, which was built to sell accessories, not to run a
warehouse. It matters because **it is the shape a warehouse product will default to unless the design set
forbids it in v1**, and because four verticals will want to migrate onto `warehouse-base` later.

---

## Headline

| | Count |
|---|---|
| Tier-1 capabilities enumerated | **392** |
| Placed in **v1** (built) | 74 |
| Placed in **v1 as model-only** (`V1-M`) | 8 |
| Placed in v1.1 | 112 |
| Placed in v2 | 118 |
| Placed in v3 | 60 |
| Supplied by the platform (`PLAT`) | 7 |
| Deliberately not built (`NO`) | 13 |
| Findings raised | **98** (`T-001` … `T-097`, plus `T-020a`) |
| — **BLOCKER** | 28 |
| — **MAJOR** | 35 |
| — **MINOR** | 35 |
| Of the BLOCKERs, structural / irreversible (§3) | 22 |

### The seven findings that decide whether this is a WMS or a stock spreadsheet

1. **The stock ledger must be double-sided and append-only, and it must carry seven dimensions from the
   first migration** — `owner_id`, `stock_status`, `lot_id`, `serial_id`, `lpn_id`, `location_id`,
   `qty_base` + `qty_entered`/`uom_id`. Six of the seven are absent from the existing accessories
   precedent, and every one of them is unbackfillable in the sense that matters: you can add the column,
   but you cannot invent the historical value, so every report that spans the migration boundary lies
   forever. (**T-001, T-002, T-004, T-005, T-006, T-011, T-014** — §3.1–§3.8.)
2. **Inventory status is a master table with behaviour flags, not a CHECK constraint and not a location.**
   Every tier-1 product has this: SAP EWM stock types (unrestricted / quality inspection / blocked),
   Manhattan and Oracle inventory status codes with an allocatable flag. Quarantined stock is on hand, is
   valued, is owned, and is not allocatable — those four facts are independent and cannot be expressed by
   moving the goods to a "QC bin". (**T-004**, §3.3.)
3. **Allocation is an open-item ledger, not a `quantity_reserved` counter.** `StockLevel.java:62`
   is the counter. With a counter you cannot answer "release order 4471's reservation", cannot
   distinguish soft from hard allocation, cannot allocate to a specific lot or LPN, cannot expire a
   reservation, and cannot reconcile. This is the exact structural analogue of the bill-by-bill finding
   in the accounting audit, and it has the same consequence: a balance that is right in total and useless
   in detail. (**T-014**, §3.7.)
4. **`owner_id` on the ledger in v1, in every install, even single-owner.** It costs one nullable-then-
   NOT-NULL column and one seeded default-owner row now. It costs a re-key of the on-hand table, every
   allocation, every valuation layer and every report later. The `warehouse-3pl` module in the brief is
   *entirely* a consequence of this column; if it is not in `warehouse-base` v1, `warehouse-3pl` is not a
   module, it is a rewrite. (**T-002**, §3.8.)
5. **A task/document separation, with `wb_tasks` present in v1 even when v1 has no RF gun.** Every tier-1
   WMS separates the business document (receipt, order) from the execution instruction (SAP EWM warehouse
   task / warehouse order; Manhattan and Blue Yonder tasks; Oracle WMS Cloud tasks from wave templates).
   If v1's receiving screen writes the ledger directly, then RF, task assignment, interleaving, labour
   measurement and automation are all a rebuild of inbound and outbound rather than a new consumer of an
   existing table. (**T-041**, §3.10.)
6. **Valuation must be layer-based and must be a policy, not a column.** `StockLevel.average_cost` is a
   column; that design cannot produce FIFO, cannot produce specific identification, cannot revalue, cannot
   restate, and cannot reconcile to a GL. `wb_cost_layers` + a valuation ledger, with the **valuation
   grain** (owner × item × site? × company?) decided in v1 because changing it restates history. Note the
   tier-1 split here: **SAP EWM holds no value at all** — quantities live in EWM, value lives in S/4
   MM/FI and the Material Ledger. We must decide explicitly whether `warehouse` owns value or the
   accounting product does. Deciding late is the expensive path. (**T-060, T-061, T-062**, §3.9.)
7. **There is no allocated migration range and no module registration for four new modules.** CLAUDE.md's
   MODULES table stops at `V800000-V809999` (Product Lift) and contains no warehouse rows; the memory
   note *"New module = 8+ touchpoints, gate is BUILD-time"* says this is not a formality. Four modules
   need four ranges, four SafeTranslation files, four Docker frontend merges and four sets of menu and
   permission seeds, decided before the first migration is written. (**T-095**, MINOR only because it is
   cheap — but it is cheap *now* and a renumbering exercise later.)

---

# §1 — THE CAPABILITY MATRIX

392 capabilities across 21 areas. Product columns `● ◐ ○ ?`. Verdict column `V1 · V1-M · V1.1 · V2 · V3 · PLAT · NO`.

## 1.1 Item / SKU master

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | Item master, own entity in the WMS | ● | ● | ◐ mirrored from S/4 material master | ● | ● | ● | **V1** `wb_items` |
| 2 | Item mastered in ERP, distributed to WMS | ● | ● | ● core design (CIF/DRF) | ● interfaced | ● | ● | **V1** — `warehouse-base` owns it; adapters sync |
| 3 | Item type vocabulary (stocked / non-stock / service / kit / phantom / packaging) | ● | ● | ● | ● | ● | ● | **V1** `wb_items.item_type` |
| 4 | Item status lifecycle (active / phase-out / obsolete / blocked-for-receipt / blocked-for-issue) | ● | ● | ● | ● | ● | ● | **V1** — four independent flags, not one enum (T-020) |
| 5 | Owner/client-specific item record (3PL) | ● | ● | ◐ party-entitled-to-dispose | ● item is per-company | ● | ● | **V1-M** `wb_items.owner_id` nullable → default owner |
| 6 | Item category / hierarchy / group | ● | ● | ● | ● | ● | ● | **V1** |
| 7 | Base stocking UoM, immutable after first movement | ● | ● | ● | ● | ● | ● | **V1** — immutability enforced by trigger (T-011) |
| 8 | Distinct buy / stock / sell / pack UoM | ● | ● | ● | ● | ● | ● | **V1** |
| 9 | Item-specific UoM conversion (case = 12 for A, 6 for B) | ● | ● | ● | ● | ● | ● | **V1** `wb_item_uom_conversions` (T-011) |
| 10 | Packaging hierarchy each→inner→case→pallet with dims/weight per level | ● | ● | ● packaging specification | ● | ● | ● | **V1.1** — table in V1, UI in V1.1 |
| 11 | Catch weight (nominal vs actual weight per unit) | ● | ◐ ? | ● | ◐ ? | ● ? food vertical | ● ? food vertical | **V1-M** second qty column on ledger (T-012) |
| 12 | Variants (size/colour/style matrix) | ◐ retail style-colour-size | ◐ | ○ ERP-side | ◐ ? | ◐ ? | ◐ ? | **V2** — v1 = separate SKUs |
| 13 | Alternate / substitute item | ◐ | ◐ | ○ ERP-side | ◐ ? | ◐ ? | ◐ | **V1.1** `wb_item_substitutes` |
| 14 | **Supersession chain (A→B→C), automotive spares** | ○ | ○ | ○ | ○ | ○ | ○ | **V1.1** — nobody in tier 1 has it; it is our vertical's table stakes (T-021) |
| 15 | Kit / BOM / assembly item definition | ◐ | ◐ | ◐ VAS + ERP BoM | ◐ | ● | ◐ | **V1.1** `wb_kits`, `wb_kit_components` |
| 16 | Serial control **mode** (none / at-receipt / at-ship / full-track / at-issue-only) | ● | ● | ● (several serial profiles) | ● | ● | ● | **V1** enum, not a boolean (T-006) |
| 17 | Lot / batch control flag | ● | ● | ● | ● | ● | ● | **V1** |
| 18 | Shelf life: total, min remaining on receipt, min remaining on ship | ● | ● | ● (SLED / BBD, min remaining shelf life) | ● | ● | ● | **V1-M** columns V1, enforcement V1.1 (T-030) |
| 19 | FEFO allocation | ● | ● | ● | ● | ● | ● | **V1.1** |
| 20 | Hazmat / DG class (UN number, class, packing group, segregation code) | ● | ● | ● (EH&S integration) | ◐ | ◐ ? | ◐ ? | **V2** columns V1-M |
| 21 | Temperature class / controlled storage requirement | ● | ● | ● | ● | ● | ● | **V2** |
| 22 | Item dimensions & weight | ● | ● | ● | ● | ● | ● | **V1** |
| 23 | ABC classification by value, recomputed on a schedule | ● | ● | ● | ● | ● | ● | **V1.1** |
| 24 | XYZ / demand-variability classification | ◐ | ● (planning heritage) | ◐ | ◐ | ◐ ? | ◐ ? | **V2** |
| 25 | Velocity / movement class driving slotting and count frequency | ● | ● | ● | ● | ● | ● | **V1.1** `wb_items.velocity_class` + nightly job |
| 26 | Cycle-count class → count frequency | ● | ● | ● | ● | ● | ● | **V1.1** |
| 27 | Country of origin | ● | ● | ● | ● | ● | ● | **V2** |
| 28 | HS / customs tariff code | ◐ | ◐ | ● (ERP) | ◐ | ◐ | ◐ | **V2** |
| 29 | Multiple barcodes / GTIN per item, with UoM per barcode | ● | ● | ● | ● | ● | ● | **V1** `wb_item_barcodes(item_id, barcode, uom_id)` (T-022) |
| 30 | GS1 application-identifier parsing on scan (01/10/17/21/00) | ● | ● | ● | ● | ● | ● | **V1.1** |
| 31 | Item image / attachment | ◐ | ◐ | ◐ | ◐ | ◐ | ◐ | **PLAT** document storage |
| 32 | Item↔location assignment (fixed pick face) with per-location min/max | ● | ● | ● | ● | ● | ● | **V1.1** `wb_item_locations` |
| 33 | Supplier part number cross-reference | ● | ● | ● | ● | ● | ● | **V1.1** |
| 34 | Customer part number cross-reference | ● | ● | ◐ | ● | ● | ● | **V2** |
| 35 | Handling constraints: stackability, orientation, crush limit, max stack height | ● | ● | ● | ◐ | ◐ ? | ◐ ? | **V2** |
| 36 | Vehicle fitment / application master (automotive) | ○ | ○ | ○ | ○ | ○ | ○ | **V1.1** in `warehouse-adapter-dealer`, **not** in base (T-023) |
| 37 | Item revision / engineering change level | ◐ | ◐ | ● ERP | ◐ | ◐ | ◐ | **V3** |
| 38 | Item-level cycle-count / adjustment tolerance override | ● | ● | ● | ● | ● ? | ● ? | **V1.1** |

## 1.2 Units of measure, packaging and quantity semantics

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 39 | UoM master with dimension class (count / weight / volume / length) | ● | ● | ● | ● | ● | ● | **V1** |
| 40 | Conversion factor **per item**, not global on the UoM | ● | ● | ● | ● | ● | ● | **V1** — the accessories precedent gets this wrong (`Uom.java:64-73`) (T-011) |
| 41 | Transact in any UoM, persist in base UoM | ● | ● | ● | ● | ● | ● | **V1** `qty_entered` + `uom_id` + `qty_base` on **every** ledger row |
| 42 | Non-integer conversions with explicit rounding & remainder policy | ● | ● | ● | ● | ● ? | ● ? | **V1.1** |
| 43 | Distinct receiving / storage / picking / shipping UoM per item-location | ● | ● | ● | ● | ● | ● | **V1.1** |
| 44 | Break-case / repack transaction converting case → each in stock | ● | ● | ● | ● | ● | ● | **V1.1** — must be a two-sided ledger event, not an UPDATE |
| 45 | **Catch weight**: a second, independent quantity carried on every record | ● | ◐ ? | ● | ◐ ? | ● ? | ● ? | **V1-M** `qty_catch` + `catch_uom_id` nullable on ledger & on-hand (T-012) |
| 46 | Nominal vs actual weight variance reporting | ● | ◐ ? | ● | ◐ ? | ● ? | ● ? | **V2** |
| 47 | Weight & volume derived from packaging level for load planning | ● | ● | ● | ● | ● | ● | **V2** |
| 48 | Dual-UoM reporting (show stock in cases and kg simultaneously) | ● | ● | ● | ● | ● | ● | **V1.1** |
| 49 | UoM change on an item after movements exist — blocked | ● | ● | ● | ● | ● | ● | **V1** DB trigger (T-011) |
| 50 | Conversion at *allocation* time (order in eaches, pick in cases) | ● | ● | ● | ● | ● | ● | **V1.1** |

## 1.3 Lot, serial, licence plate / handling unit, traceability

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 51 | **Lot as a first-class entity**, not a string on the movement | ● | ● | ● (batch master, ERP-side) | ● | ● | ● | **V1** `wb_lots` (T-005) |
| 52 | Lot attributes: mfg date, expiry/SLED, supplier lot, receipt date, COA ref | ● | ● | ● (batch characteristics) | ● | ● | ● | **V1** |
| 53 | Lot **status** independent of item and location (hold a whole lot everywhere) | ● | ● | ● | ● | ● | ● | **V1.1** — column V1 |
| 54 | Lot-level QC result / certificate document | ◐ | ◐ | ● QIE | ◐ | ◐ | ◐ | **V2** (`PLAT` doc storage) |
| 55 | **Serial as a first-class entity** with current location, status, owner, LPN | ● | ● | ● | ● | ● | ● | **V1** `wb_serials` (T-006) |
| 56 | Configurable serial capture point (receipt / putaway / pick / pack / ship) | ● | ● | ● | ● | ● | ● | **V1.1** |
| 57 | Serial genealogy through kit / assembly / repack | ◐ | ◐ | ◐ | ◐ | ◐ ? | ◐ ? | **V2** `wb_serial_genealogy` |
| 58 | **LPN / handling unit as a first-class object** | ● | ● | ● (HU) | ● *the* core object | ● | ● | **V1-M** `wb_lpns` + `lpn_id` on ledger (T-007) |
| 59 | Nested LPN (pallet → cartons → items) | ● | ● | ● | ● | ● | ● | **V2** — `parent_lpn_id` present V1 |
| 60 | Mixed-item / mixed-lot LPN with rules | ● | ● | ● | ● | ● | ● | **V2** |
| 61 | Move / pick / ship by LPN scan (one scan moves N items) | ● | ● | ● | ● | ● | ● | **V1.1** |
| 62 | SSCC generation to GS1 | ● | ● | ● | ● | ● | ● | **V2** |
| 63 | LPN history and audit | ● | ● | ● | ● | ● | ● | **V1.1** — free if the ledger carries `lpn_id` |
| 64 | Forward trace: lot → every shipment and customer that received it | ● | ● | ● | ● | ● | ● (Tecsys/food strength) | **V1.1** — a query over the ledger, *if* §3 is respected |
| 65 | Backward trace: shipment/serial → supplier lot and receipt | ● | ● | ● | ● | ● | ● | **V1.1** |
| 66 | Mass hold / recall by lot, supplier, date range, with task generation | ● | ● | ● | ● | ● | ● | **V2** |
| 67 | Serial validation against supplier ASN | ● | ● | ● | ● | ● | ● | **V2** |
| 68 | Pallet build / de-consolidation transactions | ● | ● | ● | ● | ● | ● | **V2** |
| 69 | Consumption of a serial recorded against a customer asset / vehicle | ○ | ○ | ○ | ○ | ○ | ○ | **V1.1** in adapters (warranty, our verticals) |

## 1.4 Facility and location model

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 70 | Multiple sites / warehouses in one instance | ● | ● | ● warehouse number | ● | ● | ● | **V1** `wb_sites` |
| 71 | Site → building → zone → aisle → rack → level → position hierarchy | ● | ● | ● storage type / section / bin | ● | ● | ● | **V1** `wb_locations` self-referencing + `location_level` (T-008) |
| 72 | Location **type** vocabulary driving behaviour | ● | ● | ● storage type | ● | ● | ● | **V1** `wb_location_types` master with flags |
| 73 | Capacity constraints: weight, volume, height, LPN count, unit count | ● | ● | ● | ● | ● | ● | **V1.1** — columns V1 |
| 74 | Mixed-SKU allowed / mixed-lot allowed per location | ● | ● | ● | ● | ● | ● | **V1.1** — columns V1 |
| 75 | Location status (available / blocked / counting / damaged / frozen) | ● | ● | ● | ● | ● | ● | **V1** |
| 76 | **Virtual locations** (in-transit, adjustment offset, customer, supplier, production, scrap) | ● | ● | ● | ● | ● | ● | **V1** — non-negotiable, closes the double-entry (T-009) |
| 77 | Dock doors and staging lanes modelled as locations | ● | ● | ● | ● | ● | ● | **V1.1** |
| 78 | Yard positions / trailer as a location | ● | ● | ● YM | ◐ | ◐ ? | ● | **V2** |
| 79 | Location barcode + check digit verification | ● | ● | ● | ● | ● | ● | **V1.1** |
| 80 | Pick-path / traversal sequence per location | ● | ● | ● | ● | ● | ● | **V1.1** `wb_locations.pick_sequence` |
| 81 | Zone → work-area → resource-type assignment | ● | ● | ● activity area | ● | ● | ● | **V2** |
| 82 | Temperature zone attribute | ● | ● | ● | ● | ● | ● | **V2** |
| 83 | Hazmat segregation rules between locations | ● | ◐ | ● | ◐ | ◐ ? | ◐ ? | **V3** |
| 84 | Capacity check enforced at putaway (hard block vs warn) | ● | ● | ● | ● | ● | ● | **V2** |
| 85 | 3D coordinates / mezzanine levels | ● | ● | ● | ● | ● | ● 3D visualisation | **V3** |
| 86 | Mass location creation (aisle × rack × level generator) | ● | ● | ● | ● | ● | ● | **V1** — a generator screen, not 4,000 manual rows (T-024) |
| 87 | Location utilisation / occupancy reporting | ● | ● | ● | ● | ● | ● | **V2** |
| 88 | Location import via CSV | ● | ● | ● | ● | ● | ● | **PLAT** import framework |
| 89 | Multi-timezone: each site posts in its own local day | ● | ● | ● | ● | ● | ● | **V1** — `occurred_at` UTC + `site_timezone` (T-018) |

## 1.5 Inbound

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 90 | Purchase order / inbound delivery interfaced from ERP | ● | ● | ● inbound delivery | ● | ● | ● | **V1** — via the generic inbound movement port |
| 91 | **ASN** (advance shipping notice) as a document | ● | ● | ● | ● | ● | ● | **V1.1** `wb_asn`, `wb_asn_lines` |
| 92 | EDI 856 inbound ASN | ● | ● | ● | ● | ● | ● | **V2** |
| 93 | ASN carrying LPN/SSCC detail → receive a pallet with one scan | ● | ● | ● | ● | ● | ● | **V2** |
| 94 | Appointment / dock scheduling | ● | ● | ◐ (with TM / dock appointment scheduling) | ◐ ? | ● ? | ● | **V2** |
| 95 | Carrier self-service appointment portal | ◐ | ◐ | ○ | ○ ? | ◐ ? | ◐ ? | **V3** |
| 96 | Gatehouse / gate check-in | ● | ● | ● YM | ◐ | ◐ ? | ● | **V3** |
| 97 | Receipt **against ASN** | ● | ● | ● | ● | ● | ● | **V1.1** |
| 98 | Receipt **against PO** | ● | ● | ● | ● | ● | ● | **V1** |
| 99 | **Blind receipt** (no expectation document) | ● | ● | ● | ● | ● | ● | **V1** — the 3PL and returns default |
| 100 | Over-receipt tolerance, per item/supplier, block vs warn | ● | ● | ● | ● | ● | ● | **V1.1** |
| 101 | Short receipt / close a PO line short with reason | ● | ● | ● | ● | ● | ● | **V1.1** |
| 102 | Damaged receipt → distinct stock status, not a separate bin | ● | ● | ● | ● | ● | ● | **V1** — depends entirely on the status model (T-004) |
| 103 | Rule-driven receipt status (this supplier/item always lands in QC hold) | ● | ● | ● | ● | ● | ● | **V1.1** |
| 104 | QC inspection with sampling plan, accept / reject / partial | ◐ | ◐ | ● QIE | ◐ | ◐ ? | ◐ ? | **V2** |
| 105 | Quarantine & disposition workflow (release / reject / return / scrap) | ● | ● | ● | ● | ● | ● | **V1.1** |
| 106 | **Opportunistic cross-dock** (received item matches an open demand) | ● | ● | ● | ● | ● | ● | **V2** |
| 107 | **Planned cross-dock / flow-through** (ASN pre-allocated before arrival) | ● | ● | ● | ● | ● ? | ● | **V3** |
| 108 | Directed putaway by rule (item class, LPN, lot, capacity, zone, velocity) | ● | ● | ● putaway strategies | ● | ● | ● | **V1.1** `wb_putaway_rules` |
| 109 | Fixed pick-face putaway vs random reserve putaway | ● | ● | ● | ● | ● | ● | **V1.1** |
| 110 | Putaway override with reason code, captured | ● | ● | ● | ● | ● | ● | **V1.1** |
| 111 | Multi-step putaway (dock → staging → final) via storage control | ● | ● | ● process/layout-oriented storage control | ● | ● | ● | **V2** |
| 112 | Returns receiving (RMA) as an inbound flow | ● | ● | ● | ● | ● | ● | **V1.1** |
| 113 | Supplier compliance scorecard (ASN accuracy, on-time, labelling) | ● | ● | ◐ | ◐ ? | ◐ ? | ● | **V3** |
| 114 | Supplier chargeback / non-compliance fee | ◐ | ◐ | ○ | ○ ? | ◐ ? | ◐ ? | **V3** |
| 115 | Receiving label / LPN label print at the dock | ● | ● | ● | ● | ● | ● | **V1.1** |
| 116 | Receipt reversal ("un-receive") by reversing ledger rows, never delete | ● | ● | ● | ● | ● | ● | **V1** (T-017) |
| 117 | Consignment receipt — on hand, not owned, not valued | ● | ● | ● | ● | ● ? | ● | **V2** — enabled by `owner_id` in V1 |
| 118 | Inbound container / multi-PO shipment object | ● | ● | ● | ● | ● | ● | **V2** |
| 119 | Landed-cost components captured at receipt | ◐ (ERP) | ◐ | ○ (ERP MM) | ◐ (Fusion Costing ●) | ◐ ? | ◐ ? | **V2** — hooks in V1 cost layer |
| 120 | Dock-to-stock cycle-time measurement | ● | ● | ● | ● | ● | ● | **V1.1** — free if `occurred_at` is per-step |

## 1.6 Inventory control and the stock ledger

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 121 | On hand keyed by item × location × lot × serial × LPN × status × owner | ● | ● | ● | ● | ● | ● | **V1** — the full key, day one (T-003) |
| 122 | **Append-only, immutable stock ledger** | ● | ● | ● | ● | ● | ● | **V1** (T-001) |
| 123 | **Double-sided movement**: every transfer writes a negative and a positive row | ● | ● | ● | ● | ● | ● | **V1** — accessories writes one row with from+to (T-001) |
| 124 | Reconstruct on-hand at any past instant purely from the ledger | ● | ● | ● | ● | ● | ● | **V1** — declare it as a testable invariant (T-019) |
| 125 | Inventory **status master** with `is_allocatable` / `is_on_hand` / `is_valued` flags | ● | ● | ● stock types + availability groups | ● | ● | ● | **V1** (T-004) |
| 126 | Status change transaction with reason code (unrestricted → blocked) | ● | ● | ● posting change | ● | ● | ● | **V1** |
| 127 | Hold / release by lot, LPN, location, supplier, item, date range | ● | ● | ● | ● | ● | ● | **V1.1** |
| 128 | Adjustment with **mandatory reason code**, reason → GL account mapping | ● | ● | ● movement types | ● | ● | ● | **V1** `wb_reason_codes` (T-010) |
| 129 | Adjustment approval threshold by value / qty | ● | ● | ● | ● | ● ? | ● ? | **V1.1** |
| 130 | Bin-to-bin move within a site | ● | ● | ● | ● | ● | ● | **V1** |
| 131 | **Inter-site transfer with in-transit ownership** (3 legs: ship, transit, receive) | ● | ● | ● | ● | ● | ● | **V1.1** — virtual in-transit location in V1 (T-016) |
| 132 | Transfer order document with expected vs received, and shrinkage in transit | ● | ● | ● | ● | ● | ● | **V1.1** |
| 133 | Negative-stock policy: block / warn / allow, per site and item | ● | ● | ● | ● | ● | ● | **V1** — default **block**; the setting must exist (T-025) |
| 134 | Soft vs hard reservation, as records not counters | ● | ● | ● | ● | ● | ● | **V1** `wb_allocations` (T-014) |
| 135 | Reservation against a specific lot / serial / LPN / owner | ● | ● | ● | ● | ● | ● | **V1.1** |
| 136 | Reservation expiry and automatic release | ● | ● | ● | ● | ● ? | ● ? | **V1.1** |
| 137 | Expiry management: block expired stock from allocation | ● | ● | ● | ● | ● | ● | **V1.1** |
| 138 | Min remaining shelf life at allocation, per customer | ● | ● | ● | ● | ● | ● | **V2** |
| 139 | Aged stock / days-on-hand by lot and receipt date | ● | ● | ● | ● | ● | ● | **V1.1** |
| 140 | Slow-moving & obsolete identification | ● | ● | ● | ● | ● | ● | **V2** |
| 141 | Consignment / VMI stock held but not owned | ● | ● | ● | ● | ● ? | ● | **V2** |
| 142 | **Ownership-transfer event** (consignment → owned on consumption) | ● | ● | ● | ● | ● ? | ● | **V2** — a ledger row with `owner_id` change, free if T-002 lands |
| 143 | Kit assembly / disassembly as a balanced ledger transaction | ● | ● | ● | ● | ● | ● | **V1.1** |
| 144 | Repack / UoM conversion transaction | ● | ● | ● | ● | ● | ● | **V1.1** |
| 145 | Scrap / write-off with reason and approval | ● | ● | ● | ● | ● | ● | **V1** |
| 146 | Inventory freeze (site, zone, location) for counting | ● | ● | ● | ● | ● | ● | **V1.1** |
| 147 | UoM conversion applied and recorded at every transaction | ● | ● | ● | ● | ● | ● | **V1** |
| 148 | Stock **period** with soft/hard close for valuation stability | ◐ (ERP-side) | ◐ | ● (ERP MM periods) | ● (Fusion) | ◐ ? | ◐ ? | **V1-M** `wb_stock_periods` (T-064) |
| 149 | Backdated / effective-dated posting with a stated policy | ◐ | ◐ | ● posting date ≠ entry date | ● | ◐ ? | ◐ ? | **V1** — `occurred_at` vs `posted_at` (T-018) |
| 150 | Correction by reversal only; no UPDATE, no DELETE on the ledger | ● | ● | ● | ● | ● | ● | **V1** DB trigger (T-017) |
| 151 | On-hand snapshot table for performance, provably rebuildable from the ledger | ● | ● | ● | ● | ● | ● | **V1** + a nightly reconciliation job that alarms on drift (T-019) |
| 152 | Multi-site / network on-hand visibility in one query | ● | ● | ● | ● | ● | ● | **V1.1** |
| 153 | Stock by owner (whose goods are these) | ● | ● | ◐ | ● | ● | ● | **V2** UI; **V1-M** data |

## 1.7 Counting

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 154 | Cycle count driven by ABC class and frequency | ● | ● | ● | ● | ● | ● | **V1.1** |
| 155 | Cycle count by zone / location range / aisle sweep | ● | ● | ● | ● | ● | ● | **V1** |
| 156 | Count by item across locations | ● | ● | ● | ● | ● | ● | **V1** |
| 157 | Blind count (no expected quantity shown) | ● | ● | ● | ● | ● | ● | **V1** — a flag on the count header, cheap now (T-089) |
| 158 | Count-back / mandatory second count on variance | ● | ● | ● | ● | ● | ● | **V1.1** |
| 159 | Variance tolerance by qty % **and** by value | ● | ● | ● | ● | ● | ● | **V1.1** |
| 160 | Variance approval workflow before the adjustment posts | ● | ● | ● | ● | ● | ● | **V1.1** — the count must not post until approved (T-090) |
| 161 | Recount assignment to a different counter | ● | ● | ● | ● | ● ? | ● ? | **V1.1** |
| 162 | Physical inventory / wall-to-wall with a freeze and a snapshot | ● | ● | ● | ● | ● | ● | **V1.1** |
| 163 | Count tag generation & reconciliation (find the missing tag) | ● | ● | ● | ● | ● | ● | **V2** |
| 164 | Dynamic cycle counting while operations continue in the same zone | ● | ● | ● | ● | ● | ● | **V2** |
| 165 | **Zero-stock check / empty-bin verification** on last pick | ● | ● | ● explicit zero stock check | ● | ● | ● | **V1.1** — the highest-yield count type per hour, and nearly free |
| 166 | Low-stock check triggered by a pick below threshold | ◐ | ◐ | ● | ◐ | ◐ ? | ◐ ? | **V2** |
| 167 | Count accuracy KPI by counter, zone, item class | ● | ● | ● | ● | ● | ● | **V2** |
| 168 | Count adjustment posts to GL with the count's reason code | ● | ● | ● | ● | ● | ● | **V1.1** |
| 169 | Statistical / process-based sampling in place of full counts | ◐ | ◐ | ● | ◐ ? | ◐ ? | ◐ ? | **V3** |

## 1.8 Outbound orders, allocation and wave planning

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 170 | Outbound order interfaced from ERP / OMS | ● | ● | ● outbound delivery order | ● | ● | ● | **V1** via the outbound port |
| 171 | Multiple demand types on one model (sales, transfer, work order, replen, VAS) | ● | ● | ● | ● | ● | ● | **V1** — one `wb_demand` model, not four tables (T-042) |
| 172 | Order pool with a status model and a supervisor console | ● | ● | ● | ● | ● | ● | **V1.1** |
| 173 | Order priority, service level, ship-by / must-arrive-by date | ● | ● | ● | ● | ● | ● | **V1** |
| 174 | Allocation strategy FIFO / FEFO / LIFO configurable per item or client | ● | ● | ● stock removal strategies | ● | ● | ● | **V1.1** — V1 ships FIFO only, but the strategy is a **column not an if-statement** (T-043) |
| 175 | Allocate to a specific lot / serial / owner on demand | ● | ● | ● | ● | ● | ● | **V1.1** |
| 176 | Location-priority allocation (pick face before reserve) | ● | ● | ● | ● | ● | ● | **V1.1** |
| 177 | Partial allocation and backorder with a stated policy | ● | ● | ● | ● | ● | ● | **V1** |
| 178 | Allocation rules per customer / order type / channel | ● | ● | ● | ● | ● | ● | **V2** |
| 179 | Soft allocation on order receipt, hard allocation at release | ● | ● | ● | ● | ● | ● | **V1.1** |
| 180 | **Wave planning** by cut-off, carrier, route, order type, zone | ● | ● | ● | ● | ● | ● | **V1.1** `wb_waves` |
| 181 | Wave templates, scheduled auto-release | ● | ● | ● | ● | ● | ● | **V2** |
| 182 | Wave simulation / preview with shortage report before release | ● | ● | ● | ● | ● ? | ● ? | **V2** |
| 183 | **Waveless / continuous release** (Manhattan "Order Streaming") | ● the differentiator | ◐ ? | ◐ | ◐ ? | ◐ ? | ◐ ? | **V3** — do not chase this at v1 |
| 184 | Short-pick handling: re-allocate, emergency replen, or short the line | ● | ● | ● | ● | ● | ● | **V1.1** |
| 185 | Cancel an order after allocation → deterministic de-allocation | ● | ● | ● | ● | ● | ● | **V1** — impossible with a counter (T-014) |
| 186 | Modify an order after release (add/remove lines, change qty) | ● | ● | ● | ● | ● ? | ● ? | **V2** |
| 187 | Shipment consolidation across orders to one customer/route | ● | ● | ● | ● | ● | ● | **V2** |
| 188 | Order split / sourcing across sites | ● (DOM) | ● (DOM) | ○ (ERP/ATP) | ◐ | ◐ ? | ◐ ? | **NO** — §4, that is an OMS |
| 189 | Substitute-item allocation | ◐ | ◐ | ◐ | ◐ ? | ◐ ? | ◐ ? | **V2** |
| 190 | Customer-specific packing / labelling requirement driving the pick | ● | ● | ● | ● | ● | ● | **V2** |
| 191 | Allocation audit: why did this order get this stock | ● | ● | ● | ● | ● ? | ● ? | **V1.1** — a column on `wb_allocations`, not a log line |

## 1.9 Picking and execution methods

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 192 | Discrete single-order pick | ● | ● | ● | ● | ● | ● | **V1** |
| 193 | Batch pick (multi-order, one pass, consolidate later) | ● | ● | ● | ● | ● | ● | **V1.1** |
| 194 | Cluster pick (cart with N totes, pick to position) | ● | ● | ● | ● | ● | ● | **V2** |
| 195 | Zone pick, pick-and-pass | ● | ● | ● | ● | ● | ● | **V2** |
| 196 | Zone pick with downstream consolidation | ● | ● | ● | ● | ● | ● | **V2** |
| 197 | Pick to carton (cartonisation-driven pick) | ● | ● | ● | ● | ● | ● | **V2** |
| 198 | Pick-to-light / put-to-light | ● | ● | ◐ (via interface) | ◐ | ● ? | ● ? | **V3** interface only |
| 199 | Voice picking | ● | ● ? | ◐ (partner/interface) | ◐ ? | ● (Voiteq heritage) | ● | **V3** interface only |
| 200 | Put wall / order sortation | ● | ● | ◐ | ◐ ? | ● ? | ● ? | **V3** |
| 201 | Piece / case / pallet pick distinguished with different flows | ● | ● | ● | ● | ● | ● | **V1.1** |
| 202 | Full-LPN pick (move a whole pallet to shipping) | ● | ● | ● | ● | ● | ● | **V1.1** |
| 203 | **Task interleaving** (assign a putaway on the return trip) | ● | ● | ● | ● | ● | ● | **V2** — needs `wb_tasks` from V1 (T-041) |
| 204 | Task priority and dynamic re-prioritisation | ● | ● | ● | ● | ● | ● | **V2** |
| 205 | Task assignment by user, zone, equipment capability | ● | ● | ● resource type / qualification | ● | ● | ● | **V2** |
| 206 | Short / skip / exception codes with supervisor queue | ● | ● | ● | ● | ● | ● | **V1.1** |
| 207 | Scan verification at pick: location, item, lot, serial, qty | ● | ● | ● | ● | ● | ● | **V1.1** |
| 208 | Pick-path optimisation within a zone | ● | ● | ● | ● | ● | ● | **V2** |
| 209 | Directed (system picks the task) vs user-selected task | ● | ● | ● | ● | ● | ● | **V1.1** |
| 210 | Pick confirmation offline, synced later, with conflict resolution | ● | ● | ◐ | ◐ | ● ? | ● ? | **V3** (T-053) |

## 1.10 Packing, shipping, load and dock

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 211 | Cartonisation (pre-plan carton mix from dims/weight) | ● | ● | ● packing instructions | ● | ● | ● | **V2** |
| 212 | Pack station with scan-verify against the order | ● | ● | ● | ● | ● | ● | **V1.1** |
| 213 | Check weight tolerance at pack | ● | ● | ● | ● | ● ? | ● ? | **V2** |
| 214 | Carton content label, GS1-128 / SSCC | ● | ● | ● | ● | ● | ● | **V2** |
| 215 | Packing list / delivery challan print | ● | ● | ● | ● | ● | ● | **V1** — India: delivery challan is a legal document for stock movement |
| 216 | BoL, commercial invoice, shipping documents | ● | ● | ● | ● | ● | ● | **V2** |
| 217 | Carrier rate shop / service selection | ◐ (Manhattan TMS ●) | ◐ (BY TMS ●) | ○ (SAP TM ●) | ◐ | ◐ ? | ◐ ? | **NO** — §4, that is a TMS |
| 218 | Parcel carrier label generation via carrier API | ● | ● | ◐ | ● | ● ? | ● ? | **V3** — one carrier connector, not an engine |
| 219 | Manifest / end-of-day close | ● | ● | ● | ● | ● | ● | **V2** |
| 220 | Load planning and load build (which pallets on which trailer) | ● | ● | ● | ◐ | ◐ ? | ● | **V3** |
| 221 | Dock door assignment and staging lane management | ● | ● | ● | ● | ● | ● | **V2** |
| 222 | Loading sequence and load verification scan | ● | ● | ● | ● | ● | ● | **V2** |
| 223 | **Ship confirm → inventory relief as a ledger event** | ● | ● | ● goods issue | ● | ● | ● | **V1** |
| 224 | Proof of delivery hand-off / ePOD | ◐ | ◐ | ○ | ○ | ◐ ? | ◐ ? | **V2** — hand off to the existing field-service / delivery modules |
| 225 | Outbound ASN / EDI 856 to the customer | ● | ● | ● | ● | ● | ● | **V3** |
| 226 | Small parcel vs LTL vs FTL distinguished flows | ● | ● | ◐ | ● | ● ? | ● ? | **V3** |
| 227 | Carrier tracking status returned onto the shipment | ◐ | ◐ | ○ | ◐ | ◐ ? | ◐ ? | **V3** |
| 228 | Freight cost capture on the shipment | ◐ | ◐ | ○ | ◐ | ◐ ? | ◐ ? | **V3** |
| 229 | Export / customs documentation | ◐ | ◐ | ● (GTS) | ◐ | ◐ ? | ◐ ? | **NO** — §4 |
| 230 | **e-Way bill trigger on stock transfer / outbound (India)** | ○ | ○ | ◐ (India localisation) | ○ | ○ | ○ | **V1.1** — statutory here, absent from every tier-1 (T-083) |

## 1.11 Replenishment and slotting

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 231 | Min/max replenishment of pick faces | ● | ● | ● | ● | ● | ● | **V1.1** |
| 232 | Demand-driven / wave-driven replenishment | ● | ● | ● | ● | ● | ● | **V2** |
| 233 | Top-off / opportunistic replenishment during idle time | ● | ● | ● | ● | ● ? | ● ? | **V2** |
| 234 | Break-case replenishment (case reserve → each pick face) | ● | ● | ● | ● | ● | ● | **V2** |
| 235 | Emergency replenishment triggered by a short pick | ● | ● | ● | ● | ● | ● | **V2** |
| 236 | Replenishment priority vs pick starvation control | ● | ● | ● | ● | ● ? | ● ? | **V2** |
| 237 | Slotting analysis (velocity → golden zone) | ● | ● | ● slotting & rearrangement | ◐ | ● ? | ◐ ? | **V3** |
| 238 | Slotting what-if / optimisation run | ● | ● (Slotting Optimization) | ● | ◐ ? | ◐ ? | ◐ ? | **V3** |
| 239 | Re-slotting move-task generation | ● | ● | ● | ◐ | ◐ ? | ◐ ? | **V3** |
| 240 | Slotting by cube, weight, ergonomics | ● | ● | ● | ◐ | ◐ ? | ◐ ? | **V3** |
| 241 | Slotting by pick affinity (items ordered together) | ● | ● | ◐ | ○ ? | ◐ ? | ◐ ? | **V3** |
| 242 | Seasonal / periodic re-slotting campaign | ● | ● | ● | ◐ ? | ◐ ? | ◐ ? | **V3** |

## 1.12 Execution layer — RF, tasks, labour, automation

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 243 | RF / handheld screen for every warehouse transaction | ● | ● | ● (ITSmobile / RF framework) | ● | ● | ● | **V1.1** — on the existing `mobile/` app (T-051) |
| 244 | **Configurable RF flows without code** | ● | ● | ◐ (dev-ish) | ● screen configuration | ● Architect toolkit | ● | **V3** |
| 245 | Native Android/iOS app rather than telnet emulation | ● | ● | ◐ | ● | ● | ● | **V1.1** — we already have one; a real advantage |
| 246 | Offline RF operation with queued transactions | ◐ | ◐ | ○ | ◐ | ● ? | ● ? | **V3** (T-053) |
| 247 | Camera scanning as well as laser/imager | ● | ● | ◐ | ● | ● | ● | **V1.1** |
| 248 | Task engine: priority, zone, resource capability, queue | ● | ● | ● WT/WO + creation rules | ● | ● | ● | **V1-M** (T-041) |
| 249 | **Labour management: engineered standards** (discrete elements, travel time) | ● a genuine differentiator | ● RedPrairie heritage | ● EWM LM | ◐ ? | ◐ ? | ● | **NO** as a standards engine — §4; **V2** for actual-vs-target |
| 250 | Actual vs standard performance reporting by operator | ● | ● | ● | ◐ ? | ◐ ? | ● | **V2** |
| 251 | Incentive pay calculation | ● | ● | ◐ | ○ ? | ○ ? | ◐ ? | **NO** — §4 |
| 252 | Workload planning / shift staffing projection | ● | ● | ● | ◐ ? | ◐ ? | ◐ ? | **V3** |
| 253 | Exception queue and supervisor console | ● | ● | ● (monitor) | ● | ● | ● | **V1.1** |
| 254 | Voice interface | ● | ● ? | ◐ | ◐ ? | ● | ● | **V3** — integrate, never build |
| 255 | Pick-to-light interface | ● | ● | ◐ | ◐ ? | ● ? | ● ? | **V3** |
| 256 | Conveyor / sorter (WCS) interface | ● | ● | ● | ◐ | ● (Aberle) | ● | **V3** |
| 257 | **AS/RS direct control (PLC telegrams)** | ◐ (via WES) | ◐ | ● MFS — unique at this depth | ○ | ● ? (Aberle) | ◐ ? | **NO** — §4 |
| 258 | AMR / robotics orchestration | ● | ● | ◐ | ◐ | ● | ● ? | **V3** — event API only |
| 259 | Label design + print service (zebra/ZPL, printer groups) | ● | ● | ● | ● | ● | ● | **V1.1** |
| 260 | Real-time operations dashboard / control tower | ● | ● (Luminate) | ● | ● | ● | ● | **V2** on `PLAT` dashboards |
| 261 | Device / session management, forced logout, device registry | ● | ● | ● | ● | ● | ● | **V2** |
| 262 | Shift simulation / digital twin | ◐ | ● ? | ◐ | ○ | ◐ ? | ◐ ? | **NO** — §4 |

## 1.13 Valuation and the finance interface

> **The single most important row in this table is #263.** SAP EWM carries **no value at all** — quantity
> lives in EWM, value lives in S/4 MM/FI and the Material Ledger. Manhattan, Blue Yonder, Körber, Infor
> and Oracle WMS Cloud are the same: they are quantity engines that hand movements to an ERP. Oracle
> *Fusion Cloud Inventory* does carry cost, but through **Oracle Cost Management**, a separate product.
> That is the tier-1 consensus and it is a warning: whoever builds valuation into the WMS is building an
> accounting sub-ledger, and it must be built to sub-ledger standards or not at all.

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 263 | Does the WMS hold inventory **value** at all? | ○ (ERP) | ○ (ERP) | ○ — deliberately | ○ WMS Cloud / ● Fusion Inv + Costing | ○ ? | ◐ ? | **V1** — we hold it, because our buyer has no ERP (T-060) |
| 264 | FIFO costing over receipt layers | n/a | n/a | n/a (S/4 ●) | ● (Costing) | n/a | ◐ ? | **V1** — the only v1 method |
| 265 | Weighted average (moving) | n/a | n/a | n/a (S/4 ●) | ● | n/a | ◐ ? | **V1.1** |
| 266 | Standard cost with purchase price and usage variances | n/a | n/a | n/a (S/4 ●) | ● | n/a | ◐ ? | **V2** |
| 267 | Specific identification (cost carried on the serial/lot) | n/a | n/a | n/a (S/4 ◐) | ◐ | n/a | ◐ ? | **V1.1** — for serialised automotive parts |
| 268 | LIFO | n/a | n/a | n/a (S/4 ◐, jurisdiction-limited) | ◐ | n/a | ○ ? | **NO** — §4, not permitted under Ind AS / IFRS |
| 269 | **Cost layers with remaining quantity** | n/a | n/a | n/a | ● | n/a | ◐ ? | **V1** `wb_cost_layers` (T-061) |
| 270 | Landed cost apportionment (freight, duty, insurance, clearing) | n/a | n/a | n/a (S/4 ●) | ● | n/a | ◐ ? | **V2** — layer must allow later cost adjustment (T-063) |
| 271 | Revaluation as a document, not an UPDATE | n/a | n/a | n/a (S/4 ●) | ● | n/a | ◐ ? | **V1.1** |
| 272 | COGS recognised at ship confirm | n/a | n/a | n/a | ● | n/a | ◐ ? | **V1.1** |
| 273 | GL posting rules keyed by transaction type × reason code × item group | n/a | n/a | ● movement types drive it | ● | n/a | ◐ ? | **V1** `wb_posting_rules` (T-065) |
| 274 | Inventory sub-ledger ↔ GL control account reconciliation report | n/a | n/a | ● (ERP) | ● | n/a | ◐ ? | **V1.1** — the report that makes an auditor sign (T-066) |
| 275 | Stock valuation **as at any past date** | n/a | n/a | ● (ERP) | ● | n/a | ◐ ? | **V1.1** — only possible if §3.1 holds |
| 276 | Obsolescence provision / NRV write-down | n/a | n/a | ● (ERP) | ● | n/a | ○ ? | **V2** |
| 277 | Inter-site / intercompany transfer pricing | n/a | n/a | ● (ERP) | ● | n/a | ◐ ? | **V2** |
| 278 | Consignment stock excluded from valuation | n/a | n/a | ● (ERP) | ● | n/a | ◐ ? | **V2** — free once `owner_id` + `is_valued` exist |
| 279 | Multi-currency purchase cost with a rate captured at receipt | n/a | n/a | ● (ERP) | ● | n/a | ◐ ? | **V2** |
| 280 | Value by owner (3PL: client's goods are off our balance sheet) | n/a | n/a | ◐ | ● | n/a | ◐ ? | **V2** |
| 281 | **Declared valuation grain** (owner × item × site, or × company) | n/a | n/a | ● plant/valuation area | ● | n/a | ◐ ? | **V1** — a written decision, not an emergent property (T-062) |
| 282 | Negative-stock costing policy (what cost does an oversell consume) | n/a | n/a | ● | ● | n/a | ◐ ? | **V1.1** |
| 283 | Hand-off to the Classic accounting product rather than a private GL | — | — | — | — | — | — | **V1** — publish events; do not write journals directly (T-067) |

## 1.14 Multi-owner, 3PL and billing

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 284 | **Owner of goods on every stock record** | ● | ● | ◐ (party entitled to dispose) | ● company/facility model | ● | ● | **V1-M** — the column, always (T-002) |
| 285 | 3PL client master with per-client configuration | ● | ● | ◐ | ● | ● | ● | **V2** `warehouse-3pl` |
| 286 | Client-level data segregation and user scoping | ● | ● | ◐ | ● | ● | ● | **V2** — on `PLAT` RBAC + a row-level guard |
| 287 | Client-specific item, UoM, location and rule overrides | ● | ● | ◐ | ● | ● | ● | **V2** |
| 288 | Client portal: stock visibility, order entry, reports | ● | ● | ○ | ● | ● | ● | **V2** — reuse the platform's public/no-login foundation |
| 289 | **Storage billing** (per pallet-day, per sqft, per unit, per LPN) | ● | ● | ○ | ● ? | ● | ● | **V2** |
| 290 | **Handling billing** (receipt, putaway, pick, pack, ship) | ● | ● | ○ | ● ? | ● | ● | **V2** |
| 291 | Activity-based billing engine with rate cards and effective dates | ● | ● | ○ | ◐ ? | ● | ● | **V2** — needs a `billable_event` flag on the ledger (T-071) |
| 292 | Ad-hoc / accessorial charges | ● | ● | ○ | ◐ ? | ● | ● | **V2** |
| 293 | Billing period close → invoice generation | ● | ● | ○ | ◐ ? | ● | ● | **V2** — hand to the accounting product |
| 294 | Minimum charges, tiered / banded rates, contract terms | ● | ● | ○ | ◐ ? | ● | ● | **V2** |
| 295 | Client SLA definition and measurement | ● | ● | ○ | ◐ ? | ● ? | ● ? | **V3** |
| 296 | Dedicated vs shared space allocation and charging | ● | ● | ○ | ◐ ? | ● ? | ● ? | **V3** |
| 297 | Cross-client contamination prevention (no mixed-owner LPN/location) | ● | ● | ◐ | ● | ● | ● | **V2** — a rule on the location, enabled by `owner_id` |
| 298 | Client onboarding template / copy-a-client | ◐ | ◐ | ○ | ◐ ? | ● ? | ◐ ? | **V3** |
| 299 | Billing for value-added services (kitting, labelling) with labour capture | ● | ● | ○ | ◐ ? | ● | ● | **V3** |

## 1.15 Planning-adjacent — and where the boundary sits

> The tier-1 boundary is consistent: a WMS holds **reorder point, min/max and safety stock as item-site
> attributes** and generates replenishment *inside* the four walls, but forecasting, multi-echelon
> optimisation and purchase planning belong to a planning product (Blue Yonder's planning suite, SAP
> IBP, Oracle Demand Management, Manhattan's demand forecasting). We should draw the same line and say
> so, then put the rest in a future supply-chain/logistics module rather than pretending it is out of
> scope.

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 300 | Reorder point / safety stock per item-site | ◐ | ◐ | ○ (ERP) | ◐ (Fusion ●) | ◐ | ● | **V1** — columns exist in accessories already |
| 301 | Min/max per item-**location** (not just item-site) | ● | ● | ● | ● | ● | ● | **V1.1** |
| 302 | EOQ / order quantity calculation | ○ | ◐ (planning) | ○ | ◐ | ○ ? | ◐ ? | **V2** |
| 303 | Purchase requisition generation from below-ROP | ○ | ◐ | ○ | ◐ | ○ ? | ◐ ? | **V1.1** — a suggestion list, not a PO engine |
| 304 | Supplier lead time held and used | ◐ | ● | ○ | ● | ◐ ? | ● | **V1.1** |
| 305 | Demand forecast **interface** (consume a forecast, do not compute one) | ● | ● | ◐ | ● | ◐ ? | ● | **V3** |
| 306 | Forecasting itself | ○ (separate product) | ● (separate product) | ○ | ○ (separate) | ○ | ○ | **NO** — §4, future logistics module |
| 307 | Days-of-cover / stock-out prediction | ◐ | ● | ○ | ◐ | ◐ ? | ◐ ? | **V2** |
| 308 | ABC/XYZ recomputation job | ● | ● | ● | ● | ● | ● | **V1.1** |
| 309 | Excess & obsolete alerting | ◐ | ● | ○ | ◐ | ◐ ? | ◐ ? | **V2** |
| 310 | Multi-echelon inventory optimisation | ○ | ● (separate) | ○ | ◐ | ○ | ○ | **NO** — §4 |
| 311 | Fair-share allocation across sites in shortage | ◐ | ● | ○ | ◐ | ○ ? | ◐ ? | **V3** |
| 312 | ATP / available-to-promise served to other modules | ◐ | ● | ○ (ERP) | ● (GOP) | ◐ ? | ◐ ? | **V1.1** — a read API `GET /availability`; our verticals need it immediately |
| 313 | Seasonal profile / promotion uplift | ○ | ● | ○ | ◐ | ○ ? | ○ ? | **NO** — §4 |
| 314 | Vendor-managed inventory / supplier portal replenishment | ◐ | ● | ◐ | ◐ | ◐ ? | ◐ ? | **V3** |

## 1.16 Value-added services, kitting and light manufacturing

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 315 | Kit assembly work order with component consumption | ● | ● | ● VAS order | ● | ● | ● | **V1.1** |
| 316 | Disassembly / de-kit back to components | ● | ● | ● | ● | ● | ● | **V1.1** |
| 317 | Kit BOM with substitutes and yield/scrap % | ◐ | ◐ | ◐ | ◐ | ● ? | ◐ ? | **V2** |
| 318 | Labelling / ticketing / re-pricing VAS | ● | ● | ● | ● | ● | ● | **V2** |
| 319 | Rework / repack orders | ● | ● | ● | ● | ● | ● | **V2** |
| 320 | VAS attached to an inbound or outbound flow (not standalone) | ● | ● | ● | ● | ● | ● | **V2** |
| 321 | Light assembly / assemble-to-order | ◐ | ◐ | ◐ | ◐ | ● ? | ◐ ? | **V3** |
| 322 | Component backflush on assembly completion | ◐ | ◐ | ● | ● | ◐ ? | ◐ ? | **V2** |
| 323 | Serial genealogy preserved through assembly | ◐ | ◐ | ◐ | ◐ | ◐ ? | ◐ ? | **V2** |
| 324 | VAS labour capture, billable to a 3PL client | ● | ● | ◐ | ◐ ? | ● | ● | **V3** |
| 325 | **Fitment / installation consumption** (part issued to a job card) | ○ | ○ | ○ | ○ | ○ | ○ | **V1.1** — adapter to `services` / `field-service`; our whole reason to exist (T-081) |

## 1.17 Returns and reverse logistics

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 326 | RMA / return authorisation document | ● | ● | ● returns delivery | ● | ● | ● | **V1.1** |
| 327 | Blind return receipt (no RMA) | ● | ● | ● | ● | ● | ● | **V1.1** |
| 328 | Return reason code capture | ● | ● | ● | ● | ● | ● | **V1.1** |
| 329 | Disposition: restock / repair / scrap / RTV / liquidate / quarantine | ● | ● | ● | ● | ● | ● | **V1.1** |
| 330 | Return-to-vendor document and shipment | ● | ● | ● | ● | ● | ● | **V2** |
| 331 | Credit hand-off to finance | ◐ | ◐ | ● (ERP) | ● | ◐ ? | ◐ ? | **V2** |
| 332 | Warranty return linked to the original serial and shipment | ◐ | ◐ | ◐ | ◐ | ◐ ? | ◐ ? | **V2** — high value for our verticals |
| 333 | Refurbishment / repair loop with a distinct stock status | ◐ | ◐ | ◐ | ◐ | ◐ ? | ◐ ? | **V2** |
| 334 | **Core return / exchange unit (automotive)** | ○ | ○ | ○ | ○ | ○ | ○ | **V2** — a vertical capability nobody in tier 1 has (T-082) |
| 335 | Condition grading on return (A/B/C) | ◐ | ◐ | ◐ | ◐ | ● ? | ◐ ? | **V2** |
| 336 | Returns land in a dedicated stock status, never straight to available | ● | ● | ● | ● | ● | ● | **V1.1** |
| 337 | Returns analytics by reason, item, customer, supplier | ◐ | ● | ◐ | ◐ | ◐ ? | ● ? | **V2** |

## 1.18 Yard, dock and appointments

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 338 | Internal appointment booking against dock capacity | ● | ● | ◐ | ◐ ? | ● ? | ● | **V2** |
| 339 | Carrier self-service appointment portal | ◐ | ◐ | ○ | ○ ? | ◐ ? | ◐ ? | **V3** |
| 340 | Dock door calendar and capacity model | ● | ● | ◐ | ◐ ? | ● ? | ● | **V2** |
| 341 | Gate check-in / check-out with driver and vehicle | ● | ● | ● YM | ◐ | ◐ ? | ● | **V3** |
| 342 | Trailer master and yard position tracking | ● | ● | ● | ◐ | ◐ ? | ● | **V3** |
| 343 | Yard move task (spot to door, door to spot) | ● | ● | ● | ◐ | ◐ ? | ● | **V3** |
| 344 | Detention / demurrage measurement | ● | ● | ◐ | ○ ? | ◐ ? | ◐ ? | **V3** |
| 345 | Driver kiosk / mobile check-in | ◐ | ◐ | ○ | ○ ? | ◐ ? | ◐ ? | **V3** |
| 346 | Seal number capture at load and unload | ● | ● | ● | ● | ● ? | ● | **V2** |
| 347 | Trailer as a stock location (inventory on wheels) | ● | ● | ● | ◐ | ◐ ? | ● | **V3** |

## 1.19 Analytics, KPI and compliance

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 348 | Dock-to-stock time | ● | ● | ● | ● | ● | ● | **V1.1** |
| 349 | Order cycle time / on-time ship | ● | ● | ● | ● | ● | ● | **V1.1** |
| 350 | Pick accuracy, lines/hour, units/hour | ● | ● | ● | ● | ● | ● | **V2** |
| 351 | Inventory record accuracy (from counts) | ● | ● | ● | ● | ● | ● | **V1.1** |
| 352 | Fill rate / OTIF | ● | ● | ◐ | ● | ● | ● | **V2** |
| 353 | Dwell time (receipt to putaway, pick to ship) | ● | ● | ● | ● | ● | ● | **V2** |
| 354 | Space / location utilisation | ● | ● | ● | ● | ● | ● | **V2** |
| 355 | Labour productivity by operator and function | ● | ● | ● | ◐ | ◐ ? | ● | **V2** |
| 356 | Configurable dashboards | ● | ● | ● | ● | ● | ● | **PLAT** |
| 357 | Full audit trail on every stock transaction | ● | ● | ● | ● | ● | ● | **V1** — the ledger *is* the audit trail |
| 358 | Forward/backward traceability report | ● | ● | ● | ● | ● | ● | **V1.1** |
| 359 | Recall execution workflow (hold, notify, report) | ● | ● | ● | ● | ● | ● | **V2** |
| 360 | e-signature / 21 CFR Part 11 style controls | ◐ ? | ◐ ? | ◐ ? | ◐ ? | ◐ ? | ◐ ? | **V3** |
| 361 | UDI / medical-device compliance | ◐ | ◐ | ◐ | ◐ | ◐ ? | ◐ ? — **Tecsys ●** | **NO** — §4 |
| 362 | GDP/GMP, temperature excursion capture | ◐ | ◐ | ● | ◐ | ● ? | ◐ ? | **V3** |

## 1.20 Integration surface and extensibility

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 363 | REST API for masters and transactions | ● | ● | ◐ (OData/BAPI/IDoc) | ● | ● | ● | **V1** |
| 364 | **Idempotent ingestion** with an external key | ● | ● | ● (IDoc dedup) | ● | ● ? | ● ? | **V1** — `source_system + source_ref + source_ref_line` unique (T-091) |
| 365 | Event / webhook publishing on stock change | ● | ● | ◐ | ● | ● | ● | **V1.1** — the adapters' subscription point |
| 366 | EDI 850/855/856/940/943/944/945/947/810/214 | ● | ● | ◐ (via PI/CPI) | ● | ● | ● | **V3** |
| 367 | Flat-file / SFTP batch interface | ● | ● | ● | ● | ● | ● | **PLAT** import framework |
| 368 | Message queue interface (AMQP/Kafka) | ● | ● | ◐ | ● | ● ? | ● ? | **V3** |
| 369 | Interface monitoring, error queue, reprocess-from-UI | ● | ● | ● | ● | ● | ● | **V1.1** — `wb_inbound_messages` with a status and a retry action (T-092) |
| 370 | Pre-built ERP connector packs | ● | ● | ● (native) | ● | ● | ● | **V1** — our "connector" is the vertical adapter |
| 371 | Carrier connectors | ● | ● | ◐ | ● | ● ? | ● ? | **V3** |
| 372 | WCS / automation interface | ● | ● | ● | ◐ | ● | ● | **V3** |
| 373 | Marketplace / e-commerce connectors | ◐ | ◐ | ○ | ◐ | ● ? | ◐ ? | **V3** |
| 374 | **Rules engine / low-code configuration of flows** | ● | ● | ◐ | ● | ● Architect — the marquee feature | ● | **V2** — a rules *table*, not an engine (T-093) |
| 375 | Custom fields on core objects, without a schema change | ● | ● | ◐ | ● | ● | ● | **V3** — CLAUDE.md forbids JSONB, so this needs a designed EAV or nothing (T-094) |
| 376 | Custom label and document templates | ● | ● | ● | ● | ● | ● | **V2** |
| 377 | Sandbox / test environment with data refresh | ● | ● | ● | ● | ● | ● | **V3** |
| 378 | Bulk endpoints and rate limits | ● | ● | ◐ | ● | ● ? | ● ? | **V1.1** |
| 379 | Data export to BI / warehouse | ● | ● | ● | ● | ● | ● | **PLAT** export + a read replica |
| 380 | Versionless / continuous upgrade | ● Manhattan Active is explicitly versionless | ◐ | ◐ | ● | ◐ | ◐ | **V1** — we are single-codebase SaaS; state it as a differentiator |

## 1.21 Non-functional

| # | Capability | Manhattan | Blue Yonder | SAP EWM | Oracle WMS Cloud | Körber | Infor | Our v1 verdict |
|---|---|---|---|---|---|---|---|---|
| 381 | Multi-tenant SaaS | ● | ◐ | ○ | ● | ◐ | ◐ | **NO** — we are single-tenant per install by platform decision; state it |
| 382 | On-prem / private deployment option | ● | ● | ● | ○ | ● | ● | **V1** — inherited |
| 383 | Throughput: hundreds of thousands of lines/day per site | ● | ● | ● | ● | ● | ● | **V1** — needs the ledger partitioned by `occurred_at` from day one (T-095) |
| 384 | Sub-second RF transaction response | ● | ● | ● | ● | ● | ● | **V1.1** |
| 385 | Offline tolerance on the floor | ◐ | ◐ | ○ | ◐ | ● ? | ● ? | **V3** |
| 386 | High availability / failover | ● | ● | ● | ● | ● | ● | **V1** — inherited |
| 387 | Multi-language UI | ● | ● | ● | ● | ● | ● | **PLAT** i18n |
| 388 | Multi-timezone across sites in one instance | ● | ● | ● | ● | ● | ● | **V1** (T-018) |
| 389 | Granular role/permission model | ● | ● | ● | ● | ● | ● | **PLAT** RBAC |
| 390 | Ledger volume: 10^8+ rows with acceptable query latency | ● | ● | ● | ● | ● | ● | **V1** — partitioning + the snapshot table (T-095) |
| 391 | Disaster recovery / RPO-RTO commitments | ● | ● | ● | ● | ● | ● | **V2** |
| 392 | Data retention / archive of ledger rows without losing reconstructibility | ● | ● | ● | ● | ● ? | ● ? | **V3** — archive must carry an opening-balance row (T-020a) |

## 1.22 Softeon and Tecsys — where they diverge from the six columns

Softeon and Tecsys are in the brief but not in the matrix columns; putting them in would have made
every table unreadable. Both are genuine tier-1/upper-mid competitors and both are relevant to us for
specific reasons.

**Softeon.** Known for configurability-over-customisation and for a strong **Distributed Order
Management** alongside the WMS, and for warehouse-execution capability (put walls, order sortation,
e-commerce fulfilment). Softeon's commercial pitch has historically been rapid deployment and a lower
total cost than Manhattan/Blue Yonder at comparable function, which makes them the product a buyer
compares us to when they have decided they cannot afford tier 1. **Relevance to us:** their positioning
is the one we would occupy if we execute; their DOM is a capability we should explicitly *not* chase
(§4). Confidence on specific module names: `?`.

**Tecsys.** Distinctive in **healthcare supply chain** — point-of-use replenishment at nursing units,
surgical case-cart picking, consignment implant tracking, UDI capture — and in complex distribution
and 3PL. Tecsys also carries a delivery-management/last-mile capability alongside the WMS, which is
unusual. **Relevance to us:** (a) their point-of-use and consignment model is the closest existing
analogue to *our* van-stock / job-card consumption problem in `services` and `field-service`, and is
worth studying rather than inventing; (b) their UDI/healthcare compliance is exactly the vertical we
should decline (§4). Confidence on specific module names: `?`.

**What both of them prove for §5:** neither wins on breadth against SAP EWM or Manhattan. They win by
being *complete on a defined operating model* and by deploying fast. That is the only credible shape
for our v1.

---

# §2 — FINDINGS

**Table-prefix convention used throughout** (proposed, and itself a decision to ratify):
`wb_` = `warehouse-base` · `wh_` = `warehouse` · `w3_` = `warehouse-3pl` · `wa_<vertical>_` = adapters.
Where a finding says a column belongs on `wb_stock_ledger`, it means `warehouse-base` owns it and every
other module reads it.

**Severity.** `BLOCKER` = a real WMS cannot be sold without it, **or** it is a schema/sequencing
decision that is unrecoverable later. `MAJOR` = a deal-losing or operationally painful gap that can be
added without restating history. `MINOR` = should exist, cheap whenever it is done.

---

## 2.1 The stock ledger and the core model (T-001 … T-020)

### T-001 — BLOCKER — The stock ledger must be double-sided and append-only; the existing precedent is neither
**Gap.** `accessory_inventory_transactions` (`InventoryTransaction.java:77-93`) writes **one row per
movement carrying `from_warehouse_id`, `from_bin_id`, `to_warehouse_id`, `to_bin_id`**. Every tier-1
WMS writes a movement as **two signed rows** — a decrease at the source and an increase at the
destination — exactly as a general ledger writes a debit and a credit.
**Why it matters.** With from/to on one row, "on hand at location L" is not `SUM(qty) WHERE
location_id = L`; it is a `CASE` over two nullable columns, repeated in every query, report, export and
allocation join in the product. Receipts have a null from-side, issues have a null to-side, and
adjustments have neither, so the `CASE` grows a branch per transaction type forever. It also makes it
impossible to state the invariant that makes a stock system trustworthy: **Σ qty across all locations
for an item = 0 only when every movement has a counterparty.** That invariant is what lets you detect
that stock has leaked, and it is unavailable in a from/to model.
**Recommendation.** `wb_stock_ledger`, insert-only, one row per movement *side*:
`id, movement_id, movement_line_no, side (+1/-1), occurred_at, posted_at, site_id, location_id,
item_id, lot_id, serial_id, lpn_id, owner_id, stock_status_id, qty_base NUMERIC(18,4), uom_id,
qty_entered NUMERIC(18,4), qty_catch NUMERIC(18,4), catch_uom_id, unit_cost, cost_layer_id, value_base,
currency_code, reason_code_id, ref_doc_type, ref_doc_id, ref_doc_line_id, source_module, source_system,
source_ref, actor_user_id, device_id, reversal_of_ledger_id, created_at`.
Add `wb_stock_movements` as the header (`movement_type`, `movement_number`, `status`, narrative) so a
transfer is one movement with two ledger rows. Enforce with a DB constraint that a movement of type
`TRANSFER` has exactly one `-1` and one `+1` row per line, and every movement's ledger rows sum to zero
in `qty_base` **unless** the counterparty is a virtual location (T-009).
**Module.** `warehouse-base`. **Version.** **v1** — this is migration one.

### T-002 — BLOCKER — `owner_id` must be on the ledger and the on-hand table in v1, in every install
**Gap.** The brief puts owner-of-goods separation in `warehouse-3pl`, a later module. If `owner_id` is
not a column on `wb_stock_ledger` and `wb_stock_on_hand` from the first migration, `warehouse-3pl` is
not a module that plugs in — it is a re-key of the two largest tables in the product plus every
allocation, every cost layer, every report and every index.
**Why it matters.** Owner is a *dimension of the stock*, like location and lot. Manhattan, Blue Yonder,
Oracle WMS Cloud, Körber and Infor all carry it natively because all of them sell to 3PLs; SAP EWM
carries a weaker "party entitled to dispose". Beyond 3PL, `owner_id` is also what makes **consignment
stock**, **VMI**, **customer-owned material** (a customer's part left with a service workshop) and
**inter-company stock** expressible at all — four capabilities our own verticals need before any 3PL
deal exists. And it is what keeps a client's goods off our balance sheet, which is a statutory
distinction, not a convenience.
**Recommendation.** `wb_owners (id, owner_code, owner_name, owner_type ENUM('SELF','CLIENT',
'SUPPLIER_CONSIGNED','CUSTOMER_OWNED'), is_valued BOOLEAN, is_active)`; seed exactly one row per install
with `owner_type='SELF'`. Put `owner_id UUID NOT NULL` on `wb_stock_ledger`, `wb_stock_on_hand`,
`wb_allocations`, `wb_cost_layers`, `wb_lpns` and `wb_lots`. In v1 the UI never shows it and every write
defaults to the SELF owner. In v2 `warehouse-3pl` adds clients and the data model does not move.
**Module.** `warehouse-base` (column) / `warehouse-3pl` (behaviour). **Version.** **v1 model-only**.

### T-003 — BLOCKER — The on-hand unique key must be the full dimension tuple from day one
**Gap.** `accessory_stock_levels` (`StockLevel.java:46-79`) keys on product × warehouse × bin ×
`batch_number` string × `serial_number` string. Missing: stock status, owner, LPN, and lot-as-an-entity.
**Why it matters.** The on-hand table's unique key *is* the definition of what a stock balance is. Every
dimension you leave out is a dimension you can never report on, allocate by, or hold. Adding
`stock_status_id` later is worse than adding a column, because it changes the *meaning* of every
existing row: today's rows are implicitly "available", and the first quarantine transaction after the
migration makes historical rows ambiguous.
**Recommendation.** `wb_stock_on_hand` with
`UNIQUE (site_id, location_id, item_id, owner_id, stock_status_id, lot_id, serial_id, lpn_id)` — nullable
dimension columns get a sentinel (the nil UUID; the codebase already has a nil-UUID constant convention)
so the unique index actually fires on NULLs. Columns: `qty_on_hand, qty_allocated_hard,
qty_allocated_soft, qty_catch, last_movement_at, last_count_at, version`. `qty_available` is a **derived
view**, not a stored column, because its formula changes when soft allocation arrives.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-004 — BLOCKER — Inventory status must be a master table with behaviour flags, not an enum and not a location
**Gap.** No tier-1 WMS models "damaged" or "quarantine" as a bin. All of them have an inventory-status
dimension: SAP EWM stock types (unrestricted-use / quality inspection / blocked) plus availability
groups; Manhattan, Oracle and Körber have inventory status codes with an allocatable flag. The
accessories precedent has a `status` column that means *record* status (`'ACTIVE'`,
`InventoryTransaction.java:132-134`) — a different concept entirely.
**Why it matters.** Four facts about quarantined stock are independent and a bin cannot express them:
it **is** on hand; it **is** valued and owned; it **is not** allocatable; it **may** physically sit in the
pick face. Modelling status as a location forces a physical move for a paperwork event, breaks
FEFO/FIFO across the "same" stock, and makes the count of a bin disagree with the count of the item.
Modelling it as a CHECK-constrained enum on the ledger means every new status (`AWAITING_QC`,
`CUSTOMER_HOLD`, `RECALL_HOLD`, `RETURNED_UNGRADED`, `DEMO`, `EXPIRED`) is a migration plus a code
change in every query that lists "available" statuses.
**Recommendation.** `wb_stock_statuses (id, status_code, status_name, is_on_hand BOOLEAN,
is_allocatable BOOLEAN, is_valued BOOLEAN, blocks_shipment BOOLEAN, requires_disposition BOOLEAN,
is_system BOOLEAN, sort_order, is_active)`. Seed v1 with `AVAILABLE, QC_HOLD, DAMAGED, EXPIRED,
BLOCKED, IN_TRANSIT`. `stock_status_id` on the ledger and the on-hand row. Availability is
`SUM(qty) WHERE status.is_allocatable` — a join, never a hardcoded list. A **status change** is a
balanced two-row movement at the *same* location with `movement_type='STATUS_CHANGE'` and a mandatory
reason code.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-005 — BLOCKER — Lot must be an entity, not a `VARCHAR(50)` on the movement
**Gap.** `batch_number VARCHAR(50)` denormalised onto both the transaction and the stock level
(`InventoryTransaction.java:116-117`, `StockLevel.java:71-72`).
**Why it matters.** A lot has attributes — manufacture date, expiry, supplier lot, receipt date, a
certificate of analysis, and **its own status**. On a string you cannot hold a lot (T-004's hold applies
to a lot across every location at once), cannot compute FEFO without parsing, cannot attach a document,
cannot detect that the same physical lot was keyed two ways (`"L-2024/07"` vs `"L2024-07"`), and cannot
answer a recall — which is the one question that must be answerable in minutes, not days. The
free-string design is precisely why traceability retrofits are quoted in months.
**Recommendation.** `wb_lots (id, item_id, lot_code, supplier_lot_code, manufactured_on, expires_on,
best_before_on, received_on, country_of_origin, lot_status_id → wb_stock_statuses, attributes…,
UNIQUE(item_id, lot_code))`. `lot_id` on the ledger, on-hand, allocations and LPN contents. Lot codes
are `UPPER(TRIM())` normalised on write, per the codebase's existing code convention.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-006 — BLOCKER — Serial must be an entity with a current state, and serial control is a mode not a boolean
**Gap.** `serial_number VARCHAR(100)` on the movement and the balance; `Product.is_serialized BOOLEAN`
(`Product.java:152-154`).
**Why it matters.** (a) A boolean cannot express the four control modes every tier-1 supports —
*not tracked* / *captured at receipt only* / *captured at ship only* / *fully tracked through every
movement*. Real warehouses use all four on different items, and "captured at ship only" is by far the
most common for automotive spares and electronics. Forcing full tracking on an item that only needs
ship capture makes receiving unusable; forcing none loses warranty traceability. (b) A serial is a
*thing* with a current location, status, owner and parent LPN. Without a `wb_serials` row you cannot
answer "where is serial X now" without scanning the whole ledger, cannot detect a duplicate serial at
receipt, and cannot link a warranty claim to the shipment that sent it.
**Recommendation.** `wb_items.serial_control ENUM('NONE','RECEIPT','SHIP','FULL')` and
`wb_items.lot_control ENUM('NONE','OPTIONAL','REQUIRED')`. `wb_serials (id, item_id, serial_no,
current_site_id, current_location_id, current_status_id, current_owner_id, current_lpn_id, lot_id,
first_received_at, last_movement_at, UNIQUE(item_id, serial_no))`. Uniqueness scope
(per item vs global) is itself a v1 decision — recommend per item, with a site-level duplicate warning.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-007 — BLOCKER — `lpn_id` must exist on the ledger in v1 even though LPN handling is v1.1/v2
**Gap.** No licence-plate / handling-unit concept anywhere in the precedent.
**Why it matters.** Oracle WMS Cloud is *built* on the LPN — it is the primary object, and every
receipt, move, pick and ship is an LPN operation. SAP EWM has handling units; Manhattan, Blue Yonder,
Körber and Infor all have licence plates. It is how a warehouse moves 48 cartons with one scan. If
`lpn_id` is not a nullable column on `wb_stock_ledger` and `wb_stock_on_hand` in v1, then adding pallet
handling in v2 means every historical row has an unknowable LPN and every "what was on this pallet"
query starts at the v2 boundary. The column is free now; the history is not recoverable later.
**Recommendation.** `wb_lpns (id, lpn_code, parent_lpn_id, lpn_type, site_id, current_location_id,
status, owner_id, is_open, closed_at, gross_weight, UNIQUE(lpn_code))` plus `lpn_id` nullable on the
ledger, on-hand and allocations. v1 writes NULL everywhere and shows nothing. v1.1 introduces
receive-by-LPN and move-by-LPN. v2 does nesting and SSCC.
**Module.** `warehouse-base`. **Version.** **v1 model-only**.

### T-008 — BLOCKER — The location model must be a hierarchy, not four VARCHARs
**Gap.** `accessory_storage_bins` carries `zone`, `aisle`, `rack`, `level` as four independent
`VARCHAR` columns (`StorageBin.java:56-69`).
**Why it matters.** Four strings cannot answer "count zone A", "block aisle 12 for maintenance",
"assign all of mezzanine 2 to the night shift", or "what is the utilisation of rack B-04" — because
there is no row representing the zone, the aisle or the rack. They cannot be given a status, a capacity,
a work-area assignment or a pick sequence. Every tier-1 has a real hierarchy (SAP EWM storage
type → section → bin, plus activity areas; Manhattan and Oracle have area/zone/location trees).
Reparenting later is possible but every historical ledger row points at a bin whose ancestry has
changed, so historical zone-level reporting silently rewrites itself.
**Recommendation.** `wb_locations (id, site_id, parent_location_id, location_code, location_level
SMALLINT, location_type_id, zone_id, pick_sequence, is_virtual, status, capacity_weight,
capacity_volume, capacity_height, capacity_lpn_count, allow_mixed_item, allow_mixed_lot,
allow_mixed_owner, temperature_class, barcode, check_digit, UNIQUE(site_id, location_code))` with a
materialised `path` column for ancestor queries. Plus `wb_location_types` as a master carrying the
behaviour flags (`is_pickable`, `is_receivable`, `counts_as_on_hand`, `is_staging`, `is_dock`).
**Module.** `warehouse-base`. **Version.** **v1**.

### T-009 — BLOCKER — Virtual locations are mandatory, or the ledger cannot balance
**Gap.** Implicit in T-001: receipts have no source and issues have no destination, so the double-entry
has a hole.
**Why it matters.** Every accounting system closes this with a counter-account; every WMS closes it with
a virtual location. Without them, "the ledger sums to zero" is not a checkable invariant and a leak is
undetectable. It is also the only clean way to model **in-transit** stock between sites (T-016), which
otherwise becomes a `status='IN_TRANSIT'` hack that hides which site owns the risk.
**Recommendation.** Seed `wb_locations` with `is_virtual = true` rows per site and per install:
`VIRT_SUPPLIER`, `VIRT_CUSTOMER`, `VIRT_ADJUSTMENT`, `VIRT_SCRAP`, `VIRT_PRODUCTION`,
`VIRT_IN_TRANSIT`, `VIRT_COUNT_VARIANCE`, `VIRT_OPENING_BALANCE`. Every movement has a real
`from_location` and `to_location`, one of which may be virtual. Virtual locations have
`counts_as_on_hand = false` so they never appear in stock reports but always balance the ledger.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-010 — BLOCKER — Reason codes must be a master with a GL mapping, seeded in v1
**Gap.** Adjustments in the precedent carry free-text `notes` (`InventoryTransaction.java:126-127`).
**Why it matters.** "Why did stock change" is the question an auditor asks and the question a warehouse
manager is measured on. Free text cannot be grouped, cannot be trended, cannot drive an approval
threshold, and cannot be mapped to a GL account — which means the accounting hand-off (T-065) has
nothing to key on. Every tier-1 either has reason codes or, in SAP's case, movement types that carry the
same information.
**Recommendation.** `wb_reason_codes (id, reason_code, reason_name, applies_to_movement_types,
requires_approval_above_value, requires_document, gl_account_hint, is_increase_allowed,
is_decrease_allowed, is_active)`. `reason_code_id NOT NULL` on every adjustment, status change, scrap and
count-variance ledger row. Seed a v1 set: `COUNT_VARIANCE, DAMAGE_IN_WAREHOUSE, DAMAGE_IN_TRANSIT,
THEFT, EXPIRY, SAMPLE_ISSUE, FOUND, OPENING_BALANCE, SYSTEM_CORRECTION, RECLASSIFICATION`.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-011 — BLOCKER — UoM conversion belongs on the item, not on the UoM master
**Gap.** `accessory_uom.conversion_factor` is a column on the **UoM master** with a `base_unit_id`
self-reference (`Uom.java:64-73`). That says "a CASE is 12" globally.
**Why it matters.** A case of oil filters is 12; a case of wiper blades is 6; a case of brake pads is 4.
A global factor is only correct for physical units (kg→g, m→cm) and is wrong for every packaging unit,
which is most of a warehouse's UoM traffic. Once movements exist against the wrong factor, every
historical quantity is wrong in the base UoM and no migration can tell which rows were entered under
which assumption.
**Recommendation.** Keep `wb_uoms` for *physical* dimension conversion only (`uom_class`,
`base_uom_id`, `factor`) and add `wb_item_uom_conversions (item_id, from_uom_id, to_uom_id, factor
NUMERIC(18,6), is_default_purchase, is_default_sales, is_default_pack, UNIQUE(item_id, from_uom_id,
to_uom_id))`. `wb_items.base_uom_id` immutable once a ledger row exists — enforce with a trigger, do not
trust the service layer. Every ledger row persists `qty_entered` + `uom_id` **and** `qty_base`, so a
later factor correction never rewrites history.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-012 — BLOCKER (structural) — Catch weight needs a second quantity column reserved in v1
**Gap.** No second quantity dimension anywhere.
**Why it matters.** Catch weight — an item stocked in *eaches* but priced and shipped by *actual
weight* — is standard in food, meat, produce, chemicals and some metals, and is supported natively by
SAP EWM and Manhattan. It is not a UoM conversion: the weight of each unit is *different and must be
recorded*. Retrofitting a second quantity into a ledger means every aggregate, every report, every
integration payload and every valuation calculation changes shape. Reserving two nullable columns costs
nothing.
**Recommendation.** `qty_catch NUMERIC(18,4) NULL` and `catch_uom_id UUID NULL` on `wb_stock_ledger`
and `wb_stock_on_hand`; `wb_items.is_catch_weight BOOLEAN DEFAULT false` and `catch_uom_id`. v1 writes
NULL. If we never sell to food, we have carried two nullable columns; if we do, we have not rewritten
the ledger.
**Module.** `warehouse-base`. **Version.** **v1 model-only**.

### T-013 — BLOCKER — No JSONB anywhere in the stock model, and the precedent already violates this
**Gap.** `accessory_products.vehicle_compatibility` is `columnDefinition = "jsonb"`
(`Product.java:148-149`) in a codebase whose own standard says **NO JSONB** (CLAUDE.md, DATABASE
CONVENTIONS).
**Why it matters.** Beyond the standards violation, a JSONB attribute bag on an item or a ledger row is
the classic escape hatch that makes every future filter, index and report impossible. This is worth
stating as a design rule *before* the first migration because the temptation is strongest exactly where
tier-1 products offer "custom fields" (#375).
**Recommendation.** State the rule in the design set. Where variable attributes are genuinely needed
(lot characteristics, item attributes per client), use a designed typed-attribute table
`wb_item_attributes (item_id, attribute_def_id, value_text, value_number, value_date, value_uuid)` with
`wb_attribute_definitions` — not JSONB. Referred to the standards reviewer as well.
**Module.** `warehouse-base`. **Version.** **v1** (as a rule).

### T-014 — BLOCKER — Allocation must be an open-item ledger, not `quantity_reserved`
**Gap.** `accessory_stock_levels.quantity_reserved` is a scalar (`StockLevel.java:62-64`).
**Why it matters.** This is the exact structural analogue of the bill-by-bill finding in the accounting
audit, with the same consequence: a number that is right in aggregate and useless in detail. With a
counter you cannot answer *who* holds the reservation, cannot release order 4471's hold when the order
is cancelled, cannot distinguish soft (planning) from hard (picked-to) allocation, cannot allocate to a
specific lot/serial/LPN, cannot expire a stale reservation, and cannot reconcile the counter against
reality — so it drifts, and once it drifts the only repair is to zero it, which releases everyone's
stock at once. Every tier-1 WMS holds allocations as records.
**Recommendation.** `wb_allocations (id, demand_type, demand_id, demand_line_id, item_id, owner_id,
site_id, allocation_type ENUM('SOFT','HARD'), qty_base, uom_id, qty_entered, location_id NULL,
lot_id NULL, serial_id NULL, lpn_id NULL, stock_status_id, allocated_at, allocated_by, expires_at,
status ENUM('OPEN','PICKED','SHORT','RELEASED','CANCELLED'), release_reason_code_id,
allocation_rule_id, version)`. `qty_available = on_hand − Σ hard allocations` computed by view.
Keep the denormalised `qty_allocated_hard` on `wb_stock_on_hand` only as a *cache*, with a nightly
reconciliation job that alarms on drift (same pattern as T-019).
**Module.** `warehouse-base`. **Version.** **v1**.

### T-015 — BLOCKER — Movement type must be a master table, because it is the join point for everything
**Gap.** The precedent uses a `VARCHAR(30) transaction_type` with a comment listing five values
(`InventoryTransaction.java:56-57`).
**Why it matters.** SAP's movement types are the best-known example of why this matters: the movement
type is what drives the GL posting, the permitted status transitions, the document required, the
reversal counterpart, whether the movement is billable to a 3PL client, and whether it affects
valuation. A string with a comment can drive none of those and produces `if (type.equals("RECEIPT"))`
chains in six services.
**Recommendation.** `wb_movement_types (id, code, name, direction ENUM('IN','OUT','TRANSFER',
'STATUS_CHANGE','VALUE_ONLY'), affects_quantity, affects_value, requires_reason, requires_approval,
default_reason_code_id, reversal_movement_type_id, is_billable_event, gl_posting_rule_id, is_system,
is_active)`. Seed ~25 types in v1 (`RECEIPT_PO`, `RECEIPT_BLIND`, `RECEIPT_RETURN`, `PUTAWAY`,
`MOVE`, `PICK`, `SHIP`, `ADJUST_IN`, `ADJUST_OUT`, `COUNT_ADJ`, `STATUS_CHANGE`, `TRANSFER_SHIP`,
`TRANSFER_RECEIVE`, `SCRAP`, `KIT_ASSEMBLE`, `KIT_DISASSEMBLE`, `REPACK`, `OWNER_TRANSFER`,
`OPENING_BALANCE`, `REVERSAL`, …).
**Module.** `warehouse-base`. **Version.** **v1**.

### T-016 — BLOCKER — Inter-site transfer must be three legs with in-transit ownership, decided in v1
**Gap.** A single-row transfer (T-001) implies stock teleports: it leaves site A and arrives at site B in
the same instant.
**Why it matters.** Real transfers take days. During that time the stock exists, is owned by somebody,
is at risk to somebody, and is invisible if the model has no place for it. Shrinkage in transit is a
real and measured loss, and it can only be detected if the shipped quantity and the received quantity
are separately recorded. Every tier-1 does ship/receive as separate events. The *policy* decision —
does in-transit stock belong to the sending site, the receiving site, or a company-level in-transit
owner — changes valuation and branch reporting and must be taken in v1 because it determines which
`site_id` the in-transit ledger rows carry.
**Recommendation.** `wh_transfer_orders` + `wh_transfer_order_lines` with `qty_ordered, qty_shipped,
qty_received, qty_variance`. Three movements: `TRANSFER_SHIP` (from source location → `VIRT_IN_TRANSIT`
at the **sending** site — recommended, because the sender bears the risk until receipt), then
`TRANSFER_RECEIVE` (from in-transit → destination location at the receiving site), and an explicit
`TRANSIT_LOSS` adjustment with a reason code when they differ. Write the policy into the design set.
**Module.** `warehouse` (documents) + `warehouse-base` (ledger). **Version.** **v1.1**, with the
virtual location and the policy statement in **v1**.

### T-017 — BLOCKER — The ledger must be UPDATE-proof and DELETE-proof at the database level
**Gap.** The precedent has `is_active` and `deleted_at` soft-delete columns on inventory transactions
(`InventoryTransaction.java:136-138`) — i.e. movements can be retracted.
**Why it matters.** If a posted movement can be edited or soft-deleted, then every stock report is a
function of *when you ran it*, historical valuation is unreproducible, and the audit trail is
advisory. The accounting product in this same monorepo already took the opposite decision (three-layer
immutability with reversal-only correction) and the warehouse sub-ledger must match it or the two will
never reconcile.
**Recommendation.** A `BEFORE UPDATE OR DELETE` trigger on `wb_stock_ledger` that raises. Correction is
a new movement of type `REVERSAL` with `reversal_of_ledger_id` set and a mandatory reason code. No
`is_active`, no `deleted_at` on the ledger. The *header* (`wb_stock_movements`) may carry a
`status` including `CANCELLED`, but cancelling a posted movement writes reversal rows rather than
hiding the originals.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-018 — BLOCKER — Three timestamps, not one: `occurred_at`, `posted_at`, `created_at`
**Gap.** The precedent has a single `transaction_date` (`InventoryTransaction.java:51-52`).
**Why it matters.** Three different questions need three different answers. *When did the physical event
happen* (`occurred_at`) drives valuation period, shelf-life, dwell-time KPIs and backdated counts. *When
did the system learn about it* (`posted_at`) drives reconciliation with an offline RF sync or a nightly
adapter batch. *When was the row written* (`created_at`) is the audit fact. Collapsing them makes a
transaction recorded on Monday for a Friday event either falsify Friday's stock or falsify Monday's, and
you cannot choose. Multi-site multi-timezone (#388) makes it worse: "the 30th" is a different 24 hours
in each site.
**Recommendation.** All three, `TIMESTAMP WITH TIME ZONE`, on `wb_stock_ledger`. `wb_sites.timezone`
for local-day bucketing. A stated backdating policy: how far back, who may, and whether a closed stock
period blocks it (T-064).
**Module.** `warehouse-base`. **Version.** **v1**.

### T-019 — BLOCKER — Declare and test the reconstructibility invariant
**Gap.** Not a missing feature — a missing *guarantee*. Both the precedent tables (`accessory_stock_levels`
and `accessory_inventory_transactions`) exist, and nothing proves they agree.
**Why it matters.** A snapshot table is necessary for performance (nobody sums 10^8 rows to draw a
grid). But the moment the snapshot is authoritative rather than derived, the ledger becomes decorative
and the product loses the one property that distinguishes it from a spreadsheet: *any past balance can
be recomputed and defended*. Drift is not hypothetical; it is what happens the first time a service
throws between the ledger insert and the snapshot update.
**Recommendation.** (a) Both writes in one transaction, ledger first. (b) A scheduled
`StockReconciliationJob` that recomputes `wb_stock_on_hand` from `wb_stock_ledger` for a rolling window
and raises an alert on any difference, writing findings to `wb_reconciliation_exceptions`. (c) An
acceptance test in the design set: *"for a randomly chosen item, location and past instant, the
ledger-derived balance equals the snapshot as of that instant."* (d) A `GET /stock/as-at?at=…` API that
answers from the ledger, so the claim is exercised in production, not only in tests.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-020 — MAJOR — Item status is four independent facts, not one enum
**Gap.** A single `status` / `is_active` on the item.
**Why it matters.** "Blocked for receipt but still pickable" (running an item out), "pickable but not
orderable" (phase-out), "orderable but not yet receivable" (pre-launch) and "fully blocked" (recall) are
four operationally distinct states that every tier-1 expresses with independent flags. One enum forces
either a combinatorial explosion of values or a wrong answer.
**Recommendation.** `wb_items.is_receivable`, `is_issuable`, `is_orderable`, `is_countable` booleans plus
`lifecycle_status ENUM('NEW','ACTIVE','PHASE_OUT','OBSOLETE','BLOCKED')` for reporting.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-020a — MINOR — Archiving must write an opening-balance row, or reconstructibility dies at the archive boundary
**Gap.** Implied by T-019 at volume: eventually old ledger rows must leave the hot table.
**Why it matters.** If archiving simply deletes or moves rows, then "recompute the balance from the
ledger" stops working the day the first archive runs, silently.
**Recommendation.** Archiving is a *transaction*: for each surviving (site, location, item, owner,
status, lot, serial, lpn) tuple, write one `OPENING_BALANCE` movement dated at the archive cut-off, then
move the archived rows to `wb_stock_ledger_archive`. The invariant then holds against the hot table
alone. Design it in v1 even if it runs in v3.
**Module.** `warehouse-base`. **Version.** **v3** (design in **v1**).

## 2.2 Item master, UoM, identification (T-021 … T-032)

### T-021 — MAJOR — Supersession chains: absent from every tier-1, mandatory for our vertical
**Gap.** Part A is superseded by B, which is superseded by C. No tier-1 WMS models this — it lives in
automotive DMS and parts catalogues. Our primary verticals are a car dealer, a service workshop and a
parts business, so this is not an enhancement; it is why a dealer would choose us over Oracle WMS Cloud.
**Why it matters.** Without it: a pick for A shorts while C sits on the shelf; a count of A and C
disagrees with the catalogue; stock of a superseded part is invisible obsolescence; and a technician
orders C while the store has 40 of A. This is the single most common "why does your system not know
this" complaint in a parts warehouse.
**Recommendation.** `wb_item_supersessions (id, from_item_id, to_item_id, effective_from,
supersession_type ENUM('ONE_WAY','BIDIRECTIONAL','INTERCHANGEABLE'), qty_ratio NUMERIC(18,6),
notes, is_active)` with a resolver service that walks the chain to its terminal item, and cycle
detection at insert. Allocation consults it when the requested item is short (`allocation_rule`
`ALLOW_SUPERSESSION`). Reporting must show "stock of A including superseded equivalents" as a distinct
figure from "stock of A".
**Module.** `warehouse-base` (table + resolver) / `warehouse-adapter-dealer` (catalogue feed).
**Version.** **v1.1**.

### T-022 — MAJOR — Multiple barcodes per item, each with its own UoM
**Gap.** `accessory_products.barcode` is a single `VARCHAR(100)` (`Product.java:63-64`).
**Why it matters.** A case has a different barcode from an each. Scanning the case barcode must add 12,
not 1. Every tier-1 supports N barcodes per item with a UoM per barcode; without it, RF receiving of
cased goods is manual quantity entry, which is where miscounts come from. Suppliers also send the same
part with different EANs across regions.
**Recommendation.** `wb_item_barcodes (id, item_id, barcode, barcode_type ENUM('EAN13','UPC','GTIN14',
'CODE128','GS1_128','QR','INTERNAL'), uom_id, qty_per_scan NUMERIC(18,4) DEFAULT 1, is_primary,
is_active, UNIQUE(barcode))` — global uniqueness of the barcode string, because a scanner has no
context. Scan resolution is one indexed lookup returning item + UoM + quantity.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-023 — MAJOR — Vehicle fitment belongs in the adapter, not in `warehouse-base`
**Gap.** The precedent puts `vehicle_compatibility` on the product as JSONB (`Product.java:148-149`),
and there is an entire `accessory_vehicle_compatibility` table alongside it — two representations of
the same fact.
**Why it matters.** This is the generality question the four-module split exists to answer. If
`warehouse-base` learns about vehicles, it cannot serve `assets`, `field-service` or a future logistics
vertical. If the adapter owns it, base stays generic and the dealer vertical gets the depth it needs.
Getting this wrong in either direction is expensive: a vehicle column in base is a permanent smell, and
fitment scattered across three modules is a permanent data-quality problem.
**Recommendation.** `wa_dealer_item_fitment (item_id, model_id, variant_id, year_from, year_to,
position, notes)` in `warehouse-adapter-dealer`, referencing `automotive`'s existing model master.
`warehouse-base` knows only `wb_items`. The item grid in the dealer vertical joins; the base item grid
does not.
**Module.** `warehouse-adapter-dealer`. **Version.** **v1.1**.

### T-024 — MAJOR — A location generator screen, or nobody will ever key 4,000 bins
**Gap.** Location creation as a normal CRUD form.
**Why it matters.** A modest warehouse has 3,000–20,000 locations with a regular naming pattern
(`A-01-01-A` … `F-24-06-D`). Every tier-1 ships a generator. Without it, implementation is a
spreadsheet-and-import exercise for the customer, which is where go-lives slip and where location
barcodes end up inconsistent with the labels already stuck to the racking.
**Recommendation.** A "Generate locations" screen taking zone, aisle range, rack range, level range,
position range, a format mask (`{zone}-{aisle:02}-{rack:02}-{level}`), a location type and default
capacities, previewing the count and the first/last codes before committing. Plus CSV import on the
platform framework as the fallback.
**Module.** `warehouse`. **Version.** **v1**.

### T-025 — MAJOR — Negative-stock policy must be an explicit, configurable decision
**Gap.** Unstated. Systems that do not decide this default to whatever the first `if` statement did.
**Why it matters.** Allowing negative stock lets operations continue when paperwork lags, and destroys
valuation (what does a negative layer cost?). Blocking it stops the line when a receipt has not been
keyed. Every tier-1 makes it a setting, usually per site and overridable per item. It also interacts
with T-062: a negative balance has no cost layer to consume, so the costing policy must state what
happens.
**Recommendation.** `wb_sites.negative_stock_policy ENUM('BLOCK','WARN','ALLOW')` with
`wb_items.negative_stock_policy_override`. Default **BLOCK**. If `ALLOW`, the costing policy for the
negative consumption must be declared (recommend: last known unit cost, with a
`NEGATIVE_STOCK_COSTED` flag on the ledger row so it can be re-costed when the receipt lands).
**Module.** `warehouse-base`. **Version.** **v1**.

### T-026 — MINOR — Item unit cost does not belong on the item master
**Gap.** `accessory_products.base_cost_price` (`Product.java:109-110`) — a cost on the item.
**Why it matters.** Cost is a property of a *receipt layer*, not of an item. A cost column on the item
will inevitably be used by a report or an export, and it will disagree with the ledger. The only
legitimate item-level cost is a **standard cost** with an effective date, and that is a different
column with different semantics.
**Recommendation.** No cost on `wb_items`. If standard costing lands (v2),
`wb_item_standard_costs (item_id, site_id, cost, currency, effective_from, effective_to)`.
**Module.** `warehouse-base`. **Version.** **v1** (as an omission).

### T-027 — MINOR — Reorder point / min / max belong on item **×** site **×** location, not on the item
**Gap.** `accessory_products.min_stock_level / max_stock_level / reorder_point / reorder_quantity /
lead_time_days` are scalars on the product (`Product.java:119-133`).
**Why it matters.** A ten-branch dealer does not want the same reorder point at the flagship and the
satellite. Every tier-1 holds these at item-site minimum, and pick-face min/max at item-location.
**Recommendation.** `wb_item_sites (item_id, site_id, reorder_point, safety_stock, min_qty, max_qty,
reorder_qty, lead_time_days, abc_class, velocity_class, count_frequency_days, primary_location_id)` and
`wb_item_locations (item_id, location_id, min_qty, max_qty, replen_uom_id, is_fixed_pick_face)`.
**Module.** `warehouse-base`. **Version.** **v1** for `wb_item_sites`, **v1.1** for `wb_item_locations`.

### T-028 — MINOR — Shelf-life columns in v1 even though FEFO is v1.1
**Gap.** Expiry is on the movement as `expiry_date` in the precedent, not on the lot.
**Why it matters.** Once T-005 makes lot an entity, `expires_on` lives there. But `wb_items.shelf_life_days`,
`min_shelf_life_receipt_pct` and `min_shelf_life_ship_pct` should be present in v1 so the data is
being captured before the rules that consume it exist — otherwise FEFO in v1.1 has no history to work
with and every existing lot needs a manual expiry backfill.
**Module.** `warehouse-base`. **Version.** **v1 model-only**.

### T-029 — MINOR — Item deactivation must not orphan stock
**Gap.** Soft delete on the product with no check.
**Why it matters.** Deactivating an item that has on-hand stock creates inventory nobody can see or
transact — a classic source of "the count says 40 and the system says 0".
**Recommendation.** Block deactivation when `SUM(qty_on_hand) <> 0` for the item across all sites,
statuses and owners; offer "block for receipt/issue" (T-020) as the alternative.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-030 — MAJOR — Shelf-life enforcement points must be named, not assumed
**Gap.** "FEFO" is often specified as a single word. It is at least four separate rules.
**Why it matters.** (1) Refuse receipt of stock with less than X% shelf life remaining. (2) Allocate
earliest-expiry-first. (3) Refuse to ship stock with less than Y days remaining, sometimes per customer.
(4) Automatically move expired stock to an `EXPIRED` status by a scheduled job. Tier-1 products
implement all four separately. A design that says "FEFO" and implements only (2) will fail a food or
pharma demo on (1) and (3) and will fail an audit on (4).
**Recommendation.** Four named requirements, one scheduled job (`ExpiryStatusJob`), and a
`wb_customer_shelf_life_rules` table for (3) in v2.
**Module.** `warehouse`. **Version.** **v1.1** for (1)(2)(4), **v2** for (3).

### T-031 — MINOR — Kit/BOM must state whether the kit is stocked or virtual
**Gap.** "Kits" specified without the stocking question.
**Why it matters.** A *stocked* kit is assembled in advance and has its own on-hand and cost. A
*virtual/phantom* kit is exploded at allocation and never has stock. They need different item types,
different allocation behaviour and different valuation. Getting this wrong means a kit whose components
are picked but whose on-hand never moves, or vice versa.
**Recommendation.** `wb_items.item_type` includes both `KIT_STOCKED` and `KIT_PHANTOM`;
`wb_kits`/`wb_kit_components` with `component_qty`, `is_optional`, `substitute_group`, `scrap_pct`.
**Module.** `warehouse-base`. **Version.** **v1.1**.

### T-032 — MINOR — GS1 AI parsing is one utility, and it should be written once
**Gap.** Barcode scanning usually gets implemented as "read the string".
**Why it matters.** A GS1-128 label carries GTIN (01), batch (10), expiry (17), serial (21) and SSCC
(00) in one scan. Parsing it is the difference between one scan and four keystrokes at every receipt.
Every tier-1 does it. It is also the sort of helper that gets written three times in three modules if
not placed deliberately — the codebase's own `/preflight-check` rule exists for exactly this.
**Recommendation.** One parser in `warehouse-base` returning a typed result; consumed by the web pack
station and the mobile RF screens alike.
**Module.** `warehouse-base`. **Version.** **v1.1**.

## 2.3 Inbound (T-033 … T-040)

### T-033 — MAJOR — A generic inbound movement port must be idempotent and typed, or every adapter reinvents it
**Gap.** The brief names "a generic inbound movement port" in `warehouse-base` without stating its
contract.
**Why it matters.** Five adapters will call it. If it accepts a loose payload, each adapter will
develop its own dialect and the port becomes five ports. If it is not idempotent, a retried adapter
call double-receives stock — the single most common integration defect in this class of product, and
one this codebase has already met in a different form (`reference_import_validateapi_persisting_endpoint`).
**Recommendation.** One endpoint, `POST /api/warehouse/movements`, taking
`{source_system, source_ref, source_ref_line, idempotency_key, movement_type_code, occurred_at, lines[]}`
where each line carries item identification (id **or** sku **or** barcode), from/to location, owner,
status, lot, serial, LPN, `qty_entered` + `uom_code`, reason code and reference document. Persist the
request in `wb_inbound_messages` before processing. `UNIQUE(source_system, idempotency_key)` returns the
original result on replay, 200 not 409. Validate against `wb_movement_types` and reject unknown types
rather than silently defaulting.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-034 — MAJOR — Blind receipt must be a first-class v1 flow, not a fallback
**Gap.** Receiving usually gets designed as "receive against a PO".
**Why it matters.** Three of our own scenarios have no PO at the moment of receipt: a 3PL client's goods
arriving, a customer return, and a workshop's over-the-counter purchase. Every tier-1 supports blind
receipt. If v1 only receives against a PO, the first pilot customer will key fake POs, and fake POs
become permanent.
**Recommendation.** `wh_receipts` with `receipt_type ENUM('AGAINST_PO','AGAINST_ASN','BLIND','RETURN',
'TRANSFER_IN')`, PO reference nullable. Blind receipt requires item, qty, UoM, owner, status and
location, nothing else.
**Module.** `warehouse`. **Version.** **v1**.

### T-035 — MAJOR — Receipt must be able to land in a non-available status
**Gap.** Implicit "receive → available".
**Why it matters.** QC hold on receipt, damaged-on-arrival, and un-graded returns all need to land as
on-hand-but-not-allocatable on the *first* transaction. If v1 hardcodes `AVAILABLE`, then every
quarantine flow in v1.1 is a second transaction that briefly exposes the stock to allocation — a real
defect, not a cosmetic one, because a wave released in that window will pick quarantined goods.
**Recommendation.** `stock_status_id` is an input on the receive screen, defaulted from
`wb_items.default_receipt_status_id` → `wb_suppliers.default_receipt_status_id` → `AVAILABLE`.
**Module.** `warehouse`. **Version.** **v1**.

### T-036 — MAJOR — Over-receipt and short-receipt policy, or the PO line never closes
**Gap.** Unstated tolerance handling.
**Why it matters.** Suppliers over-ship and under-ship. Without a tolerance and a close-short action,
PO lines accumulate forever and the "open PO" report becomes meaningless within a quarter, which then
breaks reorder suggestions (T-084).
**Recommendation.** `wb_items.over_receipt_tolerance_pct` and a site default;
`wh_purchase_order_lines.qty_ordered / qty_received / qty_cancelled / line_status`; a "close short"
action with a reason code.
**Module.** `warehouse`. **Version.** **v1.1**.

### T-037 — MAJOR — Putaway rules must be data, not code
**Gap.** Putaway typically gets built as "pick a location from a dropdown" in v1 and "add rules" in v2 —
which means rewriting the receiving service.
**Why it matters.** Directed putaway is the capability that separates a WMS from a stock ledger; all six
matrix products have rule-driven putaway. The cheap v1 move is to build the *evaluation* against a rules
table that initially contains one rule ("suggest the item's fixed location, else any location with
capacity in the default zone").
**Recommendation.** `wb_putaway_rules (id, site_id, sequence, item_filter…, criteria columns,
strategy ENUM('FIXED_LOCATION','NEAREST_EMPTY','CONSOLIDATE_SAME_LOT','ZONE_BY_VELOCITY','BULK_RESERVE'),
zone_id, is_active)` evaluated in sequence, returning a suggested location the operator can override
with a reason.
**Module.** `warehouse`. **Version.** **v1.1** (evaluation harness in **v1**).

### T-038 — MINOR — Receipt reversal must be an action, not a data fix
**Gap.** Un-receiving is often left to support.
**Why it matters.** Mis-keyed receipts happen daily. If the only remedy is an adjustment, the PO line's
received quantity is now wrong forever and the accounting hand-off double-counts.
**Recommendation.** A "reverse receipt" action generating a `REVERSAL` movement linked by
`reversal_of_ledger_id`, decrementing `qty_received` on the PO line, blocked once the stock has moved
on (then it is an adjustment, correctly).
**Module.** `warehouse`. **Version.** **v1**.

### T-039 — MINOR — Cross-dock needs a flag on the receipt line in v1 even though cross-dock is v2
**Gap.** No hook.
**Why it matters.** Opportunistic cross-dock (received stock matches an open allocation → route it to
shipping instead of putaway) is a v2 feature, but knowing *which* receipts were cross-docked is a KPI
from day one, and retrofitting the flag means the history is blank.
**Recommendation.** `wh_receipt_lines.cross_dock_allocation_id` nullable in v1.
**Module.** `warehouse`. **Version.** **v1 model-only**.

### T-040 — MINOR — Supplier is a dimension the warehouse needs, and it lives in another module
**Gap.** Suppliers exist in the dealer/accessories verticals, not in `warehouse-base`.
**Why it matters.** Receipt quality, lot traceability backwards, supplier hold rules and RTV all key on
supplier. Base cannot depend on a vertical.
**Recommendation.** `wb_trading_partners (id, partner_type ENUM('SUPPLIER','CUSTOMER','CARRIER',
'INTERNAL'), code, name, external_ref, source_module)` in base, populated by adapters — the same
pattern the accounting modules already use for parties. Do **not** FK into `dealer` or `accessories`.
**Module.** `warehouse-base`. **Version.** **v1**.

## 2.4 Tasks, outbound and allocation (T-041 … T-050)

### T-041 — BLOCKER — `wb_tasks` must exist in v1, even if v1 has no RF device
**Gap.** The brief places "the advanced execution layer" in `warehouse` without saying when the task
object appears.
**Why it matters.** This is the second-deepest structural decision after the ledger. Every tier-1 WMS
separates the *business document* from the *execution instruction*: SAP EWM's warehouse task and
warehouse order (with warehouse-order-creation rules deciding how tasks bundle into work); Manhattan,
Blue Yonder, Oracle and Körber all have task engines. If v1's receiving screen writes the ledger
directly and v1's pick screen writes the ledger directly, then **RF, task assignment, interleaving,
labour measurement, exception queues, wave release and automation are each a rewrite of inbound and
outbound**, not a new consumer of an existing table. Building `wb_tasks` in v1 with a single
synchronous consumer costs perhaps a week; retrofitting it costs the execution layer twice.
**Recommendation.** `wb_tasks (id, site_id, task_type_id, status ENUM('CREATED','ASSIGNED',
'IN_PROGRESS','COMPLETED','SHORT','CANCELLED'), priority SMALLINT, zone_id, from_location_id,
to_location_id, item_id, lot_id, serial_id, lpn_id, owner_id, stock_status_id, qty_requested,
qty_completed, uom_id, demand_type, demand_id, demand_line_id, allocation_id, wave_id, assigned_to_user_id,
assigned_at, started_at, completed_at, exception_code_id, device_id, ledger_movement_id, version)` plus
`wb_task_types` and `wb_work_units` (the bundle — EWM's warehouse order, Manhattan's task group). v1
creates one task per receipt line and per pick line, and completes it in the same request. The screens
change in v1.1; the model does not.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-042 — MAJOR — One demand model for all demand types, not one table per source
**Gap.** The natural build is `wh_sales_orders`, then `wh_transfer_orders`, then `wh_work_orders`, each
with its own allocation and picking code.
**Why it matters.** Allocation, waving, picking, packing and shipping are identical regardless of why
the stock is leaving. Tier-1 products normalise this (EWM's outbound delivery order; Manhattan's and
Oracle's order object with a type). Three parallel implementations means three places to fix every
allocation bug and three sets of KPIs that do not add up.
**Recommendation.** `wh_demand_headers (id, demand_type ENUM('SALES','TRANSFER','WORK_ORDER',
'REPLENISHMENT','VAS','SAMPLE','SCRAP'), demand_number, site_id, owner_id, partner_id, priority,
required_by, ship_by, status, source_system, source_ref)` + `wh_demand_lines`. The document-specific
extras (job card id, sales order id) live in adapter tables keyed to `demand_header_id`.
**Module.** `warehouse`. **Version.** **v1**.

### T-043 — BLOCKER — Allocation strategy must be a configured value, not an if-statement
**Gap.** v1 will ship one strategy. The risk is that it ships as code.
**Why it matters.** FIFO, FEFO, LIFO, lot-specific, location-priority, owner-specific and
minimum-shelf-life are all the *same algorithm with a different ORDER BY and filter*. Every tier-1
exposes them as configuration (EWM stock removal strategies, Manhattan/Oracle allocation rules). If v1
hardcodes FIFO, v1.1's FEFO is a branch in the allocator, v2's lot-specific is another, and by v2 the
allocator is untestable.
**Recommendation.** `wb_allocation_strategies (id, code, name, order_by_expression_key,
respects_shelf_life, allows_partial, allows_substitution, allows_cross_status, is_active)` and
`wb_allocation_rules (id, site_id, sequence, item_filter, owner_filter, customer_filter,
demand_type_filter, strategy_id, is_active)`. The allocator resolves a rule → a strategy → a
whitelisted ordering clause (the same `SqlSortBuilder`-style whitelist discipline the codebase already
mandates, for the same injection reason). v1 seeds `FIFO_BY_RECEIPT` and `FIXED_LOCATION_FIRST`.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-044 — MAJOR — Wave is a real object and its absence in v1 must be a stated deferral, not silence
**Gap.** Waves are v1.1 in my verdicts, which is defensible — but the *release* step must exist in v1.
**Why it matters.** "Release" is the moment soft allocation becomes hard allocation and tasks are
created. If v1 has no release step, every order is hard-allocated at creation, which means a
cancelled order's stock stays locked and a shortage on one order blocks another. Tier-1 products all
have the two-phase model.
**Recommendation.** v1: an explicit "Release" action on the demand header, creating hard allocations and
tasks. v1.1: `wh_waves` groups releases, and the same action operates on N orders.
**Module.** `warehouse`. **Version.** **v1** (release) / **v1.1** (wave).

### T-045 — MAJOR — Short pick must be a first-class outcome with an exception code
**Gap.** Picking is usually specified as "confirm the pick".
**Why it matters.** The interesting case is when the stock is not there. Every tier-1 has short-pick
handling: record the shortfall, choose re-allocate / emergency replenish / short the line, and — most
importantly — **trigger a count of that location**, because a short pick is the highest-quality signal
of an inventory error that a warehouse ever gets. Systems that silently reduce the pick quantity
destroy that signal.
**Recommendation.** `wb_task_exception_codes` seeded with `SHORT_NOT_FOUND`, `SHORT_DAMAGED`,
`SHORT_WRONG_ITEM`, `LOCATION_BLOCKED`, `LOT_EXPIRED`. A short pick sets task status `SHORT`, releases
the unmet allocation, and auto-creates a cycle-count task for the location (a switch on the site).
**Module.** `warehouse`. **Version.** **v1.1**.

### T-046 — MAJOR — Ship confirm is the inventory-relief event and must be atomic with the allocation close
**Gap.** Unstated ordering between "pick complete", "pack", "ship" and "stock leaves".
**Why it matters.** If stock is relieved at pick, then picked-not-shipped goods vanish from on-hand
while physically present, and a count of the staging lane disagrees. If relieved at ship, staging must
be a real location (T-008/T-009) holding stock in a `STAGED` or `ALLOCATED` status. Tier-1 products all
move stock to a staging/shipping location on pick and relieve at goods issue. Choosing late means
choosing twice.
**Recommendation.** Pick = move from pick location → staging location (a real, countable location).
Ship confirm = move from staging → `VIRT_CUSTOMER`, closing the allocation, in one transaction. State
it in the design set as the shipping model.
**Module.** `warehouse`. **Version.** **v1**.

### T-047 — MINOR — Backorder policy must be stated per demand type
**Gap.** Partial allocation with no stated policy.
**Why it matters.** Ship-complete-only, ship-partial-and-backorder, and ship-partial-and-cancel-rest are
three different customer promises. Warehouses that guess get it wrong on the orders that matter.
**Recommendation.** `wh_demand_headers.fulfilment_policy ENUM('SHIP_COMPLETE','SHIP_PARTIAL_BACKORDER',
'SHIP_PARTIAL_CANCEL')`, defaulted per partner.
**Module.** `warehouse`. **Version.** **v1.1**.

### T-048 — MINOR — Allocation audit: record *why* this stock was chosen
**Gap.** Allocation decisions are usually invisible after the fact.
**Why it matters.** "Why did the system pick lot B when lot A expires sooner" is asked weekly, and
without the rule id and strategy id on the allocation row the answer is a code reading exercise.
**Recommendation.** `wb_allocations.allocation_rule_id` and `strategy_id`, shown on the allocation
detail view.
**Module.** `warehouse-base`. **Version.** **v1.1**.

### T-049 — MINOR — De-allocation on cancel must be deterministic and reason-coded
**Gap.** Follows from T-014; worth calling out separately because it is the acceptance test.
**Recommendation.** Cancelling a demand line sets every open allocation for it to `RELEASED` with
`release_reason_code_id`, decrements the on-hand cache, and cancels any un-started tasks. Acceptance
test: allocate 10, cancel, assert `qty_available` returns to its pre-allocation value exactly.
**Module.** `warehouse`. **Version.** **v1**.

### T-050 — MINOR — Pick confirmation must validate the scan, not trust the operator
**Gap.** "Confirm pick" as a button.
**Why it matters.** Scan validation of location, then item, then lot/serial, then quantity is what
produces pick accuracy above 99.9%. A confirm button produces about 98%, and the difference is the
entire business case for a WMS.
**Recommendation.** `wb_task_types.requires_location_scan / requires_item_scan / requires_lot_scan /
requires_serial_scan / requires_qty_entry` as configuration per task type, honoured identically by web
and mobile.
**Module.** `warehouse`. **Version.** **v1.1**.

## 2.5 Execution layer, RF and mobile (T-051 … T-059)

### T-051 — BLOCKER — There is no mobile counterpart planned, and in this codebase that is a hard rule
**Gap.** The brief describes an "advanced execution layer" in `warehouse` but says nothing about
`mobile/`. CLAUDE.md Principle #3 makes web↔mobile mirroring **mandatory**, and the memory hub
(`reference_mobile_hub`) says almost every user-visible pattern has a mobile counterpart.
**Why it matters.** A WMS without a handheld is not a WMS — it is a stock ledger with a web form. Every
one of the six matrix products is RF-first; the *warehouse* screens are the RF screens and the web
screens are for supervisors. Deciding this late produces a web-shaped design (wide grids, modals,
multi-field forms) that cannot be re-expressed on a 4-inch screen held in one hand by someone wearing
a glove.
**Recommendation.** Name the mobile screens in the design set at the same time as the web ones:
`ReceiveScreen`, `PutawayScreen`, `MoveScreen`, `PickScreen`, `PackScreen`, `ShipScreen`,
`CycleCountScreen`, `StockEnquiryScreen`, `TaskListScreen`. They are all consumers of `wb_tasks`
(T-041), which is why T-041 is a blocker. Note the module's known constraints
(`EntityListScreen` supports dropdown filters only; APIs are object literals) — the RF screens are not
`EntityListScreen` screens and should not try to be.
**Module.** `mobile/` + `warehouse`. **Version.** **v1.1** for the first four screens; **v1** for the
decision and the task model.

### T-052 — MAJOR — RF screens need a different interaction contract from web screens
**Gap.** Not stated.
**Why it matters.** RF flows are: one field visible, scan advances, no mouse, no scrolling, errors
spoken/vibrated, and every screen resumable after a dropped connection. Designing them as mobile
versions of web forms is the standard failure. Oracle WMS Cloud and Körber make RF flow configuration a
headline feature precisely because the interaction is so specific.
**Recommendation.** Write the RF interaction rules into the design set as constraints (single active
input, scan-to-advance, no free-text where a scan exists, a persistent "current task" banner, an
always-available "report exception" action).
**Module.** `mobile/`. **Version.** **v1.1**.

### T-053 — MAJOR — Offline behaviour must be decided in v1, even if the answer is "online only"
**Gap.** Unstated.
**Why it matters.** Warehouses have dead zones — cold stores, mezzanines, steel racking. "Online only"
is a legitimate v1 answer and several tier-1 SaaS products are effectively that, but it must be a
*stated* answer, because the alternative (queued offline transactions) changes the API contract:
every transaction needs a client-generated id, an `occurred_at` from the device, and a server-side
conflict policy. Adding that later means re-versioning every RF endpoint.
**Recommendation.** State "online-only in v1". Even so, put `client_txn_id UUID` and a device-supplied
`occurred_at` in the movement API from v1 (they cost nothing and they are the offline hooks), and
reject duplicates on `client_txn_id`.
**Module.** `warehouse-base` + `mobile/`. **Version.** **v1** (decision + hooks), **v3** (offline).

### T-054 — MAJOR — Label printing is infrastructure and needs an owner
**Gap.** Not mentioned in the brief.
**Why it matters.** Receiving without an LPN label, and picking without a carton label, are manual
processes. Every tier-1 ships label templates and a print service with printer groups per zone. This is
also a genuinely awkward piece of infrastructure in a browser-based product (network printers, ZPL,
printer selection per station) and it will be discovered late if it is not named early.
**Recommendation.** `wb_label_templates (code, name, format ENUM('ZPL','PDF','HTML'), body,
applies_to)`, `wb_printers (site_id, zone_id, code, name, connection_type, address)`,
`wb_print_jobs` for the audit trail and reprints. A reprint action on every labelled object.
**Module.** `warehouse-base`. **Version.** **v1.1**.

### T-055 — MINOR — Task assignment model must distinguish pull from push
**Gap.** Unstated.
**Why it matters.** "Operator asks for the next task" (pull) and "supervisor assigns a queue to an
operator" (push) are both used, often in the same warehouse. Building only one and adding the other
later means changing the task lifecycle.
**Recommendation.** `wb_tasks.assigned_to_user_id` nullable plus a `GET /tasks/next` endpoint honouring
zone, task type and equipment capability. Both modes from the same table.
**Module.** `warehouse`. **Version.** **v1.1**.

### T-056 — MINOR — Equipment / resource type is a dimension of a task
**Gap.** No resource model.
**Why it matters.** A pallet in a high rack needs a reach truck; a case pick needs a trolley. Tier-1
products model resource types and qualifications (EWM resources; Manhattan and Blue Yonder equipment
classes). Without it, task assignment sends the wrong person and interleaving is impossible.
**Recommendation.** `wb_resource_types`, `wb_user_qualifications`, and
`wb_task_types.required_resource_type_id`. Column in v1.1, behaviour in v2.
**Module.** `warehouse`. **Version.** **v2** (columns **v1.1**).

### T-057 — MINOR — A supervisor exception console is the v1.1 screen that makes the product usable
**Gap.** Not named.
**Why it matters.** Every exception — short pick, failed scan, capacity breach, count variance, blocked
location — needs somewhere to go. Without a console they go to a phone call.
**Recommendation.** One grid over `wb_tasks WHERE status IN ('SHORT') OR exception_code_id IS NOT NULL`
plus `wb_reconciliation_exceptions` (T-019) and `wb_inbound_messages` errors (T-091), with actions.
**Module.** `warehouse`. **Version.** **v1.1**.

### T-058 — MINOR — Task duration must be captured from v1 even though labour management is v2
**Gap.** Without `started_at`/`completed_at` on the task there is no productivity data.
**Why it matters.** Labour reporting in v2 needs history. If v1 does not stamp the timestamps, v2 starts
with an empty baseline and the first "are we faster than last quarter" question cannot be answered for
a year.
**Recommendation.** `started_at`, `completed_at`, `assigned_at`, `device_id`, `travel_distance` nullable
on `wb_tasks` from v1.
**Module.** `warehouse-base`. **Version.** **v1 model-only**.

### T-059 — MINOR — Automation integration should be an event contract, not a protocol
**Gap.** The brief mentions robotics/AS-RS/conveyor interfaces.
**Why it matters.** SAP EWM MFS talks PLC telegrams; that is a decade of work and we should not do it
(§4). But we should not close the door either: an AMR vendor integrating against a documented task
event stream is a two-week integration for *them*.
**Recommendation.** Publish `task.created`, `task.assigned`, `task.completed`, `stock.changed` events
with a stable schema; accept task completion through the same idempotent movement port (T-033). No
protocol-level automation in our codebase.
**Module.** `warehouse-base`. **Version.** **v3** (contract stated in **v1.1**).

## 2.6 Valuation and the finance interface (T-060 … T-070)

### T-060 — BLOCKER — Decide, in writing, whether the WMS owns inventory value
**Gap.** The brief lists "valuation" as a `warehouse` capability without stating the boundary against
the accounting product being built alongside.
**Why it matters.** The tier-1 consensus is unambiguous and it is the opposite of the brief: **SAP EWM
holds no value**, Manhattan holds no value, Blue Yonder holds no value, Körber holds no value, Oracle
*WMS Cloud* holds no value — value lives in the ERP (S/4 MM/FI + Material Ledger, Oracle Cost
Management). They are quantity engines. The reason is that inventory value is an accounting sub-ledger:
it needs periods, close, revaluation, GL reconciliation and audit, and building half of that inside a
WMS produces a number that disagrees with the books.
Our situation genuinely differs — our buyer is an SMB dealer or workshop who has no ERP, and the
accounting product is a sibling module rather than a third-party system. So "we hold value" is
defensible. But it must be a **decision with consequences accepted**, not a bullet on a feature list.
The unacceptable outcome is value in both products, computed differently.
**Recommendation.** Write the boundary into the design set as a numbered decision. Recommended split:
`warehouse-base` owns **cost layers and quantity-derived value**; the accounting product owns the
**GL**; the warehouse **publishes** valued movements and never writes journals itself (T-067). Where
the accounting module is not installed, the warehouse's valuation reports stand alone.
**Module.** `warehouse-base` ↔ `accounting`. **Version.** **v1** (the decision).

### T-061 — BLOCKER — Cost layers, not a cost column on the balance
**Gap.** `accessory_stock_levels.average_cost` and `last_cost` (`StockLevel.java:81-85`).
**Why it matters.** A cost column on a balance cannot produce FIFO (no layers), cannot produce specific
identification (no per-unit cost), cannot be revalued without destroying history, cannot be reconciled
to a GL, and cannot answer "what did the stock we shipped last March cost". Moving-average as a column
also silently breaks on negative stock and on backdated receipts.
**Recommendation.** `wb_cost_layers (id, item_id, site_id, owner_id, lot_id NULL, serial_id NULL,
receipt_ledger_id, layer_date, qty_received, qty_remaining, unit_cost, landed_cost_adjustment,
currency_code, exchange_rate, is_open, closed_at)` and `wb_cost_consumptions (id, layer_id,
issue_ledger_id, qty, unit_cost, value)`. Issues consume layers per the costing policy; the ledger row
carries `cost_layer_id` where a single layer applies and the consumption rows carry the rest. WAC is
then a *reporting* function over layers, not a stored number, so switching methods does not require a
different schema.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-062 — BLOCKER — The valuation grain is a v1 decision and it restates history if changed
**Gap.** Unstated.
**Why it matters.** Is a unit's cost the same across all sites (company-level valuation) or per site
(site-level)? SAP calls this the valuation area and it is a foundational configuration precisely because
changing it restates every balance. Site-level makes inter-site transfers a valuation event (with
possible profit-in-stock elimination); company-level makes them free but hides site-level performance.
Adding `owner_id` (T-002) adds a third axis: a 3PL client's goods are valued at *their* cost or not at
all.
**Recommendation.** State the grain as `(owner_id, item_id, site_id)` — recommended, because our buyers
are multi-branch and branch P&L matters to them — and make `wb_cost_layers` unique-ish on that tuple.
Write the inter-site transfer valuation rule at the same time (recommend: transfer at sending site's
cost, no margin, so there is no profit in stock to eliminate).
**Module.** `warehouse-base`. **Version.** **v1**.

### T-063 — MAJOR — Landed cost requires layers that can be adjusted after the fact
**Gap.** Landed cost is v2 in my verdicts, but the hook is v1.
**Why it matters.** The freight invoice arrives three weeks after the goods. If a cost layer is
immutable, the adjustment has nowhere to go; if the layer is mutable, history is unstable. Tier-1
practice is a separate cost-adjustment document that adds value to the layer and to any already-consumed
quantity.
**Recommendation.** `wb_cost_layers.landed_cost_adjustment` (v1, always zero) plus a v2
`wb_cost_adjustments` document that apportions a cost across layers by value/weight/volume/qty and
writes a `VALUE_ONLY` movement (T-015's `affects_quantity = false`) for the portion already consumed.
**Module.** `warehouse-base`. **Version.** **v2** (column in **v1**).

### T-064 — MAJOR — Stock periods with a close, or valuation reports change after they are signed
**Gap.** Unstated.
**Why it matters.** If a backdated movement can land in a month whose stock valuation has been reported,
the report is not reproducible and the auditor's copy no longer matches the system. The accounting
sibling already has periods and close; the warehouse must have a compatible concept or the two will
never agree at a period boundary.
**Recommendation.** `wb_stock_periods (site_id, period_start, period_end, status ENUM('OPEN',
'SOFT_CLOSED','HARD_CLOSED'), closed_by, closed_at)`. Soft close warns; hard close blocks any movement
with `occurred_at` inside the period. Reopen with a reason and an audit row. Align period boundaries
with the accounting module's.
**Module.** `warehouse-base`. **Version.** **v1 model-only**, enforced in **v1.1**.

### T-065 — MAJOR — GL posting rules must be data keyed on movement type × reason code
**Gap.** Unstated.
**Why it matters.** SAP's whole design is that the movement type carries the account determination. If
posting is code, then adding a reason code becomes a backend release, and every vertical will want its
own.
**Recommendation.** `wb_posting_rules (id, movement_type_id, reason_code_id NULL, item_group_id NULL,
site_id NULL, owner_type NULL, debit_account_code, credit_account_code, is_active, effective_from)`
resolved most-specific-first. The output is a posting *instruction*, handed to accounting (T-067).
**Module.** `warehouse-base`. **Version.** **v1** (table) / **v1.1** (used).

### T-066 — MAJOR — The stock-to-GL reconciliation report is the one an auditor asks for
**Gap.** Not usually specified until an audit.
**Why it matters.** "Closing stock value per the warehouse = the inventory control account balance per
the GL" is the single report that makes a finance director trust the system. It is also the report that
finds every integration defect.
**Recommendation.** One report: opening value + receipts + adjustments + revaluations − issues =
closing value, per site/owner/item group, with a column for the GL control account balance and a
variance column that drills to the offending movements.
**Module.** `warehouse` ↔ `accounting`. **Version.** **v1.1**.

### T-067 — MAJOR — Publish valued movements; do not write journals from the warehouse
**Gap.** The temptation is a direct insert into the accounting journal tables.
**Why it matters.** The accounting product has its own posting rules, immutability triggers, period
locks, numbering and approval. A foreign module writing into its journal defeats all of them, and the
two modules become undeployable independently — which contradicts the whole four-module rationale.
**Recommendation.** The warehouse writes `wb_posting_events` (movement, rule, debit, credit, amount,
status) and the accounting adapter consumes them idempotently, exactly as the existing
`accounting-adapter-dealer` pattern does for its vertical. Failures land in a retryable queue, not in
a swallowed exception.
**Module.** `warehouse-base` + a new `accounting-adapter-warehouse` (or an existing adapter).
**Version.** **v1.1**.

### T-068 — MINOR — LIFO must be explicitly refused, not silently omitted
**Gap.** LIFO is in the brief's list of costing methods.
**Why it matters.** LIFO is not permitted under Ind AS 2 / IAS 2. Offering it invites a customer to
produce non-compliant accounts. Tier-1 products that offer it do so for specific jurisdictions.
**Recommendation.** State the refusal and the reason in the design set. (§4.)
**Module.** — **Version.** **NO**.

### T-069 — MINOR — Opening balance is a movement, not a column
**Gap.** Go-live stock loading is usually treated as "import the on-hand table".
**Why it matters.** If opening stock is written directly to the balance table, the ledger does not
explain it, T-019's invariant fails on day one, and there is no cost layer for the opening stock, so the
first issue has no cost.
**Recommendation.** Go-live import writes `OPENING_BALANCE` movements from `VIRT_OPENING_BALANCE`, with
unit costs, creating cost layers. On the platform's existing import framework, with a dry run.
**Module.** `warehouse`. **Version.** **v1**.

### T-070 — MINOR — Currency on the cost layer, even in a single-currency v1
**Gap.** —
**Why it matters.** Imported spares are bought in USD/EUR. A layer without `currency_code` and
`exchange_rate` cannot ever record what was actually paid, and adding them later leaves history in an
assumed currency.
**Recommendation.** `currency_code CHAR(3) NOT NULL` and `exchange_rate NUMERIC(18,6) NOT NULL DEFAULT 1`
on `wb_cost_layers` from v1, defaulted to the install's base currency.
**Module.** `warehouse-base`. **Version.** **v1**.

## 2.7 Multi-owner and 3PL (T-071 … T-078)

### T-071 — MAJOR — Billable events must be flagged on the ledger from v1, or 3PL billing has no history
**Gap.** `warehouse-3pl` billing is v2, but billing is computed from *past* activity.
**Why it matters.** Activity-based billing charges per receipt line, per pick, per pallet-day stored.
If the ledger and task tables do not mark which events were billable and to whom, the first billing run
can only charge from its own start date, and any dispute about last month is unanswerable. Manhattan,
Blue Yonder, Körber and Infor all built 3PL billing on top of their transaction history for exactly
this reason.
**Recommendation.** `wb_movement_types.is_billable_event` (T-015) and `wb_tasks.is_billable`, plus
`owner_id` everywhere (T-002). The v2 billing engine then reads history rather than starting a new one.
**Module.** `warehouse-base`. **Version.** **v1 model-only**.

### T-072 — MAJOR — Storage billing needs a daily inventory snapshot, and snapshots must start early
**Gap.** Storage charges are per pallet-day or per sqft-day.
**Why it matters.** You cannot reconstruct "how many pallet positions did client X occupy on the 14th"
from a movement ledger cheaply at scale — and if you can (T-019), you still want it materialised.
Starting the snapshot in v2 means no billing history.
**Recommendation.** `wb_daily_stock_snapshots (snapshot_date, site_id, owner_id, item_id, location_id,
qty, lpn_count, volume, weight)` written by a nightly job from **v1**. It doubles as the ageing and
days-on-hand source, so it earns its keep before 3PL exists.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-073 — MAJOR — Owner segregation must be enforced at the row level, not only in the UI
**Gap.** Multi-client data separation is usually specified as menu/permission scoping.
**Why it matters.** A 3PL client seeing another client's stock is a contract breach, not a bug. The
codebase's own memory notes the same class of problem for branch scope
(`reference_branch_scope_record_level_guard`): a UI filter is not a guard.
**Recommendation.** A repository-level owner predicate applied in the query layer for every
`wb_stock_*` read when the user's role is client-scoped, plus `w3_client_users` mapping. Tested with a
negative test per endpoint.
**Module.** `warehouse-3pl`. **Version.** **v2** (guard designed in **v1**).

### T-074 — MINOR — Mixed-owner rules belong on the location
**Gap.** —
**Why it matters.** Most 3PLs forbid two clients' goods in one location and always forbid them in one
LPN. This is a location and LPN attribute, not a policy in code.
**Recommendation.** `wb_locations.allow_mixed_owner` (T-008) and `wb_lpns` single-owner constraint.
**Module.** `warehouse-base`. **Version.** **v1** (column) / **v2** (enforced).

### T-075 — MINOR — Client rate cards need effective dating from the first version
**Gap.** —
**Why it matters.** Rates change mid-contract and old invoices must remain reproducible.
**Recommendation.** `w3_rate_cards` + `w3_rate_card_lines (charge_code, uom, rate, min_charge,
tier_from, tier_to, effective_from, effective_to)`. Never update a rate; supersede it.
**Module.** `warehouse-3pl`. **Version.** **v2**.

### T-076 — MINOR — Client portal should reuse the platform's public/no-login foundation
**Gap.** —
**Why it matters.** A second authentication surface is a security liability and duplicated work; the
platform already has a public-page foundation (`project_public_nologin_foundation`).
**Module.** `warehouse-3pl`. **Version.** **v2**.

### T-077 — MINOR — Consignment and VMI are the same model as 3PL, and should be built once
**Gap.** They appear in different capability areas (#117, #141, #314) and will otherwise be built twice.
**Why it matters.** Supplier-consigned stock in our warehouse, our stock in a customer's premises, and a
3PL client's stock in our warehouse are all "on hand, owned by someone else" with an ownership-transfer
event on consumption. One model, three configurations.
**Recommendation.** `wb_owners.owner_type` (T-002) covers all three; the ownership transfer is a
`OWNER_TRANSFER` movement type. Say so explicitly in the design set so it is not built three times.
**Module.** `warehouse-base`. **Version.** **v2**.

### T-078 — MINOR — Storage-billing charges must hand off to accounting, not invoice independently
**Gap.** —
**Why it matters.** A second invoice numbering series and a second AR ledger is exactly the fragmentation
the accounting product exists to prevent.
**Recommendation.** `warehouse-3pl` produces charge lines; the accounting module raises the invoice.
**Module.** `warehouse-3pl` ↔ `accounting`. **Version.** **v2**.

## 2.8 Our verticals, adapters and statutory reality (T-079 … T-088)

### T-079 — BLOCKER — The adapter contract must be defined before the first adapter is written
**Gap.** The brief names five adapters (dealer, services, field-service, assets, future logistics) but
no contract.
**Why it matters.** The generality question is the whole reason for the four-module split, and it is
decided by the *first* adapter. If `warehouse-adapter-dealer` is allowed to call `warehouse-base`
services directly, reach into `wb_` tables, or add columns to base tables, the split is cosmetic and the
second adapter will copy the first. This is the same failure mode the accounting set had to be
protected from.
**Recommendation.** State the contract as: adapters may (a) call the movement port (T-033), (b) call
read APIs, (c) subscribe to events, (d) own their **own** tables prefixed `wa_<vertical>_`, and
(e) contribute reference data through documented endpoints. Adapters may **not** write to `wb_` or
`wh_` tables, add columns to them, or bypass the port. Put an architecture test in the design set.
**Module.** all. **Version.** **v1**.

### T-080 — MAJOR — Van stock / technician stock is a location type, not a new concept
**Gap.** `field-service` and `services` need stock on a van and consumed against a job.
**Why it matters.** This is the single highest-value warehouse capability for our existing verticals and
it is *absent from every tier-1 WMS* (the closest analogue is Tecsys' point-of-use replenishment). It is
also trivially expressible if the model is right: a van is a `wb_locations` row with
`location_type = 'MOBILE'` and an owning technician; issuing a part to a job is a movement from the van
to `VIRT_CONSUMED`; replenishing the van is a transfer. If the model is wrong — no location hierarchy,
no owner, no ledger — it becomes a separate table and a separate reconciliation problem.
**Recommendation.** `wb_locations.assigned_user_id` and a `MOBILE` location type; a `wa_fieldservice_`
adapter mapping job cards to demand headers.
**Module.** `warehouse-base` + `warehouse-adapter-field-service`. **Version.** **v1.1**.

### T-081 — MAJOR — Job-card / work-order consumption is our equivalent of "production issue"
**Gap.** #325 in the matrix — absent from all six products because they interface to an ERP for it.
**Why it matters.** A workshop's stock movement is overwhelmingly "issue this part to this job".
Without it the warehouse is disconnected from the business that funds it. It also carries the
warranty/serial link (a serialised part fitted to a customer's vehicle) that makes returns and recalls
work later.
**Recommendation.** `wa_services_job_issues (job_card_id, demand_line_id, item_id, serial_id, qty,
issued_at, returned_qty)` in the adapter; the movement itself goes through the port as
`ISSUE_TO_JOB` with `ref_doc_type='JOB_CARD'`.
**Module.** `warehouse-adapter-services`. **Version.** **v1.1**.

### T-082 — MAJOR — Core returns / exchange units are an automotive capability nobody in tier 1 has
**Gap.** #334.
**Why it matters.** A customer buys a reconditioned alternator and returns the old one as a "core",
against which a deposit is refunded. The core is stock — it has a value, a location, a status
(`CORE_UNGRADED`) and a downstream disposition (return to remanufacturer). A parts business that cannot
track cores loses real money, and no tier-1 WMS models it.
**Recommendation.** A `CORE` item type linked to the sale item (`wb_item_core_links`), a
`CORE_RECEIVED` movement type, and a core-liability report. Feasible only because `owner_id` and the
status model exist.
**Module.** `warehouse-adapter-dealer`. **Version.** **v2**.

### T-083 — MAJOR — India: a stock transfer between branches is a taxable movement with statutory documents
**Gap.** #230. Absent from all six products except through SAP's India localisation.
**Why it matters.** In India an inter-state (and often intra-state, inter-GSTIN) stock transfer requires
a delivery challan and, above a threshold, an **e-way bill**; branch transfers between different GSTINs
are deemed supplies with GST implications. A warehouse product sold in India that ships stock between
branches and produces no challan is not usable. The platform already stores GSTIN per branch (CLAUDE.md:
"GSTIN is per-state: stored on `branches`"), so the data exists.
**Recommendation.** Delivery challan print on `TRANSFER_SHIP` in v1 (a document, not a tax engine); an
e-way-bill payload builder and the transfer's GST treatment in v1.1, handed to the accounting/India
module rather than implemented in the warehouse.
**Module.** `warehouse` + `accounting-india`. **Version.** **v1** (challan) / **v1.1** (e-way bill).

### T-084 — MINOR — Reorder suggestions, not purchase orders
**Gap.** #303.
**Why it matters.** Our buyers want "what should I buy" — but a purchasing module is a different
product, and the dealer/accessories modules already have purchasing shapes. Building a PO engine inside
the warehouse duplicates them.
**Recommendation.** A "Replenishment suggestions" grid (item, site, on hand, allocated, on order, ROP,
suggested qty, supplier, lead time) with an export and an event; the PO is raised elsewhere.
**Module.** `warehouse`. **Version.** **v1.1**.

### T-085 — MINOR — An availability API is what the rest of the suite actually wants first
**Gap.** #312.
**Why it matters.** Before any vertical wants waves it wants "can I promise this part today". That one
endpoint is the warehouse's most-used integration and it should be designed as a first-class contract,
not fall out of the stock grid.
**Recommendation.** `GET /api/warehouse/availability?item=&site=&owner=&as_of=` returning on hand,
hard-allocated, soft-allocated, available, in-transit, on-order and the earliest expiry — with a bulk
variant, because a quotation screen asks for 40 items at once.
**Module.** `warehouse-base`. **Version.** **v1.1**.

### T-086 — MINOR — Accessories, and any other vertical with existing stock, needs a stated migration path
**Gap.** `accessory_stock_levels` and `accessory_inventory_transactions` hold live data.
**Why it matters.** If `warehouse-base` succeeds, the accessories module should stop keeping its own
inventory. That migration is a one-way door and its feasibility depends on decisions taken in v1
(can we synthesise `owner_id`, `stock_status_id` and `lot_id` for historical rows? Answer: only as
defaults, so historical detail is permanently lost — which is an argument for migrating *early*).
**Recommendation.** State the intent and the approach in the design set: import current balances as
`OPENING_BALANCE` movements at a cut-over date, archive the old transaction table read-only, and do not
attempt to replay history. Same for any `services` parts stock.
**Module.** `warehouse` + `accessories`. **Version.** **v2** (decision in **v1**).

### T-087 — MINOR — Assets module overlap must be resolved, not discovered
**Gap.** `assets` already tracks physical items with locations and statuses.
**Why it matters.** An asset and a stocked item are different things (an asset is depreciated and
individually managed; stock is fungible and valued in layers), but a spare part *becomes* an asset when
issued. Two modules claiming the same physical object is a data-quality problem that surfaces at
year-end.
**Recommendation.** State the boundary: the warehouse owns items until issue; `assets` owns them after
capitalisation; the hand-off is an event carrying `serial_id`.
**Module.** `warehouse-adapter-assets`. **Version.** **v1.1**.

### T-088 — MINOR — The "future logistics module" is where the deferred planning capabilities go
**Gap.** The brief's rule is that nothing is dropped, and §1.15 defers a lot.
**Why it matters.** Without a named destination, "v3" reads as "never" and the capability list rots.
**Recommendation.** Name the destination explicitly for forecasting, multi-echelon optimisation,
seasonal profiles, fair-share allocation, TMS, carrier rating, load planning and yard: a future
`logistics` / `supply-chain` module. §4 items that are refusals stay refusals; these are relocations.
**Module.** future. **Version.** **v3**.

## 2.9 Counting (T-089 … T-090)

### T-089 — BLOCKER — A count is a document that *proposes* an adjustment; it must never write on-hand directly
**Gap.** The precedent has `accessory_inventory_counts` / `accessory_inventory_count_items` but the
posting discipline is unstated, and the natural implementation sets `quantity_on_hand = counted_qty`.
**Why it matters.** If a count writes the balance, then (a) the ledger no longer explains the balance and
T-019's invariant dies, (b) there is no adjustment to post to the GL and no reason code, (c) the variance
is unrecoverable once overwritten, and (d) a count keyed against a stale snapshot silently reverses
movements that happened during the count. Every tier-1 posts a count as an *adjustment transaction*
against a frozen expected quantity.
**Recommendation.** `wh_counts (id, site_id, count_type ENUM('CYCLE','SPOT','ZERO_CHECK','PHYSICAL'),
is_blind, status ENUM('DRAFT','ASSIGNED','COUNTING','PENDING_APPROVAL','POSTED','CANCELLED'),
freeze_scope, frozen_at, posted_at)` and `wh_count_lines (count_id, location_id, item_id, lot_id,
serial_id, lpn_id, owner_id, stock_status_id, expected_qty_at_freeze, counted_qty, variance_qty,
variance_value, recount_seq, counted_by, counted_at, exception_code_id)`. Posting emits one
`COUNT_ADJ` movement per non-zero variance line, from/to `VIRT_COUNT_VARIANCE`, with the count's
reason code. `is_blind` hides `expected_qty_at_freeze` from the counter but stores it.
**Module.** `warehouse`. **Version.** **v1**.

### T-090 — MAJOR — Variance tolerance and approval must gate posting, by value as well as quantity
**Gap.** Unstated.
**Why it matters.** A 1-unit variance on a 3,000-unit washer line is noise; a 1-unit variance on an
engine control unit is an investigation. Quantity-percentage tolerance alone gets this exactly backwards,
which is why every tier-1 offers both a quantity and a value threshold. Without an approval gate, a
mis-keyed count posts a five-figure write-off with no second pair of eyes — and because the ledger is
immutable (correctly), the only repair is a compensating adjustment that now also looks like a loss.
**Recommendation.** `wb_sites.count_tolerance_qty_pct` and `count_tolerance_value`; lines inside
tolerance post automatically, lines outside move the count to `PENDING_APPROVAL` and optionally generate
a recount task (`recount_seq`). Approval is a permission (`warehouse:counts:approve`) distinct from
counting, and the approver may not be the counter.
**Module.** `warehouse`. **Version.** **v1.1**.

## 2.10 Integration, platform and process (T-091 … T-097)

### T-091 — BLOCKER — Idempotency is a schema property of the movement port, not a service convention
**Gap.** —
**Why it matters.** Every adapter will retry: on timeout, on redeploy, on a failed batch re-run. A
non-idempotent movement port turns each retry into duplicate stock. The codebase has met this exact
defect class before in the import framework
(`reference_import_validateapi_persisting_endpoint` — a validate endpoint that persisted, producing
duplicate rows). It is far cheaper to make it structurally impossible.
**Recommendation.** `wb_inbound_messages (id, source_system, idempotency_key, payload_hash,
received_at, status ENUM('RECEIVED','PROCESSED','FAILED','REJECTED'), result_movement_id, error_detail,
retry_count, UNIQUE(source_system, idempotency_key))`. Persist first, process second, return the stored
result on replay. Same key on `wb_stock_ledger.source_ref` so a movement can always be traced to its
originating message.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-092 — MAJOR — An interface error queue with a reprocess action, visible to an operator
**Gap.** —
**Why it matters.** Integrations fail. If failures are only in the application log, the first sign is a
customer noticing missing stock a week later. All six matrix products ship an interface monitor.
**Recommendation.** A grid over `wb_inbound_messages` and `wb_posting_events` filtered to `FAILED`, with
a "reprocess" action (idempotent by construction, per T-091) and an alert when the queue is non-empty
for longer than a threshold. Built on the platform's existing grid/filter/export machinery, so it is a
migration and a page, not an engineering project.
**Module.** `warehouse-base`. **Version.** **v1.1**.

### T-093 — MAJOR — Configurability should be a rules *table*, not a rules *engine*
**Gap.** Körber's Architect toolkit, Oracle's RF screen configuration and Blue Yonder's and Manhattan's
configuration layers are marquee tier-1 features, and the temptation is to answer them with a
general-purpose rules engine.
**Why it matters.** A general rules engine is a product in itself, is untestable in the way this
codebase tests things, and becomes the place where business logic hides from code review. But
*zero* configurability means every customer variation is a release. The tier-1 lesson worth copying is
narrower than it looks: what they actually configure is a small set of ordered, typed rule tables —
putaway, allocation, wave selection, task creation, posting. Each is a table with filter columns and a
strategy column.
**Recommendation.** Five named rule tables (`wb_putaway_rules`, `wb_allocation_rules`,
`wb_task_creation_rules`, `wb_posting_rules`, `wh_wave_selection_rules`), each evaluated in `sequence`
order with a whitelisted strategy enum. No expression language, no scripting, no JSONB conditions
(T-013). Say "no rules engine" explicitly so it is not built by accident.
**Module.** `warehouse-base` + `warehouse`. **Version.** **v2** (the tables land as each feature lands).

### T-094 — MINOR — Custom fields: decide, because the platform forbids the usual answer
**Gap.** #375. Every tier-1 offers user-defined fields; CLAUDE.md forbids JSONB, which is how everyone
else implements them.
**Why it matters.** Without a decision, the first customer request produces either a JSONB column
(standards violation, and the accessories precedent shows this already happens) or a schema change per
customer (unmaintainable in a single-codebase SaaS).
**Recommendation.** Either declare "no custom fields; we add typed columns on request" — defensible for
a single-codebase product — or build the typed-attribute tables from T-013 once. Recommend the former
for v1/v2 and the latter only if a deal requires it.
**Module.** `warehouse-base`. **Version.** **v3**.

### T-095 — MAJOR — The stock ledger must be partitioned from the first migration
**Gap.** —
**Why it matters.** A single mid-size site generates on the order of 10^5–10^6 ledger rows a month once
tasks and status changes are counted; a multi-site install reaches 10^8 within a few years. Converting a
large heap table to a partitioned table later requires a rewrite with downtime, and this codebase
deploys migrations baked into the image (`reference_migrations_baked_into_backend_image`) — there is no
comfortable window for it.
**Recommendation.** `wb_stock_ledger` declared `PARTITION BY RANGE (occurred_at)` with monthly
partitions and an automatic partition-creation job, from migration one. Index strategy stated at the
same time: `(item_id, site_id, occurred_at)`, `(location_id, occurred_at)`, `(ref_doc_type, ref_doc_id)`,
`(source_system, source_ref)`.
**Module.** `warehouse-base`. **Version.** **v1**.

### T-096 — MINOR — Four new modules need four sets of platform registrations, decided before migration one
**Gap.** CLAUDE.md's MODULES table has no warehouse rows and no migration ranges; there is no
`WarehouseSafeTranslation.tsx`; there is no Docker frontend merge entry; there are no menu, permission or
`permission_dependencies` seeds. The memory note
`reference_new_module_integration_points` says a new module has 8+ touchpoints and the gate is at
**build** time, not runtime.
**Why it matters.** Purely mechanical, entirely predictable, and it stops the first build if missed.
Migration ranges in particular must be allocated *before* anyone writes `V1__`, because renumbering
Flyway files after they have run anywhere is a known landmine in this repo
(`reference_flyway_phantom_applied_versions`, `reference_module_migration_move_constraints`).
**Recommendation.** Allocate four contiguous ranges and record them in CLAUDE.md's MODULES table in the
same change as the first migration. Suggested (avoiding every existing range):
`warehouse-base` V900000–V909999 · `warehouse` V910000–V919999 · `warehouse-adapter-*`
V920000–V920999 per vertical · `warehouse-3pl` V930000–V939999. Plus four SafeTranslation files,
frontend merge entries, menu seeds with `WHERE NOT EXISTS` guards, permission seeds and
`permission_dependencies` rows (`permission_id`, **`dependent_permission_id`**).
**Module.** all. **Version.** **v1**.

### T-097 — MINOR — Every warehouse grid must register its filters in the platform allowlist
**Gap.** —
**Why it matters.** A filter field not present in `COMMON_FILTER_CONFIGS.{SCOPE}` in
`platform/frontend/src/utils/filterUtils.ts` is silently dropped by `convertFiltersForApi()` and the
filter appears to do nothing — CLAUDE.md CRITICAL #17, and a recurring defect in this codebase
(`reference_api_filter_param_gate`). A warehouse has *many* filters: site, zone, location, item, lot,
serial, LPN, owner, status, movement type, reason code, date ranges. It will be the largest single
addition to that allowlist the codebase has seen.
**Recommendation.** Define the filter scopes (`WAREHOUSE_STOCK`, `WAREHOUSE_MOVEMENTS`,
`WAREHOUSE_TASKS`, `WAREHOUSE_COUNTS`, `WAREHOUSE_ITEMS`, `WAREHOUSE_LOCATIONS`) in the design set, and
make "the API service forwards every declared filter in `getForManagement`" an explicit acceptance
criterion — an enumerating service silently drops unknown keys.
**Module.** `warehouse` + `platform`. **Version.** **v1**.

---

# §3 — THE STRUCTURAL ONES

Twenty-two findings are in this section because they share one property: **they are nearly free before
the first migration runs and they are either very expensive or genuinely impossible afterwards.** Not
"hard" — impossible, in the specific sense that the *historical values do not exist and cannot be
invented*, so every report that spans the change boundary is permanently untrue.

The distinction that matters is between three kinds of later change:

- **Additive** — a new nullable column, a new table, a new screen. Cheap whenever it is done. Most of
  §2 is here, and that is why so much is deferred to v1.1/v2 without anxiety.
- **Re-keying** — changing the unique key of a large table, or adding a NOT NULL dimension to it.
  Mechanically possible; requires backfilling a value, re-indexing, and touching every query, report,
  export and integration that joins on it. Weeks, plus a risk of silent breakage.
- **Unbackfillable** — the new column's historical value was never observed and cannot be derived.
  You can add the column; you cannot populate it truthfully. Every aggregate that crosses the boundary
  becomes a lie that looks like data. **This is the class that must be prevented, not managed.**

| # | Finding | Change class if deferred | What is permanently lost |
|---|---|---|---|
| 1 | **T-001** ledger double-sided, append-only | Rewrite | Every historical movement's counterparty. A from/to row cannot be split into two sides without inventing which side was authoritative |
| 2 | **T-002** `owner_id` on ledger + on-hand | Re-key → **unbackfillable** | Who owned pre-migration stock. Everything defaults to SELF, so consignment and 3PL history begins at the migration |
| 3 | **T-003** full on-hand unique key | Re-key | The distinction between rows that merged under the narrower key. Merged rows cannot be un-merged |
| 4 | **T-004** status as a master with flags | **Unbackfillable** | Whether historical stock was available, quarantined or damaged. Everything becomes "available" retroactively |
| 5 | **T-005** lot as an entity | Re-key + data quality | The identity of lots keyed inconsistently as strings. `"L-2024/07"` and `"L2024-07"` cannot be proven to be the same lot |
| 6 | **T-006** serial entity + control **mode** | Re-key | Serial state history. A serial's past locations must be reconstructed from string matches |
| 7 | **T-007** `lpn_id` on the ledger | **Unbackfillable** | What was on which pallet, ever, before the change |
| 8 | **T-008** location hierarchy, not 4 VARCHARs | Rewrite | Zone/aisle-level history if the hierarchy is later reparented — historical zone reports silently rewrite themselves |
| 9 | **T-009** virtual locations | Rewrite of every movement | The balancing counterparty. Without it there is no invariant to test, so leaks were never detectable |
| 10 | **T-010** reason codes on adjustments | **Unbackfillable** | Why historical stock changed. Free text cannot be grouped, trended or mapped to a GL account after the fact |
| 11 | **T-011** UoM conversion per item; base UoM immutable | **Unbackfillable** | Which factor a historical quantity was entered under. Every base quantity is suspect |
| 12 | **T-012** `qty_catch` / `catch_uom_id` reserved | Rewrite of every aggregate | Actual weights never captured. Two nullable columns now; a reshaped ledger later |
| 13 | **T-014** allocations as records, not a counter | Rewrite | Which demand held which stock. A counter's history is a single number |
| 14 | **T-015** movement type as a master | Refactor + **unbackfillable** | Posting treatment, billability and reversal counterpart of historical movements |
| 15 | **T-017** UPDATE/DELETE trigger on the ledger | **Unbackfillable** | Any movement edited or soft-deleted before the trigger existed. You cannot prove what the ledger said last year |
| 16 | **T-018** `occurred_at` / `posted_at` / `created_at` | **Unbackfillable** | The difference between when it happened and when it was recorded — for every row written under one timestamp |
| 17 | **T-041** `wb_tasks` present in v1 | Rewrite of inbound + outbound | Not data but architecture: RF, assignment, interleaving, labour and automation each become a rebuild rather than a consumer |
| 18 | **T-043** allocation strategy as data | Refactor, growing with each strategy | Nothing historical — but the allocator becomes untestable, and by the third hardcoded strategy the cost exceeds the original build |
| 19 | **T-062** declared valuation grain | **Restatement** | Nothing is lost, but changing the grain restates every historical balance, which is an accounting event with an audit consequence, not a migration |
| 20 | **T-072** daily stock snapshot job started in v1 | **Unbackfillable** | Occupancy on each past day. Storage billing and ageing cannot be reconstructed from a movement ledger cheaply, and disputes about last month are unanswerable |
| 21 | **T-091** idempotency key on the movement port | **Unbackfillable** + live duplication | Duplicate stock already created by retries, indistinguishable from real movements |
| 22 | **T-095** ledger partitioned by `occurred_at` | Rewrite with downtime | Nothing is lost, but migrations here are baked into the container image, so the conversion has no comfortable window |

## 3.1 Why the from/to row is the deepest of them (T-001)

It looks like a modelling preference. It is not. A from/to row makes the following query undefinable:

> *"What was on hand at location L, for item I, owned by O, in status S, at 14:00 on 3 March?"*

With two signed rows it is `SUM(qty_base) WHERE location_id = L AND … AND occurred_at <= '…'`. With
from/to it is a `CASE` over two nullable location columns, one branch per movement type, and the branch
list grows every time a movement type is added. Worse, the correctness of the `CASE` is not checkable:
there is no invariant like "the rows for a movement sum to zero", so a movement that decrements the
source and forgets the destination — the classic partial-failure — is silently a stock leak.

Every consequence in this document flows from getting this one right: reconstructibility (T-019),
valuation as-at (#275), traceability (#64/#65), the reconciliation report (T-066), 3PL billing history
(T-071) and the stock-to-GL invariant (T-066). It is the first migration and it should be written before
anything else in the design set is agreed.

## 3.2 Why the status model cannot be a location, and cannot be an enum (T-004)

Three tempting shortcuts, and what each costs:

| Shortcut | Breaks on |
|---|---|
| "Damaged stock goes in the DAMAGED bin" | Damaged stock in the pick face; counting a bin then disagrees with counting an item; FEFO across the "same" stock splits; a physical move is forced for a paperwork event |
| "`status` is a CHECK-constrained enum on the ledger" | Every new status is a migration **plus** a code change in every query that hardcodes the available list. Our own codebase has a documented recurring defect of exactly this shape (a status present in the CHECK constraint but missing from the frontend union, the variant map, the filter options or the i18n keys) |
| "Availability is `status = 'AVAILABLE'`" | Any second allocatable status — e.g. `AVAILABLE_SHORT_DATED` sellable to a discount channel — requires finding every hardcoded comparison |

The master table with `is_allocatable` makes availability a join, and a new status a seed row.

## 3.3 Why the allocation counter is the same mistake as a balance without open items (T-014)

The accounting audit's deepest finding was that a party balance without bill-by-bill references is right
in total and useless in detail. `quantity_reserved` is the identical error in the stock domain, and it
fails identically:

- **Cannot release.** Cancelling an order must decrement the counter by exactly what that order held.
  A counter does not remember, so the code must recompute it from the order — and if the order changed
  in between, the counter drifts.
- **Cannot reconcile.** There is nothing to compare the counter *to*. Drift is undetectable until
  available goes negative, and the only repair is to zero it, releasing every reservation at once.
- **Cannot qualify.** Soft vs hard, allocated-to-lot, allocated-to-LPN, expiring reservations — none are
  expressible in a scalar.
- **Cannot audit.** "Why can't I pick this stock?" has no answer.

## 3.4 The one-week decisions that unlock whole later modules

| Decision taken in v1 | Module it unlocks without a rewrite |
|---|---|
| `owner_id` on ledger, on-hand, allocations, cost layers | `warehouse-3pl` in its entirety; consignment; VMI; customer-owned material |
| `wb_tasks` with one synchronous consumer | The whole execution layer: RF, assignment, interleaving, labour, automation, exception console |
| `lpn_id` nullable everywhere | Pallet receiving, LPN picking, cartonisation, SSCC, nested handling units |
| `qty_catch` / `catch_uom_id` nullable | The entire food/meat/chemicals vertical |
| Status master with flags | QC, quarantine, damage, returns grading, recall hold, short-dated channels |
| Movement-type master with `is_billable_event` | 3PL activity billing computed from real history, not from its own go-live date |
| Daily snapshot job | Storage billing, ageing, days-on-hand, obsolescence — all with history |
| `occurred_at` separate from `posted_at` | Offline RF, backdated counts, multi-timezone sites, period-correct valuation |
| Allocation strategies as rows | FEFO, lot-specific, location-priority, customer-specific — as configuration, not branches |
| Ledger partitioned by month | Surviving year three without a downtime migration |

---

# §4 — WHAT WE SHOULD DELIBERATELY NOT BUILD

Fifteen refusals. Each is a capability a tier-1 product has, that we should decline **and say we
decline**, because an unstated absence reads as an oversight and invites someone to build it badly.

| # | Not building | Who has it | Why not |
|---|---|---|---|
| 1 | **A transportation management system** — carrier rate shopping, freight procurement, route optimisation | Manhattan TMS, Blue Yonder TMS, SAP TM, Oracle OTM — all *separate products* even at their own vendors | The tier-1 vendors themselves keep TMS out of the WMS. Rating engines need carrier contracts, fuel surcharges, accessorial rules and dimensional-weight logic; it is a product, not a feature. Integrate a carrier API for label generation (v3) and stop |
| 2 | **Distributed order management / order sourcing across sites** | Manhattan DOM, Blue Yonder, Softeon | This is an OMS. It decides *where* to fulfil from; a WMS executes once that is decided. Building it inside the warehouse would make the warehouse the system of record for orders, which it must not be |
| 3 | **A labour-standards engineering engine** (MOST/MTM element libraries, travel-time models, discrete standards) | Manhattan LM, Blue Yonder (RedPrairie heritage), SAP EWM LM, Infor | Engineered standards require industrial-engineering time studies per site. We should measure *actual* task duration (T-058, free) and report it; we should not claim to compute an engineered standard |
| 4 | **Incentive pay computation** | Manhattan, Blue Yonder | Payroll consequences from a warehouse metric is a labour-relations product, and a wrong number is a legal problem, not a bug |
| 5 | **Direct automation control (PLC telegrams, AS/RS material flow)** | SAP EWM MFS is uniquely deep here; Körber via Aberle | This is real-time control software with safety implications, written to a different engineering standard than a web application. Expose a task event contract (T-059) and let the WCS vendor integrate |
| 6 | **Voice recognition** | Körber (Voiteq heritage), Infor, Manhattan, Blue Yonder | Speech recognition tuned for warehouse noise and accents is a specialist product. Integrate; never build |
| 7 | **A slotting optimisation solver** | Manhattan, Blue Yonder Slotting Optimization, SAP EWM | The *analysis* (velocity, cube, affinity) is worth having in v3. The optimiser is an OR problem whose value depends on constraints we will not have modelled. Report the recommendation; let a human move the stock |
| 8 | **Demand forecasting, multi-echelon inventory optimisation, seasonal profiles** | Blue Yonder (their origin), SAP IBP, Oracle Demand Management | A planning product. Consume a forecast through an interface (v3); do not compute one. Relocated to a future `logistics` module (T-088), not refused outright |
| 9 | **LIFO costing** | SAP, Oracle (jurisdiction-limited) | Not permitted under Ind AS 2 / IAS 2. Offering it invites non-compliant accounts (T-068) |
| 10 | **A general-purpose rules engine / scripting layer** | Körber Architect, Blue Yonder and Manhattan configuration layers, Oracle RF screen config | Five ordered, typed rule tables give 90% of the benefit and remain reviewable and testable. A scripting layer becomes the place business logic hides from code review (T-093) |
| 11 | **JSONB custom-field bags** | Every tier-1 offers user-defined fields | Forbidden by the platform's own standards, and the mechanism by which filters, indexes and reports become impossible. Typed attribute tables or nothing (T-013, T-094) |
| 12 | **Multi-tenant SaaS** (one database, many customers) | Oracle WMS Cloud, Manhattan Active | The platform is single-tenant per install by existing decision. `owner_id` gives us multi-*client* separation inside one install, which is what a 3PL needs; it is not the same thing and we should not conflate them in a sales conversation |
| 13 | **UDI / medical-device and pharma-serialisation compliance regimes** | Tecsys is the reference here | Each is a regulatory programme with certification, not a feature. Decline the vertical rather than half-support it |
| 14 | **Export/customs documentation, bonded warehouse, FTZ** | SAP GTS, Manhattan and Infor partially | Country-specific regulatory software. Our India obligations (delivery challan, e-way bill — T-083) are in scope; international trade compliance is not |
| 15 | **Shift simulation / digital twin / 3D warehouse visualisation** | Infor's 3D visualisation; Blue Yonder simulation `?` | Demo-ware at our stage. It sells to buyers who are not our buyers, and it consumes the effort that should go into RF screens |

**A note on how to say these.** Each refusal above should appear in the design set as a one-line
statement with its reason, in the same place a reader would look for the feature. "Not built, because
X" is a credible answer in a sales conversation; silence is not.

---

# §5 — THE MINIMUM CREDIBLE v1

## 5.1 The shape

The v1 that can be demonstrated without embarrassment is **not** a thin slice of a tier-1 WMS. It is a
*complete, correct, single-site, single-owner stock system with a real ledger, a real status model, real
counting, and a handheld* — the Softeon/Tecsys shape rather than the Manhattan shape: narrow scope,
completely finished, deployable in weeks.

The test I would apply: **can a warehouse manager run their entire day in it without touching a
spreadsheet, and can a finance director reconcile it to the books?** Breadth beyond that buys nothing at
this stage; a hole inside that scope loses the deal.

## 5.2 What is in it

**Foundations (`warehouse-base`) — all of §3, none of it visible**
`wb_items` · `wb_item_barcodes` · `wb_item_uom_conversions` · `wb_uoms` · `wb_sites` · `wb_locations`
(hierarchy + virtual + generator) · `wb_location_types` · `wb_stock_statuses` · `wb_owners` ·
`wb_lots` · `wb_serials` · `wb_lpns` (empty) · `wb_movement_types` · `wb_reason_codes` ·
`wb_stock_movements` · `wb_stock_ledger` (partitioned, immutable, double-sided, all seven dimensions) ·
`wb_stock_on_hand` (full key, reconciled nightly) · `wb_allocations` · `wb_cost_layers` ·
`wb_cost_consumptions` · `wb_tasks` · `wb_task_types` · `wb_allocation_strategies` ·
`wb_allocation_rules` · `wb_posting_rules` · `wb_inbound_messages` · `wb_daily_stock_snapshots` ·
`wb_trading_partners` · `wb_item_sites` · `wb_stock_periods`.
Plus: the movement port (idempotent), the availability API, the reconstructibility job and its test.

**Operations (`warehouse`)**
Receive (against PO, and blind) into a chosen status · putaway (suggested location, override with
reason) · bin-to-bin move · stock enquiry by every dimension · adjustment with reason code · status
change · scrap · demand entry and **release** (soft → hard allocation, task creation) · discrete pick ·
pack · ship confirm · cycle count by location range and by item, blind or not, posting through the
ledger with variance approval · opening-balance import · delivery challan print.

**Reporting**
Stock on hand (by item, location, lot, status, owner) · stock movement / ledger enquiry with full drill ·
stock valuation with an as-at date · stock ageing · adjustment register by reason · count variance
register · dock-to-stock and order cycle time. All on the platform's grid/filter/export machinery, with
the filter scopes registered (T-097).

**Mobile (`mobile/`)** — the decision and the task model in v1, the first screens immediately after:
Receive · Putaway · Move · Pick · Stock enquiry.

**Adapters** — one only, whichever vertical is the pilot. Building two adapters before the first is
proven is how the port contract (T-079) gets weakened.

## 5.3 What is explicitly not in v1, and how to say so

Waves · FEFO · putaway rule editor · RF-configurable flows · labour reporting · cross-dock · 3PL
billing · packing cartonisation · returns dispositions · slotting · yard · replenishment. Each of these
should be visible in the roadmap with a version, because a buyer who hears "not yet, it is v1.1 and here
is the data model that already supports it" hears a product; a buyer who hears silence hears a
prototype.

## 5.4 Who we lose to at this cut, and on what

| Competitor | We lose when the buyer says | Honest assessment |
|---|---|---|
| **Oracle WMS Cloud** | "Show me RF flows I can configure myself, and LPN-based receiving" | We lose. Their RF configurability and LPN-native model are a decade ahead. We do not compete for their deals in v1 |
| **Manhattan (Active WM / SCALE)** | "How does your waving and labour management work?" | We lose, and should not be in the room. Their labour management alone is larger than our whole v1 |
| **Blue Yonder** | "Slotting, labour standards, and integrated planning" | We lose |
| **SAP EWM** | "We run S/4 and want warehousing inside it" | We lose, and correctly — that buyer should use EWM |
| **Körber** | "We need to configure the system ourselves without your consultants" | We lose on configurability; we may win on price and time-to-value |
| **Infor WMS** | "3PL billing and multi-client out of the box" | We lose in v1, and should be competitive in v2 **if and only if** `owner_id` and `is_billable_event` are in v1 (T-002, T-071) |
| **Softeon** | "Fast deployment, complete on our operating model, lower TCO" | This is the deal we are *actually* competing for. We win or lose on completeness within scope, not breadth |
| **Tecsys** | "Point-of-use / consignment / field stock" | Closest analogue to our van-stock and job-card story (T-080, T-081). We can win here in v1.1 with a vertical they do not serve |

**And who we beat, which is the point.** At this cut we are not selling against tier 1. We are selling
against: a dealer running parts on `accessories` plus three spreadsheets; a workshop with no stock
system; Tally's inventory module; Zoho Inventory and similar SMB tools; and the inventory module inside
a generic ERP. Against those, a real double-entry stock ledger with lots, serials, statuses, counting
with approval, valuation that reconciles, and a handheld is decisively better — **and it is better
precisely because of §3**, which none of them have.

## 5.5 The one-sentence version

*Build the ledger and its seven dimensions correctly in v1, build a small number of screens on top of it,
put a handheld in someone's hand, and defer everything else with a version number attached — because the
deferrable things are additive and the ledger is not.*

---

## Appendix A — Confidence register

Claims in this document I am **not** confident about, marked `?` in the matrices, listed so a reader
knows exactly what to verify before quoting any of it externally:

- Catch-weight maturity in Blue Yonder, Oracle WMS Cloud, Körber and Infor.
- Whether Oracle WMS Cloud ships a 3PL **billing engine** as opposed to billing-relevant activity data.
- Körber's labour-management depth relative to Manhattan and Blue Yonder.
- Infor's slotting capability as a distinct offering.
- Blue Yonder's native voice capability vs. a partner integration.
- Whether appointment/dock scheduling in each product is in the WMS or an adjacent module.
- Manhattan's yard management packaging relative to Active WM.
- Blue Yonder's simulation capability.
- Softeon's and Tecsys's specific module names throughout §1.22.
- The Voiteq acquisition as the basis of Körber's voice capability, and the Aberle acquisition as the
  basis of its automation/AS-RS capability — the corporate lineage I am confident about, the current
  product packaging I am not.
- Whether SAP LE-WM is fully out of mainstream maintenance, and on what date. I have deliberately
  stated no date; EWM is unambiguously the strategic product either way.

- All statements about which capabilities are separately licensed — I have deliberately made none.

**No version numbers and no pricing tiers appear anywhere in this document**, for any competitor,
because I could not verify them.

## Appendix B — What this lens did not cover

- **Mid-market and SMB competitors** (Zoho Inventory, Unicommerce, Increff, Odoo, ERPNext, Fishbowl,
  Cin7, Katana, Sortly, and the WMS-inside-ERP options). That is a separate lens and it matters more to
  §5's win/loss table than tier 1 does.
- **India-specific WMS vendors and 3PL operators' in-house systems.**
- **The existing codebase's non-inventory capabilities** beyond the `accessories` precedent cited in the
  header — no `services`, `field-service` or `assets` stock model was audited, because none exists
  (`find` for a `Warehouse` entity returns only the accessories one).
- **Effort estimation.** No finding carries a size. Placement in v1/v1.1/v2/v3 is a *sequencing*
  judgement about irreversibility and commercial necessity, not a schedule.
