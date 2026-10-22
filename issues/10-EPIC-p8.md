TITLE: [Warehouse] EPIC: P8 — Manufacturing stores in core (gate, bill-matched GRN, sampling QC, MRN, requisition, issue, return, order ports)
LABELS: epic,warehouse,phase-p8
issue: TBD
---
Part of __MASTER__ · Modules `warehouse` (documents, `wh_`) + `warehouse-base` (seed rows only) · Migrations — **app `V510400`–`V510413`, base `V500300`–`V500305`, seeds `V511400`–`V511416`** (enumerated below) · Ships in **v1.1** · **Depends on `P7`** (removal, renames and the one DB rebuild, `RN-052`) · Requirements [`docs/frd/FRD-STORES.md`](../docs/frd/FRD-STORES.md) (`FR-500`…`FR-539`)

## Overview

**The client's purchase-to-stores flow, end to end, in core** ([`reviews/R27`](../docs/reviews/R27-client-p2p-stores-gap.md)
§1; placement [`reviews/R28`](../docs/reviews/R28-manufacturing-storage-retarget-impact.md) §8b `RN-053`):

gate entry with the PO and the supplier bill on arrival → receiving session → GRN with billed vs received
vs accepted, short → supplier claim, excess → approve or refuse → incoming QC with configurable lot-size
sampling → reject → *raise supplier return* (manual) → **MRN authorised by a second person** → store →
**material requisition** from a department / cost centre / production order → **store issue** to
`VIRT-CONSUMED` with the cost object on the issue lines → **store return** linked to the issue line —
plus returnable / non-returnable **gate passes**, and the two **order ports** (`warehouse-trade`'s
purchase and sales) and the **polymorphic QC source** (`warehouse-manufacturing`'s in-process and final
QC) that the siblings build on.

**What P8 deliberately does not do** (FRD §12): no debit or credit note, no bill booking (accounting
deferred, `RN-054`); no PR/RFQ/rate contract/PO approval matrix (`P9`); no production order, backflush or
MRP (`P10`); no switching rules or skip-lot dynamics; no gate pass that moves stock; no mobile.

## Exit criterion — a rebuilt dev DB, `platform` + `warehouse-base` + `warehouse`, MRN on

`WH-SC-*` run **in order** on one site with the `CLIENT-DEFAULT` sampling scheme:

1. **`WH-SC-420`/`-421`** — an `OPEN` PO at a fixed rate; a firm schedule line released (manually — trade is off).
2. **`WH-SC-427`** — the truck is gated in with PO, bill no and bill date; a session is created from the entry.
3. **`WH-SC-438`** — bill 100, received 92: the GRN posts 92 and a `SHORT_SHIPMENT` claim opens in `DRAFT`.
4. **`WH-SC-443`** — QC proposes a sample of 20 for a lot of 2,400 from the band table.
5. **`WH-SC-449`** / **`WH-SC-452`** — two defectives reject the lot; *Raise supplier return* creates a `DRAFT` return.
6. *(second GRN, clean lot)* **`WH-SC-454`** — release lands `MRN_PENDING`; the MRN is authorised by a third user; putaway is created only now; the MRN prints.
7. **`WH-SC-458`** — Maintenance requisitions 10, the head approves 8 (reserved).
8. **`WH-SC-461`/`-463`** — 5 issued to `VIRT-CONSUMED` with cost centre CC-MNT on the issue line; 3 handed off (with a test hand-off bean).
9. **`WH-SC-467`** — 2 come back `GOOD` at the issue's unit cost.
10. **`WH-SC-471`** — consumption by department shows net 3 at value; the *Stores performance* tab shows gate-to-GRN, GRN-to-MRN, QC lead time, issue turnaround and return cycle for the walk (`FR-534`).
11. **`WH-SC-432`/`-435`** — a die leaves on an RGP and partly returns; the overdue tile counts it the day after its due date.

## The invariants and properties this phase establishes

| | What P8 makes true | Where |
|---|---|---|
| **A gate pass never posts stock** | stock leaves on its own posting document; the pass references it | `P8-03` · `GTE-UNR-01` · `STO-D4` |
| **Billed, received, accepted are three stored numbers** | `billedQuantity()` no longer returns received | `P8-04` · `GBM-UNR-04` |
| **Refused excess never enters stock** | the movement posts `received − excess_refused` | `P8-04` · `GBM-T4-01` |
| **No silent supplier return** | only the manual action creates one, in `DRAFT` | `P8-07` · `IIS-UNR-01` (`FR-139` amended) |
| **Availability by status** | `MRN_PENDING.is_allocatable = false`; authorise is the only exit | `P8-08` · `MRA-GRD-06` |
| **The cost object lives on issue lines, never on the ledger** | `S-052` resolved without an append-only retrofit | `P8-10` · `SIR-UNR-01` · `RN-034` |
| **A posted store issue is immutable** | correction = return + new issue | `P8-10` · `STO-D11` |
| **Returns are valued at the issue cost** | a return never revalues stock | `P8-11` · `SIR-T4-03` |
| **FKs point down only** | no `wh_`/`whb_` FK to `wht_`/`whm_`; siblings plug in through resolver beans and ports | all · `D-16` item 5 |

## Migration blocks

| Block | Module | Task | Content |
|---|---|---|---|
| `V500300` | base | `P8-03` | code lists `GATE_PURPOSE`, `GATE_PASS_PURPOSE`, `SUPPLIER_DOCUMENT_TYPE`, `RETURN_CONDITION`; reason contexts `GATE_TURN_BACK`, `GATE_PASS_CLOSE` |
| `V500301` | base | `P8-06` | `QC_SOURCE_TYPE`, `INSPECTION_STAGE` |
| `V500302` | base | `P8-08` | stock status `MRN_PENDING`; document type `MATERIAL_RECEIPT_NOTE`; reason `MRN_AUTHORISED` |
| `V500303` | base | `P8-09` | `COST_OBJECT_TYPE`, `REQUISITION_PURPOSE`; document type `MATERIAL_REQUISITION` |
| `V500304` | base | `P8-10` | document type `STORE_ISSUE` |
| `V500305` | base | `P8-11` | movement type `ISSUE_RETURN`; reason context `STORE_RETURN`; document type `STORE_RETURN` |
| `V510400` | app | `P8-01` | PO type / validity / source / idempotency; nullable `ordered_quantity`; schedule lines; GRN-line schedule allocations |
| `V510401` | app | `P8-02` | demand-order source / SO / customer-PO refs; demand schedule lines |
| `V510402` | app | `P8-03` | gate entries, documents, gate passes, lines, returns; `wh_receiving_sessions.gate_entry_id`; weighing `subject_type` CHECK widened |
| `V510403` | app | `P8-04` | GRN bills + bill lines; GRN `gate_entry_id`; GRN-line billed / excess columns and replaced CHECK; recon case type and resolutions |
| `V510404` | app | `P8-05` | sampling schemes + bands; plan parameter columns and widened formula CHECK; plan assignments; inspection verdict/destructive columns; scheme seeds |
| `V510405` | app | `P8-06` | inspection source / stage columns; nullable `grn_id`/`grn_line_id`; new uk |
| `V510406` | app | `P8-07` | supplier-return origin inspection columns |
| `V510407` | app | `P8-08` | MRNs + lines |
| `V510408` | app | `P8-09` | cost centres; material requisitions + lines + hand-offs |
| `V510409` | app | `P8-10` | store issues + lines + serials |
| `V510410` | app | `P8-11` | store returns + lines + serials |
| `V510411` | app | `P8-12` | print template kinds, `SYS-` templates, `SYS-GRN` v2 |
| `V510413` | app | `P8-16` | `wh_replenishment_runs.run_type` CHECK + `EXTERNAL`; suggestion `origin`, `origin_document_*`, `need_date`, nullable `reorder_point`; `REPLENISHMENT_ORIGIN` list; reason `WITHDRAWN_BY_ORIGIN` |
| `V510412` | app | `P8-15` | RMA source / idempotency columns; supplier-return `intent_code`; `SUPPLIER_RETURN_INTENT` code list |
| `V511400`…`V511410` | app seeds | `P8-01`…`P8-11` (one each; `V511405` = `P8-06`) | permissions + dependency rows, grids, filters, `grid_preferences`, settings, number series |
| `V511412` | app seeds | `P8-13` | register grids, `wh_stores_registers` permissions |
| `V511413`, `V511414` | app seeds | `P8-14` | menus; settings registry completion |
| `V511416` | app seeds | `P8-16` | suggestion grid `origin`, `needDate` columns and filters |
| `V511415` | app seeds | `P8-15` | `warehouse:orders:port` reuse check, RMA grid columns/filters for source refs and supplier-return intent |

`V511411` is unused. All blocks are **new files** sorting after the `P7` rebuild (`STO-D12`).

### Existing tables that change

| Table | Change | Task |
|---|---|---|
| `wh_purchase_orders` | + `po_type`, `valid_from`, `valid_to`, `agreement_ref`, `source_*`, `idempotency_key`, `request_fingerprint`, `revision_no`, `approval_source` | P8-01 |
| `wh_purchase_order_lines` | `ordered_quantity`, `line_total` nullable; CHECK replaced; + `rate_source`, `rate_source_ref`, `agreement_line_ref`, `scheduled_quantity` | P8-01 |
| `wh_demand_orders` | + `source_*`, `sales_order_ref`, `customer_po_ref`, `customer_po_date`, `revision_no`; idempotency uk widened | P8-02 |
| `wh_receiving_sessions` | + `gate_entry_id` (partial uk) | P8-03 |
| `wh_weighing_records` | `subject_type` CHECK + `GATE_ENTRY` | P8-03 |
| `wh_goods_receipts` | + `gate_entry_id` | P8-04 |
| `wh_goods_receipt_lines` | + `billed_quantity`, `excess_accepted_quantity`, `excess_refused_quantity`, `excess_refused_reason_code_id`, `excess_approved_by/at`, `excess_approval_note`; CHECK replaced | P8-04 |
| `wh_inspection_plans` | + `sampling_scheme_id`, `fixed_sample_quantity`, `sample_percent`, `min_sample_quantity`, `inspection_level`; formula CHECK + `BAND_TABLE` | P8-05 |
| `wh_quality_inspections` | + `plan_assignment_id`, `sampling_scheme_id` (P8-05); `grn_id` nullable, + `source_type(_list)`, `source_document_id`, `source_document_ref`, `inspection_stage(_list)`, `warehouse_id` (P8-06) | P8-05, P8-06 |
| `wh_quality_inspection_lines` | + sample/verdict/destructive columns (P8-05); `grn_line_id` nullable, + `source_line_id`, `item_id`, `lot_id`, `held_location_id`, `held_status_code`, `owner_id`, uk replaced (P8-06) | P8-05, P8-06 |
| `wh_supplier_returns` / `_lines` | + `origin_inspection_id` / `origin_inspection_line_id` (P8-07); + `intent_list`, `intent_code` (P8-15) | P8-07, P8-15 |
| `wh_replenishment_runs` / `wh_replenishment_suggestions` | `run_type` CHECK + `EXTERNAL`; + `origin_list`, `origin`, `origin_document_type`, `origin_document_id`, `need_date`; `reorder_point` nullable (CHECK for `REORDER`) | P8-16 |
| `wh_store_issue_lines` (new in P8-10) | `counter_location_purpose` | P8-10 |
| `wh_rmas` | + `source_module`, `source_document_type`, `source_document_id`, `source_document_ref`, `idempotency_key`, `request_fingerprint` | P8-15 |
| `whb_stock_statuses`, `whb_movement_types`, `whb_document_types`, `whb_code_list_values`, `whb_reason_codes` | seed rows only | P8-03…P8-11 |

## Tasks

__TASKS__

| Task | Title | FRs |
|---|---|---|
| `P8-01` | PO type, schedule lines, receipt allocation, purchase-order port | FR-500–504 |
| `P8-02` | Demand-order port, customer delivery schedule | FR-505 |
| `P8-03` | Gate entry register and gate passes | FR-507–515 |
| `P8-04` | GRN bill, billed qty, short claim, excess accept/refuse | FR-516–520 |
| `P8-05` | Configurable sampling, plan assignments, verdict, destructive qty | FR-521–524 |
| `P8-06` | Polymorphic QC source | FR-525 |
| `P8-07` | Raise supplier return from QC (manual) | FR-526 |
| `P8-08` | MRN authorisation, `MRN_PENDING`, MRN/GRN print | FR-527, FR-538 (part) |
| `P8-09` | Material requisition, cost-object seam, cost centres, PR hand-off | FR-528–532, FR-533 (seam, cost centres) |
| `P8-10` | Store issue to `VIRT-CONSUMED` with cost object | FR-533, FR-535 |
| `P8-11` | Store return | FR-536–537 |
| `P8-12` | Stores print documents | FR-538 |
| `P8-13` | Stores registers and stores performance benchmarks | FR-539, FR-534 |
| `P8-14` | Menus, settings, i18n, filter scopes | — |
| `P8-15` | RMA-creation port; supplier-return intent (`REPLACE`/`CREDIT`/`NO_ACTION`) and dispatched event | FR-506 |
| `P8-16` | External replenishment-suggestion port (MRP origin) and single conversion owner | FR-528 (SEAM-M3 amendment) |

**Order:** `P7` → `P8-01` → `{P8-02, P8-03}` → `P8-04` → `P8-05` → `P8-06` → `{P8-07, P8-08}` → `P8-09` →
`P8-10` → `P8-11` → `{P8-12, P8-13, P8-15}` → `P8-14`. `P8-15` needs only `P8-01`, `P8-02` and `P8-07` and may run as soon as they land; `P8-16` needs only `P8-01`.

**Downstream:** `P9` needs `P8-01`, `P8-02`, `P8-09` (hand-off port), `P8-15` (`p9-13`, TRADE `OD-33`); `P10` needs `P8-06` (incl. non-stock-bearing sources, SEAM-M4), `P8-09`
(requisition port, cost-object resolver with counter purpose and hooks, SEAM-M1/M2), `P8-10`, `P8-11`, `P8-16` (SEAM-M3).

## Contracts

[`gate-entry`](../docs/contracts/gate-entry.contract.md) · [`grn-bill-match`](../docs/contracts/grn-bill-match.contract.md) ·
[`incoming-inspection-sampling`](../docs/contracts/incoming-inspection-sampling.contract.md) ·
[`mrn-authorisation`](../docs/contracts/mrn-authorisation.contract.md) ·
[`material-requisition`](../docs/contracts/material-requisition.contract.md) ·
[`store-issue-return`](../docs/contracts/store-issue-return.contract.md) ·
[`po-schedule-port`](../docs/contracts/po-schedule-port.contract.md) — all v0; each goes through
`functional-reviewer` (dual engine) before its task is filed (R28 §8c item 4).

## Traps this phase must not walk into

- **Editing a rebuilt migration.** `P7` rebuilds once; every P8 change is a new file (`STO-D12`).
- **Widening the demand order into a requisition** (`STO-D9`) or **routing a store issue through despatch** (relieves to `VIRT-CUSTOMER`, `WhDespatchService.java:312-319`).
- **A cost-object column on the ledger** (`RN-034`).
- **Auto-anything**: no auto supplier return, no auto PR, no auto-close of requisitions, no auto-authorised MRN, no barrier `EXIT` closing a gate entry.
- **Generating accounting documents** (`RN-054`): claims, cases and outbox events are the handover.
- **`ordered_quantity` null for `OPEN` lines** breaks every reader that multiplies it — grep and fix all (`P8-01`).
- **Filter fields not in `COMMON_FILTER_CONFIGS`** are silently dropped (`P8-14` audit).
- **Mobile**: none (`D-16` item 7).

## Open decisions

`OD-25` client band reading · `OD-26` MRN default per site · `OD-27` cost-centre source · `OD-28` free-of-charge excess · `OD-29` requisition approval levels — each with a built safe default (FRD §11).

## Definition of done

Every `FR-500`…`FR-539` row closed by a merged task; every contract row cited in a test name; the exit
chain above passes on a rebuilt DB; `reviewer` and `functional-reviewer` clean on every task;
`shared/scripts/ci-gate.sh ratchets warehouse` green; `grep -rn "wht_\|whm_" warehouse/ warehouse-base/` → 0.
