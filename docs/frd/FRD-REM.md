# FRD-REM — removing dealer and retail code from the warehouse, and the dual-use renames

**Area** REM · **Phase** `P7` (runs first: every later phase builds on the cleaned schema) · **Date** 2026-10-22
**Derives from** `D-16` · [`R28`](../reviews/R28-manufacturing-storage-retarget-impact.md) §8b `RN-050`…`RN-054` (authoritative), §1 `RN-004`, §2 `RN-010`…`RN-018`, §3 `RN-020`…`RN-024`, §9 `RN-040`…`RN-047`
**Ids owned** `FR-480`–`FR-499` · `WH-SC-660`–`WH-SC-679` · `OD-22`–`OD-24` · tasks `issues/p7-NN.md` · EPIC `issues/09-EPIC-p7.md`
**Code evidence** `classic/` @ `65b41be8a6`, read-only, verified by four inventory passes on 2026-10-22. R28's counts were only the starting point. **Where this file and R28 differ, this file has the measured value** (see §1.2).

---

## 1. Purpose and scope

The warehouse is re-targeted at **manufacturing and storage** (`D-16`). This FRD specifies, **at capability level and testably**, what leaves
the four classic warehouse modules (`warehouse-base`, `warehouse`, `warehouse-3pl`, `warehouse-india`), what is renamed, and
what must keep working. The `P7` tasks implement it. The appendices are the full inventory a builder works from.

**Method (`RN-052`).** This is a clean rewrite, not a migration. Removed features' migration files are **deleted**. Mixed files are **rewritten**
so they neither create nor reference a removed object. The dev database is **dropped and rebuilt once**. There are **no drop
migrations, no `to_regclass` guards added for removed objects, no compatibility shims, no feature flags left behind**. For
warehouse only, this supersedes the standing "never edit an applied migration", "never delete an applied migration" and
"never wipe the dev DB" rules, and (user decision recorded with `RN-052`) the "never delete i18n" rule.

**Fence (`RN-054`).** The `dealer`, `automotive`, `accessories`, `insurance`, `services` and `assets` modules are not edited.
Three platform files must change, because they hold warehouse-only registrations:
- `platform/frontend/src/utils/filterUtils.ts`: 17 warehouse feature filter scopes plus the 7 dead dealer/services adapter scopes (`R29` F9), the `isDualEligible` boolean, and the Parts-KPI scope rename
- `platform/backend/src/main/java/ai/platform/config/CacheConfiguration.java:781,783`: two warehouse cache names
- `platform/backend/src/main/resources/db/client/logix/*`: the warehouse demo seed

No mobile work: warehouse has no mobile screens. A grep of `mobile/src` finds only `accessoryWarehouse*`, which belongs to accessories.

### 1.1 Personas

| Persona | What changes for them |
|---|---|
| **Installer / administrator** | A fresh install has no retail or dealer tables, menus, permissions, roles, settings or jobs. The Channels L1 menu is gone. Its generic leaves (Cross-dock Plans, Working Calendars, Tracking Events, Carrier Status Mappings) are under **Shipping → Carrier Tracking & Planning** |
| **Storekeeper / despatch clerk** | Shipments, labels, manifests, handovers, pickups, consignments, tracking events, return receipts, RMAs and gradings behave as before. They no longer see any AWB pool, NDR, COD, RTO or tracking-link control. The demand-order form loses Payment mode and COD amount. Purchase orders offer **Line stop / machine down** instead of `VOR` |
| **Planner / analyst** | The **Stock KPIs** report replaces Parts KPIs. Its metrics and definitions are unchanged. Coexistence and Consolidated Valuation are gone. Stock Valuation is the valuation report |
| **Developer / reviewer** | Grep gates (§6) and DB probes (§5) prove absence. `ci-gate.sh ratchets warehouse` is green |

### 1.2 Measured against R28

| R28 said | Measured (2026-10-22) |
|---|---|
| ~215 main Java, ~30 test (`RN-047`) | **retail 215 main + 28 test = 243**, all in `warehouse`. **Dealer 83 main + 12 test = 95**, including consolidated valuation and the base persona port. **Total 338 Java files deleted** |
| ~95 frontend files | **140** frontend files deleted (34,628 lines) |
| 11 i18n sections | **1,757 leaf keys** in each of en, fr and hi (5,271 in all), plus about 32 vocabulary keys in each language inside kept sections |
| ~48 permission-constant lines | 16 blocks in `warehousePermissions.ts`, 2 in `warehouseBasePermissions.ts`, and 15 help entries (~620 lines) in `warehouseHelp.ts` plus 2 in `warehouseBaseHelp.ts` |
| 12 retail-only migrations + 13 mixed (`RN-046`) | **20 whole-file deletes**, plus **34 mixed files** (plus comment-only touches) and **4 logix client seeds** to rewrite (Appendix B) |
| `WhDespatchService:214` reads `paymentMode` (`RN-043`) | **Wrong.** `:214` passes `channelId` to the shelf-life floor. The only reader of `paymentMode` is `WhCarrierShipmentFactsReader`, and only removed classes consume it |
| `whb_channels` keep, B2B only | Confirmed. FKs from `whb_stock_movements` (`V500059:81`), `whb_item_identifiers`, `wh_demand_orders` and `wh_fulfilment_policies` |
| Consolidated valuation not listed | It reads `whb_external_stock_snapshots` (accessories side), so it is **D3 scope** and is removed |
| `V500054` coexistence | **Refuted.** It only creates the generic `whb_activity_history` view. It stays |

---

## 2. Decisions (REM)

Applied as defaults. The user confirms them at the final review. Each one closes a question an inventory pass raised.

| # | Decision | Why |
|---|---|---|
| **REM-D1** | **Drop `wh_demand_orders.payment_mode`, `cod_amount` and `channel_account_id`.** Also drop their CHECKs, the partial unique index `uk_wh_demand_orders_channel_external_ref`, the `PAYMENT_MODE` wave criterion and its value in the `V510100` CHECK, and the `paymentMode` derivation in `WhCarrierShipmentFactsReader` | No kept reader except the wave criterion (`WhWaveCriteria:51`). `channel_account_id` is written only by the channel-order import writer. COD is a retail payment mode |
| **REM-D2** | **Keep `whb_channels` and every `channel_id` column. Keep only the `B2B` `CHANNEL_KIND` value** (delete `MARKETPLACE`, `OWN_STORE`, `POS`) | The append-only ledger references it (`V500059:81`). Fulfilment policies (`WhDemandOrderService:411`), the channel-level shelf-life floor (`WhDespatchService:214`) and channel-scoped identifiers use it. A manufacturer still sells through distributor, OEM and export channels |
| **REM-D3** | **Remove all unbuilt adapter source systems**: `ADAPTER_DEALER`, `ADAPTER_SERVICES`, `ADAPTER_FIELD_SERVICE`, `ADAPTER_ASSETS` and `ACCESSORIES`. Delete `V501117` whole. A future adapter seeds its own row under `RL-003` | No adapter exists. A reserved row for a module that is not coming is an unstated absence. The reserved-band ratchet in `WarehouseBaseCouplingTest:1567-1570,2124-2126,2362-2437` **stays**, because it guards bands, not rows |
| **REM-D4** | **Remove the NDR and RTO carrier normalised statuses** (`NDR`, `RTO_INITIATED`, `RTO_IN_TRANSIT`, `RTO_DELIVERED`): the `V510203` CHECKs, `WhCarrierStatusMapping:57-60,70`, the tracking-events `ndr` statistic tile, and the i18n. **Remove the NDR and RTO reason codes** | They only feed the removed NDR/RTO workflows. A B2B carrier's failed delivery maps to an existing exception status (verify the list in `V510203` while writing `P7-03`) |
| **REM-D5** | **Renames change the STORED code, not only the label**: `VOR`→`LINE_STOP`, `WORKSHOP`→`PRODUCTION_STORE`, `OEM_PART_NUMBER`→`MANUFACTURER_PART_NUMBER`, `PartsKpi`→`StockKpi` (classes, endpoint, permission resource, grid id, menu, route, export filename, i18n section, help page id, filter scope) | Clean rewrite plus DB rebuild means no stored row carries the old code. In-place edits of the seeding files cost nothing, and leave no dealer word in a code that ledger and document rows will store for ever. Label-only would have been preferred **only** if rows already existed; none do (§1.2, `inv-migrations` §7: no running DB holds the warehouse band) |
| **REM-D6** | **Delete Consolidated Valuation** (`WS-222`, `V511262`, 8 Java, 4 FE files + 3 i18n sections) and the trade-customer persona port **`WhbTradeCustomerGrantProvider`** (its only implementation is the trade-portal adapter) | Consolidated valuation is accessories coexistence (an external snapshot union). Its warehouse half duplicates `WS-211` Stock Valuation |
| **REM-D7** | **Drop `whb_item_categories.is_dual_eligible`**: the column, index and comment (`V500014:80,114,124,134`), the seed inserts in `warehouse-india V540130:252,261`, its grid and filter rows, 11 Java files, 6 FE files plus i18n, and `filterUtils.ts:1014-1021` | It is the D-9 coexistence flag. Nothing else reads it |
| **REM-D8** | **The i18n no-delete rule is waived** for this removal (`RN-052`). Every removed feature's keys are deleted in en, fr and hi in the same task that removes its code | A key for a deleted screen is dead text that a future screen could collide with |
| **REM-D9** | **The generic category picker moves before coexistence is deleted.** `getStockingCategoryOptions` and `findStockingCategoryOptions` move to the item-category query service and repository. `WhClaimTransitionData` moves to `types/whSupplierClaim.ts`. The money helper `WhObsolescenceReturnValidationService.lineValue` moves into `WhSupplierClaimValidationService`. The SHA-256 fingerprint helper is inlined into `WhDemandOrderValidationService`, byte-identical | Each is generic behaviour that a kept class reaches through a removed one. Moving it first (`P7-01`) keeps every later task a pure delete |
| **REM-D10** | **Remove the `CHANNEL_ORDER_ID` attribute key** (`V500010:438`, guard `:522`). `WhbStockLedgerWriterIntegrationTest:123` switches to another seeded text key | It exists only for channel order imports |
| **REM-D11** | **Keep** the return types `REFUSED_DELIVERY`, `CANCELLED_IN_TRANSIT` and `EXCHANGE`. **Delete** `RTO` and `MARKETPLACE` (`RETURN_TYPE` goes from 10 to 8) | A B2B customer refuses deliveries and swaps goods. RTO and marketplace returns are e-commerce. `OD-23` asks the user to confirm |
| **REM-D12** | **Keep** `wh_carrier_accounts.payment_mode` (`CREDIT`/`PREPAID`/`TO_PAY`) and the kept-shipping uses of the words "AWB" and "waybill" | The account column is a carrier billing term, not COD. "AWB" is the carrier's tracking-number word |
| **REM-D13** | **Trim `WhCarrierConnector`** to `owningModule()`. Delete `rate()`, `fetchAwbBlock()` and their records. Keep `WhCarrierConnectorRegistry` as the API | The rate shop and AWB top-up were the only callers. No implementation exists anywhere |
| **REM-D14** | **Drop the carrier clock fields** `ndr_response_hours`, `ndr_auto_rto_grace_hours` and `cod_remittance_days`. They disappear because the files that create them (`V510206`, `V510207`) are deleted. Remove them from 5 Java files, the carrier modal's "NDR & COD" tab, and logix `V910031:24-34` | Only NDR and COD read them |
| **REM-D15** | **Menu re-home (R9).** Delete the L1 `warehouse_channels` and its L2s `warehouse_channels_fulfilment` and `warehouse_channels_carriers`. Four generic leaves survive: **Cross-dock Plans**, **Working Calendars**, **Tracking Events** and **Carrier Status Mappings**. `V511271` is rewritten so that its L1 is **`warehouse_shipping`** ("Shipping", same sort 66), with **one** L2 **`warehouse_shipping_planning`** ("Carrier Tracking & Planning") holding all four leaves. `V511272` and `V511273` file their kept leaves under that L2. Every moved leaf keeps its name key, `route_path` and `required_permission_prefix` (the `V511248` re-parent rule) | The caps are ≤ 8 L3 per L2 and ≤ 10 L2 per L1. Every candidate section is full: Outbound has 8 (`V511248` + `V511250` waves), Packing & VAS has 8 (`V511265`), Returns has 3 free slots for 4 leaves, and Warehouse Operations already has 10 L2s. A one-L2 L1 is the only placement that fits the caps without moving unrelated leaves |
| **REM-D16** | **Delete the per-module `(public)` route group** (`warehouse/frontend/src/app/(public)/layout.tsx`, `track/[token]/page.tsx`). The platform `SecurityConstants.PUBLIC_PATTERN "/public/**"` stays, because other modules share it | After the removal, warehouse has no unauthenticated endpoint |
| **REM-D17** | Historical artefacts stay untouched: `.claude/tasks/reports/warehouse-p5-*` (49 files), `.claude/.reviewer/codex/*`, `ci-gate/results/**` (untracked). The batch drivers `BATCH-WAREHOUSE-*.md` get a superseded note only | They are evidence of past runs, not instructions |
| **REM-D18** | **"Rebuild once" is measured, not assumed.** `P7-13` first counts warehouse rows in `flyway_schema_history`. Where the count is 0 (the git dev stack on 2026-10-22), enabling the modules applies the clean set and no volume is dropped. Where it is non-zero, the volume is dropped and rebuilt, **after the user's explicit go**. Fresh-install proofs run on a disposable side stack | Dropping a volume destroys platform data too. That cost is worth paying only where warehouse state actually exists. Flyway repair is never a substitute, because it leaves removed DDL in place |
| **REM-D19** | **Two named grep-gate exceptions, and nothing else** (`R29` F6). (1) `WB/V500200__Allow_warehouse_in_platform_module_check_constraints.sql:75` keeps `'ACCESSORIES'`: it is the **platform module list** behind a global-settings CHECK, naming the accessories *module*, not the removed source system; GATE-3 excludes this one file. (2) `WarehouseBaseCouplingTest.java` keeps the reserved-band ratchet (`REM-D3`), whose fixtures name `warehouse-adapter-dealer`/`-services` bands and `whad_` tables; GATE-6 already excludes this one file, and its `ACCESSORIES` fixtures leave with `ReservedAccessoriesRule` in `P7-10`. The kept carrier-account `payment_mode` (`REM-D12`) needs **no** exception: GATE-3 is anchored to the demand-order and wave tokens instead of the bare word | A gate that cannot pass without editing a fenced or generic file is a broken gate, not a licence for a silent allowlist. Each exception is one file, named here with its reason |
| **REM-D20** | **Drop-ship stays in core, as B2B direct ship** (R30 `CP-GA-009`). `WhDropShipService`, `WhDropShipController`, `WhDropShipGuard` and the drop-ship wiring in `WhGoodsReceiptPostingService` / `WhDemandOrderService` (`OD-18`: demand line + GRN ceiling linked) are generic: a supplier ships straight to a manufacturer's customer. No `P7` task removes them; `INSTALL.md` keeps them gated off as v2. A trade sales order that needs direct ship uses this seam (`P9-09` decides whether it does). Default, for the user's confirmation at the final review |
| **REM-D21** | **The L1 menu name `warehouse_trade` is retired with the Trade Portal and never reused** (R30 `CP-SC-002`). Re-using it would bring back favourites, visit history and role grants stored against the old key and would fail `WH-SC-662`. `P7-08` deletes the L1/L2 rows and, in the same migration, every `menu_permissions`, role-menu, favourite and visit-history row that names them; a later module chooses a new key (`warehouse-trade` → e.g. `warehouse_purchase_sales`, owned by `P9-01` / `FRD-TRADE` `TRD-07`) |

## 3. Open decisions (OD)

| # | Decision | Deadline | Safe default written into `P7` |
|---|---|---|---|
| **OD-22** | **Does `wh_carrier_services.supports_cod` stay?** It is a carrier service-level capability (`V510044:112`, grid `:358`/`:393`, filter `:360`/`:431`, carrier-services page). After COD remittances and demand-order COD go, nothing reads it | before `P7-03` | **Drop it** in `P7-03`: column, grid/filter rows, Java, FE, i18n. Reversing that means re-adding one boolean **RESOLVED (DEFAULT), 2026-10-23** (`R31-decisions` `RMV-OPEN-01`). |
| **OD-23** | **Which `RETURN_TYPE` values does a manufacturer keep?** `REM-D11` keeps `REFUSED_DELIVERY`, `CANCELLED_IN_TRANSIT` and `EXCHANGE` and drops `RTO` and `MARKETPLACE` | before `P7-05` | Keep three, drop two. Assertions: `V500010:810-813` and `V510050:944-947` expect **8** **RESOLVED (DEFAULT), 2026-10-23** (`R31-decisions` `RMV-OPEN-02`). |
| **OD-24** | **What meters 3PL freight once rate quotes are gone?** `Wh3plFreightBillingService:40` documents `meter()` as pricing the QUOTED cost from a `wh_rate_quotes` row. `meter()` has no main caller today, so nothing breaks. The 3PL freight design, though, loses its source. Owner: `warehouse-3pl` | before any 3PL freight-billing build | `P7-02` rewrites the comment to "no metering source; see OD-24" and changes no behaviour. `warehouse-3pl/docs/contracts/billing-cycle.contract.md:124` gets the same note **RESOLVED — user decision `D-18` item 4, 2026-10-23:** freight is quoted from the 3PL's own tariff at despatch and trued up when the carrier invoice arrives (`FR-295` kept); the `P7-02` comment cites `D-18` (`RMV-OPEN-03`). |

## 4. Requirements

Module codes as in `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §2. **Ver/Ph:** `v1`·`P7`. "Absent" means **every** surface: no table, column,
constraint, trigger or function; no Java class or bean; no endpoint; no page or route; no menu row; no permission, role or role grant;
no grid, filter or grid-preference row; no admin setting; no job or schedule; no number series; no code-list, reason, movement-type,
document-type, event-type or source-system row; no i18n key; no permission constant; no help entry; no `filterUtils` scope.

| # | Requirement | Module | Ver | Ph | Closes |
|---|---|---|---|---|---|
| **FR-480** | **AWB pools are absent.** That covers `wh_awb_pools`, `wh_awb_numbers`, the claim/void/top-up services, the `AWB_VOID` reason context, the top-up job and the `WAREHOUSE_AWB_POOL_LOW` alert. A shipment's tracking number is whatever the clerk keys or the label returns. Dispatch, edit and cancel no longer claim, mark used or void a pool waybill (`WhShipmentService:282-287,343-345,376,493-499`; `SHIPMENT_TRACKING_NOT_CLAIMED_AWB` deleted) | app | v1 | P7 | `RN-010` `RN-050` |
| **FR-481** | **Courier serviceability and rate quotes are absent** (`wh_carrier_serviceability`, `wh_rate_quotes`, the rate shop, the `WH_CARRIER_SERVICEABILITY` import kind). **Carrier account scopes stay** (`wh_carrier_account_scopes`, `wh_carrier_accounts:view:all`/`:view:branch`). The carrier, account and service-level delete guards count only kept documents (`WhCarrierRepositoryCustomImpl:212`, `WhCarrierAccountRepositoryCustomImpl:202-213`, `WhCarrierServiceLevelRepositoryCustomImpl:187-199`). `WhCarrierConnector` is trimmed (`REM-D13`) | app | v1 | P7 | `RN-017` `RN-042` |
| **FR-482** | **The NDR workflow is absent** (`wh_shipment_ndrs`, `wh_ndr_actions`, the escalation and auto-RTO jobs, the `WAREHOUSE_NDR_OVERDUE` alert). The NDR/RTO normalised carrier statuses are gone (`REM-D4`). The carrier clock fields go too (`REM-D14`). Ingesting a tracking event still stores the event, applies the status mapping, and delivers the shipment on a mapped `DELIVERED` (`WhTrackingEventIngestService:189-191`). It raises and closes nothing else | app | v1 | P7 | `RN-011` `RN-041` |
| **FR-483** | **COD is absent.** That covers `wh_cod_remittances` and `_lines`, the `COD` number series, the ageing job, the `WhCodAccountingSink` port, the demand-order `payment_mode`/`cod_amount` columns and form fields, the `PAYMENT_MODE` wave criterion (`REM-D1`) and, per `OD-22`, `supports_cod`. The demand-order create fingerprint is computed over the remaining fields only | app | v1 | P7 | `RN-012` `RN-043` |
| **FR-484** | **Channel accounts, channel order imports and channel publish rules, logs and runs are absent.** That covers 6 tables, the `channel.inventory.published` event type, the `CHANNEL_PUBLISH_RUN` document type, the `CHANNEL_ORDER_ID` attribute key (`REM-D10`), `wh_demand_orders.channel_account_id` with its unique index, and the two `dropdown.whChannel*` cache names. A demand order is created only by the warehouse's own screens and ports | app · platform | v1 | P7 | `RN-013` |
| **FR-485** | **Customer tracking links, tracking notifications and the public tracking page are absent.** The warehouse exposes **no unauthenticated endpoint**: no `/public/warehouse/**` mapping, no `(public)` route group, and no customer e-mail or WhatsApp is sent on dispatch, out-for-delivery or delivery | app | v1 | P7 | `RN-014` `REM-D16` |
| **FR-486** | **Marketplace claims are absent**: `wh_marketplace_claims`, the `MARKETPLACE_CLAIM_TYPE` code list and its 4 values, the two `warehouse.marketplace_claims.*` settings, the claim-window job, and `WhClaimSettlementRequest`. Posting or reversing a return receipt opens or cancels no claim | app | v1 | P7 | `RN-015` |
| **FR-487** | **RTO consignments are absent**: `wh_rto_consignments`, `WhRtoReceiptLinker`, the `RTO_RECEIPT`/`RTO_RECEIPT_REVERSAL` movement types, the RTO-context reasons, and the `RTO` and `MARKETPLACE` return types (`REM-D11`). A carrier `DELIVERED` event is never refused because an RTO had begun (`WhShipmentValidationService:251-270` loses `rtoBegun`). Return receipts post and reverse with **the same stock movements as before** | app · base | v1 | P7 | `RN-016` `RN-041` |
| **FR-488** | **The Channels L1 menu is absent** (`warehouse_channels`, `warehouse_channels_fulfilment`, `warehouse_channels_carriers`). Cross-dock Plans, Working Calendars, Tracking Events and Carrier Status Mappings stay reachable under L1 `warehouse_shipping` → L2 `warehouse_shipping_planning` (`REM-D15`), each with its name key, route and permission prefix unchanged. No L2 exceeds 8 leaves and no L1 exceeds 10 L2s. Every menu-count assertion in a rewritten migration matches the new tree | app | v1 | P7 | `RN-018` `REM-D15` |
| **FR-489** | **Generic shipping is preserved.** Carriers, carrier services, carrier accounts with scopes, shipping labels, manifests, handovers, pickup requests, consignments, carrier status mappings, tracking events, shipments, demand orders, RMAs, return receipts and return gradings keep their tables, screens, permissions and tests. Their only behaviour changes are those named in `FR-480`…`FR-487`. Each such change is listed in the task that makes it | app | v1 | P7 | `RN-050` |
| **FR-490** | **OEM obsolescence returns are absent**: `wh_obsolescence_returns` and `_lines`, the `OBR` series, the two jobs, and the two `warehouse.obsolescence_returns.*` settings. Supplier claims offer **four** claim types: no `OBSOLESCENCE` type and no `OBSOLESCENCE_RETURN` source document. The `V510216` ladder trigger no longer checks one. The **`OBSOLESCENCE` stock KPI** (no movement in 12 months, `V500048:198-201`) **stays** | app | v1 | P7 | `RN-020` `RN-051` |
| **FR-491** | **The trade portal is absent**: `wh_trade_portal_users`, the role `Warehouse Trade Customer` with its grants and menu permissions, the L1 `warehouse_trade`, the customer persona in `WhbOwnerScopeResolver` (`permittedCustomers`/`requireCustomerPermitted`/`CustomerScope`), the `WhbTradeCustomerGrantProvider` port, and every `*ForCustomer`/`toCustomerResponses`/`createTradePortalDraft` path. The counterparty `CUSTOMER` role stays | app · base | v1 | P7 | `RN-021` `REM-D6` |
| **FR-492** | **Accessories coexistence is absent**: `whb_category_stocking_ownership`, `whb_external_stock_snapshots`, `WhbStockingSystemResolver`, the Coexistence report (`WS-225`), Consolidated Valuation (`WS-222`), the `WhInventorySeparationNotice`, and `is_dual_eligible` (`REM-D7`). The stocking-category picker that allocation strategies, GL posting rules and valuation policies use **still works** from its relocated home (`REM-D9`). Item, company, location and counterparty external refs stay | base · app · india | v1 | P7 | `RN-023` `REM-D6` `REM-D7` |
| **FR-493** | **No dead adapter switch exists.** The base enable expression is `base or warehouse or adapter.example or 3pl or india` (`WarehouseBaseModuleConfig:53` cut). There is no `ADAPTER_*` or `ACCESSORIES` source system (`REM-D3`), no `ADAPTER_DEALER`-style i18n label, no "Parts Counter 60 / Workshop Parts 70" menu-slot comment, and no `WAREHOUSE_DEALER_*`/`WAREHOUSE_SERVICES_*` filter scope in `filterUtils.ts` (`R29` F9). The reserved-band ratchet stays | base · app | v1 | P7 | `RN-004` `REM-D3` |
| **FR-494** | **No dealer or retail seeded vocabulary exists**: the document types `JOB_CARD`, `POS_SHIFT` and `CHANNEL_PUBLISH_RUN`; the identifier type `MARKETPLACE_LISTING`; the return types `RTO` and `MARKETPLACE`; the channel kinds `MARKETPLACE`, `OWN_STORE` and `POS`; the RTO, NDR and `AWB_VOID` reasons and `CARRIER_INITIATED`; and the movement types `RTO_RECEIPT` and `RTO_RECEIPT_REVERSAL`. Every seed migration's own count and verification assertion matches the trimmed set | base · app | v1 | P7 | `RN-024` |
| **FR-495** | **`whb_channels` stays with the `B2B` kind only** (`REM-D2`). `whb_stock_movements.channel_id`, `whb_item_identifiers.channel_id`, `wh_demand_orders.channel_id` and `wh_fulfilment_policies.channel_id` stay, with their FKs. The Channels master leaf (`warehouse_channels`, L3, `V500051`) stays. It is **not** the removed L1 of the same name | base · app | v1 | P7 | `RN-043` `REM-D2` |
| **FR-496** | **The dual-use codes are renamed in storage and on every surface**: `LINE_STOP` (label *Line stop / machine down*) in `chk_wh_purchase_orders_order_source`; `PRODUCTION_STORE` (*Production store / shop floor*) as a `WAREHOUSE_TYPE` value; `MANUFACTURER_PART_NUMBER` (*Manufacturer part no.*) as an `IDENTIFIER_TYPE` value. Java constants, en/fr/hi labels and registry-openness tests carry the new code. No stored or displayed `VOR`, `WORKSHOP` or `OEM_PART_NUMBER` remains in the four modules. Supersessions, `ISSUE_TO_ASSET`/`FITMENT`, kits and gate events are unchanged | base · app · 3pl · india | v1 | P7 | `RN-051` `REM-D5` |
| **FR-497** | **Parts KPIs is renamed Stock KPIs everywhere**: classes `WhStockKpi*` (package `whstockkpi`), endpoint `/warehouse/reports/stock-kpis`, permission resource `wh_rpt_stock_kpis`, grid id `wh_rpt_stock_kpis`, menu `warehouse_stock_kpis` → `/dashboard/warehouse/reports/stock-kpis`, export filename `warehouse-stock-kpis`, i18n section `stockKpis` + `help.stockKpis`, help page id `warehouse-reports-stock-kpis`, filter scope `WAREHOUSE_RPT_STOCK_KPI`, ci-gate spec `WhStockKpiFillRateDenominatorTest`. The four metric codes and their frozen definitions are unchanged | app · platform | v1 | P7 | `RN-022` `REM-D5` |
| **FR-498** | **The migration set is a clean rewrite.** No migration in the four modules or the logix client seed creates, alters, inserts into, selects from, casts to or names a removed object. No migration drops one, because none is ever created. A **fresh install on an empty database** succeeds with platform + all four warehouse modules enabled, and with `warehouse-3pl` and `warehouse-india` each disabled. No migration file is renumbered; deleted versions simply leave gaps | base · app · 3pl · india · platform | v1 | P7 | `RN-046` `RN-052` |
| **FR-499** | **The dev database is rebuilt once.** After `P7-13`, `flyway_schema_history` holds no row for a deleted version and no checksum-repaired row for a rewritten one. Every grep gate in §6 returns zero. `shared/scripts/ci-gate.sh ratchets warehouse` and `integration warehouse` pass. Docs, QA notes and contracts in `classic` no longer describe a removed feature as present | all | v1 | P7 | `RN-052` |

**One owner task per requirement (`R29` F13).** `FR-480`, `FR-481`, `FR-489` → `P7-02` · `FR-482`, `FR-483`, `FR-485` → `P7-03` · `FR-484` → `P7-04` · `FR-486`, `FR-487` → `P7-05` · `FR-488` → `P7-06` · `FR-490` → `P7-07` · `FR-491` → `P7-08` · `FR-492` → `P7-09` · `FR-493`, `FR-494`, `FR-495` → `P7-10` · `FR-496`, `FR-497` → `P7-11` · `FR-498`, `FR-499` → `P7-13`. Another task may do part of a requirement's work; it says so as "contributes to", never "closes".

## 5. Verification scenarios

Run against the rebuilt dev DB (`P7-13`) unless the row says otherwise. `psql` means `docker compose exec -T postgres psql` with `shared/docker/.env`.

| # | Given | When | Then | FR | L | Mod | V·Ph | Type |
|---|---|---|---|---|---|---|---|---|
| **WH-SC-660** | Empty postgres volume; `ENABLE_WAREHOUSE_BASE/WAREHOUSE/3PL/INDIA=true`; image rebuilt from the `P7` tree | the backend boots | Flyway applies every warehouse version with no failure and no `FLYWAY_REPAIR_APPLIED` log line; `to_regclass` is NULL for every table in Appendix D.1 (24 tables) | `FR-498` | — | all | v1·P7 | happy |
| **WH-SC-661** | the install of 660 | `SELECT count(*) FROM permissions WHERE name ~ '^(wh_(awb_pools|shipment_ndrs|cod_remittances|channel_accounts|channel_order_imports|channel_publish_rules|tracking_links|marketplace_claims|rto_consignments|carrier_serviceability|rate_quotes|obsolescence_returns|trade_portal|trade_portal_users|rpt_coexistence|rpt_consolidated_valuation|rpt_parts_kpis)|whb_(category_stocking_ownership|external_stock_snapshots)):'` | **0**, and `roles` has no `Warehouse Trade Customer` | `FR-480`…`FR-492` `FR-497` | — | app | v1·P7 | happy |
| **WH-SC-662** | the install of 660 — the `P7` exit install, before any `P9` migration runs (R30 `CP-SC-002`: the name check below is a `P7`-exit assertion; the route check holds on every later install) | query `menus` for the 17 removed `route_path`s (Appendix D.3) and the names `warehouse_channels` at L1, `warehouse_channels_fulfilment`, `warehouse_channels_carriers`, `warehouse_trade`, `warehouse_trade_customers` | **0 rows**. `warehouse_channels` exists **once, at L3** (the Channels master). Cross-dock Plans, Working Calendars, Tracking Events and Carrier Status Mappings each exist once with their old route and prefix, under `warehouse_shipping_planning` (4 children) in L1 `warehouse_shipping` | `FR-488` `FR-495` | — | app | v1·P7 | happy |
| **WH-SC-663** | the install of 660 | `SELECT grid_identifier FROM grid_preferences` ∪ `grid_column_definitions` ∪ `filter_definitions` for the 18 removed grid ids (Appendix D.4) | 0 rows each; `wh_rpt_stock_kpis` has 9 columns and 7 filters; no `wh_rpt_parts_kpis` row | `FR-497` | — | app | v1·P7 | happy |
| **WH-SC-664** | the install of 660 | query `whb_source_systems`, `whb_document_types`, `whb_code_list_values` (`RETURN_TYPE`, `CHANNEL_KIND`, `IDENTIFIER_TYPE`, `WAREHOUSE_TYPE`), `whb_reason_codes`, `whb_movement_types`, `whb_event_types`, `whb_attribute_keys`, `whb_number_series`, `admin_settings` for the Appendix D.5 codes | none present; `CHANNEL_KIND` = `{B2B}`; `RETURN_TYPE` count = 8; `IDENTIFIER_TYPE` has `MANUFACTURER_PART_NUMBER`, not `OEM_PART_NUMBER`; `WAREHOUSE_TYPE` has `PRODUCTION_STORE`, not `WORKSHOP`; no reason with context `RTO`, `NDR` or `AWB_VOID` | `FR-494` `FR-496` | `I-18` | base | v1·P7 | happy |
| **WH-SC-665** | the install of 660 | `\d wh_demand_orders`, `\d wh_carriers`, `\d wh_carrier_services`, `\d whb_item_categories` | no `payment_mode`, `cod_amount`, `channel_account_id`; no `ndr_response_hours`, `ndr_auto_rto_grace_hours`, `cod_remittance_days`; no `supports_cod` (`OD-22` default); no `is_dual_eligible`; `channel_id` with `fk_wh_demand_orders_channel` **present** | `FR-483` `FR-484` `FR-492` `FR-495` | — | app · base | v1·P7 | happy |
| **WH-SC-666** | `stores1` on the rebuilt install; carrier `BLUEDART`, shipment `SHP-0001` packed | the clerk dispatches with tracking `1234567890`, the carrier posts `DELIVERED` through ingest | the shipment is `DISPATCHED` (`WhShipment.STATUS_DISPATCHED`, `WhShipment.java:55`), then `DELIVERED`; its demand order is `SHIPPED`, then `DELIVERED`; the tracking event and status mapping are stored; **no** AWB row, NDR, tracking link, notification or e-mail is written; the despatch stock movement equals the expectation of the kept baseline tests `WhDespatchServiceTest` (case `WH-SC-056`: one `ISSUE` relief, staging → `VIRT-CUSTOMER`) and `WhShipmentConfirmedDispatchIntegrationTest` (one `shipment.confirmed` per dispatch), both run unchanged before and after `P7` (`R29` F15) | `FR-480` `FR-482` `FR-485` `FR-489` | `L-1` | app | v1·P7 | happy |
| **WH-SC-667** | `BLUEDART` has 1 shipping label and no other document | the admin deletes the carrier | refused **409 `CARRIER_IN_USE`** with count 1. The guard SQL names no removed table. A carrier with no documents deletes | `FR-481` `FR-489` | — | app | v1·P7 | edge |
| **WH-SC-668** | a posted return receipt of type `CUSTOMER` for customer `CUST-01` | it is reversed | the reversal movement mirrors the original; no claim or RTO row is touched; the return-type picker offers exactly the 8 kept types | `FR-486` `FR-487` | `L-3` | app | v1·P7 | happy |
| **WH-SC-669** | a demand-order create request with `Idempotency-Key K1` | it is sent twice with an identical body | one order is created and the replay returns it. The fingerprint is a SHA-256 over the canonical fields **without** `paymentMode`/`codAmount`. A request body still carrying `paymentMode` or `codAmount` is **ignored**, not refused: the platform `ObjectMapper` disables `FAIL_ON_UNKNOWN_PROPERTIES` (`platform/backend/src/main/java/ai/platform/config/JacksonConfig.java:73`) and `WhDemandOrderRequest` has no override; the order is created and its fingerprint equals that of the same body without the two fields (`R29` F12) | `FR-483` | — | app | v1·P7 | edge |
| **WH-SC-670** | supplier `SUP-01`; a claim modal on Supplier Claims | the buyer opens the claim-type picker | 4 types; no `OBSOLESCENCE`; source-document picker has no `OBSOLESCENCE_RETURN`; a claim line value = qty × unit cost rounded HALF_UP to money scale (relocated helper) | `FR-490` | — | app | v1·P7 | happy |
| **WH-SC-671** | the KPI report for `SITE-A` | the planner opens **Reports → Stock KPIs** and exports | the page loads at `/dashboard/warehouse/reports/stock-kpis`; the API is `/warehouse/reports/stock-kpis/management`; a user with `wh_rpt_stock_kpis:view` sees it and one without it is refused 403; the export file is `warehouse-stock-kpis-*.xlsx`; metric values equal the `WhStockKpiFillRateDenominatorTest` expectations | `FR-497` | — | app | v1·P7 | happy |
| **WH-SC-672** | a PO for `OF-1120` | the buyer picks order source **Line stop / machine down** and saves | stored `order_source = 'LINE_STOP'`; `WhSupplierLeadTimeQueryService` excludes it from lead-time history as it did `VOR`; inserting `'VOR'` by SQL fails `chk_wh_purchase_orders_order_source` | `FR-496` | — | app | v1·P7 | edge |
| **WH-SC-673** | allocation-strategy, GL-posting-rule and valuation-policy modals | each opens its category picker | the stocking-category tree loads from the item-category query service; `WhbAllocationStrategyService`, `WhbGlPostingRuleService` and `WhbValuationPolicyService` inject no class named `*StockingOwnership*` | `FR-492` | — | base | v1·P7 | happy |
| **WH-SC-674** | the rebuilt stack | `curl -i /api/public/warehouse/tracking/anything` and open `/track/anything` | **404** both; `grep -rn '/public/warehouse' warehouse*/backend/src/main` = 0 | `FR-485` | — | app | v1·P7 | error |
| **WH-SC-675** | the `P7` tree | the grep gates GATE-1…GATE-8 of §6 run from the classic root | every gate prints nothing and exits 1 (no match) | `FR-480`…`FR-499` | — | all | v1·P7 | happy |
| **WH-SC-676** | the `P7` tree | `shared/scripts/ci-gate.sh ratchets warehouse` then `integration warehouse` | both exit 0; `20-warehouse.def` names `WhStockKpiFillRateDenominatorTest` and no deleted test class | `FR-499` | — | all | v1·P7 | happy |
| **WH-SC-677** | empty volume; `ENABLE_WAREHOUSE_3PL=false`, `ENABLE_WAREHOUSE_INDIA=false` | the backend boots | migrations succeed. No base or app migration depends on a 3PL or India object. `is_dual_eligible` is absent without India's `V540130` | `FR-498` | — | base · app | v1·P7 | edge |
| **WH-SC-678** | `CLIENT_NAME=logix`, empty volume | the backend boots with the logix client seeds | `V910021`, `V910031`, `V910032` and `V910033` apply. No `COD` or `OBR` number series exists. The `wh_carriers` and `wh_demand_orders` inserts name no dropped column | `FR-498` | — | platform | v1·P7 | happy |
| **WH-SC-679** | the rebuilt dev DB | `SELECT version FROM flyway_schema_history WHERE version IN (<Appendix B.1 versions>)`, plus `WHERE type='DELETE' OR description LIKE '%repair%'` | 0 rows each; one history row per present warehouse file, with checksums matching the files | `FR-499` | — | all | v1·P7 | happy |

## 6. Grep gates

Run from the classic root. Each gate is wrapped as `! grep … ` (pass = no match). `--exclude-dir={target,node_modules,.next,results}`
applies throughout. Scope `$W` = `warehouse-base warehouse warehouse-3pl warehouse-india` (sources, resources, frontend, tests, docs);
`$P` = `platform/frontend/src/utils/filterUtils.ts platform/backend/src/main/java/ai/platform/config/CacheConfiguration.java platform/backend/src/main/resources/db/client/logix shared/scripts/ci-gate`. `$P` takes **only the logix client seed**: the other client folders (`vehicron`, `pasco`, `ktlautomobiles`) are dealer seeds behind the `RN-054` fence, and their `'ACCESSORIES'`/`'RTO'`/`'WORKSHOP'` department and document codes are not warehouse vocabulary (`R29` F6).

**Per-task gates (`R29` F7).** A `P7-02`…`P7-11` acceptance grep runs over `$T` = `warehouse-base warehouse warehouse-3pl warehouse-india` with `--exclude-dir={target,node_modules,.next,results,docs} --exclude='*.md'`, plus the platform files and `.claude/testing/descriptors` it names. It matches only the task's own surfaces: docs belong to `P7-12`, and a code another task renames later (`OEM_PART_NUMBER`, `VOR`, `WORKSHOP`, `PartsKpi` → `P7-11`) is left out of the earlier task's pattern. **The full gate set GATE-1…GATE-8, over `$W $P`, runs only in `P7-13`.**

| Gate | Pattern (`grep -rIE`) | Scope | Owner task |
|---|---|---|---|
| **GATE-1 classes** | `WhAwb|AwbPool|ShipmentNdr|WhNdr|CodRemittance|WhCod[A-Z]|ChannelAccount|ChannelOrderImport|ChannelPublish|TrackingLink|TrackingNotification|TrackingPublic|MarketplaceClaim|RtoConsignment|RtoReceipt|CarrierServiceability|RateQuote|RateShop|ObsolescenceReturn|ObsolescenceCandidate|ObsolescenceWindow|TradePortal|TradeCustomer|CustomerPersona|Coexistence|CategoryStockingOwnership|ExternalStockSnapshot|StockingSystem|ConsolidatedValuation|InventorySeparation|PartsKpi|partsKpi` | `$W $P` `--include=*.{java,ts,tsx,json,sql,def}` | `P7-02`…`P7-11` |
| **GATE-2 tables/resources** | `wh_awb_|wh_shipment_ndrs|wh_ndr_actions|wh_cod_remittance|wh_channel_account|wh_channel_order_import|wh_channel_publish|wh_tracking_link|wh_tracking_notification|wh_marketplace_claim|wh_rto_consignment|wh_carrier_serviceability|wh_rate_quote|wh_obsolescence_return|wh_trade_portal|whb_category_stocking_ownership|whb_external_stock_snapshot|wh_rpt_coexistence|wh_rpt_consolidated_valuation|wh_rpt_parts_kpis|is_dual_eligible|isDualEligible|supports_cod|supportsCod` | `$W $P` | all |
| **GATE-3 vocabulary** | `ADAPTER_(DEALER|SERVICES|FIELD_SERVICE|ASSETS)|'ACCESSORIES'|"ACCESSORIES"|JOB_CARD|POS_SHIFT|MARKETPLACE_LISTING|CHANNEL_PUBLISH_RUN|CHANNEL_ORDER_ID|RTO_RECEIPT|RTO_INITIATED|RTO_IN_TRANSIT|RTO_DELIVERED|NDR_[A-Z_]+|CARRIER_INITIATED|AWB_VOID|OWN_STORE|OBSOLESCENCE_RETURN|TYPE_OBSOLESCENCE|OEM_PART_NUMBER|\bPAYMENT_MODE\b|DO_PAYMENT_MODE|DO_COD_AMOUNT|PAYMENT_(PREPAID|COD)\b|WhDemandOrder\.PAYMENT_MODES|channel\.inventory\.published|CHANNEL_INVENTORY_PUBLISHED`. The payment terms are anchored to the demand-order and wave tokens (`WhWaveCriteria` `"PAYMENT_MODE"`, the `V510100` CHECK value, the i18n wave label, `WhDemandOrder.PAYMENT_*`, `DO_PAYMENT_MODE_UNKNOWN`), so the kept `WhCarrierAccount.PAYMENT_MODE_CREDIT`/`PAYMENT_MODES` (`REM-D12`) never match | `$W $P` `--exclude=V500200__Allow_warehouse_in_platform_module_check_constraints.sql` (`REM-D19`) | `P7-03`, `P7-04`, `P7-10`, `P7-11` |
| **GATE-4 literal codes** | `'(RTO|NDR|COD|POS|MARKETPLACE|VOR|WORKSHOP|OBR)'|"(RTO|NDR|COD|POS|MARKETPLACE|VOR|WORKSHOP|OBR)"` | `$W $P` | `P7-10`, `P7-11` |
| **GATE-5 routes** | `outbound/(awb-pools|ndr|cod-remittances|channel-accounts|channel-imports|publish-rules|tracking-links|rto|serviceability|rate-quotes|trade-portal)|inbound/(obsolescence-returns|marketplace-claims)|reports/(coexistence|consolidated-valuation|parts-kpis)|masters/category-ownership|platform/external-snapshots|/public/warehouse` | `$W $P` | `P7-02`…`P7-11` |
| **GATE-6 adapter switches** | `adapter\.dealer|adapter\.services|warehouse-adapter-(dealer|services)|warehouseadapter(dealer|services)|Parts Counter|Workshop Parts|WAREHOUSE_(DEALER|SERVICES)_|whad_|whas_` | `$W platform/frontend/src/utils/filterUtils.ts` **excluding** `WarehouseBaseCouplingTest.java` (reserved-band ratchet, `REM-D3`, `REM-D19`) | `P7-10` |
| **GATE-7 public route group** | `find warehouse/frontend/src/app -path '*(public)*'` prints nothing | — | `P7-03` |
| **GATE-8 i18n sections** | `jq -e 'has("awbPool") or has("shipmentNdr") or has("codRemittance") or has("channelAccount") or has("channelOrderImport") or has("publishRule") or has("trackingLink") or has("marketplaceClaim") or has("rtoConsignment") or has("carrierServiceability") or has("rateQuote") or has("obsolescenceReturn") or has("tradePortal") or has("coexistence") or has("inventorySeparation") or has("consolidatedValuation") or has("partsKpis")'` on each `warehouse/.../{en,fr,hi}/warehouse.json`, and `has("categoryStockingOwnership") or has("externalStockSnapshot")` on each `warehouseBase.json` → false. `help.*` sub-keys likewise | — | each task for its own sections |

**Runnable form (R31 F-SR-009, F-SR-010).** The per-artefact checks are run from `rem-removal.contract.md` §1.7 — the same patterns unescaped (a `\|` copied from a markdown table cell is a literal pipe in ERE and in PostgreSQL `~`), the literal `RMV-UNR-17` route list, the exact-path absence of every Appendix A file (`RMV-UNR-26`), and an anti-vacuous run on the pre-`P7` tree that must match. The GATE patterns in the table above are already unescaped.

Gate exceptions are not allowed, except the two one-file exclusions named in `REM-D19` and the `OBSOLESCENCE` **KPI metric**. GATE-3 never matches the bare `OBSOLESCENCE`,
and GATE-4 matches only quoted whole codes. If a legitimate kept use is found, the task records it in §2 before merging. A silent allowlist is not permitted.

## 7. Refusals (out of scope, stated)

- **No `warehouse-retail` or `warehouse-dealer` sibling** (`RN-050` withdraws §9's extraction). Recreation is a future decision with its own band.
- **No drop migration, no `to_regclass` guard added for a removed object, no feature flag, no deprecation period** (`RN-052`).
- **No data migration.** No database holds warehouse rows that need preserving (`inv-migrations` §7: the git stack has 0 rows in V50xxxx–V54xxxx). Any other warehouse-enabled database is rebuilt, never repaired.
- **No renumbering** of surviving migrations. Gaps left by deleted versions stay as gaps.
- **No change to** `dealer`, `automotive`, `accessories`, `insurance`, `services`, `assets`, accounting adapters (`ENABLE_ACCOUNTING_ADAPTER_DEALER` is out of scope), mobile, or platform code beyond the three files of §1.
- **No re-use of the freed menu slots 60/70** or of the deleted permission names.
- **No new feature.** Re-homing menus, relocating helpers and renaming codes are the only additive edits.
- **`CLAUDE.md`'s stale `WarehouseAdapterDealerSafeTranslation.tsx` mention** is reported to the user. It is not edited here, because a CLAUDE.md edit needs user approval.

## 8. Existing tasks this phase supersedes

| Task | State before `P7` | Note added by REM |
|---|---|---|
| `P5-09`, `P5-11`, `P5-13`, `P5-08` | PARTIALLY VOID (SPINE) | none needed. The void parts are removed by `P7-02`…`P7-08` |
| `P5-12`, `P5-15` | VOID (SPINE) | none needed |
| `P1-04` | live: `V500053` + the D-9 mitigations | **PARTIALLY VOID**: category ownership and external snapshots → `P7-09`. Item external refs stay |
| `P2-12` | live: `WS-122` RTO | **PARTIALLY VOID**: RTO consignments → `P7-05`. Return receipts and RMAs stay |
| `P2-21` | live: `WS-217` Parts KPIs | **PARTIALLY SUPERSEDED**: `WS-217` renamed Stock KPIs by `P7-11`. The rest stays |
| `P2-27` | live: `WS-225` | **VOID** → `P7-09` |
| `P3-17` | live: `WS-222` + KPI snapshots | **PARTIALLY VOID**: `WS-222` → `P7-09`. KPI snapshots stay |
| `P6-11` | live: accessories absorption path | **VOID**: accessories coexistence is removed (`RN-051`) |

---

## Appendix A — files to delete (full path lists)

Generated from the four inventories (`scratchpad/rem/inv-*.txt`, 2026-10-22). Each task owns the groups named in its Scope.

### A.1 Backend Java to delete — retail (RN-050)

#### R1 AWB pools + numbers — 29 files

- `warehouse/backend/src/main/java/ai/warehouse/controller/` — `WhAwbPoolController.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/request/` — `WhAwbBlockRequest.java`, `WhAwbClaimRequest.java`, `WhAwbPoolRequest.java`, `WhAwbVoidRequest.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/response/` — `WhAwbNumberResponse.java`, `WhAwbPoolResponse.java`, `WhAwbPoolStatisticsResponse.java`
- `warehouse/backend/src/main/java/ai/warehouse/entity/` — `WhAwbNumber.java`, `WhAwbPool.java`
- `warehouse/backend/src/main/java/ai/warehouse/repository/` — `WhAwbNumberRepository.java`, `WhAwbNumberRepositoryCustom.java`, `WhAwbNumberRepositoryCustomImpl.java`, `WhAwbPoolRepository.java`, `WhAwbPoolRepositoryCustom.java`, `WhAwbPoolRepositoryCustomImpl.java`
- `warehouse/backend/src/main/java/ai/warehouse/scheduler/` — `WhAwbPoolTopUpScheduler.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/` — `WhAwbPoolExportService.java`, `WhAwbPoolService.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/whawbpool/` — `WhAwbClaimService.java`, `WhAwbPoolMapper.java`, `WhAwbPoolQueryService.java`, `WhAwbPoolTopUpJob.java`, `WhAwbPoolValidationService.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/whawbpool/` — `WhAwbClaimConcurrencyIntegrationTest.java`, `WhAwbClaimServiceTest.java`, `WhAwbPoolTopUpJobTest.java`, `WhAwbPoolValidationServiceTest.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/whshipment/` — `WhShipmentTrackingAwbRuleTest.java`

#### R2 NDR — 29 files

- `warehouse/backend/src/main/java/ai/warehouse/controller/` — `WhShipmentNdrController.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/request/` — `WhNdrAcknowledgeRequest.java`, `WhNdrActionRequest.java`, `WhNdrBulkActionRequest.java`, `WhShipmentNdrRequest.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/response/` — `WhNdrActionResponse.java`, `WhNdrBulkActionResponse.java`, `WhShipmentNdrResponse.java`, `WhShipmentNdrStatisticsResponse.java`
- `warehouse/backend/src/main/java/ai/warehouse/entity/` — `WhNdrAction.java`, `WhShipmentNdr.java`
- `warehouse/backend/src/main/java/ai/warehouse/repository/` — `WhNdrActionRepository.java`, `WhShipmentNdrRepository.java`, `WhShipmentNdrRepositoryCustom.java`, `WhShipmentNdrRepositoryCustomImpl.java`
- `warehouse/backend/src/main/java/ai/warehouse/scheduler/` — `WhNdrScheduler.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/` — `WhShipmentNdrExportService.java`, `WhShipmentNdrService.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/whshipmentndr/` — `WhNdrAutoRtoJob.java`, `WhNdrClock.java`, `WhNdrEscalationJob.java`, `WhNdrLifecycleService.java`, `WhShipmentNdrMapper.java`, `WhShipmentNdrQueryService.java`, `WhShipmentNdrValidationService.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/` — `WhShipmentNdrServiceBulkTest.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/whshipmentndr/` — `WhNdrAutoRtoJobTest.java`, `WhNdrClockTest.java`, `WhNdrLifecycleServiceTest.java`

#### R3 COD remittances — 25 files

- `warehouse/backend/src/main/java/ai/warehouse/controller/` — `WhCodRemittanceController.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/request/` — `WhCodRemittanceLineRequest.java`, `WhCodRemittanceRequest.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/response/` — `WhCodAgeingResponse.java`, `WhCodRemittanceLineResponse.java`, `WhCodRemittanceResponse.java`, `WhCodRemittanceStatisticsResponse.java`
- `warehouse/backend/src/main/java/ai/warehouse/entity/` — `WhCodRemittance.java`, `WhCodRemittanceLine.java`
- `warehouse/backend/src/main/java/ai/warehouse/repository/` — `WhCodRemittanceLineRepository.java`, `WhCodRemittanceRepository.java`, `WhCodRemittanceRepositoryCustom.java`, `WhCodRemittanceRepositoryCustomImpl.java`
- `warehouse/backend/src/main/java/ai/warehouse/scheduler/` — `WhCodRemittanceScheduler.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/` — `WhCodRemittanceExportService.java`, `WhCodRemittanceService.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/whcodremittance/` — `WhCodAccountingSink.java`, `WhCodEnvelopeHandover.java`, `WhCodRemittanceMapper.java`, `WhCodRemittanceMatcher.java`, `WhCodRemittanceQueryService.java`, `WhCodRemittanceValidationService.java`, `WhCodUnremittedAgeingJob.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/` — `WhCodRemittanceHandoverDispositionTest.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/whcodremittance/` — `WhCodRemittanceMatcherTest.java`

#### R4 Channel accounts / order imports / publish rules+logs+runs — 68 files

- `warehouse/backend/src/main/java/ai/warehouse/controller/` — `WhChannelAccountController.java`, `WhChannelOrderImportController.java`, `WhChannelPublishRuleController.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/request/` — `WhChannelAccountRequest.java`, `WhChannelAccountWarehouseRequest.java`, `WhChannelOrderImportRequest.java`, `WhChannelPublishAcknowledgeRequest.java`, `WhChannelPublishRuleRequest.java`, `WhChannelPublishRunRequest.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/response/` — `WhChannelAccountResponse.java`, `WhChannelAccountStatisticsResponse.java`, `WhChannelAccountWarehouseResponse.java`, `WhChannelOrderImportResponse.java`, `WhChannelOrderImportStatisticsResponse.java`, `WhChannelPublishLogResponse.java`, `WhChannelPublishLogStatisticsResponse.java`, `WhChannelPublishRuleResponse.java`, `WhChannelPublishRuleStatisticsResponse.java`, `WhChannelPublishRunResponse.java`
- `warehouse/backend/src/main/java/ai/warehouse/entity/` — `WhChannelAccount.java`, `WhChannelAccountWarehouse.java`, `WhChannelOrderImport.java`, `WhChannelPublishLog.java`, `WhChannelPublishRule.java`
- `warehouse/backend/src/main/java/ai/warehouse/repository/` — `WhChannelAccountRepository.java`, `WhChannelAccountRepositoryCustom.java`, `WhChannelAccountRepositoryCustomImpl.java`, `WhChannelAccountWarehouseRepository.java`, `WhChannelOrderImportRepository.java`, `WhChannelOrderImportRepositoryCustom.java`, `WhChannelOrderImportRepositoryCustomImpl.java`, `WhChannelPublishLogRepository.java`, `WhChannelPublishLogRepositoryCustom.java`, `WhChannelPublishLogRepositoryCustomImpl.java`, `WhChannelPublishRuleRepository.java`, `WhChannelPublishRuleRepositoryCustom.java`, `WhChannelPublishRuleRepositoryCustomImpl.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/` — `WhChannelAccountExportService.java`, `WhChannelAccountService.java`, `WhChannelOrderImportExportService.java`, `WhChannelOrderImportService.java`, `WhChannelPublishLogExportService.java`, `WhChannelPublishRuleExportService.java`, `WhChannelPublishRuleService.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/whchannelaccount/` — `WhChannelAccountMapper.java`, `WhChannelAccountQueryService.java`, `WhChannelAccountSiteResolver.java`, `WhChannelAccountValidationService.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/whchannelorderimport/` — `WhChannelOrderImportMapper.java`, `WhChannelOrderImportPayloadCodec.java`, `WhChannelOrderImportQueryService.java`, `WhChannelOrderImportRejection.java`, `WhChannelOrderImportValidationService.java`, `WhChannelOrderImportWriter.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/whchannelpublishrule/` — `WhChannelPublishCalculator.java`, `WhChannelPublishRuleMapper.java`, `WhChannelPublishRuleQueryService.java`, `WhChannelPublishRuleValidationService.java`, `WhChannelPublishService.java`
- `warehouse/backend/src/test/java/ai/warehouse/controller/` — `WhChannelAccountVerbGateTest.java`, `WhChannelPublishRuleVerbGateTest.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/` — `WhChannelAccountExportParityTest.java`, `WhChannelPublishExportParityTest.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/whchannelaccount/` — `WhChannelAccountSitesTest.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/whchannelorderimport/` — `WhChannelOrderImportDecisionTest.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/whchannelpublishrule/` — `WhChannelPublishCalculatorTest.java`, `WhChannelPublishRuleStockStatusTest.java`, `WhChannelPublishServiceTest.java`

#### R5 Tracking links / notification rules / public track — 27 files

- `warehouse/backend/src/main/java/ai/warehouse/controller/` — `WhTrackingLinkController.java`, `WhTrackingLinkPublicController.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/request/` — `WhTrackingEventRequest.java`, `WhTrackingLinkRequest.java`, `WhTrackingLinkRevokeRequest.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/response/` — `WhTrackingLinkResponse.java`, `WhTrackingLinkStatisticsResponse.java`, `WhTrackingNotificationRuleResponse.java`, `WhTrackingPublicResponse.java`
- `warehouse/backend/src/main/java/ai/warehouse/entity/` — `WhTrackingLink.java`, `WhTrackingNotificationRule.java`
- `warehouse/backend/src/main/java/ai/warehouse/repository/` — `WhTrackingLinkRepository.java`, `WhTrackingLinkRepositoryCustom.java`, `WhTrackingLinkRepositoryCustomImpl.java`, `WhTrackingNotificationRuleRepository.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/` — `WhTrackingLinkExportService.java`, `WhTrackingLinkService.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/whtrackinglink/` — `WhTrackingLinkIssuer.java`, `WhTrackingLinkMapper.java`, `WhTrackingLinkNotifier.java`, `WhTrackingLinkPublicService.java`, `WhTrackingLinkQueryService.java`, `WhTrackingLinkTokenService.java`
- `warehouse/backend/src/test/java/ai/warehouse/security/` — `WhPublicTrackingLinkAdversarialIntegrationTest.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/whtrackinglink/` — `WhTrackingLinkNotifierTest.java`, `WhTrackingLinkPublicServiceTest.java`, `WhTrackingLinkTokenServiceTest.java`

#### R6 Marketplace claims — 17 files

- `warehouse/backend/src/main/java/ai/warehouse/controller/` — `WhMarketplaceClaimController.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/request/` — `WhClaimSettlementRequest.java`, `WhMarketplaceClaimSubmitRequest.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/response/` — `WhMarketplaceClaimResponse.java`, `WhMarketplaceClaimStatisticsResponse.java`
- `warehouse/backend/src/main/java/ai/warehouse/entity/` — `WhMarketplaceClaim.java`
- `warehouse/backend/src/main/java/ai/warehouse/repository/` — `WhMarketplaceClaimRepository.java`, `WhMarketplaceClaimRepositoryCustom.java`, `WhMarketplaceClaimRepositoryCustomImpl.java`
- `warehouse/backend/src/main/java/ai/warehouse/scheduler/` — `WhMarketplaceClaimWindowScheduler.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/` — `WhMarketplaceClaimExportService.java`, `WhMarketplaceClaimService.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/whmarketplaceclaim/` — `WhMarketplaceClaimMapper.java`, `WhMarketplaceClaimQueryService.java`, `WhMarketplaceClaimValidationService.java`, `WhMarketplaceClaimWindowJob.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/whmarketplaceclaim/` — `WhMarketplaceClaimWindowTest.java`

#### R7 RTO consignments — 14 files

- `warehouse/backend/src/main/java/ai/warehouse/controller/` — `WhRtoConsignmentController.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/request/` — `WhRtoConsignmentRequest.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/response/` — `WhRtoConsignmentResponse.java`, `WhRtoConsignmentStatisticsResponse.java`
- `warehouse/backend/src/main/java/ai/warehouse/entity/` — `WhRtoConsignment.java`
- `warehouse/backend/src/main/java/ai/warehouse/repository/` — `WhRtoConsignmentRepository.java`, `WhRtoConsignmentRepositoryCustom.java`, `WhRtoConsignmentRepositoryCustomImpl.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/` — `WhRtoConsignmentExportService.java`, `WhRtoConsignmentService.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/whrtoconsignment/` — `WhRtoConsignmentMapper.java`, `WhRtoConsignmentQueryService.java`, `WhRtoConsignmentValidationService.java`, `WhRtoReceiptLinker.java`

#### R8 Courier serviceability + rate quotes/rate shop — 34 files

- `warehouse/backend/src/main/java/ai/warehouse/controller/` — `WhCarrierServiceabilityController.java`, `WhRateQuoteController.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/request/` — `WhCarrierServiceabilityRequest.java`, `WhRateShopRequest.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/response/` — `WhCarrierServiceabilityResponse.java`, `WhCarrierServiceabilityStatisticsResponse.java`, `WhRateQuoteResponse.java`, `WhRateQuoteStatisticsResponse.java`, `WhRateShopResponse.java`
- `warehouse/backend/src/main/java/ai/warehouse/entity/` — `WhCarrierServiceability.java`, `WhRateQuote.java`
- `warehouse/backend/src/main/java/ai/warehouse/repository/` — `WhCarrierServiceabilityRepository.java`, `WhCarrierServiceabilityRepositoryCustom.java`, `WhCarrierServiceabilityRepositoryCustomImpl.java`, `WhRateQuoteRepository.java`, `WhRateQuoteRepositoryCustom.java`, `WhRateQuoteRepositoryCustomImpl.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/` — `WhCarrierServiceabilityExportService.java`, `WhCarrierServiceabilityImportFileExportService.java`, `WhCarrierServiceabilityService.java`, `WhRateQuoteExportService.java`, `WhRateQuoteService.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/whcarrierserviceability/` — `WhCarrierServiceabilityImportHandler.java`, `WhCarrierServiceabilityMapper.java`, `WhCarrierServiceabilityQueryService.java`, `WhCarrierServiceabilityValidationService.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/whratequote/` — `WhCarrierServiceabilityChecker.java`, `WhRateQuoteMapper.java`, `WhRateQuoteQueryService.java`, `WhRateQuoteReader.java`, `WhRateShopService.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/whcarrierserviceability/` — `WhCarrierServiceabilityImportHandlerTest.java`, `WhCarrierServiceabilityValidationServiceTest.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/whratequote/` — `WhRateShopServiceTest.java`

Retail Java total: **243** files (+ `WhCarrierIntegrationJobConfiguration.java`, deleted whole because every bean in it goes).

### A.2 Backend Java to delete — dealer (RN-051)

#### D1 Oem Obsolescence Returns — 26 files

- `warehouse/backend/src/main/java/ai/warehouse/controller/` — `WhObsolescenceReturnController.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/request/` — `WhObsolescenceReturnLineRequest.java`, `WhObsolescenceReturnRequest.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/response/` — `WhObsolescenceCandidateResponse.java`, `WhObsolescenceReturnLineResponse.java`, `WhObsolescenceReturnResponse.java`, `WhObsolescenceReturnStatisticsResponse.java`
- `warehouse/backend/src/main/java/ai/warehouse/entity/` — `WhObsolescenceReturn.java`, `WhObsolescenceReturnLine.java`
- `warehouse/backend/src/main/java/ai/warehouse/repository/` — `WhObsolescenceReturnLineRepository.java`, `WhObsolescenceReturnRepository.java`, `WhObsolescenceReturnRepositoryCustom.java`, `WhObsolescenceReturnRepositoryCustomImpl.java`
- `warehouse/backend/src/main/java/ai/warehouse/scheduler/` — `WhObsolescenceCandidatesScheduler.java`, `WhObsolescenceWindowWarningScheduler.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/` — `WhObsolescenceReturnExportService.java`, `WhObsolescenceReturnService.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/whobsolescencereturn/` — `WhObsolescenceCandidatesJob.java`, `WhObsolescenceReturnMapper.java`, `WhObsolescenceReturnQueryService.java`, `WhObsolescenceReturnValidationService.java`, `WhObsolescenceWindowWarningJob.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/` — `WhObsolescenceReturnCostSuppressionTest.java`, `WhObsolescenceReturnCostWriteTest.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/whobsolescencereturn/` — `WhObsolescenceReturnClaimTest.java`, `WhObsolescenceWindowWarningJobTest.java`

#### D2 Trade Portal — 27 files

- `warehouse/backend/src/main/java/ai/warehouse/controller/` — `WhTradePortalController.java`, `WhTradePortalUserController.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/request/` — `WhTradePortalOrderRequest.java`, `WhTradePortalUserRequest.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/response/` — `WhTradePortalAvailabilityResponse.java`, `WhTradePortalUserResponse.java`, `WhTradePortalUserStatisticsResponse.java`
- `warehouse/backend/src/main/java/ai/warehouse/entity/` — `WhTradePortalUser.java`
- `warehouse/backend/src/main/java/ai/warehouse/repository/` — `WhTradePortalReadRepository.java`, `WhTradePortalUserRepository.java`, `WhTradePortalUserRepositoryCustom.java`, `WhTradePortalUserRepositoryCustomImpl.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/` — `WhTradePortalService.java`, `WhTradePortalUserExportService.java`, `WhTradePortalUserService.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/whtradeportal/` — `WhTradePortalCustomerGrantAdapter.java`, `WhTradePortalUserMapper.java`, `WhTradePortalUserQueryService.java`, `WhTradePortalUserValidationService.java`
- `warehouse/backend/src/test/java/ai/warehouse/repository/` — `WhTradePortalReadRepositoryHouseOwnerTest.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/` — `WhTradePortalDraftOrderTest.java`, `WhTradePortalServiceScopeTest.java`, `WhTradePortalUserServiceTest.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/whdemandorder/` — `WhTradePortalCreateReplayIntegrationTest.java`
- `warehouse/backend/src/test/java/ai/warehouse/service/whtradeportal/` — `WhTradePortalAvailabilityContractTest.java`
- `warehouse-base/backend/src/main/java/ai/warehousebase/service/owner/` — `WhbTradeCustomerGrantProvider.java`
- `warehouse-base/backend/src/test/java/ai/warehousebase/service/owner/` — `WhbOwnerScopeResolverCustomerPersonaTest.java`

#### D3a Accessories Coexistence — 34 files

- `warehouse-base/backend/src/main/java/ai/warehousebase/controller/` — `WhbCategoryStockingOwnershipController.java`, `WhbExternalStockSnapshotController.java`
- `warehouse-base/backend/src/main/java/ai/warehousebase/dto/request/` — `WhbCategoryStockingOwnershipEndRequest.java`, `WhbCategoryStockingOwnershipRequest.java`
- `warehouse-base/backend/src/main/java/ai/warehousebase/dto/response/` — `WhbCategoryStockingOwnershipResponse.java`, `WhbExternalStockSnapshotResponse.java`, `WhbStockingSystemResolutionResponse.java`
- `warehouse-base/backend/src/main/java/ai/warehousebase/entity/` — `WhbCategoryStockingOwnership.java`, `WhbExternalStockSnapshot.java`
- `warehouse-base/backend/src/main/java/ai/warehousebase/repository/` — `WhbCategoryStockingOwnershipRepository.java`, `WhbCategoryStockingOwnershipRepositoryCustom.java`, `WhbCategoryStockingOwnershipRepositoryCustomImpl.java`, `WhbExternalStockSnapshotRepository.java`, `WhbExternalStockSnapshotRepositoryCustom.java`, `WhbExternalStockSnapshotRepositoryCustomImpl.java`
- `warehouse-base/backend/src/main/java/ai/warehousebase/service/` — `WhbCategoryStockingOwnershipExportService.java`, `WhbCategoryStockingOwnershipService.java`, `WhbExternalStockSnapshotExportService.java`, `WhbExternalStockSnapshotService.java`
- `warehouse-base/backend/src/main/java/ai/warehousebase/service/whbcategorystockingownership/` — `WhbCategoryStockingOwnershipMapper.java`, `WhbCategoryStockingOwnershipQueryService.java`, `WhbCategoryStockingOwnershipValidationService.java`, `WhbStockingSystemResolver.java`
- `warehouse-base/backend/src/main/java/ai/warehousebase/service/whbexternalstocksnapshot/` — `WhbExternalStockSnapshotMapper.java`, `WhbExternalStockSnapshotQueryService.java`
- `warehouse/backend/src/main/java/ai/warehouse/controller/` — `WhCoexistenceController.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/response/` — `WhCoexistenceReadinessResponse.java`, `WhCoexistenceResponse.java`, `WhCoexistenceStatisticsResponse.java`
- `warehouse/backend/src/main/java/ai/warehouse/repository/` — `WhCoexistenceRepositoryCustom.java`, `WhCoexistenceRepositoryCustomImpl.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/` — `WhCoexistenceExportService.java`, `WhCoexistenceService.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/whcoexistence/` — `WhCoexistenceQueryService.java`

#### D3b Consolidated Valuation (Ws-222, V511262) — 8 files

- `warehouse/backend/src/main/java/ai/warehouse/controller/` — `WhConsolidatedValuationController.java`
- `warehouse/backend/src/main/java/ai/warehouse/dto/response/` — `WhConsolidatedValuationResponse.java`, `WhConsolidatedValuationStatisticsResponse.java`
- `warehouse/backend/src/main/java/ai/warehouse/repository/` — `WhConsolidatedValuationRepositoryCustom.java`, `WhConsolidatedValuationRepositoryCustomImpl.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/` — `WhConsolidatedValuationExportService.java`, `WhConsolidatedValuationService.java`
- `warehouse/backend/src/main/java/ai/warehouse/service/whconsolidatedvaluation/` — `WhConsolidatedValuationQueryService.java`

Dealer Java total: **95** files.

### A.3 Frontend files to delete (pages, components, services, types, tests)

#### R1 — 10 files

- `warehouse/frontend/src/app/dashboard/warehouse/outbound/awb-pools/` — `page.tsx`
- `warehouse/frontend/src/components/whAwbPool/` — `WhAwbClaimModal.tsx`, `WhAwbPoolViewModal.tsx`, `WhAwbPoolModal.tsx`, `WhAwbNumberVoidModal.tsx`, `WhAwbPoolFilter.tsx`, `WhAwbPoolManagementTable.tsx`, `WhAwbPoolAddBlockModal.tsx`
- `warehouse/frontend/src/services/api/` — `whAwbPoolApi.ts`
- `warehouse/frontend/src/types/` — `whAwbPool.ts`

#### R2 — 10 files

- `warehouse/frontend/src/app/dashboard/warehouse/outbound/ndr/` — `page.tsx`
- `warehouse/frontend/src/components/whShipmentNdr/` — `WhShipmentNdrManagementTable.tsx`, `WhShipmentNdrViewModal.tsx`, `WhNdrBulkResultModal.tsx`, `WhNdrAcknowledgeModal.tsx`, `WhShipmentNdrFilter.tsx`, `WhNdrResponseModal.tsx`, `WhShipmentNdrModal.tsx`
- `warehouse/frontend/src/services/api/` — `whShipmentNdrApi.ts`
- `warehouse/frontend/src/types/` — `whShipmentNdr.ts`

#### R3 — 8 files

- `warehouse/frontend/src/app/dashboard/warehouse/outbound/cod-remittances/` — `page.tsx`
- `warehouse/frontend/src/components/whCodRemittance/` — `WhCodRemittanceFilter.tsx`, `WhCodRemittanceViewModal.tsx`, `WhCodRemittanceModal.tsx`, `WhCodAgeingModal.tsx`, `WhCodRemittanceManagementTable.tsx`
- `warehouse/frontend/src/services/api/` — `whCodRemittanceApi.ts`
- `warehouse/frontend/src/types/` — `whCodRemittance.ts`

#### R4 — 26 files

- `warehouse/frontend/src/app/dashboard/warehouse/outbound/channel-accounts/` — `page.tsx`
- `warehouse/frontend/src/app/dashboard/warehouse/outbound/channel-imports/` — `page.tsx`
- `warehouse/frontend/src/app/dashboard/warehouse/outbound/publish-rules/` — `page.tsx`
- `warehouse/frontend/src/components/whChannelAccount/` — `WhChannelAccountViewModal.tsx`, `WhChannelAccountManagementTable.tsx`, `WhChannelAccountSitesModal.tsx`, `WhChannelAccountModal.tsx`, `WhChannelAccountFilter.tsx`
- `warehouse/frontend/src/components/whChannelOrderImport/` — `WhChannelOrderImportFilter.tsx`, `WhChannelOrderImportViewModal.tsx`, `WhChannelOrderImportManagementTable.tsx`
- `warehouse/frontend/src/components/whChannelPublishRule/` — `WhChannelPublishRuleManagementTable.tsx`, `WhChannelPublishRuleViewModal.tsx`, `WhChannelPublishRuleFilter.tsx`, `WhChannelPublishRunModal.tsx`, `WhChannelPublishRuleModal.tsx`
- `warehouse/frontend/src/components/whChannelPublishLog/` — `WhChannelPublishLogViewModal.tsx`, `WhChannelPublishLogTable.tsx`, `WhChannelPublishLogAcknowledgeModal.tsx`
- `warehouse/frontend/src/services/api/` — `whChannelAccountApi.ts`, `whChannelOrderImportApi.ts`, `whChannelPublishRuleApi.ts`
- `warehouse/frontend/src/types/` — `whChannelAccount.ts`, `whChannelOrderImport.ts`, `whChannelPublishRule.ts`
- `warehouse/frontend/src/__tests__/` — `whChannelPublishRunReferences.test.tsx`

#### R5 — 12 files

- `warehouse/frontend/src/app/(public)/` — `layout.tsx`
- `warehouse/frontend/src/app/(public)/track/[token]/` — `page.tsx`
- `warehouse/frontend/src/app/dashboard/warehouse/outbound/tracking-links/` — `page.tsx`
- `warehouse/frontend/src/components/whTrackingLink/` — `WhTrackingLinkModal.tsx`, `WhTrackingLinkManagementTable.tsx`, `WhTrackingLinkNotificationRulesModal.tsx`, `WhTrackingLinkFilter.tsx`, `WhTrackingLinkUrlModal.tsx`, `WhTrackingLinkRevokeModal.tsx`, `WhTrackingLinkViewModal.tsx`
- `warehouse/frontend/src/services/api/` — `whTrackingLinkApi.ts`
- `warehouse/frontend/src/types/` — `whTrackingLink.ts`

#### R6 — 7 files

- `warehouse/frontend/src/app/dashboard/warehouse/inbound/marketplace-claims/` — `page.tsx`
- `warehouse/frontend/src/components/whMarketplaceClaim/` — `WhMarketplaceClaimManagementTable.tsx`, `WhMarketplaceClaimSubmitModal.tsx`, `WhMarketplaceClaimFilter.tsx`, `WhMarketplaceClaimViewModal.tsx`
- `warehouse/frontend/src/services/api/` — `whMarketplaceClaimApi.ts`
- `warehouse/frontend/src/types/` — `whMarketplaceClaim.ts`

#### R7 — 7 files

- `warehouse/frontend/src/app/dashboard/warehouse/outbound/rto/` — `page.tsx`
- `warehouse/frontend/src/components/whRtoConsignment/` — `WhRtoConsignmentFilter.tsx`, `WhRtoConsignmentManagementTable.tsx`, `WhRtoConsignmentModal.tsx`, `WhRtoConsignmentViewModal.tsx`
- `warehouse/frontend/src/services/api/` — `whRtoConsignmentApi.ts`
- `warehouse/frontend/src/types/` — `whRtoConsignment.ts`

#### R8 — 14 files

- `warehouse/frontend/src/app/dashboard/warehouse/outbound/serviceability/` — `page.tsx`
- `warehouse/frontend/src/app/dashboard/warehouse/outbound/rate-quotes/` — `page.tsx`
- `warehouse/frontend/src/components/whCarrierServiceability/` — `WhCarrierServiceabilityFilter.tsx`, `WhCarrierServiceabilityManagementTable.tsx`, `WhCarrierServiceabilityViewModal.tsx`, `WhCarrierServiceabilityModal.tsx`
- `warehouse/frontend/src/components/whRateQuote/` — `WhRateQuoteFilter.tsx`, `WhRateQuoteViewModal.tsx`, `WhRateQuoteManagementTable.tsx`, `WhRateShopModal.tsx`
- `warehouse/frontend/src/services/api/` — `whCarrierServiceabilityApi.ts`, `whRateQuoteApi.ts`
- `warehouse/frontend/src/types/` — `whCarrierServiceability.ts`, `whRateQuote.ts`

#### D1 — 8 files

- `warehouse/frontend/src/app/dashboard/warehouse/inbound/obsolescence-returns/` — `page.tsx`
- `warehouse/frontend/src/components/whObsolescenceReturn/` — `WhObsolescenceReturnManagementTable.tsx`, `WhObsolescenceReturnModal.tsx`, `WhObsolescenceReturnFilter.tsx`, `WhObsolescenceReturnViewModal.tsx`
- `warehouse/frontend/src/services/api/` — `whObsolescenceReturnApi.ts`
- `warehouse/frontend/src/types/` — `whObsolescenceReturn.ts`
- `warehouse/frontend/src/__tests__/` — `whObsolescenceReturnKeptUnitCost.test.tsx`

#### D2 — 10 files

- `warehouse/frontend/src/app/dashboard/warehouse/outbound/trade-portal/` — `page.tsx`
- `warehouse/frontend/src/components/whTradePortal/` — `WhTradePortalUserFilter.tsx`, `WhTradePortalUserManagementTable.tsx`, `WhTradePortalRecordViewModal.tsx`, `WhTradePortalUserViewModal.tsx`, `WhTradePortalCustomerPortal.tsx`, `WhTradePortalUserModal.tsx`, `WhTradePortalOrderModal.tsx`
- `warehouse/frontend/src/services/api/` — `whTradePortalApi.ts`
- `warehouse/frontend/src/types/` — `whTradePortal.ts`

#### D3 — 28 files

- `warehouse/frontend/src/app/dashboard/warehouse/reports/coexistence/` — `page.tsx`
- `warehouse/frontend/src/app/dashboard/warehouse/reports/consolidated-valuation/` — `page.tsx`
- `warehouse/frontend/src/components/whCoexistence/` — `WhCoexistenceManagementTable.tsx`, `WhCoexistenceViewModal.tsx`, `WhCoexistenceFilter.tsx`, `WhCoexistenceReadinessBanner.tsx`
- `warehouse/frontend/src/components/whConsolidatedValuation/` — `WhConsolidatedValuationManagementTable.tsx`, `WhConsolidatedValuationViewModal.tsx`, `WhConsolidatedValuationFilter.tsx`
- `warehouse/frontend/src/services/api/` — `whCoexistenceApi.ts`, `whConsolidatedValuationApi.ts`
- `warehouse/frontend/src/types/` — `whCoexistence.ts`, `whConsolidatedValuation.ts`
- `warehouse/frontend/src/components/common/` — `WhInventorySeparationNotice.tsx`
- `warehouse-base/frontend/src/app/dashboard/warehouse/platform/external-snapshots/` — `page.tsx`
- `warehouse-base/frontend/src/app/dashboard/warehouse/masters/category-ownership/` — `page.tsx`
- `warehouse-base/frontend/src/types/` — `whbExternalStockSnapshot.ts`, `whbCategoryStockingOwnership.ts`
- `warehouse-base/frontend/src/services/api/` — `whbCategoryStockingOwnershipApi.ts`, `whbExternalStockSnapshotApi.ts`
- `warehouse-base/frontend/src/components/warehouseCatalogues/` — `WhbExternalStockSnapshotFilter.tsx`, `WhbExternalStockSnapshotManagementTable.tsx`, `WhbExternalStockSnapshotViewModal.tsx`, `WhbCategoryStockingOwnershipEndModal.tsx`, `WhbCategoryStockingOwnershipFilter.tsx`, `WhbCategoryStockingOwnershipManagementTable.tsx`, `WhbCategoryStockingOwnershipModal.tsx`, `WhbCategoryStockingOwnershipViewModal.tsx`

Frontend total: **140** files.

---

### A.4 Kept files edited for residue (R30 `CP-CODE-*`, file:line in `classic` @ `65b41be8a6`)

Kept files, not deletes. Each line is mandatory in its task; a `P7-13` gate failure on one is fixed in the task named here (`§6`). Re-read the line before editing (numbers drift by 1–10).

| R30 | File:line | Edit | Task |
|---|---|---|---|
| `CP-CODE-001` BLOCKER | `LGX/V910031__logix_wh_outbound.sql:37-46` | drop `supports_cod` from the `wh_carrier_services` column list and `v.cod` from every value row (fresh logix install fails otherwise) | `P7-03` |
| `CP-CODE-002` | `WB/V500001:51` · `WB/V500002:41` · `W/V510101:319` · `IN/V540000:33` · `IN/V541000:165` | reword the adapter / Parts Counter / Workshop Parts comments (GATE-6) | `P7-10` |
| `CP-CODE-003` | `warehouseBase.json:7878` `help.sourceSystems.overview` (en, fr, hi) + `warehouseBaseHelp.ts:2898` fallback | describe the post-`P7` source systems (no dealer, services, field-service or assets adapter rows) | `P7-10` |
| `CP-CODE-003` | `warehouse-base/frontend/src/__tests__/warehouseMobileDecisionGate.test.ts:773,800,813` (GATE 3 fixtures; `:813` is the anti-false-positive case) and `:781-783` (pins `INSTALL.md` §16) | update the fixtures with the new wording; co-edit the §16 pin with `P7-12` | `P7-10`, `P7-12` |
| `CP-CODE-004` | `warehouseBase.json` `outboxEvent.eventTypeByCode.channel` (nested, en/fr/hi) | delete the subtree; `jq` proof in acceptance | `P7-04` |
| `CP-CODE-005` | `warehouseBase.json` `reasonCode.byCode.{CUSTOMER_REFUSED,ADDRESS_INCOMPLETE,PREMISES_CLOSED,COD_NOT_READY,FUTURE_DELIVERY_REQUESTED,CARRIER_REPORTED}` | delete (seeded only by deleted `W/V510206`) | `P7-03` |
| `CP-CODE-005` | `warehouseBase.json` `reasonCode.byCode.CARRIER_REJECTED` | delete (seeded only by deleted `W/V510205`) | `P7-02` |
| `CP-CODE-006` | `warehouse/frontend/src/types/whCarrierService.ts:19,35,44,52` (incl. `supportsCodCount`) · `components/whCarrierService/WhCarrierServiceFilter.tsx:26,126,128` · i18n `carrierService.statistics.supportsCod` · `W/V510044:417` comment · `help.carrierServices.{flow1,flow2,purposeDescription}` COD prose | drop the field / filter / label; reword the prose | `P7-03` |
| `CP-CODE-007` | `shipment.hints.trackingEvents`, `help.shipmentDetail.{flow3,rule3}`, `help.carriers.{flow2,rule3}` (tracking link) · `WhShipmentTrackingEventRepositoryCustom:59` (NDR) · `WhWorkingCalendarService:43,248` (NDR response clock) | reword | `P7-03` |
| `CP-CODE-007` | `WhOrderEditRuleValidationService:50,82` ("the answer is a return or an RTO" — user-facing) · `rma.placeholders.externalRef` (marketplace) · `WhEvidencePhotoStore:22` · `W/V511294:26` · 3PL `Wh3plBillableEventVocabulary:15` | reword ("the answer is a return") | `P7-05` |
| `CP-CODE-007` | `help.supplierClaims.flow1`, `supplierClaim.hints.headerExplainer` (obsolescence return) | reword | `P7-07` |
| `CP-CODE-007` | `WhbItemIdentifier:88` ("Set for a marketplace listing") | reword | `P7-10` |
| `CP-CODE-008` | `WarehouseBaseModuleConfig:28-29` javadoc · `WarehousePrintDataProvider:12` · `WhPrintRenderer:27` · `WhHoldQueryService:284` · `whHold.ts:15` · `WhHold.java:35` (cites `dealer/V20735`) · `WhbCompanyOptionResponse:11` · `WhbItemSiteSetting:27` · `WB/V500048:57` · `W/V510090:493` · `WarehouseDocumentDisplayRegistryTest:87-155` (`dealerSalesOrderResolver` / `PDI_JOB` fixtures → a neutral resolver name) | reword the dealer persona / adapter residue | `P7-10` |
| `CP-CODE-008` | `NonFunctionalFoundationsTest:169` + `warehouse-base/INSTALL.md:2177` ("20,000 ledger rows per day (dealer parts department)") | change together to the `FR-534` envelope wording (no dealer sizing row) | `P7-10` (test), `P7-12` (INSTALL) |
| `CP-CODE-009` | `BATCH-WAREHOUSE-{P1,P4,P6}.md`, `WAVE-STATE-WAREHOUSE-P4.md` (one removed-feature hit each) · `shared/scripts/ci-gate/20-warehouse.def:792-794` (comment for the deleted `WhbOwnerScopeResolverCustomerPersonaTest`) | superseded note / prune | `P7-12` |
| `CP-GA-010` | `W/V510040` `wh_demand_order_lines.original_item_id` + `WhDemandOrderLine.java:135-136` + the read in `WhDemandOrderRepositoryCustomImpl:132` | drop the column in the clean rewrite (`RN-052`); it has no writer since the dealer counter is gone | `P7-04` |

**User decisions, not edits (R30):** `CP-CODE-010` (the logix outbound demo stays a D2C dataset — rename the `d2c` flag to a neutral *parcel* flag, or re-seed it as B2B distributor orders; a re-seed is new scope) and `CP-CODE-011` (base item types `CORE`, `TYRE` and demand type `JOB_ISSUE` — default **keep all three**, optionally reword `CORE`'s description; a removal would be `P7-10`). Both are in `RETARGET-PROGRAM-STATUS.md` pending items.

## Appendix B — migrations

`WB` = `warehouse-base/backend/src/main/resources/db/migration`, `W` = `warehouse/…`, `IN` = `warehouse-india/…`, `LGX` = `platform/backend/src/main/resources/db/client/logix`.
Line numbers are at `65b41be8a6`. **Re-read each file immediately before editing it.** Line numbers drift as earlier tasks strip lines from the same file.
`warehouse-3pl` has no migration to change. Its only hits are `CARTON` noise in `V530020` and `V530030`.

### B.1 Whole-file deletes (20)

| File | Feature | Task |
|---|---|---|
| `W/V510205` AWB pools/numbers (+`AWB_VOID` reasons, 7 perms, grid) | R1 | `P7-02` |
| `W/V511277` AWB USED backfill + COD matched-once in a remittance | R1/R3 | `P7-02` (it UPDATEs `wh_awb_numbers`, so it goes with `V510205`) |
| `W/V510206` NDR (+ NDR/RTO reasons, `wh_carriers.ndr_*` columns) | R2 | `P7-03` |
| `W/V510207` COD remittances (+ `COD` series, `wh_carriers.cod_remittance_days`) | R3 | `P7-03` |
| `W/V510209` tracking links / notification rules / notifications | R5 | `P7-03` |
| `W/V511274` NDR and COD leaves + `wh_tracking_notifications.attempt_no` | R2/R3/R5 | `P7-03` |
| `W/V511276` RTO reason `CARRIER_INITIATED` + COD matched-once | R3/D5 | `P7-03` |
| `W/V510208` channel accounts / imports / publish rules / logs + `channel.inventory.published` | R4 | `P7-04` |
| `W/V510225` publish-log filters | R4 | `P7-04` |
| `W/V510226` `CHANNEL_PUBLISH_RUN` doc type | R4 | `P7-04` |
| `W/V511304` publish-log grid column drop | R4 | `P7-04` |
| `W/V510215` marketplace claims (+ code list, 2 settings, leaf) | R6 | `P7-05` |
| `W/V511270` OBR site-scoped number | D1 | `P7-07` |
| `W/V510221` trade portal users | D2 | `P7-08` |
| `W/V511209` trade portal perms, role, L1 `warehouse_trade`, grid | D2 | `P7-08` |
| `W/V511239` trade portal permission dependencies | D2 | `P7-08` |
| `WB/V500053` category stocking ownership + external stock snapshots | D3 | `P7-09` |
| `W/V511249` coexistence report seed | D3 | `P7-09` |
| `W/V511262` consolidated valuation seed | D3 | `P7-09` |
| `WB/V501117` `ADAPTER_*` reserved flag | D4/D5 | `P7-10` |

**Refuted:** `WB/V500054` stays, because it only creates the generic `whb_activity_history` view.

### B.2 Mixed files to rewrite

"FAILS" = the statement errors on a fresh install once the object is absent, so the edit is mandatory in the same task.

| File | Strip / edit | Task |
|---|---|---|
| `W/V510204` | strip §1 `wh_carrier_serviceability` `:59-124`, §3 `wh_rate_quotes` `:222-313`, perms/deps/grants `:315-385`, bundle grants `:426-433`, grids/filters `:436-506`, verification `:514-531,539-609`, round-trip `:620-660`; **keep** `:56`, §2 account scopes `:125-221`, `:388-424`, `:532-538`, `:661-688`; header `:1-53`, NOTICE `:610` | `P7-02` |
| `W/V510227` | `:32` keep `wh_carrier_status_mappings:import`, drop `wh_carrier_serviceability:import`; title `:2` | `P7-02` |
| `W/V511000` | `:294-296` drop `wh_carrier_serviceability`, `wh_awb_pools`; `:407-409` drop `wh_tracking_links:notify` | `P7-02` / `P7-03` |
| `W/V511275` | strip §3 `:97-135` (AWB live index + guard, FAILS) and `:148-150`; header `:12-13,23` | `P7-02` |
| `W/V511306` | rate-quote parts (`P7-02`); NDR/COD parts `:65-67,80-99,107-109,115-117,147-219,227-240,249-270,276-277,285-293,301-302,309-310,318-319` (`P7-03`); keep the tracking-events re-key | `P7-02`, `P7-03` |
| `W/V511308` | strip rate-quote account code `:67,94-99,121-138,151,161,204-207,218-220,227,238-239`; keep the labels/pickups/manifests/handovers re-key | `P7-02` |
| `W/V510203` | CHECK lists `:80-82`, `:151-153` drop `NDR`, `RTO_INITIATED`, `RTO_IN_TRANSIT`, `RTO_DELIVERED` (`REM-D4`) | `P7-03` |
| `W/V510044` | `supports_cod` `:112`, grid `:358,393`, filter `:360,431`, verify `:458` (`OD-22` default) | `P7-03` |
| `W/V510040` | drop `:99` `channel_account_id`, `:125` `payment_mode`, `:127` `cod_amount`, CHECKs `:150-154`, COMMENT `:206-208`, uk `:217-218`, verification `:746,749,786-788`, comments `:31,70-72,98,667-668,710`; **keep** `:97` `channel_id`, `:172-173`, `:221` | `P7-04` |
| `W/V510100` | `:142` wave-criterion CHECK drops `'PAYMENT_MODE'` | `P7-04` |
| `WB/V500010` | `:438` `CHANNEL_ORDER_ID` + guard `:522` (`P7-04`); `RETURN_TYPE` `RTO` `:155`, `MARKETPLACE` `:161` + assertion `:810-813` → 8 (`P7-05`); `CHANNEL_KIND` `:165-167` (keep `:168` B2B), `MARKETPLACE_LISTING` `:200` (`P7-10`); `OEM_PART_NUMBER` `:201` → `MANUFACTURER_PART_NUMBER` (`P7-11`) | `P7-04`, `P7-05`, `P7-10`, `P7-11` |
| `W/V510050` | strip §4 `wh_rto_consignments` `:507-551`, perms `:585-589`, IN-lists `:597,608,616,622,629,639,648,670-671`, leaf `:706-708`, translations `:724-726`, IN-lists `:735,744,757`, grid `:777-780,823-836,861-864`, verification `:898-901,925,935,982,994,1000,1013,1023,1038`, NOTICE `:1069`; `RETURN_TYPE` assertion `:944-947` → 8; comments `:1-80,101` | `P7-05` |
| `W/V511235` | drop `wh_rto_consignments` from IN-lists `:45,80,101,103`; header `:1`, NOTICE `:109` | `P7-05` |
| `W/V511248` | strip `:154` (RTO re-parent); `:76` Returns description; **`:298-299` expected leaves 45 → 44 (FAILS)**; D4 comments `:33-34,39-42,121` (`P7-10`) | `P7-05`, `P7-10` |
| `W/V511268` | marketplace leaf `:127-129` + translations + IN-lists (`P7-05`); obsolescence leaf `:124-126` + translations + IN-lists `:213,230,243-244,367,384` (`P7-07`); leaf check `:273-276`; **`:300-306` Returns count 8 → 6 (`P7-05`) → 5 (`P7-07`)**, **`:371-372` translations 24 → 21 → 18** (FAILS); comments `:30-36,45-48`, NOTICE `:393-396` | `P7-05`, `P7-07` |
| `W/V511271` | strip the tracking-links leaf `:94-96`, translations `:126-128`, IN-lists `:145-146,173-174`, verification row `:205`, translation count `:257` 21 → 18 (`P7-03`, **FAILS** at `:214-223` otherwise); strip the channel accounts/imports/publish-rules leaves `:82-90`, their translations, IN-lists and verification rows `:201-203`, translation count 18 → 9 (`P7-04`, **FAILS** otherwise); then rewrite L1 `warehouse_channels` → `warehouse_shipping`, L2 `warehouse_channels_fulfilment` → `warehouse_shipping_planning`; keep cross-dock `:91-93`; verification `:187-278` re-derived (`P7-06`) (`R29` F1) | `P7-03`, `P7-04`, `P7-06` |
| `W/V511272` | working calendars `:58-60`, `:128-136,142` re-parented to `warehouse_shipping_planning` | `P7-06` |
| `W/V511273` | strip the rate-quote, serviceability and AWB-pool leaves `:72-80` + translations `:101-109` + IN-lists `:125-126,153-154` + checks `:182-184`, translation count `:235` 18 → 9 (`P7-02`, **FAILS** at `:194-202` otherwise); then drop L2 `warehouse_channels_carriers`, re-home tracking events `:66-68` and status mappings `:69-71` to `warehouse_shipping_planning`; verification `:167-176` re-derived (`P7-06`) (`R29` F1) | `P7-02`, `P7-06` |
| `W/V510210` | strip §2 `:179-311`, §3 OBR `:312-321`, perms `:333-341`, IN-lists `:349,366,372,379,389,398`, grants `:403-426`, settings `:428-445`, leaf `:464-466`, translations `:480-482`, IN-lists `:492,505,514`, grid `:530-538,566-585,600-605`, verification lines listed in `inv-migrations` §2, NOTICE `:806-807`; **keep return gradings** | `P7-07` |
| `W/V510216` | strip §4 `:403-459` (FAILS), retirement `:567-590`, trigger arm `:274-275`, verification `:805-827,862-864` (FAILS); comments `:79-90,107,109` | `P7-07` |
| `WB/V500014` | drop `is_dual_eligible` `:80,114,124`, seed column `:134` and values; its grid column/filter rows | `P7-09` |
| `IN/V540130` | `:252,261` drop `is_dual_eligible` from the `whb_item_categories` inserts | `P7-09` |
| `WB/V500046` | strip `:217-232`, `:388-391` (guarded FK onto snapshots); comment `:11` | `P7-09` |
| `WB/V501000` | `:65`, `:67` drop the two D3 resources (4 generated perms) | `P7-09` |
| `WB/V501002` | `:154` drop `whb_category_stocking_ownership`; keep `whb_channels` | `P7-09` |
| `WB/V501101` | `:159`, `:189` drop the two D3 leaves; **keep `:158` `warehouse_channels` (L3 master)** | `P7-09` |
| `WB/V500002` | drop `ADAPTER_*` `:157-160`, `ACCESSORIES` `:164-165` (+COMMENT `:169-171`, header `:141-149`), `JOB_CARD` `:184`, `POS_SHIFT` `:192`; guard lists `:215-216,228-229`; **verification `:468-470` (FAILS)**; **count floors `:461` `v_sources < 9` → 4 and `:464` `v_documents < 13` → 11 (FAILS, `R29` F4)**; NOTICE `:487`; comment `:82` | `P7-10` |
| `WB/V500003` | `RTO_RECEIPT_REVERSAL` `:190`, `RTO_RECEIPT` `:224`, list `:246`, guard `:263`; **count floors `:429` `v_forward < 18` and `:432` `v_reversal < 18` → 17 each, with their messages (FAILS, `R29` F4)**; comment `:65` | `P7-10` |
| `WB/V500004` | RTO reasons `:154-157`, NDR reasons `:158-161`, guard `:190-191`; **count floor `:342` `v_contexts < 11` → 9, with its message (FAILS, `R29` F4)**; "eleven contexts" header comments `:12,107` → "nine"; comment `:109-110` | `P7-10` |
| `WB/V500084` | `:72-73` RTO_RECEIPT reason_context UPDATE, `:83` list; comment `:42` | `P7-10` |
| `W/V511208` | D4 comment `:63-71` | `P7-10` |
| `W/V510011` + `W/V510021` | `chk_wh_purchase_orders_order_source` `'VOR'` → `'LINE_STOP'` (`:127-128`); assertion `V510021:89-104` | `P7-11` |
| `WB/V500012` | `:199` `WORKSHOP` → `PRODUCTION_STORE`, name `Production store / shop floor`; guard `:212` | `P7-11` |
| `W/V511211` + `W/V511241` | `wh_rpt_parts_kpis` → `wh_rpt_stock_kpis` everywhere (perms `:121-124`, grants, leaf `:268-270` → `warehouse_stock_kpis` `/dashboard/warehouse/reports/stock-kpis`, translations `:301-303` → *Stock KPIs* / *Indicateurs de stock* / *स्टॉक केपीआई*, IN-lists, grid `:402-406,513-521,627-633`, verification `:658-664`, description `:235`; `V511241:56,83`) | `P7-11` |
| Comment-only (optional, in the owning task) | `W/V510043:213`, `V510105:378-380`, `V510202:21,196`, `V511265:47`, `V511303:28`, `IN/V540010:433`, `WB/V501110:134`, `WB/V500051:27`, `WB/V500017:49`; **R30 `CP-CODE-002` (GATE-6 hits, mandatory, `P7-10`):** `WB/V500001:51`, `WB/V500002:41`, `W/V510101:319`, `IN/V540000:33`, `IN/V541000:165` | each; the R30 five → `P7-10` |
| `LGX/V910031` | `:24-34` drop `ndr_response_hours`, `ndr_auto_rto_grace_hours`, `cod_remittance_days` (FAILS, `P7-03`); **`:37-46` `INSERT INTO wh_carrier_services (…, supports_cod, …)` — drop the `supports_cod` column from the column list and the `v.cod` value from every `VALUES` row (FAILS, `P7-03`, R30 `CP-CODE-001`)**; `:433,448-449` `payment_mode`/`cod_amount` (`P7-04`) | `P7-03`, `P7-04` |
| `LGX/V910032`, `LGX/V910033` | `:96`, `:306` `payment_mode` | `P7-04` |
| `LGX/V910021` | `:139` `COD` series (`P7-03`), `:141` `OBR` series (`P7-07`) | `P7-03`, `P7-07` |

**Fresh-install hazards that must be fixed in the same task as their cause:** `V511248:298`, `V511268:304`, `V511268:371`, `V500010:811`, `V510050:945`, `V500002:461` (9 → 4), `V500002:464` (13 → 11), `V500002:468-470`, `V500003:429` (18 → 17), `V500003:432` (18 → 17), `V500004:342` (11 → 9) (`R29` F4), `V511273:194-202` (`P7-02`) and `V511271:214-223` (`P7-03`, `P7-04`) (`R29` F1), `V510216:403-459` and `:809-827`, `V511275:97-150`, `V511306`, `V511308`, `V511272:58-60`, `V511273:167-176`, `LGX/V910031:24-34`, `LGX/V910031:37-46` (`supports_cod`, `P7-03`, R30 `CP-CODE-001`).

## Appendix C — seams in kept code

| Kept file | Cut | Task |
|---|---|---|
| `WhbCategoryStockingOwnershipQueryService:139-151` + `…Repository:132-147` | **relocate** the stocking-category picker to `WhbItemCategoryQueryService` and `WhbItemCategoryRepository`; repoint `WhbAllocationStrategyService:24,81,91,100,166`, `WhbGlPostingRuleService:22,61,70,77,86`, `WhbValuationPolicyService:17,62,70,76,85` and the tests `WhbGlPostingRuleServiceTest:20,89`, `WhbValuationPolicyServiceTest:23,112` | `P7-01` |
| `types/whObsolescenceReturn.ts:110-114` `WhClaimTransitionData` | **relocate** it to `types/whSupplierClaim.ts`; repoint `supplier-claims/page.tsx:36` and `WhClaimTransitionModal.tsx:19` | `P7-01` |
| `WhObsolescenceReturnValidationService:123` `lineValue` | **relocate** to `WhSupplierClaimValidationService`; repoint `WhSupplierClaimService:321,516` and `WhSupplierClaimQueryService:427` | `P7-01` |
| `WhDemandOrderValidationService:11,153` codec | **inline** a private SHA-256 hex helper (`HexFormat` over `MessageDigest` SHA-256 of UTF-8, byte-identical) | `P7-01` |
| `WhShipmentService` | AWB `:25,106,131,151,282-287,343-345,376,493-499` (`P7-02`); notifier `:19,32,110,133,153,384,534` (`P7-03`); RTO `:21,108,132,152,469` (`P7-05`) | `P7-02`, `P7-03`, `P7-05` |
| `WhShipmentValidationService` | `:230-249` `requireTrackingMatchesClaimedAwb` (`P7-02`); `:251-270` drop `rtoBegun` (`P7-05`) | `P7-02`, `P7-05` |
| `WhTrackingEventIngestService` | `:15,17,92-93,103-104,110-111,182-184,192-194`; docs `:46-52,59,80-81` | `P7-03` |
| `WhReturnReceiptService` | `:26,88-89,104,106,119,121,337-340,509-510` | `P7-05` |
| `WhCarrierRepositoryCustomImpl:212-214` (+ `…Custom:47-51`, `WhCarrierQueryService:170,178`) | drop the `wh_rate_quotes` term (`P7-02`) and the `wh_shipment_ndrs` and `wh_cod_remittances` terms (`P7-03`) | `P7-02`, `P7-03` |
| `WhCarrierAccountRepositoryCustom(Impl):52,202-213`, `WhCarrierAccountQueryService:173,176` | delete `countRateQuotesForAccount` | `P7-02` |
| `WhCarrierServiceLevelRepositoryCustom(Impl):43,187-199`, `WhCarrierServiceLevelQueryService:161-167` | delete `countRateQuotesForServiceCode` | `P7-02` |
| `WhCarrierConnector:28-51` | trim to `owningModule()` (`REM-D13`) | `P7-02` |
| `WhCarrierConnectorRegistryTest:85-91` (`defaultConnectorOffersNothing` calls `rate(null)`/`fetchAwbBlock(null)`), doc `:22` | delete that one method; keep the registration, duplicate-owner and unavailable tests; reword the doc (`R29` F2) | `P7-02` |
| `WhCarrierIntegrationJobConfiguration` | AWB bean `:20` (`P7-02`); delete the file (`P7-03`) | `P7-02`, `P7-03` |
| `WhReturnsJobConfiguration` | marketplace bean `:3,32-35` (`P7-05`); obsolescence beans `:4-5,117-125` (`P7-07`) | `P7-05`, `P7-07` |
| `WhCarrier:61,106-118`, `WhCarrierRequest`, `WhCarrierResponse`, `WhCarrierService`, `WhCarrierMapper:69-71` | drop the 3 clock fields | `P7-03` |
| `WhCarrierStatusMapping:57-60,70`, `WhShipmentTrackingEventStatisticsResponse:25-26`, `…RepositoryCustomImpl:60`, `…QueryService:154` | drop the NDR/RTO statuses and the `ndr` stat | `P7-03` |
| `WhDemandOrder:111-115,162-164,284-290`, `WhDemandOrderRequest:106,110,211-215`, `…Response:84-85,189-193,283-284`, `…Mapper:114-115`, `…ValidationService:51-53,142,203-216,236`, `WhDemandOrderService:1085,1108`, `…QueryService:362`, `WhWaveCriteria:51`, `WhWaveQueryService:182`, `WhWaveValidationService:173`, `WhCarrierShipmentFactsReader:18-19,31,48` | drop payment mode, COD amount and channel account (`REM-D1`) | `P7-04` |
| `CacheConfiguration.java:781,783` (platform) | drop `dropdown.whChannelAccount` and `dropdown.whChannelPublishRule` | `P7-04` |
| `WhTradePortalService.redact():336-337` (`setPaymentMode(null)`, `setCodAmount(null)`), `WhTradePortalServiceScopeTest:258,265` | delete the two lines and the test's builder call and assert, so the tree compiles before `P7-08` deletes the portal (`R29` F3) | `P7-04` |
| `WhSupplierClaim:31,72,76-77,81,83-84`, `WhSupplierClaimService:19,23,29,84,87,96-110,230,392-393,413-418,434,445-460`, `…QueryService:16,22,30,141,154,166,317,375-388`, `…ValidationService:101-107`, `…Mapper:26,55-56`, `…RepositoryCustomImpl:101,103`, `…Response:28-29,118-122,249-250` | drop the obsolescence type and source | `P7-07` |
| `WhbOwnerScopeResolver:64-67,84,97-110,285-380,445-476`; `WhDemandOrderService:278-287`; `WhDemandOrderQueryService:215-265`; `WhDemandOrderExportService:44,56-71,100-101`; `WhPrintJobService:219-231`; `WhPrintJobQueryService:186-196`; `WhShipmentQueryService:227-236` | drop the customer persona | `P7-08` |
| `WhValuationRepositoryCustomImpl:207-208,266` | return the WS-222 members to private and drop their docs | `P7-09` |
| `WhbItemCategory` + 10 files (`REM-D7`) | drop `isDualEligible` | `P7-09` |
| `WarehouseBaseModuleConfig:53` | cut the dealer and services adapter terms | `P7-10` |
| `WarehouseBaseCouplingTest` `ReservedAccessoriesRule` (`:39,1678-1680,1838-1872,2174-2178,2498-2526`) and the anti-vacuous anchor `:2195`; `warehouseRegistryOpenness.test.ts:957`, `wh3plRegistryOpenness.test.ts:977`, `whinRegistryOpenness.test.ts:1035` | retire the rule; swap each `ACCESSORIES` anchor for the kept base row `LOGISTICS`; the band ratchet stays (`R29` F5) | `P7-10` |
| Install-health tests `WhInstallHealthIntegrationTest:79-82`, `Wh3plInstallHealthIntegrationTest:67-70`, `WhinUpgradeAndActivationIntegrationTest:86-89`, `WhbBaseOnlyInstallHealthIntegrationTest:75-76`; doc `WhPermissionAdversarialFixture:51` | drop `Warehouse Trade Customer` and the `V511209` citation, all four modules (`R29` F8) | `P7-08` |
| Orphan comments naming deleted classes (`R29` F7): `WhWorkingCalendar{Controller:49,RepositoryCustomImpl:21,ExportService:19,Mapper:17,ValidationService:28}`, `WhCarrierAccountScope{Controller:29,Service:38,ValidationService:17}`, `WhDemandOrderRepository:131` (`P7-04`); `WhShipmentTrackingEventMapper:14`, 3PL `Wh3plArAccountingSink:12` (`P7-03`); `WhCarrierConnectorRegistryTest:22`, India `WhinDeliveryChallanIssueIntegrationTest:104` (`P7-02`); `warehouse-base/docs/contracts/outbox.contract.md:254` (`P7-12`) | reword without the deleted name | as listed |
| `WhCarrierServiceLevel*` `supports_cod` beyond entity/DTO/mapper/export/filter: `…StatisticsResponse:18,33-34`, `…RepositoryCustomImpl:51,122` (stats SQL), `…RepositoryCustom:51`, `…Service:191`, `…Controller:76,167,186-187`, `…ExportService:76,91`, `…QueryService:52` | drop (`OD-22`, `R29` F11) | `P7-03` |
| `WhPurchaseOrder:86`, `WhSupplierLeadTimeQueryService:27,32,41,97` (+ docs) | `VOR` → `LINE_STOP` | `P7-11` |
| Kept **tests**: `WhOwnerScopeContractTest` (entries per feature: `:133,140-144,184,211,231-234,260-261` retail; `:190` D1; `:35,46-47,98,262,295,420-430` D2; `:145,151` D3; `:194-195` N4), `WhWarehouseScopeContractTest:54,58,60,74,80,97-98`, `WhShipmentCarrierLifecycleTest`, `WhTrackingEventIngestServiceTest`, `WhReturnLineDispositionedLifecycleTest:13,17,81-82`, `WhDemandOrderLineUomDefaultTest:3-12,111-135`, `WhCarrierPartyReferenceIntegrationTest` (16 methods), `WhSupplierClaimLadderTest:11-21,247-249,274-295`, `WhCostBearingResponseContractTest:29,58,122-123`, `WhDownloadScopeAdversarialIntegrationTest:37-38,88-115`, `WarehouseBaseCouplingTest:1304-1305,1369-1383,1416-1433,1462,1468-1480`, `ExportServiceContractTest:179,182`, `WhKpiDenominatorReconciliationTest`, `WhReportsComputeFromLedgerTest`, `WhLedgerLineBound(Benchmark)IntegrationTest`, `WhStockAgeingFullHistoryIntegrationTest`, `WhValuationPolicyPrecedenceIntegrationTest:64,123,224-226,370-390`, `WhbPortReferenceResolverClaimabilityTest:34,48`, `WhbStockLedgerWriterIntegrationTest:123`, `WhSupplierLeadTimeQueryServiceTest`, `WhStockToGlLedgerEffectIntegrationTest` | trim per owning task | each |
| Frontend: `whCostColumnVisibility.test.tsx:17-24,66-71,163-187`; `WhSupplierClaimModal.tsx:75,149,560,602`; `WhClaimTransitionModal.tsx` comments; `WhCarrierModal.tsx:47-80,85,154-159,273-275,305-307,337,471-519`; `WhCarrierViewModal.tsx:61,137-150`; `types/whCarrier.ts:28-33,49-51`; `WhShipmentTransitionModal.tsx:137,195`; tracking-events page `~442-448` + `types/whTrackingEvent.ts:62` + `whTrackingEventApi.ts:16`; `WhDemandOrderModal.tsx:86-87,124-125,164,382-383,437-441,543-548,618-619,1027-1042`, `types/whDemandOrder.ts:108-109,187-188,280`, `whDemandOrderApi.ts:82`, `orders/[demandOrderId]/page.tsx:354-357`; `WhRmaModal.tsx:691`; `whReturnReceiptApi.ts:90`; base tests `whModalSubmitRefusal`, `warehouseRegistryOpenness:628-629,745`, `warehouseMobileDecisionGate:42,116-121,670-688,942-944,1012-1014`, `whbRegistryLabelFallback:145`, `whbCatalogueModalPlaceholders:67`, `whDateOnlyRender:67-71`; `wh3plRegistryOpenness:743`, `whinRegistryOpenness:798` | trim per owning task | each |

## Appendix D — seeded rows and removed objects

### D.1 Tables absent after `P7` (24)
`wh_awb_pools`, `wh_awb_numbers`, `wh_shipment_ndrs`, `wh_ndr_actions`, `wh_cod_remittances`, `wh_cod_remittance_lines`, `wh_channel_accounts`, `wh_channel_account_warehouses`,
`wh_channel_order_imports`, `wh_channel_publish_rules`, `wh_channel_publish_rule_stock_statuses`, `wh_channel_publish_logs`, `wh_tracking_links`, `wh_tracking_notification_rules`,
`wh_tracking_notifications`, `wh_marketplace_claims`, `wh_rto_consignments`, `wh_carrier_serviceability`, `wh_rate_quotes`, `wh_obsolescence_returns`, `wh_obsolescence_return_lines`,
`wh_trade_portal_users`, `whb_category_stocking_ownership`, `whb_external_stock_snapshots`.

### D.2 Permissions absent (103 live rows)
`wh_awb_pools` (7) · `wh_carrier_serviceability` (6 incl. `:import`) · `wh_channel_accounts` (6) · `wh_channel_order_imports` (6) · `wh_channel_publish_rules` (8) ·
`wh_cod_remittances` (7) · `wh_marketplace_claims` (7) · `wh_obsolescence_returns` (8 live) · `wh_rate_quotes` (5) · `wh_rto_consignments` (5) · `wh_shipment_ndrs` (6) ·
`wh_tracking_links` (7) · `wh_trade_portal` (2) · `wh_trade_portal_users` (5) · `wh_rpt_coexistence` (4) · `wh_rpt_consolidated_valuation` (4) ·
`whb_category_stocking_ownership` (4 + 2 generated) · `whb_external_stock_snapshots` (2 + 2 generated). **Renamed:** `wh_rpt_parts_kpis:*` (4) → `wh_rpt_stock_kpis:*`.
They have role grants to ADMIN, AUDITOR (view tiers), ADMIN_GROUP, the Warehouse Storekeeper/Supervisor/Stock Controller/Manager/Finance Controller bundles and Branch Admin, plus their `permission_dependencies`. **Role removed:** `Warehouse Trade Customer`.

### D.3 Menus absent
Leaves (all under `/dashboard/warehouse`):
- `outbound/`: `rto`, `channel-accounts`, `channel-imports`, `publish-rules`, `tracking-links`, `rate-quotes`, `serviceability`, `awb-pools`, `ndr`, `cod-remittances`, `trade-portal`
- `inbound/`: `obsolescence-returns`, `marketplace-claims`
- `reports/`: `coexistence`, `consolidated-valuation`
- `masters/category-ownership`, `platform/external-snapshots`

That is 17 leaves. Containers: L1 `warehouse_channels`, L2 `warehouse_channels_fulfilment`, L2 `warehouse_channels_carriers`, L1 `warehouse_trade`, L2 `warehouse_trade_customers`.
**Renamed:** `warehouse_parts_kpis` → `warehouse_stock_kpis`. **Re-homed:** `warehouse_cross_dock_plans`, `warehouse_working_calendars`, `warehouse_tracking_events` and `warehouse_carrier_status_mappings` → `warehouse_shipping_planning`.

### D.4 Grids absent (18)
`wh_awb_pools`, `wh_carrier_serviceability`, `wh_channel_accounts`, `wh_channel_order_imports`, `wh_channel_publish_logs`, `wh_channel_publish_rules`, `wh_cod_remittances`,
`wh_marketplace_claims`, `wh_obsolescence_returns`, `wh_rate_quotes`, `wh_rpt_coexistence`, `wh_rpt_consolidated_valuation`, `wh_rto_consignments`, `wh_shipment_ndrs`,
`wh_tracking_links`, `wh_trade_portal_users`, `whb_category_stocking_ownership`, `whb_external_stock_snapshots`. These held 293 `grid_column_definitions` and 87 `filter_definitions` rows. **Renamed:** `wh_rpt_parts_kpis` → `wh_rpt_stock_kpis`.
**Trimmed:** the `isDualEligible` column/filter on the item-categories grid, and `supportsCod` on the carrier-services grid (`OD-22`).

### D.5 Catalogue rows absent
- `whb_source_systems`: `ADAPTER_DEALER`, `ADAPTER_SERVICES`, `ADAPTER_FIELD_SERVICE`, `ADAPTER_ASSETS`, `ACCESSORIES`
- `whb_document_types`: `JOB_CARD`, `POS_SHIFT`, `CHANNEL_PUBLISH_RUN`
- `whb_code_lists`: `MARKETPLACE_CLAIM_TYPE` (+4 values)
- `whb_code_list_values`:
  - `RETURN_TYPE`: `RTO`, `MARKETPLACE`
  - `CHANNEL_KIND`: `MARKETPLACE`, `OWN_STORE`, `POS`
  - `IDENTIFIER_TYPE`: `MARKETPLACE_LISTING`
- `whb_attribute_keys`: `CHANNEL_ORDER_ID`
- `whb_movement_types`: `RTO_RECEIPT`, `RTO_RECEIPT_REVERSAL`
- `whb_reason_codes` (23): `V500004` 3 RTO + 3 NDR; `V510205` 5 `AWB_VOID`; `V510206` 9 NDR + 2 RTO; `V511276` `CARRIER_INITIATED`
- `whb_event_types`: `channel.inventory.published`
- `whb_number_series`: `COD`, `OBR`
- `admin_settings`: `warehouse.marketplace_claims.window_days`, `.due_alert_lead_days`, `warehouse.obsolescence_returns.window_warning_lead_days`, `.no_movement_months`
- `wh_tracking_notification_rules`: 8 rows

**Renamed codes:** `VOR` → `LINE_STOP`, `WORKSHOP` → `PRODUCTION_STORE`, `OEM_PART_NUMBER` → `MANUFACTURER_PART_NUMBER`.

**Not catalogue rows:**
- Jobs: `WH_AWB_POOL_TOP_UP`, `WH_NDR_ESCALATION`, `WH_NDR_AUTO_RTO`, `WH_COD_UNREMITTED_AGEING`, `WH_MARKETPLACE_CLAIM_WINDOW`, `WH_OBSOLESCENCE_WINDOW_WARNING` and `WH_OBSOLESCENCE_CANDIDATES` are Java descriptors with no SQL row. Their `@Scheduled` crons are defaults, not set in any yml.
- Outbox: no subscription row is retail.
- Print templates: none is retail (no ZPL or HTML template reads AWB, COD, RTO or NDR data).

## Appendix E — i18n, permission constants, help, filter scopes

**i18n sections deleted (each in en, fr and hi; leaf keys per language):**
- `warehouse.json` (1,655 keys):
  - retail: `awbPool` 121, `shipmentNdr` 139 + `help.ndr` 15, `codRemittance` 120 + `help.codRemittances` 14, `channelAccount` 93, `channelOrderImport` 61, `publishRule` 147, `help.channelAccounts`/`help.channelOrderImports`/`help.publishRules` 42, `trackingLink` 102 + `help.trackingLinks` 13, `marketplaceClaim` 89 + `help.marketplaceClaims` 13, `rtoConsignment` 61 + `help.rto` 13, `carrierServiceability` 69, `rateQuote` 102
  - dealer: `obsolescenceReturn` 130 + `help.obsolescenceReturns` 13, `tradePortal` 108 + `help.tradePortal` 13, `coexistence` 90, `inventorySeparation` 2, `consolidatedValuation` 60, `help.coexistence` 14, `help.consolidatedValuation` 11
- `warehouseBase.json` (102 keys): `categoryStockingOwnership` 58, `externalStockSnapshot` 20, `help.categoryOwnership` 14, `help.externalSnapshots` 10

**Vocabulary keys deleted inside kept sections:**
- `warehouseBase.json`:
  - `sourceSystem.byCode.{ADAPTER_DEALER,ADAPTER_SERVICES,ADAPTER_FIELD_SERVICE,ADAPTER_ASSETS,ACCESSORIES}`
  - `documentType.byCode.{JOB_CARD,POS_SHIFT,CHANNEL_PUBLISH_RUN}`
  - `itemIdentifier.identifierTypeByCode.MARKETPLACE_LISTING`
  - `disposition.returnTypeByCode.{RTO,MARKETPLACE}`
  - `channel.channelKindByCode.{MARKETPLACE,OWN_STORE,POS}`
  - `reasonCode.byCode.NDR_*` (5)
  - `reasonCode.byCode.{CUSTOMER_REFUSED,ADDRESS_INCOMPLETE,PREMISES_CLOSED,COD_NOT_READY,FUTURE_DELIVERY_REQUESTED,CARRIER_REPORTED}` — seeded only by `W/V510206` (`P7-03`, R30 `CP-CODE-005`)
  - `reasonCode.byCode.CARRIER_REJECTED` — seeded only by `W/V510205` (`P7-02`, R30 `CP-CODE-005`). `SHIPMENT_CANCELLED`, `CARRIER_CHANGED` and `LABEL_DAMAGED` are also seeded by kept `W/V510103` / `V510060` and **stay**
  - `reasonCode.byCode.CARRIER_INITIATED` (`:477`; `P7-03`, with `V511276`, `R29` F11)
  - `movementType.byCode.RTO_RECEIPT*` (2)
  - the **nested** subtree `outboxEvent.eventTypeByCode.channel` (it holds only `inventory.published`; R30 `CP-CODE-004` — the key is nested, not the flat `["channel.inventory.published"]` this list once named, so a flat delete is a no-op). Proof: `jq -e '.outboxEvent.eventTypeByCode | has("channel") | not'` on en/fr/hi (`P7-04`)
  - the `isDualEligible` keys
  - text edits: `itemExternalRef.hints.sourceModule`, `help.itemExternalRefs.overview`, `help.channels.*`
- `warehouse.json`:
  - `returnReceipt.returnTypes.{MARKETPLACE,RTO}`
  - `supplierClaim.claimTypes.OBSOLESCENCE`, `supplierClaim.sourceDocumentTypes.OBSOLESCENCE_RETURN`
  - 8 carrier clock keys
  - `carrierService.statistics.supportsCod` and the COD prose in `help.carrierServices.{flow1,flow2,purposeDescription}` (`P7-03`, R30 `CP-CODE-006`)
  - `trackingEvent.statistics.ndr`
  - `demandOrder.fields.{paymentMode,codAmount}`, `demandOrder.paymentModes.*`, and the wave-criterion label `PAYMENT_MODE` (`:5219`) (`P7-04`, `R29` F11)
  - `carrierStatusMapping`/`trackingEvent` `normalisedStatuses.{NDR,RTO_*}` (8)
  - `carrierService.*supportsCod`

**Kept:** `warehouse.claim`, `kpis.metrics.OBSOLESCENCE`, `metricInfo.kpi.obsolescence`, `carrierAccount.paymentModes`, `carrier.values.manualAwb`.

**i18n renamed:**
- `purchaseOrder.orderSources.VOR` → `.LINE_STOP`: en *Line stop / machine down*, fr *Arrêt de ligne / machine à l'arrêt*, hi *लाइन स्टॉप / मशीन बंद*
- `warehouse.warehouseTypeByCode.WORKSHOP` → `.PRODUCTION_STORE`: en *Production store / shop floor*, fr *Magasin de production / atelier*, hi *उत्पादन स्टोर / शॉप फ़्लोर*
- `itemIdentifier.identifierTypeByCode.OEM_PART_NUMBER` → `.MANUFACTURER_PART_NUMBER`: en *Manufacturer part no.*, fr *Référence fabricant*, hi *निर्माता पार्ट नंबर*
- `partsKpis` (82) + `help.partsKpis` (17) → `stockKpis` / `help.stockKpis`, with the titles, empty text, overview and `help.kpis.rule5` reworded from *parts* to *stock*

**Permission constants:**
- `warehouse/frontend/src/constants/warehousePermissions.ts`: delete `RTO_CONSIGNMENTS` 418-423, `SHIPMENT_NDRS` 424-430, `COD_REMITTANCES` 431-438, `RATE_QUOTES` 494-499, `CARRIER_SERVICEABILITY` 500-508, `AWB_POOLS` 509-518, `RPT_COEXISTENCE` 778-797, `RPT_CONSOLIDATED_VALUATION` 814-821, `OBSOLESCENCE_RETURNS` 1014-1025, `MARKETPLACE_CLAIMS` 1026-1033, `CHANNEL_ACCOUNTS` 1052-1062, `CHANNEL_ORDER_IMPORTS` 1063-1069, `CHANNEL_PUBLISH_RULES` 1070-1084, `TRACKING_LINKS` 1085-1092, `TRADE_PORTAL_USERS` 1120-1130, `TRADE_PORTAL` 1131-1138
- same file: rename `RPT_PARTS_KPIS` 751-777 → `RPT_STOCK_KPIS`
- `warehouseBasePermissions.ts`: delete `CATEGORY_STOCKING_OWNERSHIP` 433-439, `EXTERNAL_STOCK_SNAPSHOTS` 440-444

**Help config:**
- `warehouse/frontend/src/config/warehouseHelp.ts`: delete `consolidatedValuation` 98-130, `obsolescenceReturns` 1545-1586, `marketplaceClaims` 1703-1744, `rto` 2323-2358, `ndr` 2359-2402, `codRemittances` 2403-2446, `coexistence` 2793-2836, `channelAccounts` 3929-3972, `channelOrderImports` 3973-4014, `publishRules` 4015-4060, `trackingLinks` 4061-4102, `rateQuotes` 4187-4228, `carrierServiceability` 4229-4268, `awbPools` 4269-4308, `tradePortal` 4395-4436
- same file: rename `partsKpis` 3176-3223 (fix `kpis` rule5 `:3079`); reword the carriers and shipments entries
- `warehouseBaseHelp.ts`: delete `categoryOwnership` 3306-3349, `externalSnapshots` 4567-4599; reword `channels`

**`platform/frontend/src/utils/filterUtils.ts`:**
- delete 17 scopes: `WAREHOUSE_CATEGORY_STOCKING_OWNERSHIP` 1272-1277, `WAREHOUSE_EXTERNAL_STOCK_SNAPSHOT` 1279-1284, `WAREHOUSE_RPT_COEXISTENCE` 1826-1849, `WAREHOUSE_TRADE_PORTAL_USER` 1882-1885, `WAREHOUSE_RATE_QUOTE` 1921-1926, `WAREHOUSE_CARRIER_SERVICEABILITY` 1927-1932, `WAREHOUSE_AWB_POOL` 1933-1937, `WAREHOUSE_CHANNEL_ACCOUNT` 1949-1952, `WAREHOUSE_CHANNEL_ORDER_IMPORT` 1959-1964, `WAREHOUSE_CHANNEL_PUBLISH_RULE` 1965-1969, `WAREHOUSE_TRACKING_LINK` 1970-1974, `WAREHOUSE_RTO` 2079-2087, `WAREHOUSE_NDR` 2088-2094, `WAREHOUSE_COD_REMITTANCE` 2095-2101, `WAREHOUSE_OBSOLESCENCE_RETURN` 2246-2252, `WAREHOUSE_MARKETPLACE_CLAIM` 2254-2261, `WAREHOUSE_RPT_CONSOLIDATED_VALUATION` 2658-2666
- rename `WAREHOUSE_RPT_PARTS_KPI` 1803-1825 → `WAREHOUSE_RPT_STOCK_KPI`
- drop `isDualEligible` 1014-1021
- delete the 7 scopes of the adapters removed on 2026-09-21 (`R29` F9, `FR-493`): `WAREHOUSE_DEALER_COUNTER_SALE` 1983, `WAREHOUSE_DEALER_ITEM_PRICE` 1993, `WAREHOUSE_DEALER_PRICE_LEVEL` 2002, `WAREHOUSE_SERVICES_MATERIAL_REQUEST` 2010, `WAREHOUSE_SERVICES_JOB_PART_ISSUE` 2019, `WAREHOUSE_SERVICES_FITTED_SERIAL` 2029, `WAREHOUSE_DEALER_VEHICLE_FITMENT` 2106 (`P7-10`; GATE-6 now scans this file)
- `supportsCod` in the carrier-service scope (`OD-22`)

## Appendix F — docs, QA, contracts, CI in `classic`

| Path | Action | Task |
|---|---|---|
| `warehouse-base/docs/QA/Category Stocking Ownership.md` | delete | `P7-09` |
| `warehouse/docs/contracts/shipment-carrier-lifecycle.contract.md` | rewrite: remove the AWB-pool, NDR and RTO guards and transitions; keep tracking, delivery and cancel | `P7-12` |
| `warehouse/docs/contracts/order-flow-retry.contract.md:24,54,116` | remove the trade-portal rows | `P7-12` |
| `warehouse-base/INSTALL.md` (38 hits: `:198,236,240,254,277,293,865,1096,1532-1850,2059-2102,2204-2291`) | section edits | `P7-12` |
| `warehouse-base/docs/DATED-OBLIGATION-REGISTER.md:56-58,70-72,142-154` | remove the obligations | `P7-12` |
| `warehouse-base/docs/QA/{Channels,Source Systems,Reason Codes,Item Categories,Document & Reference Types,Attribute Keys}.md` | neutral redaction of each removed code (distinct values kept distinguishable) + one top `D-16` note; counts, verdicts and evidence unchanged; no section deleted (`OD-1`, 2026-10-24) | `P7-12` |
| `warehouse-base/docs/contracts/import-batch.contract.md:300`; `warehouse-3pl/docs/contracts/billing-cycle.contract.md:124` (`OD-24`) | line edits | `P7-12` |
| `warehouse/docs/QA/Warehouse Testing Resume.md:42,43,59,83,130` | drop the D3 QA links | `P7-12` |
| `.claude/testing/reports/warehouse-p2-12-returns.report.md` | RTO section note | `P7-12` |
| `.claude/tasks/BATCH-WAREHOUSE-{P5,FINDINGS,P2,P3,P2-IN,P01-CONTINUE}.md`, `WAVE-STATE-WAREHOUSE-P5.md` | one superseded note each (`REM-D17`) | `P7-12` |
| `shared/scripts/ci-gate/20-warehouse.def:64` | `WhPartsKpiFillRateDenominatorTest` → `WhStockKpiFillRateDenominatorTest` | `P7-11` |
| `shared/scripts/ci-gate/20-warehouse.def` comment ledger (`:88,169-170,648,652-653,795-833,885-952,1042,1086,1197,1219,1614-1618,1643-1653,1839,1852,1943`) | prune the deleted test classes | `P7-12` |
| `.claude/testing/descriptors/`: delete `wh-awb-pools`, `wh-serviceability`, `wh-rate-quotes` (`P7-02`); `wh-ndr`, `wh-cod-remittances`, `wh-tracking-links`, trim `supportsCod` in `wh-carrier-services` (`P7-03`); `wh-channel-accounts`, `wh-channel-imports`, `wh-publish-rules` (`P7-04`); `wh-marketplace-claims`, `wh-rto`, link in `wh-returns:11` (`P7-05`); `wh-obsolescence-returns` (`P7-07`); `wh-rpt-coexistence`, `wh-rpt-consolidated-valuation`, `whb-category-ownership`, `whb-external-snapshots`, trim `isDualEligible` in `whb-item-categories`, link in `wh-rpt-count-variance:12` (`P7-09`); rename `wh-rpt-parts-kpis` → `wh-rpt-stock-kpis` (`P7-11`) (all `.json`) | delete / trim / rename (`R29` F10) | each; `P7-12` checks the folder |
| `warehouse-issues/docs/IRREVERSIBLE.md` IRR-28 and §5 rows 1, 2, 3, 6, 13 | `D-16` notes with the post-`P7` seed sets — **done in the design set by `R29` F14**; `P7-12` checks every classic seed comment that cites §5 quotes the new number | `P7-12` |
| `CLAUDE.md` `WarehouseAdapterDealerSafeTranslation.tsx` (non-existent file) | **report to the user, do not edit** | `P7-12` |

## R29 dispositions

Review [`R29-functional-review-rem.md`](../reviews/R29-functional-review-rem.md) (2026-10-22): 17 findings, **all fixed**. Each fix was re-verified against `classic` @ `65b41be8a6`. No gate was weakened and no scope was deleted.

| Finding | What changed | Where |
|---|---|---|
| **F1** BLOCKER | Each deleting task now strips its own `V511271`/`V511273` leaves, translations, IN-lists and verification counts (`V511273` 18 → 9 in `P7-02`; `V511271` 21 → 18 in `P7-03`, → 9 in `P7-04`). `P7-06` keeps only the L1/L2 rename and the four re-homes | `P7-02`, `P7-03`, `P7-04`, `P7-06`; EPIC order note and traps; Appendix B.2 `V511271`/`V511273` rows; hazard list |
| **F2** BLOCKER | `WhCarrierConnectorRegistryTest`: delete `defaultConnectorOffersNothing` (`:85-91`), keep the other tests, reword `:22` | `P7-02` kept tests; Appendix C |
| **F3** BLOCKER | `P7-04` cuts `WhTradePortalService.redact():336-337` and `WhTradePortalServiceScopeTest:258,265`, so its tree compiles before `P7-08` | `P7-04` seams; `P7-08` note; EPIC order note; Appendix C |
| **F4** BLOCKER | The five count floors are added with their new numbers: `V500002:461` 9 → 4, `:464` 13 → 11, `V500003:429,432` 18 → 17, `V500004:342` 11 → 9, plus the "eleven contexts" comments | `P7-10` scope table and traps; Appendix B.2 rows; hazard list; EPIC traps |
| **F5** BLOCKER | `ReservedAccessoriesRule` retired; the `ACCESSORIES` anti-vacuous anchors in `WarehouseBaseCouplingTest:2195` and the three registry-openness tests become `LOGISTICS`. The band ratchet stays | `P7-10` (labels now include 3PL and India); Appendix C |
| **F6** MAJOR | `$P` narrowed to `db/client/logix`; GATE-3 anchored to demand-order and wave payment tokens (`\bPAYMENT_MODE\b`, `DO_PAYMENT_MODE`, `PAYMENT_(PREPAID|COD)`, `WhDemandOrder.PAYMENT_MODES`), which spares the kept carrier-account constants; `V500200` and the band-ratchet file are named exceptions | §2 `REM-D19`; §6 scopes, GATE-3, GATE-6 and the exceptions sentence; `P7-04` acceptance |
| **F7** MAJOR | Per-task gates run over `$T` (four modules, docs and `*.md` excluded; later renames left out); the full gate set runs only in `P7-13`. Each of the 14 orphan comments is assigned to the task that deletes the class it names | §6 "Per-task gates"; acceptance of `P7-02`…`P7-11`; `P7-10` GATE-3 drops `OEM_PART_NUMBER`; orphan lines in `P7-02`, `P7-03`, `P7-04`, `P7-12`; Appendix C |
| **F8** MAJOR | `P7-08` drops `Warehouse Trade Customer` and the `V511209` citation from the install-health tests of all four modules and from `WhPermissionAdversarialFixture:51`, and adds a pass criterion | `P7-08` (labels include 3PL and India); Appendix C |
| **F9** MAJOR | The 7 dead `WAREHOUSE_DEALER_*`/`WAREHOUSE_SERVICES_*` scopes are cut; GATE-6 now scans `filterUtils.ts` for `WAREHOUSE_(DEALER|SERVICES)_|whad_|whas_`; the `whad_`/`whas_` comment remnants, including `IN/V541000:38`, are reworded | `P7-10`; §1 platform files; `FR-493`; §6 GATE-6; Appendix E |
| **F10** MAJOR | Each feature task deletes, renames or trims its own tester descriptors and adds `.claude/testing/descriptors` to its grep; `P7-12` checks the folder is clean | `P7-02`, `P7-03`, `P7-04`, `P7-05`, `P7-07`, `P7-09`, `P7-11`, `P7-12`; Appendix F |
| **F11** MINOR | The remaining `supports_cod` sites are named (stat tile, stats SQL, `trackChanges`, controller params, export, query); the `PAYMENT_MODE` wave label (×3) is added to `P7-04`; `reasonCode.byCode.CARRIER_INITIATED` goes to `P7-03` with `V511276` | `P7-03`, `P7-04`; Appendix C and E |
| **F12** MINOR | `WH-SC-669` and `P7-04` now say the body is **ignored** (`JacksonConfig.java:73` disables `FAIL_ON_UNKNOWN_PROPERTIES`) and the fingerprint is unchanged | §5 `WH-SC-669`; `P7-04` rules |
| **F13** MINOR | One owner per FR: `FR-483` → `P7-03` (the reviewer proposed `P7-04`; `P7-03` is kept because the SPINE-owned `IMPLEMENTATION-PLAN.md` §2 assigns it there, and the contradiction is gone either way), `FR-489` → `P7-02`, `FR-495` → `P7-10`. Other tasks say "contributes to" | §4 owner map; headers and "Requirements closed" of `P7-03`, `P7-04`, `P7-05`, `P7-12` |
| **F14** MINOR | `IRREVERSIBLE.md` IRR-28 and §5 rows 1, 2, 3, 6 and 13 carry `D-16` notes with the post-`P7` seeds. `P7-12` checks that the classic comments citing §5 match | `docs/IRREVERSIBLE.md`; `P7-12`; Appendix F |
| **F15** MINOR | `WH-SC-666` asserts shipment `DISPATCHED` → `DELIVERED` and demand order `SHIPPED` → `DELIVERED`, and names the baseline tests `WhDespatchServiceTest` (`WH-SC-056`) and `WhShipmentConfirmedDispatchIntegrationTest` | §5 `WH-SC-666` |
| **F16** MINOR | The `P7-05` acceptance SQL uses `list_code` (`V500010:70`) and asserts the exact set of 8 codes | `P7-05` acceptance |
| **F17** MINOR | `P8-02` states that `(channel_id, external_order_ref)` uniqueness does not come back. Port dedup is the `(source_module, idempotency_key)` uk plus a partial unique index on the source document. `P7-04`'s trap points to it | `issues/p8-02.md` Rules (one line); `P7-04` traps |

**For the user (not edited, needs approval):** `CLAUDE.md` still lists the non-existent `WarehouseAdapterDealerSafeTranslation.tsx` in its SafeTranslation files line (Appendix F, §7).

## R30 dispositions

R30 completeness audit (2026-10-23, `reviews/R30-completeness-{github-a,github-b,requirements,screens,code}.md`; decisions `DECISIONS.md` `D-17`). Items whose carrier is a `P7` task or this file:

| Finding | What changed | Where |
|---|---|---|
| `CP-CODE-001` BLOCKER | `LGX/V910031:37-46` `supports_cod` named in B.2, the hazard list and A.4 | `P7-03` |
| `CP-CODE-002`…`-009` | every kept-file line named with its task | Appendix A.4, B.2 comment-only row, Appendix E; `P7-02`/`-03`/`-04`/`-05`/`-07`/`-10`/`-12` acceptance |
| `CP-CODE-010`, `-011`, `-013` | user decisions, recorded | A.4 footer; status file |
| `CP-GA-001` | `P7-12` puts the superseded note on `BATCH-WAREHOUSE-P6.md` too and marks `P6-02`/`P6-11`/`P6-12` VOID there; `INSTALL.md:1638` | `P7-12` |
| `CP-GA-002`, `CP-GA-014`, `CP-GA-015`, `CP-GB-014` | D-16 / D-17 headers added to the task and finding files; `--sync` and `CREATED.md` regeneration before the P7 batch | `P7-12` acceptance; `issues/p0-13`, `p2-10`, `p2-15`, `p6-02`, `p6-12`, `finding-w59`, `finding-w63` |
| `CP-GA-009` | drop-ship stays core | `REM-D20` |
| `CP-GA-010` | `original_item_id` dropped | A.4; `P7-04` |
| `CP-GA-011` | `INSTALL.md` §16 offer boundary amended for `P10` planning / routings; `P6-02` VOID | `P7-12` |
| `CP-GA-012` | `MPR-OPEN-18` narrowed in the clean rewrite | `P7-13` |
| `CP-GB-009` | the dated live FIFO check re-created after the rebuild | `P7-13` |
| `CP-GB-015` | dependency lines | `P7-02`, `P7-08` |
| `CP-FR-014` | `REM-D19` exceptions named in `P7-13`; `REM-D8` cited by every removing task; `REM-D18` cited | `P7-03`/`-05`/`-07`/`-09`/`-11`/`-13` |
| `CP-SC-002` (P7 side) | `WH-SC-662` scoped to the P7-exit install; the key is retired | `REM-D21`; `P7-08` |
| `CP-SC-004`, `-007`, `-008` | `BUILD-SPEC-SCREENS.md` index, routes and §0.8 corrected in the design set; `P7-13` re-checks | `BUILD-SPEC-SCREENS.md`; `P7-13` |
