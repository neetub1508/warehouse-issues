# WH-E2E gap review and real-world check — 2026-11-03

Every one of the 710 issues in this repository was checked against classic HEAD `4843b1648d` by twelve lanes, each run by two review engines (Claude and GPT); a GPT-only finding was kept only after it was confirmed in the code. Seven further lanes compared the plan with how Indian warehouses, stores, manufacturers and 3PL operators actually work, citing statute and product documentation. Per-lane evidence (file:line per issue) is kept with the review run; this page records the outcome.

## Verdicts

BUILT 551 · PARTIAL 56 · NOT-BUILT 102. Most NOT-BUILT issues are the unbuilt `warehouse-trade` / `warehouse-manufacturing` phases (P9, P10) or scope retired by decision; those are not findings.

## Outcome

129 findings: 54 filed as new issues, 29 reopened 27 closed issues (label `reopened-e2e`, section "Reopened scope"), 25 extended 22 open issues (section "E2E additions"), 7 confirmed already built (comment only), 13 merged as duplicates, 1 not filed. Filed severity: blocker 3, major 70, minor 35.

Statutory content in these findings rests partly on practitioner copies because CBIC and the income-tax portal refused automated fetches; each filed issue carries a note to confirm figures against the law in force at build time, and the catalogue marks UNVERIFIED rows.

## Findings

| Id | Severity | Type | Module | Title | Disposition |
|---|---|---|---|---|---|
| W01-01 | major | OPEN-SCOPE-GAP | warehouse-3pl | Meter 3PL freight at despatch and true it up on the carrier invoice | added to #39 |
| W01-02 | major | OPEN-SCOPE-GAP | warehouse-india | Produce the scrap-sale request when scrap stock is despatched | reopened #32 |
| W01-03 | minor | CLOSED-INCOMPLETE | warehouse-3pl | Apply the final storage tier's minimum before metering its charge | reopened #30 |
| W02-01 | major | CLOSED-INCOMPLETE | warehouse | Revoke AUDITOR export grants on quality registers and ratchet it | reopened #117 |
| W02-02 | minor | CLOSED-INCOMPLETE | warehouse | Show matched supplier invoices on the purchase order detail | reopened #105 |
| W02-03 | major | CLOSED-INCOMPLETE | warehouse-base | Parse import dates strictly on the server (DD/MM/YYYY, DD-MM-YY, serial) | reopened #90 |
| W02-04 | major | CLOSED-INCOMPLETE | warehouse | Route every document status change through the transition helper | reopened #111 |
| W02-05 | major | CLOSED-INCOMPLETE | warehouse-india | Exclude sandbox sites from India statutory outputs and e-way bills | reopened #116 |
| W02-06 | blocker | CLOSED-INCOMPLETE | warehouse | Re-run the recall guard when a pending movement is approved | reopened #76 |
| W02-07 | major | CLOSED-INCOMPLETE | warehouse-base | Let the movement port consume a reservation on post and reverse | reopened #71 |
| W02-08 | major | SPEC-CONFLICT | warehouse-base | Give integrations a machine login instead of a borrowed user session | reopened #119 |
| W02-09 | major | CLOSED-INCOMPLETE | warehouse-base | Build the returnable packaging balance screen with export | reopened #114 |
| W02-10 | minor | SPEC-CONFLICT | warehouse | Add a web labour timer on work orders and labour tasks | reopened #91 |
| W02-11 | minor | OPEN-ALREADY-BUILT | warehouse-india | Close #88 and #115 once their owed S5 runtime runs pass | comment on #88 |
| W03-01 | major | CLOSED-INCOMPLETE | warehouse-base | Refuse a master merge while transfers, counts or returns name the item | reopened #148 |
| W03-02 | major | MISSING-TASK | warehouse-base | Enforce the View / Operate / Admin level on warehouse and owner grants | new #717 |
| W03-03 | major | OPEN-SCOPE-GAP | warehouse | Carry one currency through the inter-company order pair | added to #133 |
| W03-04 | major | OPEN-SCOPE-GAP | warehouse-india | Give the scrap-sale accounting handover a producer and an owner | merged into W01-02 |
| W03-05 | major | MISSING-TASK | warehouse | Keep landed cost on job-work, production and sample issues out of cost of sales | new #718 |
| W03-06 | minor | CLOSED-INCOMPLETE | warehouse-base | Make warehouse exports follow the grid sort | reopened #154 |
| W03-07 | minor | OPEN-ALREADY-BUILT | warehouse-india | Mark #130's Help-button rollout as built and keep only the run checks open | comment on #130 |
| W04-01 | minor | CLOSED-INCOMPLETE | warehouse-base | Make import validation-report status transitions atomic | reopened #235 |
| W04-02 | minor | CLOSED-INCOMPLETE | warehouse-base | Correct INSTALL archiving section to match the shipped archive run | reopened #217 |
| W04-03 | major | OPEN-SCOPE-GAP | warehouse-base | Alert and catch up when a scheduled database backup fails | added to #227 |
| W04-04 | minor | MISSING-TASK | warehouse-india | Own the s.145A / Form 3CD clause 14 inventory-valuation statement | added to #677 |
| W04-05 | major | CLOSED-INCOMPLETE | warehouse | Deliver the low-stock report on a schedule with per-recipient site scope | reopened #141 |
| W04-06 | minor | OPEN-ALREADY-BUILT | warehouse-base | Run the warehouse-base ratchet gate and close #240 | comment on #240 |
| W05-01 | minor | CLOSED-INCOMPLETE | warehouse-base | Make GL posting-rule edit, end and withdraw safe against concurrent writes | reopened #281 |
| W05-02 | minor | CLOSED-INCOMPLETE | warehouse | Word the retired-owner refusal for orders and shipments correctly | reopened #258 |
| W06-01 | major | CLOSED-INCOMPLETE | warehouse | Value foreign-currency PO receipts at invoice cost times rate | reopened #329 |
| W06-02 | major | SPEC-CONFLICT | warehouse-base | Fix transfer value at departure and carry it through transit | reopened #330 |
| W06-03 | minor | OPEN-ALREADY-BUILT | warehouse-india | Close #323: Part A lapse built as a setting, default never lapse | comment on #323 |
| W07-01 | major | MISSING-TASK | warehouse-base | Date stock movements on the site's local day, not the UTC day | new #719 |
| W08-01 | major | OPEN-SCOPE-GAP | warehouse-india | Record a job-work deemed supply and take the stock off the principal's books | reopened #22 |
| W08-02 | minor | CLOSED-INCOMPLETE | warehouse-india | Re-pin the e-way recovery contract citations to current source | reopened #429 |
| W10-01 | major | CLOSED-INCOMPLETE | warehouse-base | Carry the store-issue cost object on the accounting envelope | reopened #571 |
| W10-02 | major | CLOSED-INCOMPLETE | warehouse | Pay the MRN on the quantity it authorised, not a blank GRN acceptance | reopened #569 |
| W10-03 | minor | CLOSED-INCOMPLETE | warehouse | Make the last partial store return restore the issue value exactly | reopened #572 |
| W10-04 | major | CLOSED-INCOMPLETE | warehouse | Use one cost unit for store issue, return and the issue register | reopened #571 |
| W11-01 | major | OPEN-SCOPE-GAP | warehouse | Sweep every includeId picker, not only the 11 listed in #618 | added to #618 |
| W11-02 | minor | OPEN-SCOPE-GAP | warehouse-base | Extend #609 to all 99 seeded keys missing from the settings catalogue | added to #609 |
| W11-03 | minor | OPEN-ALREADY-BUILT | warehouse | Close #630, #635 and #665 once the CI-only ITs pass | comment on #630 |
| W11-04 | major | CLOSED-INCOMPLETE | warehouse | Count only stock-effective dispositions in the quality registers | reopened #640 |
| W11-05 | major | SPEC-CONFLICT | warehouse | Exclude passes after a failed attempt from first-pass acceptance | reopened #640 |
| W12-01 | minor | OPEN-ALREADY-BUILT | warehouse | Close #698: store-returns menu leaf already seeded and routed | comment on #698 |
| W12-02 | minor | OPEN-ALREADY-BUILT | warehouse-base | Close #669 and #673 after their pending gates; code is complete | comment on #669 |
| W12-03 | major | OPEN-SCOPE-GAP | warehouse-base | Post the negative-estimate settlement variance as a value movement | added to #671 |
| W12-04 | major | OPEN-SCOPE-GAP | warehouse-base | Make REVALUATION writer-only for reversal, like STANDARD_COST_ALIGNMENT | added to #670 |
| W12-05 | major | SPEC-CONFLICT | warehouse | Decide #714: one serial per base unit for pack-unit receipts | added to #714 |
| W12-06 | major | MISSING-TASK | warehouse-3pl | Date 3PL credits by the site-local day, not the UTC day (billing B-2) | new #720 |
| W12-07 | major | MISSING-TASK | warehouse-3pl | Count storage toward the site minimum charge (billing B-3) | new #721 |
| W12-08 | minor | OPEN-SCOPE-GAP | warehouse-base | Refuse an item GTIN whose GS1 check digit is wrong at save | added to #712 |
| W12-09 | minor | OPEN-SCOPE-GAP | warehouse | Gate MRN action flags on the owner grant the action checks | added to #706 |
| W12-10 | major | OPEN-SCOPE-GAP | warehouse-3pl | Restrict 3PL snapshot-settlement evidence behind an owner-checked route | added to #708 |
| WR1-01 | major | PLANNED-WRONG | warehouse | Accept one supplier invoice delivered in lots across gate entries | new #722 |
| WR1-02 | major | MISSING-TASK | warehouse-india | Raise the India challan and e-way bill for goods going back to the supplier | new #723 |
| WR1-03 | minor | MISSING-TASK | warehouse-india | Check the supplier's e-way bill at the gate and record its rejection | merged into WR7-03 (#764) |
| WR1-04 | major | MISSING-TASK | warehouse | Record the written objection date for MSE suppliers and alert before day 15 | new #724 |
| WR1-05 | major | MISSING-TASK | warehouse-india | Check BIS Standard Mark and licence on receipt of QCO-notified items | new #725 |
| WR1-06 | major | MISSING-TASK | warehouse | Let a transit loss claim name the carrier or insurer, not only the supplier | new #726 |
| WR1-07 | minor | MISSING-TASK | warehouse | Add IS 2500 switching rules and the 2026 skip-lot to AQL sampling | new #727 |
| WR1-08 | minor | MISSING-TASK | warehouse-india | Record a Commissioner's extension of a job-work return window per challan | merged into W08-01 |
| WR1-09 | minor | PLANNED-WRONG | warehouse-india | Correct "ITC-04 for the quarter" to half-yearly / annual in the P4 epic | merged into WR7-07 (#768) |
| WR1-10 | minor | MISSING-TASK | warehouse | Let an inward gate entry reference an assets-module PO receipt | new #728 |
| WR2-01 | major | MISSING-TASK | warehouse | Report physical-verification coverage and CARO class-wise discrepancies | new #729 |
| WR2-02 | minor | MISSING-TASK | warehouse | Keep the location custodian off counting their own bins | new #730 |
| WR2-03 | minor | MISSING-TASK | warehouse | Control count sheets and tags as numbered, reconciled documents | new #731 |
| WR2-04 | major | MISSING-TASK | warehouse | Confirm and reconcile own stock held by third parties | new #732 |
| WR2-05 | major | PLANNED-WRONG | warehouse-base | Parse all GS1 date and content AIs at scan, mapping 15 to best-before | new #733 |
| WR2-06 | major | MISSING-TASK | warehouse-india | Read Schedule H2 drug QR codes into item, batch and expiry | not filed: Pharma (Schedule H2) declined by D-18 |
| WR2-07 | major | MISSING-TASK | warehouse | Record storage temperature readings and hold stock on excursion | new #734 |
| WR2-08 | major | PLANNED-WRONG | warehouse-base | Enforce dangerous-goods segregation between incompatible classes | merged into WR5-02 (#744) |
| WR2-09 | major | MISSING-TASK | warehouse-india | Stop on-hand exceeding a premises' licensed storage quantity | merged into WR5-02 (#744) |
| WR2-10 | minor | MISSING-TASK | warehouse | Report stores SoD conflicts and run periodic access reviews | new #735 |
| WR3-01 | major | PLANNED-WRONG | warehouse-manufacturing | Keep production and QC scrap as saleable on-hand stock, not VIRT-SCRAP | added to #593 |
| WR3-02 | major | PLANNED-WRONG | warehouse-india | Give moulds, dies, jigs, fixtures and tools a no-limit job-work type | added to #601 |
| WR3-03 | major | MISSING-TASK | warehouse-india | Record a Commissioner's extension of the job-work return period | merged into W08-01 |
| WR3-04 | major | MISSING-TASK | warehouse-india | Support inputs shipped direct from the supplier to the job worker | added to #601 |
| WR3-05 | major | MISSING-TASK | warehouse-india | Allow job worker to job worker movement and supply from the job worker's premises | added to #601 |
| WR3-06 | major | MISSING-TASK | warehouse-manufacturing | Build job work IN: process a customer's material as a job worker | new #736 |
| WR3-07 | minor | MISSING-TASK | warehouse-india | Raise a supply for scrap left at an unregistered job worker | added to #601 |
| WR3-08 | major | PLANNED-WRONG | warehouse-manufacturing | Absorb conversion cost on orders without routing or bookings | added to #600 |
| WR3-09 | major | MISSING-TASK | warehouse-manufacturing | Add a one-step production entry for small shops | added to #596 |
| WR3-10 | minor | PLANNED-WRONG | warehouse-manufacturing | Credit by-products at current realisable value, not a frozen BOM rate | added to #594 |
| WR3-11 | major | MISSING-TASK | warehouse-manufacturing | Produce a Batch Manufacturing Record from production data | added to #598 |
| WR3-12 | major | MISSING-TASK | warehouse-india | Keep the hazardous-waste register, manifest and Form 4 return | merged into WR5-04 (#745) |
| WR3-13 | minor | MISSING-TASK | warehouse-india | Report the Rule 56(12) monthly production account per product | added to #604 |
| WR3-14 | minor | MISSING-TASK | warehouse | Track repairable spares by condition through repair | new #737 |
| WR4-01 | blocker | PLANNED-WRONG | warehouse-india | Generate the e-way bill for invoiced sales, not only for challans | new #738 |
| WR4-02 | minor | MISSING-TASK | warehouse-india | Support multi-vehicle movement on one e-way bill | new #739 |
| WR4-03 | major | MISSING-TASK | warehouse (carrier master) + accounting-adapter-warehouse | Carry the GTA tax character of freight from transporter to bill | new #740 |
| WR4-04 | major | MISSING-TASK | warehouse-india | Record a consignment detained in transit and its release | new #741 |
| WR4-05 | minor | MISSING-TASK | warehouse | Declare each dispatch under the transit-insurance open policy | new #742 |
| WR4-06 | major | MISSING-TASK | warehouse | Model delivery exceptions: refused, partly accepted, re-attempt | new #743 |
| WR4-07 | major | MISSING-TASK | warehouse-trade | Report goods dispatched but not delivered at period end by terms | added to #586 |
| WR4-08 | major | PLANNED-WRONG | warehouse-trade + warehouse-india | Gate export dispatch on LUT and capture shipping bill, port, container | added to #644 |
| WR5-01 | major | PLANNED-WRONG | warehouse-india | Split non-pharma site licences out of the fenced regulated-goods pack | added to #88 |
| WR5-02 | major | MISSING-TASK | warehouse-base | Enforce DG class segregation, licensed store quantity and SDS on file | new #744 |
| WR5-03 | major | MISSING-TASK | warehouse-india | Gate BIS QCO goods on a valid Standard Mark licence at receipt and despatch | merged into WR1-05 (#725) |
| WR5-04 | major | MISSING-TASK | warehouse-india | Keep the hazardous-waste store: 90-day clock, Form 3 register, Form 10, Form 4 | new #745 |
| WR5-05 | major | MISSING-TASK | warehouse-india | Hold plastic-packaging weight per SKU and EPR registration on labels | new #746 |
| WR5-06 | minor | MISSING-TASK | warehouse-india | Record expired and rejected food disposal and the FSSAI quarterly data | new #747 |
| WR5-07 | minor | MISSING-TASK | warehouse | Log cold-room temperatures and hold stock on an excursion | merged into WR2-07 (#734) |
| WR5-08 | minor | MISSING-TASK | warehouse | Run and record mock recall drills against the trace report | new #748 |
| WR5-09 | minor | MISSING-TASK | warehouse-india | Add customs and hazardous-waste retention clocks anchored on removal | merged into WR7-09 (#770) |
| WR5-10 | minor | PLANNED-WRONG | warehouse-india | Correct the bonded interest rule: all clause (c) goods, from the s.60 order | new #749 |
| WR5-11 | minor | MISSING-TASK | warehouse | Produce the monthly stock-insurance declaration per insured location | new #750 |
| WR6-01 | blocker | MISSING-TASK | warehouse-india | Generate challans and e-way bills for client stock under the client's GSTIN | new #751 |
| WR6-02 | major | MISSING-TASK | warehouse-3pl | Refuse receipt of client stock at a premises the client has not registered | new #752 |
| WR6-03 | major | PLANNED-WRONG | warehouse-3pl | Track client GSTIN status and PPoB/APOB type instead of an expiry date | new #753 |
| WR6-04 | major | MISSING-TASK | warehouse-3pl | Put an overdue client's outward releases on credit hold | new #754 |
| WR6-05 | major | MISSING-TASK | warehouse-3pl | Add a custody claim register for client goods lost or damaged in storage | new #755 |
| WR6-06 | major | MISSING-TASK | warehouse-3pl | Run client exit as a handover: final joint count, stock-out, hold-over, data return | new #756 |
| WR6-07 | minor | MISSING-TASK | warehouse-3pl | Produce client-attended count sheets and a year-end stock confirmation | new #757 |
| WR6-08 | minor | MISSING-TASK | warehouse-india | Add a Rule 58 warehouse register and a GST inspection pack per owner | new #758 |
| WR6-09 | major | MISSING-TASK | warehouse-3pl | Carry a per-client tax treatment so exempt storage is not billed at 18% | new #759 |
| WR6-10 | minor | MISSING-TASK | warehouse-3pl | Alert when an approved period is not invoiced within the statutory window | new #760 |
| WR6-11 | minor | MISSING-TASK | warehouse-3pl | Add dock-to-stock, inventory accuracy and order accuracy SLA metrics | new #761 |
| WR7-01 | major | PLANNED-WRONG | warehouse-india | Re-seed scrap TCS as s.394(1) at 2% from 1 April 2026 | new #762 |
| WR7-02 | major | PLANNED-WRONG | warehouse-india | Let dispatch proceed without Part B for in-state hauls up to 50 km | new #763 |
| WR7-03 | major | MISSING-TASK | warehouse-india | Handle inbound e-way bills: verify at gate, accept/reject, consignee-generated, returns | new #764 |
| WR7-04 | major | MISSING-TASK | warehouse-india | Build Rule 55(5) lot-wise despatch for SKD/CKD and part shipments | new #765 |
| WR7-05 | major | PLANNED-WRONG | warehouse-india | Re-base goods on approval on s.31(7) and invoice at six months | new #766 |
| WR7-06 | major | PLANNED-WRONG | warehouse-india | Trace ITC reversal for produced and WIP lots to the inputs consumed | new #767 |
| WR7-07 | minor | PLANNED-WRONG | warehouse-india | Correct job-work citations and the stale quarterly ITC-04 wording | new #768 |
| WR7-08 | minor | PLANNED-WRONG | warehouse | Complete the Rule 28 transfer-valuation bases | new #769 |
| WR7-09 | major | MISSING-TASK | warehouse-india | Anchor bonded and MOOWR record retention on the removal date | new #770 |
| WR7-10 | major | PLANNED-WRONG | warehouse-india | Switch the tax-audit quantitative statement to Form 26 from tax year 2026-27 | merged into W04-04 |
| WR7-11 | major | MISSING-TASK | warehouse | Add a CARO 3(ii) physical-verification and discrepancy report | merged into WR2-01 (#729) |
