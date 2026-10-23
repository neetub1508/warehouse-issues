# Functional Contract — Bonded / MOOWR stock issued to production and sent for job work (`warehouse-india` + `warehouse-manufacturing`)

> **What this is.** The functional truth for moving stock of a **licensed duty status** (`BONDED`, `MOOWR`,
> `SEZ` — `whb_duty_statuses.requires_licence`) into manufacture and out to a job worker **under the bond
> rules**: which exits `WhinBondedVirtualExitPostGuard` accepts, the licence they need, the bond register row
> each one writes, the duty status of what the order produces, scrap and loss, job work under the bond
> officer's permission, and the MOOWR return and SEZ movement lines built from the register (`D-17` item 3,
> R30 `CP-GB-001`, `CP-GA-007`).
>
> **What this is not.** It does not restate the store issue / return (`store-issue-return`, `SIR-*`), staging
> and issue to an order (`mfg-material-staging-issue`, `MSI-*`), the receipt (`mfg-production-receipt`,
> `PRC-*`), subcontracting (`mfg-subcontracting`, `SUB-*`), ex-bond clearance and bonded losses (`p4-07`,
> `WhinBondedLossRecorder`) or the job-work challan (`p4-02`). **MFG writes no `whin_` table and imports no
> `ai.warehouseindia`** (FR-620); everything india-side runs on base's post hook and the core
> `JobWorkDispatchPort` (SEAM-M5).
>
> **Status.** Derived 2026-10-23 (v0), **not ratified**. No code exists. Statutory values **RE-VERIFY**. The
> enablement calls in GitHub reports 539 (is MOOWR process scrap a loss) and 543 (MOOWR job work) stay with
> the product owner; this contract builds the mechanism and the defaults below.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | bonded stock in store → store issue / staging + backflush to an order (`MANUFACTURE_ISSUE`) → outputs received in bond (`MANUFACTURE_OUTPUT`) → cleared ex-bond or exported (`p4-07`); or → subcontract dispatch (`JOB_WORK_OUT`) → receipt / recall (`JOB_WORK_RETURN`); scrap / write-off → bonded loss; month end → MOOWR return |
| **Module** | `warehouse-india` (registry, guard reading it, register, MOOWR return, SEZ lines, screens) · `warehouse-manufacturing` (order regime, output duty status, dispatch permission ref) |
| **Domain baseline** | FRD-MFG FR-670…FR-677, MD-42, MD-43, FR-620, FR-638, FR-659…FR-661, MD-13, MD-25, MD-28 · `DECISIONS.md` `D-17` item 3, `RL-001`, `D-8`, `L-1`, `L-11` · `p4-07` (licences, bonds, ex-bond clearance), `V541156` (`whin_bonded_losses`), `V540180` (compliance rules) · GitHub 539, 543 |
| **Owning task body** | `issues/p10-14.md`. Depends on `p10-06`, `p10-07`, `p10-10`, `p8-10`, `p8-11`, `p4-07` |
| **Primary tables** | `whin_bonded_exit_rules`, `whin_bonded_operation_lines` (`V540191`); `whin_moowr_returns`, `whin_moowr_return_lines`, `whin_sez_movements` (`V540192`); `whm_production_orders.bonded_duty_status`, `whm_subcontract_dispatches.bond_permission_ref` (`V560120`) |
| **Status columns** | `whin_bonded_operation_lines` has none (append-only; `open_quantity` on `JOB_WORK_OUT` derived on write); `whin_moowr_returns.status` (`DRAFT` / `FILED`, code list `WHIN_MOOWR_RETURN_STATUS`, no `CHECK`, `D-10`) |
| **Permission resources** | `whin_bonded_exit_rules:{view,edit}` · `whin_bonded_operation_lines:{view,export}` · `whin_moowr_returns:{view,generate,file,export}` · dispatch `whm_subcontract_dispatches:dispatch` (unchanged) |
| **Routes** | WS-338 `/warehouse/india/bonded-operations` · WS-339 `/warehouse/india/moowr-returns` · WS-185 *Bonded Licences* tab *Bond rules* · mobile: none |
| **Contract status / version** | `derived 2026-10-23 (v0), not ratified` · `v0 — 2026-10-23` |

### Acceptance checks

| # | The requester expects… | Delivered by |
|---|---|---|
| A1 | MOOWR stock issued to a production order posts and is registered (`WH-SC-680`) | `BND-GRD-01`, `BND-T4-01` |
| A2 | No active licence, or the bond rule switched off, refuses the exit (`WH-SC-681`) | `BND-GRD-02`, `-03` |
| A3 | Output of bonded inputs is received in bond; scrap is a bonded loss; one regime per order (`WH-SC-682`) | `BND-GRD-04`, `BND-T4-03`, `-04` |
| A4 | Bonded job work needs the bond officer's permission; return closes the register line; overdue raises a task (`WH-SC-683`…`-685`) | `BND-GRD-05`, `BND-T4-05`, `BND-T3-01` |
| A5 | The MOOWR return is built from the ledger and register and frozen when filed (`WH-SC-686`) | `BND-T1-01`…`-03`, `BND-T4-07` |
| A6 | Every other exit of bonded stock to a counterparty is still refused (`WH-SC-687`) | `BND-UNR-01` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind |
|---|---|---|---|---|---|
| Bond rule | active / inactive | `whin_bonded_exit_rules.is_active` | seed (`V540191`), `BND-T1-04` | `BND-T1-04` | — |
| Register line | written | a `whin_bonded_operation_lines` row | `BND-T4-01`, `-02`, `-05` | none (append-only; a reversal writes a mirror row) | terminal |
| `JOB_WORK_OUT` line | *open* (derived) | `open_quantity > 0` | `BND-T4-05` | `JOB_WORK_RETURN` rows, loss | active |
| MOOWR return | `DRAFT` | `whin_moowr_returns.status` | `BND-T1-01` | `BND-T1-02`, `-03` | initial |
| MOOWR return | `FILED` | `status`, `filed_by/at` | `BND-T1-03` | none | **terminal** |

### 1.2 Transitions

| ID | From | Event / action | To | Guard | Actor (permission) | Side effects | Comment | UI entry point | Source |
|---|---|---|---|---|---|---|---|---|---|
| BND-T1-01 | — | Generate the MOOWR return for licence × month | `DRAFT` | `BND-GRD-06` | `whin_moowr_returns:generate` | lines computed (`BND-T4-07`) | no | WS-339 **Generate** | FR-676 |
| BND-T1-02 | `DRAFT` | Regenerate | `DRAFT` | `BND-GRD-06` | `:generate` | lines recomputed; differences to the previous draft listed | no | WS-339 row **Regenerate** | FR-676 |
| BND-T1-03 | `DRAFT` | File | `FILED` | filer ≠ generator is **not** required (a statutory filing, not an approval) | `whin_moowr_returns:file` | lines frozen (trigger refuses UPDATE / DELETE); print | yes (filing reference) | WS-339 row **File** | FR-676 |
| BND-T1-04 | active ⇄ inactive | Switch a bond rule | — | — | `whin_bonded_exit_rules:edit` | audit row; takes effect on the next post | **yes** (reason) | WS-185 tab *Bond rules* | FR-671, FR-677 |

### 1.3 Guards

| ID | Predicate (must hold to proceed) | Refusal: HTTP · code · field | Message shape | DB backstop | Source |
|---|---|---|---|---|---|
| BND-GRD-01 | A forward post line that **rises at a virtual-counterparty location** in a duty status with `requires_licence` is accepted only when an **active** `whin_bonded_exit_rules` row matches (duty status, movement type, the location's base type, `RISE`) — or the type is one of the recorder's loss types or a VAS work-order type (existing exemptions), or a netting master merge | `409 BONDED_EXIT_NOT_RECORDED` · `lines[n].duty_status` (unchanged code) | names type, duty status and location type | guard on base's `WhbMovementPostGuard` chain | FR-670, MD-42 |
| BND-GRD-02 | The matched rule's site holds a `whin_bonded_licences` row of that duty status, `ACTIVE`, `valid_from ≤ posting date ≤ valid_to` | `409 BONDED_LICENCE_NOT_ACTIVE` · `lines[n].duty_status` | names licence kind, site, date | — | FR-671 |
| BND-GRD-03 | A rule exists for the line but is inactive | `409 BONDED_OPERATION_NOT_PERMITTED` · `lines[n].duty_status` | names duty status and operation kind | — | FR-671 |
| BND-GRD-04 | An order's consumption lines carry at most **one** licensed duty status (`bonded_duty_status` frozen at the first) | `409 BONDED_REGIME_MIXED` · `lines[n].dutyStatus` | names the frozen and the offered status | — | FR-673, MD-43 |
| BND-GRD-05 | A subcontract dispatch with any line in a licensed duty status carries `bond_permission_ref` (≤ 60) and `expected_return_date` | `422 BOND_PERMISSION_REF_REQUIRED` · `bondPermissionRef`; `422 EXPECTED_RETURN_DATE_REQUIRED` · `expectedReturnDate` | — | — | FR-675 |
| BND-GRD-06 | MOOWR return: licence `MOOWR` at the site; the month has ended (site timezone); no `FILED` return for licence × month | `409 MOOWR_RETURN_PERIOD_OPEN` · `period`; `409 MOOWR_RETURN_FILED` · `period` | — | uk(`licence_id`, `period_month`) | FR-676 |
| BND-GRD-07 | The same predicates (`-01`…`-03`) run again when a `PENDING` movement is approved, on its stored lines | as `-01`…`-03` | — | `WhinBondedVirtualExitApprovalGuard` | FR-671 |

### 1.4 Transitions that must be unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| BND-UNR-01 | Bonded stock leaving to `CUSTOMER`, `SUPPLIER`, `CONSUMED` or any location type no active rule names, without ex-bond clearance or a loss | `BND-GRD-01` — no seeded rule for those types | FR-670 |
| BND-UNR-02 | The guard deciding from a hard-coded list of MFG movement types | it reads `whin_bonded_exit_rules` (registry, `RL-001`); base keeps no customs flag (D-8) | MD-42 |
| BND-UNR-03 | Updating or deleting a register line; editing a `FILED` return | append-only and frozen triggers | FR-672, FR-676 |
| BND-UNR-04 | MFG writing a `whin_` table or importing `ai.warehouseindia` | rules and register are india's, run on base's post hook; MFG passes data through the core port only | FR-620 |
| BND-UNR-05 | Output of bonded inputs received as `DOMESTIC` | MFG sets the output duty status from `bonded_duty_status` (`BND-T4-03`) | FR-673 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra condition |
|---|---|---|---|---|
| BND-T2-01 | View register / export | `whin_bonded_operation_lines:view` / `:export` | — | AUDITOR views, never exports |
| BND-T2-02 | Generate / regenerate MOOWR return | `whin_moowr_returns:generate` | `DRAFT` or none | `BND-GRD-06` |
| BND-T2-03 | File MOOWR return | `whin_moowr_returns:file` | `DRAFT` | — |
| BND-T2-04 | Switch a bond rule | `whin_bonded_exit_rules:edit` | — | reason |
| BND-T2-05 | Dispatch bonded stock to a job worker | `whm_subcontract_dispatches:dispatch` | dispatch `DRAFT` | `BND-GRD-05` |

## 3. T3 — Time-driven rules & notifications

### 3.1 Statutory values — **RE-VERIFY** before ratification

| Value | Current reading | Held in | Owner |
|---|---|---|---|
| Manufacture in a bonded warehouse | permitted under s.65 Customs Act with the MOOWR Regulations 2019; a plain s.57/58 warehouse needs s.65 permission | rule rows per duty status (`BONDED` rows switchable) | india |
| Removal for job work | with the bond officer's permission, return within the permitted period | `bond_permission_ref`, `expected_return_date` | india |
| Monthly return | MOOWR return per licence per month, by the 10th of the next month | `whin_moowr_returns` | india |
| SEZ movements | per SEZ Rules, 2006 | `whin_sez_movements` | india |

### 3.2 Rules

| ID | Rule | Trigger | What it changes | Who is notified | Channel | Job class | Notify-once? | Source |
|---|---|---|---|---|---|---|---|---|
| BND-T3-01 | Bonded job work past its return date | `JOB_WORK_OUT` *open* and `expected_return_date < today` (site tz) | one compliance task (`whin_compliance_rules` row `BONDED_JOB_WORK_OVERDUE`, `V541160`) | holders of `whin_bonded_operation_lines:view` at the site | in-app | india compliance job (`V540180`) | once per line | FR-675 |
| BND-T3-02 | MOOWR return due | month ended, no `FILED` return by the 10th | none | holders of `whin_moowr_returns:file` | in-app | same job | once per licence × month | FR-676 |

## 4. T4 — Cross-entity effects

| ID | When this happens | Then this other record must change | Enforced in | Source |
|---|---|---|---|---|
| BND-T4-01 | Any post with a line matched by an active rule (`ISSUE` / `ISSUE_RETURN` at `PRODUCTION`; `PRODUCTION_RECEIPT` at `PRODUCTION` or `JOB_WORKER`; `SUBCONTRACT_DISPATCH` / `SUBCONTRACT_RECALL` at `JOB_WORKER`) | one `whin_bonded_operation_lines` row per line: licence, movement / line ids, operation kind, item, lot, duty status, base quantity, UoM, source document number | `WhinBondedOperationRecorder` on base's post hook, same transaction | FR-672 |
| BND-T4-02 | Reversal of such a movement | a mirror row (`reversal_of_id`, negated quantity); a `JOB_WORK_OUT` mirror re-opens nothing it did not open | same | FR-672 |
| BND-T4-03 | First consumption of licensed stock by an order (store issue line with cost object `PRODUCTION_ORDER`, or receipt backflush) | `whm_production_orders.bonded_duty_status` set (MFG reads the ledger line's duty status — base data); every later good output, co-product, by-product and processed item of the order is posted in that duty status (`MANUFACTURE_OUTPUT` rows by `BND-T4-01`) | MFG `CostObjectResolver.onIssuePosted` / receipt post | FR-673, MD-43 |
| BND-T4-04 | Scrap of licensed stock to `VIRT-SCRAP` (`PRODUCTION_RECEIPT` scrap line, approved `SUBCONTRACT_WRITE_OFF`) | one `whin_bonded_losses` row `OPEN` (rule kind `LOSS`, the existing recorder), resolved by india's existing paths; GitHub 539 decides whether normal process loss is a loss | `WhinBondedLossRecorder` | FR-674 |
| BND-T4-05 | Subcontract dispatch with a licensed line | `bond_permission_ref` and `expected_return_date` frozen on the dispatch and passed in `JobWorkDispatchPort.registerDispatch`; the `JOB_WORK_OUT` register row carries both and `open_quantity` = dispatched | MFG dispatch service (`SUB-T4-03`); india recorder | FR-675 |
| BND-T4-06 | Subcontract receipt / recall of that stock | `JOB_WORK_RETURN` rows reduce the dispatch's `open_quantity` (consumed in processed form, recalled, retained scrap → `BND-T4-04`); at 0 the `BND-T3-01` task closes | india recorder | FR-672, FR-675 |
| BND-T4-07 | MOOWR return generated | per item: opening (ledger before the month), received into bond, issued to manufacture, returned from manufacture, produced, sent for job work, returned from job work, cleared (ex-bond clearances, export), losses, closing — each a backend sum; closing = opening + in − out, asserted per line | `WhinMoowrReturnService` | FR-676 |
| BND-T4-08 | Register row of an `SEZ` duty status | one `whin_sez_movements` row | india recorder | FR-676 |

## 5. T5 — Screen contract (web only)

### 5.1 WS-338 Bonded Operations — `/warehouse/india/bonded-operations`

| | |
|---|---|
| **Type** | read-only register grid (reference **Department**, no Add / Edit) |
| **Grid identifier** | `whin_bonded_operation_lines` · filter scope `WAREHOUSE_INDIA_BONDED_OPERATION` |
| **Default sort** | `e.occurred_at DESC` |
| **Statistics tiles** | issued to manufacture (period) · produced in bond · out for job work (open) · overdue job work · losses `OPEN` |
| **Columns** | `occurredAt` (timestamp), `postingDate` (date-only, `formatDateSync`), `licenceNumber`, `dutyStatus` (`registryLabel`), `operationKind` (`registryLabel`), `documentNumber`, `itemCode`, `itemName`, `lotCode`, `baseQuantity`, `uomCode`, `openQuantity`, `expectedReturnDate` (date-only), `bondPermissionRef`, `isOverdue` |
| **Filters** | `warehouseId` → `licenceId`; `dutyStatus`, `operationKind` (enum); `itemId`; `postingFrom`/`postingTo` (`DateRangePicker`, date-only); `openOnly`, `overdueOnly` (boolean) — all in the scope's `COMMON_FILTER_CONFIGS` allowlist |
| **Row actions** | View (the source document) |
| **Export columns** | grid columns (superset); no created-by / updated-by column on the grid, so none in the export |

### 5.2 WS-339 MOOWR Returns — `/warehouse/india/moowr-returns`

| | |
|---|---|
| **Type** | list + transition modals (reference **Service Vehicle**) |
| **Grid identifier** | `whin_moowr_returns` · filter scope `WAREHOUSE_INDIA_MOOWR_RETURN` |
| **Default sort** | `e.period_month DESC` |
| **Statistics tiles** | `DRAFT` · `FILED` · due this month |
| **Columns** | `licenceNumber`, `periodMonth`, `status`, `lineCount`, `generatedAt` (timestamp), `filedAt` (timestamp), `filingReference`, `createdByName`, `updatedByName` |
| **Filters** | `warehouseId` → `licenceId`; `status`; `periodFrom`/`periodTo` |
| **Row actions** | View (lines tab) · Regenerate (`DRAFT`) · File (`DRAFT`) · Print · Export |
| **Toolbar** | **Generate** (modal: licence, month — `size="lg" minWidth={500} resizable`) · Export |

### 5.3 WS-185 Bonded Licences — tab *Bond rules*

Grid of `whin_bonded_exit_rules` (duty status, movement type, location type, direction, operation kind,
`is_active`), **Switch** row action with a reason (`BND-T1-04`); no add or delete — rows are seeded.

## 6. Out of scope

| Not built | Where / why |
|---|---|
| Bill of entry for home clearance of the output | india ex-bond clearance (`p4-07`) |
| Duty computation, interest | accounting / customs broker; not in warehouse |
| FTWZ manufacture | no rule seeded; FTWZ is trading and warehousing |
| Enablement decisions on process-loss treatment and MOOWR job work | GitHub 539, 543 (product owner) |
| Mobile | none (user rule) |

## 7. Amendments

| Date | Row IDs affected | Change | Found by |
|---|---|---|---|
| 2026-10-23 | all | v0 derived from FRD-MFG FR-670…677, MD-42, MD-43 and the as-built `WhinBondedVirtualExitPostGuard` | R30 `CP-GB-001`, `CP-GA-007`; `D-17` item 3 |

## 8. Invariants and scenarios this workflow must not break

| Invariant | Rows | Scenarios |
|---|---|---|
| No bonded stock leaves the regime unrecorded | `BND-GRD-01`, `BND-UNR-01` | `WH-SC-680`, `WH-SC-687` |
| Licence must be active | `BND-GRD-02` | `WH-SC-681` |
| One regime per order; output stays in bond | `BND-GRD-04`, `BND-T4-03` | `WH-SC-682` |
| Job work under permission, tracked to return | `BND-GRD-05`, `BND-T4-05`, `-06`, `BND-T3-01` | `WH-SC-683`…`WH-SC-685` |
| The return is computed, never typed, and frozen when filed | `BND-T4-07`, `BND-UNR-03` | `WH-SC-686` |
| India optional, port only (`L-1`, FR-620) | `BND-UNR-04` | `WH-SC-645` (india off: no licensed status exists, nothing here runs) |

## 9. Open rows — contradictions and holes

| ID | Contradiction / hole | Recommendation | Authority | Status |
|---|---|---|---|---|
| BND-OPEN-01 | GitHub 539: is normal process loss of MOOWR inputs a loss or a manufacturing waste shown only on the return? | default: a bonded loss (`BND-T4-04`); a decision to treat it as waste changes the rule kind for `PRODUCTION_RECEIPT` at `SCRAP` from `LOSS` to a register-only kind | product owner | open |
| BND-OPEN-02 | GitHub 543: MOOWR job work was refused everywhere; the default here allows it with the bond officer's permission | confirm the permission reference and the return period source | product owner | open |
| BND-OPEN-03 | `D-17` item 3 says "a registry flag on the movement types"; MD-42 makes it a registry row keyed by location type too | record MD-42 against `D-17` | SPINE | **resolved 2026-10-23** — `D-17` item 3 now states the rule per location type (`MD-42`) |
