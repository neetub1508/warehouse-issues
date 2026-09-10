TITLE: [Warehouse] EPIC: P2-IN — The India movement documents
LABELS: epic,warehouse,phase-p2in
issue: 6
---
Part of __MASTER__ · Modules `warehouse-india` · Migrations — **6 blocks, enumerated below** · Ships in **v1**

## Overview

**One question: can the truck leave?**

**In India, goods physically cannot move between two of a company's own premises without a
document.** A movement that is not a supply travels on a **delivery challan**; a movement whose
consignment value exceeds the threshold additionally requires an **e-way bill**, with a vehicle
number entered **before the vehicle moves**. A truck stopped without one is detained and penalised.
**This is a licence to operate, not a feature.**

The version ladder as first written put **all** of India in v2/P4. R3 and R5 both came back marking
the delivery challan, the e-way bill and the GST-aware transfer document as **v1 BLOCKERs**, and
R5 ranks `S-022`+`S-023`+`S-024` at position **7** in its *"cannot sell to a first real customer"*
list. `DECISIONS.md` §5.1 **`A-4`** accepted the argument and refined it into two waves:

> **v1 / P2-IN — the documents required to move goods legally.** Delivery challan · e-way bill
> payload and generation · the GST-aware transfer document · HSN on the item · cross-GSTIN transfer
> as a deemed supply.
>
> **v2 / P4 — the statutory registers and filings.** Rule 56 stock account · ITC-04 and job work ·
> MRP and Legal Metrology · bonded / MOOWR · the regulated-goods packs.

**A-4 exists because that lesson was paid for once already**: the accounting programme moved India
filing out of P4 into v1 after finding that without it, v1 won **1 of 11** Indian SME segments.

**Four tasks.** `IMPLEMENTATION-PLAN.md` §9.3 sizes the phase **0 XL · 1 L · 2 M · 1 S** and calls it
*"genuinely small"*, quoting `INDIA-LOCALISATION-PACK.md` §1.2: **"one document object, one filing
object, one transport block, and twenty-four columns."**
§9.4 staffs it **1 backend · 1 frontend · 1 QA with Indian GST domain knowledge** — *small in code,
unforgiving in domain* — running **alongside** all of P2.

## Why a fifth module, and why country-neutral

**`D-1`.** The brief's four modules carry a *vertical* axis and **no jurisdiction axis**. Every India
rule would otherwise live either in `warehouse` — **making the core product unsellable outside
India** — or in `warehouse-adapter-dealer` — **making it invisible to a pharma customer**.
**`D-8`** keeps the core country-neutral: **no GST, HSN semantics, e-way bill or MRP rule is
hardcoded in `warehouse-base` or `warehouse`.** Tax identity, document types, statutory registers and
print layouts are **data**.

## The hooks are not here, and that is the whole design

**The core carries only the hooks India needs, and those hooks are in v1 because they cannot be added
later.** `INDIA-LOCALISATION-PACK.md` §2.2 numbers **24 hook columns across 8 tables, all wave 1** —
`company_id` and `warehouse_id` on the movement · **`hsn_code` snapshotted on the line** ·
`duty_status` on the line **and in the `L-5` position key** · `reason_code_id` on header **and** line
· `itc_treatment` and `statutory_category` on the reason code · `legal_entity_id`,
`tax_registration_id` and `state_code` on the warehouse · `tax_classification_code` on the item ·
`gst_uqc_code` and `unece_rec20_code` on the UoM · the five Legal-Metrology columns on the lot · and
the six transfer columns including **`is_taxable_supply`, derived at creation and frozen**.

**Every one lands in P0 or P1, not here.** `FR-305`, `FR-306`, `FR-308` and `FR-312`'s clock columns
are `P1-11` / `P1-17`; **HSN on the item is `FR-066`, `P1-03`**; the transport block is
`wh_transport_details` in **`warehouse`**, `P1-11`'s `V500052`.
**P2-IN consumes them; it does not create them.**

The argument, in one line from `IRREVERSIBLE.md`: an **unbackfillable** change means the column can be
added and **cannot be populated truthfully** — *"every aggregate that crosses the boundary becomes a
lie that looks like data"*. And R3 §3.3 states the asymmetry that makes the split safe:

> If v1 ships the schema and none of the seed data, an Indian buyer cannot file a return — but
> **every row of stock ever written is correct**, and the seed data is a quarter's work. If v1 ships
> the seed data and misses even one schema item, the product **looks compliant in a demo** and every
> branch transfer ever recorded is wrong in a way that cannot be repaired without re-keying history.

## Exit criterion

On a **Mode-D** install, in order:

> A branch transfer between two GSTINs **derives `is_taxable_supply` at creation and freezes it**;
> issues a **numbered delivery challan from the sending branch's own per-branch series**; generates
> an **e-way bill Part A** from the compliance provider; **accepts Part B before the vehicle number
> is recorded**; and the gate is **refused** where an e-way bill is legally required and absent —
> and passes **freely** where it is not (`FR-195`).

**Decomposed by `SCENARIO-CATALOGUE.md` §3.12 into six scenario ids:**
**`WH-SC-206`** (the challan from its own series) · **`WH-SC-207`** (four purposes, **one challan
table**) · **`WH-SC-209`** (Part-A generated, Part-B fillable later) · **`WH-SC-210`** (Part-B empty
→ **refused**, naming the missing Part-B) · **`WH-SC-211`** (below threshold → **issues freely**,
through the same code path).
Plus `WH-SC-208` (`P1`, the polymorphic transport block the adapter reads).

**Places of business (`RG-002`, round 4).** One GSTIN covers every branch in its state, so a GSTIN
profile maps to **several** branches through `whin_gstin_profile_branches` (`PRINCIPAL`/`ADDITIONAL`,
dated, `V540010`), never to one. `WH-SC-313` — the second Delhi branch, an additional place of business
under the Delhi GSTIN, resolves the profile and issues a challan — and `WH-SC-311` — a `REGISTERED` link
to a branch in another state is refused — join the exit walk. `P2-IN-01` owns both.

**And the negative test, which is the `D-8` half:** **`WH-SC-213`** — none of that code is reachable,
and **no `whin_` table is referenced**, on a **Mode-A** install.

## Migration blocks

**6 blocks**, re-derived from the `Migrations` field of every P2-IN task header — not transcribed
from an earlier table. That glob is the authority; **re-run it after any header change**:

```bash
for f in issues/p2in-*.md; do
  printf "%-9s " "$(basename "$f" .md)"
  grep -m1 '^Part of ' "$f" | sed 's/.*· Migrations \*\*//; s/\*\* · Screens.*//; s/\*\*//g'
done
```

- `V540000` — `P2-IN-01` module bootstrap. **Creates no table**
- `V540010` — `P2-IN-01` `whin_gstin_profiles`, `whin_compliance_registrations`
- `V540011`–`V540012` — `P2-IN-02` the transplanted provider stack: providers, environments,
  credential specs, encrypted credentials, auth sessions, compliance documents, API logs
- `V540020` — `P2-IN-03` `whin_delivery_challans`, `whin_delivery_challan_lines`
- `V540030` — `P2-IN-04` `whin_eway_bills` (+ the filed-line snapshot and the lifecycle event log)
- `V541000`–`V541049` — `P2-IN-01` permissions, `permission_dependencies`, menus, grid configuration,
  `admin_settings`, i18n **en / fr / hi**

**All four tasks write migrations.** `V540031`–`V540099` is the deliberate gap between the two waves.

**These are `DATA-MODEL.md` §7.6's numbers, and they are the ones to use.**
`INDIA-LOCALISATION-PACK.md` §11's blocks **collide with wave 2** and must not be followed — see
Traps.

## Tasks

__TASKS__

**Order is strictly linear:** `P2-IN-01 → P2-IN-02 → P2-IN-03 → P2-IN-04`, with two cross-phase
edges `IMPLEMENTATION-PLAN.md` §3.6 names explicitly — the stream starts after **`P1-17`**
(the transfer schema), **`P2-IN-03` needs `P1-09`'s number series**, and **`P2-IN-04` needs
`P1-11`'s transport details**. `P2-IN-04` additionally consumes `P2-14`'s renderer for the challan
and e-way bill prints, and attaches its dispatch guard to `P2-10`'s and `P2-02`'s dispatch actions.

One sequencing note inside the phase: **`WS-175`'s *Rotate credentials* and *Test connection*
actions cannot ship with `P2-IN-01`**, because `whin_compliance_credentials` and
`whin_compliance_auth_sessions` land in `P2-IN-02`'s `V540011`.

## Every statutory threshold, with its cutoff and its re-verify instruction

**The knowledge cutoff behind this design set is May 2026.** *Indian indirect-tax thresholds move by
notification, several times a year, and at least one number below is probably already stale.*
**Not one of these is hardcoded**: each is a configuration row with an effective date, and each
migration comment carries the value, the cutoff and the instruction.

| Rule | Value held at cutoff (May 2026) | Status |
|---|---|---|
| E-way bill consignment-value threshold, **inter-state** | **₹50,000** | **RE-VERIFY** |
| E-way bill threshold, **intra-state** | state-by-state; several states ₹1 lakh; some exempt intra-city | **RE-VERIFY — per state, and they differ** |
| Required **irrespective of value** | inter-state movement to a job worker; handicraft goods | **RE-VERIFY** |
| Validity, regular cargo | **1 day per 200 km**, from first Part-B entry | **RE-VERIFY — this number has already changed once (100 → 200)** |
| Validity, over-dimensional cargo | **1 day per 20 km** | **RE-VERIFY** |
| Cancellation window | **24 hours**, if the goods were not transported | **RE-VERIFY** |
| Generation blocked | GSTIN with **two consecutive periods unfiled** | **RE-VERIFY** |
| E-invoice applicability | aggregate turnover above **₹5 crore**, B2B / export / CDN; B2C out | **RE-VERIFY** |
| E-invoice reporting window | **30 days** from document date, above **₹10 crore** turnover (from 2025) | **RE-VERIFY** |

**And the citation rule, which is not optional.** *No invented legal citation.* Where the rule is
known and the section number is not, the rule is stated and the citation is marked **`UNVERIFIED`** —
*a confidently wrong section number in a design document becomes a confidently wrong comment in a
migration and then a confidently wrong answer to an auditor.* The challan rule cites
*CGST Rules r.55 — **`UNVERIFIED`***; the e-way bill rule cites *r.138 and state notifications —
**rule number `UNVERIFIED`***.

## Traps

- **`INDIA-LOCALISATION-PACK.md` §11's migration blocks collide with `DATA-MODEL.md` §7.6's wave-2
  assignments. Follow `DATA-MODEL.md`, which `IMPLEMENTATION-PLAN.md` §1.4 names the migration
  authority.** §11.1 puts `whin_delivery_challans` at `V540100`–`V540119` and `whin_eway_bills` at
  `V540200`–`V540229`; `DATA-MODEL.md` puts them at **`V540020`** and **`V540030`** and reserves
  `V540100`+ for wave 2 (`whin_eway_bill_vehicle_updates` **is** `V540100`). §11.2 additionally puts
  wave-2 group A at `V541000`–`V541099` — **exactly the band `WIN-30` gives to wave-1 permissions and
  grids**.
- **Two further divergences between the same two documents, carried not silently resolved**
  (`IMPLEMENTATION-PLAN.md` §1.4, §11 item 2): the pack counts **14** wave-1 tables including three
  seed masters (`whin_gst_state_codes`, `whin_hsn_codes`, `whin_uqc_codes`) that `DATA-MODEL.md`
  §7.6 places at **`WIN-12`, wave 2**, leaving **12**; and the two name the registration table
  differently — `whin_gst_registrations` versus `whin_gstin_profiles` + `whin_compliance_registrations`.
- **`FR-195` has no v1 host screen.** `BUILD-SPEC-SCREENS.md` §5.1 says the gate pass *"lives on
  WS-111 (Handovers)"*, but **WS-111 `wh_handovers` is `v1.1 · P3`** (`V510104`), and there is **no
  v1 gate-pass object anywhere** — `wh_handovers.gate_pass_ref` is v1.1 and
  `wh_receiving_sessions`' gate pass is inbound. `FR-195` and `WH-SC-210`/`WH-SC-211` are **v1**.
  **The resolution:** in v1 the e-way-bill precondition is a **guard on the two outward dispatch
  actions that exist** — `WS-105` Shipments → Dispatch and `WS-090` Transfer Orders → Dispatch —
  contributed by `warehouse-india`; `P3`'s WS-111 inherits the same guard.
- **`BUILD-SPEC-SCREENS.md` WS-179 lists *Extend validity* as a v1 action and it must not ship.**
  `whin_eway_bill_extensions` is `WIN-10`, `V540100`, **wave 2**, and
  `INDIA-LOCALISATION-PACK.md` §4.2 rules that **Part-B update and cancellation are wave 1** —
  *because you cannot legally leave a wrong bill live* — while **extension and consolidation are wave
  2**, under the standing non-goal that **a schema-only statutory flow is a compliance claim we
  cannot honour**. v1 ships **four** transitions.
- **Three security constraints carried as non-goals, because the prior art shipped them as defects**
  (`P-044`): raw request and response bodies of compliance calls **are never stored unencrypted** —
  `scc_compliance_api_logs` was *designed* to store them, **including auth calls carrying client
  secrets and NIC passwords**, and had **no index on `created_at`** so any purge is a full scan;
  **no demo or test controller may trigger a real statutory filing** — `ComplianceDemoController`
  could trigger **real** IRN and EWB filings from a minimal demo body **and shipped in production
  code**; and **build a statutory flow properly or leave the tables out**.
- **The prior implementation's live e-way-bill defect must be fixed, not reproduced** (`FR-309`): a
  **null Part B sent to NIC** produced a cryptic gateway rejection. Validate Part B **locally**, with
  a field-level error naming the vehicle number.
- **GSTIN is in three of our own tables today and they disagree by design.**
  `branches.gst_number VARCHAR(15)` (`platform/…/V182__Add_financial_columns_to_branches.sql:7`) is
  the per-state registration `CLAUDE.md:148` names; `companies.gstin`
  (`automotive/…/V10002:19`) **contradicts that rule and was never dropped**; `dealers.gstin`
  (`dealer/…/V20000:11`) is a third candidate. **Read the site's `REGISTERED` branch at the document
  date. Never duplicate onto the warehouse** — duplication is how the three-way disagreement happened
  (`D-14`, `RG-001`). The warehouse's branch links are the dated junction `whb_warehouse_branches`, and
  **do not copy `accessory_warehouse_branch`'s semantics** (`accessories/…/V30018:8`): its
  unlinked-is-shared arm and its `is_primary` meaning are both refused (`RH-001`). *A warehouse under two
  tax registrations at one instant is still not a thing* — exactly one link is `REGISTERED`.
- **There is no GST state-code master and no state-code column anywhere.**
  `grep -rn "gst_state_code\|state_code" --include="*.sql" .` excluding client/test/seed → **0**.
  `branches.state` is free-text `VARCHAR(100)` (`platform/…/V149:33`), **not** the two-digit code
  Part A requires. `whb_warehouses.state_code` is a **denormalised snapshot with a derivation rule**
  — the first two digits of a valid GSTIN — not a second source of truth. The **master** is wave 2.
- **`warehouse-base` must not gain a foreign key into `warehouse-india`, in either direction**
  (`D-11`, `MODULE-INTEGRATION.md:889`). Round 4 removed the one column that
  tempted it: `whb_warehouses.tax_registration_id` is **dropped** (`RG-001`). The registration is
  resolved from the site's `REGISTERED` branch through `WarehouseBranchLinkValidator` beans that
  `warehouse-india` registers, at read time; in a non-India install none is registered.
  Likewise `wh_transfer_orders` gains no `challan_id` and `wh_shipments` no `eway_bill_id`.
- **The transport block is `wh_`, not `whin_`, and that is a deliberate divergence from
  `COEXISTENCE.md` §5 `M6`** — which places `whin_transport_details` in `warehouse-india` at v2.
  `FR-308` and `E-051` win, for a `D-8` reason: **a vehicle number is not an Indian rule.** Every
  jurisdiction's carrier has a vehicle, a consignment note and a distance; what is Indian is the
  *obligation to file them*. It is also what lets a future `logistics` module read the block without
  depending on `warehouse-india` (`G-013`, `FR-199`). **Record it in `COEXISTENCE.md`'s
  reconciliation pass; do not resolve it silently in a migration.**
- **Do not build a second number-series allocator** (`P-046`). `warehouse-base` owns
  `whb_number_series` with a **locked counter row**, following the one working gapless precedent —
  `assets/V60014:2-9` + `AssetTagSequenceRepository.java:19-27`. The platform's
  `SequentialCodeGenerator` is **scan-based and explicitly not gapless** (`:9-19`, `:41-53`) —
  correct for masters, **wrong for a statutory series**. The prior art's own defect `T-L10`:
  `scc_document_sequences` had no `updated_at` although `next_value` mutates on every allocation.
- **"Challan" in this codebase currently means a traffic fine.** The only `challan` table is
  `services/…/V40042:111` `replacement_challans`, with `place_of_violation` at `:116` and
  `fine_amount` at `:119`. The only *delivery* challan is a **document-type seed row** at
  `dealer/…/V20376:63` — a slot to upload someone else's PDF. And the entire e-way bill capability
  today is `platform/frontend/src/lib/status-utils.ts:213-224`'s status badges —
  `IRN_GENERATED`, `EWB_GENERATED`, `PENDING_IRN`, `PENDING_EWB` — with **nothing anywhere producing
  those values** (residue of the deleted `supply-chain-core`), plus
  `dealer/…/V20376:57`'s `('EWAY', 'E-way Bill', …)` filing slot.
  **A green badge with no producer and a filing cabinet.** Do not mistake either for a starting point.
- **`D-3` — never name anything `wms_*` or `scc_*`.** `platform/…/V528:37,57,59` and `V663:17-19`
  still carry hardcoded `wms_*`/`scc_*`/`warehouse-*` **permission exclusions** from a deleted
  module; a new `wms_`-prefixed permission would inherit a decision nobody took.
- **`T-15` — do not copy `accounting-india`'s banding.** It is `V602000`–`V602999`, **inside**
  `accounting-base`'s band. `warehouse-india`'s band is **disjoint**: `V540000`–`V549999`.
- **`P-045` / `FR-327` — every statutory, expiry and challan date is a SQL `DATE` mapped to
  `LocalDate`, filtered `dateOnly`, rendered date-only.** The prior art shipped them as
  `TIMESTAMP WITH TIME ZONE` / `OffsetDateTime`, so *"expired today"* shifted across a day boundary.
  CLAUDE.md's `formatUTCDate(value, true, true)` guidance is **wrong for `LocalDate`**.
- **Mobile: one screen, and the rest is a stated `none`.** `screens/whinEwayBill` does **Fill Part-B
  and Update vehicle only** — *a driver whose vehicle changed at a transhipment point must update
  Part-B from the road*; everything else in this module is a compliance desk. And
  `mobile/…/ListHeader.tsx:210-218` supports `'dropdown' | 'text'` and **not dates** (`C-044`,
  `PP-3`), which is a real constraint on a challan list whose primary filter is a date range.

## The honest boundary of the v1 wave

**`FR-311` — the inter-state stock-transfer invoice needs an invoice reference number** and routes
through the same e-invoicing adapter as a sales invoice. **That adapter is v2 / `P4-01`.** So an
install above the reporting threshold **cannot ship the v1 transfer document without it**.
`WH-SC-214` makes it a scenario, and this design set **states it rather than leaving it to be
discovered at a go-live**.

## What P2-IN deliberately does not do

**No statutory register, no filing, no tax computation** — **`OD-9`: warehouse never computes tax.**
It captures the facts — HSN, place of supply, `is_taxable_supply` frozen at creation, taxable value —
and hands them over; accounting or the compliance provider computes. **That answer drops 6
conditional tables**: the India pack is **50 or 56** depending on it.
No MRP dimension (`OD-10`: MRP belongs on the **lot**, not on the position key). No bonded
warehousing or MOOWR. No ITC-04, no Rule 56 stock account, no HSN summary, no ITC reversal, no
Legal Metrology, no regulated-goods packs, no e-invoicing adapter, no relational tax engine, no
consolidated e-way bill, no e-way bill **extension**. **All of it is P4**, and every one is named on
the screen it is absent from.

## Definition of done
Per __MASTER__ and `IMPLEMENTATION-PLAN.md` §10, with the four programme-specific additions, plus two
that are specific to this phase: **every threshold carries its value, its May-2026 cutoff and a
`RE-VERIFY BEFORE BUILD` instruction in the migration comment and in the configuration row**, and
**no legal citation is invented — where the section number is unknown it is marked `UNVERIFIED`.**
