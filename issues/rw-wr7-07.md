TITLE: [Warehouse] [Finding] Real-world WR7-07 · Correct job-work citations and the stale quarterly ITC-04 wording
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-india
issue: 768
---
Part of #8 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **PLANNED-WRONG** · Related: #22, #601 · Source: real-world gap check 2026-11-03, lane WR7 · Merges WR1-09

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

A reviewer or auditor who checks the cited section finds nothing at s.143(2), and a scenario asserting a "quarterly" ITC-04 trains testers on a frequency abolished in 2021.

## Scope

Fix the two texts and add a scenario asserting the half-yearly period for AATO > ₹5 cr and the annual period otherwise, with due date the 25th of the following month.

## Acceptance

- No design-set text cites s.143(2) for the moulds carve-out
- WH-SC-239 names a half-yearly or annual period
- An ITC-04 run for a ≤₹5 cr registration offers only FY periods

## Evidence (classic HEAD 4843b1648d, 2026-11-03)


- [S143]: the moulds, dies, jigs, fixtures and tools carve-out is in s.143(1)(b), with deemed supply in s.143(4).
- [R45]: ITC-04 has been half-yearly or annual since Notf 35/2021-CT (1 Oct 2021).
- Plan: `docs/contracts/mfg-subcontracting.contract.md:135` "(s.143(2) proviso)"; #22 WH-SC-239 "filed for the quarter".

## Merged finding WR1-09 · Correct "ITC-04 for the quarter" to half-yearly / annual in the P4 epic

ITC-04 has not been quarterly since October 2021. A scenario written "for the quarter" will build or test the wrong period and mis-state the due dates.

**Scope:** Fix the wording in the epic. Mark p4-02.md:53-54 and INDIA-LOCALISATION-PACK.md:57-58 "RE-VERIFY" rows as CONFIRMED (Nov 2026).

**Acceptance:**
- No design-set text says ITC-04 is quarterly.
- The ITC-04 period picker offers only H1/H2 or FY according to the AATO setting.

**Evidence:** Half-yearly when AATO > ₹5 cr (due 25 Oct / 25 Apr), annual otherwise (due 25 Apr) ([cleartax](https://cleartax.in/s/gst-inputcredit-job), [taxscan](https://www.taxscan.in/?p=394426)). Plan: `issues/06-EPIC-p4.md:76` "files ITC-04 for the quarter". p4-02.md:54 and mfg-subcontracting.contract.md:139 are already right.
