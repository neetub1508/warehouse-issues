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
| **Workflow** | Client: `PROSPECT` → `ONBOARDING` → `LIVE` ⇄ `SUSPENDED` → `TERMINATING` → `OFFBOARDED`. Meter: event `METERED` → `RATED` → `BILLED`, or `REVERSED` / `EXCLUDED`. Run: `DRAFT` → `RATED` → `APPROVED` → `INVOICED`, or `CANCELLED`. Around them: rate cards, storage periods, accessorials, disputes, AR handovers, SLA, GST registrations, portal |
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
| TPB-T1-02 | `PROSPECT` | Onboard | `ONBOARDING` | template chosen; series company resolvable | `Wh3plClientService.onboard` | onboarding tasks copied from `wh3_client_onboarding_template_tasks`; per-client number series provisioned in `whb_number_series` (pad `warehouse.3pl.client_series.pad_length`) | WS-155 | FR-283 |
| TPB-T1-03 | `ONBOARDING` | Go live | `LIVE` | every onboarding task `COMPLETED`, else `409 CLIENT_NOT_ONBOARDING` · `status` | `goLive` | `go_live_date` stamped | WS-155 | FR-282, FR-283 |
| TPB-T1-04 | `LIVE` | Suspend | `SUSPENDED` | — | `suspend` | — | WS-155 | FR-282 |
| TPB-T1-05 | `LIVE` · `SUSPENDED` | Terminate | `TERMINATING` | `contract_end_date` required (`V531152`) | `terminate` | notice clock `TPB-T3-02` | WS-155 | FR-282 |
| TPB-T1-06 | `TERMINATING` | Offboard | `OFFBOARDED` | — | `offboard` | terminal | WS-155 | FR-282 |
| TPB-T1-07 | `OPEN` | Complete onboarding task | `COMPLETED` (re-openable) | — | `wh3_onboarding_tasks` | audit `WH3_ONBOARDING_TASK_COMPLETED` | WS-157 | FR-283 |
| TPB-T1-08 | — | Create rate card / clone version | `DRAFT` | one draft per card, else `409 RATE_CARD_DRAFT_EXISTS` · `status`; ladder complete, else `RATE_CARD_LADDER_INCOMPLETE` | `Wh3plRateCardService.create` / `cloneVersion` | version n+1 copies lines, bands, clients | WS-159 | FR-287, FR-296 |
| TPB-T1-09 | `DRAFT` | Activate | `ACTIVE` | client overlap refused `409 RATE_CARD_CLIENT_OVERLAP` · `clientIds` | `activate` | the prior `ACTIVE` version → `SUPERSEDED` at the new `effective_from` | WS-159 | FR-287 |
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

## 2. Guards

| ID | Predicate (must hold to proceed) | Refusal: HTTP · code · field | DB backstop | Source |
|---|---|---|---|---|
| TPB-GRD-01 | Client code upper-case, unique; owner unique and immutable; a client binds one base owner | `422 CLIENT_CODE_EXISTS` · `clientCode`; `409 OWNER_ALREADY_BOUND` · `ownerId`; `422 OWNER_IMMUTABLE` | `uk_wh3_clients_owner_id`, trigger immutability | FR-282, FR-303 |
| TPB-GRD-02 | Contract end > start; notice ≥ 0; billing day inside the cycle; credit limit and minimum ≥ 0 | `422` field-keyed | `chk_wh3_clients_*` | FR-282 |
| TPB-GRD-03 | A charge code carries category, default UoM, recurring / pass-through / taxable flags, tax code, SAC/HSN and a **`revenue_purpose_code`** — never a GL account id | `422` field-keyed | `wh3_charge_codes.revenue_purpose_code NOT NULL` | FR-286 |
| TPB-GRD-04 | An event is metered once per `(source_system, source_event_key)` | idempotent replay returns the existing row | `uk_wh3_billable_events_source` | FR-285 |
| TPB-GRD-05 | Rating resolves the card **version live on the event's date**, most-specific-wins; no match → refuse, never zero | `422 WH3_UNRATED_EVENT` naming `(chargeCode, uom, basis, date)` (`Wh3plUnratedEventException`) | — | FR-287 |
| TPB-GRD-06 | A rate card's bands do not overlap; an inheriting card overrides lines of its parent only | `RATE_CARD_BAND_OVERLAP` | — | FR-287 |
| TPB-GRD-07 | A storage period reads a snapshot for every day; method ∈ {`PERIOD_END`, `PERIOD_START`, `ANNIVERSARY`, `AVERAGE_DAILY`, `SPLIT_MONTH`}; basis measurable; periods do not overlap | `STORAGE_PERIOD_SNAPSHOT_DAY_MISSING`, `STORAGE_METHOD_INVALID`, `STORAGE_BASIS_NOT_MEASURABLE`, `STORAGE_PERIOD_OVERLAP` | — | FR-288, FR-289 |
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
| TPB-T3-06 | Client GST registration expiry | `effective_to − warehouse.3pl.gst_registration_expiry.alert_lead_days` | nothing; alert | `Wh3plClientGstRegistrationExpiryJob` | FR-301 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| TPB-T4-01 | a base outbox event of a subscribed code | one billable event at billable grain (owner, lot, LPN, warehouse, timestamps carried from the outbox row) | `Wh3plBillableEventSubscriber`, `Wh3plBillableEventMeter` | FR-285 |
| TPB-T4-02 | storage period approved, client below `minimum_monthly_charge` (`minimum_scope` `CLIENT`/`WAREHOUSE`) | one `MINIMUM_TRUEUP` event on the seeded true-up charge code with the arithmetic shown; visible, disputable, reversible | `Wh3plMinimumTrueUpService` | FR-290 |
| TPB-T4-03 | dock appointment detention / after-hours receipt | auto-captured accessorial written to `wh3_accessorials` with `source` `DOCK_DETENTION` / `AFTER_HOURS` | not wired — `§6` `TPB-DIV-09` | FR-291 |
| TPB-T4-04 | dispute upheld | a reversing or credit billable event; billed line untouched | `Wh3plDisputeService.uphold` | FR-293 |
| TPB-T4-05 | run approved | one AR envelope `wh3_ar_handovers` (party, date, currency, one line per run line with revenue purpose code, SAC/HSN, qty, UoM, rate, amount, tax code; stable idempotency key, unique per `(billing_run_id, envelope_kind)` while not `VOIDED`); without accounting the same envelope exports as CSV (`getEnvelopeCsv`) and is marked posted manually | `Wh3plArHandoverDispatcher`, `Wh3plArAccountingSink`, `Wh3plArEnvelopes` | FR-294 |
| TPB-T4-06 | shipment with a freight rule | pass-through metered at the quoted amount; reconciled when the carrier cost lands | `Wh3plFreightBillingService` | FR-295 |
| TPB-T4-07 | confirmed breach with a penalty code (v3) | a negative billable event on the `SLA_CREDIT` code, subject to approval | not built — `§6` `TPB-DIV-05` | FR-299 |
| TPB-T4-08 | client profitability (v3) | metered revenue joined to labour minutes × loaded rate and snapshot × space cost | not built — `§6` `TPB-DIV-06` | FR-302 |
| TPB-T4-09 | VAS labour completed for a client owner | labour billable event priced by `Wh3plVasLabourPricingService` | `WH3_VAS_*` refusals | FR-285 |

## 5. T5 — Screen contract

| ID | Screen | Shows / offers | Permission | Source |
|---|---|---|---|---|
| TPB-T5-01 | WS-155 3PL Clients | ladder actions Onboard / Go live / Suspend / Terminate / Offboard; parties tab | `wh3_clients:*` | FR-282 |
| TPB-T5-02 | WS-156 / WS-157 Onboarding Templates / Tasks | template tasks; task complete / reopen; overdue tile | `wh3_onboarding_*` | FR-283 |
| TPB-T5-03 | WS-158 / WS-159 Charge Codes / Rate Cards | code master; card versions, clone, activate, expire; bands | `wh3_charge_codes:*`, `wh3_rate_cards:*` | FR-286, FR-287 |
| TPB-T5-04 | WS-160 Billable Events | log-style grid; Reverse / Exclude (reason) | `wh3_billable_events:*` | FR-285 |
| TPB-T5-05 | WS-161 Storage Billing Periods | compute / approve / recompute; true-up status | `wh3_storage_billing_periods:*` | FR-288, FR-290 |
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
| TPB-DIV-01 | Storage billing over **seven** bases incl. square feet occupied and allocated | `Wh3plStorageBillingVocabulary` has 5 bases: `PALLET`, `LOCATION`, `UNIT`, `WEIGHT`, `CUBIC` | FR-288 |
| TPB-DIV-02 | Method "daily average" | code value is `AVERAGE_DAILY` (name only; behaviour present) | FR-288 |
| TPB-DIV-03 | Portal v1.1: inbound ASN creation, outbound order creation + CSV upload + cancel-while-unallocated, returns | `Wh3plPortalController` exposes reads (stock, inbound, orders, shipments, billing, documents, performance) and dispute raise only; no ASN / order create, upload, cancel or returns endpoint | FR-284 |
| TPB-DIV-04 | Client sees *their* order numbers | per-client series provisioned at onboard (`whb_number_series`); whether portal order / ASN numbers draw from it is unverified because portal creation is absent (`TPB-DIV-03`) | FR-283 |
| TPB-DIV-05 | v3 SLA credit as negative event | `Wh3plSlaBreachService` has `confirm` / `waive` only; the `SLA_CREDIT` code and FK exist (`Wh3plSlaDefinition.penaltyChargeCodeId`) | FR-299 |
| TPB-DIV-06 | v3 client profitability | no `Profitab*` class or `wh3_rpt_*profit*` object in `warehouse-3pl/backend/src/main` | FR-302 |
| TPB-DIV-07 | v3 rate escalation | no escalation job; only manual `cloneVersion` (comment names `P6-07`) | FR-296 |
| TPB-DIV-09 | Auto-captured accessorials (detention from the dock appointment, after-hours from the receipt timestamp) | `chk_wh3_accessorials_source` admits `DOCK_DETENTION` / `AFTER_HOURS` and `Wh3plBillingRunVocabulary` names them, but no class writes either source; base event `dock.appointment.detention_started` (`V500040`) has no 3PL subscriber | FR-291 |
| TPB-DIV-08 | Module seeds into base registries guard ownership (`D-16` item 5, `V521000:117` pattern) | grep for an owning-module conflict guard in `warehouse-3pl` migrations finds none (india: 15 files; example adapter: 1) | FR-281 |

## 7. Out of scope

Invoice, numbering and tax (accounting, `D-16` item 6 — handover points only); multi-tenant SaaS (`FR-440`); mobile (`D-16` item 7).

## 8. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived for R30 `CP-FR-007` row 16 (`D-17` item a) |

## 9. Invariants and scenarios

`L-1`, `L-2`; scenarios `WH-SC-233`, `WH-SC-234`, `WH-SC-235`, `WH-SC-236`, `WH-SC-237`, `WH-SC-238`, `WH-SC-244`, `WH-SC-333`, `WH-SC-334`, `WH-SC-336`, `WH-SC-140`, `WH-SC-412`, `WH-SC-377`.

## 10. Open rows

| ID | Question | Default | Source |
|---|---|---|---|
| TPB-OPEN-01 | Square-feet bases (`TPB-DIV-01`): add to the vocabulary or restate the FR at five bases | restate is the user's call; code stays at five | FR-288 |
| TPB-OPEN-02 | Portal write surfaces (`TPB-DIV-03`): `p5-08` is PARTIALLY VOID (`D-16`, the trade-customer persona only) — does its surviving scope still owe ASN / order create, upload, cancel and returns | yes; `p5-08` owes them | FR-284 |
| TPB-OPEN-03 | Freight reconciliation: the FR gives no tolerance or timing for "reconciled when the carrier invoice lands" | difference posted as an adjusting billable event, no tolerance | FR-295 |
