# Created issues

Filed in `neetub1508/warehouse-issues`, **regenerated from GitHub on 2026-10-24 (P7-12 `#560`, R30 `CP-GA-002`):**
issue numbers **1–609** hold **604 issues and 5 pull requests** (`#2`, `#9`, `#155`, `#162`, `#164`). **Open: 120** = 7 epics +
107 tasks + 6 other (`#185`, `#323`, `#324`, `#386`, `#519`, `#520`). **Closed: 484** = 451 completed + 25 not planned
(`#142` and `#144` among them) + 8 duplicates. The rounds below explain how the numbers were filed.

> Verified against the file glob, which is the authority:
> `ls issues/p*.md | wc -l` → **201**; per phase
> `for p in p0 p1 p2 p2in p3 p4 p5 p6 p7 p8 p9 p10; do ls issues/$p-[0-9][0-9].md | wc -l; done`
> → **17 · 22 · 29 · 4 · 24 · 13 · 23 · 12 · 13 · 16 · 14 · 14**. `ls issues/*EPIC*.md | wc -l` → **13**
> (1 master + 12 phase). Commands: `gh issue list --state all --limit 1000 --json number,state,stateReason,labels`,
> `gh pr list --state all`. That the `--sync` ran **before** P7 started cannot be proved after the fact and is not claimed.

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

> **D-16 re-target (2026-10-22) filed 60 issues with `create-issues.sh --file-tbd`:** the phase epics
> `P7` #545 · `P8` #546 · `P9` #547 · `P10` #548, then the 56 tasks **#549–#604** (P7 #549–#561,
> P8 #562–#577, P9 #578–#591, P10 #592–#604). Each task carries one comment listing its R29 findings.
> The VOID tasks `P2-24` #149, `P2-25` #150, `P2-26` #151, `P3-19` #95, `P5-12` #67, `P5-15` #81 and
> `P6-09` #134 are closed as not planned.

> **Tracking fix (2026-10-23) filed two findings and reopened 41 tasks.** `W72` #606 and `W73` #607
> (`FINDINGS-2026-10-23.md`) are the contract divergences with no owning task. 41 closed tasks carry a
> *Reopened scope — R30/R31 (2026-10-23)* section and the `reopened-r31` label; their rows below are
> unchanged. The full list and the divergence triage are in `docs/reviews/OPEN-WORK-INDEX.md`.

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

These existing GitHub reports have no source task file in this batch; listed for reference resolution only. Their bodies and states were not modified. `#167`, `#285`, `#329`, `#389`, `#474` and `#487` were added 2026-10-22 because the design docs cite them (all closed).

| Issue | Task file | Title |
|---|---|---|
| #165 | `—` (existing report; no source file) | [Warehouse] P2-12 follow-up · RMA expiry job (RJ-012) — open RMAs expire on the site's date |
| #166 | `—` (existing report; no source file) | [Warehouse] P2-11 follow-up · Pack evidence and item documents cannot be deleted out from under a sealed carton |
| #167 | `—` (existing report; no source file) | [Warehouse] P2-24 follow-up · A reservation remembers the part the customer asked for when a substitute is held |
| #168 | `—` (existing report; no source file) | [Warehouse] P2-24 follow-up · MERGE_DEMAND is read by the demand calculation |
| #169 | `—` (existing report; no source file) | [Warehouse] P2-16 follow-up · Cost Layers and Valuation Policies screens |
| #170 | `—` (existing report; no source file) | [Warehouse] P2-16 follow-up · Movement lines keep the approved cost, the source-currency amount and the cost source line |
| #171 | `—` (existing report; no source file) | [Warehouse] P2-16 follow-up · Receipts, supplier returns, transfers and workshop returns give the costing engine what it needs |
| #172 | `—` (existing report; no source file) | [Warehouse] P2-16 follow-up · Ratify costing defaults, contract codes and run the integration tests in the gate |
| #173 | `p8-25.md` (R32 2026-10-25: task file written for the existing issue; body to be synced) | [Warehouse] Follow-up · Accounting envelope v2 — duty status, lot, serial and exchange rate per line |
| #174 | `p8-23.md` (R32 2026-10-25: task file written for the existing issue; body to be synced) | [Warehouse] Follow-up · The accounting-facing adapter has no home — no module owns WhbAccountingHandoverSink or WhbGlBalanceProvider |
| #175 | `p8-24.md` (R32 2026-10-25: task file written for the existing issue; body to be synced) | [Warehouse] Follow-up · Prove INTEGRATED mode end to end — WH-SC-156, WH-SC-157, CONFIG-CASE-07/10 |
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
| #285 | `—` (existing report; no source file) | W14 follow-up: movement port accepts any registered type from human roles (bypasses task/document guards) |
| #329 | `—` (existing report; no source file) | [Follow-up W08] Native receipt exchange rate on the GRN (OD-16 SOURCE_RATE) - product-owner decision first |
| #389 | `—` (existing report; no source file) | [Warehouse] W35-D3 · Receipt status default chain missing: no RECEIPT movement-type default, no supplier level, no AVAILABLE fallback -> 422 RECEIVED_STATUS_UNRESOLVED |
| #474 | `—` (existing report; no source file) | [Follow-up W64] X-068: re-key carrier references on wh_shipment_tracking_events and wh_rate_quotes to stable codes (IRR-26) |
| #487 | `—` (existing report; no source file) | [Follow-up #474] X-068: wh_shipping_labels / wh_pickup_requests / wh_manifests / wh_handovers still hold carrier_id FKs |
| #545 | `issues/09-EPIC-p7.md` | EPIC: P7 — Remove dealer and retail code, rename the dual-use items, rebuild on a clean migration set |
| #546 | `issues/10-EPIC-p8.md` | EPIC: P8 — Manufacturing stores in core (gate, bill-matched GRN, sampling QC, MRN, requisition, issue, return, order ports) |
| #547 | `issues/11-EPIC-p9.md` | EPIC: P9 — `warehouse-trade`: manufacturing purchase and sales, mirrored |
| #548 | `issues/12-EPIC-p10.md` | EPIC: P10 — Manufacturing (warehouse-manufacturing) |
| #549 | `issues/p7-01.md` | P7-01 · Relocate the four generic helpers that kept code reaches through removed classes — the stocking-category picker, the claim-transition type, the claim line-value helper and the order fingerprint hash |
| #550 | `issues/p7-02.md` | P7-02 · Remove AWB pools, courier serviceability and rate quotes; keep carrier account scopes; cut the carrier delete-guard SQL and trim the carrier connector |
| #551 | `issues/p7-03.md` | P7-03 · Remove the NDR workflow, COD remittances, customer tracking links and the public tracking page; drop the NDR/RTO carrier statuses and the carrier NDR/COD clocks |
| #552 | `issues/p7-04.md` | P7-04 · Remove channel accounts, channel order imports and channel publish rules; drop the demand-order payment mode, COD amount and channel account; keep whb_channels and channel_id |
| #553 | `issues/p7-05.md` | P7-05 · Remove RTO consignments and marketplace claims; return receipts post and reverse with the same stock movements; drop the RTO and MARKETPLACE return types |
| #554 | `issues/p7-06.md` | P7-06 · Replace the Channels L1 menu with Shipping → Carrier Tracking & Planning and re-home its four generic leaves |
| #555 | `issues/p7-07.md` | P7-07 · Remove OEM obsolescence returns and the OBSOLESCENCE claim type; supplier claims keep four types |
| #556 | `issues/p7-08.md` | P7-08 · Remove the trade portal, the Warehouse Trade Customer role and the customer persona in the owner-scope resolver |
| #557 | `issues/p7-09.md` | P7-09 · Remove accessories coexistence — category stocking ownership, external stock snapshots, the coexistence report, consolidated valuation and is_dual_eligible |
| #558 | `issues/p7-10.md` | P7-10 · Remove the dealer and retail seeded vocabulary and the dead adapter switches; whb_channels keeps only the B2B kind |
| #559 | `issues/p7-11.md` | P7-11 · Rename the dual-use codes in storage — LINE_STOP, PRODUCTION_STORE, MANUFACTURER_PART_NUMBER — and Parts KPIs to Stock KPIs on every surface |
| #560 | `issues/p7-12.md` | P7-12 · Bring classic's docs, QA notes, contracts and the ci-gate ledger in line with the removal |
| #561 | `issues/p7-13.md` | P7-13 · Rebuild the dev database once on the clean migration set, prove Flyway history and every grep gate, and turn ci-gate green |
| #562 | `issues/p8-01.md` | P8-01 · PO type (FIXED / OPEN / BLANKET_RELEASE), schedule lines with open quantity, receipt allocation, and the purchase-order port |
| #563 | `issues/p8-02.md` | P8-02 · The demand-order port for sales orders — SO and customer-PO references, a customer delivery schedule, firm-within-horizon allocation |
| #564 | `issues/p8-03.md` | P8-03 · Gate entry register (inward / outward) with PO, bill and weighment on arrival, and returnable / non-returnable gate passes with return tracking and overdue |
| #565 | `issues/p8-04.md` | P8-04 · GRN bill number / date / billed quantity, the duplicate-bill guard, short receipt opening a supplier claim, and excess accepted within an approved excess or refused |
| #566 | `issues/p8-05.md` | P8-05 · Configurable sampling — band tables per item / category / supplier, FIXED_QUANTITY and PERCENTAGE fixed, the Z1.4 table kept as one option, lot verdict from Ac/Re, destructive test quantity |
| #567 | `issues/p8-06.md` | P8-06 · QC with a polymorphic source — goods receipt, store return, production receipt, in-process, stock — through resolver beans, so manufacturing can inspect without a GRN |
| #568 | `issues/p8-07.md` | P8-07 · QC reject → an explicit, manual "Raise supplier return" action (FR-139 amended — never automatic) |
| #569 | `issues/p8-08.md` | P8-08 · MRN — material receipt note authorised by a second person, MRN_PENDING as the stock-availability rule, putaway on authorisation, MRN and GRN print |
| #570 | `issues/p8-09.md` | P8-09 · Material requisition (indent) for a department, cost centre or production order — per-line approval, reservation, partial issue, closure — the cost-object seam, cost centres, and the back-to-back purchase-requisition hand-off |
| #571 | `issues/p8-10.md` | P8-10 · Store issue to VIRT-CONSUMED with a cost object (department / cost centre / production order) on every issue line — S-052 resolved per RN-034 |
| #572 | `issues/p8-11.md` | P8-11 · Store return — linked to the issue line, partial, valued at the issue cost, condition decides status and QC, through a new ISSUE_RETURN movement type |
| #573 | `issues/p8-12.md` | P8-12 · Stores print documents — gate entry slip, RGP/NRGP gate pass, GRN with the bill block, MRN, material requisition, store issue slip, store return note |
| #574 | `issues/p8-13.md` | P8-13 · Stores registers and performance — RGP pending / overdue, requisitions pending issue, issue register by cost object, consumption by department, stores performance benchmarks |
| #575 | `issues/p8-14.md` | P8-14 · Stores menus, settings registry, i18n and filter-scope wave for P8 — within the 8-leaf / 10-section caps |
| #576 | `issues/p8-15.md` | P8-15 · The RMA-creation port for sales-return authorisation, and the supplier-return intent (REPLACE / CREDIT / NO_ACTION) with a dispatched event |
| #577 | `issues/p8-16.md` | P8-16 · External replenishment suggestions — the MRP supply seam (origin MRP), converted once: to a draft core PO with trade off, to a PR by trade with trade on |
| #578 | `issues/p9-01.md` | P9-01 · The trade module — `warehouse-trade` scaffold, enable flag, menu tree and the platform touchpoints |
| #579 | `issues/p9-02.md` | P9-02 · Trade masters — supplier and customer trade profiles, approved vendor list, customer item references, T&C templates and the trade vocabularies |
| #580 | `issues/p9-03.md` | P9-03 · The trade approval matrix — rules, levels, maker ≠ checker, delegation, escalation and My Approvals |
| #581 | `issues/p9-04.md` | P9-04 · Purchase requisition — manual, from stores shortage, from replenishment / MRP; approval, consolidation and partial conversion |
| #582 | `issues/p9-05.md` | P9-05 · Sourcing — RFQ to many suppliers, vendor quotations with versions, comparative statement with L1 and the approved award |
| #583 | `issues/p9-06.md` | P9-06 · Agreed prices, both sides — purchase rate contracts, sales rate contracts, price lists, dated revisions, slabs, ceilings and the two price-resolution services |
| #584 | `issues/p9-07.md` | P9-07 · Purchase orders — FIXED, OPEN and BLANKET with delivery schedules, releases, and the hand-off to core through the PO port |
| #585 | `issues/p9-08.md` | P9-08 · Pre-sales — sales enquiry, customer quotation with versions, regret, won / lost and the win/loss analysis |
| #586 | `issues/p9-09.md` | P9-09 · Sales orders — FIXED, OPEN and BLANKET with the customer delivery schedule, dispatch planning from the FG store, and the hand-off to core through the demand-order port |
| #587 | `issues/p9-10.md` | P9-10 · Acknowledgement, expediting / commitment tracking, short-close and auto-close — both sides |
| #588 | `issues/p9-11.md` | P9-11 · Order amendments and versions — one engine, PO and SO, with snapshots, port push, amendment prints and version compare |
| #589 | `issues/p9-12.md` | P9-12 · Counterparty evaluation — vendor rating and customer rating / OTIF on one weighted engine, with grade-driven review tasks |
| #590 | `issues/p9-13.md` | P9-13 · Sales return authorisation → core RMA, and the purchase-side replacement reinstatement |
| #591 | `issues/p9-14.md` | P9-14 · Trade print documents and the trade reports pack |
| #592 | `issues/p10-01.md` | P10-01 · The manufacturing module — `warehouse-manufacturing` scaffold, enable flag, menu tree, settings registry and the platform touchpoints |
| #593 | `issues/p10-02.md` | P10-02 · Manufacturing registries — movement, document and location types, code lists, reason contexts, the REWORK disposition, print kinds and number series, under the RL-003 owning-module guard |
| #594 | `issues/p10-03.md` | P10-03 · Bill of materials — multi-level, versioned, maker–checker BOMs with alternates, scrap, phantoms, co-/by-products; explosion, where-used and cost roll-up |
| #595 | `issues/p10-04.md` | P10-04 · Work centres and the optional BOM operation list — a lightweight routing that is never mandatory |
| #596 | `issues/p10-05.md` | P10-05 · Production orders — BOM snapshot, release with availability check and component reservations, hold, complete, reopen, MTO link, the PRODUCTION_ORDER cost-object resolver and the traveller |
| #597 | `issues/p10-06.md` | P10-06 · Material to the order — staging to line-side, manual issue and return through core store documents, component substitution and the consumption policy |
| #598 | `issues/p10-07.md` | P10-07 · Production receipt — FG, co- and by-products in one movement with backflush and scrap, tolerances and completion, lot genealogy, maker–checker reversal and the FG receipt note |
| #599 | `issues/p10-08.md` | P10-08 · Operation confirmations, in-process and final QC through the core polymorphic source, and the REWORK disposition that creates a rework order |
| #600 | `issues/p10-09.md` | P10-09 · Actual costing of output, exact co-product split, close by settlement, and the cost sheet — accounting as handover only |
| #601 | `issues/p10-10.md` | P10-10 · Subcontracting and job work — subcontract orders, dispatch to the job worker, processed-item receipt, reconciliation, and the India challan / ITC-04 path through a core port |
| #602 | `issues/p10-11.md` | P10-11 · Planning masters — item planning parameters per item × site and demand plans (forecast / MPS-lite) with consumption modes |
| #603 | `issues/p10-12.md` | P10-12 · MRP — regenerative per-site run, netting with low-level codes, lot sizing and fences, pegged proposals, firm / convert / dismiss, BUY to core replenishment suggestions, exception messages |
| #604 | `issues/p10-13.md` | P10-13 · Capacity load (infinite, visible) and the manufacturing registers — production, WIP by order, scrap, yield, consumption variance |
| #605 | `issues/p10-14.md` | P10-14 · Bonded / MOOWR stock to production and to a job worker — bond rules read by the exit guard, the bond register, output in bond, bonded loss, job work under permission, the MOOWR return and SEZ movement lines |
| #606 | `finding-w72.md` | [Warehouse] [Finding] W72 · Counterfeit control has no open owner after P3-24 was closed not planned |
| #607 | `finding-w73.md` | [Warehouse] [Finding] W73 · Nine non-functional rules are verified only by the reviewer gate |
| #636 | `issues/p8-17.md` | P8-17 · Non-conformance report (NCR) for every reject, with containment, root cause, CAPA actions, closure approval, and the defect-code master |
| #637 | `issues/p8-18.md` | P8-18 · Quality deviation (concession) — bound by quantity and / or time, expiring, approved in levels (QC Manager, then Plant Head), consumed by IQC "accept under deviation" and by manufacturing through a port |
| #638 | `issues/p8-19.md` | P8-19 · Inspector authorisation by site × stage × item category, segregation of duties (inspector ≠ receiver, ≠ producer), and QC Manager approval of inspection results |
| #639 | `issues/p8-20.md` | P8-20 · QC measuring-instrument master and calibration register — due dates, certificates, a reading against an out-of-calibration instrument refused, and the impact list of a failed calibration |
| #640 | `issues/p8-21.md` | P8-21 · Quality registers — vendor-wise rejection % and line-rejection ppm, defect Pareto, open NCR / CAPA ageing, deviations, and pass rate by inspection stage |
| #641 | `issues/p8-22.md` | P8-22 · Status stores — quarantine, rejected, scrap and sample stay stock statuses (D-20 #16), with an optional dedicated location per status per site that every status change moves into and that reports show as a store |
| #642 | `issues/p8-26.md` | P8-26 · Core SPIs and port changes owed to trade and manufacturing — import receipt valuation and receipt landed cost (CN-15), tax preview (CN-16), customer credit check (CN-17), accounting envelope enricher (CN-18), production progress and MFG ports (CN-19), immediate allocation and transport on every release (CN-20), gate-out guard (CN-21), pre-ship guard (CN-22) |
| #643 | `issues/p8-30.md` | P8-30 · One document-approval engine for every document type — rules by document type × site × department × item category × value / quantity band, multi-level, maker ≠ checker in the service, append-only decisions with the band used, upward escalation, in-app / e-mail / WhatsApp, delegation, My Approvals and the approval register |
| #644 | `issues/p9-15.md` | P9-15 · GST on purchase and sales documents — CGST / SGST / UTGST / IGST previewed by accounting's tax determination through the core tax-preview SPI, on PO, vendor quotation, comparative statement, customer quotation and SO |
| #645 | `issues/p9-16.md` | P9-16 · Send trade documents to the counterparty by e-mail and WhatsApp — PO, schedule release, RFQ, quotation, regret letter, SO acknowledgement — with a delivery log and supplier follow-up reminders |
| #646 | `issues/p9-17.md` | P9-17 · Credit, overdue and advance checks at SO approval and dispatch through the accounting credit service, with a reasoned override approval |
| #647 | `issues/p9-18.md` | P9-18 · Import purchase — import PO, bill of entry with customs duties, and BoE landed cost onto the receipt through a core port |
| #648 | `issues/p9-19.md` | P9-19 · Enquiry feasibility review and queue, pre-sale costing from manufacturing with a margin check, and the sample-request hook |
| #649 | `issues/p9-20.md` | P9-20 · Hand-off to accounting — trade enrichment of core's shipment invoice request and return credit-note proposal, billing status per SO line from the invoice acknowledgement, SO closure when shipped and invoiced, gate-out on invoice |
| #650 | `issues/p9-21.md` | P9-21 · Order book with produced vs dispatched vs invoiced, SO progress status, SO pending to produce, and the trade Customer 360 |
| #651 | `issues/p10-15.md` | P10-15 · Operators, skills and shifts — shift master per site, operator master over platform users, dated skill / operation authorisations checked at every job-card booking |
| #652 | `issues/p10-16.md` | P10-16 · Operation master and the routing master — a separate, versioned, released routing with its own revision, mandatory for make items run on job cards |
| #653 | `issues/p10-17.md` | P10-17 · Engineering change notice — ECN with impact analysis on open orders, purchase demand and old-part stock, Design Head + Plant Head approval, and implement that releases the new versions |
| #654 | `issues/p10-18.md` | P10-18 · Drawings — drawing master with controlled revisions and files, maker–checker release for sample and for production, current-revision display, UNCONTROLLED COPY watermark, copy-issue log and the core DrawingRevisionPort |
| #655 | `issues/p10-19.md` | P10-19 · Samples — sample request from enquiry / SO, SAMPLE production order on a trial BOM, internal check, approved dispatch, customer feedback iterations, golden sample, and the "sample approval required" gate on production (not on the SO line) |
| #656 | `issues/p10-20.md` | P10-20 · Production batches and job cards per batch per stage — sequencing and transfer, start / pause / complete, crew + machine + shift booking with good / rework / rejected / scrap, stage consumption, and the job-work stage |
| #657 | `issues/p10-21.md` | P10-21 · Unit serials and as-built binding — chassis / VIN series with check digit and pre-printed ranges, assignment at the first stage, void register, and part-serial ↔ chassis binding at the consuming stage |
| #658 | `issues/p10-22.md` | P10-22 · PDI gate per vehicle — per-model checklist plus SO-specific points, 100 % with serials-match, PASS / REWORK / HOLD, QC-Manager-signed PDI certificate PDF, FG receipt only after PDI, and PDI before dispatch from stock |
| #659 | `issues/p10-23.md` | P10-23 · Manufacturer unit registry for warranty — unit lifecycle from build to sale with bound part serials, sale date and invoice ref, the UnitRegistryPort, chassis traceability both ways, and homologation / Form 22 / VAHAN data per unit |
| #660 | `issues/p10-24.md` | P10-24 · Production board and daily plans — orders by status, batch Kanban across stages, WIP by stage, delayed orders, and today's plan vs actual |
| #661 | `issues/p10-25.md` | P10-25 · Pre-sale cost estimate service — CostEstimatePort for warehouse-trade quotations: BOM roll-up + routing conversion + overhead per unit, domestic value addition %, and a frozen estimate record |
| #662 | `issues/p10-26.md` | P10-26 · Tooling / die master and preventive maintenance — tool life by shots / units / hours consumed at booking, tools per routing operation, PM plans and maintenance orders for machines and tools, breakdown and downtime capture |
