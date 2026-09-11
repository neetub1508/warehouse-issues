# Functional Contract — Receipt → QC → putaway (and receipt reversal)

> **What this is.** The functional truth for receiving goods at the dock (receiving session and GRN),
> the GRN's effect on the purchase order, optional quality inspection with its QC hold / release /
> reject / scrap dispositions, the putaway task that moves received stock to its bin, and the receipt
> reversal. Every row cites its source id, so a later gate can check a diff against the row rather
> than re-derive it.
>
> **What this is not.** It does not restate the movement writer. Everything this flow posts goes
> through [`movement-post-reverse.contract.md`](movement-post-reverse.contract.md), and a row here cites
> its `MPR-*` id instead of repeating the guard. It does not restate `DECISIONS.md`, `DATA-MODEL.md` or
> the screen spec. It does not cover coding standards. Where two sources disagree, the row says so and
> points at §9. It never picks one source silently.
>
> **Status.** Derived from the design set on 2026-09-12. **No code exists yet** (warehouse is greenfield
> in `classic`). The contract binds only once a human ratifies it (`DERIVED — ratify before
> trusting`). `TBD` marks a cell no source answers. `OPEN-nn` marks a cell where sources contradict.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Receiving session → GRN (blind or against PO) → post → optional quality inspection and disposition → putaway task → completion; receipt reversal; the PO roll-up each of these drives |
| **Module** | `warehouse` (documents, `wh_`); posts through `warehouse-base`'s single writer (`FR-436`) |
| **Domain baseline** | `docs/DECISIONS.md` (`L-1`, `L-2`, `L-3`, `L-7`, `L-8`, `L-9`, `L-12`, `L-13`, `D-15`) · `docs/DATA-MODEL.md` §2.1.13, §2.2.1 · `docs/BUILD-SPEC-SCREENS.md` §0.11, §0.13, §10.2, WS-072…WS-082 · `docs/SCENARIO-CATALOGUE.md` §3.2, §3.3, §3.21 · `docs/IRREVERSIBLE.md` (`IRR-23`, `IRR-34`) · `docs/GLOBAL-SETTINGS-DECISIONS.md` (`warehouse.receiving.over_receipt_percent`, `CONFIG-CASE-14`) · `docs/PORT-AND-ADAPTER-CONTRACT.md` event vocabulary |
| **Owning task bodies** | `issues/p1-12.md` (PO, cancel cascade, line ladder) · `issues/p1-13.md` (sessions, GRNs, blind receipt) · `issues/p1-14.md` (inspection, disposition) · `issues/p1-15.md` (putaway rules and tasks) · `issues/p1-16.md` (receipt reversal). Depends on `issues/p0-05.md` (statuses, dispositions), `issues/p0-10.md` (`whb_tasks`), `issues/p1-02.md` (scan resolution), `issues/p1-03.md` (tolerance ladder), `issues/p1-05.md` (virtual locations), `issues/p1-07.md` (lots, serials, LPNs), `issues/p1-09.md` (gapless numbers), `issues/p1-20.md` (verb seed) |
| **Primary table(s)** | `wh_purchase_orders`, `wh_purchase_order_lines` (`V510011`); `wh_receiving_sessions`, `wh_receiving_session_documents` (`V510013`); `wh_goods_receipts`, `wh_goods_receipt_lines`, `wh_goods_receipt_line_serials` (`V510014`); `wh_inspection_plans`, `wh_inspection_plan_criteria` (`V510015`); `wh_quality_inspections`, `wh_quality_inspection_lines`, `wh_quality_inspection_results` (`V510016`); `wh_putaway_rules`, `wh_putaway_tasks` (`V510017`) over `whb_tasks` (`V500034`); `wh_receipt_reversals`, `wh_receipt_reversal_lines` (`V510018`) |
| **Status columns** | **No DB `CHECK` on any of them, by design** (`D-10`, BUILD-SPEC §0.11 *"why a document and not a `CHECK`"*). The service is the only enforcement point. Ladders: session and GRN (`p1-13`), PO header (BUILD-SPEC §0.11), PO line (`p1-12`), reversal (`p1-16`), task (`whb_tasks.status`, `p0-10`). **`wh_quality_inspections` has no status column** — its state is derived from `started_at`/`completed_at` (§1.1) |
| **Permission resources** | `wh_purchase_orders:*` + `:approve` `:cancel` · `wh_receiving_sessions:*` + `:complete` `:cancel` · `wh_goods_receipts:*` + `:post` `:cancel` · `wh_quality_inspections:*` + `:disposition` `:approve` · `wh_inspection_plans:*` · `wh_putaway_rules:*` · `wh_putaway_tasks:*` (verbs: **OPEN-11**) · `wh_receipt_reversals:*` + `:approve` `:post` (seed: `p1-20` `V511000`/`V511001`) |
| **Routes** | web: `/warehouse/inbound/purchase-orders` (WS-072) + `/[id]` (WS-073), `/warehouse/inbound/receiving-sessions` (WS-075), `/warehouse/inbound/goods-receipts` (WS-076) + `/[id]` (WS-077), `/warehouse/inbound/receipt-reversals` (WS-078), `/warehouse/inbound/inspection-plans` (WS-079), `/warehouse/inbound/quality-inspections` (WS-080), `/warehouse/inbound/putaway-rules` (WS-081), `/warehouse/inbound/putaway-tasks` (WS-082) · **mobile: none.** Scope rule set by the user on 2026-09-11: warehouse gets **no mobile app**, so this screen contract is web only, and the RF-gun / scan flows (WS-229 RF Receive, WS-230 RF Putaway, every `screens/wh*` mobile screen the bodies name) are **out of scope for the classic build**. The sources that still say otherwise are listed at **OPEN-16** |
| **Requirement source** | `issues/p1-12.md` … `issues/p1-16.md` at `warehouse-issues` `main` `57bd7df` |
| **Contract status** | `derived (unratified)` — built from the design set, no code exists; ratify with `/functional-contract` |
| **Contract version** | `v0 — 2026-09-12` |

### Acceptance checks

| # | The requester expects… | Delivered by |
|---|---|---|
| A1 | One session holds N POs × N GRNs with a nullable supplier; a blind receipt posts with no PO (`WH-SC-063`, `WH-SC-064`, `WH-SC-086`) | `RQP-T1-01`, `RQP-T1-07`, `RQP-GRD-01` |
| A2 | Post is the only ledger-writing path; it writes a balanced receipt against the supplier virtual location with a gapless GRN number, and the PO line counts it (`WH-SC-051`, `WH-SC-194`) | `RQP-T1-09`, `RQP-T4-01`…`-04` |
| A3 | Received status defaults item → supplier → `AVAILABLE`, never hard-coded; tolerance, UoM, serial and identifier guards refuse with the field named (`WH-SC-066`, `-067`, `-073`, `-078`, `-079`, `-175`, `-176`) | `RQP-GRD-02`…`-08` |
| A4 | PO cancel is a cascade with a stock gate that names its blocker; close-short is explicit and creates no backorder (`WH-SC-068`, `WH-SC-083`) | `RQP-T1-14`, `RQP-T1-15`, `RQP-GRD-13`, `RQP-GRD-14` |
| A5 | One inspection series per GRN; completion refuses an incomplete result set; a completed inspection is never re-opened; the rollup is stated to the value (`WH-SC-070`, `WH-SC-301`) | `RQP-T1-16`…`-19`, `RQP-GRD-15`…`-17` |
| A6 | Disposition is QA-gated and posts a balanced status movement; scrap waits for a second user; release — and only release — creates the putaway task for QC-held stock (`WH-SC-071`, `RJ-005`, `RJ-017`) | `RQP-T1-20`…`-23`, `RQP-T4-05`, `RQP-T4-08` |
| A7 | Putaway suggests from rules-as-data, captures an override reason, refuses a policy-forbidden location, and posts a conserving move (`WH-SC-052`, `WH-SC-074`, `WH-SC-075`, `WH-SC-076`) | `RQP-T1-24`…`-27`, `RQP-GRD-21`…`-23` |
| A8 | Receipt reversal is request → approve → post, posts a linked `REVERSAL`, decrements the PO line in one transaction, and refuses once stock has moved on, naming what moved (`WH-SC-081`, `WH-SC-082`) | `RQP-T1-29`…`-32`, `RQP-GRD-24`…`-27` |
| A9 | `CONFIG-CASE-14` holds for this flow: over-receipt zero is respected (`GLOBAL-SETTINGS-DECISIONS.md`) | `RQP-GRD-06` |
| A10 | No edit of a posted GRN exists anywhere; no document writes a position directly | `RQP-UNR-01`, `RQP-UNR-06` |

---

## 1. T1 — State machine

The flow is five ladders that hand work to each other: **session** (the truck) → **GRN** (the legal
receipt) → optional **inspection** (the QC act) → **putaway task** (the move to the bin), with the
**PO** as a roll-up and the **receipt reversal** as the only correction. Verification always happens on
the GRN; inspection is optional and a different screen (`FR-127`).

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| Session | `ARRIVED` | `wh_receiving_sessions.status`; `arrived_at` stamped | `RQP-T1-01` | `-02`, `-06` | active |
| Session | `UNLOADING` | `status`; `docked_at`, `unload_started_at` stamped | `RQP-T1-02` | `-05`, `-06` | active |
| Session | `COMPLETED` | `status`; `unload_completed_at` stamped | `RQP-T1-05` | none | **terminal** |
| Session | `CANCELLED` | `status`; reason recorded | `RQP-T1-06` | none | **terminal** |
| GRN | `DRAFT` | `wh_goods_receipts.status` | `RQP-T1-07` | `-09`, `-10` | active |
| GRN | `POSTED` | `status`; `receipt_movement_id` on each line | `RQP-T1-09` | `-11` | active |
| GRN | `CANCELLED` | `status` | `RQP-T1-10` | none | **terminal** |
| GRN | `REVERSED` | `status` | `RQP-T1-11` (effect only) | none | **terminal** |
| PO header | `DRAFT` · `SUBMITTED` · `APPROVED` | `wh_purchase_orders.status` | BUILD-SPEC §0.11 authoring rows (cited, not restated — §6) | §0.11 | active |
| PO header | `PARTIALLY_RECEIVED` · `RECEIVED` | `status` | `RQP-T1-12` (effect only) | `RQP-T1-14`; the reversal regress is **undefined** (§9 hole H6) | active |
| PO header | `CLOSED` · `CANCELLED` | `status` | `RQP-T1-14`, `RQP-T1-15` | none — but WS-072 offers **Reopen** (**OPEN-07**) | **terminal** |
| PO line | `OPEN` · `PARTIALLY_RECEIVED` · `RECEIVED` | `wh_purchase_order_lines.line_status` | `p1-12` Add line; `RQP-T1-12`, `-13` | `RQP-T1-12`…`-15` | active |
| PO line | `CLOSED` · `CANCELLED` | `line_status` | `RQP-T1-14`, `RQP-T1-15` | none | **terminal** |
| Inspection | *in progress* (derived) | `started_at` set, `completed_at` null. **No status column** (DATA-MODEL §2.2.1) | `RQP-T1-16` | `-18` | active |
| Inspection | *completed* (derived) | `completed_at` set, `result` set | `RQP-T1-18` | none; a correction is a **new** inspection (`RQP-T1-19`) | **terminal** (`WH-SC-301`) |
| Scrap disposition | *pending approval* (derived) | no column names it (**OPEN-13**) | `RQP-T1-22` | `RQP-T1-23`; no decline / withdraw path (hole H3) | active |
| Putaway task | `CREATED` · `ASSIGNED` · `STARTED` · `PAUSED` · `COMPLETED` · `CANCELLED` · `EXCEPTION` | `whb_tasks.status` — `p0-10`'s ladder, with `wh_putaway_tasks` as the 1:1 extension carrying no lifecycle column (`p1-15` Traps) | `RQP-T1-24`…`-28` | `p0-10` | `COMPLETED`, `CANCELLED` terminal; `EXCEPTION`'s exits are `p0-10`'s and are not written as §0.11 rows (hole H9) |
| Reversal | `REQUESTED` | `wh_receipt_reversals.status` | `RQP-T1-29` | `-30`, `-31` | active |
| Reversal | `APPROVED` | `status`; `approved_by`, `approved_at` | `RQP-T1-30` | `-32` only — **dead end** when Post is refused (hole H4) | active |
| Reversal | `REJECTED` · `POSTED` | `status`; `reversal_movement_id` on `POSTED` | `RQP-T1-31`, `RQP-T1-32` | none | **terminal** |

Not statuses, stated so they are not mistaken for them: seals, `departed_at` and the gate pass are
recorded facts (`p1-13`); `match_status` (`MATCHED`/`QTY_OVER`/`QTY_UNDER`/`ITEM_MISMATCH`) is a
receipt outcome, not a lifecycle (**OPEN-02**, **OPEN-18**); `result` (`PASS`/`FAIL`/`PARTIAL`, literal
**OPEN-01**) is a verdict; the ASN (`wh_asns`) is v1.1 and has no status values in v1 (`RJ-018`).

### 1.2 Transitions

| ID | From | Event / action | To | Guard (service, first) | Actor (permission) | Side effects | Comment/reason required | UI entry point |
|---|---|---|---|---|---|---|---|---|
| RQP-T1-01 | — | Gate-in: a truck arrives; one session for N POs × N ASNs × N GRNs, supplier **nullable** (`FR-124`) | Session `ARRIVED` | — | `wh_receiving_sessions:create` | stamps `arrived_at` (`IRR-23`, cannot be backfilled) | no | `TBD` — WS-075 lists no Gate-in/Add action; WS-072 *Receive against* routes to WS-075 pre-filled (hole H1) |
| RQP-T1-02 | `ARRIVED` | Start | `UNLOADING` | dock door set | `wh_receiving_sessions:edit` | stamps `docked_at`, `unload_started_at` | no | WS-075 row action **Start** |
| RQP-T1-03 | `ARRIVED` · `UNLOADING` (`TBD`) | Attach PO / ASN — child editor over `wh_receiving_session_documents` | unchanged | ASN attach needs `wh_asns` (v1.1) | `TBD` (`wh_receiving_sessions:edit` assumed, unsourced) | junction row | no | WS-075 **Attach PO/ASN** |
| RQP-T1-04 | `ARRIVED` · `UNLOADING` (`TBD`) | Record seals in / out, gate pass (`FR-211`) | unchanged | — | `TBD` | `seal_number_in` / `_out`, `gate_pass_ref` | no | WS-075 **Record seals** |
| RQP-T1-05 | `UNLOADING` | Complete | `COMPLETED` | `RQP-GRD-10` | `wh_receiving_sessions:complete` — **not** `:edit` (`RJ-005`) | stamps `unload_completed_at` | no | WS-075 **Complete** |
| RQP-T1-06 | `ARRIVED` · `UNLOADING` | Cancel | `CANCELLED` | `RQP-GRD-11` | `wh_receiving_sessions:cancel` — **not** `:edit` (`RJ-005`) | none on stock | **yes** | WS-075 **Cancel** |
| RQP-T1-07 | — | Create GRN — from a session, or a **blind receipt** with no PO (`FR-128`) | GRN `DRAFT` | `RQP-GRD-01`; whether a GRN needs a session is `TBD` (hole H2); whether the PO must be `APPROVED` is `TBD` (hole H5) | `wh_goods_receipts:create` | gapless GRN number (`RQP-T4-04`) | no | WS-075 **Create GRN**; WS-076 **Blind receipt** modal |
| RQP-T1-08 | `DRAFT` | Receive line — item by id / sku / barcode / `(source_module, external_id)`; quantity, UoM, lot, `expiry_date_override`, serials, LPN, free quantity + `scheme_reference`, received stock status, `LOT`-kind attributes, `cross_dock_reference` | unchanged | `RQP-GRD-02`…`-08` | `TBD` — no source names the permission for line capture | line rows; `conversion_factor_used` fixed on the line | no | WS-076 **Receive line**, **Over/short** modals |
| RQP-T1-09 | `DRAFT` | **Post** — the only path that writes the ledger, through `MPR-T1-01` | `POSTED` | `RQP-GRD-09`, then every `MPR-T1-01` guard | `wh_goods_receipts:post` | `RQP-T4-01`…`-07` | no | WS-076 row action **Post** |
| RQP-T1-10 | `DRAFT` | Cancel | `CANCELLED` | `RQP-GRD-12` | `wh_goods_receipts:cancel` — **not** `:edit` (`RJ-005`) | none; the issued GRN number stays in the issue log (`TBD`, inferred from `whb_number_series_issued`) | `TBD` | `TBD` — WS-076's action list has no Cancel (hole H1) |
| RQP-T1-11 | `POSTED` | *(effect of `RQP-T1-32`)* | `REVERSED` | never set directly | `wh_receipt_reversals:post` (**OPEN-10**) | — | — | none — WS-076 **Reverse** routes to WS-078 |
| RQP-T1-12 | PO header `APPROVED` · `PARTIALLY_RECEIVED`; line `OPEN` · `PARTIALLY_RECEIVED` | *(effect of a GRN post)* | header `PARTIALLY_RECEIVED` / `RECEIVED`; line `PARTIALLY_RECEIVED` when 0 < received < ordered − tolerance, `RECEIVED` when ordered − received ≤ tolerance | never set directly (BUILD-SPEC §0.11); which tolerance bounds the short side is **OPEN-19** | `wh_goods_receipts:post` | `received_quantity` / `accepted_quantity` / `rejected_quantity` rolled up; `first_receipt_at` setter `TBD` | — | none (a screen offering it is the defect, §0.11) |
| RQP-T1-13 | PO line `PARTIALLY_RECEIVED` · `RECEIVED` | *(effect of a receipt-reversal post)* | line `OPEN` · `PARTIALLY_RECEIVED` | `received_quantity` decremented **in the same transaction** (`p1-16`) | `wh_receipt_reversals:post` | the PO **header** has no matching regress row (hole H6) | — | none |
| RQP-T1-14 | header `APPROVED` · `PARTIALLY_RECEIVED` · `RECEIVED`; line `OPEN` · `PARTIALLY_RECEIVED` · `RECEIVED` | Close / **Close short** | `CLOSED` | `RQP-GRD-14` | `wh_purchase_orders:edit` | line remainder → `cancelled_quantity`; **no backorder** (`WH-SC-068`); stamps `closed_at` | **yes** where received < ordered | WS-072 **Close short** modal (where the action lives: **OPEN-03**) |
| RQP-T1-15 | header `DRAFT` · `SUBMITTED` · `APPROVED`; line `OPEN` | Cancel — a **cascade with a stock gate**, not a status flip (`FR-132`) | `CANCELLED` | `RQP-GRD-13` | `wh_purchase_orders:cancel` | lines → `CANCELLED`; cascade to non-completed GRNs and to the session (**OPEN-21**) | `TBD` | WS-072 **Cancel** modal |
| RQP-T1-16 | — (or a completed inspection of the same GRN) | Start an inspection. **One series per GRN; a re-inspection takes the next number** (`RJ-014`, `FR-133`) | *in progress* | GRN `POSTED` (`TBD` — inferred: QC-held stock exists only after post); plan resolved from `whb_item_categories.default_inspection_plan_id` in the service, never an FK (`p1-14` Traps) | `TBD` — WS-080 names `wh_quality_inspections:*`, no verb for Start | header + one line per inspected GRN line | no | WS-076 **Inspect** → WS-080 **Start** |
| RQP-T1-17 | *in progress* | Record results — per line and per criterion, typed; per-line endpoints for incremental capture (`FR-133`) | unchanged | criterion rows only; no JSONB (`FR-383`) | `TBD` (`wh_quality_inspections:edit` assumed, unsourced) | `wh_quality_inspection_results` rows | no | WS-080 **Record results** |
| RQP-T1-18 | *in progress* | Complete | *completed* | `RQP-GRD-15`, `RQP-GRD-17` | `TBD` — no verb names Complete | `result` rolled up; `started_at` = min of line starts, `completed_at` = max (`FR-133`). **Nothing moves** | no | WS-080 **Complete** |
| RQP-T1-19 | *completed* | Submit again / edit the verdict | refused | `RQP-GRD-16` | any | none — the correction is `RQP-T1-16` with a new number; the first verdict stays | — | none (`RQP-UNR-04`) |
| RQP-T1-20 | QC-held stock of a GRN line | **Disposition → release** | stock in its released status | `RQP-GRD-18`; order against Complete `TBD` (hole H7) | `wh_quality_inspections:disposition` (QA-role gated) | a status change through `MPR-T1-10` (balanced, same location, reason mandatory); **then a putaway task for the released quantity** (`RQP-T4-05`, `RJ-017`) | **yes** (`FR-103`) | WS-080 **Disposition** |
| RQP-T1-21 | QC-held stock | **Disposition → reject / return to supplier** | stock in the disposition's target status | `RQP-GRD-18`; the target codes are **OPEN-12** | `wh_quality_inspections:disposition` | `MPR-T1-10`; **no putaway task** (`RJ-017`); the supplier return document is `p2-13`'s (`WH-SC-072`) | **yes** | WS-080 **Disposition** |
| RQP-T1-22 | QC-held stock | **Disposition → scrap** | *pending approval* | `RQP-GRD-18` | `wh_quality_inspections:disposition` | **nothing posts yet** (`RJ-005`) | **yes** | WS-080 **Disposition** |
| RQP-T1-23 | *pending approval* | Approve the scrap | stock scrapped | `RQP-GRD-19` | `wh_quality_inspections:approve` — **or** `whb_stock_movements:approve` (**OPEN-13**) | only now does the movement post; its shape (status change vs issue to `VIRT-SCRAP`) is **OPEN-13**; no putaway task | `TBD` | `TBD` — WS-080's action list has no Approve (hole H3) |
| RQP-T1-24 | — | Create the putaway task: **at GRN post** for a line received into an available status; **at release** for QC-held stock, for the released quantity; **never** for rejected or scrapped quantity (`RJ-017`) | task `CREATED` | the rule chain evaluates in sequence and returns `suggested_location_id` + `rule_id` (`FR-135`); whether v1 then auto-completes in the same request is **OPEN-08** | system (effect of `RQP-T1-09` / `-20`) | one `whb_tasks` row + one `wh_putaway_tasks` row per line (`p0-10`) | — | none |
| RQP-T1-25 | `CREATED` | Assign | `ASSIGNED` | explicit assignment only; no `FOR UPDATE SKIP LOCKED` claiming in v1 (`p1-15` Traps, `C-040`) | `TBD` (**OPEN-11**) | stamps `assigned_at` | no | WS-082 **Assign** |
| RQP-T1-26 | `CREATED` · `ASSIGNED` · `STARTED` (`TBD`) | **Complete** — scan the actual location; capture the override reason when actual ≠ suggested | `COMPLETED` | `RQP-GRD-21`, `-22`, `-23`; every `MPR-T1-01` guard | `wh_putaway_tasks:complete` (`p1-20`) — absent from BUILD-SPEC §10.2 (**OPEN-11**) | `RQP-T4-11`: a two-line conserving move staging → actual through `MPR-T1-01`; stamps `started_at` / `completed_at`, `completion_movement_id` | **yes, when overriding** | WS-082 **Complete** modal |
| RQP-T1-27 | `CREATED` · `ASSIGNED` (`TBD`) | Cancel | `CANCELLED` | `TBD` | `TBD` (**OPEN-11**) | what happens to the stock still at staging, and whether a new task is raised, is `TBD` (hole H8) | reason-coded per `p0-10` WS-059 | WS-082 **Cancel** |
| RQP-T1-28 | `STARTED` · `ASSIGNED` | Ages past the task type's `stale_after_minutes` | `EXCEPTION` | `p0-10` (`Y-004`) | scheduled job (`RQP-T3-02`) | unassigned; supervisor notified | — | none |
| RQP-T1-29 | — | Request a receipt reversal | Reversal `REQUESTED` | `RQP-GRD-24` | `wh_receipt_reversals:create` | reversal number from `p1-09`'s gapless series; per-line quantities in `wh_receipt_reversal_lines` (partial reversal: **OPEN-20**) | **yes** — catalogue reason code | WS-078 **Request**; WS-076 **Reverse** routes here |
| RQP-T1-30 | `REQUESTED` | Approve | `APPROVED` | `RQP-GRD-25` | `wh_receipt_reversals:approve` | stamps `approved_by`, `approved_at` | no | WS-078 **Approve** |
| RQP-T1-31 | `REQUESTED` | Reject | `REJECTED` | reason recorded | `wh_receipt_reversals:approve` | none | **yes** | WS-078 `TBD` — WS-078 lists no Reject action (hole H1) |
| RQP-T1-32 | `APPROVED` | **Post** | `POSTED`; GRN → `REVERSED` (`RQP-T1-11`); PO line decrement (`RQP-T1-13`) — **one transaction** | `RQP-GRD-26`, `-27`; then `MPR-T1-08`'s guards | `wh_receipt_reversals:post` — **not** `:approve` (`RJ-005`) | `RQP-T4-12` | the request's reason travels to the `REVERSAL` movement (`MPR-GRD-11`) | WS-078 **Post** |
| RQP-T1-33 | a putaway rule a task references | Edit / Reorder | a new rule version; the old one deactivated | copy-on-write (`version_no`, `supersedes_id`); a direct `UPDATE`/`DELETE` is refused by `I-24` (`RL-010`) | `wh_putaway_rules:edit` | the task's `rule_id` still resolves to the rule that ran | no | WS-081 **Edit** / **Reorder** |
| RQP-T1-34 | — | Test the rule chain: item + quantity + status → suggested location and the winning rule | — (nothing) | — | `wh_putaway_rules:view` (`TBD` — no verb stated) | **writes nothing** | — | WS-081 **Test** modal |

### 1.3 Guards — the predicate, the refusal, and where it lands

Every guard has a **service pre-check that rejects first, inside the transaction, with a field-level
error** in the house envelope `{ "error", "details": { "errors": { "<field path>": "<message>" } } }`
(`DECISIONS.md` §4, BUILD-SPEC §0.13). This flow's documents carry **no DB trigger of their own** except
`I-24` on putaway rules, so the service check is the only enforcement for `RQP-GRD-01`…`-21` and
`-24`…`-27`. Anything the post reaches in the ledger is backstopped by the `MPR-GRD-*` row cited; a
ledger trigger that fires in production is an incident, not a validation (`DATA-MODEL.md` §6.0).

| ID | Predicate (must hold to proceed) | Refusal: HTTP · code · field | Message shape | DB backstop | Source |
|---|---|---|---|---|---|
| RQP-GRD-01 | Blind receipt: item, quantity, UoM, owner, status and location suffice — **no PO, no placeholder PO number**. Every inbound receipt names a counterparty — whether a blind receipt must too is **OPEN-15** | `422` naming the missing field; code `TBD` | `TBD` | — | `FR-128`, `FR-120`, `WH-SC-063` |
| RQP-GRD-02 | The line's UoM converts to the item's base UoM. **The GRN modal does not offer an unconvertible unit** — the same guard as the PO line editor, built once | `422 UOM_NOT_CONVERTIBLE` · `lines[n].uom_code` | *"LITRE is not convertible to base UoM EA for item OF-1120"* | the ledger's frozen factor (`MPR-GRD-26`) | `FR-143`, `WH-SC-078`, `L-7` |
| RQP-GRD-03 | Tracking follows the item's **control policy** (serial `NONE`/`RECEIPT`/`SHIP`/`FULL`, lot `NONE`/`OPTIONAL`/`REQUIRED`, expiry policy), never a mode string read alone | `422 SERIAL_REQUIRED` · `lines[n].serials` (the code is not in `FR-039`'s list — hole H10); `LOT_REQUIRED` for a lot-required item | names the item and its policy | — | `FR-144`, `FR-098`, `WH-SC-079` |
| RQP-GRD-04 | No duplicate serial, LPN or lot in its uniqueness scope. The same serial under a **different owner** is accepted with a site-level warning; lot codes are normalised on write | `409 SERIAL_ALREADY_ISSUED` · `lines[n].serials[m]` | names the serial and its existing owner | `uk(owner, item, serial_number)`; lot `uk(owner_id, item_id, lot_code)` | `FR-106`, `WH-SC-080`, `WH-SC-142` |
| RQP-GRD-05 | The item resolves uniquely from id / sku / barcode / `(source_module, external_id)`; supplying two identifiers that resolve to different items is refused, never settled by precedence. A scanned code resolves by session owner → counterparty context → refuse | `422 UNKNOWN_ITEM`; `422 ITEM_IDENTIFIER_CONFLICT` · `lines[n]`; `409 AMBIGUOUS_IDENTIFIER` **listing the candidates** | names both identifiers and both items | — | `FR-038`, `WH-SC-175`, `WH-SC-176`, `RL-005` |
| RQP-GRD-06 | Received − ordered (free quantity excluded) ≤ the over-receipt tolerance, resolved PO line → PO header → item → warehouse → the terminal level (**OPEN-14**). Explicit zero blocks; NULL inherits; a percentage, not a fraction. Within tolerance: posts with `match_status = QTY_OVER` | `422` · `lines[n].quantity`; code `TBD` (hole H11) | *"received 560 exceeds ordered 500 by 12.00%, over which the tolerance is 5.00%"* **and the ladder level that supplied the 5.00%**; offers raise-the-PO or receive-to-tolerance + an `OVER_RECEIPT` reconciliation case. Nothing posts until one is chosen | — | `FR-130`, `RE-004`, `WH-SC-066`, `WH-SC-067`, `WH-SC-085`, `CONFIG-CASE-14` |
| RQP-GRD-07 | The received stock status is **resolved item → supplier → `AVAILABLE`** and written on the line; `AVAILABLE` appears in no code path as a literal default | — (a predicate on the code, asserted by test) | — | — | `FR-129`, `WH-SC-073` |
| RQP-GRD-08 | `LOT`-kind attribute keys entered on Receive line exist in `whb_attribute_keys` with `applies_to = LOT`, and are written to `whb_entity_attribute_values` in the post transaction | `422` naming the key; code `TBD` | names the unregistered key | FK to the key registry | `RL-007` |
| RQP-GRD-09 | Post: at least one line; the UoM guard (`RQP-GRD-02`) re-run; `match_status` computed; the post goes through the single writer and nothing else (architecture test) — then every `MPR-T1-01` guard (period `MPR-GRD-09`/`-10`, registered instant `MPR-GRD-07`, company `MPR-GRD-08`, registries `MPR-GRD-21`, attributes `MPR-GRD-24`, rounding `MPR-GRD-26`) | as the cited `MPR-GRD-*` row; the empty-GRN code is `TBD` | as cited | as cited | BUILD-SPEC §0.11, `p1-13` ladder, `FR-436` |
| RQP-GRD-10 | Session Complete: no GRN in the session is `DRAFT` | `TBD` code · `TBD` field | should name the `DRAFT` GRN (`TBD`) | — | `p1-13` ladder |
| RQP-GRD-11 | Session Cancel: no `POSTED` GRN in the session; a reason is recorded | `TBD` | should name the posted GRN (`TBD`) | — | `p1-13` ladder |
| RQP-GRD-12 | GRN Cancel: nothing posted | `TBD` | `TBD` | — | `p1-13` ladder, BUILD-SPEC §0.11 |
| RQP-GRD-13 | PO Cancel: **no GRN line has received stock** against any PO line, **and** no session this PO is attached to through `wh_receiving_session_documents` is `ARRIVED` or `UNLOADING`. **No v1 code path reads `wh_asns`** (the ASN clause activates in `P3-05`) | `TBD` code; the modal **names the blocking GRN line**, or **names the session** | *"…because GRN-… line n has received stock"* / *"…because receiving session … has arrived"* | — | `FR-132`, `WH-SC-083`, `RJ-018` |
| RQP-GRD-14 | Close / Close short: a reason is required where received < ordered; the remainder moves to `cancelled_quantity`; **no backorder is created** | `422` · reason field; code `TBD` | `TBD` | — | `FR-130`, `WH-SC-068`, `p1-12` line ladder |
| RQP-GRD-15 | Inspection Complete: **every mandatory criterion on every line has a result**. The rollup is never computed from a partial set | `422 INSPECTION_INCOMPLETE` · `lines[n].results` | names **each unrecorded mandatory criterion by line number and criterion code** | — | `WH-SC-301`, `Q-006` |
| RQP-GRD-16 | A completed inspection is never re-opened or re-submitted | `409 INSPECTION_ALREADY_COMPLETED` | points to re-inspection under the next number of the GRN's series | — | `WH-SC-301`, `RJ-014` |
| RQP-GRD-17 | Rollup, **stated to the value**: all pass → `PASS`, all fail → `FAIL`, anything mixed → the mixed literal (**OPEN-01**). Three tests, one per outcome | — | — | — | `FR-133`, `p1-14` Acceptance |
| RQP-GRD-18 | Disposition: the actor holds `wh_quality_inspections:disposition` (QA role); the status change is a balanced two-line movement at the same location with a mandatory reason (`MPR-T1-10`, `MPR-GRD-18`, `MPR-GRD-11`); it never mutates a position | `403` naming the permission (`WH-SC-071`: `stores1` refused); the ledger refusals as cited | as cited | `MPR-GRD-18`'s backstop | `FR-134`, `FR-103`, `FR-408` |
| RQP-GRD-19 | Scrap approval: the approver holds the approving permission (**OPEN-13**) **and is not the disposer** | `403` naming the maker-checker rule | `TBD` | — | `RJ-005`, `FR-164`, `FR-408` |
| RQP-GRD-20 | `sample_size_formula` and putaway `strategy` accept **whitelisted values only** — no expression, script or rule DSL | `422` · the field; code `TBD` | lists the allowed values (`TBD`) | — | `FR-041`, `p1-14`, `p1-15` Traps |
| RQP-GRD-21 | Putaway Complete with actual ≠ suggested: `override_reason_code_id` present. **The reason is captured, never silently discarded** | `422` · `override_reason_code_id`; code `TBD` | `TBD` | — | `FR-135`, `WH-SC-052` |
| RQP-GRD-22 | The actual location admits the stock: temperature class matches the zone; `commingle_policy` and `dedicated_owner_id` hold against existing stock. **Refused by the port, and the override path cannot walk past it** — the override is for *"a better location"*, never *"the guard is inconvenient"* | `422 TEMPERATURE_ZONE_MISMATCH` · `lines[1].location_id`; `409 LOCATION_POLICY_VIOLATED` · `lines[1].location_id` | names the item's class and the zone; names **the policy and the conflicting stock**. Distinguishable from a rule-engine suggestion | the port (a port refusal in production is an incident) | `FR-068`, `FR-087`, `WH-SC-075`, `WH-SC-076`, `Q-006` |
| RQP-GRD-23 | The putaway move is two lines, conserving: same status, owner, lot, quantity; from the staging location to the actual location (`L-1`, `MPR-GRD-01`) | as `MPR-GRD-01` | as cited | `I-1` | `WH-SC-052`, `p1-15` Traps |
| RQP-GRD-24 | Reversal request: the GRN is `POSTED`; a catalogue reason code is given | `TBD` code · `grn_id` / `reason_code_id` | `TBD` | — | `p1-16` ladder |
| RQP-GRD-25 | Reversal approve: approver ≠ requester | `403` naming the rule | `TBD` | — | `FR-408`, `p1-16` ladder |
| RQP-GRD-26 | Reversal post: **the received stock has not moved on**, re-checked at post — not put away and picked, not status-changed, not left the site (the exact test is **OPEN-09**); the period admits it (`MPR-GRD-09`, `-10`; which date is `MPR-OPEN-17`); the target is not a reversal and not already reversed (`MPR-GRD-12`, `-13`) | `TBD` code for *moved on*; the others as cited | **names what moved**: *"144 EA of this receipt have moved on (24 shipped, 120 relocated); reverse receipt is unavailable"* — never *"stock has moved"*. Offers an adjustment instead | as cited | `FR-131`, `WH-SC-082`, `p1-16` Traps; answers `MPR` §9 G7 one level up |
| RQP-GRD-27 | Reversal post: the `REVERSAL` movement, the GRN → `REVERSED` and the PO line decrement commit **in one transaction**; the reversal movement carries **its own idempotency key** (`MPR-GRD-03`, `-04`); the corrected receipt is later posted under a new key (`WH-SC-081`) | as cited | — | as cited | `p1-16` ladder, `FR-035`, `WH-SC-081` |

### 1.4 Transitions that must be unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| RQP-UNR-01 | Editing a posted GRN, from any screen or endpoint | no edit modal for a posted GRN anywhere in the product, **proved by grep**; correction is WS-078 only; ledger immutability is `MPR-UNR-01` | `p1-13`, `p1-16` Acceptance, `L-2`, `L-3` |
| RQP-UNR-02 | Setting a GRN to `REVERSED`, or a PO header/line to `PARTIALLY_RECEIVED` / `RECEIVED`, directly | these are effects only; no screen offers them | BUILD-SPEC §0.11, `p1-12`, `p1-13` |
| RQP-UNR-03 | A `CLOSED` or `CANCELLED` PO, a `COMPLETED`/`CANCELLED` session, a `CANCELLED`/`REVERSED` GRN, or a `REJECTED`/`POSTED` reversal moving anywhere | terminal in every ladder — but WS-072's **Reopen** contradicts this for the PO (**OPEN-07**) | §0.11, `p1-12`, `p1-13`, `p1-16` |
| RQP-UNR-04 | Re-opening a completed inspection, or overwriting its verdict | `RQP-GRD-16`; the correction is a new inspection | `WH-SC-301` |
| RQP-UNR-05 | A receipt, disposition or putaway writing `whb_stock_positions` | architecture test; every write goes through `MPR-T1-01` / `-10` (`MPR-UNR-08`). The `accessories` failure mode — a document that says `POSTED` and writes no stock — is tested for (`C-023`) | `FR-436`, `p1-13` Traps |
| RQP-UNR-06 | A reversal as an `UPDATE` on the GRN plus a compensating position write | the reversal is a `REVERSAL` movement through `MPR-T1-08`; no `cascade = ALL` from `wh_receipt_reversals` to its lines (`T-1`) | `p1-16`, `L-3` |
| RQP-UNR-07 | A putaway task created at GRN post for QC-held quantity, or ever for rejected or scrapped quantity | `RJ-017` creation rule (`RQP-T1-24`) | `RJ-017` |
| RQP-UNR-08 | An override that places stock in a policy-forbidden location | `RQP-GRD-22` | `Q-006` |
| RQP-UNR-09 | A scrap posting before a **different** user approves it | `RQP-GRD-19` | `RJ-005` |
| RQP-UNR-10 | `UPDATE` or `DELETE` of a putaway rule a task references | `I-24` trigger (`V510017`) | `RL-010` |
| RQP-UNR-11 | Reversal Post by a user holding only `:approve`, or Approve by one holding only `:post`; a `:view → :approve` dependency row | separate verbs; the reverse dependency row must not exist | `RJ-005`, `p1-16` Acceptance |
| RQP-UNR-12 | Reversing a reversal, or reversing into a `CLOSED` period | `MPR-UNR-04`, `MPR-UNR-06` | `FR-035`, `L-8` |
| RQP-UNR-13 | A JSONB column on any table of this flow (criteria, sampling, serials) | criteria and results are rows; serials are `wh_goods_receipt_line_serials` | `FR-383`, `P-007` |

---

## 2. T2 — Action × role × state

One row per action; `Allowed from` lists the §1.1 states it is offered in (every other state: not
offered). Every management query and action is further limited to the user's allowed warehouses
(`p1-18`, `D-14`, resolved through `BranchScopeService`), and an auditor is read-only everywhere.

| ID | Action | Permission | Allowed from | Extra condition |
|---|---|---|---|---|
| RQP-T2-01 | Gate-in a session | `wh_receiving_sessions:create` | — | entry point `TBD` (hole H1) |
| RQP-T2-02 | Start | `wh_receiving_sessions:edit` | Session `ARRIVED` | dock door set |
| RQP-T2-03 | Attach PO/ASN · Record seals | `TBD` | Session `ARRIVED` · `UNLOADING` (`TBD`) | ASN attach is v1.1 |
| RQP-T2-04 | Complete session | `wh_receiving_sessions:complete` | `UNLOADING` | `RQP-GRD-10`; refused to a user with only `:edit` |
| RQP-T2-05 | Cancel session | `wh_receiving_sessions:cancel` | `ARRIVED` · `UNLOADING` | `RQP-GRD-11`; refused to a user with only `:edit` |
| RQP-T2-06 | Create GRN · Blind receipt | `wh_goods_receipts:create` | — | — |
| RQP-T2-07 | Receive line · Over/short | `TBD` | GRN `DRAFT` | — |
| RQP-T2-08 | Post GRN | `wh_goods_receipts:post` | GRN `DRAFT` | `RQP-GRD-09` |
| RQP-T2-09 | Cancel GRN | `wh_goods_receipts:cancel` | GRN `DRAFT` | refused to a user with only `:edit` |
| RQP-T2-10 | Edit a GRN | **none exists after post** | — | `RQP-UNR-01` |
| RQP-T2-11 | Close / Close short a PO or PO line | `wh_purchase_orders:edit` | header `APPROVED` · `PARTIALLY_RECEIVED` · `RECEIVED` | reason where short (`RQP-GRD-14`) |
| RQP-T2-12 | Cancel a PO | `wh_purchase_orders:cancel` | header `DRAFT` · `SUBMITTED` · `APPROVED` | `RQP-GRD-13` |
| RQP-T2-13 | Start inspection · Record results · Complete | `TBD` (only `wh_quality_inspections:*` is named) | GRN `POSTED` (`TBD`); inspection *in progress* | — |
| RQP-T2-14 | Disposition (release / reject / RTV / scrap) | `wh_quality_inspections:disposition` | QC-held stock of an inspected GRN; before or after Complete is `TBD` (hole H7) | the reverse dependency row (`:view → :disposition`) must not exist |
| RQP-T2-15 | Approve a scrap disposition | `wh_quality_inspections:approve` / `whb_stock_movements:approve` (**OPEN-13**) | *pending approval* | approver ≠ disposer |
| RQP-T2-16 | Assign putaway task | `TBD` (**OPEN-11**) | `CREATED` | explicit, no claiming |
| RQP-T2-17 | Complete putaway task | `wh_putaway_tasks:complete` (**OPEN-11**) | `CREATED` · `ASSIGNED` · `STARTED` (`TBD`) | override reason when overriding |
| RQP-T2-18 | Cancel putaway task | `TBD` (**OPEN-11**) | `CREATED` · `ASSIGNED` (`TBD`) | reason-coded |
| RQP-T2-19 | Request reversal | `wh_receipt_reversals:create` | GRN `POSTED` | catalogue reason |
| RQP-T2-20 | Approve / Reject reversal | `wh_receipt_reversals:approve` | Reversal `REQUESTED` | approver ≠ requester; reject needs a reason |
| RQP-T2-21 | Post reversal | `wh_receipt_reversals:post` | Reversal `APPROVED` | `RQP-GRD-26`, `-27` |
| RQP-T2-22 | Reverse row action on WS-076 | `TBD` — `wh_goods_receipts:reverse` (`p1-20`) or `wh_receipt_reversals:create` (**OPEN-10**) | GRN `POSTED` | routes to WS-078 |
| RQP-T2-23 | Putaway rule Add / Edit / Reorder | `wh_putaway_rules:create` / `:edit` | — | copy-on-write once referenced (`RQP-T1-33`) |
| RQP-T2-24 | Putaway rule Test | `TBD` | — | writes nothing |
| RQP-T2-25 | Inspection plan Add / Edit | `wh_inspection_plans:create` / `:edit` | — | criteria as rows; whitelisted formula |
| RQP-T2-26 | View / export any screen of this flow | `<resource>:view` / `:export` (or `ADMIN` for export) | every state | warehouse scope (`p1-18`) |

---

## 3. T3 — Time-driven rules & notifications

| ID | Rule | Trigger (clock / date field) | What it changes | Who is notified | Channel | Job class | Notify-once? |
|---|---|---|---|---|---|---|---|
| RQP-T3-01 | PO **overdue** | `expected_delivery_date < today` in the **site's** timezone (`FR-439`) | nothing — a backend-computed filter (`overdueOnly`) and a WS-072 tile | none named | — | none — computed on read | — |
| RQP-T3-02 | Putaway task ageing: an `ASSIGNED` or `STARTED` task past its type's `stale_after_minutes` → `EXCEPTION`, unassigned | job clock vs `assigned_at` / `started_at` (`Y-004`) | `whb_tasks.status`, `exception_code` | supervisor; also the `warehouse.tasks.blocked_alert_minutes` alert (default 15) | `TBD` | `p0-10`'s job | `TBD` |
| RQP-T3-03 | Pending-approval escalation after `warehouse.approval.pending_alert_hours` (default 24) — whether it covers a `REQUESTED` receipt reversal or a *pending* scrap is `TBD` | elapsed hours since request | nothing — never auto-approves | `TBD` | `TBD` | `p2-23`'s | one alert per pending episode |
| RQP-T3-04 | Minimum remaining shelf life at receipt (`min_shelf_life_receipt_pct`) | receipt date vs lot expiry | refusal `SHELF_LIFE_RULE_VIOLATED` (`FR-039`) | — | — | columns ship v1 (`p1-03`); **enforcement is `p2-05`'s** | — |
| RQP-T3-05 | Lifecycle timestamps stamped by the transitions that cause them — session `arrived_at`, `docked_at`, `unload_started_at`, `unload_completed_at`, `departed_at`; GRN `received_at`, `dock_to_stock_completed_at`; PO `submitted_at`, `first_receipt_at`, `closed_at`; task `assigned_at`, `started_at`, `completed_at`. **None can be backfilled** | the injected UTC clock at the transition | the stamped column | — | — | the transition's service | — |
| RQP-T3-06 | Business time of the receipt and putaway movements | `occurred_at` / `posting_date` | as `MPR-GRD-05`, `-07`, `-09`, `MPR-T3-05` | — | — | the writer | — |

Scan for untracked dated obligations — each is a hole at §9, not invented here: a session left
`ARRIVED`/`UNLOADING` (the detention clock is WS-086, v1.1); a `DRAFT` GRN; QC-held stock nobody
inspects; a `REQUESTED` or `APPROVED` reversal; a *pending* scrap. **No source gives
`dock_to_stock_completed_at` a setter** (hole H12).

---

## 4. T4 — Cross-entity effects

| ID | When this happens | Then this other record must change | Enforced in |
|---|---|---|---|
| RQP-T4-01 | GRN post (`RQP-T1-09`) | **one balanced receipt movement** through `MPR-T1-01`: −quantity at the site's supplier virtual location (`VIRT-SUPPLIER-<SITE>`, `p1-05`), +quantity at the receiving location, in the resolved received status, with lot, serial, LPN, owner and the frozen `conversion_factor_used`; `receipt_movement_id` stored bare on each GRN line. Which virtual location a non-supplier blind receipt balances against is `TBD` (hole H13) | GRN service → writer (`WH-SC-051`, `L-1`, `L-7`) |
| RQP-T4-02 | GRN post | PO line `received_quantity` (and accepted / rejected) move; `line_status` and header `status` follow `RQP-T1-12`; `po_id` on the header is **derived** — set only when every line's `po_line_id` belongs to one PO. *GRNs of PO X* reads through lines (`RG-019`) | GRN service, same transaction |
| RQP-T4-03 | GRN post | lots, serials and LPNs are resolved or created (normalised codes); captured serials land in `wh_goods_receipt_line_serials`; `LOT`-kind attributes land in `whb_entity_attribute_values`; the counterparty is named, so the lot has a backward traceability end (`L-12`) | GRN service (`p1-07`, `RL-007`, `WH-SC-142`) |
| RQP-T4-04 | GRN created (`WH-SC-051`) / reversal requested / inspection started | a **gapless** number from the pessimistically locked counter row, logged in `whb_number_series_issued`. At create or at post is `TBD` for the GRN | `p1-09` (`WH-SC-194`) |
| RQP-T4-05 | GRN post, line received into an available status; **or** release (`RQP-T1-20`) of QC-held stock | a putaway task for that quantity (`RQP-T1-24`). What counts as *available* (the status's `is_allocatable`?) is `TBD` | `RJ-017` |
| RQP-T4-06 | GRN post | a cost layer is inserted — a backdated receipt **inserts a layer and restates nothing** (`D-15`); the landed value spreads across billed **plus** free quantity (₹41,250 over 110 → ₹375.00) | `p0-17` / `p2-16` — cited, not restated (`WH-SC-085`) |
| RQP-T4-07 | GRN post | outbox `receipt.line.confirmed` per line, carrying owner, lot, LPN, warehouse and the three timestamps, plus `MPR-T4-07`'s `stock.movement.posted`; the accounting handover per `MPR-T4-08` | outbox (`WH-SC-294`) |
| RQP-T4-08 | Disposition posts (release / reject / RTV; scrap after approval) | a status-change movement per `MPR-T1-10`; `wh_quality_inspection_lines.disposition_code` / `target_status_code` recorded; release adds `RQP-T4-05`. RTV feeds a supplier return document, which is `p2-13`'s | inspection service |
| RQP-T4-09 | Inspection Complete | nothing moves — `result` and the per-line results only | inspection service |
| RQP-T4-10 | Session Complete / Cancel; GRN Cancel | nothing moves | session / GRN service |
| RQP-T4-11 | Putaway Complete | a two-line conserving movement staging → actual through `MPR-T1-01`; `whb_tasks.completion_movement_id`, `completed_at`; `actual_location_id`, `override_reason_code_id`; outbox `putaway.task.completed` and `task.completed`; the referenced `rule_id` is frozen by `I-24` | putaway service (`WH-SC-052`) |
| RQP-T4-12 | Reversal Post | a `REVERSAL` movement through `MPR-T1-08` (own idempotency key, reason); `reversal_movement_id` stored; GRN → `REVERSED`; PO line decrement and `line_status` regress (`RQP-T1-13`); cost per `MPR-T4-05`; outbox `stock.movement.reversed` (`MPR-T4-07`); handover per `MPR-T4-08`. Both documents stay visible | reversal service, one transaction |
| RQP-T4-13 | PO Cancel | every line → `CANCELLED`; the cascade to the PO's non-completed GRNs and receiving session is **OPEN-21** | PO service |
| RQP-T4-14 | Close short | the line leaves the open-PO report; the remainder is `cancelled_quantity`; **no automatic backorder**. Whether a header Close closes its open lines is `TBD` | PO service (`WH-SC-068`) |
| RQP-T4-15 | Over-receipt refused (`RQP-GRD-06`) | nothing posts. Auto-creating the `OVER_RECEIPT` reconciliation case is `WH-SC-084` (v1·P2), and **the case never moves stock** | reconciliation (`p2-13`, `FR-138`) |

---

## 5. T5 — Screen contract (web only — see §0)

### 5.1 `/warehouse/inbound/receiving-sessions` — WS-075 Receiving Sessions

| | |
|---|---|
| **Type** | list + transition modals (reference: **Service Vehicle**) |
| **Grid identifier** | `wh_receiving_sessions` · filter scope `WAREHOUSE_RECEIVING_SESSION` |
| **Default sort** | `TBD` |
| **Statistics tiles** | `TBD` — no source names any |
| **Columns** | `sessionNumber`, `warehouseName`, `dockDoorCode`, `supplierName` (nullable), `carrierName`, `vehicleNumber`, `driverName`, `sealNumberIn`, `sealNumberOut`, `gatePassRef`, `arrivedAt`, `startedAt`, `completedAt`, `status`, `documentCount`, `grnCount`, audit |
| **Filters** | `warehouseId` → `dockDoorId` → `status`; `supplierCounterpartyId` typeahead; `vehicleNumber` text; `arrivedFrom`/`arrivedTo` (`date`); `openOnly` |
| **Row actions** | Start → `RQP-T2-02` · Attach PO/ASN → `RQP-T2-03` · Create GRN → `RQP-T2-06` · Record seals → `RQP-T2-03` · Complete → `RQP-T2-04` · Cancel → `RQP-T2-05` |
| **Toolbar** | `TBD` — no Gate-in/Add named (hole H1) |
| **Export columns** | `TBD` — no source states the export; audit names required because the grid shows audit |
| **Mobile counterpart** | none (§0) |

### 5.2 `/warehouse/inbound/goods-receipts` — WS-076 Goods Receipts · `/[id]` — WS-077

| | |
|---|---|
| **Type** | list + transition modals (reference: **Service Vehicle**); WS-077 is a route with tabs |
| **Grid identifier** | `wh_goods_receipts` · filter scope `WAREHOUSE_GOODS_RECEIPT` |
| **Default sort** | `TBD` |
| **Statistics tiles** | `TBD` |
| **Columns** | `grnNumber`, `sessionNumber`, `poNumber`, `asnNumber`, `supplierName`, `warehouseName`, `ownerName`, `receivedByName`, `receivedAt`, `isBlindReceipt`, `receivingMode`, `grnTiming`, `status`, `matchStatus` (values: **OPEN-18**), `lineCount`, `receivedQuantity`, `acceptedQuantity`, `rejectedQuantity`, `freeQuantity`, `invoiceMatched`, audit |
| **Filters** | `warehouseId` → `supplierCounterpartyId` → `status` (**multiselect**); `matchStatus`; `isBlindReceipt`; `poNumber` (reads through `po_line_id`, `RG-019`); `grnNumber`; `receivedFrom`/`receivedTo` (`date`); `awaitingQc`; `awaitingPutaway` |
| **Row actions** | View → WS-077 · **Post** → `RQP-T2-08` (`DRAFT`) · **Reverse** → WS-078 (`POSTED`, **OPEN-10**) · **Inspect** → WS-080 · **Putaway** → WS-082 · Print GRN · Raise reconciliation case → WS-083. **Cancel is not listed** although the ladder has it (hole H1) |
| **Modals** | Blind receipt · Receive line · Over/short · Post. **No edit modal for a posted GRN** (`RQP-UNR-01`) |
| **Export columns** | header + line grain: `lineNo`, `poLineNo`, `itemCode`, `expectedQuantity`, `receivedQuantity`, `acceptedQuantity`, `rejectedQuantity`, `freeQuantity`, `schemeReference`, `uomCode`, `conversionFactorUsed`, `lotCode`, `expiryDate`, `unitCost`, `stockStatusCode`, `putawayLocationCode`, `crossDockReference`, plus `createdByName`, `updatedByName` |
| **WS-077 tabs** | Lines · Serials · QC · Putaway · Movements · Landed costs · Reversals · Documents · Audit |
| **Mobile counterpart** | none (§0) |

### 5.3 `/warehouse/inbound/purchase-orders` — WS-072 and `/[id]` — WS-073 (the receipt-facing part)

| | |
|---|---|
| **Grid identifier** | `wh_purchase_orders` · filter scope `WAREHOUSE_PURCHASE_ORDER` · cache `dropdown.whPurchaseOrder` |
| **Receipt-facing columns** | `status`, `orderedQuantity` / `receivedQuantity` / `cancelledQuantity` (**backend-computed** Σ of line counters), `ownershipTransferPoint`, audit quartet + names (a document, not a ledger row) |
| **Receipt-facing filters** | `status` **multiselect**; `overdueOnly` (backend-computed, site timezone); `openOnly`; both date pairs `dateOnly` |
| **Statistics tiles** | open POs · overdue · fully received this month · value on order |
| **Receipt-facing actions** | Receive against → WS-075 pre-filled · **Cancel** → `RQP-T2-12` · **Close short** → `RQP-T2-11` · **Reopen** (no ladder row — **OPEN-07**) |
| **WS-073** | a route, not a modal: Lines · GRNs · QC results · Putaways · Invoices / three-way match · Returns · Exceptions · Movements (`FR-036` lineage) · Documents · Audit — child grids, **no `gridIdentifier` per tab**. The three quantities are shown side by side and never reconciled away (`FR-123`, `WH-SC-065`, `WH-SC-069`) |
| **Mobile counterpart** | none (§0) |

### 5.4 `/warehouse/inbound/quality-inspections` — WS-080, and `/warehouse/inbound/inspection-plans` — WS-079

| | |
|---|---|
| **Grid identifiers** | `wh_quality_inspections` · `WAREHOUSE_QUALITY_INSPECTION` (Service Vehicle); `wh_inspection_plans` · `WAREHOUSE_INSPECTION_PLAN` (Customer) |
| **WS-080 columns** | `inspectionNumber`, `grnNumber`, `planName`, `inspectorName`, `startedAt`, `completedAt`, `result` (literal **OPEN-01**), `dispositionCode`, `inspectedQuantity`, `passedQuantity`, `failedQuantity`, audit |
| **WS-080 filters** | `warehouseId` → `planId` → `result`; `inspectorId` typeahead; `dispositionCode`; `startedFrom`/`startedTo` (`date`). `result` and `dispositionCode` **fetch** their values from the registry, never a TypeScript union (`OD-5`, `FR-380`) |
| **WS-080 actions** | Start → `RQP-T2-13` · Record results · **Disposition** → `RQP-T2-14` · Complete. Scrap approval has no named action (hole H3) |
| **WS-079** | columns `code`, `name`, `inspectionType` (`FULL`/`SAMPLING`/`SKIP_LOT`), `samplingPlan`, `sampleSizeFormula` (whitelisted), `aql`, `criterionCount`, `isActive`, audit; filters `inspectionType`, `isActive`, `code`/`name`; Add/Edit with a child editor over `wh_inspection_plan_criteria` |
| **Default sort · tiles · export** | `TBD` for both |
| **Mobile counterpart** | none (§0) |

### 5.5 `/warehouse/inbound/putaway-tasks` — WS-082, and `/warehouse/inbound/putaway-rules` — WS-081

| | |
|---|---|
| **Grid identifiers** | `wh_putaway_tasks` · `WAREHOUSE_PUTAWAY_TASK` (Service Vehicle); `wh_putaway_rules` · `WAREHOUSE_PUTAWAY_RULE` (Customer) |
| **WS-082 columns** | `taskNumber` (from `whb_tasks`), `grnNumber`, `itemCode`, `quantity`, `lotCode`, `lpnCode`, `suggestedLocationCode`, `actualLocationCode`, `overrideReasonName`, `stagingLocationCode`, `ruleName`, `status`, `assignedToName` (the shared user-display helper) |
| **WS-082 filters** | `warehouseId` → `status` (**multiselect**) → `assignedTo` typeahead; `grnNumber`; `itemId` typeahead; **`hasOverride`** — the report that finds a wrong rule |
| **WS-082 actions** | Assign → `RQP-T2-16` · **Complete** → `RQP-T2-17` (own modal: scan location, override reason) · Cancel → `RQP-T2-18` |
| **WS-081** | columns `code`, `name`, `warehouseName`, `sequence`, `scopeCategoryName`, `scopeItemCode`, `scopeStatusCode`, `strategy` (whitelisted, fetched), `isActive`, audit; filters `warehouseId` → `strategy`, `isActive`; actions Add / Edit / **Reorder** (copy-on-write, `RQP-T1-33`) / **Test** (`RQP-T1-34`) |
| **Grid config** | both grids ship `default_columns` **and** `default_filters`; both scopes registered (`p1-15` Acceptance) |
| **Default sort · tiles · export** | `TBD` for both |
| **Mobile counterpart** | none (§0) |

### 5.6 `/warehouse/inbound/receipt-reversals` — WS-078

| | |
|---|---|
| **Type** | list + transition modals (reference: **Service Vehicle**); statistics `—` (filter-aware, `FR-395`) |
| **Grid identifier** | `wh_receipt_reversals` · filter scope `WAREHOUSE_RECEIPT_REVERSAL` |
| **Columns** | `reversalNumber`, `grnNumber`, `reasonCodeName`, `requestedByName`, `approvedByName`, `approvedAt`, `status`, `reversalMovementSequenceNo`, audit quartet + names |
| **Filters** | `warehouseId`; `status`; `reasonCodeId` (fetched from `whb_reason_codes`, never a union); `requestedFrom`/`requestedTo` (`date`) |
| **Actions** | **Request** → `RQP-T2-19` · **Approve** → `RQP-T2-20` · **Post** → `RQP-T2-21`. Reject is on the ladder and not on the screen (hole H1) |
| **Default sort · export** | `TBD` |
| **Mobile counterpart** | none (§0) |

Screens this workflow feeds but does not own: WS-040/WS-041 (the movements, `MPR`), WS-042 (positions, and
*Change status* for QC-held stock with no inspection — hole H14), WS-059 (tasks, `p0-10`), WS-064 (job
runs), WS-083 (reconciliation cases), WS-084 (supplier returns).

---

## 6. Out of scope (explicit decisions)

| Baseline item | Decision | Reason | Revisit |
|---|---|---|---|
| Mobile and RF screens — `screens/whPurchaseOrder`, `whReceivingSession`, `whGoodsReceipt`, `whQualityInspection`, `whPutawayTask`; WS-229 RF Receive; WS-230 RF Putaway | **not built** | user scope rule of 2026-09-11 (§0); sources to be amended (**OPEN-16**) | only if the user reverses the rule |
| Movement post / reverse mechanics, period gating, availability, idempotency | [`movement-post-reverse.contract.md`](movement-post-reverse.contract.md) | cited by `MPR-*` id, never restated | — |
| PO authoring ladder (Create, Submit, Approve, Return for correction) | BUILD-SPEC §0.11 rows, cited | this contract covers the PO only where receipts drive or gate it | a PO contract |
| ASN as a document (`wh_asns`, WS-074) and the ASN clause of the cancel guard | v1.1 (`P3-05`) | `wh_asns` has no status values in v1 (`RJ-018`) | v1.1 |
| Task-driven putaway, claiming, the putaway optimiser | `P3-02`, `P3`, `P6` | v1 ships the evaluation harness only (`FR-135`) | P3 / P6 |
| Inspection plan per item × supplier × site (`wh_inspection_plan_assignments`, `V510220`) | v2 | v1 keeps the category default (`RG-018`) | v2 |
| Cross-dock flow, three-way match | v2 | v1 ships the nullable `cross_dock_reference` column only (`FR-137`) | v2 |
| Reconciliation case lifecycle, supplier returns | `p2-13` | T4 cross-reference only | P2 |
| Cost layers and landed-cost arithmetic | `p0-17` / `p2-16` under `D-15` | cited, never restated | — |
| Receipt shelf-life enforcement | `p2-05` | v1 ships the columns (`p1-03`) | P2 |
| Dock appointments and the detention clock | WS-086, v1.1 scheduling | schema only in v1 | v1.1 |

---

## 7. Amendments

| Date | Row IDs affected | Change | Found by |
|---|---|---|---|
| 2026-09-12 | all | v0 derived from the design set at `57bd7df`; unratified | `functional-reviewer`, derive mode (task W0-2b) |

---

## 8. Invariants and scenarios this workflow must not break

| Invariant | Rows that carry it | Scenarios that prove it |
|---|---|---|
| `L-1` conservation | `RQP-T4-01`, `RQP-T4-11`, `RQP-GRD-23` | `WH-SC-051`, `WH-SC-052`, `WH-SC-063`, `WH-SC-066`, `WH-SC-069`, `WH-SC-073` |
| `L-2` append-only | `RQP-UNR-01`, `RQP-UNR-05` | `WH-SC-081` |
| `L-3` correction is reversal | `RQP-T1-29`…`-32`, `RQP-UNR-06`, `RQP-UNR-12` | `WH-SC-081`, `WH-SC-082` |
| `L-7` frozen factor | `RQP-GRD-02`, `RQP-T4-01` | `WH-SC-078` |
| `L-8` period-bound | `RQP-GRD-09`, `RQP-GRD-26` | `WH-SC-021` |
| `L-9` idempotent ingestion | `RQP-GRD-27` | `WH-SC-081` |
| `L-12` traceability | `RQP-T4-03` | `WH-SC-051`, `WH-SC-079` |
| `L-13` timestamps (and `IRR-23`) | `RQP-T3-05` | `WH-SC-052` |
| `D-15` never restate | `RQP-T4-06` | `WH-SC-085` |
| `FR-408` maker–checker | `RQP-GRD-19`, `RQP-GRD-25` | `WH-SC-071` |
| Other scenarios in scope | sessions, PO roll-up, inspection, numbering, identifiers, events | `WH-SC-064`, `WH-SC-065`, `WH-SC-067`, `WH-SC-068`, `WH-SC-070`, `WH-SC-071` (v1·P2, owned by `p2-01`), `WH-SC-074`, `WH-SC-075`, `WH-SC-076`, `WH-SC-077`, `WH-SC-080`, `WH-SC-083`, `WH-SC-084`, `WH-SC-086`, `WH-SC-142`, `WH-SC-175`, `WH-SC-176`, `WH-SC-194`, `WH-SC-294`, `WH-SC-301` |

---

## 9. Open rows — contradictions between sources, and holes no source fills

**Contradictions.** Each is left open for the ratifier. Where the design set's own precedence rule points
one way, the row says so. That is a pointer, not a decision.

| ID | Contradiction | Source A | Source B | Rows affected | Precedence pointer |
|---|---|---|---|---|---|
| RQP-OPEN-01 | The mixed-result rollup literal stored in `wh_quality_inspections.result` | `PARTIAL` — `DATA-MODEL.md` §2.2.1, BUILD-SPEC WS-080, `issues/p1-14.md` (three places) | `CONDITIONAL` — `FR-133`, `WH-SC-070` | GRD-17, WS-080 | filed as `X-055`, a product-owner naming decision; all five sites change in one commit |
| RQP-OPEN-02 | Where `match_status` lives | GRN **header** column — `DATA-MODEL.md` §2.2.1, `issues/p1-13.md`, WS-076 | the **PO line** — *"the PO line's received quantity becomes 240 and its `match_status` is `MATCHED`"* (`WH-SC-051`); *"the PO line closes at 160 with `match_status = QTY_UNDER`"* (`WH-SC-068`). `wh_purchase_order_lines` has `line_status`, no `match_status` | GRD-06, T4-02, T1-14 | DATA-MODEL owns schema |
| RQP-OPEN-03 | Where the explicit close-short action lives | the **PO** — WS-072 *Close short* modal, `p1-12` line ladder (`wh_purchase_orders:edit`), `WH-SC-068` | the **GRN** — `issues/p1-13.md` Scope (*"`match_status` … and an explicit close-short action"*) and Acceptance (*"a short receipt offers an explicit close-short action"*); WS-076 lists no such action | T1-14, T2-11, WS-072, WS-076 | BUILD-SPEC owns screen contracts, and it puts it on WS-072 |
| RQP-OPEN-04 | Whether a GRN may span POs | *"each GRN belongs to exactly one PO"* — `WH-SC-064` | a GRN over two POs stores `po_id = null` and is found through its lines — `RG-019` in `issues/p1-13.md` and `DATA-MODEL.md` §2.2.1 | T4-02, WS-076 `poNumber` | DATA-MODEL owns schema; the round-4 fold is later |
| RQP-OPEN-05 | A damaged quantity on the GRN line | *"received 240, accepted 228, rejected 0, damaged 12 — the GRN carries all four columns independently"* — `WH-SC-069` | `wh_goods_receipt_lines` carries received / accepted / rejected / free quantity, `condition_code` and `damage_notes` — **no damaged quantity** — `DATA-MODEL.md` §2.2.1 | T1-08, export | DATA-MODEL owns schema |
| RQP-OPEN-06 | Whether stock found damaged at receipt enters its non-available status in the receipt itself or by a second movement | *"the 12 land in a `DAMAGED` stock status … by a balanced status-change movement"* — `WH-SC-069` | *"receipt into a non-available status on the first transaction"*; a second transaction is the defect — `FR-129`, `WH-SC-073` | T4-01, GRD-07 | DECISIONS / FRD over a scenario fixture; the two may be reconcilable (damage found after receipt) |
| RQP-OPEN-07 | Whether a PO can be reopened | WS-072 *Modals* and `issues/p1-12.md` list a **Reopen** transition modal | BUILD-SPEC §0.11 marks `CLOSED` and `CANCELLED` terminal and has no Reopen row. The §0.11 row *Return for correction* (`SUBMITTED → DRAFT`) has no modal on WS-072 either | §1.1, UNR-03, WS-072 | BUILD-SPEC disagrees with itself (§0.11 vs WS-072) |
| RQP-OPEN-08 | Whether a v1 putaway task is open work or auto-completed | *"v1 creates one task per putaway line … and completes it in the same request"*, `assigned_at = started_at = completed_at = now()` — `issues/p0-10.md`; `whb_tasks` purpose in `DATA-MODEL.md` §2.1.13; `WH-SC-052` | the task is created at GRN post or at release (`RJ-017`) and completed later through WS-082 **Assign** and the **Complete** modal, with explicit assignment in v1 — `issues/p1-15.md`, WS-082 | T1-24…-27, T3-02 | the round-4 fold (`RJ-017`) is later than `p0-10`'s body; neither amends the other |
| RQP-OPEN-09 | What *"moved on"* means for a receipt reversal | *"put away **and** picked, or their status changed, or they have left the site"* — `issues/p1-16.md` Scope | a relocation alone counts: *"(24 shipped, **120 relocated**)"* — `WH-SC-082`; the reversible case is *"the stock is still at `RECV-01`"* — `WH-SC-081`. Whether a completed putaway alone blocks reversal is read two ways | GRD-26 | the catalogue owns fixtures; `FR-131` says only *"moved on"* |
| RQP-OPEN-10 | The permission behind reversing a receipt | `wh_goods_receipts:reverse` — `issues/p1-20.md` *The verb permissions this wave adds* | `wh_receipt_reversals:create` / `:approve` / `:post`, and the GRN ladder's `POSTED → REVERSED` gated on `wh_receipt_reversals:post` — `issues/p1-13.md`, `issues/p1-16.md`, BUILD-SPEC §0.11, §10.2 | T1-11, T2-22, WS-076 | BUILD-SPEC §10.2 and §0.11 are *"the same list read from two sides"*; `p1-20` carries an extra string |
| RQP-OPEN-11 | Putaway task verbs | `wh_putaway_tasks:complete` is seeded — `issues/p1-20.md` | BUILD-SPEC §10.2 names **no** putaway-task verb; Assign and Cancel have no verb in any source, so by §10.2's own rule they fall to anyone with `:edit` | T1-25…-27, T2-16…-18 | BUILD-SPEC §10.2 owns verb strings |
| RQP-OPEN-12 | The disposition vocabulary QC writes | release / reject / return to supplier / scrap — WS-080, `FR-134`, `issues/p1-14.md`; the rejected stock moves to `REJECTED` — `WH-SC-071` | the `whb_dispositions` seed is `RESTOCK_SELLABLE`, `RESTOCK_UNSELLABLE`, `REFURB`, `REPACK`, `SCRAP`, `RTV`, `DONATE`, `HOLD_FOR_CLIENT`, `RETURN_TO_CLIENT` (no release, no reject), and the stock-status seed has no `REJECTED` — `issues/p0-05.md` (`RE-005`), which makes *"a code that appears in a requirement … and not in the seed"* a merge blocker | T1-20, T1-21, GRD-18 | `p0-05`'s merge-blocker rule: the seed gains the codes, or the QC verbs map onto seeded ones |
| RQP-OPEN-13 | Where a scrap waits for approval, who approves it, and what it posts | a document-level pending state approved by `wh_quality_inspections:approve`; *"only then does the status movement post"* — `issues/p1-14.md` (`RJ-005`), BUILD-SPEC §10.2 round-4 table. `wh_quality_inspections` / `_lines` carry no status or approval column — `DATA-MODEL.md` §2.2.1 | a movement-level `approval_status` for `requires_approval` types, *"v1 (scrap)"* — `IRREVERSIBLE.md` §4.1, approved by `whb_stock_movements:approve` (`MPR-T1-04`, `MPR-T1-05`). And a scrap elsewhere is an issue to `VIRT-SCRAP`, not a status change | §1.1, T1-22, T1-23, GRD-19, T2-15 | open: two approval homes; DATA-MODEL owns schema and has columns only for the movement-level one |
| RQP-OPEN-14 | The last rung of the over-receipt tolerance ladder, and its columns | PO line → PO header → item → warehouse → **`BLOCK`** — `issues/p1-03.md` (`RE-004`), `issues/p1-13.md`. `FR-130`: *"a tolerance on the item and a warehouse default"* (two levels) | PO line → PO header → item → warehouse → **global** `warehouse.receiving.over_receipt_percent` (default 0, 0–100) — `GLOBAL-SETTINGS-DECISIONS.md`, `issues/p1-12.md`. And `wh_purchase_order_lines` has **no** tolerance column; only the header carries `over_receipt_tolerance_pct` — `DATA-MODEL.md` §2.2.1 | GRD-06 | `GLOBAL-SETTINGS-DECISIONS.md` is DECISIONS' adopted amendment (default 0 blocks, so the outcomes agree); the PO-line column is a schema gap |
| RQP-OPEN-15 | Whether a blind receipt names a counterparty | *"Every inbound receipt names a counterparty"* — `FR-120`, `issues/p1-13.md` Scope | blind receipt needs item, quantity, UoM, owner, status and location — *"nothing else required"* — `FR-128`, `issues/p1-13.md`, `WH-SC-063` (which cites both) | GRD-01 | open; both are v1 FRs |
| RQP-OPEN-16 | Mobile scope | user scope rule of 2026-09-11: warehouse gets **no mobile app** (already written into `issues/p1-12.md` and `issues/p1-13.md` as `RB-001` lines) | `issues/p1-14.md` Acceptance (*"the mobile inspection screen records results"*) and its v2 increment; `issues/p1-15.md` Acceptance (*"the mobile decision recorded per screen"*); `issues/p1-12.md` Acceptance (*"the mobile PO screen is read-only"*); BUILD-SPEC WS-072, WS-075/076 and *Mobile for §3.1* paragraphs; `WH-SC-227`; `D-13`. Same conflict as `MPR-OPEN-13` | §0, §6, T5 | a user decision outranks the set; `p1-14`, `p1-15` and the acceptance lines are not yet amended |
| RQP-OPEN-17 | Whether a fully received PO line is closed | *"the PO line **closes** as fully received"* — `WH-SC-066` | `RECEIVED` is non-terminal and a line reaches `CLOSED` only by an explicit Close / Close short (`wh_purchase_orders:edit`) — `issues/p1-12.md` line ladder, BUILD-SPEC §0.11 | T1-12, T1-14 | the ladder is the ratifiable text (§0.11 *"ratify each block"*); the scenario's word may be loose |
| RQP-OPEN-18 | `match_status` values on WS-076 | `MATCHED`/`QTY_OVER`/`QTY_UNDER` — BUILD-SPEC WS-076 column, `FR-130` | adds `ITEM_MISMATCH` (a received item on no attached PO line) — `DATA-MODEL.md` §2.2.1, `issues/p1-13.md` (`RJ-014`) | WS-076 | DATA-MODEL owns schema; the round-4 fold is later |
| RQP-OPEN-19 | Which tolerance bounds the short side of a PO line | the line is `RECEIVED` when *"ordered − received ≤ the **over-receipt** tolerance"* — `issues/p1-12.md` line ladder, BUILD-SPEC §0.11 header row | the item carries a separate **`short_receipt_tolerance_pct`** — `issues/p1-03.md` (`RE-004`); the settings catalogue has no short-receipt key | T1-12 | DATA-MODEL owns columns; the ladder text predates `RE-004` |
| RQP-OPEN-20 | Partial receipt reversal | per-line reversal **quantity** in `wh_receipt_reversal_lines` — `DATA-MODEL.md` §2.2.1; a partly-moved receipt reported as *"144 EA … have moved on"* — `WH-SC-082` | the reversal mirrors the original movement **line for line** (`MPR-GRD-14`), one reversal per movement (`MPR-UNR-05`), and the GRN goes to terminal `REVERSED` on the first reversal — `issues/p1-13.md` ladder | T1-29, T1-32, GRD-26 | open; `L-3` (DECISIONS) favours whole-movement mirroring |
| RQP-OPEN-21 | The PO cancel cascade into sessions | cancellation *"cascades to its receiving session and every non-completed GRN"* — `WH-SC-083` | cancel is refused while any attached session is `ARRIVED` or `UNLOADING` (`RJ-018`), and those are the only non-terminal session states (`issues/p1-13.md`) — so the cascade can never reach a live session. A session also serves N POs, so cancelling it for one PO would strand the others | T1-15, T4-13 | the round-4 guard (`RJ-018`) is later and is written into the same scenario |

**Holes.** No source answers these, so nothing is contradicted. Each blocks a row from being fully
checkable.

| ID | Hole | Rows |
|---|---|---|
| H1 | **Entry points missing from the screens.** The session's Gate-in (`— → ARRIVED`), GRN **Cancel** (`wh_goods_receipts:cancel`) and reversal **Reject** are ladder rows with a seeded verb and no action on WS-075, WS-076 or WS-078 | T1-01, T1-10, T1-31 |
| H2 | Whether a GRN (a blind receipt in particular) requires a receiving session; `session_id`'s nullability is unstated | T1-07 |
| H3 | Scrap approval: which screen offers **Approve**, and a pending scrap has no decline or withdraw exit | T1-22, T1-23 |
| H4 | An `APPROVED` reversal whose Post is refused (the stock moved on after approval) has **no exit** — no cancel, withdraw or expiry | §1.1, T1-32 |
| H5 | Whether a GRN may be created or posted against a PO not yet `APPROVED` — the PO ladder's first receipt row starts at `APPROVED` and no guard says so | T1-07, T1-12 |
| H6 | The PO **header** after a receipt reversal: the line ladder regresses, the header ladder has no row out of `RECEIVED` / `PARTIALLY_RECEIVED` except `CLOSED` | T1-13, §1.1 |
| H7 | Whether Disposition requires the inspection to be complete; whether a re-inspection may re-disposition stock already released. BUILD-SPEC §0.11 *Still owed* also lists *"is a disposition reversible before the putaway posts?"* against this task, and `p1-14` does not answer it | T1-20…-23, T2-14 |
| H8 | Putaway **Cancel**: where the stock at staging goes and whether a replacement task is raised; who sets `staging_location_id` and what `wh_goods_receipt_lines.putaway_location_id` means next to the task's actual location | T1-27 |
| H9 | `whb_tasks`' ladder (exits of `PAUSED` and `EXCEPTION`, Reassign) is `p0-10`'s and is not written as §0.11 rows | §1.1 |
| H10 | `SERIAL_REQUIRED` (`WH-SC-079`) is not in `FR-039`'s stable vocabulary; neither are `INSPECTION_INCOMPLETE`, `INSPECTION_ALREADY_COMPLETED`, `ITEM_IDENTIFIER_CONFLICT` or `AMBIGUOUS_IDENTIFIER` (the last is in BUILD-SPEC §0.13) | GRD-03, GRD-05, GRD-15, GRD-16 |
| H11 | The refusal **codes** for over-receipt, session complete/cancel, GRN cancel, PO cancel (both blockers), close-short without reason, a missing override reason, a non-whitelisted value and *"moved on"* are never allocated | GRD-06, -10…-14, -20, -21, -24, -26 |
| H12 | `dock_to_stock_completed_at` (GRN) and `first_receipt_at` (PO) have no setter in any source | T3-05 |
| H13 | The counter-side virtual location of a blind receipt that is not a supplier's goods (a customer's repair, a 3PL client's goods, `WH-SC-063`); and what counts as an *available* status for `RJ-017` | T4-01, T4-05 |
| H14 | QC-held stock of an item whose category has no inspection plan (*"verification without inspection remains possible"*, `p1-14`): its only exit is WS-042 *Change status* (`MPR-T1-10`), whose permission is `MPR` §9 G3 | §5 |
| H15 | Untracked dated obligations: a session left `ARRIVED`/`UNLOADING`, a `DRAFT` GRN, uninspected QC-held stock, a `REQUESTED`/`APPROVED` reversal and a pending scrap have no ageing or reminder rule; whether `warehouse.approval.pending_alert_hours` covers the last two is unstated | T3 |
| H16 | Default sort, statistics tiles and export columns for WS-075, WS-078…WS-082; the WS-076 tiles | T5 |
| H17 | Permissions for Receive line, Attach PO/ASN, Record seals, inspection Start / Record results / Complete, and rule Test | T1-03, -04, -08, -16…-18, -34 |

<!-- Ratify with /functional-contract. A derived contract proves nothing until a human has ratified it. -->
