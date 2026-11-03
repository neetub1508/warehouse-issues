TITLE: [Warehouse] [Finding] Real-world WR2-01 · Report physical-verification coverage and CARO class-wise discrepancies
LABELS: task,warehouse,gap-real-world,phase-p2
issue: 729
---
Part of #5 · Module **`warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #37, #141, #156, #136, #303 · Source: real-world gap check 2026-11-03, lane WR2 · Merges WR7-11

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Every audited company's auditor must say under CARO 2020 para 3(ii)(a) whether management verified inventory at reasonable intervals, whether coverage and procedure were appropriate, and whether discrepancies of 10% or more (by value, in aggregate per class of inventory) were found and properly dealt with. Today the count engine posts variances but nothing tells the auditor which items/classes were counted in the year, what share of value was covered, or the class-wise discrepancy percentage. The finance team rebuilds it in Excel from count exports, and the auditor cannot tie it to the ledger.

## Scope

(1) Inventory class mapping per item category to Schedule III classes (raw material, WIP, finished goods, stock-in-trade, stores and spares, loose tools, packing material, goods in transit), reusing neetub1508/accounting#303's class list through the adapter where it exists. (2) Physical Verification Register per company x period: every POSTED count with date, site, class, counted positions, book value counted, variance value (gross and net), counters/approvers. (3) Coverage report: per class and site, value and item-count share verified in the period, items never counted in the period. (4) CARO 3(ii)(a) summary: per class, aggregate net discrepancy value / book value of items counted, flag >= 10%, with the adjustment movements that dealt with it; export feeds neetub1508/accounting#211.

## Acceptance

- A class with book value 100,000 counted and net variance -10,000 shows 10.0% and is flagged; 9,999 shows 9.999% and is not.
- Coverage report lists every item with on-hand > 0 at period end that had no POSTED count in the period.
- Every register row drills to the count document and its COUNT_ADJ movements; totals tie to the adjustment register for the same period.
- Unposted (cancelled) counts are excluded and shown separately.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

CARO 3(ii)(a) text and value basis (P): https://taxguru.in/company-law/caro-2020-key-disclosure-requirement.html ; https://bcajonline.org/journal/caro-2020-series-new-clauses-and-modifications-inventories-and-other-current-assets/ . grep -ril "class of inventory" design set = 0; "CARO" only in docs/reviews/R5-standards-industry-ops.md:510; neetub1508/accounting#211 (CARO paper) acceptance has no inventory clause input; P2-21 (#141) count-variance report is per count, not per class per year.

## Global setting

`WAREHOUSE_PV_COVERAGE_PERIOD` default=FINANCIAL_YEAR alternatives=HALF_YEAR,QUARTER (the 10% CARO threshold is statutory, not a setting)

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#37

## Merged finding WR7-11 · Add a CARO 3(ii) physical-verification and discrepancy report

Every statutory auditor of a company holding stock must report two things:
- whether physical verification was done at reasonable intervals, and whether discrepancies of 10% or more in aggregate for any class of inventory were found and dealt with in the books;
- where secured working-capital limits exceed ₹5 crore, whether the quarterly stock statements filed with the bank agree with the books.
Today the store can count, but it cannot show coverage, class-wise aggregate discrepancy or statement-to-book agreement. Stores staff rebuild these in Excel every March.

**Scope:** 
- (a) PV coverage per year: items and locations counted at least once, with dates, counters and verifiers.
- (b) Discrepancy summary by inventory class (the item's STOCKING category, or an `inventory_class` attribute: RM, WIP, FG, stores and spares, scrap, goods in transit or with third parties), with book value, physical value, net and gross discrepancy %, a ≥10% flag, and the adjustment documents that cleared it.
- (c) A register of bank stock statements (period, bank, value filed by class) reconciled to the books as at that date, with differences explained.
- (d) Stock at third parties (job workers, approval, 3PL) listed with confirmation status.

**Acceptance:**
- A year where FG shows a 12% aggregate discrepancy flags FG and lists the clearing adjustments
- Items never counted in the FY appear on the coverage exceptions
- A filed Q2 statement differing from books by ₹4 lakh shows the difference by class
- Stock at job workers lists confirmation received or pending

**Evidence:** [CARO]. Plan: #37 gates by line tolerance, and #141 reports variance by line. grep `each class|class of inventory|CARO` in issues = 0. WS-224 (#136) gives stock as at a back date but holds no record of the statement filed with the bank.

**Global setting:** `WAREHOUSE_CARO_DISCREPANCY_THRESHOLD_PCT` default=10 alternatives=any lower value for internal policy
