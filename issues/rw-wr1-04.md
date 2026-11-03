TITLE: [Warehouse] [Finding] Real-world WR1-04 · Record the written objection date for MSE suppliers and alert before day 15
LABELS: task,warehouse,gap-real-world,phase-p8
issue: 724
---
Part of #546 · Module **`warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #568, #569, #692, #174, #579 · Source: real-world gap check 2026-11-03, lane WR1

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

For micro and small suppliers, the payment clock and the 43B(h) disallowance run from acceptance. If no written objection reaches the supplier within 15 days of delivery, the law deems the goods accepted on the delivery date. Where QC takes longer (lab tests), the company loses its right to dispute and still has to pay within 45 days. Accounting's 43B(h) register needs the delivery date, the objection date and the acceptance date, and only the warehouse knows them.

## Scope

On a GRN of a supplier with MSME category MICRO/SMALL, compute `objection_deadline` = receipt date + 15 days. An alert at `WAREHOUSE_MSE_OBJECTION_ALERT_DAYS` before it while any quantity is still in QC / MRN-pending. A "Communicate objection" action on the rejection note / NCR / short-receipt claim stamps `objection_sent_at` + channel. The MRN envelope (FR-719) carries `delivery_date`, `objection_sent_at`, `acceptance_date` (MRN authorisation, or the deemed date when no objection was sent in time) per line.

## Acceptance

- A MICRO supplier GRN still in QC on day 12 raises the alert to QC and purchase.
- An objection sent on day 10 stamps the date. An MRN on day 20 sends acceptance = MRN date, objection = day 10.
- With no objection, an MRN on day 20 sends acceptance = receipt date (deemed) and flags `DEEMED`.
- A non-MSE supplier creates no deadline.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

Deemed acceptance when there is no written objection within 15 days of delivery ([busy.in](https://busy.in/tds/section-43bh-msme-payment-rule-and-45-day-limit-explained/), [taxguru](https://taxguru.in/income-tax/section-43b-income-tax-act-payment-msme.html)). Accounting #97 (comment) needs "acceptance/objection history". Plan: grep of `objection|deemed accept|acceptance date` in issues/FRD/contracts finds 0. FR-717 prints a rejection note but records no date of communication. #692 QC-held ageing is not supplier-class aware.

## Global setting

`WAREHOUSE_MSE_OBJECTION_ALERT_DAYS` default=3 alternatives=0-14

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#569, #174
