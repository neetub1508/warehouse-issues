TITLE: [Warehouse] [Finding] W14 · Generic bin movement ownership remains unresolved
LABELS: task,warehouse,warehouse-base
issue: 208
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W14** · Module **`warehouse-base`, `warehouse`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P1 (audit recommendation, not a programme phase). **Evidence class:** Reported. **Applies to:** Warehouses needing ad hoc internal moves.

## Scope

### What happens / remaining gap

Removal of BIN_TO_BIN from transfer documents leaves a reported unowned generic internal movement workflow. Existing task-driven movements do not prove a general operator path.

### Required work

Identify the supported movement action and task ownership; do not add an invalid transfer type back by default.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#176](https://github.com/neetub1508/warehouse-issues/issues/176).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W14** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #176 — [Warehouse] P2-02 follow-up · FR-150 / WH-SC-285 bin-to-bin movement has no owning task — the deferral, not a closure.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.

## Acceptance

- [ ] An authorized user moves stock between bins with scope, lot/serial, capacity and ledger evidence, using a documented UI/API.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Locations and ad hoc moves**: Scoped bin movement with lot/serial/LPN identity and balanced ledger; reversal and capacity refusal. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #176</summary>

Raised 2026-09-20 from **P2-02 (#24)**, round-2 functional re-verify.

`FR-150` / `WH-SC-285` — the **bin-to-bin move** — has **no owning task anywhere in the design set**, and `P2-02` claims it as closed.

**How it got here.** The P2-02 driver ruling of 2026-09-20 (`F11`) removed `BIN_TO_BIN` from `WhTransferOrder.TRANSFER_TYPES` — a bin-to-bin move is an ordinary two-line movement with **no document**, so it is not a transfer type and `V511246` narrows the `CHECK` accordingly. `WS-090` therefore posts nothing for it: it left the vocabulary endpoint, the Add modal and the grid filter with it.

**What is left unowned.** `IMPLEMENTATION-PLAN.md:472` allocates `FR-147…FR-150` to `P2-02` and **no other `issues/p*.md` claims `FR-150`**. With the move out of `P2-02` the requirement and `WH-SC-285` have no owner at all. `issues/p2-02.md:296` already records this in the acceptance list (*"Owner of `FR-150`'s movement: none"*), but the same file went on to list `FR-150` under **Requirements closed** (`:226`) and under **Closes** (`:244`, `T-008 T-015`) — a false closure.

**What this issue owns.** The deferral itself: `FR-150` / `WH-SC-285` is **deferred, not delivered**, and this issue is the record of that until a task builds the move. `p2-02.md:226` and `:244` now point here instead of claiming closure.

**What the move needs when it is built** (nothing is built today): a two-line movement within one site, identical owner and stock status on both lines, no document, no ladder — i.e. a screen or action against the existing ledger writer, not a `wh_transfer_orders` row.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W14 -->
