# Functional Contract — Access scope: permissions, branch and site scope, owner grants, approval levels

> **What this is.** The functional truth for **who may see and do what** in the warehouse modules:
> `@PreAuthorize` on every method, the permission seed rules, the re-taken auditor and branch-admin
> decisions, the **three-mode view pattern** as a record-level guard, **warehouse-scoped access** derived
> from branch links, **owner grants** through one resolver, the reserved `logistics:*` namespace, support
> impersonation, menu seeding, and **ordered approval levels** (v2).
>
> **Status.** Derived 2026-10-23 (v0) for R30 `CP-FR-007` row 22 (`D-17` item a) from
> `WAREHOUSE-FUNCTIONAL-REQUIREMENTS.md` §6.23 and §6.28, checked against the built code and
> `BUILD-SPEC-SCREENS.md` §10.2. Not ratified. `FR-408` (maker ≠ checker) is owned by the workflow
> contracts that apply it and is cited, not restated.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | Every request: authenticate → `@PreAuthorize` → resolve site scope (branch-derived) ∩ owner scope ∩ warehouse grants → record-level `WHERE` → refuse `403` out of scope. Approval: document value → required levels → each level approved by a different user |
| **Module** | `warehouse-base` (scope services, owner resolver, base seeds) · `warehouse` (app resources, approval levels) · `platform` (`BranchScopeService`, impersonation) |
| **Domain baseline** | `D-3`, `D-14`, `RH-002`, `FR-408`; `BUILD-SPEC-SCREENS.md` §10.2 (the sole seed authority, `RA-007`) |
| **Owning tasks** | `issues/p0-15.md` (permissions, seeds, menus, role decisions) · `issues/p1-18.md` (warehouse-scoped access) · `issues/p0-06.md` (owner grants) · `issues/p0-13.md` (audit events, impersonation column) · `issues/p2-23.md` (approval levels, v2 increment) |
| **Primary tables** | platform `permissions`, `permission_dependencies`, `role_permissions`, `menus`; `whb_owner_grants` (`V500044`); `whb_audit_events` (`V501011`, `on_behalf_of_actor_id`); `wh_approval_levels` (`V510222`, v2) |
| **Services** | `BranchScopeService` (platform) · `WhbWarehouseScopeService` · `WhbOwnerScopeResolver` |
| **Routes** | WS-020 Owner Grants · WS-238 Warehouse Grants (`/warehouse/masters/warehouse-grants`) · WS-063 Warehouse Audit Events · WS-241 Approval Levels; every warehouse management route |
| **Contract version** | `v0 — 2026-10-23` |

### Acceptance checks

| # | Expects | Delivered by |
|---|---|---|
| A1 | A storekeeper at branch A cannot read or adjust branch B's stock; out of scope is `403`, never an empty grid (`WH-SC-242`) | `ACS-GRD-03`, `-04` |
| A2 | Owner segregation holds on grid, export and statistics (`WH-SC-140`) | `ACS-GRD-05` |
| A3 | The auditor reads everything and writes nothing (`WH-SC-245`) | `ACS-T2-02` |

---

## 1. Rules

### 1.1 Guards

| ID | Predicate | Refusal: HTTP · code · field | Backstop | Source |
|---|---|---|---|---|
| ACS-GRD-01 | Every controller method carries `@PreAuthorize` in `resource:action` form; resources are prefixed for this product (`whb_`, `wh_`, `wh3_`, `whin_`, `warehouse:`) and **never** named after the deleted prior module | `403` | architecture test (controller enumeration) | FR-401 |
| ACS-GRD-02 | Every management resource is seeded with the tier pair `<resource>:view:all` / `<resource>:view:branch` beside `:view`; the pattern is platform's `BranchScopeService`, never a re-implemented branch resolution | — (seed) | `V501000`, `V511000` | FR-404 |
| ACS-GRD-03 | Every management query (grid, export, statistics, dropdown, detail) carries the site predicate in its `WHERE` clause: `allowedWarehouseIds` resolved **once per request** from the caller's branches through any current link whose role grants visibility — `null` = view-all, empty set = no access, short-circuited before SQL, **including a non-empty branch set that resolves to no site** | `403 WAREHOUSE_SITE_NOT_PERMITTED` (a named site); no access is answered before any SQL runs | `WhbWarehouseScopeContractTest` | FR-404, FR-405 |
| ACS-GRD-04 | A two-ended record (transfer, inter-site document) is in scope if **either** site is; composition is owner ∩ branch-derived sites ∩ any warehouse grant — it narrows, never widens | `403` as above | — | FR-405 |
| ACS-GRD-04a | **The warehouse-grant axis.** A caller whose grantee set (user, roles, groups) has **no** `whb_warehouse_grants` row is **unscoped on this axis, not blind** — they keep every site their branches reach. A caller with **any** grant row, whatever its dates, is on the axis: their sites are the grants **current now** intersected with the branch tier, so a grant narrows and never widens, and a user whose only grant has **expired** loses access to every site it named (`WhbWarehouseScopeService.java:153-165`, `narrowByWarehouseGrants`) | `403` as above | — | FR-405 |
| ACS-GRD-05 | Owner grants are enforced by the single server-side resolver; every repository method touching an owner-scoped table takes an owner-set parameter, and each grid's export path and statistics map applies it | `403 OWNER_NOT_PERMITTED` | `WhbOwnerScopeContractTest` fails the build otherwise | FR-406 |
| ACS-GRD-07 | Cost and value are suppressed **by actor**: every endpoint returning `unit_cost`, `total_value`, `standard_cost` or a cost layer — exports included — omits them from the response DTO unless the caller holds `warehouse:cost:view`; applied in the mapper and asserted per endpoint, **never** a frontend column hide (`role_field_configs` is client-side only) | — (the fields are absent from the payload) | per-endpoint tests | FR-450 |
| ACS-GRD-06 | A document whose value falls in a band with current approval levels (v2) needs every level of its type whose `min_value` ≤ its value, in `sequence_no` order, each by a holder of that level's `required_permission`; **no user approves one document twice**; with no rows for a type, the v1 single-step approval stands | `403` naming the level's permission; `403` on a second approval by the same user | `uk(company_id, document_type_code, sequence_no)` among current rows | FR-466 — §10 row 1 |

### 1.2 Unreachable

| ID | Must never happen | What makes it unreachable | Source |
|---|---|---|---|
| ACS-UNR-01 | A warehouse migration that **creates** `permission_dependencies` (it is a platform table; rows are inserted) | migration review; no `CREATE TABLE permission_dependencies` in any warehouse module | FR-402 |
| ACS-UNR-02 | The prior module's one-shot auditor / branch-admin exclusions relied on. They are re-taken in `V501000` / `V511000`: AUDITOR holds every `:view` and `:view:all`, no `:export`, no write and no verb; Branch Admin holds `:view:branch` and never `:view:all` | seed migrations (`BUILD-SPEC-SCREENS.md` §10.2 `FR-403` block) | FR-403 |
| ACS-UNR-03 | Branch scope implemented as a UI filter or a menu filter only | `ACS-GRD-03` | FR-404, FR-405 |
| ACS-UNR-04 | An unlinked site visible to a branch-scoped user (accessories' *unlinked is shared* arm, refused by name) | `WhbWarehouseScopeService` | FR-405 |
| ACS-UNR-05 | A `logistics:*` permission invented in v2 and retro-granted by hand: the namespace and its dependency rows are reserved and seeded in v1 | `V501000` (`logistics:epod:*`, `logistics:freight:*`, `logistics:trips:*`) | FR-407 |
| ACS-UNR-06 | A menu insert guarded by `ON CONFLICT` alone; every warehouse menu insert is `WHERE NOT EXISTS (… name, parent_id, menu_level …)` and seeds translations for en, fr and hi | migration review (all 134 warehouse menu-inserting migrations carry `NOT EXISTS`) | FR-410 |
| ACS-UNR-07 | A support session's actions recorded as the customer's own: the audit event carries `on_behalf_of_actor_id` from the first audit migration | `whb_audit_events.on_behalf_of_actor_id` (`V501011`) | FR-409 |
| ACS-UNR-08 | A workflow designer for approvals (FRD §10 refusal); approval levels are a bounded table | scope rule | FR-466 |

## 2. T2 — Action × role

| ID | Action | Permission | Extra | Source |
|---|---|---|---|---|
| ACS-T2-01 | Read any management grid | `<resource>:view` + `:view:all` or `:view:branch` | site predicate `ACS-GRD-03`; owner predicate `ACS-GRD-05` | FR-404, FR-405 |
| ACS-T2-02 | Any write as AUDITOR | — | refused `403` everywhere, including the ledger | FR-403 |
| ACS-T2-03 | Impersonate a customer user for support | platform support-access session (`SupportImpersonationFilter`) | with the customer's consent, time-boxed, audited with `on_behalf_of_actor_id` | FR-409 |
| ACS-T2-04 | Maintain approval levels (v2) | WS-241 resource permissions | Department-shaped master | FR-466 |

## 3. T3 — Time-driven rules

| ID | Rule | Clock | Changes | Source |
|---|---|---|---|---|
| ACS-T3-01 | Site access reads **today's** links (classification reads `occurred_at`, `facility-branch-link.contract.md` `FBL-T3-01`) | now | the resolved `allowedWarehouseIds` | FR-405 |
| ACS-T3-02 | A support impersonation session ends at its time box | session expiry | further requests run as the support user only | FR-409 |
| ACS-T3-03 | Approval levels are effective-dated `[effective_from, effective_to)`; a document reads the levels current at its approval request | document approval time | which levels apply | FR-466 |

## 4. T4 — Cross-entity effects

| ID | When | Then | Enforced in | Source |
|---|---|---|---|---|
| ACS-T4-01 | A permission is seeded that requires another (`edit` requires `view`) | a `permission_dependencies` row (`permission_id`, `dependent_permission_id`) is inserted | seed migration | FR-402 |
| ACS-T4-02 | One level of a multi-level approval is given (v2) | a `whb_audit_events` row names the document, the level's `sequence_no` and the approver; the document stays in its approval state until the last level; `approved_by` holds the last approver | approve actions (PO, adjustment, count variance, transfer) | FR-466 |

## 5. T5 — Screen contract

| ID | Screen | Contract | Source |
|---|---|---|---|
| ACS-T5-01 | every warehouse grid | the branch / site filter offers only in-scope sites (`useUserBranches` → sites); a URL naming another site answers `403`, shown as a permission message, not an empty grid | FR-404, FR-405 |
| ACS-T5-02 | WS-063 Warehouse Audit Events | shows the on-behalf-of actor beside the actor | FR-409 |
| ACS-T5-03 | WS-241 Approval Levels (v2) | grid `companyName`, `documentTypeCode`, `sequenceNo`, `minValue`, `requiredPermission`, effective dates; company and document-type filters | FR-466 |
| ACS-T5-04 | every warehouse menu | appears only to holders of its `required_permission_prefix`; labels in en, fr, hi | FR-410 |
| ACS-T5-05 | WS-238 Warehouse Grants | Customer-reference grid `whb_warehouse_grants`, filter scope `WAREHOUSE_WAREHOUSE_GRANT`, `whb_warehouse_grants:*`; grantee, site and effective dates; the page states that a user with no grant row keeps branch-derived access (`ACS-GRD-04a`) | FR-405 |

## 6. Out of scope

`FR-408` maker ≠ checker (each workflow contract); 3PL portal grants (`FR-284`, `FR-300`); device sessions.

## 7. Amendments

| Date | Change |
|---|---|
| 2026-10-23 | v0 derived for R30 `CP-FR-007` row 22 |
| 2026-10-23 | R31 `F-CA-016`: `ACS-GRD-04a` (no grant row = unscoped; any row = current grants ∩ branch tier; an expired-only grant removes access) and WS-238 (`ACS-T5-05`, §0 routes) added |

## 8. Invariants and scenarios

`D-14`, `RH-002`, `FR-408`. Scenarios `WH-SC-140`, `-241`, `-242`, `-245`, `-246`, `-247`, `-299`, `-323`.

## 9. Open rows

None — every rule above is stated by the FRD or `BUILD-SPEC-SCREENS.md` §10.2.

## 10. Code divergences (for the build to fix)

| # | File:line | FR | What differs |
|---|---|---|---|
| 1 | `warehouse/backend/.../db/migration/` (no `V510222`) | FR-466 | `wh_approval_levels` and the multi-level approve path are not built (v2 increment of `P2-23`) |
