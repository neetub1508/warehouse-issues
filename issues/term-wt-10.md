TITLE: [Warehouse] [Finding] Terminology WT-10 · Rename planned screens that collide with built names
LABELS: task,warehouse,gap-terminology,phase-p9,warehouse-trade
issue: 805
---
Part of #547 · Module **`warehouse-trade`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **PLANNED-WRONG** · Related: #584, #582, #589, #598 · Source: terminology review 2026-11-03, lane WT

## Why this task exists

Planned screens repeat names that are already built.
- **Purchase Orders.** With trade installed, the menu shows two leaves called "Purchase Orders": core Inbound (`wh_purchase_orders`) and trade WS-292 (`wht_purchase_orders`, linked by `core_po_id`).
- **Receipt Reversals.** MFG WS-327 "Receipt Reversals" sits next to core Inbound "Receipt Reversals".
- **Vendor vs Supplier.** Trade mixes "Vendor Quotations" and "Vendor Evaluations" with "Supplier Trade Profiles", against a built UI that says Supplier (WT-04).

Users will open the wrong screen.

## Scope

Design-set label changes only (FRD screen names, menu display names in the planned seeds). Routes and keys stay as planned.
- WS-327 becomes "Production Receipt Reversals".
- WS-289 becomes "Supplier Quotations", and WS-297 becomes "Supplier Evaluations". "Approved Vendor List (AVL)" keeps its industry name.
- The P9-07 trade migration relabels the core Inbound leaf, display only (name key, route and permission prefix unchanged), to "PO Receipt Tracking" when trade is installed. Without trade it stays "Purchase Orders".

## Acceptance

- With all modules installed, no two warehouse menu leaves share an en label.
- FRD-TRADE and FRD-MFG screen tables use the new names, and the planned menu seeds match.
- An install without trade still shows the core leaf as "Purchase Orders".

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

- **Trade screens:** `warehouse-issues/docs/frd/FRD-TRADE.md:400` (WS-289 Vendor Quotations), :403 (WS-292 Purchase Orders), :408 (WS-297 Vendor Evaluations); `issues/p9-07.md:13` (`core_po_id` → `wh_purchase_orders`).
- **MFG screen:** `docs/frd/FRD-MFG.md:520` (WS-327 Receipt Reversals).
- **Built screens:** core menus `V511010:58` (Purchase Orders) and Inbound "Receipt Reversals".
- **Real-world source:** one term per concept (https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N2318089.html).
