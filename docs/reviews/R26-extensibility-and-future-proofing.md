# R26 — extensibility and future-proofing

**Date** 2026-09-10 · **Prefix** `RL-` · **Branch** `docs/round-4-cardinality-and-gaps`

**Scope boundary.** This lens asks one question of every design choice: *what does the next vertical,
jurisdiction, channel, customer or version have to change, and can it change it without a commit to
`warehouse-base`?* It explicitly does **not** cover scalar-vs-M:N association choices; those belong to
the sibling lens R22. Where a candidate was a cardinality defect, it is refused in §4 and handed over.

**File set read — 19 files.**

```bash
cd /private/tmp/claude-501/-Users-bbhushan-work-git2-workspace-classic/caed8239-abcc-4985-bfe7-ea4688ad865e/scratchpad/warehouse-issues
# docs/ (11): README · DECISIONS · IRREVERSIBLE · DATA-MODEL (§1, §2.1–2.2, §3.3–3.5, §6.4 I-18..I-20, §7.2)
#             PORT-AND-ADAPTER-CONTRACT (§2.3–2.6, §4, §7, §8, §10) · MODULE-INTEGRATION (§8–10, §15–16)
#             GAP-REGISTER-R3 (§2 all 52 rows) · GAP-REGISTER (G-038, T-094 rows) · PLATFORM-DEPENDENCIES:500-512
#             OPEN-DECISIONS-RESOLVED:680-686 · WAREHOUSE-FUNCTIONAL-REQUIREMENTS (rows cited below)
# docs/reviews/ (4): R16 (the shape) · R12 Z-004..Z-007 · R19 RD-002 · R20/R11/R13 headings
# issues/ (5): p0-02 p0-11 p1-02 p2-07 p3-18 (headers + cited lines)
# classic, read-only (4): platform V149/V160 (branches) · accounting-base V600002 · mobile/src/schemas/common.schemas.ts
grep -rohE "\bRL-[0-9]{1,3}\b" docs/ issues/ tools/ | wc -l      # → 0   (the prefix was free)
```

**Method, in three sentences.** I took the twenty-three extensibility axes the brief names (open
vocabularies, status ladders, polymorphic columns, generic references, effective dating, deletion,
rule versioning, currency/UoM/timezone/language, country-neutrality, port leakage, events, API
versions, custom attributes, partitioning, meaning-bearing identifiers, global namespaces,
multi-company, offline sync, feature toggles, plug-in points, test seams). For each I named the
**next concrete consumer** who will need to extend it: `warehouse-adapter-services` in v1, a second
3PL client in v2, a second jurisdiction, the v3 `logistics` module, a customer's second install
under `OD-3`. Then I asked whether that consumer can do it with a seed `INSERT` in its own band, or
whether it needs an `ALTER`, a base release, a relabel or a restatement. Every absence prints the
command that established it; every candidate an earlier round already owns is refused in §4 and not
re-filed.

---

## §1 · Verdict

**The set is future-proofed exactly where it looked, and leaks where it did not.** `D-10`,
`IRREVERSIBLE.md` and the port contract are the most deliberate extensibility design I have seen in
this monorepo. Fourteen registries, the no-`CHECK` rule, the coupling test, the fixture adapter,
additive-only wire evolution, path versioning and the external-ref tables all work. So the findings
below are nearly all about the **edge of that design**: vocabularies, keys and contracts that sit one
step outside the fourteen named registries and so receive none of their protection.

**Two are one-way doors that close inside `P0`.**

1. **`duty_status` sits in the position key, in `L-1`'s conservation grain and on every cost layer,
   and it is the one vocabulary on the ledger with no registry** (`RL-001`). It is a bare
   `VARCHAR(30) DEFAULT 'DOMESTIC'` with no `REFERENCES`. `IRR-12` fills it with Indian customs
   regimes (`MOOWR`, `SEZ`, `FTWZ`), and `I-18`'s fourteen-pair enumeration does not include it.
   So `warehouse-india` cannot add a regime without a base release, a second jurisdiction cannot use
   the column without Indian vocabulary in its core, and a typo creates a new balance bucket that
   `L-1` then treats as a separate grain. Free in `V500005`/`V500030`; after `PNR-1` it is a type and
   FK change on a partitioned, append-only ledger.
2. **The migration authority and the port contract describe two different outboxes** (`RL-002`).
   `PORT-AND-ADAPTER-CONTRACT.md` `PC-38`/`FR-331` put `event_version`, `company_id`, `lot_id`,
   `lpn_id` and the three timestamps on every event from day one, and say in so many words that
   *"adding a dimension to an existing code is not [cheap]"*. The `DATA-MODEL.md` row for
   `whb_outbox` has none of them, has a `payload TEXT` that `PC-37` forbids, and `P0-11` builds from
   that row. The event-type registry `PC-43` promises also has no table. The first event emitted
   under the wrong row can never be re-emitted with the missing dimensions.

**Ten MAJORs share one root cause: a key or vocabulary that is global, closed, or single-scheme by
default.** Catalogue codes are `uk(code)` install-wide, and the port's own worked example silently
collides with base's seed through `ON CONFLICT DO NOTHING` (`RL-003`). Location, LPN and item codes
and every formatted document number are globally unique, so site, owner and company get baked into
printed identifiers (`RL-004`). The identifier table's key contradicts `FR-059` in the one sentence
`FR-059` exists to state (`RL-005`). Eleven second-tier vocabularies, including four on the
partitioned ledger, have no open-or-closed ruling, and the classic house default is
`CHECK (status IN …)` in 205 migration files (`RL-006`). The attribute mechanism, the set's answer to
custom fields, applies to items and movement lines only (`RL-007`). Three columns in the
country-neutral core are named for one country's tax scheme (`RL-008`). The mobile schema file will
re-close every registry the web leaves open (`RL-009`). Allocation, putaway and negative-stock rules
are edited in place under the ids that reservations and tasks record (`RL-010`). Every high-volume
table except the ledger is created unpartitioned (`RL-011`). And `OD-3`'s one technical consequence,
that configuration must travel between databases, is restated in three documents and owned by no
task (`RL-012`).

**None of this needs new infrastructure.** Two BLOCKERs and seven MAJORs are a column type, a key, a
seed rule or a sentence in a migration **that has not been written yet**. The rest are v1.1–v2 builds
recorded so they are not lost, per `D-12`.

---

## §1.1 · Coverage table

**Verdict key:** `SOUND` = the next consumer extends it with a seed row or an additive change ·
`HOLED` = extensible with a named hole · `BROKEN` = the next consumer needs a base release, a
relabel or a restatement · `OWNED` = a real gap already carried by an earlier finding, not re-filed.

| # | Axis | Verdict | Finding |
|---|---|---|---|
| 1 | Open vocabularies (`D-10`) | **HOLED**: the fourteen are open; the ledger's fifteenth and eleven app-level ones are not | **`RL-001`** `RL-006` |
| 2 | Status ladders | **HOLED**: closed by design (`OD-5` permits), no transition hook | `RL-006` `RL-014` |
| 3 | Polymorphism-by-columns | **OWNED by R22**: `variant_axis_1/2/3_value_id` is numbered-column cardinality | §4 #1 |
| 4 | Generic references | **SOUND**: every one of `G1`–`G15` names a registry-typed discriminator or a stated guard (`DATA-MODEL.md:1497-1513`) | — |
| 5 | Effective dating on masters | **OWNED**: `Z-004`'s *Frozen when* column | §4 item 2 |
| 6 | Hard vs soft delete | **SOUND**: `RESTRICT` + `is_active`, no `deleted_at` (`DATA-MODEL.md:110-132`); retirement is `Z-005` | §4 #3 |
| 7 | Versioning of rules and config | **HOLED**: valuation, GL, kits, templates versioned; allocation, putaway, negative-stock not | `RL-010` |
| 8 | Single currency | **OWNED**: `OD-16` / `RF-004` | §4 #7 |
| 9 | Single UoM | **SOUND**: per-item conversion, frozen factor, secondary quantity (`IRR-34`, `IRR-35`) | — |
| 10 | Single timezone | **SOUND**: `FR-439` v1, `whb_warehouses.timezone`, `occurred_at_tz_offset`, `p1-12.md:92` | — |
| 11 | Single language | **HOLED**: registry rows carry one `name` | `RL-015` |
| 12 | Country-specific fields in the core (`D-8`) | **BROKEN** for a second jurisdiction | **`RL-001`** `RL-008` |
| 13 | Port leaking vertical concepts | **SOUND**: one envelope (`PC-06`); the header's *deliberately not* list (`PORT…:242-245`); `B4` import ban | — |
| 14 | Domain events, outbox, event versioning | **BROKEN**: two outbox specifications | **`RL-002`** (protocol half is `RD-002`) |
| 15 | API versioning | **SOUND** for the port (`PC-75`, §10.2, §10.3); **HOLED** for the handheld-facing management API | `RL-017` |
| 16 | Custom fields / extensible attributes | **HOLED**: two subject kinds only | `RL-007` |
| 17 | Partitioning / archival | **HOLED**: the ledger only | `RL-011` (ledger archive is `Z-006`) |
| 18 | Identifiers embedding meaning / global namespaces | **BROKEN** at the second site, owner and company | `RL-003` `RL-004` `RL-005` |
| 19 | Multi-company / multi-install | **HOLED**: keys global; config not portable | `RL-004` `RL-012` (`OD-3` itself escalated) |
| 20 | Mobile offline sync / vocabulary | **OWNED** (`RD-003` queue) · **HOLED** (vocabulary re-closure) | `RL-009` |
| 21 | Feature flags / module toggles | **SOUND**: `ENABLE_*` + `ModuleImportSelector` (`MODULE-INTEGRATION.md` §8–9); per-item modes are data; disable leftovers are `RE-008` | — |
| 22 | Plug-in points | verticals **SOUND** (`D-11`, `PC-72`–`PC-74`) · channels **SOUND** (`FR-207`) · statutory providers **SOUND** (`whin_compliance_providers`, `INDIA-LOCALISATION-PACK.md:1233-1237`) · carriers **OWNED** (`RD-005`) · printers **HOLED** | `RL-006` |
| 23 | Test seams | fixture adapter **SOUND** (`PC-73`) · time **HOLED** | `RL-016` |

---

## §2 · The findings

### `RL-001` · `duty_status` is in the position key, in `L-1`'s conservation grain and on every cost layer, and it is the only vocabulary on the ledger with no registry — its values are Indian customs regimes in the country-neutral core — **BLOCKER**

- **What is missing or wrong:**
  - **No registry, no FK.** `whb_stock_movement_lines.duty_status` is `VARCHAR(30) NOT NULL DEFAULT
    'DOMESTIC'` with **no `REFERENCES` clause** (`DATA-MODEL.md:693`; `IRREVERSIBLE.md:486`;
    `PORT-AND-ADAPTER-CONTRACT.md:275`). Every sibling on the line is an FK by code:
    `stock_status_code` (`:691`), `condition_code` (`:692`), `movement_type_code` (`:604`).
  - **Indian vocabulary in the core.** `IRR-12` enumerates the values as `DOMESTIC` · `BONDED` ·
    `MOOWR` · `SEZ` · `FTWZ` · `EXPORT_UNDER_BOND` (`IRREVERSIBLE.md:168`). Four of the six are
    Indian customs regimes, placed in the table `D-8` says carries *"no GST, HSN semantics, e-way
    bill or MRP rule"* (`DECISIONS.md:207-209`).
  - **Load-bearing everywhere.** The column is a member of the `L-5` nine-member key
    (`DATA-MODEL.md:785`), of `L-1`'s balance grain `(owner, item, lot, serial, duty_status)`
    (`:2184`, `:2394`), of `whb_cost_layers` (`:857`, `V500021`), and of five `wh_` document lines.
  - **Outside the no-`CHECK` guard.** `I-18`'s test enumerates **fourteen** `table.column` pairs, and
    this is not one of them (`DATA-MODEL.md:2796-2799`).
  - **Recorded twice.** `BONDED` is **also** a seeded **stock status** (`IRREVERSIBLE.md:668`), so
    one fact now has two axes.
  - **Round 1 assumed a table that does not exist.** It dispositioned `G-038` with a residual of
    *"the `BONDED`/`BONDED_ZONE` seed rows are not enumerated"* (`GAP-REGISTER.md:455`), but there is
    no table to seed them into.
- **Why it matters — what breaks later:**
  1. **`warehouse-india` (v2) cannot add a regime without touching base.** An EOU unit or a Section
     58 warehouse is a new value. As a free string there is no behaviour row to say whether it may
     be allocated to domestic demand, whether it needs a licence, or whether it may commingle. As a
     Java enum, every new regime is a base release, which breaks `D-11`'s *zero commits to
     `warehouse-base`* ratchet.
  2. **A typo is a new balance grain, not an error.** `'BONDED '` or `'Bonded'` passes the column and
     creates its own position row. `L-1` then balances per the misspelt value, so the movement either
     fails to conserve or conserves into a bucket nobody queries. `IRR-12` itself calls commingling
     here *"a customs offence, not a data-quality issue"*; the reverse, one regime split across two
     spellings, is an ex-bond Bill of Entry that cannot find its identified quantity.
  3. **A second jurisdiction inherits India's names in its position key.** EU customs warehousing,
     inward processing, T1 transit and GCC free zones are the same shape with different values. The
     only honest place for them is a registry each jurisdiction module seeds.
  4. **Two axes for one fact.** A unit can be `stock_status = BONDED` and `duty_status = DOMESTIC`,
     and nothing refuses it.
- **Negative evidence:**
  ```bash
  grep -n "duty_status" docs/DATA-MODEL.md | grep -c "REFERENCES\|→ whb_"          # 0
  grep -rn "whb_duty_statuses\|duty_status_code" docs/ issues/ | wc -l             # 0
  sed -n '2796,2799p' docs/DATA-MODEL.md                                          # fourteen pairs; duty_status not among them
  grep -n "BONDED" docs/IRREVERSIBLE.md | cut -c1-80                               # :168 (duty) and :668 (stock status seed)
  ```
- **Where it belongs:** `warehouse-base` · **v1 (column/registry)**, v2 (India regimes) · **P0**
- **Disposition — the minimum cheap-now change:** fold into **`P0-05`** and **`P0-02`**.
  - `V500005`, which already creates `whb_stock_statuses` and `whb_condition_codes`, also creates a
    **fifteenth registry**, `whb_duty_statuses`, in the §1.8 shape. Its behaviour columns are
    `is_duty_paid`, `is_allocatable_to_domestic_demand`, `requires_licence` and `commingle_group`.
    **Base seeds `DOMESTIC` only**; `warehouse-india` seeds `BONDED`, `MOOWR`, `SEZ`, `FTWZ` and
    `EXPORT_UNDER_BOND` in `V540xxx`.
  - `V500021` and `V500030` declare the column as
    `duty_status VARCHAR(40) NOT NULL DEFAULT 'DOMESTIC' REFERENCES whb_duty_statuses(code)`.
  - `I-18` enumerates fifteen pairs.
  - `BONDED` is **removed from the stock-status seed** (`IRREVERSIBLE.md:668`); a customs *hold* is a
    `wh_hold_types` row, not a status.
  - `IRR-12`'s value list moves into `INDIA-LOCALISATION-PACK.md`.
- **Affected tasks:** `P0-05`, `P0-02`, `P0-17` (`V500021` cost layers), `P2-01`, `P2-16`, `P4-07`,
  `P2IN-03`.
- **Irreversibility:** **one-way door at `V500021`/`V500030`.** Retyping and adding an FK to a
  column of a partitioned table under the `L-2` trigger is a scan of every partition; the misspelt
  history it would have prevented cannot be merged back under `L-2`/`L-3`.
- **Relationship to earlier rounds:** **new.** `G-038` treated the column as if its registry existed.
  `IRR-12` argued *that* the column must exist, and was right; nobody asked *what shape*.

---

### `RL-002` · The migration authority and the port contract specify two different outboxes: `DATA-MODEL.md`'s row has no `event_version`, none of the dimensions `PC-38` says are irreversible, and a `TEXT` payload `PC-37` forbids — and `P0-11` builds from that row — **BLOCKER**

- **What is missing or wrong:**
  - **Two specifications.** `PORT-AND-ADAPTER-CONTRACT.md:709-741` specifies `whb_outbox` with
    `event_version SMALLINT NOT NULL DEFAULT 1`, `company_id`, `item_id`, `lot_id`, `serial_id`,
    `lpn_id`, `location_id`, `stock_status_code`, `quantity`, `uom_code`, `recorded_at`,
    `posting_date`, the lineage quad and the actor triple. `PC-38` (`:748-752`) and `FR-331` say these
    are on *"every event from day one"* because *"adding a dimension to an existing code is not"*
    cheap. `DATA-MODEL.md:879`, which `README.md:20` names **the migration authority**, lists
    `cursor`, `event_type`, `occurred_at`, `warehouse_id`, `owner_id`, `movement_id`,
    `movement_line_id`, `subject_type`, `subject_id`, **`payload TEXT`**, `payload_hash`. That is no
    `event_version`, no `company_id`, no `lot_id`/`lpn_id`/`serial_id`, no `recorded_at` and no
    `posting_date`.
  - **The builder follows the authority.** `P0-11` writes `V500040` from the `DATA-MODEL.md` row. Its
    `WS-056` column list is `cursor … payloadHash … movementSequenceNo` (`issues/p0-11.md:63`).
  - **The payload is the forbidden shape.** `PC-37` forbids *"an outbox that carries an opaque
    blob"*; `FR-434` lists *"JSON smuggled in a text column"* as a named failure mode
    (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:754`).
  - **No event-type registry.** `PC-43` says `event_type` is *"a registry-backed code … on the same
    terms as the thirteen catalogues"* (`PORT…:817-819`). No such table exists.
  - **Subscriptions cannot pin a version.** Neither subscription specification (`DATA-MODEL.md:880`:
    `transport`, `last_delivered_cursor`; `PORT…:760-769`: `target_kind`,
    `last_delivered_sequence_no`, which also disagree with each other) lets a subscriber declare
    which `event_version` it accepts. So `PC-75`'s promise that *"outbox events version
    independently, by `event_version`"* has no receiving half.
  - **The accounting envelope has no version either.** `whb_accounting_handovers` stores `payload
    TEXT` *"verbatim for replay"* (`DATA-MODEL.md:860-864`) with an `envelope_kind` and no envelope
    version.
- **Why it matters — what breaks later:** this is the one place the set itself says an event
  decision is irreversible, and the migration will be written against the row that loses the
  argument.
  - **3PL billing (v2).** It needs `lot_id`/`lpn_id` per pick line (`PC-42`). From `V500040` onward
    every emitted event lacks them, and *"consumers' cursors have already passed them"*.
  - **`logistics` (v3).** It needs `company_id` and `posting_date` to route and settle; it gets a
    `subject_id` and a blob to parse.
  - **The first shape change.** The first `event_version = 2` has no subscriber-side pin, so an HTTP
    consumer receives v2 bodies unannounced. That is *"change the meaning of an existing field"*, the
    worst row in `PORT…` §10.2.
  - **Accounting.** When accounting changes its envelope, a stored v1 handover replayed after the
    change is parsed as v2.
- **Negative evidence:**
  ```bash
  grep -c "event_version" docs/DATA-MODEL.md issues/p0-11.md docs/PORT-AND-ADAPTER-CONTRACT.md   # 0 · 0 · 2
  grep -c "lot_id\|lpn_id\|company_id" issues/p0-11.md                                          # 0
  grep -rn "whb_event_types\|event_types" docs/ issues/ | wc -l                                  # 0
  sed -n '879,881p' docs/DATA-MODEL.md | grep -o "payload\*\* \*\*TEXT\|payload\` \*\*TEXT"    # the TEXT payload
  ```
- **Where it belongs:** `warehouse-base` · **v1** · **P0** (`V500040`, `V500042`)
- **Disposition — the minimum cheap-now change:** fold into **`P0-11`**, with **`DATA-MODEL.md`
  §2.1.12 amended to match `PORT…` §4.2 — the contract wins, because `FR-331` is the requirement and
  the row is the transcription.**
  1. `whb_outbox` takes `PC-36`'s column set verbatim, including `event_version`. `payload TEXT` is
     replaced by `PC-37`'s `payload_ref` into typed attribute rows; this needs `RL-007`'s
     `applies_to = EVENT`.
  2. `whb_event_types` joins the registries as the sixteenth (`code`, `owning_module`, `grain`,
     `current_version`, `is_billable`), seeded with `PC-42`'s thirteen codes, and `event_type` becomes
     an FK by code.
  3. `whb_outbox_subscriptions` gains `accepted_event_version SMALLINT NOT NULL DEFAULT 1`. Base
     emits each event at the version the subscription accepts until the subscriber moves, and
     `PC-75` states it.
  4. `whb_accounting_handovers` gains `envelope_version`.
  5. Do all of this **in the same edit as `RD-002`'s signing columns**: same migration, same task.
- **Affected tasks:** `P0-11` (`V500040`), `P0-12` (`V500042`), `P3-22`, `P0-05` (registry), and
  `P5-03` as the first consumer.
- **Irreversibility:** **one-way from the first emitted event.** In `FR-331`'s own words the finer
  facts *"cannot be reconstructed from a coarse event after the fact"*.
- **Relationship to earlier rounds:** **new.** `RD-002` is the outbound **protocol** (signing, status
  mapping, timeouts) and is refused here as owned. This is the **schema and versioning** of what is
  sent, and the divergence between two documents that nobody diffed.

---

### `RL-003` · Catalogue codes are one install-wide namespace, `PC-66` makes every consumer insert with `ON CONFLICT DO NOTHING`, and the contract's own worked example silently collides with base's seed — so the second module to claim a code posts under the first module's behaviour flags — **MAJOR**

- **What is missing or wrong:**
  - **One namespace.** Every registry is `CONSTRAINT uk_whb_<name>_code UNIQUE (code)`
    (`DATA-MODEL.md:275`).
  - **Silent on collision.** `PC-66` instructs consumers to add values by *"seed `INSERT` … `ON
    CONFLICT DO NOTHING`"* (`PORT…:1171-1173`).
  - **The worked example collides.** The *"whole cost of a logistics module learning to move stock"*
    inserts `TRANSFER_DEPART`, `TRANSFER_ARRIVE` and `TRANSIT_LOSS` with `owning_module =
    'logistics'`, its own `balance_rule` and its own `reversal_type_code` (`PORT…:1201-1206`). Base
    already seeds all three in `V500003` (`IRREVERSIBLE.md:665`, row 1). `DO NOTHING` keeps base's
    row, so every logistics value in that `INSERT` is discarded without a word.
  - **Only one collision is forbidden.** `B7` forbids reusing another adapter's **source-system**
    code (`PORT…:1304`). Nothing forbids two modules seeding the same movement-type, reason, status or
    task code.
  - **Reason codes are global too.** `whb_reason_codes` is `uk(code)` across all contexts. The
    example's reason `INSERT` uses a target-less `ON CONFLICT DO NOTHING` (`:1208-1210`). The
    accounting precedent the set cites is `uk(company_id, context, code)`
    (`accounting-base/…/V600002__Create_acc_reason_codes.sql:19`).
- **Why it matters — what breaks later:**
  - **Adapters.** `warehouse-adapter-dealer` and `warehouse-adapter-services` both ship in v1, and
    both plausibly need a `WARRANTY_ISSUE` movement type or a `WARRANTY` reason. Whichever migrates
    second gets a silent no-op, and its postings carry the first adapter's `is_financial`,
    `requires_approval` and `reversal_type_code`.
  - **History.** Under `L-2` and `PORT…` §10.2 (*"rename a catalogue code: no"*), movements posted
    with the wrong semantics cannot be corrected except by reversal, and nothing flags which ones
    they were.
  - **Reason codes.** `DAMAGE` cannot exist in both the `ADJUSTMENT` and `RETURN` contexts, so codes
    start embedding their context (`DAMAGE_ADJ`, `DAMAGE_RET`), which is the meaning-in-identifier
    pattern `RL-004` records elsewhere.
- **Negative evidence:**
  ```bash
  grep -n "ON CONFLICT" docs/PORT-AND-ADAPTER-CONTRACT.md | cut -c1-60     # :1172 rule · :1193 :1199 :1206 (code) · :1210 (none)
  grep -n "TRANSFER_DEPART" docs/IRREVERSIBLE.md | cut -c1-60              # :665 — base's v1 seed
  grep -rn "owning_module <>\|owning_module !=" docs/ issues/ | wc -l      # 0 — no collision guard anywhere
  ```
- **Where it belongs:** `warehouse-base` · **v1** · **P0**
- **Disposition — the minimum cheap-now change:** fold into **`P0-04`** and into `PORT…` §7.3.
  1. **A module inserts only codes it owns.** To *use* a base code it references it and never
     re-inserts it. The worked example is corrected to reference `TRANSFER_DEPART` and to insert only
     `TRIP`/`MANIFEST`/`CONSIGNMENT` and its genuinely new codes.
  2. **The seed idiom becomes guarded.** After `ON CONFLICT (code) DO NOTHING`, one `DO $$ … IF
     EXISTS (SELECT 1 FROM <registry> WHERE code = … AND owning_module <> '<me>') THEN RAISE
     EXCEPTION …` block runs, in `V600200:150-161`'s verification shape. It stays idempotent for the
     owner and fails loudly for anyone else.
  3. **`PC-72` gains assertion 7:** across all warehouse-family bands, no `(registry, code)` pair is
     inserted by two `owning_module` values.
  4. **`whb_reason_codes` is keyed `uk(context, code)`** in `V500004`, following accounting minus
     `company_id`.
- **Affected tasks:** `P0-04` (`V500002`–`V500004`), `P0-05`, `P1-02`, `P1-08`, `P2-25` and every
  adapter registration migration (`V520000`+, `V521000`+).
- **Irreversibility:** **the collision is unrecoverable once a colliding code is posted against**;
  the guard itself is reversible. `V500004` sets the reason-code key.
- **Relationship to earlier rounds:** **new.** `RE-005` found the seeds unenumerated and `Z-005`
  found retirement closed; neither looked at two writers of one code.

---

### `RL-004` · Location, LPN and item codes and every formatted document number are globally unique, so site, owner and company get baked into printed identifiers — the second site's bin-grid run collides, and `RE-002` has already adopted the site-prefix workaround — **MAJOR**

- **What is missing or wrong:** six keys are install-wide where their natural scope is narrower.

  | Key | Where | Natural scope | Evidence |
  |---|---|---|---|
  | `whb_locations.code` | `uk(code)` globally, *"so a scanned location string resolves without a site"* | the site — `uk(warehouse_id, code)` is also declared | `DATA-MODEL.md:453` |
  | `whb_lpns.code` | `uk(code)` | owner × site | `:576` |
  | `whb_items.code` | `uk(code)` globally, beside the owner-scoped `uk(owner_id, sku)` | owner | `:529`, `:2813-2815` |
  | `whb_number_series_issued.formatted_number` | `uk(formatted_number)` across **every series, module and company** | the series | `:911`, `:2821` |
  | `whb_owners.code` · `whb_warehouses.code` | **both** `uk(code)` **and** `uk(company_id, code)`, where the global key makes the scoped one dead | company | `:499`, `:452` |
  | every registry `code` | `uk(code)` | see `RL-003` | `:275` |

  The workaround is already in the backlog. `RE-002`'s disposition fixes virtual locations as
  **`VIRT-<PURPOSE>-<SITE CODE>`**, *"because `whb_locations.code` is globally unique"*
  (`GAP-REGISTER-R3.md:270`).

  Platform made the same move once. `branches` began owner-scoped (`uk(owner_type, owner_id,
  branch_code)`, `platform/…/V149__create_branches_table.sql:60`) and was widened to global
  (`V160__Remove_owner_fields_from_branches.sql:18-20`).
- **Why it matters — what breaks later:**
  1. **The second site.** `FR-089`'s generator takes a format mask and produces 3,000–20,000 codes
     per site (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:229`). Run the same mask at site B, which is the
     v1 exit criterion's *"transfers stock to a second site"*, and every code collides. The only
     escape is a site token in every code. That token is then **printed on every bin label**, and
     `FR-064` records that a printed label cannot be recalled. A site-code change, a merger or a
     consolidation of two `OD-3` databases is a relabel of the building.
  2. **The second 3PL client.** `IRR-19` rescued the SKU from global uniqueness and `whb_items.code`
     re-closed it one column over. Client 2's `A100` cannot be `code = A100`, so onboarding scripts
     prefix the owner into the code.
  3. **The second company.** Company B's `GRN-000001` collides with company A's, so every series
     prefix must embed a company token. A `YEARLY` reset collides with its own previous year unless
     the year is in the string, which `Z-002` found from the other side.
- **Negative evidence:**
  ```bash
  grep -n "uk(\`code\`) globally\|uk(\`formatted_number\`)\|uk_whb_number_series_issued_number" docs/DATA-MODEL.md | cut -c1-90
  grep -n "VIRT-<PURPOSE>-<SITE CODE>" docs/GAP-REGISTER-R3.md | cut -c1-60        # :270
  ```
- **Where it belongs:** `warehouse-base` · **v1** · **P1** (`V500007`, `V500012`, `V500013`,
  `V500015`, `V500018`, `V500020`)
- **Disposition — the minimum cheap-now change:** one decision per key, written into `DATA-MODEL.md`
  §1.3 and the owning tasks.
  - **`formatted_number`:** `uk(series_id, formatted_number)`. The global index adds nothing
    gaplessness needs (`I-20` is per series).
  - **Owners and warehouses:** keep **one** key, `uk(company_id, code)`.
  - **Items:** `code` is a **system-generated, immutable surrogate**, never a user-typed SKU. `P1-01`
    already freezes it (`issues/p1-01.md:24`). Or it becomes `uk(owner_id, code)`.
  - **Locations and LPNs:** either (a) keep the global key and make `FR-089`'s mask **require** a
    `{SITE}` token, stated as a product decision because it goes onto physical labels; or (b)
    `uk(warehouse_id, code)` only, with `FR-062`'s scan resolution scoped by the session's or
    device's site and an `AMBIGUOUS_LOCATION` code for a cross-site scan. **Recommend (b).** The
    resolver already returns a typed object and a site context is always known on a handheld.
- **Affected tasks:** `P1-05`, `P1-06` (`WS-018` generator), `P1-01`, `P1-07`/`P1-08` (`whb_lpns`),
  `P1-09` (`V500020`), `P0-05` (`V500013` virtual-location seed, with `RE-002`).
- **Irreversibility:** the **indexes** are reversible on master tables. The **printed codes** are
  not: every label generated under a global key already carries its prefix.
- **Relationship to earlier rounds:** **new.** `RE-002` accepted the global location key as a premise
  and built on it; `IRR-19`/`I-19` fixed the SKU and left `code` beside it.

---

### `RL-005` · `FR-059` says the identifier table is *"deliberately not globally unique — two owners legitimately carry the same EAN"*, and the migration authority declares `uk(identifier_type, identifier_value)` — one install-wide key over EANs, OEM part numbers and supplier part numbers alike — **MAJOR**

- **What is missing or wrong:**
  - **The requirement.** `FR-059`: *"It is deliberately **not globally unique** — two owners
    legitimately carry the same EAN"* (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:194`).
  - **The key actually declared.** `whb_item_identifiers`: *"uk(`identifier_type`,
    `identifier_value`)"* (`DATA-MODEL.md:532`), restated at `IRREVERSIBLE.md:539-540`. `P1-02`
    indexes `normalised_value` (`issues/p1-02.md:105`).
  - **Scope columns outside the key.** `counterparty_id` (set for a supplier or customer part number)
    and `channel_id` (set for a marketplace listing) are on the row and not in the key. There is no
    `owner_id` on the row at all.
  - **No registry for the type.** `identifier_type` has no registry, so the rule *"a supplier part
    number is unique per supplier; an EAN is unique per owner"* has nowhere to live.
- **Why it matters — what breaks later:**
  - **v1, dealer adapter.** A multi-brand dealer loads two OEMs' part-number catalogues as
    `OEM_PART_NUMBER` identifiers, and the strings overlap across OEMs. The second load is refused,
    and the counter clerk's *"scan or part number"* (`FR-359`) resolves to the wrong brand or to
    nothing.
  - **v2, 3PL.** A second client stocking the same branded EAN cannot register it, which is `FR-059`
    refused by its own table.
  - **Rejected rows never land.** As `IRR-14` says of serials, the rows a wrong constraint rejected
    were never recorded. The workaround codes typed instead (`EAN-2`) pollute the alias table
    permanently.
- **Negative evidence:**
  ```bash
  grep -n "not globally unique" docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md | cut -c1-40    # :194 FR-059
  grep -n "uk(\`identifier_type\`,\`identifier_value\`)" docs/DATA-MODEL.md | cut -c1-40   # :532
  grep -rn "identifier_types\|AMBIGUOUS_IDENTIFIER" docs/ issues/ | wc -l                  # 0
  ```
- **Where it belongs:** `warehouse-base` · **v1** · **P1** (`V500016`)
- **Disposition — the minimum cheap-now change:** fold into **`P1-02`**.
  - `whb_item_identifiers` gains `owner_id`, denormalised from the item, and the key becomes
    `uk(identifier_type, normalised_value, owner_id, counterparty_id, channel_id) NULLS NOT DISTINCT`.
  - `identifier_type` becomes a registry row (via `RL-006`'s code list, or its own table) carrying
    `uniqueness_scope` (`OWNER` / `COUNTERPARTY` / `CHANNEL`), `check_digit_algorithm` and
    `normalisation_rule`.
  - `FR-062`'s resolver gains a stated disambiguation order: session owner → counterparty context →
    refuse with `AMBIGUOUS_IDENTIFIER` listing the candidates.
  - `FR-059`'s sentence becomes the key's comment.
- **Affected tasks:** `P1-02`, `P1-12`/`P1-13` (scan surfaces), `P2-25` (counter sale), `P5-*`
  (client onboarding).
- **Irreversibility:** reversible as an index; **not** reversible for the identifiers that were
  refused and re-keyed by hand in the meantime.
- **Relationship to earlier rounds:** **new.** `F-006`/`E-012` produced `FR-059`'s sentence; no lens
  read the key against it.

---

### `RL-006` · Eleven vocabularies outside the fourteen registries — four of them on the partitioned ledger — carry enumerated values and no open-or-closed ruling, the classic house default is `CHECK (status IN …)`, and two round-3 findings have already had to add a value to a closed ledger vocabulary — **MAJOR**

- **What is missing or wrong:** `D-10` rules on the fourteen, and `OD-5` permits unions for *"a
  closed system vocabulary the product itself defines and no install may extend"*. Nothing
  classifies the rest, and each of the following has a named consumer who must extend it.

  | Column | Values as written | Who must extend it | Evidence |
  |---|---|---|---|
  | `wh_print_templates.template_kind` | *"one of the eleven of `FR-225`"* | the dealer **cash ticket** (`FR-359`, v1); India's challan and e-way bill prints (`P2-IN`, v1); a 3PL invoice annex (v2) | `DATA-MODEL.md:1036`; `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:410` |
  | `wh_print_templates.format` | `ZPL`/`EPL`/`TSPL`/`PDF`/`HTML` | DPL, IPL and SBPL printer fleets | `:1036` |
  | `wh_demand_orders.demand_type` + **`whb_allocation_rules.demand_type_code`** | *"sales, transfer, work order, replenishment, VAS, sample, scrap, job issue"*; a `*_code` column **with no table** | services job issue; logistics trip load; 3PL | `:1021`, `:831`; `issues/p2-07.md:12` |
  | `wh_return_receipts.return_type` | eight values incl. `MARKETPLACE`, `RECALL` | each channel connector | `:1072` |
  | `whb_channels.channel_kind` | `MARKETPLACE`/`OWN_STORE`/`POS`/`B2B` | quick-commerce, distributor apps | `:928` |
  | `whb_item_identifiers.identifier_type` | none stated | every marketplace, GS1 (GIAI/GRAI), medical UDI | `:532` · `RL-005` |
  | `whb_locations.location_level` | `SITE`…`POSITION`, seven | a mezzanine, a cold room inside a zone; `whb_location_types.default_location_level` reads it | `:453`, `:417` |
  | `whb_stock_movements.actor_type` | six (`PORT…:233`) | v3 automation interfaces: an AMR, a vision tunnel | `:622` |
  | `whb_stock_movements.approval_status` | unstated | **`RA-004` adds `WITHDRAWN`** — *"a `CHECK` drop-and-rebuild on the hottest table afterwards"* | `GAP-REGISTER-R3.md:218` |
  | `whb_stock_movement_lines.cost_basis` | five | **`RF-002` adds `ESTIMATED`** | `GAP-REGISTER-R3.md:323` |
  | `whb_barcode_formats` | a **registry referenced and never defined** — `V500056` inserts a `GS1_DIGITAL_LINK` row into it | GS1 | `DATA-MODEL.md:2927`; defined nowhere |

  Plus `warehouse_type`, `lpn_type`, `transformation_type` and `work_order_type`, which have no
  values stated at all.
- **Why it matters — what breaks later:**
  - **The house default wins by omission.** 205 migration files in classic carry
    `CHECK (status IN …)`. An unclassified column gets one, and each of the first six rows above
    becomes a base/app release per consumer, which is `D-11`'s ratchet broken by a column nobody
    ruled on.
  - **The ledger rows are already moving.** The last four are on **`whb_stock_movements` /
    `_lines`**, where round 3 has already had to widen two of them *before the first line of code*.
    A `CHECK` added to or rebuilt on a partitioned table validates every partition under an `ACCESS
    EXCLUSIVE` lock (whether `NOT VALID` is usable on a partitioned parent in PG 17 is
    **UNVERIFIED**; it would be settled by a `psql` test against `platform-postgres`).
  - **A registry that exists only in prose.** `whb_barcode_formats` has rows inserted into it and no
    `CREATE TABLE`.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git2/workspace/classic
  grep -rlE "CHECK \(status IN|CHECK \([a-z_]*status IN" --include=*.sql . | wc -l      # 205
  cd -; grep -rn "whb_barcode_formats" docs/ issues/ | wc -l                            # 1 — the V500056 row only
  grep -rn "demand_types\|whb_demand_type" docs/ issues/ | wc -l                          # 0 — demand_type_code has no target
  ```
- **Where it belongs:** `warehouse-base` + `warehouse` · **v1** · **P0**/P1/P2
- **Disposition — the minimum cheap-now change:** one table and one rule, no ten new registries.
  1. **`DATA-MODEL.md` §2.1.1 gains a *Vocabulary classification* table.** Every enumerated column
     in the model is tagged `REGISTRY` (FK by code, no `CHECK`, enumerated by `I-18`) or
     `CLOSED-SYSTEM` (`OD-5` union allowed; `CHECK` allowed **except on the two partitioned ledger
     tables, which carry no `CHECK (… IN …)` at all** — the writer service and the `I-2` trigger
     enforce them).
  2. **One generic open list for low-behaviour vocabularies:**
     `whb_code_lists(list_code)` + `whb_code_list_values(list_code, code, name, owning_module,
     is_system, sort_order, is_active)`, FK'd by the composite `(list_code, code)`. It carries
     `template_kind`, `print_format`, `demand_type`, `return_type`, `channel_kind` and
     `actor_type`, each seedable by any module under `RL-003`'s guard.
  3. **`whb_barcode_formats`** is either defined in `V500056` or the reference is removed.
- **Affected tasks:** `P0-02` (ledger classification), `P0-05` (`V500010`), `P1-02`, `P1-05`,
  `P2-07`, `P2-14` (print), `P2-25` (cash ticket), `P3-24` (`V500056`).
- **Irreversibility:** **the ledger four are `V500030`**; the rest are reversible, but each `CHECK`
  written is a future drop-and-rebuild with `FR-377`'s merge idiom.
- **Relationship to earlier rounds:** **new as a class.** `RA-004` and `RF-002` are two instances,
  each fixed alone; `RD-006` specifies what a template *kind* renders and not whether the kinds are
  open.

---

### `RL-007` · The attribute mechanism — the set's answer to custom fields — applies to items and movement lines only, so lots, serials, locations, counterparties, documents and outbox events have no extensible attribute, and the movement-line side table is specified in two incompatible shapes inside `V500030` — **MAJOR**

- **What is missing or wrong:**
  - **Two subject kinds.** `whb_attribute_keys.applies_to` is `ITEM`/`MOVEMENT_LINE`/`BOTH`
    (`DATA-MODEL.md:425`; `WS-013` at `BUILD-SPEC-SCREENS.md:773`; `issues/p0-05.md:45`). Value
    tables exist for exactly those two (`:535`, `:740`).
  - **The outbox depends on a third.** `PC-37` routes outbox event facts through *"typed rows in a
    side table keyed by registered `whb_attribute_keys`"* (`PORT…:743-746`), and there is no `EVENT`
    value and no event value table.
  - **The only other answer is forbidden to the modules that need it.** `FR-078`'s answer to custom
    fields is *"a typed column on request, or the attribute tables of `FR-076`"*
    (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:213`). A typed column on a base table is what `D-11`
    `B2` forbids every adapter and jurisdiction module to add (`PORT…:1299`).
  - **Two shapes at `PNR-1`.** `DATA-MODEL.md:740` gives `whb_movement_line_attributes` four typed
    columns (`value_string`/`_number`/`_date`/`_boolean`). `IRREVERSIBLE.md:500-501` and
    `PORT…:291-292` give it `(attribute_value, value_type)`, one text value with a type tag, which is
    `FR-434`'s *"JSON smuggled in a text column"* at a smaller scale. The table is created in
    `V500030` and is append-only.
- **Why it matters — what breaks later:**
  - **Lot attributes are unbackfillable.** `IRR-53`'s own argument is that *"every one of these is
    printed on a pack that has already been put away."* A pharma customer's potency, a food
    customer's harvest date or a cold-chain certificate number is not in `IRR-53`'s fixed ten.
    With no lot-attribute table it is either not captured at receipt, which is unrecoverable, or
    captured as an `ALTER` to `whb_lots` in base.
  - **Other subjects have nowhere to go.** A customer's PO reference on the GRN, a chassis number on
    a job issue, a counterparty's licence number: none can be recorded without a base column.
  - **`T-094` was placed at v3 as *"typed attribute tables"***
    (`COMPETITOR-BENCHMARK.md:163`). The v1 shape is what that v3 build will have to live with.
- **Negative evidence:**
  ```bash
  grep -n "applies_to" docs/DATA-MODEL.md | cut -c1-60                              # :425 — ITEM/MOVEMENT_LINE/BOTH
  grep -rn "lot_attribute\|entity_attribute\|document_attribute" docs/ issues/ | wc -l   # 0
  grep -n "attribute_value, value_type" docs/IRREVERSIBLE.md docs/PORT-AND-ADAPTER-CONTRACT.md | cut -c1-70
  ```
- **Where it belongs:** `warehouse-base` · **v1** (shape) · v3 (`T-094` screens) · **P0**
- **Disposition — the minimum cheap-now change:** fold into **`P0-05`** (`V500010`) and **`P0-02`**
  (`V500030`).
  - `applies_to` becomes an open list: `ITEM`, `MOVEMENT_LINE`, `LOT`, `SERIAL`, `LPN`, `LOCATION`,
    `COUNTERPARTY`, `DOCUMENT`, `EVENT`.
  - **One** generic typed table serves the non-partitioned subjects:
    `whb_entity_attribute_values(entity_kind, entity_id, attribute_key_id, value_string,
    value_number, value_date, value_boolean)`, keyed `uk(entity_kind, entity_id, attribute_key_id)`.
  - The two specialised tables stay.
  - `V500030`'s side table takes `DATA-MODEL.md`'s **four typed columns**, and `IRREVERSIBLE.md` §4.2
    and `PORT…` §2.5 are amended.
  - **State that install-created keys (`owning_module = 'INSTALL'`) through `WS-013` are the
    product's custom-field answer**, so `T-094` is a screen, not a schema, in v3.
- **Affected tasks:** `P0-05`, `P0-02`, `P0-11` (event facts, `RL-002`), `P1-02` (`V500016`),
  `P1-07`/`P1-08` (lots).
- **Irreversibility:** the line side-table shape is **`PNR-1`**. Lot attributes not captured at
  receipt are **unbackfillable** (`IRR-53`'s class).
- **Relationship to earlier rounds:** **extends** `T-094`/`FR-078` (COVERED), which decided *that*
  attributes are typed tables and not *which subjects* they reach.

---

### `RL-008` · Three columns in the country-neutral core are named for one country's tax scheme — `hsn_code` on the ledger line, `gst_uqc_code` on the UoM, `itc_treatment` on the reason code — and `D-11` forbids the next jurisdiction module to add its own, so a second country must either overload India's names or commit to base — **MAJOR**

- **What is missing or wrong:**
  - **The ledger line is named for India; everything else is neutral.** The item carries the neutral
    `tax_classification_code` (*"HSN/SAC — a string"*, `DATA-MODEL.md:529`), as do the PO and demand
    lines (`:968`, `:1022`). The **ledger line** snapshots it as **`hsn_code VARCHAR(8)`** (`:701`;
    `PORT…:285`).
  - **The UoM.** `whb_uoms.gst_uqc_code` (`:564`, `V500009`).
  - **The reason code.** `whb_reason_codes.itc_treatment` (`:418`, `V500004`), where ITC is India's
    input-tax-credit concept.
  - **`D-8` allows the hook and `P1-02` defends it.** `D-8` allows *"HSN on the item"* as a hook
    (`DECISIONS.md:210`), and `P1-02` defends `gst_uqc_code` as *"not India-only"*
    (`issues/p1-02.md:111-113`). The objection is to the **name and the cardinality**: one column
    per scheme on a base table, where a scheme-keyed row would do.
- **Why it matters — what breaks later:**
  - **A second jurisdiction has only bad options.** A future `warehouse-<country>` module, a sibling
    of `warehouse-india` under `D-1`, needs the EU CN8/TARIC code (10 digits), the US HTS code (10
    digits), a VAT unit code and a VAT-recovery treatment. `D-11` `B2` and the *zero commits to
    `warehouse-base`* ratchet leave it three: store a TARIC code in a column called `hsn_code` that is
    two characters too short; add columns to base; or skip the snapshot `IRR-42` says is
    unbackfillable.
  - **Renaming later is cheap in the database and expensive everywhere else.** In PostgreSQL a rename
    or a `VARCHAR` widening is catalogue-only. But the column is on the port response, the outbox and
    every export, and `PORT…` §10.2 forbids renaming or repurposing a field.
- **Negative evidence:**
  ```bash
  grep -n "| \`hsn_code\` \|gst_uqc_code\|itc_treatment" docs/DATA-MODEL.md | cut -c1-70
  grep -rn "tax_classification_scheme\|uom_scheme_codes\|tax_treatments" docs/ issues/ | wc -l      # 0
  ```
- **Where it belongs:** `warehouse-base` · **v1** (names) · v2 (second scheme) · **P0/P1**
- **Disposition — the minimum cheap-now change:**
  - **Line:** `V500030` names the snapshot `tax_classification_code VARCHAR(20)` plus
    `tax_classification_scheme VARCHAR(20)` (`HSN` for India), mirroring the item.
  - **UoM:** `V500009` keeps `unece_rec20_code`, which is an international standard, and moves the
    national code into `whb_uom_scheme_codes(uom_code, scheme_code, code)`. India seeds `GST_UQC`
    rows. Alternatively keep `gst_uqc_code` for v1 and **state** that the second scheme goes in the
    side table.
  - **Reason code:** `V500004` moves `itc_treatment`/`statutory_category` into
    `whb_reason_code_tax_treatments(reason_code_id, scheme_code, treatment_code,
    statutory_category)`, seeded by `warehouse-india`.
- **Affected tasks:** `P0-02`, `P0-04`, `P1-02`, `P2IN-03`, `P4-*` (India v2).
- **Irreversibility:** `V500030` for the line name; cheap in the database later, but a wire-contract
  break under §10.2.
- **Relationship to earlier rounds:** **new.** `S-031`/`IRR-42` established the snapshot; `D-8`
  established the hook; neither considered a second scheme.

---

### `RL-009` · The mobile schema file re-closes every registry the web leaves open: `FR-382` is a v1.1 "consideration" while `D-13` puts a mobile counterpart on every v1 screen, and the live schema file carries 36 `z.enum` literals — so an adapter's seed row makes a handheld save fail silently — **MAJOR**

- **What is missing or wrong:**
  - **Web only.** `PC-67`/`FR-380` forbid a TypeScript union over a registry **on the web**.
  - **Mobile is deferred and soft.** The mobile rule is `FR-382`: *"a **mobile-vocabulary
    consideration** on day one, because the mobile schema file is a third copy of every dropdown
    vocabulary and a missing value makes the mobile save fail validation silently"* — versioned
    **v1.1 · P3** (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:678`).
  - **`D-13` requires mobile in v1.** Every v1 screen has its mobile counterpart *"in the same task"*
    (`DECISIONS.md:275-281`), so v1 mobile screens with status, reason-code and movement-type
    pickers are written before the rule exists, and in words that do not rule anything out.
  - **The live pattern is the closed one.** `mobile/src/schemas/common.schemas.ts` carries **36**
    `z.enum` literals, including a re-closed master vocabulary, `companyType: z.enum(['OEM',
    'BRAND', 'SUBSIDIARY', 'DISTRIBUTOR'])` at `:2562`.
- **Why it matters — what breaks later:** `warehouse-adapter-services` seeds a movement type or a
  reason code. The web fetches it and works. The handheld's zod schema refuses it, silently, per
  `FR-382`'s own words. And handhelds are updated on an MDM schedule, not a server schedule, so even
  a corrected schema lags every new seed row by a release cycle. The loose-coupling claim is then
  true on the server and false on the device the operators actually use.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git2/workspace/classic
  grep -c "z.enum" mobile/src/schemas/common.schemas.ts          # 36
  grep -n "companyType: z.enum" mobile/src/schemas/common.schemas.ts | cut -c1-80   # :2562
  cd -; grep -n "^| \*\*FR-382\*\*" docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md | grep -o "mobile | v1.1 | P3"
  ```
- **Where it belongs:** `mobile` · **v1** · **P0**
- **Disposition — the minimum cheap-now change:**
  - `FR-382` is re-versioned **v1 · P0** and reworded from *consideration* to rule: *"a
    registry-backed field is `z.string().min(1)` validated against the fetched dropdown list, never a
    `z.enum`; a `z.enum` literal containing a seeded registry code fails CI."*
  - `PC-67` gains the same sentence for mobile.
  - `P0-16`'s mobile section cites it; the six tasks already citing `FR-382` inherit it.
- **Affected tasks:** `P0-16`, `P0-04`, `P1-02`, `P1-19`, `P2-03`, `P3-01`, `P3-04`.
- **Irreversibility:** reversible in code. **Not** reversible in the field: every handheld build
  shipped with an enum keeps it until the device is updated.
- **Relationship to earlier rounds:** **extends** `G-066`/`FR-382` (COVERED), which found the risk and
  placed its remedy a version too late and a word too soft.

---

### `RL-010` · Allocation strategies, allocation rules, putaway rules and negative-stock policies are edited in place, while reservations and putaway tasks record the id of the rule that chose — so `FR-173`'s "why did it pick lot B" points at rules that have since changed — **MAJOR**

- **What is missing or wrong:**
  - **What is recorded.** `whb_reservations` records `allocation_strategy_id`, `allocation_rule_id`
    and `chosen_reason` (`DATA-MODEL.md:828`); `wh_putaway_tasks` records `rule_id` (`:985`).
    `FR-173`: *"The rule and strategy that chose the stock are recorded on the reservation row and
    shown on its detail view"* (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:348`).
  - **What they point at.** `whb_allocation_strategies`, `whb_allocation_strategy_rules` and
    `whb_allocation_rules` (`:829-832`), `wh_putaway_rules` (`:984`) and `whb_negative_stock_policies`
    (`:830`) carry `is_active` and no version, no effective dating and no immutability rule.
    `WS-048`'s editor is a *"child editor over the rule rows"* (`issues/p2-07.md:64`).
  - **The set already versions its other rule-shaped objects:**
    - `whb_valuation_policies`: effective-dated (`:855`)
    - `whb_gl_posting_rules`: effective-dated (`:859`)
    - `whb_kit_definitions`: versioned (`:542`)
    - `wh_print_template_versions`: *"a label layout is never edited in place"* (`:1037`)
    - `wh_carrier_status_mappings`: `effective_from` (`:1048`)
- **Why it matters — what breaks later:** a supervisor changes the `FAST_MOVERS` strategy from FEFO
  to FIFO on Tuesday. Monday's reservations still say `allocation_strategy_id = FAST_MOVERS`, and the
  detail view `FR-173` promises now explains Monday's pick with Tuesday's rules. `chosen_reason` is a
  sentence, not the rule set. The same is true of every putaway override audit and every
  negative-stock decision. When the v3 slotting and replenishment engines (`IRREVERSIBLE.md:727`)
  arrive and try to learn from history, the rules that produced that history are gone.
- **Negative evidence:**
  ```bash
  sed -n '829,832p;984p' docs/DATA-MODEL.md | grep -c "effective_from\|version_no\|supersedes"   # 0
  grep -n -i "version\|effective\|immutable" issues/p2-07.md | wc -l                              # 0
  ```
- **Where it belongs:** `warehouse-base` + `warehouse` · **v1** · **P0/P2**
- **Disposition — the minimum cheap-now change:** **a rule row referenced by any reservation or task
  is immutable**, enforced by a trigger in `I-9`'s shape.
  - An edit is copy-on-write: a new row with `version_no` and `supersedes_id`, and the old row
    deactivated.
  - The recorded id therefore always resolves to the rules that actually ran.
  - This applies to all three allocation tables in `V500033`, to `wh_putaway_rules`, and to
    `whb_negative_stock_policies` in `V500031`.
  - `WS-048` shows the version history.
- **Affected tasks:** `P0-09` (`V500033`), `P2-07`, `P1-15` (putaway rules), `P0-03`/`P0-02`
  (negative-stock policy, `V500031`), and `RA-008`'s new approval-policy table.
- **Irreversibility:** reversible as a trigger; **not** reversible for the explanations lost to
  in-place edits before it lands.
- **Relationship to earlier rounds:** **new.** `Z-001` fixed the *resolution* shape of these ladders;
  this is their *history*.

---

### `RL-011` · Only the ledger is partitioned; the outbox (billable granularity, above the ledger's own million rows a day), the inbound-message log, the delivery log, the batch results, the daily position snapshot and the audit chain are created as plain heaps — and `IRR-62`'s own argument says a later conversion has no window — **MAJOR**

- **What is missing or wrong:** `FR-022` and `IRR-62` partition `whb_stock_movements`/`_lines` from
  the first migration because *"migrations in this repo are baked into the backend image at build
  time … a partition conversion has no comfortable window"* (`IRREVERSIBLE.md:156`). The same
  argument applies to six more tables, none of them partitioned:
  - `whb_outbox` (`DATA-MODEL.md:879`): one row per receipt line, putaway, pick line, carton and
    task, on top of one per movement. `FR-422` sizes the ledger alone at *"one million ledger rows a
    day at peak"* (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:742`).
  - `whb_inbound_messages` (`:876`): a `TEXT` payload per request.
  - `whb_outbox_deliveries` (`:881`): one row per attempt.
  - `whb_movement_batch_results` (`:878`).
  - **`whb_stock_position_snapshots`** (`:805`): one row per position per day. At `FR-422`'s five
    million live positions that is up to 5,000,000 × 365 = **1.825 billion rows a year** if every
    position is snapshotted (fewer if only non-zero ones are, which the row does not state).
  - `whb_audit_events` (`:920`): an install-wide hash chain.
  - `wh_shipment_tracking_events` (`:1047`, v2): a raw `TEXT` payload per carrier event.

  `FR-434` names *"unbounded log tables"* as one of nineteen failure modes the ratchet exists to
  prevent (`:754`).
- **Why it matters — what breaks later:** the snapshot table is `PNR-3` by its **start date**
  (`DATA-MODEL.md:2918`), so it begins filling on go-live day. By the time v2 storage billing reads
  it, it is the second-largest table in the product, and converting it is the downtime `IRR-62`
  refused for the ledger. The outbox is worse: `PC-46` forbids pruning below the slowest cursor, so
  it only grows, and without partitions *"prune"* is a `DELETE` over hundreds of millions of rows.
  Retention cannot become policy (`Z-006`'s `whb_retention_policies`) on a table that can only be
  deleted from row by row.
- **Negative evidence:**
  ```bash
  grep -n "PARTITION BY" docs/DATA-MODEL.md | cut -c1-70          # ledger only (header + lines)
  grep -n "Not partitioned" docs/DATA-MODEL.md | cut -c1-60        # :750 positions — correctly, bounded by grain
  ```
- **Where it belongs:** `warehouse-base` · **v1** · **P0**
- **Disposition — the minimum cheap-now change:** partition at `CREATE`, reusing `P0-02`'s
  partition-creation job.
  - `whb_stock_position_snapshots` `PARTITION BY RANGE (snapshot_date)`, monthly, in `V500045`.
  - `whb_outbox` by `recorded_at`, monthly; the PK becomes `(cursor, recorded_at)` and the gapless
    cursor still comes from its sequence (`V500040`).
  - `whb_inbound_messages`, `whb_movement_batch_results` and `whb_outbox_deliveries` by their
    received/attempted timestamp (`V500040`, `V500041`).
  - `whb_audit_events` by `occurred_at`, PK `(sequence_no, occurred_at)` (`V500043`).
  - Each gets a retention-class row in `whb_retention_policies`, so disposal becomes dropping a
    partition. The snapshot row states whether zero positions are snapshotted.
- **Affected tasks:** `P0-11` (`V500040`), `P0-08` (`V500041`), `P0-13` (`V500043`), `P0-03`
  (`V500045`), `P4-09` (retention), `P5-*` (tracking events).
- **Irreversibility:** **re-keying under downtime once populated.** The snapshot's first-day content is
  `PNR-3`.
- **Relationship to earlier rounds:** **new.** `Z-006` covers the ledger's archive and disposal;
  `RD-002` covers an HTTP subscription pinning outbox retention. Neither asks how the non-ledger
  tables are stored.

---

### `RL-012` · `OD-3`'s one technical consequence — "every mapping profile, import template, label template and reason-code catalogue must be exportable and importable" — is restated in three documents and two tasks and built for mapping profiles only — **MAJOR**

- **What is missing or wrong:**
  - **The consequence is stated.** `OD-3` keeps one database per customer (`DECISIONS.md:331`) and
    names its consequence: *"the second customer is a different database, so every mapping profile,
    import template, label template and reason-code catalogue must be **exportable and
    importable**"* (`PLATFORM-DEPENDENCIES.md:505-507`; `OPEN-DECISIONS-RESOLVED.md:683-684`).
  - **Two tasks restate it as a Trap.** `issues/p3-18.md:51-53` and `issues/p5-01.md:114-115`.
  - **One task builds a slice of it.** `P3-18` builds exportable **migration mapping profiles** only
    (`:12`), in v1.1.
  - **Nothing exports the rest.** No task exports the fifteen registries, print templates and their
    versions, allocation strategies, putaway rules, attribute keys, number-series definitions, alert
    rules or `admin_settings` warehouse keys.
- **Why it matters — what breaks later:** every go-live after the first is hand-built.
  - **Consistency.** The implementer re-keys dozens of reason codes, statuses, location types and
    templates per customer, and customer 2's `DMG` means something different from customer 1's.
  - **Upgrades.** A fix to a seeded template or strategy reaches existing installs only as a
    migration, and install-edited rows diverge silently.
  - **No template installs.** A "golden install" for a vertical (dealer parts, 3PL) cannot exist.
- **Negative evidence:**
  ```bash
  grep -rln -i "exportable and importable" issues/ | xargs -n1 basename     # p3-18.md p5-01.md — both as Traps
  grep -n "exportable and importable" issues/p3-18.md | cut -c1-60           # :12 (mapping profile) · :52 (the Trap)
  grep -rn -i "configuration package\|config export" docs/ issues/ | wc -l  # 0
  ```
- **Where it belongs:** `warehouse-base` · **v1** (the one rule) · **v1.1** (the build) · P0/P3
- **Disposition — the minimum cheap-now change:**
  - **v1 (one sentence in `P0-04`):** install-created configuration rows carry `owning_module =
    'INSTALL'`, so an export can tell install configuration from module seed. Every configuration
    table keeps a stable `code` (`IRR-26` already requires it).
  - **v1.1 (a build, recorded so it is not lost):** a *configuration package* export and import on
    the existing handler-registry import framework (`whb_import_batches`, `FR-416`). There is one
    `import_kind` per configuration object, the upsert is keyed on `code`, and `is_dry_run` gives a
    diff. Owner: `P3-18`, whose header gains the configuration kinds beside mapping profiles.
- **Affected tasks:** `P0-04`, `P0-10` (`V500046`), `P3-18`, `P5-01`.
- **Irreversibility:** reversible. The cost of not doing it is linear in installs.
- **Relationship to earlier rounds:** **new as an owned gap.** `S-080` produced the sentence; `OD-3` is
  escalated and is **not** re-opened here. This files only the unowned consequence.

---

### `RL-013` · Code-keyed foreign keys are declared `ON UPDATE CASCADE` "so a correction must propagate" — into an append-only, partitioned ledger whose `I-2` trigger refuses the cascade, against a contract that forbids renaming a code — **MINOR**

- **What is missing or wrong:**
  - **The rule.** `DATA-MODEL.md:132`: *"Natural-key parents referenced by `code` (every catalogue,
    `whb_uoms`, `currencies`) | `ON UPDATE CASCADE` — the key *is* the value, so a correction must
    propagate."*
  - **The contract says the opposite.** `PORT…:1669`: *"Rename a catalogue `code` — **no**. Posted
    history references it. Deactivate the row and seed a new one."* `BUILD-SPEC-SCREENS.md:742` makes
    the registry `code` immutable.
  - **The ledger refuses it anyway.** The ledger's `movement_type_code`, `source_system`,
    `source_document_type`, `stock_status_code`, `uom_code` and `base_uom_code` are code FKs in
    `V500030`, and `I-2` refuses every `UPDATE` to a posted line.
- **Why it matters — what breaks later:** the clause is either dead or harmful. On any used code the
  cascade reaches a posted line and fails inside a master-screen save as `I-2 violated`, an opaque
  500. On an unused code it succeeds and rewrites nothing. It is the one place in the schema that
  invites exactly the edit three other documents forbid, and it is written in the `PNR-1` file.
- **Negative evidence:** `sed -n '132p' docs/DATA-MODEL.md`; `sed -n '1669p' docs/PORT-AND-ADAPTER-CONTRACT.md`.
- **Where it belongs:** `warehouse-base` · **v1** · **P0**
- **Disposition — the minimum cheap-now change:** `DATA-MODEL.md:132` becomes **`ON UPDATE RESTRICT`**
  for every code-keyed FK. A code is corrected by `Z-005`'s retire-and-reseed. `Z-004`'s *Frozen
  when* column gains registry `code` = `once any row references it`.
- **Affected tasks:** `P0-02`, `P0-04`, `P0-05`, `P1-02`.
- **Irreversibility:** the clause is written in `V500030`. Changing an FK action later is a
  constraint rebuild across every partition.
- **Relationship to earlier rounds:** **new**; the one-line residue of `Z-005`'s retirement fix.

---

### `RL-014` · Document status ladders are closed by design and have no extension point: no generic status-changed event and no pre-transition hook, so a customer's extra approval gate is a fork — **MINOR**

- **What is missing or wrong:** PO, GRN, demand-order, shipment, transfer and task statuses are
  closed product vocabularies, legitimately (`OD-5`). But `PC-42`'s event catalogue
  (`PORT…:796-810`) emits billable-grain facts only; there is no `po.approved`, no
  `demand_order.released` and no `transfer.dispatched`. There is also no guard SPI through which an
  adapter or install can veto a transition. The set already owns the right shape: `PC-04`'s
  `List<T>` bean registry, which `FR-357` uses for resolvers.
- **Why it matters — what breaks later:** the most common implementation request in a stock system
  is *"add a second approval before release above ₹X for client Y"* or *"tell our ERP when the PO is
  approved"*. Today each is a change inside `warehouse`. The design's own adapter model can express
  neither.
- **Negative evidence:** `grep -rn "status_changed\|TransitionGuard" docs/ issues/ | wc -l` → 0.
- **Where it belongs:** `warehouse` · **v1.1** · P3
- **Disposition — a v1.1 build, recorded:**
  - One generic outbox event, `document.status_changed` (`document_type`, `document_id`,
    `from_status`, `to_status`, actor), emitted by the single transition helper.
  - A `WhTransitionGuard` `List<T>` SPI consulted before every transition; base ships none.
  - The event code joins `RL-002`'s registry in v1 so the grain is fixed early.
- **Affected tasks:** `P0-11` (event code), `P3-*` (state machines, with `H-004`).
- **Irreversibility:** additive.
- **Relationship to earlier rounds:** **adjacent to `H-004`**, which finds no enumerated state machine
  for 31 P3–P6 status tables. This is the hook, not the machine.

---

### `RL-015` · Registry rows carry a single-language `name`, so install-created reason codes, statuses and location types — and every document printed from them — have one language, while platform already translates menus by row — **MINOR**

- **What is missing or wrong:** the registry shape has one `name VARCHAR(255)` (`DATA-MODEL.md:262`).
  `PC-69` falls back to that name when an i18n key misses (`PORT…:1231-1233`), which is correct for a
  **seeded** row with a key. An **install-created** row (`RL-012`'s `owning_module = 'INSTALL'`) has
  no key at all. Warehouse ships `en`/`fr`/`hi` from the first file (`MODULE-INTEGRATION.md:1091`),
  and the platform precedent for translating data rows exists: `menu_translations`, which `V501010`
  already writes (`DATA-MODEL.md:2944`).
- **Why it matters — what breaks later:** a Hindi-first store's reason codes render in whatever
  language the administrator typed on every screen, handheld and printed delivery document. A
  bilingual print layout (a regional-language challan) has nothing to bind to.
- **Negative evidence:** `grep -rn "registry_translations\|name_translations" docs/ issues/ | wc -l` → 0.
- **Where it belongs:** `warehouse-base` · **v2** · P4/P5
- **Disposition — a v2 build, recorded:** `whb_registry_translations(registry_table, code, locale,
  name)` mirroring `menu_translations`, read by `PC-69`'s fallback before the row's own name. Nothing
  is needed in v1 beyond `code` stability, which `RL-013` secures.
- **Affected tasks:** `P0-04` (fallback order), `P2-14` (template bindings).
- **Irreversibility:** additive.
- **Relationship to earlier rounds:** **new.**

---

### `RL-016` · Every time-driven rule in the product reads the wall clock, and nothing specifies an injectable clock — so expiry, reservation TTL, period generation, the snapshot day boundary and SLA clocks cannot be walked deterministically — **MINOR**

- **What is missing or wrong:** the v1 time-driven rules include:
  - reservation expiry (`expires_at`, `DATA-MODEL.md:828`)
  - the expiry sweep (`FR-160`)
  - period generation (`RE-001`)
  - the daily snapshot's day boundary per site (`FR-439`)
  - the partition-creation job
  - `occurred_at <= recorded_at + 5 minutes` (`:2730`)
  - claim windows (`:1081`)

  No document names a `java.time.Clock` bean or forbids `Instant.now()`/`LocalDate.now()` in
  business code, and neither platform nor accounting-base has a precedent to copy.
- **Why it matters — what breaks later:** `SCENARIO-CATALOGUE.md`'s time-driven scenarios (TTL,
  expiry, soft close, month-end partition) can then only be walked by waiting or by editing rows. An
  append-only ledger forbids the latter. The first boundary bug (the 23:59 IST posting that lands in
  the next UTC month) is found in production.
- **Negative evidence:**
  ```bash
  grep -rn "java.time.Clock\|Clock bean\|fixed clock" docs/ issues/ | wc -l        # 0
  cd /Users/bbhushan/work/git2/workspace/classic
  grep -rln "Clock.systemUTC\|Clock.systemDefaultZone\|@Bean.*Clock" --include=*.java platform/backend/src/main/java accounting-base/backend/src/main/java | wc -l   # 0
  ```
- **Where it belongs:** `warehouse-base` · **v1** · **P0**
- **Disposition — the minimum cheap-now change:** one line in **`P0-13`**. Every warehouse service
  takes an injected UTC `Clock`, and the module's `ArchitectureInvariantsTest` gains a scanner that
  fails on a bare `Instant.now()`, `LocalDate.now()` or `LocalDateTime.now()` under
  `ai.warehouse*`, with the `ScannerIntegrity` self-test. `recorded_at` is set from that clock, so the
  `:2730` `CHECK` stays consistent under test.
- **Affected tasks:** `P0-13`, `P0-01` (module skeleton test).
- **Irreversibility:** reversible, but retrofitting a clock into fifty services is a sweep.
- **Relationship to earlier rounds:** **new.** `K-001` is the job execution contract; this is the time
  source beneath it.

---

### `RL-017` · Only the port is versioned; the management API that long-lived handheld apps call is not, and `whb_devices.app_version` is recorded with no minimum-version rule — so the first renamed response field breaks every handheld not yet updated — **MINOR**

- **What is missing or wrong:** `PC-75` versions the port by path and `PORT…` §10.2 makes it
  additive-only. Every mobile screen (`D-13`) and every v1.1 RF flow reads the **management**
  endpoints (`/warehouse/<resource>`, `MODULE-INTEGRATION.md:563-568`), which carry neither rule.
  `whb_devices.app_version` exists (`DATA-MODEL.md:909`, v1.1) and nothing reads it.
- **Why it matters — what breaks later:** handhelds are MDM-managed and lag the server by weeks. A
  field renamed for the web in a P3 release breaks every scan gun on the floor that morning, and a
  handheld on the wrong build cannot be told to update. It just misbehaves.
- **Negative evidence:** `grep -rn -i "min_app_version\|minimum app\|X-Client-Version" docs/ issues/ | wc -l` → 0.
- **Where it belongs:** `warehouse` + `mobile` · **v1.1** · P3
- **Disposition — a v1.1 rule, recorded:**
  - `PORT…` §10.2's additive-only table is extended to **every endpoint a mobile screen calls**, and
    each such endpoint is marked in `BUILD-SPEC-SCREENS.md`'s mobile block.
  - An `admin_settings` key `warehouse.mobile.min_app_version` is checked at login and sync, with a
    named `426 CLIENT_UPGRADE_REQUIRED` error.
  - `whb_devices.app_version` is what the device grid filters on.
- **Affected tasks:** `P0-16` (mobile §4), `P3-04`, `P3-01`.
- **Irreversibility:** additive.
- **Relationship to earlier rounds:** **new.** `RD-003` is the offline queue on the same device.

---

## §2.1 · Summary — deadline, one-way doors, tasks

| Finding | Sev | One-way door? | Deadline | Version | Tasks |
|---|---|---|---|---|---|
| `RL-001` | **BLOCKER** | **yes**: partitioned ledger column + position key | `V500005`/`V500021`/`V500030` | v1 | `P0-05` `P0-02` `P0-17` `P2-01` `P2-16` `P4-07` `P2IN-03` |
| `RL-002` | **BLOCKER** | **yes**: from the first emitted event (`FR-331`) | `V500040` | v1 | `P0-11` `P0-12` `P3-22` `P0-05` `P5-03` |
| `RL-003` | MAJOR | **yes** once a colliding code is posted | `V500004`, then each adapter's first migration | v1 | `P0-04` `P0-05` `P1-02` `P1-08` `P2-25` |
| `RL-004` | MAJOR | printed labels | `V500012`–`V500020` | v1 | `P1-05` `P1-06` `P1-01` `P1-07` `P1-08` `P1-09` `P0-05` |
| `RL-005` | MAJOR | refused rows never recorded | `V500016` | v1 | `P1-02` `P1-12` `P1-13` `P2-25` |
| `RL-006` | MAJOR | ledger four at `V500030` | `V500030`; app tables per task | v1 | `P0-02` `P0-05` `P1-02` `P1-05` `P2-07` `P2-14` `P2-25` `P3-24` |
| `RL-007` | MAJOR | **yes**: line side table `PNR-1`; lot facts `PNR-3` | `V500010`/`V500030` | v1 (shape) · v3 (screens) | `P0-05` `P0-02` `P0-11` `P1-02` `P1-07` `P1-08` |
| `RL-008` | MAJOR | wire contract | `V500004`/`V500009`/`V500030` | v1 · v2 | `P0-02` `P0-04` `P1-02` `P2IN-03` |
| `RL-009` | MAJOR | shipped handheld builds | before the first v1 mobile screen | v1 | `P0-16` `P0-04` `P1-02` `P1-19` `P2-03` `P3-01` `P3-04` |
| `RL-010` | MAJOR | lost explanations | `V500031`/`V500033` | v1 | `P0-09` `P2-07` `P1-15` `P0-03` |
| `RL-011` | MAJOR | re-keying under downtime | `V500040`–`V500045` | v1 | `P0-11` `P0-08` `P0-13` `P0-03` `P4-09` |
| `RL-012` | MAJOR | no | `P0-04` (rule) · `P3-18` (build) | v1 · v1.1 | `P0-04` `P0-10` `P3-18` `P5-01` |
| `RL-013` | MINOR | constraint rebuild | `V500030` | v1 | `P0-02` `P0-04` `P0-05` `P1-02` |
| `RL-014` | MINOR | no | `P0-11` (event code) | v1.1 | `P0-11` `P3-*` |
| `RL-015` | MINOR | no | — | v2 | `P0-04` `P2-14` |
| `RL-016` | MINOR | no | `P0-13` | v1 | `P0-13` `P0-01` |
| `RL-017` | MINOR | no | before `P3` RF flows | v1.1 | `P0-16` `P3-04` `P3-01` |

**Seven of the seventeen bind at or before `V500030`** (`RL-001`, `RL-003` via `V500004`, `RL-006`,
`RL-007`, `RL-008`, `RL-013`, and `RL-004` via `V500012`–`V500020`). `V500022`–`V500029` is the
declared landing gap for a forgotten prerequisite (`DATA-MODEL.md:2904`). `RL-001`'s registry could
also land there, but `V500021`'s cost-layer FK means it must precede `V500021`, which is why the
recommendation is `V500005`.

---

## §3 · What I checked and found sound

Listed so round 5 does not re-walk this ground.

| What I went looking for | Where it is covered |
|---|---|
| **The fourteen registries' shape and guard** | §1.8 shape, `owning_module` opaque, `I-18` test, `PC-66` seed-only extension, `PC-72` assertion 4. The design is right; `RL-001`/`RL-006` are about what it does not reach |
| **Generic references with no registry** | `DATA-MODEL.md` §3.3: fifteen generic references, each with a registry-typed discriminator or a named guard; `G6`'s bare UUID is stated and justified |
| **Port evolution** | `PC-75` path versioning, never branching on `source_system`; §10.2 additive table; §10.3 four-step deprecation with per-`source_system` usage counts; §10.6 the four unrecoverable wire decisions |
| **Port leaking vertical concepts** | one envelope (`PC-06`); the header's *deliberately not* list; `B4`'s import ban including `ai.accessories`; price, tax and carrier kept off the wire |
| **Adapter plug-in model** | sibling packages (`D-1`); `warehouse-adapter-example` fixture (`PC-73`); two real adapters in v1; the honest *zero commits to base, never to platform* caveat (`PC-74`) |
| **Statutory-provider plug-in** | `whin_compliance_providers` + environments + credentials, vendor-agnostic (`INDIA-LOCALISATION-PACK.md:1233-1237`) |
| **Channel plug-in** | `FR-207`: each connector an adapter, base never names a vendor |
| **Timezone** | `FR-439` v1/P0, `whb_warehouses.timezone`, local-day bucketing in `p1-12.md:92` and `p1-05.md:166` |
| **UoM** | per-item conversion, frozen `conversion_factor_used`, base-UoM trigger `I-9`, catch weight reserved |
| **Deletion** | `RESTRICT` + service check, `is_active` on masters only, no second deletion mechanism (`DATA-MODEL.md:110-132`) |
| **Owner vs tenant** | `D-5`: a 3PL's clients are an owner dimension in every install |
| **Module toggles** | `ENABLE_*` relaxed binding, the base OR-ing every consumer flag, sibling-package scan trap spelled out (`MODULE-INTEGRATION.md` §8–9) |
| **Versioned config done right** | print templates never edited in place (`:1037`); valuation and GL rules effective-dated; carrier status mappings reinterpretable (`:1048`) |
| **Display resolver fallback** | `FR-357`: a base-only install renders raw ids, never blanks |

---

## §4 · Refused

Candidates I declined, with the finding that already owns each. Per the governing rule, a
restatement is worse than no finding.

1. **`whb_items.variant_axis_1/2/3_value_id` is numbered-column polymorphism: a fourth apparel axis
   (waist × length × colour × fit) is an `ALTER`.** A scalar-vs-M:N choice → **R22**, by the brief.
   Noted so it is not lost.
2. **Conversion factor, packaging level, `category_id`, `lot_control_mode` edited in place; offline
   replay resolving today's factor.** → **`Z-004`**'s *Frozen when* column, which also closes the
   offline case (a frozen factor cannot differ between capture and post). One addition for `Z-004`'s
   list: **`whb_locations.parent_location_id`**, since `IRREVERSIBLE.md:548` states *"reparenting
   later silently rewrites historical zone reports"* and nothing forbids it.
3. **No catalogue value can be retired.** → **`Z-005`**. `RL-013` files only the `ON UPDATE CASCADE`
   residue.
4. **Webhook signing, status ladder, timeout, TLS.** → **`RD-002`**. `RL-002` is the event schema
   and version, and recommends landing both in one migration.
5. **Carrier connectors have no adapter contract.** → **`RD-005`**.
6. **The offline queue drops scans.** → **`RD-003`**.
7. **Multi-currency costing.** → **`OD-16`** / **`RF-004`**.
8. **Shared multi-tenancy.** → **`OD-3`**, escalated. `RL-012` files only its unowned technical
   consequence.
9. **Ledger archive cut-off and disposal.** → **`Z-006`**. `RL-011` is the non-ledger tables.
10. **Registry seed lists missing.** → **`RE-005`**.
11. **Disabling a module leaves menus live.** → **`RE-008`**.
12. **Out-of-process port authentication.** → **`OD-8`**.
13. **Print template body language, bindings, escaping.** → **`RD-006`**. `RL-006` is only whether
    the kinds and formats are open.
14. **Job execution contract.** → **`K-001`**. `RL-016` is the clock beneath it.
15. **`occurred_at` below the oldest partition.** → **`K-006`**.
16. **Most-specific-first ladders unexpressible.** → **`Z-001`**. `RL-010` is their history, not
    their resolution.

---

## §5 · Counts

```bash
cd /private/tmp/claude-501/-Users-bbhushan-work-git2-workspace-classic/caed8239-abcc-4985-bfe7-ea4688ad865e/scratchpad/warehouse-issues/docs/reviews
grep -cE '^### `RL-[0-9]{3}`' R26-extensibility-and-future-proofing.md                    # 17
grep -E '^### `RL-' R26-extensibility-and-future-proofing.md \
  | grep -oE '\*\*(BLOCKER|MAJOR|MINOR)\*\*$' | sort | uniq -c
#   2 **BLOCKER**
#  10 **MAJOR**
#   5 **MINOR**
```

| Severity | Count | Findings |
|---|---|---|
| **BLOCKER** | 2 | `RL-001` `RL-002` |
| **MAJOR** | 10 | `RL-003` `RL-004` `RL-005` `RL-006` `RL-007` `RL-008` `RL-009` `RL-010` `RL-011` `RL-012` |
| **MINOR** | 5 | `RL-013` `RL-014` `RL-015` `RL-016` `RL-017` |
| **Total** | **17** | |

**Axis arithmetic:** 23 axes walked · 9 `SOUND` (fully or in part) · 12 `HOLED` · 3 `BROKEN` · 7
`OWNED` by an earlier finding or by R22. An axis can carry two verdicts; the table in §1.1 is the
authority.

**By version:** v1 schema/rule — 13 (`RL-001`–`RL-011`, `RL-013`, `RL-016`) · v1.1 builds — 3
(`RL-012`'s build half, `RL-014`, `RL-017`) · v2 — 1 (`RL-015`). **One-way doors:** `RL-001`, `RL-002`,
`RL-007` (line side table) outright; `RL-003`, `RL-004`, `RL-005`, `RL-011` once data exists.

**Prefix allocation check, run before writing:**

```bash
grep -rohE "\bRL-[0-9]{1,3}\b" docs/ issues/ tools/ | wc -l     # 0 before this file existed
```

**Owed, not done here (this file edits no other).** `DECISIONS.md` §6 needs a register row
`RL-001 … RL-017 | reviews/R26`, and `tools/check-design-set.py`'s `REVIEWS`/`FINDING_DEF_RE` need the
`RL` prefix, exactly as round 3 did for `RA-`…`RF-`. **New ids proposed:** tables
`whb_duty_statuses`, `whb_event_types`, `whb_code_lists`/`whb_code_list_values`,
`whb_entity_attribute_values`, `whb_uom_scheme_codes`, `whb_reason_code_tax_treatments` (v1) and
`whb_registry_translations` (v2). **No migration version is invented**: each rides an existing
allocation (`V500004`, `V500005`, `V500009`, `V500010`, `V500016`, `V500030`, `V500031`, `V500033`,
`V500040`–`V500045`). The only new DDL beyond those tables is the partition clauses of `RL-011` and
the key changes of `RL-004`/`RL-005`, all in migrations not yet written.
