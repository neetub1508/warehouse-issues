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
| **Module** | `warehouse-base` (FR-073 enquiry half: `warehouse-base`, WS-042 — `P8-14`) |
| **Domain baseline** | `D-9`, `D-10`, `L-5`, `L-7`, `L-12`; FRD §6.3 `FR-048`…`FR-078` (`FR-068` and `FR-074` are not in scope here; `FR-074` is WITHDRAWN by `D-16`) · `movement-post-reverse.contract.md` `MPR-T1-01` (every stock effect posts through it) |
| **Owning tasks** | `issues/p1-01.md` (items, item types, status facts) · `issues/p1-02.md` (UoM, identifiers, packaging, scan resolver) · `issues/p1-03.md` (item × site, classification, supersession, hazmat, shelf-life columns) · `issues/p1-04.md` (external refs, documents) · `issues/p3-10.md` (kits) · `issues/p3-15.md` (GS1 composite) · `issues/p7-11.md` (`FR-072`, `D-17` item 5; the MERGE_STOCK posting) · `issues/p8-14.md` (`FR-073` enquiry half, re-homed 2026-10-24 OD1) |
| **Primary tables** | `whb_items` (`V500015`), `whb_item_types` (`V500008`), `whb_uom_classes`, `whb_uoms` (`V500009`), `whb_uom_scheme_codes` (`V500076`), `whb_item_identifiers`, `whb_item_packaging_levels`, `whb_item_uom_conversions`, `whb_item_location_settings` (`V500016`), `whb_item_external_refs`, `whb_item_documents` (`V500017`), `whb_item_site_settings`, `whb_item_supplier_sources`, `whb_item_supersessions` (`V500050`), `whb_kit_definitions`, `whb_kit_components` (`V500060`), `whb_entity_attribute_values` (`V500010`) |
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
| ITM-T1-11 | `MERGE_STOCK` | Set another stock treatment · delete the link · change its type, direction or ratio | refused — `MERGE_STOCK` is terminal | `ITM-GRD-16` (`409 MERGE_STOCK_FINAL`) | `whb_item_supersessions:edit` / `:delete` | — | WS-030 | FR-072 |

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
| ITM-GRD-16 | Merge stock: posts through the single writer (`MPR-T1-01`) as ONE `SUPERSESSION_MERGE` movement per (company, site), each item balanced against the site's `VIRT-PRODUCTION` (`ITM-T4-05`), the successor carrying the value relieved from the predecessor, under the link's `quantity_ratio`. Refused `409` before anything posts when the link is already `MERGE_STOCK` (`MERGE_STOCK_ALREADY_MERGED`), is `INTERCHANGE` or bidirectional (`MERGE_STOCK_NO_DIRECTION`, WH-SC-302), the predecessor or successor is lot- or serial-tracked (`MERGE_STOCK_TRACKED_STOCK`), the predecessor has open reservations (`MERGE_STOCK_RESERVED_STOCK` — never released), any holding position is outside the caller's owners or sites (`MERGE_STOCK_OUT_OF_SCOPE`), a movement of the predecessor awaits approval (`MERGE_STOCK_PENDING_MOVEMENTS`), the reason `ITEM_SUPERSESSION/MERGE_STOCK` is not installed or is retired (`MERGE_STOCK_REASON_CODE_MISSING`), a holding site has no `VIRT-PRODUCTION` (`VIRTUAL_SET_INCOMPLETE`), or a predecessor grain cannot be valued exactly — a negative position or layer, no open cost layer, or open layers that do not hold exactly the grain's physical stock (`MERGE_STOCK_UNVALUED_STOCK`; never posted with the successor unvalued). A site whose predecessor positions changed between planning and the writer's position locks is `409 POSITION_CONTENTION` (retryable). Locks, in order: the link row (also taken by an edit, a treatment change and a delete before their finality check), then both items `FOR NO KEY UPDATE` in id order (waits for a master merge or another stock merge, never for a ledger line's foreign-key `KEY SHARE`), then per site the writer's positions and the valuation grains, all before the first post. The link is marked `MERGE_STOCK` only if every movement posted with ledger effect (a PENDING result is `409 MERGE_STOCK_NOT_POSTED`; it and any refusal roll everything back). `MERGE_STOCK` is final: delete, a treatment change and a type / direction / ratio change of a merged link are `409 MERGE_STOCK_FINAL` | the refusals above, or the writer's own; nothing changes on refusal | `L-1`, `L-2` | FR-072 — §10 row 2 |
| ITM-GRD-17 | A kit's components are active, not themselves phantom kits where the parent stocks, convertible to their UoM; versions do not overlap | `KIT_COMPONENT_IS_PHANTOM` / `KIT_COMPONENT_UOM_NOT_CONVERTIBLE` / `KIT_VERSION_OVERLAP` | `V500089` (a phantom kit holds no stock) | FR-075 |
| ITM-GRD-18 | An item document link references platform `documents` with `ON DELETE NO ACTION`; a file with a link cannot be deleted silently | `ITEM_DOCUMENT_*` on the link | FK `ON DELETE NO ACTION` (`V500017:113`) | FR-077 |
| ITM-GRD-19 | Planning numbers — reorder point, safety stock, min, max, reorder quantity, lead time — are read from **item × site** (v1) and **item × location** (v1.1); item-level values only seed a new row | `ITEM_SITE_SETTING_ALREADY_EXISTS` on a duplicate | `whb_item_site_settings` (`V500050:98`), `whb_item_location_settings` (`V500016`) | FR-053 |
| ITM-GRD-20 | An item's owner never changes; an item two owners stock is two items | `422 ITEM_OWNER_IMMUTABLE` · `ownerId` (`WhbItemValidationService.java:219`) | — | FR-048 |
| ITM-GRD-21 | The lot and serial control modes do not change (a downgrade included) while the item has any non-zero position, virtual and negative included | `422 ITEM_HAS_STOCK` · the first changed mode field (`validateControlModesUnchanged`, `WhbItemValidationService.java:251-256`) | **database trigger** (`V500027`) — the service check only names the field | FR-098 |
| ITM-GRD-22 | A conversion a posted ledger line has used is not edited or deleted; a new factor supersedes it (`ITM-T1-06`) | `409 CONVERSION_IN_USE` (`WhbItemUomConversionService.java:39`, `:49`) | database trigger | FR-055 |
| ITM-GRD-23 | UoM delete and class change ignore the unit's own `whb_uom_scheme_codes` rows when counting references. Every other FK source still refuses. Delete removes the unit's own scheme rows first (`WhbUomService.java:246`). This restores existing behaviour after the backfill; it is not a new rule | delete: `409 REGISTRY_ROW_IN_USE` (`WhbUomService.java:233-238`) · class change: `UOM_CLASS_CHANGE_REFUSED` (`WhbUomService.java:166-168`, `WhbUomValidationService.validateClassChangeAllowed`) | — | FR-056 |
| ITM-GRD-24 | A scheme row needs both a scheme and a code. A legacy scheme (`GST_UQC`, `UNECE_REC20`) is refused in the list, and so is a duplicate scheme | field-named `422 UOM_SCHEME_CODE_INVALID` / `UOM_SCHEME_CODE_DUPLICATE` on `schemeCodes[i].scheme\|code` (`WhbUomValidationService.java:36-37, 83-94`) | `uk(uom_code, scheme)` (`V500076`) | FR-056 |
| ITM-GRD-R32A-01 | A document line's flow (purchase, manufacture, sale, production issue) is allowed by the item's type flags (R32, PRD §4 "item type drives which flows apply") | `422 ITEM_TYPE_FLOW_NOT_ALLOWED` · `itemId` | `WhbItemFlowPolicy` | FR-730 |
| ITM-GRD-R32A-02 | With `warehouse-india` on and `warehouse.item.hsn_must_resolve`, **on create, on an HSN change, or when an item becomes purchasable / saleable** (never on an unrelated edit of an existing item — R32-fix F-R32CA-025), a purchasable or saleable item's HSN resolves in `whin_hsn_tax_master` at today's date; the GST rate is shown, never stored on the item | `422 HSN_NOT_IN_TAX_MASTER` · `taxClassificationCode` | `WhbTaxRateLookup` | FR-731 |
| ITM-GRD-R32A-03 | A `qc_required` item's receipt line resolves an inspection plan that inspects | `422 QC_PLAN_REQUIRED` · `itemId` | plan resolver | FR-731 |
| ITM-GRD-R32A-04 | `default_location_id` is an active, physical location or zone of the same site — not a virtual counterparty, not transit, not mobile. A retired store the row already carries is kept when unchanged (Z-005); putaway re-checks it at use | `422 DEFAULT_LOCATION_INVALID` · `defaultLocationId` | — | FR-731 |
| ITM-GRD-R32A-05 | A `WARN` / `ALLOW` negative-stock mode applies only to a non-lot, non-serial item on a `BACKFLUSH` consumption (every inbound line at a `CONSUMED` / `PRODUCTION` virtual location) posted straight through — a movement held for approval loses the context and resolves `BLOCK` at approval; the `I-6` resolver function returns `BLOCK` otherwise. Saving a `WARN` / `ALLOW` item-site setting for a tracked item is refused; a `WARN` / `ALLOW` policy row scoped to a tracked item is refused by the database (no policy API). An item later edited from untracked to tracked is not refused — the resolver answers `BLOCK` for it. The site-level `negativeStockMode` is not read by the resolver (it reads `whb_negative_stock_policies` only) | `422 NEGATIVE_STOCK_NOT_ALLOWED_FOR_TRACKED_ITEM` · `negativeStockMode` (item-site setting); policy row: `RAISE NEGATIVE_STOCK_NOT_ALLOWED_FOR_TRACKED_ITEM`, no field | DB resolver + policy trigger (`V500601`) | FR-732 |

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
| ITM-T2-04 | Read an item's PURCHASE unit default for a PO line: `GET /warehouse/inbound/purchase-orders/items/{itemId}/uom-default?counterpartyId&warehouseId&orderDate` (`orderDate` ISO date; all optional) → 200 with the resolved row, 204 when there is none. An unknown item is 404 (as `/items/{itemId}/uoms`); a named site outside the caller's branch tier is 403 before the resolver runs (as `/owners`). Ship-to is never applied on a PO. The base `GET /warehouse/masters/items/{id}/uom-defaults/resolve` (`whb_items:view`, optional `at` instant) stays the master's own lookup | `wh_purchase_orders:view` | any (read) | RG-010, #13 G2 |
| ITM-T2-05 | Edit a **system** item type (seeded by a module): only the six flow flags (`isPurchasable`, `isManufacturable`, `isSaleable`, `isProductionIssuable`, `avlRequiredDefault`, `qcRequiredDefault`) change; any other field is refused, and delete / deactivate stay locked. Each flag change is audited | `whb_item_types:edit` | active | FR-730, `ITM-GRD-R32A-01` |

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
| ITM-T4-05 | Merge stock posts (`ITM-T1-09`) | one `SUPERSESSION_MERGE` movement per (company, site) through the writer, four lines per predecessor physical position: `-q` A at its location, `+q` A at the site's `VIRT-PRODUCTION`, `+q × ratio` B at the same location (same status, LPN, duty status), `-q × ratio` B at `VIRT-PRODUCTION` (lines 3 and 4 share one rounded figure); B's receipt lines carry exactly the value the engine relieves from A, by the item's own valuation method (a grain that cannot be valued exactly is refused, `ITM-GRD-16`; an owner whose type does not post to our GL is valued on neither side); A's positions at locations whose type is a virtual counterparty (`is_virtual_counterparty`) stay; key `SUPERSESSION_MERGE:<link>:<site>`; catalogue rows in place in `V500050`, reason context bound by `V500084`; link `stock_treatment` → `MERGE_STOCK` in the same transaction. B gets a fresh cost layer dated at the merge, so its age restarts there (as `MASTER_MERGE` and work-order output) — not an ageing defect | supersession service → writer | FR-072 |
| ITM-T4-06 | A stock enquiry finds the item short (WS-042) | it shows the interchange / alternate parts ("not in stock — 2 available as `<interchange>`") with availability across every branch, grouped by each site's **`REGISTERED` branch at today**; a shared site appears once tagged with the branches it serves; a *sister* is a site with a different `REGISTERED` branch, so a site is never its own sister | stock-enquiry query service | FR-073 — §10 row 4 |
| ITM-T4-07 | A movement line or position carries a catch-weight item | `secondary_quantity` + `secondary_uom_id` are columns on the line and the position from v1 (v1 writes null); `is_catch_weight` on the item | columns (`V500030:333`, `V500015:163`) | FR-065 |
| ITM-T4-08 | An LPN, warehouse, location or party is labelled or exchanged | `sscc` on the LPN and `gln` on warehouse, location and counterparty are v1 columns | columns (`V500018`, `V500012`, `V500013`, `V500011`) | FR-064 |
| ITM-T4-09 | A hazmat item is shipped or printed | the hazmat block — UN number, class, packing group, proper shipping name, subsidiary classes — is read from the item (`hazmat_*`, `V500015`) | consumers | FR-067 |
| ITM-T4-10 | A UoM is created or edited with `schemeCodes` (#20 settlements 3 and 6) | the two scalars stay required (`ITM-GRD-11`) and mirror to `GST_UQC` / `UNECE_REC20` rows in the same transaction. The null-scalar delete branch is defensive and cannot be reached through the API. `schemeCodes` absent or `null` leaves other schemes untouched; `[]` removes them. An overwrite is recorded by `trackChanges` as `schemeCodes.<SCHEME>`. Permissions: POST is under `whb_uoms:create` and PUT under `whb_uoms:edit`. No new permission (this is the #20 settlement 4 wording to ratify) | `WhbUomService.syncSchemeCodes` | FR-056 |

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
| ITM-T5-09 | WS-072 PO modal — unit default, date → instant | the UI sends the order **date**; the service reads the default at the site's local midnight (`whb_warehouses.timezone`), or at **now** when the date is the site's today (a default the item gained earlier today starts after midnight). No site: a UTC day by the same rule. No date: now | R22 §1.3 rule 1, RG-010 |
| ITM-T5-10 | WS-072 PO modal — pinned / unpinned unit | a line's unit is **pinned** when the user picks it or the saved line carries it; the default never overwrites a pinned unit. An unpinned line takes its item's default and follows supplier, site and date changes. A new item, or an owner change, clears and unpins the unit. Picking the unit that is already pre-filled fires no change and leaves the line unpinned (noted for ratification) | RG-010, #13 G2 |
| ITM-T5-11 | WS-072 PO modal — convertible units only | the pre-fill offers only a unit that converts to the item's base unit at the read instant (FR-143): the endpoint answers 204 for a non-convertible default (the same `convertibleUnits` source as `/items/{itemId}/uoms`), and the modal pre-fills only a code present in the line's unit list | FR-143, RG-010 |
| ITM-T5-12 | WS-072 PO modal — pending / failed lookup | a supplier, site or date change blanks every unpinned line's unit until the new lookup answers; a pending lookup leaves it blank, a failed lookup leaves it blank (required-unit validation then asks the user). Pinned lines are never touched | RG-010, #13 G2 |
| ITM-T5-13 | WS-027 Item × Site — default store picker | `GET /warehouse/masters/item-site-settings/location-options?warehouseId&search&limit` under `whb_item_site_settings:view` (a site outside the caller's branch tier is 403); empty until a site is chosen; offers only active locations the save accepts (`ITM-GRD-R32A-04`), narrowed before the cap | FR-731, `ITM-GRD-R32A-04` |
| ITM-T5-14 | WS-034 Units of Measure — scheme sub-grid | the view modal lists every scheme row. In the Add/Edit modal, the legacy rows are read-only (they are edited in their own fields) and other schemes can be added and removed. Edit mode while the read is pending shows Loading. Edit mode when the read failed and nothing is cached shows an in-modal error and offers no scheme editing; a save then leaves the stored scheme rows untouched. No new screen, menu, permission, grid, filter, cache or export column. Mobile: DEFERRED (`D-17` item 2(b)). **#20 settlement 5 wording:** the view and edit modals read the full list (`WhbUomQueryService.getSchemeCodes`, through `getById`). `codeFor(uomCode, scheme)` is the per-scheme API for future single-scheme readers. It reads only the side table, returns null on a miss and never falls back to the scalars. It has no production consumer in this round | FR-056 |

## 6. Out of scope

Standard-cost table semantics (valuation contract); FEFO / shelf-life enforcement (lot contract, `P2-05`);
ABC recompute (`FR-463`); variants and style matrices (`FR-443`…`445`, segment decision pending, R30
`CP-FR-012`); fitment (`FR-074`, WITHDRAWN by `D-16`); mobile scanning (`D-17` item 2).

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived for R30 `CP-FR-007` row 2; `FR-072`/`FR-073` re-homed to `P7-11` per `D-17` item 5 |
| 2026-10-23 | R31 `F-CA-012`: guards `ITM-GRD-20`…`-22` added; `ITM-OPEN-01` decided |
| 2026-10-24 | #13 G2 (RG-010 PO pre-fill): `ITM-T2-04`, `ITM-T5-09`…`-12` added. **Owed, not made here:** `DATA-MODEL.md:816` still names the UoM-default scope column `channel_id`; settled S1 / NFR-OPEN-03 uses `ship_to_address_id` — amend `DATA-MODEL.md` |
| 2026-10-25 | R32 (`D-20` items 1, 2-13a, 2-14): guards `ITM-GRD-R32A-01`…`-05` — item-type flow flags and the manufacturing types, GST rate shown from the HSN master, `make_or_buy`, `qc_required`, default store, negative stock restricted to non-tracked backflush (`issues/p1-03.md` §R32) |
| 2026-10-25 | `ITM-GRD-R32A-02` | **R32-fix (`F-R32CA-025`).** The HSN check runs on create, HSN change or becoming purchasable / saleable only; unrelated edits of existing items are not refused | R32 review |
| 2026-10-25 | #33 lane A S3 (`cd7f3480c3`): `ITM-GRD-R32A-04` states the active / non-mobile / non-transit rule and the Z-005 retired-but-unchanged exception; `ITM-GRD-R32A-05` names the real refusal field (`negativeStockMode`; the policy guard is a database raise), the approval-path exclusion, the untracked → tracked edit and the unread site-level mode; `ITM-T2-05` (system item-type flow-flag edit) and `ITM-T5-13` (default-store picker) added |
| 2026-10-25 | R31 P1-02 #20 S6: `whb_uom_scheme_codes` added; `ITM-GRD-23` (own-row exclusion on delete / class change), `ITM-GRD-24` (scheme refusals), `ITM-T5-14` (WS-034 sub-grid; the #20 overlay named it `ITM-T5-13`, which #33 took first, so it is numbered `-14`); `ITM-T4-10` (T1 / T4 behaviour, #20 settlements 3 and 6); #20 settlement 5 wording corrected (`codeFor` has no production consumer) |

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
| 2 | `warehouse-base/.../service/WhbItemSupersessionService.java:200-207` | FR-072 | `mergeStock` always refuses `409 MERGE_STOCK_POSTING_UNAVAILABLE` ("the stock writer service is not installed"), although `WhbStockLedgerWriter` (`P0-03`) exists; `ITM-T4-05` is not reachable — **Triage 2026-10-23: FIX-CODE** — **FIXED 2026-10-24 by `P7-11` #559**: `mergeStock` posts one `SUPERSESSION_MERGE` movement per site through `WhbStockLedgerWriter`; `ITM-T4-05` reachable (classic 906609a361, 7a7e699a38, 72e9dc87e2) |
| 3 | `warehouse-base/.../V500016__…:38-40`, `:214` | FR-057 | The identifier row stores `uom_code` and `pack_quantity`, trigger-derived from the packaging level. The FRD says quantity is never stored on the barcode; the derived copy is a second truth to keep in step — **Triage 2026-10-23: AMEND-SPEC** — rule: quantity is owned by the packaging row; the identifier row holds a **trigger-maintained** copy of `uom_code` / `pack_quantity` that no caller writes and two AFTER triggers re-derive when the level changes (`IRR-43`). Evidence: `V500016__…:38-40`, `:214`, `:317-327`. `FR-057` amended |
| 4 | `warehouse/backend` (no interchange-availability query; WS-042) | FR-073 | No stock enquiry shows interchange / alternate availability grouped by `REGISTERED` branch; `P7-11` owns it — **Triage 2026-10-23: CARRIED** — owner `P8-14` #575 — re-homed 2026-10-24 (OD1, decision-p7-11-12; was `P7-11` #559) |
