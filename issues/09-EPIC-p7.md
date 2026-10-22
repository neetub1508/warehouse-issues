TITLE: [Warehouse] EPIC: P7 — Remove dealer and retail code, rename the dual-use items, rebuild on a clean migration set
LABELS: epic,warehouse,phase-p7
issue: TBD
---
Part of __MASTER__ · Modules `warehouse-base`, `warehouse`, `warehouse-3pl`, `warehouse-india` (+ three platform registration files) · Migrations — **20 deleted, 34 rewritten, 4 client seeds edited** (FRD-REM Appendix B) · Ships **before** `P8`, `P9` and `P10` · Requirements [`FRD-REM`](../docs/frd/FRD-REM.md) `FR-480`…`FR-499` · Scenarios `WH-SC-660`…`WH-SC-679` · Decision `D-16` (`RN-050`…`RN-054`)

## Overview

**The warehouse becomes a manufacturing-and-storage product** (`D-16`). This phase takes out everything built for retail/e-commerce and for the dealer:
- AWB pools, NDR, COD, channel accounts/imports/publish rules, customer tracking links and the public tracking page
- marketplace claims, RTO, serviceability and rate quotes, and the Channels menu
- OEM obsolescence returns and the trade portal
- accessories coexistence, including consolidated valuation and `is_dual_eligible`
- the dead adapter switches, and the seeded dealer/retail vocabulary

It renames the dual-use codes (`LINE_STOP`, `PRODUCTION_STORE`, `MANUFACTURER_PART_NUMBER`, Stock KPIs), in storage as well as on screen.

**Size, measured:** 338 Java files and 140 frontend files deleted; 1,757 i18n keys × 3 languages; 103 permissions, 17 menu leaves + 5 containers, 18 grids, 24 tables.
Generic shipping **stays**: carriers, services, accounts with scopes, labels, manifests, handovers, pickups, consignments, status mappings, tracking events, shipments, RMAs, return receipts and gradings.

**How (`RN-052`):** a clean rewrite. Delete the removed features' migrations, rewrite the mixed ones, rebuild the DB once. **No drop migrations and no shims.**
Every later phase builds on the cleaned schema, so **`P7` runs first**.

## Exit criterion

`P7-13` completes on the rebuilt dev DB and on three disposable fresh installs (all modules; 3PL and India off; logix):
1. **`WH-SC-660`, `WH-SC-677`, `WH-SC-678`:** fresh installs boot with no Flyway failure and no repair.
2. **`WH-SC-661`…`WH-SC-665`:** no retail or dealer table, column, permission, role, menu, grid, filter or catalogue row exists. `CHANNEL_KIND` = `{B2B}`. The renamed codes are present.
3. **`WH-SC-666`…`WH-SC-674`:** generic shipping, returns, supplier claims, Stock KPIs, the line-stop order source and the category picker behave as specified. Warehouse has no unauthenticated endpoint.
4. **`WH-SC-675`, `WH-SC-679`:** every grep gate is clean. Flyway history has no deleted version.
5. **`WH-SC-676`:** `ci-gate.sh ratchets warehouse`, `integration warehouse` and `frontend` are green.

## The properties this phase establishes

| Property | Proof |
|---|---|
| **Absence is total.** A removed feature leaves no table, column, Java class, endpoint, page, menu, permission, role, grid, filter, setting, job, series, catalogue row, i18n key, constant, help entry or filter scope | FRD §4 "absent" definition; gates G-1…G-8 |
| **Kept behaviour is unchanged except where listed.** Each behaviour change is named in the task that makes it, and tested | `FR-489`; the "Rules" section of `P7-02`, `P7-03`, `P7-04`, `P7-05` |
| **Every task is a pure delete or a pure rename.** The one exception, `P7-01`, is a pure move | `P7-01` runs first |
| **Every intermediate tree installs fresh.** Each task edits the count assertions its own deletions break | FRD Appendix B "fresh-install hazards" |
| **The ledger is untouched.** `whb_stock_movements` and its `channel_id` FK stay. No posted-movement shape changes | `FR-495`; `WH-SC-666`, `WH-SC-668` |

## Migration blocks

| Block | Files | Task |
|---|---|---|
| Delete | `V510205`, `V511277` | `P7-02` |
| Delete | `V510206`, `V510207`, `V510209`, `V511274`, `V511276` | `P7-03` |
| Delete | `V510208`, `V510225`, `V510226`, `V511304` | `P7-04` |
| Delete | `V510215` | `P7-05` |
| Delete | `V511270` | `P7-07` |
| Delete | `V510221`, `V511209`, `V511239` | `P7-08` |
| Delete | `WB/V500053`, `V511249`, `V511262` | `P7-09` |
| Delete | `WB/V501117` | `P7-10` |
| Rewrite | 34 mixed files + 4 logix seeds | per FRD Appendix B.2, owner task per row |

No version number is reused or renumbered. Deleted versions leave gaps.

## Tasks

__TASKS__

**Order:** `P7-01 → P7-02 → P7-03 → {P7-04, P7-05} → P7-06 → P7-07 → {P7-08, P7-09} → P7-10 → P7-11 → P7-12 → P7-13`.

- **`P7-01` first:** it relocates the four generic helpers (category picker, `WhClaimTransitionData`, claim `lineValue`, fingerprint hash), so every later task only deletes.
- **`P7-02 → P7-03`:** `P7-02` deletes `V511277`, which UPDATEs `wh_awb_numbers`, and the rate-quote half of the carrier guard. `P7-03` deletes the rest of the carrier-integration jobs file.
- **`P7-04` after `P7-02`:** the last `paymentMode` consumers (AWB claim, rate shop) must already be gone.
- **`P7-05` before `P7-07`:** both edit `V511268`'s Returns count, from 8 to 6 and then from 6 to 5.
- **`P7-06` after `P7-02`…`P7-04`:** the Channels L1 can be replaced only once its retail leaves are gone.
- **`P7-10` after `P7-02`…`P7-09`:** a vocabulary row can be deleted only when no kept reader remains.
- **`P7-11` after `P7-10`:** both edit `WB/V500010`.
- **`P7-13` last:** it needs the user's go before any volume is dropped.

Each task is one PR and reviewable alone. Each leaves a tree that installs fresh and passes `ci-gate.sh ratchets warehouse`.

## Traps this phase must not walk into

- **An allowlisted grep gate is a shim.** A hit means the owning task is unfinished (FRD §6).
- **Count assertions in seed migrations** (`V511248:298`, `V511268:304,371`, `V500010:811`, `V510050:945`, `V500002:468-470`) fail a fresh install silently if the deleting task does not edit them.
- **`warehouse_channels` is two different menu rows**: the removed L1 and the kept L3 Channels master. Always filter on `menu_level`.
- **`OBSOLESCENCE` is two different things**: the removed supplier-claim type, and the kept stock KPI.
- **`payment_mode` is two different columns**: the demand-order one is dropped. The carrier-account one (`CREDIT`/`PREPAID`/`TO_PAY`) is kept.
- **Platform files:** `filterUtils.ts`, `CacheConfiguration.java` and the logix seed are the only platform edits. Anything beyond them breaches `RN-054`.
- **Flyway repair is not a rebuild.** It leaves removed DDL in the database (`P7-13`).

## Open decisions

`OD-22` (`supports_cod`, default drop), `OD-23` (return types, default keep 3 and drop 2) and `OD-24` (3PL freight metering source, no behaviour change). See FRD-REM §3.

## Definition of done
Per __MASTER__, plus the exit criterion above.
