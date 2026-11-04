TITLE: [Warehouse] [Finding] Terminology WT-09 · Make customer item references reuse the base customer part number
LABELS: task,warehouse,gap-terminology,phase-p9,warehouse-trade
issue: 804
---
Part of #547 · Module **`warehouse-trade`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **PLANNED-WRONG** · Related: #579, #654 · Source: terminology review 2026-11-03, lane WT

## Why this task exists

P9-02 plans `wht_customer_item_refs` (customer × item → customer part number, drawing and revision, approval). But base already stores the customer part number as a `CUSTOMER_PART_NUMBER` identifier scoped to the customer, and that is the row the scanner and labels read (and, after WT-06, documents and search too). With two stores, sales would print one number while the warehouse scans and labels another. P9-02 only forbids `whb_item_external_refs`. It does not mention identifiers.

## Scope

Design change to P9-02 and FR-545.
- `wht_customer_item_refs` keeps the drawing revision, customer approval status and validity.
- It holds a FK to the `whb_item_identifiers` row (type CUSTOMER_PART_NUMBER, same item and customer) instead of its own part-number column. Creating a ref with a new number creates the identifier through the base service.
- The uk becomes (company, customer, item, drawing_revision), as now, with the part number read through the FK.

No base change.

## Acceptance

- P9-02 and FR-545 no longer define a free-text customer part number column.
- Creating a customer item ref with part number X leaves exactly one CUSTOMER_PART_NUMBER identifier X for that item and customer.
- A sales quotation line and a delivery challan for that customer show the same part number.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

- **P9-02 plan:** `warehouse-issues/issues/p9-02.md:23` (`wht_customer_item_refs`) and :142 (forbids external refs only); FRD-TRADE FR-545.
- **Base store:** `B/resources/db/migration/V500016__…:219-220` (`counterparty_id` "Set for a supplier or customer part number") and `V500010:196`.
- **Real-world source:** one customer-material info record per customer and item (https://docs.frappe.io/erpnext/user/manual/en/item).

## Depends on

#579
