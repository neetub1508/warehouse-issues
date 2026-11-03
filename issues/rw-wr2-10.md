TITLE: [Warehouse] [Finding] Real-world WR2-10 · Report stores SoD conflicts and run periodic access reviews
LABELS: task,warehouse,gap-real-world,phase-p2
issue: 735
---
Part of #5 · Module **`warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **MISSING-TASK** · Related: #146, #47 · Source: real-world gap check 2026-11-03, lane WR2

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

The runtime rule stops one person approving their own document, but a role that carries item-master edit + adjustment create + count approve, or a user holding storekeeper and stores-approver roles together, is a standing SoD conflict the internal and statutory auditor test under internal financial controls. There is no report of such combinations and no periodic sign-off that stores users still need their access, so the auditor's ITGC work starts from a raw permission dump.

## Scope

Seeded SoD rule set for warehouse permissions (e.g. wh_counts:edit vs :approve, adjustments create vs approve, item master edit vs adjustment approve, receipt post vs supplier-return approve), editable; report of users/roles violating a rule per site; quarterly access-review campaign listing each warehouse user's permissions for their manager to keep/revoke, with sign-off audit.

## Acceptance

- A role granting both wh_counts:edit and wh_counts:approve appears on the conflict report with every user holding it.
- An access-review campaign cannot close while any line is unanswered; revocations are applied and logged.
- Report export includes rule, user, role, site.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

ICAI IFC guidance names segregation of duties among control-environment objectives (secondary): https://assets.kpmg.com/content/dam/kpmg/pdf/2015/09/ICAI-releases-revised-guidance-on-Internal-Financial-Controls-Over-Financial-Reporting.pdf ; periodic access reviews as ITGC practice (P): https://www.schellman.com/blog/soc-examinations/simple-system-access-periodic-reviews . grep "access review|recertif|SoD conflict" design set = 0; platform `GroupPermissionRepository.findConflictingPermissions` is grant/deny conflict, not SoD.

## Global setting

`WAREHOUSE_ACCESS_REVIEW_FREQUENCY` default=QUARTERLY alternatives=MONTHLY,HALF_YEARLY,YEARLY

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#146
