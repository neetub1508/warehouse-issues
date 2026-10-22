# Created issues

Filed in `neetub1508/warehouse-issues`: **159 issues = 152 + 6 filed in round 4 + 1 filed in round 5
(`#163`, `P1-22`).** Open: **1 master epic + 8 phase epics + 144 tasks = 153.** The six round-4 task issues `#156`–`#161` are **closed as
duplicates** — each was folded into its most similar existing task on 2026-09-10 and has no task file.

> Verified against the file glob, which is the authority:
> `ls issues/p*.md | wc -l` → **144**; per phase
> `for p in p0 p1 p2 p2in p3 p4 p5 p6; do ls issues/$p-[0-9][0-9].md | wc -l; done`
> → **17 · 22 · 29 · 4 · 24 · 13 · 23 · 12**. `ls issues/*EPIC*.md | wc -l` → **9**
> (1 master + 8 phase). The headline is correct.

> **Round 4 (2026-09-10) filed six tasks, `#156`–`#161`:** `P3-25` and `P5-24`…`P5-28`
> (`docs/GAP-REGISTER-R4.md`), and the same day folded each into an existing host (user rule: no
> duplicate tasks; `GAP-REGISTER-R4.md` §4.6). Their rows below are kept, marked closed, so every
> `#156`–`#161` citation still resolves; a regeneration of this file must keep them. **`#155` is a pull request** (the round-3 review and backlog map),
> for the same reason as `#2` and `#9` below.

> **`#2` and `#9` are pull requests, not issues.** GitHub draws issue and pull-request
> numbers from one sequence per repository, and two PRs were opened while the backlog was
> being filed. That is why the master epic is `#1`, the phase epics are
> `#3 #4 #5 #6 #7 #8 #10 #11` — **not** `#2`–`#9` — and the 143 tasks run **#12–#154**
> rather than #10–#152. There is no gap in the backlog; the two missing numbers are the PRs.

> **Round 5 (2026-09-14) filed one task, `#163` = `P1-22`** (`DECISIONS.md` `D-14` item 8), for the
> built screens only, because closed tasks are never reopened. `#162` is a pull request (round 4).

> **The `.md` files win.** Every file below carries an `issue: NN` line in its front matter,
> which is what `create-issues.sh --sync` and `--check` read. GitHub is a mirror:
> `--sync` pushes, `--check` fails CI on drift. Never edit an issue body in the GitHub UI.
> See `issues/README.md`.

This is also the map `tools/check-design-set.py` check 5 resolves every `#NN`
cross-reference against — regenerate it with `create-issues.sh`, do not hand-edit it.

| Issue | Task file | Title |
|---|---|---|
| #1 | `00-EPIC-master.md` | EPIC: Warehouse and inventory management — master |
| #3 | `01-EPIC-p0.md` | EPIC: P0 — Ledger foundation |
| #4 | `02-EPIC-p1.md` | EPIC: P1 — Masters, identity, inbound |
| #5 | `03-EPIC-p2.md` | EPIC: P2 — Outbound, counting, valuation, returns, printing, reports |
| #6 | `04-EPIC-p2in.md` | EPIC: P2-IN — The India movement documents |
| #7 | `05-EPIC-p3.md` | EPIC: P3 — Execution & mobile |
| #8 | `06-EPIC-p4.md` | EPIC: P4 — India statutory & compliance |
| #10 | `07-EPIC-p5.md` | EPIC: P5 — 3PL, channels and reverse logistics |
| #11 | `08-EPIC-p6.md` | EPIC: P6 — Optimisation, planning and the logistics seam |
| #15 | `p0-01.md` | P0-01 · Five-module scaffold and the 16-file registration runbook |
| #25 | `p0-02.md` | P0-02 · The ledger — movements, lines, positions and every invariant trigger |
| #34 | `p0-03.md` | P0-03 · The single writer service, availability, concurrency and the L-4 rebuild |
| #43 | `p0-04.md` | P0-04 · The open-catalogue framework and the four the ledger cannot exist without |
| #49 | `p0-05.md` | P0-05 · The remaining ledger-facing registries, and status change as a balanced movement |
| #56 | `p0-06.md` | P0-06 · Owners — the column that cannot be added later |
| #63 | `p0-07.md` | P0-07 · Companies, the company axis, and stock periods with their close ladder |
| #71 | `p0-08.md` | P0-08 · The movement port — a wire contract you cannot take back |
| #77 | `p0-09.md` | P0-09 · Reservations as an open-item ledger, never a counter |
| #83 | `p0-10.md` | P0-10 · Tasks — the execution object, in v1, because a duration cannot be backfilled |
| #89 | `p0-11.md` | P0-11 · The transactional outbox — no precedent anywhere in this repository |
| #97 | `p0-12.md` | P0-12 · The accounting seam — handovers, posting rules, and the architecture test that keeps it shut |
| #104 | `p0-13.md` | P0-13 · The ledger is the audit trail — hash-chained events, job runs, and the dated-obligation register |
| #110 | `p0-14.md` | P0-14 · The adapter contract as artefacts — the example adapter, the coupling test, the ratchet |
| #117 | `p0-15.md` | P0-15 · Base permissions, verb permissions, menus, the first grid block and admin settings |
| #124 | `p0-16.md` | P0-16 · Non-functional foundations, written down so they can be tested against |
| #127 | `p0-17.md` | P0-17 · Cost-layer schema, DDL only — because the ledger line FKs to it |
| #13 | `p1-01.md` | P1-01 · The item master, its four status facts, and the variant schema |
| #20 | `p1-02.md` | P1-02 · UoM and identity — one scan-resolution service, and a barcode that resolves to a packaging level |
| #33 | `p1-03.md` | P1-03 · The item's commercial and compliance block, and every statutory date as a DATE |
| #40 | `p1-04.md` | P1-04 · Item external refs, item documents, and D-9's two mandatory mitigations |
| #54 | `p1-05.md` | P1-05 · The facility model — warehouses, the location hierarchy and the virtual-location seed |
| #60 | `p1-06.md` | P1-06 · The location generator, and dock doors as locations |
| #70 | `p1-07.md` | P1-07 · Lots, serials and LPNs as entities, and genealogy recorded at the moment of transformation |
| #78 | `p1-08.md` | P1-08 · Counterparties — a thin identity, because nothing else in the repo owns one |
| #84 | `p1-09.md` | P1-09 · Gapless document numbering from a locked counter row |
| #92 | `p1-10.md` | P1-10 · The import framework in the handler-registry shape, with a reversal path |
| #98 | `p1-11.md` | P1-11 · Channels, transport details, the activity-history view and the logistics-seam v1 columns |
| #105 | `p1-12.md` | P1-12 · Purchase orders — the layered-truth model and the lifecycle command centre |
| #113 | `p1-13.md` | P1-13 · Receiving — sessions, GRNs, blind receipt, and receiving behaviour as configuration |
| #120 | `p1-14.md` | P1-14 · Quality inspection as a header over lines, with the rollup stated to the value |
| #126 | `p1-15.md` | P1-15 · Putaway rules as data, with the override reason captured |
| #129 | `p1-16.md` | P1-16 · Receipt reversal as an action, not a data fix |
| #133 | `p1-17.md` | P1-17 · Transfer-order schema with the India and ownership hooks |
| #137 | `p1-18.md` | P1-18 · Warehouse-scoped user access in every management query's WHERE clause |
| #139 | `p1-19.md` | P1-19 · i18n en/fr/hi, SafeTranslation registration, and the status badge from a registry column |
| #145 | `p1-20.md` | P1-20 · App permissions, menus, grid configuration wave 1, and the shared-registry edits |
| #148 | `p1-21.md` | P1-21 · Master merge — two duplicate items, or two duplicate counterparties, reconciled by a movement rather than by an UPDATE |
| #163 | `p1-22.md` | P1-22 · Associations to the existing-page standard — row-action assignment modals, warehouse and owner company links, install-wide codes |
| #18 | `p2-01.md` | P2-01 · Adjustments with a value-based approval threshold, the insufficient-stock log and the blocked-move queue |
| #24 | `p2-02.md` | P2-02 · Transfers as three legs, through a per-transfer in-transit location |
| #29 | `p2-03.md` | P2-03 · Holds as records with a release audit, not a status column |
| #37 | `p2-04.md` | P2-04 · Counting — a document that proposes an adjustment and never writes on-hand |
| #42 | `p2-05.md` | P2-05 · Expiry is a state, not an alert — and the four shelf-life enforcement points named separately |
| #47 | `p2-06.md` | P2-06 · The reconciliation-exception grid — drift with an owner and an action, not a log line |
| #53 | `p2-07.md` | P2-07 · Allocation — soft and hard reservations, expiry as a job, strategy as a configured row |
| #59 | `p2-08.md` | P2-08 · One demand model for every demand type, with six independent quantity columns |
| #65 | `p2-09.md` | P2-09 · Discrete picking to a real staging location, and dispatch as the only inventory-relief event |
| #73 | `p2-10.md` | P2-10 · Shipments and the outbound object chain, with carrier masters and a nullable account owner |
| #79 | `p2-11.md` | P2-11 · Cartons, carton contents and pack evidence captured at pack time |
| #87 | `p2-12.md` | P2-12 · Returns v1 (A-1) — the return receipt is primary, the RMA is optional, and returns never land in AVAILABLE |
| #93 | `p2-13.md` | P2-13 · Supplier returns, quarantine disposition, and inbound reconciliation as a decision centre that never moves stock |
| #100 | `p2-14.md` | P2-14 · Printing (A-2) — net-new template and label rendering, with ZPL first |
| #106 | `p2-15.md` | P2-15 · Replenishment as a document, demand history maintained by posting, and lost sales captured |
| #115 | `p2-16.md` | P2-16 · The costing engine (D-6) — layers, consumption, weighted average and FIFO |
| #125 | `p2-17.md` | P2-17 · Landed cost with the apportionment basis on the receipt, and revaluation as a document |
| #128 | `p2-18.md` | P2-18 · The accounting handover — one valued envelope per event, and a rejected-handover queue with an owner |
| #132 | `p2-19.md` | P2-19 · Opening stock as a first-class feature, with a signed reconciliation certificate |
| #136 | `p2-20.md` | P2-20 · Report pack 1 — stock on hand, the movement register, the godown statement, valuation as-at and ageing |
| #141 | `p2-21.md` | P2-21 · Report pack 2 — the adjustment register, count variance, low stock, KPIs with frozen definitions, and traceability |
| #143 | `p2-22.md` | P2-22 · The interface error queue, with a reprocess action that is idempotent by construction |
| #146 | `p2-23.md` | P2-23 · Approval permissions distinct from execution permissions, and the approver may not be the actor |
| #149 | `p2-24.md` | P2-24 · Supersession stock and demand treatment, bidirectional interchange, and fitment in the dealer adapter |
| #150 | `p2-25.md` | P2-25 · warehouse-adapter-dealer — the first port proof, with a keyboard-first counter sale |
| #151 | `p2-26.md` | P2-26 · warehouse-adapter-services — the genericity proof, because one adapter proves nothing |
| #152 | `p2-27.md` | P2-27 · The D-9 coexistence reports — the category-ownership reconciliation, and the counted cost surfaced in the product |
| #153 | `p2-28.md` | P2-28 · Value-only movements, the value-conservation invariant, and daily storage snapshots |
| #154 | `p2-29.md` | P2-29 · Grid configuration wave 3 — export follows the visible columns, and filter-aware statistics carry no cache name |
| #130 | `p2in-01.md` | P2-IN-01 · The fifth module — `warehouse-india` scaffold, GSTIN profiles and compliance registrations |
| #135 | `p2in-02.md` | P2-IN-02 · The compliance-provider abstraction, transplanted rather than reinvented |
| #140 | `p2in-03.md` | P2-IN-03 · The delivery challan as a numbered document on its own per-branch series — and there is one challan table |
| #147 | `p2in-04.md` | P2-IN-04 · The e-way bill lifecycle implemented in v1, not just its number — and the gate pass conditional on it |
| #12 | `p3-01.md` | P3-01 · The RF screen family and its interaction contract — nine screens, one input, no mouse |
| #14 | `p3-02.md` | P3-02 · Task assignment pull and push from one table, the supervisor exception console, and SKIP LOCKED claiming |
| #19 | `p3-03.md` | P3-03 · The device registry — device-bound sessions, shared sign-in, shift handover and remote kill |
| #23 | `p3-04.md` | P3-04 · The offline queue, degraded-mode and catch-up entry, the mobile vocabulary sweep, and grid config wave 4 |
| #28 | `p3-05.md` | P3-05 · The ASN as a document, live dock appointments, and seals captured at load and at unload |
| #31 | `p3-06.md` | P3-06 · Waves as a real object, and batch picking as the one method v1.1 adds |
| #36 | `p3-07.md` | P3-07 · The pack session as an operator flow, and scan verification as configuration per task type |
| #41 | `p3-08.md` | P3-08 · The print server — printer registry, routing rules, direct-to-printer, and labels as stored artefacts with a void path |
| #46 | `p3-09.md` | P3-09 · Manifest, handover and pickup request as three objects, plus consignments |
| #50 | `p3-10.md` | P3-10 · Kits as a master, and virtual against physical kits as different objects with the same BOM |
| #57 | `p3-11.md` | P3-11 · Work orders as VAS and light manufacturing — assembly that balances by value, repack and break-case as two-sided events, packaging as stock |
| #61 | `p3-12.md` | P3-12 · Reorder policy at item × location, and pick-face replenishment tasks |
| #66 | `p3-13.md` | P3-13 · Order edit after release as a seeded rule matrix, and fulfilment policy per owner and channel |
| #69 | `p3-14.md` | P3-14 · Zero-stock / empty-bin verification on the last pick from a location |
| #74 | `p3-15.md` | P3-15 · LPN move as one movement with stored expanded lines, nested LPNs, and GS1 element-string parsing |
| #80 | `p3-16.md` | P3-16 · Alert rules, alert events, and the six per-install health signals |
| #85 | `p3-17.md` | P3-17 · KPI snapshots and the D-9 mitigations — consolidated valuation across both inventories, with the caveat on the report |
| #90 | `p3-18.md` | P3-18 · Migration mapping profiles, twelve months of demand history, and the OEM price file with a dry-run diff |
| #95 | `p3-19.md` | P3-19 · The OEM order interface — transmit, and consume the acknowledgement |
| #102 | `p3-20.md` | P3-20 · warehouse-adapter-field-service — the van as a mobile location owned by a technician |
| #108 | `p3-21.md` | P3-21 · warehouse-adapter-assets — spares issued against a complaint resolution, with the custody boundary stated |
| #111 | `p3-22.md` | P3-22 · The event stream as the adapters' subscription point — in-process and HTTP, registered by the consumer |
| #116 | `p3-23.md` | P3-23 · A sandbox practice warehouse with disposable data, and in-product help per screen |
| #121 | `p3-24.md` | P3-24 · GS1 identity — SSCC allocation, EPC on the serial and the LPN, Digital Link, and the authorised-source flag |
| #156 | `p3-25.md` | **closed — folded into #33 (`P1-03`)** · P3-25 · Simple ABC recompute — the class a v1 count programme reads, computed at v1.1 |
| #16 | `p4-01.md` | P4-01 · GST reference masters, the relational tax engine with its known defects fixed as blockers, and the e-invoicing adapter for the transfer IRN |
| #22 | `p4-02.md` | P4-02 · Job work and ITC-04 — the challan clock aged, and the return filed from warehouse data |
| #27 | `p4-03.md` | P4-03 · The Rule 56 statutory stock account — a shipped report in the mandated categories, not a movement grid |
| #32 | `p4-04.md` | P4-04 · ITC reversal reaching back to the receipt that brought the lot in, and scrap sale as a supply |
| #38 | `p4-05.md` | P4-05 · MRP as a balance dimension, stock by MRP, and MRP-inclusive back-calculation of the taxable value |
| #45 | `p4-06.md` | P4-06 · Goods sent on approval / sale or return — our asset at the customer, on a challan, with a deemed-supply clock |
| #51 | `p4-07.md` | P4-07 · Bonded and MOOWR warehousing — licences, bonds with a running utilisation balance, and ex-bond clearance consuming identified quantity |
| #55 | `p4-08.md` | P4-08 · Extended-producer-responsibility reporting for batteries, e-waste, tyres and plastic packaging |
| #64 | `p4-09.md` | P4-09 · Two retention clocks on the same rows, per-item shelf-life retention, and retention beats erasure |
| #68 | `p4-10.md` | P4-10 · Compliance tasks and bounded rules, and client GST registrations with the warehouse as an additional place of business |
| #75 | `p4-11.md` | P4-11 · A second, tax-basis inventory value carried alongside the book value |
| #82 | `p4-12.md` | P4-12 · E-way bill wave 2 — vehicle updates, cancellations, extensions, and consolidated bills |
| #88 | `p4-13.md` | P4-13 · The regulated-goods licence pack — one licence object, one expiry clock, one despatch guard, one register |
| #17 | `p5-01.md` | P5-01 · `warehouse-3pl` scaffold, the client as an object, and the build-time proof that it is a module |
| #21 | `p5-02.md` | P5-02 · Charge codes as a master, and rate cards versioned and effective-dated |
| #26 | `p5-03.md` | P5-03 · The billable-event meter — append-only and reversible, exactly like the stock ledger |
| #30 | `p5-04.md` | P5-04 · Storage billing in four methods, and the minimum monthly charge as a metered true-up |
| #35 | `p5-05.md` | P5-05 · The billing run with a frozen approved state, accessorials, disputes, and the AR handover |
| #39 | `p5-06.md` | P5-06 · Four freight-billing modes, and the client's own carrier account |
| #44 | `p5-07.md` | P5-07 · SLA definitions, measurements and breaches as objects, and the portal's performance tab |
| #48 | `p5-08.md` | P5-08 · The client portal as a permission surface, owner segregation with a negative test per endpoint, and the custody report |
| #52 | `p5-09.md` | P5-09 · Channel accounts, idempotent order import, publish rules as the oversell control, tracking links and cross-dock |
| #58 | `p5-10.md` | P5-10 · The three-way match on an allocation junction, and one working calendar used by two callers |
| #62 | `p5-11.md` | P5-11 · Carrier integration — tracking events normalised and raw, rate shopping that persists the quote, serviceability, and the AWB pool |
| #67 | `p5-12.md` | P5-12 · NDR as a workflow with a response clock, and COD remittance reconciliation where the AWB lives |
| #72 | `p5-13.md` | P5-13 · Grading at receipt, OEM obsolescence returns, and the marketplace return-claim window |
| #76 | `p5-14.md` | P5-14 · Recall — quarantine in place, list every consignee, release every reservation |
| #81 | `p5-15.md` | P5-15 · Cores are inventory, and warranty scrap-and-hold |
| #86 | `p5-16.md` | P5-16 · NRV write-down as a register with its reversal, and the COGS recognition point as a configured policy |
| #91 | `p5-17.md` | P5-17 · The weighing instrument as a legal instrument, and labour tasks timed |
| #96 | `p5-18.md` | P5-18 · Replenishment beyond the reorder point — the sister-branch transfer, and emergency, opportunistic and break-case replenishment |
| #101 | `p5-19.md` | P5-19 · Lot and serial genealogy surviving assembly, and VAS priced by the labour minute |
| #107 | `p5-20.md` | P5-20 · Ratio and assortment packs, and the style × variant matrix screens |
| #114 | `p5-21.md` | P5-21 · The four remaining owner- and transport-shaped v2 items — per-owner print templates, fitments and equipment, the gate, and returnable packaging |
| #119 | `p5-22.md` | P5-22 · The integration surface — named API clients, rotatable keys, rate limits, replay, and the lag-shaped signal the outbox does not have |
| #123 | `p5-23.md` | P5-23 · One supplier claim register — short shipment, damage, quality reject, obsolescence and price, with a status ladder, a settlement and an ageing report |
| #157 | `p5-24.md` | **closed — split across #54 (`P1-05`, owns `FR-468`), #43 (`P0-04`), #56 (`P0-06`), #89 (`P0-11`), #13 (`P1-01`), #20 (`P1-02`), #33 (`P1-03`), #120 (`P1-14`), #37 (`P2-04`), #114 (`P5-21`)** · P5-24 · The v2 association junctions — UoM defaults, site-scoped supplier sources, company and owner links, owner-set cages, tax-scheme codes and configuration scopes |
| #158 | `p5-25.md` | **closed — folded into #48 (`P5-08`)** · P5-25 · Trade-customer portal — the independent garage orders from the dealer on the portal surface |
| #159 | `p5-26.md` | **closed — folded into #133 (`P1-17`)** · P5-26 · Inter-company movement as a linked sale and purchase, created in one action |
| #160 | `p5-27.md` | **closed — folded into #146 (`P2-23`)** · P5-27 · Value-banded approval levels — ordered typed rows, not a workflow engine |
| #161 | `p5-28.md` | **closed — folded into #139 (`P1-19`)** · P5-28 · Registry row translations — install-created codes render in the reader's language |
| #94 | `p6-01.md` | P6-01 · Archiving as a transaction — an `OPENING_BALANCE` movement at the cut-off before a single row moves |
| #99 | `p6-02.md` | P6-02 · The best stocking level is computed, not typed |
| #103 | `p6-03.md` | P6-03 · Measured labour, not engineered standards — and the refusal is the requirement |
| #109 | `p6-04.md` | P6-04 · Automation, AS/RS and robotics through a published task-event contract and the movement port — an interface, never a control layer |
| #112 | `p6-05.md` | P6-05 · Receipt facts emitted as evidence — and the supplier scorecard is deliberately not built here |
| #118 | `p6-06.md` | P6-06 · The `party-base` extraction trigger is recorded, not acted on |
| #122 | `p6-07.md` | P6-07 · 3PL v3 — rate escalation as a new version, the SLA credit as a negative billable event, and client profitability |
| #131 | `p6-08.md` | P6-08 · The `logistics` module — trips, ePOD and freight settlement, posting through the port, with zero commits to `warehouse-base` |
| #134 | `p6-09.md` | P6-09 · The dealer vehicle-inventory test, stated rather than answered |
| #138 | `p6-10.md` | P6-10 · The real-time operations dashboard on the platform widget framework |
| #142 | `p6-11.md` | P6-11 · The accessories absorption path, stated in advance so it is a decision rather than a discovery |
| #144 | `p6-12.md` | P6-12 · Multi-level BOM with routings is not built — recorded so the refusal is a decision with a way back in |

## Warehouse-only readiness findings — 2026-10-01

Created at the user’s request as one `[Finding]` issue per audit entry. Existing related implementation issues remain linked, unchanged. [Batch index](FINDINGS-2026-10-01.md).

| Issue | Task file | Title |
|---|---|---|
| #195 | `finding-w01.md` | [Warehouse] [Finding] W01 · Historical stock report can omit older surviving stock |
| #196 | `finding-w02.md` | [Warehouse] [Finding] W02 · Zone-less putaway rules can throw during response mapping |
| #197 | `finding-w03.md` | [Warehouse] [Finding] W03 · Blank unit on imported/direct demand order is not defaulted |
| #198 | `finding-w04.md` | [Warehouse] [Finding] W04 · Style/variant matrix has no supported style-creation path found |
| #199 | `finding-w05.md` | [Warehouse] [Finding] W05 · Supplier preference by site remains unverified in implementation |
| #200 | `finding-w06.md` | [Warehouse] [Finding] W06 · Cost-layer and valuation-policy maintenance surfaces remain unbuilt/unproven |
| #201 | `finding-w07.md` | [Warehouse] [Finding] W07 · Approval cost and original-currency evidence require persistence reconciliation |
| #202 | `finding-w08.md` | [Warehouse] [Finding] W08 · Cost inputs from receipt/return/transfer producers need end-to-end proof |
| #203 | `finding-w09.md` | [Warehouse] [Finding] W09 · Costing contract documentation and runtime evidence need reconciliation |
| #204 | `finding-w10.md` | [Warehouse] [Finding] W10 · Accounting-integrated mode lacks an installed implementation |
| #205 | `finding-w11.md` | [Warehouse] [Finding] W11 · Versioned accounting-envelope extension |
| #206 | `finding-w12.md` | [Warehouse] [Finding] W12 · RMA expiry has no scheduled transition found |
| #207 | `finding-w13.md` | [Warehouse] [Finding] W13 · Sealed-carton/item attachments lack an owning-module delete guard |
| #208 | `finding-w14.md` | [Warehouse] [Finding] W14 · Generic bin movement ownership remains unresolved |
| #209 | `finding-w15.md` | [Warehouse] [Finding] W15 · Emergency replenishment issue is partly stale |
| #210 | `finding-w16.md` | [Warehouse] [Finding] W16 · Replenishment source is not reserved when task is raised |
| #211 | `finding-w17.md` | [Warehouse] [Finding] W17 · Partial pick-face replenishment is unsupported |
| #212 | `finding-w18.md` | [Warehouse] [Finding] W18 · Replenishment priority is not recalculated at claim time |
| #213 | `finding-w19.md` | [Warehouse] [Finding] W19 · Generic task completion/cancellation signaling is inconsistent or unproven |
| #214 | `finding-w20.md` | [Warehouse] [Finding] W20 · Blocked-task alert setting has no consumer found |
| #215 | `finding-w21.md` | [Warehouse] [Finding] W21 · Snapshot schedule outage and missing-day recovery need proof |
| #216 | `finding-w22.md` | [Warehouse] [Finding] W22 · Full-history ageing performance remains unmeasured |
| #217 | `finding-w23.md` | [Warehouse] [Finding] W23 · Archiving and hot-ledger reconstruction are deferred |
| #218 | `finding-w24.md` | [Warehouse] [Finding] W24 · Scheduled reports cannot yet guarantee recipient-specific scope |
| #219 | `finding-w25.md` | [Warehouse] [Finding] W25 · Stock-to-GL search treats literal wildcards as patterns |
| #220 | `finding-w26.md` | [Warehouse] [Finding] W26 · Stock-period Site sort is advertised but unsupported |
| #221 | `finding-w27.md` | [Warehouse] [Finding] W27 · Opening-stock row validation filter has no operator surface |
| #222 | `finding-w28.md` | [Warehouse] [Finding] W28 · Receiving-session export label differs from grid |
| #223 | `finding-w29.md` | [Warehouse] [Finding] W29 · Handover shipment picker renders a null name |
| #224 | `finding-w30.md` | [Warehouse] [Finding] W30 · Site-access denial reports misleading permission |
| #225 | `finding-w31.md` | [Warehouse] [Finding] W31 · Date/filter/export consistency still needs broad UI verification |
| #226 | `finding-w32.md` | [Warehouse] [Finding] W32 · Install and contract documents contain contradictory current-state claims |
| #227 | `finding-w33.md` | [Warehouse] [Finding] W33 · Warehouse-only disaster recovery is not demonstrated |
| #228 | `finding-w34.md` | [Warehouse] [Finding] W34 · Database integration tests are outside the passing default gate |
| #229 | `finding-w35.md` | [Warehouse] [Finding] W35 · The standalone acceptance sequence remains incompletely demonstrated |
| #230 | `finding-w36.md` | [Warehouse] [Finding] W36 · Frontend test breadth does not establish operator-flow readiness |
| #231 | `finding-w37.md` | [Warehouse] [Finding] W37 · Warehouse is deliberately web-only and online-only |
| #232 | `finding-w38.md` | [Warehouse] [Finding] W38 · Physical scanner, printer and device operation is not field-proven |
| #233 | `finding-w39.md` | [Warehouse] [Finding] W39 · Frontend health endpoint fails, with an additional localhost binding mismatch |
| #234 | `finding-w40.md` | [Warehouse] [Finding] W40 · Fresh install / upgrade / module combinations need runtime proof |
| #235 | `finding-w41.md` | [Warehouse] [Finding] W41 · Import validation cache assumes one backend instance |
| #236 | `finding-w42.md` | [Warehouse] [Finding] W42 · Import update cannot clear optional values |
| #237 | `finding-w43.md` | [Warehouse] [Finding] W43 · Large generated import reverse still needs execution-budget decision |
| #238 | `finding-w44.md` | [Warehouse] [Finding] W44 · Dock data and picker can admit confusing legacy combinations |
| #239 | `finding-w45.md` | [Warehouse] [Finding] W45 · Regulated-item setup refuses contradictions too late |
| #240 | `finding-w46.md` | [Warehouse] [Finding] W46 · Optional tax-basis valuation remains deferred |
| #241 | `finding-w47.md` | [Warehouse] [Finding] W47 · Provider-backed operational features require actual connector evidence |
| #242 | `finding-w48.md` | [Warehouse] [Finding] W48 · 3PL billing needs an independent cycle-level reconciliation |
| #243 | `finding-w49.md` | [Warehouse] [Finding] W49 · Permissions need adversarial workflow tests, not only annotations |
| #244 | `finding-w50.md` | [Warehouse] [Finding] W50 · Idempotency/concurrency across the complete order flow needs proof |
| #245 | `finding-w51.md` | [Warehouse] [Finding] W51 · Cut-over performance and opening-stock reversal need measured evidence |
| #246 | `finding-w52.md` | [Warehouse] [Finding] W52 · Alert and background-job recovery need an operational drill |
| #247 | `finding-w53.md` | [Warehouse] [Finding] W53 · Production performance and resource limits lack a current benchmark |
| #248 | `finding-w54.md` | [Warehouse] [Finding] W54 · Backup retention, attachments and external acknowledgments need one recovery policy |
| #249 | `finding-w55.md` | [Warehouse] [Finding] W55 · Data import handoff and document permissions complicate onboarding |
| #250 | `finding-w56.md` | [Warehouse] [Finding] W56 · Product promises exceed the evidence in some help text |
| #251 | `finding-w57.md` | [Warehouse] [Finding] W57 · Operational KPI semantics and coexistence defaults require sign-off |
| #252 | `finding-w58.md` | [Warehouse] [Finding] W58 · Existing demand-merge option has no calculation consumer found |
| #253 | `finding-w59.md` | [Warehouse] [Finding] W59 · Advanced operational features must remain explicitly outside the basic offer |
| #254 | `finding-w60.md` | [Warehouse] [Finding] W60 · Filter parity gate cannot reliably parse current filter declarations/helpers |
| #255 | `finding-w61.md` | [Warehouse] [Finding] W61 · Registry-label gate has parser/mapping failures and unresolved label checks |
| #256 | `finding-w62.md` | [Warehouse] [Finding] W62 · Registry and mobile gates conflate equal strings from different domains |
| #257 | `finding-w63.md` | [Warehouse] [Finding] W63 · Carrier and shipment lifecycle has recorded unowned transitions |
| #258 | `finding-w64.md` | [Warehouse] [Finding] W64 · Client offboarding and accounting-related operational follow-ups remain recorded |
| #259 | `finding-w65.md` | [Warehouse] [Finding] W65 · Task assignment may accept an inactive or out-of-site operator |
| #260 | `finding-w66.md` | [Warehouse] [Finding] W66 · Paper catch-up and device session edge cases need acceptance |
| #261 | `finding-w67.md` | [Warehouse] [Finding] W67 · GS1 pallet identity remains intentionally deferred |
| #262 | `finding-w68.md` | [Warehouse] [Finding] W68 · Weighing and labour capture have recorded interface limits |
| #263 | `finding-w69.md` | [Warehouse] [Finding] W69 · India e-way lifecycle has recorded state and race gaps |
| #264 | `finding-w70.md` | [Warehouse] [Finding] W70 · India challan evidence and setup need further closure |
| #265 | `finding-w71.md` | [Warehouse] [Finding] W71 · Closed receiving and access work contains unresolved smaller obligations |

### Earlier reported issues referenced by this batch

These existing GitHub reports have no source task file in this batch; listed for reference resolution only. Their bodies and states were not modified.

| Issue | Task file | Title |
|---|---|---|
| #165 | `—` (existing report; no source file) | [Warehouse] P2-12 follow-up · RMA expiry job (RJ-012) — open RMAs expire on the site's date |
| #166 | `—` (existing report; no source file) | [Warehouse] P2-11 follow-up · Pack evidence and item documents cannot be deleted out from under a sealed carton |
| #168 | `—` (existing report; no source file) | [Warehouse] P2-24 follow-up · MERGE_DEMAND is read by the demand calculation |
| #169 | `—` (existing report; no source file) | [Warehouse] P2-16 follow-up · Cost Layers and Valuation Policies screens |
| #170 | `—` (existing report; no source file) | [Warehouse] P2-16 follow-up · Movement lines keep the approved cost, the source-currency amount and the cost source line |
| #171 | `—` (existing report; no source file) | [Warehouse] P2-16 follow-up · Receipts, supplier returns, transfers and workshop returns give the costing engine what it needs |
| #172 | `—` (existing report; no source file) | [Warehouse] P2-16 follow-up · Ratify costing defaults, contract codes and run the integration tests in the gate |
| #173 | `—` (existing report; no source file) | [Warehouse] Follow-up · Accounting envelope v2 — duty status, lot, serial and exchange rate per line |
| #174 | `—` (existing report; no source file) | [Warehouse] Follow-up · The accounting-facing adapter has no home — no module owns WhbAccountingHandoverSink or WhbGlBalanceProvider |
| #175 | `—` (existing report; no source file) | [Warehouse] Follow-up · Prove INTEGRATED mode end to end — WH-SC-156, WH-SC-157, CONFIG-CASE-07/10 |
| #176 | `—` (existing report; no source file) | [Warehouse] P2-02 follow-up · FR-150 / WH-SC-285 bin-to-bin movement has no owning task — the deferral, not a closure |
| #177 | `—` (existing report; no source file) | [Warehouse] P2-02 follow-up · RA-006 — P2-09's emergency replenish is specified as a BIN_TO_BIN transfer, which V511246 makes unbuildable |
| #178 | `—` (existing report; no source file) | [Warehouse] OD-20 · Does v1 ship a union valuation report across the two ownership domains? (gates P2-20, P2-27) |
| #179 | `—` (existing report; no source file) | [Warehouse] P2-20 · WS-224's 365-day lower bound makes the as-at quantity a windowed net, not an all-time balance |
| #180 | `—` (existing report; no source file) | WhStockToGl search: an unescaped LIKE makes '_' and '%' live wildcards |
| #181 | `—` (existing report; no source file) | wh_opening_stock_lines.validationStatus: a seeded filter row nothing can consume |
| #182 | `—` (existing report; no source file) | WS-212 Ageing now scans the whole ledger: PP-7's bound was removed on purpose, and the cost is unmeasured |
| #183 | `—` (existing report; no source file) | V511248's header loses its § characters, so MigrationHeaderRule fails and blocks every warehouse ci-gate run |
| #184 | `—` (existing report; no source file) | P2-21: four product calls taken by default in report pack 2 |
| #185 | `—` (existing report; no source file) | RH-010 unmet: WS-215 cannot be scheduled without a platform commit |
| #186 | `—` (existing report; no source file) | [Warehouse] W13-1 carry: WH-SC-044…WH-SC-059 not demonstrated (SCENARIO-CATALOGUE.md not available locally) |
| #187 | `—` (existing report; no source file) | [Warehouse] Site-access 403s name the wrong permission (shared requirePermitted) |
| #188 | `—` (existing report; no source file) | [Warehouse] P4-13 follow-up · Refuse an unlotted regulated item at the item screen; Schedule H1 prescriber/patient fields (adviser-gated) |
| #189 | `—` (existing report; no source file) | [Warehouse] Putaway Rules: creating/editing a zone-less rule (FIXED_LOCATION or CONSOLIDATE_SAME_LOT) always 500s |
| #190 | `—` (existing report; no source file) | [Warehouse] Receiving Sessions export labels the Site column "Warehouse" |
| #191 | `—` (existing report; no source file) | [Warehouse Base] Style x Variant Matrix: no code path ever creates a "style" — page is permanently empty |
| #192 | `—` (existing report; no source file) | [Warehouse Base] Stock Periods: "Site" column marked sortable but sort is silently ignored |
| #193 | `—` (existing report; no source file) | [Warehouse] Channel order import rejects lines with no uomCode instead of defaulting to the item's base unit |
| #194 | `—` (existing report; no source file) | [Warehouse] Handovers: shipment picker shows literal "TRACKING - null" when ship-to name is blank |
