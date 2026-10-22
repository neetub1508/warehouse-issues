TITLE: [Warehouse] EPIC: P9 — `warehouse-trade`: manufacturing purchase and sales, mirrored
LABELS: epic,warehouse,phase-p9
issue: TBD
---
Part of __MASTER__ · Module `warehouse-trade` (`ai.warehousetrade`, band **V550000–V559999**, prefix **`wht_`**) · Migrations — **14 blocks, enumerated below** · Depends on **`P8`** (`p8-01`, `p8-02` hard; `p8-03`, `p8-04`, `p8-06`, `p8-07`, `p8-09`, `p8-10`, `p8-15`, `p8-16` for read tabs, sources and the RMA port) · Runs in parallel with **`P10`**

## Overview

**The commitment layer above the stores.** R27 found the client's purchase department steps — requisition,
quotation, fixed / open / blanket order — absent from the build (`RM-001`…`RM-006`), because R7 had given
them to a supply-chain module that never existed (`RM-025`). `D-16` / `RN-053` puts them in one switchable
sibling, **purchase and sales together, sales mirroring purchase row for row**:

```
PR (manual · stores shortage · replenishment · MRP)        Sales enquiry (customer RFQ)
  → RFQ to N suppliers → vendor quotations (versions)        → customer quotation (versions)
  → comparative statement, L1 → approved award               → won / lost / regretted
  → rate contract (slabs, ceiling, dated revisions)          → sales rate contract · price list
  → PO FIXED / OPEN / BLANKET + delivery schedule            → SO FIXED / OPEN / BLANKET + customer schedule
  → releases → core PO (p8-01)                               → dispatch releases → core demand order (p8-02)
  → gate entry, GRN + bill, QC, MRN (core, read-only)        → pick, ship, outward gate pass, challan (core / india)
  → acknowledgement · expediting · short-close · amendments  → acknowledgement · commitments · short-close · amendments
  → vendor rating                                            → customer rating / OTIF · return authorisation → RMA
```

Requirements, the mirror table, screens, scenarios, decisions, open decisions and refusals:
**[`docs/frd/FRD-TRADE.md`](../docs/frd/FRD-TRADE.md)**. Contracts (one per workflow):
`trade-approval-matrix`, `trade-purchase-requisition`, `trade-rfq-award`, `trade-rate-contract`,
`trade-purchase-order`, `trade-sales-enquiry-quotation`, `trade-sales-order`, `trade-order-amendment`,
`trade-counterparty-evaluation`, `trade-sales-return-authorisation` (`docs/contracts/`).

**What P9 deliberately does not do:** no credit limit, invoice, bill, debit or credit note, payment or
MSME due-date tracking (accounting deferred, `RN-054`); no tax computation or FX; no supplier portal,
e-auction or EDI; no service / capex / subcontract POs; no mobile. FRD-TRADE §11 lists all eighteen.

## Exit criterion — a Mode-D-plus install: platform + `warehouse-base` + `warehouse` + `warehouse-trade`

Run in order on a clean database:
1. **`WH-SC-480`** with trade **off** — nothing changes in core.
2. **`WH-SC-481`** with trade on — the bootstrap asserts the core contract.
3. **`WH-SC-496` → `WH-SC-500` → `WH-SC-505` → `WH-SC-510` → `WH-SC-513`** — PR, consolidation, RFQ, CS, award.
4. **`WH-SC-515` → `WH-SC-524` → `WH-SC-532`** — rate contract price, FIXED PO to core, gate entry + GRN with bill visible on the trade PO.
5. **`WH-SC-529` → `WH-SC-531` → `WH-SC-527`** — blanket schedule, proposal, release; open PO call-offs and ceiling.
6. **`WH-SC-537` → `WH-SC-542` → `WH-SC-539`** — acknowledgement with changes, amendment, short-close.
7. **`WH-SC-550` → `WH-SC-554` → `WH-SC-555` → `WH-SC-557` → `WH-SC-559` → `WH-SC-580`** — enquiry, quotation, won, blanket SO, dispatch release (WS-313), shipment visible, core demand order back `OPEN` until trade closes it.
8. **`WH-SC-560`, `WH-SC-562`, `WH-SC-547`** — schedule revision, return authorisation, vendor rating.
9. **`WH-SC-565`** — the auditor sees everything and exports nothing.

## The invariants and properties this phase establishes

- **Commitment in trade, quantity in core** (`TRD-01`, `G-026`): trade never writes `wh_` / `whb_` rows
  beyond guarded seeds, never posts a movement, never stores a received or shipped quantity (`TRD-03`).
- **FKs point down only** (`FR-540`), proved by `ArchitectureInvariantsTest`.
- **Maker ≠ checker on every approval**; no rule ⇒ refusal; nothing approves by time (`TAM`).
- **Every vocabulary is a code list; no status `CHECK`** (`D-10`).
- **Port calls are idempotent and transactional with the trade transition** (`FR-618`), and use the
  FRD-STORES *Port & seam registry* exactly: `PortEnvelope('warehouse-trade', key, actingUserId)`, keys
  `<SOURCE_DOCUMENT_TYPE>:<id>:<operation>:<sequence>` (FRD-TRADE §12a), a changed body on a reused key
  refused `409 PORT_IDEMPOTENCY_CONFLICT`.
- **The port principal is the person who triggered the call** (`TRD-13`): the last approver, the submitter
  for a `SYSTEM` approval, the order's buyer / sales executive for a job. Each task grants core
  `warehouse:orders:port` to its approver and maker bundles in its `V5510n0` / `V5511n0` block; without it
  core refuses `403 PORT_AUTHORITY_REQUIRED` and the trade transition rolls back.
- **One core demand order per SO, `OD-45` (A)**: its header returns to `OPEN` after each despatch, and only
  trade's `closeDemand` (auto-close or header short-close) ends it.
- **Change guards** on every trade-created core document: `409 PO_OWNED_BY_SOURCE_MODULE`,
  `409 DEMAND_OWNED_BY_SOURCE_MODULE` (allocation allowed), `409 RMA_OWNED_BY_SOURCE_MODULE` (expiry allowed).
- **Notifications** use the one platform category `NotificationCategory.WAREHOUSE_TRADE`, in-app only
  (platform commit in p9-03; kinds per FRD-TRADE §12b).
- **FIXED needs no release** on either side (`TRD-12`); releases and amendments are numbered
  `<order>-Rnn` / `-Dnn` / `-Ann` with no series; dispatch releases are listed on **WS-313** (p9-09).
- **Mirror parity:** each purchase capability and its sales twin ship in the same task on tables of
  identical shape (`TRD-02`), or the refusal is written (FRD-TRADE §5).

## Migration blocks

| Block | Content | Task |
|---|---|---|
| `V550000` | bootstrap + core-contract assertion | p9-01 |
| `V550010`, `V550011` | profiles, AVL, customer item refs, T&C templates; vocabularies, document types, series, template kinds | p9-02 |
| `V550020` | approval engine | p9-03 |
| `V550030` | purchase requisitions + allocations | p9-04 |
| `V550040` | RFQ, vendor quotations, comparative statements | p9-05 |
| `V550050` | rate contracts (both sides), price lists, contract amendments | p9-06 |
| `V550060` | purchase orders, schedules, releases | p9-07 |
| `V550070` | enquiries, customer quotations | p9-08 |
| `V550080` | sales orders, schedules, dispatch releases | p9-09 |
| `V550090` | acknowledgements, follow-ups (both sides) | p9-10 |
| `V550100` | amendments + version snapshots (both sides) | p9-11 |
| `V550110` | evaluation engine | p9-12 |
| `V550120` | sales return authorisations | p9-13 |
| `V551000`–`V551141` | per task: permissions + dependencies + menus (`V5510n0` / `V5511n0`), grids + filters + `grid_preferences` + admin settings (`…1`) | each |

## Tasks

__TASKS__

| Task | Title | Depends on |
|---|---|---|
| [`p9-01`](p9-01.md) | Module bootstrap — scaffold, flag, menu tree, the 22 applicable platform touchpoints | `p8-01`, `p8-02` |
| [`p9-02`](p9-02.md) | Trade masters — profiles, AVL, customer item refs, T&C templates, vocabularies | p9-01 |
| [`p9-03`](p9-03.md) | Approval matrix + My Approvals | p9-01 |
| [`p9-04`](p9-04.md) | Purchase requisition | p9-03, `p8-09`, `p8-10`, `p8-16` (MRP source) |
| [`p9-05`](p9-05.md) | RFQ, vendor quotation, comparative statement, award | p9-02, p9-03, p9-04 |
| [`p9-06`](p9-06.md) | Rate contracts, price lists, price resolution — both sides | p9-02, p9-03 |
| [`p9-07`](p9-07.md) | Purchase orders FIXED / OPEN / BLANKET, releases, PO port | p9-03, p9-06, `p8-01`, `p8-03`, `p8-04` |
| [`p9-08`](p9-08.md) | Sales enquiry, quotation, win/loss | p9-02, p9-03, p9-06 |
| [`p9-09`](p9-09.md) | Sales orders, customer schedule, dispatch planning, dispatch releases (WS-313), demand-order port | p9-03, p9-06, `p8-02`, `p8-03` |
| [`p9-10`](p9-10.md) | Acknowledgement, expediting / commitments, short-close — both sides | p9-07, p9-09 |
| [`p9-11`](p9-11.md) | Amendments + versions — both sides | p9-07, p9-09 |
| [`p9-12`](p9-12.md) | Vendor and customer evaluation | p9-07, p9-09, p9-13, `p8-06` |
| [`p9-13`](p9-13.md) | Sales return authorisation → RMA; supplier-return replacement | p9-07, p9-09, p9-11, `p8-15` (`OD-33`) |
| [`p9-14`](p9-14.md) | Print documents + reports | p9-04 … p9-13 |

Parallel lanes after p9-03: {p9-04 → p9-05}, {p9-06}, then {p9-07 ‖ p9-08 → p9-09}, then {p9-10 ‖ p9-11},
then {p9-13 → p9-12}, then p9-14. Shared-registry edits (`filterUtils.ts`, `CacheConfiguration.java`,
SafeTranslation, i18n) serialize at the barrier.

## Admin settings seeded by P9 (each by the task that first reads it)

`warehouse.trade.avl.enforcement` (REFUSE) · `warehouse.trade.rfq.min_suppliers` (3) ·
`warehouse.trade.rfq.reminder_days` (2) · `warehouse.trade.rfq.sealed_until_due` (false) ·
`warehouse.trade.pr.ageing_days` (7) · `warehouse.trade.contract.expiry_alert_days` (30) ·
`warehouse.trade.release_horizon_days` (7) · `warehouse.trade.firm_zone_days` (14) ·
`warehouse.trade.expedite.days_before` (3) · `warehouse.trade.ack.alert_days` (3) ·
`warehouse.trade.quotation.validity_days` (30) · `warehouse.trade.quotation.followup_days` (7) ·
`warehouse.trade.sales.discount_approval_pct` (10) · `warehouse.trade.sales.dispatch_horizon_days` (7) ·
`warehouse.trade.sales.at_risk_days` (5) · `warehouse.trade.sales.ack_send_alert_days` (1, p9-10) ·
`warehouse.trade.sales.firm_zone_days` (14, p9-09) · `warehouse.trade.sales.return_validity_days` (30,
p9-13) · `warehouse.trade.evaluation.review_grade` (D) · reuses
`warehouse.approval.pending_alert_hours` (24). `admin_settings.description` ≤ 255 characters.

## Open decisions this phase carries

`OD-30` trade number = supplier-facing, stored as `source_document_ref` (picker match owed by `p8-03`/`p8-04`) · `OD-31` MRP → PR via core suggestions with origin `MRP` (`p8-16` `WhReplenishmentSuggestionPort`, written by MFG) · `OD-32` unreleased
customer schedule as core `FORECAST` lines (closed by `p8-02`; MFG to confirm) · **`OD-33` RMA port — `p8-15` `WhRmaPort` + supplier-return `intent_code`, blocks p9-13** ·
`OD-34` per-currency approval bands · `OD-35` per-line slabs · `OD-36` rate change on un-received qty
only · `OD-37` sealed default off · `OD-38` QC decided by core inspection plans · `OD-39` trade registers
change guards on `p8-01` / `p8-02` / `p8-15`'s seams (closed) · **`OD-45` (A)** one core demand order per
SO, header back to `OPEN` after each despatch until `closeDemand` (closed by STORES). Each has an adopted
default (FRD-TRADE §10). Core changes trade still needs from STORES are listed in FRD-TRADE §12c
(`CN-1`…`CN-7`).

## Traps this phase must not walk into

- **A fourth PO.** `RM-030` already counts three. The trade PO is the commercial document; the core PO is
  its execution. Never add a second receivable PO in trade.
- **Sales drift.** A purchase feature merged without its sales twin (or written refusal) fails review.
- **Accounting creep.** A "just record the debit note number" column is how a second ledger starts — the
  hand-over points are stated per contract and nothing more.
- **Sibling cross-imports.** Trade never imports `ai.warehousemanufacturing` or `ai.warehouseindia`;
  MRP and India facts arrive through core (`TRD-09`).
- **Mobile.** None — user rule 2026-09-11.
- **Docker only** for build and test; never a local `mvn` / `npm`.

## Definition of done

- [ ] Every task merged with reviewer + functional-reviewer clean against its contract rows
- [ ] The exit criterion's nine steps pass in order on a clean database
- [ ] FRD-TRADE §13 traceability: every FR-540…FR-619 closed by a merged task
- [ ] The mirror table (FRD-TRADE §5) re-checked against the merged code: every row built on both sides or refused
- [ ] `OD-30`…`OD-39` resolved or their defaults ratified in `DECISIONS.md` by SPINE
