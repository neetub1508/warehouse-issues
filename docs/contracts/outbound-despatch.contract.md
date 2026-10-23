# Functional Contract — Outbound: demand order → wave → pick → pack → ship → confirm delivery

> **What this is.** The functional truth for every stock that leaves a site on a demand: one demand model for
> every demand type, the six quantity columns, holds and the edit-after-release matrix, fulfilment policy,
> release and waves, discrete pick to a real staging location, the short pick, the pack session and cartons,
> the shipment → consignment → manifest chain with handovers and pickup requests, carrier masters, labels with
> a void path, tracking events with data-held mappings, dispatch as the only relief event, delivery
> confirmation, the de-stage path on a late cancel, and the drop-shipment. Every rule row names its
> requirement in **Source** (`DECISIONS.md` `D-17` item 1).
>
> **What this is not.** Reservations and allocation are [`reservation-allocation.contract.md`](reservation-allocation.contract.md);
> the transfer's own ladder is [`stock-transfer.contract.md`](stock-transfer.contract.md); the task ladder that
> pick tasks ride is [`task-execution-printing.contract.md`](task-execution-printing.contract.md); every
> movement posts through [`movement-post-reverse.contract.md`](movement-post-reverse.contract.md) `MPR-T1-01`.
> Removed by `D-16` item 2 and not covered: order intake from external sales platforms, pooled tracking numbers,
> delivery-exception workflows, payment collection on delivery, public tracking pages.
>
> **Status.** Derived 2026-10-23 (v0) from `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.11 (`FR-177`…`FR-191`,
> `FR-193`, `FR-194`, `FR-196`…`FR-199`, `FR-206`, `FR-207`) and `FR-447`, `FR-449`, `FR-467`, checked against the
> built code in `classic` by name. `FR-192` is **DEFERRED by `D-17`** and not covered. Not ratified.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Demand order: create → allocate → release (holds clear) → pick (to staging) → pack (session, cartons) → ship (shipment loaded → dispatched) → delivered; cancel with de-stage · Wave (v1.1): create → release N orders · Manifest / handover / pickup request as three objects · Label void · Tracking event ingestion · Drop-shipment (v2, `OD-18`) |
| **Module** | `warehouse` (`wh_`), over `warehouse-base` (reservations, tasks, channels, writer) |
| **Domain baseline** | `L-1`, `L-2`, `L-10`; `FR-436`; `D-16` item 2 (B2B channel only; generic shipping stays in core); `OD-18` (drop-shipment) |
| **Owning tasks** | `issues/p2-08.md` (demand model) · `issues/p2-09.md` (pick, dispatch) · `issues/p2-10.md` (shipments, carriers) · `issues/p2-11.md` (cartons, evidence) · `issues/p3-06.md` (waves) · `issues/p3-07.md` (pack session) · `issues/p3-09.md` (manifest, handover, pickup, consignment) · `issues/p3-13.md` (edit matrix, fulfilment policy) · `issues/p5-10.md` (working calendar) · `issues/p5-11.md` (tracking events) · `issues/p5-09.md` (drop-shipment) · `issues/p1-11.md` (channel master) |
| **Code (as built)** | `WhDemandOrderService`, `WhDemandOrderValidationService`, `WhDemandOrderQuantityRules`, `WhWaveService`, `WhPickTaskWriter`, `WhDespatchService`, `WhPackSessionService`, `WhCartonService`, `WhShipmentService`, `WhConsignmentService`, `WhManifestService`, `WhHandoverService`, `WhPickupRequestService`, `WhShippingLabelService`, `WhShipmentTrackingEventService`, `WhCarrierStatusRederiveService`, `WhCarrierConnectorRegistry`, `WhOrderEditRuleService`, `WhOrderAmendmentRecorder`, `WhFulfilmentPolicyService`, `WhBackorderHorizonSweeper`, `WhWorkingCalendarService`, `WhDropShipService` |
| **Routes** | WS-099 / WS-100 Demand Orders · WS-101 Waves · WS-102 Pick Tasks · WS-103 Pack Sessions · WS-104 Cartons · WS-105 / WS-106 Shipments · WS-107 Carriers · WS-108 Carrier Services · WS-109 Carrier Accounts · WS-110 Manifests · WS-111 Handovers · WS-112 Pickup Requests · WS-113 Consignments · WS-114 Shipping Labels · WS-115 Tracking Events · WS-116 Carrier Status Mappings · WS-127 Working Calendars · WS-128 Order Edit Rules · WS-257 Fulfilment Policies |
| **Contract version** | `v0 — 2026-10-23` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Reachable via | Exits via | Kind | Source |
|---|---|---|---|---|---|---|
| Demand order | `OPEN` → `ALLOCATED` → `RELEASED` → `PICKING` → `PACKED` → `SHIPPED` → `DELIVERED` | `wh_demand_orders.status` | `ODS-T1-01`…`-08` | as §1.2 | active; `DELIVERED` terminal | `FR-177`, `FR-447` |
| Demand order | `CANCELLED` | `status`; reason | `ODS-T1-09` | none | **terminal** | `FR-171`, `FR-449` |
| Wave | `OPEN` → `RELEASED` → `PICKING` → `PICKED` → `PACKED` → `SHIPPED`; `CANCELLED` | `wh_waves.status` | `ODS-T1-10`, `-11` | — | v1.1 | `FR-187` |
| Pack session | `IN_PROGRESS` → `COMPLETED`; `CANCELLED` | `status` | `ODS-T1-13`…`-15` | — | v1.1 | `FR-190` |
| Carton | `OPEN` → `SEALED`; `VOID` | `status` | `ODS-T1-14` | — | active | `FR-191` |
| Shipment | `OPEN` → `LOADED` → `DISPATCHED` → `DELIVERED`; `CANCELLED` | `wh_shipments.status` | `ODS-T1-16`…`-19` | — | active | `FR-193`, `FR-447` |
| Manifest · Handover · Pickup request | `OPEN`→`CLOSED` · `PREPARED`→`HANDED_OVER` · `REQUESTED`→`CONFIRMED`→`COMPLETED`; each `CANCELLED` | their `status` | `ODS-T1-20`…`-22` | — | three objects | `FR-194` |
| Shipping label | live → voided | `voided_at`, void reason, carrier void reference | `ODS-T1-23` | none | record | `FR-197` |

### 1.2 Transitions

| ID | From | Event / action | To | Guard | Actor (permission) | Side effects | Source |
|---|---|---|---|---|---|---|---|
| ODS-T1-01 | — | Create a demand order of any demand type | `OPEN` | `ODS-GRD-01`, `-02`, `-19` | `wh_demand_orders:create` | one header for sales, transfer, work order, replenishment, VAS, sample, scrap, job issue, vendor return | `FR-177`, `FR-178`, `FR-180` |
| ODS-T1-02 | `OPEN` | Allocate | `ALLOCATED` | `RSA-GRD-*` | `wh_demand_orders:allocate` | `SOFT` reservations (`RSA-T1-01`) | `FR-177` |
| ODS-T1-03 | `OPEN` · `ALLOCATED` | Place / release an order hold | unchanged | `ODS-GRD-03` | `wh_demand_orders:hold` | a hold record per hold type | `FR-182` |
| ODS-T1-04 | `ALLOCATED` | **Release** (v1: on the demand header; v1.1: N orders through a wave) | `RELEASED` | `ODS-GRD-03`, `-05` | `wh_demand_orders:release` | reservations soft → hard (`RSA-T1-04`); one pick task per pick line | `FR-169`, `FR-187`, `FR-212` |
| ODS-T1-05 | `RELEASED` · `PICKING` | Complete a pick task (discrete pick in v1) | `PICKING` | `ODS-GRD-07` | `wh_pick_tasks:complete` | `ODS-T4-02` | `FR-186`, `FR-188` |
| ODS-T1-06 | `RELEASED` · `PICKING` | **Short pick** | `PICKING` | `ODS-GRD-06` | `wh_pick_tasks:complete` / `wh_demand_orders:short_pick` | `ODS-T4-04` | `FR-185` |
| ODS-T1-07 | `PICKING` | Pack complete | `PACKED` | `ODS-GRD-09`, `-10` | `wh_pack_sessions:complete` | sealed cartons with contents | `FR-190`, `FR-191` |
| ODS-T1-08 | `PACKED` / `PICKING` | Shipment dispatched | `SHIPPED` | `ODS-GRD-08` | `wh_shipments:dispatch` | `ODS-T4-03` | `FR-188`, `FR-189` |
| ODS-T1-09 | any not terminal | Cancel (whole order or a line quantity) | `CANCELLED` | `ODS-GRD-17` | `wh_demand_orders:cancel` | `ODS-T4-06`, `RSA-T4-02` | `FR-171`, `FR-449` |
| ODS-T1-10 | — | Create a wave over allocated orders | wave `OPEN` | `ODS-GRD-20` | `wh_waves:create` | — | `FR-187` |
| ODS-T1-11 | wave `OPEN` | Release the wave | wave `RELEASED`; each order `ODS-T1-04` | `ODS-GRD-20` | `wh_waves:release` | the same Release action on N orders | `FR-187` |
| ODS-T1-12 | `RELEASED` and after | Edit an order after release | unchanged, or as the matrix compensates | `ODS-GRD-04` | `wh_demand_orders:edit_after_release` | `ODS-T4-05` | `FR-183` |
| ODS-T1-13 | — | Start a pack session | `IN_PROGRESS`; the first carton auto-created | `ODS-GRD-09` | `wh_pack_sessions:create` | one active carton | `FR-190` |
| ODS-T1-14 | carton `OPEN` | Scan (quantity on scan; repeat scans merge into the pack line) / Seal | carton `SEALED`; the next carton auto-created only while units remain | `ODS-GRD-09`, `-10` | `wh_pack_sessions:create` / `wh_cartons:seal` | pack evidence `ODS-T4-10` | `FR-190`, `FR-191`, `FR-206` |
| ODS-T1-15 | `IN_PROGRESS` | Complete (× 1) / Cancel | `COMPLETED` / `CANCELLED` | `ODS-GRD-09` | `wh_pack_sessions:{complete,cancel}` | — | `FR-190` |
| ODS-T1-16 | — | Create a shipment for picked orders; optionally one consignment | shipment `OPEN` | `ODS-GRD-11`, `-12` | `wh_shipments:create` · `wh_consignments:create` | `wh_shipment_orders` rows | `FR-179`, `FR-193`, `FR-196` |
| ODS-T1-17 | shipment `OPEN` | Load | `LOADED` | `ODS-GRD-08` (sealed cartons only) | `wh_shipments:edit` | — | `FR-190`, `FR-191` |
| ODS-T1-18 | shipment `LOADED` | Dispatch | `DISPATCHED` | `ODS-GRD-08` | `wh_shipments:dispatch` | `ODS-T4-03` | `FR-188`, `FR-189` |
| ODS-T1-19 | shipment `DISPATCHED` | **Confirm delivery** (date-time, optional proof document, optional receiver name) | `DELIVERED`; order `DELIVERED` | `ODS-GRD-16` | `wh_shipments:confirm_delivery` | `ODS-T4-07` | `FR-447` |
| ODS-T1-20 | — / `OPEN` | Manifest create / close | `OPEN` / `CLOSED` | `ODS-GRD-13` | `wh_manifests:{create,close,cancel}` | the carrier's signed consignment / tracking-number list | `FR-194` |
| ODS-T1-21 | `PREPARED` | Hand over (who, when, signature) | `HANDED_OVER` | `ODS-GRD-13` | `wh_handovers:hand_over` | our record that N shipments left | `FR-194` |
| ODS-T1-22 | `REQUESTED` | Confirm / complete a pickup request (vehicle window) | `CONFIRMED` / `COMPLETED` | — | `wh_pickup_requests:confirm` | — | `FR-194` |
| ODS-T1-23 | live label | Void | voided | `ODS-GRD-14` | `wh_shipping_labels:void` | label kept, `voided_at` | `FR-197` |
| ODS-T1-24 | — | Record a drop-shipment confirmation (v2) | — (a movement) | `ODS-GRD-18` | `wh_demand_orders:drop_ship` / `:drop_ship_reverse` | `ODS-T4-09` | `FR-467` |

### 1.3 Guards

| ID | Predicate (must hold to proceed) | Refusal: code · field | Message shape | Source |
|---|---|---|---|---|
| ODS-GRD-01 | The demand type is a registered `DEMAND_TYPE` row; type-specific extras sit in adapter tables keyed to the header, never in a parallel order | `DO_DEMAND_TYPE_UNKNOWN` · `demandType` | names the type | `FR-177` |
| ODS-GRD-02 | Each line keeps six independent quantities — ordered, allocated, picked, shipped, cancelled, backordered; a partial cancel or amend moves only its own column | `DO_AMEND_QUANTITY_INVALID`, `DO_QUANTITY_EXCEEDS` · `lines[n].quantity` | names the column | `FR-178` |
| ODS-GRD-03 | An order releases to picking only with **zero open holds** whose type `blocks_pick` / `blocks_allocation`; the check is a query, not a status | `DO_RELEASE_HELD`; `WAVE_ORDER_HELD`, `PICK_HELD`, `SHIPMENT_HELD`, `DESPATCH_HELD` | names the hold | `FR-182` |
| ODS-GRD-04 | An edit after release is allowed only where the seeded matrix row (from-status × edit type) allows it, by its required permission, running its compensating actions (release reservation, cancel pick task, reprint pick list, void label, unpack, reverse movements); after ship there is no edit — the answer is a return | `ORDER_EDIT_NOT_ALLOWED`, `ORDER_EDIT_RULE_MISSING`, `ORDER_EDIT_TYPE_NOT_SUPPORTED`; `DO_NOT_EDITABLE` | names the rule row | `FR-183` |
| ODS-GRD-05 | The fulfilment policy (ship complete · ship partial and backorder · ship partial and cancel) resolves per owner and per customer; a release below the minimum fill percentage is refused | `MIN_FILL_NOT_MET`; `DO_POLICY_UNKNOWN` | names fill and minimum | `FR-184` |
| ODS-GRD-06 | A short pick records the shortfall against an exception code; it is never a silently reduced quantity | `DO_EXCEPTION_CODE_UNKNOWN`; a plain Complete of a short line refused `TASK_PICK_USE_SHORT_PICK` | names the line | `FR-185` |
| ODS-GRD-07 | A pick moves stock to a real staging location; the staging lane resolves | `PICK_STAGING_UNRESOLVED`, `PICK_QUANTITY_INVALID`, `PICK_TASK_NOT_OPEN` | names the task | `FR-188` |
| ODS-GRD-08 | Dispatch relieves only staged stock of picked orders, and only sealed cartons load | `DESPATCH_NOTHING_STAGED`, `SHIPMENT_ORDER_NOT_PICKED`, `SHIPMENT_CARTONS_NOT_SEALED` | names the shipment | `FR-188`, `FR-190`, `FR-191` |
| ODS-GRD-09 | A pack session has one active carton; there is no loose packing; a packed lot or serial is one that was picked | `PACK_SESSION_NO_ACTIVE_CARTON`, `PACK_SESSION_ALREADY_OPEN`, `PACK_SESSION_LOT_NOT_PICKED`, `PACK_SESSION_SERIAL_NOT_PICKED`, `PACK_SESSION_NOTHING_TO_PACK` | names the scan | `FR-190` |
| ODS-GRD-10 | A carton is not over-packed, not sealed empty, holds a serial once, and carries the pack evidence its configuration requires | `CARTON_OVERPACK`, `CARTON_EMPTY`, `CARTON_SERIAL_ALREADY_PACKED`, `CARTON_EVIDENCE_REQUIRED` | names the carton | `FR-191`, `FR-206` |
| ODS-GRD-11 | An order rides one shipment; the carrier service and carrier account are valid for the carrier; `owner_id` on the account is nullable, null = the house account | `SHIPMENT_ORDER_ON_OTHER_SHIPMENT`, `SHIPMENT_SERVICE_INVALID`, `SHIPMENT_ACCOUNT_INVALID`, `SHIPMENT_CARRIER_REQUIRED` | names the account | `FR-193`, `FR-196` |
| ODS-GRD-12 | A consignment is 1:1 and optional with its shipment; "add truck" lives on the shipment, so a consignment cannot create a sibling | `CONSIGNMENT_SHIPMENT_TAKEN`, `CONSIGNMENT_SHIPMENT_IMMUTABLE` | names the shipment | `FR-193` |
| ODS-GRD-13 | A shipment on an open manifest is changed only after it is removed from the manifest; a handover names a valid pickup request | `SHIPMENT_ON_OPEN_MANIFEST`; `HANDOVER_PICKUP_REQUEST_INVALID`, `HANDOVER_NOT_EDITABLE` | names the manifest | `FR-194` |
| ODS-GRD-14 | A carton has at most one live label; a void names the carrier's void reference and a reason; a voided label is not voided again | `SHIPPING_LABEL_LIVE_LABEL_EXISTS`, `SHIPPING_LABEL_CARRIER_VOID_REFERENCE_REQUIRED`, `SHIPPING_LABEL_VOIDED` | names the label | `FR-197` |
| ODS-GRD-15 | A tracking event stores raw and normalised status; a raw status with no mapping row is stored `UNMAPPED`, never dropped | — (stored) | — | `FR-198` |
| ODS-GRD-16 | Confirm delivery only a `DISPATCHED` shipment, with a delivery time not before dispatch and not in the future | `SHIPMENT_DELIVERY_DATE_INVALID` · `deliveredAt`; `SHIPMENT_TRANSITION_INVALID` | names both times | `FR-447` |
| ODS-GRD-17 | An order with picked units in staging reaches `CANCELLED` only after the de-stage path posts them back; if they cannot be de-staged the cancel is refused | `409 STAGED_STOCK`; `DO_CANCEL_REASON_REQUIRED` | names the staged quantity | `FR-449` |
| ODS-GRD-18 | A drop-shipment is refused while disabled (default) or when the adapter is unavailable; it names its purchase line and demand line; lot and serial are mandatory for a tracked item | `DROP_SHIP_DISABLED`, `DROP_SHIP_ADAPTER_UNAVAILABLE`, `DROP_SHIP_PO_LINE_INVALID`, `DROP_SHIP_DEMAND_LINE_INVALID`, `DROP_SHIP_LOT_INVALID`, `DROP_SHIP_SERIAL_INVALID`, `DROP_SHIP_QUANTITY_EXCEEDED` | names the line | `FR-467` |
| ODS-GRD-19 | The order's channel, when given, is a `whb_channels` row of the B2B kind | `DO_CHANNEL_UNKNOWN` | names the channel | `FR-207` |
| ODS-GRD-20 | A wave admits only allocated, un-held orders of a supported wave type; v1.1 adds batch pick, other methods are refused | `WAVE_ORDER_NOT_ALLOCATED`, `WAVE_ORDER_HELD`, `WAVE_TYPE_NOT_SUPPORTED`, `WAVE_NO_ORDERS`, `WAVE_NOT_OPEN` | names the order | `FR-186`, `FR-187` |
| ODS-GRD-21 | A carrier connector is an adapter registered in the bean registry and named by `wh_carriers.owning_module`; with none on the classpath `api_enabled` is inert and the manual path stands | — (inert flag) | — | `FR-196` |
| ODS-GRD-22 | **Seals at load and at unload.** The seal applied at load is captured on the outbound handover (`wh_handovers.seal_number`) and, inbound, declared on the ASN (`wh_asns.seal_number`); the seal found at unload is the receiving session's `seal_number_in`; a load-vs-unload difference is surfaced (`sealMismatch`), never silently accepted. The **receiving session owns** the seal, the gate-pass reference, the driver and the arrival photograph | — (captured, compared, shown) | the WS-074 grid shows both seals and the mismatch | `FR-211` |

### 1.4 Transitions that must be unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| ODS-UNR-01 | A transfer or a vendor return with a pick of its own | each creates one demand order (`ODS-T4-01`) | `FR-177` |
| ODS-UNR-02 | Backorder derived from two other quantity columns | `backordered_quantity` is its own column | `FR-178` |
| ODS-UNR-03 | A tracking-number column on the order | tracking lives on shipment / carton / label | `FR-179` |
| ODS-UNR-04 | An order hold as a status value | holds are records (`ODS-GRD-03`) | `FR-182` |
| ODS-UNR-05 | An edit of a shipped order | `ODS-GRD-04` | `FR-183` |
| ODS-UNR-06 | Relief of stock at pick, or by any event other than dispatch | pick is a move to staging; dispatch is the only relief (`ODS-T4-03`) | `FR-188`, `FR-189` |
| ODS-UNR-07 | Loose packing, or loading an unsealed carton | `ODS-GRD-08`, `-09` | `FR-190`, `FR-191` |
| ODS-UNR-08 | Manifest, handover and pickup request merged into one object | three tables and three screens | `FR-194` |
| ODS-UNR-09 | `warehouse` naming a carrier vendor in code | connectors are adapters (`ODS-GRD-21`) | `FR-196` |
| ODS-UNR-10 | Deleting a label | void path only (`ODS-T1-23`) | `FR-197` |
| ODS-UNR-11 | A per-carrier `switch` in Java mapping tracking statuses | mappings are rows (WS-116) | `FR-198` |
| ODS-UNR-12 | An FK from a referencing table to a relocatable object (carriers, tracking events) | referenced by a stable code resolved through a service | `FR-199` |
| ODS-UNR-13 | `delivered_at` or `pod_document_id` written by anything but Confirm delivery in v1 | `ODS-T1-19` is the only writer | `FR-447` |
| ODS-UNR-14 | An order `CANCELLED` with units still in staging | `ODS-GRD-17` | `FR-449` |
| ODS-UNR-15 | A drop-shipment creating a physical stock position | `ODS-T4-09` books virtual `SUPPLIER` → `CUSTOMER` only | `FR-467` |
| ODS-UNR-16 | Channel kinds other than B2B, or channel accounts and connectors | `D-16` item 2 | `FR-207` |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Extra | Source |
|---|---|---|---|---|---|
| ODS-T2-01 | Order create / edit / allocate / release / hold / short pick / cancel | `wh_demand_orders:{create,edit,allocate,release,hold,short_pick,cancel}` | as §1.2 | — | `FR-177`, `FR-182` |
| ODS-T2-02 | Edit after release | `wh_demand_orders:edit_after_release` plus the matrix row's permission | `RELEASED` and after, before ship | — | `FR-183` |
| ODS-T2-03 | Waves; pick tasks; pack sessions; cartons | `wh_waves:*` · `wh_pick_tasks:{edit,complete}` · `wh_pack_sessions:*` · `wh_cartons:{create,seal,capture_evidence}` | as §1.2 | — | `FR-186`, `FR-187`, `FR-190`, `FR-206` |
| ODS-T2-04 | Shipments; confirm delivery | `wh_shipments:{create,edit,dispatch,cancel,confirm_delivery}` | as §1.2 | — | `FR-193`, `FR-447` |
| ODS-T2-05 | Manifests / handovers / pickup requests / consignments / labels | `wh_manifests:*` · `wh_handovers:*` · `wh_pickup_requests:*` · `wh_consignments:*` · `wh_shipping_labels:void` | — | — | `FR-194`, `FR-197` |
| ODS-T2-06 | Carrier masters; status mappings; re-derive | `wh_carriers:*`, `wh_carrier_accounts:*` · `wh_carrier_status_mappings:{create,edit,rederive}` | — | admin | `FR-196`, `FR-198` |
| ODS-T2-07 | Edit rules; fulfilment policies; working calendars | `wh_order_edit_rules:edit` · `wh_fulfilment_policies:*` · `wh_working_calendars:*` | — | admin | `FR-181`, `FR-183`, `FR-184` |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger (clock) | Changes | Notified | Job | Source |
|---|---|---|---|---|---|---|
| ODS-T3-01 | A backordered line past the policy's `backorder_hold_days` / `auto_cancel_after_days` is cancelled by the horizon | the line's backorder date + the policy's days | line cancelled quantity; reservations released | order owner | `WhBackorderHorizonSweeper` | `FR-184`, `FR-165` |
| ODS-T3-02 | A promise (`promised_ship_at`, `promised_deliver_at`) and its breach are both computed by **the same working-calendar code**, layered over the `REGISTERED` branch's platform holidays (read-only), per warehouse and per client | order create / every breach measure | the promise; the breach flag | — | `WhWorkingCalendarService` | `FR-180`, `FR-181` |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| ODS-T4-01 | A transfer is allocated, or a vendor return raised | one demand order of type `TRANSFER` / `VENDOR_RETURN`, reserved, picked and staged by the same path as a sale | `WhDemandOrderService` | `FR-177` |
| ODS-T4-02 | Pick complete | a two-line move source location → staging location; the pick task carries `owner_id`; the hard reservation is consumed or re-attached at the picked grain | `WhPickTaskWriter` | `FR-186`, `FR-188` |
| ODS-T4-03 | Shipment dispatch | in **one transaction**: staging → `VIRT-CUSTOMER` (sale), → the transfer's `IN_TRANSIT` location (`TRANSFER_DEPART`, `STR-T4-02`), or → the supplier (vendor return); reservations closed; quantities shipped | `WhDespatchService.confirm` | `FR-188`, `FR-189` |
| ODS-T4-04 | Short pick | the shortfall goes to backordered (re-allocate is v1.1); the unmet reservation released; emergency replenish offered; with `warehouse.short_pick.auto_count` on, a count for the location is raised | `WhPickTaskWriter` | `FR-185` |
| ODS-T4-05 | An edit after release is allowed | its compensating actions run and each is written to the append-only amendment log (`DONE` / `SKIPPED`) | `WhOrderAmendmentRecorder` | `FR-183` |
| ODS-T4-06 | Cancel after pick | staged holds released through the pick port, the rest de-allocated, each staged pick reversed staging → source, then the order `CANCELLED` — all before anything else can allocate the units | `WhDemandOrderService` cancel | `FR-449` |
| ODS-T4-07 | Confirm delivery | `delivered_at`, optional `pod_document_id`, optional receiver name written on the shipment; the delivery-lead-time column fills | `WhShipmentService` | `FR-447` |
| ODS-T4-08 | A status mapping is corrected | tracking history is re-derived from the stored raw events | `WhCarrierStatusRederiveService` | `FR-198` |
| ODS-T4-09 | Drop-shipment confirmed | one movement `−q` at `SUPPLIER`, `+q` at `CUSTOMER`, purchase and sales lines in the source quad; on-hand at every physical site unchanged; reversal follows the original links | `WhDropShipService` | `FR-467` |
| ODS-T4-10 | Carton sealed with evidence | pack photo (platform document) and scale weight (with instrument) captured at pack time as `wh_carton_evidence` rows | `WhCartonService` | `FR-206` |
| ODS-T4-11 | Order → shipments → cartons | three tables (`wh_demand_orders`, `wh_shipments` with `wh_shipment_orders`, `wh_cartons`) even where one carton ships | schema | `FR-179` |

## 5. T5 — Screen contract (web only, `D-17` item 2)

| ID | Screen | Rule | Source |
|---|---|---|---|
| ODS-T5-01 | WS-099 / WS-100 Demand Orders | one grid for every demand type; the six quantities per line; priority, promised ship / deliver and SLA reference shown; Release on the header; holds listed as records; cancel offers the de-stage path | `FR-177`, `FR-178`, `FR-180`, `FR-182`, `FR-449` |
| ODS-T5-02 | WS-101 Waves | v1.1: Release operates on N orders; unsupported methods are not offered | `FR-186`, `FR-187` |
| ODS-T5-03 | WS-102 Pick Tasks | Complete and Short pick (exception code required) | `FR-185`, `FR-186` |
| ODS-T5-04 | WS-103 Pack Sessions · WS-104 Cartons | one active carton; quantity field on scan; a change-package control above the scanner; no loose-pack option; evidence capture | `FR-190`, `FR-206` |
| ODS-T5-05 | WS-105 / WS-106 Shipments | Load, Dispatch, **Confirm delivery** (`deliveredAt` column); consignment shown 1:1 | `FR-193`, `FR-447` |
| ODS-T5-06 | WS-110 / WS-111 / WS-112 | three screens — manifest, handover, pickup request | `FR-194` |
| ODS-T5-07 | WS-107 / WS-108 / WS-109 Carriers | account owner blank = house account | `FR-196` |
| ODS-T5-08 | WS-114 Shipping Labels | Void (reason + carrier void reference); voided labels stay listed | `FR-197` |
| ODS-T5-09 | WS-115 / WS-116 | raw and normalised status side by side; mappings editable; Re-derive | `FR-198` |
| ODS-T5-10 | WS-128 · WS-257 · WS-127 | the edit matrix, the fulfilment policies, the working calendars | `FR-181`, `FR-183`, `FR-184` |

## 6. Error codes (as built)

The codes in §1.3, raised by the services named in §0. `STAGED_STOCK` is `409` (`FR-449`); the other HTTP
statuses are fixed by the owning task.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived for `D-17` item 1 (R30 `CP-FR-007` row 10) |

## 8. Invariants and scenarios

`L-1`, `L-2`, `L-10`, `FR-436`; scenarios `WH-SC-053`, `WH-SC-054`, `WH-SC-056`, `WH-SC-093`, `WH-SC-094`,
`WH-SC-095`, `WH-SC-097`, `WH-SC-098`, `WH-SC-103`, `WH-SC-104`, `WH-SC-106`, `WH-SC-232`, `WH-SC-279`, `WH-SC-326`,
`WH-SC-333`, `WH-SC-401`.

## 9. Code divergences (FRD rule kept)

| ID | File:line | FR | Difference |
|---|---|---|---|
| ODS-DIV-01 | `warehouse/…/entity/WhFulfilmentPolicy.java:67-70` | `FR-184` | the FRD sets the policy per owner **and per customer**; the code keys it by `owner_id` × `channel_id` — no customer column |
| ODS-DIV-02 | `warehouse/…/service/WhDemandOrderService.java:722-731` | `FR-449` | the FRD de-stages to the source **or a nominated putaway location**; the code reverses each staged pick to its source only |
| ODS-DIV-03 | `warehouse/…/service/WhDemandOrderService.java:144` | `FR-181` | the calendar computes the promise; no SLA-breach measure reads `WhWorkingCalendarService` (its only other consumer is a class `D-16` item 2 removes) |
| ODS-DIV-04 | `warehouse/…/db/migration/V510043__Create_wh_shipments_and_shipment_orders.sql:147` (and `:64`, the account FK added by `V510044`) | `FR-199` | the FRD forbids an FK from the referencing table to a relocatable carrier object; `wh_shipments` carries FKs on `carrier_counterparty_id` and `carrier_account_id` |
| ODS-DIV-05 | `warehouse-base/…/db/migration/V500010__Create_whb_code_lists_task_types_dispositions_attribute_keys.sql:165-168` | `FR-207` | three `CHANNEL_KIND` rows besides `B2B` are still seeded (their removal is `P7`) |
| ODS-DIV-06 | `warehouse/…/entity/WhDemandOrder.java:289`; `warehouse/…/service/whshipment/WhShipmentValidationService.java:59` | `FR-177`, `FR-193` | payment-collection columns and a pooled-tracking-number guard that `D-16` item 2 removes are still present (their removal is `P7`) |

## 10. Open rows

| ID | Question | Missing decision | Default until decided | Source |
|---|---|---|---|---|
| ODS-OPEN-01 | Who owns the **trip** that ends the shipment → consignment → manifest → trip chain, and the "truck" a carton rides in a split dispatch | the FRD names the trip but no warehouse object or owner (the logistics seam is `FR-330`…`FR-348`) | no trip object in warehouse; the chain ends at the manifest | `FR-193`, `FR-191` |
| ODS-OPEN-02 | The carrier weight-dispute object, its due date and the carrier-invoice reconciliation (v2) | not specified beyond naming | evidence captured only (`ODS-T4-10`) | `FR-206` |

<!-- v0 2026-10-23. Amend with /functional-contract: every change references a row id and adds a §7 row. -->
