# GAP-REGISTER — the disposition of every review finding

<!-- check-design-set: scenario-citations file WH-SC-301 — the allocation marker from SCENARIO-CATALOGUE.md §5 rule 3, not a scenario. This register cites it in §3.4 to explain the checker's own false positives (X-040) -->
<!-- check-design-set: finding-citations file T-244 T-264 T-325 T-326 T-337 E-754 E-1 E-8 — the eight dangling citations this register reports in §3.7 and DESIGN-SET-DEFECTS.md X-045. Naming them is the finding; they are quoted, not used -->
<!-- check-design-set: screen-citations file WS-238 — the screen id X-001's fix allocates for the marketplace-claim queue; BUILD-SPEC-SCREENS.md §1 has not yet carried the row (X-001, check-12) -->

> **What this document is for.** `DECISIONS.md` `D-12` says *"every capability found by any lens is
> placed in a version and carried in a task file **now**"* and *"every one of the 575 findings is
> dispositioned into a task in `GAP-REGISTER.md`"*. This is that document, and it is written to be
> **falsifiable**: every count below carries the command that produced it, and where the claim does
> not hold, the number is printed rather than rounded away.
>
> **The failure this exists to prevent.** The accounting programme failed the same way four times:
> findings were *indexed* and never *traced*, and each round looked finished and was not. Indexing
> feels like closure. It is not. `IMPLEMENTATION-PLAN.md` §11 item 5 already names the exposure —
> *"until `GAP-REGISTER.md` exists, 'every finding is dispositioned' is an intention, not a computed
> fact"*. It now exists, and the honest answer is in §4: **fourteen findings are owned by nothing**,
> one of them a segment BLOCKER.

| | |
|---|---|
| **Date** | 2026-09-02 |
| **Authority** | Subordinate to [`DECISIONS.md`](DECISIONS.md) on modules, bands, prefixes, namespaces and the ladder. Subordinate to `reviews/R1` on any claim about the live `classic` checkout |
| **Universe** | `reviews/R1`–`R7` — **575** findings (§1) |
| **Task set** | `issues/pN-nn.md` — **138** task files, 8 phase epics, 1 master epic |
| **Method** | reading + `grep` + `python3` only. No `mvn`/`npm`/`tsc`/`psql` (Docker-only build, CLAUDE.md). Every count carries its command |
| **Companion** | [`DESIGN-SET-DEFECTS.md`](DESIGN-SET-DEFECTS.md) — the merged defect log this register's §3 failures feed |

---

## §1 · The finding universe

### 1.1 The count, computed

```bash
cd docs/reviews
for f in R1-codebase-reality.md:C R2-tier1-wms-audit.md:T R3-erp-midmarket-audit.md:E \
         R4-fulfilment-3pl-audit.md:F R5-standards-industry-ops.md:S \
         R6-prior-art-triage.md:P R7-logistics-supply-chain-seam.md:G; do
  file=${f%%:*}; pre=${f##*:}
  printf '%-34s %s\n' "$file" "$(grep -oE "\b$pre-[0-9]{3}\b" "$file" | sort -u | wc -l)"
done
```

| Lens | Review | Namespace (`DECISIONS.md` §6) | Findings | BLOCKER | MAJOR | MINOR |
|---|---|---|---|---:|---:|---:|
| R1 | `R1-codebase-reality.md` | `C-001`…`C-050` | **50** | 5 | 25 | 20 |
| R2 | `R2-tier1-wms-audit.md` | `T-001`…`T-097` **+ `T-020a`** | **98** | 28 | 35 | 35 |
| R3 | `R3-erp-midmarket-audit.md` | `E-001`…`E-090` | **90** | 16 | 54 | 20 |
| R4 | `R4-fulfilment-3pl-audit.md` | `F-001`…`F-093` | **93** | 21 | 51 | 21 |
| R5 | `R5-standards-industry-ops.md` | `S-001`…`S-098` | **98** | 36 | 54 | 8 |
| R6 | `R6-prior-art-triage.md` | `P-001`…`P-060` | **60** | 6 | 33 | 21 |
| R7 | `R7-logistics-supply-chain-seam.md` | `G-001`…`G-086` | **86** | 11 | 36 | 39 |
| | | | **575** | **123** | **288** | **164** |

Severity was read off each review's own definition line, whose shape differs per lens
(`| **C-nnn** | **BLOCKER** |` in R1/R5, `### T-nnn — BLOCKER —` in R2,
`**E-nnn · title** — **BLOCKER**` in R3, the bold line under `### \`F-nnn\`` in R4,
`### \`P-nnn\` · VERDICT · **BLOCKER**` in R6, `**\`G-nnn\` · BLOCKER ·` in R7). All 575 carry one;
`P-014`, `P-054`, `P-055` and `P-060` needed the `### \`P-nnn\` · KEEP/DUPLICATE/OBSOLETE (…) ·`
variant and were read individually.

### 1.2 No id was withdrawn, and one was never in the contiguous range

**Contiguity, computed.** For each lens, `comm` of the ids present against `seq` of the declared
range returns empty in both directions:

```
=== C (expect 001..50) ===  missing:   extra:
=== T (expect 001..97) ===  missing:   extra:
=== E (expect 001..90) ===  missing:   extra:
=== F (expect 001..93) ===  missing:   extra:
=== S (expect 001..98) ===  missing:   extra:
=== P (expect 001..60) ===  missing:   extra:
=== G (expect 001..86) ===  missing:   extra:
```

**Nothing was withdrawn and nothing is unissued.** The seven declared ranges sum to **574**:

```bash
echo $((50+97+90+93+98+60+86))     # → 574
```

**The 575th is `T-020a`.** R2's own header states it — *"Findings raised | **98** (`T-001` …
`T-097`, plus `T-020a`)"* (`R2-tier1-wms-audit.md:84`) — it has a real heading at `:1020`
(*"Archiving must write an opening-balance row, or reconstructibility dies at the archive
boundary"*, MINOR), it is cited by `FR-023`, and `issues/p6-01.md:50` closes it. `issues/00-EPIC-master.md:15`
already reconciles the 574/575 gap this way; **this register confirms it by reading the finding.**

```bash
grep -rohE '\b[CTEFSPG]-[0-9]{3}[a-z]\b' docs/reviews/*.md | sort -u   # → T-020a  (the only one)
```

**Consequence for tooling.** `T-020a` is invisible to the obvious regex `[CTEFSPG]-[0-9]{3}\b` —
the `\b` fails between `0` and `a`. Any script that counts findings, including this register's own
first pass, undercounts by one unless the suffix form is matched explicitly.
`tools/check-design-set.py` gets this right: its R2 register reports **98 findings**.

---

## §2 · The disposition of every finding

### 2.1 The buckets, and how each was decided

| Bucket | Test applied | Command |
|---|---|---|
| **CITED** | a task file's `## Closes` section names the id | `awk '/^## Closes/{c=1;next} /^## /{c=0} c' issues/pN-nn.md` |
| **COVERED-uncited** | no `## Closes` names it, but a `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` row's `Closes` column cites it — and every `FR-nnn` is owned by exactly one task (§3.3) — or a named design-set row (`I-nn`, `D-n`, `OD-n`, a `DATA-MODEL.md` fold-in row) carries the behaviour. The owning artefact is printed in every row | §2.3 |
| **DECIDED** | a `D-n` answers it, so no task is needed | read individually |
| **OPEN-DECISION** | it *is* an `OD-n` and nothing else owns it | §2.2 — **zero members, and that is a finding in itself** |
| **WONTFIX** | the lens itself, or `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §10's refusal table, declines it. Reason and re-entry path in the row | read individually |
| **NEEDS-TASK** | nothing owns it. **The honest failure column** | §4 |

**The 68 findings that neither a task nor an FR cites were read one by one**, not bucketed by rule:

```bash
# findings cited by no task's ## Closes AND by no FRD row
comm -23 uncited.txt <(cut -f1 uncited_via_fr.txt | sort -u) | wc -l    # → 68
```

### 2.2 `OPEN-DECISION` is empty, and that is load-bearing

`DECISIONS.md` §3 names four findings as the source of an open decision — `G-025`, `G-026`, `G-050`,
`G-064`:

```bash
awk '/^## 3\. OD/,/^## 4\./' docs/DECISIONS.md | grep -oE '\b[CTEFSPG]-[0-9]{3}\b' | sort -u
# → G-025 G-026 G-050 G-064
```

**All four are also `CITED`** — `G-025` by `P0-08`/`P1-08`/`P5-01`, `G-026` by `P0-08`/`P1-08`/`P6-05`,
`G-050` by `P1-05`/`P1-11`/`P6-09`, `G-064` by `P0-04`. So no finding's *only* disposition is
"it became an open decision", and the bucket is legitimately empty. **It is not empty because the
question was skipped.**

### 2.3 The tally

```bash
cut -f3 DISPOSITION.tsv | sort | uniq -c | sort -rn
```

| Disposition | Count | Share |
|---|---:|---:|
| **CITED** — a task's `## Closes` names it | **378** | 65.7 % |
| **COVERED-uncited** — owned, but the id is not in a `## Closes` | **162** | 28.2 % |
| **WONTFIX** — declined, with a reason and a re-entry path | **15** | 2.6 % |
| **NEEDS-TASK** — **nothing owns it** | **14** | 2.4 % |
| **DECIDED** — answered by a `D-n` | **6** | 1.0 % |
| **OPEN-DECISION** | **0** | — |
| | **575** | 100 % |

**Owned one way or another: 561 of 575 (97.6 %).** Not 100 %, and §4 says which fourteen.

### 2.4 Per lens

```bash
awk -F'\t' '{print substr($1,1,1), $3}' DISPOSITION.tsv | sort | uniq -c
```

| Lens | CITED | COVERED-uncited | DECIDED | WONTFIX | NEEDS-TASK | Total |
|---|---:|---:|---:|---:|---:|---:|
| **R1 `C-`** | 47 | 1 | 0 | 2 | 0 | **50** |
| **R2 `T-`** | 72 | 26 | 0 | 0 | 0 | **98** |
| **R3 `E-`** | 55 | 30 | 1 | 0 | 4 | **90** |
| **R4 `F-`** | 71 | 20 | 0 | 1 | 1 | **93** |
| **R5 `S-`** | 56 | 31 | 1 | 3 | 7 | **98** |
| **R6 `P-`** | 46 | 7 | 1 | 5 | 1 | **60** |
| **R7 `G-`** | 31 | 47 | 3 | 4 | 1 | **86** |
| | **378** | **162** | **6** | **15** | **14** | **575** |

**R7 is the outlier and the reason is structural, not sloppy.** Only 31 of its 86 findings are cited
by a task, because most of R7 is about a `logistics` module that does not exist yet: its findings
land in the FRD as v1 *seam* requirements (47 `COVERED-uncited`) rather than as work a v1 task does.
The register carries them as owned because the FRD row is owned; **a reader planning the logistics
module should start from R7, not from `issues/`.**

### 2.5 The register

Every row of the universe, in one table. `Owner` names the artefact that discharges the finding:
a task id for `CITED`, an `FR-nnn`→task pair or a named design-set row for `COVERED-uncited`, and
nothing for `NEEDS-TASK`.

| Finding | Sev | Disposition | Owner | Note |
|---|---|---|---|---|
| `C-001` | BLOCKER | **CITED** | `P0-01` | — |
| `C-002` | BLOCKER | **CITED** | `P0-01` | — |
| `C-003` | MAJOR | **CITED** | `P0-01` | — |
| `C-004` | MINOR | **CITED** | `P0-01` | — |
| `C-005` | MAJOR | **CITED** | `P0-01` | — |
| `C-006` | MAJOR | **CITED** | `P0-01` | — |
| `C-007` | MINOR | **WONTFIX** | — | R1:506 — "Skipping it is the house style. Do not spend an issue on it". Re-entry: if `FlywayConfiguration` is ever made module-complete |
| `C-008` | MINOR | **WONTFIX** | — | R1:507 — "No edit needed"; Spring relaxed binding covers the unlisted modules. Re-entry: none |
| `C-009` | MAJOR | **CITED** | `P0-01` | — |
| `C-010` | MINOR | **COVERED-uncited** | — | `P0-01` acceptance — "Railway and `startX2.sh` are either edited or carry a written out-of-scope decision — silence is the defect" |
| `C-011` | MAJOR | **CITED** | `P0-01` | — |
| `C-012` | MAJOR | **CITED** | `P0-01` | — |
| `C-013` | MINOR | **CITED** | `P0-01` | — |
| `C-014` | MAJOR | **CITED** | `P0-01` `P6-10` | — |
| `C-015` | MINOR | **CITED** | `P0-01` | — |
| `C-016` | MINOR | **CITED** | `P1-05` | — |
| `C-017` | MAJOR | **CITED** | `P0-15` | — |
| `C-018` | MAJOR | **CITED** | `P1-04` | — |
| `C-019` | MAJOR | **CITED** | `P1-09` | — |
| `C-020` | MAJOR | **CITED** | `P1-10` | — |
| `C-021` | BLOCKER | **CITED** | `P0-02` | — |
| `C-022` | BLOCKER | **CITED** | `P0-03` `P0-09` | — |
| `C-023` | BLOCKER | **CITED** | `P1-13` `P2-04` | — |
| `C-024` | MAJOR | **CITED** | `P0-02` `P0-03` | — |
| `C-025` | MAJOR | **CITED** | `P0-03` `P0-08` | — |
| `C-026` | MAJOR | **CITED** | `P0-02` `P1-01` `P1-02` | — |
| `C-027` | MAJOR | **CITED** | `P0-17` `P2-16` | — |
| `C-028` | MAJOR | **CITED** | `P0-02` `P0-05` `P1-07` | — |
| `C-029` | MINOR | **CITED** | `P0-05` `P1-05` | — |
| `C-030` | MINOR | **CITED** | `P0-07` `P1-05` | — |
| `C-031` | MAJOR | **CITED** | `P0-06` `P1-08` `P1-13` | — |
| `C-032` | MAJOR | **CITED** | `P1-01` `P1-04` `P2-27` | — |
| `C-033` | MAJOR | **CITED** | `P0-03` `P1-05` `P2-21` | — |
| `C-034` | MAJOR | **CITED** | `P2-25` `P2-26` `P3-20` `P3-21` | — |
| `C-035` | MAJOR | **CITED** | `P0-06` `P1-08` | — |
| `C-036` | MAJOR | **CITED** | `P2-29` | — |
| `C-037` | MAJOR | **CITED** | `P0-02` | — |
| `C-038` | MAJOR | **CITED** | `P0-02` `P0-13` | — |
| `C-039` | MAJOR | **CITED** | `P0-04` `P0-08` | — |
| `C-040` | MINOR | **CITED** | `P0-03` `P0-10` `P3-02` | — |
| `C-041` | MINOR | **CITED** | `P0-01` `P0-14` | — |
| `C-042` | MINOR | **CITED** | `P0-02` `P1-20` | — |
| `C-043` | MINOR | **CITED** | `P1-20` `P2-29` | — |
| `C-044` | MINOR | **CITED** | `P0-16` `P3-01` | — |
| `C-045` | MINOR | **CITED** | `P0-03` `P2-01` `P2-21` | — |
| `C-046` | MINOR | **CITED** | `P0-01` `P0-16` | — |
| `C-047` | MINOR | **CITED** | `P0-01` | — |
| `C-048` | MINOR | **CITED** | `P0-13` `P1-11` | — |
| `C-049` | MINOR | **CITED** | `P0-01` | — |
| `C-050` | MINOR | **CITED** | `P0-01` `P1-19` | — |
| `E-001` | BLOCKER | **CITED** | `P0-12` `P2-16` | — |
| `E-002` | MAJOR | **CITED** | `P2-18` | — |
| `E-003` | MAJOR | **COVERED-uncited** | `FR-017`→`P0-08` · `FR-032`→`P0-08` | cited by the FRD row, not by the task |
| `E-004` | MAJOR | **COVERED-uncited** | `FR-018`→`P0-02` · `FR-357`→`P0-04` | cited by the FRD row, not by the task |
| `E-005` | MINOR | **CITED** | `P1-04` | — |
| `E-006` | MAJOR | **CITED** | `P0-14` `P2-25` | — |
| `E-007` | BLOCKER | **COVERED-uncited** | `FR-048`→`P1-01` · `FR-049`→`P1-01` | cited by the FRD row, not by the task |
| `E-008` | MAJOR | **COVERED-uncited** | `FR-050`→`P1-01` | cited by the FRD row, not by the task |
| `E-009` | MAJOR | **COVERED-uncited** | `FR-009`→`P0-02` · `FR-055`→`P1-02` | cited by the FRD row, not by the task |
| `E-010` | MINOR | **COVERED-uncited** | `FR-030`→`P0-02` | cited by the FRD row, not by the task |
| `E-011` | MINOR | **COVERED-uncited** | `FR-065`→`P1-03` | cited by the FRD row, not by the task |
| `E-012` | MAJOR | **COVERED-uncited** | `FR-059`→`P1-02` | cited by the FRD row, not by the task |
| `E-013` | MAJOR | **COVERED-uncited** | `FR-053`→`P1-03` · `FR-252`→`P1-03` | cited by the FRD row, not by the task |
| `E-014` | BLOCKER | **COVERED-uncited** | `FR-094`→`P1-07` · `FR-095`→`P1-07` | cited by the FRD row, not by the task |
| `E-015` | MAJOR | **COVERED-uncited** | — | `P2-16` via `FR-234`/`FR-236` — `whb_cost_layers` is keyed with the lot (`DATA-MODEL.md` §2.1) |
| `E-016` | MAJOR | **CITED** | `P4-05` | — |
| `E-017` | MAJOR | **CITED** | `P2-07` | — |
| `E-018` | MAJOR | **CITED** | `P2-05` | — |
| `E-019` | MAJOR | **CITED** | `P2-05` | — |
| `E-020` | MAJOR | **CITED** | `P1-12` | — |
| `E-021` | MAJOR | **CITED** | `P1-13` | — |
| `E-022` | MINOR | **CITED** | `P1-16` | — |
| `E-023` | MAJOR | **COVERED-uncited** | `FR-135`→`P1-15` | cited by the FRD row, not by the task |
| `E-024` | MAJOR | **COVERED-uncited** | `FR-107`→`P0-02` | cited by the FRD row, not by the task |
| `E-025` | MINOR | **COVERED-uncited** | — | `P1-07` via `FR-100` — the LPN **is** the handling unit, columns in v1 |
| `E-026` | BLOCKER | **COVERED-uncited** | `FR-001`→`P0-02` | cited by the FRD row, not by the task |
| `E-027` | MAJOR | **COVERED-uncited** | `FR-122`→`P1-12` | cited by the FRD row, not by the task |
| `E-028` | MAJOR | **CITED** | `P5-10` | — |
| `E-029` | MINOR | **CITED** | `P2-13` | — |
| `E-030` | MAJOR | **COVERED-uncited** | — | `P2-06` via `E-042`/`FR-163`/`FR-166` (allocation rows) and `P2-10`'s shipment state ladder |
| `E-031` | MINOR | **COVERED-uncited** | — | `P2-09`/`P3-06` via `F-029`; version settled by `COMPETITOR-BENCHMARK.md` §9 row 10 (v1.1) |
| `E-032` | MAJOR | **CITED** | `P2-02` | — |
| `E-033` | MAJOR | **CITED** | `P2-01` `P2-15` | — |
| `E-034` | MAJOR | **CITED** | `P2-01` `P2-23` | — |
| `E-035` | BLOCKER | **CITED** | `P2-16` | — |
| `E-036` | MAJOR | **CITED** | `P2-17` | — |
| `E-037` | MINOR | **CITED** | `P2-17` | — |
| `E-038` | MAJOR | **CITED** | `P2-04` | — |
| `E-039` | MAJOR | **CITED** | `P2-04` | — |
| `E-040` | MAJOR | **CITED** | `P2-15` `P2-21` `P5-18` | — |
| `E-041` | MINOR | **CITED** | `P5-18` | — |
| `E-042` | MAJOR | **CITED** | `P2-06` | — |
| `E-043` | MAJOR | **CITED** | `P2-07` | — |
| `E-044` | MAJOR | **CITED** | `P3-10` `P3-11` `P6-12` | — |
| `E-045` | BLOCKER | **CITED** | `P2-01` `P2-15` | — |
| `E-046` | MAJOR | **COVERED-uncited** | `FR-020`→`P0-07` · `FR-251`→`P0-07` · `FR-404`→`P0-15` · `FR-405`→`P1-18` | cited by the FRD row, not by the task |
| `E-047` | BLOCKER | **COVERED-uncited** | `FR-056`→`P1-02` · `FR-066`→`P1-03` · `FR-318`→`P0-02` · `FR-319`→`P1-03` | cited by the FRD row, not by the task |
| `E-048` | BLOCKER | **COVERED-uncited** | `FR-079`→`P1-05` · `FR-080`→`P1-05` | cited by the FRD row, not by the task |
| `E-049` | BLOCKER | **CITED** | `P2IN-03` | — |
| `E-050` | BLOCKER | **CITED** | `P2-18` | — |
| `E-051` | BLOCKER | **CITED** | `P2IN-02` | — |
| `E-052` | MAJOR | **CITED** | `P2-20` | — |
| `E-053` | BLOCKER | **CITED** | `P2-20` | — |
| `E-054` | MAJOR | **CITED** | `P2IN-03` `P4-02` | — |
| `E-055` | BLOCKER | **COVERED-uncited** | `FR-071`→`P1-03` | cited by the FRD row, not by the task |
| `E-056` | MAJOR | **CITED** | `P2-24` | — |
| `E-057` | MAJOR | **CITED** | `P2-07` `P2-24` | — |
| `E-058` | MAJOR | **CITED** | `P2-24` | — |
| `E-059` | MINOR | **COVERED-uncited** | `FR-418`→`P1-10` | cited by the FRD row, not by the task |
| `E-060` | MAJOR | **CITED** | `P5-13` | — |
| `E-061` | MAJOR | **CITED** | `P2-15` | — |
| `E-062` | MAJOR | **CITED** | `P3-19` | — |
| `E-063` | MAJOR | **CITED** | `P5-15` | — |
| `E-064` | MAJOR | **CITED** | `P5-15` | — |
| `E-065` | BLOCKER | **CITED** | `P2-25` `P2-26` | — |
| `E-066` | MAJOR | **CITED** | `P2-01` `P2-15` `P3-18` `P6-02` | — |
| `E-067` | MAJOR | **CITED** | `P2-15` | — |
| `E-068` | MAJOR | **CITED** | `P3-18` | — |
| `E-069` | MINOR | **NEEDS-TASK** | — | `grep -rn "pricing_matri\|pricing matrix" docs/ issues/` outside `reviews/` → 0. No FR, no table, no task |
| `E-070` | MINOR | **CITED** | `P1-18` | — |
| `E-071` | MAJOR | **COVERED-uncited** | `FR-062`→`P1-02` | cited by the FRD row, not by the task |
| `E-072` | BLOCKER | **CITED** | `P3-01` `P3-04` | — |
| `E-073` | MAJOR | **CITED** | `P2-14` `P3-08` | — |
| `E-074` | MINOR | **COVERED-uncited** | `FR-221`→`P0-16` | cited by the FRD row, not by the task |
| `E-075` | MAJOR | **CITED** | `P2-20` | — |
| `E-076` | MAJOR | **CITED** | `P2-05` `P2-20` | — |
| `E-077` | MAJOR | **CITED** | `P2-21` | — |
| `E-078` | MINOR | **NEEDS-TASK** | — | The price-list home is a boundary decision no document records. `grep "price list" MODULE-INTEGRATION.md` → 0 |
| `E-079` | MINOR | **COVERED-uncited** | — | Events half: `P0-11` via `FR-330` (outbox). Marketplace half: `P5-09` (channel accounts) |
| `E-080` | MINOR | **COVERED-uncited** | `FR-141`→`P1-13` | cited by the FRD row, not by the task |
| `E-081` | MINOR | **NEEDS-TASK** | — | `grep -rn "supplier_claim\|supplier claim" docs/ issues/` outside `reviews/` → 0 |
| `E-082` | MAJOR | **DECIDED** | — | `D-5` — `owner_id` `NOT NULL` in v1 and in the position key is exactly E-082's three things |
| `E-083` | MAJOR | **COVERED-uncited** | `FR-061`→`P1-04` · `FR-368`→`P1-04` | cited by the FRD row, not by the task |
| `E-084` | MAJOR | **CITED** | `P3-17` | — |
| `E-085` | MINOR | **NEEDS-TASK** | — | `COEXISTENCE.md` §5.4 `M4` (shared vocabularies) is named in **no** task file — `grep -ohE '\bM[1-9]\b' issues/p*.md` returns M1 M2 M3 M5 M6 M8 M9, never M4 |
| `E-086` | MAJOR | **CITED** | `P2-27` | — |
| `E-087` | MINOR | **COVERED-uncited** | `FR-350`→`P0-14` · `FR-367`→`P0-04` | cited by the FRD row, not by the task |
| `E-088` | BLOCKER | **CITED** | `P2-18` `P2-19` | — |
| `E-089` | MAJOR | **CITED** | `P3-18` | — |
| `E-090` | MINOR | **COVERED-uncited** | — | `P0-01` via `MODULE-INTEGRATION.md` §14 — the 23-step enumerated touchpoint runbook is E-090's list |
| `F-001` | BLOCKER | **CITED** | `P0-06` | — |
| `F-002` | BLOCKER | **CITED** | `P0-06` `P5-01` | — |
| `F-003` | MAJOR | **COVERED-uncited** | `FR-086`→`P1-05` · `FR-087`→`P1-05` | cited by the FRD row, not by the task |
| `F-004` | BLOCKER | **CITED** | `P5-08` | — |
| `F-005` | MAJOR | **COVERED-uncited** | `FR-060`→`P1-01` | cited by the FRD row, not by the task |
| `F-006` | MAJOR | **COVERED-uncited** | `FR-059`→`P1-02` | cited by the FRD row, not by the task |
| `F-007` | MAJOR | **CITED** | `P5-01` | — |
| `F-008` | MAJOR | **CITED** | `P5-08` | — |
| `F-009` | MINOR | **COVERED-uncited** | `FR-042`→`P0-02` · `FR-111`→`P0-06` | cited by the FRD row, not by the task |
| `F-010` | BLOCKER | **CITED** | `P5-08` | — |
| `F-011` | BLOCKER | **CITED** | `P0-08` `P0-11` `P5-03` | — |
| `F-012` | BLOCKER | **CITED** | `P5-03` | — |
| `F-013` | MAJOR | **CITED** | `P5-02` | — |
| `F-014` | MAJOR | **CITED** | `P5-02` | — |
| `F-015` | MAJOR | **CITED** | `P5-04` | — |
| `F-016` | MAJOR | **CITED** | `P2-28` `P5-04` | — |
| `F-017` | MAJOR | **CITED** | `P5-04` | — |
| `F-018` | MAJOR | **CITED** | `P5-05` | — |
| `F-019` | MAJOR | **CITED** | `P5-05` | — |
| `F-020` | MAJOR | **CITED** | `P5-05` | — |
| `F-021` | BLOCKER | **CITED** | `P5-05` | — |
| `F-022` | MINOR | **CITED** | `P6-07` | — |
| `F-023` | MAJOR | **CITED** | `P5-17` `P5-19` `P6-07` | — |
| `F-024` | MINOR | **CITED** | `P5-06` | — |
| `F-025` | MAJOR | **CITED** | `P4-10` | — |
| `F-026` | MAJOR | **COVERED-uncited** | `FR-207`→`P1-11` | cited by the FRD row, not by the task |
| `F-027` | MAJOR | **CITED** | `P5-09` | — |
| `F-028` | BLOCKER | **CITED** | `P0-09` `P2-07` | — |
| `F-029` | MAJOR | **CITED** | `P2-09` `P3-06` | — |
| `F-030` | MAJOR | **CITED** | `P1-06` `P1-15` `P2-10` | — |
| `F-031` | MAJOR | **CITED** | `P2-08` `P3-13` | — |
| `F-032` | MAJOR | **CITED** | `P2-08` `P5-10` | — |
| `F-033` | MAJOR | **CITED** | `P2-03` `P2-08` | — |
| `F-034` | MAJOR | **CITED** | `P2-07` `P3-13` | — |
| `F-035` | MINOR | **CITED** | `P5-09` | — |
| `F-036` | MAJOR | **CITED** | `P2-10` | — |
| `F-037` | MAJOR | **CITED** | `P0-09` `P5-11` | — |
| `F-038` | MAJOR | **CITED** | `P2-11` `P3-11` | — |
| `F-039` | MAJOR | **CITED** | `P3-08` | — |
| `F-040` | MAJOR | **CITED** | `P3-09` | — |
| `F-041` | MINOR | **CITED** | `P5-11` | — |
| `F-042` | BLOCKER | **CITED** | `P3-02` `P5-11` | — |
| `F-043` | MAJOR | **CITED** | `P5-11` | — |
| `F-044` | BLOCKER | **CITED** | `P5-12` | — |
| `F-045` | BLOCKER | **CITED** | `P5-12` | — |
| `F-046` | BLOCKER | **CITED** | `P2-12` `P5-12` | — |
| `F-047` | MAJOR | **CITED** | `P2-11` | — |
| `F-048` | MINOR | **COVERED-uncited** | — | `FR-095` (country of origin on the lot, `P1-05`); the v3 export/customs half is refused by FRD §10 row 15 |
| `F-049` | MINOR | **CITED** | `P5-09` | — |
| `F-050` | MAJOR | **CITED** | `P2-12` | — |
| `F-051` | MAJOR | **CITED** | `P5-13` | — |
| `F-052` | MAJOR | **CITED** | `P2-01` `P2-12` | — |
| `F-053` | MAJOR | **COVERED-uncited** | `FR-274`→`P0-05` | cited by the FRD row, not by the task |
| `F-054` | MAJOR | **COVERED-uncited** | `FR-270`→`P0-05` | cited by the FRD row, not by the task |
| `F-055` | MINOR | **CITED** | `P5-13` | — |
| `F-056` | MINOR | **CITED** | `P2-12` `P2-13` | — |
| `F-057` | MAJOR | **CITED** | `P3-10` `P3-11` | — |
| `F-058` | MAJOR | **CITED** | `P3-11` | — |
| `F-059` | BLOCKER | **CITED** | `P3-11` | — |
| `F-060` | MINOR | **CITED** | `P3-11` `P5-21` | — |
| `F-061` | MINOR | **CITED** | `P4-02` | — |
| `F-062` | MINOR | **CITED** | `P2-14` `P5-21` | — |
| `F-063` | BLOCKER | **CITED** | `P5-14` | — |
| `F-064` | BLOCKER | **CITED** | `P3-15` | — |
| `F-065` | MAJOR | **CITED** | `P2-21` `P5-19` | — |
| `F-066` | MAJOR | **CITED** | `P2-03` `P2-21` `P5-14` | — |
| `F-067` | MAJOR | **CITED** | `P2-05` | — |
| `F-068` | BLOCKER | **CITED** | `P2-05` `P2-12` | — |
| `F-069` | MINOR | **COVERED-uncited** | `FR-068`→`P1-03` · `FR-086`→`P1-05` | cited by the FRD row, not by the task |
| `F-070` | MINOR | **CITED** | `P3-15` | — |
| `F-071` | MINOR | **WONTFIX** | — | FRD §10 row 20 refuses the EPCIS repository; the emit shape is `IRR-20`'s v1 columns. Re-entry: a v3 projection, adapter-only |
| `F-072` | MINOR | **CITED** | `P6-04` | — |
| `F-073` | MINOR | **NEEDS-TASK** | — | India pharma licence register — the same unowned `whin_` group-H set as `S-035` |
| `F-074` | BLOCKER | **CITED** | `P2-08` `P2-21` | — |
| `F-075` | MAJOR | **CITED** | `P5-07` | — |
| `F-076` | MAJOR | **COVERED-uncited** | — | `P2-04` via `IRREVERSIBLE.md` `IRR-52` (`count_snapshot_quantity`). The v2 ABC/accuracy-KPI half is unowned |
| `F-077` | MAJOR | **CITED** | `P5-07` | — |
| `F-078` | MINOR | **CITED** | `P6-07` | — |
| `F-079` | MINOR | **CITED** | `P5-17` `P6-03` | — |
| `F-080` | MINOR | **COVERED-uncited** | `FR-092`→`P1-06` | cited by the FRD row, not by the task |
| `F-081` | BLOCKER | **COVERED-uncited** | `FR-017`→`P0-08` · `FR-029`→`P0-03` · `FR-032`→`P0-08` · `FR-033`→`P0-08` | cited by the FRD row, not by the task |
| `F-082` | BLOCKER | **COVERED-uncited** | `FR-004`→`P0-02` · `FR-005`→`P0-02` · `FR-006`→`P0-02` · `FR-035`→`P0-08` | cited by the FRD row, not by the task |
| `F-083` | BLOCKER | **COVERED-uncited** | `FR-007`→`P0-02` · `FR-008`→`P0-02` | cited by the FRD row, not by the task |
| `F-084` | BLOCKER | **COVERED-uncited** | `FR-018`→`P0-02` · `FR-036`→`P0-08` | cited by the FRD row, not by the task |
| `F-085` | MAJOR | **COVERED-uncited** | `FR-020`→`P0-07` | cited by the FRD row, not by the task |
| `F-086` | MAJOR | **COVERED-uncited** | `FR-330`→`P0-11` · `FR-333`→`P0-11` | cited by the FRD row, not by the task |
| `F-087` | MAJOR | **COVERED-uncited** | `FR-003`→`P0-04` · `FR-026`→`P0-02` · `FR-027`→`P0-02` · `FR-375`→`P0-04` | cited by the FRD row, not by the task |
| `F-088` | MAJOR | **CITED** | `P2-17` `P2-28` | — |
| `F-089` | MAJOR | **CITED** | `P2-02` | — |
| `F-090` | MAJOR | **CITED** | `P0-09` | — |
| `F-091` | MAJOR | **CITED** | `P2-06` | — |
| `F-092` | MINOR | **COVERED-uncited** | `FR-034`→`P0-08` | cited by the FRD row, not by the task |
| `F-093` | MAJOR | **COVERED-uncited** | `FR-009`→`P0-02` | cited by the FRD row, not by the task |
| `G-001` | MAJOR | **COVERED-uncited** | — | `P6-08` — the nullable `log_*` link columns are logistics-side; `p6-06.md` lists `log_carriers`/`log_customers` against `P6-08` |
| `G-002` | MAJOR | **CITED** | `P5-21` | — |
| `G-003` | MAJOR | **CITED** | `P5-21` | — |
| `G-004` | MINOR | **COVERED-uncited** | `FR-049`→`P1-01` · `FR-337`→`P1-11` | cited by the FRD row, not by the task |
| `G-005` | MINOR | **COVERED-uncited** | `FR-049`→`P1-01` · `FR-337`→`P1-11` | cited by the FRD row, not by the task |
| `G-006` | MINOR | **WONTFIX** | — | A defect in the prior-art TMS document's own headline count, not in this design set. Re-entry: the logistics FRD |
| `G-007` | MINOR | **WONTFIX** | — | R7 states "Referred, not adjudicated here" — a `logistics` HR-overlap question. Re-entry: the logistics FRD's pre-flight |
| `G-008` | MINOR | **WONTFIX** | — | Deferred to the logistics FRD: `grep "rate card" PORT-AND-ADAPTER-CONTRACT.md` → 0. Re-entry: `P6-08` |
| `G-009` | MAJOR | **COVERED-uncited** | — | `PORT-AND-ADAPTER-CONTRACT.md` §1.2 "The boundary rule, stated once" carries R4 §4.1's physical rule |
| `G-010` | MINOR | **COVERED-uncited** | `FR-339`→`P1-11` | cited by the FRD row, not by the task |
| `G-011` | MAJOR | **COVERED-uncited** | `FR-341`→`P1-11` | cited by the FRD row, not by the task |
| `G-012` | MAJOR | **COVERED-uncited** | `FR-341`→`P1-11` | cited by the FRD row, not by the task |
| `G-013` | MAJOR | **CITED** | `P2-10` `P6-08` | — |
| `G-014` | MAJOR | **COVERED-uncited** | `FR-092`→`P1-06` | cited by the FRD row, not by the task |
| `G-015` | MINOR | **COVERED-uncited** | `FR-092`→`P1-06` | cited by the FRD row, not by the task |
| `G-016` | MAJOR | **CITED** | `P5-21` | — |
| `G-017` | BLOCKER | **COVERED-uncited** | `FR-090`→`P1-05` · `FR-339`→`P1-11` | cited by the FRD row, not by the task |
| `G-018` | MAJOR | **CITED** | `P2-18` | — |
| `G-019` | MAJOR | **CITED** | `P2-02` | — |
| `G-020` | MAJOR | **CITED** | `P6-08` | — |
| `G-021` | MAJOR | **CITED** | `P6-08` | — |
| `G-022` | MINOR | **COVERED-uncited** | — | `p6-08.md` names it directly (body, not `## Closes`) |
| `G-023` | MAJOR | **CITED** | `P2-17` `P2-28` | — |
| `G-024` | MINOR | **CITED** | `P5-21` | — |
| `G-025` | BLOCKER | **CITED** | `P0-08` `P1-08` `P5-01` | — |
| `G-026` | MAJOR | **CITED** | `P0-08` `P1-08` `P6-05` | — |
| `G-027` | BLOCKER | **COVERED-uncited** | `FR-116`→`P1-08` · `FR-118`→`P1-08` | cited by the FRD row, not by the task |
| `G-028` | MAJOR | **COVERED-uncited** | — | `P6-08` — `p6-06.md`'s table assigns `log_carriers` and `log_customers` to `P6-08` |
| `G-029` | MAJOR | **CITED** | `P6-06` | — |
| `G-030` | MINOR | **COVERED-uncited** | `FR-119`→`P1-08` | cited by the FRD row, not by the task |
| `G-031` | MINOR | **COVERED-uncited** | `FR-118`→`P1-08` | cited by the FRD row, not by the task |
| `G-032` | MAJOR | **CITED** | `P2-07` `P3-05` `P6-05` | — |
| `G-033` | MINOR | **COVERED-uncited** | — | `P1-13` via `FR-128` — "Blind receipt is a first-class v1 flow" |
| `G-034` | MAJOR | **CITED** | `P5-10` | — |
| `G-035` | MAJOR | **COVERED-uncited** | `FR-041`→`P0-08` · `FR-066`→`P1-03` | cited by the FRD row, not by the task |
| `G-036` | MINOR | **CITED** | `P2-15` | — |
| `G-037` | MINOR | **NEEDS-TASK** | — | `grep -rin "drop.ship" docs/ issues/` outside `reviews/` → 0. R7 says decide in v1's FRD; nothing decided it |
| `G-038` | MINOR | **COVERED-uncited** | — | `D-5`'s `duty_status` v1 column + `whb_stock_statuses`/`whb_location_types` catalogues. Residual: the `BONDED`/`BONDED_ZONE` seed rows are not enumerated in `DATA-MODEL.md` |
| `G-039` | BLOCKER | **COVERED-uncited** | `FR-349`→`P0-14` · `FR-350`→`P0-14` · `FR-354`→`P0-14` | cited by the FRD row, not by the task |
| `G-040` | BLOCKER | **COVERED-uncited** | `FR-038`→`P1-13` · `FR-061`→`P1-04` | cited by the FRD row, not by the task |
| `G-041` | MAJOR | **COVERED-uncited** | `FR-357`→`P0-04` | cited by the FRD row, not by the task |
| `G-042` | BLOCKER | **CITED** | `P2-07` | — |
| `G-043` | MAJOR | **COVERED-uncited** | `FR-356`→`P0-14` | cited by the FRD row, not by the task |
| `G-044` | MINOR | **COVERED-uncited** | `FR-426`→`P1-09` | cited by the FRD row, not by the task |
| `G-045` | BLOCKER | **COVERED-uncited** | `FR-330`→`P0-11` · `FR-332`→`P0-11` | cited by the FRD row, not by the task |
| `G-046` | BLOCKER | **CITED** | `P3-22` `P6-08` | — |
| `G-047` | MAJOR | **CITED** | `P0-01` `P0-11` `P0-14` `P1-20` `P2-29` | — |
| `G-048` | MINOR | **CITED** | `P6-08` | — |
| `G-049` | MAJOR | **COVERED-uncited** | `FR-353`→`P0-14` | cited by the FRD row, not by the task |
| `G-050` | MAJOR | **CITED** | `P1-05` `P1-11` `P6-09` | — |
| `G-051` | MAJOR | **CITED** | `P2-27` | — |
| `G-052` | MINOR | **COVERED-uncited** | `FR-367`→`P0-04` | cited by the FRD row, not by the task |
| `G-053` | BLOCKER | **COVERED-uncited** | `FR-108`→`P0-06` · `FR-375`→`P0-04` · `FR-376`→`P0-04` · `FR-377`→`P0-01` | cited by the FRD row, not by the task |
| `G-054` | MAJOR | **COVERED-uncited** | `FR-003`→`P0-04` | cited by the FRD row, not by the task |
| `G-055` | MAJOR | **COVERED-uncited** | `FR-083`→`P1-05` | cited by the FRD row, not by the task |
| `G-056` | MAJOR | **COVERED-uncited** | `FR-102`→`P0-05` | cited by the FRD row, not by the task |
| `G-057` | MAJOR | **COVERED-uncited** | `FR-117`→`P1-08` | cited by the FRD row, not by the task |
| `G-058` | MINOR | **COVERED-uncited** | `FR-019`→`P0-04` | cited by the FRD row, not by the task |
| `G-059` | MINOR | **COVERED-uncited** | `FR-056`→`P1-02` | cited by the FRD row, not by the task |
| `G-060` | MAJOR | **COVERED-uncited** | `FR-049`→`P1-01` | cited by the FRD row, not by the task |
| `G-061` | MINOR | **COVERED-uncited** | — | `whb_task_types` is `DATA-MODEL.md` §catalogue row 8, v1, `PNR-1` (`P0-10`) |
| `G-062` | MINOR | **CITED** | `P2-12` | — |
| `G-063` | MINOR | **COVERED-uncited** | `FR-026`→`P0-02` · `FR-076`→`P1-01` | cited by the FRD row, not by the task |
| `G-064` | MAJOR | **CITED** | `P0-04` | — |
| `G-065` | MINOR | **COVERED-uncited** | `FR-381`→`P1-19` | cited by the FRD row, not by the task |
| `G-066` | MINOR | **CITED** | `P3-04` | — |
| `G-067` | BLOCKER | **COVERED-uncited** | — | `IRREVERSIBLE.md` is that consolidation — its §2 header names "R2 §3, R4 §3.7 + §5.4, R5's cannot-be-added-later table, R7 §6", and 50 task files cite its `I-nn` rows |
| `G-068` | MAJOR | **COVERED-uncited** | `FR-346`→`P0-15` · `FR-407`→`P0-15` | cited by the FRD row, not by the task |
| `G-069` | MAJOR | **COVERED-uncited** | `FR-346`→`P0-15` | cited by the FRD row, not by the task |
| `G-070` | MINOR | **DECIDED** | — | `D-2` — the bands are V500000–V549999; R4's V930000 is superseded |
| `G-071` | MAJOR | **CITED** | `P2-02` | — |
| `G-072` | MINOR | **COVERED-uncited** | `FR-024`→`P0-02` · `FR-034`→`P0-08` | cited by the FRD row, not by the task |
| `G-073` | MINOR | **COVERED-uncited** | `FR-037`→`P0-08` | cited by the FRD row, not by the task |
| `G-074` | MINOR | **COVERED-uncited** | `FR-085`→`P1-05` | cited by the FRD row, not by the task |
| `G-075` | MINOR | **CITED** | `P2-02` | — |
| `G-076` | MINOR | **COVERED-uncited** | `FR-025`→`P0-02` | cited by the FRD row, not by the task |
| `G-077` | MINOR | **CITED** | `P2IN-02` | — |
| `G-078` | MINOR | **COVERED-uncited** | — | `P2-IN-01`/`P2-IN-04` — `DATA-MODEL.md` §7.6 carries the provider stack at `V540011`–`V540012` |
| `G-079` | BLOCKER | **CITED** | `P1-17` | — |
| `G-080` | MINOR | **DECIDED** | — | Resolved in place: thin PO in `warehouse` v1.1 (`G-032`, cited by `P2-07`/`P3-05`/`P6-05`), relocating to SC in v3 |
| `G-081` | MINOR | **DECIDED** | — | `D-2` supersedes R3 `E-005`'s ranges |
| `G-082` | MINOR | **COVERED-uncited** | — | `DATA-MODEL.md`:862 settles one name — `whb_inbound_messages` |
| `G-083` | MINOR | **COVERED-uncited** | — | `MODULE-INTEGRATION.md` §13.2 `WarehouseBaseCouplingTest` is the single test; `P0-01` owns it |
| `G-084` | MAJOR | **CITED** | `P6-08` | — |
| `G-085` | MINOR | **CITED** | `P6-08` | — |
| `G-086` | MINOR | **WONTFIX** | — | A meta-row recording R7's own UNVERIFIED list. No build consequence |
| `P-001` | BLOCKER | **CITED** | `P0-01` | — |
| `P-002` | BLOCKER | **CITED** | `P0-01` | — |
| `P-003` | BLOCKER | **COVERED-uncited** | — | `p0-04.md` Traps names it, and `OD-4` carries the rule ("never an FK from base into another module") |
| `P-004` | MAJOR | **COVERED-uncited** | — | `p0-01.md` Traps names it (`global_settings.chk_global_setting_module` credit to a non-existent migration) |
| `P-005` | MAJOR | **WONTFIX** | — | A premise correction — the built `warehouse-base` does not exist in this checkout. Its build consequence is carried by `P-001`/`P-003`/`P-004`, all cited |
| `P-006` | MAJOR | **CITED** | `P1-20` | — |
| `P-007` | MAJOR | **CITED** | `P0-02` `P0-05` `P1-06` `P1-14` | — |
| `P-008` | BLOCKER | **CITED** | `P0-02` | — |
| `P-009` | BLOCKER | **CITED** | `P0-02` | — |
| `P-010` | MINOR | **CITED** | `P0-07` `P1-08` | — |
| `P-011` | MINOR | **CITED** | `P0-14` `P1-05` | — |
| `P-012` | MINOR | **COVERED-uncited** | — | `C-018` (cited by `P1-04`) prescribes `wh_document_links` following `acc_document_links` |
| `P-013` | MINOR | **CITED** | `P1-19` | — |
| `P-014` | MAJOR | **CITED** | `P0-04` `P0-15` `P1-18` `P2-20` | — |
| `P-015` | MINOR | **WONTFIX** | — | The lens itself says "drop the finding" — `useAuthGuard` delegates to `usePageAccess` |
| `P-016` | MINOR | **CITED** | `P0-01` | — |
| `P-017` | MINOR | **CITED** | `P1-04` | — |
| `P-018` | MAJOR | **CITED** | `P1-12` | — |
| `P-019` | MAJOR | **CITED** | `P1-12` `P1-13` `P3-05` | — |
| `P-020` | MAJOR | **CITED** | `P1-12` `P3-05` | — |
| `P-021` | MAJOR | **CITED** | `P1-13` | — |
| `P-022` | MAJOR | **CITED** | `P0-03` | — |
| `P-023` | MAJOR | **CITED** | `P0-13` | — |
| `P-024` | MAJOR | **CITED** | `P0-02` `P0-03` | — |
| `P-025` | MAJOR | **CITED** | `P0-02` `P0-06` | — |
| `P-026` | MAJOR | **CITED** | `P1-12` | — |
| `P-027` | MAJOR | **CITED** | `P0-02` `P0-08` `P1-16` | — |
| `P-028` | MAJOR | **CITED** | `P2-12` `P2-13` | — |
| `P-029` | MAJOR | **CITED** | `P1-13` `P1-14` | — |
| `P-030` | MINOR | **CITED** | `P1-01` `P1-03` | — |
| `P-031` | MAJOR | **CITED** | `P1-01` `P1-03` | — |
| `P-032` | MINOR | **CITED** | `P5-15` | — |
| `P-033` | MAJOR | **CITED** | `P2-04` | — |
| `P-034` | MAJOR | **CITED** | `P1-02` `P1-07` | — |
| `P-035` | MAJOR | **CITED** | `P1-02` | — |
| `P-036` | MAJOR | **CITED** | `P1-02` | — |
| `P-037` | MAJOR | **CITED** | `P2-11` `P3-07` | — |
| `P-038` | MAJOR | **CITED** | `P1-17` `P2-09` `P2-10` `P2IN-04` `P3-05` `P3-09` | — |
| `P-039` | MAJOR | **CITED** | `P5-10` | — |
| `P-040` | MINOR | **COVERED-uncited** | — | `DATA-MODEL.md`:3885 re-homes `wms_invoice_orders` to `wh_three_way_match_allocations` (`FR-140`, `P5-10`) |
| `P-041` | MAJOR | **CITED** | `P1-10` | — |
| `P-042` | BLOCKER | **CITED** | `P1-08` | — |
| `P-043` | MAJOR | **CITED** | `P4-01` | — |
| `P-044` | MAJOR | **CITED** | `P2IN-02` `P2IN-04` `P4-12` | — |
| `P-045` | MINOR | **CITED** | `P1-03` | — |
| `P-046` | MINOR | **CITED** | `P1-09` | — |
| `P-047` | MINOR | **COVERED-uncited** | — | `DATA-MODEL.md`:1068 and :3876 carry the split verbatim and cite `P-047`; `FR-267` is `P5-19`'s |
| `P-048` | MINOR | **WONTFIX** | — | The lens says "do not carry any of its rows" — `ERP_FEATURE_GAPS.md` is superseded in full |
| `P-049` | MINOR | **CITED** | `P1-13` `P1-15` | — |
| `P-050` | MAJOR | **CITED** | `P0-17` | — |
| `P-051` | MAJOR | **CITED** | `P1-03` `P2-05` | — |
| `P-052` | MAJOR | **WONTFIX** | — | FRD §10 row 9 refuses service-parts planning. Re-entry: `FR-070`'s four nullable seam columns (`P1-03`) then a planning module |
| `P-053` | MINOR | **NEEDS-TASK** | — | The onboarding narrative has no owner. `P3-23` ships in-product help per screen (`S-094`/`FR-442`), which is not the same artefact |
| `P-054` | MAJOR | **CITED** | `P0-16` `P3-01` | — |
| `P-055` | MAJOR | **COVERED-uncited** | `FR-354`→`P0-14` · `FR-433`→`P1-20` · `FR-434`→`P0-01` | cited by the FRD row, not by the task |
| `P-056` | MINOR | **WONTFIX** | — | A method to copy (self-revising findings), not a capability. No task needed |
| `P-057` | MINOR | **CITED** | `P1-13` | — |
| `P-058` | MINOR | **CITED** | `P0-10` `P2-21` `P6-10` | — |
| `P-059` | MINOR | **COVERED-uncited** | `FR-373`→`P0-01` | cited by the FRD row, not by the task |
| `P-060` | MINOR | **DECIDED** | — | `DATA-MODEL.md`:3895 records the ten `scc_vehicle_*`/`scc_driver_*` tables as out of scope, citing `P-060` |
| `S-001` | BLOCKER | **COVERED-uncited** | `FR-057`→`P1-02` | cited by the FRD row, not by the task |
| `S-002` | BLOCKER | **CITED** | `P3-15` | — |
| `S-003` | MAJOR | **COVERED-uncited** | `FR-057`→`P1-02` | cited by the FRD row, not by the task |
| `S-004` | BLOCKER | **COVERED-uncited** | `FR-064`→`P1-02` · `FR-100`→`P1-07` | cited by the FRD row, not by the task |
| `S-005` | MAJOR | **NEEDS-TASK** | — | `grep -in "gs1\|GS1" DATA-MODEL.md` → 0. No `gs1_settings` table and no SSCC allocator anywhere; `FR-100` carries only the `sscc` column |
| `S-006` | MAJOR | **COVERED-uncited** | `FR-064`→`P1-02` | cited by the FRD row, not by the task |
| `S-007` | BLOCKER | **COVERED-uncited** | `FR-007`→`P0-02` · `FR-439`→`P0-02` | cited by the FRD row, not by the task |
| `S-008` | MAJOR | **CITED** | `P5-19` | — |
| `S-009` | MAJOR | **COVERED-uncited** | — | The four EPCIS dimensions are v1 columns (`DATA-MODEL.md`:683, `IRR-20`); FRD §10 row 20 refuses the repository. The v3 emit adapter itself has no task |
| `S-010` | MAJOR | **NEEDS-TASK** | — | `grep -in "RFID\|EPC Gen2" FRD` → 0. No `epc` column and no reader-event endpoint anywhere |
| `S-011` | MAJOR | **COVERED-uncited** | `FR-056`→`P1-02` · `FR-319`→`P1-03` | cited by the FRD row, not by the task |
| `S-012` | BLOCKER | **COVERED-uncited** | `FR-009`→`P0-02` | cited by the FRD row, not by the task |
| `S-013` | BLOCKER | **COVERED-uncited** | `FR-065`→`P1-03` | cited by the FRD row, not by the task |
| `S-014` | MAJOR | **COVERED-uncited** | — | `FR-065` (`P1-03`) creates `secondary_quantity`, S-014's destination. Residual: the GTIN indicator-9 parse itself is v2 and unowned |
| `S-015` | MAJOR | **CITED** | `P3-05` | — |
| `S-016` | MAJOR | **COVERED-uncited** | `FR-080`→`P1-05` | cited by the FRD row, not by the task |
| `S-017` | MINOR | **NEEDS-TASK** | — | `grep -in "Digital Link\|barcode_format" FRD` → 0. R5 places the **enum value** in v1 — an enum widened later is a migration, not a column |
| `S-018` | MAJOR | **COVERED-uncited** | `FR-097`→`P1-07` | cited by the FRD row, not by the task |
| `S-019` | MAJOR | **COVERED-uncited** | — | `FR-224` (`P2-14`) — the template carries format and dimensions; the printer registry with DPI is v1.1 |
| `S-020` | MINOR | **COVERED-uncited** | — | `whb_item_types` seeds `RETURNABLE_EQUIPMENT` (`WHB-08`, `V500008`) and `FR-343` (`P5-21`) carries the per-counterparty balance |
| `S-021` | BLOCKER | **CITED** | `P1-11` `P1-17` `P2IN-01` | — |
| `S-022` | BLOCKER | **COVERED-uncited** | `FR-025`→`P0-02` · `FR-079`→`P1-05` · `FR-080`→`P1-05` · `FR-305`→`P1-17` | cited by the FRD row, not by the task |
| `S-023` | BLOCKER | **CITED** | `P2IN-03` | — |
| `S-024` | BLOCKER | **CITED** | `P2IN-04` | — |
| `S-025` | MAJOR | **CITED** | `P4-01` | — |
| `S-026` | BLOCKER | **CITED** | `P2IN-03` `P4-02` | — |
| `S-027` | BLOCKER | **CITED** | `P4-03` | — |
| `S-028` | BLOCKER | **COVERED-uncited** | `FR-019`→`P0-04` · `FR-315`→`P0-04` | cited by the FRD row, not by the task |
| `S-029` | MAJOR | **CITED** | `P4-04` | — |
| `S-030` | MAJOR | **CITED** | `P1-09` `P4-04` | — |
| `S-031` | MAJOR | **COVERED-uncited** | `FR-066`→`P1-03` · `FR-318`→`P0-02` | cited by the FRD row, not by the task |
| `S-032` | MAJOR | **CITED** | `P4-06` | — |
| `S-033` | MAJOR | **COVERED-uncited** | `FR-095`→`P1-07` · `FR-320`→`P1-03` | cited by the FRD row, not by the task |
| `S-034` | MINOR | **CITED** | `P5-17` | — |
| `S-035` | BLOCKER | **NEEDS-TASK** | — | **Segment BLOCKER.** The core half is `FR-098`/`IRR-56`. The `whin_` half — `whin_entity_licences`, `whin_counterparty_licences`, `whin_licence_types`, `whin_schedule_h1_register`, `whin_recall_notifications` — has no FR, no `DATA-MODEL.md` row and no task (`D-P4-3`, `D-P4-4`) |
| `S-036` | MAJOR | **WONTFIX** | — | FRD §10 row 14 declines pharma-serialisation compliance regimes; we implement the shape only (`FR-100`, `FR-105`). Re-entry: an adapter once `S-004`/`S-007`/`S-008` land |
| `S-037` | MAJOR | **CITED** | `P2-13` | — |
| `S-038` | MAJOR | **COVERED-uncited** | `FR-095`→`P1-07` | cited by the FRD row, not by the task |
| `S-039` | BLOCKER | **CITED** | `P2-05` | — |
| `S-040` | MAJOR | **CITED** | `P2-21` `P5-14` | — |
| `S-041` | BLOCKER | **COVERED-uncited** | `FR-068`→`P1-03` | cited by the FRD row, not by the task |
| `S-042` | MAJOR | **COVERED-uncited** | `FR-067`→`P1-03` | cited by the FRD row, not by the task |
| `S-043` | MINOR | **WONTFIX** | — | `INDIA-LOCALISATION-PACK.md`:1048 carries it as v3, adapter-chem. Re-entry: an adapter over data we already hold |
| `S-044` | BLOCKER | **CITED** | `P4-07` | — |
| `S-045` | MAJOR | **CITED** | `P1-07` `P4-07` | — |
| `S-046` | MINOR | **WONTFIX** | — | `INDIA-LOCALISATION-PACK.md`:1316 — "eNWR specifically is `S-046`, v3, and only if agri 3PL becomes a target" |
| `S-047` | MAJOR | **CITED** | `P5-15` | — |
| `S-048` | MAJOR | **CITED** | `P2-26` | — |
| `S-049` | MINOR | **NEEDS-TASK** | — | `grep -rin counterfeit docs/ issues/` outside `reviews/` → 0. R5 §6 lists it as an automotive-distribution addition at v2 |
| `S-050` | MAJOR | **CITED** | `P4-08` | — |
| `S-051` | BLOCKER | **CITED** | `P4-09` `P6-01` | — |
| `S-052` | MAJOR | **NEEDS-TASK** | — | `grep -in "cost object\|cost centre" FRD` → 0. R5 rates it MAJOR: issues must carry a cost object or consumption is not reportable by it |
| `S-053` | BLOCKER | **CITED** | `P2-16` `P4-11` | — |
| `S-054` | MAJOR | **COVERED-uncited** | `FR-004`→`P0-02` · `FR-005`→`P0-02` | cited by the FRD row, not by the task |
| `S-055` | MINOR | **CITED** | `P4-09` | — |
| `S-056` | BLOCKER | **CITED** | `P1-01` `P1-03` `P5-20` | — |
| `S-057` | MAJOR | **CITED** | `P2-05` | — |
| `S-058` | MAJOR | **CITED** | `P5-17` | — |
| `S-059` | MAJOR | **COVERED-uncited** | — | `P5-09` (channel accounts, order import, publish rules) + `P5-13` (returns grading) + `S-069` (`P2-02`) |
| `S-060` | MAJOR | **CITED** | `P3-20` | — |
| `S-061` | MAJOR | **CITED** | `P2-26` | — |
| `S-062` | BLOCKER | **DECIDED** | — | `D-9` — accessories inventory stays permanently separate, with the cost named in `COEXISTENCE.md` |
| `S-063` | MAJOR | **CITED** | `P2-15` `P2-25` | — |
| `S-064` | BLOCKER | **COVERED-uncited** | `FR-107`→`P0-02` · `FR-230`→`P0-12` | cited by the FRD row, not by the task |
| `S-065` | BLOCKER | **CITED** | `P2-16` `P2-18` | — |
| `S-066` | BLOCKER | **CITED** | `P0-12` `P2-16` `P2-18` | — |
| `S-067` | BLOCKER | **CITED** | `P0-12` `P2-18` | — |
| `S-068` | MAJOR | **CITED** | `P0-12` | — |
| `S-069` | BLOCKER | **CITED** | `P2-02` | — |
| `S-070` | MAJOR | **CITED** | `P2-16` | — |
| `S-071` | MAJOR | **CITED** | `P2-17` | — |
| `S-072` | MAJOR | **CITED** | `P5-16` | — |
| `S-073` | MAJOR | **CITED** | `P2-18` | — |
| `S-074` | MAJOR | **CITED** | `P2-18` | — |
| `S-075` | MAJOR | **CITED** | `P5-16` | — |
| `S-076` | MAJOR | **COVERED-uncited** | `FR-014`→`P0-03` | cited by the FRD row, not by the task |
| `S-077` | MAJOR | **COVERED-uncited** | — | `FR-020` (`P0-07`) — a movement in a `CLOSED` period is refused, `SOFT_CLOSED` needs an override permission (`L-8`) |
| `S-078` | BLOCKER | **CITED** | `P0-06` `P0-12` `P5-08` | — |
| `S-079` | BLOCKER | **CITED** | `P2-19` | — |
| `S-080` | BLOCKER | **CITED** | `P3-18` | — |
| `S-081` | MAJOR | **CITED** | `P2-19` | — |
| `S-082` | BLOCKER | **COVERED-uncited** | `FR-429`→`P0-16` | cited by the FRD row, not by the task |
| `S-083` | MAJOR | **CITED** | `P2-20` `P2-21` | — |
| `S-084` | MAJOR | **CITED** | `P2-29` `P3-01` | — |
| `S-085` | BLOCKER | **COVERED-uncited** | `FR-016`→`P0-03` · `FR-175`→`P0-03` | cited by the FRD row, not by the task |
| `S-086` | BLOCKER | **COVERED-uncited** | `FR-047`→`P0-08` · `FR-221`→`P0-16` | cited by the FRD row, not by the task |
| `S-087` | BLOCKER | **CITED** | `P2-14` `P3-08` | — |
| `S-088` | MAJOR | **CITED** | `P3-01` `P3-03` | — |
| `S-089` | BLOCKER | **CITED** | `P2-01` | — |
| `S-090` | MAJOR | **CITED** | `P0-16` | — |
| `S-091` | MAJOR | **CITED** | `P2-04` `P2-21` | — |
| `S-092` | BLOCKER | **COVERED-uncited** | `FR-409`→`P0-13` | cited by the FRD row, not by the task |
| `S-093` | MAJOR | **CITED** | `P3-16` | — |
| `S-094` | MAJOR | **CITED** | `P3-23` | — |
| `S-095` | MAJOR | **COVERED-uncited** | `FR-431`→`P1-19` | cited by the FRD row, not by the task |
| `S-096` | MAJOR | **CITED** | `P6-01` | — |
| `S-097` | MINOR | **NEEDS-TASK** | — | `grep -in "webhook\|API key\|rate limit" FRD` → 0. `OD-8` covers only how a consumer authenticates, not the integration surface |
| `S-098` | BLOCKER | **CITED** | `P3-04` | — |
| `T-001` | BLOCKER | **CITED** | `P0-02` | — |
| `T-002` | BLOCKER | **CITED** | `P0-02` `P0-06` | — |
| `T-003` | BLOCKER | **CITED** | `P0-02` `P0-05` `P1-07` `P2-20` | — |
| `T-004` | BLOCKER | **CITED** | `P0-09` `P2-03` | — |
| `T-005` | BLOCKER | **CITED** | `P0-04` `P2-05` | — |
| `T-006` | BLOCKER | **COVERED-uncited** | `FR-097`→`P1-07` · `FR-098`→`P1-07` · `FR-106`→`P1-07` · `FR-144`→`P1-13` | cited by the FRD row, not by the task |
| `T-007` | BLOCKER | **CITED** | `P3-15` | — |
| `T-008` | BLOCKER | **CITED** | `P2-02` | — |
| `T-009` | BLOCKER | **COVERED-uncited** | `FR-002`→`P0-02` · `FR-084`→`P1-05` | cited by the FRD row, not by the task |
| `T-010` | BLOCKER | **CITED** | `P2-01` | — |
| `T-011` | BLOCKER | **CITED** | `P3-11` | — |
| `T-012` | BLOCKER | **COVERED-uncited** | `FR-065`→`P1-03` | cited by the FRD row, not by the task |
| `T-013` | BLOCKER | **COVERED-uncited** | `FR-026`→`P0-02` · `FR-041`→`P0-08` · `FR-076`→`P1-01` · `FR-078`→`P1-02` | cited by the FRD row, not by the task |
| `T-014` | BLOCKER | **CITED** | `P2-07` | — |
| `T-015` | BLOCKER | **CITED** | `P2-02` `P3-11` | — |
| `T-016` | BLOCKER | **CITED** | `P2-02` | — |
| `T-017` | BLOCKER | **CITED** | `P0-03` `P0-13` | — |
| `T-018` | BLOCKER | **CITED** | `P0-08` | — |
| `T-019` | BLOCKER | **CITED** | `P0-03` `P2-06` `P2-20` | — |
| `T-020` | MAJOR | **CITED** | `P1-06` `P1-16` | — |
| `T-020a` | MINOR | **CITED** | `P6-01` | — |
| `T-021` | MAJOR | **CITED** | `P2-07` `P2-24` `P2-25` | — |
| `T-022` | MAJOR | **COVERED-uncited** | `FR-057`→`P1-02` | cited by the FRD row, not by the task |
| `T-023` | MAJOR | **CITED** | `P2-24` | — |
| `T-024` | MAJOR | **COVERED-uncited** | `FR-089`→`P1-06` | cited by the FRD row, not by the task |
| `T-025` | MAJOR | **COVERED-uncited** | `FR-014`→`P0-03` | cited by the FRD row, not by the task |
| `T-026` | MINOR | **COVERED-uncited** | `FR-052`→`P1-01` | cited by the FRD row, not by the task |
| `T-027` | MINOR | **CITED** | `P3-12` | — |
| `T-028` | MINOR | **COVERED-uncited** | `FR-069`→`P1-03` | cited by the FRD row, not by the task |
| `T-029` | MINOR | **COVERED-uncited** | `FR-051`→`P1-01` | cited by the FRD row, not by the task |
| `T-030` | MAJOR | **CITED** | `P0-10` `P2-05` | — |
| `T-031` | MINOR | **CITED** | `P3-10` `P3-11` | — |
| `T-032` | MINOR | **CITED** | `P3-15` | — |
| `T-033` | MAJOR | **COVERED-uncited** | `FR-032`→`P0-08` · `FR-038`→`P1-13` | cited by the FRD row, not by the task |
| `T-034` | MAJOR | **COVERED-uncited** | `FR-128`→`P1-13` | cited by the FRD row, not by the task |
| `T-035` | MAJOR | **CITED** | `P1-15` | — |
| `T-036` | MAJOR | **CITED** | `P6-05` | — |
| `T-037` | MAJOR | **COVERED-uncited** | `FR-135`→`P1-15` | cited by the FRD row, not by the task |
| `T-038` | MINOR | **CITED** | `P2-13` | — |
| `T-039` | MINOR | **CITED** | `P5-09` | — |
| `T-040` | MINOR | **COVERED-uncited** | `FR-116`→`P1-08` · `FR-117`→`P1-08` · `FR-120`→`P1-13` | cited by the FRD row, not by the task |
| `T-041` | BLOCKER | **CITED** | `P3-02` `P3-06` `P3-12` `P3-14` `P5-18` | — |
| `T-042` | MAJOR | **CITED** | `P2-08` | — |
| `T-043` | BLOCKER | **CITED** | `P2-07` | — |
| `T-044` | MAJOR | **CITED** | `P2-07` `P2-09` | — |
| `T-045` | MAJOR | **CITED** | `P2-09` `P3-02` `P5-18` | — |
| `T-046` | MAJOR | **CITED** | `P2-09` | — |
| `T-047` | MINOR | **CITED** | `P3-13` | — |
| `T-048` | MINOR | **CITED** | `P2-07` | — |
| `T-049` | MINOR | **CITED** | `P2-07` | — |
| `T-050` | MINOR | **CITED** | `P0-11` `P3-07` | — |
| `T-051` | BLOCKER | **CITED** | `P3-01` | — |
| `T-052` | MAJOR | **CITED** | `P3-01` | — |
| `T-053` | MAJOR | **COVERED-uncited** | `FR-047`→`P0-08` · `FR-221`→`P0-16` | cited by the FRD row, not by the task |
| `T-054` | MAJOR | **CITED** | `P2-14` `P3-08` | — |
| `T-055` | MINOR | **CITED** | `P3-02` | — |
| `T-056` | MINOR | **COVERED-uncited** | `FR-215`→`P0-10` | cited by the FRD row, not by the task |
| `T-057` | MINOR | **CITED** | `P3-02` | — |
| `T-058` | MINOR | **CITED** | `P6-03` | — |
| `T-059` | MINOR | **CITED** | `P3-22` `P6-04` | — |
| `T-060` | BLOCKER | **CITED** | `P0-07` | — |
| `T-061` | BLOCKER | **CITED** | `P2-16` | — |
| `T-062` | BLOCKER | **CITED** | `P2-16` | — |
| `T-063` | MAJOR | **CITED** | `P2-17` | — |
| `T-064` | MAJOR | **COVERED-uncited** | `FR-020`→`P0-07` · `FR-251`→`P0-07` | cited by the FRD row, not by the task |
| `T-065` | MAJOR | **CITED** | `P2-18` | — |
| `T-066` | MAJOR | **CITED** | `P2-18` | — |
| `T-067` | MAJOR | **CITED** | `P2-18` | — |
| `T-068` | MINOR | **CITED** | `P2-16` | — |
| `T-069` | MINOR | **CITED** | `P2-18` `P2-19` | — |
| `T-070` | MINOR | **CITED** | `P0-15` `P1-18` `P1-20` `P2-16` | — |
| `T-071` | MAJOR | **CITED** | `P5-03` | — |
| `T-072` | MAJOR | **CITED** | `P2-28` | — |
| `T-073` | MAJOR | **CITED** | `P5-08` | — |
| `T-074` | MINOR | **COVERED-uncited** | `FR-086`→`P1-05` | cited by the FRD row, not by the task |
| `T-075` | MINOR | **CITED** | `P5-02` | — |
| `T-076` | MINOR | **CITED** | `P5-08` | — |
| `T-077` | MINOR | **COVERED-uncited** | `FR-111`→`P0-06` · `FR-113`→`P0-06` | cited by the FRD row, not by the task |
| `T-078` | MINOR | **CITED** | `P5-05` | — |
| `T-079` | BLOCKER | **CITED** | `P2-25` | — |
| `T-080` | MAJOR | **CITED** | `P3-20` | — |
| `T-081` | MAJOR | **CITED** | `P2-26` | — |
| `T-082` | MAJOR | **CITED** | `P5-15` | — |
| `T-083` | MAJOR | **CITED** | `P2IN-03` | — |
| `T-084` | MINOR | **CITED** | `P2-15` | — |
| `T-085` | MINOR | **CITED** | `P2-07` | — |
| `T-086` | MINOR | **CITED** | `P6-11` | — |
| `T-087` | MINOR | **CITED** | `P3-21` | — |
| `T-088` | MINOR | **COVERED-uncited** | — | FRD §10 row 8 — "Relocated, not refused"; `FR-258` (`P6-02`) is the boundary |
| `T-089` | BLOCKER | **CITED** | `P2-04` `P3-14` | — |
| `T-090` | MAJOR | **CITED** | `P2-01` `P2-04` `P2-23` | — |
| `T-091` | BLOCKER | **COVERED-uncited** | `FR-017`→`P0-08` · `FR-033`→`P0-08` · `FR-044`→`P0-08` | cited by the FRD row, not by the task |
| `T-092` | MAJOR | **CITED** | `P2-22` `P3-02` | — |
| `T-093` | MAJOR | **COVERED-uncited** | — | FRD §10 row 11 refuses the engine and names the four bounded rule tables, each owned by a task |
| `T-094` | MINOR | **COVERED-uncited** | `FR-078`→`P1-02` | cited by the FRD row, not by the task |
| `T-095` | MAJOR | **COVERED-uncited** | `FR-022`→`P0-02` · `FR-423`→`P0-02` | cited by the FRD row, not by the task |
| `T-096` | MINOR | **COVERED-uncited** | `FR-373`→`P0-01` | cited by the FRD row, not by the task |
| `T-097` | MINOR | **COVERED-uncited** | `FR-432`→`P1-20` | cited by the FRD row, not by the task |

---

## §3 · The traceability proof

Six claims, each with its one-line command and its **actual output**, run 2026-09-02 from the
repository root. Four hold. Two do not, and the failures are named.

### 3.1 Every finding id cited in a task file resolves to a real finding — **HOLDS**

```bash
for f in issues/p[0-9]*-*.md; do
  awk '/^## Closes/{c=1;next} /^## /{c=0} c' "$f" | grep -oE '\b[CTEFSPG]-[0-9]{3}\b'
done | sort -u > cited.txt
comm -23 cited.txt universe.txt        # cited but not a real finding
```

```
(empty)
```

**377 three-digit ids plus `T-020a` = 378 distinct findings cited across 138 `## Closes` blocks, and
every one resolves.** `tools/check-design-set.py` check-7 agrees for `issues/` — its eight failures
are all in `docs/`, not in a task file (§3.7).

### 3.2 Every finding in the universe has a disposition row — **HOLDS**

```bash
wc -l < DISPOSITION.tsv                                    # → 575
comm -3 <(cut -f1 DISPOSITION.tsv | sort) universe575.txt  # → (empty)
```

575 rows, one per finding, one bucket each. §2.5 is the table.

### 3.3 Every `FR-nnn` is owned by exactly one task — **HOLDS in `issues/`, FAILS in the plan**

```bash
for f in issues/p[0-9]*-*.md; do b=$(basename $f .md); \
  blk=$(awk '/^## Requirements closed/{c=1;next} c&&/^[[:space:]]*$/&&seen{exit} c&&/^## /{exit} c&&NF{seen=1;print}' "$f"); \
  case "$blk" in '**None'*) continue;; esac; \
  printf '%s' "$blk" | grep -oE 'FR-[0-9]{3}' | sed "s/^/$b\t/"; done | sort -u > FR_OWNER.txt
cut -f2 FR_OWNER.txt | sort -u | wc -l        # distinct FRs owned
cut -f2 FR_OWNER.txt | sort | uniq -d         # double-owned
comm -23 <(grep -oE '^\| \*\*FR-[0-9]{3}' docs/WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md \
           | grep -oE 'FR-[0-9]{3}' | sort -u) <(cut -f2 FR_OWNER.txt | sort -u)   # unowned
```

```
446
(no double-owned)
(no unowned)
tasks owning zero FR: p0-17 p4-12
```

**446 requirements, 446 owned exactly once.** The two zero-FR tasks are deliberate and say so in
their own files (`p0-17.md`: *"None. Deliberate"*; `p4-12.md`: *"this task closes no requirement of
its own"*), and `IMPLEMENTATION-PLAN.md` §8.3 declares both.

> **Two cautions for anyone re-running this.** The naive extraction — every `FR-nnn` inside the
> `## Requirements closed` section — reports **seven** double-owned requirements (`FR-137` `FR-141`
> `FR-234` `FR-235` `FR-236` `FR-245` `FR-312`). All seven are false positives: they are prose lines
> that **disclaim** ownership, e.g. `p0-17.md`'s *"The FRs for this schema's behaviour are `P2-16`'s"*
> and `p1-17.md`'s *"`FR-312`'s wave-1 clock columns also ride on this table, and `P4-02` owns
> ITC-04"*. The command above takes only the first contiguous block and skips a block opening
> `**None`. **A checker that does not do this will report a clean set as broken.**

**The failure is on the plan's side.** `tools/check-design-set.py` check-10:

```
check-10 FAIL    3  every FR-nnn is owned by exactly one task
  docs/IMPLEMENTATION-PLAN.md:374: FR-224 is defined in the FRD but no §2 task row closes it
  docs/IMPLEMENTATION-PLAN.md:374: FR-225 is defined in the FRD but no §2 task row closes it
  issues/p2-14.md:73: P2-14 claims FR-224 FR-225, which §2's `Closes` column does not assign to it
```

`IMPLEMENTATION-PLAN.md` §8.1 asserts *"every requirement is owned by exactly one task"* and §8.5
records **446 owned exactly once**. In §2 it is **444**. `P2-14` (printing) picked the two up, which
is right — `FR-224` is `A-2`'s printing requirement and `FR-225` its sibling — but §2 was never
amended. Filed as `X-039`.

### 3.4 Every `WH-SC-nnn` cited resolves; none is phantom — **HOLDS**

```bash
grep -oE '^\| \*\*WH-SC-[0-9]{3}\*\*' docs/SCENARIO-CATALOGUE.md \
  | grep -oE 'WH-SC-[0-9]{3}' | sort -u > sc_defined.txt          # → 300
grep -rohE 'WH-SC-[0-9]{3}' issues/*.md | sort -u > sc_cited.txt  # → 300
comm -13 sc_defined.txt sc_cited.txt      # cited by a task, not defined
comm -23 sc_defined.txt sc_cited.txt      # defined, cited by no task
```

```
cited-not-defined : WH-SC-301
defined-not-cited : WH-SC-204
```

**Neither is a dangling reference.**

- **`WH-SC-301` is the allocation marker, not a scenario.** `SCENARIO-CATALOGUE.md:685` §5 rule 3
  reserves it as *"new scenarios start from"*, and the 29 citations of it in `issues/` are all
  instructions to claim the next free id. `tools/check-design-set.py` check-2 reports all 29 as
  failures; **the checker is wrong here, not the design set** — filed as `X-040`.
- **`WH-SC-204`** (*"the same LPN label, printed once at 203 dpi and once at 300 dpi"*) is a real
  scenario that no task claims. It belongs to `P2-14` (printing) or `P3-08` (the print server);
  one line in one `## Scenarios closed` block closes it. Filed as `X-041`.

### 3.5 Every migration number is owned by exactly one task and sits in its module's band — **HOLDS for numbers, FAILS for three module cells**

```bash
python3 - <<'PY'
import glob,os,re
rows=[]
for f in sorted(glob.glob('issues/p[0-9]*-*.md')):
    b=os.path.basename(f)[:-3].upper()
    hdr=open(f).read().split('\n')[3]
    m=re.search(r'Migrations (.*?)(?: · \*?\*?Screens|$)',hdr)
    if not m: continue
    cell=m.group(1)
    for a,z in re.findall(r'V(\d{6})\s*[–-]\s*V(\d{6})',cell):
        rows += [(b,'V%06d'%n) for n in range(int(a),int(z)+1)]
    rows += [(b,'V'+a) for a in re.findall(r'V(\d{6})',re.sub(r'V\d{6}\s*[–-]\s*V\d{6}','',cell))]
import collections
own=collections.defaultdict(set)
for b,v in rows: own[v].add(b)
print('numbers claimed      :', len(own))
print('claimed by two tasks :', {v:sorted(t) for v,t in own.items() if len(t)>1} or 'none')
print('outside V500000-549999:', [v for v in own if not 500000<=int(v[1:])<=549999] or 'none')
bands={'base':(500000,509999),'app':(510000,519999),'adapter':(520000,529999),
       '3pl':(530000,539999),'india':(540000,549999)}
c=collections.Counter(k for v in own for k,(lo,hi) in bands.items() if lo<=int(v[1:])<=hi)
print(dict(c))
PY
```

```
numbers claimed      : 915
claimed by two tasks : {'V520012': ['P2-25', 'P3-19']}
outside V500000-549999: none
{'adapter': 320, 'app': 219, 'base': 141, 'india': 118, '3pl': 117}
```

- **`V520012` is a false positive.** `p3-19.md:4`'s header reads `Migrations **—**
  (\`whad_oem_orders\`, \`whad_oem_order_lines\` already exist at \`V520012\`)` — a parenthetical, not
  a claim. `P2-25` owns it. **915 numbers, one owner each, none out of band.**
- **915, not the 914 the plan states.** `IMPLEMENTATION-PLAN.md` §8.3 prints `914` and `app: 218`.
  The extra number is **`V510215`**, claimed by `p5-13.md` for `wh_marketplace_claims` — the fix
  the P5 authoring pass applied for `D-P5-1`/`X-001` after the plan was written. The plan's §8.3 is
  stale by exactly one, and §11 item 4 predicted this: *"the moment those files exist, they win over
  §2 of this page"*. Filed as `X-042`.
- **§8.3 is not re-runnable as written.** Its command reads a transcription file `migs.txt`;
  `ls migs.txt issues/migs.txt tools/migs.txt` → *No such file or directory*. A claim whose command
  cannot be re-run is the exact class `DECISIONS.md` §7 rule 1 exists against. Filed as `X-043`.
- **Three task headers declare a module cell that does not contain their band.**
  `tools/check-design-set.py` check-4:

```
issues/p2-29.md:4: V501070-V501099 is outside the band of its declared module: warehouse V510000-V519999
issues/p3-04.md:4: V501101-V501109 is outside the band of its declared module: warehouse V510000-V519999
issues/p6-08.md:4: V524000-V524099 is claimed but the header declares no banded module (logistics, platform)
```

`P6-08` is benign — `D-2` and `00-EPIC-master.md` reserve `V524000`–`V524999` for `logistics` inside
the adapter band on purpose. **`P2-29` and `P3-04` are not.** A `V501xxx` file must live in
`warehouse-base/backend/src/main/resources/db/migration/` because `Dockerfile.backend:140-181` copies
per module. `issues/DEFECTS-FOUND.md` `D-P01-5` predicted exactly these two — *"the same reading
applies to `P2-29` and `P3-04`"* — and only `P1-20` was fixed. Filed as `X-044`.

### 3.6 Every task file carries the required sections — **HOLDS**

```bash
grep -h '^## ' issues/p[0-9]*-*.md | sed 's/ .*//;s/^## //' | sort | uniq -c
```

```
138 ## Traps
138 ## Scenarios closed
138 ## Requirements closed
138 ## Closes
138 ## Acceptance
138 ## Scope   (135 bare, 3 with a suffix — `## Scope — …`)
```

`tools/check-design-set.py` check-6 (*"task files carry the six required sections"*) — **pass, 0**.

### 3.7 What the checker says about the whole set, verbatim

```bash
python3 tools/check-design-set.py
```

```
check-1  pass    0  FR-nnn citations resolve to the FRD
check-2  FAIL   26  WH-SC-nnn citations resolve to the scenario catalogue
check-3  FAIL   46  warehouse tables in task files appear in DATA-MODEL.md
check-4  FAIL    3  Flyway versions: claimed once, inside the module band
check-5  pass    0  #NN issue cross-references resolve to issues/CREATED.md
check-6  pass    0  task files carry the six required sections
check-7  FAIL    8  finding ids resolve to a real finding in their owning review
check-8  pass    0  IMPLEMENTATION-PLAN.md §2 and issues/ agree on the task list
check-9  FAIL    6  every task sits in exactly one phase epic's task region
check-10 FAIL    3  every FR-nnn is owned by exactly one task
check-11 FAIL   14  no id is used for two different kinds of thing
check-12 FAIL    1  WS-nnn citations resolve to BUILD-SPEC-SCREENS.md

107 violations across 12 checks
```

> **The run before this document existed reported 116.** The difference is nine and all of it is
> bookkeeping, not repair: the two defect logs this register's companion replaced carried four
> violations of their own (three `WH-SC-301`, one `WS-238`), and this register and
> `DESIGN-SET-DEFECTS.md` quote the dangling ids they *report* — so both files declare a narrow,
> id-named exemption at the top, which the checker prints on every run:
>
> ```
> check-2   exempt 15 mentions — scenario-citations 10 (3 declarations in 3 files) · code-block 5
> check-7   exempt 39 mentions — finding-citations 31 (2 declarations in 2 files) · code-block 8
> check-12  exempt  6 mentions — screen-citations  5 (3 declarations in 3 files) · code-block 1
> ```
>
> **No violation was suppressed that the exemption does not name by id.** `X-040`, `X-045` and
> `X-001` remain open and still fail against the files that actually carry them.

Read against this register:

> **Status 2026-09-02: every row below is now closed, and the checker exits 0.** The `Disposition`
> column records how — **FIX** (the design set was wrong and was corrected), **FENCE** (a narrow,
> id-naming `begin`/`end` directive over a legitimate quotation) or **REPORT** (left failing and
> recorded). No check was weakened, deleted or made advisory to get there.

| Check | Real, or an artefact? | Where it is filed | Disposition |
|---|---|---|---|
| **check-2** (26) | **artefact** — all 26 are `WH-SC-301`, the allocation marker (§3.4) | `X-040` | **FENCE** — 29 region fences naming only `WH-SC-301`, in the catalogue, the two phase epics and the 23 P5/P6 tasks that reserve from it |
| **check-3** (46) | **real, and mostly already known** — 46 tables named in task files with no `DATA-MODEL.md` row. They are the `D-P4-3` wave-2 India orphans, `D-P5-1`/`D-P5-2`/`D-P5-3`'s new tables, and the report/archive tables the tasks invent | `X-053`, superset of `X-002` `X-003` `X-012` | **FIX + FENCE** — 4 typos corrected; **11 tables added** to `DATA-MODEL.md` §2 and §7 (`WHB-64` `WHB-65` `WHB-66` `WH-115` `WIN-05` `WIN-22`); the 20 `*_rpt_*` **grid identifiers documented as non-tables** in §8.3 note 4; 22 prior-art / counter-example quotations fenced by id |
| **check-4** (3) | **2 real, 1 benign** (§3.5) | `X-044` | **FIX** — `p2-29`/`p3-04` now name `warehouse-base`; `p6-08` withdraws `V524000`–`V524099`, and `D-2` / `DATA-MODEL.md` §2.5.6 now state that `logistics` gets no band here |
| **check-7** (8) | **real** — 5 R2 capability-matrix rows cited as findings in `COMPETITOR-BENCHMARK.md` (`T-244` `T-264` `T-325` `T-326` `T-337`), 1 fabricated `E-754`, 2 unpadded `E-1`/`E-8` in R6. **The exact failure `DECISIONS.md` §7.4a says was already caught four times** | `X-045` | **FIX ×7 + FENCE ×1** — the five matrix rows are now cited as `R2 §1.n row N`; `E-1`/`E-8` rewritten as `§L items 1–8`. **`E-754` was not fabricated**: it is the tail of *IEEE-754* at `R1:441`, quoted in §10 to explain why the counting command excludes it — fenced by id |
| **check-9** (6) | **real, mechanical** — six phase epics put `__TASKS__` on a `## ` heading line, which `create-issues.sh` corrupts on substitution | `X-046` | **FIX** — all six now carry `## Tasks` + `__TASKS__` alone; 101 hand-maintained checklist rows deleted |
| **check-10** (3) | **real** (§3.3) | `X-039` | **FIX** — `P2-14`'s §2 row carried two **escaped pipes**, splitting it into 9 cells and moving `Closes` out of column 6 |
| **check-11** (14) | **real** — `I-10`…`I-20` are defined by **two** registers (`DATA-MODEL.md` enforceable constraints and `IRREVERSIBLE.md` irreversible rows), and `DECISIONS.md` §6 declares no namespace for `I-`, `WS-` or R1 §8's `T-n` traps | `X-047` | **FIX** — the irreversible register renamed **`IRR-01`…`IRR-63`**, file by file and verified in context; `IRR-`, `WS-` and the `T-n` trap register declared in `DECISIONS.md` §6 |
| **check-12** (1) | **real** — `WS-238`, claimed by `p5-13.md` for the marketplace-claim queue, has no row in `BUILD-SPEC-SCREENS.md` §1 | `X-001` | **FENCE + partial FIX** — the *table* it needed now exists (`wh_marketplace_claims`, `WH-115`, `V510215`); the **screen id remains unallocated** and is fenced as the next-free marker. `X-001` stays open on the screen row |

**The checker has no check that every finding is dispositioned.**
`grep -c "GAP-REGISTER" tools/check-design-set.py` → **0**. `D-12` says the script *"fails if any
finding is untraced"*; it does not, and cannot, until this register is machine-readable to it.
Filed as `X-048`, with the recommended check in §7.

---

## §4 · `NEEDS-TASK` — what is not owned

**Fourteen of 575.** This list is short because it is honest, not because it was padded down: each
row below was reached by reading the finding, then failing to find its behaviour in the FRD, in
`DATA-MODEL.md`, in a `D-n`, in an `OD-n`, in `IRREVERSIBLE.md`, in a refusal row, or in any of the
138 task files. **Each row prints the negative grep that establishes it.**

The opposite error was available and was refused: eleven further findings could have been waved at a
nearby task and called covered. They are the `WONTFIX` rows in §2.5, each carrying the sentence — from
the lens itself or from `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §10 — that declines it.

| # | Finding | Sev | What it asks for | The negative evidence | What it would take |
|---|---|---|---|---|---|
| 1 | **`S-035`** | **BLOCKER (segment)** | Pharma licence gating: licence number/type/expiry on our entity and on every counterparty, a hard despatch block against an expired licence, and the Schedule H1 register | `grep -nE '^\| \*\*FR-[0-9]{3}\*\*.*licence' FRD` → 2 rows, neither about a licence register. `whin_entity_licences`, `whin_counterparty_licences`, `whin_licence_types`, `whin_licence_quantity_ceilings`, `whin_schedule_h1_register`, `whin_recall_notifications` appear in `INDIA-LOCALISATION-PACK.md` §11.2 group H and in **no** `DATA-MODEL.md` §7.6 row and **no** task | **A new P4 task, `P4-13`** — the regulated-goods licence pack. Needs an `FR-` row first (there is none), a `DATA-MODEL.md` §7.6 block, and a migration in `V540000`–`V540199`. See `X-013`: the phase description in four documents already promises it |
| 2 | **`S-005`** | MAJOR | An SSCC allocator: GS1 company prefix, extension digit, serial reference, check digit, per-key counters | `grep -in "gs1" docs/DATA-MODEL.md` → **0**. `FR-100` carries only the `sscc` **column** on the LPN | **Fold into a new P3 task, `P3-24`** with `S-010`/`S-017` (row 4) — one GS1 identity task. *"Not derivable later for labels already printed"* is R5's own note |
| 3 | **`S-010`** | MAJOR | `epc` on the serial and the LPN; a reader-event endpoint idempotent on `(epc, read_point, event_at)` | `grep -inE "RFID\|EPC Gen2" FRD` → **0** | Same task as row 2. The two **columns** are v1-shaped; the ingestion endpoint is v2 |
| 4 | **`S-017`** | MINOR | `barcode_format` must admit `GS1_DIGITAL_LINK`, and the scan resolver must accept a URI | `grep -in "Digital Link\|barcode_format" FRD` → **0** | Same task as row 2. **R5 places the enum *value* in v1 deliberately** — widening a vocabulary later is a migration, and `D-10` makes it a catalogue row, which makes this cheap only if the catalogue exists |
| 5 | **`S-052`** | MAJOR | Every issue carries a cost object (job, cost centre, work order) so consumption is reportable by it — Companies Act s.148 cost records | `grep -in "cost object\|cost centre" FRD` → **0**. `E-065`'s workshop issue has a job, but no general cost-object dimension | **A P2 amendment, not a new task**: one nullable `cost_object_type`/`cost_object_id` pair on the movement line, authored inside `P0-02`'s `V500030` — because the movement is sealed against `UPDATE` from that migration onward (`IRR-41`'s shape). **If it misses `V500030` it is unbackfillable**, which is why it is second on this list by urgency despite being MAJOR |
| 6 | **`S-097`** | MINOR | The integration surface: API keys, webhooks, rate limits, replay | `grep -in "webhook\|API key\|rate limit" FRD` → **0**. `OD-8` covers only *how a consumer authenticates to the port*, not the surface | **A new P5 task, `P5-22`.** v2, and it should be platform work — `OD-8`'s recommendation (a platform service principal) is the same conversation |
| 7 | **`S-049`** | MINOR | Counterfeit-part control: an authorised-supplier flag on item × supplier, and a `SUSPECT` disposition | `grep -rin counterfeit docs/ issues/` outside `reviews/` → **0** | Two rows and a flag. Fold into `P3-19` (the dealer OEM-order task) or a new `P3-24`. R5 §6 lists it as an automotive-distribution addition at v2 |
| 8 | **`F-073`** | MINOR | India pharma: drug-licence numbers on the owner and the warehouse with expiry alerts, prescription-schedule flags on the item | The same negative evidence as row 1 | **Same task as row 1** (`P4-13`). `F-073` and `S-035` are one unit of work seen from two lenses |
| 9 | **`E-081`** | MINOR | A supplier claim register unifying receipt discrepancies, expiry/breakage claims and price claims, with an ageing report | `grep -rn "supplier_claim\|supplier claim" docs/ issues/` outside `reviews/` → **0** | **A new P5 task, `P5-23`.** v2. Marg/GoFrugal parity in pharma-and-FMCG-adjacent distribution; for a dealership it is the OEM claim book |
| 10 | **`E-069`** | MINOR | A pricing matrix by cost band / margin, resolved most-specific-first with the resolved row recorded on the sale line | `grep -rn "pricing_matri\|pricing matrix" docs/ issues/` outside `reviews/` → **0** | **Do not build it here until `E-078` (row 11) is answered.** If price lists live in `accounting`, so does this |
| 11 | **`E-078`** | MINOR | One home for price lists — `accounting` already has `acc_price_lists` (`V600138`), `accessories` has three pricing tables | `grep -n "price list" docs/MODULE-INTEGRATION.md` → **0**. No boundary row anywhere in the set | **A `D-n` row, not a task.** It is one paragraph in `MODULE-INTEGRATION.md` and it unblocks row 10 |
| 12 | **`E-085`** | MINOR | Shared vocabularies across the two ledgers: UoM, reason codes, movement types, warehouse codes seeded from one list | `COEXISTENCE.md` §5.4 mitigation **`M4`** is named in **no** task file: `grep -ohE '\bM[1-9]\b' issues/p*.md \| sort -u` → `M1 M2 M3 M5 M6 M8 M9` — every mitigation except `M4` | **Fold into `P2-27`** (the coexistence task, which already ships `M1`, `M2` and `M8`) or a small P3 task. One shared seed list, referenced by both sides' migrations |
| 13 | **`G-037`** | MINOR | Drop-ship: decide whether it produces movements at all — no movements, or a zero-duration `SUPPLIER`→`CUSTOMER` pair | `grep -rin "drop.ship" docs/ issues/` outside `reviews/` → **0** | **An `OD-` row, not a task.** R7's own instruction is *"decide in v1's FRD; implement in v2"*, because *"choosing it in v3 means history is missing or double-counted"* |
| 14 | **`P-053`** | MINOR | The onboarding narrative — the prior art's 1,719-line `WAREHOUSE_EXPLAINED.md` shape: every menu against one running example, with *depends on / used by* | `P3-23` ships **in-product help per screen** (`S-094`, `FR-442`) — a different artefact | **A documentation task, or an explicit decline.** The cheapest honest answer is a one-line `WONTFIX` in this register once someone decides |

### 4.1 The four proposed tasks, with their next free ids

Ids taken from the file glob, which `DECISIONS.md` §6 makes the authority
(`ls issues/pN-*.md | tail -1`): highest today is `p0-17` · `p1-20` · `p2-29` · `p2in-04` · `p3-23` ·
`p4-12` · `p5-21` · `p6-12`.

| Proposed | Phase | Closes | Why one task and not three |
|---|---|---|---|
| **`P4-13`** · The regulated-goods licence pack | P4 · v2 | `S-035` `F-073` | One licence object, one expiry clock, one despatch guard, one register. Splitting it produces three tables that each need the other two. **It also discharges `X-013`**, the promise four phase descriptions make and no task keeps |
| **`P3-24`** · GS1 identity — SSCC allocation, EPC and Digital Link | P3 · v1.1 | `S-005` `S-010` `S-017` `S-049` | All four are keys and code formats on the same two objects (serial, LPN). `S-049`'s authorised-supplier flag rides along because it is the same item × party table |
| **`P5-22`** · The integration surface | P5 · v2 | `S-097` | Standalone by nature — API keys, webhooks, rate limits, replay — and it should be argued as platform work first |
| **`P5-23`** · Supplier claim register | P5 · v2 | `E-081` | One header, one line, one ageing report |

**Three of the fourteen are not tasks at all** and should be recorded as such rather than
manufactured into backlog: `E-078` and `E-069` need one `D-n` between them, `G-037` needs one `OD-n`,
and `P-053` needs a decision. **`S-052` is not a task either — it is two columns that must ride
`V500030`, and `V500030` is `PNR-1` **and** `PNR-2`.**

---

## §5 · The BLOCKER audit

**123 findings are scored BLOCKER by their lens.**

```bash
awk -F'\t' '$2=="BLOCKER"' DISPOSITION.tsv | wc -l                    # → 123
awk -F'\t' '$2=="BLOCKER"{print $3}' DISPOSITION.tsv | sort | uniq -c
```

| Disposition | BLOCKERs |
|---|---:|
| **CITED** — a task's `## Closes` names it | **85** |
| **COVERED-uncited** — an FRD row or a named design-set row owns it | **36** |
| **DECIDED** — `S-062`, answered by `D-9` | **1** |
| **NEEDS-TASK** — **`S-035`** | **1** |
| | **123** |

### 5.1 The one unowned BLOCKER

> **`S-035` · Pharma licences, the Schedule H1 register and the despatch guard · BLOCKER (segment) ·
> adapter/`warehouse-india` · v2 — owned by nothing.**

This is the most important line in this document. It is **not** a surprise and **not** an oversight of
one author — three independent passes reached the edge of it and stopped:

- `issues/DEFECTS-FOUND.md` `D-P4-3` (→ `X-012`) lists group H's six tables as *"unowned"*.
- `issues/DEFECTS-FOUND.md` `D-P4-4` (→ `X-013`) proves the deeper cause: `DECISIONS.md` §5,
  `IMPLEMENTATION-PLAN.md` §1.6, `PORT-AND-ADAPTER-CONTRACT.md` §9.6 and the FRD §6.18 preamble all
  promise *"the regulated-goods packs"* at v2/P4, and **no `FR-nnn` covers them**. §8's claim
  *"every requirement is owned by exactly one task"* stays true only *because there is no requirement*.
- `p4-05.md` names group F as unowned and states the Legal Metrology boundary rather than absorbing it.

**Every author did the right thing and the gap still shipped**, because no document's own integrity
check could see it: a promise with no `FR-` behind it is invisible to a requirement-to-task tracer.
That is precisely the class of failure this register exists to catch, and it is caught here by
starting from the *finding* rather than from the requirement.

**Two honest options, and both are cheap today:**
1. Write the `FR-` rows and `P4-13` (§4.1), or
2. Amend the four phase descriptions to stop promising regulated goods, and move `S-035` to `WONTFIX`
   with *"pharma is not a target segment"* written down.

**Silence is the third option and it is the one that fails**, because R5 §6 marks pharmaceutical
distribution `CANNOT SERVE` and a salesperson reading `DECISIONS.md` §5 will bid it.

### 5.2 The 36 `COVERED-uncited` BLOCKERs — a lesser, real risk

These are owned, but **only through an FRD row's `Closes` column**, so a builder reading only their
task file never meets the finding:

`E-007` `E-014` `E-026` `E-047` `E-048` `E-055` · `F-081` `F-082` `F-083` `F-084` ·
`G-017` `G-027` `G-039` `G-040` `G-045` `G-053` `G-067` · `P-003` ·
`S-001` `S-004` `S-007` `S-012` `S-013` `S-022` `S-028` `S-041` `S-064` `S-082` `S-085` `S-086` `S-092` ·
`T-006` `T-009` `T-012` `T-013` `T-091`

Four of them are day-one ship-blockers in R5 §7.1 — **`S-064`** (owner in the position key),
**`S-085`** (allocation concurrency), **`S-082`** (restore) and **`S-092`** (support impersonation).
`S-064` is the single highest-leverage row in the whole review set — *"one column in v1 turns a
cannot into a can"* — and **no task file names it.** Its FRs (`FR-107`, `FR-230`) are owned by
`P0-02` and `P0-12`, so the work will happen; but if `P0-02`'s ledger review is done against the
task file alone, the reviewer never reads why.

**Remedy, one line each:** add the id to the owning task's `## Closes`. It costs 36 lines and it is
the difference between *traceable* and *traced*.

> **Applied 2026-09-02.** All 36 are now in a `## Closes` block, each under a line saying why it was
> added, across sixteen task files — `P0-02` took eleven of them, `P1-03` four, `P1-02` three,
> `P0-08` three, and the rest one or two each. `S-064` is now named in `p0-02.md`, which was the
> point: a reviewer doing `P0-02`'s ledger review against the task file alone now reads *why* the
> owner column is in the position key. **The finding was that the ids were invisible, not that the
> work was unowned** — no scope moved, and the FRD rows that owned them still own them.

---

## §6 · The industry and segment verdicts, consolidated

From R3 §5 (the two-inventory cost), R5 §6 (the industry verdict table), R5 §7 (ship-blockers) and
`COMPETITOR-BENCHMARK.md` §8/§9 — each tied to the version that changes it and the task that carries it.

### 6.1 Segment verdicts, and the version that moves each one

| Segment | R5 §6 verdict | What changes it | Version | Owning task | Register status |
|---|---|---|---|---|---|
| Automotive spare-parts distribution | **SERVES WITH ADDITIONS** | cores (`S-047`), VIN recall (`S-048`), lost sales (`S-063`), EPR (`S-050`), counterfeit control (`S-049`) | v1.1–v2 | `S-047`→`P5-15` · `S-048`→`P2-26` · `S-063`→`P2-15`/`P2-25` · `S-050`→`P4-08` · **`S-049` unowned** | 4 of 5 owned |
| Vehicle dealership parts | **SERVES WITH ADDITIONS** | counter sale + VOR (`S-063`), GSTIN per branch (`S-022`, mandatory) | v1–v1.1 | `S-063`→`P2-15`/`P2-25` · `S-022`→`FR-025`/`FR-079`/`FR-080`/`FR-305` (`P0-02` `P1-05` `P1-17`) | owned |
| Workshop / service parts issue | **SERVES WITH ADDITIONS** | `warehouse-adapter-services` (`S-061`) — reserve → issue with the job as cost object → return unissued → VIN | v1.1 | `S-061`→`P2-26` | owned; **but the general cost-object dimension (`S-052`) is unowned** |
| Accessories retail | **SERVES WITH ADDITIONS** | absorb-vs-coexist (`S-062`) + MRP on the lot (`S-033`) | v1 | `S-033`→`P1-07`/`P1-03` | **`S-062` DECIDED by `D-9`: coexist, permanently.** Cost priced in `COEXISTENCE.md`; `M4` unowned (`E-085`) |
| **Pharmaceutical distribution** | **CANNOT SERVE** | three v1 schema rows — LPN/SSCC (`S-004`), EPCIS dimensions (`S-007`), transformation genealogy (`S-008`) — then licences (`S-035`) and serialisation (`S-036`) | v1 schema · v2 · v3 | `S-004`→`P1-02`/`P1-07` · `S-007`→`P0-02` · `S-008`→`P5-19` · **`S-035` unowned** · `S-036` WONTFIX | **the v1 columns land; the v2 licence pack has no owner.** §5.1 |
| Food & FMCG | **SERVES WITH ADDITIONS** | best-before vs use-by (`S-038`), min remaining shelf life (`S-039`), recall (`S-040`), FSSAI gating | v1–v1.1 | `S-038`→`P1-07` · `S-039`→`P2-05` · `S-040`→`P2-21`/`P5-14` | owned; FSSAI licence gating is inside `S-035`'s gap |
| Cold chain | **CANNOT SERVE** | sensor readings, excursion events, QA disposition (`S-041`) | v2 | `S-041`→`FR-068`→`P1-03` (zone columns, v1) | **deliberate deferral**, recorded in FRD §10's deferral row B |
| **Apparel / footwear** | **CANNOT SERVE** — *"the largest addressable segment we are declining"* | style × variant matrix (`S-056`) as **v1 schema** | v1 schema · v2 screens | `A-3` accepted it; `FR-443`–`FR-445`; `S-056`→`P1-01`/`P1-03`/`P5-20` | **verdict overturned by `A-3`.** `COMPETITOR-BENCHMARK.md` §9 row 2 still reads UNRESOLVED (`X-050`) |
| Electronics (serialised) | **SERVES WITH ADDITIONS** | specific identification (`S-065`), dual-custody picking (`S-057`) | v1 · v1.1 | `S-065`→`P2-16`/`P2-18` · `S-057`→`P2-05` | owned |
| Chemicals (hazmat, catch weight) | **SERVES WITH ADDITIONS** | catch weight (`S-013`, **v1 schema**), segregation matrix + SDS + DG docs (`S-042`) | v1 · v2 | `S-013`→`FR-065`→`P1-03` · `S-042`→`FR-067`→`P1-03` | owned; threshold-quantity reporting (`S-043`) is WONTFIX/v3 |
| Construction materials | **SERVES WITH ADDITIONS** | weighbridge as a legal instrument (`S-034`, `S-058`) | v2 | `S-034`/`S-058`→`P5-17` | owned; **Legal Metrology's own promise is `X-013`** |
| E-commerce fulfilment | **SERVES WITH ADDITIONS** | channel SKU mapping, single-line waves, returns grading, manifests (`S-059`) | v2 | `S-059` → `P5-09` + `P5-13` (id in neither `## Closes`) | owned |
| **3PL contract logistics** | **CANNOT SERVE — one column decides it** | `owner_party_id`/`owner_type` in the position key (`S-064`) | **v1** | `P0-02` via `FR-107` | **owned, but the id is in no `## Closes`** (§5.2). `D-5` settles it |
| Spare parts for assets / field service | **SERVES WITH ADDITIONS** | the van as a mobile, person-owned location (`S-060`) | v1.1 | `P3-20` | owned; the location model permits it from v1 |

**Read across the column: eleven of fourteen segments are reachable, and the two `CANNOT SERVE`
verdicts that remain — pharma and cold chain — are one unowned task and one recorded deferral.**
Apparel's `CANNOT SERVE` has already been overturned by `A-3` and only the benchmark has not caught up.

### 6.2 The two-inventory cost, and what is mitigated

`D-9` takes the decision; R3 §5.2 prices it at **eleven costs C1–C11**, and R3 §5.4 offers **nine
merge-free mitigations M1–M9**. Ownership, computed:

| Mitigation | Addresses | Version | Owner |
|---|---|---|---|
| `M1` cross-map registry | C1, C2 | v1 | `P1-04` (`D-9`'s mitigation 1) · `P2-27` |
| `M2` category-ownership rule + reconciliation report | C2 | v1 | `P2-27` |
| `M3` union valuation report | C3, C4 | v1.1 | `P3-17` (`E-084`) — **blocked on an unnumbered decision** (`X-036`) |
| `M4` shared vocabularies | C1, C4, C5 | v1.1 | **none — `E-085`, §4 row 12** |
| `M5` cross-system availability lookup | C6 | v1.1 | named in `p2-27.md` as *not this task*; no other owner |
| `M6` one document layer for statutory movements | C7 | v1 | `P2-IN-03` — but `COEXISTENCE.md` §5's `M6` is superseded by `A-4` and `FR-308` (`X-037`) |
| `M7` backport compliance columns to accessories | C8 | v1 | `P2-27` boundary; the accessories-side migration has no task |
| `M8` no cross-writes, ever | C2, C9 | v1 | `P2-27` |
| `M9` one reporting scope | C4 | v1.1 | named in `p2-27.md` as *not this task*; no other owner |

**Four of the nine load-bearing-by-R3's-own-account mitigations (`M1` `M2` `M7` `M8`) are owned.**
`M4` is owned by nothing, and `M5`/`M9` are v1.1 with no task. R3's warning applies literally:
*"without `M1` and `M2`, C2 — the same unit counted twice — is not merely unmitigated, it is
undetectable."* Those two **are** owned, so the load-bearing half holds.

### 6.3 The product verdict, and where it is stale

`COMPETITOR-BENCHMARK.md` §8.2 states the v1 product in one paragraph and closes:
*"…and — as the ladder currently reads — **not yet able to take a return**, which is the one gap that
would embarrass it in front of any buyer in any segment."*

**That sentence is no longer true.** `DECISIONS.md` §5.1 `A-1` moved basic returns into **v1/P2** and
`A-2` moved templated printing into **v1/P2**, and:

```bash
grep -coE '`A-[1-4]`' docs/COMPETITOR-BENCHMARK.md   # → 0
```

The benchmark carries **no** reference to any of the four amendments, so its §8.1 rows 12 and 15, its
§8.2 headline verdict, and four of its sixteen §9 disagreement rows (1 returns · 2 apparel · 3 cost
layers · 4 printing, all marked UNRESOLVED) are stale against the spine that outranks it. Same check
on the rest of the set: `COEXISTENCE.md` 0 · `MODULE-INTEGRATION.md` 0 · `PLATFORM-DEPENDENCIES.md` 0
· `IRREVERSIBLE.md` 0 (defensible — it is schema-level, not ladder-level) · FRD 17 · plan 21 ·
`DATA-MODEL.md` 12 · `INDIA-LOCALISATION-PACK.md` 5 · `BUILD-SPEC-SCREENS.md` 3 ·
`SCENARIO-CATALOGUE.md` 3 · `PORT-AND-ADAPTER-CONTRACT.md` 1. Filed as `X-050`.

**The corrected one-paragraph verdict**, with the amendments applied: at v1 the product is a correct,
single-owner, multi-site stock ledger with an automotive-parts catalogue, an India-correct schema,
**basic returns**, **templated document and label printing including a ZPL path**, and the **v1
variant schema** — but not a warehouse-execution system (no RF, no print server, no waves until
v1.1), not an Indian compliance product (the schema is right, the registers are v2), and not a 3PL
platform (the columns are there, the billing is v2).

---

## §7 · Ship-blockers — what must be true before the first real customer

R5 §7.1 ranks eleven of its 36 BLOCKERs as day-one. Traced here to the task that carries each.

| # | R5 §7.1 | The one-sentence reason | Owning task | Phase | Register status |
|---:|---|---|---|---|---|
| 1 | **`S-064`** two systems of record for stock | the first customer who buys both modules gets two stock reports that disagree at the first month end | `P0-02` (`FR-107`) · `P0-12` (`FR-230`) | **P0** | `COVERED-uncited` — **add the id to `P0-02`'s `## Closes`** |
| 2 | **`S-087`** nothing prints a label | `grep -rli "zpl"` → 0; a warehouse that cannot print a pallet label cannot receive its first pallet | `P2-14` (`FR-224`) · `P3-08` | **P2** | CITED. `A-2` moved it to v1 — **but `IMPLEMENTATION-PLAN.md` §2 does not assign `FR-224`/`FR-225` to any task** (`X-039`) |
| 3 | **`S-089`** no recovery when the system rejects a move that physically happened | operators learn within a week to work around the system, and every number after that is fiction | `P2-01` | P2 | CITED |
| 4 | **`S-085`** + `S-076` allocation concurrency and negative-stock policy | two pickers, one unit; a generated `quantity_available` column does not protect against it | `S-085`→`FR-016`/`FR-175`→`P0-03` · `S-076`→`FR-014`→`P0-03` | **P0** | both `COVERED-uncited`. **Both must be decided before the position table's constraints are written** |
| 5 | **`S-079`** + `S-080` opening stock and migration from Tally/Busy/Marg | there is no way to onboard customer one without loading their stock, with value, from an incumbent | `S-079`→`P2-19` · `S-080`→`P3-18` · `E-088`→`P2-18`/`P2-19` | P2 · **P3** | CITED. **`S-080` sits in P3, after the first customer would need it** |
| 6 | **`S-082`** restore does not exist | we would hold statutory stock records under s.128 with a `pg_dump` and no executed restore | `FR-429`→`P0-16` | **P0** | `COVERED-uncited`. **Platform work — it does not compete with warehouse engineers, and it has no platform task in this set** |
| 7 | **`S-022`**+`S-023`+`S-024` GSTIN, challan, e-way bill | an Indian warehouse that cannot produce an e-way bill cannot move a truck | `P2-IN-01`…`P2-IN-04` | **P2-IN** | CITED/`COVERED-uncited`. `A-4` created the wave. **`P2-IN-04` is blocked by `X-027`** — `FR-195`'s gate pass has no v1 host screen |
| 8 | **`S-069`** the ledger nets to zero over locations, including virtual ones | if v1 allows a null `from`/`to`, in-transit, consignment and job-work stock are all nowhere | `P2-02` · `P1-05` (`FR-084`) | **P0/P1** | CITED. **Blocked by `X-029`** — the value-offset virtual location has two names and `FR-084` seeds neither |
| 9 | **`S-028`** reason codes as a closed, tax-mapped catalogue | a year of free text cannot be reclassified into the six statutory categories | `FR-019`/`FR-315`→`P0-04` | **P0** | `COVERED-uncited` |
| 10 | **`S-067`** `handover_id` + `posting_status` on the movement row | without them, *"does stock tie to the GL"* is unanswerable for exactly the period the first audit covers | `P0-12` `P2-18` | **P0** | CITED. **Blocked by `X-026`** — the columns must ride `P0-02`'s `V500030`, which `P0-12` does not own |
| 11 | **`S-092`** no support impersonation | on day two we cannot answer the customer's question without their password or a standing admin account | `FR-409`→`P0-13` | **P0** | `COVERED-uncited`. **The schema half (`on_behalf_of_actor_id`) must land in the first audit migration** |

### 7.1 The gates that must close before P0 merges

Not findings — **decisions with a deadline**, from `DECISIONS.md` §3 and `IMPLEMENTATION-PLAN.md` §7.

| Gate | Deadline | Status |
|---|---|---|
| **`OD-12`** — the partition key: `occurred_at` (FRD + `DATA-MODEL.md` `WHB-30`) vs `posting_date` (`PD-D5`) | **before `P0-02`** — `V500030` is `PNR-1` **and** `PNR-2` | open; recommendation is `occurred_at`. **Numbered 2026-09-02** (`X-024`); was unnumbered when this row was written; the next is free and unassigned (`X-024`) |
| **`OD-10`** — is MRP a dimension of the position key? | **before `PNR-1`** — the tightest deadline in the set | open; recommendation is *no* |
| **`OD-11`** — do value-only movements conserve value? Is there an `L-15`? | before P2 valuation | open. **`DECISIONS.md` §4 stops at `L-14` and `DATA-MODEL.md` §6.3 stops at `I-20`** (`X-030`) |
| **`OD-7`** — precision scales | before `P0-02` | open; adopt accounting's resolved set |
| **`OD-8`** — how an out-of-process consumer authenticates to the port | before `P0` builds the port | open. **Platform work, and the only thing platform must build for warehouse** |
| **`OD-1`** — the reciprocal accounting edits | before accounting's P3 **and** before `P0-02` | open; a *different* repository's design set |
| **`OD-13`** — the value-offset location's code: `VALUE_OFFSET` (`OD-11`, `P2-28`) vs `LANDED_COST_OFFSET` (`PC-12`), and `FR-084` seeds neither | **before `P1-05` writes `V500013`** | open; recommendation is `VALUE_OFFSET`. **Numbered 2026-09-02** (`X-029`) |
| **`OD-14`** — is value conservation a fifteenth invariant `L-15`, or a movement-type behaviour column? | **before `P0-02`** — the guard is a constraint on the table | open; recommendation is `L-15` plus a matching `I-21`. **Numbered 2026-09-02** (`X-030`) |
| **`OD-15`** — `M3`, the union valuation report: build it (R3 `M3`/`E-084`) or refuse it (R7 §4.6) | *"before the P2 reports task is written"* — **which is now** | open; recommendation is *not in v1*. **Numbered 2026-09-02** (`X-036`) |

**All nine gates now have an id.** When this section was written, four of them did not: the partition
key, the value-offset code, the value-conservation invariant and `M3` sat outside the `OD-` namespace
that `DECISIONS.md` §3 owns, and an unnumbered gate cannot be tracked. They were allocated
**`OD-12`…`OD-15`** on 2026-09-02 and each is cited by id in its blocking task file. **Numbering a gate
does not answer it** — all nine are still open, and every deadline above still stands.

### 7.2 The shortest honest statement of readiness

> **`platform` + `warehouse-base` + `warehouse` cannot be sold to a first customer until: the eleven
> R5 §7.1 ship-blockers are built (all eleven have an owning task, and two of the eleven are gated by
> a defect in this set — `X-027` and `X-029`); the nine gates in §7.1 are answered before `V500030`
> merges — the four that were unnumbered are now `OD-12`…`OD-15`, which makes them trackable, not
> settled; and `S-035` is either written as a task or written off as a declined segment.**
>
> Everything else on the 575-finding list is a version placement, and the version placements are
> carried in 138 task files.

---

## §8 · How to keep this register true

1. **Every new task file adds its finding ids to `## Closes`.** The register is reconstructible from
   `issues/` by one `awk`; it stops being reconstructible the moment a task closes a finding silently.
2. **Add the 36 `COVERED-uncited` BLOCKER ids to their owning tasks** (§5.2). 36 lines, and it moves
   them from *traceable* to *traced*.
3. **Teach `tools/check-design-set.py` the disposition check `D-12` promises.** It has none today
   (`grep -c GAP-REGISTER tools/check-design-set.py` → 0). The check is:

```python
# check-13: every finding in reviews/R1-R7 has a disposition row in docs/GAP-REGISTER.md §2.5
universe = findings_from_reviews()                 # 575, incl. the T-020a suffix form
dispositioned = ids_in_table(GAP_REGISTER, '§2.5') # first column of the register table
assert not (universe - dispositioned), universe - dispositioned
# and: no row may be NEEDS-TASK without a §4 entry naming what it would take
```

4. **Re-run §3's six commands on every PR that touches `issues/` or `docs/`.** Four of the six hold
   today; the two that fail are filed, not hidden.
5. **When a `NEEDS-TASK` row gets a task, move it — do not delete it.** The row becomes `CITED` and
   names the task. A finding that disappears from this table is the failure mode, not the fix.
