TITLE: [Warehouse] EPIC: P9 — `warehouse-trade`: manufacturing purchase and sales, mirrored
LABELS: epic,warehouse,phase-p9
issue: 547
---
Part of __MASTER__ · Module `warehouse-trade` (`ai.warehousetrade`, band **V550000–V559999**, prefix **`wht_`**) · Migrations — **14 blocks + the R32 `V552000` band, enumerated below** · Depends on **`P8`** (`p8-01`, `p8-02` hard; `p8-03`, `p8-04`, `p8-06`, `p8-07`, `p8-09`, `p8-10`, `p8-15`, `p8-16` for read tabs, sources and the RMA port) · Runs in parallel with **`P10`**

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
`trade-counterparty-evaluation`, `trade-sales-return-authorisation`, `trade-reports` (`docs/contracts/`; eleven).

**What P9 deliberately does not do:** no credit limit, invoice, bill, debit or credit note, payment or
MSME due-date tracking (accounting deferred, `RN-054`); no tax computation or FX; no supplier portal,
e-auction or EDI; no service / capex POs and no subcontract PO **except** the service-line PO linked to an MFG
subcontract order (`D-18` item 3, FR-682…FR-689, `p9-07`); no mobile. FRD-TRADE §11 lists all eighteen. **R32 (`D-20`) narrows this:** credit checks through the accounting credit service (`p9-17`), GST previewed by accounting's tax determination through the core SPI and the accounting adapter (`p9-15`, `D-21` item 1), service + sample POs (`p9-07`), import / bill of entry (`p9-18`), **enrichment** of core's invoice-request and credit-note events for accounting (`p9-20`, `D-21` item 2), e-mail / WhatsApp to counterparties (`p9-16`) — trade still issues no invoice, debit or credit note and keeps no payment ledger.

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
10. **R32:** **`WH-SC-750` → `WH-SC-752` → `WH-SC-753` → `WH-SC-755` → `WH-SC-757` → `WH-SC-758` → `WH-SC-761` → `WH-SC-766` → `WH-SC-768`** — HOD → Purchase PR, PO over PR, direct PO, GST, share, credit block + override, feasibility, invoice hand-off + close on invoice, order book (each needs its `CN-15`…`CN-22` seam, carried by core `P8-26` / `p8-23`; with a seam missing the step is skipped and listed).

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
  for a `SYSTEM` approval; a scheduled job calls as trade's seeded service principal (`p9-01`, `STO-D20`),
  never under a person's id. Each task grants core
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
| `V552000`–`V552061` *(R32)* | `V5520n0` DDL, `V5520n1` permissions + menus + grids + settings: p9-15 (`…00`/`…01`), p9-16 (`…10`/`…11`), p9-17 (`…20`/`…21`), p9-18 (`…30`/`…31`), p9-19 (`…40`/`…41`), p9-20 (`…50`/`…51`), p9-21 (`…60`/`…61`, no table) | p9-15 … p9-21 |
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
| [`p9-15`](p9-15.md) | GST on PO / RFQ / quotation / SO through accounting's tax determination (core SPI `CN-16`, `P8-26`) *(R32)* | p9-05, p9-07, p9-08, p9-09, `CN-16` |
| [`p9-16`](p9-16.md) | Share documents by e-mail / WhatsApp, supplier reminders *(R32)* | p9-05, p9-07 … p9-10 |
| [`p9-17`](p9-17.md) | Credit / overdue / advance checks via the accounting credit service + override *(R32)* | p9-03, p9-09, p9-15, p9-20, `CN-17` |
| [`p9-18`](p9-18.md) | Import PO, bill of entry, BoE landed cost *(R32)* | p9-07, p9-20, `CN-15` |
| [`p9-19`](p9-19.md) | Feasibility review + queue, pre-sale costing, sample hook *(R32)* | p9-03, p9-08, `CN-19` |
| [`p9-20`](p9-20.md) | Accounting hand-off: enrichment of core's invoice request / credit-note proposal, billing status, close on invoice, gate-out on invoice *(R32)* | p9-09, p9-10, p9-13, p9-15, `CN-18`, `CN-21` |
| [`p9-21`](p9-21.md) | Order book, SO progress status, SO pending to produce, Customer 360 *(R32)* | p9-09, p9-14, p9-17, p9-20, `CN-19` |

Parallel lanes after p9-03: {p9-04 → p9-05}, {p9-06}, then {p9-07 ‖ p9-08 → p9-09}, then {p9-10 ‖ p9-11},
then {p9-13 → p9-12}, then p9-14. **R32:** after p9-09 → {p9-15 ‖ p9-16 ‖ p9-19}, then p9-20 → {p9-17 ‖ p9-18}, then p9-21 (each also waits for its `CN-15`…`CN-22` seam; carrier core `P8-26`). Shared-registry edits (`filterUtils.ts`, `CacheConfiguration.java`,
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
p9-13) · `warehouse.trade.evaluation.review_grade` (D) · `warehouse.trade.sales.lost_sale_reason_codes`
(`NO_STOCK,LEAD_TIME_NOT_MET`, p9-08) · **R32:** `warehouse.trade.pr.auto_draft_sources` (`REORDER,MRP`, p9-04) · `warehouse.trade.pr.auto_draft_interval_minutes` (60) · `warehouse.trade.pr.auto_draft_department_code` (`STORES`) · `warehouse.trade.pr.mr_handoff_auto_submit` (true) · `warehouse.trade.pr.over_allocation_pct` (0) · `warehouse.trade.po.direct_category_restriction` (false, p9-07) · `warehouse.trade.approval.value_basis` (`NET`, p9-03) · `warehouse.trade.cs.rank_basis` (`LANDED_NET_OF_ITC`, p9-15) · `warehouse.trade.share.channels` (`EMAIL,WHATSAPP`, p9-16) · `warehouse.trade.expedite.auto_remind_supplier` (false) · `warehouse.trade.sales.so_requires_won_quotation` (true, p9-09) · `warehouse.trade.sales.reservation_timing` (`AT_APPROVAL`) · `warehouse.trade.sales.dispatch_release_approval` (`ONE_LEVEL`) · `warehouse.trade.sales.dispatch_checklist_required` (true) · `warehouse.trade.sales.credit_check_points` (`SO_APPROVAL,DISPATCH_RELEASE`, p9-17) · `warehouse.trade.sales.credit_check_unavailable` (`WARN`) · `warehouse.trade.sales.overdue_grace_days` (0) · `warehouse.trade.import.auto_cost_on_grn` (true, p9-18) · `warehouse.trade.feasibility.required_for` (`CUSTOM`, p9-19) · `warehouse.trade.quotation.target_margin_pct` (15) · `warehouse.trade.sales.sample_approval_before_order` (true) · `warehouse.trade.sales.close_rule` (`SHIPPED_AND_INVOICED` with an accounting target, p9-20) · reuses
`warehouse.approval.pending_alert_hours` (24). `admin_settings.description` ≤ 255 characters.

## Open decisions this phase carries

`OD-30` trade number = supplier-facing, stored as `source_document_ref` (picker match owed by `p8-03`/`p8-04`) · `OD-31` MRP → PR via core suggestions with origin `MRP` (`p8-16` `WhReplenishmentSuggestionPort`, written by MFG) · `OD-32` unreleased
customer schedule as core `FORECAST` lines (closed by `p8-02`; MFG to confirm) · **`OD-33` RMA port — `p8-15` `WhRmaPort` + supplier-return `intent_code`, blocks p9-13** ·
`OD-34` per-currency approval bands · `OD-35` per-line slabs · `OD-36` rate change on un-received qty
only · `OD-37` sealed default off · `OD-38` QC decided by core inspection plans · `OD-39` trade registers
change guards on `p8-01` / `p8-02` / `p8-15`'s seams (closed) · **`OD-45` (A)** one core demand order per
SO, header back to `OPEN` after each despatch until `closeDemand` (closed by STORES). Each has an adopted
default (FRD-TRADE §10). The core changes trade asked of STORES, FRD-TRADE §12c
(`CN-1`…`CN-7`), are all resolved (2026-10-22; `STO-D19`, `STO-D20`); `CN-8` resolved 2026-10-23 (`STO-D25`);
`CN-9`…`CN-13` agreed in R31 (registry R.2 / R.1: `firmScheduleLine(…, releaseRef)`, `closeScheduleLineShort`,
`WhLostSalePort.captureLostSale`, the `amendOrder` received floor, port-principal site scope); **`CN-14`** (the
subcontract charge seam — resolver kind + job worker, received-output read, value-only landed-cost apply) is open
and blocks only the subcontract half of `p9-07`.

## Traps this phase must not walk into

- **A fourth PO.** `RM-030` already counts three. The trade PO is the commercial document; the core PO is
  its execution. Never add a second receivable PO in trade.
- **Sales drift.** A purchase feature merged without its sales twin (or written refusal) fails review.
- **Accounting creep.** A "just record the debit note number" column is how a second ledger starts — the
  hand-over points are stated per contract and nothing more.
- **Sibling cross-imports.** Trade never imports `ai.warehousemanufacturing` or `ai.warehouseindia`;
  MRP and India facts arrive through core (`TRD-09`). A subcontract service line holds a bare
  `whm_production_orders` id resolved through core's `CostObjectResolver` — never an FK, a `whm_` read or an MFG class.
- **Port principal without site scope.** `warehouse:orders:port` alone is refused by core's site check; every
  port-calling bundle also holds `:view:branch`, the service principal `:view:all` (FR-617, R31 F-SR-004).
- **Mobile.** None — user rule 2026-09-11.
- **Docker only** for build and test; never a local `mvn` / `npm`.

## Definition of done

- [ ] Every task merged with reviewer + functional-reviewer clean against its contract rows
- [ ] The exit criterion's nine steps pass in order on a clean database
- [ ] FRD-TRADE §13 traceability: every FR-540…FR-619, FR-680…FR-689 and the R32 FR-740…FR-777 closed by a merged task
- [ ] The mirror table (FRD-TRADE §5) re-checked against the merged code: every row built on both sides or refused
- [ ] `OD-30`…`OD-39` resolved or their defaults ratified in `DECISIONS.md` by SPINE
