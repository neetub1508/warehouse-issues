# R16 — role and persona completeness

<!-- check-design-set: screen-citations file WS-238 — the BUILD-SPEC-SCREENS.md §1 next-free allocation marker (X-001), the same one R9, R10, GAP-REGISTER.md, GAP-REGISTER-R2.md and DESIGN-SET-DEFECTS.md declare. RA-001 and RA-002 propose taking it and the id after it; by definition neither has an index row yet -->

**Date** 2026-09-02 · **Prefix** `RA-` · **Branch** `docs/round-3-functional-completeness`

**File set read — 23 files.**

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues
# docs/ (10): DECISIONS.md · WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md · BUILD-SPEC-SCREENS.md
#             SCENARIO-CATALOGUE.md · DATA-MODEL.md · PORT-AND-ADAPTER-CONTRACT.md
#             GAP-REGISTER.md · GAP-REGISTER-R2.md · DESIGN-SET-DEFECTS.md · IMPLEMENTATION-PLAN.md
# docs/reviews/ (4): R10 R11 R12 R13   (read first, per the brief's governing rule)
# issues/ (8): p0-13 p0-15 p1-05 p1-18 p2-01 p2-09 p2-15 p2-25
# classic (1): platform/backend/src/main/resources/db/migration/V150__create_branch_staff_table.sql
grep -rohE "\bRA-[0-9]{1,3}\b" docs/ issues/ | wc -l        # → 0   (the prefix is free)
```

**Method, in three sentences.** I took the eight human actors the FRD names
(`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:84-90`), added the five the set *implies* but does not name —
packer, QA inspector, gate/dock coordinator, counter clerk, IT administrator — and walked each one
through a **shift**, not through a document: every screen they open in order, every permission they
must hold, every signal that starts their work, every enquiry that informs a decision, and the
handoff that carries their work to the next person. Where R10 walked ten *orders* through the
building and R11 walked 61 *exceptions*, this lens asks the orthogonal question — *can this person
finish their day, and does anything they are granted let them do something they must not* — which is
why five of the eight findings below sit on screens both of those lenses marked ✔ or SPEC. Every id
was opened and read before it was cited, and every absence prints the command that established it.

---

## §1 · Verdict

**The set designs objects and documents superbly and designs *people* by implication.** Eleven actors
are tabulated in one place in the FRD and then never resolve into anything a migration can seed, a
screen can grant, or a test can assert. Round 2's `Z-010` found the outline of this — *"not one
operational role is seeded"* — and its remedy is now folded into `P0-15` as four starting bundles.
**Nobody has audited that remedy**, because round 2 wrote it, and it does not survive contact with the
set's own permission tables: the Storekeeper bundle is specified as a **four-verb deny-list**
(`no :approve, no :reverse, no :close, no :override`) against a **sixty-verb** authority space, so it
silently grants the QC release gate, the blocked-movement force, the hold release and the reservation
release; and the four bundles cover **four of the eight human actors**, leaving `mgr1` and `fin1` —
the named actors of nine v1·P0 acceptance scenarios between them — mapped to nothing at all.

**Two roles cannot finish a v1 day.** The **administrator** cannot grant warehouse-scoped access,
because `FR-405`'s predicate has **no table, no screen and no migration** — `P1-18`'s own header reads
*Migrations **none** · Screens **none*** — while `whb_owner_grants` gets both for the owner axis; the
site-closure pre-check in `P1-05` nonetheless enumerates *"warehouse-scoped user grants"* as a
blocking class with *"a count and a link"* to a screen that does not exist, and `WH-SC-243` is
unpassable. The **counter clerk** cannot price a line: `price_level` is a keystroke in a
sub-ten-second bill and a column on `whad_counter_sales`, and there is **no price table anywhere in
the data model** — `retail_price` was deliberately dropped with the words *"a price is the commercial
module's"* — while the only thing that would load one, `whad_price_files`, is **v1.1**.

**Three roles hold an instrument that does not work.** The **auditor** is promised tamper evidence by
`FR-006` and asked by `WH-SC-245` (v1·P0) to open *"the immutability evidence"*; the chain has no
verification action on any screen, no job in `P0-13`'s nine-row dated-obligation register, and the
port contract states in terms that the **feature is v2**. The **warehouse manager** approves
adjustments *"above threshold"* and the threshold has no home — not a column, not an
`admin_settings` key, not a screen — while `P2-01` says only that *"both thresholds live on
configuration"*. The **picker** is offered *"emergency replenish"* on a v1 screen whose entire
mechanism (`wh_replenishment_tasks`, `WS-142`, trigger `SHORT_PICK`) is **v1.1**, so the empty pick
face stays empty for the next picker.

**And one boundary is defined twice.** `PORT-AND-ADAPTER-CONTRACT.md` `PC-31` and
`BUILD-SPEC-SCREENS.md` §10.2 are two authorities for the same v1 permissions and they disagree:
**six of `PC-31`'s ten strings appear nowhere in the screen spec**, four of them being the port's name
for a gate §10.2 already names differently. `P0-15` seeds one namespace. The integration principal
and the device — two of the three system actors — authenticate against the other.

The good news is that none of this is deep. Seven of the eight findings are a seed row, a column, a
screen block or a sentence in a task file, all before their point of no return. The eighth
(`RA-001`) is a small table and a small screen, and it is `P1`.

---

## §1.1 · Coverage table

Sixteen roles walked — the FRD's eight persons, its three system principals, and five the set names
only in prose. **Verdict key:** `COMPLETE` = every screen, permission, signal, enquiry and handoff of
a full shift exists at the version the role needs it · `HOLED` = the shift completes with a named
hole already owned by an earlier lens · `BROKEN` = the role cannot finish its day · `v2` = the role's
whole surface is a stated later version and nothing in v1 depends on it.

| # | Role | FRD actor row | Seeded bundle | Shift verdict | Finding |
|---|---|---|---|---|---|
| 1 | **Storekeeper / receiving clerk** (`stores1`) | `:84` | Storekeeper | **HOLED** — receives, inspects, puts away and counts on v1 screens; blind at both ends (`U-004` arrival, `U-002` who-is-told), and over-granted | `RA-003` |
| 2 | **Picker** (`stores2`) | `:84` (same row) | Storekeeper | **HOLED** — picks on `WS-102`; the third of three short-pick actions has no v1 mechanism | **`RA-006`** |
| 3 | **Packer** | *(none — implied by `FR-190` `FR-206`)* | none | **BROKEN** — already `U-001`; **refused, not re-filed** | `U-001` |
| 4 | **QA inspector** | *(none — implied by `wh_quality_inspections:disposition`, "QA-role gated")* | none | **BROKEN as a boundary** — the gate exists and the role that must hold it does not; the Storekeeper bundle is not written to exclude it | **`RA-003`** |
| 5 | **Shift supervisor** (`sup1`) | `:85` | Supervisor | **HOLED** — `U-002` owns the morning; the bundle inherits every over-grant of item 1 | `RA-003` |
| 6 | **Stock controller / cycle-count auditor** (`inv1`) | `:87` | Stock Controller | **COMPLETE** — the best-served persona in the set (`WS-093`/`094`/`095`, blind counts, tolerance, `FR-408` self-approval bar) | — |
| 7 | **Warehouse manager** (`mgr1`) | `:86` | **none** | **BROKEN** — no bundle; the approval threshold that defines the role has no home; the soft-close permission the scenario names is not in the spec | **`RA-003`** `RA-007` `RA-008` |
| 8 | **Buyer / parts manager** | `:88` | none | **COMPLETE** — `WS-072` carries `overdueOnly`, an *open POs · overdue · value on order* strip and a `WS-141` suggestion→PO conversion. No finding |
| 9 | **Counter clerk** (dealer adapter, v1) | *(none — implied by `FR-359`)* | none | **BROKEN** — cannot price a line | **`RA-002`** |
| 10 | **Finance controller** (`fin1`) | `:89` | **none** | **HOLED** — reads `WS-219`/`WS-052`/`WS-211` fine; closes the period on one pre-check and strands every in-flight approval | **`RA-004`** |
| 11 | **External auditor** (`aud1`) | `:90` | platform AUDITOR (`P0-15`) | **HOLED** — five of the six reads `WH-SC-245` demands exist; the sixth, *the immutability evidence*, does not | **`RA-005`** |
| 12 | **IT administrator / implementer** | *(none)* | ADMIN | **BROKEN** — cannot grant site scope to anyone | **`RA-001`** |
| 13 | **Transport / dock coordinator** | *(none)* | none | **HOLED** — `U-004` (arrival), `X-027` (gate pass); **refused, not re-filed** | `U-004` |
| 14 | **3PL billing clerk** | *(none)* | none | **v2** — `WS-158`…`WS-163` + `H-001`'s 25 verbs; nothing in v1 depends on it | — |
| 15 | **3PL client portal user** | `:91` | 3PL Client | **v2** — `WS-172` + `wh3_clients:portal_access`; the v1 half (`whb_owner_grants`, `WS-020`) exists and is sound | — |
| 16 | **Integration principal · device · scheduler** | `:92-94` | n/a | **HOLED** — authenticate against `PC-31`'s namespace, which `P0-15` does not seed | **`RA-008`** |

```bash
# the actor table is 8 persons + 3 system principals
awk '/^## 4. Actors/,/^## 5\./' docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md | grep -c "| a person |"        # 8
awk '/^## 4. Actors/,/^## 5\./' docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md | grep -c "system principal"    # 3
# how often each named actor is exercised by an acceptance scenario
for a in stores1 stores2 sup1 mgr1 inv1 fin1 aud1; do \
  printf "%-8s %s\n" "$a" "$(grep -c "\b$a\b" docs/SCENARIO-CATALOGUE.md)"; done
# stores1 32 · stores2 2 · sup1 5 · mgr1 17 · inv1 9 · fin1 5 · aud1 3
```

**The number that frames this review:** `mgr1` is the actor of **17** scenarios and `fin1` of **5** —
second and fifth busiest in the cast — and neither has a seeded bundle.

---

## §2 · The findings

### `RA-001` · Warehouse-scoped user access — the predicate that scopes a storekeeper to a site — has no table, no screen and no migration, so no administrator can grant it and `WH-SC-243` is unpassable — **BLOCKER**

- **What is missing or wrong:** `FR-405` requires *"warehouse-scoped user access participates in every
  management query's predicate"*, and `P1-18` builds the predicate. Its own header is
  `Part of __P1__ · Module warehouse-base + warehouse · Migrations **none** · Screens **none**`
  (`issues/p1-18.md:5`). A predicate reads data; nothing in the set holds it.
  - The **owner** axis has both halves: `whb_owner_grants` (`DATA-MODEL.md:498`) with
    `grantee_type`/`grantee_id`/`access_level`/`effective_from`/`effective_to`, and **`WS-020` Owner
    Grants**, a v1·P0 screen at `/warehouse/masters/owner-grants` (`BUILD-SPEC-SCREENS.md:469`), plus a
    *Manage grants* action from the owner screen (`:945`).
  - The **branch** axis is platform's three-mode pattern (`FR-404`, `P0-15`).
  - The **warehouse** axis has neither. `whb_owner_grants` is the only `*_grants` table in the entire
    data model.
- **Why it matters:** name the moment. **Go-live Monday, 08:00.** The administrator opens the product to
  restrict `stores1` to `SITE-A` and there is no screen; the only site dimension available is the
  branch, and `whb_warehouses.branch_id` (`DATA-MODEL.md:450`) means a branch with two sites cannot be
  split at all. Every storekeeper therefore adjusts every site's stock, which is precisely the sentence
  `FR-405` exists to prevent. Two further consequences make this structural rather than cosmetic:
  1. **`P1-18`'s own acceptance is unreachable.** It requires *"the composition order of owner ∩ branch
     ∩ warehouse scope … tested with a user who is restricted on all three axes"* (`p1-18.md:91`).
     If warehouse scope is derived from branch scope it is not a third axis and the test is vacuous; if
     it is a third axis it needs the grant the set does not define. The set never chooses.
  2. **`P1-05`'s site-closure pre-check references the missing object as data.** It returns *"every
     blocking class at once — on-hand stock, in-transit inbound, open receipts and orders, open tasks
     and reservations, an active number series, **warehouse-scoped user grants**, assigned devices —
     each with a count and a link"* (`issues/p1-05.md:37`, restated `:186`). A link to what screen?
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -oE '`whb?[a-z0-9]*_[a-z_]*grants?`' docs/DATA-MODEL.md | sort -u   # `whb_owner_grants`  — one table
  grep -rn "user_warehouse\|warehouse_access\|whb_user_" docs/DATA-MODEL.md          # 0
  grep -nE '^\| WS-[0-9]{3} \|' docs/BUILD-SPEC-SCREENS.md | grep -i "grant"          # WS-020 only
  head -5 issues/p1-18.md | tail -1                                                   # Migrations none · Screens none
  ```
  And in `classic`, the only user↔place table platform owns is branch-grained:
  `platform/backend/src/main/resources/db/migration/V150__create_branch_staff_table.sql:10-15`
  (`branch_staff(branch_id, user_id, …)`) — there is no warehouse dimension for warehouse to reuse.
- **Where it belongs:** `warehouse-base` · v1 · **P1**
- **Disposition:** *fold into tasks `P1-18` and `P1-05`, plus a `DATA-MODEL.md` §2.1 row and a
  `BUILD-SPEC-SCREENS.md` §1 screen row.* The line to add to `P1-18`: *"`whb_warehouse_grants` mirrors
  `whb_owner_grants` exactly — `warehouse_id`, `grantee_type` (`USER`/`ROLE`/`GROUP`), `grantee_id`,
  `access_level` (`VIEW`/`OPERATE`/`ADMIN`), `effective_from`, `effective_to`,
  `uk(warehouse_id, grantee_type, grantee_id, effective_from)` — read by the same single server-side
  resolver, with **`WS-238` Warehouse Grants** as its screen, the Customer reference, alongside
  `WS-020`. **A user with no grant row is unscoped, not blind**: the shipped default must be stated, or
  the first install locks every operator out of every site."* `P1-05`'s closure pre-check then has a
  real table to count and a real screen to link to.
- **Irreversibility:** **reversible** — it is a new table and a new screen, both after `PNR-1`
  (`V500030`), inside `P1`'s own band. But it must land **before** `P1-18` writes the resolver, because
  a resolver shipped against branch scope and later widened to a third axis is every management query
  in two modules re-touched.
- **Relationship to round 1 and 2:** **new.** `GAP-REGISTER.md:280` dispositions `E-046` as
  *COVERED-uncited* with `FR-405 → P1-18` and no lens compared the requirement to its data source.
  `Z-010` is about **role bundles**; this is about the **scope grant**, a different table and a
  different screen. `F-004`/`FR-406`'s owner-set contract test is the model this copies.

---

### `RA-002` · The counter clerk cannot price a line in v1: `price_level` is a keystroke and a column with no vocabulary, there is no price table anywhere in the data model, and the only price loader is v1.1 — **BLOCKER**

- **What is missing or wrong:** `FR-359` (**v1·P2**) requires *"counter sale is keyboard-first: scan or
  part number, quantity, **price level**, print, next — a sub-ten-second bill, **with trade price
  levels** and a cash ticket"*. `WS-194` renders that literally: *"Scan or part number → quantity →
  **price level** → print → next"* (`BUILD-SPEC-SCREENS.md:1910`). `whad_counter_sales.price_level` and
  `whad_counter_sale_lines.unit_price`/`discount_percent`/`line_total` are **v1** columns
  (`DATA-MODEL.md:1270-1271`). Nothing supplies any of them:
  - **There is no price table.** The only price-bearing rows in the whole model are
    `whad_price_file_lines.new_price`/`old_price` (`DATA-MODEL.md:1275`) and the PO/order line's
    `unit_price` — a *purchase* price and an *entered* price, neither a sell price.
  - **The set dropped the sell price deliberately and did not re-home it.**
    `DATA-MODEL.md:4000`: *"`last_purchase_price` and `retail_price` are **dropped**"*; `:4042`:
    *"`unit_price`, `currency` and `price_effective_from`/`_to` are dropped — the PO line carries the
    price"*. Both sentences are about *purchase* price and neither answers *sell* price.
  - **`price_level` has no vocabulary.** It is not one of `D-10`'s thirteen catalogues, has no table,
    no seed and no screen. It is a bare column with a dropdown behind it that nothing populates.
  - **The one thing that would load prices is v1.1.** `whad_price_files`/`_lines` and `WS-197` are
    **v1.1 · P3** (`BUILD-SPEC-SCREENS.md:1913`, `DATA-MODEL.md:1274-1275`), and `P2-25`, the task that
    builds the counter sale, holds migrations `V520000, V520011, V520012, V520100–V520149` — no price
    table among them (`issues/p2-25.md:4`).
- **Why it matters:** the counter clerk's *entire* job is the ten-second bill, and the bill has a
  number on it. In v1 that number is typed by hand for every line, at every counter, for thirty
  thousand part numbers — which is the spreadsheet-and-Dymo outcome `A-2` moved printing to v1 to
  avoid. `WH-SC-216` is a v1 acceptance scenario and its sixth step is *"price applied from a trade
  price level"*; there is nothing to apply it from. Note the boundary this finding does **not** cross:
  `WH-SC-216` itself says *"the price is on the adapter's document; it never enters the port"*, so the
  price is correctly the adapter's — the defect is that the adapter has no place to keep it. This is
  therefore **orthogonal to `U-003`**, which argues that the *tax* and *payment* legs of the same
  screen must be removed; removing them leaves the price leg standing and still sourceless.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -oE '`[a-z_]*price[a-z_]*`' docs/DATA-MODEL.md | sort | uniq -c | sort -rn
  #  5 `unit_price` · 2 `whad_price_files` · 2 `whad_price_file_lines` · 2 `transfer_price_basis`
  #  2 `retail_price` (both in the "dropped" rows) · 1 `price_level` · 1 `last_purchase_price` …
  grep -rn "price_level\|price level" docs/ issues/ | grep -v reviews | wc -l    # 5, all the same keystroke
  grep -rn "whad_price" issues/p2-25.md                                          # 1 hit: "belongs to P2-24 … v1.1"
  ```
- **Where it belongs:** `warehouse-adapter-dealer` · v1 · **P2**
- **Disposition:** *fold into task `P2-25`.* Two lines: *"`V520015` creates `whad_price_levels`
  (`code`, `name`, `is_default`, `is_active` — a catalogue, no `CHECK`, per `D-10`) and
  `whad_item_prices` (`item_id`, `price_level_code`, `unit_price`, `currency_code`, `effective_from`,
  `effective_to`, `uk(item_id, price_level_code, effective_from)`), both adapter-owned — **base learns
  nothing about selling**, exactly as it learns nothing about vehicle fitment (`D-11`). **`WS-238`+
  Item Prices** is a Department-shape screen with `ImportButton`, because thirty thousand prices are
  never keyed. `whad_price_file_lines.applied` writes into `whad_item_prices` when `P3`'s price-file
  loader lands, which is why the table is v1 and the loader is v1.1."* Amend `FR-359`'s row to name the
  table, and add one v1 scenario in the `WH-SC-216` shape asserting that a line resolves its price from
  the clerk's price level and refuses when no effective row exists.
- **Irreversibility:** **reversible** — adapter-owned tables in the adapter's own band, after every
  `PNR`. Cheap now; after go-live it is a price history nobody captured, so the first price-file diff
  has no *old* side.
- **Relationship to round 1 and 2:** **new.** `E-065` and `S-063` are dispositioned CITED against
  `P2-15`/`P2-25` (`GAP-REGISTER.md:299`, `:626`) and are about the counter sale *existing*. R10 walked
  this exact step and marked it **✔** on the strength of the requirement text
  (`R10 §2` walk 7 step 6) without asking where the price comes from. `U-003` is the money boundary;
  this is the price source.

---

### `RA-003` · The four seeded role bundles are defined by a four-verb deny-list over a sixty-verb authority space, and cover four of the eight human actors — so the storekeeper is granted the QC release gate and `mgr1`, the actor of seventeen scenarios, has no role at all — **MAJOR**

- **What is missing or wrong:** `Z-010`'s remedy is now in `P0-15` (`issues/p0-15.md:15-24`), and it
  defines **Storekeeper** as *"every `:view`, receipt/putaway/pick/count execution, **no `:approve`, no
  `:reverse`, no `:close`, no `:override`**"*. That is a deny-list of four verb names. §10.2 of the
  screen spec enumerates **60** verb permission strings for P0–P2-IN and **17** more for P5
  (`BUILD-SPEC-SCREENS.md:2202` onward). **Forty-seven of the sixty are not named by any of the four
  exclusions**, so a literal reading of the bundle grants them. Among them:

  | Verb the deny-list does not exclude | What it does | Screen |
  |---|---|---|
  | `wh_quality_inspections:disposition` | release / reject / RTV / scrap — the spec's own note says **"QA-role gated"** | WS-080 |
  | `wh_return_receipts:disposition` | restock / quarantine / scrap a customer return | WS-135 |
  | `wh_blocked_movements:force` | force a movement the ledger refused | WS-097 |
  | `wh_holds:place` · `:release` · `:mass` | release a quality/legal hold on stock | WS-092 |
  | `whb_reservations:release` · `:extend` | release another team's allocation | WS-047 |
  | `wh_opening_stock_batches:post` · `wh_cutover_checklists:certify` | post opening stock; sign the go-live certificate | WS-150, WS-151 |
  | `whb_job_runs:trigger` · `whb_outbox:replay` · `whb_accounting_handovers:retry` | operate the plumbing | WS-064, WS-056, WS-052 |
  | `wh_shipments:dispatch` | **the inventory-relief event** | WS-105 |

  Separately, the bundle set is **Storekeeper · Supervisor · Stock Controller · 3PL Client** — and the
  FRD names **eight** persons. **Warehouse manager** (`mgr1`) and **Finance / controller** (`fin1`)
  have no bundle, and neither does the **QA inspector**, who is not an actor row at all despite owning
  the one permission the spec singles out as role-gated. `mgr1` is the approver in `WH-SC-039`
  (v1·P0, a ₹5.76 lakh scrap) and the override-holder in `WH-SC-022` (v1·P0); `fin1` is the reader in
  `WH-SC-060` (v1·P2).
- **Why it matters:** this is the exact failure the brief names — *a role that can do its job only by
  being granted a permission that also lets it do something it must not*. Concretely: the storekeeper
  who must complete a putaway is, on the shipped bundle, also able to **release stock that QA
  quarantined**, which is the single control standing between a failed inspection and a customer
  shipment. In a pharma or food install that is a regulatory finding on day one. And because the
  bundles ship as *"a customer-editable starting point"*, every customer's real roles are **clones of
  this one**, so the over-grant propagates by copy. The manager gap bites differently: `P0-15` grants
  `whb_stock_movements:approve` to **Supervisor**, so the person `FR-408` requires to be a *second*
  user is the storekeeper's shift lead rather than the manager the FRD names — and with no Manager
  bundle at all, the install's answer at 6pm on go-live Sunday is `ADMIN`, which is the outcome
  `Z-010` was filed to prevent.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  # 60 P0–P2-IN verb strings in §10.2; 47 are outside the Storekeeper deny-list
  python3 - <<'PY'
  import re
  L=open('docs/BUILD-SPEC-SCREENS.md').read().split('\n')
  def verbs(a,b):
      out=[]
      for ln in L[a-1:b]:
          if not ln.startswith('| `'): continue
          last=None
          for t in re.findall(r'`([a-z0-9_:]+)`', ln.split('|')[1]):
              if t.startswith(':'): out.append(last.split(':')[0]+t)
              else: out.append(t); last=t
      return out
  t1, t2 = verbs(2205,2245), verbs(2258,2275)
  deny={'approve','reverse','close','override'}
  print(len(t1), len(t2), len([v for v in t1 if v.rsplit(':',1)[1] not in deny]))
  PY
  # 60 17 47
  grep -n "QA-role gated" docs/BUILD-SPEC-SCREENS.md            # 1567, 2226 — the only role-gated verb in the set
  grep -c "| a person |" docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md   # 8 actors
  grep -n "Storekeeper" issues/p0-15.md                          # 16, 18 — four bundles, named once
  ```
- **Where it belongs:** `warehouse-base` · v1 · **P0** (`V501002`)
- **Disposition:** *fold into task `P0-15`, amending the `Z-010` block rather than adding a new one.*
  Three changes: **(1) the bundles are allow-lists, not deny-lists** — each names the verb strings it
  grants, and `P0-15`'s acceptance gains *"every one of §10.2's verb permissions appears in at least one
  bundle or in an explicit `granted to no seeded bundle` list, asserted by a query that fails when
  §10.2 grows"*. **(2) Two more bundles**: **Warehouse Manager** (Supervisor plus
  `wh_stock_adjustments:approve`, `whb_stock_periods:close`, the soft-close override of `RA-008`,
  `wh_counts:approve`, `wh_blocked_movements:force`) and **Finance Controller** (`:view` and `:export`
  everywhere, `warehouse:cost:view` from `K-002`, `whb_accounting_handovers:retry`,
  `wh_revaluations:approve`, `wh_landed_cost_documents:apply`, and **no** operational verb). **(3) A QA
  bundle and a QA actor row** — `wh_quality_inspections:disposition` and `wh_return_receipts:disposition`
  belong to it and to nothing else, and the FRD §4 actor table gains the row it is missing.
- **Irreversibility:** **reversible** — role seeds are forward-only inserts, as `Z-010` established. But
  a bundle that shipped over-granted and was then narrowed is a **revocation** across every clone a
  customer made of it, which is hand work of exactly the kind `FR-407` exists to avoid.
- **Relationship to round 2:** this **audits `Z-010`'s remedy**, which no lens has done because round 2
  authored it. `Z-010` established *that* bundles are needed and named four; this establishes that the
  four as written are unsafe and incomplete. `Q-003` (AUDITOR and `:export`) and `H-001` (the 25 P5
  verbs) are adjacent and neither touches bundle composition. `X-014` is about verbs with **no** name;
  this is about named verbs with no home.

---

### `RA-004` · Closing a stock period strands every in-flight approval: the pre-check is a single condition, and `FR-020` then refuses the approved posting "including a reversal", so a submitted scrap becomes an unpostable, undeletable row — **MAJOR**

- **What is missing or wrong:** `WS-045`'s three close modals are specified as *"each refusing while
  `pendingHandoverCount > 0`"* (`BUILD-SPEC-SCREENS.md:1391`, restated `issues/p0-07.md:49`, `:107`) —
  **one** condition, and it points **downstream**, at accounting. Nothing checks the period's own
  in-flight work. Meanwhile `FR-027` (v1·P0) makes an approval-bearing movement exist *before* it
  posts, and `WH-SC-039` spells out the sequence: *"On submit the movement is created with
  `approval_status = PENDING` and **no ledger effect** … On approval it posts"*. `FR-020` then says a
  movement whose date falls in a `CLOSED` period *"is refused, **including a reversal**"*. Put the
  three together and the outcome is undefined and bad:
  - `stores1` submits a `SCRAP` of 12 ECUs on **30 September**. `mgr1` is on leave.
  - `fin1` closes `2026-09` on **2 October**; the close is allowed, because there is no pending
    handover for a movement that never posted.
  - `mgr1` approves on **3 October**. The posting is refused by `FR-020`. A **current-dated** posting
    is not offered — the movement row already exists with its own date, and `L-2` forbids deleting it
    and forbids `UPDATE`.
  The same shape applies to `wh_stock_adjustments` in `SUBMITTED`, `wh_counts` in pending approval, and
  every unresolved `wh_blocked_movements` row — all of which hold physical facts about the closing
  period.
- **Why it matters:** the finance controller takes the single most consequential decision in the
  product's month with one number in front of them, and the number is about the *next* ledger rather
  than about their own. The cost is not a stuck screen: it is a **scrap that physically happened in
  September and is in no period at all**, sitting forever in `whb_stock_movements` as an unposted row
  the append-only rule will not let anyone remove. The storekeeper who did the work sees nothing, since
  `Y-008` already establishes that pending approvals have no clock and no signal. And note the
  asymmetry the set has already accepted as correct in the mirror direction: `WH-SC-163` has
  **accounting's** close blocked by *warehouse's* pending handover, naming it. Warehouse's own close
  blocks on nothing of its own.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rn "pendingHandoverCount" docs/ issues/ | grep -v reviews | wc -l   # 5 — the only close pre-check
  grep -rn -i "pre-close\|before close\|closing check" docs/ issues/ | grep -v reviews   # 0
  grep -rn "approval_status" docs/ issues/ | grep -v reviews | wc -l        # 7 — none mentions a period
  sed -n '1383,1394p' docs/BUILD-SPEC-SCREENS.md   # WS-045: movementCount + pendingHandoverCount, nothing else
  ```
- **Where it belongs:** `warehouse-base` · v1 · **P0** (`P0-07`, `WS-045`) with a service rule in `P0-02`
- **Disposition:** *fold into tasks `P0-07` and `P0-02`.* To `P0-07`: *"the close pre-check returns
  **every** blocking class at once, in the `P1-05` site-closure shape — pending handovers, movements
  in `approval_status = PENDING` dated in the period, `wh_stock_adjustments` and `wh_counts` awaiting
  approval, unresolved `wh_blocked_movements` — each with a count and a link. `WS-045` gains
  `pendingApprovalCount` and `unresolvedBlockedCount` beside `pendingHandoverCount`. **Soft close warns
  and lists; hard close refuses.**"* To `P0-02`: *"a movement approved after its period closed is
  refused with a named code and the refusal message states the only correct act — **withdraw and
  resubmit current-dated**, which `WH-SC-021` already establishes as the pattern for reversals. A
  `PENDING` movement therefore needs a terminal `WITHDRAWN` state, because `L-2` forbids deleting
  it."* One scenario in the `WH-SC-021` shape.
- **Irreversibility:** **reversible as code**, and the pre-check is a query. But the *state* is not:
  every install that closes a period over pending approvals accumulates permanent unpostable rows, and
  `L-2` means they can never be cleaned up — only explained.
- **Relationship to round 2:** **new.** `Y-008` (MINOR, folded into `P0-02`) owns *visibility* of
  pending approvals — no filter, no clock, no signal. This owns their *interaction with the period
  lock*, which is a data-loss outcome rather than a visibility one, and it lands on a different
  screen and a different task. `Z-002`'s financial-year boundary is a numbering defect at the same
  calendar moment and is unrelated in mechanism.

---

### `RA-005` · The auditor's tamper evidence has no verifier: three v1·P0 scenarios assert the chain verifies, no screen action and no job recomputes it, and the port contract states the feature is v2 — **MAJOR**

- **What is missing or wrong:** `FR-006` (v1·P0) gives every movement *"a gapless `sequence_no` per
  warehouse and a `prev_payload_hash`, giving a **tamper-evident chain**"*. Three v1·P0 scenarios then
  spend it:
  - `WH-SC-033` — *"**recomputing the chain** over the four rows verifies"*;
  - `WH-SC-245` — `aud1` *"opens the ledger, the movement register, the adjustment register, the count
    history, the valuation and **the immutability evidence**"*, and all six reads succeed;
  - `WH-SC-253` — after a point-in-time restore, *"the hash chain of `WH-SC-033` **still verifies**"*.

  Nothing recomputes it. `WS-041` renders `payload_hash` and `prev_payload_hash` as two fields on one
  movement's header panel (`BUILD-SPEC-SCREENS.md:1307`) and offers *Reverse · Approve · Print*;
  `WS-040`'s toolbar has *Simulate* and no verify; `WS-063` shows `prevHash`/`payloadHash` as grid
  columns. `P0-13`'s dated-obligation register lists **nine** jobs (`issues/p0-13.md:54-62`) and none is
  a chain verifier. And the port contract answers the question in terms:
  *"Tamper evidence. A chain begun in v2 proves nothing about v1. **Feature is v2; the column is v1.**"*
  (`PORT-AND-ADAPTER-CONTRACT.md:223`).
- **Why it matters:** the auditor is the only actor in the FRD whose entire job is *reading*, and the
  one artefact that distinguishes this ledger from a table with an append-only trigger is the chain.
  Today `aud1`'s shift is: five reads that work, and a sixth — the one the immutability claim rests on
  — that resolves to two 64-character strings on a detail page with no way to tell whether they are
  correct. That is worse than not having the chain, because the columns invite the trust that stops the
  auditor asking. It also breaks a v1·P0 *acceptance criterion*: `DECISIONS.md` §5 makes scenarios the
  phase exit, and `WH-SC-033` cannot be signed off by inspection of a column. Note what is **not**
  claimed here: the *columns* are correctly v1 (`IRR-03` — a chain cannot be started retroactively),
  and deferring a *tamper-forensics console* to v2 is a legitimate call. What is missing is the
  cheapest possible verifier, and three v1 scenarios that already assume it exists.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rn -i "verify chain\|chain verif\|recompute the chain\|hash verif" docs/ issues/ | grep -v reviews   # 0
  grep -n "prev_payload_hash" docs/BUILD-SPEC-SCREENS.md      # 1307 only — a field on WS-041, no action
  sed -n '54,62p' issues/p0-13.md | grep -ci hash             # 0 of the nine dated obligations
  grep -n "Feature is v2; the column is v1" docs/PORT-AND-ADAPTER-CONTRACT.md   # 223
  ```
- **Where it belongs:** `warehouse-base` · v1 · **P0** (`P0-13`, which owns `whb_job_runs` and `WS-064`)
- **Disposition:** *fold into task `P0-13`.* The line to add: *"a tenth dated obligation —
  **`chain-verify`**, a nightly job per warehouse that walks `whb_stock_movements` in `sequence_no`
  order, recomputes each row's `prev_payload_hash` against its predecessor's `payload_hash`, writes a
  `whb_job_runs` row on success **and** on failure, and raises a `wh_reconciliation_exceptions` row
  naming the first divergent `sequence_no`. **`WS-040` gains a `Verify chain` toolbar action** gated on
  `whb_stock_movements:view`, running the same walk over the filtered range and reporting *verified to
  sequence N* — which is what makes `WH-SC-033` and `WH-SC-245` assertable and what `WH-SC-253`'s
  restore test runs. A verification that cannot fail is not a control: the acceptance asserts a
  deliberately corrupted row is named."* Amend `PC-31`'s neighbouring `prev_payload_hash` row so the
  document no longer says the feature is v2 while three v1 scenarios spend it.
- **Irreversibility:** **reversible** — a job and a toolbar action, no schema. The *columns* are already
  correctly under `PNR-1`, which is why this is a MAJOR and not a BLOCKER.
- **Relationship to round 2:** **new.** `K-001` (BLOCKER) establishes that **no job in the product has
  an execution contract**; this establishes that one particular job **does not exist at all**, and it
  is the one three acceptance scenarios name. `Y-008`'s two additions to the same register are a
  different pair of clocks. `IRR-03` is cited by neither for this purpose.

---

### `RA-006` · The picker is offered "emergency replenish" on a v1 screen whose entire mechanism is v1.1, so a picker who empties a pick face has no way to ask for a refill — **MAJOR**

- **What is missing or wrong:** `FR-185` is **v1·P2** and requires the short pick to *"offer
  **re-allocate / emergency replenish / short the line**"*; `P2-09`, the task that builds `WS-102`,
  restates all three verbatim (`issues/p2-09.md:38`). Two of the three exist in v1
  (`wh_demand_orders:allocate`, `wh_demand_orders:short_pick`). The third does not:
  - `FR-259` — *"**Emergency replenishment triggered by a short pick**, opportunistic top-off …"* — is
    **v2 · P5** (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:471`).
  - `FR-255` — *"Pick-face replenishment tasks are generated from item × location min/max"* — is
    **v1.1 · P3** (`:467`).
  - `WS-142` Replenishment Tasks — whose `trigger` enum is literally
    `MIN_MAX/**SHORT_PICK**/OPPORTUNISTIC/BREAK_CASE` — is **v1.1 · P3**
    (`BUILD-SPEC-SCREENS.md:591`, `:1786`).
  - The v1 replenishment task, `P2-15`, is the **buyer's** document — runs, suggestions, purchase or
    sister-branch transfer — and states its own boundary (`issues/p2-15.md:40`). It has nothing to do
    with moving a pallet from reserve to a pick face.
  `P2-09`'s acceptance list asserts the exception code, the released reservation and the cycle-count
  task (`p2-09.md:105-106`) and asserts nothing about the replenish path, so the gap is invisible at
  build time.
- **Why it matters:** an empty pick face is the most common physical event in a warehouse day, and the
  short pick is — in `FR-185`'s own words — *"the highest-quality signal of an inventory error a
  warehouse ever gets"*. In v1 the picker records the shortfall, the reservation releases, a
  cycle-count task is created for the location if the site switch is on — and the **bin is still
  empty**. The next picker on the same face shorts again, and the one after that. The order can be
  re-allocated to another location only if another location has it; when the stock is in bulk reserve
  above the face, which is the normal case, v1 has no verb that brings it down. The clean part of
  `FR-185` — the auto cycle count — actually makes it worse, because it manufactures a count document
  per short on a face nobody has refilled.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rn "wh_replenishment_tasks" issues/*.md | cut -d: -f1 | sort -u   # p3-12, p6-02, p5-18 — no P2 task
  grep -n "WS-142 " docs/BUILD-SPEC-SCREENS.md                            # 591: v1.1 · P3
  grep -n "FR-255\b\|FR-259\b" docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md  # 467: v1.1 · P3   471: v2 · P5
  grep -c -i "replenish" issues/p2-09.md                                   # 1 — the offered action, and nothing else
  # and the per-site switch that gates the auto cycle count has no home either
  grep -rn "warehouse\.[a-z_]*\.[a-z_]*" docs/ issues/ -o | grep -v reviews | grep -v adapter | sort -u | wc -l  # 8 settings keys, none of them this
  ```
- **Where it belongs:** `warehouse` · v1 · **P2**
- **Disposition:** *fold into task `P2-09`, and amend `FR-185`.* The minimum honest v1 is not the
  v1.1 task engine: *"in v1 **emergency replenish creates a `wh_transfer_orders` row of type
  `BIN_TO_BIN`** from the resolved reserve location to the short pick face, pre-filled with the
  shortfall quantity and carrying the pick task's exception code as its reference — one existing v1
  object, one existing v1 screen (`WS-090`), no new table. `FR-255`'s min/max-generated task engine and
  `WS-142` stay v1.1 and supersede this path when they land."* If that is judged too much for P2, the
  alternative is equally acceptable and must be **written down**: remove *emergency replenish* from
  `FR-185`'s v1 offer, state that v1 has two short-pick outcomes, and amend `p2-09.md:38` — a screen
  that offers a button it cannot honour is the worse of the two. Also give the per-site auto-count
  switch a home: `admin_settings` key `warehouse.short_pick.auto_count`, seeded in `P0-15`'s `V501100`
  beside the other five.
- **Irreversibility:** **reversible** — no schema, no seal.
- **Relationship to round 1 and 2:** **new.** R10 walked this step and marked it **✔** (`R10 §2` walk 3
  step 9); R11 marked the same exception `B9` **SPEC** on the strength of *"three offered actions"*.
  Neither checked the version of the mechanism behind the third. `U-002` owns *who is told* about the
  short (step 9b); this owns *what the picker can do about it*.

---

### `RA-007` · The permission the integration principal and the device authenticate with is defined twice, in two namespaces, and `P0-15` seeds one — six of `PC-31`'s ten v1 strings appear nowhere in the screen spec — **MAJOR**

- **What is missing or wrong:** the set has **two** authorities for v1 permission names and they
  disagree.
  - `PORT-AND-ADAPTER-CONTRACT.md` `PC-31` (`:625-636`) lists the permissions a port caller needs and
    says they *"exist in **v1** even where the feature is later, because retro-granting a permission
    invented in v2 to every existing role is hand work"*.
  - `BUILD-SPEC-SCREENS.md` §10.2 (`:2202`) lists the verb permissions and is what `P0-15`'s
    `V501000` seeds.

  Four of `PC-31`'s strings match. **Six appear nowhere in the screen spec**, and four of those six are
  the port's name for a gate §10.2 already names differently:

  | `PC-31` says | §10.2 says | Same gate? |
  |---|---|---|
  | `warehouse:stock:view` | `whb_stock_positions:view` | yes — two names |
  | `warehouse:reservations:release` | `whb_reservations:release` | yes — two names |
  | `warehouse:reservations:hold` | `wh_holds:place` / `whb_reservations:extend` | unclear — no mapping stated |
  | `warehouse:outbox:replay` · `:view` | `whb_outbox:replay` | yes — two names |
  | `warehouse:movements:post:backdated` | — *(`whb_stock_periods:override` is the period-side verb)* | **no equivalent** |

  `warehouse:movements:post:backdated` is the sharpest, because a **v1·P0 acceptance scenario turns on
  it**: `WH-SC-022` reads *"`stores1` has no backdating permission; `mgr1` holds
  `warehouse:movements:post:backdated`"*, and the assertion is a `403` naming the missing permission.
  `WH-SC-241`, also v1·P0 and the acceptance test for `FR-401` itself, is written against
  `warehouse:stock:view` — a string §10.1's own naming rule (*"Permission resource | the table name"*)
  would render `whb_stock_positions:view`.
- **Why it matters:** two of the three system actors — **Integration** and **Device** — exist only as
  port callers, and the port is where `PC-31`'s names live. `P0-15` seeds §10.2's names. Whichever
  document the implementer follows, the other half of the product returns `403` to a caller holding a
  permission that, by the set's own claim, exists in v1. The human cost lands on `mgr1`: the soft-close
  override is the one authority that distinguishes a manager from a storekeeper at a period boundary,
  and it is a permission string that appears in exactly two documents and in no seed. And a permission
  *name* is the one thing `FR-407`/`IRR-63` say cannot be fixed cheaply later — renaming it after
  go-live is retro-granting work across every role a customer has built.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  for p in warehouse:movements:post warehouse:movements:reverse warehouse:movements:view \
           warehouse:movements:simulate warehouse:movements:post:backdated warehouse:stock:view \
           warehouse:reservations:hold warehouse:reservations:release \
           warehouse:outbox:replay warehouse:outbox:view; do
    printf "%-40s %s\n" "$p" "$(grep -cF "$p" docs/BUILD-SPEC-SCREENS.md)"; done
  # …post 1 · …reverse 1 · …view 1 · …simulate 1 · …post:backdated 0 · stock:view 0
  # reservations:hold 0 · reservations:release 0 · outbox:replay 0 · outbox:view 0
  grep -rn "post:backdated" docs/ issues/ | grep -v reviews    # 2 hits: PC-31 (:633) and WH-SC-022 — no seed
  grep -rn "warehouse:stock:view" docs/ issues/ | grep -v reviews   # 1 hit: WH-SC-241
  ```
- **Where it belongs:** `warehouse-base` · v1 · **P0** (`V501000`), with amendments to two documents
- **Disposition:** *fold into task `P0-15`, and amend `PORT-AND-ADAPTER-CONTRACT.md` `PC-31` or
  `BUILD-SPEC-SCREENS.md` §10.2 — **one of them must lose**, and the loser must be edited rather than
  left standing.* Recommended: **§10.2 is the seed authority** (it is what the migration is written
  from and it follows §10.1's table-name rule), so `PC-31` is rewritten to cite §10.2's strings, with
  two additions §10.2 must carry because the port needs gates no screen has:
  **`whb_stock_movements:post_backdated`** (posting into a `SOFT_CLOSED` period — the `mgr1` authority
  of `WH-SC-022`, distinct from `whb_stock_periods:override` which changes the *period*, not a
  *movement*) and **`whb_outbox:view`**. `WH-SC-022` and `WH-SC-241` are then amended to the seeded
  strings — a scenario asserting a `403` on a permission name that does not exist tests nothing.
- **Irreversibility:** **reversible today, unrecoverable after go-live.** `FR-407`'s whole argument —
  reserve `logistics:*` in v1 because retro-granting is hand work — applies verbatim to renaming a
  warehouse permission after roles have been built on it (`IRR-63`).
- **Relationship to round 2:** **new, and adjacent to `X-014`, not a restatement of it.** `X-014` says
  §10.2 lists **no** verb for any P3–P6 transition — names that exist nowhere, for later phases. This
  says two documents give **different names to the same v1 gate**, and that a v1·P0 acceptance scenario
  cites a name neither seeds. `H-001` added 25 P5 strings to §10.2 and did not reconcile `PC-31`.

---

### `RA-008` · The warehouse manager's authority boundary is undefined data: `FR-145` mandates an approval threshold by value and by quantity, and no column, setting or screen holds one — **MINOR**

- **What is missing or wrong:** the FRD defines the warehouse manager by a threshold —
  *"**Adjustments above threshold**, write-offs, period close, count approval"*
  (`WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md:86`) — and `FR-145` makes it a requirement:
  *"gated by an approval threshold expressed **by value as well as by quantity**. A one-unit variance
  on a washer line is noise; a one-unit variance on an engine control unit is an investigation"*.
  `wh_stock_adjustments`' description repeats it — *"Adjustment header with an approval threshold by
  value as well as by quantity"* — and its column list carries `requires_approval`, `approved_by`,
  `approved_at` and **no threshold** (`DATA-MODEL.md:999`). `P2-01` says *"Both thresholds live on
  configuration, both are evaluated at submit"* (`issues/p2-01.md:31`) without naming the
  configuration, and `WS-089` has no threshold field. Compare `wh_count_programs`, which does this
  correctly: `recount_threshold_pct`, `approval_threshold_pct`, `approval_threshold_value` on the
  programme row (`DATA-MODEL.md:1005`).
- **Why it matters:** the boundary between the storekeeper who *submits* and the manager who
  *approves* is a number, and the number has no home, so the implementer will hard-code one. The
  operational shape of the wrong choice is familiar in both directions: set it low and the manager
  approves four hundred washer variances a month and starts rubber-stamping; set it high and the ECU
  write-off posts unseen. It is also the second half of `RA-003` — a Warehouse Manager bundle is not
  worth much when the thing it gates is a constant. This is MINOR only because it is one column set
  and one modal field, in a task that has not been built.
- **Negative evidence:**
  ```bash
  cd /Users/bbhushan/work/git/workspace/warehouse-issues
  grep -rn -i "threshold" docs/DATA-MODEL.md | grep -c "wh_stock_adjustments"   # 1 — the prose, not a column
  grep -rn "warehouse\.[a-z_]*\.[a-z_]*" docs/ issues/ -o | grep -v reviews | grep -v adapter | sort -u
  # 8 admin_settings keys — negative_stock.default_mode, period.soft_close_requires_approval,
  # outbox.max_attempts, reservation.default_ttl_minutes, port.rejected_queue_threshold,
  # position.max_contention_retries, outbox.max_cursor_lag — none is an adjustment threshold
  grep -n -i "threshold" issues/p2-01.md    # 1, 29, 31, 136 — all prose, no home named
  ```
- **Where it belongs:** `warehouse` · v1 · **P2** (`P2-01`, `V510030`)
- **Disposition:** *fold into task `P2-01`.* The line to add: *"the threshold is a **row, not a
  constant** — `wh_adjustment_approval_policies` with nullable `warehouse_id`, `owner_id`,
  `item_category_id`, `reason_code_id`, a computed `specificity` and
  `threshold_quantity`/`threshold_value`, resolved most-specific-first, **mirroring
  `whb_gl_posting_rules` exactly** as `Z-001` requires of every policy ladder in this set, with the
  all-null row seeded from `admin_settings warehouse.adjustment.default_threshold_value`. `WS-089`
  shows the resolved threshold and which row supplied it, and offers the **Test resolution** modal
  `WS-051` already defines."* Amend `DATA-MODEL.md:999`'s description so it stops asserting a
  threshold the columns do not carry.
- **Irreversibility:** **reversible** — `V510030` is well after `PNR-1` and nothing about it is sealed.
- **Relationship to round 2:** **new instance, known shape.** `Z-001` (BLOCKER) enumerates **five**
  most-specific-first ladders and grades them; the adjustment threshold is not one of the five and is
  the same failure — a policy the requirement states and the table cannot express. Filing it here
  rather than reopening `Z-001` keeps `Z-001`'s five-row table as the dated record round 2 wrote.

---

## §3 · What I checked and found sound

Listed so round 4 does not re-walk this ground.

| What I went looking for | Where it is covered |
|---|---|
| **The stock controller's whole month** — programme by ABC class, blind count, freeze, book snapshot stored even when blind, tolerance by percentage *and* value, recount, self-approval barred, one movement per variance line | `WS-093`/`094`/`095` · `FR-153`–`FR-159` · `FR-408` · `wh_count_programs.approval_threshold_pct`/`_value`. The best-designed persona in the set |
| **The buyer's decision surface** — what is late, what is open, what is on order, what to raise | `WS-072` filters `overdueOnly`/`openOnly`, statistics strip *open · overdue · fully received · value on order*, `WS-141` suggestion → PO in one action (`FR-253`), `WH-SC-284` excludes VOR/emergency from lead-time statistics |
| **The receiving clerk's two handoffs** — receipt → QC, QC → putaway — carried as data the receiver can filter on | `WS-076` filters `awaitingQc` and `awaitingPutaway` booleans; `WS-080` `Disposition`; `WS-082` `Complete` with a captured override reason |
| **Maker–checker as a stated rule rather than an assumption** | `FR-408` · `WH-SC-039` (`stores1` submits, `mgr1` approves, self-approval `403`) · `WS-094`'s *"the counter may not approve their own count"* · `WS-163`'s *"the approver may not be the raiser"* |
| **The auditor is read-only and it is asserted, not assumed** | `FR-403` · `WH-SC-245` · `P0-15`'s *"AUDITOR must never receive a verb permission"* trap, with `:export` explicitly yes |
| **Cost suppressed by actor, in the mapper and in the export** | `K-002` → `P1-18`'s round-2 block: `warehouse:cost:view`, response-DTO omission, asserted on raw JSON, `role_field_configs` explicitly not used |
| **The 3PL client's row-level segregation exists in v1 even though the portal is v2** | `whb_owner_grants` + `WS-020` are **v1·P0**, `IRR-60`, `FR-114`'s `403 OWNER_NOT_PERMITTED` rather than an empty grid |
| **Operator work on a handheld is a *stated* v1.1 deferral, not an oversight** | `DECISIONS.md` §5 places RF task flows in v1.1/`P3`; `A-2` pulled **printing** into v1 precisely so the v1 shift runs on paper and a desk. The only line that reads otherwise is the actor table's *"Lives on a handheld, not a desk"* (`:84`), which describes the v1.1 world; worth one clarifying clause, not a finding |
| **`wh_blocked_movements` as the supervisor's landing zone** | `FR-028` · `WS-097` — *"refusing the transaction does not un-move the goods"*. The single best decision in the set for the operator personas |
| **Device and scheduler as first-class non-human actors** | `actor_type = DEVICE` + `device_id` on the movement; `OD-8` correctly holds the out-of-process authentication question open with a deadline |

---

## §4 · Refused

Candidates I declined, and the finding id that already owns each. Per the governing rule, a restatement
is worse than no finding.

1. **"No operational role is seeded."** → **`Z-010`** (R12, MINOR, FOLD-TASK `P0-15`,
   `GAP-REGISTER-R2.md:181`). Refused as written. `RA-003` audits the *remedy* — the four bundles as
   they now stand in `p0-15.md:15-24` — which is a different claim about a different artefact.
2. **"The packer cannot work in v1."** → **`U-001`** (R10, BLOCKER). The most expensive role gap in the
   set and entirely owned. Recorded as `BROKEN` in the coverage table so the persona view is complete,
   and not re-filed.
3. **"Nobody is told that work is waiting."** → **`U-002`** (R10, BLOCKER, re-phased **P3-16 → P2**,
   `GAP-REGISTER-R2.md:158`). This is the single biggest role-level defect in the set and it is closed.
   Every *"who is told"* question I hit — the QA inspector's queue, the supervisor's morning, the
   reconciliation case owner, the drift alarm, the rejected handover — resolves to it. Refused six
   times over.
4. **"The dock coordinator cannot stamp an arrival."** → **`U-004`** (R10, MAJOR) and **`X-027`** (the
   gate pass). Both v1-column/v1.1-writer, both owned.
5. **"The dispatcher has no closing event."** → **`U-005`** (R10, MAJOR).
6. **"Work in flight has no abandonment clock, so a picker's shift ends mid-task."** → **`Y-004`**
   (R11, MAJOR), which names the shift-end symptom explicitly. A separate *shift-handover* object
   would be over-engineering: `whb_tasks` already carries `assigned_to`, `paused_seconds` and a
   `PAUSED` state, and `Y-004`'s reclaim is the right mechanism.
7. **"Cost and value are visible to any operator who can open the screen."** → **`K-002`** (R13,
   MAJOR), already folded into `P1-18` with the mapper-level rule. The storekeeper-sees-value question
   is answered.
8. **"Jobs are invisible, so nobody knows the expiry sweep did not run."** → **`K-001`** (R13,
   BLOCKER). `RA-005` files only the **one job that does not exist**, not the execution contract of the
   jobs that do.
9. **"§10.2 has no verb permission for P3–P6 transitions, so the v1.1 supervisor's task board is
   `:edit`-gated."** → **`X-014`** (DESIGN-SET-DEFECTS, MAJOR). `RA-007` is confined to the **v1**
   strings where two documents collide.
10. **"`wh_orders:edit_after_release` in `WH-SC-095` names a table that does not exist
    (`wh_demand_orders`) and a verb §10.2 does not carry."** → **`X-014`** again; the scenario is
    v1.1·P3 and falls inside its scope. Noted here only so the next reader does not re-derive it.
11. **"The 3PL billing clerk has no bundle."** → **`H-001`** authored the 25 P5 verb strings and
    `P5-01` seeds them; the bundle question is `RA-003`'s allow-list rule applied at P5, and pulling a
    v2 role forward would be the over-engineering `DECISIONS.md` §7 warns against. `wh3_disputes:raise`
    / `:uphold` already carries the segregation note.
12. **"The QA inspector has no dedicated screen."** Refused — `WS-080` is a complete inspection surface
    (`Start · Record results · Disposition · Complete`, a header over lines, one inspection per GRN).
    The QA defect is a **permission boundary**, not a screen, and it is `RA-003`.
13. **"`whb_devices` is v1.1 while `whb_tasks.device_id` and `wh_blocked_movements.deviceId` are v1."**
    Refused as the same shape as **`U-006`** (the `printerId` filter over a v1.1 table) and materially
    smaller: a device id is a free string on a movement in v1 and the registry adds a name to it. One
    line in `P0-13` at most; not worth a finding of its own.
14. **"Warehouse has no user-management screen."** Refused — users, roles and role assignment are
    platform's, correctly. What warehouse owes is the *warehouse-shaped* grant, and that is `RA-001`.

---

## §5 · Counts

```bash
cd /Users/bbhushan/work/git/workspace/warehouse-issues/docs/reviews
grep -cE '^### `RA-[0-9]{3}`' R16-role-and-persona-completeness.md                  # 8
grep -E '^### `RA-' R16-role-and-persona-completeness.md \
  | grep -oE '\*\*(BLOCKER|MAJOR|MINOR)\*\*$' | sort | uniq -c
#   2 **BLOCKER**
#   5 **MAJOR**
#   1 **MINOR**
grep -rohE "\bRA-[0-9]{1,3}\b" ../../docs ../../issues | sort -u | wc -l            # 8, all in this file
```

| Severity | Count | Findings |
|---|---|---|
| **BLOCKER** | 2 | `RA-001` `RA-002` |
| **MAJOR** | 5 | `RA-003` `RA-004` `RA-005` `RA-006` `RA-007` |
| **MINOR** | 1 | `RA-008` |
| **Total** | **8** | |

**Role inventory:** 16 walked · **3 COMPLETE** · 6 HOLED · 5 BROKEN · 2 v2-only.
**Actor arithmetic:** 8 human actors · **4** with a seeded bundle · `mgr1` (17 scenarios) and `fin1`
(5) among the four without.
**Permission arithmetic:** 60 P0–P2-IN verb strings in §10.2 · **47** outside the Storekeeper
deny-list · 10 strings in `PC-31` · **6** absent from §10.2.

**Prefix allocation check, run before writing:**

```bash
grep -rohE "\bRA-[0-9]{1,3}\b" docs/ issues/ | wc -l     # 0 before this file existed
```

**New ids proposed:** two screens — `WS-238` Warehouse Grants (`RA-001`) and the next free id for Item
Prices (`RA-002`) — both taking the next free ids from `BUILD-SPEC-SCREENS.md` §1's allocation marker
rather than reusing a screen's grid. **No migration version is invented**: `RA-001` and `RA-008` ride
their owning tasks' existing bands (`P1-18`/`P1-05` in `V510xxx`, `P2-01`'s `V510030`); `RA-002` asks
`P2-25` for the next free number **in the `warehouse-adapter-dealer` band `V520000`–`V520999`**, which
its own header already lists as `V520011`–`V520013` — `V520015` is free at the time of writing and the
task confirms it before authoring. Everything else is a seed row, a job, a toolbar action or a sentence
in a task file. All eight fold into existing tasks: `P0-02`, `P0-07`, `P0-13`, `P0-15` (×2), `P1-05`,
`P1-18`, `P2-01`, `P2-09`, `P2-25`.
