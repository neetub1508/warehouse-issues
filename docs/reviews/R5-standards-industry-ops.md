# Lens R5 — standards, statute, industry verticals and the operational surface

**2026-09-01** · target: the **new** warehouse design set — `warehouse-base` (V900000–V909999) ·
`warehouse` (V910000–V919999) · `warehouse-adapter-<vertical>` (V920000+) · `warehouse-3pl`
(V930000–V939999). Primary market **India**, sold into the Classic multi-vertical suite.

**The design set does not exist yet.** `/Users/bbhushan/work/git/workspace/warehouse-issues` has
`docs/contracts/`, `docs/reviews/`, `issues/`, `tools/` — all empty, and `git log` reports *"your
current branch 'main' does not have any commits yet"*. This lens is therefore **a requirements
register written before the FRD**, not a conformance review of one. That is the most useful moment
for it: every row below is still free, and roughly a third of them stop being free the day the first
`V900xxx` migration is merged.

**Evidence base actually read** (no web access; knowledge cutoff **May 2026**):

| Source | What it is | Why it counts |
|---|---|---|
| `classic-issues/warehouse-base/docs/**` (28,397 lines, 36 files) | the **prior** WMS design set — `spi/WMS_DATABASE_DESIGN.md` specifies **72 `wms_*` tables** in full DDL; `WMS/*.md` specifies inbound, outbound, packaging, scanning | the new set will inherit from it. Where a column exists there, this lens scores `PRIOR-ART`; where it does not, the gap is real and inherited |
| `accounting/docs/DATA-MODEL.md`, `ACCOUNTING-FUNCTIONAL-REQUIREMENTS.md`, `reviews/R11-*.md` | the in-flight accounting design set | it already contains a **valued stock ledger**. §4 is mostly about that collision |
| `classic/accounting-base/**` (137 files, migrations `V600000`–`V600200`) | accounting-base as built today | the seam is being poured now, not later |
| `classic/` platform, `accessories/`, `services/`, `dealer/`, `mobile/` | the install this ships into | §5 |

## Scoring rule applied

| Score | Means |
|---|---|
| `PRIOR-ART` | a column, table or spec paragraph exists in the prior WMS set. Named, with file and line. |
| `PLATFORM-PROVIDES` | Classic already has the mechanism; reuse it, do not rebuild. Named. |
| `MISSING` | neither. |
| `DECIDE` | not a build — a decision that must be written down before a migration depends on it. |

Severity is **BLOCKER** (cannot sell / cannot be legal / cannot be retrofitted), **MAJOR** (loses the
segment or costs a rebuild), **MINOR** (real, deferrable).

**On citations.** Where I know the rule but not the section number, the rule is stated and the
citation is marked `citation unverified`. Nothing below invents a clause number. Several Indian
thresholds — e-way bill validity distance, e-invoice turnover applicability, ITC-04 periodicity,
HSN-digit thresholds — **move almost yearly**; every one is marked with the value I hold as of
May 2026 and an instruction to re-verify. Treat none of them as current without checking.

---

## Four facts established up front, because most of the report depends on them

### Fact 1 — accounting is already building a stock ledger, and it is not the same shape as ours

`accounting/docs/DATA-MODEL.md` specifies, today, all of the following as `accounting`/`accounting-base`
tables:

| Table | Grain / content | Line |
|---|---|---|
| `acc_valuation_entries` | *"Valued stock ledger — every quantity move with its value"*: `item_id`, `godown_id`, `movement_date`, `movement_type` (RECEIPT·ISSUE·ADJUSTMENT·REVALUATION·OPENING), `quantity`, `unit_cost`, `value`, `balance_quantity`, `balance_value` | `DATA-MODEL.md:436` |
| `acc_cost_layers` | FIFO / specific layers, `quantity_remaining`, `is_exhausted` | `:434` |
| `acc_stock_balances` | quantity on hand per `item × godown × batch × serial`, maintained in the posting transaction, rebuilt nightly with a drift alert | `:507` |
| `acc_source_document_movements` | **the port**: `direction` (RECEIPT·ISSUE), `item_external_id`, `godown_external_id`, `quantity`, **`unit_cost`**, `movement_date`, `status`, `valuation_entry_id` | `:277` |
| `acc_godowns`, `acc_batches` | schema at `V600136` / `V600137`, feature P3 | `:4281–4282` |
| `acc_stock_journals`, `acc_physical_stock_counts` | schema at `V610143`, feature P3 | `:4311` |
| `acc_job_work_challans` (+ lines) | goods to a job worker with the four-year clock, ITC-04 built over it | `:489–490` |

So the accounting product already has a stock ledger, a cost-layer engine, a stock-balance cache, a
stock journal, a physical count and a job-work challan. **The warehouse product is not being added to
a system with a hole in it; it is being added next to a system with an overlapping half.** Until §4's
seam is settled in writing, both sets will be designed as the system of record for quantity, and
every "who owns this" question — count adjustments, opening stock, negative stock, backdated
movements — has two answers.

### Fact 2 — the suite already contains three partial stock ledgers, and one of them is a text field

- `accessories/backend/.../V30130__Create_accessory_stock_levels_table.sql` — `accessory_stock_levels`
  keyed `product × warehouse × bin × batch_number × serial_number` (unique index lines 39–46, with
  the `COALESCE` sentinel idiom), plus `accessory_inventory_transactions` (`V30131`),
  `accessory_stock_adjustments` (`V30132`), `accessory_stock_transfers` (`V30133`),
  `accessory_inventory_counts` (`V30135`). A working miniature of exactly this product.
- `dealer/.../V20083__Create_pdi_vehicle_inventory_table.sql` — vehicle inventory by stock yard.
- `services/.../V40095__Change_parts_used_from_jsonb_to_text.sql` — **`service_entries.parts_used` is
  free `TEXT`.** The migration comment says it outright: *"the field is used as free-text input"*.
  A workshop parts issue in this suite today has **no stock effect at all**.

Consequence for this lens: the "workshop parts issue" and "accessories retail" verticals in the §6 verdict table are not
greenfield — they are **migrations off an existing ledger** (accessories) and **a first ledger where
there was prose** (services). Both belong in `warehouse-adapter-*`, and both need a stated
absorb-or-coexist decision before `V900000`.

### Fact 3 — the platform has no tenancy, no restore, and no offline

Verified in the checkout on 2026-09-01:

- `grep -ril "tenant" platform/backend/src/main/java` → **0 files**. Classic is one database per
  customer. A 3PL's *clients* are therefore **not** tenants and must be modelled as an owner
  dimension inside one database (§4, `S-064`).
- `grep -n "restore" platform/.../service/DatabaseBackupService.java` → **0 hits**. There is backup
  (`pg_dump` + retention) and **no restore path at all**.
- `grep -rli "persistQueryClient\|createAsyncStoragePersister\|offlineQueue" mobile/src` → **0**.
  `mobile/src/contexts/NetworkContext.tsx` reports `isConnected` and nothing queues behind it.
- `grep -rli "zpl\|escpos\|dymo"` across all Java/TS → **0**. There is no label rendering anywhere in
  this codebase.
- `I18nConstants.SupportedLocales:44` → `"en", "hi", "fr"`.

### Fact 4 — the prior WMS set is strong on execution and thin on identity, statute and value

It has 72 tables covering dock appointments, waves, pick tasks, cartons, cycle counts, kits, VAS,
supersessions and interchangeability. It has **no** cost-layer table, **no** landed cost, **no**
ownership grain in the shipped DDL (though `WMS_Inbound_Corrections_Build_Contract.md:109` correctly
demands one), **no** duty status, **no** GLN, **no** EPCIS dimensions, **no** temperature log, **no**
recall object, **no** period lock, **no** device registry and **no** UQC/UN-Rec-20 code on the UoM
master. Its own `ERP_FEATURE_GAPS.md` lists most of these at headline level ("*Hazardous materials
handling & compliance*", "*Multi-client (3PL) inventory segregation*", "*Temperature / cold-chain
monitoring*"). This lens turns those headlines into columns.

---

# §1 — Standards and identification

## 1.1 What GS1 actually is, in schema terms

GS1 is not "barcodes". It is a set of **identification keys**, an **element-string grammar** for
carrying them, and an **event model** for recording what happened to them. A WMS that adopts the keys
but not the grammar ends up with a `barcode VARCHAR(100)` column that cannot tell a case from an each,
and a WMS that adopts neither cannot trade with a modern retailer at all.

| Key | Shape | What it identifies | Where it must live in our schema |
|---|---|---|---|
| **GTIN** (8/12/13/14) | numeric, check digit | a trade item *at a specific packaging level* | `warehouse_item_barcodes.gtin` **plus `uom_id` and `pack_quantity`** — one row per packaging level |
| **SSCC** | 18 digits, AI `(00)` | one **logistic unit** (a pallet, a carton on the road) | `warehouse_licence_plates.sscc` — the LPN table (`S-004`) |
| **GLN** | 13 digits | a party or a **physical location** | `warehouse_warehouses.gln`, `warehouse_locations.gln`, party `gln` |
| **SGTIN** | GTIN + serial, AI `(01)+(21)` | one serialised unit | `warehouse_serials` keyed `(item_id, serial_number)` |
| **GRAI / GIAI** | returnable asset / individual asset | pallets, crates, cylinders, totes | `S-020` — returnable packaging with deposits |

**The AI grammar is the part people skip.** A GS1-128 or DataMatrix scan is a concatenation of
application identifiers, some fixed-length and some variable-length terminated by the FNC1/`<GS>`
(ASCII 29) separator. The ones a warehouse in scope will meet, and what each fills:

| AI | Meaning | Fills |
|---|---|---|
| `(00)` | SSCC | licence plate |
| `(01)` | GTIN | item + packaging level |
| `(02)` + `(37)` | GTIN of contained items + count | mixed/homogeneous pallet contents |
| `(10)` | batch / lot | `lot_number` |
| `(11)` `(13)` `(15)` `(17)` | production / packaging / best-before / expiration date (YYMMDD) | lot dates — **note `(15)` best-before and `(17)` expiry are different obligations** (§2 food vs pharma) |
| `(21)` | serial | serial |
| `(30)` `(310n)` `(320n)` | variable count / net weight kg / net weight lb, `n` = decimal position | **catch weight** (`S-013`) |
| `(240)` `(241)` | additional / customer part number | customer cross-reference |
| `(400)` `(401)` `(402)` | customer PO, consignment number, shipment ID | inbound/outbound matching |
| `(410)`…`(417)` | ship-to / bill-to / ship-from GLN | address identification (`S-006`) |
| `(7003)` `(7007)` | expiry date **and time**, harvest date | pharma / fresh food |
| `(90)`–`(99)` | internal | anything mutually agreed — where most Indian trading partners actually live |

**GS1 Digital Link** re-expresses those keys as an HTTPS URI, and the industry's "Sunrise 2027"
initiative aims at 2D codes (DataMatrix/QR) being accepted at retail point of sale. As of my cutoff
this is an *initiative with a target date*, not a mandate — but it is the reason the barcode format
enum must accept a URI payload from day one rather than assuming digits (`S-017`).

## 1.2 EPCIS — and what "capture what/when/where/why" forces into the ledger

EPCIS 2.0 (ratified 2022; also published as ISO/IEC 19987, with the Core Business Vocabulary as
ISO/IEC 19988 — *citation numbers believed correct, unverified*) defines five event types:

| Event | Means | Warehouse operation |
|---|---|---|
| **ObjectEvent** | something happened to these objects | receipt, pick, count, adjust, ship |
| **AggregationEvent** | children were put on / taken off a parent | palletise, de-palletise, carton pack |
| **TransactionEvent** | objects were associated with a business transaction | GRN against a PO, dispatch against an SO |
| **TransformationEvent** | inputs were consumed and outputs created | kitting, repack, decant, assembly |
| **AssociationEvent** (2.0) | an object was associated with a physical asset | tote/pallet/sensor binding |

The four dimensions, and the exact columns each demands:

| Dimension | EPCIS fields | Column consequence |
|---|---|---|
| **what** | `epcList`, `quantityList` | identity at **three** levels: item, lot, serial — *and* the logistic unit (LPN). A ledger keyed only on item+lot cannot express "pallet 0034…7 moved" |
| **when** | `eventTime`, **`recordTime`**, `eventTimeZoneOffset` | **three** time columns, not one. Physical event time ≠ system capture time ≠ posting date (`S-007`). An offline RF gun makes `recordTime − eventTime` hours, and a backdated correction makes `posting_date` a fourth |
| **where** | `readPoint`, `bizLocation` | *where it was read* ≠ *where it now is*. A dock scanner reads at the dock; the goods' business location is the QC bin. Two location columns |
| **why** | `bizStep`, `disposition`, `bizTransactionList`, `sourceList`/`destinationList` | **`bizStep` (what process) and `disposition` (what state the goods are now in) are different axes**, and this is the single most common modelling error in a WMS. The prior set collapses them: `wms_inventory.stock_status` mixes workflow (`ALLOCATED`, `PICKED`, `PACKED`) with condition (`DAMAGED`, `EXPIRED`) with legal state (`BLOCKED`) — `WMS_DATABASE_DESIGN.md:1899-1903` |

**We do not need to implement EPCIS in v1.** We need the ledger to be *capable of emitting* it, which
costs eight columns and one aggregation table now and is a rebuild later. That is `S-007`.

## 1.3 Barcode symbologies

| Symbology | Where | Note |
|---|---|---|
| EAN-13 / UPC-A | consumer unit retail | UPC-A is GTIN-12; **the same product scans as 12 digits in one place and 13 in another** — normalise to GTIN-14 on store (`S-003`) |
| ITF-14 | corrugated cases | prints on brown board where DataMatrix does not |
| **GS1-128** | logistics labels, SSCC | the workhorse. Carries the AI string |
| GS1 DataBar | small items, loose produce, some pharmacy | carries GTIN + AI in a fraction of the width |
| **DataMatrix (ECC200)** | regulated goods, tiny items, direct part marking | the EU FMD unique identifier and the Indian pharma QR mandate both land here |
| QR / GS1 Digital Link | consumer-facing, Indian pharma top-brands mandate | needs URI payload parsing |
| Code 39 / Code 128 | internal LPNs, location labels | fine for internal use; never for trade |

## 1.4 RFID / EPC

EPC UHF Gen2 (ISO/IEC 18000-63) with the EPC Tag Data Standard encodings (`sgtin`, `sscc`, `sgln`,
`grai`, `giai`). India's delicensed UHF band is 865–867 MHz (*unverified*), which matters because
tags and readers sourced for the US 902–928 MHz band under-perform here. Apparel retail in India is
the segment that will actually ask for this. `S-010`.

## 1.5 EDI — what a buyer will actually ask for

| Doc | X12 / EDIFACT | Who asks | Verdict |
|---|---|---|---|
| **ASN** | **856** / DESADV | every large retail customer, every 3PL client, GS1-labelled inbound | **Real. v1.1.** Also the inbound half — receiving against a supplier ASN with SSCC scan is the single biggest receiving-speed win |
| Warehouse shipping order | **940** | 3PL clients instructing our warehouse to ship | **Real for `warehouse-3pl`. v2** |
| Warehouse shipping advice | **945** | the reply to 940 | **Real. v2** |
| Warehouse stock transfer shipment / receipt advice | **943 / 944** | 3PL client moving stock in | v2 |
| Warehouse inventory adjustment advice | **947** | 3PL client reconciliation | v2 |
| Inventory inquiry/advice | **846** | client/marketplace stock feeds | **Real, and the most-asked in India — usually as a CSV/API, not EDI. v1.1 as an API, v2 as EDI** |
| PO / PO ack / invoice | 850 / 855 / 810 | procurement | belongs to accounting/procurement, not here |
| Transport status | 214 / IFTSTA | carriers | v2, TMS |

**Honest India note:** outside pharma majors, auto OEMs and global 3PL contracts, Indian trading
partners overwhelmingly integrate by **portal upload, SFTP CSV or REST**, not X12/EDIFACT. Building a
full EDI translator in v1 is the wrong bet; building a **document-shaped integration port** whose
first two adapters are CSV and REST, and whose third is an EDI mapper, is the right one (`S-015`).

## 1.6 Units of measure

Three vocabularies must coexist and they are not the same list:

1. **Internal** — `EA`, `CASE`, `PALLET`. Ours.
2. **UN/CEFACT Recommendation 20** — `EA`/`PCE`, `KGM`, `LTR`, `MTR`, `H87`. What EDI and most
   international integrations expect.
3. **GST UQC** — the fixed, closed list the GST portal accepts on invoices and e-way bills
   (`NOS`, `PCS`, `KGS`, `BOX`, `BTL`…). **An e-invoice with a UQC outside the list is rejected at the
   IRP.** *(List contents as of cutoff; re-verify.)*

The prior `wms_units_of_measure` (`WMS_DATABASE_DESIGN.md:766`) has `uom_code`, `uom_name`,
`uom_type` and nothing else. Two columns — `unece_rec20_code`, `gst_uqc_code` — and the compliance
payloads and EDI both become derivable. Without them, every integration hand-maps (`S-011`).

---

# §2 — Statute and regulated goods

## 2.0 Where the India pack lives — a topology decision that must precede `V900000`

The accounting product solved this by creating a **separate module**, `accounting-india`
(`classic/accounting-india/`, its own `pom.xml`, its own migration folder). The warehouse brief names
four modules and **none of them is a jurisdiction module**: `warehouse-adapter-<vertical>` is a
*vertical* axis (dealer, services, accessories), not a *jurisdiction* axis.

Everything in §2.1–§2.3 below — e-way bill, delivery challan, job work, ITC-04, Rule 56 stock account,
MRP declarations, bonded warehousing — is India-specific and will be dead weight in the first
non-India install. Putting it in `warehouse` makes the core product un-sellable outside India; putting
it in `warehouse-adapter-dealer` makes it invisible to a pharma customer.

**Add a fifth module, `warehouse-india`**, with its own band, before the first migration is written.
This is `S-021` and it is a `DECIDE`, not a build.

## 2.1 GST and stock movement

### The rule that reshapes the transfer document

A stock transfer between two establishments of the same legal entity that hold **different GSTINs**
(different states, or two registrations in one state) is a **supply between distinct persons** and is
taxable even though no money moves and no third party is involved. It requires a **tax invoice**, not
a delivery challan, and the value is determined by the valuation rules — open market value, failing
that the value of like goods, failing that cost-plus — with the practical relief that where the
recipient is entitled to full input tax credit, **the value declared on the invoice is deemed to be
the open market value**.

*Source: CGST Act Schedule I (supplies without consideration between distinct persons) and CGST Rules
r.28 (value of supply between distinct or related persons), second proviso. Substance confident;
**exact paragraph and rule numbers unverified**.*

A transfer between two locations under **the same GSTIN** is not a supply, and moves on a **delivery
challan** instead (CGST Rules r.55 — *rule number believed correct, unverified*).

**What this forces into the schema.** A warehouse must know its tax registration, because *the same
physical operation is two different legal documents depending on it*:

```
warehouse.legal_entity_id      -- which company owns this site
warehouse.tax_registration_id  -- which GSTIN it operates under
warehouse.state_code           -- GST state code, 2 digits
transfer.document_kind         -- TAX_INVOICE | DELIVERY_CHALLAN, derived, never chosen
```

The prior set's `wms_warehouses` (`WMS_DATABASE_DESIGN.md:141`) and `wms_warehouse_branches` (`:246`)
carry no registration at all. A transfer document with no registration on either end **cannot be
classified**, and no amount of later code can classify the historical ones. `S-022`, `S-023`.

### E-way bill

Required for movement of goods where the consignment value exceeds the threshold — **₹50,000** for
inter-state, with **state-specific intra-state thresholds that differ** (several states set ₹1 lakh;
some exempt intra-city movement) — and required **irrespective of value** for inter-state movement of
goods to a job worker and for handicraft goods. *(CGST Rules r.138 and state notifications; thresholds
as of cutoff, **re-verify — these move**.)*

The data it needs, and where it comes from:

| EWB field | Source in a WMS | Prior set |
|---|---|---|
| Supply type, sub-type (supply / export / job work / SKD-CKD / line sales / recipient not known / **own use** / exhibition) | the movement's reason | MISSING |
| Document type + number + date | the transfer/invoice/challan | partial |
| From GSTIN, from place, from **PIN code**, from state | warehouse registration | MISSING (`S-022`) |
| To GSTIN, to place, to PIN, to state | destination warehouse / customer | MISSING |
| Per-line **HSN**, description, quantity + **UQC**, taxable value, tax rates | item + UoM masters | `commodity_code` exists (`:843`); UQC does not (`S-011`) |
| Transport mode (road/rail/air/ship), transporter GSTIN/TRANSIN, document number & date | carrier | `wms_carriers` exists (`:2366`), no TRANSIN |
| Vehicle number and type (regular / over-dimensional cargo) | dispatch | MISSING |
| **Approximate distance** | PIN-to-PIN | MISSING — and it drives validity |

Mechanics that are behaviour, not fields: **Part-A is generated by the consignor, Part-B (vehicle) may
be filled later and must be filled before movement**; validity is **one day per 200 km** for regular
cargo (20 km for over-dimensional) counted from the time Part-B is first entered, extendable in
transit; cancellation is allowed within **24 hours** if goods were not transported; a **consolidated
e-way bill (EWB-02)** covers multiple consignments in one vehicle; and EWB generation is **blocked**
for a GSTIN that has not filed returns for two consecutive periods. *(All numbers as of cutoff;
re-verify. The 100 km→200 km change happened; whether it has moved again since, I cannot say.)*

The prior set has a real e-way bill implementation living in a `supply-chain-core` module
(`WMS_Competitive_Gap_Analysis_And_Roadmap.md:240`: *"production-grade Ports & Adapters …
vendor-agnostic `ComplianceProviderPort`, provider resolver, rule engine, encrypted credentials, API
logging (`scc_compliance_*`)"*), and `WMS_Outbound_Flow_Gap_Review.md:86` records a live defect in it
(null Part-B sent to NIC producing a cryptic gateway rejection). **That is prior art worth
transplanting, not rebuilding** — but it must land in `warehouse-india`, and the data it consumes must
exist in `warehouse-base`. `S-024`.

### E-invoice

Applicable above an aggregate turnover threshold (**₹5 crore** as of my cutoff, having stepped down
from ₹500 crore over several years), for B2B supplies, exports and credit/debit notes; B2C is out.
An IRN must be obtained from an IRP before the invoice is valid, and taxpayers above a higher turnover
(**₹10 crore**, from 2025) must report within **30 days** of the document date. *(All three numbers as
of cutoff; **re-verify**.)*

Warehouse touches this in exactly one place and it is easy to miss: **the inter-state stock transfer
invoice of §2.1 is a B2B invoice and needs an IRN.** A design that treats transfers as "internal" will
ship a document that is legally invalid. `S-025`.

### Job work

Inputs sent to a job worker must be returned (or supplied from the job worker's premises) within
**one year**; capital goods within **three years**; failing which the sending is deemed a supply on the
date the goods were sent, with interest. The movement goes on a **delivery challan**, and the
quantities out and back are reported in **ITC-04** *(periodicity now depends on turnover —
half-yearly / annually around a ₹5 crore line; as of cutoff, re-verify)*. *(CGST Act s.143 and Rules
r.45 / r.55; substance confident, **section numbers believed correct but unverified**.)*

This matters far more than it looks in this suite. **Every workshop that sends a part out for
machining, every dealer that sends a body panel for painting, every accessories retailer that sends
material for embroidery is doing job work.** The obligation is a **dated clock measured from the
challan date**, so — exactly as the accounting set already argues for `acc_job_work_challans`
(`DATA-MODEL.md:489`: *"a movement predating the table has no challan row, therefore no clock, and the
liability is silently untracked"*) — a movement recorded before the challan object exists can never
acquire one. The job worker must also be **a stock location** (our goods, their premises), which is the
same modelling need as consignment. `S-026`.

### The stock account the law actually requires

Every registered person (other than a composition dealer) must keep a **true and correct account of
goods**: opening balance, receipts, supplies, **goods lost, stolen, destroyed, written off or disposed
of by way of gift or free sample**, and closing balance — separately for raw materials, finished
goods, scrap and wastage; plus, where relevant, the details of goods with a job worker. Records must be
retained for **72 months from the due date of the annual return**. *(CGST Act s.35 / s.36 and Rules
r.56; substance confident, **rule numbers believed correct, unverified**.)*

Two consequences, both structural:

1. **There must be a statutory stock register report**, per GSTIN, per period, in those exact
   categories — not a generic movement grid. `S-027`.
2. **The adjustment reason code is a tax classification, not a note.** "Lost", "stolen", "destroyed",
   "written off", "gift", "free sample" are the six the statute enumerates and each triggers ITC
   reversal under the blocked-credit provision (CGST s.17(5)(h) — *substance confident, clause letter
   believed correct*). The prior set has `wms_stock_transactions.reason_code VARCHAR(50)` — **free
   text** (`WMS_DATABASE_DESIGN.md:1962`). Free text cannot drive a reversal, cannot be reported, and
   cannot be corrected retrospectively across a year of adjustments. `S-028`.

### The rest of the GST surface

| Rule | Warehouse consequence | Finding |
|---|---|---|
| ITC reversal on write-off, loss, free issue, gift, samples (s.17(5)(h)) | the reversal **amount** needs the original ITC, which needs the receipt-side tax on that lot — a movement must be able to reach its receipt | `S-029` |
| Scrap sale is a taxable supply with its own HSN; **TCS at 1% under Income-tax s.206C(1)** on scrap | scrap is not "shrinkage", it is inventory with a value, a location and a sale | `S-030` |
| HSN reporting digits vary by turnover (4 / 6 / 8) | HSN belongs on the item **and must be snapshotted on the movement line** — reclassifications happen and history must not move | `S-031` |
| Goods sent on **approval / sale or return** — delivery challan, deemed supply at six months | a stock state "at customer, not sold" that is still our asset | `S-032` |

## 2.2 Legal Metrology / weights and measures

The Legal Metrology Act 2009 and the **Legal Metrology (Packaged Commodities) Rules 2011** require a
pre-packaged commodity to declare: name and address of manufacturer/packer/importer, common or generic
name, **net quantity in standard units**, month and year of manufacture/packing/import, **retail sale
price (MRP) inclusive of all taxes**, consumer-care contact, unit sale price, and — for imports and
e-commerce listings — **country of origin**. Weighing and measuring instruments used in trade
(a weighbridge, a counter scale) must be **verified and stamped** periodically by the Legal Metrology
department. *(Substance confident; **rule numbers unverified**.)*

Warehouse consequences that are not obvious:

- **MRP is a property of the pack run, not of the SKU.** Two batches of the same item legitimately
  carry different MRPs, and retail/dealer stock must be valuable and sellable at *the printed* MRP.
  MRP therefore belongs on the **lot/batch**, with the item carrying only the current default. Adding
  it later means every historical lot has a null MRP and no way to recover it. `S-033`.
- Net content, pack size and the count-per-pack are the same data the GTIN packaging level needs
  (`S-001`), so model them once.
- A weighbridge is a legal instrument: its **verification certificate, validity date and calibration
  record** are audit evidence for every bulk receipt weighed on it. `S-034`.

## 2.3 Regulated goods

### Pharmaceutical

| Obligation | Source | Schema consequence |
|---|---|---|
| Batch number and expiry are **mandatory** on every pack, and stock must be traceable by batch | Drugs and Cosmetics Act 1940 / Drugs Rules 1945 (*rule numbers unverified*) | batch tracking cannot be an item-level *option* for these items — it must be enforced by the item's regulatory class |
| Sale/purchase records with batch, and **Schedule H1** register kept for three years | Drugs Rules, Schedule H1 (*retention period believed 3 years, unverified*) | a dispensing/sale register distinct from the stock ledger |
| Wholesale/retail **drug licence** on the entity and on every counterparty; sales only to licensed parties | Drugs Rules Forms 20B/21B (*form numbers unverified*) | `party.licence_number`, `licence_expiry`, and a **hard block on despatch to an expired licence** |
| **Barcoding of exported drug formulations** at primary/secondary/tertiary pack with GS1 keys | DGFT public notices; the DAVA/iVEDA reporting portal | serialisation + aggregation (`S-004`, `S-036`) |
| **QR code / barcode on the top-300 drug brands'** packs, sourced to a database giving batch, dates, manufacturer | MoHFW amendment to the Drugs Rules, in force from Aug 2023 (*rule number unverified; scope may have widened since my cutoff*) | DataMatrix/QR parse (`S-002`) and a per-pack identity |
| API manufacturers' QR mandate | Drugs Rules amendment 2023 (*unverified*) | as above |
| **Recall** — CDSCO recall guidance rather than a single statutory recall regulation as of my cutoff | guidance | a recall object: scope by lot/serial, downstream trace, quantity recovered, disposition |

**For a global buyer**, the comparison is **DSCSA** — the US Drug Supply Chain Security Act, Title II
of DQSA 2013 (*the brief says "DSCPA"; the correct name is DSCSA*). It requires unit-level
serialisation and, at full effect, **interoperable, electronic, package-level tracing** — in practice
EPCIS-based. Enforcement was staged into 2024–25 with a stabilisation period and small-dispenser
exemptions; **I cannot state the position after May 2026.** The EU equivalent is the Falsified
Medicines Directive: a DataMatrix unique identifier plus tamper-evident closure, verified against the
European Medicines Verification System at dispense.

**Verdict for our design:** we do not implement DSCSA or FMD. We implement **the shape** — SGTIN
identity, aggregation, and an event log with EPCIS's four dimensions — so that an
`warehouse-adapter-pharma` can emit either. Without that shape, pharma is `CANNOT SERVE` permanently.
`S-035`, `S-036`, `S-037`.

### Food and FMCG

| Obligation | Source | Consequence |
|---|---|---|
| FSSAI licence/registration for every food business operator, displayed and quoted | FSS Act 2006; FSS (Licensing and Registration) Regulations 2011 | licence number + expiry on our entity **and on every counterparty**; despatch blocked to an expired licence |
| Records of raw material, production and sale retained for **one year or the shelf life, whichever is longer** (*believed correct, unverified*) | Licensing Regulations | retention policy is **per-item**, driven by shelf life — not a global setting (`S-051`) |
| **Recall plan is mandatory**, with one-step-forward / one-step-back traceability | FSS (Food Recall Procedure) Regulations 2017 | mock recall, trace-forward report, recall register (`S-040`) |
| Labelling: date of manufacture, **best before vs use by**, batch/lot | FSS (Labelling and Display) Regulations 2020 | two different date columns with different meanings — best-before is quality, use-by is safety; only one of them justifies a hard despatch block (`S-038`) |
| Hygiene and temperature control | Schedule 4 of the Licensing Regulations (*unverified*) | temperature logging (`S-041`) |
| Voluntary but universally demanded by modern trade: **HACCP / ISO 22000 / FSSC 22000**, Codex | — | CCP records tied to lots |

### Cold chain

This is the one place where the standards world and the statute world meet cleanly: **EPCIS 2.0 added
sensor data (`sensorElementList`) to the event model precisely for this.** A cold-chain warehouse
needs: a temperature/humidity reading stream bound to a **zone, a location, a shipment or an LPN**; an
**excursion event** with duration and severity; and a **disposition decision** — the goods are not
automatically scrap, a QA person decides, and that decision is the audit record. None of the three
exists in the prior set; `wms_item_storage` has `temperature_min_c`/`max_c` as *item requirements*
(`WMS_DATABASE_DESIGN.md:949-950`) with nothing measuring against them. `S-041`.

### Hazardous and dangerous goods

The prior set is better here than anywhere else: `wms_item_storage` carries `is_hazmat`,
`hazmat_un_number`, `hazmat_class` (1–9), `hazmat_packing_group` (I/II/III),
`hazmat_proper_shipping_name`, `hazmat_subsidiary_classes` (`:955-961`). That is a correct UN Model
Regulations classification block and it should be kept verbatim.

What is missing is everything that *uses* it:

| Requirement | Source | Missing |
|---|---|---|
| **Segregation** — which classes may not be stored or loaded together | UN Model Regs / IMDG segregation table; MSIHC Rules 1989 for storage | a class×class segregation matrix, enforced at **putaway** and at **load**, not just declared |
| **Storage quantity limits** per licensed premises | Manufacture, Storage and Import of Hazardous Chemical Rules 1989; Petroleum Rules 2002 / PESO licence for petroleum classes A/B/C; Explosives Rules | a per-zone / per-licence quantity ceiling with a **live** check, and the licence itself as a dated object |
| **Safety data sheet** current version available at the site | MSIHC / GHS practice | SDS as a versioned document on the item, with an expiry review date |
| **Transport documentation** — class labels, emergency information panel, **TREM card**, trained driver, vehicle fitness | Central Motor Vehicles Rules 1989, rr.129–137 for transport of dangerous goods (*rule range believed correct, unverified*) | dispatch-time document generation and a driver/vehicle eligibility check |

`S-042`, `S-043`.

### Customs and bonded warehousing — the deepest schema consequence in this report

A bonded warehouse holds goods on which **duty has not been paid**. Everything follows from that:

| Mechanism | Substance | *(Citations: Customs Act 1962 Chapter IX, ss.57–73; Warehouse (Custody and Handling of Goods) Regulations 2016; MOOWR 2019 under s.65. **Section numbers believed correct, unverified.**)* |
|---|---|---|
| Licence | public / private / special warehouse licence, with a bond officer | the site is a **licensed** object with a validity |
| **Warehousing bond** | a bond, commonly for **triple the duty**, executed by the importer (s.59) | a bond object with a running utilisation balance |
| **Warehousing period** | one year for general goods, extendable; **capital goods under MOOWR effectively until clearance**; interest accrues after 90 days for some categories | a **dated clock per Bill of Entry**, with interest |
| Ex-bond clearance | ex-bond Bill of Entry for home consumption (s.68) or for export (s.69) | a clearance document that consumes specific bonded quantity, **per BoE** |
| Inter-warehouse transfer | removal from one warehouse to another (s.67), re-warehousing certificate | a transfer that preserves duty status |
| **MOOWR** | manufacture/other operations in a bonded warehouse with duty **deferred**, no interest; digital records in a prescribed form; monthly return to the bond officer; waste and scrap treated on clearance | input-output tracking and a monthly statutory return |
| SEZ / FTWZ | a separate customs territory; movement DTA↔SEZ is import/export with its own documents; NFE obligations | a location that is legally outside the domestic tariff area |

**The schema consequence is one column and it is unforgiving: `duty_status` must be part of the stock
position's identity.** Bonded and duty-paid stock of the same SKU in the same warehouse **must never
merge into one balance**, because clearing the wrong one is a customs offence, and because the ex-bond
BoE consumes an identified bonded quantity. Adding `duty_status` after go-live means every historical
row is `DOMESTIC` by assumption and no bonded operation can be reconstructed. `S-044`, `S-045`.

Adjacent and much smaller: the **Warehousing (Development and Regulation) Act 2007** and WDRA
registration, which is what lets a warehouse issue **negotiable warehouse receipts** (now electronic —
eNWR) against agricultural commodities. Relevant only if we chase agri 3PL; it is a v3 adapter.
`S-046`.

### Automotive

| Requirement | Prior set | Finding |
|---|---|---|
| Spare-parts warranty | `wms_serial_numbers.warranty_start_date` / `warranty_end_date` (`:2091-2092`) | `PRIOR-ART` — keep |
| **Core returns** (a remanufacturable old part exchanged against a new one, with a core charge) | `wms_core_exchanges` (`:3134`) and `wms_serial_numbers.linked_core_serial_id` (`:2095`) | `PRIOR-ART` — genuinely good. What is missing is the **core as inventory**: a returned core is stock, in a condition state, with a value, awaiting return to the OEM (`S-047`) |
| **Recall, VIN-linked** | none | a part serial/lot must be reachable **from the VIN it was fitted to**, which means the outbound movement must record the vehicle — and that link only exists if the workshop/dealer adapter writes it at issue time (`S-048`) |
| Counterfeit-part control | none | authorised-supplier flag on the item×supplier pair; serial authentication against the OEM; a "suspect part" quarantine disposition (`S-049`) |
| **EPR — batteries, e-waste, tyres, plastic packaging** | none | Battery Waste Management Rules 2022, E-Waste (Management) Rules 2022, Plastic Waste Management Rules and tyre EPR each require **quantity reporting by category** and certificate purchase. An auto-parts warehouse handles all four categories. This is a *reporting* obligation over quantities we already hold (`S-050`) |

## 2.4 Records, audit and the valuation statutes

| Obligation | Source | Consequence for this design |
|---|---|---|
| Books of account, incl. stock records, kept **8 financial years** | Companies Act 2013 s.128(5) | a retention clock, an archival tier, and a **legal-hold flag** — the ledger cannot simply grow forever and cannot simply be purged (`S-051`) |
| GST records **72 months** from the annual-return due date | CGST s.36 | a *second, different* clock. Two retention regimes on the same rows |
| **Quantitative details of stock** — opening, purchases, sales, closing, shortage/excess — in the tax audit report | Income-tax s.44AB, Form 3CD (*clause believed 35, unverified*) | **the single most concrete report obligation in this section**: a per-item quantitative reconciliation for a financial year that must tie to both the stock ledger and the GL (`S-051`) |
| **Cost records and cost audit** for specified industries (incl. much of auto components) | Companies Act s.148, Companies (Cost Records and Audit) Rules 2014, CRA-1 (*rule reference unverified*) | quantitative records of materials consumed by cost centre — reachable from our ledger only if issues carry a cost object (`S-052`) |
| **Audit trail** in accounting software, with edit log, not disableable | Companies (Accounts) Rules r.3(1) proviso; auditor reports on it under CARO-adjacent rules | the stock ledger is part of the books. **Append-only, no `UPDATE`, no `DELETE`, corrections as reversing rows** (`S-054`) |
| **Ind AS 2 / AS 2 / IAS 2** — cost formulas | permitted: specific identification (for non-interchangeable items and segregated projects), FIFO, weighted average. **LIFO is prohibited** (removed from IAS 2 in the 2003 revision and never permitted under Ind AS). Standard cost and retail method permitted **if they approximate cost**. Lower of cost and NRV, item by item. **Write-down reversal is required when the cause ceases** — unlike US GAAP | `S-053`, and §4 |
| **ICDS II** for tax, and **s.145A** | tax valuation follows FIFO/weighted average (no LIFO), and s.145A requires inventory to be valued **inclusive of tax, duty, cess actually paid** to bring goods to their present location and condition | a *second* valuation basis alongside books. If the design has one `unit_cost` per movement, the 145A adjustment is a spreadsheet forever (`S-053`) |
| Erasure vs retention | DPDP Act 2023 (*section unverified*) | same precedence question the accounting lens raised (`N-043`): retention beats erasure, satisfied by pseudonymisation. State it once (`S-055`) |

---

# §3 — Industry analysis

The full verdict table is **§6**. This section carries only the findings that arise from the analysis
and are not already covered by §1, §2 or §4.

## 3.1 The three verticals already inside this suite

**Workshop / service parts issue** is not a greenfield vertical — it is a **repair**.
`services/backend/.../V40095__Change_parts_used_from_jsonb_to_text.sql` converted
`service_entries.parts_used` from JSONB to `TEXT` with the comment *"the field is used as free-text
input"*. So today: a mechanic types the part name, no stock moves, no cost reaches the job, no reorder
point fires, and no warranty claim can be evidenced. Fixing it means a `warehouse-adapter-services`
that (a) reserves parts against a job card, (b) issues on fitment with the job as the cost object,
(c) **accepts returns of unissued parts**, which is the half everyone forgets and the reason
counter-stock walks, and (d) links the issue to the vehicle for `S-048`'s VIN recall. `S-061`.

**Accessories retail** already has a working miniature ledger (`accessory_stock_levels` +
`accessory_inventory_transactions` + adjustments + transfers + counts, `V30130`–`V30136`). The design
set must state, before `V900000`, whether `warehouse-base` **absorbs** it (migrating history, which is
the only way to get one number for stock in the group) or **coexists** with it (two stock figures
forever). There is no third option and silence picks the second. `S-062`.

**Dealership parts department** is the nearest thing to a real customer this product has. It needs
counter sale with a walk-in customer, VOR/emergency ordering, **lost-sale capture** (the part we did
not have — the only data that ever improves a parts stocking policy), supersession chains and
interchangeability. The last two are `PRIOR-ART` and unusually good: `wms_item_supersessions`
(`:1203`), `wms_interchangeability_groups` (`:1236`). Lost-sale capture is `MISSING` and it is cheap.
`S-063`.

## 3.2 The verticals that need a structural addition, not a feature

**Apparel and footwear** is the largest single organised-retail inventory segment in India and our
item master **cannot express it**. A style comes in a size × colour matrix; a buyer orders a *ratio
pack* (2 S, 4 M, 4 L, 2 XL); a store replenishes at variant level but plans at style level; and every
grid, filter and report is a matrix, not a list. `wms_items` is a flat SKU with `product_family
VARCHAR(100)` (`:842`) and nothing else. Retrofitting a style/variant/dimension model onto a year of
flat SKUs is a data-migration project, not a feature. `S-056`.

**Chemicals** needs §2's hazmat enforcement *plus* **catch weight** (`S-013`) and often **potency /
assay** on the lot — the same nominal 100 kg drum is 98.2% active and priced on the active. A lot
attribute set that cannot carry an assay cannot serve it.

**Construction materials** needs the **weighbridge** as a first-class device: gross/tare/net capture,
two weighings bound to one movement, a tolerance policy, moisture deduction, and the instrument's
verification certificate (`S-034`). It also needs bulk locations (silo, heap, yard) whose "count" is a
survey, not a count sheet. `S-058`.

**E-commerce fulfilment** needs single-line wave strategies, put-to-light or tote-based batch picking,
courier manifest and label generation, **returns grading into condition states**, and a marketplace SKU
mapping table. The prior set's wave/pick/pack machinery (`wms_waves` `:2631`, `wms_pick_tasks` `:2722`,
`wms_shipment_cartons` `:2921`) is a good base; the identity mapping and the returns grading are the
gaps. `S-059`.

**3PL** is the one vertical whose requirement is not a feature at all but **a dimension** — see
`S-064` in §4 and the whole of `warehouse-3pl`. Without an owner on the position and on the document,
3PL is `CANNOT SERVE`, and no amount of billing code changes that.

## 3.3 The finding nobody expects: assets and field service are a spare-parts vertical

`assets/` (maintenance) and `field-service/` (job execution) both consume parts and neither has a parts
ledger — `grep` for `part|consum|material` in either module's migrations returns nothing. A field
engineer's van is **a stock location** (a mobile one), a preventive-maintenance task **reserves** a
part before the visit, and an unused part **returns to the van, not to the warehouse**. Van stock is
the classic reason a service business's inventory number is wrong. It is a small adapter over a ledger
that already has locations — provided the location model allows a **mobile/virtual location owned by a
person**. `S-060`.

---

# §4 — The valuation and accounting seam

## 4.1 The collision, stated plainly

| | Warehouse | Accounting (as designed today) |
|---|---|---|
| Quantity ledger | `warehouse_stock_movements` (proposed) | `acc_valuation_entries` — *"every quantity move with its value"*, `DATA-MODEL.md:436` |
| Balance cache | `warehouse_stock_positions` (proposed) | `acc_stock_balances`, `:507` |
| Grain | item × **location** × lot × serial × **owner** × **duty status** × condition | item × **godown** × batch × serial |
| Physical count | cycle counts + full stocktake | `acc_physical_stock_counts`, `V610143` |
| Adjustment document | stock adjustment with approval | `acc_stock_journals`, `V610143` |
| Cost layers | — | `acc_cost_layers`, `:434` |

Two systems, both authoritative for quantity, at two different grains, with two counts and two
adjustment documents. **This is a BLOCKER and it is a decision, not a build.** `S-064`.

The only coherent split, and the one I recommend:

> **Warehouse owns quantity and physical truth at full grain. Accounting owns value.**
> `warehouse` is the system of record for every movement, position, count and adjustment.
> `accounting` never maintains a quantity balance of its own: `acc_stock_balances` is deleted or
> demoted to a **read-through projection** of the warehouse ledger, and `acc_physical_stock_counts` /
> `acc_stock_journals` become *inbound document kinds*, not user-facing screens, whenever the
> warehouse product is installed.

That requires a **third state** in the accounting design — today it assumes either "a source module
sends documents" or "accounting does it itself". A warehouse install is the case where accounting must
*stand down* from a capability it otherwise owns. Say so explicitly, or the first customer with both
modules gets two stock reports that disagree and neither team owns the difference. `S-064`.

## 4.2 Costing methods and what each forces into the schema

| Method | Schema it forces | Permitted? |
|---|---|---|
| **Moving average (AVCO)** | one `unit_cost` per position **plus** `moving_average_after` snapshotted **on every movement row** — otherwise a backdated receipt silently restates the cost of issues already posted, and nothing can prove what the average was on 31 March | Ind AS 2 / ICDS II: **yes** |
| **FIFO** | a **layer table** (`receipt_date`, `quantity_in`, `quantity_remaining`, `unit_cost`) **and a consumption table** linking each issue to the layers it consumed, with quantities. Two tables, not one | **yes**, and this is the India default |
| **Standard cost** | `standard_cost` with an effective-dated history, plus **variance accounts**: purchase price variance at receipt, usage/quantity variance at issue, revaluation variance at standard change | **yes, if it approximates actual** — which means a periodic variance-to-actual test, not a promise |
| **Specific identification** | the cost travels on the **serial or the lot**, not on the item×location | **required** for non-interchangeable items; the accounting FRD **explicitly defers it** (`ACCOUNTING-FUNCTIONAL-REQUIREMENTS.md:230`: *"Specific identification, manufacturing and WIP are out of scope — deferred explicitly"*) |
| **LIFO** | — | **Prohibited** under Ind AS 2 / IAS 2 and under ICDS II. **Do not build it, do not offer it in the enum, and say why in the FRD** — because a Tally-migrating customer will ask for it, and "we removed it" is a better answer than "we never thought about it" |

`S-053`'s consequence and `S-065`: **specific identification is not optional for this product** even
though it is optional for accounting. Vehicle inventory (dealer), high-value electronics, and any
serialised spare are non-interchangeable by definition. If the warehouse ledger carries serial-level
cost and accounting cannot receive it, the seam drops it.

**Retail method** (sell price less margin) deserves one line: it is permitted, it is how a lot of
Indian retail actually values stock, and it needs `sell_price` on the position — which the MRP-on-lot
column of `S-033` already provides.

## 4.3 Landed cost

Duty, freight, insurance, clearing charges and port handling arrive **after** the goods do, on a
different document, in a different currency, often weeks later. The design must decide, in v1's schema:

- an **apportionment basis** per charge (value / net weight / volume / quantity / manual);
- **retrospective revaluation** of the receipt layer — which, if the layer has already been partly
  consumed, splits into a layer adjustment and a **COGS adjustment** for what already shipped;
- a link from the charge document back to the receipt movements it loads.

The trap: landed cost is what makes `acc_cost_layers.unit_cost` *not final at receipt*. A port whose
`unit_cost` is write-once (`acc_source_document_movements.unit_cost`, `DATA-MODEL.md:277`) cannot carry
this. `S-071`.

## 4.4 NRV, write-down and provisioning

Ind AS 2 requires the lower of cost and net realisable value, assessed **item by item**, with **reversal
when the cause ceases**. A warehouse is where the evidence lives: ageing, slow-moving, obsolete,
damaged, expired. What the schema needs is a **write-down register** — item/lot, assessed NRV, basis,
assessor, date, amount, and the reversal linked to the original — not a one-way `provision_amount`
column. And an ageing/slow-moving/obsolescence policy that produces *candidates*, because the write-down
itself is a judgement someone signs. `S-072`.

## 4.5 Cut-off — the three period-end questions that need columns

| Question | The stock state | Column |
|---|---|---|
| Goods received, not invoiced (**GRNI**) | ours, on our shelf, unbilled | the receipt must carry `invoice_matched` and the accrual must be derivable per movement |
| Goods in transit | **ownership depends on the Incoterm** — EXW/FCA means it is ours the moment it leaves the supplier's dock | `in_transit` as a **location type**, plus `ownership_transfer_point` on the purchase/transfer document |
| Consignment | in our building, **not our asset** (or in the customer's building and still ours) | the owner dimension, `S-064` |

All three are the same underlying statement: **the warehouse's four walls are not the boundary of the
inventory asset**, and a design that keys stock only to physical locations we control will report the
wrong balance sheet twice a year. The virtual-location scheme in `S-069` is the mechanism.

## 4.6 Inter-branch transfer pricing

A transfer between GSTINs (§2.1) carries a **tax invoice at a price**. Under Ind AS that price is not
cost, so **unrealised profit sits in the receiving branch's stock** and must be eliminated in the
entity's accounts. Two numbers per transferred unit, therefore: **transfer price** (the tax document)
and **cost** (what follows the goods). A design with one `unit_cost` on a transfer either overstates
inventory or files a wrong invoice. `S-074`.

## 4.7 COGS recognition timing

Dispatch, delivery or invoice? All three are defensible and the answer differs by customer. The design
must make it **a configured policy with a stock state per stage**: `PICKED` → `DISPATCHED (in transit,
still ours)` → `DELIVERED (COGS)`. If it is hardcoded to "COGS on dispatch", every FOB-destination
customer is wrong every month end, and there is no state in which the goods are simultaneously off our
shelf and on our balance sheet. `S-075`.

## 4.8 The interface to `accounting-base` — exactly what crosses

**Warehouse must not write `acc_*` tables.** Reasons, in order of how expensive they are to learn late:
the accounting ledger is **hash-chained and append-only** (`acc_audit_events`, `V600111`) and a foreign
writer breaks the chain it is the whole product's claim to protect; period locks, approvals and reason
codes are enforced in accounting's service layer, not by its constraints; and a cross-module FK into
`accounting` inverts the module dependency the accounting set spent a whole review (`DATA-MODEL.md`
§3.1 crossing table) making point downward.

**The handover, concretely.** One envelope per posting-relevant event, through the existing source-
document port:

```
handover {
  idempotency_key        -- warehouse movement/batch UUID. Replays are no-ops.
  company_id, branch_id
  document_kind          -- STOCK_RECEIPT | STOCK_ISSUE | STOCK_ADJUSTMENT | STOCK_TRANSFER
                         -- | STOCK_WRITE_DOWN | STOCK_REVALUATION | OPENING_STOCK
  document_number, document_date
  posting_date           -- accounting date, NOT the physical movement time
  reason_code            -- from the closed catalogue of S-028; drives the account and the ITC rule
  movements[] {
     direction           -- RECEIPT | ISSUE
     item_external_id, godown_external_id
     owner_type, owner_party_external_id   -- NEW. Non-own stock must not be valued (S-078)
     duty_status                            -- NEW. Bonded stock is not a duty-paid asset (S-044)
     lot_external_id, serial                -- for specific identification (S-065)
     quantity, base_uom
     unit_cost           -- present only where WAREHOUSE computes it; null where accounting does
     cost_basis          -- NEW. WAREHOUSE_COMPUTED | ACCOUNTING_TO_COMPUTE
  }
}
```

Three explicit decisions this shape forces, none of which exists today:

- **`S-066` — who computes cost.** The port has `unit_cost` (`DATA-MODEL.md:277`) *and* accounting has
  `acc_cost_layers`. Both cannot be true. Recommendation: **accounting computes value; warehouse
  supplies quantity, identity and the receipt-side purchase cost only.** Then FIFO/AVCO/standard lives
  in one place and the warehouse never has to be right about accounting policy.
- **`S-067` — the acknowledgement path.** Every warehouse movement row needs `handover_id` and
  `posting_status` (`NOT_APPLICABLE | PENDING | POSTED | REJECTED`), and a **rejected** handover needs
  a queue with an owner. Without it, "does the stock ledger tie to the GL" is unanswerable, and it is
  the first question at every close and every audit.
- **`S-068` — the invariant, tested.** An architecture test that fails the build if any class under
  `ai.warehouse*` references an `acc_*` table or an `ai.accounting*` type. `accounting-base` already
  ships `ArchitectureInvariantsTest`; copy the pattern.

## 4.9 Consignment, 3PL and "not our asset"

`acc_valuation_entries` has no owner column, so **every movement that reaches it becomes our
inventory**. For a 3PL that is catastrophic in both directions: the client's stock lands on our balance
sheet, and our storage revenue has no cost of goods at all. The rule is one line and it must be in the
FRD: **movements whose `owner_type != OWN` are handed over for *quantity and custody reporting only*
and are never valued.** What we do carry for them is a **custody liability** and an insured value —
which is a different number, on a different report. `S-078`.

---

# §5 — The SaaS operational surface

A WMS differs from an accounting product in one way that dominates this section: **the warehouse does
not stop.** An accounting package that is down for an hour is an inconvenience; a WMS that is down for
an hour has forty people standing in an aisle, and goods that moved anyway. Almost every row below is
a consequence of that sentence.

## 5.1 Go-live and migration

| Requirement | Reality | Finding |
|---|---|---|
| **Opening stock import at scale** | a mid-size distributor opens with 20k–200k SKUs and 200k–1M position rows: item × location × lot × serial × **owner** × **duty status**, each with a **value** and, under FIFO, **layers**. Value must be imported, not derived — there is no purchase history | `S-079` |
| **Migration from Tally / Busy / Marg / Excel** | these are the incumbents. Each exports a different shape; none exports locations, none exports layers, most export a godown-level closing quantity and a closing value. Duplicate SKUs, unit mismatches (`PCS` vs `NOS` vs `EA`), and alternate units are the three failures every time | `S-080` |
| Dry run + reconciliation certificate | accounting solved this well (`P2-15`: dry run, error report, dry-run trial balance compared against the source's own, apply, rollback, certificate). **Copy it**, with "closing stock value per the source" as the tie-out figure | `S-079` |
| Cutover with a **stock freeze window** | the count that establishes opening stock happens on a Sunday and go-live is Monday; anything that moves between is manual. A documented cutover procedure is a deliverable | `S-081` |

## 5.2 Backup, restore and the ledger's own integrity

`DatabaseBackupService` runs a `pg_dump` and **has no restore path** (`grep -n "restore"` → 0). For a
statutory stock ledger that is not an availability risk, it is a **records risk**. Add to it: no WAL
archiving, no PITR, no restore-verification job, no stated RPO/RTO. `S-082` — and it is platform work,
so it does not compete with warehouse engineers.

## 5.3 The audit trail an auditor will ask for

Not "we log things". Specifically:

1. **Stock ledger as at a date**, reproducible — for the 3CD clause-35 quantitative statement and the
   statutory stock account of §2.1. A *reproduction*, not a live query: the same date must give the
   same answer next year (`S-083`).
2. **Movement-level audit export** for a period: every movement with who, when, from what document,
   with what reason code, including reversals and their originals.
3. **Adjustment analysis**: every quantity that entered or left without a commercial document, by
   reason code, by user, by value — this is the fraud report, and it is the one an internal auditor
   asks for first.
4. **Count history** with variance, by counter, including recounts.
5. **Immutability evidence**: the ledger is append-only and the corrections are visible as corrections
   (`S-054`).

## 5.4 Performance targets — because none are stated anywhere

The prior set specifies indexes but no targets. Propose these as the FRD's non-functional section, so
the design can be tested against something:

| Dimension | Target to design against |
|---|---|
| Stock ledger rows | **1M/day peak** for a large 3PL; 20k/day for a dealer parts department. Partition or archive strategy stated at design time, not after |
| Position table | ≤ 5M live rows; **the unique key is the hot spot** — every extra grain column multiplies it |
| Scan-to-response | **< 300 ms** at the handheld, or the operator stops trusting it and works ahead of the system |
| Allocation | **200 order lines/second** with no oversell |
| Count sheet | 5,000 lines in one count, entered by 10 counters concurrently |
| Pick list generation | a 500-line wave in < 5 s |
| Export | 100k-row stock report without holding a transaction open (the platform's known export failure mode) |

`S-084`.

## 5.5 Allocation under concurrency — the correctness problem, not the speed problem

Two pickers, one unit. The prior set has the right *buckets*
(`quantity_allocated/picked/packed/blocked`, `quantity_available` as a **generated stored column**,
`WMS_DATABASE_DESIGN.md:1876-1880`) and one document mentions a `version` optimistic lock
(`WMS_PO_To_Inventory_And_Scanning_Flow.md:118`). What is not specified anywhere is **the locking
discipline**: optimistic retry, `SELECT … FOR UPDATE`, or an allocation queue. Under a generated
column, two concurrent allocations both read `available = 5` and both write, and the CHECK constraint
`quantity_on_hand >= 0` **does not catch it** because on-hand did not change. The negative-stock
policy — allowed / warned / blocked, per warehouse or per item — must be decided in the same breath,
because it determines whether the constraint is `>= 0` at all. `S-085`.

## 5.6 Offline and poor connectivity

There is **no offline mutation queue anywhere in this codebase** (Fact 3). A warehouse has metal
racking, cold rooms and dead spots; a receiving dock has a truck waiting. Three levels, and the design
must pick one per screen:

| Level | What it means | Where it is required |
|---|---|---|
| **Read-cached** | last known list survives a dropout | putaway/pick lists |
| **Queued write** | scans buffer locally, replay on reconnect, **idempotency key per scan**, conflict surfaced not swallowed | counting, receiving, picking |
| **True offline** | a whole session offline for hours | rarely needed; do not promise it |

The idempotency key is the part that is irreversible: replayed scans without one produce duplicate
ledger rows, and a duplicate in an append-only ledger can only be fixed by a reversal that looks like
an adjustment. `S-086`.

## 5.7 Printing and labels — the largest single omission in the prior set

`grep -rli "zpl\|escpos\|dymo"` across the whole repo → **0**. `wms_label_templates` exists
(`:3393`) with no rendering engine behind it. What is actually required:

- **ZPL** (Zebra) as the primary target — every Indian warehouse label printer speaks it or emulates
  it; EPL and TSPL for cheaper units; PDF for laser.
- **Direct-to-printer** from the handheld over the network, not "download a PDF and print it" — an
  operator with a pallet cannot use a browser download dialog.
- A **printer registry**: printer per zone/dock, default label size, DPI (203 vs 300 changes every
  barcode's width), media type.
- A **print job log with reprints flagged** — a reprinted SSCC label is a duplicate licence plate in
  the wild, and it is exactly how two pallets end up with the same ID.
- Label kinds: **item/shelf label, LPN/pallet label (SSCC, GS1-128), carton label, shipping label,
  location label, GRN, pick list, packing slip, delivery challan, e-way bill print, hazmat class
  label**.

`S-087`.

## 5.8 Devices

No device registry exists (`DeviceRegistrationRequest` in the platform is a **push-notification token**,
not a device). An RF deployment needs: a device inventory with an assignment, **device-bound sessions**
with a long expiry (an operator will not type a password every 15 minutes with gloves on), a shared-
device sign-in that is fast, **session handover at shift change**, and a way to remotely end a session
on a lost gun. Add the ergonomics constraint that shapes every screen: **one-handed, gloves, scanner
trigger, no free typing** — which mostly means the mobile app's `EntityListScreen` filter constraints
(CLAUDE.md, MOBILE MODULE) are the wrong base for warehouse screens and a dedicated RF screen family
is needed. `S-088`.

## 5.9 Error recovery — the physical move that the system rejected

This is the defining WMS support case and it deserves a first-class object. The goods **have already
moved**. Refusing the transaction does not un-move them; it only guarantees the system is wrong and
that the operator will stop telling it the truth.

Required: a **discrepancy / blocked-move queue** that records the attempted movement, the rejection
reason, the operator and the physical reality, keeps the goods in a **`PENDING_RESOLUTION`
disposition**, and routes to a supervisor who can force it with a reason code and an approval. Plus the
common concrete cases — receipt exceeding PO tolerance, pick from an empty location, putaway into a
full/incompatible location, scan of an unknown barcode, count variance beyond threshold, despatch of an
expired lot. `S-089`.

## 5.10 Month-end freeze

No period-lock object exists in the prior set. Required: a **stock period** with a lock, per warehouse
or per company, that (a) blocks new movements with a posting date in the closed period, (b) blocks
*backdating* into it, (c) allows an explicit reopen with an approval and an audit event, and (d) is the
same period the accounting seam locks — otherwise the two ledgers can be closed at different moments
and will never agree. `S-090`.

## 5.11 Counting

The prior set has cycle counting (`wms_cycle_count_programs/tasks/results`, `:3200`–`:3331`) and **no
full physical stocktake**, which is the one every auditor attends and every customer does at least
annually. It needs: a **snapshot freeze** of book quantity at count start (otherwise the variance is
computed against a moving target), **blind counting** (counter does not see book quantity — without
this the count is worthless), **recount thresholds**, multi-counter assignment by zone, count sheets
that can be printed and keyed back, and an **approval before posting** with the variance value shown.
`S-091`.

## 5.12 Support, diagnostics and training

| Requirement | State | Finding |
|---|---|---|
| **Support impersonation** with consent and audit | `grep -rli "impersonat"` across platform and both design sets = 0. Same finding the accounting lens raised as a day-one ship-blocker (`N-045`) | `S-092` |
| Per-install health: movements posted today vs baseline, handovers stuck in `PENDING`, counts overdue, negative positions, orphan allocations, unreconciled positions | none | `S-093` |
| In-product help / SOP per screen | `HelpButton` exists in the platform component set — `PLATFORM-PROVIDES`, needs content | `S-094` |
| Training surface: a **sandbox/practice warehouse** with disposable data | none. For a WMS this is not a nicety — you cannot train pickers on live stock | `S-094` |
| i18n on the warehouse floor | platform supports en/hi/fr. **Warehouse operators are the most language-diverse users in the whole suite**; the RF screens are the place where Hindi and regional languages actually matter, and where icons beat words | `S-095` |
| Data volume and archival | a 1M-rows/day ledger needs a stated partition/archive strategy that **does not break "as at" reproduction** (§5.3) | `S-096` |
| Integration surface for e-commerce/marketplace | API keys, webhooks, rate limits, replay | `S-097` |
| **Degraded-mode operation** | when the system is down the warehouse keeps working on paper. The product needs a documented paper fallback and a **catch-up entry mode** that accepts backdated movements with the real event time (`S-007`'s three time columns are what make this possible) | `S-098` |

---

# Findings register — `S-001` … `S-098`

**98 findings: 36 BLOCKER · 54 MAJOR · 8 MINOR.**
`schema` = a column, key or dimension that is cheap now and expensive-to-impossible later (see the
irreversibility table). `feature` = buildable any time on a schema that already exists.
`DECIDE` = neither; a decision that must be written before a migration depends on it.

## Register A — standards and identification

| # | Sev | Requirement | Source | Recommendation (tables/columns/screens) | Module | Ver |
|---|---|---|---|---|---|---|
| **S-001** | **BLOCKER** | A barcode must resolve to a **packaging level**, not just an item. Scanning a case must add a case | GS1 GTIN allocation rules (a different packaging level is a different GTIN) | `warehouse_item_barcodes`: add `gtin` (normalised GTIN-14), **`uom_id` NOT NULL**, **`pack_quantity` NOT NULL**, `packaging_level` (EACH·INNER·CASE·PALLET), `is_variable_measure`. Prior set's `wms_item_barcodes` (`:1142`) has none of these — a case scan books 1 EA | base | **v1** |
| **S-002** | **BLOCKER** | Parse GS1 element strings: AI table, fixed vs variable length, FNC1/`<GS>` separator | GS1 General Specifications | A **scan-resolution service** in `warehouse-base` returning a structured `{gtin, lot, serial, expiry, sscc, quantity, …}`. Every scan surface calls it; nothing parses barcodes inline | base | **v1** |
| **S-003** | MAJOR | GTIN-8/12/13/14 are the same product with different lengths | GS1 | Normalise to GTIN-14 on write, validate the check digit, index on the normalised form. Otherwise UPC-A and EAN-13 of one product are two items | base | v1 |
| **S-004** | **BLOCKER** | A **logistic unit** (pallet/carton in transit) must be identifiable and movable as one thing | GS1 SSCC; EPCIS AggregationEvent | `warehouse_licence_plates` (`lpn`, `sscc`, `parent_lpn_id`, `status`, `current_location_id`) + `warehouse_lpn_contents`. Movements may reference `lpn_id`. **Schema v1**, full aggregation UI v1.1 | base | **v1** (schema) |
| **S-005** | MAJOR | SSCC allocation needs the GS1 company prefix, extension digit, serial reference and check digit | GS1 | `warehouse_gs1_settings` (company prefix, per-key serial counters) + an allocator. Not derivable later for labels already printed | base | v1.1 |
| **S-006** | MAJOR | Locations and parties need a **global** identifier for EDI/EPCIS | GS1 GLN | `gln` on `warehouse_warehouses`, `warehouse_locations`, and the party record. One nullable column each, now | base | v1 |
| **S-007** | **BLOCKER** | The ledger must be able to answer **what / when / where / why** | EPCIS 2.0 (ISO/IEC 19987, *unverified*) | On every movement row: `event_at` (physical), `recorded_at` (system), `posting_date` (accounting), `event_tz_offset`; `read_point_location_id` **and** `biz_location_id`; **`biz_step`** and **`disposition`** as two separate enums (never one `status`); `biz_transaction_ref`. Prior set collapses all of this into one `transaction_date` + one `stock_status` (`:1899`, `:1967`) | base | **v1** |
| **S-008** | MAJOR | Kitting/repack/decant destroys lot genealogy | EPCIS TransformationEvent | `warehouse_transformations` + `warehouse_transformation_inputs/outputs`. Without it a recall stops at the kit boundary | base | **v1** (schema) |
| **S-009** | MAJOR | Emit/receive EPCIS 2.0 events (JSON-LD, REST capture & query) | pharma DSCSA, EU FMD, large retail | An `warehouse-adapter-epcis`. Only possible if `S-007` and `S-008` land in v1 | adapter | v3 |
| **S-010** | MAJOR | RFID/EPC reads | EPC Gen2 / ISO 18000-63; India UHF 865–867 MHz (*unverified*) | `epc` on serial and LPN; a reader-event ingestion endpoint that is idempotent by `(epc, read_point, event_at)` | base+adapter | v2 |
| **S-011** | MAJOR | Compliance payloads and EDI need standard unit codes | UN/CEFACT Rec 20; GST UQC list | `warehouse_uoms`: add `unece_rec20_code`, `gst_uqc_code`. Two columns; without them every integration hand-maps and the IRP rejects invoices | base | **v1** |
| **S-012** | **BLOCKER** | Quantities must be stored in a **base** unit, not in the transaction's unit | practice; ICDS/Ind AS quantitative records | Every movement row carries `quantity`, `uom_id` **and** `base_quantity`, `base_uom_id`, `conversion_factor_applied`. Conversion factors are corrected over time; re-deriving history with today's factor silently restates the stock account | base | **v1** |
| **S-013** | **BLOCKER** (segment) | Catch-weight goods: the priced quantity and the counted quantity are different units | meat, cheese, chemicals, metals; GS1 AI `(310n)` | `secondary_quantity` + `secondary_uom_id` on movement and position, and a `is_catch_weight` item flag. Retrofit is impossible: the weights were never captured | base | **v1** (schema) |
| **S-014** | MAJOR | Variable-measure trade items (GTIN indicator 9 + embedded weight/price) | GS1 | Parse and route to `secondary_quantity` | base | v2 |
| **S-015** | MAJOR | Partner integration document set | X12 856/940/943/944/945/947/846; EDIFACT DESADV/RECADV/INVRPT | A **document-shaped integration port** with CSV and REST adapters first, EDI mapper third. **ASN inbound (856/DESADV) with SSCC receiving is the highest-value single item** | base + 3pl | v1.1 (ASN, 846-as-API) / v2 (EDI) |
| **S-016** | MAJOR | Structured location identification | e-way bill needs PIN, state code, distance; EDI needs GLN | `warehouse_warehouses`: `address_line*`, `city`, `state_code` (GST 2-digit), `pincode`, `country_code`, `latitude`, `longitude`, `gln`. Prior `wms_warehouses` (`:141`) has no structured address usable for compliance | base | **v1** |
| **S-017** | MINOR | 2D codes will carry URIs, not digits | GS1 Digital Link; the "Sunrise 2027" initiative (*a target, not a mandate, as of cutoff*) | `barcode_format` enum must include `GS1_DIGITAL_LINK`; the scan resolver must accept a URI | base | v1 (enum) / v2 (parse) |
| **S-018** | MAJOR | Serial numbers are **not globally unique** across manufacturers | practice | Unique on `(item_id, serial_number)`, not on `serial_number` alone — prior set has `uk_wms_serial_numbers UNIQUE (serial_number)` (`:2102`), which rejects a legitimate second manufacturer's identical serial forever | base | **v1** |
| **S-019** | MAJOR | Label templates need symbology, DPI and printer language | practice | See `S-087`. `wms_label_templates` (`:3393`) has no rendering target | base | v1.1 |
| **S-020** | MINOR | Returnable transport items (pallets, crates, cylinders, totes) are assets with deposits | GS1 GRAI/GIAI | `warehouse_returnable_assets` + a balance per customer. Common in beverages, gases, auto logistics | base | v2 |

## Register B — statute

| # | Sev | Requirement | Source | Recommendation | Module | Ver |
|---|---|---|---|---|---|---|
| **S-021** | **BLOCKER** (`DECIDE`) | The India statutory pack has no module to live in | the brief's four modules are core + app + **vertical** adapters + 3PL; none is a jurisdiction | **Add `warehouse-india`** with its own band, mirroring `accounting-india`. Decide before `V900000` | topology | **v1** |
| **S-022** | **BLOCKER** | A transfer between GSTINs is a **supply**; the same physical move is two different legal documents | CGST Sch. I + Rules r.28 (*numbers unverified*) | `warehouse_warehouses.legal_entity_id`, `tax_registration_id`, `state_code`; transfer `document_kind` **derived** from the pair, never chosen by a user | base + india | **v1** |
| **S-023** | **BLOCKER** | Delivery challan as a first-class document kind | CGST Rules r.55 (*unverified*) | `DELIVERY_CHALLAN` document kind + print; used for same-GSTIN transfers, job work, approval sales, SKD/CKD | india | **v1** |
| **S-024** | **BLOCKER** | E-way bill data and lifecycle | CGST Rules r.138 (*thresholds/validity as of cutoff — re-verify*) | The field list in §2.1; `warehouse_eway_bills` (EWB no., Part-A/Part-B state, validity, vehicle, transporter, distance, consolidated ref, cancellation). **Transplant the prior `ComplianceProviderPort` design** (`Competitive_Gap_Analysis:240`) rather than rebuilding, and fix its known null-Part-B defect (`Outbound_Flow_Gap_Review:86`) | india | v1 (data) / v1.1 (gateway) |
| **S-025** | MAJOR | The inter-state stock-transfer invoice needs an **IRN** | e-invoice mandate (*₹5 cr as of cutoff*) | Route the transfer invoice through the same IRP adapter as a sales invoice. A design that calls transfers "internal" ships an invalid document | india | v1.1 |
| **S-026** | **BLOCKER** | Job work: challan, 1-year / 3-year clock, ITC-04, job worker as a stock location | CGST s.143, Rules r.45/r.55 (*unverified*) | `warehouse_job_work_challans` + lines with `quantity_sent` / `quantity_returned` / `due_date`; job worker premises as a **location we do not own but hold stock at**. Accounting's own set makes the identical argument for `acc_job_work_challans` (`DATA-MODEL.md:489`) — **do not build it twice; decide which side owns it** | india | **v1** |
| **S-027** | **BLOCKER** | The statutory **stock account** report | CGST s.35/36, r.56 (*unverified*) | A per-GSTIN, per-period register in the mandated categories (opening · receipts · supplies · lost · stolen · destroyed · written off · gift · free sample · closing; separately raw material, finished, scrap, wastage; plus goods at job worker). Not a generic movement grid | india | v1 |
| **S-028** | **BLOCKER** | Adjustment reasons are a **tax classification**, not a note | CGST s.17(5)(h) ITC reversal (*clause letter believed correct*) | `warehouse_reason_codes` — closed catalogue, FK from every adjustment, with `itc_treatment`, `gl_account_purpose`, `requires_approval`, `statutory_category`. Prior set has `reason_code VARCHAR(50)` free text (`:1962`) | base | **v1** |
| **S-029** | MAJOR | ITC reversal amount needs the original credit | s.17(5)(h) | A write-off movement must be able to reach the receipt that brought the lot in — i.e. lot/layer linkage (`S-070`) | base + india | v1.1 |
| **S-030** | MAJOR | Scrap is inventory, its sale is a supply, and TCS applies | Income-tax s.206C(1) (*rate 1%, as of cutoff*) | A scrap condition state with its own location and value; scrap sale as a normal outbound with an HSN and a TCS flag | india | v1.1 |
| **S-031** | MAJOR | HSN changes over time; history must not move | GST invoicing | `hsn_code` on the item **and snapshotted** on the movement/document line | base | **v1** |
| **S-032** | MAJOR | Goods sent on approval / sale or return | CGST r.55; deemed supply at six months | A stock state "at customer, unsold, still ours" — the same owner/location mechanism as consignment (`S-064`, `S-069`) | base | v1.1 |
| **S-033** | MAJOR | MRP, net quantity, country of origin are **per pack run** | Legal Metrology (Packaged Commodities) Rules 2011 (*unverified*) | `mrp`, `net_content`, `net_content_uom`, `country_of_origin`, `pack_month_year` on the **lot**, with item-level defaults | base | **v1** |
| **S-034** | MINOR | A weighbridge/scale is a legal instrument | Legal Metrology Act 2009 verification & stamping | `warehouse_devices` (see `S-088`) with `verification_certificate_no`, `verified_until`; a weighing that used an out-of-verification instrument is flagged | base | v2 |
| **S-035** | **BLOCKER** (segment) | Pharma: licences, mandatory batch/expiry, Schedule H1 register, despatch blocked to unlicensed/expired parties | Drugs & Cosmetics Act 1940 / Drugs Rules 1945 (*rule numbers unverified*) | `regulatory_class` on the item forcing batch tracking; `licence_number`/`licence_expiry`/`licence_type` on party and on our own entity; a hard despatch guard | adapter-pharma | v2 |
| **S-036** | MAJOR | Pharma serialisation + aggregation for export barcoding and for DSCSA/EU FMD comparison | DGFT export barcoding public notices; US **DSCSA** (Title II, DQSA 2013) — *the brief's "DSCPA" is a typo*; EU FMD | Depends entirely on `S-004`, `S-007`, `S-008` existing in v1. The event export itself is `S-009` | adapter-pharma | v3 |
| **S-037** | MAJOR | Regulated receipts are **quarantined by default** | GDP/GMP practice; CDSCO | `disposition = QUARANTINE` on receipt for regulated classes, released only by a QA role. Different from `wms_inventory.quantity_quality_hold`, which is a bucket, not a gate | base | v1.1 |
| **S-038** | MAJOR | Food: FSSAI licence on every party; **best-before ≠ use-by** | FSS Act 2006; Labelling & Display Regs 2020 | `best_before_date` **and** `use_by_date` as separate lot columns with different despatch rules; FSSAI licence + expiry on party | base + adapter-food | v1 (columns) |
| **S-039** | **BLOCKER** (segment) | Minimum remaining shelf life on despatch, per customer | modern-trade contracts (75%/50% rules); FEFO | `min_shelf_life_percent` / `_days` on the customer or the order, enforced at allocation. FEFO alone is not enough — FEFO ships the *oldest*, which is exactly what a retailer rejects at the gate | base | v1.1 |
| **S-040** | MAJOR | Recall: trace forward and back, one-up/one-down, mock recall | FSS (Food Recall Procedure) Regulations 2017; CDSCO guidance | `warehouse_recalls` + scope by lot/serial + a **downstream trace report** (which customer got which lot) + quantity recovered + disposition. The trace is only possible if outbound movements record the lot — which requires `S-007` | base | v1.1 |
| **S-041** | **BLOCKER** (segment) | Cold chain: temperature logging, excursion, disposition decision | FSSAI Schedule 4 (*unverified*); GDP; EPCIS 2.0 sensor elements | `warehouse_sensor_readings` (bound to zone/location/LPN/shipment), `warehouse_temperature_excursions` (start, end, min/max, duration, severity) and a **QA disposition** record. Item-level `temperature_min_c/max_c` (`:949`) is a requirement with nothing measuring against it | adapter-coldchain | v2 |
| **S-042** | MAJOR | Hazmat: segregation, storage limits, SDS, transport documents | UN Model Regs / IMDG segregation; MSIHC Rules 1989; Petroleum Rules 2002 / PESO; CMVR rr.129–137 (*range unverified*) | A class×class **segregation matrix** enforced at putaway and load; per-zone quantity ceilings tied to a licence object; versioned SDS on the item; TREM card + emergency panel + class labels at despatch. The **classification block is already right** (`:955-961`) — keep it | base + adapter-chem | v2 |
| **S-043** | MINOR | Threshold-quantity reporting to the regulator | MSIHC; PESO licence conditions | A stored-quantity-vs-licence report | adapter-chem | v3 |
| **S-044** | **BLOCKER** (segment) | **Duty status is a stock dimension.** Bonded and duty-paid stock must never merge | Customs Act 1962 Ch. IX ss.57–73; MOOWR 2019 under s.65 (*section numbers unverified*) | `duty_status` (DOMESTIC·BONDED·MOOWR·SEZ·FTWZ·EXPORT_UNDER_BOND) **in the position's unique key and on every movement**; `warehouse_customs_bonds`, `warehouse_boe_references` with the warehousing-period clock; ex-bond clearance consuming identified bonded quantity; monthly customs stock statement | base (column) / adapter-customs (feature) | **v1** (column) / v2 |
| **S-045** | MAJOR | Import landed cost = duty + freight + insurance + clearing, arriving later | Ind AS 2 cost of purchase; s.145A | See `S-071` | base + accounting seam | v1.1 |
| **S-046** | MINOR | Negotiable warehouse receipts | Warehousing (Development and Regulation) Act 2007; WDRA/eNWR | Only if agri 3PL is targeted | 3pl | v3 |
| **S-047** | MAJOR | A returned **core is inventory** | auto aftermarket practice | Core as a condition state with a value, awaiting OEM return; core charge as a receivable. `wms_core_exchanges` (`:3134`) models the credit, not the stock | adapter-dealer | v1.1 |
| **S-048** | MAJOR | Recall by **VIN** | Motor Vehicles (Amendment) Act 2019 recall provisions (*section unverified*) | The issue movement must record the vehicle/asset it was fitted to, written by the services/field-service adapter. Retro-linking a year of parts issues to VINs is impossible | adapter-dealer/services | v1.1 |
| **S-049** | MINOR | Counterfeit-part control | brand protection practice | Authorised-supplier flag on item×supplier; a `SUSPECT` disposition | adapter-dealer | v2 |
| **S-050** | MAJOR | **EPR** reporting: batteries, e-waste, tyres, plastic packaging | Battery Waste Management Rules 2022; E-Waste (Management) Rules 2022; Plastic Waste Management Rules (*as of cutoff*) | An `epr_category` on the item and a quantity-by-category report per period. Pure reporting over quantities we already hold — cheap, and every auto/electronics warehouse needs it | india | v2 |
| **S-051** | **BLOCKER** | Retention: **two clocks** (8 FYs Companies Act, 72 months GST) plus per-item shelf-life-based food retention; legal hold; and 3CD quantitative details | Companies Act s.128(5); CGST s.36; Form 3CD (*clause believed 35*); FSSAI | A retention policy object, an archival tier that preserves "as at" reproduction, a `legal_hold` flag, and the **3CD quantitative statement** as a built report | base + india | v1.1 |
| **S-052** | MAJOR | Cost records for specified industries | Companies Act s.148; Cost Records & Audit Rules 2014, CRA-1 (*unverified*) | Issues must carry a cost object (job, cost centre, work order) so consumption is reportable by it | base | v2 |
| **S-053** | **BLOCKER** | The valuation engine is **constrained by statute**: FIFO / weighted average / specific identification / standard-if-approximates; **LIFO prohibited**; NRV lower-of with **reversal**; s.145A inclusive-of-duty basis for tax | Ind AS 2 / AS 2 / IAS 2; ICDS II; Income-tax s.145A | Enum excludes LIFO **and the FRD says why**; specific identification is in scope (unlike accounting's FRD-101 deferral); write-down register with reversal; a second, tax-basis value | base + accounting seam | **v1** (enum, columns) |
| **S-054** | MAJOR | The stock ledger is part of the books: append-only, corrections visible | Companies (Accounts) Rules r.3(1) proviso | No `UPDATE`/`DELETE` on movement rows; `reverses_movement_id`; enforced by trigger, not convention | base | **v1** |
| **S-055** | MINOR (`DECIDE`) | Erasure vs retention precedence | DPDP Act 2023 (*section unverified*) | One paragraph: retention beats erasure, satisfied by pseudonymising the person, never the quantity | base | v1 |

## Register C — industry structure

| # | Sev | Requirement | Source | Recommendation | Module | Ver |
|---|---|---|---|---|---|---|
| **S-056** | **BLOCKER** (segment) | Apparel/footwear: **style × size × colour matrix**, ratio/assortment packs, plan at style, transact at variant | the largest organised-retail inventory segment in India | `warehouse_styles` + `warehouse_item_variants` with `dimension_1/2/3` (size, colour, fit) and an ordered size scale; matrix grid entry; pack templates. `wms_items` is flat (`:831`) — retrofitting a variant model onto a year of flat SKUs is a migration project | base | **v1** (schema) / v2 (matrix UI) |
| **S-057** | MAJOR | Electronics: serialised, high value, DOA/RMA, IMEI | practice | Mostly covered by `wms_serial_numbers` (`:2067`) + returns. Missing: **serial-level cost** (`S-065`), IMEI as a second serial key, and high-value dual-custody picking | base | v1.1 |
| **S-058** | MAJOR | Construction: weighbridge, tare/gross/net, moisture, tolerance, bulk locations | practice; Legal Metrology verification | Two-weighing movements bound to one document; `tolerance_percent` on the item; bulk locations counted by survey, not by count sheet | adapter-bulk | v2 |
| **S-059** | MAJOR | E-commerce: single-line waves, batch/tote picking, marketplace SKU mapping, courier manifests, **returns grading** | practice | `warehouse_channel_item_refs`; returns disposition into condition states (`S-069`); manifest print (`S-087`). Wave/pick/pack base is `PRIOR-ART` (`:2631`,`:2722`,`:2921`) | adapter-ecom | v2 |
| **S-060** | MAJOR | Field service / assets: **the van is a stock location** | practice | The location model must permit a mobile location owned by a person; reserve-before-visit; return-unused-to-van. `assets/` and `field-service/` have **no parts tables at all** today | adapter-fs | v1.1 |
| **S-061** | MAJOR | Workshop parts issue is currently free text | `services/.../V40095`: *"the field is used as free-text input"* | `warehouse-adapter-services`: reserve against job card → issue on fitment with the job as cost object → **return unissued parts** → link to VIN (`S-048`) | adapter-services | v1.1 |
| **S-062** | **BLOCKER** (`DECIDE`) | Accessories already has a stock ledger (`V30130`–`V30136`) | the install | Decide **absorb vs coexist** before `V900000`. Silence picks coexist, and the group then has two stock numbers forever | topology | **v1** |
| **S-063** | MAJOR | Dealer parts counter: walk-in sale, VOR order, **lost-sale capture** | practice | Lost sale is one small table and it is the only data that ever improves a stocking policy. Supersessions (`:1203`) and interchangeability (`:1236`) are `PRIOR-ART` — keep both | adapter-dealer | v1.1 |

## Register D — valuation and the accounting seam

| # | Sev | Requirement | Source | Recommendation | Module | Ver |
|---|---|---|---|---|---|---|
| **S-064** | **BLOCKER** (`DECIDE`) | **Two systems of record for stock quantity** | `acc_valuation_entries` `:436`, `acc_stock_balances` `:507`, `acc_physical_stock_counts` + `acc_stock_journals` `:4311` vs the warehouse ledger | Write the split down: warehouse owns quantity at full grain; accounting owns value; `acc_stock_balances` becomes a projection and accounting's count/stock-journal screens **stand down** when warehouse is installed. Add that third state to the accounting design | seam | **v1** |
| **S-065** | **BLOCKER** | Specific identification is **required** here and **deferred** there | Ind AS 2 for non-interchangeable items; `ACCOUNTING-FUNCTIONAL-REQUIREMENTS.md:230` defers it | Serial/lot-level cost must survive the handover: `serial`, `lot_external_id` and `cost_basis` on the movement envelope | seam | **v1** |
| **S-066** | **BLOCKER** (`DECIDE`) | Who computes cost — the port carries `unit_cost` **and** accounting owns `acc_cost_layers` | `DATA-MODEL.md:277` vs `:434` | Recommendation: **accounting computes value**; warehouse supplies quantity, identity and the receipt-side purchase cost only. Then one FIFO engine exists, not two | seam | **v1** |
| **S-067** | **BLOCKER** | Ledger↔GL reconciliation is impossible without a handover marker | audit; every month end | `handover_id` + `posting_status` (NOT_APPLICABLE·PENDING·POSTED·REJECTED) **on the movement row**, plus a rejected-handover queue with an owner and an alert | base | **v1** |
| **S-068** | MAJOR | Warehouse must never write `acc_*` | the hash chain (`V600111`), period locks, module direction | An `ArchitectureInvariantsTest` in `warehouse-base` that fails the build on any `acc_*` / `ai.accounting*` reference. `accounting-base` already ships the pattern | base | v1 |
| **S-069** | **BLOCKER** | Stock exists **outside our four walls** and must still be on the ledger | Ind AS 2; consignment; job work; in-transit; van stock; goods on approval | Make the ledger a **double entry over locations**: `from_location_id` and `to_location_id` are both NOT NULL, with **virtual location types** (`SUPPLIER`, `CUSTOMER`, `JOB_WORKER`, `IN_TRANSIT`, `SCRAP`, `ADJUSTMENT`, `OPENING`). Then every movement nets to zero and in-transit stock is locatable. Prior set allows both to be null (`:1945-1946`), and in-transit stock is then nowhere | base | **v1** |
| **S-070** | MAJOR | FIFO needs layers **and consumptions**, AVCO needs a snapshot | Ind AS 2 | `warehouse_cost_layers` (or accounting's, per `S-066`) **plus** a consumption table; `moving_average_after` on every movement. Switching AVCO→FIFO later has no layer history to build from | base/seam | **v1** (schema) |
| **S-071** | MAJOR | Landed cost arrives after the goods | Ind AS 2 cost of purchase; s.145A | Apportionment basis per charge; retrospective layer revaluation **plus a COGS adjustment for what already shipped**; charge document → receipt movement linkage. Requires `unit_cost` to be **not write-once** at the port | seam | v1.1 |
| **S-072** | MAJOR | NRV write-down, item by item, **with reversal** | Ind AS 2 (reversal required — unlike US GAAP) | A write-down register (item/lot, NRV, basis, assessor, date, amount, reversal link) + ageing/slow-moving/obsolete candidate reports | seam | v1.1 |
| **S-073** | MAJOR | Period-end cut-off: GRNI, in-transit by Incoterm, consignment | Ind AS 2; audit | `invoice_matched` on receipts; `ownership_transfer_point` on purchase/transfer documents; the owner dimension | base + seam | v1.1 |
| **S-074** | MAJOR | Inter-branch transfer carries a **price** and a **cost** | GST r.28 valuation vs Ind AS cost | Two amounts on a transfer line: `transfer_price` (the tax document) and `unit_cost` (what follows the goods) + unrealised-profit elimination data | base + india | v1.1 |
| **S-075** | MAJOR | COGS timing is a policy, not a constant | Incoterms; revenue recognition | Configurable `cogs_recognition_point` (DISPATCH·DELIVERY·INVOICE) with a stock state per stage and an in-transit account | seam | v1.1 |
| **S-076** | MAJOR (`DECIDE`) | Negative stock policy | practice; it determines the CHECK constraint | Per warehouse / per item: `BLOCK` · `WARN` · `ALLOW`. If `ALLOW`, the valuation of the subsequent receipt must true-up the negative issue's cost. Decide before the constraint is written | base | **v1** |
| **S-077** | MAJOR | Backdated movement into a closed period | audit; the close | Blocked by `S-090`'s period lock; permitted only via an explicit adjustment in the open period with a reason code | base + seam | v1.1 |
| **S-078** | **BLOCKER** | 3PL/consignment stock **is not our asset** and must not be valued | Ind AS 2; the balance sheet | Rule stated in the FRD: `owner_type != OWN` → handed over for quantity/custody reporting only, never valued. Custody liability and insured value are separate figures on a separate report. `acc_valuation_entries` has **no owner column** today, so every movement that reaches it becomes our inventory | seam | **v1** |

## Register E — the operational surface

| # | Sev | Requirement | Recommendation | Module | Ver |
|---|---|---|---|---|---|
| **S-079** | **BLOCKER** | Opening stock import at scale | An import that carries position **and value and layers and lot and serial and owner and duty status**, with dry run, error report, a **closing-value tie-out against the source**, apply and a reconciliation certificate. Copy accounting's `P2-15` shape. Design for 200k–1M rows | base | **v1** |
| **S-080** | **BLOCKER** | Migration from Tally / Busy / Marg / Excel | Mapping profiles (item, UoM incl. alternate units, godown, party), duplicate-SKU resolution, unit-conversion validation, and an **exportable/importable profile** — a database-per-customer install means the second customer is a different database | base | **v1** |
| **S-081** | MAJOR | Cutover procedure | A documented freeze-count-load-verify runbook and a **stock freeze window** object | base | v1 |
| **S-082** | **BLOCKER** | **Restore does not exist** | `DatabaseBackupService` has 0 `restore` hits. Restore path, PITR/WAL archiving, a **restore-verification job**, stated RPO/RTO. Platform work | platform | **v1** |
| **S-083** | MAJOR | The auditor's five artefacts | Stock ledger **as at** a date (reproducible), movement audit export, adjustment analysis by reason/user/value, count history with variance, immutability evidence | base | v1.1 |
| **S-084** | MAJOR | No performance targets exist | Adopt §5.4's table into the FRD's non-functional section, and state the partition/archival strategy at design time | base | v1 |
| **S-085** | **BLOCKER** | Allocation under concurrency | State the locking discipline. Under a **generated** `quantity_available`, two concurrent allocations both pass `CHECK (quantity_on_hand >= 0)` because on-hand did not change. Decide with `S-076` | base | **v1** |
| **S-086** | **BLOCKER** | Offline / poor connectivity | Read-cached lists; **queued writes with a per-scan idempotency key**; conflicts surfaced not swallowed. Nothing in this codebase queues today | base + mobile | v1.1 |
| **S-087** | **BLOCKER** | Printing | ZPL first (EPL/TSPL/PDF after), direct-to-printer from the handheld, a **printer registry** (zone, size, DPI, media), a print-job log with **reprints flagged**, and the eleven label/document kinds of §5.7. Nothing renders labels in this codebase | base | **v1** |
| **S-088** | MAJOR | Device management | `warehouse_devices` (type, serial, assignment, status, verification for scales), device-bound long sessions, fast shared-device sign-in, shift handover, remote session kill. RF screens are a **separate screen family** from `EntityListScreen` | base + mobile | v1.1 |
| **S-089** | **BLOCKER** | The physical move the system rejected | A **discrepancy / blocked-move queue**: attempted movement, rejection reason, operator, physical reality, `PENDING_RESOLUTION` disposition, supervisor force-with-reason. Refusing the transaction does not un-move the goods | base | **v1** |
| **S-090** | MAJOR | Month-end freeze | `warehouse_stock_periods` with a lock, blocking new **and backdated** postings, explicit reopen with approval and audit event, **synchronised with the accounting period lock** | base + seam | v1 |
| **S-091** | MAJOR | Full physical stocktake | Snapshot freeze of book quantity at count start, **blind counting**, recount thresholds, multi-counter zones, printable sheets, approval before posting with variance value. Prior set has cycle counts only (`:3200`) | base | v1 |
| **S-092** | **BLOCKER** | Support impersonation | `grep -rli "impersonat"` = 0 across platform and both design sets. With consent, time-boxed, and `on_behalf_of_actor_id` **on the audit event from the first migration** | platform | **v1** (schema) |
| **S-093** | MAJOR | Per-install health signals | Movements today vs baseline, handovers stuck `PENDING`, counts overdue, negative positions, orphan allocations, unreconciled positions — all already-modelled data with no watcher | base | v1.1 |
| **S-094** | MAJOR | Training surface | `HelpButton` is `PLATFORM-PROVIDES` and needs content; a **practice/sandbox warehouse** with disposable data is not a nicety — you cannot train pickers on live stock | base | v1.1 |
| **S-095** | MAJOR | Floor-language i18n | Platform has en/hi/fr. Warehouse operators are the most language-diverse users in the suite; RF screens need Hindi and icon-first design. **RTL is absent platform-wide** and silently rules out the Gulf | base | v1.1 |
| **S-096** | MAJOR | Ledger volume and archival | A partition/archive strategy that does not break "as at" reproduction (`S-083`) or the retention clocks (`S-051`) | base | v2 |
| **S-097** | MINOR | Integration surface | API keys, webhooks, rate limits, replay — for marketplaces and client systems | base + 3pl | v2 |
| **S-098** | **BLOCKER** | Degraded-mode operation | A documented paper fallback **and a catch-up entry mode** accepting backdated movements with the true event time. Only possible because `S-007` separates `event_at` from `recorded_at` | base | v1.1 |

---

# CANNOT BE ADDED LATER — the v1 schema commitments

**The single most valuable output of this lens.** Every row below is a column, key or dimension that must
exist in the **v1 schema** even where the feature ships in v1.1/v2/v3. The test applied to each:
*if we add this in year two, can the year-one data be made correct?* Where the answer is no, the row
is here.

| # | Column / key / dimension | Table | Feature ships | Why it cannot be added later |
|---|---|---|---|---|
| 1 | **`owner_party_id` + `owner_type`** (OWN·CONSIGNMENT_IN·CONSIGNMENT_OUT·CLIENT_3PL·CUSTOMER·JOB_WORKER) **in the position's unique key and on every movement** | position + movement | v1.1 (consignment) / v2 (3PL) | Retrofitting makes every historical row implicitly `OWN`. Consignment stock received before the column existed is **already on the balance sheet** and cannot be reclassified without restating closed periods. It also changes the unique key of the hottest table in the product. The prior set's own build contract says it: *"Pre-prod = cheap now; brutal retrofit later"* (`WMS_Inbound_Corrections_Build_Contract.md:109`) |
| 2 | **`duty_status`** (DOMESTIC·BONDED·MOOWR·SEZ·FTWZ·EXPORT_UNDER_BOND) **in the position key and on every movement** | position + movement | v2 (bonded) | Bonded and duty-paid stock of one SKU **must never merge into one balance**. Once a year of movements has commingled them, no algorithm separates them, the ex-bond BoE cannot consume identified bonded quantity, and the warehouse cannot be licensed retrospectively over the mixture. Customs offence, not a data-quality issue |
| 3 | **`condition` / `disposition` as an axis separate from `biz_step`** | position + movement | v1.1 | Merging workflow state and goods condition into one `status` (as `wms_inventory.stock_status` does, `:1899`) is unrecoverable: "PICKED" and "DAMAGED" are simultaneously true and the single column silently drops one. Splitting later cannot tell which historical `DAMAGED` rows were also allocated |
| 4 | **`base_quantity` + `base_uom_id` + `conversion_factor_applied`** | every movement | v1 | Conversion factors are corrected over time. If history stores only the transaction UoM, re-deriving base quantities uses **today's** factor and silently restates the statutory stock account for closed periods |
| 5 | **`secondary_quantity` + `secondary_uom_id`** (catch weight) | position + movement | v1.1 | The weights were never captured. There is nothing to backfill from |
| 6 | **`event_at` / `recorded_at` / `posting_date` (+ `event_tz_offset`)** as three columns | every movement | v1 | One timestamp cannot be split into three afterwards. It destroys the offline replay audit (`S-086`), the degraded-mode catch-up (`S-098`), period cut-off, and EPCIS `eventTime` vs `recordTime` |
| 7 | **`read_point_location_id` + `biz_location_id`** as two columns | every movement | v2 (EPCIS) | Where a scan happened and where the goods then were are different facts. A single `location_id` has already merged them |
| 8 | **`reverses_movement_id`** + append-only enforcement (no UPDATE/DELETE) | every movement | v1 | Immutability is a claim about history. Turning it on in year two says nothing about year one, and year one is what the auditor tests. Rows already updated in place cannot be un-updated |
| 9 | **`reason_code_id` FK to a closed catalogue** with `itc_treatment` and `statutory_category` | every adjustment/write-off | v1 | Free-text reasons cannot be mapped backwards. A year of `"damaged in handling"`/`"dmgd"`/`"broken"` cannot be classified into the six statutory categories the GST stock account requires, so the ITC reversal for that year cannot be computed |
| 10 | **`cost_layer_id` on issues + a layer table with `quantity_remaining`** | movement + layers | v1.1 (FIFO) | An AVCO-only v1 keeps no layer history. Switching to FIFO in v2 has nothing to build layers from, so the change silently begins at the switch date and the opening layer set is a guess |
| 11 | **`moving_average_after`** snapshotted on each movement | movement | v1 | A backdated receipt recomputes the average. Without the snapshot there is no evidence of what the cost was on 31 March, and the year-end valuation cannot be reproduced |
| 12 | **`handover_id` + `posting_status`** | every movement | v1.1 (GL integration) | Pre-integration movements have no marker, so "does the stock ledger tie to the GL" is permanently unanswerable for the period before the seam was built — which is exactly the period the first audit covers |
| 13 | **`lpn_id`** on movements + `warehouse_licence_plates` with `parent_lpn_id` | movement + LPN | v1.1 | Pallet-level history cannot be reconstructed from item-level rows. Every recall, every EPCIS AggregationEvent and every ASN with SSCC depends on it |
| 14 | **`transformation_id`** + input/output tables | kit/repack | v1.1 | A recall that must cross a kit boundary needs the genealogy recorded **at the moment of transformation**. Nothing later can say which input lots went into which kit |
| 15 | **`uom_id` + `pack_quantity` on the barcode row** | barcodes | v1 | Scans already recorded interpreted the barcode as base units. Reinterpreting them later would restate quantities that were physically correct at the time |
| 16 | **Serial unique on `(item_id, serial_number)`**, not on `serial_number` | serials | v1 | Changing a global unique key after data exists is a migration with duplicates to resolve by hand — and the rows that were *rejected* by the wrong constraint were never recorded at all |
| 17 | **Lot columns: `manufacture_date`, `expiry_date`, `best_before_date`, `use_by_date`, `retest_date`, `country_of_origin`, `mrp`, `net_content`, `supplier_lot`, `parent_lot_id`** | lots | v1.1–v2 | Every one of these is printed on a pack that has already been put away. Nobody will re-open cartons to backfill. `parent_lot_id` in particular: a lot split/merge not recorded when it happened is invisible forever |
| 18 | **`hsn_code` snapshotted on the movement/document line** | line | v1 | HSN reclassification is retrospective in effect: reading the item master later gives the *new* code for *old* documents, and the historical GST return no longer reconciles to the system |
| 19 | **`legal_entity_id` + `tax_registration_id` + `state_code` on the warehouse** | warehouse | v1 | Without them a historical transfer cannot be classified as supply vs non-supply, so it cannot be established whether a tax invoice was legally required — for a period already filed |
| 20 | **`from_location_id` + `to_location_id` both NOT NULL, with virtual location types** | movement | v1 | If nulls are allowed, in-transit / at-job-worker / at-customer stock has no location and the ledger does not net to zero. Backfilling a null "from" is guessing |
| 21 | **`ledger_seq BIGINT` — a monotonic total order** | movement | v1 | Two movements with the same timestamp make "balance as at" ambiguous. A sequence added later cannot order the rows that already collide |
| 22 | **`idempotency_key`** unique per movement | movement | v1.1 (offline) | Replayed offline scans without it produce duplicate ledger rows. In an append-only ledger a duplicate can only be removed by a reversal, which then looks like a shrinkage adjustment forever |
| 23 | **`count_snapshot_quantity`** on count lines | count lines | v1 | Variance computed against a live quantity is not reproducible. The book figure at count time is gone the moment the next movement posts |
| 24 | **Style / variant model (`dimension_1/2/3`, size scale)** | item master | v2 (apparel) | Converting a year of flat SKUs into a style×size×colour matrix is a data-migration project with human judgement in it, not a schema change |
| 25 | **`on_behalf_of_actor_id`** on the audit event | audit | v1.1 (impersonation) | Support sessions before the column exists are indistinguishable from the customer's own actions — which voids the audit claim retrospectively for that period |
| 26 | **`gln` on warehouse/location/party; `unece_rec20_code` + `gst_uqc_code` on UoM** | masters | v1.1–v2 | Cheap now (four nullable columns). Later they are four migrations across live master data plus a re-mapping of every integration already in production |
| 27 | **`epr_category`, `regulatory_class`, `is_catch_weight`, `hazmat` block on the item** | item master | v2 | Classification of a live catalogue of 50k items is manual work nobody funds. Seeding it at item-creation time costs nothing |
| 28 | **`period_id` on the movement** | movement | v1 | Rows posted before periods existed belong to no period, so the first close has an un-closeable opening set |

**Cost of all 28 if done in v1:** roughly 30 columns, 4 small tables and 3 unique-key decisions.
**Cost if done later:** at least six of them (1, 2, 3, 16, 20, 24) are unique-key or type changes on the
two hottest tables in the product, and four (6, 9, 17, 23) are unrecoverable — the data was never
captured.

---

# §6 — Industry verdict table

Verdict is against the design **as scoped in the brief plus the prior WMS set's inheritance**. "Serves
with additions" means the ledger model does not fight the addition; "cannot serve" means a structural
change is required first.

| Industry | Verdict | Additions required, with version |
|---|---|---|
| **Automotive spare-parts distribution** | **SERVES WITH ADDITIONS** | The prior set is closest to this vertical and it shows: supersessions (`:1203`), interchangeability (`:1236`), core exchange (`:3134`), service-parts item attributes (`:1101`) are all `PRIOR-ART`. Add: core-as-inventory (`S-047`, v1.1), VIN-linked recall (`S-048`, v1.1), lost-sale capture (`S-063`, v1.1), EPR reporting (`S-050`, v2), counterfeit control (`S-049`, v2). Nothing structural |
| **Vehicle dealership parts department** | **SERVES WITH ADDITIONS** | As above plus counter sale and VOR ordering (`S-063`, v1.1). The GSTIN-per-branch work (`S-022`, v1) is mandatory here because dealer groups are multi-state by definition |
| **Workshop / service parts issue** | **SERVES WITH ADDITIONS — and it is a repair, not a build** | Today `service_entries.parts_used` is free `TEXT` (`V40095`). Needs `warehouse-adapter-services` (`S-061`, v1.1): reserve → issue with job as cost object → **return unissued** → VIN link. Also job work (`S-026`, v1) because workshops send parts out for machining and painting |
| **Accessories retail** | **SERVES WITH ADDITIONS** | Working miniature ledger already exists (`V30130`–`V30136`). The addition is a **decision** — absorb or coexist (`S-062`, v1) — plus MRP-on-lot (`S-033`, v1) because accessories are pre-packaged commodities under Legal Metrology |
| **Pharmaceutical distribution** | **CANNOT SERVE — until three v1 schema rows land** | Not a feature gap: batch/expiry alone is not pharma. It needs unit-level identity (`S-004` LPN/SSCC), the EPCIS dimensions (`S-007`), and transformation genealogy (`S-008`) — **all v1 schema**. On top: licence gating and quarantine-by-default (`S-035`, `S-037`, v2), serialisation/aggregation reporting (`S-036`, v3). Without the three v1 rows the answer stays *cannot* permanently |
| **Food & FMCG** | **SERVES WITH ADDITIONS** | Best-before vs use-by as separate columns (`S-038`, v1), **minimum remaining shelf life per customer** (`S-039`, v1.1 — FEFO alone gets stock rejected at the retailer's gate), recall with downstream trace (`S-040`, v1.1), FSSAI licence gating (`S-038`, v1.1), shelf-life-based retention (`S-051`) |
| **Cold chain** | **CANNOT SERVE** | Item-level `temperature_min_c/max_c` (`:949`) is a *requirement* with nothing measuring against it. Needs sensor readings, excursion events and a QA disposition (`S-041`, v2). The v1 cost is small — bind readings to zone/location/LPN — but the *excursion decision* is a workflow and it is v2 |
| **Apparel / footwear** | **CANNOT SERVE — and this is the largest addressable segment we are declining** | `wms_items` is a flat SKU. A style × size × colour matrix with ratio packs (`S-056`) is a **v1 schema decision**; the matrix UI is v2. Retrofit is a data-migration project with human judgement in it. If apparel is not a target market, say so in the FRD — do not leave it to be discovered |
| **Electronics (serialised, high value)** | **SERVES WITH ADDITIONS** | Serial machinery is `PRIOR-ART` (`:2067`). Add serial-level cost i.e. specific identification (`S-065`, v1), IMEI as a second key, dual-custody picking (`S-057`, v1.1) |
| **Chemicals (hazmat, catch weight)** | **SERVES WITH ADDITIONS — one of which is v1 schema** | Classification block is already correct (`:955-961`). Add catch weight (`S-013`, **v1 schema**), segregation matrix + storage limits + SDS + DG transport docs (`S-042`, v2), assay/potency on the lot |
| **Construction materials (bulk, weighbridge)** | **SERVES WITH ADDITIONS** | Weighbridge as a legal instrument (`S-034`, `S-058`, v2), two-weighing movements, tolerance and moisture, bulk locations counted by survey. Catch weight (`S-013`) is the shared v1 dependency |
| **E-commerce fulfilment** | **SERVES WITH ADDITIONS** | Wave/pick/pack/carton base is `PRIOR-ART`. Add marketplace SKU mapping, single-line wave strategies, returns grading into condition states, courier manifests (`S-059`, v2). Depends on `S-069`'s condition axis being in v1 |
| **3PL contract logistics** | **CANNOT SERVE — one column decides it** | Without `owner_party_id`/`owner_type` in the position key (**`S-064`, v1**), client stock lands on our balance sheet and our storage revenue has no cost of goods. With it, everything else — rate cards, storage/handling billing, client-scoped RBAC, client portal, 940/945 EDI — is ordinary v2 work in `warehouse-3pl`. **This is the highest leverage-to-cost row in the report: one column in v1 turns a *cannot* into a *can*** |
| **Spare-parts service for assets / field service** | **SERVES WITH ADDITIONS** | `assets/` and `field-service/` have no parts tables at all. Needs the van as a mobile, person-owned stock location (`S-060`, v1.1) — which the location model must permit from v1 |

---

# §7 — SHIP-BLOCKERS

The test applied: **would this stop us onboarding the first real customer at all**, as distinct from
losing a deal we could still bid for? Of the 36 BLOCKERs above, **eleven** are day-one.

## 7.1 Ranked — cannot sell to a first real customer without these

| # | Finding | Why it is day-one, not year-one |
|---|---|---|
| **1** | `S-064` **Two systems of record for stock** | The first customer who buys both modules gets two stock reports that disagree at the first month end, and neither team owns the difference. It is a **decision**, costs an afternoon, and until it is taken, `S-065`–`S-078` are all being designed against an imaginary architecture. Also the cheapest thing on this list |
| **2** | `S-087` **Nothing prints a label** | `grep -rli "zpl"` = 0. A warehouse that cannot print a pallet label, a shelf label and a pick list cannot receive its first pallet. This is not a v1.1 feature; it is the first hour of the first day |
| **3** | `S-089` **No recovery when the system rejects a move that physically happened** | The single defining WMS support case. Without a discrepancy queue, operators learn within a week to work around the system, and every number after that is fiction. Cheap to build, impossible to bolt on culturally |
| **4** | `S-085` + `S-076` **Allocation concurrency and negative-stock policy** | Two pickers, one unit. A generated `quantity_available` column does **not** protect against it because on-hand did not change, so `CHECK (quantity_on_hand >= 0)` never fires. Both are decisions that must be taken **before the position table's constraints are written**, not after |
| **5** | `S-079` + `S-080` **Opening stock and migration from Tally/Busy/Marg** | There is no way to onboard customer number one without loading their stock, with value, from an incumbent that exports a godown-level closing quantity and nothing else. The reconciliation certificate is what makes the customer sign off the number |
| **6** | `S-082` **Restore does not exist** | We would hold a customer's statutory stock records — part of the books under s.128 — in a system with a `pg_dump` and no executed restore path, no PITR, no verification job. Platform work, so it does not compete with warehouse engineers |
| **7** | `S-022` + `S-023` + `S-024` **GSTIN on the warehouse, delivery challan, e-way bill** | An Indian warehouse that cannot produce an e-way bill cannot move a truck. And a transfer document that cannot be classified as supply vs non-supply is a filed-return problem, not a feature gap. The prior `ComplianceProviderPort` is transplantable — the **data** it needs is what must land in `V900xxx` |
| **8** | `S-069` **The ledger must net to zero over locations, including virtual ones** | If v1 allows null `from`/`to`, in-transit stock is nowhere, consignment is nowhere, job-work stock is nowhere, and the first period end produces a balance sheet that is wrong in three directions. It is a NOT NULL decision, taken once |
| **9** | `S-028` **Reason codes as a closed, tax-mapped catalogue** | A year of free-text reasons cannot be reclassified into the six statutory categories, so that year's ITC reversal cannot be computed and the GST stock account cannot be produced. One table, one FK |
| **10** | `S-067` **`handover_id` + `posting_status` on the movement row** | Two columns. Without them, "does stock tie to the GL" is unanswerable for every movement posted before the seam was built — which is precisely the period the first audit covers |
| **11** | `S-092` **No support impersonation** | On day two the customer asks a question we cannot answer without their password or a standing admin account, and the second silently voids the audit trail. The **schema half** (`on_behalf_of_actor_id`) must land in the first audit migration or the trail is re-keyed later. Identical to accounting's `N-045` — fix it once, in the platform |

## 7.2 Not ship-blockers — they lose segments, they do not stop the first customer

- `S-044` **bonded/duty status**, `S-035`/`S-036` **pharma**, `S-041` **cold chain**, `S-056`
  **apparel** — each gates a whole segment and none gates the first customer. **But three of the four
  are only reachable if a v1 column lands**: `duty_status` (`S-044`), the EPCIS dimensions plus LPN and
  transformation (`S-004`/`S-007`/`S-008`), and the style/variant model (`S-056`). Ship the columns,
  defer the features.
- `S-053` **valuation statutes** — year-one, not day-one; but the **enum without LIFO** and the
  **specific-identification decision** are v1, because both are contradicted by the accounting FRD
  today (`ACCOUNTING-FUNCTIONAL-REQUIREMENTS.md:230`) and the contradiction must be resolved once.
- `S-086` **offline**, `S-088` **devices**, `S-091` **full stocktake**, `S-090` **period freeze** —
  all v1.1, all needed before the *second* customer, none before the first if the first is small.
- `S-021` **`warehouse-india` module** and `S-062` **accessories absorb-or-coexist** — decisions, not
  builds, and both must be taken **before `V900000` is merged**, because both determine which module a
  migration belongs to and migrations do not move cheaply between modules.

## 7.3 The seven cheapest items in the whole report

Named separately because each costs hours now and is irreversible after the migration that would have
carried it:

1. **`owner_party_id` + `owner_type`** in the position unique key — **the entire 3PL segment stops
   being *cannot serve*** (`S-064`, `S-078`).
2. **`duty_status`** in the same key — bonded warehousing likewise (`S-044`).
3. **Three timestamps instead of one** (`event_at`, `recorded_at`, `posting_date`) — makes offline,
   degraded mode, cut-off and EPCIS all possible later (`S-007`).
4. **`uom_id` + `pack_quantity` on the barcode row** — without it a case scan books one each, which is
   the most common WMS data-quality failure in existence (`S-001`).
5. **`base_quantity` + `base_uom_id`** on every movement (`S-012`).
6. **Serial unique on `(item_id, serial_number)`** rather than globally (`S-018`).
7. **`unece_rec20_code` + `gst_uqc_code` on the UoM master** — two columns that make every compliance
   payload and every EDI mapping derivable (`S-011`).

Adjacent and equally cheap: `ledger_seq`, the monotonic total order (irreversibility table, row 21), `handover_id`/`posting_status` (`S-067`),
`hsn_code` snapshot on the line (`S-031`), `gln` on warehouse/location/party (`S-006`),
`count_snapshot_quantity` (`S-091`), and `on_behalf_of_actor_id` on the audit event (`S-092`).

---

## Referred to the standards reviewer — not this lens's business

One line each, no detail, because `.claude/commands/standards-parity-checklist.md` and the `reviewer`
agent own them:

- The prior WMS design uses `metadata JSONB DEFAULT '{}'::jsonb` on `wms_items`
  (`WMS_DATABASE_DESIGN.md:861`) and elsewhere; CLAUDE.md's DATABASE CONVENTIONS say **NO JSONB**.
- `grid_column_definitions` / `filter_definitions` / `grid_preferences.default_filters` +
  `default_columns`, `COMMON_FILTER_CONFIGS` scope registration, and `CacheConfiguration.java` cache
  names will apply to every new warehouse grid.
- Web↔mobile parity (CLAUDE.md Principle #3) applies to every warehouse screen; the RF screen family
  proposed in `S-088` is a deliberate divergence from `EntityListScreen` and needs an explicit ruling.
- Migration-range discipline: `warehouse-india` (`S-021`) needs a band allocated in CLAUDE.md's MODULES
  table before its first migration.

---

## Appendix — what this lens did not do, and what to re-verify

- **It did not review a design set, because none exists.** `warehouse-issues` has no commits. Every
  score is against the prior WMS set at `classic-issues/warehouse-base/docs/**` as the inheritance, and
  against the platform and accounting checkouts as they stood on **2026-09-01**.
- It did not review competitor feature parity, the module split proof, the migration numbering, the
  grid contract, or the codebase's own standards conformance. Other lenses own those.
- It did not price or sequence anything beyond proposing v1/v1.1/v2/v3.
- **Re-verify before relying on any of these**, all of which move: the e-way bill thresholds and the
  km-per-day validity, the e-invoice turnover threshold and the 30-day reporting rule, the ITC-04
  periodicity, the HSN-digit thresholds, the DSCSA enforcement position, the Indian pharma QR scope
  beyond the top-300 brands, the EPR rules' reporting formats, and every rule/section number marked
  *unverified*. My knowledge ends **May 2026**; four months of Indian indirect-tax notifications have
  happened since, and at least one of the numbers above is probably already wrong.
- Every `grep` count quoted was run on **2026-09-01** against
  `/Users/bbhushan/work/git/workspace/classic`, `.../accounting` and `.../classic-issues`. Re-run
  before treating one as current.
