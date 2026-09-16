# The movement port and adapter contract

> **Current adopted amendment (2026-09-11):** [Global settings and resolved behaviour](GLOBAL-SETTINGS-DECISIONS.md) supplies defaults, scoped choices, resolved OD answers and acceptance cases. Earlier open/escalated or contradictory wording is historical where explicitly superseded there. Implement these answers; do not re-ask the same design questions.


<!-- check-design-set: issue-citations file #2 #9 #790 #791 — `#2` and `#9` are ordinals in prose, not issue references — *Refusal #2*, *Adapter #2 (services)*, *ship-blocker #2*, *logistics needs #1, #2, #3, #5, #6, #10* — and at COMPETITOR-BENCHMARK.md:70/:146 `#9` is the markdown in-page anchor `[§9](#9--where-the-audits-disagree)`. In this repository `#2` and `#9` are in fact the two **pull requests** opened while the backlog was being filed, so no issue row can ever exist for either: see issues/CREATED.md. And `#790` and `#791` are issues in **`neetub1508/classic`**, cited as `classic#790, #791` with the second elided in the ordinary English way. The first resolves; the elided continuation reads to the checker as a bare `#NN`. It is a cross-repo citation, never a warehouse issue -->

> **What this document is for.** The user's requirement is that warehouse serves the dealer module
> now, a logistics/supply-chain module later, and *"if we have more in the future, we should be able
> to do that"*. This is the document that turns that sentence into a **testable claim**. It is read
> by every adapter author, by whoever builds the `logistics` module, and by the reviewer who has to
> decide whether a pull request broke the seam.
>
> **Where it sits in the hierarchy.** [`DECISIONS.md`](DECISIONS.md) wins over this document on every
> question. [`reviews/R1-codebase-reality.md`](reviews/R1-codebase-reality.md) wins on every question
> about what the *existing* `classic` codebase does. This document wins over `reviews/R4` §3–§4 and
> `reviews/R7` §4–§6 on the **wire shape** of the port, because those are lenses and this is the
> ratified contract assembled from them — but every place it moves away from either is stated in the
> row itself, never silently.
>
> **What it is not.** It is not a schema list — [`IRREVERSIBLE.md`](IRREVERSIBLE.md) §4 is, and this
> document cites it rather than restating it. It is not a requirements catalogue —
> [`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md`](WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md) is, and every
> normative clause below cites the `FR-nnn` it implements. It is not an integration runbook —
> [`MODULE-INTEGRATION.md`](MODULE-INTEGRATION.md) is.

| | |
|---|---|
| **Established** | 2026-09-01 |
| **Live codebase read** | `/Users/bbhushan/work/git/workspace/classic`, branch `main` |
| **Sources** | `DECISIONS.md` (`D-1`…`D-14`, `L-1`…`L-14`, `OD-1`…`OD-7`) · round-4 fold `GAP-REGISTER-R4.md` §4.2 (`reviews/R24`–`R26`) · `reviews/R4` §3 + §4 · `reviews/R7` §2, §4, §5, §6 · `IRREVERSIBLE.md` §4, §7 · `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` · `MODULE-INTEGRATION.md` §12, §13 · `reviews/R1` `WF-6` |
| **Method** | reading and `grep` only. No `mvn` / `npm` / `tsc` — this project builds only in Docker (`DECISIONS.md` §7 rule 6). Every count carries the command that produced it |
| **Local id namespace** | **`PC-01` … `PC-75`** — normative clauses of this contract. Confined to this file and to references into it. Not used anywhere else in the set (`DECISIONS.md` §6) |

**How to read a clause.** `PC-nn` is normative: an implementation that violates it is wrong, and
where a build-time test can catch it, §8.4 names the test. Everything not carrying a `PC-nn` is
explanation, and explanation never overrides a clause.

---

## Contents

1. [The one-sentence contract, and the boundary rule](#1--the-one-sentence-contract-and-the-boundary-rule)
2. [The inbound movement port — the wire contract](#2--the-inbound-movement-port--the-wire-contract)
3. [Semantics](#3--semantics)
4. [The outbound side — events](#4--the-outbound-side--events)
5. [The reservation API](#5--the-reservation-api)
6. [The external-reference registries](#6--the-external-reference-registries)
7. [The thirteen open catalogues](#7--the-thirteen-open-catalogues)
8. [The adapter contract](#8--the-adapter-contract)
9. [The concrete consumers, defined now](#9--the-concrete-consumers-defined-now)
10. [Versioning and compatibility](#10--versioning-and-compatibility)
11. [A worked example](#11--a-worked-example)
12. [Appendix — what this document could not resolve](#12--appendix--what-this-document-could-not-resolve)

---

# 1 · The one-sentence contract, and the boundary rule

## 1.1 The contract

> **`warehouse-base` accepts stock movements from anyone who can name themselves, their document and
> a key that makes a retry safe; it publishes what happened to anyone who asks; and it never knows
> who either of them is.**

Everything in this document is that sentence made checkable. The two halves are symmetric and both
are load-bearing:

- **Inbound** — §2, §3. A producer describes *what physically happened to goods* in a vocabulary that
  is entirely warehouse's (item, location, owner, lot, quantity, condition), tagged with *its own*
  identity (`source_system`) and *its own* document (`source_document_type` + `source_document_id`).
  Base validates against its own rules and posts. It never resolves the producer's document, never
  branches on the producer's identity, and never imports the producer's types.
- **Outbound** — §4. Base writes every posting-relevant fact to an outbox with a monotonic cursor.
  Consumers read by cursor. Base holds **no list of consumers in code** — the list is
  `whb_outbox_subscriptions` rows, which are data.

## 1.2 The boundary rule, stated once

R4 §4.1 states the physical rule:

> *"Warehouse owns the goods while they are stationary and inside a boundary. Logistics owns them
> while they are moving between boundaries. The dock door is the boundary, and it is a warehouse
> resource."*

R7 §2.1 sharpens it, and **this contract follows R7**, because R4's rule gives the wrong answer for
four things a fleet business actually owns — a tarpaulin on a moving truck, a tyre on an axle, diesel
in a depot tank, a spare part in the transport store — and cannot decide the gatehouse at all:

> **`PC-01`** · **Warehouse owns *how much of what, whose, in what condition, and where*. Logistics
> owns *which vehicle, on whose journey, at what freight cost*. If a fact answers the first question
> it is a warehouse ledger fact, even while the goods are moving; if it answers the second it is
> logistics, even while the vehicle is parked. R4's dock door remains exactly right for the physical
> handover; the ledger boundary is the movement port, and the port never moves.**
> *(`FR-330` preamble; R7 §2.1; the two rules agree on every row of R4 §4.2.)*

## 1.3 Applying it mechanically — the four questions

Every allocation dispute is settled by asking these in order. No judgement, no precedent-hunting.

| # | Question | If yes |
|---|---|---|
| 1 | Does the fact change *how much of what, whose, in what condition, at which location*? | It is a **movement**. It goes through the port. Nothing else may change stock (`PC-02`). |
| 2 | Does the fact name a *vehicle, a journey or a freight cost*? | It belongs to the consumer. Base carries it **only** as the lineage quad — `source_document_type = 'TRIP'` and the trip's id as an opaque string. |
| 3 | Does the fact describe a *physical thing that both modules need to identify*? | Two rows, one per question each answers, joined by an **external-refs table**, never an FK, and neither side may require the other to exist (§6, R7 §2.4). |
| 4 | Is it a *device fact* — which vehicle crossed a line, which gun scanned what, when? | It belongs to **neither**. It is published to a handler list, the shape already live at `automotive/backend/src/main/java/ai/automotive/controller/BoomBarrierWebhookController.java:44-48` with resolution at `:198-209`. (`FR-340`) |

> **`PC-02`** · **The port is the only write path to stock.** No module — including `warehouse`
> itself — changes `whb_stock_positions` other than as the ledger's projection, and no module writes
> `whb_stock_movements` / `whb_stock_movement_lines` except through the one writer service behind the
> port. *(`L-2`, `L-4`, `FR-350`, R7 `B5`.)*
>
> This is not theoretical. The suite already contains the failure it prevents:
> `accessories/backend/src/main/java/ai/accessories/service/inventory/StockReceiptService.java:374-410`
> — `reverseStockLevel()` recomputes `quantityOnHand`, calls `stockLevel.setQuantityOnHand(newQty)`
> at `:406` and `stockLevelRepository.save(stockLevel)` at `:408`, and writes **no**
> `InventoryTransaction` row anywhere in the method. The balance is therefore not derivable from the
> transaction log. That is `R1 C-021` and `D-4`'s reason for existing. **Do not copy it.**

## 1.4 The deletion test — the seam's acceptance criterion

> **`PC-03`** · Two deletion tests define "the seam works", and both are acceptance criteria, not
> aspirations. **Delete the consumer module: warehouse still works** — locations remain, external
> references resolve to null, the display resolver falls back to rendering the document type and id
> (`FR-357`). **Delete the warehouse module: the consumer still works** — its own tables carry no
> foreign key into `whb_*`. Any design where one answer is "no" has a foreign key pointing the wrong
> way. *(`FR-336`, R7 §2.4 `G-021`.)*

---

# 2 · The inbound movement port — the wire contract

## 2.1 The design premise, and the shape that is already settled

The port is a **stock journal** — the exact analogue of an accounting journal entry: a header with
lineage and time, balanced signed lines, immutable once posted, corrected only by reversal (R4 §3.0).
The analogy is not decoration: it is why the shape is known in advance to be sufficient.

**The bean-registry half of the shape is settled by precedent, not by preference.** `R1 WF-6` records
that this monorepo already implements a "many implementations, base knows none of them" registry
three times, and all three are `List<T>` bean collections rather than a `@Primary` override — which
admits only one implementation and is therefore useless for an N-consumer port:

| Precedent | Constructor | What it proves |
|---|---|---|
| `platform/backend/src/main/java/ai/platform/service/export/ExportService.java:31` — `public ExportService(List<ExportFormatHandler> handlerList)`, indexed into a `Map` at `:32-39` by `handler.getFormat()` (`ExportFormatHandler.java:19`) | `List<T>` | A base service dispatches to whichever handlers are on the classpath, with no conditional anywhere |
| `automotive/backend/src/main/java/ai/automotive/controller/BoomBarrierWebhookController.java:47-48` — `public BoomBarrierWebhookController(List<IBoomBarrierHandler> handlers, ObjectMapper objectMapper)`, resolution at `:198-209` via `handler.validateApiKey(apiKey)`, enabled-handler fallback at `:168-171` | `List<T>` | A single inbound endpoint routed to whichever vertical claims it — the three-party device integration shape |
| `accounting-base/backend/src/main/java/ai/accountingbase/service/imports/AccImportHandlerRegistry.java:41-45` — `public AccImportHandlerRegistry(List<AccImportHandler> handlers)`, indexed in `@PostConstruct index()` at `:47-74`, duplicate claims fail the **boot** at `:65-69` | `List<T>` | The registry is explicitly *"the runtime substitute for the CHECK constraint V600120 deliberately does not put on `acc_import_batches.import_type`"* (`:15-16`), and the class comment at `:18-24` gives §7's argument in the base's own words |

> **`PC-04`** · Every extension point in `warehouse-base` — document display resolvers, in-process
> event subscribers, import handlers, gate-event handlers, **branch-link validators**
> (`WarehouseBranchLinkValidator` — a jurisdiction pack checks every `whb_warehouse_branches` link on
> save, e.g. `warehouse-india`'s GSTIN-state rule; `D-8`, `D-14`) and **pre-transition guards**
> (`WhTransitionGuard` — consulted before every document status transition, v1.1, base ships none;
> `P3-22`) — is a **`List<T>` bean-collection
> registry** indexed at `@PostConstruct`, with a **duplicate claim failing the boot loudly** and a
> **base-shipped fallback** for the empty-list case. Never a `@Primary` override. *(`FR-357`,
> `R1 WF-6`, `E-004`.)* `AccImportHandlerRegistry:42-45` documents why the injected list may
> legitimately be empty in a base-only install and is never null.

## 2.2 Endpoint surface

| Method | Path | Semantics | Permission | FR |
|---|---|---|---|---|
| `POST` | `/api/warehouse/movements` | post one movement, synchronously, **all or nothing** | `warehouse:movements:post` | `FR-032`, `FR-040` |
| `POST` | `/api/warehouse/movements/batch` | post many, each independently, **per-movement results** | `warehouse:movements:post` | `FR-034` |
| `POST` | `/api/warehouse/movements/{id}/reverse` | post the mirror; own idempotency key; mandatory reason; optional `occurred_at`/`posting_date`, current-dated when omitted (`PC-20`) | `warehouse:movements:reverse` | `FR-035` |
| `POST` | `/api/warehouse/movements/{id}/withdraw` | withdraw a `PENDING` movement — **maker only** (the submitting actor); own idempotency key; `approval_status → WITHDRAWN`, the row is kept (`RA-004`) | `warehouse:movements:post` | `FR-027` |
| `GET` | `/api/warehouse/movements/{id}` | read back, including the assigned `sequence_no` | `warehouse:movements:view` | `FR-032` |
| `GET` | `/api/warehouse/movements?source_system=&source_document_type=&source_document_id=` | **the lineage query** — how a consumer finds its own postings | `warehouse:movements:view` | `FR-036` |
| `POST` | `/api/warehouse/movements/simulate` | validate and return balance deltas **without writing** | `warehouse:movements:simulate` | `FR-037` |
| `GET` | `/api/warehouse/stock?…` · `/api/warehouse/stock/as-at?at=…` | balances and availability; never a table read | `warehouse:stock:view` | `FR-013`, `FR-174` |
| `POST` · `DELETE` | `/api/warehouse/reservations` | hold and release, by holder quad | `warehouse:reservations:hold` · `:release` | `FR-166`, `FR-167` |

> **`PC-05`** · `@PreAuthorize` on **every** port method, in `resource:action` form, with no
> exceptions — CLAUDE.md CRITICAL #1 and `FR-043`. The posting permission is additionally checked
> against the caller's **owner grants** by the single server-side resolver of `FR-114`; a request
> naming an owner the caller has no grant for is `403 OWNER_NOT_PERMITTED`, **never** an empty
> result, because an empty grid is indistinguishable from "no stock".

## 2.3 The envelope

```jsonc
POST /api/warehouse/movements
{
  "source_system":            "ADAPTER_DEALER",     // FK -> whb_source_systems.code
  "source_document_type":     "PARTS_INVOICE",      // FK -> whb_document_types.code
  "source_document_id":       "PI-2026-004417",     // opaque string, the producer's id
  "source_document_line_no":  3,                    // optional
  "idempotency_key":          "ADAPTER_DEALER:PI-2026-004417:ISSUE:1",
  "company_id":               "…uuid…",
  "warehouse_id":             "…uuid…",
  "movement_type_code":       "SALE_ISSUE",         // FK -> whb_movement_types.code
  "occurred_at":              "2026-09-01T14:22:05.000Z",
  "occurred_at_tz_offset":    330,                  // minutes; optional, v1.1 feature
  "posting_date":             "2026-09-01",
  "actor": { "actor_type": "USER", "actor_user_id": "…uuid…", "device_id": null },
  "reason_code_id":           null,
  "notes":                    null,
  "lines": [ { /* §2.5 */ } ]
}
```

> **`PC-06`** · The envelope is **one shape for every producer**. There is no per-vertical variant,
> no "simple" endpoint alongside the full one, and no second idempotency scheme. *(`FR-350`, R7
> `B6`, R3 `E-003`.)* A producer that finds the envelope inconvenient has found a base gap, and the
> place to prove that is `warehouse-adapter-example` (§8.5), not a second endpoint.

> **`PC-07`** · **`posting_date`, not `effective_date`.** `DECISIONS.md` `L-13` names the three
> timestamps `occurred_at` / `recorded_at` / `posting_date`, and `IRREVERSIBLE.md` §4.1 carries
> `posting_date DATE NOT NULL`. R4 §3.2 and the request example inside `FR-032` both say
> `effective_date`. They are the same field. **`DECISIONS.md` wins**, on both the wire and the
> column, and `FR-032`'s wording needs the one-word correction. Recorded here so an implementer does
> not build two names for one date.

## 2.4 Header — `whb_stock_movements`

`R` = required on the wire. `S` = server-assigned, rejected if a client sends it. `O` = optional.

| Field | Type | Wire | Semantics | Why it must exist on day one — the irreversibility argument |
|---|---|---|---|---|
| `id` | UUID | S | the movement | — |
| `company_id` | UUID FK | **R** | the legal entity whose books this move belongs to | **Unbackfillable.** Cross-GSTIN transfers (`F-025`) and multi-entity installs. Adding a company axis after the ledger has rows assigns every historic row to a *guessed* entity, and a GST return computed from guessed entities is a filing error, not a data-quality issue. `FR-025`, `IRR-17` |
| `warehouse_id` | UUID FK | **R** | the site the movement is sequenced under | **Re-keying.** `sequence_no` is gapless **per warehouse**; adding the axis later renumbers history and invalidates every outbox cursor and hash chain already issued. `IRR-17` |
| `movement_type_code` | VARCHAR(40) FK → `whb_movement_types` | **R** | what business act this is | **A row, never an enum** (`FR-003`, `D-10`). An adapter that needs `PDI_CONSUME`, or logistics that needs `TRANSFER_DEPART` and `TRANSIT_LOSS`, must not need a base release. If this is a Java enum, a `CHECK` or a TypeScript union, **every adapter is blocked on base** and the port's claim is void |
| `source_system` | VARCHAR(40) FK → `whb_source_systems` | **R** | who is posting | **Unbackfillable, and half the idempotency key.** It **partitions the key namespace across producers**. Inferring it later means two producers' keys collide *retroactively*, and a collision in an append-only ledger is not repairable. `IRR-04`, `IRR-24`, `IRR-28` |
| `source_document_type` | VARCHAR(40) FK → `whb_document_types` | **R** | the producer's document kind — `SALES_ORDER`, `JOB_CARD`, `TRIP`, `POS_SHIFT`, `WORK_ORDER` | A row, not an enum, for the same reason as `movement_type_code`. `TRIP`, `MANIFEST` and `CONSIGNMENT` are *logistics* document types and must be insertable from the logistics migration. `FR-018`, R7 §6 item 8 |
| `source_document_id` | VARCHAR(100) | **R** | the producer's own id, **opaque** | Deliberately `VARCHAR`, not UUID: **an external system's id is not ours**. A POS shift id, a marketplace order number and a trip reference are not UUIDs, and coercing them loses the identity |
| `source_document_line_no` | INTEGER | O | the producer's header-level line pointer | Without it a **partially reversed** multi-line source document cannot be reconciled line by line — and partial reversal is the normal case, not the exception |
| `idempotency_key` | VARCHAR(200) | **R** | caller-supplied, unique within `source_system` | **The most irreversible field in the schema.** Unique per `source_system` **across months** through the non-partitioned `whb_movement_idempotency_keys` registry (`DATA-MODEL.md` §1.9, `I-11`). A ledger that has already double-posted **cannot be deduplicated afterwards**, because a duplicate is indistinguishable from a legitimate repeat of the same real event. `L-9`, `FR-017`, `IRR-04` |
| `payload_hash` | CHAR(64) | S | SHA-256 of the canonicalised request body (§3.3) | Distinguishes *"retry"* from *"different payload, reused key"*. **Without it the conflict rule in §3.2 cannot exist** — the server can only choose between silently overwriting and silently ignoring, and both are wrong |
| `sequence_no` | BIGINT | S | gapless, per warehouse | **A sequence cannot be started retroactively over rows that already exist.** The outbox cursor (§4) and the hash chain both key on it. `FR-006`, `IRR-03` |
| `prev_payload_hash` | CHAR(64) | S | the previous movement's `payload_hash` in the same warehouse | Tamper evidence. **A chain begun in v2 proves nothing about v1.** Feature is v2; the column is v1. `IRR-03` |
| `occurred_at` | TIMESTAMPTZ | **R** | **producer-supplied business time** — when it physically happened | **Unbackfillable, and the single most commonly collapsed field.** A gate-out at 22:00 synced at 09:00 next morning dates itself wrong; in-transit ageing is a day out; storage anniversary billing bills the wrong month. It cannot be reconstructed from `recorded_at`. `L-13`, `FR-007`, `IRR-21` |
| `occurred_at_tz_offset` | SMALLINT (minutes) | O | the producer's local offset at `occurred_at` | A UTC instant does not say *which local day* it was, and **every statutory register is a local-day register**. Column v1, feature v1.1. `IRR-21` |
| `recorded_at` | TIMESTAMPTZ | S | server clock at post | The delta from `occurred_at` is **the only latency diagnostic that exists**. Once collapsed into one column it is gone for the past |
| `posting_date` | DATE | **R** | the accounting / billing date | Diverges from `occurred_at` at a period boundary and at a client's billing cycle. Collapsing them means a 2nd-of-month posting of a 31st-of-month event **silently lands in the wrong invoice and the wrong period**. `L-13`, `FR-007` |
| `period_id` | UUID FK → `whb_stock_periods` | S | resolved from `posting_date` | **Rows posted before periods existed belong to no period**, so the first close has an un-closeable opening set. `FR-021`, `IRR-22` |
| `reversal_of_movement_id` | UUID FK self | S | set by `/reverse` only | If v1 permits `UPDATE`, **the corrections are already invisible by the time this column arrives**. `FR-005`, `IRR-02` |
| `reversed_by_movement_id` · `is_reversed` | UUID FK self · BOOLEAN | S | denormalised | For *"is this still live"* without a self-join on the hot table |
| `actor_type` | VARCHAR(30) | **R** | `USER` · `DEVICE` · `INTEGRATION` · `SCHEDULED_JOB` · `IMPORT` · `SYSTEM_CORRECTION` | *"Who moved this"* is the **first** audit question and it is **not always a user**. A geofence-triggered arrival, an RFID portal read and a scan-gun posting have no attributable actor without `DEVICE`. `FR-024`, `IRR-48` |
| `actor_user_id` | UUID FK → `users` | O | required when `actor_type = USER` | — |
| `device_id` | VARCHAR(100) | O | which gun, which portal, which dock terminal | **Diagnosing a mis-scanning device retroactively is impossible without it.** The symptom — one bin's counts drifting for three weeks — is only attributable if the device was on the row. Column v1, RF feature v1.1 |
| `reason_code_id` | UUID FK → `whb_reason_codes` | O / conditionally **R** | required when the movement type carries `requires_reason` | **A reason recorded as free text in v1 is a categorical dimension that can never be reported on for the past.** A transit loss without a categorical reason is unreportable and unclaimable against the carrier. `FR-019`, `IRR-32` |
| `handover_id` · `posting_status` | UUID · VARCHAR(20) | S | the accounting seam (`D-6`) | `NOT_APPLICABLE` · `PENDING` · `POSTED` · `REJECTED`, default `NOT_APPLICABLE`. Pre-integration movements have no marker, so *"does the stock ledger tie to the GL"* is unanswerable **for the audited period**. `IRR-41` |
| `approval_status` · `approved_by` · `approved_at` | — | S | for types with `requires_approval` | Scrap and write-down. `FR-027` |
| `posted_at` · `notes` | TIMESTAMPTZ · TEXT | S · O | — | — |
| audit columns | `created_by`, `created_at`, `updated_by`, `updated_at`, `version` | S | house convention | `updated_*` exist and are **never written after post** (`L-2`) |

**Deliberately not on the header** — stated so it is not "discovered" later as a gap: `owner_id` (it
is per line — `FR-042`), `item_id`, `quantity`, `location_id` (a movement is not a single line), any
JSONB payload, any carrier / AWB / trip / vehicle, any price / customer / tax, any billing charge
code, any free-text `reference`. §2.9 gives each one its home.

## 2.5 Line — `whb_stock_movement_lines`

> **`PC-08`** · **A line has exactly one end.** One `location_id`, one `stock_status_code`, one
> `owner_id`, one `lpn_id`, one `duty_status`, and a **signed** `quantity`. A movement is **two or
> more** such lines that conserve quantity (`D-4`, `L-1`). A putaway, a `STATUS_CHANGE` and an
> `OWNER_CHANGE` are each **two lines**, never one row with two ends.
>
> **Divergence, stated.** R4 §3.3 puts `from_location_id` **and** `to_location_id` on one line (and
> additionally `from_stock_status_code`, `from_lpn_id` / `to_lpn_id`), and R5 row 20 asks for both
> location columns `NOT NULL`. Under `D-4` that is the from/to row — the exact shape `T-001` /
> `IRR-01` exists to prevent, and the shape the prior WMS art used. **`DECISIONS.md` wins**
> (`IRREVERSIBLE.md` §7.1). **The irreversible content of both proposals survives intact**: virtual
> locations must exist so that no side of a movement is ever absent (`IRR-05`, `FR-002`), and status
> must be on the line *and* in the position key (`IRR-10`). Only the mechanism changes.

| Field | Type | Wire | Semantics | Why it must exist on day one |
|---|---|---|---|---|
| `line_no` | INTEGER | **R** | ordinal within the movement | — |
| **`owner_id`** | UUID FK → `whb_owners` | **R** | **whose the goods are** | **The single most expensive column to add late in the entire design.** No rule recovers whose a unit was; backfill is impossible; the position unique key changes; every query changes grain. Four lenses reached this independently (`T-002`, `F-001`/`F-002`, R5, R7 §6 item 1). `D-5`, `FR-107`, `IRR-06`. **`NOT NULL` in every install, including single-owner ones — there is no single-owner mode** (`FR-109`) |
| `owner_type_code` | VARCHAR(40) | **echo** | resolved from the owner, returned on the response | **Derived, never accepted as authority.** It drives `is_financial` and `cost_basis` (`L-14`). A producer *may* send it; if it disagrees with the owner's actual type the movement is refused (`OWNER_TYPE_MISMATCH`, §3.9) rather than silently preferring one. Registry: `whb_owner_types` (`FR-108`) |
| `item_id` | UUID FK → `whb_items` | **R\*** | what | \* or one of the four identifiers of `PC-09` below |
| `location_id` | UUID FK → `whb_locations` | **R** | where — **including virtual locations** | `NOT NULL` **is the whole of `L-1`**. A receipt's counter-side is a `SUPPLIER` virtual location, never an absent row; without it the ledger has a hole and a leak is undetectable. `FR-002`, `FR-084`, `IRR-05` |
| `quantity` | DECIMAL(18,4) | **R** | **signed**, as entered | **No `CHECK (quantity <> 0)`** — value-only movements need zero (§2.7). `FR-010`, `IRR-37` |
| `uom_code` | VARCHAR(20) FK → `whb_uoms` | **R** | as entered by the producer | Freight is billed per kg, stock is held in cases. The entered unit is a fact about the producer's document and is not recoverable from the base quantity |
| `base_uom_code` | VARCHAR(20) FK | S | the item's stocking unit | — |
| `base_quantity` | DECIMAL(18,4) | S | signed, computed at post | `L-1` sums **this** |
| `conversion_factor_used` | DECIMAL(18,8) *(`OD-7`)* | S | **frozen at post** | **Conversion factors change.** A ledger that re-derives from today's factor **silently restates last year**, and the restatement is undetectable because nothing records what the factor was. `L-7`, `FR-009`, `IRR-34` |
| `stock_status_code` | VARCHAR(40) FK → `whb_stock_statuses` | **R** | the condition the goods are in at this end | Otherwise **quarantine is modelled as a location** and "damaged stock in the bulk aisle" is unrepresentable — and the **balance unique key is wrong for every historic row** the day status is added. `F-068`, `FR-102`, `IRR-10` |
| `duty_status` | VARCHAR(40) FK → `whb_duty_statuses(code)` | **R** (default `DOMESTIC`) | customs status — registry 15 (`DATA-MODEL.md` §2.1.1). **Base seeds `DOMESTIC` only**; `BONDED`, `MOOWR`, `SEZ`, `FTWZ` and `EXPORT_UNDER_BOND` are `warehouse-india`'s rows (`P4-07`) | **Bonded and duty-paid stock of one SKU must never merge into one balance.** Once commingled **no algorithm separates them**, and it is a customs offence, not a data-quality issue. A value that is not a registry code is refused by the FK, so no new balance grain appears (`WH-SC-327`). Column v1, feature v2 (`warehouse-india`). `D-5`, `FR-104`, `IRR-12`, `RL-001` |
| `lot_id` | UUID FK → `whb_lots` | O | required when the item's `lot_control_mode` demands it | **A recall is a question about the past.** `FR-094`, `IRR-13` |
| `serial_id` | UUID FK → `whb_serials` | O | required per the item's `serial_control_mode` | A tyre is a serial; a chassis is a serial. `FR-097`, `IRR-14` |
| `lpn_id` | UUID FK → `whb_lpns` | O | the licence-plate / pallet this end refers to | **Per-pallet and anniversary storage billing are defined over pallets**, and a pallet the ledger never recorded cannot be billed for the past. `whb_lpns.received_at` is the anniversary anchor and has no substitute. `F-064`, `FR-100`, `IRR-15` |
| `condition_code` | VARCHAR(40) FK | O | condition as an axis **separate** from workflow step | Merged into `stock_status_code`, the single column silently drops one of the two facts. Column v1, feature v1.1. `IRR-11` |
| `unit_cost` | DECIMAL(19,6) *(`OD-7`)* | O | per base unit | Warehouse owns cost (`D-6`). A **price** is a commercial fact about a sale and never rides the line (`FR-041`) |
| `cost_currency_code` | CHAR(3) | O | — | **Retro-fitting currency onto a cost history is guessing.** Column v1, multi-currency v2. `IRR-36` |
| `extended_cost` | DECIMAL(19,4) | O | the value effect of this line | The carrier of a value-only movement (§2.7) |
| `cost_basis` | VARCHAR(30) | **R** | `ACTUAL` · `STANDARD` · `AVERAGE` · `INFORMATIONAL` · `ZERO_BAILMENT` | **Decides whether an accounting envelope is emitted at all.** Decided downstream = a year of wrong journals, unwound by hand. `L-14`, `FR-112`, `IRR-36` |
| `moving_average_after` · `cost_layer_id` | DECIMAL(19,6) · UUID | S | valuation snapshots | Without the snapshot the 31-March cost is **not reproducible**. Columns v1; AVCO v1.1, FIFO v1.1. `IRR-38`, `IRR-39`. *(Whose table the layers live in is `OD-1`/`OD-6`; the **columns** are not in doubt — `IRREVERSIBLE.md` §7.3 item 1)* |
| `tax_classification_code` · `tax_classification_scheme` | VARCHAR(20) · VARCHAR(20) | S | snapshotted from the item at post: the code (HSN/SAC under `warehouse-india`) and the scheme that issued it | **Reading the item master later gives the *new* code for *old* documents**, on a filed return. Named for no one country's scheme, so a second jurisdiction is a new scheme value, not a renamed ledger column (`RL-008`). `FR-066`, `IRR-42` |
| `reason_code_id` | UUID FK | O | line-level override of the header reason | — |
| `source_line_ref` | VARCHAR(100) | O | **the producer's own line identity** | Distinct from the header's `source_document_line_no`: the header field points at *a line of the producer's document*; this points at *the producer's own line-level identity*, which for a scan-gun batch or a marketplace order is not an ordinal. Without both, a partially reversed multi-line document cannot be reconciled. R7 §6 item 3, `FR-018` |
| `expiry_date_override` · `qc_result_code` | DATE · VARCHAR(30) | O | producer knows an expiry the lot does not yet carry; receipt already inspected | — |
| `read_point_location_id` · `biz_location_id` | UUID FK · UUID FK | O | EPCIS: where the scan happened vs where the goods then were | Two different facts. Columns v1, feature v2. `IRR-20` |

**Attributes side table** — `whb_movement_line_attributes (movement_line_id, occurred_at,
attribute_key_id FK → whb_attribute_keys, value_string, value_number, value_date, value_boolean)`:
**four typed value columns**, the one matching the key's `value_type` populated, as `DATA-MODEL.md`
§2 carries it. The earlier `(attribute_value, value_type)` pair — one text value with a type tag — is
withdrawn: the table is append-only from `V500030`, and a typed value cannot be recovered from text
afterwards (`RL-007`).

> **`PC-09`** · **Registered keys only. No JSONB.** An unregistered key is a column nobody can
> filter, export or index — *"JSONB with extra steps and no index"* (R7 `G-063`). `whb_attribute_keys`
> is the thirteenth catalogue (§7) precisely so that "typed side table" cannot degrade into a
> free-text key column. *(`FR-026`, `FR-383`.)* Note the live nuance recorded by `R1 CM-3`: CLAUDE.md's
> blanket *"NO JSONB"* is overstated — `platform/backend/src/test/java/ai/platform/architecture/ArchitectureInvariantsTest.java:225-239`
> freezes a **baseline** rather than banning it, and every warehouse grid migration **must** still
> emit `'[…]'::jsonb` for `grid_preferences`. **The rule that holds is: no JSONB on a new warehouse
> business table.**

> **Amended 2026-09-16 (C5) — `value_date` is a producer INSTANT and the screen files a calendar
> DAY; settled by default.** Both typed side tables carry `value_date` as `TIMESTAMPTZ`, and the port
> normalises it as an instant: `WhbMovementEnvelopeCodec.java:472` parses the member with
> `instant(...)`, and `INSTANT_FIELDS` (`:100`) carries `value_date` beside `occurred_at` so `PC-17`
> hashes it to UTC Z at milliseconds. A `DATE` attribute key, though, is a calendar day on every
> screen that files or renders one. **A producer east of UTC posting after local midnight therefore
> renders a day early** — `2026-03-10T02:00+09:00` is stored `2026-03-09T17:00Z` and reads back as
> 9 March. A day entered on a screen is filed at UTC midnight and reads back correctly, so the drift
> is the producer's instant alone. **The fix is the retype, not a render-time shim**: separate
> `value_date DATE` and `value_datetime TIMESTAMPTZ`, the shape `assets` already carries
> (`assets/.../V60674__Asset_custom_field_engine_tables.sql:269-270`), rather than a bare retype —
> `whb_attribute_keys` has no DATETIME value type today. It lands in each owning table's **v2
> increment** and nowhere else: `whb_item_attribute_values` in `P1-01`'s, `whb_movement_line_attributes`
> in `P0-02`'s, because that table is partitioned and append-only from `V500030` and `UPDATE` is
> refused to every actor. Recorded, not fixed: no v1 behaviour changes.

## 2.6 Identifying an item without knowing warehouse's UUIDs

> **`PC-10`** · A line identifies its item by **`item_id`**, or **`sku`**, or **`barcode`**, or
> **`{source_module, external_id}`** resolved through `whb_item_external_refs` (§6). Exactly one
> must be supplied; supplying two that disagree is `ITEM_IDENTIFIER_CONFLICT`. *(`FR-038`, `T-033`,
> `G-040`.)*
>
> **Why the fourth is not optional.** A dealer's own part number, a job card's material code and an
> OEM's number are **none of the first three**. Without the fourth, either every adapter stores a
> warehouse UUID in its own tables — a hidden coupling that makes a re-seed impossible — or the port
> grows a per-vertical identifier column, which is the failure the port exists to prevent. `FR-061`.

The same rule applies to `location_id` (via `whb_location_external_refs`) and to any counterparty
reference (via `whb_counterparty_external_refs`).

## 2.7 Value-only movements — `quantity = 0` with `unit_cost` present

> **`PC-11`** · **Zero-quantity, non-zero-value movements are legal.** There is no
> `CHECK (quantity <> 0)` on the line. Freight, duty, clearing charges and write-downs arrive
> **after** the goods and must land on the received lot. *(`FR-010`, `FR-046`, `F-088`.)* The v1
> seeded value-only movement types are `LANDED_COST_APPLY`, `COST_ADJUSTMENT`, `REVALUATION` and
> `WRITE_DOWN` (`FR-046`).
>
> **The cost of not having it**, stated because it is the argument that carries: freight can never
> capitalise into stock cost, and warehouse and accounting then disagree **permanently** with no
> mechanism to converge. R7 §1.7 records that **no prior-art transport document in this monorepo
> connects freight to inventory value at all** — so this is net-new and the hook must be in v1.

> **`PC-12`** · A value-only movement is still **two or more lines** (`D-4`). Both carry
> `quantity = 0`, so `L-1`'s quantity conservation holds trivially; the **value** conserves across
> the lines — the positive `extended_cost` on the stock-bearing location/lot, the negative on a
> **virtual offset location**. The movement type declares
> `balance_rule = MUST_BALANCE_PER_OWNER_ITEM` for quantity and `value_balance_rule = MUST_BALANCE`
> for value.
>
> **Two things this clause needs and does not have.** (a) `FR-084`'s seeded virtual-location list —
> `SUPPLIER`, `CUSTOMER`, `ADJUSTMENT`, `SCRAP`, `PRODUCTION`, `IN_TRANSIT`, `COUNT_VARIANCE`,
> `OPENING_BALANCE`, `CONSUMED`, `JOB_WORKER` — **has no value-offset row**. A one-row addition
> (`LANDED_COST_OFFSET`, or the reuse of an `ADJUSTMENT_OFFSET`-typed location) is required and is
> flagged in §12 rather than assumed. (b) **Value conservation is not among `L-1`…`L-14`** — `L-1`
> conserves quantity only. Whether `value_balance_rule` is a movement-type behaviour column or a
> fifteenth invariant is a `DECISIONS.md` question and is raised in §12, not decided here.

## 2.8 One movement, two owners

> **`PC-13`** · A single movement **may** carry lines of two different owners where the movement
> type permits it, and it then balances **per `(owner, item)`** rather than per movement. Each
> movement type declares `balance_rule ∈ {MUST_BALANCE_PER_OWNER_ITEM, MUST_BALANCE_PER_ITEM,
> UNBALANCED_ALLOWED}` and `allows_mixed_owner` (default `false`). *(`FR-042`, `F-059`, `F-009`.)*
>
> **Why it is one movement and not two.** A 3PL's own carton consumed against a client's order is
> **one atomic event**. Modelled as two calls, the second can fail independently and the consumption
> is then unbilled and the carton unaccounted, with no transaction boundary that would have caught
> it. The same shape covers a title transfer (`OWNER_CHANGE`): goods change owner **without moving**,
> as a negative line on the outgoing owner and a positive on the incoming, same item, lot, serial,
> LPN, location and status (`FR-111`, `L-11`). An `UPDATE` to the position's owner would mean the
> ledger no longer explains the balance, which is `L-4`'s whole point.

## 2.9 What the port must NOT carry — and where each thing goes instead

Stated so it is not "discovered" as a gap by the fourth reviewer. *(`FR-041`, R4 §3.6.)*

| Not in the port | Why | Where it goes instead |
|---|---|---|
| A carrier, an AWB, a trip, a vehicle | `warehouse-base` must not know transport exists | the lineage quad — `source_document_type = 'TRIP'`, `source_document_id = <trip id>` |
| A **sales price**, a customer, a tax | a movement is not a sale. *(A **unit cost** does ride the line, because warehouse owns cost under `D-6`; a price is a commercial fact about the document that sells)* | the accounting envelope emitted from the outbox |
| A billing charge code | the meter subscribes to events; base does not bill | `wh3_billable_events` (`F-011`) |
| A channel-specific field | one channel's field becomes fifty | `whb_movement_line_attributes` with a **registered** key |
| A JSONB payload | forbidden on new business tables (`PC-09`); it is how a schema becomes unqueryable | the typed attribute side table |
| A free-text `reference` | it cannot be joined or indexed meaningfully | the four lineage columns + `source_line_ref` |
| An expression, a script or a rule DSL | the fifth rule engine always introduces one | bounded rows — the pattern of `F-028`, `F-037`, `F-090` |
| A carrier's rate, a freight cost | transport money | `log_freight_charges`; its *effect* on stock value crosses as `LANDED_COST_APPLY` (§2.7) |

## 2.10 The twelve provably unaddable properties

R4 §3.7 states the claim this section exists to support: twelve properties are **provably unaddable**
rather than merely inconvenient. Restated against this contract's field names, with each one's clause:

| # | Property | Clause | If it lands in v2 instead |
|---|---|---|---|
| 1 | `owner_id` per **line** | `PC-08` | No rule recovers whose a unit was. Re-key of the two largest tables **and** an unbackfillable |
| 2 | `occurred_at` distinct from `recorded_at` | §2.4 | A device's business time is lost at sync, permanently |
| 3 | `posting_date` distinct from both | `PC-07` | A billed period cannot be re-derived for the past |
| 4 | `idempotency_key` unique + `payload_hash` | `PC-14`…`PC-17` | An already-duplicated ledger **cannot be deduplicated** |
| 5 | Append-only + `sequence_no` + `prev_payload_hash` | `PC-19` | A chain cannot be started over mutable history |
| 6 | `reversal_of_movement_id` | `PC-20` | If v1 allowed edits, the corrections are already invisible |
| 7 | `lot_id` / `serial_id` | §2.5 | A recall is retrospective by definition |
| 8 | `lpn_id` + `whb_lpns.received_at` | §2.5 | Anniversary storage billing has no other anchor |
| 9 | `stock_status_code` on the line **and** in the position key | §2.5 | Condition and place are permanently conflated |
| 10 | `uom_code` + **frozen** `conversion_factor_used` | §2.5 | Factors change; history silently restates |
| 11 | The lineage quad + `source_line_ref` | §2.4, §2.5 | A single free-text ref cannot be joined; a consumer cannot find its own postings |
| 12 | `is_financial` (type) + `cost_basis` (line) | §2.5 | A year of bailed stock in our own GL, unwound by hand |

**Everything else in R4 can wait. These twelve cannot.** The full merged list, with the argument per
item and the four points of no return, is [`IRREVERSIBLE.md`](IRREVERSIBLE.md) — cited, not restated.

---

# 3 · Semantics

## 3.1 Atomicity

> **`PC-14`** · A movement posts **wholly or not at all**. There is **no partial success within a
> single movement**. A producer that wants per-line independence sends **one movement per line** and
> uses the batch endpoint. *(`FR-040`.)*

## 3.2 Idempotency — the exact table

> **`PC-15`** · `(source_system, idempotency_key)` is unique **across months**: it is the `PRIMARY KEY` of
> `whb_movement_idempotency_keys`, inserted in the posting transaction for a movement, a reversal and a
> withdraw alike, each on its own key (`DATA-MODEL.md` `I-11`). The key is **caller-supplied and never
> server-generated**. *(`L-9`, `FR-017`.)*

| Condition | Response | Body |
|---|---|---|
| Key unseen | **`201 Created`** | the new movement id and its assigned `sequence_no` |
| Key seen, `payload_hash` **identical** | **`200 OK`** | the **original** movement id and its original `sequence_no`. **This is not an error.** Nothing is posted |
| Key seen, `payload_hash` **different** | **`409 Conflict`** · `IDEMPOTENCY_KEY_REUSED` | nothing posted; the body **names the original movement id** so the caller can diff |
| Key absent or blank | **`422 Unprocessable Entity`** · `IDEMPOTENCY_KEY_REQUIRED` | — |

> **`PC-16`** · **Never generate a key server-side, and never silently overwrite.** A
> server-generated key makes a retried network timeout post **twice** — which is the exact failure
> the key exists to prevent. A silent overwrite makes the ledger disagree with the producer with no
> record that it ever did.

## 3.3 The payload hash — what is hashed, stated because no source states it

R4 §3.2 names `payload_hash` and gives its purpose; **neither R4 nor R7 nor the FRD says what is
hashed**. Two producers computing the hash differently, or the server computing it over an enriched
body, makes the `409` rule fire randomly. This contract closes the gap:

> **`PC-17`** · `payload_hash` is `SHA-256`, lower-case hex, computed **server-side** over the
> **canonicalised received request body**, before any defaulting, enrichment or resolution.
> Canonicalisation is: object keys sorted lexicographically at every level; no insignificant
> whitespace; `null`-valued keys **omitted**; numbers rendered in the decimal string form in which
> they were received; timestamps normalised to UTC `Z` with millisecond precision; arrays in
> received order. `idempotency_key` **is** part of the hashed body; transport headers, the
> authenticated principal and `recorded_at` are **not**.
>
> **A client-supplied hash is rejected.** Trusting one lets a buggy producer declare two different
> payloads identical, which is a silent double-post with a clean audit trail — worse than a loud
> failure. Hashing the *received* body rather than the normalised one is what makes a v1 producer's
> replay stable after v2 adds an optional field with a server default (§10.2).

## 3.4 Batch posting — per-movement results

> **`PC-18`** · `POST /api/warehouse/movements/batch` accepts N movements, **each with its own
> idempotency key**, **each in its own transaction**, and returns a **per-movement result array**
> with a per-movement HTTP-equivalent status and error code. **It is never all-or-nothing.**
> *(`FR-034`, `F-092`.)*
>
> **The argument, in one sentence:** a driver's device syncing forty scans after a route, or a scan
> gun syncing four hundred after a shift, **must not lose thirty-nine because one bin was renamed**.
>
> **Divergence, stated.** R4 places batch posting at v1.1 (`F-092`); R7 §6 item 12 places it in the
> v1 irreversible list. **`FR-034` follows R7 and so does this contract**, because the port's *shape*
> is a P0 concern: adding an endpoint later is cheap, but a producer that has already built
> one-movement-per-call retry logic against a 201/409 contract cannot be retro-fitted to a
> per-movement result array without a version bump for every consumer.

```jsonc
// 207-style response body; the HTTP status is 200 when the batch was accepted for processing
{
  "results": [
    { "index": 0, "status": 201, "movement_id": "…", "sequence_no": 88412 },
    { "index": 1, "status": 200, "movement_id": "…", "sequence_no": 88390, "idempotent_replay": true },
    { "index": 2, "status": 422, "error": "UNKNOWN_LOCATION",
      "details": { "errors": { "lines[0].location_id": "No location with code 'A-12-03' at this warehouse" } } },
    { "index": 3, "status": 409, "error": "IDEMPOTENCY_KEY_REUSED", "original_movement_id": "…" }
  ],
  "accepted": 2, "replayed": 1, "rejected": 1
}
```

**Ordering inside a batch.** Movements are processed **in array order** and a failure does not stop
the batch. Where a producer's movements are causally dependent (depart before arrive), it is the
producer's responsibility to order them; base does not reorder and does not infer dependency.

## 3.5 Correction is reversal — there is no edit and no delete

> **`PC-19`** · **Append-only.** No posted movement or line is ever `UPDATE`d or `DELETE`d.
> Three layers, and convention is not one of them: **one writer service with no update method**, a
> **database trigger** rejecting `UPDATE` / `DELETE` **and `INSERT` into an already-posted
> movement**, and **no repository path** that could do it. *(`L-2`, `FR-004`.)*

> **`PC-20`** · **Correction is reversal.** `POST /movements/{id}/reverse` with a **new idempotency
> key** and a **mandatory `reason_code_id`**. It produces a mirror: the same lines with negated
> quantities, the same lot / serial / LPN / status / owner / duty status, `movement_type_code` set
> to the original type's `reversal_type_code`, and `reversal_of_movement_id` set. *(`L-3`, `FR-005`,
> `FR-035`.)*
>
> - **A reversal is itself irreversible** — `CANNOT_REVERSE_A_REVERSAL`. Re-doing is a **new forward
>   movement**, which is the honest record of what happened.
> - **Reversing an already-reversed movement** is `ALREADY_REVERSED`.
> - **A reversal respects the period rules.** A reversal into a `CLOSED` period is `PERIOD_CLOSED`,
>   and the correct act is a **current-dated** reversal, not a backdated one.
> - **The reversal's dates.** The request may carry `occurred_at` and `posting_date`. When it omits
>   them the reversal is **current-dated**: the injected `Clock`'s now and the current date. Every date
>   guard reads the reversal's own dates.
> - **The reversal's key is its own**, claimed in `whb_movement_idempotency_keys` like any other; a
>   retry with the same key returns `200` and the same reversal (`WH-SC-171`).
> - **"Edit" is never offered anywhere in the product** — not on a screen, not on the API, not as an
>   admin tool.

## 3.6 Ordering, and out-of-order arrival

Offline sync makes out-of-order arrival **normal**, not exceptional. The rules must therefore be
stated rather than discovered by the first consumer that syncs a shift.

> **`PC-21`** · `sequence_no` is assigned **in server acceptance order**, per warehouse, gaplessly.
> It is **not** business order. `occurred_at` is business order. The two routinely disagree and
> nothing in the product may assume otherwise.

> **`PC-22`** · **A movement is never refused for arriving after a movement with a later
> `occurred_at`.** Late arrival is not an error condition.

> **`PC-23`** · **Stock sufficiency is evaluated against the balance as it stands at post time, not
> as at `occurred_at`.** This is the surprising consequence and it is a decision, not an oversight:
> evaluating as-at would require replaying the ledger forward from an arbitrary point on every post,
> and would let a late arrival retro-invalidate movements already accepted. The visible consequence
> is that a genuinely-valid historical sequence can be refused with `INSUFFICIENT_STOCK` if it
> arrives after the stock was consumed by something else — which is a **real** stock discrepancy and
> belongs in the blocked-move queue of `FR-028`, not silently accepted.

> **`PC-24`** · **`occurred_at` in the future is refused outright** — `OCCURRED_AT_IN_FUTURE`.
> A future business time breaks every ageing calculation **silently**. *(`FR-008`.)*

> **`PC-25`** · **A back-dated post changes as-at answers for the past, by design.**
> `GET /stock/as-at?at=…` recomputes from the ledger (`FR-013`), so an as-at answer given before a
> late arrival and after it will legitimately differ. Consumers that cache an as-at figure must
> record the `sequence_no` at which they computed it. This is what makes `L-4` — positions are a
> cache that a full rebuild reproduces exactly — true rather than approximately true.

## 3.7 Periods and backdating

> **`PC-26`** · `posting_date` in an **`OPEN`** period: accepted. In a **`SOFT_CLOSED`** period:
> requires the override permission and **records the override with the overriding user**. In a
> **`CLOSED`** period: refused, `PERIOD_CLOSED`, **including a reversal**. *(`L-8`, `FR-020`,
> `F-085`.)* A trigger with session-GUC gating is the backstop; the service rejects first, in the
> transaction, with a field-level error. **A trigger firing in production is an incident, not a
> validation** (`DECISIONS.md` §4).

## 3.8 Simulate

> **`PC-27`** · `POST /movements/simulate` runs the **whole** validation chain and returns the
> resulting balance deltas and the **complete** error list, and **writes nothing** — no movement, no
> inbound-message row, no outbox event, no idempotency-key claim. *(`FR-037`.)*
>
> It is what a channel adapter calls **before promising stock**, what an operator screen calls to
> **explain a rejection**, and what support calls when a client says *"it says insufficient stock and
> there are 40 on the shelf"* — which is, not coincidentally, the exact symptom an orphaned
> reservation produces (§5).

## 3.9 The error-code vocabulary

> **`PC-28`** · Every refusal is an exception carrying a **stable, machine-readable code** in the
> platform's standard envelope — `{ "error": …, "details": { "errors": { "<field path>": "<message>" } } }`
> — and **the ledger never returns quietly**. *(`FR-029`, `FR-039`.)*

> **`PC-29`** · **The codes are stable from v1 and renaming one is a breaking change to five
> callers**, because a producer's retry logic branches on them. Codes may be **added**; they are
> never renamed and never repurposed. *(`FR-039`, R4 §3.5.)*

### 3.9.1 The ratified core — 31 codes, verbatim from R4 §3.5

`R?` = should the caller retry the identical request unchanged?

| Code | HTTP | Retry? | Scope |
|---|---|---|---|
| `UNKNOWN_ITEM` | 422 | no — fix the identifier | line |
| `UNKNOWN_LOCATION` | 422 | no | line |
| `UNKNOWN_OWNER` | 422 | no | line |
| `UNKNOWN_LOT` | 422 | no | line |
| `UNKNOWN_SERIAL` | 422 | no | line |
| `UNKNOWN_LPN` | 422 | no | line |
| `UNKNOWN_MOVEMENT_TYPE` | 422 | no — the type must be registered by a migration first | header |
| `LOT_REQUIRED` | 422 | no | line |
| `SERIAL_REQUIRED` | 422 | no | line |
| `SERIAL_ALREADY_ISSUED` | 409 | no | line |
| `SERIAL_NOT_AT_LOCATION` | 409 | no | line |
| `INSUFFICIENT_STOCK` | 409 | **conditionally** — after stock arrives; see `PC-23` | line |
| `NEGATIVE_STOCK_NOT_ALLOWED` | 409 | conditionally | line |
| `MOVEMENT_UNBALANCED` | 422 | no | header |
| `MIXED_OWNER_NOT_ALLOWED` | 422 | no | header |
| `STATUS_TRANSITION_NOT_ALLOWED` | 422 | no | line |
| `LOCATION_POLICY_VIOLATED` | 409 | no — the message names the policy and the conflicting stock (`FR-087`) | line |
| `TEMPERATURE_ZONE_MISMATCH` | 422 | no | line |
| `SHELF_LIFE_RULE_VIOLATED` | 422 | no | line |
| `EXPIRED_LOT_NOT_ISSUABLE` | 422 | no | line |
| `UOM_NOT_CONVERTIBLE` | 422 | no | line |
| `PERIOD_CLOSED` | 409 | no — re-date and re-post with a **new** key | header |
| `OWNER_NOT_PERMITTED` | 403 | no | header |
| `LPN_CLOSED` | 409 | no | line |
| `LPN_NOT_AT_LOCATION` | 409 | no | line |
| `APPROVAL_REQUIRED` | 409 | **yes**, once approved | header |
| `IDEMPOTENCY_KEY_REQUIRED` | 422 | no | header |
| `IDEMPOTENCY_KEY_REUSED` | 409 | **no — never retry**; the body names the original movement | header |
| `ALREADY_REVERSED` | 409 | no | header |
| `CANNOT_REVERSE_A_REVERSAL` | 409 | no | header |
| `OCCURRED_AT_IN_FUTURE` | 422 | no — the producer's clock is wrong | header |

### 3.9.2 Additions this contract requires — and they need ratifying into `FR-039`

Marked as **additions**, each with the clause that makes it necessary. They are not in R4 §3.5.
`FR-039` names its list as *stable and documented from v1*, so these must be folded into `FR-039`
**before v1 ships** — not discovered afterwards, which would be exactly the renaming `PC-29` forbids.

| Code | HTTP | Retry? | Required by |
|---|---|---|---|
| `UNKNOWN_SOURCE_SYSTEM` | 422 | no | `PC-15` — the key namespace is partitioned by `source_system`; an unregistered one cannot be partitioned |
| `SOURCE_SYSTEM_NOT_CLAIMABLE` | 403 | no | §7.2 row 3 / `G-052` — `ACCESSORIES` is a **reserved** row with `is_claimable = false` |
| `UNKNOWN_DOCUMENT_TYPE` | 422 | no | §2.4 — `whb_document_types` is a registry and the row must exist |
| `UNKNOWN_STOCK_STATUS` · `UNKNOWN_DUTY_STATUS` | 422 | no | `PC-08` — both are on the line and both are registry-backed |
| `UNKNOWN_REASON_CODE` · `REASON_CODE_REQUIRED` | 422 | no | `FR-019` — the movement type's `requires_reason`; `FR-005` makes it mandatory on every reversal |
| `ITEM_IDENTIFIER_CONFLICT` | 422 | no | `PC-10` — two identifiers supplied that resolve differently |
| `OWNER_TYPE_MISMATCH` | 422 | no | §2.5 — a producer-supplied `owner_type_code` disagreeing with the owner |
| `VALUE_UNBALANCED` | 422 | no | `PC-12` — value conservation on a value-only movement |
| `MOVEMENT_TYPE_NOT_PERMITTED_FOR_SOURCE` | 403 | no | §8.3 `B7` — a `source_system` may be scoped to the types its own migration registered |
| `WAREHOUSE_MISMATCH` | 422 | no | §2.4 — a line's location not belonging to the header's `warehouse_id`; `sequence_no` is per warehouse |
| `COMPANY_MISMATCH` | 422 | no | `FR-025` — a location or owner outside the header's `company_id` |
| `PERIOD_CLOSED_SINCE_SUBMISSION` | 409 | no — withdraw and resubmit current-dated | `RA-004` — approving a `PENDING` movement whose `posting_date` period closed after it was submitted |
| `POSITION_CONTENTION` | 409 | **yes** | `FR-016` — a position's optimistic-lock conflict still unresolved after `warehouse.position.max_contention_retries` (`MPR-GRD-17`, contract G1) |
| `BATCH_TOO_LARGE` | 422 | no — split the batch | `RD-004` — a batch above `warehouse.port.max_batch_size`, refused before any movement posts (`MPR-GRD-23`) |
| `RETRY_AFTER` | 429 | **yes** — after the interval | `RD-004` — reserved from v1 so a producer's retry logic can branch on it; `P5-22` builds the limiter (v2) |
| `OCCURRED_AT_BEFORE_RETENTION` | 422 | no | `Y-008` — an `occurred_at` older than the oldest live ledger partition (`MPR-GRD-06`, contract G1) |
| `UNREGISTERED_INSTANT` | 422 | no | `RG-001` — the site has no `REGISTERED` link covering `occurred_at` (`MPR-GRD-07`, contract G1) |
| `PERIOD_OVERRIDE_FORBIDDEN` | 403 | no | `RA-007` / `PC-26` — posting into a `SOFT_CLOSED` period without the override permissions (`MPR-GRD-10`; built precedent) |
| `PERIOD_OVERRIDE_SELF_APPROVED` | 422 | no | `RA-007` — the override's approver is the poster (`MPR-GRD-10`; built precedent) |
| `MOVEMENT_NOT_PENDING` | 409 | no | `RA-004` — Approve, Reject or Withdraw on a row that is not `PENDING` (`MPR-GRD-28`) |
| `MOVEMENT_SELF_APPROVED` | 403 | no | `FR-408` — the approver or rejecter is the movement's actor (`MPR-GRD-19`) |
| `NEGATIVE_STOCK_OVERRIDE_FORBIDDEN` | 403 | no | `FR-015` — a `WARN` acknowledgement without `whb_negative_stock_policies:override` (`MPR-GRD-16`, contract G2) |
| `MOVEMENT_NOT_SUBMITTER` | 403 | no | `RA-004` — Withdraw by anyone but the submitting actor, a replay included (`MPR-GRD-28`) |
| `UNKNOWN_ATTRIBUTE_KEY` | 422 | no | `RL-007` — a line attribute naming no active `MOVEMENT_LINE` key (`MPR-GRD-24`) |
| `ATTRIBUTE_VALUE_TYPE_MISMATCH` | 422 | no | `RL-007` — a line attribute's value not in the one typed column its key's `value_type` names (`MPR-GRD-24`) |

**Total: 31 ratified + 27 additions = 58** — the set `FR-039` names, folded by `RD-008` (2026-09-16), and the
set `WhbLedgerErrorCodes.VOCABULARY` publishes; `WhbLedgerErrorCodesTest` asserts the 58. Counted from the two
tables above.

## 3.10 Authentication, authorisation and the permission a caller needs

> **`PC-30`** · **In-process callers** — `warehouse`, every adapter, `warehouse-3pl`,
> `warehouse-india` — authenticate as the platform principal already on the request. There is no
> second authentication scheme inside the monolith, and an adapter must not invent one.

> **`PC-31`** · The permissions a caller needs, and they exist in **v1** even where the feature is
> later, because retro-granting a permission invented in v2 to every existing role is hand work
> (`FR-407`, R7 §6 item 25):
>
> | Permission | Needed for |
> |---|---|
> | `warehouse:movements:post` | `POST /movements`, `POST /movements/batch`, `POST /movements/{id}/withdraw` (the submitter only) |
> | `warehouse:movements:reverse` | `POST /movements/{id}/reverse` |
> | `warehouse:movements:view` | `GET /movements/{id}`, the lineage query |
> | `warehouse:movements:simulate` | `POST /movements/simulate` |
> | `whb_stock_movements:post_backdated` | posting into a `SOFT_CLOSED` period (`PC-26`), together with `whb_stock_periods:override` and an approved override row whose approver is not the poster (`RA-007`) |
> | `warehouse:stock:view` | `GET /stock`, `GET /stock/as-at` |
> | `warehouse:reservations:hold` · `:release` | §5 |
> | `warehouse:outbox:replay` · `:view` | §4.6, the dead-letter grid |
>
> Plus: **`logistics:*` is reserved in v1** (`FR-407`, `FR-346`), and every dependency is inserted
> into `permission_dependencies` — **rows, never `CREATE TABLE`**. That table is platform's
> (`platform/backend/src/main/resources/db/migration/V248__Create_permission_dependencies_table.sql:17`);
> the defensive re-creation at
> `dealer/backend/src/main/resources/db/migration/V20501__add_permission_dependencies_for_customers.sql:10`
> is the documented false premise (`R1 C-017`, `FR-402`) and must not be copied.

> **`PC-32`** · **Owner scope is a `WHERE`-clause guard, not a UI filter.** The owner-grant check runs
> in the single server-side resolver of `FR-114` and is passed to every query service, export service,
> statistics map and dropdown endpoint. A contract test fails the build if a repository method
> touching an owner-scoped table takes no owner-set parameter (`FR-406`). For a 3PL, a client seeing
> another client's stock is a **contract breach, not a bug** (`FR-300`).

> **`PC-33` · OPEN — out-of-process authentication is not decided, and this contract does not decide
> it.** A `logistics` module deployed separately (which `G-046` explicitly allows) must authenticate
> to the port over HTTP, and **there is no service-account or API-key infrastructure in platform to
> do it with**. Computed: `grep -rn "CREATE TABLE.*api_key" --include=*.sql platform/backend/src/main/resources/db/migration/`
> → **0 rows**; the only API-key path in the repo is per-handler, inside the boom-barrier webhook —
> `automotive/…/BoomBarrierWebhookController.java:62` reads the `X-API-Key` header and `:209`
> delegates to `handler.validateApiKey(apiKey)`, i.e. each vertical validates its own. That is the
> right shape for a **device** webhook and is not a general machine-caller scheme.
> **Recommendation:** a platform-level service principal with owner grants, so that `PC-05` and
> `PC-32` apply unchanged and no second authorisation model exists. **This needs an `OD-` row in
> `DECISIONS.md` before `whb_outbox_subscriptions` HTTP delivery is built in v1.1** — allocating
> `OD-` ids is that document's business, not this one's.

## 3.11 The inbound message log — persist first, process second

> **`PC-34`** · **The request is persisted before it is processed.** An inbound-message row carries
> the payload reference, a status ladder (`RECEIVED` / `PROCESSED` / `FAILED` / `REJECTED`), the
> resulting movement id, the error detail and a retry count. On replay, the **stored result** is
> returned. *(`FR-044`, `T-091`.)*
>
> This is what makes `PC-15`'s `200` branch cheap and correct: the original response is *stored*,
> not recomputed. It is also what makes the **interface error queue** of `FR-045` possible — a grid
> over failed inbound messages with a reprocess action that is idempotent by construction, and an
> alert when the queue is non-empty beyond a threshold. A reprocess needs the stored endpoint's own
> permission (`PC-31`) as well as `whb_inbound_messages:reprocess`; a bulk reprocess is capped at
> `warehouse.port.max_batch_size`; a reprocess or discard of a row no longer `FAILED` is
> `409 INBOUND_MESSAGE_NOT_FAILED` — a screen refusal, not a §3.9 code; and a row an interrupted
> request left `RECEIVED` is failed by a recovery job (`movement-post-reverse.contract.md` `MPR-T3-06`).

---

# 4 · The outbound side — events

## 4.1 There is no outbox in this repository. Budget it as net-new.

**Computed 2026-09-01, on the live tree:**

```bash
grep -rli "outbox" --include=*.java --include=*.sql .    # → 0 files
```

**Zero.** Not in `platform`, not in the four accounting modules, not in `dealer`, `automotive`,
`services`, `assets`, `accessories`, `field-service`, `insurance`, `insurance-360`, `submittals`,
`lead-sharing`, `product-lift`, `doc-ocr-ai` or `mobile`. The only event-ish infrastructure in the
repo is **inbound** webhook logging (`automotive/…/V10108__Create_webhook_logs_table.sql`,
`services/…/V40015__Fix_service_webhook_logs_table.sql`).

> **`PC-35`** · **There is no precedent to copy, no retry framework and no dead-letter handling.**
> Estimating the outbox as *"a table"* will be wrong. The budget is: **the table, the gapless cursor,
> the publisher job, retry with backoff, a dead-letter grid, and a replay-from-cursor endpoint** —
> six items. `@Async` is **not** sufficient; the repo's own memory records
> `reference_async_notification_lazyinit` as a live trap. *(`FR-330`, `FR-332`, `G-045`.)*

## 4.2 `whb_outbox` — the table and the cursor

> **`PC-36`** · `warehouse-base` maintains an outbox with a **gapless monotonic cursor**, and **base
> does not know its consumers**. Consumers read **by cursor**, delivery is **at-least-once**, and a
> consumer **deduplicates on `(consumer, cursor)`**. *(`FR-330`, `F-086`.)* `DATA-MODEL.md` §2's
> `whb_outbox` row carries the column set below verbatim, from `V500040` (`P0-11`, `RL-002`).

```
whb_outbox (
  cursor            BIGINT       NOT NULL,   -- the cursor, from one sequence. Monotonic, gapless, install-wide
  recorded_at       TIMESTAMPTZ  NOT NULL,   -- the partition key
  event_type        VARCHAR(60)  NOT NULL,   -- §4.4; FK -> whb_event_types(code), no CHECK (PC-43)
  event_version     SMALLINT     NOT NULL DEFAULT 1,   -- §10.4
  occurred_at       TIMESTAMPTZ  NOT NULL,   -- business time, copied from the movement
  posting_date      DATE         NOT NULL,
  company_id        UUID NOT NULL,
  warehouse_id      UUID NOT NULL,
  owner_id          UUID NOT NULL,           -- PC-38: on EVERY event, from day one
  item_id           UUID NULL,
  lot_id            UUID NULL,
  serial_id         UUID NULL,
  lpn_id            UUID NULL,
  location_id       UUID NULL,
  stock_status_code VARCHAR(40) NULL,
  quantity          DECIMAL(18,4) NULL,      -- base UoM, signed
  uom_code          VARCHAR(20)  NULL,
  movement_id       UUID NULL,               -- when the event is ledger-derived
  movement_sequence_no BIGINT NULL,          -- the ledger cursor this event corresponds to
  source_system     VARCHAR(40) NULL,        -- the lineage quad, carried through
  source_document_type VARCHAR(40) NULL,
  source_document_id   VARCHAR(100) NULL,
  source_line_ref      VARCHAR(100) NULL,
  reason_code_id    UUID NULL,
  actor_type        VARCHAR(30) NULL,
  actor_user_id     UUID NULL,
  device_id         VARCHAR(100) NULL,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (cursor, recorded_at)
) PARTITION BY RANGE (recorded_at)           -- partitioned at CREATE, P0-02's partition job (RL-011, IRR-67)
```

> **`PC-37`** · **No payload column on the outbox in v1** — not JSONB, not `TEXT`, not a
> `payload_ref`. **The event is its typed columns**: the dimensions `PC-38` fixes plus the lineage
> quad. A consumer that needs more of the source document calls the lineage `GET` (`FR-036`) with the
> quad the event carries. An outbox that carries an opaque blob is a schema nobody can filter, index
> or reconcile — and it is the shape a billing meter cannot aggregate over; this contract meets that
> ban by having no blob. *(`RL-002`; the heavier `payload_ref` into typed attribute rows was declined —
> `GAP-REGISTER-R4.md` §3.7 (e).)*

> **`PC-38`** · **`owner_id`, `warehouse_id`, `lot_id`, `lpn_id` and the three timestamps are on
> every event from day one, even where v1 has no consumer for them.** *(`FR-331`, `IRR-66`.)*
> **Adding an event code later is cheap; adding a dimension to an existing code is not** — because
> the dimension was never emitted for the events already consumed, and consumers' cursors have
> already passed them.

## 4.3 `whb_outbox_subscriptions` — how an out-of-process consumer subscribes

> **`PC-39`** · The subscription **table** ships in **v1**; only the **in-process** delivery path is
> implemented in v1; **HTTP delivery lands in v1.1**. *(`FR-333`, `G-046`.)*

```
whb_outbox_subscriptions (
  id, subscriber_code VARCHAR(40) NOT NULL UNIQUE,
  transport         VARCHAR(20)  NOT NULL,   -- IN_PROCESS | HTTP.  NO CHECK: this is a catalogue-adjacent column
  endpoint_url      VARCHAR(500) NULL,       -- HTTP only
  secret_ref        VARCHAR(200) NULL,       -- a reference to a secret, never the secret
  event_type_filter VARCHAR(500) NULL,       -- null = all
  owner_filter_id   UUID NULL,               -- FK -> whb_owners; null = no owner narrowing
  accepted_event_version SMALLINT NOT NULL DEFAULT 1,  -- PC-75: emitted at this version until the subscriber moves
  last_delivered_cursor BIGINT NOT NULL DEFAULT 0,
  max_attempts      INTEGER NOT NULL DEFAULT 8,
  backoff_seconds   INTEGER NULL,            -- PC-44's backoff base
  is_active, status, version, audit columns
)
```

Column names are `DATA-MODEL.md` §2's; this section's earlier `target_kind` and
`last_delivered_sequence_no` are withdrawn in their favour.

> **`PC-40` · Divergence from R4, stated.** R4 `F-086` specifies the outbox and says *"base knows no
> consumers"* — correct — but **does not specify how an out-of-process consumer subscribes**, and an
> in-process `List<WhMovementEventSubscriber>` cannot reach one. **This contract follows R7 `G-046`.**
> The argument: a `logistics` module **may be a separate deployable**, and **adding the subscription
> table after three in-process subscribers exist means redesigning all three**, plus retrofitting
> delivery guarantees, retry state and a per-subscriber cursor onto events that have **already been
> consumed**. The table now is one table. The table later is a redesign.

> **`PC-41`** · A subscription is **data**, not code. Base contains **no list of consumers in Java**.
> The in-process path is the `List<T>` registry of `PC-04`; the HTTP path is a row. Neither requires
> base to name a consumer.

## 4.4 The event catalogue, and the billable-granularity requirement

> **`PC-42`** · **The event vocabulary is fixed in v1 and emits at *billable* granularity.**
> *(`FR-331`, `F-012`.)*
>
> **The argument, and it is the one that decides the design:** a 3PL bills for **handling per pick
> line** and **per carton**, and for **storage per pallet**. A design that emits only
> `order.shipped` makes per-line handling billing — **how every audited 3PL prices** —
> **permanently unavailable for the past**, because the finer facts were never emitted and cannot be
> reconstructed from a coarse event after the fact. This is the one place where an event-catalogue
> decision is *irreversible* rather than additive.

| Event code | Emitted when | Grain | Why this grain |
|---|---|---|---|
| `stock.movement.posted` | every successful post | **movement** | the ledger mirror; the lineage a consumer subscribes to |
| `stock.movement.reversed` | every reversal | movement | a reversal is a business fact, not a correction to hide |
| `receipt.line.confirmed` | a receipt line is accepted | **line** | inbound handling is billed per line |
| `putaway.task.completed` | a putaway task closes | **task** | putaway is billed per task or per pallet |
| `pick.line.confirmed` | a pick line is confirmed | **line** | **the single most commonly under-modelled event.** Per-line handling billing depends on it and nothing else can substitute |
| `carton.packed` | a carton/LPN closes | **carton** | packing is billed per carton; dimensional weight is captured here |
| `shipment.confirmed` | a shipment despatches | shipment | the coarse event — necessary, and **not sufficient** |
| `task.completed` | any task type closes | task | labour minutes, VAS pricing, cost-to-serve |
| `count.variance.posted` | a count variance posts | line | inventory accuracy KPI; the variance reason is the dimension |
| `return.line.dispositioned` | a return line gets a disposition | line | reverse-logistics handling is per line and per disposition |
| `work_order.completed` | a VAS / kitting work order closes | work order | VAS billing |
| `owner.changed` | an `OWNER_CHANGE` posts | line | a title transfer is a billable and a reportable event |
| `stock.reservation.created` / `.released` | §5 | reservation | a consumer plans against reserved stock before it is picked (`G-042`) |
| `document.status_changed` | a document's status changes, through the single transition helper | document | an install or ERP learns *"PO approved"* without a fork. **Code seeded in v1 so the grain is fixed; emitted from v1.1** (`P3-22`, `RL-014`) — see §12.2 item 9 |

**Additions this contract carries from R7 §2.7**, for the logistics seam:
`equipment.issued_to_trip` (serial, trip ref, expected return) and
`dock.appointment.detention_started` (appointment, `arrived_at`, free-time expiry) — *the charge is
logistics', the clock is ours*.

> **`PC-43`** · **`event_type` is an FK by code into `whb_event_types`** — registry 17
> (`DATA-MODEL.md` §2.1.1), created and seeded by `P0-11` in `V500040` with §4.4's codes plus
> `document.status_changed` — **with no `CHECK`**, on the same terms as the catalogues of §7. Adding
> an event code is a seed `INSERT` from the owning module's migration under `PC-66`'s guard, never an
> `ALTER`. *(`RL-002`.)*

## 4.5 Delivery guarantees

> **`PC-44`** · **At-least-once, in `cursor` order, per subscriber.**
> - **Ordering:** a subscriber's cursor advances monotonically; base never delivers `n+1` before `n`
>   to the same subscriber. Cross-subscriber ordering is not coordinated and is not promised.
> - **Duplication:** a consumer **must** deduplicate on `(subscriber_code, cursor)`. Base does
>   not promise exactly-once and no consumer may assume it. A consumer whose handler is not
>   idempotent has a bug, not a base gap.
> - **The outbox row is written in the same transaction as the movement.** That is the whole point of
>   the pattern: if the movement committed, the event exists; if it rolled back, it does not. A
>   publisher that reads committed rows and delivers them is therefore consistent by construction —
>   which is exactly why `@Async` from the service is not a substitute (`PC-35`).
> - **Retry** is exponential backoff up to `max_attempts` (default 8), per subscription.
> - **A slow or dead subscriber never blocks posting.** Delivery is a separate job reading committed
>   rows; the posting transaction does not wait on it.

## 4.6 Replay

> **`PC-45`** · `POST /api/warehouse/outbox/subscriptions/{code}/replay?from_cursor=…` resets a
> subscriber's cursor and re-delivers. It is permissioned (`warehouse:outbox:replay`), audited, and
> **the only supported recovery mechanism** — there is no "re-emit this one event" and no manual row
> insert into `whb_outbox`, because either would break the gapless-cursor guarantee that consumers
> deduplicate against.

> **`PC-46`** · The outbox is **never pruned below the oldest active subscriber's cursor**. Archiving
> beyond that point follows the ledger's archive transaction (`FR-023`) and is a v3 concern.

## 4.7 Poison messages and the dead-letter grid

> **`PC-47`** · A delivery that fails `max_attempts` times is moved to **dead-letter** state with the
> last error, the attempt count and the timestamps, and the subscriber's cursor **does not advance
> past it**. *(`FR-332`.)*
>
> **The cursor deliberately blocks.** Skipping a poison message would silently deliver an
> out-of-order stream to a consumer that was promised ordering by `PC-44`, and the consumer would
> have no way to detect it. A blocked cursor is visible, alarming and correct.

> **`PC-48`** · There is a **dead-letter grid** with a per-row retry and a skip-with-reason action,
> and an alert when a subscription has been blocked beyond a threshold. A dead letter that nobody can
> see is an outage nobody knows about. The grid follows the house pattern —
> `grid_column_definitions` + `filter_definitions` rows, both `grid_preferences.default_filters` and
> `default_columns` populated, and one `COMMON_FILTER_CONFIGS` scope (§8.6).
>
> **Note the table name.** It is **`filter_definitions`**, created at
> `platform/backend/src/main/resources/db/migration/V229__Add_filter_definitions_table.sql:8`. There
> is **no `grid_filter_definitions` table**: computed —
> `grep -rn "grid_filter_definitions" --include=*.sql .` → **9** matches, all of them comments or an
> `information_schema`-guarded block (e.g.
> `dealer/…/V20708__Remove_budget_min_rename_budget_max_to_budget.sql:29`), and
> `grep -rn "CREATE TABLE.*grid_filter_definitions" --include=*.sql .` → **0**. An unguarded insert
> into that name fails at Flyway and crash-loops the backend (`R1 CM-4`).

---

# 5 · The reservation API

## 5.1 Why a reservation is a row and not a counter

> **`PC-49`** · **Allocation is an open-item ledger, never a counter.** *(`L-10`, `FR-166`.)*
> With a counter you cannot say **who** holds a reservation, cannot release **one** order's hold,
> cannot distinguish soft from hard, cannot reserve a specific lot / serial / LPN, cannot expire a
> stale hold and cannot reconcile — so it drifts, and **the only repair is to zero it, which releases
> everyone's stock at once**.

> **`PC-50`** · **Availability is computed, never stored.**
> `available = Σ on_hand where status.is_allocatable − Σ open reservations`. A stored column drifts,
> and its formula changes the day soft allocation arrives. *(`FR-168`, `L-6`.)*

## 5.2 The holder quad

> **`PC-51`** · Every reservation carries the **holder quad** —
> `(holder_system, holder_document_type, holder_document_id, holder_line_no)` — and an
> **`expires_at`**. *(`L-10`, `FR-167`, `G-042`.)*
>
> **Divergence from R4, stated.** R4 `F-028` makes reservations a table and defines
> `available = on_hand − reserved`. It does **not** make a reservation **holdable by a module that is
> not warehouse**. **This contract follows R7 `G-042`**, which extends it, and the argument is
> concrete: **logistics reserves stock for a planned trip before any wave exists.** When the trip
> cancels, base must be able to answer *"release everything trip X held"* — and it **cannot**, if the
> only holder is an internal allocation id. **Orphaned reservations silently and permanently reduce
> availability**, and the symptom is precisely the support call `simulate` exists for: *"it says
> insufficient stock and there are 40 on the shelf"*.

Note the shape of the quad: it is **the lineage quad again**, in the reservation table. That
symmetry is deliberate — a consumer that can post a movement can release its own holds using the
same four values it already has, with no new identifier to store.

## 5.3 The surface

| Method | Path | Semantics | Permission |
|---|---|---|---|
| `POST` | `/api/warehouse/reservations` | hold, with the quad, a TTL and a reservation type | `warehouse:reservations:hold` |
| `GET` | `/api/warehouse/reservations?holder_system=&holder_document_type=&holder_document_id=` | *what does trip X hold* | `warehouse:reservations:view` |
| `DELETE` | `/api/warehouse/reservations?holder_system=&holder_document_type=&holder_document_id=` | **release everything trip X held** — the operation the quad exists to make answerable | `warehouse:reservations:release` |
| `DELETE` | `/api/warehouse/reservations/{id}` | release one | `warehouse:reservations:release` |
| `PATCH` | `/api/warehouse/reservations/{id}` | extend `expires_at`, or promote soft → hard | `warehouse:reservations:hold` |

```
whb_reservations (
  id, company_id, owner_id, item_id, location_id, lot_id, serial_id, lpn_id, stock_status_code,
  quantity, base_quantity, uom_code,
  holder_system         VARCHAR(40)  NOT NULL,
  holder_document_type  VARCHAR(40)  NOT NULL,
  holder_document_id    VARCHAR(100) NOT NULL,
  holder_line_no        INTEGER      NULL,
  reservation_type      VARCHAR(20)  NOT NULL,   -- SOFT | HARD
  priority              INTEGER,
  strategy_code         VARCHAR(40),             -- FR-173: why this stock was chosen
  expires_at            TIMESTAMPTZ  NULL,
  released_at           TIMESTAMPTZ  NULL,
  release_reason_code_id UUID        NULL,
  created_by, created_at
)
```

## 5.4 Lifecycle rules

> **`PC-52`** · **`released_at`, never a `DELETE`.** Released rows stay forever as audit history, and
> exclusivity is enforced by a **partial unique index**, not by application logic. This is the repo's
> own best occupancy model and it should be copied rather than redesigned:
> `dealer/backend/src/main/resources/db/migration/V20735__create_pdi_storage_slot_assignments.sql`
> — the released-rows-stay comment at `:8`, and two partial unique indexes at `:56-58`
> (`WHERE released_at IS NULL AND slot_index IS NOT NULL`) and `:61-63`
> (`WHERE released_at IS NULL`), with occupancy **derived at read time** rather than cached
> (`dealer/backend/src/main/java/ai/dealer/service/PdiYardStorageLocationService.java:65-70`). *(`FR-093`, `C-033`.)*

> **`PC-53`** · **A partial unique index cannot be `DEFERRABLE` in PostgreSQL**, so the write path
> owes an explicit `flush()` before it relies on the constraint. Recorded because it is a real
> obligation on the implementer, not a note (`G-042`, `R1 :468`).

> **`PC-54`** · **Reservations expire.** A scheduled job releases them, notifies the holder, writes a
> movement-free audit row and feeds an ageing report. A part held against an abandoned estimate is
> **invisible dead stock**. *(`FR-170`.)* Expiry emits `stock.reservation.released` on the outbox so
> the holder learns of it without polling.

> **`PC-55`** · **De-allocation on cancel is deterministic and reason-coded**, and has a stated
> acceptance test: **allocate ten, cancel, and availability returns to exactly its pre-allocation
> value**. *(`FR-171`.)*

> **`PC-56`** · The **rule and strategy that chose the stock are recorded on the reservation row**
> and shown on its detail view. *"Why did the system pick lot B when lot A expires sooner"* is asked
> weekly. *(`FR-173`.)*

---

# 6 · The external-reference registries

## 6.1 The shape, and the precedent it is copied from

Three tables: **`whb_item_external_refs`**, **`whb_location_external_refs`**,
**`whb_counterparty_external_refs`**. All three copy one live, self-documenting precedent —
`acc_company_external_refs`, at
`accounting-base/backend/src/main/resources/db/migration/V600001__Create_acc_companies_and_external_refs.sql:204-229`.

The precedent states the rule in its own comment, and it is the rule this whole section rests on:

> *"`source_module` is an OPAQUE STRING here, not an FK. `acc_source_modules(code)` is created at
> V600100 (ACB-32), 99 versions LATER, and a low-numbered file may not depend on anything a
> higher-numbered file creates (§7.7): on a fresh ascending install the FK would abort Flyway."*
> — `V600001…:193-195`

and its header states the design intent:

> *"an automotive/dealer/services company is LINKED here, never copied. In a standalone install this
> table is empty and everything still works"* — `V600001…:189-191`

```
whb_item_external_refs (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id        UUID         NOT NULL,
  source_module  VARCHAR(30)  NOT NULL,     -- OPAQUE STRING. 'ACCESSORIES', 'DEALER', 'SERVICES', …
  external_id    VARCHAR(100) NOT NULL,     -- a code, or a UUID rendered as text (36 chars)
  external_label VARCHAR(255) NULL,         -- what the producer calls it, for display
  is_active, status, version, created_at, updated_at, created_by, updated_by,
  CONSTRAINT uk_whb_item_external_refs_source_external UNIQUE (source_module, external_id),
  CONSTRAINT fk_whb_item_external_refs_item FOREIGN KEY (item_id)
      REFERENCES whb_items (id) ON DELETE RESTRICT
)
```

> **`PC-57`** · `uk(source_module, external_id)` — **map, not mirror.** One external identity resolves
> to **at most one** warehouse row. Both members are `NOT NULL`, so the key needs no
> `NULLS NOT DISTINCT` (the precedent says so at `:201-203`).

> **`PC-58`** · **No index on the parent id.** The precedent states why at `:231-233`: the query the
> table exists to serve is *"which warehouse item is source X's item Y"*, which
> `uk(source_module, external_id)` seeks directly. An index on `item_id` is write cost for a query
> nobody makes.

> **`PC-59`** · **`source_module` is never a foreign key**, even after `whb_source_systems` exists.
> The base-band migration that creates the xref tables must not depend on a higher-numbered file
> (the exact hazard the precedent names), and more importantly: an adapter must be able to register
> a mapping row **without base learning that the adapter exists**.

## 6.2 What each one is for

| Table | Joins | Primary consumer |
|---|---|---|
| `whb_item_external_refs` | a warehouse item ↔ a producer's own part number, material code, OEM number, marketplace SKU | every adapter; `PC-10`'s fourth identifier |
| `whb_location_external_refs` | a warehouse location ↔ a producer's own place identity | **the vehicle's dual identity** — §6.3 |
| `whb_counterparty_external_refs` | a thin warehouse counterparty ↔ an automotive customer, an `asset_vendors` row, a future `SC` supplier profile | inbound receiving, RTV, job work |

## 6.3 The two that are load-bearing for a non-obvious reason

### (a) `whb_location_external_refs` — the vehicle's dual identity

> **`PC-60`** · A truck is **two rows**, and **neither is the other's master**:
> - `whb_locations (location_type = 'VEHICLE', is_mobile = true)`, its driver the current `CUSTODIAN`
>   row of `whb_location_user_assignments` (`RG-004`) — so
>   stock can **sit on it**, be **counted on it**, and be **short-picked from it**;
> - `log_vehicles` — so it can have a registration, an **insurance expiry**, a tyre and an odometer.
>
> They are joined **through `whb_location_external_refs`, never by a foreign key**. *(`FR-090`,
> `FR-339`, `G-017`.)*

**Why only this works.** There are exactly three ways to let stock sit on a truck, and R7 `G-017`
enumerates them:

| Option | Consequence |
|---|---|
| (a) `whb_locations.vehicle_id` FK into logistics | **base depends on logistics — fatal.** `warehouse-base` becomes undeployable without a module that ships two versions later |
| (b) logistics duplicates the location tree | **two location truths**, and a permanent synchronisation problem with no arbiter |
| (c) an external-refs table | **the only one that survives.** Delete logistics: locations remain and xrefs resolve to null. Delete warehouse: `log_vehicles` has no FK into `whb_*` |

Retrofitting means **every historic van-stock location has an unresolvable identity** — and van stock
(`T-080`) is the same object as a delivery vehicle's load, so the whole last-mile capability is built
on this one table. The generalised rule (R7 §2.4) is `PC-03`'s deletion test: **the physical thing
has exactly one row per question it answers; the rows are joined by an external-refs table, never by
a foreign key, and neither side may require the other to exist.** The same rule decides the **tyre**
(stock serial ↔ `log_tyre_fitments`) and the **hub** (`whb_warehouses` ↔ `log_hubs`).

### (b) `whb_item_external_refs` — the `ACCESSORIES` cross-map

> **`PC-61`** · `whb_item_external_refs` carries an **`ACCESSORIES` `source_module` row for every
> dual-stocked SKU**, in v1, mandatory. *(`D-9` mitigation 1, `FR-368`.)*

**Why, and it is the honest part of `D-9`.** `accessories` keeps its own inventory permanently and is
**explicitly not an adapter** (§9.8). The counted cost is 17 tables, 71 backend files, ~12 web routes,
11 reports, 33 mobile screens, 25+ filter scopes and 12 permission resources duplicated
(`R1 C-032`, `FR-370`). But the load-bearing cost is different from all of those: **the same physical
unit counted in both systems is not merely unmitigated but *undetectable*.**

The cross-map is what makes it **detectable**. `uk(source_module, external_id)` means an accessories
part number resolves to at most one warehouse item, so a scheduled reconciliation report can name
every part number present in both **with stock in both** (`FR-369`). It is a detection control, not a
prevention control, and the difference is stated rather than hidden.

> **`PC-62`** · The mitigation is a **cross-map plus a category-ownership rule recorded as data** —
> for any item category, exactly one of the two systems is the stocking system of record — **not a
> union view**. A union view over `accessory_stock_levels` would be a **compile-time dependency**
> (the accessories reports read that table directly via `StockLevelRepository`, `R1 §5.1`), which is
> exactly the coupling the separation exists to avoid. *(`FR-369`, `G-051`.)* **Note:** R3 `M3`/`E-084`
> argues the opposite — a union valuation report tagged by `source_system`. `IRREVERSIBLE.md` §7.2
> records that this conflict is **unresolved** and is a product decision needing an `OD-` row. This
> contract follows R7 because a union view is the option that creates a module dependency; if the
> `OD-` decision goes the other way, only §6.3(b) changes, and no schema does.

---

# 7 · The thirteen open catalogues

## 7.1 The shape, seeded once

> **`PC-63`** · **Every extensible vocabulary is a catalogue table with no `CHECK` constraint, no
> Java enum, and no TypeScript string union that re-closes on the frontend what the backend opened.**
> *(`D-10`, `FR-375`, `FR-376`.)*

```
<name> (
  id, [company_id],
  code           VARCHAR(40)  NOT NULL,               -- NO CHECK CONSTRAINT, EVER
  name           VARCHAR(255) NOT NULL,
  owning_module  VARCHAR(30)  NOT NULL,               -- OPAQUE STRING, NOT AN FK
  is_system      BOOLEAN      NOT NULL DEFAULT false, -- system rows are undeletable
  sort_order     INTEGER      NOT NULL DEFAULT 0,
  <behaviour columns: typed booleans / small closed sets describing HOW the row behaves>,
  is_active, status, version, created_at, updated_at, created_by, updated_by,
  uk(code) or uk(company_id, code)
)
```

**The precedent that works, verbatim from the migration that does it right:**

> *"`context` carries NO CHECK constraint, deliberately. It is a CATALOGUE, not an enum: p1-20 adds
> an ORDER_SHORT_CLOSE context and p2-10 an interest-waiver context, and both must be a seed INSERT
> rather than an ALTER of a CHECK in accounting-base."*
> — `accounting-base/backend/src/main/resources/db/migration/V600002__Create_acc_reason_codes.sql:22-26`

**The counter-precedent, equally live.** `widget_definitions.chk_module` has been widened by
DROP/ADD **three times** — `platform/…/V234__Create_dashboard_system_tables.sql:36` → `V276:10` →
`V557:18` — and **still admits neither `warehouse` nor `logistics`**. Same story for
`global_settings.chk_global_setting_module` (`V337:42` → `V553:15`). And the prior warehouse product
broke on exactly this: `location_type` / `zone_type` CHECKs *"dropped and recreated with completely
different enum value sets"* 36 versions after creation (R6, `WAREHOUSE_CORE_ISSUES.md:DB-1`).

> **`PC-64`** · Where a **platform** `CHECK` must be widened anyway, the migration **reads
> `pg_get_constraintdef`, `regexp_matches` every quoted literal already allowed, `array_append`s the
> new one and rebuilds** — never a hardcoded DROP/ADD, which **silently discards another module's
> value**. The idiom is live at
> `accounting-base/…/V600200__Allow_accounting_in_platform_module_check_constraints.sql:55-95`.
> *(`FR-377`, `G-053`.)*

## 7.2 The thirteen

| # | Vocabulary | Table | Behaviour columns — what makes it a table rather than a list | Who may `INSERT` |
|---|---|---|---|---|
| 1 | **Movement type** | `whb_movement_types` | `direction`, `is_financial`, `cost_basis_default`, `reversal_type_code`, `requires_approval`, `requires_reason`, `affects_availability`, `is_stock_bearing`, `balance_rule`, `allows_mixed_owner`, `default_stock_status_code`, `billable_event_code` | any module |
| 2 | **Document / reference type** | `whb_document_types` | `owning_module`, `display_resolver_bean`, `is_stock_bearing`, `is_external` | any |
| 3 | **Source system / adapter id** | `whb_source_systems` | `module`, `is_reserved`, `is_claimable`, `post_permission` | **one row per module, by its own migration** |
| 4 | **Stock status** | `whb_stock_statuses` | `is_on_hand`, `is_available_to_promise`, `is_allocatable`, `is_pickable`, `is_shippable`, `is_countable`, `is_valued`, `is_owned_asset`, `blocks_shipment`, `requires_reason_to_enter`/`_to_leave`, `badge_variant` | any |
| 5 | **Location type** | `whb_location_types` | `is_physical`, `is_stock_holding`, `is_virtual_counterparty`, `is_mobile`, `is_transit`, `allows_mixed_owner`, `requires_assigned_user`, `is_pickable`, `is_receivable`, `counts_as_on_hand` | any |
| 6 | **Reason code + context** | `whb_reason_codes` | `context` (**no CHECK**, `V600002:21-25` verbatim), `requires_note`, `owning_module`, `blocks_posting`; keyed `uk(context, code)` (`V500004`, `RL-003`) | any |
| 7 | **UoM class + UoM** | `whb_uom_classes` + `whb_uoms` + `whb_uom_conversions` | `is_base_for_class`, `decimal_places`, `unece_rec20_code`, `gst_uqc_code` | any |
| 8 | **Task type** | `whb_task_types` | `owning_module`, `is_directed`, `default_priority`, `interleavable`, `labour_standard_minutes` | any |
| 9 | **Owner type** | `whb_owner_types` | `is_house`, `posts_to_our_gl`, `default_cost_basis` | any |
| 10 | **Item type** | `whb_item_types` | `is_stocked`, `is_serial_default`, `is_lot_default`, `is_returnable_equipment`, `is_asset_shaped`, `is_value_only` | any |
| 11 | **Counterparty role** | `whb_counterparty_roles` + `whb_counterparty_role_links` | link row carries `is_primary`, `valid_from`, `valid_to` | any |
| 12 | **Disposition** | `whb_dispositions` | `movement_type_code`, `target_stock_status_code`, `requires_inspection`, `emits_credit_signal` | any |
| 13 | **Attribute key** | `whb_attribute_keys` | `value_type`, `owning_module`, `is_filterable`, `is_exportable` | any |

**Thirteen, not six.** Accounting's round-4 review found six closed vocabularies in its base. A
warehouse has more axes than a ledger, and each of the thirteen is a place a future consumer must
extend: **logistics** needs #1, #2, #3, #5, #6, #10; a **supply-chain** module needs #2, #6, #11; a
**3PL** needs #4, #9, #12; an **EDI adapter** needs #13. *(R7 §5.2.)*

**Two divergences this contract carries, both argued by R7:**

- **`G-057` — counterparty role is a link table, not `partner_type ENUM`.** R2 `T-040` proposes the
  enum. Three concrete reasons to diverge: (1) the same legal entity is routinely **two roles at
  once** — a carrier who also supplies tyres, a customer who is also a job worker — and an enum
  forces two rows and two codes for one GSTIN; (2) `logistics` needs `TRANSPORTER` and `CONSIGNEE`
  and `warehouse-3pl` needs `CLIENT_3PL`, so the enum needs an `ALTER` per consumer; (3) the
  evidence that four values is not enough is already in the repo —
  `assets/…/V60056__…:3-38` gives `asset_vendors.vendor_type` **six** values and still would not
  cover a carrier. R2's table-name intent and its *"populated by adapters, do not FK into dealer or
  accessories"* rule are both retained. *(`FR-117`.)*
- **`G-060` — `item_type` is a registry row, not an enum.** R3 `E-007` proposes seven fixed values.
  Four more arrive with **logistics alone** — `RETURNABLE_EQUIPMENT`, `TYRE`, `FUEL`, `PACKAGING` —
  and R4 `F-060` adds packaging independently. **Seven values chosen before the second consumer
  exists is the definition of a closed vocabulary.** R3's *content* is right; only its shape changes.
  *(`FR-049`.)*

**And the reserved row that is a decision, not an omission:**

> **`PC-65`** · `whb_source_systems` carries an **`ACCESSORIES` row with `is_reserved = true,
> is_claimable = false`** and a column comment naming `D-9`. *(`G-052`, `FR-367`.)* Omitting the
> string invites a future author to claim it, or a well-meaning agent to "complete" the adapter set.
> A reserved row explains itself. Asserted by the coupling test (§8.4, assertion 6).

## 7.3 How a consumer adds a value without a base release

> **`PC-66`** · A consumer adds a catalogue value by a **seed `INSERT` from its own migration, in its
> own Flyway sub-band, individually idempotent**. No `ALTER`, no base commit, no coordination.
> *(`FR-356`, `G-043`.)* Every registry is one install-wide namespace, so two rules make that safe
> *(`RL-003`)*:
>
> 1. **A module inserts only codes it owns.** To *use* a code another module seeded — base's
>    `TRANSFER_DEPART`, say — it references the code and never re-inserts it. A re-insert under
>    `ON CONFLICT DO NOTHING` keeps the first writer's row and silently discards the second writer's
>    behaviour flags, and the second module then posts under the first module's `is_financial` and
>    `reversal_type_code`.
> 2. **The seed is guarded.** `ON CONFLICT (<key>) DO NOTHING` is followed by a `DO $$ … $$` block
>    that raises if any code the migration seeds exists under another `owning_module`, in the
>    verification shape of `accounting-base/…/V600200__Allow_accounting_in_platform_module_check_constraints.sql:150-161`.
>    It stays idempotent for the owner and fails loudly for anyone else. Reason codes key on
>    `(context, code)`, so their conflict target is `(context, code)`. Install-created rows carry
>    `owning_module = 'INSTALL'` (`RL-012`). `PC-72` assertion 7 catches the same collision in the
>    reactor, before any install runs.
>
> **Idempotency per statement is not optional here.** `R1 C-047`: any Flyway failure in this codebase
> triggers a **blind `repair()` plus one retry** (`FlywayConfiguration.java:246-264`), so a migration
> that is not individually idempotent will be partially re-run.

The adapter sub-bands are pre-allocated so parallel work cannot collide — dealer `V520000–520999`,
services `V521000–521999`, field-service `V522000–522999`, assets `V523000–523999`, **logistics
`V524000–524999`** — all inside `warehouse-adapter-*`'s `V520000–V529999` band (`D-2`, `G-043`).
**No task in this design set writes a number inside the logistics sub-band** (`H-006`): the reservation
exists so the `logistics` design set can number its own registration migration, and the example below
is written **from that module's repository**, not from this one. `IMPLEMENTATION-PLAN.md` §11 records
the withdrawal of `P6-08`'s former `V524000`–`V524099` claim.

**Worked example — the whole cost of a logistics module learning to move stock.** Base's v1 seed
already carries the transfer and transit-loss movement types, the `TRIP`/`MANIFEST`/`CONSIGNMENT`
document types and the `LOGISTICS` source-system row (`IRREVERSIBLE.md` §2 rows 1–3, `P0-04`). Under
`PC-66` rule 1 logistics references those and inserts only what it alone owns. *(Corrected in round 4:
the earlier version re-inserted all three base movement types under `owning_module = 'logistics'`,
and `DO NOTHING` discarded every one of its values without a word — `RL-003`.)*

```sql
-- logistics/backend/src/main/resources/db/migration/V524001__Register_logistics_with_warehouse.sql
-- References, never re-inserts, base's v1 seed (IRREVERSIBLE.md §2 rows 1-3):
--   whb_source_systems  LOGISTICS
--   whb_document_types  TRIP, MANIFEST, CONSIGNMENT
--   whb_movement_types  TRANSFER_DEPART, TRANSFER_ARRIVE, TRANSIT_LOSS
-- Inserts only the codes logistics owns.

INSERT INTO whb_movement_types (code, name, direction, is_financial, reversal_type_code,
                                requires_reason, balance_rule, owning_module, is_system)
VALUES ('EQUIPMENT_ISSUE',  'Equipment — issue to trip',    'INTERNAL', false, 'EQUIPMENT_ISSUE_REV',  false, 'MUST_BALANCE_PER_OWNER_ITEM', 'logistics', false),
       ('EQUIPMENT_RETURN', 'Equipment — return from trip', 'INTERNAL', false, 'EQUIPMENT_RETURN_REV', false, 'MUST_BALANCE_PER_OWNER_ITEM', 'logistics', false)
ON CONFLICT (code) DO NOTHING;

INSERT INTO whb_reason_codes (context, code, name, owning_module, requires_note, is_system)
VALUES ('TRANSIT_LOSS', 'CARRIER_DAMAGE', 'Damaged in transit by carrier', 'logistics', true, false)
ON CONFLICT (context, code) DO NOTHING;

-- PC-66 rule 2: idempotent for the owner, loud for anyone else
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM whb_movement_types
               WHERE code IN ('EQUIPMENT_ISSUE', 'EQUIPMENT_RETURN') AND owning_module <> 'logistics') THEN
        RAISE EXCEPTION 'V524001: a movement-type code logistics seeds is owned by another module';
    END IF;
    IF EXISTS (SELECT 1 FROM whb_reason_codes
               WHERE context = 'TRANSIT_LOSS' AND code = 'CARRIER_DAMAGE' AND owning_module <> 'logistics') THEN
        RAISE EXCEPTION 'V524001: reason code TRANSIT_LOSS/CARRIER_DAMAGE is owned by another module';
    END IF;
END $$;
```

**Commits to `warehouse-base` required by the above: zero.** That is the claim, and it is the thing
§8.4 measures.

## 7.4 The rule that stops the frontend re-closing what the backend opened

An open backend registry is worthless if the frontend hardcodes the list. This repo has a
**documented, recurring defect of exactly that shape** — R2 §3.2 names it: *"a status present in the
CHECK constraint but missing from the frontend union, the variant map, the filter options or the i18n
keys"*. Three rules, each checkable:

> **`PC-67`** · **No TypeScript string-union type may enumerate a registry vocabulary.** The type is
> `type MovementTypeCode = string` plus a runtime list fetched from a dropdown endpoint. String
> unions remain right for genuinely closed system vocabularies (`'ACTIVE' | 'INACTIVE'`,
> `posting_status`). *(`FR-380`.)* **The same rule holds on mobile** *(`FR-382`, v1 · P0, `P0-16`,
> `RL-009`)*: a registry-backed field in `mobile/…/common.schemas.ts` is `z.string().min(1)`
> validated against the fetched dropdown list, never a `z.enum`, and a `z.enum` literal containing a
> seeded registry code fails CI. Handhelds update on an MDM schedule, so a closed mobile enum would
> refuse every adapter's new seed row, silently, for a release cycle.

> **`PC-68`** · **`StatusBadge` variant comes from a `badge_variant` column on the registry row**, not
> from a frontend map. One less place to forget. *(`FR-381`.)*

> **`PC-69`** · **i18n falls back to the registry row's `name`** when `t('warehouse:statuses.<code>')`
> misses, so a newly registered status renders in **English rather than as a raw key**. *(`FR-381`,
> `G-065`.)* From **v2** the fallback reads `whb_registry_translations` for the user's locale
> **first**, then the row's `name` (`FR-469`, `P1-19`'s v2 increment, `RL-015`): an install-created row
> (`owning_module = 'INSTALL'`) has no i18n key at all, and its translation is the only place a
> second language can live. And every registry gets a **mobile-vocabulary consideration on day one**, because
> `mobile/…/common.schemas.ts` is a third copy of every dropdown vocabulary and a missing value makes
> the mobile save fail validation silently (`FR-382`, `G-066`).

> **`PC-70` · OPEN — `OD-5`, referred to the standards owner, recommendation attached.**
> `PC-67` knowingly diverges from **CLAUDE.md TYPESCRIPT RULES #6** (*"String union types over
> TypeScript enums"*). That rule is right for a genuinely fixed set and **wrong for a catalogue**,
> but it is a house rule and resolving a house rule inside a warehouse contract is how two review
> gates start contradicting each other.
> **Status: OPEN.** `DECISIONS.md` `OD-5` gives the deadline — *before the first warehouse page is
> written* — and names the standards owner as the decider.
> **Recommendation, attached and not applied:** catalogue-backed dropdowns fetch their values;
> string unions permitted only for closed system vocabularies. *(`G-064`.)*

---

# 8 · The adapter contract

## 8.1 What an adapter is, in one sentence

> **An adapter is a module that translates one vertical's documents into warehouse movements and
> back, owns only its own tables, and can be added or deleted without a single line changing in
> `warehouse-base`.** *(`D-11`, R7 §4.1, `FR-349`.)*

> **`PC-71`** · **The adapter package is a *sibling*** — `ai.warehouseadapter<vertical>`, **never**
> `ai.warehouse.adapter.*`. *(`D-1`, `FR-351`.)*
>
> **Why, precisely:** `@ComponentScan` matches by **package prefix**, so an adapter placed under
> `ai.warehouse` would be component-scanned and its beans loaded **unconditionally, in every install
> — including installs where the vertical is not built**. The accounting set states the same trap in
> its own words at
> `accounting/backend/src/main/java/ai/accounting/AccountingModuleConfig.java:22-25`:
> *"The dealer adapter lives in `ai.accountingadapterdealer`, a SIBLING package, never
> `ai.accounting.adapter.dealer`. The `@ComponentScan` below matches by package prefix, so an adapter
> placed under `ai.accounting` would be component-scanned and its beans loaded in an install that
> never set ENABLE_ACCOUNTING_ADAPTER_DEALER."* The adapter itself is correspondingly clean:
> `accounting-adapter-dealer/backend/src/main/java/ai/accountingadapterdealer/AccountingAdapterDealerModuleConfig.java:1-8`
> declares `package ai.accountingadapterdealer;` and imports exactly one `ai.*` type —
> `ai.platform.util.PlatformLogger`.
>
> Table prefixes are `D-3`'s and are **not** `wha_<vertical>_` as R7 §4.5 writes them: dealer
> `whad_`, services `whas_`, field-service `whaf_`, assets `whaa_` (`IRREVERSIBLE.md` §7.1).

## 8.2 What an adapter MAY do

| # | May | Mechanism |
|---|---|---|
| **A1** | Post stock movements | `POST /api/warehouse/movements`, plus the batch and reverse variants (§2.2) |
| **A2** | Simulate before promising | `POST /api/warehouse/movements/simulate` (`PC-27`) |
| **A3** | Find its own postings | `GET /movements?source_system=&source_document_type=&source_document_id=` (`FR-036`) |
| **A4** | Read balances and availability | `GET /api/warehouse/stock?…` — **never a direct table read** |
| **A5** | Hold and release a reservation | `POST` / `DELETE /api/warehouse/reservations` with a **holder quad** and a TTL (§5) |
| **A6** | Register its own **movement types, document types, reason codes and contexts, stock statuses, location types, task types, item types, dispositions, attribute keys** | rows inserted by the adapter's **own migration**, in its own Flyway sub-band (`PC-66`) |
| **A7** | Register its **source-system id** | one row in `whb_source_systems` |
| **A8** | Map its own identifiers to warehouse ones | the three tables of §6 |
| **A9** | Render its own document numbers in warehouse grids | register a `WhDocumentReferenceResolver` bean; base collects them via `List<T>` (`PC-04`) and ships a fallback (`FR-357`) |
| **A10** | Subscribe to stock events | in-process `List<WhMovementEventSubscriber>` **or** an HTTP row in `whb_outbox_subscriptions` (`PC-39`) |
| **A11** | Own tables | its own `D-3` prefix, in its own migration band |
| **A12** | Register permissions, menus, grids, filters | migration inserts — **plus one `filterUtils.ts` scope and one `CacheConfiguration` name, which are platform edits** (§8.6) |
| **A13** | Take a gapless document number | `whb_number_series`, scoped by `owning_module` (`G-044`) |

## 8.3 What an adapter MUST NOT do

| # | Must not | Why, and how it is caught |
|---|---|---|
| **B1** | `INSERT` / `UPDATE` / `DELETE` any `whb_*` or `wh_*` table | it bypasses idempotency, the balance projection and the outbox at once. Caught by the migration scanner (§8.4 assertion 2) |
| **B2** | Add a column to a base table | the second adapter wants a *different* column. Caught: no `ALTER TABLE whb_` outside the base band |
| **B3** | Create an FK **from** a base table **to** an adapter table | it makes base undeployable without the adapter, and fails `PC-03`'s deletion test. Caught by §8.4 assertion 3 |
| **B4** | Be imported by base | `import ai.warehouseadapter*`, `ai.logistics`, `ai.dealer`, `ai.services`, `ai.assets`, `ai.fieldservice`, `ai.automotive`, **`ai.accessories`**, `ai.insurance*`, `ai.submittals`, `ai.leadsharing`, `ai.productlift` anywhere under `warehouse-base/backend/src/main/java` — **the whole point.** Caught by §8.4 assertion 1 |
| **B5** | Change stock outside the port | a second write path means two balance truths — `PC-02`, and the live accessories failure it cites |
| **B6** | Define a second envelope shape or a second idempotency scheme | `PC-06`; R3 `E-003` |
| **B7** | Reuse another adapter's `source_system` code | **idempotency keys would collide retroactively** (`PC-15`) |
| **B8** | Put a `CHECK (x IN (…))` on any of the thirteen registry columns | it re-closes what base opened. Caught by §8.4 assertion 4 |
| **B9** | Read or write `accessory_stock_levels` | `E-087`; the `D-9` separation is worthless if an adapter tunnels under it |
| **B10** | Ship a screen duplicating a base grid | two grid mechanisms is how 40 grid identifiers become 80 (R4 §5.5 #9) |

## 8.4 The build-time test — three layers

**The problem this solves, stated from the evidence.** The accounting equivalent of this test **does
not exist as a test** — it exists as a comment (`AccountingModuleConfig.java:22-25`, quoted in
`PC-71`). Correct today, unenforced tomorrow. And the existing per-module ratchets do **not** cover
dependency direction: inspected
`accounting-base/backend/src/test/java/ai/accountingbase/architecture/ArchitectureInvariantsTest.java`,
whose `@DisplayName`s at `:64`, `:79`, `:121`, `:173`, `:198` and `:225` cover `@PreAuthorize`, cache
names, `PageRequest.of`, `findById`-in-a-loop and the scanner self-tests — **and nothing else.**
Computed: `find . -name ArchitectureInvariantsTest.java` → **3** files (platform 713 lines,
accounting-base 660, accounting 660).

### Layer 1 — `WarehouseBaseCouplingTest`, static, in `warehouse-base`

> **`PC-72`** · Seven assertions, and **adding a fourteenth registry means adding a row to assertion
> 4**. *(`FR-354`, R7 §4.4.)*
>
> 1. **No forbidden import.** No source file under `warehouse-base/backend/src/main/java` contains
>    `import ai.warehouse.`, `import ai.warehouseadapter`, `import ai.warehouse3pl`,
>    `import ai.warehouseindia`, `import ai.logistics`, or any vertical package (the `B4` list,
>    **including `ai.accessories`**).
> 2. **No cross-prefix reference in a base migration.** No migration in `V500000–V509999` contains
>    the token `whad_`, `whas_`, `whaf_`, `whaa_`, `wh3_`, `whin_`, `log_`, `accessory_`, `pdi_`,
>    `service_` or `asset_` inside a `REFERENCES` clause.
> 3. **Every base-band FK targets a `whb_` table or an asserted platform whitelist** (`users`,
>    `user_details`, `branches`, `documents`). **The whitelist is itself asserted**, so widening it
>    is a reviewed act rather than a diff nobody notices.
> 4. **No `CHECK (… IN (…))` on any of the thirteen registry columns of §7.2.** The test names the
>    thirteen `table.column` pairs **explicitly**.
> 5. **The scanners self-test.** Copy the shape at
>    `accounting-base/…/ArchitectureInvariantsTest.java:225-346`. The accounting copy states why at
>    `:43-57`: *"a scan that finds nothing because there is nothing to find is indistinguishable from
>    a scan that finds nothing because it is pointed at the wrong directory or its regexes are
>    broken."*
> 6. **`whb_source_systems` contains the `ACCESSORIES` row with `is_reserved = true`** and no adapter
>    claims it (`PC-65`).
> 7. **No `(registry, code)` pair is inserted by two `owning_module` values** across every
>    warehouse-family band (`D-2`), reason codes compared on `(context, code)`. `PC-66`'s guard
>    catches a collision in one install; this catches it in the reactor (`RL-003`).

### Layer 2 — `warehouse-adapter-example`, a fixture adapter in the repo

> **`PC-73`** · A real Maven module in the reactor, listed only in `all-modules` and in its own
> `with-warehouse-adapter-example` profile. **Zero screens.** It contains **exactly one of each thing
> an adapter is allowed to have**: one movement type, one document type, one row in
> `whb_source_systems`, one item external ref, one reservation with a holder quad, one
> `WhMovementEventSubscriber`, one `WhDocumentReferenceResolver`, one `whae_`-prefixed table. Its
> integration test **posts a movement, reserves, consumes, reverses and reads back — using only the
> public API of §8.2.** *(`FR-353`, `G-049`.)*
>
> **Why this is materially stronger than any grep.** If the fixture compiles and its test passes, the
> contract is **expressible**. If a real adapter needs something the fixture cannot express, that is a
> **base gap found before the base ships**, not after a customer deadline. It is the cheapest possible
> answer to R2 `T-079`'s *"the generality question is decided by the first adapter"* — because the
> first adapter is then a fixture we control.
>
> And it is why **two real adapters ship in v1**, not one: *one adapter proves nothing about
> genericity.* The port is accepted only if **neither adapter required a base-schema change the other
> did not want** (`D-11`, `FR-352`, `E-006`).

### Layer 3 — the review ratchet, and its honest caveat

> **`PC-74`** · At the commit that merges the **second** adapter:
>
> ```bash
> git log --oneline -- warehouse-base/ | wc -l   # must equal its value at the previous commit
> ```
>
> The number is recorded **in the adapter's PR description**. CI cannot see this reliably across
> rebases; a reviewer can, in one command.
>
> **The caveat, stated inside the contract because a false invariant gets ignored — taking the true
> ones with it.** *(`D-10` corollary, `G-047`, `FR-355`, `MODULE-INTEGRATION.md` §12.3.)*
>
> > **The ratchet can only ever be *zero commits to `warehouse-base`*. It can never be *zero commits
> > to `platform`*.**
>
> Because, computed on the live tree 2026-09-01:
> - `COMMON_FILTER_CONFIGS` is a TypeScript `const` beginning at
>   `platform/frontend/src/utils/filterUtils.ts:346`, and
>   `awk '/COMMON_FILTER_CONFIGS/,0' platform/frontend/src/utils/filterUtils.ts | grep -cE "^  [A-Z0-9_]+: \{"`
>   → **213 scopes**. A filter field absent from its scope is **silently dropped by
>   `convertFiltersForApi()` before the request is built** — the filter UI renders, accepts input and
>   does nothing (CLAUDE.md CRITICAL #17).
> - `CacheConfiguration.java` is platform Java;
>   `awk 'NR>101 && NR<423' platform/backend/src/main/java/ai/platform/config/CacheConfiguration.java | grep -cE '^[[:space:]]+"[a-zA-Z0-9._-]+",?$'`
>   → **234 registered names**, and `:375-376` warns in the file itself: *"An unregistered name throws
>   `IllegalArgumentException` on the FIRST call, not at startup, so it must be here."*
>
> **Every warehouse grid, in every module including every adapter, edits both files.** A contract
> claiming otherwise is false on day one.

## 8.5 The lifecycle of an adapter

| Step | What happens | Gate |
|---|---|---|
| 1 | Module skeleton — sibling package, own Flyway sub-band, own `D-3` prefix, own `ArchitectureInvariantsTest` (an **edit**, not a copy: package root, **empty** baselines, `ScannerIntegrity` replacing platform's `> 500` vacuity guard — `MODULE-INTEGRATION.md` §13.3) | build |
| 2 | Register: one `whb_source_systems` row; its movement types, document types, reason codes; its permissions and `permission_dependencies` rows; its menus (**guarded by `WHERE NOT EXISTS`**, because the menu table has no unique key on the natural key and a Flyway retry duplicates the row — `FR-410`) | migration |
| 3 | Map identities into the three xref tables | migration or runtime |
| 4 | Implement translation: vertical document → movement envelope; register a `WhDocumentReferenceResolver` | code |
| 5 | Screens, grids, filters, i18n for **all three locales** (`accounting-base` ships `{en,fr,hi}` — `R1 AF-2`), mobile counterpart (`D-13`) | review |
| 6 | Prove it: `WarehouseBaseCouplingTest` green, fixture green, `git log -- warehouse-base/` unchanged, number in the PR | `PC-72`…`PC-74` |
| **Deletion** | Remove the module and its profile. Its `whb_*` registry rows **stay** (they are `is_system = false` data referenced by posted history); its xref rows resolve to null; the display resolver falls back. **Base does not change.** | `PC-03` |

## 8.6 The registration surface — the complete list

Every one of these is an **edit an adapter author must make**, and three of them are outside the
adapter's own directory. Naming them here is what stops "loose coupling" from being discovered as a
half-truth during the first adapter.

| Surface | Where | Inside the adapter? |
|---|---|---|
| Permissions + `permission_dependencies` rows | adapter migration; **rows only, never `CREATE TABLE`** (`PC-31`) | yes |
| Menus | adapter migration, `WHERE NOT EXISTS`-guarded | yes |
| Grid columns | `grid_column_definitions` | yes |
| Grid filters | **`filter_definitions`** — *not* `grid_filter_definitions` (`PC-48`) | yes |
| Grid defaults | `grid_preferences.default_filters` **and** `default_columns`, both populated, both `'[…]'::jsonb` | yes |
| **Filter allowlist scope** | `platform/frontend/src/utils/filterUtils.ts` `COMMON_FILTER_CONFIGS` | **NO — platform edit** |
| **Cache names** | `platform/…/config/CacheConfiguration.java` — `dropdown.warehouse.<entity>`. **Not** a `statistics.*` name for a **filter-aware** strip: `:191-196` records that exact mistake (issues #790, #791), and warehouse strips are filter-aware by design | **NO — platform edit** |
| i18n | the module's own SafeTranslation file, **all three locales** | yes |
| **CI ratchet job** | `.github/workflows/tests.yml` | **NO — repo edit**, §8.7 |

## 8.7 Making the ratchet actually run

Copying the accounting ratchet is not enough; it has to be **in a job that can fail the build**.

**The evidence.** `.github/workflows/tests.yml:97` and `:201` carry `continue-on-error: true` on the
frontend and backend test steps, because both suites are red. **A ratchet inside either job enforces
nothing.** Accounting's answer is a **separate, blocking job**, and the file says so in its own words
at `:240-241`: *"A ratchet that runs behind `continue-on-error` enforces nothing, so this job does
not have it."* The `accounting-ratchets` job begins at `:259` and carries **no**
`continue-on-error` — verified: `grep -n "continue-on-error" .github/workflows/tests.yml` returns
`17, 24, 28, 32, 35, 97, 106, 201, 241, 308, 413`, and the only two live step-level uses are `:97`
and `:201`, both inside the two non-blocking jobs.

Three shapes must be copied, not paraphrased:

1. **The two-step build.** `:300-306` runs `-am … -Dmaven.test.skip=true install` so `-am` drags
   `platform/backend` into the reactor **without running its red suite**; `:308-321` then drops `-am`
   so surefire runs **only** in the selected modules. The comment at `:308-315` states why.
2. **The anti-vacuous assertion.** `:334` *"Assert the ratchets actually executed"*, with the
   non-obvious rule at `:323-333` preserved verbatim: surefire 3.2.2 writes **one XML per `@Nested`
   class** (`TEST-<FQCN>$<Nested>.xml`) and the plain `TEST-<FQCN>.xml` is either absent or has
   `tests="0"`, *"so checking the plain file alone fails a GREEN build in both directions. Sum the
   whole family instead."*
3. **The `ScannerIntegrity` existence check** at `:368-377`, per module — it is what makes an empty
   module unable to pass vacuously. **Keep the nested class named `ScannerIntegrity` in every
   warehouse copy**; the workflow hardcodes the name in a shell string at `:372` and, at `:375`,
   prints *"If the nested class was renamed, update this check to match."*

**What must change for a warehouse ratchet to actually run:**

- a `warehouse-ratchets` job, copied from `tests.yml:259-408`, re-scoped to `-Pwith-warehouse` and
  `-pl warehouse-base/backend,warehouse/backend,warehouse-adapter-dealer/backend,warehouse-adapter-services/backend`
  (adding `warehouse-3pl/backend,warehouse-india/backend` at v2), **without** `continue-on-error`,
  with one `dir:prefix` pair per warehouse module in the assertion step;
- a **blocking** Jest step inside the existing `frontend` job, copied from `:123-128`, with
  `--passWithNoTests` (required — "no tests found" is a non-zero exit in Jest and the trees are empty
  on day one) and a `--testPathPattern` regex whose alternation covers **every** warehouse module,
  or one tree is matched and the others silently missed;
- `warehouse-ratchets` runs on every PR the day it lands; failure is visible, not merge-blocking (required-check setting waived — branch protection unavailable on the current GitHub plan; added to the **required status checks** if the plan ever allows).

**Scoping is what makes this safe** — `:255-257`: *"Scoping the gate to
`-pl accounting-base/backend,accounting/backend` means nothing outside those two directories can turn
this job red. The two jobs above are untouched, so no existing module's CI behaviour changes."* The
same holds for warehouse.

---

# 9 · The concrete consumers, defined now

Defined **now**, per `D-12`: nothing is left to "we'll look at it later". Each subsection says what
the consumer posts, which types and document types it needs, which catalogue rows it seeds, what it
reads, and its version.

## 9.1 `warehouse-adapter-dealer` — spare parts · **v1**

| | |
|---|---|
| **Maps** | parts counter sale, workshop parts request, OEM order, core return |
| **Posts** | `SALE_ISSUE`, `COUNTER_RETURN`, `CORE_RECEIVED`, `RTV_OEM` |
| **Document types** | `PARTS_INVOICE`, `WORKSHOP_REQUEST`, `OEM_ORDER`, `CORE_RETURN` |
| **Catalogue rows** | `whb_source_systems`: `ADAPTER_DEALER` · `whb_stock_statuses`: `CORE_UNGRADED` · `whb_item_types`: `CORE` · reason codes for core grading |
| **Own tables** | `whad_part_issues`, `whad_core_links`, `whad_part_supersessions` |
| **Reads** | balances and availability via API; the automotive model master for **fitment** — which lives **in the adapter, never in base** (`FR-074`: *if base learns about vehicles it cannot serve assets, field-service or logistics*) |
| **Xrefs** | `whb_item_external_refs` with `source_module = 'DEALER'` for the dealer's own part numbers |
| **Version** | **v1** — it is the adapter that proves the port |

## 9.2 `warehouse-adapter-services` — job-card parts · **v1**

| | |
|---|---|
| **Maps** | job card / `service_entries` parts lines |
| **Posts** | `ISSUE_TO_JOB`, `JOB_PART_RETURN` |
| **Document types** | `JOB_CARD` |
| **Catalogue rows** | `whb_source_systems`: `ADAPTER_SERVICES` · reason codes for job return |
| **Own tables** | `whas_job_part_issues` |
| **Reads** | availability, for *"can I promise this part today"* (`FR-174`) |
| **Version** | **v1**, and it is the **largest consumer** |
| **Note** | `services` has **no parts table today** — a clean sheet. `services.parts_used` is free `TEXT` (`services/…/V40095__Change_parts_used_from_jsonb_to_text.sql`). Material request → reservation before it is an order → issue in parts as the job progresses → **return to store crediting the job** → the warranty split (`FR-360`). **Parts issued to open jobs are neither stock nor cost of sale** and report as WIP at every month end (`FR-361`) |

**Why it is in v1 and not v1.1:** *one adapter proves nothing about genericity* (`D-11`, `E-006`).
The dealer adapter and the services adapter must both land without either forcing a base-schema
change the other did not want. That is the whole acceptance test for the port.

## 9.3 `warehouse-adapter-field-service` — van stock · **v1.1**

| | |
|---|---|
| **Maps** | `service_jobs`, `job_trips` |
| **Posts** | `VAN_REPLENISH`, `ISSUE_AT_SITE`, `VAN_RETURN` |
| **Catalogue rows** | `whb_source_systems`: `ADAPTER_FIELD_SERVICE` · `whb_location_types`: uses **`MOBILE`** |
| **Own tables** | `whaf_van_stock_assignments` |
| **Reads** | the van's current location — `job_trips` already knows it (`field-service/…/V80007__Create_job_trips_and_track_points.sql:13-48`) |
| **Base columns it depends on** | the current `CUSTODIAN` row of `whb_location_user_assignments` (`RG-004`) + the `MOBILE` location type — **v1**, feature v1.1. Without them van stock becomes a separate table and a separate reconciliation problem (`FR-088`, `T-080`, R7 §6 item 13) |
| **Version** | **v1.1** |

The van is a `whb_locations` row with `location_type = 'MOBILE'`, its technician the current
`CUSTODIAN` row of `whb_location_user_assignments` (`RG-004`). Replenished by a transfer, consumed at job close, cycle-counted,
and its unreturned parts age (`FR-363`).

## 9.4 `warehouse-adapter-assets` — spares · **v1.1**

| | |
|---|---|
| **Maps** | `asset_complaints` resolution, `asset_po_receipts` |
| **Posts** | `ISSUE_TO_ASSET`, `SPARE_RETURN` |
| **Own tables** | `whaa_spare_consumptions` |
| **Xrefs** | `whb_counterparty_external_refs` — assets has the **vendor master warehouse lacks** (`asset_vendors`, `assets/…/V60056__…:3-38`), mapped rather than copied |
| **Boundary, stated** | **warehouse owns the item until issue; the assets module owns it after capitalisation; the hand-off is an event carrying the serial** (`FR-364`) |
| **Version** | **v1.1** |
| **Note** | `asset_po_receipts` receives **assets, not stock** — a model to extend, not reuse (`R1 §6`) |

## 9.5 `warehouse-3pl` · **v2**

Not an adapter — a **module** that depends on base **and** app, with **neither depending on it**
(`FR-281`). It consumes the port and the outbox rather than extending them.

| | |
|---|---|
| **Consumes** | the outbox at **billable granularity** (`PC-42`) — `pick.line.confirmed`, `carton.packed`, `receipt.line.confirmed`, `task.completed` |
| **Own tables** | `wh3_billable_events`, `wh3_rate_cards`, `wh3_charge_codes`, `wh3_billing_runs`, `wh3_storage_snapshots` |
| **Catalogue rows** | `whb_owner_types`: `CLIENT_3PL` · `whb_dispositions`: `RETURN_TO_CLIENT`, `HOLD_FOR_CLIENT` · `whb_stock_statuses` as its contracts need |
| **Base concessions it stands on — all v1, all unavoidable** | `owner_id NOT NULL` per line (`D-5`) · `whb_lpns.received_at` (anniversary storage) · billable-granularity events · `cost_basis` including `ZERO_BAILMENT` · owner-scoped access |
| **Version** | **v2** |

> **The honest framing (R4 §5.3):** `warehouse-3pl` is a **thin module standing on a wide base
> concession**, and **the concession is not optional, not deferrable and not flaggable**. A feature
> flag would not save a single column, because the unaddable items are in `warehouse-base` and are
> required whether or not anyone ever buys 3PL. And: **movements whose `owner_type != OWN` are handed
> over for quantity and custody reporting only, and are never valued** (`L-14`, `FR-112`) — a 3PL
> that posts its clients' stock to its own balance sheet has a catastrophe in both directions.

## 9.6 `warehouse-india` · **v1 (documents) + v2 (registers)**

Splits in two waves per `DECISIONS.md` §5.1 `A-4`. It consumes **only** base columns that already
exist — `company_id`, `duty_status`, `tax_classification_code`, `whb_uoms.gst_uqc_code`, the reason-code catalogue —
and adds **no** base column.

| Wave | Contents |
|---|---|
| **v1 / P2-IN** | the documents required to **move goods legally**: delivery challan, e-way bill payload and generation, the GST-aware transfer document, HSN on the item, cross-GSTIN transfer as a supply |
| **v2 / P4** | the statutory registers and filings: Rule 56 stock account, ITC-04 and job work, MRP & Legal Metrology, bonded/MOOWR, the regulated-goods packs |

**Why the v1 wave exists:** in India goods physically cannot move between branches without a challan
and an e-way bill, so a v1 that ships transfers but no challan ships *a transfer feature an Indian
customer may not legally use*. **This does not weaken `D-8`** — the core stays country-neutral; the
hooks (`company_id`, `duty_status`, `gst_uqc_code`, `tax_classification_code`, registry-backed reason codes) are in
v1 **because they cannot be added later**, and every rule is in `warehouse-india`.

## 9.7 The future `logistics` module · **v2 posting, v3 optimisation**

> **`PC-33` note aside, this is the consumer the whole contract is a test for.**

| | |
|---|---|
| **Posts** | `TRANSFER_DEPART`, `TRANSFER_ARRIVE`, `TRANSIT_LOSS`, `EQUIPMENT_ISSUE`, `EQUIPMENT_RETURN`, `ISSUE_TO_ASSET` / `RETURN_FROM_ASSET` (tyre fitment), `LANDED_COST_APPLY` |
| **Document types** | `TRIP`, `MANIFEST`, `CONSIGNMENT` |
| **Catalogue rows** | `whb_source_systems`: `LOGISTICS` · `whb_location_types`: uses `IN_TRANSIT`, `VEHICLE`, `TRAILER`, `MOBILE` · `whb_item_types`: uses `RETURNABLE_EQUIPMENT`, `TYRE`, `FUEL`, `PACKAGING` · reason codes in a `TRANSIT_LOSS` context |
| **Own tables** | `log_*` — trips, stops, legs, consignments, vehicles, drivers, fuel, maintenance, freight, PODs, GPS pings |
| **Reads** | the lineage query, availability, `whb_lpns` for load planning, `wh_dock_appointments` |
| **Adapter?** | **No.** It **posts directly.** *(`FR-366`, `G-048`)* — an adapter exists to translate a vertical that does not know about warehouse; `logistics` is a first-class module of our own that can be built knowing the port, and *an adapter between two of our own modules is a layer with no translation in it.* Recorded so a later reviewer does not "discover" the missing adapter |
| **Flyway** | `V524000–V524999`, **reserved in v1**, along with the `log_` prefix and the `logistics:*` permission namespace (`FR-346`, `FR-407`) |
| **Version** | **v2** — the module; **v3** — optimisation, telematics, control tower, spot bidding |

**In-transit stock is the whole seam** (`FR-335`, R4 §4.3). A transfer is **at least two** movements:

```
TRANSFER_DEPART   A/PICK_FACE          (−)  →  A/IN_TRANSIT-<trip>  (+)
TRANSFER_ARRIVE   A/IN_TRANSIT-<trip>  (−)  →  B/RECEIVING          (+)
```

The transit location is a per-transfer `IN_TRANSIT` child of the **source** site A, created at
dispatch — never a separate transit warehouse (`FR-147`, `FR-148`, `GAP-REGISTER-R4.md` §3.4). In-transit
value stays in the sender's grain (`FR-236`), and classification resolves to A's `REGISTERED` link,
which is the transfer's frozen source branch. B's storekeeper posts the arrive leg against **that**
transfer's transit location regardless of site scope, and against nothing else at A (`P1-18`,
`RJ-002`). Both legs carry `source_document_type = 'TRIP'` and the trip id, so logistics finds its own postings
through `A3` **without base knowing what a trip is**. Three consequences fall out, and all three are
things customers ask for: **in-transit stock is countable and reportable**; **a transit loss is a
normal reason-coded adjustment** against the transit location, which is what makes it claimable
against the carrier; and **a partial arrival is representable** — twelve of fifteen cartons arrive,
three stay in transit and age, and nobody has to decide whether B "received" fifteen.

The v1 cost of supporting this before logistics exists is **one `location_type` value
(`IN_TRANSIT`, seeded by `P1-05`), one transit location created per transfer at the source site,
and a transfer service that posts two movements instead of one.** The v2 cost of adding it afterwards is that **every historic transfer is a single movement
with no transit state**, in-transit ageing is unanswerable for the past, and every transfer report in
the product changes shape.

**And the correction R4 §4.4 needs** (`G-019`, `FR-342`): *"delivery is not a movement"* is **true for
a customer and false for our own branch**. Delivery to a customer posts nothing — the stock left at
despatch. Delivery to **our own branch posts `TRANSFER_ARRIVE`**, and a partial arrival is fewer
lines. Delivery to a 3PL client's site is `OWNER_CHANGE` or `TRANSFER_ARRIVE` depending on the
contract. An implementer who reads only *"delivery is not a movement"* builds inter-branch transfers
that depart and never arrive.

## 9.8 `accessories` — **never an adapter**, and what that means for the registry

**User decision, `D-9`, taken 2026-09-01.** Four concrete consequences, none of which is "do nothing":

1. **`whb_source_systems` gets an `ACCESSORIES` row with `is_reserved = true, is_claimable = false`**
   and a column comment naming the decision (`PC-65`). The string is **reserved so nobody claims it
   and nobody "completes" the adapter set**. Asserted by §8.4 assertion 6.
2. **`ai.accessories` is on the forbidden-import list** (`B4`) — the only vertical forbidden **by
   decision** rather than by the general rule.
3. **No adapter may read or write `accessory_stock_levels`** (`B9`). Without this, the separation is
   defeated by a helpful adapter that *"just reads"* the balance.
4. **The cross-map is mandatory** (`PC-61`), and the **counted cost is carried in the FRD and
   surfaced in the product** (`FR-370`, `G-051`): an explicit statement on both stock-summary screens
   that the figure covers one system only. A user in an install running both **will** ask *"how much
   of part X do we hold"* and get two answers; the product should say so rather than let them find
   out.

## 9.9 Deliberately **not** consumers, and why

| | Decision | Source |
|---|---|---|
| **Dealer vehicle inventory** (`pdi_vehicle_inventory`, 26 `pdi_*` tables) | **Not migrated in v1 or v2.** The **test** is stated rather than the answer: *can `whb_serials` + `whb_movement_line_attributes` carry a chassis number, a colour, a variant and a PDI status **without `warehouse-base` acquiring a single vehicle-shaped column**?* If the answer needs a base column, the answer is **no, permanently**. Revisit at v3 | `OD-2`, `G-050`, `FR-365` |
| **A second item master** | No module other than `accessories` (`D-9`) may own one | `FR-048` |
| **A shared `party-base`** | Not extracted now. **The trigger is recorded**: the **third** module that needs the same GSTIN to be authoritative for tax filing. Until then extraction is speculative; after then it is overdue. The cost of not extracting — up to **seven** party-shaped masters — is stated, not hidden | `OD-4`, `FR-121`, R7 §3.3 |

---

# 10 · Versioning and compatibility

## 10.1 The rule

> **The port evolves by addition only. A shipped consumer that sends exactly what it sent yesterday
> gets exactly what it got yesterday, forever.**

That is what makes "any number of future consumers" true across time as well as across modules. A
consumer built in v1 against `warehouse-base` must still post successfully against v3's base without
a code change, because a `logistics` module and a customer's own integration will both be on their
own release cycles.

## 10.2 What may change, and what may not

| Change | Allowed? | Rule |
|---|---|---|
| **Add an optional request field** | **yes** | Must have a server-side default that reproduces the previous behaviour exactly. Because `PC-17` hashes the **received** body, a v1 producer's replay hashes identically after the field is added |
| **Add a response field** | **yes** | Consumers must ignore unknown fields. Stated here so it is a contract term rather than a hope |
| **Add a catalogue row** (movement type, status, location type, …) | **yes** | §7 — that is the whole point of the catalogues |
| **Add an error code** | **yes** | §3.9.2. A consumer must treat an unrecognised code as non-retryable |
| **Add an outbox event code** | **yes** | `PC-43`. A consumer filters on `event_type` and ignores the rest |
| **Add a dimension to an existing outbox event** | **no, in effect** | `PC-38` — the dimension was never emitted for events already consumed, and cursors have passed them. This is why the dimension set is fixed in v1 |
| **Make an optional request field required** | **no** | Breaking. Enforce it with a new movement type's behaviour flag instead |
| **Rename or repurpose an error code** | **no** | `PC-29` — five callers branch on them |
| **Rename a catalogue `code`** | **no** | Posted history references it. Deactivate the row (`is_active = false`) and seed a new one |
| **Change the meaning of an existing field** | **no** | The worst kind of break: it compiles, it returns 201, and the numbers are wrong |
| **Remove anything** | **no**, except by §10.3 | — |
| **Change a management endpoint a mobile screen calls** (`/warehouse/<resource>`) | **additive only**, from **v1.1** | Every row above applies to it as it does to the port, and each such endpoint is marked in its `BUILD-SPEC-SCREENS.md` mobile block. Handhelds lag the server on an MDM schedule, so a response field renamed for the web breaks every scan gun on the floor that morning (`RL-017`, `P3-04`) |

**The handheld floor (v1.1).** The server refuses an app older than the `admin_settings` key
`warehouse.mobile.min_app_version`, checked at login and at sync, with `426 CLIENT_UPGRADE_REQUIRED`;
`whb_devices.app_version` is what the device grid filters on. A handheld on the wrong build is told to
update rather than left to misbehave (`P3-04`; `P0-16`'s mobile section points here).

## 10.3 The deprecation path

> Four steps, and the clock starts at step 1, not at step 3.
>
> 1. **Mark.** The field/endpoint is documented as deprecated in this file with the version it will
>    be removed in, and the response carries a `Deprecation` header naming the replacement.
> 2. **Instrument.** Usage is counted per `source_system` — the port already knows who is calling,
>    because `source_system` is mandatory (§2.4). *"Nobody uses it"* becomes a measurement rather
>    than an assumption.
> 3. **Wait.** Removal cannot happen in the version that deprecates it, and cannot happen while any
>    `source_system` still uses it. The minimum is **one full minor version**.
> 4. **Remove**, in a **major** version, with the removal listed in §10 and in the release note.
>
> **A catalogue row is never removed** — it is deactivated. Posted history references it, and a
> `code` whose row has vanished renders as a raw string on a report about a period that is already
> filed.

## 10.4 Wire versioning — how it is done, and how it is not

> **`PC-75`** · **The port is versioned by URL path segment** — `/api/warehouse/movements` is v1;
> a breaking change would be `/api/warehouse/v2/movements`, with **both live simultaneously** and the
> v1 path continuing to post to the same ledger. **Not** by a header, **not** by content negotiation,
> and **never** by branching on `source_system` — which would make base's behaviour depend on who is
> calling, i.e. base knowing its consumers, i.e. the thing this whole document forbids.
>
> Outbox events version **independently**, by `event_version` on the row (§4.2), because a consumer's
> read cursor cannot be path-versioned. **Each subscription names the version it accepts** —
> `whb_outbox_subscriptions.accepted_event_version` (§4.3) — and base emits each event to it at that
> version until the subscriber moves. *(`RL-002`, `IRR-66`.)*

## 10.5 What a breaking change would actually cost

Named so nobody proposes one casually:

- **Every consumer redeploys**, on their own schedule, and the two versions run in parallel until the
  slowest one moves. For an out-of-process `logistics` deployable that is a **coordinated release**,
  which is exactly the coupling module independence was bought to avoid.
- **The idempotency keyspace must be preserved across the versions**, or a retry that crosses the
  cutover double-posts. `uk(source_system, idempotency_key)` therefore spans both paths — which
  means the two versions are not really independent, and a v2 that changes what a key *means* is
  not implementable at all.
- **`payload_hash` semantics must be preserved per version**, or every v1 key looks reused.
- **Every error code the consumers branch on must survive**, so a v2 that "cleans up the error
  vocabulary" is not a v2, it is a new product.
- **The outbox cannot be re-versioned retroactively**, so v1 events stay v1 forever and every
  consumer needs both handlers.

The honest conclusion: **there is no cheap breaking change to this port.** That is the argument for
getting §2's field list right in v1, and it is the same argument [`IRREVERSIBLE.md`](IRREVERSIBLE.md)
makes about the schema.

## 10.6 The four API-contract decisions that are unrecoverable later

Distinct from the schema list in `IRREVERSIBLE.md` — these are **wire-contract** decisions, and no
migration can repair any of them.

| # | Decision | Why it cannot be recovered |
|---|---|---|
| **1** | **The idempotency key is caller-supplied, and its namespace is partitioned by `source_system`** (`PC-15`, `PC-16`) | Once two producers have posted, the partitioning cannot be changed: re-partitioning makes historical keys **collide retroactively**, and a collision in an append-only ledger is not repairable. Making the server generate keys later is worse — every producer's retry logic was written against a contract where a retry is safe, and it silently stops being safe |
| **2** | **The error-code vocabulary is stable strings, with no version negotiation** (`PC-29`) | Consumers branch on the code. Renaming one changes behaviour in a deployed consumer with **no compile error and no runtime error** — the branch just stops being taken. There is no mechanism to detect it and no way to re-run the affected postings, because they were accepted or rejected at the time |
| **3** | **The lineage quad is the only join to a producer's document** (§2.4, `FR-018`, `FR-036`) | A free-text `reference` cannot be retro-split into four columns for history: the four values were never separated, and no parser recovers them reliably. A consumer that cannot find its own postings cannot reconcile, cannot reverse selectively and cannot be audited |
| **4** | **The outbox's event granularity and its per-event dimension set** (`PC-38`, `PC-42`) | A coarse event **cannot be refined for the past** — the finer facts were never emitted — and consumers' cursors have already passed the coarse ones. A design that emits only `order.shipped` makes per-line 3PL billing permanently unavailable for every period already elapsed, which is the difference between a billing engine and a billing *report* |

---

# 11 · A worked example

Four calls, in JSON, with the resulting ledger lines shown. Ids are abbreviated for readability; every
`…` is a UUID.

**Setup, seeded per install and per site** (`FR-084`): virtual locations `VIRT-SUPPLIER`,
`VIRT-CUSTOMER`, `VIRT-ADJUSTMENT`, `VIRT-SCRAP`, `VIRT-OPENING`, `VIRT-COUNT-VAR`, and, created
per transfer at dispatch, an `IN_TRANSIT` location under the **source** site (`FR-147`, `FR-148`). All have `counts_as_on_hand = false`, so they never
inflate on-hand while still making every movement two-sided (`L-1`, `IRR-05`).

---

## 11.1 A receipt

A goods receipt against a purchase document: 10 cases of oil filter `OF-1120`, lot `L-2609`, into
`SITE-A / RECV-01`, at ₹412.50 per **each**. The item's base UoM is `EA`; a `CASE` is 12.

**Request**

```jsonc
POST /api/warehouse/movements
{
  "source_system":           "WAREHOUSE",
  "source_document_type":    "GRN",
  "source_document_id":      "GRN-2026-000841",
  "source_document_line_no": 2,
  "idempotency_key":         "WAREHOUSE:GRN-2026-000841:2:RECEIPT",
  "company_id":              "c0…01",
  "warehouse_id":            "w0…0A",
  "movement_type_code":      "RECEIPT",
  "occurred_at":             "2026-09-01T09:14:00.000Z",
  "occurred_at_tz_offset":   330,
  "posting_date":            "2026-09-01",
  "actor":  { "actor_type": "USER", "actor_user_id": "u0…77", "device_id": null },
  "lines": [
    { "line_no": 1, "owner_id": "o0…HOUSE", "sku": "OF-1120",
      "location_id": "l0…RECV01", "quantity": 10, "uom_code": "CASE",
      "lot_id": "lot…2609", "stock_status_code": "AVAILABLE", "duty_status": "DOMESTIC",
      "unit_cost": 412.50, "cost_currency_code": "INR", "cost_basis": "ACTUAL",
      "source_line_ref": "PO-77120/L2" },
    { "line_no": 2, "owner_id": "o0…HOUSE", "sku": "OF-1120",
      "location_id": "l0…VIRT-SUPPLIER", "quantity": -10, "uom_code": "CASE",
      "lot_id": "lot…2609", "stock_status_code": "AVAILABLE", "duty_status": "DOMESTIC",
      "unit_cost": 412.50, "cost_currency_code": "INR", "cost_basis": "ACTUAL",
      "source_line_ref": "PO-77120/L2" }
  ]
}
```

**Response — `201 Created`**

```jsonc
{
  "movement_id": "m0…A1", "sequence_no": 88412,
  "recorded_at": "2026-09-01T09:14:03.117Z",
  "payload_hash": "9f2c…e41b", "posting_status": "PENDING", "period_id": "p0…2609"
}
```

**Ledger lines written** — `whb_stock_movement_lines`

| line | owner | item | location | qty (entered) | uom | factor | **base_qty** | lot | status | duty | unit_cost | cost_basis |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | HOUSE | OF-1120 | `SITE-A/RECV-01` | **+10** | CASE | 12.00000000 | **+120** | L-2609 | AVAILABLE | DOMESTIC | 412.50 | ACTUAL |
| 2 | HOUSE | OF-1120 | `VIRT-SUPPLIER` | **−10** | CASE | 12.00000000 | **−120** | L-2609 | AVAILABLE | DOMESTIC | 412.50 | ACTUAL |

`L-1`: `+120 − 120 = 0` per `(owner, item, lot, serial, duty_status)`. ✔
**On-hand effect:** `SITE-A/RECV-01` `+120 EA` — `VIRT-SUPPLIER` has `counts_as_on_hand = false`.
`conversion_factor_used = 12` is **frozen on both lines**; if the case size becomes 6 next year, this
receipt still says 120 (`L-7`).

**Outbox rows written** (same transaction): `stock.movement.posted` (seq 140911) and
`receipt.line.confirmed` (seq 140912, grain = line, carrying owner, lot, location, quantity and the
lineage quad — `PC-38`).

**Now retry the identical call** — the device's network timed out and it resends:

```
→ 200 OK   { "movement_id": "m0…A1", "sequence_no": 88412, "idempotent_replay": true }
```

Nothing posted. **Now change the quantity to 11 and reuse the key:**

```jsonc
409 Conflict
{ "error": "IDEMPOTENCY_KEY_REUSED",
  "original_movement_id": "m0…A1",
  "details": { "errors": { "idempotency_key": "Key already used for movement m0…A1 with a different payload" } } }
```

Nothing posted, nothing overwritten (`PC-16`).

---

## 11.2 A two-leg transfer, with a partial arrival

15 cases move from `SITE-A` to `SITE-B` on trip `TRIP-8842`. **Logistics posts both legs**, and base
never learns what a trip is.

**Leg 1 — depart** (`source_system: "LOGISTICS"`, `source_document_type: "TRIP"`,
`source_document_id: "TRIP-8842"`, `idempotency_key: "LOGISTICS:TRIP-8842:DEPART:OF-1120:L2609"`,
`movement_type_code: "TRANSFER_DEPART"`, `occurred_at: "2026-09-01T22:05:00.000Z"` — the **gate-out**
time, not the sync time):

| line | owner | location | qty | base_qty | lot | status |
|---|---|---|---|---|---|---|
| 1 | HOUSE | `SITE-A/PICK-FACE-03` | **−15** | **−180** | L-2609 | AVAILABLE |
| 2 | HOUSE | `SITE-A/IN_TRANSIT-TRIP-8842` | **+15** | **+180** | L-2609 | AVAILABLE |

The transit location is **per reference, not one global bucket** (`FR-085`), so two consignments on
the road are separately countable and separately ageable. It is a child of the **source** site,
`SITE-A`, so in-transit value stays in the sender's grain and resolves to `SITE-A`'s `REGISTERED`
branch (`FR-147`, `FR-148`).

**Leg 2 — arrive, partially.** Twelve cases arrive on 2 September; three are missing. `SITE-B`'s
storekeeper posts this leg against that transfer's transit location regardless of site scope
(`P1-18`).

| line | owner | location | qty | base_qty | lot | status |
|---|---|---|---|---|---|---|
| 1 | HOUSE | `SITE-A/IN_TRANSIT-TRIP-8842` | **−12** | **−144** | L-2609 | AVAILABLE |
| 2 | HOUSE | `SITE-B/RECV-01` | **+12** | **+144** | L-2609 | AVAILABLE |

**Position after both legs:**

| location | on hand |
|---|---|
| `SITE-A/PICK-FACE-03` | −180 EA against its prior balance |
| `SITE-A/IN_TRANSIT-TRIP-8842` | **+36 EA (3 cases) — still on the road, countable, ageable, attributable** |
| `SITE-B/RECV-01` | +144 EA |

**Nobody had to decide whether B "received" fifteen.** The three cases are a real, visible,
owner-attributed balance in a transit location. If they are then written off:

**Leg 3 — transit loss** (`movement_type_code: "TRANSIT_LOSS"`, `reason_code_id` = `CARRIER_DAMAGE`
in the `TRANSIT_LOSS` context, mandatory because the type carries `requires_reason`):

| line | owner | location | qty | base_qty | status | reason |
|---|---|---|---|---|---|---|
| 1 | HOUSE | `SITE-A/IN_TRANSIT-TRIP-8842` | **−3** | **−36** | AVAILABLE | CARRIER_DAMAGE |
| 2 | HOUSE | `VIRT-ADJUSTMENT` | **+3** | **+36** | AVAILABLE | CARRIER_DAMAGE |

That is a **reason-coded loss against a transit location with a named owner** — which is exactly what
makes it claimable against the carrier, and what stops it appearing as mysterious shrinkage at
`SITE-B` (R4 §4.6). **Commits to `warehouse-base` for any of this: zero.**

---

## 11.3 A reversal

The receipt of §11.1 was posted against the wrong lot. There is **no edit** (`PC-19`).

**Request**

```jsonc
POST /api/warehouse/movements/m0…A1/reverse
{
  "idempotency_key": "WAREHOUSE:GRN-2026-000841:2:RECEIPT:REV",
  "reason_code_id":  "rc…WRONG_LOT",
  "posting_date":    "2026-09-01",
  "occurred_at":     "2026-09-01T11:02:00.000Z",
  "actor": { "actor_type": "USER", "actor_user_id": "u0…77" }
}
```

**Response — `201 Created`** — `{ "movement_id": "m0…A2", "sequence_no": 88431, "reversal_of_movement_id": "m0…A1" }`

**Ledger lines written** — the mirror. Same lot, same status, same owner, same duty status, same
frozen factor; only the sign changes:

| line | owner | location | qty | base_qty | lot | status | reason |
|---|---|---|---|---|---|---|---|
| 1 | HOUSE | `SITE-A/RECV-01` | **−10** | **−120** | L-2609 | AVAILABLE | WRONG_LOT |
| 2 | HOUSE | `VIRT-SUPPLIER` | **+10** | **+120** | L-2609 | AVAILABLE | WRONG_LOT |

`movement_type_code` = `RECEIPT_REV` (the original type's `reversal_type_code`). On `m0…A1`:
`is_reversed = true`, `reversed_by_movement_id = m0…A2`. **No row was updated to achieve this except
those two denormalised flags on the header, which are part of the posting, not a correction of it.**

Then re-post the receipt correctly, with the right lot and a **new** key
(`…:RECEIPT:V2`). The audit trail reads: received wrongly, reversed with a reason, received
correctly. Three movements, all visible, none hidden. That is `L-3`.

**Now try to reverse the reversal:**

```jsonc
409 Conflict   { "error": "CANNOT_REVERSE_A_REVERSAL",
                 "details": { "errors": { "movement_id": "m0…A2 is a reversal of m0…A1" } } }
```

---

## 11.4 A value-only movement — landed cost

Freight of **₹4,500** on `GRN-2026-000841` arrives a week later and capitalises into the cost of lot
`L-2609` at `SITE-A/RECV-01`. **The quantity does not change. The value does.**

**Request**

```jsonc
POST /api/warehouse/movements
{
  "source_system":        "LOGISTICS",
  "source_document_type": "FREIGHT_CHARGE",
  "source_document_id":   "FC-2026-01991",
  "idempotency_key":      "LOGISTICS:FC-2026-01991:APPLY:GRN-2026-000841",
  "company_id":           "c0…01",
  "warehouse_id":         "w0…0A",
  "movement_type_code":   "LANDED_COST_APPLY",
  "occurred_at":          "2026-09-08T16:40:00.000Z",
  "posting_date":         "2026-09-08",
  "reason_code_id":       "rc…FREIGHT_CAPITALISATION",
  "actor": { "actor_type": "INTEGRATION", "actor_user_id": null, "device_id": null },
  "lines": [
    { "line_no": 1, "owner_id": "o0…HOUSE", "sku": "OF-1120",
      "location_id": "l0…RECV01", "quantity": 0, "uom_code": "EA",
      "lot_id": "lot…2609", "stock_status_code": "AVAILABLE", "duty_status": "DOMESTIC",
      "extended_cost":  4500.00, "cost_currency_code": "INR", "cost_basis": "ACTUAL",
      "source_line_ref": "FC-2026-01991/1" },
    { "line_no": 2, "owner_id": "o0…HOUSE", "sku": "OF-1120",
      "location_id": "l0…VIRT-LANDED-COST-OFFSET", "quantity": 0, "uom_code": "EA",
      "lot_id": "lot…2609", "stock_status_code": "AVAILABLE", "duty_status": "DOMESTIC",
      "extended_cost": -4500.00, "cost_currency_code": "INR", "cost_basis": "ACTUAL",
      "source_line_ref": "FC-2026-01991/1" }
  ]
}
```

**Ledger lines written**

| line | owner | item | location | qty | base_qty | lot | extended_cost | cost_basis |
|---|---|---|---|---|---|---|---|---|
| 1 | HOUSE | OF-1120 | `SITE-A/RECV-01` | **0** | **0** | L-2609 | **+4,500.00** | ACTUAL |
| 2 | HOUSE | OF-1120 | `VIRT-LANDED-COST-OFFSET` | **0** | **0** | L-2609 | **−4,500.00** | ACTUAL |

- `L-1` quantity conservation: `0 − 0 = 0`. ✔ *(and there is deliberately no `CHECK (quantity <> 0)`
  — `PC-11`)*
- Value conservation: `+4,500 − 4,500 = 0`. ✔ *(per `PC-12`'s `value_balance_rule`)*
- **On-hand is unchanged.** The **cost layer** for lot `L-2609` is increased by ₹4,500 across 120 EA,
  i.e. `+₹37.50` per each; `moving_average_after` is stamped on the line, so the 30-September cost is
  reproducible (`IRR-39`).
- The accounting envelope carries the freight capitalisation with `handover_id` and
  `posting_status = PENDING`; **`warehouse` never writes an `acc_*` table** (`D-6`).

**Without `PC-11`, none of this is possible**, and freight sits in an expense account forever while
warehouse and accounting disagree permanently about what the stock cost. That is the argument in
`FR-345`, and R7 §1.7 records that **no prior-art transport document in this monorepo connects
freight to inventory value at all** — so the hook has to be in v1 or it is never built.

---

# 12 · Appendix — what this document could not resolve

`DECISIONS.md` §7 rule 2 requires a claim to be evidenced or marked `UNVERIFIED`, and requires
disagreement to be stated rather than diverged from silently.

## 12.1 Divergences carried, and from whom

| # | Divergence | Followed | Why |
|---|---|---|---|
| 1 | Ledger table names — R4 `whb_movements`/`whb_movement_lines` | **`DECISIONS.md`** — `whb_stock_movements` / `whb_stock_movement_lines` | `L-1`, `L-2`, `L-4`; `IRREVERSIBLE.md` §7.1 |
| 2 | `from_location_id` **and** `to_location_id` on one line (R4 §3.3, R5 row 20) | **`DECISIONS.md`** — one end per line, signed (`PC-08`) | `D-4` + `L-1`. The irreversible *content* of both proposals survives |
| 3 | `effective_date` (R4 §3.2, `FR-032`) | **`DECISIONS.md`** — `posting_date` (`PC-07`) | `L-13`, `IRREVERSIBLE.md` §4.1. `FR-032`'s wording needs a one-word correction |
| 4 | Batch posting at v1.1 (R4 `F-092`) | **R7 / `FR-034`** — v1 (`PC-18`) | The port's *shape* is P0; a consumer's retry logic cannot be retro-fitted |
| 5 | Outbox without a subscription table (R4 `F-086`) | **R7 `G-046`** — `whb_outbox_subscriptions` in v1 (`PC-39`, `PC-40`) | Logistics may be a separate deployable; three in-process subscribers make it a redesign |
| 6 | Reservations without a holder quad (R4 `F-028`) | **R7 `G-042`** — the quad + `expires_at` (`PC-51`) | *"Release everything trip X held"* is otherwise unanswerable |
| 7 | Dock-appointment schema at v2 (R4 `F-080`) | **R7 `G-014` / `FR-092`** — schema v1, screen v1.1–v2 | A duration cannot be backfilled; a v2 table means every v1 receipt has no arrival time, forever |
| 8 | `partner_type ENUM` (R2 `T-040`) | **R7 `G-057`** — a role link table (§7.2 row 11) | One entity, two roles, one GSTIN; `asset_vendors.vendor_type` already has six values and misses carrier |
| 9 | `item_type` as an enum (R3 `E-007`) | **R7 `G-060`** — a registry row (§7.2 row 10) | Logistics alone adds four types; seven values before the second consumer is a closed vocabulary |
| 10 | Adapter table prefix `wha_<vertical>_` (R7 §4.5) | **`DECISIONS.md` `D-3`** — `whad_`/`whas_`/`whaf_`/`whaa_` | `D-3` fixes prefixes; `IRREVERSIBLE.md` §7.1 |
| 11 | `warehouse-3pl` prefix `wh3pl_` (R4) / band `V930000` (R4 §5.1) | **`DECISIONS.md`** — `wh3_`, `V530000–V539999` | `D-2` (the V900000 bands are occupied), `D-3` |
| 12 | A union stock report across accessories (R3 `M3`/`E-084`) | **R7 §4.6 item 4** — a documented separation statement, not a union view (`PC-62`) | A union is a compile-time dependency on `accessory_stock_levels`. **`IRREVERSIBLE.md` §7.2 records this as genuinely unresolved and needing an `OD-` row** |

**Where I diverge from both R4 and R7, and argue it:** nowhere on substance. Two places I have
**added** rather than diverged, because both sources are silent and an implementer would otherwise
guess: `PC-17` (what exactly is hashed into `payload_hash`) and `PC-21`…`PC-25` (ordering and
out-of-order arrival, in particular `PC-23`'s decision that sufficiency is evaluated at post time
rather than as-at `occurred_at`). Both are stated as decisions of this contract, both carry the
argument, and both should be reflected into the FRD.

## 12.2 Open, and this document does not decide them

| # | Open item | Deadline | Recommendation |
|---|---|---|---|
| 1 | **`OD-5` — may a TypeScript string union enumerate an open backend catalogue?** | before the first warehouse page is written | `PC-70`. **Referred to the standards owner**, recommendation attached, not applied |
| 2 | **Out-of-process caller authentication** (`PC-33`) | before `whb_outbox_subscriptions` HTTP delivery in v1.1 | A platform service principal with owner grants, so `PC-05` and `PC-32` apply unchanged. **Needs an `OD-` row in `DECISIONS.md`** — allocating `OD-` ids is that document's business |
| 3 | **Value conservation on a value-only movement** (`PC-12`) | before `P0-02` writes the ledger | Either a `value_balance_rule` behaviour column on `whb_movement_types`, or a fifteenth `L-` invariant. `L-1`…`L-14` currently conserve **quantity only** |
| 4 | **A value-offset virtual location** (`PC-12`) | with the above | `FR-084`'s seeded list has no value-offset row. One seed row (`LANDED_COST_OFFSET`) or the reuse of an `ADJUSTMENT_OFFSET`-typed location. **Flagged, not assumed** |
| 5 | **§3.9.2's twelve added error codes** | before v1 ships | Fold into `FR-039`. `PC-29` forbids renaming after the fact, so adding them late is the failure it prevents |
| 6 | **`OD-1` / `OD-6` — where the cost-layer tables live** | before `P2` | Not this document's. What is **not** in doubt: `cost_basis`, `unit_cost`, `cost_currency_code`, `moving_average_after` and `cost_layer_id` are **columns on the ledger line** whoever computes the numbers (`IRREVERSIBLE.md` §7.3) |
| 7 | **`OD-7` — precision** | before `P0-02` | Every numeric type in §2 is a recommendation carrying a citation, not a ruling. `conversion_factor_used` in particular: R4 proposes `numeric(18,8)`; the accounting set's `DECIMAL(19,8)` is explicitly *"the **currency-conversion** type and nothing else"* |
| 8 | **`OD-3` — one DB per customer vs shared multi-tenancy** | before `warehouse-3pl` P5 | Not this document's. Note only that `PC-32`'s owner scope is what carries the 3PL case either way |
| 9 | **Where `document.status_changed` carries `from_status` / `to_status`** (`RL-014`) | before `V500040` ships | `PC-37` leaves no payload and `PC-36`'s column set has no status pair, so the v1.1 event cannot say which transition happened. Either two nullable `VARCHAR(40)` columns join the v1 set in `V500040` (a dimension added later is `PC-38`'s irreversible case), or the consumer reads the status back by document id. **Flagged for `P0-11`/`P3-22`, not decided here** |

## 12.3 `UNVERIFIED`, stated plainly

- **Migration numbers.** No task file exists yet (`ls issues/` in `warehouse-issues` → empty), so no
  `V5nnnnn__*.sql` number is cited anywhere in this document. The bands are `D-2`'s; the numbers are
  the task files' to allocate.
- **Counts move.** Every count here was computed on 2026-09-01 against
  `/Users/bbhushan/work/git/workspace/classic` at branch `main`, with the command shown. Two have
  already moved between documents in this set — `COMMON_FILTER_CONFIGS` scopes read **210** in R7,
  **211** in `MODULE-INTEGRATION.md` and **213** here; `CacheConfiguration` names read **202** in R1,
  **230** in `MODULE-INTEGRATION.md` (its window) and **234** here (over `NR>101 && NR<423`, the whole
  `setCacheNames` block). **Re-run before treating any of them as current** — `DECISIONS.md` rule 1.
  The *argument* they support — that both files are platform source and every grid edits both — does
  not depend on the number.
- **Event delivery latency, retry backoff constants and `max_attempts`** are stated as defaults, not
  as measured values. There is no outbox anywhere in the repo to measure (§4.1), so any number here
  would be invented.

## 12.4 Referred to the standards reviewer — one line each, no detail

- `OD-5` / `PC-70` — whether a TypeScript string union may enumerate an open backend catalogue.
- Every warehouse and adapter grid needs a `COMMON_FILTER_CONFIGS` scope, a `CacheConfiguration`
  name, `grid_column_definitions` + **`filter_definitions`** rows, and both
  `grid_preferences.default_filters` **and** `default_columns` populated.
- `dateOnly` versus `date` on every pure SQL `DATE` filter (`posting_date`, `expiry_date`,
  `count_date`) — the wrong one shifts the bound by a calendar day for users east of UTC.
- Web↔mobile parity (`D-13`, CLAUDE.md Principle #3) applies to every warehouse screen; the RF screen
  family is a deliberate divergence from `EntityListScreen` and needs an explicit ruling.
- The `no-JSONB` rule as it actually holds (`PC-09`): a frozen baseline plus *no JSONB on new
  warehouse business tables*, **not** a blanket ban — grid-preference columns must still emit
  `'[…]'::jsonb`.

---

*Established 2026-09-01. Authority order: [`DECISIONS.md`](DECISIONS.md) > `reviews/R1` (on codebase
facts) > this document (on the wire shape of the port) > `reviews/R4` §3–§4 and `reviews/R7` §4–§6.
Every `grep`, `awk` and `find` count in this document carries the command that produced it and was run
on that date against `/Users/bbhushan/work/git/workspace/classic`. Re-run before treating one as
current.*


## Adopted configuration integration boundary — 2026-09-11

The base-owned port accepts base-valued `unit_cost`/`extended_value` and explicit source currency/rate evidence; adapters normalize original prices once. A foreign-currency source without a positive rate is refused atomically; repeat identity with changed normalized payload conflicts. The source snapshot preserves original amount, currency and rate evidence for audit; no base-to-accounting table access.

Tax/cost provider capabilities are lower-layer interfaces with optional adapter registrations. A dealer adapter does not import warehouse-india classes or tables. The composition layer selects an installed provider under Global Settings, captures its result or external evidence in the owning document's audit payload, and blocks the affected finalization when absent. Core stock-only operations do not acquire a tax-engine dependency. All callbacks verify document identity and retain accepted results; timeout/retry is not permission to create a second invoice.
