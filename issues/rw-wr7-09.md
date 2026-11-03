TITLE: [Warehouse] [Finding] Real-world WR7-09 · Anchor bonded and MOOWR record retention on the removal date
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-india
issue: 770
---
Part of #8 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #51, #64, #605 · Source: real-world gap check 2026-11-03, lane WR7 · Merges WR5-09

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Under MOOWR, capital goods and long-held inputs can stay in bond for years. The licensee must keep receipt and removal records for at least five years after the goods leave. A retention clock running from the record date can purge a receipt while its goods are still in bond, or soon after removal, which loses the duty trail the bond officer audits.

## Scope

Add a `CUSTOMS_BONDED` clock kind whose anchor is the latest removal (ex-bond clearance) of the quantity a record covers. While any bonded quantity from a Bill of Entry remains, the clock does not start. Effective period is a dated seed (5 years).

## Acceptance

- A BoE receipt from 2019 with 10 units still in bond is never eligible for purge
- After the last unit's removal on 1 Jun 2026, the receipt becomes eligible no earlier than 1 Jun 2031, or later if another clock is longer
- A legal hold still overrides

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

[MOOWR17]: digital records kept off-site, at least 5 years from the date of removal. Plan: #64 has clock kinds COMPANIES_ACT · GST · SHELF_LIFE only. grep `5 years|five years|60 months` in the bonded contract, #51, #64 and #605 = 0.

## Depends on

#64

## Merged finding WR5-09 · Add customs and hazardous-waste retention clocks anchored on removal

P4-09 knows Companies Act, GST and shelf-life clocks only. MOOWR reg. 17(2) keeps records for 5 years from the date the goods are removed from the warehouse, an anchor that is neither a financial year nor a GST period. Archiving a bonded lot's rows on the GST clock could destroy records customs can still demand.

**Scope:** A clock kind anchored on an event date (bond removal / ex-bond date) with seeded customs and MOOWR policies. Bonded rows take the longest applicable clock. Also seed a hazardous-waste records policy once WR5-04 (#745) exists; its period is UNVERIFIED and must not be seeded until an adviser confirms it.

**Acceptance:**
- A bonded lot cleared in March 2026 is not archivable before March 2031, even when the GST clock has expired
- The retention report shows which clock governs each row

**Evidence:** [TaxClue on MOOWR reg. 17](https://taxclue.in/blog/regulation-17-20-moowr-regulations-2019-records-audit-penalty-and-exemption/) (practitioner). P4-09 #64 clock kinds: COMPANIES_ACT · GST · SHELF_LIFE (issues/p4-09.md:40).
