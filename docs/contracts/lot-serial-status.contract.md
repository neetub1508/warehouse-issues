# Functional Contract — Lots, serials, LPNs, holds, duty status and genealogy

> **What this is.** The functional truth for the identity records the ledger moves stock under: the **lot**
> (an entity, its dates and its parties), the **serial** (an entity, never globally unique), the **LPN** (a
> ledger object and the storage-anniversary anchor), the **hold** (one way to hold a lot), **duty status**
> (a registry FK in the position key), **genealogy** recorded at transformation, and the v1.1 GS1 identity
> (SSCC allocation, EPC, Digital Link).
>
> **Status.** Derived 2026-10-23 (v0) for R30 `CP-FR-007` row 4 (`D-17` item a) from
> `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.5 and §6.27, checked against the built code. Not ratified.
> Code disagreements are in §10.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Lot create on first receipt (or by master) → hold / release → expire / retest; serial create → move → sold-to / warranty; LPN create → move (one movement) → close; transformation (kit, repack, decant, split, merge) writes genealogy |
| **Module** | `warehouse-base` (lots, serials, LPNs, duty status, genealogy, GS1); holds (`wh_holds`, WS-091 / WS-092) are owned by [`cycle-count.contract.md`](cycle-count.contract.md) (`CCT-T1-20`…`-22`, `CCT-GRD-12`) and only cited here (R31 `F-CA-011`) |
| **Domain baseline** | `D-5`, `L-5`, `L-9`, `L-12`, `RL-001` · `movement-post-reverse.contract.md` `MPR-T1-01`, `MPR-T1-10` (status change) |
| **Owning tasks** | `issues/p1-07.md` (lots, serials, LPNs, genealogy) · `issues/p2-05.md` (holds, expiry state) · `issues/p3-15.md` (LPN move) · `issues/p3-24.md` (GS1 identity) · `issues/p0-02.md` (duty status in the key) |
| **Primary tables** | `whb_lots`, `whb_lot_counterparties`, `whb_serials`, `whb_serial_identifiers`, `whb_lpns` (`V500018`); `whb_transformations` + inputs/outputs (`V500035`); `whb_duty_statuses` (`V500005`) — `wh_hold_types`, `wh_holds` (`V510032`) belong to `cycle-count` |
| **Permission resources** | `whb_lots:{view,create,edit,delete,export}` · `whb_serials:*` · `whb_lpns:{view,create,edit,delete,export,move,split,merge,close}` · `whb_transformations:view` · `wh_holds:{view,place,release,mass,export}` |
| **Routes** | WS-036 Lots · WS-037 Serials · WS-038 LPNs · WS-039 Genealogy Explorer (`/warehouse/ledger/genealogy`) — WS-091 / WS-092 are `cycle-count`'s |
| **Contract version** | `v0 — 2026-10-23` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | A lot is keyed `(owner, item, lot_code)` with normalised codes (`WH-SC-142`) | `LSS-GRD-01` |
| A2 | A whole lot is held everywhere at once without moving anything (`WH-SC-139`) | `LSS-T1-03`, `LSS-T4-02` |
| A3 | Bonded and duty-paid stock never merge into one balance (`WH-SC-016`) | `LSS-GRD-07` |
| A4 | Genealogy answers forward and backward across a kit boundary (`WH-SC-003`) | `LSS-T4-04` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Kind |
|---|---|---|---|
| Lot | `AVAILABLE` · `EXPIRED` (set by the expiry job) | `whb_lots.status_code` — lifecycle only; a hold is **not** a lot status | lifecycle |
| Hold | open / released | `wh_holds` row — owned by `cycle-count` §1.1 | independent of item and location |
| Serial | current location, status, owner, LPN, lot | `whb_serials.current_*` | position-like |
| LPN | `OPEN` · `CLOSED` · `SHIPPED` (written by shipment dispatch on every sealed carton's plate, `outbound-despatch` `ODS-T4-13`; terminal) · `CONSUMED` (allowed by `V500018:290` but **unreachable** — no writer, `WhbLpn.java:46`; reserved) | `whb_lpns.status` | ledger object |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | Side effects | UI | Source |
|---|---|---|---|---|---|---|---|---|
| LSS-T1-01 | — | Create a lot (owner, item, lot code, dates, parties) | `AVAILABLE` | `LSS-GRD-01`…`-03` | `whb_lots:create` (or the receipt) | lot-party rows dated from the receipt | WS-036 / receipt | FR-094, FR-095 |
| LSS-T1-02 | — | Create a serial | at its location | `LSS-GRD-04` | `whb_serials:create` (or the receipt) | further identifiers as `whb_serial_identifiers` rows | WS-037 / receipt | FR-097 |
| LSS-T1-03 | no open hold of the type | **Place hold** on a lot (or order / item / location scope) — as `cycle-count` `CCT-T1-20`, which owns the row | hold open | `CCT-GRD-12` | `wh_holds:place` | `LSS-T4-02` | WS-092 **Place** | FR-096 |
| LSS-T1-04 | hold open | Release — as `cycle-count` `CCT-T1-21` | hold released | — | `wh_holds:release` | the lot becomes allocatable again unless another hold is open | WS-092 **Release** | FR-096 |
| LSS-T1-05 | LPN `OPEN` or `CLOSED` at a location (`MOVABLE_STATUSES`, `WhbLpnMovementService.java:94-96`) | **Move LPN** — the plate **and every plate nested inside it** | at the new location | `LSS-GRD-06` | `whb_lpns:move` | `LSS-T4-03` | WS-038 **Move** | FR-101 |
| LSS-T1-05a | LPN `OPEN` with no nested plate | **Split** / **Merge** | split: a new plate; merge: contents into the target | `LSS-GRD-06a` | `whb_lpns:split` / `:merge` | movement per `LSS-T4-03` | WS-038 **Split** / **Merge** (hidden when `hasChildren`) | FR-101 |
| LSS-T1-06 | — | Allocate an SSCC to an LPN (v1.1) | `sscc` set | `LSS-GRD-09` | LPN label print | — | WS-038 **Label** | FR-452 |

### 1.3 Guards

| ID | Predicate | Refusal: HTTP · code · field | Backstop | Source |
|---|---|---|---|---|
| LSS-GRD-01 | A lot is unique on `(owner, item, lot_code)` and on its normalised code (normalised on write, so one physical lot keyed two ways is detected) | `409 LOT_ALREADY_EXISTS` · `lotCode` | `uk_whb_lots_owner_item_lot_code` (`V500018:131`), `uk_whb_lots_owner_item_normalised` (`:175`) | FR-094 |
| LSS-GRD-02 | Lot dates are consistent: manufacture ≤ expiry; best-before and use-by are **separate** columns with different despatch rules; retest date; manufacture not in the future | `LOT_DATES_INCONSISTENT` / `LOT_DATE_IN_FUTURE` · the date field | `chk_whb_lots_*` | FR-095 |
| LSS-GRD-02a | **Shelf-life despatch rule (the one statement; `cycle-count` and `outbound-despatch` cite it).** A lot is **expired** on a day when its status is `EXPIRED` or its **hard date** `LEAST(expiry_date, use_by_date)` has passed (`WhbShelfLifePolicyService.isExpired`, `:210-214`; `WhbShelfLife.hardExpiryDate`); an expired lot is refused by the allocator and at despatch. **Past use-by blocks despatch.** **Past best-before warns, and the despatch needs a reason** (R31 `LSS-OPEN-01`). Best-before is otherwise only the fallback date shelf life is measured against when the lot carries no hard date (`WhbShelfLife.governingDate`, `:28-40`). A customer minimum remaining shelf life is a separate setting (counterparty, then channel, then item — `resolveDespatchMinimum`) with no universal margin | `EXPIRED_LOT_NOT_ISSUABLE` (`WhbLedgerErrorCodes.java:65`); `SHELF_LIFE_RULE_VIOLATED` (`:64`) for the minimum; the best-before warning and its reason: not built (§10 row 5) | `WhbShelfLifePolicyService` | FR-095 |
| LSS-GRD-03 | A lot's parties (supplier, manufacturer, packer, importer) are `whb_lot_counterparties` rows, one **current** row per role, dated from the receipt | `LOT_PARTY_ALREADY_CURRENT` / `LOT_PARTY_RANGE_INVALID` · `role` | `uk_whb_lot_counterparties_current_role` (`V500018:248`) | FR-094 |
| LSS-GRD-04 | A serial is unique on `(owner, item, serial_number)` — **never globally**; a serial identifier (e.g. second IMEI) is unique per owner, never globally, and either resolves on scan | `409 SERIAL_ALREADY_EXISTS` / `SERIAL_IDENTIFIER_ALREADY_EXISTS` · `serialNumber` | `uk_whb_serials_owner_item` (`:405`), `uk_whb_serial_identifiers_owner_type_value` (`:468`) | FR-097 |
| LSS-GRD-05 | At most one open hold of one type on one scope | `HOLD_ALREADY_OPEN` · `holdTypeCode` | — | FR-096 |
| LSS-GRD-06 | An LPN moves whole — with every plate nested inside it, locked together in one id-ordered statement — within one site, from its current location, while `OPEN` or `CLOSED` | `LPN_NOT_AT_LOCATION` / `403 LPN_SPANS_SITES` · `lpnId`; a plate nested in after the lock is refused | — | FR-101 |
| LSS-GRD-06a | Split and merge only an `OPEN` plate with no plate nested inside it (nested split / merge is v2); a split never takes more than the plate holds | `LPN_NOT_OPEN`, `LPN_NESTING_NOT_SUPPORTED`, `LPN_SPLIT_QUANTITY_TOO_LARGE` · `lpnId` | — | FR-101 |
| LSS-GRD-07 | `duty_status` is an FK by code to `whb_duty_statuses` (registry 15), never a `CHECK`; base seeds `DOMESTIC`, `warehouse-india` seeds `BONDED`, `MOOWR`, `SEZ`, `FTWZ`, `EXPORT_UNDER_BOND`; it is on every movement line and in the position key | `422 UNKNOWN_*` · `lines[n].duty_status` (`MPR-GRD-21`); `422 MOVEMENT_UNBALANCED` naming the duty status (`MPR-GRD-01`) | FK `ON UPDATE RESTRICT`; `I-5` | FR-104 |
| LSS-GRD-08 | An LPN's `received_at` (the storage-anniversary anchor) never changes after it is set; `parent_lpn_id`, `sscc`, type, dimensions, gross weight, mixed flags are columns | `LPN_RECEIVED_AT_IMMUTABLE` · `receivedAt` | — | FR-100 |
| LSS-GRD-09 | An SSCC is **allocated, never typed in**: GS1 company prefix + extension digit + serial reference from a per-key counter + mod-10 check digit | a typed SSCC is refused as a read-only field | `uk_whb_lpns_sscc` (`V500018:319`) | FR-452 — §10 row 2 |

### 1.4 Unreachable

| ID | Must never happen | Source |
|---|---|---|
| LSS-UNR-01 | A second way to hold a lot (a lot status meaning "held", or a status-change movement used to hold). A status-change movement is for physical segregation only | FR-096 |
| LSS-UNR-02 | A global unique key on serial numbers (a second manufacturer's identical serial is legitimate) | FR-097 |
| LSS-UNR-03 | An LPN move whose lines are left implicit: the expanded lines are **stored** on the movement | FR-101 |
| LSS-UNR-04 | Bonded and duty-paid stock of one SKU in one position row | FR-104 |
| LSS-UNR-05 | A second ingestion table or idempotency mechanism for RFID / EPC reads | FR-453 |
| LSS-UNR-06 | `GS1_DIGITAL_LINK` as a `CHECK` value; it is a seed row in the open `BARCODE_FORMAT` registry | FR-454 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| LSS-T2-01 | Place / release / mass hold — as `cycle-count` §2 | `wh_holds:place` / `:release` / `:mass` | no open hold of the type / open | FR-096 |
| LSS-T2-02 | Move / split / merge / close an LPN | `whb_lpns:move` / `:split` / `:merge` / `:close` | move: `OPEN` · `CLOSED`; split / merge: `OPEN`, no nested plate; close: `OPEN` | FR-101 |
| LSS-T2-03 | View genealogy | `whb_transformations:view` | — | FR-105 |

## 3. T3 — Time-driven rules

| ID | Rule | Trigger | Changes | Notified | Job | Source |
|---|---|---|---|---|---|---|
| LSS-T3-01 | Expiry is a state: a lot past its hard date (`LSS-GRD-02a`) stops being allocatable | hard date < site day, injected `Clock` | **both effects** (`WhbLotExpiryJob.java:143-144`): a `STATUS_CHANGE` of each issuable position to `EXPIRED` (`cycle-count` `CCT-T4-08`), then `whb_lots.status_code = EXPIRED` once none of the lot's stock is still issuable | alert rule | `WHB_LOT_EXPIRY` | FR-095 |
| LSS-T3-02 | Retest due: a lot at its retest date with stock on hand and no open retest hold gets one | `retest_date` ≤ today | a `wh_holds` row (`WhLotRetestHoldPlacer`); no movement | `WAREHOUSE_LOT_RETEST_DUE` alert | daily | FR-095, FR-096 |
| LSS-T3-03 | Storage anniversaries are computed from the LPN's `received_at` | `received_at` + billing cycle | none here (3PL billing reads it) | — | — | FR-100 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| LSS-T4-01 | A serial is despatched / sold | `sold_to_counterparty_id`, warranty start and end, current custody and the carrying shipment are recorded, so "where is it now, who received it, is it in warranty" is answerable | serial service, despatch | FR-099 |
| LSS-T4-02 | A hold is open on a lot | allocation, pick and issue skip or refuse the lot everywhere at once — the allocator skips held subjects through `WhbAllocationHoldGate` and refuses `ALLOCATION_HELD` (`cycle-count` `CCT-GRD-12`); nothing moves | `WhbAllocationHoldGate` | FR-096 |
| LSS-T4-03 | An LPN moves | **one** movement whose lines the service expands from the LPN's current contents and stores (`lpn_id`, `from_lpn_id` / `to_lpn_id`) | LPN service → writer | FR-101, FR-100 |
| LSS-T4-04 | A kit, repack, decant, split or merge posts | a `whb_transformations` row with its inputs and outputs is written in the same transaction; WS-039 answers forward (where did this lot go) and backward (what went into this unit) for the retention period | transformation service | FR-105 |
| LSS-T4-05 | A lot is split or merged | `parent_lot_id` records the parent at the time | lot service | FR-095, FR-105 |
| LSS-T4-06 | An RFID / EPC read arrives (v2 endpoint; v1.1 columns) | it is an inbound message on the existing port, idempotent by `(epc, read_point, event_at)` through `whb_inbound_messages`' `uk(source_system, idempotency_key)`; a read resolving to no serial or LPN is a **recorded rejection** | port (`MPR-T4-03`) | FR-453 — §10 row 3 |
| LSS-T4-07 | A GS1 Digital Link URI is scanned (v1.1) | the scan resolver parses the AI path segments out of the URI and resolves exactly as for a GTIN | scan service | FR-454 — §10 row 4 |

## 5. T5 — Screen contract

| ID | Screen | Contract | Source |
|---|---|---|---|
| LSS-T5-01 | WS-036 Lots | columns include `lotCode`, `ownerName`, `itemCode`, manufacture / expiry / best-before / use-by / retest dates, `supplierLot`, `countryOfOrigin`, `mrp`, `netContent`, `packMonthYear`, `receiptDate`, `parentLotCode`, `lotStatus`, open-hold indicator; parties tab | FR-094, FR-095 |
| LSS-T5-02 | WS-037 Serials | `serialNumber`, identifiers, current location / status / owner / LPN / lot, `soldToCounterpartyName`, warranty dates | FR-097, FR-099 |
| LSS-T5-03 | WS-038 LPNs | `code`, `sscc` (read-only), type, parent, location, status, `receivedAt`; Move / Split / Merge / Close | FR-100, FR-101, FR-452 |
| LSS-T5-04 | WS-039 Genealogy Explorer | forward and backward trace from a lot, serial or LPN | FR-105 |
| LSS-T5-05 | WS-092 Holds | as `cycle-count` T5 (owner): order / lot / item / location scope, hold type, reason, placed / released by and at | FR-096 |

## 6. Out of scope

FEFO allocation order (`P2-05`, the reservation contract); recall workflow; nested-LPN split / merge (v2);
the RFID reader endpoint (v2); holds (owned by `cycle-count`).

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived for R30 `CP-FR-007` row 4 |
| 2026-10-23 | R31: `F-CA-003` (LPN `SHIPPED`, `CONSUMED` unreachable); `F-CA-008` (`LSS-T1-05`, `-05a`, `LSS-GRD-06`, `-06a`, `LSS-T2-02`); `F-CA-009` (`LSS-GRD-02a` the one shelf-life rule, `LSS-T3-01` both effects); `F-CA-011` (holds owned by `cycle-count`, `LOT_NOT_ISSUABLE` dropped); `F-CA-014` (`lotStatus`, `soldToCounterpartyName`); `LSS-OPEN-01` decided |

## 8. Invariants and scenarios

`D-5`, `L-5`, `L-9`, `L-12`. Scenarios `WH-SC-003`, `-016`, `-080`, `-107`, `-139`, `-142`, `-144`, `-145`.
`FR-452`…`454` have no scenario yet (R30 `CP-FR-010`).

## 9. Open rows

| ID | Question | Default until decided | Source |
|---|---|---|---|
| LSS-OPEN-01 | `FR-095`: best-before and use-by have "different despatch rules", but no FR in §6.5 states them (which blocks despatch, which warns, by how many days) | **DECIDED R31 (2026-10-23), default replaced:** past use-by blocks despatch; past best-before warns and the despatch needs a reason; customer minimum remaining shelf life is a separate setting with no universal margin — stated in `LSS-GRD-02a` | FR-095 |

## 10. Code divergences (for the build to fix)

| # | File:line | FR | What differs |
|---|---|---|---|
| 1 | `warehouse-base/.../V500018__…:95-125` (the `whb_lots` column list) | FR-095 | No `hs_code` column on the lot; the FRD lists HS code among the v1 lot attributes — **Triage 2026-10-23: AMEND-SPEC** — rule: the HS / HSN code is an item attribute carried by `whb_items.tax_classification_code` (`P1-03`, snapshotted onto documents), not a lot column — it does not vary by lot. `FR-095` amended. reviewer-confirm |
| 2 | `warehouse-base/.../db/migration/` (no `V500056`) | FR-452 | SSCC allocation (company-prefix settings, per-key counter, check digit) is not built; `sscc` is a plain column with a unique index — **Triage 2026-10-23: AMEND-SPEC** — rule: SSCC allocation is deferred by the product owner's `OD-17` ruling (2026-09-24, #121 closed not planned; `V500056` stays reserved) until a customer brings a GS1 prefix. `FR-452` amended |
| 3 | `V500018` (no `epc` column on `whb_serials` / `whb_lpns`) | FR-453 | The EPC identity columns (v1.1) are not built — **Triage 2026-10-23: AMEND-SPEC** — rule: EPC is deferred with the GS1 work by `OD-17` (#121). `FR-453` amended |
| 4 | `V500010__…:829-831` | FR-454 | `GS1_DIGITAL_LINK` is refused by the v1 seed and left to `P3-24` (`V500056`), which is not built; the scan resolver does not accept a URI — **Triage 2026-10-23: AMEND-SPEC** — rule: the Digital Link parser is deferred by `OD-17` (#121); the v1 seed's refusal of `GS1_DIGITAL_LINK` is the supported boundary. `FR-454` amended |
| 5 | `warehouse/backend` despatch (no best-before check; `WhbShelfLife.governingDate` uses best-before only as a fallback) | FR-095 | The past-best-before **warning with a reason** at despatch (`LSS-GRD-02a`, R31 `LSS-OPEN-01`) is not built; `P2-05` (expiry, shelf life) owns it (acceptance item added) — **Triage 2026-10-23: FIX-CODE** — owner `P2-05` #42, reopened |
