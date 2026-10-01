TITLE: [Warehouse] [Finding] W08 · Cost inputs from receipt/return/transfer producers need end-to-end proof
LABELS: task,warehouse
issue: 202
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W08** · Module **`warehouse`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P1 (audit recommendation, not a programme phase). **Evidence class:** Code-supported / reported. **Applies to:** Foreign purchases, returns and transfers.

## Scope

### What happens / remaining gap

Current movement constructors use the shorter shape with absent currency/source-cost details. The issue reports foreign receipt refusal and missing return/transfer cost lineage. Some older adapter references are obsolete.

### Required work

Audit current native producers individually; retain sender/origin cost and normalize source currency exactly once.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#171](https://github.com/neetub1508/warehouse-issues/issues/171); [WhGoodsReceiptPostingService.java:849](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whgoodsreceipt/WhGoodsReceiptPostingService.java#L849); [WhTransferOrderPostingService.java:265](https://github.com/neetub1508/classic/blob/0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa/warehouse/backend/src/main/java/ai/warehouse/service/whtransferorder/WhTransferOrderPostingService.java#L265).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W08** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #171 — [Warehouse] P2-16 follow-up · Receipts, supplier returns, transfers and workshop returns give the costing engine what it needs.

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.

## Acceptance

- [ ] Foreign PO receipt, matched supplier return and transfer receipt preserve correct cost without double conversion or destination recosting.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Purchase and receipt**: Partial/over/foreign-currency receipt, duplicate submission, lot/serial/UOM and receipt evidence. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Relevant flow check — **Returns and RMA**: Expired RMA, matching origin, partial return, QC outcome, cost lineage and weighing behavior. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Relevant flow check — **Inter-site transfers**: Dispatch/in-transit/partial receipt/loss/reversal, narrow receiving permissions and source valuation preserved. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Relevant flow check — **Valuation and period close**: Old surviving stock, backdated events, FIFO/average, rounding, policy changes and period refusal. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #171</summary>

Follow-up from #115 (P2-16 costing engine) · Modules **`warehouse`**, **`warehouse-adapter-services`** · Migrations: none expected

## Scope
The engine values every posting, but some producers do not yet pass what it needs:
- **Goods receipt** passes no currency or exchange rate, so a foreign-currency PO receipt is refused once a supplier price is in another currency.
- **Return to vendor (P2-13)** should pass the origin receipt line so the supplier return relieves that receipt's own layer (RJ-010).
- **Transfer receipt (P2-02)** should pass the dispatch line so stock arrives at the sending site's cost (WH-SC-127).
- **Replenishment** `findUnitCosts` should read Σ `layer_value` / Σ `quantity_remaining`.
- **Workshop part return (P2-26)** sends the layer's source currency with a base-currency cost; it must send base currency, or a returned part bought in USD is refused.

## Acceptance
1. Receiving a USD purchase order values the stock in rupees at the rate on the receipt.
2. Returning a received batch to the supplier takes it out at exactly its receipt cost.
3. Returning an unused workshop part bought in USD is accepted.

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W08 -->
