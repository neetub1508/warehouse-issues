# GAP-REGISTER-R4 — the disposition of every round-4 finding, and the fold plan

<!-- check-design-set: scenario-citations file WH-SC-306 WH-SC-307 WH-SC-308 WH-SC-309 WH-SC-310 WH-SC-311 WH-SC-312 WH-SC-313 WH-SC-314 WH-SC-315 WH-SC-316 WH-SC-317 WH-SC-318 WH-SC-319 WH-SC-320 WH-SC-321 WH-SC-322 WH-SC-323 WH-SC-324 WH-SC-325 WH-SC-326 WH-SC-327 WH-SC-328 — allocated by §4.0 from the SCENARIO-CATALOGUE.md §5 rule 3 marker; the rows are owed to §3.22 by the P-CORE fold, and WH-SC-328 is the marker's new position -->
<!-- check-design-set: screen-citations file WS-238 WS-239 WS-240 WS-241 WS-242 — WS-238 and WS-239 are the two ids GAP-REGISTER-R3.md §4.4 recommends for the unfolded round-3 screens (RA-001, RA-002) and are reserved here, not taken; WS-240 and WS-241 are allocated by §4.0 and owed to BUILD-SPEC-SCREENS.md §1; WS-242 is the next-free marker -->

> **What this document is for.** `GAP-REGISTER.md`, `-R2` and `-R3` disposition rounds 1–3 (575 + 62 + 52
> findings). This one dispositions the **83** findings of round 4 — five lenses, `reviews/R22`–`R26`,
> registers `RG-` `RH-` `RJ-` `RK-` `RL-` — under `D-12` and under three user decisions taken on
> 2026-09-10. Decisions (1) and (2) are recorded as **`D-14`**; decision (3) is applied throughout as the
> placement rule. Every finding has exactly one disposition row in §2.
>
> **Rounds 1–3 are not superseded** except where `D-14` reverses them by user decision: `FR-079`'s
> *"belongs to exactly one branch"*, `DATA-MODEL.md` §9.2's dropped-junction row, the scalar rows in
> `IRREVERSIBLE.md`, and the advice of `C-016`/`C-030`. `E-048` and `S-022` stay closed. **Reviews are
> dated records and are never edited**: where a lens asks for one to change (`RH-010` → R18 §4, `RH-012` →
> R6's source list) the correction is recorded here, not there.
>
> **This file changes nothing but itself.** `DECISIONS.md` (`D-14`, `OD-18`, `OD-19`, §6) and
> `tools/check-design-set.py` were edited in the same commit. §4 is the complete edit set for the four
> fold agents, in four disjoint file partitions, with **every new id already allocated** so no fold agent
> allocates one.

**Date** 2026-09-10 · **Branch** `docs/round-4-cardinality-and-gaps`

---

## §1 · The round, the decisions it ran under, and the counts

### 1.1 The five axes

| Lens | Prefix | The axis | BLOCKER | MAJOR | MINOR | n |
|---|---|---|---:|---:|---:|---:|
| **R22** | `RG-` | **Cardinality and junctions** — every scalar association in `DATA-MODEL.md` §2 classified, and the branch↔warehouse junction specified in full | 2 | 7 | 18 | 27 |
| **R23** | `RH-` | **Platform alignment** — 39 platform capabilities checked against the live tree: reuse, duplicate, gap, platform dependency | 2 | 7 | 3 | 12 |
| **R24** | `RJ-` | **Workflow contract completeness** — thirteen workflows, five contract tables each, derived from the set's own text | 4 | 8 | 6 | 18 |
| **R25** | `RK-` | **Competitor gap, round 3** — 17 named products × 31 capabilities, multi-branch operation first | 0 | 3 | 6 | 9 |
| **R26** | `RL-` | **Extensibility and future-proofing** — 23 axes, each tested against its next concrete consumer | 2 | 10 | 5 | 17 |
| | | **Total** | **10** | **35** | **38** | **83** |

```bash
cd warehouse-issues
for f in R22 R23 R24 R25 R26; do grep -hE '^### `R[G-L]-[0-9]{3}`' docs/reviews/$f-*.md \
  | grep -oE '(BLOCKER|MAJOR|MINOR)\*\*$' | sort | uniq -c | tr '\n' ' '; echo; done
# R22:  2 BLOCKER  7 MAJOR 18 MINOR · R23: 2 7 3 · R24: 4 8 6 · R25: 0 3 6 · R26: 2 10 5   -> 10 · 35 · 38 = 83
python3 tools/check-design-set.py --check 7 | head -1        # pass — all 83 resolve against their own lens
```

### 1.2 The three user decisions, and how each was applied

| # | Decision (binding, not re-litigated) | Where it lives | How this register applied it |
|---|---|---|---|
| **1** | Every association between two independent masters is an effective-dated M:N junction, with `is_primary` or a role where a default is needed. Parent→line composition and ledger fact rows stay scalar | **`D-14`** item 1 | R22's §1.3 convention is adopted verbatim for every junction in this round, including two the lenses left undated (`RH-004`'s `whb_company_branches`, `RK-006`'s portal users). R22's six KEEP-SCALAR findings are the carve-out's edge and are kept as traps |
| **2** | Branch↔warehouse is `whb_warehouse_branches` with exactly one `REGISTERED` branch per warehouse at a time; it supplies the GSTIN; `SERVING` branches may draw stock; drawing across GSTINs is a cross-GSTIN supply. Reverses `FR-079` and `C-016`/`C-030` | **`D-14`** items 2–6 | `RG-001` is canonical. Four findings from three other lenses merge into it (§3.1). **One serving-branch rule** is stated (§3.2) |
| **3** | Don't over-engineer. Useful-but-not-day-one goes to v2 or a later phase, and still gets a task | **`D-14`** item 7; applied here | Six **new task files**, five of them v2 (`P5-24`…`P5-28`) and one v1.1 (`P3-25`). Every v2 table a lens hung on a v1 task is lifted out into `P5-24`, so no v1 task carries v2 work. Where a lens offered a heavier and a lighter shape, the lighter is taken and the reason written (§3.7) |

### 1.3 The buckets

- **`COVERED-uncited`** — inside an existing task's declared scope. The task gains a line, a column, a key,
  a seed row, a trigger, a trap or an acceptance box. **Its header does not change.**
- **`NEEDS-AMENDMENT`** — an existing task gains or loses a **table, a migration, a screen, a requirement or
  a deliverable**, so its header, its `IMPLEMENTATION-PLAN.md` §2 row or its epic row changes.
- **`NEW-TASK`** — a task file that does not exist, with an id minted in §4.0.
- **`DECIDED`** — not an authoring gap; a person chooses. The `OD-` row is named.
- **`MERGED-into-<id>`** — the same defect as a canonical finding; what it adds is folded into that row.
- **`DECLINED`** — refused with a written reason. **Round 4 declines no whole finding**; five partial
  refusals are written into the rows they belong to (§3.7).

**Deadline** is the migration or task at which the finding stops being free. `PNR-1` and `PNR-2` are both
`V500030` (`P0-02`); `PNR-3` is the first movement in any install.

---

## §2 · The disposition of all 83

### 2.1 R22 · `RG-` — cardinality and junctions

| Finding | Sev | The defect, in one line | Disposition | Owning file — and what it gains | Deadline | Person? |
|---|---|---|---|---|---|---|
| `RG-001` | **BLOCKER** | The warehouse's branch is a mutable scalar with two more scalars copying its tax identity, so registration history is overwritten and a site can serve no second branch | **NEEDS-AMENDMENT** · canonical for `D-14` | **`P1-05`** owns R22 §1.2 in full, as reconciled in §3: `whb_warehouse_branch_roles` (registry 16) and `whb_warehouse_branches` in `V500012`; `whb_warehouses` loses `branch_id`, `tax_registration_id`, `legal_entity_id`; the four guards; the `WarehouseBranchLinkValidator` bean collection; `WS-016`'s *Branches* tab and *Change registration* (maker–checker); `FR-460`. **`P0-02`** gains `I-22` in `V500030` and claims **`V500037`** for `I-23`. **`P0-15`** seeds `warehouse:warehouses:change_registration`. **`P1-18`** owns R22 §1.2.5. One-rule amendments to the tasks in §4.3–§4.5 | **`V500012`** — before `PNR-1` | **yes — `OD-19`** (on-hand stock at a registration change) |
| `RG-002` | **BLOCKER** | One GSTIN profile has one branch, but a registration covers every branch in its state; the second Delhi branch resolves no GSTIN | **NEEDS-AMENDMENT** | **`P2-IN-01`** — `whin_gstin_profile_branches` (`place_role` `PRINCIPAL`/`ADDITIONAL` as a closed statutory `CHECK` under `OD-5`, dated, `EXCLUDE (company_id, branch_id, range)`) in `V540010`; `whin_gstin_profiles.branch_id` dropped, `gstin` stays unique; service equality with `branches.gst_number` on save **and** a nightly drift row (this is `RH-005`'s choice, taken here); `WS-173` *Places of business*; `WH-SC-313`; the cast gains a second Delhi branch | `V540010` — before the first challan | no |
| `RG-003` | MAJOR | A counterparty has one tax id and one address; its GSTIN depends on the ship-to state and the challan/e-way bill need the recipient's | **NEEDS-AMENDMENT** | **`P1-08`** — `whb_counterparty_addresses` and `whb_counterparty_tax_registrations` in `V500011`, dated, per R22; `national_tax_id` stays the legal-entity id; `FR-119` reverses its exclusion for addresses and tax registrations only. **`P2-IN-03`/`P2-IN-04`** freeze `to_counterparty_tax_registration_id` and `to_counterparty_address_id` | `V500011` · first filed document | no |
| `RG-004` | MAJOR | Location custody is one overwritable `assigned_user_id` | **NEEDS-AMENDMENT** | **`P1-05`** — `whb_location_user_assignments` (`assignment_role` a code list `CUSTODY_ROLE`: `CUSTODIAN`/`DRIVER`/`HELPER`) in `V500013`; one current `CUSTODIAN` + `EXCLUDE`; `assigned_user_id` dropped, crossing FK `B2` moves. **`P3-20`**: `whaf_van_stock_assignments` FKs down to the base row | `V500013` | no |
| `RG-005` | MAJOR | An item has one category, and the category keys six resolvers; re-categorisation silently re-costs | **NEEDS-AMENDMENT** | **`P1-01`** — `whb_item_category_assignments` in `V500015` (scheme = the root of the category tree, denormalised by trigger; one current row per item × scheme; seeded system root `STOCKING`, mandatory for stocked items, **the only scheme any resolver reads, at `occurred_at`**); `category_id` dropped. One line each in `P0-12`, `P0-17`, `P1-04`, `P1-14`, `P2-04`, `P2-07`, `P2-16`, `P2-20` | `V500015` | no |
| `RG-006` | MAJOR | A lot has one counterparty, conflating supplier, manufacturer, packer and importer | **NEEDS-AMENDMENT** | **`P1-07`** — `whb_lot_counterparties` in `V500018`, role from registry 11 seeded with `MANUFACTURER`/`PACKER`/`IMPORTER`; `counterparty_id` dropped. **`P4-05`** reads the parties. The party list is a **RE-VERIFY** row in `INDIA-LOCALISATION-PACK.md` (§5 item 3) | `V500018` · `PNR-3` | RE-VERIFY only |
| `RG-007` | MAJOR | A serial has one secondary identifier; a dual-SIM handset has two IMEIs | **NEEDS-AMENDMENT** | **`P1-07`** — `whb_serial_identifiers` in `V500018` (`identifier_type` open, `uk(owner_id, identifier_type, identifier_value)`, never global); `secondary_serial` dropped. **`P1-02`**'s scan resolver reads it | `V500018` · `PNR-3` | no |
| `RG-008` | MAJOR | The fixed pick face is stored twice, in two cardinalities, a version apart | **NEEDS-AMENDMENT** | **`P1-02`** — `whb_item_location_settings` DDL moves into `V500016` with `is_fixed` and dates; `whb_locations.fixed_item_id` and its `ALTER` dropped. **`P3-12`'s header loses `V500061`**, which becomes a hole (`DATA-MODEL.md` §7.1 rule 2). One line in `P1-05`, `P1-15` | `V500016` | no |
| `RG-009` | MAJOR | The variant model is three fixed slots on the schema `A-3` calls unrecoverable | **NEEDS-AMENDMENT** | **`P1-01`** — `whb_style_variant_axes` + `whb_item_variant_values` in `V500015`, **deliberately undated** (R22 §1.3 rule 6); the three slots dropped. **`P5-20`** reads them | `V500015` | no |
| `RG-010` | MINOR | Purchase and sale UoM are item scalars but supplier- and channel-specific | **NEW-TASK** `P5-24` | `whb_item_uom_defaults` (v2) in `V500070`. `P1-01` keeps the two scalars in v1 and says they are superseded at v2 | before `P5` | no |
| `RG-011` | MINOR | Supplier sources are undated and cannot be preferred per site | **NEW-TASK** `P5-24` | the **site scope** (`warehouse_id`, one current preferred per item × site) at v2 in `V500070`. **The dating half is v1** and rides `RG-021` in `P1-03`, because `D-14` item 1 dates every junction at creation | before `P5` | no |
| `RG-012` | MINOR | A site has one company and nothing asserts a movement's company matches it | **NEW-TASK** `P5-24` | `whb_warehouse_companies` (`OPERATOR`/`STOCK_HOLDER`) at v2. **In v1 `P0-02` gains the free assertion** — the movement's `company_id` equals its site's `company_id` | `V500030` for the v1 line | no |
| `RG-013` | MINOR | An owner has one company | **NEW-TASK** `P5-24` | `whb_owner_companies` (`HOUSE`/`SERVICED_BY`, dated) at v2; the one-house-per-company index moves to it. `P0-06` records the supersession | before `P5` | no |
| `RG-014` | MINOR | A location is dedicated to one owner; a client group's shared cage cannot be declared | **NEW-TASK** `P5-24` | `whb_location_owner_dedications` + commingle policy `OWNER_SET` at v2 | before `P5` | no |
| `RG-015` | MINOR | Functional zones are forced into the physical tree | **NEEDS-AMENDMENT** | **`P3-06`** claims **`V500068`** (a `warehouse-base` number; its header gains the module) for `whb_location_zone_memberships`; `parent_location_id` stays | before `P3-06` | no |
| `RG-016` | MINOR | A carrier account has no site scope, and nothing makes a carrier 1:1 with its party | **NEEDS-AMENDMENT** | **`P2-10`** — `uk(counterparty_id)` on `wh_carriers` in `V510044` (v1, KEEP-SCALAR). **`P5-11`** gains `wh_carrier_account_scopes` in `V510204` (v2) | `V510044` for the key | no |
| `RG-017` | MINOR | Five v2 tables not yet built are specified scalar | **NEEDS-AMENDMENT** | at build, in their own migrations: **`P5-09`** `wh_channel_account_warehouses` (`V510208`) · **`P5-10`** `wh_working_calendar_assignments` (`V510202`) · **`P5-01`** `wh3_client_counterparties` (`V530010`) · **`P5-02`** `wh3_rate_card_clients` with the one-`ACTIVE`-card guard as an `EXCLUDE` (`V530021`) · **`P5-07`** `wh3_sla_definition_clients` (`V530050`) | at build | no |
| `RG-018` | MINOR | Configuration scopes are single scalars, and two lists live in one column | **NEW-TASK** `P5-24` | the v2 scopes lifted out of v1 tasks into `P5-24`: `whb_outbox_subscription_owners` (`V500070`), `wh_print_template_scopes` and `wh_inspection_plan_assignments` (`V510220`), a `WAREHOUSE` scope value on `wh_count_program_scopes`. **At build, not new:** `P3-03` `whb_device_assignments` (`V500062`, v1.1) · `P2-IN-01` `whin_compliance_registration_document_kinds` (`V540010`, v1) · `P5-22` `whb_api_client_endpoints` + `whb_api_client_companies` (`V500066`, v2) | each at its build | no |
| `RG-019` | MINOR | Four document headers carry a single parent their lines already associate many-to-one | **COVERED-uncited** | header column nullable and **derived** ("the only parent, when there is one"): `P1-13` (`wh_goods_receipts.po_id`), `P2-17` (`wh_landed_cost_documents.grn_id`), `P2-12` (`wh_return_receipts` three columns), `P2-13` (`wh_supplier_returns` two). "GRNs of PO X" reads through lines | `V510014` | no |
| `RG-020` | MINOR | Jurisdictional codes are single-valued on country-neutral masters | **NEW-TASK** `P5-24` | `whb_item_tax_classifications`, `whb_uom_scheme_codes`, `whb_reason_code_tax_treatments` at v2 (`V500070`); the counterparty `gln` moves to `RG-003`'s address rows in v1. **The v1 half is `RL-008`** (§3.6) | before `P5` | no |
| `RG-021` | MINOR | Existing junctions use three date vocabularies and none prevents overlap | **COVERED-uncited** | R22 §1.3 on every existing junction, plus the `EXCLUDE`: `P1-08` (role links, and the first `btree_gist` declaration, `V500011`), `P0-06` (owner grants), `P0-17` (valuation policies), `P1-04` (stocking ownership), `P1-03` (supplier sources — `RG-011`'s dating half), and at build `P3-20`, `P4-10` | `V500011` | no |
| `RG-022` | MINOR | KEEP-SCALAR, redefine: `whb_lpns.owner_id` beside `is_mixed_owner` | **COVERED-uncited** | `P1-07` — the column is the custodian/label owner; owner reporting reads positions | `V500018` | no |
| `RG-023` | MINOR | KEEP-SCALAR: item, lot and serial ownership are identity (`I-19`) | **COVERED-uncited** | one trap line each in `P1-01`, `P1-07` | — | no |
| `RG-024` | MINOR | KEEP-SCALAR: the base UoM (`L-7`, `I-9`) | **COVERED-uncited** | one trap line in `P1-01` | — | no |
| `RG-025` | MINOR | KEEP-SCALAR: physical containment (`I-4`) | **COVERED-uncited** | one trap line in `P1-05` | — | no |
| `RG-026` | MINOR | KEEP-SCALAR: stock-period scope (`L-8`) — never by branch through the junction | **COVERED-uncited** | one trap line in `P0-07` | — | no |
| `RG-027` | MINOR | KEEP-SCALAR: branch or registration never joins the ledger line or `L-5`; serial `current_*` are caches | **COVERED-uncited** | one trap line in `P0-02` | — | no |

### 2.2 R23 · `RH-` — platform alignment

| Finding | Sev | The defect, in one line | Disposition | Owning file — and what it gains | Deadline | Person? |
|---|---|---|---|---|---|---|
| `RH-001` | **BLOCKER** | Every branch predicate binds `whb_warehouses.branch_id`, platform's fragment is column-shaped, and accessories' M:N guard treats an unlinked warehouse as shared | **MERGED-into-`RG-001`** | contributes to `P1-18`: the resolver returns `Set<UUID> allowedWarehouseIds` (null = view-all, empty = short-circuit); **an unlinked warehouse is visible to no branch-scoped caller**, and accessories' *"unassigned warehouses stay shared"* arm (`AccessoryStockTransferAccessGuard.java:186-187`) is refused by name; accessories' `is_primary` meaning is not copied; the architecture rule is re-aimed at `:allowedWarehouseIds` | before `P1-18` | no |
| `RH-002` | **BLOCKER** | The set re-specifies branch scoping while platform ships `BranchScopeService` and the `:view:all`/`:view:branch` pair; `P0-15` seeds no scope tier | **NEEDS-AMENDMENT** | **`P0-15`** (`V501000`/`V501001`) and **`P1-20`** (`V511000`/`V511001`) seed `<resource>:view:all` and `:view:branch` for every management resource with dependency rows; ADMIN and AUDITOR `:all`, Branch Admin `:branch` never `:all`, operational bundles `:branch`; an `ArchitectureInvariantsTest` rule refuses injecting `BranchStaffRepository`. **`P1-18`** wraps `branchScopeService.resolveStrict(...)`. **`PP-13`/`PD-D11` are withdrawn**; `FR-404` names the pair | `V501000` | no |
| `RH-003` | MAJOR | PD says a site **is** a branch, DATA-MODEL says it **belongs to** one; under M:N neither holds | **COVERED-uncited** | **`P1-05`** trap: *"a warehouse is linked to branches, never mirrored as one"*, with the one exception of R23 (a `WAREHOUSE`-type branch only for a site that is itself a GST place of business no branch carries). `PLATFORM-DEPENDENCIES.md` §1.1 and §2.1 corrected (`whb_sites` removed). Consistent with R22 §4 refusal 4 — see §3.5 | `V500012` | no |
| `RH-004` | MAJOR | The company axis has no platform anchor; `WS-016`'s cascade is unimplementable; `whb_api_clients.company_id` points at automotive | **NEEDS-AMENDMENT** | **`P0-07`** — `whb_company_branches` in `V500001`, **effective-dated per `D-14`** (R23's `is_active` shape overruled), on `WS-015`; `warehouse-adapter-dealer` may seed it from automotive through `whb_company_external_refs`, base never reads automotive. **`P1-05`** — `422 WAREHOUSE_BRANCH_COMPANY_MISMATCH` on a `REGISTERED` branch not linked to the site's company; `WS-016`'s branch options come from a warehouse endpoint intersecting my-branches with the company's branches in the backend. **`P5-22`** — FK to `whb_companies` | `V500001` | no |
| `RH-005` | MAJOR | The same-GSTIN test, the per-branch series and `whin_gstin_profiles` each receive a set under M:N | **MERGED-into-`RG-001`** | contributes: *the `REGISTERED` link is the only branch any tax, statutory-numbering or supply rule reads*; the `whin_gstin_profiles` choice is **keep `gstin` + equality check + nightly drift row** (carried by `RG-002`); its *"at `dispatched_at`"* is overruled by `FR-305`'s *frozen at creation* (§3.7) | `V500012` | no |
| `RH-006` | MAJOR | Branch rollups double-count a shared site; the dashboard needs three platform edits | **NEEDS-AMENDMENT** | the rollup rule (stock and value to the `REGISTERED` branch; flows to the document's branch; a branch-filtered shared site shows *"shared by N branches"* and refuses a total) is `RG-001` row 11 in `P2-20`/`P2-21`. **`P0-01`** seeds `widget:warehouse:view`/`:view:all`/`:view:branch` and the `V727`-style source-page row in `V500200`. **`P6-10`** carries the platform commits (`FALLBACK_MODES`, the `registry.ts` union), listed in `PP-9` | `V500200` | no |
| `RH-007` | MAJOR | Warehouse notifications need a `NotificationCategory` value, a code-registered email template and a menu binding; SMS is a stub | **NEEDS-AMENDMENT** | **`P2-15`** is the **first** warehouse notification in v1 (it is `RK-004`'s) and owns the two platform commits (`NotificationCategory.WAREHOUSE_REPLENISHMENT`, one `EmailTemplateDefaults` registration) plus the menu row. **`P3-16`** carries the rest and hides `notify_sms` until platform ships SMS. `PLATFORM-DEPENDENCIES.md` §1.9 and `PP-9` gain the rows | before `P2-15` | no |
| `RH-008` | MAJOR | The runbook has no mobile touchpoint; a screen needs three navigation files and a string-matching gate | **NEEDS-AMENDMENT** | **`P0-01`** — the runbook deliverable gains the five mobile touchpoints, and a warehouse L1 menu is seeded with an `is_mobile_enabled` L2 child before any mobile task merges; `MODULE-INTEGRATION.md` §2 gains five rows. **`P3-01`** — the shared GS1-capable scanner extracted from `AssetQrScannerScreen` (v1.1, `PP-9`) | before the first mobile task | no |
| `RH-009` | MAJOR | Platform's importer parses in the browser under a global 500-row cap; opening stock is 200k–1M rows | **NEEDS-AMENDMENT** | **`P1-10`** — above `bulk_import_max_rows` the file goes to platform `documents` and is parsed, validated and applied server-side in batches with progress on the batch row; `ImportButton` only for small masters; the global setting is never raised. **`P2-19`** uses it. PD §1.7 → SHAPE-MISMATCH | before `P2-19` | no |
| `RH-010` | MINOR | R18 refused *schedulable* reports; platform ships a pluggable scheduler | **COVERED-uncited** | **`P2-21`** — *schedulable* stays, met by one `ReportDataProviderInterface` bean and `report_types` rows `module = 'warehouse'`; **UNVERIFIED** that the run applies the recipient's scope, settled by reading the interface before writing the provider. R18 §4's refusal row is corrected **here**, not in R18 | before `P2-21` | no |
| `RH-011` | MINOR | The v2 calendar re-keys platform holidays; the site timezone is a free string | **COVERED-uncited** | **`P1-05`** validates `whb_warehouses.timezone` against platform `timezones`. **`P5-10`** layers cut-offs and exceptions over the `REGISTERED` branch's platform holiday assignment, read-only | `V500012` | no |
| `RH-012` | MINOR | Telemetry is opt-in, the document viewer is never named, and the prior module's code survives on `origin/warehouse` | **COVERED-uncited** | PD §1.10 → *opt-in per role (`V719`)*; **`P1-04`** names `DocumentViewerPane`, `DocumentPreviewModal`, `useDocumentViewerControls`; `origin/warehouse` is recorded in PD §1.15(a) as un-triaged code prior art (**R6 is not edited**) | — | no |

### 2.3 R24 · `RJ-` — workflow contract completeness

| Finding | Sev | The defect, in one line | Disposition | Owning file — and what it gains | Deadline | Person? |
|---|---|---|---|---|---|---|
| `RJ-001` | **BLOCKER** | The M:N decision is unfolded and four authorities refuse it | **MERGED-into-`RG-001`** | contributes rules R1, R2, R3 and R5 as reconciled in §3.2 and §3.7; **R4 (only the `REGISTERED` branch's users may receive, count, adjust, close) is not adopted** — operating verbs are governed by permissions and `RA-001`'s grants, one mechanism, not by a link's role; **R1's `posting_date` is overruled by `occurred_at`** | `V500012` | no |
| `RJ-002` | **BLOCKER** | In-transit stock sits at two different places by document, and either way the receiving storekeeper is refused by `P1-18` | **COVERED-uncited** | **the FRD reading wins** (§3.4): the transit location is a per-transfer child of the **source** warehouse, location type `IN_TRANSIT`; `TRANSIT-WH` is deleted from the port contract, the scenarios and `p2-02`/`p6-08`. **`P1-18`**: `wh_transfer_orders:receive` and the transit-loss adjustment authorise posting against **that transfer's** transit location regardless of site scope, and nothing else at the source site. **`P1-05`** seeds the type only (`RE-002`'s transit-site seeding shrinks to it) | before the first transfer | no |
| `RJ-003` | **BLOCKER** | Transfers and supplier returns run beside the one demand model, so their stock is never reserved | **NEEDS-AMENDMENT** | **`P2-08`**'s `V510040` adds nullable `demand_order_id` to `wh_transfer_orders` and `wh_supplier_returns` by `ALTER` (the FK cannot sit in `V510031`/`V510020`, which run first); demand types `TRANSFER` and `VENDOR_RETURN` are `DEMAND_TYPE` code-list rows (`RL-006`). **`P2-02`**/**`P2-13`** lose their own Pick/Dispatch: reservation, pick and staging are `P2-07`/`P2-09`, dispatch is `wh_shipments:dispatch` posting `TRANSFER_DEPART` into transit. `FR-189`: *"dispatch is the only relief event; for a transfer the relief is into transit"* | `V510040` | no |
| `RJ-004` | **BLOCKER** | 21 v1 workflow status columns have no values and no ladder | **COVERED-uncited** | R24 Appendix A is **adopted** as the ladder text, with `RK-001`'s `REQUESTED` on transfers (§3.3) and `RJ-011`'s `VOIDED` on handovers; each creating task carries its ladder in §0.11's format plus the acceptance line *"no state without an inbound transition; no non-terminal state without an outbound one"*: `P1-12` `P1-13` `P1-16` `P1-17` `P2-01` `P2-02` `P2-04` `P2-06` `P2-08` `P2-10` `P2-12` `P2-13` `P2-15` `P2-17` `P2-25` `P2-26`. `BUILD-SPEC-SCREENS.md` §0.11 carries the table | each creating migration | no |
| `RJ-005` | MAJOR | Eleven v1 documents change state gated by no verb permission | **NEEDS-AMENDMENT** | R24's table becomes §10.2 rows. **P1 verbs** ride `P1-20`'s `V511000`/`V511001` (receiving sessions, quality-inspection scrap approval, receipt reversals). **P2+ verbs** each claim one `WH-206` pair (§4.0): `P2-01` `P2-02` `P2-04` `P2-10` `P2-12` `P2-13` `P2-15` and `P3-11`. Adapter verbs ride their own bands (`P2-25` `V520100`+, `P2-26` `V521100`+). Scrap approval reuses `:approve` semantics with approver ≠ actor (`FR-408`). Base verbs `whb_accounting_handovers:void` and `warehouse:warehouses:change_registration` ride `P0-15`'s `V501000` | `V511201` onward | no |
| `RJ-006` | MAJOR | Five v1 states have no way out | **COVERED-uncited** | `P2-02` `IN_TRANSIT → CANCELLED` posts `TRANSFER_RETURN` (a new base movement type seeded by **`P0-04`** in `V500003`); **`P1-05`** writes the `whb_locations.status` ladder — count freeze sets `COUNTING`, post or cancel restores the prior status, `FROZEN` is set only by the stocktake window (`FR-157`); `P2-13` `PICKED → CANCELLED` refused with `409 STAGED_STOCK` until de-staged; `P2-12` return receipt `POSTED → REVERSED` before disposition; `P2-10` shipment Cancel only before `DISPATCHED` | each creating migration | no |
| `RJ-007` | MAJOR | Hard reservations expire mid-pick | **COVERED-uncited** | `expires_at` applies to `SOFT` rows only; `HARD` rows end only by consume, cancel or explicit release; ageing shows stale `HARD` rows separately — `P0-09`, `P2-07`, `P2-09`; `WH-SC-317` | `V500033` | no |
| `RJ-008` | MAJOR | A lot can be held three ways | **COVERED-uncited** | a lot hold is **only** a `wh_holds` row; `whb_lots.status_code` keeps lifecycle states set by jobs (e.g. `EXPIRED`) and is never a hold; `hold_reason_code_id` dropped; the status-change movement is for physical segregation only — `P1-07`, `P2-03`, `P2-07`; `WH-SC-139` re-pointed | `V500018` | no |
| `RJ-009` | MAJOR | The per-customer shelf-life-at-ship guard has no column | **COVERED-uncited** | **lighter than R24's rule table** (§3.7): nullable `min_shelf_life_ship_pct` on `whb_counterparties` (`P1-08`, `V500011`) and `whb_channels` (`P1-11`, `V500051`), resolved counterparty → channel → item — `P1-03`, `P2-05`; `WH-SC-134` names the order | `V500011` | no |
| `RJ-010` | MAJOR | Blind returns and returns to vendor carry no cost rule | **COVERED-uncited** | matched return reverses the consumption; unmatched takes the site's current method cost with `cost_basis = RETURN_UNMATCHED`, reported; return to vendor with `origin_grn_id` relieves that receipt's layer — `P2-12`, `P2-13`, `P2-16`; `WH-SC-318` | `V500021` for the value | no |
| `RJ-011` | MAJOR | A rejected handover can only be retried and can block close or strand a billing run | **COVERED-uncited** | `REJECTED → VOIDED` via `whb_accounting_handovers:void`, approver ≠ requester, only when the movement is reversed or reclassified `NOT_APPLICABLE`; reversing a never-posted movement voids both envelopes; `VOIDED` is outside the close guard; a billing run may cancel once its AR handover is `VOIDED` — `P0-12`, `P2-18`, `P2-22`, `P5-05` | `V500042` | no |
| `RJ-012` | MAJOR | Five dated columns have no job | **COVERED-uncited** | five rows in **`P0-13`**'s register, each job in its owning task: `expected_arrival_date` (`P2-02`), `wh_rmas.expiry_date` (`P2-12`), `whb_lots.retest_date` (`P2-05`), `wh_count_programs.next_scheduled_date` (`P2-04`), `wh_reconciliation_exceptions.age_days` computed on read (`P2-06`) | each task | no |
| `RJ-013` | MINOR | A v1·P1 scenario depends on v1.1 kitting | **COVERED-uncited** | `WH-SC-135` split: `P1-07` keeps shipments and locations; the kit half moves to `P3-11`/`P5-19` | — | no |
| `RJ-014` | MINOR | Four vocabulary drifts | **COVERED-uncited** | (a) `return_type` becomes the `RETURN_TYPE` code list seeded from `FR-270`'s ten; `WH-SC-057` uses a seeded value; (b) `suggested_source` = `TRANSFER` everywhere, `WS-141` drops `FR-254`; (c) `ITEM_MISMATCH` joins `P1-13`'s column; (d) `FR-133` reads *one inspection series per GRN; a re-inspection takes its own number* — `P2-12`, `P1-13`, `P2-15`, `P1-14` | — | no |
| `RJ-015` | MINOR | Re-attaching a reservation at pick has no mechanism | **COVERED-uncited** | release the row (reason `PICKED`) and create a new one at staging with the same holder quad, in the pick's writer transaction — `P0-09`, `P2-09` | `V500033` | no |
| `RJ-016` | MINOR | Counts with no programme have no tolerance | **COVERED-uncited** | install defaults `warehouse.count.default_tolerance_pct`/`_value` in `P1-20`'s `V511200`, inherited when no programme — `P2-04` | `V511200` | no |
| `RJ-017` | MINOR | When quarantined stock is put away is unstated | **COVERED-uncited** | the putaway task is created at QC release, for the released quantity — `P1-14`, `P1-15` | — | no |
| `RJ-018` | MINOR | A v1 PO-cancel guard reads a v1.1 object | **COVERED-uncited** | in v1 the guard reads receiving-session arrival; the ASN clause activates in `P3-05` — `P1-12`, `P3-05` | — | no |

### 2.4 R25 · `RK-` — competitor gap, round 3

| Finding | Sev | The defect, in one line | Disposition | Owning file — and what it gains | Deadline | Person? |
|---|---|---|---|---|---|---|
| `RK-001` | MAJOR | A transfer can only be pushed by the sender; the request-and-approve half is paid for in the schema and never built | **NEEDS-AMENDMENT** | **`P2-02`** gains `FR-462`, `WH-SC-314` and the verbs `wh_transfer_orders:request`/`:approve`/`:reject` (its `V511202`/`V511232`): a user scoped to the **destination** creates a transfer in `REQUESTED`; a holder of `:approve` scoped to the **source** approves, part-approves (line `approved_quantity` < requested) or rejects with a reason; approval creates the `TRANSFER` demand order and so reserves (`RJ-003`); the unapproved remainder writes `wh_insufficient_stock_log` with `source_type = TRANSFER_REQUEST`. **`P1-17`** gains `REQUESTED` in the status vocabulary and `approved_quantity` on the line (`V510031`). One verb and one ladder with `RJ-005` (§3.3). `P5-18`'s sister suggestion later **creates** requests | `V510031` | no |
| `RK-002` | MAJOR | Nothing says whether a branch may sell from another branch's warehouse | **MERGED-into-`RG-001`** | contributes the counter-sale and job-issue half of the serving-branch rule (§3.2), carried as `FR-461` by `P2-25`, applied in `P2-26`; its *"do not build a service-map table"* is **overtaken by `D-14`** — the junction exists anyway, and the GSTIN rule is kept on top of it | before `P2-25` | no |
| `RK-003` | MINOR | v1 ships an ABC count programme; nothing computes the class until v3 | **NEW-TASK** `P3-25` | the simple recompute at v1.1 (`FR-463`, `V500069`, `WH-SC-320`); `P2-04` labels `programType = ABC` *"uses manually maintained classes"* in v1; `P6-02` keeps velocity/XYZ | before `P3` | no |
| `RK-004` | MAJOR | A reorder point is a threshold column with no job | **NEEDS-AMENDMENT** | **`P2-15`** — `wh_replenishment_runs.run_type` gains `SCHEDULED`; a per-site schedule (nightly default, `warehouse.replenishment.default_schedule` in `P1-20`'s `V511200`) runs it with a `whb_job_runs` record; a run that produces suggestions notifies the site's buyer role in-app and by email (`RH-007`'s first notification); no auto-PO. `FR-165` enumerates quantity thresholds; `FR-253` states the schedule; `WH-SC-315` | before `P2-15` | no |
| `RK-005` | MINOR | Drop-ship: "decide in v1, implement in v2" was never decided | **DECIDED** — **`OD-18`** (escalated) | R25's decision text is the recommendation on the row. The v2 flow is placed now so it is not lost: **`P5-09`** gains `FR-467` and `WH-SC-326`, gated on `OD-18`. The movement type is **not** seeded in v1 (movement types are `V500003`, not `V500013` as R25 wrote) — `D-10` lets any module seed it when `OD-18` is answered | first drop-shipped purchase | **yes** |
| `RK-006` | MINOR | No B2B trade-customer portal | **NEW-TASK** `P5-25` | a second persona on `FR-284`'s surface, scoped by customer counterparty through the single resolver; availability as a flag, never a quantity; demand orders in `DRAFT`; status and document download; no pricing engine, no payment (`FR-464`, `WS-240`, `WH-SC-321`). A separate task so the 3PL portal (`P5-08`) ships alone | before `P5` | no |
| `RK-007` | MINOR | A transfer between two legal entities is neither supported nor refused | **NEW-TASK** `P5-26` | v2 linked pair (`FR-465`, `WH-SC-322`). **The v1 half is a guard in `P1-17`**: a transfer's two sites belong to one company; `WS-090`'s destination picker is filtered to the source's company; `422 CROSS_COMPANY_TRANSFER`; `WH-SC-319` | `V510031` for the guard | no |
| `RK-008` | MINOR | Every approval is one step | **NEW-TASK** `P5-27` | `wh_approval_levels` — ordered typed rows, not a workflow engine (`FR-466`, `WS-241`, `WH-SC-323`) | before `P5` | no |
| `RK-009` | MINOR | The benchmark has no row for `RK-001`…`RK-008`, and an R3 `UNVERIFIED` is answerable | **COVERED-uncited** | `COMPETITOR-BENCHMARK.md` gains the eight rows and R25 §4.2's four declines. **`GAP-REGISTER-R3.md` §5.1's transfer-price bullet is answered here**: `wh_transfer_orders` carries `transfer_price_basis`, `transfer_price` and `cost_value` (`DATA-MODEL.md:1003`); R3 is not edited | — | no |

### 2.5 R26 · `RL-` — extensibility and future-proofing

| Finding | Sev | The defect, in one line | Disposition | Owning file — and what it gains | Deadline | Person? |
|---|---|---|---|---|---|---|
| `RL-001` | **BLOCKER** | `duty_status` is in the position key, `L-1`'s grain and every cost layer, and has no registry; its values are Indian regimes | **NEEDS-AMENDMENT** | **`P0-05`** — `whb_duty_statuses` (registry 15; `is_duty_paid`, `is_allocatable_to_domestic_demand`, `requires_licence`, `commingle_group`) in `V500005`; **base seeds `DOMESTIC` only**; `BONDED` leaves the stock-status seed. **`P0-02`**/**`P0-17`**: `duty_status VARCHAR(40) NOT NULL DEFAULT 'DOMESTIC' REFERENCES whb_duty_statuses(code)` in `V500030`/`V500021`. **`P4-07`** seeds `BONDED` `MOOWR` `SEZ` `FTWZ` `EXPORT_UNDER_BOND` in `V540140`. `IRR-12`'s list moves to the India pack; `I-18` enumerates seventeen registries; `WH-SC-327` | **`V500005`**, before `V500021` | no |
| `RL-002` | **BLOCKER** | `DATA-MODEL.md` and the port contract specify two different outboxes; `P0-11` builds from the one that loses | **NEEDS-AMENDMENT** | **`P0-11`** (`V500040`) — `whb_outbox` takes `PC-36`'s column set verbatim with `event_version`; **`payload TEXT` is dropped and no `payload_ref` is added in v1** (the event *is* its typed columns; a consumer wanting more calls the lineage `GET`) — lighter than R26's proposal (§3.7); `whb_event_types` (registry 17) seeded with `PC-42`'s codes plus `document.status_changed`; `accepted_event_version` on subscriptions. **`P0-12`** — `envelope_version` on handovers. Lands in the same migration as `RD-002`'s columns | **`V500040`** — from the first emitted event | no |
| `RL-003` | MAJOR | Catalogue codes are one namespace, seeds are `ON CONFLICT DO NOTHING`, and the contract's own example collides silently | **COVERED-uncited** | **`P0-04`** — a module inserts only codes it owns; the guarded seed idiom (`DO NOTHING` then `RAISE` if the code exists under another `owning_module`); `PC-72` assertion 7; `whb_reason_codes` keyed `uk(context, code)` in `V500004`; `PORT…` §7.3's example corrected | `V500004` | no |
| `RL-004` | MAJOR | Location, LPN and item codes and every formatted number are install-wide | **COVERED-uncited** | R26 option **(b)** adopted: `whb_locations` `uk(warehouse_id, code)` only, scan resolution scoped by the session's or device's site, `AMBIGUOUS_LOCATION` on a cross-site scan (`P1-05`, `P1-06`, `P1-02`); `whb_owners`/`whb_warehouses` keep only `uk(company_id, code)` (`P0-06`, `P1-05`); `whb_number_series_issued` `uk(series_id, formatted_number)` (`P1-09`); `whb_items.code` a system-generated immutable surrogate (`P1-01`). **Partial decline:** `whb_lpns.code` stays install-wide — an LPN travels between sites and is an SSCC-shaped plate (§3.7). `RE-002`'s `VIRT-<PURPOSE>-<SITE CODE>` convention stands; the site suffix is now naming, not a key workaround | `V500012`–`V500020` | no |
| `RL-005` | MAJOR | `FR-059` says the identifier table is not globally unique; its key is | **COVERED-uncited** | **`P1-02`** — `owner_id` denormalised onto `whb_item_identifiers`; key `uk(identifier_type, normalised_value, owner_id, counterparty_id, channel_id) NULLS NOT DISTINCT`; `identifier_type` from the `IDENTIFIER_TYPE` code list; resolver order session owner → counterparty context → `AMBIGUOUS_IDENTIFIER` listing candidates. One line in `P1-12`, `P1-13`, `P2-25` | `V500016` | no |
| `RL-006` | MAJOR | Eleven vocabularies outside the registries carry no open-or-closed ruling; the house default is `CHECK (status IN …)` | **NEEDS-AMENDMENT** | **`P0-05`** — `whb_code_lists` + `whb_code_list_values` in `V500010` (one generic open list for low-behaviour vocabularies, seedable by any module under `RL-003`'s guard; referencing columns carry a constant `<col>_list` column and a composite FK); `DATA-MODEL.md` §2.1.1 gains a **Vocabulary classification** table tagging every enumerated column `REGISTRY`, `CODE-LIST` or `CLOSED-SYSTEM`; **the two partitioned ledger tables carry no `CHECK (… IN …)` at all**. Lists seeded in v1: `DEMAND_TYPE`, `RETURN_TYPE`, `CHANNEL_KIND`, `ACTOR_TYPE`, `PRINT_TEMPLATE_KIND`, `PRINT_FORMAT`, `IDENTIFIER_TYPE`, `ATTRIBUTE_SUBJECT`, `ADDRESS_ROLE`, `CUSTODY_ROLE`, `BARCODE_FORMAT` (the last replaces the never-defined `whb_barcode_formats`, so `P3-24`'s row is a code-list row). One line in `P0-02`, `P1-02`, `P1-05`, `P2-07`, `P2-14`, `P2-25`, `P3-24` | **`V500010`**; ledger half `V500030` | no |
| `RL-007` | MAJOR | The attribute mechanism reaches items and movement lines only, and the line side table has two shapes at `PNR-1` | **NEEDS-AMENDMENT** | **`P0-05`** — `applies_to` becomes the `ATTRIBUTE_SUBJECT` list (`ITEM`, `MOVEMENT_LINE`, `LOT`, `SERIAL`, `LPN`, `LOCATION`, `COUNTERPARTY`, `DOCUMENT`); `whb_entity_attribute_values` (four typed value columns, `uk(entity_kind, entity_id, attribute_key_id)`) in `V500010`; install-created keys are the product's custom-field answer. **`P0-02`** — `whb_movement_line_attributes` takes **`DATA-MODEL.md`'s four typed columns**; `IRREVERSIBLE.md` §4.2 and `PORT…` §2.5 amended. **`P1-13`** captures `LOT`-kind keys on the GRN line in v1, because a lot fact not captured at receipt is unbackfillable. No `EVENT` subject (§3.7) | **`V500030`** for the line shape | no |
| `RL-008` | MAJOR | Three core columns are named for India's tax scheme | **COVERED-uncited** | v1 renames, all free now: the ledger line snapshot becomes `tax_classification_code VARCHAR(20)` + `tax_classification_scheme VARCHAR(20)` (`P0-02`, `V500030`, and the wire in `PORT…` §2.5); `whb_reason_codes.itc_treatment` → `tax_treatment_code`, values seeded by `warehouse-india` (`P0-04`, `P2-IN-01`); `whb_uoms.gst_uqc_code` **stays** in v1 with the stated rule that a second scheme goes to the v2 side table. The three side tables are `RG-020`'s, in `P5-24` | **`V500030`** | no |
| `RL-009` | MAJOR | The mobile schema file re-closes every registry the web leaves open | **NEEDS-AMENDMENT** | `FR-382` is re-versioned **v1 · P0** and reworded to a rule; **ownership moves from `P3-04` to `P0-16`** (coordinated, §4.1); `PC-67` gains the mobile sentence; one line in `P0-04`, `P1-02`, `P1-19`, `P2-03`, `P3-01`, `P3-04` | before the first v1 mobile screen | no |
| `RL-010` | MAJOR | Allocation, putaway and negative-stock rules are edited in place under ids that reservations and tasks record | **COVERED-uncited** | a rule row referenced by any reservation or task is **immutable** (`I-24`, `I-9`'s shape); an edit is copy-on-write with `version_no` + `supersedes_id` — `P0-09` (`V500033`), `P0-02` (`V500031`), `P1-15` (`V510017`), `P2-07` (`WS-048` shows history) | `V500031` | no |
| `RL-011` | MAJOR | Only the ledger is partitioned | **COVERED-uncited** | partitioned at `CREATE`, reusing `P0-02`'s partition job: `whb_stock_position_snapshots` by `snapshot_date` (non-zero positions only, stated) in `V500045` (`P0-03`); `whb_outbox` by `recorded_at` with PK `(cursor, recorded_at)` and `whb_outbox_deliveries` in `V500040` (`P0-11`); `whb_inbound_messages` and `whb_movement_batch_results` in `V500041` (`P0-08`); `whb_audit_events` by `occurred_at` with PK `(sequence_no, occurred_at)` in `V500043` (`P0-13`); each gets a retention-class row (`P4-09`); `wh_shipment_tracking_events` at build (`P5-11`) | `V500040`–`V500045` | no |
| `RL-012` | MAJOR | `OD-3`'s consequence — configuration must travel between databases — is owned by no task | **NEEDS-AMENDMENT** | v1: **`P0-04`** — install-created configuration rows carry `owning_module = 'INSTALL'`. v1.1: **`P3-18`**'s header gains the *configuration package* kinds on the import framework (`FR-414` amended). R26's *"`P0-10` (`V500046`)"* is `P1-10` | `P0-04` | no |
| `RL-013` | MINOR | Code-keyed FKs are `ON UPDATE CASCADE` into an append-only ledger | **COVERED-uncited** | `DATA-MODEL.md:132` becomes `ON UPDATE RESTRICT`; a code is corrected by `Z-005`'s retire-and-reseed; `Z-004`'s *Frozen when* gains registry `code` — `P0-02`, `P0-04`, `P0-05`, `P1-02` | `V500030` | no |
| `RL-014` | MINOR | Document ladders have no status-changed event and no pre-transition hook | **NEEDS-AMENDMENT** | **`P3-22`** (v1.1) gains `document.status_changed` emitted by the single transition helper and a `WhTransitionGuard` `List<T>` SPI (base ships none); the event code is seeded in v1 by `P0-11` (`RL-002`) | `V500040` for the code | no |
| `RL-015` | MINOR | Registry rows carry a single-language name | **NEW-TASK** `P5-28` | `whb_registry_translations` (`FR-469`, `V500071`, `WH-SC-325`); `PC-69`'s fallback reads it first | before `P5` | no |
| `RL-016` | MINOR | Every time-driven rule reads the wall clock | **COVERED-uncited** | **`P0-13`** — every warehouse service takes an injected UTC `Clock`; the `ArchitectureInvariantsTest` fails a bare `Instant.now()`/`LocalDate.now()`/`LocalDateTime.now()` under `ai.warehouse*`; `P0-01`'s module skeleton carries the scanner | `P0-13` | no |
| `RL-017` | MINOR | The management API the handhelds call is unversioned | **COVERED-uncited** | **`P3-04`** (v1.1) — `PORT…` §10.2's additive-only table covers every endpoint a mobile screen calls, marked in each mobile block; `warehouse.mobile.min_app_version` checked at login and sync with `426 CLIENT_UPGRADE_REQUIRED`; `P0-16`'s mobile section points to it | before `P3` | no |

### 2.6 The disposition tally

| Bucket | Count | Findings |
|---|---:|---|
| **`COVERED-uncited`** | **36** | `RG-019` `RG-021`…`RG-027` · `RH-003` `RH-010` `RH-011` `RH-012` · `RJ-002` `RJ-004` `RJ-006`…`RJ-018` · `RK-009` · `RL-003` `RL-004` `RL-005` `RL-008` `RL-010` `RL-011` `RL-013` `RL-016` `RL-017` |
| **`NEEDS-AMENDMENT`** | **30** | `RG-001`…`RG-009` `RG-015` `RG-016` `RG-017` · `RH-002` `RH-004` `RH-006` `RH-007` `RH-008` `RH-009` · `RJ-003` `RJ-005` · `RK-001` `RK-004` · `RL-001` `RL-002` `RL-006` `RL-007` `RL-009` `RL-012` `RL-014` |
| **`NEW-TASK`** | **12** | `RG-010` `RG-011` `RG-012` `RG-013` `RG-014` `RG-018` `RG-020` → `P5-24` · `RK-003` → `P3-25` · `RK-006` → `P5-25` · `RK-007` → `P5-26` · `RK-008` → `P5-27` · `RL-015` → `P5-28` |
| **`DECIDED`** | **1** | `RK-005` → **`OD-18`** |
| **`MERGED`** | **4** | `RH-001` `RH-005` `RJ-001` `RK-002` → `RG-001` |
| **`DECLINED`** | **0** | — thirteen partial refusals and overrulings are written into their rows and §3.7 |
| **Total** | **83** | |

---

## §3 · Reconciliations — where the lenses overlap or disagree

### 3.1 The junction — `RG-001` is canonical

Four findings in three lenses describe the same object. **`RG-001`** carries the DDL, the constraints, the
roles and the sixteen readers (R22 §1.2); the other four merge into it and each contributes one thing:

| Merged | What it adds to `RG-001` | What of it is overruled |
|---|---|---|
| `RJ-001` | the workflow reading — transfers, counter sale, scope, numbering, envelope, reports (rules R1–R5) | R1's `posting_date` → `occurred_at`; R4 not adopted (§3.7) |
| `RH-001` | fail-closed on an unlinked site; `allowedWarehouseIds` as the bound set; accessories' unlinked-is-shared arm and `is_primary` meaning refused by name | nothing |
| `RH-005` | *"the `REGISTERED` link is the only branch any tax, numbering or supply rule reads"*; the `whin_gstin_profiles` copy kept with an equality check | *"at `dispatched_at`"* → frozen at creation (`FR-305`), see §3.7 |
| `RK-002` | the counter-sale and job-issue half of the serving-branch rule, and the refusal code | *"no service-map table"* — overtaken by `D-14` |

R22's own sub-proposals are adopted with three amendments from this section: the transit-pool rule of
R22 §1.2.3 is **superseded** by `RJ-002` (§3.4); R22 §1.2.4 row 6's *"offers Raise transfer"* becomes
*"offers Raise request"* so the counter clerk uses `RK-001`'s object; and `I-22`/`I-23` are numbered here
(§4.0) rather than left to `DATA-MODEL.md`.

### 3.2 The one serving-branch rule — for counter sales, job issues, orders and draws across GSTINs

Written once, as `D-14` item 3 and as **`FR-461`**:

1. **Every stock-consuming document's tax registration is the fulfilling site's `REGISTERED` branch** at the
   document date.
2. **Handed over at the requesting branch** — a counter sale, a job issue to a workshop. It posts directly
   from a site **only when** the requesting branch holds a current `REGISTERED` or `SERVING` link to that
   site **and** its GSTIN equals the site's `REGISTERED` GSTIN. The adapter compares `branches.gst_number`,
   because it cannot read `whin_` (`D-1`).
3. **A `SERVING` branch under a different GSTIN draws by transfer, never by a direct sale.** The draw is a
   **cross-GSTIN supply**: a transfer with `is_taxable_supply = true`, source branch = the site's
   `REGISTERED` branch, destination = a site `REGISTERED` to the serving branch, carrying its challan or
   tax invoice and, above the threshold, an e-way bill. The counter refuses a direct sale with
   **`422 CROSS_GSTIN_COUNTER_SALE`** and offers *Raise request* (`RK-001`). A serving branch that stocks
   nothing of its own needs one small site registered to it — which the statute requires anyway, because
   goods received under another registration are received at a place of business of that registration.
4. **Despatched from the site to a third party** — a demand order shipped to a customer. It may be taken by
   any branch with a visibility link and is billed from the site's `REGISTERED` GSTIN at despatch; the
   ordering branch is a label (R22 §1.2.4 row 7).
5. **Same GSTIN, different branch** — a `SERVING` issue under the same registration is a non-supply challan
   (R22 §1.2.3), not a transfer invoice.

### 3.3 Transfer approval — `RK-001` against `RJ-005`

`RJ-005` found `requires_approval`/`approved_by` dead and no verb; `RK-001` found no request and no approval.
**One verb, one ladder, one owner (`P2-02`):**

- verbs `wh_transfer_orders:request`, `:approve`, `:reject` beside the existing `:dispatch` and
  `:receive`, plus `:report_variance` and `:cancel` from `RJ-005`, all seeded in `P2-02`'s `V511202`;
- the ladder `REQUESTED → APPROVED | REJECTED`, `DRAFT → APPROVED` where `requires_approval`, then
  `ALLOCATED · IN_TRANSIT · PARTIALLY_RECEIVED · RECEIVED · CLOSED · CANCELLED` (R24 Appendix A);
- **part-approval is a line quantity, not a state**: `approved_quantity` below the requested quantity on an
  `APPROVED` header. R25's `PARTIALLY_APPROVED` is not adopted;
- `:approve` is scoped to the **source** site and `FR-408` applies. `REQUESTED` may be created only by a
  user scoped to the **destination** site;
- approval creates the `TRANSFER` demand order, and the demand order reserves (`RJ-003`). There is
  exactly one reservation path.

### 3.4 The transit location lives at the source site — `RJ-002`

Five documents put the per-transfer transit location under a separate `TRANSIT-WH` site; the FRD
(`FR-147`, `FR-148`) and `WS-090` put it at the sending site. **The FRD wins.** It keeps in-transit value in
the sender's grain (`FR-236`), and it keeps its classification automatic: a line at the transit location
resolves to the source site's `REGISTERED` link, which is the transfer's frozen source branch. So R22 §1.2.3's
special rule for a transit pool's administrative registration is no longer needed. Two consequences are
carried:

- `TRANSIT-WH` leaves `PORT-AND-ADAPTER-CONTRACT.md`, `SCENARIO-CATALOGUE.md`'s cast, `issues/p2-02.md` and
  `issues/p6-08.md`;
- `RE-002`'s transit-site seeding shrinks to one location type, `IN_TRANSIT`, created per transfer at
  dispatch.

The scope conflict is closed in `P1-18`. The receiving verb authorises **that** transfer's transit
location, and nothing else at the source site.

### 3.5 Link, never mirror — `RH-003`

`PLATFORM-DEPENDENCIES.md` §1.1 (*"a site **is** a platform branch"*) is wrong under any cardinality and is
corrected. R22 §4 refusal 4 (*"a site may be `REGISTERED` to a `WAREHOUSE`-type branch"*) agrees with
`RH-003`. The narrowing is taken from `RH-003`: such a branch row is created **only** when the site is itself
a GST place of business that no existing branch carries. `whb_warehouses.code` never derives from, copies
or validates against `branch_code`, and R14's refusal of that collision stands.

### 3.6 RL against RG — the cardinality boundary

R26 states that it does not cover scalar-versus-M:N choices and refers them to R22 (R26 §4 item 1). The
boundary held, and there is **no finding the two lenses dispose of differently**. Four places touch:

| Where | `RG` says | `RL` says | Resolution |
|---|---|---|---|
| Tax codes | `RG-020`: side tables for item and UoM, v2 | `RL-008`: rename the ledger snapshot and the reason-code column now; UoM side table optional | **v1** is `RL-008`'s two renames. **v2** is `RG-020`'s three side tables in `P5-24`, which also absorb `RL-008`'s reason-code treatment table |
| History | `RG-021`: date every junction, add `EXCLUDE` | `RL-010`: rule rows are copy-on-write | **Both.** They cover different classes. A junction is an association (dated); a rule row is configuration that a fact recorded (versioned and immutable once referenced) |
| Variant axes | `RG-009` | R26 §4 item 1 refused to R22 | `RG-009` |
| Identifier scope | R22 §3: identifiers are already the association | `RL-005`: the key contradicts `FR-059` | **`RL-005`'s key.** It is a key correction, not a cardinality change |

`RL-006`'s code lists also absorb the open role vocabularies `RG-003` and `RG-004` introduce
(`ADDRESS_ROLE`, `CUSTODY_ROLE`). `RG-002`'s `place_role` stays a closed statutory `CHECK` under `OD-5`.

### 3.7 The remaining conflicts, and the lighter shapes taken under user decision (3)

| # | Conflict or heavier proposal | Taken | Why |
|---|---|---|---|
| a | `RH-005` freezes transfer branches at `dispatched_at`; `FR-305` freezes them at creation | **creation** | R22 §1.2.6 refuses a registration change while the site holds stock under a different GSTIN, so a created-but-undispatched transfer cannot go stale |
| b | `RJ-001` R1 resolves the `REGISTERED` branch at `posting_date` | **`occurred_at`** | `posting_date` is the accounting clock (`L-13`). Registration follows where the goods physically were |
| c | `RJ-001` R4 restricts receive, count, adjust and close to the `REGISTERED` branch's users | **not adopted** | a service-branch storekeeper who works in the shared godown would be locked out (R23's own example). Operating rights are permissions plus `RA-001`'s grants — one mechanism |
| d | `RH-004` gives `whb_company_branches` an `is_active` flag | **effective-dated** | `D-14` item 1, and R22 §1.3 rule 3 (no `is_active` on a dated junction) |
| e | `RL-002` replaces `payload TEXT` with a `payload_ref` into typed attribute rows (`EVENT` subject) | **typed columns only, no payload in v1** | the dimensions `PC-36` names are the event. A side table as large as the outbox, for facts no v1 consumer reads, is over-engineering. `PC-37`'s ban on an opaque blob is met by having no blob |
| f | `RJ-009` proposes a `whb_shelf_life_ship_rules` table with a category axis | **two nullable columns** (counterparty, channel) | `FR-161` point 3 and `WH-SC-134` need customer and channel only. No new screen |
| g | `RL-004` could scope LPN codes by owner × site | **LPN codes stay install-wide** | a pallet crosses sites on a transfer, and its code is an SSCC-shaped plate |
| h | `RL-006` could add ten registries | **one generic code list** | R26's own minimum. Registries stay for vocabularies with behaviour flags |
| i | `RL-005` could add an identifier-type registry with a `uniqueness_scope` | **key change + code list** | the scoped key already makes a supplier part number unique per supplier and an EAN unique per owner |
| j | `RK-005` seeds the drop-ship type in `V500013` | **not seeded in v1** | movement types are `V500003` (`P0-04`), and the decision is open (`OD-18`) |
| k | `RJ-003` puts `demand_order_id` in `V510031`/`V510020` | **`ALTER` in `V510040`** | `wh_demand_orders` is created by `V510040`, which runs after both |
| l | `RL-012` names `P0-10 (V500046)` | **`P1-10`** | `V500046` is `P1-10`'s import framework |
| m | R23 asks for R18 §4 and R6's source list to be edited | **recorded here** | reviews are dated records |

---

## §4 · The fold plan

**Four agents, four disjoint partitions, no agent allocates an id.** Every id a fold needs is in §4.0.
Where two partitions must say the same thing, §4.1 names the pair and the exact text.

### 4.0 Allocations — taken here, from the markers the files declare

```bash
# the markers, read before allocation (2026-09-10)
grep -ohE '\bFR-[0-9]{3}\b' docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md | sort -u | tail -1   # FR-459
grep -n 'New ids continue from' docs/SCENARIO-CATALOGUE.md                                  # WH-SC-306
grep -n 'next free is' docs/DECISIONS.md                                                    # WS-238
grep -ohE '\bIRR-[0-9]{2}\b' docs/IRREVERSIBLE.md | sort -u | tail -1                       # IRR-63
grep -c 'whb_warehouse_grants' issues/p1-18.md          # 0 — round 3 is unfolded, so its WS-238/WS-239 stay reserved
for v in V500037 V500068 V500069 V500070 V500071 V510220 V510221 V510222 V511180; do \
  grep -l "$v" issues/p*.md; done                        # no task header claims any of them
grep -ohE 'V5112[0-9]{2}' issues/p*.md | sort -u         # V511200 only — the WH-206 pairs are all free
```

**Requirements** — ten rows for a new `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` **§6.28 Round-4 amendments**.
The next free id afterwards is **`FR-470`**.

| Id | Requirement (one sentence for P-CORE to expand) | Module | Ver · Phase | Owner | Closes |
|---|---|---|---|---|---|
| **`FR-460`** | A warehouse is linked to platform branches through `whb_warehouse_branches`. Roles come from `whb_warehouse_branch_roles`, with exactly one `REGISTERED` link at every instant, which supplies the site's GSTIN, branch-scoped series and statutory attribution. Classification reads the link at `occurred_at`; access reads today's links. A registration change closes one row and opens the next, maker–checker | base | v1 · P1 | `P1-05` | `RG-001` `RH-001` `RH-005` `RJ-001` |
| **`FR-461`** | The serving-branch rule of §3.2: a document handed over at the requesting branch posts directly only on a same-GSTIN link. Across GSTINs the draw is a taxable transfer (`422 CROSS_GSTIN_COUNTER_SALE`), and a despatched demand order bills from the site's `REGISTERED` GSTIN | ad-dealer · ad-services | v1 · P2 | `P2-25` | `RK-002` `RG-001` |
| **`FR-462`** | A branch that needs stock raises a transfer **request** against another site. The source approves it, part-approves it by line quantity, or rejects it with a reason. Approval reserves through the demand model, and a refused remainder is recorded as insufficient-stock demand | app | v1 · P2 | `P2-02` | `RK-001` |
| **`FR-463`** | A simple ABC recompute runs at v1.1 over twelve months of issue value per item × site, with two Pareto cut-offs held on the site. The previous class is kept for one cycle, and each run writes a `whb_job_runs` record | base+app | v1.1 · P3 | `P3-25` | `RK-003` |
| **`FR-464`** | A trade-customer portal is a second persona on `FR-284`'s surface, scoped by customer counterparty through the single resolver. It offers availability as a flag, `DRAFT` sales demand orders, status and documents. It has no pricing engine and no payment | app | v2 · P5 | `P5-25` | `RK-006` |
| **`FR-465`** | A movement of goods between two companies in one install is a demand order in one company plus a purchase order in the other, created in one action and cross-referenced in the source quad, priced from the transfer-price columns. It is never a transfer | app | v2 · P5 | `P5-26` | `RK-007` |
| **`FR-466`** | Approval levels are ordered, typed rows keyed by document kind, value band and sequence, each naming its permission. The existing approve actions read them. `FR-408` applies at every level, and no user approves one document twice | app | v2 · P5 | `P5-27` | `RK-008` |
| **`FR-467`** | A drop-shipment posts as `OD-18` decides. The recommended shape is one movement: `−q` at `SUPPLIER`, `+q` at `CUSTOMER`, with both documents in the source quad and serial and lot capture mandatory where the item is tracked | app | v2 · P5 | `P5-09` | `RK-005` |
| **`FR-468`** | The v2 association junctions are built dated per `D-14`: UoM defaults, site-scoped supplier preference, warehouse and owner companies, owner-set cages, tax-scheme codes and configuration scopes | base+app | v2 · P5 | `P5-24` | `RG-010` `RG-011` `RG-012` `RG-013` `RG-014` `RG-018` `RG-020` |
| **`FR-469`** | Registry rows carry per-locale names in `whb_registry_translations`, read before the row's own name | base | v2 · P5 | `P5-28` | `RL-015` |

**Scenarios** — twenty-two rows for a new `SCENARIO-CATALOGUE.md` **§3.22 Round-4 additions**. The §5
rule 3 marker moves to **`WH-SC-328`**.

| Id | Given / When / Then, in one line | Ver · Phase | Closed by |
|---|---|---|---|
| **`WH-SC-306`** | A site holds stock and its `REGISTERED` branch is changed to a branch under a different GSTIN → refused. The site is emptied by transfer and the change is repeated → accepted, and the history row is closed and the next opened at one instant | v1 · P1 | `P1-05` |
| **`WH-SC-307`** | A site is re-registered mid-quarter → the Rule 56 account for each GSTIN covers only its own range, split at the switch instant | v2 · P4 | `P4-03` |
| **`WH-SC-308`** | A `SERVING` branch under another GSTIN draws 10 EA → a transfer with `is_taxable_supply = true`, a challan or invoice, and an e-way bill above the threshold | v1 · P2 | `P2-02` |
| **`WH-SC-309`** | A same-GSTIN `SERVING` counter sells from a shared site → allowed, billed under the site's `REGISTERED` GSTIN. A different-GSTIN counter → `422 CROSS_GSTIN_COUNTER_SALE` with *Raise request* | v1 · P2 | `P2-25` |
| **`WH-SC-310`** | Two branch-scoped users both see a shared site. A user whose branches link to no site gets zero rows, not every row | v1 · P1 | `P1-18` |
| **`WH-SC-311`** | A `REGISTERED` link to a branch whose GSTIN state differs from the site's `state_code` → refused by the India validator | v1 · P2-IN | `P2-IN-01` |
| **`WH-SC-312`** | A movement whose `occurred_at` falls where the site has no `REGISTERED` link → refused by `I-22` with a field-level error | v1 · P0 | `P0-02` |
| **`WH-SC-313`** | The second Delhi branch, an additional place of business under the Delhi GSTIN, resolves the profile and issues a challan | v1 · P2-IN | `P2-IN-01` |
| **`WH-SC-314`** | Pune requests 5 EA from Nashik. Nashik approves 3 → 3 reserved, 2 written to the insufficient-stock log as `TRANSFER_REQUEST` | v1 · P2 | `P2-02` |
| **`WH-SC-315`** | The nightly scheduled replenishment run finds items below reorder point → suggestions, a `whb_job_runs` row, and one notification to the buyer role with the count, value and link | v1 · P2 | `P2-15` |
| **`WH-SC-316`** | A transfer is cancelled while `IN_TRANSIT` → `TRANSFER_RETURN` posts from its transit location back to the source, with a reason | v1 · P2 | `P2-02` |
| **`WH-SC-317`** | The expiry job runs while a `HARD` reservation is being picked → the reservation survives. A `SOFT` one past `expires_at` is released | v1 · P2 | `P2-07` |
| **`WH-SC-318`** | A blind return with no original shipment → costed at the site's current method cost, `cost_basis = RETURN_UNMATCHED`, and listed on the report | v1 · P2 | `P2-12` |
| **`WH-SC-319`** | A transfer whose destination site belongs to another company → `422 CROSS_COMPANY_TRANSFER`. The destination picker never offered it | v1 · P1 | `P1-17` |
| **`WH-SC-320`** | The monthly ABC run over 12 months of demand history → classes set by the site's cut-offs, previous class kept, job run recorded | v1.1 · P3 | `P3-25` |
| **`WH-SC-321`** | A trade customer logs in → sees in-stock / on-order flags for its own lines only, creates a `DRAFT` order, and downloads its challan | v2 · P5 | `P5-25` |
| **`WH-SC-322`** | Company A moves parts to company B → one action creates A's demand order and B's purchase order, cross-referenced. No transfer exists | v2 · P5 | `P5-26` |
| **`WH-SC-323`** | A PO over the second value band → needs the parts manager, then the general manager. The same user cannot approve twice | v2 · P5 | `P5-27` |
| **`WH-SC-324`** | One item prefers supplier X at Delhi and supplier Y at Mumbai → each site's replenishment run proposes its own | v2 · P5 | `P5-24` |
| **`WH-SC-325`** | An install-created reason code with a Hindi translation → the `hi` user's screen and printed challan show the Hindi name | v2 · P5 | `P5-28` |
| **`WH-SC-326`** | An OEM ships a serialised part straight to a fleet customer → one movement `SUPPLIER → CUSTOMER` with the serial captured. The later return has an origin | v2 · P5 | `P5-09` |
| **`WH-SC-327`** | A line with `duty_status = 'Bonded'` (not a registry code) → refused by the FK. No new balance grain appears | v1 · P0 | `P0-02` |

**Screens** — `BUILD-SPEC-SCREENS.md` §1. **`WS-238` and `WS-239` are reserved** for round 3's
`RA-001` (*Warehouse Grants*) and `RA-002` (*Item Prices*), as `GAP-REGISTER-R3.md` §4.4 recommends; this
fold does not write their rows. Round 4 takes **`WS-240`** *Trade Portal* (`P5-25`, v2, the Customer
reference) and **`WS-241`** *Approval Levels* (`P5-27`, v2, the Department reference). **The next free id is
`WS-242`.** No other round-4 change takes a screen id: the junctions are sub-grids on `WS-015`, `WS-016`,
`WS-017`, `WS-021`, `WS-023` and `WS-173`.

**Irreversible rows** — `IRREVERSIBLE.md` §2. The next free id afterwards is **`IRR-68`**.

| Id | Row | Class · gate |
|---|---|---|
| **`IRR-64`** | The site's registration history: `whb_warehouse_branches` `REGISTERED` rows, dated, append-only once a movement stands in their range; `whin_gstin_profile_branches` likewise | `UB` · `V500012` / `V540010`, unrecoverable from the first registration change |
| **`IRR-65`** | Master-association history on the v1 junctions: counterparty tax registrations and addresses frozen on documents, location custody, item category per scheme, lot parties, serial identifiers | `UB` · `PNR-3` |
| **`IRR-66`** | The outbox event schema: `PC-36`'s dimensions and `event_version` on every event, from the first one emitted | one-way from the first event · `V500040` |
| **`IRR-67`** | Non-ledger high-volume tables partitioned at `CREATE`: position snapshots, outbox, deliveries, inbound messages, batch results, audit events | `RK` · `V500040`–`V500045`; the snapshot's start date is `PNR-3` |

**Enforceable constraints** — `DATA-MODEL.md` §6.3, after the `I-21` that `OD-14` owes:

| Id | Constraint | Where |
|---|---|---|
| **`I-22`** | `BEFORE INSERT` on `whb_stock_movements`: a `REGISTERED` link must cover `NEW.occurred_at` at `NEW.warehouse_id` | `V500030` (`P0-02`) |
| **`I-23`** | The `REGISTERED` history: the exclusion (no overlap, from `V500012`), the deferred at-least-one trigger, and the append-only trigger (no `DELETE` and no key edit once a posted movement is in range; `effective_to` never inside a `CLOSED` period). It reads the ledger, so it cannot live in `V500012` | **`V500037`** (`P0-02`) |
| **`I-24`** | A rule row referenced by a reservation or task is immutable. An edit is copy-on-write | `V500031`, `V500033`, `V510017` |

**Registries** — `DATA-MODEL.md` §2.1.1: **15** `whb_duty_statuses` (`V500005`), **16**
`whb_warehouse_branch_roles` (`V500012`), **17** `whb_event_types` (`V500040`). `I-18` enumerates seventeen
registries plus every `CODE-LIST` column of the new classification table.

**Flyway versions** — twenty-nine new claims and one release:

| Version | Task | Content | Band note |
|---|---|---|---|
| `V500037` | `P0-02` | `I-23` | from the `V500037`–`V500039` gap |
| `V500061` | — | **released** (hole) | `whb_item_location_settings` moves to `V500016` (`RG-008`); `P3-12`'s header loses it |
| `V500068` | `P3-06` | `whb_location_zone_memberships` | post-v1 base DDL gap `V500068`–`V500099` (`V500067` is `P4-09`'s; `DATA-MODEL.md` §7.2's gap row is stale and is corrected) |
| `V500069` | `P3-25` | ABC cut-off columns on `whb_warehouses`; `previous_abc_class`, `abc_computed_at` on `whb_item_site_settings` | same gap |
| `V500070` | `P5-24` | the eight v2 base junctions and side tables | same gap |
| `V500071` | `P5-28` | `whb_registry_translations` | same gap |
| `V510220` | `P5-24` | `wh_print_template_scopes`, `wh_inspection_plan_assignments` | carved from the `V510217`+ correction reserve — `IMPLEMENTATION-PLAN.md` §2.9 row 7 |
| `V510221` | `P5-25` | `wh_trade_portal_users` (dated) | same carve |
| `V510222` | `P5-27` | `wh_approval_levels` | same carve |
| `V511180` | `P5-27` | the `WS-241` grid configuration | from `V511180`–`V511199`, left free by `P3-04`; `issues/05-EPIC-p3.md:86` and `p3-04.md:52` are corrected |
| `V511201` + `V511231` | `P2-01` | verb permissions + dependency rows | `WH-206`, one pair per transition-shipping task |
| `V511202` + `V511232` | `P2-02` | transfer verbs (`request` `approve` `reject` `report_variance` `cancel`) | `WH-206` |
| `V511203` + `V511233` | `P2-04` | count verbs | `WH-206` |
| `V511204` + `V511234` | `P2-10` | shipment verbs | `WH-206` |
| `V511205` + `V511235` | `P2-12` | RMA and return-receipt verbs | `WH-206` |
| `V511206` + `V511236` | `P2-13` | supplier-return verbs | `WH-206` |
| `V511207` + `V511237` | `P2-15` | replenishment-suggestion verbs | `WH-206` |
| `V511208` + `V511238` | `P3-11` | work-order verbs | `WH-206` |
| `V511209` + `V511239` | `P5-25` | portal resource permissions, dependencies, menu | `WH-206` |
| `V511210` + `V511240` | `P5-27` | approval-level resource permissions, dependencies, menu | `WH-206` |

Every other round-4 table rides a migration its owning task already claims (`V500001`, `V500005`,
`V500010`–`V500018`, `V500030`, `V500040`, `V500062`, `V500066`, `V510040`, `V510044`, `V510202`,
`V510204`, `V510208`, `V530010`, `V530021`, `V530050`, `V540010`).

**Tasks** — the next free ids by the file glob (`GAP-REGISTER-R3.md` §4.3): `P3-25`, then `P5-24`…`P5-28`.
**Six new task files, 143 → 149.** Each must be **filed as an issue by `create-issues.sh`** after it
lands. No author writes an `issue:` line (`GAP-REGISTER-R3.md` §4.3).

**Decisions** — `D-14`; `OD-18` (drop-ship), `OD-19` (stock at a registration change). Next free `OD-20`.

### 4.1 Rules for the four agents, and the edits that must land together

1. **Stay inside your partition.** No agent opens another partition's file. `DECISIONS.md`, the four GAP
   registers, `tools/` and `docs/reviews/` are in no partition and are not edited.
2. **Allocate nothing.** An id not in §4.0 is a defect. If a fold needs one, stop and report it.
3. **Transcribe, then check.** Each agent runs `python3 tools/check-design-set.py` on its own tree before
   handing back. Cross-partition checks (8, 9, 10) pass only when all four land, so **merge all four in one
   commit**.
4. **The coupled pairs.** Each of these is written by two partitions and must say the same thing:

| Pair | Partition A writes | Partition B writes |
|---|---|---|
| `FR-460`…`FR-469` exist and are owned | P-CORE: the ten FRD rows in §6.28 | P-EARLY `p1-05` (`FR-460`); P-MID `p2-02` (`FR-462`), `p2-25` (`FR-461`); P-LATE `p5-09` (`FR-467`), the six new files, and **`IMPLEMENTATION-PLAN.md` §2's `Closes` cells** for all ten |
| `FR-382` moves `P3-04` → `P0-16` | P-EARLY: `p0-16`'s `## Requirements closed` gains `FR-382` | P-LATE: `p3-04` loses it; plan §2 rows for `P0-16` and `P3-04`; `FR-382`'s FRD row (P-CORE) reads **v1 · P0** |
| New migration claims | P-EARLY `p0-02` (`V500037`); P-MID `p2-01` `p2-02` `p2-04` `p2-10` `p2-12` `p2-13` `p2-15` (their `WH-206` pairs) | P-LATE: the plan §2 `Migrations` cells, the epics' re-derived blocks (`DECISIONS.md` §7 rule 7), `p3-06` (+`V500068`, and `warehouse-base` on its header), `p3-11`, `p3-12` (−`V500061`); P-CORE: `DATA-MODEL.md` §7.2/§7.3 rows |
| New scenarios exist and are closed | P-CORE: the twenty-two catalogue rows | the closing tasks in §4.0's table, in each partition |
| `WS-240`/`WS-241` | P-CORE: `BUILD-SPEC-SCREENS.md` §1 rows and blocks | P-LATE: `p5-25`, `p5-27` headers |
| New tables named in task files | P-CORE: `DATA-MODEL.md` §2 rows for all 41 | every task file naming one (check 3) |

### 4.2 P-CORE — `docs/*.md` except `DECISIONS.md`, the four GAP registers and `IMPLEMENTATION-PLAN.md` (P-LATE) · **13 files**

**`docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md`**
- **New §6.28 *Round-4 amendments***: `FR-460`…`FR-469` from §4.0, in §2's row format. The count becomes
  469 in the header, §7 and §8.
- `FR-079` is rewritten to `D-14` item 2 plus `RH-003`'s *link, never mirror*. `FR-080` loses
  `tax_registration_id` and `legal_entity_id`. `FR-081` says a non-physical site still carries a
  `REGISTERED` row (`RG-001`).
- `FR-073`, `FR-162`, `FR-233`, `FR-254`, `FR-307`, `FR-314`, `FR-342`, `FR-386` and `FR-426` each gain
  *"the `REGISTERED` branch at `occurred_at`"* or *"at the document date"*, per R22 §1.2.4 rows 1–12.
  `FR-073`/`FR-254`: a sister is a site with a **different** `REGISTERED` branch.
- `FR-305` keeps *frozen at creation* and adds the two link-row snapshots and the same-company rule
  (`RK-007`). `FR-359`/`FR-360` cite `FR-461`.
- `FR-404` names `BranchScopeService` and the `:view:all`/`:view:branch` pair (`RH-002`). `FR-405`: access
  is any current link whose role grants visibility; an unlinked site is invisible; the resolver returns
  `allowedWarehouseIds` (`RH-001`).
- `FR-020` gains the dated `whb_company_branches` (`RH-004`). `FR-119`'s exclusion list loses addresses and
  tax registrations (`RG-003`). `FR-088` adds custody through `whb_location_user_assignments` (`RG-004`).
- `FR-443` carries the variant values (`RG-009`) and the item's category assignments under the `STOCKING`
  scheme (`RG-005`). `FR-094`/`FR-097`/`FR-320` add lot parties and serial identifiers (`RG-006`,
  `RG-007`).
- `FR-104`: `duty_status` is an FK to registry 15, and base seeds `DOMESTIC` only (`RL-001`).
- `FR-059`: the key sentence becomes the key's comment (`RL-005`). `FR-062`: scan resolution is scoped by
  site, with `AMBIGUOUS_LOCATION` and `AMBIGUOUS_IDENTIFIER`. `FR-089`: codes unique within the site
  (`RL-004`).
- `FR-070` loses the ABC recompute to `FR-463` and keeps velocity/XYZ at v3. `FR-156`: the `ABC`
  programme type is labelled manual until v1.1 (`RK-003`).
- `FR-165` enumerates quantity thresholds and `RJ-012`'s five columns, and requires the injected `Clock`
  (`RL-016`). `FR-253` adds the `SCHEDULED` run and the buyer notification (`RK-004`). `FR-398`: SMS hidden
  until platform ships it (`RH-007`).
- `FR-147`/`FR-148`: the transit location is a per-transfer `IN_TRANSIT` child of the source site
  (`RJ-002`). `FR-177`/`FR-189`: transfers and vendor returns run through the demand model (`RJ-003`).
- `FR-170`: `expires_at` applies to `SOFT` only (`RJ-007`). `FR-096`: a lot hold is a `wh_holds` row
  (`RJ-008`). `FR-161` point 3 resolves counterparty → channel → item (`RJ-009`).
- `FR-234`/`FR-275`: the unmatched-return and return-to-vendor cost rule (`RJ-010`). `FR-270`: the ten
  values seed `RETURN_TYPE` (`RJ-014`). `FR-133`: one inspection series per GRN (`RJ-014`). `FR-132`: the
  v1 guard reads receiving-session arrival (`RJ-018`).
- `FR-022` extends partitioning to the six tables of `RL-011`. `FR-331`: the outbox is `PC-36`'s column set
  with `event_version`, no payload, and `whb_event_types` (`RL-002`).
- `FR-380` gains the three-way vocabulary classification (`RL-006`). `FR-382` is **v1 · P0**, owner
  `P0-16`, reworded to a rule (`RL-009`). `FR-076`/`FR-078`: the attribute subjects and
  `whb_entity_attribute_values`; install-created keys are the custom-field answer (`RL-007`).
- `FR-173`: referenced rule rows are immutable (`RL-010`). `FR-414` adds the v1.1 configuration package
  (`RL-012`). `FR-334` adds the v1.1 status-changed event and guard SPI (`RL-014`). `FR-430` adds the v1.1
  minimum app version (`RL-017`).
- `FR-416`/`FR-417`: the server-side import path (`RH-009`). `FR-181`: calendars layer over platform
  holidays. `FR-439`: timezone validated against platform `timezones` (`RH-011`).
- **§9** gains `OD-18` and `OD-19`. **§10** gains R25 §4.2's four declines (vendor portal, marketplace
  catalogue, workflow designer, SOR auto-invoice), each with its re-entry path.

**`docs/DATA-MODEL.md`**
- §1.3 and `:132`: `ON UPDATE RESTRICT` for every code-keyed FK (`RL-013`); R22 §1.3's junction convention
  as a stated rule; `RL-004`'s key decisions.
- **§2.1.1** gains registries 15, 16 and 17 and the **Vocabulary classification** table (`RL-006`);
  `whb_code_lists`/`whb_code_list_values` and `whb_entity_attribute_values` (`V500010`);
  `whb_attribute_keys.applies_to` → `ATTRIBUTE_SUBJECT`; `I-18` → seventeen.
- `whb_reason_codes`: `uk(context, code)`; `itc_treatment` → `tax_treatment_code`. `whb_companies` gains
  `whb_company_branches`. `whb_owners`: `uk(company_id, code)` only. `whb_owner_grants`: dated +
  `EXCLUDE`.
- `whb_counterparties`: `min_shelf_life_ship_pct`, plus `whb_counterparty_addresses` and
  `whb_counterparty_tax_registrations`. `whb_counterparty_role_links`: renamed to
  `effective_from`/`effective_to` + `EXCLUDE`.
- **`whb_warehouses`** (`:452`): drops `branch_id`, `tax_registration_id`, `legal_entity_id` and
  `idx(branch_id)`; `uk(company_id, code)` only; timezone validated against platform `timezones`.
  Adds `whb_warehouse_branches` and `whb_warehouse_branch_roles` with R22 §1.2.2's DDL and guards (the
  transit-pool paragraph of R22 §1.2.3 omitted, §3.4).
- `whb_locations`: `uk(warehouse_id, code)` only; `assigned_user_id` and `fixed_item_id` dropped;
  `whb_location_user_assignments` added; `IN_TRANSIT` per-transfer children of the source; the
  `status` ladder with its setters.
- `whb_items`: `category_id` and the three variant slots dropped; `whb_item_category_assignments`,
  `whb_style_variant_axes` and `whb_item_variant_values` added; `code` a system surrogate.
  `whb_item_identifiers`: `owner_id` + `RL-005`'s key. `whb_item_location_settings` moves to `V500016`
  with `is_fixed` and dates.
- `whb_lots`: `counterparty_id` and `hold_reason_code_id` dropped; `whb_lot_counterparties` added.
  `whb_serials`: `secondary_serial` dropped; `whb_serial_identifiers` added. `whb_lpns.owner_id` is
  defined as the custodian/label owner.
- `whb_number_series`: the `branch_id` resolution rule. `whb_number_series_issued`:
  `uk(series_id, formatted_number)`.
- `whb_valuation_policies` and `whb_category_stocking_ownership`: `EXCLUDE`. `whb_item_supplier_sources`:
  dated (v1).
- `whb_cost_layers`: `duty_status` FK; `cost_basis` gains `RETURN_UNMATCHED`.
- `whb_stock_movements`: `I-22`; the company assertion.
- `whb_stock_movement_lines`: `duty_status VARCHAR(40)` FK; `tax_classification_code` +
  `tax_classification_scheme` replace `hsn_code`; no `CHECK (… IN …)` on either ledger table.
- `whb_movement_line_attributes`: four typed columns.
- `whb_reservations`: the `SOFT`-only expiry and the re-attach rule. The allocation tables,
  `whb_negative_stock_policies` and `wh_putaway_rules`: `version_no`, `supersedes_id`, `I-24`.
- `whb_outbox`: `PC-36`'s columns, no `payload`, partitioned by `recorded_at` with PK
  `(cursor, recorded_at)`. `whb_outbox_subscriptions.accepted_event_version`. `whb_outbox_deliveries`,
  `whb_inbound_messages`, `whb_movement_batch_results`, `whb_audit_events` (PK
  `(sequence_no, occurred_at)`) and `whb_stock_position_snapshots` (non-zero positions only):
  partitioned.
- `whb_accounting_handovers`: `envelope_version`, and `VOIDED` in its ladder.
- `whb_devices` gains `whb_device_assignments` (v1.1, `V500062`). `whb_api_clients`: the FK goes to
  `whb_companies`, plus `whb_api_client_endpoints` and `whb_api_client_companies` (v2, `V500066`).
- `wh_goods_receipts.po_id`, `wh_landed_cost_documents.grn_id`, and the `wh_return_receipts` and
  `wh_supplier_returns` origin columns: nullable, derived.
- `wh_transfer_orders`: the ladder incl. `REQUESTED`; line `approved_quantity`;
  `source_warehouse_branch_id`/`destination_warehouse_branch_id`; `demand_order_id` (by `ALTER` in
  `V510040`); the same-company guard. `wh_supplier_returns.demand_order_id` (same `ALTER`).
- `wh_demand_orders.demand_type` and `whb_allocation_rules.demand_type_code` → `DEMAND_TYPE`.
- `wh_replenishment_runs.run_type` gains `SCHEDULED`; `suggested_source` = `TRANSFER`.
  `wh_return_receipts.return_type` → `RETURN_TYPE`. `wh_goods_receipt_lines` gains `ITEM_MISMATCH`.
- `wh_carriers`: `uk(counterparty_id)`. `whb_channels`: `min_shelf_life_ship_pct`; `channel_kind` →
  `CHANNEL_KIND`. `wh_print_templates.template_kind`/`format` → code lists.
- `whin_gstin_profiles`: `branch_id` dropped, plus `whin_gstin_profile_branches` and the equality rule.
  `whin_compliance_registrations`: `document_kinds` → `whin_compliance_registration_document_kinds`.
  `whin_delivery_challans`/`whin_eway_bills`: the frozen counterparty registration and address.
  `whad_counter_sales`: the pair rule of `FR-461`.
- The v1.1/v2 tables of §4.0 get their §2 rows: `whb_location_zone_memberships`, `P3-25`'s columns,
  `P5-24`'s ten tables, `whb_registry_translations`, `wh_trade_portal_users`, `wh_approval_levels`,
  `wh_carrier_account_scopes`, and the five `RG-017` tables.
- §3.2 crossing FKs: `B1` → `whb_warehouse_branches.branch_id`; `B2` →
  `whb_location_user_assignments.user_id`; `W8` gains the two snapshots; `N2` →
  `whin_gstin_profile_branches`; a new row for `whb_company_branches.branch_id`. §4.1/§4.10 ER edges
  through the junction.
- §6.3: `I-22`, `I-23`, `I-24`. `:755`: *"every warehouse-set guard"*.
- §7.2/§7.3/§7.6: every §4.0 version. `V500061` → hole. The stale `V500067`–`V500099` gap row →
  `V500072`–`V500099`. `WH-206` lists its claimed pairs.
- §8.1/§8.4 regenerated **together** (+41 tables). §9.2: `wms_warehouse_branches` → **re-homed** as
  `whb_warehouse_branches`.

**`docs/IRREVERSIBLE.md`**
- Rows `IRR-64`…`IRR-67` from §4.0.
- `IRR-57` keeps `state_code` and replaces the two scalars with the dated `REGISTERED` link; §3.4 `:339`
  and §4.5 `:554-555` are reversed.
- `IRR-12`: the value list moves to the India pack; registry FK; base seeds `DOMESTIC`.
- `IRR-30` → the custody junction. `IRR-42` → `tax_classification_code` + scheme. `IRR-06` → the LPN
  owner definition.
- `:665`: `TRANSFER_RETURN` joins the v1 movement-type seed. `:668`: `BONDED` leaves the stock-status seed.
  §4.2 `:500-501`: four typed columns. `:539-540`: `RL-005`'s key.
- Counts: 63 → 67.

**`docs/BUILD-SPEC-SCREENS.md`**
- **§1**: `WS-240` *Trade Portal* and `WS-241` *Approval Levels* rows and blocks. The marker →
  **`WS-242`**, noting that `WS-238`/`WS-239` are reserved for round 3.
- `WS-016`: `registeredBranchName`; a *Linked branches* count column; the *Branches* modal tab (branch,
  role, from, to, primary; *End link*, *Change registration*); filter `relationshipRoleCode` in the
  `WAREHOUSE_WAREHOUSE` scope; export + `registeredBranchName` + `linkedBranchNames`; branch options
  from the warehouse endpoint (`RH-004`); mobile picker per R22 §1.2.4 row 15; timezone select.
- `WS-015` gains the *Company branches* sub-grid. `WS-017`: codes unique per site, plus a *Custody*
  sub-grid. `WS-018`: uniqueness preview within the site. `WS-021`: *Addresses* and *Tax registrations*
  tabs, and a shelf-life field. `WS-023`: category-per-scheme and variant values. `WS-013`: the
  `applies_to` options. `WS-036`/`WS-037`: lot parties and serial identifiers. `WS-048`: version history.
  `WS-061`: series branch = the `REGISTERED` branch.
- `WS-090`: *Request* · *Approve* · *Reject*, with `REQUESTED` creatable by a destination-scoped user;
  destination picker filtered to the source's company; *Pick* removed (the demand path); *Dispatch* is
  `wh_shipments:dispatch`; *Cancel* in transit posts `TRANSFER_RETURN`.
- `WS-084` runs via a demand order. `WS-093` gets the manual-ABC label. `WS-135` gets *Reverse*.
  `WS-141` drops `FR-254`.
- `WS-173` gets *Places of business*. `WS-178`/`WS-179` get the recipient registration. `WS-183` reads per
  `REGISTERED` at `occurred_at`. `WS-194`: the picker lists sites linked `REGISTERED`/`SERVING` to the
  selling branch, and states the `422`.
- `WS-208`/`WS-210`/`WS-211`/`WS-212` and §7's report header: the `RH-006` rollup rule.
- **§0.11** gets R24 Appendix A as amended by §3.3, plus `VOIDED` and the location ladder. **§10.2** gets
  `RJ-005`'s rows, the transfer and handover verbs, `change_registration`, the tier pairs, and the two new
  resources.
- **§0's error register** gains `CROSS_GSTIN_COUNTER_SALE`, `CROSS_COMPANY_TRANSFER`,
  `WAREHOUSE_BRANCH_COMPANY_MISMATCH`, `AMBIGUOUS_LOCATION`, `AMBIGUOUS_IDENTIFIER`, `STAGED_STOCK` (409),
  `UNREGISTERED_INSTANT` (`I-22`) and `CLIENT_UPGRADE_REQUIRED` (426, v1.1).
- Each registry block gains a v2 *Translations* tab note (`P5-28`).

**`docs/SCENARIO-CATALOGUE.md`**
- **New §3.22**: `WH-SC-306`…`WH-SC-327`. The §5 rule 3 marker → **`WH-SC-328`**; §1.2's coverage rows
  recomputed.
- The cast (`:104-111`): add **`DEL-02`** under the Delhi GSTIN; give one site a `SERVING` link to a branch
  in another state; delete `TRANSIT-WH`.
- Rewrites: `WH-SC-045` (a second current `REGISTERED` is refused, `SERVING` is offered);
  `WH-SC-058`/`120`/`122`/`125` (transit at the source site, receive authorised by the transfer verb,
  raised through the demand path); `WH-SC-102`/`124`/`156`/`206`/`242`/`243` per R22 §1.2.7;
  `WH-SC-135` split; `WH-SC-057` return type; `WH-SC-134` resolution order; `WH-SC-139` hold via
  `wh_holds`; `WH-SC-083` guard; `WH-SC-301` re-inspection number.

**`docs/PLATFORM-DEPENDENCIES.md`**
- §1.1 `:45` → *"a site is linked to branches (M:N, one `REGISTERED`), never a branch row"*; §2.1
  `:111-121` loses `whb_sites`.
- §2.2 `:143`: the supply test reads the two `REGISTERED` branches. §2.3 `:148-181`: items 1–3 re-pointed
  to `allowedWarehouseIds`, and *empty in, empty out* stated twice.
- §1.7 → SHAPE-MISMATCH and the server path. §1.9 adds the enum, the email template and the SMS stub.
  §1.10 → opt-in per role. §1.15(a) records `origin/warehouse`.
- §4.11 and `PD-D11` → *"reuse `BranchScopeService` (shipped); aspect-level enforcement optional, never
  blocking"*.
- The seven R23 §2.1 dependencies become PD rows. §7 `:885`: the `GenericScreen` gate is **verified**.

**`docs/PORT-AND-ADAPTER-CONTRACT.md`**
- §2.5: `duty_status` FK; `tax_classification_code` + scheme on the wire; line attributes typed.
- §4.2: `PC-36`–`PC-38` now match `DATA-MODEL.md`; `PC-37` states *no payload in v1*; `PC-43` →
  `whb_event_types`; `PC-75` + `accepted_event_version`; the subscription column names reconciled to
  `DATA-MODEL.md`.
- §7.3 `PC-66`: the owned-codes-only rule and the guarded idiom; the worked example `:1201-1210` corrected;
  `PC-72` assertion 7. `PC-67` gets the mobile sentence.
- Transfer sections `:1594-1595`, `:1743`: `TRANSIT-WH` → the per-transfer `IN_TRANSIT` location at the
  source.
- §10.2 covers mobile-called management endpoints (v1.1). `PC-04` names `WarehouseBranchLinkValidator`
  and `WhTransitionGuard`. `PC-69`'s fallback reads `whb_registry_translations` first (v2).

**`docs/MODULE-INTEGRATION.md`**
- §2 gains five rows after the current last: `lazyScreens.ts`, `RootNavigator.tsx`, `GenericScreen.tsx`'s
  route chain, `is_mobile_enabled` menus, and *every L1 needs an L2 child*, each **B/R**.
- §12's platform-file ledger adds `NotificationCategory.java`, `EmailTemplateDefaults.java`,
  `DashboardWidgetScopeResolver.java`, `registry.ts`, and the three mobile navigation files.
- The touchpoint count follows.

**`docs/COEXISTENCE.md`** — `C5` `:199`: *"one branch, one GSTIN"* → *"one `REGISTERED` branch at a
time"*.

**`docs/INDIA-LOCALISATION-PACK.md`**
- §3.4 rules 1–2 `:353-362`: *"exactly one `REGISTERED` link at every instant"*; `state_code` is the site's
  own address fact.
- `S3` `:1144`, `:420`, `:1228`: the challan branch is the `REGISTERED` branch at the challan date.
- Places of business and the nightly GSTIN equality (`RG-002`); per-state counterparty registrations
  (`RG-003`).
- The duty-status regime values moved from `IRR-12`, seeded in `P4-07`'s `V540140`. The tax-treatment
  values seeded by `warehouse-india`.
- The RE-VERIFY register gains two rows: the Packaged Commodities party list (`RG-006`), and the statutory
  treatment at a re-registration (→ `OD-19`).

**`docs/COMPETITOR-BENCHMARK.md`** — the eight `RK-009` rows under §2.5/§2.7/§2.8/§2.9/§2.11/§2.14/§2.17
with R25's marks and versions; §7 gains R25 §4.2's four declines.

**`docs/README.md`**
- Counts: 469 requirements; the new table total from §8.4; 327 scenarios; 67 irreversible rows; 149 tasks;
  `D-1`…`D-14`; `OD-1`…`OD-19`.
- The reviews row reads **26 lenses** and names `GAP-REGISTER-R3.md` and `-R4.md` in row 5.

**`docs/DESIGN-SET-DEFECTS.md`**
- §5's check-13 ask gains its fourth clause: *every finding in `reviews/R22`–`R26` has a disposition row
  in `GAP-REGISTER-R4.md` §2.1–§2.5* (§7).
- The round-3 defect *"two-letter registers are invisible to check 7"*, if listed, is marked
  **discharged 2026-09-10**.

### 4.3 P-EARLY — `issues/p0-*.md`, `issues/p1-*.md` · **35 files**

| File | Amendment |
|---|---|
| `p0-01` | `RH-006`: `V500200` seeds `widget:warehouse:view`/`:view:all`/`:view:branch` + the source-page row. `RH-008`: runbook touchpoints for mobile, and the L1 menu with an `is_mobile_enabled` L2 child. `RL-016`: the module skeleton's `Clock` scanner test |
| `p0-02` | **Header `Migrations` + `V500037`**. `I-22` in `V500030` and `I-23` in `V500037` (`RG-001`); `duty_status VARCHAR(40)` FK (`RL-001`); `tax_classification_code` + scheme (`RL-008`); four typed attribute columns (`RL-007`); no `CHECK (… IN …)` on either ledger table (`RL-006`); `ON UPDATE RESTRICT` (`RL-013`); the company-equals-site assertion (`RG-012`); `whb_negative_stock_policies` versioned under `I-24` (`RL-010`). Traps: `RG-024`, `RG-025`, `RG-027`. Scenarios + `WH-SC-312`, `WH-SC-327`. Closes + `RG-027` `RL-001` |
| `p0-03` | `RL-011`: `whb_stock_position_snapshots` partitioned by `snapshot_date`, non-zero only (`V500045`). `RL-016`: the writer takes the injected `Clock` |
| `p0-04` | `RL-003`: owned codes only, the guarded seed idiom, `PC-72` assertion 7, `uk(context, code)` (`V500004`). `RL-008`: `tax_treatment_code`. `RJ-006`: `TRANSFER_RETURN` seeded in `V500003`. `RL-012`: `owning_module = 'INSTALL'`. `RL-013`: immutable codes. `RL-009`: registry-backed mobile fields are never `z.enum`. Drop-ship is not seeded (`OD-18`) |
| `p0-05` | `RL-001`: `whb_duty_statuses` in `V500005`, `DOMESTIC` only, and `BONDED` out of the status seed. `RL-006`: `whb_code_lists` + values in `V500010` with the eleven v1 lists, and the classification rule. `RL-007`: `ATTRIBUTE_SUBJECT` + `whb_entity_attribute_values` in `V500010`. `I-18` → seventeen. `RL-013`. Closes + `RL-006` `RL-007` |
| `p0-06` | `RG-021`: owner grants dated + `EXCLUDE`. `RL-004`: `whb_owners` `uk(company_id, code)` only. `RG-013`: superseded at v2 by `P5-24` |
| `p0-07` | `RH-004`: `whb_company_branches` (dated) in `V500001` and the `WS-015` sub-grid. `RG-026` trap. Closes + `RH-004` |
| `p0-08` | `RL-011`: `whb_inbound_messages` and `whb_movement_batch_results` partitioned in `V500041` |
| `p0-09` | `RJ-007`: `SOFT`-only expiry. `RJ-015`: the re-attach rule. `RL-010`: the three allocation tables versioned + `I-24` in `V500033` |
| `p0-11` | `RL-002`: `PC-36`'s column set, no payload, `whb_event_types` (registry 17) seeded with `PC-42`'s codes + `document.status_changed`, `accepted_event_version`. `RL-011`: outbox and deliveries partitioned. `RG-018`: subscription owners at v2 in `P5-24`. Closes + `RL-002` |
| `p0-12` | `RJ-011`: `VOIDED` and `:void`. `RL-002`: `envelope_version`. `RG-005`: posting rules read the `STOCKING` category at `occurred_at`. `RG-001` row 10: the envelope branch |
| `p0-13` | `RJ-012`: five register rows. `RK-004`: the quantity-threshold row pointing at `P2-15`. `RL-016`: the `Clock` rule + scanner. `RL-011`: `whb_audit_events` partitioned (`V500043`) |
| `p0-15` | `RH-002`: tier pairs on every base resource, the grants and the architecture rule. Verbs `warehouse:warehouses:change_registration` (maker–checker) and `whb_accounting_handovers:void` in `V501000`. Closes + `RH-002` |
| `p0-16` | **`## Requirements closed` + `FR-382`** (§4.1). `RL-009`: the mobile rule text. `RL-017`: pointer to `P3-04`'s v1.1 rule |
| `p0-17` | `RL-001`: the cost-layer `duty_status` FK (`V500021`). `RG-021`: valuation policies `EXCLUDE`. `RG-005`: policy resolution by `STOCKING` at `occurred_at`. `RJ-010`: the `RETURN_UNMATCHED` value |
| `p1-01` | `RG-005`: `whb_item_category_assignments`. `RG-009`: `whb_style_variant_axes` + `whb_item_variant_values`; slots dropped (`V500015`). `RL-004`: `code` a surrogate. Traps `RG-023`, `RG-024`. `RG-010`/`RG-020`: superseded at v2 by `P5-24`. Closes + `RG-005` `RG-009` `RG-023` `RG-024` |
| `p1-02` | `RG-008`: `whb_item_location_settings` moves into `V500016` (`is_fixed`, dated); the `fixed_item_id` `ALTER` dropped. `RL-005`: the key, `owner_id`, the resolver order and `AMBIGUOUS_IDENTIFIER`. `RG-007`: the resolver reads serial identifiers. `RL-013`. Closes + `RG-008` `RL-005` |
| `p1-03` | `RG-021`/`RG-011`: supplier sources dated + `EXCLUDE` (site scope at v2 in `P5-24`). `RJ-009`: the resolution order |
| `p1-04` | `RG-021`: stocking ownership `EXCLUDE`. `RG-005`: `D-9` reads the `STOCKING` category. `RH-012`: the three viewer components named |
| `p1-05` | **`## Requirements closed` + `FR-460`**. `RG-001` in full per §3 (roles registry 16 + junction in `V500012`; the three scalars dropped; guards 1, 3, 4 here with `I-23` in `P0-02`; validator bean collection; `WS-016` *Branches* tab + *Change registration*; the OD-19 default refusal). `RH-003`: trap replaced (*link, never mirror*; the one exception; not accessories' `is_primary` or its unlinked-is-shared guard). `RH-004`: the mismatch `422` + branch-options endpoint. `RH-011`: timezone validation. `RG-004`: custody junction (`V500013`). `RJ-002`: the `IN_TRANSIT` type; no `TRANSIT-WH`. `RJ-006`: the location ladder. `RL-004`: location and warehouse keys. Trap `RG-025`. Scenarios + `WH-SC-306`. Closes + `RG-001` `RG-004` `RG-025` `RH-003` `RH-011` `RJ-002` |
| `p1-06` | `RL-004`: the generator checks uniqueness within the site; the mask needs no site token |
| `p1-07` | `RG-006` + `RG-007` tables (`V500018`); `RG-022` definition; `RG-023` trap. `RJ-008`: no hold on the lot row; `hold_reason_code_id` dropped. `RJ-013`: `WH-SC-135`'s kit half removed. Closes + `RG-006` `RG-007` `RG-022` `RJ-008` `RJ-013` |
| `p1-08` | `RG-003`: two tables in `V500011`, `FR-119` amended. `RG-021`: role links dated + `EXCLUDE`; the first `btree_gist` declaration with the fail-loudly check. `RJ-009`: `min_shelf_life_ship_pct`. Closes + `RG-003` `RG-021` |
| `p1-09` | `RG-001` row 2: a branch-scoped series resolves to the `REGISTERED` branch at the document date. `RL-004`: `uk(series_id, formatted_number)` |
| `p1-10` | `RH-009`: the server-side path through `documents` above `bulk_import_max_rows`. `RL-012`: the v1.1 configuration kinds come later on this framework. Closes + `RH-009` |
| `p1-11` | `RJ-009`: `whb_channels.min_shelf_life_ship_pct`. `RL-006`: `channel_kind` → `CHANNEL_KIND` |
| `p1-12` | `RJ-018`: the guard reads receiving-session arrival. `RJ-004`: the PO line ladder |
| `p1-13` | `RJ-004`: session and GRN ladders. `RJ-005`: complete/cancel verbs (seeded by `P1-20`). `RG-019`: `po_id` nullable, derived. `RJ-014`: `ITEM_MISMATCH`. `RL-007`: `LOT`-kind attribute capture on the GRN line. `RL-005`: scan surface |
| `p1-14` | `RJ-005`: the scrap-disposition approve verb (seeded by `P1-20`). `RJ-017`: putaway at release. `RJ-014`: re-inspection number. `RG-018`: plan assignments at v2 in `P5-24` |
| `p1-15` | `RJ-017`. `RL-010`: `wh_putaway_rules` versioned + `I-24` (`V510017`) |
| `p1-16` | `RJ-004`: the receipt-reversal ladder; approve/post verbs seeded by `P1-20` |
| `p1-17` | `RK-001`: `REQUESTED` + line `approved_quantity` (`V510031`). `RK-007`: the same-company guard, `422 CROSS_COMPANY_TRANSFER`, `WH-SC-319`. `RG-001` row 4: the two link snapshots. `RJ-003`: `demand_order_id` arrives by `P2-08`'s `ALTER`. `RJ-004`: the ladder per §3.3 |
| `p1-18` | `RG-001` §1.2.5 with `RH-001`'s rules (`allowedWarehouseIds`, fail-closed, empty-in-empty-out twice, two-ended records, branch-carrying tables keep `BRANCH_FILTER_SQL`, composition order, present-tense access). `RH-002`: wraps `resolveStrict`. `RJ-002`: the transfer-verb authorisation. Scenarios + `WH-SC-310` |
| `p1-19` | `RL-009`: mobile status badges and registry pickers fetch; never `z.enum` |
| `p1-20` | `RJ-005`: the P1 verbs in `V511000`/`V511001`. `RH-002`: app tier pairs. `V511200`: `warehouse.replenishment.default_schedule` (`RK-004`) and `warehouse.count.default_tolerance_pct`/`_value` (`RJ-016`) |

### 4.4 P-MID — `issues/p2-*.md`, `issues/p2in-*.md` · **27 files**

| File | Amendment |
|---|---|
| `p2-01` | **Header + `V511201` `V511231`**. `RJ-004` adjustment ladder; `RJ-005` submit/post/cancel. Closes + `RJ-005` |
| `p2-02` | **Header + `V511202` `V511232`; `## Requirements closed` + `FR-462`**. `RK-001` per §3.3; `RJ-002` transit at source and `TRANSIT-WH` deleted from this file; `RJ-003` through the demand model; `RJ-004` ladder; `RJ-006` `TRANSFER_RETURN`; `RJ-012` arrival job; `RG-001` rows 4/5/13 and `FR-461`'s transfer path. Scenarios + `WH-SC-308` `WH-SC-314` `WH-SC-316`. Closes + `RK-001` `RJ-003` `RJ-006` |
| `p2-03` | `RJ-008`: a mass lot hold writes `wh_holds` rows. `RL-009` |
| `p2-04` | **Header + `V511203` `V511233`**. `RJ-004`; `RJ-005`; `RJ-006` cancel restores the location status; `RJ-012` schedule job; `RJ-016` install default; `RK-003` manual-ABC label; `RG-005`; `RG-018` (`WAREHOUSE` scope at v2) |
| `p2-05` | `RJ-009` resolution; `RJ-012` retest job; `RG-001` row 11 (branch split by `REGISTERED`) |
| `p2-06` | `RJ-004` exception ladder; `RJ-012` `age_days` computed on read |
| `p2-07` | `RJ-007`; `RJ-008` (the allocator consults `wh_holds`); `RL-010` (`WS-048` history); `RL-006` (`demand_type_code` → `DEMAND_TYPE`); `RG-005` |
| `p2-08` | `RJ-003`: `V510040` `ALTER`s `demand_order_id` onto the two tables and seeds `TRANSFER`/`VENDOR_RETURN`; `RJ-004` demand-order ladder; `RG-001` row 7 bill-from |
| `p2-09` | `RJ-003` transfer dispatch into transit; `RJ-007`; `RJ-015` |
| `p2-10` | **Header + `V511204` `V511234`**. `RJ-004`; `RJ-005`; `RJ-006` Cancel only before `DISPATCHED`; `RG-016` `uk(counterparty_id)` in `V510044`. Closes + `RG-016` |
| `p2-12` | **Header + `V511205` `V511235`**. `RJ-004`; `RJ-005`; `RJ-006` reverse before disposition; `RJ-010`; `RJ-012` RMA expiry; `RJ-014` `RETURN_TYPE`; `RG-019`; `RG-001` row 8. Scenarios + `WH-SC-318` |
| `p2-13` | **Header + `V511206` `V511236`**. `RJ-003` through a demand order; `RJ-005`; `RJ-006` `STAGED_STOCK`; `RJ-010` RTV layer; `RG-019` |
| `p2-14` | `RL-006` template kinds and formats as code lists (cash ticket, India prints); `RG-018` scopes at v2; `RL-015` v2 note |
| `p2-15` | **Header + `V511207` `V511237`, and the deliverable: the scheduled run and the first notification** (`RH-007`'s two platform commits + menu row). `RK-004`; `RJ-004` suggestion ladder; `RJ-005` accept/reject; `RJ-014` `TRANSFER`; `RG-001` row 12. Scenarios + `WH-SC-315`. Closes + `RK-004` `RH-007` |
| `p2-16` | `RL-001` layer references; `RJ-010`; `RG-005` |
| `p2-17` | `RG-019` (`grn_id` derived); `RJ-004` landed-cost and revaluation ladders |
| `p2-18` | `RG-001` row 10; `RJ-011`; `RL-002` `envelope_version` |
| `p2-19` | `RH-009`: opening stock uses the server path |
| `p2-20` | `RG-001` row 11 and `RH-006`'s rollup header. Closes + `RH-006` |
| `p2-21` | `RH-006`; `RH-010` provider bean + the UNVERIFIED recipient-scope check. Closes + `RH-010` |
| `p2-22` | `RJ-011`: *Void* from the queue |
| `p2-24` | `RG-001` row 12: availability grouped by `REGISTERED` |
| `p2-25` | **`## Requirements closed` + `FR-461`**. `WS-194` picker and `422`; `RL-003` guarded seeds; `RL-006` cash-ticket kind; `RL-005` OEM part numbers per counterparty; `RJ-004` counter-sale ladder; `RJ-005` verbs in `V520100`+. Scenarios + `WH-SC-309`. Closes + `RK-002` |
| `p2-26` | `FR-461` applied to job issue; `RJ-004` material-request ladder; `RJ-005` reserve/return-unused/cancel in `V521100`+ |
| `p2in-01` | `RG-002` (`V540010`), the `RH-005` choice, `WS-173`; `RG-018` document-kinds child table; the three `WarehouseBranchLinkValidator`s; `tax_treatment_code` values (`RL-008`). Scenarios + `WH-SC-311` `WH-SC-313`. Closes + `RG-002` |
| `p2in-03` | the `REGISTERED` branch at the challan date and its series; `RG-003` frozen recipient registration and address |
| `p2in-04` | the GSTIN of the `REGISTERED` branch, dispatch-from = the site's address; `RG-003` frozen recipient registration |

### 4.5 P-LATE — `p3`–`p6`, the new task files, the epics, the plan and `issues/README.md` · **50 files**

**Existing task files (34).**

| File | Amendment |
|---|---|
| `p3-01` | `RH-008`: the shared GS1 scanner (`PP-9`); `RL-009`; `RL-017` endpoint marking |
| `p3-03` | `RG-018`: `whb_device_assignments` (dated) in `V500062` |
| `p3-04` | **`## Requirements closed` − `FR-382`** (§4.1). `RL-017`: `warehouse.mobile.min_app_version`, `426`; `RL-009`. **`V511180`–`V511199` is no longer free** — `V511180` is `P5-27`'s |
| `p3-05` | `RJ-018`: the ASN clause activates here |
| `p3-06` | **Header: module + `warehouse-base`, Migrations + `V500068`** — `whb_location_zone_memberships` (`RG-015`). Closes + `RG-015` |
| `p3-11` | **Header + `V511208` `V511238`**; `RJ-005` work-order verbs; `RJ-013` kit trace |
| `p3-12` | **Header − `V500061`**; reads `whb_item_location_settings` from `V500016` (`RG-008`) |
| `p3-16` | `RH-007`: the remaining categories and templates; `notify_sms` hidden |
| `p3-18` | **Header deliverable + the configuration-package import kinds** (`RL-012`). Closes + `RL-012` |
| `p3-20` | `RG-004`: the adapter row FKs to the base custody row; `RG-021` vocabulary |
| `p3-22` | **Deliverable + `document.status_changed` and `WhTransitionGuard`** (`RL-014`). Closes + `RL-014` |
| `p3-24` | `RL-006`: `GS1_DIGITAL_LINK` is a `BARCODE_FORMAT` code-list row |
| `p4-02` | `RG-001` row 9: ITC-04 per `REGISTERED` at `occurred_at` |
| `p4-03` | `RG-001` row 9: the Rule 56 split. Scenarios + `WH-SC-307` |
| `p4-05` | `RG-006`: lot parties on the MRP report |
| `p4-06` | `RG-001` row 2: the series |
| `p4-07` | `RL-001`: India's duty-status seeds in `V540140` |
| `p4-10` | `RG-021`: `wh3_client_gst_registrations` dated + `EXCLUDE` |
| `p5-01` | `RG-017`: `wh3_client_counterparties` (`V530010`). Closes + `RG-017` |
| `p5-02` | `RG-017`: `wh3_rate_card_clients` + `EXCLUDE` (`V530021`) |
| `p5-03` | `RL-002`: the first consumer reads `event_version` and the dimensions |
| `p5-05` | `RJ-011`: a run may cancel once its AR handover is `VOIDED` |
| `p5-07` | `RG-017`: `wh3_sla_definition_clients` (`V530050`) |
| `p5-08` | `RK-006`: the trade persona ships separately in `P5-25` on this surface |
| `p5-09` | **`## Requirements closed` + `FR-467`** (gated on `OD-18`); `RG-017` `wh_channel_account_warehouses` (`V510208`). Scenarios + `WH-SC-326`. Closes + `RK-005`. **`## Blocked on` `OD-18`** |
| `p5-10` | `RG-017`: `wh_working_calendar_assignments` (`V510202`); `RH-011` layering |
| `p5-11` | `RG-016`: `wh_carrier_account_scopes` (`V510204`); `RL-011` tracking events partitioned |
| `p5-18` | `RG-001` row 12; `RK-001`: sister suggestions create `REQUESTED` transfers |
| `p5-19` | `RJ-013`: the kit trace |
| `p5-20` | `RG-009`: the matrix reads `whb_item_variant_values` |
| `p5-22` | `RH-004`: FK → `whb_companies`; `RG-018` endpoints and companies in `V500066` |
| `p6-02` | `RK-003`: the ABC recompute leaves this scope (`P3-25`) |
| `p6-08` | `RJ-002`: `TRANSIT-WH` → the per-transfer transit location at the source |
| `p6-10` | `RH-006`: `FALLBACK_MODES` + `registry.ts` union, listed in `PP-9`; branch tiles use `REGISTERED` |

**New task files (6).** Each carries the six required sections, a `TITLE:`/`LABELS:`/`---` front matter
**with no `issue:` line**, and the header shown. Scope bullets are the finding's disposition in §2.

| File | `TITLE:` | Header (`Part of … · Module … · Migrations … · Screens …`) | Requirements · Scenarios · Closes | Dep |
|---|---|---|---|---|
| `p3-25.md` | `[Warehouse] P3-25 · Simple ABC recompute — the class a v1 count programme reads, computed at v1.1` | `Part of __P3__` · `warehouse-base` + `warehouse` · **`V500069`** · `WS-016` (settings), `WS-093` | `FR-463` · `WH-SC-320` · `RK-003` | `P2-15` `P2-04` `P0-13` |
| `p5-24.md` | `[Warehouse] P5-24 · The v2 association junctions — UoM defaults, site-scoped supplier sources, company and owner links, owner-set cages, tax-scheme codes and configuration scopes` | `Part of __P5__` · `warehouse-base` + `warehouse` · **`V500070`** · **`V510220`** · sub-grids on existing screens, no new id | `FR-468` · `WH-SC-324` · `RG-010` `RG-011` `RG-012` `RG-013` `RG-014` `RG-018` `RG-020` | `P1-01` `P1-03` `P1-05` `P0-06` `P0-11` `P1-14` `P2-14` `P2-04` |
| `p5-25.md` | `[Warehouse] P5-25 · Trade-customer portal — the independent garage orders from the dealer on the portal surface` | `Part of __P5__` · `warehouse` · **`V510221`** · **`V511209`** · **`V511239`** · `WS-240` | `FR-464` · `WH-SC-321` · `RK-006` | `P5-08` `P2-08` `P1-08` |
| `p5-26.md` | `[Warehouse] P5-26 · Inter-company movement as a linked sale and purchase, created in one action` | `Part of __P5__` · `warehouse` · Migrations **—** · `WS-090` (action) | `FR-465` · `WH-SC-322` · `RK-007` | `P1-17` `P2-08` `P1-12` `P2-18` |
| `p5-27.md` | `[Warehouse] P5-27 · Value-banded approval levels — ordered typed rows, not a workflow engine` | `Part of __P5__` · `warehouse` · **`V510222`** · **`V511180`** · **`V511210`** · **`V511240`** · `WS-241` | `FR-466` · `WH-SC-323` · `RK-008` | `P2-23` `P2-01` `P1-12` `P2-02` |
| `p5-28.md` | `[Warehouse] P5-28 · Registry row translations — install-created codes render in the reader's language` | `Part of __P5__` · `warehouse-base` · **`V500071`** · a *Translations* tab on each registry screen | `FR-469` · `WH-SC-325` · `RL-015` | `P0-04` `P1-19` |

Labels follow the existing files: `task,warehouse,phase-p3|phase-p5,<module labels>`.

**Epics (8).**
- `00-EPIC-master`: 143 → **149** tasks with the new sum (17 + 21 + 29 + 4 + 25 + 13 + 28 + 12); `D-14`;
  `OD-18`/`OD-19`.
- `01-EPIC-p0`: the migration block re-derived with `V500037`.
- `02-EPIC-p1`: the invariants gain *one `REGISTERED` branch at every instant* (`FR-460`).
- `03-EPIC-p2`: the migration block re-derived with the seven `WH-206` pairs.
- `04-EPIC-p2in`: places of business (`RG-002`).
- `05-EPIC-p3`: `P3-25` added; blocks re-derived (`V500068`, `V500069`, `P3-11`'s pair, `P3-12` minus
  `V500061`); `:86` loses *"`V511180`–`V511199` left free"*.
- `07-EPIC-p5`: 23 → **28** tasks, the five new tasks in the build order and the blocks; `P5-09` blocked on
  `OD-18`.
- `08-EPIC-p6`: `P6-02`'s narrowed scope.

**`docs/IMPLEMENTATION-PLAN.md`**
- §2: six new rows in §2.5/§2.7, and every header or `Closes` change of §4.3–§4.5 (`P0-02`, `P0-16`,
  `P1-05`, `P2-01`, `P2-02`, `P2-04`, `P2-10`, `P2-12`, `P2-13`, `P2-15`, `P2-25`, `P3-04`, `P3-06`,
  `P3-11`, `P3-12`, `P5-09`). Section headings: P3 25 tasks, P5 28, total 149.
- §2.9 row 7: `V510220`–`V510222` carved from the app correction reserve, `V511180` from the free
  grid-config range, and the `WH-206` pairs enumerated.
- `PP-9` gains `RH-006`/`RH-007`/`RH-008`'s platform files. `PP-13` is withdrawn (`RH-002`).
- §3 dependency graphs; §7 gains the `OD-18` and `OD-19` gates; §8.1/§8.3 recomputed by their commands;
  §5.1 notes `RK-001`/`RK-004` in v1.

**`issues/README.md`**
- 143 → 149 tasks; 152 filed + 6 to file. The layout rows become `p3-01`…`p3-25` and `p5-01`…`p5-28`.
- 459 → 469 FRs; the scenario and screen markers `WH-SC-328`/`WS-242`.
- The round-4 citation count line, and *six new files await `create-issues.sh`*.

### 4.6 Post-fold amendment, 2026-09-10 — the six `NEW-TASK` dispositions folded into existing hosts

**Added the same day, after the fold agents merged, under a user rule: no duplicate tasks.** The six task
files §4.0 minted — `P3-25`, `P5-24`…`P5-28` — were filed as `#156`–`#161` and then folded into the most
similar existing task, found by the owner of the related table, screen or requirement. The files are
deleted and the six issues are closed as duplicates. **§2, §4.0 and §4.5 above are not rewritten**: they
are the dated record of what round 4 decided, and they name the former ids. Read the host for each id
from this table.

Each folded item keeps its own version. A v1.1 or v2 item inside a v1 host is marked *"v1.1 / v2
increment of this task — design the schema now, build in the v1.1 / v2 wave"* in a section headed
`## Round-4 additions (folded from former P?-??, #NNN)`.

| Former task | Finding | Host | Migration claimed by the host | Requirement · scenario now owned by the host |
|---|---|---|---|---|
| `P3-25` (`#156`) | `RK-003` | **`P1-03`** (`#33`) — owns `abc_class` (`FR-070`) · v1.1 increment | `V500069` | `FR-463` · `WH-SC-320` |
| `P5-24` (`#157`) | `RG-012`, `RG-014` | **`P1-05`** (`#54`) — owns `whb_warehouses`, `whb_locations` · v2 increment | `V500070` | `FR-468` (all of it; the rows below are its parts) |
| `P5-24` | `RG-020` (reason codes) | **`P0-04`** (`#43`) · v2 increment | **`V500072`** (new) | — |
| `P5-24` | `RG-013` | **`P0-06`** (`#56`) · v2 increment | **`V500073`** (new) | — |
| `P5-24` | `RG-018` (subscriptions) | **`P0-11`** (`#89`) · v2 increment | **`V500074`** (new) | — |
| `P5-24` | `RG-010`, `RG-020` (items) | **`P1-01`** (`#13`) · v2 increment | **`V500075`** (new) | — |
| `P5-24` | `RG-020` (UoMs) | **`P1-02`** (`#20`) · v2 increment | **`V500076`** (new) | — |
| `P5-24` | `RG-011` | **`P1-03`** (`#33`) · v2 increment | **`V500077`** (new) | `WH-SC-324` |
| `P5-24` | `RG-018` (inspection plans) | **`P1-14`** (`#120`) · v2 increment | `V510220` | — |
| `P5-24` | `RG-018` (print templates) | **`P5-21`** (`#114`) · v2, its own wave | **`V510223`** (new) | — |
| `P5-24` | `RG-018` (count programmes) | **`P2-04`** (`#37`) · v2 increment | none — a whitelisted scope value | — |
| `P5-25` (`#158`) | `RK-006` | **`P5-08`** (`#48`) — the portal surface and resolver it extends · v2 | `V510221`, `V511209`, `V511239` | `FR-464` · `WH-SC-321` · `WS-240` |
| `P5-26` (`#159`) | `RK-007` | **`P1-17`** (`#133`) — already owns `RK-007`'s v1 guard · v2 increment | none | `FR-465` · `WH-SC-322` |
| `P5-27` (`#160`) | `RK-008` | **`P2-23`** (`#146`) — owns `FR-408` on every approval surface · v2 increment | `V510222`, `V511180`, `V511210`, `V511240` | `FR-466` · `WH-SC-323` · `WS-241` |
| `P5-28` (`#161`) | `RL-015` | **`P1-19`** (`#139`) — owns the registry-name fallback and the locales · v2 increment | `V500071` | `FR-469` · `WH-SC-325` |

**Seven new migration numbers, and why §4.1 rule 2 is not broken by them.** Former `P5-24` claimed one
base migration (`V500070`) and one app migration (`V510220`) for tables whose parents belong to ten
different tasks. A Flyway version has exactly one owner (`D-2`, check 4), so the split needed one number
per host: `V500072`–`V500077` from the post-v1 base gap and `V510223` from the app correction reserve.
They were taken at the fold, after every fold agent had merged, and are recorded here as §4.0 recorded
its own. Every other migration moved with its content under the number §4.0 gave it. Net: **851 → 858**
allocated numbers; **149 → 143** tasks; tasks writing no migration **32 → 28** (`IMPLEMENTATION-PLAN.md`
§8.3).

**`RG-017` and `RG-018`'s *at-build* tables never lived in `P5-24`** and did not move: `wh3_client_counterparties`
(`P5-01`), `wh3_rate_card_clients` (`P5-02`), `wh3_sla_definition_clients` (`P5-07`),
`wh_channel_account_warehouses` (`P5-09`), `wh_working_calendar_assignments` (`P5-10`),
`wh_carrier_account_scopes` (`P5-11`), `whb_api_client_endpoints` + `whb_api_client_companies` (`P5-22`),
`whb_device_assignments` (`P3-03`) and `whin_compliance_registration_document_kinds` (`P2-IN-01`).

**Where the citations were re-pointed**: every task file, the eight epics, `issues/README.md`,
`issues/CREATED.md` (the six rows kept, marked closed), `DECISIONS.md` (`D-14` item 7, an amendment note),
`DATA-MODEL.md` §2 and §7, the FRD §6.28 intro, `BUILD-SPEC-SCREENS.md` (`WS-240`/`WS-241` owners,
`WS-093`, the registry block), `COMPETITOR-BENCHMARK.md`, `PORT-AND-ADAPTER-CONTRACT.md` and
`IMPLEMENTATION-PLAN.md` §2, §2.9, §3, §8 and §9. **Not edited**: `docs/reviews/` (dated records) and
`GAP-REGISTER-R3.md` §4.3, whose *next free id* table was true when written.


---

## §5 · What needs a person

| # | Decision | Deadline | Why it cannot be authored |
|---|---|---|---|
| **1** | **`OD-19`** — the statutory treatment of on-hand stock when a site's `REGISTERED` branch moves to another GSTIN | before `P1-05` ships *Change registration* | a tax question with a liability tail. Until it is answered the design refuses the change while stock is held, which is safe and operationally costly |
| **2** | **`OD-18`** — what v1 records for a drop-shipment | the first drop-shipped purchase | it decides what the product claims to track for goods it never touches. R7 asked for it in round 1 |
| **3** | **RE-VERIFY** the Packaged Commodities party list behind `RG-006`'s seed roles | before `P1-07` seeds registry 11 | a statutory fact to be checked, not decided — the India pack's standing rule |
| **4** | **UNVERIFIED** (`RH-010`) — whether a platform scheduled report applies the recipient's scope | before `P2-21` writes the provider | settled by reading `ReportDataProviderInterface`; recorded so it is not assumed |
| **5** | **Carried from round 3, unchanged** — `OD-1`, `OD-3`, `OD-8`, `OD-9`, `OD-16`, `OD-17`, `S-035`, and round 3's own §5 | as dated there | round 4 does not move them. `OD-9` interacts with `FR-461`: if the counter sale leaves warehouse, the rule moves with it |

R24 Appendix A asked that its ladders be ratified with `/functional-contract` before any build. This
register **adopts** them as fold text, which is an author's act. The functional-contract run remains the
build-time proof, and it is not a gate on the fold.

## §6 · What round 4 did not find

Each lens's §3 lists what it went looking for and found sound. They are not restated here. Five lenses
disputed **no** `L-`, `I-` or `IRR-` row. `RG-022`…`RG-027` and `RL-013` are *applications* of existing
invariants that the set had not written down.

No round-4 finding contradicts a round-1–3 **disposition** except where `D-14` does so by user decision,
and three where R23 corrects an earlier ruling against the live tree: `PP-13`/`PD-D11`, R18 §4's refusal
row, and PD §1.7.

## §7 · Traceability

```bash
cd warehouse-issues
python3 tools/check-design-set.py | tail -1       # -> 0 violations across 12 checks
```

- **Check 7 now sees round 4.** `FINDING_CITE_RE` is `R[A-HJ-L]` plus the single letters, and `REVIEWS`,
  `FINDING_DEF_RE`, `REVIEW_LABEL` and `AUTHORITY_STEM` carry `RG`, `RH`, `RJ`, `RK` and `RL`.
  **Negative test, run 2026-09-10:** a bogus `RG-` id numbered nine-nine-nine, cited on this line, made check 7 fail with *"RG-(that id) is
  cited but not defined in docs/reviews/R22-cardinality-and-junctions.md (R22 cardinality & junctions, 27
  findings)"*. The citation was removed and the check passed again.
- **Checks 1, 2 and 12** are satisfied by the three `file` declarations at the top of this document,
  which name exactly the allocated ids. As the P-CORE fold writes the rows, those mentions resolve
  normally, and the declarations shrink to the markers.
- **The check-13 `DESIGN-SET-DEFECTS.md` §5 asks for** gains a fourth clause: *every finding in
  `reviews/R22`–`R26` has a disposition row in `GAP-REGISTER-R4.md` §2.1–§2.5.* This §2 was generated from
  the lens headings and holds 83 rows.

## §8 · The honest readiness statement

1. **Round 4 is the first round to add task files since round 2.** It adds six, and five are v2. That is
   user decision (3) applied: nothing is lost, and no v1 task carries v2 work. **The v1 task set gains
   work, not tasks.**
2. **Ten BLOCKERs, and eight of them bind at or before `V500040`.** `RG-001` (`V500012`), `RL-001`
   (`V500005`), `RJ-002` (the first transfer), `RL-002` (`V500040`), `RH-002` (`V501000`) and `RJ-003`
   (`V510040`) are migration content that nobody has written. They are free today and not recoverable
   later.
3. **The branch model changed shape, and the new one is simpler to reason about than the old.** One
   `REGISTERED` link classifies, any visibility link grants access, and a draw across GSTINs is always a
   transfer. Sixteen readers now have one answer each (R22 §1.2.4), where before they had a scalar that
   answered the wrong question once history mattered.
4. **Two decisions need a person.** Both are narrow (§5). Neither blocks the fold, and each has a safe
   default written into the design.
