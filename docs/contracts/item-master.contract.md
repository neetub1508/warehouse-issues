# Functional Contract — Item master: identity, status facts, UoM, identification, packaging, supersession as engineering change

> **What this is.** The functional truth for the one item master (`whb_items`) and the records that hang off
> it: the four status facts, the base stocking UoM and per-item conversions, identifiers and barcodes,
> packaging levels, external references, attributes and documents, kits, and **supersession — in a plant,
> the engineering-change record** (`D-16`, `RN-051`) — with its stock and demand treatment and interchange.
>
> **Status.** Derived 2026-10-23 (v0) for R30 `CP-FR-007` row 2 (`D-17` item a) from
> `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.3 and checked against the built `warehouse-base` code. Not
> ratified. Disagreements between the FRD and the code are in §10; the FRD rule stands in every row.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Item create → edit → status facts change → deactivate (refused with stock); UoM conversion create / supersede; identifier and packaging maintenance; supersession link create → stock treatment → (for `MERGE_STOCK`) merge posting; kit definition versions |
| **Module** | `warehouse-base` (FR-072 / FR-073 enquiry half: `warehouse`) |
| **Domain baseline** | `D-9`, `D-10`, `L-5`, `L-7`, `L-12`; FRD §6.3 `FR-048`…`FR-078` (`FR-068` and `FR-074` are not in scope here; `FR-074` is WITHDRAWN by `D-16`) · `movement-post-reverse.contract.md` `MPR-T1-01` (every stock effect posts through it) |
| **Owning tasks** | `issues/p1-01.md` (items, item types, status facts) · `issues/p1-02.md` (UoM, identifiers, packaging, scan resolver) · `issues/p1-03.md` (item × site, classification, supersession, hazmat, shelf-life columns) · `issues/p1-04.md` (external refs, documents) · `issues/p3-10.md` (kits) · `issues/p3-15.md` (GS1 composite) · `issues/p7-11.md` (`FR-072`, `FR-073` re-homed, `D-17` item 5) |
| **Primary tables** | `whb_items` (`V500015`), `whb_item_types` (`V500008`), `whb_uom_classes`, `whb_uoms` (`V500009`), `whb_item_identifiers`, `whb_item_packaging_levels`, `whb_item_uom_conversions`, `whb_item_location_settings` (`V500016`), `whb_item_external_refs`, `whb_item_documents` (`V500017`), `whb_item_site_settings`, `whb_item_supplier_sources`, `whb_item_supersessions` (`V500050`), `whb_kit_definitions`, `whb_kit_components` (`V500060`), `whb_entity_attribute_values` (`V500010`) |
| **Permission resources** | `whb_items:{view,create,edit,delete,export}` · `whb_item_uom_conversions:*` · `whb_item_identifiers:*` · `whb_item_supersessions:{view,create,edit,delete,export,merge}` (and the matching resources of WS-024…WS-035) |
| **Routes** | WS-023 Items · WS-024 Identifiers & Barcodes · WS-025 Packaging Levels · WS-026 UoM Conversions · WS-027 Item × Site · WS-028 Item × Location · WS-030 Supersessions · WS-031 External References · WS-034 Units of Measure · WS-035 Kit Definitions · WS-010 Item Types · WS-013 Attribute Keys · WS-071 Scan Enquiry Console · WS-208 Stock on Hand |
| **Contract version** | `v0 — 2026-10-23` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | One item master; uniqueness is `(owner, sku)` plus a global `item_code` (`WH-SC-047`) | `ITM-GRD-01`, `-02` |
| A2 | An item with stock cannot be deactivated; blocking receipt or issue is the alternative (`WH-SC-259`) | `ITM-T1-04`, `ITM-GRD-05` |
| A3 | The base UoM cannot change once a ledger row exists, by a database trigger (`WH-SC-020`) | `ITM-GRD-06` |
| A4 | A barcode resolves to a packaging level; a scan never guesses (`WH-SC-262`, `WH-SC-265`) | `ITM-GRD-09`, `ITM-T4-03` |
| A5 | A supersession is cycle-free, walks to the terminal item, and records a reproducible stock / demand treatment; `MERGE_STOCK` is a movement (`WH-SC-101`) | `ITM-GRD-14`…`-16`, `ITM-T1-08`, `ITM-T4-05` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Kind |
|---|---|---|---|
| Item | `NEW` · `ACTIVE` · `PHASE_OUT` · `OBSOLETE` · `BLOCKED` | `lifecycle_status` — **reporting only**; the operative facts are `is_receivable`, `is_issuable`, `is_orderable`, `is_countable` (independent) | lifecycle |
| Item | active / inactive | `is_active` | master |
| UoM conversion | current / superseded | `effective_from`, `effective_to` | dated history |
| Supersession link | `KEEP_SEPARATE` · `MERGE_DEMAND` · `MERGE_STOCK` | `stock_treatment` | treatment |
| Kit definition version | in force / ended | dated version range | dated history |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | UI | Source |
|---|---|---|---|---|---|---|---|---|
| ITM-T1-01 | — | Create item: owner, `sku`, name, item type, base UoM, category, tax classification, status facts | active, `lifecycle_status` as given (default `ACTIVE`) | `ITM-GRD-01`…`-04` | `whb_items:create` | system-generated immutable `code` (`item_code`) | WS-023 **Add** | FR-048, FR-060 |
| ITM-T1-02 | active | Edit | unchanged | `ITM-GRD-03`, `-06`, `-07`, `-20`, `-21` | `whb_items:edit` | — | WS-023 **Edit** | FR-048 |
| ITM-T1-03 | any | Change a status fact (receivable / issuable / orderable / countable) or `lifecycle_status` | facts as set | each fact independent of the others and of `lifecycle_status` | `whb_items:edit` | the consuming document checks the fact (`ITM-T4-01`) | WS-023 Edit | FR-050 |
| ITM-T1-04 | active | Deactivate | inactive | `ITM-GRD-05` | `whb_items:edit` | — | WS-023 **Deactivate** | FR-051 |
| ITM-T1-05 | — | Create a UoM conversion (item-specific, or global with a null item) | current | `ITM-GRD-08` | `whb_item_uom_conversions:create` | — | WS-026 | FR-055 |
| ITM-T1-06 | current | Supersede a conversion (new factor) | old row ended, new row current | `ITM-GRD-08`, `-22`; no ledger line's frozen factor changes (`L-7`) | `whb_item_uom_conversions:edit` | — | WS-026 | FR-055 |
| ITM-T1-07 | — | Create a supersession link: predecessor, successor, type (`REPLACES` / `INTERCHANGE` / `PARTIAL`), `chain_sequence`, `quantity_ratio`, effective date | link with `KEEP_SEPARATE` | `ITM-GRD-14`, `-15` | `whb_item_supersessions:create` | — | WS-030 **Add** | FR-071 |
| ITM-T1-08 | `KEEP_SEPARATE` | Set stock treatment `MERGE_DEMAND` | `MERGE_DEMAND` (recorded only) | — | `whb_item_supersessions:edit` | none — no report or calculation reads it (W58 scope note) | WS-030 action | FR-072 |
| ITM-T1-09 | `KEEP_SEPARATE` · `MERGE_DEMAND` | **Merge stock** | `MERGE_STOCK` | `ITM-GRD-16` | `whb_item_supersessions:merge` | `ITM-T4-05` in one transaction | WS-030 action **Merge stock** | FR-072 |
| ITM-T1-10 | — | Create a kit definition version (`PHANTOM` or `STOCKED`, same component list shape) | in force from its start | `ITM-GRD-17` | kit definitions `:create` | — | WS-035 | FR-075 |

### 1.3 Guards

| ID | Predicate | Refusal: HTTP · code · field | Backstop | Source |
|---|---|---|---|---|
| ITM-GRD-01 | `(owner_id, sku)` is unique; `code` is globally unique, system-generated and immutable; every FK points at `id`, the label shows `code` | `422 ITEM_SKU_EXISTS` · `sku` | `uk_whb_items_owner_sku`, `uk_whb_items_code` (`V500015:217-218`) | FR-060 |
| ITM-GRD-02 | No module other than `accessories` (`D-9`) creates a second item master; every consumer reads `whb_items` or links through `whb_item_external_refs` | — (architecture: `WarehouseBaseCouplingTest`) | — | FR-048 |
| ITM-GRD-03 | `item_type` is an active row of the `whb_item_types` registry (seeded at least `STOCK`, `NON_STOCK`, `SERVICE`, `KIT_STOCKED`, `KIT_PHANTOM`, `CORE`, `CONSUMABLE`, `PACKAGING`, `RETURNABLE_EQUIPMENT`, `TYRE`, `FUEL`, `ASSET`) | `422` `UNKNOWN_*` · `itemTypeCode` | FK by code | FR-049 |
| ITM-GRD-04 | The item carries **no cost column**; a request carrying a cost is refused as an unknown field. A standard cost is a separate effective-dated table | `400` unknown field | no column | FR-052 |
| ITM-GRD-05 | Deactivate: on-hand is zero across every site, status and owner | `409 ITEM_HAS_STOCK` · header, naming the offered alternative (block for receipt / issue) | — | FR-051 |
| ITM-GRD-06 | The base stocking UoM does not change once any ledger line references the item | `422 ITEM_BASE_UOM_IMMUTABLE` · `baseUomCode` | **database trigger** (`V500036`) — not trusted to the service | FR-054 |
| ITM-GRD-07 | `tax_classification_code` is a string, never an FK into a tax master | — | column type | FR-066 |
| ITM-GRD-08 | A conversion converts between two different units; at most one current row per `(item, from, to)`; a null-item row is the global (physical-dimension) conversion and an item row overrides it | `CONVERSION_SAME_UNIT` · `CONVERSION_OVERLAP` (`409`) · `toUomCode` | `uk_whb_item_uom_conversions_current` (`V500016:403`) | FR-055 |
| ITM-GRD-09 | An identifier names a packaging level (or the each); its key is `uk(identifier_type, normalised_value, owner_id, counterparty_id, channel_id)` — **deliberately not globally unique**; a barcode carries a type (purpose) distinct from a format (symbology) and a status that retires it without deleting scan history; **quantity is never stored on the barcode** | `409 IDENTIFIER_ALREADY_EXISTS` · `value` | `uk_whb_item_identifiers_key` (`V500016:260-262`) | FR-057, FR-059 — §10 row 3 |
| ITM-GRD-10 | An alias row carries the identifier type (owner SKU, GTIN-13/14, UPC/EAN, manufacturer part number, supplier code, customer part number, legacy code) and `pack_qty`; a supplier part number is unique per supplier | `409 IDENTIFIER_ALREADY_EXISTS` | as `ITM-GRD-09` | FR-059 |
| ITM-GRD-11 | Every UoM carries `unece_rec20_code` and `gst_uqc_code` | `422` field-named on WS-034 | columns (`V500009`) | FR-056 |
| ITM-GRD-12 | `whb_item_external_refs (item_id, source_module, external_id, external_label)` is unique on `(source_module, external_id)`; `source_module` is an opaque string | `409 EXTERNAL_REF_ALREADY_EXISTS` · `externalId` | `uk_whb_item_external_refs_source_external` (`V500017:69`) | FR-061 |
| ITM-GRD-13 | An attribute value names a registered key whose subject list includes the value's subject (item, movement line, lot, serial, LPN, location, counterparty, document) and sets exactly the typed column of the key's `value_type` | `422 ITEM_ATTRIBUTE_KEY_NOT_REGISTERED` / `ITEM_ATTRIBUTE_KEY_WRONG_SUBJECT` / `ITEM_ATTRIBUTE_VALUE_TYPE_MISMATCH` · `attributes.<key>` | key / value-type trigger | FR-076 |
| ITM-GRD-14 | A supersession link is not to itself and closes no cycle across the chain; `chain_sequence ≥ 1`, `quantity_ratio > 0`, type ∈ {`REPLACES`, `INTERCHANGE`, `PARTIAL`}, bidirectional only for `INTERCHANGE` | `422 SUPERSESSION_SELF` / `422 SUPERSESSION_CYCLE` / `SUPERSESSION_DATES_INVALID` · `successorItemId` | `chk_whb_item_supersessions_*` (`V500050:236-245`) | FR-071, FR-073 |
| ITM-GRD-15 | Predecessor and successor are fixed once created | `SUPERSESSION_ITEMS_IMMUTABLE` | — | FR-071 |
| ITM-GRD-16 | Merge stock: posts through the single writer (`MPR-T1-01`), each predecessor position moved to the successor **at the predecessor's cost layers**, under the link's `quantity_ratio`; the link is marked `MERGE_STOCK` only if the movement posted | the writer's refusal; nothing changes on refusal | `L-1`, `L-2` | FR-072 — §10 row 2 |
| ITM-GRD-17 | A kit's components are active, not themselves phantom kits where the parent stocks, convertible to their UoM; versions do not overlap | `KIT_COMPONENT_IS_PHANTOM` / `KIT_COMPONENT_UOM_NOT_CONVERTIBLE` / `KIT_VERSION_OVERLAP` | `V500089` (a phantom kit holds no stock) | FR-075 |
| ITM-GRD-18 | An item document link references platform `documents` with `ON DELETE NO ACTION`; a file with a link cannot be deleted silently | `ITEM_DOCUMENT_*` on the link | FK `ON DELETE NO ACTION` (`V500017:113`) | FR-077 |
| ITM-GRD-19 | Planning numbers — reorder point, safety stock, min, max, reorder quantity, lead time — are read from **item × site** (v1) and **item × location** (v1.1); item-level values only seed a new row | `ITEM_SITE_SETTING_ALREADY_EXISTS` on a duplicate | `whb_item_site_settings` (`V500050:98`), `whb_item_location_settings` (`V500016`) | FR-053 |
| ITM-GRD-20 | An item's owner never changes; an item two owners stock is two items | `422 ITEM_OWNER_IMMUTABLE` · `ownerId` (`WhbItemValidationService.java:219`) | — | FR-048 |
| ITM-GRD-21 | The lot and serial control modes do not change (a downgrade included) while the item has any non-zero position, virtual and negative included | `422 ITEM_HAS_STOCK` · the first changed mode field (`validateControlModesUnchanged`, `WhbItemValidationService.java:251-256`) | **database trigger** (`V500027`) — the service check only names the field | FR-098 |
| ITM-GRD-22 | A conversion a posted ledger line has used is not edited or deleted; a new factor supersedes it (`ITM-T1-06`) | `409 CONVERSION_IN_USE` (`WhbItemUomConversionService.java:39`, `:49`) | database trigger | FR-055 |

### 1.4 Unreachable

| ID | Must never happen | Source |
|---|---|---|
| ITM-UNR-01 | A user-defined JSONB custom field on any item-master table. The answer is a typed column on request, or an install-created attribute key (`owning_module = 'INSTALL'`, WS-013) | FR-078 |
| ITM-UNR-02 | A barcode parsed inline at a scan surface, or a scanner SDK in the codebase. Every scan surface calls the one scan-resolution service with a plain string | FR-062 |
| ITM-UNR-03 | A scan that guesses: a location code matching another site answers `AMBIGUOUS_LOCATION`; an identifier matching several items resolves session owner → counterparty context and otherwise answers `AMBIGUOUS_IDENTIFIER` with the candidates | FR-062 |
| ITM-UNR-04 | A lookup path that reads a superseded item without the supersession resolver — stock enquiry, material requisition, reorder, receipt matching and barcode scan each walk the chain to the terminal item | FR-071 — §10 row 1 |
| ITM-UNR-05 | A `MERGE_DEMAND` treatment read by any report or calculation (it is recorded only; demand history stays per physical item) | FR-072 |
| ITM-UNR-06 | A virtual (`PHANTOM`) kit holding stock; a physical (`STOCKED`) kit stocked other than by a work order converting components | FR-075 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| ITM-T2-01 | Create / edit / deactivate item | `whb_items:create` / `:edit` | — / active | FR-048, FR-051 |
| ITM-T2-02 | Maintain conversions, identifiers, packaging, external refs | the WS-024…WS-031 resources | — | FR-055, FR-057, FR-058, FR-061 |
| ITM-T2-03 | Merge stock on a supersession | `whb_item_supersessions:merge` | `KEEP_SEPARATE` · `MERGE_DEMAND` | FR-072 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Source |
|---|---|---|---|---|
| ITM-T3-01 | A supersession is effective from its effective date: before it the predecessor resolves to itself, from it the resolver walks to the successor | the link's effective date vs the lookup time | resolution result only | FR-071 |
| ITM-T3-02 | Shelf-life columns `shelf_life_days`, `min_shelf_life_receipt_pct`, `min_shelf_life_ship_pct` exist from v1 so the later FEFO / shelf-life rules read data captured from the first receipt | — (columns, `V500015:165-168`) | none here; consumed by the lot contract | FR-069 |
| ITM-T3-03 | ABC, velocity / movement and count-frequency classes are held on item × site from v1; the ABC recompute is `FR-463` (v1.1), velocity / XYZ recompute v3 | the recompute job (not in this contract) | `whb_item_site_settings.abc_class`, `velocity_class`, `count_frequency_class` | FR-070 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| ITM-T4-01 | A receipt, issue, order or count names an item | it checks the matching fact (`is_receivable` / `is_issuable` / `is_orderable` / `is_countable`), never `lifecycle_status` or `is_active` alone | each document's validation | FR-050 |
| ITM-T4-02 | A document or movement line names an item | `tax_classification_code` is **snapshotted** onto the line; a later item edit never changes an old line | writer / document services | FR-066 |
| ITM-T4-03 | A scan resolves to an identifier | the quantity is taken from its packaging level (supplier-specific → supplier-agnostic default → loose / each, `priority` inside a tier, `WhbPackagingResolver`), never from the barcode row | scan service, packaging resolver | FR-057, FR-058 |
| ITM-T4-04 | A GS1 element string is scanned (AI `01`/`10`/`17`/`21`/`00`/`310n`, FNC1) | one composite result `{gtin, lot, expiry, serial, sscc, quantity}` (`WhbGs1Elements`) | scan service | FR-063 |
| ITM-T4-05 | Merge stock posts (`ITM-T1-09`) | one movement through the writer: −qty at each predecessor position, +qty × ratio at the successor, at the predecessor's cost layers; link `stock_treatment` → `MERGE_STOCK` in the same transaction | supersession service → writer | FR-072 |
| ITM-T4-06 | A stock enquiry finds the item short (WS-208) | it shows the interchange / alternate parts ("not in stock — 2 available as `<interchange>`") with availability across every branch, grouped by each site's **`REGISTERED` branch at today**; a shared site appears once tagged with the branches it serves; a *sister* is a site with a different `REGISTERED` branch, so a site is never its own sister | stock-enquiry query service | FR-073 — §10 row 4 |
| ITM-T4-07 | A movement line or position carries a catch-weight item | `secondary_quantity` + `secondary_uom_id` are columns on the line and the position from v1 (v1 writes null); `is_catch_weight` on the item | columns (`V500030:333`, `V500015:163`) | FR-065 |
| ITM-T4-08 | An LPN, warehouse, location or party is labelled or exchanged | `sscc` on the LPN and `gln` on warehouse, location and counterparty are v1 columns | columns (`V500018`, `V500012`, `V500013`, `V500011`) | FR-064 |
| ITM-T4-09 | A hazmat item is shipped or printed | the hazmat block — UN number, class, packing group, proper shipping name, subsidiary classes — is read from the item (`hazmat_*`, `V500015`) | consumers | FR-067 |

## 5. T5 — Screen contract

| ID | Screen | Contract | Source |
|---|---|---|---|
| ITM-T5-01 | WS-023 Items (reference **Department**) | columns include `code`, `sku`, `ownerName`, `itemTypeName`, `baseUomCode`, the four facts, `lifecycleStatus`, `taxClassificationCode`, `isActive`; **no cost column**; Deactivate on a stocked item shows `ITEM_HAS_STOCK` inside the modal and offers *Block receipt / issue* | FR-048, FR-050, FR-051, FR-052 |
| ITM-T5-02 | WS-026 UoM Conversions | a null item shows as *Global*; `fromUom`/`toUom`/item read-only on edit; supersede opens a new dated row | FR-055 |
| ITM-T5-03 | WS-024 Identifiers & Barcodes | `identifierType`, `value`, `normalisedValue`, `barcodeFormat`, `packagingLevel`, `owner`, `counterparty`, `status`; no editable quantity | FR-057, FR-059 |
| ITM-T5-04 | WS-030 Supersessions | `chain_sequence`, type, ratio, effective date, treatment (`MERGE_DEMAND` labelled *Merge demand (recorded only)*); a *Chain* view walks to the terminal item; **Merge stock** only with `:merge` | FR-071, FR-072 |
| ITM-T5-05 | WS-071 Scan Enquiry Console | shows the typed result, or `AMBIGUOUS_LOCATION` / `AMBIGUOUS_IDENTIFIER` with the candidates; every scan logged, resolved or not | FR-062 |
| ITM-T5-06 | WS-013 Attribute Keys | install-created keys (`owning_module = INSTALL`) are the custom-field answer; subject list and value type shown | FR-076, FR-078 |
| ITM-T5-07 | WS-035 Kit Definitions | kit type `PHANTOM` / `STOCKED`; a phantom kit's availability is `MIN(component available ÷ required)`, computed by the backend | FR-075 |
| ITM-T5-08 | WS-027 Item × Site · WS-028 Item × Location | the operative reorder numbers and classes; the item row's values appear only as defaults on create | FR-053, FR-070 |

## 6. Out of scope

Standard-cost table semantics (valuation contract); FEFO / shelf-life enforcement (lot contract, `P2-05`);
ABC recompute (`FR-463`); variants and style matrices (`FR-443`…`445`, segment decision pending, R30
`CP-FR-012`); fitment (`FR-074`, WITHDRAWN by `D-16`); mobile scanning (`D-17` item 2).

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived for R30 `CP-FR-007` row 2; `FR-072`/`FR-073` re-homed to `P7-11` per `D-17` item 5 |
| 2026-10-23 | R31 `F-CA-012`: guards `ITM-GRD-20`…`-22` added; `ITM-OPEN-01` decided |

## 8. Invariants and scenarios

`L-5`, `L-7`, `L-12`, `D-9`, `D-10`. Scenarios `WH-SC-019`, `-020`, `-042`, `-047`, `-101`, `-130`, `-146`,
`-175`, `-203`, `-212`, `-257`…`-265`, `-267`…`-269`, `-280`, `-287`.

## 9. Open rows

| ID | Question | Default until decided | Source |
|---|---|---|---|
| ITM-OPEN-01 | `FR-073` shows availability "across every branch", but `FR-405` scopes every management query to the caller's branch-derived sites. Does the interchange enquiry show sites outside the caller's scope (quantity only), or only in-scope sites? | **DECIDED R31 (2026-10-23): default stands** — in-scope sites only (`FR-405` is the guard) | FR-073 |

## 10. Code divergences (for the build to fix)

| # | File:line | FR | What differs |
|---|---|---|---|
| 1 | `warehouse-base/.../service/whbitemsupersession/WhbSupersessionChainResolver.java:34` (consumers: `WhbItemSupersessionService`, `WhbAllocationService` only) | FR-071 | The resolver is not called by the scan service (`service/scan/`), replenishment / reorder or receipt matching in `warehouse`; `ITM-UNR-04` is not yet true — **Triage 2026-10-23: FIX-CODE** — owner `P1-03` #33 (`FR-071`), reopened |
| 2 | `warehouse-base/.../service/WhbItemSupersessionService.java:200-207` | FR-072 | `mergeStock` always refuses `409 MERGE_STOCK_POSTING_UNAVAILABLE` ("the stock writer service is not installed"), although `WhbStockLedgerWriter` (`P0-03`) exists; `ITM-T4-05` is not reachable — **Triage 2026-10-23: FIX-CODE** — owner `P7-11` #559 (open; `FR-072` re-homed by `D-17` item 5) — acceptance item added |
| 3 | `warehouse-base/.../V500016__…:38-40`, `:214` | FR-057 | The identifier row stores `uom_code` and `pack_quantity`, trigger-derived from the packaging level. The FRD says quantity is never stored on the barcode; the derived copy is a second truth to keep in step — **Triage 2026-10-23: AMEND-SPEC** — rule: quantity is owned by the packaging row; the identifier row holds a **trigger-maintained** copy of `uom_code` / `pack_quantity` that no caller writes and two AFTER triggers re-derive when the level changes (`IRR-43`). Evidence: `V500016__…:38-40`, `:214`, `:317-327`. `FR-057` amended |
| 4 | `warehouse/backend` (no interchange-availability query; WS-208) | FR-073 | No stock enquiry shows interchange / alternate availability grouped by `REGISTERED` branch; `P7-11` owns it — **Triage 2026-10-23: CARRIED** — `P7-11` #559 (`p7-11.md:59`) |
