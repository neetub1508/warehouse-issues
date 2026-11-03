TITLE: [Warehouse] [Finding] W23 · Archiving and hot-ledger reconstruction are deferred
LABELS: task,warehouse,warehouse-base
issue: 217
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W23** · Module **`warehouse-base`, `warehouse`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P2 (audit recommendation, not a programme phase). **Evidence class:** Intentional scope limit. **Applies to:** Long-lived/high-volume deployments.

## Scope

### What happens / remaining gap

Archiving is a later-version task. It must not be assumed operational just because partitions and retention configuration exist.

### Required work

Publish supported retention/capacity bounds; implement archival opening balances before activating archive.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#94](https://github.com/neetub1508/warehouse-issues/issues/94).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W23** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #94 — [Warehouse] P6-01 · Archiving as a transaction — an `OPENING_BALANCE` movement at the cut-off before a single row moves.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Implementation order and dependencies

**Recommended wave:** 4 — Conditional scale/valuation extensions; scope decision first. This is a scheduling recommendation, not a requirement to finish every lower-wave issue before starting independent work.

### Before dependent implementation

- [W53 / #247](https://github.com/neetub1508/warehouse-issues/issues/247) — Measured scale and retention pressure establishing whether archive work is necessary.
- [W54 / #248](https://github.com/neetub1508/warehouse-issues/issues/248) — Recovery/retention requirements for archived data.

### Before final acceptance / closure

- No mandatory whole-issue completion dependency is identified. Meet this task’s acceptance and any applicable handoff/external prerequisites before closure.
- Preparatory analysis, fixtures and independent fixes can proceed while prerequisites are open. If a prerequisite is already satisfied in current code, link its commit/test evidence instead of waiting or rebuilding it.

### Setup, decisions and conditional dependencies

Current task can close with an explicit supported limit. Actual archiving is conditional on customer scope and proven reconstruction; no automatic enterprise expansion.

### Coordination and change control

- Earlier issues in “Related issues / existing implementation ownership” are ownership/history links, not automatic blockers. Preserve their accepted decisions and coordinate overlapping changes.
- A start dependency above can be a contract or test-environment handoff; it does not require closing the whole upstream issue. This avoids circular waits between implementation and acceptance tasks.
- Before implementation, confirm the applicable package, owner, schema/API/event contracts and required external fixtures. If a new blocker is discovered, add its issue link, exact deliverable, reason and applicability here and update the batch dependency index before dependent work proceeds.
- Record each prerequisite as satisfied with evidence, blocked with an owner, or not applicable with a scope reason. Do not silently bypass prerequisites or turn conditional features into universal blockers.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.
- This includes a scope or documentation decision. Closure can be a verified correction or supported-boundary decision; it must not silently expand the product.

## Acceptance

- [ ] Dependency review completed: all applicable prerequisites above have linked evidence or explicit scope disposition; newly discovered blockers are recorded in this task and the batch index.
- [ ] Any future archive preserves rebuild and audit checks; current deployments have a measured storage-growth plan.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Performance and topology**: Reference data size and concurrency; report load, imports, replica routing, DB locks and resource limits. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

<!-- warehouse-readiness-finding: 2026-10-01/W23 -->


## Reopened scope (WH-E2E review, 2026-11-03)

Found by the 2026-11-03 end-to-end review (code at classic HEAD 4843b1648d, plus the real-world check). This issue cannot close until each item below is met.

### W04-02 · Correct INSTALL archiving section to match the shipped archive run (minor, CLOSED-INCOMPLETE)

#### Why this matters

An installer or CA reading the install guide is told nothing can be archived, while the product ships an archive operation that moves ledger history behind an OPENING_BALANCE cut-off. They will either never use it or not know it exists when an auditor asks how old years are retained.

#### Scope

Rewrite the W23 paragraph to describe the archive run as built (who may run it, cut-off rule, what moves, statutory minimums still enforced, how to reconstruct), and drop the "not operational" claim; recheck §15/§16 cross-references.

#### Acceptance

- INSTALL names the archive endpoint/screen, its permission and its refusal when the cut-off is inside a statutory retention window.
- No sentence in INSTALL says archiving is deferred or not operational.
- Statutory minimums (CGST s.36/s.44, Rule 56, Companies Act s.128(5)) remain stated and match the seeded retention policies.

#### Evidence (classic HEAD 4843b1648d, 2026-11-03)

warehouse-base/INSTALL.md:1184-1188 "Archiving is not operational ... no job, screen or endpoint archives ... Deferred (v3) to P6-01 #94". Shipped: WhbLedgerArchiveController.java:26, WhbLedgerArchiveService.java:64, WhbLedgerArchiveWriter.java:37, WhbLedgerArchiveRequest/RunResponse DTOs.


#### Corrected INSTALL text (design-set correction, 2026-11-03, docs only)

Confirmed against classic HEAD `9579c5a095` (the shipped archive run: `WhbLedgerArchiveController`, `WhbLedgerArchiveService`, `WhbLedgerArchiveWriter`, `WhbLedgerArchiveRequest`, `WhbLedgerArchiveRunResponse`, `V501280`). The INSTALL guide is `warehouse-base/INSTALL.md` in classic, which a docs-only design task does not edit; the text below replaces it (see *Edits owed to classic INSTALL.md*). Facts, each from the source named:

- **Endpoint and who.** `POST /warehouse/ledger/archive-runs`, body `{companyId, cutOffAt}`; 201 with the completed run, or a field-level refusal naming why nothing moved. **No screen** (D16): an administrative operation. Permission `whb_stock_movements:archive`, granted to the `ADMIN` role only (`V501280`); `@PreAuthorize` on the controller method.
- **Switched off by default.** Setting `warehouse.archive.execution_mode` (Global Settings, Warehouse tab, group Base) is `DISABLED` by default and an unknown value reads as `DISABLED`; only `MANUAL` runs. While off the call is refused 409 `ARCHIVE_DISABLED` on field `executionMode`.
- **Cut-off rule.** `cutOffAt` is the first instant of a UTC month (`ARCHIVE_CUT_OFF_INVALID` otherwise, 422) and moves forward only: a cut-off at or before one already archived is refused. One advisory lock per company serialises runs.
- **Refusals before anything is written** (each names `cutOffAt`): `ARCHIVE_DISABLED`; `ARCHIVE_CUT_OFF_INVALID`; `NOTHING_TO_ARCHIVE` (422, no movement before C); the retention resolver's `NO_RETENTION_POLICY`, `LEGAL_HOLD` and `RETENTION_NOT_EXPIRED` (the ledger record class on the latest moved posting date, then every moved item or category that carries its own policy; the longest clock binds; a legal hold beats every clock; the seeded `INSTALL`/`DEFAULT` fallback counts as a policy); `ARCHIVE_PERIOD_NOT_CLOSED` (a stock period holding a moved movement is not CLOSED, or the run-date period is not OPEN); `ARCHIVE_OPEN_WORK` (a PENDING movement, a PENDING reversal or compensation of a moved movement, or an accounting hand-over not POSTED / DISCARDED / VOIDED before C); `ARCHIVE_OUTBOX_LAG` (an active subscriber's cursor is behind an event of a movement that would move); `ARCHIVE_SANDBOX_SITE`; `ARCHIVE_UNBALANCED` (L-1).
- **What the run does, in one transaction, in this order.** (1) writes the run row `RUNNING`; (2) writes one `ARCHIVE_OPENING_BALANCE` checkpoint per site of the company, dated C, into the open period of the run date, **before any row moves**; (3) moves every stock movement with `occurred_at < C` with its lines, attributes and approved costs to the `*_archive` tables (`whb_archive_runs` records the run); (4) proves each checkpoint equal, tuple for tuple, to what moved and records the run `COMPLETED` with its counts. Any failure rolls back every step. Snapshot, outbox and audit rows are **not** moved by this run.
- **Statutory minimums stay enforced.** The retention clocks above are the guard, so the minimums seeded by `V541116` (96 months books of account, 72 months GST from the record date) and the `IN-CA-*` / `IN-GST-*` clocks (CGST s.36 and s.44; Rule 56 sets no period and forbids erasure; Companies Act 2013 s.128(5), 8 financial years) refuse a cut-off inside their window as `RETENTION_NOT_EXPIRED`. The 120-month fallback applies where no specific clock does. **Archive moves, it never deletes**: no purge, `TRUNCATE`, `DETACH` or partition drop is supported and disposal at the end of retention is not built.
- **Irreversible; take a backup first.** There is no un-archive and `DatabaseBackupService` has no restore path, so a verified backup precedes setting `MANUAL`.
- **How to reconstruct and answer an auditor.** After a run, a full position rebuild from the live ledger reproduces every position (L-4) and `GET /stock/as-at` answers the same for any instant (FR-013); the opening-balance checkpoint, the `*_archive` rows and `whb_archive_runs` are the audit trail of where history went.

**Edits owed to classic `warehouse-base/INSTALL.md`** (docs only, to be scheduled by the driver; line numbers at HEAD `9579c5a095`):
1. `:1186-1190` replace "Archiving is not operational ... Deferred (v3) to P6-01 `#94`" with the paragraph above, keeping the retention-fallback and India-minimums bullets (`:1192-1224`) and changing "They govern nothing until P6-01 ships" (`:1196`) and "Nothing is enforced until P6-01 ships: no clock deletes or archives a row" (`:1222`) to say the clocks gate the archive run and still delete nothing.
2. `:1226-1241` "There is no supported archive" becomes "the only supported way to move ledger history is the archive run; never detach, drop or truncate by hand"; the "future archive must preserve" bullet becomes "the archive run preserves" (position-rebuild fold, ageing, as-at, Stock-to-GL zero first opening, audit hash chain, outbox cursor, posting floor, `requireArchivable`).
3. `:1624` (Supported history bound) and `:2147` (Deferred (v3) table row "Ledger archiving") drop "(v3)" / "Deferred" and describe the run and its default-off setting; the row stops listing snapshot, outbox and audit rows as moved.
4. Recheck the §15/§16 cross-references (`:1189`, `:1624`) and the P6-01 `#94` mentions at `:1196`, `:1222`, `:1239`, `:1240`.
