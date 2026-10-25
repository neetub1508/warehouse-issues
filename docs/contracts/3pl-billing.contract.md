# Functional Contract — 3PL client, meter, rating and the billing run

> **What this is.** The functional truth for selling storage to third parties in `warehouse-3pl`: the
> **client as an object** with its own ladder, the **billable-event meter** (append-only, reversible),
> **charge codes and versioned rate cards** with a fail-rather-than-guess resolver, **storage billing** over
> persisted daily snapshots, the **billing run with a frozen approved state**, accessorials, disputes, the
> single **AR envelope** to accounting, freight billing, SLA objects, client GST registrations and the
> client portal as a permission surface. The README names this contract (billing run freeze, storage
> anniversaries).
>
> **Status.** Derived 2026-10-23 (v0) from `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.17 (`FR-281`…`FR-303`)
> for R30 `CP-FR-007` row 16 under `D-17` item a (every active FR is covered by a contract rule). Verified
> against `classic/warehouse-3pl` by grep. Not ratified. A 3PL client is a **storage customer of a plant
> or storage operator** (`D-16` item 1); no retail or e-commerce vocabulary applies.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Client: `PROSPECT` → `ONBOARDING` → `LIVE` → `SUSPENDED` → `TERMINATING` → `OFFBOARDED` — one-way: there is **no `SUSPENDED → LIVE`** (`Wh3plClientService.java:62-63`; the ladder trigger refuses it, `V530010:114-115`), so a suspended client can only be terminated. Meter: event `METERED` → `RATED` → `BILLED`, or `REVERSED` / `EXCLUDED`. Run: `DRAFT` → `RATED` → `APPROVED` → `INVOICED`, or `CANCELLED`. Around them: rate cards, storage periods, accessorials, disputes, AR handovers, SLA, GST registrations, portal |
| **Module** | `warehouse-3pl` (`ai.warehouse3pl`, band `V530000`–`V539999`, prefix `wh3_`, flag `enable.warehouse.3pl`, `Wh3plModuleConfig`) |
| **Domain baseline** | `FR-281`…`FR-303` · `D-11`, `D-16`, `D-17` · `L-1`, `L-2` · `OD-3` · base snapshots `whb_stock_position_snapshots` / `whb_stock_position_snapshot_days` (`V500045`, `V501125`) · base number series `whb_number_series` · base outbox subscription `WH3_BILLING_METER` (`V530030`) |
| **Owning tasks** (R30 §4) | `issues/p5-01.md` (`FR-281`…`283`, `303`) · `p5-02` (`286`, `287`) · `p5-03` (`285`) · `p5-04` (`288`, `290`) · `p2-28` (`289`) · `p5-05` (`291`…`294`) · `p5-06` (`295`) · `p5-07` (`297`, `298`) · `p5-08` (`284`, `300`) · `p4-10` (`301`) · `p6-07` (`296`, `299`, `302`) |
| **Primary tables** | `wh3_clients`, `wh3_client_counterparties` (`V530010`) · `wh3_client_onboarding_templates`, `_template_tasks`, `wh3_client_onboarding_tasks` (`V530011`) · `wh3_charge_codes` (`V530020`) · `wh3_rate_cards`, `wh3_rate_card_clients`, `wh3_rate_card_lines`, `wh3_storage_aging_bands` (`V530021`) · `wh3_billable_events` (`V530030`, guards `V530101`, `V530102`) · `wh3_storage_billing_periods`, `wh3_storage_billing_lines` (`V530031`) · `wh3_billing_runs`, `wh3_billing_run_lines` (`V530040`) · `wh3_accessorials` (`V530041`) · `wh3_disputes` (`V530042`) · `wh3_ar_handovers` (`V530043`) · `wh3_freight_billing_rules` (`V530044`) · `wh3_sla_definitions`, `_definition_clients`, `_measurements`, `_breaches` (`V530050`) · `wh3_client_gst_registrations` (`V530060`) |
| **Routes** | `/warehouse/3pl/{clients, onboarding-templates, onboarding-tasks, charge-codes, rate-cards, billable-events, storage-billing-periods, billing-runs, accessorials, disputes, ar-handovers, freight-billing-rules, sla-definitions, sla-measurements, sla-breaches, client-gst-registrations, portal, reports/custody-value}` · screens WS-155…WS-172, WS-227 |
| **Contract version** | `v0 — 2026-10-23` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | Nothing in base or core depends on 3PL | `TPB-UNR-01` |
| A2 | A meter event is never deleted or edited after billing; a correction is a reversing event | `TPB-UNR-02`, `TPB-T1-12` |
| A3 | An unrated event blocks the run and names the missing combination | `TPB-GRD-05`, `TPB-T1-16` |
| A4 | An approved run is frozen; a change is a reversal run | `TPB-UNR-03`, `TPB-T1-19` |
| A5 | 3PL emits one AR envelope and owns no invoice, number or tax | `TPB-T4-05`, `TPB-UNR-05` |
| A6 | A client never sees another client's stock | `TPB-GRD-10` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Kind | Source |
|---|---|---|---|---|
| Client | `PROSPECT` · `ONBOARDING` · `LIVE` · `SUSPENDED` · `TERMINATING` · `OFFBOARDED` | `wh3_clients.status` + `trg_wh3_clients_status_ladder` | ladder; `OFFBOARDED` terminal | FR-282 |
| Onboarding task | `OPEN` · `COMPLETED` | `wh3_client_onboarding_tasks.status` | — | FR-283 |
| Rate card | `DRAFT` · `ACTIVE` · `SUPERSEDED` | `wh3_rate_cards.status` | `SUPERSEDED` terminal | FR-287 |
| Billable event | `METERED` · `RATED` · `BILLED` · `REVERSED` · `EXCLUDED` | `wh3_billable_events.status` + `trg_wh3_billable_events_guard` | `REVERSED`/`EXCLUDED` terminal | FR-285 |
| Storage period | `COMPUTED` · `APPROVED` (true-up `NOT_APPLICABLE`/`NOT_REQUIRED`/`POSTED`/`PENDING_RATING`/`DEFERRED`) | `wh3_storage_billing_periods.status`, `true_up_status` | — | FR-288, FR-290 |
| Billing run | `DRAFT` · `RATED` · `APPROVED` · `INVOICED` · `CANCELLED` | `wh3_billing_runs.status` + `trg_wh3_billing_runs_guard` | `INVOICED`/`CANCELLED` terminal | FR-292 |
| Accessorial | `RAISED` · `APPROVED` · `REJECTED` · `BILLED` | `wh3_accessorials.status` + `trg_wh3_accessorials_guard` | `REJECTED` terminal | FR-291 |
| Dispute | `RAISED` · `INVESTIGATING` · `UPHELD` · `REJECTED` · `WITHDRAWN` | `wh3_disputes.status` + trigger | last three terminal | FR-293 |
| AR handover | `PENDING` · `SENT` · `POSTED` · `REJECTED` · `VOIDED` | `wh3_ar_handovers.status` + trigger | `POSTED`/`VOIDED` terminal | FR-294 |
| SLA breach | `CONFIRMED` · `WAIVED` | `wh3_sla_breaches.status` | — | FR-297 |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | UI | Source |
|---|---|---|---|---|---|---|---|---|
| TPB-T1-01 | — | Create client (owner, contract dates, notice, billing cycle/day, currency, terms, credit limit, minimum charge, tax profile) | `PROSPECT` | `TPB-GRD-01`, `-02` | `wh3_clients:create` | — | WS-155 **Add** | FR-282 |
| TPB-T1-02 | `PROSPECT` | Onboard | `ONBOARDING` | template chosen; series company resolvable | `wh3_clients:onboard` (`Wh3plClientService.onboard`) | onboarding tasks copied from `wh3_client_onboarding_template_tasks`; per-client number series provisioned in `whb_number_series` (pad `warehouse.3pl.client_series.pad_length`) | WS-155 | FR-283 |
| TPB-T1-03 | `ONBOARDING` | Go live | `LIVE` | no **blocking** onboarding task still `OPEN`, else `409 BLOCKING_TASKS_OPEN` · `status`, naming the tasks (`Wh3plClientValidationService.java:275-279`); optional tasks may stay open; the go-live date is given and not in the future, else `422 GO_LIVE_DATE_INVALID` · `goLiveDate` (`:263-270`). (`CLIENT_NOT_ONBOARDING` is the refusal for reopening an onboarding task, `TPB-T1-07`) | `wh3_clients:onboard` (`goLive`) | `go_live_date` stamped | WS-155 | FR-282, FR-283 |
| TPB-T1-04 | `LIVE` | Suspend | `SUSPENDED` (one-way) | — | `wh3_clients:suspend` | — | WS-155 | FR-282 |
| TPB-T1-05 | `LIVE` · `SUSPENDED` | Terminate | `TERMINATING` | `contract_end_date` required (`V531152`) | `wh3_clients:terminate` | notice clock `TPB-T3-02` | WS-155 | FR-282 |
| TPB-T1-06 | `TERMINATING` | Offboard | `OFFBOARDED` | contract end date set and reached, else `422 CONTRACT_END_REQUIRED` / `409 CONTRACT_END_NOT_REACHED` · `contractEndDate` (`Wh3plClientValidationService.java:215-224`); the caller is unscoped (may read every owner), else `403 OFFBOARD_REQUIRES_UNSCOPED` (`:237`); the owner holds no stock or open reservation, base's `OWNER_HAS_STOCK` (`:242`) | `wh3_clients:terminate` (`offboard`) | terminal; `TPB-T4-10` | WS-155 | FR-282 |
| TPB-T1-07 | `OPEN` | Complete onboarding task | `COMPLETED` (re-openable while the client is `ONBOARDING`, else `CLIENT_NOT_ONBOARDING`) | — | `wh3_client_onboarding_tasks:complete` / `:reopen` / `:assign` | audit `WH3_ONBOARDING_TASK_COMPLETED` | WS-157 | FR-283 |
| TPB-T1-08 | — | Create rate card / clone version | `DRAFT` | one draft per card, else `409 RATE_CARD_DRAFT_EXISTS` · `status`; ladder complete, else `RATE_CARD_LADDER_INCOMPLETE` | `Wh3plRateCardService.create` / `cloneVersion` | version n+1 copies lines, bands, clients | WS-159 | FR-287, FR-296 |
| TPB-T1-09 | `DRAFT` | Activate | `ACTIVE` | client overlap refused `409 RATE_CARD_CLIENT_OVERLAP` · `clientIds` | `wh3_rate_cards:activate` | the prior `ACTIVE` version → `SUPERSEDED` at the new `effective_from` | WS-159 | FR-287 |
| TPB-T1-09a | `ACTIVE` | **Expire** | `ACTIVE` (status unchanged) — `effective_to` moved earlier; the card keeps pricing the dates it covered | `validateExpiry` (the new end is valid for the window) | `wh3_rate_cards:expire` (`Wh3plRateCardController.java:262-263`, `Wh3plRateCardService.java:255-258`) | — | WS-159 | FR-287 |
| TPB-T1-10 | — | Meter an event | `METERED` | `TPB-GRD-04` | `Wh3plBillableEventMeter` (outbox subscriber `WH3_BILLING_METER`, `Wh3plBillableEventSubscriber`) | — | — | FR-285 |
| TPB-T1-11 | `METERED` | Rate | `RATED` | `TPB-GRD-05` | `Wh3plBillingRunRatingEngine` | rate, amount, rate-card version stamped | — | FR-287 |
| TPB-T1-12 | `METERED` · `RATED` | Reverse | `REVERSED` + a reversing row | not already reversed (`409 BILLABLE_EVENT_ALREADY_REVERSED`); not billed (`409 BILLABLE_EVENT_BILLED`) | `Wh3plBillableEventService.reverse` | reversing event `reversal_of_id` (`uk_wh3_billable_events_reversal_of`) | WS-160 | FR-285 |
| TPB-T1-13 | `METERED` · `RATED` | Exclude | `EXCLUDED` | reason code required, `422 EXCLUSION_REASON_REQUIRED` · `exclusionReasonCode` (context `BILLING_EXCLUSION`) | `exclude` | author + reason kept; row never deleted | WS-160 | FR-285 |
| TPB-T1-14 | — | Compute storage period | `COMPUTED` | `TPB-GRD-07` | `Wh3plStorageBillingPeriodService.compute` | lines per method × basis; `STORAGE_CHARGE` events | WS-161 | FR-288 |
| TPB-T1-15 | `COMPUTED` | Approve storage period | `APPROVED` | not billed (`STORAGE_PERIOD_BILLED`) | `approve` | minimum true-up `TPB-T4-02` | WS-161 | FR-288, FR-290 |
| TPB-T1-16 | `DRAFT` | Rate run | `RATED` | unrated count = 0, else `422 WH3_BILLING_RUN_UNRATED` (count + summary kept, `noRollbackFor`) | `Wh3plBillingRunService.rate` | lines written once | WS-162 | FR-292, FR-287 |
| TPB-T1-17 | `RATED` | Re-rate | `DRAFT` → `RATED` | run not `APPROVED` | `rerate` | lines replaced | WS-162 | FR-292 |
| TPB-T1-18 | `RATED` | Approve | `APPROVED` | approver ≠ rater above `warehouse.3pl.billing_run.approval_separation_threshold`, else `403 WH3_BILLING_RUN_SELF_APPROVAL` | `approve` | events `BILLED`, accessorials `BILLED`; `TPB-T4-05` | WS-162 | FR-292 |
| TPB-T1-19 | `APPROVED` · `INVOICED` | Reverse run | new ad-hoc run of reversing events | no live reversal (`WH3_BILLING_RUN_HAS_LIVE_REVERSAL`), no open dispute (`WH3_BILLING_RUN_HAS_OPEN_DISPUTE`) | `reverse` | the original stays frozen | WS-162 | FR-292 |
| TPB-T1-20 | `DRAFT` · `RATED` · `APPROVED` | Cancel | `CANCELLED` | no handover in flight (`WH3_BILLING_RUN_HANDOVER_IN_FLIGHT`) | `cancel` | billed rows of the run released (`V530102`); accessorials back to `APPROVED` | WS-162 | FR-292 |
| TPB-T1-21 | `APPROVED` | Handover posted | `INVOICED` | handover `POSTED` | `emitArHandover` / manual mark | — | WS-162, WS-170 | FR-294 |
| TPB-T1-22 | — → `RAISED` → `APPROVED` / `REJECTED` | Raise / approve / reject accessorial | as named | `TPB-GRD-08` | `Wh3plAccessorialService` | `APPROVED` rows enter the next run | WS-163 | FR-291 |
| TPB-T1-23 | — → `RAISED` → `INVESTIGATING` → `UPHELD` / `REJECTED`; `RAISED` → `WITHDRAWN` | Dispute ladder | as named | `TPB-GRD-09` | `Wh3plDisputeService` (portal raise via `/portal/disputes`) | `UPHELD` → `TPB-T4-04` | WS-164, WS-172 | FR-293 |
| TPB-T1-24 | `PENDING` → `SENT` → `POSTED` / `REJECTED`; `REJECTED` → `PENDING` (retry) / `VOIDED`; `PENDING` → `POSTED` manual | Handover delivery | as named | trigger `AR_HANDOVER_STATUS_TRANSITION` | `Wh3plArHandoverDispatcher`, `Wh3plArHandoverService.retry` / `voidHandover` | — | WS-170 | FR-294 |
| TPB-T1-25 | — | Confirm / waive SLA breach | `CONFIRMED` / `WAIVED` | waiver separation above `warehouse.3pl.sla.waiver_separation_threshold` | `Wh3plSlaBreachService.confirm` / `waive` | — | WS-168 | FR-297, FR-299 |

### 1.3 T2 — Action × permission × state (R31 `F-CB-003`, as built)

| ID | Action | Permission (`@PreAuthorize`) | Allowed from | Source |
|---|---|---|---|---|
| TPB-T2-01 | Create / edit a client; parties | `wh3_clients:create` / `:edit` | — / not `OFFBOARDED` | FR-282 |
| TPB-T2-02 | Onboard; **go live** | `wh3_clients:onboard` (both — `Wh3plClientController.java:291-302`) | `PROSPECT`; `ONBOARDING` | FR-282, FR-283 |
| TPB-T2-03 | Suspend | `wh3_clients:suspend` | `LIVE` | FR-282 |
| TPB-T2-04 | Terminate; **offboard** | `wh3_clients:terminate` (both — `:321-332`) | `LIVE` · `SUSPENDED`; `TERMINATING` | FR-282 |
| TPB-T2-05 | Onboarding task assign / complete / reopen | `wh3_client_onboarding_tasks:{assign,complete,reopen}` | `OPEN` / `COMPLETED` | FR-283 |
| TPB-T2-06 | Rate card create / edit / clone version / activate / expire | `wh3_rate_cards:{create,edit,clone_version,activate,expire}` | — / `DRAFT` / any / `DRAFT` / `ACTIVE` | FR-287, FR-296 |
| TPB-T2-07 | Billable event reverse; **exclude** | `wh3_billable_events:reverse` (both — exclude has no verb of its own) | `METERED` · `RATED` | FR-285 |
| TPB-T2-08 | Storage period compute / approve / recompute | `wh3_storage_billing_periods:{compute,approve,recompute}` | — / `COMPUTED` / `COMPUTED` | FR-288, FR-290 |
| TPB-T2-09 | Billing run create / rate / re-rate / approve / emit AR handover / cancel | `wh3_billing_runs:create` / `:rate` (both) / `:approve` / `:emit_ar_handover` / `:cancel` | as §1.2 | FR-292, FR-294 |
| TPB-T2-10 | **Reverse a billing run** | `wh3_billing_runs:reverse` (requires `:view`; `V531158`, R33 #35 G1 — granted on deploy to every holder of `:create`). Reverse ends by rating the reversal run internally (`Wh3plBillingRunService.reverse` → `rate`), so no `:rate` check applies — intended. Row lock, reason and the `validateReverse` refusals (reversal of a reversal, live reversal, open dispute) unchanged | `APPROVED` · `INVOICED` | FR-292 |
| TPB-T2-11 | Accessorial raise / approve / reject | `wh3_accessorials:{raise,approve,reject}` | — / `RAISED` | FR-291 |
| TPB-T2-12 | Dispute raise / withdraw; investigate / uphold / reject | `wh3_disputes:raise` (withdraw too) / `:investigate` / `:uphold` / `:reject` | as `TPB-T1-23` | FR-293 |
| TPB-T2-13 | AR handover retry / void | `wh3_ar_handovers:{retry,void}` | `REJECTED` | FR-294 |
| TPB-T2-14 | SLA breach confirm / waive | `wh3_sla_breaches:{confirm,waive}` | candidate / `CONFIRMED` | FR-297, FR-299 |
| TPB-T2-15 | Portal read and dispute raise | `wh3_clients:portal_access` | — | FR-284 |

## 2. Guards

| ID | Predicate (must hold to proceed) | Refusal: HTTP · code · field | DB backstop | Source |
|---|---|---|---|---|
| TPB-GRD-01 | Client code upper-case, unique; owner unique and immutable; a client binds one base owner | `422 CLIENT_CODE_EXISTS` · `clientCode`; `409 OWNER_ALREADY_BOUND` · `ownerId`; `422 OWNER_IMMUTABLE` | `uk_wh3_clients_owner_id`, trigger immutability | FR-282, FR-303 |
| TPB-GRD-02 | Contract end > start; notice ≥ 0; billing day inside the cycle; credit limit and minimum ≥ 0 | `422` field-keyed | `chk_wh3_clients_*` | FR-282 |
| TPB-GRD-03 | A charge code carries category, default UoM, recurring / pass-through / taxable flags, tax code, SAC/HSN and a **`revenue_purpose_code`** — never a GL account id | `422` field-keyed | `wh3_charge_codes.revenue_purpose_code NOT NULL` | FR-286 |
| TPB-GRD-04 | An event is metered once per `(source_system, source_event_key)` | idempotent replay returns the existing row | `uk_wh3_billable_events_source` | FR-285 |
| TPB-GRD-05 | Rating resolves the card **version live on the event's date**, most-specific-wins; no match → refuse, never zero | `422 WH3_UNRATED_EVENT` naming `(chargeCode, uom, basis, date)` (`Wh3plUnratedEventException`) | — | FR-287 |
| TPB-GRD-06 | A rate card's bands do not overlap; an inheriting card overrides lines of its parent only | `RATE_CARD_BAND_OVERLAP` | — | FR-287 |
| TPB-GRD-07 | A storage period reads a snapshot for every day; method ∈ {`PERIOD_END`, `PERIOD_START`, `ANNIVERSARY`, `AVERAGE_DAILY`, `SPLIT_MONTH`}; basis on P5-02's seven-value whitelist (`SQFT_ALLOCATED`: `PERIOD_END` only, no snapshot-day read; `SQFT_OCCUPIED`: every physical location measured and unshared) — R33 #30; periods do not overlap | `STORAGE_PERIOD_SNAPSHOT_DAY_MISSING`, `STORAGE_METHOD_INVALID`, `STORAGE_BASIS_INVALID`, `STORAGE_MEASURE_MISSING` · `basis`, `STORAGE_LOCATION_SHARED` · `basis`, `STORAGE_PERIOD_OVERLAP` | — | FR-288, FR-289 |
| TPB-GRD-07a | **Square-feet measurement (R33 #30, `V531157`).** `SQFT_OCCUPIED`: identity = the location; units = `whb_locations.width_cm × depth_cm / 929.0304`, counted **once per location per day** however many items, lots or LPNs it holds; a row on no location or on a virtual / transit location is skipped (as PALLET skips LPN-less rows); all five methods run as LOCATION, anchor = the oldest receipt among the location's rows; footprint is the live master, stamped on the line and frozen once a run holds the events (as WEIGHT/CUBIC). `SQFT_ALLOCATED`: one line per period = the resolved rate line's `allocated_area_sq_ft` × rate, billed whether stock is on hand or not, `warehouse_id` NULL, `snapshot_date` = `period_to`; full rate per period, no pro-rating, no free days, no ageing band; **one tier per (charge, unit)** on a rate card (S4 F1) so the area is always the resolved line's - the line that states the area is the line that prices it; the **period-range bound stays** (S4 F3): no per-site snapshot-day check, but the period must start on or after the install's first stock snapshot and end on or before its latest (`TPB-GRD-07` / PNR-3) - so a period that has not finished cannot be billed | `422 STORAGE_MEASURE_MISSING` · `basis` (location without width/depth, naming code and day; rate line without area, naming card and version); `422 STORAGE_LOCATION_SHARED` · `basis` (another owner holds stock in the location that day); `422 STORAGE_METHOD_INVALID` · `method` (`SQFT_ALLOCATED` not `PERIOD_END`); rate card: `422 RATE_CARD_ALLOCATED_AREA_REQUIRED` / `RATE_CARD_ALLOCATED_AREA_NOT_ALLOWED` · `lines[i].allocatedAreaSqFt`, `RATE_CARD_BANDS_NOT_AGEABLE` · `lines[i].agingBands`, `RATE_CARD_ALLOCATED_AREA_TIERED` · `lines[i].tierFrom` (a second tier for the charge and unit); `422 STORAGE_PERIOD_BEFORE_FIRST_SNAPSHOT` · `periodFrom` / `STORAGE_PERIOD_AFTER_LAST_SNAPSHOT` · `periodTo` (as every basis) | `chk_wh3_rate_card_lines_allocated_area`, `chk_wh3_storage_billing_lines_site`, `trg_wh3_storage_billing_lines_basis_guard` (`V531157`) | FR-288 |
| TPB-GRD-08 | Accessorial carries author, date (not future), reason; above `warehouse.3pl.accessorial.second_approval_threshold` the approver ≠ raiser | `422 WH3_ACCESSORIAL_REASON_REQUIRED` · `reason`; `403 WH3_ACCESSORIAL_SELF_APPROVAL` | `chk_wh3_accessorials_separation` | FR-291 |
| TPB-GRD-09 | Dispute: reason required; inside `warehouse.3pl.dispute.window_days`; run disputable; upheld by someone other than the raiser; withdrawn only by the raiser; resolution required to close | `422 WH3_DISPUTE_REASON_REQUIRED`, `422 WH3_DISPUTE_WINDOW_CLOSED` · `billingRunId`, `409 WH3_DISPUTE_RUN_NOT_DISPUTABLE`, `403 WH3_DISPUTE_SELF_UPHOLD`, `WH3_DISPUTE_WITHDRAW_NOT_RAISER`, `422 WH3_DISPUTE_RESOLUTION_REQUIRED` | `chk_wh3_disputes_separation`, `_withdrawn`, `_resolution` | FR-293 |
| TPB-GRD-10 | Every 3PL read, portal read included, is narrowed to the caller's own owner at the **query layer**; a negative test per endpoint | portal `requireOwnedBy` / `requireSameClient` → refusal, never a filtered UI | `Wh3plOwnerScopeContractTest` (ci-gate `warehouse-ratchets`) | FR-300, FR-284 |
| TPB-GRD-11 | Portal endpoints are gated by `wh3_clients:portal_access` and reuse the base/app screens' data; no second login | `403` | `@PreAuthorize` on `Wh3plPortalController` | FR-284 |
| TPB-GRD-12 | Freight rule mode ∈ {`AT_COST`, `COST_PLUS_PERCENT`, `COST_PLUS_FIXED`, `OWN_TARIFF`, `CLIENT_OWN_ACCOUNT`}, each mode carrying exactly its own term; no rule → refuse | `WH3_FREIGHT_NO_RULE`, `WH3_FREIGHT_NO_CARRIER_COST`, `WH3_FREIGHT_TARIFF_CARD_INVALID` | `wh3_freight_billing_rules` mode-shape CHECK, EXCLUDE per client | FR-295 |
| TPB-GRD-13 | An SLA definition names metric, target, comparison, window, calendar and an `SLA_CREDIT` penalty charge code | `422 SLA_PENALTY_CHARGE_CODE_INVALID` · `penaltyChargeCodeId`, `SLA_CALENDAR_UNAVAILABLE`, `SLA_CLIENT_OVERLAP` | — | FR-297 |
| TPB-GRD-14 | A client GST registration carries GSTIN, the warehouse as additional place of business, certificate, effective dates | `422 GSTIN_REQUIRED` / `GSTIN_INVALID` · `gstin` | — | FR-301 |

### 2.1 Unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| TPB-UNR-01 | A `whb_`/`wh_` FK to a `wh3_` table, a base or core import of `ai.warehouse3pl`, a migration below `V530000` naming `wh3_` | `Wh3plCouplingTest.shouldHaveNoUpwardForeignKey`, `shouldCrossOnlyThroughTheAllowList`; `WarehouseBaseCouplingTest`; the only link is `fk_wh3_clients_owner` → `whb_owners` | FR-281 |
| TPB-UNR-02 | Deleting, truncating or editing a billable event's measured columns; editing a `REVERSED`/`EXCLUDED` row | `BILLABLE_EVENT_APPEND_ONLY`, `BILLABLE_EVENT_IMMUTABLE`, `BILLABLE_EVENT_TERMINAL` (`V530030`, `V530101`) | FR-285, `L-2` |
| TPB-UNR-03 | Re-rating or editing an `APPROVED` run or its lines | `BILLING_RUN_FROZEN`, `BILLING_RUN_LINE_WRITE_ONCE`, `BILLING_RUN_STATUS_TRANSITION` (`V530040`) | FR-292 |
| TPB-UNR-04 | An upheld dispute editing a billed line | `Wh3plDisputeService.uphold` posts a credit event; run lines write-once | FR-293 |
| TPB-UNR-05 | An invoice, invoice number sequence or tax engine inside 3PL | `Wh3plCouplingTest.shouldCreateNoBillingObject`; numbers from base series via `Wh3plBillingSeriesProvisioner` | FR-294 |
| TPB-UNR-06 | Mutating an `ACTIVE` rate card's lines (escalation included) | escalation and edits go through `cloneVersion` → new `DRAFT` version | FR-296, FR-287 |
| TPB-UNR-07 | A tenant concept; a 3PL client as a tenant | one database per install; the client is an owner dimension (`OD-3`) | FR-303 |
| TPB-UNR-08 | A billed storage snapshot changing silently | base snapshot rows are superseded, never updated (`V500045`) | FR-289 |

## 3. T3 — Time rules

| ID | Rule | Clock | Changes | Job | Source |
|---|---|---|---|---|---|
| TPB-T3-01 | Daily storage snapshot per date × client × owner × warehouse × basis, carrying `oldest_receipt_date` (anniversary anchor), `age_days`, `outbox_cursor_at_computation`; a re-run supersedes | site day | new snapshot row | base nightly job (v1, `p2-28`); missed day → health signal (`V501125`) | FR-289, FR-288 |
| TPB-T3-02 | Contract notice | `contract_end_date − notice_period_days − warehouse.3pl.contract_notice.alert_lead_days` | nothing; alert | `Wh3plContractNoticeJob` | FR-282 |
| TPB-T3-03 | Onboarding task overdue | task due date | nothing; alert | `Wh3plOnboardingTaskOverdueJob` | FR-283 |
| TPB-T3-04 | Anniversary storage: each pallet billed for a storage month from its own receipt date | `oldest_receipt_date` | storage line | `Wh3plStorageBillingCalculator` | FR-288 |
| TPB-T3-05 | SLA measurement per window, storing numerator and denominator (percentage derived) | definition window + calendar | `wh3_sla_measurements` row; breach candidate | `Wh3plSlaMeasurementJob`, `Wh3plSlaCalendarVerdict` | FR-297 |
| TPB-T3-07 | **Scheduled monthly SLA / performance export** to the client: cadence monthly, recipients the client's own portal users only (scoped to the client's owner, `TPB-GRD-10`), produced by a platform report schedule | month end | an exported file per client | platform report scheduling — **not built** (`TPB-DIV-11`) | FR-298 |
| TPB-T3-06 | Client GST registration expiry | `effective_to − warehouse.3pl.gst_registration_expiry.alert_lead_days` | nothing; alert | `Wh3plClientGstRegistrationExpiryJob` | FR-301 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| TPB-T4-01 | a base outbox event of a subscribed code | one billable event at billable grain (owner, lot, LPN, warehouse, timestamps carried from the outbox row) | `Wh3plBillableEventSubscriber`, `Wh3plBillableEventMeter` | FR-285 |
| TPB-T4-02 | storage period approved, client below `minimum_monthly_charge` (`minimum_scope` `CLIENT`/`WAREHOUSE`) | one `MINIMUM_TRUEUP` event on the seeded true-up charge code with the arithmetic shown; visible, disputable, reversible | `Wh3plMinimumTrueUpService` | FR-290 |
| TPB-T4-03 | dock appointment detention / after-hours receipt | auto-captured accessorial written to `wh3_accessorials` with `source` `DOCK_DETENTION` / `AFTER_HOURS` — **producer:** warehouse core `WhDockAppointmentEvents` appends `dock.appointment.detention_started` inside the Depart transaction when `detention_minutes > 0` (quantity = minutes, MIN, subject the appointment; the seeded code now means *detention measured at Depart*); `receipt.line.confirmed` (one per GRN line). **Owner:** the single owner via ASN→PO or PO, else not emitted. **Consumer:** `WH3_ACCESSORIAL_CAPTURE` (own cursor, `V531158`, from the outbox head). **Grain:** one per appointment / one per GRN (first confirmed line's business time, calendar resolved for site + owner, `[open, close)`). **Pricing:** the client's rate line (`ACC_DETENTION` MIN / `ACC_AFTER_HOURS_RECEIPT` EA) — free quantity, rounding, min / max — never the whole dwell. **Free quantity is per capture** (one appointment / one GRN), not the run's per-period allowance: on the 1 EA after-hours line any `free_quantity` ≥ 1 means after-hours is never billed (S2-c). **Billability:** the run's own date rule (`Wh3plBillingRunRatingEngine.exclusionOn`) on the charge's date (detention: the site date at Depart; after-hours: the calendar date of the receipt's business time) — before go-live → `PRE_GO_LIVE`, before contract start / after contract end → `OUTSIDE_CONTRACT`, logged skip; current status is **not** read, so a capture replayed after offboarding still bills a charge dated inside the contract. The manual raise keeps its current-status rule (PROSPECT / OFFBOARDED refused) (S3 F2, R33). **Numbering:** `WH3-ACCESSORIAL` per company; a company with no series yet has it provisioned at capture by the event's `actorUserId` (the Depart user / GRN poster), exactly as the first manual raise does — a first automatic charge never dead-letters (S3 F1, replaces S2-b). **Actor:** none (`raised_by` NULL, "Automatic (<source>)" in grid / View / export), RAISED → normal Approve. **Dedupe:** `uk_wh3_accessorials_captured_subject (source, subject_type, subject_id)` + capture lock. **Failure:** unsupported version or no calendar → dead-letter (capture only); not a client / charge date not billed (PRE_GO_LIVE / OUTSIDE_CONTRACT) / no rate line (NOT_CONTRACTED) / within free time / within hours / setting off → logged skip. Settings `warehouse.3pl.accessorial.auto_capture_dock_detention` / `…auto_capture_after_hours` (default true) | wired — R33 #35 | FR-291 |
| TPB-T4-04 | dispute upheld | a reversing or credit billable event; billed line untouched | `Wh3plDisputeService.uphold` | FR-293 |
| TPB-T4-05 | run approved | one AR envelope `wh3_ar_handovers` (party, date, currency, one line per run line with revenue purpose code, SAC/HSN, qty, UoM, rate, amount, tax code; stable idempotency key, unique per `(billing_run_id, envelope_kind)` while not `VOIDED`); without accounting the same envelope exports as CSV (`getEnvelopeCsv`) and is marked posted manually | `Wh3plArHandoverDispatcher`, `Wh3plArAccountingSink`, `Wh3plArEnvelopes` | FR-294 |
| TPB-T4-06 | shipment with a freight rule | **`D-18` item 4:** the pass-through is metered **at despatch at a quoted amount from the 3PL's own tariff**; when the carrier invoice arrives the difference (markup included) is a **delta billable event in an open billing run** — a frozen run is never edited, no tolerance, no silent write-off (`Wh3plFreightBillingService` `meter` / `reconcile`, `:38-43`) | `Wh3plFreightBillingService` | FR-295 — **see `TPB-DIV-12`** |
| TPB-T4-10 | client offboarded | every live owner grant on the client's owner is **ended** (a future-dated one deleted), then the owner is **retired** — access beyond the client record goes too | `Wh3plClientService.java:375-395` (`closeOwnerAccess`) | FR-282 |
| TPB-T4-07 | confirmed breach with a penalty code (v3) | a negative billable event on the `SLA_CREDIT` code, subject to approval | not built — `§6` `TPB-DIV-05` | FR-299 |
| TPB-T4-08 | client profitability (v3) | metered revenue joined to labour minutes × loaded rate and snapshot × space cost | not built — `§6` `TPB-DIV-06` | FR-302 |
| TPB-T4-09 | VAS labour completed for a client owner | labour billable event priced by `Wh3plVasLabourPricingService` | `WH3_VAS_*` refusals | FR-285 |

## 5. T5 — Screen contract

| ID | Screen | Shows / offers | Permission | Source |
|---|---|---|---|---|
| TPB-T5-01 | WS-155 3PL Clients | ladder actions Onboard / Go live / Suspend / Terminate / Offboard; parties tab | `wh3_clients:*` | FR-282 |
| TPB-T5-02 | WS-156 / WS-157 Onboarding Templates / Tasks | template tasks; task complete / reopen; overdue tile | `wh3_onboarding_*` | FR-283 |
| TPB-T5-03 | WS-158 / WS-159 Charge Codes / Rate Cards | code master; card versions, clone, activate, expire; bands; the rate-card export is **card-level** (one row per card version, the grid's columns) - line fields (rate, tier, basis, allocated area) are not exported (S4 F4, R33 #30) | `wh3_charge_codes:*`, `wh3_rate_cards:*` | FR-286, FR-287 |
| TPB-T5-04 | WS-160 Billable Events | log-style grid; Reverse / Exclude (reason) | `wh3_billable_events:*` | FR-285 |
| TPB-T5-05 | WS-161 Storage Billing Periods | compute / approve / recompute; true-up status; the Compute basis picker offers all seven bases incl. `SQFT_OCCUPIED` / `SQFT_ALLOCATED` (R33 #30); WS-159 Rate Cards shows and edits `allocatedAreaSqFt` on an `SQFT_ALLOCATED` line only (no ageing bands there) | `wh3_storage_billing_periods:*` | FR-288, FR-290 |
| TPB-T5-06 | WS-162 Billing Runs / WS-170 AR Handover Queue | rate / re-rate / approve / cancel / reverse; unrated count; handover retry / void | `wh3_billing_runs:*`, `wh3_ar_handovers:*` | FR-292, FR-294 |
| TPB-T5-07 | WS-163 Accessorials / WS-164 Disputes | raise (keyed in seconds), approve / reject; dispute ladder | `wh3_accessorials:*`, `wh3_disputes:*` | FR-291, FR-293 |
| TPB-T5-08 | WS-165 Freight Billing Rules | one rule per client, mode + term | `wh3_freight_billing_rules:*` | FR-295 |
| TPB-T5-09 | WS-166 / WS-167 / WS-168 SLA | definitions; measurements (numerator / denominator); breaches confirm / waive | `wh3_sla_*` | FR-297 |
| TPB-T5-10 | WS-172 Client Portal | stock, inbound, orders, shipments, billing, disputes (raise), performance (trend + failing orders), documents — own owner only | `wh3_clients:portal_access` | FR-284, FR-298, FR-300 |
| TPB-T5-11 | WS-169 Client GST Registrations | registrations, certificate, expiry tile | `wh3_client_gst_registrations:*` | FR-301 |
| TPB-T5-12 | WS-171 Client Profitability | v3 | — | FR-302 |

## 6. Code divergences

| ID | FR says | Code has (grep) | Source |
|---|---|---|---|
| TPB-DIV-01 | Storage billing over **seven** bases incl. square feet occupied and allocated | `Wh3plStorageBillingVocabulary` has 5 bases: `PALLET`, `LOCATION`, `UNIT`, `WEIGHT`, `CUBIC` — **Triage 2026-10-23: FIX-CODE** — owner `P5-04` #30 — **CLOSED R33 (2026-10-26):** seven bases built (`SQFT_OCCUPIED`, `SQFT_ALLOCATED` — the applied spelling; never a second one), `TPB-GRD-07a`, `V531157` | FR-288 |
| TPB-DIV-02 | Method "daily average" | code value is `AVERAGE_DAILY` (name only; behaviour present) — **Triage 2026-10-23: AMEND-SPEC** — rule: the FRD's *daily average* method is stored as the code value `AVERAGE_DAILY` (label "Daily average"); same behaviour, the value is the build's. Evidence: `Wh3plStorageBillingCalculator.java:99`, `:121` | FR-288 |
| TPB-DIV-03 | Portal v1.1: inbound ASN creation, outbound order creation + CSV upload + cancel-while-unallocated, returns | `Wh3plPortalController` exposes reads (stock, inbound, orders, shipments, billing, documents, performance) and dispute raise only; no ASN / order create, upload, cancel or returns endpoint — **Triage 2026-10-23: AMEND-SPEC** — rule: the portal stays a read surface plus dispute raise; a client user creates ASNs and outbound orders through the existing screens' own verbs under owner scope (`FR-284`: *a permission surface over the existing screens*). Evidence: `issues/p5-08.md:173` (recorded at build, *portal_access is read-only by construction*); `FR-284` amended. reviewer-confirm | FR-284 |
| TPB-DIV-04 | Client sees *their* order numbers | per-client series provisioned at onboard (`whb_number_series`); whether portal order / ASN numbers draw from it is unverified because portal creation is absent (`TPB-DIV-03`) — **Triage 2026-10-23: FIX-CODE** — owner `P5-01` #17, reopened: client-created documents draw from the per-client series, proved by a test | FR-283 |
| TPB-DIV-05 | v3 SLA credit as negative event | `Wh3plSlaBreachService` has `confirm` / `waive` only; the `SLA_CREDIT` code and FK exist (`Wh3plSlaDefinition.penaltyChargeCodeId`) — **Triage 2026-10-23: CARRIED** — `P6-07` #122 (v3, `FR-299`) | FR-299 |
| TPB-DIV-06 | v3 client profitability | no `Profitab*` class or `wh3_rpt_*profit*` object in `warehouse-3pl/backend/src/main` — **Triage 2026-10-23: CARRIED** — `P6-07` #122 (v3, `FR-302`) | FR-302 |
| TPB-DIV-07 | v3 rate escalation | no escalation job; only manual `cloneVersion` (comment names `P6-07`) — **Triage 2026-10-23: CARRIED** — `P6-07` #122 (v3, `FR-296`) | FR-296 |
| TPB-DIV-09 | Auto-captured accessorials (detention from the dock appointment, after-hours from the receipt timestamp) | `chk_wh3_accessorials_source` admits `DOCK_DETENTION` / `AFTER_HOURS` and `Wh3plBillingRunVocabulary` names them, but no class writes either source; base event `dock.appointment.detention_started` (`V500040`) has no 3PL subscriber — **Triage 2026-10-23: FIX-CODE** — owner `P5-05` #35 (`FR-291`), reopened — **CLOSED R33 (2026-10-26):** producer at Depart, `WH3_ACCESSORIAL_CAPTURE` subscriber, system-raised rows and dedupe key, `ACC_AFTER_HOURS_RECEIPT`, two settings (`TPB-T4-03`), `V531158` | FR-291 |
| TPB-DIV-10 | A separate permission for reversing an approved billing run (`TPB-T2-10`) | reverse is gated by `wh3_billing_runs:create` (`Wh3plBillingRunController.java:249-250`), so run creators can reverse frozen runs; `P5-05` owns the decision (keep `:create` with a written reason, or a `:reverse` verb in the next free `V531…` with `permission_dependencies`) — **Triage 2026-10-23: FIX-CODE** — owner `P5-05` #35, reopened — **CLOSED R33 (2026-10-26):** `wh3_billing_runs:reverse` verb (`TPB-T2-10`), `V531158` | FR-292 |
| TPB-DIV-11 | A scheduled monthly export (`TPB-T3-07`) | not built: needs a platform `ReportType` and a recipient-aware data-provider SPI (`issues/p5-08.md:172`) — **Triage 2026-10-23: FIX-CODE** — owner `P5-07` #44 (`FR-298`), reopened; blocked on the platform `ReportType` commit (as `#185`) | FR-298 |
| TPB-DIV-12 | `D-18` item 4: the freight quote is taken from **the 3PL's own tariff** | the build meters the quote persisted by `P5-11` (`wh_rate_quotes`) under the client's mode; only `OWN_TARIFF` prices from the 3PL's rate card. `P5-06` confirms the quote source per mode (acceptance item added) — **Triage 2026-10-23: FIX-CODE** — owner `P5-06` #39, reopened | FR-295 |
| TPB-DIV-08 | Module seeds into base registries guard ownership (`D-16` item 5, `V521000:117` pattern) | grep for an owning-module conflict guard in `warehouse-3pl` migrations finds none (india: 15 files; example adapter: 1) — **Triage 2026-10-23: FIX-CODE** — owner `P5-01` #17 (`FR-281`), reopened | FR-281 |

## 7. Out of scope

Invoice, numbering and tax (accounting, `D-16` item 6 — handover points only); multi-tenant SaaS (`FR-440`); mobile (`D-16` item 7).

## 8. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived for R30 `CP-FR-007` row 16 (`D-17` item a) |
| 2026-10-23 | R31: `F-CB-003` (§1.3 T2 table; `TPB-DIV-10`); `F-CB-004` (`TPB-T1-03` predicate and code, `TPB-T1-06` guards, `TPB-T4-10`); `F-CB-005` (one-way ladder, `TPB-T1-09a` expire); `F-CB-011` (`TPB-T3-07`, `TPB-DIV-11`); `D-18` item 4 (`TPB-T4-06`, `TPB-DIV-12`); `TPB-OPEN-01`…`-03` decided |
| 2026-10-26 | R33 #30 P5-04: `TPB-DIV-01` / `TPB-OPEN-01` closed (codes spelled `SQFT_*`), `TPB-GRD-07` amended, `TPB-GRD-07a` square-feet measurement rules added, `TPB-T5-05` picker; `V531157` |
| 2026-10-26 | R33 #30 P5-04 S4: `TPB-GRD-07a` amended - `SQFT_ALLOCATED` one tier per (charge, unit) (`RATE_CARD_ALLOCATED_AREA_TIERED`, F1), period-range bound recorded (F3); `TPB-T5-03` card-level export, line fields not exported (F4) |

## 9. Invariants and scenarios

`L-1`, `L-2`; scenarios `WH-SC-233`, `WH-SC-234`, `WH-SC-235`, `WH-SC-236`, `WH-SC-237`, `WH-SC-238`, `WH-SC-244`, `WH-SC-333`, `WH-SC-334`, `WH-SC-336`, `WH-SC-140`, `WH-SC-412`, `WH-SC-377`.

## 10. Open rows

| ID | Question | Default | Source |
|---|---|---|---|
| TPB-OPEN-01 | Square-feet bases (`TPB-DIV-01`): add to the vocabulary or restate the FR at five bases | **DECIDED R31 (2026-10-23), default replaced:** build the FR's seven bases — add `SQFT_ALLOCATED` (contracted area on the rate card) and `SQFT_OCCUPIED` (the existing `whb_locations.width_cm` × `depth_cm` - no base column added); the FR is not restated to five. `P5-04` acceptance item. **Built R33 (2026-10-26), closed** — spelling `SQFT_*` as the code and V530021 always had it (`TPB-GRD-07a`) | FR-288 |
| TPB-OPEN-02 | Portal write surfaces (`TPB-DIV-03`): `p5-08` is PARTIALLY VOID (`D-16`, the trade-customer persona only) — does its surviving scope still owe ASN / order create, upload, cancel and returns | **DECIDED R31 (2026-10-23): default stands** — `p5-08` still owes ASN and order create, CSV upload, cancel-while-unallocated and returns; `D-16` removed only the trade-customer persona | FR-284 |
| TPB-OPEN-03 | Freight reconciliation: the FR gives no tolerance or timing for "reconciled when the carrier invoice lands" | **DECIDED R31 (2026-10-23): default stands**, with `D-18` item 4 — the carrier-invoice difference (markup included) is an adjusting billable event in an open run; frozen runs are never edited; no tolerance, no silent write-off (`TPB-T4-06`) | FR-295 |
| 2026-10-26 | R33 #35 P5-05: `TPB-T2-10` amended (`:reverse`), `TPB-DIV-10` closed; `TPB-T4-03` expanded (producer, timing, owner, grain, pricing, system actor, dedupe, failure policy), `TPB-DIV-09` closed; `V531158` |
| 2026-10-26 | R33 #35 P5-05 S4 (S3 F1 / F2 / S2-c): `TPB-T4-03` gains **Numbering** (series provisioned at capture by the event's actor — replaces S2-b), **Billability** (the run's date rule on the charge date, not current status) and the per-capture free-quantity meaning; no migration |
