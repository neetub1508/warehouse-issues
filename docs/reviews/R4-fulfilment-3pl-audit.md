# Lens R4 — fulfilment, eCommerce and 3PL audit

**2026-09-01.** Scored against the **stated architecture only**. At the time of writing
`warehouse-issues/` contains no FRD, no data model, no implementation plan and no task files —
`docs/contracts/`, `issues/` and `tools/` are empty directories. There is therefore nothing to
diff against, and this lens is not a conformance report. It is a **forward audit**: what the 3PL,
eCommerce-fulfilment and Indian-carrier world actually requires, mapped onto the four modules the
brief names, with every capability placed in a version.

| Module | Package | Flyway range | Role as stated |
|---|---|---|---|
| `warehouse-base` | `?` (not stated) | `?` (must sit **below** 3PL's range) | stock ledger engine · masters · generic inbound movement port |
| `warehouse` | `?` | `?` | the application — receiving, putaway, picking, packing, shipping, counting |
| `warehouse-adapter-<vertical>` | `?` | `?` | per-vertical translation into the port |
| `warehouse-3pl` | `ai.warehouse3pl` | **V930000–V939999** | owner-of-goods separation · storage & handling billing · client portal · SLAs |
| *(future)* logistics / supply chain | `?` | `?` | integrates **through** `warehouse-base`'s movement port |

Prior art inside the monorepo that this product supersedes rather than extends: `accessory_stock_levels`,
`accessory_inventory_transactions`, `accessory_stock_adjustments`, `accessory_storage_bins`,
`accessory_inventory_counts` in the accessories module, and `pdi_storage_slot_assignments` /
`pdi_vehicle_inventory` in dealer. Those are a per-vertical stock table, not a ledger; whether they
migrate onto the port is R1's question, not mine. I raise it only where it changes a day-one column.

## Scoring rule

The legend applies to the **competitor** columns:

| Mark | Means |
|---|---|
| `●` | ships it as a configurable, first-class object |
| `◐` | partial — present but hard-coded, single-variant, or bolted on via a partner product |
| `○` | absent |
| `?` | I am not confident; treat as unknown, do not cite this cell |

The **Our verdict / version** column is a *decision I am proposing*, not a score of something that
exists. Nothing exists. Where a row says `v1` it means: this must be in the first shippable cut or
it becomes disproportionately expensive later, and §2 gives the finding that argues it.

Version vocabulary, used consistently throughout:

| Version | Means |
|---|---|
| **v1** | the first shippable warehouse. Own-stock WMS + the whole movement port + every column that is unaddable later |
| **v1.1** | the first 3PL cut and the first Indian carrier cut. Ships within two quarters of v1; the schema it needs is already in v1 |
| **v2** | depth — rate shopping, cartonisation, waving, channel connectors, cold chain, disputes |
| **v3** | optimisation and standards — labour standards, slotting, EPCIS, RFID, automation interfaces, 4PL |

**No capability found in this audit is dropped.** Where I judge something should not be built at all,
it appears in §5.4 with a reason and a re-entry path, which is a placement, not a deletion.

## Headline

**Of 148 capabilities scored: 0 designed. By the version in which each first lands — 41 in v1,
57 in v1.1, 40 in v2, 10 in v3.** Nothing is dropped.

The distribution is the finding, but not in the direction it first looks. **v1 is a small release on
a wide schema.** §2.10 lists **forty** v1 items that are columns, keys or seeded tables carrying *no
v1 screen at all*. They exist because the ledger is append-only and a ledger cannot be retro-fitted
with a dimension it never recorded — and because `warehouse-3pl`, which ships in v1.1 at the
earliest, is metered from events that `warehouse-base` either emitted in v1 or lost forever.

Five structural conclusions, each argued in full below:

1. **`owner_id` is not a 3PL feature.** It is a ledger dimension, it is `NOT NULL`, and it belongs
   in `warehouse-base` v1 even though `warehouse-3pl` ships in v1.1 at the earliest. Consignment
   vendor stock, customer-owned repair stock, job-work material and bailed 3PL stock are the same
   shape; a warehouse that cannot say *whose* a unit is has to be rewritten to say it. This is the
   single most expensive column to add late in the entire design. (`F-001`, `F-002`, `F-010`)
2. **The billing meter is a base concession, not a 3PL table.** `warehouse-3pl` can build rate cards
   and billing runs at any time. It can never reconstruct *per-pick-line* or *per-carton* events that
   `warehouse-base` did not emit. If base v1's outbox emits `order.shipped` and not
   `pick.line.confirmed`, per-line handling billing is permanently unavailable, and per-line handling
   billing is how every audited 3PL prices. (`F-011`, `F-012`)
3. **India is not a localisation pack here; it is a second product surface.** AWB pools, NDR with a
   response SLA, COD remittance reconciliation, RTO as an inbound stock stream, weight-discrepancy
   disputes and e-way bills are not "carrier integration". They are six workflows with their own
   tables, their own screens and their own daily operators, and four of them post stock movements.
   No global product in the audited set has them; every Indian one does. (`F-042`…`F-047`, `F-025`)
4. **The movement port must be EPCIS-shaped without being EPCIS.** Every one of the nine capability
   areas resolves, at the ledger, to the same five questions GS1 EPCIS asks — *what · when · where ·
   why · who* — plus two the standard leaves to the implementer: *whose* and *how much is it worth*.
   A port with those seven axes serves the WMS, the 3PL meter, the future logistics module, a POS and
   a channel adapter without ever knowing they exist. A port that carries only item/qty/location
   forces a schema change for each of them. (§3)
5. **`warehouse-3pl` is a real module — but it is a thin module standing on a wide base concession.**
   About 30% of the 3PL capability surface is genuinely 3PL-only (rate cards, storage snapshots,
   billing runs, disputes, portal, SLA penalties). The other 70% is multi-owner stock handling,
   billable-event granularity, ownership-scoped access and lifecycle timestamps — all of which leak
   into `warehouse-base` and all of which are unaddable afterwards. A feature flag would be the wrong
   shape for the 30% and would not save a single column of the 70%. (§5)

Two things this lens found that are **decisions the design set must take before the first migration**,
not competitor gaps:

- **A single movement may need lines with two different owners.** A 3PL consuming its own packaging
  against a client's outbound order is one atomic event with a house-owned consumption line and a
  client-owned pick line. If the port balances per *movement* rather than per *(owner, item)*, that
  event cannot be posted and the consumable falls out of the ledger. (`F-059`)
- **In-transit stock is stock.** The moment a logistics module exists, a unit that has left warehouse
  A and not arrived at warehouse B must be *somewhere* in the ledger, or the trial balance of units
  breaks every time a truck is on the road. That requires an `IN_TRANSIT` location type and a
  warehouse row that maps to no building — a day-one decision in `warehouse-base`, taken long before
  the logistics module is funded. (`F-089`, §4)

---

# 1. THE CAPABILITY MATRIX

148 capabilities across nine areas.

**3PL/4PL platforms:** `EXT` Extensiv (3PL Warehouse Manager) · `LGW` Logiwa · `DAV` Da Vinci Unified ·
`CAM` Camelot 3PL (Excalibur) · `DEP` Deposco · `M4N` Made4net · `IFP` Infoplus · `SHH` ShipHero 3PL ·
`CCL` Synergy CartonCloud · `MIN` Mintsoft · `PVX` Peoplevox.
**eCommerce fulfilment / shipping:** `SBB` ShipBob · `SWR` Shipwire · `FUL` Fulfil.io · `VEQ` Veeqo ·
`SST` ShipStation/ShipEngine · `FBA` Amazon FBA/MCF · `FLX` Flexport.
**India:** `INC` Increff · `UNI` Unicommerce · `EEC` EasyEcom · `VIN` Vinculum · `WIQ` WareIQ ·
`SRF` Shiprocket Fulfilment · `CAR` Indian carrier APIs as a class (Delhivery / Ecom Express /
Blue Dart / XpressBees).

## 1.1 Owner of goods and multi-client

| # | Capability | EXT | LGW | CAM | IFP | SHH | CCL | SBB | UNI | WIQ | Our verdict / version |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Owner/client is a dimension on the stock record itself**, not a separate database or schema | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1 — `warehouse-base`.** `owner_id` NOT NULL on every ledger line, balance row, lot, serial, LPN and reservation (`F-001`) |
| 2 | Owner **types** beyond "3PL client" — house stock, consignment vendor, customer-owned, job-work material | ◐ | ◐ | ◐ | ◐ | ○ | ◐ | ○ | ◐ | ? | **v1 — base.** `whb_owners.owner_type` (`F-002`) |
| 3 | One physical bin holds **two owners'** stock (commingling permitted) | ● | ● | ● | ● | ◐ | ● | ● | ◐ | ? | **v1 — base.** Permitted by default; policy per location (`F-003`) |
| 4 | Commingle **policy** per location — single-owner / single-SKU / single-lot / free | ● | ● | ● | ◐ | ○ | ◐ | ? | ○ | ? | **v1 — base.** `whb_locations.commingle_policy` + `dedicated_owner_id` (`F-003`) |
| 5 | **Client-scoped users** with hard server-side row isolation | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1 — base + platform.** `whb_owner_user_grants`; scoped in the query, never in the UI (`F-004`) |
| 6 | **Per-client SKU master** — client A's `SKU-1` ≠ client B's `SKU-1` | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1 — base.** uk(`owner_id`,`sku`) — a global unique SKU is a one-way door (`F-005`) |
| 7 | **Item cross-reference / alias** table (client SKU, GTIN/EAN, vendor part, marketplace code) | ● | ● | ● | ● | ◐ | ● | ◐ | ● | ● | **v1 — base.** `whb_item_aliases` (`F-006`) |
| 8 | Same physical item shared across owners with per-owner attributes | ◐ | ◐ | ◐ | ● | ○ | ◐ | ○ | ◐ | ? | **v2.** Alias table covers 90%; a shared-catalogue object is v2 (`F-006`) |
| 9 | **Client onboarding** object — contract, go-live checklist, integrations, rate card, SLA | ● | ◐ | ● | ◐ | ◐ | ● | ● | ◐ | ? | **v1.1 — `warehouse-3pl`** (`F-007`) |
| 10 | **Client portal** — stock visibility, order entry, ASN entry, returns, reports | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1.1 read-only + order entry; v2 full** (`F-008`) |
| 11 | Portal **document vault** — client sees PODs, packing lists, inspection photos, invoices | ● | ◐ | ● | ◐ | ◐ | ● | ● | ◐ | ? | **v2 — 3pl** (`F-008`) |
| 12 | **Title transfer without physical movement** (owner change in place) | ◐ | ○ | ◐ | ◐ | ○ | ◐ | ○ | ○ | ? | **v1 (movement type) / v1.1 (screen) — base.** `OWNER_CHANGE` (`F-009`) |
| 13 | **Bailment** — client stock is off the 3PL's balance sheet; no inventory-value journal | ● | ◐ | ● | ◐ | ○ | ● | n/a | ◐ | ? | **v1 — base.** `is_financial` on the movement type + `cost_basis=ZERO_BAILMENT` (`F-010`) |
| 14 | Owner-scoped **virtual warehouse / zone allocation** (client X gets aisles 1–4) | ● | ● | ● | ● | ◐ | ● | ● | ◐ | ? | **v1.1 — base column, 3pl screen** (`F-003`) |
| 15 | Per-owner **numbering series** (order no., receipt no. visible to the client) | ● | ◐ | ● | ● | ○ | ● | ◐ | ● | ? | **v1.1 — 3pl.** Reuse the platform gapless-numbering pattern (`F-007`) |
| 16 | Client **contact and notification routing** — who gets the low-stock, the NDR, the invoice | ● | ◐ | ● | ● | ◐ | ● | ● | ◐ | ? | **v2 — 3pl** (`F-008`) |

## 1.2 3PL billing

This is the table that most sharply separates a 3PL WMS from an eCommerce WMS, and the one where our
architecture has the most to lose by deferring.

| # | Capability | EXT | CAM | DAV | IFP | LGW | M4N | CCL | SHH | MIN | Our verdict / version |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17 | **Billable-event meter** — an append-only, per-event, per-client table that every charge is rated from | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | **v1 (base emission) / v1.1 (the table) — 3pl.** `wh3pl_billable_events` (`F-011`) |
| 18 | Base WMS emits at **billable granularity** — per receipt line, per putaway, per pick line, per carton | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | **v1 — base. The single most important 3PL concession in the whole report** (`F-012`) |
| 19 | **Charge-code master** with category, UoM basis, taxability, revenue mapping | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | **v1.1 — 3pl** (`F-013`) |
| 20 | **Rate card per client**, versioned and effective-dated | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | **v1.1 — 3pl** (`F-014`) |
| 21 | **Volume tiers** on a rate line (first 500 orders @ x, next 2,000 @ y) | ● | ● | ◐ | ● | ◐ | ● | ● | ○ | ◐ | **v2 — 3pl** (`F-014`) |
| 22 | Storage basis: **per pallet** | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | **v1.1 — 3pl** (`F-015`) |
| 23 | Storage basis: **per bin / per location** | ● | ● | ● | ● | ● | ● | ● | ○ | ◐ | **v1.1 — 3pl** (`F-015`) |
| 24 | Storage basis: **per sq ft / per cubic** (occupied vs. allocated) | ● | ● | ◐ | ● | ◐ | ● | ● | ○ | ◐ | **v1.1 occupied / v2 allocated — 3pl** (`F-015`) |
| 25 | Storage basis: **per unit / per weight** | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1.1 — 3pl** (`F-015`) |
| 26 | Storage method: **month-end snapshot** | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | **v1.1 — 3pl** (`F-015`) |
| 27 | Storage method: **anniversary / receipt-date** (each pallet billed a month from its own arrival) | ● | ● | ◐ | ● | ○ | ◐ | ● | ○ | ◐ | **v1.1 — 3pl. Requires `occurred_at` + LPN from base v1** (`F-015`, `F-016`) |
| 28 | Storage method: **daily average / pallet-days** | ● | ● | ● | ● | ● | ● | ● | ○ | ● | **v1.1 — 3pl** (`F-015`) |
| 29 | Storage method: **split month** (1st–15th, 16th–EOM at half rate) | ● | ● | ◐ | ◐ | ○ | ? | ● | ○ | ? | **v2 — 3pl** (`F-015`) |
| 30 | **Free storage days / grace period** per client or per SKU | ● | ● | ◐ | ● | ◐ | ? | ● | ○ | ◐ | **v1.1 — 3pl** (`F-015`) |
| 31 | **Long-term / aged-inventory surcharge** (the FBA analogue) | ◐ | ◐ | ○ | ◐ | ○ | ? | ◐ | ○ | ○ | **v2 — 3pl.** `FBA ●` is the reference implementation (`F-015`) |
| 32 | **Daily storage snapshot** persisted, not recomputed | ● | ● | ● | ● | ◐ | ● | ● | ○ | ◐ | **v1.1 — 3pl.** `wh3pl_storage_snapshots` (`F-016`) |
| 33 | Handling: **inbound** per pallet / carton / unit / line / labour hour | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | **v1.1 — 3pl** (`F-011`) |
| 34 | Handling: **outbound** per order / line / unit / carton / pick | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1.1 — 3pl** (`F-011`) |
| 35 | **VAS billed by labour minute** with a timed task record | ● | ● | ◐ | ● | ◐ | ● | ● | ○ | ◐ | **v2 — `warehouse` (the timer) + 3pl (the rate)** (`F-023`) |
| 36 | **Accessorials** — pallets supplied, wrap, dunnage, hazmat, after-hours, detention, reschedule | ● | ● | ◐ | ● | ◐ | ● | ● | ○ | ◐ | **v1.1 — 3pl** (`F-018`) |
| 37 | **Minimum monthly charge** with automatic true-up line | ● | ● | ◐ | ● | ○ | ? | ● | ○ | ◐ | **v1.1 — 3pl** (`F-017`) |
| 38 | **Setup / onboarding / integration one-off charges** | ● | ● | ◐ | ● | ○ | ? | ● | ○ | ◐ | **v1.1 — 3pl** (`F-013`) |
| 39 | **Billing run** object with statuses, re-rate, and a frozen approved state | ● | ● | ● | ● | ◐ | ● | ● | ◐ | ● | **v1.1 — 3pl** (`F-019`) |
| 40 | **Dispute / credit** workflow raised from the portal | ◐ | ● | ◐ | ◐ | ○ | ? | ● | ○ | ○ | **v2 — 3pl** (`F-020`) |
| 41 | **Hand the invoice to an accounting/AR system**, do not print one | ● | ● | ◐ | ● | ◐ | ● | ● | ◐ | ● | **v1.1 — 3pl.** Emit an AR envelope to the accounting inbound port; build no numbering, no tax engine (`F-021`) |
| 42 | **Shipping charged through** to the client, with markup or at cost | ● | ● | ◐ | ● | ● | ● | ● | ● | ● | **v1.1 — 3pl** (`F-024`) |
| 43 | Ship on the **client's own carrier account** (zero pass-through) | ● | ● | ◐ | ● | ● | ● | ● | ● | ● | **v1.1 — `warehouse`.** `wh_carrier_accounts.owner_id` (`F-036`) |
| 44 | **Annual escalation / CPI uplift** clause on a rate card | ◐ | ● | ○ | ◐ | ○ | ? | ◐ | ○ | ○ | **v3 — 3pl** (`F-022`) |
| 45 | **Profitability per client** — revenue vs. cost to serve | ◐ | ● | ○ | ◐ | ○ | ● | ● | ○ | ○ | **v3 — 3pl** (`F-023`) |
| 46 | Warehousing **GST/SAC treatment** and place-of-supply for storage services (India) | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ◐ | ○ | **v1.1 — 3pl.** SAC `996729`; POS rule `?` — verify before build (`F-025`) |

## 1.3 Order sources and channel integration

| # | Capability | LGW | DEP | SHH | PVX | MIN | FUL | VEQ | UNI | EEC | VIN | Our verdict / version |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 47 | **Order source / channel master**, with a per-owner channel account | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1 — base (the FK) / v2 (connectors)** (`F-026`) |
| 48 | **Channel listing** — channel SKU ↔ our item ↔ owner | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1 — base.** Same table as the alias (`F-006`, `F-026`) |
| 49 | Marketplace connectors — Amazon, Flipkart, Myntra, Ajio, Nykaa, Meesho | ○ | ○ | ○ | ◐ | ○ | ○ | ◐ | ● | ● | ● | **v2 — adapter per channel.** The Indian marketplace set is `UNI/EEC/VIN ●` and nobody else (`F-026`) |
| 50 | Cart connectors — Shopify, WooCommerce, Magento, BigCommerce | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v2 — adapter** (`F-026`) |
| 51 | **Idempotent order import** keyed on (channel, channel order id) | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1 — base.** Same idempotency discipline as the port (`F-027`) |
| 52 | Order **update / cancel** sync back from the channel after import | ● | ● | ◐ | ● | ● | ● | ◐ | ● | ● | ● | **v2** (`F-027`, `F-034`) |
| 53 | **Reservation / allocation** as a first-class record, separate from on-hand | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1 — base.** `whb_reservations` (`F-028`) |
| 54 | **Allocation strategy** as data — FEFO, FIFO, nearest, fewest-touches, single-bin-preferred | ● | ● | ◐ | ● | ◐ | ● | ○ | ● | ◐ | ● | **v1 (FEFO/FIFO) / v2 (rest) — base** (`F-028`, `F-067`) |
| 55 | **Wave / batch planning** with a wave object | ● | ● | ● | ● | ◐ | ◐ | ○ | ● | ◐ | ● | **v2 — `warehouse`** (`F-029`) |
| 56 | Pick strategies — discrete, batch, cluster, zone, pick-and-pass | ● | ● | ● | ● | ◐ | ◐ | ○ | ● | ◐ | ● | **v1 discrete + batch / v2 rest** (`F-029`) |
| 57 | **Split shipment** — one order, many shipments, from one or many warehouses | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1 — base/`warehouse`.** The order↔shipment cardinality is a one-way door (`F-030`) |
| 58 | **Backorder** with a policy per client/channel (hold all vs. ship what you have) | ● | ● | ◐ | ● | ● | ● | ◐ | ● | ● | ● | **v1 (columns) / v1.1 (policy) ** (`F-031`) |
| 59 | **Order priority, ship-by and cut-off calendar** per channel and carrier | ● | ● | ◐ | ● | ◐ | ● | ○ | ● | ◐ | ● | **v1 — columns; v1.1 — the calendar** (`F-032`) |
| 60 | **Holds** — fraud, credit, address, stock, client request, compliance — as a record with a release audit | ● | ● | ◐ | ● | ◐ | ● | ◐ | ● | ● | ◐ | **v1 — `warehouse`.** `wh_order_holds` (`F-033`) |
| 61 | **Order edit after release** with automatic de-allocation and an amendment audit | ● | ● | ◐ | ● | ◐ | ● | ○ | ● | ◐ | ◐ | **v1.1 — `warehouse`.** The most-requested and least-designed feature in every WMS (`F-034`) |
| 62 | **Channel inventory publish rules** — buffer qty, per-channel split, min publish | ◐ | ● | ◐ | ● | ◐ | ● | ● | ● | ● | ● | **v2.** The oversell control (`F-035`) |
| 63 | **Order pooling across clients** for a shared carrier pickup | ◐ | ● | ○ | ◐ | ○ | ○ | ○ | ◐ | ○ | ? | **v2 — `warehouse`** (`F-029`, `F-040`) |
| 64 | **B2B / retail-compliance orders** — routing guide, ASN 856, label spec, chargebacks | ◐ | ● | ○ | ○ | ○ | ◐ | ○ | ◐ | ◐ | ◐ | **v3 — adapter.** Declare out of v1/v2 explicitly (`§5.4`) |

## 1.4 Shipping and carriers

| # | Capability | SST | SHH | LGW | MIN | SBB | FBA | SRF | WIQ | CAR | Our verdict / version |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 65 | **Carrier / service / account** master, account owned by 3PL **or** by client | ● | ● | ● | ● | ● | n/a | ● | ● | n/a | **v1 — `warehouse`** (`F-036`) |
| 66 | **Rate shopping** across carriers with the quote persisted | ● | ● | ● | ● | ● | ○ | ● | ● | ○ | **v2 — `warehouse`.** `wh_rate_quotes` (`F-037`) |
| 67 | Rate-shop **rules** — cheapest, fastest, cheapest-meeting-SLA, client-preferred, zone-restricted | ● | ● | ● | ◐ | ● | ○ | ● | ● | ○ | **v2** (`F-037`) |
| 68 | **Cartonisation** — pick the box, 3D pack, multi-carton split | ◐ | ● | ● | ◐ | ● | n/a | ◐ | ◐ | ○ | **v2 — `warehouse`** (`F-038`) |
| 69 | **Packaging master** with dims, tare, max weight, cost, and its own stock | ◐ | ● | ● | ◐ | ● | n/a | ○ | ◐ | ○ | **v1 (master + stock) / v2 (algorithm)** (`F-038`, `F-060`) |
| 70 | **Dimensional weight** with a per-carrier per-service divisor | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1 — columns; v2 — the calculation** (`F-038`) |
| 71 | **Label generation and storage**, with void | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1.1 — `warehouse`** (`F-039`) |
| 72 | **Manifest / EOD close-out / handover** document | ● | ● | ● | ● | ● | n/a | ● | ● | ● | **v1.1 — `warehouse`** (`F-040`) |
| 73 | **Pickup scheduling** as a separate request from the label | ● | ◐ | ◐ | ● | n/a | n/a | ● | ● | ● | **v1.1 — `warehouse`.** Indian carriers require it; US carriers mostly do not (`F-040`) |
| 74 | **Address validation / normalisation** | ● | ● | ● | ● | ● | ● | ◐ | ◐ | ◐ | **v2** (`F-041`) |
| 75 | **Pincode serviceability** — prepaid / COD / pickup / ODA, per carrier | ○ | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | **v1.1 — adapter.** India-only; no global product has it (`F-041`) |
| 76 | **AWB / waybill pool** — pre-fetched number blocks held before a label exists | ○ | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | **v1.1 — adapter.** Without it you cannot label an Indian shipment at all (`F-042`) |
| 77 | **Tracking events** stored normalised **and** raw, webhook-idempotent | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1.1 — `warehouse`** (`F-043`) |
| 78 | **Delivery exceptions** with a normalised code vocabulary | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1.1** (`F-043`) |
| 79 | **NDR** — non-delivery report with a merchant response SLA and an action API | ○ | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | **v1.1 — `warehouse` + adapter.** India's second-largest daily workflow (`F-044`) |
| 80 | **COD** — amount carried, collected, and remitted | ◐ | ◐ | ◐ | ◐ | ○ | ○ | ● | ● | ● | **v1.1** (`F-045`) |
| 81 | **COD remittance reconciliation** — UTR, file import, per-shipment match, shortfall | ○ | ○ | ○ | ○ | ○ | ○ | ● | ● | ● | **v1.1 — `warehouse` (match) + accounting port (the receipt)** (`F-045`) |
| 82 | **RTO** as an inbound stock stream matched by AWB, with QC and put-back | ○ | ○ | ○ | ◐ | ○ | ◐ | ● | ● | ● | **v1.1 — `warehouse`.** 15–30% of Indian COD volume (`F-046`) |
| 83 | **Weight / dimension discrepancy dispute** with evidence images | ○ | ○ | ○ | ○ | ○ | ◐ | ● | ● | ● | **v2** (`F-047`) |
| 84 | **International documentation** — commercial invoice, HS, COO, incoterm, customs value | ● | ● | ◐ | ● | ● | ● | ● | ◐ | ● | **v3 — adapter** (`F-048`) |
| 85 | **Branded tracking page / customer notifications** | ● | ● | ◐ | ● | ● | n/a | ● | ● | ◐ | **v2** (`F-049`) |
| 86 | **Returns label** — pre-generated or on demand | ● | ● | ◐ | ● | ● | ● | ● | ● | ● | **v2** (`F-050`) |
| 87 | **Multi-piece shipment** — one AWB, many cartons, per-carton tracking | ● | ● | ● | ● | ● | ● | ◐ | ◐ | ● | **v1.1 — columns in v1** (`F-030`, `F-038`) |
| 88 | **Freight / LTL / FTL** shipping alongside parcel | ◐ | ◐ | ◐ | ○ | ● | n/a | ◐ | ◐ | ● | **v2 warehouse-side / future logistics module** (§4) |

## 1.5 Returns and reverse logistics

| # | Capability | EXT | LGW | SHH | PVX | MIN | SBB | FBA | UNI | EEC | WIQ | Our verdict / version |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 89 | **RMA** object — authorised return, expected lines, reason, window | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1.1 — `warehouse`** (`F-050`) |
| 90 | **Blind return** — goods arrive with no RMA, received first, matched later | ● | ● | ◐ | ● | ● | ● | ● | ● | ● | ● | **v1.1.** In India this is the *normal* case, not the exception (`F-050`) |
| 91 | **Return type** vocabulary — customer return · RTO · refused · recall · vendor return | ◐ | ◐ | ○ | ◐ | ◐ | ◐ | ◐ | ● | ● | ● | **v1 — base column, `F-054`.** An enum retrofit here rewrites the disposition rules |
| 92 | **Inspection / grading** with condition codes and photographs | ● | ● | ◐ | ● | ◐ | ● | ● | ● | ● | ● | **v1.1 — `warehouse`** (`F-051`) |
| 93 | **Disposition** vocabulary as data — restock sellable · restock unsellable · refurb · repack · scrap · RTV · donate · hold for client · return to client | ● | ● | ◐ | ● | ◐ | ● | ● | ● | ● | ● | **v1.1 — base (vocabulary) + `warehouse` (screen)** (`F-052`) |
| 94 | Each disposition produces a **specific, different stock movement** | ● | ● | ◐ | ● | ◐ | ● | ● | ● | ● | ● | **v1.1.** The port must already accept all of them in v1 (`F-052`) |
| 95 | **Refund / credit is emitted, not decided** — the warehouse tells the channel and stops | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1.1 — outbox event, never a refund screen** (`F-053`) |
| 96 | **Return-to-vendor** with a debit-note interface | ● | ◐ | ○ | ◐ | ◐ | ○ | ○ | ● | ● | ? | **v2 — `warehouse` + accounting port** (`F-056`) |
| 97 | **Marketplace return-claim window** — claim a short/wrong/damaged return within N days or eat it | ○ | ○ | ○ | ○ | ○ | ○ | ◐ | ● | ● | ● | **v2 — adapter.** Pure India; a real cash line for our customers (`F-055`) |
| 98 | **Refurbishment / repair loop** with a work order | ◐ | ◐ | ○ | ◐ | ○ | ○ | ○ | ◐ | ◐ | ? | **v2 — `warehouse`** (`F-058`) |
| 99 | **Returns portal for the end consumer** | ○ | ◐ | ● | ◐ | ● | ● | ● | ● | ● | ● | **v3 — declare out; it belongs to the channel, not the warehouse (`§5.4`)** |
| 100 | **Restocking fee / return handling charge** billed to the client | ● | ◐ | ○ | ◐ | ◐ | ● | ● | ◐ | ◐ | ? | **v1.1 — 3pl.** A charge code, nothing more (`F-013`) |

## 1.6 Kitting, VAS and light manufacturing

| # | Capability | EXT | LGW | DAV | IFP | SHH | DEP | M4N | FUL | INC | UNI | Our verdict / version |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 101 | **Kit / BOM master** per owner | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1.1 — base (master) ** (`F-057`) |
| 102 | **Virtual kit** — components allocated and picked at order time, never assembled | ● | ● | ◐ | ● | ● | ● | ● | ● | ● | ● | **v1.1** (`F-057`) |
| 103 | **Physical kit** — pre-assembled, holds its own stock, its own SKU | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1.1** (`F-057`) |
| 104 | **Work order** — assembly, disassembly, repack, relabel, QC, custom | ● | ● | ● | ● | ◐ | ● | ● | ● | ● | ◐ | **v1.1 — `warehouse`** (`F-058`) |
| 105 | **Balanced consume/produce movement** with cost roll-up from components to output | ● | ◐ | ● | ● | ○ | ● | ● | ● | ◐ | ○ | **v1 — the port must allow it; v1.1 — the screen** (`F-059`) |
| 106 | **Mixed-owner movement** — the 3PL's own packaging consumed against a client's order | ◐ | ○ | ◐ | ◐ | ○ | ◐ | ◐ | ○ | ○ | ○ | **v1 — base. Balance per `(owner,item)`, not per movement** (`F-059`) |
| 107 | **Consumables** — packaging as stock, decremented and billed | ● | ◐ | ● | ● | ○ | ● | ● | ◐ | ◐ | ○ | **v1.1 — `warehouse` + 3pl** (`F-060`) |
| 108 | **Yield, scrap and by-product** on a work order | ◐ | ○ | ● | ◐ | ○ | ● | ● | ● | ◐ | ○ | **v2** (`F-058`) |
| 109 | **Labour minutes captured on the work order** and billable | ● | ◐ | ◐ | ● | ○ | ● | ● | ◐ | ◐ | ○ | **v2** (`F-023`, `F-079`) |
| 110 | **Job work** — material sent out for processing and returned (India, s.143 / ITC-04) | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ◐ | ◐ | **v2 — adapter + accounting port.** `?` on ITC-04 current form (`F-061`) |
| 111 | **Print integration** — labels, barcodes, GS1-128, at the workstation | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1.1 — `warehouse`** (`F-062`) |

## 1.7 Traceability and compliance

| # | Capability | DAV | M4N | DEP | EXT | LGW | IFP | INC | UNI | FBA | Our verdict / version |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 112 | **Lot / batch** on the stock record and on the ledger line | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1 — base. NULLable column, day one** (`F-063`) |
| 113 | **Serial** on the stock record and on the ledger line | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | **v1 — base. Day one** (`F-063`) |
| 114 | **Piece-level unique barcoding** (every physical piece serialised — apparel model) | ◐ | ◐ | ◐ | ◐ | ◐ | ◐ | ● | ○ | ○ | **v2.** `INC ●` is the reference; it is a policy over the v1 serial column (`F-063`) |
| 115 | **LPN / licence plate** — a pallet or tote is an object you move as one | ● | ● | ● | ● | ● | ● | ● | ◐ | ● | **v1 — base. `lpn_id` on the ledger line, day one** (`F-064`) |
| 116 | **Nested LPN** — cases on a pallet, pallets in a container | ● | ● | ● | ◐ | ◐ | ◐ | ◐ | ○ | ● | **v2 — the `parent_lpn_id` column in v1** (`F-064`) |
| 117 | **Genealogy** — parent/child across assembly, repack, split, relabel | ● | ● | ◐ | ◐ | ○ | ◐ | ◐ | ○ | ○ | **v2 — base table, v1 movement lineage makes it derivable** (`F-065`) |
| 118 | **Recall** — "which orders received lot X", with a hold action | ● | ● | ● | ● | ◐ | ● | ● | ◐ | ● | **v2 — `warehouse`.** Answerable in v1 only if `F-063` lands (`F-066`) |
| 119 | **Expiry / FEFO allocation** | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1 — base** (`F-067`) |
| 120 | **Minimum remaining shelf life on dispatch**, per client and per channel | ● | ● | ◐ | ● | ◐ | ● | ● | ● | ● | **v1.1 — base rule table.** Amazon India and modern trade both enforce it (`F-067`) |
| 121 | **Stock status** as data — available · quarantine · damaged · hold · expired · pending-QC | ● | ● | ● | ● | ● | ● | ● | ● | ● | **v1 — base. Not a magic location** (`F-068`) |
| 122 | **Cold chain** — temperature zone on a location, excursion event, auto-quarantine | ● | ● | ◐ | ◐ | ○ | ◐ | ○ | ○ | ● | **v2** (`F-069`) |
| 123 | **GS1 identifiers** — GTIN, SSCC, GLN as first-class fields | ● | ● | ● | ◐ | ◐ | ◐ | ● | ◐ | ● | **v1 columns / v2 issuance** (`F-070`) |
| 124 | **GS1-128 / DataMatrix AI parsing on scan** (01 · 10 · 17 · 21 · 00 · 37 · 3202) | ● | ● | ● | ◐ | ◐ | ◐ | ● | ○ | ● | **v2 — `warehouse` scan service** (`F-070`) |
| 125 | **EPCIS event capture / export** (Object · Aggregation · Transaction · Transformation) | ◐ | ◐ | ○ | ○ | ○ | ○ | ○ | ○ | ◐ | **v3 — a projection over the port, not a second ledger** (`F-071`) |
| 126 | **RFID / EPC reads as a movement source** | ◐ | ● | ◐ | ○ | ○ | ○ | ◐ | ○ | ● | **v3** (`F-072`) |
| 127 | **Pharma batch-wise stock, drug licence, Schedule H** (India) | ● | ◐ | ○ | ◐ | ○ | ○ | ○ | ◐ | ○ | **v2 — adapter.** `DAV ●` for US pharma; India specifics `?` (`F-073`) |
| 128 | **Country of origin and HS code on the lot**, not just the item | ● | ● | ◐ | ◐ | ○ | ◐ | ◐ | ○ | ● | **v1 — column on `whb_lots`** (`F-063`, `F-048`) |
| 129 | **E-way bill and delivery challan** for stock movement (India) | ○ | ○ | ○ | ○ | ○ | ○ | ◐ | ● | ○ | **v1.1 — adapter; the data columns in v1** (`F-025`, `F-088`) |
| 130 | **Cross-GSTIN branch transfer is a taxable supply**, not a challan | ○ | ○ | ○ | ○ | ○ | ○ | ◐ | ● | ○ | **v1.1 — accounting port.** GSTIN lives on `branches` in this platform (`F-025`) |

## 1.8 Performance and SLA

| # | Capability | DEP | M4N | EXT | LGW | CCL | IFP | SBB | WIQ | Our verdict / version |
|---|---|---|---|---|---|---|---|---|---|---|
| 131 | **Lifecycle timestamps** at every stage of receipt, order, task, shipment | ● | ● | ● | ● | ● | ● | ● | ● | **v1 — `warehouse`. Unaddable: you cannot backfill a duration** (`F-074`) |
| 132 | **Dock-to-stock** hours | ● | ● | ● | ● | ● | ● | ● | ◐ | **v1.1 report over v1 columns** (`F-074`) |
| 133 | **Order cycle time** — release to ship, and receipt to ship | ● | ● | ● | ● | ● | ● | ● | ● | **v1.1** (`F-074`) |
| 134 | **On-time ship %** against a cut-off, with a working calendar | ● | ● | ● | ● | ● | ● | ● | ● | **v1.1 — needs the calendar from `F-032`** (`F-075`) |
| 135 | **Pick / pack accuracy**, mis-pick tracking | ● | ● | ● | ● | ● | ● | ● | ◐ | **v2** (`F-076`) |
| 136 | **Inventory accuracy** from cycle counts, with ABC-driven count schedules | ● | ● | ● | ● | ● | ● | ● | ◐ | **v1 count / v2 ABC schedule + accuracy metric** (`F-076`) |
| 137 | **SLA definition object** per client, per metric, with targets and exclusions | ◐ | ● | ● | ◐ | ● | ◐ | ● | ● | **v2 — 3pl** (`F-075`) |
| 138 | **SLA measurement and breach records**, client-visible | ◐ | ● | ● | ◐ | ● | ◐ | ● | ● | **v2 — 3pl** (`F-075`, `F-077`) |
| 139 | **SLA penalty / service credit** posted onto the billing run | ○ | ◐ | ◐ | ○ | ◐ | ○ | ○ | ◐ | **v3 — 3pl** (`F-078`) |
| 140 | **Labour tracking** — task times, units per hour, per operator | ● | ● | ◐ | ● | ● | ◐ | ● | ○ | **v2 — `warehouse`** (`F-079`) |
| 141 | **Engineered labour standards** and a productivity target per task type | ● | ● | ○ | ◐ | ○ | ○ | ○ | ○ | **v3** (`F-079`) |
| 142 | **Dock appointment scheduling** with adherence measurement | ◐ | ● | ◐ | ◐ | ● | ○ | ● | ○ | **v2 — `warehouse` (the door is a warehouse resource)** (`F-080`, §4) |
| 143 | **Slotting / re-slotting recommendations** | ◐ | ● | ○ | ◐ | ○ | ○ | ○ | ○ | **v3** (`§5.4`) |

## 1.9 The inbound movement port itself

Nothing in this section is a *feature* a customer asks for. Every row is an architectural property
that the nine areas above jointly demand. This is the section that decides whether the product has a
second life.

| # | Property | Who does it this way | Our verdict / version |
|---|---|---|---|
| 144 | **Append-only ledger, correction only by reversal** | every WMS with a defensible audit trail; the accounting design set already committed to it for journals | **v1 — base.** No `UPDATE`, no `DELETE`, ever (`F-082`) |
| 145 | **Producer-supplied idempotency key**, unique per source system | `SST/ShipEngine ●` (idempotency headers), `FBA ●`, `FLX ●`; most WMS `◐` (dedupe by source doc id only) | **v1 — base** (`F-081`) |
| 146 | **Business time vs. record time vs. effective date**, three separate columns | `CAM ●` (storage anniversary depends on it), `EXT ●`; most `◐` | **v1 — base** (`F-083`) |
| 147 | **Structured source lineage** — system · document type · document id · line no | `M4N ●`, `DEP ●`, EPCIS `bizTransactionList` `●`; most `◐` (one free-text ref) | **v1 — base** (`F-084`) |
| 148 | **Value-only movement** (zero quantity, non-zero value) for landed cost and revaluation | `FUL ●`, `DEP ◐`, ERP-class `●`; pure WMS `○` | **v1 — base movement type** (`F-088`) |

---

# 2. FINDINGS — `F-001` … `F-093`

**93 findings: 21 BLOCKER · 51 MAJOR · 21 MINOR.**

Each block carries: **severity · kind · module · version · products**. `Kind` is **schema** (a column,
key or table that must land in or before the version that first writes the data) or **feature**
(deferrable without rework) or **seam** (an interface decision between two modules).

A finding marked `schema · v1` with a version later than v1 in its title line means *the column lands
in v1, the screen lands later*. That combination is deliberate and is the whole point of this report.

---

## 2.1 Owner of goods and multi-client

### `F-001` · `owner_id` is a ledger dimension and must be `NOT NULL` in `warehouse-base` v1
**BLOCKER · schema · `warehouse-base` · v1 · Products: Extensiv, Logiwa, Camelot, Infoplus, CartonCloud, ShipHero, Deposco, Made4net, Unicommerce, WareIQ — all `●`**

**What they do.** Every 3PL WMS in the audited set treats the owner of the goods as a **column on the
stock record**, not as a tenant, not as a schema, not as a separate database. Extensiv's `CustomerId`
is on the receipt, the item, the location assignment, the order and every inventory transaction.
Camelot, Infoplus and CartonCloud are identical. This is not because they wanted multi-tenancy; it is
because a single physical count of a bin has to resolve to more than one balance sheet.

**What the architecture implies today.** The brief puts "owner-of-goods separation" inside
`warehouse-3pl` (`ai.warehouse3pl`, V930000+). Read literally, that says `warehouse-base` ships a
single-owner ledger and `warehouse-3pl` adds ownership on top. That is not implementable. Ownership
cannot be a join table hung off a ledger line, because:

- `whb_stock_balances` needs `owner_id` **in its unique key**, alongside item, location, lot, serial,
  LPN and status. Adding a column to a unique key on a table with production rows is a rebuild, not
  a migration, and every balance row already merged two owners' quantities into one.
- Every `SELECT` that computes availability, every FEFO allocation, every cycle-count variance and
  every storage snapshot changes shape.
- The historical rows cannot be backfilled. There is no rule that recovers *whose* a unit was in
  March from a ledger that did not record it.
- Every index, every grid filter (`filter_definitions`), every export and every statistics map is
  built for the wrong grain.

**Why it is not a 3PL question.** `owner_id` earns its place before any 3PL customer exists:
consignment stock held for a vendor, customer-owned units in for repair, material held under job work,
demo stock owned by an OEM, and — inside this monorepo already — dealer stock physically at a
workshop but owned by the finance company. `warehouse` v1 sets `owner_id` to the install's own house
owner row on every movement, so the code path is exercised from day one instead of lying dormant.

**Paste-ready requirement.**
> **FR-W001** · `owner_id` (UUID, `NOT NULL`, FK `whb_owners`) is present on `whb_movement_lines`,
> `whb_stock_balances`, `whb_reservations`, `whb_lots`, `whb_serials`, `whb_lpns`,
> `whb_item_aliases` and `wh_orders`/`wh_order_lines`/`wh_receipts`/`wh_shipments`. It participates
> in the unique key of `whb_stock_balances`: uk(`warehouse_id`,`location_id`,`owner_id`,`item_id`,
> `lot_id`,`serial_id`,`lpn_id`,`stock_status_code`), with the nullable members handled by a
> partial-unique or a `COALESCE`-to-nil-UUID discipline chosen once and applied everywhere. Every
> query in `warehouse-base` and `warehouse` filters by owner scope server-side. There is no
> "single-owner mode": `warehouse` v1 posts against the house owner row seeded by the first
> migration.

---

### `F-002` · `whb_owners` belongs in base, and an owner is not the same thing as a 3PL client
**BLOCKER · schema · `warehouse-base` · v1 · Products: Extensiv `●`, Camelot `●`, Infoplus `●`, CartonCloud `●`; most conflate owner with client `◐`**

**What they do — and where they are weak.** Extensiv, Camelot and Infoplus all have a single
"customer" object that means *both* "the party who owns this stock" *and* "the party we invoice".
For a pure 3PL that is fine. For us it is not, because `warehouse` v1 has owners and no clients at
all, and because consignment, job work and customer-owned repair stock are owners we never invoice
for storage.

**The two-object split.**

| Object | Module | Means |
|---|---|---|
| `whb_owners` | `warehouse-base` | **whose the goods are.** Every ledger line points at exactly one |
| `wh3pl_clients` | `warehouse-3pl` | **whom we bill.** FK to one owner (usually), plus contract, rate card, portal config, SLA |

**Paste-ready requirement.**
> **FR-W002** · `whb_owners` — (id, `owner_code` uk, `owner_name`, `owner_type` FK
> `whb_owner_types`, `party_id` nullable — a link to the platform/dealer customer or vendor record —
> `is_house` boolean, `default_stock_status_code`, `is_active`, standard audit columns).
> `whb_owner_types` is a **seeded table, not an enum**: `HOUSE`, `CLIENT_3PL`, `CONSIGNMENT_VENDOR`,
> `CUSTOMER_OWNED`, `JOB_WORK_MATERIAL`, `TRANSIT` (see `F-089`), `SUPPLIER_MANAGED`. Exactly one
> row has `is_house = true` per company and it is seeded by the first migration so `warehouse` v1
> has an owner to post against. `wh3pl_clients.owner_id` is a nullable FK **from** 3PL **to** base;
> base never references 3PL.

---

### `F-003` · Commingling is the default; the *policy* is the column
**MAJOR · schema · `warehouse-base` · v1 (column) / v1.1 (screen) · Products: Extensiv `●`, Logiwa `●`, Camelot `●`, CartonCloud `●`**

**What they do.** Every 3PL WMS lets two owners' stock sit in one bin, because bulk floor storage
would be uneconomic otherwise, and then constrains it per location: Extensiv and Camelot let a
location be dedicated to a customer; Logiwa constrains by SKU/lot for pick faces. Amazon's FBA is the
extreme case — deliberate commingling of identical GTINs across sellers, which is also why FBA has a
commingling *opt-out*, because counterfeits become everyone's problem.

**Why the column and not the code.** Whether a bin may hold two owners is a warehouse-design decision
that changes per aisle and per client contract. Hard-coding "commingling allowed" makes a pharma or
bonded client unsellable; hard-coding "one owner per bin" makes bulk storage uneconomic. Both are
one-line answers if the policy is data and a rewrite if it is not.

**Paste-ready requirement.**
> **FR-W003** · `whb_locations.commingle_policy` ∈ {`FREE`, `SINGLE_OWNER`, `SINGLE_ITEM`,
> `SINGLE_LOT`, `SINGLE_LPN`} default `FREE`, and `whb_locations.dedicated_owner_id` nullable FK.
> The port rejects a movement into a location whose policy the resulting balance would violate, with
> `LOCATION_POLICY_VIOLATED` naming the policy and the conflicting owner/item/lot. A **zone
> allocation** table `whb_zone_owner_allocations` (zone, owner, from/to date, allocated capacity,
> capacity uom) records which client has which aisles; it is read by the storage biller (`F-015`) for
> **allocated**-space pricing and by the putaway strategy. The screens land with `warehouse-3pl` in
> v1.1; the column and the port check land in v1.

---

### `F-004` · Client-scoped access is a base concern, and the platform's role model is global
**BLOCKER · schema · `warehouse-base` + platform · v1 · Products: all 3PL platforms `●`**

**What they do.** Extensiv, Logiwa, Infoplus and CartonCloud all issue portal logins bound to exactly
one customer, and every query in the product is filtered by that binding server-side. ShipBob's
merchant dashboard is the same object. It is the single feature a 3PL cannot sell without, because
showing client A client B's stock is a contract breach, not a bug.

**What we have.** The platform's roles are install-global; branch scoping exists but is record-level
and is the wrong axis (a client's stock is in *our* branch). The accounting design set hit the
identical wall on companies (`S-007` there) and the resolution should be the same shape here so the
platform grows one scoping mechanism rather than three.

**The specific hazard.** A portal user who is filtered in the UI but not in the query is
indistinguishable from a correct implementation until an export, a statistics tile, a dropdown
endpoint or a grid filter leaks. This codebase has ~77 grid identifiers and each one has an export
path and a statistics map; every one of them is a leak site.

**Paste-ready requirement.**
> **FR-W004** · `whb_owner_user_grants` — (user id, owner id, `access_level` ∈ {`FULL`, `READ_ONLY`,
> `PORTAL`}, granted_by, granted_at, revoked_at), uk(user, owner) on live rows. Resolution is
> **server-side and mandatory**: a request with no grant for the owner it names is rejected `403`,
> never returned empty, because an empty grid is indistinguishable from "no stock". A single
> `OwnerScopeResolver` produces the owner-id set for the session and every query service, export
> service, statistics map and dropdown endpoint in `warehouse-base`, `warehouse` and `warehouse-3pl`
> takes it as a parameter — enforced by a contract test that fails the build if a repository method
> that touches an owner-scoped table has no owner-set parameter. `PORTAL` additionally restricts to
> the portal's endpoint set and forbids export of other owners' identifiers.

---

### `F-005` · Item uniqueness is `(owner_id, sku)`, and a global unique SKU is a one-way door
**MAJOR · schema · `warehouse-base` · v1 · Products: all `●`**

**What goes wrong.** The natural first migration writes `uk_items_sku UNIQUE (sku)`. The first 3PL
client that arrives with `SKU-001` when another client already has `SKU-001` breaks it. The fix is
not a migration — by then there are orders, aliases, barcodes and grid preferences keyed on the item,
and merchants' SKUs are printed on cartons in a warehouse.

**Paste-ready requirement.**
> **FR-W005** · `whb_items` — uk(`owner_id`, `sku`). A **house** item (owner = the house row) and a
> client item with the same string are different rows and are permitted. `whb_items.item_code` (our
> internal, globally unique, system-generated) exists **in addition**, is what every FK points at,
> and is what appears on a bin label; `sku` is what the owner calls it and is what appears on the
> client portal and on channel feeds. Barcode uniqueness is scoped the same way and lives in
> `whb_item_aliases` (`F-006`), not on the item.

---

### `F-006` · One alias table, and it is also the channel-listing table
**MAJOR · schema · `warehouse-base` · v1 · Products: Extensiv `●`, Infoplus `●`, Unicommerce `●`, EasyEcom `●`, Vinculum `●`**

**What they do.** Unicommerce, EasyEcom and Vinculum exist largely *because* Indian sellers carry five
identifiers for one physical unit: their own SKU, the EAN, Amazon's ASIN/FNSKU, Flipkart's FSN, and
Myntra's style/option code — and the picker scans whichever is on the carton. Every one of them holds
these in a channel-listing table keyed by (channel, channel identifier).

**The consolidation.** Do not build `item_barcodes`, `item_client_skus` and `channel_listings` as
three tables. They are one table with a type column, and keeping them one is what makes "scan
anything, find the item" a single indexed lookup instead of a three-way union.

**Paste-ready requirement.**
> **FR-W006** · `whb_item_aliases` — (id, `item_id`, `owner_id`, `alias_type` FK
> `whb_alias_types`, `alias_value`, `channel_id` nullable, `uom_code` nullable, `is_primary`,
> `pack_qty` default 1, valid_from/valid_to, audit). `whb_alias_types` seeded:
> `OWNER_SKU`, `GTIN13`, `GTIN14`, `UPC`, `EAN`, `ASIN`, `FNSKU`, `FSN`, `MYNTRA_STYLE`,
> `VENDOR_PART`, `CUSTOMER_PART`, `INTERNAL_LEGACY`. uk(`owner_id`,`alias_type`,`alias_value`,
> `channel_id`) — deliberately **not** globally unique, because two owners legitimately carry the
> same EAN. `pack_qty` is on the alias, not the item, because a case barcode and a piece barcode are
> two aliases of one item with different multipliers — this is the column that stops a case scan
> booking one unit.

---

### `F-007` · Client onboarding is an object, not a checklist in a spreadsheet
**MAJOR · feature · `warehouse-3pl` · v1.1 · Products: Extensiv `●`, Camelot `●`, CartonCloud `●`, ShipBob `●`**

**What they do.** CartonCloud and Extensiv both model the client relationship as a record with a
contract period, a rate card version, an SLA, integration credentials, storage allocation and a
go-live state. It matters because a 3PL's growth is measured in clients onboarded per month and the
onboarding is where the rate card, the SKU import, the channel connection and the label spec are all
agreed and then forgotten.

**Paste-ready requirement.**
> **FR-W007** · `wh3pl_clients` — (id, `owner_id` FK base, `client_code` uk, legal name,
> `billing_party_id` — the accounting party, may differ from the owner — contract_start,
> contract_end, notice_period_days, `billing_cycle` ∈ {`MONTHLY`,`FORTNIGHTLY`,`WEEKLY`},
> `billing_day`, `currency_code`, `payment_terms_days`, `credit_limit`, `status` ∈
> {`PROSPECT`,`ONBOARDING`,`LIVE`,`SUSPENDED`,`OFFBOARDING`,`CLOSED`}, `go_live_date`,
> `minimum_monthly_charge`, `tax_profile_id`, audit).
> `wh3pl_client_onboarding_tasks` — (client, task_code, owner_user_id, due_date, completed_at,
> completed_by, notes) seeded from a template so every client is onboarded the same way.
> `wh3pl_client_number_series` — (client, document_type, prefix, next_number) reusing the platform's
> gapless-numbering service, because a client sees *their* order numbers, not ours.

---

### `F-008` · The client portal is the product, not a report
**MAJOR · feature · `warehouse-3pl` · v1.1 (read + order entry) / v2 (full) · Products: all 3PL `●`, ShipBob `●`**

**What they do.** Every audited 3PL platform ships a customer-facing portal and every one of them has
the same six surfaces: live stock by SKU, inbound ASN creation and status, outbound order creation
(single and CSV), order/shipment tracking, returns, and documents+invoices. ShipBob's merchant
dashboard is the same six with a better chart library.

**The staging that actually works.** Read-only visibility plus order entry is the 90% and can ship in
v1.1 on top of `F-004`'s grants. The expensive half — document vault, dispute raising, report
scheduling, per-client branding, API keys for the client's own developers — is v2.

**The trap.** A portal built as a second frontend with its own auth becomes a second product. Build it
as a **role** in the existing frontend with `PORTAL` grants (`F-004`), a restricted menu and a
restricted set of grid identifiers. The accounting set reached the same conclusion for its customer
portal and the reasoning transfers exactly.

**Paste-ready requirement.**
> **FR-W008** · The portal is a permission surface over the existing `warehouse` and `warehouse-3pl`
> screens, not a separate application. v1.1 surfaces: **Stock** (by item, lot, expiry, status,
> with an export), **Inbound** (create ASN, view receipt + discrepancy), **Outbound** (create order,
> CSV upload, cancel while unallocated, view shipment + tracking), **Returns** (view), **Billing**
> (view billing runs and their lines). v2 adds: document vault (`wh3pl_client_documents` linking
> to the platform `documents` table), dispute raising (`F-020`), scheduled reports,
> `wh3pl_client_api_keys` for machine access, and `wh3pl_client_notification_routes` — (client,
> event_code, channel ∈ {`EMAIL`,`WHATSAPP`,`WEBHOOK`}, address, is_active) so a low-stock alert or
> an NDR reaches the right person at the client.

---

### `F-009` · Title can change without the goods moving, and the ledger must be able to say so
**MINOR · schema · `warehouse-base` · v1 (movement type) / v1.1 (screen) · Products: Extensiv `◐`, Camelot `◐`, CartonCloud `◐`**

**What it is.** A client buys out its supplier's consignment stock; a 3PL client is acquired and its
stock transfers to the acquirer's owner code; goods on job work are deemed supplied; a vendor-managed
inventory unit is consumed and title passes at the moment of pick. In each case nothing physically
moves and the owner changes.

**Why it needs to be a movement and not an `UPDATE`.** The balance changes for two owners
simultaneously. If it is an update to `whb_stock_balances.owner_id`, the ledger no longer explains
the balance, the storage biller silently bills the wrong client for the whole month, and the
reconciliation ratchet (`F-091`) fails with no way to find the cause.

**Paste-ready requirement.**
> **FR-W009** · `OWNER_CHANGE` is a seeded `whb_movement_types` row with
> `requires_balanced_pairs = true` and `allows_mixed_owner = true`. It posts as two lines: a negative
> line on the outgoing owner and a positive line on the incoming owner, same item, same lot, same
> serial, same LPN, same location, same stock status, with `unit_cost` carried or restated per
> `cost_basis`. It is the same mechanism as `F-059`'s mixed-owner movement, which is why both must be
> settled in v1 even though neither has a v1 screen.

---

### `F-010` · Bailment — a 3PL must never post its clients' stock value to its own ledger
**BLOCKER · schema · `warehouse-base` · v1 · Products: Camelot `●`, Extensiv `●`, CartonCloud `●`; ShipHero `○`**

**What it is.** Goods a 3PL holds are a **bailment**. They are not the 3PL's inventory asset, they are
not in its closing stock, they do not appear in its balance sheet, and their value never touches its
P&L. What *does* touch its P&L is the storage and handling fee — and, if the goods are lost or
damaged, a liability. The audited 3PL-native products get this right by construction (Camelot's
customer-owned inventory has no GL effect); the eCommerce-native ones (`SHH ○`) simply do not model
value at all, which works until the first customer wants landed cost.

**Why it is a day-one column and not an accounting-adapter rule.** The decision "does this movement
produce an accounting envelope" is a property of the **movement**, made at post time, in the ledger.
If it is made downstream, the outbox has already emitted the event and either the adapter has to
re-derive ownership economics it cannot see, or someone writes a filter in the adapter that a later
adapter forgets. And once a year of movements has been emitted without the flag, the accounting
module's stock account has to be unwound by hand.

**Paste-ready requirement.**
> **FR-W010** · Two columns, both v1:
> - `whb_movement_types.is_financial` (boolean) — whether movements of this type are *capable* of
>   producing an accounting envelope at all (a putaway is not; a receipt is).
> - `whb_movement_lines.cost_basis` ∈ {`ACTUAL`, `STANDARD`, `AVERAGE`, `INFORMATIONAL`,
>   `ZERO_BAILMENT`} with `unit_cost`, `cost_currency_code`, `extended_cost`.
>
> The outbox emits an accounting envelope only when `is_financial = true` **and** `cost_basis ∉
> {INFORMATIONAL, ZERO_BAILMENT}`. `whb_owners.default_cost_basis` seeds the line default, so a
> `CLIENT_3PL` owner defaults to `ZERO_BAILMENT` and a `HOUSE` owner to the install's valuation
> method. `INFORMATIONAL` exists separately from `ZERO_BAILMENT` because a client's declared value
> is needed for **insurance and for a loss claim** even though it must never post — and the two
> cannot be one value if the difference is what an auditor asks about.

---

## 2.2 3PL billing

### `F-011` · The billable-event meter is the whole billing engine; everything else is a report over it
**BLOCKER · schema · `warehouse-3pl` (the table) / `warehouse-base` (the emission) · v1.1 · Products: Extensiv `●`, Camelot `●`, Infoplus `●`, Da Vinci `●`, Made4net `●`, Mintsoft `●`**

**What they do.** Extensiv's "Smart Billing", Camelot's Excalibur billing and Infoplus's billing all
have the same architecture: warehouse operations write **metered events**, a rating step applies the
client's rate card, and an invoice is the sum of rated events over a period. Nobody computes a bill by
querying the operational tables at month end, because operational tables get corrected, re-received,
cancelled and re-picked, and the bill has to reflect what happened, not what is currently true.

**The property that matters.** The meter is **append-only and reversible**, exactly like the stock
ledger. A cancelled pick does not delete its billable event; it adds a reversing one. This is what
makes a re-run of a billing period produce the same number twice and what makes a dispute resolvable
without archaeology.

**Paste-ready requirement.**
> **FR-W011** · `wh3pl_billable_events` — (id, `client_id`, `owner_id`, `warehouse_id`,
> `charge_code_id`, `occurred_at`, `effective_date`, `quantity` numeric signed, `uom_code`,
> `item_id` nullable, `lot_id` nullable, `lpn_id` nullable, `order_id` nullable, `receipt_id`
> nullable, `shipment_id` nullable, `work_order_id` nullable, `movement_id` nullable FK to base,
> `source_system`, `source_event_key` — **the idempotency key**, uk(`source_system`,
> `source_event_key`) — `rate_card_line_id` nullable until rated, `unit_rate`, `rated_amount`,
> `currency_code`, `billing_run_id` nullable, `status` ∈ {`METERED`,`RATED`,`BILLED`,`REVERSED`,
> `EXCLUDED`}, `reversal_of_event_id` nullable, `exclusion_reason_code` nullable, audit).
> **No `UPDATE` except the rating fields and `billing_run_id`.** A correction is a reversing row.
> `EXCLUDED` with a reason exists so a credit decision is a *recorded* act with an author, not a
> deleted row.

---

### `F-012` · The base outbox must emit at billable granularity, or per-line billing is permanently impossible
**BLOCKER · seam · `warehouse-base` · v1 · Products: every 3PL platform prices per line or per unit; ShipHero's late-added billing is `◐` precisely because its event stream was not built for it**

**This is the single most consequential concession in the report.** `warehouse-3pl` can be written in
v1.1, v2 or v3. `warehouse-base`'s event granularity is fixed the day the first outbox row is written,
because a bill for last quarter cannot be reconstructed from events that were never emitted.

**How the audited products price, and what each price needs.**

| Price basis | Event `warehouse-base` must emit | Emitted by a coarse design? |
|---|---|---|
| Per receipt line | `receipt.line.confirmed` with qty, uom, item, lot | no — a coarse design emits `receipt.completed` |
| Per pallet received | same, plus `lpn_id` and a pallet count | **no** — impossible without `F-064` |
| Per putaway | `putaway.task.completed` with from/to location, lpn | no |
| Per pick line | `pick.line.confirmed` with qty, item, location | **no** — the most common outbound price basis in the set |
| Per unit picked | same event, quantity dimension | no |
| Per carton / per package | `shipment.carton.packed` with dims and weight | no |
| Per order shipped | `shipment.confirmed` | yes — this is the *only* one a coarse design gives you |
| Per storage day | daily balance snapshot, which needs `occurred_at` (`F-083`) | derivable only if `F-083` and `F-064` land |
| Per labour minute | `task.completed` with start/end timestamps | no — needs `F-079` |

**Paste-ready requirement.**
> **FR-W012** · `warehouse-base` maintains `whb_event_outbox` — (id, `sequence_no` BIGINT gapless,
> `event_code`, `aggregate_type`, `aggregate_id`, `owner_id`, `warehouse_id`, `occurred_at`,
> `recorded_at`, `movement_id` nullable, `payload_ref` — a row id in a typed side table, never a
> JSONB blob (CLAUDE.md forbids JSONB) — `published_at` nullable, `attempt_count`).
> The **event vocabulary is fixed in v1** and includes, at minimum, the eight rows above plus
> `stock.movement.posted`, `stock.movement.reversed`, `count.variance.posted`,
> `return.line.dispositioned`, `workorder.completed`, `owner.changed`. Consumers (the 3PL meter, the
> accounting adapter, a channel adapter, the future logistics module) read by `sequence_no` cursor,
> at-least-once, and dedupe on (`consumer`, `sequence_no`). **Adding an event code later is cheap;
> adding a *dimension* to an event code later is not** — which is why `owner_id`, `lot_id`, `lpn_id`
> and the timestamps are on every event from day one even where v1 has no consumer for them.

---

### `F-013` · Charge codes are a master with a tax and revenue mapping, not strings on a rate line
**MAJOR · schema · `warehouse-3pl` · v1.1 · Products: Extensiv `●`, Camelot `●`, Infoplus `●`, Da Vinci `●`**

**Paste-ready requirement.**
> **FR-W013** · `wh3pl_charge_codes` — (id, `charge_code` uk, name, `charge_category` ∈
> {`STORAGE`,`INBOUND_HANDLING`,`OUTBOUND_HANDLING`,`VAS`,`ACCESSORIAL`,`SHIPPING_PASSTHROUGH`,
> `ADMIN_SETUP`,`MINIMUM_TRUEUP`,`SLA_CREDIT`,`ADJUSTMENT`}, `default_uom_code`, `is_recurring`,
> `is_pass_through`, `is_taxable`, `tax_code_id` nullable, `sac_hsn_code` — **India: warehousing and
> storage is SAC `996729`; supporting services in transport is the `9967` family** — `revenue_purpose_code`
> (the string the accounting module resolves to a GL account; do **not** store an account id here,
> because the accounting module owns the chart), `is_active`, audit.
> Seeded with the ~40 codes every audited product ships with, so a new client's rate card is built by
> pricing existing codes rather than inventing strings. `SLA_CREDIT` and `MINIMUM_TRUEUP` are charge
> codes, not special cases in the biller (`F-017`, `F-078`).

---

### `F-014` · Rate cards are versioned and effective-dated, and a billing run rates against the version live on the event date
**MAJOR · schema · `warehouse-3pl` · v1.1 (flat) / v2 (tiers) · Products: Extensiv `●`, Camelot `●`, Infoplus `●`, CartonCloud `●`, Made4net `●`**

**Why versioning is not optional.** Rates change mid-period, contracts are backdated, and a re-run of
March in June must reproduce March's number. A rate card without an effective date makes every
historical invoice unreproducible, which is the one thing a client's finance team will test.

**Paste-ready requirement.**
> **FR-W014** · `wh3pl_rate_cards` — (id, `client_id`, `version_no`, `effective_from`,
> `effective_to` nullable, `currency_code`, `status` ∈ {`DRAFT`,`ACTIVE`,`SUPERSEDED`}, approved_by,
> approved_at, `parent_rate_card_id` — a client card may inherit a standard card and override lines,
> which is how a 3PL prices 200 clients without 200 hand-built cards).
> `wh3pl_rate_card_lines` — (id, `rate_card_id`, `charge_code_id`, `uom_code`, `rate`,
> `minimum_charge`, `maximum_charge` nullable, `free_quantity`, `rounding_mode` ∈
> {`NONE`,`UP`,`NEAREST`,`DOWN`}, `rounding_increment`, `tier_from`, `tier_to`,
> `tier_basis` ∈ {`PER_EVENT`,`PERIOD_CUMULATIVE`}, `applies_to_item_group_id` nullable,
> `applies_to_channel_id` nullable, `applies_to_warehouse_id` nullable, `storage_method` nullable
> (`F-015`), `condition_priority`). Resolution is **most-specific-wins with an explicit priority
> order** and a **fail-rather-than-guess** rule: an unrated event blocks the billing run and names
> the missing (client, charge code, conditions) combination. It is never silently rated at zero.
> Tiers are v2; the `tier_*` columns land in v1.1 so the resolver never changes shape.

---

### `F-015` · Storage billing is four different algorithms and the client's contract names one
**MAJOR · schema+feature · `warehouse-3pl` · v1.1 (snapshot · anniversary · daily-average) / v2 (split-month · allocated-space · aged surcharge) · Products: Camelot `●` (the reference), Extensiv `●`, Infoplus `●`, CartonCloud `●`, Amazon FBA `●` for the surcharge model**

**What they do.** Camelot's Excalibur is the canonical implementation and is explicit about the four:

| Method | How it computes | What it needs from base |
|---|---|---|
| **Snapshot** | the position at a nominated instant (month end, or the 1st) × rate | balance at a date — needs `occurred_at` (`F-083`) |
| **Anniversary / receipt-date** | each pallet is billed for a storage month starting on *its own* receipt date; a pallet received on the 20th is billed 20th–19th | needs `lpn_id` (`F-064`) **and** the receipt date per LPN, per lot |
| **Daily average / storage-days** | Σ(daily units or pallets) ÷ days in period × rate, or × a per-day rate | needs a daily snapshot (`F-016`) |
| **Split month** | positions on the 1st and the 16th, each billed at half the monthly rate | as snapshot, twice |

Plus the bases: **per pallet · per bin/location · per unit · per weight · per cubic · per sq ft
(occupied) · per sq ft (allocated)**. And the modifiers every contract has: **free days** (goods
received in the last N days are not billed), **minimum billable quantity**, and — the FBA
contribution — an **aged-inventory surcharge** that steps up after 181/271/365 days, which is how a
3PL stops being a free long-term warehouse.

**Why anniversary is the one that catches people out.** It is the most common method in North American
3PL contracts and it is the only one that cannot be computed from a month-end balance. It requires
knowing, per pallet, when *that pallet* arrived — which requires the pallet to be an object in the
ledger (`F-064`) and the ledger to carry business time (`F-083`). Both are v1 base columns with no v1
screen. This row is the clearest single argument in the report for why `warehouse-base` v1 cannot be
"item, quantity, location".

**Paste-ready requirement.**
> **FR-W015** · `wh3pl_rate_card_lines.storage_method` ∈ {`SNAPSHOT_PERIOD_END`,
> `SNAPSHOT_PERIOD_START`, `ANNIVERSARY`, `DAILY_AVERAGE`, `SPLIT_MONTH`} and `storage_basis` ∈
> {`PALLET`,`LOCATION`,`UNIT`,`WEIGHT`,`CUBIC`,`SQFT_OCCUPIED`,`SQFT_ALLOCATED`}, with
> `free_days`, `minimum_billable_quantity`, and `wh3pl_storage_aging_bands` — (rate_card_line,
> from_day, to_day, rate_multiplier) for the surcharge. Each method is a named, separately tested
> rater over `wh3pl_storage_snapshots` (`F-016`); none of them queries `whb_stock_balances` directly,
> because the current balance is not last month's balance.

---

### `F-016` · The daily storage snapshot is persisted, not recomputed
**MAJOR · schema · `warehouse-3pl` · v1.1 · Products: Extensiv `●`, Camelot `●`, Da Vinci `●`, Infoplus `●`, Made4net `●`**

**Why persist it.** Recomputing a historical position by replaying the ledger is correct and is also
the query that takes four minutes per client per month on a real dataset — and it changes if anyone
backdates. Every audited product materialises it nightly. The persisted row is also the evidence a
client is shown when they dispute a storage line.

**Paste-ready requirement.**
> **FR-W016** · `wh3pl_storage_snapshots` — (id, `snapshot_date`, `client_id`, `owner_id`,
> `warehouse_id`, `storage_basis`, `item_id` nullable, `lot_id` nullable, `lpn_id` nullable,
> `location_id` nullable, `quantity`, `uom_code`, `oldest_receipt_date` — the anniversary anchor —
> `age_days`, `computed_at`, `computed_from_sequence_no` — the base outbox cursor at computation
> time, which is what makes a recomputation detectable). uk(`snapshot_date`,`client_id`,`owner_id`,
> `warehouse_id`,`storage_basis`,`item_id`,`lot_id`,`lpn_id`,`location_id`). A nightly job writes it;
> a re-run for a date **supersedes** rather than updates, with the superseded row retained, because a
> billed snapshot that silently changes is the same defect class as a mutable ledger.

---

### `F-017` · Minimum monthly charge with an automatic true-up line
**MAJOR · feature · `warehouse-3pl` · v1.1 · Products: Extensiv `●`, Camelot `●`, Infoplus `●`, CartonCloud `●`**

**What it is.** Almost every 3PL contract has a floor — "₹75,000 per month or actuals, whichever is
higher". If it is a manual adjustment at invoice time it is forgotten in month four, and it is the
single most common source of leaked 3PL revenue.

**Paste-ready requirement.**
> **FR-W017** · `wh3pl_clients.minimum_monthly_charge` + `minimum_scope` ∈ {`ALL_CHARGES`,
> `STORAGE_ONLY`, `HANDLING_ONLY`, `EXCLUDING_PASSTHROUGH`}. The billing run computes actuals in
> scope, and where they fall short posts **a billable event** on the seeded `MINIMUM_TRUEUP` charge
> code for the difference — not a hidden invoice line. It is visible in the meter, it is disputable,
> it reverses like anything else, and it appears on the client's portal with the arithmetic shown.
> Per-client, per-warehouse minima (`wh3pl_client_warehouse_minimums`) are v2.

---

### `F-018` · Accessorials are ad-hoc charges with an author and a reason, and they need a screen
**MAJOR · feature · `warehouse-3pl` · v1.1 · Products: Extensiv `●`, Camelot `●`, Infoplus `●`, Made4net `●`, CartonCloud `●`**

**What it is.** Pallets supplied, stretch wrap, dunnage, hazmat handling, temperature handling,
after-hours receiving, detention/demurrage on a waiting vehicle, a rescheduled dock slot, a
photograph requested by the client, a manual count. Some are captured by the system (a dock
appointment missed); most are keyed by a supervisor who has to be able to key them in thirty seconds
against a client, a date and a reason.

**Paste-ready requirement.**
> **FR-W018** · A **Manual Charge** screen writing `wh3pl_billable_events` directly, with
> `source_system = 'MANUAL'` and `source_event_key` = the screen's own record id, requiring client,
> charge code, quantity, date, reason and an optional link to a receipt/order/shipment. Permission
> `wh3pl_manual_charges:create`, and an approval threshold above which a second user must approve —
> because an unreviewed manual charge on a client's invoice is how a 3PL loses a client. Auto-captured
> accessorials (detention from `F-080`'s appointment record, after-hours from the receipt timestamp
> against the client's calendar) write the same table with their own `source_system`.

---

### `F-019` · The billing run is an object with a frozen approved state
**MAJOR · schema · `warehouse-3pl` · v1.1 · Products: Extensiv `●`, Camelot `●`, Da Vinci `●`, Infoplus `●`, Made4net `●`, Mintsoft `●`**

**Paste-ready requirement.**
> **FR-W019** · `wh3pl_billing_runs` — (id, `client_id`, `period_start`, `period_end`, `run_type` ∈
> {`SCHEDULED`,`AD_HOC`,`FINAL_OFFBOARDING`}, `status` ∈ {`DRAFT`,`RATED`,`REVIEW`,`APPROVED`,
> `INVOICED`,`CANCELLED`}, `rated_at`, `approved_by`, `approved_at`, `invoiced_at`,
> `external_invoice_ref` — the accounting module's document id — `subtotal`, `tax_total`, `total`,
> `currency_code`, `unrated_event_count`, audit).
> `wh3pl_billing_run_lines` — (run, charge_code, description, quantity, uom, unit_rate, amount,
> `event_count`, drill-through to the events). Re-rating is permitted in `DRAFT`/`RATED` and
> forbidden after `APPROVED`; a change after approval is a **new run** of type `AD_HOC` carrying
> reversing events, never an edit. `unrated_event_count > 0` blocks the transition to `REVIEW`
> (`F-014`'s fail-rather-than-guess rule).

---

### `F-020` · Disputes are a record, and a credit is a charge code
**MAJOR · feature · `warehouse-3pl` · v2 · Products: Camelot `●`, CartonCloud `●`, Extensiv `◐`**

**Paste-ready requirement.**
> **FR-W020** · `wh3pl_billing_disputes` — (id, `billing_run_line_id` or `billable_event_id`,
> `raised_by_user_id`, `raised_at`, `raised_via` ∈ {`PORTAL`,`INTERNAL`,`EMAIL`}, `reason_code_id`,
> `disputed_quantity`, `disputed_amount`, `status` ∈ {`OPEN`,`INVESTIGATING`,`UPHELD`,`REJECTED`,
> `PARTIALLY_UPHELD`}, `resolution_note`, `resolved_by`, `resolved_at`, `credit_event_id` nullable).
> An upheld dispute posts a reversing or a `SLA_CREDIT`/`ADJUSTMENT` billable event — it never edits
> a billed line. The dispute is raisable from the portal, which is the point of building it.

---

### `F-021` · `warehouse-3pl` must not contain an invoice; it emits an AR document to the accounting port
**BLOCKER · seam · `warehouse-3pl` ↔ accounting · v1.1 · Products: Extensiv `●` (QuickBooks/Xero handoff), Camelot `●`, Infoplus `●`, Mintsoft `●`, CartonCloud `●`**

**What they do.** Not one audited 3PL WMS is the system of record for the receivable. Every one of them
rates, approves and then **hands off** — to QuickBooks, Xero, Sage or an ERP. They do this because an
invoice carries tax determination, numbering law, credit control, dunning, receipts, allocation and
statutory reporting, and a WMS that grows those becomes a bad accounting package.

**The specific hazard here.** This monorepo has (or is designing) an accounting module with an inbound
document port, gapless numbering, GST/e-invoice handling and an AR subledger. If `warehouse-3pl`
builds `wh3pl_invoices` with its own numbering and its own tax logic, we ship two AR subledgers in one
product and the first customer to run both discovers that their turnover appears twice.

**Paste-ready requirement.**
> **FR-W021** · An approved `wh3pl_billing_run` emits **one AR document envelope** to the accounting
> module's inbound port: party = `wh3pl_clients.billing_party_id`, date = `period_end`, currency,
> one line per `wh3pl_billing_run_lines` row carrying `revenue_purpose_code` (`F-013`),
> `sac_hsn_code`, quantity, uom, rate, amount and `tax_code_id`; a stable idempotency key of
> (`warehouse-3pl`, `billing_run_id`); and lineage back to the run. Accounting resolves the GL
> account, the tax, the place of supply, the number and the e-invoice. `warehouse-3pl` stores only
> `external_invoice_ref` and a status echo. **Where no accounting module is installed**, the same
> envelope is exportable as CSV/Excel and the run is marked `INVOICED` manually — the port shape does
> not change. There is no `wh3pl_invoices` table, no `wh3pl_invoice_numbers` sequence and no tax
> engine in this module, in any version.

---

### `F-022` · Rate escalation and indexation
**MINOR · feature · `warehouse-3pl` · v3 · Products: Camelot `●`, CartonCloud `◐`, Extensiv `◐`**

**Paste-ready requirement.**
> **FR-W022** · `wh3pl_rate_card_escalations` — (rate_card, effective_date, `basis` ∈
> {`FIXED_PERCENT`,`INDEX`}, percent, `index_code` nullable, `index_value_ref` nullable, applies_to
> ∈ {`ALL`,`STORAGE`,`HANDLING`}, status). Escalation **generates a new rate-card version** for
> review; it never mutates an active card. Deferred to v3 because a spreadsheet plus `F-014`'s
> versioning does the job for the first hundred clients — but the finding is recorded so it is not
> "discovered" as an oversight.

---

### `F-023` · VAS priced by labour minute needs a timed task in `warehouse`, and cost-to-serve needs it too
**MAJOR · feature · `warehouse` + `warehouse-3pl` · v2 · Products: Made4net `●`, Deposco `●`, Camelot `●`, Infoplus `●`, CartonCloud `●`**

**What it is.** "Relabel 4,000 units" is priced per unit if it is routine and per labour hour if it is
not. Both need the work order (`F-058`) to record who did it, from when to when, and how many units
came out. The same record is the only honest input to **profitability per client** — revenue from the
meter, cost from labour minutes plus space occupied.

**Paste-ready requirement.**
> **FR-W023** · `wh_labour_tasks` — (id, warehouse, `task_type_code`, `owner_id`, user_id,
> `started_at`, `ended_at`, `paused_seconds`, `units_processed`, `uom_code`, `reference_type`,
> `reference_id`, `work_order_id` nullable, device_id) in `warehouse`. It emits
> `task.completed` on the base outbox and the 3PL meter rates it against a `VAS` charge code with
> `uom = LABOUR_MINUTE`. Cost-to-serve (`wh3pl_client_profitability`, v3) joins metered revenue to
> labour minutes × a loaded rate and to storage snapshot × a space cost.

---

### `F-024` · Shipping is charged through at cost, at cost+markup, at a published tariff, or not at all
**MINOR · schema · `warehouse-3pl` · v1.1 · Products: all 3PL `●`**

**What it is.** Four distinct commercial arrangements, and a 3PL runs all four simultaneously across
its client base: (a) the 3PL's carrier account, billed at the carrier's actual charge; (b) the same
plus a percentage or per-shipment markup; (c) the 3PL's own published tariff by weight and zone,
unrelated to what the carrier charged; (d) the **client's own carrier account**, where the 3PL bills
nothing for freight and only handles.

**Paste-ready requirement.**
> **FR-W024** · `wh3pl_clients.freight_billing_mode` ∈ {`AT_COST`,`COST_PLUS_PERCENT`,
> `COST_PLUS_FIXED`,`OWN_TARIFF`,`CLIENT_ACCOUNT_NO_CHARGE`} with `freight_markup_percent` /
> `freight_markup_amount`, and `wh3pl_freight_tariffs` (client-or-standard, carrier, service, zone,
> weight band, rate) for `OWN_TARIFF`. Mode (d) requires `wh_carrier_accounts.owner_id` (`F-036`) and
> suppresses the `SHIPPING_PASSTHROUGH` charge entirely. The carrier's **actual** charge arrives
> later than the shipment (on the carrier invoice), so the pass-through event is metered at the
> quoted amount and **reconciled** when the carrier invoice lands — which is `F-047`'s table doing
> double duty.

---

### `F-025` · India: warehousing GST, e-way bills, and the additional-place-of-business problem
**MAJOR · seam · `warehouse-3pl` + adapter + accounting port · v1.1 · Products: Unicommerce `●`, EasyEcom `●`, Vinculum `◐`; no global product `○`**

**Three separate obligations, none of which any global product in the audited set carries.**

1. **Warehousing services are taxable at 18% under SAC `996729`** (storage and warehousing). The
   place-of-supply rule for storage/warehousing changed in the 2023 amendments and I will not state
   it from memory — **`?`, verify with a tax adviser before the rating code is written**, because
   getting it wrong means every interstate 3PL invoice has the wrong tax head (CGST+SGST vs IGST)
   and a year of returns to amend.
2. **Movement of goods requires a document.** A stock transfer between two of our own warehouses
   needs a **delivery challan** under Rule 55 if it is not a supply, and an **e-way bill** above the
   threshold (₹50,000, state variations `?`) carrying Part A (invoice/challan, value, HSN,
   transporter) and Part B (vehicle number). A transfer between two branches with **different
   GSTINs** is a *taxable supply* and needs a tax invoice, not a challan — and in this platform GSTIN
   lives on `branches`, so the warehouse's branch determines which it is.
3. **A 3PL warehouse must usually be declared on the client's GST registration** as an additional
   place of business for the client to hold stock there. This is a client-onboarding obligation with
   a document, an effective date and an expiry, and it is a compliance risk the 3PL is asked about in
   every RFP.

**Paste-ready requirement.**
> **FR-W025** · (a) `wh3pl_charge_codes.sac_hsn_code` and `tax_code_id` (`F-013`); the AR envelope
> carries them and **the accounting module determines the tax** (`F-021`) — no tax logic in warehouse.
> (b) `wh_stock_transfers` carries `document_type` ∈ {`DELIVERY_CHALLAN`,`TAX_INVOICE`},
> `from_gstin`, `to_gstin`, `taxable_value`, `hsn_code`, `transport_mode`, `transporter_id`,
> `vehicle_number`, `distance_km`, `eway_bill_no`, `eway_bill_date`, `eway_bill_valid_until`,
> `eway_bill_status` — **the columns land in v1**, the e-way bill API adapter lands in v1.1, because
> a transfer posted in v1 without these columns cannot be e-way-billed retrospectively.
> (c) `wh3pl_client_registrations` — (client, gstin, state_code, warehouse_id, `is_additional_place`,
> certificate document ref, effective_from, effective_to) with an expiry alert.

---

## 2.3 Order sources and channel integration

### `F-026` · Channel is a master with per-owner accounts, and the connector is an adapter
**MAJOR · schema · `warehouse-base` (master) + `warehouse-adapter-<channel>` · v1 (master) / v2 (connectors) · Products: Unicommerce `●`, EasyEcom `●`, Vinculum `●`, Logiwa `●`, Peoplevox `●`**

**What they do.** Unicommerce, EasyEcom and Vinculum are, commercially, connector companies: Amazon,
Flipkart, Myntra PPMP, Ajio, Nykaa, Meesho, Snapdeal, JioMart, plus Shopify/Woo/Magento and the D2C
carts. The connector count is the sales pitch. What matters architecturally is that each connector is
a **per-owner credential** — a 3PL runs client A's Amazon account and client B's Amazon account side
by side and must never cross them.

**Paste-ready requirement.**
> **FR-W026** · `whb_channels` — (id, `channel_code` uk, name, `channel_family` ∈
> {`MARKETPLACE`,`CART`,`ERP`,`EDI`,`MANUAL`,`POS`,`API`}, `country_code`, is_active) in base,
> because the ledger's source lineage and the item alias both reference it.
> `wh_channel_accounts` — (id, `channel_id`, `owner_id`, account label, credential ref — stored via
> the platform's admin-settings secret masking, never in this table in plaintext — `sync_orders`,
> `sync_inventory`, `sync_shipments`, `sync_returns`, `last_order_cursor`, `last_error_at`,
> is_active) in `warehouse`. Each connector is `warehouse-adapter-<channel>` and posts orders and
> stock movements through the ports; **`warehouse-base` never names a channel vendor**.

---

### `F-027` · Order import is idempotent on (channel account, channel order id), and re-imports are updates with a version
**MAJOR · schema · `warehouse` · v1 · Products: all `●`**

**Paste-ready requirement.**
> **FR-W027** · `wh_orders` — uk(`channel_account_id`, `external_order_id`) where the channel account
> is not null, plus `external_order_version` / `external_updated_at` so a re-poll that carries an
> older version is discarded rather than applied. `wh_order_import_log` records every inbound payload
> reference, its decision (`CREATED`/`UPDATED`/`IGNORED_STALE`/`REJECTED`) and the rejection reason,
> because "the order never came through" is the single most common support call in this product
> category and it has to be answerable in one screen.

---

### `F-028` · Reservations are a table, not a column, and `available = on_hand − reserved`
**BLOCKER · schema · `warehouse-base` · v1 · Products: all `●`**

**What goes wrong without it.** The tempting design is `whb_stock_balances.qty_reserved`, incremented
and decremented. It fails on the first partial cancellation, the first expired reservation, the first
"why is 40 reserved when the orders only need 30", and it can never answer *which* demand holds a
unit — which is exactly what an allocation screen, a backorder release and a recall all need.

**Paste-ready requirement.**
> **FR-W028** · `whb_reservations` — (id, `owner_id`, `warehouse_id`, `item_id`, `lot_id` nullable,
> `serial_id` nullable, `lpn_id` nullable, `location_id` nullable — null means "reserved against the
> warehouse, not yet against a bin" — `stock_status_code`, `quantity`, `uom_code`,
> `demand_type` ∈ {`SALES_ORDER`,`TRANSFER_ORDER`,`WORK_ORDER`,`HOLD`,`SAFETY_STOCK`,`CHANNEL_BUFFER`},
> `demand_id`, `demand_line_id`, `priority` smallint, `reserved_at`, `expires_at` nullable, `status`
> ∈ {`SOFT`,`HARD`,`PICKED`,`RELEASED`,`EXPIRED`,`CANCELLED`}, `released_at`, audit).
> Availability is a computed projection, never a stored column that can drift.
> `whb_allocation_strategies` — (id, code, `sequence`, `sort_expression` chosen from a bounded set:
> FEFO, FIFO, LIFO, nearest-location, fewest-locations, single-LPN-preferred, highest-quantity-bin)
> with a per-(owner, item group, channel) assignment. **Bounded rows, no expression language** — the
> same discipline the accounting set applied to posting rules, for the same reason.

---

### `F-029` · Waving and pick strategy
**MAJOR · schema+feature · `warehouse` · v1 (discrete + batch) / v2 (wave object, cluster, zone) · Products: Deposco `●`, Made4net `●`, Logiwa `●`, Peoplevox `●`, Extensiv `●`, Unicommerce `●`**

**Paste-ready requirement.**
> **FR-W029** · v1 ships `wh_pick_tasks` — (id, warehouse, `owner_id`, order_line_id, item, lot,
> location, lpn, quantity, uom, `assigned_user_id`, `sequence_no`, status, started_at, completed_at,
> `short_quantity`, `short_reason_code`) and two strategies: **discrete** (one order, one picker) and
> **batch** (many orders, one pass, sorted at pack). v2 adds `wh_waves` — (id, warehouse, wave_code,
> `release_criteria_id`, planned_at, released_at, released_by, status, order_count, line_count) with
> `wh_wave_orders`, plus cluster and zone/pick-and-pass. **Cross-client waving** (`F-063` in the
> matrix, row 63) is v2 and requires the pick task to carry `owner_id` — which it does from v1.
> `short_quantity` and `short_reason_code` are v1 columns because a short pick is a stock movement
> (`COUNT_ADJUSTMENT` or a re-allocation) and because "why did we short" is the second question every
> client asks after "where is my order".

---

### `F-030` · One order, many shipments — the cardinality is a one-way door
**MAJOR · schema · `warehouse` · v1 · Products: all `●`**

**What goes wrong.** A `wh_orders.tracking_number` column is the natural first design and it is wrong
within a month: a multi-carton parcel shipment, a split across two warehouses, a backorder released
later, and an item that ships separately because it is oversize all produce more than one shipment.
Retrofitting means every screen, export, tracking webhook and channel confirmation changes.

**Paste-ready requirement.**
> **FR-W030** · `wh_shipments` — (id, `order_id` nullable — a shipment may exist without a sales
> order, e.g. a transfer or a sample — `owner_id`, warehouse, carrier, service, `carrier_account_id`,
> `tracking_number`, `master_tracking_number` nullable, ship_to address ref, `package_count`,
> `total_weight`, `weight_uom`, `declared_value`, `cod_amount`, `status`, timestamps per `F-074`).
> `wh_shipment_lines` — (shipment, order_line, item, lot, serial, lpn, quantity). `wh_shipment_cartons`
> — (shipment, carton_no, `packaging_type_id`, length/width/height, dim_uom, actual_weight,
> `dim_weight`, `billable_weight`, tracking_number, label ref). Three tables, in v1, even though v1
> ships one carton per shipment in practice.

---

### `F-031` · Backorder policy is per client and per channel
**MAJOR · schema · `warehouse` · v1 (columns) / v1.1 (policy) · Products: Logiwa `●`, Deposco `●`, Peoplevox `●`, Unicommerce `●`, Fulfil `●`**

**Paste-ready requirement.**
> **FR-W031** · `wh_order_lines.quantity_ordered / quantity_allocated / quantity_picked /
> quantity_shipped / quantity_cancelled / quantity_backordered` — six columns in v1; deriving
> backorder from two of them fails the moment a partial cancel lands. `wh_fulfilment_policies` —
> (owner, channel nullable, `partial_ship_allowed`, `min_fill_percent`, `backorder_hold_days`,
> `auto_cancel_after_days`, `substitute_allowed`) in v1.1.

---

### `F-032` · Priority, ship-by and a working calendar with cut-offs
**MAJOR · schema · `warehouse` · v1 (columns) / v1.1 (calendar) · Products: Deposco `●`, Made4net `●`, Logiwa `●`, Unicommerce `●`, ShipBob `●`**

**Why the calendar is not optional.** "Same-day dispatch if ordered before 2 pm" is the SLA every
client signs and every SLA measurement (`F-075`) divides by it. Without a working calendar, a 24-hour
SLA measured across Diwali reports a breach that the contract does not consider one, and the client
stops trusting the report.

**Paste-ready requirement.**
> **FR-W032** · `wh_orders.priority` smallint, `promised_ship_at`, `promised_deliver_at`,
> `sla_id` nullable — all v1. `wh_calendars` / `wh_calendar_days` (warehouse or client scoped,
> working day, open time, close time, `order_cutoff_time`, holiday flag, reason) in v1.1, with a
> `CalendarService.addWorkingDuration(from, duration, calendar)` used by both the promise engine and
> the SLA measurement so a promise and a breach are computed by the same code.

---

### `F-033` · Holds are records with a release audit, not a status
**MAJOR · schema · `warehouse` · v1 · Products: Extensiv `●`, Deposco `●`, Peoplevox `●`, Fulfil `●`, Unicommerce `●`**

**Why not a status.** An order can be on two holds at once (fraud review *and* out of stock), and
`status = ON_HOLD` cannot represent that; releasing one hold then wrongly releases the order.

**Paste-ready requirement.**
> **FR-W033** · `wh_order_holds` — (id, order_id, `hold_type` FK `wh_hold_types` seeded
> {`FRAUD_REVIEW`,`CREDIT`,`ADDRESS_INVALID`,`STOCK`,`CLIENT_REQUEST`,`COMPLIANCE`,`PAYMENT_PENDING`,
> `PRICE_MISMATCH`,`DUPLICATE_SUSPECTED`}, reason, `placed_by`, `placed_at`, `released_by`,
> `released_at`, release_note). An order is releasable to picking only when it has zero open holds;
> the check is a query, not a status. Each hold type carries `blocks_allocation` and `blocks_pick`
> flags because an address hold should not stop allocation.

---

### `F-034` · Order edit after release, with de-allocation semantics that are written down
**MAJOR · feature · `warehouse` · v1.1 · Products: Deposco `●`, Extensiv `●`, Peoplevox `●`, Fulfil `●`, Unicommerce `●`; ShipHero `◐`**

**What it is, and why every WMS gets asked for it.** The customer changes the address, adds a line,
cancels a line, or the client changes the carrier — after allocation, after the pick list printed,
sometimes after packing. Every product in the set has an answer; the ones that handle it well do so
by defining, per order state, which edits are allowed and what compensating action each triggers.

**Paste-ready requirement.**
> **FR-W034** · A matrix, seeded as data in `wh_order_edit_rules` — (from_status, `edit_type` ∈
> {`ADD_LINE`,`REMOVE_LINE`,`CHANGE_QTY`,`CHANGE_ADDRESS`,`CHANGE_CARRIER`,`CHANGE_PRIORITY`,
> `CANCEL_ORDER`}, `allowed`, `requires_permission`, `compensating_action` ∈
> {`NONE`,`RELEASE_RESERVATION`,`CANCEL_PICK_TASK`,`REPRINT_PICKLIST`,`VOID_LABEL`,`UNPACK`,
> `REVERSE_MOVEMENTS`}) — and an append-only `wh_order_amendments` (order, edit_type, before/after
> summary, actor, timestamp, compensating movements posted). After `SHIPPED` there is no edit; the
> answer is a return or an RTO (`F-046`, `F-054`), and the rule table says so rather than the UI
> silently disabling a button.

---

### `F-035` · Channel inventory publish rules, or you will oversell
**MINOR · schema · `warehouse` · v2 · Products: Unicommerce `●`, EasyEcom `●`, Vinculum `●`, Deposco `●`, Veeqo `●`, Fulfil `●`**

**Paste-ready requirement.**
> **FR-W035** · `wh_channel_inventory_rules` — (channel_account, owner, item nullable, item_group
> nullable, `basis` ∈ {`AVAILABLE`,`ON_HAND`,`AVAILABLE_MINUS_BUFFER`,`FIXED`,`PERCENT_OF_AVAILABLE`},
> `buffer_quantity`, `percent`, `max_publish_quantity`, `min_publish_threshold` — below which publish
> zero rather than one — `include_stock_statuses`, `include_warehouses`, `publish_frequency_minutes`).
> `wh_channel_inventory_publish_log` records what was pushed and what the channel acknowledged, since
> "the marketplace shows 3 and we have 0" is otherwise unarguable.

---

## 2.4 Shipping and carriers

### `F-036` · The carrier account can belong to the 3PL or to the client
**MAJOR · schema · `warehouse` · v1 · Products: all 3PL `●`, ShipStation `●`, ShipHero `●`**

**Paste-ready requirement.**
> **FR-W036** · `wh_carriers` (code, name, country, `is_parcel`/`is_ltl`/`is_ftl`, `adapter_code`),
> `wh_carrier_services` (carrier, service code, name, `transit_days_min/max`, `supports_cod`,
> `supports_reverse`, `dim_divisor`, `dim_uom`, `max_weight`, `max_dimensions`),
> `wh_carrier_accounts` (id, carrier, `owner_id` **nullable — null means the house account**,
> account number, credential ref, `is_default`, `pickup_location_code`, `billing_mode`, is_active).
> Rate shopping, label generation and manifesting all resolve the account from (owner → carrier), and
> the pass-through billing mode (`F-024`) reads `owner_id` from it. This nullable column is the whole
> of the "ship on the client's account" feature and it costs nothing in v1.

---

### `F-037` · Rate shopping with the quote persisted
**MAJOR · feature · `warehouse` · v2 · Products: ShipStation/ShipEngine `●`, ShipHero `●`, Logiwa `●`, Mintsoft `●`, ShipBob `●`, Shiprocket `●`, WareIQ `●`**

**Paste-ready requirement.**
> **FR-W037** · `wh_rate_quotes` — (id, shipment_id or a pre-shipment key, carrier, service,
> carrier_account, `quoted_amount`, `currency`, `estimated_transit_days`, `estimated_delivery_at`,
> `billable_weight`, `is_selected`, `selection_reason`, `quoted_at`, `raw_response_ref`) — persisted
> because the selection has to be explainable three months later when the carrier invoice disagrees
> (`F-047`). `wh_rate_shop_rules` — (owner nullable, channel nullable, destination scope, `objective`
> ∈ {`CHEAPEST`,`FASTEST`,`CHEAPEST_MEETING_PROMISE`,`PREFERRED_CARRIER`,`CLIENT_SPECIFIED`},
> allowed/blocked carrier list, `max_amount`, priority) — bounded rows, no expression language.

---

### `F-038` · Cartonisation and dimensional weight
**MAJOR · schema+feature · `warehouse` · v1 (masters + columns) / v2 (algorithm) · Products: ShipHero `●`, Logiwa `●`, ShipBob `●`, Deposco `●`, Made4net `●`**

**Paste-ready requirement.**
> **FR-W038** · `wh_packaging_types` — (code, name, inner/outer L·W·H, dim_uom, tare_weight,
> max_content_weight, `item_id` nullable — packaging that is itself stock, so it decrements and is
> billable (`F-060`) — cost, is_active, `owner_id` nullable for client-supplied packaging).
> `whb_items` carries `length`, `width`, `height`, `dim_uom`, `gross_weight`, `net_weight`,
> `weight_uom`, `is_stackable`, `hazmat_class` — **v1 columns**, because cartonisation, dim weight,
> cubic storage billing (`F-015`) and vehicle loading in the future logistics module (§4) all read
> them and none of them can be backfilled from a photograph. Billable weight = `MAX(actual,
> ceil(L×W×H ÷ dim_divisor))` per carrier service (`F-036`), stored on the carton.

---

### `F-039` · Labels are stored artefacts with a void path
**MAJOR · schema · `warehouse` · v1.1 · Products: all `●`**

**Paste-ready requirement.**
> **FR-W039** · `wh_shipment_labels` — (id, shipment_id, carton_id nullable, `label_type` ∈
> {`SHIPPING`,`RETURN`,`CUSTOMS`,`PACKING_LIST`,`COD`}, carrier, `tracking_number`, `format` ∈
> {`PDF`,`ZPL`,`EPL`,`PNG`}, `document_id` FK to the platform `documents` table, `generated_at`,
> `voided_at`, `void_reason`, `carrier_void_ref`). A label is voided, never deleted — an Indian
> carrier bills for a generated-and-unused AWB in some contracts, and the void call is what stops it.

---

### `F-040` · Manifest, handover and pickup are three things, and India needs all three
**MAJOR · schema · `warehouse` · v1.1 · Products: ShipStation `●` (SCAN form), Mintsoft `●`, Shiprocket `●`, WareIQ `●`, Indian carrier APIs `●`**

**The distinction that gets collapsed and should not be.**

| Object | What it is | Who needs it |
|---|---|---|
| **Manifest** | the carrier's list of AWBs handed over, printed and signed | every Indian carrier; USPS SCAN form; DHL/FedEx close-out |
| **Handover** | *our* record that N shipments physically left, who took them, at what time, against which signature | 3PL client SLA evidence; the seam to a future logistics module (§4) |
| **Pickup request** | a scheduled request to the carrier to send a vehicle, with a window and a package count | Indian carriers require it explicitly; US parcel is mostly implicit |

**Paste-ready requirement.**
> **FR-W040** · `wh_manifests` — (id, warehouse, carrier, carrier_account, `manifest_date`,
> `manifest_number`, `carrier_manifest_ref`, `shipment_count`, `total_weight`, `closed_at`,
> `closed_by`, document ref, status). `wh_manifest_shipments` (manifest, shipment). `wh_handovers` —
> (id, manifest nullable, `handed_to_name`, `handed_to_id_ref`, vehicle_number, `handed_at`,
> `handed_by_user_id`, signature/photo document ref, shipment_count) — **this is the row the future
> logistics module reads to take custody** (§4). `wh_pickup_requests` — (id, warehouse, carrier,
> `requested_for_date`, window_from, window_to, `expected_package_count`, `carrier_pickup_ref`,
> status, cancelled_at). Keeping the three separate is what lets a logistics module take over the
> transport leg without touching the warehouse's carrier manifest.

---

### `F-041` · Address validation, and India's pincode serviceability is a different question
**MINOR · schema · `warehouse` + adapter · v2 (validation) / v1.1 (serviceability) · Products: ShipStation `●`, ShipBob `●`, Shiprocket `●`, WareIQ `●`, Indian carriers `●`**

**The difference.** Address *validation* asks "is this a real, deliverable address" and matters most in
the US/EU. **Serviceability** asks "will *this carrier* deliver here, will it accept COD here, will it
collect a return here, and is it an ODA (out of delivery area) location with a surcharge" — and in
India it is checked **before** rate shopping, because half the carriers do not serve half the pincodes.

**Paste-ready requirement.**
> **FR-W041** · `wh_addresses` — (…, `validation_status` ∈ {`UNVALIDATED`,`VALID`,`CORRECTED`,
> `INVALID`,`AMBIGUOUS`}, `validated_at`, `normalised_line1/2`, `normalised_city`, `normalised_state`,
> `normalised_postal_code`, `latitude`, `longitude`, `address_type` ∈ {`RESIDENTIAL`,`COMMERCIAL`,
> `PO_BOX`,`UNKNOWN`} — residential surcharges depend on it).
> `wh_carrier_serviceability` — (carrier, service, `postal_code`, `country_code`, `supports_prepaid`,
> `supports_cod`, `supports_pickup`, `supports_reverse`, `is_oda`, `oda_surcharge`,
> `expected_transit_days`, `refreshed_at`) refreshed from the carrier adapter. Serviceability gates
> the rate shop; validation only warns.

---

### `F-042` · India: you cannot generate a label without an AWB pool
**BLOCKER · schema · `warehouse-adapter-<carrier>` · v1.1 · Products: Shiprocket `●`, WareIQ `●`, Delhivery/Ecom Express/XpressBees `●`; no global product `○`**

**What it is.** Indian carriers do not mint a tracking number as a side effect of a label call the way
FedEx or UPS do. They issue **waybill numbers in blocks**, fetched ahead of time and held by the
shipper (Delhivery's waybill fetch, Ecom Express's AWB allocation, and every aggregator on top of
them). The label is then created *against* a number you already hold. A design that assumes
"call the carrier, get a label, get a tracking number back" simply does not work here, and discovering
that during the integration sprint means redesigning the pack station.

**Second-order consequences that also need modelling.** A held AWB is a consumable resource: it can be
exhausted (packing stops), it can expire, it is carrier- and account- and sometimes
service-and-payment-mode-specific (a COD AWB block is not a prepaid AWB block), and an unused AWB may
be billable or may need explicit cancellation.

**Paste-ready requirement.**
> **FR-W042** · `wh_awb_pool` — (id, carrier, `carrier_account_id`, service_code nullable,
> `payment_mode` ∈ {`PREPAID`,`COD`,`ANY`}, `awb_number` uk per carrier, `fetched_at`,
> `expires_at` nullable, `status` ∈ {`AVAILABLE`,`ASSIGNED`,`USED`,`CANCELLED`,`EXPIRED`},
> `assigned_at`, `shipment_id` nullable, `cancelled_at`, `cancel_reason`).
> `wh_awb_pool_fetch_runs` — (carrier, account, requested_count, received_count, run_at, error).
> A **low-watermark alert** per (carrier, account, payment mode) with a background top-up job, because
> running out of AWBs stops dispatch entirely. Assignment is a transactional
> `SELECT … FOR UPDATE SKIP LOCKED` claim so two pack stations never take the same number.

---

### `F-043` · Tracking events, stored normalised **and** raw
**MAJOR · schema · `warehouse` · v1.1 · Products: all `●`**

**Paste-ready requirement.**
> **FR-W043** · `wh_shipment_tracking_events` — (id, shipment_id, `awb_number`, carrier,
> `carrier_event_code`, `carrier_event_text`, `mapped_status_code` FK `wh_tracking_statuses`,
> `event_at` — the carrier's timestamp, with `event_timezone` — `received_at`, location text,
> `location_pincode`, `remarks`, `raw_payload_ref`, `source` ∈ {`WEBHOOK`,`POLL`,`MANUAL`},
> `idempotency_key` uk(carrier, awb, carrier_event_code, event_at)).
> `wh_tracking_statuses` seeded: `MANIFESTED`, `PICKED_UP`, `IN_TRANSIT`, `REACHED_HUB`,
> `OUT_FOR_DELIVERY`, `DELIVERED`, `UNDELIVERED_ATTEMPT`, `NDR_RAISED`, `RTO_INITIATED`,
> `RTO_IN_TRANSIT`, `RTO_DELIVERED`, `LOST`, `DAMAGED`, `CANCELLED`, `EXCEPTION`.
> `wh_carrier_status_mappings` — (carrier, carrier_event_code, mapped_status_code) as **data**, seeded
> per carrier, because every carrier's vocabulary is different and a Java `switch` per carrier is how
> this becomes unmaintainable at carrier number six. Keeping the raw code is what lets a mapping be
> corrected and the history re-derived.

---

### `F-044` · India: NDR is a workflow with a response clock, not an exception code
**BLOCKER · schema+feature · `warehouse` + adapter · v1.1 · Products: Shiprocket `●`, WareIQ `●`, Unicommerce `●`, EasyEcom `●`, Indian carriers `●`; no global product `○`**

**What it is.** When an Indian courier fails a delivery attempt it raises an **NDR** with a reason —
customer not available, customer refused, address incomplete, customer asked for a later date, COD
amount not ready, phone unreachable, out of station, office closed. The shipper then has a **short
window** (commonly 24–48 hours, contractual) to respond with an action: reattempt, reattempt on a
given date, change the delivery address or phone, or authorise RTO. No response, and the shipment
auto-RTOs — which costs the client the freight both ways plus the stock being out for a week.

Managing this queue is a full-time job at any Indian fulfilment operation, and it is the thing WareIQ
and Shiprocket market hardest after rates. It also has a **stock consequence** the global products
never model: an NDR is the leading indicator that a unit is coming back and will need a receiving
slot, an inspection and a put-back (`F-046`).

**Paste-ready requirement.**
> **FR-W044** · `wh_shipment_ndrs` — (id, shipment_id, awb, `attempt_number`, `ndr_raised_at`,
> `ndr_reason_code` FK `wh_ndr_reasons`, `carrier_reason_text`, `response_due_at` — computed from a
> per-carrier SLA — `action_taken` ∈ {`REATTEMPT`,`REATTEMPT_ON_DATE`,`CHANGE_ADDRESS`,`CHANGE_PHONE`,
> `RTO`,`HOLD_AT_HUB`,`NO_ACTION`}, `action_taken_at`, `action_taken_by`, `action_payload_*` typed
> columns (new date / new address ref / new phone), `carrier_ack_ref`, `outcome` ∈
> {`DELIVERED`,`RTO`,`PENDING`,`EXPIRED_AUTO_RTO`}, `customer_contacted_at`, `contact_channel`,
> `contact_note`).
> An **NDR queue screen** sorted by `response_due_at` with bulk actions, a breach counter, and
> per-client visibility in the portal. `wh_ndr_reasons` is seeded and carries `default_action` and
> `is_customer_fault` — the latter because who pays for the reattempt is a contractual question and a
> billing input (`F-018`).

---

### `F-045` · India: COD remittance reconciliation
**BLOCKER · schema+feature · `warehouse` + accounting port · v1.1 · Products: Shiprocket `●`, WareIQ `●`, Unicommerce `●`, EasyEcom `●`; global `○`**

**What it is.** In a COD shipment the courier collects cash from the consumer and remits it, in
batches, days or weeks later, minus its charges, against a bank UTR. Reconciling "which shipments does
this ₹4,82,317 remittance cover" is a daily finance job for every Indian seller and 3PL, and the
missing money — collected but never remitted, or remitted short — is real and material.

**Why it belongs in the warehouse product and not only in accounting.** The join key is the **AWB**,
which accounting has never heard of. The warehouse holds the shipment, the AWB, the COD amount and the
delivery event; accounting holds the bank receipt. The match must happen where the AWB lives, and the
result — a matched receipt with a party and an amount — is what crosses to accounting.

**Paste-ready requirement.**
> **FR-W045** · `wh_shipments.cod_amount`, `cod_currency`, `cod_collected_at`,
> `cod_remittance_line_id` nullable — **v1 columns**.
> `wh_cod_remittances` — (id, carrier, carrier_account, `remittance_ref`, `remitted_at`, `utr_number`,
> `gross_amount`, `deduction_amount`, `net_amount`, `currency`, `bank_account_ref`, `imported_at`,
> `imported_by`, `source_file_document_id`, status).
> `wh_cod_remittance_lines` — (remittance, awb, shipment_id nullable until matched, `cod_amount`,
> `deduction_amount`, `net_amount`, `match_status` ∈ {`MATCHED`,`UNMATCHED_AWB`,`AMOUNT_MISMATCH`,
> `DUPLICATE`}, `variance_amount`, `resolution_note`).
> An **ageing report** of COD delivered-but-not-remitted by carrier, which is the screen that recovers
> the money. The matched net amount emits a receipt envelope to the accounting port (`F-021`'s
> pattern); the deduction emits an expense line; **warehouse posts no journal itself.**

---

### `F-046` · India: RTO is an inbound stock stream, and it is the biggest single reverse flow
**BLOCKER · schema+feature · `warehouse` · v1.1 · Products: Shiprocket `●`, WareIQ `●`, Unicommerce `●`, EasyEcom `●`, Increff `●`; global `◐`/`○`**

**What it is.** A shipment that could not be delivered comes back. For COD fashion and electronics in
India the RTO rate commonly runs **15–30%** of dispatched orders — an order of magnitude above US
parcel undeliverable rates, which is why no global product models it as a first-class stream.

**What makes it different from a customer return.** There is **no RMA and no customer interaction**.
The goods simply arrive at the dock, in a carrier's bulk RTO consignment, identified only by the AWB
on the shipping label. Frequently the outer packaging is intact and the unit is directly sellable;
frequently it is not, and frequently what comes back is not what went out. The operational sequence is:
receive the RTO consignment → scan AWBs → match to the original shipment → open and verify contents
against the original shipment lines → grade → put back to sellable, to unsellable, or to a claim.

**Paste-ready requirement.**
> **FR-W046** · `wh_shipments.rto_initiated_at`, `rto_reason_code`, `rto_awb_number` — the return leg
> often has its **own** AWB — `rto_received_at`, `rto_status` ∈ {`NONE`,`INITIATED`,`IN_TRANSIT`,
> `RECEIVED`,`SHORT`,`LOST`,`DISPUTED`}. **v1 columns.**
> `wh_rto_consignments` — (id, warehouse, carrier, received_at, `expected_awb_count`,
> `scanned_awb_count`, received_by, document refs for the carrier's RTO manifest).
> `wh_rto_receipt_lines` — (consignment, awb, shipment_id nullable, `scan_at`, `match_status`,
> `opened_at`, `verified_by`, item, quantity_expected, quantity_received, `condition_grade`,
> `disposition_code`, `variance_reason`, photo document refs).
> The receipt posts a `RTO_RECEIPT` movement per line (`F-054`'s return type), which restocks to
> `AVAILABLE` or to a `DAMAGED`/`QUARANTINE` status. An **RTO-in-transit ageing report** (initiated
> more than N days ago, not received) is the screen that finds carrier-lost stock, and a lost RTO
> becomes a claim, not a silent shrinkage adjustment.

---

### `F-047` · India: carrier weight/dimension discrepancy disputes
**MAJOR · schema+feature · `warehouse` · v2 · Products: Shiprocket `●`, WareIQ `●`, Unicommerce `◐`; global `○` (Amazon FBA `◐` for its own measurements)**

**What it is.** The carrier re-weighs and re-measures at its hub and bills the higher of declared and
measured. Overcharges are routine, disputes are time-limited (commonly 7–15 days from the charge),
and the evidence is a photograph of the packed carton on a weighing scale with the AWB visible —
which means the **pack station has to capture it at pack time**, before the dispute exists.

**Paste-ready requirement.**
> **FR-W047** · `wh_shipment_weight_disputes` — (id, shipment, awb, `declared_weight`,
> `declared_dimensions`, `carrier_measured_weight`, `carrier_measured_dimensions`,
> `charge_difference`, `raised_at`, `dispute_due_at`, `evidence_document_ids`, `status` ∈
> {`OPEN`,`SUBMITTED`,`ACCEPTED`,`REJECTED`,`PARTIALLY_ACCEPTED`,`LAPSED`}, `carrier_ref`,
> `recovered_amount`). `wh_shipment_cartons` gains `pack_photo_document_id` and
> `scale_weight_captured_at` in **v1**, because the evidence cannot be created retroactively.
> The same table reconciles the carrier invoice against `wh_rate_quotes` (`F-024`, `F-037`).

---

### `F-048` · International documentation
**MINOR · schema · `warehouse` + adapter · v3 · Products: ShipStation `●`, ShipBob `●`, Flexport `●`, Shipwire `●`, Blue Dart `●`**

**Paste-ready requirement.**
> **FR-W048** · `whb_items.hs_code`, `country_of_origin` — and the same two on `whb_lots`, because
> origin is a lot property and a customs officer asks about the lot (`F-063`). **v1 columns.**
> `wh_customs_declarations` — (shipment, `incoterm`, `declared_value`, currency, `reason_for_export`,
> `exporter_ref`, `importer_of_record`, `eori_vat_refs`, document refs) and
> `wh_customs_declaration_lines` (item, hs_code, origin, quantity, unit_value, net/gross weight) in v3.

---

### `F-049` · Branded tracking and consumer notifications
**MINOR · feature · `warehouse` · v2 · Products: ShipStation `●`, ShipHero `●`, Shiprocket `●`, WareIQ `●`, Mintsoft `●`**

**Paste-ready requirement.**
> **FR-W049** · A signed, expiring public tracking link per shipment (the same shape as the
> accounting set's public party-ledger link — one mechanism, not two), plus
> `wh_notification_rules` — (owner, `trigger_status_code`, channel ∈ {`EMAIL`,`SMS`,`WHATSAPP`},
> template ref, is_active) driving consumer messages on dispatch, out-for-delivery, NDR and delivery.
> Reuse the platform's existing WhatsApp provider rather than adding a second.

---
## 2.5 Returns and reverse logistics

### `F-050` · RMA is optional; the return receipt is not
**MAJOR · schema · `warehouse` · v1.1 · Products: all `●`**

**The design mistake to avoid.** Modelling returns as "an RMA that is later received" makes the
**blind return** — goods that arrive with no authorisation — unrepresentable, and in India (and in
marketplace returns generally) the blind return is the *majority* case. The correct shape is the
inverse: the **return receipt** is the primary object, and an RMA, where one exists, is matched to it.

**Paste-ready requirement.**
> **FR-W050** · `wh_rmas` — (id, `owner_id`, `rma_number`, `original_order_id` nullable,
> `channel_id` nullable, `external_rma_ref`, `customer_ref`, `reason_code_id`, `requested_at`,
> `approved_by`, `approved_at`, `expected_by`, `return_label_id` nullable, status) — optional.
> `wh_rma_lines` — (rma, item, quantity_expected, reason_code, expected_condition).
> `wh_return_receipts` — (id, warehouse, `owner_id`, `return_type` (`F-054`), `received_at`,
> `received_by`, carrier, `awb_number` nullable, `rma_id` nullable, `original_shipment_id` nullable,
> `match_status`, `carrier_consignment_ref`, document refs) — **mandatory, and creatable with none of
> the optional links filled in.** Matching an unmatched receipt to an RMA or a shipment later is a
> screen, not a re-receipt.

---

### `F-051` · Inspection and grading, with photographs, at the point of receipt
**MAJOR · schema+feature · `warehouse` · v1.1 · Products: Extensiv `●`, Logiwa `●`, Peoplevox `●`, ShipBob `●`, Unicommerce `●`, EasyEcom `●`, Increff `●`**

**Paste-ready requirement.**
> **FR-W051** · `wh_return_inspections` — (id, `return_receipt_line_id`, `inspected_by`,
> `inspected_at`, `condition_grade` FK `wh_condition_grades` — seeded `A_SELLABLE`, `B_MINOR`,
> `C_DAMAGED`, `D_SCRAP`, `WRONG_ITEM`, `MISSING`, `COUNTERFEIT_SUSPECTED` — `condition_notes`,
> `photo_document_ids`, `disposition_code` (`F-052`), `serial_verified`, `lot_verified`,
> `weight_check_passed`, `packaging_intact`). Per-client inspection **checklists**
> (`wh_inspection_checklists` / `_items`) are v2, because different clients demand different checks
> and a hard-coded checklist is unsellable.

---

### `F-052` · Disposition is a vocabulary, and each value posts a different movement
**MAJOR · schema · `warehouse-base` (vocabulary) + `warehouse` (screen) · v1.1 · Products: Extensiv `●`, Logiwa `●`, Peoplevox `●`, ShipBob `●`, Amazon FBA `●`, Unicommerce `●`**

**Paste-ready requirement.**
> **FR-W052** · `whb_dispositions` — seeded (code, name, `target_stock_status_code`,
> `target_location_type`, `posts_movement_type`, `requires_approval`, `is_value_destroying`,
> `notifies_channel`, `billable_charge_code` nullable):

| Code | Target status | Movement posted |
|---|---|---|
| `RESTOCK_SELLABLE` | `AVAILABLE` | `RETURN_RECEIPT` into a pick face or reserve |
| `RESTOCK_UNSELLABLE` | `DAMAGED` | `RETURN_RECEIPT` into the damaged area |
| `REFURBISH` | `PENDING_WORK` | `RETURN_RECEIPT` + a `REFURBISH` work order (`F-058`) |
| `REPACK` | `PENDING_WORK` | `RETURN_RECEIPT` + a `REPACK` work order |
| `SCRAP` | — | `RETURN_RECEIPT` then `SCRAP`, `is_value_destroying = true`, approval required |
| `RETURN_TO_VENDOR` | `HOLD` | `RETURN_RECEIPT` then an outbound RTV shipment (`F-056`) |
| `RETURN_TO_CLIENT` | `HOLD` | `RETURN_RECEIPT` then an outbound transfer to the client |
| `HOLD_FOR_CLIENT_DECISION` | `HOLD` | `RETURN_RECEIPT` only |
| `DONATE` | — | `RETURN_RECEIPT` then `SCRAP` with a donation reason |
| `QUARANTINE_INVESTIGATE` | `QUARANTINE` | `RETURN_RECEIPT` |

> A disposition never silently discards stock: `SCRAP` and `DONATE` post an explicit
> value-destroying movement with a reason code and an approver, because unexplained shrinkage in a
> 3PL is a claim against the 3PL.

---

### `F-053` · The warehouse emits the disposition; it never decides a refund
**MAJOR · seam · `warehouse` → channel / accounting · v1.1 · Products: all `●`**

**Paste-ready requirement.**
> **FR-W053** · On inspection completion, `warehouse` emits `return.line.dispositioned` on the outbox
> with owner, original order/shipment, item, quantity, condition grade, disposition and the inspection
> photograph references. Channel adapters translate it to the marketplace's returns API; the
> accounting adapter translates a `RESTOCK_*` into a stock movement envelope and — where the client
> wants it — a credit-note *proposal*. **There is no refund screen, no refund amount and no payment
> path in any warehouse module, in any version.** The reason is the same as `F-021`'s: a refund is a
> receivable event with tax consequences and it belongs where the receivable lives.

---

### `F-054` · `return_type` is a day-one column because the disposition rules branch on it
**MAJOR · schema · `warehouse-base` · v1 · Products: Unicommerce `●`, EasyEcom `●`, WareIQ `●`; global `◐`**

**Paste-ready requirement.**
> **FR-W054** · `whb_return_types` seeded: `CUSTOMER_RETURN`, `RTO`, `REFUSED_DELIVERY`,
> `CANCELLED_IN_TRANSIT`, `VENDOR_RETURN`, `RECALL`, `CLIENT_WITHDRAWAL`, `MARKETPLACE_RETURN`,
> `WARRANTY`, `EXCHANGE`. Carried on `wh_return_receipts` and on the `RETURN_RECEIPT` movement line.
> It matters because the downstream differs entirely: an `RTO` has no customer to refund and no RMA;
> a `MARKETPLACE_RETURN` has a claim window (`F-055`); a `RECALL` must not be restocked under any
> disposition; a `CLIENT_WITHDRAWAL` is an outbound, not a return, and is billed differently.

---

### `F-055` · India: the marketplace return-claim window
**MINOR · feature · `warehouse-adapter-<channel>` · v2 · Products: Unicommerce `●`, EasyEcom `●`, WareIQ `●`; global `○`**

**What it is.** Indian marketplaces return goods to the seller and the seller must inspect and, if the
return is short, wrong or damaged, **raise a claim within a fixed window** (varies by marketplace,
commonly 48h–7 days from receipt) with photographic evidence, or absorb the loss. Sellers routinely
lose one to three percent of revenue here purely by missing the window.

**Paste-ready requirement.**
> **FR-W055** · `wh_marketplace_return_claims` — (id, return_receipt_line, channel, external_return_id,
> `claim_type` ∈ {`SHORT`,`WRONG_ITEM`,`DAMAGED`,`EMPTY_PACKAGE`,`USED`}, `claim_due_at`,
> `raised_at`, `evidence_document_ids`, `claim_amount`, `status`, `settled_amount`, `settled_at`).
> The due date is computed at receipt from a per-channel window, and the queue is sorted by it — the
> same pattern as `F-044`'s NDR queue, because it is the same failure mode: a clock nobody is watching.

---

### `F-056` · Return to vendor
**MINOR · feature · `warehouse` + accounting port · v2 · Products: Extensiv `●`, Unicommerce `●`, EasyEcom `●`**

**Paste-ready requirement.**
> **FR-W056** · An RTV is an outbound shipment with `shipment_purpose = RETURN_TO_VENDOR`, a vendor
> party, a reference to the originating receipt/lot, and an emitted debit-note proposal to the
> accounting port. It posts an ordinary issue movement; it is not a special ledger case.

---

## 2.6 Kitting, VAS and light manufacturing

### `F-057` · Kits are a master, and virtual and physical kits are different objects with the same BOM
**MAJOR · schema · `warehouse-base` · v1.1 · Products: all `●`**

**Paste-ready requirement.**
> **FR-W057** · `whb_kits` — (id, `owner_id`, `kit_item_id`, `kit_type` ∈ {`VIRTUAL`,`PHYSICAL`},
> `version_no`, effective_from/to, `assembly_time_minutes`, is_active) and `whb_kit_components` —
> (kit, component_item_id, quantity, uom, `is_optional`, `substitute_group` nullable,
> `scrap_percent`). **Virtual**: no stock of the kit item ever exists; availability is
> `MIN(component available ÷ required)` and allocation reserves the components. **Physical**: the kit
> item holds stock and a work order (`F-058`) converts components into it. The distinction is a column
> and the availability engine branches on it — a design that supports only one of the two is rebuilt
> when the second client arrives.

---

### `F-058` · The work order is the VAS record and the light-manufacturing record
**MAJOR · schema · `warehouse` · v1.1 · Products: Extensiv `●`, Logiwa `●`, Infoplus `●`, Deposco `●`, Made4net `●`, Da Vinci `●`, Fulfil `●`**

**Paste-ready requirement.**
> **FR-W058** · `wh_work_orders` — (id, `owner_id`, warehouse, `work_order_number`, `wo_type` FK
> `wh_work_order_types` seeded {`ASSEMBLE`,`DISASSEMBLE`,`REPACK`,`RELABEL`,`QC_INSPECT`,`REFURBISH`,
> `POLYBAG`,`GIFT_WRAP`,`STICKER`,`CUSTOM`}, `kit_id` nullable, `output_item_id` nullable,
> `quantity_planned`, `quantity_produced`, `quantity_scrapped`, `scrap_reason_code`, status,
> `planned_start`, `actual_start`, `actual_end`, `assigned_to`, `client_instruction_document_id`,
> `billing_charge_code_id` nullable).
> `wh_work_order_components` — (wo, item, lot, serial, lpn, `quantity_planned`,
> `quantity_consumed`, `is_consumable`). Completion posts **one balanced movement** (`F-059`).
> `client_instruction_document_id` exists because VAS instructions arrive as a PDF from the client
> and the operator on the floor needs to see exactly the version that was priced.

---

### `F-059` · A single movement may carry lines of two different owners, and it must balance per (owner, item), not per movement
**BLOCKER · schema · `warehouse-base` · v1 · Products: none model it explicitly; Extensiv/Camelot/Made4net approximate it `◐`**

**The scenario, which is completely ordinary.** A 3PL packs a client's order. The carton, the void fill
and the branded tape are the **3PL's own** stock (`HOUSE` owner), consumed at that moment. The units
inside are the **client's** stock. It is one physical event, one atomic transaction, and it decrements
two owners' balances.

**Why it forces a decision now.** Two plausible port designs, and only one survives:

| Design | What it does to this scenario |
|---|---|
| **A movement has one `owner_id` on the header, lines inherit it** | the consumable cannot be on the same movement. It becomes a second, separate movement, correlated by nothing, posted by a second call that can fail independently. The atomicity is lost and the consumable silently vanishes when the second call errors |
| **`owner_id` is per line; the movement balances per (owner, item, lot)** | one call, one transaction, one lineage, correct |

The same argument applies to `OWNER_CHANGE` (`F-009`), to a client-to-client transfer during an
acquisition, and to a 3PL absorbing a shrinkage loss on a client's stock (client's stock out, 3PL's
loss account in).

**Paste-ready requirement.**
> **FR-W059** · `owner_id` is on `whb_movement_lines`, **not** on `whb_movements`.
> `whb_movement_types` carries `allows_mixed_owner` (default false — the port rejects a mixed-owner
> movement unless the type permits it, so a bug cannot quietly move stock between owners) and
> `balance_rule` ∈ {`MUST_BALANCE_PER_OWNER_ITEM`, `MUST_BALANCE_PER_ITEM`, `UNBALANCED_ALLOWED`}.
> A receipt is `UNBALANCED_ALLOWED` (stock enters from outside), a transfer is
> `MUST_BALANCE_PER_OWNER_ITEM`, an assembly is `MUST_BALANCE_PER_ITEM` **by value not quantity**
> (components in, kit out) and therefore carries `value_balance_required = true` with a
> `variance_reason_code` when it does not.

---

### `F-060` · Packaging and consumables are stock, and stock that is billable
**MINOR · schema · `warehouse` + `warehouse-3pl` · v1.1 · Products: Extensiv `●`, Infoplus `●`, Made4net `●`, Da Vinci `●`**

**Paste-ready requirement.**
> **FR-W060** · A consumable is an ordinary `whb_items` row with `is_consumable = true` and
> `default_owner_id` = the house owner. Packing consumes it via a movement line on the same movement
> as the pack (`F-059`) and meters a billable event on the client's charge code. Client-supplied
> packaging is the same item under the client's owner — which is the whole reason the packaging master
> (`F-038`) carries a nullable `owner_id`.

---

### `F-061` · India: job work — material out, material back, on a statutory clock
**MINOR · seam · `warehouse-adapter-india` + accounting port · v2 · Products: Increff `◐`, Unicommerce `◐`; global `○`**

**What it is.** Goods sent to a processor without a sale: a delivery challan under Rule 55, ITC-04
reporting `?` (the form and its periodicity have changed more than once — **verify before build**),
and a return clock — broadly one year for inputs and three for capital goods `?` — after which the
material is deemed supplied and tax falls due. It matters for us because a 3PL doing VAS off-site and
a manufacturer sending components out are the same shape, and because the deemed-supply date is a
liability nobody notices until an assessment.

**Paste-ready requirement.**
> **FR-W061** · `wh_job_work_challans` — (id, owner, job_worker_party_id, challan_number, challan_date,
> `challan_type` ∈ {`INPUTS`,`CAPITAL_GOODS`}, e-way bill fields (`F-025`), `due_return_date`
> computed from the type, status, `returned_quantity`, `deemed_supply_at` nullable) with lines. The
> out-movement is an ordinary transfer to a `JOB_WORK` owner or to a supplier-type location; the
> compliance clock and the ITC-04 extract are adapter concerns.

---

### `F-062` · Label and document printing at the workstation
**MINOR · feature · `warehouse` · v1.1 · Products: all `●`**

**Paste-ready requirement.**
> **FR-W062** · `wh_print_templates` — (code, `document_type` ∈ {`ITEM_LABEL`,`LPN_LABEL`,
> `LOCATION_LABEL`,`SHIPPING_LABEL`,`PACKING_LIST`,`GS1_128`,`PICK_LIST`,`PUTAWAY_LIST`},
> `owner_id` nullable — clients demand their own label layouts — `format` ∈ {`ZPL`,`PDF`,`EPL`},
> template body, `label_width`, `label_height`, is_default) and `wh_printers` — (warehouse, zone,
> name, `connection_type`, address, `default_template_id`). Client-specific label layouts are a real
> 3PL requirement and the `owner_id` on the template is the whole of it.

---

## 2.7 Traceability and compliance

### `F-063` · `lot_id`, `serial_id` and the lot's own attributes are day-one ledger columns
**BLOCKER · schema · `warehouse-base` · v1 · Products: all `●`**

**Why this is a BLOCKER even though v1 may not sell to pharma.** A recall question is retrospective:
"which customers received lot `X`". It is answered by joining shipment lines to movement lines to
lots. A ledger that recorded quantity but not lot **can never answer it about the past**, and the
first customer who needs it needs it about the past. The same is true of expiry (FEFO cannot be
applied to stock that arrived without a recorded expiry), of serial warranty lookups, and of country
of origin at a customs inspection.

The cost of the column in v1 is: two nullable UUIDs on a table, two nullable UUIDs in a unique key,
and a `tracking_policy` on the item that decides whether the port demands them. That is a day's work.
The cost in v2 is a data migration that cannot be performed correctly.

**Paste-ready requirement.**
> **FR-W063** · `whb_lots` — (id, `owner_id`, `item_id`, `lot_code`, `supplier_lot_code`,
> `manufactured_date`, `expiry_date`, `best_before_date`, `country_of_origin`, `hs_code`,
> `received_date`, `mrp` — India: printed maximum retail price, which is a lot property and a legal
> one — `attributes` via a typed side table, audit), uk(`owner_id`,`item_id`,`lot_code`).
> `whb_serials` — (id, `owner_id`, `item_id`, `serial_number`, `lot_id` nullable, `current_status`,
> `current_location_id`, `current_lpn_id`, `first_received_at`, `last_movement_id`),
> uk(`owner_id`,`item_id`,`serial_number`).
> `whb_movement_lines.lot_id` / `.serial_id` — nullable, indexed, **v1**.
> `whb_items.tracking_policy` ∈ {`NONE`,`LOT`,`SERIAL`,`LOT_AND_SERIAL`} and
> `expiry_policy` ∈ {`NONE`,`OPTIONAL`,`REQUIRED`} drive the port's validation
> (`LOT_REQUIRED` / `SERIAL_REQUIRED` errors, `F-081`). Piece-level serialisation (the Increff model)
> is `tracking_policy = SERIAL` applied to everything — a policy over the same column, not a
> different design.

---

### `F-064` · The LPN is a ledger object, and moving a pallet is one movement
**BLOCKER · schema · `warehouse-base` · v1 · Products: Made4net `●`, Deposco `●`, Da Vinci `●`, Extensiv `●`, Logiwa `●`, Infoplus `●`, Amazon `●`**

**What it is.** A licence plate — an SSCC-numbered pallet, a case, a tote, a carton — is a container
whose contents are known and which is moved, stored, counted and shipped **as one thing**. Scanning
one label moves 48 cases.

**Two independent reasons it must be in v1.**

1. **Operational.** Without an LPN, every pallet move is N line-level movements that a picker must
   confirm individually, and bulk/reserve storage is unusable. Retrofitting means re-labelling a
   physical warehouse.
2. **Commercial.** Per-pallet storage billing and the **anniversary** storage method (`F-015`) are
   defined over pallets. A ledger that does not know which pallet a unit is on cannot compute either,
   and cannot compute them for the past. This is the concrete mechanism by which `warehouse-3pl`'s
   revenue model depends on a `warehouse-base` v1 column.

**Paste-ready requirement.**
> **FR-W064** · `whb_lpns` — (id, `lpn_code` uk — SSCC where issued (`F-070`) — `owner_id`,
> `lpn_type` ∈ {`PALLET`,`CASE`,`TOTE`,`CARTON`,`CONTAINER`,`RACK`}, `parent_lpn_id` nullable,
> `current_location_id`, `current_warehouse_id`, `status` ∈ {`OPEN`,`CLOSED`,`SHIPPED`,`CONSUMED`,
> `EMPTY`}, `received_at` — **the anniversary anchor** — `gross_weight`, `dimensions`,
> `packaging_type_id`, `is_mixed_item`, `is_mixed_lot`, `is_mixed_owner`, audit).
> `whb_movement_lines.lpn_id` and `from_lpn_id`/`to_lpn_id` nullable, **v1**. An LPN move is a single
> movement with `movement_type = LPN_MOVE` whose lines the service expands from the LPN's current
> contents — expanded and **stored**, never left implicit, so the ledger remains self-explaining.
> `parent_lpn_id` lands in v1 as a column; nested-LPN operations are v2.

---

### `F-065` · Genealogy
**MAJOR · schema · `warehouse-base` · v2 (table) · v1 (derivability) · Products: Da Vinci `●`, Made4net `●`, Deposco `◐`**

**Paste-ready requirement.**
> **FR-W065** · `whb_lot_genealogy` — (id, `parent_lot_id`, `child_lot_id`, `movement_id`,
> `work_order_id` nullable, `quantity`, `relationship` ∈ {`SPLIT`,`MERGE`,`TRANSFORM`,`REPACK`,
> `RELABEL`}) and `whb_serial_genealogy` for serial-into-kit. In v1 the relationship is **derivable**
> from a work-order-completion movement whose lines carry both parent and child lots — which is why
> `F-059`'s single balanced movement matters. v2 materialises it because the recursive query is not
> something an operator should wait for.

---

### `F-066` · Recall
**MAJOR · feature · `warehouse` · v2 · Products: Da Vinci `●`, Made4net `●`, Deposco `●`, Extensiv `●`, Infoplus `●`**

**Paste-ready requirement.**
> **FR-W066** · `wh_recalls` — (id, owner, `recall_reference`, item, lot range or list, reason,
> `severity`, `initiated_at`, `initiated_by`, `regulator_reference`, status) with an action that
> (a) posts a status-change movement putting all on-hand matching stock into `QUARANTINE`, (b) lists
> every shipment that carried the lot with its consignee and tracking, (c) lists every open order
> allocated to it and releases those reservations, and (d) exports the affected-customer list.
> (a)–(d) are all single queries **if and only if** `F-063` landed in v1.

---

### `F-067` · FEFO and minimum remaining shelf life on dispatch
**MAJOR · schema · `warehouse-base` · v1 (FEFO) / v1.1 (shelf-life rules) · Products: all `●`**

**What it is.** "Do not ship stock with less than 70% (or 90 days, or 6 months) of its shelf life
remaining" is a clause in every FMCG, pharma and marketplace contract — Amazon India and modern trade
both enforce it, and a shipment that breaches it is rejected at the client's DC at our cost.

**Paste-ready requirement.**
> **FR-W067** · `whb_shelf_life_rules` — (id, `owner_id`, `item_id` nullable, `item_group_id`
> nullable, `channel_id` nullable, `customer_group` nullable, `min_remaining_days` nullable,
> `min_remaining_percent` nullable, `on_breach` ∈ {`BLOCK`,`WARN`,`REQUIRE_APPROVAL`}, priority).
> Allocation excludes non-compliant lots; the port rejects a pick movement that breaches a `BLOCK`
> rule with `SHELF_LIFE_RULE_VIOLATED`. A **near-expiry report** by owner, with days-to-expiry bands,
> is v1.1 and is the report that saves a client more money than any other in the product.

---

### `F-068` · Stock status is a vocabulary, and quarantine is not a location
**BLOCKER · schema · `warehouse-base` · v1 · Products: all `●`**

**The mistake it prevents.** The cheap design puts damaged stock in a "DAMAGED" bin. Then: damaged
stock in the bulk aisle cannot be represented; a quarantined lot has to be physically moved to be
quarantined; "available in this bin" and "this is the available bin" become the same query; and a
recall (`F-066`) cannot quarantine in place. Every audited product separates the two axes.

**Paste-ready requirement.**
> **FR-W068** · `whb_stock_statuses` — seeded (code, name, `is_available_to_promise`,
> `is_on_hand`, `is_pickable`, `blocks_shipment`, `requires_approval_to_leave`, sort_order):
> `AVAILABLE`, `PENDING_QC`, `QUARANTINE`, `DAMAGED`, `EXPIRED`, `ON_HOLD`, `BLOCKED_RECALL`,
> `IN_TRANSIT`, `AWAITING_DISPOSITION`, `SCRAPPED`. `whb_movement_lines.stock_status_code` is
> `NOT NULL`; a status change is a movement of type `STATUS_CHANGE` with a from-status line and a
> to-status line in the same location; the status participates in the balance unique key (`F-001`).
> Locations separately carry `location_type` — that axis is about *where*, never about *condition*.

---

### `F-069` · Cold chain
**MINOR · schema+feature · `warehouse` · v2 · Products: Da Vinci `●`, Made4net `●`, Amazon `●`, Extensiv `◐`**

**Paste-ready requirement.**
> **FR-W069** · `whb_locations.temperature_zone_id` FK `whb_temperature_zones` (code, min_c, max_c,
> humidity range). `wh_temperature_readings` — (zone or location, sensor_ref, reading_c, humidity,
> read_at, source). `wh_cold_chain_excursions` — (zone, started_at, ended_at, min/max observed,
> duration_minutes, `affected_lot_ids`, `auto_quarantined`, disposition, investigated_by) with a rule
> that an excursion beyond a threshold posts a `STATUS_CHANGE` movement to `QUARANTINE` for the
> affected stock. Also `whb_items.storage_temperature_zone_id` so a putaway into the wrong zone is
> rejected by the port with `TEMPERATURE_ZONE_MISMATCH`.

---

### `F-070` · GS1 — GTIN, SSCC, GLN and AI parsing on the scanner
**MINOR · schema (v1) + feature (v2) · `warehouse-base` + `warehouse` · Products: Da Vinci `●`, Made4net `●`, Deposco `●`, Increff `●`, Amazon `●`**

**Why the columns are v1 and the parser is v2.** A GS1-128 label encodes GTIN + batch + expiry +
serial + count in one barcode with application identifiers (`01`, `10`, `17`, `21`, `37`, `00`,
`3202`). Parsing it is a scanner-service feature and can wait. But **SSCC on the LPN** and **GLN on
the location and the party** are identifiers that get printed on physical labels and exchanged with
trading partners, and issuing them later means re-labelling.

**Paste-ready requirement.**
> **FR-W070** · `whb_lpns.sscc` (18 digits, uk where not null), `whb_locations.gln`,
> `whb_owners.gln`, `whb_warehouses.gln`, `whb_item_aliases` already carries GTIN-13/14 (`F-006`) —
> **all v1 columns.** `whb_gs1_company_prefixes` — (owner, prefix, next_serial_reference,
> check_digit_method) for issuing our own SSCCs, v2. A `ScanParseService` decoding GS1-128 and
> GS1 DataMatrix into (GTIN, batch, expiry, serial, quantity, SSCC), v2, used by every scan entry
> point so a single scan resolves item + lot + expiry in one action.

---

### `F-071` · EPCIS
**MINOR · feature · `warehouse` · v3 · Products: Da Vinci `◐`, Made4net `◐`, Amazon `◐`; the standard is the reference, not any product**

**What it is and why it is here.** GS1 EPCIS 2.0 describes supply-chain events as *what · when · where
· why*, in four event types — `ObjectEvent` (something happened to these EPCs), `AggregationEvent`
(these were put on that pallet), `TransactionEvent` (these were associated with this business
transaction), `TransformationEvent` (these inputs became those outputs). Pharma serialisation regimes
and large retail trading-partner programmes require it.

**The design consequence, which is not deferred.** Our movement port (§3) must be *shaped* like this,
because these four event types are exactly `MOVE`, `LPN_AGGREGATE`, the source-lineage triple, and
`WORK_ORDER_COMPLETE`. If the port carries what/when/where/why/whose, EPCIS output in v3 is a
**projection**. If it does not, EPCIS is a second event stream and a second source of truth.

**Paste-ready requirement.**
> **FR-W071** · v3: `EpcisProjectionService` rendering `whb_movements` + `whb_movement_lines` +
> `whb_lpns` into EPCIS 2.0 JSON/XML, with `bizStep` and `disposition` vocabularies mapped from
> `whb_movement_types` and `whb_stock_statuses` — mappings held as **seeded rows**, not code. v1
> requirement: the port's field set must be sufficient for this projection, and §3 is written so that
> it is. No EPCIS repository, no subscription/query interface, ever — that is a partner product.

---

### `F-072` · RFID
**MINOR · feature · `warehouse` · v3 · Products: Made4net `●`, Amazon `●`, Deposco `◐`, Increff `◐`**

**Paste-ready requirement.**
> **FR-W072** · An RFID read is a **movement source**, not a new subsystem:
> `whb_movements.actor_type = 'DEVICE'` with `device_id`, and `whb_serials.epc` /
> `whb_lpns.epc` as the identifiers a read resolves to. `wh_rfid_read_events` buffers raw reads and a
> rules service converts sustained reads at a portal into movements. The v1 requirement is only that
> `actor_type`/`device_id` exist on the movement (§3) — which they must anyway, for scan guns.

---

### `F-073` · India pharma
**MINOR · feature · `warehouse-adapter-pharma` · v2 · Products: Da Vinci `●` (US), Made4net `◐`; India specifics `?`**

**Paste-ready requirement.**
> **FR-W073** · Batch-wise stock is `F-063`. Beyond it: drug licence numbers on the owner and the
> warehouse with expiry alerts, prescription-schedule flags on the item, MRP on the lot (`F-063`),
> and — for exports — barcoding/track-and-trace obligations whose current shape I will not state from
> memory (**`?`, confirm with a regulatory adviser**). Everything here is an adapter over v1 columns;
> nothing in this row changes `warehouse-base`.

---
## 2.8 Performance and SLA

### `F-074` · Lifecycle timestamps are day-one columns because a duration cannot be backfilled
**BLOCKER · schema · `warehouse` · v1 · Products: Deposco `●`, Made4net `●`, Extensiv `●`, Logiwa `●`, CartonCloud `●`, ShipBob `●`**

**What it is.** Every operational KPI in this product category is a difference between two timestamps.
Dock-to-stock is `putaway_completed_at − arrived_at`. Order cycle time is `shipped_at − released_at`.
On-time ship is `shipped_at ≤ promised_ship_at`. Not one of them can be computed from a `status`
column and an `updated_at`, because `updated_at` is overwritten by the next status change.

**Why it is a BLOCKER and not a MINOR reporting item.** These are the numbers on the client's monthly
review deck. A 3PL that cannot produce them loses the renewal. And the first time they are asked for
— which is month two of the first client — the answer has to cover month one. There is no report you
can write in month three that recovers month one's durations.

**Paste-ready requirement.**
> **FR-W074** · Explicit, immutable-once-set timestamp columns, all `v1`:
> - `wh_receipts`: `expected_at`, `vehicle_arrived_at`, `dock_assigned_at`, `unload_started_at`,
>   `unload_completed_at`, `count_completed_at`, `qc_completed_at`, `putaway_started_at`,
>   `putaway_completed_at`, `closed_at`
> - `wh_orders`: `received_at`, `promised_ship_at`, `released_at`, `allocated_at`, `pick_started_at`,
>   `pick_completed_at`, `packed_at`, `label_generated_at`, `manifested_at`, `shipped_at`,
>   `first_hold_at`, `total_hold_seconds`
> - `wh_shipments`: `shipped_at`, `first_scan_at`, `out_for_delivery_at`, `delivered_at`,
>   `rto_initiated_at`, `rto_received_at`
> - `wh_pick_tasks` / `wh_labour_tasks`: `assigned_at`, `started_at`, `completed_at`,
>   `paused_seconds`
>
> `total_hold_seconds` is stored, not derived, because hold time must be **excluded** from cycle time
> and reconstructing it from the hold table across many overlapping holds is a query nobody will get
> right twice.

---

### `F-075` · SLA definitions, measurements and breaches are objects
**MAJOR · schema · `warehouse-3pl` · v2 · Products: Made4net `●`, Extensiv `●`, CartonCloud `●`, ShipBob `●`, WareIQ `●`**

**Paste-ready requirement.**
> **FR-W075** · `wh3pl_sla_definitions` — (id, client, `metric_code` FK `wh3pl_sla_metrics`
> {`DOCK_TO_STOCK_HOURS`,`ORDER_CYCLE_HOURS`,`ON_TIME_SHIP_PCT`,`ON_TIME_DELIVER_PCT`,
> `PICK_ACCURACY_PCT`,`INVENTORY_ACCURACY_PCT`,`ORDER_FILL_RATE_PCT`,`RETURN_TAT_HOURS`,
> `NDR_RESPONSE_HOURS`,`SHORT_SHIP_PCT`}, `target_value`, `comparison` ∈ {`LTE`,`GTE`},
> `measurement_window` ∈ {`DAILY`,`WEEKLY`,`MONTHLY`}, `calendar_id`, `exclusion_rule_ids`,
> `penalty_charge_code_id` nullable, `penalty_basis`, effective_from/to).
> `wh3pl_sla_measurements` — (definition, period_start, period_end, `numerator`, `denominator`,
> `measured_value`, `sample_count`, `computed_at`, `is_breach`, `excluded_count`).
> `wh3pl_sla_breaches` — (measurement, severity, acknowledged_by, root_cause_code, corrective_action,
> `credit_event_id` nullable). Measurements store numerator and denominator, not just the percentage,
> because every SLA conversation begins with "which orders were in the denominator".

---

### `F-076` · Inventory accuracy needs the count to be a ledger event with a variance reason
**MAJOR · schema · `warehouse-base` + `warehouse` · v1 (count) / v2 (ABC + accuracy metric) · Products: all `●`**

**Paste-ready requirement.**
> **FR-W076** · `wh_cycle_counts` — (id, warehouse, `count_type` ∈ {`CYCLE`,`FULL`,`SPOT`,`BLIND`,
> `RECOUNT`,`AUDIT`}, `owner_id` nullable, scope (zone/location/item/lot/abc class), `scheduled_for`,
> started_at, completed_at, counted_by, `approved_by`, `approval_threshold_breached`, status).
> `wh_cycle_count_lines` — (count, location, owner, item, lot, serial, lpn, status,
> `system_quantity` — snapshotted at count creation — `counted_quantity`, `variance_quantity`,
> `variance_value`, `variance_reason_code`, `recount_of_line_id`, `movement_id` — the adjustment
> posted). `whb_items.abc_class` + `wh_count_schedules` (abc class, frequency, warehouse) in v2.
> **Accuracy is measured on lines, not on value**: `1 − (|variance lines| ÷ counted lines)` by
> location and by piece, both reported, because a client's contract will name one of them and it is
> never obvious which.

---

### `F-077` · Client-facing SLA reporting
**MAJOR · feature · `warehouse-3pl` · v2 · Products: Extensiv `●`, CartonCloud `●`, ShipBob `●`, Made4net `●`, WareIQ `●`**

**Paste-ready requirement.**
> **FR-W077** · A portal **Performance** tab rendering `wh3pl_sla_measurements` as trend plus current
> period, with drill-through to the failing orders (permission-filtered to the client's own owner),
> and a scheduled monthly PDF/Excel. It reuses the platform's export and grid framework rather than a
> charting side-product.

---

### `F-078` · SLA penalties and service credits post to the billing run
**MINOR · feature · `warehouse-3pl` · v3 · Products: Made4net `◐`, CartonCloud `◐`, Extensiv `◐`; contractually universal, systematically rare**

**Paste-ready requirement.**
> **FR-W078** · A confirmed breach with a `penalty_charge_code_id` posts a negative billable event on
> the `SLA_CREDIT` charge code (`F-013`), subject to approval, appearing on the next billing run as a
> visible credit line. Deferred to v3 because until `F-075`'s measurements are trusted, an automatic
> credit is a liability — but the charge code and the FK exist from v1.1 so the wiring is a service,
> not a migration.

---

### `F-079` · Labour tracking, then labour standards
**MINOR · feature · `warehouse` · v2 (tracking) / v3 (standards) · Products: Deposco `●`, Made4net `●`, Logiwa `●`, CartonCloud `●`**

**Paste-ready requirement.**
> **FR-W079** · v2 is `wh_labour_tasks` (`F-023`) plus a UPH report by user, task type and shift.
> v3 adds `wh_labour_standards` — (task_type, item_group nullable, zone nullable, `standard_minutes`,
> `setup_minutes`, `travel_factor`) and a performance-to-standard measure. Do not build v3 before
> v2 has a year of data; an engineered standard set from a vendor's textbook is worse than no
> standard.

---

### `F-080` · Dock appointments, and the door is a warehouse resource
**MINOR · schema+feature · `warehouse` · v2 · Products: Made4net `●`, CartonCloud `●`, ShipBob `●`, Deposco `◐`**

**Why it is warehouse-side and not logistics-side.** The dock door is capacity inside our four walls,
it is the resource that dock-to-stock is measured against, and detention charges (`F-018`) are billed
from it. The **vehicle, the trip and the driver** on the other side of the door belong to the future
logistics module (§4). The appointment is the join between them.

**Paste-ready requirement.**
> **FR-W080** · `wh_docks` — (warehouse, door code, `dock_type` ∈ {`INBOUND`,`OUTBOUND`,`BOTH`},
> `vehicle_types_supported`, is_active). `wh_dock_appointments` — (id, dock, `direction`,
> `scheduled_from`, `scheduled_to`, `carrier_id` nullable, `owner_id` nullable, `reference_type`,
> `reference_id`, `vehicle_number`, `driver_name`, `driver_phone`, `arrived_at`, `docked_at`,
> `departed_at`, `status`, `no_show`, `detention_minutes`) — where `detention_minutes` is what a
> `DETENTION` accessorial is metered from, and `arrived_at` is what dock-to-stock starts from.
> The future logistics module **reads** the appointment and posts arrival/departure through the port
> (§4); it does not own the door.

---

## 2.9 The movement port and the ledger

The eleven findings below are all consequences of §3, and §3 states the full specification. They are
listed here so that each is individually reviewable, individually assignable and individually
testable.

### `F-081` · Idempotency key with strict conflict semantics
**BLOCKER · schema · `warehouse-base` · v1 · Products: ShipEngine `●`, Flexport `●`, Amazon SP-API `●`; most WMS `◐`**

**Paste-ready requirement.**
> **FR-W081** · `whb_movements` — (`source_system`, `idempotency_key`) unique, both `NOT NULL`, plus
> `payload_hash`. A repeat with the **same** hash returns `200` and the original movement id. A repeat
> with a **different** hash returns `409 IDEMPOTENCY_KEY_REUSED` and posts nothing. A missing key is
> `422 IDEMPOTENCY_KEY_REQUIRED` — never generated server-side, because a server-generated key makes
> a retried network timeout post twice, which is the exact failure the key exists to prevent.

### `F-082` · Append-only; correction is reversal
**BLOCKER · schema · `warehouse-base` · v1**
> **FR-W082** · No `UPDATE` and no `DELETE` on `whb_movements` / `whb_movement_lines`, enforced by a
> database trigger, not by convention. `reversal_of_movement_id`, `reversed_by_movement_id`,
> `is_reversed` on the header; `POST /movements/{id}/reverse` with its own idempotency key; a
> reversal is itself irreversible (reversing a reversal is `422`) and re-reversal is a new forward
> movement. `whb_movements.sequence_no` BIGINT gapless per warehouse plus `prev_payload_hash` gives a
> tamper-evident chain — the same discipline the accounting design set adopted for journals, and the
> reason a client can be shown an unarguable stock history.

### `F-083` · Three time columns, not one
**BLOCKER · schema · `warehouse-base` · v1**
> **FR-W083** · `occurred_at` (business time, producer-supplied, `TIMESTAMP WITH TIME ZONE`),
> `recorded_at` (server clock, set by us), `effective_date` (`DATE`, the billing/accounting date).
> Storage anniversary billing (`F-015`) reads `occurred_at`; period close (`F-085`) reads
> `effective_date`; latency diagnostics and idempotent replay read the difference between the first
> two. A scan gun that syncs after four hours offline supplies `occurred_at` from the device;
> collapsing the three loses that permanently.

### `F-084` · Source lineage is four columns, not a free-text reference
**BLOCKER · schema · `warehouse-base` · v1**
> **FR-W084** · `source_system`, `source_document_type`, `source_document_id`,
> `source_document_line_no` on the header (and `source_line_ref` per line), all indexed. This is what
> makes "every movement for trip `T`", "every movement for order `O`", "every movement this channel
> adapter posted" a single indexed query, and it is what the future logistics module (§4) uses to
> find its own movements without `warehouse-base` knowing what a trip is.

### `F-085` · Stock periods, and a closed period rejects a backdated post
**MAJOR · schema · `warehouse-base` · v1**
> **FR-W085** · `whb_stock_periods` — (warehouse, period_start, period_end, `status` ∈
> {`OPEN`,`SOFT_CLOSED`,`CLOSED`}, closed_by, closed_at). A movement whose `effective_date` falls in
> a `CLOSED` period is rejected `422 PERIOD_CLOSED`; `SOFT_CLOSED` requires an override permission and
> records the override. Without this, a 3PL invoice approved in April silently changes in May and the
> client's reconciliation breaks with no explanation available.

### `F-086` · Outbox with a sequence cursor
**MAJOR · schema · `warehouse-base` · v1** — specified in `F-012`; repeated here as the port's own
obligation. Consumers are not registered in base; base does not know they exist.

### `F-087` · Movement types are rows, attributes are a typed side table, and nothing is JSONB
**MAJOR · schema · `warehouse-base` · v1**
> **FR-W087** · `whb_movement_types` is a seeded table with behaviour flags
> (`affects_on_hand`, `affects_available`, `balance_rule`, `allows_mixed_owner`, `is_financial`,
> `requires_reason_code`, `requires_approval`, `default_stock_status_code`,
> `allowed_from_status_codes`, `allowed_to_status_codes`, `is_reversal_only`) — **not a Java enum and
> not a `CHECK` constraint on a varchar**, because an adapter for a new vertical adds a movement type
> and must not need a core release. Extra producer-specific data goes in
> `whb_movement_line_attributes` — (movement_line_id, `attribute_key` FK to a registered key table,
> `attribute_value`, `value_type`) — a typed EAV side table, because **CLAUDE.md forbids JSONB** and
> because an unregistered key is how a schema becomes unqueryable.

### `F-088` · Value-only movements, or landed cost can never be applied
**MAJOR · schema · `warehouse-base` · v1**
> **FR-W088** · A movement type with `affects_on_hand = false` and a non-zero value:
> `COST_ADJUSTMENT`, `REVALUATION`, `LANDED_COST_APPLY`, `WRITE_DOWN`. Freight, duty and clearing
> charges arrive days after the goods and belong on the received lot; a ledger whose only currency is
> quantity can never accept them, and the accounting module's stock account then permanently
> disagrees with the warehouse. Zero-quantity lines must be legal from day one, which also means
> `quantity` has no `CHECK (quantity <> 0)`.

### `F-089` · `IN_TRANSIT` is a location type, and a warehouse row may map to no building
**MAJOR · schema · `warehouse-base` · v1 · the single most important seam column for §4**
> **FR-W089** · `whb_location_types` seeded: `RECEIVING`, `BULK`, `PICK_FACE`, `PACK`, `STAGING`,
> `DOCK`, `QUARANTINE`, `DAMAGE`, `RETURNS`, `WORK_AREA`, `IN_TRANSIT`, `VIRTUAL_CUSTOMER`,
> `VIRTUAL_SUPPLIER`, `VIRTUAL_LOSS`. `whb_warehouses.is_physical` boolean, so a carrier or a trip
> can be a virtual warehouse holding in-transit stock. A stock transfer becomes two movements — out
> of A into transit, out of transit into B — which is what makes goods on a truck **visible and
> countable** and what lets a transit loss be adjusted against the right party. Retrofitting this
> after a year means every historic transfer is a single movement with no in-transit state and
> in-transit ageing is unanswerable for the past.

### `F-090` · Negative stock policy is data
**MAJOR · schema · `warehouse-base` · v1**
> **FR-W090** · `whb_negative_stock_policies` — (warehouse nullable, owner nullable, item_group
> nullable, `policy` ∈ {`BLOCK`,`WARN`,`ALLOW`}, priority). Most warehouses want `BLOCK`; a
> high-throughput operation with asynchronous receipt confirmation wants `ALLOW` with a reconciliation
> report; a 3PL wants `BLOCK` per client because a negative balance on a client's stock is a claim.
> Hard-coding either answer makes a segment unsellable.

### `F-091` · The balance projection is rebuildable, and a ratchet test proves it
**MAJOR · feature · `warehouse-base` · v1**
> **FR-W091** · `whb_stock_balances` is a projection with `last_movement_sequence_no`. A
> `RebuildBalancesService` recomputes it from the ledger for a scope, and a scheduled reconciliation
> job asserts `Σ whb_movement_lines.base_quantity == whb_stock_balances.quantity_on_hand` per key,
> raising an alert on any divergence. A **test that fails the build** on divergence for a seeded
> scenario set is the cheapest insurance in the product: once the projection and the ledger disagree
> in production, no one can tell which is right.

### `F-092` · Batch posting for offline devices
**MINOR · feature · `warehouse-base` · v1.1**
> **FR-W092** · `POST /movements/batch` accepting up to N movements, each with its **own** idempotency
> key, each posted in its own transaction, returning a per-movement result array with per-movement
> error codes. Never all-or-nothing across the batch: a scan gun that syncs 400 movements after a
> shift must not lose 399 because one bin was renamed.

### `F-093` · UOM conversion is frozen at post time
**MAJOR · schema · `warehouse-base` · v1**
> **FR-W093** · `whb_movement_lines` carries `uom_code` and `quantity` **as entered** plus
> `base_uom_code`, `base_quantity` and `conversion_factor_used`, all computed at post and never
> recomputed. `whb_item_uoms` — (item, uom, `factor_to_base`, `is_purchase`, `is_sales`, `is_stock`,
> `barcode` via aliases, effective_from) changes over time — a case pack goes from 12 to 10 — and a
> ledger that re-derives the base quantity from today's factor silently restates last year's stock.

---

## 2.10 Index — all 93, by severity, with the module, the version and the kind

`Kind`: **schema** = a column/key/table that must land in the stated version · **feature** = a screen
or service, deferrable · **seam** = an interface decision between two modules.

| ID | Sev | Kind | Module | Version | Finding |
|---|---|---|---|---|---|
| `F-001` | BLOCKER | schema | base | v1 | `owner_id` NOT NULL on every ledger, balance, lot, serial, LPN, reservation |
| `F-002` | BLOCKER | schema | base | v1 | `whb_owners` + owner types in base; `wh3pl_clients` is a separate object |
| `F-004` | BLOCKER | schema | base+platform | v1 | Owner-scoped access grants, enforced server-side by a shared resolver |
| `F-010` | BLOCKER | schema | base | v1 | Bailment — `is_financial` + `cost_basis`; client stock never posts to our GL |
| `F-011` | BLOCKER | schema | 3pl | v1.1 | Append-only billable-event meter with idempotency and reversal |
| `F-012` | BLOCKER | seam | base | v1 | Outbox emits at billable granularity — per receipt line, putaway, pick line, carton |
| `F-021` | BLOCKER | seam | 3pl↔accounting | v1.1 | Emit an AR envelope; build no invoice, no numbering, no tax engine |
| `F-028` | BLOCKER | schema | base | v1 | Reservations as a table; availability is computed, never stored |
| `F-042` | BLOCKER | schema | adapter | v1.1 | India AWB pool — no label without pre-fetched waybill blocks |
| `F-044` | BLOCKER | schema+feature | warehouse+adapter | v1.1 | India NDR queue with a response clock and an action API |
| `F-045` | BLOCKER | schema+feature | warehouse | v1.1 | India COD remittance reconciliation by AWB, with UTR and shortfall |
| `F-046` | BLOCKER | schema+feature | warehouse | v1.1 | India RTO as an inbound stock stream matched by AWB (columns in v1) |
| `F-059` | BLOCKER | schema | base | v1 | Mixed-owner movement; balance per `(owner, item)`, not per movement |
| `F-063` | BLOCKER | schema | base | v1 | `lot_id` / `serial_id` on the ledger line; lot attributes incl. expiry, origin, MRP |
| `F-064` | BLOCKER | schema | base | v1 | LPN as a ledger object; `received_at` is the storage-anniversary anchor |
| `F-068` | BLOCKER | schema | base | v1 | Stock status vocabulary; quarantine is a status, not a location |
| `F-074` | BLOCKER | schema | warehouse | v1 | Lifecycle timestamps — a duration cannot be backfilled |
| `F-081` | BLOCKER | schema | base | v1 | Idempotency key with same-hash/different-hash conflict semantics |
| `F-082` | BLOCKER | schema | base | v1 | Append-only ledger; correction by reversal; gapless sequence + hash chain |
| `F-083` | BLOCKER | schema | base | v1 | `occurred_at` · `recorded_at` · `effective_date` as three columns |
| `F-084` | BLOCKER | schema | base | v1 | Four-column source lineage, not a free-text reference |
| `F-003` | MAJOR | schema | base | v1 / v1.1 | Commingle policy + dedicated owner + zone allocation |
| `F-005` | MAJOR | schema | base | v1 | Item uniqueness is `(owner_id, sku)` |
| `F-006` | MAJOR | schema | base | v1 | One alias table = client SKU + GTIN + marketplace codes + pack qty |
| `F-007` | MAJOR | feature | 3pl | v1.1 | Client onboarding object, tasks, per-client number series |
| `F-008` | MAJOR | feature | 3pl | v1.1 / v2 | Client portal as a permission surface, not a second application |
| `F-013` | MAJOR | schema | 3pl | v1.1 | Charge-code master with SAC/HSN and a revenue purpose code |
| `F-014` | MAJOR | schema | 3pl | v1.1 / v2 | Versioned effective-dated rate cards; tiers; fail-rather-than-guess |
| `F-015` | MAJOR | schema+feature | 3pl | v1.1 / v2 | Four storage methods × seven bases; free days; aged surcharge |
| `F-016` | MAJOR | schema | 3pl | v1.1 | Persisted daily storage snapshots, superseded not updated |
| `F-017` | MAJOR | feature | 3pl | v1.1 | Minimum monthly charge as a metered true-up event |
| `F-018` | MAJOR | feature | 3pl | v1.1 | Accessorials with an author, a reason and an approval threshold |
| `F-019` | MAJOR | schema | 3pl | v1.1 | Billing run with a frozen approved state; unrated events block review |
| `F-020` | MAJOR | feature | 3pl | v2 | Disputes raised from the portal; credits are charge codes |
| `F-023` | MAJOR | feature | warehouse+3pl | v2 | Labour-minute VAS billing and cost-to-serve |
| `F-025` | MAJOR | seam | 3pl+adapter | v1.1 | India GST/SAC, e-way bill columns in v1, client place-of-business registration |
| `F-026` | MAJOR | schema | base+adapter | v1 / v2 | Channel master in base; per-owner channel accounts; connectors are adapters |
| `F-027` | MAJOR | schema | warehouse | v1 | Idempotent order import with an external version and a decision log |
| `F-029` | MAJOR | schema+feature | warehouse | v1 / v2 | Pick tasks with short qty + reason; waves in v2 |
| `F-030` | MAJOR | schema | warehouse | v1 | Order → many shipments → many cartons; the cardinality is a one-way door |
| `F-031` | MAJOR | schema | warehouse | v1 / v1.1 | Six quantity columns on the order line; fulfilment policy per owner/channel |
| `F-032` | MAJOR | schema | warehouse | v1 / v1.1 | Priority, promise dates, working calendar with cut-offs |
| `F-033` | MAJOR | schema | warehouse | v1 | Holds as records with a release audit and per-type blocking flags |
| `F-034` | MAJOR | feature | warehouse | v1.1 | Order edit after release, as a seeded rule matrix with compensating actions |
| `F-036` | MAJOR | schema | warehouse | v1 | `wh_carrier_accounts.owner_id` — ship on the client's account |
| `F-037` | MAJOR | feature | warehouse | v2 | Rate shopping with the quote persisted; bounded rule rows |
| `F-038` | MAJOR | schema+feature | warehouse | v1 / v2 | Item dims and weights in v1; packaging master; dim weight; cartonisation in v2 |
| `F-039` | MAJOR | schema | warehouse | v1.1 | Labels as stored artefacts with a void path |
| `F-040` | MAJOR | schema | warehouse | v1.1 | Manifest · handover · pickup request are three objects |
| `F-043` | MAJOR | schema | warehouse | v1.1 | Tracking events normalised **and** raw; carrier status mappings as data |
| `F-047` | MAJOR | schema+feature | warehouse | v2 | Weight-discrepancy disputes; pack photo captured in v1 |
| `F-050` | MAJOR | schema | warehouse | v1.1 | Return receipt is primary; the RMA is optional and matched later |
| `F-051` | MAJOR | schema+feature | warehouse | v1.1 | Inspection grading with photographs at receipt |
| `F-052` | MAJOR | schema | base+warehouse | v1.1 | Disposition vocabulary; each value posts a specified movement |
| `F-053` | MAJOR | seam | warehouse→channel | v1.1 | Emit the disposition; never decide a refund |
| `F-054` | MAJOR | schema | base | v1 | `return_type` — the disposition rules branch on it |
| `F-057` | MAJOR | schema | base | v1.1 | Kit master; virtual and physical are one BOM and two behaviours |
| `F-058` | MAJOR | schema | warehouse | v1.1 | Work order = VAS record = light-manufacturing record |
| `F-065` | MAJOR | schema | base | v1 derivable / v2 table | Lot and serial genealogy |
| `F-066` | MAJOR | feature | warehouse | v2 | Recall — quarantine in place, list consignees, release reservations |
| `F-067` | MAJOR | schema | base | v1 / v1.1 | FEFO in v1; minimum-remaining-shelf-life rules in v1.1 |
| `F-075` | MAJOR | schema | 3pl | v2 | SLA definitions, measurements (numerator + denominator), breaches |
| `F-076` | MAJOR | schema | base+warehouse | v1 / v2 | Cycle counts as ledger events with variance reasons; ABC in v2 |
| `F-077` | MAJOR | feature | 3pl | v2 | Client-facing SLA reporting in the portal |
| `F-085` | MAJOR | schema | base | v1 | Stock periods; a closed period rejects a backdated post |
| `F-086` | MAJOR | schema | base | v1 | Outbox with a gapless sequence cursor; base knows no consumers |
| `F-087` | MAJOR | schema | base | v1 | Movement types are rows; attributes are a typed side table; no JSONB |
| `F-088` | MAJOR | schema | base | v1 | Value-only movements — landed cost, revaluation, write-down |
| `F-089` | MAJOR | schema | base | v1 | `IN_TRANSIT` location type; non-physical warehouses |
| `F-090` | MAJOR | schema | base | v1 | Negative-stock policy as data, scoped by warehouse/owner/item group |
| `F-091` | MAJOR | feature | base | v1 | Rebuildable balance projection + a reconciliation ratchet test |
| `F-093` | MAJOR | schema | base | v1 | UOM conversion frozen at post time |
| `F-009` | MINOR | schema | base | v1 / v1.1 | `OWNER_CHANGE` — title moves, goods do not |
| `F-022` | MINOR | feature | 3pl | v3 | Rate escalation generates a new card version, never mutates one |
| `F-024` | MINOR | schema | 3pl | v1.1 | Four freight-billing modes incl. the client's own carrier account |
| `F-035` | MINOR | schema | warehouse | v2 | Channel inventory publish rules — the oversell control |
| `F-041` | MINOR | schema | warehouse+adapter | v1.1 / v2 | Pincode serviceability (India, v1.1); address validation (v2) |
| `F-048` | MINOR | schema | warehouse+adapter | v1 cols / v3 | HS code and origin on item **and lot**; customs declarations in v3 |
| `F-049` | MINOR | feature | warehouse | v2 | Branded tracking link + consumer notification rules |
| `F-055` | MINOR | feature | adapter | v2 | India marketplace return-claim window |
| `F-056` | MINOR | feature | warehouse | v2 | Return to vendor with a debit-note proposal |
| `F-060` | MINOR | schema | warehouse+3pl | v1.1 | Packaging and consumables are stock, and billable |
| `F-061` | MINOR | seam | adapter | v2 | India job work — challan, return clock, ITC-04 `?` |
| `F-062` | MINOR | feature | warehouse | v1.1 | Print templates with a per-owner layout |
| `F-069` | MINOR | schema+feature | warehouse | v2 | Cold-chain zones, excursions, auto-quarantine |
| `F-070` | MINOR | schema/feature | base+warehouse | v1 cols / v2 | SSCC, GLN, GTIN columns in v1; GS1-128 parsing in v2 |
| `F-071` | MINOR | feature | warehouse | v3 | EPCIS as a projection over the port, never a second stream |
| `F-072` | MINOR | feature | warehouse | v3 | RFID as a movement source; `actor_type`/`device_id` in v1 |
| `F-073` | MINOR | feature | adapter | v2 | India pharma — licences, schedules, MRP; specifics `?` |
| `F-078` | MINOR | feature | 3pl | v3 | SLA penalties post as `SLA_CREDIT` billable events |
| `F-079` | MINOR | feature | warehouse | v2 / v3 | Labour tracking, then engineered standards |
| `F-080` | MINOR | schema+feature | warehouse | v2 | Dock appointments; the door is a warehouse resource |
| `F-092` | MINOR | feature | base | v1.1 | Batch posting with per-movement idempotency for offline devices |

### The v1 schema list — the only part of this report that is genuinely urgent

Everything below is a column, a key or a small seeded table. **None of it has a v1 screen.** All of it
is unaddable or prohibitively expensive later, and together it is perhaps three weeks of schema work:

`F-001` owner_id · `F-002` whb_owners · `F-003` commingle_policy · `F-004` owner grants ·
`F-005` (owner,sku) uk · `F-006` aliases · `F-010` is_financial + cost_basis · `F-012` outbox
granularity · `F-025` e-way bill columns on transfers · `F-026` channel master · `F-028` reservations ·
`F-030` order→shipment→carton · `F-031` six quantity columns · `F-032` promise columns ·
`F-033` holds · `F-036` carrier_account.owner_id · `F-038` item dims and weights ·
`F-045` COD columns · `F-046` RTO columns · `F-047` pack photo · `F-048` hs_code + origin on the lot ·
`F-054` return_type · `F-059` per-line owner + balance_rule · `F-063` lot_id/serial_id ·
`F-064` lpn_id + lpn.received_at · `F-067` FEFO · `F-068` stock_status_code · `F-070` SSCC/GLN ·
`F-074` lifecycle timestamps · `F-076` count lines · `F-081` idempotency · `F-082` append-only +
sequence + hash · `F-083` three timestamps · `F-084` lineage quad · `F-085` stock periods ·
`F-087` movement types as rows · `F-088` value-only movements · `F-089` IN_TRANSIT ·
`F-090` negative policy · `F-093` frozen UOM.

**Forty items. Every one is a column, a key or a seeded table.** That is the whole argument of this
report in one paragraph: build a small v1 on a wide schema, and every later version is additive.

---

# 3. THE MOVEMENT PORT SPECIFICATION

This is the section the rest of the report exists to support. Everything in §1 and §2 resolves, at the
ledger, to one question: **what must an inbound "move stock" call carry so that `warehouse-base` never
has to know who called it?**

## 3.0 The design premise

The port is a **stock journal**. It is the exact analogue of an accounting journal entry: a header
with lineage and time, balanced signed lines, immutable once posted, corrected only by reversal. That
analogy is not decoration — it is the reason the shape is already known to be sufficient, because
double-entry survived two hundred years of people wanting to change history.

Five callers must be able to post through it without base depending on any of them:

| Caller | Example movement | What it needs the port to carry that a naive port would not |
|---|---|---|
| `warehouse` (our own app) | pick, pack, putaway, count | task lineage, actor, device, short reasons |
| `warehouse-adapter-<vertical>` | a dealer PDI consumes a part | a vertical's own document type and id |
| A future **logistics** module | truck departs A, arrives B, one carton lost | `IN_TRANSIT` location, trip lineage, loss reason |
| A **POS / channel** | a shop sells 3 units; a marketplace confirms an order | channel identity, external order id, business time |
| `warehouse-3pl` | title transfers from client A to client B | two owners on one movement |

If any of those five forces a column to be added to `whb_movements` later, the port was designed
wrong. The field list below is chosen so that none of them does.

## 3.1 Endpoint surface

| Method | Path | Semantics |
|---|---|---|
| `POST` | `/api/warehouse/movements` | post one movement, synchronously, all-or-nothing |
| `POST` | `/api/warehouse/movements/batch` | post many, each independently, per-movement results (`F-092`) |
| `POST` | `/api/warehouse/movements/{id}/reverse` | post the mirror; own idempotency key (`F-082`) |
| `GET` | `/api/warehouse/movements/{id}` | read back, including assigned `sequence_no` |
| `GET` | `/api/warehouse/movements?source_system=&source_document_type=&source_document_id=` | lineage lookup — the call the logistics module makes to find its own postings |
| `POST` | `/api/warehouse/movements/simulate` | validate and return the resulting balance deltas **without posting** — the analogue of a posting preview; the single cheapest support tool in the product |

`@PreAuthorize` on every method (`warehouse:movements:post`, `:reverse`, `:view`, `:simulate`), per
this monorepo's non-negotiable rule. The posting permission is additionally checked against the
caller's owner grants (`F-004`).

## 3.2 Header — `whb_movements`

| Field | Type | Null | Day one? | Why, and what is irreversible about it |
|---|---|---|---|---|
| `id` | UUID | no | yes | — |
| `company_id` | UUID | no | **yes** | Cross-GSTIN transfers (`F-025`) and multi-entity installs. Adding a company axis after the ledger has rows means every historic row is assigned to a guessed entity, and a GST return computed from guessed entities is a filing error |
| `warehouse_id` | UUID | no | **yes** | The gapless `sequence_no` is per warehouse; adding the axis later renumbers history |
| `movement_type_code` | varchar FK `whb_movement_types` | no | **yes** | A **row, not an enum** (`F-087`). A vertical adapter that needs `PDI_CONSUME` must not need a core release. If this is a Java enum or a `CHECK` constraint, every adapter is blocked on base |
| `source_system` | varchar | no | **yes** | Half of the idempotency key. Cannot be inferred later — two producers' keys would collide retroactively |
| `source_document_type` | varchar | no | **yes** | `SALES_ORDER`, `TRIP`, `POS_SHIFT`, `WORK_ORDER`… (`F-084`) |
| `source_document_id` | varchar | no | **yes** | Deliberately varchar, not UUID: an external system's id is not ours |
| `source_document_line_no` | int | yes | **yes** | Without it, a partially reversed multi-line source document cannot be reconciled line by line |
| `idempotency_key` | varchar | no | **yes** | uk(`source_system`,`idempotency_key`). **The most irreversible field in the schema**: a ledger that has already double-posted cannot be deduplicated afterwards, because the duplicate is indistinguishable from a legitimate repeat of the same real event (`F-081`) |
| `payload_hash` | char(64) | no | **yes** | Distinguishes "retry" from "different payload, reused key". Without it the conflict rule cannot exist |
| `occurred_at` | timestamptz | no | **yes** | Business time, **producer-supplied**. Storage anniversary billing, dock-to-stock and offline scanner sync all read it (`F-015`, `F-074`, `F-083`). Cannot be reconstructed from `recorded_at` |
| `recorded_at` | timestamptz | no | **yes** | Server clock. The difference from `occurred_at` is the only latency diagnostic that exists |
| `effective_date` | date | no | **yes** | The billing/accounting date. Diverges from `occurred_at` when a period is closed or a client's cycle differs. Collapsing them means a 2nd-of-month posting of a 31st-of-month event silently lands in the wrong invoice |
| `sequence_no` | bigint | no | **yes** | Gapless per warehouse. The outbox cursor and the hash chain both key on it; a sequence cannot be started retroactively over rows that already exist (`F-082`, `F-086`) |
| `prev_payload_hash` | char(64) | yes | **yes** | Tamper evidence. A chain begun in v2 proves nothing about v1 |
| `reversal_of_movement_id` | UUID | yes | **yes** | If v1 permits `UPDATE`, the history is already gone by the time the column arrives |
| `reversed_by_movement_id` | UUID | yes | yes | Denormalised for the "is this still live" query |
| `is_reversed` | boolean | no | yes | — |
| `actor_type` | varchar | no | **yes** | `USER`, `DEVICE`, `INTEGRATION`, `SCHEDULED_JOB`, `IMPORT`, `SYSTEM_CORRECTION`. "Who moved this" is the first audit question and it is not always a user. RFID (`F-072`) needs `DEVICE` and it must already exist |
| `actor_user_id` | UUID | yes | yes | — |
| `device_id` | varchar | yes | **yes** | Which scan gun, which RFID portal, which dock terminal. Diagnosing a mis-scanning device retroactively is impossible without it |
| `reason_code_id` | UUID FK | yes | **yes** | Adjustments, losses, short picks, damage. A reason recorded as free text in v1 is a categorical dimension that can never be reported on |
| `notes` | text | yes | yes | — |
| `approval_status` / `approved_by` / `approved_at` | — | yes | yes | For movement types with `requires_approval` (scrap, write-down) |
| `posted_at` | timestamptz | no | yes | — |
| standard audit columns | — | — | yes | `created_by`, `created_at` per house convention |

**Not on the header, deliberately:** `owner_id` (it is per line — `F-059`), `item_id`, `quantity`,
`location_id` (a movement is not a single line), and any JSONB payload (`F-087`).

## 3.3 Lines — `whb_movement_lines`

| Field | Type | Null | Day one? | Why, and what is irreversible about it |
|---|---|---|---|---|
| `movement_id` | UUID | no | yes | — |
| `line_no` | int | no | yes | — |
| **`owner_id`** | UUID FK | **no** | **yes** | `F-001`, `F-059`. Backfill is impossible; the balance unique key changes; every query changes grain. **The single most expensive column to add late in the entire design** |
| `item_id` | UUID FK | no | yes | — |
| `quantity` | numeric(18,4) | no | yes | **Signed.** No `CHECK (quantity <> 0)` — value-only movements need zero (`F-088`) |
| `uom_code` | varchar | no | **yes** | As entered by the producer |
| `base_uom_code` | varchar | no | **yes** | — |
| `base_quantity` | numeric(18,4) | no | **yes** | Computed at post |
| `conversion_factor_used` | numeric(18,8) | no | **yes** | `F-093`. Conversion factors change; a ledger that re-derives from today's factor silently restates last year's stock, and the restatement is undetectable |
| `from_location_id` | UUID FK | yes | yes | Null for a receipt |
| `to_location_id` | UUID FK | yes | yes | Null for an issue |
| `from_lpn_id` / `to_lpn_id` | UUID FK | yes | **yes** | `F-064`. Per-pallet and anniversary storage billing are defined over pallets, and a pallet the ledger never recorded cannot be billed for the past |
| `lot_id` | UUID FK | yes | **yes** | `F-063`. A recall is a question about the past |
| `serial_id` | UUID FK | yes | **yes** | `F-063` |
| `stock_status_code` | varchar FK | no | **yes** | `F-068`. Otherwise quarantine is modelled as a location and "damaged stock in the bulk aisle" is unrepresentable — and the balance unique key is wrong for every historic row |
| `from_stock_status_code` | varchar FK | yes | **yes** | A `STATUS_CHANGE` needs both ends on one line or two lines; either way the column must exist |
| `unit_cost` | numeric(18,6) | yes | **yes** | `F-010`, `F-088` |
| `cost_currency_code` | char(3) | yes | **yes** | — |
| `extended_cost` | numeric(18,4) | yes | yes | — |
| `cost_basis` | varchar | no | **yes** | `ACTUAL`·`STANDARD`·`AVERAGE`·`INFORMATIONAL`·`ZERO_BAILMENT` (`F-010`). Decides whether an accounting envelope is emitted. Decided downstream = a year of wrong journals |
| `reason_code_id` | UUID FK | yes | yes | Line-level override of the header reason |
| `source_line_ref` | varchar | yes | **yes** | The producer's own line identity, distinct from `source_document_line_no` on the header |
| `expiry_date_override` | date | yes | yes | Where the producer knows an expiry the lot record does not yet carry |
| `qc_result_code` | varchar | yes | yes | Receipt lines that arrive already inspected |

**Attributes side table** `whb_movement_line_attributes` — (movement_line_id, `attribute_key_id` FK to
a registered key table, `attribute_value`, `value_type`). Registered keys only. **No JSONB** — CLAUDE.md
forbids it, and an unregistered key is a column nobody can filter, export or index.

## 3.4 The seven axes, and why they are exactly seven

| Axis | Columns | The question it answers |
|---|---|---|
| **What** | `item_id`, `lot_id`, `serial_id`, `lpn_id`, `quantity`, `uom` | which physical things |
| **Where** | `from_location_id`, `to_location_id`, `warehouse_id` | between which places, including virtual ones |
| **When** | `occurred_at`, `recorded_at`, `effective_date` | in business time, in record time, in ledger time |
| **Why** | `movement_type_code`, `reason_code_id`, source lineage quad | what business act caused it |
| **Who** | `actor_type`, `actor_user_id`, `device_id` | who or what performed it |
| **Whose** | `owner_id`, `cost_basis` | on whose account, and whether it is ours financially |
| **What it is worth** | `unit_cost`, `cost_currency_code`, `extended_cost` | what the accounting module should do about it |

GS1 EPCIS names the first five (`what · where · when · why · who`). The last two are what the standard
leaves to the implementer and are exactly the two that a 3PL and an accounting integration cannot do
without. A port with all seven can emit EPCIS as a projection (`F-071`), feed a billing meter
(`F-012`), feed an accounting adapter (`F-010`), and satisfy a logistics module (§4), with no
schema change for any of them.

## 3.5 Validation and error semantics

**Atomicity.** A movement posts wholly or not at all. There is **no partial success** on a single
movement. A producer that wants per-line independence sends one movement per line, and the batch
endpoint (`F-092`) gives it per-movement independence.

**Idempotency, precisely.**

| Condition | Response |
|---|---|
| Key unseen | `201`, movement id, assigned `sequence_no` |
| Key seen, `payload_hash` identical | `200`, the **original** movement id. Not an error |
| Key seen, `payload_hash` different | `409 IDEMPOTENCY_KEY_REUSED`, nothing posted, response names the original movement id |
| Key absent | `422 IDEMPOTENCY_KEY_REQUIRED`. **Never generate one server-side** — a server-generated key makes a retried network timeout post twice, which is the exact failure the key exists to prevent |

**Error codes.** Machine-readable, per line where applicable, in the platform's standard
`{ "error": …, "details": { "errors": { … } } }` envelope:

`UNKNOWN_ITEM` · `UNKNOWN_LOCATION` · `UNKNOWN_OWNER` · `UNKNOWN_LOT` · `UNKNOWN_SERIAL` ·
`UNKNOWN_LPN` · `UNKNOWN_MOVEMENT_TYPE` · `LOT_REQUIRED` · `SERIAL_REQUIRED` ·
`SERIAL_ALREADY_ISSUED` · `SERIAL_NOT_AT_LOCATION` · `INSUFFICIENT_STOCK` ·
`NEGATIVE_STOCK_NOT_ALLOWED` · `MOVEMENT_UNBALANCED` · `MIXED_OWNER_NOT_ALLOWED` ·
`STATUS_TRANSITION_NOT_ALLOWED` · `LOCATION_POLICY_VIOLATED` · `TEMPERATURE_ZONE_MISMATCH` ·
`SHELF_LIFE_RULE_VIOLATED` · `EXPIRED_LOT_NOT_ISSUABLE` · `UOM_NOT_CONVERTIBLE` · `PERIOD_CLOSED` ·
`OWNER_NOT_PERMITTED` · `LPN_CLOSED` · `LPN_NOT_AT_LOCATION` · `APPROVAL_REQUIRED` ·
`IDEMPOTENCY_KEY_REQUIRED` · `IDEMPOTENCY_KEY_REUSED` · `ALREADY_REVERSED` ·
`CANNOT_REVERSE_A_REVERSAL` · `OCCURRED_AT_IN_FUTURE`.

Every code is **stable and documented from v1**, because a producer's retry logic branches on them and
renaming one is a breaking change to five callers.

**Reversal.**
- `POST /movements/{id}/reverse` with a new idempotency key and a mandatory `reason_code_id`.
- Produces a mirror movement: same lines, negated quantities, same lot/serial/LPN/status/owner,
  `movement_type_code` = the original type's `reversal_type_code`, `reversal_of_movement_id` set.
- A reversal is itself irreversible (`CANNOT_REVERSE_A_REVERSAL`); re-doing is a new forward movement.
- Reversal respects `effective_date` and the period rules — a reversal into a closed period is
  `PERIOD_CLOSED` and the correct act is a current-dated reversal, not a backdated one.
- **There is no delete and no edit.** A trigger enforces it; convention does not.

**Backdating.** Permitted while the `effective_date` falls in an `OPEN` stock period (`F-085`);
`SOFT_CLOSED` requires an override permission and records the override with the overriding user;
`CLOSED` refuses. `occurred_at` in the future is refused outright, because a future business time
breaks every ageing calculation silently.

**Simulate.** `POST /movements/simulate` runs the whole validation chain and returns the balance
deltas and the error list without writing. It is what a channel adapter calls before promising stock,
what an operator screen calls to explain a rejection, and what the support team calls when a client
says "it says insufficient stock and there are 40 on the shelf".

## 3.6 What the port must NOT carry

Stated so it is not "discovered" later as a gap:

| Not in the port | Why | Where it goes instead |
|---|---|---|
| A carrier, an AWB, a trip or a vehicle | `warehouse-base` must not know transport exists (§4) | the source lineage quad — `source_document_type = 'TRIP'` |
| A price, a customer or a tax | a movement is not a sale | the accounting envelope emitted from the outbox |
| A billing charge code | the meter subscribes to events; base does not bill | `wh3pl_billable_events` (`F-011`) |
| A channel-specific field | one channel's field becomes fifty | `whb_movement_line_attributes` with a registered key |
| A JSONB payload | CLAUDE.md forbids it, and it is how the schema becomes unqueryable | typed attribute side table |
| A free-text `reference` | it cannot be joined or indexed meaningfully | the four lineage columns (`F-084`) |
| An expression or script | the fifth rule engine always introduces one | bounded rows, as in `F-028`, `F-037`, `F-090` |

## 3.7 The day-one column list, restated as a single claim

Twelve properties, each of which is **provably unaddable** rather than merely inconvenient:

1. `owner_id` per line — no rule recovers whose a unit was.
2. `occurred_at` distinct from `recorded_at` — a device's business time is lost at sync.
3. `effective_date` distinct from both — a billed period cannot be re-derived.
4. `idempotency_key` unique + `payload_hash` — an already-duplicated ledger cannot be deduplicated.
5. Append-only + `sequence_no` + `prev_payload_hash` — a chain cannot be started over mutable history.
6. `reversal_of_movement_id` — if v1 allowed edits, the corrections are already invisible.
7. `lot_id` / `serial_id` — a recall is retrospective by definition.
8. `lpn_id` + `whb_lpns.received_at` — anniversary storage billing has no other anchor.
9. `stock_status_code` — otherwise condition and place are permanently conflated.
10. `uom_code` + frozen `conversion_factor_used` — factors change and history silently restates.
11. The lineage quad — a single free-text ref cannot be joined, and the logistics module needs to find
    its own postings.
12. `is_financial` + `cost_basis` — a year of bailed stock in our own GL is unwound by hand.

Everything else in this report can wait. These twelve cannot.

---

# 4. THE LOGISTICS / SUPPLY-CHAIN SEAM

The brief says a logistics module is planned and will integrate through `warehouse-base`'s movement
port, and that this report must say what the port has to carry so that module does not force a schema
change. §3 gives the field list. This section gives the **line** — which tables sit on which side,
and which events cross.

## 4.1 The line, in one sentence

> **Warehouse owns the goods while they are stationary and inside a boundary. Logistics owns them
> while they are moving between boundaries. The dock door is the boundary, and it is a warehouse
> resource.**

Every allocation below follows from that sentence, and where a product in the audited set disagrees —
CartonCloud is the interesting one, because it deliberately merges WMS and TMS in a single product —
the disagreement is a packaging decision, not a data-model one. CartonCloud still has consignments on
one side and stock on the other.

## 4.2 Table allocation

| Concern | `warehouse` / `warehouse-base` | future `logistics` |
|---|---|---|
| **Stock existence and position** | `whb_movements`, `whb_movement_lines`, `whb_stock_balances`, `whb_reservations`, `whb_lots`, `whb_serials`, `whb_lpns` | — reads via API, posts via the port |
| **Places** | `whb_warehouses`, `whb_locations`, `whb_zones`, `whb_docks` | `log_hubs`, `log_routes`, `log_route_stops`, `log_service_areas` |
| **The package** | `wh_shipments`, `wh_shipment_lines`, `wh_shipment_cartons`, `wh_shipment_labels` — *what is in the box, what it weighs, what it measures, where it is going* | `log_consignments`, `log_consignment_pieces` — *the transport view of the same box, with a freight rate and a route* |
| **The vehicle and the person** | — | `log_vehicles`, `log_drivers`, `log_driver_shifts`, `log_vehicle_documents`, `log_fuel_entries`, `log_maintenance` |
| **The journey** | — | `log_trips`, `log_trip_stops`, `log_trip_legs`, `log_trip_events`, `log_gps_pings`, `log_pods` |
| **Handover** | `wh_manifests`, `wh_handovers`, `wh_pickup_requests` (`F-040`) | `log_trip_stops` referencing the handover |
| **The door** | `wh_docks`, `wh_dock_appointments` (`F-080`) | reads the appointment; posts arrival/departure |
| **Freight money** | `wh3pl_billable_events` for the **pass-through** charge to the client (`F-024`) | `log_freight_rate_cards`, `log_freight_charges`, `log_carrier_invoices`, `log_carrier_invoice_reconciliation` |
| **Third-party carriers** | `wh_carriers`, `wh_carrier_services`, `wh_carrier_accounts` — because v1 ships parcels long before a logistics module exists | migrates to logistics when it lands; the warehouse continues to *read* it. **This is the one boundary that moves**, and §4.5 says how |
| **Tracking of a third-party parcel** | `wh_shipment_tracking_events`, `wh_shipment_ndrs`, `wh_cod_remittances`, `wh_rto_consignments` | for **own-fleet** movements, `log_trip_events` is the equivalent and maps into the same normalised status vocabulary |
| **Demand for transport** | `wh_stock_transfers` — "these goods need to go from A to B" | `log_transport_orders` — "here is a vehicle and a route that will do it" |
| **Planning** | putaway, allocation, waving (`F-029`) | route optimisation, load planning, vehicle capacity, multi-drop sequencing |
| **In-transit stock** | **`whb_locations` of type `IN_TRANSIT` on a non-physical warehouse (`F-089`)** | posts the two movements that put stock into and out of it |

## 4.3 In-transit stock is the whole seam

This is the design decision that either makes the seam clean or makes it a permanent argument.

**The wrong model.** A transfer is one movement: stock leaves A and appears at B. Between the two,
either it is at A (wrong — A has counted it out) or at B (wrong — B has not received it). Any real
implementation of that model ends with a "goods in transit" *report* computed by subtracting despatches
from receipts, which cannot be counted, cannot be adjusted, cannot be aged, cannot be insured and
cannot be attributed when a carton goes missing.

**The right model.** A transfer is at least **two** movements:

```
  TRANSFER_DEPART   A/PICK_FACE ──(-)──►  TRANSIT-WH / IN_TRANSIT-<trip>   (+)
  TRANSFER_ARRIVE   TRANSIT-WH / IN_TRANSIT-<trip> ──(-)──►  B/RECEIVING   (+)
```

with `source_document_type = 'TRIP'` and `source_document_id = <trip id>` on both, so the logistics
module can find its own postings through the lineage query in §3.1 without base knowing what a trip
is. Three consequences fall out immediately, and all three are things customers ask for:

- **In-transit stock is countable and reportable.** "What is on the road right now, whose is it, how
  old is it" is a query, not a reconciliation.
- **A transit loss is a normal adjustment** against the transit location with a reason code and an
  owner — which is what makes it claimable against the carrier, and what stops it being a mysterious
  shrinkage at B.
- **A partial arrival is representable.** Twelve of fifteen cartons arrive; three stay in transit and
  age; nobody has to decide whether B "received" fifteen.

**The v1 cost of supporting this before the logistics module exists:** one `location_type` value, one
`is_physical` boolean on the warehouse, and a stock-transfer service that posts two movements instead
of one. **The v2 cost of adding it afterwards:** every historic transfer is a single movement with no
transit state, in-transit ageing is unanswerable for the past, and every transfer report in the
product changes shape.

## 4.4 The events that cross

**`warehouse` → `logistics`** (published on the base outbox, `F-012`, or on `warehouse`'s own; the
logistics module subscribes, base does not know it exists):

| Event | Payload essentials | What logistics does with it |
|---|---|---|
| `transfer.order.created` | from warehouse, to warehouse, owner, lines, weight, volume, required-by date, temperature class, hazmat class | creates a transport demand for planning |
| `shipment.ready_for_dispatch` | shipment, cartons with dims and weights, destination address, service level, promised date, COD amount, declared value | creates a consignment |
| `handover.completed` | handover id, manifest, shipment list, vehicle, person, timestamp, signature ref | takes custody; opens the trip leg |
| `dock.appointment.created` / `.changed` | dock, window, direction, reference | schedules the vehicle |
| `stock.movement.posted` | the whole movement | ledger mirror where logistics needs stock visibility |

**`logistics` → `warehouse`** (through the movement port, or through `warehouse`'s own APIs):

| Event / call | Mechanism | Notes |
|---|---|---|
| depart | `POST /movements` `TRANSFER_DEPART` | lineage `TRIP`/`<trip id>`; `occurred_at` = gate-out time |
| arrive | `POST /movements` `TRANSFER_ARRIVE` | partial arrival = fewer lines; the remainder stays in transit |
| transit loss / damage | `POST /movements` `TRANSIT_LOSS` with a reason code | against the transit location; becomes a carrier claim |
| delivery confirmed | `PATCH` on the shipment + a tracking event | not a movement — the stock already left at despatch |
| delivery failed | tracking event → NDR (`F-044`) | for own-fleet, logistics raises the NDR into the warehouse's queue |
| RTO initiated | tracking event, then an eventual `RTO_RECEIPT` movement (`F-046`) | the return leg is a new trip |
| POD captured | document link on the shipment/handover | a document, never a movement |
| freight cost known | `POST /movements` `LANDED_COST_APPLY`, zero quantity (`F-088`) | **only** where freight capitalises into inventory cost; otherwise it is purely an accounting event |
| vehicle arrived / departed at our dock | `PATCH` on `wh_dock_appointments` | drives detention (`F-018`) and dock-to-stock (`F-074`) |

## 4.5 The one boundary that will move, and how to make the move cheap

`wh_carriers` / `wh_carrier_services` / `wh_carrier_accounts` live in `warehouse` in v1 because v1
ships parcels and there is no logistics module to hold them. When logistics lands, they belong there —
a carrier is a transport concept, its rate card is a freight rate card, and its invoice is a freight
invoice.

**Make the move cheap by deciding two things now, in v1:**

1. **Nothing in `warehouse-base` references a carrier.** The ledger's only knowledge of transport is
   the lineage quad and the `IN_TRANSIT` location type. This is already true if §3 is followed, and it
   is the reason the move is a `warehouse` refactor and not a ledger migration.
2. **`wh_shipments` references the carrier by a stable code, resolved through a service**, so the
   table the code resolves in can be relocated without touching the shipment. The same pattern
   `F-021` uses for the accounting party.

**And declare the shape of the eventual merge now:** `log_consignments` will be the transport view of
`wh_shipments` with a 1:1 link, not a replacement. A shipment that is never transported by our fleet
(a third-party parcel) will simply have no consignment. That is the only allocation that keeps both
modules independently useful — a warehouse with no fleet, and a fleet moving goods a warehouse never
held.

## 4.6 What the port needs that only logistics will use

Restated from §3, as the specific answer to the brief's question:

| Port capability | Used only by logistics | Cost if missing |
|---|---|---|
| `IN_TRANSIT` location type + non-physical warehouse (`F-089`) | yes | stock falls off the books between two movements; every transfer report is rebuilt |
| Lineage quad with `source_document_type = 'TRIP'` (`F-084`) | mostly | logistics cannot find its own postings; a free-text ref is unjoinable |
| `occurred_at` supplied by the producer (`F-083`) | partly | a gate-out at 22:00 posted at 09:00 next morning dates itself wrong, and in-transit ageing is wrong by a day |
| Value-only `LANDED_COST_APPLY` (`F-088`) | mostly | freight can never capitalise into stock cost; accounting and warehouse permanently disagree |
| Reason-coded loss against a transit location (`F-090` + reason codes) | yes | transit shrinkage is indistinguishable from warehouse shrinkage, and the carrier claim has no evidence |
| Batch posting with per-movement idempotency (`F-092`) | partly | a driver's device syncing after a route loses 39 of 40 scans on one bad row |
| `actor_type = DEVICE` + `device_id` (§3.2) | partly | a GPS- or scanner-originated movement has no attributable actor |

**Seven capabilities. Six of them are day-one columns in `warehouse-base` v1, and none of them
requires `warehouse-base` to know that transport exists.** That is the test the port passes.

---

# 5. IS `warehouse-3pl` A REAL MODULE OR A FEATURE FLAG?

## 5.1 The question, stated precisely

Not "should 3PL be separately licensable" — that is a pricing question and the answer is obviously
yes. The question is: **is there enough cohesive, genuinely 3PL-only behaviour to justify a fourth
module with its own package (`ai.warehouse3pl`), its own Flyway range (V930000–V939999), its own
migration ordering risk and its own build-time integration cost?**

Answer it from the evidence, by counting.

## 5.2 The count

Of the 148 capabilities scored in §1, I classify them by where they must live:

| Class | Count | Examples |
|---|---|---|
| **A — genuinely 3PL-only, cohesive, heavy** | **41** | rate cards, charge codes, billable events, storage snapshots and their four methods, billing runs, minimums, accessorials, disputes, escalation, client onboarding, portal, SLA definitions/measurements/breaches/penalties, per-client numbering, freight pass-through modes, client GST registrations, client profitability |
| **B — looks 3PL, actually base or app, unaddable later** | **23** | `owner_id` everywhere, `whb_owners`, commingle policy, owner grants, `(owner, sku)` uniqueness, aliases, `is_financial`/`cost_basis`, outbox granularity, LPN, `lpn.received_at`, `occurred_at`, lifecycle timestamps, mixed-owner movements, per-owner carrier accounts, per-owner print templates, zone allocation, `OWNER_CHANGE` |
| **C — general WMS, needed with or without 3PL** | **69** | receiving, putaway, picking, packing, shipping, counting, returns, kitting, lots, serials, statuses, FEFO, waves, holds, tracking, NDR, COD, RTO |
| **D — India / channel / carrier surface, adapter-shaped** | **15** | AWB pool, serviceability, e-way bill, marketplace claims, job work, pharma, channel connectors |

**Class A is 28% of the surface.** That is a module. Forty-one cohesive capabilities with about
eighteen tables, one clear consumer (the meter), one clear producer (the base outbox), one clear
downstream (the accounting AR port) and one clear audience (the 3PL operator and their client). It has
its own vocabulary — charge code, rate card, billing run, storage method, accessorial, SLA credit —
that appears nowhere else in the product. Splitting it out means a customer running an own-stock
warehouse never installs a single billing table, and the accounting integration is a seam, not an
entanglement.

**Class B is 16% of the surface, and it is the real finding.** Every one of those 23 items leaks into
`warehouse-base` or `warehouse`, and every one is on the day-one list in §3.7 or §2.10. The module
split does **not** save us from them, and no feature flag can defer them.

## 5.3 The verdict, and the condition attached to it

> **`warehouse-3pl` is a real module. It is also a thin module standing on a wide base concession, and
> the concession is not optional, not deferrable and not flaggable.**

A feature flag would be the wrong shape for two independent reasons:

1. **It would not save a single column.** The unaddable items are in class B, in `warehouse-base`, and
   they are required whether or not anyone ever buys 3PL. A flag defers screens, never schema.
2. **The 30% is too big to hide behind a boolean.** Eighteen tables, a nightly snapshot job, a rating
   engine, a billing-run state machine, a portal permission surface and an accounting handoff are not
   an `if`. Behind a flag they become dead code in every install, and dead code in a Flyway-migrated
   monorepo is dead *tables* in every customer's database.

**The condition.** A module split is only honest if the dependency runs one way. State it and test it:

> `warehouse-3pl` depends on `warehouse-base` and on `warehouse`. **Neither depends on
> `warehouse-3pl`.** No table in `warehouse-base` or `warehouse` has a foreign key to a `wh3pl_*`
> table; no service imports `ai.warehouse3pl`; no migration below V930000 references a `wh3pl_` name.
> `wh3pl_clients.owner_id → whb_owners.id` is the only structural link and it points the right way.
> A build-time check enforces it, because the first violation is always innocent and always
> load-bearing.

## 5.4 What MUST land in `warehouse-base` v1 even though `warehouse-3pl` ships later

This is the operative output of §5. Every item is class B; every item is unaddable; none has a v1
screen.

| # | Must be in base/app v1 | Finding | If it is not, what breaks when 3PL ships |
|---|---|---|---|
| 1 | `owner_id NOT NULL` on every ledger line, balance, lot, serial, LPN, reservation, and in the balance unique key | `F-001` | The ledger is rebuilt and history has no recoverable owner. **The most expensive single omission in the design** |
| 2 | `whb_owners` + `whb_owner_types`, house owner seeded | `F-002` | Same as 1, plus consignment and customer-owned stock have nowhere to live in v1 either |
| 3 | `owner_id` **per line**, `balance_rule`, `allows_mixed_owner` | `F-059` | A 3PL's own packaging consumed against a client's order cannot be posted atomically |
| 4 | `is_financial` on the movement type, `cost_basis` on the line | `F-010` | A year of clients' bailed stock has posted to our own GL and is unwound by hand |
| 5 | Outbox events at billable granularity — receipt line, putaway, pick line, carton, task | `F-012` | Per-line handling billing — how every audited 3PL prices — is permanently unavailable for the past |
| 6 | `lpn_id` on the ledger, `whb_lpns.received_at` | `F-064` | Per-pallet and **anniversary** storage billing cannot be computed at all, for any period |
| 7 | `occurred_at` / `recorded_at` / `effective_date` | `F-083` | Storage days, split-month and anniversary all bill from the wrong date |
| 8 | Lifecycle timestamps on receipts, orders, tasks, shipments | `F-074` | The first client's month-one SLA report cannot be produced, ever |
| 9 | Owner-scoped access grants + a single server-side resolver | `F-004` | The portal leaks another client's data through an export, a statistics tile or a dropdown |
| 10 | `(owner_id, sku)` item uniqueness and the alias table | `F-005`, `F-006` | The second client with a colliding SKU cannot be onboarded |
| 11 | `commingle_policy` + `dedicated_owner_id` on locations | `F-003` | Either bulk storage is uneconomic or a bonded/pharma client is unsellable |
| 12 | `wh_carrier_accounts.owner_id` nullable | `F-036` | "Ship on the client's account" — a standard contract clause — needs a schema change |
| 13 | Stock periods with a close | `F-085` | An approved 3PL invoice silently changes after billing |
| 14 | `stock_status_code` on the ledger, in the balance key | `F-068` | Damaged/quarantined client stock cannot be segregated without moving it, and recall cannot hold in place |
| 15 | Idempotency + append-only + reversal + sequence | `F-081`, `F-082` | The meter double-bills on a retry and the client's dispute cannot be resolved |

**Fifteen items. All schema. All in `warehouse-base` or `warehouse` v1. Together, well under a
month of work** — and each one is either free now or impossible later.

## 5.5 What we should deliberately NOT build

Recorded so a later reviewer, a later agent or a later salesperson does not "discover" these as
oversights. Each exists in at least one audited product and is placed, not dropped.

| # | Not building | Present in | Why not | Re-entry path |
|---|---|---|---|---|
| 1 | **An invoice, a tax engine or a receivable in `warehouse-3pl`** | none of the audited 3PL products do this either | It duplicates the accounting module and gives the customer two AR subledgers and double-counted turnover (`F-021`) | Never. The AR envelope is the interface, and the CSV fallback covers an install with no accounting module |
| 2 | **A refund or payment path anywhere in warehouse** | Shopify-adjacent tools | A refund is a receivable event with tax consequences (`F-053`) | Emit the disposition; the channel or accounting decides |
| 3 | **A consumer returns portal** | ShipHero, ShipBob, Shiprocket, Unicommerce | It belongs to the brand's storefront, not to the warehouse. Building it means owning consumer identity, consumer support and a public attack surface for a screen the brand wants to skin themselves | An API. `wh_rmas` accepts an externally-created RMA today |
| 4 | **An EPCIS repository with a query/subscription interface** | GS1 solution vendors | It is a compliance product in its own right. Our obligation is to *emit* correct events, which `F-071` does as a projection | Projection first. A repository only if a pharma customer's trading partner requires one, and then as an adapter |
| 5 | **Slotting optimisation and engineered labour standards in v1/v2** | Deposco, Made4net | Both need a year of our own data to be anything but a vendor's textbook. Shipping a bad optimiser destroys trust in the good reports next to it | `F-079` v3, on top of `wh_labour_tasks` from v2 |
| 6 | **Warehouse automation interfaces** (AS/RS, conveyor, sorter, robotics) | Made4net, Deposco, Logiwa `◐` | Each is a bespoke integration with a hardware vendor and a site commissioning project, not a feature | An adapter per vendor, posting through the port. The port already supports it: `actor_type = DEVICE` |
| 7 | **Retail-compliance / EDI B2B** (routing guides, ASN 856, chargebacks, GS1 pallet label specs per retailer) | Deposco, Made4net `◐` | It is a per-retailer specification treadmill, and no Indian customer needs it in v1 | `warehouse-adapter-edi`. The LPN, SSCC and shipment structures it needs are already v1 columns |
| 8 | **Demand forecasting and replenishment planning** | Fulfil, Deposco, Increff `◐` | It is a planning product. A WMS that guesses at forecasts is a worse forecaster than a spreadsheet and a worse WMS for the distraction | A separate module reading the ledger. `whb_movements` with `occurred_at` is exactly the history a forecaster needs — another dividend of `F-083` |
| 9 | **A second grid-preferences or filter mechanism for the client portal** | — | Not a competitor gap; a standing hazard. The portal is a permission surface over the existing grids (`F-008`). Two mechanisms is how 40 grid identifiers become 80 | — |
| 10 | **An expression language in allocation, rating, rate-shopping or SLA rules** | Infoplus (scripts), NetSuite-class ERPs | Four rule engines appear in this report — allocation (`F-028`), rate shopping (`F-037`), rating (`F-014`), negative stock (`F-090`) — and every one is specified as **bounded rows**. Stated as a set so the fifth does not introduce an interpreter because "the other four are limiting" | A new bounded operator, reviewed once. Never an interpreter |
| 11 | **Offline-writing desktop or thick-client operation** | some legacy WMS | The port's idempotency and batch endpoints (`F-092`) already give a scan gun offline **capture** with deferred sync, which is the actual requirement. Offline *authority* would falsify the append-only sequence and the hash chain simultaneously | None. The honest answer to offline authority is "not this product" |
| 12 | **Yard and trailer management** | Made4net, Deposco `◐`, CartonCloud `◐` | The dock door is ours (`F-080`); the yard beyond it is transport | The future logistics module. `wh_dock_appointments` is the join and it exists in v2 |

## 5.6 A closing note on migration ordering

One operational hazard, outside my lens but adjacent enough to be worth a line, because it has cost
this monorepo rebuild cycles before: `warehouse-3pl` sits at V930000–V939999 and `warehouse-base` must
sit **below** it, but Flyway in this codebase applies modules in an order that has previously surprised
people in both directions, and migrations are baked into the backend image at build time. Whoever
assigns the base and app ranges should confirm the applied order against a **fresh** install as well as
an upgrade, before the first `wh3pl_clients.owner_id → whb_owners.id` foreign key is written. That is
R1's territory, not mine; I note it only because the FK direction argued in §5.3 is the thing that
would fail.

---

## Appendix — how to read this report alongside the other lenses

- Anything in §2 marked **schema · v1** is a claim about the *first migration*, and it is the only
  part of this report with a deadline. If another lens disagrees with a v1 placement, resolve it
  before the migration is written, not after.
- Anything marked `?` is genuine uncertainty and must be verified by a human before it becomes a
  requirement. In prose they are concentrated in Indian tax and regulatory detail
  (`F-025`, `F-061`, `F-073`); in the §1 tables they mark competitor cells I could not score with
  confidence. Do not cite a `?` cell as evidence of anything.
- Nothing in this report is a conformance finding, because there is no design set to conform to. When
  one exists, this report becomes the input to a conformance pass, and the `F-` ids should survive
  into it so a later reviewer can tell what was considered and consciously placed rather than missed.
