# Open work index — every open warehouse issue, once
<!-- check-design-set: issue-citations file #323 #324 #386 #397 #519 #520 #539 #543 #610 #611 #613 #608 #609 #612 #614 #615 #616 #617 #618 #619 #620 #621 #622 #623 #624 #625 #626 #627 #628 #629 #630 #631 #632 #633 #634 — real issues in this repository filed as follow-ups outside create-issues.sh, so they have no task file and no CREATED.md row; listed here so every open issue appears once -->

**Updated 2026-10-24 (#566, #113, #123, #562, #577, #93, #567, #563, #564, #570, #54, #89, #13 closed; #608, #609, #610–#634 filed).** One row per open issue in `neetub1508/warehouse-issues`. Every piece of warehouse work sits in exactly one open issue; this file says which. Rebuild it whenever an issue opens or closes, and re-run the reconcile in §11.

**Order (user, 2026-10-23): `P7` first, then the rest.** *Must run after P7* is **true** where a `P7` task edits a file, class, table or permission the item touches, or the item adds a migration or schema change (`P7` rewrites the migration set in place once, `D-16` item 4, and `P7-13` rebuilds on it); all of `P8`–`P10` are true by `P7-13`'s rule. *Scope* says whether the whole task is to build or only its *Reopened scope* items.

**Totals: 130 open issues** — P7 1 · P8 10 · P9 15 · P10 15 · P5/P6 survivors 11 · reopened 35 · new findings 2 · old open findings 4 · other 37 (#539 #543 closed as carried by `P10-14` #605, 2026-10-23).

## 1. P7 — removal and the clean rebuild (run first) — 1 open

| Issue | Task file | Title | Scope | Must run after P7 | Why |
|---|---|---|---|---|---|
| #545 | `issues/09-EPIC-p7.md` | EPIC: P7 — Remove dealer and retail code, rename the dual-use items, rebuild on a clean… | epic (checklist of its tasks) | false | is P7 |

## 2. P8 — stores in core — 10 open

| Issue | Task file | Title | Scope | Must run after P7 | Why |
|---|---|---|---|---|---|
| #546 | `issues/10-EPIC-p8.md` | EPIC: P8 — Manufacturing stores in core (gate, bill-matched GRN, sampling QC, MRN, requ… | epic (checklist of its tasks) | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #565 | `issues/p8-04.md` | P8-04 · GRN bill number / date / billed quantity, the duplicate-bill guard, short recei… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #568 | `issues/p8-07.md` | P8-07 · QC reject → an explicit, manual "Raise supplier return" action (FR-139 amended … | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #569 | `issues/p8-08.md` | P8-08 · MRN — material receipt note authorised by a second person, MRN_PENDING as the s… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #571 | `issues/p8-10.md` | P8-10 · Store issue to VIRT-CONSUMED with a cost object (department / cost centre / pro… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #572 | `issues/p8-11.md` | P8-11 · Store return — linked to the issue line, partial, valued at the issue cost, con… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #573 | `issues/p8-12.md` | P8-12 · Stores print documents — gate entry slip, RGP/NRGP gate pass, GRN with the bill… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #574 | `issues/p8-13.md` | P8-13 · Stores registers and performance — RGP pending / overdue, requisitions pending … | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #575 | `issues/p8-14.md` | P8-14 · Stores menus, settings registry, i18n and filter-scope wave for P8 — within the… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #576 | `issues/p8-15.md` | P8-15 · The RMA-creation port for sales-return authorisation, and the supplier-return i… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |

## 3. P9 — `warehouse-trade` — 15 open

| Issue | Task file | Title | Scope | Must run after P7 | Why |
|---|---|---|---|---|---|
| #547 | `issues/11-EPIC-p9.md` | EPIC: P9 — `warehouse-trade`: manufacturing purchase and sales, mirrored | epic (checklist of its tasks) | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #578 | `issues/p9-01.md` | P9-01 · The trade module — `warehouse-trade` scaffold, enable flag, menu tree and the p… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #579 | `issues/p9-02.md` | P9-02 · Trade masters — supplier and customer trade profiles, approved vendor list, cus… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #580 | `issues/p9-03.md` | P9-03 · The trade approval matrix — rules, levels, maker ≠ checker, delegation, escalat… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #581 | `issues/p9-04.md` | P9-04 · Purchase requisition — manual, from stores shortage, from replenishment / MRP; … | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #582 | `issues/p9-05.md` | P9-05 · Sourcing — RFQ to many suppliers, vendor quotations with versions, comparative … | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #583 | `issues/p9-06.md` | P9-06 · Agreed prices, both sides — purchase rate contracts, sales rate contracts, pric… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #584 | `issues/p9-07.md` | P9-07 · Purchase orders — FIXED, OPEN and BLANKET with delivery schedules, releases, an… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #585 | `issues/p9-08.md` | P9-08 · Pre-sales — sales enquiry, customer quotation with versions, regret, won / lost… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #586 | `issues/p9-09.md` | P9-09 · Sales orders — FIXED, OPEN and BLANKET with the customer delivery schedule, dis… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #587 | `issues/p9-10.md` | P9-10 · Acknowledgement, expediting / commitment tracking, short-close and auto-close —… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #588 | `issues/p9-11.md` | P9-11 · Order amendments and versions — one engine, PO and SO, with snapshots, port pus… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #589 | `issues/p9-12.md` | P9-12 · Counterparty evaluation — vendor rating and customer rating / OTIF on one weigh… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #590 | `issues/p9-13.md` | P9-13 · Sales return authorisation → core RMA, and the purchase-side replacement reinst… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #591 | `issues/p9-14.md` | P9-14 · Trade print documents and the trade reports pack | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |

## 4. P10 — `warehouse-manufacturing` — 15 open

| Issue | Task file | Title | Scope | Must run after P7 | Why |
|---|---|---|---|---|---|
| #548 | `issues/12-EPIC-p10.md` | EPIC: P10 — Manufacturing (warehouse-manufacturing) | epic (checklist of its tasks) | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #592 | `issues/p10-01.md` | P10-01 · The manufacturing module — `warehouse-manufacturing` scaffold, enable flag, me… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #593 | `issues/p10-02.md` | P10-02 · Manufacturing registries — movement, document and location types, code lists, … | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #594 | `issues/p10-03.md` | P10-03 · Bill of materials — multi-level, versioned, maker–checker BOMs with alternates… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #595 | `issues/p10-04.md` | P10-04 · Work centres and the optional BOM operation list — a lightweight routing that … | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #596 | `issues/p10-05.md` | P10-05 · Production orders — BOM snapshot, release with availability check and componen… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #597 | `issues/p10-06.md` | P10-06 · Material to the order — staging to line-side, manual issue and return through … | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #598 | `issues/p10-07.md` | P10-07 · Production receipt — FG, co- and by-products in one movement with backflush an… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #599 | `issues/p10-08.md` | P10-08 · Operation confirmations, in-process and final QC through the core polymorphic … | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #600 | `issues/p10-09.md` | P10-09 · Actual costing of output, exact co-product split, close by settlement, and the… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #601 | `issues/p10-10.md` | P10-10 · Subcontracting and job work — subcontract orders, dispatch to the job worker, … | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #602 | `issues/p10-11.md` | P10-11 · Planning masters — item planning parameters per item × site and demand plans (… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #603 | `issues/p10-12.md` | P10-12 · MRP — regenerative per-site run, netting with low-level codes, lot sizing and … | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #604 | `issues/p10-13.md` | P10-13 · Capacity load (infinite, visible) and the manufacturing registers — production… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |
| #605 | `issues/p10-14.md` | P10-14 · Bonded / MOOWR stock to production and to a job worker — bond rules read by th… | whole task | **true** | `P7-13`: P8–P10 start only after P7 is merged |

## 5. P5/P6 survivors (P5 has none open; P6 v3 tasks that survive `D-16`/`D-17`/`D-18`, plus the open P4 task and epics) — 11 open

| Issue | Task file | Title | Scope | Must run after P7 | Why |
|---|---|---|---|---|---|
| #8 | `issues/06-EPIC-p4.md` | EPIC: P4 — India statutory & compliance | epic (checklist of its tasks) | false | no P7 file in scope |
| #11 | `issues/08-EPIC-p6.md` | EPIC: P6 — Optimisation, planning and the logistics seam | epic (checklist of its tasks) | false | no P7 file in scope |
| #75 | `issues/p4-11.md` | P4-11 · A second, tax-basis inventory value carried alongside the book value | whole task | false | no P7 file in scope |
| #94 | `issues/p6-01.md` | P6-01 · Archiving as a transaction — an `OPENING_BALANCE` movement at the cut-off befor… | whole task | false | no P7 file in scope |
| #103 | `issues/p6-03.md` | P6-03 · Measured labour, not engineered standards — and the refusal is the requirement | whole task | **true** | P7 also edits: `CacheConfiguration` |
| #109 | `issues/p6-04.md` | P6-04 · Automation, AS/RS and robotics through a published task-event contract and the … | whole task | false | no P7 file in scope |
| #112 | `issues/p6-05.md` | P6-05 · Receipt facts emitted as evidence — and the supplier scorecard is deliberately … | whole task | **true** | P7 also edits: `wh_purchase_orders`, `whb_item_identifiers` |
| #118 | `issues/p6-06.md` | P6-06 · The `party-base` extraction trigger is recorded, not acted on | whole task | false | no P7 file in scope |
| #122 | `issues/p6-07.md` | P6-07 · 3PL v3 — rate escalation as a new version, the SLA credit as a negative billabl… | whole task | false | no P7 file in scope |
| #131 | `issues/p6-08.md` | P6-08 · The `logistics` module — trips, ePOD and freight settlement, posting through th… | whole task (+1 tracking item 2026-10-23) | **true** | P7 also edits: `CacheConfiguration`, `filterUtils`, `wh_carrier_accounts`, `wh_carrier_services` |
| #138 | `issues/p6-10.md` | P6-10 · The real-time operations dashboard on the platform widget framework | whole task | **true** | P7 also edits: `CacheConfiguration`, `registry` |

## 6. Reopened — R30/R31 scope (`reopened-r31`) — 35 open

| Issue | Task file | Title | Scope | Must run after P7 | Why |
|---|---|---|---|---|---|
| #14 | `issues/p3-02.md` | P3-02 · Task assignment pull and push from one table, the supervisor exception console,… | reopened items only (1) | **true** | adds a migration / schema change — P7 rewrites the migration set (`D-16` item 4) |
| #17 | `issues/p5-01.md` | P5-01 · `warehouse-3pl` scaffold, the client as an object, and the build-time proof tha… | reopened items only (3) | **true** | adds a migration / schema change — P7 rewrites the migration set (`D-16` item 4) |
| #20 | `issues/p1-02.md` | P1-02 · UoM and identity — one scan-resolution service, and a barcode that resolves to … | reopened items only (1) | **true** | adds a migration / schema change — P7 rewrites the migration set (`D-16` item 4) |
| #28 | `issues/p3-05.md` | P3-05 · The ASN as a document, live dock appointments, and seals captured at load and a… | reopened items only (1) | false | no P7 file in scope |
| #29 | `issues/p2-03.md` | P2-03 · Holds as records with a release audit, not a status column | reopened items only (1) | false | no P7 file in scope |
| #30 | `issues/p5-04.md` | P5-04 · Storage billing in four methods, and the minimum monthly charge as a metered tr… | reopened items only (1) | **true** | adds a migration / schema change — P7 rewrites the migration set (`D-16` item 4) |
| #33 | `issues/p1-03.md` | P1-03 · The item's commercial and compliance block, and every statutory date as a DATE | reopened items only (5) | **true** | P7 also edits: `WhbItemSupersessionService`, `whb_warehouses` |
| #35 | `issues/p5-05.md` | P5-05 · The billing run with a frozen approved state, accessorials, disputes, and the A… | reopened items only (2) | **true** | adds a migration / schema change — P7 rewrites the migration set (`D-16` item 4) |
| #36 | `issues/p3-07.md` | P3-07 · The pack session as an operator flow, and scan verification as configuration pe… | reopened items only (1) | false | no P7 file in scope |
| #37 | `issues/p2-04.md` | P2-04 · Counting — a document that proposes an adjustment and never writes on-hand | reopened items only (1) | false | no P7 file in scope |
| #39 | `issues/p5-06.md` | P5-06 · Four freight-billing modes, and the client's own carrier account | reopened items only (1) | **true** | P7 also edits: `Wh3plFreightBillingService` |
| #42 | `issues/p2-05.md` | P2-05 · Expiry is a state, not an alert — and the four shelf-life enforcement points na… | reopened items only (1) | false | no P7 file in scope |
| #44 | `issues/p5-07.md` | P5-07 · SLA definitions, measurements and breaches as objects, and the portal's perform… | reopened items only (1) | false | no P7 file in scope |
| #53 | `issues/p2-07.md` | P2-07 · Allocation — soft and hard reservations, expiry as a job, strategy as a configu… | reopened items only (1) | false | no P7 file in scope |
| #57 | `issues/p3-11.md` | P3-11 · Work orders as VAS and light manufacturing — assembly that balances by value, r… | reopened items only (2) | false | no P7 file in scope |
| #65 | `issues/p2-09.md` | P2-09 · Discrete picking to a real staging location, and dispatch as the only inventory… | reopened items only (1) | **true** | P7 also edits: `WhDemandOrderService` |
| #66 | `issues/p3-13.md` | P3-13 · Order edit after release as a seeded rule matrix, and fulfilment policy per own… | reopened items only (1) | **true** | adds a migration / schema change — P7 rewrites the migration set (`D-16` item 4) |
| #70 | `issues/p1-07.md` | P1-07 · Lots, serials and LPNs as entities, and genealogy recorded at the moment of tra… | reopened items only (1) | false | no P7 file in scope |
| #71 | `issues/p0-08.md` | P0-08 · The movement port — a wire contract you cannot take back | reopened items only (1) | false | no P7 file in scope |
| #83 | `issues/p0-10.md` | P0-10 · Tasks — the execution object, in v1, because a duration cannot be backfilled | reopened items only (1) | false | no P7 file in scope |
| #88 | `issues/p4-13.md` | P4-13 · The regulated-goods licence pack — one licence object, one expiry clock, one de… | reopened items only (1) | false | no P7 file in scope |
| #90 | `issues/p3-18.md` | P3-18 · Migration mapping profiles, twelve months of demand history, and the OEM price … | reopened items only (1) | false | no P7 file in scope |
| #92 | `issues/p1-10.md` | P1-10 · The import framework in the handler-registry shape, with a reversal path | reopened items only (1) | false | no P7 file in scope |
| #106 | `issues/p2-15.md` | P2-15 · Replenishment as a document, demand history maintained by posting, and lost sal… | reopened items only (2) | **true** | P7 also edits: `wh_purchase_orders` |
| #110 | `issues/p0-14.md` | P0-14 · The adapter contract as artefacts — the example adapter, the coupling test, the… | reopened items only (1) | false | no P7 file in scope |
| #115 | `issues/p2-16.md` | P2-16 · The costing engine (D-6) — layers, consumption, weighted average and FIFO | reopened items only (2) | **true** | P7 also edits: `filterUtils` |
| #128 | `issues/p2-18.md` | P2-18 · The accounting handover — one valued envelope per event, and a rejected-handove… | reopened items only (1) | **true** | P7 also edits: `filterUtils` |
| #130 | `issues/p2in-01.md` | P2-IN-01 · The fifth module — `warehouse-india` scaffold, GSTIN profiles and compliance… | reopened items only (1) | false | no P7 file in scope |
| #133 | `issues/p1-17.md` | P1-17 · Transfer-order schema with the India and ownership hooks | reopened items only (1) | false | no P7 file in scope |
| #135 | `issues/p2in-02.md` | P2-IN-02 · The compliance-provider abstraction, transplanted rather than reinvented | reopened items only (1) | false | no P7 file in scope |
| #139 | `issues/p1-19.md` | P1-19 · i18n en/fr/hi, SafeTranslation registration, and the status badge from a regist… | reopened items only (1) | **true** | adds a migration / schema change — P7 rewrites the migration set (`D-16` item 4) |
| #140 | `issues/p2in-03.md` | P2-IN-03 · The delivery challan as a numbered document on its own per-branch series — a… | reopened items only (1) | false | no P7 file in scope |
| #141 | `issues/p2-21.md` | P2-21 · Report pack 2 — the adjustment register, count variance, low stock, KPIs with f… | reopened items only (2) | **true** | renamed by `P7-11` (`WhPartsKpi*` → Stock KPIs) |
| #146 | `issues/p2-23.md` | P2-23 · Approval permissions distinct from execution permissions, and the approver may … | reopened items only (1) | **true** | adds a migration / schema change — P7 rewrites the migration set (`D-16` item 4) |
| #147 | `issues/p2in-04.md` | P2-IN-04 · The e-way bill lifecycle implemented in v1, not just its number — and the ga… | reopened items only (2) | false | no P7 file in scope |

## 7. New findings W72+ — 2 open

| Issue | Task file | Title | Scope | Must run after P7 | Why |
|---|---|---|---|---|---|
| #606 | `issues/finding-w72.md` | [Finding] W72 · Counterfeit control has no open owner after P3-24 was closed not planned | whole task | false | no P7 file in scope |
| #607 | `issues/finding-w73.md` | [Finding] W73 · Nine non-functional rules are verified only by the reviewer gate | whole task | **true** | scanners read pages P7 removes / renames |

## 8. Old open findings (W01–W71) — 4 open

| Issue | Task file | Title | Scope | Must run after P7 | Why |
|---|---|---|---|---|---|
| #227 | `issues/finding-w33.md` | [Finding] W33 · Warehouse-only disaster recovery is not demonstrated | whole task | false | no P7 file in scope |
| #232 | `issues/finding-w38.md` | [Finding] W38 · Physical scanner, printer and device operation is not field-proven | whole task | false | no P7 file in scope |
| #240 | `issues/finding-w46.md` | [Finding] W46 · Optional tax-basis valuation remains deferred | whole task | false | no P7 file in scope |
| #241 | `issues/finding-w47.md` | [Finding] W47 · Provider-backed operational features require actual connector evidence | whole task | false | no P7 file in scope |

## 9. Other open issues (master epic and follow-ups without a task file) — 37 open

Dispositions 2026-10-23: none is unbatched. #1 counts via `CLOSE-1` of each batch; #173 #174 #175 are `[!] DEFERRED` (accounting) and #185 #323 #324 #386 #519 #520 `[!] BLOCKED`, all listed in `BATCH-WAREHOUSE-REOPENED-R31.md` § Deferred / blocked. #539 and #543 were **closed (duplicate) as CARRIED** by `P10-14` #605 (`issues/p10-14.md:164` — #539 items 1–2 added as an acceptance item — and `:168`; item 3 and #543 decided by `D-18` item 1). #397 was already closed.

| Issue | Task file | Title | Scope | Must run after P7 | Why |
|---|---|---|---|---|---|
| #1 | `issues/00-EPIC-master.md` | EPIC: Warehouse and inventory management — master | epic (checklist of its tasks) | **true** | P7 also edits: `CacheConfiguration`, `filterUtils` |
| #610 | — (follow-up of `issues/p8-05.md`) | P8-05 follow-up: seed the ISO 2859-1 / Z1.4 AQL sampling table family | whole issue | false | P8-05 carry G10; needs a licensed table |
| #611 | — (follow-up of `issues/p8-01.md`) | P8-01 follow-up: an OPEN purchase order's header value is 0 while the value-on-order tile counts its firm lines | whole issue | false | P8-01 S5 deviation; no spec text for an OPEN header value |
| #613 | — (follow-up of `issues/p8-16.md`) | P8-16 follow-up: replaying an empty published suggestion group answers 201 instead of 200 | whole issue | false | P8-16 S5 deviation (low); body correct, status only |
| #608 | — (no task file; tracking hygiene) | Issue mirror sync never checks titles — #30 and #80 have drifted | whole issue | false | `issues/create-issues.sh` tooling only; no code |
| #609 | — (no task file; settings governance) | GLOBAL-SETTINGS catalogue misses P8–P10 and contract-only setting keys | whole issue | false | doc-only (`GLOBAL-SETTINGS-DECISIONS.md`); P8 keys land with `P8-14` #575 |
| #612 | — (follow-up of `issues/p1-05.md`) | WhbLocationCustodyModal uses raw HTML controls, a hand-rolled tab strip, window.confirm and useEffect fetching | whole issue | false | R31 #54 reviewer gate; sibling of the new Dedicated owners modal |
| #614 | — (follow-up of `issues/p0-11.md`) | warehouse-base catalogue modals: replace native confirm() with ConfirmDialog (6 modals) | whole issue | false | R31 #89 S4 re-verify; `WhbLocationDedicatedOwnersModal` (#54) is the pattern |
| #615 | — (follow-up of `issues/p1-01.md`) | WhWarehouseScopeContractTest.SITE_SCOPED_TABLES drifted from the warehouse-base list (3 tables missing) | whole issue | false | R31 #13 barrier added `whb_item_uom_defaults` to the base list only |
| #616 | — (follow-up of `issues/p8-02.md`) | Port replay must re-check the post-lock verb: audit P8-01 PO port and P8-16 replenishment port (D8 template) | whole issue | false | P8-02 S3 F5/F11; P8-02 fixed (12305dfd73), closed siblings to audit |
| #617 | — (follow-up of `issues/p8-01.md`) | P8-01 PO schedule overdue digest: stamp does not re-check overdue; re-notify period compares instants | whole issue | false | found fixing P8-03 #564 F7/F8 |
| #618 | — (follow-up of `issues/p8-03.md`) | Audit single-id includeId pickers for scope widening (id = :includeId OR …) across warehouse | whole issue | false | P8-03 S4 read-leak fix; same shape elsewhere |
| #619 | — (follow-up of the R31/P8 barrier) | warehouseHelp: 78 help keys missing for carrierStatusMappings and trackingEvents pages (en/fr/hi) | whole issue | false | barrier writer 7fcaa0c3fb cross-check; i18n only |
| #620 | — (follow-up of `issues/p8-09.md`) | WhbAlertNotifier swallows delivery failures, so a once-only reminder latch is set for undelivered alerts (all stamp-and-tell jobs) | whole issue | false | P8-09 S3/S5; shared by P8-01 and P8-03 jobs |
| #621 | — (follow-up of `issues/p8-09.md`) | reasonCode.byCode labels are code-only: DUPLICATE/OTHER show other groups' wording on requisition reason pickers | whole issue | false | P8-09 barrier writer (87dec2c996) |
| #622 | — (follow-up of `issues/p8-06.md`) | GR line does not expose the inspection plan assignment that decided its status (P8-06 follow-up) | whole issue | false | P8-06 S5 deviation |
| #623 | — (follow-up of `issues/p8-09.md`) | Requisitions: Approve shown to a non-head approver under DEPARTMENT_HEAD policy (then 403) (P8-09 #570 follow-up) | whole issue | false | P8-09 S5 deviation (UI flag; server refuses) |
| #624 | — (follow-up of `issues/p8-09.md`) | Requisitions: contract decisions to ratify: zero estimate skips second approval, open required-by date, raw reason description (P8-09 #570) | whole issue | false | P8-09 decisions built as defaults; ratification owed |
| #625 | — (follow-up of `issues/p8-09.md`) | Requisitions / CN-14: flows not runtime-testable without MFG and buying modules (P8-09 #570 test debt) | whole issue | false | needs P10 (MFG) and P9 (buying) owner beans |
| #626 | — (follow-up of `issues/p8-03.md`) | Gate entries/passes: validation and flag gaps from P8-03 S5 (uomCode, direction/purpose, can* flags, cancel strictness) | whole issue | false | P8-03 S5 deviations (low) |
| #627 | — (follow-up of `issues/p8-02.md`, `issues/p8-03.md`, `issues/p8-09.md`) | Grid /management with no sortBy returns oldest-first, not the contract default created DESC (shared BaseController) | whole issue | false | P8-02/P8-03/P8-09 S5; shared `BaseController` default |
| #628 | — (follow-up of `issues/p8-02.md`) | Demand orders: port edge behaviours from P8-02 S5 (no-op amend bumps revision, null revision message, create-after-cancel, partial reduction after release) | whole issue | false | P8-02 S5 deviations |
| #629 | — (follow-up of `issues/p1-01.md`) | Item UoM defaults: PO uom-default with unknown warehouseId returns 204 (not 404); effectiveFrom ignores its @JsonFormat (R31 #13) | whole issue | false | R31 #13 S5 deviations (low) |
| #630 | — (follow-up of `issues/p1-05.md`) | Location dedications: runtime test gaps and same-owner re-add error ordering (R31 #54) | whole issue | false | R31 #54 S5 deviations / test debt |
| #631 | — (follow-up of `issues/p8-06.md`) | Inspection plans: test-resolution reads at start of date; inspectable-stock picker positive case untested (P8-06 #567) | whole issue | false | P8-06 S5 deviation / test debt |
| #632 | — (no task file; process) | Process: rebase.autoStash is on in both repos, contradicting the batch never-stash rule | whole issue | false | repo config; no code |
| #633 | — (no task file; QA fixtures) | QA fixture residue needing manual cleanup after P8/R31 S5 runs | whole issue | false | local dev stack data only; no code |
| #634 | — (follow-up of `issues/p8-09.md`) | Requisitions: first approver can still reject at the final-approval step (contract decision) | whole issue | false | P8-09 S5; contract decision owed |
| #173 | — (no task file) | Follow-up · Accounting envelope v2 — duty status, lot, serial and exchange rate per line | whole issue | — | **DEFERRED-ACCOUNTING** — label `deferred-accounting`; `[!] DEFERRED` in `BATCH-WAREHOUSE-REOPENED-R31.md` § Deferred / blocked (receivers accounting #36/#37, adapter P4-01) |
| #174 | — (no task file) | Follow-up · The accounting-facing adapter has no home — no module owns WhbAccountingHan… | whole issue | — | **DEFERRED-ACCOUNTING** — label `deferred-accounting`; `[!] DEFERRED` in `BATCH-WAREHOUSE-REOPENED-R31.md` § Deferred / blocked (adapter home accounting P4-01) |
| #175 | — (no task file) | Follow-up · Prove INTEGRATED mode end to end — WH-SC-156, WH-SC-157, CONFIG-CASE-07/10 | whole issue | — | **DEFERRED-ACCOUNTING** — label `deferred-accounting`; `[!] DEFERRED` in `BATCH-WAREHOUSE-REOPENED-R31.md` § Deferred / blocked (needs receiver + #174 adapter) |
| #185 | — (no task file) | RH-010 unmet: WS-215 cannot be scheduled without a platform commit | whole issue | — | **BLOCKED-EXTERNAL** — platform commit not approved (USER 2026-10-05); `[!] BLOCKED` in `BATCH-WAREHOUSE-REOPENED-R31.md` § Deferred / blocked; also blocks `P5-07` #44 |
| #323 | — (no task file) | [Follow-up W69] Part A-only e-way bill never lapses locally - challan held after the ca… | whole issue | — | **BLOCKED-EXTERNAL** — India tax adviser lapse ruling; `[!] BLOCKED` in `BATCH-WAREHOUSE-REOPENED-R31.md` § Deferred / blocked |
| #324 | — (no task file) | [Follow-up W69] Already-live Part A owned by a released bill cannot be reconciled witho… | whole issue | — | **BLOCKED-EXTERNAL** — customer GSP API contract via W47 #241; `[!] BLOCKED` in `BATCH-WAREHOUSE-REOPENED-R31.md` § Deferred / blocked |
| #386 | — (no task file) | F380 · Concurrent posting near-serialised: 10 posters ≈1.3× one poster, 50 posters exce… | whole issue | — | **BLOCKED-EXTERNAL** — USER ruling 2026-10-05 do not build (ledger owner); `[!] BLOCKED` in `BATCH-WAREHOUSE-REOPENED-R31.md` § Deferred / blocked; `P10-07` #598 only measures |
| #519 | — (no task file) | [!] type C, W53 follow-up: production sizing: customer target profile [!1] and deployme… | whole issue | — | **BLOCKED-EXTERNAL** — customer profile + deployment sizing; `[!] BLOCKED` in `BATCH-WAREHOUSE-REOPENED-R31.md` § Deferred / blocked |
| #520 | — (no task file) | W53 follow-up (G9): HTTP concurrent-user load and browser time-to-interactive, owner USER | whole issue | — | **BLOCKED-EXTERNAL** — USER load/TTI environment; `[!] BLOCKED` in `BATCH-WAREHOUSE-REOPENED-R31.md` § Deferred / blocked |

## 10. Code-divergence triage (2026-10-23) — 103 rows

Every `XXX-DIV-nn` row and every *Code divergences* table row in `docs/contracts/*.contract.md` (`costing-valuation` row 6 was already deleted by R31). Each contract row carries the same verdict inline as **Triage 2026-10-23**. Counts: **FIX-CODE 49**, **AMEND-SPEC 32**, **CARRIED 14**, **P7-REMOVES 8** (13 marked *reviewer-confirm*).

- **FIX-CODE** — the code must change; the owner is named. A closed owner was reopened with the item in its *Reopened scope*; an open owner got an acceptance item (`P7-11`, `P6-08`); no sensible owner → new finding (`W72`, `W73`).
- **AMEND-SPEC** — the code is right (code comment, decision or later migration); the FRD / contract / BUILD-SPEC was edited now and the row restated as a rule. Rows marked *applied R31* were already amended.
- **CARRIED** — an open task or a `P8`–`P10` task builds it. **P7-REMOVES** — residue a `P7` task deletes.

| Contract | Row | Verdict | Owner / rule and evidence |
|---|---|---|---|
| `3pl-billing` | TPB-DIV-01 | FIX-CODE | owner `P5-04` #30, reopened (Reopened scope) |
| `3pl-billing` | TPB-DIV-02 | AMEND-SPEC | rule: the FRD's *daily average* method is stored as the code value `AVERAGE_DAILY` (label "Daily average"); same behaviour, the value is the build's. Evidence: `Wh3plStorageBillingCalculator.java:99`, `:121` |
| `3pl-billing` | TPB-DIV-03 | AMEND-SPEC | rule: the portal stays a read surface plus dispute raise; a client user creates ASNs and outbound orders through the existing screens' own verbs under owner scope (`FR-284`: *a permission surface over the existing screens*). Evidence: `issues/p5-08.md:173` (recorded at build, *portal_access is read-only by construction*); `FR-284` amended. reviewer-confirm |
| `3pl-billing` | TPB-DIV-04 | FIX-CODE | owner `P5-01` #17, reopened: client-created documents draw from the per-client series, proved by a test |
| `3pl-billing` | TPB-DIV-05 | CARRIED | `P6-07` #122 (v3, `FR-299`) |
| `3pl-billing` | TPB-DIV-06 | CARRIED | `P6-07` #122 (v3, `FR-302`) |
| `3pl-billing` | TPB-DIV-07 | CARRIED | `P6-07` #122 (v3, `FR-296`) |
| `3pl-billing` | TPB-DIV-08 | FIX-CODE | owner `P5-01` #17 (`FR-281`), reopened |
| `3pl-billing` | TPB-DIV-09 | FIX-CODE | owner `P5-05` #35 (`FR-291`), reopened |
| `3pl-billing` | TPB-DIV-10 | FIX-CODE | owner `P5-05` #35, reopened |
| `3pl-billing` | TPB-DIV-11 | FIX-CODE | owner `P5-07` #44 (`FR-298`), reopened; blocked on the platform `ReportType` commit (as `#185`) |
| `3pl-billing` | TPB-DIV-12 | FIX-CODE | owner `P5-06` #39, reopened |
| `access-scope` | §10/§11 row 1 | FIX-CODE | owner `P2-23` #146 (v2 increment), reopened |
| `accounting-handover` | §10/§11 row 1 | FIX-CODE | owner `P2-18` #128, reopened |
| `costing-valuation` | §10/§11 row 1 | FIX-CODE | owner `P2-16` #115 (v1.1 part of `FR-235`), reopened |
| `costing-valuation` | §10/§11 row 2 | AMEND-SPEC | rule: while accounting is not installed (`D-16` item 6, accounting deferred), revaluation is approved in warehouse under `wh_revaluations:approve`; with accounting installed the approval moves to it. `FR-240` amended. reviewer-confirm |
| `costing-valuation` | §10/§11 row 3 | AMEND-SPEC | rule: same as row 2 for NRV — warehouse approves and posts under `wh_nrv_assessments:approve` while accounting is deferred (`D-16` item 6). `FR-241` amended. reviewer-confirm |
| `costing-valuation` | §10/§11 row 4 | CARRIED | `P4-11` #75 (open, `FR-250`) and finding `W46` #240 |
| `costing-valuation` | §10/§11 row 5 | AMEND-SPEC | rule: `FR-232` already lists the six built values (R31 `AHO-OPEN-12`); `posting_status` is a fixed lifecycle, not one of the `IRREVERSIBLE.md` §5 catalogue columns, and the service is its only writer — no divergence remains |
| `costing-valuation` | §10/§11 row 7 | AMEND-SPEC | rule: warehouse enforces the stock side of the lock sync only; the accounting side belongs to the accounting module when installed (`D-16` item 6). `FR-251` amended |
| `costing-valuation` | §10/§11 row 8 | FIX-CODE | owner `P2-16` #115, reopened |
| `counterparty-master` | §10/§11 row 1 | FIX-CODE | no open owner — `P3-24` #121 closed not planned on `OD-17`, which covers GS1 only; new finding `W72` |
| `cycle-count` | CCT-DIV-01 | AMEND-SPEC | rule: the count variance posts as `COUNT_ADJUST` (manual) / `COUNT_ADJUST_AUTO` (auto-post), both `source_document_type = COUNT`. Evidence: `V500003` seed, `WhCountPostingService.java:68`. `FR-153` amended |
| `cycle-count` | CCT-DIV-02 | AMEND-SPEC | rule: the despatch point refuses below a minimum **percentage** of shelf life remaining (`min_shelf_life_ship_pct`), resolved counterparty → channel → item — the same unit as the receipt point. Evidence: `WhbShelfLifePolicyService.java:170-177` javadoc cites `FR-161`. `FR-161` amended. reviewer-confirm |
| `cycle-count` | CCT-DIV-03 | FIX-CODE | owner `P1-03` #33 (v1.1 increment, `V500069` + job), reopened |
| `cycle-count` | CCT-DIV-04 | FIX-CODE | owner `P2-03` #29 (v2 mass action), reopened |
| `cycle-count` | CCT-DIV-05 | FIX-CODE | owner `P2-04` #37, reopened |
| `facility-branch-link` | §10/§11 row 1 | CARRIED | `P8-10` #571 (store issue) |
| `facility-branch-link` | §10/§11 row 2 | FIX-CODE | owner `P1-17` #133 (v2), reopened |
| `facility-branch-link` | §10/§11 row 3 | FIX-CODE | owner `P3-02` #14, reopened |
| `import-go-live` | §10/§11 row 1 | FIX-CODE | owner `P1-10` #92, reopened |
| `import-go-live` | §10/§11 row 2 | FIX-CODE | owner `P3-18` #90 (v1.1), reopened |
| `india-movement-documents` | IMD-DIV-01 | AMEND-SPEC | applied R31 (`FR-319` restated); stands as the rule |
| `india-movement-documents` | IMD-DIV-02 | AMEND-SPEC | applied R31 (clause withdrawn); stands as the rule |
| `india-movement-documents` | IMD-DIV-03 | FIX-CODE | owner `P2-IN-02` #135, reopened (architecture test) |
| `india-movement-documents` | IMD-DIV-04 | AMEND-SPEC | rule: no divergence — `FR-311` is v2/`P4`, and `P4-01` built the e-invoicing path in that wave (`WhinComplianceGatewayIrnTest`) |
| `india-movement-documents` | IMD-DIV-05 | AMEND-SPEC | withdrawn R31; stands as the rule `IMD-GRD-21` |
| `india-movement-documents` | IMD-DIV-06 | FIX-CODE | owner `P2-IN-04` #147 (`FR-195`), reopened |
| `india-movement-documents` | IMD-DIV-07 | FIX-CODE | owners `P2-IN-03` #140 and `P2-IN-04` #147, reopened |
| `item-master` | §10/§11 row 1 | FIX-CODE | owner `P1-03` #33 (`FR-071`), reopened |
| `item-master` | §10/§11 row 2 | FIXED | `P7-11` #559 closed 2026-10-24 — `mergeStock` posts one `SUPERSESSION_MERGE` movement per site (classic 906609a361, 7a7e699a38, 72e9dc87e2) |
| `item-master` | §10/§11 row 3 | AMEND-SPEC | rule: quantity is owned by the packaging row; the identifier row holds a **trigger-maintained** copy of `uom_code` / `pack_quantity` that no caller writes and two AFTER triggers re-derive when the level changes (`IRR-43`). Evidence: `V500016__…:38-40`, `:214`, `:317-327`. `FR-057` amended |
| `item-master` | §10/§11 row 4 | CARRIED | CARRIED → `P8-14` #575 (re-homed 2026-10-24, OD1) |
| `lot-serial-status` | §10/§11 row 1 | AMEND-SPEC | rule: the HS / HSN code is an item attribute carried by `whb_items.tax_classification_code` (`P1-03`, snapshotted onto documents), not a lot column — it does not vary by lot. `FR-095` amended. reviewer-confirm |
| `lot-serial-status` | §10/§11 row 2 | AMEND-SPEC | rule: SSCC allocation is deferred by the product owner's `OD-17` ruling (2026-09-24, #121 closed not planned; `V500056` stays reserved) until a customer brings a GS1 prefix. `FR-452` amended |
| `lot-serial-status` | §10/§11 row 3 | AMEND-SPEC | rule: EPC is deferred with the GS1 work by `OD-17` (#121). `FR-453` amended |
| `lot-serial-status` | §10/§11 row 4 | AMEND-SPEC | rule: the Digital Link parser is deferred by `OD-17` (#121); the v1 seed's refusal of `GS1_DIGITAL_LINK` is the supported boundary. `FR-454` amended |
| `lot-serial-status` | §10/§11 row 5 | FIX-CODE | owner `P2-05` #42, reopened |
| `module-contract` | MOD-DIV-01 | FIX-CODE | owner `P0-14` #110, reopened |
| `module-contract` | MOD-DIV-02 | AMEND-SPEC | applied R31 (FRs withdrawn); stands as the rule |
| `module-contract` | MOD-DIV-03 | AMEND-SPEC | rule: for warehouse only, `D-16` item 4 supersedes the never-edit rule once — a clean migration rewrite and one DB rebuild (`P7-13`); every later migration is forward-only again. `FR-374` amended |
| `movement-post-reverse` | §10/§11 row 1 | AMEND-SPEC | rule: `balance_rule` ∈ {`MUST_BALANCE_PER_OWNER_ITEM` (default), `MUST_BALANCE_PER_ITEM`, `MUST_BALANCE_PER_MOVEMENT` (value-only types)}; there is no `UNBALANCED_ALLOWED`; mixed owners are admitted by `is_ownership_transfer` on the type, or by `V501105` where a two-owner movement moving no title balances per owner and item; `allows_mixed_owner` lives on locations / location types. Evidence: `V500003:90`, `V501105:102` (a later migration). `FR-042` amended; `MPR-GRD-01` is the rule, `MPR-GRD-42` retired. reviewer-confirm |
| `movement-post-reverse` | §10/§11 row 2 | AMEND-SPEC | rule: the lineage index is the document triple `(source_system, source_document_type, source_document_id)`; line number and `source_line_ref` are resolved within that document, and the lineage `GET` is one index seek (`P0-08` acceptance). `FR-018` amended. reviewer-confirm |
| `movement-post-reverse` | §10/§11 row 3 | AMEND-SPEC | rule: exactly one house owner **per company** (`uk_whb_owners_house_per_company`, re-keyed by `V500073`, `D-14` item 8 multi-company). `FR-108` amended |
| `movement-post-reverse` | §10/§11 row 4 | FIX-CODE | owner `P1-19` #139 (v2 increment `V500071`), reopened |
| `movement-post-reverse` | §10/§11 row 5 | AMEND-SPEC | rule: the position key fires on nulls by `NULLS NOT DISTINCT` (`V500031`, `MPR-OPEN-10`). `FR-011` amended |
| `movement-post-reverse` | §10/§11 row 6 | AMEND-SPEC | rule: the accounting date is `posting_date` (`V500030:229`, `MPR-OPEN-04`). `FR-007` and `FR-032` amended |
| `movement-post-reverse` | §10/§11 row 7 | P7-REMOVES | `P7-05` #553 and `P7-10` #558 |
| `non-functional` | NFR-DIV-01 | CARRIED | `P6-01` #94 (archiving) |
| `non-functional` | NFR-DIV-02 | CARRIED | finding `W33` #227 (open; disaster recovery) |
| `non-functional` | NFR-DIV-03 | FIX-CODE | owners by parent table, each reopened: `P1-05` #54 `V500070`, `P0-11` #89 `V500074`, `P1-01` #13 `V500075`, `P1-02` #20 `V500076`, `P1-03` #33 `V500077` |
| `non-functional` | NFR-DIV-04 | FIX-CODE | resolved R31; menu hiding owner `P4-13` #88, reopened |
| `non-functional` | NFR-DIV-05 | AMEND-SPEC | rule: the eight numbers belong to `FR-534`'s system performance envelope (`FRD-STORES.md`, R30 `CP-FR-003`); the test and its numbers stand under that id |
| `non-functional` | NFR-DIV-06 | P7-REMOVES | `P7-02` #550 removes the waybill / AWB pools |
| `non-functional` | NFR-DIV-07 | FIX-CODE | no owning task — new finding `W73` |
| `non-functional` | NFR-DIV-08 | FIX-CODE | owners `P5-01` #17, `P2-IN-01` #130, `P0-08` #71, reopened; the page scanner is `W73` |
| `outbound-despatch` | ODS-DIV-01 | FIX-CODE | owner `P3-13` #66 (`FR-184`), reopened |
| `outbound-despatch` | ODS-DIV-02 | FIX-CODE | owner `P2-09` #65 (`FR-449`), reopened |
| `outbound-despatch` | ODS-DIV-03 | AMEND-SPEC | rule: false divergence — the 3PL SLA measure reads the calendar: `Wh3plSlaCalendarVerdict` and `Wh3plSlaDefinitionValidationService` use `WhWorkingCalendarService` (P5-10), the code the promise uses |
| `outbound-despatch` | ODS-DIV-04 | FIX-CODE | owner `P6-08` #131 (open; the logistics relocation and its deletion test) — acceptance item added. reviewer-confirm |
| `outbound-despatch` | ODS-DIV-05 | P7-REMOVES | `P7-10` #558 |
| `outbound-despatch` | ODS-DIV-06 | P7-REMOVES | `P7-04` #552 (payment columns) and `P7-02` #550 (pooled-tracking guard) |
| `outbound-despatch` | ODS-DIV-07 | FIX-CODE | owner `P3-07` #36, reopened |
| `outbox-events` | OEV-DIV-01 | AMEND-SPEC | applied R31 (`FR-338` restated); stands as the rule |
| `outbox-events` | OEV-DIV-02 | AMEND-SPEC | rule: the platform question was settled by `OD-8` (resolved 2026-09-11, `GLOBAL-SETTINGS-DECISIONS.md`): the port authenticates an ordinary platform user and the API client is a warehouse-base integration surface that narrows it. Evidence: `V500066` header *THE DECISION THIS FILE IMPLEMENTS*. `FR-458` amended |
| `outbox-events` | OEV-DIV-03 | CARRIED | `P6-08` #131 (`p6-08.md:120`, `:229` — the two deletion tests) |
| `receipt-qc-putaway` | RQP-DIV-01 | FIX-CODE | owner `P1-13` #113, reopened |
| `receipt-qc-putaway` | RQP-DIV-02 | FIX-CODE | owner `P3-05` #28 (`FR-136`), reopened |
| `receipt-qc-putaway` | RQP-DIV-03 | FIX-CODE | owner `P2-13` #93, reopened |
| `receipt-qc-putaway` | RQP-DIV-04 | FIX-CODE | owner `P2-13` #93, reopened |
| `replenishment` | §10/§11 row 1 | FIX-CODE | owner `P1-03` #33 (v1.1 part of `FR-252`), reopened. reviewer-confirm |
| `replenishment` | §10/§11 row 2 | FIX-CODE | owner `P2-15` #106 (`FR-260`), reopened. reviewer-confirm |
| `replenishment` | §10/§11 row 3 | FIX-CODE | owner `P2-15` #106, reopened |
| `replenishment` | §10/§11 row 4 | CARRIED | `P10-11` #602 |
| `reports-kpis` | §10/§11 row 1 | P7-REMOVES | `P7-11` #559 (the rename) |
| `reports-kpis` | §10/§11 row 2 | FIX-CODE | owner `P2-21` #141 (`FR-393`), reopened; runs after `P7-11` |
| `reports-kpis` | §10/§11 row 3 | FIX-CODE | owner `P2-21` #141 (`FR-394`), reopened. reviewer-confirm |
| `reports-kpis` | §10/§11 row 4 | CARRIED | `P8-13` #574 |
| `reports-kpis` | §10/§11 row 5 | CARRIED | `P6-10` #138 |
| `reports-kpis` | §10/§11 row 6 | P7-REMOVES | `P7-09` #557 |
| `reservation-allocation` | RSA-DIV-01 | AMEND-SPEC | rule: the FRD's *fewest locations* key is the code value `FEWEST_PICKS` (`WhbAllocationVocabulary`). `FR-172` amended |
| `reservation-allocation` | RSA-DIV-02 | FIX-CODE | owner `P2-07` #53 (`FR-176`), reopened |
| `returns-rma` | §10/§11 row 1 | P7-REMOVES | `P7-05` #553 and `P7-10` #558 |
| `returns-rma` | §10/§11 row 2 | P7-REMOVES | `P7-07` #555 |
| `returns-rma` | §10/§11 row 3 | FIX-CODE | owner `P5-23` #123 (`FR-459`), reopened |
| `stock-transfer` | STR-DIV-01 | AMEND-SPEC | applied R31 (WS-090 amended to the build); stands as the rule `STR-UNR-05` / `STR-GRD-06` |
| `stock-transfer` | STR-DIV-02 | AMEND-SPEC | applied R31 (contract corrected to the build, `F-CA-001`); `FR-147` defines the three legs, not the status ladder, so no FRD edit is owed |
| `task-execution-printing` | TEP-DIV-01 | CARRIED | `P6-03` #103 (`FR-228`: the column stays a manual reference until measured labour exists) |
| `task-execution-printing` | TEP-DIV-02 | CARRIED | `P6-04` #109 (v3 task-event contract, R31 `TEP-OPEN-01`) |
| `task-execution-printing` | TEP-DIV-03 | FIX-CODE | owner `P0-10` #83, reopened |
| `vas-work-order` | §10/§11 row 1 | FIX-CODE | owner `P3-11` #57 (`FR-261`), reopened. reviewer-confirm |
| `vas-work-order` | §10/§11 row 2 | AMEND-SPEC | rule: the work-order types are the four built codes `ASSEMBLY`, `DISASSEMBLY`, `REPACK`, `VAS` (`WhWorkOrder.java:109-118`); decanting is a `REPACK`. BUILD-SPEC WS-144 amended. reviewer-confirm |
| `vas-work-order` | §10/§11 row 3 | FIX-CODE | owner `P3-11` #57, reopened |

## 11. Reconcile with GitHub

`gh issue list --state open` was diffed against the issue numbers in §1–§9 at publication:

```
comm -3 <(gh issue list --repo neetub1508/warehouse-issues --state open --limit 1000 --json number -q '.[].number' | sort -n) \
        <(grep -oE '^\| #[0-9]+ \|' docs/reviews/OPEN-WORK-INDEX.md | tr -dc '0-9\n' | sort -n)
```

Result: **empty** — every open issue appears exactly once, nothing is missing (130 open issues on GitHub, 130 distinct rows here, 2026-10-24, after #567 #563 #564 #570 #54 #89 #13 closed and #608–#634 listed; was 129/129 on 2026-10-23).

**Batch reconcile (2026-10-23).** Every open issue has exactly one open batch line (`- [ ]` or `- [!]`) across `BATCH-WAREHOUSE-P4/P6/P7/P8/P9/P10/REOPENED-R31.md` in classic; the §9 follow-ups are the `[!] DEFERRED`/`[!] BLOCKED` lines in `REOPENED-R31.md` § Deferred / blocked, and the epics count via their close-out lines. Issues in no batch: **none**. (#88 also has a ticked `[x]` line in `P4.md`, its pre-reopen close; its one open line is in `REOPENED-R31.md`.)

## 12. Sweep and batch notes

- **Closed tasks with post-close work.** `git diff a793b83~1 HEAD -- issues/` added 24 unchecked items to **23** closed tasks (the request listed 22; `P2-15` #106 was the 23rd, with `RPN-OPEN-01`). The sweep of every other closed, non-VOID task found unchecked items newer than the close date in `P0-03` #34 and `P0-05` #49 (rewordings of items the code already meets: `WhbInsufficientStockRecorder`, `V500058` seeds `REJECTED`), `P1-03` #33 line 305 (the supplier-rung hand-off, settled by default by F391 / #397 and recorded in `receipt-qc-putaway` 2026-10-05), `P1-05` #54 (the `V500070` v2 items — reopened) and `P1-01` #13 (the `V500075` retype — reopened).
- **`BATCH-WAREHOUSE-P5.md`.** Its 20 unticked boxes are the *Definition of done* template (lines 202–236), not tasks; every P5 task box is ticked and every P5 issue was closed. The P5 work missing in code is reopened in §6 (`P5-01`, `P5-04`, `P5-05`, `P5-06`, `P5-07`, `P5-23`).
- **`BATCH-WAREHOUSE-P6.md`.** Its 32 unstarted lines are 22 *Definition of done* template boxes, 8 tasks and the two wave items `W5-1` / `W5-2`. The 8 tasks (`P6-01`, `-03`, `-04`, `-05`, `-06`, `-07`, `-08`, `-10`) carry no VOID header and no `D-16`/`D-17`/`D-18` item voids them; all 8 are open. `P6-02`, `P6-09`, `P6-11`, `P6-12` are VOID and closed not planned. `W5-1` / `W5-2` belong to the open P6 epic #11. GitHub state matches.
- **Old findings.** `W33` #227, `W38` #232, `W46` #240 and `W47` #241 stay open: each is `[!] FINAL` in `BATCH-WAREHOUSE-FINDINGS.md` on an **external** owner (deployment admin / customer DR drill; customer site devices; customer tax-basis requirement and adviser sign-off — the code has no `tax_basis`, `costing-valuation` §10 row 4; customer GSP / provider accounts). None can be closed from code evidence.
