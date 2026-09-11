# Global settings and resolved warehouse behaviour

**Status: adopted requirements, 2026-09-11. No application implementation is claimed.**

This closes the client-choice questions left by the existing reviews. DECISIONS adopts these resolutions. Existing historical review findings remain evidence; they do not reopen a decision below. Product defaults below are deterministic starting values, not legal or industry mandates.

## Settings page and change contract

Use the existing Global/Admin Settings page, **Warehouse** tab (`AdminSettingsWarehouseTab`), with Base, Operations, Cost & Accounting, Documents and Optional capabilities sections. Reuse typed `admin_settings` seeds: base keys in the already assigned V501100, app keys in V511200. Store default, type and validation with each key. Do not create a second settings store. Site/item/owner exceptions remain in their existing policy tables; the global page links to scoped policies and previews the effective value, source and precedence.

Both `admin_settings:edit` and `whb_settings:edit` are required to change warehouse settings, including through imports/API. P0-15 seeds the warehouse permission and dependency. Read access follows existing platform settings permissions; operational users see only the effective non-secret policy relevant to their authorized records. Never show another owner/site while previewing scope. Provider credentials stay in the existing secure provider profile, not a setting value or export.

Save a related group atomically with an expected revision. Invalid fields return field-level errors with allowed values; stale revision returns a conflict and current non-secret revision. Record actor, time, reason, before/after, scope and revision. Restore default is a new audited change. Missing optional configuration uses the declared default; corrupt stored configuration blocks the affected operation with an admin diagnostic. Unknown keys and unavailable capabilities are rejected by the API as well as the UI.

Effective policy resolution uses the existing most-specific policy rules and rejects equal-rank overlap at save. NULL inherits; zero/false never means inherit. Persist the effective policy/version on newly created operational work. Old work retains it; changing a default neither rewrites movements nor extends reservations nor re-costs history. Permissions, period lock, current registration and safety eligibility are rechecked at the commit/external-effect boundary. Disabling a capability blocks new intake but preserves authorized completion, compensation, retry and reconciliation of existing records. No switch changes module ownership, ledger invariants, owner scope, audit retention or idempotency.

## Complete settings catalogue for this amendment

| Key | Default | Allowed values / validation | Owner | Effect / fallback |
|---|---|---|---|---|
| warehouse.negative_stock.default_mode | BLOCK | BLOCK / WARN / ALLOW | Base / P0-15; policy P1-03 | WARN requires explicit acknowledgement and override permission; ALLOW still requires an explicit matching policy and audit. Never auto-reserve shortage. |
| warehouse.reservation.default_ttl_minutes | 30 | integer 1–10080 | Base / P0-15; P0-09 | Only new reservations inherit it; extensions are explicit, authorized and retain history. |
| warehouse.outbox.max_attempts | 10 | integer 1–100 | Base / P0-15; P0-11 | Subscription-specific value wins. Exhausted work enters retained failed queue; retry keeps original event key. |
| warehouse.port.rejected_queue_threshold | 10 | integer 1–10000 | Base / P0-15; P0-14 | Alert at count >= threshold; alert once per breach episode, resolve below threshold; no automatic discard. |
| warehouse.position.max_contention_retries | 3 | integer 0–10 | Base / P0-15; P0-03 | Bounded transaction retries only; exhaustion returns retryable conflict with the same idempotency key. |
| warehouse.outbox.max_cursor_lag | 1000 | integer 1–1000000 events | Base / P0-15; P0-11 | Measures pending event sequence distance; alert on breach, recovery below threshold. Never advance a cursor to silence an alert. |
| warehouse.period.soft_close_requires_approval | true | locked true | Base / P0-15; P0-07 | Display the rule read-only. No setting permits a hard-close write or maker self-approval. |
| warehouse.blocked_movement.alert_minutes | 15 | integer 1–10080 | Base / P0-15; P0-13 | Alert once when an unresolved blocked movement's age exceeds the horizon; recovery on resolution. Never resolves, posts or discards the movement (RE-007). No body states a number: default and range mirror warehouse.tasks.blocked_alert_minutes. |
| warehouse.short_pick.auto_count | false | boolean; install scope only | Base / P0-15; P2-09 | On: a confirmed short pick auto-creates a cycle-count task for the short location (FR-185). Off: the other short-pick outcomes are unchanged. Never adjusts stock itself (RA-006). No body states a default: off, because FR-185 makes it an opt-in switch. |
| warehouse.port.max_batch_size | 400 | integer 1–10000 movements | Base / P0-15; P0-08 | A batch above the value is refused 422 BATCH_TOO_LARGE before any movement posts; a repeated batch_reference still returns its stored result (RD-004). Default is the batch size P0-08's acceptance test uses, per the register; the range is this catalogue's choice. |
| warehouse.adjustment.default_threshold_value | 0 | decimal ≥ 0, DECIMAL(19,4), company base currency | Base / P0-15; P2-01 | Seeds the all-null wh_adjustment_approval_policies row; scoped rows win. Above the resolved threshold, an adjustment requires approval; explicit zero makes every valued adjustment require approval; never auto-approves (RA-008). No body states a default: zero, because an approval amount is a customer financial fact. |
| warehouse.accounting.mode | STANDALONE | STANDALONE / INTEGRATED | App / P1-20; P2-18 | Integrated requires tested contract; disable pauses new delivery, preserves accepted and pending envelopes for reconciliation. |
| warehouse.tax.mode | MANUAL_EVIDENCE | MANUAL_EVIDENCE / PROVIDER / NONE | App / P1-20; P2-25; P4-01 | Provider profile required for PROVIDER. Manual mode cannot finalize a taxable invoice without an external document; stock-only receipt remains supported. |
| warehouse.cost.exchange_rate_source | SOURCE_RATE | SOURCE_RATE / PROVIDER_RATE | App / P1-20; P2-16 | Provider failure blocks valuation posting requiring a rate. Explicit authorized source rate with evidence is a separate selection, never silent fallback. |
| warehouse.labels.lpn_format | INTERNAL_CODE128 | INTERNAL_CODE128 / GS1_128 | App / P1-20; P2-14; P3-24 | GS1 unavailable until allocator/parser readiness; profile includes valid prefix and counter range. Never reset or recycle issued identifiers. |
| warehouse.receiving.over_receipt_percent | 0 | decimal 0–100 inclusive | App / P1-20; P1-11; P1-12 | Use PO line, PO header, item, warehouse, global in that order; NULL inherits, explicit zero blocks over-receipt; percentage, not fraction. |
| warehouse.expiry.near_expiry_days | 45 | integer 0–3650 | App / P1-20; P2-05 | Item-site then item then global; zero means only today. Alert uses site business date, never changes expiry or FEFO eligibility. |
| warehouse.approval.pending_alert_hours | 24 | integer 1–720 | App / P1-20; P2-23 | Escalate a pending approval after elapsed hours; never auto-approve. One alert per pending episode. |
| warehouse.tasks.blocked_alert_minutes | 15 | integer 1–10080 | App / P1-20; P0-10 | Alert supervisor after elapsed blocked duration; retain task state and ownership. |
| warehouse.dropship.enabled | false | boolean; v2 capability required | App / P1-20; P5-09 | Disable blocks new drop-ship orders; linked in-flight confirmations, reversals and reconciliation remain available. |
| warehouse.regulated_profile | NONE | NONE / tested profile identifier | App / P1-20; P4-13 | A profile supplies validated licence, traceability, recall and retention rules. An incomplete profile cannot be enabled or advertised as supported. |

A provider selection is a reference to an installed, enabled, tested registry profile; blank is permitted while the capability is off. Activation validates the required directions/features, profile validity and connectivity. It does not ask an implementer to choose a vendor. Retry never changes an accepted envelope or its identity. Configuration import previews a diff, remaps identifiers, excludes credentials, checks capabilities and permissions, and commits atomically only when all selected rows validate.

## Resolved questions, reasons and implementation consequences

### OD-1 — resolved

Warehouse owns quantity and cost. Default STANDALONE; INTEGRATED requires an installed, tested accounting adapter that accepts authoritative extended values and stable idempotency keys. Missing capabilities block activation, not standalone stock posting. Reciprocal work in another repository remains an external integration dependency, not an unanswered warehouse decision.

### OD-2 — resolved

Keep vehicle inventory in its existing authority in v1/v2. In v3 offer an opt-in adapter only after serial, custody, reconciliation, rollback and source-write-exclusion acceptance passes. No automatic migration and no dual writer.

### OD-3 — resolved

One database per customer installation. A 3PL client is an owner with enforced row scope, never a database tenant. Configuration export/import is supported through the existing task with identifier remapping and no secrets.

### OD-4 — resolved

warehouse-base keeps its counterparty master. Other products join through external references; no upward foreign key. A future extraction must preserve identifiers and port compatibility; it is not a customer toggle.

### OD-8 — resolved

Use existing authenticated users and movement permissions in v1. Separate service consumers remain capability-gated to the v3 identity adapter with revocation, scope and audit tests. No anonymous/API-key shortcut and no warehouse-owned duplicate identity store.

### OD-9 — resolved

Warehouse does not implement its own tax calculation engine. PROVIDER uses a tested accounting/localisation provider; MANUAL_EVIDENCE records an externally issued document and its totals; NONE permits only operations requiring no tax document. Never silently treat missing tax as zero. Conditional engine schema remains documented as reserved history, with no active build obligation.

### OD-16 — resolved

Stored unit_cost and layer_value are in company base currency. Preserve original currency, original amount, positive exchange_rate and rate evidence on the source snapshot; rate is base units per one original-currency unit and is frozen at post. Only base-currency input may default to rate 1. SOURCE_RATE is the standalone default; PROVIDER_RATE is optional after capability validation. No direct read of accounting tables.

### OD-17 — resolved

v1 ships an internal Code-128 LPN label encoding lpn_code and resolvable by the v1 scanner. GS1-128/SSCC is an optional v1.1 capability enabled only when the existing allocator and parser tasks both pass. All eleven document kinds remain in v1; GS1 symbology is not falsely promised in v1. Existing labels remain resolvable after a setting change.

### OD-18 — resolved

v2 drop shipment uses a SUPPLIER-to-CUSTOMER virtual movement with purchase and demand line references and required lot/serial evidence, without changing physical on-hand. Default disabled; refuse in v1 or when the adapter is unavailable. Receipt/dispatch confirmations are idempotent and reversal follows the original links.

### OD-19 — resolved

Changing registered branch across GSTINs is allowed only with zero on-hand and no open reservations, in-flight transfers, counts or unposted warehouse documents tied to the old registration. Otherwise refuse with actionable dependency links; use the existing transfer/settlement workflow. Maker-checker and effective history are mandatory; there is no bypass switch.

### Negative stock and available-to-promise — resolved contradiction

The former formula permitted negative on-hand but required its subtraction result to remain nonnegative. Distinguish **signed balance** from **allocatable quantity**. For the same owner/site/item and applicable stock dimensions, let Q be allocatable-status physical on-hand and R open reservations. Display signed balance Q−R (including a shortage), but use `available_to_promise = max(0, Q−R)` for new allocation. A new reservation must fit the un-clamped positive free quantity under the writer's lock; clamping must never authorize an extra reservation. An existing reservation is consumed/released atomically with its dispatch.

BLOCK refuses physical issues producing negative on-hand. WARN requires policy eligibility, explicit acknowledgement, reason and override permission; ALLOW permits the eligible issue without acknowledgement but records the same policy and shortage audit. Neither mode may consume quantity protected by another holder's reservation: refuse or perform the existing authorized explicit release first. Physical negative inventory is shown as debt and can be corrected only by a subsequent ledger movement. Serial-controlled unique units cannot be issued twice under any policy. Default BLOCK makes the ordinary path unchanged. A database constraint on raw signed availability must not contradict the approved negative-stock path; service/transaction guards enforce allocations and the immutable ledger reconstructs the signed position. P0-03 and P1-03 own this distinction.

### Cost, value and currency — complete answer

Keep the already declared valuation grain `(company, owner, item, site)` and current category-at-occurred-at policy resolution. Weighted average and FIFO ship in v1, standard with variance in v1.1, LIFO never. Changing method is effective-dated with the existing controlled transition/revaluation workflow, not retroactive. Stored unit cost is base currency, with original source currency/amount/rate retained as evidence. For USD 42 at INR 88.415 per USD, base unit cost is INR 3713.430000; preserve USD 42 and 88.41500000. Never multiply an already base-valued unit_cost by the exchange rate again. The adapter must explicitly normalize its source price before submitting a base-valued movement. Missing foreign rate is a validation failure before any stock or cost write.

Value-only lines conserve signed extended value by currency using VALUE_OFFSET and the precision/rounding rules already adopted. Refuse a mixed quantity/value-only movement, missing value counterpart or rounding imbalance. Preserve separate, linked movements when both effects are required. No configurable tolerance can waive ledger conservation. A ZERO_BAILMENT movement does not generate a valued accounting envelope. Integrated delivery carries frozen extended_value as authority, source posting_date, currency and cost_basis; the receiver must not re-cost. STANDALONE retains an auditable export and reconciliation reference; installing an adapter does not resend already acknowledged manual exports automatically.

### First-day operations and optional workflows — resolved

Use [INSTALL.md](../INSTALL.md) as the acceptance walkthrough for P0-16. Company-dependent period and virtual-location provisioning runs after company/site creation, is idempotent and is not an unconditional migration against a guessed company. Create current and next non-overlapping company stock periods before admitting movements. Register the site and its eleven virtual location codes, including VALUE_OFFSET; transit follows the existing per-transfer source-site child-location contract. No setting bypasses cross-registration transfer permissions.

Tax mode NONE is not a zero-tax shortcut: document finalization requiring tax evidence is refused. MANUAL_EVIDENCE records issuer, external document reference/date/currency, line/tax totals and attachment; duplicate references are checked in issuer scope. PROVIDER records response/version and totals, retains rejection state and retries with the same identity. These modes do not invent current statutory rules; optional jurisdiction profiles carry their validated rules. Counter-sale screens show captured/provider totals and never a hidden warehouse tax calculator. The six formerly conditional engine tables remain reserved in documentation; do not allocate or build a second engine from historical prose.

A business chooses a tested regulated profile, not a generic 'compliant' switch. Activation requires the existing regulated task's licence, lot/expiry, recall/hold, access and evidence scenarios. No profile means the regulated workflow is unavailable. Operational recovery of already created records remains accessible when a profile is disabled. Administrative locks, erasure restrictions, retention and separation of duties stay enforced.

## Acceptance cases and ownership

These cases supplement the existing numbered scenarios; they do not replace their ownership.

| Case | Given / action | Required result | Existing task owners |
|---|---|---|---|
| CONFIG-CASE-01 | New standalone install, no optional provider; rerun setup | Declared defaults, one settings row per key, one period/site seed set; stock-only receipt works without accounting | P0-15, P0-16, P1-20 |
| CONFIG-CASE-02 | Two admins save same revision; API sends invalid enum or out-of-range value | One atomic save; stale save conflicts; invalid save makes no partial change; audit excludes secrets | P0-15, P1-20 |
| CONFIG-CASE-03 | Site override is 0/false; other site has no override | Explicit value wins; other site inherits; scoped user cannot preview inaccessible records | P1-03, P1-18, P1-20 |
| CONFIG-CASE-04 | Change TTL/method after reservation/movement exists | Existing expiry and historical cost unchanged; new work takes new revision; reservation expiry releases once | P0-09, P2-16 |
| CONFIG-CASE-05 | Q=2,R=0, issue 3 under BLOCK/WARN/ALLOW; try new reservation after allowed issue | BLOCK refuses; WARN requires authorized acknowledgement; ALLOW logs; signed on-hand −1, ATP 0; new reservation refused. Another holder's reserved quantity and duplicate serial always protected | P0-03, P1-03, P0-09 |
| CONFIG-CASE-06 | Post foreign price 42 at rate 88.415; omit rate; resend same accepted key | Base unit 3713.430000 and original evidence frozen; missing foreign rate refuses atomically; same payload replays, changed payload conflicts | P0-08, P0-17, P2-16 |
| CONFIG-CASE-07 | Enable accounting/tax/GS1 profile without required capability; disable with work pending | Activation refused with missing-capability list; no hidden fallback; pending work retained for authorized recovery | P1-20, P2-18, P2-14, P4-01 |
| CONFIG-CASE-08 | v1 LPN label then scan; later enable GS1 and reprint older job | Internal code resolves in v1; GS1 refused until ready; reprint preserves original identifier and template; both issued formats remain resolvable | P2-14, P1-04, P3-24 |
| CONFIG-CASE-09 | Manual tax mode without evidence; provider rejects; duplicate successful response | Finalization blocks; pending/rejected state remains; duplicate does not create a second document or movement | P2-25, P4-01 |
| CONFIG-CASE-10 | Value-only movement missing counterpart; zero-bailment; retry export acknowledgement | Unbalanced movement refuses; bailment has no valued envelope; duplicate acknowledgement does not resend/re-cost | P0-02, P2-17, P2-18, P2-28 |
| CONFIG-CASE-11 | Register new branch with stock/open work; self-approve; then settle dependencies | Refuse with dependency links; self-approval refused; eligible change appends effective history, never rewrites past postings | P1-05, P1-18 |
| CONFIG-CASE-12 | v1 drop-ship request; enabled v2 supplier confirmation repeated/reversed | v1 refuses; v2 links PO/demand, physical balance unchanged; repeat idempotent; reversal linked and auditable | P5-09 |
| CONFIG-CASE-13 | Export/import settings into another customer's database | No credentials or source database identifiers reused; preview/remap validates; invalid batch writes nothing | P3-18 |
| CONFIG-CASE-14 | Set over-receipt 0, expire alert threshold, lower retries with failed work | Zero is respected; threshold alerts do not approve/discard work; retained failed records are recoverable under the same key | P1-12, P0-11, P2-23 |

## Readiness boundary

The decisions above are answered. Capability tests, provider credentials, company base currency/time zone and customer master data are installation inputs; they are not unresolved design questions. External modules are not asserted to implement a contract merely because this repository specifies it. Implementers must prove these acceptance cases and the existing design-set checks before calling a workflow implemented. Future requirements changes remain versioned changes, not permission to silently choose a different behaviour.

## Implementation scope — final clarification

Reuse existing platform settings validation, version checks, cache invalidation and audit storage. A policy version/snapshot is needed only on the work whose behavior must remain reproducible; this does not require a second event store or configuration framework. Implement each shared concern once in P0-15/P1-20, and let consumers use that contract. A CONFIG-CASE shared by several owners is split by their existing responsibility: a provider consumer proves its refusal/recovery path, not every unrelated provider UI. A capability reserved for a later version remains unavailable in the current version; its switch is not an instruction to build it early.
