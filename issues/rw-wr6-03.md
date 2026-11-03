TITLE: [Warehouse] [Finding] Real-world WR6-03 · Track client GSTIN status and PPoB/APOB type instead of an expiry date
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-3pl
issue: 753
---
Part of #8 · Module **`warehouse-3pl`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **PLANNED-WRONG** · Related: #68, #508 · Source: real-world gap check 2026-11-03, lane WR6

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Regular GST registrations do not lapse on a date. The risks are cancellation, suspension, and the client deleting the warehouse from its registration. An alarm keyed to `effective_to` misses all three, and staff will leave the field blank. A client may also hold the warehouse as its principal place: Rule 14B as recommended, or any small client. The APOB-only flag then raises a false alarm (P4-10 F4: "only an APOB successor silences").

## Scope

Replace `is_additional_place` with `place_type` (PPOB, APOB). Add `gstin_status` (ACTIVE, SUSPENDED, CANCELLED, UNVERIFIED) with a last-verified timestamp, re-verified on a schedule through the existing warehouse-india GSTIN verification. Raise the alarm on a status other than ACTIVE, or on a missing covering row, while stock is on the floor. Keep `effective_to` for casual/NRTP registrations only.

## Acceptance

- A client registration flipped to CANCELLED by verification alarms within one job run, while that client's stock is at the site.
- A PPOB row covers the site and silences the alarm.
- A regular registration can be saved without `effective_to`, and no expiry alarm fires for it.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

s.27 sets a validity period only for casual/NRTP persons: https://taxinformation.cbic.gov.in/content/html/tax_repository/gst/acts/2017_CGST_act/active/chapter6/section27_v1.00.html (validity for regular registrations: UNVERIFIED, none found). Rule 14B recommendation: wr4_57th.txt l.411-425. Plan: p4-10.md:26 "expiry alert", :42 "declared as APOB" boolean. The INDIA pack already has a GSTIN verification and drift check (`WhinGstinDriftCheckService`) for parties, but no client use.

## Global setting

`WAREHOUSE_3PL_GSTIN_REVERIFY_DAYS` default=30 alternatives=7, 90

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#68
