TITLE: [Warehouse] [Finding] W22 · Full-history ageing performance remains unmeasured
LABELS: task,warehouse
issue: 216
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W22** · Module **`warehouse`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P1 (audit recommendation, not a programme phase). **Evidence class:** Verification gap. **Applies to:** Large/old ledgers.

## Scope

### What happens / remaining gap

Removing the lower window protects old stock correctness but requires a measured query plan and workload test. Later last-outward changes do not themselves prove scale.

### Required work

Benchmark representative history, indexes and concurrent operations; retain correctness.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#182](https://github.com/neetub1508/warehouse-issues/issues/182); [WhStockAgeingRepositoryCustomImpl.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/repository/WhStockAgeingRepositoryCustomImpl.java#L1).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W22** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #182 — WS-212 Ageing now scans the whole ledger: PP-7's bound was removed on purpose, and the cost is unmeasured.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.

## Acceptance

- [ ] Oldest-stock buckets remain correct and latency meets an agreed measured target without slowing posting.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Valuation and period close**: Old surviving stock, backdated events, FIFO/average, rounding, policy changes and period refusal. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Relevant flow check — **Performance and topology**: Reference data size and concurrency; report load, imports, replica routing, DB locks and resource limits. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #182</summary>

Raised so the reason is on record before someone hits the latency and re-litigates it. **This is a deliberate trade, not a defect.**

**What changed.** P2-20 (#136) first put WS-212 Stock Ageing inside PP-7's 365-day window, then took it back out (`4d1d3dced2`).

**Why the window had to go.** WS-212's `over 365 days` bucket is *by definition* stock whose last movement is more than 365 days old. With `movedFrom = asAtDate − 365d`, such a grain has **no movement inside the window at all**, so it does not land in that bucket — it disappears from the report. The oldest-stock bucket would have read near zero, and that bucket is the commercial point of an ageing report: obsolescence provisioning and OEM obsolescence returns both read it. A performance bound that deletes the report's most important row is not a bound, it is a wrong answer.

**What replaced it.** WS-212 is bounded ABOVE by its required `asAtDate` parameter, which `WhbReportParameterGuard` refuses to let a caller omit, and the grid is paginated at the database. The in-module precedent is WS-210, whose opening read deliberately carries no lower bound for exactly the same reason — everything before the period start IS the opening. Acceptance `p2-20.md:166` ("none opens on 'all time'") is satisfied by the upper bound.

**The cost, unmeasured.** PP-7's stated reason for the 365-day bound is that an unbounded ledger read is not survivable at 100M rows with `OFFSET` paging (keyset paging is v1.1). Removing the lower bound makes WS-212's `ledger` CTE and `PICKER_GRAIN` scan **every partition** of `whb_stock_movement_lines` up to `:asAtInstant` — on the grid, the count, the five-tile strip, the export **and** both cascading pickers. There was no database available to measure it, and the old partial index `idx_whb_positions_ageing` no longer serves this report at all, since the positions table is no longer read.

**What to do.**
1. Measure it — `EXPLAIN (ANALYZE, BUFFERS)` on the grid, the count and both pickers at realistic ledger volume.
2. If it does not hold, the fix is an index or a materialisation, **not** a lower bound. Candidates: a partial index supporting `MAX(occurred_at) FILTER (direction = 'OUT')` at the seven-member grain; or a maintained last-outward projection that is itself rebuilt from the ledger (and so stays `L-4`-honest, unlike reading `whb_stock_positions.last_outward_movement_at`, which was the original defect).
3. The cascading pickers are the cheapest win — they need distinct grain members, not the full fold, so they can likely be narrowed without touching the report.

Related: **#179** (WS-224 keeps its 365-day window, which makes its as-at quantity a windowed net).

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W22 -->
