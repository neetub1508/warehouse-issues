# Functional Contract — Removal of dealer and retail code, and the dual-use renames (P7)

> **What this is.** The functional truth for what must **not exist** in the four classic warehouse modules
> after `P7`, what is **renamed**, and what must **keep working**. Removal has no state machine: every rule
> here is an absence check (`RMV-UNR`), a rename check (`RMV-REN`) or a preservation check (`RMV-KEEP`) that
> the functional reviewer runs against the `P7` tree and the rebuilt dev database. It closes R30 `CP-FR-007`
> group 25, where the reviewer had nothing to run "must not exist" against.
>
> **Status.** Derived 2026-10-23 (v0) from [`frd/FRD-REM.md`](../frd/FRD-REM.md) `FR-480`…`FR-499`,
> `REM-D1`…`REM-D21`, `OD-22`…`OD-24`, §6 grep gates and Appendices A–F. Every pattern below was run
> against `classic` @ `74102d8d04` on 2026-10-23 and **matches today** (the artefact exists, so the check is
> not vacuous) — **in its runnable, unescaped form of §1.7**; the table cells escape `|` for markdown (R31 F-SR-009). Not ratified.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | none — a one-time clean rewrite (`RN-052`): delete, rewrite mixed files, rebuild the dev DB once. The checks run at the `P7` exit (`P7-13`); per-task subsets run in `P7-02`…`P7-11` |
| **Module** | `warehouse-base`, `warehouse`, `warehouse-3pl`, `warehouse-india`; plus exactly three platform registrations (`FRD-REM` §1 fence, `RN-054`) |
| **Domain baseline** | `D-16`, `RN-004`, `RN-010`…`RN-024`, `RN-040`…`RN-054`, `R29` F6/F7/F9/F13, `FRD-REM` §6 GATE-1…GATE-8 |
| **Owning tasks** | `issues/p7-01.md`…`issues/p7-13.md`; one owner per FR (`FRD-REM` §4 owner map) |
| **Scopes** | `$W` = `warehouse-base warehouse warehouse-3pl warehouse-india`; `$P` = `platform/frontend/src/utils/filterUtils.ts platform/backend/src/main/java/ai/platform/config/CacheConfiguration.java platform/backend/src/main/resources/db/client/logix shared/scripts/ci-gate`; every grep is `grep -rIE --exclude-dir={target,node_modules,.next,results}` from the classic root, **pass = no match**. `psql` = `docker compose exec -T postgres psql` with `shared/docker/.env` |
| **Exceptions** | exactly two, both one file (`REM-D19`): `WB/V500200__Allow_warehouse_in_platform_module_check_constraints.sql` (GATE-3) and `WarehouseBaseCouplingTest.java` (GATE-6). Any other allowlist is a defect |
| **Contract version** | `v0 — 2026-10-23` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Every removed feature is absent on every surface (`WH-SC-660`, `-661`, `-663`, `-675`) | `RMV-UNR-01`…`-12`, `RMV-UNR-26`; run as §1.7 |
| A2 | No dead vocabulary, adapter switch or public endpoint remains (`WH-SC-664`, `-674`) | `RMV-UNR-13`…`-21` |
| A3 | The three dual-use codes and Parts KPIs are renamed in storage and on screen (`WH-SC-664`, `-671`, `-672`) | `RMV-REN-01`…`-04` |
| A4 | Generic shipping, channels, the category picker and the menu re-home still work (`WH-SC-662`, `-666`…`-670`, `-673`) | `RMV-KEEP-01`…`-07` |
| A5 | The migration set is clean and the dev DB is rebuilt once (`WH-SC-676`…`-679`) | `RMV-UNR-22`, `RMV-UNR-23`, `RMV-KEEP-08` |

## 1. T1 — State machine

None. No status is added, removed or renamed by a transition; the removed workflows' own state machines
(NDR, COD, RTO, marketplace claim, obsolescence return) leave with their tables (`RMV-UNR-02`…`-09`).

### 1.4 Unreachable — must not exist after `P7`

Per-feature rows name every surface of one removed artefact class. The cross-cutting rows (`-13` onward)
are the whole-tree sweeps that catch a surface a feature row missed.

| ID | Must not exist | Absence check (pass = 0 rows / no match) | Owner | Source |
|---|---|---|---|---|
| RMV-UNR-01 | **AWB pools**: `wh_awb_pools`, `wh_awb_numbers`, the claim / void / top-up services, job `WH_AWB_POOL_TOP_UP`, alert `WAREHOUSE_AWB_POOL_LOW`, the `AWB_VOID` reason context (5 reasons, `V510205`), error `SHIPMENT_TRACKING_NOT_CLAIMED_AWB`, route `outbound/awb-pools`, permissions `wh_awb_pools:*` (7), grid `wh_awb_pools`, i18n `awbPool`, scope `WAREHOUSE_AWB_POOL`, descriptor `wh-awb-pools.json` | `grep -rIE 'WhAwb\|AwbPool\|wh_awb_\|AWB_VOID\|SHIPMENT_TRACKING_NOT_CLAIMED_AWB\|WAREHOUSE_AWB_POOL_LOW\|WH_AWB_POOL_TOP_UP\|outbound/awb-pools' $W $P`; dispatch / edit / cancel in `WhShipmentService` claim, mark or void no pool waybill | `P7-02` | FR-480 |
| RMV-UNR-02 | **Courier serviceability and rate quotes**: `wh_carrier_serviceability`, `wh_rate_quotes`, the rate shop, import kind `WH_CARRIER_SERVICEABILITY`, routes `outbound/serviceability` and `outbound/rate-quotes`, permissions `wh_carrier_serviceability:*` (6 incl. `:import`) and `wh_rate_quotes:*` (5), grids of the same names, i18n `carrierServiceability` and `rateQuote`, scopes `WAREHOUSE_CARRIER_SERVICEABILITY` / `WAREHOUSE_RATE_QUOTE`; `WhCarrierConnector.rate()` and `fetchAwbBlock()` with their records (`REM-D13`) | `grep -rIE 'CarrierServiceability\|RateQuote\|RateShop\|wh_carrier_serviceability\|wh_rate_quote\|CARRIER_SERVICEABILITY\|outbound/(serviceability\|rate-quotes)\|fetchAwbBlock' $W $P`; `WhCarrierConnector` declares `owningModule()` only | `P7-02` | FR-481 |
| RMV-UNR-03 | **NDR workflow**: `wh_shipment_ndrs`, `wh_ndr_actions`, jobs `WH_NDR_ESCALATION` and `WH_NDR_AUTO_RTO`, alert `WAREHOUSE_NDR_OVERDUE`, the NDR / RTO normalised carrier statuses `NDR`, `RTO_INITIATED`, `RTO_IN_TRANSIT`, `RTO_DELIVERED` (`V510203` CHECKs, `WhCarrierStatusMapping`, the `ndr` statistic tile, `REM-D4`), the carrier clock columns `ndr_response_hours`, `ndr_auto_rto_grace_hours` (`REM-D14`), route `outbound/ndr`, permissions `wh_shipment_ndrs:*` (6), grid, i18n `shipmentNdr` + `help.ndr`, scope `WAREHOUSE_NDR` | `grep -rIE 'ShipmentNdr\|WhNdr\|wh_shipment_ndrs\|wh_ndr_actions\|WH_NDR_\|WAREHOUSE_NDR\|RTO_INITIATED\|RTO_IN_TRANSIT\|RTO_DELIVERED\|ndr_response_hours\|ndr_auto_rto_grace_hours\|outbound/ndr' $W $P`; `\d wh_carriers` lists neither clock column (`WH-SC-665`) | `P7-03` | FR-482 |
| RMV-UNR-04 | **COD**: `wh_cod_remittances` + `_lines`, number series `COD`, job `WH_COD_UNREMITTED_AGEING`, port `WhCodAccountingSink`, the demand-order `payment_mode` / `cod_amount` columns and form fields, the `PAYMENT_MODE` wave criterion and its `V510100` CHECK value (`REM-D1`), carrier `cod_remittance_days` (`REM-D14`), `wh_carrier_services.supports_cod` with its grid / filter rows and stat tile (`OD-22` default), route `outbound/cod-remittances`, permissions `wh_cod_remittances:*` (7), grid, i18n `codRemittance` + `help.codRemittances`, scope `WAREHOUSE_COD_REMITTANCE` | `grep -rIE 'CodRemittance\|WhCod[A-Z]\|wh_cod_remittance\|cod_remittance_days\|supports_cod\|supportsCod\|DO_PAYMENT_MODE\|DO_COD_AMOUNT\|PAYMENT_(PREPAID\|COD)\b\|WhDemandOrder\.PAYMENT_MODES\|outbound/cod-remittances' $W $P`; `\d wh_demand_orders` has no `payment_mode` / `cod_amount`, `\d wh_carrier_services` no `supports_cod` (`WH-SC-665`); `SELECT 1 FROM whb_number_series WHERE series_code = 'COD'` = 0 | `P7-03` | FR-483 |
| RMV-UNR-05 | **Channel accounts, channel order imports, channel publish rules / logs / runs**: the six tables `wh_channel_accounts`, `wh_channel_account_warehouses`, `wh_channel_order_imports`, `wh_channel_publish_rules`, `wh_channel_publish_rule_stock_statuses`, `wh_channel_publish_logs`; event type `channel.inventory.published`; document type `CHANNEL_PUBLISH_RUN`; attribute key `CHANNEL_ORDER_ID` (`REM-D10`); `wh_demand_orders.channel_account_id` and `uk_wh_demand_orders_channel_external_ref`; the two `dropdown.whChannel*` cache names; routes `outbound/channel-accounts`, `outbound/channel-imports`, `outbound/publish-rules`; permissions `wh_channel_accounts:*` (6), `wh_channel_order_imports:*` (6), `wh_channel_publish_rules:*` (8); grids incl. `wh_channel_publish_logs`; i18n `channelAccount`, `channelOrderImport`, `publishRule` + their help keys | `grep -rIE 'ChannelAccount\|ChannelOrderImport\|ChannelPublish\|wh_channel_account\|wh_channel_order_import\|wh_channel_publish\|channel\.inventory\.published\|CHANNEL_INVENTORY_PUBLISHED\|CHANNEL_PUBLISH_RUN\|CHANNEL_ORDER_ID\|channel_account_id\|dropdown\.whChannel\|outbound/(channel-accounts\|channel-imports\|publish-rules)' $W $P` | `P7-04` | FR-484 |
| RMV-UNR-06 | **Customer tracking links, notifications and the public tracking page**: `wh_tracking_links`, `wh_tracking_notification_rules` (8 seeded rows), `wh_tracking_notifications`, any `/public/warehouse/**` mapping, the `(public)` route group (`layout.tsx`, `track/[token]/page.tsx`, `REM-D16`), any customer e-mail / WhatsApp on dispatch, out-for-delivery or delivery; route `outbound/tracking-links`; permissions `wh_tracking_links:*` (7); i18n `trackingLink` + `help.trackingLinks` | `grep -rIE 'TrackingLink\|TrackingNotification\|TrackingPublic\|wh_tracking_link\|wh_tracking_notification\|/public/warehouse\|outbound/tracking-links' $W $P`; `find warehouse/frontend/src/app -path '*(public)*'` prints nothing (GATE-7); `curl -i /api/public/warehouse/tracking/x` and `/track/x` → **404** (`WH-SC-674`) | `P7-03` | FR-485 |
| RMV-UNR-07 | **Marketplace claims**: `wh_marketplace_claims`, code list `MARKETPLACE_CLAIM_TYPE` (+4 values), settings `warehouse.marketplace_claims.window_days` / `.due_alert_lead_days`, job `WH_MARKETPLACE_CLAIM_WINDOW`, `WhClaimSettlementRequest`; route `inbound/marketplace-claims`; permissions `wh_marketplace_claims:*` (7); grid; i18n `marketplaceClaim` + `help.marketplaceClaims`; scope `WAREHOUSE_MARKETPLACE_CLAIM`. Posting or reversing a return receipt opens or cancels no claim | `grep -rIE 'MarketplaceClaim\|wh_marketplace_claim\|MARKETPLACE_CLAIM_TYPE\|warehouse\.marketplace_claims\|WH_MARKETPLACE_CLAIM_WINDOW\|WhClaimSettlementRequest\|inbound/marketplace-claims' $W $P` | `P7-05` | FR-486 |
| RMV-UNR-08 | **RTO consignments**: `wh_rto_consignments`, `WhRtoReceiptLinker`, movement types `RTO_RECEIPT` / `RTO_RECEIPT_REVERSAL`, the RTO-context reasons, return types `RTO` and `MARKETPLACE` (`REM-D11`), the `rtoBegun` refusal in `WhShipmentValidationService`; route `outbound/rto`; permissions `wh_rto_consignments:*` (5); grid; i18n `rtoConsignment` + `help.rto`; scope `WAREHOUSE_RTO` | `grep -rIE 'RtoConsignment\|RtoReceipt\|wh_rto_consignment\|RTO_RECEIPT\|rtoBegun\|outbound/rto\b' $W $P`; `RETURN_TYPE` has exactly 8 values (`WH-SC-664`, `-668`) | `P7-05`, `P7-10` | FR-487 |
| RMV-UNR-09 | **OEM obsolescence returns**: `wh_obsolescence_returns` + `_lines`, series `OBR`, jobs `WH_OBSOLESCENCE_WINDOW_WARNING` / `WH_OBSOLESCENCE_CANDIDATES`, settings `warehouse.obsolescence_returns.window_warning_lead_days` / `.no_movement_months`, supplier-claim type `OBSOLESCENCE` and source document `OBSOLESCENCE_RETURN` (the `V510216` ladder trigger checks neither); route `inbound/obsolescence-returns`; permissions `wh_obsolescence_returns:*` (8); grid; i18n `obsolescenceReturn` + `help.obsolescenceReturns`; scope `WAREHOUSE_OBSOLESCENCE_RETURN` | `grep -rIE 'ObsolescenceReturn\|ObsolescenceCandidate\|ObsolescenceWindow\|wh_obsolescence_return\|OBSOLESCENCE_RETURN\|TYPE_OBSOLESCENCE\|warehouse\.obsolescence_returns\|inbound/obsolescence-returns' $W $P`; the supplier-claim type picker offers 4 types (`WH-SC-670`). The **`OBSOLESCENCE` stock-KPI metric stays** (GATE-3 never matches the bare word) | `P7-07` | FR-490 |
| RMV-UNR-10 | **Trade portal**: `wh_trade_portal_users`; role `Warehouse Trade Customer` with its grants and menu permissions; L1 `warehouse_trade` and L2 `warehouse_trade_customers` (`REM-D21`: the key is retired, never reused); the customer persona in `WhbOwnerScopeResolver` (`permittedCustomers`, `requireCustomerPermitted`, `CustomerScope`); port `WhbTradeCustomerGrantProvider`; every `*ForCustomer` / `toCustomerResponses` / `createTradePortalDraft` path; route `outbound/trade-portal`; permissions `wh_trade_portal:*` (2), `wh_trade_portal_users:*` (5); i18n `tradePortal` + `help.tradePortal`; scope `WAREHOUSE_TRADE_PORTAL_USER` | `grep -rIE 'TradePortal\|TradeCustomer\|CustomerPersona\|wh_trade_portal\|permittedCustomers\|requireCustomerPermitted\|CustomerScope\|ForCustomer\b\|toCustomerResponses\|createTradePortalDraft\|outbound/trade-portal\|WAREHOUSE_TRADE_PORTAL_USER\|tradePortal\|CUSTOMER_PATH\|exportCustomerDemandOrders\|downloadCustomerDocument\|isCustomerUnscoped\|customerUnscopedAuthorities\|customerGrantProviders\|CUSTOMER_NOT_PERMITTED\|PERSONA_PARAMETERS\|warehouse_trade\b' $W $P`; `SELECT 1 FROM roles WHERE name = 'Warehouse Trade Customer'` = 0 (`WH-SC-661`); `SELECT 1 FROM menus WHERE name IN ('warehouse_trade','warehouse_trade_customers')` = 0 at the `P7` exit (`WH-SC-662`) | `P7-08` | FR-491 |
| RMV-UNR-11 | **Accessories coexistence**: `whb_category_stocking_ownership`, `whb_external_stock_snapshots`, `WhbStockingSystemResolver`, the Coexistence report (`WS-225`), `WhInventorySeparationNotice`, `whb_item_categories.is_dual_eligible` (column, index, comment, India seed inserts, grid / filter rows, `filterUtils.ts` boolean, `REM-D7`); routes `masters/category-ownership`, `platform/external-snapshots`, `reports/coexistence`; permissions `whb_category_stocking_ownership:*`, `whb_external_stock_snapshots:*`, `wh_rpt_coexistence:*` (4); i18n `coexistence`, `inventorySeparation`, `help.coexistence`, `warehouseBase.json` `categoryStockingOwnership`, `externalStockSnapshot`, `help.categoryOwnership`, `help.externalSnapshots`; QA doc `warehouse-base/docs/QA/Category Stocking Ownership.md` | `grep -rIE 'Coexistence\|CategoryStockingOwnership\|ExternalStockSnapshot\|StockingSystem\|InventorySeparation\|whb_category_stocking_ownership\|whb_external_stock_snapshot\|wh_rpt_coexistence\|is_dual_eligible\|isDualEligible\|masters/category-ownership\|platform/external-snapshots\|reports/coexistence' $W $P`; `\d whb_item_categories` has no `is_dual_eligible` (`WH-SC-665`, `-677`) | `P7-09` | FR-492 |
| RMV-UNR-12 | **Consolidated Valuation** (`WS-222`, `V511262`, 8 Java + 4 FE files + 3 i18n sections, `REM-D6`): route `reports/consolidated-valuation`, permissions `wh_rpt_consolidated_valuation:*` (4), grid, scope `WAREHOUSE_RPT_CONSOLIDATED_VALUATION`, i18n `consolidatedValuation` + `help.consolidatedValuation` | `grep -rIE 'ConsolidatedValuation\|wh_rpt_consolidated_valuation\|reports/consolidated-valuation' $W $P`; `ls warehouse/backend/src/main/resources/db/migration/V511262__*` finds nothing | `P7-09` | FR-492 |
| RMV-UNR-13 | **Dead adapter switches**: the base enable expression naming `adapter.dealer` / `adapter.services` (it is `base or warehouse or adapter.example or 3pl or india`); source systems `ADAPTER_DEALER`, `ADAPTER_SERVICES`, `ADAPTER_FIELD_SERVICE`, `ADAPTER_ASSETS`, `ACCESSORIES` (`V501117` deleted whole, `REM-D3`); their i18n labels; the "Parts Counter 60 / Workshop Parts 70" menu-slot comment; the 7 dead `filterUtils.ts` scopes `WAREHOUSE_DEALER_*` / `WAREHOUSE_SERVICES_*` (`R29` F9); `ReservedAccessoriesRule` | GATE-6 `grep -rIE 'adapter\.dealer\|adapter\.services\|warehouse-adapter-(dealer\|services)\|warehouseadapter(dealer\|services)\|Parts Counter\|Workshop Parts\|WAREHOUSE_(DEALER\|SERVICES)_\|whad_\|whas_' $W platform/frontend/src/utils/filterUtils.ts --exclude=WarehouseBaseCouplingTest.java`; GATE-3 arm `ADAPTER_(DEALER\|SERVICES\|FIELD_SERVICE\|ASSETS)\|'ACCESSORIES'\|"ACCESSORIES"` with `--exclude=V500200__Allow_warehouse_in_platform_module_check_constraints.sql` | `P7-10` | FR-493, REM-D19 |
| RMV-UNR-14 | **Dealer / retail seeded vocabulary**: document types `JOB_CARD`, `POS_SHIFT`, `CHANNEL_PUBLISH_RUN`; identifier type `MARKETPLACE_LISTING`; return types `RTO`, `MARKETPLACE`; channel kinds `MARKETPLACE`, `OWN_STORE`, `POS`; the 23 RTO / NDR / `AWB_VOID` reasons and `CARRIER_INITIATED` (`V500004`, `V510205`, `V510206`, `V511276`); movement types `RTO_RECEIPT`, `RTO_RECEIPT_REVERSAL`. Every seed migration's own count / verification assertion matches the trimmed set | GATE-3 vocabulary arm `JOB_CARD\|POS_SHIFT\|MARKETPLACE_LISTING\|CHANNEL_PUBLISH_RUN\|RTO_RECEIPT\|NDR_[A-Z_]+\|CARRIER_INITIATED\|AWB_VOID\|OWN_STORE`; GATE-4 `'(RTO\|NDR\|COD\|POS\|MARKETPLACE\|OBR)'` and the double-quoted form; `psql` over `whb_document_types`, `whb_code_list_values`, `whb_reason_codes`, `whb_movement_types` for the `FRD-REM` D.5 codes = 0 (`WH-SC-664`) | `P7-10` | FR-494 |
| RMV-UNR-15 | **Removed tables** — the 24 of `FRD-REM` D.1 | `SELECT to_regclass('<t>')` is NULL for each (`WH-SC-660`); GATE-2 over `$W $P` | `P7-13` | FR-498 |
| RMV-UNR-16 | **Removed permissions and the role** — the 103 rows of D.2, their role grants (ADMIN, AUDITOR, ADMIN_GROUP, the Warehouse Storekeeper / Supervisor / Stock Controller / Manager / Finance Controller bundles, Branch Admin) and their `permission_dependencies`; role `Warehouse Trade Customer`. The deleted names are never re-used (`FRD-REM` §7) | `SELECT count(*) FROM permissions WHERE name ~ '^(wh_(awb_pools\|shipment_ndrs\|cod_remittances\|channel_accounts\|channel_order_imports\|channel_publish_rules\|tracking_links\|marketplace_claims\|rto_consignments\|carrier_serviceability\|rate_quotes\|obsolescence_returns\|trade_portal\|trade_portal_users\|rpt_coexistence\|rpt_consolidated_valuation\|rpt_parts_kpis)\|whb_(category_stocking_ownership\|external_stock_snapshots)):'` = **0** (`WH-SC-661`) | `P7-13` | FR-480, FR-481, FR-482, FR-483, FR-484, FR-485, FR-486, FR-487, FR-490, FR-491, FR-492, FR-497 |
| RMV-UNR-17 | **Removed menus** — the 17 leaves of D.3 (`outbound/{rto,channel-accounts,channel-imports,publish-rules,tracking-links,rate-quotes,serviceability,awb-pools,ndr,cod-remittances,trade-portal}`, `inbound/{obsolescence-returns,marketplace-claims}`, `reports/{coexistence,consolidated-valuation}`, `masters/category-ownership`, `platform/external-snapshots`) and the containers L1 `warehouse_channels`, L2 `warehouse_channels_fulfilment`, L2 `warehouse_channels_carriers`, L1 `warehouse_trade`, L2 `warehouse_trade_customers`; with them every `menu_permissions`, role-menu, favourite and visit-history row naming them (`REM-D21`); freed slots 60 / 67 / 70 are not re-used (67 was the trade L1 `warehouse_trade`, `V511209` deleted by `P7-08`) | §1.7 `RMV-UNR-17` (the literal 17 `route_path` values) = 0 on every install; the container names = 0 at the `P7` exit, except `warehouse_channels` exactly once **at L3** (`RMV-KEEP-03`, `WH-SC-662`); GATE-5 | `P7-06`, `P7-08` | FR-488, FR-491 |
| RMV-UNR-18 | **Removed grids** — the 18 of D.4 (293 `grid_column_definitions` + 87 `filter_definitions` rows); the `isDualEligible` column / filter on item categories and `supportsCod` on carrier services | `SELECT 1 FROM grid_preferences / grid_column_definitions / filter_definitions WHERE grid_identifier IN (<the 18>)` = 0 each (`WH-SC-663`) | `P7-13` | FR-497, FR-492, FR-483 |
| RMV-UNR-19 | **Removed catalogue rows** — D.5: the source systems, document types, `MARKETPLACE_CLAIM_TYPE`, the `RETURN_TYPE` / `CHANNEL_KIND` / `IDENTIFIER_TYPE` values, `CHANNEL_ORDER_ID`, the RTO movement types, the 23 reasons, `channel.inventory.published`, series `COD` / `OBR`, the four `admin_settings` keys, the 8 `wh_tracking_notification_rules` rows | `psql` per D.5 list = 0; `CHANNEL_KIND` = `{B2B}`; `RETURN_TYPE` count = 8 (`WH-SC-664`); logix client seeds create no `COD` / `OBR` series (`WH-SC-678`) | `P7-13` | FR-494, FR-484, FR-486, FR-490 |
| RMV-UNR-20 | **Removed i18n sections** — every section of `FRD-REM` Appendix E, in **en, fr and hi**, in the same task that removes its code (`REM-D8` waives the no-delete rule for warehouse only) | GATE-8: `jq -e 'has("awbPool") or has("shipmentNdr") or has("codRemittance") or has("channelAccount") or has("channelOrderImport") or has("publishRule") or has("trackingLink") or has("marketplaceClaim") or has("rtoConsignment") or has("carrierServiceability") or has("rateQuote") or has("obsolescenceReturn") or has("tradePortal") or has("coexistence") or has("inventorySeparation") or has("consolidatedValuation") or has("partsKpis")'` on each `warehouse/frontend/src/i18n/locales/{en,fr,hi}/warehouse.json` → `false`; `has("categoryStockingOwnership") or has("externalStockSnapshot")` on each `warehouseBase.json` → `false`; the `help.*` keys of Appendix E likewise | each `P7-02`…`P7-11` for its own sections | REM-D8, FR-499 |
| RMV-UNR-21 | **Removed filter scopes and cache names** — the 17 feature scopes of Appendix E in `filterUtils.ts`, the 7 dead adapter scopes (`RMV-UNR-13`), the `isDualEligible` boolean and `supportsCod`; the two warehouse cache names `dropdown.whChannel*` in `CacheConfiguration.java` | `grep -nE 'WAREHOUSE_(CATEGORY_STOCKING_OWNERSHIP\|EXTERNAL_STOCK_SNAPSHOT\|RPT_COEXISTENCE\|TRADE_PORTAL_USER\|RATE_QUOTE\|CARRIER_SERVICEABILITY\|AWB_POOL\|CHANNEL_ACCOUNT\|CHANNEL_ORDER_IMPORT\|CHANNEL_PUBLISH_RULE\|TRACKING_LINK\|RTO\|NDR\|COD_REMITTANCE\|OBSOLESCENCE_RETURN\|MARKETPLACE_CLAIM\|RPT_CONSOLIDATED_VALUATION\|RPT_PARTS_KPI)\b' platform/frontend/src/utils/filterUtils.ts` = 0; `grep -n 'dropdown.whChannel' platform/backend/src/main/java/ai/platform/config/CacheConfiguration.java` = 0 | `P7-02`…`P7-11` | FR-484, FR-493, FR-497 |
| RMV-UNR-22 | **A migration that names a removed object, a drop migration, or a guard for a removed object** — no file in the four modules or the logix seed creates, alters, inserts into, selects from, casts to or names a removed object; no `DROP` for one, no `to_regclass` guard added for one, no feature flag, no renumbered file (deleted versions leave gaps) | GATE-1…GATE-8 over `$W $P` all pass (`WH-SC-675`); fresh install on an empty volume with all four modules, and with `warehouse-3pl` / `warehouse-india` each disabled, boots with no Flyway failure (`WH-SC-660`, `-677`) | `P7-13` | FR-498 |
| RMV-UNR-23 | **A history row for a deleted version, or a repaired checksum** in the rebuilt dev DB; a volume dropped without the user's explicit go when warehouse rows exist (`REM-D18`) | `SELECT version FROM flyway_schema_history WHERE version IN (<Appendix B.1 versions>)` = 0 and `WHERE type = 'DELETE' OR description LIKE '%repair%'` = 0; one history row per present file with matching checksum (`WH-SC-679`); `P7-13` records the pre-rebuild warehouse-row count and, if non-zero, the go | `P7-13` | FR-499, REM-D18 |
| RMV-UNR-24 | **A grep-gate exception beyond the two of `REM-D19`** — any other excluded file, path or silent allowlist in GATE-1…GATE-8, or a gate that passes only by editing a fenced module | the gate commands in `P7-13` carry exactly `--exclude=V500200__Allow_warehouse_in_platform_module_check_constraints.sql` (GATE-3) and `--exclude=WarehouseBaseCouplingTest.java` (GATE-6); a legitimate kept use is recorded in `FRD-REM` §2 before merge | `P7-13` | REM-D19, FR-499 |
| RMV-UNR-25 | **Docs, QA notes, contracts and descriptors in `classic` describing a removed feature as present** (Appendix F); `ci-gate` naming a deleted test class | `warehouse/docs/contracts/shipment-carrier-lifecycle.contract.md` has no AWB-pool / NDR / RTO guard or transition; `order-flow-retry.contract.md` no trade-portal row; the `.claude/testing/descriptors` of Appendix F deleted / trimmed / renamed; `shared/scripts/ci-gate/20-warehouse.def` names no deleted test class (`WH-SC-676`) | `P7-12` | FR-499 |
| RMV-UNR-26 | **Any file of `FRD-REM` Appendix A** (478 paths) — by exact path, so a deletion target whose content matches no semantic pattern (e.g. `WhTrackingEventRequest.java`, `FRD-REM.md:263`) cannot survive the proof (R31 F-SR-010) | §1.7 `RMV-UNR-26`: the generated list has 478 lines and no `STILL PRESENT` line prints | `P7-13` | FR-498 |

### 1.5 Renames — stored code and every surface (`REM-D5`)

| ID | Old → new | Check (old absent **and** new present) | Owner | Source |
|---|---|---|---|---|
| RMV-REN-01 | **`VOR` → `LINE_STOP`** (label *Line stop / machine down*) in `chk_wh_purchase_orders_order_source`, Java constants, en / fr / hi | GATE-4 `'VOR'` / `"VOR"` = 0 over `$W $P`; PO saved with order source *Line stop / machine down* stores `LINE_STOP`; `WhSupplierLeadTimeQueryService` excludes it from lead-time history as it did `VOR`; inserting `'VOR'` fails the CHECK (`WH-SC-672`) | `P7-11` | FR-496 |
| RMV-REN-02 | **`WORKSHOP` → `PRODUCTION_STORE`** (*Production store / shop floor*) as a `WAREHOUSE_TYPE` value | GATE-4 `'WORKSHOP'` / `"WORKSHOP"` = 0 over `$W $P` (`$P` takes the logix seed only, so dealer client folders' `WORKSHOP` department codes are outside the gate); `WAREHOUSE_TYPE` has `PRODUCTION_STORE`, not `WORKSHOP` (`WH-SC-664`) | `P7-11` | FR-496 |
| RMV-REN-03 | **`OEM_PART_NUMBER` → `MANUFACTURER_PART_NUMBER`** (*Manufacturer part no.*) as an `IDENTIFIER_TYPE` value; registry-openness tests carry the new code | GATE-3 arm `OEM_PART_NUMBER` = 0; `IDENTIFIER_TYPE` has `MANUFACTURER_PART_NUMBER` (`WH-SC-664`). Supersessions, `ISSUE_TO_ASSET` / `FITMENT`, kits and gate events unchanged | `P7-11` | FR-496 |
| RMV-REN-04 | **Parts KPIs → Stock KPIs**: classes `WhStockKpi*` (package `whstockkpi`), endpoint `/warehouse/reports/stock-kpis`, permission resource and grid `wh_rpt_stock_kpis`, menu `warehouse_stock_kpis` → `/dashboard/warehouse/reports/stock-kpis`, export `warehouse-stock-kpis-*.xlsx`, i18n `stockKpis` + `help.stockKpis`, help page `warehouse-reports-stock-kpis`, scope `WAREHOUSE_RPT_STOCK_KPI`, ci-gate spec `WhStockKpiFillRateDenominatorTest` (today `WhPartsKpiFillRateDenominatorTest`, `20-warehouse.def:64`). The four metric codes and their frozen definitions are unchanged | GATE-1 arm `PartsKpi\|partsKpi` and GATE-2 `wh_rpt_parts_kpis` = 0; GATE-8 `partsKpis` false; `wh_rpt_stock_kpis` has 9 columns and 7 filters (`WH-SC-663`); a user without `wh_rpt_stock_kpis:view` gets 403; metric values equal the denominator test's expectations (`WH-SC-671`) | `P7-11` | FR-497 |

### 1.6 Kept — must still work after `P7`

| ID | Must still hold | Check | Owner | Source |
|---|---|---|---|---|
| RMV-KEEP-01 | **Generic shipping** keeps its tables, screens, permissions and tests: carriers, carrier services, carrier accounts **with scopes** (`wh_carrier_account_scopes`, `wh_carrier_accounts:view:all` / `:view:branch`), shipping labels, manifests, handovers, pickup requests, consignments, carrier status mappings, tracking events, shipments, demand orders, RMAs, return receipts, return gradings. Behaviour changes are only those of `RMV-UNR-01`…`-08`, each listed in the task that makes it | dispatch with tracking `1234567890` then a mapped `DELIVERED`: shipment `DISPATCHED` → `DELIVERED`, demand order `SHIPPED` → `DELIVERED`, event and mapping stored, no AWB / NDR / link / notification row; `WhDespatchServiceTest` (`WH-SC-056`) and `WhShipmentConfirmedDispatchIntegrationTest` pass unchanged before and after (`WH-SC-666`) | `P7-02` | FR-489, FR-480, FR-482, FR-485 |
| RMV-KEEP-02 | **Carrier delete guards count only kept documents** (`WhCarrierRepositoryCustomImpl`, `WhCarrierAccountRepositoryCustomImpl`, `WhCarrierServiceLevelRepositoryCustomImpl`) | a carrier with one shipping label is refused **409 `CARRIER_IN_USE`** with count 1; one with no documents deletes; the guard SQL names no removed table (`WH-SC-667`) | `P7-02` | FR-481, FR-489 |
| RMV-KEEP-03 | **`whb_channels` stays with the `B2B` kind only**; `channel_id` with its FK stays on `whb_stock_movements`, `whb_item_identifiers`, `wh_demand_orders` (`fk_wh_demand_orders_channel`), `wh_fulfilment_policies`; the Channels master leaf `warehouse_channels` (L3, `V500051`) stays | `CHANNEL_KIND` = `{B2B}`; `\d wh_demand_orders` shows `channel_id` + `fk_wh_demand_orders_channel` (`WH-SC-665`); `warehouse_channels` exists once, at L3 (`WH-SC-662`) | `P7-10` | FR-495 |
| RMV-KEEP-04 | **Menu re-home**: Cross-dock Plans, Working Calendars, Tracking Events and Carrier Status Mappings sit under L1 `warehouse_shipping` (*Shipping*, sort 66) → one L2 `warehouse_shipping_planning` (*Carrier Tracking & Planning*), each with its name key, `route_path` and `required_permission_prefix` unchanged; no L2 exceeds 8 leaves, no L1 exceeds 10 L2s; every menu-count assertion in a rewritten migration matches (`REM-D15`) | `warehouse_shipping_planning` has exactly 4 children with their old routes and prefixes (`WH-SC-662`) | `P7-06` | FR-488 |
| RMV-KEEP-05 | **Return receipts post and reverse with the same stock movements as before**; a carrier `DELIVERED` is never refused because an RTO had begun; return types `REFUSED_DELIVERY`, `CANCELLED_IN_TRANSIT`, `EXCHANGE` stay (`REM-D11`, `OD-23`) | reversal of a posted `CUSTOMER` return receipt mirrors the original, touches no claim or RTO row; the return-type picker offers exactly the 8 kept types (`WH-SC-668`) | `P7-05` | FR-487, FR-486 |
| RMV-KEEP-06 | **The stocking-category picker still works from its relocated home** (`REM-D9`): `getStockingCategoryOptions` / `findStockingCategoryOptions` on the item-category query service and repository; `WhbAllocationStrategyService`, `WhbGlPostingRuleService`, `WhbValuationPolicyService` inject no `*StockingOwnership*` class; item, company, location and counterparty external refs stay | each modal's category tree loads (`WH-SC-673`); `grep -rn 'StockingOwnership' warehouse-base/backend/src/main` = 0 | `P7-01`, `P7-09` | FR-492 |
| RMV-KEEP-07 | **Supplier claims keep four claim types and the relocated value helper** (`WhObsolescenceReturnValidationService.lineValue` → `WhSupplierClaimValidationService`, `REM-D9`); the demand-order create fingerprint is a SHA-256 over the remaining canonical fields, byte-identical helper inlined into `WhDemandOrderValidationService`; a body still carrying `paymentMode` / `codAmount` is **ignored**, not refused (`JacksonConfig.java:73`) | claim line value = qty × unit cost HALF_UP to money scale (`WH-SC-670`); an identical replay with `Idempotency-Key K1` returns the first order, fingerprint equal with and without the two fields (`WH-SC-669`) | `P7-01`, `P7-04`, `P7-07` | FR-490, FR-483 |
| RMV-KEEP-08 | **CI stays green and the reserved-band ratchet stays** (`WarehouseBaseCouplingTest`, `REM-D3`) | `shared/scripts/ci-gate.sh ratchets warehouse` and `integration warehouse` exit 0 (`WH-SC-676`) | `P7-13` | FR-499, FR-493 |
| RMV-KEEP-09 | **Drop-ship stays in core as B2B direct ship** (`REM-D20`): `WhDropShipService`, `WhDropShipController`, `WhDropShipGuard` and the wiring in `WhGoodsReceiptPostingService` / `WhDemandOrderService`; `INSTALL.md` keeps them gated off as v2 | no `P7` task deletes them; `ls warehouse/backend/src/main/java/ai/warehouse/service/WhDropShipService.java` exists after `P7` | — | FR-489 |
| RMV-KEEP-10 | **The kept shipping terms**: `wh_carrier_accounts.payment_mode` (`CREDIT` / `PREPAID` / `TO_PAY`) and the shipping uses of "AWB" / "waybill" as the carrier's tracking-number word (`REM-D12`) | `WhCarrierAccount.PAYMENT_MODE_*` present; GATE-3 is anchored to the demand-order and wave tokens, so it never matches them | `P7-03`, `P7-04` | FR-483, FR-480 |

### 1.7 Runnable form of the checks (R31 F-SR-009, F-SR-010)

Inside the §1.4 table a `\|` is **markdown escaping** for a pipe, not grep syntax: in ERE (GNU grep, ugrep) and in PostgreSQL `~`, `\|` is a *literal* pipe, so a cell copied as written matches nothing and passes vacuously. **Run the checks from this block, never from a table cell.** Each line below is the cell's command with the escaping removed; `RMV-UNR-14` uses `FRD-REM` §6 GATE-3 / GATE-4 as written there (unescaped); `RMV-UNR-17` is expanded to the literal route list. Run from the classic root with `$W` / `$P` as in §0.

```bash
W="warehouse-base warehouse warehouse-3pl warehouse-india"
P="platform/frontend/src/utils/filterUtils.ts platform/backend/src/main/java/ai/platform/config/CacheConfiguration.java platform/backend/src/main/resources/db/client/logix shared/scripts/ci-gate"
X="--exclude-dir=target --exclude-dir=node_modules --exclude-dir=.next --exclude-dir=results"
# RMV-UNR-01
grep -rIE $X 'WhAwb|AwbPool|wh_awb_|AWB_VOID|SHIPMENT_TRACKING_NOT_CLAIMED_AWB|WAREHOUSE_AWB_POOL_LOW|WH_AWB_POOL_TOP_UP|outbound/awb-pools' $W $P
# RMV-UNR-02
grep -rIE $X 'CarrierServiceability|RateQuote|RateShop|wh_carrier_serviceability|wh_rate_quote|CARRIER_SERVICEABILITY|outbound/(serviceability|rate-quotes)|fetchAwbBlock' $W $P
# RMV-UNR-03
grep -rIE $X 'ShipmentNdr|WhNdr|wh_shipment_ndrs|wh_ndr_actions|WH_NDR_|WAREHOUSE_NDR|RTO_INITIATED|RTO_IN_TRANSIT|RTO_DELIVERED|ndr_response_hours|ndr_auto_rto_grace_hours|outbound/ndr' $W $P
# RMV-UNR-04
grep -rIE $X 'CodRemittance|WhCod[A-Z]|wh_cod_remittance|cod_remittance_days|supports_cod|supportsCod|DO_PAYMENT_MODE|DO_COD_AMOUNT|PAYMENT_(PREPAID|COD)\b|WhDemandOrder\.PAYMENT_MODES|outbound/cod-remittances' $W $P
# RMV-UNR-05
grep -rIE $X 'ChannelAccount|ChannelOrderImport|ChannelPublish|wh_channel_account|wh_channel_order_import|wh_channel_publish|channel\.inventory\.published|CHANNEL_INVENTORY_PUBLISHED|CHANNEL_PUBLISH_RUN|CHANNEL_ORDER_ID|channel_account_id|dropdown\.whChannel|outbound/(channel-accounts|channel-imports|publish-rules)' $W $P
# RMV-UNR-06
grep -rIE $X 'TrackingLink|TrackingNotification|TrackingPublic|wh_tracking_link|wh_tracking_notification|/public/warehouse|outbound/tracking-links' $W $P
# RMV-UNR-07
grep -rIE $X 'MarketplaceClaim|wh_marketplace_claim|MARKETPLACE_CLAIM_TYPE|warehouse\.marketplace_claims|WH_MARKETPLACE_CLAIM_WINDOW|WhClaimSettlementRequest|inbound/marketplace-claims' $W $P
# RMV-UNR-08
grep -rIE $X 'RtoConsignment|RtoReceipt|wh_rto_consignment|RTO_RECEIPT|rtoBegun|outbound/rto\b' $W $P
# RMV-UNR-09
grep -rIE $X 'ObsolescenceReturn|ObsolescenceCandidate|ObsolescenceWindow|wh_obsolescence_return|OBSOLESCENCE_RETURN|TYPE_OBSOLESCENCE|warehouse\.obsolescence_returns|inbound/obsolescence-returns' $W $P
# RMV-UNR-10
grep -rIE $X 'TradePortal|TradeCustomer|CustomerPersona|wh_trade_portal|permittedCustomers|requireCustomerPermitted|CustomerScope|ForCustomer\b|toCustomerResponses|createTradePortalDraft|outbound/trade-portal|WAREHOUSE_TRADE_PORTAL_USER|tradePortal|CUSTOMER_PATH|exportCustomerDemandOrders|downloadCustomerDocument|isCustomerUnscoped|customerUnscopedAuthorities|customerGrantProviders|CUSTOMER_NOT_PERMITTED|PERSONA_PARAMETERS|warehouse_trade\b' $W $P
# RMV-UNR-11
grep -rIE $X 'Coexistence|CategoryStockingOwnership|ExternalStockSnapshot|StockingSystem|InventorySeparation|whb_category_stocking_ownership|whb_external_stock_snapshot|wh_rpt_coexistence|is_dual_eligible|isDualEligible|masters/category-ownership|platform/external-snapshots|reports/coexistence' $W $P
# RMV-UNR-12
grep -rIE $X 'ConsolidatedValuation|wh_rpt_consolidated_valuation|reports/consolidated-valuation' $W $P
# RMV-UNR-13
grep -rIE $X 'adapter\.dealer|adapter\.services|warehouse-adapter-(dealer|services)|warehouseadapter(dealer|services)|Parts Counter|Workshop Parts|WAREHOUSE_(DEALER|SERVICES)_|whad_|whas_' $W platform/frontend/src/utils/filterUtils.ts --exclude=WarehouseBaseCouplingTest.java
# RMV-UNR-21
grep -nE 'WAREHOUSE_(CATEGORY_STOCKING_OWNERSHIP|EXTERNAL_STOCK_SNAPSHOT|RPT_COEXISTENCE|TRADE_PORTAL_USER|RATE_QUOTE|CARRIER_SERVICEABILITY|AWB_POOL|CHANNEL_ACCOUNT|CHANNEL_ORDER_IMPORT|CHANNEL_PUBLISH_RULE|TRACKING_LINK|RTO|NDR|COD_REMITTANCE|OBSOLESCENCE_RETURN|MARKETPLACE_CLAIM|RPT_CONSOLIDATED_VALUATION|RPT_PARTS_KPI)\b' platform/frontend/src/utils/filterUtils.ts
# RMV-UNR-21
grep -n 'dropdown.whChannel' platform/backend/src/main/java/ai/platform/config/CacheConfiguration.java
```

```sql
-- RMV-UNR-16 (expect 0)
SELECT count(*) FROM permissions WHERE name ~ '^(wh_(awb_pools|shipment_ndrs|cod_remittances|channel_accounts|channel_order_imports|channel_publish_rules|tracking_links|marketplace_claims|rto_consignments|carrier_serviceability|rate_quotes|obsolescence_returns|trade_portal|trade_portal_users|rpt_coexistence|rpt_consolidated_valuation|rpt_parts_kpis)|whb_(category_stocking_ownership|external_stock_snapshots)):';
-- RMV-UNR-17 (expect 0): the 17 leaves of FRD-REM D.3, literal
SELECT count(*) FROM menus WHERE route_path IN (
  '/dashboard/warehouse/outbound/rto',
  '/dashboard/warehouse/outbound/channel-accounts',
  '/dashboard/warehouse/outbound/channel-imports',
  '/dashboard/warehouse/outbound/publish-rules',
  '/dashboard/warehouse/outbound/tracking-links',
  '/dashboard/warehouse/outbound/rate-quotes',
  '/dashboard/warehouse/outbound/serviceability',
  '/dashboard/warehouse/outbound/awb-pools',
  '/dashboard/warehouse/outbound/ndr',
  '/dashboard/warehouse/outbound/cod-remittances',
  '/dashboard/warehouse/outbound/trade-portal',
  '/dashboard/warehouse/inbound/obsolescence-returns',
  '/dashboard/warehouse/inbound/marketplace-claims',
  '/dashboard/warehouse/reports/coexistence',
  '/dashboard/warehouse/reports/consolidated-valuation',
  '/dashboard/warehouse/masters/category-ownership',
  '/dashboard/warehouse/platform/external-snapshots');
-- RMV-UNR-17 containers (expect 1: warehouse_channels at menu_level 3 only, RMV-KEEP-03)
SELECT name, menu_level FROM menus WHERE name IN ('warehouse_channels','warehouse_channels_fulfilment','warehouse_channels_carriers','warehouse_trade','warehouse_trade_customers');
```

```bash
# RMV-UNR-26 (expect no output): every Appendix A path is gone - exact paths, generated from FRD-REM
awk '/^## Appendix A/{p=1;next} /^## Appendix B/{p=0} p && /^- `[^`]*\/` — /{d=$2; gsub(/`/,"",d); n=split($0,a,"`"); for(i=4;i<=n;i+=2) print d a[i]}' \
  ../warehouse-issues/docs/frd/FRD-REM.md > /tmp/rem-appendix-a.txt
test "$(wc -l < /tmp/rem-appendix-a.txt)" -eq 478 || echo 'APPENDIX A PARSE: expected 478 paths'
while read -r f; do [ -e "$f" ] && echo "STILL PRESENT: $f"; done < /tmp/rem-appendix-a.txt
```

**Anti-vacuous step (required before the exit run).** Run every command of this block against the **pre-`P7` tree** (`classic` @ `74102d8d04`, or the `P7` branch point) and the pre-rebuild DB, and require a **match** from each: ≥ 1 file for every grep, a non-zero count for `RMV-UNR-16` / `-17`, all 478 paths present for `RMV-UNR-26`. A check that finds nothing before `P7` proves nothing after it and is fixed before the exit run. Re-run on 2026-10-23 with the escaping removed, every grep above matched (`RMV-UNR-01` 62 files … `RMV-UNR-13` 17, `RMV-UNR-21` 19 lines) and all 478 Appendix A paths exist.

## 2. T2 — Action × role × state

No action is added. The permission absences are `RMV-UNR-16`; the one rename is `RMV-REN-04`. A
`P7` tree in which any removed permission name is re-seeded for a new feature fails `RMV-UNR-16`.

## 3. T3 — Time-driven rules

None remain from the removed features. The jobs `WH_AWB_POOL_TOP_UP`, `WH_NDR_ESCALATION`,
`WH_NDR_AUTO_RTO`, `WH_COD_UNREMITTED_AGEING`, `WH_MARKETPLACE_CLAIM_WINDOW`,
`WH_OBSOLESCENCE_WINDOW_WARNING` and `WH_OBSOLESCENCE_CANDIDATES` are Java descriptors with no SQL row and
leave with their classes (`RMV-UNR-01`, `-03`, `-04`, `-07`, `-09`).

## 4. T4 — Cross-entity effects

The removals cut effects out; `RMV-KEEP-01` and `RMV-KEEP-05` state the ones that remain unchanged.

## 5. T5 — Screen contract

No screen is added. Removed routes: `RMV-UNR-17`; renamed route: `RMV-REN-04`; re-homed leaves:
`RMV-KEEP-04`; public pages: `RMV-UNR-06`.

## 6. Out of scope

No `warehouse-retail` / `warehouse-dealer` sibling; no drop migration, `to_regclass` guard, flag or
deprecation period; no data migration; no renumbering; no change to `dealer`, `automotive`, `accessories`,
`insurance`, `services`, `assets`, accounting adapters, mobile, or platform beyond the three fenced files;
no new feature (`FRD-REM` §7). `CLAUDE.md`'s stale `WarehouseAdapterDealerSafeTranslation.tsx` line is
reported to the user, not edited.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived from `FRD-REM` §4–§6 and Appendices A–F (R30 `CP-FR-007` group 25); every check pattern run against `classic` @ `74102d8d04` and found matching today |
| 2026-10-23 | R31 (`R31-functional-review-stores-rem.md`): §1.7 runnable unescaped checks, literal `RMV-UNR-17` route list and the anti-vacuous pre-`P7` step (F-SR-009); `RMV-UNR-26` exact-path absence of Appendix A (F-SR-010); `RMV-OPEN-01`…`-04` resolved (`R31-decisions`, `D-18` item 4) |
| 2026-10-24 | `P7-13` (G6, the gate-widening TODO from `P7` S1): `RMV-UNR-02` takes bare `CARRIER_SERVICEABILITY` in place of `WH_CARRIER_SERVICEABILITY` (a superset, also catching `WAREHOUSE_CARRIER_SERVICEABILITY` and the import kind) and `RMV-UNR-05` adds `CHANNEL_INVENTORY_PUBLISHED`, in both §1.4 (escaped) and §1.7 (unescaped); `FRD-REM` GATE-3 adds `CHANNEL_INVENTORY_PUBLISHED`. The new arms match the pre-`P7` tree (`e9ba5b74a6`) and nothing at `classic` HEAD |

## 8. Invariants and scenarios

`L-1` (`WH-SC-666`), `L-3` (`WH-SC-668`), `I-18` (`WH-SC-664`); scenarios `WH-SC-660`…`WH-SC-679`.

## 9. Open rows

| ID | Question | Default |
|---|---|---|
| RMV-OPEN-01 | `OD-22`: does `wh_carrier_services.supports_cod` stay? | drop it (`RMV-UNR-04`); reversing re-adds one boolean **RESOLVED (DEFAULT), 2026-10-23** (`R31-decisions`). |
| RMV-OPEN-02 | `OD-23`: which `RETURN_TYPE` values does a manufacturer keep? | keep `REFUSED_DELIVERY`, `CANCELLED_IN_TRANSIT`, `EXCHANGE`; drop `RTO`, `MARKETPLACE` — 8 values (`RMV-UNR-08`, `RMV-KEEP-05`) **RESOLVED (DEFAULT), 2026-10-23** (`R31-decisions`). |
| RMV-OPEN-03 | `OD-24`: what meters 3PL freight once rate quotes are gone? | `P7-02` rewrites the `Wh3plFreightBillingService` comment to "no metering source; see OD-24" and changes no behaviour **RESOLVED — user decision `D-18` item 4, 2026-10-23:** 3PL freight is **quoted from the 3PL's own tariff at despatch and trued up when the carrier invoice arrives** (`FR-295` kept; the difference is an adjusting billable event, `TPB-OPEN-03`). `P7-02`'s comment-only change stays as interim cleanup and now cites `D-18`. |
| RMV-OPEN-04 | `REM-D4`: which existing carrier exception status does a B2B failed delivery map to once `NDR` is gone? `FRD-REM` defers the list to `V510203` while writing `P7-03` | `P7-03` names it in its acceptance; until then `RMV-UNR-03` checks only the absence **RESOLVED (default replaced), 2026-10-23** (`R31-decisions`): a B2B failed delivery maps to `EXCEPTION`, keeping the raw carrier status (`V510203:79-82`); `P7-03` states it in its acceptance. |
