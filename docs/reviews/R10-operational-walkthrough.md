# R10 — The end-to-end operational walkthrough: does a whole day's work actually complete?

<!-- FR-447 was a proposal when this file was written; it is now a real row in WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md §6.27, so the fr-citations exemption that stood here has been removed rather than left stale -->
<!-- check-design-set: scenario-citations file WH-SC-306 — the SCENARIO-CATALOGUE.md §5 rule 3 allocation marker, the next free scenario id. Same allocation DESIGN-SET-DEFECTS.md and GAP-REGISTER.md already declare. Round 2 took WH-SC-301-WH-SC-305 for SCENARIO-CATALOGUE.md 3.21, so the marker — and this declaration with it — moved to WH-SC-306 -->

**Date** 2026-09-02 · **Prefix** `U-` · **Branch** `docs/round-2-functional-review`

**File set read.**

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
ls docs/*.md docs/reviews/*.md issues/*.md \
  | grep -vE 'reviews/R(8|9|10|11)-' | wc -l                  # → 171  (the set as it stood, excluding round-2 output)
grep -rohE "\bU-[0-9]{1,3}\b" docs/ issues/ | wc -l         # → 0   (the prefix is free)
```

Read in full: `DECISIONS.md`, `README.md`, `GAP-REGISTER.md` §2/§4/§5/§7, `DESIGN-SET-DEFECTS.md`
§1/§2/§6.4, `BUILD-SPEC-SCREENS.md` §1 (all 237 rows) and the §3 blocks for every screen a journey
touches, `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` (all 446 rows extracted and indexed),
`SCENARIO-CATALOGUE.md` (all 300 rows extracted and indexed), plus targeted reads of `DATA-MODEL.md`,
`PLATFORM-DEPENDENCIES.md`, `INDIA-LOCALISATION-PACK.md`, `IMPLEMENTATION-PLAN.md` and 14 task files.

**Method, in three sentences.** Round 1 asked *"does the set cover topic X?"* seven times; this lens
asks the opposite question — *walk the work*, step by step, as the human doing it, and at every step
name the screen (`WS-nnn`), the requirement (`FR-nnn`) and the scenario (`WH-SC-nnn`) that make the
step possible, or write **NONE**. Every id cited below was grepped and its text read before it was
written down, because the predecessor set shipped 19 citations that resolved to a different real
requirement. A step that returns NONE on all three is a gap; a step that returns NONE on one of three
is usually a traceability gap; a step whose *column* exists in v1 but whose *writer* does not is the
failure mode this lens exists to catch, and it is the shape of four of the six findings below.

---

## §1 · Verdict

The design set is unusually strong on **objects** and unusually weak on **the moment a person does
something to an object**. Every one of the ten journeys has its tables designed, its invariants
argued and its scenarios written; three of them cannot be executed by a human being in v1 because the
screen that performs a mandatory step was placed in v1.1 while the column it writes was pulled into
v1, and nobody re-read the pair together. That pattern — *v1 column, v1.1 writer* — occurs four times
(cartons, dock arrival, alert recipients, delivery confirmation), and it is not a version-ladder
quibble: in three of the four the set states in its own words that the value **cannot be created
retroactively**, so a v1 install accumulates a permanent hole exactly where the set argued the data
was too important to defer. The most expensive single omission is the **carton**: `FR-191` makes
cartons mandatory and enumerates six reasons, `FR-206` requires the pack photo and scale weight at
pack time *in v1*, and the only screen that can create or seal a carton is `WS-103`, which is v1.1 —
`WS-104` (v1) can view and print but not create, and `P2-11` closes the gap in prose ("v1 creates
cartons from the shipment screen") naming an action that appears in **no** screen contract anywhere in
the set. Second most expensive: in v1 **nothing tells anyone anything** — the alert rule, condition,
recipient and event tables are all v1.1, the supervisor exception console (`FR-216`) is v1.1, and six
v1 requirements (two of them **P0**) each demand a notification with *configured* recipients; the
storekeeper's discrepancy, the rebuild-drift alarm and the rejected accounting handover all land in a
grid nobody is told to open. Third: `whad_counter_sales` computes `tax_amount` and takes
`payment_mode` in **v1**, which is the losing side of `OD-9` ("warehouse never computes tax") and a
direct contradiction of `FR-274` ("no refund screen, no refund amount and no payment path in any
warehouse module in any version") — and `OD-9`'s stated deadline, *before `P2-IN`*, falls **after**
`P2-25`, the P2 task that builds the table.

**Blunt answer.** Journeys **1 (Day 0)**, **4 (the stock controller's month)**, **6 (returns)**,
**9 (3PL)** and **10 (India compliance)** complete end to end — journey 1 is the best-designed thing
in the set and journey 4 is close behind. Journeys **2 (inbound)**, **5 (transfer)** and
**7 (adapters)** complete with a hole: gate arrival is uncapturable in v1, and the counter sale's
money leg has no owner. **Journey 3 — an order's whole life — is the one that breaks first, and it
breaks at step 11, pack**: after a picker has moved stock to staging, there is no v1 surface on which
a carton can be created or sealed, so `wh_shipments.total_cartons` is zero, the e-way bill's mandatory
package count cannot be supplied, the consignment note cannot be raised, and `FR-206`'s weight-dispute
evidence — which the set says cannot be created afterwards — is never captured. Everything downstream
of pack in journey 3 is designed and unreachable.

---

## §2 · The ten walks

Legend: **✔** the three ids resolve and the step is executable · **⚠** executable but with a stated
or discovered hole · **✖** no surface exists.

### Walk 1 · Day 0 — empty database to first posted receipt

| # | Step | Actor | Screen | Requirement | Scenario | Verdict |
|---|---|---|---|---|---|---|
| 1 | Company, branch, warehouse, site | implementer | WS-001…WS-010 (site/zone/location masters) | `FR-079` `FR-080` | `WH-SC-279` | ✔ |
| 2 | Zones and a bin grid | implementer | WS-011 bin-grid generator | `FR-218` | — | ✔ (mobile `none`, reasoned, `p1-06.md:44`) |
| 3 | UoM and conversions | implementer | UoM masters | `FR-074` `FR-075` | — | ✔ |
| 4 | Item master import | implementer | platform 6-stage wizard | `FR-418` | — | ✔ |
| 5 | Opening stock: stage → validate → dry run → apply | `mgr1` | **WS-150** Opening Stock Batches (v1) | `FR-411` `FR-249` | **`WH-SC-049`** `WH-SC-193` | ✔ |
| 6 | Valuation of opening stock, first cost layer | system | — | `FR-249` `FR-234` | `WH-SC-049` | ✔ |
| 7 | Tie-out against the source figure, reconciliation certificate | controller | **WS-151** Cut-over Checklists (v1) | `FR-412` `FR-413` | **`WH-SC-050`** | ✔ |
| 8 | Users, roles, permissions | admin | platform | `FR-404` `FR-114` | — | ✔ |
| 9 | Printers | implementer | WS-133 (**v1.1**) | `FR-224` | — | ✔ — *stated* deferral: v1 is template + renderer + browser download, v1.1 is the print server and printer registry (`FR-224`). See `U-006` for the one loose end. |
| 10 | Numbering series | implementer | numbering masters | `FR-426` | `WH-SC-233` | ✔ |
| 11 | Catalogues seeded (13 open vocabularies) | migration | — | `D-10` | `WH-SC-292` | ✔ |
| 12 | First login, period opened, first receipt | storekeeper | WS-076 | `FR-126` `FR-251` | `WH-SC-050` | ✔ |

**Walk 1 completes.** This is the strongest journey in the set and the one most design sets skip.

### Walk 2 · A storekeeper's day (inbound)

| # | Step | Actor | Screen | Requirement | Scenario | Verdict |
|---|---|---|---|---|---|---|
| 1 | Vehicle arrives, driver checks in, `arrived_at` stamped | gate clerk | **WS-086 is v1.1; mobile `whDockAppointment` check-in is v1.1** | `FR-092` (schema v1) | `WH-SC-274` | ✖ **`U-004`** |
| 2 | Dock assigned, `docked_at` | supervisor | WS-086 (v1.1) | `FR-092` | `WH-SC-274` | ✖ same |
| 3 | Unload | operator | WS-230 RF Putaway / WS-076 | `FR-126` | — | ✔ |
| 4 | Count and verify | storekeeper | WS-076 receiving | `FR-127` `FR-128` | — | ✔ |
| 5 | GRN against the purchase document | storekeeper | WS-076 | `FR-126` `FR-130` | `WH-SC-081` | ✔ |
| 6 | Receipt lands in a non-available status | system | — | `FR-129` | — | ✔ |
| 7 | QC sampling, inspection, hold | inspector | **WS-080** + mobile `whQualityInspection` | `FR-133` `FR-134` | — | ✔ |
| 8 | Disposition (release / reject / RTV / scrap), QA-gated | QA | WS-080 | `FR-134` | — | ✔ |
| 9 | Putaway suggestion | system | WS-081 rules | `FR-135` | — | ✔ |
| 10 | Putaway confirm, override reason captured | operator | **WS-230 RF Putaway** | `FR-135` | — | ✔ |
| 11 | Discrepancy: short / over / damaged | storekeeper | WS-076 (`match_status`) | `FR-130` | `WH-SC-084` | ✔ |
| 12 | A reconciliation case opens and is **assigned** | system → supervisor | WS-083 | `FR-138` | `WH-SC-084` | ✔ |
| 13 | **Who is told** | — | NONE | NONE in v1 | NONE | ✖ **`U-002`** — the case has an owner column and an Assign action, and no channel reaches that owner in v1 |
| 14 | Effect on the purchase document (close short, reverse, cancel cascade) | buyer | WS-076 / WS-078 | `FR-130` `FR-131` `FR-132` | `WH-SC-081` `WH-SC-082` | ✔ |

**Walk 2 completes physically, but blind at both ends**: no arrival time, and no one is notified of
the exception.

### Walk 3 · An order's whole life (outbound) — **the journey that breaks**

| # | Step | Actor | Screen | Requirement | Scenario | Verdict |
|---|---|---|---|---|---|---|
| 1 | Order arrives through the movement port | vertical adapter | — | `FR-041` `FR-349` | `WH-SC-216` `WH-SC-217` | ✔ |
| 2 | Order keyed by hand | CSR | **WS-099** Add (multi-tab modal) | `FR-177` | — | ✔ |
| 3 | Credit / stock check → order hold | CSR | WS-099 Place hold | `FR-182` | — | ✔ |
| 4 | Allocation | CSR / system | WS-099 Allocate | `FR-169` `FR-174` | — | ✔ |
| 5 | Wave build | supervisor | WS-101 (**v1.1**) | `FR-187` | — | ✔ *stated deferral* — v1 releases on the demand header |
| 6 | Release | supervisor | WS-099 Release | `FR-169` `FR-187` | — | ✔ |
| 7 | Pick list printed | supervisor | WS-131/132, kind `PICK_LIST` | `FR-225` | `WH-SC-203` | ✔ |
| 8 | Pick | picker | **WS-232 RF Pick** / WS-102 | `FR-186` `FR-192` | — | ✔ |
| 9 | Short pick, exception-coded, replenishment triggered | picker | WS-102 Short pick | `FR-185` | — | ✔ |
| 9b | …and **who is told** about the short | — | WS-153 is **v1.1** | `FR-216` **v1.1** | NONE | ✖ **`U-002`** |
| 10 | Pick moves stock to a countable staging location | system | — | `FR-188` | — | ✔ |
| 11 | **Pack — create a carton, scan into it, seal it** | packer | **NONE in v1.** WS-103 is v1.1; WS-104 (v1) has *View contents · View evidence · Print · Reprint* only | `FR-190` **v1.1** | NONE | ✖ **`U-001` — the break** |
| 12 | Weigh, photograph, capture scale reading | packer | **NONE in v1** | `FR-206` says *v1, and cannot be created retroactively* | `WH-SC-106` | ✖ **`U-001`** |
| 13 | Carton label | packer | WS-104 Print carton label | `FR-225` | — | ✔ *(prints a carton that cannot exist)* |
| 14 | Manifest | dispatcher | WS-110 (**v1.1**) | `FR-194` | — | ✔ *stated deferral* |
| 15 | Gate pass (e-way-bill-conditional) | gate clerk | no v1 host screen | `FR-195` | `WH-SC-210` `WH-SC-211` | ⚠ already `X-027` |
| 16 | Dispatch — the inventory-relief event | dispatcher | WS-105 **Dispatch** | `FR-189` | — | ✔ |
| 17 | Seal number at load | dispatcher | — | `FR-211` **v1.1** | — | ⚠ already `X-015` |
| 18 | **ePOD / delivery confirmation** | driver / CSR | **NONE** until `logistics` at **v3·P6** | NONE | NONE | ✖ **`U-005`** — yet `deliveredAt` is a **v1 grid column** on WS-105 |
| 19 | Order reaches a terminal state | system | NONE | NONE | NONE | ✖ **`U-005`** |
| 20 | Handover to invoicing (the **stock** leg, valued) | system | — | `FR-233` `FR-232` | — | ✔ |

### Walk 4 · A stock controller's month

| # | Step | Actor | Screen | Requirement | Scenario | Verdict |
|---|---|---|---|---|---|---|
| 1 | Cycle-count programme scoped by ABC class | controller | WS-093 count programmes | `FR-156` | `WH-SC-268` | ✔ |
| 2 | Schedule generates count tasks | system | `whb_tasks` | `FR-156` | — | ✔ |
| 3 | Count sheet / blind count | counter | **WS-231 RF Cycle Count** | `FR-154` | — | ✔ |
| 4 | Recount above threshold | counter | WS-094 | `FR-154` | — | ✔ |
| 5 | Variance review; tolerance gates posting | controller | WS-094 | `FR-155` | — | ✔ |
| 6 | Approval above threshold | warehouse manager | WS-094 | `FR-155` | — | ✔ |
| 7 | Adjustment posts as a movement | system | WS-089 | `FR-155` | — | ✔ |
| 8 | Stock period soft-close | controller | WS-060 stock periods | `FR-251` | `WH-SC-021` | ✔ |
| 9 | Valuation run | controller | valuation report | `FR-235` `FR-237` | — | ✔ |
| 10 | Reconcile position ↔ ledger ↔ valuation | controller | nightly rebuild + exception table | `FR-012` | — | ✔ |
| 10b | …**drift alerts on** | — | NONE in v1 | `FR-012` **P0** says "alerts on drift" | NONE | ✖ **`U-002`** |
| 11 | Stock-to-GL reconciliation | finance controller | WS-166 | **`FR-247`** | — | ✔ |
| 12 | Rejected-handover queue worked | finance controller | handover queue | `FR-232` | — | ✔ |
| 12b | …with **an alert**, as `FR-232` (P0) requires | — | NONE in v1 | `FR-232` | NONE | ✖ **`U-002`** |
| 13 | Handover to accounting | system | — | `FR-233` `FR-248` | — | ✔ |
| 14 | Period hard-close, synchronised with accounting's lock | controller | WS-060 | `FR-251` | `WH-SC-021` | ✔ |

**Walk 4 completes.** The accounting seam is the best-argued part of the set.

### Walk 5 · A branch-to-branch transfer

| # | Step | Actor | Screen | Requirement | Scenario | Verdict |
|---|---|---|---|---|---|---|
| 1 | Request | branch storekeeper | WS-099 (`demand_type` = transfer) | `FR-177` `FR-147` | — | ✔ |
| 2 | Approval | manager | WS-099 Release | `FR-182` | — | ✔ |
| 3 | Pick | picker | WS-232 / WS-102 | `FR-186` | — | ✔ |
| 4 | Pack into cartons | packer | **NONE in v1** | `FR-190` v1.1 | NONE | ✖ **`U-001`** |
| 5 | Delivery challan, own per-branch series | dispatcher | WS-18x (india) | **`FR-307`** | — | ✔ |
| 6 | E-way bill Part-A / Part-B | dispatcher | india screens | `FR-308` `FR-309` | `WH-SC-214` | ✔ (package count blocked by step 4) |
| 7 | Depart into a per-transfer in-transit location | system | — | **`FR-147`** | — | ✔ |
| 8 | In-transit stock is countable, ageable, attributable | controller | WS-149 ageing | `FR-149` `FR-335` | — | ✔ |
| 9 | Arrival at destination | receiver | WS-076 | `FR-147` | — | ✔ |
| 10 | Receipt; the third leg posts | receiver | WS-076 | `FR-147` | — | ✔ |
| 11 | **Shortage found in transit — who owns the loss** | controller | WS-083 case | **`FR-148`** (the sender bears the risk and holds the stock until receipt) `FR-335` | — | ✔ — *explicitly answered* |
| 12 | Transfer carries two numbers (transfer price and cost) | system | — | `FR-244` | — | ✔ |

### Walk 6 · Returns, both directions

| # | Step | Actor | Screen | Requirement | Scenario | Verdict |
|---|---|---|---|---|---|---|
| 1 | Customer return authorised (RMA **optional**) | CSR | WS-14x | **`FR-269`** | — | ✔ |
| 2 | Blind return received with no RMA | storekeeper | WS-076 blind receipt | `FR-128` `FR-269` | — | ✔ |
| 3 | `return_type` recorded day one | system | — | `FR-270` | — | ✔ |
| 4 | Inspection | inspector | WS-080 | `FR-133` | — | ✔ |
| 5 | Disposition restock / quarantine / scrap | QA | disposition registry | **`FR-273`** (v1 ships the three that close the loop) | — | ✔ |
| 6 | Credit handover | — | **deliberately none** | **`FR-274`** — "no refund screen, no refund amount and no payment path in any warehouse module in any version" | — | ✔ *decided, not missing* |
| 7 | Return to vendor raised | buyer | WS-084 | `FR-139` `FR-275` | — | ✔ |
| 8 | Pick and dispatch; stock relieved **only at dispatch** | dispatcher | WS-084 Dispatch | `FR-139` | — | ✔ |
| 9 | Debit-note proposal | — | v2 (`P5`) | `FR-275` | — | ✔ *stated deferral* |

**Walk 6 completes**, and its money boundary is the cleanest in the set — which is exactly why
`U-003` is a defect rather than a matter of taste.

### Walk 7 · The two v1 adapters

| # | Step | Actor | Screen | Requirement | Scenario | Verdict |
|---|---|---|---|---|---|---|
| 1 | Workshop parts request against a job | service advisor | vertical screen | `FR-357` | `WH-SC-217` | ✔ |
| 2 | Reserve | system | port | `FR-169` `FR-349` | `WH-SC-217` | ✔ |
| 3 | Issue to the job | storekeeper | port → ledger | `FR-349` | `WH-SC-217` | ✔ |
| 4 | Job cancelled; part returns to store, job credited | storekeeper | port | `FR-349` | **`WH-SC-220`** | ✔ |
| 5 | Counter sale keyed, keyboard-first | counter clerk | **WS-194** | `FR-358` `FR-359` | `WH-SC-216` | ✔ |
| 6 | Price applied from a trade price level | system | WS-194 | `FR-359` | `WH-SC-216` — *"the price is on the adapter's document; it never enters the port"* | ✔ |
| 7 | Stock issued through the port | system | — | `FR-041` `FR-349` | `WH-SC-216` | ✔ |
| 8 | **`tax_amount` computed** | system | WS-194 column | **contradicts `OD-9`** | NONE | ✖ **`U-003`** |
| 9 | **`payment_mode` captured — money taken** | counter clerk | WS-194 column | **contradicts `FR-274`** | NONE | ✖ **`U-003`** |
| 10 | Cash ticket printed | counter clerk | WS-131/132 | `FR-359` `FR-225` | NONE | ⚠ prints a document that is a tax invoice in India |
| 11 | **Handover of the receivable / the day's takings** | — | NONE | NONE | NONE | ✖ **`U-003`** |
| 12 | Counter return reverses stock **and** money | counter clerk | `COUNTER_RETURN` movement type | `FR-349` (stock only) | — | ⚠ stock reverses, money does not |

### Walk 8 · A supervisor's morning (08:00)

| # | What the supervisor needs to see | Screen | Requirement | Verdict |
|---|---|---|---|---|
| 1 | Exceptions in one place | **WS-153 Supervisor Exception Console** | `FR-216` | ✖ **v1.1** |
| 2 | Stuck / unassigned tasks | WS-154 Task Assignment Board | `FR-215` | ✖ **v1.1** |
| 3 | Unallocated / late orders | WS-099 filters `lateOnly`, `onHoldOnly` + statistics strip | `FR-180` `FR-182` | ✔ |
| 4 | Held QC | WS-080 filter `result` | `FR-133` | ✔ |
| 5 | Expiring stock | near-expiry report | `FR-160` | ✔ report ✖ notification |
| 6 | Negative-available attempts | WS-097 / blocked-move queue | `FR-028` `L-6` | ✔ |
| 7 | Yesterday's count variances | WS-094 + variance register | `FR-390` | ✔ |
| 8 | **L-4 rebuild drift alert** | reconciliation-exception table | `FR-012` **P0** | ✔ table ✖ alert |
| 9 | Interface error queue non-empty | WS-06x | `FR-045` | ✔ grid ✖ alert |
| 10 | Operations dashboard | WS-228 | `FR-394` | ✖ **v3** |

**Walk 8 is the worst-served journey in v1.** The supervisor has seven grids and must know to open
each of them, on the right filter, every morning; nothing arrives. Findings `U-002` (no channel) and
the deliberate v1.1 placement of `FR-216` compound: the set has a console *and* an alert engine, and
in v1 it has neither.

### Walk 9 · A 3PL client's month (v2)

| # | Step | Screen | Requirement | Scenario | Verdict |
|---|---|---|---|---|---|
| 1 | Client onboarded from a template, own number series | WS-15x | `FR-282` `FR-283` | `WH-SC-233` | ✔ |
| 2 | Receive on behalf of an owner; non-own stock never valued | WS-076 | `FR-112` `L-14` | — | ✔ |
| 3 | Store; daily storage snapshots persisted | — | `FR-288` `FR-289` | — | ✔ |
| 4 | Ship on the client's carrier account (`owner_id` nullable) | WS-105 | `FR-196` | — | ✔ |
| 5 | Billable events metered, append-only and reversible | WS-16x | `FR-285` | — | ✔ |
| 6 | Accessorials, incl. detention auto-captured from the dock appointment | WS-16x | `FR-291` | — | ⚠ depends on `arrived_at`, see `U-004` |
| 7 | Minimum monthly true-up | — | `FR-290` | — | ✔ |
| 8 | Billing run rated, approved, frozen | WS-163 | `FR-292` | — | ✔ |
| 9 | **One AR document envelope to accounting; no invoice here** | — | **`FR-294`** | — | ✔ |
| 10 | Client portal: stock, inbound, outbound, billing, disputes, performance | **WS-172** | `FR-284` `FR-298` `FR-300` | — | ✔ |
| 11 | Row-level owner segregation with a negative test per endpoint | — | `FR-300` | — | ✔ |

### Walk 10 · An India compliance officer's month (v2)

| # | Step | Requirement | Verdict |
|---|---|---|---|
| 1 | Rule 56 stock account | §7 register set, v2 (`A-4`) | ✔ |
| 2 | Job work and ITC-04 | `FR-307` (challan) + register set | ✔ |
| 3 | Delivery challan series per branch | `FR-307` | ✔ |
| 4 | E-way bill lifecycle, not just the number | `FR-309` | ✔ |
| 5 | Deemed supply between GSTINs | `FR-305` `FR-306` | ✔ |
| 6 | Inter-state transfer invoice needs an IRN | `FR-311` + `WH-SC-214` | ✔ *honest boundary, stated* |
| 7 | MRP / Legal Metrology | `FR-321` (gated on `OD-10`) | ⚠ open decision, already tracked |
| 8 | Tax computed by accounting or the provider, never here | **`OD-9`** | ✖ **contradicted in v1 by `U-003`** |

---

## §3 · The findings

### `U-001` · No carton can be created in v1: the only screen with a create/seal action is v1.1, and `P2-11` closes the gap with an action that exists in no screen contract — **BLOCKER**

- **What is missing or wrong:** `WS-104 Cartons` ships **v1 · P2** with the action list
  *View contents · View evidence · Print carton label · Reprint* — every one of them read-only.
  `WS-103 Pack Sessions`, whose actions are *Start (auto-creates the first carton) · Add carton ·
  Close carton · Complete*, ships **v1.1 · P3** (`FR-190`). `WS-105 Shipments` (v1) has
  *Add · Assign carrier · Rate shop (v2) · Dispatch · Print shipping label · Add to manifest ·
  Cancel* — no carton affordance. `issues/p2-11.md:44-50` resolves this in prose — *"v1 creates
  cartons from the shipment screen"* and *"in v1 the capture is on the web pack action"* — but no
  such action is specified on `WS-105`, on `WS-104`, or anywhere else in `BUILD-SPEC-SCREENS.md`.
  `P2-11` therefore names `WS-104` as its only screen and closes `FR-206`, and cannot.
- **Why it matters:** the moment is the first afternoon of the first pilot. A picker has moved stock
  to staging (`FR-188`); the packer has nothing to open. `FR-191` makes cartons **mandatory** and
  enumerates six reasons — you scan cartons not items; the consignment note has a mandatory
  package-count field; **the e-way bill requires package count and description**; a carton rides
  exactly one truck; damage claims are per handling unit; 3PL handover manifests are carton-based.
  All six fail. `wh_shipments.total_cartons` is 0, so the e-way bill (`P2-IN-04`) cannot be filed for
  any outbound consignment, and `FR-195`'s gate pass — which *blocks* where an e-way bill is legally
  required and not yet generated — refuses every dispatch. Worse, `FR-206` states that the pack photo
  and scale weight are captured at pack time **in v1** *"because the evidence for a carrier
  weight-discrepancy dispute cannot be created after the dispute"*; `P2-11` repeats it as *"the
  evidence is v1 or it does not exist"*. With no v1 capture surface it does not exist, permanently,
  for every shipment a v1 install makes.
- **Negative evidence:**
  ```bash
  grep -rn "Add carton\|Create carton\|New carton\|Seal carton" docs/BUILD-SPEC-SCREENS.md \
    | grep -c "WS-104\|WS-105"                    # → 0
  grep -rn "Add carton" docs/ issues/ | grep -v reviews/
  # → docs/BUILD-SPEC-SCREENS.md:1507  (WS-103, "v1.1")
  # → issues/p3-07.md:38               (P3-07, phase P3)
  grep -rn "pack action" docs/ issues/ | grep -v reviews/
  # → issues/p2-11.md:50   — the only occurrence in the set; defined nowhere
  grep -rniE "pack session|wh_cartons|carton" docs/DESIGN-SET-DEFECTS.md docs/GAP-REGISTER.md
  # → (no output) — neither the defect register nor the gap register mentions cartons at all
  ```
- **Where it belongs:** `warehouse` · **v1** · **P2**
- **Disposition:** *fold into task `P2-11`.* Add to its **Screens** line and its `WS-104` block:
  *"`WS-104` carries **Create carton** (against a shipment, allocating `carton_number` and `lpn_code`),
  **Add contents** (scan into `wh_carton_contents` to the serial), **Capture evidence** (pack photo +
  `scale_weight_kg`, `FR-206`) and **Seal**; `WS-105` carries **Cartons** as a row action opening the
  scoped `WS-104` list. The one-active-carton operator flow (`FR-190`) remains `P3-07`; v1 is the
  desk-grade equivalent, not the absence of the capability."* Add the same four actions to `WS-104`'s
  block in `BUILD-SPEC-SCREENS.md` and to its permission list (`wh_cartons:create` `:seal`
  `:capture_evidence`, each `→ :view`).
- **Irreversibility:** the *schema* is fine — `wh_cartons`, `wh_carton_contents` and
  `wh_carton_evidence` are already `V510042`. The **evidence** is irreversible by the set's own
  argument (`FR-206`): every carton shipped before the capture action exists has no photo and no scale
  weight, and that cannot be backfilled. No migration change is needed; the deadline is the first v1
  dispatch.
- **Relationship to round 1:** **new.** `P-037` and `F-038` argued the carton *object* into v1 and
  `F-047` argued the *evidence* into v1; both were accepted (`A-2`-era ladder work) and neither
  checked that a v1 screen could produce either.

---

### `U-002` · In v1 nothing tells anyone anything: the alert rule / recipient / event substrate is v1.1 while six v1 requirements — two of them P0 — mandate a notification with configured recipients — **BLOCKER**

- **What is missing or wrong:** `whb_alert_rules`, `whb_alert_rule_conditions`,
  `whb_alert_rule_recipients` and `whb_alert_events` are all marked **v1.1**
  (`DATA-MODEL.md:920-923`), land in `V500063` under **`P3-16`** (`issues/p3-16.md:4,8`), and their
  screens `WS-069`/`WS-070` are **v1.1 · P3** (`BUILD-SPEC-SCREENS.md:321-322`). Six requirements
  scheduled **v1** each require a notification, and each names *recipients* as configuration:
  - `FR-012` (base · **v1 · P0**) — the nightly rebuild *"writes findings to a reconciliation-exception table and **alerts on drift** (`L-4`)"*
  - `FR-232` (base · **v1 · P0**) — *"a **rejected-handover queue has an owner and an alert**"*
  - `FR-045` (base · v1 · P2) — *"an **alert** when the queue is non-empty beyond a threshold"*
  - `FR-160` (app · v1 · P2) — *"raises a **notification** at `expiry − near_expiry_days` … ships with its job, **its recipients** and its report **or not at all**"*
  - `FR-165` (base·app · **v1 · P0**) — *"Every dated obligation … ships with its job, **its notification recipients** and its report, in the same task"*
  - `FR-170` (app · v1 · P2) — *"a scheduled job releases them, **notifies the holder**"*

  `issues/p2-05.md` (the expiry task, P2) carries the acceptance line *"A notification fires at
  expiry − near_expiry_days to a named recipient set, and **the recipients are configuration, not
  code**"* — unsatisfiable with no recipient table until P3. The supervisor's fallback, the exception
  console `FR-216`/`WS-153`, is **also v1.1**.
- **Why it matters:** the moment is 08:00 on any day of a v1 install. The reconciliation-exception
  table has a drift row from last night's `L-4` rebuild — the single most important integrity signal
  in the product — and it sits there. The rejected-handover queue has three envelopes accounting
  refused; the finance controller finds out at month end. A reservation expired and the holder was
  not notified. A lot crosses `near_expiry_days` and nobody is told, which is the exact failure
  `FR-160` was written to prevent. `FR-165` is not advisory: it says a threshold column with no job
  reading it *"is a defect at the moment it is merged"* — and the v1 plan merges nine of them. The
  platform substrate is present and usable (`notifications` @ `V319`, `NotificationDeliveryListener`
  @ `platform/…/listener/NotificationDeliveryListener.java:39`, per
  `PLATFORM-DEPENDENCIES.md` §1 row 1.9), so this is a phase-placement defect, not a missing
  capability: a v1 build would either hardcode recipients (violating `FR-165` and `p2-05`'s
  acceptance) or ship the alerts silently disabled.
- **Negative evidence:**
  ```bash
  sed -n '920,923p' docs/DATA-MODEL.md | grep -o 'v1\.1' | wc -l        # → 4  (all four tables v1.1)
  grep -n "^| WS-069\|^| WS-070" docs/BUILD-SPEC-SCREENS.md
  # → 321: WS-069 Alert Rules   … v1.1 · P3
  # → 322: WS-070 Alert Events  … v1.1 · P3
  grep -rn "whb_alert_rules" issues/*.md | cut -d: -f1 | sort -u        # → issues/p3-16.md
  grep -rniE "alert_rules|recipients are configuration" docs/GAP-REGISTER.md docs/DESIGN-SET-DEFECTS.md
  # → (no output)
  ```
- **Where it belongs:** `warehouse-base` · **v1** · **P2** (the four tables and `WS-069`/`WS-070`);
  the console `FR-216`/`WS-153` may stay v1.1 **only if** the alert substrate moves.
- **Disposition:** *fold into task `P3-16`, moving it to P2.* `V500063` already sorts after
  `PNR-1`/`V500030`, so the migration number does not change — only the phase does. Add to `P3-16`
  (renamed `P2-30` or re-phased in place): *"Phase **P2**, because `FR-012` and `FR-232` are **P0**
  requirements that name an alert, `FR-165` makes 'a threshold column with no job that reads it' a
  merge-time defect, and `issues/p2-05.md` cannot meet its own acceptance line
  ('the recipients are configuration, not code') without `whb_alert_rule_recipients`. Seed the six v1
  alert types — `LEDGER_REBUILD_DRIFT`, `HANDOVER_REJECTED`, `INTERFACE_QUEUE_BACKLOG`,
  `LOT_NEAR_EXPIRY`, `RESERVATION_EXPIRED`, `RECONCILIATION_CASE_ASSIGNED` — with recipient rows, in
  the same migration."*
- **Irreversibility:** **reversible** as data, but the *events not raised* are unrecoverable: nobody
  learns about a drift row from three weeks ago. No `PNR` implication.
- **Relationship to round 1:** **new.** `T-092` produced the interface error queue and `T-057` the
  console; `R6` #59/#60 catalogued the prior art's `wms_alert_rules` JSONB columns and R2 row 96
  scored gatehouse capability — none of them compared the substrate's version against the six v1
  requirements that consume it.

---

### `U-003` · The v1 counter sale computes tax and takes payment inside a warehouse module — the losing side of `OD-9` and a direct contradiction of `FR-274` — and `OD-9`'s deadline falls after the task that builds it — **BLOCKER**

- **What is missing or wrong:** `whad_counter_sales` (**v1**, `DATA-MODEL.md:1254`, mirrored on
  `WS-194` at `BUILD-SPEC-SCREENS.md:1704`) carries `price_level`, `subtotal`, **`tax_amount`**,
  `total_amount` and **`payment_mode`**. Three documents forbid this:
  - **`OD-9`** (`DECISIONS.md:294`) is **resolved**: *"**Warehouse never computes tax.** It captures
    the tax-relevant facts (HSN, place of supply, `is_taxable_supply` frozen at creation, taxable
    value) and hands them over; accounting or the compliance provider computes."*
  - **`FR-274`** (v1): *"There is **no refund screen, no refund amount and no payment path in any
    warehouse module in any version**. A refund is a receivable event with tax consequences and it
    belongs where the receivable lives."* `payment_mode` on a sale is the same seam in the same
    module in the opposite direction.
  - **`FR-294`** is the set's only AR-document envelope — and it is `warehouse-3pl`, **v2 · P5**.
    `INDIA-LOCALISATION-PACK.md:602-614` states the rule for transfers only (*"Warehouse holds the
    **stock** side and the challan; **it never numbers a tax invoice**"*) and says nothing about the
    counter sale.

  There is no requirement, screen, envelope or scenario anywhere that carries the counter sale's
  money leg to accounting. `WH-SC-216`'s "Then" says only *"the price is on the adapter's document; it
  never enters the port"* — true, and the document it stays on goes nowhere. Separately: `OD-9`'s
  stated deadline is *"Before `P2-IN`"*, but `whad_counter_sales` is built by **`P2-25`**, in phase
  **P2** — the decision is due **after** the code that depends on it.
- **Why it matters:** the moment is the first counter transaction at a dealer parts desk. A walk-in
  pays cash; `FR-359` prints *"a cash ticket"*. In India that ticket is a tax invoice: it needs a
  GSTIN, an HSN, a place of supply, a per-branch invoice series and — above the threshold — an IRN.
  Warehouse has computed `tax_amount` with no tax engine (`FR-325`, the relational engine, is
  **v2 · P4** and India-scoped), has taken money with no receivable, and has no day-end takings
  reconciliation:
  `grep -rniE "cash drawer|till|day.end|receivable|remittance" issues/p2-25.md` → **0 matches**.
  The dealer's accountant reconciles the parts counter by hand from a printout, forever, and the
  first GST audit asks who numbered the document. If `OD-9` is honoured instead, the three columns
  must be deleted from a shipped table.
- **Negative evidence:**
  ```bash
  grep -n "OD-9" docs/DECISIONS.md            # → 294: "Warehouse never computes tax."
  grep -n "tax_amount" docs/DATA-MODEL.md | grep whad_counter_sales   # → 1254
  grep -rniE "cash drawer|till|day.end|receivable|remittance|accounting handover" issues/p2-25.md | wc -l   # → 0
  grep -rniE "counter.?sale|whad_counter|tax_amount|cash ticket" docs/GAP-REGISTER.md docs/DESIGN-SET-DEFECTS.md
  # → GAP-REGISTER.md:1131 only — a coverage row for S-063, not the tax/money seam
  ```
- **Where it belongs:** `warehouse-adapter-dealer` · **v1** · **P2** — and the decision itself is
  `DECISIONS.md`.
- **Disposition:** *is an `OD-` decision, not a task* — **`OD-9`'s deadline must move from
  "Before `P2-IN`" to "Before `P2-25`"**, and its resolution text must name the counter sale
  explicitly. Then *fold into `P2-25`*, adding: *"`whad_counter_sales` carries the **tax-relevant
  facts** (`hsn_code`, `place_of_supply`, `is_taxable_supply`, `taxable_value`) and **not**
  `tax_amount` or `total_amount`; `payment_mode` is captured as a **fact about the vertical's
  document**, not as a payment path, and the sale emits **one AR source-document envelope** through
  accounting's port on the `FR-233` shape, with `document_kind = COUNTER_SALE`. Warehouse numbers no
  invoice and holds no receivable (`OD-9`, `FR-274`). Where no accounting module is installed
  (Modes A/B), the adapter emits nothing and the vertical's own billing owns the ticket — state which,
  do not leave it to the implementer."*
- **Irreversibility:** the columns ride `V520100`–`V520149` (`p2-25.md`), well above `PNR-1`. Adding
  the four fact columns is reversible; **shipping `tax_amount` and then removing it is not**, because
  a v1 install will have posted values into it. The decision must land **before** `P2-25` merges.
- **Relationship to round 1:** materially extends **`E-065`** (R3, BLOCKER — which asked for the
  counter sale and the cash ticket) and **`X-049`** (which records that `OD-9` is missing from the
  FRD's §9 gate table). What is new: `E-065` predates `OD-9`, and nobody re-read the table it produced
  against the decision that followed it — so a v1 table implements the option `OD-9` rejected, and
  `OD-9`'s own deadline is later than the task that depends on it.

---

### `U-004` · `wh_dock_appointments.arrived_at` was pulled into v1 *because it cannot be backfilled*, and has no v1 writer on any surface — **MAJOR**

- **What is missing or wrong:** `FR-092` places the dock-appointment **schema** in v1 with
  `arrived_at`, `docked_at`, `departed_at`, `no_show` and `detention_minutes`, *"and the screens land
  in v1.1"*. `WS-086`'s block confirms the Check-in action and annotates it
  *"`arrived_at` — the dock-to-stock clock starts here and **cannot be backfilled**"*, then states
  *"Schema is v1 (`V510010`); the scheduling screen is v1.1"*. The mobile counterpart is explicitly
  v1.1 too: `issues/p1-06.md:44` — *"**check-in** lands on `screens/whDockAppointment` in **v1.1**"*.
  So no surface, web or handheld, can write `arrived_at` in v1. `WH-SC-274`'s "Then" asserts the
  opposite outcome: *"a v1 install has the history the v1.1 screens will display, and month two of
  the first client can answer for month one."*
- **Why it matters:** the moment is the first client QBR. Dock-to-stock is one of ten dashboard
  widgets (`BUILD-SPEC-SCREENS.md:1843`, *"Impossible without `arrived_at`, which is why the dock
  schema is v1"*) and reads `wh_dock_appointments.arrived_at` → putaway completion. For every install
  that runs v1 before v1.1, that widget and the whole detention clock have no history and never will,
  which is precisely the outcome the schema was pulled forward to prevent. It also degrades walk 9
  step 6: `FR-291`'s auto-captured detention accessorial has no source, so a 3PL bills detention by
  hand for its first release.
- **Negative evidence:**
  ```bash
  grep -n "WS-086" docs/BUILD-SPEC-SCREENS.md | head -2
  # → 338: | WS-086 | Dock Appointments | app | … | v1.1 · P3 |
  grep -rn "whDockAppointment" docs/ issues/ | grep -v reviews/
  # → docs/BUILD-SPEC-SCREENS.md:1373  (mobile, "check-in only" — under the v1.1 §3.1 block)
  # → issues/p1-06.md:44               ("check-in lands on screens/whDockAppointment in v1.1")
  # → issues/p3-05.md:37               (P3)
  grep -rn "arrived_at" issues/*.md | grep -v p3-05 | wc -l     # → 0 outside the P3 task
  ```
- **Where it belongs:** `warehouse` · **v1** · **P1** (a check-in surface only; the scheduling grid
  may stay v1.1)
- **Disposition:** *fold into task `P1-06`* (which already owns the dock schema and states the mobile
  `none` decisions). Replace its line 44 note with: *"**Check-in is v1, not v1.1.** `arrived_at`
  cannot be backfilled and `WH-SC-274` asserts a v1 install has the history; ship a minimal v1
  check-in surface — the mobile `screens/whDockAppointment` check-in screen (`FR-092`, `D-13`) plus a
  **Check in / Dock / Depart / Mark no-show** action set on the inbound receiving screen `WS-076`
  against an auto-created walk-in appointment. The **scheduling** grid `WS-086` stays v1.1."*
- **Irreversibility:** **irreversible as data.** Every arrival before the writer exists has no time,
  by the set's own statement. No new migration — `V510010` already carries the columns.
- **Relationship to round 1:** materially extends **`G-015`** (R7 §, `R7-logistics-supply-chain-seam.md:873-878`),
  which won the argument to move the *schema* to v1 and wrote *"the **screen** stays v2"*. What is
  new: with the screen deferred, the v1 columns have no writer at all, so the benefit `G-015` was
  granted — a v1 install accumulating arrival history — is not obtained, and `WH-SC-274`'s "Then"
  clause is unachievable as written.

---

### `U-005` · The outbound journey has no closing event in v1: `delivered_at`, `pod_document_id` and the `deliveredAt` grid column exist in v1 and nothing writes them until v3 — **MAJOR**

- **What is missing or wrong:** `wh_shipments` (**v1**) carries `delivered_at` and `pod_document_id`;
  `wh_demand_orders` (**v1**) carries `delivered_at` and `promised_deliver_at`; `WS-105`'s **v1** grid
  shows `deliveredAt` as a visible column. No v1 action writes any of them: `WS-105`'s action list ends
  at *Dispatch · Print shipping label · Add to manifest · Cancel*, and `WS-099`'s statistics strip ends
  at *shipped today*. The only proof-of-delivery capability in the set is the **reserved permission**
  `logistics:epod:view|capture`, which belongs to the `logistics` module at **v3 · P6** (`P6-08`).
  Carrier tracking events, the other possible writer, are `FR-198` — **v2**.
- **Why it matters:** the moment is the second week of the first pilot. A CSR opens Shipments, sorts
  by Delivered, and every cell is blank forever — the failure mode the set itself names in
  `WH-SC-268` (*"a classification stored and never consumed is a defect the prior product shipped"*),
  here in its mirror image: consumed on screen, never produced. The order has no terminal state, so
  "how many orders are still out?" is unanswerable and `promised_deliver_at` — a v1 column
  (`FR-180`) — can never be measured against anything, while `promised_ship_at` can. It also silently
  constrains `FR-243` (COGS at *dispatch, delivery or invoice*, v2): two of the three configured
  policies have no event to fire on.
- **Negative evidence:**
  ```bash
  grep -rniE "epod|proof of delivery" docs/ issues/ | grep -v reviews/ | grep -vc "logistics"   # → 0
  # every hit is the v3/P6 logistics module (IMPLEMENTATION-PLAN.md:362,585 · p6-08.md · DECISIONS.md:336)
  grep -rn "delivered_at\|deliveredAt" docs/ issues/ | grep -v reviews/ | wc -l    # → 5
  # 3 schema rows, 1 grid column, 1 note about Object[] type mapping (p2-10.md:86) — no writer
  grep -n "WS-105" docs/BUILD-SPEC-SCREENS.md | grep -c "Mark delivered\|Confirm delivery\|Capture POD"   # → 0
  ```
- **Where it belongs:** `warehouse` · **v1** · **P2** (a manual confirmation only; the driver app,
  signature capture and geo-stamp stay with `logistics` at v3)
- **Disposition:** *needs an `FR-` row first* — one row in §6.11, next free `FR-447`:
  *"**Delivery is confirmed, not inferred.** `WS-105` carries a **Confirm delivery** action in v1
  recording `delivered_at`, a delivery reference and an optional `pod_document_id` through the
  platform's `documents` table, and it cascades to `wh_demand_orders.delivered_at` when every shipment
  on the order is delivered. It is a manual, desk-or-handheld confirmation; the driver-side ePOD with
  signature and geo-stamp is `logistics` at v3 (`P6-08`) and replaces the manual path without
  re-keying. A v1 column with no v1 writer is the defect `WH-SC-268` names."* Then fold the action
  into **`P2-10`** (which already owns `wh_shipments` and its `Object[]` timestamp mapping) and add a
  scenario at the next free id (`WH-SC-306` as of 2026-09-02).
- **Irreversibility:** **reversible.** The columns exist; only the action and one FR row are missing.
  The lost history is real but low-value compared with `U-004`'s.
- **Relationship to round 1:** **new.** `F-030`/`P-038` designed the shipment chain and `F-043`
  deferred tracking events to v2; neither noticed that deferring both writers leaves a v1 grid column
  that can never be non-null.

---

### `U-006` · `WS-132 Print Jobs` ships in v1 with a `printerName` column and a `printerId` filter over `wh_printers`, which is v1.1 — **MINOR**

- **What is missing or wrong:** `FR-224` splits printing cleanly and deliberately — *"v1 ships the
  template object and the renderer … **v1.1 ships the print server**: direct-to-printer from the
  handheld … and a **printer registry**"* — and `WS-133 Printers` is correctly v1.1 · P3
  (`p3-08`). But `WS-132 Print Jobs`, **v1 · P2** (`p2-14`), lists `printerName` among its grid
  columns and `printerId` select among its filters, both sourced from `wh_printers`.
- **Why it matters:** the first v1 print-job grid has a permanently blank column and a filter whose
  dropdown has no rows — the same "blank cell is indistinguishable from a broken one" problem the set
  calls out for widgets (`BUILD-SPEC-SCREENS.md:1857`). Trivial to fix, and it is the same
  v1-column/v1.1-source pattern as `U-004` and `U-005`, which is why it is worth one line.
- **Negative evidence:**
  ```bash
  grep -n "^| WS-13[123]" docs/BUILD-SPEC-SCREENS.md
  # → 383: WS-131 Print Templates … v1 · P2
  # → 384: WS-132 Print Jobs      … v1 · P2
  # → 385: WS-133 Printers        … v1.1 · P3
  sed -n '1557p' docs/BUILD-SPEC-SCREENS.md | grep -o "printerName\|printerId"   # → printerName, printerId
  ```
- **Where it belongs:** `warehouse` · v1 · P2 (documentation of a v1.1 column)
- **Disposition:** *fold into task `P2-14`.* Add: *"`printerName` and the `printerId` filter are
  **v1.1** on `WS-132` — `wh_printers` is `P3-08`. In v1 the print job records the browser download
  and the two are absent from the default grid and filter strip, not present-and-empty."*
- **Irreversibility:** **reversible.**
- **Relationship to round 1:** **new** — a corner of `T-054`/`E-073`/`A-2`'s printing-to-v1 work.

---

## §4 · What I checked and found sound

These are the seams I walked expecting a hole and did not find one. Round 3 should not re-walk them.

| Step / seam | Covered by |
|---|---|
| Day 0 end to end — masters, opening stock as movements, first cost layer, tie-out, cut-over checklist, the period gate | `FR-411` `FR-412` `FR-413` `FR-418` `FR-249` · `WS-150` `WS-151` · `WH-SC-049` `WH-SC-050` `WH-SC-193` |
| 50k-row opening import performance and the conservation-trigger memoisation | `WH-SC-193` (`L-1`, `I-1`) |
| The inbound discrepancy → reconciliation case → resulting document chain, and that the case **never moves stock itself** | `FR-138` · `WS-083` · `WH-SC-084` |
| Over/short receipt tolerance, `match_status`, explicit close-short with a reason | `FR-130` |
| Receipt reversal as an action, blocked once stock has moved on | `FR-131` · `WH-SC-081` `WH-SC-082` |
| PO cancellation as a cascade with a stock gate, refused on an ARRIVED ASN | `FR-132` |
| Short pick as a first-class outcome with an exception code and an auto cycle-count task | `FR-185` · `WS-102` Short pick |
| Pick to a **real, countable** staging location; dispatch as the only relief event | `FR-188` `FR-189` · `WS-105` |
| Wave, manifest/handover/pickup-request, batch pick and scan verification deferred to v1.1 **with the deferral stated on the screen** | `FR-186` `FR-187` `FR-192` `FR-194` · `WS-101` `WS-110` `WS-111` |
| Cycle count: policy object, blind count, recount threshold, tolerance gating, approval, variance register | `FR-154` `FR-155` `FR-156` `FR-390` |
| ABC class populated by the go-live import and **consumed in v1** by the count programme | `WH-SC-268` |
| Stock periods separate from accounting periods, closing earlier, locks synchronised; backdated posting into a closed period | `FR-251` · `WH-SC-021` |
| The whole accounting seam: valued envelopes, no `acc_*` writes, classification quad resolved by accounting, stock-to-GL reconciliation, retryable failure queue | `FR-230`…`FR-233` `FR-246` `FR-247` `FR-248` |
| Transfer as three legs with a per-transfer in-transit location; **who owns the transit loss** is answered explicitly | `FR-147` **`FR-148`** `FR-149` `FR-335` |
| Transfer carries two numbers — transfer price and cost | `FR-244` |
| Returns: the receipt is primary and the RMA optional; blind return representable; `return_type` day one; three dispositions that close the loop | `FR-269` `FR-270` `FR-273` |
| **Warehouse never decides a refund** — no refund screen, amount or payment path, in any version | `FR-274` |
| Return to vendor as ordinary outbound, relieved only at dispatch; debit-note proposal explicitly v2 | `FR-139` `FR-275` |
| Services adapter: reserve → issue → **return to store crediting the job** | `WH-SC-217` `WH-SC-220` |
| The port carries no price, and the counter sale's price stays on the adapter's document | `FR-041` · `WH-SC-216` |
| Printing split: v1 template + renderer + browser download, v1.1 print server + printer registry, **stated** | `FR-224` `FR-225` · `WH-SC-203` |
| Adapter reference data seeded idempotently in its own Flyway sub-band, re-run safe | `WH-SC-292` |
| 3PL month end to end: metered events, storage snapshots persisted, minimum true-up, frozen billing run, **one AR envelope and no invoice in `warehouse-3pl`**, owner segregation at row level, the portal as a permission surface | `FR-285`…`FR-294` `FR-300` · `WS-172` |
| India month: challan series, e-way bill lifecycle (not just the number), deemed supply across GSTINs, and the **honest** v2/P4 IRN boundary stated up front | `FR-305`…`FR-311` · `WH-SC-214` |

---

## §5 · Refused

Candidate findings I deliberately did **not** file.

| Candidate | Why refused |
|---|---|
| "There is no inbound **gate entry** — `grep -i 'gate entry'` returns 0 across the FRD and the screen spec" | Two existing items already own it: `X-015` (`FR-211`, seal/gate/driver/photographs at the receiving session, proved by no scenario) and `X-027` (`FR-195`'s gate pass has no v1 host screen). The *arrival timestamp* half is the only genuinely unowned piece and is filed as `U-004`. |
| "The v1 supervisor has no exception console" | `FR-216`/`WS-153` place it at v1.1 as a **stated** deferral, closing `T-057`. Refiling the version placement would restate round 1. The consequence that matters — that in v1 there is no console **and** no notification channel — is folded into `U-002`, where it is a compound claim round 1 could not have made. |
| "Wave, pack session, manifest, batch pick, scan verification and the print server are all v1.1, so v1 outbound is thin" | Each is a stated deferral written on the screen row itself, and `D-12` makes v1 a cut line rather than the scope limit. Over-engineering to refile. The one that is *not* a legitimate deferral — carton creation, because `FR-191` makes cartons mandatory and `FR-206` makes the evidence uncreatable later — is `U-001`. |
| "`FR-325` still describes a relational tax engine carried forward, after `OD-9` said warehouse never computes tax" | `X-049` already records that `OD-9` is absent from the FRD §9 gate table and that `FR-325` therefore reads as ungated. Filing the same inconsistency again would inflate the register. The part `X-049` does not cover — a **v1 table** implementing the rejected option, with `OD-9`'s deadline falling after the task that builds it — is `U-003`. |
| "`FR-224`/`FR-225` are assigned to no task in `IMPLEMENTATION-PLAN.md` §2" | Already `X-039`. |
| "`WS-238` has no row in the screen index" | Already `X-001` / `R-1`. |
| "No `v3·P6` scenario exists, so the logistics exit criterion is prose" | `issues/00-EPIC-master.md:135` states it and assigns the authoring to `P6-08` as its first act. Decided, not missing. |
| "The counter sale prints a cash ticket that is legally a tax invoice, so the India pack needs a counter-sale invoice series" | The right answer is not to build one — it is `OD-9`'s answer, that warehouse hands the facts over. Folded into `U-003`'s disposition rather than filed as a second finding. Filing it separately would push warehouse toward owning an invoice series, which the set has repeatedly and correctly refused (`FR-274`, `FR-294`, `INDIA-LOCALISATION-PACK.md:602-614`). |
| "The dashboard `WS-228` is v3 so a v1 supervisor has no dashboard" | The ten widgets are specified with their scopes and their empty-state rules, and the platform widget framework already renders them; the *console* gap is the real one and is in `U-002`. |
| "Journeys 9 and 10 are v2, so a v1 3PL or India customer cannot operate" | `DECISIONS.md` §2 modes and `A-4` state exactly this, per deployment mode. Decided. |

---

## §6 · Counts

```bash
grep -cE '^### `U-[0-9]{3}`' docs/reviews/R10-operational-walkthrough.md          # → 6
grep -oE '\*\*(BLOCKER|MAJOR|MINOR)\*\*$' docs/reviews/R10-operational-walkthrough.md | sort | uniq -c
```

| Severity | Count | Findings |
|---|---:|---|
| **BLOCKER** | **3** | `U-001` (no v1 carton) · `U-002` (no v1 notification of anything) · `U-003` (counter-sale tax and money leg) |
| **MAJOR** | **2** | `U-004` (`arrived_at` has no v1 writer) · `U-005` (no v1 delivery confirmation) |
| **MINOR** | **1** | `U-006` (`WS-132` printer column sourced from a v1.1 table) |
| **Total** | **6** | |

**Journeys walked:** 10 · **steps enumerated:** 121 · **steps returning NONE on all three questions:**
9, of which 6 are new findings and 3 are already owned (`X-015`, `X-027`, and the stated `FR-216`
deferral).

**Disposition summary for the caller.** Four of the six fold into existing tasks (`P2-11`, `P1-06`,
`P2-14`, and `P3-16` re-phased to P2). One needs a new FR row (`FR-447`) before it can be a task
line. One is a decision: **`OD-9`'s deadline must move from *"Before `P2-IN`"* to *"Before `P2-25`"***,
and that is the single most time-critical item in this document, because `P2-25` builds the table that
implements the option `OD-9` rejected.
