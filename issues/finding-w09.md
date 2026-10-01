TITLE: [Warehouse] [Finding] W09 · Costing contract documentation and runtime evidence need reconciliation
LABELS: task,warehouse,warehouse-base
issue: 203
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W09** · Module **`warehouse-base`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P1 (audit recommendation, not a programme phase). **Evidence class:** Reported / documentation. **Applies to:** Valued stock.

## Scope

### What happens / remaining gap

The adopted settings amendment already answers several cost-policy questions that #172 calls open. Database costing tests are excluded from the default gate.

### Required work

Apply the adopted decisions, update stale wording and execute the costing integration scenarios; avoid reopening answered product questions.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#172](https://github.com/neetub1508/warehouse-issues/issues/172); [warehouse-base/backend/pom.xml](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse-base/backend/pom.xml).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W09** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #172 — [Warehouse] P2-16 follow-up · Ratify costing defaults, contract codes and run the integration tests in the gate.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.

## Acceptance

- [ ] FIFO/average, effective policy changes, rounding, negative stock and approval cost cases pass against PostgreSQL.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Valuation and period close**: Old surviving stock, backdated events, FIFO/average, rounding, policy changes and period refusal. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #172</summary>

Follow-up from #115 (P2-16 costing engine) · Design set / contract ratification · Migrations: none

## Decisions to ratify (made by the build under "use the recommendation")
1. **Default method when no valuation policy exists: weighted average (AVCO).** V500021 says the default is a company decision.
2. **Policy precedence:** category + site, then category only, then site only, then company-wide; the category must match exactly (no parent search).
3. **`layer_value` means the layer's remaining value**, so the average is Σ `layer_value` / Σ `quantity_remaining` exactly as the contract states; the V500021/V500023 comments ("quantity_in × unit_cost") are stale.
4. **Method naming:** the movement-type seed says `WEIGHTED_AVERAGE`, layers say `AVERAGE` — pick one.
5. **P0-08 port contract** gains wire fields `exchange_rate`, `cost_source_line_id` and refusal codes `EXCHANGE_RATE_REQUIRED`, `VALUATION_METHOD_NOT_SUPPORTED`, `BASE_CURRENCY_REQUIRED` (the ledger error list is frozen at 58).
6. **Test harness:** `ci-gate.sh` cannot run Testcontainers tests (no Docker socket; Testcontainers 1.21.3 also needs `api.version` pinned for this Docker engine). The costing, ledger and allocation integration tests were run by hand for #115 and pass; wire them into the gate.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W09 -->
