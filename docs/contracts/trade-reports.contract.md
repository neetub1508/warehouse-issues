# Functional Contract — Trade reports pack (WS-312, eight read-only report grids)

> **What this is.** The functional truth for `warehouse-trade`'s eight report grids on WS-312 *Trade Reports*:
> what each one reads, how it is filtered, sorted, exported and drilled into, and what it must never do. The
> reports change nothing; every figure is computed in the backend from trade rows and core reads.
>
> **Why it exists.** R30 `CP-SC-005`: WS-312 was specified only in `issues/p9-14.md`'s table, with no actions,
> no tiles, no default filters or columns and no export rule beyond FR-616. This contract is that screen's §5.
>
> **Status.** Derived 2026-10-23 (v0). No code exists yet.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | none — read-only reports; each row drills into the document it came from |
| **Module** | `warehouse-trade` |
| **Domain baseline** | FRD-TRADE FR-619 (the eight reports), FR-616 (grid standards, currency grouping), FR-617 (permissions), `TRD-02` (purchase and sales mirrored), `TRD-03` (fulfilment derived from core on read), `TRD-06` (no money summed across currencies) · mirror rows M33 |
| **Owning task body** | `issues/p9-14.md` |
| **Primary tables** | none of its own — backend report queries over `wht_*` documents and core reads (`getReceiptPosition`, `getFulfilmentPosition`, `WhAvailableToPromiseQuery`); grid ids are not tables |
| **Permission resources** | `wht_rpt_open_po`, `wht_rpt_pr_ageing`, `wht_rpt_schedule_adherence`, `wht_rpt_dispatch_adherence`, `wht_rpt_contract_expiry`, `wht_rpt_open_so`, `wht_rpt_dispatch_backlog`, `wht_rpt_quotation_hit_rate` — each `:view`, `:export` |
| **Routes** | WS-312 `/warehouse/trade/reports/<report>` (FRD-TRADE §6; one tab per report) · mobile: none |
| **Contract status / version** | `derived` · `v0 — 2026-10-23` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Each of the eight reports lists, filters, sorts and paginates in SQL (`WH-SC-565`) | `TRP-T4-01`, §5 |
| A2 | No report or total adds money across currencies (`WH-SC-591`) | `TRP-GRD-01`, `TRP-UNR-02` |
| A3 | Export is a superset of the visible columns; the auditor views, never exports | `TRP-T2-02`, `-03` |
| A4 | A row drills into its source document; nothing on the screen writes | `TRP-UNR-01`, §5 |

## 1. T1 — State machine

None. A report has no state and no transition.

### 1.3 Guards

| ID | Predicate | Refusal | Source |
|---|---|---|---|
| TRP-GRD-01 | A money total is grouped by `currencyCode`; a request for an ungrouped total is not offered | — (no such endpoint) | FR-616, FR-619 |
| TRP-GRD-02 | Record scope: rows only for the companies and sites the caller is granted (core's company / site grants) | rows outside scope are not returned | FR-617 |
| TRP-GRD-03 | Sort key on the `SqlSortBuilder` whitelist of the report; default sort per §5 | unknown key → default sort | FR-616 |
| TRP-GRD-04 | Date range filters on date-only fields are inclusive and read as dates (no zone shift) | `422` field error on `from > to` | FR-616 |

### 1.4 Unreachable

| ID | Forbidden | Why | Source |
|---|---|---|---|
| TRP-UNR-01 | Any write from WS-312 | read-only endpoints; the row actions are links | FR-619 |
| TRP-UNR-02 | A total across currencies | `TRP-GRD-01` | FR-616, `TRD-06` |
| TRP-UNR-03 | A received / shipped quantity cached in `wht_` for a report | read from core on each request (`TRD-03`) | FR-619 |
| TRP-UNR-04 | Aggregation in the page | every figure is a backend column (CLAUDE.md rule 8) | FR-616 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| TRP-T2-01 | Open a report tab | `wht_rpt_<name>:view` | — | FR-619 |
| TRP-T2-02 | Export a report | `wht_rpt_<name>:export` (`hasAuthority(…) or hasRole('ADMIN')`) | — | FR-619 |
| TRP-T2-03 | Auditor | `:view` only (FR-617) | — | FR-617 |

## 3. T3 — Time-driven rules

None. Reports are computed on read; no job writes them.

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| TRP-T4-01 | Any report read | native SQL with LIMIT / OFFSET and a count query; core quantities by batch port reads for the page's documents only (never one call per row) | `TradeReportQueryService` | FR-616, FR-619 |
| TRP-T4-02 | Export | the same query without the page limit, columns ⊇ visible; money with its currency; date-only as dates | `TradeReportExportService` | FR-616 |

## 5. T5 — Screen contract

WS-312 *Trade Reports* (reference **Department**, read-only report grids; one tab per report). Every tab:
`DynamicDataTable` with its grid id and `preloadedGridPreferences`; `grid_column_definitions`,
`filter_definitions` and a `grid_preferences` row with **both** `default_columns` and `default_filters`; its
filter scope in `COMMON_FILTER_CONFIGS`; Export; no Add / Edit; statistics strip as stated (counts, or money
grouped by currency). Date-only columns use `formatDateSync`; timestamps `formatDateWithTimezoneSync`.

| Report · grid id · scope | Default columns | Default filters | Default sort | Tiles | Row action |
|---|---|---|---|---|---|
| Open PO register · `wht_rpt_open_po` · `WAREHOUSE_TRADE_RPT_OPEN_PO` | `poNumber`, `poType`, `supplierName`, `itemName`, `orderedQuantity`, `releasedQuantity`, `receivedQuantity`, `openQuantity`, `netPrice`, `openValue`, `currencyCode`, `nextDueDate`, `ackStatus` | `supplierId`, `warehouseId`, `poType`, `dueFrom`/`dueTo` | `nextDueDate ASC` | open lines · overdue lines · open value per currency | View PO (WS-293) |
| PR ageing · `wht_rpt_pr_ageing` · `WAREHOUSE_TRADE_RPT_PR_AGEING` | `prNumber`, `lineNo`, `itemName`, `departmentName`, `requesterName`, `requiredByDate`, `approvedAt`, `ageDays`, `lineStatus`, `allocatedQuantity` | `warehouseId`, `departmentId`, `lineStatus`, `ageingOnly` | `ageDays DESC` | open lines · past required date | View PR |
| Schedule adherence — purchase · `wht_rpt_schedule_adherence` · `WAREHOUSE_TRADE_RPT_SCHEDULE_ADHERENCE` | `supplierName`, `poNumber`, `scheduleLineNo`, `agreedDate`, `agreedQuantity`, `receivedDate`, `receivedQuantity`, `daysLate`, `isInFull`, `isOtif` | `supplierId`, `warehouseId`, `periodFrom`/`periodTo`, `itemCategoryId` | `agreedDate DESC` | lines · OTIF % | View PO |
| Dispatch adherence — sales · `wht_rpt_dispatch_adherence` · `WAREHOUSE_TRADE_RPT_DISPATCH_ADHERENCE` | `customerName`, `soNumber`, `scheduleLineNo`, `committedDate`, `committedQuantity`, `shippedDate`, `shippedQuantity`, `daysLate`, `isInFull`, `isOtif` | `customerId`, `warehouseId`, `periodFrom`/`periodTo`, `itemCategoryId` | `committedDate DESC` | lines · OTIF % | View SO (WS-304) |
| Rate contract expiry · `wht_rpt_contract_expiry` · `WAREHOUSE_TRADE_RPT_CONTRACT_EXPIRY` | `side`, `contractNumber`, `counterpartyName`, `validTo`, `terminatesOn`, `supersededOn`, `daysLeft`, `ceilingConsumedPercent`, `currencyCode` | `side`, `counterpartyId`, `expiringWithinDays` | `validTo ASC` | expiring ≤ 30 days · expired | View contract |
| Open SO register · `wht_rpt_open_so` · `WAREHOUSE_TRADE_RPT_OPEN_SO` | `soNumber`, `soType`, `customerName`, `customerPoNumber`, `itemName`, `orderedQuantity`, `releasedQuantity`, `shippedQuantity`, `openQuantity`, `netPrice`, `openValue`, `currencyCode`, `nextCommittedDate`, `ackStatus` | `customerId`, `warehouseId`, `soType`, `dueFrom`/`dueTo` | `nextCommittedDate ASC` | open lines · open value per currency | View SO |
| Dispatch backlog · `wht_rpt_dispatch_backlog` · `WAREHOUSE_TRADE_RPT_DISPATCH_BACKLOG` | `soNumber`, `scheduleLineNo`, `committedDate`, `dueQuantity`, `unreleasedQuantity`, `releasedNotShippedQuantity`, `atpShortfall`, `isAtRisk` | `customerId`, `warehouseId`, `horizonDays`, `atRiskOnly` | `committedDate ASC` | due lines · at risk | Plan dispatch (WS-305) |
| Quotation hit rate · `wht_rpt_quotation_hit_rate` · `WAREHOUSE_TRADE_RPT_QUOTATION_HIT_RATE` | `salesExecName`, `customerName`, `sentCount`, `wonCount`, `lostCount`, `expiredCount`, `hitRatePercent`, `wonValue`, `currencyCode` | `periodFrom`/`periodTo`, `customerId`, `salesExecId` | `hitRatePercent DESC` | quotations sent · hit rate % | Open WS-300 |

Empty state per tab: *No rows for the selected filters.* Export columns: the grid columns plus every
non-visible column of the definition (superset). Report grids have no created-by / updated-by column, so the
export has none either (grid ↔ export parity).

## R32 additions (PRD 2026-10-24, `D-20`)

Rows added by the R32 fold (FRD-TRADE §4.15). Numbers continue each kind's sequence; where a number exists on one side of the purchase / sales mirror only, the asymmetry is stated in FRD-TRADE §5 rows M35…M40.

| ID | Kind | Rule | Refusal / effect | Source |
|---|---|---|---|---|
| TRP-T4-03 | effect | Reports `wht_rpt_direct_po`, `wht_rpt_pr_to_po_lead_time`, `wht_rpt_purchase_price_history`, `wht_rpt_enquiry_conversion` — backend queries, grid + export, money grouped by currency; menu split *Trade Reports — Purchase* / *— Sales* | — | FR-759 |
| TRP-T4-04 | effect | WS-315 Order Book and report `wht_rpt_so_pending_production` (ordered − produced − reserved free stock; ordered = FIXED line qty / BLANKET `FIRM` qty / OPEN released qty) read core production progress (`CN-19`, declared by `P8-26`, MFG implements), shipments and billings | — | FR-776 |
| TRP-T4-05 | effect | Report *Sample status* (PRD §13.1) under *Trade Reports — Sales*: enquiry lines with a sample request, MFG status and customer feedback read live through `SampleRequestPort.status` (`CN-19`); permissions `wht_rpt_sample_status:{view,export}`; empty with *No manufacturing module* without MFG | `403` without the verb | FR-776 |
| TRP-T2-04 | action | WS-316 Customer 360 with `wht_customer_profiles:view_360`; trade + warehouse data only; each tab exports (audited) | `403` without the verb | FR-777 |

## 6. Out of scope

| Item | Decision |
|---|---|
| Lost-sale and fill-rate reporting | core (`wh_insufficient_stock_log`, P7-11 *Stock KPIs*); trade only produces the rows (FR-680, FR-681) |
| Charts, scheduled e-mail of a report | not in v1 |

## 7. Amendments

| Date | Rows | Change | Found by |
|---|---|---|---|
| 2026-10-23 | all | v0 derived from `issues/p9-14.md` (Reports table) and FRD-TRADE FR-616, FR-619 | R30 `CP-SC-005` |
| 2026-10-23 | §2 | R31: Source column added to the T2 table (F-TR-019) | R31 |
| 2026-10-25 | `TRP-T4-04`, `TRP-T4-05` (new) | R32-fix: order-book ordered basis per SO type; *Sample status* report leaf (ledger `crm-so-dispatch-reports:13.1-04` reclassified AMEND) | R32 review F-R32TR-025, -035 |
| 2026-10-25 | `TRP-T4-03`, `TRP-T4-04`, `TRP-T2-04` (new, *R32 additions*) | R32 fold of the client PRD (`D-20`): four reports, menu split, order book, SO pending to produce, customer 360 | R32 / `D-20` |

## 8. Invariants and scenarios

`WH-SC-565` (auditor sweep), `WH-SC-591` (currency grouping).

## 9. Open rows

None.
