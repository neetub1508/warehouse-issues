# COEXISTENCE — the cost of `D-9`, named and costed

> **`DECISIONS.md` `D-9` is settled: `accessories` inventory stays permanently separate. This
> document does not argue with that.** It makes the consequence visible, it verifies every claim
> against the live codebase, and it turns nine mitigations into buildable specifications — two of
> which `D-9` already makes **mandatory in v1**.
>
> Subordinate to [`DECISIONS.md`](DECISIONS.md). Where a source review disagrees with it, the
> correction is stated in §8, never applied silently.

**The one-sentence version.** Separation is the right call and it buys real things — a live revenue
flow keeps shipping with zero migration risk — but it costs a second item master, a second UoM
vocabulary, a second warehouse master, two stock truths with no reconciliation, and **one failure
mode that is not merely unmitigated but undetectable**: the same physical unit counted in both
systems. `D-9` makes two detective controls mandatory in v1 precisely because of that last one, and
§5 `M1` and `M2` specify them.

**Every count in this document carries the command that produced it, run 2026-09-01 against
`/Users/bbhushan/work/git/workspace/classic`.** Every claim about behaviour carries `file:line`.

---

## §1 — What `accessories` actually is

### 1.1 The tables

`accessories` owns **71** tables in total, of which **19** are inventory-scoped.

```
# total
grep -rhoiE 'CREATE TABLE (IF NOT EXISTS )?(public\.)?accessory_[a-z_]+' \
  accessories/backend/src/main/resources/db/migration/ \
  | sed -E 's/.*(accessory_[a-z_]+)/\1/' | sort -u | wc -l          # -> 71

# inventory-scoped subset
… | grep -cE 'stock|inventory|warehouse|storage_bin|issuance|uom'   # -> 19
```

| # | Table | Created at | What it is |
|---|---|---|---|
| 1 | `accessory_warehouses` | `V30017:8` | Warehouse master. `code`, `name`, `warehouse_type ('MAIN','SATELLITE','VIRTUAL','RETURNS')`, address, `capacity INTEGER`. **No `branch_id`** |
| 2 | `accessory_warehouse_branch` | `V30018:8` | Many-to-many junction warehouse ↔ platform branch |
| 3 | `accessory_storage_bins` | `V30033:8` | `bin_code`, `warehouse_id`, and **free-text** `zone` / `aisle` / `rack` / `level` VARCHARs, `bin_type`, `max_weight`, `max_volume`. No zone entity, no bin hierarchy, no putaway rules; the capacity columns are stored and never read |
| 4 | `accessory_uom` | `V30013:8` | UoM master. `name`, `symbol`, `uom_type` (vocabulary in a SQL comment, **no `CHECK`**), `base_unit_id` self-FK, `conversion_factor DECIMAL(18,6)` — **the factor is on the UoM, not on the item** |
| 5 | `accessory_uom_company` | `V30014:8` | UoM ↔ company junction |
| 6 | `accessory_stock_levels` | `V30130:6` | **The balance.** `product_id`, `warehouse_id`, `bin_id`, `quantity_on_hand DECIMAL(18,4)`, `quantity_reserved`, `quantity_available GENERATED ALWAYS AS (on_hand − reserved) STORED`, `batch_number VARCHAR(50)`, `serial_number VARCHAR(100)`, `expiry_date`, `average_cost`, `last_cost`, `last_count_date`, `last_movement_date`. Unique on `(product, warehouse, COALESCE(bin), COALESCE(batch), COALESCE(serial))` (`:40-46`) |
| 7 | `accessory_inventory_transactions` | `V30131:6` | **The movement log** — and *also* the Stock Receipt entity. `transaction_number` unique, `transaction_date`, `transaction_type VARCHAR(30)` (vocabulary in a comment at `:10`, **no `CHECK`**), `product_id`, single `quantity`, nullable `uom_id`, `from_warehouse_id`/`from_bin_id`/`to_warehouse_id`/`to_bin_id`, `unit_cost`, `total_cost`, `reference_type`/`reference_id`/`reference_number` (vocabulary in a comment at `:27`, no registry), batch/serial/expiry |
| 8 | `accessory_stock_adjustments` | `V30132:6` | Adjustment document |
| 9–10 | `accessory_stock_transfers` · `_items` | `V30133:6` · `V30134:6` | Transfer header + lines |
| 11–12 | `accessory_inventory_counts` · `_items` | `V30135:6` · `V30136:6` | Count header + lines |
| 13 | `accessory_stock_receipt_documents` | `V30215:6` | Receipt attachments |
| 14 | `accessory_stock_receipt_history` | `V30216:20` | Receipt edit history |
| 15–16 | `accessory_stock_receipt_imports` · `_import_batches` | `V30293:6` · `V30293:67` | Bulk receipt import staging |
| 17–18 | `accessory_issuance_records` · `_items` | `V30212:9` · `V30212:29` | Issuance against a sales order |
| 19 | `accessory_insufficient_stock_logs` | `V30290:8` | Log of blocked / pended issuances |

The item master is a twentieth table that is **not** inventory-scoped by name and is entirely
load-bearing for stock: **`accessory_products`** (`V30050:8`) — `sku VARCHAR(50)`, `barcode`,
`name`, `category_id`, `brand_id`, `manufacturer_id`, **one** `uom_id`, weight/dimensions,
`base_cost_price`, `base_selling_price`, `min_stock_level INTEGER`, `max_stock_level`,
`reorder_point`, `reorder_quantity`, `lead_time_days`, `is_serialized BOOLEAN`,
`is_batch_tracked BOOLEAN`, `vehicle_compatibility JSONB` (`:42`), `mrp` (added by `V30217:2`),
`sub_category_id` (`V30225`), `product_number` (`V30229`). Unique key
`uk_accessory_products_sku UNIQUE(sku, deleted_at)` (`:62`) — i.e. **a globally unique SKU**. No
`company_id`; a junction table carries it (`:61`).

### 1.2 The rest of the surface

| Surface | Count | Command / evidence |
|---|---|---|
| Backend Java files in `**/inventory*` packages | **71** | `service/inventory` 43 + `dto/response/inventory` 13 + `dto/request/inventory` 15 — `find accessories/backend/src/main/java -type d -iname 'inventory*' -exec sh -c 'ls -1 "$1"/*.java \| wc -l' _ {} \;` |
| Backend Java files whose path matches the wider stock vocabulary | **181** | `find accessories/backend/src/main/java -name '*.java' \| grep -icE 'inventory\|stock\|warehouse\|storagebin\|uom\|issuance'` |
| Web routes, top level | **21**, of which **10** are inventory | `ls -d accessories/frontend/src/app/accessories/*/` → `inventory`, `inventory-counts`, `stock-adjustments`, `stock-receipt-imports`, `stock-receipts`, `stock-transfers`, `storage-bins`, `units-of-measure`, `warehouses`, `reports` |
| Reports | **11**, all inventory or sales-over-inventory | `ls accessories/frontend/src/app/accessories/reports/` → `stock-summary`, `stock-movement`, `low-stock`, `insufficient-stock`, `inventory-valuation`, `warehouse-utilization`, `slow-moving`, `top-selling`, `category-performance`, `sales-summary`, `return-analysis` |
| Mobile screens | **33** `accessory*`, of which **14** are inventory | `ls mobile/src/screens/ \| grep -c '^accessory'`; inventory subset by `grep -iE 'stock\|inventory\|warehouse\|storagebin\|uom\|issuance'` |
| Permission resources | **36** distinct `accessory-*`, of which **17** are inventory | `grep -rhoE "'accessory-[a-z-]+'" accessories/…/db/migration/*.sql \| sort -u` |
| Filter scopes in `platform/frontend/src/utils/filterUtils.ts` | **33** `ACCESSORY_*`, of which **15** are inventory | `grep -oE "^  ACCESSORY_[A-Z_]+:" platform/frontend/src/utils/filterUtils.ts \| wc -l`; the block runs `:1624`–`:2269` |
| Report-type registry | `V30257__seed_accessories_report_types_and_default_configs.sql` (+ `V30288`) | the registry `M9` proposes reusing |
| Global setting | `ACCESSORIES_ENFORCE_STOCK_VALIDATION` | `AccessoryStockEnforcementSettingService.java:17`; read at `SalesOrderQueryService.java:402` |

### 1.3 The workflows

Six, all live: **stock receipt** (with edit / deactivate / reactivate and a bulk-import pipeline),
**stock adjustment**, **stock transfer** (draft → submit → approve → ship → receive, with cancel),
**inventory count**, **issuance from a sales order** (with a configurable insufficient-stock policy),
and the **11 reports**. Plus the accessories sales chain that consumes stock — quotations, sales
orders, deliveries, returns.

### 1.4 What it does well — stated first, because the decision rests on it

- **Grid / filter / export / report machinery is complete and standards-compliant**: DB-level
  pagination, `SqlSortBuilder` whitelists, filter-aware statistics, branch-scoped queries, 11 reports
  with summary cards computed over the whole filtered set.
- **Bin-level granularity exists in the schema**, and the balance's unique index correctly treats
  bin / batch / serial as part of the identity via `COALESCE` sentinels (`V30130:40-46`).
- **A configurable enforcement switch** — block issuance on insufficient stock, or issue and mark
  `PENDING` — with a log table and a report behind it. That is a genuinely good product decision and
  `C-045` recommends warehouse copy the *idea*.
- **Receipt edit / deactivate / reactivate reverses and re-applies stock** rather than soft-deleting
  and leaving the balance wrong (`StockReceiptService.java:374-411`, `:417-421`).

### 1.5 What it structurally is **not** — verified

This matters because it decides whether warehouse could have *inherited* anything, and the answer is
no. Each row was re-verified for this document; where R1's line reference has moved, the verified one
is given and the difference noted.

| # | Claim | Verified evidence | R1 |
|---|---|---|---|
| 1 | **There is no double-sided stock ledger.** `accessory_inventory_transactions` has a single `quantity` and *optional* from/to warehouses. It is a log written **next to** an in-place update of `accessory_stock_levels`, not the source of the balance. Nothing recomputes the balance from movements and nothing reconciles them | balance writes at `StockReceiptService.java:346-367`, `StockAdjustmentService.java:401`; entity helpers `StockLevel.java:170-186`; DDL `V30131:11-20` (one `quantity`, four nullable location columns) | `C-021` |
| 2 | **Some balance changes write no movement at all.** `reverseStockLevel()` subtracts the receipt quantity, recomputes the average cost, saves the balance — and inserts **no** `InventoryTransaction`. From that moment the log and the balance disagree, permanently and silently | `StockReceiptService.java:374-411` — the method body ends at `stockLevelRepository.save(stockLevel)` `:408` with no `transactionRepository.save` anywhere between `:374` and `:411`. The only `transactionRepository.save` calls in the file are at `:119`, `:167`, `:242`, all on the forward path | `C-021` |
| 3 | **Reservations do not exist.** `quantity_reserved` is a column and `quantity_available` is `GENERATED ALWAYS AS (quantity_on_hand − quantity_reserved) STORED` (`V30130:14`), so available **always equals on hand** | `grep -rn "reserveQuantity\|releaseReservedQuantity" accessories/backend/src/main/java \| grep -v '/entity/'` → **0 hits**. The methods exist only as `StockLevel.java:190` and `:199` | `C-022` |
| 4 | **Physical counts never post.** `generateAdjustments()` validates, sets `count.setStatus("POSTED")`, saves the count, logs the audit line — and creates no adjustment, writes no stock level and inserts no transaction | `InventoryCountService.java:325-345`; `grep -c "StockLevel" .../InventoryCountService.java` → **0** | `C-023` (line range refined from `:322-345`) |
| 5 | **No UoM conversion is ever applied.** `accessory_stock_levels` has **no UoM column at all** (`grep -n uom V30130*.sql` → no match) and `accessory_inventory_transactions.uom_id` is nullable and never used in arithmetic. All stock is in one implicit unit | `grep -rln conversionFactor accessories/backend/src/main/java` → **5 files**, all display/CRUD: `Uom.java`, `UomRequest.java`, `UomResponse.java`, `UomMapper.java`, `UomExportService.java`. And the factor lives on the **UoM master** (`V30013:13-14`), not the item | `C-026` |
| 6 | **Valuation is one moving-average number on the balance row.** No cost layers, no FIFO, no as-at-date, no revaluation. The reversal path recomputes the average by **subtracting the reversed receipt's own cost**, which is not the inverse of a weighted average and therefore drifts | forward AVCO at `StockReceiptService.java:346-364`; reverse at `:386-408` | `C-027` |
| 7 | **The valuation report does not use the average cost the module maintains.** Every valuation figure — the report rows, the summary cards and the default sort — is `quantity_on_hand * last_cost` | `StockReportQueryService.java:544` (default sort `COALESCE(sl.quantity_on_hand * sl.last_cost, 0) DESC`); `StockLevelRepository.java:236`, `:296`, `:451` (`SUM(COALESCE(sl.quantity_on_hand * sl.last_cost, 0)) AS total_stock_value` / `AS stock_value`) | `C-027` |
| 8 | **Lots and serials are strings on the balance row**, part of a composite index. No lot master, no serial master, no genealogy, no split/merge, no uniqueness — a serial number is unique nowhere | `V30130:17-19`, `:40-46` | `C-028` |
| 9 | **No concurrency control on stock anywhere.** No `@Version` on `StockLevel`, no `@Lock` on `StockLevelRepository`, **no `CHECK (quantity_on_hand >= 0)` in any migration**, and no pessimistic locking in the module at all. The guard is a Java read-compare-write, and the code comment names the race it loses | `grep -n "@Version\|@Lock" StockLevel.java StockLevelRepository.java` → **0 hits**; `grep -rn quantity_on_hand accessories/…/db/migration/ \| grep -i check` → **0**; `grep -rn "PESSIMISTIC\|FOR UPDATE" accessories/backend/src/main/java` → **0**. The comment: *"Callers pre-check availability (on hand less reserved), so this only fires when that check raced against another movement"* — `InventoryStockAdjustmentService.java:63-65` | `C-024` |
| 10 | **Issuing against a product with no stock-level row silently succeeds.** `issueStock()` logs a warning and returns — no deduction, no transaction, no error to the caller | `InventoryStockAdjustmentService.java:56-60` | `C-025` |
| 11 | **Issuance swallows non-business exceptions.** A `BusinessException` correctly propagates (`:270-276`), but the general `catch (Exception e)` immediately after logs *"Stock adjustment failed for product {}, continuing"* and continues — so a DB error during deduction lets the issuance complete with stock unchanged | `AccessoryIssuanceService.java:277-279` (refined from R1's `:275-278`) | `C-025` |
| 12 | **Issuance is bin-blind.** `issueStock()` resolves the balance with `findByProductAndWarehouse`, so with bin-level rows present the deduction hits an arbitrary row | `InventoryStockAdjustmentService.java:52-54` | `C-025` |
| 13 | **No supplier anywhere in receiving.** `StockReceiptRequest` has exactly **ten** fields and none is a vendor, a PO or a shipper: `productId`, `warehouseId`, `binId`, `quantity`, `unitCost`, `referenceNumber`, `batchNumber`, `serialNumber`, `expiryDate`, `notes` | `StockReceiptRequest.java:23,26,28,32,35,40,43,46,48,51` | `C-031` |
| 14 | **Transit is a document status, not a stock state.** `shipTransfer()` deducts from source and sets `transfer.setStatus("IN_TRANSIT")`; `receiveTransfer()` adds to destination. **Between the two the goods are on no balance row anywhere** | `StockTransferService.java:283-316` (ship, deduction call at `:298`, status at `:301`), `:495-...` (`deductStockFromSource`), `:322` / `:554` (receive, `addStockToDestination`) | `C-021`; **refines R1 §5.1 item 15** — the two-step transfer *is* modelled, as a document; it is the in-transit *stock* that does not exist |
| 15 | **No PO, ASN, GRN, QC, putaway, wave, pick/pack/ship, kitting, RMA-to-stock, replenishment run, cycle-count schedule, slotting, labour, dock or yard** | absence across the 71-table list | `C-021`…`C-031` |
| 16 | **Nothing is extractable as a library.** None of it sits behind an interface, none is in a shared artifact, and `StockLevel` / `InventoryTransaction` are FK-bound to `accessory_products`, `accessory_warehouses`, `accessory_storage_bins` and `accessory_uom` | `V30130:34-36` (product · warehouse · bin) and `V30131:44-49` (product · **uom** · from/to warehouse · from/to bin) | `C-032` |

> **The conclusion this section exists to support:** given rows 1–16, warehouse would not inherit
> anything worth keeping. **`D-9` is right on the merits, not merely on the risk.** What must be
> budgeted is the duplication — and what must be *built* is the detection in §5.

---

## §2 — Correct the premise: it is three stock systems, not two

`D-9` and R3 §5.1 both make this point and it is the single most useful correction in the document.
**Two stock systems is a priced decision. Three is an accident.**

### 2.1 The map — who holds stock in this suite today

| # | System | Grain | Ledger? | Value? | Evidence | Status |
|---|---|---|---|---|---|---|
| **1** | **`accessories`** — `accessory_stock_levels` + `accessory_inventory_transactions` | product × warehouse × bin × batch-string × serial-string | **No.** Single-sided log beside an in-place-mutated balance; some paths write no movement at all | AVCO maintained, `last_cost` reported (§1.5 rows 6–7) | §1 | **Live, in production.** `D-9`: stays |
| **2** | **`dealer` PDI** — `pdi_vehicle_inventory`, `pdi_stock_yards`, `pdi_yard_storage_locations`, `pdi_storage_slot_assignments` | **one physical serialised unit per row.** Quantity-free: no UoM, no cost, no lot, no reservation, no partial quantity | Occupancy is **derived, not cached**; assignments are append-only with `released_at` retained and exclusivity by **partial unique index** | none | 26 `pdi_*` tables (`grep -rhoiE 'CREATE TABLE .*pdi_[a-z_]+' dealer/…/db/migration/ \| sort -u \| wc -l` → **26**); `dealer/…/V20735:8`, `:57-59`, `:62-64`; `PdiYardStorageLocationService.java:67`; `PdiStockYardMapper.java:83`, `:118` | **Live.** `OD-2`: **not** migrated in v1 or v2; a documented future adapter |
| **3** | **`services.parts_used`** — a **`TEXT` column** | free text | no | no | `services/…/V40095__Change_parts_used_from_jsonb_to_text.sql` — *"used as free-text input"*, and the default `'[]'::jsonb` was dropped to `NULL` | **Live.** The clean-sheet case: `warehouse-adapter-services` is **v1** |
| **4** | **`accounting`** — `acc_stock_balances`, `acc_valuation_entries`, `acc_cost_layers`, `acc_godowns`, `acc_batches`, `acc_stock_journals`, `acc_physical_stock_counts` | item × godown × batch × serial | designed: `acc_valuation_entries` is *"every quantity move with its value"* | FIFO layers + consumptions | `accounting/docs/DATA-MODEL.md:436` (`acc_valuation_entries`), `:434` (`acc_cost_layers`), `:435` (consumptions), `:507` (`acc_stock_balances`) | **Designed, unbuilt — phase P3.** Resolved by `D-6` and `OD-1` |
| **5** | **`warehouse`** — `whb_stock_movements` + `whb_stock_positions` | the full `L-5` nine-member key | double-sided, append-only, immutable, rebuildable | `D-6`: quantity here, value in accounting | `DECISIONS.md` `D-4`, `L-1`…`L-14` | **To be built** |
| — | **`services`, `field-service`, `assets`, `insurance-360`, `submittals`** | — | — | — | `grep -rhoiE 'CREATE TABLE (IF NOT EXISTS )?[a-z_]*(stock\|inventory\|spare\|consumable)[a-z_]*' <module>/…/db/migration/ \| sort -u \| wc -l` → **0** for all five | **No stock capability at all.** These are warehouse's actual market inside the suite |

### 2.2 What `D-6` and `OD-1` do about #4

Left alone, systems #4 and #5 would be **two products both authoritative for quantity, at two
grains, with two counts and two adjustment documents.** `D-6` resolves it in one sentence —
*"`warehouse` is the system of record for every movement, position, count, adjustment and physical
truth, at full grain; `accounting` is the system of record for **value**"* — and `OD-1` books the
reciprocal edit to the accounting design set, with a deadline: *before accounting's P3 starts, and
before warehouse `P0-02` writes `whb_stock_movements`.*

**Two things make `OD-1` cheaper than R5 assumed, and they should be said so the deadline is not
treated as tighter than it is:**

1. **The accounting set already calls `acc_stock_balances` a cache** — *"maintained in the posting
   transaction and rebuilt nightly with a drift alert, exactly as `acc_account_balances` is. **It is
   a cache**, subject to the same L-9 discipline: derived, never authoritative"*
   (`accounting/docs/DATA-MODEL.md:507`). Demoting it to a read-through projection of the warehouse
   ledger is therefore a change of *source*, not a change of *kind*.
2. **All of it is phase P3 and unbuilt** — `acc_cost_layers` (`:434`), `acc_valuation_entries`
   (`:436`), `acc_stock_balances` (`:507`) and `acc_source_document_movements` (`:277`) are every one
   marked `P3`. The edit is to a design document, not to a table with rows in it.

**What `OD-1` still has to decide, and this document flags rather than answers:** the port column
`acc_source_document_movements.unit_cost` is write-once (`accounting/docs/DATA-MODEL.md:277`), and
R5 `S-071` shows landed cost makes a receipt's unit cost **not final at receipt** — duty, freight and
clearing arrive weeks later on a different document. A write-once `unit_cost` cannot carry that, and
warehouse's answer (`IRREVERSIBLE.md` `IRR-37`, value-only movements with `quantity = 0`) needs the
port to accept one.

### 2.3 And the thing the map makes obvious

**Four of the five verticals in the dealer stack have no stock capability whatsoever.** `services`,
`field-service` and `assets` return zero on the table grep above, and `services` records a job's
parts as free `TEXT`. That — not accessories — is warehouse's addressable surface inside this suite,
and it is why `D-9` costs less than it first appears: warehouse is not competing with accessories
for a customer, it is serving the four modules accessories was never going to serve.

---

## §3 — The costs, itemised

R3 §5.2's eleven costs, each re-verified against the codebase, with **who notices** and **when** —
because a cost nobody experiences is not a cost, and a cost the *customer* experiences is a different
budget line from one an *engineer* experiences.

| # | Cost | Verified, in this codebase | Who notices | When |
|---|---|---|---|---|
| **C1** | **Duplicate item master** | A floor mat is `accessory_products` (`sku VARCHAR(50)`, `barcode`, one `uom_id`, `min_stock_level INTEGER`, `mrp`, `uk(sku, deleted_at)` — `V30050:8-63`, `V30217:2`) **and** `whb_items` (`code`, `whb_item_identifiers`, `base_uom_code`, per-item conversions, `uk(owner_id, sku)`). Two codes, two barcode tables, **two UoM vocabularies** (`accessory_uom` `V30013:8` vs `whb_uoms`), two category trees. Every price change, every barcode addition, every MRP update is two edits | **Data-entry staff, daily.** Then the parts manager, when the two disagree | Week one of running both |
| **C2** | **Two stock truths for one physical shelf** | Group quantity is `accessory_stock_levels.quantity_on_hand + whb_stock_positions.quantity_on_hand`, and **nothing prevents the same physical unit being in both.** There is no cross-map table today: `acc_company_external_refs` is the **only** external-ref table in the entire repository (`grep -rhoiE 'CREATE TABLE .*(external_ref\|xref\|cross_map\|item_map)' */backend/src/main/resources/db/migration/` → one hit, in `accounting-base`) | **Nobody — that is the problem.** See §3.1 | Never, unaided |
| **C3** | **No consolidated valuation, and the two numbers are not comparable** | Accessories values at `quantity_on_hand * last_cost` (`StockLevelRepository.java:236`, `:296`, `:451`) while *maintaining* `average_cost` on the same row and never using it. Warehouse will value from cost layers (`OD-6`: weighted average + FIFO). **Three methods across two systems, one of them not the one the module thinks it uses.** They cannot be summed without a caveat, and the caveat is exactly what an auditor will not accept | **The CFO and the statutory auditor** | First year-end |
| **C4** | **Reports cannot be unified** | 11 accessories report grids (`V30166`–`V30177`) with their own `grid_column_definitions`, all reading `accessory_stock_levels` **directly** — `StockReportQueryService` injects `StockLevelRepository`, `InventoryTransactionRepository`, `WarehouseRepository`, `StorageBinRepository` (`:36-49`) and nothing else. Warehouse ships its own. *"Ageing across the whole business"* means running two reports and pasting them together | **The parts manager and the GM** | First management review |
| **C5** | **Two warehouse masters for one building** | `accessory_warehouses` (`V30017:8`) has **no `branch_id`**; the link is the many-to-many `accessory_warehouse_branch` (`V30018:8`). `whb_warehouses` has one `REGISTERED` branch at a time, with dated history (`IRREVERSIBLE.md` `IRR-57`, `D-14`). The same physical godown is two rows with **different branch semantics**, so a godown-wise stock statement for the site is not producible | **The accountant**, at GST filing | First return after go-live |
| **C6** | **No cross-system availability at the counter** | *"Not in stock here — 2 at the other branch"* cannot see accessories stock from a warehouse screen, and the accessories screen cannot see parts stock. The counterman checks two screens, or does not check | **The customer**, as a lost sale | Immediately, and invisibly — a lost sale leaves no row |
| **C7** | **Two GST treatments of one transfer** | A branch transfer of mixed stock is **one lorry, one e-way bill, one tax invoice** — and two systems, neither of which can produce the combined document. Accessories transfers have no statutory document layer at all | **The despatch clerk**, at the gate, with a truck waiting | First inter-state transfer |
| **C8** | **Double the compliance surface** | HSN, UQC, batch/expiry, MRP, delivery challan and e-way must be built **twice**, or accessories stays non-compliant. **`accessory_products` has no HSN column**: the module's only `hsn_code` is on `accessory_quotation_pricing_components` (`V30066:37`), a pricing line, not a product. `accessory_uom` has no UQC code. So the second build has not started | **The compliance owner** | The quarter `warehouse-india` ships |
| **C9** | **Two remediation streams forever** | Every schema gap in §1.5 is a gap in accessories too, and fixing warehouse fixes none of them: strings for batch/serial (row 8), no cost layers (row 6), reservations with no rows behind them (row 3), transit as a status (row 14), **no concurrency control at all** (row 9). Each future finding is triaged twice | **Engineering**, every sprint | Continuously |
| **C10** | **Two mobile surfaces** | **14** `accessory*` inventory screens on mobile (`accessoryStockLevel`, `accessoryStockReceipt`, `accessoryStockTransfer`, `accessoryStockAdjustment`, `accessoryInventoryCount`, `accessoryStorageBin`, `accessoryWarehouse`, `accessoryUom` + 6 report screens) and a warehouse RF/handheld family alongside. A storeman scanning stock has **two apps' worth of screens for one job**, and `D-13` makes the warehouse half non-optional | **The storeman**, every shift | Day one of v1.1 |
| **C11** | **Migration debt compounds** | The longer both run, the more history exists in the losing schema — so a merge, if ever reconsidered, gets **monotonically more expensive**. §7 costs the reversal explicitly so this is a known curve rather than a surprise | **Whoever revisits `D-9`** | Increasing, forever |

### 3.1 The load-bearing one: **C2 is not unmitigated, it is undetectable**

State it as plainly as it deserves, because everything in §5 exists to change this sentence:

> If a floor mat is receipted in `accessories` and also received in `warehouse` — which happens the
> first time a dealer's parts store stocks an accessory line — **the group stock figure is wrong and
> there is no query, no report, no constraint and no job anywhere in the suite that can notice.**

Why it is undetectable rather than merely unfixed, in three verified facts:

1. **There is no shared key.** `accessory_products.sku` and `whb_items.code` are independent
   namespaces. No table joins them, and the only external-ref table in the repository is
   `acc_company_external_refs` in `accounting-base` (§3 C2). Nothing can even *ask* whether two rows
   are the same part.
2. **There is no shared vocabulary to fall back on.** UoM is two tables with two symbol sets;
   accessories' factor is on the UoM master (`V30013:13-14`) and warehouse's is on the item
   (`IRREVERSIBLE.md` `IRR-34`). A quantity match is not evidence of the same part, and a name match is
   not evidence of anything.
3. **There is no report that spans both.** Every accessories report reads `accessory_stock_levels`
   directly (`StockReportQueryService.java:36-49`), and a warehouse report cannot union them without
   a compile-time dependency on `accessories` — which `D-11` B4 and `D-9` both forbid.

**The failure is silent in both directions**: double-counted stock inflates the balance sheet, and a
part deliberately held in only one system reads as a stock-out in the other. Neither raises anything.

**This is exactly why `D-9` makes `M1` and `M2` mandatory in v1 rather than advisory.** They do not
prevent C2 — nothing short of a merge does — they make it **detectable**, which is the whole
difference between a known cost and a silent one.

### 3.2 Two costs the other lenses found that R3 §5 does not list

| # | Cost | Evidence | Who notices |
|---|---|---|---|
| **C12** | **The `ACCESSORIES` source-system string must be reserved and defended, or the separation is defeated by a well-meaning agent.** Without a reserved, unclaimable row, a future author uses `ACCESSORIES` as a `source_system` for something else — and, worse, an agent "completes" the adapter set by writing `warehouse-adapter-accessories`, which is decision drift disguised as tidiness | R7 §4.6 items 1–2; `IRREVERSIBLE.md` §5 registry #3 | Nobody, until a movement is posted with the wrong lineage — and lineage is `PNR-1`, so it is not repairable |
| **C13** | **An adapter that "just reads" `accessory_stock_levels` defeats the separation silently.** The rule has to be stated as a prohibition *and* asserted, because the first violation is always innocent — a cross-system availability lookup that reads the table directly instead of calling an endpoint | R3 `E-087`; R7 §4.3 B9 | Nobody at the time; engineering, when accessories changes its balance semantics and the adapter breaks |

---

## §4 — What is **not** lost

Stated so the decision is not over-attacked, and because two of these are bankable rather than
rhetorical.

- **Accessories inventory works and is in production.** It has branch scope, guards, import, export,
  11 reports and a mobile surface, and it serves a genuinely different business — retail accessory
  sales with quotations, orders, deliveries, discounting and fitment. Warehouse is not a better
  version of that; it is a different product.
- **Zero migration risk to a live module and zero regression risk to a working revenue flow.** No
  data move, no cut-over, no reconciliation certificate, no chance of a wrong balance on a Monday
  morning. This is the benefit, it is real, and it is presumably why the decision was taken.
- **Warehouse loses nothing it wanted.** Per §1.5, there is no ledger, no reservations, no posting
  count, no UoM conversion, no cost layers, no lot or serial entity, no concurrency control and no
  supplier to inherit. Absorption would have meant importing 19 tables of shape that `D-4` exists to
  reject.
- **The four verticals that matter are untouched.** `services`, `field-service`, `assets` and dealer
  spare parts have **zero** stock tables (§2.1). Warehouse's v1 market inside the suite is
  unaffected by `D-9` in either direction.
- **The good ideas are still copyable, and two should be copied.** The insufficient-stock
  enforcement switch plus its log and report (`AccessoryStockEnforcementSettingService.java:17`,
  `accessory_insufficient_stock_logs` `V30290:8`) — `C-045` recommends warehouse ship the same as
  `WAREHOUSE_ALLOW_NEGATIVE_STOCK`. And the `COALESCE`-sentinel unique index on a balance with
  nullable members (`V30130:40-46`) is a solved problem worth reading before choosing
  `NULLS NOT DISTINCT` instead (`accounting/docs/DATA-MODEL.md:507` records why the accounting set
  went the other way).
- **Nothing here is a one-way door.** §7 shows the reversal is expensive but not impossible, and
  that building `M1` properly makes it materially cheaper.

---

## §5 — The mitigations, as buildable specifications

R3 §5.4 proposes nine merge-free mitigations. This section turns each into something a task file can
be written from: the tables, the columns, the screens, the reports, the module, the band, the version
and the phase.

**Two of the nine are mandatory in v1 by `D-9` and are tasks, not advice** — `M1` and `M2`. R3 names
four as load-bearing (`M1`, `M2`, `M7`, `M8`); `D-9` promotes two of those to obligations and this
document keeps `M7` and `M8` as strong recommendations with owners named.

**On task ids.** `warehouse-issues/issues/` is empty (`ls issues/` → no files) and
`GAP-REGISTER.md` does not exist yet, so **no task id is invented below.** Each mitigation names the
**phase** that must own it, per `DECISIONS.md` §5 — `P0` ledger foundation · `P1` masters, identity,
inbound · `P2` outbound, counting, valuation, reports · `P3` execution & mobile · `P4` India · `P5`
3PL/channels · `P6` optimisation. Whoever writes the task files allocates the ids.

### M1 — The cross-map registry · **MANDATORY, v1** · `warehouse-base` · **P1** owns the table, **P2** owns the report

**Addresses:** C1, C2, C12. **Source:** R3 `M1`/`E-083`, `D-9` obligation 1, `IRREVERSIBLE.md` `IRR-25`.

**The table is `whb_item_external_refs`** — `D-9` names it, and it is one of the three external-ref
tables `IRR-25` already requires for the adapter join. Adding the accessories rows costs **no new
table**. Shape verbatim from `accounting-base/…/V600001__Create_acc_companies_and_external_refs.sql:204-229`:

```
whb_item_external_refs (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id        UUID         NULL,          -- NULL where map_status <> 'MAPPED'
  source_module  VARCHAR(30)  NOT NULL,      -- opaque string, NOT an FK: 'ACCESSORIES', 'DEALER', …
  external_entity VARCHAR(60) NOT NULL,      -- 'accessory_products'
  external_id    VARCHAR(100) NOT NULL,      -- the accessory_products.id, rendered as text
  external_code  VARCHAR(100) NULL,          -- the accessory_products.sku, for human reading
  map_status     VARCHAR(30)  NOT NULL,      -- see below. NO CHECK: it is a catalogue value
  mapped_by      UUID NULL REFERENCES users(id),
  mapped_at      TIMESTAMPTZ NULL,
  map_note       TEXT NULL,
  is_active, status, version, created_at, updated_at, created_by, updated_by,
  CONSTRAINT uk_whb_item_external_refs_source_external UNIQUE (source_module, external_id),
  CONSTRAINT fk_whb_item_external_refs_item FOREIGN KEY (item_id)
      REFERENCES whb_items (id) ON DELETE RESTRICT
)
```

- **`map_status` values** (R3's enrichment, carried forward): `MAPPED` · `UNMAPPED` · `AMBIGUOUS` ·
  **`DELIBERATELY_SEPARATE`**. The fourth is the one that makes the registry honest — it is how a
  deliberate duplication is recorded as a decision rather than read as an omission.
- **`map_status` carries no `CHECK`**, per `D-10` and `IRREVERSIBLE.md` §5. It is a catalogue value,
  and `DELIBERATELY_SEPARATE_PENDING_REVIEW` will be wanted within a year.
- **`item_id` is nullable** — an `UNMAPPED` row is the whole point of the registry, and a `NOT NULL`
  FK would make the unmapped case unrecordable.
- **`uk(source_module, external_id)` — map, not mirror.** One accessories product resolves to at most
  one warehouse item. **No index on `item_id`**: the accounting precedent states why (`:231-233`) —
  the query this table serves is *"which warehouse item is source X's item Y"*, which the unique key
  seeks directly.

**`D-9`'s obligation, precisely:** *an `ACCESSORIES` source-module row for every dual-stocked SKU.*
Read literally that is only the overlap, and the overlap is exactly what nobody can compute yet. So
the buildable form is stronger and cheaper:

> **Every `accessory_products` row gets a `whb_item_external_refs` row**, seeded once and maintained
> by the reconciliation job, with `map_status` recording what is known. `DELIBERATELY_SEPARATE` is
> the expected value for most of them. The dual-stocked set is then a **query**
> (`map_status = 'MAPPED'`) rather than a judgement.

**How it is populated without a cross-module read** — because `D-11` B1/B4 forbid `warehouse-base`
importing `ai.accessories` or reading `accessory_*`:

| Path | Mechanism | Version |
|---|---|---|
| **Seed** | A CSV/XLSX import through the standard import framework, shaped on `AccImportHandlerRegistry` + `acc_import_batches`/`_rows` with a reversal path (`C-020`). The implementer exports `accessory_products` once and imports it | **v1** |
| **Ongoing** | A screen: *Item cross-map* — grid + filter + export, with a row action to map / unmap / mark deliberately separate | **v1** |
| **Never** | A direct read of `accessory_products` from `warehouse-base`. That is `D-11` B1/B4 and `M8` | — |

**The screen** — `warehouse-base` frontend, following the Department canonical reference:
`whItemCrossMapManagementTable.tsx`, `whItemCrossMapFilter.tsx`, `whItemCrossMapModal.tsx`,
`whItemCrossMapViewModal.tsx`. Grid identifier `wh_item_cross_map`; filter scope
`WH_ITEM_CROSS_MAP` in `COMMON_FILTER_CONFIGS`; permission resource `wh-item-cross-map`; a mobile
counterpart per `D-13`. **Filenames must be globally unique** — `Dockerfile.frontend:80-177` merges
module `src/` trees with `cp -r`, last write wins (`C-012`).

**The report** — *Unmapped and ambiguous external items*, scheduled nightly, listing every
`whb_item_external_refs` row where `map_status IN ('UNMAPPED','AMBIGUOUS')`, grouped by
`source_module`, with counts and an export. **Not** a statistics tile — filter-aware statistics must
not be given a `statistics.*` cache name in this repo (`C-043`).

**The invariant the registry buys:** *"how much of part X do we hold"* becomes answerable for every
`MAPPED` row, and every `UNMAPPED` row is a named, dated, exportable admission that it is not.

### M2 — The category-ownership rule · **MANDATORY, v1** · `warehouse-base` · **P1** table, **P2** report

**Addresses:** C2. **Source:** R3 `M2`/`E-086`, `D-9` obligation 2.

R3 proposes *"an ownership rule written into the FRD"*. **A rule in prose is not a control.** `D-9`
says *"recorded as data"*, and that is the difference between something an auditor can test and
something an engineer can forget. Specification:

```
whb_category_stocking_ownership (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id         UUID NOT NULL,
  category_scope     VARCHAR(30)  NOT NULL,   -- 'WAREHOUSE_CATEGORY' | 'EXTERNAL_CATEGORY'
  category_ref       VARCHAR(100) NOT NULL,   -- whb_item_categories.code, or the external code
  stocking_system    VARCHAR(30)  NOT NULL,   -- 'WAREHOUSE' | 'ACCESSORIES'. NO CHECK - catalogue
  effective_from     DATE NOT NULL,
  effective_to       DATE NULL,
  decided_by         UUID NOT NULL REFERENCES users(id),
  decision_note      TEXT NOT NULL,           -- NOT NULL deliberately: a rule with no reason gets reversed by the next person
  is_active, status, version, audit columns,
  CONSTRAINT uk_whb_category_stocking_ownership
      UNIQUE (company_id, category_scope, category_ref, effective_from)
)
```

- **Exactly one stocking system per category per company per effective period.** The unique key plus
  an overlap guard in the service layer; the `L-8`-style trigger is not needed here because the row
  is master data, not a ledger entry.
- **`effective_from`/`effective_to`** because ownership *moves*: a category migrated from accessories
  to warehouse must be answerable historically, or last year's violation report re-renders as clean.
- **`stocking_system` carries no `CHECK`** — a third system (a future POS, a channel) is a seed row.

**The report — *Dual-stocked item reconciliation* — is the actual control**, and it is a **detective**
control, not a preventive one. Nothing can prevent a receipt in the other module. Its rows:

| Exception | Condition | Severity |
|---|---|---|
| **Dual-stocked** | An item with `map_status = 'MAPPED'` holding non-zero stock in **both** systems on the same as-at date | **the C2 failure, caught.** Critical |
| **Wrong-system stock** | An item whose category's `stocking_system` is `ACCESSORIES` holding stock in `whb_stock_positions` (or the reverse) | Warning |
| **Unmapped with stock** | A warehouse item with stock and no `whb_item_external_refs` row, where its category is declared dual-eligible | Warning |
| **Category undeclared** | A category with items in either system and no `whb_category_stocking_ownership` row | Info — but it is the row that means the control is not yet armed |

**The accessories half of the input.** `warehouse` cannot read `accessory_stock_levels` (`M8`,
`D-11` B9), so the accessories quantity arrives the same way its item master does: an operator-run
or scheduled **export from accessories** loaded into a staging table
(`whb_external_stock_snapshots (source_module, external_id, as_at_date, quantity_on_hand,
loaded_at)`), and the report runs over the snapshot.

> **Say the limitation out loud on the report itself**, in the header, not a footnote: *"Accessories
> quantities as at `<loaded_at>`, loaded by snapshot. This report is a detective control and does
> not prevent double-stocking."* A control whose staleness is invisible is worse than no control,
> because it is trusted.

**Version:** the table and the snapshot loader are **v1** (`P1`); the report is **v1** (`P2`).
`D-9` makes the pair mandatory, so neither may slip to v1.1.

### M3 — Union valuation report · **v1.1** · `warehouse` · **P2** · **AND IT IS DISPUTED**

**Addresses:** C3, C4. **Source:** R3 `M3`/`E-084` — *versus* R7 §4.6 item 4.

**The conflict, stated because both lenses are in this repository and they disagree:**

- **R3 `M3`** — build `group-inventory-valuation`, a read-only report that UNIONs
  `accessory_stock_levels` (valued at its cost basis) with `whb_stock_positions` (valued from the
  cost layers), tagged by `source_system`, **with the differing-method caveat rendered on the report
  itself**. *"Ugly, honest, and the only way a CFO gets one number without a merge."*
- **R7 §4.6 item 4** — *"`G-051` is that the **report** gap is the part customers will actually hit,
  and the honest mitigation is a documented 'these two inventories are separate' statement in the
  UI, not a union view."*

**Neither is settled by `DECISIONS.md`.** It is a product decision, it gates no migration, and it
should not be decided by whichever document is read last.

**Recommendation, offered and not imposed: build it, and make the caveat structural rather than
textual.** The argument for R3 is that the CFO adds the two numbers anyway, in a spreadsheet, with
no caveat at all — so refusing to build the report does not prevent the union, it only prevents the
warning travelling with it. The argument for R7 is that a report implies comparability, and §3 C3
shows these two numbers are **not** comparable: accessories values at
`quantity_on_hand * last_cost` (`StockLevelRepository.java:236`) while maintaining an unused
`average_cost`, and warehouse values from layers.

The reconciling shape: **render the two totals side by side and never print a sum.** Two labelled
columns, a `source_system` tag on every row, the valuation method named per column, the snapshot
staleness from `M2` in the header — and **no grand total anywhere on the page or in the export**. A
report that refuses to add them up makes the same point R7 wants made, in the place the user is
standing.

> **This needs an `OD-` row in `DECISIONS.md`.** That document owns the `OD-` namespace, so this
> document does not allocate one. The deadline is *before the `P2` reports task is written*.

### M4 — Shared vocabularies · **v1.1** · both sides · **P1** authors it

**Addresses:** C1, C4, C5. **Source:** R3 `M4`/`E-085`.

Seed UoM codes, reason codes, movement-type names and warehouse codes from **one list** even though
the tables stay separate — so `M3`'s report and any future migration are **mechanical rather than
interpretive**.

Concretely: a one-page vocabulary appendix in this design set, then two seed migrations —
`warehouse-base` in `V500000–V509999` seeding `whb_uoms` / `whb_reason_codes` /
`whb_movement_types`, and **a companion migration in the accessories band `V30000–V39999`** aligning
`accessory_uom.symbol` to the same codes. The second is an edit to a live module and needs its owner's
consent; it is listed here so the cost is visible, not assumed.

**Note the shape mismatch that alignment does not fix:** accessories' conversion factor lives on the
**UoM master** with a `base_unit_id` self-FK (`V30013:13-14`); warehouse's lives on the **item**
(`IRREVERSIBLE.md` `IRR-34`), because a case of one item is not a case of another. Aligning the *codes*
is worth doing; aligning the *semantics* is not possible without changing accessories.

### M5 — Cross-system availability lookup · **v1.1** · `warehouse` · **P2**

**Addresses:** C6. **Source:** R3 `M5`, extending `E-057`.

A read-only endpoint returning availability by branch for a mapped item, consumed by **both**
counters. `GET /api/warehouse/availability?itemId=&branchId=` returns warehouse availability plus,
for a `MAPPED` `whb_item_external_refs` row, the accessories quantity **from the `M2` snapshot** —
with `as_at` on the response so the caller can render the staleness.

**It must not read `accessory_stock_levels` directly** (`M8`, `D-11` B9, C13). If a live accessories
number is wanted rather than a snapshot, the correct shape is an endpoint **published by
accessories** and called by warehouse — which is a change to accessories and therefore that module's
decision to make, not this design set's.

### M6 — One document layer for statutory movements · **v2** *(corrected from R3's v1.1)* · `warehouse-india` · **P4**

**Addresses:** C7. **Source:** R3 `M6`/`E-049`/`E-051`.

`whin_delivery_challans` + `whin_transport_details` accept lines sourced from **either** system, so
one transfer produces one challan and one e-way bill even when the goods come from two ledgers. The
line carries `source_system` + `external_id` and, for accessories lines, resolves the item through
`whb_item_external_refs`.

**Two corrections to R3 here.** The tables are `whin_`, not `wh_`, because `D-1` and `D-3` place every
India rule in `warehouse-india` (`V540000–V549999`) — R3 predates `D-1`. And the version is **v2**,
not v1.1, because `DECISIONS.md` §5 places `P4` India in v2; R3's v1.1 is superseded.

### M7 — Backport the compliance columns to accessories · **v1** · `accessories` · **not this design set's to build**

**Addresses:** C8. **Source:** R3 `M7`, mirroring `E-047`.

`accessory_products.hsn_code`, a UQC code on `accessory_uom`, MRP on the batch. Verified need:
**`accessory_products` has no HSN column at all** — the module's only `hsn_code` is on
`accessory_quotation_pricing_components` (`V30066:37`), a pricing line, not a product.

**This is required whether or not warehouse is ever built**, which is precisely why it is listed and
why it is **not** a warehouse task. It belongs to the accessories module's own backlog, in its own
band (`V30000–V39999`). Listing it here is the mechanism by which the warehouse design set hands a
finding to a neighbour rather than absorbing it.

### M8 — No cross-writes, ever · **v1** · all modules · **P0** asserts it

**Addresses:** C2, C9, C13. **Source:** R3 `M8`/`E-087`, R7 §4.3 B9, §4.6 items 1–3.

The full rule is §6. The **build-time assertion** is the part that belongs to a phase:
`WarehouseBaseCouplingTest` (R7 §4.4 layer 1) asserts that no source file under
`warehouse-base/backend/src/main/java` contains `import ai.accessories`, that no migration in
`V500000–V509999` references `accessory_` in a `REFERENCES` clause, and that
`whb_source_systems` contains an `ACCESSORIES` row with `is_reserved = true` and
`is_claimable = false` that no adapter claims.

> **`ai.accessories` is the only vertical forbidden *by decision* rather than by the general rule.**
> Every other vertical is forbidden to `warehouse-base` because base depends on nothing; accessories
> is additionally forbidden to **adapters**, which are otherwise allowed to read their own vertical.
> The comment in the test must say which rule it is enforcing, or a later reader will "fix" it.

### M9 — One reporting scope · **v1.1** · `warehouse` · **P2**

**Addresses:** C4. **Source:** R3 `M9`/`E-085`.

Register warehouse report grids under the **same report-type registry accessories already uses** —
`V30257__seed_accessories_report_types_and_default_configs.sql`, extended by `V30288` — so a user
sees **one** Reports menu even though the data comes from two engines.

**Verified, and the answer is the good one.** `report_types` is a **platform** table, created at
`platform/…/V431__create_report_types_and_seed_platform_reports.sql:12`, and `V30257` merely
`INSERT`s into it (`:9-11`, `ON CONFLICT (code) DO NOTHING`). So warehouse seeding it is not a
cross-module write and `M8` is not engaged. Command:
`grep -rl "CREATE TABLE.*report_type" */backend/src/main/resources/db/migration/` → one hit, in
`platform`.

**And `report_types.module` is `VARCHAR(50) NOT NULL` with no `CHECK`** (`V431:12`), so `'warehouse'`
needs no widening migration — unlike `widget_definitions.chk_module`, which has been dropped and
rebuilt three times and still admits neither `warehouse` nor `logistics` (`C-014`). One free row per
warehouse report type; add `idx_report_types_module` is already there (`V431:23`).

### 5.1 Summary — what actually gets built, and when

| Mitigation | Obligation | Module · band | Version | Phase | New tables |
|---|---|---|---|---|---|
| **M1** cross-map registry + screen + nightly exception report | **`D-9` mandatory** | `warehouse-base` · V500000–V509999 | **v1** | P1 · P2 | none new (`whb_item_external_refs` is already `IRR-25`) |
| **M2** category-ownership rule + reconciliation report | **`D-9` mandatory** | `warehouse-base` · V500000–V509999 | **v1** | P1 · P2 | `whb_category_stocking_ownership`, `whb_external_stock_snapshots` |
| **M3** side-by-side valuation, no grand total | **disputed — needs an `OD-` row** | `warehouse` · V510000–V519999 | v1.1 | P2 | none |
| **M4** shared vocabularies | recommended | both · two bands | v1.1 | P1 | none |
| **M5** cross-system availability endpoint | recommended | `warehouse` | v1.1 | P2 | none |
| **M6** one statutory document layer | recommended | **`warehouse-india`** · V540000–V549999 | **v2** *(corrected from R3's v1.1)* | P4 | `whin_delivery_challans`, `whin_transport_details` |
| **M7** compliance columns on accessories | **hand-off — not ours** | `accessories` · V30000–V39999 | v1 | — | none |
| **M8** no cross-writes | **`D-11` invariant** | all | **v1** | P0 | none |
| **M9** one reporting scope | recommended · **verified free** | `warehouse` | v1.1 | P2 | none |

**Two new tables in total.** That is the entire schema cost of making an undetectable problem
detectable.

---

## §6 — The rules of engagement

Two ledgers is a cost. **Two ledgers with cross-writes is a corruption**, and it is a corruption
that arrives innocently — the first violation is always a helpful read.

### 6.1 The no-cross-writes rule

> **Neither system writes the other's tables. Ever. In either direction. Including "just a read that
> becomes a write later", including a migration, including a support script, including a one-off
> data fix.**

| Actor | May **write** | May **read** |
|---|---|---|
| `warehouse-base` | its own `whb_*` only | its own `whb_*`, plus the whitelisted platform set (`users`, `user_details`, `branches`, `documents`, and the permission/menu/grid tables it seeds) |
| `warehouse` | `wh_*` and, through the port, `whb_*` | `whb_*`, `wh_*`, platform |
| `warehouse-adapter-<vertical>` | its own `whad_`/`whas_`/`whaf_`/`whaa_` tables only. Stock **only through the movement port** | its own tables, its own vertical's tables, and warehouse **through the public API of R7 §4.2** — never a direct `whb_*` table read |
| **any warehouse module or adapter** | **never `accessory_*`** | **never `accessory_*`** — not `accessory_stock_levels`, not `accessory_products`, not for a "read-only availability lookup" |
| `accessories` | its own `accessory_*` only | its own. If it ever needs warehouse stock it uses **the same inbound port and the same public API as everyone else** |

**Why "never read" and not just "never write".** R7 §4.3 B9 states it and R3 `E-087` states it, and
the reason is that a read creates a **coupling to another module's balance semantics**. The moment an
adapter reads `accessory_stock_levels.quantity_available`, it has silently adopted the fact that
available always equals on-hand there (§1.5 row 3) — and it breaks, in production, on the day
accessories implements reservations. A read is a write to your own assumptions.

**The one legitimate channel between the two, and it is one-directional and offline:** the
`whb_external_stock_snapshots` load of `M2`, which is an **import**, carries an `as_at` date, and is
rendered as stale wherever it is shown.

### 6.2 What each side may **show** about the other

| Screen | May show | May **not** show |
|---|---|---|
| An **accessories** screen | Nothing about warehouse stock. Accessories is not being modified by this design set and gains no warehouse awareness | Any warehouse quantity, item or location |
| A **warehouse** grid or view modal | Nothing about accessories stock. A warehouse grid shows warehouse positions | Any accessories quantity inline in a stock grid — it would read as one number when it is two |
| The **`M1` cross-map screen** | The accessories SKU, name and `map_status`, from `whb_item_external_refs` — which are **warehouse's own rows**, not a cross-module read | A live accessories quantity |
| The **`M2` reconciliation report** | Both quantities, side by side, **with the snapshot `as_at` in the header** | A summed group total |
| The **`M3` valuation report** (if built) | Both totals, side by side, method named per column | **A grand total. Anywhere. Including the export** |
| The **`M5` availability endpoint** | Warehouse availability, plus the snapshot accessories figure with its `as_at` | The accessories figure presented as live |

**One UI rule that costs nothing and prevents the most likely misreading:** wherever both numbers
appear, they appear in **two labelled columns with the source named**, never in one column with a
tag. A tag gets sorted, filtered and summed; a column does not.

### 6.3 Go-live, when a customer has both

This is the situation the rules exist for, and it happens on day one at any dealership group that
already runs accessories and buys warehouse for its parts store.

| Step | What happens | Owner | Gate |
|---|---|---|---|
| **1** | **Declare category ownership before any stock is loaded.** Every item category gets a `whb_category_stocking_ownership` row with a `decision_note`. A category with no row is a **blocker**, not a warning | Implementation + the customer's parts manager | **`M2` armed** |
| **2** | **Seed the cross-map.** Export `accessory_products`, import into `whb_item_external_refs`. Every row gets a `map_status`; the default is `DELIBERATELY_SEPARATE` and every `MAPPED` row is a deliberate act with a named `mapped_by` | Implementation | **`M1` armed** |
| **3** | **Load warehouse opening stock**, as `OPENING` movements so the ledger starts balanced — with quantity **and** cost, batch, expiry, serial, bin and owner, staged, dry-runnable and re-runnable after a failed attempt. It is a first-class feature, not an import script (`E-088`) | Implementation | Ledger balances; a full rebuild reproduces positions (`L-4`) |
| **4** | **Run the `M2` reconciliation before the customer sees a number.** Every dual-stocked exception is resolved — by moving the stock, or by recording the duplication as a decision | Implementation | **Zero unexplained Critical rows** |
| **5** | **Agree the counter script.** For a category owned by accessories, the warehouse counter screen shows nothing and the counterman uses the accessories screen. This is a **training and process** answer, and pretending otherwise is how C6 becomes a lost sale nobody logs | Implementation + branch manager | Written into the cut-over checklist |
| **6** | **Schedule the snapshot load and the two reports.** Nightly. With a **silence alert** — a reconciliation report that has not run is indistinguishable from a clean one, which is the failure mode accounting's `acc_alert_conditions` was built for (*"a scheduled job that did not run — silence, not failure"*, `accounting/docs/DATA-MODEL.md` alert-conditions row) | Implementation | Both reports produce output on day one |
| **7** | **Record the residual risk in the cut-over sign-off**, in one sentence the customer reads: *"Accessory and warehouse stock are separate systems. Group quantity is the sum of two reports and is reconciled nightly, not continuously."* | Implementation lead | Customer signature |

**The failure mode to design against is step 5, not steps 1–4.** Steps 1–4 are engineering and they
get done. Step 5 is a habit, and a counterman who checks one screen when the answer is on the other
loses the sale silently — no row, no exception, no report. `M5`'s availability endpoint is the only
technical mitigation and it is v1.1, so **for the whole of v1 this is a process control**. Say so in
the sign-off rather than discovering it in month two.

---

## §7 — The reversal path

Stated neutrally and in one place, so the option is not lost. **This is not an argument to revisit
`D-9`.** It is the answer to *"what if we ever do?"*, costed, so that the decision to keep the
separation stays a decision rather than becoming an assumption.

### 7.1 What a merge would actually be

Not a migration. A merge is **four projects**, and only the first is a data move:

| # | Project | What it is | Cost driver |
|---|---|---|---|
| **1** | **Item master consolidation** | Map every `accessory_products` row to a `whb_items` row, or create one. Resolve SKU collisions (accessories' key is `uk(sku, deleted_at)` — **globally unique**, `V30050:62`; warehouse's is `uk(owner_id, sku)`), two barcode namespaces, two category trees, two UoM vocabularies with **different conversion semantics** (factor on the UoM master vs on the item) | **Human judgement per SKU.** Not automatable beyond an exact-code match |
| **2** | **Opening-balance cut-over, not a history migration** | Post one `OPENING` movement per `accessory_stock_levels` row into `whb_stock_movements`, at the balance's quantity and `average_cost`, against a virtual `OPENING` counterparty. **Accessories history is not migrated** — see §7.2 | Mechanical, once project 1 is done |
| **3** | **Application rewrite** | 71 backend files in `**/inventory*` packages (181 by the wider vocabulary), 10 web routes, 11 reports, 14 mobile screens, 17 permission resources, 15 filter scopes. **None of it is extractable**: no interfaces, no shared artifact, and `StockLevel`/`InventoryTransaction` are FK-bound to `accessory_products`, `accessory_warehouses`, `accessory_storage_bins` (`V30130:34-36`) and `accessory_uom` (`V30131:44-49`). Extraction is a rewrite, not a refactor | **The largest of the four**, and it grows with every accessories release |
| **4** | **Decommission** | 19 tables retained read-only or archived, their screens removed, their permissions revoked, their menu entries removed, their filter scopes deleted from `filterUtils.ts`, their report types deactivated. Plus every downstream consumer inside accessories' own sales chain — quotations, sales orders, deliveries, returns all reference stock | Coupled to project 3 |

### 7.2 The part that cannot be recovered, whenever the merge happens

**Accessories history does not migrate.** It cannot, and the reason is `IRREVERSIBLE.md`'s own
argument turned around: `accessory_inventory_transactions` is single-sided, some balance changes
wrote no movement at all (`StockReceiptService.java:374-411`), counts never posted
(`InventoryCountService.java:325-345`) and reservations never existed — so the log **cannot be
replayed into a conserving ledger** because it does not conserve. There is no double-sided history
to import at any price.

So a merge is always an **opening-balance cut-over**: the warehouse ledger begins on the cut-over
date, and accessories history is retained in read-only tables for as long as retention requires. That
is C11's curve — the retained-history period grows monotonically, and with it the number of years for
which two reports must be run to answer one question.

### 7.3 What building it this way costs, and what it saves

| Doing it the way this document describes | Effect on a future reversal |
|---|---|
| **`M1` cross-map, populated for every SKU from v1** | **Saves the largest single cost.** Project 1 — the human-judgement item mapping — is *already done*, incrementally, by people who knew the answer at the time. A merge inherits a complete, dated, attributed map instead of commissioning one. **This is the strongest argument for `M1` beyond detection** |
| **`M2` category ownership with `effective_from`/`effective_to`** | The cut-over set is a query, not a discovery exercise. Categories already owned by warehouse need no migration at all |
| **`M4` shared vocabularies (if built)** | UoM and reason-code alignment is the second-largest judgement cost in project 1, and `M4` retires it in advance |
| **`M8` no cross-writes** | Guarantees there is no hidden third state to reconcile. Every cross-write that *had* been permitted would be a row nobody can classify at merge time |
| **`M2`'s `whb_external_stock_snapshots`** | The loader is already the opening-balance staging path. Project 2 reuses it |
| **`D-9`'s reserved `ACCESSORIES` `whb_source_systems` row** | The merge's `OPENING` movements have a correct, pre-existing `source_system` lineage, so they are distinguishable from organic movements forever |
| **Deferring `M1`/`M2` to "when we need them"** | The map is then commissioned at merge time by people who **do not know** which of two same-named parts was which. Project 1 becomes a discovery project on cold data, which is the expensive version |

**The one-line summary:** building the detection makes the reversal roughly **one project cheaper**
out of four, and it is the project that has no mechanical shortcut. That is a side effect of `M1`,
not its purpose — but it is the reason `M1` should be populated for **every** SKU rather than only
for the ones believed to be dual-stocked.

### 7.4 What would have to be true to revisit `D-9`

Recorded so the trigger is a fact rather than a mood. Any **two** of these, together, would justify
re-opening it:

1. A customer running both reports a **material** dual-stocked variance — one that changes a filed
   number — in the `M2` report, more than once.
2. The accessories module needs `C8`'s compliance surface (HSN, UQC, MRP-on-batch, challan, e-way)
   in a jurisdiction where it is mandatory, i.e. `M7` is no longer optional and is a build rather
   than three columns.
3. A single customer's counter staff are demonstrably losing sales to `C6`, and `M5` has shipped and
   has not fixed it.
4. The accessories inventory code is being remediated anyway for `C9` reasons at a cost approaching
   project 3.

**None of these is true today**, which is why `D-9` stands. Re-evaluate at the **v2 planning gate**,
with the `M2` report's own history as the evidence — which is a further reason to build it in v1.

---

## §8 — Corrections, conflicts and what could not be verified

### 8.1 Where a source review is superseded by `DECISIONS.md`

| Source | What it says | Superseded by | Effect here |
|---|---|---|---|
| **R3 §5.4 `M1`/`E-083`** names the table **`wh_external_item_map`**; R3 uses `wh_` for base tables throughout (`wh_items`, `wh_stock_balances`, `wh_uoms`, `wh_cost_layers`) | — | `D-3` — **`wh_` is the *application*, `whb_` is the base**; *"R3's usage is the one that changes"*. `D-9` names the table **`whb_item_external_refs`** | §5 `M1` uses `whb_item_external_refs`. R3's `map_status` enrichment is carried forward verbatim because it is the useful part |
| **R3 `M6`/`E-049`/`E-051`** puts the statutory document layer in `wh_*` at **v1.1** | — | `D-1` creates **`warehouse-india`** as the fifth module; `D-3` gives it the `whin_` prefix; `D-2` gives it `V540000–V549999`; `DECISIONS.md` §5 places `P4` India in **v2**. R3 predates `D-1` | §5 `M6` corrected to `whin_*`, `warehouse-india`, **v2** |
| **R3 §5.1** lists the third stock system as `accounting` *"quantity + value + FIFO layers"* implying a live competitor | — | The accounting set now calls `acc_stock_balances` a **cache** — *"derived, never authoritative"* (`accounting/docs/DATA-MODEL.md:507`) — and every stock table there is **phase P3, unbuilt** (`:434`, `:436`, `:507`) | §2.2 records that `OD-1` is cheaper than R3 and R5 assumed. `D-6`'s substance is unchanged |
| **R7 §4.5** uses the adapter table prefix **`wha_<vertical>_`**; **R7 §4.4** layer-1 assertion 2 asserts on the token `wha_` | — | `D-3` fixes **`whad_`** (dealer), **`whas_`** (services), **`whaf_`** (field-service), **`whaa_`** (assets) | §6.1 uses `D-3`'s prefixes. The coupling test's token list must be updated to the four, or it asserts on a prefix that never appears |
| **R1 §5.1 headline** — *"17 of its 71 tables are inventory-scoped"*, quoted forward into `D-9` | — | R1's own table enumerates **19** distinct table names (its rows compound `_items`, `_history`, `_imports` and `_company` siblings) | §1.1 states **19**, with the command. `D-9`'s "17 tables" is R1's headline, not a different fact — the underlying surface is identical and the budget conclusion is unchanged |
| **R1 §5.1 item 15** — *"the goods are never in transit, so a two-step transfer is not modelled"* | — | Verified more precisely | The two-step transfer **is** modelled, as a **document** (`StockTransferService.java:283-316`, `:322`). What does not exist is in-transit **stock**: between ship and receive the goods are on no balance row anywhere. R1's conclusion holds; the mechanism is R3 `E-032`'s *"transit as a status"* |
| **R1 `C-025`** cites the issuance exception-swallow at `AccessoryIssuanceService.java:275-278` | — | Verified at **`:277-279`** | Line reference refined in §1.5 row 11. The `BusinessException` branch immediately above (`:270-276`) correctly re-throws, with a comment explaining why; it is the general `catch (Exception e)` that continues |
| **R1 `C-023`** cites `InventoryCountService.java:322-345` | — | Verified at **`:325-345`** | Refined in §1.5 row 4. `grep -c "StockLevel"` → **0** confirmed |
| **R7 §4.6 item 4** quotes R1 `C-032`'s *"~12 web routes"* | — | Computed: **21** top-level accessories routes, of which **10** are inventory, plus 11 report subpages | §1.2 gives both figures with the command. The difference is scoping, not error |

### 8.2 The unresolved conflict

**`M3`, the union valuation report.** R3 `M3`/`E-084` says build it; R7 §4.6 item 4 says do not, and
document the separation in the UI instead. `DECISIONS.md` does not settle it. §5 `M3` states both
positions, offers a reconciling shape (side-by-side columns, no grand total anywhere including the
export), and **flags that it needs an `OD-` row in `DECISIONS.md`** — that document owns the `OD-`
namespace, so this one does not allocate an id. Deadline: **before the `P2` reports task is written**.

### 8.3 `UNVERIFIED`, stated plainly

- **Every claim about `warehouse` behaviour is a claim about a design, not about code.** The module
  does not exist. Only §1, §2.1 rows 1–3, §3's evidence column and §7.1–7.2 are verified against a
  running codebase; §5, §6 and §7.3 describe things to be built.
- **`whb_external_stock_snapshots`, `whb_category_stocking_ownership`** and the two reports of `M1`/`M2`
  **do not appear in `DECISIONS.md`.** `D-9` mandates the *obligations*; these are this document's
  proposed shape for them and are subject to the phase task that adopts them.
- **No task id, `FR-nnn`, `WH-SC-nnn`, `I-n` SQL-invariant id or issue `#NN` is cited anywhere in
  this document**, because `warehouse-issues/issues/` is empty and `GAP-REGISTER.md`,
  `DATA-MODEL.md` and `SCENARIO-CATALOGUE.md` do not exist (`ls -R` on the repo: `docs/DECISIONS.md`,
  `docs/reviews/R1`–`R7`, and empty `docs/contracts/`, `issues/`, `tools/`). Every such citation
  would resolve to nothing — the accounting set's most expensive failure, where 25 dangling `FR-nnn`
  references included **19 that resolved to a different real requirement**, so live gaps read as
  closed. Phases (`P0`…`P6`) are cited instead, because `DECISIONS.md` §5 defines them.
- **`M7` is a hand-off to the `accessories` module's own backlog** and this design set has no
  authority over it. It is listed so the finding is not lost, not so it is claimed.
- **Whether accessories would consent to `M4`'s companion seed migration** in its own band is
  unknown. It is an edit to a live module and needs its owner's agreement; §5 `M4` says so.

### 8.4 Referred to the standards reviewer — not this document's business

One line each, no detail:

- `accessory_products.vehicle_compatibility JSONB` (`V30050:42`) against CLAUDE.md's DATABASE
  CONVENTIONS **NO JSONB** — pre-existing, in a live module, noted only so warehouse does not copy it.
- The `M1` and `M2` screens each need a `COMMON_FILTER_CONFIGS` scope, a `CacheConfiguration` cache
  name, `grid_column_definitions` + `filter_definitions` rows, both
  `grid_preferences.default_filters` **and** `default_columns` populated, `WarehouseSafeTranslation`
  entries in **all** locales, and a mobile counterpart (`D-13`).
- The `M1`/`M2` reports' statistics strips are filter-aware and must therefore **not** be given a
  `statistics.*` cache name (`C-043`).
- Warehouse frontend filenames must be globally unique — `Dockerfile.frontend:80-177` merges module
  `src/` trees last-write-wins (`C-012`).

---

*Established 2026-09-01. Every `grep`, `find`, `sed` and `ls` count in this document was run on that
date against `/Users/bbhushan/work/git/workspace/classic`, `.../accounting` and
`.../warehouse-issues`. Re-run before treating one as current — `DECISIONS.md` rule 1.*

*Companion document: [`IRREVERSIBLE.md`](IRREVERSIBLE.md) — `IRR-25` is the schema half of `M1`, and
`D-9`'s two obligations are the only entries on that list whose deadline is a **product** decision
rather than a migration.*
