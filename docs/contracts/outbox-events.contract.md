# Functional Contract — Outbox, event stream, API clients and the logistics seam

> **What this is.** The functional truth for how warehouse facts leave the ledger: the **transactional
> outbox** with a gapless monotonic cursor, the **fixed event vocabulary** at billable grain, the
> **subscription table** with per-subscriber cursors, in-process and HTTP delivery, **retry, dead-letter and
> replay**, the generic `document.status_changed` event and its `WhbTransitionGuard` SPI, the **API client**
> surface (keys, rotation, revocation, rate limit, lag) — and the **logistics seam** that decides which facts
> are warehouse ledger facts (in-transit stock, equipment, vehicles and trailers as locations, the gate,
> returnable packaging, title transfer, freight capitalisation). The README lists delivery, retry and
> dead-letter for it.
>
> **Status.** Derived 2026-10-23 (v0) from `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.19 (`FR-330`…`FR-348`) and
> §6.27 `FR-458` for R30 `CP-FR-007` row 18 under `D-17` item a. Verified against `classic/warehouse-base` and
> `warehouse` by grep. Not ratified. No logistics module exists; its rows are the seam warehouse keeps open.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | A posting appends staged rows in its own transaction (each producer takes its ordering key under the staging barrier inside its COMMIT, `V501224`) → **later**, as the first step of the publisher job, the sequencer assigns gapless cursors in its own `REQUIRES_NEW` transactions, in batches of `warehouse.outbox.sequencer.batch-size` (default 5000) — until it runs, a committed posting's events sit in `whb_outbox_staged` with no cursor (the staging backlog) → the publisher delivers each event to every matching subscription (`OK` / `RETRY` / `DEAD` / `SKIPPED`) and advances that subscription's cursor → a dead delivery is retried or skipped by an operator; a cursor can be reset to replay |
| **Module** | `warehouse-base` (`ai.warehousebase`); consumers in `warehouse`, `warehouse-3pl`, adapters |
| **Domain baseline** | `FR-330`…`FR-348`, `FR-458` · `D-16`, `D-17` · `OD-8` · `L-1` · tables `whb_event_types`, `whb_outbox`, `whb_outbox_subscriptions`, `whb_outbox_deliveries`, `whb_outbox_cursor_counter` (`V500040`), `whb_outbox_staged`, `whb_outbox_staged_order` (`V501223`, `V501224`), document-status columns + HTTP settings (`V501106`), `whb_api_clients`, `_keys`, `_endpoints`, `_companies` (`V500066`) |
| **Owning tasks** (R30 §4) | `issues/p0-11.md` (`FR-330`…`333`, `336`) · `p3-22` (`334`) · `p2-02` (`335`, `342`) · `p1-11` (`337`, `339`, `341`) · `p5-21` (`338`, `340`, `343`) · `p1-17` (`344`) · `p2-28` (`345`) · `p0-15` (`346`) · `p6-08` (`347`, `348`) · `p5-22` (`458`) |
| **Permission resources** | `whb_outbox:{view,replay,export}`; `logistics:*` reserved, never granted (`V501000`) |
| **Screens** | WS-056 Outbox Monitor · WS-057 Outbox Subscriptions · WS-058 Outbox Dead-letter · WS-246 API Clients · WS-247 API Client Keys |
| **Contract version** | `v0 — 2026-10-23` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | The cursor is gapless and monotonic; consumers dedupe on (consumer, sequence) | `OEV-GRD-01`, `OEV-GRD-03` |
| A2 | Every event carries owner, lot, LPN, warehouse and the timestamps, and no payload | `OEV-GRD-02` |
| A3 | A failing subscriber retries with backoff, then dead-letters, and can be replayed | `OEV-T1-03`…`-06` |
| A4 | Base knows no consumer | `OEV-UNR-01` |
| A5 | Transit stock is a ledger fact at an in-transit location | `OEV-T4-01` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Source |
|---|---|---|---|
| Outbox row | appended (immutable) | `whb_outbox` row with `cursor` | FR-330 |
| Delivery | `OK` · `RETRY` · `DEAD` · `SKIPPED` | `whb_outbox_deliveries.status` (`WhbOutboxVocabulary`) | FR-332 |
| Subscription | active / inactive; held (`RESTORE_DETECTED`, `START_HELD_FLAG`) | `whb_outbox_subscriptions.is_active`, hold | FR-333 |
| API client key | live · revoked · expired | `whb_api_client_keys` (`revoked_at`, `expires_at`) | FR-458 |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor / class | Side effects | UI | Source |
|---|---|---|---|---|---|---|---|---|
| OEV-T1-01 | — | A posting in the same transaction | staged | event code exists in `whb_event_types` (FK by code) | `WhbOutboxAppender` | — | — | FR-330, FR-331 |
| OEV-T1-02 | staged (producer committed) | Sequencer pass (publisher job, step one) | appended with next cursor | one sequencer pass under an advisory lock (`V501227`); only the staged prefix at or below the highest committed `order_seq` is copied | `WhbOutboxSequencer` (`REQUIRES_NEW`, batch-size 5000, `WhbOutboxSequencer.java:19-36,60`) | cursor counter advanced; copied staged rows deleted in the same batch transaction — a crash leaves them staged for the next run, never both, never neither | — | FR-330 |
| OEV-T1-03 | appended | Publish to a matching subscription | delivery `OK` | event filter / owner filter / accepted version match | `WhbOutboxPublisher`, `WhbOutboxPublisherJob`, `WhbOutboxDeliveryStep` | subscription `last_delivered_cursor` advanced | WS-056 | FR-332, FR-333 |
| OEV-T1-04 | delivery | Transport failure | `RETRY` → … → `DEAD` | `max_attempts` (`warehouse.outbox.max_attempts`, default 10, 1…100), `backoff_seconds` (default 60) | `WhbOutboxRetryPolicy`, `WhbOutboxDeliveryFailure` | blocked alert (`WhbOutboxBlockedAlertService`) | WS-058 | FR-332 |
| OEV-T1-05 | `DEAD` | Retry / retry all dead / skip | `RETRY` / `SKIPPED` | — | `POST /retry`, `/retry-dead`, `/skip` · `whb_outbox:replay` | — | WS-058 | FR-332 |
| OEV-T1-06 | subscription | Reset cursor (replay from cursor) | cursor moved back | — | `POST /{id}/reset-cursor` · `whb_outbox:replay` | redelivery from that cursor, consumers dedupe | WS-057 | FR-332, FR-458 |
| OEV-T1-07 | held | Release hold after a restore | active | — | `POST /{id}/release-hold` · `whb_outbox:replay`; `WhbOutboxRestoreGuard` | — | WS-057 | FR-332 |
| OEV-T1-08 | — | Any document transition through the single helper | `document.status_changed` appended (type, id, from, to, actor) | every registered `WhbTransitionGuard` consulted first; base registers none | `WhbDocumentTransitionService` | — | — | FR-334 |
| OEV-T1-09 | — | Issue / rotate / revoke an API client key | live → revoked / expired | revocation reason required | `WhbApiClientService` | — | WS-246, WS-247 | FR-458 |

## 2. Guards

| ID | Predicate (must hold to proceed) | Refusal: HTTP · code · field | DB backstop | Source |
|---|---|---|---|---|
| OEV-GRD-01 | The outbox cursor is gapless and monotonic in commit order | — | `whb_outbox_cursor_counter`, sequencer barrier (`V501223`, `V501224`, deferrable at-commit ordering) | FR-330 |
| OEV-GRD-02 | Every outbox row carries `event_version`, `occurred_at`, `posting_date`, `recorded_at`, `company_id`, `warehouse_id`, `owner_id`, `item_id`, `lot_id`, `serial_id`, `lpn_id`, `location_id`, `stock_status_code`, `quantity`, `uom_code`, movement and source lineage, actor — and **no payload column** | — | `V500040` column set (`PC-36` comment) | FR-331 |
| OEV-GRD-03 | Delivery is at-least-once; a subscriber dedupes on (subscriber, cursor) | — | per-subscription `last_delivered_cursor` | FR-330, FR-333 |
| OEV-GRD-04 | A subscription is a row: `subscriber_code`, `transport` `IN_PROCESS` / `HTTP`, `endpoint_url`, `secret_ref`, `event_type_filter`, `owner_filter_id`, `accepted_event_version`, `signing_algorithm`, `delivery_timeout_seconds` | — | `whb_outbox_subscriptions`; HTTP via `WhbOutboxHttpTransport` + `WhbOutboxSignature` (v1.1) | FR-333 |
| OEV-GRD-05 | An API-client request presents a live key of an active client, for an endpoint in its scope, under its per-client rate limit; it narrows the user's session, never authenticates | `403 API_CLIENT_REFUSED` (one message for unknown / revoked / expired); `403 API_CLIENT_ENDPOINT_NOT_IN_SCOPE`; `429 RETRY_AFTER` | `chk_whb_api_clients_rate_limit` (`rate_limit_per_minute`) | FR-458 |
| OEV-GRD-06 | A lag-shaped signal sits beside the failure-shaped ones | — | `WhbOutboxLagAlertService` | FR-458 |
| OEV-GRD-07 | A transit loss is an ordinary reason-coded adjustment against the in-transit location | reason required | in-transit virtual location (`V500013`); `WhbMovementTransitCarveOutRuleTest` | FR-335 |
| OEV-GRD-08 | A gate ENTRY stamps only a `SCHEDULED` appointment of that vehicle at that site whose start is on the same site day; otherwise the handler answers `IGNORED` | — | `WhDockAppointmentGateHandler` | FR-340 |
| OEV-GRD-09 | Whether a destination is our own branch is read from its `REGISTERED` branch at the document date | — | core transfer rules | FR-342 |
| OEV-GRD-10 | `ownership_transfer_point` exists on purchase order, goods receipt and transfer | — | `V510011`, `V510014`, `V510031` | FR-344 |

### 2.1 Unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| OEV-UNR-01 | A consumer registered in base; base importing a consumer | `WhbOutboxSubscriberRegistry` is a bean list filled by consumers; `WarehouseBaseCouplingTest` | FR-330, FR-334 |
| OEV-UNR-02 | Updating or deleting an outbox row | `WhbOutboxDeletionContractTest` | FR-330 |
| OEV-UNR-03 | A foreign key from a warehouse table into a logistics table, or from logistics into ours | `WhbLogisticsSeamContractTest.shouldFindNoLaterForeignKeyOnDocumentId`; vehicle ↔ location joined only by `whb_location_external_refs` | FR-336, FR-339 |
| OEV-UNR-04 | A fitment or trip table in warehouse | `WhbNoFitmentOrTripTableContractTest` — the fitment record belongs to logistics | FR-338 |
| OEV-UNR-05 | A transfer that teleports in one movement | `TRANSFER_DEPART` then `TRANSFER_ARRIVE` through in-transit (`V500003`) | FR-335 |
| OEV-UNR-06 | Granting a `logistics:*` permission before the module exists | `V501000` seeds them reserved and excludes them from every grant | FR-346 |
| OEV-UNR-08 | A v1 migration inside `V524000`–`V524999` or a `log_` table | `WarehouseBaseCouplingTest` band and prefix scanners (FR-346 rule) | FR-346 |
| OEV-UNR-07 | Delivery to a customer posting a movement | stock left at despatch; only an own-branch arrival posts | FR-342 |

## 3. T3 — Time rules

| ID | Rule | Clock | Changes | Job | Source |
|---|---|---|---|---|---|
| OEV-T3-01 | Publish pass | scheduler | deliveries | `WhbOutboxPublisherScheduler` / `WhbOutboxPublisherJob` | FR-332 |
| OEV-T3-02 | Retry backoff | `backoff_seconds` per attempt | `RETRY` → next attempt / `DEAD` | `WhbOutboxRetryPolicy` | FR-332 |
| OEV-T3-03 | Subscription lag / blocked | cursor distance and age | alert | `WhbOutboxLagAlertService`, `WhbOutboxBlockedAlertService`, `WhbOutboxHoldHealthSignalSource` | FR-458 |
| OEV-T3-04 | In-transit ageing | depart time | ageing figure; partial arrival leaves the rest in transit | stock ageing (`WhStockAgeingResponse`) | FR-335 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| OEV-T4-01 | transfer departs / arrives | `TRANSFER_DEPART` to in-transit; `TRANSFER_ARRIVE` from it, fewer lines on a partial arrival; an arrival under a different GSTIN still posts on a taxable transfer | core transfer service → writer | FR-335, FR-342 |
| OEV-T4-02 | any movement posted / reversed, receipt line confirmed, putaway completed, pick confirmed, carton packed, shipment confirmed, task completed, count variance posted, return dispositioned, work order completed, owner changed, reservation created / released, equipment issued to trip, detention started | the seeded event code in `whb_event_types` | `V500040` seed | FR-331, FR-334 |
| OEV-T4-03 | tyre, fuel, returnable equipment, packaging held | warehouse stock of a warehouse item type (`TYRE`, `FUEL`, `RETURNABLE_EQUIPMENT`, `PACKAGING`) | `V500052`, `V500008`; `WhbLogisticsSeamContractTest` | FR-337 |
| OEV-T4-04 | equipment issued to / returned from a trip | `EQUIPMENT_ISSUE` / `EQUIPMENT_RETURN` through the port; event `equipment.issued_to_trip` | `V500003` | FR-338 |
| OEV-T4-05 | a vehicle or yard trailer holds stock | it is a stock-holding warehouse location; weighbridge tare / gross / net belong to the receipt (`wh_weighing_records`, `V510213`) | `WhbLogisticsSeamContractTest.shouldSeedBothAsStockHolding` | FR-341, FR-339 |
| OEV-T4-06 | gate event received | published to a handler list; warehouse claims it for the dock appointment | `WhbGateEventController`, `WarehouseGateEventPublisher` | FR-340 |
| OEV-T4-07 | returnable packaging exchanged | per-counterparty balance entry; balance reconciles to entries | `whb_packaging_balances`, `whb_packaging_balance_entries` (reconcile triggers, `V501114`) | FR-343 |
| OEV-T4-08 | freight charged on a receipt | zero-quantity `LANDED_COST_APPLY` value-only movement | `V500003`; value conservation `p2-28` | FR-345 |
| OEV-T4-09 | a future logistics module is built | it posts through the port directly, no adapter; its pre-flight enumerates the four existing transport-shaped surfaces (field-service trips, services pickup / drop ladder, the automotive gate webhook, and the dealer PDI movements kept as history under `D-16`) and names the party / vehicle master overlap | `issues/p6-08.md` pre-flight | FR-347, FR-348, FR-366 |

## 5. T5 — Screen contract

| ID | Screen | Offers | Permission | Source |
|---|---|---|---|---|
| OEV-T5-01 | WS-056 Outbox Monitor | events by cursor, filters by type / owner / warehouse | `whb_outbox:view` | FR-330, FR-332 |
| OEV-T5-02 | WS-057 Outbox Subscriptions | status toggle, reset cursor, release hold | `whb_outbox:view` / `:replay` | FR-333, FR-332 |
| OEV-T5-03 | WS-058 Outbox Dead-letter | retry, retry all dead, skip, export | `whb_outbox:replay` / `:export` | FR-332 |
| OEV-T5-04 | WS-246 / WS-247 API Clients / Keys | clients, endpoints, companies, keys with rotate / revoke | API-client resources | FR-458 |

## 6. Code divergences

| ID | FR says | Code has (grep) | Source |
|---|---|---|---|
| OEV-DIV-01 | Issue-to-asset and return-from-asset are posted through the port | `V500003` seeds `EQUIPMENT_ISSUE` / `EQUIPMENT_RETURN` only; no `ISSUE_TO_ASSET` / `RETURN_FROM_ASSET` type — **resolved R31**: `FR-338` restated to this pair (`OEV-OPEN-02`) — **Triage 2026-10-23: AMEND-SPEC** — applied R31 (`FR-338` restated); stands as the rule | FR-338 |
| OEV-DIV-02 | The integration surface is argued as platform work first and built in base only if platform declines | built in base (`V500066`, `WhbApiClientGate`); no recorded platform decline found — **Triage 2026-10-23: AMEND-SPEC** — rule: the platform question was settled by `OD-8` (resolved 2026-09-11, `GLOBAL-SETTINGS-DECISIONS.md`): the port authenticates an ordinary platform user and the API client is a warehouse-base integration surface that narrows it. Evidence: `V500066` header *THE DECISION THIS FILE IMPLEMENTS*. `FR-458` amended | FR-458 |
| OEV-DIV-03 | Seam acceptance = two deletion tests (delete logistics; delete warehouse) | only the warehouse side is tested (no FK out); no logistics module exists to delete — **Triage 2026-10-23: CARRIED** — `P6-08` #131 (`p6-08.md:120`, `:229` — the two deletion tests) | FR-336 |

## 7. Out of scope

The logistics module itself (`p6-08`, v3); trips, ePOD and freight settlement; mobile.

## 8. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived for R30 `CP-FR-007` row 18 (`D-17` item a) |
| 2026-10-23 | R31 `F-CB-016`: cursor assignment is producer-commit-then-sequencer, not at commit (§0, `OEV-T1-02`); `OEV-OPEN-01`, `-02` decided |

## 9. Invariants and scenarios

`L-1`; scenarios `WH-SC-252`, `WH-SC-294`, `WH-SC-058`, `WH-SC-226`, `WH-SC-295`, `WH-SC-363`, `WH-SC-273`, `WH-SC-296`, `WH-SC-123`, `WH-SC-364`, `WH-SC-128`, `WH-SC-034`, `WH-SC-246`, `WH-SC-337`.

## 10. Open rows

| ID | Question | Default | Source |
|---|---|---|---|
| OEV-OPEN-01 | `OD-8`: does platform own API clients (service principals) after all, making `OEV-DIV-02` a migration later | **DECIDED R31 (2026-10-23):** default stands — base keys only narrow an authenticated user (`OD-8` RESOLVED) | FR-458 |
| OEV-OPEN-02 | Asset fitment movement types (`OEV-DIV-01`): add `ISSUE_TO_ASSET` / `RETURN_FROM_ASSET` or restate the FR to the equipment pair | **DECIDED R31 (2026-10-23):** default stands — `FR-338` restated to the equipment issue / return pair | FR-338 |
