# R28 — re-targeting the warehouse to manufacturing + storage: impact and architecture

**Date** 2026-10-22 · **Prefix** `RN-` · **Status** analysis recorded; nothing changed in code or docs yet — decisions pending (§7)
**Follows** [R27](R27-client-p2p-stores-gap.md) (client purchase-to-stores gap).

**User direction, 2026-10-22.** The warehouse product is for **manufacturing and storage only**. It has
nothing to do with the dealer module or retail. It is a different product from the dealer module.
Purchasing that serves the stores is in scope. **Accounting is deferred** and needed later.

`grep -rohE "\bRN-[0-9]{1,3}\b" docs issues tools | wc -l` → 0 before this file.

---

## 1. Coupling to the dealer module in code — none

| ID | Finding | Evidence (`classic/`) |
|---|---|---|
| `RN-001` | No main-code import of `ai.dealer`, `ai.automotive`, `ai.services` or `ai.accessories`. An architecture test forbids them | `warehouse-base/.../architecture/WarehouseBaseCouplingTest.java` |
| `RN-002` | No SQL reads dealer, automotive or accessory tables. The mentions are refusal guards or comments | `WB/V500001:37-52`, `WB/V500054:29-98`, `WhCoexistenceRepositoryCustomImpl.java:35-46` |
| `RN-003` | Gate events are warehouse-owned (`WarehouseGateEventPublisher`). The automotive boom barrier appears only in a comment (`:25`) | keep — a manufacturing gate needs it |
| `RN-004` | **Dead leftovers from the deleted adapters** (`64d1fe74d5`): `enable.warehouse.adapter.dealer` and `.services` in the base enable expression; `ADAPTER_DEALER` i18n label; comments; menu sort slots 60/70 ("Parts Counter", "Workshop Parts") left free | `warehouse-base/.../WarehouseBaseModuleConfig.java:53`; `warehouseBase.json:386`; `W/V511248:33-34,121`; `W/V511208:67` |

**Conclusion:** re-targeting is about **scope, vocabulary and features**. It is not about untangling a
dependency on the dealer module, because none exists.

`WB` = `warehouse-base/backend/src/main/resources/db/migration`, `W` = `warehouse/backend/src/main/resources/db/migration`.

## 2. Retail / D2C / e-commerce features in the built code

| ID | Feature | Tables | Page(s) | Blast radius |
|---|---|---|---|---|
| `RN-010` | AWB pools | `wh_awb_pools`, `wh_awb_numbers` (`W/V510205`) | outbound/awb-pools | 24 Java, 7 perms, 1 job |
| `RN-011` | NDR | `wh_shipment_ndrs`, `wh_ndr_actions` (`W/V510206`) | outbound/ndr | 25 Java, 6 perms, 2 jobs, FK to RTO |
| `RN-012` | COD remittances | `wh_cod_remittances`, `_lines` (`W/V510207`) | outbound/cod-remittances | 25 Java, 7 perms, 1 job |
| `RN-013` | Channel accounts, order imports, publish rules | 6 tables (`W/V510208`) | channel-accounts, channel-imports, publish-rules | 59 Java, 20 perms |
| `RN-014` | Tracking links, notifications, public track page | 3 tables (`W/V510209`) | tracking-links, `(public)/track/[token]` | the product's only unauthenticated endpoint |
| `RN-015` | Marketplace claims | `wh_marketplace_claims` (`W/V510215`) | inbound/marketplace-claims | 15 Java, 7 perms, 1 job |
| `RN-016` | RTO consignments | `wh_rto_consignments` (`W/V510050:509`) | outbound/rto | 15 Java, 5 perms |
| `RN-017` | Courier serviceability, rate quotes | 3 tables (`W/V510204`) | serviceability, rate-quotes | 28 Java, 11 perms |
| `RN-018` | The "Channels" L1 menu and its fulfilment/carriers sections | — | — | `W/V511271, V511273, V511274` |

About **12 pages, 20 tables, ~17 migrations and 22 seeded rows**.

**Keep, but trim:**
- `whb_channels` stays, because the append-only ledger references it (`WB/V500059:81`). Keep only the B2B kind.
- `wh_demand_orders.payment_mode` and `cod_amount` are hidden in the UI.

**Generic, keep:** carriers, labels, manifests, handovers, consignments and RMAs. A manufacturer ships B2B.

## 3. Dealer / automotive items in the built code

| ID | Item | Evidence | Proposed action |
|---|---|---|---|
| `RN-020` | OEM obsolescence returns | `W/V510210:181,250`; 22 Java, 9 perms, 2 jobs | remove, or relabel as **supplier buy-back** |
| `RN-021` | Trade Portal ("garages, fleet operators and sub-dealers") | `W/V510221`, `W/V511209:174` | relabel as **distributor / B2B customer portal**, or remove |
| `RN-022` | Parts KPIs report | `W/V511211:121-185`; 8 Java | relabel as **Stock KPIs** |
| `RN-023` | Accessories coexistence (category ownership, external snapshots, coexistence report) | `WB/V500053:55,110` | remove if accessories is never co-installed |
| `RN-024` | Seeded vocabulary (31 rows): `ADAPTER_*`/`ACCESSORIES` source systems, `JOB_CARD`/`POS_SHIFT` document types, `WORKSHOP` site type, `OEM_PART_NUMBER`/`MARKETPLACE_LISTING` identifiers, retail return types and channel kinds, RTO/NDR reasons, `RTO_RECEIPT` movement, PO order source `VOR` | `WB/V500002:157-192`, `WB/V500010:155-169`, `WB/V500012:199`, `W/V510011:128` | relabel or hide. **Never delete**: the ledger FKs reference them |

**Keep for manufacturing:**
- supersessions (engineering change)
- `VOR`, relabelled as **line-stop / machine-down**
- `OEM_PART_NUMBER`, relabelled as **manufacturer part no.**
- `WORKSHOP`, relabelled as **production store / shop floor**
- `ISSUE_TO_ASSET`/`FITMENT` (issue to a machine)
- kits, gate events, supplier claims and returns, and India job work

**3PL** (`warehouse-3pl`: 25 tables, 18 pages) is *storage sold to third parties*. It fits "storage", and the proposal keeps it.

## 4. Capability matrix for manufacturing + storage (33 rows)

| Group | REUSE | EXTEND | NEW |
|---|---|---|---|
| A Procurement | — | PO types + schedule (A3), approval matrix (A6), supplier master (A8) | requisition (A1), RFQ/quotation/award (A2), rate contract (A4), PO amendment (A5), vendor rating (A7) |
| B Inbound + stores | job-work challan, India (B9) | GRN bill no/date/billed qty (B2), sampling bands (B3), QC-reject → return action (B5) | gate-entry register + returnable gate pass (B1), MRN authorisation (B4), material requisition (B6), store issue with cost object (B7), store return (B8) |
| C Manufacturing | FG receipt (C5), scrap (C7), genealogy (C11) | BOM multi-level (C1), production order (C2), issue to production / backflush (C3), WIP location (C4), co-product (C6), in-process/final QC (C8), subcontract returning a different item (C9) | MRP (C10); routing/work centres (C12, recommended out of scope) |
| D Sales touchpoints | sales demand order → dispatch (D1), challan/e-way bill (D2), customer RMA (D4) | outward gate pass (D3) | — |

**Totals:** 7 REUSE, 14 EXTEND, 12 NEW. That is about **38 new tables, ~30 new or changed screens, ~25 services**. MRP is the largest single engine.

## 5. Design decisions that must be reversed or amended

| ID | Current decision | Needed change |
|---|---|---|
| `RN-030` | FR-119: no price on supplier sources | Agreed and contract rates live in the procurement module, not on `whb_item_supplier_sources` |
| `RN-031` | FR-139: QC never raises a supplier return automatically | Add an explicit **"raise supplier return"** action from the inspection. It stays manual and maker/checker; no silent auto-return |
| `RN-032` | FR-268: multi-level BOM belongs to "a manufacturing module" | Now owned by `warehouse-manufacturing` (§6) |
| `RN-033` | FR-261 / I-1: one terminal movement per work order | Production orders need staged issue, partial completion and co-products. Use a **separate production-order document**; do not widen the VAS work order |
| `RN-034` | `S-052` cost object "V500030 or never" | Carry the cost object (department / cost centre / production order) on the **issue document's lines**, referenced by `source_document_type/id`. No ledger column, so no append-only retrofit |
| `RN-035` | R7: PR/RFQ owned by a supply-chain module that does not exist | Owned by `warehouse-procurement` (§6) |
| `RN-036` | Segment #1 "dealer parts department — the target"; dealer/retail personas | Target = manufacturing plant stores + storage; add department requester, stores-issue clerk, production planner and QC inspector personas |

## 6. Architecture — options and recommendation

| Option | Pros | Cons |
|---|---|---|
| A. Everything in core `warehouse` | no new touchpoints; direct FKs | mixes purchasing approval workflow and production planning into the stock app; costly to extract later |
| B. Two siblings: `warehouse-procurement` + `warehouse-manufacturing` | india pattern; clean toggles | ~27 platform touchpoints each (`MODULE-INTEGRATION.md:106-140`); stores issue/MRN still need core edits |
| C. One combined sibling | one set of touchpoints | two unrelated domains share one switch |
| **D. Layered (recommended)** | generic stores stay in core, the right home for a manufacturing-first warehouse; each domain switches on independently | two new modules over time; core must publish a PO port first |

**Recommended layering.** Dependencies point downward only, as india does. No `wh_`/`whb_` table ever gets an FK to a sibling table.

```
warehouse-base  (ledger, masters, catalogues)
   └─ warehouse (core)  — gate entry, GRN+bill, QC bands, MRN, material requisition,
   │                      store issue (cost object on lines), store return, PO types + schedule lines
   ├─ warehouse-procurement (new, ai.warehouseprocurement, V550000–V559999)
   │      PR → RFQ/quotation → award → rate contract / blanket agreement → creates & releases POs via a core port
   ├─ warehouse-manufacturing (new, ai.warehousemanufacturing, V560000–V569999)
   │      multi-level BOM, production order, issue-to-WIP / backflush, FG + co-product receipt,
   │      in-process/final QC, MRP; job work via warehouse-india seams
   ├─ warehouse-3pl  (kept — storage for third parties)
   └─ warehouse-india (kept — challan, e-way bill, job work/ITC-04)
```

**Core changes in every option:**
- `po_type` and schedule lines; open quantity on release lines only
- bill no/date/billed quantity on the GRN, and bill no/date/PO on gate entry
- configurable sampling-band table
- MRN authorisation step
- QC with a polymorphic source (GRN or production)
- a published PO-creation port, plus a PO contributor/guard seam
- removing the dead adapter flags from `WarehouseBaseModuleConfig.java:53`

**Future-proofing rules carried from R26:**
- Every vocabulary is code-list rows; no new CHECKs on extensible values.
- Each sibling's seed migration carries the owning-module check (`V521000:117` pattern) against the shared code namespace (`RL-003`).
- New bands and prefixes go into `DECISIONS.md` D-2/D-3.

## 7. Documentation changes needed

| Class | Files | Action |
|---|---|---|
| Spine docs | DECISIONS, FRD, COMPETITOR-BENCHMARK, IMPLEMENTATION-PLAN, PORT-AND-ADAPTER-CONTRACT, MODULE-INTEGRATION, DATA-MODEL §2.5.1, BUILD-SPEC-SCREENS (WS-194…198), README | REWRITE the sections listed below |
| Examples | SCENARIO-CATALOGUE, COEXISTENCE, INDIA-LOCALISATION-PACK, PLATFORM-DEPENDENCIES, IRREVERSIBLE, `classic/warehouse-base/INSTALL.md` | RELABEL the examples |
| Tasks | issues p2-24/25/26, p3-18/19, p6-09, p5-08/15, p2in-01, EPICs 00/03/04/07/08 | mark VOID or rewrite; ~20 more RELABEL |
| History | reviews R1–R26, GAP-REGISTER*, competitive/, reference/, BATCH-WAREHOUSE-* | **do not edit**; one superseded note per file pointing here |
| No change | `classic/CLAUDE.md` (adapter rows already REMOVED), `.claude/agents|commands`, QA, contracts | — |

**Load-bearing lines:**
- `DECISIONS.md` `:26, :52, :56, :108, :203, :265, :517, :577, :579, :582-584`
- FRD `:39, :82, :92-104, :175, :220, :475-483, :516, :519, :653-666, :745-759`, and refusals `:1084, :1094-1099`, `:1049`
- `COMPETITOR-BENCHMARK.md` `:47, :59, :99-105, :194, :502, :646, :654, :718-752`
- `IMPLEMENTATION-PLAN.md` `:36, :165-199, :272, :320-350, :494-496, :536, :607, :946, :1183, :1278-1289, :1364`

**Scale:** in `warehouse-issues`, about 145 files and 1,746 lines hit the dealer/retail terms, but only
about 19 spine files and 15 task files need real edits. In `classic`, about 37 files and 175 lines, mostly no change.

## 8a. Direction superseding §8 items 2–3 (user, 2026-10-22, later the same day)

- **Only the warehouse modules change** (`warehouse-base`, `warehouse`, `warehouse-3pl`, `warehouse-india`, plus new warehouse siblings). The separate `dealer`, `accessories`, `insurance` and `assets` modules are **not touched**.
- **No dealer module.** Dealer-related code (`RN-020`…`RN-024`, §3) is **removed from warehouse**. It will be recreated later if needed. This supersedes the `warehouse-dealer` / `warehouse-retail` sibling idea for dealer code.
- **Focus: manufacturing.** Purchase and sales both get manufacturing support, with sales mirroring purchasing step for step (§4 groups A and D).
- The project is in development with no clients, so a clean rewrite is allowed: no compatibility hacks or patches.
- Open: retail/e-commerce code (§2, §9), the migration handling, and the module placement of purchase/sales. Asked in one batch.

## 8b. Decisions (user, 2026-10-22) — authoritative; they override §6 option D, §8 and §9 where they differ

| ID | Decision |
|---|---|
| `RN-050` | **Retail/e-commerce code is removed from warehouse** like the dealer code (§2 `RN-010`…`RN-018`). It is recreated later only if a retail need appears. Generic shipping (carriers, services, accounts, labels, manifests, handovers, pickups, consignments, status mappings, tracking events, RMAs, return gradings) **stays in core**. §9's `warehouse-retail` extraction is withdrawn |
| `RN-051` | **Dual-use dealer items are renamed, not deleted:** `VOR` → line-stop / machine-down; `WORKSHOP` site type → production store; `OEM_PART_NUMBER` → manufacturer part no.; item supersessions stay (engineering change); Parts KPIs → Stock KPIs. **Deleted:** OEM obsolescence returns (and the `OBSOLESCENCE` claim type), the garage/sub-dealer Trade Portal, accessories coexistence (category ownership, external snapshots, coexistence report), dead adapter switches and labels (`RN-004`), and the dealer/retail seeded vocabulary (`RN-024`) |
| `RN-052` | **Clean rewrite, then rebuild the database.** Delete the removed features' migration files. Rewrite the mixed files (`RN-046`) so they neither create nor reference removed objects. Then drop and rebuild local/dev databases from scratch once. No drop migrations and no compatibility shims. This supersedes, for warehouse only, the standing "never wipe the dev DB" and "never edit an applied migration" rules |
| `RN-053` | **Module placement:** core `warehouse` keeps the shared stores pieces: gate entry, GRN with bill fields, sampling bands, MRN, material requisition, store issue with cost object, store return, PO/SO type and schedule-line schema, and the PO/SO creation ports. **New `warehouse-trade`** (`ai.warehousetrade`, proposed band `V550000`–`V559999`) holds purchase **and** sales together under one toggle: PR / sales enquiry → RFQ / customer quotation → award → rate contract → blanket/open/fixed order with delivery schedule → releases → amendments → approval. Sales mirrors purchase row for row. **New `warehouse-manufacturing`** (`ai.warehousemanufacturing`, proposed band `V560000`–`V569999`): multi-level BOM, production order, issue to WIP / backflush, FG + co-product receipt, in-process/final QC, MRP; job work through `warehouse-india`. `warehouse-3pl` and `warehouse-india` stay |
| `RN-054` | **Scope fence:** the separate `dealer`, `automotive`, `accessories`, `insurance`, `services` and `assets` modules are not edited. Accounting is deferred (`RM-030`…`RM-032` stay recorded) |

## 8c. Program plan (agreed sequence; the build loop starts only on the user's go)

1. **Decision record.** `DECISIONS.md` gains D-15, which records `RN-050`…`RN-054`, and the D-2/D-3 bands and prefixes for `warehouse-trade` and `warehouse-manufacturing`.
2. **Spine rewrite** (§7). Rewrite DECISIONS, FRD (scope, personas, segments, refusals), COMPETITOR-BENCHMARK, IMPLEMENTATION-PLAN, PORT-AND-ADAPTER-CONTRACT, MODULE-INTEGRATION, DATA-MODEL, BUILD-SPEC-SCREENS, SCENARIO-CATALOGUE and README. Historical files get one superseded note each.
3. **Functional requirements.** New FR rows for:
   - (a) removal of dealer and retail code, as a capability-level spec
   - (b) the core stores additions (`RM-007`…`RM-017`)
   - (c) `warehouse-trade`, purchase and sales mirrored (§4 A + D)
   - (d) `warehouse-manufacturing` (§4 C)

   Every row is scored against a reference process catalogue (`RM-040`).
4. **Functional contracts** per workflow (`/functional-contract`), each run through the `functional-reviewer` with the Claude + GPT dual engine (`.claude/scripts/functional-review-codex.sh`). Gaps are folded in before any task is written.
5. **Task files** in `issues/p*.md` plus phase EPICs, each also run through the functional reviewer, then **filed as GitHub issues** (`issues/create-issues.sh`, `CREATED.md`).
6. **BATCH files** in `classic/.claude/tasks/` via `/create-batch`, in the shape of `BATCH-WAREHOUSE-P*.md`.
7. **Stop for the user's go**, then `/run-batch`.

## 8. Decisions (user, 2026-10-22)

1. **Architecture: option D, layered — DECIDED.**
2. **Retail/e-commerce `RN-010`…`RN-018`: move into a new toggleable sibling `warehouse-retail` — DECIDED in principle.** The user wants them "enabled when we need it". §9 covers feasibility and the migration-strategy choice still open.
3. Dealer items `RN-020`…`RN-024`: **pending**. Re-asked with a plain explanation.
4. **Docs: rewrite the spine docs; historical files get a superseded note only — DECIDED.**

## 9. `warehouse-retail` extraction — feasibility

| ID | Finding | Evidence (`classic/`) |
|---|---|---|
| `RN-040` | **No FK from any core table to a retail table.** Retail tables point outward only (e.g. `wh_rto_consignments` → `wh_shipments`, `wh_return_receipts`) | grep of every `REFERENCES` in `warehouse/.../db/migration`; `V510050:509-540` |
| `RN-041` | **Core Java calls retail in four places:** `WhShipmentService` (AWB claim :282/:343/:376/:493; tracking notify :384/:534; RTO exists :469), `WhReturnReceiptService` (marketplace claim :338/:509; RTO linker :340/:510), `WhTrackingEventIngestService` (NDR :183; tracking :193), `WhDemandOrderValidationService:153` (a static codec) | `warehouse/backend/src/main/java/ai/warehouse/service/…` |
| `RN-042` | **Core native SQL reads retail tables** in the carrier/service-level delete guards. These fail if the tables are absent | `WhCarrierRepositoryCustomImpl.java:212-214`, `WhCarrierAccountRepositoryCustomImpl.java:210`, `WhCarrierServiceLevelRepositoryCustomImpl.java:193` |
| `RN-043` | **Retail columns on core tables stay in core:** `wh_demand_orders.channel_id`, `channel_account_id`, `payment_mode`, `cod_amount` (core despatch and carrier facts read `paymentMode`) | `V510040:97-154`; `WhDespatchService:214` |
| `RN-044` | **Flyway has no per-module locations.** Module SQL is copied into platform `db/migration` at image build, gated by `ENABLE_*`. `validate-on-migrate: true`, `out-of-order: true`, no `ignore-migration-patterns` | `FlywayConfiguration.java:92`; `shared/docker/Dockerfile.backend:206-245`; `application.yml:110-113` |
| `RN-045` | **Turning a module off on a database where its migrations were applied** → "applied migration not resolved locally" → `FlywayDriftGuard.repairAndRetry` marks those rows deleted. Re-enabling later would **re-run** them (menus and permissions re-inserted). The same latent hazard exists for `warehouse-3pl`/`warehouse-india` today | `FlywayDriftGuard.java:181-199` |
| `RN-046` | **12 migrations are retail-only** (`V510205-209`, `V510215`, `V510225-226`, `V511274`, `V511276-277`, `V511304`). **13 are mixed or core files that alter retail tables** (`V510050`, `V510204`, `V510227`, `V511000`, `V511235`, `V511268`, `V511271`, `V511273`, `V511275`, `V511306`, `V511308`, …). On a fresh install with retail off, the core ALTERs fail | per-file read |
| `RN-047` | **Size:** ~215 main Java, ~30 test, ~95 frontend files; 11 i18n sections; ~48 permission-constant and ~195 help-config lines to split | — |

**Verdict:** the Java and UI move once core gains about **six seams**:
- shipment lifecycle events (AWB, tracking, RTO)
- return-receipt posted/reversed listener (marketplace claim, RTO)
- carrier-event listener (NDR, tracking)
- carrier / service-level in-use counter SPI (replaces `RN-042`)
- optional AWB provider port
- optional mounting of the carrier-account scopes modal

Carrier account scopes (`V510204`) are edited from the core carrier-accounts page; **keep them in core**.

**Migration strategy options:**

| Option | What | Risk |
|---|---|---|
| **M-A (recommended)** | Leave the already-applied schema files in `warehouse`; the tables keep existing, harmless when unused. Move Java, UI, i18n, menus and permissions to `warehouse-retail`. New V550000+ migrations in the retail module activate its menus and permissions; a core migration deactivates them in core. All future retail schema goes in V550000+ | lowest; schema present even when disabled |
| M-B | Move the 12 retail-only files with their V510 numbers unchanged | breaks the band rule; disabling triggers `RN-045` repair and later re-run |
| M-C | Renumber to V55xxxx with a `flyway_schema_history` rewrite, and split or `to_regclass`-guard the 13 mixed files | highest: edits applied files (checksums), changes fresh-install order |
