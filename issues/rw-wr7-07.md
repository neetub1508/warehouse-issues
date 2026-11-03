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

## Design-set correction (done 2026-11-03, docs only)

**ITC-04, law in force today.** Rule 45(3) CGST Rules as amended by Notification No. 35/2021-Central Tax (24 Sep 2021, from 1 Oct 2021): the specified period is six months (1 April and 1 October starts) when the principal's aggregate turnover in the preceding financial year exceeds Rs 5 crore, otherwise the financial year; the form is due by the 25th of the month after the period (25 Oct and 25 Apr for half-yearly filers, 25 Apr for annual filers; FY 2026-27: 25 Oct 2026 and 25 Apr 2027). No quarterly ITC-04 exists. Sources: [taxclue, ITC-04 specified period](https://taxclue.in/blog/itc-04-specified-period-and-the-five-crore-split), [cleartax](https://cleartax.in/s/gst-inputcredit-job), [taxscan](https://www.taxscan.in/?p=394426). The notification text on the CBIC site was not reachable from this run; confirm the figures against the notification at build time.

**CGST Act s.143 citations.** The moulds, dies, jigs, fixtures and tools exclusion is in the words of s.143(1)(a) and (1)(b) (and again in s.143(4)); the unreturned-goods deemed supply is s.143(3) for inputs (1 year) and s.143(4) for capital goods (3 years); there is no s.143(2) proviso for it. The ITC exclusion is s.19(7). Sources: [knowyourgst s.143](https://www.knowyourgst.com/gstlaw/cgst-act/143-job-work-procedure-143/), [taxguru job-work analysis](https://taxguru.in/goods-and-service-tax/job-work-gst-detailed-analysis-part-1.html) (unofficial; the CBIC page was unreachable).

**Corrected in:** `docs/contracts/mfg-subcontracting.contract.md` (moulds row), `docs/SCENARIO-CATALOGUE.md` (WH-SC-239), `issues/06-EPIC-p4.md` (scenario line), `issues/p4-02.md` (periodicity row CONFIRMED, WH-SC-239 line), `docs/INDIA-LOCALISATION-PACK.md` (periodicity row CONFIRMED, s.143 note). No design-set text now calls ITC-04 quarterly or cites s.143(2) for the carve-out.

**Code owed (build, not done here)**
1. ITC-04 run (`p4-02`): the period picker offers H1/H2 (Apr-Sep, Oct-Mar) when the AATO setting is above Rs 5 crore, otherwise only financial years; due date = the 25th of the month after the period.
2. Test: an ITC-04 run for a registration at or below Rs 5 crore offers only FY periods (acceptance 3); a scenario asserting the half-yearly and annual periods and due dates is authored at build.
3. Check classic job-work text/comments for "quarter" or `s.143(2)` (`warehouse-india` job-work contract and seeds) and correct in the same pass.

## Merged finding WR1-09 · Correct "ITC-04 for the quarter" to half-yearly / annual in the P4 epic

ITC-04 has not been quarterly since October 2021. A scenario written "for the quarter" will build or test the wrong period and mis-state the due dates.

**Scope:** Fix the wording in the epic. Mark p4-02.md:53-54 and INDIA-LOCALISATION-PACK.md:57-58 "RE-VERIFY" rows as CONFIRMED (Nov 2026).

**Acceptance:**
- No design-set text says ITC-04 is quarterly.
- The ITC-04 period picker offers only H1/H2 or FY according to the AATO setting.

**Evidence:** Half-yearly when AATO > ₹5 cr (due 25 Oct / 25 Apr), annual otherwise (due 25 Apr) ([cleartax](https://cleartax.in/s/gst-inputcredit-job), [taxscan](https://www.taxscan.in/?p=394426)). Plan: `issues/06-EPIC-p4.md:76` "files ITC-04 for the quarter". p4-02.md:54 and mfg-subcontracting.contract.md:139 are already right.
