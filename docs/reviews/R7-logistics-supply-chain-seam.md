# Lens R7 — the logistics / supply-chain seam

**Question this lens exists to answer:** what must `warehouse-base` commit to in **v1** so that a
logistics/TMS module, a supply-chain/procurement module, and N future vertical adapters can be built
later **without ever editing `warehouse-base`**?

| | |
|---|---|
| **Date** | 2026-09-01 |
| **Live codebase** | `/Users/bbhushan/work/git/workspace/classic`, branch `main`, tree clean at start |
| **Prior art read** | `classic-issues/logistics/docs/TMS/` (**13** `.md` files — computed `ls *.md \| wc -l`), `classic-issues/supply-chain-core/docs/SCC_MODULE_ISSUES_ANALYSIS.md`, `classic-issues/warehouse-core/docs/WAREHOUSE_CORE_ISSUES.md` |
| **Sibling reports read** | `R1-codebase-reality.md` (`C-`), `R2-tier1-wms-audit.md` (`T-`), `R3-erp-midmarket-audit.md` (`E-`), `R4-fulfilment-3pl-audit.md` (`F-`, §3 and §4 in full), `R5-standards-industry-ops.md` (`S-`) |
| **Method** | reading and `grep` only. No `mvn`/`npm`/`tsc` (Docker-only build, CLAUDE.md). Every count below was computed with a command; anything not computed is marked `UNVERIFIED` or carries `?` |
| **Decided architecture, not re-litigated** | `warehouse-base` (`ai.warehousebase`) · `warehouse` (`ai.warehouse`) · `warehouse-adapter-<vertical>` · `warehouse-3pl` · `warehouse-india`. Flyway **V500000–V549999**. `accessories` inventory permanently separate. `accounting-base`/`accounting` owns the GL |

**Honesty rules applied.** Every claim about the live codebase carries `file:line`. Every claim about
the prior art cites the file. Competitor facts I could not confirm carry `?`. I did not modify
anything outside this file.

---

## 0. Headline — the eight conclusions this lens is confident about

1. **The TMS prior art contains no item identity at all.** `grep -n "item_id\|product_id\|sku"` over
   the whole 2,300-line `TMS_Functional_Document.md` returns **zero hits**. `tms_consignment_items`
   (`:648-674`) carries `description VARCHAR(500)`, a captured `hsn_code` and a captured `uom_code`,
   and nothing that identifies *what* is in the box. **A TMS designed to that document is
   structurally incapable of posting a stock movement.** That is not a defect — it is the boundary,
   and it is the strongest available evidence that the warehouse↔logistics seam is real and clean.
   (`G-001`)

2. **But that same document reinvents four private stock ledgers inside the TMS**, because a fleet
   business owns things: `tms_equipment_inventory` (`:483-500` — serialised tarpaulins, chains, GPS
   devices with `condition` and `availability_status`), `tms_tyres` (`:1235-1264` — with
   `tyre_status IN_STOCK/FITTED/REMOVED/RETREAD/SCRAPPED`, which is a stock-status vocabulary),
   Fleetable's spare-parts inventory (`02_Fleetable.md:105-106`), and fuel. **Every one of those
   belongs in the warehouse ledger with a different `item_type`, not in a TMS table.** (`G-002`…`G-005`)

3. **The previous attempt at this exact seam failed by making warehouse structurally FK-dependent on
   a supply-chain module.** `SCC_MODULE_ISSUES_ANALYSIS.md:§4.4` records the FK reference counts from
   warehouse-core/warehouse-base *into* `scc_*`: units_of_measure 26, carriers 18, suppliers 13,
   vehicles 8, customers 5, brands 5, customer_addresses 4, hsn_tax_master 3, gst_state_codes 1,
   compliance_documents 1 — **84 references, summing their own numbers**. It also records the reverse
   rot: warehouse migrations referencing `scc_items`, `scc_drivers`, `scc_alert_rules`,
   `scc_alert_history` — **tables that never existed**. That is not a seam, it is a merge with a
   module boundary drawn on top. **Do not repeat it.** (`G-025`, `G-026`)

4. **The supplier master is the load-bearing question and the answer is "warehouse-base owns a
   counterparty, logistics owns its own, and an external-refs table is the only join."** The live
   repo has no shared party master (R1 §7, `C-035`): `asset_vendors` is assets-owned
   (`assets/.../V60056:3-38`), automotive `customers`/`companies` are automotive-owned, accessories
   receiving has **no supplier field at all** (`accessories/.../dto/request/inventory/StockReceiptRequest.java:23-51`).
   The copy target already exists and is recent: `acc_company_external_refs`
   (`accounting-base/.../V600001__Create_acc_companies_and_external_refs.sql:204-231`), whose own
   comment states the rule — *"source_module is an OPAQUE STRING here, not an FK"* (`:193`). (`G-027`…`G-031`)

5. **The open-registry pattern already has a live, documented precedent in this repo, and it must be
   applied thirteen times, not six.** `acc_reason_codes.context` carries **no CHECK constraint,
   deliberately**, and the migration says why: *"It is a CATALOGUE, not an enum … both must be a seed
   INSERT rather than an ALTER of a CHECK in accounting-base"*
   (`accounting-base/.../V600002__Create_acc_reason_codes.sql:22-26`). The counter-example is equally
   live: `widget_definitions.chk_module` has been widened by DROP/ADD **three times** — 3 values at
   `platform/.../V234__Create_dashboard_system_tables.sql:36`, 5 at `V276:10`, 7 at `V557:18` — and
   still does not allow `warehouse`, `accounting` or `logistics`. §5 names thirteen columns that must
   be catalogues. (`G-053`…`G-066`)

6. **There is no outbox anywhere in this repository.** `grep -rli "outbox"` over `platform`,
   `accounting-base`, `accounting`, `dealer`, `automotive`, `services`, `assets` returns **0 files**.
   R4 `F-086`/`F-012` require one; I additionally require `whb_outbox_subscriptions`, because
   **logistics may be a separate deployable** and an in-process `List<T>` registry cannot reach it.
   This is the one place where I extend R4 rather than restate it. (`G-045`, `G-046`)

7. **The repo already contains three transport-shaped surfaces and a fourth is about to be built.**
   `field-service` has a real GPS trip model — `job_trips` with polyline, `distance_method_used` and
   `job_track_points` with accuracy/speed/heading
   (`field-service/.../V80007__Create_job_trips_and_track_points.sql:13-80`); `services` has doorstep
   pickup/drop with a driver and a seven-state ladder
   (`services/.../V40197__Create_service_pickup_drop_tables.sql:15-60`); `automotive` has a gate-event
   webhook routed to verticals by a `List<IBoomBarrierHandler>` bean collection
   (`automotive/.../controller/BoomBarrierWebhookController.java:44-48`); `dealer` has PDI vehicle
   movements. **`log_trips` + `log_gps_pings` will be the third GPS trip model in the monorepo.** Say
   so before it is built, not after. (`G-020`, `G-084`)

8. **The `filterUtils.ts` allowlist and `CacheConfiguration.java` are platform *source files*, not
   data.** `COMMON_FILTER_CONFIGS` is a TypeScript `const` at
   `platform/frontend/src/utils/filterUtils.ts:346` with **210 scopes** (computed
   `grep -c "^  [A-Z_0-9]*: {"`). Therefore the loose-coupling test can only ever be *"zero commits to
   `warehouse-base`"* — **never** *"zero commits to `platform`"*. Any contract that claims otherwise
   is false on day one. State the caveat in the contract itself. (`G-047`)

---

# §1 — The TMS / logistics capability map, and what touches stock

Sourced from the 13 prior-art files plus general knowledge. **Touches stock** is the column this lens
exists for: `NO` = never changes a quantity, `INDIRECT` = drives timing/valuation of a movement
someone else posts, `YES` = must post through the movement port or it is a second stock truth.

## 1.1 Order-to-trip planning

| # | Capability | Evidence in prior art | Touches stock | Note |
|---|---|---|---|---|
| 1 | Transport order / consignment (LR / GR) | `TMS_Functional_Document.md:528-620` | INDIRECT | 1:1 with a warehouse shipment; the transport view of the same box |
| 2 | Consignment items with HSN + UoM | `:648-674` | **NO — and that is the finding** | no `item_id` anywhere; free-text `description` |
| 3 | Order intake: portal, bulk CSV, API, e-comm plugin | `01_Shipsy.md:59`; `05_Delhivery_OS.md:14` | NO | |
| 4 | Load building / consolidation (manifest) | `:707-738` | INDIRECT | groups shipments; does not change quantity |
| 5 | FTL / PTL load type | `:565` | NO | |
| 6 | Indent / vehicle requisition | `:742-786` | NO | demand for a *vehicle*, not for stock |
| 7 | Spot bidding / reverse auction | `:789-852`; `09_SuperProcure.md` | NO | |
| 8 | Carrier allocation (SOB, round-robin, AI) | `:763` `allocation_method`; `08_Fretron.md` | NO | |
| 9 | Route & stop master | `:346-380` | NO | |
| 10 | Route optimisation | `01_Shipsy.md:30-33` (200+ constraints); `03_LogiNext.md` | NO | |
| 11 | Trip creation and dispatch | `:854-925` | **YES** | dispatch is `TRANSFER_DEPART` when the goods are ours |
| 12 | Multi-leg / hub-and-spoke (FMLM) | `01_Shipsy.md:27` | **YES** | each leg is a transit-to-transit movement |
| 13 | Last mile, delivery windows | `TMS_Sales_Feature_Overview.md` "Dispatch & Route Execution" | INDIRECT | |
| 14 | Backhaul planning | `TMS_Sales_Feature_Overview.md` | NO | |

## 1.2 Masters

| # | Capability | Evidence | Touches stock | Note |
|---|---|---|---|---|
| 15 | Vehicle master + vehicle types | `:142-210` | **INDIRECT — dual identity** | a vehicle is a logistics *asset* and a warehouse *location* (§2.4) |
| 16 | Driver master + KYC | `:211-252` | INDIRECT | a driver owns a van's stock (`assigned_user_id`) |
| 17 | Carrier master + service areas | `:295-345` | NO | but see the movable boundary, §2.6 |
| 18 | Customer master (consignor / consignee) | `:253-294` | NO | logistics' own; not warehouse's |
| 19 | Branch / hub master | `:101-141` | **CONTESTED** | a hub that *stores* is a warehouse (§2.5) |
| 20 | **Equipment types + inventory** (tarps, chains, GPS units) | `:465-500` | **YES** | serialised stock reinvented in a TMS (`G-002`) |
| 21 | Payment modes, expense types | `:444-464`, `:504-523` | NO | |

## 1.3 Rating, contracts and procurement of transport

| # | Capability | Evidence | Touches stock | Note |
|---|---|---|---|---|
| 22 | Customer rate cards | `:382-414` | NO | |
| 23 | Carrier rate cards | `:415-443` | NO | |
| 24 | Freight rating engine, lane rates | `01_Shipsy.md:19` | NO | |
| 25 | Rate-card versioning + expiry alerts | `01_Shipsy.md:19` | NO | mirrors R4 `F-014` for 3PL rate cards — **two rating engines, same shape**; do not share code, do share the *pattern* |
| 26 | Indent → tendering → allocation to transporters | `:742-852` | NO | |

## 1.4 Execution and visibility

| # | Capability | Evidence | Touches stock | Note |
|---|---|---|---|---|
| 27 | Yard / in-plant: gate, dock, weighment, TAT | `:990-1040` | **CONTESTED** | the door is warehouse, the yard is logistics, the gate is neither (§2.3) |
| 28 | GPS tracking (4 methods: GPS/SIM/FASTag/App) | `:1685-1704`; `04_NaaviQ.md` | NO | third GPS model in the monorepo (`G-020`) |
| 29 | FASTag transactions | `:1705-1728` | NO | |
| 30 | Geofence + milestone alerts | `:1729-1762` | INDIRECT | may auto-post `TRANSFER_ARRIVE` — needs `actor_type=DEVICE` |
| 31 | ePOD: signature, photo, GPS, OTP | `:1043-1082` | **NO — a document, never a movement** | agrees with R4 §4.4 |
| 32 | **Partial delivery / damaged / short packages** | `:1068-1070` (`packages_delivered`, `packages_damaged`, `packages_short`) | **YES** | this is `TRANSIT_LOSS` with a reason code |
| 33 | NDR with reason codes and a response clock | `:1084-1110` | INDIRECT | R4 `F-044` puts the NDR in `warehouse` v1 |
| 34 | RTO — auto reverse consignment | `:1111` auto-trigger | **YES** | R4 `F-046`: the biggest single reverse stock stream |
| 35 | COD collection and remittance reconciliation | `:604-607`, `:1073-1075` | NO (money) | R4 `F-045` |
| 36 | Detention / demurrage / TAT charge | `:1020-1023` (`total_tat_minutes`) | **SPLIT** | the clock is warehouse, the charge is logistics (§2.7) |
| 37 | Control tower / exception dashboard | menu `:22`; `01_Shipsy.md:79` (Atlas) | NO | |

## 1.5 Fleet and driver

| # | Capability | Evidence | Touches stock | Note |
|---|---|---|---|---|
| 38 | Vehicle documents + expiry alerts | `:1132-1161` | NO | |
| 39 | Vehicle maintenance | `:1162-1195` | **YES if parts are consumed** | maintenance issues spares → a movement |
| 40 | Fuel log (retail / card) | `:1196-1231` | NO as designed | **but depot bulk fuel is stock and the prior art has no depot tank** (`G-005`) |
| 41 | **Tyre management** | `:1232-1268` | **YES** | `tyre_status IN_STOCK/FITTED/REMOVED/RETREAD/SCRAPPED` is a stock lifecycle (`G-003`) |
| 42 | Vehicle EMI | `:1269-1310` | NO | |
| 43 | Challans / penalties | `:1311-1339` | NO | |
| 44 | **Fleet spare-parts inventory** | `02_Fleetable.md:105-106` | **YES** | absent from `TMS_Functional_Document.md`; present in the vendor it copies from |
| 45 | Driver documents, attendance, leave, salary, advances | `:1340-1444` | NO | overlaps platform HR (`G-085`) |

## 1.6 Compliance

| # | Capability | Evidence | Touches stock | Note |
|---|---|---|---|---|
| 46 | E-way bill register + **Part-B vehicle update** | `:1449-1492`; design principle `:12` | INDIRECT | reads the movement; R5 §2.1 lists the eight fields it needs |
| 47 | E-invoice register | `:1493-1515` | INDIRECT | R5 `S-025`: an inter-state transfer invoice needs an IRN |
| 48 | Document vault | `:1516-1535` | NO | |

## 1.7 Freight money

| # | Capability | Evidence | Touches stock | Note |
|---|---|---|---|---|
| 49 | Customer freight invoices with GST | `:1540-1597` | NO | |
| 50 | Carrier bills + **freight audit / rate variance** | `:1598-1644`; `01_Shipsy.md:41` | NO | |
| 51 | Trip settlement / P&L | `:1645-1680` | NO | |
| 52 | Driver settlement | menu `:70` | NO | |
| 53 | **Landed cost — freight capitalised into stock value** | *absent from all 13 prior-art files* | **YES** | R4 `F-088` value-only movement; R5 §4.3. The prior art never connects freight to inventory cost (`G-023`) |
| 54 | Margin analysis, carrier scorecard | `:2209+`; `01_Shipsy.md` | NO | |

**Count: 54 capabilities, tallied from the tables above — 9 `YES` (including "yes if parts are
consumed"), 9 `INDIRECT`, 3 `CONTESTED`/`SPLIT`, 33 `NO` (including the two qualified `NO`s at rows 40
and 35).** Those counts are of the table above, which I built; they are not a claim about any vendor's
product. Note that row 40's `NO as designed` becomes `YES` the moment a depot tank exists — which is
`G-005`.

---

# §2 — The boundary, table by table and event by event

## 2.1 The rule — stated once, then applied mechanically

R4 §4.1 states it as:

> *"Warehouse owns the goods while they are stationary and inside a boundary. Logistics owns them
> while they are moving between boundaries. The dock door is the boundary, and it is a warehouse
> resource."*

**I do not contradict that; I sharpen it, and I say why.** R4's rule is a *physical* rule. It gives
the right answer for a pallet and the wrong answer for four things a fleet business actually owns: a
tarpaulin on a moving truck (moving → logistics by R4's rule, but it is van stock), a tyre fitted to a
vehicle, diesel in a depot tank, and a spare part in the transport store. It also cannot decide the
gatehouse, because a gate event is a *device*, not a place. The refinement:

> **Warehouse owns *how much of what, whose, in what condition, and where*. Logistics owns *which
> vehicle, on whose journey, at what freight cost*. If a fact answers the first question it is a
> warehouse ledger fact, even while the goods are moving; if it answers the second it is logistics,
> even while the vehicle is parked. R4's dock door remains exactly right for the *physical handover*;
> the *ledger* boundary is the movement port, and the port never moves.**

The two rules agree on every row of R4 §4.2. Mine additionally decides equipment, tyres, fuel, fleet
spares, the gatehouse and hubs, which R4's does not reach. Every borderline case in §2.3 is resolved
by applying it mechanically and showing the working.

## 2.2 Table allocation — extending R4 §4.2

R4's table stands. These are the rows R4 did not have, plus the ones I would annotate. Prefixes follow
R4 (`whb_` base, `wh_` app, `wh3pl_`, `log_` logistics); see `G-079` on the three-way prefix conflict
between the sibling reports.

| Concern | `warehouse-base` | `warehouse` | future `logistics` | Rule that decides it |
|---|---|---|---|---|
| **The vehicle** | `whb_locations` row, `location_type='VEHICLE'`, linked by xref | — | `log_vehicles` (RC, insurance, fitness, PUC, permit, odometer) | dual identity: *where stock is* vs *which asset it is* |
| **The tyre** | `whb_items` (`item_type='TYRE'`), `whb_serials` | receipt / issue / scrap screens | `log_tyre_fitments (stock_serial_id, vehicle_id, position, fitted_odo, removed_odo, retread_count)` | on the shelf = quantity; on the axle = a fitment |
| **Transport equipment** (tarps, chains, straps, GPS units) | `whb_items` (`item_type='RETURNABLE_EQUIPMENT'`), `whb_serials` | issue / return screens | `log_trip_equipment (trip_id, reservation_id)` — a **reservation** against warehouse stock | it has a quantity and a condition ⇒ stock |
| **Depot bulk fuel** | `whb_items` (`item_type='FUEL'`, UoM litres), a tank is a `whb_location` | dip readings as counts | `log_fuel_issues` referencing the movement | held in a tank we own ⇒ stock. Retail card fuel ⇒ logistics expense, no movement |
| **Fleet spare parts** | ledger | receive / issue | `log_maintenance_parts (maintenance_id, movement_id)` | stock consumed by a work order — identical to `services` job parts |
| **The hub** | `whb_warehouses` with `is_physical=true` **if it stores overnight** | — | `log_hubs` **if it only cross-docks within one trip** | "does stock ever rest here unattributed to a trip?" (§2.5) |
| **The gate** | — | `wh_gate_events` (optional) | posts arrival/departure | a gate event is a **device actor**, not a place (§2.3) |
| **Detention clock** | lifecycle timestamps on the movement (`F-074`) | `wh_dock_appointments.arrived_at / released_at` | `log_detention_charges` | the clock is ours because the door is ours; the money is theirs |
| **Landed cost / freight capitalisation** | `LANDED_COST_APPLY` value-only movement (`F-088`) | apportionment basis on the receipt | `log_freight_charges` is the source document | the *charge* is transport; the *effect on stock value* is warehouse |
| **Incoterm / title transfer** | `whb_movement_lines.owner_id` answers *whose* | `wh_transfer_orders.ownership_transfer_point`, `wh_receipts.ownership_transfer_point` | reads it | *when* title passes is a commercial term on the document, not a property of the movement |
| **Returnable packaging / pallet pool** | `whb_items` (`item_type='PACKAGING'`) + a per-counterparty balance | issue / return / reconcile | `log_pallet_exchanges` at a stop | R4 `F-060` covers packaging as stock; the **counterparty balance** is new (`G-024`) |

## 2.3 Borderline cases, worked

**Dock doors → `warehouse`.** Agreed with R4. `wh_docks`, `wh_dock_appointments`.
*But see `G-014`: R4 places `F-080` at v2 and I argue the schema is v1.*

**Yard (beyond the door) → `logistics`.** Agreed with R4 §5.5 #12. **With one condition:** a trailer
parked in the yard *holding stock* must be a `whb_locations` row of type `TRAILER`, or that stock is
off the books while it sits there — the exact failure R4 §4.3 identifies for in-transit. Yard *slot
management* is logistics; a yard slot *holding a stock-bearing trailer* is a warehouse location. The
prior art proves the case is real: `tms_yard_entries` carries `dock_number`, `loading_start_time`,
`tare/gross/net_weight_kg` (`TMS_Functional_Document.md:1005-1017`) — a weighbridge measures the
stock, not the yard.

**Gatehouse → neither. It is a device integration.** The rule: a gate event answers neither *how much
of what* nor *which journey* — it answers *which vehicle crossed a line at what time*, and both
modules want it. The repo already solved this shape once: `BoomBarrierWebhookController` takes
`List<IBoomBarrierHandler>` and routes one webhook to whichever vertical claims the API key
(`automotive/.../controller/BoomBarrierWebhookController.java:44-48`, `:69`, `:168-175`). **Copy that
exact shape:** a gate event is published to a handler list; `warehouse` claims it to stamp a dock
appointment, `logistics` claims it to stamp a trip departure, and neither owns the gate. (`G-016`)

**Staging → `warehouse`.** A `whb_location_types` row (`STAGING`), `is_stock_holding=true`. Stock in
staging is picked but not despatched; it must be countable and it must not be allocatable to a second
order.

**Trailer / vehicle as a location → both, by two rows joined through an xref.** The one design
decision in this section that must be taken now. A truck is:
- `whb_locations (location_type='VEHICLE', is_mobile=true, assigned_user_id=<driver>)` — so stock can
  sit on it, be counted on it, and be short-picked from it;
- `log_vehicles` — so it can have an RC, an insurance expiry, a tyre and an odometer.

**Neither is the other's master.** They are joined by `whb_location_external_refs (source_module,
external_id, location_id)`, the `acc_company_external_refs` shape. Consequences that fall out and are
all things customers ask for: van stock (R2 `T-080`) is the same object as a delivery vehicle's load;
a driver's shortage is a stock adjustment against a location with an owner; and a fleet business
with no warehouse still works, because `log_vehicles` has no FK to `whb_locations`. (`G-017`)

**In-transit stock ownership → `warehouse` ledger, `logistics`-posted.** Agreed with R4 §4.3 in full.
**One addition R4 does not make:** the `IN_TRANSIT` location tells you *where*; `owner_id` tells you
*whose*; neither tells you *when title passed*. Under EXW/FCA the goods are ours the moment they leave
the supplier's dock (R5 §4.5). Without `ownership_transfer_point` on the source document, a
period-end goods-in-transit figure is a guess. Column in v1, behaviour in v2. (`G-018`)

**Shipment vs consignment vs load vs trip → four objects, three cardinalities.** The prior art
confirms the shape: `tms_consignments.manifest_id`, `.trip_id`, `.indent_id` (`:594-596`);
`tms_manifests.trip_id` (`:725`).

| Object | Owner | What it is | Cardinality |
|---|---|---|---|
| `wh_shipments` | `warehouse` | *what is in the box* — cartons, weights, dims, destination | 1 per outbound pack |
| `log_consignments` | `logistics` | *the transport contract for that box* — LR/GR, freight, consignor/consignee, route | **1:1** with a shipment, and **optional** — a third-party parcel has none (R4 §4.5) |
| `log_manifests` / loads | `logistics` | consignments grouped for one vehicle | N consignments : 1 manifest |
| `log_trips` | `logistics` | the vehicle's journey | N manifests : 1 trip |

**ASN → `warehouse` owns the document; the supply-chain module owns the supplier who sent it.**
An ASN is a *receipt expectation* — it drives dock appointments, pre-allocation and cross-dock. It is
not a transport object (nobody in the 13 TMS files models one). `wh_asns` + `wh_asn_lines`, R2 `T-091`
places them at v1.1.

**Packing vs loading → packing is `warehouse`, loading is `logistics`.** Packing produces cartons/LPNs
with dims and weights; loading decides which carton goes on which vehicle in what sequence with what
axle load. The load plan references `whb_lpns` by id. The seam is the LPN, and R4 `F-064` already
makes the LPN a v1 ledger object.

**ePOD vs goods receipt → different objects, and the difference depends on the destination.**

| Destination | ePOD | Stock movement |
|---|---|---|
| A customer | yes | **none** — the stock left at despatch (R4 §4.4) |
| Our own branch / warehouse | yes | **`TRANSFER_ARRIVE`** — and a partial arrival is fewer lines |
| A 3PL client's site | yes | `OWNER_CHANGE` or `TRANSFER_ARRIVE` depending on the contract |

R4 states the first row. The second is the one that matters for an inter-branch business and it is
worth stating explicitly, because an implementer who reads only "delivery is not a movement" will
build inter-branch transfers that never arrive. (`G-019`)

## 2.4 The dual-identity rule, generalised

Three objects now have two identities across the seam: **vehicle** (location ↔ asset), **tyre** (stock
serial ↔ fitment), **hub** (warehouse ↔ stop). The rule that makes this safe rather than a
synchronisation problem:

> **The physical thing has exactly one row per *question it answers*. The rows are joined by an
> external-refs table, never by a foreign key, and neither side may require the other to exist.**

Test: delete the logistics module. Does `warehouse` still work? (Yes — locations remain, xrefs go
stale but resolve to null, the display resolver falls back to the raw external id.) Delete the
warehouse module. Does `logistics` still work? (Yes — `log_vehicles` has no FK into `whb_*`.) Any
design where one answer is "no" has an FK pointing the wrong way. (`G-021`)

## 2.5 The hub, resolved

`log_hubs` in R4 §4.2 is the one row I would qualify. Apply the rule: does stock ever **rest at a hub
unattributed to a trip**? If yes, someone will eventually count it, find a discrepancy, and have
nowhere to post the adjustment — so it is a `whb_warehouses` row (possibly with
`is_physical=true, has_picking=false`). If a hub only ever cross-docks *within* a single trip, the
stock never leaves `IN_TRANSIT-<trip>` and the hub is a `log_route_stops` row.

**Recommendation: make it configurable per hub, in v2, with the default being "warehouse".** The
column is `log_hubs.stock_holding_warehouse_id UUID NULL`. Non-null ⇒ arrivals post
`TRANSFER_ARRIVE`; null ⇒ the trip's transit location persists across the stop. (`G-022`)

## 2.6 The boundaries that will move — R4 §4.5, extended from one to five

R4 names carriers as *"the one boundary that will move"*. Applying the same test — *does this object
exist in `warehouse` v1 only because logistics does not exist yet?* — gives **five**, not one:

| Object | In `warehouse` v1 because | Moves to `logistics` in | R4 finding |
|---|---|---|---|
| `wh_carriers`, `wh_carrier_services`, `wh_carrier_accounts` | v1 ships parcels | v2 | `F-036`, R4 §4.5 |
| `wh_shipment_tracking_events` | third-party parcel tracking | v2 for own fleet; stays for third-party | `F-043` |
| `wh_shipment_ndrs` | NDR has a response clock and a warehouse queue | v2 for own fleet | `F-044` |
| `wh_rto_consignments` | RTO is an inbound stock stream | never fully — the *receipt* stays | `F-046` |
| `wh_cod_remittances` | COD reconciliation must exist before logistics | v2 | `F-045` |

**All five obey R4's rule 2 verbatim: reference by a stable code resolved through a service, never by
an FK from the referencing table into the relocatable one.** Applying that rule to one object and not
the other four is how the move stops being cheap. (`G-013`)

## 2.7 The events that cross — additions to R4 §4.4

R4 §4.4 lists five `warehouse → logistics` events and nine `logistics → warehouse` calls. I would add:

**`warehouse → logistics`**

| Event | Payload essentials | Why |
|---|---|---|
| `stock.reservation.created` / `.released` | reservation id, holder quad, item, qty, expiry | logistics plans a trip against reserved stock before it is picked (`G-042`) |
| `equipment.issued_to_trip` | serial, trip ref, expected return | tarps and chains go out and must come back |
| `dock.appointment.detention_started` | appointment, arrived_at, free-time expiry | the charge is logistics', the clock is ours |

**`logistics → warehouse`**

| Call | Mechanism | Why |
|---|---|---|
| gate-in / gate-out | handler list (§2.3), then `PATCH wh_dock_appointments` | the detention clock and dock-to-stock |
| equipment returned | `POST /movements` `EQUIPMENT_RETURN` | otherwise the equipment ledger drifts, exactly as `tms_equipment_inventory` would |
| tyre fitted / removed | `POST /movements` `ISSUE_TO_ASSET` / `RETURN_FROM_ASSET` | the fitment is logistics', the stock effect is ours |
| freight cost apportioned | `POST /movements` `LANDED_COST_APPLY`, qty 0 | R4 §4.4 has this; I flag that **the apportionment basis must be on the receipt, not the freight charge** (`G-023`) |

---

# §3 — The supply-chain / procurement seam

## 3.1 The demand-side rule

> **Warehouse owns what physically happened to goods. Supply-chain owns what we *intend* and what we
> *agreed*. Accounting owns what we *owe* and what it *cost*. A document that commits us to a
> counterparty is supply-chain; a document that changes a quantity is warehouse; a document that
> changes a balance is accounting.**

Applied: a PO is a commitment (supply-chain). A GRN is a quantity change (warehouse). A supplier
invoice is an obligation (accounting). The three-way match is a *reconciliation across all three* and
therefore belongs to whichever module owns the invoice — **accounting** — reading the other two.

## 3.2 The allocation table

`SC` = a future supply-chain / procurement module. `ACC` = `accounting-base`/`accounting`.
`—` = does not hold it.

| # | Capability | `warehouse-base` | `warehouse` | `SC` | `ACC` | Version | Note |
|---|---|---|---|---|---|---|---|
| 1 | **Item master** | **owns** `whb_items` | — | reads | reads via xref | v1 | R3 `E-007`. One master. `SC` must not build a second |
| 2 | Item identifiers / barcodes / OEM + supplier part numbers | **owns** `whb_item_identifiers` | — | contributes | — | v1 | R3 `E-012` |
| 3 | **Item cross-reference to a vertical's own part number** | **owns** `whb_item_external_refs` | — | contributes | — | **v1** | the adapter's join. `G-040` |
| 4 | UoM, UoM class, conversions | **owns** | — | reads | reads | v1 | R4 `F-093` freezes the factor at post |
| 5 | Item–site policy (ROP, safety stock, lead time, ABC) | `whb_item_sites` | screens | reads for planning | — | v1 | R2 `T-032`, R3 `E-013` |
| 6 | **Supplier master (identity)** | **owns** `whb_counterparties` + `whb_counterparty_external_refs` | — | **links, never copies** | links | **v1** | §3.3. `G-027` |
| 7 | Supplier addresses, contacts, bank, tax registrations | minimal on the counterparty | — | **owns the rich profile** | owns bank/tax for payment | v1 minimal / v2 rich | `G-029` |
| 8 | Counterparty **role** (supplier / customer / carrier / 3PL client / job worker) | **owns** `whb_counterparty_roles` (many-to-many) | — | adds roles | adds roles | v1 | **not an enum** — `G-057` |
| 9 | Purchase requisition | — | — | **owns** | — | v2 | |
| 10 | RFQ / quotation / bid comparison | — | — | **owns** | — | v2 | |
| 11 | **Purchase order** | — | `wh_purchase_orders` **only if `SC` is absent** | **owns when present** | — | v1.1 (warehouse-lite) / v2 (`SC`) | `G-032` — the PO is the second movable boundary of this seam |
| 12 | PO amendment / version | — | — | owns | — | v2 | |
| 13 | Supplier contract / price agreement | — | — | owns | — | v2 | |
| 14 | OEM price file / supersession load | — | `wh_price_file_imports` | owns when present | — | v1.1 | R3 `E-068`, `E-062` |
| 15 | Lead time (agreed) vs lead time (actual) | actual is derivable from the ledger | reports | agreed lives here | — | v1 (actual) / v2 (agreed) | R3 `:1185` — exclude emergency buys or the maths is poisoned |
| 16 | MOQ, order multiple, pack size | `whb_items` / `whb_item_sites` | — | reads | — | v1 | |
| 17 | **MRP / reorder planning** | — | **`wh_replenishment_suggestions` only** | **owns the planning run** | — | v1.1 (suggestions) / v3 (`SC` MRP) | R2 `T-084`: suggestions, never POs |
| 18 | **ASN / inbound shipment notice** | — | **owns** `wh_asns` | supplier sends it | — | v1.1 | it is a receipt expectation, not a commitment |
| 19 | Inbound scheduling / dock appointment | — | **owns** `wh_dock_appointments` | reads | — | **v1 schema** / v2 screen | I diverge from R4's v2 — `G-014` |
| 20 | **GRN / goods receipt** | the movement | **owns the document** | reads | reads | v1 | R3 `E-027`: GRN ≠ supplier invoice |
| 21 | QC / inspection on receipt | `whb_stock_statuses` | inspection screens | supplier quality rules | — | v1 (status) / v1.1 (screen) | R2 `T-035` |
| 22 | Over-receipt / short-receipt tolerance | — | enforces | **owns the policy** | — | v1.1 | R2 `T-036`; R3 `:1421-1425` on the three-way-match consequence |
| 23 | Put-away | — | owns | — | — | v1 | |
| 24 | Purchase return / RTV | the movement | owns the document | owns the debit note | posts | v1.1 | R2 `T-056` |
| 25 | **Three-way match** (PO ↔ GRN ↔ invoice) | — | exposes the GRN by API | exposes the PO | **owns the match** | v2 | `G-034` |
| 26 | Supplier invoice, payment, TDS | — | — | — | **owns** | v2 | |
| 27 | **Landed cost** | `LANDED_COST_APPLY` value-only movement | apportionment basis on the receipt | the charge document | the accrual and the FX | **v1 hook / v2 feature** | R4 `F-088`, R5 §4.3, `G-023` |
| 28 | Supplier scorecard (OTIF, short-supply, quality) | ledger is the evidence | supplies receipt facts | **owns the scorecard** | — | v2 | R2 `#113`, R3 `#173` |
| 29 | Supplier claims (damage, shortage, expiry, price) | reason-coded movements | raises from a receipt | owns the register | posts the credit | v2 | R3 `E-081` |
| 30 | Consignment / VMI stock | **`owner_id` + `whb_owner_types`** | screens | the agreement | the bailment treatment | **v1 schema** | R4 `F-002`, `F-010`; R3 `E-032` |
| 31 | Subcontract / job work (material out, material back, on a clock) | movements + a job-work owner | owns the challan | owns the vendor agreement | GST treatment | v1.1 (`warehouse-india`) | R4 `F-061`, R5 §2.1 |
| 32 | HSN / SAC / tax classification | `whb_items.tax_classification_code` (a **string**, not an FK) | — | — | **owns the HSN master** | v1 (column) | `G-035` — the prior art's `scc_hsn_tax_master` gave warehouse 3 FKs it did not need |
| 33 | **Incoterms / ownership transfer point** | — | on the PO / transfer doc | on the contract | drives cut-off | **v1 column** | R5 §4.5, `G-018` |
| 34 | Currency, FX rate at receipt | `whb_movement_lines.cost_currency_code` | — | — | **owns the rate** | v1 (column) | R4 §3.3 |
| 35 | Import documentation, BoE, bonded warehousing | bonded is a **stock status + location** | screens | the BoE document | duty accrual | v2 (`warehouse-india`) | R5 §2.3 — "the deepest schema consequence in this report" |
| 36 | Drop-ship (supplier → customer, never ours) | **a movement pair through virtual locations, or none at all** | the decision | the PO | revenue/COGS | v2 | `G-037` |
| 37 | Intercompany / inter-GSTIN transfer pricing | `company_id` on the movement | two prices on the transfer | — | eliminates unrealised profit | v1 (column) / v2 | R5 §4.6 |

## 3.3 Who owns the supplier master — the load-bearing answer

**The evidence first.**

- The live repo has **no shared party master**. R1 §7 enumerates the four candidates and rejects all
  four: `asset_vendors` (`assets/.../V60056:3-38`) is right-shaped but assets-owned; automotive
  `customers` (`automotive/.../V10010:9`) and `companies` (`automotive/.../V10002:11`) model buyers
  and OEMs and are automotive-owned; `acc_companies` is accounting's own book-owning entity.
  Accessories receiving has no supplier field at all (`StockReceiptRequest.java:23-51`).
- The previous attempt put suppliers in a supply-chain module and it produced the **84 FK references**
  of `G-025`, plus `WAREHOUSE_CORE_ISSUES.md:WF-3`, which records `scc*`-named classes and a shared
  `SCC_NAMESPACES` i18n registry **inside warehouse-core** and defers the un-tangling: *"a full rename
  needs a Docker build to verify … Recommend a dedicated pass."* That is what a leaked boundary looks
  like eighteen months later.
- The precedent that works is 99 lines of SQL: `acc_companies` + `acc_company_external_refs`
  (`accounting-base/.../V600001:61`, `:204-231`), whose header says the rule out loud — *"an
  automotive/dealer/services company is LINKED here, never copied. In a standalone install this table
  is empty and everything still works"* (`:190-192`).

**The answer, in four parts.**

1. **`warehouse-base` owns `whb_counterparties`** — a *thin* identity: `code`, `name`, `legal_name`,
   `national_tax_id`, `is_active`, plus `whb_counterparty_roles` (many-to-many, §3.2 row 8). It does
   **not** own payment terms, credit limits, bank details, contacts or addresses beyond a default.
2. **`warehouse-base` owns `whb_counterparty_external_refs (counterparty_id, source_module,
   external_id)`** with `uk(source_module, external_id)` and `source_module` as an **opaque string,
   not an FK** — the `V600001:193` idiom verbatim.
3. **`logistics` owns `log_carriers` and `log_customers` as its own rows**, each with an optional
   `whb_counterparty_id`-shaped link *resolved through the xref table*, never an FK. A fleet business
   with no warehouse must install `logistics` and work.
4. **A future `SC` module owns the rich supplier profile** (terms, credit, bank, scorecard, contracts)
   and links the same way.

**The cost, stated rather than hidden.** After this decision the monorepo has, in the worst case,
**seven** party-shaped masters: automotive `customers`, automotive `companies`, `asset_vendors`,
`acc_companies`, `whb_counterparties`, `log_carriers`, `log_customers`. That is the price of module
independence and it is the *right* price — but it must be in the FRD, not discovered.
**Name the trigger for extracting a `party-base`:** the **third** module that needs the same GSTIN to
be authoritative for tax filing. Until then, extraction is speculative; after then, it is overdue.
(`G-027`…`G-031`)

---

# §4 — The N-consumer problem: the adapter contract

## 4.1 What an adapter is, in one sentence

> **An adapter is a module that translates one vertical's documents into warehouse movements and
> back, owns only its own `wha_<vertical>_*` tables, and can be added or deleted without a single
> line changing in `warehouse-base`.**

## 4.2 What an adapter MAY do

| # | May | Mechanism |
|---|---|---|
| A1 | Post stock movements | `POST /api/warehouse/movements` (R4 §3.1); batch and reverse variants |
| A2 | Simulate before promising | `POST /api/warehouse/movements/simulate` |
| A3 | Find its own postings | `GET /movements?source_system=&source_document_type=&source_document_id=` |
| A4 | Read balances and availability | `GET /api/warehouse/stock?…` — never a direct table read |
| A5 | Hold and release a reservation | `POST /api/warehouse/reservations` with a **holder quad** and a TTL (`G-042`) |
| A6 | Register its own **movement types**, **document types**, **reason-code contexts**, **stock statuses**, **location types**, **task types**, **item types** | rows inserted by the adapter's **own migration**, in the adapter's Flyway sub-band |
| A7 | Register its **source-system id** | one row in `whb_source_systems` |
| A8 | Map its own identifiers to warehouse ones | `whb_item_external_refs`, `whb_counterparty_external_refs`, `whb_location_external_refs` |
| A9 | Render its own document numbers in warehouse grids | register a `WhDocumentReferenceResolver` bean; base collects them via `List<T>` (R3 `E-004`) |
| A10 | Subscribe to stock events | in-process `List<WhMovementEventSubscriber>` **or** an HTTP subscription row in `whb_outbox_subscriptions` (`G-046`) |
| A11 | Own tables | prefix `wha_<vertical>_`, in the adapter's own migration band |
| A12 | Register permissions, menus, grids, filters | migration inserts; **plus one `filterUtils.ts` scope, which is a platform edit** (`G-047`) |
| A13 | Take a gapless document number | `whb_number_series` scoped by `owning_module` (`G-044`) |

## 4.3 What an adapter MUST NOT do

| # | Must not | Why, and how it is caught |
|---|---|---|
| B1 | `INSERT`/`UPDATE`/`DELETE` on any `whb_*` or `wh_*` table | it bypasses idempotency, the balance projection and the outbox. Caught by grep in the invariants test |
| B2 | Add a column to a base table | the second adapter wants a different column. Caught: no `ALTER TABLE whb_` outside the base band |
| B3 | Create an FK **from** a base table **to** an adapter table | it makes base undeployable without the adapter. R4 §5.3 states the same rule for 3PL |
| B4 | Be imported by base — no `import ai.warehouseadapter*` / `ai.logistics` / `ai.dealer` / `ai.services` / `ai.assets` / `ai.fieldservice` / `ai.automotive` / `ai.accessories` anywhere under `warehouse-base/backend/src/main/java` | the whole point |
| B5 | Change stock outside the port | a second write path means two balance truths — the accessories failure (R1 `C-021`) |
| B6 | Define a second envelope shape or a second idempotency scheme | R3 `E-003` |
| B7 | Reuse another adapter's `source_system` code | idempotency keys would collide retroactively (R4 §3.2, `idempotency_key`) |
| B8 | Put a `CHECK (x IN (…))` on any of the thirteen registry columns of §5 | it re-closes what base opened |
| B9 | Read or write `accessory_stock_levels` | R3 `E-087`; the separation decision is worthless if an adapter tunnels under it |
| B10 | Ship a screen that duplicates a base grid | R4 §5.5 #9 — two grid mechanisms is how 40 grid identifiers become 80 |

## 4.4 The build-time test that proves loose coupling

The accounting equivalent of this test **does not exist as a test** — it exists as a comment:
`accounting/backend/src/main/java/ai/accounting/AccountingModuleConfig.java:22` says *"The dealer
adapter lives in `ai.accountingadapterdealer`, a SIBLING package"*, and
`accounting-adapter-dealer/.../AccountingAdapterDealerModuleConfig.java:3` imports only
`ai.platform.util.PlatformLogger`. Correct today, unenforced tomorrow. The existing
`ArchitectureInvariantsTest` (both copies) covers `@PreAuthorize`, cache names, `PageRequest.of` and
`findById`-in-a-loop, plus scanner self-tests — **it contains no dependency-direction test**
(inspected: `accounting-base/backend/src/test/java/ai/accountingbase/architecture/ArchitectureInvariantsTest.java`,
`@DisplayName` list at `:64-346`).

**Three layers, in increasing strength.**

**Layer 1 — `WarehouseBaseCouplingTest` (static, in `warehouse-base`).** Six assertions:

1. No source file under `warehouse-base/backend/src/main/java` contains `import ai.warehouse.`,
   `import ai.warehouseadapter`, `import ai.warehouse3pl`, `import ai.logistics`, or any vertical
   package (`ai.dealer`, `ai.services`, `ai.assets`, `ai.fieldservice`, `ai.automotive`,
   **`ai.accessories`**, `ai.insurance*`, `ai.submittals`, `ai.leadsharing`, `ai.productlift`).
2. No migration in `V500000–V509999` contains the token `wha_`, `wh3pl_`, `log_`, `accessory_`,
   `pdi_`, `service_`, `asset_` in a `REFERENCES` clause.
3. Every `FOREIGN KEY … REFERENCES` in the base band targets a `whb_` table or one of a whitelisted
   platform set (`users`, `user_details`, `branches`, `companies`?, `documents`). The whitelist is
   itself asserted, so widening it is a reviewed act.
4. **No `CHECK (… IN (…))` exists on any of the thirteen registry columns of §5.** The test names the
   thirteen `table.column` pairs explicitly; adding a fourteenth registry means adding a row here.
5. The scanners self-test (copy the existing shape at `:225-346`) so none of the above passes
   vacuously.
6. `whb_source_systems` contains a row for `ACCESSORIES` with `is_reserved = true` and no adapter
   claims it (`G-052`).

**Layer 2 — `warehouse-adapter-example`, a fixture adapter in the repo.** Zero screens. One movement
type, one document type, one item xref, one reservation, one subscriber. Its integration test posts a
movement, reserves, consumes, reverses, and reads back — **using only the public API of §4.2**. If the
fixture compiles and passes, the contract is expressible; if a real adapter needs something the
fixture cannot express, that is a base gap found before the base ships. This is materially stronger
than any grep, and it is the thing R2 `T-079` and R3 `E-006` both ask for without naming the
mechanism.

**Layer 3 — the review ratchet, stated as procedure not as a test.** At the commit that merges the
*second* adapter, `git log --oneline -- warehouse-base/ | wc -l` must equal its value at the commit
before. A CI job cannot see this reliably across rebases; a reviewer can, in one command. Record the
number in the adapter's PR description. **Honest caveat:** `platform/frontend/src/utils/filterUtils.ts`
and `platform/.../CacheConfiguration.java` will change — the ratchet is on `warehouse-base/`, never on
`platform/` (`G-047`).

## 4.5 The concrete adapters, defined now

| Adapter | Vertical objects it maps | Movement types it registers | Its own tables | Version | Notes |
|---|---|---|---|---|---|
| **`warehouse-adapter-dealer` (spare parts)** | parts counter sale, workshop parts request, OEM order, core return | `SALE_ISSUE`, `COUNTER_RETURN`, `CORE_RECEIVED`, `RTV_OEM` | `wha_dealer_part_issues`, `wha_dealer_core_links` | **v1** | R3 `E-006` requires two adapters in v1 to prove genericity |
| **`warehouse-adapter-dealer` (vehicle-shaped)** | `pdi_vehicle_inventory` — one chassis per row | *none in v1* | *none in v1* | **v3, and it is an open decision** | `G-050`. `pdi_*` is a serialised, quantity-free inventory with its own append-only slot model (R1 §5.2, `dealer/V20735:8,57-69`). Migrating it is a rewrite of a live vertical. **The test of whether it should ever happen: can `whb_serials` carry a chassis number, a colour, a variant and a PDI status without base learning what a vehicle is?** If the answer needs a base column, the answer is no |
| **`warehouse-adapter-services`** | job card / `service_entries` parts lines | `ISSUE_TO_JOB`, `JOB_PART_RETURN` | `wha_services_job_issues` | **v1** | R2 `T-081`, R3 `E-065`. `services` has **no parts table today** (R1 §5.3: zero hits) — clean sheet |
| **`warehouse-adapter-field-service`** | `service_jobs`, `job_trips` | `VAN_REPLENISH`, `ISSUE_AT_SITE`, `VAN_RETURN` | `wha_fieldservice_van_stock_links` | **v1.1** | R2 `T-080`. The van is a `whb_locations` row, `location_type='MOBILE'`, `assigned_user_id = technician`. `job_trips` already knows where the van is (`V80007:13-48`) |
| **`warehouse-adapter-assets`** | `asset_complaints` resolution, `asset_po_receipts` | `ISSUE_TO_ASSET`, `SPARE_RETURN` | `wha_assets_spare_issues` | **v1.1** | R1 §6: `asset_po_receipts` receives *assets*, not stock — model to extend, not reuse. Assets also has the vendor master warehouse lacks, mapped through the counterparty xref |
| **`warehouse-adapter-logistics`** *(or the logistics module posting directly)* | trips, equipment, tyres, depot fuel, transit loss | `TRANSFER_DEPART`, `TRANSFER_ARRIVE`, `TRANSIT_LOSS`, `EQUIPMENT_ISSUE`, `EQUIPMENT_RETURN`, `FIT_TO_ASSET`, `REMOVE_FROM_ASSET`, `LANDED_COST_APPLY` | in `logistics` itself | **v2** | `G-048` — decide now whether logistics gets an adapter or posts directly. **Recommendation: posts directly**, because logistics is a full module with its own team, and an adapter between two of our own modules is ceremony |
| **`warehouse-adapter-accessories`** | — | — | — | **NEVER** | §4.6 |

## 4.6 What "accessories is explicitly NOT an adapter" means for the registry

Four concrete consequences, none of which is "do nothing":

1. **`whb_source_systems` gets an `ACCESSORIES` row with `is_reserved = true, is_claimable = false`**
   and a comment naming the decision. Reserving the string stops a future author using `ACCESSORIES`
   for something else and stops a well-meaning agent "completing" the adapter set. Asserted by
   `WarehouseBaseCouplingTest` layer-1 assertion 6.
2. **`ai.accessories` is in the forbidden-import list** (B4) — the only vertical that is forbidden
   *by decision* rather than by the general rule.
3. **No adapter may read or write `accessory_stock_levels`** (B9, R3 `E-087`). Without this, the
   separation is defeated by a helpful adapter that "just reads" the balance.
4. **The FRD carries the counted cost.** R1 `C-032`: 17 tables, 71 backend files, ~12 web routes, 11
   reports, 33 mobile screens, 25+ filter scopes, 12 permission resources duplicated permanently, and
   **no query can answer "how much of part X do we hold" across both**. `G-051` is that the *report*
   gap is the part customers will actually hit, and the honest mitigation is a documented "these two
   inventories are separate" statement in the UI, not a union view.

---

# §5 — Closed vocabularies are the enemy: the open-registry table

## 5.1 The pattern, specified once

Every registry table below has **exactly this shape**, and the shape is copied from a live, commented
precedent:

```
<name> (
  id, [company_id],
  code           VARCHAR(40)  NOT NULL,     -- NO CHECK CONSTRAINT, EVER
  name           VARCHAR(255) NOT NULL,
  owning_module  VARCHAR(30)  NOT NULL,     -- OPAQUE STRING, NOT AN FK  (V600001:193)
  is_system      BOOLEAN      NOT NULL DEFAULT false,   -- system rows undeletable
  sort_order     INTEGER      NOT NULL DEFAULT 0,
  <behaviour columns: typed booleans / small closed sets that describe HOW the row behaves>,
  is_active, status, version, created_at, updated_at, created_by, updated_by,
  uk(code) or uk(company_id, code)
)
```

Precedent, verbatim from the migration that does it right:

> *"`context` carries NO CHECK constraint, deliberately. It is a CATALOGUE, not an enum: p1-20 adds an
> ORDER_SHORT_CLOSE context and p2-10 an interest-waiver context, and both must be a seed INSERT
> rather than an ALTER of a CHECK in accounting-base."*
> — `accounting-base/.../V600002__Create_acc_reason_codes.sql:22-26`

Counter-precedent, verbatim from the live platform, three migrations deep:
`widget_definitions.chk_module` — `('platform','dealer','shared')` at
`platform/.../V234__Create_dashboard_system_tables.sql:36` → five at `V276:10` → seven at `V557:18`,
and **still** no `warehouse`, no `accounting`, no `logistics`. Same story for
`global_settings.chk_global_setting_module`: five at `V337:42`, seven at `V553:15`.

**The safe widening idiom, when a platform CHECK must be widened anyway**, is
`accounting-base/.../V600200__Allow_accounting_in_platform_module_check_constraints.sql:55-95`: read
`pg_get_constraintdef`, `regexp_matches` every quoted literal already allowed, `array_append` the new
one, rebuild. A hardcoded DROP/ADD silently discards another module's value; that idiom cannot.
(`G-053`)

## 5.2 The thirteen registries

| # | Vocabulary | The wrong shape (and where it already exists) | Registry table | Behaviour columns (what makes it a table rather than a list) | Who may INSERT | v1 seed |
|---|---|---|---|---|---|---|
| 1 | **Movement type** | Java enum / `CHECK`. Accessories does the *other* wrong thing: `transaction_type VARCHAR(30)` with the vocabulary only in a comment and **no CHECK at all** (`accessories/.../V30131:10`, `:68`) | `whb_movement_types` | `direction`, `is_financial`, `cost_basis_default`, `reversal_type_code`, `requires_approval`, `requires_reason`, `affects_availability`, `is_stock_bearing`, `billable_event_code` | any module | RECEIPT, ISSUE, TRANSFER_DEPART, TRANSFER_ARRIVE, TRANSIT_LOSS, ADJUST_UP/DOWN, COUNT_ADJUST, STATUS_CHANGE, OWNER_CHANGE, SCRAP, RETURN_RECEIPT, RTO_RECEIPT, LANDED_COST_APPLY + reversal counterparts |
| 2 | **Document / reference type** | free-text `reference_type` (`accessories/.../V30131` carries `reference_type`/`reference_id`/`reference_number` with no registry) | `whb_document_types` | `owning_module`, `display_resolver_bean`, `is_stock_bearing`, `is_external` | any | SALES_ORDER, TRANSFER_ORDER, WORK_ORDER, JOB_CARD, PO, ASN, GRN, COUNT, TRIP, MANIFEST, CONSIGNMENT, POS_SHIFT, RMA |
| 3 | **Source system / adapter id** | a hardcoded string in the adapter | `whb_source_systems` | `module`, `is_reserved`, `is_claimable`, `post_permission` | one row per module, by its own migration | WAREHOUSE, ADAPTER_DEALER, ADAPTER_SERVICES, ADAPTER_FIELD_SERVICE, ADAPTER_ASSETS, LOGISTICS, WAREHOUSE_3PL, IMPORT, **ACCESSORIES (reserved)** |
| 4 | **Stock status** | `CHECK` on the ledger; or modelled as a location | `whb_stock_statuses` (R2 `T-004`, R4 `F-068`) | `is_available`, `is_allocatable`, `is_shippable`, `is_countable`, `is_owned_asset`, `requires_reason_to_enter`, `requires_reason_to_leave`, `badge_variant` | any | AVAILABLE, QC_HOLD, DAMAGED, QUARANTINE, EXPIRED, BLOCKED, CORE_UNGRADED, BONDED |
| 5 | **Location type** | `CHECK` — **and this is the one the prior product actually broke**: `WAREHOUSE_CORE_ISSUES.md:DB-1` records `zone_type` and `location_type` CHECKs *dropped and recreated with completely different enum value sets* at V200042, 36 versions after creation | `whb_location_types` | `is_physical`, `is_stock_holding`, `is_virtual_counterparty`, `is_mobile`, `is_transit`, `allows_mixed_owner`, `requires_assigned_user` | any | BIN, BULK, STAGING, RECEIVING, SHIPPING, DOCK, **IN_TRANSIT**, **MOBILE**, **VEHICLE**, **TRAILER**, CUSTOMER, SUPPLIER, SCRAP, ADJUSTMENT_OFFSET, PRODUCTION |
| 6 | **Reason code + reason context** | free text | `whb_reason_codes` | `context` (**no CHECK** — `V600002:22-26` verbatim), `requires_note`, `owning_module`, `blocks_posting` | any | adjustment, short-pick, damage, transit-loss, scrap, return, count-variance, hold, release, RTO, NDR |
| 7 | **UoM class + UoM** | `CHECK` on class | `whb_uom_classes` + `whb_uoms` + `whb_uom_conversions` | `is_base_for_class`, `decimal_places`, `uqc_code` (the statutory GST code, R5 `S-011`) | any | MASS, VOLUME, LENGTH, COUNT, AREA, TIME; EA, BOX, CASE, PALLET, KG, L, M, CFT |
| 8 | **Task type** | enum | `whb_task_types` (R2 `T-041`) | `owning_module`, `is_directed`, `default_priority`, `interleavable`, `labour_standard_minutes` | any | PUTAWAY, PICK, REPLEN, COUNT, MOVE, LOAD, PACK, QC, VAS |
| 9 | **Owner type** | `CHECK` on `whb_owners` | `whb_owner_types` (R4 `F-002`) | `is_house`, `posts_to_our_gl`, `default_cost_basis` | any | HOUSE, CLIENT_3PL, CONSIGNOR, CUSTOMER_OWNED, SUPPLIER_CONSIGNED, JOB_WORK |
| 10 | **Item type** | `CHECK` (R3 `E-007` proposes an enum — **I diverge**, `G-060`) | `whb_item_types` | `is_stocked`, `is_serial_default`, `is_lot_default`, `is_returnable_equipment`, `is_asset_shaped`, `is_value_only` | any | STOCK, NON_STOCK, SERVICE, KIT, CORE, CONSUMABLE, **PACKAGING**, **RETURNABLE_EQUIPMENT**, **TYRE**, **FUEL** |
| 11 | **Counterparty role** | `partner_type ENUM(...)` — R2 `T-040` proposes exactly this and **I diverge**, `G-057` | `whb_counterparty_roles` + `whb_counterparty_role_links` | `role_code`, `owning_module`; the link row carries `is_primary`, `valid_from/to` | any | SUPPLIER, CUSTOMER, CARRIER, CLIENT_3PL, TRANSPORTER, JOB_WORKER, INTERNAL |
| 12 | **Disposition** (return/RMA outcome) | `CHECK` — R4 `F-052` already calls it "a vocabulary" | `whb_dispositions` | `movement_type_code`, `target_stock_status_code`, `requires_inspection`, `emits_credit_signal` | any | RESTOCK_SELLABLE, RESTOCK_UNSELLABLE, REFURB, REPACK, SCRAP, RTV, DONATE, HOLD_FOR_CLIENT, RETURN_TO_CLIENT |
| 13 | **Attribute key** (the side-table keys of R4 §3.3) | JSONB — forbidden by CLAUDE.md and by R4 §3.6 | `whb_attribute_keys` | `value_type`, `owning_module`, `is_filterable`, `is_exportable` | any | temperature, cold-chain excursion, COA ref, channel order id, GS1 AI codes |

**Thirteen, not six.** Accounting's round-4 review found six closed vocabularies in its base. A
warehouse has more axes than a ledger, and every one of the thirteen above is a place a future
consumer must extend: logistics needs #1, #2, #3, #5, #6, #10; a supply-chain module needs #2, #6,
#11; a 3PL needs #4, #9, #12; an EDI adapter needs #13.

## 5.3 The rule that stops the frontend re-closing what the backend opened

An open backend registry is worthless if the frontend hardcodes the list. This repo has a **recurring,
documented defect of exactly that shape** — R2 §3.2 names it: *"a status present in the CHECK
constraint but missing from the frontend union, the variant map, the filter options or the i18n
keys"*. Three concrete rules, each checkable:

1. **No TypeScript string-union type may enumerate a registry vocabulary.** The type is
   `type MovementTypeCode = string` plus a runtime list fetched from a dropdown endpoint. This
   knowingly diverges from CLAUDE.md's "String union types over TypeScript enums" — that rule is
   right for genuinely fixed sets (`'ACTIVE' | 'INACTIVE'`) and wrong for a catalogue. **Referred to
   the standards reviewer to adjudicate, with my recommendation attached** (`G-064`).
2. **`StatusBadge` variant comes from a `badge_variant` column on the registry row**, not from a
   frontend map. One less place to forget.
3. **i18n falls back to the registry row's `name`** when `t('warehouse:statuses.<code>')` misses, so a
   newly registered status renders in English rather than as a raw key. (`G-065`)

---

# §6 — The irreversible list: what `warehouse-base` v1 must carry for logistics to be possible in v2/v3 without editing base

This is the section the lens exists for. Each item is either **free now or impossible later**. Items
marked `[R4]` restate a sibling finding — included because the list must be complete, not because it
is new. Items marked `[NEW]` are not in any sibling report.

| # | Must be in `warehouse-base` v1 | Source | The argument — what specifically breaks if it lands in v2 |
|---|---|---|---|
| 1 | `owner_id NOT NULL` on every line, balance, lot, serial, LPN, reservation | `[R4 F-001]` | In-transit stock has an owner. A transit loss that cannot name whose unit was lost is not a carrier claim, it is shrinkage. Backfill is impossible — no rule recovers whose a unit was |
| 2 | `IN_TRANSIT` location type + `is_physical=false` on a warehouse + `whb_location_types.is_transit` | `[R4 F-089]` | Without it a transfer is one movement and stock falls off the books between despatch and arrival. Every historic transfer becomes unsplittable; in-transit ageing is unanswerable for the past |
| 3 | The lineage quad on the header + `source_line_ref` on the line | `[R4 F-084]` | It is how logistics finds its own postings (`?source_document_type=TRIP`). A free-text `reference` cannot be joined or indexed |
| 4 | `occurred_at` **producer-supplied**, distinct from `recorded_at` and `effective_date` | `[R4 F-083]` | A gate-out at 22:00 synced at 09:00 dates itself wrong; in-transit ageing is a day out; storage billing bills the wrong month |
| 5 | `idempotency_key` + `payload_hash`, `uk(source_system, idempotency_key)`, key **never** server-generated | `[R4 F-081]` | A driver's device retries. An already-double-posted ledger cannot be deduplicated afterwards, because the duplicate is indistinguishable from a legitimate repeat |
| 6 | Append-only, reversal-only correction, gapless `sequence_no` | `[R4 F-082, F-086]` | A sequence cannot be started retroactively over rows that already exist. The outbox cursor and any hash chain both key on it |
| 7 | `whb_movement_types` as **rows** with `owning_module`, no CHECK | `[R4 F-087]` + §5 | `TRANSFER_DEPART`, `TRANSIT_LOSS`, `EQUIPMENT_ISSUE`, `FIT_TO_ASSET` are logistics types. If the type is an enum, every one of them is a base release |
| 8 | `whb_document_types` and `whb_source_systems` as rows | `[NEW]` §5 | `TRIP`, `MANIFEST`, `CONSIGNMENT` are logistics document types. Same argument as #7, and `source_system` additionally partitions the idempotency key namespace |
| 9 | Value-only movements — `quantity = 0` permitted with `unit_cost` present | `[R4 F-088]` | Freight capitalisation is `LANDED_COST_APPLY` with zero quantity. Without it, freight can never enter stock cost, and warehouse and accounting disagree permanently. **No prior-art TMS file connects freight to inventory value** (§1.7 row 53) |
| 10 | `reason_code_id` on header **and** line; `whb_reason_codes.context` with no CHECK | `[R4]` + §5 | A transit loss without a categorical reason is unreportable and unclaimable. Free text in v1 is a dimension that can never be aggregated for the past |
| 11 | `actor_type` including `DEVICE`, plus `device_id` | `[R4 §3.2]` | A geofence-triggered arrival and a scan-gun posting have no attributable actor otherwise. Diagnosing a mis-scanning device retroactively is impossible |
| 12 | Batch posting with **per-movement** idempotency and per-movement results | `[R4 F-092]` | A driver's device syncing forty scans after a route must not lose thirty-nine because of one bad row |
| 13 | `whb_locations.assigned_user_id` + `MOBILE` and `VEHICLE` location types | `[R2 T-080]` + §2.4 | Van stock, last-mile stock and a driver's shortage. Without it, van stock becomes a separate table and a separate reconciliation problem — and last mile is unbuildable on the ledger |
| 14 | **`whb_location_external_refs (location_id, source_module, external_id)`** | `[NEW]` | The vehicle's dual identity (§2.4). Without it, either `whb_locations` gets a `vehicle_id` FK into logistics (base depends on logistics — fatal) or logistics duplicates the location tree |
| 15 | **`whb_item_external_refs`** and **`whb_counterparty_external_refs`** | `[NEW]` (shape from `V600001:204-231`) | The adapter join. R2 `T-033` lets the port identify an item by sku or barcode; a dealer's own part number is neither. Retrofitting means every historic movement has an unresolvable external identity |
| 16 | **`whb_reservations` with a holder quad `(holder_system, holder_document_type, holder_document_id, holder_line_no)` and an `expires_at`** | extends `[R4 F-028]` | R4 makes reservations a table; it does not make them **holdable by a module that is not warehouse**. Logistics reserves stock for a planned trip before a wave exists. Without the holder quad, base cannot answer "release everything trip X held" when the trip cancels, and orphaned reservations silently reduce availability forever |
| 17 | **`whb_outbox` with a monotonic cursor AND `whb_outbox_subscriptions` for HTTP delivery** | extends `[R4 F-086/F-012]` | R4 specifies the outbox. It does not specify that a consumer may be **out of process**. There are **zero** `outbox` files in `platform`, `accounting-base`, `accounting`, `dealer`, `automotive`, `services`, `assets` (computed) — this is net-new infrastructure either way, and adding the subscription table now is one table; adding it after three in-process subscribers exist is a redesign of all three |
| 18 | `whb_stock_statuses` as rows, `stock_status_code` on the ledger **and in the balance unique key** | `[R4 F-068]` | Damaged-in-transit stock must be segregable without moving it. If status is not in the balance key, every historic balance row is wrong the day it is added |
| 19 | `lot_id` / `serial_id` / `lpn_id` on the line | `[R4 F-063, F-064]` | A tyre is a serial. A pallet moved as one unit is an LPN. A recall is retrospective by definition |
| 20 | `whb_item_types` admitting `RETURNABLE_EQUIPMENT`, `TYRE`, `FUEL`, `PACKAGING` | `[NEW]` §1.2/§1.5 | This is what stops `tms_equipment_inventory` and `tms_tyres` being built as private ledgers. It costs four seed rows in v1 |
| 21 | `whb_counterparties` + roles as a link table | `[R1 C-035]`, diverging from `[R2 T-040]` on the enum | Inbound receiving cannot name who shipped. A carrier is a counterparty with a role, not a `partner_type` value |
| 22 | `company_id` on the movement | `[R4 §3.2]` | Cross-GSTIN transfers and e-way bills. A GST return computed from guessed entities is a filing error |
| 23 | `uom_code` + `base_uom_code` + **frozen `conversion_factor_used`** | `[R4 F-093]` | Freight is billed per kg, stock is held in cases. A ledger that re-derives from today's factor silently restates last year |
| 24 | **A stable string key for every base-resolved reference another module holds** (item code, location code, counterparty code, carrier code) | generalises `[R4 §4.5 rule 2]` | It is what makes the five movable boundaries of §2.6 a refactor rather than a data migration |
| 25 | **Permission namespace reservation and `permission_dependencies` rows**: `warehouse:movements:post` exists in v1, and `logistics:*` is reserved | `[NEW]` | A logistics user who dispatches a trip posts a stock movement. If that permission is invented in v2, every existing role must be re-granted by hand. `permission_dependencies` is a platform table — **insert rows, never `CREATE TABLE`** (R1 `C-017`, `T-10`; the documented false premise is `dealer/V20501:10`) |

**Twenty-five items, counted from the table above: seventeen restate a sibling finding, five are new
here (8, 14, 15, 20, 25), and three extend or generalise a sibling's (16, 17, 24).** None of them
requires `warehouse-base` to know that transport exists — which is the test R4 §4.6 sets and which
this list passes. I have not counted them as "columns vs tables", because several items are both.

---

# §7 — Sequencing

| Version | Logistics-facing work | Rationale |
|---|---|---|
| **v1** — `warehouse-base` + `warehouse` first release | All 25 items of §6. The thirteen registries of §5, seeded. The transfer service posting **two** movements through an `IN_TRANSIT` location. `wh_carriers` / `wh_carrier_services` / `wh_carrier_accounts` in `warehouse` (they will move). `wh_shipments` + cartons. `wh_dock_appointments` **schema** (see `G-014`). `whb_counterparties` + all three xref tables. `WarehouseBaseCouplingTest` + `warehouse-adapter-example`. Two real adapters (dealer parts, services) to prove genericity per R3 `E-006` | Everything here is either a column that cannot be added later, or a test that stops the boundary rotting while nobody is looking |
| **v1.1** | `whb_outbox_subscriptions` wired to a first HTTP consumer. Reservation holder quad exposed publicly. `wh_asns`. Dock-appointment **screens**. Delivery challan print. `field-service` and `assets` adapters. Van stock. Mobile screens (R2 `T-051` — mandatory in this codebase). E-way bill payload builder in `warehouse-india`, reading only §6 columns | The first real integrations, on schema that already exists |
| **v2** — **the `logistics` module itself** | Consignments (1:1 with shipments), manifests, trips, trip stops/legs, indents, deliveries, ePOD, NDR, RTO. Own-fleet vehicles, drivers, documents, maintenance, fuel, EMI, challans. Carrier rate cards, carrier bills, freight audit, trip settlement. Yard and gate. Detention. `wh_carriers` → `log_carriers` (the movable boundary, §2.6). Equipment and tyres **as warehouse stock with logistics fitments**. Landed-cost apportionment. Hub decision per hub (`G-022`) | This is the whole TMS core of `TMS_Functional_Document.md` modules 1, 2, 3, 4 and 6, minus everything that was allocated to warehouse in §2 |
| **v3** | Route optimisation. Telematics/FASTag/geofence auto-status. Control tower. Spot bidding / reverse auction. Multi-leg hub-and-spoke. Carrier scorecards. Tyre lifecycle analytics. Driver settlement. `SC` module: requisition, RFQ, PO, contracts, MRP, scorecards, three-way match. **The dealer vehicle-as-stock decision** (`G-050`) | Everything that needs either a year of our own data, a third-party integration, or a decision this lens deliberately leaves open |

---

# §8 — Findings register `G-001` … `G-086`

Format: **ID** · severity · gap/decision · why it matters · recommendation · module · version.

## 8.1 The capability map (§1)

**`G-001` · MAJOR · The TMS prior art has no item identity, and that is the boundary.**
*Gap.* `grep -n "item_id\|product_id\|sku" TMS_Functional_Document.md` → **0 hits**.
`tms_consignment_items:648-674` identifies goods by `description VARCHAR(500)` + captured `hsn_code` +
captured `uom_code`.
*Why.* A logistics module built to that spec **cannot post a stock movement**, which proves the seam
is real — but it also means the *integrated* install needs a link the prior art does not have.
*Recommendation.* `log_consignment_items.shipment_line_id UUID NULL` referencing `wh_shipment_lines`
by id, and `log_consignments.shipment_id UUID NULL` — both **nullable**, because a freight-only
customer's consignment has no warehouse shipment. Never make them `NOT NULL`.
*Module.* `logistics`. *Version.* **v2**.

**`G-002` · MAJOR · `tms_equipment_inventory` is a stock ledger inside a TMS.**
*Gap.* `TMS_Functional_Document.md:483-500` — serialised tarpaulins, chains, ropes and GPS devices with
`condition (GOOD/DAMAGED/SCRAPPED)` and `availability_status (AVAILABLE/ASSIGNED/MAINTENANCE)`, plus
`tms_trip_equipment` (`:971-989`).
*Why.* That is an item master, a serial master, a stock-status vocabulary and a reservation, rebuilt
badly. It will not reconcile with anything and it cannot be valued.
*Recommendation.* `whb_item_types` row `RETURNABLE_EQUIPMENT`; equipment is `whb_serials`;
`tms_trip_equipment` becomes `log_trip_equipment (trip_id, whb_reservation_id)`; issue and return are
`EQUIPMENT_ISSUE` / `EQUIPMENT_RETURN` movements.
*Module.* `warehouse-base` (type) + `logistics`. *Version.* **v1 (type)** / **v2 (use)**.

**`G-003` · MAJOR · `tms_tyres.tyre_status` is a stock lifecycle wearing a fleet label.**
*Gap.* `:1254-1256` — `IN_STOCK, FITTED, REMOVED, RETREAD, SCRAPPED` plus a second axis
`condition (GOOD/WORN/DAMAGED/BURST)`, `purchase_cost`, `purchase_vendor`, `serial_number UNIQUE`.
*Why.* A tyre on the shelf is stock with a cost and a supplier; a tyre on an axle is a fitment. One
table conflating both means tyre stock is invisible to inventory valuation and the fitment history is
lost when the tyre goes back on the shelf.
*Recommendation.* `whb_item_types` row `TYRE`; the tyre is a `whb_serials` row; **`log_tyre_fitments
(whb_serial_id, vehicle_id, position, fitted_date, fitted_odometer_km, removed_date,
removed_odometer_km, retread_count)`** is an *event log*, not a master. `FIT_TO_ASSET` /
`REMOVE_FROM_ASSET` movements move the serial between the store location and the vehicle location.
*Module.* `warehouse-base` + `logistics`. *Version.* **v1 (type)** / **v2 (fitments)** / **v3 (analytics)**.

**`G-004` · MINOR · Fleet spare-parts inventory is in the vendor study but not in the TMS document.**
*Gap.* `02_Fleetable.md:105-106` — *"Spare Parts Inventory: stock levels, purchase orders, auto reorder
alerts"*. `TMS_Functional_Document.md` has no such table; `08_Fretron.md:192` and `07_FarEye.md:114`
both list its absence as a gap in their products.
*Why.* Whoever writes the logistics FRD will notice the gap and build a spare-parts table.
*Recommendation.* State in the logistics FRD that fleet spares are **warehouse stock consumed by
`log_vehicle_maintenance`**, with `log_maintenance_parts (maintenance_id, movement_id)` as the only
link. Identical shape to `services` job parts — one adapter pattern, two consumers.
*Module.* `logistics`. *Version.* **v2**.

**`G-005` · MINOR · Depot bulk fuel is a stock item and no prior-art file models it.**
*Gap.* `tms_fuel_logs:1199-1222` models retail/card purchase only (`fuel_station_name`,
`rate_per_liter`, `payment_mode CASH/FUEL_CARD/COMPANY_ACCOUNT`). No tank, no dip reading, no
receipt into a tank.
*Why.* Any operator with a depot tank holds thousands of litres of a fungible commodity with a value
and a shrinkage rate. As a TMS "expense" it is invisible to inventory and unreconcilable.
*Recommendation.* `whb_item_types` row `FUEL` (UoM litres); a tank is a `whb_locations` row; a dip
reading is a `COUNT_ADJUST`; issue to a vehicle is `ISSUE_TO_ASSET`. Card fuel stays an expense with
no movement — the distinction is `is the fuel ours before it is in the vehicle?`.
*Module.* `warehouse-base` (type) + `logistics`. *Version.* **v1 (type)** / **v2 (use)**.

**`G-006` · MINOR · The TMS document's own table count is internally inconsistent.**
*Gap.* Heading says **"COMPLETE TABLE COUNT: 47 Tables"** (`:1808`); the list beneath it numbers to 56
and the footer says **"Total: 56 Tables"** with a breakdown summing to 56 (`:1869`).
*Why.* Not a design defect, but the document is called *"the single source of truth for TMS
development"* (`:2266`). A stale headline count in a source-of-truth document is how scope estimates
go wrong.
*Recommendation.* Treat **56** as the number; correct the heading when the logistics FRD is written.
*Module.* prior art. *Version.* —.

**`G-007` · MINOR · Driver management in the TMS overlaps platform HR.**
*Gap.* `tms_driver_attendance`, `tms_driver_leaves`, `tms_driver_salary`, `tms_driver_advances`
(`:1368-1444`). The platform already has attendance, leave (`LeaveBalance`, `LeaveRequest` — see
CLAUDE.md and R1 §9's `@Version`/`@Lock` precedents) and user management.
*Why.* Out of my lens's scope for the *stock* boundary, but it is the same class of error: a module
rebuilding a platform capability because the platform one was not considered.
*Recommendation.* Before writing `log_driver_*`, enumerate the platform HR tables and state per table
whether it is reused, extended or duplicated. **Referred, not adjudicated here.**
*Module.* `logistics`. *Version.* **v2**.

**`G-008` · MINOR · Two rate-card engines will exist and must not share code.**
*Gap.* `warehouse-3pl` has versioned, effective-dated rate cards rated against the version live on the
event date (R4 `F-014`); `logistics` has customer and carrier rate cards (`:382-443`).
*Why.* They look identical and are not: one rates *storage and handling events*, the other rates
*lanes and weights*. A shared engine acquires both vocabularies and serves neither.
*Recommendation.* Share the **pattern** (versioned header, effective-dated, rate against the version
live on the event date, never re-rate history), never the tables or the service.
*Module.* `warehouse-3pl` + `logistics`. *Version.* **v1.1 / v2**.

## 8.2 The boundary (§2)

**`G-009` · MAJOR · Sharpen R4's boundary rule so it decides equipment, tyres, fuel and the gate.**
*Decision.* R4 §4.1's physical rule is correct for goods and silent on four things a fleet owns.
*Recommendation.* Adopt the two-part rule of §2.1 and record that it is a **refinement of R4, not a
replacement** — R4's dock-door sentence remains the rule for the physical handover.
*Module.* design set. *Version.* **v1**.

**`G-010` · MINOR · The three transport-shaped objects have dual identity; make it a named rule.**
*Recommendation.* §2.4's rule, with its two deletion tests, in the FRD's architecture chapter.
*Module.* design set. *Version.* **v1**.

**`G-011` · MAJOR · A stock-bearing trailer in the yard must be a warehouse location.**
*Gap.* R4 §5.5 #12 defers yard and trailer management to logistics, correctly — but says nothing about
stock *on* a trailer parked in our yard.
*Why.* It is R4 §4.3's own in-transit argument applied one step earlier: if the trailer is neither at
the dock nor in transit, the stock is nowhere.
*Recommendation.* `whb_location_types` row `TRAILER` (`is_stock_holding=true`, `is_mobile=true`),
seeded in v1. Yard *slot* management stays in logistics v2.
*Module.* `warehouse-base`. *Version.* **v1 (seed row)**.

**`G-012` · MAJOR · The weighbridge measures stock, not the yard.**
*Gap.* `tms_yard_entries.tare_weight_kg / gross_weight_kg / net_weight_kg` (`:1015-1017`).
*Why.* A weighbridge net weight is a *quantity claim about goods*. Bulk commodity receiving is
frequently weight-based, and a receipt of 19.4 t against an ASN of 20 t is a short-receipt, not a
yard note.
*Recommendation.* The yard entry stays in logistics; when a weighment resolves a receipt quantity, the
receipt line carries `weighment_source_document_type='YARD_ENTRY'` + id via the lineage quad, and the
movement's quantity is the net weight. No new base column needed — this is a *use* of §6 item 3, and
it is worth naming because otherwise someone will add `net_weight_kg` to `whb_movement_lines`.
*Module.* `warehouse` + `logistics`. *Version.* **v2**.

**`G-013` · MAJOR · Five boundaries will move, not one; apply R4 §4.5's rule to all five.**
*Gap.* R4 §4.5 names carriers as *"the one boundary that will move"*. Tracking events, NDRs, RTO
consignments and COD remittances (`F-043`…`F-046`) are all in `warehouse` v1 for the same reason.
*Why.* Rule 2 (reference by a stable code resolved through a service) applied to one object and not
the other four is how a cheap move becomes a data migration.
*Recommendation.* §2.6's table in the FRD, with the rule applied to all five, and a note that
`wh_rto_consignments` only **partly** moves — the RTO *receipt* is permanently a warehouse movement.
*Module.* `warehouse`. *Version.* **v1 (the rule)** / **v2 (the move)**.

**`G-014` · MAJOR · I diverge from R4: dock-appointment schema is v1, not v2.**
*Divergence, stated explicitly.* R4 `F-080` is `MINOR · schema+feature · warehouse · v2`
(`R4:2187`), and R4 §5.5 #12 says *"`wh_dock_appointments` is the join and it exists in v2"*.
*Why I disagree.* R4's own `F-074` makes lifecycle timestamps v1 *because a duration cannot be
backfilled*, and dock-to-stock and detention are exactly such durations. R4 `F-018` (accessorials) and
the detention charge both read `arrived_at` / `released_at`. A v2 table means every v1 receipt has no
arrival time, so the first client's dock-to-stock report has no history, forever.
*Recommendation.* `wh_dock_appointments` **schema in v1** (dock, window, direction, reference,
`vehicle_ref_source_module`, `vehicle_ref_external_id`, denormalised `vehicle_registration_number`,
`arrived_at`, `released_at`); the **screen** stays v2. R4's severity and feature placement otherwise
stand.
*Module.* `warehouse`. *Version.* **v1 (schema)** / **v2 (screen)**.

**`G-015` · MINOR · R4 §4.4 requires a vehicle identity on the dock appointment and does not specify one.**
*Gap.* R4 §4.4 has *"vehicle arrived / departed at our dock → `PATCH` on `wh_dock_appointments`"*,
while R4 §3.6 forbids the port from carrying a vehicle. Both are right; the appointment still needs to
know which truck.
*Recommendation.* The three columns in `G-014`. The registration number is **denormalised at
appointment time** because the source row may be deleted and a detention dispute is about what was
true then. Same reasoning as `tms_trips.vehicle_number NOT NULL` even for 3PL (`:874`).
*Module.* `warehouse`. *Version.* **v1**.

**`G-016` · MAJOR · The gate belongs to neither module; copy the boom-barrier handler-list shape.**
*Gap.* Neither R4 nor the TMS document allocates the gatehouse. `tms_yard_entries` puts it in
logistics; a warehouse with a gate and no fleet also needs it.
*Why.* A gate event answers *which vehicle crossed a line when* — a device fact both modules consume.
*Recommendation.* Copy `BoomBarrierWebhookController(List<IBoomBarrierHandler>)`
(`automotive/.../controller/BoomBarrierWebhookController.java:44-48`, resolution at `:69`, the
enabled-handler fallback at `:168-175`) exactly: one webhook endpoint, a handler list, first enabled
handler whose key matches wins. `warehouse` registers a handler that stamps a dock appointment;
`logistics` registers one that stamps a trip. Neither owns the gate. **This is a live, working
precedent in this repo for a three-party device integration and it should not be redesigned.**
*Module.* `platform` or `warehouse` (host) + handlers in each. *Version.* **v1.1 (host)** / **v2 (logistics handler)**.

**`G-017` · BLOCKER · The vehicle's dual identity requires `whb_location_external_refs` in v1.**
*Gap.* Not in R4 §3, not in R4 §4, not in R1/R2/R3/R5.
*Why.* There are exactly three ways to let stock sit on a truck: (a) `whb_locations.vehicle_id` FK
into logistics — **base depends on logistics, fatal**; (b) logistics duplicates the location tree —
two location truths; (c) an external-refs table — the accounting precedent. Only (c) survives.
Retrofitting means every historic van-stock location has an unresolvable identity.
*Recommendation.* `whb_location_external_refs (id, location_id, source_module, external_id,
audit cols, uk(source_module, external_id))` — `acc_company_external_refs`
(`accounting-base/.../V600001:204-231`) with the parent swapped.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-018` · MAJOR · `ownership_transfer_point` on the source document, in v1.**
*Gap.* R4 §4.3 models *where* in-transit stock is; R5 §4.5 establishes that *whose* it is depends on
the Incoterm. Neither puts a column anywhere.
*Why.* Goods-in-transit at period end is a balance-sheet number. Under EXW/FCA it is ours from the
supplier's dock; under DDP it is not ours until delivery. Without the column the number is a guess and
the guess is made twice a year.
*Recommendation.* `wh_purchase_orders.ownership_transfer_point`, `wh_transfer_orders.
ownership_transfer_point`, `wh_receipts.ownership_transfer_point` — a **registry-backed code**, not a
CHECK (Incoterms are revised: 2010, 2020, and there will be another). v1 column, v2 behaviour.
*Module.* `warehouse`. *Version.* **v1 (column)** / **v2 (cut-off behaviour)**.

**`G-019` · MAJOR · "Delivery is not a movement" is true for a customer and false for our own branch.**
*Gap.* R4 §4.4 states *"delivery confirmed → not a movement — the stock already left at despatch"*.
Correct for a customer delivery; wrong for an inter-branch transfer arrival, which **must** post
`TRANSFER_ARRIVE`.
*Why.* An implementer reading only R4 §4.4 will build inter-branch transfers that depart and never
arrive — the exact failure R4 §4.3 warns about, reintroduced through the delivery path.
*Recommendation.* The three-row destination table of §2.3 in the FRD, and a service rule: the arrival
handler branches on `destination_is_internal`, which is a property of the destination location, not of
the delivery event.
*Module.* `warehouse` + `logistics`. *Version.* **v1 (the rule)** / **v2 (logistics path)**.

**`G-020` · MAJOR · `log_trips` + `log_gps_pings` will be the third GPS trip model in this monorepo.**
*Gap.* `field-service` already has one: `job_trips` (start/end lat-lng, `total_km`,
`total_duration_sec`, encoded `polyline`, `distance_method_used HAVERSINE/ROADS_API`) and
`job_track_points` (lat, lng, `recorded_at`, `accuracy_m`, `speed_mps`, `heading`) —
`field-service/.../V80007__Create_job_trips_and_track_points.sql:13-80`. `services` has a driver-assigned
doorstep pickup/drop with a seven-state ladder —
`services/.../V40197__Create_service_pickup_drop_tables.sql:15-60`. `dealer` has PDI vehicle movements.
*Why.* Four models of "a person moved a vehicle from A to B with GPS" is four sets of distance maths,
four map components and four mobile screens. It is also CLAUDE.md Principle #3 territory.
*Recommendation.* **Not a warehouse decision** — but it must be raised in the logistics FRD's
pre-flight, with `job_trips` named as the extraction candidate and an explicit answer to *"is
`log_trips` a generalisation of `job_trips` or a fourth copy?"*. Do **not** silently build the fourth.
*Module.* `logistics` + `field-service`. *Version.* **v2 (decision before build)**.

**`G-021` · MAJOR · State the two deletion tests as the seam's acceptance criterion.**
*Recommendation.* In the FRD: *"Delete `logistics`: `warehouse` still builds, migrates and runs; xrefs
resolve to null and the display resolver falls back to the raw external id. Delete `warehouse`:
`logistics` still builds, migrates and runs; consignments have no shipment."* Both are testable at
build time by toggling the `ENABLE_*` flags that already exist in `Dockerfile.backend` and
`start.sh` (R1 §2 rows 4, 10, 11).
*Module.* all. *Version.* **v1**.

**`G-022` · MINOR · Hubs are ambiguous; make the ambiguity a column.**
*Recommendation.* `log_hubs.stock_holding_warehouse_id UUID NULL`. Non-null ⇒ arrival posts
`TRANSFER_ARRIVE` into that warehouse; null ⇒ the trip's transit location persists across the stop.
Default when creating a hub: **prompt**, do not guess.
*Module.* `logistics`. *Version.* **v2**.

**`G-023` · MAJOR · Landed cost: the apportionment basis lives on the receipt, not on the freight charge.**
*Gap.* R4 §4.4 has `LANDED_COST_APPLY`; R5 §4.3 lists the basis (value/weight/volume/quantity/manual)
and the retrospective-revaluation problem. Neither says which side of the seam holds the basis. **No
prior-art TMS file connects freight to inventory value at all** (§1.7 row 53).
*Why.* If the basis lives on the freight charge, the same charge apportioned to two receipts can use
two bases and the layers disagree. If it lives on the receipt, the receipt owns its own cost story.
*Recommendation.* `wh_receipts.landed_cost_basis` (registry-backed) + `wh_receipt_landed_costs
(receipt_id, charge_source_document_type, charge_source_document_id, amount, currency, basis,
applied_movement_id)`. `logistics` supplies the charge; `warehouse` decides the apportionment;
`accounting` books the accrual. v1 is the column and the value-only movement type; v2 is the
apportionment engine and the partly-consumed-layer split.
*Module.* `warehouse`. *Version.* **v1 (columns + movement type)** / **v2 (engine)**.

**`G-024` · MINOR · Returnable packaging needs a per-counterparty balance, and nobody has one.**
*Gap.* R4 `F-060` makes packaging stock and billable. Neither R4 nor the TMS files model **pallet
pooling** — "we owe this customer 40 pallets, they owe us 12 crates".
*Why.* It is a real receivable/payable in kind, and it is the commonest source of end-of-year
disputes in distribution.
*Recommendation.* `whb_item_types` row `PACKAGING` in v1; `wh_returnable_balances (counterparty_id,
item_id, balance_qty)` **derived from movements against `CUSTOMER`/`SUPPLIER` virtual locations**,
never stored as a mutable column — the R1 `C-021` lesson. v2.
*Module.* `warehouse`. *Version.* **v1 (type)** / **v2 (balance report)**.

## 8.3 The supply-chain seam (§3)

**`G-025` · BLOCKER · The previous attempt coupled warehouse to a supply-chain module with ~84 FKs. Do not repeat it.**
*Evidence.* `SCC_MODULE_ISSUES_ANALYSIS.md:§4.4` records the per-table FK reference counts from
warehouse-core/warehouse-base into `scc_*`: 26 + 18 + 13 + 8 + 5 + 5 + 4 + 3 + 1 + 1. Summing their
numbers: **84**. (I did not recount the files — `supply-chain-core` and `warehouse-core` are **not in
this checkout**; `grep -rl "scc_"` over `classic` (excluding `node_modules`) returns exactly **two
files, both comments**: `platform/.../V663__Grant_branch_admin_branch_safe_permissions.sql:18` and
`platform/.../util/CountryStateRegistry.java:32` — the latter a Javadoc line still asserting *"the
platform stores them in `scc_warehouses.state` and friends"*, which is a ghost reference to a table
that does not exist here. `warehouse-core` survives only as a stale comment in `platform/.../V553:4`
and `product-lift/.../V800039:45`.)
*Why.* 84 FKs is not a seam. It also rotted: the same section records warehouse migrations
referencing **`scc_items`, `scc_drivers`, `scc_alert_rules`, `scc_alert_history` — tables that never
existed**, and `WAREHOUSE_CORE_ISSUES.md:WF-3` records `scc*`-named classes and a shared
`SCC_NAMESPACES` i18n registry living *inside* warehouse-core, with the untangling deferred.
*Recommendation.* **Zero FKs from `warehouse-base` into any supply-chain, logistics or vertical
table.** Enforced by `WarehouseBaseCouplingTest` assertion 3.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-026` · MAJOR · Adopt the demand-side rule of §3.1 and record it.**
*Recommendation.* *"Commitment ⇒ supply-chain. Quantity ⇒ warehouse. Obligation ⇒ accounting."* Then
the §3.2 table, applied mechanically.
*Module.* design set. *Version.* **v1**.

**`G-027` · BLOCKER · `warehouse-base` owns a thin counterparty; the rich profile lives elsewhere.**
*Gap.* No shared party master exists (R1 §7, `C-035`). Accessories receiving has **no supplier field
at all** (`accessories/.../dto/request/inventory/StockReceiptRequest.java:23-51`).
*Why.* Inbound receiving cannot name who shipped; lot traceability backwards, supplier hold rules and
RTV all key on it. And base cannot depend on `assets` or `automotive` to get one.
*Recommendation.* `whb_counterparties` (thin: code, name, legal_name, national_tax_id, is_active) +
`whb_counterparty_external_refs`, copying `accounting-base/.../V600001:61,204-231`. The rich profile —
terms, credit, bank, contacts, scorecard — belongs to `SC` or `accounting`.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-028` · MAJOR · `logistics` owns its own carrier and customer masters; the xref is the only join.**
*Why.* A fleet business with no warehouse must install `logistics` and work. An FK from `log_carriers`
into `whb_counterparties` makes that impossible.
*Recommendation.* `log_carriers` / `log_customers` as their own rows; the link is a
`whb_counterparty_external_refs` row with `source_module='LOGISTICS'`. Neither is the other's master.
*Module.* `logistics`. *Version.* **v2**.

**`G-029` · MAJOR · Name the trigger for extracting a `party-base`, and the count that makes it urgent.**
*Gap.* After this design the monorepo has up to **seven** party-shaped masters: automotive
`customers` (`automotive/.../V10010:9`), automotive `companies` (`V10002:11`), `asset_vendors`
(`assets/.../V60056:3-38`), `acc_companies` (`accounting-base/.../V600001:61`), `whb_counterparties`,
`log_carriers`, `log_customers`.
*Why.* Not stating it is how it gets discovered as a defect. Stating it makes it a budgeted decision.
*Recommendation.* Put the count and the cost in the FRD. **Trigger for extraction: the third module
that needs the same GSTIN to be authoritative for a statutory filing.** Before that, speculative;
after that, overdue.
*Module.* design set. *Version.* **v1 (the statement)** / **v3+ (the extraction)**.

**`G-030` · MINOR · `whb_counterparties` must not acquire payment terms or credit limits.**
*Why.* `asset_vendors` has `payment_term_id`, `credit_limit`, `currency`, `rating`
(`assets/.../V60056:3-38`) — right for a vertical, wrong for a stock ledger's counterparty. Once base
has a credit limit, base has an opinion about AR, and the accounting seam leaks.
*Recommendation.* A hard list of the seven permitted columns in the FRD, and a review rule: any new
column on `whb_counterparties` must be justified as *needed to post a movement*.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-031` · MINOR · `source_module` is an opaque string, and the registry that validates it arrives later.**
*Recommendation.* Copy `V600001:193-195` verbatim in spirit: `whb_*_external_refs.source_module
VARCHAR(30) NOT NULL` with **no FK** to `whb_source_systems`, even after that table exists — because a
low-numbered migration may not depend on a higher-numbered one, and because a de-installed module's
historic refs must still read. Validate in the service, not the schema.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-032` · MAJOR · The purchase order is the supply-chain seam's movable boundary.**
*Gap.* v1 needs receiving-against-a-PO long before an `SC` module exists (R2 `T-034` insists blind
receipt is first-class *precisely because* not everything has a PO — and by implication some things do).
*Why.* Exactly the `wh_carriers` situation on the demand side.
*Recommendation.* `wh_purchase_orders` + `_lines` in `warehouse` at **v1.1**, deliberately thin (no
approval workflow, no RFQ, no contract). Referenced from the receipt **by a stable code resolved
through a service**, so it relocates to `SC` in v3 as a refactor. Say so in the table comment.
*Module.* `warehouse`. *Version.* **v1.1 (thin)** / **v3 (relocate)**.

**`G-033` · MINOR · Blind receipt must remain first-class after the PO exists.**
*Why.* R2 `T-034`: *"If v1 only receives against a PO, the first pilot customer will key fake POs, and
fake POs become permanent."* Adding `wh_purchase_orders` at v1.1 is precisely when that pressure
appears.
*Recommendation.* `wh_receipts.receipt_type` is a **registry-backed code**, and `BLIND` is a seeded
row that no later migration may remove. Assert it in the invariants test alongside the `ACCESSORIES`
reservation.
*Module.* `warehouse`. *Version.* **v1**.

**`G-034` · MAJOR · The three-way match belongs to accounting and needs two read APIs from us.**
*Gap.* R3 `:1421-1425` names the trap: receiving 11 against an invoice for 10 either breaks the match
or silently books free stock, and free quantity moves the unit cost.
*Recommendation.* `warehouse` exposes `GET /api/warehouse/receipts?po_ref=…` returning received
quantity **by PO line**, with the movement ids. Warehouse **never** holds a tolerance, a match status
or an invoice. `SC` holds the PO; `accounting` holds the invoice and owns the match.
*Module.* `warehouse` (API) + `accounting`. *Version.* **v2**.

**`G-035` · MAJOR · HSN is a string on the item, never an FK into a tax master.**
*Gap.* The prior product gave warehouse **3 FK references into `scc_hsn_tax_master`**
(`SCC_MODULE_ISSUES_ANALYSIS.md:§4.4`), and that master has a documented ambiguity bug: overlapping
effective-date ranges with `uk(hsn_code, effective_from)` only, so *"rate for HSN X on date D can
return two rows"* (`T-H3`).
*Why.* A stock ledger does not need a tax rate. It needs a classification code to print on a challan
and to hand to a tax engine.
*Recommendation.* `whb_items.tax_classification_code VARCHAR(8)` — a plain string. The HSN master, its
rates and its effective-dating belong to `accounting`/`warehouse-india`. Warehouse never joins.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-036` · MINOR · Reorder planning produces suggestions in `warehouse`, never purchase orders.**
*Recommendation.* R2 `T-084` verbatim: a `wh_replenishment_suggestions` grid (item, site, on hand,
allocated, on order, ROP, suggested qty, source, lead time) with an export and an event. The PO is
raised in `SC` or by a human. v1.1 for suggestions; MRP proper is `SC` v3.
*Module.* `warehouse`. *Version.* **v1.1**.

**`G-037` · MINOR · Drop-ship: decide now whether it produces movements at all.**
*Gap.* Supplier ships direct to customer; the goods never touch our building. Absent from every
sibling report.
*Why.* Two defensible answers — (a) no movements, it is a pure `SC`/`accounting` flow; (b) a
zero-duration movement pair through `SUPPLIER` → `CUSTOMER` virtual locations so the item's velocity,
supplier scorecard and customer history include it. Whichever is chosen, choosing it in v3 means
history is missing or double-counted.
*Recommendation.* **Decide in v1's FRD; implement in v2.** My recommendation is (b), because the
virtual locations already exist for double-entry (R2 `T-009`) and the alternative makes drop-shipped
items invisible to every warehouse report.
*Module.* design set. *Version.* **v1 (decision)** / **v2 (build)**.

**`G-038` · MINOR · Bonded/customs is a stock status plus a location, not a module.**
*Recommendation.* R5 §2.3 calls it *"the deepest schema consequence in this report"*. Two seeded rows
in v1 — `whb_stock_statuses.BONDED` (`is_shippable=false` without a clearance) and a
`whb_location_types.BONDED_ZONE` — cost nothing and make v2's `warehouse-india` customs pack possible.
*Module.* `warehouse-base`. *Version.* **v1 (rows)** / **v2 (`warehouse-india`)**.

## 8.4 The adapter contract (§4)

**`G-039` · BLOCKER · Write the adapter contract before the first adapter, as §4.2/§4.3.**
*Gap.* R2 `T-079` and R3 `E-006` both demand this; neither enumerates the permissions and
prohibitions.
*Why.* R2 `T-079` states the failure mode exactly: *"the generality question … is decided by the
first adapter"*, and the second copies the first.
*Recommendation.* §4.2 (thirteen MAYs) and §4.3 (ten MUST NOTs) as a document in the design set, cited
by every adapter issue.
*Module.* all. *Version.* **v1**.

**`G-040` · BLOCKER · `whb_item_external_refs` is a v1 table.**
*Gap.* R2 `T-033` lets the port identify an item by `id` **or** `sku` **or** `barcode`. A dealer's own
part number is none of those; nor is a services job-card's material code, nor an OEM's.
*Why.* Without it, either every adapter stores a warehouse UUID in its own tables (coupling), or the
port grows a per-vertical identification mode (base learns the vertical). Retrofitting leaves every
historic movement with an unresolvable external identity.
*Recommendation.* `whb_item_external_refs (id, item_id, source_module, external_id, external_label,
audit cols, uk(source_module, external_id))`. The port accepts `{source_module, external_id}` as a
fourth identification mode and resolves it here.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-041` · MAJOR · The display resolver is a `List<T>` bean registry, and base ships the fallback.**
*Gap.* R3 `E-004` asks for a resolver so a movement grid can render "RO-2026-004512" without base
importing `services`; it does not name the mechanism.
*Why.* R1 `WF-6`/`C-039` settles the mechanism from three live precedents:
`ExportService(List<ExportFormatHandler>)` (`platform/.../service/export/ExportService.java:31`),
`BoomBarrierWebhookController(List<IBoomBarrierHandler>)` (`:44-48`), and
`AccImportHandlerRegistry(List<AccImportHandler>)` (`accounting-base/.../AccImportHandlerRegistry.java:36-44`
— which explicitly handles the empty-list case: *"A base-only install may legitimately have none of
these on the classpath"*). **Not `@Primary`, which admits only one.**
*Recommendation.* `List<WhDocumentReferenceResolver>` indexed by `document_type_code` in a
`LinkedHashMap` (the `AccImportHandlerRegistry:38` shape). Base ships a fallback that renders
`source_document_type + ':' + source_document_id`, so an unresolved reference is ugly, never blank.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-042` · BLOCKER · Reservations need a holder quad and a TTL, or a cancelled trip leaks availability forever.**
*Gap.* R4 `F-028` makes reservations a table and `available = on_hand − reserved`. It does not make a
reservation **holdable by a module that is not warehouse**.
*Why.* Logistics reserves stock for a planned trip before any wave exists. When the trip cancels, base
must be able to answer *"release everything trip X held"* — and it cannot, if the only holder is an
internal allocation id. Orphaned reservations silently and permanently reduce availability, and the
symptom ("it says insufficient stock and there are 40 on the shelf") is the exact support call R4 §3.5
builds `simulate` for.
*Recommendation.* `whb_reservations.holder_system`, `.holder_document_type`, `.holder_document_id`,
`.holder_line_no`, `.expires_at`, plus `DELETE /api/warehouse/reservations?holder_system=&
holder_document_type=&holder_document_id=` and a scheduled expiry sweep. Note the R1 `:468` obligation:
a partial unique index (one active reservation per line) **cannot be `DEFERRABLE` in PostgreSQL**, so
the write path owes an explicit `flush()`.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-043` · MAJOR · Adapters register reference data by migration, in their own Flyway sub-band.**
*Recommendation.* R1 §12 already reserves adapter sub-bands: dealer V520000-520999, services
V521000-521999, field-service V522000-522999, assets V523000-523999, **logistics V524000-524999**. An
adapter's registry rows go in its own band, `ON CONFLICT DO NOTHING`, and must be individually
idempotent — R1 `C-047`: any Flyway failure triggers a blind `repair()` + one retry
(`FlywayConfiguration.java:246-264`).
*Module.* all. *Version.* **v1**.

**`G-044` · MINOR · `whb_number_series` should be module-scoped so logistics need not build a second generator.**
*Gap.* R1 `C-019`: no platform number-series table; `SequentialCodeGenerator` is scan-based and
**explicitly not gapless** (`platform/.../util/SequentialCodeGenerator.java:9-19,41-53`); the gapless
precedent is `assets` `*_sequences` + `@Lock(PESSIMISTIC_WRITE)`, with the race documented at
`AssetTagSequenceRepository.java:19-27`.
*Why.* An LR number must be gapless for the same statutory reason a GRN number is.
*Recommendation.* `whb_number_series (owning_module, series_code, prefix, next_value, …)` with the
assets locking shape. If logistics declines to use it, that is acceptable — but offering it costs one
column (`owning_module`) in v1 and saves a second generator.
*Module.* `warehouse-base`. *Version.* **v1 (the column)**.

**`G-045` · BLOCKER · There is no outbox anywhere in this repository; budget it as net-new.**
*Evidence.* `grep -rli "outbox"` over `platform`, `accounting-base`, `accounting`, `dealer`,
`automotive`, `services`, `assets` → **0 files** (computed). The only event-ish infrastructure is
*inbound* webhook logging (`automotive/.../V10108__Create_webhook_logs_table.sql`,
`services/.../V40015__Fix_service_webhook_logs_table.sql`).
*Why.* R4 `F-012`/`F-086` treat the outbox as a design choice; in this codebase it is also a
**capability that does not exist**, with no precedent to copy, no retry framework and no dead-letter
handling. Estimating it as "a table" will be wrong.
*Recommendation.* Budget: the table, the sequence cursor, the publisher job, retry with backoff, a
dead-letter grid, and a replay-from-cursor endpoint. `@Async` is not sufficient — R1's memory index
records `reference_async_notification_lazyinit` as a live trap.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-046` · BLOCKER · `whb_outbox_subscriptions` in v1, because logistics may be a separate deployable.**
*Divergence in emphasis from R4, stated.* R4 `F-086` specifies the outbox and says *"base knows no
consumers"* — correct. It does not specify **how** an out-of-process consumer subscribes, and an
in-process `List<WhMovementEventSubscriber>` cannot reach one.
*Why.* Adding the subscription table after three in-process subscribers exist means redesigning all
three, plus retrofitting delivery guarantees, retry state and a cursor per subscriber onto events that
have already been consumed.
*Recommendation.* `whb_outbox_subscriptions (id, subscriber_code, target_kind IN_PROCESS|HTTP,
endpoint_url, secret_ref, event_type_filter, last_delivered_sequence_no, is_active, …)` in v1, with
only the in-process path implemented. The HTTP path is v1.1. The **table** is v1.
*Module.* `warehouse-base`. *Version.* **v1 (table)** / **v1.1 (HTTP delivery)**.

**`G-047` · MAJOR · The loose-coupling test is "zero commits to `warehouse-base`", never "zero commits to `platform`".**
*Evidence.* `COMMON_FILTER_CONFIGS` is a TypeScript `const` at
`platform/frontend/src/utils/filterUtils.ts:346` with **210** scopes (computed
`grep -c "^  [A-Z_0-9]*: {"`), and a field absent from a scope is **silently dropped** before the API
call (CLAUDE.md CRITICAL #17; R1 `T-6`). `CacheConfiguration.java` is likewise a platform Java file
(R1: 202 registered names; an unregistered name throws on the **first call**, not at startup —
`CacheConfiguration.java:375-376`).
*Why.* An adapter with grids and cached statistics **must** touch two platform source files. A
contract that claims "zero commits outside my module" is false on day one, and a false invariant gets
ignored, taking the true ones with it.
*Recommendation.* State the caveat inside the contract, and scope the ratchet to `warehouse-base/`
only. Additionally: R1 `C-043` — a **filter-aware** statistics strip must **not** be given a
`statistics.*` cache name (`CacheConfiguration.java:190-196` records that exact mistake, issues #790,
#791). Most warehouse strips are filter-aware.
*Module.* design set. *Version.* **v1**.

**`G-048` · MINOR · Decide now whether `logistics` gets an adapter or posts directly.**
*Recommendation.* **Posts directly.** An adapter exists to translate a vertical that does not know
about warehouse; `logistics` is a first-class module of our own that can be built knowing the port.
An adapter between two of our own modules is a layer with no translation in it. Record the decision so
the fourth reviewer does not "discover" the missing adapter.
*Module.* design set. *Version.* **v1 (decision)**.

**`G-049` · MAJOR · Ship `warehouse-adapter-example` as a fixture, and make it the contract's proof.**
*Recommendation.* §4.4 layer 2. Zero screens, one of everything, one integration test using only the
public API. It is the cheapest possible answer to R2 `T-079`'s *"the generality question is decided by
the first adapter"* — because the first adapter is then a fixture we control, not a customer deadline.
*Module.* `warehouse-adapter-example`. *Version.* **v1**.

**`G-050` · MAJOR · The dealer vehicle-as-stock question is open; state the test rather than the answer.**
*Gap.* `pdi_vehicle_inventory` is a live, serialised, quantity-free inventory — one chassis per row,
26 `pdi_*` tables, with the repo's best occupancy model (append-only assignments, partial unique
indexes, occupancy **derived** not cached — `dealer/.../V20735:8,43-52,57-69`;
`PdiYardStorageLocationService.java:67`; `PdiStockYardMapper.java:83,118`).
*Why.* Migrating it is a rewrite of a live vertical, and R1 §5.2 notes it *"is quantity-free … the
right model for serial-tracked warehouse stock and useless for everything else"*.
*Recommendation.* **v1 posts nothing for vehicles.** The test for whether it should ever move:
*can `whb_serials` + `whb_movement_line_attributes` carry a chassis number, colour, variant and PDI
status without `warehouse-base` acquiring a single vehicle-shaped column?* If the answer needs a base
column, the answer is no, permanently. Revisit at v3.
*Module.* `warehouse-adapter-dealer`. *Version.* **v3 (decision)**.

**`G-051` · MAJOR · The accessories separation's real cost is the report nobody can write; say so in the UI.**
*Gap.* R1 `C-032` counts the duplication (17 tables, 71 backend files, ~12 web routes, 11 reports, 33
mobile screens, 25+ filter scopes, 12 permission resources) and names the real cost: *"there will be
two stock truths with no reconciliation and no unified report"*. The accessories reports read
`accessory_stock_levels` directly via `StockLevelRepository` (R1 §5.1), so a union is a compile-time
dependency.
*Why.* A user in an install running both will ask "how much of part X do we hold" and get two answers.
*Recommendation.* An explicit statement on both stock-summary screens ("this figure covers
{Warehouse|Accessories} stock only") and in the FRD. **Not** a union view — that would create exactly
the dependency the separation exists to avoid.
*Module.* `warehouse` + `accessories`. *Version.* **v1**.

**`G-052` · MINOR · Reserve `ACCESSORIES` in `whb_source_systems` rather than omitting it.**
*Recommendation.* One seed row, `is_reserved=true, is_claimable=false`, with the decision in the
column comment; asserted by `WarehouseBaseCouplingTest`. Omission invites a future author to claim the
string; a reserved row explains itself.
*Module.* `warehouse-base`. *Version.* **v1**.

## 8.5 Open registries (§5)

**`G-053` · BLOCKER · Thirteen vocabularies must be catalogues, not CHECK constraints.**
*Evidence for the pattern.* `acc_reason_codes.context` — *"NO CHECK constraint, deliberately. It is a
CATALOGUE, not an enum"* (`accounting-base/.../V600002:22-26`).
*Evidence for the failure.* `widget_definitions.chk_module`: 3 values (`platform/.../V234:36`) → 5
(`V276:10`) → 7 (`V557:18`), still missing `warehouse`, `accounting`, `logistics`.
`global_settings.chk_global_setting_module`: 5 (`V337:42`) → 7 (`V553:15`).
*Recommendation.* §5.2's thirteen tables, all with the §5.1 shape, all seeded in v1, all with
`owning_module`, none with a CHECK on `code`. Where a platform CHECK must still be widened, use the
merge idiom at
`accounting-base/.../V600200__Allow_accounting_in_platform_module_check_constraints.sql:55-95`.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-054` · MAJOR · `whb_movement_types` must carry behaviour columns, not just a name.**
*Why.* A row that is only `(code, name)` forces base to `switch` on the code somewhere, which
re-closes the vocabulary in Java. R4 `F-087` says "rows, attributes in a typed side table"; the
behaviour must be **columns on the type row**.
*Recommendation.* The nine behaviour columns of §5.2 row 1. Rule: **base reads behaviour columns; base
never reads a `code` literal.** Add an invariants-test scan for string literals equal to a seeded
movement-type code inside `warehouse-base/src/main/java`.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-055` · MAJOR · `whb_location_types` — the prior product broke exactly this.**
*Evidence.* `WAREHOUSE_CORE_ISSUES.md:DB-1`: `zone_type` and `location_type` CHECK constraints
*"dropped and recreated with completely different enum value sets"* at V200042, 36 versions after
creation — e.g. `PUTAWAY_STAGING/BULK_STORAGE/FORWARD_PICK/…` replaced by
`PICK_FORWARD/PICK_RESERVE/COLD/FROZEN/…`. The doc's own verdict: *"Anyone reading V200005/V200006 …
is misled — those files describe a table shape that never exists in a built DB."*
*Why.* This is not a hypothetical; it is the most direct evidence in the whole prior-art set that a
CHECK-constrained location vocabulary does not survive contact with a second requirement.
*Recommendation.* §5.2 row 5, with `IN_TRANSIT`, `MOBILE`, `VEHICLE`, `TRAILER` seeded in v1.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-056` · MAJOR · Stock status is a master with behaviour flags (restating R2/R4 because it is the most-copied mistake).**
*Recommendation.* §5.2 row 4, per R2 `T-004` and R4 `F-068`, with `badge_variant` added (§5.3 rule 2).
`stock_status_code` is in the balance **unique key** from v1.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-057` · MAJOR · I diverge from R2 `T-040`: counterparty role is a link table, not `partner_type ENUM`.**
*Divergence, stated.* R2 `T-040` proposes `wb_trading_partners (…, partner_type ENUM('SUPPLIER',
'CUSTOMER','CARRIER','INTERNAL'), …)`.
*Why I disagree.* Three reasons, each concrete. (1) The same legal entity is routinely two roles at
once — a carrier who is also a supplier of tyres, a customer who is also a job worker. An enum forces
two rows and two codes for one GSTIN. (2) `logistics` needs `TRANSPORTER` and `CONSIGNEE`, and
`warehouse-3pl` needs `CLIENT_3PL`, so the enum needs an ALTER per consumer — the exact failure §5
exists to prevent. (3) The evidence that four values is not enough is in the repo already:
`asset_vendors.vendor_type` has **six** and still would not cover a carrier
(`assets/.../V60056:3-38`).
*Recommendation.* `whb_counterparty_roles` (catalogue) + `whb_counterparty_role_links (counterparty_id,
role_code, is_primary, valid_from, valid_to)`. R2's table name and its "populated by adapters, do not
FK into `dealer` or `accessories`" rule are both retained.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-058` · MINOR · Reason-code `context` must be CHECK-free, copying `V600002` verbatim.**
*Recommendation.* §5.2 row 6, including `owning_module` so `logistics` can add an `NDR` context and a
`TRANSIT_LOSS` context in its own migration.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-059` · MINOR · UoM needs the statutory UQC code from v1.**
*Why.* R5 `S-011` — the e-way bill and e-invoice both require the government's Unit Quantity Code, and
it is not the same string as our display UoM. Adding it later means mapping every historic line by
hand.
*Recommendation.* `whb_uoms.uqc_code VARCHAR(10) NULL` in v1; populated in `warehouse-india`.
*Module.* `warehouse-base`. *Version.* **v1 (column)**.

**`G-060` · MAJOR · I diverge from R3 `E-007`: `item_type` is a registry row, not an enum.**
*Divergence, stated.* R3 `E-007` proposes `item_type ∈ (STOCK, NON_STOCK, SERVICE, KIT, CORE,
CONSUMABLE, ASSET)`.
*Why I disagree.* §1 shows four more types arriving with logistics alone — `RETURNABLE_EQUIPMENT`,
`TYRE`, `FUEL`, `PACKAGING` — and R4 `F-060` adds packaging independently. Seven values chosen before
the second consumer exists is the definition of a closed vocabulary.
*Recommendation.* `whb_item_types` per §5.2 row 10, seeded with R3's seven **plus** the four above.
R3's *content* is right; only its shape changes.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-061` · MINOR · Task type is a registry even though v1 has no RF device.**
*Why.* R2 `T-041` makes `wb_tasks` v1 with a single synchronous consumer. If `task_type` is an enum,
`LOAD` (logistics), `VAS` (3PL) and `FIT_TO_ASSET` (fleet) are each a base release.
*Recommendation.* §5.2 row 8.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-062` · MINOR · Disposition is a registry with a movement type on each row.**
*Recommendation.* §5.2 row 12, per R4 `F-052`. `warehouse-3pl` adds `RETURN_TO_CLIENT` and
`HOLD_FOR_CLIENT` in its own migration; `logistics` adds RTO-specific rows.
*Module.* `warehouse-base`. *Version.* **v1 (table + core rows)** / **v1.1 (screen)**.

**`G-063` · MINOR · `whb_attribute_keys` is the thirteenth registry and the one that stops JSONB creeping back.**
*Why.* R4 §3.3 mandates a typed attribute side table and forbids JSONB; without a **registered key
table**, "typed side table" degrades into a free-text key column, which is JSONB with extra steps and
no index. Note R1 `CM-3`: CLAUDE.md's blanket "NO JSONB" is overstated — the ratchet at
`platform/.../ArchitectureInvariantsTest.java:225-239` freezes a baseline — and warehouse grid
migrations **must** still emit `'[…]'::jsonb` for `grid_preferences`. The rule that holds is *no jsonb
on new business tables*.
*Recommendation.* §5.2 row 13, with `is_filterable` / `is_exportable` so an unregistered key can never
appear in a grid.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-064` · MAJOR · No TypeScript string-union may enumerate a registry vocabulary — and this needs the standards reviewer.**
*Gap.* CLAUDE.md TYPESCRIPT RULES #6 says *"String union types over TypeScript enums:
`'ACTIVE' | 'INACTIVE'`"*. Applied to a catalogue, that rule **re-closes on the frontend what the
backend opened**, and R2 §3.2 records that this codebase has a *documented recurring defect* of
exactly that shape.
*Why.* It is a genuine conflict between a house rule and this design, and resolving it in a warehouse
FRD without the standards owner is how two gates start contradicting each other.
*Recommendation.* My recommendation: unions stay for genuinely fixed two-or-three-value sets; the
thirteen catalogues use `type XCode = string` plus a runtime dropdown. **Referred to the standards
reviewer to adjudicate before the first warehouse page is written.**
*Module.* `warehouse` frontend + standards. *Version.* **v1**.

**`G-065` · MINOR · Badge variant and i18n fallback come from the registry row.**
*Recommendation.* `badge_variant` column on the status registry; `t('warehouse:statuses.<code>')` with
the registry row's `name` as the fallback, so a newly registered status renders in English rather than
as a raw key. This closes three of the four legs of the recurring status-drift defect (CHECK ↔ union ↔
variant map ↔ i18n) by construction rather than by discipline.
*Module.* `warehouse` frontend. *Version.* **v1**.

**`G-066` · MINOR · Every registry table needs a mobile counterpart consideration on day one.**
*Why.* CLAUDE.md Principle #3 makes web↔mobile mirroring mandatory, and R2 `T-051` calls the missing
mobile plan a BLOCKER. A registry-driven dropdown is *easier* on mobile than a hardcoded list, but
only if the mobile screen fetches it. R1 `C-044` corrects CLAUDE.md: `EntityListScreen`
`additionalFilters` now supports `type?: 'dropdown' | 'text'`
(`mobile/src/components/common/ListHeader.tsx:210-218`) — **date filters still are not supported**.
And the memory index records a third copy of every dropdown vocabulary in
`mobile/src/schemas/common.schemas.ts` zod enums.
*Recommendation.* Every registry gets a `/dropdown` endpoint in v1, and the mobile screens consume it
rather than a zod enum. State the zod-enum hazard in the mobile issue.
*Module.* `warehouse` + `mobile`. *Version.* **v1 (endpoints)** / **v1.1 (screens)**.

## 8.6 The irreversible list and sequencing (§6, §7)

**`G-067` · BLOCKER · Adopt §6's twenty-five items as the v1 schema commitment for the logistics seam.**
*Recommendation.* §6's table, merged with R4 §3.7's twelve and R5's "CANNOT BE ADDED LATER" list into
one consolidated v1 schema list before the first migration is written. Where two lists disagree on a
version, resolve **before** the migration, per R4's own appendix instruction.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-068` · MAJOR · Reserve the `logistics:*` permission namespace and the dependency rows in v1.**
*Gap.* Not in any sibling report.
*Why.* A logistics user who dispatches a trip posts a stock movement. If `warehouse:movements:post`
does not exist until v1 and `logistics:trips:dispatch` does not exist until v2, every role granted in
between must be re-granted by hand at upgrade.
*Recommendation.* Seed `warehouse:movements:post|reverse|view|simulate` in v1. Reserve the
`logistics:` prefix (documented, not seeded). At v2, insert `permission_dependencies` rows so
`logistics:trips:dispatch` implies `warehouse:movements:post`. **Insert rows only — never
`CREATE TABLE`**: `permission_dependencies` is a platform table (R1 `C-017`, `T-10`;
`platform/.../V248:17-30`), and the documented false premise is `dealer/.../V20501:10`. Columns are
`permission_id` / **`dependent_permission_id`** / `dependency_type`.
*Module.* `warehouse-base` + `logistics`. *Version.* **v1 (reserve)** / **v2 (rows)**.

**`G-069` · MAJOR · Reserve `V524000–V524999` for logistics now, and record the ordering rule.**
*Evidence.* R1 §12 already allocates it. R1 `C-001`/`C-002` prove why the band matters: V900000–V909999
holds **135** OEM-seed files and V910000–V919999 holds **434** per-client files with versions
deliberately reused across five client directories, and `FlywayConfiguration.java:296-327` renumbers
legacy history into those bands and then `DELETE`s duplicate-version rows — *so a collision does not
fail loudly, it deletes a history row and re-runs a migration*. All module migrations are physically
flattened into one directory at build time (`Dockerfile.backend:140-181`), which is why this is fatal
rather than cosmetic.
*Recommendation.* `logistics` proper (not the adapter sub-band) needs its own 10 000-wide band —
recommend **V540000–V549999**, inside the brief's V500000–V549999 reservation and disjoint from
base/app/adapters/3PL. Record: base < app < adapters < 3PL < logistics, so a partial install always
migrates in dependency order. **Do not copy `accounting-india`'s nested sub-band** (V602000–V602999
inside V600000–V609999) — R1 `T-15`/`C-004`.
*Module.* all. *Version.* **v1**.

**`G-070` · MINOR · R4's stated Flyway band for `warehouse-3pl` is stale; do not propagate it.**
*Divergence, stated.* R4 §5.3 and §5.6 place `warehouse-3pl` at **V930000–V939999**. R1 `C-001`/`WF-3`
show that region sits between two platform-reserved bands inside the seed/client numbering region that
`FlywayConfiguration` treats as its own — *"numerically safe, semantically a landmine"* — and the brief
now fixes V500000–V549999.
*Why flagged.* R4 §5.6 explicitly asks whoever assigns the bands to confirm the applied order *"before
the first `wh3pl_clients.owner_id → whb_owners.id` foreign key is written"*. That instruction stands;
only the numbers change.
*Recommendation.* `warehouse-3pl` at **V530000–V539999** per R1 §12. R4's §5.6 ordering caution
applies unchanged.
*Module.* all. *Version.* **v1**.

**`G-071` · MAJOR · v1 must post two movements for a transfer, even with no logistics module.**
*Recommendation.* R4 §4.3 verbatim: `TRANSFER_DEPART` → `TRANSIT-WH/IN_TRANSIT-<ref>` →
`TRANSFER_ARRIVE`, with the lineage quad on both. R4 prices it: *"one `location_type` value, one
`is_physical` boolean, and a stock-transfer service that posts two movements instead of one."* This is
the single highest ratio of future capability to present cost in the whole seam.
*Module.* `warehouse`. *Version.* **v1**.

**`G-072` · MINOR · Batch posting and `actor_type=DEVICE` are the driver's-device requirements; do not defer them.**
*Recommendation.* R4 `F-092` + §3.2. A route's forty scans sync as one batch with per-movement
idempotency and per-movement results; the actor is `DEVICE` with a `device_id`. Both are v1 columns
and both are unbackfillable diagnostics.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-073` · MINOR · `simulate` is the seam's support tool and belongs in v1.**
*Why.* R4 §3.5 calls it *"the single cheapest support tool in the product"*. For the logistics seam
specifically, it is what a trip planner calls before promising a load, and what answers the
orphaned-reservation symptom of `G-042`.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-074` · MINOR · The transit location must be per-reference, not one global `IN_TRANSIT` bucket.**
*Gap.* R4 §4.3's diagram writes `IN_TRANSIT-<trip>`, which implies per-trip locations, but does not
say so as a rule.
*Why.* One global transit location makes "what is on the road right now, on whose truck" a query with
no join, and a partial arrival cannot be attributed. Per-reference locations make in-transit ageing
and carrier claims work.
*Recommendation.* Transit locations are **created on demand** by the transfer service, keyed by the
source document reference, with a nightly job that closes empty ones. State the cardinality
explicitly, because "one transit location" is the obvious and wrong first implementation.
*Module.* `warehouse`. *Version.* **v1**.

**`G-075` · MINOR · In-transit ageing needs a report in v1.1, or the column is never exercised.**
*Why.* R4 §4.3 lists countable in-transit stock as a customer-visible benefit. A schema capability with
no screen is not verifiable and quietly rots.
*Recommendation.* A "Stock in transit" grid (transit reference, from, to, owner, item, qty, days in
transit, expected arrival) at v1.1, filter-aware, with statistics tiles — and **no `statistics.*` cache
name**, per R1 `C-043`.
*Module.* `warehouse`. *Version.* **v1.1**.

**`G-076` · MINOR · Cross-GSTIN transfer is the statutory reason `company_id` is a v1 column.**
*Why.* R5 §2.1 establishes that a transfer between GSTINs is a deemed supply needing a tax invoice and
an e-way bill, and R5 `S-025` adds that such an invoice needs an IRN. R4 makes `company_id` v1 for
multi-entity installs; the logistics seam gives the same column a second, statutory justification.
*Recommendation.* Restate the joint justification in the FRD so nobody proposes deferring it in a
single-entity pilot.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-077` · MINOR · The e-way bill's eight fields must all be derivable from v1 columns.**
*Why.* R5 §2.1's table lists eight EWB inputs and marks five MISSING in the prior set — from-PIN,
to-GSTIN/PIN, transport mode, transporter GSTIN/TRANSIN, vehicle number and type, approximate
distance. Four of those are **logistics** facts (mode, transporter, vehicle, distance) and three are
**warehouse** facts (from/to place and PIN, per-line HSN + UQC + quantity).
*Recommendation.* Confirm as an acceptance criterion that the warehouse three are v1 columns
(`whb_locations` address + PIN, `whb_items.tax_classification_code`, `whb_uoms.uqc_code` — `G-059`),
and that the logistics four reach the builder through the lineage quad, **not** through new base
columns. The builder itself is `warehouse-india`, v1.1.
*Module.* `warehouse-base` + `warehouse-india`. *Version.* **v1 (columns)** / **v1.1 (builder)**.

**`G-078` · MINOR · The prior product's e-way bill implementation is worth transplanting, not rebuilding — with caveats.**
*Evidence.* `SCC_MODULE_ISSUES_ANALYSIS.md:§2` lists a full compliance schema (`scc_compliance_providers`,
`_provider_environments`, `_credential_specs`, `scc_gstin_profiles`, `_registrations`, `_credentials`,
`_auth_sessions`, `_documents`, `_tasks`, `_api_logs`, `scc_irn_cancellations`, `scc_ewb_*`,
`_compliance_rules`, `_rule_conditions`), and R5 §2.1 records it as *"production-grade Ports & Adapters
… vendor-agnostic `ComplianceProviderPort`"*.
*The caveats, from the same document, and they are not small.* `scc_compliance_api_logs`,
`scc_irn_cancellations` and `scc_ewb_extensions` are **orphans with no repository and no service**
(`§4.1`) — the API-log table means API calls are *never actually logged*. `scc_compliance_api_logs` is
*"designed to store plaintext secrets"* (`T-H4`). `ComplianceDemoController` — a test harness that can
*"trigger live statutory filings"* — ships in production code (`§4.3`).
*Recommendation.* Transplant the **port/adapter shape and the rule engine**; rebuild the logging and
delete the demo controller. It lands in `warehouse-india`, and it must consume only §6 columns.
*Module.* `warehouse-india`. *Version.* **v1.1**.

## 8.7 Coordination between the six lenses

**`G-079` · BLOCKER · Three sibling reports use three different table prefixes. Settle it before the first migration.**
*Gap.* R2 §3 uses `wb_` (base) / `wh_` (app) / `w3_` (3PL) / `wa_<vertical>_` (adapters) — stated at
`R2:682`. R4 §3–§4 uses `whb_` / `wh_` / `wh3pl_`. R3 uses `wh_` for base tables (`wh_items`,
`wh_batches`, `wh_item_locations`).
*Why.* R1 `T-11` and `C-012`: the frontend merge is `cp -r`, **last write wins** across the whole
`src/` tree (`Dockerfile.frontend:80-177`), and R1 `T-12`/`C-011`: all module migrations are physically
flattened into one directory before the Maven build (`Dockerfile.backend:140-181`). A prefix disagreement
is not cosmetic here — and a design set that names the same table two ways will produce two tables.
*Recommendation.* Adopt **R4's** scheme (`whb_` / `wh_` / `wh3pl_`), because R4 §3 is the movement-port
specification and its names appear in the most cross-references, plus `wha_<vertical>_` for adapters
and `log_` for logistics. Rewrite the other reports' names in the consolidated FRD, once, with a
mapping table. **This is a coordination blocker, not a design flaw in any report.**
*Module.* design set. *Version.* **v1**.

**`G-080` · MINOR · Two reports disagree on where `wh_purchase_orders` lives; §3.2 row 11 resolves it.**
*Gap.* R2 `T-084` says the warehouse produces suggestions and *"the PO is raised elsewhere"*; R3 `#53`
and `E-027` put `wh_goods_receipts` in warehouse and imply a PO reference.
*Recommendation.* Both are right at different times: thin PO in `warehouse` v1.1 (`G-032`), relocating
to `SC` in v3. Record the resolution so it is not rediscovered.
*Module.* design set. *Version.* **v1**.

**`G-081` · MINOR · R3 `E-005`'s Flyway ranges are superseded by R1 `C-003`.**
*Gap.* R3 `E-005:495-496` reserves `warehouse-base V900000-V909999` etc. R1 proves those bands hold
135 and 434 files.
*Recommendation.* R1 §12's allocation is authoritative. Note it in the consolidated FRD so R3's
numbers are not copied.
*Module.* design set. *Version.* **v1**.

**`G-082` · MINOR · Agree one name for the movement port's tables across reports.**
*Gap.* R2 `T-033` proposes `wb_inbound_messages` for the persisted request; R3 `E-003` proposes
`wh_inbound_documents` / `wh_inbound_movements` with *"identical column names and semantics"* to
`acc_source_documents`/`_movements`; R4 §3.2/§3.3 specifies `whb_movements` / `whb_movement_lines` with
idempotency on the movement itself.
*Why.* These are not the same design. R3's is an inbound staging pair (the accounting shape); R4's puts
idempotency directly on the ledger row. Both work; shipping both means two envelopes, which is exactly
what R3 `E-003` warns against.
*Recommendation.* **R4's shape** (idempotency on `whb_movements`), plus R3's rule that a movement
forwarded to accounting carries the **same `idempotency_key`**. R2's `wb_inbound_messages` becomes an
optional raw-payload archive, not the ledger's front door.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-083` · MINOR · The 3PL condition and the adapter condition are the same test; state them together.**
*Recommendation.* R4 §5.3's condition (*"no table in `warehouse-base` or `warehouse` has a foreign key
to a `wh3pl_*` table; no service imports `ai.warehouse3pl`; no migration below the 3PL band references
a `wh3pl_` name"*) is §4.4 layer-1 assertions 1–3 with a different prefix. Implement **one** test with
a list of forbidden prefixes, so adding `log_` in v2 is a one-line change.
*Module.* `warehouse-base`. *Version.* **v1**.

**`G-084` · MAJOR · Four transport-shaped surfaces already exist; enumerate them in the logistics FRD's pre-flight.**
*Evidence.* `field-service` `job_trips`/`job_track_points`
(`field-service/.../V80007__Create_job_trips_and_track_points.sql:13-80`); `services`
`service_pickup_drop_requests` with `assigned_driver_id` and a seven-state ladder
(`services/.../V40197:15-60`); `automotive`/`services` boom-barrier gate events
(`automotive/.../controller/BoomBarrierWebhookController.java:44-48`;
`services/.../V40105__Add_entry_source_and_checkout_source_to_service_entries.sql:3`); `dealer`
`pdi_vehicle_movements` (`dealer/.../V20085`).
*Why.* CLAUDE.md Principle #3 requires enumerating every place a user-facing pattern exists **before**
implementing. A logistics module is the largest such enumeration this monorepo will ever do.
*Recommendation.* A pre-flight section in the logistics FRD naming all four, with a per-surface verdict
(reuse / generalise / leave alone), and an explicit answer on `job_trips` (`G-020`).
*Module.* `logistics`. *Version.* **v2 (before build)**.

**`G-085` · MINOR · Driver/vehicle masters overlap platform HR and dealer/services vehicle masters.**
*Gap.* `log_drivers` overlaps platform `users`/`user_details` and the `services` pickup/drop driver
(`assigned_driver_id UUID REFERENCES users(id)` — `V40197:43`). The prior product resolved this one way
worth knowing: `SCC_MODULE_ISSUES_ANALYSIS.md:§2` records *"NO `scc_drivers` table — drivers are
platform `users` with role `WMS_DRIVER`"*, split into licence/employment/documents child tables — and
`§3.2 T-M1` records the resulting mess: `scc_driver_employment` with a **quadruple** usable-state
(`employment_status` + `is_available` + `current_availability_status` + `is_active`), where *"is this
driver usable is ambiguous"*.
*Recommendation.* Drivers are platform users with a role plus `log_driver_profiles` (one row, one
status column). **Not** four availability flags. Outside my lens to decide; inside it to flag, because
a driver holds van stock (`G-013`) and "is this driver usable" then gates a stock movement.
*Module.* `logistics`. *Version.* **v2**.

**`G-086` · MINOR · Record what this lens did not verify.**
See §9.

---

# §9 — UNVERIFIED, and what would verify it

| Claim | Why not verified | What would verify it |
|---|---|---|
| Whether `supply-chain-core` / `warehouse-core` exist in any *other* checkout, and whether their code matches their issue documents | Neither module is in `classic` — `grep -rl "scc_"` returns one comment line (`platform/.../V663:18`), and `warehouse-core` survives only in comments (`platform/.../V553:4`, `product-lift/.../V800039:45`). I read the issue documents, not the code | Locate the repo/branch that holds them, or accept the documents as the only record |
| The **84** FK count of `G-025` | Computed by summing the ten per-table counts stated in `SCC_MODULE_ISSUES_ANALYSIS.md:§4.4`. I did not count files, because the files are not here | `grep -c "REFERENCES scc_" ` over the warehouse-core/warehouse-base migrations, wherever they live |
| Every competitor capability marked `?` or attributed to a vendor | Read from the 13 prior-art `.md` files only; I did not access any vendor's documentation | Vendor docs / a trial |
| Whether `tms_*` is a built module or a design document | `TMS_Functional_Document.md` reads as a build spec; no `tms_` table exists in `classic` (verified: `find . -name "V19000*.sql"` → none; no `tms` migrations) | Ask the author |
| Whether any live database has V900000+/V910000+ history rows renumbered by `fixLegacyMigrationVersions` | Needs a DB query; R1 flags the same gap | `SELECT version FROM flyway_schema_history WHERE version::int >= 900000` |
| Whether a `List<T>` bean-collection registry across **Maven modules** resolves correctly when only some are enabled | The three precedents are all within-module or platform-hosted. `AccImportHandlerRegistry:44-46` handles an empty list, which is evidence but not proof for the cross-module case | A Docker boot with `ENABLE_WAREHOUSE=true, ENABLE_WAREHOUSE_ADAPTER_*=false`, checking the registry log line |
| Whether `enable.logistics` relaxed-binds from `ENABLE_LOGISTICS` | No local Spring run (Docker-only build) | A Docker boot; R1 `WF-5` establishes the digit-segment precedent (`enable.insurance.360`, `pom.xml:195`) |
| Free `menus.sort_order` at L1 for a warehouse root and a future logistics root | Static analysis cannot see seeded rows (R1 §10) | `SELECT name, sort_order FROM menus WHERE menu_level = 1 ORDER BY sort_order` |
| Whether `mobile/src/screens/GenericScreen.tsx` gates a warehouse or logistics route | Not read | Read its `routePath.includes(...)` chain |
| Exact Incoterm revision to encode, and current e-way bill thresholds/validity | Statutory, and they move; R5 marks the same numbers "re-verify" | A tax adviser at FRD sign-off |

---

# §10 — Referred to other owners, not adjudicated here

- **Standards reviewer:** `G-064` — CLAUDE.md TYPESCRIPT RULES #6 (string unions) conflicts with §5's
  open registries on the frontend. Needs an owner's ruling before the first warehouse page.
- **Standards reviewer:** `G-047` — the "zero commits" ratchet cannot cover `platform/`, because
  `filterUtils.ts:346` and `CacheConfiguration.java` are platform source. The contract must say so.
- **R1's territory:** `G-069`/`G-070` — Flyway band assignment and applied-order confirmation on a
  **fresh** install as well as an upgrade (R4 §5.6 raises the same, with stale numbers).
- **Whoever owns the logistics FRD:** `G-007` (driver HR overlap), `G-020`/`G-084` (the fourth GPS trip
  model), `G-085` (driver master). All are logistics-internal; this lens only flags that a stock
  decision depends on them.

---

## Appendix — how to read this report alongside the other lenses

- Where I diverge from a sibling, the finding says **"Divergence, stated"** and gives the reason:
  `G-014` (dock-appointment version, vs R4 `F-080`), `G-046` (outbox subscriptions, extending R4
  `F-086`), `G-057` (counterparty role, vs R2 `T-040`), `G-060` (item type, vs R3 `E-007`), `G-070`
  (3PL Flyway band, vs R4 §5.3/§5.6), `G-081` (Flyway bands, vs R3 `E-005`), `G-082` (port table
  naming, R2 vs R3 vs R4). Everything else in R4 §3 and §4 I adopt unchanged.
- `G-079` is a **coordination blocker**, not a defect in any report: three sibling reports use three
  table-prefix schemes and the build flattens both migrations and frontend sources, so the
  disagreement is load-bearing.
- Anything marked `?` or listed in §9 is genuine uncertainty. Do not cite it as evidence.
- The `G-` ids should survive into the design set, so a later reviewer can tell what was considered and
  consciously placed rather than missed.
