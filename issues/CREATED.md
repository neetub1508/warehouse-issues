# Created issues

Filed in `neetub1508/warehouse-issues`. **1 master epic + 8 phase epics + 143 tasks = 152.**

> Verified against the file glob, which is the authority:
> `ls issues/p*.md | wc -l` → **143**; per phase
> `for p in p0 p1 p2 p2in p3 p4 p5 p6; do ls issues/$p-[0-9][0-9].md | wc -l; done`
> → **17 · 21 · 29 · 4 · 24 · 13 · 23 · 12**. `ls issues/*EPIC*.md | wc -l` → **9**
> (1 master + 8 phase). The headline is correct.

> **`#2` and `#9` are pull requests, not issues.** GitHub draws issue and pull-request
> numbers from one sequence per repository, and two PRs were opened while the backlog was
> being filed. That is why the master epic is `#1`, the phase epics are
> `#3 #4 #5 #6 #7 #8 #10 #11` — **not** `#2`–`#9` — and the 143 tasks run **#12–#154**
> rather than #10–#152. There is no gap in the backlog; the two missing numbers are the PRs.

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
