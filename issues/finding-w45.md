TITLE: [Warehouse] [Finding] W45 · Regulated-item setup refuses contradictions too late
LABELS: task,warehouse,warehouse-base
issue: 239
---
Part of #1 · Audit **warehouse-only readiness, 2026-10-01** · Finding **W45** · Module **`warehouse-base`, `warehouse`** · Migrations **none allocated by this audit; reserve only if implementation requires one** · Screens **existing affected surfaces identified below; no new screen IDs allocated**

**Priority:** P1 (audit recommendation, not a programme phase). **Evidence class:** Reported conditional gap. **Applies to:** Only enabled regulated profiles.

## Scope

### What happens / remaining gap

The issue records non-lot-controlled regulated items being accepted at setup and refused at dispatch. Other requested jurisdiction fields remain adviser-gated.

### Required work

Validate the enabled profile’s contradictions at item save; confirm profile-specific requirements before implementation.

### Boundary and ownership

This task tracks one finding from the warehouse-only audit. Complete the work or evidence needed for the affected existing workflow. Planning, forecasting, optimization and competitor feature work are excluded. Optional-module work applies only to the stated scope. Existing web-only/online-only decisions and removed-adapter decisions remain authoritative. An intentional limit is closed by enforcing/documenting the supported boundary unless a later explicit scope decision authorizes expansion.

## Evidence and affected code

[#188](https://github.com/neetub1508/warehouse-issues/issues/188).

Audit code baseline: `neetub1508/classic@0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`. Design baseline: `neetub1508/warehouse-issues@7b96725eb5850748cd94b2a784466cb16728a55d`.

Recheck the affected path at the implementation commit. “Reported” and “verification gap” do not mean a fresh runtime failure; “code-supported” does not mean a live reproduction. Preserve that distinction in the resolution.

## Requirements closed

The existing warehouse behavior described in Scope and Acceptance. This audit does not allocate new FR identifiers or claim any requirement already closed. Reuse the adopted requirements in related task sources; record exact applicable IDs when implementing instead of inventing them.

## Scenarios closed

No scenario is newly marked passed by creating this task. Execute the finding-specific acceptance below and affected refusal/retry paths. Record the current commit, supported module configuration, fixture, role, steps and actual results; reuse catalogue scenarios where they apply.

## Closes

Audit finding **W45** once its acceptance is met and evidence is linked. This issue does not automatically close or reopen earlier tasks.

### Related issues / existing implementation ownership

- #188 — [Warehouse] P4-13 follow-up · Refuse an unlotted regulated item at the item screen; Schedule H1 prescriber/patient fields (adviser-gated).

These links preserve earlier ownership/history. Coordinate overlapping implementation in one change and link both issues; do not build a second competing implementation. Closed duplicates remain closed.

## Traps

- Follow `docs/DECISIONS.md` and its adopted settings amendment; older task wording is historical where superseded.
- Preserve stock/valuation lineage, tenant/site/owner scope and existing service ownership on affected paths.
- Do not interpret a missing runtime test as proof that the feature is missing. Verify before replacing working code.

## Acceptance

- [ ] Activation/setup catches invalid item configuration before goods reach dispatch; disabled profiles make no compliance promise.
- [ ] Verify current behavior against the cited evidence; record which concern is reproduced, already resolved, accepted by an existing decision, or still awaiting applicable integration evidence.
- [ ] Relevant flow check — **Site/owner/item setup**: Create masters and required associations through UI; effective dates, invalid setups and per-site sourcing behave consistently. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Relevant flow check — **India optional workflows**: Provider sandbox, document issuance/print history, concurrent cancel/dispatch, ambiguous response and dates. Limit this task to its finding; link adjacent tasks for the rest.
- [ ] Run the targeted automated/runtime checks needed for this change, plus required module gates; retain actual results. A skipped integration test or code read is not a runtime pass.
- [ ] Update affected contract/help/runbook text and the related issue evidence so the supported behavior agrees across code and documentation.
- [ ] List remaining conditional dependencies explicitly; do not close an enabled workflow with unverified stock integrity, access control or external-state recovery.

## Earlier report detail (reference, verify against current code)

The following preserves the original observations/reproduction details. It is historical context; the Scope and adopted decisions above govern implementation.

<details>
<summary>Source issue #188</summary>

Follow-up from #88 (P4-13 regulated-goods licence pack), W3 gate finding F6 · Modules **`warehouse-base`** (a new item-validation port) + **`warehouse-india`** (its implementation) · Migrations: possibly a `V540xxx` correction-reserve migration for the H1 fields, only once an adviser confirms them

## Scope
Two acceptance items of #88 were merged unbuilt and stay unchecked there:

1. **Refuse the contradiction at the item screen, not at the dock.** The spec's trap says an item marked with a `REGULATED_LICENCE_TYPE` and `lot_control_mode = NONE` must be refused when the item is saved. Today it is refused only at despatch (`REGULATED_ITEM_NOT_LOT_CONTROLLED` in `WhinRegulatedGoodsDispatchGuard`), and that check is inert while `warehouse.regulated_profile` is `NONE`. So items can be set up this way now, and the first despatch after a profile is activated refuses every one of them.
   - Add a warehouse-base port, e.g. `WhbItemValidationContributor`, that the item save and the item-attribute save call (collected through `ObjectProvider`, the `WhShipmentDispatchGuard` pattern). The core never names a jurisdiction.
   - warehouse-india implements it: a regulated item with no lot control is refused field-level on `lotControlMode`, whatever the profile.
   - Keep the despatch-time check as the backstop.
2. **Schedule H1 prescriber and patient fields.** Spec §5 says the H1 register carries "the prescriber and patient fields the rule names". `whin_schedule_h1_register` (V540183) has neither. The field list stays **blocked** until a regulatory adviser confirms it in writing (the same gate as the licence-type seed, `X-067`). Only then add the columns in the `V540xxx` correction reserve and the capture point.

## Acceptance
1. Saving an item, or its `REGULATED_LICENCE_TYPE` attribute, with `lot_control_mode = NONE` is refused with a field-level error that names the item. This holds under every regulated profile, including `NONE`.
2. An install without warehouse-india saves items exactly as before.
3. The H1 register gains the adviser-confirmed prescriber and patient fields, and a rebuild of a closed month still states identical rows. The adviser's written confirmation is linked in the PR. **Blocked** until that confirmation exists.
4. #88's two acceptance items (the item-screen refusal, and the adviser confirmation for the H1 field list) are ticked only when this issue closes.

NO MOBILE (FR-218).

</details>

<!-- warehouse-readiness-finding: 2026-10-01/W45 -->
