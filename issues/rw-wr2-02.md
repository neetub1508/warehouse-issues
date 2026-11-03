TITLE: [Warehouse] [Finding] Real-world WR2-02 · Keep the location custodian off counting their own bins
LABELS: task,warehouse,gap-real-world,phase-p2
issue: 730
---
Part of #5 · Module **`warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **MISSING-TASK** · Related: #37, #146, #54 · Source: real-world gap check 2026-11-03, lane WR2

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

The storekeeper who holds custody of a bin is the person with a motive to hide a shortage. Standard stock-taking practice has the count done by someone other than the custodian (custodian may attend). The plan stops the counter approving their own count, but lets the custodian count their own bins, which an internal auditor will call a design weakness of the count procedure that CARO 3(ii)(a) asks about.

## Scope

At count-task assignment and at count submission, compare the counter with the location's CUSTODIAN at the count's freeze instant; apply the setting; record "custodian present" (user) on the count line as an optional witness field; show the conflict in the count approval screen.

## Acceptance

- With BLOCK, assigning a zone whose bins have custodian U to U returns 422 naming the bins.
- With WARN, assignment succeeds and the approval screen shows a custodian-counted flag per line.
- With OFF, behaviour is today's.
- The witness field is stored and appears in the count export.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

California SAM physical inventories: count by a designated employee "preferably not the storekeeper or custodian": https://www.dgs.ca.gov/Resources/SAM/TOC/10800/10860/10860-Feb-1965 ; tags checked by persons independent of counters (P): https://www.utoledo.edu/offices/internalaudit/pdfs/5-8manageinventories.pdf ; custodian-present practice: https://aiims.edu/images/pdf/notice/msu-28-8-24.pdf . Code: custody is `whb_location_user_assignments` (V500013__...sql:258-284, CUSTODIAN role) but `grep -rl CUSTODIAN|LocationUserAssignment` in warehouse count services = 0; p2-04.md enforces only approver != counter.

## Global setting

`WAREHOUSE_COUNT_CUSTODIAN_RULE` default=WARN alternatives=BLOCK,OFF

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#37
