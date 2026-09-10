# R22 — cardinality and junctions

**Date** 2026-09-10 · **Prefix** `RG-` · **Branch** `docs/round-4-cardinality-and-gaps`

**Binding input — a user decision, not re-litigated here.** *Every association between two
independently-existing entities is an effective-dated M:N junction (with `is_primary` / a role where a
default is needed), even where the business needs only 1:N today. Parent→line composition and ledger
fact rows stay scalar. Branch↔warehouse specifically is a new junction `whb_warehouse_branches`
(`warehouse_id`, `branch_id`, a `relationship_role` catalogue — `REGISTERED`/`SERVING`/`FULFILMENT`/
`RETURNS` — `effective_from`/`effective_to`) with a partial unique index giving exactly one
`REGISTERED` branch per warehouse at a time; the `REGISTERED` branch supplies the GSTIN; issuing stock
to a `SERVING` branch under another GSTIN is a cross-GSTIN supply.* This reverses `FR-079`,
`DATA-MODEL.md` `whb_warehouses.branch_id`, the §9.2 dropped-table row for `wms_warehouse_branches`,
and the advice of `C-016`/`C-030`.

**File set read — 26 files.**

```bash
cd warehouse-issues
# docs/ (13): README · DECISIONS · DATA-MODEL (all 4,186 lines) · IRREVERSIBLE · WAREHOUSE-FUNCTIONAL-REQUIREMENTS
#             BUILD-SPEC-SCREENS · SCENARIO-CATALOGUE · INDIA-LOCALISATION-PACK · PLATFORM-DEPENDENCIES
#             COEXISTENCE · IMPLEMENTATION-PLAN · GAP-REGISTER · DESIGN-SET-DEFECTS
# docs/reviews/ (3): R16 (the shape this file mirrors) · R1 (C-016, C-030) · R6 (§2 row 2)
# issues/ (every file matching branch|gstin — 41 read at the matching lines; 10 read in full):
#             p1-05 p1-17 p1-18 p0-15 p1-09 p2in-01 p2in-03 p2-25 p4-03 p4-10
# classic (7): platform V149, V150, V160, V182 · accessories V30018 · BranchFilterService.java
#              · mobile/src/hooks/useScopedBranchOptions.ts
grep -rohE "\bRG-[0-9]{1,3}\b" docs/ issues/ | wc -l      # → 0 before this file (the prefix is free)
```

**Method, in three sentences.** I read every table row of `DATA-MODEL.md` §2 and put each column
that names another row into one of seven classes: **catalogue** (a vocabulary code — out of scope),
**composition** (parent→child), **fact** (a ledger or document record of what happened), **cache**
(an `L-4` projection of the ledger), **identity** (a member of a unique key), **extension** (a 1:1
specialisation) and **association** (two independently-existing masters) — and only the last class
is bound by the decision. Every association was then tested three ways: whether a list is needed
where a single value is stored, whether the scalar is mutable so that its *history* is the thing
being destroyed (`IRREVERSIBLE.md`'s `UB` class), and whether making it M:N would break an `L-n`
invariant, which makes it a **KEEP-SCALAR** finding rather than a junction. The branch↔warehouse
redesign was then walked through every reader of "the warehouse's branch" in the set — 16 of them,
tabulated in §1.2.4 — because a junction that nobody reads correctly is a scalar with extra rows.

---

## §1 · Verdict

**The set models one cardinality question with great care and every other one by default.** The
position key (`L-5`, nine members), the item key (`I-19`), the serial key, the shipment↔order junction
(*"the cardinality is a one-way door"*, `DATA-MODEL.md:1032`) and the counterparty role link
(`:513`) were argued. The associations between masters mostly were not. They were written as the
obvious scalar, and several of those scalars are **mutable columns whose history is the evidence a
filed return depends on**.

**The branch↔warehouse scalar is the worst of them, and the design set half-knows it.** `FR-079`
says the GSTIN is *"read from the branch, never duplicated onto the warehouse"*
(`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:219`). Yet `whb_warehouses` carries **`tax_registration_id`**
and **`legal_entity_id`** beside `branch_id` (`DATA-MODEL.md:452`). `IRR-57` defends those two by
arguing that *"without them a historical transfer cannot be classified as supply vs non-supply — for
a period whose return has already been filed"* (`IRREVERSIBLE.md:247`). That argument is correct, and
it defeats the scalar it defends. A mutable `branch_id` or `tax_registration_id` answers *"which
registration is this site under **now**"*. The filed period asks *"which registration was it under
**on 14 March**"*, and that answer is overwritten the first time a registration changes. Only
effective-dated rows keep it. `whb_stock_movements` can never gain a branch column after `PNR-2`
(`DATA-MODEL.md:2905`), so **the junction is the only place in the design where registration history
can live**. That makes `RG-001` a v1 BLOCKER independently of the user decision. The decision only
settles its shape.

**The GSTIN side has the mirror-image defect, and no scenario can see it.** `whin_gstin_profiles`
declares `gstin` unique with a scalar `branch_id` (`DATA-MODEL.md:1189`, `issues/p2in-01.md:47`). So
one GSTIN has exactly one branch. That is false in the only jurisdiction it exists for: a company
holds **one** registration per state, and every other branch in that state is an additional place of
business under it. The scenario cast gives each branch its own state (`SCENARIO-CATALOGUE.md:104-108`),
so no acceptance test can see the defect. The first dealer group with two Delhi showrooms will
(`RG-002`).

**Seven MAJOR findings are the same shape one level down:**
- a counterparty with one tax id and one address, when its GSTIN varies by ship-to state (`RG-003`)
- a location with one `assigned_user_id`, whose overwrite destroys custody history (`RG-004`)
- an item with one category, where the category is the resolution key for costing (`RG-005`)
- a lot with one counterparty, where Legal Metrology needs the manufacturer, packer and importer
  (`RG-006`)
- a serial with one secondary identifier, when a dual-SIM phone has two IMEIs (`RG-007`)
- a fixed pick face stored twice, in two different cardinalities (`RG-008`)
- a variant model capped at three fixed slots, on the one schema `A-3` calls unrecoverable (`RG-009`)

**The reverse is equally important, and it is why six of the 27 findings are KEEP-SCALAR.** The
decision is safe exactly as far as its own carve-out. It must not reach:
- item, lot or serial identity (`I-19`)
- the base UoM (`L-7`, `I-9`)
- physical containment (`I-4`'s per-warehouse sequence)
- the stock period (`L-8`'s one-period-per-movement)
- the ledger line and the position key (`L-5`, `L-2`)

Branch or registration must **never** become a position-key member: it is derived from the warehouse's
`REGISTERED` link at `occurred_at`, the same move `OD-10` made for MRP.

---

## §1.1 · Coverage table — every scalar association in `DATA-MODEL.md` §2

**Catalogue codes are excluded by construction** — `*_type_code`, `*_status_code`, `uom_class_code`,
`default_putaway_strategy_code`, currency codes and every registry FK of §2.1.1. A code classifies a
row; it does not associate two things that exist independently (§1.3 note 3 of `DATA-MODEL.md`
references them by value for exactly that reason). **The ledger carve-out is applied as the decision
states it**: `whb_stock_movements`, `_lines`, positions, reservations, cost layers, consumptions,
handovers, outbox rows and every document line are facts or caches, and are not listed row by row.

| # | Table.column | Points at | Class | Verdict | Finding |
|---|---|---|---|---|---|
| 1 | `whb_warehouses.branch_id` | `branches` | association | **JUNCTION v1** `whb_warehouse_branches` | **`RG-001`** |
| 2 | `whb_warehouses.tax_registration_id`, `.legal_entity_id` | registration / legal entity | association (a second copy of row 1 and of `company_id`) | **DROP** — resolved through rows 1 and 4 | **`RG-001`** |
| 3 | `whin_gstin_profiles.branch_id` (+ `gstin` unique) | `branches` | association | **JUNCTION v1** `whin_gstin_profile_branches` | **`RG-002`** |
| 4 | `whb_warehouses.company_id` | `whb_companies` | association | JUNCTION v2 `whb_warehouse_companies` | `RG-012` |
| 5 | `whb_locations.warehouse_id`, `.parent_location_id` | warehouse, location | composition (physical containment) | **KEEP-SCALAR** | `RG-025` |
| 6 | `whb_locations.assigned_user_id` | `users` | association | **JUNCTION v1** `whb_location_user_assignments` | **`RG-004`** |
| 7 | `whb_locations.dedicated_owner_id` | `whb_owners` | association | JUNCTION v2 `whb_location_owner_dedications` | `RG-014` |
| 8 | `whb_locations.fixed_item_id` | `whb_items` | association, stored twice | **JUNCTION v1** — `whb_item_location_settings` moved forward | **`RG-008`** |
| 9 | *(missing)* location ↔ functional zone | `whb_locations` | association | JUNCTION v1.1 `whb_location_zone_memberships` | `RG-015` |
| 10 | `whb_owners.company_id` | `whb_companies` | association | JUNCTION v2 `whb_owner_companies` | `RG-013` |
| 11 | `whb_owners.counterparty_id` | `whb_counterparties` | extension (a stock-holding role of a party; many owners per party is legitimate) | KEEP-SCALAR | §3 |
| 12 | `whb_counterparties` one address block, one `gln` | address | cardinality | **CHILD v1** `whb_counterparty_addresses` | **`RG-003`** |
| 13 | `whb_counterparties.national_tax_id` as the only registration | registrations | cardinality | **CHILD v1** `whb_counterparty_tax_registrations` | **`RG-003`** |
| 14 | `whb_items.owner_id` · `whb_lots.(owner_id,item_id)` · `whb_serials.(owner_id,item_id)` | owner, item | identity (`I-19`) | **KEEP-SCALAR** | `RG-023` |
| 15 | `whb_items.category_id` | `whb_item_categories` | association | **JUNCTION v1** `whb_item_category_assignments` | **`RG-005`** |
| 16 | `whb_items.base_uom_code` | `whb_uoms` | identity (`L-7`) | **KEEP-SCALAR** | `RG-024` |
| 17 | `whb_items.purchase_uom_code`, `.sale_uom_code` | `whb_uoms` | association (defaults) | JUNCTION v2 `whb_item_uom_defaults` | `RG-010` |
| 18 | `whb_items.variant_axis_1/2/3_value_id` | axis values | cardinality (three fixed slots) | **JUNCTION v1** `whb_item_variant_values` | **`RG-009`** |
| 19 | `whb_items.style_item_id` · `whb_item_categories.parent_category_id` | item, category | composition (tree) | KEEP-SCALAR | §3 |
| 20 | `whb_items.tax_classification_code` · `whb_uoms.gst_uqc_code`/`unece_rec20_code` | jurisdiction codes | cardinality | CHILD v2 | `RG-020` |
| 21 | `whb_item_categories.default_inspection_plan_id` | `wh_inspection_plans` (generic) | association (default) | RULE ROWS v2 | `RG-018` |
| 22 | `whb_lots.counterparty_id` | `whb_counterparties` | association | **JUNCTION v1** `whb_lot_counterparties` | **`RG-006`** |
| 23 | `whb_serials.secondary_serial` | identifier | cardinality | **CHILD v1** `whb_serial_identifiers` | **`RG-007`** |
| 24 | `whb_serials.current_location_id/_lpn_id/_status_code`, `.sold_to_counterparty_id` | location, LPN, party | cache (`L-4`) | **KEEP-SCALAR** | `RG-027` |
| 25 | `whb_lpns.owner_id` (beside `is_mixed_owner`) | `whb_owners` | identity, self-contradicting | KEEP-SCALAR, redefine | `RG-022` |
| 26 | `whb_stock_periods.(company_id, warehouse_id)` | company, warehouse | rule scope bound to `L-8` | **KEEP-SCALAR** | `RG-026` |
| 27 | `whb_number_series.(company_id, warehouse_id, branch_id)` | scope tuple | rule scope | KEEP; branch resolved through `RG-001` | `RG-001` |
| 28 | `whb_outbox_subscriptions.owner_filter_id` | `whb_owners` | association (config) | JUNCTION v2 | `RG-018` |
| 29 | `whb_devices.(warehouse_id, assigned_to)` | warehouse, user | association | JUNCTION at build (v1.1) | `RG-018` |
| 30 | `whb_api_clients.company_id`, `.allowed_endpoints` (a list in one column) | company, endpoints | association + list | CHILD at build (v2) | `RG-018` |
| 31 | `wh_transfer_orders.source_branch_id`, `.destination_branch_id` | `branches` | fact (frozen at creation, `FR-305`) | KEEP-SCALAR + link snapshot | `RG-001` |
| 32 | `wh_goods_receipts.po_id` · `wh_landed_cost_documents.grn_id` · `wh_return_receipts.(rma_id, original_shipment_id, original_demand_order_id)` · `wh_supplier_returns.(origin_grn_id, origin_lot_id)` | documents | header scalar contradicting a line-level association | DERIVE / DROP v1 | `RG-019` |
| 33 | `wh_count_programs.warehouse_id` | `whb_warehouses` | association (config) | SCOPE ROW v2 | `RG-018` |
| 34 | `wh_carriers.counterparty_id` | `whb_counterparties` | extension (1:1) | KEEP-SCALAR + `uk` | `RG-016` |
| 35 | `wh_carrier_accounts.owner_id` (and no warehouse) | owner, warehouse | association | JUNCTION v2 `wh_carrier_account_scopes` | `RG-016` |
| 36 | `wh_print_templates.(owner_id, warehouse_id)` | owner, warehouse | association (scope of a default) | JUNCTION v2 | `RG-018` |
| 37 | `wh_channel_accounts.warehouse_id` · `wh_working_calendars.(warehouse_id, owner_id)` | warehouse, owner | association | JUNCTION at build (v2) | `RG-017` |
| 38 | `wh3_clients.counterparty_id` · `wh3_rate_cards.client_id` · `wh3_sla_definitions.client_id` | party, client | association | JUNCTION at build (v2) | `RG-017` |
| 39 | `wh3_clients.owner_id` (`uk`) | `whb_owners` | extension (`T1`) | KEEP-SCALAR | §3 |
| 40 | `whin_compliance_registrations.document_kinds` | a list in one column | cardinality | CHILD at build (v1) | `RG-018` |
| 41 | `whad_counter_sales.(branch_id, warehouse_id)` | branch, warehouse | fact (document) + a pair rule | KEEP + validate through `RG-001` | `RG-001` |
| 42 | `whaf_van_stock_assignments` | location, technician | existing junction, adapter-owned | KEEP as extension of `RG-004`'s base row | `RG-004` |
| 43 | the effective dates of every existing junction | — | convention | AMEND v1 | `RG-021` |

```bash
# the scalar-association inventory above was built from these two greps over §2, then classified by hand
awk '/^## 2\. The tables/,/^## 3\. The split proof/' docs/DATA-MODEL.md | grep -oE '`[a-z_]+_id`' | sort | uniq -c | sort -rn | head -40
awk '/^## 2\. The tables/,/^## 3\. The split proof/' docs/DATA-MODEL.md | grep -cE '^\| `(whb|wh|wh3|whin|wha[a-z])_'   # 169 table rows
```

**Arithmetic:** 43 rows · **17** become a junction or child table (**10 in v1**, **7** later) · **9**
KEEP-SCALAR · **1** DROP · **3** re-shaped document headers · the remainder amendments or KEEP with a
validation rule.

---

## §1.2 · Branch ↔ warehouse — the specification (`RG-001`'s disposition, in full)

### §1.2.1 · The rows, in `DATA-MODEL.md` §2 format

**A fifteenth registry**, `DATA-MODEL.md` §2.1.1 shape (§1.8's common columns implied):

| # | Registry | Table | Behaviour columns | Ver | Gate |
|---|---|---|---|---|---|
| **15** | **Warehouse–branch relationship role** | **`whb_warehouse_branch_roles`** | `is_registration` (true on exactly one system row), `grants_branch_visibility`, `allows_issue_to_branch`, `allows_returns_from_branch`, `is_fulfilment_source`, `max_current_per_warehouse` (1 for `REGISTERED`, null = many) · seed `REGISTERED` (`is_system`, `is_registration`), `SERVING`, `FULFILMENT`, `RETURNS` | v1 | **PNR-1** |

**The junction**, `DATA-MODEL.md` §2.1.2 shape:

| Table | Purpose | Key columns | Keys / indexes | FKs | FR | Ver |
|---|---|---|---|---|---|---|
| `whb_warehouse_branches` | **Which platform branches a site stands in which relationship to, and since when.** Exactly one `REGISTERED` branch at any instant — the branch whose registration the site is declared under, and the only source of the site's tax identity. Every other role is an ordinary row. **Never deleted once a movement exists in its range; a change closes one row and opens the next** | `warehouse_id`, `branch_id`, `relationship_role_code`, `effective_from` `TIMESTAMPTZ`, `effective_to` `TIMESTAMPTZ` (null = open, half-open `[from, to)`), `is_primary` (the branch-side default for `FULFILMENT`/`RETURNS`), `priority`, `change_reason_code_id`, `decision_note` | uk one current `REGISTERED` per warehouse (partial); **exclusion** — no two `REGISTERED` ranges overlap for one warehouse; **exclusion** — no two ranges overlap for one `(warehouse, branch, role)`; uk one current primary per `(branch, role)` (partial); idx(`branch_id`,`warehouse_id`) `WHERE effective_to IS NULL`; idx(`warehouse_id`,`effective_from`) | `warehouse_id → whb_warehouses` `ON DELETE RESTRICT`; `branch_id ↓platform branches(id)` `NO ACTION` (`B1` moves here); `relationship_role_code → whb_warehouse_branch_roles(code)` — **no `ON UPDATE CASCADE`**, see §1.2.2; `change_reason_code_id → whb_reason_codes` | new FR (next free id) · `FR-079` rewritten · `FR-305` `FR-307` `FR-314` `FR-404` `FR-405` | **v1** |

**`whb_warehouses` as amended** — **loses** `branch_id`, `tax_registration_id` and `legal_entity_id`;
keeps `company_id` (until `RG-012`), `state_code` (the site's own address fact, no longer "derived
from the GSTIN", `INDIA-LOCALISATION-PACK.md:359-362`) and everything else. `idx(branch_id)` goes.

### §1.2.2 · Constraints

```sql
-- V500012 (P1-05), in the same file as whb_warehouses, before any movement can exist
CREATE EXTENSION IF NOT EXISTS btree_gist;       -- precedent: accounting-base V600030:72, assets V60634:29
DO $$ BEGIN                                       -- and fail loudly, as assets V60634:427-429 does
  IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'btree_gist') THEN
    RAISE EXCEPTION 'V500012: btree_gist is absent; the REGISTERED-history exclusion cannot be created';
  END IF; END $$;

CREATE UNIQUE INDEX uk_whb_warehouse_branches_one_registered
    ON whb_warehouse_branches (warehouse_id)
 WHERE relationship_role_code = 'REGISTERED' AND effective_to IS NULL;          -- the user's index

ALTER TABLE whb_warehouse_branches
  ADD CONSTRAINT chk_whb_warehouse_branches_range
      CHECK (effective_to IS NULL OR effective_to > effective_from),
  ADD CONSTRAINT uk_whb_warehouse_branches_registered_history                   -- one at EVERY instant,
      EXCLUDE USING gist (warehouse_id WITH =,                                  -- not only now
                          tstzrange(effective_from, effective_to, '[)') WITH &&)
      WHERE (relationship_role_code = 'REGISTERED'),
  ADD CONSTRAINT uk_whb_warehouse_branches_pair_history
      EXCLUDE USING gist (warehouse_id WITH =, branch_id WITH =, relationship_role_code WITH =,
                          tstzrange(effective_from, effective_to, '[)') WITH &&);

CREATE UNIQUE INDEX uk_whb_warehouse_branches_primary_per_branch
    ON whb_warehouse_branches (branch_id, relationship_role_code)
 WHERE is_primary AND effective_to IS NULL;
```

Four further guards, each with the service pre-check first (§6.0 of `DATA-MODEL.md`):

1. **"Exactly", not "at most".** The partial index gives *at most one*. The *at least one* half is a
   deferred constraint trigger on `whb_warehouses` (insert/update) and on `whb_warehouse_branches`
   (update/delete). It asserts that every active warehouse ends the transaction with a current
   `REGISTERED` row, and it is memoised per §6.2 of `DATA-MODEL.md`. The warehouse-create service
   writes the site and its `REGISTERED` link in one transaction. `WS-016` offers no way to save a site
   without one.
2. **The ledger refuses a movement at an unregistered instant.** A plain `BEFORE INSERT` trigger on
   `whb_stock_movements` requires a `REGISTERED` row whose range contains `NEW.occurred_at`. It is not
   deferred, so the service can translate the failure (the `I-6` pattern, `DATA-MODEL.md:2570-2572`).
   It lands in `V500030` and is **a new `I-n`, the next free after `I-21`**, allocated by
   `DATA-MODEL.md` §6 — not here.
3. **Registration history is append-only once a movement stands on it.** A `BEFORE UPDATE OR DELETE`
   trigger on `REGISTERED` rows applies three rules:
   - `DELETE` is refused if any posted movement at the warehouse falls inside the row's range.
   - `warehouse_id`, `branch_id`, `relationship_role_code` and `effective_from` are frozen on such a
     row.
   - `effective_to` may only be set at or after the latest posted `occurred_at` in the range, and
     never inside a `CLOSED` period (`I-10`).

   The check is one seek on `idx_whb_stock_movements_wh_occurred` (`DATA-MODEL.md:643`). The trigger
   reads the ledger, so it cannot live in `V500012`. It goes in a number from the
   `V500037`–`V500039` gap, or is folded into `V500032` beside `I-10`, at `P0-02`'s choice. Non-
   `REGISTERED` rows classify nothing (§1.2.3) and are freely editable, subject to the pair exclusion.
4. **The role code is immutable.** The partial index and the exclusion predicate carry the literal
   `'REGISTERED'`, so that registry row is `is_system` and its `code` may never change. The FK is
   declared **without** the `ON UPDATE CASCADE` that `DATA-MODEL.md:132` gives other natural-key
   parents. A cascade would silently empty the predicate. The other three codes are open catalogue
   rows under `D-10`, and `I-18`'s test enumerates **fifteen** registries.

**Jurisdiction rules stay out of base (`D-8`).** Base exposes a `List<WarehouseBranchLinkValidator>`
bean collection, the `IBoomBarrierHandler` pattern R1 records. `warehouse-india` contributes three
validators:
- (a) the `REGISTERED` branch's GSTIN state code equals `whb_warehouses.state_code`, because an
  additional place of business is always in the registration's own state;
- (b) its GSTIN profile belongs to the warehouse's company (`RG-002`);
- (c) the change rule of §1.2.6.

`SERVING`/`FULFILMENT`/`RETURNS` may be in any state. Across a state line they are an inter-state
supply, and that is the point of recording them.

### §1.2.3 · What each role means

| Role | Meaning | Classifies movements? | Grants branch visibility? | Tax consequence |
|---|---|---|---|---|
| **`REGISTERED`** | The site is declared under this branch's registration. Exactly one at any instant | **Yes** — the only role that does | yes | the site's GSTIN, series, Rule 56 account and envelope branch |
| **`SERVING`** | This branch's operations draw stock from the site (a central godown serving showrooms and workshops) | no | yes | issue to it under a **different** GSTIN is a **cross-GSTIN supply**: a transfer order with `is_taxable_supply = true`, a tax invoice or challan, and an e-way bill above the threshold — never a plain issue. Same GSTIN: a non-supply challan |
| **`FULFILMENT`** | The site is a fulfilment source for orders taken at this branch; `is_primary` + `priority` give sourcing order | no | yes | the bill-from registration is the shipping site's `REGISTERED` GSTIN at despatch; the ordering branch is a label |
| **`RETURNS`** | The site accepts returns on this branch's behalf | no | yes | a return of goods despatched under another GSTIN is a cross-GSTIN inbound, flagged on the return receipt; its document is `warehouse-india`'s |

**A non-physical site is not a registration.** `FR-081`'s `is_physical = false` sites (the cast's
`TRANSIT-WH`, `SCENARIO-CATALOGUE.md:110`; `RE-002`) still carry a `REGISTERED` row, because guard 1
admits no exception. That row is **administrative only**. A line at a per-transfer transit location
resolves to the transfer's frozen `source_branch_id`, because `FR-148` makes the sender hold in-transit
stock (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:318`). Otherwise every consignment on the road would be
filed under whichever branch registered the transit pool.

### §1.2.4 · Everything that reads "the warehouse's branch"

| # | Reader | Rule | Changes in |
|---|---|---|---|
| 1 | **GSTIN resolution** | `from_gstin` = the profile of the `REGISTERED` branch at the document date, via `whin_gstin_profile_branches` (`RG-002`), cross-checked against `branches.gst_number` (`platform/…/V182:7`). The e-way bill's dispatch-from address, pincode and state are the **warehouse's** (`whb_transport_details.dispatch_from_*`), the GSTIN is the branch's (`issues/p2in-04.md:87`) | `P2-IN-01` `P2-IN-03` `P2-IN-04` · `WS-173` `WS-178` `WS-179` |
| 2 | **Number series per branch** | A branch-scoped series (challan, transfer invoice) resolves `whb_number_series.branch_id` = the issuing site's `REGISTERED` branch at the document date. Warehouse-scoped series (GRN, pick, ship) are unaffected. A re-registration switches series from that instant and renumbers nothing (`FR-307`, `FR-426`) | `P1-09` `P2-IN-03` `P4-06` · `WS-061` |
| 3 | **Branch-scope guard / record-level access** | §1.2.5 — the user's branches resolve to a warehouse set through **current** links whose role `grants_branch_visibility` | `P0-15` `P1-18` `P6-10` · `FR-404` `FR-405` · `WH-SC-242` `WH-SC-243` |
| 4 | **Transfers** | `source_branch_id` / `destination_branch_id` stay **frozen snapshots** (`FR-305`), derived at creation from the two sites' `REGISTERED` links — or, for an issue to a `SERVING` branch, the serving branch. **Add `source_warehouse_branch_id` and `destination_warehouse_branch_id`** → `whb_warehouse_branches(id)` (app → base, downward, legal) so the derivation is auditable | `P1-17` `P2-02` · `WS-090` · `WH-SC-124` `WH-SC-206` |
| 5 | **Issue to a `SERVING` branch** | GSTINs compared on `branches.gst_number`, exactly as the transfer service already does (`PLATFORM-DEPENDENCIES.md:143`). Differ → a taxable transfer; equal → a non-supply challan | `P1-17` `P2-02` `P2-IN-03` |
| 6 | **Counter sale** | `whad_counter_sales.(branch_id, warehouse_id)` is valid only if the branch holds a current `REGISTERED` or `SERVING` link to the site. A `SERVING` link under a **different** GSTIN is refused with `422 CROSS_GSTIN_COUNTER_SALE` and offers *Raise transfer*: a counter sale may not silently become a cross-GSTIN supply. The adapter compares `branches.gst_number` because it cannot read `whin_` (`D-1`) | `P2-25` · `WS-194` · `FR-359` |
| 7 | **Demand fulfilment** | The bill-from registration is the shipping site's `REGISTERED` branch at despatch, carried on the envelope (row 10) | `P2-08` `P2-10` |
| 8 | **Returns** | A return receipt compares its site's `REGISTERED` GSTIN with the original shipment's and flags a mismatch as cross-GSTIN (`A-1` basic returns stay v1; the document is P2-IN's) | `P2-12` |
| 9 | **Rule 56 stock account · ITC-04** | Movement → site → `REGISTERED` link **at `occurred_at`** → branch → profile. It is *"per registration, not per warehouse"* (`issues/p4-03.md:110`), and that is now computable for history. A site re-registered mid-period is split at the switch instant; §1.2.6 ensures it holds no stock at that instant, so the split needs no synthetic line | `P4-03` `P4-02` · `WS-183` · `FR-314` |
| 10 | **Accounting envelope** | `branch` = the `REGISTERED` branch at `occurred_at`, frozen in the hashed payload (`FR-233`) | `P2-18` · `WH-SC-156` |
| 11 | **Reports grouped by branch** | **Stock and value group by the `REGISTERED` branch**: as at the report date for as-at reports (`WS-208`, `WS-211`, `WS-212`), and at each movement's `occurred_at` for period reports (`WS-210`'s opening/inward/outward/closing, `FR-386`). A "linked branches" view is a separate grouping and is **not additive across roles** — summing it double-counts every shared site | `P2-20` `P2-21` `P2-05` · `FR-162` `FR-386` |
| 12 | **Availability across branches · sister branch** | Group by `REGISTERED`. A shared site appears once, tagged with its serving branches. A "sister" is a site with a **different** `REGISTERED` branch, so a site is never its own sister | `P2-24` `P2-15` `P5-18` · `FR-073` `FR-254` · `WH-SC-102` |
| 13 | **In-transit** | Held by the transfer's frozen `source_branch_id`, never by a transit pool's registration (§1.2.3) | `P2-02` · `FR-148` |
| 14 | **Dashboards** | Every tile scoped by the resolved warehouse set; branch-grouped tiles use `REGISTERED` | `P6-10` · `BUILD-SPEC-SCREENS.md:2059` |
| 15 | **Mobile branch picker** | `useScopedBranchOptions` → branch → `GET /warehouses/dropdown?branchId=` returns sites with a current link of a visibility role. `REGISTERED` sites come first, each with a role badge. `WS-016`'s mobile `additionalFilters.branchId` means *"linked to"*, not *"registered under"* (`BUILD-SPEC-SCREENS.md:842-844`) | `P1-05` and every P3 RF site picker |
| 16 | **Stock periods, valuation grain** | **Unaffected.** Period scope is company/warehouse (`RG-026`). The valuation grain is `(company, owner, item, site)` (`FR-236`), and a re-registration moves no stock | — |

### §1.2.5 · Branch scope → warehouse scope

Platform resolves a user's branches from `branch_staff` (`platform/…/V150__create_branch_staff_table.sql:14-24`)
through `BranchFilterService.resolveBranchFilter` (`…/service/common/BranchFilterService.java:77-92`). The
platform fragment filters on **`%s.branch_id`** (`:167-169`). **No `whb_`/`wh_` ledger or document table
has a `branch_id` column**, so the fragment, and `PLATFORM-DEPENDENCIES.md` §2.3's architecture rule —
*"every native query … from a `whb_`/`wh_` table **with a `branch_id` column** must bind
`:userBranchIds`"* (`:179-181`) — would both pass vacuously on every warehouse grid. The replacement:

```sql
-- resolved once per request by WarehouseScopeService, inside warehouse-base
SELECT DISTINCT wb.warehouse_id
  FROM whb_warehouse_branches wb
  JOIN whb_warehouse_branch_roles r ON r.code = wb.relationship_role_code
 WHERE wb.branch_id IN (SELECT CAST(UNNEST(STRING_TO_ARRAY(CAST(:userBranchIds AS TEXT), ',')) AS UUID))
   AND r.grants_branch_visibility
   AND wb.effective_from <= CURRENT_TIMESTAMP
   AND (wb.effective_to IS NULL OR wb.effective_to > CURRENT_TIMESTAMP)
```

```java
// the warehouse twin of BranchFilterService.BRANCH_FILTER_SQL — same null/'' shape, warehouse column
public static final String WAREHOUSE_FILTER_SQL =
    "(CAST(:userWarehouseIds AS TEXT) IS NULL OR CAST(:userWarehouseIds AS TEXT) = '' " +
    "OR %s.warehouse_id IN (SELECT CAST(UNNEST(STRING_TO_ARRAY(CAST(:userWarehouseIds AS TEXT), ',')) AS UUID)))";
```

**Six rules, the second of which is a new leak:**

1. **View-all** → `null` → no predicate.
2. **Empty in, empty out — twice.** An empty branch set short-circuits to zero rows, as
   `PLATFORM-DEPENDENCIES.md:175-178` already requires. **So does a non-empty branch set that resolves
   to zero warehouses** — a branch with no site link. That case is new with the junction. The fragment
   reads `''` as *no filter*, so a service that passes it through returns every site to a user who
   should see none. Assert both cases in the per-endpoint negative test.
3. **Two-ended records** (transfers) are in scope if **either** site is in the set.
4. **Branch-carrying tables** (`whad_counter_sales`, `whin_gstin_profiles`, `whin_delivery_challans`,
   `whb_number_series`) keep `BRANCH_FILTER_SQL` directly.
5. **Composition** is owner ∩ (branch → warehouse) ∩ warehouse grant (`P1-18`'s order,
   `issues/p1-18.md:91-92`). If `RA-001`'s grant table is adopted, it **narrows** within the
   branch-derived set and never widens it.
6. **Access is present-tense; classification is as-at.** Who may see a site is decided on today's
   links. Which registration a historical movement belongs to is decided on the link at its
   `occurred_at`. Mixing the two is how a user who lost a branch keeps seeing it, or how last year's
   return is re-filed under this year's registration.

`PLATFORM-DEPENDENCIES.md` §2.3 item 3 is restated: *every native query selecting from a `whb_`/`wh_`
table with a `warehouse_id` (or `source_`/`destination_warehouse_id`) column binds
`:userWarehouseIds`.*

### §1.2.6 · Changing a registration — the one hard workflow

A new verb permission, `warehouse:warehouses:change_registration` (seeded by `P0-15`'s `V501000`), is
maker–checker (`FR-408`). The service:
1. refuses an `effective_from` in a `CLOSED` period, or earlier than the site's latest posted
   `occurred_at`;
2. **refuses while the site holds non-zero on-hand, if the old and new GSTINs differ.** Goods at a
   place of business that changes registration have changed registration, and the design has no
   movement that says so. The operator empties the site by transfer first. **The statutory treatment of
   on-hand stock at a registration change is `RE-VERIFY` and is escalated with this finding; it is not
   decided here**;
3. closes the current row and opens the next at the same instant (contiguity, asserted nightly);
4. writes a `whb_audit_events` row, and prompts for the new branch-scoped series (§1.2.4 row 2).

### §1.2.7 · Every artefact that must change

**Reviews are dated records and are never edited** (`DECISIONS.md` §6); `C-016`/`C-030` (`R1:517`,
`:531`) are superseded by disposition in the next gap register, not by rewriting. R6 triaged
`wms_warehouse_branches` to **`B`** — `warehouse-base` (`R6:214`, `:222`); `DATA-MODEL.md` §9.2
overruled it, and this restores R6's triage with role and dating added.

| Artefact | Where | Change |
|---|---|---|
| `DECISIONS.md` §2 | new `D-` row (next free) | **Record the user decision in the spine.** Without it `FR-079`'s reversal rests on a review, and the next reader re-litigates it |
| `DATA-MODEL.md` §2.1.1 | registry table, `:411-433` | row 15 `whb_warehouse_branch_roles`; `I-18` enumerates fifteen |
| `DATA-MODEL.md` §2.1.2 | `whb_warehouses` `:452` | drop `branch_id`, `tax_registration_id`, `legal_entity_id`, `idx(branch_id)`; add the `whb_warehouse_branches` row |
| `DATA-MODEL.md` §2.1.8 | positions note `:755` | *"every branch guard is one predicate"* → *"every warehouse-set guard"* |
| `DATA-MODEL.md` §2.1.13 | `whb_number_series` `:910` | the `branch_id` resolution rule |
| `DATA-MODEL.md` §2.2.2 | `wh_transfer_orders` `:1003` | add the two link-row snapshots |
| `DATA-MODEL.md` §2.4.1 / §2.5.1 | `:1189`, `:1272` | `RG-002`; the counter-sale pair rule |
| `DATA-MODEL.md` §3.2 | `B1` `:1411`, `W8` `:1435`, `N2` `:1468`, `A6` `:1485` | `B1` becomes `whb_warehouse_branches.branch_id`; `W8` gains the snapshots; `N2` moves to `RG-002`'s junction |
| `DATA-MODEL.md` §4.1 / §4.10 | `:1586`, `:1997` | ER edges `BRANCHES }o--o{ WHB_WAREHOUSES` through the junction; drop *"one branch, one GSTIN"* |
| `DATA-MODEL.md` §6.3 | constraint table `:2327-2348` | the new `I-n` (§1.2.2 guard 2) |
| `DATA-MODEL.md` §7.2 | `WHB-12` `:2894`; §7.7 `PNR-1` `:3100` | `V500012` creates three tables; the history trigger's number |
| `DATA-MODEL.md` §8.1 / §8.4 | inventory + version blocks | +2 tables, **regenerated together** (`DECISIONS.md` §7 rule 7) |
| `DATA-MODEL.md` §9.2 | `:3991` | `wms_warehouse_branches`: **dropped → re-homed** as `whb_warehouse_branches` |
| `IRREVERSIBLE.md` | `IRR-57` `:247`; §3.4 `:339`; §4.5 `:554-555` | `IRR-57` keeps `state_code` and replaces the two scalars with the dated link; `:555` reversed; a new `IRR` row (next free): registration history, `UB`, `PNR-1` |
| FRD | `FR-079` `:219` · `FR-080` `:220` · `FR-305` `:567` · `FR-307` `:569` · `FR-314` `:576` · `FR-404`/`FR-405` `:710-711` · `FR-233` `:436` · `FR-148` `:318` · `FR-162` `:332` · `FR-386` `:687` · `FR-073` `:208` · `FR-254` `:466` · `FR-342` `:615` · `FR-359` `:643` · `FR-426` `:746` | rewrite `FR-079`; drop the two scalars from `FR-080`; every other row gains *"the `REGISTERED` branch at …"*; **one new FR** (next free) for the junction |
| Scenarios | cast `:104-111` · `WH-SC-045` `:216` · `WH-SC-102` `:283` · `WH-SC-124` `:315` · `WH-SC-156` `:357` · `WH-SC-206` `:434` · `WH-SC-242` `:489` · `WH-SC-243` `:490` | `WH-SC-045`'s *"attempting to attach a second registration is not offered"* → a second **current `REGISTERED`** is refused and a `SERVING` link is offered. **Six new scenarios** (next free ids): a re-registration splitting a Rule 56 period; an issue to a cross-GSTIN `SERVING` branch; a refused counter sale; a shared site seen by two branch-scoped users; a cross-state `REGISTERED` refused; a movement at an unregistered instant refused. **Add a second Delhi branch to the cast** — without it `RG-002` has no test |
| Screens | `WS-016` `:806-846` · `WS-061` `:1449` · `WS-090` `:1614` · `WS-173` `:1859` · `WS-178`/`WS-179` `:1864-1865` · `WS-183` · `WS-194` `:1910` · `WS-208`/`WS-210`/`WS-211`/`WS-212` `:1982-1986` | `WS-016`: `branchName` → `registeredBranchName`; `gstin` read through the `REGISTERED` link; an eighth modal tab *Branches* (sub-grid: branch, role, from, to, primary) with *End link* and *Change registration*; filter `relationshipRoleCode` added to the `WAREHOUSE_WAREHOUSE` `COMMON_FILTER_CONFIGS` scope; export gains `registeredBranchName` + `linkedBranchNames`; mobile picker per §1.2.4 row 15 |
| `INDIA-LOCALISATION-PACK.md` | §3.4 rules 1–2 `:353-358` · `S3` `:1144` · `:420` · `:1228` | *"`branch_id NOT NULL`"* → *"exactly one `REGISTERED` link at every instant"*; the challan identity's `branch_id` is the `REGISTERED` branch at the challan date |
| `PLATFORM-DEPENDENCIES.md` | §1.1 `:45` · §2.2 `:143` · §2.3 `:150-181` | a site **references** branches and is not one; §2.3 item 3 restated per §1.2.5 |
| `COEXISTENCE.md` · `IMPLEMENTATION-PLAN.md` · `GAP-REGISTER.md` | `C5` `:199` · `P1-05` `:435` · `:282` `:585` `:1151` | *"one branch, one GSTIN"* → *"one `REGISTERED` branch at a time"*. `E-048` and `S-022` stay **closed** — the site is still bound to a branch that carries the GSTIN, now with history |
| **Tasks** | owner **`P1-05`** (`V500012`, `WS-016` + mobile) | the rows, the constraints, the validator hook, the screen |
| | **`P0-02`** (`V500030`) · **`P0-15`** (`V501000`, the verb, the three-mode predicate) · **`P1-18`** (the resolver, §1.2.5) | ledger guard · permission · scope |
| | `P1-09` · `P1-17` · `P2-02` · `P2-05` · `P2-08` · `P2-10` · `P2-12` · `P2-15` · `P2-18` · `P2-20` · `P2-21` · `P2-24` · `P2-25` · `P2-IN-01` · `P2-IN-03` · `P2-IN-04` · `P4-02` · `P4-03` · `P4-06` · `P4-10` · `P5-18` · `P6-10` | one rule each, from §1.2.4 |

---

## §1.3 · The junction convention every `RG-` proposal uses

1. **`effective_from TIMESTAMPTZ NOT NULL`, `effective_to TIMESTAMPTZ NULL`, half-open `[from, to)`.**
   Not `DATE`: movements carry `occurred_at` (`L-13`), and a resolver asking *"the link at this
   instant"* needs an instant. The UI captures a date. The service converts it to site-local midnight
   using `whb_warehouses.timezone` (`FR-439`).
2. **"One current X"** is a partial unique index on `effective_to IS NULL` (§1.7 of `DATA-MODEL.md`,
   the flag-swap shape). **"One X at every instant"** is an `EXCLUDE USING gist` over a `tstzrange`,
   and needs `btree_gist` — declared by the migration that uses it, because `D-7`'s standalone install
   has neither accounting-base nor assets to have created it.
3. **No `is_active` on a dated junction.** `effective_to` is the only end. Two end markers disagree,
   and §1.4 of `DATA-MODEL.md` already refuses the second deletion mechanism for that reason.
4. **Rows that classify posted history are append-only once a movement stands on them** (§1.2.2
   guard 3). Rows that only grant visibility or defaults are freely editable.
5. **Resolvers read the link at `occurred_at`; access reads the link at now.**
6. **Identity-bearing associations are the one exception to dating** (`RG-009`). A variant whose size
   changes is a different item, for the same reason `I-9` refuses a base-UoM change.

---

## §2 · The findings

### `RG-001` · The warehouse's branch is a mutable scalar, with two more scalars copying its tax identity — so registration history, the thing `IRR-57` exists to keep, is overwritten by the first change, and a site can serve no second branch — **BLOCKER**

- **What is missing or wrong:**
  - `whb_warehouses` carries `branch_id`, **and** `tax_registration_id`, **and** `legal_entity_id`
    (`DATA-MODEL.md:452`).
  - `FR-079` forbids the second: *"the GSTIN is read from the branch, never duplicated onto the
    warehouse"* (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:219`, restated `issues/p1-05.md:56-57`,
    `issues/p2in-01.md:154`).
  - `IRR-57` mandates it (`IRREVERSIBLE.md:247`), and the set never reconciles the two.
  - All three are single mutable values. A branch moving to a new GSTIN, a site re-registered under a
    different branch, or a central godown serving three showrooms — each is either unrepresentable or
    represented by overwriting the fact a filed return was computed from.
  - The reasons given for rejecting the junction were *"a warehouse under two tax registrations is not
    a thing"* (`FR-079`) and *"do not repeat accessories' junction"* (`IRREVERSIBLE.md:555`,
    `DATA-MODEL.md:3991`). They conflate **registered under** (one, at a time — true) with
    **associated with** (many — also true).
  - Accessories' junction did not fail for being M:N. It failed for having **no role and no dating**,
    and for `ON DELETE CASCADE` on both FKs, which deletes the history
    (`accessories/…/V30018__*.sql:10-13,21`).
- **Why it matters:** name the moment. **31 March, a dealer group moves its central godown from the
  Gurgaon registration to the Delhi one.** On 1 April the `whb_warehouses.branch_id` update succeeds.
  In September the auditor asks for the Rule 56 account of the Gurgaon GSTIN for Q4. `FR-314` wants
  it *"per registration and per period"*, and `issues/p4-03.md:110` says *"per registration … not per
  warehouse"*. The query that answers it joins movements to sites to **today's** branch, and files
  the godown's whole quarter under Delhi. `whb_stock_movements` cannot carry the branch instead,
  because `V500030` is `PNR-2` and a column added later is null on every existing row
  (`DATA-MODEL.md:2905`). Two reader-level consequences follow:
  1. The branch-scope guard has nothing to bind on. `PLATFORM-DEPENDENCIES.md`'s rule is keyed on a
     `branch_id` column that no warehouse ledger or document table has (`:179-181`, §1.2.5).
  2. The counter sale (`WS-194`) and the sister-branch run (`FR-254`) both assume a site belongs to
     exactly one branch, which a shared godown contradicts.
- **Negative evidence:**
  ```bash
  grep -n "tax_registration_id\|legal_entity_id" docs/DATA-MODEL.md | head -3          # :452 — on the warehouse
  grep -rn "tax_registration_id" docs/DESIGN-SET-DEFECTS.md docs/GAP-REGISTER*.md      # 0 — the contradiction is unlogged
  grep -rn "whb_warehouse_branches\|warehouse_branch" docs/DATA-MODEL.md               # only the §9.2 'dropped' row, :3991
  grep -rn "effective_from" docs/DATA-MODEL.md | grep -c "whb_warehouses"              # 0 — no dating anywhere on the site
  ```
- **Where it belongs:** `warehouse-base` · **v1** · **P1** (`V500012`, a `PNR-1` prerequisite, §7.7)
- **Disposition:** *fold into `P1-05` as owner, per §1.2 in full*, with one-rule amendments to the 25
  tasks listed in §1.2.7. The artefact list in §1.2.7 is the complete edit set.
- **Irreversibility:** **`UB` from the first registration change after go-live.** The rows are free
  until `V500012` ships. After `PNR-3`, *which branch was this site under on a past date* is an
  observation that was never recorded if the column was a scalar.
- **Relationship to rounds 1–3:** **new, and reverses three documents by user decision.** `E-048` and
  `S-022` (both BLOCKER, `GAP-REGISTER.md:282`, `:585`) stay closed — their requirement was a
  branch-bound GSTIN, which the `REGISTERED` link keeps. `RA-001` (warehouse grants) composes with
  §1.2.5 and is not restated.

### `RG-002` · One GSTIN profile has exactly one branch, but a registration covers every branch in its state — so the second branch in a state cannot resolve a GSTIN, and no scenario can see it because the cast has one branch per state — **BLOCKER**

- **What is missing or wrong:**
  - `whin_gstin_profiles` has `gstin` **unique** and a scalar `branch_id` (`DATA-MODEL.md:1189`,
    `issues/p2in-01.md:47`), drawn in the ER as *"one branch, one GSTIN (platform)"*
    (`DATA-MODEL.md:1997`).
  - A company holds one registration per state. Every other branch in that state is an additional
    place of business under it.
  - `branches.gst_number` is per branch (`platform/…/V182:7`), so two Delhi branches both hold
    `07AABCM1234F1Z5`. Only one of them can be the profile's `branch_id`.
- **Why it matters:** `RG-001` resolves site → `REGISTERED` branch → profile. A site registered to the
  second Delhi branch finds no profile. So no challan can be issued (`P2-IN-03`), no e-way bill
  generated (`P2-IN-04`), and under `A-4` the goods cannot legally move. Resolving by the
  `branches.gst_number` **string** instead (the `X-7` idiom, `DATA-MODEL.md:1532`) works today and
  fails at history: `gst_number` is a mutable platform scalar with no dates, so *"which branches did
  this registration cover in Q4"* — which the Rule 56 account needs to know which sites' movements
  belong to it — is lost the day a branch's number is edited.
- **Negative evidence:**
  ```bash
  sed -n '104,108p' docs/SCENARIO-CATALOGUE.md          # DEL-01 · MUM-01 · BLR-01 — one branch per state
  grep -rn -i "additional place" docs/*.md | grep -vi "client\|3pl" | wc -l            # 0 for OUR branches
  ```
- **Where it belongs:** `warehouse-india` · **v1** · **P2-IN** (`V540010`)
- **Disposition:** *fold into `P2-IN-01`.*
  - `whin_gstin_profile_branches`: `gstin_profile_id`, `branch_id ↓platform branches(id)`, `company_id`
    (denormalised from the profile by trigger), `place_role` (`PRINCIPAL`/`ADDITIONAL`), `effective_from`,
    `effective_to`.
  - Constraints: one current `PRINCIPAL` per profile (partial uk); `EXCLUDE (company_id =, branch_id =,
    range &&)`, so a branch is under one registration per company at a time.
  - `place_role` is a statute-closed set, so it takes a `CHECK` as a closed system vocabulary under
    `OD-5`'s ruling, not a `D-10` catalogue.
  - `whin_gstin_profiles.branch_id` is dropped; `gstin` stays unique.
  - A nightly assertion compares `branches.gst_number` for every linked branch with the profile's
    `gstin`, because platform can edit the number and warehouse cannot block it.
  - `WS-173` gains a *Places of business* sub-grid. The cast gains a second Delhi branch.
- **Irreversibility:** **`UB`** for the history half, from the first filed period.
- **Relationship to rounds 1–3:** **new.** `DESIGN-SET-DEFECTS.md:594` records the prior art's
  `scc_gstin_profiles` had no owning company; nobody examined the branch cardinality.

### `RG-003` · A counterparty has one tax id and one address, but its GSTIN depends on the ship-to state, and the v1 e-way bill and challan need the recipient's — **MAJOR**

- **What is missing or wrong:** `whb_counterparties` carries `national_tax_id`, one `gln` and a
  *"default address block"* (`DATA-MODEL.md:512`). `FR-119` excludes *"addresses beyond one
  default"* (`:517-522`, `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:279`). An Indian customer has one PAN
  and one GSTIN **per state**. `whin_eway_bills.shipment_id` is v1 (`DATA-MODEL.md:1200`) and
  `whin_delivery_challans.to_counterparty_id` is v1 (`:1198`), but neither records **which** of the
  recipient's registrations was used.
- **Why it matters:** a sale shipped to a customer's Pune depot is filed under its Maharashtra GSTIN.
  The next shipment, to its Chennai depot, needs the Tamil Nadu one. With one `national_tax_id` the
  operator types a GSTIN onto each document. What was filed is then unreconstructible from the
  master, which is `UB` for every filed e-way bill.
- **Negative evidence:** `grep -n "address" docs/DATA-MODEL.md | grep -c whb_counterparties` → 1 (the
  single default block).
- **Where it belongs:** `warehouse-base` · **v1** · **P1** (`V500011`)
- **Disposition:** *fold into `P1-08`; amend `P2-IN-03`/`P2-IN-04`.*
  - `whb_counterparty_addresses`: `counterparty_id`, `address_role` (`REGISTERED`/`BILL_TO`/
    `SHIP_TO`/`PICKUP`/`RETURN`), the structured block with `state_code`, `gln`, `is_primary` per
    role, and dates.
  - `whb_counterparty_tax_registrations`: `counterparty_id`, `country_code`, `registration_scheme`
    (an opaque string — `D-8`), `registration_number`, `state_code`, `address_id`, `is_primary` per
    country, and dates; `uk(registration_scheme, registration_number, effective_from)`.
  - `national_tax_id` stays as the **legal-entity** id (PAN).
  - The challan and the e-way bill freeze `to_counterparty_tax_registration_id` and
    `to_counterparty_address_id`.
  - **This reverses `FR-119` for addresses and tax registrations only.** Payment terms, credit,
    bank details, contacts and scorecard stay excluded.
- **Irreversibility:** **`UB`** per filed document once shipping starts.
- **Relationship to rounds 1–3:** **new.** `OD-4` owns *who* owns the party master, not its
  cardinality.

### `RG-004` · Location custody is one overwritable `assigned_user_id`, so who held the van's stock at last Tuesday's shortage is not recorded — **MAJOR**

- **What is missing or wrong:**
  - `whb_locations.assigned_user_id` (`DATA-MODEL.md:453`, `IRR-30`, `FR-088`) is a scalar.
  - The history lives in `whaf_van_stock_assignments` (`:1300`), which is **adapter-owned and v1.1**,
    so base cannot read it (`D-11`).
  - A van with a driver and a helper cannot be represented.
- **Why it matters:** a van reconciliation finds a shortage (`FR-088`: van stock is the same object as the vehicle's
  location). The custody
  liability belongs to whoever held the location **when the stock left**, and a reassigned scalar
  says only who holds it now.
- **Negative evidence:** `grep -n "assigned_from" docs/DATA-MODEL.md` → `:1300` only (adapter).
- **Where it belongs:** `warehouse-base` · **v1** · **P1** (`V500013`)
- **Disposition:** *fold into `P1-05`; amend `P3-20`.*
  - `whb_location_user_assignments`: `location_id`, `user_id ↓platform users(id)`, `assignment_role`
    (`CUSTODIAN`/`DRIVER`/`HELPER`), and dates.
  - One current `CUSTODIAN` per location; `EXCLUDE` on the `CUSTODIAN` range.
  - `assigned_user_id` is dropped; `B2` moves to the new table.
  - `whb_location_types.requires_assigned_user` means *requires a current `CUSTODIAN`*.
  - `whaf_van_stock_assignments` keeps the vehicle reference and FKs down to the base row.
- **Irreversibility:** `IRR-30` classes the column **`RK`** at `PNR-1` (`IRREVERSIBLE.md:205`). The
  custody history the scalar overwrites is **`UB`** from the first reassignment.
- **Relationship to rounds 1–3:** **new.**

### `RG-005` · An item has one category, and the category is the resolution key for costing, posting, allocation, negative stock and `D-9` — so a re-categorisation silently re-costs, and a second classification scheme is impossible — **MAJOR**

- **What is missing or wrong:**
  - `whb_items.category_id` is scalar (`DATA-MODEL.md:529`).
  - It keys six resolvers:
    - `whb_valuation_policies.category_id` (`:855`)
    - `whb_gl_posting_rules.item_category_id` (`:859`)
    - `whb_allocation_rules` and `whb_negative_stock_policies` (`:830-831`)
    - `D-9`'s `whb_category_stocking_ownership` (`:926`)
    - the category-level inspection default (`:528`)
  - Merchandising, regulatory and stocking classifications cannot coexist.
- **Why it matters:** moving an item from category FIFO to category AVCO by `UPDATE` changes, from
  that instant, the method the next layer consumption resolves. *"Which method costed this layer"*
  is then answerable only from the effective-dated policy **and** the item's category history, and
  the second half is not kept (`IRR-40`'s declared grain).
- **Where it belongs:** `warehouse-base` · **v1** · **P1** (`V500014`/`V500015`)
- **Disposition:** *fold into `P1-01`; amend `P0-17`, `P0-12`, `P2-07`, `P2-16`, `P1-04`,
  `P1-14`, `P2-04`, `P2-20`.*
  - `whb_item_category_assignments`: `item_id`, `category_id`, `scheme_root_category_id` (the root of
    the category's tree **is** the scheme — no new registry; denormalised by trigger), and dates.
  - One current row per `(item, scheme)`; `EXCLUDE` per `(item, scheme)`.
  - A seeded system root `STOCKING` is mandatory for stocked items, and **it is the only scheme any
    resolver reads**, at `occurred_at`.
  - `category_id` is dropped.
- **Irreversibility:** **`UB`** for costing history after the first re-categorisation.
- **Relationship to rounds 1–3:** **new.**

### `RG-006` · A lot has one counterparty, conflating supplier, manufacturer, packer and importer — the parties a Legal Metrology declaration and a recall name — **MAJOR**

- **What is missing or wrong:** `whb_lots.counterparty_id` (`DATA-MODEL.md:574`) sits beside
  `FR-320`'s pack-run declarations (`mrp`, `net_content`, `country_of_origin`). The same declaration
  names the manufacturer, packer or importer, and a recall is issued by the manufacturer — who is not
  the distributor we bought from. **`RE-VERIFY`** the exact party list against the Packaged
  Commodities rules before build, as `INDIA-LOCALISATION-PACK.md` does for every statutory claim.
- **Where it belongs:** `warehouse-base` · **v1** · **P1** (`V500018`)
- **Disposition:** *fold into `P1-07`; amend `P1-03`, `P4-05`.*
  - `whb_lot_counterparties`: `lot_id`, `counterparty_id`, `role_code → whb_counterparty_roles(code)`
    — registry 11 already exists; seed `MANUFACTURER`/`PACKER`/`IMPORTER` beside `SUPPLIER`.
  - `effective_from` defaults to the receipt date.
  - uk one current row per `(lot, role)`.
  - `counterparty_id` is dropped.
- **Irreversibility:** **`UB`** — `PNR-3`: lot attributes are observed at receipt (`IRR-53`).
- **Relationship to rounds 1–3:** **new.**

### `RG-007` · A serial has one secondary identifier, but a dual-SIM handset has two IMEIs and either may be scanned — **MAJOR**

- **What is missing or wrong:** `whb_serials.secondary_serial` (`DATA-MODEL.md:575`, *"IMEI-shaped
  items"*) is one column. A dual-SIM phone has IMEI 1 and IMEI 2; an eSIM device adds an EID; a
  network device has a MAC address.
- **Why it matters:** the returning unit is scanned by whichever IMEI the customer quotes. A second
  identifier not captured at receipt cannot be backfilled without re-scanning every unit.
- **Where it belongs:** `warehouse-base` · **v1** · **P1** (`V500018`)
- **Disposition:** *fold into `P1-07`; amend `P1-02`'s scan-resolution service.*
  - `whb_serial_identifiers`: `serial_id`, `identifier_type` (open string), `identifier_value`, and
    `owner_id` denormalised.
  - `uk(owner_id, identifier_type, identifier_value)` — **never global**, by `IRR-14`'s argument.
  - `secondary_serial` is dropped.
- **Irreversibility:** **`UB`** (`PNR-3`).
- **Relationship to rounds 1–3:** **new.**

### `RG-008` · The fixed pick face is stored twice, in two cardinalities — `whb_locations.fixed_item_id` (one item per location, v1) and `whb_item_location_settings.is_pick_face` (many, v1.1) — **MAJOR**

- **What is missing or wrong:** `fixed_item_id` (`DATA-MODEL.md:453`) is added by an `ALTER` in
  `V500016` (`:3120-3125`). `whb_item_location_settings` (`:538`) is the item × location junction,
  allocated at `V500061` (`:2930`, v1.1). A two-SKU shared pick face, or one item with faces in two
  zones, fits only the second. The putaway strategy `FIXED_LOCATION` (`:984`) reads the first.
- **Why it matters:** two truths about one fact, maintained by two screens a version apart. That is
  the drift `DATA-MODEL.md` refuses everywhere else (the `whb_lpn_contents` argument, `:581-587`).
- **Where it belongs:** `warehouse-base` · **v1** · **P1** (`V500016`)
- **Disposition:** *fold into `P1-02`; amend `P1-05`, `P1-15`, `P3-12`.* Drop `fixed_item_id` and its
  `ALTER`. Move `whb_item_location_settings` DDL into `V500016`, adding `is_fixed` and dates.
  `V500061` becomes a hole (§7.1 rule 2).
- **Irreversibility:** reversible today; a data merge after go-live.
- **Relationship to rounds 1–3:** **new.**

### `RG-009` · The variant model is three fixed slots, on the one schema `A-3` calls unrecoverable — a fourth axis, or a style whose axis order differs, has nowhere to go — **MAJOR**

- **What is missing or wrong:** `whb_items.variant_axis_1/2/3_value_id` (`DATA-MODEL.md:529`).
  `DESIGN-SET-DEFECTS.md:216-217` records the triple as the *fix*. Nothing ties slot 1 to one axis,
  so `SIZE` may sit in slot 1 on one style and slot 2 on another, and every matrix query must search
  all three. Apparel routinely carries size × colour × fit × length.
- **Why it matters:** `A-3` accepts the variant model as v1 schema **because a flat model is
  unrecoverable**. The same argument applies to a capped one.
- **Where it belongs:** `warehouse-base` · **v1** · **P1** (`V500014`/`V500015`)
- **Disposition:** *fold into `P1-01`; amend `P5-20`.*
  - `whb_style_variant_axes`: `style_item_id`, `axis_id`, `sequence`; uk on both pairs.
  - `whb_item_variant_values`: `item_id`, `axis_id`, `axis_value_id`; `uk(item_id, axis_id)`.
  - The service asserts a variant's axis set equals its style's.
  - **Deliberately not dated** (§1.3 rule 6).
- **Irreversibility:** **`RK`** — a re-key of every variant row after go-live.
- **Relationship to rounds 1–3:** **new**; `A-3` is the premise, not the finding.

### `RG-010` · Purchase and sale UoM are item scalars, but both are supplier- and channel-specific — **MINOR**

- **What is missing or wrong:** `whb_items.purchase_uom_code`, `.sale_uom_code` (`DATA-MODEL.md:529`).
  Supplier-specific packs already exist as rows (`whb_item_packaging_levels.counterparty_id`, `:533`);
  the default purchase unit does not follow them.
- **Where it belongs:** `warehouse-base` · **v2** — defaults only; every line freezes `uom_code` and
  `conversion_factor_used` (`L-7`), so no history is lost.
- **Disposition:** *`P1-01`/`P1-02` at v2.* `whb_item_uom_defaults` (`item_id`, `uom_role`
  `PURCHASE`/`SALE`/`ISSUE`/`COUNT`, `uom_code`, nullable `counterparty_id`/`channel_id`/
  `warehouse_id`, dates; one current per scope `NULLS NOT DISTINCT`).
- **Irreversibility:** reversible.
- **Relationship to rounds 1–3:** new.

### `RG-011` · The item–supplier junction is right and undated — re-sourcing overwrites lead time and MOQ history, and "preferred" cannot differ by site — **MINOR**

- **What is missing or wrong:** `whb_item_supplier_sources` `uk(item_id, counterparty_id)`, one
  preferred per item (`DATA-MODEL.md:539`). A Delhi site preferring one distributor and a Mumbai site
  another cannot both be true.
- **Where it belongs:** `warehouse-base` · **v2** (reversible)
- **Disposition:** *`P1-03` at v2.* Add dates and a nullable `warehouse_id`; uk
  `(item_id, counterparty_id, warehouse_id, effective_from)` `NULLS NOT DISTINCT`; one current
  preferred per `(item, warehouse)`. **KEEP-JUNCTION.**
- **Irreversibility:** reversible.
- **Relationship to rounds 1–3:** new.

### `RG-012` · A site has one company, and nothing asserts a movement's company matches it — **MINOR**

- **What is missing or wrong:** `whb_warehouses.company_id` (`DATA-MODEL.md:452`).
  `DATA-MODEL.md:728-734` admits the header's `company_id` is *"a third copy of a fact … that nothing
  keeps in agreement"*. A group godown shared by two legal entities — each holding its own stock,
  already separable because `company_id` is in `L-5` — is refused by nothing and permitted by
  nothing.
- **Where it belongs:** `warehouse-base` · **v2** (`RK` — the ledger carries `company_id` itself)
- **Disposition:** *`P1-05` + `P0-02` at v2.* `whb_warehouse_companies` (role `OPERATOR`/
  `STOCK_HOLDER`, dates, one current `OPERATOR`). The writer asserts the movement's company holds a
  `STOCK_HOLDER` link at `occurred_at`. **In v1**, add that assertion against the scalar — it is free.
- **Irreversibility:** reversible.
- **Relationship to rounds 1–3:** new.

### `RG-013` · An owner has one company, and "one house owner per company" rides on it — **MINOR**

- **What is missing or wrong:** `whb_owners.company_id` (`DATA-MODEL.md:499`). A 3PL group with two
  legal entities serving one client cannot represent it.
- **Where it belongs:** `warehouse-base` · **v2** (`RK`; `L-5` carries both members independently)
- **Disposition:** *`P0-06` + `P5-01` at v2.* `whb_owner_companies` (role `HOUSE`/`SERVICED_BY`,
  dates). The one-house-per-company partial index moves to it.
- **Irreversibility:** reversible.
- **Relationship to rounds 1–3:** new.

### `RG-014` · A location is dedicated to one owner — a client group's shared cage cannot be declared — **MINOR**

- **What is missing or wrong:** `whb_locations.dedicated_owner_id` (`DATA-MODEL.md:453`), read by
  `commingle_policy = SINGLE_OWNER`.
- **Where it belongs:** `warehouse-base` · **v2**
- **Disposition:** *`P1-05` schema, consumed by P5.* `whb_location_owner_dedications` (dates),
  plus a commingle policy `OWNER_SET` evaluated by the port (`FR-087`).
- **Irreversibility:** reversible.
- **Relationship to rounds 1–3:** new.

### `RG-015` · Functional zones are forced into the physical tree — a bin is in exactly one zone, so a pick zone that crosses two aisles' storage zones cannot exist — **MINOR**

- **What is missing or wrong:** zones are `whb_locations` rows under `parent_location_id`
  (`DATA-MODEL.md:470-479`), correctly, for **containment**. Pick zones, labour zones and count
  zones cut across it.
- **Where it belongs:** `warehouse-base` · **v1.1** (zone picking, `FR-187`'s wave family; `P3-06`
  holds the wave DDL)
- **Disposition:** `whb_location_zone_memberships` (`location_id`, `zone_location_id`, `zone_role`,
  dates). **`parent_location_id` stays** (`RG-025`).
- **Irreversibility:** reversible.
- **Relationship to rounds 1–3:** new.

### `RG-016` · A carrier account is scoped to one nullable owner and to no warehouse, though carrier pickup locations are per site; and nothing makes a carrier 1:1 with its party — **MINOR**

- **What is missing or wrong:** `wh_carrier_accounts.owner_id` and the default per carrier + owner
  (`DATA-MODEL.md:1035`); no warehouse column. `wh_carriers.counterparty_id` (`:1033`) has no uk, so
  two carrier rows can claim one party.
- **Where it belongs:** `warehouse` · **v2** for the junction · **v1** for the uk
- **Disposition:** *`P2-10`.*
  - Add `uk(counterparty_id)` on `wh_carriers` now (**KEEP-SCALAR** — a 1:1 extension, like `T1`).
  - At v2, `wh_carrier_account_scopes` (`carrier_account_id`, nullable `owner_id`/`warehouse_id`,
    `pickup_location_code`, `is_default`, dates; one default per carrier × owner × warehouse).
    Consumed by the v2 carrier tasks at `V510204`/`V510205`.
- **Irreversibility:** reversible.
- **Relationship to rounds 1–3:** new; `IRR-59` (the nullable owner) is kept.

### `RG-017` · Five v2 tables not yet built are specified with scalar associations — build them junction-shaped and the retrofit costs nothing — **MINOR**

- **What is missing or wrong:**
  - `wh_channel_accounts.warehouse_id` (`DATA-MODEL.md:1058`) — a marketplace account fulfils from
    several sites.
  - `wh_working_calendars.(warehouse_id, owner_id)` (`:1062`).
  - `wh3_clients.counterparty_id` (`:1149`) — bill-to, consignor and importer are different parties
    of one client.
  - `wh3_rate_cards.client_id` (`:1154`) — a negotiated card shared across a client group.
  - `wh3_sla_definitions.client_id` (`:1164`).
- **Where it belongs:** `warehouse` / `warehouse-3pl` · **at build (v2)**
- **Disposition:** *fold into `P5-09`, `P5-10`, `P5-01`, `P5-02`, `P5-07`.*
  - `wh_channel_account_warehouses` (priority, role `FULFIL`/`RETURNS`).
  - `wh_working_calendar_assignments`.
  - `wh3_client_counterparties` (role).
  - `wh3_rate_card_clients` — the "one `ACTIVE` card per client" guard moves here as an `EXCLUDE`.
  - `wh3_sla_definition_clients`.
- **Irreversibility:** none, if done at build.
- **Relationship to rounds 1–3:** new.

### `RG-018` · Configuration scopes are single scalars, and two lists are stored in one column — **MINOR**

- **What is missing or wrong:**
  - `whb_outbox_subscriptions.owner_filter_id` (`DATA-MODEL.md:880`, `P0-11`) — a subscriber
    filtered to a set of owners.
  - `wh_print_templates.(owner_id, warehouse_id)` (`:1036`, `P2-14`) — one layout for a client group.
  - `whb_devices.(warehouse_id, assigned_to)` (`:909`, `P3-03`) — floater devices, shift hand-over.
  - `wh_count_programs.warehouse_id` (`:1007`, `P2-04`) — a programme across sites.
  - `whb_item_categories.default_inspection_plan_id` (`:528`) and
    `whb_item_supplier_sources.inspection_strategy` (`:539`) — the plan per item × supplier × site
    has no home (`P1-14`).
  - **Lists in one column:** `whin_compliance_registrations.document_kinds` (`:1190`, `P2-IN-01`)
    and `whb_api_clients.allowed_endpoints` (`:882`, `P5-22`) — CLAUDE.md's no-JSONB rule forbids
    the shape these will take.
- **Where it belongs:** as named · **v2**; `whb_devices` and `whb_api_clients` **at build**;
  `document_kinds` **at build, v1**.
- **Disposition:**
  - `whb_outbox_subscription_owners`.
  - `wh_print_template_scopes`.
  - `whb_device_assignments` (dates).
  - A `WAREHOUSE` scope type on the existing `wh_count_program_scopes`.
  - `wh_inspection_plan_assignments` — most-specific-first, the `whb_allocation_rules` shape.
  - `whin_compliance_registration_document_kinds`.
  - `whb_api_client_endpoints` + `whb_api_client_companies`.
- **Irreversibility:** reversible.
- **Relationship to rounds 1–3:** new.

### `RG-019` · Four document headers carry a single parent document that their lines already associate many-to-one — so a consolidated GRN, a multi-GRN freight bill and a two-shipment return contradict their own header — **MINOR**

- **What is missing or wrong:**
  - `wh_goods_receipts.po_id` beside `wh_goods_receipt_lines.po_line_id` (`DATA-MODEL.md:974-975`).
  - `wh_landed_cost_documents.grn_id` beside `wh_landed_cost_allocations.grn_line_id` (`:1106-1107`).
  - `wh_return_receipts.(rma_id, original_shipment_id, original_demand_order_id)` (`:1072`).
  - `wh_supplier_returns.(origin_grn_id, origin_lot_id)` (`:988`).
- **Where it belongs:** `warehouse` · **v1** (free before `V510014`)
- **Disposition:** *`P1-13`, `P2-17`, `P2-12`, `P2-13`.* The header column becomes nullable and
  **derived** ("the only PO, when there is one"), or is dropped. The line is the association.
  `idx(po_id)`'s query ("GRNs of PO X") goes through lines.
- **Irreversibility:** reversible now.
- **Relationship to rounds 1–3:** new.

### `RG-020` · Jurisdictional codes are single-valued on country-neutral masters, and one of them is India's name in `warehouse-base` — **MINOR**

- **What is missing or wrong:**
  - `whb_items.tax_classification_code` (`DATA-MODEL.md:529`) — one HSN. An item traded in two
    jurisdictions has two codes.
  - `whb_uoms.gst_uqc_code` (`:564`) — a GST name on a base table, which `D-8` forbids in kind.
  - `unece_rec20_code` beside it — one scheme per column.
  - `gln` on the counterparty (`:512`) — a party has a GLN per location (`RG-003`).
- **Where it belongs:** `warehouse-base` · **v2** — the line snapshots `hsn_code` (`IRR-42`), so
  history survives.
- **Disposition:** *`P1-01`, `P1-02` at v2.*
  - `whb_item_tax_classifications` (`country_code`, `scheme`, `code`, dates).
  - `whb_uom_scheme_codes` (`uom_code`, `scheme`, `code`) — `GST_UQC` and `UNECE_REC20` become rows.
  - The counterparty `gln` moves onto `RG-003`'s address rows.
- **Irreversibility:** `RK` per `IRR-44`, but not `UB`.
- **Relationship to rounds 1–3:** new, adjacent to `IRR-44`.

### `RG-021` · The junctions that exist use three vocabularies for their dates, and none prevents overlapping ranges — **MINOR**

- **What is missing or wrong:**
  - `whb_counterparty_role_links` uses `valid_from`/`valid_to` (`DATA-MODEL.md:513`).
  - `whaf_van_stock_assignments` uses `assigned_from`/`assigned_to` (`:1300`).
  - `whb_owner_grants`, `wh3_client_gst_registrations`, `whb_valuation_policies` and
    `whb_category_stocking_ownership` use `effective_from`/`effective_to` (`:500`, `:1167`, `:855`,
    `:926`).
  - Every one is keyed `uk(…, effective_from)`. That refuses two rows starting at one instant and
    admits two rows **overlapping** — two valuation methods for one category and site, or two
    stocking systems for one category (`D-9`'s *"exactly one"*).
- **Where it belongs:** as named · **v1** (free before first row)
- **Disposition:** *`P1-08`, `P0-06`, `P0-17`, `P1-04`; `P3-20` and `P4-10` at build.* Adopt §1.3;
  add the `EXCLUDE`. **KEEP-JUNCTION** in every case.
- **Irreversibility:** reversible now; overlap cleanup after.
- **Relationship to rounds 1–3:** new.

### `RG-022` · KEEP-SCALAR, redefine: `whb_lpns.owner_id` is `NOT NULL` beside `is_mixed_owner` — a mixed-owner pallet has an owner column that cannot be its owner — **MINOR**

- **What is missing or wrong:** `whb_lpns` (`DATA-MODEL.md:576`); `IRR-06` lists LPNs among the
  owner-bearing tables (`IRREVERSIBLE.md:162`). An LPN's contents are its positions, and each
  position carries its own owner (`L-5`). A junction would be a second truth about the same fact —
  the `whb_lpn_contents` argument, `DATA-MODEL.md:581-587`.
- **Where it belongs:** `warehouse-base` · **v1**
- **Disposition:** *`P1-07`.* Keep the column, and define it as **the custodian/label owner**. For an
  `is_mixed_owner` pallet it is the house owner. Owner reporting reads positions, never this column.
- **Irreversibility:** —
- **Relationship to rounds 1–3:** new.

### `RG-023` · KEEP-SCALAR: item, lot and serial ownership are identity, and M:N would break `I-19` — **MINOR**

- **What is missing or wrong:** nothing. **The finding is the prohibition.**
  - `uk(owner_id, sku)`, `uk(owner_id, item_id, lot_code)` and `uk(owner_id, item_id,
    serial_number)` (`DATA-MODEL.md:2804-2805`, `:574`) make owner a member of the identity.
  - An item shared by two owners is **two items** plus external refs, never one item with two
    owners. Otherwise one `item_id` resolves to two identity keys, and `L-5`'s owner member on the
    line no longer determines whose SKU namespace it is.
- **Where it belongs:** `warehouse-base` · v1 · `P1-01`, `P1-07` — no change
- **Disposition:** one sentence in each task's trap list.
- **Irreversibility:** `PNR-4`.
- **Relationship to rounds 1–3:** confirms `IRR-19`/`IRR-14`.

### `RG-024` · KEEP-SCALAR: the base UoM — M:N would break `L-7`, `I-8` and `I-9` — **MINOR**

- **What is missing or wrong:** nothing. `L-1` sums `base_quantity` in **one** base UoM per item;
  `I-9` makes it immutable once stock exists (`DATA-MODEL.md:2631-2647`). Every other UoM is already
  M:N through conversions (`:534`), and `RG-010` makes the defaults so.
- **Where it belongs:** `P1-01`, `P0-02` — no change
- **Disposition:** state it in `P1-01`.
- **Irreversibility:** `PNR-1`.
- **Relationship to rounds 1–3:** confirms.

### `RG-025` · KEEP-SCALAR: physical containment — a location in two warehouses would break `I-4` and `IRR-17` — **MINOR**

- **What is missing or wrong:** nothing.
  - `sequence_no` is gapless **per warehouse** (`I-4`, `DATA-MODEL.md:2332`).
  - `whb_stock_positions.warehouse_id` is denormalised from the location (`:755`).
  - A movement header names one warehouse (`IRR-17`).
  - A location with two warehouses makes each of these ambiguous.
  - `parent_location_id` is containment. Cross-cutting zones are `RG-015`, a separate junction.
- **Where it belongs:** `P1-05`, `P0-02` — no change
- **Disposition:** state it in `P1-05`.
- **Irreversibility:** `PNR-1`.
- **Relationship to rounds 1–3:** confirms.

### `RG-026` · KEEP-SCALAR: stock-period scope — an M:N period scope would break `L-8`'s one-period resolution — **MINOR**

- **What is missing or wrong:** nothing.
  - `whb_stock_movements.period_id` is `NOT NULL` and single (`DATA-MODEL.md:618`).
  - `I-10` reads one period row (`:2656-2681`).
  - Periods scoped `(company, warehouse | all)` (`:821`) resolve to exactly one.
  - A period↔site junction admits two open periods covering one site and date. PostgreSQL cannot
    exclude that across a junction and a parent without a trigger over both. **Do not scope periods
    by branch through `RG-001`'s junction either.**
- **Where it belongs:** `P0-07` — no change
- **Disposition:** state it in `P0-07`.
- **Irreversibility:** —
- **Relationship to rounds 1–3:** confirms.

### `RG-027` · KEEP-SCALAR: branch or registration must never join the ledger line or the `L-5` key, and a serial's `current_*` columns are caches — **MINOR**

- **What is missing or wrong:** nothing, and there are two temptations.
  - **First:** a reader of `RG-001` will propose a `branch_id` or `gstin` on `whb_stock_movement_lines`
    or in the position key. It is refused for three reasons. It is a tenth key member, which `OD-10`
    refused for MRP. It is post-`PNR-2` dead on arrival (`DATA-MODEL.md:2485-2488`). And it is
    derivable exactly from the dated link at `occurred_at`, which is what §1.2.4 row 9 does.
  - **Second:** `whb_serials.current_location_id`/`current_lpn_id`/`current_status_code`/
    `sold_to_counterparty_id` (`:575`) are projections of the last movement (`L-4`). A unit is in
    exactly one position (`L-5`, `I-1` per serial), so M:N contradicts the ledger it caches.
- **Where it belongs:** `P0-02`, `P1-07` — no change
- **Disposition:** state it in `P0-02`'s trap list.
- **Irreversibility:** `PNR-2`.
- **Relationship to rounds 1–3:** confirms `OD-10`'s reasoning.

---

## §3 · What I checked and found sound

| What I went looking for | Where it is covered |
|---|---|
| **Junctions that exist and should stay** | `whb_counterparty_role_links` (`:513`, `FR-117` — the precedent this decision generalises) · `whb_owner_grants` (`:500`) · `whb_item_supplier_sources` (`:539`, amended by `RG-011`) · `whb_item_site_settings` (`:537`) · `whb_item_supersessions` (dated, `:540`) · `whb_item_documents` (`:541`) · `wh_shipment_orders` (*"the cardinality is a one-way door"*, `:1032`) · `wh_wave_orders` · `wh_manifest_shipments` · `wh_receiving_session_documents` · `wh_three_way_match_allocations` · `wh3_client_gst_registrations` (`:1167`) · `whad_vehicle_fitments` (`:1271`) |
| **Scoped child rows that are already the association** | `whb_item_identifiers.(counterparty_id, channel_id)` and `whb_item_packaging_levels.counterparty_id` — each row *is* item × party, with the party in the unique key (`:532-533`) |
| **The external-ref tables are M:1 by design, and must stay so** | `uk(source_module, external_id)` — *"map, not mirror"* (`G12`, `:1510`). One external identity resolving to two warehouse rows would defeat `D-9`'s detectability, the only reason those tables are mandatory |
| **1:1 extensions that are not associations** | `wh3_clients.owner_id` `uk` (`T1`, `:1450`) · `whb_owners.counterparty_id` (M:1: one party may be two owners for brand segregation) · the four `wh_*_tasks` 1:1 over `whb_tasks` (`W3`) |
| **Cardinality already right** | barcodes (`whb_item_identifiers`, many per item) · per-item UoM conversions · one timezone per site (`FR-439`; a site is in one place) · holds (*"two holds at once is the normal case"*, `:1006`) · multi-counter count zones (`:1010`) · carrier services (`:1034`) · one MRP per lot (`OD-10`) |
| **The ledger carve-out** | movement header and lines, positions, reservations (holder quad), cost layers and consumptions, handovers, outbox — every one a fact or a cache, and every one scalar, which the decision confirms |

---

## §4 · Refused

1. **"Users need an M:N link to warehouses."** → **`RA-001`** (R16, BLOCKER) proposed
   `whb_warehouse_grants`, dated. It composes with §1.2.5 rule 5 and is not re-filed.
2. **"Price lists need a warehouse or branch association."** → **`RA-002`**, which found there is no
   price table at all. If `whad_price_levels` is built, its branch/site scope is a junction at build
   (`RG-017`'s rule). Not re-filed.
3. **"Counterparties need contacts, payment terms and bank details as lists."** → `FR-119`, a scope
   decision about **commercial** data, not an association between masters. `RG-003` reverses only the
   two things a tax document needs.
4. **"A warehouse site should be a platform branch (`C-016`)."** Unnecessary under the junction and
   harmless: a site may be `REGISTERED` to a `WAREHOUSE`-type branch or to a showroom. Recorded so
   `PLATFORM-DEPENDENCIES.md:45` is amended rather than contradicted.
5. **"`wh_consignments` should be M:N to shipments."** → `FR-193` decided 1:1-optional, and the v2
   consolidated e-way bill (`:1211-1212`) is the multi-shipment object. Not re-opened.
6. **"Tasks should be multi-assignee."** Tasks are documents (§1.4's no-`is_active` class). The
   multi-counter case is `wh_count_zone_assignments`.
7. **"The transit warehouse has no clear registration."** → **`RE-002`** owns the transit site's
   seeding. §1.2.3 adds only the classification rule.

---

## §5 · Counts

```bash
cd warehouse-issues/docs/reviews
grep -cE '^### `RG-[0-9]{3}`' R22-cardinality-and-junctions.md                          # 27
grep -E '^### `RG-' R22-cardinality-and-junctions.md \
  | grep -oE '\*\*(BLOCKER|MAJOR|MINOR)\*\*$' | sort | uniq -c
#   2 **BLOCKER**
#   7 **MAJOR**
#  18 **MINOR**
grep -cE '^### `RG-[0-9]{3}` · KEEP-SCALAR' R22-cardinality-and-junctions.md             # 6
```

| Severity | Count | Findings |
|---|---|---|
| **BLOCKER** | 2 | `RG-001` `RG-002` |
| **MAJOR** | 7 | `RG-003` `RG-004` `RG-005` `RG-006` `RG-007` `RG-008` `RG-009` |
| **MINOR** | 18 | `RG-010`…`RG-021` · KEEP-SCALAR `RG-022`…`RG-027` |
| **Total** | **27** | |

**The register, one row per finding:**

| ID | Sev | Class | Current | Proposal | Ver | Owning task | Affected |
|---|---|---|---|---|---|---|---|
| `RG-001` | BLOCKER | association | `whb_warehouses.branch_id` + 2 copies | `whb_warehouse_branches` + `whb_warehouse_branch_roles` | **v1** | `P1-05` | `P0-02` `P0-15` `P1-18` + 22 (§1.2.7) |
| `RG-002` | BLOCKER | association | `whin_gstin_profiles.branch_id` | `whin_gstin_profile_branches` | **v1** | `P2-IN-01` | `P2-IN-03` `P2-IN-04` `P4-02` `P4-03` `P4-10` |
| `RG-003` | MAJOR | cardinality | one tax id, one address | `whb_counterparty_tax_registrations`, `whb_counterparty_addresses` | **v1** | `P1-08` | `P2-IN-03` `P2-IN-04` |
| `RG-004` | MAJOR | association | `whb_locations.assigned_user_id` | `whb_location_user_assignments` | **v1** | `P1-05` | `P3-20` |
| `RG-005` | MAJOR | association | `whb_items.category_id` | `whb_item_category_assignments` | **v1** | `P1-01` | `P0-12` `P0-17` `P1-04` `P1-14` `P2-04` `P2-07` `P2-16` `P2-20` |
| `RG-006` | MAJOR | association | `whb_lots.counterparty_id` | `whb_lot_counterparties` | **v1** | `P1-07` | `P1-03` `P4-05` |
| `RG-007` | MAJOR | cardinality | `whb_serials.secondary_serial` | `whb_serial_identifiers` | **v1** | `P1-07` | `P1-02` |
| `RG-008` | MAJOR | two truths | `whb_locations.fixed_item_id` | `whb_item_location_settings` moved to `V500016` | **v1** | `P1-02` | `P1-05` `P1-15` `P3-12` |
| `RG-009` | MAJOR | cardinality | three variant slots | `whb_item_variant_values`, `whb_style_variant_axes` | **v1** | `P1-01` | `P5-20` |
| `RG-010` | MINOR | association | purchase/sale UoM | `whb_item_uom_defaults` | v2 | `P1-01` | `P1-02` |
| `RG-011` | MINOR | amend junction | undated supplier sources | dates + site scope | v2 | `P1-03` | — |
| `RG-012` | MINOR | association | `whb_warehouses.company_id` | `whb_warehouse_companies` | v2 | `P1-05` | `P0-02` `P0-07` |
| `RG-013` | MINOR | association | `whb_owners.company_id` | `whb_owner_companies` | v2 | `P0-06` | `P5-01` |
| `RG-014` | MINOR | association | `dedicated_owner_id` | `whb_location_owner_dedications` | v2 | `P1-05` | P5 |
| `RG-015` | MINOR | missing association | zone = parent only | `whb_location_zone_memberships` | v1.1 | `P3-06` | `P1-05` |
| `RG-016` | MINOR | association | carrier account owner, no site | `wh_carrier_account_scopes`; `uk` on `wh_carriers` | v2 / v1 | `P2-10` | v2 carrier tasks |
| `RG-017` | MINOR | association | five v2 scalars | five junctions at build | v2 | `P5-01` | `P5-02` `P5-07` `P5-09` `P5-10` |
| `RG-018` | MINOR | config scope + lists | seven scalars/lists | seven child tables | v2 / at build | `P0-11` | `P1-14` `P2-04` `P2-14` `P2-IN-01` `P3-03` `P5-22` |
| `RG-019` | MINOR | document headers | four header scalars | derive or drop | v1 | `P1-13` | `P2-12` `P2-13` `P2-17` |
| `RG-020` | MINOR | cardinality | HSN, UQC, GLN single | scheme-coded children | v2 | `P1-01` | `P1-02` `P1-08` |
| `RG-021` | MINOR | convention | three date vocabularies, no overlap guard | §1.3 + `EXCLUDE` | v1 | `P1-08` | `P0-06` `P0-17` `P1-04` `P3-20` `P4-10` |
| `RG-022` | MINOR | KEEP-SCALAR | `whb_lpns.owner_id` | redefine as custodian owner | v1 | `P1-07` | — |
| `RG-023` | MINOR | KEEP-SCALAR | item/lot/serial owner | — (`I-19`) | — | `P1-01` | `P1-07` |
| `RG-024` | MINOR | KEEP-SCALAR | base UoM | — (`L-7` `I-9`) | — | `P1-01` | `P0-02` |
| `RG-025` | MINOR | KEEP-SCALAR | location containment | — (`I-4`) | — | `P1-05` | `P0-02` |
| `RG-026` | MINOR | KEEP-SCALAR | period scope | — (`L-8`) | — | `P0-07` | — |
| `RG-027` | MINOR | KEEP-SCALAR | no branch on the line; serial caches | — (`L-5` `L-4`) | — | `P0-02` | `P1-07` |

**Junctions proposed:** **v1 — 12 tables** (`whb_warehouse_branches`, `whb_warehouse_branch_roles`,
`whin_gstin_profile_branches`, `whb_counterparty_tax_registrations`, `whb_counterparty_addresses`,
`whb_location_user_assignments`, `whb_item_category_assignments`, `whb_lot_counterparties`,
`whb_serial_identifiers`, `whb_item_variant_values`, `whb_style_variant_axes`, and
`whb_item_location_settings` moved forward) · **v1.1 — 2** (`whb_location_zone_memberships`,
`whb_device_assignments` at build) · **v2 — 17** (`RG-010`–`RG-014`, `RG-016`–`RG-018`, `RG-020`).
**Every v1 table rides an existing task's existing migration; no number is invented.**

**Owed, and not made here per the brief (edit no other file):**
- `DECISIONS.md` §6 needs an `RG-` register row, and a `D-` row recording the user decision.
- `tools/check-design-set.py`'s `FINDING_CITE_RE` is `R[A-F]` (`:200`), so **every `RG-` citation is
  invisible to check 7** until `REVIEWS`, `FINDING_DEF_RE`, `REVIEW_LABEL` and `AUTHORITY_STEM` gain
  `RG` — the same obligation round 3 recorded for `RA`–`RF`.
- A round-4 gap register dispositions all 27.
