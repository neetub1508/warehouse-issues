# Functional Contract — Kits and the VAS / light-manufacturing work order

> **What this is.** The functional truth for kit definitions (stocked and phantom), the work order that is
> both the value-added-service record and the light-manufacturing record (assembly, disassembly, repack,
> VAS), the **one balanced movement** its completion posts, the genealogy it records, and the labour minute a
> 3PL prices it by. Production orders are **not** this document: `warehouse-manufacturing` owns them and
> cites this posting shape (`WhWorkOrderPostingService`); the work order is not widened (`D-16` item 5,
> `RN-033`).
>
> **Status.** Derived 2026-10-23 (v0) from `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.15 (`FR-261`…`FR-267`)
> and verified against the built code in `classic`. Not ratified. Written for R30 `CP-FR-007` row 14 /
> `D-17` item 1.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Kit definition (WS-035, versioned) → work order `DRAFT` → Release → Issue components (records what left the shelf; posts nothing) → **Complete** (one movement, genealogy, variance) · Cancel before completion. Labour is timed on WS-146 and priced by the 3PL module |
| **Module** | `warehouse-base` (`whb_kit_definitions`, `whb_kit_components`, `whb_transformations` + `_inputs` / `_outputs`; `WhbKitDefinitionService`, `WhbTransformationRecorder`, `WhbGenealogyQueryService`) + `warehouse` (`WhWorkOrderService`, `WhWorkOrderPostingService`, `WhWorkOrderValidationService`, `WhLabourTaskService`) + `warehouse-3pl` (`Wh3plVasLabourPricingService`) |
| **Domain baseline** | `FR-436` (single writer), `L-1`, `L-2`, `L-4` · [`movement-post-reverse`](movement-post-reverse.contract.md) · [`costing-valuation`](costing-valuation.contract.md) `CVL-T4-02` (relief values) |
| **Owning tasks** | `issues/p3-11.md` (work orders, kits, assembly by value, repack, packaging) · `issues/p5-19.md` (genealogy through assembly, labour-minute pricing) · `issues/p5-14.md` (a recall walking kit lots) |
| **Primary tables** | `whb_kit_definitions`, `whb_kit_components`, `whb_transformations`, `whb_transformation_inputs`, `whb_transformation_outputs`, `wh_work_orders`, `wh_work_order_lines`, `wh_vas_service_types`, `wh_labour_tasks`; movement types `ASSEMBLY`, `DISASSEMBLY`, `REPACK`, `VAS` and their `*_REVERSAL` twins (`V510102`) |
| **Status columns** | `wh_work_orders.status` `DRAFT`/`RELEASED`/`IN_PROGRESS`/`COMPLETED`/`CANCELLED` (service-owned ladder) |
| **Permission resources** | `whb_kit_definitions:{view,create,edit,delete,export}` · `wh_work_orders:{view,create,edit,release,issue_components,complete,cancel,export}` · `wh_labour_tasks:{view,record,export}` · `whb_transformations:{view,export}` |
| **Routes** | WS-035 `/warehouse/masters/kits` · WS-144 `/warehouse/vas/work-orders` · WS-145 `/warehouse/vas/service-types` · WS-146 `/warehouse/execution/labour-tasks` · WS-039 `/warehouse/ledger/genealogy` · mobile: none (`D-16` item 7) |
| **Contract version** | `v0 — 2026-10-23` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Assembly and disassembly are balanced ledger transactions; a phantom kit never has stock (`WH-SC-287`) | `VWO-T4-01`, `VWO-UNR-01`, `-02` |
| A2 | The work order carries type, kit, output, planned / produced / scrapped, scrap reason, windows, assignee, instruction document version, charge code (`WH-SC-288`) | `VWO-T1-01`, `VWO-T5-02` |
| A3 | Completion balances by value with a variance reason (`WH-SC-288`) | `VWO-T4-02`, `VWO-GRD-06` |
| A4 | Repack / break-case is two-sided; packaging is ordinary stock (`WH-SC-289`) | `VWO-GRD-07`, `VWO-T4-03` |
| A5 | Genealogy survives assembly (`WH-SC-135`) | `VWO-T4-04` |
| A6 | VAS priced by the labour minute (`WH-SC-358`) | `VWO-T4-05` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Reachable via | Exits via | Kind |
|---|---|---|---|---|
| Work order | `DRAFT` | `VWO-T1-01` | `-02`, `-05` | initial |
| Work order | `RELEASED` | `VWO-T1-02` | `-03`, `-05` | active |
| Work order | `IN_PROGRESS` | `VWO-T1-03` | `-04`, `-05` | active |
| Work order | `COMPLETED` | `VWO-T1-04` | none (undo = ledger reversal of the movement) | **terminal** |
| Work order | `CANCELLED` | `VWO-T1-05` | none | **terminal** |
| Kit definition version | effective range | `VWO-T1-06` | end-dated | master |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | Reason? | Source |
|---|---|---|---|---|---|---|---|---|
| VWO-T1-01 | — | Create: site, owner, type (`ASSEMBLY`/`DISASSEMBLY`/`REPACK`/`VAS`), VAS service type, kit (version), output item / location / UoM, planned quantity, planned start / end, assignee, client instruction document **and its version**, billing charge code, lines (role `INPUT` / `OUTPUT` / `PACKAGING`) | `DRAFT` | `VWO-GRD-01`…`-04` | `wh_work_orders:create` / `:edit` | number `WO…`; Explode copies one kit version's BOM into the lines | no | FR-262 |
| VWO-T1-02 | `DRAFT` | Release | `RELEASED` | `DRAFT` only, else `409 WORK_ORDER_NOT_DRAFT` | `:release` | `release_note` | no | FR-262 |
| VWO-T1-03 | `RELEASED` | Issue components (actual quantities taken from the shelf) | `IN_PROGRESS` | `RELEASED` only, else `409 WORK_ORDER_NOT_RELEASED`; no consumption lot under recall (`VWO-GRD-14`) | `:issue_components` | **posts nothing**; under `warehouse.work_orders.issue_reservation` = `HARD` (default) one HARD hold per issued `INPUT`/`PACKAGING` line at the line's own grain, holder (`WAREHOUSE`, `WORK_ORDER`, wo id, `line_no`), all or none (`VWO-GRD-11`, `VWO-T4-07`); `NONE` holds nothing (the behaviour before V511430); the mode is stamped on `issue_reservation_mode`; `actual_start_at` | no | FR-261, `VWO-OPEN-01` |
| VWO-T1-04 | `IN_PROGRESS` | **Complete**: produced, scrapped (+ reason), output serials, variance reason | `COMPLETED` | `VWO-GRD-05`…`-08`; `IN_PROGRESS` only, else `409 WORK_ORDER_NOT_IN_PROGRESS`; no consumption lot under recall (`VWO-GRD-14`); at least one `INPUT` line issued, else `422 WORK_ORDER_NO_INPUT_ISSUED` · `lines` (`WhWorkOrderValidationService.java:547`) | `:complete` | `VWO-T4-01`…`-04` in one transaction; the movement names the order's open holds as consumed and each closes `CONSUMED` (`WORK_ORDER_CONSUMED`) against its line's movement line (`VWO-T4-07`); a refused Complete keeps them; `posted_movement_id`, `transformation_id`, `actual_end_at` | no | FR-261, FR-263 |
| VWO-T1-05 | `DRAFT` · `RELEASED` · `IN_PROGRESS` | Cancel (from `IN_PROGRESS` after a `HARD` Issue: with every issued line's return) | `CANCELLED` | not terminal, else `409 WORK_ORDER_NOT_CANCELLABLE`; `VWO-GRD-12` | `:cancel` | nothing posted; after a `HARD` Issue each issued line records `returned_quantity` (= `actual_quantity`), `returned_by`, `returned_at` and the order's holds are released `HOLDER_CANCELLED` (`VWO-T4-07`); `RELEASED` → Cancel has nothing to release | optional (`cancel_reason_code_id`; validated when given — `WO-GRD-08`, #530 F3, #57 S4 F5 decision) | FR-262, `VWO-OPEN-01` |
| VWO-T1-06 | — | Add a kit definition version: kit item, kit type (`KIT_TYPE` code list: stocked or `PHANTOM`), components with UoM, effective range | version | `VWO-GRD-09` | `whb_kit_definitions:create` / `:edit` | — | no | FR-261 |

### 1.3 Guards

| ID | Predicate | Refusal | Backstop | Source |
|---|---|---|---|---|
| VWO-GRD-01 | Type valid; a kit is required for `ASSEMBLY`/`DISASSEMBLY` and refused where the type takes none; the output item is the kit's item | `422 WORK_ORDER_TYPE_INVALID` / `WORK_ORDER_KIT_REQUIRED` / `WORK_ORDER_KIT_NOT_ALLOWED` / `WORK_ORDER_KIT_ITEM_MISMATCH` | — | FR-262 |
| VWO-GRD-02 | Lines: at least one; an output and an input where the type needs them; each line resolves at the order's site, at a physical (non-virtual) location, at its item's grain (lot / serial mode); line role valid; a kit component is on the kit | `422 WORK_ORDER_NO_LINES` / `_NO_OUTPUT` / `_NO_INPUT` / `_LINE_UNRESOLVED` / `_LINE_SITE_MISMATCH` / `_LINE_VIRTUAL_LOCATION` / `_LINE_GRAIN_INVALID` / `_LINE_ROLE_INVALID` / `_KIT_COMPONENT_UNKNOWN` · `lines[i]` | — | FR-262 |
| VWO-GRD-03 | The planned window is ordered; the site is immutable after create | `422 WORK_ORDER_PLANNED_WINDOW_INVALID` / `WORK_ORDER_SITE_IMMUTABLE` | — | FR-262 |
| VWO-GRD-04 | A phantom kit is never the output of a work order | `422 WORK_ORDER_PHANTOM_KIT_OUTPUT` | — | FR-261 |
| VWO-GRD-05 | Quantities positive; scrapped ≤ actual; a scrap carries a valid reason (note when required); serialised output has its serials captured | `422 WORK_ORDER_QUANTITY_INVALID` / `_SCRAP_EXCEEDS_ACTUAL` / `_REASON_INVALID` / `_REASON_NOTE_REQUIRED` / `_OUTPUT_SERIAL_NOT_CAPTURED` | — | FR-262 |
| VWO-GRD-06 | Value balance: Σ input value relieved = Σ output value; where they differ the completion carries a variance reason (context `WORK_ORDER_VARIANCE`) and `variance_value` | `422` field-named on the reason | `total_input_value`, `total_output_value`, `variance_value` | FR-263 |
| VWO-GRD-07 | A `REPACK` / break-case is the same item, and its two sides agree in base units | `422 WORK_ORDER_REPACK_UNBALANCED` | ledger `MUST_BALANCE_PER_OWNER_ITEM` | FR-264 |
| VWO-GRD-08 | Every input was costed by the engine under the valuation lock | `WORK_ORDER_INPUT_NOT_COSTED` | — | FR-263 |
| VWO-GRD-09 | Kit version: items known and active, kit item immutable, type does not change across versions and matches the item type, no overlapping or retroactive range, components known / active / not a kit / not phantom / not repeated, UoM convertible, at least one mandatory component; a phantom kit item holds no stock, has no ledger history and is never a component | `422 KIT_*` (e.g. `KIT_VERSION_OVERLAP`, `KIT_COMPONENT_IS_PHANTOM`, `PHANTOM_KIT_HOLDS_STOCK`, `PHANTOM_KIT_HAS_LEDGER_HISTORY`) | — | FR-261 |
| VWO-GRD-10 | Packaging consumed on a work order is an ordinary stock item; a client-supplied line must be a `PACKAGING` line, owned by the client, else the house owner | `422` field-named | `chk_wh_work_order_lines_client_supplied_is_packaging` | FR-265 |
| VWO-GRD-11 | Issue under `HARD`: every issued `INPUT`/`PACKAGING` line fits the free stock at its own grain, the hold sized in base units by the ledger writer's own rule (the resolver's factor, scale 4 away from zero, MPR-GRD-26) so it equals what Complete's relief takes off the grain (#57 S3 F1); the factor and that base quantity are stored on the line (`issued_conversion_factor`, `issued_base_quantity`, V511433) and Complete converts the line at them - lock, dry relief, post (the ledger writer's forward conversion, `MPR-GRD-26`; not a reversal, so `MPR-GRD-11`'s reversal reason is not asked) and genealogy - so a conversion changed between Issue and Complete never relieves more than the hold took (#57 G2 item 6); a line issued under `NONE` or before V511433 converts at the factor in force; a shortfall on any line refuses the whole Issue and rolls back every hold and the status change | `409 INSUFFICIENT_STOCK` · `lines[i].actualQuantity` | the ledger writer's `admitReservation` under the grain lock | `VWO-OPEN-01` (#57 G1) |
| VWO-GRD-12 | Cancel from `IN_PROGRESS` of an order issued under `HARD`: every issued consumption line records its return in full (`returnedQuantity` = issued `actualQuantity`); no partial return | `422 WORK_ORDER_RETURN_INCOMPLETE` · `lines[i].returnedQuantity` / `lines` | `chk_wh_work_order_lines_returned_quantity`, `_returned_together` | `VWO-OPEN-01` (#57 D2) |
| VWO-GRD-13 | A work order's hold is never released by hand (WS-047), by a holder release, by a status change with release intent (QI disposition, lot expiry) or by a master merge. **A recall Initiate on a lot a HARD work-order hold covers is refused like a staged pick** (`WhRecallService.initiate`, the whole Initiate rolls back; checked before any recall row or quarantine over EVERY lot of the recalled set, whatever the held stock's status — quarantine meets allocatable stock only, #57 S4 round b): `409 RECALL_WORK_ORDER_HOLDS` on `lotId`, naming the work orders, telling the user to cancel them with the return recorded and initiate again, never to complete them; a recall never overrides the hold (#57 S3 F3, R33 decision) | `409 RESERVATION_HELD_BY_WORK_ORDER` (recall: `409 RECALL_WORK_ORDER_HOLDS` · `lotId`) | `WhWorkOrderHoldReleaseGuard` (`WhbReservationReleaseGuard`) | `VWO-OPEN-01` (#57 G1) |
| VWO-GRD-14 | **A recalled lot is blocked for all use.** Issue and Complete refuse a consumption line whose lot is under ANY recall — the recall gate's own lookup (`WhRecallRepositoryCustom.findRecallNumbersByLot`: the recalled lot, its persisted lot set, its affected lines, the lots its quarantine moved), every site, **whatever the stock status** (quarantine moves allocatable stock only, so a RETURNED unit of the lot is still on the shelf); Complete judges it under the positions' lock, so a recall that committed after Issue still blocks it. Nothing is held, posted or stamped (#57 S3 F1 on 660d5bb597, R33 decision (a)) | `409 WORK_ORDER_LOT_UNDER_RECALL` · `lines[i].lotId` (Complete: `lines`) | `WhWorkOrderValidationService.requireNoLotUnderRecall` | FR-266, `VWO-GRD-13` |

### 1.4 Unreachable

| ID | Must never happen | Why it cannot | Source |
|---|---|---|---|
| VWO-UNR-01 | An `UPDATE` to a parent or kit quantity in place of a ledger transaction | completion goes through `WhbStockLedgerWriter` only; nothing in the work-order code writes `whb_stock_positions` | FR-261 |
| VWO-UNR-02 | A stock position for a phantom kit | a forward posting naming a phantom kit item is refused `UNKNOWN_ITEM` (`WhbMovementPostValidationService`), backed by `trg_whb_stock_positions_phantom_kit_holds_no_stock` (`V500089`) | FR-261 |
| VWO-UNR-03 | A separate issue movement and receipt movement for one completion | one movement of the work order's type, idempotency key `<MOVEMENT_TYPE>:<work order id>` | FR-263 |
| VWO-UNR-04 | A repack or UoM conversion written as an `UPDATE` to a quantity in another unit | `VWO-GRD-07`; two-sided lines | FR-264 |
| VWO-UNR-05 | A VAS output receipting stock that did not come into being | a VAS output's good quantity posts nothing (only its scrap posts) | FR-265 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| VWO-T2-01 | Create / edit | `wh_work_orders:create` / `:edit` | — / `DRAFT` | FR-262 |
| VWO-T2-02 | Release · Issue components · Complete · Cancel | `:release` · `:issue_components` · `:complete` · `:cancel` | `DRAFT` · `RELEASED` · `IN_PROGRESS` · non-terminal | FR-261, FR-262 |
| VWO-T2-03 | Kit definitions | `whb_kit_definitions:*` | — | FR-261 |
| VWO-T2-04 | Time labour (start / pause / resume / end) | `wh_labour_tasks:record` (own timer only, `LABOUR_TIMER_NOT_OWN`) | — | FR-267 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Source |
|---|---|---|---|---|
| VWO-T3-01 | A kit version is in force over its effective range; the order keeps the version it exploded, so a later BOM never re-explodes an earlier order | each create / explode | — | FR-261 |
| VWO-T3-02 | Labour minutes run between start and end, less paused time; one open timer per user and task | timer events | `wh_labour_tasks` | FR-267 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| VWO-T4-01 | Complete | **one** movement of type `ASSEMBLY`/`DISASSEMBLY`/`REPACK`/`VAS`: each consumption line (`INPUT`/`PACKAGING`) of actual *A*, scrap *S*: −*A* at its bin, +(*A*−*S*) at `VIRT-PRODUCTION-<site>`, +*S* at `VIRT-SCRAP-<site>`; each `OUTPUT` line: +(*A*−*S*) at its bin, −(*A*−*S*) at `VIRT-PRODUCTION`, scrap to `VIRT-SCRAP` — **except a `VAS` order, whose `OUTPUT` lines receipt nothing** (goods serviced in place; only their scrap posts, `VWO-UNR-05`, `WhWorkOrderPostingService.java:411-412`); every grain nets to zero | `WhWorkOrderPostingService` → `WhbStockLedgerWriter` | FR-261 |
| VWO-T4-02 | Complete | consumption lines carry the engine's relief unit cost; output lines carry the extended cost of what went in; the difference is `variance_value` with its reason; non-own stock is `ZERO_BAILMENT` | same | FR-263 |
| VWO-T4-03 | Complete with packaging lines | the packaging is relieved on the same movement as the pack | same | FR-265 |
| VWO-T4-04 | Complete | a `whb_transformations` row with inputs (lots / serials consumed) and outputs (lots / serials produced); the genealogy explorer walks it forward and backward, and a recall reaches every kit lot built from a recalled lot | `WhbTransformationRecorder`, `WhbGenealogyQueryService` | FR-266 |
| VWO-T4-05 | A 3PL billing run prices a completed, billable VAS work order | the charge reads the timed labour minutes of the work order's labour tasks, at the client's rate for the charge code; refused when not completed, not timed, a timer is open, no charge code, or the owner is not a client (`WH3_VAS_*`) | `Wh3plVasLabourPricingService` | FR-267 |
| VWO-T4-06 | A phantom kit line is allocated on a demand order | the kit is exploded into its MANDATORY components BEFORE sizing and the lock plan, as the version in force on the site's day (`WhbPhantomExplosionService`; `P10-03` contributes the BOM provider); each component is reserved under the line's holder quad, all or none, every reservation stamped with the kit, the line, the provider, definition, version and quantity per (`whb_reservations.explosion_*`, V501243 — never `requested_item_id`); the line's allocated, picked and shipped quantities are WHOLE kits, FLOOR(MIN over components of held ÷ quantity per); the stamp — not a fresh explosion — is re-used by the Release check, pick, despatch (which relieves every staged component), task and line short pick, amend top-up and line-cancel re-size, so a later version never re-explodes the line (VWO-T3-01); a hold on the phantom item blocks its line; the kit itself is never stock (`UNKNOWN_ITEM`, `VWO-UNR-02` kept); `warehouse.allocation.phantom_kit_explosion` = `EXPLODE` (default) / `OFF` (the line asks for the phantom item, the behaviour before #57) | allocation, release, pick, despatch | FR-261 — **built 2026-10-26 (#57 G2, S1 D3 / D4):** `WhPhantomKitLines`, `WhDemandOrderService`, `WhPickTaskWriter`, `WhDespatchService`, `WhbAllocationService` (duplicate guard per component), `WhbPickReservationService.reattach` (stamp carried to staging) |
| VWO-T4-07 | Issue (`HARD`) · Complete · Cancel after Issue | Issue admits one HARD, status-named hold per issued consumption line in `whb_reservations` through the ledger writer; Complete's movement names them in `consumedReservationIds` (they are not counted against its relief) and closes each `CONSUMED` with its movement line and reason `WORK_ORDER_CONSUMED`; a Cancel that recorded the return closes them `HOLDER_CANCELLED`. The line's open hold is shown on the view (`heldQuantity`, base units). Complete relieves each consumption line at the factor and base quantity its Issue stored (`VWO-GRD-11`, #57 G2 item 6) | `WhWorkOrderReservationCoordinator` | `VWO-OPEN-01` (#57 G1) |

## 5. T5 — Screen contract

| ID | Screen · grid · scope | Contract | Source |
|---|---|---|---|
| VWO-T5-01 | WS-035 Kit Definitions · `whb_kit_definitions` · `WAREHOUSE_KIT_DEFINITION` | versions with effective range; kit type; components with UoM; availability (`WhbKitAvailabilityCalculator`) | FR-261 |
| VWO-T5-02 | WS-144 Work Orders · `wh_work_orders` · `WAREHOUSE_WORK_ORDER` | columns `workOrderNumber`, `workOrderType`, kit, output item, planned / produced / scrapped, status, assignee, planned / actual windows, variance; actions Release · Issue components · Complete · Cancel by state; detail shows the instruction document **version** priced, lines by role, and the posted movement | FR-262, FR-263 |
| VWO-T5-03 | WS-145 VAS Service Types · `wh_vas_service_types` · `WAREHOUSE_VAS_SERVICE_TYPE` | `code`, `name`, `serviceCategory`, `billingUnit`, `estimatedMinutesPerUnit`, `isActive` | FR-262, FR-267 |
| VWO-T5-04 | WS-146 Labour Tasks · `wh_labour_tasks` · `WAREHOUSE_LABOUR_TASK` | start / pause / resume / end against a work order or task; minutes per task | FR-267 |
| VWO-T5-05 | WS-039 Genealogy Explorer · `whb_transformations` | forward and backward walk by lot / serial | FR-266 |

## 6. Out of scope

Production orders, BOMs, backflush and WIP (`warehouse-manufacturing`); the 3PL billing run itself
(`warehouse-3pl`); mobile.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived (R30 `CP-FR-007` row 14) |
| 2026-10-23 | R31 `F-CB-023`: `WORK_ORDER_NO_INPUT_ISSUED` moved to its real transition (`VWO-T1-04`); VAS output exception in `VWO-T4-01`; `VWO-OPEN-01` decided, §10 row 3 |
| 2026-10-26 | R31 `P3-11` #57 S2 (S1 G1, D1, D2, D3): `VWO-T1-03`…`-05` amended (hold at Issue, consume at Complete, return on Cancel); `VWO-GRD-11`…`-13` and `VWO-T4-07` added; `VWO-OPEN-01` built; §10 row 3 closed; `VWO-T4-06` phantom-explosion seam built, its allocation wiring open (§10 row 1) |
| 2026-10-26 | R31 `P3-11` #57 S4 (S3 F1, F3): `VWO-GRD-11` hold sized by the writer's base rule; `VWO-GRD-13` recall refused naming the holding work orders (`RECALL_WORK_ORDER_HOLDS`), single answer, no setting |
| 2026-10-26 | R31 `P3-11` #57 S4 round b (S3 F3, F5): `VWO-GRD-13` checked before quarantine over every lot of the set whatever its stock status; `VWO-T1-05` cancel reason restated as optional, validated when given (`WO-GRD-08`, #530 F3 decision kept) |
| 2026-10-26 | R31 `P3-11` #57 S2b (G2 items 1–5, 7; S3 F1 on 660d5bb597): `VWO-T4-06` allocation wiring built (explode before sizing, component holds stamped once, whole-kit quantities through release / pick / despatch / short pick / amend / cancel), §10 row 1 closed; `VWO-GRD-14` added (Issue and Complete refuse a lot under recall, R33 decision (a)), `VWO-T1-03` / `-04` guards amended |
| 2026-10-26 | R31 `P3-11` #57 S2c (G2 item 6, S3 F1 residual): `VWO-GRD-11`, `VWO-T4-07` - Issue stores each consumption line's factor and base quantity (V511433); Complete's lock, dry relief, post and genealogy use them through the writer's new forward conversion (`movement-post-reverse` `MPR-GRD-26`); regression cases for a factor change between Issue and Complete and for scale-4-UP rounding |
| 2026-10-26 | R31 `P3-11` #57 S4e (scoped re-verify F1–F6, classic 0b21f1a642) — overlay, rows otherwise unchanged: **`VWO-T4-06`** a phantom line names WHOLE kits (`422 DO_PHANTOM_KIT_NOT_WHOLE` at save, amend, port amend, allocate; partial takes and whole-kit counts round DOWN to the kits the line unit names exactly), every kit pick trims each component to the line's kits (short pick: whole excess tasks withdrawn; excess staged holds released, left free at staging), despatch trims then refuses `409 DESPATCH_KIT_INCOMPLETE` when a component is staged beyond the picked kits — a broken kit never ships as loose components (F1, F2); **`VWO-T3-01`** the line unit's conversion is part of the stamp (`whb_reservations.explosion_kit_factor`, V501247; a pre-V501247 stamp resolves it as before) (F3); **`VWO-GRD-14`** Initiate and Complete are serialised by the recall gate — `pg_advisory_xact_lock` EXCLUSIVE in Initiate before its lot set, SHARED in Complete before its positions (F5); **`VWO-GRD-11` / `VWO-T4-07`** a frozen line's usage-variance leg is stated in the item's base unit, so a conversion retired after Issue does not refuse Complete (F6). Single answers, no setting. |
| 2026-10-26 | R31 `P3-11` #57 S4f (classic 980df07025) — overlay on **`VWO-T4-06`**: **trim-released stock is not moved by the system** — it stays on the staging location as free, unreserved stock (the release audit `WH_PICK_KIT_COMPONENT_TRIMMED` names it), visible to stock enquiry and replenishment, and is returned by the site's manual putaway/move; a later cancel de-stages only each pick's share of its staged hold's CURRENT quantity (a trimmed pick moves its share forward to its pick face by `DESTAGE`, never by reversing the whole `PICK`); a partial line cancel (person or port) leaving a part kit is `422 DO_PHANTOM_KIT_NOT_WHOLE`; a substitute's take/convert rounding (`conversionAllowance`) is not a broken kit. |

## 8. Invariants and scenarios

`L-1`, `L-2`, `L-4`, `FR-436`; `WH-SC-135`, `WH-SC-287`…`WH-SC-289`, `WH-SC-358`.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| VWO-OPEN-01 | Issue components takes no reservation (`WhWorkOrderService` issueComponents), so two orders can be issued against one on-hand and a cancel after issue leaves floor and ledger apart until an adjustment. Accept, or reserve at issue? | **DECIDED R31 (2026-10-23):** default replaced — hard-reserve at Issue components, consume at Complete, release on Cancel only with a recorded return. **Built 2026-10-26 (#57 S2):** `VWO-T1-03`…`-05`, `VWO-GRD-11`…`-13`, `VWO-T4-07`; setting `warehouse.work_orders.issue_reservation` `HARD` (default) / `NONE` (V511430) |

## 10. Code divergences

The FRD rule is kept; the code is what differs.

| # | File:line | FR | Difference |
|---|---|---|---|
| 1 | `warehouse-base/…/service/allocation/` (no phantom handling); `warehouse-base/…/service/ledger/writer/WhbMovementPostValidationService.java:896` | FR-261 | a phantom kit is refused as stock (`UNKNOWN_ITEM`), but no explosion of a phantom kit at allocation was found — **Triage 2026-10-23: FIX-CODE** — owner `P3-11` #57 (`FR-261`), reopened. reviewer-confirm settled by S1 D3 (one seam, owned by base). **2026-10-26 (#57 S2):** the seam is built (`VWO-T4-06`); the allocation wiring stays open **CLOSED 2026-10-26 (#57 G2):** the allocation wiring is built (`VWO-T4-06`), behind `warehouse.allocation.phantom_kit_explosion` (V501243) |
| 2 | `warehouse/…/entity/WhWorkOrder.java:109-118` | FR-262 | types are `ASSEMBLY`/`DISASSEMBLY`/`REPACK`/`VAS`; BUILD-SPEC WS-144 lists `ASSEMBLE`/`DISASSEMBLE`/`REPACK`/`DECANT`/`VAS` (no `DECANT` in code) — **Triage 2026-10-23: AMEND-SPEC** — rule: the work-order types are the four built codes `ASSEMBLY`, `DISASSEMBLY`, `REPACK`, `VAS` (`WhWorkOrder.java:109-118`); decanting is a `REPACK`. BUILD-SPEC WS-144 amended. reviewer-confirm |
| 3 | `warehouse/…/service/WhWorkOrderService.java:391` (`issueComponents`, no reservation) | FR-261 | **CLOSED 2026-10-26 (#57 S2):** Issue hard-reserves (setting `HARD` default), Complete consumes, Cancel after Issue releases only with the recorded return (`VWO-T4-07`). Was: decided `VWO-OPEN-01`: Issue components hard-reserves the issued quantities, Complete consumes them, Cancel releases only with a recorded return; built today with no reservation, so two orders can issue against one on-hand and a cancel after issue leaves floor and ledger apart (owner `p3-11`) — **Triage 2026-10-23: FIX-CODE** — owner `P3-11` #57, reopened |
