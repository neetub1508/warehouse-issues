# Competitor benchmark — where the Classic Warehouse product stands against the market

> **Authority.** [`DECISIONS.md`](DECISIONS.md) wins over this document on every question of module
> names, Flyway bands, table prefixes, invariants and the version ladder. This document does not
> re-decide anything; it reads the five audits against that spine and turns them into one picture a
> product owner and a salesperson can both use.
>
> **This is a synthesis, not a re-run.** Nothing here was scored fresh. Every competitor cell is
> carried from `reviews/R2`–`R5` (with capability material from `R6` and `R7`), and every one that the
> source marked uncertain is carried as `?`. No cell was upgraded from `?` to a confident mark.
>
> **Date:** 2026-09-01 · **Sources:** `reviews/R1`–`R7`, 11,750 lines, **575 findings**
> (`C-`, `T-`, `E-`, `F-`, `S-`, `P-`, `G-`). Counts and their commands are in [§10](#10--counts-and-how-they-were-computed).

---

## §0 · How to read this document

### 0.1 The legend

| Mark | Means |
|---|---|
| `●` | shipped and mature in the typical product of that segment |
| `◐` | partial — present but tiered, add-on, hard-coded, single-variant, or bolted on via a partner product |
| `○` | absent |
| `?` | the source audit could not verify it. **Treat as unknown, not as absent. Do not cite this cell externally.** |
| `–` | **no audit scored this segment for this capability.** Unknown for a different reason: nobody looked. Several of these are rows where the whole market is silent, which is itself a finding |

`–` is an addition to the audits' own legend. It exists so that "we do not know" and "we know it is
absent" never share a symbol, which is how a benchmark quietly becomes marketing.

### 0.2 The segment columns

Each of the three audits scored against a different product set with a different column layout. This
document collapses them to one representative column per segment. The mark in a segment column is the
**modal** score across that segment's products in the source audit, with named exceptions in the row
note where the spread is wide.

| Col | Segment | Products behind it | Scored by |
|---|---|---|---|
| **T1** | Tier-1 / enterprise WMS | Manhattan · Blue Yonder · SAP EWM · Oracle WMS Cloud · Körber · Infor (+ Softeon, Tecsys in prose) | R2 |
| **ERP** | ERP-embedded inventory | NetSuite (+WMS) · D365 SCM (+Advanced WMS) · SAP B1 · Odoo 18 · ERPNext · Acumatica · Sage · Epicor | R3 |
| **SMB** | Mid-market / SMB standalone | Cin7 Core · Unleashed · Finale · Fishbowl · Zoho Inventory · Katana · inFlow · Sortly · SkuVault · Ordoro | R3 |
| **IN** | India market | Tally Prime · Busy · Marg · Vyapar · GoFrugal · Logic; Increff · Unicommerce · EasyEcom · Vinculum · WareIQ · Shiprocket Fulfilment | R3 + R4 |
| **DMS** | Automotive dealer parts | CDK · Reynolds · Tekion · Dealertrack · Autosoft · Karmak · Autologue | R3 |
| **3PL** | 3PL / eCommerce fulfilment | Extensiv · Logiwa · Da Vinci · Camelot · Deposco · Made4net · Infoplus · ShipHero · CartonCloud · Mintsoft · Peoplevox · ShipBob · Shipwire · Fulfil.io · Veeqo · ShipStation/ShipEngine · Amazon FBA/MCF · Flexport | R4 |

**68 named products** across the six columns, enumerated above. That enumeration *is* the count —
see [§10](#10--counts-and-how-they-were-computed).

### 0.3 Our column

Never a bare tick. Always `v1` · `v1.1` · `v2` · `v3` · `NO`, per the `DECISIONS.md` §5 ladder:

| Version | Phases | What lands |
|---|---|---|
| **v1** | P0 ledger · P1 masters & inbound · P2 outbound, counting, valuation, reports | the stock ledger and inventory control, plus the dealer-parts and services adapters |
| **v1.1** | P3 execution & mobile | RF/handheld, tasks, waves, batch/cluster/zone picking, packing, labels, dock appointments, van stock, field-service + assets adapters |
| **v2** | P4 India & statutory · P5 3PL, channels & reverse logistics | `warehouse-india`, `warehouse-3pl`, channel/carrier intake, RMA & reverse logistics, NDR/RTO/COD |
| **v3** | P6 optimisation, planning & the logistics seam | slotting, replenishment optimisation, labour standards reporting, ABC/XYZ, planning, EPCIS, automation interfaces, the `logistics` module |

Where a row says `v1 schema / v2 feature`, the column exists in the first migration and the screen
ships later. Roughly a third of our v1 is of this shape, and that is deliberate: an append-only ledger
cannot be retro-fitted with a dimension it never recorded (`DECISIONS.md` D-5, R5's 28-row
*CANNOT BE ADDED LATER* table, R4 §5.4's 15 base concessions).

### 0.4 Where the audits disagree with each other or with the ladder

Sixteen such disagreements were found. They are **not** hidden inside the matrix — each is flagged in
place with a `‡` and all sixteen are consolidated in [§9](#9--where-the-audits-disagree). Three of
them are consequential enough that a product owner should decide before the first migration.

### 0.5 What the audits' verdict columns are, and are not

R2, R3 and R4 each wrote their own "our v1 verdict" column **before `DECISIONS.md` existed**. Those
columns are proposals from a lens, not commitments. Two things follow, and they matter when reading
the source documents directly:

- Every table name in those columns uses a **stale prefix** — R2 proposed `wb_`/`w3_`, R3 used `wh_`
  for the base, R4 used `whb_`/`wh3pl_`. `DECISIONS.md` D-3 fixed `whb_` (base) · `wh_` (application) ·
  `wh3_` (3PL) · `whin_` (India) · `whad_`/`whas_`/`whaf_`/`whaa_` (adapters).
- Every Flyway band in those columns is **wrong**. All five lenses wrote `V900000+`; D-2 moved the
  allocation to **V500000–V549999** because `V900000`–`V919999` is occupied by 135 dealer OEM seed
  files and 434 platform per-client files, and `FlywayConfiguration.java:296-327` renumbers and then
  *deletes* colliding history rows rather than failing loudly (R1 `C-001`…`C-003`).

This document uses D-3 prefixes and the D-2 bands throughout.

---

## §1 · The market map

### 1.1 The segments, and who owns each

| # | Segment | Who owns it today | Do we compete? | From which version |
|---|---|---|---|---|
| 1 | **Vehicle-dealership parts department** (multi-branch, India) | CDK · Reynolds · Tekion · Karmak · Autologue; in India the OEM's own DMS, Marg, or a spreadsheet | **YES — this is the target** | v1 |
| 2 | **Workshop / service parts issue** | *nothing* — in this suite `service_entries.parts_used` is free `TEXT` (`services/…/V40095`, R5 Fact 2) | **YES — greenfield** | v1 (`warehouse-adapter-services`) |
| 3 | **Field-service van stock & asset spares** | Tecsys point-of-use is the closest analogue; `assets/` and `field-service/` have no parts tables at all (R1 `C-034`) | **YES** | v1.1 (adapters) |
| 4 | **Auto-parts distribution / wholesale (India)** | Marg · Busy · GoFrugal · Tally | **YES, partially** — we lose on schemes, van sales, price | v1, competitive at v2 |
| 5 | **General SME multi-godown inventory (India)** | Tally Prime · Busy · Marg · Vyapar | **YES on operations, never on the GL** | v1 |
| 6 | **Contract logistics / 3PL** | Extensiv · Camelot · Infoplus · Made4net · Logiwa; Increff in India | **YES** — one v1 column decides it (R5 §6, `S-064`) | v2 (`warehouse-3pl`) |
| 7 | **D2C / marketplace eCommerce fulfilment (India)** | Unicommerce · EasyEcom · Vinculum · Increff · WareIQ · Shiprocket Fulfilment | **YES, late and not on connector breadth** | v2 |
| 8 | **Bonded / MOOWR / SEZ / FTWZ warehousing** | SAP GTS as a separate product; nobody in the Indian generic set | **YES — an unusual opening** | v1 column, v2 feature (`S-044`) |
| 9 | **Food & FMCG distribution** | Marg · Busy · ERP-embedded | **YES with additions** (`S-038`, `S-039`, `S-040`) | v1 columns, v1.1/v2 features |
| 10 | **Electronics / high-value serialised** | ERP-embedded; SkuVault; Increff | **YES with additions** (`S-057`, `S-065`) | v1, v1.1 |
| 11 | **Chemicals & construction bulk** | ERP-embedded; specialist | **YES with additions**, one of which is v1 schema (catch weight, `S-013`) | v1 schema, v2 |
| 12 | **Pharmaceutical distribution** | Marg (India) · Da Vinci (US) · Tecsys | **CANNOT SERVE until three v1 rows land** (`S-004`, `S-007`, `S-008`), then v2 — **and R2 refusal #13 declines the vertical outright** ‡ | contested |
| 13 | **Cold chain** | ERP-embedded; specialist | **CANNOT SERVE** — v1 cost is small (bind readings to zone/location/LPN), the excursion workflow is v2 (`S-041`) | v2 |
| 14 | **Apparel / footwear** | ERP-embedded; Increff; Unicommerce | **CANNOT SERVE** without a v1 style×size×colour schema decision (`S-056`) — **the largest addressable segment we are currently declining** ‡ | undecided |

### 1.2 Segments we are explicitly **not** entering

Blunt, because an unstated absence reads as an oversight:

- **Tier-1 enterprise WMS deals.** Manhattan, Blue Yonder and SAP EWM buyers want waving, engineered
  labour standards, slotting solvers and integrated planning. We should not be in the room (R2 §5.4).
- **Transportation management.** Manhattan TMS, Blue Yonder TMS, SAP TM and Oracle OTM are separate
  products *at their own vendors*. Refusal #1 (§7).
- **Distributed order management / order sourcing.** That is an OMS; it decides *where* to fulfil
  from. Refusal #2.
- **Multi-tenant SaaS economics.** Classic is one database per customer
  (`grep -ril "tenant" platform/backend/src/main/java` → 0 files, R5 Fact 3; `DECISIONS.md` OD-3).
  `owner_id` gives multi-*client*, which a 3PL needs; it is not the same thing and must never be
  conflated in a sales conversation. Refusal #12.
- **US retail-compliance / EDI B2B** (routing guides, ASN 856 per retailer, chargebacks). A
  per-retailer specification treadmill. Refusal #20.
- **UDI / medical device and pharma serialisation regimes.** Each is a certification programme, not a
  feature. Refusal #13 — *contested by R5*, see ‡ above.
- **International trade compliance / customs documentation / FTZ.** Refusal #14 — *partially
  overruled*: `duty_status` is a v1 column per D-5 and `S-044`, and bonded/MOOWR ships in v2, so the
  refusal now covers export/customs documentation only.

### 1.3 Where we actually intend to compete, in one line

**The Softeon/Tecsys shape, not the Manhattan shape** (R2 §5.1): narrow scope, completely finished,
deployable in weeks, sold to a buyer who has already decided they cannot afford tier 1 — and, in our
case, to a buyer whose *parts catalogue* and *Indian statutory shape* no generic WMS models at all.

---

## §2 · The consolidated capability matrix

18 areas. Every cell is carried from `R2`–`R5`; the source finding id is in the row note where a claim
depends on one. `‡` marks a row where the audits disagree with each other or with the `DECISIONS.md`
ladder — all sixteen are consolidated in [§9](#9--where-the-audits-disagree).

### 2.1 Item master & identity

| Capability | T1 | ERP | SMB | IN | DMS | 3PL | Ours · version |
|---|---|---|---|---|---|---|---|
| Item master as a first-class entity in the stock product | ● (EWM ◐ — mirrored from S/4) | ● | ● | ● | ● | ● | **v1** `whb_items` |
| Item **type** vocabulary (stock · non-stock · service · kit · core · consumable) | ● | ● | ◐ (Sortly ○) | ● | ● | – | **v1** — a catalogue table, no CHECK (D-10) |
| Item status lifecycle as **four independent facts**, not one enum | ● | ● | ◐ | ◐ | ● | – | **v1** (`T-020`) |
| Per-owner item record; `(owner_id, sku)` uniqueness | ● (EWM ◐) | ◐ | ◐ | ◐ | ? | ● | **v1** (`F-005`) — a global unique SKU is a one-way door |
| Multiple barcodes per item, each with **its own UoM and pack quantity** | ● | ● | ● | ● | ● | ● | **v1** (`T-022`, `S-001`) — without `pack_quantity` a case scan books one each |
| GS1 AI parsing on scan (01 · 10 · 17 · 21 · 00) | ● | ● | ◐ | ◐ | ○ | ◐ | **v1** scan-resolution service (`S-002`) / **v1.1** RF surfaces ‡ |
| Manufacturer / supplier / customer part cross-reference | ● (customer: EWM ◐) | ● | ◐ | ● | ● | ● | **v1** `whb_item_identifiers` ‡ |
| Item images, documents, spec attributes | ◐ | ● | ● | ◐ | ● | – | **v1.1** — platform document storage |
| Variants / style × size × colour matrix | ◐ (EWM ○) | ● | ● | ● (Busy parameterised) | ◐ | – | **undecided** ‡ — `S-056` says v1 schema; R2/R3 say v2 |
| Custom fields on core objects without a schema change | ● | ● | ● | ◐ | ? | ● | **NO** as a JSONB bag (refusal #11) · **v3** as typed attribute tables (`T-094`) |

### 2.2 Units of measure & quantity semantics

| Capability | T1 | ERP | SMB | IN | DMS | 3PL | Ours · version |
|---|---|---|---|---|---|---|---|
| UoM master with a dimension class (count · weight · volume · length) | ● | ● | ◐ | ● | ● | – | **v1** |
| Conversion factor **per item**, not global on the UoM | ● | ● | ◐ | ● | ● | – | **v1** (`T-011`, `E-009`) — the `accessories` precedent gets this wrong (`Uom.java:64-73`) |
| Transact in any UoM, persist in base UoM, **factor frozen on the line** | ● | ● | ● | ● | ◐ | ● | **v1** (L-7, `S-012`, `F-093`) |
| UoM change blocked once movements exist | ● | ● | ● | ● | ● | – | **v1** DB trigger |
| Break-case / repack as a two-sided ledger event, never an UPDATE | ● | ● | ◐ | ● | ○ | ● | **v1.1** ‡ (R3 says v2) |
| **Catch weight** — a second, independent quantity on every record | ● (BY `◐ ?`, Oracle `◐ ?`, Körber `● ?`, Infor `● ?`) | ◐ (D365 ●) | ◐ | ◐ | ○ | – | **v1 schema** (`S-013`, `T-012`) / **v2 feature** ‡ |
| UN/CEFACT Rec-20 + GST UQC code on the UoM master | – | ◐ | ○ | ● | ● | – | **v1** (`S-011`) — two columns that make every compliance payload derivable |
| Dual-UoM reporting (stock in cases *and* kg) | ● | ● | ◐ | ◐ | ◐ | – | **v1.1** |
| Decimal quantity with declared precision | ● | ● | ● | ● | ◐ | ● | **v1** — precision set by OD-7 |

### 2.3 Catalogue depth — supersession, interchange, fitment, cores

> This is the table where the DMS column is `●` and every other column is `○` or `◐`. That gap is the
> product (R3 §4).

| Capability | T1 | ERP | SMB | IN | DMS | 3PL | Ours · version |
|---|---|---|---|---|---|---|---|
| **Supersession chain A→B→C, resolved forward at every lookup** | ○ *(all six)* | ◐ (Epicor ●) | ○ | ◐ (Marg `?`) | ● | ○ | **v1** ‡ (`E-055`; R2 `T-021` placed it v1.1) |
| Backward traceability — "what did this part replace" | ○ | ◐ | ○ | ◐ | ● | ○ | **v1** (`E-055`) |
| Supersession that **merges stock and demand history** | ○ | ○ | ○ | ○ | ● | ○ | **v1.1** (`E-056`) |
| Interchange / alternate / non-OEM equivalent, bidirectional | ◐ | ◐ | ○ | ◐ | ● | ○ | **v1.1** (`E-057`) |
| **Vehicle fitment** — make × model × variant × year × engine × position | ○ *(all six)* | ○ | ○ | ◐ | ● | ○ | **v1** in `warehouse-adapter-dealer` (`E-058`, `T-023`) |
| Core / exchange part linked to its serviceable parent | ○ | ○ | ○ | ○ | ● | ○ | **v1.1** (`E-063`) |
| Kit / BOM / service-package definition | ◐ (Körber ●) | ● | ● | ● | ● | ● | **v1.1** (`E-044`, `F-057`) |
| Industry catalogue-standard ingest (ACES/PIES; `?` for India) | – | ◐ (Epicor ●) | ○ | ○ | ● | – | **v3** (`E-059`) |

### 2.4 Lot / batch, serial, LPN, traceability

| Capability | T1 | ERP | SMB | IN | DMS | 3PL | Ours · version |
|---|---|---|---|---|---|---|---|
| **Lot as a first-class entity**, not a string on the balance | ● | ● | ● | ● | ◐ | ● | **v1** `whb_lots` (`T-005`, `E-014`) |
| Lot attributes: mfg date, expiry, **best-before ≠ use-by**, MRP, supplier lot, country of origin | ● | ● | ◐ | ● | ◐ | ●/◐ | **v1 columns** (`S-033`, `S-038`, `F-063`) |
| **Serial as a first-class entity**, unique on `(item_id, serial_number)` not globally | ● | ● | ● | ◐ | ◐ | ● | **v1** (`T-006`, `S-018`) |
| **LPN / handling unit as a first-class object** | ● (Oracle: *the* core object) | ● (D365 ●, NetSuite ●) | ◐ (SkuVault ●) | ◐ (Increff ●) | ○ | ● | **v1 column** (`T-007`, `F-064`) / v1.1 handling |
| Nested LPN (pallet → cartons → items) | ● | ● | ◐ | ◐ | ○ | ● (EXT ◐, UNI ○) | **v2** — `parent_lpn_id` in v1 |
| **FEFO allocation** | ● | ● (Odoo ●) | ● (Cin7 ●) | ● (Marg ●) | ○ | ● | **v1** ‡ (R3 `E-017`, R4 `F-067`; R2 placed it v1.1) |
| Minimum remaining shelf life on dispatch, per customer | ● | ? | ? | ? | ○ | ● | **v1.1** (`S-039`, `F-067`) — FEFO alone gets stock rejected at the retailer's gate |
| Forward + backward trace (lot → shipments; serial → supplier lot) | ● | ● (Odoo ●) | ◐ | ◐ | ○ | ◐/● | **v1.1** — a query over the ledger, *if* the ledger is double-sided |
| Transformation genealogy through kit / repack / decant | ◐ (Körber `◐ ?`, Infor `◐ ?`) | ● | ◐ | ◐ | ○ | ◐ | **v1 schema** (`S-008`) / **v2 feature** ‡ |
| Mass hold / recall by lot, supplier, date range, with task generation | ● | ● | ◐ | ◐ | ○ | ● | **v2** ‡ (`S-040` says v1.1) |
| GS1 SSCC generation | ● | ◐ | ◐ | ◐ | ○ | ●/◐ | **v2** ‡ (`S-005` says v1.1) |
| EPCIS event capture / export | ◐ ? | ◐ | ○ | ○ | ○ | ◐ (DAV ◐, M4N ◐, rest ○) | **v3 projection** (`S-009`, `F-071`) · repository refused (#19) |

### 2.5 Facility & location model

| Capability | T1 | ERP | SMB | IN | DMS | 3PL | Ours · version |
|---|---|---|---|---|---|---|---|
| Multiple sites / warehouses in one instance | ● | ● | ● | ● | ● | ● | **v1** `whb_sites` |
| Location **hierarchy** site → zone → aisle → rack → level → bin | ● | ● (Odoo ●, D365 ●) | ◐ (Cin7 ●) | ◐ (Increff ●) | ◐ | ● | **v1** (`T-008`, `E-020`) |
| Location **type** vocabulary driving behaviour | ● | ● | ◐ | ○ | ◐ | ● | **v1** catalogue, no CHECK (D-10) |
| **Virtual locations** — in-transit · supplier · customer · job-worker · scrap · adjustment · opening | ● | ● (Odoo ●) | ○ | ○ | ○ | ◐ | **v1 — non-negotiable** (L-1, `T-009`, `S-069`). Without them the ledger cannot net to zero |
| Warehouse bound to a legal entity + tax registration + state code | ◐ | ◐ (localised) | ○ | ● | ● | ◐ | **v1** (`E-048`, `S-022`) |
| **Commingle policy per location** + dedicated owner | ● | ◐ | ○ | ○ | ○ | ● (IFP ◐, SHH ○) | **v1 column** (`F-003`) |
| Capacity constraints: weight · volume · height · LPN count · unit count | ● | ● | ◐ | ◐ | ○ | ● | **v1 columns** / v1.1 enforcement |
| Mass location generator (aisle × rack × level) | ● | ? | ? | ? | ? | – | **v1** (`T-024`) — nobody keys 4,000 bins by hand |
| **Van / technician stock as a location owned by a person** | ○ *(all six)* | ○ | ○ | ○ | ◐ ? | ○ | **v1.1** adapters (`S-060`, `T-080`) — Tecsys point-of-use is the closest analogue |
| **`duty_status` in the position unique key** (domestic · bonded · MOOWR · SEZ · FTWZ) | ◐ (SAP GTS, a separate product) | ◐ | ○ | ◐ | ○ | ○ | **v1 column** / v2 feature (`S-044`, D-5) |
| Multi-timezone: each site posts in its own local day | ● | ● | ◐ | ◐ | ? | ● | **v1** (`T-018`) |

### 2.6 Inbound — PO, ASN, receipt, QC, putaway

| Capability | T1 | ERP | SMB | IN | DMS | 3PL | Ours · version |
|---|---|---|---|---|---|---|---|
| Receipt against a purchase order | ● | ● | ● | ● | ● | ● | **v1** |
| Goods receipt note distinct from the supplier invoice | ● | ● | ● | ● | ● | ● | **v1** (`E-027`) |
| **ASN** as a document; EDI 856 inbound | ● | ● | ◐ (SkuVault ●) | ◐ | ● (OEM ASN ●) | ● | **v1.1** ASN ‡ · **v3** EDI (`S-015` rates ASN+SSCC the highest-value single integration) |
| **Blind receipt** (no expectation document) | ● | ● | ◐ | ○ | ● | ● | **v1** ‡ (R3 says v2) — the 3PL and returns default |
| Multi-PO / multi-ASN **receiving session** ("a truck is not a purchase order") | – | – | – | – | – | – | **v1.1** (`P-021`) — no sibling lens mentions it; prior-art origin |
| Receipt lands in a **non-available status** (damaged / QC hold), not a "QC bin" | ● | ● | ◐ | ◐ | ◐ | ● | **v1** (`T-035`) — depends entirely on the status master |
| Rule-driven directed putaway | ● | ● | ◐ (Cin7 ●) | ◐ | ○ | ● | **v1.1** ‡ (R3 says v2) |
| QC inspection with sampling plan, **header/line grain** | ◐ (EWM ● QIE) | ● | ◐ | ◐ | ◐ | ◐ | **v2** (`E-029`) + the header/line correction from `P-029` |
| Over-receipt / short-receipt tolerance, per item and supplier | ● | ● | ● | ● | ● | ● | **v1.1** (`T-036`) |
| Cross-dock — opportunistic, then planned | ● | ◐ | ◐ | ◐ | ○ | ● ? | **v2** / **v3** |
| Receipt reversal by reversing rows, never a delete | ● | ● | ◐ | ● | ● | ● | **v1** (L-2, L-3, `T-017`) |
| Three-way match PO ↔ GRN ↔ bill, variance surfaced | – (ERP-side) | ● | ◐ | ● | ● | ○ | **v1.1**, value leg in `accounting` (`E-028`, structure from `P-039`) |
| Landed-cost components captured at receipt | ◐ (ERP) | ● | ● (Unleashed ●) | ● (Marg ●) | ◐ | ○ | **v1** value-only movement type (`F-088`) / **v1.1** apportionment / **v2** retrospective |

### 2.7 Inventory control & the stock ledger — the core

> Nothing else in this document matters if this table is wrong. Every row here is a `DECISIONS.md`
> invariant (L-1…L-14) or a v1 schema commitment.

| Capability | T1 | ERP | SMB | IN | DMS | 3PL | Ours · version |
|---|---|---|---|---|---|---|---|
| **Append-only, immutable ledger; correction only by reversal** | ● | ● | ◐ | ● | ● | ● | **v1** (D-4, L-2, L-3, `S-054`, `F-082`) |
| **Double-sided movement that nets to zero over locations** | ● | ● (Odoo `stock.move`) | ○ | ○ | ○ | ◐ | **v1** (D-4, L-1, `T-001`, `S-069`). The `accessories` precedent writes one row with `from`+`to` and some paths write no movement at all (R1 `C-021`) |
| Position keyed by the **full nine-tuple** (company · owner · item · location · lot · serial · LPN · stock status · duty status) | ● *(seven of nine)* | ◐ | ○ | ○ | ○ | ◐ | **v1** (L-5). **No audited product carries all nine** — `duty_status` is ours |
| Reconstruct on-hand at any past instant purely from the ledger | ● | ● | ◐ | ● (Tally) | ● | ● | **v1**, declared as a testable invariant with a nightly drift alarm (L-4, `T-019`) |
| **Inventory status master** with `is_allocatable` / `is_on_hand` / `is_valued` flags | ● | ● | ● | ● | ● | ● | **v1** catalogue (`T-004`, `F-068`) — never an enum, never a location |
| **`owner_id` NOT NULL** on every ledger line, balance, lot, serial, LPN, reservation | ● (EWM ◐) | ◐ (Odoo ●) | ◐ | ◐ (Increff ●) | ● (OEM consignment `?`) | ● | **v1, in every install** (D-5, `T-002`, `F-001`, `S-064`). The single most expensive column to add late |
| **Allocation as an open-item ledger** with a holder quad and an expiry, not a counter | ● | ● soft / ◐ hard | ◐ | ○ | ◐ | ● | **v1** (L-10, `T-014`, `F-028`) |
| Negative-stock policy per site × item — block · warn · allow | ● | ● | ● | ● | ● | ◐ | **v1**, default block (L-6, `T-025`, `S-076`, `F-090`) |
| Inter-site transfer with **in-transit as a real location** (three legs) | ● | ● | ◐ (Cin7 ●) | ◐ | ● | ◐ | **v1** ‡ (`E-032`, `S-069`; R2 placed the three-leg document v1.1) |
| Adjustment with a **mandatory reason code from a closed, tax-mapped catalogue** | ● | ● | ● | ◐ | ● | ● | **v1** (`T-010`, `S-028`, `E-033`) — free text for a year cannot be reclassified |
| **Three timestamps** — occurred · recorded · posting date | ◐ (EWM ● posting ≠ entry) | ◐ | ○ | ◐ | ? | ◐ (CAM ●, EXT ●) | **v1** (L-13, `S-007`, `F-083`, `T-018`) |
| Idempotent ingestion with a **producer-supplied** key | ● / ◐ | ● | ◐ | ○ | ◐ | ◐ (SST ●, FBA ●) | **v1** (L-9, `T-091`, `F-081`) |
| Stock periods with a close, independent of the accounting close | ◐ (ERP-side) | ● | ○ | ◐ | ◐ | ◐ | **v1** (L-8, `E-046`, `F-085`, `S-090`) |
| **`ledger_seq` — a monotonic total order** | – | – | – | – | – | – | **v1** (R5 irreversibility row 21) — two movements with one timestamp make "balance as at" ambiguous |
| **Title transfer with no physical movement** (`OWNER_CHANGE`) | ● | ● | ◐ | ◐ | ◐ | ◐ (LGW ○, SHH ○) | **v1** movement type (L-11, `F-009`) / v1.1 screen |
| **A discrepancy queue for the physical move the system rejected** | – | – | – | – | – | – | **v1** (`S-089`). R5 ranks this ship-blocker **#3**: without it operators work around the system within a week and every number after that is fiction |

### 2.8 Counting

| Capability | T1 | ERP | SMB | IN | DMS | 3PL | Ours · version |
|---|---|---|---|---|---|---|---|
| Full physical count with a freeze / snapshot of book quantity | ● | ● | ● | ● | ● | ● | **v1** (`S-091`, `E-038`) |
| Cycle count by zone / location range / aisle sweep | ● | ● | ◐ (SkuVault ●) | ◐ | ● | ● | **v1** |
| Cycle count driven by ABC / count class on a schedule | ● | ● | ◐ | ◐ | ● | ● | **v1.1** |
| Blind count (book quantity hidden from the counter) | ● | ● | ● | ◐ | ● | ● | **v1** — a flag on the header, cheap now (`T-089`) |
| **`count_snapshot_quantity` on the count line** | – | – | – | – | – | – | **v1** (`S-091`). Variance against a live quantity is not reproducible |
| Variance tolerance by qty % **and by value**, approval before posting | ● | ● | ◐ | ◐ | ● | ● | **v1** approval (`T-090`, `E-038`) / v1.1 tolerance table |
| A count **proposes** an adjustment; it never writes on-hand directly | ● | ● | ◐ | ● | ● | ● | **v1** (`T-089`) |
| Zero-stock / empty-bin verification on last pick | ● (EWM explicit) | ? | ? | ? | ? | – | **v1.1** — the highest-yield count type per hour, and nearly free |
| Count-accuracy KPI by counter, zone, item class | ● | ◐ | ? | ? | ● | ● | **v2** (`F-076`) |

### 2.9 Outbound — demand, allocation, waves, picking

| Capability | T1 | ERP | SMB | IN | DMS | 3PL | Ours · version |
|---|---|---|---|---|---|---|---|
| **One demand model for all demand types** (sales · transfer · work order · replen · VAS) | ● | ● | ◐ | ◐ | ● | ● | **v1** (`T-042`) — not one table per source |
| Order → allocate → pick → despatch as distinct states | ● | ● | ● | ◐ | ● | ● | **v1** ‡ (the v1 exit criterion requires it; R3 placed it v1.1) |
| **Direct issue with no order** — counter sale, workshop issue | ○ | ● | ◐ | ● | ● | ○ | **v1** (`E-064`, `E-065`) |
| **Reservation for a workshop job card that is not yet an order** | ○ | ◐ | ○ | ○ | ● | ○ | **v1** (`E-065`) |
| Allocation strategy as configured **data**, not an if-statement | ● | ● | ◐ | ◐ | ◐ | ● | **v1** FIFO/FEFO as a column (`T-043`, `F-028`) |
| **Wave planning** as a real object | ● | ● (NetSuite WMS ●, D365 ●) | ◐ (SkuVault ●) | ◐ (Increff ●) | ◐ | ● | **v1.1** ‡ (R3 and R4 both said v2) |
| Batch / cluster / zone picking, pick-and-pass | ● | ● | ◐ | ◐ | ◐ | ● | **v1.1** batch · **v2** cluster/zone |
| Waveless / continuous release (Manhattan "Order Streaming") | ● *Manhattan only*; others ◐ ? | ◐ | ○ | ◐ | ○ | ◐ | **v3** — do not chase this |
| Short-pick handling: re-allocate, emergency replen, or short the line | ● | ◐ | ◐ | ◐ | ◐ | ● | **v1.1** |
| **Order holds as records with a release audit**, not a status | ● | ◐ | ◐ | ● | ? | ● | **v1** (`F-033`) |
| Split shipment — one order, many shipments | ● | ● | ● | ● | ● | ● | **v1 cardinality** (`F-030`) — a one-way door |
| Order edit after release with automatic de-allocation | ● | ◐ | ◐ | ◐ | ? | ◐ | **v1.1** ‡ (`F-034`; R2 said v2) — the most-requested and least-designed feature in every WMS |
| Cancel after allocation → deterministic de-allocation | ● | ● | ◐ | ◐ | ● | ● | **v1** — impossible with a counter (`T-014`) |
| Order split / sourcing across sites (DOM) | ● (Manhattan/BY DOM) | ◐ | ○ | ○ | ○ | ◐ | **NO** — refusal #2, that is an OMS |
| Pick confirmation validates the scan (location · item · lot · serial · qty) | ● | ● | ● | ◐ | ● | ● | **v1.1** (`T-050`) |

### 2.10 Packing, shipping, carriers — including the Indian carrier surface

| Capability | T1 | ERP | SMB | IN | DMS | 3PL | Ours · version |
|---|---|---|---|---|---|---|---|
| Pack station with scan-verify against the order | ● | ● | ● | ◐ | ○ | ● | **v1.1** |
| **Pack session with sealed cartons** / cartonisation | ● | ● | ◐ | ◐ | ○ | ● (SHH ●, LGW ●) | **v1.1** pack session (`P-037`) / **v2** cartonisation algorithm (`F-038`) |
| Packing list / delivery challan print | ● | ● | ● | ● | ● | ● | **v1** doc-type mechanism / **v2** India challan pack ‡ |
| **Ship confirm → inventory relief as a ledger event** | ● | ● | ● | ● | ● | ● | **v1** |
| Carrier / service / account master, account owned by us **or** by the client | ◐ (their TMS ●) | ◐ | ● (Ordoro ●) | ● (Unicommerce ●) | ○ | ● | **v1 column** `owner_id` (`F-036`) / v2 feature |
| **Label generation, storage and void** | ● | ● | ● | ● | ● | ● | **v1.1** (`F-039`, `S-087`). `grep -rli "zpl\|escpos\|dymo"` across all Java/TS → **0**. R5 ranks this ship-blocker **#2** |
| Rate shopping with the quote persisted | ◐ (their TMS ●) | ◐ | ● | ● | ○ | ● (FBA ○) | **v2** (`F-037`) — freight procurement itself is refusal #1 |
| Manifest / EOD close-out / handover document | ● | ◐ | ● | ● | ○ | ● | **v2** (`F-040`) |
| Pickup scheduling as a request separate from the label | ? | ? | ● | ● | ○ | ◐ | **v2** — Indian carriers require it; US carriers mostly do not (`F-040`) |
| **AWB / waybill pool** — pre-fetched number blocks | ○ | ○ | ○ | ● | ○ | ○ | **v2** (`F-042`). **Without it you cannot label an Indian shipment at all** |
| **Pincode serviceability** — prepaid / COD / pickup / ODA per carrier | ○ | ○ | ○ | ● | ○ | ○ | **v2** (`F-041`) — no global product has it |
| **NDR** with a merchant response SLA and an action API | ○ | ○ | ○ | ● | ○ | ○ | **v2** (`F-044`) — India's second-largest daily workflow |
| **COD** carried / collected / remitted, with UTR reconciliation | ○ | ○ | ○ | ● | ○ | ◐ | **v2** (`F-045`) |
| **RTO as an inbound stock stream** matched by AWB | ○ | ○ | ○ | ● | ○ | ○ (MIN ◐, FBA ◐) | **v2** (`F-046`) — 15–30% of Indian COD volume |
| Carrier weight / dimension discrepancy dispute with evidence | ○ | ○ | ○ | ● | ○ | ○ (FBA ◐) | **v2** (`F-047`) |
| **e-Way bill trigger on transfer / outbound** | ○ (EWM ◐ localisation) | ○ | ○ | ● | ● | ○ (UNI ●) | **v1 data columns** / **v2** gateway (`S-024`, `E-051`, `T-083`) |
| International customs documentation | ◐ (SAP GTS ●) | ● | ● | ◐ | ○ | ●/◐ | **NO** — refusal #14 (bonded/MOOWR carved back in, see §7) |
| Tracking events stored normalised **and** raw, webhook-idempotent | ◐ | ◐ | ● | ● | ○ | ● | **v2** (`F-043`) |

### 2.11 Replenishment, stocking policy and the planning boundary

| Capability | T1 | ERP | SMB | IN | DMS | 3PL | Ours · version |
|---|---|---|---|---|---|---|---|
| Min / max / reorder point per item × warehouse | ◐ (EWM ○ — ERP-side) | ● | ● | ● | ● | ◐ | **v1** (`E-013`, `E-040`) |
| Min / max per item × **location** | ● | ● | ◐ | ◐ | ● | ● | **v1.1** |
| Pick-face replenishment — min/max, demand-driven, top-off, break-case, emergency | ● | ◐ | ◐ | ◐ | ○ | ◐ | **v1.1** min/max · **v2** the rest |
| Replenishment run producing an **order document**, not a grid to retype | ○ (suggestions only) | ● | ● | ◐ | ● | ◐ | **v1.1** (`E-040`) |
| **Computed best stocking level** from demand hits, with phase-in / phase-out | ◐ | ● (NetSuite ●, D365 ●) | ◐ (Finale ●) | ○ | ● | ○ | **v2** (`E-066`) — **the row that decides the DMS fight** |
| **Lost-sale capture** | ○ | ○ | ○ | ○ | ● | ○ | **v1.1** (`E-067`, `S-063`) — upstream of the entire KPI set |
| Reason codes that exclude adjustments / warranty from demand history | – | – | – | – | – | – | **v1 column** `affects_demand_history` (`E-033`) — without it a write-off inflates the reorder point |
| Suggested transfer from a sister branch before buying | ◐ | ● | ◐ | ◐ | ● | ◐ | **v2** (`E-041`) |
| Days-supply / months-supply as maintained columns | ◐ | ● | ◐ | ○ | ● | ◐ | **v2** (`E-077`) |
| **ATP / availability served to other modules** | ◐ (Oracle GOP ●, BY ●) | ● | ◐ | ○ | ◐ | ● | **v1.1** read API ‡ — our own verticals need it immediately (`T-085`) |
| Demand forecasting, MEO, seasonal profiles | ● *only as a separate product* | ● | ◐ | ○ | ◐ | ◐ | **NO in warehouse** · **v3** planning/logistics module (refusal #8) |
| Service-parts planning — initial provisioning · last-time-buy · rotable pool · installed base · PBL | – | – | – | – | – | – | **v3** planning module (`P-052`); four nullable seam columns in v1. **Zero hits across R1–R5** |

### 2.12 Execution layer — RF, tasks, labour, printing, devices

| Capability | T1 | ERP | SMB | IN | DMS | 3PL | Ours · version |
|---|---|---|---|---|---|---|---|
| **Task object separating the business document from the execution instruction** | ● | ◐ | ◐ | ◐ | ○ | ● | **v1 model** (`T-041`) / v1.1 screens. Without it, RF/interleaving/labour are a rebuild of inbound and outbound |
| RF / handheld screen for every warehouse transaction | ● | ● (NetSuite WMS ●, D365 ●) | ● (SkuVault ●, Cin7 ●) | ● (Increff ●) | ● | ● | **v1.1** (D-13, `T-051`, `E-072`) |
| **Native app rather than telnet emulation** | ● (EWM ◐) | ● | ● | ● | ● | ● | **v1.1** — we already have `mobile/`; a genuine advantage |
| Configurable RF flows without code | ● (Oracle ●, Körber ●) | ◐ | ○ | ○ | ◐ | ◐ | **v3** (R2 §1.12 row 244) |
| Offline **capture** with queued writes and a per-scan idempotency key | ◐ (EWM ○, Körber `● ?`) | ◐ | ◐ | ◐ | ◐ | ◐ | **v1.1** (`S-086`, `F-092`) — offline *authority* is refusal #22 |
| **Label design + print service** (ZPL, printer registry, reprint log) | ● | ● | ● | ● | ● | ● | **v1.1** (`S-087`) |
| Keyboard-wedge scan engine, **no vendor SDK in the codebase** | – | – | – | – | – | – | **v1** (`P-036`) — otherwise every deployment becomes a customisation project |
| Device registry, shared-device sign-in, remote session kill | ● | ◐ | ◐ | ◐ | ? | ◐ | **v1.1** (`S-088`) |
| Task interleaving, dynamic priority, assignment by zone / equipment capability | ● | ◐ | ○ | ◐ | ○ | ● | **v2** |
| Supervisor exception console | ● | ◐ | ◐ | ◐ | ◐ | ● | **v1.1** (`T-057`) |
| Labour tracking — actual task times, units per hour, per operator | ● | ◐ | ◐ | ○ | ◐ | ● (DEP ●, M4N ●) | **v2** (`F-079`, `T-058` captures duration from v1) |
| **Engineered labour standards** | ● (Manhattan, BY, EWM, Infor) | ○ | ○ | ○ | ○ | ● (DEP ●, M4N ●) | **NO** as an engine (refusal #3) · **v3** actual-vs-target |
| Voice · pick-to-light · put wall | ● / ◐ | ○ | ○ | ○ | ○ | ◐ | **v3 interface only** (refusal #6 for voice recognition itself) |
| Support impersonation with `on_behalf_of_actor_id` on the audit event | – | – | – | – | – | – | **v1 schema** (`S-092`) — `grep -rli "impersonat"` → 0 across platform and both design sets |
| Floor-language i18n (Hindi, icon-first RF) | ● | ● | ● | ● | ● | ● | **v1.1** (`S-095`). Platform has `en, hi, fr`; **RTL is absent platform-wide** and silently rules out the Gulf |

### 2.13 Valuation and the finance seam

> **The single most important context for this table:** SAP EWM holds **no value at all** — quantity
> lives in EWM, value lives in S/4 MM/FI. Manhattan, Blue Yonder, Körber and Oracle WMS Cloud are the
> same: quantity engines that hand movements to an ERP. That is the tier-1 consensus, and it is why
> `DECISIONS.md` D-6 splits **quantity (ours)** from **value (accounting's)** rather than building an
> accounting sub-ledger inside a WMS.

| Capability | T1 | ERP | SMB | IN | DMS | 3PL | Ours · version |
|---|---|---|---|---|---|---|---|
| Does the stock product hold inventory **value** at all? | ○ *deliberately* (Oracle WMS Cloud ○ / Fusion + Costing ●; Infor `◐ ?`) | ● | ●/◐ | ● | ● | ◐ | **Neither, by design** — warehouse owns quantity, `accounting` owns value (D-6). A deliberate third answer |
| Cost layers with remaining quantity (FIFO) | n/a | ● | ◐ | ● | ● | ○ | **v1** — layers live on the accounting side per D-6; OD-6 open on scope ‡ |
| Weighted average with `moving_average_after` snapshotted on the movement | n/a | ● | ● | ● | ● | ○ | **v1** ‡ (OD-6 recommends WAVG + FIFO in v1; R2 said FIFO-only, R3 said AVCO) |
| Specific identification for serialised items | n/a (S/4 ◐) | ● | ◐ | ◐ | ● | ○ | **v1** (`S-065`) — required by Ind AS 2; the accounting FRD currently defers it |
| Standard cost with purchase-price and usage variances | n/a | ● | ◐ | ● (Tally ●) | ◐ | ○ | **v1.1** (OD-6) |
| **LIFO** | n/a (S/4 ◐, jurisdiction-limited) | ◐ | ○ | ◐ | ○ | ○ | **NO — never built.** Prohibited under Ind AS 2 / IAS 2 (refusal #9, `T-068`, OD-6) |
| Landed cost apportioned, and applied **retrospectively** after issue | n/a (S/4 ●) | ● | ● (Unleashed ●) | ● (Marg ●) | ◐ | ○ | **v1** value-only movement type (`F-088`) / **v1.1** apportionment / **v2** retro (`S-071`) |
| Stock valuation **as at any past date** | n/a (ERP ●) | ● | ◐ | ● (Tally ●) | ● | ◐ | **v1** (`E-053`) — only possible because the ledger is append-only |
| **Non-own stock is never valued** (bailment) | ◐ | ◐ | ○ | ◐ | ● ? | ● (EXT ●, CAM ●, CCL ●) | **v1 rule** (L-14, `S-078`, `F-010`). A 3PL posting clients' stock to its own balance sheet is a catastrophe in both directions |
| **`handover_id` + `posting_status` on the movement row** | – | – | – | – | – | – | **v1** (`S-067`, D-6). Two columns; without them "does stock tie to the GL" is permanently unanswerable for the first audit period |
| Inventory sub-ledger ↔ GL control account reconciliation | n/a (ERP ●) | ● | ○ | ◐ | ◐ | ○ | **v1.1**, owned by `accounting` (`E-002`, `T-066`) — the report that makes an auditor sign |
| NRV write-down **with reversal** | n/a (ERP ●) | ● | ◐ | ◐ | ○ ? | ○ | **v1.1** (`S-072`) — accounting side |
| Inter-branch transfer carries both a **transfer price** and a **cost** | n/a (ERP ●) | ● | ◐ | ● | ● | ○ | **v1 columns** (`E-050` S5, `S-074`) |
| Warehouse never writes an `acc_*` table, proved by a build-time test | – | – | – | – | – | – | **v1** (D-6, `S-068`) — `ArchitectureInvariantsTest` fails the build |

### 2.14 Multi-owner, 3PL and billing

| Capability | T1 | ERP | SMB | IN | DMS | 3PL | Ours · version |
|---|---|---|---|---|---|---|---|
| Owner of goods on every stock record | ● (EWM ◐) | ◐ (Odoo ●) | ◐ | ◐ (Increff ●) | ● ? | ● | **v1** (D-5) |
| **Owner *types* beyond "3PL client"** — house · consignment · customer-owned · job-work material | ◐ | ◐ | ○ | ◐ | ◐ | ◐ (SHH ○, SBB ○, WIQ `?`) | **v1** catalogue (`F-002`) — **we are ahead of the 3PL segment here** |
| Client-scoped users with **hard server-side row isolation** | ● | ◐ | ○ | ● | ○ | ● | **v1** (`F-004`) — scoped in the query, never in the UI |
| **Billable-event meter emitted at per-pick-line granularity** | ● | ○ | ○ | ● (Increff ●) | ○ | ● (SHH ◐) | **v1 emission** (`F-012`) / **v2** meter table. Base v1 either emits it or it is lost forever |
| Charge-code master; rate cards versioned and effective-dated | ● | ○ | ○ | ● | ○ | ● (SHH ◐) | **v2** (`F-013`, `F-014`) |
| Storage billing — four bases (pallet · bin · sq ft · unit/weight) × five methods (month-end · anniversary · daily average · split month · free days) | ● (EWM ○) | ○ | ○ | ● | ○ | ● (LGW/SHH partial) | **v2** (`F-015`) — needs `occurred_at` + `lpn.received_at` from v1 |
| Daily storage snapshot **persisted**, not recomputed | ● | ○ | ○ | ◐ | ○ | ● (SHH ○) | **v2** table / **v1** emission (`F-016`) |
| Handling billing — inbound and outbound, per pallet/carton/unit/line/hour | ● | ○ | ○ | ● | ○ | ● | **v2** (`F-011`) |
| Billing run with a frozen approved state; dispute and credit | ● | ○ | ○ | ◐ | ○ | ● (dispute: EXT ◐, LGW ○) | **v2** (`F-019`, `F-020`) |
| **Invoice handed to accounting AR — the WMS prints none** | ● | – | – | ● | – | ● | **v2** AR envelope (`F-021`) — refusal #16 |
| Client portal — stock, order entry, ASN, returns, reports, document vault | ● (EWM ○) | ◐ | ○ | ● | ○ | ● | **v2** (`F-008`) on the platform public/no-login foundation |
| Per-owner numbering series | ● | ◐ | ○ | ● | ○ | ● (SHH ○) | **v2** (`F-007`) |
| **Mixed-owner movement balancing per `(owner, item)`**, not per movement | ? | ? | ○ | ○ | ○ | ◐ (LGW ○, SHH ○, FUL ○) | **v1** (`F-059`) — **ahead of the segment.** A 3PL's own packaging consumed against a client's order is one atomic event |
| Client SLA definition, measurement, breach record, service credit | ● | ○ | ○ | ● | ○ | ● / ◐ (penalties mostly ○) | **v2** SLA · **v3** penalties (`F-075`, `F-078`) |
| Client profitability / cost-to-serve | ● | ○ | ○ | ○ | ○ | ◐ (CAM ●, M4N ●, CCL ●) | **v3** (`F-023`) |
| Warehousing GST/SAC and place-of-supply for storage services (India) | ○ | ○ | ○ | ◐ | ○ | ○ (SHH ◐) | **v2** (`F-025`, `warehouse-india`). SAC `996729`; POS rule `?` — verify before build |

### 2.15 Returns and reverse logistics

> **‡ The sharpest ladder-vs-lens divergence in the document.** R2, R3 and R4 all placed returns at
> **v1.1**. `DECISIONS.md` §5 places "RMA & reverse logistics" in **v2/P5**. A stock product with no
> sales-return path at v1 loses to literally every product in every column. See [§4.1](#41--v1) and
> [§9](#9--where-the-audits-disagree).

| Capability | T1 | ERP | SMB | IN | DMS | 3PL | Ours · version |
|---|---|---|---|---|---|---|---|
| RMA / return authorisation object | ● | ● | ● | ◐ | ● | ● | **v2 per the ladder; all three lenses said v1.1** ‡ |
| Blind return — goods arrive with no RMA | ● | ● | ● | ● | ● | ● (SHH ◐) | **v2 per the ladder** ‡ — in India this is the *normal* case |
| **`return_type` vocabulary** — customer · RTO · refused · recall · vendor | ◐ | ◐ | ◐ | ● | ◐ | ◐ | **v1 column** (`F-054`) — the disposition rules branch on it; an enum retrofit rewrites them |
| Inspection / grading with condition codes and photographs | ● | ● | ◐ | ● | ● | ● (SHH ◐) | **v2** (`F-051`) |
| Disposition vocabulary as data, each value posting a **different** movement | ● | ● | ◐ | ● | ● | ● | **v2** vocabulary + screen; the port accepts all of them in **v1** (`F-052`) |
| Returns land in a dedicated stock status, never straight to available | ● | ● | ◐ | ◐ | ● | ● | **v2** ‡ |
| **Refund is emitted, never decided** by the warehouse | ● | – | – | ● | – | ● | **v2** outbox event — refusal #17 |
| Return to vendor with a debit-note interface | ● | ● | ● | ● | ● | ◐ (SHH ○) | **v2** (`F-056`) |
| **Core return / core bank with ageing on uncredited cores** | ○ *(all six)* | ○ | ○ | ○ | ● | ○ | **v1.1** (`E-063`, `T-082`, `S-047`) |
| **OEM obsolescence return with an allowance window and %** | ○ | ○ | ○ | ○ | ● | ○ | **v1.1** (`E-060`) |
| **Warranty parts scrap-and-hold with a retention clock** | ○ | ○ | ○ | ○ | ● | ○ | **v1.1** (`E-064`) |
| Marketplace return-claim window (India) | ○ | ○ | ○ | ● | ○ | ○ (FBA ◐) | **v2** adapter (`F-055`) — a real cash line for our customers |
| Refurbishment / repair loop with a work order | ◐ | ◐ | ◐ | ◐ | ◐ | ◐ (SHH ○) | **v2** (`F-058`) |
| Consumer-facing returns portal | ◐ | ◐ | ◐ | ● | ○ | ● (SHH ●, SBB ●) | **NO** — refusal #18 |

### 2.16 India statutory and regulated goods

| Capability | T1 | ERP | SMB | IN | DMS | 3PL | Ours · version |
|---|---|---|---|---|---|---|---|
| HSN on the item **and snapshotted on the line**; UQC on the line | ○ | ◐ (add-on) | ○ | ● | ● | ○ | **v1 schema** (`E-047`, `S-031`) |
| Branch = GSTIN; a cross-GSTIN transfer is a **taxable supply**, with the Rule 28 valuation method recorded | ○ | ◐ | ○ | ● | ● | ○ (UNI ●) | **v1 schema** (`E-050`, `S-022`) / **v2** documents |
| Delivery challan as a numbered document with its own series | ○/print-only | ◐ | ○ | ● | ● | ○ | **v1** doc-type mechanism / **v2** India pack (`S-023`) ‡ |
| Transport details block — dispatch-from / deliver-to, mode, transporter, vehicle, LR, distance | ○ | ○ | ○ | ● | ● | ○ | **v1 columns** (`E-051` S7). A branch transfer has no invoice to hang them on |
| E-way bill Part A + Part B lifecycle, validity, consolidated, cancellation | ○ (EWM ◐) | ○ | ○ | ● | ● | ○ (UNI ●) | **v1 data** / **v2** gateway (`S-024`) |
| E-invoice IRN on the inter-state transfer invoice | ○ | ◐ | ○ | ● | ◐ | ○ | **v2** (`S-025`) — a design that calls transfers "internal" ships an invalid document |
| Job work — challan out, statutory clock, job worker as a location we do not own, ITC-04 | ○ | ◐ (localised) | ○ | ● | ◐ | ○ (INC ◐, UNI ◐) | **v1 schema** / **v2** feature (`S-026`, `E-054`, `F-061`) |
| The Rule 56 **statutory stock account** in the mandated categories | ○ | ◐ | ○ | ● | ◐ | ○ | **v2** (`S-027`) — depends entirely on the v1 reason-code catalogue |
| Godown-wise stock statement (a bank/statutory deliverable) | ◐ | ◐ | ○ | ● | ● | ○ | **v1** (`E-052`) |
| Stock as at a back date for 44AB / a bank stock statement | ◐ | ◐ | ○ | ● | ● | ◐ | **v1** (`E-053`) |
| MRP, net content, country of origin **per pack run on the lot** (Legal Metrology) | ○ | ○ | ○ | ● | ● | ◐ | **v1 columns** (`S-033`, `E-016`) |
| Duty status — bonded · MOOWR · SEZ · FTWZ, ex-bond consumption, customs stock statement | ◐ (SAP GTS, separate) | ◐ | ○ | ◐ | ○ | ○ | **v1 column** / **v2** feature (`S-044`) ‡ |
| ITC reversal on write-off (s.17(5)(h)); scrap sale TCS | ○ | ◐ | ○ | ● | ◐ | ○ | **v1** reason-code mapping (`S-028`) / **v2** report (`S-030`) |
| EPR reporting — batteries, e-waste, tyres, plastic packaging | ○ | ○ | ○ | ◐ | ◐ | ○ | **v2** (`S-050`) — pure reporting over quantities we already hold |
| Pharma — licence gating, Schedule H register, quarantine by default | ◐ | ◐ | ○ | ● (Marg) | ○ | ● (DAV, US pharma) | **v2 adapter, gated on three v1 columns** ‡ — **and refusal #13 declines the vertical** |
| FSSAI licence on the party; best-before ≠ use-by | ○ | ◐ | ○ | ● | ○ | ◐ | **v1 columns** / **v2** adapter (`S-038`) |
| Hazmat — classification, segregation matrix, SDS, TREM card | ● (EWM EH&S) | ◐ | ○ | ◐ | ◐ | ◐ | **v1** classification block / **v2** (`S-042`) |

### 2.17 Analytics, KPI and audit

| Capability | T1 | ERP | SMB | IN | DMS | 3PL | Ours · version |
|---|---|---|---|---|---|---|---|
| Stock on hand by item × location × lot × serial × status × owner | ● | ● | ● | ● | ● | ● | **v1** |
| **Stock movement / ledger register, fully drillable** | ● | ● | ● | ● | ● | ● | **v1** (`E-075`) — the ledger *is* the audit trail |
| Valuation report with method, cost, value, as-at date | n/a (ERP ●) | ● | ◐ | ● | ● | ◐ | **v1** |
| Ageing / no-movement buckets (0-3-6-12-24 months) | ● | ● | ◐ | ● | ● | ◐ | **v1** (`E-076`) |
| **Fill rate / off-shelf first-pick / OTIF** | ● | ◐ | ○ | ○ | ● | ● | **v1.1** (`E-077`) — impossible without lost-sale capture |
| **Inventory turns, true turns, days supply** | ● | ● | ◐ | ◐ | ● | ◐ | **v1.1** (`E-077`) |
| **Obsolescence % and idle-stock value** | ◐ | ◐ | ○ | ◐ | ● | ○ | **v1.1** (`E-077`) |
| Dock-to-stock, order cycle time, on-time ship against a cut-off | ● | ● | ◐ | ◐ | ◐ | ● | **v1.1** over v1 lifecycle columns (`F-074`) |
| Inventory record accuracy from counts | ● | ● | ◐ | ◐ | ● | ● | **v1.1** |
| **The auditor's five artefacts** — as-at ledger · movement export · adjustment analysis by reason/user/value · count history · immutability evidence | – | – | – | – | – | – | **v1.1** (`S-083`) |
| Configurable dashboards / control tower | ● | ● | ◐ | ◐ | ◐ | ● | **PLATFORM** + **v2** |
| **A metric explainer stating each KPI's definition** | – | – | – | – | – | – | **v1.1** (R3 §4.7) — a KPI a manager cannot reproduce by hand is a KPI they will not trust |

### 2.18 Integration, extensibility and non-functional

| Capability | T1 | ERP | SMB | IN | DMS | 3PL | Ours · version |
|---|---|---|---|---|---|---|---|
| REST API over every stock object | ● (EWM ◐) | ● | ● | ◐ | ◐ | ● | **v1** |
| **Idempotent, typed inbound movement port with structured source lineage** (system · doc type · doc id · line no) | ● / ◐ | ● | ◐ | ○ | ◐ | ◐ (M4N ●, DEP ●) | **v1** (`T-091`, `F-081`, `F-084`) — our architectural centre |
| Outbound events at **billable granularity** with a sequence cursor | ● | ● | ● | ◐ | ◐ | ● | **v1 emission** (`F-012`, `F-086`) |
| Interface error queue with reprocess-from-UI | ● | ◐ | ◐ | ◐ | ◐ | ● | **v1.1** (`T-092`) |
| Marketplace / cart connectors | ◐ | ◐ | ● (Cin7 ●) | ● (UNI/EEC/VIN ●) | ○ | ● | **v2**, one adapter per channel (`E-079`, `F-026`) |
| EDI 850/855/856/940/943/944/945/947/810/214 | ● (EWM ◐ via PI/CPI) | ● | ◐ (Cin7 Omni ●) | ◐ | ● | ● | **v3** — retail-compliance B2B is refusal #20 |
| Rules as **bounded, ordered tables**, not an engine | ● engine (Körber Architect is the marquee feature) | ● | ◐ | ○ | ◐ | ◐ (Infoplus scripts) | **v2 rules tables** (`T-093`) — engine and expression language refused (#10) |
| Multi-tenant SaaS | ● (Oracle ●, Manhattan Active ●) | ◐ | ◐ | ◐ | ◐ | ● | **NO** — one DB per customer (OD-3, refusal #12) |
| On-prem / private deployment option | ● (Oracle ○) | ● | ◐ | ● | ● | ◐ | **v1** — inherited from the platform |
| Ledger partitioned from the first migration; 10⁸+ rows at acceptable latency | ● | ● | ◐ | ◐ | ? | ● | **v1** (`T-095`) |
| **Opening-stock import** carrying position, value, layers, lot, serial, owner and duty status, with a reconciliation certificate | ● | ● | ● | ● | ● | ● | **v1** (`S-079`) — designed for 200k–1M rows |
| **Migration in from Tally / Busy / Marg / Excel** with saveable mapping profiles | ● (they migrate *from* us) | ◐ | ◐ | ● *(they are the incumbent)* | ◐ | ◐ | **v1** (`S-080`) — a database-per-customer install means the second customer is a different database |
| Restore / PITR / a **verified** restore path | – | – | – | – | – | – | **v1 platform work** (`S-082`). `grep -n "restore" …/DatabaseBackupService.java` → **0 hits** today |
| Adapter contract proved by a **build-time** test, not by intent | – | – | – | – | – | – | **v1** (D-11, `T-079`) — `warehouse-adapter-dealer` ships with zero commits to `warehouse-base` |
| Open catalogue vocabularies — no CHECK, no Java enum, no re-closing TS union | ● | ● | ◐ | ◐ | ◐ | ● | **v1** (D-10; OD-5 open on the frontend half) |

---

## §3 · Where we win

Five wins that the design earns, and one that it only *enables*. Each carries its caveat, because a
win claimed without its caveat is the thing a customer discovers in week three.

### W1 — The automotive-parts surface, on a real ledger

**The claim.** Supersession chains resolved forward, backward "what did this replace", vehicle
fitment, interchange, cores and a core bank, OEM obsolescence returns with an allowance window,
warranty scrap-and-hold with a retention clock, VOR/emergency order source, counter sale, workshop
material-request → reserve → issue → **return unused to store**, lost-sale capture, and the four KPIs
a parts manager is judged on (fill rate, turns, obsolescence %, days supply).

**The evidence.** In §2.3 and §2.15 every one of these is `○` across T1, ERP, SMB and generic-IN, and
`●` only in DMS (R2 `T-021`/`T-023`/`T-082` and R2 §1.16 row 325; R3 §1.22 rows 183–196; R5 §6 rows 1–3).
Conversely, no DMS-parts product in R3's column carries a double-entry, append-only ledger with owner,
duty status, stock status and LPN dimensions.

**Why it is a win and not a coincidence.** The win is the *combination*. A generic WMS cannot issue a
part to a job card; a DMS parts module cannot produce a reconstructible stock ledger, a godown-wise
statement or a bonded position. We are the only product in the audited set positioned to do both.

**The caveat, stated plainly.** We lose to the DMS column on **computed best stocking level**
(`E-066`, v2) and on **mature OEM order/acknowledgement/invoice/claim interfaces** (`E-062`, v1.1).
R3 §6.3 is explicit: `E-066` and `E-067` are *"precisely the two that separate 'a stock system with a
parts screen' from 'a parts system'"*, and both sit outside v1.

### W2 — One stock ledger across four verticals, with the adapter proved at build time

**The claim.** Dealer parts, workshop job cards, field-service van stock and asset spares all post
through one port to one ledger, and each adapter is a sibling package (`ai.warehouseadapter<vertical>`,
D-1) that ships with **zero commits to `warehouse-base`**, enforced by `ArchitectureInvariantsTest`
plus a `warehouse-adapter-example` reference adapter that CI builds (D-11).

**The evidence.** No product in any column is scored for this because it is not a capability any of
them sells — it is a suite property. The nearest analogue is Tecsys's point-of-use replenishment
(R2 §1.22), which serves healthcare rather than automotive. `services`, `field-service` and `assets`
have **no stock capability at all** today (R1 `C-034`), and `services.parts_used` is free `TEXT`
(`services/…/V40095`, R5 Fact 2).

**The caveat.** `accessories` is permanently excluded (D-9). R3 §5.2 costs that at eleven named items
(C1–C11): a duplicate item master, two stock truths for one physical shelf, no consolidated valuation,
11 report grids that cannot be unified, two warehouse masters for one building, no cross-system
availability at the counter, two GST treatments of one transfer, a doubled compliance surface, two
remediation streams, two mobile surfaces and compounding migration debt. And the load-bearing one:
**the same physical unit counted in both systems is not merely unmitigated, it is undetectable**
without the `whb_item_external_refs` cross-map and the category-ownership rule that D-9 makes
mandatory in v1.

### W3 — The platform we get for free

**The claim.** Branch scoping, RBAC with permission dependencies, `DynamicDataTable` with saved grid
preferences, `BaseFilter`, export/import, i18n, dashboards, document storage, audit logging and a
shipped React Native app. A tier-1 competitor licenses these; an SMB competitor rebuilds them per
screen; we inherit them.

**The evidence.** Scored `PLATFORM` rather than `v1` on eight rows across §2 (item attachments,
location CSV import, configurable dashboards, multi-language UI, granular permissions, flat-file
batch interface, BI export, on-prem deployment).

**The caveat, which is a real constraint on the plan.** D-10's corollary: the loose-coupling ratchet
can only ever be *"zero commits to `warehouse-base`"*, **never** *"zero commits to `platform`"*.
`COMMON_FILTER_CONFIGS` is a TypeScript `const` at `platform/frontend/src/utils/filterUtils.ts:346`
with **210 scopes**, and `CacheConfiguration.java` is platform Java. Every new warehouse grid edits
both (R7 `G-047`, `T-097`).

### W4 — India in the schema, not in a localisation pack

**The claim.** All sixteen of R3 §3.1's S1–S16 land in the first migration: HSN + UQC on item and
line, warehouse → branch → GSTIN binding, the taxable-transfer flag with its Rule 28 valuation method
frozen at creation, a delivery-challan document kind with its own series, the transport-details block,
batches with expiry and MRP, MRP as a valued dimension, an as-at-date-queryable movement history,
stock periods, in-transit as a location, job work with a return-due date, `owner_party_id`,
reason codes with a GL and ITC mapping, and free/scheme quantity on the receipt line.

**The evidence.** In §2.16, every row is `●` in the IN and DMS columns and `○` or `◐` everywhere else.
No global product in any of the four audits carries them; every Indian product carries the *pack* but
none carries a real ledger underneath it.

**The caveat.** R3 §3.3's asymmetry cuts both ways. Shipping S1–S16 and none of D1–D12 means **an
Indian buyer cannot file a return from the product at v1** — the e-way gateway, the IRP adapter, the
Rule 56 stock account and the ITC-04 return are all v2. We are Indian-*correct* at v1 and
Indian-*filing-capable* at v2. Say that, do not blur it.

### W5 — One quantity truth feeding one GL, from one vendor

**The claim.** D-6's split — warehouse is the system of record for every movement, position, count and
adjustment at full grain; `accounting` is the system of record for value — with `handover_id` and
`posting_status (NOT_APPLICABLE | PENDING | POSTED | REJECTED)` on our own movement so that "does the
stock ledger tie to the GL" is answerable from row one.

**The evidence.** §2.13 shows this is the tier-1 consensus: SAP EWM holds no value, Manhattan and Blue
Yonder are quantity engines, Oracle splits value into Oracle Cost Management. The difference is that
their buyer must also own an ERP; ours gets both halves from one vendor and one install.

**The caveat, and it is a live risk.** **OD-1 is unresolved.** The `accounting` design set already
specifies `acc_valuation_entries`, `acc_cost_layers`, `acc_stock_balances`, `acc_godowns`,
`acc_batches`, `acc_stock_journals`, `acc_physical_stock_counts` and an idempotent movement port
(R5 Fact 1, R3 §0.2). Until accounting's set adds the third install state — *"a warehouse product is
present and owns quantity"* — the suite ships **two stock truths**, and R3 §0.2 names the precedent:
QuickBooks Commerce / TradeGecko, withdrawn from standalone sale, its buyers left reconciling two
stock figures by hand.

### W6 — The nine-dimension position key: a *potential*, not yet a feature

`owner_id` **and** `duty_status` in the position unique key is a combination **no audited product
has**. The 3PL products carry owner but not duty status; SAP GTS carries bonded but as a separate
product; nobody in the generic Indian set carries either. R5 §6 puts it starkly: for 3PL contract
logistics, *"one column in v1 turns a **cannot** into a **can**"*.

**The caveat is the whole point of listing it separately.** At v1 this is columns and a seeded default
owner, with no screens. The 3PL product is v2 and the bonded product is v2. Sell the *architecture* to
an investor and the *roadmap* to a customer; do not sell the column as a feature.

### What we do **not** win, so nobody claims it

Breadth · configurability without our consultants · RF flow configuration · waving and wave templates ·
labour standards · slotting · marketplace connector breadth · price against Tally, Marg or Odoo ·
onboarding polish against Zoho or Cin7 · multi-tenant SaaS economics.

---

## §4 · Where we lose, by version

The most useful section in this document. Not softened.

### 4.1 · v1

At v1 we are a correct single-owner, multi-site stock ledger with a parts catalogue, an Indian-correct
schema and enough screens for a storekeeper to run a day. Here is who takes the deal off us and on
what.

| We lose to | On the specific capability | Version that closes it | Honest assessment |
|---|---|---|---|
| **Everyone with a returns screen** — Tally, Marg, Busy, Zoho, Cin7, NetSuite, Odoo, every DMS, every 3PL product | **RMA / sales return / purchase return.** The ladder puts reverse logistics in v2/P5; R2, R3 and R4 all placed it at v1.1 ‡ | v2 as written | **This is the most damaging line in the table and it is self-inflicted.** A stock product with no return path at v1 is not credible in any segment. Resolve the placement before P2 planning closes |
| **Every product with a label printer** | Nothing in this codebase renders a label — `grep -rli "zpl\|escpos\|dymo"` → 0 (R5 Fact 3). R5 ranks it **ship-blocker #2**: *"a warehouse that cannot print a pallet label, a shelf label and a pick list cannot receive its first pallet"* | v1.1 | If v1 ships without it we lose to a spreadsheet with a Dymo. Reconsider the v1.1 placement |
| **CDK · Reynolds · Tekion · Karmak · Autologue** | Computed best stocking level (`E-066`, v2) · lost-sale capture (`E-067`, v1.1) · OEM order/ack/invoice/claim interfaces (`E-062`, v1.1) · price-file load and escalation (`E-068`, v1.1/v2) | v1.1 → v2 | **The dangerous one.** We keep supersession, fitment, counter sale and workshop issue-and-return — enough to be recognised as a parts system. But `E-066` and `E-067` are what a parts manager tests us on. Every quarter they slip costs us the segment we are best positioned to win |
| **Marg · GoFrugal · Busy** | Schemes and free quantity (10+1, `E-080`) · van sales · expiry/breakage claim automation (`E-081`) · decades of Indian distribution muscle memory · a price point we cannot match | v2 (schemes, claims); van sales unplaced | **Partly acceptable.** We must not lose them on batch, expiry, MRP, godown statement, challan or as-at-date — all of which are in the v1 cut for exactly this reason |
| **Tally Prime** | Ten valuation methods · instant back-dated everything · universal accountant familiarity · the accountant already owns it | never | **Unavoidable, and not the fight.** We win by being the *operational* system the workshop and parts counter live in, feeding one GL. As-at-date reporting (`E-053`) is the minimum needed to stop losing on Tally's home ground |
| **Oracle WMS Cloud** | Configurable RF flows the customer edits themselves; LPN-native receiving | v1.1 (LPN handling) / v3 (RF config) | We lose. Their RF configurability and LPN-native model are a decade ahead. Do not bid |
| **Manhattan · Blue Yonder · SAP EWM** | Waving · labour management · slotting · integrated planning · MFS/AS-RS | v1.1 waves, rest refused | We lose, and correctly. Manhattan's labour management alone is larger than our whole v1 |
| **Körber** | Configure the system without the vendor's consultants (Architect) | v2 rules tables (never a scripting layer) | We lose on configurability; we may win on price and time-to-value |
| **Infor WMS** | 3PL billing and multi-client out of the box | v2 | We lose in v1 and should be competitive in v2 **if and only if** `owner_id` and the billable-event emission are in v1 (`T-002`, `T-071`, `F-012`) |
| **SkuVault · Increff · Cin7 · NetSuite WMS · D365 Advanced WMS** | Wave/cluster picking · putaway optimisation · handling units · cartonisation · offline RF | v1.1–v2 | **Right loss.** A 400–5,000 SKU parts store does not pick in waves |
| **Unicommerce · EasyEcom · Vinculum · Shiprocket · WareIQ · Ordoro · Cin7 Omni** | The entire Indian D2C surface: marketplace connectors, AWB pools, pincode serviceability, NDR, COD remittance, RTO | v2 | **Right loss for our buyer**, and a total loss for the D2C buyer. We should not bid the segment at v1 |
| **Extensiv · Camelot · Infoplus · Logiwa · CartonCloud** | Rate cards, storage and handling billing, billing runs, client portal | v2 | We cannot bill for stored goods at all in v1. We can *hold* them correctly, which is the part that cannot be added later |
| **Zoho Inventory · Unleashed · Katana · inFlow · Fishbowl · Finale · Sortly** | Polish · onboarding speed · price | never | **Right loss, and it does not matter** — none of them can issue a part to a job card, model a core or a supersession, or produce a godown-wise stock statement |

**Segments that cannot be served at all at v1** (R5 §6): pharmaceutical distribution (until `S-004`,
`S-007`, `S-008` land — then v2), cold chain (v2), apparel/footwear (a **v1 schema decision** that has
not been taken), 3PL contract logistics (v2), and eCommerce fulfilment (v2).

### 4.2 · v1.1

RF/handheld, tasks, waves, batch picking, packing, labels, dock appointments, van stock, and the
field-service and assets adapters land. What still loses the deal:

| We lose to | On what | Closes at |
|---|---|---|
| **CDK · Reynolds · Tekion · Karmak** | **Computed best stocking level with phase-in/out** (`E-066`) — still the single row a parts manager tests | v2 |
| **The whole Indian statutory set** (Marg, Busy, Tally, and any GST bolt-on) | Cannot file: no e-way gateway, no IRP, no Rule 56 stock account, no ITC-04 | v2 |
| **The whole 3PL and D2C set** | No billing, no client portal, no channel intake, no carrier integration, no NDR/COD/RTO | v2 |
| **Oracle WMS Cloud · Körber** | RF flows the customer configures | v3 (and the scripting layer never) |
| **SkuVault · Cin7 · ShipHero · Logiwa** | Cartonisation algorithm, rate shopping, putaway optimisation, ATP rules, cluster/zone picking | v2 |
| **Everyone in food, pharma and cold chain** | Minimum-remaining-shelf-life enforcement lands at v1.1 (`S-039`) but excursion handling, licence gating and quarantine-by-default do not | v2 |
| **Increff · Unicommerce** | Piece-level unique barcoding as a policy over the serial column | v2 |
| **Anyone needing an apparel matrix** | Still undecided, and unrecoverable if the v1 schema shipped flat | — |

### 4.3 · v2

`warehouse-india` and `warehouse-3pl` ship, plus channels, carriers and reverse logistics. What still
loses:

| We lose to | On what | Closes at |
|---|---|---|
| **Manhattan · Blue Yonder** | Engineered labour standards, slotting optimisation, waveless order streaming, DOM | **never** — refusals #3, #7, #2 |
| **Blue Yonder · NetSuite · D365 · Fulfil · Deposco** | Demand forecasting, MEO, seasonality, replenishment planning | **never in warehouse**; v3 in a planning/logistics module — refusal #8 |
| **Extensiv · Camelot · Made4net · Infoplus** | 3PL billing corner cases: volume tiers, split-month storage, CPI escalation, client profitability, SLA penalties | v2 (tiers) → v3 (escalation, profitability, penalties) |
| **Unicommerce · EasyEcom · Vinculum · Amazon FBA** | Marketplace connector *breadth* and marketplace-native depth. One adapter per channel is not a connector catalogue | never at their breadth |
| **Deposco · Made4net (US retail suppliers)** | Retail-compliance EDI B2B — routing guides, per-retailer ASN 856, chargebacks, GS1 pallet label specs | **never** — refusal #20 |
| **ShipHero · ShipBob · Shiprocket · Unicommerce** | A consumer-facing returns portal | **never** — refusal #18 |
| **Tecsys** | UDI and healthcare supply chain | **never** — refusal #13 |
| **SAP GTS** | International trade compliance and export/customs documentation | **never** — refusal #14 |
| **Made4net · Deposco · Logiwa** | AS/RS, conveyor, sorter and robotics control | **never** as control; v3 as an event contract — refusals #5 and #21 |
| **Körber · Infor · Manhattan** | Voice picking | **never** as a built capability; v3 as an interface — refusal #6 |

### 4.4 · v3

Slotting analysis, replenishment optimisation, labour reporting, ABC/XYZ, planning, EPCIS projection,
automation interfaces, control-tower analytics and the `logistics` module land. **At v3 the remaining
loss list is exactly the refusal list in §7** — every one a deliberate decision with a stated re-entry
path, not a gap.

The one item that is *not* a refusal and still open at v3: **multi-tenant SaaS economics**. Oracle WMS
Cloud and Manhattan Active are multi-tenant; we are one database per customer by platform decision
(OD-3). That is a cost structure, not a feature, and it will show up in per-seat price against a
cloud-native competitor for as long as the platform is single-tenant.

---

## §5 · The India picture

### 5.1 Which Indian segments we can serve, by version

| Segment | v1 | v1.1 | v2 | v3 | The gating item |
|---|---|---|---|---|---|
| **Multi-branch dealership group parts store** (3–8 branches, 1–2 states) | **YES** | YES+ | YES | YES | `E-066` computed stocking is the credibility gap until v2 |
| **Independent workshop / multi-brand service chain** | **YES — greenfield** | YES+ | YES | YES | Nothing competes; `services.parts_used` is `TEXT` today |
| **Field-service / asset spares operator** | partial | **YES** | YES | YES | Van-as-a-location adapter is v1.1 (`S-060`) |
| **General SME multi-godown inventory** | **YES on operations** | YES | YES | YES | Never the GL — Tally keeps that |
| **Auto-parts distributor / wholesaler** | partial | partial | **YES** | YES | Schemes (`E-080`), van sales, expiry claims (`E-081`) |
| **FMCG / food distributor** | partial (columns) | partial | **YES** | YES | Min-remaining-shelf-life v1.1; FSSAI gating and recall v1.1–v2 |
| **Bonded / MOOWR / SEZ / FTWZ operator** | column only | column only | **YES** | YES | `duty_status` in v1 or never (`S-044`) |
| **Pharmaceutical distributor** | **NO** | NO | contested ‡ | contested | Three v1 columns (`S-004`, `S-007`, `S-008`) — then refusal #13 has to be revisited |
| **D2C brand / marketplace seller** | NO | NO | **YES, not on breadth** | YES | AWB pool, serviceability, NDR, COD, RTO — all v2 (`F-042`…`F-046`) |
| **3PL / contract logistics operator** | NO | NO | **YES** | YES | `owner_party_id` in v1 or never (`S-064`) |
| **Apparel / footwear retailer or brand** | **NO** | NO | NO | NO | A v1 style×variant schema decision that has not been taken (`S-056`) ‡ |

### 5.2 Which Indian products we displace, and which we do not

**Displaced at v1**

- **Spreadsheets** — the actual incumbent in most target sites, and the one R2 §5.4 names: *"a dealer
  running parts on `accessories` plus three spreadsheets; a workshop with no stock system"*.
- **Tally's inventory module as an operational system.** Not Tally as the GL — we feed that. But the
  godown-wise statement (`E-052`), the as-at-date stock (`E-053`) and batch/expiry/MRP (`E-014`,
  `E-016`) are in v1 *specifically* so we stop losing on Tally's home ground.
- **The OEM DMS parts module, partially** — on catalogue depth and workshop issue-and-return, not on
  stocking policy or OEM interfaces.

**Displaced at v1.1** — paper pick lists, the clipboard operating model, and the second data-entry
pass that exists because nobody has a handheld. Also the ad-hoc claim spreadsheets that track cores,
obsolescence returns and warranty scrap-and-hold.

**Displaced at v2** — the GST bolt-on (e-way portal spreadsheets, manual challan books, the ITC-04
that somebody reconstructs each quarter), and the 3PL's Excel billing workbook.

**Not displaced, at any version**

| Product | Why not |
|---|---|
| **Tally Prime as the accounting system** | Ten valuation methods, instant back-dating, and the accountant already owns it. We are the operational layer that feeds it, by design (D-6) |
| **Marg / GoFrugal on a pure distribution counter** | Schemes, van sales, expiry-claim automation and a price point we cannot match. R3 §6.2 accepts this loss in v1 |
| **Unicommerce / EasyEcom / Vinculum on marketplace breadth** | One adapter per channel is not a connector catalogue, at any version |
| **Increff on apparel** | Piece-level barcoding is v2 for us; the style×size×colour matrix is undecided |
| **The OEM's own DMS where the OEM mandates it** | A commercial constraint, not a capability gap |

### 5.3 The one asymmetry a product owner must internalise

R3 §3.3, restated because it decides the first migration:

> If v1 ships **S1–S16** (the schema) and *none* of D1–D12 (the seed and the pack), an Indian buyer
> cannot file a return from the product — **but every row of stock ever written is correct**, and
> D1–D12 are a quarter's work.
>
> If v1 ships D1–D12 and misses even **S3** (warehouse → branch → GSTIN), **S4** (taxable-transfer
> flag) or **S7** (transport details), the product looks compliant in a demo and **every branch
> transfer ever recorded is wrong in a way that cannot be repaired without re-keying the history**.

---

## §6 · The 3PL picture

### 6.1 The verdict, and the one column it turns on

R5 §6 scores 3PL contract logistics **CANNOT SERVE — one column decides it**, and calls it *"the
highest leverage-to-cost row in the report: one column in v1 turns a **cannot** into a **can**"*. That
column is `owner_party_id` / `owner_type` in the position unique key and on every movement.
`DECISIONS.md` D-5 puts it in v1, `NOT NULL`, in every install. Four lenses reached that independently
(`T-002`, `F-001`, `F-002`, `S-064`, R7 §6).

### 6.2 Is `warehouse-3pl` a module or a feature flag? — the count

R4 §5.2 classifies all 148 fulfilment capabilities by where they must live:

| Class | Count | Share | What it is |
|---|---|---|---|
| **A** — genuinely 3PL-only, cohesive, heavy | **41** | 28% | rate cards, charge codes, billable events, storage snapshots and their four methods, billing runs, minimums, accessorials, disputes, escalation, client onboarding, the portal, SLA definitions and penalties, per-client numbering, freight pass-through, client GST registrations, profitability |
| **B** — looks 3PL, is actually base or app, **unaddable later** | **23** | 16% | `owner_id` everywhere, `whb_owners`, commingle policy, owner grants, `(owner, sku)` uniqueness, aliases, `is_financial`/`cost_basis`, outbox granularity, LPN + `received_at`, `occurred_at`, lifecycle timestamps, mixed-owner movements, per-owner carrier accounts, zone allocation, `OWNER_CHANGE` |
| **C** — general WMS, needed with or without 3PL | **69** | 47% | receiving, putaway, picking, packing, shipping, counting, returns, kitting, lots, serials, statuses, FEFO, waves, holds, tracking, NDR, COD, RTO |
| **D** — India / channel / carrier, adapter-shaped | **15** | 10% | AWB pool, serviceability, e-way bill, marketplace claims, job work, pharma, channel connectors |

**Verdict (R4 §5.3):** *"`warehouse-3pl` is a real module. It is also a thin module standing on a wide
base concession, and the concession is not optional, not deferrable and not flaggable."* A flag would
not save a single column of class B, and 28% of the surface — eighteen tables, a nightly snapshot job,
a rating engine, a billing-run state machine, a portal permission surface and an accounting hand-off —
is too big to hide behind a boolean.

### 6.3 The v1 checklist that decides whether v2 is possible

R4 §5.4's fifteen items — all schema, none with a v1 screen, together *"well under a month of work"*
and each either free now or impossible later:

`owner_id NOT NULL` in the position key · `whb_owners` + owner types with the house owner seeded ·
`owner_id` **per line** with a `balance_rule` · `is_financial` on the movement type + `cost_basis` on
the line · outbox events at billable granularity · `lpn_id` + `whb_lpns.received_at` ·
`occurred_at`/`recorded_at`/`effective_date` · lifecycle timestamps on receipts, orders, tasks and
shipments · owner-scoped access grants resolved server-side · `(owner_id, sku)` uniqueness plus the
alias table · `commingle_policy` + `dedicated_owner_id` on locations · `owner_id` on carrier accounts ·
stock periods with a close · `stock_status_code` in the balance key · idempotency + append-only +
reversal + sequence.

Miss item 5 and *per-line handling billing — how every audited 3PL prices — is permanently unavailable
for the past*. Miss item 6 and *anniversary storage billing cannot be computed at all, for any period*.

### 6.4 Contract logistics vs eCommerce fulfilment — not the same fight

| | Contract logistics (pallet in, pallet out, storage-billed) | eCommerce fulfilment (per-order, carrier-heavy) |
|---|---|---|
| Reachable at | **v2** on our shape | **v2**, but materially more work |
| Incumbents | Extensiv · Camelot · Infoplus · Made4net; Increff in India | Logiwa · ShipHero · Deposco · WareIQ · Shiprocket; Unicommerce/EasyEcom/Vinculum on the channel side |
| What we need | rate cards, storage snapshots, handling meters, billing run, portal | all of the above **plus** the entire India carrier surface: AWB pool, serviceability, NDR, COD remittance, RTO, weight disputes (`F-041`…`F-047`) |
| Our realistic position | competitive on the core; behind on tiers, split-month, escalation, profitability | behind on connector breadth permanently; competitive only where the client wants their own warehouse, not a marketplace router |

### 6.5 Where we are ahead of the 3PL segment, even at v1

Three rows in §2.14 where our design scores above the segment's modal mark, and each is a v1 concession
rather than a v2 feature:

1. **Owner *types* beyond "3PL client"** (`F-002`) — the segment is `◐`. Consignment vendor stock,
   customer-owned repair stock and job-work material are the same shape as bailed 3PL stock, and we
   model them once.
2. **Mixed-owner movement balancing per `(owner, item)`** (`F-059`) — the segment is mostly `◐`/`○`.
   A 3PL consuming its own packaging against a client's order is one atomic event with a house-owned
   consumption line and a client-owned pick line. A port that balances per *movement* cannot post it.
3. **Bailment as a property of the movement type** (`F-010`, L-14) rather than a reporting convention —
   `is_financial` + `cost_basis = ZERO_BAILMENT`, enforced in the service, not in a report filter.

And one the global segment does not have at all: **the India surface** (`F-025` warehousing SAC and
place of supply, e-way bill on stock movement, cross-GSTIN transfer as a taxable supply) is `○` across
the entire global 3PL column and `●` only for Unicommerce.

### 6.6 The condition on the module split

Restated from R4 §5.3 because it is the thing that fails first:

> `warehouse-3pl` depends on `warehouse-base` and on `warehouse`. **Neither depends on
> `warehouse-3pl`.** No table in `warehouse-base` or `warehouse` has a foreign key to a `wh3_*` table;
> no service imports `ai.warehouse3pl`; no migration below the 3PL band references a `wh3_` name.
> `wh3_clients.owner_id → whb_owners.id` is the only structural link and it points the right way. A
> build-time check enforces it, because the first violation is always innocent and always
> load-bearing.

(Prefix and band corrected to D-3 / D-2; R4 wrote `wh3pl_` and V930000.)

---

## §7 · Deliberate refusals

**27 source rows → 23 distinct topics.** R2 §4 contributes 15, R4 §5.5 contributes 12, and four pairs
merge: R2#3+R2#7 with R4#5 (labour standards and slotting), R2#5 with R4#6 (automation control),
R2#8 with R4#8 (forecasting), R2#10 with R4#10 (rules engine / expression language). The merge list
*is* the method — see [§10](#10--counts-and-how-they-were-computed).

Each refusal must appear in the product documentation **in the place a reader would look for the
feature**, with its reason. *"Not built, because X"* is a credible answer in a sales conversation;
silence is not.

**Re-entry paths.** R4 §5.5 states one per row and those are carried verbatim in intent. R2 §4 states
none, so the re-entry path for those rows is **derived here** and marked `(derived)` — it is a
proposal for the product owner, not a finding of either audit.

| # | We do not build | Source | Who has it | Why not | Re-entry path — what would have to change |
|---|---|---|---|---|---|
| 1 | **A transportation management system** — rate shopping, freight procurement, route optimisation | R2#1 | Manhattan TMS · Blue Yonder TMS · SAP TM · Oracle OTM — all separate products at their own vendors | Rating needs carrier contracts, fuel surcharges, accessorials and dim-weight logic. It is a product, not a feature | *(derived)* The `logistics` module at v3 (D-1 does not list it as one of the five; `DECISIONS.md` §5 puts it in P6). Label generation via one carrier API at v2 is the boundary, and it stays there |
| 2 | **Distributed order management / cross-site order sourcing** | R2#2 | Manhattan DOM · Blue Yonder · Softeon | It decides *where* to fulfil from; a WMS executes once that is decided. Building it makes the warehouse the system of record for orders, which it must not be | *(derived)* Only if an OMS module is funded as a separate consumer of the availability API (`T-085`). Never inside `warehouse` |
| 3 | **A labour-standards engineering engine** (MOST/MTM element libraries, travel-time models) | R2#3 · R4#5 | Manhattan LM · Blue Yonder · SAP EWM LM · Infor · Deposco · Made4net | Engineered standards need industrial-engineering time studies per site. We measure *actual* task duration (free from `T-058`) and report it | R4: v3 on top of `wh_labour_tasks` from v2. Actual-vs-target reporting is v2 and is **not** refused; only the standards engine is |
| 4 | **Incentive pay computation** | R2#4 | Manhattan · Blue Yonder | Payroll consequences from a warehouse metric is a labour-relations product; a wrong number is a legal problem, not a bug | *(derived)* Export measured task durations to a payroll system. Never compute pay here |
| 5 | **Direct automation control** — PLC telegrams, AS/RS material flow, conveyor, sorter, robotics | R2#5 · R4#6 | SAP EWM MFS is uniquely deep; Körber via Aberle; Made4net · Deposco · Logiwa `◐` | Real-time control software with safety implications, written to a different engineering standard than a web application | An adapter per vendor posting through the port. The port already supports it: `actor_type = DEVICE` (`T-059`, `F-072`) |
| 6 | **Voice recognition** | R2#6 | Körber (Voiteq heritage) · Infor · Manhattan · Blue Yonder | Speech recognition tuned for warehouse noise and accents is a specialist product | *(derived)* Integrate a vendor at v3 against the task event contract. Never build the recogniser |
| 7 | **A slotting optimisation solver** | R2#7 · R4#5 | Manhattan · Blue Yonder Slotting Optimization · SAP EWM · Made4net | An OR problem whose value depends on constraints we will not have modelled. Shipping a bad optimiser destroys trust in the good reports next to it | The *analysis* (velocity, cube, affinity) is **v3 and not refused**. The solver re-enters only after a year of our own data — R4's exact condition |
| 8 | **Demand forecasting, multi-echelon optimisation, seasonal profiles, replenishment planning** | R2#8 · R4#8 | Blue Yonder (their origin) · SAP IBP · Oracle Demand Management · NetSuite · D365 · Fulfil · Deposco | A planning product. A WMS that guesses at forecasts is a worse forecaster than a spreadsheet and a worse WMS for the distraction | Consume a forecast through an interface at v3; a separate planning module reads the ledger. `whb_stock_movements` with `occurred_at` is exactly the history a forecaster needs — a dividend of `F-083` |
| 9 | **LIFO costing** | R2#9 | SAP · Oracle, jurisdiction-limited | Not permitted under Ind AS 2 / IAS 2. Offering it invites non-compliant accounts | **None.** OD-6 states it: *"LIFO is never built"*. The valuation enum excludes it and the FRD says why (`S-053`) |
| 10 | **A general-purpose rules engine, scripting layer or expression language** | R2#10 · R4#10 | Körber Architect (their marquee feature) · Manhattan · Blue Yonder · Oracle RF config · Infoplus scripts | Bounded, ordered, typed rule tables give 90% of the benefit and stay reviewable and testable. A scripting layer becomes where business logic hides from code review. Four rule surfaces already exist — allocation, rate shopping, rating, negative stock — and all four are specified as bounded rows | A new **bounded operator**, reviewed once. Never an interpreter. Stated as a set so the fifth surface does not introduce one because *"the other four are limiting"* |
| 11 | **JSONB custom-field bags** | R2#11 | every tier-1 offers user-defined fields | Forbidden by CLAUDE.md's DATABASE CONVENTIONS, and the mechanism by which filters, indexes and reports become impossible | A **designed** typed attribute model at v3 (`T-094`), or nothing. The prior WMS set used `metadata JSONB` on `wms_items` and is referred to the standards reviewer for it |
| 12 | **Multi-tenant SaaS** (one database, many customers) | R2#12 | Oracle WMS Cloud · Manhattan Active | The platform is single-tenant per install by existing decision. `owner_id` gives multi-*client* separation inside one install — what a 3PL needs — and it is **not** the same thing | A platform decision (OD-3), not a warehouse one. `grep -ril "tenant" platform/backend/src/main/java` → 0 files today |
| 13 | **UDI / medical-device and pharma-serialisation compliance regimes** | R2#13 | Tecsys is the reference; Da Vinci for US pharma | Each is a regulatory programme with certification, not a feature. Decline the vertical rather than half-support it | ‡ **Contested.** R5 §6 scores pharma *"CANNOT SERVE **until three v1 schema rows land**"* (`S-004` LPN/SSCC, `S-007` EPCIS dimensions, `S-008` transformation genealogy) and then places licence gating at v2 and serialisation reporting at v3. All three rows are in v1 anyway for other reasons — so the refusal is about the **vertical**, not the schema, and can be revisited when a pharma customer appears |
| 14 | **Export/customs documentation, international trade compliance, FTZ** | R2#14 | SAP GTS · Manhattan and Infor partially | Country-specific regulatory software | ‡ **Partially overruled already.** D-5 puts `duty_status` in the v1 position key and `DECISIONS.md` §5 puts *"bonded/MOOWR duty status"* in v2. The refusal now covers **export and customs documentation only**; bonded warehousing is in the plan |
| 15 | **Shift simulation / digital twin / 3D warehouse visualisation** | R2#15 | Infor 3D visualisation · Blue Yonder simulation `?` | Demo-ware at our stage. It sells to buyers who are not our buyers, and consumes the effort that should go into RF screens | *(derived)* Never as a product feature. If a buyer needs it, export the location and movement data and let a specialist tool consume it |
| 16 | **An invoice, a tax engine or a receivable inside `warehouse-3pl`** | R4#1 | none of the audited 3PL products do this either | It duplicates the accounting module and gives the customer two AR sub-ledgers and double-counted turnover | **Never.** The AR envelope to accounting's inbound port is the interface, and a CSV fallback covers an install with no accounting module (`F-021`) |
| 17 | **A refund or payment path anywhere in warehouse** | R4#2 | Shopify-adjacent tools | A refund is a receivable event with tax consequences | Emit the disposition; the channel or accounting decides (`F-053`) |
| 18 | **A consumer returns portal** | R4#3 | ShipHero · ShipBob · Shiprocket · Unicommerce | It belongs to the brand's storefront. Building it means owning consumer identity, consumer support and a public attack surface for a screen the brand wants to skin themselves | An API. `wh_rmas` accepts an externally-created RMA |
| 19 | **An EPCIS repository with a query/subscription interface** | R4#4 | GS1 solution vendors | A compliance product in its own right. Our obligation is to *emit* correct events | Projection first (`F-071`, `S-009`, v3). A repository only if a pharma customer's trading partner requires one, and then as an adapter |
| 20 | **Retail-compliance / EDI B2B** — routing guides, per-retailer ASN 856, chargebacks, GS1 pallet label specs | R4#7 | Deposco · Made4net `◐` | A per-retailer specification treadmill, and no Indian customer needs it in v1 | `warehouse-adapter-edi`. The LPN, SSCC and shipment structures it needs are already v1 columns |
| 21 | **A second grid-preferences or filter mechanism for the client portal** | R4#9 | — (a standing hazard, not a competitor gap) | The portal is a permission surface over the existing grids. Two mechanisms is how 40 grid identifiers become 80 | — |
| 22 | **Offline-*writing* thick-client operation** (offline authority) | R4#11 | some legacy WMS | The port's idempotency and batch endpoints already give a scan gun offline **capture** with deferred sync, which is the actual requirement. Offline *authority* would falsify the append-only sequence and the hash chain simultaneously | **None.** The honest answer to offline authority is *"not this product"*. Offline capture is v1.1 (`S-086`, `F-092`) |
| 23 | **Yard and trailer management** | R4#12 | Made4net · Deposco `◐` · CartonCloud `◐` · Manhattan · Blue Yonder · SAP EWM YM · Infor | The dock door is ours; the yard beyond it is transport | The future `logistics` module. `wh_dock_appointments` is the join and it exists in v2 (`F-080`, R7 §2.3) |

---

## §8 · The scoreboard

### 8.1 Capability area × our v1 verdict × the market's median

**Method.** *Our v1 verdict* is the modal mark our column would carry across that area's rows in §2,
mapped to `●` (v1 or PLATFORM) / `◐` (mixed v1 + later, or v1 schema with a later screen) / `○` (v1.1
or later throughout) / `NO`. *The market's median* is the median of the six segment marks over the same
rows, with `–` and `?` cells excluded from the median. Both are read off §2; the mapping is stated so a
reader can re-derive it.

| # | Capability area | Our v1 | Market median | Read |
|---|---|---|---|---|
| 1 | Item master & identity | ◐ | ● | v1 covers identity, types, barcodes with pack quantity; variants undecided, custom fields refused |
| 2 | UoM & quantity semantics | ● | ● | **at or above the median** — per-item conversion and a frozen factor beat most of the SMB and IN columns |
| 3 | Catalogue depth (supersession · fitment · cores) | ● | ○ | **the widest gap in our favour.** `○` everywhere except DMS |
| 4 | Lot / serial / LPN / traceability | ◐ | ● | lot and serial full; LPN, genealogy, recall and SSCC are columns in v1 and features later |
| 5 | Facility & location model | ● | ◐ | virtual locations and `duty_status` put us **above** the median; capacity enforcement is v1.1 |
| 6 | Inbound | ◐ | ● | receipt, GRN, blind receipt, reversal in v1; ASN, putaway rules, tolerances v1.1; QC v2 |
| 7 | **Inventory control & the stock ledger** | ● | ◐ | **the area we are built to win.** Median is `◐` because SMB, IN-generic and DMS are single-sided |
| 8 | Counting | ● | ● | at the median; ABC scheduling and accuracy KPIs later |
| 9 | Outbound (demand · allocation · picking) | ◐ | ● | discrete flow and open-item allocation v1; waves and advanced picking v1.1 |
| 10 | Packing, shipping & carriers | ○ | ● | **the weakest v1 area.** Ship confirm and challan only; labels v1.1; the whole India carrier surface v2 |
| 11 | Replenishment & stocking policy | ◐ | ◐ | min/max v1; the DMS-standard computed stocking is v2 |
| 12 | Execution layer (RF · tasks · printing) | ○ | ● | task model in v1, **no RF and no label until v1.1** |
| 13 | Valuation & the finance seam | ◐ | ● | the split is v1 and correct; layers, as-at valuation and the handover markers land, reconciliation v1.1 |
| 14 | Multi-owner, 3PL & billing | ◐ | ◐ | every column is in v1; **no billing at all until v2**. Median is `◐` because ERP/SMB/DMS score `○` |
| 15 | Returns & reverse logistics | ○ | ● | **`return_type` in v1 and nothing else.** The ladder's most damaging placement ‡ |
| 16 | India statutory & regulated goods | ◐ | ○ | schema complete in v1; the pack is v2. Median `○` because only IN and DMS score it |
| 17 | Analytics, KPI & audit | ◐ | ● | the ledger reports are v1; the parts KPIs and the auditor's artefacts are v1.1 |
| 18 | Integration & non-functional | ● | ● | the port, idempotency, partitioning, opening-stock import and the migration-in tooling are all v1 |

**Where we are above the median at v1:** areas 3, 5, 7 (and 2 at parity-plus). **Where we are below:**
areas 10, 12, 15 — and all three are the same story: v1 is a *ledger* release, not a *floor* release.

### 8.2 The honest one-paragraph answer

> **What is this product, in one sentence, at v1?**
>
> At v1 the Classic Warehouse product is a **correct, single-owner, multi-site stock ledger with an
> automotive-parts catalogue and an India-correct schema** — a double-entry, append-only,
> reconstructible ledger keyed on nine dimensions, with items, UoM, lots, serials, statuses, locations
> and virtual locations, receiving, putaway, allocation, picking, shipping, transfers through
> in-transit, adjustments and counts with approval, valuation that hands over to `accounting`, the
> reports a storekeeper and an auditor need, supersession and fitment and counter sale and workshop
> issue-and-return, and the dealer and services adapters that prove the port. It is **not** a
> warehouse-execution system (no RF, no labels, no waves until v1.1), **not** an Indian compliance
> product (the schema is right, the pack is v2), **not** a 3PL platform (the columns are there, the
> billing is v2), and — as the ladder currently reads — **not yet able to take a return**, which is
> the one gap that would embarrass it in front of any buyer in any segment. It is bought by a
> dealership group or a workshop chain that today runs parts on spreadsheets and posts to Tally; it is
> not bought by anyone currently evaluating Manhattan, Increff or Unicommerce, and it should not be
> bid into those deals.

---

## §9 · Where the audits disagree

Sixteen disagreements, each marked `‡` in place above. Rank 1–3 need a decision before P0/P1 close.

| # | Subject | Position A | Position B | Status |
|---|---|---|---|---|
| **1** | **Returns & reverse logistics placement** | R2 §1.17 rows 326–337, R3 §6.1, R4 `F-050`…`F-056` all say **v1.1** | `DECISIONS.md` §5 puts *"RMA & reverse logistics"* in **v2 / P5** | **UNRESOLVED — highest priority.** §4.1 ranks it the most damaging v1 loss |
| **2** | **Apparel style × size × colour model** | R2 #12 and R3 #15 say **v2** | R5 `S-056` says **v1 schema**, BLOCKER-segment: retrofitting a year of flat SKUs is a data-migration project with human judgement in it | **UNRESOLVED.** Decide before the item master's first migration |
| **3** | **Who owns cost layers** | R3 `E-001` recommends warehouse owns quantity **and** cost-layer mechanics | D-6 gives value — *"cost layers, valuation method, revaluation, NRV, COGS and the GL"* — to `accounting`; OD-6 says *"with the layer table present"* | **AMBIGUOUS.** Resolve inside OD-1/OD-6 before `whb_stock_movements` is written |
| 4 | **Label printing placement** | R5 `S-087` ranks it **ship-blocker #2**, v1 | The ladder puts printing in **v1.1 / P3** | Unresolved; §4.1 flags the commercial cost |
| 5 | Valuation methods in v1 | R2 §1.13 row 264: FIFO only. R3 #116/#117: AVCO **and** FIFO | OD-6 recommends **weighted average + FIFO**, layer table present, standard cost v1.1 | OD-6 open; recommendation stands |
| 6 | FEFO | R2 #19 says **v1.1** | R3 `E-017` and R4 `F-067` say **v1** | Majority v1; carried as v1 |
| 7 | Blind receipt | R2 #99 says **v1** (the 3PL and returns default) | R3 #60 says **v2** | Carried as v1 |
| 8 | Supersession chain | R2 `T-021` says **v1.1** | R3 `E-055` says **v1** — the differentiator | Carried as v1 (dealer adapter is v1 per D-1) |
| 9 | In-transit three-leg transfer document | R2 `T-016` says **v1.1** (virtual location v1) | R3 `E-032` and R5 `S-069` say **v1** | Carried as v1; the v1 exit criterion requires a two-site transfer through in-transit |
| 10 | Wave planning | R3 `E-031` and R4 `F-029` say **v2** | The ladder puts waves in **v1.1 / P3** | Carried as v1.1 |
| 11 | Catch weight | R2 `T-012` **v1 model** · R3 #7 **v2** · R5 `S-013` **v1 schema** | — | Carried as v1 schema / v2 feature |
| 12 | Transformation genealogy | R2 #57 **v2** · R4 `F-065` **v2** with v1 lineage | R5 `S-008` **v1 schema** | Carried as v1 schema / v2 feature |
| 13 | Recall | R2 #66 and R4 `F-066` say **v2** | R5 `S-040` says **v1.1** | Carried as v2; flagged for food/FMCG buyers |
| 14 | SSCC generation | R2 #62 says **v2** | R5 `S-005` says **v1.1** | Carried as v2 |
| 15 | Pharma vertical | R2 refusal #13 **declines it** | R5 §6 places it as reachable at v2/v3 once three v1 columns land | Contested; refusal #13 carries the contest note |
| 16 | Customs / bonded | R2 refusal #14 **declines** export/customs/bonded/FTZ | D-5 and R5 `S-044` put `duty_status` in v1 and bonded/MOOWR in v2 | **Partially overruled**; refusal #14 narrowed to export/customs documentation |

### 9.1 A note on competitor cells

Searched for a capability where two audits score the **same named product** differently. None was
found, and the reason is structural rather than reassuring: the audits' column sets barely overlap —
R2 scores six named tier-1 products, R3 scores four *group* columns with named anchors, R4 scores 25
named 3PL/eCommerce/India products. The only overlap is at group level. **Every disagreement above is
therefore about *our* version placement, not about a competitor cell.**

Where a group column and a named product differ — for example R3 scores the India column `◐ (Increff ●)`
for handling units while R4 scores `INC ●` — both readings are carried and the named exception is
shown in the row.

### 9.2 What every reader must carry forward

- **Do not cite a `?` cell externally.** R2 Appendix A lists eleven specific uncertainties (catch-weight
  maturity in four products, whether Oracle WMS Cloud ships a 3PL *billing engine*, Körber's labour
  depth, Infor's slotting, Blue Yonder's native voice, whether appointment scheduling sits in the WMS
  or an adjacent module, Manhattan's yard packaging, Blue Yonder's simulation, Softeon's and Tecsys's
  module names, Körber's Voiteq/Aberle lineage, and SAP LE-WM's maintenance status). R4's appendix
  concentrates its `?` in Indian tax and regulatory detail (`F-025`, `F-061`, `F-073`).
- **No competitor version numbers and no pricing tiers appear anywhere in this document**, for any
  product, because no source audit could verify any.
- **Indian statutory thresholds move almost yearly.** R5 marks every one — e-way bill validity and
  distance, e-invoice turnover applicability, ITC-04 periodicity, HSN-digit thresholds, TCS rate — with
  the value held as of a May 2026 knowledge cutoff and an instruction to re-verify. Treat none as
  current without checking.

---

## §10 · Counts, and how they were computed

Run from `/Users/bbhushan/work/git/workspace/warehouse-issues/docs/reviews`.

<!-- check-design-set: finding-citations begin E-754 — §10's counting note names this token to explain why the command excludes it: `E-754` is the tail of *IEEE-754* at docs/reviews/R1-codebase-reality.md:441, and R1's own word boundary drops it. It is quoted as a false positive, never cited as an R3 finding -->

| Count | Value | Command / method |
|---|---|---|
| Capabilities scored by R2 (tier-1) | **392** | `awk '/^# §1 — THE CAPABILITY MATRIX/,/^## 1.22/' R2-tier1-wms-audit.md \| grep -cE '^\| [0-9]+ \|'` |
| Capabilities scored by R3 (ERP / mid-market) | **196** | `awk '/^## 1. CAPABILITY MATRIX/,/^## 2. FINDINGS/' R3-erp-midmarket-audit.md \| grep -cE '^\| [0-9]+ \|'` |
| Capabilities scored by R4 (fulfilment / 3PL) | **148** | `awk '/^# 1. THE CAPABILITY MATRIX/,/^# 2. FINDINGS/' R4-fulfilment-3pl-audit.md \| grep -cE '^\| [0-9]+ \|'` |
| Capabilities mapped by R7 (logistics seam) | **54** | `awk '/^# §1 — The TMS/,/^# §2/' R7-logistics-supply-chain-seam.md \| grep -cE '^\| [0-9]+ \|'` |
| **Total capability rows across the four matrices** | **790** | 392 + 196 + 148 + 54 |
| Distinct findings across R1–R7 | **575** | `grep -ohE '\b(C\|T\|E\|F\|S\|P\|G)-[0-9]{3}[a-z]?\b' *.md \| sort -u \| wc -l` — matches `DECISIONS.md` §1 |
| — per lens | C 50 · T 98 · E 90 · F 93 · S 98 · P 60 · G 86 | same command, one prefix at a time. `E-754` in `R1:441` is *IEEE-754*, correctly excluded by the word boundary |
| R2 version distribution | v1 74 · v1-model 8 · v1.1 112 · v2 118 · v3 60 · platform 7 · not-built 13 | R2 §Headline. A recount by verdict mark returns 74 / 9 / 112 / 119 / 60 / 7 / 13 = **394** because two rows carry two marks; R2's own 392 is the row count |
| R3 version distribution | **v1 85 · v1.1 59 · v2 43 · v3 9** | first version token per verdict cell: `awk … '{v=$(NF-1); if (match(v,/v1\.1\|v1\|v2\|v3\|OUT/)) print substr(v,RSTART,RLENGTH)}' \| sort \| uniq -c` — sums to 196 |
| R4 version distribution | **v1 41 · v1.1 57 · v2 40 · v3 10** | same method on R4 — sums to 148 and matches R4's own headline exactly |
| R5 findings by severity | 36 BLOCKER · 54 MAJOR · 8 MINOR = **98** | R5 §Findings register header |
| R5 day-one ship-blockers | **11** of 36 | R5 §7.1 |
| R5 *cannot be added later* v1 schema commitments | **28** | `awk '/^# CANNOT BE ADDED LATER/,/^# §6/' R5-standards-industry-ops.md \| grep -cE '^\| [0-9]+ \|'` |
| R5 industry verdicts | **14** segments | `awk '/^# §6 — Industry verdict table/,/^# §7/' R5-standards-industry-ops.md \| grep -cE '^\| \*\*'` |
| R4 base-v1 concessions for 3PL | **15** | `awk '/^## 5.4 What MUST land/,/^## 5.5/' R4-fulfilment-3pl-audit.md \| grep -cE '^\| [0-9]+ \|'` |
| R4 3PL capability classification | A 41 · B 23 · C 69 · D 15 = **148** | R4 §5.2 |
| R3 India v1 **schema** commitments | **16** (S1–S16) | `awk '/^### 3.1 SCHEMA/,/^### 3.2/' R3-erp-midmarket-audit.md \| grep -cE '^\| S[0-9]+ \|'` |
| R3 costs of the `accessories` separation | **11** (C1–C11) | `awk '/^### 5.2 What the buyer actually loses/,/^### 5.3/' R3-erp-midmarket-audit.md \| grep -cE '^\| C[0-9]+ \|'` |
| Refusal rows in R2 §4 | **15** | `awk '/^# §4 — WHAT WE SHOULD DELIBERATELY NOT BUILD/,/^# §5/' R2-tier1-wms-audit.md \| grep -cE '^\| [0-9]+ \|'` |
| Refusal rows in R4 §5.5 | **12** | `awk '/^## 5.5 What we should deliberately NOT build/,/^## 5.6/' R4-fulfilment-3pl-audit.md \| grep -cE '^\| [0-9]+ \|'` |
| **Distinct refusal topics** | **23** from 27 rows | Hand-merge of four pairs, listed at the head of §7: R2#3+R2#7↔R4#5, R2#5↔R4#6, R2#8↔R4#8, R2#10↔R4#10. 15 + 12 − 4 = 23 |
| Named competitor products in the six segment columns | **68** | Enumerated in §0.2: 8 tier-1 + 8 ERP + 10 SMB + 12 India + 7 DMS + 18 3PL/eComm + 4 Indian carriers + 1 cautionary (QuickBooks Commerce/TradeGecko) |
| Rows in this document's consolidated matrix (§2, 18 areas) | **236** | `sed -n '148,492p' ../COMPETITOR-BENCHMARK.md \| grep -E '^\|' \| grep -vE '^\|-' \| grep -vcE '^\| Capability \|'` — lines 148–492 are §2.1 to the start of §3; 272 table lines less 18 header rows and 18 separator rows |
| Disagreements between audits or with the ladder | **16** | §9 table, hand-compiled; each is marked `‡` at its point of use |

<!-- check-design-set: finding-citations end -->


**Citing R2: a matrix row is not a finding, and they look identical.** R2 numbers its capability-matrix
rows independently of its findings, and the rows run to **392** while the findings stop at **`T-097`**.
A row number copied as `` `T-nnn` `` therefore *reads* like a finding and resolves to nothing —
`DECISIONS.md` §7 rule 4a names this as a known hazard and `tools/check-design-set.py` check 7 catches
it. **Five such miscitations were live in this document until 2026-09-02** and are now written as
section references: row 244 (§1.12, configurable RF flows), row 264 (§1.13, FIFO costing), row 325
(§1.16, fitment consumption) and rows 326–337 (§1.17, returns). **Cite a matrix row as
`R2 §1.n row N`, never as `T-N`.**

**Counts deliberately not stated:** effort, cost, schedule, market size, win rate, or any competitor's
revenue, customer count or release cadence. No source audit computed any of them, and none is
derivable from what is in this repository.

---

*Compiled 2026-09-01 from `reviews/R1`–`R7`. Every competitor cell is carried, not re-scored. Every
`?` is the source's, and no `?` was upgraded. `DECISIONS.md` wins on every conflict with this file;
where a lens disagrees with `DECISIONS.md`, §9 records both rather than silently picking one.*
