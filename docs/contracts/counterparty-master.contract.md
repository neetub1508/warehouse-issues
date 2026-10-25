# Functional Contract — Counterparty master (core): thin identity, dated roles, external references, authorised sources

> **What this is.** The functional truth for `warehouse-base`'s **thin counterparty identity** — the one party
> record the stock ledger, receipts, despatches and the trade module name — its **dated many-to-many roles**,
> its **external references** to parties owned by other modules, the recorded trigger for a shared
> `party-base`, and the counterfeit-control flag on item × supplier. It does **not** cover supplier
> evaluation, the approved-vendor list or trade documents (`trade-counterparty-evaluation.contract.md`).
>
> **Status.** Derived 2026-10-23 (v0) for R30 `CP-FR-007` row 6 (`D-17` item a) from
> `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.7 and §6.27, checked against the built code. Not ratified.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Counterparty create → add / end role links → add addresses and tax registrations → link external refs → retire; item × supplier source with `is_authorised_source` |
| **Module** | `warehouse-base` |
| **Domain baseline** | `OD-4` (long-term home of the party), `D-1` (base depends on platform only) |
| **Owning tasks** | `issues/p1-08.md` (counterparties, roles, external refs) · `issues/p6-06.md` (`party-base` trigger, recorded only) · `issues/p3-24.md` (`FR-455`) |
| **Primary tables** | `whb_counterparties`, `whb_counterparty_roles`, `whb_counterparty_role_links`, `whb_counterparty_addresses`, `whb_counterparty_tax_registrations`, `whb_counterparty_external_refs` (`V500011`); `whb_item_supplier_sources` (`V500050`); `whb_dispositions` (`V500010`) |
| **Permission resources** | `whb_counterparties:{view,create,edit,delete,export}` · counterparty roles (WS-011) · item supplier sources (WS-029) |
| **Routes** | WS-021 Counterparties · WS-011 Counterparty Roles · WS-029 Item Supplier Sources · WS-012 Dispositions |
| **Contract version** | `v0 — 2026-10-23` |

---

## 1. T1 — State machine

### 1.1 Status inventory

| Entity | Status | Represented by | Kind |
|---|---|---|---|
| Counterparty | active / retired | `is_active` | master |
| Role link | current / ended | `effective_from`, `effective_to` | dated history |

### 1.2 Transitions

| ID | From | Event | To | Guard | Actor | UI | Source |
|---|---|---|---|---|---|---|---|
| CPM-T1-01 | — | Create: code, name, legal name, national tax id | active | `CPM-GRD-01` | `whb_counterparties:create` | WS-021 **Add** | FR-116 |
| CPM-T1-02 | active | Add a role link (`SUPPLIER`, `CUSTOMER`, `CARRIER`, `CLIENT_3PL`, `TRANSPORTER`, `JOB_WORKER`, `INTERNAL`) with validity dates | link current | `CPM-GRD-02` | `whb_counterparties:edit` | WS-021 roles tab | FR-117 |
| CPM-T1-03 | link current | End a role link | link ended | end after start | `whb_counterparties:edit` | WS-021 roles tab | FR-117 |
| CPM-T1-04 | active | Link an external reference (`source_module`, `external_id`) | linked | `CPM-GRD-03` | `whb_counterparties:edit` | WS-021 external refs tab | FR-118 |
| CPM-T1-05 | active | Retire | inactive | `CPM-GRD-04` | `whb_counterparties:edit` | WS-021 **Deactivate** | FR-116 |

### 1.3 Guards

| ID | Predicate | Refusal: HTTP · code · field | Backstop | Source |
|---|---|---|---|---|
| CPM-GRD-01 | `code` is unique and immutable; `national_tax_id` (the legal-entity id) is indexed and **not** unique (two legal entities in two countries may share one) | `409 COUNTERPARTY_CODE_EXISTS` · `code`; `COUNTERPARTY_CODE_IMMUTABLE` | `uk_whb_counterparties_code` (`V500011:174`) | FR-116 |
| CPM-GRD-02 | A role is an active row of the `whb_counterparty_roles` registry; links of one role for one counterparty do not overlap in time | `COUNTERPARTY_ROLE_INACTIVE` · `roleCode`; `409 COUNTERPARTY_ROLE_OVERLAP` · `effectiveFrom` | exclusion on `(counterparty_id, role_code, tstzrange)` (`V500011:220-221`) | FR-117 |
| CPM-GRD-03 | `(source_module, external_id)` is unique; `source_module` is an opaque string, never an FK | `409` on `externalId` | unique key on `whb_counterparty_external_refs` (`V500011`) | FR-118 |
| CPM-GRD-04 | A counterparty that is an active owner cannot be retired | `409 COUNTERPARTY_HAS_ACTIVE_OWNERS` | — | FR-116 |
| CPM-GRD-05 | Receiving **any item** (serialised or not) whose effective source for the GRN's supplier — the item × supplier row current at the receipt instant (`receivedAt`, else post time) under half-open `[effective_from, effective_to)`, the site's own row before an every-site row (FR-252) — has `is_authorised_source = false` lands the line in the `SUSPECT` disposition's `target_stock_status_code` (`SUSPECT`, a `whb_stock_statuses` row with QUARANTINE's flags; both rows `V501239`). An item with **no** such row, or a GRN with no supplier, is *unlisted*: received as before under `warehouse.receiving.unlisted_source_treatment = NOT_SUSPECT` (default), or as `SUSPECT` under `SUSPECT` (`V511424`). This rung runs **first** — above FR-134 regulated `QUARANTINE`, the line's own status, the item × site default and `NO_INSPECTION`. **Never refuses**: a missing SUSPECT row lands `QUARANTINE` with a warning. `is_authorised_source` and AVL approval (`RQP-GRD-44/45`) are separate facts. Upstream, replenishment never proposes an unauthorised source (`RPN-T4-01`, `WhbPreferredSupplierSourceSql`) | the receipt line takes `SUSPECT`; no bespoke refusal | — | FR-455 — §10 row 1 (closed, classic `8db39bb014`) |

### 1.4 Unreachable

| ID | Must never happen | Source |
|---|---|---|
| CPM-UNR-01 | A `partner_type` enum or a single role column; a party is routinely two roles at once | FR-117 |
| CPM-UNR-02 | A party from another module (automotive, assets) **copied** into `whb_counterparties`; it is linked through `whb_counterparty_external_refs`. In a standalone install the table is empty and everything works | FR-118 |
| CPM-UNR-03 | A shared `party-base` extracted before the recorded trigger — **the third module that needs the same GSTIN to be authoritative for tax filing** (`OD-4`); recorded, not acted on (v3) | FR-121 |
| CPM-UNR-04 | A bespoke counterfeit workflow; a suspect part travels the existing disposition path | FR-455 |
| CPM-UNR-05 | A payment-terms, credit-limit, bank-details, contacts or scorecard column or child table on the counterparty — they belong to the module that owns the commercial relationship (`trade-counterparty-evaluation` carries the scorecard). **Excepted:** dated addresses by role (`whb_counterparty_addresses`) and per-state tax registrations (`whb_counterparty_tax_registrations`), which the challan and e-way bill freeze; `national_tax_id` stays the legal-entity id | FR-119 |

## 2. T2 — Action × role × state

| ID | Action | Permission | Allowed from | Source |
|---|---|---|---|---|
| CPM-T2-01 | Create / edit / retire a counterparty; maintain roles, addresses, tax registrations, external refs | `whb_counterparties:create` / `:edit` | — / active | FR-116, FR-117, FR-118 |
| CPM-T2-02 | Mark an item × supplier source authorised / not authorised (Add, Edit in place — audited `isAuthorisedSource` change — and Re-source, which copies the current value unless the request overrides it); post the receipt that the flag judges | `whb_item_supplier_sources:create` / `:edit`; receipt post unchanged (`wh_goods_receipts:post`) | source not ended | FR-455, CPM-GRD-05 |

## 3. T3 — Time-driven rules

| ID | Rule | Clock | Changes | Source |
|---|---|---|---|---|
| CPM-T3-01 | A role is in force only inside its `[effective_from, effective_to)`; a document dated outside it does not see the role (e.g. a supplier role ended before a PO date) | document date | nothing — a read rule | FR-117 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| CPM-T4-01 | Another module needs a party | it reads `whb_counterparties` or joins through `whb_counterparty_external_refs`, never by an FK into its own party table | consumers | FR-118 |
| CPM-T4-02 | A third module needs the same GSTIN authoritative for tax filing | the `party-base` extraction is due; `issues/p6-06.md` records it | — (recorded) | FR-121 |
| CPM-T4-03 | A GRN is posted with a line whose item is suspect under `CPM-GRD-05` | the line's `received_status_code = SUSPECT` (its serials too), the stock lands SUSPECT (on hand, not allocatable — no putaway task; the GRN grid flags it awaiting QC), it is QC-held and appears on the WS-080 candidate list, and one `WH_GRN_LINE_SUSPECT_SOURCE` audit entry per line names the GRN, line, item, supplier, source-row id and flag, written after the post commits; rejected units on the line still land REJECTED | `WhGoodsReceiptSourceAuthorisation` + `WhGoodsReceiptPostingService.resolveReceivedStatus` (one batch read per receipt) | FR-455 |

## 5. T5 — Screen contract

| ID | Screen | Contract | Source |
|---|---|---|---|
| CPM-T5-01 | WS-021 Counterparties (reference **Department**, with relation tabs) | grid `code`, `name`, `legalName`, `nationalTaxId`, current roles, `isActive`, audit; tabs roles (dated), addresses, tax registrations, external refs; filters role, active | FR-116, FR-117, FR-118 |
| CPM-T5-02 | WS-029 Item Supplier Sources | shows `isAuthorisedSource` per item × supplier: a `Toggle` on Add/Edit (terms tab) and Re-source, a View row, a boolean grid column (visible, in `default_columns`, after `isAsnCapable`) and the export column beside `isAsnCapable`; no filter | FR-455 |

## 6. Out of scope

Supplier evaluation, AVL and approval (`trade-counterparty-evaluation`); counterparty GSTIN validation
(India pack); customer credit.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived for R30 `CP-FR-007` row 6, as a NEW core contract (the trade contracts are not edited) |
| 2026-10-23 | R31 `F-CA-017`: `CPM-UNR-05` (the `FR-119` exclusion, with its address and tax-registration exception); `CPM-OPEN-01` decided |
| 2026-10-26 | W72 #606 S2 (classic `8db39bb014`, `V501239`, `V511424`): `CPM-GRD-05` amended — all items, effective at `receivedAt`, site row first, the unlisted setting, target `SUSPECT`, never refuses, first rung; `CPM-T2-02`, `CPM-T4-03` added; `CPM-T5-02` detailed; §10 row 1 closed. Runbook: an install that narrows `RECEIPT.allowed_to_status_codes` to exclude `SUSPECT` gets `STATUS_TRANSITION_NOT_ALLOWED` on a suspect receipt — the same misconfiguration as excluding `QUARANTINE` today; keep `SUSPECT` allowed. The inspection arm (QC → `SUSPECT`) is **not built**: under `RQP-GRD-29` it would use the line's series cap and leave the stock unreleasable |
| 2026-10-26 | W72 #606 S4 (classic `956d43c66f`): `CPM-GRD-05` — replenishment proposes authorised sources only (#106 H4); S3 F1 setting label, F2 help rule7, Re-source modal tabbed |

## 8. Invariants and scenarios

`OD-4`, `D-1`. Scenarios `WH-SC-277`, `WH-SC-278`; `FR-455`: `WH-SC-800`…`WH-SC-803`. `FR-121` has no scenario yet.

## 9. Open rows

| ID | Question | Default until decided | Source |
|---|---|---|---|
| CPM-OPEN-01 | `OD-4`: the long-term home of the party (base vs a future `party-base`) | **DECIDED R31 (2026-10-23): default stands** — `warehouse-base` owns the thin identity; other modules join through external references (`OD-4` RESOLVED) | FR-116, FR-121 |

## 10. Code divergences (for the build to fix)

| # | File:line | FR | What differs |
|---|---|---|---|
| 1 | `warehouse-base/.../V500050__…:159` (`whb_item_supplier_sources`, no `is_authorised_source`); `V500010` (no `SUSPECT` disposition) | FR-455 | Counterfeit control is not built (`P3-24`, v1.1) — **Triage 2026-10-23: FIX-CODE** — no open owner — `P3-24` #121 closed not planned on `OD-17`, which covers GS1 only; new finding `W72` — **CLOSED 2026-10-26 (W72 #606 S2, classic `8db39bb014`)**: `V501239` adds the column and the `SUSPECT` status + disposition; `WhGoodsReceiptSourceAuthorisation` applies it at the GRN post; `SUSPECT` is in `QC_HELD_STATUSES` |
