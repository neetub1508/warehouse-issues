# Warehouse — design set

**Adopted solutions:** [Global settings and resolved behaviour](GLOBAL-SETTINGS-DECISIONS.md) · [First-day setup](../INSTALL.md). Existing historical questions are resolved by this contract where named.


Pre-implementation design for the Classic **Warehouse and Inventory Management** product for
**manufacturing plant stores and storage** (`DECISIONS.md` `D-16`, 2026-10-22). It is a separate product
from the `dealer` module; dealer and retail/e-commerce features are removed. No production code lives
here.

**Modules:** `warehouse-base` · `warehouse` · `warehouse-3pl` · `warehouse-india` · **`warehouse-trade`**
(purchase + sales) · **`warehouse-manufacturing`** (BOM, production, MRP) · plus the CI-only
`warehouse-adapter-example` — packages `ai.warehousebase`, `ai.warehouse`, `ai.warehouse3pl`,
`ai.warehouseindia`, `ai.warehousetrade`, `ai.warehousemanufacturing` · prefixes `whb_` `wh_` `wh3_`
`whin_` `wht_` `whm_` (`whae_` for the example) · Flyway **V500000–V569999**. The dealer and services
adapters (`whad_`, `whas_`, `V520000`–`V521999`) were removed and their bands stay reserved.

**Start here for the re-target:** [`reviews/R27-client-p2p-stores-gap.md`](reviews/R27-client-p2p-stores-gap.md)
(the client purchase-to-stores gap) → [`reviews/R28-manufacturing-storage-retarget-impact.md`](reviews/R28-manufacturing-storage-retarget-impact.md)
(impact and decisions; §8b is authoritative) → `DECISIONS.md` `D-16` → the per-area requirements in
[`frd/`](frd/) (`FRD-REM`, `FRD-STORES`, `FRD-TRADE`, `FRD-MFG`) and the workflow contracts in
[`contracts/`](contracts/). Phases `P7` → `P8` → {`P9`, `P10`} (`IMPLEMENTATION-PLAN.md` §1.9). Reviews
R1–R26, the gap registers and `competitive/` predate `D-16` and are historical.

---

## Read in this order

| # | Document | For | Why |
|---|---|---|---|
| 1 | **[DECISIONS.md](DECISIONS.md)** | Everyone | **The spine. Read this first, always.** Module names, packages, Flyway bands, table prefixes, id namespaces, the version ladder, `D-1`…`D-16`, `OD-1`…`OD-46`, `L-1`…`L-15`, and the authoring rules. **It wins over every other document here** except `reviews/R1` on a question about the existing codebase |
| 2 | **[IRREVERSIBLE.md](IRREVERSIBLE.md)** | Whoever writes a migration | **Free now, impossible later.** 67 merged rows, the four points of no return, and the full v1 column set per table — including every column whose *feature* ships in v1.1, v2 or v3. **Check this immediately before writing any migration.** If you read only two documents before building, read this and `DECISIONS.md` |
| 3 | **[WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md](WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md)** | Everyone | The spec. **471 requirements** `FR-001`…`FR-471` in 29 areas (24 **WITHDRAWN by `D-16`**), each carrying its module, version, phase and the findings it closes. The re-target adds **190** more, `FR-480`…`FR-669`, in [`frd/`](frd/) — `FRD-REM` 20 · `FRD-STORES` 40 · `FRD-TRADE` 80 · `FRD-MFG` 50 — **661 in all**. **This document wins over the build spec, which wins over the screens** |
| 4 | **[DATA-MODEL.md](DATA-MODEL.md)** | Engineers, reviewers | **478 tables** across `whb_` `wh_` `wht_` `whin_` `whm_` `wh3_` and the adapters (§8.1), the ER diagrams, §3 the split proof (every crossing FK, proven to point downward), §5 money and rounding, §6 the invariants as enforceable `I-n` constraints with their SQL, §7 the migration allocation. **This is the migration authority** |
| 5 | **[GAP-REGISTER.md](GAP-REGISTER.md)** · **[GAP-REGISTER-R2.md](GAP-REGISTER-R2.md)** · **[GAP-REGISTER-R3.md](GAP-REGISTER-R3.md)** · **[GAP-REGISTER-R4.md](GAP-REGISTER-R4.md)** | Everyone | The disposition of all **575 findings** across seven lenses — CITED, COVERED-uncited, DECIDED, WONTFIX, and the honest `NEEDS-TASK` column. Plus the BLOCKER audit and the ship-blockers. **`-R2` does the same for round 2's 62 findings** across eight further lenses, and records the thirteen requirements and five tasks they added. **`-R3` dispositions round 3's 52 findings** across six lenses, and **`-R4` round 4's 83** across five — including `D-14`'s branch↔warehouse junction and the fold plan that added `FR-460`…`FR-469` and six task files. **Read before starting P0** |
| 6 | **[IMPLEMENTATION-PLAN.md](IMPLEMENTATION-PLAN.md)** | Delivery | 12 phases, **200 tasks** (144 in P0–P6, 7 of them VOID by `D-16`; 56 in P7–P10, §1.9 and §2.8.1–§2.8.4), the critical path, the highest-risk tasks, the v1 cut line, the platform prerequisites, and the open decisions as dated gates |
| 7 | **[SCENARIO-CATALOGUE.md](SCENARIO-CATALOGUE.md)** | QA, reviewers | **411 scenarios** in Given/When/Then, plus **257** in the [`frd/`](frd/) area files — 668 in all. **These are the acceptance criteria** — a task issue names its subset, and "done" means walked in a running application |
| 8 | **[BUILD-SPEC-SCREENS.md](BUILD-SPEC-SCREENS.md)** | Engineers | **255 screen blocks**, plus **72** in the [`frd/`](frd/) area files — 327 in all: the canonical reference page each one copies, `gridIdentifier`, filter scope, cache names, permissions, columns, filters, export columns, modals, and the mobile counterpart (no re-target phase has a mobile screen) |
| 9 | **[PORT-AND-ADAPTER-CONTRACT.md](PORT-AND-ADAPTER-CONTRACT.md)** | Adapter authors, the logistics team | 75 normative clauses `PC-01`…`PC-75`: the movement port wire contract, idempotency and batch semantics, the outbox, reservations, the external-ref registries, the open catalogues, and the build-time test that proves loose coupling |
| 10 | **[MODULE-INTEGRATION.md](MODULE-INTEGRATION.md)** | Whoever builds P0 | The 18-touchpoint wiring runbook — no dealer or services profile since `D-16`; `warehouse-trade` and `warehouse-manufacturing` follow the `warehouse-india` column. Getting this wrong means the module does not ship — or ships and silently loads nothing |
| 11 | **[PLATFORM-DEPENDENCIES.md](PLATFORM-DEPENDENCIES.md)** | Delivery, platform team | What warehouse needs **from** platform: 14 capabilities that fit, 14 that shape-mismatch, and **6 that do not exist and block shipping** — no restore, no label rendering, no outbox, no offline queue, no service principal, no tenancy |
| 12 | **[INDIA-LOCALISATION-PACK.md](INDIA-LOCALISATION-PACK.md)** | Product, India delivery | The two waves, the core hooks that cannot be added later, and a 21-row threshold register where every value carries its knowledge-cutoff date and a **re-verify before build** instruction |
| 13 | **[COEXISTENCE.md](COEXISTENCE.md)** | Product | The cost of keeping `accessories` inventory permanently separate, named and itemised — and the two v1 mitigations that make an otherwise **undetectable** double-count detectable — **historical since `D-16`**, which deletes the accessories coexistence features (category ownership, external snapshots, coexistence report) and amends `D-9` |
| 14 | **[COMPETITOR-BENCHMARK.md](COMPETITOR-BENCHMARK.md)** | Product, sales | 236 capabilities across six market segments, where we win, and — the section not to soften — **where we lose, by version, with the products named** |
| 15 | **[DESIGN-SET-DEFECTS.md](DESIGN-SET-DEFECTS.md)** | Anyone building from this set | **55 entries** — every defect found *in this design set* by its own authors and its own checker: fixed, open, or referred. `X-001`…`X-038` are the merge of two concurrent logs, `X-039`…`X-053` were computed by traceability commands, `X-054` came from review round 2. **Append-only: a fixed entry changes Status and names the file, it is never deleted.** Read it before trusting a cross-document claim |
| 16 | [`reviews/`](reviews/) | Anyone challenging a claim | The evidence reports this design set was derived from, 27,861 lines — `R1`–`R7` are round 1 (575 findings), `R8`–`R15` round 2 (62), `R16`–`R21` round 3 (52), `R22`–`R26` round 4 (83), then the re-target: `R27` the client purchase-to-stores gap, `R28` the re-target impact (§8b authoritative), and `R29` the dual-engine functional review of the four areas (five files, 145 findings). [`RETARGET-PROGRAM-STATUS.md`](reviews/RETARGET-PROGRAM-STATUS.md) says where the re-target stands. `wc -l docs/reviews/*.md` |
| 17 | [`contracts/`](contracts/) | The `functional-reviewer` agent | **28** functional contracts — the machine-checkable behaviour spec per workflow: 3 core, 7 stores, 10 `trade-*`, 8 `mfg-*` |

> **Precedence.** `DECISIONS.md` wins over everything. The FRD wins over the build spec, which wins
> over the screens. Where any document disagrees with **`reviews/R1-codebase-reality.md`** about what
> the *existing* codebase does, **R1 wins** — it carries `file:line` evidence.

---

## Before you build anything

```bash
python3 tools/check-design-set.py          # 13 integrity checks; exit 0 clean, 1 violations
```

It verifies that every `FR-nnn`, `WH-SC-nnn`, `WS-nnn`, table name and finding id resolves; that every
Flyway version is claimed by exactly one task inside its module's band; that every task has its
required sections and sits in exactly one epic; and that no id is used for two different things.

Each check exists because of a specific failure that has already cost this organisation a rebuild
cycle — the reasons are in [`../tools/README.md`](../tools/README.md).

## What "directly usable" means here

Every task issue in [`../issues/`](../issues/) is written so an engineer — or an agent running
`/create-entity`, `/create-page` or `/modify` — can build it without going back to first principles:

- the **migration numbers are pre-allocated per task**, so parallel work cannot collide
- every grid names its `gridIdentifier`, its `COMMON_FILTER_CONFIGS` scope, its cache names and its
  permission resource
- every task states which module it lands in
- acceptance criteria are the numbered scenarios from [SCENARIO-CATALOGUE.md](SCENARIO-CATALOGUE.md),
  not prose
- **the traps that have cost a rebuild cycle in this codebase are named on the task that will hit
  them**, with `file:line`
- every task that precedes a point of no return says so in bold, and lists the columns bound to it

## Two premises of the prior design set were false

Both were load-bearing, and both are corrected here:

1. **The Flyway bands the brief proposed are occupied.** `V900000`–`V909999` holds 135 dealer OEM-seed
   migrations and `V910000`–`V919999` holds 434 platform per-client migrations whose version numbers
   are *deliberately reused across clients*. `FlywayConfiguration` renumbers legacy history rows into
   both bands and then deletes duplicates — so a collision does not crash, it silently destroys
   history.
2. **The prior warehouse product's own build methodology was wrong.** Fourteen of its documents
   instruct the builder to edit already-shipped migration files in place, attributing the rule to
   CLAUDE.md. That rule is not in CLAUDE.md, and the house style is the opposite.

Neither is a criticism of that work — it was written against a different checkout. It is the reason
**nothing here is inherited without re-verification.**
