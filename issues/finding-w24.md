TITLE: [Warehouse] [Finding] W24 · Scheduled reports cannot yet guarantee recipient-specific scope
LABELS: task,warehouse,platform
issue: 218
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W24** · Module **`platform`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P1 (audit recommendation, not a programme phase). **Evidence class:** Code-supported / reported. **Applies to:** Customers enabling scheduled warehouse reports.

## Scope

### What happens / remaining gap

The recorded platform contract collects/render once per execution and lacks recipient identity for data filtering. Interactive scope does not prove scheduled scope.

### Required work

Implement recipient-scoped collection/rendering in the existing reporting framework before enabling sensitive warehouse schedules.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#185](https://github.com/neetub1508/warehouse-issues/issues/185); [ReportGenerationService.java:1](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/platform/backend/src/main/java/ai/platform/service/report/ReportGenerationService.java#L1).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W24** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #185 — RH-010 unmet: WS-215 cannot be scheduled without a platform commit.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.

## Acceptance

- [ ] Two recipients with different sites receive different authorized data; restricted costs remain masked.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Reports/export/search**: UI/filter/export parity, literal wildcard input, timezone dates, cost masking and scoped scheduled delivery. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #185</summary>

P2-21 (#141) shipped all seven screens, but **RH-010's scheduled-report criterion is not met and was deliberately not attempted**. Recording it so the gap is visible rather than silently absent.

## What RH-010 asked for
"A `WarehouseReportDataProvider` bean and `report_types` rows with `module = 'warehouse'` make WS-215 schedulable through platform's scheduler, with **zero platform commits**", and "a scheduled run delivers to each recipient only the rows that recipient's own scope allows".

## Why those two cannot both hold today
`ReportDataProviderInterface.collectData(String reportType, OffsetDateTime periodStart, OffsetDateTime periodEnd, UUID branchId)` carries **no principal and no recipient**, and there is no per-recipient hook above it either.

`ReportGenerationService.processExecution` calls `collectData` **once per execution**, renders **one** PDF, uploads it to **one** storage key, and only then calls `sendNotifications(...)`, which resolves recipients and hands **every one of them the same `fileUrl`**. Recipients do not exist until after the artifact does.

Warehouse's side is not the blocker: `WhbWarehouseScopeService.allowedWarehouses(UserPrincipal, String)` resolves a named user's `allowedWarehouseIds` with no SecurityContext, exactly for principal-free jobs. The provider could compute each recipient's scope — it has nowhere to deliver a per-recipient result to.

## What was considered and rejected
1. **Render unscoped** — every recipient receives every site's rows. A straight FR-405 leak.
2. **Scope to the config's branch** — a recipient with no access to that branch still receives the PDF. A smaller leak, but a leak. This is what `DealerReportDataProvider` and `ServiceReportDataProvider` do today, so it is worth asking separately whether those two leak.
3. **Seed the `report_types` row alone** — `ReportDataProviderRegistry.collectData` logs "No provider found" and renders a "Report Unavailable" PDF, so this ships a schedulable report that always mails an empty document.

Shipping nothing beats shipping a leak, so nothing was shipped.

## What would unblock it
One platform change, either:
- a `UUID recipientUserId` parameter on `collectData`, with generation moved inside the recipient loop; or
- a `boolean isRecipientScoped()` hook that makes the pipeline render once per recipient.

Both are platform commits, which RH-010 forbids — so this needs a **contract amendment**, not a workaround. RH-010's own "UNVERIFIED, and required before the provider is written" question is still unanswered, because the provider was correctly not written.

## Possibly affected beyond warehouse
`DealerReportDataProvider` and `ServiceReportDataProvider` filter on `branchId` only. If a scheduled report there has recipients outside that branch, the same leak already ships. Worth checking.

Related: #141, #183, #184.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W24 -->
