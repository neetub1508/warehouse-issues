# Functional Contract — Inspection sampling (bands, fixed, percentage, AQL), plan assignment, polymorphic QC source, raise supplier return

> **What this is.** The functional truth for *how much* is inspected and *against what*: sampling schemes
> with band tables, the fixed and percentage formulas, the kept Z1.4 table, the plan-assignment
> precedence, the lot verdict from Ac/Re, destructive test quantity, the polymorphic inspection source,
> and the manual **Raise supplier return** action. It **extends** `RQP-T1-16`…`-23`, `-36`
> ([`receipt-qc-putaway.contract.md`](receipt-qc-putaway.contract.md)); the inspection's derived state
> (in progress / completed), its disposition and scrap approval are unchanged.
>
> **Status.** Derived 2026-10-22 (v0) from [`frd/FRD-STORES.md`](../frd/FRD-STORES.md) §6.5–6.6
> (`FR-521`…`FR-526`). Not ratified.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Scheme maintain → plan configure → assignment resolve → inspection start (source-polymorphic) → sample proposed → results → complete with lot verdict → disposition (whole-lot or per line) → destructive qty consumed → **Raise supplier return** (manual) |
| **Module** | `warehouse`; code lists `QC_SOURCE_TYPE`, `INSPECTION_STAGE` in `warehouse-base` (`V501231`, owned by `P8-06`) |
| **Domain baseline** | `FR-127`, `FR-133`, `FR-139` (amended by `FR-526`), `FR-041` (no expressions), `FR-383` (no JSONB) · `STO-D6`, `STO-D7` · IS 2500 (Part 1) ≡ ISO 2859-1 ≡ ANSI/ASQ Z1.4 single sampling, normal, level II |
| **Owning tasks** | `issues/p8-05.md` (schemes, plan columns, assignments, formulas, verdict, destructive qty) · `issues/p8-06.md` (polymorphic source) · `issues/p8-07.md` (raise supplier return) |
| **Primary tables** | new `wh_sampling_schemes`, `wh_sampling_scheme_bands`, `wh_inspection_plan_assignments` (`V511314`); ALTER `wh_inspection_plans` (`V511314`): `sampling_scheme_id`, `fixed_sample_quantity`, `sample_percent`, `min_sample_quantity`, `inspection_level`; formula CHECK widened with `BAND_TABLE`; ALTER `wh_quality_inspection_lines` (`V511314`, `P8-05` — the task file wins, so `P8-06` does not recreate them; P8-05 S1 `G11`): `plan_id`, `plan_assignment_id`, `sampling_scheme_id` (the **version row** used — every scheme version is its own `wh_sampling_schemes` row, so one column name serves; R29 F30) per line (P8 decision `G5`), `sample_size_proposed`, `accept_number`, `reject_number`, `defective_count`, `lot_verdict_proposed`, `lot_verdict`, `lot_verdict_override_reason`, `destructive_quantity`, `destructive_movement_id`, and the destructive-test cost object `destructive_cost_object_type_list` / `_type` / `_id` / `_ref` (R29 F11); ALTER `wh_quality_inspections` (`V511314`): `plan_assignment_id`, `sampling_scheme_id` — the header `plan_id` / `plan_assignment_id` / `sampling_scheme_id` are set only when every line resolves the same, else NULL; ALTER `wh_quality_inspections` / `_lines` (`V511315`, `P8-06`): `source_type(_list)`, `source_document_id`, `source_line_id`, `source_document_ref`, `inspection_stage(_list)`, `grn_id`/`grn_line_id` nullable, `item_id`, `lot_id`, `warehouse_id`, `held_location_id`; ALTER `wh_supplier_returns` / `_lines` (`V511316`): `origin_inspection_id`, `origin_inspection_line_id` |
| **Permission resources** | `wh_sampling_schemes:{view,view:all,view:branch,create,edit,export}` · `wh_inspection_plan_assignments:{view,view:all,view:branch,create,edit,export}` (the scope pair on every new resource, R29 F1 — company masters with no site column resolve unscoped for `:view:branch` holders) · new verb `wh_quality_inspections:raise_supplier_return` (`V511404`, `V511406`) |
| **Routes** | WS-264 `/warehouse/quality/sampling-schemes` · WS-265 `/warehouse/quality/plan-assignments` · WS-079, WS-080 (changed) |
| **Contract version** | `v0 — 2026-10-22` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | The client's own bands configurable and contiguous (`WH-SC-442`, `-443`, `-475`) | `IIS-T1-01`…`-03`, `IIS-GRD-01`…`-03` |
| A2 | FIXED and PERCENTAGE really compute (`WH-SC-444`…`-446`) | `IIS-GRD-04`, `IIS-T1-06` |
| A3 | Z1.4 kept as one option, unchanged | `IIS-T1-06` row `AQL_TABLE` |
| A4 | Plan chosen per item / category / supplier (`WH-SC-447`, `-448`) | `IIS-T1-05` |
| A5 | Ac/Re proposes a lot verdict; destructive qty balances (`WH-SC-449`, `-450`) | `IIS-T1-08`, `IIS-T4-02` |
| A6 | Production and store-return sources work without a GRN (`WH-SC-451`, `-469`) | `IIS-T1-07`, `IIS-GRD-07` |
| A7 | Reject → supplier return is one press, manual, never automatic (`WH-SC-452`, `-453`) | `IIS-T1-10`, `IIS-UNR-01` |

---

## 1. T1 — State machine

### 1.1 Status inventory (additions)

| Entity | Status | Represented by | Kind |
|---|---|---|---|
| Sampling scheme | `ACTIVE` / `INACTIVE` + `version_no` | registry convention; copy-on-write versions (`supersedes_id`) | registry |
| Plan assignment | current / ended | `effective_from` / `effective_to` (half-open) | dated fact — **[!]** *current* on the grid, its `currentOnly` filter and its statistics is judged on the **UTC** day (display meaning only, labelled in help: an assignment carries no site); **End** writes the day the user picks in a `DatePicker` (default: the user's today), and with no date the server defaults to the **latest site-local today across active sites**, so End never reaches back into a day a site has started (P8-05 S3 `F4`/`R5`) |
| Inspection | *in progress* / *completed* | unchanged (`RQP` §1.1) | — |
| Lot verdict | *proposed* → *confirmed* | `lot_verdict_proposed`, `lot_verdict` (`ACCEPT_LOT` / `REJECT_LOT` / null = per-line) | fact set at Complete |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | UI |
|---|---|---|---|---|---|---|---|---|
| IIS-T1-01 | — | Create scheme with bands | `ACTIVE` v1 | `IIS-GRD-01`…`-03` | `wh_sampling_schemes:create` | band rows | no | WS-264 **Add** |
| IIS-T1-02 | v*n* unused by any inspection | Edit bands | v*n* updated in place | same | `:edit` | — | no | WS-264 **Edit** |
| IIS-T1-03 | v*n* used by any inspection | Edit bands | v*n*+1 `ACTIVE` (a new row, `supersedes_id` = v*n*), v*n* `INACTIVE` | same | `:edit` | **in the same transaction every `wh_inspection_plans.sampling_scheme_id` pointing at v*n* is re-pointed to v*n*+1** (plans follow the latest version); inspections keep the `sampling_scheme_id` they ran with (R29 F30) | no | WS-264 **Edit** (banner *creates version n+1*) |
| IIS-T1-03a | `ACTIVE` | **Deactivate** a scheme (R29 F30) | `INACTIVE` | no active `BAND_TABLE` plan points at it, else `409 SAMPLING_SCHEME_IN_USE` naming the plans; an `is_system` scheme is never deactivated | `:edit` | — | **yes** | WS-264 row **Deactivate** / **Activate** |
| IIS-T1-03b | `INACTIVE` | **Activate** a scheme (P8-05 S1 `G11`) | `ACTIVE` | a superseded version (one with a successor, `supersedes_id` pointing at it) is never re-activated, refused `409` naming the successor; an `is_system` scheme is never inactive, so it never reaches this row | `:edit` | — | no | WS-264 row **Activate** |
| IIS-T1-04 | — | Create / end an assignment (scope `ITEM_SUPPLIER`, `ITEM`, `CATEGORY_SUPPLIER`, `SUPPLIER`, `CATEGORY`; plan **or** `NO_INSPECTION`; `effective_from`) | current | `IIS-GRD-05` | `wh_inspection_plan_assignments:create`/`:edit` | ending sets `effective_to`; never deleted; once **used** — recorded on an inspection line or header, or on a posted GRN line as the `NO_INSPECTION` decision (`wh_goods_receipt_lines.inspection_plan_assignment_id`, P8-05 S3 `F3`) — only its end can change | no | WS-265 |
| IIS-T1-05 | — | **Resolve plan** for a source line at start (and at GRN post to decide QC hold) | — | precedence: item+supplier → item → category+supplier → supplier → category → `whb_item_categories.default_inspection_plan_id` (via `whb_item_category_assignments`, today's query `WhQualityInspectionRepositoryCustomImpl.java:342-354`) → none; within a scope the latest `effective_from ≤ receipt date` wins — the assignment valid at the receipt's **site-local** date, range `[effective_from, effective_to)`; an inactive plan is skipped (deactivating a plan that a current assignment uses is allowed, P8-05 S1 `G11`) | system | `plan_assignment_id` (with `plan_id` and `sampling_scheme_id`) recorded on each inspection **line**, criteria keyed per line; the header carries them only when every line agrees, else NULL (P8 decision `G5`). `NO_INSPECTION`: when it decided a status that is not QC-held, the GRN line records the assignment (`wh_goods_receipt_lines.inspection_plan_assignment_id`, the durable record) and one `WH_GRN_LINE_NO_INSPECTION` audit entry naming the resolved status is written **after the post commits** (P8-05 S3 `F3`/`R4`); the received status is resolved in this order (P8 decision `G6b`): FR-134 regulated `QUARANTINE` wins; then an explicit line `receivedStatusCode`; then the item × site default — when the assignment is `NO_INSPECTION` and that default is QC-held (`QC_HELD_STATUSES`), fall to the `RECEIPT` movement-type default; if that is also QC-held, refuse `422 RECEIVED_STATUS_UNRESOLVED`. There is no `AVAILABLE` literal anywhere; the result then passes through `MRA-T4-01` routing (`MRN_PENDING`) like any unheld receipt | — | none (effect) |
| IIS-T1-06 | — | **Propose sample size** per inspection line from the still-held quantity *L* | — | `ALL`/no plan → *L*; `NONE` → 0; `SQUARE_ROOT_PLUS_ONE` → ⌈√L⌉+1; `AQL_TABLE` → Z1.4 GII table (unchanged constants `WhQualityInspectionSampleSize.java:35-38`); **`FIXED_QUANTITY` → `fixed_sample_quantity`**; **`PERCENTAGE` → ⌈L × `sample_percent`/100⌉, raised to `min_sample_quantity`**; **`BAND_TABLE` → the band containing ⌈L⌉: its `sample_size`, or ⌈L × `sample_percent`/100⌉**; every result capped at *L* (`RQP-GRD-20`) | system at `RQP-T1-16` | *L* is counted in the receipt line's unit (today's behaviour — `inspected_quantity` is keyed in the GRN line unit), so bands count receipt units (P8-05 S1 `G11`); `sample_size_proposed` stored; Ac/Re copied from the band (or the AQL master table when `aql` is set — `IIS-OPEN-01`) | — | WS-080 **Start** |
| IIS-T1-07 | — | **Start** an inspection of a non-GRN source (`source_type` ≠ `GOODS_RECEIPT`) | *in progress* | `IIS-GRD-07`, `-08` | `wh_quality_inspections:create` | the resolver returns item, lot, quantity held, location, warehouse, owner; one series per `(source_type, source_document_id)` | no | WS-080 **Start** (from the source screen) |
| IIS-T1-08 | *in progress* | **Complete** with `defective_count` per line | *completed* | `RQP-GRD-15`, `-17` | `wh_quality_inspections:edit` | when Ac/Re present: `lot_verdict_proposed` = `ACCEPT_LOT` if defectives ≤ Ac, else `REJECT_LOT` (with `Re = Ac + 1`, `IIS-GRD-03`, the two cover every count — R29 F22); inspector confirms (`lot_verdict`) or overrides with a reason | override only | WS-080 **Complete** |
| IIS-T1-09 | *completed*, `lot_verdict` set | **Disposition whole lot** | stock released / rejected | `RQP-GRD-18`, `-29` | `wh_quality_inspections:disposition` | one disposition per line for *(held − destructive)*: `ACCEPT_LOT` → `RESTOCK_SELLABLE` (the `MRN_PENDING` branch, `MRA-T4-01`, is `P8-08`'s — `P8-05` uses `RESTOCK_SELLABLE` / `REJECT` only), `REJECT_LOT` → `REJECT`; a disposition against the verdict that **releases** a `REJECT_LOT` lot (to an allocatable status or `MRN_PENDING`) is allowed only as `ACCEPT_UNDER_DEVIATION` against an applicable approved deviation once `P8-18` is built — otherwise `409 VERDICT_OVERRIDE_REQUIRES_DEVIATION` · `lines[i].dispositionCode` (`DEV-UNR-03`; R32-fix F-R32CQ-002 supersedes the reason-only "MRB use-as-is" of P8-05 S1 `G11`); a non-releasing override keeps the mandatory reason (`requireReason`); `destructive_quantity` posted by `IIS-T4-02` first | yes (`FR-103`) | WS-080 **Disposition** (pre-filled from the verdict: the server returns `suggestedDispositionCode` per line — registry codes resolved server-side, only while that arm is active — and the remaining held quantity; the user may override, the reason stays mandatory; P8-05 S3 `F5`) |
| IIS-T1-10 | *completed*; GOODS_RECEIPT source; Σ dispositioned `REJECT`/`RTV` not on a live (non-`CANCELLED`) supplier return > 0 | **Raise supplier return** | supplier return `DRAFT` | `IIS-GRD-09` | `wh_quality_inspections:raise_supplier_return` **and** `wh_supplier_returns:create` | `WhSupplierReturnService.create` with supplier, `origin_grn_id`, `origin_inspection_id`, reason `QUALITY_REJECTED`, one line per inspection line (qty = rejected not yet returned, lot, serials, `stock_status_code` = the target status, `origin_grn_line_id`, `origin_inspection_line_id`); **nothing approved, picked, dispatched or posted** | no | WS-080 row action **Raise supplier return** → opens WS-084 on the new return |
| IIS-T1-11 | — | **GRN post** with lines landing in a QC-held status (the shared `QC_HELD_STATUSES` set — `QC_HOLD`, `QUARANTINE` — as `WhQualityInspectionValidationService.java:151`; R32-fix F-R32CQ-025) through a resolved plan, `warehouse.quality.auto_create_inspection = true` (R32) | inspection *pending* (`started_at` null) | `IIS-GRD-11` | system, in the post transaction | header + one line per QC-held GRN line, sample proposed (`IIS-T1-06`); *Start* later stamps inspector and `started_at` | no | FR-704 · WS-080 *Pending* tab (QC worklist, ageing from GRN post) |
| IIS-T1-12 | *in progress* | **Record per-serial results** for a serial-controlled item (`serial_items_inspect_per_serial`) | *in progress* | `IIS-GRD-13` | `wh_quality_inspections:edit` | `wh_quality_inspection_serial_results` rows; the line's pass / defective count roll up from them; a rejecting disposition names the serials, each taking the **disposition's own target** — `REJECT` → `REJECTED`, `RTV` → `BLOCKED`, `SCRAP` → the virtual `SCRAP` write-off (`WhQualityInspectionDispositionService.java:43-44`, `:225`; R32-fix F-R32CQ-037) | no | FR-706 · WS-080 results grid with a serial scan field |
| IIS-T1-13 | *pending* / *in progress* | **Attach** a photo / file to a result, a line (COA with number and date) or the inspection | unchanged | `IIS-GRD-12`, `IIS-GRD-15` | `wh_quality_inspections:edit` | `wh_document_attachments` row (subject `QC_RESULT` / `QC_INSPECTION_LINE` / `QC_INSPECTION`) | no | FR-705 · WS-080 *Attachments* |
| IIS-T1-14 | — | **Resolve plan for a first article** — QC-required item, no accepted `GOODS_RECEIPT` inspection of item × supplier (or none within `first_article_lapse_days`), `first_article_required = true`; **also every GRN line with `receipt_purpose = SAMPLE_IN`** from a supplier the `ApprovedSupplierPolicy` does not approve for the item (the AVL-exempt sample, `RQP-GRD-44`; R32-fix F-R32CQ-023) | stage `FIRST_ARTICLE` | `IIS-GRD-14` | system at GRN post | the `FIRST_ARTICLE`-stage assignment, else a 100 % plan; a `NO_INSPECTION` assignment is not applied | no | FR-707 · WS-077 / WS-080 *First article* chip |
| IIS-T1-15 | — | **Periodic re-test due** (`IIS-T3-03`) | `STOCK`-source inspection *pending*, stage `PERIODIC` | — | system job | **always** one `STATUS_CHANGE` `AVAILABLE → QC_HOLD`, reason `PERIODIC_RETEST`, of the lot's **unreserved, unpicked** quantity only — the built STOCK source inspects QC-held stock only (`WhStockInspectionSource.java:117-120`), so there is no non-holding re-test and no `retest_holds_stock` setting (R32-fix F-R32CQ-013); reserved and picked quantity is not moved, is listed on the inspection as *reserved — not held*, and the lot shows a *Retest due* chip on pick; a lot with no unreserved quantity is skipped and re-evaluated the next day (R32-fix F-R32CQ-024) | no | FR-707 · WS-080 *Pending* |
| IIS-T1-16 | *completed*; `STORE_RETURN` source; rejected quantity not on a live supplier return; the lot traces to a supplier receipt (`IIS-T4-06`) | **Raise supplier return** (line rejection) | supplier return `DRAFT` | `IIS-GRD-16` | `:raise_supplier_return` + `wh_supplier_returns:create` | as `IIS-T1-10` with reason `LINE_REJECTION`, `origin_store_return_*`, `origin_mrn_id`, `origin_po_line_ref`; nothing approved or posted | no | FR-716 · WS-080 row action → WS-084 |
| IIS-T1-17 | disposition `REJECT`/`RTV`/`SCRAP` or outcome `REJECT` | **Raise the NCR** (`NCR-T1-01`) | NCR `OPEN` | `IIS-GRD-17` | system, same transaction | one NCR per rejected line; `wh_quality_inspection_lines.defect_code_id` copied | no | FR-690 · WS-080 `ncrNumber` link |
| IIS-T1-18 | *completed* | **Disposition `ACCEPT_UNDER_DEVIATION`** with an applicable deviation (`DEV-GRD-05`) | stock released as `RESTOCK_SELLABLE` | `DEV-GRD-04`, `-05` | `wh_quality_inspections:disposition` | `deviation_id` on the line; usage row (`DEV-T1-06`) | yes | FR-696 · WS-080 disposition modal |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| IIS-GRD-01 | bands start at 1, are contiguous (`lot_to + 1 = next lot_from`), no overlap, last band `lot_to IS NULL` | `422 SAMPLING_BANDS_NOT_CONTIGUOUS` · `bands[i].lotFrom` naming the first uncovered size | uk `(scheme_id, lot_from)`; CHECK `lot_to IS NULL OR lot_to >= lot_from` | FR-521 |
| IIS-GRD-02 | each band has exactly one of `sample_size` (>0, integer) or `sample_percent` (0 < p ≤ 100) | `422 SAMPLING_BAND_SIZE_REQUIRED` | CHECK `num_nonnulls(sample_size, sample_percent) = 1` | FR-521 |
| IIS-GRD-03 | single sampling: when Ac and Re are set, **`Re = Ac + 1`** (no gap, so every defective count yields a verdict; R29 F22); Ac ≥ 0; sample size ≥ Re — for a fixed `sample_size` band at save; for a `sample_percent` band **at Start**, where a computed sample below Re drops Ac/Re and the line records `no_verdict_reason = SAMPLE_BELOW_REJECT_NUMBER`, shown on Results and Complete (P8-05 S3 `F6`) | `422 SAMPLING_BAND_ACCEPT_REJECT_INVALID` | CHECK `accept_number IS NULL OR reject_number IS NULL OR reject_number = accept_number + 1` | FR-521 |
| IIS-GRD-04 | `FIXED_QUANTITY` ⇒ `fixed_sample_quantity > 0`; `PERCENTAGE` ⇒ `0 < sample_percent ≤ 100`; `BAND_TABLE` ⇒ `sampling_scheme_id` of an active scheme | `422 SAMPLE_PARAMETER_REQUIRED` · the missing field | CHECK per formula | FR-522 |
| IIS-GRD-05 | no two **current** assignments with the same scope key and overlapping ranges | `409 PLAN_ASSIGNMENT_OVERLAP` | `EXCLUDE USING gist` on `(scope_type, item_id, category_id, supplier_counterparty_id, daterange)` (`btree_gist` already required by `V500012`) | FR-523 |
| IIS-GRD-06 | the sample proposal never exceeds the held quantity | — (capped) | — | RQP-GRD-20 |
| IIS-GRD-07 | a `QualityInspectionSourceResolver` is registered for `source_type` | `422 QC_SOURCE_TYPE_UNSUPPORTED` · `sourceType` | composite FK to `QC_SOURCE_TYPE` code list | FR-525 |
| IIS-GRD-07a | **non-stock-bearing source** (`InspectableSource.stockBearing = false`, SEAM-M4, MFG `IN_PROCESS`): no held quantity, location or status; lines carry `outcome_code` (`INSPECTION_OUTCOME`: `ACCEPT`/`REJECT`/`REWORK`) and never `disposition_code`; Disposition is not offered; **no movement**; the outcome goes to the resolver's `onDisposition` — at Complete only when the result approval is `NOT_REQUIRED`, else at `INSPECTION_RESULT` approval, exactly once (`QIC-T4-02`; R32-fix F-R32CQ-010) | `409 INSPECTION_SOURCE_NOT_STOCK_BEARING` on a disposition attempt | CHECK `outcome_code IS NULL OR disposition_code IS NULL`; `item_id` nullable only when `stock_bearing = false` | FR-525 |
| IIS-GRD-08 | `GOODS_RECEIPT` ⇔ `grn_id`/`grn_line_id` set; the resolver confirms the source is inspectable (GRN `POSTED`, store return `POSTED` with a `NEEDS_INSPECTION` line, MFG's own rule) and no inspection of that source is *in progress* | `409 INSPECTION_SOURCE_NOT_INSPECTABLE` / `409 INSPECTION_IN_PROGRESS` | CHECK `(source_type <> 'GOODS_RECEIPT') OR (grn_id IS NOT NULL)` on header and `grn_line_id` on lines; uk lines `(inspection_id, source_line_id)` replaces `(inspection_id, grn_line_id)` | FR-525 |
| IIS-GRD-09 | Raise supplier return: inspection completed, source `GOODS_RECEIPT`, the rejected quantity not yet on a live return > 0 | `409 SUPPLIER_RETURN_ALREADY_RAISED` / `409 NOTHING_TO_RETURN` | — | FR-526 |
| IIS-GRD-10 | `destructive_quantity ≤ inspected_quantity` and ≤ held | `422 DESTRUCTIVE_QUANTITY_EXCEEDS_SAMPLE` | CHECK | FR-524 |
| IIS-GRD-11 | one auto-created inspection series per GRN; a GRN line already on a live inspection is not added twice; a `NO_INSPECTION` or non-QC-held line gets none | — (idempotent) | uk lines `(inspection_id, source_line_id)` | FR-704 |
| IIS-GRD-12 | *Complete* needs a `COA` attachment (and number) on every line whose plan has `coa_required`, and a photo on every result whose criterion has `photo_required` | `422 COA_REQUIRED` · `lines[i]` / `422 RESULT_PHOTO_REQUIRED` · `results[i]` | — | FR-705 |
| IIS-GRD-13 | per-serial: every sampled serial belongs to the source line; every criterion has a result per sampled serial before *Complete*; a rejecting disposition names serials whose total equals the rejected quantity | `422 SERIAL_NOT_ON_SOURCE_LINE` · `422 SERIAL_RESULTS_INCOMPLETE` · `422 SERIAL_DISPOSITION_MISMATCH` | uk `(inspection_line_id, serial_id, COALESCE(criterion_id))` | FR-706 |
| IIS-GRD-14 | a first article is never skipped by a `NO_INSPECTION` assignment and is inspected at 100 % unless a `FIRST_ARTICLE`-stage plan says otherwise | — (resolution rule) | — | FR-707 |
| IIS-GRD-15 | attachments of a *completed* inspection are read-only; unlinking never deletes the platform document | `409 SUBJECT_CLOSED_ATTACHMENTS_LOCKED` | `document_id … ON DELETE NO ACTION` | FR-705 |
| IIS-GRD-16 | the line-rejection supplier return needs a supplier origin; with two candidate GRNs the user picks one **at disposition** — a `REJECT` / `RTV` / `SCRAP` disposition of a `STORE_RETURN`-source line whose trace returns several candidates needs `originGrnLineId`, stored on the inspection line (`origin_grn_line_id`) and reused by `IIS-T4-07`, `NCR-T4-02` and the later *Raise supplier return* (R32-fix F-R32CQ-019) | `409 NO_SUPPLIER_ORIGIN` · `422 SUPPLIER_ORIGIN_AMBIGUOUS` · `lines[i].originGrnLineId` | — | FR-716 |
| IIS-GRD-17 | a rejecting disposition / outcome carries an active, stage-applicable defect code while `defect_code_required` | `422 DEFECT_CODE_REQUIRED` · `422 DEFECT_CODE_NOT_APPLICABLE` | — | FR-693 |

### 1.4 Unreachable

| ID | Must never happen |
|---|---|
| IIS-UNR-01 | a supplier return created by Complete, Disposition, a job or any path other than `IIS-T1-10` (`FR-139` amended — no silent auto-return) |
| IIS-UNR-02 | `FIXED_QUANTITY` or `PERCENTAGE` proposing the whole lot because a parameter is missing (refused at plan save instead) |
| IIS-UNR-03 | a free expression, script or JSONB in a plan or scheme (`FR-041`, `FR-383`) |
| IIS-UNR-04 | a completed inspection's verdict, scheme version or sample changed (`RQP-UNR-04`) |
| IIS-UNR-05 | an FK from `wh_quality_inspections` to a `whm_` table |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra |
|---|---|---|---|---|
| IIS-T2-01 | Maintain schemes | `wh_sampling_schemes:create/edit` | — | QA manager |
| IIS-T2-02 | Maintain assignments | `wh_inspection_plan_assignments:create/edit` | — | QA manager |
| IIS-T2-03 | Start / record / complete | `wh_quality_inspections:create/edit` | per `RQP` | inspector |
| IIS-T2-04 | Confirm / override verdict | `wh_quality_inspections:edit` | at Complete | override reason |
| IIS-T2-05 | Disposition | `wh_quality_inspections:disposition` | *completed* | QA role |
| IIS-T2-06 | Raise supplier return | `:raise_supplier_return` + `wh_supplier_returns:create` | *completed* + rejected qty unreturned | the return's approver must differ (`P2-13`) |
| IIS-T2-07 | Print rejection note (`SYS-REJECTION-NOTE`) | `wh_quality_inspections:view` (WS-080) / `wh_supplier_returns:view` (WS-084) | *completed* with rejected quantity / a QC-raised return | FR-717 · reprint marked duplicate |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Once? |
|---|---|---|---|---|---|---|
| IIS-T3-01 | QC-held ageing | stock in `QC_HOLD` from a source with no inspection started > `warehouse.quality.inspection_due_hours` (default 24) | nothing — tile *Awaiting inspection > SLA* | QA in-charge | daily alert job (`p2-23` family) | once per source |
| IIS-T3-02 | Rejected stock not returned | rejected qty with no supplier return after `warehouse.quality.reject_return_alert_days` (default 7) | nothing | inspector, buyer | same | once per inspection |
| IIS-T3-03 | Periodic re-test due | an `AVAILABLE` lot of an item with a current `PERIODIC`-stage assignment whose last accepted inspection (or receipt) is older than the plan's `retest_interval_days` | opens `IIS-T1-15` for the unreserved quantity (skipped, re-evaluated next day, when none) | QA in-charge | daily per site | FR-707 · once per lot per due date |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in |
|---|---|---|---|
| IIS-T4-01 | GRN post with a resolved plan (not `NO_INSPECTION`) whose item requires QC | line received into `QC_HOLD` (today's `received_status_code` resolution, unchanged) | GRN post |
| IIS-T4-02 | disposition with `destructive_quantity > 0` | one `ISSUE` movement −destructive at the held location in `QC_HOLD`, +destructive at `VIRT-CONSUMED-<site>`, **`source_document_type = QCINSP`** — the registered QC document type every WS-080 posting already uses (`WhQualityInspectionRepository.java:36`; a `whb_document_types` FK, so no new row; R29 F11); the cost object is stored on the inspection line's `destructive_cost_object_*` columns = `DEPARTMENT` from `warehouse.quality.qc_department_id` (resolver-validated, `SIR` §1). The issue register and *consumption by department* (`SIR` §5.4) read **store-issue lines and these inspection lines** (`UNION ALL` on the cost object), so QC destruction is counted | inspection service → writer, same transaction as the disposition |
| IIS-T4-03 | `IIS-T1-10` | supplier return `DRAFT` with origin columns; supplier claim **not** created (a user may create `QUALITY_REJECT` from the return through `getPrefill` `:345`) | supplier-return service |
| IIS-T4-04 | completed `STORE_RETURN`-source inspection disposition release | the released quantity goes `AVAILABLE` with a putaway task (store returns never need an MRN) | disposition service |
| IIS-T4-05 | `PRODUCTION_RECEIPT` (stock-bearing) source | **core posts** the disposition's `STATUS_CHANGE` (and scrap / destructive movements) exactly as for any stock-bearing source; MFG's `onDisposition` is then called inside the same transaction and **only reacts** (updates its own order / rework records) — it never posts a movement for the disposition (R29 F25; `mfg-qc-rework.contract.md:77`). `IN_PROCESS` (non-stock-bearing) posts nothing (`IIS-GRD-07a`) and hands the outcome to `onDisposition` | inspection service; resolver bean |
| IIS-T4-06 | a `STORE_RETURN`-source inspection rejects a lot | `SupplierOriginTrace`: store-return line → issue line → lot → its first `RECEIPT` movement from a goods receipt → GRN line → MRN line → PO line, returned as candidates | FR-716 · trace service (read only) |
| IIS-T4-07 | a line rejection with a supplier origin is dispositioned (single candidate, or the candidate picked at disposition — `IIS-GRD-16`) | outbox `supplier_line_rejection.recorded` (supplier, item, lot, quantity, origin GRN / MRN / PO line, defect) in the disposition transaction; the NCR carries responsibility `SUPPLIER` | FR-716 · inspection service |

## 5. T5 — Screen contract

### 5.1 WS-264 Sampling Schemes (reference: **Department**)

| | |
|---|---|
| **Grid** | `wh_sampling_schemes` · scope `WAREHOUSE_SAMPLING_SCHEME` · sort `e.code ASC` |
| **Columns** | `code`, `name`, `standardReference` (free text: *IS 2500-1*, *client*), `versionNo`, `bandCount`, `planCount`, `isSystem`, `isActive`, audit |
| **Filters** | `search` (code/name), `isActive` |
| **Modal** | header + editable band grid (`lotFrom`, `lotTo` (blank = and above), `sampleSize` **or** `samplePercent`, `acceptNumber`, `rejectNumber`); live *coverage check* message; in-modal refusal |
| **View** | `ViewModalBase` with *Bands* table and *Used by plans* |
| **Export** | one sheet: the header columns + audit (P8-05 S1 `G8`; bands are in View) |
| **Row actions** *(R30 `CP-SC-006`)* | View (gray) · Edit (primary, `IIS-T1-02`/`-03`; only when `canEdit && isActive`) · Deactivate (warning, `IIS-T1-03a`) / Activate (success). `default_columns` = the columns above less audit; `default_filters` = `search`, `isActive` (`STO-D22`) |

### 5.2 WS-265 Inspection Plan Assignments (reference: **Customer** — cascading filters)

| | |
|---|---|
| **Grid** | `wh_inspection_plan_assignments` · scope `WAREHOUSE_PLAN_ASSIGNMENT` · sort `e.scope_rank ASC, e.effective_from DESC` |
| **Columns** | `scopeType`, `itemCode`, `itemName`, `categoryName`, `supplierName`, `planCode` (or *No inspection*), `effectiveFrom`, `effectiveTo` (date-only, `formatDateSync`), `isCurrent`, audit |
| **Filters** | `scopeType`; `categoryId` → `itemId` (cascade); `supplierCounterpartyId`; `planId`; `currentOnly` |
| **Toolbar** | Add · **Test resolution** (item + supplier + date → winning assignment, writes nothing) · Export |

### 5.3 WS-079 / WS-080 changes

- WS-079 plan modal: formula select drives required fields (`fixedSampleQuantity`, `samplePercent` + `minSampleQuantity`, `samplingSchemeId`); `aql` and `inspectionLevel` shown for `AQL_TABLE`.
- WS-080 grid gains `sourceType`, `inspectionStage`, `sourceDocumentRef`, `sampleSizeProposed`, `defectiveCount`, `lotVerdict`; filters `sourceType`, `inspectionStage`; row action **Raise supplier return** (visible per `IIS-T2-06`); complete modal shows proposed verdict with confirm/override.

## 6. Out of scope

Switching rules, skip-lot dynamics, variables sampling, SPC (FRD §12 row 4); auto supplier return; mobile.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-22 | v0 derived. Settles `RQP-T1-16`'s open note *"FIXED_QUANTITY / PERCENTAGE propose the whole lot until `wh_inspection_plans` gains a parameter column"* |
| 2026-10-22 | R29 dispositions: scope pair; `Re = Ac + 1`; one `sampling_scheme_id` column name, plans re-pointed on copy-on-write, scheme deactivation; destructive issue under `QCINSP` with its cost object on the inspection line; core posts `PRODUCTION_RECEIPT` dispositions |
| 2026-10-23 | `IIS-OPEN-01`/`-02` resolved, defaults stand (`R31-decisions`) |
| 2026-10-24 | P8 decision record (DECISIONS `D-19`): per-line plan, assignment and scheme columns, header only when all lines agree (`G5`, §0, `IIS-T1-05`); `NO_INSPECTION` status order and audit (`G6b`, `IIS-T1-05`). P8-05 S1 `G11`: sampling columns owned by `V511314` (`P8-05`), not `V511315`; Activate row `IIS-T1-03b`; unit of *L* = receipt line unit (`IIS-T1-06`); disposition against the verdict allowed, `MRN_PENDING` branch is `P8-08`'s (`IIS-T1-09`); inactive plans skipped; `IIS-OPEN-03` (T3 owner) |
| 2026-10-24 | P8-05 S3 functional review: `IIS-OPEN-01` re-opened (Z1.4 family not seeded; follow-up task; "refuse unseeded AQL" deferred) — `G10`; §1.1 assignment row `[!]` UTC display day vs site-local End default — `F4`/`R5`; `IIS-T1-04`/`-05` the `NO_INSPECTION` decision recorded on the GRN line, audit after commit, only when not QC-held — `F3`/`R4`; `IIS-T1-09` server-suggested disposition — `F5`; `IIS-GRD-03` percentage-band rule at Start with a shown no-verdict reason — `F6`; contract quality: §5.1 export is one sheet, `isSystem` column listed, `IIS-T1-02`/`-03` read "any inspection" |
| 2026-10-25 | **R32-fix** (`R32-functional-review-core-quality.md`). Releasing a `REJECT_LOT` lot only as `ACCEPT_UNDER_DEVIATION` (`IIS-T1-09`; F-R32CQ-002); non-stock outcome held until result approval (`IIS-GRD-07a`; F-010); auto IQC on every QC-held status (`IIS-T1-11`; F-025); per-serial targets per disposition (`IIS-T1-12`; F-037); periodic re-test always holds, unreserved quantity only, `retest_holds_stock` withdrawn (`IIS-T1-15`, `IIS-T3-03`; F-013, F-024); unapproved-supplier sample → first article (`IIS-T1-14`; F-023); supplier origin picked at disposition (`IIS-GRD-16`, `IIS-T4-07`; F-019) |
| 2026-10-25 | **R32 (PRD 2026-10-24, `D-20`).** `P8-06` reopened: auto-created inspection worklist `IIS-T1-11`/`-GRD-11`, evidence and COA `IIS-T1-13`/`-GRD-12`/`-15`, per-serial results `IIS-T1-12`/`-GRD-13`, first article and periodic re-test `IIS-T1-14`/`-15`/`-GRD-14`/`-T3-03`. `P8-07` R32: line-rejection supplier return from a store-return inspection `IIS-T1-16`/`-GRD-16`/`-T4-06`/`-07` (supersedes the "GOODS_RECEIPT only" limit of `IIS-T1-10` for that case). `P8-17`: NCR on reject `IIS-T1-17`/`-GRD-17`. `P8-18`: `ACCEPT_UNDER_DEVIATION` `IIS-T1-18` (the reason-only "MRB use-as-is" release of `IIS-T1-09` is withdrawn by the R32-fix row above). `P8-12`: rejection note `IIS-T2-07`. Contract stays v0 |

## 8. Invariants and scenarios

`L-1` (destructive qty posts); `FR-041`; `FR-139` amended; scenarios `WH-SC-442`…`-453`, `-469`, `-475`.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| IIS-OPEN-01 | For `AQL_TABLE` with an `aql` value, seed the full Z1.4/IS 2500 single-sampling master table (Ac/Re by code letter × AQL) as data? | **OPEN (re-opened 2026-10-24, P8-05 S3 `G10`).** The answer stands — a seeded `is_system` scheme family `Z14-GII-AQL-<aql>` for the eleven common AQLs (0.065…6.5) — but it is **not seeded in `V511314`**: the cells immediately above each Ac 1 / Re 2 plan could not be verified against the standard. **Follow-up task** (own migration, own number): seed the family cell by cell from ANSI/ASQ Z1.4-2003 (R2018) Table II-A, verified against the standard. **[!] Interim v1:** `AQL_TABLE` sizes from the unchanged code-letter constants and proposes no verdict (acceptance `A3` met). **Deferred:** refusing an `AQL_TABLE` plan whose `aql` has no seeded family — until the family is seeded it would refuse every AQL plan with an `aql` value. |
| IIS-OPEN-02 | OD-25 band reading | contiguous **RESOLVED (DEFAULT), 2026-10-23** (`R31-decisions`). Contiguous bands with an open top band (`OD-25`). |
| IIS-OPEN-03 | Who owns `IIS-T3-01` (QC-held ageing) and `IIS-T3-02` (rejected not returned)? | **Not `P8-05`** — they are outside its row list (`p8-05.md` cites `IIS-T1-01`…`-09`, `IIS-GRD-01`…`-06`, `-10`). An owner task is to be named by the P8 driver before either alert is built (P8-05 S1 `G11`, 2026-10-24) |
