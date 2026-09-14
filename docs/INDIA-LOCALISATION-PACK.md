# India localisation pack — Warehouse

> **Current adopted amendment (2026-09-11):** [Global settings and resolved behaviour](GLOBAL-SETTINGS-DECISIONS.md) supplies defaults, scoped choices, resolved OD answers and acceptance cases. Earlier open/escalated or contradictory wording is historical where explicitly superseded there. Implement these answers; do not re-ask the same design questions.


> **Authority.** [`DECISIONS.md`](DECISIONS.md) wins over this document on module names, packages,
> Flyway bands, prefixes and the version ladder. [`reviews/R1-codebase-reality.md`](reviews/R1-codebase-reality.md)
> wins on any claim about the *existing* `classic` codebase. This document is the India **content**:
> what the rules require, which of it is schema and which is seed data, and which wave it lands in.
>
> **Primary sources.** [`reviews/R5-standards-industry-ops.md`](reviews/R5-standards-industry-ops.md) §2
> (statute) · [`reviews/R3-erp-midmarket-audit.md`](reviews/R3-erp-midmarket-audit.md) §3 (the
> schema-vs-seed split) and §1.19 · [`reviews/R4-fulfilment-3pl-audit.md`](reviews/R4-fulfilment-3pl-audit.md)
> `F-025`, `F-042`–`F-047` (the fulfilment surface) · [`IRREVERSIBLE.md`](IRREVERSIBLE.md) (the hooks) ·
> [`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md`](WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md) §6.18 (`FR-304`…`FR-329`).
>
> **`D-1`** — `warehouse-india` is a real fifth module: package `ai.warehouseindia`, Flyway
> **V540000–V549999**, table prefix **`whin_`**.
> **`D-8`** — the core is country-neutral. No GST, HSN semantics, e-way bill or MRP *rule* is
> hardcoded in `warehouse-base` or `warehouse`. The core carries only the **hooks**, and the hooks
> are v1 because they cannot be added later.
> **`§5.1 A-4`** — India ships in **two waves**. That amendment is the single most important
> instruction in this document and it is §1.

---

## Citation discipline — read before quoting anything below

Two rules, both non-negotiable, both applied throughout.

1. **No invented legal citation.** Where the rule is known and the section number is not, the rule is
   stated and the citation is marked **`UNVERIFIED`**. A confidently wrong section number in a design
   document becomes a confidently wrong comment in a migration and then a confidently wrong answer to
   an auditor.
2. **Every threshold carries its value *and* an instruction to re-verify.** The knowledge cutoff
   behind this document is **May 2026**. Indian indirect-tax thresholds move by notification, several
   times a year, and at least one number below is probably already stale. R5's own appendix says the
   same thing about the same numbers; this document does not improve on that, it repeats it.

Every claim about the `classic` codebase carries `file:line`. Every count states the command that
produced it. All `grep` counts were run on **2026-09-01** against
`/Users/bbhushan/work/git/workspace/classic`; re-run before treating one as current.

### The threshold register — re-verify every row before build

| Rule | Value held at cutoff (May 2026) | Where it is used below | Status |
|---|---|---|---|
| E-way bill consignment-value threshold, **inter-state** | ₹50,000 | §4.2 | **RE-VERIFY** |
| E-way bill threshold, **intra-state** | state-by-state; several states ₹1 lakh; some exempt intra-city | §4.2 | **RE-VERIFY — per state, and they differ** |
| E-way bill required **irrespective of value** | inter-state movement to a job worker; handicraft goods | §4.2, §5.2 | **RE-VERIFY** |
| E-way bill validity, regular cargo | 1 day per 200 km, from first Part-B entry | §4.2 | **RE-VERIFY — this number has already changed once (100→200)** |
| E-way bill validity, over-dimensional cargo | 1 day per 20 km | §4.2 | **RE-VERIFY** |
| E-way bill cancellation window | 24 hours, if goods were not transported | §4.2 | **RE-VERIFY** |
| E-way bill generation blocked | GSTIN with two consecutive periods unfiled | §4.2 | **RE-VERIFY** |
| E-invoice applicability | aggregate turnover above ₹5 crore, B2B / export / CDN; B2C out | §4.3 | **RE-VERIFY** |
| E-invoice reporting window | 30 days from document date, above ₹10 crore turnover (from 2025) | §4.3 | **RE-VERIFY** |
| Job work return window | 1 year for inputs, 3 years for capital goods | §4.4, §5.2 | **RE-VERIFY** |
| ITC-04 periodicity | turnover-dependent, half-yearly / annually around a ₹5 crore line | §5.2 | **RE-VERIFY** |
| HSN reporting digits | 4 / 6 / 8, by turnover | §5.3 | **RE-VERIFY** |
| Goods sent on approval — deemed supply | 6 months | §4.5 | **RE-VERIFY** |
| GST records retention | 72 months from the annual-return due date | §5.1, §10 | **RE-VERIFY** |
| Companies Act books retention | 8 financial years | §5.1, §10 | **RE-VERIFY** |
| TCS on scrap | 1% | §5.5 | **RE-VERIFY** |
| Warehousing bond amount | commonly 3× the duty | §7.2 | **RE-VERIFY** |
| Bonded warehousing period | 1 year general goods, extendable; interest after 90 days for some categories | §7.2 | **RE-VERIFY** |
| Warehousing services SAC | `996729`, 18% | §3.5, §9 | **RE-VERIFY — and the place-of-supply rule changed in 2023; do not state it from memory** |
| Schedule H1 register retention | 3 years | §8.1 | **RE-VERIFY** |
| Food records retention | 1 year or the shelf life, whichever is longer | §8.2 | **RE-VERIFY** |
| Packaged Commodities declaration — the parties a pack must name, and so the lot-party roles seeded in registry 11 for `whb_lot_counterparties` | manufacturer · packer · importer, beside the supplier the goods were bought from | §6 | **RE-VERIFY — the seed rows `MANUFACTURER`/`PACKER`/`IMPORTER` follow this list (`RG-006`)** |
| Treatment of on-hand stock when a site's `REGISTERED` branch moves to a branch under a different GSTIN | **not held** — a supply, a transfer of a going concern, or an amendment of the place of business; the design set cannot say which | §3.4 | **RE-VERIFY — escalated as `OD-19`. Until an adviser rules, the change is refused while the site holds stock, and the operator empties it by taxable transfers first** |

Statutory instruments named in this document, with the confidence attached to each: CGST Act
Schedule I and CGST Rules r.28 (deemed supply between distinct persons and its valuation) —
substance confident, **paragraph and rule numbers `UNVERIFIED`**; CGST Rules r.55 (delivery challan)
— **`UNVERIFIED`**; CGST Rules r.138 (e-way bill) — **`UNVERIFIED`**; CGST Act s.143 with Rules r.45
(job work) — **`UNVERIFIED`**; CGST Act s.35/s.36 with Rules r.56 (accounts and records, the stock
account) — **`UNVERIFIED`**; CGST s.17(5)(h) (blocked credit / ITC reversal on goods lost, stolen,
destroyed, written off, or disposed of by gift or free sample) — substance confident, **clause letter
believed correct, `UNVERIFIED`**; Income-tax s.206C(1) (TCS on scrap) and s.44AB with Form 3CD
(quantitative details of stock, **clause believed 35, `UNVERIFIED`**); Companies Act 2013 s.128(5)
(books), s.148 with the Companies (Cost Records and Audit) Rules 2014 (**`UNVERIFIED`**), and the
Companies (Accounts) Rules r.3(1) proviso (audit trail, **`UNVERIFIED`**); Legal Metrology Act 2009
and the Legal Metrology (Packaged Commodities) Rules 2011 — **rule numbers `UNVERIFIED`**; Customs
Act 1962 Chapter IX ss.57–73, the Warehouse (Custody and Handling of Goods) Regulations 2016, and
MOOWR 2019 under s.65 — **section numbers `UNVERIFIED`**; Drugs and Cosmetics Act 1940 with the Drugs
Rules 1945 including Schedule H1 and Forms 20B/21B — **`UNVERIFIED`**; FSS Act 2006 with the
Licensing and Registration Regulations 2011, the Food Recall Procedure Regulations 2017 and the
Labelling and Display Regulations 2020; MSIHC Rules 1989, Petroleum Rules 2002 / PESO, and CMVR 1989
rr.129–137 for dangerous-goods transport — **range `UNVERIFIED`**; Battery Waste Management Rules
2022, E-Waste (Management) Rules 2022 and the Plastic Waste Management Rules (EPR); the Warehousing
(Development and Regulation) Act 2007 and WDRA/eNWR; Ind AS 2 / AS 2 / IAS 2 and ICDS II with
Income-tax s.145A; DPDP Act 2023 — **section `UNVERIFIED`**.

---

## §1 · The two waves

### 1.1 Why there are two, and why the split is where it is

**In India, goods physically cannot move between two of a company's own premises without a
document.** A movement that is not a supply travels on a **delivery challan**; a movement whose
consignment value exceeds the threshold additionally requires an **e-way bill**, with a vehicle
number entered before the vehicle moves. A truck stopped without one is detained and penalised. This
is a licence to operate, not a feature — R5 ranks `S-022`+`S-023`+`S-024` at position **7** in its
"cannot sell to a first real customer" list precisely on that ground
(`reviews/R5-standards-industry-ops.md:1110-1124`).

The version ladder as first written put **all** of India in v2/P4. R3 and R5 both came back marking
the delivery challan, the e-way bill and the GST-aware transfer document as **v1 BLOCKERs**
(`R3` §1.19 rows 156–158, `R5` Register B `S-022`/`S-023`/`S-024`). `DECISIONS.md` §5.1 **A-4**
accepted the argument and refined it:

> **v1 / P2-IN — the documents required to move goods legally.** Delivery challan · e-way bill
> payload and generation · the GST-aware transfer document · HSN on the item · cross-GSTIN transfer
> as a deemed supply.
>
> **v2 / P4 — the statutory registers and filings.** Rule 56 stock account · ITC-04 and job work ·
> MRP and Legal Metrology · bonded / MOOWR · the regulated-goods packs.

The line between the waves is **"can the truck leave?"** Everything needed to answer *yes* is wave 1.
Everything needed to answer *what did we file last quarter?* is wave 2. A v1 that ships transfers but
no challan ships a transfer feature an Indian customer **may not legally use** — which is the same
mistake the accounting programme made and corrected: it moved India filing out of P4 into v1 after
finding that without it, v1 won **1 of 11** Indian SME segments. A-4 exists because that lesson was
paid for once already.

### 1.2 Exactly how small wave 1 is

Counted from §11 of this document, which enumerates every table:

| Wave 1 costs | Count | Where |
|---|---|---|
| New tables in `warehouse-india` | **14** | §11.1 |
| New tables in `warehouse` | **1** (`wh_transport_details`) | §11.1, §4.2 |
| New columns on existing `warehouse-base` / `warehouse` tables | **24 numbered hooks across 8 tables** — 25 physical columns, because `reason_code_id` lands on both the movement header and the line | §2.2 |
| New tables in `warehouse-base` | **0** — the hooks are columns on tables that already exist | §2 |
| Screens | challan list + detail, e-way bill list + detail, transfer document-kind derivation on the existing transfer screen, registration master | §4 |

Of the 14 tables, **3 are pure seed masters** (`whin_gst_state_codes`, `whin_hsn_codes`,
`whin_uqc_codes`), **1 is per-install master data** (`whin_gstin_profiles`, named `whin_gst_registrations` before round 4) and **5 are the
transplanted `P-044` compliance-provider stack** rather than new design. The genuinely new modelling
in wave 1 is therefore **five tables**: the challan and its lines, the e-way bill, its filed lines
and its lifecycle event log. 3 + 1 + 5 + 5 = 14.

That is the whole of it. Wave 1 is one document object, one filing object, one transport block, and
twenty-four columns.

### 1.3 The asymmetry, stated once

R3 §3.3 puts it in one line and it is the reason the split works
(`reviews/R3-erp-midmarket-audit.md:1587-1596`):

> If v1 ships the schema and none of the seed data, an Indian buyer cannot file a return from the
> product — but **every row of stock ever written is correct**, and the seed data is a quarter's
> work. If v1 ships the seed data and misses even one schema item, the product **looks compliant in
> a demo** and every branch transfer ever recorded is wrong in a way that cannot be repaired without
> re-keying the history.

A-4 sits one notch further along the same axis: wave 1 is the schema **plus** the smallest set of
documents that makes the schema usable. Wave 2 is everything that reads history.

### 1.4 The clock columns that must land with their document, not with their report

One consequence of A-4 is easy to miss and expensive to get wrong. **ITC-04 is wave 2, but the
job-work clock is wave 1.** The statutory return window runs from the *challan date*
(`FR-312`), so `whin_delivery_challan_lines.expected_return_date` and `.deemed_supply_due_date` must
exist in the migration that creates the challan. A challan row written in wave 1 without them can
never acquire a clock — the same argument the accounting set already records against
`acc_job_work_challans` (`accounting/docs/DATA-MODEL.md:489`, quoted by R3 `E-054`), and the same
shape as `FR-165`: *a threshold column with no scheduled job that reads it is a defect at the moment
it is merged* — inverted here into *a job with no column to read is unbuildable*.

The same rule applies to the approval / sale-or-return clock (§4.5) and to the bonded warehousing
clock (§7.2), whose anchor column is `duty_status` — wave 1 — even though the bonded feature is
wave 2.

---

## §2 · The core hooks that cannot be added later

**This is the section that stops someone "saving effort" by deferring all of India.**

### 2.1 The argument

`D-8` says the core is country-neutral and every India *rule* lives in `warehouse-india`. That is
correct and it is not a reason to defer the core columns, because the columns are not rules. They are
**observations about a movement that was made once and will never be made again**.
[`IRREVERSIBLE.md`](IRREVERSIBLE.md) §1 classifies them: an *additive* change is cheap whenever it is
done; a *re-keying* change costs weeks plus silent breakage; an **unbackfillable** change means the
column can be added and **cannot be populated truthfully** — *"every aggregate that crosses the
boundary becomes a lie that looks like data"* (`IRREVERSIBLE.md:36`).

`IRREVERSIBLE.md` also names the four gates. The relevant one is **`PNR-2`**: the migration that
installs the `L-2` append-only trigger on the movement tables. *After that, `UPDATE` is refused to
every actor, and a column added later is `NULL` on every pre-existing row forever, with no backfill
path* (`IRREVERSIBLE.md:293`). And `PNR-3` — the first movement posted in any install — closes
everything observational, including the whole `IRR-51`…`IRR-57` block (`IRREVERSIBLE.md:294`).

`IRREVERSIBLE.md:712` states the disposition of this whole document in one row:

> **E-way bill, delivery challan, ITC-04, the Rule 56 stock account, MRP declarations** — *additive*,
> in `warehouse-india`. `D-8` keeps the rules out of the core as data. **The hooks are irreversible
> and are already here**: `IRR-17` `company_id`, `IRR-32` tax-mapped reason codes, `IRR-42` tax-classification
> snapshot, `IRR-57` warehouse legal identity, `IRR-12` `duty_status`. **Ship the hooks, defer the
> rules.**

### 2.2 The hooks — 24 numbered rows, 8 tables, all wave 1

Each row cites its `IRREVERSIBLE.md` id rather than restating the argument, per the standing
instruction.

| # | Column(s) | Table · module | `I-` row | Gate | Class | One-line consequence of deferring |
|---|---|---|---|---|---|---|
| 1 | `company_id` | `whb_stock_movements` · base | `IRR-17` | `PNR-1` | **UB** | Historic rows get a *guessed* legal entity, and a GST return computed from guessed entities is a filing error, not a report defect |
| 2 | `warehouse_id` | `whb_stock_movements` · base | `IRR-17` | `PNR-1` | **UB** | `sequence_no` is gapless per warehouse; adding the axis later renumbers history |
| 3 | `tax_classification_code` + `tax_classification_scheme` (`HSN`) | `whb_stock_movement_lines` · base | `IRR-42` | `PNR-1` | **UB** | Reading the item master later gives the **new** code for **old** documents, so a filed return no longer reconciles to the system that produced it |
| 4 | `duty_status` | `whb_stock_movement_lines` · base **and in the `L-5` position key** | `IRR-12`, `IRR-09` | `PNR-1` | **UB** | Bonded and duty-paid stock of one SKU merge into one balance and no algorithm separates them. §7.1 |
| 5 | `reason_code_id` (header **and** line) | `whb_stock_movements`, `whb_stock_movement_lines` · base | `IRR-32` | `PNR-1` | **UB** | A year of free-text reasons cannot be reclassified into the statutory categories, so that year's ITC reversal cannot be computed and the Rule 56 account cannot be produced |
| 6–7 | `tax_treatment_code`, `statutory_category` | `whb_reason_codes` · base — **no `CHECK` on `context`** (`D-10`) | `IRR-32` | `PNR-1` | **UB** | As above; and the catalogue must stay open or `warehouse-india` cannot add a category without a base release |
| 8–10 | `state_code`; the `REGISTERED` link's `branch_id` and `effective_from`/`effective_to` | `whb_warehouses`, `whb_warehouse_branches` · base (`D-14`) | `IRR-57`, `IRR-64` | `PNR-1` | **UB** | A historical transfer **cannot be classified as supply vs non-supply**, so it cannot be established whether a tax invoice was legally required — for a period whose return has already been filed. The GSTIN and the legal entity are read through the `REGISTERED` branch at `occurred_at`, never copied onto the site |
| 11 | `tax_classification_code` (HSN/SAC) — a **string**, never an FK into a tax master | `whb_items` · base (`FR-066`) | `IRR-42` | `PNR-3` | **UB** | §5.3. No item table in this codebase has one today |
| 12–13 | `gst_uqc_code`, `unece_rec20_code` | `whb_uoms` · base (`FR-056`) | `IRR-44` | `PNR-1` | **RK** | The return carries the government's unit code, not our UoM name; a line with no UQC cannot be summarised, and the IRP rejects the invoice |
| 14–18 | `mrp`, `net_content`, `net_content_uom`, `country_of_origin`, `pack_month_year` | `whb_lots` · base (`FR-320`, `FR-095`) | `IRR-53` | `PNR-3` | **UB** | Every one is printed on a pack already put away. Nobody re-opens cartons to backfill. §6 |
| 19–24 | `from_branch_id`, `to_branch_id`, `is_taxable_supply`, `document_kind`, `transfer_valuation_method`, `transfer_price_amount` | `wh_stock_transfers` · app (`FR-305`, `FR-306`, `E-050`) | — | with the transfer table | **UB** | §3.2. `is_taxable_supply` is **frozen at creation**; re-deriving it later from today's registrations restates a filed period |

Plus **one new table in `warehouse`**, not in `warehouse-india`: `wh_transport_details` (`FR-308`,
`E-051`) — see §4.2 for why it is core and not India.

Plus **two structural facts already carried elsewhere and not re-argued here**: `owner_id` `NOT NULL`
in v1 (`D-5`, `IRR-06`), without which job-work stock at a job worker and goods-on-approval at a
customer are unrepresentable; and virtual locations existing before the first movement (`IRR-05`,
`FR-084`), without which the job-worker and customer-approval locations of §4.4 and §4.5 have nowhere
to be.

### 2.3 Two reconciliations against `IRREVERSIBLE.md`, caused by A-4

`IRREVERSIBLE.md` §4's column tables carry a **"Feature ships"** column, distinct from the gate. It
was written before A-4 and two of its cells are now stale in the *feature* direction only — the gate
in every case is still `PNR-1` and no column moves:

| Cell | Says | Should say under A-4 | Evidence |
|---|---|---|---|
| `hsn_code` on the movement line | *Feature ships: **v2** (India)* | **v1 — wave 1.** HSN is on every e-way bill line and every challan line | `IRREVERSIBLE.md:482` vs `FR-318` (v1·P0), `A-4` |
| `whb_warehouses.legal_entity_id · tax_registration_id · state_code` — since 2026-09-10, `state_code` + the `REGISTERED` link (`D-14`) | *Feature ships: **v2** (India)* | **v1 — wave 1.** The transfer document kind is derived from these. *Applied in round 4's rewrite of `IRREVERSIBLE.md` §4.5* | `IRREVERSIBLE.md:542` vs `IRR-57` (`:235`, gate `PNR-1`), `FR-080` (v1·P1), `A-4` |
| `duty_status` on the movement line | *Feature ships: **v2** (`warehouse-india`)* | **correct as written.** Column wave 1, feature wave 2 | `IRREVERSIBLE.md:474`, `FR-104` |

`COEXISTENCE.md` §5 `M6` needs the same pass: it places `whin_delivery_challans` +
`whin_transport_details` at **v2 / P4** and says so explicitly as a *correction* of R3's v1.1
(`COEXISTENCE.md:487-499`, `:558`, `:710`). A-4 is later than that correction and supersedes it —
challan and transport details are **wave 1**. See §4.2 for the separate question of whether the
transport table is `whin_` or `wh_`.

### 2.4 The one thing that is *not* a hook

`warehouse-base` must not gain a foreign key into `warehouse-india`. `D-11` forbids it in both
directions and `MODULE-INTEGRATION.md:889` already enforces the reverse by test. Since `D-14`
(2026-09-10) base holds **no registration id at all**: `whb_warehouses` has no `tax_registration_id`.
The site's registration is reached through its `REGISTERED` link in `whb_warehouse_branches`, then the
platform branch, then `whin_gstin_profile_branches`, whose foreign key points **down** at platform
branches and never into base. In a non-India install nothing on that path exists beyond the branch, and the `ArchitectureInvariantsTest`
that proves `warehouse-base` names no `whin_` table (`MODULE-INTEGRATION.md:889`) keeps it that way.

---

## §3 · GST and stock movement

### 3.1 The rule that reshapes the transfer document

A stock transfer between two establishments of the same legal entity holding **different GSTINs** —
different states, or two registrations in one state — is a **supply between distinct persons**. It is
taxable even though no money moves, no third party is involved and nothing was sold. It requires a
**tax invoice**, not a delivery challan. A transfer between two locations under **the same GSTIN** is
not a supply at all and moves on a delivery challan.

*Source: CGST Act Schedule I (supplies without consideration between distinct persons) with CGST
Rules r.28 (value of supply between distinct or related persons) for valuation, and r.55 for the
challan. Substance confident; **paragraph and rule numbers `UNVERIFIED`.***

Valuation follows the rules for a supply between distinct persons: open market value, failing that
the value of like goods, failing that cost-plus — with the practical relief that where the recipient
is entitled to **full** input tax credit, the value declared on the invoice is deemed to be the open
market value. *(Rule number `UNVERIFIED`.)*

### 3.2 Everything the rule changes

The same physical operation — a pallet on a truck from godown A to godown B — is two entirely
different legal objects depending on a fact about the two ends. R3 `E-050` calls this *"the single
most common India-specific inventory question in a multi-branch dealership, and it is unbuildable as
an afterthought"* (`reviews/R3-erp-midmarket-audit.md:1017-1035`).

| What changes | Same GSTIN | Different GSTIN |
|---|---|---|
| **Document kind** | delivery challan | tax invoice |
| **Numbering series** | challan series, per branch | invoice series, per registration — a *different* statutory series with its own GSTR-1 document-series summary |
| **Valuation** | none required; goods move at cost for internal purposes | a taxable value under the r.28 rules, and **which method was used must be recorded** |
| **Tax** | none | IGST, or CGST+SGST, charged and paid |
| **ITC** | none | the receiving registration takes credit |
| **E-invoice** | not applicable | **applicable** if the entity is above the turnover threshold — see §4.3 |
| **GL posting** | a stock-only movement | an inter-branch supply, handed to accounting as an `INTER_BRANCH_SUPPLY` source document |
| **Both branches' stock statements** | one company, two godowns | must still show the goods correctly at every instant, including in transit |

**`is_taxable_supply` must be frozen at creation.** `FR-305` states it as *derived at creation from
the two registrations and frozen*. The reason is not convenience: a registration can be surrendered,
amended, migrated or newly obtained, and a transfer re-classified three years later by re-reading
today's registrations silently restates a period whose return has been filed. Freeze the boolean,
freeze the two branch ids, freeze the valuation method and the amount, and record the document kind
as **derived, never chosen by a user** — R5 `S-022` uses exactly that phrase
(`reviews/R5-standards-industry-ops.md:938`).

### 3.3 Where GSTIN actually lives in this codebase — verified

`CLAUDE.md:148` states the rule: *"GSTIN is per-state: stored on `branches` (platform), NOT on
company."* The schema **does not fully obey it**, and a warehouse resolver that assumes it does will
read the wrong number.

Census, run 2026-09-01:

```
grep -rniE "^\s*(ADD COLUMN IF NOT EXISTS\s+)?[a-z_]*gst[a-z_]*(_number|in)?\s+VARCHAR" \
  --include="*.sql" . | grep -v "db/client\|db/test\|db/seed"
```

→ **8 GSTIN-bearing column declarations across 6 tables**:

| # | Column | `file:line` | Whose registration is it? |
|---|---|---|---|
| 1 | `branches.gst_number VARCHAR(15)` | `platform/…/V182__Add_financial_columns_to_branches.sql:7` | **ours** — the per-state registration `CLAUDE.md:148` names, indexed at `V182:18`, commented *"GST registration number (format: 22AAAAA0000A1Z5)"* at `V182:25` |
| 2 | `branches.gst_name VARCHAR(255)` | `platform/…/V182:8` | ours — legal name as per registration |
| 3 | `companies.gstin VARCHAR(15)` | `automotive/…/V10002__Create_companies_table.sql:19`, with `chk_companies_gstin` at `:45` | **ours, and it contradicts `CLAUDE.md:148`.** Never dropped — `grep -rn "DROP COLUMN.*gstin"` → 0 |
| 4 | `dealers.gstin VARCHAR(15)` | `dealer/…/V20000__Create_dealers_table.sql:11` | ours — a third candidate |
| 5 | `customers.gstin VARCHAR(15)` | `automotive/…/V10010__Create_customers_table.sql:24`, indexed `:51` | theirs — the counterparty |
| 6 | `customers.shipping_gstin VARCHAR(15)` | `automotive/…/V10072__Add_office_shipping_address_columns_to_customers.sql:29` | theirs — ship-to |
| 7 | `asset_disposals.buyer_gstin VARCHAR(15)` | `assets/…/V60160__Asset_disposal.sql:108` | theirs — scrap buyer |
| 8 | `service_entries.invoice_gstin VARCHAR(20)` | `services/…/V40180__…:18` | denormalised onto an invoice |

**Three tables carry *our own* registration, and they disagree by design.** `branches.gst_number` is
the per-state registration; `companies.gstin` and `dealers.gstin` are legal-entity-level fields that
the rule says should not exist. A fourth is missing entirely: **there is no GST state-code master and
no state-code column anywhere** —

```
grep -rn "gst_state_code\|state_code" --include="*.sql" . | grep -v "db/client\|db/test\|db/seed"
```

→ **0 results**. `branches.state` is a free-text `VARCHAR(100)`
(`platform/…/V149__create_branches_table.sql:33`), not the two-digit GST state code that Part A of an
e-way bill requires.

### 3.4 What that means for the warehouse's site model

The FRD calls the table `whb_warehouses` (`FR-079`, `FR-080`, `IRR-57`, `IRREVERSIBLE.md:327`,
`:532-543`). Two documents call it `whb_sites` (`COMPETITOR-BENCHMARK.md:214`,
`PLATFORM-DEPENDENCIES.md:114`). **`whb_warehouses` is the name in the requirement and the
irreversibility register; the two `whb_sites` mentions are a naming drift for the reconciliation pass
to fix.** This document uses `whb_warehouses` throughout.

The rules that follow from §3.3:

1. **Exactly one `REGISTERED` link at every instant, and the GSTIN is read from that branch, never
   duplicated onto the warehouse** (`D-14` item 2, `FR-079`, `E-048`). `whb_warehouses` has no
   `branch_id`. `whb_warehouse_branches` records which branch the site is registered under, and since
   when, and every tax rule reads the link at the movement's `occurred_at`. Duplication is how the
   three-way disagreement above happened.
2. **Many links, one registration.** Accessories links a warehouse to branches through a many-to-many
   bridge (`accessories/…/V30018:8`, cited in `COEXISTENCE.md:199`) with no role and no dates, and
   that is the part not to copy. *A warehouse under two tax registrations at once is still not a
   thing.* `SERVING`, `FULFILMENT` and `RETURNS` links grant visibility and let a branch draw stock. A
   `SERVING` branch under a different GSTIN draws by a taxable transfer, never by a direct sale
   (`D-14` item 3). A registration change is maker–checker and is **refused while the site holds stock
   under a different GSTIN**. Its statutory treatment is on the RE-VERIFY register above and is
   escalated as `OD-19`.
3. **`whb_warehouses.state_code` is the site's own address fact** — the two-digit GST code of the
   state the building stands in. It is distinct from the branch's free-text `state`, because the code
   does not exist anywhere in the platform today and the e-way bill needs it. It is not a copy of the
   registration: `warehouse-india`'s link validator refuses a `REGISTERED` link whose GSTIN state
   code differs from it, because an additional place of business is always in its registration's own
   state.
4. **The legal entity is not a warehouse column, and it is not `company_id` from automotive.** `D-7`
   makes standalone the reference configuration, so base cannot depend on `automotive.companies`. The
   legal entity is read through the `REGISTERED` branch's GSTIN profile, and a second validator
   refuses a link whose profile belongs to another company.
5. **`branches.branch_type` already admits `'WAREHOUSE'` and `'DISTRIBUTION_CENTER'`**
   (`platform/…/V149:61`) — so the branch side of this costs nothing.
6. **A GSTIN covers every branch in its state, as its principal or an additional place of business**
   (`RG-002`). A company holds one registration per state, so two Delhi branches share one GSTIN, and
   a profile cannot carry a single `branch_id`. `whin_gstin_profile_branches` (`V540010`) records each
   covered branch with a `place_role` of `PRINCIPAL` or `ADDITIONAL`. That set is closed by statute,
   so it is a `CHECK` under `OD-5`, not a catalogue. The rows are dated, with one current `PRINCIPAL`
   per profile and an `EXCLUDE` so a branch sits under one registration per company at a time; `gstin`
   stays unique on the profile. Platform can edit `branches.gst_number` and warehouse cannot block it,
   so the profile's `gstin` is compared with every linked branch's number on save, and a **nightly
   assertion** writes a drift row wherever they differ. `WS-173` gains a **Places of business**
   row action and modal (`D-14` item 8b).
7. **A counterparty's registration is per state too** (`RG-003`). An Indian customer has one PAN and
   one GSTIN in each state it operates in. `national_tax_id` stays the legal-entity id (PAN).
   `whb_counterparty_tax_registrations` and `whb_counterparty_addresses` (base, `V500011`, dated) hold
   the per-state GSTINs and the ship-to blocks. The challan and the e-way bill **freeze**
   `to_counterparty_tax_registration_id` and `to_counterparty_address_id`, so what was filed can be
   reconstructed from the document.

The live counter-example is worth stating because it is the exact failure §2 exists to prevent:
`accessory_warehouses` (`accessories/…/V30017__Create_accessory_warehouses_table.sql:8-31`) has **no
`branch_id`, no registration, no legal entity** — only a free-text `state VARCHAR(100)` at `:16`. An
`accessory_stock_transfers` row (`accessories/…/V30133:6-15`) therefore **cannot be classified** as
supply or non-supply by any amount of later code, and its `IN_TRANSIT` is a workflow
`status VARCHAR(20)` at `V30133:15` rather than a location, so the goods belong to no balance while
they are on the road (`E-032`, `FR-085`). That is not a hypothetical: it is a shipped module, and it
is `COEXISTENCE.md`'s cost `C5`.

### 3.5 The additional-place-of-business problem (3PL)

A 3PL warehouse must usually be declared **on the client's own GST registration as an additional
place of business** before the client can legally hold stock there. It is a client-onboarding
obligation with a certificate, an effective date and an expiry, and R4 `F-025` notes it is asked
about in every RFP (`reviews/R4-fulfilment-3pl-audit.md:927-957`).

This lands in **`warehouse-3pl` with an India-owned validation**, not in `warehouse-india` alone:
`FR-301` places `whin_client_registrations` at `3pl·india`, v2/P4. Its shape is (client owner,
GSTIN, state code, warehouse, `is_additional_place`, certificate document ref, `effective_from`,
`effective_to`) with an **expiry alert** — which under `FR-165` means the alert job, its recipients
and its report ship in the same task as the column.

Two adjacent facts, both marked **RE-VERIFY**: warehousing and storage services are taxable under
**SAC `996729`** at 18%; and **the place-of-supply rule for storage and warehousing changed in the
2023 amendments** and R4 explicitly refuses to state it from memory — *"getting it wrong means every
interstate 3PL invoice has the wrong tax head (CGST+SGST vs IGST) and a year of returns to amend"*
(`R4:934-938`). This document takes the same position. **Do not write the rating code until a tax
adviser has confirmed the rule.** Per `FR-294`, warehouse never computes the tax anyway — it emits
the SAC and the charge code on an AR envelope and accounting resolves the head.

---

## §4 · The documents

### 4.1 Delivery challan — `whin_delivery_challans`

**The rule.** Goods moved otherwise than by way of supply travel on a delivery challan: branch
transfer under one GSTIN, job work, goods on approval, exhibition stock, goods for repair, SKD/CKD
consignments, and a part sent out with a mobile technician. *(CGST Rules r.55 — **`UNVERIFIED`**.)*

**Why it is a document and not a print template.** R3 `E-049` states it plainly: the movements that
need a challan have **no invoice** to hang attributes on
(`reviews/R3-erp-midmarket-audit.md:1002-1010`). There is nothing else in the system that carries the
number, the date, the declared value, the transport block or the return clock. A print template over
a transfer cannot be numbered, cannot be cancelled, cannot be aged, and cannot be reported.

**Fields.**

| Group | Fields |
|---|---|
| Identity | `challan_number`, `challan_date` (a **`DATE`**, per `FR-327`/`P-045`), `company_id`, `branch_id` — **the site's `REGISTERED` branch at the challan date** (`D-14`), `series_id` |
| Kind | `challan_type` — a **catalogue FK**, not a `CHECK`: `BRANCH_TRANSFER`, `JOB_WORK`, `APPROVAL`, `EXHIBITION`, `REPAIR`, `SKD_CKD`, `LINE_SALES`, `OTHER` (`D-10`) |
| Ends | `from_warehouse_id`, `to_warehouse_id` nullable, `to_counterparty_id` nullable, ship-from and ship-to address blocks with **pincode and state code**; the recipient's `to_counterparty_tax_registration_id` and `to_counterparty_address_id`, **frozen** (`RG-003`) |
| Value | `declared_value`, `currency_code`, `valuation_basis` |
| Lifecycle | `status`, `cancelled_at`, `cancel_reason_code_id`, `source_document_ref` (the lineage quad) |
| Line | `item_id`, `lot_id`, `serial_id`, `quantity`, `uom_code`, `gst_uqc_code` **snapshotted**, `tax_classification_code` **snapshotted**, `unit_value`, `taxable_value` |
| **Return clock — wave 1, per §1.4** | `expected_return_date`, `deemed_supply_due_date`, `quantity_returned` (maintained), `closed_at` |

**Numbering.** Its own series, **per branch** (the site's `REGISTERED` branch at the challan date), gapless. It does **not** get its own sequence table:
`P-046` establishes that `warehouse-base` owns the number-series mechanism
(`reviews/R6-prior-art-triage.md:1094-1100`) — a locked counter row, following the one working
gapless precedent in this repo (`assets/V60014:2-9` + `AssetTagSequenceRepository.java:19-27`), not
the scan-based `SequentialCodeGenerator` that R1 `C-019` records as explicitly not gapless.
`warehouse-india` registers a series **kind**; it does not build a second allocator.

**Print layout.** A challan is a physical document that travels with the goods, in triplicate by
convention (consignee / transporter / consignor). It needs: both parties' names, addresses and
GSTINs, the challan number and date, the HSN and description per line, quantity with UQC, taxable
value and tax where charged, the place of supply, the transport block, and a signature panel. This is
the first real consumer of the **v1 templated document printing** that `A-2` moved into v1/P2 —
which matters, because `grep -rli "zpl\|escpos\|dymo"` across all Java and TypeScript returns **0**
(`DECISIONS.md` §5.1 `A-2`); there is no document or label rendering anywhere in this codebase today.

**Screens.** A challan list grid with `grid_identifier`, filters and export; a challan detail/view
modal; a "generate challan" action on the transfer and on the job-work despatch; a cancellation
action with a reason from the catalogue. Per `D-13`, each has a mobile counterpart in the same task —
and per `C-044`, `mobile/src/components/common/ListHeader.tsx:210-218` supports
`type?: 'dropdown' | 'text'` filters but **not date filters**, which is a real constraint on a
challan list whose primary filter is a date range.

**Registry cost.** One `COMMON_FILTER_CONFIGS` scope in
`platform/frontend/src/utils/filterUtils.ts` and one cache name in `CacheConfiguration.java` per
grid. Computed 2026-09-01:
`awk 'NR>346' platform/frontend/src/utils/filterUtils.ts | grep -cE '^  [A-Z][A-Z0-9_]*: \{'` →
**213** scopes; `grep -cE '^\s+"[a-zA-Z]' .../CacheConfiguration.java` → **235** cache-name lines.
(`IRREVERSIBLE.md:719` computed 211 and 231 the same day; the tree moves under you — see
`D-10`'s corollary, which is why the ratchet is *"zero commits to `warehouse-base`"* and never
*"zero commits to `platform`"*.)

**What exists today.** Nothing. The census:

```
grep -rn "CREATE TABLE[^;]*challan" --include="*.sql" -i . | grep -v "db/test\|db/client"
```

→ **exactly one table**, `services/…/V40042__Create_replacement_handovers_tables.sql:111`,
`replacement_challans` — and it is a **traffic-violation** challan: `place_of_violation VARCHAR(500)`
at `:116`, `fine_amount` at `:119`, `payment_status ∈ (PENDING, PAID_BY_CUSTOMER, PAID_BY_COMPANY,
WAIVED)` at `:132`. The word "challan" in this codebase means a traffic fine. The only *delivery*
challan is a **customer document type seed row** —
`dealer/…/V20376__create_customer_document_types_table.sql:63`:
`('CHALLAN', 'Delivery Challan', 'Delivery Challan', 19, true)` — i.e. a slot to upload a PDF someone
else produced.

### 4.2 E-way bill — `whin_eway_bills`

**The rule.** Required for the movement of goods where the consignment value exceeds the threshold —
**₹50,000** inter-state, with **state-specific intra-state thresholds that differ**, several states
setting ₹1 lakh and some exempting intra-city movement — and required **irrespective of value** for
inter-state movement to a job worker and for handicraft goods. *(CGST Rules r.138 and state
notifications — **rule number `UNVERIFIED`; every threshold `RE-VERIFY`**.)*

**Part A / Part B, and why the split is behavioural, not cosmetic.**

- **Part A** is generated by the consignor from the document: parties, value, HSN, quantity, UQC.
- **Part B** carries the vehicle. It **may be filled later and must be filled before the vehicle
  moves.**
- **Validity runs from the moment Part B is first entered** — 1 day per 200 km for regular cargo,
  1 day per 20 km for over-dimensional cargo — and is extendable in transit. **`RE-VERIFY`: this
  number has already moved once (100 km → 200 km).**
- **Cancellation** is permitted within **24 hours** if the goods were not transported. **`RE-VERIFY`.**
- A **consolidated e-way bill** covers multiple consignments in one vehicle.
- **Generation is blocked** for a GSTIN that has not filed returns for two consecutive periods —
  which means "generate" has a *failure mode that is not our bug* and must surface as such.

The prior implementation shipped a live defect on exactly this seam: a null Part B sent to NIC
producing a cryptic gateway rejection (`R5:311`, citing
`WMS_Outbound_Flow_Gap_Review.md:86`). `FR-309` requires that defect to be **fixed rather than
reproduced**.

**Which movements need one, and which do not.**

| Movement | Needs an e-way bill? |
|---|---|
| Inter-state branch transfer, value above threshold | **Yes** — and it is also a tax invoice (§3.1) |
| Intra-state branch transfer above the state threshold | **Yes**, on a delivery challan |
| Intra-state transfer below the state threshold | **No** — but the challan is still required |
| Despatch to a job worker, **inter-state** | **Yes, irrespective of value** — `RE-VERIFY` |
| Despatch to a job worker, intra-state | threshold applies |
| Sales despatch above threshold | Yes |
| Goods on approval | Yes above threshold, on a challan |
| Movement **within one premises** — bin to bin, zone to zone, putaway, pick | **No.** No public road, no document |
| A stock-status change in place (quarantine, release, damage) | **No.** `FR-103` makes it a balanced two-line movement at the **same location** — nothing moves |
| Adjustment, count variance, write-off | **No** |
| Non-motorised transport | Exempt — `RE-VERIFY` |

That table is the reason `whin_eway_bills` hangs off a **document**, not off a movement: most
movements never need one, and the ones that do need one *per consignment*, not per line.

**Fields, and where each comes from.** R5 tabulates this and marks what the prior art was missing
(`reviews/R5-standards-industry-ops.md:288-306`):

| EWB field | Source | Held where in our design |
|---|---|---|
| Supply type and sub-type (supply / export / job work / SKD-CKD / line sales / recipient not known / **own use** / exhibition) | the movement's reason | `whin_delivery_challans.challan_type` + `whb_reason_codes` |
| Document type, number, date | the challan or the transfer invoice | `whin_eway_bills.source_document_*` |
| From GSTIN, place, **pincode**, state code | the warehouse's branch registration | `whb_warehouses` (§2.2 rows 8–10) |
| To GSTIN, place, pincode, state | destination warehouse or counterparty | challan ship-to block |
| Per-line **HSN**, description, quantity + **UQC**, taxable value, tax rates | item and UoM masters, **snapshotted** | `whin_eway_bill_lines` |
| Transport mode (road / rail / air / ship), transporter GSTIN or **TRANSIN**, document number and date | carrier | `wh_transport_details` |
| Vehicle number and type (regular / over-dimensional) | dispatch | `wh_transport_details` |
| **Approximate distance** | PIN-to-PIN | `wh_transport_details.approximate_distance_km` — **and it drives validity**, so it is not optional decoration |

**Why the transport block is `wh_`, not `whin_`.** `FR-308` places transport details at module
`base·app`, v1, *"all columns optional at the core; a localisation rule makes them mandatory"*.
`COEXISTENCE.md:491` and `:558` place `whin_transport_details` in `warehouse-india` at v2. This
document follows `FR-308` and `E-051`, for a `D-8` reason: **a vehicle number is not an Indian rule.**
Every jurisdiction's carrier has a vehicle, a consignment note and a distance; what is Indian is the
*obligation* to file them, and that obligation is the `whin_eway_bills` row. Keeping the block in
`warehouse` is also what lets a future `logistics` module read it without depending on
`warehouse-india`, which `G-013`'s five-relocatable-objects rule (`FR-199`) requires. **This is a
divergence from `COEXISTENCE.md` §5 `M6` and should be recorded there in the reconciliation pass, not
resolved silently in a migration.**

**`whin_eway_bill_lines` is a snapshot, not a view.** What was *filed* is what you defend three years
later. Re-deriving the payload from the challan after an HSN reclassification or a lot correction
produces a payload that never existed. Same reasoning as `IRR-42`.

**Numbering.** The EWB number is issued by the portal; we store it. What we own is our own request
correlation id and the idempotency key, so a retried generation cannot produce two live bills for one
consignment (`L-9`'s pattern, `(source_system, idempotency_key)` unique, key never server-generated).

**API / GSP integration surface.** `P-044` is transplanted rather than rebuilt
(`reviews/R6-prior-art-triage.md:1061-1081`): provider, per-provider environment, credential
**specification**, encrypted credentials, auth session, compliance document, and an API log. Three
constraints carried as **non-goals**, not features, because the prior art shipped them as defects:

1. **Raw request and response bodies of compliance calls are never stored unencrypted.** The prior
   `scc_compliance_api_logs` was *designed* to store them — including auth calls carrying client
   secrets and NIC passwords — in clear, undermining an otherwise correctly encrypted credential
   design. It also had **no index on `created_at`**, so any retention purge is a full scan.
2. **No demo or test controller may trigger a real statutory filing.** `ComplianceDemoController`
   could trigger real IRN and EWB filings from a minimal demo body with random source-document ids,
   and it shipped in production code.
3. **A schema-only statutory flow is a compliance claim we cannot honour.** IRN cancellation and EWB
   extension shipped as tables with no repository and no service and were deleted as orphans. Build
   them properly or leave the tables out. In this design, **Part-B update and cancellation are wave
   1** because you cannot legally leave a wrong bill live; **extension and consolidation are wave
   2** (`FR-309`).

**What exists today.** Two artefacts, no capability.

```
grep -rniE "\bewb\b|eway|e_way_bill|way_bill|waybill" --include="*.sql" --include="*.java" \
  --include="*.ts" --include="*.tsx" .
```

→ 21 files, of which **two are real** and the rest are `gateway`, `oneWay` and `sideways`:

- `platform/frontend/src/lib/status-utils.ts:213-224` carries a complete GST-compliance status
  vocabulary — `IRN_GENERATED`, `EWB_GENERATED`, `PENDING_IRN`, `PENDING_EWB` — under a comment
  reading *"Handle GST compliance document lifecycle (complianceStatus / irnStatus / ewbStatus)"* at
  `:207-211`. **Nothing anywhere produces those values**:
  `grep -rn "EWB_GENERATED" --include="*.ts" --include="*.tsx" --include="*.java" --include="*.sql" .`
  → 2 hits, both the badge definition itself. It is residue of the deleted `supply-chain-core`
  module — the same deletion that left the `wms_*` / `scc_*` permission exclusions `D-3` warns about.
- `dealer/…/V20376__create_customer_document_types_table.sql:57`:
  `('EWAY', 'E-way Bill', 'E-way Bill', 13, true)`, with labels at
  `dealer/frontend/src/i18n/locales/en/customerDocument.json:54` and
  `.../hi/customerDocument.json:54`. Again: a slot to file the PDF, not a generator.

**Today, this product's entire e-way bill capability is a green badge with no producer and a filing
cabinet.**

### 4.3 E-invoice where it touches stock

E-invoicing applies above an aggregate-turnover threshold — **₹5 crore** at cutoff, having stepped
down from ₹500 crore — to B2B supplies, exports and credit/debit notes; B2C is out. An IRN must be
obtained from an IRP before the invoice is valid, and above a higher turnover (**₹10 crore**, from
2025) the document must be reported within **30 days** of its date. **All three numbers
`RE-VERIFY`.**

Warehouse touches this in **exactly one place, and it is easy to miss**: the inter-state stock
transfer of §3.1 raises a **tax invoice**, and that invoice is a B2B document that needs an IRN.
*A design that treats transfers as "internal" ships a document that is legally invalid* (`S-025`,
`FR-311`).

Consequences:

- The transfer invoice routes through **the same IRP adapter as a sales invoice**. There is not a
  second e-invoicing path for transfers.
- **Accounting raises the invoice, not warehouse.** `D-6` and `FR-294` are unambiguous: warehouse
  emits an `INTER_BRANCH_SUPPLY` source-document envelope through accounting's port and accounting
  resolves the number, the tax, the place of supply and the IRN. Warehouse holds the **stock** side
  and the challan; it never numbers a tax invoice.
- Where **no accounting module is installed** (`D-7` standalone), the same envelope exports and the
  transfer is marked invoiced externally. The port shape does not change.
- The IRN, acknowledgement number and signed QR are stored in `whin_compliance_documents`, and the
  document is **locked** once the IRN is issued, with a cancellation window. That lock is a *warehouse
  concern* even though the invoice is accounting's, because the underlying movement must not be
  reversed behind a filed IRN — `L-8`'s period lock and this lock are two different gates and both
  must fire.

Wave: the columns and the compliance-document store are **wave 1** (they are the same store the
e-way bill uses); the IRP round-trip for transfers is **wave 2 / P4** with `FR-311`.

### 4.4 Job-work challan and the return window

**The rule.** Inputs sent to a job worker must be returned, or supplied from the job worker's
premises, within **one year**; capital goods within **three years**. Failing that, the sending is
**deemed a supply on the date the goods were sent**, with interest. The movement travels on a
delivery challan and the quantities out and back are reported in **ITC-04**. *(CGST Act s.143 with
Rules r.45 and r.55 — **section numbers `UNVERIFIED`**; windows and ITC-04 periodicity
**`RE-VERIFY`**.)*

**Why this matters more in this suite than it looks.** R5 puts it bluntly: *every workshop that sends
a part out for machining, every dealer that sends a body panel for painting, every accessories
retailer that sends material for embroidery is doing job work*
(`reviews/R5-standards-industry-ops.md:340-347`). Body-shop panels out for painting, engines for
reboring, batteries for refurbishment — all job work (`E-054`).

**The modelling, and the two things it forces.**

1. **The job worker's premises is a stock location we do not own.** Goods leave to a `JOB_WORKER`
   virtual location (`FR-084` seeds exactly that type) **with `owner_id` unchanged** — still ours.
   This is the same mechanism as consignment and as goods-on-approval, and it is why `D-5` puts
   `owner_id` `NOT NULL` in v1 in every install. Without it, job-work stock is either invisible or
   wrongly de-recognised.
2. **The clock is measured from the challan date**, so the columns land in wave 1 (§1.4). A
   `@Scheduled` job ages open challan lines and raises the obligation *before* it becomes a deemed
   supply — and per `FR-165`, that job, its notification recipients and its report ship **in the same
   task as the column**, not later.

**There is one challan table.** `FR-313` is explicit: warehouse's `whin_delivery_challans` **is** the
job-work challan, with `challan_type = JOB_WORK`. The accounting set's parallel
`acc_job_work_challans` (`accounting/docs/DATA-MODEL.md:489`) is reduced to a view over it or deleted.
**This is gated on `OD-1`** — the reciprocal accounting edits — and must not be built twice on the
strength of this document alone.

**Fields beyond the base challan:** `job_worker_counterparty_id`, `job_work_type ∈ {INPUTS,
CAPITAL_GOODS}` (a catalogue, not a `CHECK`), `expected_return_date`, `deemed_supply_due_date`,
`quantity_sent`, `quantity_returned`, `quantity_scrapped_at_job_worker`, `waste_treatment`,
`closed_at`. Returns are recorded against the challan **line**, not the header, because partial
returns across multiple dates are the normal case and a header-level counter cannot age them.

**Print and screens.** The job-work challan prints as a delivery challan with the job-work
declarations; the screens are the challan screens plus an **open-job-work ageing grid** sorted by
`deemed_supply_due_date` — the screen that stops the liability, and the direct analogue of `F-044`'s
NDR queue (§9.2): *a clock nobody is watching* (`R4:1517`).

### 4.5 Goods sent on approval / sale or return

A challan type in wave 1, a feature in wave 2. Goods at a customer, unsold, **still our asset**, with
a deemed supply at **six months** (`RE-VERIFY`). It is the same owner-and-location mechanism as job
work and consignment (`S-032`, `FR-322`): an `APPROVAL` challan to a `CUSTOMER`-type location with
`owner_id` unchanged, and `deemed_supply_due_date` on the line. **No new table** — which is the point:
`owner_id`, the virtual-location types and the challan clock columns being wave 1 is what makes this
feature purely additive later.

---

## §5 · The registers and the filings — wave 2

### 5.1 The stock account the law actually requires (Rule 56)

**The rule.** Every registered person other than a composition dealer must keep a **true and correct
account of goods**: opening balance, receipts, supplies, **goods lost, stolen, destroyed, written off,
or disposed of by way of gift or free sample**, and closing balance — **separately for raw materials,
finished goods, scrap and wastage** — plus, where relevant, the details of goods lying with a job
worker. Records are retained for **72 months from the due date of the annual return**. *(CGST Act
s.35/s.36 with Rules r.56 — **rule numbers `UNVERIFIED`**; retention **`RE-VERIFY`**.)*

**Two structural consequences, both from R5 (`:349-367`).**

1. **It is a shipped report in the mandated shape, per registration and per period — not a movement
   grid with filters.** The opening / receipts / supplies / losses-by-category / closing skeleton is
   the whole point; a generic grid cannot produce it because the categories are statutory, not
   user-chosen (`S-027`, `FR-314`). Same lesson as `E-052`'s godown-wise stock statement: *"a grid
   with a warehouse dropdown is not this report — the opening/inward/outward/closing shape is the
   whole point"* (`R3:1053-1057`).
2. **The adjustment reason code is a tax classification, not a note.** "Lost", "stolen",
   "destroyed", "written off", "gift", "free sample" are the categories the statute enumerates, and
   each triggers ITC reversal. The prior product had
   `wms_stock_transactions.reason_code VARCHAR(50)` — **free text**
   (`WMS_DATABASE_DESIGN.md:1962`, via `R5:364`). Free text cannot drive a reversal, cannot be
   reported, and cannot be corrected retrospectively across a year of adjustments (`S-028`,
   `IRR-32`, `FR-315`).

**Why it is computed from movements, never from balances.** `FR-328` and `E-053`: a balance table
answers "now". The Rule 56 account, the s.44AB quantitative statement and the bank stock statement all
ask *"as at a date in the past, recomputed including entries made since"*. Month-end snapshots exist
for performance and are explicitly a **cache** — the same `L-4` discipline as positions.

**Tables.** `whin_stock_account_runs` + `whin_stock_account_lines` hold the **filed artefact** (which
period, which registration, run at what time, by whom, with which parameters, and the numbers as
filed). The report itself is derived. Storing the run is what makes "why does this quarter's opening
not equal last quarter's closing?" answerable.

### 5.2 ITC-04 and job work

The return reports quantities sent to and received back from job workers in the period.
**Periodicity is turnover-dependent — half-yearly or annually around a ₹5 crore line at cutoff —
`RE-VERIFY`.**

It is a **report over the wave-1 challan**, plus a run/line snapshot for the same reason as §5.1.
`FR-313`'s single-challan rule and `OD-1` govern who owns the filing: warehouse owns the goods and
the challan, accounting consumes it for the return. `whin_itc04_runs` + `whin_itc04_lines` hold what
was filed.

The thing that cannot be deferred is already in wave 1: the challan, the clock columns and the
job-worker location. **ITC-04 is genuinely additive.**

### 5.3 The GSTR-1 HSN summary, and what it needs from stock

The HSN summary is **HSN × UQC × quantity × taxable value**, filed monthly. Every India-group
product — Tally, Busy, Marg, Vyapar, Zoho, GoFrugal — keys it off the stock item (`R3:1035-1042`).
The number of HSN digits required varies by turnover (**4 / 6 / 8** — `RE-VERIFY`).

**The verified finding: no item table anywhere in this codebase has an HSN column today.**

```
grep -rn "hsn_code\|invoice_hsn_code" --include="*.sql" . | grep -v "db/client\|db/test\|db/seed"
```

→ **7 lines: 5 column declarations on 5 tables in 4 migration files**, the other two being comments in
`services/…/V40180` at `:6` and `:25`. **Not one of the five is an item or product master**:

| # | Column | `file:line` | What the table is |
|---|---|---|---|
| 1 | `accessory_quotation_pricing_components.hsn_code VARCHAR(20)` | `accessories/…/V30066__…:37` | a **quotation pricing line** |
| 2 | `quotation_pricing_components.hsn_code VARCHAR(20)` | `dealer/…/V20350__…:24` | a **quotation pricing line** |
| 3 | `asset_disposals.hsn_code VARCHAR(20)` | `assets/…/V60160__Asset_disposal.sql:121`, under a comment reading *"GST block for the scrap sale"* at `:120` | a **disposal document** |
| 4 | `service_entries.invoice_hsn_code VARCHAR(20)` | `services/…/V40180__…:19`, commented *"Primary HSN code at invoice level (Maruti WI: hsn_NO)"* at `:25` | an **invoice header** |
| 5 | `service_entry_charges.hsn_code VARCHAR(20)` | `services/…/V40180__…:35` | an **invoice charge line** |

The item master that most needs one — `accessory_products`
(`accessories/…/V30050__Create_accessory_products_table.sql:8`) — has none, and no later `ALTER`
adds one (`grep -rn "accessory_products" … | grep -i alter` → 10 hits, none HSN). So **HSN is
retyped per document, five different ways, and the HSN summary cannot be produced from stock at
all.** That is `E-047` verified against the live tree rather than asserted.

**What wave 1 fixes:** `whb_items.tax_classification_code` as a **string, never an FK into a tax
master** (`FR-066`), snapshotted onto every document and movement line (`IRR-42`, `FR-318`), plus
`gst_uqc_code` on `whb_uoms` (`FR-056`, `IRR-44`) and copied to the line (`FR-319`). **What wave 2
adds:** the HSN code list itself as seed rows, and the summary report — which, per R3 `D11`, *lives
in accounting, not here*. Warehouse supplies the grain; accounting files the return.

### 5.4 ITC reversal on write-off, loss and free issue

The reversal is required on goods lost, stolen, destroyed, written off, or disposed of by way of gift
or free sample. *(CGST s.17(5)(h) — substance confident, **clause letter believed correct,
`UNVERIFIED`**.)*

**The reversal amount needs the original credit**, and the original credit is the tax on the receipt
that brought *that lot* in. So `FR-316`/`S-029`: **a write-off movement must be able to reach the
receipt that brought the lot in** — the lot-to-cost-layer linkage. `whb_cost_layers` is present in v1
under `OD-6`, and `IRR-38` makes `cost_layer_id` a v1 column on the movement line even though FIFO
consumption ships in v1.1 — *"an AVCO-only v1 has nothing to build layers from later"*
(`IRREVERSIBLE.md:479`).

The reversal itself is `whin_itc_reversals`: reason code, statutory category, movement reference,
lot, quantity, original ITC, reversed amount, period, and the return it was reported in. Wave 2.

**What makes it possible is wave 1:** the reason-code catalogue with `tax_treatment_code` and
`statutory_category` (§2.2 rows 5–7). The column is named for no one scheme (`RL-008`; it was
`itc_treatment`). Its India values, the ITC treatments including this reversal, are seeded by
`warehouse-india` and never by base. Without it the reversal is uncomputable for every movement
already posted, and that is precisely the year the first audit covers.

### 5.5 Scrap, and TCS

**Scrap is inventory, not shrinkage.** It has a value, a location, a stock status and an owner, and
its sale is a **taxable supply with its own classification code**. **TCS at 1% applies** under
Income-tax s.206C(1) — *rate `RE-VERIFY`* (`S-030`, `FR-317`).

Modelling: scrap is a `stock_status_code` with `is_on_hand = true`, `is_valued = true`,
`is_allocatable = false` (`FR-102`'s behaviour-flag registry — which is why the registry has flags
rather than a badge colour), reached by a balanced two-line status-change movement with a reason code
(`FR-103`). The sale is an ordinary outbound. What is India-specific is one seed table,
`whin_tcs_sections`, and a `tcs_applicable` flag resolved from the item's classification.

Note the live precedent that already got this half right: `asset_disposals`
(`assets/…/V60160:94-126`) carries `hsn_code`, `taxable_value`, `cgst_amount`, `sgst_amount`,
`igst_amount` and `buyer_gstin` for exactly this reason — a scrap sale with a GST block. It is the
only place in the codebase that treats a disposal as a supply, and its shape is worth copying.

### 5.6 Retention, and the s.44AB quantitative statement

**Two clocks run on the same rows** (`S-051`, `FR-329`): the Companies Act's **8 financial years**
for books of account (s.128(5)) and GST's **72 months** from the annual-return due date (s.36). Both
**`RE-VERIFY`**. Food adds a third, **per-item** clock — *one year or the shelf life, whichever is
longer* (§8.2). So retention is a **policy object with a legal-hold flag**, not a global setting, and
archival must preserve "as at" reproduction rather than delete.

The **most concrete report obligation in the whole statutory surface** is the s.44AB tax-audit
quantitative statement — Form 3CD, **clause believed 35, `UNVERIFIED`** — a per-item quantitative
reconciliation for a financial year showing opening, purchases, sales, closing and shortage/excess,
that must tie to both the stock ledger and the GL. `whin_form3cd_runs` + `whin_form3cd_lines`, wave 2,
computed from movements per `FR-328`.

DPDP erasure versus statutory retention is stated once and not re-argued: **retention beats erasure,
satisfied by pseudonymising the person and never the quantity** (`S-055`; DPDP Act 2023, section
**`UNVERIFIED`**).

---

## §6 · Legal Metrology and MRP

**The rule.** The Legal Metrology Act 2009 and the Legal Metrology (Packaged Commodities) Rules 2011
require a pre-packaged commodity to declare: the name and address of the manufacturer / packer /
importer; the common or generic name; the **net quantity in standard units**; the month and year of
manufacture, packing or import; the **retail sale price (MRP) inclusive of all taxes**; a
consumer-care contact; the unit sale price; and — for imports and e-commerce listings — the **country
of origin**. Weighing and measuring instruments used in trade must be periodically **verified and
stamped** by the Legal Metrology department. *(Substance confident; **rule numbers `UNVERIFIED`**.)*

### 6.1 MRP on the item versus MRP on the batch — the one that is unrecoverable

**MRP is a property of the pack run, not of the SKU.** Two batches of the same item legitimately
carry different MRPs after a price revision, and both must be sellable and reportable **at the
printed price**. So MRP belongs on the **lot**, with the item carrying only the current default
(`S-033`, `FR-320`, `IRR-53`).

Adding it later leaves every historical lot with a null MRP **and no way to recover it** — the label
is on a carton that was put away months ago and nobody re-opens cartons to backfill. That is the
`PNR-3` class in `IRREVERSIBLE.md:294`: *"the column may still be addable and writable; the historical
observation it was supposed to record was never made."*

**What exists today.** Exactly one MRP column, and it is on the item:

```
grep -rn "mrp" --include="*.sql" . | grep -v "db/client\|db/test\|db/seed"
```

→ `accessories/…/V30217__Add_mrp_column_to_accessory_products.sql:2`:
`ALTER TABLE accessory_products ADD COLUMN IF NOT EXISTS mrp DECIMAL(15, 2);` — item-level, single
value, no history. And batch is not an entity at all in that module: `batch_number VARCHAR(50)` sits
on the **balance row** (`accessories/…/V30130__Create_accessory_stock_levels_table.sql:17`) alongside
`expiry_date DATE` at `:19`, which is `E-014`'s argument made concrete — *the same batch in two bins
can hold two expiry dates, and cannot be blocked or recalled.*

`net_content`: `grep -rn "net_content" --include="*.sql" .` → **0 results**.
`country_of_origin`: **1 result**, and it is on a *manufacturer*, not a lot —
`assets/…/V60002__Create_asset_manufacturers_table.sql:12`.

### 6.2 What a retail-facing warehouse must store

| Declaration | Where it lives | Wave |
|---|---|---|
| MRP, inclusive of all taxes | `whb_lots.mrp`, with `whb_items` default | **column wave 1** (`FR-320`) |
| Net quantity in standard units | `whb_lots.net_content` + `net_content_uom` | **column wave 1** |
| Month and year of manufacture / packing / import | `whb_lots.pack_month_year`, `manufacture_date` | **column wave 1** |
| Country of origin | `whb_lots.country_of_origin` | **column wave 1** (also `F-048`'s customs need) |
| Manufacturer / packer / importer name and address | counterparty, with a role link (`IRR-33`) | wave 1 (base) |
| Consumer-care contact, unit sale price | `whin_packaged_commodity_declarations` | **wave 2** |
| The declaration set per item × pack size, and its print | `whin_packaged_commodity_declarations` + label template | **wave 2** |
| MRP revision history, and stock reported by MRP | `whin_mrp_revisions`; `FR-321` makes MRP a **balance dimension** for non-batch-tracked items too | **wave 2** |
| Weighbridge / scale verification certificate and validity | `whin_instrument_verifications`, referencing the base device (`S-034`) | **wave 2** |

Two design notes. **Net content, pack size and count-per-pack are the same data the GS1 packaging
level needs** (`S-001`, `FR-057`/`FR-058`) — model them once, on the packaging row, not twice.
And **a weighing taken on an out-of-verification instrument must be flagged**, which means the
verification validity is a dated object the receipt path reads, not a certificate in a filing cabinet.

`FR-321` is the one row here with a re-keying cost: making MRP a **balance dimension** for
non-batch-tracked items means MRP joins the position key. Under `L-4` positions are a rebuildable
cache, so this is recoverable **iff MRP is on the movement line** — which `whb_lots.mrp` plus a lot on
the line gives for batch-tracked items, and which for non-batch-tracked items needs an explicit
decision before `PNR-1`. **Flagged as a candidate open decision for `DECISIONS.md` §3; do not number
it here.**

---

## §7 · Customs, bonded warehousing and MOOWR

R5 calls this *"the deepest schema consequence in this report"*
(`reviews/R5-standards-industry-ops.md:465`). It is the only item in the whole India surface whose
failure mode is **criminal rather than commercial**.

### 7.1 `duty_status` — one column, and it is unforgiving

A bonded warehouse holds goods on which **duty has not been paid**. Everything else follows from
that. The schema consequence is a single column, and it must be part of the stock position's
identity:

```
duty_status  VARCHAR(40) NOT NULL DEFAULT 'DOMESTIC' REFERENCES whb_duty_statuses(code)
  base seeds             DOMESTIC
  warehouse-india seeds  BONDED | MOOWR | SEZ | FTWZ | EXPORT_UNDER_BOND      -- P4-07, V540140
```

on **every movement line** and **in the `L-5` position unique key** (`FR-104`, `IRR-12`, `IRR-09`,
`D-5`).

**The regime values live in this pack, not in base** (`RL-001`). They moved here from `IRR-12`, which
now names only the column and its registry. `whb_duty_statuses` is registry 15 (`V500005`), with the
behaviour columns `is_duty_paid`, `is_allocatable_to_domestic_demand`, `requires_licence` and
`commingle_group`. Base seeds `DOMESTIC`; `P4-07` seeds the five Indian regimes in `V540140`. So a new
regime is a seed row in this module, never a base release. The FK is also what stops a misspelt
`'Bonded'` from opening a balance grain of its own. `BONDED` is **not** also a stock status: a
customs hold is a `wh_hold_types` row, so one fact is recorded on one axis.

**Bonded and duty-paid stock of the same SKU in the same warehouse must never merge into one
balance.** `IRREVERSIBLE.md:156` states the consequence in the terms that matter:

> Once a year of movements has commingled them **no algorithm separates them**, the ex-bond Bill of
> Entry cannot consume identified bonded quantity, and the warehouse cannot be licensed
> retrospectively over the mixture. This is a **customs offence, not a data-quality issue** — the
> only row on this list whose failure mode is criminal rather than commercial.

Adding the column after go-live means every historical row is `DOMESTIC` **by assumption** and no
bonded operation can be reconstructed. The column is **wave 1**; the feature is **wave 2**. That is
`D-8` working exactly as intended, and R5 §7.2 says so directly: bonded stock *"gates a whole segment
and does not gate the first customer — but is only reachable if a v1 column lands. Ship the columns,
defer the features"* (`R5:1126-1131`).

**Verified absence:** `grep -ril "duty_status" --include="*.sql" --include="*.java" --include="*.ts"
--include="*.tsx" .` → **0 files**. Same for `bonded` → 0, `moowr` → 0. Nothing in this codebase has
ever distinguished bonded stock.

### 7.2 The mechanisms, and what each forces

*Citations for this whole subsection: Customs Act 1962 Chapter IX ss.57–73; the Warehouse (Custody
and Handling of Goods) Regulations 2016; MOOWR 2019 under s.65. **Section numbers believed correct,
`UNVERIFIED`.** Every number below **`RE-VERIFY`.***

| Mechanism | Substance | What it forces into the schema |
|---|---|---|
| **Licence** | public / private / special warehouse licence, with a bond officer | the site is a **licensed object with a validity** — `whin_customs_licences`, and a despatch/receipt guard that reads it |
| **Warehousing bond** | a bond, commonly for **3× the duty**, executed by the importer (s.59) | `whin_customs_bonds` with a **running utilisation balance** — a bond is consumed and released, not a static number |
| **Warehousing period** | one year for general goods, extendable; capital goods under MOOWR effectively until clearance; interest accrues after 90 days for some categories | a **dated clock per Bill of Entry**, with interest — `whin_bill_of_entry_references`, and per `FR-165` the ageing job ships with the column |
| **Ex-bond clearance** | ex-bond BoE for home consumption (s.68) or for export (s.69) | `whin_exbond_clearances` — a clearance that **consumes an identified bonded quantity, per BoE**. This is why `duty_status` alone is insufficient and the BoE reference must reach the lot |
| **Inter-warehouse transfer** | removal from one warehouse to another (s.67), with a re-warehousing certificate | a transfer that **preserves duty status** across the move — which a `duty_status` in the position key gives for free, and which nothing else does |
| **MOOWR** | manufacture or other operations in a bonded warehouse with duty **deferred**, no interest; digital records in a prescribed form; a monthly return to the bond officer; waste and scrap treated on clearance | input-output tracking (which is `FR-105`'s transformation genealogy, `IRR-54`, v1 because it can only be populated by the act itself) and `whin_moowr_returns` |
| **SEZ / FTWZ** | a separate customs territory; movement DTA↔SEZ is import/export with its own documents; net-foreign-exchange obligations | a **location that is legally outside the domestic tariff area** — a `duty_status` value plus `whin_sez_movements` for the document pair |

### 7.3 Ledger consequences

1. **The position key gains a member.** `L-5` already lists `duty_status` as one of its nine members
   (`DECISIONS.md` §4). Because `L-4` makes positions a rebuildable cache, the key is recoverable
   *iff* `duty_status` is on the line — which is `IRR-12`'s whole point.
2. **Nullable key members need `NULLS NOT DISTINCT`.** `duty_status` is `NOT NULL` with a default of
   `DOMESTIC`, so it does not participate in that hazard — but it sits in a key several of whose
   members are nullable, and `IRREVERSIBLE.md:502` records the failure mode: without
   `NULLS NOT DISTINCT` the cache inserts a fresh row per movement and the `L-4` drift alert fires
   forever. Do not use the `COALESCE`-sentinel workaround `accessories/…/V30130:40-46` uses.
3. **Valuation splits.** Bonded stock has no duty in its cost; duty-paid stock does. `S-045`'s landed
   cost and `S-053`'s s.145A *inclusive-of-duty* tax basis both land on this seam. If the design has
   one `unit_cost` per movement, the s.145A adjustment is a spreadsheet forever — which is why
   `IRR-36`'s `cost_basis` is a wave-1 column with an explicit `INFORMATIONAL` value.
4. **Ex-bond clearance is not a transfer.** It changes `duty_status` in place, at the same location,
   against an identified BoE quantity — the same balanced two-line, same-location movement shape as a
   stock-status change (`FR-103`). Modelling it as a transfer loses the BoE consumption.

### 7.4 Adjacent, and deliberately not built

The **Warehousing (Development and Regulation) Act 2007** and WDRA registration are what let a
warehouse issue **negotiable warehouse receipts** (now electronic — eNWR) against agricultural
commodities. Relevant only if agri 3PL is targeted; `S-046` places it at **v3**, as an adapter. See
§12.

---

## §8 · Regulated goods in India

**The split this section applies.** R5 places pharma, food, cold chain and hazmat in *vertical
adapters* (`adapter-pharma`, `adapter-food`, `adapter-coldchain`, `adapter-chem` — Register B
`S-035`…`S-042`); the ladder's v2/P4 bullet lists "the regulated-goods packs" under India
(`DECISIONS.md` §5). Both are right about different halves, and the reconciliation is `D-8` applied
literally:

> **The licence-and-register objects that exist *because Indian law says so* are `warehouse-india`.
> The operational machinery — segregation matrices, sensors, excursions, FEFO, shelf-life gates,
> quarantine-on-receipt — is country-neutral and belongs in `warehouse-base` / `warehouse` / a
> vertical adapter.**

A German pharma warehouse needs batch-mandatory items, quarantine-on-receipt and a recall object. It
does not need a CDSCO form. So the first is core, the second is `whin_`.

**Verified absence of every India regulator in the codebase today:** `fssai` → 0 files, `cdsco` → 0
files, `legal metrology` → 0 files, `wdra` → 0 files, `rule 56` → 0 files, `itc_04`/`itc-04` → 0
files (all `grep -ril`, all extensions, 2026-09-01).

### 8.1 Pharmaceutical

| Obligation | Source | **Schema — core, country-neutral** | **Configuration / `whin_`** |
|---|---|---|---|
| Batch number and expiry **mandatory** on every pack; stock traceable by batch | Drugs and Cosmetics Act 1940 / Drugs Rules 1945 — **`UNVERIFIED`** | Batch tracking cannot be an item-level *option*: `lot_control_mode` and `expiry_policy` are **modes**, not booleans (`FR-098`), and `regulatory_class` on the item (`IRR-56`) **forces** the mode. Core, wave 1 columns | which regulatory classes force which mode — seed rows |
| Wholesale / retail **drug licence** on our entity and on every counterparty; sales only to licensed parties | Drugs Rules Forms 20B/21B — **`UNVERIFIED`** | `licence_number`, `licence_type`, `licence_expiry` on the counterparty; **a hard block on despatch to an expired licence** — a guard, and guards are code | `whin_entity_licences`, `whin_counterparty_licences`, `whin_licence_types` (catalogue, **no `CHECK`**) |
| **Schedule H1** sale/purchase register with batch, kept 3 years | Drugs Rules Schedule H1 — retention **`RE-VERIFY`** | — | `whin_schedule_h1_register` — a dispensing register **distinct from the stock ledger** |
| **QR / barcode on the top-300 drug brands'** packs, resolving to batch, dates, manufacturer | MoHFW amendment to the Drugs Rules, in force from Aug 2023 — **rule number `UNVERIFIED`; scope may have widened since cutoff — `RE-VERIFY`** | DataMatrix / GS1 element-string parse (`FR-063`) and per-pack identity (`FR-097`, `FR-100`) | which brands / items are in scope — seed |
| **Barcoding of exported formulations** at primary / secondary / tertiary pack with GS1 keys | DGFT public notices; the DAVA reporting portal | serialisation + aggregation (`S-004`, `S-036`) — SGTIN identity, `parent_lpn_id`, transformation genealogy | the DAVA payload — adapter |
| **Recall** | CDSCO recall guidance rather than a single statutory regulation as of cutoff | the recall **object**: scope by lot or serial, downstream trace, quantity recovered, disposition (`S-040`, `L-12`) — core | `whin_recall_notifications` — the regulator-facing filing |

**Global comparison, stated so the shape is right and the implementation is not attempted.** The US
equivalent is **DSCSA** (Title II of DQSA 2013 — *the "DSCPA" seen in briefs is a typo*), requiring
unit-level serialisation and, at full effect, interoperable electronic package-level tracing, in
practice EPCIS-based; enforcement was staged into 2024–25 with a stabilisation period and
small-dispenser exemptions and **the position after May 2026 cannot be stated**. The EU equivalent is
the Falsified Medicines Directive: a DataMatrix unique identifier plus tamper-evident closure,
verified against the European Medicines Verification System at dispense.

**We implement neither.** We implement **the shape** — SGTIN identity, aggregation, and an event log
carrying EPCIS's four dimensions — so an adapter can emit either. Without that shape pharma is
`CANNOT SERVE` permanently (`S-035`, `S-036`, `S-037`).

### 8.2 Food and FMCG

| Obligation | Source | **Schema — core** | **Configuration / `whin_`** |
|---|---|---|---|
| FSSAI licence / registration for every food business operator, displayed and quoted | FSS Act 2006; Licensing and Registration Regulations 2011 | licence number + expiry on our entity **and every counterparty**, with despatch blocked to an expired licence — same mechanism as §8.1 | `whin_entity_licences` with `licence_type = FSSAI` |
| Records retained **one year or the shelf life, whichever is longer** — **`RE-VERIFY`** | Licensing Regulations | retention is **per-item, driven by shelf life**, not a global setting (`S-051`) — so `shelf_life_days` is a wave-1 item column (`FR-069`) | the retention *policy* rows |
| **Recall plan mandatory**, with one-step-forward / one-step-back traceability | FSS (Food Recall Procedure) Regulations 2017 | trace-forward and trace-back over the ledger (`L-12`, `FR-105`); mock recall; recall register | the FSSAI notification format |
| Labelling: **best before vs use by**, batch, date of manufacture | FSS (Labelling and Display) Regulations 2020 | **two separate columns with different meanings** — best-before is quality, use-by is safety, and **only one of them justifies a hard despatch block** (`S-038`, `IRR-53`, `FR-095`). Merging them is unbackfillable | which class of item uses which |
| Hygiene and temperature control | Schedule 4 of the Licensing Regulations — **`UNVERIFIED`** | sensor readings bound to zone / location / LPN / shipment; excursion with duration and severity; **a QA disposition decision** — goods are not automatically scrap, a person decides, and that decision is the audit record (`S-041`) | thresholds per item class |
| HACCP / ISO 22000 / FSSC 22000 | voluntary, universally demanded by modern trade | CCP records tied to lots | — |
| **Minimum remaining shelf life on despatch**, per customer (the 75% / 50% modern-trade rules) | contractual, not statutory | `min_shelf_life_ship_pct` / `_days` on the customer or order, enforced at allocation (`S-039`, `FR-069`). **FEFO alone is not enough** — FEFO ships the *oldest*, which is exactly what a retailer rejects at the gate | the percentages |

**Cold chain** is where the standards world and the statute world meet: EPCIS 2.0 added
`sensorElementList` to the event model for precisely this. None of the three objects — reading
stream, excursion, disposition — exists in the prior art; `wms_item_storage` had
`temperature_min_c`/`max_c` as *item requirements* (`WMS_DATABASE_DESIGN.md:949-950`) **with nothing
measuring against them** (`S-041`). A requirement stored and never consumed is a defect the prior
product shipped, and `FR-070` names that pattern explicitly.

### 8.3 Hazardous and dangerous goods

**The prior art is better here than anywhere else and is kept verbatim.** `wms_item_storage` carried
`is_hazmat`, `hazmat_un_number`, `hazmat_class` (1–9), `hazmat_packing_group` (I/II/III),
`hazmat_proper_shipping_name` and `hazmat_subsidiary_classes` (`WMS_DATABASE_DESIGN.md:955-961`) —
a correct UN Model Regulations classification block. `FR-067` puts it on `whb_items` in **v1**.

What is missing is everything that **uses** it:

| Requirement | Source | **Schema — core** | **`whin_`** |
|---|---|---|---|
| **Segregation** — which classes may not be stored or loaded together | UN Model Regs / IMDG segregation table; MSIHC Rules 1989 for storage | a **class × class matrix enforced at putaway and at load**, not merely declared. Country-neutral | — |
| **Storage quantity limits** per licensed premises | MSIHC Rules 1989; Petroleum Rules 2002 / PESO licence for classes A/B/C; Explosives Rules | a per-zone / per-licence quantity ceiling with a **live** check | `whin_licence_quantity_ceilings`, and the licence as a dated object in `whin_entity_licences` |
| **Safety data sheet**, current version, available at site | MSIHC / GHS practice | SDS as a **versioned document on the item** with a review date | — |
| **Transport documentation** — class labels, emergency information panel, **TREM card**, trained driver, vehicle fitness | CMVR 1989 rr.129–137 — **range `UNVERIFIED`** | dispatch-time document generation; a driver / vehicle eligibility check | the TREM card template and the Indian document set |
| Threshold-quantity reporting to the regulator | MSIHC; PESO licence conditions | — | a stored-quantity-vs-licence report (`S-043`, v3) |

### 8.4 The one-line test applied to §8

If the **core** ships regulatory class forcing lot/expiry modes, licence fields on the counterparty
with a despatch guard, separate best-before and use-by, sensor/excursion/disposition, and the hazmat
block with a segregation matrix — then every India pack in this section is **seed rows, a register
table and a print template**. If the core ships none of it, no `whin_` table can rescue a lot that
was received without an expiry.

---

## §9 · The India fulfilment surface

Source: R4 `F-042`–`F-047` and `F-025`. R4's own framing:
*"No global product in the audited set has them; every Indian one does"* (`R4:78`).

### 9.1 The module question, answered once

**Almost none of this is `warehouse-india`, and that is the point.** An AWB pool exists because
Indian carriers issue waybill blocks; an NDR exists because Indian couriers raise one; COD
reconciliation exists because Indian consumers pay cash. Those are **carrier and commercial
mechanics**, not statute. `D-8` puts rules in `warehouse-india`; it does not put *India-shaped
commercial behaviour* there, because a Brazilian or Indonesian marketplace operation has the same
shapes with different names.

The one member of this set that **is** statutory — the 3PL client's additional-place-of-business
registration — is the one that carries `india` in its module cell (`FR-301`).

| Capability | R4 | FRD | Module | Wave |
|---|---|---|---|---|
| **AWB pool** — pre-fetched waybill blocks, claimed with `FOR UPDATE SKIP LOCKED` | `F-042` | `FR-202` | `warehouse` + `warehouse-adapter-<carrier>` | v2 / P5 |
| **Tracking events**, normalised **and** raw, webhook-idempotent, with carrier status mappings as **data** | `F-043` | (`FR-199`'s relocatable set) | `warehouse` | v1.1–v2 |
| **NDR** — reason, response clock, action, carrier ack, outcome | `F-044` | `FR-203` | `warehouse` + adapter | v2 / P5 |
| **COD** amount, collected, remitted | `F-045` | `FR-204` | `warehouse`; **columns in v1** | v1 columns / v2 feature |
| **COD remittance reconciliation** — UTR, file import, per-AWB match, shortfall, ageing | `F-045` | `FR-204` | `warehouse` (match) + accounting port (the receipt) | v2 / P5 |
| **RTO as an inbound stock stream** | `F-046` | `FR-205` | `warehouse`; **columns in v1** | v1 columns / v2 flow |
| **Weight / dimension discrepancy dispute** | `F-047` | `FR-206` | `warehouse`; **pack photo + scale weight in v1** | v1 evidence / v2 dispute |
| **Client GST registration as an additional place of business** | `F-025` | `FR-301` | **`warehouse-3pl` · `warehouse-india`** | v2 / P4 |
| Warehousing SAC and place of supply | `F-025` | `FR-286`, `FR-294` | `warehouse-3pl` charge code; **accounting determines the tax** | v2 / P5 |

### 9.2 The four that carry a v1 obligation anyway

Even at v2, four of these force something into v1 — and the reason is always the same as §2's: the
observation cannot be made retroactively.

1. **COD columns on the shipment** — `cod_amount`, `cod_currency`, `cod_collected_at` (`FR-204`,
   `F-045`). A shipment posted without them cannot be matched to a remittance that lands three weeks
   later.
2. **RTO columns on the shipment** — `rto_initiated_at`, `rto_reason_code`, `rto_awb_number` (the
   return leg often has its **own** AWB), `rto_received_at`, `rto_status` (`FR-205`, `F-046`).
3. **Pack photo and scale weight at pack time** (`FR-206`, `F-047`). The evidence for a
   weight-discrepancy dispute is a photograph of the packed carton on a scale with the AWB visible.
   **It cannot be created retroactively** — which is the purest `PNR-3` argument in the whole
   fulfilment set.
4. **`return_type` on the return** — customer return, **RTO**, refused delivery, cancelled in
   transit, vendor return, recall, client withdrawal, marketplace return, warranty, exchange — a
   **day-one column** (`FR-270`, `F-054`), because the disposition rules branch on it: an RTO has no
   customer to refund, and a recall must not be restocked under any disposition.

### 9.3 Why RTO is a stock problem and not an order status

RTO rates for Indian COD fashion and electronics commonly run **15–30% of dispatched orders** — an
order of magnitude above US parcel undeliverable rates, which is why no global product models it as a
first-class stream (`R4:1341-1370`). The goods arrive at the dock in a carrier's bulk consignment,
**identified only by the AWB on the shipping label**, with no RMA and no customer interaction. The
sequence is: receive the consignment → scan AWBs → match to the original shipment → open and verify
contents against the original lines → grade → put back to sellable, unsellable or a claim.

Two consequences for the ledger: a **lost RTO becomes a claim, not a silent shrinkage adjustment**
(which is a reason code with a `tax_treatment_code`, §5.4); and an NDR is the **leading indicator** that a
unit is coming back and will need a receiving slot — which is why `F-044`'s queue and `F-046`'s
consignment are one workflow, not two.

---

## §10 · The schema / seed-data split

**R3's one-line test, stated verbatim** (`reviews/R3-erp-midmarket-audit.md:1544-1548`):

> **Can this be added later by inserting rows, changing a config value, or writing a report?** If
> yes, it is seed / config and can wait. If it requires a column, a foreign key, a new document type,
> or a change to what a movement *means*, it is **schema** and must be in the first migration —
> because every stock row written before it exists is permanently wrong.

R3 applied it and got **16 schema items and 12 seed-data items**. This table restates all 28, applies
the test to each explicitly, adds the wave under A-4, and adds the rows this document raises that R3
did not (marked ✚). Counts computed from the rows below: **21 schema rows** (16 from R3 §3.1 + 5 ✚)
and **17 seed rows** (12 from R3 §3.2 + 5 ✚).

### 10.1 SCHEMA — a column, an FK, a document type, or a change to what a movement means

| # | Item | Apply the test | Wave | Source |
|---|---|---|---|---|
| S1 | `whb_items.tax_classification_code` (HSN/SAC) **and snapshotted on the line** | Adding it later gives the **new** code for **old** documents. Not rows | **1** | `E-047`, `IRR-42`, `FR-066`/`FR-318` |
| S2 | `gst_uqc_code` on the UoM and copied to the line | A filed line with no UQC cannot be summarised; the value was never captured | **1** | `E-047`, `IRR-44`, `FR-056`/`FR-319` |
| S3 | `whb_warehouse_branches` — **exactly one `REGISTERED` link at every instant**, dated (`D-14`) | Without the link no movement's tax treatment is ever determinable; without the dates, not for any past movement | **1** | `E-048`, `FR-079`, `RG-001` |
| S4 | `wh_stock_transfers.{from_branch_id, to_branch_id, is_taxable_supply}`, **frozen at creation** | Changes the document, the series, the valuation and the GL posting. None of that is a setting | **1** | `E-050`, `FR-305` |
| S5 | `transfer_valuation_method` + `transfer_price_amount` | Which r.28 basis was used must be defensible three years later; it is not re-derivable | **1** | `E-050`, `FR-306` |
| S6 | `whin_delivery_challans` as a **numbered document with its own series** | A challan is a document, not a print template. Rule 55 movements have no invoice to hang attributes on | **1** | `E-049`, `FR-307` |
| S7 | `wh_transport_details` — dispatch-from / deliver-to, mode, transporter, vehicle, LR number and date, distance | A compliance-*reference* store holds a number, not a vehicle | **1** | `E-051`, `FR-308` |
| S8 | `whb_lots` as an **entity** with `expiry_date`, `manufactured_date`, `mrp`, `batch_status` | As strings on a balance row the same batch in two bins holds two expiry dates and cannot be blocked or recalled | **1** | `E-014`/`E-016`, `IRR-53`, `FR-094` |
| S9 | **MRP as a valued dimension** | Two MRPs of one SKU coexist legitimately; retrofitting MRP into the balance key is a rewrite of every stock query | **1 schema** (2 feature) | `E-016`, `FR-320`/`FR-321` |
| S10 | Movements **immutable, date-stamped, queryable as-at** | No configuration turns a balance into a history | **1** | `E-053`, `L-2`, `FR-328` |
| S11 | `wh_stock_periods` **distinct from accounting periods** | Stock closes before books close; a back-date into a submitted bank-statement period must be refused | **1** | `E-046`, `L-8` |
| S12 | **In-transit as a location**, per reference | A `status = 'IN_TRANSIT'` flag makes the goods belong to no balance and to no 31-March statement | **1** | `E-032`, `FR-085` |
| S13 | Job-work movement to an **owner-preserving external location** with `expected_return_date` | The clock is measured from the challan; a movement predating the field has no clock, ever | **1 schema** (2 ITC-04) | `E-054`, `FR-312` |
| S14 | `owner_id` on movements and positions | Consignment / 3PL / job-work stock is not ours to value; adding it later invalidates every valuation query already written | **1** | `E-024`, `D-5`, `IRR-06` |
| S15 | `whb_reason_codes` with `tax_treatment_code` + `statutory_category` + posting target | A year of free text cannot be reclassified, so that year's reversal cannot be computed | **1** | `E-033`, `S-028`, `IRR-32` |
| S16 | **Free / scheme quantity** on the receipt line (10+1) | It changes the unit cost and therefore the taxable base of the onward sale; bolting it on corrupts cost layers already written | **1 column** (2 feature) | `E-080` |
| ✚ S17 | `duty_status` on the line **and in the position key** | Once commingled, no algorithm separates them. Customs offence, not data quality | **1 column** (2 feature) | `S-044`, `IRR-12`, `FR-104` |
| ✚ S18 | `company_id` + `warehouse_id` on the movement header | A GST return computed from guessed entities is a filing error | **1** | `IRR-17`, `F-025` |
| ✚ S19 | `whb_warehouses.state_code` + the dated `REGISTERED` history (`IRR-64`); no `legal_entity_id` or `tax_registration_id` on the site (`D-14`) | A historical transfer cannot be classified as supply vs non-supply for a filed period | **1** | `S-022`, `IRR-57`, `FR-080` |
| ✚ S20 | `whb_lots.net_content` + `net_content_uom` + `country_of_origin` + `pack_month_year` | Printed on a pack already put away; nobody re-opens cartons | **1** | `S-033`, `IRR-53`, `FR-095` |
| ✚ S21 | `cost_layer_id` on the line, so a write-off can reach its receipt | The ITC-reversal amount needs the original credit, and an AVCO-only v1 has nothing to build layers from later | **1 column** (2 reversal) | `S-029`, `IRR-38`, `FR-316` |

### 10.2 SEED DATA / CONFIGURATION — rows, a setting, or a report

| # | Item | Apply the test | Wave | Source |
|---|---|---|---|---|
| D1 | The HSN code list, and HSN → rate mapping | Rows in a master. The **column** (S1) is what cannot wait | 1 (rows) | `R3 D1` |
| D2 | UQC code list (`NOS`, `KGS`, `LTR`, `MTR`, …) and the UoM → UQC mapping | Rows | 1 | `R3 D2` |
| D3 | The 36 state / UT jurisdiction rows and their GST codes | Rows. Accounting needs the same master — **FK to one, do not build a second** | 1 | `R3 D3`, `I-007` |
| D4 | Tax rates, cess rates, effective dates | Owned by accounting entirely; warehouse never computes tax | 2 | `R3 D4`, `FR-294` |
| D5 | Reason-code vocabulary (`EXPIRY`, `DAMAGE`, `SHRINKAGE`, `THEFT`, `TRANSIT_SHORTAGE`, `WRITE_OFF_ITC_REVERSAL`, and the six statutory categories) | Rows. The **columns** on that table (S15) are schema | 1 | `R3 D5`, `D-10` |
| D6 | E-way bill threshold, distance-to-validity table, exempt-goods list, per-state intra-state thresholds | Values in a localisation pack. The **attributes** (S7) are schema. **Every value `RE-VERIFY`** | 1 | `R3 D6` |
| D7 | Document-series formats for challans and transfers | Configuration, given S6 exists | 1 | `R3 D7` |
| D8 | Near-expiry alert horizons, obsolescence buckets, count-class frequencies | Configuration | 1.1 | `R3 D8` |
| D9 | E-invoice / e-way portal credentials, and the adapter | An adapter over S7 | 1 (adapter), credentials always config | `R3 D9`, `P-044` |
| D10 | Print layouts for challan and transfer note, bilingual and thermal | Templates over S6/S7 | 1 | `R3 D10`, `A-2` |
| D11 | GSTR-1 HSN summary **report** | A report over S1/S2 — **and it lives in accounting, not here** | 2 | `R3 D11` |
| D12 | ITC-04 **return** | A report over S13; accounting owns the filing | 2 | `R3 D12`, `OD-1` |
| ✚ D13 | Which `regulatory_class` values force lot / expiry / serial control | Rows against a column that already exists (`IRR-56`, `FR-098`) | 2 | `S-035` |
| ✚ D14 | Licence types (drug wholesale / retail, FSSAI, PESO, customs warehouse) and their renewal horizons | Rows in an open catalogue | 2 | `S-035`, `S-038`, `D-10` |
| ✚ D15 | EPR categories (batteries, e-waste, tyres, plastic packaging) and the reporting format | Rows plus a report over `epr_category`, which is already a v1 item column (`IRR-56`) | 2 | `S-050`, `FR-324` |
| ✚ D16 | TCS sections and rates | Rows | 2 | `S-030` |
| ✚ D17 | Retention horizons (8 FY / 72 months / shelf-life) and legal-hold reasons | Rows against S10's history and a policy object | 2 | `S-051`, `FR-329` |

### 10.3 The asymmetry, in numbers

If wave 1 ships **S1–S21** and none of **D1–D17**: an Indian buyer cannot file a return from the
product, but **every row of stock ever written is correct**, and D1–D17 is a quarter's work.

If wave 1 ships **D1–D17** and misses even **S3, S4, S7 or S17**: the product demos beautifully, and
every branch transfer ever recorded is wrong in a way that cannot be repaired without re-keying the
history — or, for S17, in a way that is a customs offence.

**That asymmetry is the entire argument for putting the schema in the first migration.** It is also
why A-4 moves five *documents* into wave 1 and leaves all fourteen *registers* in wave 2: the
documents are the smallest set that makes the schema usable, and the registers read history that will
already be correct.

---

## §11 · Tables

**Band:** `warehouse-india` owns **V540000–V549999** (`D-2`), prefix **`whin_`** (`D-3`), package
`ai.warehouseindia` (`D-1`).

**Sub-allocation idiom.** The precedent is live: `accounting-india` sub-allocates its band in
hundred-blocks per task (`V602000–V602099`, `V602100–V602199`, `V602300–V602349` —
`.claude/tasks/BATCH-ACCOUNTING-P2.md:218-225`, band declared at `CLAUDE.md:123`). The blocks below
follow that idiom. **They are ranges, not assignments** — every task file pre-allocates its own
numbers *inside* its block, and `tools/check-design-set.py` fails the build on double-ownership or an
out-of-band number (`DECISIONS.md` §7 rule 3). **Never write a number here that a task has not
claimed.**

Two structural rules that hold for every row below. **No `CHECK (x IN (…))` on any vocabulary column**
(`D-10`) — thirteen catalogues in base and every one of India's is the same shape. And **no `whb_` or
`wh_` table gains a foreign key to a `whin_` table**, in either direction (`D-11`,
`MODULE-INTEGRATION.md:889`); cross-module references are stable string keys or external-ref rows.

### 11.1 Wave 1 — v1 / P2-IN — **14 tables** — V540000–V540999

| # | Table | Key columns | Block |
|---|---|---|---|
| 1 | `whin_gstin_profiles` | `id`, `company_id`, `gstin` uk, `legal_name`, `trade_name`, `state_code`, `registration_type` (catalogue: REGULAR · COMPOSITION · SEZ_UNIT · SEZ_DEVELOPER · CASUAL · NON_RESIDENT · UNREGISTERED), `effective_from`, `effective_to`, `is_active`, `certificate_document_id` | V540000–V540009 |
| 2 | `whin_gst_state_codes` | `state_code` (2 digits) uk, `state_name`, `state_type` (STATE·UT), `is_active` — **36 seed rows** | V540010–V540019 |
| 3 | `whin_hsn_codes` | `code` uk, `description`, `chapter`, `digit_length`, `effective_from`, `effective_to`, `uqc_default` — **seed** | V540020–V540029 |
| 4 | `whin_uqc_codes` | `uqc_code` uk (`NOS`, `KGS`, `LTR`, `MTR`, …), `description`, `unece_rec20_code` — **seed**, plus the `whb_uoms.gst_uqc_code` mapping seed | V540030–V540039 |
| 5 | `whin_delivery_challans` | §4.1's field table: identity · `challan_type` FK · both ends with pincode and state code · declared value and basis · status · cancellation · `source_document_ref` quad. uk(`company_id`,`series_id`,`challan_number`); `from_gstin_profile_id` is the profile of the issuing site's `REGISTERED` branch at `challan_date` | V540100–V540119 |
| 6 | `whin_delivery_challan_lines` | `challan_id`, `line_no`, `item_id`, `lot_id`, `serial_id`, `quantity`, `uom_code`, **`gst_uqc_code` snapshot**, **`tax_classification_code` snapshot**, `unit_value`, `taxable_value`, **`expected_return_date`**, **`deemed_supply_due_date`**, `quantity_returned`, `closed_at`, `job_work_type` | V540100–V540119 |
| 7 | `whin_eway_bills` | `id`, `company_id`, `source_document_type`, `source_document_id`, `ewb_number`, `ewb_date`, `supply_type`, `sub_type`, `part_a_status`, `part_b_status`, `generated_at`, `valid_until`, `distance_km`, `status` (catalogue), `cancelled_at`, `cancel_reason_code_id`, `consolidated_ewb_id` nullable, `idempotency_key` uk, `provider_document_id` | V540200–V540229 |
| 8 | `whin_eway_bill_lines` | **the filed snapshot**: `eway_bill_id`, `line_no`, `hsn_code`, `description`, `quantity`, `uqc_code`, `taxable_value`, `cgst_rate`, `sgst_rate`, `igst_rate`, `cess_rate` | V540200–V540229 |
| 9 | `whin_eway_bill_events` | append-only lifecycle log: `eway_bill_id`, `event_type` (catalogue — wave 1 admits `PART_A_GENERATED`, `PART_B_UPDATED`, `CANCELLED`; wave 2 adds `EXTENDED`, `CONSOLIDATED`, `REJECTED_BLOCKED_GSTIN`), `occurred_at`, `actor_id`, `vehicle_number`, `transport_document_ref`, `provider_reference`, `raw_response_document_id` | V540200–V540229 |
| 10 | `whin_compliance_providers` | `code` uk, `name`, `capabilities` (EWB·IRN·both), `is_active` — the vendor-agnostic layer (`P-044`) | V540300–V540349 |
| 11 | `whin_compliance_provider_environments` | `provider_id`, `environment` (SANDBOX·PRODUCTION), `base_url`, `timeout_ms`, `is_active` | V540300–V540349 |
| 12 | `whin_compliance_credentials` | `provider_environment_id`, `gst_registration_id`, **encrypted** credential ref via the platform's admin-settings secret masking, `credential_spec_id`, `valid_until`, `last_rotated_at` — **never plaintext in this table** | V540300–V540349 |
| 13 | `whin_compliance_documents` | `id`, `document_kind` (EWB·IRN), `source_document_type`, `source_document_id`, `provider_id`, `external_reference`, `ack_number`, `ack_date`, `signed_qr_document_id`, `locks_document`, `cancellable_until`, `status` | V540300–V540349 |
| 14 | `whin_compliance_api_logs` | `id`, `provider_environment_id`, `operation`, `request_document_id`, `response_document_id` — **both encrypted at rest**, per §4.2's non-goal #1 — `http_status`, `duration_ms`, `created_at` **indexed**, `correlation_id` | V540300–V540349 |
| — | permissions · menus · grid column definitions · `filter_definitions` · `grid_preferences` (`default_filters` **and** `default_columns`) · `permission_dependencies` | seed only, no new table | V540400–V540499 |

**Outside `whin_`, same wave:** `wh_transport_details` in `warehouse` (`V510000–V519999`, §4.2),
and the 24 columns of §2.2 in `warehouse-base` (`V500000–V509999`) and `warehouse`.

### 11.2 Wave 2 — v2 / P4 — **42 tables** — V541000–V548999

| Group | Tables | Key content | Block |
|---|---|---|---|
| **A · Job work & ITC-04** (3) | `whin_job_work_returns` · `whin_itc04_runs` · `whin_itc04_lines` | return receipts against a challan **line**; the filed return snapshot with period, registration, quantities sent and received | V541000–V541099 |
| **B · Rule 56 stock account** (2) | `whin_stock_account_runs` · `whin_stock_account_lines` | per registration, per period, in the mandated categories; opening · receipts · supplies · lost · stolen · destroyed · written off · gift · free sample · closing; separately raw material / finished / scrap / wastage; plus goods at a job worker | V541100–V541199 |
| **C · HSN summary & ITC reversal** (3) | `whin_hsn_summary_runs` · `whin_hsn_summary_lines` · `whin_itc_reversals` | HSN × UQC × quantity × taxable value as filed; reversal with reason, statutory category, original ITC, movement and lot reference | V541200–V541299 |
| **D · Scrap & TCS** (1) | `whin_tcs_sections` | section, rate, threshold, effective dates — **seed** | V541300–V541399 |
| **E · Approval / sale or return** (0) | — | **no new table**: a challan type plus the wave-1 clock columns | — |
| **F · MRP & Legal Metrology** (3) | `whin_packaged_commodity_declarations` · `whin_mrp_revisions` · `whin_instrument_verifications` | the declaration set per item × pack size; MRP revision history; weighbridge / scale certificate, verified-until, calibration record, referencing the base device by id | V542000–V542099 |
| **G · Customs, bonded, MOOWR, SEZ** (9) | `whin_customs_licences` · `whin_customs_bonds` · `whin_bill_of_entry_references` · `whin_bill_of_entry_lines` · `whin_exbond_clearances` · `whin_exbond_clearance_lines` · `whin_moowr_returns` · `whin_moowr_return_lines` · `whin_sez_movements` | licence with validity and bond officer; bond with a **running utilisation balance**; per-BoE warehousing clock with interest; clearance **consuming identified bonded quantity**; monthly MOOWR statement; DTA↔SEZ document pairs | V543000–V543199 |
| **H · Regulated goods — the statutory slice only** (6) | `whin_licence_types` (catalogue, **no `CHECK`**) · `whin_entity_licences` · `whin_counterparty_licences` · `whin_licence_quantity_ceilings` · `whin_schedule_h1_register` · `whin_recall_notifications` | drug / FSSAI / PESO / customs licences with expiry and a **despatch guard**; per-zone hazmat ceilings tied to a licence; the H1 register; the CDSCO / FSSAI filing. **The segregation matrix, sensors, excursions, FEFO and shelf-life gates are core, not here** (§8) | V544000–V544199 |
| **I · EPR** (3) | `whin_epr_categories` (seed) · `whin_epr_returns` · `whin_epr_return_lines` | quantity by category per period over `whb_items.epr_category`, which is already a v1 column | V545000–V545099 |
| **J · Retention, records & 3CD** (3) | `whin_retention_policies` · `whin_form3cd_runs` · `whin_form3cd_lines` | two clocks plus per-item shelf-life retention, legal hold; the s.44AB quantitative statement as a **built report with a stored run** | V546000–V546099 |
| **K · Relational tax engine — transplant, `P-043`** (6) | `whin_tax_entity_types` · `whin_tax_components` · `whin_tax_rules` · `whin_tax_rule_components` · `whin_tax_rule_conditions` · `whin_tax_resolution_audit` | **conditional — see §11.4.** Carried with `T-H1` and `T-H3` as **wave-2 blockers, not deferred items**: a deterministic discriminator so slab rules cannot all match simultaneously; non-overlapping effective-date ranges enforced by a `btree_gist` `EXCLUDE`; seed guards that can actually fire (`rule_code` `NOT NULL`, or `ON CONFLICT` never fires); `UNIQUE(rule_code, version)` (`FR-325`) | V547000–V547199 |
| **L · Compliance lifecycle remainder, `P-044`** (3) | `whin_eway_bill_consolidations` · `whin_eway_bill_consolidation_items` · `whin_compliance_tasks` | consolidated EWB (EWB-02) and the retry/queue object. **Extension and cancellation are built properly here or not at all** — no schema-only statutory flow | V547500–V547599 |
| **M · Reserved** | — | headroom for a jurisdiction the pack does not yet cover, and for `FR-301`'s `whin_client_registrations` if `warehouse-3pl` places it here rather than in `wh3_` | V548000–V549999 |

**Wave 2 total: 3+2+3+1+0+3+9+6+3+3+6+3 = 42 tables.**
**`whin_` total across both waves: 14 + 42 = 56 tables.**

For scale: R6 records that the prior `supply-chain-core` shipped **26 built-and-audited India tables**
— a 6-table relational tax engine plus an 18-table compliance stack plus masters — and calls it *"the
highest-leverage single carry-forward into `warehouse-india`"*
(`reviews/R6-prior-art-triage.md:88-90`). Groups **K** and **L** and wave-1 rows 10–14 are that
carry-forward; they are not new design.

### 11.3 One table this pack deliberately does not build

**A number-series allocator.** `P-046` puts `wh_number_series` in `warehouse-base` with a locked
counter row. `warehouse-india` registers series *kinds* and consumes the base allocator. Building a
second one is how the prior art ended up with `scc_document_sequences` carrying no `updated_at` even
though `next_value` mutates on every allocation (`T-L10`, `R6:1098`).

### 11.4 Group K is conditional, and the condition is an open decision

There is a real, unresolved conflict in the source set and it must not be resolved by whoever writes
the migration:

- `FR-325` carries the relational tax engine forward into `warehouse-india` and makes its two
  unresolved defects **wave-2 blockers**.
- `R3 D4` says *"tax rates, cess rates, effective dates — owned by `accounting` entirely; **warehouse
  never computes tax**"*, and `FR-294` says `warehouse-3pl` contains no tax engine in any version.
- `D-7` makes **standalone** the reference configuration, and a standalone install still has to put a
  taxable value on an e-way bill line.

**The shape of the answer is almost certainly the `OD-1` pattern — a third install state.** Warehouse
carries the engine and uses it *only* when no accounting module is present; where `accounting-india`
is installed, the engine stands down and warehouse asks accounting for the rate exactly as it asks it
for the invoice. That is a recommendation, not a decision. **It needs a numbered row in
`DECISIONS.md` §3 with a deadline of "before the first `whin_` tax-engine migration"; this document
does not number it, because inventing an `OD-n` here is how two things end up sharing one id**
(`DECISIONS.md` §6).

Until it is taken, **group K is 6 tables that may not exist**, and the counts above should be read as
56 with it and 50 without.

---

## §12 · What we do not do — and the way back in

`D-12` says v1 is a cut line, not the scope limit, and that nothing is deferred to "we'll look at it
later". These are different: they are **declined**, with the reason and the re-entry path stated so
that a later reader knows a decision was taken rather than a topic forgotten.

| # | Not built | Why | Re-entry path |
|---|---|---|---|
| 1 | **State entry taxes — octroi, LBT, entry tax** | Subsumed by GST. Building a levy that no longer exists is building a defect | If any state reintroduces a local levy, it is a `whin_` charge type over the existing challan and transport block. No schema |
| 2 | **CST-regime statutory forms — C, F, H, I forms** | Superseded by GST. The F-form's purpose — evidencing a branch transfer as a non-sale — is exactly what §3's `is_taxable_supply` and the challan now do | Historical-data migration only, for a customer bringing pre-GST history. A read-only import, never a live document |
| 3 | **TRAN-1 / TRAN-2 transition credits** | The transition window closed years before this product exists | None. If a customer needs it they need an accountant, not a warehouse |
| 4 | **Filing the returns themselves** — GSTR-1, GSTR-3B, GSTR-9, ITC-04, 24Q/26Q/27EQ | `D-6` and `FR-294`: accounting owns the ledger and the filings. Warehouse owns quantity and produces the **extract**. Two systems filing one return is worse than one system that cannot | The extract is already wave 2 (§5). Accounting consumes it through its existing port. If accounting is absent, the extract exports as a file |
| 5 | **Computing GST rates when accounting is present** | Two tax engines in one install produce two answers and neither team owns the difference — the same failure `D-6` resolved for cost | §11.4's open decision. The engine exists for the standalone case only, if at all |
| 6 | **A second jurisdiction / state master** | `R3 D3`: accounting already needs one; warehouse **FKs to it, never builds a second**. `OD-4`'s rule — never an FK from base into another module — makes this an external-ref join | `whin_gst_state_codes` is 36 seed rows for the standalone case; where `accounting-india` is installed it is an xref, not a second truth. **This is a candidate `DECISIONS.md` §3 row; do not number it here** |
| 7 | **Anything requiring a licence we would not hold** — customs broker (filing a Bill of Entry), drug licence (dispensing), PESO licence (storing explosives), WDRA registration (issuing negotiable warehouse receipts) | We are the **system of record**, not the licensee. We store the licence, we age it, we block a despatch against an expired one, and we produce the register. We never *act* under a licence we do not hold | Each is an adapter over data we already hold. eNWR specifically is `S-046`, **v3**, and only if agri 3PL becomes a target |
| 8 | **EPCIS as a queryable event repository** | Our obligation is to **emit** correct events, which is a projection over the ledger. A queryable repository is a compliance product in its own right | `IRREVERSIBLE.md:717`: the irreversible halves are `IRR-20` (read point vs business location) and `IRR-21` (event time vs record time), both v1 columns. The repository is additive whenever it is wanted |
| 9 | **DSCSA and EU FMD compliance** | Not Indian law, and the post-May-2026 US enforcement position cannot be stated (§8.1) | We ship the **shape** — SGTIN identity, aggregation, four-dimension events — so `warehouse-adapter-pharma` can emit either. Without the shape, pharma is `CANNOT SERVE` permanently |
| 10 | **The dealer vehicle inventory migrating onto the ledger** | `OD-2`, explicitly not v1 or v2. Prove the ledger on parts first | A documented future `whad_` adapter, v3 planning |
| 11 | **`accessories` absorbing into this India pack** | `D-9`: permanently separate, and the cost is named in `COEXISTENCE.md` rather than hidden | `M6`'s one document layer — `whin_delivery_challans` accepts lines sourced from **either** system through `whb_item_external_refs`, so one transfer produces one challan even when goods come from two ledgers. That is the re-entry, and A-4 moves it to **wave 1** (§2.3) |
| 12 | **Per-state e-way bill threshold logic hardcoded anywhere** | The thresholds differ by state and change by notification. A hardcoded ₹50,000 is a defect with a date on it | `D6` seed rows in the localisation pack, effective-dated, with the **`RE-VERIFY`** register of this document as the review checklist |

---

## Appendix A — Reconciliations this document raises for the concurrent FRD re-cut

Recorded here so the reconciliation pass finds them, not resolved here.

| # | Where | What it says | What A-4 or verification makes it |
|---|---|---|---|
| 1 | `IRREVERSIBLE.md:482` | `hsn_code` *feature ships **v2** (India)* | **v1 — wave 1.** §2.3 |
| 2 | `IRREVERSIBLE.md:542` | warehouse legal-identity triple *feature ships **v2** (India)* | **v1 — wave 1.** §2.3 |
| 3 | `COEXISTENCE.md:487-499`, `:558`, `:710` | `M6` statutory document layer at **v2 / P4**, stated as a correction of R3's v1.1 | **wave 1.** A-4 is later than that correction. §2.3 |
| 4 | `COEXISTENCE.md:491`, `:558` | table named `whin_transport_details` | **`wh_transport_details`, in `warehouse`** per `FR-308`/`E-051` — a vehicle number is not an Indian rule. §4.2 |
| 5 | `COMPETITOR-BENCHMARK.md:214`, `PLATFORM-DEPENDENCIES.md:114` | table named `whb_sites` | **`whb_warehouses`** per `FR-079`/`FR-080`/`IRR-57`. §3.4 |
| 6 | `CLAUDE.md:148` | *"GSTIN is per-state: stored on `branches`, NOT on company"* | **The schema does not obey it**: `companies.gstin` (`automotive/…/V10002:19`) and `dealers.gstin` (`dealer/…/V20000:11`) both exist and were never dropped. `whb_warehouses` reads the **branch**. §3.3 |
| 7 | `FR-325` vs `R3 D4` / `FR-294` | warehouse carries a tax engine · warehouse never computes tax | **Unresolved.** Needs a numbered `DECISIONS.md` §3 row; §11.4 recommends the `OD-1` three-state pattern |
| 8 | `FR-321` | MRP becomes a balance dimension for non-batch-tracked items | Needs an explicit pre-`PNR-1` decision on where MRP sits on the **movement line** for non-batch-tracked items, or the position key is not rebuildable. §6.2 |
| 9 | `FR-313` / `R3 E-054` | one challan table; `acc_job_work_challans` reduced to a view or deleted | **Gated on `OD-1`.** Do not build on this document alone. §4.4 |

## Appendix B — Every codebase claim in this document, with its command

All run 2026-09-01 against `/Users/bbhushan/work/git/workspace/classic`. **Re-run before treating any
count as current** — the tree moves (`filterUtils.ts` scopes were 211 in `IRREVERSIBLE.md:719` and
are **213** here, the same day).

| Claim | Command | Result |
|---|---|---|
| GSTIN lives in 6 tables, 8 columns | `grep -rniE "^\s*(ADD COLUMN IF NOT EXISTS\s+)?[a-z_]*gst[a-z_]*(_number\|in)?\s+VARCHAR" --include="*.sql" . \| grep -v "db/client\|db/test\|db/seed"` | 8 declarations |
| No GST state code anywhere | `grep -rn "gst_state_code\|state_code" --include="*.sql" . \| grep -v "db/client\|db/test\|db/seed"` | **0** |
| No item table has HSN | `grep -rn "hsn_code\|invoice_hsn_code" --include="*.sql" . \| grep -v "db/client\|db/test\|db/seed"` | **7 lines**, of which **5 are column declarations** (the other 2 are comments at `services/…/V40180:6,25`) — 5 tables, 4 files, **none an item master** |
| `accessory_products` has no HSN and no later `ALTER` adds one | `grep -n "hsn" .../V30050__Create_accessory_products_table.sql` · `grep -rn "accessory_products" .../migration/ \| grep -i alter` | 0 · 10 hits, none HSN |
| One MRP column, item-level | `grep -rn "mrp" --include="*.sql" . \| grep -v "db/client\|db/test\|db/seed"` | 1 — `accessories/…/V30217:2` |
| No `net_content` | `grep -rn "net_content" --include="*.sql" .` | **0** |
| `country_of_origin` exists once, on a manufacturer | `grep -rn "country_of_origin" --include="*.sql" . \| grep -v "db/client\|db/test\|db/seed"` | 1 — `assets/…/V60002:12` |
| Batch is a string on the balance row | read `accessories/…/V30130:17,19` | `batch_number VARCHAR(50)`, `expiry_date DATE` |
| In-transit is a status, not a location | read `accessories/…/V30133:15` | `status VARCHAR(20) … 'IN_TRANSIT'` |
| `accessory_warehouses` has no branch or registration | read `accessories/…/V30017:8-31` | free-text `state` at `:16`, nothing else |
| `branches` carries the registration and `WAREHOUSE` type | read `platform/…/V182:7,18,25` and `V149:33,35,61` | `gst_number`, `state VARCHAR(100)`, `chk_branches_type` admits `WAREHOUSE` and `DISTRIBUTION_CENTER` |
| No `duty_status`, `bonded`, `moowr`, `fssai`, `cdsco`, `wdra`, `itc_04`, `uqc`, "legal metrology", "rule 56" | `grep -ril "<term>" --include="*.sql" --include="*.java" --include="*.ts" --include="*.tsx" .` | **0 each** (`uqc` returned 3 password-hash false positives only) |
| Only one `challan` table, and it is a traffic fine | `grep -rn "CREATE TABLE[^;]*challan" --include="*.sql" -i . \| grep -v "db/test\|db/client"` | 1 — `services/…/V40042:111`, with `place_of_violation` `:116` and `fine_amount` `:119` |
| Delivery challan exists only as a document type to upload | read `dealer/…/V20376:63` | `('CHALLAN', 'Delivery Challan', …)` |
| E-way bill exists only as a badge with no producer and a document type | `grep -rniE "\bewb\b\|eway\|waybill" …` then `grep -rn "EWB_GENERATED" …` | 21 files, 2 real; `EWB_GENERATED` → **2 hits, both the badge itself** (`platform/frontend/src/lib/status-utils.ts:215-216`) |
| `accounting-india` is a shell, and the sibling-package rule is live | `find accounting-india -type f` · read `AccountingIndiaModuleConfig.java:19-30,55` | **3 files**, 0 migrations (`.gitkeep`); *"a SIBLING of `ai.accounting`, never `ai.accounting.india`"* |
| Registry cost per grid | `awk 'NR>346' platform/frontend/src/utils/filterUtils.ts \| grep -cE '^  [A-Z][A-Z0-9_]*: \{'` · `grep -cE '^\s+"[a-zA-Z]' .../CacheConfiguration.java` | **213** scopes · **235** cache names |
