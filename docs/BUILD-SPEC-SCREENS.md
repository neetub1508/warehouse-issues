# Build spec — screens

> **Current adopted amendment (2026-09-11):** [Global settings and resolved behaviour](GLOBAL-SETTINGS-DECISIONS.md) supplies defaults, scoped choices, resolved OD answers and acceptance cases. Earlier open/escalated or contradictory wording is historical where explicitly superseded there. Implement these answers; do not re-ask the same design questions.


> **What this document is.** The per-screen block an engineer or a `/create-page` agent builds from
> without going back to first principles. For every grid and every screen in the Warehouse product it
> names the canonical reference page to diff against, the `gridIdentifier`, the
> `COMMON_FILTER_CONFIGS` scope, the cache names, the permission resource, the columns with their
> source `table.column`, the filters with their type and dropdown source, the export set, the modals,
> the row and toolbar actions with their gates, the mobile counterpart, and the version and phase.
>
> **Authority.** [`DECISIONS.md`](DECISIONS.md) wins over this document on modules, prefixes, bands,
> the version ladder and `D-13`/`OD-5`. [`DATA-MODEL.md`](DATA-MODEL.md) wins on any table or column
> name. [`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md`](WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md) wins on what a
> screen must do. [`MODULE-INTEGRATION.md`](MODULE-INTEGRATION.md) wins on the shared-registry edits.
> Where this document says something none of them says, it is this document's own ruling and it is
> marked as such.
>
> **House standards.** `/Users/bbhushan/work/git/workspace/classic/CLAUDE.md` governs every line
> built from this spec. The three canonical reference pages it names are the only three shapes used
> here — there is no fourth.

---

## 0. Conventions — read once, apply to every block

### 0.1 The three references, and how to pick

| Reference | Real path in `classic` | Use it when |
|---|---|---|
| **Department** | `platform/frontend/src/app/dashboard/admin/departments/page.tsx` + `DepartmentFilter.tsx`, `DepartmentModal.tsx`, `DepartmentViewModal.tsx`; backend `platform/backend/.../department/{DepartmentController,DepartmentService,DepartmentQueryService,DepartmentRepositoryCustomImpl}.java` | The entity is a master or a catalogue: create/edit in a modal, no lifecycle, no cross-entity cascade. Every one of the fourteen catalogues is this shape |
| **Customer** | `dealer/frontend/src/app/dealers/customers/page.tsx` | The entity has relations and the filter strip cascades (filter A resets filter B), and mutations need `useQueryInvalidation` from `@platform/hooks/useDataQuery` (`useDataQuery.ts:245`) |
| **Service Vehicle** | `services/frontend/src/app/dashboard/services/vehicles/page.tsx` | The entity has a **state ladder**, transitions happen through **their own modals**, and/or the entity supports **bulk import** via `ImportButton` (`page.tsx:18`, `:909`) |

Both the Department and Service Vehicle pages hydrate their grid through
`usePersistedFilters({ gridIdentifier, initialFilters, filterScope, columnTranslations, urlParamMapper, onAfterApply, onAfterClear })`
(`departments/page.tsx:163-179`, `vehicles/page.tsx:203-205`) and fetch through
`useDataListQuery({ …, isGridPrefsInitialized: preferencesHydrated })`
(`departments/page.tsx:238-251`). **Copy that, not an older page.** Every block below assumes it.

**Divergence from the chosen reference is a violation** (CLAUDE.md, "Pick the closest shape … then
diff your output against it").

### 0.2 Identifiers

| Thing | Rule | Example |
|---|---|---|
| `gridIdentifier` | **the table name**, verbatim | `whb_items`, `wh_goods_receipts` |
| Filter scope | `WAREHOUSE_` + SCREAMING_SNAKE singular of the grid | `WAREHOUSE_ITEM`, `WAREHOUSE_GOODS_RECEIPT` |
| Permission resource | the table name | `whb_items:view` |
| Route | `/warehouse/<module segment>/<screen>` | `/warehouse/masters/items` |
| i18n key root | the camelCase entity inside the module namespace | `warehouseBase:items.table.headers.sku` |

**The filter-scope prefix is `WAREHOUSE_`, not `WHB_`/`WH_`, and that is a deliberate divergence from
the accounting set's `ACC_*` convention.** [`MODULE-INTEGRATION.md`](MODULE-INTEGRATION.md) §12.1 fixes
it (*"named for the grid identifier: `WAREHOUSE_STOCK_MOVEMENT`, `WAREHOUSE_STOCK_POSITION`,
`WAREHOUSE_ITEM`, …"*). Verified free — no scope beginning `WAREHOUSE` exists today:

```bash
# from the classic repo root
awk '/COMMON_FILTER_CONFIGS/,0' platform/frontend/src/utils/filterUtils.ts \
  | grep -oE "^  [A-Z0-9_]+: \{" | sed 's/[ :{]//g' | grep -c '^WAREHOUSE'    # → 0
```

Beware the near-misses that **do** exist and must not be reused: `ACCESSORY_WAREHOUSE`,
`ACCESSORY_STOCK_LEVEL`, `ACCESSORY_STOCK_ADJUSTMENT`, `ACCESSORY_STOCK_TRANSFER`,
`ACCESSORY_STOCK_RECEIPT`, `ACCESSORY_STOCK_SUMMARY`, `ACCESSORY_INVENTORY_COUNT`,
`ACCESSORY_INVENTORY_VALUATION`, `ACCESSORY_STOCK_MOVEMENT_REPORT`, `ACCESSORY_INSUFFICIENT_STOCK`,
`ACCESSORY_WAREHOUSE_UTILIZATION`, `LOW_STOCK_REPORT`, `STOCK_PERFORMANCE`, `PDI_STOCK_YARD`. Those
are `accessories` and dealer grids and they stay separate forever (`D-9`).

### 0.3 Cache names — and the one that must **not** be registered

CLAUDE.md's convention is `statistics.{entityCamelCase}` / `dropdown.{entityCamelCase}`, registered in
`platform/backend/src/main/java/ai/platform/config/CacheConfiguration.java` inside the
`setCacheNames(Arrays.asList(…))` block that begins at `:101`. An unregistered name throws
`IllegalArgumentException` on the **first call**, not at startup — the warning is in the file at
`:375-377`.

**But every warehouse statistics strip is filter-aware, so it gets no cache name.** `FR-395` and
[`MODULE-INTEGRATION.md`](MODULE-INTEGRATION.md) §12.2 rule on it, citing the platform's own recorded
mistake (`CacheConfiguration.java:190-196`, issues `neetub1508/classic#790`, `#791`): statistics
computed from the same search + filters as the rows *"are uncacheable under any key short of the full
filter set"*, and registering a name for them caches nothing while reading as though it did.

> **The rule for every block in this document:** the cache column carries `dropdown.<entityCamelCase>`
> where the screen exposes a `/dropdown` endpoint, and `— (filter-aware, FR-395)` for statistics.
> A `statistics.*` name appears **only** where the number is provably independent of the filter
> strip; no v1 warehouse screen qualifies.

Counts, computed 2026-09-01 from the `classic` checkout:

```bash
awk '/COMMON_FILTER_CONFIGS/,0' platform/frontend/src/utils/filterUtils.ts \
  | grep -cE "^  [A-Z0-9_]+: \{"                                                      # → 213 scopes
awk 'NR>101 && /^\s*\)\);/{exit} NR>101' \
  platform/backend/src/main/java/ai/platform/config/CacheConfiguration.java \
  | grep -cE '^[[:space:]]*"[a-zA-Z0-9._-]+",?$'                                      # → 234 cache names
```

(`MODULE-INTEGRATION.md` §12 recorded 211 and 230 the same day with a fixed `NR>=101 && NR<=415`
window; the tree moved and the window no longer ends at the closing paren. The boundary-aware command
above is the one to use.)

### 0.4 Filter types — eight, and no `daterange`

`platform/frontend/src/utils/filterUtils.ts:30`:

```ts
export type FilterFieldType = 'text' | 'select' | 'enum' | 'multiselect' | 'boolean' | 'date' | 'dateOnly' | 'number';
```

Two consequences that cost rebuild cycles if missed:

1. **There is no range type.** Every *from → to* and every *as-at* filter in this document is **two
   keys** (`…From` / `…To`), and **both** go in the scope allowlist.
2. **`dateOnly` is load-bearing for warehouse.** `filterUtils.ts:49-56` documents that `date` shifts
   to UTC day boundaries for `TIMESTAMP` columns, *"which moves the 'from' bound to the previous
   calendar day for users east of UTC"*. `FR-327` makes every statutory, expiry, manufacture and count
   date a SQL `DATE`. **Those filters are `dateOnly`.** `occurred_at`, `recorded_at`, `created_at` and
   every other `TIMESTAMPTZ` filter is `date`.

The DB side is a **different** registry: `filter_definitions.filter_type` (V229:13, default `'text'`)
is the render hint and takes `text | select | date | number | boolean | multiselect`. The two must
agree; a `dateOnly` scope entry pairs with a `date` row in `filter_definitions`.

### 0.5 Three-way filter parity, and grid↔export parity

A filter is live only if it exists in **all three** places. Missing from any one and the UI renders,
accepts input and does nothing:

1. `filter_definitions` (the row that renders it) — **the table is `filter_definitions`, created by
   `platform/…/V229__Add_filter_definitions_table.sql:8`. There is no `grid_filter_definitions`
   table**; inserting into that name fails at Flyway and crash-loops the backend
   (`grep -rln "CREATE TABLE.*grid_filter_definitions" --include=*.sql . | wc -l` → **0**).
2. `COMMON_FILTER_CONFIGS.{SCOPE}` in `filterUtils.ts` (silent drop by `convertFiltersForApi()`).
3. The API service's `getForManagement` parameter list (an enumerating service drops unknown keys).

**Export is a superset of the visible grid columns** (`FR-400`, CLAUDE.md Table Rules). Where the grid
shows `createdByName` / `updatedByName`, the backend `ExportService` must emit them too.
**The rule is grid↔export parity, not a fixed column list.** The ledger- and log-style warehouse grids
below deliberately show no created-by/updated-by column, because they are append-only and their actor
is a first-class business column (`whb_stock_movements.actor_user_id`, `FR-024`), not an audit
afterthought. Those grids must **not** gain export-only audit columns. They are named once, here:

`whb_stock_movements` · `whb_stock_movement_lines` · `whb_stock_positions` ·
`whb_stock_position_snapshots` · `whb_position_drift_findings` · `whb_number_series_issued` ·
`whb_audit_events` · `whb_job_runs` · `whb_outbox` · `whb_outbox_deliveries` ·
`whb_inbound_messages` · `whb_movement_batch_results` · `wh_insufficient_stock_log` ·
`wh_blocked_movements` · `wh_reconciliation_exceptions` · `wh_shipment_tracking_events` ·
`wh_demand_history` · `wh_labour_tasks` · `wh_kpi_snapshots` · `wh3_billable_events` ·
`wh3_storage_billing_lines` · `whin_compliance_api_logs` · `whin_stock_account_lines` ·
plus every report grid in §7.

### 0.6 Modals

| Kind | Shape |
|---|---|
| Add / Edit | `Modal` with `size="lg"`, `minWidth={500}`, `resizable={true}`, default export, mounted only when `isOpen` |
| View | `ViewModalBase` (`platform/frontend/src/components/common/ViewModalBase.tsx:31`) with `InfoSection`, `InfoRow`, `InfoGrid`, `StatusCard`, `DataTable`, `AlertBox` |
| Multi-tab | **> 6 logical field groups** → `TabNavigation` + `useModalTabState`. Department Modal (4 tabs) is the reference |
| Loading | every modal through `lazyModal()` + `Suspense` — never `React.lazy()`, never a direct import |

Where a document has a lifecycle, the **transition is its own modal**, not a field on the edit form —
Service Vehicle's `TemporaryInModal` / `TemporaryOutModal` / `CheckOutModal` (`vehicles/page.tsx:48-51`)
is the pattern. `FR-005` forbids an "Edit" affordance on anything posted to the ledger, anywhere in
the product; a posted document's only write actions are **Reverse** and **Cancel**.

### 0.7 The mobile counterpart — stated for every screen, always

`D-13` and `FR-218`: **silence is a defect.** Every block below carries a `Mobile` row. It says one of:

- a mobile screen path under `mobile/src/screens/<camelCaseEntity>/`, and what it can and cannot do; or
- `none — <reason>`, which is a decision, not an omission.

The constraints, verified in the tree:

- `mobile/src/components/common/ListHeader.tsx` — `AdditionalFilterConfig.type?: 'dropdown' | 'text'`.
  **Date filters are not supported.** Any web screen whose default filter strip is date-driven ships
  the mobile equivalent as a dropdown of named periods, and the block says so.
- API services are **object literals**, not `BaseApiService` subclasses. Do not refactor.
- `EntityListScreen` is the wrong base for one-handed, gloved RF work (`FR-220`); the nine RF screens
  of `FR-217` are a **separate screen family** (§6.9), not `EntityListScreen` instances.
- `mobile/src/schemas/common.schemas.ts` is a **third copy** of every dropdown vocabulary. `FR-382`
  and `OD-5`: a catalogue-backed vocabulary must be fetched there too, never re-enumerated as a zod
  enum — a value the backend opened and the mobile schema closed fails the save with no message.

### 0.8 Route ownership — one segment per module, because the frontends merge

`shared/docker/Dockerfile.frontend` merges every module's `frontend/src/` into one tree with
`cp -r`, **last-write-wins**; 39 relative paths already collide across shipped modules
(`MODULE-INTEGRATION.md` §6.2, computed 2026-09-01). Two warehouse modules writing the same route
directory silently produce one page. The allocation below is exclusive and is not negotiable:

| Module | Owns exactly these route roots |
|---|---|
| `warehouse-base` | `/warehouse/masters/*` · `/warehouse/ledger/*` · `/warehouse/catalogues/*` · `/warehouse/platform/*` |
| `warehouse` | `/warehouse/inbound/*` · `/warehouse/inventory/*` · `/warehouse/outbound/*` · `/warehouse/execution/*` · `/warehouse/printing/*` · `/warehouse/golive/*` · `/warehouse/reports/*` |
| `warehouse-3pl` | `/warehouse/3pl/*` |
| `warehouse-india` | `/warehouse/india/*` |
| `warehouse-adapter-dealer` | `/warehouse/dealer/*` |
| `warehouse-adapter-services` | `/warehouse/services/*` |
| `warehouse-adapter-field-service` | `/warehouse/field-service/*` |
| `warehouse-adapter-assets` | `/warehouse/assets/*` |

Components, API services, types and constants are prefixed per `MODULE-INTEGRATION.md` §6.2:
`components/whbItem/WhbItemManagementTable.tsx`, `services/api/whbItemApi.ts`, `types/whbItem.ts`,
`constants/warehouseBasePermissions.ts`, `constants/warehouseBaseGrids.ts`.

### 0.9 Migration bands for grid configuration

Never invent a number outside the module's band (`D-2`). The grid-config allocations are already made
in [`DATA-MODEL.md`](DATA-MODEL.md) §7 and every block below points at one of them:

| Module | Table DDL | Permissions | `permission_dependencies` | Menus | **Grid config — one migration per grid** |
|---|---|---|---|---|---|
| `warehouse-base` | `V500001`–`V500063` | `V501000` | `V501001` | `V501010` | **`V501020`–`V501099`** (WHB-74) |
| `warehouse` | `V510010`–`V510199` | `V511000` | `V511001` | `V511010` | **`V511020`–`V511199`** (WH-203) |
| `warehouse-3pl` | `V530xxx` | `V531000`–`V531199` | same file range | same | **`V531000`–`V531199`** (W3-20) |
| `warehouse-india` | `V540xxx` | `V541000`–`V541199` | same file range | same | **`V541000`–`V541199`** (WIN-30) |
| adapter · dealer | `V520000`–`V520999` | in-band | in-band | in-band | in-band |
| adapter · services | `V521000`–`V521999` | in-band | in-band | in-band | in-band |
| adapter · field-service | `V522000`–`V522999` | in-band | in-band | in-band | in-band |
| adapter · assets | `V523000`–`V523999` | in-band | in-band | in-band | in-band |
| adapter · example | `V525000`–`V525999` | — | — | — | none (no screens) |
| **reserved** | `V524000`–`V524999` | — | — | — | **`logistics`, v3. Write nothing in v1** |

`V500200` (WHB-70) is the platform `CHECK` widening — see §8.

### 0.10 Screen-id namespace

This document registers **`WS-nnn`**. `DECISIONS.md` §6 owns the id namespaces; `WS-` collides with
none of them (`P0-01`… tasks, `FR-`, `D-`, `OD-`, `L-`, `I-`, `WH-SC-`, `C-`/`T-`/`E-`/`F-`/`S-`/`P-`/`G-`
findings). Verified: `grep -rn "WS-[0-9]" docs/` outside this file → **0 hits**, 2026-09-01.

### 0.11 State ladders — added in round 2 (`H-004`)

**Before round 2 this design set contained not one from→to transition table.** 96 `DATA-MODEL.md`
rows name a `status` or `state` column, 20 enumerate a vocabulary inline, and **none** stated which
transition was legal from which state, who could perform it, what guard it had to pass, or which
states were terminal. `WS-045`'s parenthesised *"a status ladder OPEN → SOFT_CLOSED → CLOSED"* was the
single ladder drawn in sixteen documents.

```bash
grep -E '^\| `(whb|wh|wh3|whad|whas|whaf|whaa|whae|whin)_[a-z0-9_]+`' docs/DATA-MODEL.md \
  | grep -cE '`[a-z_]*status[a-z_]*`|`[a-z_]*state`'        # status-bearing tables → 96
grep -E '^\| `(whb|wh|wh3|whad|whas|whaf|whaa|whae|whin)_[a-z0-9_]+`' docs/DATA-MODEL.md \
  | grep -cE '`[a-z_]*status[a-z_]*` \(`[A-Z]'             # ... with a vocabulary → 20
```

**Why a document and not a `CHECK`.** `D-10` declines `CHECK (… IN (…))` on the open catalogues, so
the database will not constrain the ladder either. The service is the only enforcement point, and a
service can only enforce a ladder somebody wrote down. **A status value written by a build that
guessed the ladder is in the customer's table forever**, and the `IRR-41`-shaped append-only tables
cannot be corrected by `UPDATE`.

**The columns.** `Table | From | To | Verb | Actor (permission) | Guard | Terminal?` — the `Verb` is a
§10.2 row and the `Actor` is its permission string. **§10.2 and this section are the same list read
from two sides**, which is why round 2 authored them together: a verb with no ladder row has no
guard, and a ladder row with no verb is a transition anybody with `:edit` can perform.

**The completion rule** (also in `00-EPIC-master.md`'s Definition of done): *a task creating a
`status` column ships its ladder rows in the same PR. A state with no inbound transition and a
non-terminal state with no outbound transition are both defects.* The blocks below seed the ladders
whose absence was already producing divergent answers; the remaining status-bearing tables owe theirs
to their own task, and the list is at the end of this section.

#### `whb_stock_periods` — the model, and the only ladder that existed before round 2

| Table | From | To | Verb | Actor (permission) | Guard | Terminal? |
|---|---|---|---|---|---|---|
| `whb_stock_periods` | — | `OPEN` | period generation | `whb_stock_periods:create` | the previous period exists | no |
| `whb_stock_periods` | `OPEN` | `SOFT_CLOSED` | Soft close | `whb_stock_periods:close` | none — soft close is reversible by design | no |
| `whb_stock_periods` | `SOFT_CLOSED` | `OPEN` | Reopen | `whb_stock_periods:reopen` | reason code recorded | no |
| `whb_stock_periods` | `SOFT_CLOSED` | `CLOSED` | Close | `whb_stock_periods:close` | no unposted movement, no open handover (a `VOIDED` handover is not open, `RJ-011`), `L-4` drift check clean | **yes** |
| `whb_stock_periods` | `SOFT_CLOSED` | `SOFT_CLOSED` | Override (post into a soft-closed period) | `whb_stock_periods:override` | approved and recorded per `L-8`; the session GUC is set by the service, never by a support script | no |

**`CLOSED` is terminal, including for a reversal** (`L-8`). A correction to a closed period is a
movement in the *current* period carrying the original's link — not a reopen.

#### `wh_purchase_orders` — the one v1 app table that already carried a full vocabulary

| Table | From | To | Verb | Actor (permission) | Guard | Terminal? |
|---|---|---|---|---|---|---|
| `wh_purchase_orders` | — | `DRAFT` | Create | `wh_purchase_orders:create` | — | no |
| `wh_purchase_orders` | `DRAFT` | `SUBMITTED` | Submit | `wh_purchase_orders:edit` | at least one line, counterparty active | no |
| `wh_purchase_orders` | `SUBMITTED` | `APPROVED` | Approve | `wh_purchase_orders:approve` | **approver ≠ submitter** above the value threshold (`FR-408`) | no |
| `wh_purchase_orders` | `SUBMITTED` | `DRAFT` | Return for correction | `wh_purchase_orders:approve` | reason recorded | no |
| `wh_purchase_orders` | `APPROVED` | `PARTIALLY_RECEIVED` | *(effect of a GRN post)* | `wh_goods_receipts:post` | **never set directly** — this row is a derived transition, and the guard is that no screen offers it | no |
| `wh_purchase_orders` | `PARTIALLY_RECEIVED` | `RECEIVED` | *(effect of a GRN post)* | `wh_goods_receipts:post` | ordered − received ≤ the over-receipt tolerance | no |
| `wh_purchase_orders` | `APPROVED` · `PARTIALLY_RECEIVED` · `RECEIVED` | `CLOSED` | Close | `wh_purchase_orders:edit` | short-close reason required where received < ordered | **yes** |
| `wh_purchase_orders` | `DRAFT` · `SUBMITTED` · `APPROVED` | `CANCELLED` | Cancel | `wh_purchase_orders:cancel` | **no receipt exists against any line** — this is the cancel cascade §10.2 names | **yes** |

**`PARTIALLY_RECEIVED` and `RECEIVED` have no verb of their own.** They are consequences of
`wh_goods_receipts:post`, and a screen that lets a user set them directly is the defect — the PO
status would then disagree with the ledger, which is the only thing that actually knows what arrived.

#### `whb_accounting_handovers` and `wh3_ar_handovers` — the same ladder, twice

| Table | From | To | Verb | Actor (permission) | Guard | Terminal? |
|---|---|---|---|---|---|---|
| `whb_accounting_handovers` | — | `PENDING` | *(emitted by the posting service)* | — | idempotency key present and never server-generated (`L-9`) | no |
| `whb_accounting_handovers` | `PENDING` | `SENT` | *(transmit)* | — | — | no |
| `whb_accounting_handovers` | `SENT` | `POSTED` | *(acknowledgement)* | — | external document ref recorded | **yes** |
| `whb_accounting_handovers` | `SENT` | `REJECTED` | *(negative acknowledgement)* | — | rejection code and message recorded | no |
| `whb_accounting_handovers` | `REJECTED` | `PENDING` | Retry | `whb_accounting_handovers:retry` | the **same** idempotency key is reused — a retry that mints a new key double-posts | no |
| `whb_accounting_handovers` | `REJECTED` | `VOIDED` | Void | `whb_accounting_handovers:void` | **added in round 4 (`RJ-011`)** — **approver ≠ requester** (`FR-408`); only when the movement is reversed or reclassified `NOT_APPLICABLE`; reversing a movement whose envelope never posted voids **both** envelopes. `VOIDED` is outside the period-close guard | **yes** |
| `wh3_ar_handovers` | *(identical ladder, including `REJECTED → VOIDED`)* | | Retry · Void | `wh3_ar_handovers:retry` · the void verb `P5-05` seeds | Retry **added in round 2** — §10.2 carried the base string and not this one, which is how the asymmetry was found (`H-001`). `VOIDED` added in round 4 (`RJ-011`) | |

#### `wh3_billing_runs` — and the `INVOICED → CANCELLED` question, now answered

| Table | From | To | Verb | Actor (permission) | Guard | Terminal? |
|---|---|---|---|---|---|---|
| `wh3_billing_runs` | — | `DRAFT` | Create | `wh3_billing_runs:create` | client active, period not already run for this `run_type` | no |
| `wh3_billing_runs` | `DRAFT` | `RATED` | Rate | `wh3_billing_runs:rate` | exactly one `ACTIVE` rate card resolves for the whole period | no |
| `wh3_billing_runs` | `RATED` | `DRAFT` | Re-rate *(withdraw)* | `wh3_billing_runs:rate` | reason recorded; billable events are **re-read**, never edited | no |
| `wh3_billing_runs` | `RATED` | `APPROVED` | Approve | `wh3_billing_runs:approve` | **approver ≠ the user who rated** above the threshold (`FR-408`); the state freezes here | no |
| `wh3_billing_runs` | `APPROVED` | `INVOICED` | Emit AR handover | `wh3_billing_runs:emit_ar_handover` | a `wh3_ar_handovers` row reaches `POSTED` | **yes** |
| `wh3_billing_runs` | `DRAFT` · `RATED` | `CANCELLED` | Cancel | `wh3_billing_runs:cancel` | — | **yes** |
| `wh3_billing_runs` | `APPROVED` | `CANCELLED` | Cancel | `wh3_billing_runs:cancel` | **only while no AR handover has left `PENDING`, or once it is `VOIDED`** (`RJ-011` — otherwise an approved run whose AR handover is `REJECTED` can neither invoice nor cancel) | **yes** |
| `wh3_billing_runs` | `INVOICED` | *(nothing)* | — | — | — | **terminal** |

> **`INVOICED → CANCELLED` is illegal.** This is the question `H-004` found two P5 tasks about to
> answer differently, and the answer follows from the document's own words: `WS-162` says Approve
> *"freezes the state"* and `WS-164` says an upheld dispute *"becomes a credit charge code — **never a
> silent edit of the run**"*. Once accounting holds the invoice, the recovery path is a **credit**
> through `wh3_disputes` or a credit charge code on the next run. A cancelled invoice the customer has
> already received, which accounting has already posted, is the failure this row prevents.

#### `wh3_disputes` — the credit-self-grant

| Table | From | To | Verb | Actor (permission) | Guard | Terminal? |
|---|---|---|---|---|---|---|
| `wh3_disputes` | — | `RAISED` | Raise | `wh3_disputes:raise` | billing run is `INVOICED` or `APPROVED`; within the contract's dispute window | no |
| `wh3_disputes` | `RAISED` | `INVESTIGATING` | Investigate | `wh3_disputes:investigate` | assigned to a named user | no |
| `wh3_disputes` | `INVESTIGATING` | `UPHELD` | Uphold | `wh3_disputes:uphold` | **the upholder is not the raiser**, and a `credit_charge_code` is set | **yes** |
| `wh3_disputes` | `INVESTIGATING` | `REJECTED` | Reject | `wh3_disputes:reject` | resolution text recorded and visible on the portal | **yes** |
| `wh3_disputes` | `RAISED` | `WITHDRAWN` | *(client withdraws from the portal)* | `wh3_disputes:raise` (portal-bound) | raiser only | **yes** |

> **`:raise` and `:uphold` must not sit in one role bundle.** `P5-01` seeds them into different
> bundles, and the reason is in the table: an upheld dispute writes a credit. Before round 2
> `wh3_disputes:uphold` had no string at all, so the person who raised a credit could grant it.

#### `wh3_rate_cards`, `wh3_clients`, `wh3_accessorials`, `wh3_client_onboarding_tasks`

| Table | From | To | Verb | Actor (permission) | Guard | Terminal? |
|---|---|---|---|---|---|---|
| `wh3_rate_cards` | — | `DRAFT` | Create · Clone as new version | `wh3_rate_cards:create` · `:clone_version` | version = max + 1 for the `card_code` | no |
| `wh3_rate_cards` | `DRAFT` | `ACTIVE` | Activate | `wh3_rate_cards:activate` | **no overlapping `ACTIVE` card for the client** — service overlap guard plus the partial unique index | no |
| `wh3_rate_cards` | `ACTIVE` | `SUPERSEDED` | *(effect of activating a later version)* | `wh3_rate_cards:activate` | the successor's `effective_from` sets this card's `effective_to` | **yes** |
| `wh3_rate_cards` | `ACTIVE` | `SUPERSEDED` | Expire | `wh3_rate_cards:expire` | **no `DRAFT`/`RATED` billing run reads it** | **yes** |
| `wh3_clients` | — | `ONBOARDING` | Create | `wh3_clients:create` | one client per `owner_id` | no |
| `wh3_clients` | `ONBOARDING` | `ACTIVE` | Onboard | `wh3_clients:onboard` | every **mandatory** onboarding task is `COMPLETED` | no |
| `wh3_clients` | `ACTIVE` | `SUSPENDED` | Suspend | `wh3_clients:suspend` | reason recorded. **Billable-event capture stops; stock does not move** | no |
| `wh3_clients` | `SUSPENDED` | `ACTIVE` | Reinstate | `wh3_clients:onboard` | — | no |
| `wh3_clients` | `ACTIVE` · `SUSPENDED` | `TERMINATED` | Terminate | `wh3_clients:terminate` | **zero on-hand for the owner, and no billing run below `INVOICED`** — otherwise the stock has no owner and the money has no client | **yes** |
| `wh3_accessorials` | — | `RAISED` | Raise | `wh3_accessorials:raise` | charge code active for the client | no |
| `wh3_accessorials` | `RAISED` | `APPROVED` | Approve | `wh3_accessorials:approve` | approver ≠ raiser above the threshold | no |
| `wh3_accessorials` | `RAISED` | `REJECTED` | Reject | `wh3_accessorials:reject` | reason recorded | **yes** |
| `wh3_accessorials` | `APPROVED` | `BILLED` | *(effect of a run reaching `RATED`)* | `wh3_billing_runs:rate` | never set directly | **yes** |
| `wh3_client_onboarding_tasks` | — | `PENDING` | *(instantiated from the template)* | — | — | no |
| `wh3_client_onboarding_tasks` | `PENDING` | `ASSIGNED` | Assign | `wh3_client_onboarding_tasks:assign` | assignee active | no |
| `wh3_client_onboarding_tasks` | `ASSIGNED` | `COMPLETED` | Complete | `wh3_client_onboarding_tasks:complete` | evidence note required where the template says so | no |
| `wh3_client_onboarding_tasks` | `COMPLETED` | `ASSIGNED` | Reopen | `wh3_client_onboarding_tasks:reopen` | **refused once the client is `ACTIVE`** — reopening a mandatory task behind an onboarded client makes the onboarding guard a lie | no |

#### Round 4 — the v1 ladders of R24 Appendix A, adopted (`RJ-004`)

`GAP-REGISTER-R4.md` §2.3 adopts R24 Appendix A as the ladder text. Three amendments apply: `RK-001`'s
request on transfers (register §3.3), `RJ-011`'s `VOIDED` on handovers (above), and the location ladder
written out in full (`RJ-006`). Each creating task carries its rows in this format, plus the acceptance line
*"no state without an inbound transition; no non-terminal state without an outbound one"*:
`P1-12` `P1-13` `P1-16` `P1-17` `P2-01` `P2-02` `P2-04` `P2-06` `P2-08` `P2-10` `P2-12` `P2-13` `P2-15`
`P2-17` `P2-25` `P2-26`. **Ratify each block with `/functional-contract` before building from it**, as
Appendix A itself says. A guard is inferred from the cited source, and the task confirms it.

| Table | From | To | Verb | Actor (permission) | Guard | Terminal? |
|---|---|---|---|---|---|---|
| `wh_goods_receipts` | — | `DRAFT` | Create | `wh_goods_receipts:create` | — | no |
| `wh_goods_receipts` | `DRAFT` | `POSTED` | Post | `wh_goods_receipts:post` | at least one line; the UoM convertibility guard (`FR-143`) | no |
| `wh_goods_receipts` | `DRAFT` | `CANCELLED` | Cancel | `wh_goods_receipts:cancel` | nothing posted | **yes** |
| `wh_goods_receipts` | `POSTED` | `REVERSED` | *(effect of a `wh_receipt_reversals` row reaching `POSTED`)* | `wh_receipt_reversals:post` | `FR-131` — the stock has not moved on. Never set directly | **yes** |
| `wh_receipt_reversals` | — | `REQUESTED` | Request | `wh_receipt_reversals:create` | the GRN is `POSTED` | no |
| `wh_receipt_reversals` | `REQUESTED` | `APPROVED` | Approve | `wh_receipt_reversals:approve` | **approver ≠ requester** (`FR-408`) | no |
| `wh_receipt_reversals` | `REQUESTED` | `REJECTED` | Reject | `wh_receipt_reversals:approve` | reason recorded | **yes** |
| `wh_receipt_reversals` | `APPROVED` | `POSTED` | Post | `wh_receipt_reversals:post` | generates the `REVERSAL` movement | **yes** |
| `wh_stock_adjustments` | — | `DRAFT` | Create | `wh_stock_adjustments:create` | — | no |
| `wh_stock_adjustments` | `DRAFT` | `SUBMITTED` | Submit | `wh_stock_adjustments:submit` | at least one line; mandatory reason code | no |
| `wh_stock_adjustments` | `SUBMITTED` | `APPROVED` | Approve · *(auto-approve below the threshold, `RA-008`)* | `wh_stock_adjustments:approve` | **approver ≠ actor**; the threshold is by value as well as by quantity | no |
| `wh_stock_adjustments` | `SUBMITTED` | `REJECTED` | Reject | `wh_stock_adjustments:reject` | **approver ≠ actor**; reason recorded | **yes** |
| `wh_stock_adjustments` | `APPROVED` | `POSTED` | Post | `wh_stock_adjustments:post` | period `OPEN` (`L-8`) | **yes** |
| `wh_stock_adjustments` | `DRAFT` · `SUBMITTED` | `CANCELLED` | Cancel | `wh_stock_adjustments:cancel` | — | **yes** |
| `wh_transfer_orders` | — | `REQUESTED` | Request | `wh_transfer_orders:request` | **the creator is scoped to the destination site** (`FR-462`); both sites in one company, else `422 CROSS_COMPANY_TRANSFER` (`RK-007`) | no |
| `wh_transfer_orders` | — | `DRAFT` | Create | `wh_transfer_orders:create` | the same-company guard | no |
| `wh_transfer_orders` | `REQUESTED` | `APPROVED` | Approve · part-approve | `wh_transfer_orders:approve` | **the approver is scoped to the source site**, and approver ≠ requester (`FR-408`). **Part-approval is a line quantity, not a state**: `approved_quantity` below the requested quantity on an `APPROVED` header. The refused remainder writes `wh_insufficient_stock_log` with `source_type = TRANSFER_REQUEST`. Approval creates the `TRANSFER` demand order | no |
| `wh_transfer_orders` | `REQUESTED` | `REJECTED` | Reject | `wh_transfer_orders:reject` | source-scoped; reason recorded | **yes** |
| `wh_transfer_orders` | `DRAFT` | `APPROVED` | Approve | `wh_transfer_orders:approve` | **only where `requires_approval`**; `FR-408` | no |
| `wh_transfer_orders` | `DRAFT` · `APPROVED` | `ALLOCATED` | *(effect of the `TRANSFER` demand order allocating, `RJ-003`)* | `wh_demand_orders:allocate` | from `DRAFT` only where `requires_approval = false`. There is exactly one reservation path. Never set directly | no |
| `wh_transfer_orders` | `ALLOCATED` | `IN_TRANSIT` | Dispatch | `wh_shipments:dispatch` | the transfer's shipment dispatches, posting `TRANSFER_DEPART` into the per-transfer `IN_TRANSIT` location **at the source site** (`FR-189`: the relief is into transit) | no |
| `wh_transfer_orders` | `IN_TRANSIT` | `PARTIALLY_RECEIVED` | Receive | `wh_transfer_orders:receive` | authorised against **that transfer's** transit location regardless of site scope, and nothing else at the source (`P1-18`) | no |
| `wh_transfer_orders` | `IN_TRANSIT` · `PARTIALLY_RECEIVED` | `RECEIVED` | Receive | `wh_transfer_orders:receive` | received = dispatched | no |
| `wh_transfer_orders` | `PARTIALLY_RECEIVED` · `RECEIVED` | `CLOSED` | Report variance | `wh_transfer_orders:report_variance` | the transit location's balance is 0 once the residue is posted | **yes** |
| `wh_transfer_orders` | `REQUESTED` · `DRAFT` · `APPROVED` · `ALLOCATED` | `CANCELLED` | Cancel | `wh_transfer_orders:cancel` | the demand order's reservations are released | **yes** |
| `wh_transfer_orders` | `IN_TRANSIT` | `CANCELLED` | Cancel | `wh_transfer_orders:cancel` | **posts `TRANSFER_RETURN`** from the transit location back to the source, with a mandatory reason code (`RJ-006`) | **yes** |
| `wh_counts` | — | `GENERATED` | Generate | `wh_counts:generate` | programme or ad hoc; with no programme the install tolerance applies (`RJ-016`) | no |
| `wh_counts` | `GENERATED` | `FROZEN` | Freeze | `wh_counts:freeze` | the book snapshot is taken; the counted locations go to `COUNTING` | no |
| `wh_counts` | `FROZEN` | `COUNTING` | Enter counts | `wh_counts:edit` | the first line counted | no |
| `wh_counts` | `COUNTING` | `PENDING_APPROVAL` | Submit | `wh_counts:edit` | every line counted; lines inside tolerance need no approval | no |
| `wh_counts` | `PENDING_APPROVAL` | `COUNTING` | Recount | `wh_counts:recount` | **not after `APPROVED`** — §0.11's open question, answered | no |
| `wh_counts` | `PENDING_APPROVAL` | `APPROVED` | Approve | `wh_counts:approve` | **the counter may not approve their own count** (`FR-408`) | no |
| `wh_counts` | `APPROVED` | `POSTED` | Post | `wh_counts:post` | one movement per non-zero variance line; the locations return to their prior status | **yes** |
| `wh_counts` | `GENERATED` · `FROZEN` · `COUNTING` · `PENDING_APPROVAL` | `CANCELLED` | Cancel | `wh_counts:cancel` | **restores each location's prior status** — a cancelled count must not leave bins unpickable (`RJ-006`) | **yes** |
| `whb_locations.status` | — | `AVAILABLE` | Create | `whb_locations:create` | — | no |
| `whb_locations.status` | `AVAILABLE` | `BLOCKED` | Block | `whb_locations:block` | mandatory reason code | no |
| `whb_locations.status` | `AVAILABLE` | `DAMAGED` | Block (damage reason) | `whb_locations:block` | a reason code in the damage context | no |
| `whb_locations.status` | `BLOCKED` · `DAMAGED` | `AVAILABLE` | Unblock | `whb_locations:block` | reason recorded | no |
| `whb_locations.status` | `AVAILABLE` · `BLOCKED` · `DAMAGED` | `COUNTING` | *(effect of a count's Freeze)* | `wh_counts:freeze` | the prior status is stored on the count line. Never set directly | no |
| `whb_locations.status` | `COUNTING` | *(the stored prior status)* | *(effect of the count's Post or Cancel)* | `wh_counts:post` · `wh_counts:cancel` | — | no |
| `whb_locations.status` | `AVAILABLE` · `BLOCKED` · `DAMAGED` | `FROZEN` | *(the stocktake window opens, `FR-157`)* | `wh_counts:freeze` on a `FULL_PHYSICAL` count | **`FROZEN`'s only setter** — before round 4 it had none and was unreachable | no |
| `whb_locations.status` | `FROZEN` | *(the stored prior status)* | *(the stocktake window closes)* | `wh_counts:post` · `wh_counts:cancel` | — | no |
| `wh_demand_orders` | — | `OPEN` | Create | `wh_demand_orders:create` | — | no |
| `wh_demand_orders` | `OPEN` | `ALLOCATED` | Allocate | `wh_demand_orders:allocate` | — | no |
| `wh_demand_orders` | `ALLOCATED` | `RELEASED` | Release | `wh_demand_orders:release` | **zero open holds** that block pick | no |
| `wh_demand_orders` | `RELEASED` | `PICKING` | *(effect of the first pick task starting)* | the task API | never set directly | no |
| `wh_demand_orders` | `PICKING` | `PICKING` | Short pick | `wh_demand_orders:short_pick` | **stays `PICKING`, with a backorder line** and an exception code — §0.11's open question, answered | no |
| `wh_demand_orders` | `PICKING` | `PACKED` | *(effect of the last carton closing)* | `wh_cartons` close | never set directly | no |
| `wh_demand_orders` | `PACKED` | `SHIPPED` | *(effect of the shipment's dispatch)* | `wh_shipments:dispatch` | the only relief event (`FR-189`) | no |
| `wh_demand_orders` | `SHIPPED` | `DELIVERED` | Confirm delivery | `wh_shipments:confirm_delivery` | — | **yes** |
| `wh_demand_orders` | `OPEN` · `ALLOCATED` · `RELEASED` · `PICKING` · `PACKED` | `CANCELLED` | Cancel | `wh_demand_orders:cancel` | de-allocation is deterministic and reason-coded; staged stock is de-staged first (`FR-449`) | **yes** |
| `wh_shipments` | — | `OPEN` | Add | `wh_shipments:create` | — | no |
| `wh_shipments` | `OPEN` | `LOADED` | Load | `wh_shipments:edit` | every carton closed and scanned to the door | no |
| `wh_shipments` | `OPEN` · `LOADED` | `DISPATCHED` | Dispatch | `wh_shipments:dispatch` | **the inventory-relief event** | no |
| `wh_shipments` | `DISPATCHED` | `DELIVERED` | Confirm delivery | `wh_shipments:confirm_delivery` | — | **yes** |
| `wh_shipments` | `OPEN` · `LOADED` | `CANCELLED` | Cancel | `wh_shipments:cancel` | **only before `DISPATCHED`** (`RJ-006`) | **yes** |
| `wh_return_receipts` | — | `RECEIVED` | Receive | `wh_return_receipts:create` | — | no |
| `wh_return_receipts` | `RECEIVED` | `POSTED` | Post | `wh_return_receipts:post` | cost per `RJ-010`: a matched return reverses the consumption; an unmatched one takes the site's current method cost with `cost_basis = RETURN_UNMATCHED` | no |
| `wh_return_receipts` | `POSTED` | `DISPOSITIONED` | Disposition | `wh_return_receipts:disposition` | **scrap needs an approver ≠ actor** (`FR-273`, `FR-408`) | **yes** |
| `wh_return_receipts` | `POSTED` | `REVERSED` | Reverse | `wh_return_receipts:reverse` | **only before disposition**; an `L-3` mirror movement (`RJ-006`) | **yes** |
| `wh_rmas` | — | `OPEN` | Add | `wh_rmas:create` | — | no |
| `wh_rmas` | `OPEN` | `APPROVED` | Approve | `wh_rmas:approve` | — | no |
| `wh_rmas` | `APPROVED` | `MATCHED` | Match to receipt | `wh_rmas:match` | a return receipt exists | **yes** |
| `wh_rmas` | `OPEN` · `APPROVED` | `EXPIRED` | Expire · *(the `expiry_date` job, `RJ-012`)* | `wh_rmas:expire` | `expiry_date` passed | **yes** |
| `wh_rmas` | `OPEN` · `APPROVED` | `CANCELLED` | Cancel | `wh_rmas:cancel` | — | **yes** |
| `wh_replenishment_suggestions` | — | `PROPOSED` | *(written by a replenishment run)* | — | — | no |
| `wh_replenishment_suggestions` | `PROPOSED` | `ACCEPTED` | Accept | `wh_replenishment_suggestions:accept` | — | no |
| `wh_replenishment_suggestions` | `ACCEPTED` | `CONVERTED` | *(effect of creating the PO or transfer)* | `wh_replenishment_suggestions:accept` | `resulting_document_*` set | **yes** |
| `wh_replenishment_suggestions` | `PROPOSED` | `REJECTED` | Reject | `wh_replenishment_suggestions:reject` | reason recorded | **yes** |

**`whb_warehouse_branches` is not a status column, and it has no ladder.** Its rule is written here so it
is not mistaken for one (`D-14`, `RG-001`). A link is opened and ended (`whb_warehouses:edit`). A
**`REGISTERED` change is an end-date plus an insert at the same instant, never an update**. It is
*Change registration* on WS-016, gated on `warehouse:warehouses:change_registration` and maker–checker
(`FR-408`). The service refuses an `effective_from` in a `CLOSED` period or before the site's latest posted
`occurred_at`. It also refuses while the site holds non-zero on-hand if the old and new GSTINs differ
(`OD-19`).

#### Still owed, and by whom

The blocks above cover the tables whose ladders were already being answered two ways. The remaining
status-bearing tables owe a ladder to the task that creates the column, under the completion rule
above. The ones with a **named open question** are listed here so they are not rediscovered:

| Table | The question nobody has answered | Owed by |
|---|---|---|
| `wh_recalls` | is `CLOSED` terminal, or may a recall reopen when a second lot is implicated? | `P5`'s recall task |
| `wh_shipment_ndrs` | `WS-120` is *"a workflow with a response clock"* and the actions live in `wh_ndr_actions` — how many attempts, and what closes it? | `P5`'s NDR task |
| `wh_counts` | ~~freeze → count → recount → approve → post: is a second recount legal after approval?~~ **Answered in round 4**: no recount after `APPROVED` (the round-4 block above) | `P2-04` |
| `wh_quality_inspections` | is a disposition reversible before the putaway posts? | `P1`'s QC task |
| `wh_demand_orders` | ~~`:short_pick` is a verb with no stated destination state~~ **Answered in round 4**: the order stays `PICKING` with a backorder line (the round-4 block above) | `P2-08` |
| `wh3_sla_breaches` | `:confirm`, `:post_penalty` and `:waive` are three verbs over a table with no vocabulary at all | `P5`'s SLA task |

---

### 0.12 `Frozen when` — the per-field freeze list, added in round 2 (`Z-004`)

**Before round 2 this document said which fields were immutable exactly twice**, out of 51
Department-shape master screens:

```bash
grep -cn 'immutable' docs/BUILD-SPEC-SCREENS.md                       # → 2 (the registry `code`, and `whb_items.base_uom_code`)
awk -F'|' '/^\| WS-[0-9]+ /{if ($0 ~ /\| D \|/) c++} END{print c}' docs/BUILD-SPEC-SCREENS.md   # → 51 master screens
```

For the other 49, and for every other field of the item, nothing stated which fields stop being
editable once movements exist — so it would have been answered by whichever developer wrote each
service, differently each time.

**The rule.** Every master field table carries a **`Frozen when`** value per field, one of:

| Value | Meaning |
|---|---|
| `never` | ordinary master data; edit at any time. **This is the default and does not have to be written.** |
| `once a ledger row exists` | the field defines the grain of rows already in `whb_stock_movement_lines`; changing it makes history mean something it did not mean |
| `once stock is on hand` | the field can be changed for an item that has never been stocked, but not while a position exists |
| `once a movement in the current period exists` | the field may be changed between periods, under `L-8`'s period guard, never inside one |

The Add/Edit modal renders a frozen field **read-only with a tooltip naming the reason** — not
hidden, not silently ignored on submit. **Where the freeze is load-bearing it is a database trigger
following `I-9`'s shape** (`DATA-MODEL.md:2629`, `V500036`), not a service check: a service check is
bypassed by the importer, the port and the next module that writes the table directly.

**The minimum set — nine fields, and the two that need a trigger.**

| Field | Screen | `Frozen when` | Trigger? | Why |
|---|---|---|---|---|
| `whb_items.base_uom_code` | WS-023 | `once a ledger row exists` | **yes — `I-9`, exists** | the one instance that was already specified |
| `whb_item_uom_conversions.conversion_factor` | WS-026 | `once a ledger row exists` **for the pair used on any line** | **yes — new** | `L-7`/`IRR-34` freeze `conversion_factor_used` on the line and left the master open. A case corrected from 12 to 6 makes last year's report *internally consistent and wrong* — `IRR-34`'s own words for the undetectable failure |
| `whb_items.lot_control_mode` | WS-023 | `once stock is on hand` | **yes — new** | `NONE → REQUIRED` with units on hand strands every pre-existing position, whose `lot_id IS NULL`, as unpickable under the `L-5` grain |
| `whb_items.serial_control_mode` | WS-023 | `once stock is on hand` | **yes — new** | same, and `IRR-14` records that the rows the wrong rule rejected were never written — so retro-serialising has nothing to derive from |
| `whb_items.code` | WS-023 | `once a ledger row exists` | no — service | `uk(code)` is the stable string key every FK and every printed bin label uses (`DATA-MODEL.md:2795`) |
| the item's `STOCKING` row in `whb_item_category_assignments` — which replaces `whb_items.category_id` (`RG-005`) | WS-023 | `once a movement in the current period exists` — a new assignment may not take effect inside a period with movements for the item | no — service | `whb_valuation_policies` is keyed on the category, and every resolver reads the `STOCKING` assignment at `occurred_at`; re-categorising mid-period silently changes the item's valuation method |
| `whb_locations.code` | WS-017 | `once a movement in the current period exists` | no — service | `FR-034`'s trap is *"a scan gun syncing 400 movements after a shift must not lose 399 because one bin was renamed"* — the design assumes renames happen and must say what one does |
| `whb_locations.location_type_code`, capacity block | WS-017 | `once stock is on hand` | no — service | lowering capacity below current contents, or changing `is_stock_holding` under stock, has no defined outcome otherwise |
| `whb_valuation_policies.method` | WS-050 | `once a movement in the current period exists` | no — service | the row is effective-dated, which is the right shape, but nothing guards an `effective_from` inside a closed period — `L-8` guards movements, not policy rows — or says what happens to existing `whb_cost_layers` on `AVCO → FIFO` |

**Where the freeze is refused, the error names the field and the blocking fact** — `ITEM_HAS_LEDGER_ROWS`,
`ITEM_HAS_STOCK`, `PERIOD_HAS_MOVEMENTS` — with the count, in the shape `WH-SC-259` already uses for
`ITEM_HAS_STOCK`.

**The remaining master screens owe a `Frozen when` value to the task that creates them**, under the
same completion rule §0.11 applies to state ladders. `never` is the default and the common answer;
writing it is not required, but a field whose freeze is anything else and is not written is an
incomplete screen block.

### 0.13 The error register — codes a screen must render as a field-level or banner message

Before round 4, error codes lived only in the blocks that raise them (`REGISTRY_ROW_IN_USE`,
`ITEM_HAS_STOCK`, `OWNER_HAS_STOCK`, `CONVERSION_IN_USE`, the §0.12 freeze codes, …), and they stay
there. This register lists the codes round 4 introduces (`GAP-REGISTER-R4.md` §4.2), because each is
raised in one place and rendered on several screens. Every one travels in the house error shape
`{ "error", "details": { "errors": { field: msg } } }`. A screen that receives one renders the message
next to the field it names, or as a banner where it names none. **It never renders a generic *"save
failed"***.

| Code | HTTP | Raised by | Rendered on | Source |
|---|---|---|---|---|
| `CROSS_GSTIN_COUNTER_SALE` | 422 | the counter-sale service. A `SERVING` branch under a different GSTIN may not sell directly from the site | WS-194, WS-200 (a job issue follows the same rule), and the mobile counter screen. The message offers *Raise request* (WS-090 in `REQUESTED`) | `FR-461` · `D-14` item 3 · `RK-002` |
| `CROSS_COMPANY_TRANSFER` | 422 | the transfer service. Source and destination sites belong to different companies | WS-090. The destination picker never offers such a site, so the code is reached only by the API or an import | `RK-007` · `WH-SC-319` |
| `WAREHOUSE_BRANCH_COMPANY_MISMATCH` | 422 | the warehouse service. The `REGISTERED` branch is not in `whb_company_branches` for the site's `company_id` | WS-016 *Branches* tab and *Change registration* modal | `RH-004` |
| `AMBIGUOUS_LOCATION` | 409 | the scan resolver. A location code matches at more than one site and no session or device site disambiguates it | WS-071, every RF screen (WS-229 … WS-237), WS-017 mobile scan | `RL-004` |
| `AMBIGUOUS_IDENTIFIER` | 409 | the scan resolver. An identifier matches several items after the session-owner and counterparty context are applied. **The response lists the candidates** | WS-071, WS-024, WS-194, every RF screen | `RL-005` |
| `STAGED_STOCK` | 409 | a cancel on a document whose stock is still staged (a supplier return after `PICKED`, `RJ-006`, and a demand order under `FR-449`) | WS-084, WS-099 — the message names the staging location and the quantity to de-stage | `RJ-006` · `FR-449` |
| `UNREGISTERED_INSTANT` | 422 | the ledger. `I-22`'s trigger finds no `REGISTERED` link covering the movement's `occurred_at` at its warehouse; the service translates the SQLSTATE into this code | WS-040 *Simulate*, every posting screen, the port's per-message result (WS-053, WS-055) | `I-22` · `WH-SC-312` |
| `CLIENT_UPGRADE_REQUIRED` | 426 | **v1.1** — login and sync, when the handheld's app version is below `warehouse.mobile.min_app_version` | every mobile screen and RF screen; the handheld shows an update prompt, never a broken list | `RL-017` · `P3-04` |

---

## 1. Screen index

`Ref` = the canonical reference the screen copies: **D** Department · **C** Customer ·
**SV** Service Vehicle · **—** not a management grid (wizard, detail page, console, portal, RF screen).
`G` = has a `gridIdentifier` and therefore a `grid_column_definitions` + `filter_definitions` +
`grid_preferences` migration.

**Counts, computed from this table:**

```bash
f=docs/BUILD-SPEC-SCREENS.md
grep -cE '^\| WS-[0-9]{3} \|' $f                       # screens        → 243 (237 + WS-240, WS-241, round 4; WS-238, WS-239, WS-243, WS-244, round 3)
awk -F'|' '/^\| WS-[0-9]{3} \|/ && $7 ~ /Y/' $f | wc -l # configured grids → 220 (214 + WS-240, WS-241, WS-238, WS-239, WS-243, WS-244)
```

| id | Screen | Module | Route | Ref | G | Ver · Ph |
|---|---|---|---|---|---|---|
| WS-001 | Movement Types | base | `/warehouse/catalogues/movement-types` | D | Y | v1 · P0 |
| WS-002 | Document & Reference Types | base | `/warehouse/catalogues/document-types` | D | Y | v1 · P0 |
| WS-003 | Source Systems | base | `/warehouse/catalogues/source-systems` | D | Y | v1 · P0 |
| WS-004 | Stock Statuses | base | `/warehouse/catalogues/stock-statuses` | D | Y | v1 · P0 |
| WS-005 | Location Types | base | `/warehouse/catalogues/location-types` | D | Y | v1 · P1 |
| WS-006 | Reason Codes | base | `/warehouse/catalogues/reason-codes` | D | Y | v1 · P0 |
| WS-007 | UoM Classes | base | `/warehouse/catalogues/uom-classes` | D | Y | v1 · P1 |
| WS-008 | Task Types | base | `/warehouse/catalogues/task-types` | D | Y | v1 · P0 |
| WS-009 | Owner Types | base | `/warehouse/catalogues/owner-types` | D | Y | v1 · P0 |
| WS-010 | Item Types | base | `/warehouse/catalogues/item-types` | D | Y | v1 · P1 |
| WS-011 | Counterparty Roles | base | `/warehouse/catalogues/counterparty-roles` | D | Y | v1 · P1 |
| WS-012 | Dispositions | base | `/warehouse/catalogues/dispositions` | D | Y | v1 · P2 |
| WS-013 | Attribute Keys | base | `/warehouse/catalogues/attribute-keys` | D | Y | v1 · P1 |
| WS-014 | Condition Codes | base | `/warehouse/catalogues/condition-codes` | D | Y | v1 · P1 |
| WS-015 | Companies | base | `/warehouse/masters/companies` | D | Y | v1 · P1 |
| WS-016 | Warehouses (sites) | base | `/warehouse/masters/warehouses` | C | Y | v1 · P1 |
| WS-017 | Locations | base | `/warehouse/masters/locations` | C | Y | v1 · P1 |
| WS-018 | Location Generator | base | `/warehouse/masters/locations/generate` | — | N | v1 · P1 |
| WS-019 | Owners | base | `/warehouse/masters/owners` | D | Y | v1 · P0 |
| WS-020 | Owner Grants | base | `/warehouse/masters/owner-grants` | C | Y | v1 · P0 |
| WS-021 | Counterparties | base | `/warehouse/masters/counterparties` | C | Y | v1 · P1 |
| WS-022 | Item Categories | base | `/warehouse/masters/item-categories` | D | Y | v1 · P1 |
| WS-023 | Items | base | `/warehouse/masters/items` | C | Y | v1 · P1 |
| WS-024 | Item Identifiers & Barcodes | base | `/warehouse/masters/item-identifiers` | C | Y | v1 · P1 |
| WS-025 | Item Packaging Levels | base | `/warehouse/masters/packaging-levels` | C | Y | v1 · P1 |
| WS-026 | Item UoM Conversions | base | `/warehouse/masters/uom-conversions` | C | Y | v1 · P1 |
| WS-027 | Item × Site Settings | base | `/warehouse/masters/item-site-settings` | C | Y | v1 · P1 |
| WS-028 | Item × Location Settings | base | `/warehouse/masters/item-location-settings` | C | Y | v1.1 · P3 |
| WS-029 | Item Supplier Sources | base | `/warehouse/masters/item-supplier-sources` | C | Y | v1 · P1 |
| WS-030 | Item Supersessions | base | `/warehouse/masters/supersessions` | C | Y | v1 · P1 |
| WS-031 | Item External References | base | `/warehouse/masters/item-external-refs` | C | Y | v1 · P1 |
| WS-032 | Variant Axes & Values | base | `/warehouse/masters/variant-axes` | D | Y | v2 · P5 |
| WS-033 | Style × Variant Matrix | base | `/warehouse/masters/variant-matrix` | — | N | v2 · P5 |
| WS-034 | Units of Measure | base | `/warehouse/masters/uoms` | D | Y | v1 · P1 |
| WS-035 | Kit Definitions | base | `/warehouse/masters/kits` | C | Y | v1.1 · P3 |
| WS-036 | Lots | base | `/warehouse/masters/lots` | C | Y | v1 · P1 |
| WS-037 | Serials | base | `/warehouse/masters/serials` | C | Y | v1 · P1 |
| WS-038 | LPNs | base | `/warehouse/masters/lpns` | C | Y | v1 · P1 |
| WS-039 | Genealogy Explorer | base | `/warehouse/ledger/genealogy` | — | Y | v1 · P1 |
| WS-040 | Stock Movement Register | base | `/warehouse/ledger/movements` | SV | Y | v1 · P0 |
| WS-041 | Movement Detail | base | `/warehouse/ledger/movements/[id]` | — | N | v1 · P0 |
| WS-042 | Stock Position Enquiry | base | `/warehouse/ledger/positions` | C | Y | v1 · P0 |
| WS-043 | Position Drift Findings | base | `/warehouse/ledger/drift-findings` | C | Y | v1 · P2 |
| WS-044 | Position Snapshots | base | `/warehouse/ledger/snapshots` | C | Y | v1 · P2 |
| WS-045 | Stock Periods | base | `/warehouse/ledger/periods` | SV | Y | v1 · P0 |
| WS-046 | Soft-close Overrides | base | `/warehouse/ledger/period-overrides` | C | Y | v1 · P0 |
| WS-047 | Reservations | base | `/warehouse/ledger/reservations` | SV | Y | v1 · P2 |
| WS-048 | Allocation Strategies | base | `/warehouse/masters/allocation-strategies` | D | Y | v1 · P2 |
| WS-049 | Cost Layers | base | `/warehouse/ledger/cost-layers` | C | Y | v1 · P2 |
| WS-050 | Valuation Policies | base | `/warehouse/masters/valuation-policies` | D | Y | v1 · P2 |
| WS-051 | GL Posting Rules | base | `/warehouse/masters/gl-posting-rules` | D | Y | v1 · P2 |
| WS-052 | Accounting Handover Queue | base | `/warehouse/platform/handovers` | SV | Y | v1 · P2 |
| WS-053 | Port Monitor — Inbound Messages | base | `/warehouse/platform/port-monitor` | SV | Y | v1 · P2 |
| WS-054 | Port Rejected Queue | base | `/warehouse/platform/port-rejected` | SV | N | v1 · P2 |
| WS-055 | Movement Batches | base | `/warehouse/platform/movement-batches` | C | Y | v1 · P2 |
| WS-056 | Outbox Monitor | base | `/warehouse/platform/outbox` | C | Y | v1 · P2 |
| WS-057 | Outbox Subscriptions | base | `/warehouse/platform/outbox-subscriptions` | D | Y | v1 · P2 |
| WS-058 | Outbox Dead-letter | base | `/warehouse/platform/outbox-deliveries` | SV | Y | v1 · P2 |
| WS-059 | Tasks | base | `/warehouse/execution/tasks` | SV | Y | v1 · P0 |
| WS-060 | Devices | base | `/warehouse/platform/devices` | D | Y | v1.1 · P3 |
| WS-061 | Number Series | base | `/warehouse/masters/number-series` | D | Y | v1 · P1 |
| WS-062 | Numbers Issued | base | `/warehouse/platform/numbers-issued` | C | Y | v1 · P1 |
| WS-063 | Warehouse Audit Events | base | `/warehouse/platform/audit-events` | C | Y | v1 · P1 |
| WS-064 | Job Runs | base | `/warehouse/platform/job-runs` | C | Y | v1 · P1 |
| WS-065 | Import Batches | base | `/warehouse/platform/imports` | SV | Y | v1 · P1 |
| WS-066 | Category Stocking Ownership | base | `/warehouse/masters/category-ownership` | D | Y | v1 · P2 |
| WS-067 | External Stock Snapshots | base | `/warehouse/platform/external-snapshots` | C | Y | v1 · P2 |
| WS-068 | Channels | base | `/warehouse/masters/channels` | D | Y | v1 · P1 |
| WS-069 | Alert Rules | base | `/warehouse/platform/alert-rules` | C | Y | v1.1 · P3 |
| WS-070 | Alert Events | base | `/warehouse/platform/alert-events` | C | Y | v1.1 · P3 |
| WS-071 | Scan Enquiry Console | base | `/warehouse/ledger/scan` | — | N | v1 · P1 |
| WS-072 | Purchase Orders | app | `/warehouse/inbound/purchase-orders` | SV | Y | v1 · P1 |
| WS-073 | Purchase Order Detail | app | `/warehouse/inbound/purchase-orders/[id]` | — | N | v1 · P1 |
| WS-074 | ASNs | app | `/warehouse/inbound/asns` | SV | Y | v1.1 · P3 |
| WS-075 | Receiving Sessions | app | `/warehouse/inbound/receiving-sessions` | SV | Y | v1 · P1 |
| WS-076 | Goods Receipts | app | `/warehouse/inbound/goods-receipts` | SV | Y | v1 · P1 |
| WS-077 | Goods Receipt Detail | app | `/warehouse/inbound/goods-receipts/[id]` | — | N | v1 · P1 |
| WS-078 | Receipt Reversals | app | `/warehouse/inbound/receipt-reversals` | SV | Y | v1 · P1 |
| WS-079 | Inspection Plans | app | `/warehouse/inbound/inspection-plans` | C | Y | v1 · P1 |
| WS-080 | Quality Inspections | app | `/warehouse/inbound/quality-inspections` | SV | Y | v1 · P1 |
| WS-081 | Putaway Rules | app | `/warehouse/inbound/putaway-rules` | C | Y | v1 · P1 |
| WS-082 | Putaway Tasks | app | `/warehouse/inbound/putaway-tasks` | SV | Y | v1 · P1 |
| WS-083 | Inbound Reconciliation Cases | app | `/warehouse/inbound/reconciliation-cases` | SV | Y | v1 · P2 |
| WS-084 | Supplier Returns | app | `/warehouse/inbound/supplier-returns` | SV | Y | v1 · P2 |
| WS-085 | Dock Doors | app | `/warehouse/inbound/dock-doors` | C | Y | v1 · P1 |
| WS-086 | Dock Appointments | app | `/warehouse/inbound/dock-appointments` | SV | Y | v1.1 · P3 |
| WS-087 | Cross-dock Plans | app | `/warehouse/inbound/cross-dock` | C | Y | v2 · P5 |
| WS-088 | Three-way Matches | app | `/warehouse/inbound/three-way-match` | SV | Y | v2 · P5 |
| WS-089 | Stock Adjustments | app | `/warehouse/inventory/adjustments` | SV | Y | v1 · P2 |
| WS-090 | Transfer Orders | app | `/warehouse/inventory/transfers` | SV | Y | v1 · P2 |
| WS-091 | Hold Types | app | `/warehouse/inventory/hold-types` | D | Y | v1 · P2 |
| WS-092 | Holds | app | `/warehouse/inventory/holds` | SV | Y | v1 · P2 |
| WS-093 | Count Programs | app | `/warehouse/inventory/count-programs` | C | Y | v1 · P2 |
| WS-094 | Counts | app | `/warehouse/inventory/counts` | SV | Y | v1 · P2 |
| WS-095 | Count Entry & Variance | app | `/warehouse/inventory/counts/[id]` | — | N | v1 · P2 |
| WS-096 | Insufficient Stock & Lost Sales | app | `/warehouse/inventory/insufficient-stock` | C | Y | v1 · P2 |
| WS-097 | Blocked Movements Queue | app | `/warehouse/inventory/blocked-movements` | SV | Y | v1 · P2 |
| WS-098 | Reconciliation Exceptions | app | `/warehouse/inventory/reconciliation-exceptions` | SV | Y | v1 · P2 |
| WS-099 | Demand Orders | app | `/warehouse/outbound/orders` | SV | Y | v1 · P2 |
| WS-100 | Demand Order Detail | app | `/warehouse/outbound/orders/[id]` | — | N | v1 · P2 |
| WS-101 | Waves | app | `/warehouse/outbound/waves` | SV | Y | v1.1 · P3 |
| WS-102 | Pick Tasks | app | `/warehouse/outbound/pick-tasks` | SV | Y | v1 · P2 |
| WS-103 | Pack Sessions | app | `/warehouse/outbound/pack-sessions` | SV | Y | v1.1 · P3 |
| WS-104 | Cartons | app | `/warehouse/outbound/cartons` | C | Y | v1 · P2 |
| WS-105 | Shipments | app | `/warehouse/outbound/shipments` | SV | Y | v1 · P2 |
| WS-106 | Shipment Detail | app | `/warehouse/outbound/shipments/[id]` | — | N | v1 · P2 |
| WS-107 | Carriers | app | `/warehouse/outbound/carriers` | D | Y | v1 · P2 |
| WS-108 | Carrier Services | app | `/warehouse/outbound/carrier-services` | C | Y | v1 · P2 |
| WS-109 | Carrier Accounts | app | `/warehouse/outbound/carrier-accounts` | C | Y | v1 · P2 |
| WS-110 | Manifests | app | `/warehouse/outbound/manifests` | SV | Y | v1.1 · P3 |
| WS-111 | Handovers | app | `/warehouse/outbound/handovers` | SV | Y | v1.1 · P3 |
| WS-112 | Pickup Requests | app | `/warehouse/outbound/pickup-requests` | SV | Y | v1.1 · P3 |
| WS-113 | Consignments | app | `/warehouse/outbound/consignments` | C | Y | v1.1 · P3 |
| WS-114 | Shipping Labels | app | `/warehouse/outbound/shipping-labels` | C | Y | v1.1 · P3 |
| WS-115 | Tracking Events | app | `/warehouse/outbound/tracking-events` | C | Y | v2 · P5 |
| WS-116 | Carrier Status Mappings | app | `/warehouse/outbound/status-mappings` | D | Y | v2 · P5 |
| WS-117 | Rate Quotes | app | `/warehouse/outbound/rate-quotes` | C | Y | v2 · P5 |
| WS-118 | Carrier Serviceability | app | `/warehouse/outbound/serviceability` | C | Y | v2 · P5 |
| WS-119 | AWB Pools & Numbers | app | `/warehouse/outbound/awb-pools` | SV | Y | v2 · P5 |
| WS-120 | NDR Console | app | `/warehouse/outbound/ndr` | SV | Y | v2 · P5 |
| WS-121 | COD Remittances | app | `/warehouse/outbound/cod-remittances` | SV | Y | v2 · P5 |
| WS-122 | RTO Consignments | app | `/warehouse/outbound/rto` | SV | Y | v1 · P2 |
| WS-123 | Channel Accounts | app | `/warehouse/outbound/channel-accounts` | C | Y | v2 · P5 |
| WS-124 | Channel Order Imports | app | `/warehouse/outbound/channel-imports` | SV | Y | v2 · P5 |
| WS-125 | Channel Publish Rules | app | `/warehouse/outbound/publish-rules` | C | Y | v2 · P5 |
| WS-126 | Tracking Links | app | `/warehouse/outbound/tracking-links` | C | Y | v2 · P5 |
| WS-127 | Working Calendars | app | `/warehouse/outbound/calendars` | C | Y | v2 · P5 |
| WS-128 | Order Edit Rules | app | `/warehouse/outbound/order-edit-rules` | D | Y | v1.1 · P3 |
| WS-129 | Weighing Instruments | app | `/warehouse/execution/weighing-instruments` | D | Y | v2 · P5 |
| WS-130 | Weighing Records | app | `/warehouse/execution/weighing-records` | C | Y | v2 · P5 |
| WS-131 | Print Templates | app | `/warehouse/printing/templates` | SV | Y | v1 · P2 |
| WS-132 | Print Jobs | app | `/warehouse/printing/jobs` | SV | Y | v1 · P2 |
| WS-133 | Printers | app | `/warehouse/printing/printers` | D | Y | v1.1 · P3 |
| WS-134 | Print Routing Rules | app | `/warehouse/printing/routing-rules` | C | Y | v1.1 · P3 |
| WS-135 | Return Receipts | app | `/warehouse/inbound/returns` | SV | Y | v1 · P2 |
| WS-136 | RMAs | app | `/warehouse/inbound/rmas` | SV | Y | v1 · P2 |
| WS-137 | Return Gradings | app | `/warehouse/inbound/return-gradings` | C | Y | v2 · P5 |
| WS-138 | Obsolescence Returns | app | `/warehouse/inbound/obsolescence-returns` | SV | Y | v2 · P5 |
| WS-139 | Recalls | app | `/warehouse/inventory/recalls` | SV | Y | v2 · P5 |
| WS-140 | Replenishment Runs | app | `/warehouse/inventory/replenishment-runs` | SV | Y | v1 · P2 |
| WS-141 | Replenishment Suggestions | app | `/warehouse/inventory/replenishment-suggestions` | C | Y | v1 · P2 |
| WS-142 | Replenishment Tasks | app | `/warehouse/execution/replenishment-tasks` | SV | Y | v1.1 · P3 |
| WS-143 | Demand History | app | `/warehouse/inventory/demand-history` | C | Y | v1 · P2 |
| WS-144 | Work Orders | app | `/warehouse/execution/work-orders` | SV | Y | v1.1 · P3 |
| WS-145 | VAS Service Types | app | `/warehouse/execution/vas-service-types` | D | Y | v1.1 · P3 |
| WS-146 | Labour Tasks | app | `/warehouse/execution/labour-tasks` | C | Y | v2 · P5 |
| WS-147 | Landed Cost Documents | app | `/warehouse/inventory/landed-costs` | SV | Y | v1 · P2 |
| WS-148 | Revaluations | app | `/warehouse/inventory/revaluations` | SV | Y | v1 · P2 |
| WS-149 | NRV Assessments | app | `/warehouse/inventory/nrv-assessments` | SV | Y | v2 · P5 |
| WS-150 | Opening Stock Batches | app | `/warehouse/golive/opening-stock` | SV | Y | v1 · P2 |
| WS-151 | Cut-over Checklists | app | `/warehouse/golive/cutover` | SV | Y | v1 · P2 |
| WS-152 | Migration Mappings | app | `/warehouse/golive/mappings` | C | Y | v1.1 · P3 |
| WS-153 | Supervisor Exception Console | app | `/warehouse/execution/exceptions` | — | N | v1.1 · P3 |
| WS-154 | Task Assignment Board | app | `/warehouse/execution/assignment` | — | N | v1.1 · P3 |
| WS-155 | 3PL Clients | 3pl | `/warehouse/3pl/clients` | SV | Y | v2 · P5 |
| WS-156 | Onboarding Templates | 3pl | `/warehouse/3pl/onboarding-templates` | C | Y | v2 · P5 |
| WS-157 | Onboarding Tasks | 3pl | `/warehouse/3pl/onboarding-tasks` | SV | Y | v2 · P5 |
| WS-158 | Charge Codes | 3pl | `/warehouse/3pl/charge-codes` | D | Y | v2 · P5 |
| WS-159 | Rate Cards | 3pl | `/warehouse/3pl/rate-cards` | SV | Y | v2 · P5 |
| WS-160 | Billable Events | 3pl | `/warehouse/3pl/billable-events` | C | Y | v2 · P5 |
| WS-161 | Storage Billing Periods | 3pl | `/warehouse/3pl/storage-billing` | SV | Y | v2 · P5 |
| WS-162 | Billing Runs | 3pl | `/warehouse/3pl/billing-runs` | SV | Y | v2 · P5 |
| WS-163 | Accessorials | 3pl | `/warehouse/3pl/accessorials` | SV | Y | v2 · P5 |
| WS-164 | Disputes | 3pl | `/warehouse/3pl/disputes` | SV | Y | v2 · P5 |
| WS-165 | Freight Billing Rules | 3pl | `/warehouse/3pl/freight-rules` | C | Y | v2 · P5 |
| WS-166 | SLA Definitions | 3pl | `/warehouse/3pl/sla-definitions` | C | Y | v2 · P5 |
| WS-167 | SLA Measurements | 3pl | `/warehouse/3pl/sla-measurements` | C | Y | v2 · P5 |
| WS-168 | SLA Breaches | 3pl | `/warehouse/3pl/sla-breaches` | SV | Y | v2 · P5 |
| WS-169 | Client GST Registrations | 3pl | `/warehouse/3pl/client-gst` | C | Y | v2 · P4 |
| WS-170 | AR Handover Queue | 3pl | `/warehouse/3pl/ar-handovers` | SV | Y | v2 · P5 |
| WS-171 | Client Profitability | 3pl | `/warehouse/3pl/profitability` | C | Y | v3 · P6 |
| WS-172 | Client Portal | 3pl | `/warehouse/3pl/portal` | — | N | v2 · P5 |
| WS-173 | GSTIN Profiles | india | `/warehouse/india/gstin-profiles` | C | Y | v1 · P2-IN |
| WS-174 | Compliance Providers | india | `/warehouse/india/providers` | C | Y | v1 · P2-IN |
| WS-175 | Compliance Registrations | india | `/warehouse/india/registrations` | C | Y | v1 · P2-IN |
| WS-176 | Compliance Documents | india | `/warehouse/india/compliance-documents` | C | Y | v1 · P2-IN |
| WS-177 | Compliance API Logs | india | `/warehouse/india/api-logs` | C | Y | v1 · P2-IN |
| WS-178 | Delivery Challans | india | `/warehouse/india/challans` | SV | Y | v1 · P2-IN |
| WS-179 | E-way Bills | india | `/warehouse/india/eway-bills` | SV | Y | v1 · P2-IN |
| WS-180 | Consolidated E-way Bills | india | `/warehouse/india/eway-bills-consolidated` | SV | Y | v2 · P4 |
| WS-181 | Job Work Registrations | india | `/warehouse/india/job-work` | SV | Y | v2 · P4 |
| WS-182 | ITC-04 Returns | india | `/warehouse/india/itc04` | SV | Y | v2 · P4 |
| WS-183 | Statutory Stock Account | india | `/warehouse/india/stock-account` | C | Y | v2 · P4 |
| WS-184 | ITC Reversals | india | `/warehouse/india/itc-reversals` | C | Y | v2 · P4 |
| WS-185 | Bonded Licences | india | `/warehouse/india/bonded-licences` | C | Y | v2 · P4 |
| WS-186 | Warehousing Bonds | india | `/warehouse/india/bonds` | SV | Y | v2 · P4 |
| WS-187 | Ex-bond Clearances | india | `/warehouse/india/ex-bond` | SV | Y | v2 · P4 |
| WS-188 | Goods on Approval | india | `/warehouse/india/approval-dispatches` | SV | Y | v2 · P4 |
| WS-189 | EPR Returns | india | `/warehouse/india/epr` | SV | Y | v2 · P4 |
| WS-190 | Retention Policies | india | `/warehouse/india/retention-policies` | D | Y | v2 · P4 |
| WS-191 | Compliance Tasks & Rules | india | `/warehouse/india/compliance-tasks` | SV | Y | v2 · P4 |
| WS-192 | Tax Rules Workbench | india | `/warehouse/india/tax-rules` | — | Y | v2 · P4 |
| WS-193 | HSN / SAC / State Codes | india | `/warehouse/india/tax-reference` | D | Y | v2 · P4 |
| WS-194 | Counter Sale | dealer | `/warehouse/dealer/counter-sale` | — | Y | v1 · P2 |
| WS-195 | Vehicle Fitments | dealer | `/warehouse/dealer/fitments` | C | Y | v1 · P2 |
| WS-196 | OEM Orders | dealer | `/warehouse/dealer/oem-orders` | SV | Y | v1.1 · P3 |
| WS-197 | OEM Price Files | dealer | `/warehouse/dealer/price-files` | SV | Y | v1.1 · P3 |
| WS-198 | Core Exchanges | dealer | `/warehouse/dealer/core-exchanges` | SV | Y | v2 · P5 |
| WS-199 | Material Requests | services | `/warehouse/services/material-requests` | SV | Y | v1 · P2 |
| WS-200 | Job Part Issues & WIP | services | `/warehouse/services/job-part-issues` | C | Y | v1 · P2 |
| WS-201 | Fitted Serials | services | `/warehouse/services/fitted-serials` | C | Y | v1 · P2 |
| WS-202 | Warranty Holds | services | `/warehouse/services/warranty-holds` | SV | Y | v2 · P5 |
| WS-203 | Van Stock Assignments | field-service | `/warehouse/field-service/van-stock` | SV | Y | v1.1 · P3 |
| WS-204 | Van Replenishments | field-service | `/warehouse/field-service/van-replenishments` | SV | Y | v1.1 · P3 |
| WS-205 | Job Consumptions | field-service | `/warehouse/field-service/job-consumptions` | C | Y | v1.1 · P3 |
| WS-206 | Spare Consumptions | assets | `/warehouse/assets/spare-consumptions` | C | Y | v1.1 · P3 |
| WS-207 | Asset ↔ Item Links | assets | `/warehouse/assets/asset-item-links` | C | Y | v1.1 · P3 |
| WS-208 | Stock on Hand | app | `/warehouse/reports/stock-on-hand` | C | Y | v1 · P2 |
| WS-209 | Stock Movement Register (report) | app | `/warehouse/reports/movement-register` | C | Y | v1 · P2 |
| WS-210 | Godown-wise Stock Statement | app | `/warehouse/reports/godown-statement` | C | Y | v1 · P2 |
| WS-211 | Stock Valuation (as-at) | app | `/warehouse/reports/valuation` | C | Y | v1 · P2 |
| WS-212 | Stock Ageing | app | `/warehouse/reports/ageing` | C | Y | v1 · P2 |
| WS-213 | Adjustment Register | app | `/warehouse/reports/adjustment-register` | C | Y | v1 · P2 |
| WS-214 | Count History & Variance | app | `/warehouse/reports/count-variance` | C | Y | v1 · P2 |
| WS-215 | Low & Insufficient Stock | app | `/warehouse/reports/low-stock` | C | Y | v1 · P2 |
| WS-216 | Operational KPIs | app | `/warehouse/reports/kpis` | C | Y | v1 · P2 |
| WS-217 | Parts KPIs | app | `/warehouse/reports/parts-kpis` | C | Y | v1 · P2 |
| WS-218 | Traceability | app | `/warehouse/reports/traceability` | — | Y | v1 · P2 |
| WS-219 | Stock-to-GL Reconciliation | app | `/warehouse/reports/stock-to-gl` | C | Y | v1 · P2 |
| WS-220 | In-transit Ageing | app | `/warehouse/reports/in-transit-ageing` | C | Y | v1 · P2 |
| WS-221 | Expiry & Shelf-life Register | app | `/warehouse/reports/expiry` | C | Y | v1 · P2 |
| WS-222 | Consolidated Valuation | app | `/warehouse/reports/consolidated-valuation` | C | Y | v1.1 · P3 |
| WS-223 | Install Health Signals | app | `/warehouse/reports/health` | — | Y | v1.1 · P3 |
| WS-224 | Stock As-At | app | `/warehouse/reports/stock-as-at` | C | Y | v1 · P2 |
| WS-225 | Coexistence Reconciliation | app | `/warehouse/reports/coexistence` | C | Y | v1 · P2 |
| WS-226 | Stock by MRP | india | `/warehouse/india/stock-by-mrp` | C | Y | v2 · P4 |
| WS-227 | Custody & Insured Value | 3pl | `/warehouse/3pl/custody-value` | C | Y | v2 · P5 |
| WS-228 | Operations Dashboard | app | `/warehouse/reports/dashboard` | — | N | v3 · P6 |
| WS-229 | RF Receive | mobile | `screens/whRfReceive` | — | N | v1.1 · P3 |
| WS-230 | RF Putaway | mobile | `screens/whRfPutaway` | — | N | v1.1 · P3 |
| WS-231 | RF Move | mobile | `screens/whRfMove` | — | N | v1.1 · P3 |
| WS-232 | RF Pick | mobile | `screens/whRfPick` | — | N | v1.1 · P3 |
| WS-233 | RF Pack | mobile | `screens/whRfPack` | — | N | v1.1 · P3 |
| WS-234 | RF Ship | mobile | `screens/whRfShip` | — | N | v1.1 · P3 |
| WS-235 | RF Cycle Count | mobile | `screens/whRfCycleCount` | — | N | v1.1 · P3 |
| WS-236 | RF Stock Enquiry | mobile | `screens/whRfStockEnquiry` | — | N | v1.1 · P3 |
| WS-237 | RF Task List | mobile | `screens/whRfTaskList` | — | N | v1.1 · P3 |
| WS-238 | Warehouse Grants | base | `/warehouse/masters/warehouse-grants` | C | Y | v1 · P1 |
| WS-239 | Item Prices | dealer | `/warehouse/dealer/item-prices` | D | Y | v1 · P2 |
| WS-240 | Trade Portal | app | `/warehouse/outbound/trade-portal` | C | Y | v2 · P5 |
| WS-241 | Approval Levels | app | `/warehouse/inventory/approval-levels` | D | Y | v2 · P5 |
| WS-243 | Location Utilisation | app | `/warehouse/reports/location-utilisation` | C | Y | v3 · P6 |
| WS-244 | Metric Targets | app | `/warehouse/reports/metric-targets` | D | Y | v1 · P2 |

<!-- check-design-set: screen-citations begin WS-242 WS-245 — the §1 allocation marker: WS-242 is reserved for P5-13's marketplace-claim queue and has no row until that task's PR adds one; WS-245 is the next free id -->
**The allocation marker.** `WS-238` *Warehouse Grants* took its row on 2026-09-11, when round 3's `RA-001`
was folded into `P1-18`. The same day's second fold (lane `W0-1b`):
- gave `WS-239` *Item Prices* to `RA-002` (`P2-25`);
- **reserved `WS-242`** for `P5-13`'s marketplace-claim queue, whose table has existed since `X-001`. It
  has no row until that task's PR adds one;
- allocated `WS-243` *Location Utilisation* (`RC-009`, `P6-02`, v3) and `WS-244` *Metric Targets*
  (`RC-007`, `P2-21`).

`WS-240` and `WS-241` were allocated by `GAP-REGISTER-R4.md` §4.0. **The next free id is `WS-245`.** The
round-4 junctions are sub-grids on existing screens: WS-015, WS-016, WS-017, WS-021, WS-023 and WS-173.
<!-- check-design-set: screen-citations end -->

---

## 2. `warehouse-base` — `whb_`, band V500000–V509999

### 2.1 The fourteen catalogues — WS-001 … WS-014

`D-10` and `FR-375`/`FR-376`: every extensible vocabulary is a table with **no `CHECK` constraint, no
Java enum and no TypeScript string union**. `DATA-MODEL.md` §2.1.1 reconciles `D-10`'s thirteen with
`FR-375`'s thirteen and adds `whb_condition_codes` as the fourteenth — **`WarehouseBaseCouplingTest`
enumerates fourteen `table.column` pairs and asserts none carries a `CHECK (… IN (…))`.**

**One block for all fourteen, because they are one shape.** Build the first, then copy.

| Field | Value |
|---|---|
| Reference | **Department** — modal CRUD, no lifecycle, no cascade |
| Route | `/warehouse/catalogues/<kebab-plural>` |
| `gridIdentifier` | the table name |
| Filter scope | `WAREHOUSE_<SINGULAR>` |
| Caches | `dropdown.<entityCamelCase>` (every catalogue backs at least one dropdown) · statistics `—` (filter-aware, `FR-395`) |
| Permission | `<table>:view|create|edit|delete|export` |
| Version | v1; phase per the index above |
| Migration | seed DDL per `DATA-MODEL.md` §7.2 (`V500002`–`V500010`); grid config one file in `V501020`–`V501099` |

**Columns — every catalogue** (`{table}.` prefix implied on the source):

| key | label | type | sortable | default-visible | source |
|---|---|---|---|---|---|
| `code` | Code | string | Y | Y | `code` |
| `name` | Name | string | Y | Y | `name` |
| `description` | Description | string | N | N | `description` |
| `owningModule` | Owning module | string | Y | Y | `owning_module` — **an opaque string, never an FK** (`FR-376`) |
| `isSystem` | System | boolean | Y | Y | `is_system` — drives the delete gate |
| *behaviour columns* | per catalogue | boolean/string | Y | Y | see the delta table below |
| `isActive` | Status | boolean | Y | Y | `is_active` |
| `createdByName` | Created by | string | N | N | join `users`/`user_details` via the shared display helper |
| `updatedByName` | Updated by | string | N | N | idem |
| `createdAt` | Created | datetime | Y | N | `created_at` |
| `updatedAt` | Updated | datetime | Y | N | `updated_at` |

**Filters — every catalogue:** `code` (`text`, visible) · `name` (`text`, visible) ·
`owningModule` (`select`, visible; options from `GET /warehouse/registries/owning-modules`) ·
`isSystem` (`boolean`) · `isActive` (`boolean`, visible) · plus one `boolean` filter per behaviour
flag the operator actually triages on (named in the delta table). No cascading dependency anywhere in
this family.

**Export:** the visible set plus `description`, every behaviour column, `createdByName`,
`updatedByName`, `createdAt`, `updatedAt` — a strict superset, and the audit pair **is** present
because the grid shows it.

**Modals:** Add/Edit `Modal size="lg" minWidth={500} resizable` — single tab (never more than six
field groups): *Identity* (`code`, `name`, `description`) · *Behaviour* (the flags) · *Ownership*
(`owning_module`, `is_system` read-only) · *Status* (`is_active`). View = `ViewModalBase` with
`InfoSection` per group and a `StatusCard` for `is_active`.
**v2 — a *Translations* tab** (`P1-19`'s v2 increment, folded from `P5-28`; `FR-469`): per-locale names over `whb_registry_translations`
(`registry_table`, `code`, `locale`, `name`), which are read before the row's own `name`. It lands on
every registry screen built from this block, WS-091 and WS-158 included. It matters most for an
install-created row (`owning_module = 'INSTALL'`), which has no i18n key. **v1 has no tab** and renders the
row's `name` through `PC-69`'s fallback.
`code` is **immutable after create** and rendered read-only on edit — every ledger row FKs to it by
code (`whb_stock_movements.movement_type_code`, `…_lines.stock_status_code`).

**Actions.** Row: View (`:view`) · Edit (`:edit` **and** `is_system = false`) · Activate/Deactivate
(`:edit`; deactivation refused where a live row references the code — the service returns
`REGISTRY_ROW_IN_USE`) · Delete (`:delete` **and** `is_system = false` **and** zero references).
Toolbar: Add (`:create`) · Export (`hasAuthority('<table>:export') or hasRole('ADMIN')`) ·
Grid config · Help.

**Mobile:** `none` for all fourteen — a catalogue is administered from a desk, and no RF flow of
`FR-217` edits one. **But `FR-382`/`OD-5` obligation applies to each:** wherever a mobile screen shows
one of these vocabularies it must **fetch** it, and `mobile/src/schemas/common.schemas.ts` must not
re-enumerate it as a zod enum. That file is a third copy of every dropdown vocabulary and a value the
backend opened but the schema closed fails the save with no message.

**The deltas — the only thing that differs between the fourteen:**

| id | Screen | Table | Scope | Behaviour columns shown as grid columns (all sortable, all default-visible) | Triage filters |
|---|---|---|---|---|---|
| WS-001 | Movement Types | `whb_movement_types` | `WAREHOUSE_MOVEMENT_TYPE` | `direction`, `is_financial`, `cost_basis_default`, `balance_rule`, `requires_approval`, `requires_reason`, `affects_availability`, `is_stock_bearing`, `is_billable_event`, `reversal_type_code` | `direction` (select), `is_financial`, `requires_approval` |
| WS-002 | Document & Reference Types | `whb_document_types` | `WAREHOUSE_DOCUMENT_TYPE` | `is_stock_bearing`, `is_external`, `display_resolver_bean` | `is_external` |
| WS-003 | Source Systems | `whb_source_systems` | `WAREHOUSE_SOURCE_SYSTEM` | `module`, `is_reserved`, `is_claimable`, `post_permission` | `is_reserved`, `is_claimable` |
| WS-004 | Stock Statuses | `whb_stock_statuses` | `WAREHOUSE_STOCK_STATUS` | `is_on_hand`, `is_available_to_promise`, `is_allocatable`, `is_pickable`, `is_shippable`, `is_countable`, `is_owned_asset`, `requires_reason_to_enter`, `requires_reason_to_leave`, `badge_variant` | `is_allocatable`, `is_on_hand` |
| WS-005 | Location Types | `whb_location_types` | `WAREHOUSE_LOCATION_TYPE` | `is_physical`, `is_stock_holding`, `is_virtual_counterparty`, `is_mobile`, `is_transit`, `allows_mixed_owner`, `requires_assigned_user`, `default_location_level` | `is_physical`, `is_transit` |
| WS-006 | Reason Codes | `whb_reason_codes` | `WAREHOUSE_REASON_CODE` | `context` (**no `CHECK`** — free registry string), `requires_note`, `blocks_posting`, `affects_demand_history`, `itc_treatment`, `statutory_category` | `context` (select), `affects_demand_history` |
| WS-007 | UoM Classes | `whb_uom_classes` | `WAREHOUSE_UOM_CLASS` | `base_uom_code` | — |
| WS-008 | Task Types | `whb_task_types` | `WAREHOUSE_TASK_TYPE` | `is_directed`, `default_priority`, `interleavable`, `labour_standard_minutes`, `required_resource_type` | `is_directed`, `required_resource_type` (select) |
| WS-009 | Owner Types | `whb_owner_types` | `WAREHOUSE_OWNER_TYPE` | `is_house`, `posts_to_our_gl`, `default_cost_basis` | `is_house`, `posts_to_our_gl` |
| WS-010 | Item Types | `whb_item_types` | `WAREHOUSE_ITEM_TYPE` | `is_stocked`, `is_serial_default`, `is_lot_default`, `is_returnable_equipment`, `is_asset_shaped`, `is_value_only` | `is_stocked` |
| WS-011 | Counterparty Roles | `whb_counterparty_roles` | `WAREHOUSE_COUNTERPARTY_ROLE` | `is_supply_side`, `is_demand_side` | `is_supply_side`, `is_demand_side` |
| WS-012 | Dispositions | `whb_dispositions` | `WAREHOUSE_DISPOSITION` | `movement_type_code`, `target_stock_status_code`, `requires_inspection`, `emits_credit_signal` | `requires_inspection` |
| WS-013 | Attribute Keys | `whb_attribute_keys` | `WAREHOUSE_ATTRIBUTE_KEY` | `value_type`, `applies_to` — the `ATTRIBUTE_SUBJECT` code list (`RL-007`): `ITEM`, `MOVEMENT_LINE`, `LOT`, `SERIAL`, `LPN`, `LOCATION`, `COUNTERPARTY`, `DOCUMENT`, and **no `EVENT`** (register §3.7 e); `is_filterable`, `is_exportable`. **An install-created key (`owning_module = 'INSTALL'`) is the product's custom-field answer.** `LOT`-kind keys are captured on the GRN line in v1 (`P1-13`) | `value_type` (select), `applies_to` (select — options **fetched** from the code list, never enumerated) |
| WS-014 | Condition Codes | `whb_condition_codes` | `WAREHOUSE_CONDITION_CODE` | `is_sellable`, `is_repairable`, `grade_rank`, `default_disposition_code` | `is_sellable` |

> **`OD-5` applies to every one of these fourteen and is the single most likely way this product gets
> quietly broken.** CLAUDE.md TYPESCRIPT RULE #6 mandates string unions over enums; `D-10` mandates
> open catalogues. `FR-380` resolves it: **catalogue-backed dropdowns fetch their values; a string
> union is permitted only for a closed system vocabulary** — `posting_status`, `map_status` on an
> import row, an HTTP outcome. `types/whbMovementType.ts` must not contain
> `type MovementTypeCode = 'RECEIPT' | 'ISSUE' | …`.

---

### 2.2 Identity and the facility model

#### WS-015 · Companies

`/warehouse/masters/companies` · **Department** · `whb_companies` · `WAREHOUSE_COMPANY` ·
`whb_companies:*` · v1 · P1 · `FR-025` · table `V500001`, grid config in `V501020`–`V501099` ·
caches `dropdown.whbCompany`, statistics `—`.

**Columns:** `code` · `name` · `legalName` (`legal_name`) · `baseCurrencyCode` (`base_currency_code`,
FK ↓platform `currencies.currency_code`) · `countryCode` · `isDefault` (`is_default`) · `isActive` ·
`createdByName` · `updatedByName` · `createdAt` · `updatedAt`.
**Filters:** `code` text · `name` text · `countryCode` select (platform country source) ·
`baseCurrencyCode` select (the shared currency source — never a hand-built list) · `isActive` boolean.
**Export:** visible set + `legalName`, `isDefault`, both audit-name columns. **Modals:** single-tab
add/edit plus the *Company branches* sub-grid below; `ViewModalBase` view with a child `DataTable` of
`whb_company_external_refs` (`source_module`, `external_id`, `external_label`) — that table has **no
grid of its own**.
**Company branches** (`RH-004`, `D-14`) — a sub-grid on the modal and the view over
`whb_company_branches`: branch (`branches.branch_name`), `effectiveFrom`, `effectiveTo`. *Add link*
opens a row. *End link* sets `effective_to` and never deletes, and there is no `is_active` on this dated
junction. **This is the warehouse-owned company axis**, because platform `branches` carry no company and
`company_branches` is automotive's. WS-016's branch options and `422 WAREHOUSE_BRANCH_COMPANY_MISMATCH`
both read it. `warehouse-adapter-dealer` may seed it from automotive through
`whb_company_external_refs`; **base never reads automotive**. The junction has no grid of its own.
**Actions:** row View / Edit / Set-default (`:edit`; a partial unique index enforces one default) /
Deactivate. Toolbar Add / Export / Grid config.
**Mobile:** `none` — install-time configuration; no operator flow reads or writes it.

#### WS-016 · Warehouses (sites)

`/warehouse/masters/warehouses` · **Customer** (branch relation + cascading company→branch) ·
`whb_warehouses` · `WAREHOUSE_WAREHOUSE` · `whb_warehouses:*` · v1 · P1 ·
`FR-079` `FR-080` `FR-081` `FR-439` `FR-460` · tables `V500012` (`whb_warehouses`,
`whb_warehouse_branch_roles`, `whb_warehouse_branches` — `D-14`) · caches `dropdown.whbWarehouse`.

**A site is linked to platform branches, never mirrored as one** (`D-14`, `RG-001`). Its links are dated
rows in `whb_warehouse_branches`, and **exactly one is `REGISTERED` at every instant**. That branch supplies
the GSTIN, the branch-scoped series and the statutory attribution. `SERVING`, `FULFILMENT` and `RETURNS`
links grant visibility and let a branch draw stock. `whb_warehouses` no longer has `branch_id`,
`tax_registration_id` or `legal_entity_id`.

| key | label | type | sort | vis | source |
|---|---|---|---|---|---|
| `code` | Code | string | Y | Y | `whb_warehouses.code` — unique per company, `uk(company_id, code)` (`RL-004`) |
| `name` | Name | string | Y | Y | `name` |
| `companyName` | Company | string | Y | Y | `whb_companies.name` via `company_id` |
| `registeredBranchName` | Registered branch | string | Y | Y | **`branches.branch_name`** of the **current `REGISTERED` link** in `whb_warehouse_branches` — the platform column is `branch_name`, not `name` |
| `linkedBranchCount` | Linked branches | number | Y | Y | count of today's links of a visibility role — backend-computed. The column is labelled *Linked branches* |
| `warehouseType` | Type | string | Y | Y | `warehouse_type` |
| `isPhysical` | Physical | boolean | Y | Y | `is_physical` — `FR-081`, the logistics seam column |
| `city` | City | string | Y | Y | `city` |
| `stateCode` | State | string | Y | Y | `state_code` |
| `gstin` | GSTIN | string | N | Y | **read through the current `REGISTERED` link's `branches.gst_number`** — never duplicated onto the warehouse (`FR-079`, `D-14`) |
| `timezone` | Timezone | string | Y | N | `timezone` — `FR-439`, local-day bucketing; **a select validated against platform `timezones`**, never a free string (`RH-011`) |
| `gln` | GLN | string | N | N | `gln` |
| `orderCutoffTime` | Cut-off | string | N | N | `order_cutoff_time` |
| `hasPicking` | Picking | boolean | Y | N | `has_picking` |
| `isActive` | Status | boolean | Y | Y | `is_active` |
| `createdByName` / `updatedByName` / `createdAt` / `updatedAt` | audit | — | Y | N | audit quartet |

**Filters:** `companyId` select → **cascades to** `branchId` select → cascades to `warehouseType` ·
`relationshipRoleCode` select (options from `whb_warehouse_branch_roles`, fetched) · `isPhysical`
boolean · `stateCode` select · `isActive` boolean · `code`/`name` text. **`branchId` means *"linked
to"*** — the site holds a current link of any visibility role to the branch. With
`relationshipRoleCode = REGISTERED` it narrows to *"registered under"*. **The branch options come from a
warehouse endpoint** that returns *my-branches ∩ the company's branches* (`whb_company_branches`, WS-015),
intersected in the backend (`RH-004`). Platform `/branches/my-branches` has no company parameter, and a
frontend `.filter()` is forbidden. `relationshipRoleCode` goes into the `WAREHOUSE_WAREHOUSE` scope of
`COMMON_FILTER_CONFIGS` with the rest (§0.5).
**Export:** every visible column + `linkedBranchNames` (each current link as *branch (role)*,
comma-joined), `gln`, `latitude`, `longitude`, address lines 1/2, `postal_code`, `country_code`, both
audit names. `registeredBranchName` is a visible column and is therefore exported too. The
`legal_entity_id` and `tax_registration_id` labels are gone with their columns.
**Modals:** Add/Edit is **multi-tab** (8 field groups > 6): *Identity* · *Company* · *Address* ·
*Geo* (`latitude`, `longitude`) · *Tax identity* (the GSTIN, read-only through the `REGISTERED` link) ·
*Operations* (`timezone` select, `order_cutoff_time`, `default_putaway_strategy_code`, `has_picking`) ·
*Status* · **Branches**.
**Branches tab** — a sub-grid over `whb_warehouse_branches`: branch (`branches.branch_name`), role,
`effectiveFrom`, `effectiveTo`, `isPrimary`. *Add link* opens a non-`REGISTERED` row. *End link* sets
`effective_to` on a non-`REGISTERED` row and never deletes. **A site cannot be saved without a
`REGISTERED` link**: create writes the site and its link in one transaction (R22 §1.2.2 guard 1). A second
current `REGISTERED` link is refused, and `SERVING` is offered instead (`WH-SC-045`). A `REGISTERED` branch
missing from `whb_company_branches` for the site's company is refused with
`422 WAREHOUSE_BRANCH_COMPANY_MISMATCH`, and `warehouse-india`'s validators refuse a GSTIN state that
differs from `state_code`.
**Change registration** — its own modal, gated on `warehouse:warehouses:change_registration` and
maker–checker (`FR-408`); the checker is not the maker. It is refused for an `effective_from` in a
`CLOSED` period or before the site's latest posted `occurred_at`. It is also refused **while the site
holds non-zero on-hand and the old and new GSTINs differ**, and the modal states the on-hand quantity to
move out first (`OD-19`). It closes the current row and opens the next at the same instant, writes a
`whb_audit_events` row, and prompts for the new branch-scoped series (WS-061).
View = `ViewModalBase` with an `InfoGrid` per tab, a `StatusCard`, and a `DataTable` of the link
history, including closed rows.
**Actions:** row View / Edit / Deactivate (refused while any `whb_stock_positions` row for the site is
non-zero) / **Change registration** / **Generate locations** (`whb_locations:create`, opens WS-018).
Toolbar Add / Export / Grid config / Help.
**Mobile:** `mobile/src/screens/whbWarehouse/` — **read-only list + detail.** Site creation is a desk
task; the mobile screen exists because every RF screen needs a site picker and the picker reads this
list. **The picker follows R22 §1.2.4 row 15**: `useScopedBranchOptions` → branch →
`GET /warehouses/dropdown?branchId=`. The call returns the sites with a current link of a visibility role,
`REGISTERED` sites first, and each row carries a role badge. `additionalFilters`: `companyId`, `branchId`
(*"linked to"*, as on web) and `relationshipRoleCode` dropdowns, and `code` text. No date filter is
needed.

#### WS-017 · Locations

`/warehouse/masters/locations` · **Customer** · `whb_locations` · `WAREHOUSE_LOCATION` ·
`whb_locations:*` · v1 · P1 · `FR-082` `FR-083` `FR-084` `FR-086` `FR-087` `FR-088` `FR-091` ·
table `V500013` (★ must precede `V500030`) · caches `dropdown.whbLocation`.

| key | label | type | sort | vis | source |
|---|---|---|---|---|---|
| `code` | Code | string | Y | Y | `code` — **unique per site**: `uk(warehouse_id, code)` only (`RL-004`). A scanned code resolves within the session's or device's site, and a cross-site match is `409 AMBIGUOUS_LOCATION` (§0.13). **Frozen once a movement in the current period exists** (§0.12); it is printed on the bin label and carried by every queued scan |
| `name` | Name | string | Y | Y | `name` |
| `warehouseName` | Site | string | Y | Y | `whb_warehouses.name` |
| `locationLevel` | Level | string | Y | Y | `location_level` — SITE/BUILDING/ZONE/AISLE/RACK/LEVEL/POSITION |
| `locationTypeCode` | Type | string | Y | Y | `location_type_code` → `whb_location_types` — **frozen once stock is on hand**, with the capacity block (§0.12) |
| `parentPath` | Path | string | N | Y | the materialised `path` — this is what makes "count zone A" answerable |
| `status` | Status | string | Y | Y | `status` — AVAILABLE/BLOCKED/COUNTING/DAMAGED/FROZEN |
| `blockReason` | Block reason | string | N | N | `whb_reason_codes.name` via `block_reason_code_id` |
| `commingePolicy` | Commingle | string | Y | N | `commingle_policy` |
| `dedicatedOwnerName` | Dedicated owner | string | N | N | `whb_owners.name` via `dedicated_owner_id` |
| `assignedUserName` | Custodian | string | N | N | the current `CUSTODIAN` row in `whb_location_user_assignments` (`RG-004`; `assigned_user_id` is dropped), rendered `{firstName} {lastName} [{employee_id}] {primary_phone}` through the shared helper |
| `pickSequence` | Pick seq | number | Y | N | `pick_sequence` |
| `barcode` | Barcode | string | N | N | `barcode` |
| `temperatureZone` | Temp zone | string | Y | N | capacity block |
| `countsAsOnHand` | Counts as on-hand | boolean | Y | N | derived from `whb_location_types.is_stock_holding` |
| audit quartet + names | — | — | Y | N | — |

**Filters:** `warehouseId` select → cascades `parentLocationId` (subtree picker) → cascades
`locationLevel` select · `locationTypeCode` select · `status` select · `commingePolicy` select ·
`dedicatedOwnerId` select · `isPickable` boolean · `isReceivable` boolean · `code` text ·
`barcode` text.
**Export:** visible + the whole capacity block (`max_weight_kg`, `max_volume_cc`, `max_height_cm`,
`max_lpn_count`, `max_unit_count`, `allow_mixed_item`, `allow_mixed_lot`, `allow_mixed_owner`),
`putaway_priority`, `check_digit`, `gln`, both audit names.
**Modals:** Add/Edit multi-tab — *Identity* · *Hierarchy* (`parent_location_id`, `location_level`) ·
*Type & behaviour* · *Capacity* · *Commingle & ownership* · *Scanning* (`barcode`, `check_digit`) ·
*Status & blocking*. View = `ViewModalBase` + a child `DataTable` of
`whb_location_external_refs` (no grid of its own) and a live on-hand summary read from
`whb_stock_positions`.
**Custody** (`RG-004`, `D-14`) — a sub-grid on the modal and the view over
`whb_location_user_assignments`: user (shared display helper), `assignment_role` from the `CUSTODY_ROLE`
code list (`CUSTODIAN` / `DRIVER` / `HELPER`), `effectiveFrom`, `effectiveTo`. A location has one current
`CUSTODIAN`. *Change custodian* ends one row and opens the next, so *"who held the van's stock at last
Tuesday's shortage"* is a query and never an overwrite. The sub-grid has no grid of its own.
`whaf_van_stock_assignments` (WS-203) references these rows.
**Actions:** row View / Edit / **Block** and **Unblock** (own modals, mandatory reason code,
`whb_locations:block`) / **Print location label** (`wh_print_jobs:create`, template kind
`LOCATION_LABEL`). Toolbar Add / **Generate** (WS-018) / Import (CSV fallback of `FR-089`) /
Export / Grid config.
**Mobile:** `mobile/src/screens/whbLocation/` — read + **Block/Unblock** only. Creation and the
generator are desk tasks. Filters are `warehouseId`, `locationTypeCode`, `status` dropdowns plus a
`code`/`barcode` text input; the scan input resolves a scanned code straight to the detail.

#### WS-018 · Location Generator

`/warehouse/masters/locations/generate` · **no grid** · permission `whb_locations:create` ·
v1 · P1 · `FR-089`.

A three-step wizard, not a management page: **(1)** parameters — site, parent zone, aisle range, rack
range, level range, position range, a format mask, `location_type_code`, default capacities,
`pick_sequence` seed and step; **(2)** **preview** — the computed count, the **first and last
generated codes**, and a **uniqueness check within the site**. Location codes are unique per site only
(`uk(warehouse_id, code)`, `RL-004`), so the preview lists every generated code that collides with the
**same site's** existing codes, and never another site's. All of it is rendered before anything is written, because *"a modest warehouse has 3,000–20,000
locations and the barcodes must agree with the labels already on the racking"*; **(3)** commit, which
writes through the import framework (`whb_import_batches`, `import_kind = LOCATION_GENERATE`) so it
has a reversal path (`FR-416`).
**No modals** — the wizard is the page. **Actions:** Preview (idempotent, writes nothing) · Generate
(`whb_locations:create`) · Download CSV template (the `FR-089` fallback).
**Mobile:** `none` — a 20,000-row generation is not a handheld task, and the preview cannot be read on
a 4-inch screen. Recorded as a decision per `FR-218`.

#### WS-071 · Scan Enquiry Console

`/warehouse/ledger/scan` · **no grid** · permission `whb_stock_positions:view` · v1 · P1 ·
`FR-062` `FR-063`.

One input, one typed answer. Calls the single scan-resolution service, which resolves any scanned
string against barcodes, location codes, lot codes, serial numbers and document numbers and returns a
typed object. **Nothing parses barcodes inline anywhere in the product**, and **no scanner SDK enters
the codebase** — the engine consumes a plain string, so a keyboard-wedge device works. Every scan is
logged, resolved or not.
Result renders as a `ViewModalBase`-style panel routed by resolved type: item → on-hand by location ·
location → contents · lot → positions + expiry + genealogy link · serial → current custody, sold-to,
warranty (`FR-099`) · LPN → contents · document → the document's detail route.
**Mobile:** **WS-236 `whRfStockEnquiry` is the primary surface**, not a mirror — this web page is the
desk equivalent. See §6.9.

---

### 2.3 Owners and counterparties

#### WS-019 · Owners

`/warehouse/masters/owners` · **Department** · `whb_owners` · `WAREHOUSE_OWNER` · `whb_owners:*` ·
v1 · **P0** · `FR-107` `FR-108` `FR-109` · table `V500007` · caches `dropdown.whbOwner`.

`owner_id` is `NOT NULL` everywhere from v1 in **every** install and there is **no single-owner mode**
(`D-5`, `FR-109`) — so this screen ships in P0 even though `warehouse-3pl` is v2.
**Columns:** `code` · `name` · `ownerTypeCode` · `companyName` · `counterpartyName` (nullable — the
house owner is not a counterparty) · `isHouse` · `defaultCostBasis` · `isActive` · audit quartet + names.
**Filters:** `ownerTypeCode` select · `companyId` select → cascades `counterpartyId` async typeahead ·
`isHouse` boolean · `isActive` boolean · `code`/`name` text.
**Export:** visible + `posts_to_our_gl` (from the owner type), both audit names.
**Modals:** single-tab add/edit; view = `ViewModalBase` with a `StatusCard` and an on-hand-by-site
summary. The **house owner row is `is_system`-equivalent**: seeded by `V500007`, never deletable, and
the `is_house` partial unique index means the modal must refuse a second house owner per company with
a field-level error rather than a 500.
**Actions:** row View / Edit / Deactivate (refused with `OWNER_HAS_STOCK` while any position or open
reservation exists) / **Manage grants** (opens WS-020 filtered to the owner). Toolbar Add / Export.
**Mobile:** `mobile/src/screens/whbOwner/` — **read-only picker list.** Every RF screen posts against
an owner; the picker reads this. No writes.

#### WS-020 · Owner Grants

`/warehouse/masters/owner-grants` · **Customer** · `whb_owner_grants` · `WAREHOUSE_OWNER_GRANT` ·
`whb_owner_grants:*` · v1 · **P0** · `FR-114` `FR-406` · table `V500044`.

**Columns:** `ownerName` · `granteeType` (USER/ROLE/GROUP) · `granteeName` (rendered through the
shared user-display helper where the grantee is a user: `{firstName} {lastName} [{employee_id}]
{primary_phone}`) · `accessLevel` (VIEW/OPERATE/ADMIN) · `effectiveFrom` (`dateOnly`) ·
`effectiveTo` (`dateOnly`) · `isActive` · audit quartet + names.
**Filters:** `ownerId` select → cascades `granteeType` select → cascades `granteeId`
(async typeahead, scoped by grantee type — **scope before cap**, never cap-then-scope) ·
`accessLevel` select · `effectiveFromFrom` / `effectiveFromTo` (`dateOnly` pair — there is no
range type) · `isActive` boolean.
**Export:** visible + both audit names.
**Actions:** row View / Edit / Revoke (sets `effective_to`, never deletes). Toolbar Add / Export.
**Mobile:** `none` — access administration, desk only. Stated per `FR-218`.

> The screen is a management surface over a resolver, not the resolver. `FR-114`: a request naming an
> owner the caller has no grant for is rejected **`403`, never returned empty**, because an empty grid
> is indistinguishable from "no stock". A contract test fails the build if a repository method
> touching an owner-scoped table has no owner-set parameter (`FR-406`).

#### WS-238 · Warehouse Grants

`/warehouse/masters/warehouse-grants` · **Customer** · `whb_warehouse_grants` · `WAREHOUSE_WAREHOUSE_GRANT` ·
`whb_warehouse_grants:*` · v1 · **P1** · `FR-405` · table `V500047` · `RA-001`.

**Columns:** `warehouseName` · `granteeType` (USER/ROLE/GROUP) · `granteeName` (rendered through the
shared user-display helper where the grantee is a user) · `accessLevel` (VIEW/OPERATE/ADMIN) ·
`effectiveFrom` (`dateOnly`) · `effectiveTo` (`dateOnly`) · `isActive` · audit quartet + names.
**Filters:** `warehouseId` select → cascades `granteeType` select → cascades `granteeId` (async
typeahead, scoped by grantee type — **scope before cap**) · `accessLevel` select ·
`effectiveFromFrom` / `effectiveFromTo` (`dateOnly` pair) · `isActive` boolean.
**Export:** visible + both audit names.
**Actions:** row View / Edit / Revoke (sets `effective_to`, never deletes). Toolbar Add / Export.
**Mobile:** `none` — access administration, desk only. Stated per `FR-218`.

> The screen is a management surface over `P1-18`'s resolver, not the resolver. **A user with no grant
> row is unscoped on this axis, not blind**: a grant narrows the branch-derived site set and never
> widens it (`RA-001`, `RH-001`).

#### WS-021 · Counterparties

`/warehouse/masters/counterparties` · **Customer** · `whb_counterparties` · `WAREHOUSE_COUNTERPARTY` ·
`whb_counterparties:*` · v1 · P1 · `FR-116` `FR-117` `FR-118` `FR-119` · table `V500011` ·
caches `dropdown.whbCounterparty`.

**Columns:** `code` · `name` · `legalName` · `roles` (comma-joined from
`whb_counterparty_role_links` — SUPPLIER/CUSTOMER/CARRIER/CLIENT_3PL/TRANSPORTER/JOB_WORKER/INTERNAL) ·
`primaryRole` · `nationalTaxId` (the legal-entity id; a GSTIN is a tax-registration row) ·
`countryCode` · `city` · `gln` (these two now come from the primary address row, `RG-003`/`RG-020`) ·
`isActive` · audit quartet + names.
**Filters:** `roleCode` **multiselect** (a party is routinely two roles at once — a single-select here
is the `partner_type`-enum mistake in a filter) · `countryCode` select · `nationalTaxId` text ·
`taxRegistrationNumber` text (matches any current tax-registration row) · `code`/`name` text ·
`isActive` boolean · `sourceModule` select (drives the external-ref join).
**Export:** visible + the primary address block, the current tax registrations, `min_shelf_life_ship_pct`,
`valid_from`/`valid_to` per role, both audit names.
**Modals:** Add/Edit multi-tab — *Identity* · *Roles* (a child editor over
`whb_counterparty_role_links` with `is_primary`, `valid_from`, `valid_to`) · **Addresses** (a child
editor over `whb_counterparty_addresses`: role from the `ADDRESS_ROLE` code list, `is_primary`, the
address block, `gln`, dated) · **Tax registrations** (a child editor over
`whb_counterparty_tax_registrations`: scheme, registration number, state, dated). A counterparty's GSTIN
depends on the ship-to state, so the challan and e-way bill freeze the registration row and address row
they used (WS-178, WS-179) · *Shipping* (`min_shelf_life_ship_pct`, nullable: the shelf-life-at-ship
guard resolves counterparty → channel → item, `RJ-009`) · *Status*.
View = `ViewModalBase` + `DataTable`s of roles, addresses, tax registrations and
`whb_counterparty_external_refs`.
**The modal carries no payment terms, credit limit, bank details, contacts or scorecard** (`FR-119`)
— if a builder adds them, the seam has leaked and the field must be removed, not moved. **Round 4
reverses `FR-119`'s exclusion for addresses and tax registrations only** (`RG-003`).
**Actions:** row View / Edit / Add role / End role / Deactivate. Toolbar Add / Import / Export.
**Mobile:** `mobile/src/screens/whbCounterparty/` — read-only list + detail, used by RF Receive to
confirm who shipped. `additionalFilters`: `roleCode` dropdown, `name` text.

---

### 2.4 Items and the catalogue

#### WS-023 · Items

`/warehouse/masters/items` · **Customer** · `whb_items` · `WAREHOUSE_ITEM` · `whb_items:*` ·
v1 · P1 · `FR-048` `FR-049` `FR-050` `FR-051` `FR-052` `FR-054` `FR-060` `FR-066` `FR-067` `FR-068`
`FR-069` `FR-070` `FR-076` `FR-078` · table `V500015` (★ **PNR-4** for `uk(owner_id, sku)`) ·
caches `dropdown.whbItem`.

| key | label | type | sort | vis | source |
|---|---|---|---|---|---|
| `itemCode` | Item code | string | Y | Y | `code` — globally unique, on every bin label, what every FK points at; **frozen once a ledger row exists** (§0.12) |
| `sku` | SKU | string | Y | Y | `sku` — unique only with `owner_id` (`FR-060`) |
| `ownerName` | Owner | string | Y | Y | `whb_owners.name` via `owner_id` |
| `name` | Description | string | Y | Y | `name` |
| `itemTypeCode` | Type | string | Y | Y | `item_type_code` → `whb_item_types` |
| `categoryName` | Category | string | Y | Y | `whb_item_categories.name` of the item's **current `STOCKING` row in `whb_item_category_assignments`** (`RG-005`; `whb_items.category_id` is dropped). `STOCKING` is the seeded system scheme. It is mandatory for a stocked item, and it is **the only scheme any resolver reads, at `occurred_at`**. A new assignment is frozen per §0.12; the category keys `whb_valuation_policies` |
| `baseUomCode` | Base UoM | string | Y | Y | `base_uom_code` — **immutable once a ledger row exists** (trigger `I-9`, `V500036`) |
| `lotControlMode` | Lot control | string | Y | Y | `lot_control_mode` NONE/OPTIONAL/REQUIRED — **frozen once stock is on hand**, by trigger (§0.12) |
| `serialControlMode` | Serial control | string | Y | Y | `serial_control_mode` NONE/RECEIPT/SHIP/FULL — **frozen once stock is on hand**, by trigger (§0.12) |
| `expiryPolicy` | Expiry | string | Y | N | `expiry_policy` |
| `isReceivable` | Receivable | boolean | Y | Y | the four independent status facts of `FR-050` — |
| `isIssuable` | Issuable | boolean | Y | Y | — never collapsed into one enum |
| `isOrderable` | Orderable | boolean | Y | N | — |
| `isCountable` | Countable | boolean | Y | N | — |
| `lifecycleStatus` | Lifecycle | string | Y | Y | NEW/ACTIVE/PHASE_OUT/OBSOLETE/BLOCKED |
| `taxClassificationCode` | HSN/SAC | string | Y | N | `tax_classification_code` — a **string, never an FK into a tax master** (`FR-066`) |
| `shelfLifeDays` | Shelf life | number | Y | N | `shelf_life_days` |
| `temperatureClass` | Temp class | string | Y | N | storage class (`FR-068`) |
| `unNumber` | UN no. | string | N | N | hazmat block (`FR-067`) |
| `isCatchWeight` | Catch weight | boolean | Y | N | `is_catch_weight` — v1 writes null on the movement |
| `onHandTotal` | On hand | number | N | Y | **backend-computed** roll-up from `whb_stock_positions`; never a frontend `.filter()` |
| `isActive` | Status | boolean | Y | Y | `is_active` |
| audit quartet + names | — | — | Y | N | — |

**Filters (cascading chain is the Customer pattern):** `ownerId` select → cascades `categoryId`
select → cascades `itemTypeCode` select · `sku` text · `itemCode` text · `name` text ·
`barcode` text (resolves through `whb_item_identifiers.normalised_value`) · `lotControlMode` select ·
`serialControlMode` select · `lifecycleStatus` select · `isReceivable` / `isIssuable` /
`isOrderable` / `isCountable` boolean · `abcClass` select (from `whb_item_site_settings`, requires
`warehouseId`) · `warehouseId` select (gates the site-scoped filters) · `taxClassificationCode` text ·
`isActive` boolean. **`expiryFrom`/`expiryTo` are NOT filters here** — expiry is a lot property; that
filter lives on WS-036 and WS-221.
**Export:** every visible column plus `description`, the whole hazmat block, `min_shelf_life_receipt_pct`,
`min_shelf_life_ship_pct`, `purchase_uom_code`, `sale_uom_code`, `gst_uqc_code` (from the UoM),
`abc_class`/`velocity_class`/`count_frequency_class` where a site is filtered, `createdByName`,
`updatedByName`, `createdAt`, `updatedAt`. `FR-400`: strict superset, ≤ 100,000 rows, and the export
must not hold a transaction open.
**Modals:** Add/Edit **multi-tab** (far more than six groups) — *Identity* (`owner`, `sku`, `code`,
`name`, `description`) · *Classification* (`item_type_code`, `lifecycle_status`, and a **category-per-scheme** child editor over
`whb_item_category_assignments`, `RG-005`: one current row per item × scheme, dated, the scheme being the
root of the category tree, and the `STOCKING` row mandatory for a stocked item) ·
*Units* (`base_uom_code`, `purchase_uom_code`, `sale_uom_code`; base UoM read-only once any ledger row
exists) · *Control* (lot / serial / expiry modes, shelf-life columns) · *Status facts* (the four
booleans) · *Tax & compliance* (`tax_classification_code`, hazmat block, temperature class) ·
*Attributes* (typed rows from `whb_item_attribute_values` against `whb_attribute_keys` — **never a
JSONB bag, and only registered keys are accepted**, `FR-076`/`FR-078`) · **Variant values** (a child
editor over `whb_item_variant_values`, one value per axis of the style's `whb_style_variant_axes`, in the
style's own axis order. Any number of axes is allowed, and the rows are deliberately undated. They replace
the three fixed slots, `RG-009`).
View = `ViewModalBase` with an `InfoSection` per tab plus `DataTable`s for identifiers, packaging
levels, UoM conversions, supersessions, category assignments (every scheme, with history), variant values
and on-hand-by-site.
**There is no cost field anywhere on this modal** (`FR-052`) — cost is a property of a receipt layer.
**Actions.** Row: View · Edit · **Block for receipt** / **Block for issue** (own modals, they set the
`FR-050` booleans and are the offered alternative when deactivation is refused) · Deactivate
(**blocked with `ITEM_HAS_STOCK` while on-hand is non-zero across any site, status or owner**,
`FR-051`) · Print item/shelf label · View supersession chain (routes to WS-030 filtered).
Toolbar: Add · **Import** (`ImportButton`, the Service Vehicle pattern — item master, identifiers,
packaging, supersessions and price files all land through `whb_import_batches`, `FR-418`) ·
Export · Grid config · Help.
**Mobile:** `mobile/src/screens/whbItem/` — list + detail + barcode scan-to-item, **read-only**. Item
creation is a desk task; an operator who scans an unknown barcode gets the `UNKNOWN_ITEM` path, not a
create form. `additionalFilters`: `ownerId`, `categoryId`, `itemTypeCode`, `lifecycleStatus` dropdowns
plus `sku` and `barcode` text. No date filter is required, which is fortunate — `ListHeader.tsx`
supports only `dropdown` and `text`.

#### WS-022 · Item Categories · WS-034 · Units of Measure — Department shape

| id | Table | Scope | Columns | Filters | Notes |
|---|---|---|---|---|---|
| WS-022 | `whb_item_categories` | `WAREHOUSE_ITEM_CATEGORY` | `code`, `name`, `parentCategoryName`, `defaultInspectionPlanName`, `defaultPutawayStrategyCode`, `isDualEligible`, `isActive`, audit | `parentCategoryId` select (self-cascade), `isDualEligible` boolean, `code`/`name` text, `isActive` | `is_dual_eligible` is the scope of the `D-9` ownership rule (WS-066). `default_inspection_plan_id` is a **generic reference**, not an FK — the plan lives in `warehouse`, and base may not FK into app |
| WS-034 | `whb_uoms` | `WAREHOUSE_UOM` | `code`, `name`, `uomClassCode`, `isBaseForClass`, `decimalPlaces`, **`uneceRec20Code`**, **`gstUqcCode`**, `isActive`, audit | `uomClassCode` select, `isBaseForClass` boolean, `code`/`name` text, `isActive` | The two code columns are not optional: without them every compliance payload and EDI mapping is hand-mapped and the IRP rejects invoices (`FR-056`) |

Both: **Department** reference, `dropdown.whbItemCategory` / `dropdown.whbUom`, export = visible +
audit names, single-tab modals, row View/Edit/Deactivate, toolbar Add/Import/Export.
**Mobile:** read-only picker lists at `screens/whbItemCategory` and `screens/whbUom`.

#### WS-024 … WS-031 · The item child masters

All eight are the **Customer** shape (each hangs off an item and its filter strip cascades from it),
all v1 · P1 except WS-028 (v1.1 · P3), all with export = visible + audit names, all with single-tab
add/edit modals and a `ViewModalBase` view, and all with row View/Edit/Delete-or-Deactivate and
toolbar Add/Import/Export/Grid config.

| id | Screen | Table | Scope | Grid columns | Filters (first is the cascade root) | FR |
|---|---|---|---|---|---|---|
| WS-024 | Item Identifiers & Barcodes | `whb_item_identifiers` | `WAREHOUSE_ITEM_IDENTIFIER` | `itemCode`, `itemName`, `identifierType`, `identifierValue`, `normalisedValue`, `uomCode`, `packQuantity`, `packagingLevelCode`, `counterpartyName`, `isPrimary`, `isActive` | `itemId` async typeahead → `identifierType` select → `counterpartyId` select · `identifierValue` text · `isPrimary` boolean | `FR-057` `FR-059` |
| WS-025 | Packaging Levels | `whb_item_packaging_levels` | `WAREHOUSE_ITEM_PACKAGING_LEVEL` | `itemCode`, `levelCode`, `parentLevelCode`, `quantityInParent`, `baseQuantity`, `uomCode`, `counterpartyName`, `priority`, `isDefault`, dims, `tareWeightKg` | `itemId` → `counterpartyId` → `levelCode` select · `isDefault` boolean | `FR-058` |
| WS-026 | UoM Conversions | `whb_item_uom_conversions` | `WAREHOUSE_ITEM_UOM_CONVERSION` | `itemCode`, `fromUomCode`, `toUomCode`, `conversionFactor`, `isActive` | `itemId` → `fromUomCode` select → `toUomCode` select | `FR-055` |
| WS-027 | Item × Site Settings | `whb_item_site_settings` | `WAREHOUSE_ITEM_SITE_SETTING` | `itemCode`, `warehouseName`, `reorderPoint`, `safetyStock`, `minStock`, `maxStock`, `reorderQuantity`, `leadTimeDays`, `abcClass`, `xyzClass`, `vedClass`, `fsnClass`, `hmlClass`, `velocityClass`, `countFrequencyClass`, **`negativeStockMode`** | `warehouseId` → `itemId` → `abcClass` select · `negativeStockMode` select · `belowReorderPoint` boolean (backend-computed) | `FR-053` `FR-070` `FR-014` `FR-252` |
| WS-028 | Item × Location Settings | `whb_item_location_settings` | `WAREHOUSE_ITEM_LOCATION_SETTING` | `itemCode`, `locationCode`, `minQuantity`, `maxQuantity`, `replenTriggerQuantity`, `isPickFace` | `warehouseId` → `locationId` → `itemId` · `isPickFace` boolean | `FR-053` `FR-255` |
| WS-029 | Item Supplier Sources | `whb_item_supplier_sources` | `WAREHOUSE_ITEM_SUPPLIER_SOURCE` | `itemCode`, `counterpartyName`, `supplierPartNumber`, `leadTimeDays`, `minOrderQuantity`, `orderMultiple`, `isPreferred`, `priorityRank`, `isAsnCapable`, `inspectionStrategy` | `counterpartyId` → `itemId` · `isPreferred` boolean · `supplierPartNumber` text | `FR-058` |
| WS-030 | Item Supersessions | `whb_item_supersessions` | `WAREHOUSE_ITEM_SUPERSESSION` | `predecessorItemCode`, `successorItemCode`, `supersessionType`, `chainSequence`, `quantityRatio`, `effectiveDate` (`dateOnly`), `endDate` (`dateOnly`), **`stockTreatment`**, `isBidirectional` | `predecessorItemId` async typeahead · `successorItemId` async typeahead · `supersessionType` select · `stockTreatment` select · `effectiveDateFrom`/`effectiveDateTo` **`dateOnly` pair** | `FR-071` `FR-072` `FR-073` |
| WS-031 | Item External References | `whb_item_external_refs` | `WAREHOUSE_ITEM_EXTERNAL_REF` | `itemCode` (**nullable — an `UNMAPPED` row is the point**), `sourceModule`, `externalEntity`, `externalId`, `externalCode`, **`mapStatus`**, `mappedByName`, `mappedAt`, `mapNote` | `sourceModule` select → `mapStatus` select · `externalId` text · `itemId` async typeahead · `mappedAtFrom`/`mappedAtTo` (`date` pair) | `FR-061` `FR-368` `D-9` |

**WS-026 is `Z-004`'s worst case and carries the freeze in §0.12.** `conversion_factor` is
**frozen once a ledger row exists for that from/to pair** — enforced by a trigger in `I-9`'s shape,
not by the service, because the importer and the port write this table too. A supplier that changes
its pack quantity is a **new conversion row with a new effective date**, never an edit of the old
one: `L-7`/`IRR-34` already freeze `conversion_factor_used` on the movement line, and an edited
master with a frozen line is exactly the failure `IRR-34` calls *undetectable, because both numbers
are internally consistent*. The refusal is `CONVERSION_IN_USE` with the count of lines that used it
and a link to them.

WS-030 carries two extra row actions with their own modals: **Resolve chain** (walks to the terminal
item, shows the full chain with cycle detection) and **Set stock treatment**
(`KEEP_SEPARATE` / `MERGE_DEMAND` / `MERGE_STOCK` — `MERGE_STOCK` posts a movement at the old part's
cost layers and is gated on `whb_item_supersessions:merge`).

WS-031 is **`D-9`'s obligation 1 and it is mandatory in v1.** Its statistics strip counts
`MAPPED` / `UNMAPPED` / `AMBIGUOUS` / `DELIBERATELY_SEPARATE`, and the `UNMAPPED` tile is the one that
makes accessories double-counting *detectable*. Row action **Map to item** opens an async typeahead
modal; **Mark deliberately separate** requires a note.

#### WS-032 / WS-033 · Variant axes and the style × variant matrix — **v2 screens on v1 schema**

`A-3` and `FR-443`/`FR-444`: the model (`whb_item_variant_axes`, `whb_item_variant_axis_values`, the
parent-style link on the item) is **v1 schema**, migration `V500014`; the **screens are v2**.
WS-032 is the Department shape over the axis master (`code`, `name`, `is_ordered`, `owning_module`)
with a child editor for values carrying **`sort_order`** — a size run must render and report in size
order, not alphabetically. WS-033 is a matrix editor, not a grid: styles down, axis values across,
one cell per variant SKU. **Mobile:** `none` for both — apparel matrix maintenance is a desk task.

**Not a grid, deliberately:** `whb_item_attribute_values` (a tab inside the item modal),
`whb_item_documents` (the attachment strip on the item view; `ON DELETE NO ACTION` to
platform `documents`, `FR-077`), `whb_item_variant_axis_values` (child editor on WS-032),
`whb_company_external_refs`, `whb_counterparty_external_refs`, `whb_location_external_refs`
(child `DataTable`s on their parents' view modals), `whb_kit_components` (child editor on WS-035),
`whb_counterparty_role_links` (child editor on WS-021),
`whb_allocation_strategy_rules` (the WS-048 rule editor),
`whb_alert_rule_conditions` / `whb_alert_rule_recipients` (tabs on WS-069),
`whb_audit_event_changes` (expansion row on WS-063),
`whb_import_batch_rows` (child grid inside the WS-065 batch detail),
`whb_transformation_inputs` / `whb_transformation_outputs` (the two panes of WS-039),
`whb_movement_line_attributes` (rendered on the movement line in WS-041),
`whb_cost_layer_consumptions` (drill-down from a WS-049 layer),
`whb_stock_movement_lines` (the lines pane of WS-041 — it has no independent grid because a line
without its header is not a fact), `whb_transport_details` (a polymorphic panel rendered on the
transfer, challan or issue that owns it).

#### WS-035 · Kit Definitions — v1.1 · P3

`whb_kit_definitions` · `WAREHOUSE_KIT_DEFINITION` · **Customer** · `FR-075`.
Columns `kitItemCode`, `kitType` (**PHANTOM vs STOCKED — different objects with the same BOM**),
`version`, `effectiveFrom`/`effectiveTo` (`dateOnly`), `estimatedAssemblyMinutes`, `componentCount`,
`isActive`. Filters `kitItemId` typeahead · `kitType` select · `effectiveFromFrom`/`To` `dateOnly`
pair · `isActive`. The modal's second tab is the BOM editor over `whb_kit_components`
(`component_item_id`, `quantity`, `uom_code`, `sort_order`, `is_optional`, `scrap_factor_percent`).
A virtual kit's availability is `MIN(component available ÷ required)` and is **computed on the
backend** and rendered as a read-only column — never a frontend calculation.
**Mobile:** `none` in v1.1 (kit maintenance is a desk task); the RF consumer is WS-233 RF Pack.

---

### 2.5 Lots, serials, LPNs and genealogy

All three masters are **Customer** shape, v1 · P1, table `V500018`, export = visible + audit names.

#### WS-036 · Lots

`whb_lots` · `WAREHOUSE_LOT` · `whb_lots:*` · `FR-094` `FR-095` `FR-096` `FR-320` ·
caches `dropdown.whbLot`.
**Columns:** `lotCode`, `itemCode`, `itemName`, `ownerName`, `supplierLot`, `partyNames` (each
`whb_lot_counterparties` row as *name (role)* — `RG-006`; `whb_lots.counterparty_id` is dropped),
`manufactureDate`, **`expiryDate`**, **`bestBeforeDate`**, **`useByDate`** (three separate columns
with different despatch rules — never one "expiry"), `retestDate`, `receiptDate`, `countryOfOrigin`,
`mrp`, `netContent` + `netContentUomCode`, `packMonthYear`, `parentLotCode`, `lotStatus`,
`onHandTotal` (backend roll-up), audit quartet + names.
**Filters:** `itemId` typeahead → `ownerId` select → `warehouseId` select ·
`lotCode` text · `supplierLot` text · **`expiryFrom` / `expiryTo` (`dateOnly` pair)** ·
`manufactureFrom` / `manufactureTo` (`dateOnly` pair) · `lotStatus` select · `countryOfOrigin` select ·
`expiringWithinDays` select (30/60/90 — a **dropdown**, so the mobile screen can carry the same
filter within `ListHeader`'s dropdown-only constraint).
**Actions:** View · **Hold lot** / **Release lot** (own modals, mandatory reason code). A lot hold is
**a `wh_holds` row with `hold_scope = LOT`** (`RJ-008`), and it holds the whole lot everywhere at once
**without moving anything** (`FR-096`). `lotStatus` carries lifecycle states set by jobs, such as
`EXPIRED`, and is never a hold · **Parties** (a child editor over `whb_lot_counterparties`: supplier,
`MANUFACTURER`, `PACKER`, `IMPORTER` and the other roles of registry 11 — the parties a Legal Metrology
declaration and a recall name) ·
Split / Merge (posts a `whb_transformations` row — genealogy is recorded **at the moment of
transformation**, never reconstructed, `FR-105`) · Print lot label · Trace (routes to WS-218).
**Mobile:** `screens/whbLot` — list, detail, hold/release. `expiringWithinDays` is the dropdown that
replaces the date range.

#### WS-037 · Serials

`whb_serials` · `WAREHOUSE_SERIAL` · `FR-097` `FR-098` `FR-099` `FR-106`.
**Columns:** `serialNumber`, `identifiers` (every `whb_serial_identifiers` row as *type: value*. A
dual-SIM handset carries two IMEIs. `RG-007`; `secondary_serial` is dropped), `itemCode`, `ownerName`, `lotCode`,
`currentLocationCode`, `currentStatusCode`, `currentLpnCode`, `soldToCounterpartyName`,
`warrantyStartDate`/`warrantyEndDate` (`dateOnly`), `lastMovementAt`, `linkedCoreSerial`.
**Filters:** `itemId` typeahead → `ownerId` → `warehouseId` → `currentLocationId` ·
`serialNumber` text · `currentStatusCode` select · `soldToCounterpartyId` typeahead ·
`warrantyEndFrom`/`warrantyEndTo` `dateOnly` pair · `inWarranty` boolean (backend-computed).
The three post-sale questions — **where is it now, who did we sell it to, is it in warranty** — are
answered by the view modal, which also lists the shipment that carried it. The view carries an
*Identifiers* child editor (`identifier_type` open, `uk(owner_id, identifier_type, identifier_value)`,
never global). The scan resolver reads it, so either IMEI finds the handset (`P1-02`), and the
`serialNumber` filter matches the serial **or any of its identifiers**.
`uk(owner_id, item_id, serial_number)` — **never globally unique**; the modal's duplicate check must
be scoped, and a site-level duplicate warning is shown where the scope permits the duplicate
(`FR-106`).
**Mobile:** `screens/whbSerial` — scan-to-serial detail. Read-only.

#### WS-038 · LPNs

`whb_lpns` · `WAREHOUSE_LPN` · `FR-100` `FR-101` `FR-064`.
**Columns:** `code`, `sscc`, `lpnType`, `parentLpnCode`, `ownerName`, `currentLocationCode`,
`status` (OPEN/CLOSED/SHIPPED/CONSUMED), **`receivedAt`** (the storage-anniversary anchor —
3PL storage billing is defined over it and cannot be computed for a past the ledger never recorded),
`isMixedItem`/`isMixedLot`/`isMixedOwner`, `grossWeightKg`, dims, `contentLineCount`.
**Filters:** `warehouseId` → `currentLocationId` · `ownerId` · `code` text · `sscc` text ·
`status` select · `lpnType` select · `receivedFrom`/`receivedTo` (`date` pair) · `isMixedOwner` boolean.
**Actions:** View (contents `DataTable`) · Move LPN (**one movement whose lines the service expands
from the LPN's current contents and stores** — never leaves them implicit, `FR-101`) · Close · Print
LPN label (internal Code-128 in v1; optional GS1-128 after v1.1 capability checks, template kind `LPN_LABEL`).
**Mobile:** `screens/whbLpn` — scan-to-LPN, contents, move. This is a genuine RF flow and it shares the
engine with WS-231 RF Move.

#### WS-039 · Genealogy Explorer

`/warehouse/ledger/genealogy` · `whb_transformations` · `WAREHOUSE_TRANSFORMATION` ·
`whb_transformations:view` · v1 · P1 · `FR-105` · table `V500035`.
A grid of transformations (`transformationType`, `occurredAt`, `warehouseName`, `performedByName`,
`inputCount`, `outputCount`, `movementId`) over a two-pane detail: inputs
(`whb_transformation_inputs`) left, outputs (`whb_transformation_outputs`) right, each showing item,
lot, serial and signed base quantity, each row linking to WS-041.
**Filters:** `warehouseId` → `transformationType` select · `itemId` typeahead · `lotId` typeahead ·
`serialId` typeahead · `occurredFrom`/`occurredTo` (`date` pair).
**Ledger-style: no created-by/updated-by column, and none in the export.**
**Mobile:** `none` — a recall investigation is a desk task with two panes and a print-out.

---

### 2.6 The ledger, positions and periods

#### WS-040 · Stock Movement Register — the product's report number one

`/warehouse/ledger/movements` · **Service Vehicle** (a posted document with transitions through their
own modals; **no edit path exists anywhere**) · `whb_stock_movements` · `WAREHOUSE_STOCK_MOVEMENT` ·
`whb_stock_movements:view|export` + verb permissions · v1 · **P0** ·
`FR-001` `FR-004` `FR-005` `FR-006` `FR-007` `FR-018` `FR-024` `FR-036` `FR-385` ·
table `V500030` (★★ **PNR-1 + PNR-2**) · caches: statistics `—` (filter-aware, `FR-395`), no dropdown.

| key | label | type | sort | vis | source |
|---|---|---|---|---|---|
| `sequenceNo` | Seq | number | Y | Y | `sequence_no` — gapless **per warehouse** |
| `movementTypeCode` | Type | string | Y | Y | `movement_type_code` |
| `warehouseName` | Site | string | Y | Y | `whb_warehouses.name` |
| `companyName` | Company | string | Y | N | `whb_companies.name` |
| `occurredAt` | Occurred | datetime | Y | Y | `occurred_at` — producer-supplied business time, **the partition key** |
| `recordedAt` | Recorded | datetime | Y | N | `recorded_at` — server clock |
| `postingDate` | Posting date | date | Y | Y | `posting_date` — the accounting/billing date |
| `sourceSystem` | Source | string | Y | Y | `source_system` |
| `sourceDocumentType` | Doc type | string | Y | Y | `source_document_type` |
| `sourceDocumentNo` | Doc no. | string | Y | Y | `source_document_no` — the human-readable number, and the reason the column exists |
| `sourceDocumentId` | Doc id | string | N | N | `source_document_id` — `VARCHAR`, deliberately not a UUID and never an FK |
| `reasonCodeName` | Reason | string | Y | Y | `whb_reason_codes.name` |
| `actorType` | Actor type | string | Y | Y | `actor_type` USER/DEVICE/INTEGRATION/SCHEDULED_JOB/IMPORT/SYSTEM_CORRECTION |
| `actorUserName` | Actor | string | Y | Y | platform user via `actor_user_id`, through the shared display helper |
| `deviceId` | Device | string | Y | N | `device_id` |
| `periodCode` | Period | string | Y | N | `whb_stock_periods.period_code` |
| `lineCount` | Lines | number | N | Y | count of `whb_stock_movement_lines` |
| `totalBaseQuantity` | Qty | number | N | Y | Σ positive `base_quantity`, backend-computed |
| `postingStatus` | Posting | string | Y | Y | `posting_status` NOT_APPLICABLE/PENDING/POSTED/REJECTED |
| `approvalStatus` | Approval | string | Y | N | `approval_status` |
| `isReversed` | Reversed | boolean | Y | Y | `is_reversed` |
| `reversalOfSequenceNo` | Reverses | number | N | N | resolved from `reversal_of_movement_id` |

**Filters:** `warehouseId` select → cascades `movementTypeCode` select → cascades `reasonCodeId`
select · `sourceSystem` select → cascades `sourceDocumentType` select · `sourceDocumentNo` text ·
`itemId` typeahead (joins to the line) · `lotId` typeahead · `serialNumber` text · `locationId`
select · `ownerId` select · `actorUserId` typeahead · `actorType` select ·
**`occurredFrom` / `occurredTo` (`date` pair)** · **`postingDateFrom` / `postingDateTo`
(`dateOnly` pair — `posting_date` is a SQL `DATE`)** · `postingStatus` select · `isReversed` boolean ·
`periodId` select.
`FR-036` is the indexed lineage query: `sourceSystem` + `sourceDocumentType` + `sourceDocumentId`
together hit `idx_whb_stock_movements_lineage` as a single seek. **All three keys must be in the
scope allowlist or a logistics module cannot find its own postings.**
**Export:** a **line-grain** export — one row per `whb_stock_movement_lines` row, carrying the header
columns plus `lineNo`, `ownerName`, `itemCode`, `locationCode`, `lotCode`, `serialNumber`, `lpnCode`,
`stockStatusCode`, `conditionCode`, `dutyStatus`, `quantity`, `uomCode`, `baseQuantity`,
`baseUomCode`, `conversionFactorUsed`, `unitCost`, `extendedCost`, `costBasis`,
`movingAverageAfter`, `hsnCode`, `sourceLineRef`, `isCounterSide`.
**Ledger-style: no `createdByName` / `updatedByName` column and none in the export** — the actor is
`actorUserName`, a business column, and adding audit columns here would emit a column no reader can
select (§0.5).
**Modals:** **no add and no edit modal exists.** The only write modals are **Reverse**
(mandatory reason code from `whb_reason_codes`, its own idempotency key, refuses to reverse a
reversal, refuses a `CLOSED` period, `FR-005`/`FR-035`) and **Approve** (for movement types flagged
`requires_approval`; `FR-408` — the approver may not be the actor). View is a route, not a modal:
WS-041.
**Actions.** Row: View (WS-041) · Reverse (`whb_stock_movements:reverse` **and** `is_reversed = false`
**and** the movement is not itself a reversal **and** the period is `OPEN` or an approved
`SOFT_CLOSED` override exists) · Approve / Reject (`whb_stock_movements:approve`,
`approval_status = PENDING`) · View source document (routes by `source_document_type` through the
**bean-collection display resolver**, with base's fallback renderer when no bean is registered,
`FR-357`) · View handover (WS-052, where `handover_id` is set).
Toolbar: Export · Grid config · Help · **Simulate** (`whb_stock_movements:simulate` — `FR-037`, runs
the whole validation chain and returns balance deltas and the error list **without writing**; it is
what support calls when a client says *"it says insufficient stock and there are 40 on the shelf"*).
**There is no Add button.** Movements arrive through the port (`POST /api/warehouse/movements`) or
through a document screen. A create form here would be a second writer, and `FR-436` allows exactly
one.
**Statistics strip (filter-aware, uncached):** movements today · pending approval · pending handover ·
rejected handovers · reversed today.
**Mobile:** `screens/whMovementRegister` — read-only list + detail, filtered to the operator's site.
`additionalFilters`: `warehouseId`, `movementTypeCode`, `postingStatus` dropdowns and a
`sourceDocumentNo` text input. **The date range does not survive** — `ListHeader` has no date filter —
so mobile carries an `occurredWithin` dropdown (Today / 7 days / 30 days) instead, resolved to a range
on the backend. That divergence is deliberate and is exactly what `D-13` means by *"apply the
equivalent behaviour within those constraints"*.

#### WS-041 · Movement Detail

`/warehouse/ledger/movements/[id]` · **no grid** · `whb_stock_movements:view` · v1 · P0.
Header panel (every column of WS-040 plus `idempotency_key`, `payload_hash`, `prev_payload_hash`,
`occurred_at_tz_offset`, `handover_id`, `notes`), then tabs: **Lines** (every column of the line,
including the typed `whb_movement_line_attributes` rendered inline — registered keys only, never a
JSONB blob) · **Reversal** (the mirror movement, or the movement this one reverses) ·
**Handover** (`whb_accounting_handovers` envelope, status, rejection code and message) ·
**Outbox** (the `whb_outbox` rows this movement emitted, with their delivery state) ·
**Cost** (the `whb_cost_layers` created and the `whb_cost_layer_consumptions` recorded).
Actions: Reverse · Approve · Print movement document (`FR-225`, template kind `MOVEMENT_DOCUMENT`).
**Mobile:** reachable as the detail of `screens/whMovementRegister`; the Cost tab is hidden on mobile
because cost is not an operator fact.

#### WS-042 · Stock Position Enquiry

`/warehouse/ledger/positions` · **Customer** · `whb_stock_positions` · `WAREHOUSE_STOCK_POSITION` ·
`whb_stock_positions:view|export` · v1 · **P0** · `FR-011` `FR-012` `FR-014` `FR-384` ·
table `V500031`.

**Two tabs, one grid identifier** (`FR-384`, and it follows the two-tab pattern a shipped module
already uses): **By item** (grouped to item × site) and **By location** (full nine-member grain).
The grain is the `L-5` key: `company_id, owner_id, item_id, location_id, lot_id, serial_id, lpn_id,
stock_status_code, duty_status`.

| key | label | type | sort | vis | source |
|---|---|---|---|---|---|
| `itemCode` / `itemName` | Item | string | Y | Y | `whb_items` |
| `ownerName` | Owner | string | Y | Y | `whb_owners.name` |
| `warehouseName` | Site | string | Y | Y | `warehouse_id` (denormalised on the position row) |
| `locationCode` | Location | string | Y | Y | `whb_locations.code` |
| `lotCode` | Lot | string | Y | Y | `whb_lots.lot_code` |
| `expiryDate` | Expiry | date | Y | Y | `whb_lots.expiry_date` |
| `serialNumber` | Serial | string | Y | N | `whb_serials.serial_number` |
| `lpnCode` | LPN | string | Y | N | `whb_lpns.code` |
| `stockStatusCode` | Status | string | Y | Y | `stock_status_code` — rendered as a badge whose **variant comes from `whb_stock_statuses.badge_variant`** (`FR-381`), with i18n falling back to the registry row's `name` |
| `dutyStatus` | Duty | string | Y | N | `duty_status` |
| `quantityOnHand` | On hand | number | Y | Y | `quantity_on_hand` |
| `quantityReserved` | Reserved | number | Y | Y | `quantity_reserved` |
| `quantityAvailable` | Available | number | Y | Y | `quantity_available` |
| `baseUomCode` | UoM | string | N | Y | `base_uom_code` |
| `unitCost` / `value` | Cost / Value | number | Y | N | joined from `whb_cost_layers`; **suppressed where `owner_type != OWN`** — non-own stock is never valued (`L-14`, `FR-112`) |
| `lastMovementAt` | Last move | datetime | Y | N | `last_movement_at` |
| `lastOutwardMovementAt` | Last outward | datetime | Y | N | `last_outward_movement_at` — **ageing is measured from this, not from receipt** |
| `lastCountDate` | Last count | date | Y | N | `last_count_date` |

**Filters:** `warehouseId` select → cascades `locationId` (subtree) → cascades `itemId` typeahead ·
`ownerId` select · `lotId` typeahead · `serialNumber` text · `lpnCode` text ·
`stockStatusCode` **multiselect** · `dutyStatus` select · `itemCategoryId` select ·
`nonZeroOnly` boolean (**default true** — the three partial indexes carry
`WHERE quantity_on_hand <> 0` and a live catalogue's position table is mostly zeros) ·
`hasAvailable` boolean · `expiryFrom`/`expiryTo` `dateOnly` pair · `expiringWithinDays` select ·
`agedOverDays` select.
**Export:** every column of the nine-member grain plus quantities, UoM, cost/value where permitted,
the three timestamps. **Ledger-style: no audit-name columns.**
**Actions.** Row: View movements for this grain (routes to WS-040 pre-filtered) · **Change status**
(own modal — a **balanced two-line movement at the same location** with a mandatory reason code, so
quarantine never requires a physical move, `FR-103`) · **Adjust** (routes to WS-089 pre-filled) ·
**Reserve** (`whb_reservations:create`) · Trace (WS-218).
Toolbar: Export · Grid config · **Rebuild check** (`whb_stock_positions:rebuild` — runs the `L-4`
comparison for the filtered scope and writes findings to WS-043; the nightly job does the same thing
unattended).
**Statistics strip (filter-aware, uncached):** distinct items · total on hand · total available ·
negative signed-balance rows (visible shortage); negative ATP rows (must be 0) · rows drifted at last rebuild.
**Mobile:** `screens/whStockEnquiry` list + the RF screen WS-236. Mobile carries `warehouseId`,
`ownerId`, `stockStatusCode` dropdowns and `itemCode`/`locationCode`/`lotCode` text inputs; the date
filters become an `expiringWithin` dropdown.

#### WS-043 · Position Drift Findings · WS-044 · Position Snapshots

| id | Table | Scope | Ref | Columns | Filters | Notes |
|---|---|---|---|---|---|---|
| WS-043 | `whb_position_drift_findings` | `WAREHOUSE_POSITION_DRIFT_FINDING` | Customer | `findingType` (POSITION_DRIFT/RESERVATION_DRIFT/ORPHANED_RESERVATION/NEGATIVE_AVAILABLE), the nine key members, `cachedQuantity`, `rebuiltQuantity`, `difference`, `ownerUserName`, `detectedAt`, `resolvedAt`, `resolutionNote` | `findingType` select · `warehouseId` → `itemId` · `ownerUserId` typeahead · `detectedFrom`/`To` `date` pair · `unresolvedOnly` boolean (default true) | `FR-012` `FR-163`. **A drift alert with no findings grid is an email nobody can act on.** Row actions: Assign · Resolve (note mandatory). Ledger-style, no audit columns |
| WS-044 | `whb_stock_position_snapshots` | `WAREHOUSE_POSITION_SNAPSHOT` | Customer | `snapshotDate` (`dateOnly`), the nine key members, `warehouseName`, `quantityOnHand`, `quantityReserved`, `unitCost`, `value`, `oldestReceiptDate`, `ageDays`, `isSuperseded` | `snapshotDateFrom`/`To` `dateOnly` pair · `warehouseId` → `itemId` · `ownerId` · `isSuperseded` boolean | `FR-289`, ★ **PNR-3**: ageing, days-on-hand, obsolescence and 3PL anniversary billing all read this table and **all of them begin on the day the job was switched on**. Read-only grid; the only action is Export |

**Mobile:** `none` for both — reconciliation and snapshot administration are controller tasks.

#### WS-045 · Stock Periods · WS-046 · Soft-close Overrides

WS-045 `/warehouse/ledger/periods` · **Service Vehicle** (a status ladder OPEN → SOFT_CLOSED →
CLOSED with transitions through their own modals) · `whb_stock_periods` · `WAREHOUSE_STOCK_PERIOD` ·
v1 · P0 · `FR-020` `FR-021` `FR-251` · table `V500019` · caches `dropdown.whbStockPeriod`.
Columns `periodCode`, `companyName`, `warehouseName` (**nullable = all sites**), `startDate`/`endDate`
(`dateOnly`), `status`, `closedByName`, `closedAt`, `reopenedByName`, `reopenedAt`, `movementCount`,
`pendingHandoverCount`. Filters `companyId` → `warehouseId` · `status` select ·
`startDateFrom`/`startDateTo` `dateOnly` pair.
Actions: **Soft close** · **Close** · **Reopen** — three modals, each gated on
`whb_stock_periods:close` / `:reopen`, each refusing while `pendingHandoverCount > 0`, each writing
a `whb_audit_events` row. **A movement whose `posting_date` falls in a `CLOSED` period is refused,
including a reversal** (`FR-020`); the close modal states the count it will lock.
WS-046 is the read-only audit of `whb_stock_period_overrides` — `periodCode`, `movementSequenceNo`,
`requestedByName`, `approvedByName`, `approvedAt`, `reasonCodeName`, `justification`; filters
`periodId` → `approvedBy` typeahead, `approvedAtFrom`/`To` `date` pair. No write actions.
**Mobile:** `none` for both — period close is a manager task performed at a desk with the
reconciliation report open.

---

### 2.7 Reservations, allocation and cost

| id | Screen | Table · Scope | Ref | Key columns | Filters | Actions | FR |
|---|---|---|---|---|---|---|---|
| WS-047 | Reservations | `whb_reservations` · `WAREHOUSE_RESERVATION` | SV | `ownerName`, `itemCode`, `locationCode`, `lotCode`, `serialNumber`, `lpnCode`, `stockStatusCode`, `quantity`, `baseQuantity`, **`holderSystem`**, **`holderDocumentType`**, **`holderDocumentId`**, **`holderLineNo`**, `reservationType` (SOFT/HARD), `priority`, **`expiresAt`**, `status`, `strategyCode`, `ruleSequence` | `warehouseId` → `itemId` · `ownerId` · `holderSystem` select → `holderDocumentType` select · `holderDocumentId` text · `reservationType` select · `status` select · `expiresFrom`/`expiresTo` `date` pair · `expiredOnly` boolean | **Release** (own modal, reason-coded — release exists in v1 even though the wave does not, `FR-169`) · **Extend expiry** · View holder document (through the display resolver) | `FR-166` `FR-167` `FR-169` `FR-170` `FR-171` `FR-173` |
| WS-048 | Allocation Strategies | `whb_allocation_strategies` · `WAREHOUSE_ALLOCATION_STRATEGY` | D | `code`, `name`, `owningModule`, `scopeType` (GLOBAL/WAREHOUSE/ITEM_CATEGORY/OWNER/CHANNEL), `scopeRef`, `priority`, `ruleCount`, `isActive` | `scopeType` select → `scopeRef` select · `isActive` | Edit opens a **rule editor** over `whb_allocation_strategy_rules`: `sequence`, `ordering_key` (**whitelisted**: FIFO/FEFO/LIFO/LOT_SPECIFIED/NEAREST_LOCATION/FEWEST_PICKS/ZONE_PRIORITY/HIGHEST_QUANTITY), `direction`, `filter_column`/`filter_operator`/`filter_value` — **all whitelisted, never a free expression language**. **Version history** (`RL-010`): a rule row referenced by any reservation is immutable (`I-24`), and an edit is copy-on-write with `version_no` + `supersedes_id`. The editor lists every version, so a reservation's recorded strategy and rule ids always resolve to the rules that actually ran | `FR-172` `FR-173` |
| WS-049 | Cost Layers | `whb_cost_layers` · `WAREHOUSE_COST_LAYER` | C | `itemCode`, `ownerName`, `warehouseName`, `lotCode`, `serialNumber`, `dutyStatus`, `layerDate` (`dateOnly`), `quantityIn`, **`quantityRemaining`**, `unitCost`, `layerValue`, `currencyCode`, `exchangeRate`, `receiptOccurredAt` | `warehouseId` → `itemId` · `ownerId` · `layerDateFrom`/`To` `dateOnly` pair · `hasRemaining` boolean (default true) · `currencyCode` select | View → drill-down `DataTable` of `whb_cost_layer_consumptions` (**which layer fed which issue** — what a credit note needs to restore the original layer). Read-only: a layer is created and consumed by the ledger, never edited | `FR-234` `FR-245` `OD-6` |
| WS-050 | Valuation Policies | `whb_valuation_policies` · `WAREHOUSE_VALUATION_POLICY` | D | `companyName`, `categoryName` (null = all), `warehouseName` (null = all), `method` (**AVCO/FIFO in v1; STANDARD v1.1; LIFO never**), `valuationGrain`, `effectiveFrom`/`effectiveTo` (`dateOnly`) | `companyId` → `categoryId` → `warehouseId` · `method` select · `effectiveFromFrom`/`To` | Add/Edit/End-date. The modal's method dropdown **must not offer LIFO** — prohibited under Ind AS 2 / IAS 2 (`OD-6`) | `FR-235` `FR-236` |
| WS-051 | GL Posting Rules | `whb_gl_posting_rules` · `WAREHOUSE_GL_POSTING_RULE` | D | `companyName`, `movementTypeCode`, `reasonCodeName`, `itemCategoryName`, `warehouseName`, `ownerTypeCode`, `specificity`, `debitAccountRef`, `creditAccountRef`, `effectiveFrom`/`effectiveTo` | each wildcard dimension as its own select · `effectiveFromFrom`/`To` | Add/Edit/End-date · **Test resolution** (a modal that takes a movement type + reason + category + site + owner type and shows which rule wins, most-specific-first) | `FR-246` |
| WS-052 | Accounting Handover Queue | `whb_accounting_handovers` · `WAREHOUSE_ACCOUNTING_HANDOVER` | SV | `movementSequenceNo`, `occurredAt`, `companyName`, `envelopeKind`, `idempotencyKey`, `status` (PENDING/SENT/POSTED/REJECTED), `attemptCount`, `lastAttemptAt`, `rejectionCode`, `rejectionMessage`, `externalDocumentRef` | `status` **multiselect** (default PENDING+REJECTED) · `companyId` · `envelopeKind` select · `occurredFrom`/`To` `date` pair · `rejectionCode` select | **Retry** (idempotent by construction) · **Void** (`whb_accounting_handovers:void`, own modal, approver ≠ requester, only for a reversed or `NOT_APPLICABLE` movement — `RJ-011`, §0.11) · **View payload** (read-only `TEXT`, never JSONB) · View movement (WS-041). **No edit.** `FR-232`: the rejected-handover queue is the answer to *"does the stock ledger tie to the GL"* | `FR-231` `FR-232` `FR-233` `FR-248` |

All six are `whb_<table>:view|create|edit|delete|export` except WS-049 and WS-052, which are
`:view|export` plus verb permissions (`whb_accounting_handovers:retry`). All are
ledger-style **except** WS-048, WS-050 and WS-051, which are configuration and **do** carry
`createdByName`/`updatedByName` in grid and export.
**Mobile:** WS-047 `screens/whbReservation` read-only (an operator needs to see who holds the stock
they cannot pick); WS-048 / WS-050 / WS-051 / WS-052 `none` (configuration and finance, desk only);
WS-049 `none` — cost is not an operator fact and `L-14` forbids showing a value for non-own stock.

---

### 2.8 The port, the outbox and ingestion

These six are the ones a support engineer opens at 2 a.m. They are grids over infrastructure, they are
all ledger-style, and every one of them is a **`FR-165` obligation: a threshold column with no
scheduled job that reads it is a defect at the moment it is merged.**

| id | Screen | Table · Scope | Ref | Key columns | Filters | Actions | FR |
|---|---|---|---|---|---|---|---|
| WS-053 | Port Monitor | `whb_inbound_messages` · `WAREHOUSE_INBOUND_MESSAGE` | SV | `sourceSystem`, `idempotencyKey`, `endpoint`, `payloadHash`, `status` (RECEIVED/PROCESSED/FAILED/DISCARDED), `errorCode`, `attemptCount`, `movementSequenceNo`, `receivedAt`, `processedAt`, `batchReference` | `sourceSystem` select → `status` select → `errorCode` select · `idempotencyKey` text · `receivedFrom`/`To` `date` pair | View payload · **Reprocess** (`whb_inbound_messages:reprocess`, idempotent by construction) | `FR-044` `FR-017` `FR-033` |
| WS-054 | Port Rejected Queue | **no grid of its own** — the same `whb_inbound_messages` grid and the same `WAREHOUSE_INBOUND_MESSAGE` scope, opened with `status IN (FAILED, DISCARDED)` defaulted | SV | as WS-053 plus `ageMinutes` and `alertRaised` | as WS-053, defaulted to failures · `ageOverMinutes` select | Reprocess · Bulk reprocess · Discard with reason | `FR-045` — **and its alert.** The queue is non-empty beyond a threshold ⇒ an alert fires; the threshold lives in `admin_settings` key `warehouse.port.rejected_queue_threshold` |
| WS-055 | Movement Batches | `whb_movement_batches` (+ `_results`) · `WAREHOUSE_MOVEMENT_BATCH` | C | `sourceSystem`, `batchReference`, `submittedByName`, `actorType`, `deviceId`, `totalCount`, `succeededCount`, `failedCount`, `receivedAt`, `completedAt` | `sourceSystem` · `deviceId` text · `hasFailures` boolean · `receivedFrom`/`To` | View → child grid of `whb_movement_batch_results` (`sequenceInBatch`, `idempotencyKey`, `outcome` CREATED/DUPLICATE/CONFLICT/REJECTED, `errorCode`) | `FR-034` — *"a scan gun syncing 400 movements after a shift must not lose 399 because one bin was renamed"* |
| WS-056 | Outbox Monitor | `whb_outbox` · `WAREHOUSE_OUTBOX` | C | **`cursor`**, `eventType`, `occurredAt`, `warehouseName`, `ownerName`, `subjectType`, `subjectId`, `payloadHash`, `movementSequenceNo` | `eventType` select · `warehouseId` · `ownerId` · `cursorFrom`/`cursorTo` number pair · `occurredFrom`/`To` `date` pair | View payload · Replay from cursor (`whb_outbox:replay`) | `FR-330` `FR-331` — gapless monotonic cursor; **base does not know its consumers** |
| WS-057 | Outbox Subscriptions | `whb_outbox_subscriptions` · `WAREHOUSE_OUTBOX_SUBSCRIPTION` | D | `subscriberCode`, `transport` (IN_PROCESS/HTTP), `endpointUrl`, `eventTypeFilter`, `ownerFilterName`, `lastDeliveredCursor`, `maxAttempts`, `backoffSeconds`, `isActive` | `transport` select · `isActive` · `subscriberCode` text | Add/Edit/Disable · **Reset cursor** (own modal, requires a typed confirmation). `secret_ref` is **masked at the edge** — the response carries `hasValue`, never the value | `FR-333` |
| WS-058 | Outbox Dead-letter | `whb_outbox_deliveries` · `WAREHOUSE_OUTBOX_DELIVERY` | SV | `subscriberCode`, `cursor`, `attemptNo`, `status` (OK/RETRY/DEAD), `httpStatus`, `errorDetail`, `attemptedAt` | `subscriptionId` select → `status` select (default DEAD) · `attemptedFrom`/`To` | **Retry** · **Retry all dead for subscription** | `FR-332` — the dead-letter grid and the replay path are named in the budget, not implied |

**Mobile:** `none` for all six. Stated per `FR-218`: these are support and integration surfaces; an
operator has no action on them and a handheld cannot render a payload.

---

### 2.9 Tasks, numbering, audit, import and the coexistence mitigations

| id | Screen | Table · Scope | Ref | Key columns | Filters | Actions | FR |
|---|---|---|---|---|---|---|---|
| WS-059 | Tasks | `whb_tasks` · `WAREHOUSE_TASK` | SV | `taskTypeCode`, `warehouseName`, `zoneLocationCode`, `ownerName`, `priority`, `status` (CREATED/ASSIGNED/STARTED/PAUSED/COMPLETED/CANCELLED/EXCEPTION), `assignedToName`, `assignedAt`, `startedAt`, `completedAt`, `pausedSeconds`, `deviceId`, `travelDistance`, `exceptionCode` | `warehouseId` → `zoneLocationId` → `taskTypeCode` · `status` **multiselect** · `assignedTo` typeahead · `priority` select · `createdFrom`/`To` `date` pair · `openOnly` boolean | Assign · Reassign · Cancel (reason-coded) · Complete-with-exception. **Tasks exist in v1 even though v1 has no RF gun** (`FR-212`): v1 creates one task per receipt line and per pick line and completes it in the same request, so `assigned_at`/`started_at`/`completed_at`/`paused_seconds` are populated from day one and labour reporting has a year of honest data before any standard is set (`FR-213`) | `FR-212` `FR-213` `FR-215` |
| WS-060 | Devices | `whb_devices` · `WAREHOUSE_DEVICE` | D | `deviceCode`, `deviceType`, `warehouseName`, `assignedToName`, `lastSeenAt`, `appVersion`, `isActive` | `warehouseId` · `deviceType` select · `isActive` · `lastSeenBefore` select (dropdown of ages, so mobile can carry it) | Add/Edit/Deactivate · Force sign-out | `FR-222` (v1.1) |
| WS-061 | Number Series | `whb_number_series` · `WAREHOUSE_NUMBER_SERIES` | D | `owningModule`, `seriesCode`, `companyName`, `warehouseName`, `branchName` (**`branches.branch_name`**), `prefix`, `suffix`, `padLength`, `currentValue`, `resetPolicy`, `lastResetAt`, `isGapless` | `owningModule` select → `seriesCode` select · `companyId` → `warehouseId` → `branchId` · `isGapless` | Add/Edit · **Preview next number** (reads, never issues). **A branch-scoped series (challan, transfer invoice) resolves `branch_id` to the issuing site's `REGISTERED` branch at the document date** (`D-14`, R22 §1.2.4 row 2). Warehouse-scoped series (GRN, pick, ship) are unaffected. A re-registration switches series from that instant and renumbers nothing (`FR-307`). `current_value` is **read-only in the modal** — editing a gapless counter by hand is how a duplicate document number is created | `FR-426` |
| WS-062 | Numbers Issued | `whb_number_series_issued` · `WAREHOUSE_NUMBER_ISSUED` | C | `seriesCode`, `issuedValue`, `formattedNumber`, `issuedToType`, `issuedToId`, `issuedAt`, `issuedByName` | `seriesId` select · `formattedNumber` text · `issuedFrom`/`To` `date` pair | View only — the table is append-only and has **no `updated_*` columns at all** | `FR-426` |
| WS-063 | Warehouse Audit Events | `whb_audit_events` · `WAREHOUSE_AUDIT_EVENT` | C | `sequenceNo`, `entityType`, `entityId`, `action`, `actorUserName`, `onBehalfOfActorName`, `occurredAt`, `summary`, `prevHash`, `payloadHash` | `entityType` select → `action` select · `actorUserId` typeahead · `occurredFrom`/`To` `date` pair · `entityId` text | View → expansion row of `whb_audit_event_changes` (field, old, new). **Append-only, hash-chained; ledger-style, no audit-name columns** — the actor *is* the content. `on_behalf_of_actor_id` lands in the **first** audit migration (`FR-409`) even though impersonation ships in v1.1, because sessions recorded before the column exists are indistinguishable from the customer's own actions | `FR-427` `FR-409` |
| WS-064 | Job Runs | `whb_job_runs` · `WAREHOUSE_JOB_RUN` | C | `jobCode`, `startedAt`, `finishedAt`, `status`, `recordsRead`, `recordsWritten`, `errorDetail`, `durationSeconds` | `jobCode` select · `status` select · `startedFrom`/`To` `date` pair · `failedOnly` boolean | View · **Run now** (`whb_job_runs:trigger`). **This grid is `FR-165`'s enforcement surface**: every dated obligation in the product ships with its job, and a job with no run record cannot be proved to have run. The expiry, snapshot, reservation-expiry, drift-rebuild, outbox-publish and alert jobs all appear here | `FR-165` |
| WS-065 | Import Batches | `whb_import_batches` · `WAREHOUSE_IMPORT_BATCH` | SV | `importKind`, `fileName`, `status`, `totalRows`, `validRows`, `errorRows`, **`isDryRun`**, `appliedAt`, `reversedAt`, `reversalOfBatchNumber`, `createdByName` | `importKind` select → `status` select · `isDryRun` boolean · `createdFrom`/`To` `date` pair | View → child grid `whb_import_batch_rows` (`rowNo`, `status`, `errorCode`, `errorDetail`, `createdEntityType`, `createdEntityId`) · **Validate** (dry run — **persists nothing**; this codebase has shipped the opposite defect and it produced duplicate rows on the subsequent real import) · **Apply** · **Reverse** | `FR-416` `FR-417` `FR-418` |
| WS-066 | Category Stocking Ownership | `whb_category_stocking_ownership` · `WAREHOUSE_CATEGORY_STOCKING_OWNERSHIP` | D | `companyName`, `categoryScope` (WAREHOUSE_CATEGORY/EXTERNAL_CATEGORY), `categoryRef`, **`stockingSystem`** (WAREHOUSE/ACCESSORIES — **no `CHECK`**), `effectiveFrom`/`effectiveTo` (`dateOnly`), `decidedByName`, `decisionNote` | `companyId` → `categoryScope` select → `categoryRef` select · `stockingSystem` select · `effectiveFromFrom`/`To` | Add/Edit/End-date. **`D-9` obligation 2, mandatory in v1**: for any item category exactly one of the two inventory systems is the stocking system of record, recorded as data, and WS-225 names every violation | `FR-369` |
| WS-067 | External Stock Snapshots | `whb_external_stock_snapshots` · `WAREHOUSE_EXTERNAL_STOCK_SNAPSHOT` | C | `sourceModule`, `externalId`, `asAtDate` (`dateOnly`), `quantityOnHand`, `loadedAt`, `loadedByName`, `importBatchNumber` | `sourceModule` select · `asAtFrom`/`asAtTo` `dateOnly` pair · `externalId` text | Load snapshot (through WS-065) · Export. **`warehouse` may not read `accessory_stock_levels`** — the quantity arrives by snapshot, which is what keeps the coupling test green | `FR-368` `D-9` |
| WS-068 | Channels | `whb_channels` · `WAREHOUSE_CHANNEL` | D | `code`, `name`, `channelKind` (MARKETPLACE/OWN_STORE/POS/B2B), `owningModule`, `isActive` | `channelKind` select · `isActive` | Add/Edit/Deactivate. **In base**, because the ledger's source lineage and the item alias both reference it | `FR-207` |
| WS-069 | Alert Rules | `whb_alert_rules` · `WAREHOUSE_ALERT_RULE` | C | `alertType`, `scopeType`, `scopeRef`, `urgency`, `notifyInApp`/`_email`/`_sms`/`_push`, `escalationMinutes`, `conditionCount`, `recipientCount`, `isActive` | `alertType` select → `scopeType` select → `scopeRef` · `urgency` select · `isActive` | Add/Edit with two child tabs: **conditions** (`subject_column` and `operator` **whitelisted**, `value_text`/`value_number` — this replaces the prior art's `trigger_conditions JSONB`) and **recipients** (ROLE/USER/GROUP rows replacing `recipient_roles` / `recipient_user_ids` arrays) | `FR-383` (v1.1) |
| WS-070 | Alert Events | `whb_alert_events` · `WAREHOUSE_ALERT_EVENT` | C | `alertRuleName`, `subjectType`, `subjectId`, `title`, `message`, `triggeredAt`, `acknowledgedAt`/`ByName`, `resolvedAt`/`ByName`, `isEscalated` | `alertRuleId` select · `unacknowledgedOnly` boolean (default true) · `triggeredFrom`/`To` `date` pair · `isEscalated` boolean | Acknowledge · Resolve (note) · View subject | (v1.1) |

**Mobile:** WS-059 → **WS-237 RF Task List** is the primary surface; the web grid is the supervisor's.
WS-060 `screens/whbDevice` read-only. WS-070 `screens/whbAlertEvent` list + acknowledge — an operator
must be able to acknowledge an alert from the floor. WS-061 … WS-068 and WS-069: `none`, all
configuration or support surfaces.

---

## 3. `warehouse` — `wh_`, band V510000–V519999

Grid config for every screen in this section is **one migration per grid in `V511020`–`V511199`**
(`DATA-MODEL.md` §7.3, WH-203). Permissions `V511000`, dependencies `V511001`, menus `V511010`.
Every statistics strip here is filter-aware and therefore **carries no cache name** (`FR-395`).

### 3.1 Inbound

#### WS-072 · Purchase Orders · WS-073 · Purchase Order Detail

`/warehouse/inbound/purchase-orders` · **Service Vehicle** · `wh_purchase_orders` ·
`WAREHOUSE_PURCHASE_ORDER` · `wh_purchase_orders:*` + verbs · v1 · P1 ·
`FR-122` `FR-123` `FR-125` `FR-130` `FR-132` `FR-143` `FR-260` `FR-344` · table `V510011` ·
caches `dropdown.whPurchaseOrder`.

| key | label | type | sort | vis | source |
|---|---|---|---|---|---|
| `poNumber` | PO no. | string | Y | Y | `po_number` |
| `supplierName` | Supplier | string | Y | Y | `whb_counterparties.name` via `supplier_counterparty_id` |
| `warehouseName` | Site | string | Y | Y | `whb_warehouses.name` |
| `ownerName` | Owner | string | Y | N | `whb_owners.name` |
| `orderDate` | Order date | date | Y | Y | `order_date` (`dateOnly`) |
| `expectedDeliveryDate` | Expected | date | Y | Y | `expected_delivery_date` (`dateOnly`) |
| `status` | Status | string | Y | Y | `status` DRAFT/SUBMITTED/… — badge variant from the registry |
| `orderSource` | Source | string | Y | Y | stock / daily / VOR / emergency / special order / back order / initial stock (`FR-260`) |
| `ownershipTransferPoint` | Title transfer | string | Y | N | v1 column (`FR-344`) |
| `currencyCode` | Currency | string | N | N | `currency_code` |
| `lineCount` | Lines | number | N | Y | count |
| `orderedQuantity` / `receivedQuantity` / `cancelledQuantity` | Ordered / Received / Cancelled | number | N | Y | Σ of the line counters — backend-computed |
| `orderValue` | Value | number | Y | Y | Σ `line_total` |
| `createdByName` / `updatedByName` / `createdAt` / `updatedAt` | audit | — | Y | N | this is a **document**, not a ledger row: audit columns are shown and exported |

**Filters:** `warehouseId` → cascades `supplierCounterpartyId` async typeahead → cascades `status`
**multiselect** · `ownerId` · `orderSource` select · `poNumber` text · `itemId` typeahead (joins the
line) · `orderDateFrom`/`orderDateTo` `dateOnly` pair · `expectedFrom`/`expectedTo` `dateOnly` pair ·
`overdueOnly` boolean (backend-computed) · `openOnly` boolean.
**Export:** header columns + per-line detail (`lineNo`, `itemCode`, `orderedQuantity`, `uomCode`,
`unitPrice`, `lineTotal`, `receivedQuantity`, `acceptedQuantity`, `rejectedQuantity`,
`cancelledQuantity`, `remainingQuantity`, `lineStatus`, `taxClassificationCode`,
`expectedDeliveryDate`) + `createdByName`, `updatedByName`.
**Modals:** Add/Edit **multi-tab** — *Header* · *Supplier & terms* · *Lines* (child editor;
**the UoM convertibility guard runs here and on the GRN**, `FR-143` — the prior system had it on the
PO and not on the receipt modal) · *Delivery* (`expected_delivery_date`, `ownership_transfer_point`) ·
*Notes*. Transitions are their **own** modals: **Submit** · **Approve** · **Cancel**
(`FR-132` — a cascade with a stock gate: refused if any GRN line has received stock, and the modal
says which) · **Close short** · **Reopen**.
**Actions.** Row: View (WS-073) · Edit (`:edit` **and** `status = DRAFT`) · Submit · Approve
(`wh_purchase_orders:approve`) · Cancel · Receive against (routes to WS-075 pre-filled) ·
Print PO. Toolbar: Add · Import · Export · Grid config · Help.
**Statistics strip:** open POs · overdue · fully received this month · value on order.
**WS-073, the detail, is the lifecycle command centre** (`FR-125`) — a route, not a modal, with
sub-tabs: **Lines** · **GRNs** · **QC results** · **Putaways** · **Invoices / three-way match** ·
**Returns** · **Exceptions** (reconciliation cases) · **Movements** (the ledger lineage query of
`FR-036`) · **Documents** · **Audit**. Every tab is a child grid with no independent
`gridIdentifier`.
**Mobile:** `screens/whPurchaseOrder` — list + detail, read-only, plus **Receive against** which
launches WS-229 RF Receive. `additionalFilters`: `warehouseId`, `status`, `supplierCounterpartyId`
dropdowns and `poNumber` text. The two date ranges are replaced by an `expectedWithin` dropdown.

#### WS-075 · Receiving Sessions · WS-076/WS-077 · Goods Receipts

`FR-124` makes the session **one truck against N POs × N ASNs × N GRNs**, with a **nullable supplier**
for a consolidator's load. `FR-127` is the rule the 72-table prior design missed: **receiving
verification always happens; quality inspection is optional** — they are different acts and different
screens.

| id | Table · Scope | Ref | Key columns | Filters | Actions |
|---|---|---|---|---|---|
| WS-075 | `wh_receiving_sessions` · `WAREHOUSE_RECEIVING_SESSION` | SV | `sessionNumber`, `warehouseName`, `dockDoorCode`, `supplierName` (nullable), `carrierName`, `vehicleNumber`, `driverName`, `sealNumberIn`, `sealNumberOut`, `gatePassRef`, `arrivedAt`, `startedAt`, `completedAt`, `status`, `documentCount`, `grnCount`, audit | `warehouseId` → `dockDoorId` → `status` · `supplierCounterpartyId` typeahead · `vehicleNumber` text · `arrivedFrom`/`To` `date` pair · `openOnly` boolean | Start · Attach PO/ASN (child editor over `wh_receiving_session_documents`) · Create GRN · **Record seals** (in and out, `FR-211`) · Complete · Cancel |
| WS-076 | `wh_goods_receipts` · `WAREHOUSE_GOODS_RECEIPT` | SV | `grnNumber`, `sessionNumber`, `poNumber`, `asnNumber`, `supplierName`, `warehouseName`, `ownerName`, `receivedByName`, `receivedAt`, **`isBlindReceipt`**, `receivingMode`, `grnTiming`, `status`, **`matchStatus`** (MATCHED/QTY_OVER/QTY_UNDER), `lineCount`, `receivedQuantity`, `acceptedQuantity`, `rejectedQuantity`, `freeQuantity`, `invoiceMatched`, audit | `warehouseId` → `supplierCounterpartyId` → `status` **multiselect** · `matchStatus` select · `isBlindReceipt` boolean · `poNumber` text · `grnNumber` text · `receivedFrom`/`To` `date` pair · `awaitingQc` boolean · `awaitingPutaway` boolean | View (WS-077) · **Post** · **Reverse** (WS-078) · **Inspect** (WS-080) · **Putaway** (WS-082) · Print GRN · Raise reconciliation case (WS-083) |

**WS-076's modals** are where the product's receiving character lives:
- **Blind receipt** — a first-class v1 flow requiring only item, quantity, UoM, owner, status and
  location (`FR-128`). Three of our own scenarios have no PO at the dock.
- **Receive line** — captures lot, expiry (`expiry_date_override`), serials, LPN, **free/scheme
  quantity** with its `scheme_reference` (`FR-141`), `conversion_factor_used` frozen on the line, and
  the received **stock status**, defaulted item → supplier → `AVAILABLE` (`FR-129`; hard-coding
  `AVAILABLE` is the defect).
- **Over/short** — governed by a tolerance on the item and a warehouse default, setting `match_status`
  (`FR-130`).
- **Post** — the only path that writes the ledger, through the single writer service.
There is **no edit modal for a posted GRN.** Correction is WS-078.
**Export (WS-076):** header + line grain (`lineNo`, `poLineNo`, `itemCode`, `expectedQuantity`,
`receivedQuantity`, `acceptedQuantity`, `rejectedQuantity`, `freeQuantity`, `schemeReference`,
`uomCode`, `conversionFactorUsed`, `lotCode`, `expiryDate`, `unitCost`, `stockStatusCode`,
`putawayLocationCode`, `crossDockReference`) + `createdByName`, `updatedByName`.
**WS-077** is the GRN detail route with tabs Lines · Serials · QC · Putaway · Movements ·
Landed costs · Reversals · Documents · Audit.
**Mobile:** WS-075 `screens/whReceivingSession` (start, attach, seals, complete — a real dock flow);
WS-076 `screens/whGoodsReceipt` list + detail, with receiving itself done in **WS-229 RF Receive**.
Mobile filters are dropdowns for `warehouseId`, `status`, `matchStatus` plus `grnNumber`/`poNumber`
text; `receivedFrom`/`To` become a `receivedWithin` dropdown.

#### WS-074 · ASNs · WS-078 · Receipt Reversals · WS-079 · Inspection Plans · WS-080 · Quality Inspections · WS-081 · Putaway Rules · WS-082 · Putaway Tasks · WS-083 · Reconciliation Cases · WS-084 · Supplier Returns · WS-085 · Dock Doors · WS-086 · Dock Appointments · WS-087 · Cross-dock · WS-088 · Three-way Match

| id | Table · Scope | Ref | Key columns | Filters | Actions & notes | FR |
|---|---|---|---|---|---|---|
| WS-074 | `wh_asns` · `WAREHOUSE_ASN` | SV | `asnNumber`, `supplierName`, `warehouseName`, `carrierName`, `trackingNumber`, `vehicleNumber`, `expectedArrivalAt`, `totalPallets`, `totalCases`, `totalWeightKg`, `status`, `lineCount` | `warehouseId` → `supplierCounterpartyId` → `status` · `asnNumber` text · `expectedFrom`/`To` `date` pair | Receive against · Cancel · child grid `wh_asn_lines` with its own child `wh_asn_line_serials` (**the normalised replacement for `serial_numbers JSONB`**) | `FR-136` `FR-383` |
| WS-078 | `wh_receipt_reversals` · `WAREHOUSE_RECEIPT_REVERSAL` | SV | `reversalNumber`, `grnNumber`, `reasonCodeName`, `requestedByName`, `approvedByName`, `approvedAt`, `status`, `reversalMovementSequenceNo` | `warehouseId` · `status` · `reasonCodeId` · `requestedFrom`/`To` | Request · **Approve** (`wh_receipt_reversals:approve`; approver ≠ requester, `FR-408`) · Post. **Reversal is an action, not a data fix**: it generates a `REVERSAL` movement, decrements the PO line's received quantity, and **leaves both documents visible** | `FR-131` |
| WS-079 | `wh_inspection_plans` · `WAREHOUSE_INSPECTION_PLAN` | C | `code`, `name`, `inspectionType` (FULL/SAMPLING/SKIP_LOT), `samplingPlan`, `sampleSizeFormula` (**whitelisted**), `aql`, `criterionCount`, `isActive` | `inspectionType` select · `isActive` · `code`/`name` text | Add/Edit with a child editor over `wh_inspection_plan_criteria` — **rows, not `inspection_criteria JSONB`** | `FR-133` `FR-383` |
| WS-080 | `wh_quality_inspections` · `WAREHOUSE_QUALITY_INSPECTION` | SV | `inspectionNumber`, `grnNumber`, `planName`, `inspectorName`, `startedAt`, `completedAt`, `result` (PASS/FAIL/PARTIAL), `dispositionCode`, `inspectedQuantity`, `passedQuantity`, `failedQuantity` | `warehouseId` → `planId` → `result` select · `inspectorId` typeahead · `dispositionCode` select · `startedFrom`/`To` | Start · Record results (child editors over `wh_quality_inspection_lines` and the typed `wh_quality_inspection_results`) · **Disposition** (release / reject / return to supplier / scrap — a **QA-role-gated** workflow, `wh_quality_inspections:disposition`) · Complete. **A header over lines, one inspection number per GRN** — not one row per GRN line | `FR-133` `FR-134` |
| WS-081 | `wh_putaway_rules` · `WAREHOUSE_PUTAWAY_RULE` | C | `code`, `name`, `warehouseName`, `sequence`, `scopeCategoryName`, `scopeItemCode`, `scopeStatusCode`, `strategy` (**whitelisted**: FIXED_LOCATION/NEAREST_EMPTY/ZONE_BY_VELOCITY/…), `isActive` | `warehouseId` → `strategy` select · `isActive` | Add/Edit/Reorder · **Test** (a modal: given item + quantity + status, which location does the rule chain suggest, and why). **Rules are data, evaluated in sequence** | `FR-135` |
| WS-082 | `wh_putaway_tasks` · `WAREHOUSE_PUTAWAY_TASK` | SV | `taskNumber` (from `whb_tasks`), `grnNumber`, `itemCode`, `quantity`, `lotCode`, `lpnCode`, `suggestedLocationCode`, `actualLocationCode`, `overrideReasonName`, `stagingLocationCode`, `ruleName`, `status`, `assignedToName` | `warehouseId` → `status` **multiselect** → `assignedTo` typeahead · `grnNumber` text · `itemId` typeahead · `hasOverride` boolean | Assign · Complete (own modal: scan location, capture override reason when the operator overrides the suggestion — **the reason is captured, never silently discarded**) · Cancel | `FR-135` |
| WS-083 | `wh_reconciliation_cases` · `WAREHOUSE_RECONCILIATION_CASE` | SV | `caseNumber`, `caseType` (QUANTITY/OVER_RECEIPT/INVOICE/ASN/INVENTORY), `warehouseName`, `subjectType`, `subjectId`, `status`, `ownerUserName`, `openedAt`, `resolvedAt`, `resolutionAction`, `resultingDocumentType`, `ageDays` | `warehouseId` → `caseType` select → `status` **multiselect** · `ownerUserId` typeahead · `openedFrom`/`To` · `openOnly` boolean (default true) | Assign · Add event (child `wh_reconciliation_case_events` timeline) · **Resolve** (the modal names the resulting document; **the case never moves stock itself**, `FR-138`) | `FR-138` |
| WS-084 | `wh_supplier_returns` · `WAREHOUSE_SUPPLIER_RETURN` | SV | `returnNumber`, `supplierName`, `warehouseName`, `ownerName`, `originGrnNumber`, `originLotCode`, `reasonCodeName`, `status` (DRAFT/APPROVED/PICKED/DISPATCHED/CLOSED/CANCELLED), `lineCount`, `totalValue`, `dispatchedAt`, audit | `warehouseId` → `supplierCounterpartyId` → `status` **multiselect** · `reasonCodeId` · `returnNumber` text · `createdFrom`/`To` | Approve · Close · Cancel · Print. **It runs through a demand order** (`RJ-003`). Approval creates a `VENDOR_RETURN` demand order, which reserves. Pick and staging follow the demand path (WS-099, WS-102), and dispatch is the shipment's `wh_shipments:dispatch` — **inventory is reduced only at dispatch** (`FR-139`). There is no supplier-return Pick or Dispatch of its own. A supplier return is not an RMA and does not share its ladder. **Cancel after `PICKED` is refused with `409 STAGED_STOCK`** until the stock is de-staged (`RJ-006`, §0.13). A return with `origin_grn_id` relieves that receipt's layer (`RJ-010`) | `FR-139` `FR-275` |
| WS-085 | `wh_dock_doors` · `WAREHOUSE_DOCK_DOOR` | C | `code`, `warehouseName`, `doorType` (INBOUND/OUTBOUND/BOTH), `locationCode`, `hasLeveler`, `hasShelter`, `hasTemperatureControl`, `status` | `warehouseId` → `doorType` select · `status` select | Add/Edit/Block. Child editor `wh_dock_door_vehicle_types` — **rows replacing `compatible_vehicles JSONB`** | `FR-092` `FR-383` |
| WS-086 | `wh_dock_appointments` · `WAREHOUSE_DOCK_APPOINTMENT` | SV | `appointmentNumber`, `dockDoorCode`, `appointmentType`, `scheduledStartAt`, `scheduledEndAt`, `slotDurationMinutes`, `referenceType`, `referenceId`, **`arrivedAt`**, **`dockedAt`**, **`departedAt`**, `noShow`, **`detentionMinutes`**, `status` | `warehouseId` → `dockDoorId` → `appointmentType` select · `status` **multiselect** · `scheduledFrom`/`To` `date` pair · `noShow` boolean | Book · Reschedule · **Check in** (`arrived_at` — the dock-to-stock clock starts here and cannot be backfilled) · Dock · Depart · Mark no-show. **Schema is v1 (`V510010`); the scheduling screen is v1.1** | `FR-092` `FR-392` |
| WS-087 | `wh_cross_dock_plans` · `WAREHOUSE_CROSS_DOCK_PLAN` | C | `grnNumber`, `grnLineNo`, `asnNumber`, `demandOrderNumber`, `itemCode`, `quantity`, `crossDockType` | `warehouseId` · `crossDockType` select · `grnNumber`/`orderNumber` text | v2. The **`cross_dock_reference` column is nullable on the v1 receipt line** so "which receipts were cross-docked" is answerable for the period before the feature shipped | `FR-137` |
| WS-088 | `wh_three_way_matches` · `WAREHOUSE_THREE_WAY_MATCH` | SV | `matchNumber`, `supplierName`, `supplierInvoiceRef`, `invoiceDate`, `invoiceTotal`, `status`, `varianceAmount`, `approvedByName` | `supplierCounterpartyId` → `status` · `invoiceDateFrom`/`To` `dateOnly` pair · `hasVariance` boolean | v2. Built on an **allocation junction** (`wh_three_way_match_allocations`: invoice line × GRN line × PO line with an allocated quantity **and** amount), never on a status column | `FR-140` |

**Mobile for §3.1:** `screens/whAsn` (read-only), `screens/whPutawayTask` → **WS-230 RF Putaway** is
the real surface, `screens/whQualityInspection` (record results — a genuine floor task),
`screens/whDockAppointment` (check-in only). `none`, with the reason, for WS-078 (approval, desk),
WS-079 (configuration), WS-081 (configuration), WS-083 (a decision centre with a timeline — needs a
desk), WS-087 and WS-088 (v2, finance and planning).

### 3.2 Inventory control

#### WS-089 · Stock Adjustments

`/warehouse/inventory/adjustments` · **Service Vehicle** · `wh_stock_adjustments` ·
`WAREHOUSE_STOCK_ADJUSTMENT` · v1 · P2 · `FR-145` `FR-146` `FR-164` `FR-408`.
**Columns:** `adjustmentNumber`, `warehouseName`, `ownerName`, `adjustmentType`
(POSITIVE/NEGATIVE/MIXED), `reasonCodeName`, `totalLines`, **`totalValueImpact`**,
`requiresApproval`, `approvedByName`, `approvedAt`, `status`, `postedMovementSequenceNo`, audit.
**Filters:** `warehouseId` → `ownerId` → `reasonCodeId` · `adjustmentType` select ·
`status` **multiselect** · `requiresApproval` boolean · `approvedBy` typeahead ·
`createdFrom`/`createdTo` `date` pair · `valueImpactMin`/`valueImpactMax` number pair.
**Actions:** Add (multi-tab modal: header + line editor over `wh_stock_adjustment_lines`, **one
`location_id`, one status, one owner per line** — the from/to shape is not re-homed) · Submit ·
**Approve / Reject** (`wh_stock_adjustments:approve`; **the threshold is expressed by value as well
as by quantity**, and the approver may not be the actor) · Post · Cancel · Print.
Every adjustment carries a **mandatory catalogue reason code**, and the reason's
`affects_demand_history` flag decides whether the movement inflates the reorder point (`FR-146`).
**Statistics strip:** open · awaiting approval · posted this period · net value impact this period.
**Mobile:** `screens/whStockAdjustment` — create and submit; **approval is desk-only** and the mobile
screen says so rather than hiding the button.

#### WS-090 · Transfer Orders

`/warehouse/inventory/transfers` · **Service Vehicle** · `wh_transfer_orders` ·
`WAREHOUSE_TRANSFER_ORDER` · v1 · P2 · `FR-147` `FR-148` `FR-149` `FR-244` `FR-305` `FR-306` `FR-344`
`FR-462`. Ladder: §0.11, round 4.
**Three legs, not two** — depart from the source location into a **per-transfer** in-transit location
**at the sending site**, arrive from it at the destination. `FR-085`: the transit location is per
reference, never one global `IN_TRANSIT` bucket, so two consignments on the road are separately
countable and separately ageable.
**Columns:** `transferNumber`, `transferType` (BIN_TO_BIN/INTRA_SITE/INTER_SITE), `companyName`,
`sourceWarehouseName`, `destinationWarehouseName`, `sourceBranchName` / `destinationBranchName`
(**`branches.branch_name`** — frozen at creation from each site's `REGISTERED` link, or the `SERVING`
branch for an issue to it, `FR-305`), **`isTaxableSupply`**, `transferPrice`, `valuationMethod`,
`ownershipTransferPoint`, `status`, `requestedByName`, `approvedByName`, `demandOrderNumber`,
`dispatchedAt`, `receivedAt`, `inTransitDays`, `lineCount`, audit. Lines carry `requestedQuantity` and
**`approvedQuantity`**, because part-approval is a line quantity, not a state.
**Filters:** `companyId` → `sourceWarehouseId` → `destinationWarehouseId` (**offered only within the
source's company** — a cross-company site is never listed, `RK-007`) · `transferType` select ·
`status` **multiselect** (the §0.11 vocabulary, `REQUESTED` included) · `isTaxableSupply` boolean ·
`dispatchedFrom`/`To` `date` pair · `inTransitOverDays` select (dropdown — it is also the mobile filter) ·
`transferNumber` text.
**Actions:** Add · **Request** (`wh_transfer_orders:request` creates the transfer in `REQUESTED`, and
**only a user scoped to the destination site** may do it, `FR-462`) · **Approve** / **Reject**
(`:approve` / `:reject`, own modals). **The approver is scoped to the source site** and is not the
requester (`FR-408`). Approve may part-approve per line, and the refused remainder is written to WS-096 as
`TRANSFER_REQUEST`. Approval creates the `TRANSFER` demand order, which reserves (`RJ-003`) ·
**Dispatch** (the transfer's shipment, `wh_shipments:dispatch` on WS-105, posts `TRANSFER_DEPART` into
the transit location) · **Receive** (`:receive` posts the arrive movement. It is authorised against that
transfer's transit location regardless of site scope) · **Report variance** (`:report_variance`, the
in-transit residue) · **Cancel** (`:cancel`; **in transit it posts `TRANSFER_RETURN`** from the transit
location back to the source, with a mandatory reason code) · **Generate delivery challan**
(`whin_delivery_challans:create`, only when `warehouse-india` is installed — the button is registered
by the India module, not by `warehouse`) · Print.
**There is no Pick action.** Reservation, pick and staging are the demand path (WS-099, WS-102), because
there is exactly one reservation path (`RJ-003`). A cross-company transfer reaching the API is
`422 CROSS_COMPANY_TRANSFER` (§0.13).
**The transfer carries two numbers** (`FR-244`): a **transfer price** (the tax document) and a
**cost** (what follows the goods).
**Mobile:** `screens/whTransferOrder` — dispatch and receive are genuine floor tasks and both are on
the handheld; creation is available, and so is **Request**, because the counter clerk at the destination
raises it (`RK-001`). Approve / Reject and the challan action are not.

#### WS-091 … WS-098 · Holds, counting and the exception queues

| id | Table · Scope | Ref | Key columns | Filters | Actions & notes | FR |
|---|---|---|---|---|---|---|
| WS-091 | `wh_hold_types` · `WAREHOUSE_HOLD_TYPE` | D | `code`, `name`, `owningModule`, `holdScope` (ORDER/LOT/LOCATION/ITEM/SHIPMENT), `blocksAllocation`, `blocksPick`, `blocksShip`, `requiresReason`, `releasePermission`, `isActive` | `holdScope` select · `blocksAllocation`/`blocksPick`/`blocksShip` booleans · `isActive` | `D-10`'s twelfth registry, **living in the application** because holds are an application concern. Same catalogue block as §2.1 | `FR-151` |
| WS-092 | `wh_holds` · `WAREHOUSE_HOLD` | SV | `holdNumber`, `holdTypeCode`, `subjectType`, `subjectId`, `subjectLabel` (through the display resolver), `reasonCodeName`, `placedByName`, `placedAt`, `releasedByName`, `releasedAt`, `releaseReasonName`, `note` | `holdTypeCode` select → `subjectType` select · `activeOnly` boolean (default true) · `placedBy` typeahead · `placedFrom`/`To` `date` pair | Place · **Release** (gated on the hold type's `release_permission`) · **Mass hold / release** by lot, LPN, location, supplier, item or date range — its own modal, and **each posts a balanced status-change movement** (`FR-152`). **Two holds at once is the normal case**, so this is a record with a release audit, never a status column | `FR-151` `FR-152` |
| WS-093 | `wh_count_programs` · `WAREHOUSE_COUNT_PROGRAM` | C | `code`, `name`, `warehouseName`, `programType` (ABC/RANDOM/FULL/ZONE/ITEM/DISCREPANCY_TRIGGERED), `frequencyDays`, `scheduleCron`, `nextScheduledDate` (`dateOnly`), `isBlindCount`, `recountThresholdPct`, `approvalThresholdPct`, `scopeCount`, `isActive` | `warehouseId` → `programType` select · `isBlindCount` boolean · `nextScheduledFrom`/`To` `dateOnly` pair · `isActive` | Add/Edit with a child editor over `wh_count_program_scopes` — **rows replacing `scope_*_ids JSONB`** · **Generate counts now**. **`programType = ABC` is labelled *"uses manually maintained classes"* until v1.1**, when `P1-03`'s v1.1 increment, the simple recompute (`FR-463`), fills the class. A v1 screen must not imply a computation that does not exist (`RK-003`) | `FR-156` `FR-383` |
| WS-094 | `wh_counts` · `WAREHOUSE_COUNT` | SV | `countNumber`, `programName`, `warehouseName`, `countType` (CYCLE/FULL_PHYSICAL/ZERO_STOCK/SPOT), `status`, `isBlind`, `freezeStartedAt`, `freezeEndedAt`, `bookSnapshotTakenAt`, `lineCount`, `countedLines`, `varianceLines`, `varianceValue`, `approvedByName`, `approvedAt`, `postedAt`, audit | `warehouseId` → `programId` → `countType` select · `status` **multiselect** · `isBlind` boolean · `hasVariance` boolean · `createdFrom`/`To` `date` pair | Generate · **Freeze** · Assign zones (child `wh_count_zone_assignments`) · Enter counts (WS-095) · Recount · **Approve** (`wh_counts:approve`; **the counter may not approve their own count**, `FR-408`) · **Post** · Cancel · Print count sheet. **A count is a document that proposes an adjustment and never writes on-hand**; the book quantity is frozen at count start and stored even when the count is blind | `FR-153` `FR-154` `FR-155` `FR-157` `FR-159` |
| WS-095 | count entry route (no grid) | — | the `wh_count_lines` editor: `itemCode`, `locationCode`, `lotCode`, `serialNumber`, `lpnCode`, `ownerName`, `stockStatusCode`, `dutyStatus`, **`countSnapshotQuantity`** (hidden when `is_blind`), `countedQuantity`, `varianceQuantity`, `variancePct`, `unitCost`, `varianceValue`, `isWithinTolerance`, `recountSequence`, `countedByName` | — | **Tolerance gates posting** by quantity percentage **and** by value: lines inside tolerance post automatically, lines outside route to approval. Posting emits **one movement per non-zero variance line**, carrying the count's reason code | `FR-155` `FR-159` |
| WS-096 | `wh_insufficient_stock_log` · `WAREHOUSE_INSUFFICIENT_STOCK` | C | `warehouseName`, `itemCode`, `ownerName`, `requestedQuantity`, `availableQuantity`, `sourceType`, `sourceId`, `actorUserName`, `occurredAt`, `policyApplied` (BLOCK/WARN/ALLOW), `isLostSale` | `warehouseId` → `itemId` · `policyApplied` select · `sourceType` select · `isLostSale` boolean · `occurredFrom`/`To` `date` pair | Read-only + Export. **One table because they are the same event seen twice**: every `WARN`/`ALLOW` breach and every lost sale captured at the counter or the job-issue screen. Ledger-style, no audit columns | `FR-015` `FR-257` |
| WS-097 | `wh_blocked_movements` · `WAREHOUSE_BLOCKED_MOVEMENT` | SV | `warehouseName`, `attemptedMovementTypeCode`, `rejectionCode`, `rejectionDetail`, `actorUserName`, `deviceId`, `occurredAt`, `resolvedAt`, `resolutionAction`, `ageMinutes` | `warehouseId` → `rejectionCode` select · `unresolvedOnly` boolean (default true) · `actorUserId` typeahead · `occurredFrom`/`To` | View attempted payload (`TEXT`) · **Force with approval** (`wh_blocked_movements:force`, mandatory reason + approver) · Resolve · Discard. **A physical move the system rejected is a first-class object** — refusing the transaction does not un-move the goods, so the queue holds the goods in `PENDING_RESOLUTION` and routes to a supervisor | `FR-028` |
| WS-098 | `wh_reconciliation_exceptions` · `WAREHOUSE_RECONCILIATION_EXCEPTION` | SV | `exceptionType`, `warehouseName`, `subjectKeyText`, `detectedAt`, `ownerUserName`, `ageDays`, `status`, `resolvedAt`, `resolutionNote` | `exceptionType` select → `status` select · `warehouseId` · `ownerUserId` typeahead · `ageOverDays` select · `detectedFrom`/`To` | Assign · Resolve. Exposes ledger-vs-position drift, position-vs-allocation drift and orphaned reservations **with an owner and an ageing clock** — an exception nobody owns is an exception nobody clears | `FR-163` |

**Mobile:** WS-092 `screens/whHold` (place and release from the floor); WS-094/WS-095 → **WS-235 RF
Cycle Count** is the entry surface and the web grid is the controller's; WS-097
`screens/whBlockedMovement` — the operator who was refused must be able to see why and raise the
force request. `none` for WS-091 (registry), WS-093 (programme configuration), WS-096 and WS-098
(controller reports).

#### WS-241 · Approval Levels — v2 · P5

`/warehouse/inventory/approval-levels` · **Department** · `wh_approval_levels` · `WAREHOUSE_APPROVAL_LEVEL` ·
`wh_approval_levels:*` · v2 · P5 · `FR-466` · table `V510222`, grid config `V511180`, permissions,
dependencies and menu `V511210` + `V511240` · caches: statistics `—` (filter-aware, `FR-395`), no dropdown.

**Ordered, typed rows, not a workflow engine** (`RK-008`). A level is keyed by document kind × value
band × sequence and names the permission its approver must hold. The existing approve actions read it:
`wh_purchase_orders:approve` (WS-072), `wh_stock_adjustments:approve` (WS-089), `wh_transfer_orders:approve`
(WS-090) and the other approve verbs of §10.2. A document in a band needs every level of that band, in
sequence. **`FR-408` applies at every level, and no user approves one document twice.** The single-step
`approved_by` columns stay, holding the last approver.
**Columns:** `documentKind` · `valueBandFrom` · `valueBandTo` (null = no upper bound) · `sequence` ·
`permissionName` (the permission an approver at this level must hold) · `isActive` · audit quartet + names.
**Filters:** `documentKind` select · `permissionName` select · `isActive` boolean.
**Export:** visible + both audit names.
**Modals:** single-tab add/edit; view = `ViewModalBase` with a `StatusCard` and a `DataTable` of the
document kind's whole ladder, in band and sequence order.
**Actions:** row View / Edit / Deactivate. Toolbar Add / Export / Grid config / Help.
**Mobile:** `none` — approval configuration is a desk task. Approving a document from a handheld is
governed by that document's own mobile block. Stated per `FR-218`.

---

### 3.3 Outbound

#### WS-099 · Demand Orders · WS-100 · Demand Order Detail

`/warehouse/outbound/orders` · **Service Vehicle** · `wh_demand_orders` · `WAREHOUSE_DEMAND_ORDER` ·
v1 · P2 · `FR-177` `FR-178` `FR-180` `FR-182` `FR-185` `FR-187` `FR-189` · table per §7.3 ·
caches `dropdown.whDemandOrder`.

**One demand model for every demand type** — sales, transfer, work order, replenishment, VAS, sample,
scrap, job issue. There is no second order table anywhere in the product.

| key | label | type | sort | vis | source |
|---|---|---|---|---|---|
| `orderNumber` | Order no. | string | Y | Y | `order_number` |
| `demandType` | Demand type | string | Y | Y | `demand_type` |
| `warehouseName` | Site | string | Y | Y | — |
| `ownerName` | Owner | string | Y | Y | — |
| `customerName` | Customer | string | Y | Y | `whb_counterparties.name` |
| `channelName` / `channelAccountCode` | Channel | string | Y | N | `whb_channels` / `wh_channel_accounts` |
| `externalOrderRef` | External ref | string | Y | N | `external_order_ref` |
| `orderDate` | Order date | date | Y | Y | `dateOnly` |
| `priority` | Priority | number | Y | Y | `priority` |
| `promisedShipAt` | Promised ship | datetime | Y | Y | `promised_ship_at` — a **v1 column**; every operational KPI is computed from it |
| `promisedDeliverAt` | Promised deliver | datetime | Y | N | `promised_deliver_at` |
| `status` | Status | string | Y | Y | badge variant from the registry |
| `holdCount` | Holds | number | N | Y | open `wh_holds` on the order |
| `orderedQuantity` `allocatedQuantity` `pickedQuantity` `shippedQuantity` `cancelledQuantity` `backorderedQuantity` | the **six quantity columns** | number | N | Y | Σ of `wh_demand_order_lines` — deriving backorder from two of them makes short-ship and cancellation indistinguishable |
| `createdByName` / `updatedByName` / `createdAt` / `updatedAt` | audit | — | Y | N | shown and exported |

**Filters:** `warehouseId` → cascades `ownerId` → cascades `demandType` select ·
`customerCounterpartyId` async typeahead (**scope before cap** — scope to the owner first, then cap
the result set) · `channelId` select → `channelAccountId` select · `status` **multiselect** ·
`priority` select · `orderNumber` text · `externalOrderRef` text · `itemId` typeahead ·
`orderDateFrom`/`orderDateTo` `dateOnly` pair · `promisedShipFrom`/`promisedShipTo` `date` pair ·
`onHoldOnly` boolean · `backorderedOnly` boolean · `lateOnly` boolean (backend-computed against
`promised_ship_at`).
**Export:** header + line grain (`lineNo`, `itemCode`, `uomCode`, the six quantities, `unitPrice`,
`lotId`/`serialId` where specified, `lineStatus`, `shortPickReason`) + audit names.
**Modals:** Add/Edit multi-tab (*Header* · *Customer & channel* · *Lines* · *Promise & priority* ·
*Ship-to* · *Notes*), plus transition modals: **Allocate** · **Release** (`FR-169`/`FR-187` — the
Release action exists in v1 even though the wave does not; it is the moment stock leaves the
available pool) · **Place hold** / **Release hold** (per-type `blocks_allocation` / `blocks_pick`
flags decide the effect) · **Short pick** (records the shortfall against an **exception code**, never
a silently reduced quantity, `FR-185`) · **Cancel** (de-allocation is **deterministic and
reason-coded** and cancels un-started tasks, `FR-171`).
**Actions.** Row: View (WS-100) · Edit (`:edit`, and after release only where the seeded
`wh_order_edit_rules` matrix allows it — WS-128) · Allocate · Release · Hold · Cancel · Pick (WS-102)
· Pack (WS-103) · Ship (WS-105) · Print pick list · Print packing slip.
Toolbar: Add · Import · Export · Grid config · Help.
**Statistics strip:** open · allocated · picking · packed · shipped today · late against promise ·
on hold.
**WS-100 detail tabs:** Lines · Allocations (the `whb_reservations` holding this order) · Tasks ·
Shipments · Cartons · Holds · Movements · Documents · Audit.
**Mobile:** `screens/whDemandOrder` list + detail, with picking through **WS-232 RF Pick**.
Mobile filters: `warehouseId`, `ownerId`, `demandType`, `status`, `priority` dropdowns and
`orderNumber` text; the two date ranges become a `promisedWithin` dropdown.

#### WS-101 … WS-106 · Wave, pick, pack, carton, ship

| id | Table · Scope | Ref | Key columns | Filters | Actions & notes | FR |
|---|---|---|---|---|---|---|
| WS-101 | `wh_waves` · `WAREHOUSE_WAVE` | SV | `waveNumber`, `warehouseName`, `waveType`, `status`, `shipByAt`, `totalOrders`, `totalPickLines`, `totalUnits`, `releasedAt`, `pickStartedAt`, `pickCompletedAt`, `packCompletedAt`, `shippedAt` | `warehouseId` → `waveType` select → `status` **multiselect** · `shipByFrom`/`To` `date` pair | v1.1. Build · **Release** · Cancel. Criteria are rows in `wh_wave_criteria` with **whitelisted** `criterion_column` and `operator` — replacing `grouping_criteria JSONB`. Member orders in `wh_wave_orders`. **v1 ships the Release action on the demand header and says the wave is deferred; that is a stated deferral, not silence** | `FR-187` `FR-383` |
| WS-102 | `wh_pick_tasks` · `WAREHOUSE_PICK_TASK` | SV | `taskNumber`, `orderNumber`, `waveNumber`, `pickMethod` (DISCRETE/BATCH/CLUSTER/ZONE), `itemCode`, `lotCode`, `serialNumber`, `sourceLocationCode`, `requestedQuantity`, `pickedQuantity`, `status`, `assignedToName`, `startedAt`, `completedAt`, `exceptionCode` | `warehouseId` → `zoneLocationId` → `status` **multiselect** · `assignedTo` typeahead · `pickMethod` select · `waveId` select · `orderNumber` text · `shortPickOnly` boolean | Assign · Complete · **Short pick** (exception-coded, raises the emergency-replenishment trigger) · Cancel. **v1 is discrete pick only** and the deferral of batch (v1.1) and cluster/zone/pick-and-pass (v2) is stated here rather than discovered | `FR-186` `FR-185` |
| WS-103 | `wh_pack_sessions` · `WAREHOUSE_PACK_SESSION` | SV | `sessionNumber`, `orderNumber`, `shipmentNumber`, `warehouseName`, `packerName`, `stationLocationCode`, `startedAt`, `completedAt`, `status`, `activeCartonNumber`, `cartonCount` | `warehouseId` → `status` · `packerUserId` typeahead · `startedFrom`/`To` | v1.1. Start (**auto-creates the first carton**) · Add carton · Close carton · Complete. Designed as an **operator flow, not as arithmetic**: one active carton at a time | `FR-190` |
| WS-104 | `wh_cartons` · `WAREHOUSE_CARTON` | C | `cartonNumber`, `shipmentNumber`, `packSessionNumber`, `lpnCode`, `cartonType`, `weightKg`, `expectedWeightKg`, **`scaleWeightKg`**, dims, `volumetricWeightKg`, `trackingNumber`, `labelPrintedAt`, `contentLineCount` | `warehouseId` → `shipmentId` · `cartonNumber` text · `trackingNumber` text · `weightVarianceOver` number | View contents (`wh_carton_contents`, **to the serial**) · View evidence (`wh_carton_evidence` — the **pack photo and scale reading captured at pack time in v1**, because the evidence for a carrier weight dispute cannot be created afterwards) · Print carton label · Reprint | `FR-191` `FR-206` |
| WS-105 | `wh_shipments` · `WAREHOUSE_SHIPMENT` | SV | `shipmentNumber`, `warehouseName`, `ownerName`, `carrierName`, `carrierServiceCode`, `carrierAccountCode`, `trackingNumber`, `dockDoorCode`, ship-to block, `totalCartons`, `totalWeightKg`, `totalVolumeCc`, `shippingCost`, `status`, `dispatchedAt`, `deliveredAt`, audit | `warehouseId` → `carrierId` → `carrierServiceCode` select · `ownerId` · `status` **multiselect** · `trackingNumber` text · `shipmentNumber` text · `dispatchedFrom`/`To` `date` pair · `undispatchedOnly` boolean | Add · Assign carrier · Rate shop (v2) · **Dispatch** — and **dispatch is the inventory-relief event and it is the only one** (`FR-189`); pick moves stock to a real, countable staging location and ship confirm relieves it from staging to the virtual customer location · Print shipping label · Add to manifest · Cancel | `FR-179` `FR-188` `FR-189` |
| WS-106 | shipment detail route (no grid) | — | tabs: Orders (`wh_shipment_orders` — **many orders per shipment, many shipments per order**; the cardinality is a one-way door) · Cartons · Labels · Consignment · Tracking · Movements · Documents · Audit | — | — | `FR-179` `FR-193` |

#### WS-107 … WS-130 · Carrier, channel and transport masters

All are `warehouse` tables, all export = visible + audit names except the log-style ones named in
§0.5, and all take the reference given in the index.

| id | Table · Scope | Key columns | Filters | Notes | FR |
|---|---|---|---|---|---|
| WS-107 | `wh_carriers` · `WAREHOUSE_CARRIER` | `code`, `name`, `counterpartyName`, `carrierType`, `trackingUrlTemplate`, `apiEnabled`, `isActive` | `carrierType` select · `apiEnabled` · `isActive` | One of the **five relocatable objects** — referenced by stable code, never by an FK from a relocatable table | `FR-196` `FR-199` |
| WS-108 | `wh_carrier_services` · `WAREHOUSE_CARRIER_SERVICE` | `carrierName`, `serviceCode`, `name`, `transitDaysMin`, `transitDaysMax`, `supportsCod`, `supportsReverse` | `carrierId` → `serviceCode` · `supportsCod` boolean | — | `FR-196` |
| WS-109 | `wh_carrier_accounts` · `WAREHOUSE_CARRIER_ACCOUNT` | `carrierName`, `accountCode`, **`ownerName` (nullable)**, `paymentMode`, `isDefault`, `isActive` | `carrierId` → `ownerId` · `paymentMode` select · `isActive` | `owner_id` nullable — *"ship on the client's account"* is a standard 3PL clause. `credentials_ref` is **masked at the edge** | `FR-196` |
| WS-110 | `wh_manifests` · `WAREHOUSE_MANIFEST` | `manifestNumber`, `carrierName`, `warehouseName`, `manifestDate`, `totalShipments`, `status`, `handedOverAt` | `warehouseId` → `carrierId` · `manifestDateFrom`/`To` `dateOnly` pair · `status` | v1.1. **Manifest, handover and pickup request are three objects, not one** | `FR-194` |
| WS-111 | `wh_handovers` · `WAREHOUSE_HANDOVER` | `handoverNumber`, `warehouseName`, `carrierName`, `vehicleNumber`, `driverName`, `sealNumber`, `gatePassRef`, `handedOverAt`, `handedOverByName`, `receivedByName` | `warehouseId` → `carrierId` · `handedOverFrom`/`To` | v1.1. **Our** record that N shipments physically left | `FR-194` |
| WS-112 | `wh_pickup_requests` · `WAREHOUSE_PICKUP_REQUEST` | `requestNumber`, `carrierName`, `warehouseName`, `requestedForAt`, `status`, `carrierReference` | `warehouseId` → `carrierId` → `status` · `requestedForFrom`/`To` | v1.1 | `FR-194` |
| WS-113 | `wh_consignments` · `WAREHOUSE_CONSIGNMENT` | `consignmentNumber`, `shipmentNumber`, `carrierName`, `lrNumber`, `lrDate`, `freightTerms`, `declaredValue`, `ewayBillRef` | `carrierId` · `lrNumber` text · `lrDateFrom`/`To` `dateOnly` pair | v1.1. **1:1 with a shipment and optional** | `FR-193` |
| WS-114 | `wh_shipping_labels` · `WAREHOUSE_SHIPPING_LABEL` | `shipmentNumber`, `cartonNumber`, `carrierName`, `trackingNumber`, `format`, `generatedAt`, `voidedAt`, `voidReasonName` | `carrierId` · `trackingNumber` text · `voidedOnly` boolean · `generatedFrom`/`To` | v1.1. **Stored artefacts with a void path, never deleted** | `FR-197` |
| WS-115 | `wh_shipment_tracking_events` · `WAREHOUSE_TRACKING_EVENT` | `shipmentNumber`, `carrierName`, `eventAt`, `rawStatus`, `normalisedStatus`, `locationText`, `receivedAt` | `carrierId` → `normalisedStatus` select · `eventFrom`/`To` `date` pair | v2. Stored **normalised and raw**. Log-style: no audit columns | `FR-198` |
| WS-116 | `wh_carrier_status_mappings` · `WAREHOUSE_CARRIER_STATUS_MAPPING` | `carrierName`, `rawStatus`, `normalisedStatus`, `isTerminal`, `effectiveFrom` | `carrierId` · `normalisedStatus` select | v2. Mapping **held as data**, so a wrong mapping is corrected and the history reinterpreted | `FR-198` |
| WS-117 | `wh_rate_quotes` · `WAREHOUSE_RATE_QUOTE` | `shipmentNumber`, `carrierName`, `serviceCode`, `quotedAmount`, `currencyCode`, `transitDays`, `billableWeightKg`, `wasSelected`, `selectionReason` | `carrierId` · `wasSelected` boolean · `quotedFrom`/`To` | v2. **The quote is persisted**, including why it was or was not selected | `FR-200` |
| WS-118 | `wh_carrier_serviceability` · `WAREHOUSE_CARRIER_SERVICEABILITY` | `carrierName`, `serviceCode`, `postalCode`, `isServiceable`, `supportsCod`, `supportsReverse`, `effectiveFrom` | `carrierId` → `serviceCode` · `postalCode` text · `isServiceable` boolean | v2. **Serviceability gates the rate shop; address validation only warns** | `FR-201` |
| WS-119 | `wh_awb_pools` + `wh_awb_numbers` · `WAREHOUSE_AWB_POOL` | `carrierName`, `accountCode`, `serviceCode`, `paymentMode`, `blockFrom`, `blockTo`, `fetchedAt`, `remainingCount`, `lowWaterMark` | `carrierId` → `carrierAccountId` → `serviceCode` · `belowLowWaterMark` boolean | v2. Numbers claimed **transactionally with `FOR UPDATE SKIP LOCKED`** — a mechanism with **zero precedent in this codebase**, flagged as new work | `FR-202` `FR-425` |
| WS-120 | `wh_shipment_ndrs` · `WAREHOUSE_NDR` | `shipmentNumber`, `carrierName`, `ndrReasonName`, `raisedAt`, **`responseDueAt`**, `status`, `attemptNo`, `closedAt` | `carrierId` → `status` · `overdueOnly` boolean · `raisedFrom`/`To` | v2. **A workflow with a response clock**, not an exception code; actions in `wh_ndr_actions` | `FR-203` |
| WS-121 | `wh_cod_remittances` · `WAREHOUSE_COD_REMITTANCE` | `remittanceNumber`, `carrierName`, `utr`, `remittedAt`, `grossAmount`, `deductionAmount`, `netAmount`, `status`, `unmatchedLineCount` | `carrierId` → `status` · `utr` text · `remittedFrom`/`To` | v2. Lines match to shipments; **unmatched is a first-class state** | `FR-204` |
| WS-122 | `wh_rto_consignments` · `WAREHOUSE_RTO` | `shipmentNumber`, `initiatedAt`, `rtoReasonName`, `returnAwb`, `receivedAt`, `returnReceiptNumber`, `status`, `ageDays` | `status` select · `ageOverDays` select · `initiatedFrom`/`To` | **RTO is an inbound stock stream, not an order status** — the columns are v1, the workflow v2 | `FR-205` |
| WS-123–126 | `wh_channel_accounts`, `wh_channel_order_imports`, `wh_channel_publish_rules`, `wh_tracking_links` · `WAREHOUSE_CHANNEL_ACCOUNT` etc. | per `DATA-MODEL.md` §2.2.3 | `channelId` → `ownerId` → `warehouseId` · `outcome` select · `basis` select | v2. Import is **idempotent on (channel account, external order id)** with an external version so a stale re-poll is discarded; publish rules are **the oversell control** | `FR-207` `FR-208` `FR-209` `FR-210` |
| WS-127 | `wh_working_calendars` · `WAREHOUSE_WORKING_CALENDAR` | `code`, `name`, `warehouseName`, `ownerName`, `timezone`, `isDefault`, `dayCount` | `warehouseId` → `ownerId` · `isDefault` | v2. Child editor over `wh_working_calendar_days`. **The same code computes promised dates and SLA clocks** | `FR-181` |
| WS-128 | `wh_order_edit_rules` · `WAREHOUSE_ORDER_EDIT_RULE` | `fromStatus`, `editType`, `isAllowed`, `requiredPermission`, `compensatingAction`, `requiresReason` | `fromStatus` select → `editType` select · `isAllowed` boolean | v1.1. The **seeded from-status × edit-type matrix** that governs order edit after release | `FR-183` |
| WS-129/130 | `wh_weighing_instruments`, `wh_weighing_records` · `WAREHOUSE_WEIGHING_INSTRUMENT` / `_RECORD` | `code`, `warehouseName`, `instrumentType`, `serialNumber`, **`verificationCertificateNo`**, `verifiedFrom`/`verifiedTo` (`dateOnly`), `isActive` / `instrumentCode`, `subjectType`, `subjectId`, `grossKg`, `tareKg`, `netKg`, `weighedAt`, `weighedByName` | `warehouseId` · `expiringWithinDays` select · `weighedFrom`/`To` | v2. **A weighing instrument is a legal instrument** — a weight captured on an expired certificate is a compliance finding, and the grid's `expiringWithinDays` filter is the surface that prevents it | `FR-223` |

**Mobile for §3.3:** `screens/whShipment` (dispatch — **WS-234 RF Ship** is the scan surface),
`screens/whCarton` (read + reprint label), `screens/whPickTask` → **WS-232 RF Pick**,
`screens/whPackSession` → **WS-233 RF Pack**, `screens/whHandover` (the gate is a floor task).
`none`, each with the reason recorded: WS-107–109 and WS-116–118 and WS-127–128 (masters and
configuration), WS-110/112/113 (dispatch-office documents), WS-115/117/119/121/123–126 (v2 back-office
and integration), WS-120 (a call-centre workflow, not a warehouse one), WS-129/130 (v2, and the
instrument is at a fixed station with its own terminal).

#### WS-240 · Trade Portal — v2 · P5

`/warehouse/outbound/trade-portal` · **Customer** · `wh_trade_portal_users` ·
`WAREHOUSE_TRADE_PORTAL_USER` · `wh_trade_portal_users:*` · v2 · P5 · `FR-464` · table `V510221` ·
permissions, dependencies and menu `V511209` + `V511239` · caches: statistics `—` (filter-aware,
`FR-395`), no dropdown.

**A second persona on `FR-284`'s surface, not a second application** (`RK-006`). The 3PL client portal
(WS-172) is scoped by owner. This one is scoped by **customer counterparty**, through the same single
server-side resolver (`FR-406`). Its user is the independent garage, fleet operator or sub-dealer that buys
parts from the dealer's wholesale counter. It ships in its own task so that the 3PL portal (`P5-08`)
ships alone.
**The management grid** administers who may use the portal. Its rows are dated, in `wh_trade_portal_users`:
a platform user × a customer counterparty.
**Columns:** `userName` (the shared user-display helper) · `customerName` (`whb_counterparties.name`) ·
`effectiveFrom` · `effectiveTo` · `isCurrent` (backend-computed) · audit quartet + names.
**Filters:** `customerCounterpartyId` async typeahead (**scope before cap**) → cascades `userId`
typeahead · `currentOnly` boolean (default true).
**Export:** visible + both audit names.
**Modals:** single-tab add/edit (user, customer, `effective_from`); view = `ViewModalBase` with a
`StatusCard` and the user's access history.
**Actions:** row View / Edit / **End access** (sets `effective_to` and never deletes — a dated junction
has no `is_active`, `D-14`). Toolbar Add / Export / Grid config.
**The portal surface** has no grid of its own, as WS-172 has none. It is tabs over the existing screens,
each scoped to the caller's customer counterparty:
- **Availability** — a **flag** per item: in stock / on order / not stocked. **Never a quantity, and
  never another customer's.**
- **Orders** — the customer creates a `SALES` demand order in **`DRAFT`** for the counter to confirm
  (WS-099), and follows order and shipment status (WS-099, WS-105).
- **Documents** — challan and shipment document download.

There is **no pricing engine and no payment**.
**Scope is enforced at the row level in the query layer, with a negative test per endpoint** — `FR-300`'s
rule, applied to the customer key. Another customer's order is a `403`, never an empty grid.
**Mobile:** `none` — the portal is a browser product for the trade customer's own staff, and access
administration is a desk task. Stated per `FR-218`.

### 3.4 Printing — v1, because a warehouse that cannot print cannot be operated

`A-2` moved printing into v1 after `grep -rli "zpl\|escpos\|dymo"` across all Java and TypeScript
returned **0**: there is no label or document rendering anywhere in this codebase, so this is net-new
infrastructure with no precedent.

| id | Table · Scope | Ref | Key columns | Filters | Actions | FR |
|---|---|---|---|---|---|---|
| WS-131 | `wh_print_templates` · `WAREHOUSE_PRINT_TEMPLATE` | SV | `code`, `name`, **`templateKind`** (one of the **eleven** of `FR-225`), `format` (ZPL/EPL/TSPL/PDF/HTML), `widthMm`, `heightMm`, `defaultBarcodeFormat`, `ownerName` (nullable), `warehouseName`, `activeVersion`, `isActive` | `templateKind` select → `format` select · `warehouseId` · `ownerId` · `isActive` | Add/Edit · **Publish version** (child `wh_print_template_versions`; **a label layout is never edited in place** — a reprint of last month's label must reproduce last month's layout) · **Preview** · Set active | `FR-224` `FR-225` `FR-226` |
| WS-132 | `wh_print_jobs` · `WAREHOUSE_PRINT_JOB` | SV | `jobNumber`, `templateName`, `templateVersion`, `subjectType`, `subjectId`, `copies`, `printerName`, `status`, `printedAt`, `voidedAt`, `voidReasonName`, `requestedByName` | `templateKind` select → `status` select · `printerId` select · `subjectType` select · `printedFrom`/`To` `date` pair · `voidedOnly` boolean | Reprint · **Void** (reason-coded — **every print is a stored artefact with a void path, never a delete**) · Download rendered document | `FR-224` `FR-225` |
| WS-133 | `wh_printers` · `WAREHOUSE_PRINTER` | D | `code`, `name`, `warehouseName`, `zoneLocationCode`, `connectionType` (NETWORK/AGENT/BROWSER), `address`, `defaultFormat`, `isActive` | `warehouseId` → `zoneLocationId` · `connectionType` select · `isActive` | v1.1. Add/Edit/Test print | `FR-224` |
| WS-134 | `wh_print_routing_rules` · `WAREHOUSE_PRINT_ROUTING_RULE` | C | `sequence`, `templateKind`, `warehouseName`, `zoneLocationCode`, `deviceId`, `printerName` | `warehouseId` → `templateKind` select · `printerId` | v1.1. Add/Edit/Reorder · **Test routing** | `FR-224` |

**The eleven v1 template kinds** (`FR-225`), which are the `template_kind` vocabulary and which every
print action above references: item/shelf label · LPN or pallet label (internal Code-128 in v1; optional GS1-128 after capability checks) · carton label ·
shipping label · location label · goods-receipt note · pick list · packing slip · delivery document ·
movement document · hazard class label.
**Mobile:** WS-132 `screens/whPrintJob` — reprint from the floor is the single most requested print
action and it is on the handheld. `none` for WS-131 (template authoring is a desk task), WS-133 and
WS-134 (v1.1 configuration).

### 3.5 Returns, replenishment, VAS and go-live

| id | Table · Scope | Ref | Key columns | Filters | Actions & notes | FR |
|---|---|---|---|---|---|---|
| WS-135 | `wh_return_receipts` · `WAREHOUSE_RETURN_RECEIPT` | SV | `returnNumber`, **`returnType`** (CUSTOMER/RTO/REFUSED_DELIVERY/CANCELLED_IN_TRANSIT/VENDOR/RECALL/CLIENT_WITHDRAWAL/MARKETPLACE), `warehouseName`, `ownerName`, `customerName`, `rmaNumber` (**nullable**), `receivedAt`, `status`, `lineCount`, audit | `warehouseId` → `ownerId` → `returnType` select · `status` **multiselect** · `customerCounterpartyId` typeahead · `hasRma` boolean · `receivedFrom`/`To` `date` pair | **The return receipt is the primary object and the RMA is optional**, matched to it later on a screen rather than by re-receiving. Actions: Receive · **Match RMA** · Post · **Disposition** (v1 ships the three that close the loop: restock · quarantine · scrap; scrap needs an approver ≠ actor) · **Reverse** (`wh_return_receipts:reverse`: `POSTED → REVERSED` by an `L-3` mirror, **only before disposition**, `RJ-006`, §0.11). **Returns land in a dedicated stock status, never straight to available** | `FR-269` `FR-271` `FR-273` `FR-274` |
| WS-136 | `wh_rmas` · `WAREHOUSE_RMA` | SV | `rmaNumber`, `customerName`, `originalOrderNumber`, `rmaReasonName`, `expectedConditionCode`, `rmaDate`, `expiryDate`, `status`, `externalRef` | `customerCounterpartyId` → `status` · `rmaDateFrom`/`To` `dateOnly` pair · `expiredOnly` boolean | Add · Approve · Expire · Match to receipt. **The warehouse emits the disposition; it never decides a refund** — there is no refund screen, no refund amount and no payment path anywhere in this product | `FR-269` `FR-274` |
| WS-137 | `wh_return_gradings` · `WAREHOUSE_RETURN_GRADING` | C | `returnNumber`, `lineNo`, `conditionCode`, `gradeNote`, `gradedByName`, `gradedAt`, `photoDocumentId`, `dispositionCode` | `conditionCode` select · `dispositionCode` select · `gradedFrom`/`To` | v2. Grading **at the point of receipt**, with photographs through the platform `documents` table | `FR-272` |
| WS-138 | `wh_obsolescence_returns` · `WAREHOUSE_OBSOLESCENCE_RETURN` | SV | `claimNumber`, `supplierName`, `authorisationRef`, `windowFrom`/`windowTo`, `allowanceAmount`, `claimedAmount`, `settledAmount`, `status` | `supplierCounterpartyId` → `status` · `windowFromFrom`/`To` `dateOnly` pair | v2 | `FR-276` |
| WS-139 | `wh_recalls` · `WAREHOUSE_RECALL` | SV | `recallNumber`, `itemCode`, `lotCode`, `recallClass`, `initiatedAt`, `initiatedByName`, `regulatorReference`, `status`, `affectedShipmentCount`, `notifiedCount` | `itemId` typeahead → `lotId` typeahead · `recallClass` select · `status` · `initiatedFrom`/`To` | v2. **Quarantine all matching on-hand stock in place** with a status-change movement, then list every shipment that carried the lot (`wh_recall_lines`) and track the notification state | `FR-280` |
| WS-140 | `wh_replenishment_runs` · `WAREHOUSE_REPLENISHMENT_RUN` | SV | `runNumber`, `warehouseName`, `runType`, `runAt`, `runByName`, `status`, `totalSuggestions`, `totalValue` | `warehouseId` → `runType` select → `status` · `runFrom`/`To` `date` pair | **The run produces a document, not a grid** — a run row with suggestions under it, so "why did we order that" is answerable months later | `FR-253` |
| WS-141 | `wh_replenishment_suggestions` · `WAREHOUSE_REPLENISHMENT_SUGGESTION` | C | `runNumber`, `itemCode`, `warehouseName`, `onHand`, `allocated`, `onOrder`, `reorderPoint`, `suggestedQuantity`, **`suggestedSource`** (PURCHASE/TRANSFER — one spelling everywhere, `RJ-014` b), `sourceWarehouseName`, `reasonText`, `status` | `runId` select → `suggestedSource` select · `warehouseId` → `itemId` · `status` | Accept → creates a PO or a transfer · Reject (reason) · Bulk accept. **The sister-branch-first proposal is v2** (`P5-18`) and is not on this v1 screen. A v1 `TRANSFER` suggestion is a source the buyer picks. A scheduled run notifies the site's buyer role (`RK-004`) | `FR-253` |
| WS-142 | `wh_replenishment_tasks` · `WAREHOUSE_REPLENISHMENT_TASK` | SV | `taskNumber`, `itemCode`, `fromLocationCode`, `toLocationCode`, `quantity`, **`trigger`** (MIN_MAX/SHORT_PICK/OPPORTUNISTIC/BREAK_CASE), `status`, `assignedToName` | `warehouseId` → `trigger` select → `status` · `assignedTo` typeahead | v1.1. Pick-face replenishment, prioritised against pick starvation | `FR-255` `FR-259` |
| WS-143 | `wh_demand_history` · `WAREHOUSE_DEMAND_HISTORY` | C | `itemCode`, `warehouseName`, `periodYearMonth`, `hitCount`, `quantity`, `lostSaleCount`, `lostSaleQuantity`, `isMigrated` | `warehouseId` → `itemId` · `periodFrom`/`periodTo` text pair (YYYYMM) · `isMigrated` boolean | **Maintained by movement posting**, with adjustments and warranty issues excluded by the reason code's `affects_demand_history`. Log-style: no audit columns | `FR-256` `FR-415` |
| WS-144 | `wh_work_orders` · `WAREHOUSE_WORK_ORDER` | SV | `workOrderNumber`, `workOrderType` (ASSEMBLE/DISASSEMBLE/REPACK/DECANT/VAS), `kitName`, `outputItemCode`, `warehouseName`, `ownerName`, `plannedQuantity`, `producedQuantity`, `scrappedQuantity`, `vasServiceTypeCode`, `status` | `warehouseId` → `workOrderType` select → `status` · `outputItemId` typeahead · `createdFrom`/`To` | v1.1. Release · Issue components · **Complete** (posts **one balanced movement that balances by value, not by quantity** — components in, kit out) · Cancel. Genealogy is written at completion | `FR-261` `FR-262` `FR-263` `FR-266` |
| WS-145 | `wh_vas_service_types` · `WAREHOUSE_VAS_SERVICE_TYPE` | D | `code`, `name`, `serviceCategory`, `billingUnit`, `estimatedMinutesPerUnit`, `isActive` | `serviceCategory` select · `isActive` | v1.1. **The rate lives in `warehouse-3pl`; the service type stays here** | `FR-267` |
| WS-146 | `wh_labour_tasks` · `WAREHOUSE_LABOUR_TASK` | C | `taskNumber`, `userName`, `startedAt`, `endedAt`, `pausedSeconds`, `unitsProcessed`, `referenceType`, `referenceId`, `deviceId`, `durationMinutes` | `warehouseId` → `userId` typeahead · `referenceType` select · `startedFrom`/`To` `date` pair | v2. Log-style, no audit columns. **We measure actual task duration and report it; engineered standards are not built before a year of our own data** | `FR-227` `FR-228` |
| WS-147 | `wh_landed_cost_documents` · `WAREHOUSE_LANDED_COST_DOCUMENT` | SV | `documentNumber`, `grnNumber`, `chargeKind`, `counterpartyName`, `amount`, `currencyCode`, **`apportionmentBasis`** (VALUE/QUANTITY/WEIGHT/VOLUME/MANUAL), `appliedAt`, `appliedByName`, `status` | `warehouseId` → `chargeKind` select → `status` · `grnNumber` text · `appliedFrom`/`To` | Add · **Apply** (retrospectively revalues the receipt through a value-only movement and retains `wh_landed_cost_allocations` so the revaluation is reproducible) · Reverse. **The apportionment basis lives on the receipt, not on the freight charge** | `FR-238` `FR-239` `FR-345` |
| WS-148 | `wh_revaluations` · `WAREHOUSE_REVALUATION` | SV | `revaluationNumber`, `warehouseName`, `ownerName`, `reasonCodeName`, `effectiveDate` (`dateOnly`), `approvedByName`, `approvedAt`, `totalValueChange`, `status`, `movementSequenceNo` | `warehouseId` → `ownerId` → `status` · `effectiveFrom`/`To` `dateOnly` pair | Add · Approve · **Post** — **revaluation is a document, not an `UPDATE`**: a movement type with zero quantity and a non-zero value, so the stock ledger and the GL move together | `FR-240` |
| WS-149 | `wh_nrv_assessments` · `WAREHOUSE_NRV_ASSESSMENT` | SV | `assessmentNumber`, `itemCode`, `lotCode`, `warehouseName`, `assessedNrv`, `basis`, `assessorName`, `assessedAt`, `writeDownAmount`, `reversalOfAssessmentNumber` | `warehouseId` → `itemId` · `assessedFrom`/`To` · `isReversal` boolean | v2. **A register, not a one-way provision column** — including the reversal when NRV recovers | `FR-241` |
| WS-150 | `wh_opening_stock_batches` · `WAREHOUSE_OPENING_STOCK_BATCH` | SV | `batchNumber`, `companyName`, `warehouseName`, `asAtDate` (`dateOnly`), `status` (DRAFT/VALIDATED/POSTED/REVERSED), `importBatchNumber`, `lineCount`, `validLines`, `errorLines`, `totalValue`, `postedMovementSequenceNo` | `companyId` → `warehouseId` → `status` · `asAtFrom`/`To` `dateOnly` pair | **Opening stock is a first-class feature, not an import script.** Upload (`ImportButton`) · **Validate** (dry run, persists nothing) · **Post** (opening-balance movements from the virtual opening-balance location, **with unit costs, so the first issue has a cost**) · **Reverse** · Export errors. Design for 200,000–1,000,000 position rows; the line child grid carries `validationStatus` and `errorDetail` per row | `FR-411` `FR-412` `FR-249` `FR-417` |
| WS-151 | `wh_cutover_checklists` · `WAREHOUSE_CUTOVER_CHECKLIST` | SV | `checklistNumber`, `companyName`, `warehouseName`, `targetGoLiveAt`, `status`, `blockingOpenCount`, `certifiedByName`, `certifiedAt`, `certificateDocumentId` | `companyId` → `warehouseId` → `status` · `targetGoLiveFrom`/`To` | Complete item · **Certify** (blocked while any `is_blocking` item is open; produces the **reconciliation certificate**, which is what makes the customer sign off the number) · Reopen | `FR-412` `FR-413` |
| WS-152 | `wh_migration_mappings` · `WAREHOUSE_MIGRATION_MAPPING` | C | `profileCode`, `sourceProduct`, `entityKind`, `sourceValue`, `targetKind`, `targetCode`, `confidence`, `resolvedByName`, `resolvedAt` | `profileCode` select → `entityKind` select · `sourceProduct` select · `unresolvedOnly` boolean · `confidenceBelow` number | v1.1. Resolve · Bulk resolve · **Export profile** / **Import profile** — one database per customer means the second customer is a different database and the profile must travel | `FR-414` |
| WS-153 | supervisor exception console (no grid of its own) | — | one screen over WS-097, WS-098, WS-054 and short/exception-coded tasks | — | v1.1. **One console, not four tabs a supervisor has to remember to open** | `FR-216` |
| WS-154 | task assignment board (no grid of its own) | — | pull and push assignment over `whb_tasks`, honouring zone, task type, equipment and **user qualifications** | — | v1.1. Assignment does not send a trolley picker to a high-reach location | `FR-214` `FR-215` |

**Mobile for §3.5:** `screens/whReturnReceipt` (receiving a return is a dock task),
`screens/whReplenishmentTask` → part of **WS-237 RF Task List**, `screens/whWorkOrder` (issue and
complete). `none`, with reasons: WS-136 (an authorisation raised by customer service),
WS-137–139 (v2 and desk-bound), WS-140/141 (a buyer's screen), WS-143 (a report), WS-146 (a report),
WS-147–149 (finance), WS-150–152 (implementation), WS-153/154 (**a supervisor console with four
queues and a drag-and-drop board does not fit a handheld; the supervisor uses a tablet browser** —
recorded as a decision, not an omission).

---

## 4. `warehouse-3pl` — `wh3_`, band V530000–V539999, **v2 · P5**

Grid config, permissions, dependencies and menus all land in `V531000`–`V531199` (`DATA-MODEL.md`
§7.5, W3-20). `FR-281`: **neither base nor app depends on this module** — no `whb_`/`wh_` table has an
FK to a `wh3_` table.

| id | Screen · Table · Scope | Ref | Key columns | Filters | Actions & notes | FR |
|---|---|---|---|---|---|---|
| WS-155 | 3PL Clients · `wh3_clients` · `WAREHOUSE_3PL_CLIENT` | SV | `clientCode`, `name`, **`ownerName`**, `counterpartyName`, `contractStartDate`/`contractEndDate` (`dateOnly`), `noticePeriodDays`, `billingCycle` (MONTHLY/FORTNIGHTLY/WEEKLY), `billingDay`, `currencyCode`, `status`, audit | `ownerId` → `status` · `billingCycle` select · `contractEndBefore` (`dateOnly`) · `clientCode`/`name` text | **A client is an object, not a customer record.** Onboard (instantiates WS-157 from a template) · Suspend · Terminate. Every client is bound to exactly one `whb_owners` row — that binding is what makes `owner_id` in v1 the thing that turns a rewrite into a module | `FR-282` `D-5` |
| WS-156 | Onboarding Templates · `wh3_client_onboarding_templates` · `WAREHOUSE_3PL_ONBOARDING_TEMPLATE` | C | `code`, `name`, `isDefault`, `taskCount` | `isDefault` boolean | Child editor over `wh3_client_onboarding_template_tasks` (`sequence`, `task_name`, `owner_role`, `due_offset_days`, `is_blocking`) | `FR-283` |
| WS-157 | Onboarding Tasks · `wh3_client_onboarding_tasks` · `WAREHOUSE_3PL_ONBOARDING_TASK` | SV | `clientName`, `taskName`, `assignedToName`, `dueAt`, `completedAt`, `status`, `isBlocking`, `evidenceNote` | `clientId` → `status` · `assignedTo` typeahead · `dueBefore` (`date`) · `blockingOnly` boolean | Assign · Complete (evidence note) · Reopen | `FR-283` |
| WS-158 | Charge Codes · `wh3_charge_codes` · `WAREHOUSE_3PL_CHARGE_CODE` | D | `code`, `name`, `category`, `defaultUomCode`, `isRecurring`, `isPassThrough`, `isTaxable`, `taxClassificationCode`, `revenueAccountRef`, `isActive` | `category` select · `isRecurring`/`isPassThrough`/`isTaxable` booleans · `isActive` | `D-10`'s thirteenth registry, **living where the charges do**. Same catalogue block as §2.1 | `FR-286` |
| WS-159 | Rate Cards · `wh3_rate_cards` · `WAREHOUSE_3PL_RATE_CARD` | SV | `cardCode`, `clientName` (**null = standard card**), `version`, `inheritsFromCardCode`, `effectiveFrom`/`effectiveTo` (`dateOnly`), `currencyCode`, `status` (DRAFT/ACTIVE/…), `lineCount` | `clientId` → `status` · `effectiveFromFrom`/`To` `dateOnly` pair · `standardOnly` boolean | Add · Clone as new version · **Activate** · Expire. Child editor over `wh3_rate_card_lines` (`charge_code`, `uom_code`, `rate`, `minimum_quantity`, `tier_from`/`tier_to`, `charge_kind`, `basis`). **Escalation generates a new version for review; it never mutates an active card** | `FR-287` `FR-290` `FR-296` |
| WS-160 | Billable Events · `wh3_billable_events` · `WAREHOUSE_3PL_BILLABLE_EVENT` | C | `eventCode`, `clientName`, `ownerName`, `warehouseName`, `chargeCode`, `quantity`, `uomCode`, `occurredAt`, `postingDate`, `sourceType`, `sourceId`, `isReversal` | `clientId` → `chargeCode` select · `warehouseId` · `occurredFrom`/`To` `date` pair · `postingDateFrom`/`To` `dateOnly` pair · `isReversal` boolean | Read-only + Reverse. **Append-only and reversible, exactly like the stock ledger, with its own idempotency key.** Log-style: no audit columns | `FR-285` |
| WS-161 | Storage Billing · `wh3_storage_billing_periods` · `WAREHOUSE_3PL_STORAGE_BILLING_PERIOD` | SV | `clientName`, `periodFrom`/`periodTo` (`dateOnly`), `method` (PERIOD_END/PERIOD_START/**ANNIVERSARY**/AVERAGE_DAILY), `basis` (PALLET/SQFT/…), `computedUnits`, `chargeAmount`, `status` | `clientId` → `method` select → `status` · `periodFromFrom`/`To` `dateOnly` pair | Compute · Approve · Recompute. **Reads `whb_stock_position_snapshots` and never recomputes occupancy** — which is why the snapshot job is `PNR-3` and why anniversary billing cannot be computed for a past the ledger never recorded. Line detail in `wh3_storage_billing_lines`, log-style | `FR-288` `FR-289` |
| WS-162 | Billing Runs · `wh3_billing_runs` · `WAREHOUSE_3PL_BILLING_RUN` | SV | `runNumber`, `clientName`, `periodFrom`/`periodTo`, `runType`, `status` (DRAFT/RATED/APPROVED/INVOICED/CANCELLED), `ratedAt`, `approvedAt`, `approvedByName`, `invoicedAt`, `rateCardCode`, `subtotal`, `lineCount` | `clientId` → `status` **multiselect** · `periodFromFrom`/`To` `dateOnly` pair | Rate · **Approve** (freezes the state) · **Emit AR handover** (WS-170) · Cancel. Line detail `wh3_billing_run_lines` with the **arithmetic shown** (`computation_note`), including `is_minimum_true_up` and `is_sla_credit`. **`warehouse-3pl` contains no invoice, no numbering sequence and no tax engine, in any version** | `FR-292` `FR-294` |
| WS-163 | Accessorials · `wh3_accessorials` · `WAREHOUSE_3PL_ACCESSORIAL` | SV | `accessorialNumber`, `clientName`, `chargeCode`, `quantity`, `rate`, `amount`, `reason`, `raisedByName`, `raisedAt`, `approvedByName`, `approvedAt`, `status` | `clientId` → `chargeCode` → `status` · `raisedBy` typeahead · `raisedFrom`/`To` | Raise · **Approve** (above a threshold a **second** user must approve; the approver may not be the raiser) · Reject | `FR-291` `FR-408` |
| WS-164 | Disputes · `wh3_disputes` · `WAREHOUSE_3PL_DISPUTE` | SV | `disputeNumber`, `clientName`, `billingRunNumber`, `reason`, `disputedQuantity`, `disputedAmount`, `status`, `raisedAt`, `resolvedAt`, `resolution` | `clientId` → `status` · `billingRunId` select · `raisedFrom`/`To` | Raise (**from the portal**) · Investigate · **Uphold** (becomes a credit charge code — **never a silent edit of the run**) · Reject | `FR-293` |
| WS-165 | Freight Billing Rules · `wh3_freight_billing_rules` · `WAREHOUSE_3PL_FREIGHT_BILLING_RULE` | C | `clientName`, `mode` (at cost / cost+% / cost+fixed / own tariff / client's own account), `markupPercent`, `markupFixed`, `tariffCardCode`, `carrierAccountCode`, `effectiveFrom`/`effectiveTo` | `clientId` → `mode` select · `effectiveFromFrom`/`To` | Add/Edit/End-date | `FR-295` |
| WS-166–168 | SLA Definitions / Measurements / Breaches · `wh3_sla_definitions`, `_measurements`, `_breaches` · `WAREHOUSE_3PL_SLA_DEFINITION` etc. | C / C / SV | definition: `code`, `name`, `clientName`, `metricCode`, `targetValue`, `comparison` (GTE/LTE), `windowKind`, `calendarCode`, `penaltyChargeCode`, `isActive` · measurement: `definitionCode`, `windowFrom`/`windowTo`, `measuredValue`, `sampleCount`, `isBreach`, `computedAt` · breach: `measurementId`, `confirmedByName`, `confirmedAt`, `penaltyAmount`, `billableEventId`, `waived`, `waiverReason` | `clientId` → `metricCode` select · `isBreach` boolean · `windowFromFrom`/`To` `dateOnly` pair | Definitions: add/edit. Measurements: read-only with **drill-through to the failing rows** — a measurement nobody can drill into is a number nobody believes. Breaches: Confirm · **Waive** (reason) · Post penalty (a **negative billable event** on the SLA-credit code, subject to approval — v3) | `FR-297` `FR-298` `FR-299` |
| WS-169 | Client GST Registrations · `wh3_client_gst_registrations` · `WAREHOUSE_3PL_CLIENT_GST_REGISTRATION` | C | `clientName`, `gstin`, `warehouseName`, `isAdditionalPlaceOfBusiness`, `certificateDocumentId`, `effectiveFrom`/`effectiveTo`, `status` | `clientId` → `warehouseId` · `gstin` text · `status` | v2 · **P4**, not P5 — it is an India-pack obligation with a 3PL subject | `FR-301` |
| WS-170 | AR Handover Queue · `wh3_ar_handovers` · `WAREHOUSE_3PL_AR_HANDOVER` | SV | `billingRunNumber`, `envelopeKind`, `idempotencyKey`, `status`, `attemptCount`, `externalDocumentRef`, `rejectionCode`, `rejectionMessage` | `status` **multiselect** (default PENDING+REJECTED) · `clientId` · `createdFrom`/`To` | Retry · View payload. **An approved run emits one AR document envelope; this module writes no invoice** | `FR-294` |
| WS-171 | Client Profitability · `wh3_client_profitability_snapshots` · `WAREHOUSE_3PL_CLIENT_PROFITABILITY` | C | `clientName`, `periodFrom`/`periodTo`, `revenue`, `labourMinutes`, `labourCost`, `storageUnits`, `storageCost`, `margin`, `marginPct` | `clientId` · `periodFromFrom`/`To` `dateOnly` pair | v3. Read-only + Export | `FR-302` |
| WS-172 | Client Portal · **no grid of its own** | — | a **permission surface over the existing screens**, owner-bound, `PORTAL` grant only — not a second application with its own authentication | — | v2. Tabs: stock (WS-042 scoped) · inbound (WS-076) · outbound (WS-099/WS-105) · billing (WS-162) · disputes (WS-164) · **performance** (WS-167 rendered as trend plus current period with drill-through) · documents | `FR-284` `FR-298` `FR-300` |

**Owner segregation is enforced at the row level in the query layer, with a negative test per
endpoint** (`FR-300`). A client seeing another client's stock is the failure that ends the contract,
and it is not prevented by a UI filter. `FR-114` again: an owner the caller has no grant for is a
`403`, **never an empty grid**.
**Mobile:** `screens/wh3Client` read-only list for a 3PL operator who needs to confirm whose goods
they are handling; **`none` for every other 3PL screen** — billing, rate cards, disputes, SLA and the
portal are desk surfaces, and the portal in particular is a browser product for the client's own
staff. Stated per `FR-218`.

---

## 5. `warehouse-india` — `whin_`, band V540000–V549999

Two waves (`A-4`). **`P2-IN` is v1** — the documents without which goods may not legally move in
India — and **P4 is v2** — the statutory registers and filings. Grid config, permissions and menus in
`V541000`–`V541199`.

**`warehouse` never computes tax** (`OD-9`, `FR-294`). It captures the tax-relevant facts — HSN,
place of supply, `is_taxable_supply` frozen at creation, taxable value — and hands them over.

### 5.1 The v1 wave — `P2-IN`

| id | Screen · Table · Scope | Ref | Key columns | Filters | Actions & notes | FR |
|---|---|---|---|---|---|---|
| WS-173 | GSTIN Profiles · `whin_gstin_profiles` · `WAREHOUSE_INDIA_GSTIN_PROFILE` | C | `gstin`, `companyName`, `placeOfBusinessCount` (current `whin_gstin_profile_branches` rows), `stateCode`, `registrationType`, `legalName`, `tradeName`, `effectiveFrom`/`effectiveTo` (`dateOnly`), `isActive` | `companyId` → `branchId` (a current place of business) · `stateCode` select · `registrationType` select · `isActive` | Add/Edit/End-date · **Places of business** (a tab and sub-grid over `whin_gstin_profile_branches`: branch (`branches.branch_name`), `place_role` `PRINCIPAL`/`ADDITIONAL` — a closed statutory `CHECK` under `OD-5` — and dates). One registration covers every branch in its state, so the second Delhi branch resolves the same profile (`RG-002`, `WH-SC-313`). `whin_gstin_profiles.branch_id` is dropped. `gstin` stays unique, and it is checked equal to each place's `branches.gst_number` on save, with a nightly drift row (`RH-005`). The GSTIN is **never duplicated onto the warehouse** — a site reaches it through its `REGISTERED` link | `FR-305` |
| WS-174 | Compliance Providers · `whin_compliance_providers` (+ `_provider_environments`, `_credential_specs`) · `WAREHOUSE_INDIA_COMPLIANCE_PROVIDER` | C | `code`, `name`, `providerKind` (EWAYBILL/EINVOICE/BOTH), `baseUrlTemplate`, `environmentCount`, `isActive` | `providerKind` select · `isActive` | Add/Edit with two child editors — environments (SANDBOX/PRODUCTION) and **credential specs as rows, so a new provider is data, not a release** | `FR-326` |
| WS-175 | Compliance Registrations · `whin_compliance_registrations` (+ `_credentials`, `_auth_sessions`) · `WAREHOUSE_INDIA_COMPLIANCE_REGISTRATION` | C | `gstinProfileGstin`, `providerName`, `environment`, `documentKinds`, `registeredAt`, `status`, `tokenExpiresAt` | `gstinProfileId` → `providerId` → `environment` select · `status` | Register · Rotate credentials · Test connection. **Credential values are encrypted and masked at the edge** per the platform admin-settings idiom: the response carries `hasValue` (**`null`, not `undefined`**, when unset), never the value | `FR-326` |
| WS-176 | Compliance Documents · `whin_compliance_documents` · `WAREHOUSE_INDIA_COMPLIANCE_DOCUMENT` | C | `documentKind`, `subjectType`, `subjectId`, `registrationGstin`, `status`, `providerReference`, `sentAt`, `respondedAt`, `errorCode` | `documentKind` select → `status` select · `registrationId` · `sentFrom`/`To` `date` pair | View request/response payload (`TEXT`) · Retry. **The e-way bill adapter reads only this table and the v1 base columns; it never reaches into an operational table for a field it forgot to copy** | `FR-310` `FR-326` |
| WS-177 | Compliance API Logs · `whin_compliance_api_logs` · `WAREHOUSE_INDIA_COMPLIANCE_API_LOG` | C | `registrationGstin`, `endpoint`, `httpStatus`, `latencyMs`, `calledAt`, `correlationRef` | `registrationId` · `httpStatus` number · `calledFrom`/`To` `date` pair · `slowerThanMs` number | Read-only + Export. Log-style, no audit columns. It exists so a provider dispute is answerable with latency evidence | `FR-326` |
| WS-178 | Delivery Challans · `whin_delivery_challans` · `WAREHOUSE_INDIA_DELIVERY_CHALLAN` | SV | `challanNumber`, **`challanPurpose`** (BRANCH_TRANSFER/JOB_WORK/APPROVAL/LINE_SALE/EXHIBITION/REPAIR), `gstinProfileGstin`, `transferNumber`, `consigneeName`, `recipientGstin` (the frozen `to_counterparty_tax_registration_id`), `challanDate` (`dateOnly`), `taxableValue`, `status`, `ewayBillNo`, audit | `gstinProfileId` → `challanPurpose` select → `status` · `challanDateFrom`/`To` `dateOnly` pair · `challanNumber` text · `hasEwayBill` boolean | Generate (from a transfer, a job-work dispatch or an approval dispatch) · Print · Cancel · **Generate e-way bill** (WS-179). **There is one challan table** — warehouse's delivery challan *is* the challan, with **its own series** from `whb_number_series`, keyed by the issuing site's **`REGISTERED` branch** at the challan date (WS-061); the accounting set's parallel job-work challan is retired. **The recipient registration and address are frozen at generation**: `to_counterparty_tax_registration_id` and `to_counterparty_address_id` (WS-021, `RG-003`), the recipient's registration for the ship-to state, read-only afterwards | `FR-307` `FR-313` |
| WS-179 | E-way Bills · `whin_eway_bills` · `WAREHOUSE_INDIA_EWAY_BILL` | SV | `ewayBillNo`, `challanNumber`, `shipmentNumber`, `transferNumber`, `gstinProfileGstin`, `recipientGstin`, `generatedAt`, **`validUntil`**, `distanceKm`, **`partBFilledAt`**, `vehicleNumber`, `status` | `gstinProfileId` → `status` select · `validUntilBefore` (`date`) · `partBPending` boolean · `generatedFrom`/`To` `date` pair · `ewayBillNo` text | **Generate Part-A** · **Fill Part-B** (required before movement) · **Extend validity** · **Update vehicle** · **Cancel** (within the statutory window) — five transitions, five modals. Transport fields come from `whb_transport_details`, which attaches **polymorphically** to a transfer, a challan or an issue and is rendered as a panel, not as a grid. **The recipient registration and address** are the frozen `to_counterparty_tax_registration_id` / `to_counterparty_address_id` (`RG-003`). The from-GSTIN is the dispatching site's `REGISTERED` branch at the document date, and the dispatch-from address is the warehouse's (R22 §1.2.4 row 1) | `FR-308` `FR-309` |

**`FR-195`: the gate pass is e-way-bill-conditional** — it issues freely where no e-way bill is
required and blocks only where one is legally required and absent. That gate lives on WS-111
(Handovers) and is contributed by this module, which is why the button is registered by
`warehouse-india` rather than owned by `warehouse`.

### 5.2 The v2 wave — `P4`

| id | Screen · Table(s) | Ref | What it is | FR |
|---|---|---|---|---|
| WS-180 | `whin_eway_bills_consolidated` (+ `_consolidated_items`) · `WAREHOUSE_INDIA_EWAY_BILL_CONSOLIDATED` | SV | The consolidated e-way bill for one vehicle carrying many. Child grid of member bills | `FR-309` |
| WS-181 | `whin_job_work_registrations` (+ `_dispatch_lines`) · `WAREHOUSE_INDIA_JOB_WORK_REGISTRATION` | SV | Goods leave under a job-work challan to a location **at the job worker's premises with the owner unchanged**, carrying an expected-return clock. Columns: sent, expected return, actual return, shortfall | `FR-312` |
| WS-182 | `whin_itc04_returns` (+ `_lines`) · `WAREHOUSE_INDIA_ITC04_RETURN` | SV | The ITC-04 filing period and its lines. Generate · Review · Mark filed · Export | `FR-312` |
| WS-183 | `whin_stock_account_periods` (+ `_lines`) · `WAREHOUSE_INDIA_STOCK_ACCOUNT_PERIOD` | C | The **Rule 56 statutory stock account**, per registration and per period, in the mandated categories — opening, receipts, supplies, losses, closing. Ledger-style, no audit columns. **A movement is attributed movement → site → the `REGISTERED` link at its `occurred_at` → branch → profile** (`D-14`), so a site re-registered mid-period is split at the switch instant. Each GSTIN's account covers only its own range (`WH-SC-307`), and R22 §1.2.6 ensures no stock is on hand at the switch | `FR-314` |
| WS-184 | `whin_itc_reversals` · `WAREHOUSE_INDIA_ITC_REVERSAL` | C | The reversal on a write-off, which needs the **original credit** — so the write-off movement must be able to reach the receipt that brought the lot in, through `whb_cost_layer_consumptions` | `FR-315` `FR-316` |
| WS-185 | `whin_bonded_licences` · `WAREHOUSE_INDIA_BONDED_LICENCE` | C | The site as a licensed object with a validity. Expiry filter is `expiringWithinDays`, a dropdown | `FR-323` |
| WS-186 | `whin_warehousing_bonds` (+ `_bond_utilisations`) · `WAREHOUSE_INDIA_WAREHOUSING_BOND` | SV | A bond with a **running utilisation balance** and its utilisation ledger | `FR-323` |
| WS-187 | `whin_ex_bond_clearances` · `WAREHOUSE_INDIA_EX_BOND_CLEARANCE` | SV | Ex-bond Bill of Entry consuming **identified bonded quantity** — possible only because `duty_status` was on the movement line from v1 | `FR-323` `IRR-12` |
| WS-188 | `whin_approval_dispatches` (+ `_approval_clocks`) · `WAREHOUSE_INDIA_APPROVAL_DISPATCH` | SV | Goods sent on approval / sale-or-return: a stock state at the customer that is still our asset, on a challan, with a **deemed-supply clock** | `FR-322` |
| WS-189 | `whin_epr_returns` (+ `_lines`, `whin_epr_categories`) · `WAREHOUSE_INDIA_EPR_RETURN` | SV | Extended-producer-responsibility reporting for batteries, e-waste, tyres and plastic packaging — **pure reporting over quantities already in the ledger** | `FR-324` |
| WS-190 | `whin_retention_policies` · `WAREHOUSE_INDIA_RETENTION_POLICY` | D | **Two retention clocks on the same rows** — the Companies Act's financial years and the GST period — with per-item shelf-life overrides. **Retention beats erasure**, satisfied by pseudonymising the person and never the quantity | `FR-329` `FR-441` |
| WS-191 | `whin_compliance_tasks` (+ `whin_compliance_rules`, `_rule_conditions`) · `WAREHOUSE_INDIA_COMPLIANCE_TASK` | SV | Scheduled compliance obligations and the **bounded rules** that raise them — whitelisted subject columns and operators, never a JSONB condition bag | `FR-326` `FR-383` |
| WS-192 | `whin_tax_rules` (+ `_rule_components`, `_rule_conditions`, `whin_tax_components`, `whin_tax_entity_types`, `whin_tax_resolution_audit`) · `WAREHOUSE_INDIA_TAX_RULE` | — | The relational tax-rule workbench, **carried forward with its known defects fixed as blockers of the India pack, not deferred**. The resolution-audit grid is the surface that answers "why did it pick that rate" | `FR-325` |
| WS-193 | `whin_hsn_tax_master`, `whin_sac_master`, `whin_gst_state_codes` · `WAREHOUSE_INDIA_TAX_REFERENCE` | D | Read-mostly reference. **The item still stores the classification code as a string, never an FK into this** (`FR-066`) | `FR-325` |

**Mobile for §5:** `screens/whinEwayBill` — **Fill Part-B and Update vehicle only.** A driver whose
vehicle changed at a transhipment point must update Part-B from the road; everything else in this
module is a compliance desk. `none`, stated, for WS-173–178 and WS-180–193.

---

## 6. The four adapters — `whad_` `whas_` `whaf_` `whaa_`, band V520000–V529999

`D-11` and `FR-349`/`FR-350`: an adapter **may** register its own permissions, menus, grids and filter
scopes and own its own tables; it **must not** be depended upon by base or app, write a `whb_`/`wh_`
table directly, add a column to a base table or extend a base vocabulary by `ALTER`.
**The ratchet is `git log --oneline -- warehouse-base/ | wc -l` unchanged at the commit that merges
the second adapter**, recorded in the PR description.

`warehouse-adapter-example` (`whae_`, `V525000`–`V525999`) ships **zero screens** — one movement type,
one document type, one document kind, and a CI build. That is the point of it.

| id | Screen · Table · Scope | Ref | Key columns | Filters | Actions & notes | FR |
|---|---|---|---|---|---|---|
| WS-194 | Counter Sale · `whad_counter_sales` (+ `_lines`) · `WAREHOUSE_DEALER_COUNTER_SALE` | **— (keyboard-first single-screen flow, not a management grid page; the *list* below it is the Service Vehicle shape)** | `saleNumber`, `branchName` (**`branches.branch_name`**), `warehouseName`, `customerName`, `priceLevel`, `subtotal`, `taxAmount`, `totalAmount`, `paymentMode`, `demandOrderNumber`, `status` | `branchId` → `warehouseId` (**the picker lists only sites with a current `REGISTERED` or `SERVING` link to the selling branch**, `D-14`) · `customerCounterpartyId` typeahead · `paymentMode` select · `saleDateFrom`/`To` `date` pair | **Scan or part number → quantity → price level → print → next: a sub-ten-second bill.** One focused input, no mouse. Trade-counter behaviours: supersession substitution (`is_superseded_substitute`, `original_item_id`), interchange offer *"not in stock — 2 available as `<interchange>`"* with availability **across every branch**, and lost-sale capture straight into `wh_insufficient_stock_log` when the guard refuses. **A sale from a `SERVING` site under a different GSTIN is refused with `422 CROSS_GSTIN_COUNTER_SALE`** (§0.13, `FR-461`). The screen states why and offers *Raise request* (WS-090 in `REQUESTED`), because a counter sale never silently becomes a cross-GSTIN supply | `FR-358` `FR-359` `FR-073` `FR-257` `FR-461` |
| WS-195 | Vehicle Fitments · `whad_vehicle_fitments` · `WAREHOUSE_DEALER_VEHICLE_FITMENT` | C | `itemCode`, `modelName`, `variantName`, `yearFrom`, `yearTo`, `position`, `notes` | `modelId` → `variantId` → `itemId` typeahead · `yearFrom`/`yearTo` number pair | **Fitment lives here and never in `warehouse-base`** — if base learns about vehicle models it can no longer serve assets, field-service or logistics. References the automotive model master sideways | `FR-074` |
| WS-196 | OEM Orders · `whad_oem_orders` (+ `_lines`) · `WAREHOUSE_DEALER_OEM_ORDER` | SV | `oemOrderNumber`, `oemName`, `warehouseName`, `orderSource`, `transmittedAt`, `acknowledgedAt`, `status`, `poNumber`, `lineCount`, `backorderedLines` | `warehouseId` → `oemCounterpartyId` → `status` · `transmittedFrom`/`To` | v1.1. Transmit · Consume acknowledgement (allocated and back-ordered quantities and an ETA per line) · Match receipt against the OEM invoice file · Raise discrepancy. **Format-pluggable per OEM; no single OEM's layout is hard-coded** | `FR-420` |
| WS-197 | OEM Price Files · `whad_price_files` (+ `_lines`) · `WAREHOUSE_DEALER_PRICE_FILE` | SV | `fileReference`, `oemName`, `effectiveDate` (`dateOnly`), `importBatchNumber`, `status`, `appliedAt`, `appliedByName`, `lineCount`, `newCount`, `priceChangeCount`, `supersessionCount` | `oemCounterpartyId` → `status` · `effectiveFrom`/`To` `dateOnly` pair | v1.1. Upload · **Dry-run diff** (before apply, always) · Apply — writing item and price rows, supersessions and, where the direction warrants it, a **revaluation movement** for the on-hand quantity and a price-protection claim | `FR-419` |
| WS-239 | Item Prices · `whad_item_prices` (+ `whad_price_levels`) · `WAREHOUSE_DEALER_ITEM_PRICE` | D | `itemCode`, `itemName`, `priceLevelCode`, `unitPrice`, `currencyCode`, `effectiveFrom` (`dateOnly`), `effectiveTo` (`dateOnly`) | `priceLevelCode` select (fetched) · `itemId` typeahead · `effectiveOn` (`dateOnly`) | v1 (`RA-002`). **`ImportButton`** in the Service Vehicle import pattern — thirty thousand prices are never keyed. A *Price levels* tab maintains `whad_price_levels`. The counter sale (WS-194) resolves a line's `unit_price` here by price level at the sale date, and a line with no price row is refused, never priced at zero. `whad_price_files` (WS-197, v1.1) later loads into the same table | `FR-359` |
| WS-198 | Core Exchanges · `whad_core_exchanges` · `WAREHOUSE_DEALER_CORE_EXCHANGE` | SV | `exchangeNumber`, `orderLineRef`, `newItemCode`, `newSerialNumber`, `coreItemCode`, `coreDepositAmount`, `coreReturnDeadline` (`dateOnly`), `coreReceivedAt`, `gradingCode`, `creditAmount`, `status` | `status` select · `deadlineBefore` (`dateOnly`) · `overdueOnly` boolean | v2. **Cores are inventory**: a `CORE` item type linked to the serviceable part, a core charge, a **core-bank location with its own valuation**, a return deadline and a grading | `FR-277` |
| WS-199 | Material Requests · `whas_material_requests` (+ `_lines`) · `WAREHOUSE_SERVICES_MATERIAL_REQUEST` | SV | `requestNumber`, `jobCardRef`, `warehouseName`, `requestedByName`, `technicianName`, `requestedAt`, `status`, `lineCount`, `reservedLines`, `issuedLines` | `warehouseId` → `status` **multiselect** · `technicianUserId` typeahead · `jobCardRef` text · `requestedFrom`/`To` | **A material request against a job card → reservation before it is picked.** Request · Reserve · Issue · Return unused · Cancel. `warehouse-adapter-services` is the largest consumer of the port and it ships in v1 because **one adapter proves nothing about genericity** | `FR-352` `FR-360` |
| WS-200 | Job Part Issues & WIP · `whas_job_part_issues` · `WAREHOUSE_SERVICES_JOB_PART_ISSUE` | C | `jobCardRef`, `itemCode`, `quantity`, `unitCost`, `issuedAt`, `issuedByName`, `movementSequenceNo`, `isReturned`, `wipValue` | `warehouseId` → `itemId` · `jobCardRef` text · `issuedFrom`/`To` `date` pair · `openJobsOnly` boolean | **Parts issued to open jobs are neither stock nor cost of sale** and are reported as work-in-progress at every month end. That report is this grid with `openJobsOnly` on | `FR-361` |
| WS-201 | Fitted Serials · `whas_fitted_serials` · `WAREHOUSE_SERVICES_FITTED_SERIAL` | C | `serialNumber`, `itemCode`, `jobCardRef`, `vehicleRefType`, `vehicleRefId`, `fittedAt`, `fittedByName` | `itemId` typeahead · `serialNumber` text · `fittedFrom`/`To` `date` pair | **A serialised part fitted to a customer's vehicle records the vehicle at issue time** — retro-linking a year of part issues to vehicles is not possible | `FR-362` |
| WS-202 | Warranty Holds · `whas_warranty_holds` · `WAREHOUSE_SERVICES_WARRANTY_HOLD` | SV | `jobPartIssueRef`, `claimReference`, `holdLocationCode`, `serialNumber`, `heldAt`, `retentionUntil` (`dateOnly`), `releasedAt`, `dispositionCode` | `claimReference` text · `retentionUntilBefore` (`dateOnly`) · `heldOnly` boolean | v2. A part replaced under warranty moves to a **warranty-hold location tagged with the claim**, held until a retention period expires | `FR-278` |
| WS-203–205 | Van Stock · `whaf_van_stock_assignments`, `whaf_van_replenishments`, `whaf_job_consumptions` · `WAREHOUSE_FIELD_SERVICE_VAN_STOCK` etc. | SV / SV / C | assignment: `locationCode`, `technicianName`, `vehicleRefType`, `vehicleRefId`, `assignedAt`, `releasedAt`, `status` · replenishment: `assignmentId`, `transferNumber`, `replenishedAt`, `reconciledAt`, `varianceValue`, `status` · consumption: `assignmentId`, `jobRefType`, `jobRefId`, `itemCode`, `quantity`, `serialNumber`, `consumedAt`, `deviceId` | `technicianUserId` typeahead · `status` select · `varianceOver` number · `consumedFrom`/`To` `date` pair | v1.1. **The van is a `whb_locations` row of type `MOBILE`/`VEHICLE` with `assigned_user_id`** — not a separate table and not a separate reconciliation problem. Replenished by a transfer, consumed at the job, **reconciled at shift end** | `FR-088` `FR-363` |
| WS-206–207 | Assets spares · `whaa_spare_consumptions`, `whaa_asset_item_links` · `WAREHOUSE_ASSETS_SPARE_CONSUMPTION` / `_ASSET_ITEM_LINK` | C / C | consumption: `complaintRefType`, `complaintRefId`, `assetRefId`, `itemCode`, `quantity`, `serialNumber`, `issuedAt`, `issuedByName`, `movementSequenceNo` · link: `itemCode`, `serialNumber`, `assetRefId`, `capitalisedAt` | `itemId` typeahead · `assetRefId` text · `issuedFrom`/`To` `date` pair | v1.1. **The boundary, stated:** warehouse owns the spare while it is stock; assets owns it once it is capitalised onto an asset. `whaa_asset_item_links` is where custody changes hands | `FR-364` |

**Mobile for §6:** `screens/whadCounterSale` (**the counter is often a tablet** — the keyboard-first
flow degrades to a scan-first flow and the behaviour is identical), `screens/whasMaterialRequest`
(a technician raises and receives a request from the bay), `screens/whafVanStock` (**the van
reconciliation is the mobile flow, not a mirror of a web one** — the technician is never at a desk),
`screens/whaaSpareConsumption` (issued against a complaint in the field).
`none`, stated with the reason: WS-195 and WS-239 (catalogues maintained by the parts manager), WS-196/197
(OEM integration, desk), WS-198 and WS-202 (v2 claim administration), WS-200/201 (reports).

### 6.9 The nine RF screens — WS-229 … WS-237

`FR-217` names them at the same time as the web screens, because *"the prior product shipped ~65 web
operations screens and **zero** mobile screens; a WMS without a handheld is a stock ledger with a web
form"*. `FR-220`: they are a **separate screen family** from `EntityListScreen`, which is the wrong
base for one-handed, gloved operation.

**The interaction contract, applied to all nine** (`FR-219`): one active input · scan advances · no
free text where a scan exists · no mouse · no modal stack. **Scan-to-response under 300 ms**
(`FR-424`) or the operator stops trusting the system and works ahead of it.

| id | Screen | Backs | Offline behaviour (`FR-221`, decided per screen) | Posts through |
|---|---|---|---|---|
| WS-229 | RF Receive | WS-075/WS-076 | queued writes with a per-scan client id | `POST /movements` |
| WS-230 | RF Putaway | WS-082 | **read-cached** list; queued writes | `POST /movements` |
| WS-231 | RF Move | WS-038, WS-042 | queued writes | `POST /movements` |
| WS-232 | RF Pick | WS-102 | **read-cached** list; queued writes | `POST /movements` |
| WS-233 | RF Pack | WS-103/WS-104 | online-only (carton weight and photo need the device) | `POST /movements` |
| WS-234 | RF Ship | WS-105 | online-only (dispatch is the relief event; it must not be replayed blind) | `POST /movements` |
| WS-235 | RF Cycle Count | WS-094/WS-095 | queued writes | count API, then `POST /movements` at post |
| WS-236 | RF Stock Enquiry | WS-042, WS-071 | read-cached | read-only |
| WS-237 | RF Task List | WS-059 | read-cached | task API |

**v1 is online-only and says so** (`FR-047`). The offline *hooks* land in v1 anyway and cost nothing:
a client-generated transaction id, a device-supplied `occurred_at`, and duplicate rejection on the
client id. Adding them later means re-versioning every RF endpoint.
`POST /movements/batch` (`FR-034`) is what makes the queued-write decision honest — **N movements,
each with its own idempotency key, each in its own transaction**, so a gun syncing 400 movements after
a shift does not lose 399 because one bin was renamed. WS-055 is where the result array is read.

---

## 7. Reports and registers

Every report here is a **real grid** with a `gridIdentifier`, `grid_column_definitions`,
`filter_definitions`, a `grid_preferences` row and a `COMMON_FILTER_CONFIGS` scope — they are not
special-cased screens. What differs is three things:

1. **They are ledger-style.** They project over `whb_stock_movements` / `whb_stock_movement_lines` /
   `whb_stock_positions` and carry **no `createdByName` / `updatedByName` column, and none in the
   export.** §0.5's rule is grid↔export parity, not a fixed column list.
2. **Their statistics strips are filter-aware and carry no cache name** (`FR-395`).
3. **Several take *parameters* as well as filters** — an as-at date, a bucket set, a period — and a
   parameter is still a `filter_definitions` row and still needs a scope entry, or it is silently
   dropped like any other field.
4. **The branch rollup rule is stated on every branch-grouped report header** (`RH-006`, R22 §1.2.4
   row 11). **Stock and value** roll up to the **`REGISTERED`** branch only, so each site is counted once.
   An as-at report (WS-208, WS-211, WS-212) uses the link at the report date. A period report (WS-210)
   uses the link at each movement's `occurred_at`. **Flows and demand** roll up to the document's own
   branch (the counter sale's `branch_id`, the transfer's two ends). A **branch-filtered** view of a
   shared site shows its whole stock under each linked branch, and the header says *"shared by N
   branches"*. **A total row over a branch-filtered set is refused.** A *linked branches* grouping is a
   separate view, and it is not additive across roles.

**Export follows the visible columns and is a superset of them; a 100,000-row export does not hold a
transaction open** (`FR-400`, `FR-422`). CSV needs a UTF-8 BOM; phone-shaped and code-shaped columns
are text-pinned so Excel does not mangle them.

| id | Report | `gridIdentifier` · Scope | Reads | Columns | Filters and parameters | Exportable | FR |
|---|---|---|---|---|---|---|---|
| WS-208 | Stock on Hand | `wh_rpt_stock_on_hand` · `WAREHOUSE_RPT_STOCK_ON_HAND` | `whb_stock_positions` + masters | **two tabs.** *By item*: `itemCode`, `itemName`, `categoryName`, `ownerName`, `warehouseName`, `onHand`, `reserved`, `available`, `inTransit`, `onOrder`, `baseUomCode`, `value`. *By location*: the full nine-member grain plus quantities | `warehouseId` → `locationId` → `itemId` · `ownerId` · `itemCategoryId` · `stockStatusCode` multiselect · `dutyStatus` select · `lotId` · `nonZeroOnly` boolean (default true) · `expiringWithinDays` select. Branch grouping follows rule 4 (`REGISTERED` at the report date) | Yes | `FR-384` |
| WS-209 | Stock Movement Register | `wh_rpt_movement_register` · `WAREHOUSE_RPT_MOVEMENT_REGISTER` | movement + line | line grain: `occurredAt`, `postingDate`, `movementTypeCode`, `sequenceNo`, `sourceSystem`, `sourceDocumentType`, `sourceDocumentNo`, `reasonCodeName`, `itemCode`, `ownerName`, `locationCode`, `lotCode`, `serialNumber`, `stockStatusCode`, `quantity`, `baseQuantity`, `uomCode`, `unitCost`, `extendedCost`, `actorUserName` | `warehouseId` → `movementTypeCode` → `reasonCodeId` · `itemId` · `lotId` · `serialNumber` text · `locationId` · `ownerId` · `sourceSystem` → `sourceDocumentType` · **`occurredFrom`/`occurredTo` (`date`)** · **`postingDateFrom`/`To` (`dateOnly`)** | Yes | `FR-385` |
| WS-210 | Godown-wise Stock Statement | `wh_rpt_godown_statement` · `WAREHOUSE_RPT_GODOWN_STATEMENT` | movements aggregated per period | `warehouseName`, `itemCategoryName`, `itemCode`, `itemName`, `openingQuantity`, `openingValue`, `inwardQuantity`, `inwardValue`, `outwardQuantity`, `outwardValue`, `closingQuantity`, `closingValue` | **parameters:** `periodId` **or** `fromDate`/`toDate` (`dateOnly` pair) · `companyId` → `branchId` → `warehouseId` · `itemCategoryId` · `ownerId`. `branchId` groups by rule 4 — the `REGISTERED` branch at each movement's `occurred_at` | Yes | `FR-386` |
| WS-211 | Stock Valuation (as-at) | `wh_rpt_valuation` · `WAREHOUSE_RPT_VALUATION` | ledger + `whb_cost_layers` | `itemCode`, `ownerName`, `warehouseName`, `lotCode`, `quantity`, `unitCost`, `value`, `method`, `currencyCode` | **parameter `asAtDate` (`dateOnly`, required)** · `companyId` → `warehouseId` → `itemCategoryId` · `ownerId` · `method` select · `valuedOnly` boolean. Branch grouping follows rule 4 (`REGISTERED` at `asAtDate`) | Yes | `FR-387` `FR-328` |
| WS-212 | Stock Ageing | `wh_rpt_ageing` · `WAREHOUSE_RPT_AGEING` | `whb_stock_positions` + snapshots | `itemCode`, `warehouseName`, `ownerName`, `bucket0_30`, `bucket31_60`, `bucket61_90`, `bucket91_180`, `bucket181_365`, `bucketOver365`, each with a quantity **and a value**, `lastOutwardMovementAt` | **parameter `asAtDate`** · `warehouseId` → `itemCategoryId` → `itemId` · `ownerId`. The six bucket columns are fixed, so there is no bucket-set filter (`RB-008`). Branch grouping follows rule 4 (`REGISTERED` at `asAtDate`) | Yes | `FR-388` `FR-162` |
| WS-213 | Adjustment Register | `wh_rpt_adjustment_register` · `WAREHOUSE_RPT_ADJUSTMENT_REGISTER` | movements with adjustment types | `postingDate`, `adjustmentNumber`, `reasonCodeName`, `warehouseName`, `itemCode`, `quantity`, `valueImpact`, `actorUserName`, `approvedByName` | `warehouseId` → `reasonCodeId` · `actorUserId` typeahead · `approvedBy` typeahead · `postingDateFrom`/`To` (`dateOnly`) · `valueImpactMin`/`Max` | Yes | `FR-389` |
| WS-214 | Count History & Variance | `wh_rpt_count_variance` · `WAREHOUSE_RPT_COUNT_VARIANCE` | `wh_counts` + `wh_count_lines` | `countNumber`, `countType`, `warehouseName`, `zoneLocationCode`, `countedByName`, `countedAt`, `itemCode`, `bookQuantity`, `countedQuantity`, `varianceQuantity`, `variancePct`, `varianceValue`, `recountSequence`, `isWithinTolerance` | `warehouseId` → `programId` → `countedBy` typeahead · `countType` select · `hasVariance` boolean · `countedFrom`/`To` (`date`) · `includeRecounts` boolean | Yes | `FR-390` |
| WS-215 | Low & Insufficient Stock | `wh_rpt_low_stock` · `WAREHOUSE_RPT_LOW_STOCK` | positions + `whb_item_site_settings` + `wh_insufficient_stock_log` | **three tabs:** *Low stock* (`itemCode`, `warehouseName`, `onHand`, `available`, `reorderPoint`, `safetyStock`, `shortfall`, `suggestedQuantity`) · *Insufficient-stock breaches* · *Replenishment suggestions* | `warehouseId` → `itemCategoryId` → `itemId` · `ownerId` · `belowSafetyOnly` boolean · `occurredFrom`/`To` (breaches tab) | Yes | `FR-391` `FR-015` |
| WS-216 | Operational KPIs | `wh_rpt_kpis` · `WAREHOUSE_RPT_KPI` | lifecycle timestamps; `wh_kpi_snapshots` **only where proved slow** | `metricCode`, `metricName`, `warehouseName`, `ownerName`, `periodLabel`, `value`, `unit`, `target`, `variance` | `warehouseId` → `ownerId` → `metricCode` multiselect · `periodFrom`/`To` (`dateOnly`) · `granularity` select (day/week/month) | Yes | `FR-392` `FR-394` |
| WS-217 | Parts KPIs | `wh_rpt_parts_kpis` · `WAREHOUSE_RPT_PARTS_KPI` | ledger + `wh_demand_history` + `wh_insufficient_stock_log` | `fillRate`, `serviceLevel`, `stockTurn`, `obsolescencePct`, each by `warehouseName` and period | as WS-216 | Yes | `FR-393` |
| WS-218 | Traceability | `wh_rpt_traceability` · `WAREHOUSE_RPT_TRACEABILITY` | movements + `whb_transformations` | **two directions.** *Forward*: lot → every shipment and consignee that received it. *Backward*: shipment or serial → supplier lot and receipt | **parameters:** `direction` select (required) · `lotId` **or** `serialNumber` **or** `shipmentId` (at least one required — the query is refused, not silently unbounded) · `warehouseId` · `occurredFrom`/`To` | Yes | `FR-105` `FR-396` |
| WS-219 | Stock-to-GL Reconciliation | `wh_rpt_stock_to_gl` · `WAREHOUSE_RPT_STOCK_TO_GL` | movements + `whb_accounting_handovers` | `periodCode`, `companyName`, `warehouseName`, `openingValue`, `receiptsValue`, `adjustmentsValue`, `revaluationsValue`, `issuesValue`, `closingValue`, `handedOverValue`, `pendingValue`, `rejectedValue`, `difference` | `companyId` → `warehouseId` → `periodId` · `postingDateFrom`/`To` (`dateOnly`) · `differenceOnly` boolean | Yes | `FR-247` |
| WS-220 | In-transit Ageing | `wh_rpt_in_transit_ageing` · `WAREHOUSE_RPT_IN_TRANSIT_AGEING` | positions at per-transfer transit locations | `transferNumber`, `sourceWarehouseName`, `destinationWarehouseName`, `itemCode`, `quantity`, `value`, `dispatchedAt`, `ageDays` | `sourceWarehouseId` → `destinationWarehouseId` · `ageOverDays` select (7 · 15 · 30 · 60 · 90 · 180 · 365 days — the one ageing list, `RB-008`) · `dispatchedFrom`/`To` | Yes | `FR-149` `FR-335` |
| WS-221 | Expiry & Shelf-life Register | `wh_rpt_expiry` · `WAREHOUSE_RPT_EXPIRY` | positions + `whb_lots` | `itemCode`, `lotCode`, `warehouseName`, `locationCode`, `ownerName`, `quantity`, `manufactureDate`, `expiryDate`, `bestBeforeDate`, `useByDate`, `retestDate`, `daysToExpiry`, `shelfLifeRemainingPct`, `stockStatusCode` | `warehouseId` → `itemCategoryId` → `itemId` · `ownerId` · `expiringWithinDays` select · `expiredOnly` boolean · `expiryFrom`/`To` (`dateOnly`) | Yes | `FR-160` `FR-161` |
| WS-222 | Consolidated Valuation | `wh_rpt_consolidated_valuation` · `WAREHOUSE_RPT_CONSOLIDATED_VALUATION` | `whb_stock_positions` + `whb_external_stock_snapshots` | `sourceSystem` (**WAREHOUSE / ACCESSORIES**), `itemCode`, `warehouseName`, `quantity`, `value`, `valuationMethod` | `sourceSystem` select · `asAtDate` (`dateOnly`) · `warehouseId` · `itemCategoryId` | Yes | `FR-397` |
| WS-223 | Install Health Signals | `wh_rpt_health` · `WAREHOUSE_RPT_HEALTH` | jobs, queues, positions | `signalCode`, `signalName`, `value`, `baseline`, `status`, `lastCheckedAt` — movements posted today against a baseline · handovers stuck pending · counts overdue · negative positions · orphaned reservations · dead outbox deliveries · failed jobs | `signalCode` multiselect · `warehouseId` · `failingOnly` boolean | Yes | `FR-398` |
| WS-224 | Stock As-At | `wh_rpt_stock_as_at` · `WAREHOUSE_RPT_STOCK_AS_AT` | **the ledger, never balances** | the nine-member grain + `quantityOnHand` at the parameter date | **parameter `asAtDateTime` (required)** · `warehouseId` → `itemId` · `ownerId` · `locationId` | Yes | `FR-013` `FR-328` |
| WS-225 | Coexistence Reconciliation | `wh_rpt_coexistence` · `WAREHOUSE_RPT_COEXISTENCE` | `whb_item_external_refs` + `whb_external_stock_snapshots` + `whb_category_stocking_ownership` | `itemCode`, `accessoryExternalId`, `mapStatus`, `warehouseQuantity`, `accessoriesQuantity`, `difference`, `stockingSystemOfRecord`, **`isViolation`** | `mapStatus` select · `isViolation` boolean (default true) · `asAtDate` (`dateOnly`) · `itemCategoryId` | Yes | `FR-368` `FR-369` `FR-370` `D-9` |
| WS-226 | Stock by MRP | `whin_rpt_stock_by_mrp` · `WAREHOUSE_INDIA_RPT_STOCK_BY_MRP` | positions + `whb_lots.mrp` | `itemCode`, `mrp`, `warehouseName`, `quantity`, `value` | `warehouseId` → `itemId` · `mrpFrom`/`mrpTo` number pair · `asAtDate` | Yes | `FR-321` — **and note `OD-10`: MRP belongs on the lot, not in the position key.** The report groups by the lot's MRP; it does not imply a tenth key member |
| WS-243 | Location Utilisation | `wh_rpt_location_utilisation` · `WAREHOUSE_RPT_LOCATION_UTILISATION` | `whb_locations` capacity block + `whb_stock_positions` | `locationCode`, `rollupLevel` (location / rack / aisle / zone / site), `warehouseName`, `weightCapacity`, `weightOccupied`, `volumeCapacity`, `volumeOccupied`, `unitCapacity`, `unitsOccupied`, `lpnCapacity`, `lpnsOccupied`, `utilisationPct` | `warehouseId` → `zoneLocationId` · `rollupLevel` select · `utilisationOver` number | Yes | `FR-471` — **v3 · P6** (`RC-009`). **The analysis, never an optimiser**: it recommends no move |
| WS-227 | Custody & Insured Value | `wh3_rpt_custody_value` · `WAREHOUSE_3PL_RPT_CUSTODY_VALUE` | positions where `owner_type != OWN` | `clientName`, `ownerName`, `warehouseName`, `itemCode`, `quantity`, **`insuredValue`**, `declaredValueBasis` | `clientId` → `warehouseId` · `asAtDate` | Yes | `FR-115` `FR-112` — **a different number, on a different report, never mixed into the inventory asset** |

**Mobile for §7:** `screens/whStockOnHandReport` and `screens/whExpiryReport` only — an operator on
the floor asks *"what have I got"* and *"what is about to expire"*, and both answer with dropdown
filters alone. **Every other report is `none`**, and the reason is the same for all of them: they are
wide, parameterised and printed, and `ListHeader` supports neither a date parameter nor a column set
this wide. Recorded per `FR-218` rather than left silent.

#### WS-244 · Metric Targets — v1 · P2

`/warehouse/reports/metric-targets` · **Department** · `wh_metric_targets` · `WAREHOUSE_METRIC_TARGET` ·
`wh_metric_targets:*` · v1 · P2 · `FR-470` · table `V510091`, the metric catalogue
`whb_metric_definitions` at `V500048`, permissions and dependencies `V511211` + `V511241` · caches:
statistics `—` (filter-aware, `FR-395`), no dropdown.

**The target WS-216 measures against** (`RC-007`).
- A row is a metric × optional warehouse × optional owner × period grain, with a target value and
  effective dates.
- WS-216's `target` and `variance` read the effective row. A metric with no row renders a blank
  variance, never zero.

**Columns:** `metricCode` · `metricName` · `warehouseName` · `ownerName` · `periodGrain` · `targetValue` ·
`unit` · `effectiveFrom` · `effectiveTo` · audit quartet + names.
**Filters:** `metricCode` select (fetched from `whb_metric_definitions`) · `warehouseId` · `ownerId` ·
`periodGrain` select.
**Export:** visible + both audit names.
**Modals:** single-tab add/edit. The view is `ViewModalBase`, rendering the metric's frozen definition
through the platform metric explainer (`definition_text_key`).
**Actions:** row View / Edit / Delete. Toolbar Add / Export / Grid config / Help.
**Mobile:** `none` — a target is a desk master. Stated per `FR-218`.

---

## 8. Dashboards and widgets

### 8.1 The constraint that must be widened first, and how

`widget_definitions.chk_module` **does not admit `warehouse`.** Verified:

```sql
-- platform/backend/src/main/resources/db/migration/V557__Extend_widget_definitions_module_constraint.sql:16-18
ALTER TABLE widget_definitions DROP CONSTRAINT IF EXISTS chk_module;
ALTER TABLE widget_definitions ADD CONSTRAINT chk_module
    CHECK (module IN ('platform','dealer','shared','accessories','assets','insurance','services'));
```

The **first warehouse widget insert fails at runtime with SQLSTATE `23514`** (R1 `C-014`).
`V557` supersedes `V234:36`, `V276:9` and `insurance/V50009:8` — the constraint has been dropped and
rebuilt by a **hardcoded** list **three times**, and each rebuild silently dropped whatever a later
module had added.

**`WHB-70` / `V500200` is the widening, and it must read the existing definition and union, never
restate a hardcoded list** (`FR-377`, `FR-378`). Restating is how `V557` erased `V276`'s additions.
The same migration is where `'logistics'` is added too, because `FR-346` reserves the namespace in v1
and retro-granting a value invented in v3 is hand work.

`chk_global_setting_module` **already admits `WAREHOUSE`** and is used free (`FR-379`); a defensive
merge migration ships anyway in case a client database diverged.

### 8.2 The widget set — WS-228, v3 · P6

`FR-399` places the real-time operations dashboard at v3, **after** the constraint is widened in v1
and after `FR-394`'s twenty-nine metrics have been computed from the ledger for long enough to know
which of them are provably too slow to compute live. `FR-394` is explicit that a pre-aggregated
snapshot table (`wh_kpi_snapshots`) is added **only for what is proved slow, only after measuring**;
the repo's own best precedent is a derived-at-read-time model that deliberately does not cache.

| Widget | `module` | Scope | Reads | Notes |
|---|---|---|---|---|
| Stock value by site | `warehouse` | company → branch → warehouse | `whb_stock_positions` + `whb_cost_layers` | Non-own stock excluded (`L-14`) |
| Movements today vs baseline | `warehouse` | warehouse | `whb_stock_movements` | Also WS-223's first health signal |
| Dock-to-stock | `warehouse` | warehouse | `wh_dock_appointments.arrived_at` → putaway completion | Impossible without `arrived_at`, which is why the dock schema is v1 |
| Orders late against promise | `warehouse` | warehouse → owner | `wh_demand_orders.promised_ship_at` | |
| Pick productivity | `warehouse` | warehouse → user | `whb_tasks` timestamps | Honest actuals, **not an engineered standard** (`FR-228`) |
| Inventory record accuracy | `warehouse` | warehouse | `wh_counts` variance | |
| Handovers pending / rejected | `warehouse` | company | `whb_accounting_handovers` | The finance controller's tile |
| Expiring within 30 days | `warehouse` | warehouse → owner | positions + lots | |
| Negative available (must be 0) | `warehouse` | warehouse | positions | A non-zero value is an incident |
| Outbox dead letters | `warehouse` | — | `whb_outbox_deliveries` | Support tile |

**Every one of these is scoped by the three-mode view pattern and by owner grants** (`FR-404`,
`FR-114`) — a widget that ignores the record-level guard leaks across branches and owners exactly
where nobody is looking. **Empty state names the provider reason**; a blank tile is indistinguishable
from a broken one.
**Mobile:** the platform widget framework already renders on mobile; the warehouse widget set inherits
that with no per-widget work. Where a widget cannot be scoped on mobile it is not shown, and the tile
is absent rather than empty.

---

## 9. Grid config migration checklist

Four things are always got wrong. Each has cost a rebuild cycle in this monorepo, and each is
checkable by a grep before the migration is written.

### 9.1 `grid_column_definitions` **and** `filter_definitions` — and the table that does not exist

**There is no `grid_filter_definitions` table.** The real table is `filter_definitions`, created by
`platform/backend/src/main/resources/db/migration/V229__Add_filter_definitions_table.sql:8`.
Inserting into the wrong name fails at Flyway and **crash-loops the backend**.

```bash
grep -rln "CREATE TABLE.*grid_filter_definitions" --include=*.sql . | grep -v node_modules | wc -l   # → 0
grep -rln "CREATE TABLE.*filter_definitions"      --include=*.sql . | grep -v node_modules          # → platform/…/V229__…
```

Real column lists, so nothing is guessed:

```sql
-- grid_column_definitions (V18__Add_grid_preferences_system.sql:43-64)
grid_identifier, column_key, display_name, data_type, is_sortable, is_filterable, is_required,
is_resizable, default_visible, default_width, min_width, max_width, position,
alignment CHECK (alignment IN ('left','center','right')), format_pattern, tooltip_text
UNIQUE (grid_identifier, column_key)

-- filter_definitions (V229:8-21)
grid_identifier, filter_key, display_name, filter_type DEFAULT 'text', position,
is_required, default_visible, is_active
UNIQUE (grid_identifier, filter_key)
```

`column_key` **must equal** the frontend column key, which **must equal** the `columnTranslations` key
the page builds (`departments/page.tsx:92-106`). A mismatch renders a blank header, not an error.

### 9.2 `grid_preferences.default_filters` **AND** `default_columns` — both, as `jsonb`

`default_columns` is on the table from the start (`V18:12`, `NOT NULL DEFAULT '[]'`);
`default_filters` was added later (`V229:51`) and is **nullable**, which is exactly why it gets
forgotten. **Setting `filter_definitions.default_visible = true` alone does not populate the default
filter strip** — `useGridPreferences` reads `defaultFilters` from `grid_preferences.default_filters`.

```sql
INSERT INTO grid_preferences (grid_identifier, grid_name, grid_description,
                              default_columns, default_filters,
                              default_order_by, default_order_direction, default_page_size)
VALUES ('whb_items', 'Items', 'Warehouse item master',
        '["itemCode","sku","ownerName","name","itemTypeCode","categoryName","baseUomCode","lotControlMode","serialControlMode","isReceivable","isIssuable","lifecycleStatus","onHandTotal","isActive"]'::jsonb,
        '["ownerId","categoryId","itemTypeCode","sku","itemCode","name","barcode","lifecycleStatus","isActive"]'::jsonb,
        'itemCode', 'asc', 20)
ON CONFLICT (grid_identifier) DO NOTHING;
```

Compare against the shipped `departments` and `service_vehicles` rows before shipping.
Both casts are `::jsonb` — a `jsonb` written with `REPLACE` on a text literal is a known whitespace
trap in this repo and must not be used to patch these arrays later.

### 9.3 `filter_definitions.position` collisions

`position` is `NOT NULL DEFAULT 0` with **no uniqueness**, so two filters at the same position render
in an arbitrary order that changes between queries. **Number every warehouse grid's filters from 1,
contiguously, in the order the strip should read**, and when a later migration inserts a filter into
an existing grid, renumber the tail in the same migration rather than reusing a number.

```sql
-- before adding a filter to a shipped grid
SELECT filter_key, position FROM filter_definitions
 WHERE grid_identifier = 'whb_items' ORDER BY position;
```

### 9.4 Required columns brick the save

`grid_column_definitions.is_required = true` means the user cannot hide the column — and if a
*required* column is not in `grid_preferences.default_columns`, **every save of that user's grid
preferences fails**, silently, for that grid only. Mark `is_required` on **at most one identity
column per grid** (`itemCode`, `grnNumber`, `sequenceNo`, …) and assert it is present in
`default_columns` in the same migration.

```sql
-- the assertion to include in every warehouse grid migration
DO $$
DECLARE missing text;
BEGIN
  SELECT string_agg(cd.column_key, ', ') INTO missing
    FROM grid_column_definitions cd
    JOIN grid_preferences gp ON gp.grid_identifier = cd.grid_identifier
   WHERE cd.grid_identifier = 'whb_items'
     AND cd.is_required
     AND NOT (gp.default_columns ? cd.column_key);
  IF missing IS NOT NULL THEN
    RAISE EXCEPTION 'required column(s) % missing from default_columns', missing;
  END IF;
END $$;
```

### 9.5 The rest of the per-grid migration, in order

1. `grid_column_definitions` inserts — `ON CONFLICT (grid_identifier, column_key) DO NOTHING`.
2. `filter_definitions` inserts — `ON CONFLICT (grid_identifier, filter_key) DO NOTHING`, contiguous
   positions.
3. `grid_preferences` insert — **both** JSONB arrays — `ON CONFLICT (grid_identifier) DO NOTHING`.
4. The required-column assertion of §9.4.
5. Menu leaf under the module's L2 node, **guarded by `WHERE NOT EXISTS`, never `ON CONFLICT`** — the
   menu table has no unique constraint on `(name, parent_id, menu_level)` and a Flyway retry
   duplicates the row (`FR-410`).
6. `menu_translations` for **`en`, `fr` and `hi`** — three locales, following accounting, not the
   older `en`-only modules (`FR-431`).
7. **Outside the migration, and neither is optional:** the `COMMON_FILTER_CONFIGS.{SCOPE}` block in
   `filterUtils.ts`, and any `dropdown.*` cache name in `CacheConfiguration.java`.

Every warehouse migration is **forward-only, additive and individually idempotent**; a released
migration is never edited in place (`FR-374`).

---

## 10. Permissions

### 10.1 The shape

`@PreAuthorize` on **every** controller method, in `resource:action` form (`FR-401`, CLAUDE.md
CRITICAL #1). The resource is the table name; the actions are:

| Action | `@PreAuthorize` |
|---|---|
| view | `hasAuthority('<table>:view')` |
| create | `hasAuthority('<table>:create')` |
| edit | `hasAuthority('<table>:edit')` |
| delete | `hasAuthority('<table>:delete')` |
| export | `hasAuthority('<table>:export') or hasRole('ADMIN')` |

**Never name a warehouse permission `wms_*` or `scc_*`** (`D-3`, `FR-401`). `platform/…/V528:37,57,59`
and `V663:17-19` still carry hardcoded `wms_*` / `scc_*` / `warehouse-*` exclusions from a deleted
earlier module. Those migrations have already run, so they grant a new module nothing — but a new
`wms_`-prefixed permission would inherit a decision nobody took.

### 10.2 The verb permissions — the ones a `view/create/edit/delete/export` list does not cover

Every one of these gates a transition modal named in §2–§6. **A transition with no verb permission is
a transition anybody with `:edit` can perform**, which is the failure `FR-408` names.

| Permission | Gates | Screen |
|---|---|---|
| `warehouse:movements:post` | `POST /api/warehouse/movements` | the port (`FR-043`) |
| `warehouse:movements:reverse` | `POST /movements/{id}/reverse` | WS-040 |
| `warehouse:movements:simulate` | `POST /movements/simulate` | WS-040 toolbar |
| `warehouse:movements:view` | `GET /movements` incl. the lineage query | WS-040 |
| `whb_stock_movements:approve` | approval of `requires_approval` movement types | WS-040 |
| `whb_stock_periods:close` · `:reopen` · `:override` | soft close, close, reopen, soft-close override | WS-045, WS-046 |
| `whb_locations:block` | block / unblock a location | WS-017 |
| `whb_stock_positions:rebuild` | the `L-4` rebuild check | WS-042 |
| `whb_reservations:release` · `:extend` | reservation release and expiry extension | WS-047 |
| `whb_accounting_handovers:retry` | retry a rejected envelope | WS-052 |
| `whb_inbound_messages:reprocess` | reprocess a failed inbound message | WS-053/054 |
| `whb_outbox:replay` · `whb_outbox_subscriptions:reset_cursor` | replay from cursor, reset a subscriber | WS-056, WS-057 |
| `whb_import_batches:validate` · `:apply` · `:reverse` | the three import verbs — **validate persists nothing** | WS-065, WS-150 |
| `whb_item_supersessions:merge` | `MERGE_STOCK` treatment, which posts a movement | WS-030 |
| `whb_job_runs:trigger` | run a scheduled job now | WS-064 |
| `wh_purchase_orders:approve` · `:cancel` | PO approval and the cancel cascade | WS-072 |
| `wh_goods_receipts:post` · `wh_receipt_reversals:approve` | receipt posting and reversal approval | WS-076, WS-078 |
| `wh_quality_inspections:disposition` | release / reject / RTV / scrap — **QA-role gated** | WS-080 |
| `wh_stock_adjustments:approve` | value- and quantity-thresholded approval | WS-089 |
| `wh_transfer_orders:dispatch` · `:receive` | the two legs that post movements. **Round 4:** the depart leg posts through the transfer's shipment (`wh_shipments:dispatch`, `RJ-003`); `:dispatch` stays seeded (`GAP-REGISTER-R4.md` §3.3). The transfer's other verbs are in the round-4 table below | WS-090 |
| `wh_holds:place` · `:release` · `:mass` | plus the per-hold-type `release_permission` | WS-092 |
| `wh_counts:freeze` · `:approve` · `:post` | count lifecycle | WS-094 |
| `wh_blocked_movements:force` | force a rejected physical move, with approval | WS-097 |
| `wh_demand_orders:allocate` · `:release` · `:hold` · `:cancel` · `:short_pick` | outbound transitions | WS-099 |
| `wh_shipments:dispatch` | **the inventory-relief event** | WS-105 |
| `wh_print_jobs:void` · `wh_print_templates:publish` | void a print, publish a template version | WS-131, WS-132 |
| `wh_return_receipts:disposition` | restock / quarantine / scrap | WS-135 |
| `wh_revaluations:approve` · `wh_landed_cost_documents:apply` | valuation documents | WS-147, WS-148 |
| `wh_opening_stock_batches:post` · `:reverse` · `wh_cutover_checklists:certify` | go-live | WS-150, WS-151 |
| `wh3_billing_runs:approve` · `wh3_accessorials:approve` · `wh3_sla_breaches:waive` | 3PL money | WS-162, WS-163, WS-168 |
| `whin_eway_bills:generate` · `:part_b` · `:extend` · `:cancel` · `whin_delivery_challans:generate` | the India documents | WS-178, WS-179 |
| `whad_counter_sales:create` · `whas_material_requests:issue` | adapter transitions | WS-194, WS-199 |

**Round-2 addition (`H-001`) — the P5 verb permissions.** The 37 rows above gate P0–P2-IN plus exactly
three P5 transitions. §4 enumerates at least 28 further 3PL transitions in its own **Actions** cells
and gave none of them a string, so today `wh3_billing_runs:approve` exists while `:rate`,
`:emit_ar_handover` and `:cancel` do not — the operator allowed to edit a draft run is also allowed to
cancel an invoiced one, and `wh3_disputes:uphold` is ungated, so the person who raises a credit can
grant it. `FR-408` (second-user approval above a threshold) is unenforceable without them. The
twenty-five strings below are derived from §4's Actions cells in `<table>:<verb>` form per §10.1 and
are **seeded by `P5-01`** (`V531000`–`V531099`, the 3PL permission migration), which also inserts their
`permission_dependencies` rows per §10.3.

| Permission | Gates | Screen |
|---|---|---|
| `wh3_clients:onboard` · `:suspend` · `:terminate` | client lifecycle — suspend stops billable-event capture, terminate is terminal | WS-155 |
| `wh3_client_onboarding_tasks:assign` · `:complete` · `:reopen` | onboarding checklist transitions | WS-157 |
| `wh3_rate_cards:clone_version` · `:activate` · `:expire` | rate-card versioning — **`:activate` is the money-affecting one** | WS-159 |
| `wh3_billable_events:reverse` | reverse a captured event (never delete it) | WS-160 |
| `wh3_storage_billing_periods:compute` · `:approve` · `:recompute` | storage accrual; `:recompute` after approval is the escalated verb | WS-161 |
| `wh3_billing_runs:rate` · `:emit_ar_handover` · `:cancel` | the three transitions `:approve` does not cover | WS-162 |
| `wh3_accessorials:raise` · `:reject` | ad-hoc charge lifecycle beside the existing `:approve` | WS-163 |
| `wh3_disputes:raise` · `:investigate` · `:uphold` · `:reject` | **`:raise` and `:uphold` must not be held by one role** — that is the credit-self-grant | WS-164 |
| `wh3_sla_breaches:confirm` · `:post_penalty` | beside the existing `:waive`; `:post_penalty` writes money | WS-168 |
| `wh3_ar_handovers:retry` | retry a rejected AR envelope — the same button as `whb_accounting_handovers:retry` above, which is how the asymmetry was found | WS-170 |
| `wh3_freight_billing_rules:end_date` | close a rule without deleting it | WS-165 |
| `wh3_clients:portal_access` | the **`PORTAL` grant** WS-172 describes as *"a permission surface over the existing screens"* and which had no name; owner-bound, read-only by construction | WS-172 |

**The 27 P5/P6 screens outside §4 are not covered by this table, and that is a known hole.** They sit
under headers whose sixth column is *"Notes"*, not *"Actions"* — carriers, channels, NDR, COD, RTO,
returns grading, obsolescence, recalls, NRV, replenishment, three-way match, cross-dock, weighing,
labour — so for those the **verb itself** is not yet enumerated, only described in prose. Each owning
task enumerates its verbs before its controller is written; that is the same work, one step earlier.
`X-014` records the P3/P4 half of this.

**Round-4 addition — `RJ-005`, `RK-001`, `RJ-011`, `RG-001`, `RH-002` and the two new resources**
(`GAP-REGISTER-R4.md` §2, §3.3, §4.0). The §0.11 round-4 ladders name every verb below, and this table is
the same list read from the other side. The seed column comes from the register: **P1 verbs ride
`P1-20`'s `V511000`/`V511001`**, **P2+ verbs each claim one `WH-206` pair**, adapter verbs ride their own
bands, and **base verbs ride `P0-15`'s `V501000`**. Each verb gets its `→ :view` dependency row (§10.3).

| Permission | Gates | Screen | Seeded by |
|---|---|---|---|
| `wh_transfer_orders:request` · `:approve` · `:reject` · `:report_variance` · `:cancel` | **request** (destination-scoped) · approve and part-approve, reject (source-scoped, `FR-408`) · the variance close · cancel, which posts `TRANSFER_RETURN` in transit. Seeded beside the existing `:dispatch` and `:receive` | WS-090 | `P2-02` · `V511202` + `V511232` |
| `wh_receiving_sessions:complete` · `:cancel` | session close | WS-075 | `P1-20` · `V511000` + `V511001` |
| `wh_goods_receipts:cancel` · `wh_receipt_reversals:post` | a draft GRN's cancel; the reversal's post leg beside the existing `:approve` | WS-076, WS-078 | `P1-20` |
| `wh_quality_inspections:approve` | **scrap-disposition approval**, with `:approve` semantics and approver ≠ actor (`FR-164`, `FR-408`) | WS-080 | `P1-20` |
| `wh_stock_adjustments:submit` · `:reject` · `:post` · `:cancel` | beside the existing `:approve` | WS-089 | `P2-01` · `V511201` + `V511231` |
| `wh_counts:generate` · `:recount` · `:cancel` | beside the existing `:freeze` · `:approve` · `:post`; cancel restores location status | WS-094 | `P2-04` · `V511203` + `V511233` |
| `wh_shipments:cancel` · `:confirm_delivery` | cancel **only before `DISPATCHED`**; delivery confirmation (`FR-447`) | WS-105 | `P2-10` · `V511204` + `V511234` |
| `wh_return_receipts:post` · `:reverse` · `:approve` · `wh_rmas:approve` · `:match` · `:expire` · `:cancel` | return posting, the pre-disposition reversal, **scrap approval** (approver ≠ actor, `FR-273`), the RMA lifecycle | WS-135, WS-136 | `P2-12` · `V511205` + `V511235` |
| `wh_supplier_returns:approve` · `:close` · `:cancel` · `wh_reconciliation_cases:resolve` | supplier-return transitions — pick and dispatch are the demand path's (`RJ-003`), so there is no supplier-return pick or dispatch verb — and the case resolution | WS-084, WS-083 | `P2-13` · `V511206` + `V511236` |
| `wh_replenishment_suggestions:accept` · `:reject` | suggestion lifecycle | WS-141 | `P2-15` · `V511207` + `V511237` |
| `wh_work_orders:release` · `:issue` · `:complete` · `:cancel` | v1.1 | WS-144 | `P3-11` · `V511208` + `V511238` |
| `whas_material_requests:reserve` · `:return_unused` · `:cancel` | beside the existing `:issue` | WS-199 | `P2-26` · `V521100`+ |
| `whb_accounting_handovers:void` | `REJECTED → VOIDED`, approver ≠ requester (`RJ-011`) | WS-052 | `P0-15` · `V501000` |
| `warehouse:warehouses:change_registration` | *Change registration*, maker–checker (`FR-408`, `D-14` item 4) | WS-016 | `P0-15` · `V501000` |
| `<resource>:view:all` · `<resource>:view:branch` | **the tier pair on every management resource** (`RH-002`). ADMIN and AUDITOR hold `:all`; Branch Admin holds `:branch` and never `:all`; operational bundles hold `:branch`. It is resolved through platform's `BranchScopeService` to the allowed warehouse set (§10.4) | every management screen | `P0-15` · `V501000`/`V501001`; `P1-20` · `V511000`/`V511001` |
| `wh_trade_portal_users:view` · `:create` · `:edit` · `:delete` · `:export` | the new resource | WS-240 | `P5-08` · `V511209` + `V511239` |
| `wh_approval_levels:view` · `:create` · `:edit` · `:delete` · `:export` | the new resource | WS-241 | `P2-23` · `V511210` + `V511240` |
| `whb_warehouse_grants:view` · `:create` · `:edit` · `:delete` · `:export` | the new resource (`RA-001`) | WS-238 | `P0-15` · `V501000` + `V501001` |
| `whb_stock_movements:post_backdated` | posting into a `SOFT_CLOSED` period — `mgr1`'s `WH-SC-022` authority, distinct from `whb_stock_periods:override` (`RA-007`) | the port (`P0-08`) | `P0-15` · `V501000` |
| `whb_outbox:view` | reading the outbox and its deliveries (`RA-007`) | WS-056 | `P0-15` · `V501000` |
| `whb_stock_movements:verify` | the ledger-chain verifier (`RC-008`, `RA-005`) | WS-040 | `P0-15` · `V501000` |
| `wh_metric_targets:view` · `:create` · `:edit` · `:delete` · `:export` | the new resource (`RC-007`) | WS-244 | `P2-21` · `V511211` + `V511241` |
| `whad_item_prices:view` · `:create` · `:edit` · `:delete` · `:export` · `:import` · `whad_price_levels:view` · `:create` · `:edit` | the new resources (`RA-002`) | WS-239 | `P2-25` · `V520100`–`V520149` |

### 10.3 `permission_dependencies` — **inserted, never created**

It is a **platform** table, created by
`platform/backend/src/main/resources/db/migration/V248__Create_permission_dependencies_table.sql:17`.
The defensive re-creation in `dealer/…/V20501` is a documented false premise; warehouse **must not
copy it** (`FR-402`, `C-017`).

Real columns (`V248:18-22`):

```sql
id, permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    dependent_permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    dependency_type VARCHAR(20) NOT NULL DEFAULT 'REQUIRED',   -- REQUIRED | OPTIONAL
    description VARCHAR(255)
```

**The column is `dependent_permission_id`, not `depends_on_permission_id`**, and the semantics are
*"granting `permission_id` also grants `dependent_permission_id`"*. Inspect before authoring:

```sql
SELECT p.name, d.name FROM permission_dependencies pd
  JOIN permissions p ON pd.permission_id = p.id
  JOIN permissions d ON pd.dependent_permission_id = d.id LIMIT 5;
```

The warehouse rows, seeded in `V501001` (base) and `V511001` (app), and in-band for 3PL, India and
each adapter:

| Rule | Rows |
|---|---|
| Every non-view action requires its own `:view` | for each resource R and each action A ∈ {create, edit, delete, export}: `(R:A → R:view)` |
| Every verb permission requires its resource's `:view` | `(wh_shipments:dispatch → wh_shipments:view)`, and so on for every row in §10.2 |
| Every document screen requires the masters it renders | `(wh_goods_receipts:view → whb_items:view)`, `(… → whb_locations:view)`, `(… → whb_owners:view)`, `(wh_demand_orders:view → whb_items:view)`, `(whb_stock_positions:view → whb_items:view, whb_locations:view, whb_owners:view)` |
| Every approval requires the execution view, never the reverse | `(wh_stock_adjustments:approve → wh_stock_adjustments:view)`. **The reverse row must not exist** — `FR-408` separates approval from execution and the approver may not be the actor |
| The port's posting permission additionally checks owner grants at runtime | not expressible as a dependency row; it is the `FR-114` resolver (`whb_owner_grants`) |

### 10.4 The role decisions that must be **re-taken**, not inherited

`FR-403`: the deleted prior module's **auditor** and **branch-admin** exclusions were one-shot
migrations that have already run. They grant a new module nothing, so the recorded product decisions
— *"the auditor cannot see warehouse"*, *"branch admin must not hold warehouse view-all"* — are simply
absent and must be taken again, explicitly, in `V501000`/`V511000`:

- **AUDITOR is read-only across everything, including the ledger** (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md`
  §4). It receives every `:view` and every `:export` and **no** `:create`/`:edit`/`:delete` and **no**
  verb permission. It is never a writer.
- **Branch admin holds the branch tier only** (`FR-404`). The three-mode view pattern — view-all,
  view-branch, no view — is implemented **as a record-level guard in the `WHERE` clause of every
  management query**, not as a UI filter, and warehouse-scoped user access participates in the same
  predicate (`FR-405`). A storekeeper at branch A must not adjust branch B's stock, **and a menu
  filter is not a guard.**
- **3PL client users** get a `PORTAL` grant only, owner-bound (`FR-284`, `FR-008`).

### 10.5 The reserved `logistics:*` namespace

`FR-407` and `FR-346`: the `logistics:*` permission namespace **and its dependency rows are reserved in
v1**, in the base permission migration, because retro-granting a permission invented in v3 to every
existing role is hand work nobody budgets for. Reserved alongside it: the Flyway band
**`V524000`–`V524999`** and the table prefix **`log_`**. **No `logistics` migration is written in v1** —
the only v1 artefact is the permission seed and the reservation comment naming `FR-346`.

Reserved rows: `logistics:trips:view|create|edit|dispatch`, `logistics:epod:view|capture`,
`logistics:freight:view|settle`, each with its `→ :view` dependency, all `is_active = false` until the
module ships.

---

## 11. The shared-registry ledger

Two platform files change on **every** warehouse grid, in **every** warehouse module including every
adapter. Neither has a per-module extension point, and that is why **the loose-coupling ratchet can
only ever be *zero commits to `warehouse-base`*, never *zero commits to `platform`*** (`D-10`
corollary, `FR-355`, R7 `G-047`). A contract that claims platform is untouched is false on day one
and, being false, gets ignored — taking the true invariants with it.

Plan the serialisation of these two files rather than discovering it in a merge conflict.

### 11.1 `platform/frontend/src/utils/filterUtils.ts` — `COMMON_FILTER_CONFIGS`

**215 scopes to add**: 195 over warehouse tables + 20 over the report projections of §7.
Computed from the grid list in this document:

```bash
# in warehouse-issues
f=docs/BUILD-SPEC-SCREENS.md
awk '/^### 11.1/,/^### 11.2/' $f | grep -oE '\bWAREHOUSE(_3PL|_INDIA|_DEALER|_SERVICES|_FIELD_SERVICE|_ASSETS)?_[A-Z0-9_]+' \
  | sort -u | wc -l          # → 215
```

Current platform count **213**, computed 2026-09-01 (§0.3). After warehouse: **428**.
**Round 4** adds two v2 grids, WS-240 and WS-241, and one scope each: **217** to add, **430** after
warehouse. **Round 3's fold** adds one v1 grid, WS-238, and its scope `WAREHOUSE_WAREHOUSE_GRANT`: **218**
to add, **431** after warehouse. **Its second lane (`W0-1b`)** adds three grids — WS-239, WS-244 (v1)
and WS-243 (v3) — and their scopes `WAREHOUSE_DEALER_ITEM_PRICE`, `WAREHOUSE_METRIC_TARGET` and
`WAREHOUSE_RPT_LOCATION_UTILISATION`: **221** to add, **434** after warehouse.

