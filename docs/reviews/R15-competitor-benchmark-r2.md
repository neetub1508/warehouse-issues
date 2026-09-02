# R15 — Competitor benchmark, round 2: what the market ships in 2026 that we do not

**Date:** 2026-09-02 · **Finding prefix:** `J-` (unallocated before this file — `grep -rohE "\bJ-[0-9]{1,3}\b" docs/*.md issues/*.md | wc -l` → `0`)

**File set actually read.** The design set proper — the 16 `docs/*.md` documents and the 148 task
files — **164 files, 38,065 lines**:

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
ls  docs/*.md issues/*.md | wc -l     # → 164
cat docs/*.md issues/*.md | wc -l     # → 38065
```

`docs/reviews/` is deliberately excluded from that corpus and from every grep below: it holds review
output rather than design, and three sibling round-2 lenses were writing into it while this ran, so a
count including it is not reproducible. Round-1 reviews were read, not counted.

Read in full: `DECISIONS.md` (§1, §5, **§5.1 amendments A-1…A-4**, §6, §7), `COMPETITOR-BENCHMARK.md`
(all of it — §0 legend through §10 counts), `DESIGN-SET-DEFECTS.md` `X-045` and `X-050`,
`INDIA-LOCALISATION-PACK.md` §0 and §4.2, `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.1–§6.26 headings
and ~90 individual `FR-` rows. Spot-read `DATA-MODEL.md`, `GAP-REGISTER.md`, `MODULE-INTEGRATION.md`,
`IRREVERSIBLE.md`.

The benchmark's own row count reproduces exactly, using the document's own command:

```bash
sed -n '148,492p' docs/COMPETITOR-BENCHMARK.md | grep -E '^\|' | grep -vE '^\|-' | grep -vcE '^\| Capability \|'
# → 236
```

**Method, in three sentences.** I read the 236-row benchmark and the ladder first, so that "absent from
the set" could be told apart from "present in a later version" — the latter is a schedule, not a gap.
I then searched the 2026 feature sets of the six segments the benchmark scores, preferring the vendor's
own page over any listicle, and grepped every candidate capability against `docs/` and `issues/` before
allowing it to become a finding. Every competitor claim below carries an inline URL and a date; where a
search did not reach a vendor-owned page I have written `UNVERIFIED` and said what would settle it,
because a fabricated competitor feature is worse than a gap — it puts a false row into a sales document.

---

## §1 · Verdict

The benchmark is the best document in this set and it is **twenty-four hours out of date in a way that
matters commercially**, because the four `DECISIONS.md` §5.1 amendments landed on 2026-09-01 and nothing
in `COMPETITOR-BENCHMARK.md` moved. As it currently reads, this sales-facing document tells a
salesperson that at v1 we cannot take a return and cannot print a label — both became false on the day
the amendments were taken. `X-050` names four consequences of that staleness; there are **nine**, and
the five it does not name are in the tables a salesperson actually reads (§4.1, §4.2, §2.16, §5.1).
Correcting them is the cheapest high-value edit available to this project and `J-004` supplies the
replacement text.

On genuine market gaps, the news is better than expected: I went looking for the things 2026 competitors
shout about — cartonisation, slotting, labour standards, yard, client portals, consigned inventory,
landed cost, robotics orchestration, marketplace breadth — and **the 236 rows already carry every one of
them**, correctly placed or explicitly refused. This benchmark was built by people who knew the market.
There are only three real absences, and one of them is a hole in the floor.

That one is India. `A-4` moved e-way bill *generation* into **v1/P2-IN**, and from **1 August 2026** the
GSTN made Ship-To GSTIN mandatory in the e-Invoice and e-Way-Bill-by-IRN APIs. `whb_transport_details`
carries a `ship_to_*` **address** block and no GSTIN column, in the **base** module, which means the
column has to land in the `whb_` migration band or be retrofitted across a base table later. A v1 that
generates an e-way bill payload the NIC API rejects is a v1 an Indian customer cannot go live on. That
is `J-001` and it is the only BLOCKER here. Behind it, the India pack's own RE-VERIFY table is more than
a year stale and misses five in-force GSTN changes (`J-002`).

**The blunt answer.** The single competitor capability absent from this set that would most often lose us
a deal in 2026 is **a conversational AI assistant over the warehouse's own data** — "show me every
adjustment over ₹50,000 last month and who approved it", asked in plain language. Manhattan, Blue Yonder,
Infor, Cin7 and Odoo all shipped one in 2025–2026 and it is now the first line on the RFP, above waves
and above labour. But the honest verdict is that **it is not a v1 column and it is not a v2 project — it
is a paragraph.** The set contains **zero** occurrences of `agentic`, `conversational`,
`natural language`, `LLM`, `copilot`, `chatbot`, `machine learning` or `GenAI` across all 38,065 lines,
and the only 10 occurrences of the token `AI` are GS1 *Application Identifiers*. What is missing is not
the feature; it is a **stated position** — §7 of the benchmark says every refusal must appear in the
place a reader would look for the feature, and that rule is violated for the most-asked question of 2026.
Write the refusal row with its re-entry path, keep exactly one narrow non-refused item (natural-language
query over the immutable movement register, which this ledger is unusually well-shaped for), and decline
the other eleven things the AI wave is selling. That is `J-003`, and it costs a day, not a phase.

---

## §2 · The findings

### §2.0 · The capability delta — what 2026 competitors ship, against our 236 rows

Every row below was grepped against `docs/` and `issues/` before it was scored. "NONE" in the benchmark
column means the capability does not appear in any of the 236 rows.

| Capability (2026) | Who ships it, with the vendor page | Our status | Benchmark row that covers it | Verdict |
|---|---|---|---|---|
| **Conversational / agentic assistant embedded in the WMS** | Manhattan Active Agents, commercially available Jan 2026 ([manh.com](https://www.manh.com/about-us/newsroom/press-releases/manhattan-associates-announces-commercial-availability-of-its-ai-agent-workforce)) · Blue Yonder Warehouse Operations Agent ([blueyonder.com](https://blueyonder.com/blog/2025/introducing-your-partner-the-warehouse-operations-agent)) · Infor April-2026 release, 7 ML/GenAI WMS capabilities + Agentic Orchestrator ([infor.com](https://www.infor.com/blog/infor-industry-ai-2026-04-release)) | **absent** | **NONE** | **`J-003`** — needs a stated position, not a feature |
| ML **anomaly detection** on inventory/location data | Infor "undersized location anomaly detection", 2026 release ([infor.com](https://www.infor.com/blog/ai-meets-warehousing)) · Blue Yonder Ops Agent monitors fill rate, cycle counts, idle inventory | **absent** (`grep -rin "anomaly" docs/ issues/` → 2 hits, both about *this document set's* anomalies) | **NONE** | folded into `J-003`; the count-variance case is the only one worth a row |
| **Supplier-document capture** (invoice/GRN from a PDF) | NetSuite 2026.1 landed-cost-at-receiving flow · Extensiv · Fishbowl — and **`doc-ocr-ai/` in this very monorepo** | **absent** | **NONE** | **`J-005`** |
| ML **pick-path optimisation** | Infor, up to 25 % travel reduction ([infor.com](https://www.infor.com/mea/blog/ai-that-moves-your-warehouse-forward)) | v3 analysis; solver **refused #7** | §2.9 / §7 #7 | **decline** — already refused, correctly |
| **Demand forecasting / replenishment planning** | Cin7 ForesightAI · Odoo 18/19 `ai_inventory_forecast` (NeuralProphet) ([apps.odoo.com](https://apps.odoo.com/apps/modules/18.0/ai_inventory_forecast)) · Zoho Zia · Blue Yonder | **refused #8** | §2.11 / §7 #8 | **decline** — already refused, correctly, and 2026 has not changed the argument |
| **Cartonisation algorithm / dim weight** | Infor "advanced cartonization" 2026 · SkuVault · ShipHero | v2 (`F-038`); item dimensions and stackability are **v1 columns** | §2.10 row "Pack session … / cartonisation"; `FR-191` | **sound** — schedule, not gap |
| **3PL billing automation + client portal** | Extensiv Billing Manager ([help.extensiv.com](https://help.extensiv.com/en_US/extensiv)) · Da Vinci Unified 3PL Billing · Deposco | v2 | §2.14; §4.1 Extensiv row | **sound** — and the billable-event emission is v1 (`FR-331`), which is the part that cannot be added later |
| **Consigned inventory** as a first-class object | NetSuite 2026.1 Consigned Inventory Management (`UNVERIFIED` — netsuite.com returned HTTP 403; verify at `docs.oracle.com` NetSuite Help, "Consigned Inventory") | v1 — `owner_id` on the **line** | §2.14; `FR-042`, `FR-110` | **sound, and we are ahead**: consignment is the ledger's native shape, not a bolt-on |
| **Landed cost at receiving** | NetSuite 2026.1 (same `UNVERIFIED` caveat) | v1 mention | §2.13; `grep -ril "landed cost"` → 23 files | **sound** |
| **Mixed-fleet robotics / WES orchestration** | Deposco · Logiwa IO · Körber (Aberle) | **refused #5**, with `actor_type = DEVICE` as the re-entry | §7 #5 | **decline** — the port already anticipates it |
| **ACES 5.0 / PIES catalogue ingest** | Epicor PIM for Automotive + Epicor Catalog, 17 M part numbers / 1.4 bn vehicle applications ([epicor.com](https://www.epicor.com/en-us/products/business-intelligence-and-data-management/pim-for-automotive/)) | v3 (`E-059`) | §2.3 last row | **sound as a schedule**, but the *cell* is wrong — `J-006` |
| **WhatsApp document delivery** (challan/invoice to the buyer) | Marg ERP WhatsApp invoicing · Busy Saffron · Vyapar | **absent** from all 236 rows | **NONE** | **`J-007`** — cheap; platform already ships the provider |
| **Ship-To GSTIN in the IRN / EWB payload** | Statutory, not competitive: GSTN Advisory 664 of 17 Jun 2026, effective 1 Aug 2026 ([tutorial.gst.gov.in](https://tutorial.gst.gov.in/downloads/news/advisory_einvoice_api_ewb_by_irn_approved.pdf)) | **absent** | §2.16 e-way row (which does not name the field) | **`J-001` — BLOCKER** |
| **Voluntary EWB Closure** | Same advisory, effective 1 Aug 2026 | **absent** | **NONE** | **`J-002`** |
| AI-driven inventory rebalancing; wearable hands-free scanning | Dynamics 365 SCM 2026 release wave 1 — **`UNVERIFIED`**: `learn.microsoft.com/.../release-plan/2026wave1/...` returned 404 on 2026-09-02. Verify by opening the D365 SCM 2026 wave 1 release plan from `learn.microsoft.com/en-us/dynamics365/release-plan/` and confirming the feature names and GA dates | rebalancing ≈ **refused #8**; wearables ≈ v1.1 RF | §2.12 | not filed — see §4.1 |

---

### `J-001` · `whb_transport_details` has no Ship-To GSTIN, and from 1 August 2026 the NIC API rejects a payload without one — **BLOCKER**

- **What is missing or wrong:** `DECISIONS.md` §5.1 **`A-4`** moved *"e-way bill payload and generation"*
  into **v1 / P2-IN**. The field source for that payload is `whb_transport_details`, which
  `DATA-MODEL.md:919` describes as carrying *"every field an e-way bill needs"* and lists as
  `dispatch_from_*` **address** block + `ship_to_*` **address** block. There is no `ship_to_gstin`
  column anywhere in the set. **GSTN Advisory No. 664 dated 17 June 2026**, effective **1 August 2026**,
  makes Ship-To GSTIN **mandatory** in the e-Invoice API and the e-Way-Bill-by-IRN API wherever Ship-To
  information is present, with the literal value `URP` where the consignee is unregistered
  ([GSTN advisory PDF](https://tutorial.gst.gov.in/downloads/news/advisory_einvoice_api_ewb_by_irn_approved.pdf) ·
  [ClearTax, 2026](https://cleartax.in/s/e-way-bill-changes-june-2026) ·
  [LiveLaw, 2026](https://www.livelaw.in/articles/mandatory-ship-gstin-voluntary-closures-legal-guide-eway-bill-update-542078)).
  The `URP` sentinel is itself absent — the address block has no way to say "unregistered".
- **Why it matters:** the day a dealership group in Maharashtra tries to move a pallet of parts from the
  Pune branch to the Nashik branch, the storekeeper presses **Generate e-way bill** on the transfer
  order, the payload goes to the IRP/NIC endpoint without `ShipToGSTIN`, and the API returns a
  validation error. There is no screen field to fix it and no column to put it in. The truck does not
  leave. This is not a degraded feature; it is the v1 India wave failing at its single purpose, which
  `A-4` states as *"the documents required to move goods legally."* And because
  `whb_transport_details` is a **base** (`whb_`) table, adding the column later means a migration into
  the base band after base has frozen, plus a backfill of rows for which the GSTIN was never captured.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -niE "ship_to_gstin|ship-to gstin|shipToGstin|\bURP\b" docs/*.md issues/*.md
  # → no output (0 lines)
  grep -n "whb_transport_details" docs/DATA-MODEL.md
  # → 919:  ... `dispatch_from_*` address block, `ship_to_*` address block, `driver_name`, ...
  ```
- **Where it belongs:** `warehouse-base` (the column) + `warehouse-india` (the validation and the `URP`
  rule) · **v1** · **P0** for the column, **P2-IN** for the behaviour.
- **Disposition:** *fold into task `P0-03`* (the `whb_` masters/transport migration — confirm the exact
  task id against `IMPLEMENTATION-PLAN.md` before the PR; if `P0-03` does not own
  `whb_transport_details`, it belongs to whichever P0 task does). **The line to add:** *"`whb_transport_details`
  carries `ship_to_gstin VARCHAR(15)` and `dispatch_from_gstin VARCHAR(15)`, both nullable at the base
  layer; `warehouse-india` enforces that `ship_to_gstin` is present and is either a valid GSTIN or the
  literal `URP` before an e-way bill or IRN payload is built (GSTN Advisory 664, effective 2026-08-01)."*
  A matching `FR-` row is needed under `FR-308`'s area.
- **Irreversibility:** **irreversible.** The column must land in the `whb_` band before base freezes at
  `PNR-1` = `V500030`. After that it is an `ALTER` on a base table plus an unbackfillable data gap —
  the GSTIN of a consignee on a movement that already happened cannot be reconstructed.
- **Relationship to round 1:** **new.** No round-1 finding and no `X-` defect names the Ship-To GSTIN
  field. `X-5` (in `DATA-MODEL.md` §3.4) concerns `whb_transport_details.document_id` having no FK — a
  different defect on the same table.

---

### `J-002` · The India pack's statutory watch-list is fifteen months stale — five in-force GSTN changes are absent — **MAJOR**

- **What is missing or wrong:** `INDIA-LOCALISATION-PACK.md` §0 carries a RE-VERIFY table (lines 45–51)
  holding e-way bill thresholds, 1-day/200-km validity, ODC rules and the 24-hour cancellation window
  *"as of a May 2026 knowledge cutoff"*, and `COMPETITOR-BENCHMARK.md` §9.2 repeats the instruction to
  re-verify. Five changes that are **already in force** are absent from the pack, from the FRD and from
  every task file. Reported as one finding per `DECISIONS.md` §7 rule 8, with the computed list:
  1. **180-day document-date restriction** — an e-way bill cannot be generated against a document dated
     more than 180 days before generation. GSTN advisory 17 Dec 2024, **live on the portal 1 Jan 2025**
     ([binarysemantics.com, 2026](https://www.binarysemantics.com/blogs/e-way-bill-180-day-rule/)).
  2. **360-day extension ceiling** — extension of an EWB is capped at 360 days from original generation
     (same advisory). The pack models validity and extension but not the ceiling.
  3. **Mandatory two-factor authentication** for e-invoice and e-way bill generation, **all taxpayers
     irrespective of turnover, from 1 April 2025**
     ([ClearTax, 2026](https://cleartax.in/s/2-factor-authentication-in-e-invoice-system)). This is a
     credential-storage and session design constraint on the GSP integration, not a field.
  4. **E-Way Bill 2.0 portal** (`ewaybill2.gst.gov.in`), launched July 2025 and running **in parallel**
     with the original portal — a dual-endpoint reality for any GSP client.
  5. **Voluntary EWB Closure API**, new in GSTN Advisory 664, effective **1 August 2026** — a taxpayer
     may close an e-way bill once delivery is complete, before its validity expires. It is a new
     lifecycle state the design does not have.
- **Why it matters:** items 1 and 5 bite operationally. A parts distributor raising a challan against a
  supplier invoice from seven months ago — routine in a warranty or core-return flow — gets a portal
  rejection with no explanation from our screen, because our validation does not know the rule exists.
  Item 5 bites the other way: the benchmark's §2.16 e-way row lists *"Part A + Part B lifecycle,
  validity, consolidated, cancellation"* as the complete lifecycle, and it is now **cancellation +
  closure**. An EWB left open past delivery is exactly the pattern that draws a departmental query.
  Items 3 and 4 are integration-design constraints that cost a rewrite if discovered during P2-IN
  rather than during its design.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -niE "180[- ]day|360[- ]day|ewaybill2|EWB 2\.0|two-factor|\b2FA\b" docs/*.md issues/*.md
  # → no output (0 lines)
  grep -rin "closure" docs/INDIA-LOCALISATION-PACK.md
  # → 1007:  ... tamper-evident closure ...   (pharma packaging; unrelated)
  ```
- **Where it belongs:** `warehouse-india` · **v1** for items 1, 2 and 5 (they are validation and a
  lifecycle state on the v1/P2-IN e-way bill); **v1** design-constraint note for items 3 and 4 ·
  **P2-IN**.
- **Disposition:** *fold into task `P2-IN`'s e-way bill task* (name it from `IMPLEMENTATION-PLAN.md`
  before the PR). **The lines to add:** (a) *"EWB generation is blocked, with an explanatory message,
  where the source document date is more than 180 days before the generation date"*; (b) *"EWB extension
  is refused beyond 360 days from original generation"*; (c) *"`CLOSED` is a terminal EWB state
  alongside `CANCELLED`, reachable after delivery and before expiry, and the closure call is part of the
  gateway contract"*; (d) a design note that the GSP client must assume mandatory 2FA and a dual
  production endpoint. Then **update the §0 RE-VERIFY table's as-at date to 2026-09-02** and add these
  five rows to it, so the next reader re-verifies from the right baseline.
- **Irreversibility:** `reversible` for the validations. The **`CLOSED` state** should go into the EWB
  status enum in its first migration rather than being added to a live enum later — name it in the
  P2-IN migration.
- **Relationship to round 1:** **new.** `X-045` and `X-050` concern citations and ladder staleness; no
  round-1 finding re-verified a statutory rule against a current source. §9.2's own instruction
  (*"Treat none as current without checking"*) is what this finding discharges.

---

### `J-003` · The set has no stated position on AI, in a year when it is the first line of the RFP — **MAJOR**

- **What is missing or wrong:** across all 38,065 lines there is not one occurrence of `agentic`,
  `conversational`, `natural language`, `chatbot`, `LLM`, `copilot`, `machine learning`, `GenAI` or
  `generative AI`. Meanwhile, as of their 2026 vendor pages: **Manhattan** made its AI Agent Workforce
  commercially available in **January 2026**, embedded in every Manhattan Active solution
  ([manh.com press release](https://www.manh.com/about-us/newsroom/press-releases/manhattan-associates-announces-commercial-availability-of-its-ai-agent-workforce) ·
  [manh.com product page](https://www.manh.com/solutions/manhattan-active-platform/ai-agents-for-supply-chain-productivity));
  **Blue Yonder** ships a **Warehouse Operations Agent** that monitors fill rate, cycle counts and idle
  inventory, diagnoses root causes and pushes tasks to handhelds
  ([blueyonder.com](https://blueyonder.com/blog/2025/introducing-your-partner-the-warehouse-operations-agent) ·
  [AI agents index](https://blueyonder.com/why-blue-yonder/ai-and-machine-learning/ai-agents));
  **Infor's April 2026 release** shipped seven ML/GenAI WMS capabilities including anomaly detection and
  ML pick-path optimisation, plus an Agentic Orchestrator over a library of 100+ agents
  ([infor.com](https://www.infor.com/blog/infor-industry-ai-2026-04-release) ·
  [infor.com/blog/ai-meets-warehousing](https://www.infor.com/blog/ai-meets-warehousing)); **Cin7** ships
  ForesightAI as a paid add-on; **Odoo 18 and 19** ship an AI Inventory Forecast module using NeuralProphet
  ([apps.odoo.com](https://apps.odoo.com/apps/modules/18.0/ai_inventory_forecast)); and at the Indian
  end, **Unicommerce** advertises **"AI-based outbound QC"** on its WMS product page
  ([unicommerce.com](https://unicommerce.com/products/warehouse-management-system/)).
  **This is not a request to build any of that.** Refusal **#8** already declines forecasting and
  refusal **#7** already declines the slotting solver, and 2026 has given no reason to reopen either.
  What is missing is §7's own discipline applied to this topic: *"Each refusal must appear in the
  product documentation **in the place a reader would look for the feature**, with its reason. 'Not
  built, because X' is a credible answer in a sales conversation; silence is not."*
- **Why it matters:** the moment it bites is a demo, not a build. A prospect's IT head asks *"what's your
  AI story?"* — the single most common opening question in a 2026 software evaluation — and the person
  demoing has nothing written down: no refusal row to read from, no re-entry path, no honest
  differentiator. They will improvise, and what they improvise will either overclaim (which the first
  technical review kills) or concede the whole topic (which loses the deal to a product that has one
  paragraph more than we do). The benchmark's §8.2 one-paragraph answer — the document's most-used
  sentence — does not mention AI at all, in either direction.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -niE "\bagentic\b|\bcopilot\b|\bLLM\b|conversational|natural[- ]language|\bchatbot\b|machine learning|generative AI|\bGenAI\b" docs/*.md issues/*.md | wc -l
  # → 0
  grep -noE "\bAI\b" docs/*.md issues/*.md | wc -l
  # → 10   — and I read all ten: every one is a GS1 Application Identifier, e.g.
  #   docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:192  "GS1 element-string parsing (AI `01`/`10`/`17`/`21`/`00`/`310n` ...)"
  #   issues/p3-15.md:50                             "carries an implied decimal position in the AI itself"
  grep -niE "anomal" docs/*.md issues/*.md
  # → 2 hits: DATA-MODEL.md:10 and IMPLEMENTATION-PLAN.md:1207 — both about anomalies in *this
  #   document set*, neither about anomalies in inventory data
  ```
- **Where it belongs:** `warehouse` (the one non-refused item) · **v1.1** for that item; the refusal row
  itself is documentation and lands now.
- **Disposition:** *is a `D-`/`OD-` decision, not a task* — with one small task attached.
  1. Add **refusal #24** to `COMPETITOR-BENCHMARK.md` §7: *"Agentic AI that takes autonomous action on
     stock."* Reason: an agent that posts an adjustment, releases a hold or re-slots stock without a
     named human actor breaks the ledger's actor attribution and its approval path; a wrong number
     nobody can attribute is exactly the failure mode this whole design exists to prevent. Re-entry
     path: an agent may **propose** — it may never **post**. `actor_type` already distinguishes
     `DEVICE` (`T-059`, `F-072`); an `AGENT` actor type with proposal-only authority is the shape, and
     it is a v3 conversation.
  2. Add **refusal #25**: *"Vision-based counting and camera-based QC."* Reason: a hardware and
     calibration programme, not a feature; Unicommerce's AI outbound QC is the reference and it is
     bought with their fulfilment centres.
  3. Cross-reference refusals **#7** and **#8** from a new one-paragraph *"Our position on AI"* block in
     §8.2, so the reader who searches the document for "AI" finds an answer in the place they looked.
  4. **The one non-refused item:** a **natural-language query surface over the movement register** —
     read-only, translating a question into a bounded, parameterised query over `whb_stock_movements`
     and returning the same drillable register `E-075` already specifies. It is defensible precisely
     because the ledger is immutable and append-only: the assistant can only read, it cannot post, and
     every answer is reproducible by hand from the register beside it. This is the *"metric explainer"*
     principle (§2.17, R3 §4.7) applied to query. Sized as **v1.1**, one screen, no new table.
- **Irreversibility:** `reversible`. Nothing here is a column. Note only that the `actor_type` enum
  should be reviewed once with `AGENT` in mind before it is frozen, so a future proposal-only actor is
  not a schema change.
- **Relationship to round 1:** **new.** Seven round-1 lenses and 575 findings; `grep` above shows none
  of them used any of these words. R2's refusal list §4 was authored against the pre-agentic market.

---

### `J-004` · The benchmark's sales-facing loss tables are stale after `A-1`…`A-4` in nine places — `X-050` names four — **MAJOR**

- **What is missing or wrong:** `X-050` records that the §8.2 product verdict predates the §5.1
  amendments, and names four consequences: §8.2's returns sentence, §8.1 rows 12 and 15, and §9 rows
  1–4. It does not name the five rows a salesperson is most likely to read out loud — §4.1's first two
  rows, two §4.2 rows, §4.1's closing "segments that cannot be served at all at v1" clause, and two
  §2.16 rows. **What is new in this finding is the corrected text**, supplied below so the edit is a
  copy, not a re-derivation:

  | # | Where | Benchmark says (today) | Actually true after the §5.1 amendments |
  |---|---|---|---|
  | 1 | §4.1 row 1 | *"**RMA / sales return / purchase return.** The ladder puts reverse logistics in v2/P5 … This is the most damaging line in the table and it is self-inflicted"* | **Resolved by `A-1`.** Sales-return receipt, purchase return / RTV and disposition to a stock status (restock · quarantine · scrap) are **v1/P2**. We lose only on **full reverse logistics** — RMA portal, grading & refurbishment, credit interface, NDR/RTO/COD — which stays **v2/P5** |
  | 2 | §4.1 row 2 | *"Nothing in this codebase renders a label … v1.1. If v1 ships without it we lose to a spreadsheet with a Dymo"* | **Resolved by `A-2`.** Templated document and label printing, **including a ZPL path**, is **v1/P2**. What remains at **v1.1/P3** is the print server, printer routing and device management — a real but much narrower loss, and not to a Dymo |
  | 3 | §4.1 closing paragraph | *"apparel/footwear (a **v1 schema decision that has not been taken**)"* | **Resolved by `A-3`.** The variant model — style/parent item, variant axes and values — **is v1 schema**; the matrix screens, grids and reports are v2. The segment is reachable; the screens are the schedule |
  | 4 | §4.2 row "Anyone needing an apparel matrix" | *"Still undecided, and unrecoverable if the v1 schema shipped flat"* | **Delete the row.** `A-3` took the decision and it went the way this row feared it would not |
  | 5 | §4.2 row "The whole Indian statutory set" | *"Cannot file: no e-way gateway, no IRP, no Rule 56 stock account, no ITC-04 \| Closes at v2"* | **Half-resolved by `A-4`.** At v1 we ship the **delivery challan, the e-way bill payload and generation, the GST-aware transfer document, HSN on the item and cross-GSTIN transfer as a supply** (v1/P2-IN). The remaining loss is **IRP/e-invoice, Rule 56 and ITC-04**, at **v2/P4**. Rewrite the row to name only those three |
  | 6 | §2.16 row "Delivery challan as a numbered document" | *"**v1** doc-type mechanism / **v2** India pack"* | **v1/P2-IN in full.** `A-4` names the delivery challan explicitly as a v1 wave item |
  | 7 | §2.16 row "E-way bill Part A + Part B lifecycle …" | *"**v1 data** / **v2** gateway"* | **v1/P2-IN generation.** `A-4` names *"e-way bill payload **and generation**"*. Only the IRP round-trip stays v2. And see **`J-002`** — the lifecycle listed is missing the new `CLOSED` state |
  | 8 | §8.1 row 12 (Execution layer) | *"task model in v1, **no RF and no label until v1.1**"* — `Our v1 = ○` | *"task model **and templated label/document printing incl. ZPL** in v1; no RF until v1.1."* The mark moves **`○` → `◐`** |
  | 9 | §8.1 row 15 (Returns) | *"**`return_type` in v1 and nothing else.** The ladder's most damaging placement ‡"* — `Our v1 = ○` | *"Sales return, purchase return and disposition in v1; RMA portal, grading and the credit interface at v2."* The mark moves **`○` → `◐`**, and the `‡` and the "most damaging placement" gloss are deleted |

  Two further consequential edits: **§8.2's** clause *"and — as the ladder currently reads — **not yet
  able to take a return**, which is the one gap that would embarrass it in front of any buyer in any
  segment"* must be struck and replaced with *"able to receive a sales return and raise a return to
  vendor, but not to run an RMA portal or a grading and refurbishment flow (v2)"*; and **§9 rows 1, 2
  and 4** move from `UNRESOLVED` to **RESOLVED by `A-1` / `A-3` / `A-2` respectively**, leaving row 3
  (who owns cost layers) as the only unresolved item in the top four.
- **Why it matters:** this is the one document in the set written to be read *outside* the team.
  §8.2 is the paragraph a founder pastes into an email. As it stands it tells a prospect we cannot take
  a return — a statement that was true for one day and is now a self-inflicted disqualification. §8.1
  understates our v1 verdict in two of the three areas the same section flags as "below the median",
  which is the difference between "v1 is a ledger release, not a floor release" (true before `A-2`) and
  "v1 prints and takes returns" (true now).
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -n "A-1\|A-2\|A-3\|A-4\|5\.1" docs/COMPETITOR-BENCHMARK.md
  # → no output: the benchmark never references the amendments
  git -C . log -1 --format=%ci -- docs/DECISIONS.md docs/COMPETITOR-BENCHMARK.md
  # (the §5.1 block is dated 2026-09-01 in DECISIONS.md:342; COMPETITOR-BENCHMARK.md carries no such date)
  ```
- **Where it belongs:** documentation — `COMPETITOR-BENCHMARK.md` · no version · no phase.
- **Disposition:** *fold into `X-050`'s remediation* — apply the nine rows above verbatim, plus the two
  consequential edits. No new task id. When done, `X-050` can close and `X-045`'s dangling-citation
  sweep should run over the edited rows in the same pass.
- **Irreversibility:** `reversible`.
- **Relationship to round 1:** **materially extends `X-050`.** What is new: five stale locations `X-050`
  does not name (§4.1 rows 1–2 and its closing clause, §4.2 rows on Indian statutory and apparel, §2.16
  rows on the challan and the e-way bill), the two `○ → ◐` scoreboard mark changes, and the replacement
  text for every one of them.

---

### `J-005` · `doc-ocr-ai` — an OCR module this company already ships — is never named as a functional dependency — **MAJOR**

- **What is missing or wrong:** the monorepo contains `doc-ocr-ai/{backend,frontend,docs}` with its own
  Flyway band (V700000–V709999, `classic/CLAUDE.md` MODULES table). The warehouse design set names it
  **eight times and every one is a build artefact** — `pom.xml` line counts, a Railway
  `ENABLE_DOC_OCR_AI` flag, the module-directory listing. It is never considered as a **source of data**.
  Meanwhile the set's inbound flow requires a human to key every supplier invoice: `wh_three_way_matches`
  (v2) carries `supplier_invoice_ref`, `invoice_date` and `invoice_total` with no stated origin, and
  `FR-140`'s three-way match assumes those numbers arrive somehow.
- **Why it matters:** the moment it bites is the first customer demo where the prospect has already seen
  the same vendor's OCR module read a PDF. A parts store receiving 30–60 supplier invoices a day is
  re-keying header totals and line quantities that a module in the same repository could extract, and
  the answer *"that's a different product"* is not credible when both are on the same login. The
  commercial framing is stronger than the technical one: this is a capability we **own and are not
  claiming**, in a year where document capture is a standard mid-market line item.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -niE "\bOCR\b|doc-ocr" docs/*.md issues/*.md
  # → 7 lines, and I read all seven: MODULE-INTEGRATION.md:85,297,432,460,1091,1136 and
  #   PORT-AND-ADAPTER-CONTRACT.md:690 — every one is a pom.xml line count, a module-name loop,
  #   a startX2.sh flag or an "it is not an event source" aside. Zero functional references.
  grep -rilE "document capture|invoice capture|scan the invoice" docs/*.md issues/*.md
  # → no output
  ls -d /Users/bbhushan/work/git/workspace/classic/doc-ocr-ai/*
  # → .../backend  .../docs  .../frontend
  ```
- **Where it belongs:** `warehouse` (a consumer), reading `doc-ocr-ai` across the module seam · **v2** ·
  **P5** — it belongs with `wh_three_way_matches`, which is already v2.
- **Disposition:** *is a `D-`/`OD-` decision, not a task.* Take a one-line decision either way and write
  it where a reader looks: **either** *"`warehouse` consumes `doc-ocr-ai` for supplier-invoice header and
  line extraction at v2, alongside `FR-140`'s three-way match; extraction produces a **draft** the
  receiver confirms, never a posted document"* — **or** a refusal row with its reason. Silence is the
  only wrong answer, by §7's own rule. If accepted, it needs an `FR-` row under the FRD's inbound area
  and a note in `MODULE-INTEGRATION.md`, because it is a **new cross-module read** and this set is
  otherwise careful to enumerate every one of those (`M8`, `D-11` B9 is the precedent for how such a
  read must be shaped — snapshot, not a live table read).
- **Irreversibility:** `reversible`. It is a v2 read across a seam; no v1 column depends on it.
- **Relationship to round 1:** **new.** `MODULE-INTEGRATION.md` and R1 both name `doc-ocr-ai`, but only
  as a build-configuration precedent; no round-1 finding asks what it is *for*.

---

### `J-006` · §2.3 scores the ERP column `○` for vehicle fitment while its own neighbouring rows carry `◐ (Epicor ●)` — **MINOR**

- **What is missing or wrong:** in §2.3 (Catalogue depth), the supersession row is scored
  `ERP = ◐ (Epicor ●)` and the ACES/PIES row `ERP = ◐ (Epicor ●)`, but the **vehicle fitment** row is
  scored `ERP = ○ *(all six)*`. As of Epicor's 2026 product pages, **Epicor Catalog for Automotive**
  covers *"more than 17 million part numbers … from over 9,500 manufacturer product lines, covering in
  excess of 1.4 billion vehicle applications"*
  ([epicor.com](https://www.epicor.com/en-us/products/supply-chain-management-scm/catalog-for-automotive/)),
  and **Epicor PIM for Automotive** manages fitment and ACES/PIES compliance as its core purpose
  ([epicor.com](https://www.epicor.com/en-us/products/business-intelligence-and-data-management/pim-for-automotive/)).
  Fitment is the *most* `●` cell Epicor has, not the least. Separately: **ACES 5.0 releases 26 March
  2026** (`UNVERIFIED` against an Auto Care Association page — verify at `autocare.org`'s ACES standard
  page), so a v3 ingest will be ingesting a standard two revisions old.
- **Why it matters:** §2.3 opens with *"This is the table where the DMS column is `●` and every other
  column is `○` or `◐`. That gap is the product"*, and §8.1 row 3 calls catalogue depth *"the widest gap
  in our favour"*. **W1** — the first of the six claimed wins, and the one the whole automotive
  positioning rests on — is built on this table. A prospect who already uses Epicor data will notice the
  cell is wrong, and a wrong cell in a sales document costs more credibility than the half-mark it hides.
  The correction does not destroy W1: our claim is fitment **modelled in the item master and resolved at
  the counter**, which is a different thing from a subscription catalogue. But the claim has to be stated
  that way rather than resting on a `○`.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  sed -n '183,192p' docs/COMPETITOR-BENCHMARK.md | grep -n "fitment\|Supersession\|catalogue-standard"
  # → the supersession and ACES/PIES rows read "◐ (Epicor ●)"; the fitment row reads "○ *(all six)*"
  ```
- **Where it belongs:** documentation — `COMPETITOR-BENCHMARK.md` §2.3 and §3 W1 · no version · no phase.
- **Disposition:** *fold into `X-050`'s remediation pass* (same edit session as `J-004`). **The line to
  change:** score the vehicle-fitment row `ERP = ○ (Epicor ●)` for consistency with the two rows around
  it, and add one sentence to **W1**: *"Epicor is the named exception across this table; our claim is not
  that we have more fitment data than Epicor — we do not — but that fitment, supersession and core are
  modelled **in the item master the counter transacts on**, rather than in a subscription catalogue
  beside it."*
- **Irreversibility:** `reversible`.
- **Relationship to round 1:** **new.** §9.1 explicitly searched for a competitor-cell disagreement
  *between two audits* and found none; it did not check a cell against the vendor. This is the first
  such check, and it found one error in the sample.

---

### `J-007` · WhatsApp document delivery appears in none of the 236 rows, though Marg, Busy and Vyapar ship it and the platform already carries the provider — **MINOR**

- **What is missing or wrong:** no benchmark row and no `FR-` mentions WhatsApp. As of their 2026
  product pages, **Marg ERP** ships WhatsApp invoicing and WhatsApp ordering, and **Busy** (Saffron)
  and **Vyapar** ship WhatsApp document sending as standard for Indian SMB distribution
  (`UNVERIFIED` at the level of a single canonical vendor URL per product — verify at
  `margcompusoft.com`, `busy.in` and `vyaparapp.in` feature pages). Meanwhile the platform already
  ships the capability: `platform/backend/src/main/java/ai/platform/service/notification/whatsapp/provider/AisensyWhatsAppProvider.java:24`
  and `platform/backend/src/main/java/ai/platform/dto/whatsapp/WhatsAppMediaType.java:7`, whose enum
  includes `DOCUMENT`. The design set's only WhatsApp references are in two **v2/P5** issue files
  (`issues/p5-09.md:69`, `issues/p5-14.md:58`) and in R4 prose — all about *alert* notifications, never
  about **delivering the printed document** that `A-2` just moved into v1.
- **Why it matters:** `A-2` put document printing in v1/P2. In Indian distribution the challan and the
  invoice reach the buyer on WhatsApp, not by post and rarely by email — a driver leaves with the paper
  and the office sends the PDF to the buyer's number before the truck reaches the highway. A v1 that
  renders a delivery challan and can only print it or email it will be asked for this in the first week
  of the first deployment. It is one output channel on an existing render pipeline over an existing
  provider, which is why it is MINOR rather than MAJOR — but it is also why leaving it out is not a
  saving.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -nic "whatsapp" docs/COMPETITOR-BENCHMARK.md docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md
  # → docs/COMPETITOR-BENCHMARK.md:0
  #   docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:0
  grep -ni "whatsapp" docs/*.md issues/*.md
  # → issues/p5-09.md:69  "...already carries an AiSensy WhatsApp provider"
  #   issues/p5-14.md:58  "...the email-template registry and the AiSensy WhatsApp provider"
  #   — two hits, both v2/P5, both about *alerts*, neither about delivering a rendered document
  ```
- **Where it belongs:** `warehouse` (the send action), over `platform` (the provider) · **v1** · **P2**,
  with the document-printing task.
- **Disposition:** *fold into the P2 document-and-label printing task* (`A-2`'s task; name it from
  `IMPLEMENTATION-PLAN.md` before the PR). **The line to add:** *"A rendered document may be delivered on
  three channels — print, email and WhatsApp — through the platform's existing notification providers
  (`AisensyWhatsAppProvider`, `WhatsAppMediaType.DOCUMENT`). Warehouse adds no second provider."* Also add
  a row to `COMPETITOR-BENCHMARK.md` §2.10, scored `IN = ●` and `T1/ERP/3PL = ○`, so the India column is
  not silently over-scored. **One thing to verify before committing the line:** AiSensy sends
  *pre-approved template campaigns, not free text* (`AisensyWhatsAppProvider.java:29`) — confirm a
  document-media template can carry a generated PDF before promising the channel.
- **Irreversibility:** `reversible`.
- **Relationship to round 1:** **new** as a *document delivery* channel. R4 proposed WhatsApp as an
  **alert** channel (`R4:556`, `R4:1408`) and that is where the two v2 issue files inherited it; this is
  a different surface at a different version.

---

### `J-008` · §9.2's open `?` on SAP LE-WM's maintenance status is now answerable — **MINOR**

- **What is missing or wrong:** §9.2 lists eleven R2 uncertainties that must not be cited externally,
  the last being *"SAP LE-WM's maintenance status"*. It is settled: **compatibility scope for classic
  LE-WM on S/4HANA ended 31 December 2025**; from 1 January 2026 LE-WM receives no further technical or
  maintenance support. **Stock Room Management** — classic WM with a reduced scope, on the same data
  model — is the successor, is maintained until **2040**, and *"there will be no further investment …
  no further developments, as EWM is the strategic warehouse management solution"*
  ([SAP Community, EWM FAQ series on release strategy](https://community.sap.com/t5/supply-chain-management-blog-posts-by-sap/the-sap-extended-warehouse-management-faq-series-release-strategy-for/ba-p/14078542) ·
  [SAP Community, end of mainstream maintenance](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/the-sap-extended-warehouse-management-faq-series-end-of-mainstream/ba-p/13607684)).
- **Why it matters:** small, but it is a *sellable* fact rather than a gap. Every SAP ECC/S4 site still
  on classic WM had to decide something during 2025 and many chose Stock Room Management, which is
  explicitly frozen at basic warehouse processes. That is the precise profile of a plant or dealership
  store that would otherwise never be reachable, and it is worth one line in §5.2 ("which products we
  displace"). It also removes one of the eleven `?` cells the document forbids citing — which is the
  cheapest possible improvement to a document whose §9.1 caveat is currently its weakest section.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -niE "stock room management|LE-WM" docs/*.md
  # → docs/COMPETITOR-BENCHMARK.md:975 (the "?" list) only; "Stock Room Management" → no output
  ```
- **Where it belongs:** documentation — `COMPETITOR-BENCHMARK.md` §9.2 and §5.2 · no version · no phase.
- **Disposition:** *fold into `X-050`'s remediation pass.* Remove *"SAP LE-WM's maintenance status"*
  from the §9.2 forbidden-citation list and record the resolved fact with its date and source.
- **Irreversibility:** `reversible`.
- **Relationship to round 1:** **extends R2 Appendix A** — it closes one of its eleven declared
  uncertainties rather than adding a finding. New only in the sense that no round-1 lens had web access.

---

## §3 · What I checked and found sound

The 2026 market's loudest capabilities, checked one by one against the 236 rows and the FRD. Every one
of these was a candidate finding and every one is already correctly placed or explicitly refused. This
list exists so round 3 does not walk the ground again.

| Capability I went looking for | Where the set already covers it | Verdict |
|---|---|---|
| Cartonisation algorithm and dimensional weight | §2.10 *"Pack session with sealed cartons / cartonisation"* → v1.1 pack session (`P-037`), **v2** algorithm (`F-038`); `FR-191` puts item dimensions, weight and stackability in **v1 columns** and states why | correct: the columns are v1, the algorithm is v2 |
| Slotting optimisation | Refusal **#7**, with the *analysis* (velocity, cube, affinity) explicitly **not** refused and placed at v3 | correct, and Infor's 2026 ML slotting does not change the argument |
| Engineered labour standards / labour management | Refusal **#3**; actual task duration measured from `T-058` and actual-vs-target reporting at v2 is **not** refused | correct — Manhattan LM alone is larger than our v1 |
| Yard and trailer management | Refusal **#23**; `wh_dock_appointments` is the join and exists in **v1 schema** (`DATA-MODEL.md`, *"schema in v1 even though the scheduling screen is v1.1 — the detention clock cannot be backfilled"*) | correct, and the detention-clock reasoning is better than most competitors' |
| 3PL billing automation, rate cards, billing runs, client portal | §2.14 and §4.1's Extensiv row; billing is v2, and the **billable-event vocabulary is fixed in v1** at billable granularity (`FR-331`) | correct — the v1 part is the part that cannot be added later, and they got that right |
| Consigned inventory as a first-class object (NetSuite 2026.1) | `owner_id` **on the line, not the header**, with `balance_rule` and `allows_mixed_owner` (`FR-042`, `FR-110`) | **we are ahead**: consignment is the native shape here, not a bolt-on |
| Landed cost at receiving | 23 files reference it; §2.13 and the valuation seam | covered |
| Mixed-fleet robotics / WES orchestration (Deposco, Logiwa IO, Körber) | Refusal **#5**, re-entry via an adapter posting through the port with `actor_type = DEVICE` (`T-059`, `F-072`) | correct, and the port already anticipates it |
| Voice picking | Refusal **#6**; v3 as an interface, never as a recogniser | correct |
| Marketplace connector breadth (Unicommerce 280+, EasyEcom, Vinculum) | §4.3 *"never at their breadth"*; §4.1 declines the D2C segment at v1 | correct, and honestly stated |
| Consumer returns portal (ShipHero, Shiprocket, Unicommerce) | Refusal **#18**, re-entry as an API — `wh_rmas` accepts an externally created RMA | correct |
| Multi-tenant SaaS economics (Oracle WMS Cloud, Manhattan Active) | Refusal **#12** and §4.4's closing paragraph, which names it as a cost structure rather than a feature | correct and unusually honest |
| Recall and forward/backward traceability | `FR-280` (recall, v2/P5), `FR-396` (traceability, v1/P2), §9 row 13 records the R2-vs-R5 disagreement | covered |
| MRP as a lot attribute and MRP re-stickering (Legal Metrology) | `FR-095` puts MRP on the lot in **v1**; `FR-320`/`FR-321` and `whin_mrp_revisions` model revisions | covered — and this anticipates the Sept-2025 GST 2.0 re-sticker event, which is more foresight than most Indian ERPs showed |
| E-way bill Part A vs Part B behavioural split, and which movements need one | `INDIA-LOCALISATION-PACK.md` §4.2, including the movement→EWB decision table, the field-source table, and the argument for `wh_` rather than `whin_` transport details | genuinely good, and the reason `J-001` is a missing column rather than a missing design |
| GSP integration non-goals (no clear-text compliance logs, no demo controller triggering real filings, no schema-only statutory flow) | §4.2's three stated non-goals | covered, and worth keeping verbatim |
| ACES/PIES ingest, supersession, interchange, core/exchange | §2.3, with Epicor named as the ERP exception on two of three rows | covered — see `J-006` for the third row |
| AI-driven inventory rebalancing (D365 2026 wave 1) | Substantively **refusal #8** (replenishment planning) | not filed; the rebalancing claim is `UNVERIFIED` anyway (see §2.0) |

---

## §4 · Refused

### 4.1 · Candidate findings I did not file

- **"No forecasting / no MEO / no seasonality."** Refusal **#8**, argued well, with a re-entry path that
  names `whb_stock_movements.occurred_at` as exactly the history a forecaster needs. 2026 changed the
  packaging (an agent instead of a screen), not the argument. Filing it would restate a decision.
- **"No slotting solver."** Refusal **#7**. Same reasoning.
- **"No SOC 2 / ISO 27001 / penetration-test evidence anywhere"** — `grep -rilE "SOC 2|SOC2|ISO 27001|penetration test" docs/*.md issues/*.md` → 0 files. This is real and it does appear on 2026 RFPs, but it is **R13's lens** (non-functional and ops), not a competitor-capability gap. Left to R13 deliberately rather than filed twice.
- **"No carbon / ESG / emissions reporting per shipment"** — `grep -rilE "\bcarbon\b|\bESG\b|sustainab" docs/*.md issues/*.md` → 0 files. Tier-1 vendors market it. Declined on segment: see §4.2 below.
- **"Offline-writing thick client."** Refusal **#22**; the offline *capture* case is v1.1. Correct.
- **"Retail-compliance EDI / ASN 856 / chargebacks."** Refusal **#20**. No Indian customer in the target segment needs it.
- **Every §2 row I checked and found correctly placed** — listed in §3 rather than filed, per the brief's rule that restating round 1 is worse than silence.

### 4.2 · What we should explicitly decline — proposed refusal rows #24–#29

The backlog must not grow by two hundred rows because the market spent 2026 announcing things. Each of
these is a capability a named competitor ships, that a real target customer of **this** product —
a 3–8 branch dealership parts group, a workshop chain, an Indian distributor — never asks for. Each is a
`WONTFIX` **with a reason**, which §7 already establishes is a credible sales answer where silence is not.

| # | Decline | Who ships it | Why we decline it | Re-entry path |
|---|---|---|---|---|
| **24** | **Agentic AI that takes autonomous action on stock** — an agent that posts an adjustment, releases a hold, re-slots or re-waves without a named human | Manhattan Active Agents (GA Jan 2026) · Blue Yonder Warehouse Ops Agent · Infor Agentic Orchestrator | The entire value of this product is a ledger where every movement has an attributable actor and an approval path. An agent that posts is a number nobody can explain, which is the exact failure this design exists to prevent. It is also unsellable to the auditor who signs the s.44AB stock statement | An agent may **propose**; it may never **post**. An `AGENT` actor type with proposal-only authority, alongside `DEVICE` (`T-059`, `F-072`), at v3 |
| **25** | **Vision-based counting and camera QC** | Unicommerce "AI-based outbound QC" · several 3PL vendors | A hardware, lighting and calibration programme sold with a fulfilment centre, not a software feature. Our counting differentiator is variance approval and the reason-code catalogue, which is where the money actually leaks | None as a built capability. A count variance may be *evidenced* by a photo — `FR-206` and `FR-272` already do this |
| **26** | **An AI agent builder / agent marketplace** (configure your own agents) | Manhattan Agent Foundry · Infor's 100+ agent library | This is refusal **#10** — the general-purpose rules engine / scripting layer — wearing a 2026 label. Bounded, ordered, typed rule tables stay reviewable; an agent-authoring surface is where business logic hides from code review, with less determinism than a script | The same as #10: a new **bounded operator**, reviewed once. Never an authoring surface |
| **27** | **Carbon / ESG / emissions reporting** per movement, shipment or facility | Blue Yonder · Manhattan · SAP · most tier-1 sustainability modules | It sells to a European retail buyer with a CSRD obligation. It does not sell to a dealership parts group in Nashik, and the emission factors are a data subscription we would have to buy and maintain | Export movement and transport data; a specialist tool consumes it. The `distance_km` and `transport_mode` columns already there are the join |
| **28** | **Digital twin / 3D warehouse visualisation / shift simulation** | Infor 3D visualisation · Blue Yonder simulation | Already refusal **#15**; restated here only because the 2026 marketing wave has renamed it "warehouse digital twin" and it will be re-proposed under the new name | Unchanged from #15 |
| **29** | **Autonomous / self-configuring setup from a natural-language description** ("describe your warehouse and the system configures itself") | marketed by several tier-1 and 3PL vendors during 2026 | Configuration in this product is `whb_` master data with referential integrity and irreversible rows (`IRR-01`…`IRR-63`). A generated configuration that is wrong is not a bad suggestion — it is an unbackfillable schema decision made by a machine. `PNR-1` exists precisely because these choices are not reversible | Guided setup with **explicit, reviewable** defaults per vertical — the adapters already are this, and they are better than a prompt |

Note that #24, #26 and #29 all resolve to the same principle the set already holds: **bounded and
attributable beats flexible**. Writing them down as three rows rather than one is deliberate — each will
be proposed separately, by a different person, in a different quarter.

---

## §5 · Counts

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
grep -cE '^### `J-[0-9]{3}`' docs/reviews/R15-competitor-benchmark-r2.md          # → 8
grep -oE '^### `J-[0-9]{3}`.*— \*\*(BLOCKER|MAJOR|MINOR)\*\*$' docs/reviews/R15-competitor-benchmark-r2.md \
  | grep -oE 'BLOCKER|MAJOR|MINOR' | sort | uniq -c
# →   1 BLOCKER
#     4 MAJOR
#     3 MINOR
grep -cE '^\| \*\*2[4-9]\*\* \|' docs/reviews/R15-competitor-benchmark-r2.md      # → 6  (proposed refusals #24–#29)
```

| Severity | Count | Findings |
|---|---|---|
| **BLOCKER** | **1** | `J-001` |
| **MAJOR** | **4** | `J-002` `J-003` `J-004` `J-005` |
| **MINOR** | **3** | `J-006` `J-007` `J-008` |
| **Total** | **8** | |

**Other outputs of this lens, not counted as findings:** 6 proposed refusal rows (#24–#29, §4.2);
a 15-row capability-delta table (§2.0); the 9-row `benchmark says → actually true` rewrite that
discharges the un-named portion of `X-050` (inside `J-004`); 18 capabilities checked and found sound
(§3); and one previously-forbidden `?` cell resolved (`J-008`).

**Dispositions:** 2 *fold into an existing task* (`J-001`, `J-007`) · 1 *fold into a task, with lines
supplied* (`J-002`) · 2 *is a `D-`/`OD-` decision, not a task* (`J-003`, `J-005`) · 3 *fold into
`X-050`'s remediation pass* (`J-004`, `J-006`, `J-008`) · 0 new task ids required · 6 `WONTFIX` with
stated reasons (§4.2).

**Unverified claims, carried openly:** NetSuite 2026.1 feature names (netsuite.com HTTP 403 — verify at
`docs.oracle.com` NetSuite Help); D365 SCM 2026 wave 1 AI rebalancing and wearables
(`learn.microsoft.com` release-plan URL 404 on 2026-09-02 — verify from the release-plan index); ACES 5.0's
26 March 2026 release date (verify at `autocare.org`); and the Marg / Busy / Vyapar WhatsApp claims at
single-vendor-URL precision. None of these carries a finding on its own.
