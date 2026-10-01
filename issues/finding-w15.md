TITLE: [Warehouse] [Finding] W15 · Emergency replenishment issue is partly stale
LABELS: task,warehouse
issue: 209
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W15** · Module **`warehouse`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P2 (audit recommendation, not a programme phase). **Evidence class:** Documentation / verification. **Applies to:** Picking and pick-face replenishment.

## Scope

### What happens / remaining gap

Current short-pick code raises or escalates replenishment through the task path. The old issue wording saying nothing is built no longer describes all current behavior.

### Required work

Reconcile the obsolete BIN_TO_BIN acceptance with current task flow and run the full short-pick recovery.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#177](https://github.com/neetub1508/warehouse-issues/issues/177); [WhPickTaskWriter.java:520](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whpicktask/WhPickTaskWriter.java#L520); [WhReplenishmentTaskGenerator.java:257](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whreplenishmenttask/WhReplenishmentTaskGenerator.java#L257).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W15** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #177 — [Warehouse] P2-02 follow-up · RA-006 — P2-09's emergency replenish is specified as a BIN_TO_BIN transfer, which V511246 makes unbuildable.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.
- This includes a scope or documentation decision. Closure can be a verified correction or supported-boundary decision; it must not silently expand the product.

## Acceptance

- [ ] Short pick → one replenishment task → physical move → resumed demand works without duplicate task or unsupported transfer type.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Pick and operational replenishment**: Short pick raises task; source shortage, priority, partial workflow and eligible operator are explicit. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #177</summary>

Raised 2026-09-20 from **P2-02 (#24)**, round-2 functional re-verify. `RA-006`.

**P2-09's emergency replenish is specified as something that can no longer be built, and P2-09 is CLOSED and ticked over it.**

`docs/GAP-REGISTER-R3.md:219` and `issues/p2-09.md:68` and `:161` specify the emergency replenish as creating a `wh_transfer_orders` row of **type `BIN_TO_BIN`**. `V511246` narrows the `wh_transfer_orders.transfer_type` `CHECK` and removes `BIN_TO_BIN` from it (P2-02 driver ruling 2026-09-20, `F11`: a bin-to-bin move is an ordinary two-line movement with no document, so it is not a transfer type). That acceptance row is therefore **unbuildable as written**.

**Nothing breaks at runtime.** It was never built: `EMERGENCY_REPLENISH` appears only as an admitted value of `wh_pick_tasks.short_pick_action` (`V510041:101`), and **nothing anywhere creates a `BIN_TO_BIN` transfer**. `V511246` makes a **pre-existing unbuilt acceptance row permanently unbuildable** — it does not regress working behaviour.

**The choice** (both stated; neither ruled here):
1. **Reopen `P2-09`** with a different mechanism for emergency replenish — a document-less two-line movement inside one site, which is the same shape `FR-150` / `WH-SC-285` needs and which has no owner either.
2. **Withdraw emergency replenish from `FR-185`'s v1 offer** — `RA-006`'s own stated alternative — and strike the acceptance row rather than leaving it ticked against a mechanism that cannot exist.

Either way the ticked row on a CLOSED task is the thing to correct: as it stands `P2-09` reads as delivered against a `BIN_TO_BIN` transfer that the schema now refuses.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W15 -->
