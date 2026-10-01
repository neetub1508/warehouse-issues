# Warehouse-only market-readiness audit

**Date:** 1 October 2026. **Conclusion:** substantial warehouse execution implementation exists, but general production readiness is not yet demonstrated. Fix the stock-history and operational defects, restore reliable release gates, and complete database, operator-flow and recovery acceptance before declaring the affected configuration ready.

This pack contains **71 findings and decisions**, not 71 confirmed software bugs. It separates code-supported defects, reported carry-forward work, missing verification, documentation drift and intentional limits. Priority totals: **2 P0, 43 P1, 24 P2, 2 P3**. Priorities are audit recommendations and apply only to each finding’s stated scope.

## Start here

- [Detailed gap register: W01–W71](01-Warehouse-Only-Gap-Register.md) — evidence, impact, next action and acceptance for every item.
- [Execution-flow acceptance matrix](02-Execution-Flow-Acceptance.md).
- [All GitHub issues and disposition](03-Issue-Disposition.md).
- [Fresh tests, runtime observations and audit limits](04-Verification-Evidence.md).
- [411 scenario reference rows](05-Scenario-Traceability.md).

## Scope

Warehouse-base, warehouse, warehouse-3pl, warehouse-india and shared platform dependencies affecting them. Forecasting, planning, inventory optimization and planning AutoPilot are excluded. Operational pick-face replenishment remains included. Accounting, India, 3PL, carriers and regulated profiles are conditional release gates, not requirements for every customer.

Native mobile/RF/offline operation was deliberately excluded by the adopted September 11 decision. Removed dealer/services adapters and withdrawn verticals are not reinstated. GS1 and other deferred advanced features must remain explicit package limits.

## Highest-value work first

1. **Stock and value trust:** correct the 365-day Stock As-At window (W01), prove costing producer/approval lineage (W07–W09), and demonstrate isolated warehouse recovery (W33/W54).
2. **Basic operator flow:** resolve optional-zone putaway (W02), blank UOM (W03), setup holes (W04–W06), RMA expiry (W12) and attachment deletion protection (W13).
3. **Reliable release evidence:** fix the real frontend health failure (W39), repair and rerun the failing frontend gate (W60–W62), execute excluded database tests (W34), and complete warehouse-only acceptance (W35/W50).
4. **Operational package:** prove install/upgrade, onboarding, device/browser use, permissions, alerts and performance at the intended customer size (W38–W55).
5. **Conditional features:** close carrier/3PL/India carry-forward work (W63–W70) before selling those workflows. Keep unsupported capabilities disabled or clearly excluded.

## What is already meaningful

The codebase includes a ledger, reservation/allocation, receiving, QC, putaway, picking, packing, shipping, returns, transfers, counts, costing, background jobs, outbox/error handling and optional 3PL/India features. The fresh backend gate reports **5,449 tests, zero failures/errors and two skips**. That supports a substantial implementation; it does not prove complete user journeys or database concurrency.

Fresh warehouse frontend gate: **3,568 tests, 54 failures, 3,514 passes** across eight suites. Several failures are demonstrated scanner/parser false positives. They still leave the release gate red and require repair plus triage of remaining assertions.

## Corrections to older gap lists

- Emergency short-pick replenishment is implemented through tasks; the older missing BIN_TO_BIN claim is stale (W15).
- The migration-header defect in #183 is restored and the current backend gate passes; it is not a current defect here.
- Outbox lag monitoring and restore helpers exist. The gap is operational proof and complete warehouse recovery, not total absence of these mechanisms.
- Historical closed-issue reviews contain defects subsequently fixed. Carry-forward entries in this pack are explicitly reported until current-source/runtime closure is established.

## Market context without planning

Small/midmarket readiness still requires coherent execution: receipt, location control, barcode identity, counts, traceability, package/shipment lifecycle and trustworthy reporting. Odoo documents location-based cycle counts and barcode counting; Zoho documents serial/batch tracking, barcode transactions and package-to-delivery stages. These references set useful acceptance expectations, not proof that our implementation is weaker or stronger.

Sources checked October 1: [Odoo cycle counts](https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/inventory/warehouses_storage/inventory_management/cycle_counts.html), [Zoho barcode generation](https://www.zoho.com/us/inventory/help/items/qrcode-generation.html), [Zoho packages](https://www.zoho.com/us/inventory/help/sales-orders/packages.html). No numerical market-readiness score or competitor-internal architecture claim is made.

## Audit boundary

This is an evidence-backed baseline of known and newly identified risks, not a guarantee that no undiscovered defect exists. Source inventories, design/contract review, all issue bodies/comment collections, focused code traces and isolated gates were used. We did not manually inspect every source line or execute every scenario/browser/hardware/provider workflow. The acceptance matrix makes that remaining proof explicit.

**No product code, production data or GitHub issues were changed.**
