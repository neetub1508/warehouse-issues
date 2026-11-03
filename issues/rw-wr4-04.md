TITLE: [Warehouse] [Finding] Real-world WR4-04 · Record a consignment detained in transit and its release
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-india
issue: 741
---
Part of #8 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #147, #82, #73 · Source: real-world gap check 2026-11-03, lane WR4

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

A truck stopped by a GST officer is held under s.129: the officer records statements and inspection, then issues a detention order and a demand. The penalty is 200% of tax. The goods are released only after payment or a bond. Meanwhile the EWB may expire and must be extended, the customer delivery is late, and the payment/appeal is an accounting matter. With no state for this, the shipment reads "dispatched" for weeks, no one tracks the response window, and the penalty is not linked to the consignment for appeal. The 57th Council (8 Oct 2026) has recommended limiting interception, but s.129 is unchanged until the Act is amended.

## Scope

A `TRANSIT_HOLD` record on the shipment/EWB with authority, place, date, document references (inspection, detention order, demand), the amount demanded, a link to the payment in accounting, release date and attachments. The shipment shows `HELD_IN_TRANSIT`. An open hold prompts an EWB extension with reason `LAW_AND_ORDER`/`OTHER`. A register lists open holds by age.

## Acceptance

- Recording a detention moves the shipment to held and appears on the open-holds register
- Release returns it to dispatched; delivery cannot be confirmed while a hold is open
- An EWB expiring during an open hold raises the extension prompt
- The hold, its documents and the demand reference are kept with the EWB history

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

[GC57] (s.129 penalty 200% after Finance Act 2022; recommendation not yet enacted). The plan has only a narrative line (04-EPIC-p2in.md:14 "A truck stopped without one is detained and penalised"). Grep `MOV-|detained|s.129` in issues = no task.

## Depends on

#147
