TITLE: [Warehouse] [Finding] Real-world WR5-04 · Keep the hazardous-waste store: 90-day clock, Form 3 register, Form 10, Form 4
LABELS: task,warehouse,gap-real-world,phase-p10,warehouse-india
issue: 745
---
Part of #548 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #32, #641 · Source: real-world gap check 2026-11-03, lane WR5 · Merges WR3-12

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Factory stores hold used oil, spent solvent, sludge and contaminated drums. HOWM Rules 2016 allow 90 days on site (180 with SPCB leave), require a Form 3 record, a Form 10 manifest per consignment to an authorised recycler or TSDF, and a Form 4 annual return by 30 June. Totals must reconcile, and a late return draws penalty and consent action.

## Scope

An HW item flag with a Schedule I category; an HW store location type. Each generation posts a receipt that starts a 90-day clock per lot, with an alert before expiry. Disposal to a counterparty needs its SPCB authorisation number and validity and a Form 10 manifest number, and posts the issue. A Form 3 register (generation, storage, disposal per category). A Form 4 annual return, generated, frozen when filed, reconciling to Form 3.

## Acceptance

- An HW lot aged 85 days raises the alert; at 91 days it shows overdue unless an SPCB extension date is recorded
- Disposal to a counterparty with an expired authorisation is refused
- Form 4 for FY 2025-26 equals the Form 3 totals and reproduces identically after filing

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

[MPCB circular](https://www.mpcb.gov.in/sites/default/files/standing_orders/HazardousWasteCircular16042020.pdf) (90 / 180 days); [Corpseed](https://www.corpseed.com/knowledge-centre/hazardous-waste-authorization-annual-return) (Form 4, 30 June); [myndsolution](https://www.myndsolution.com/complete-guide-to-hazardous-waste-compliance-in-india-rules-authorisation-and-disposal-requirements/) (Form 3 and Form 10, practitioner). Grep `hazardous waste|Hazardous and Other` in issues = 0. P4-04 #32 treats scrap sale as a supply only.

## Global setting

`WAREHOUSE_HW_STORAGE_DAYS` default=90 alternatives=up to 180 per SPCB order

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

WR5-01

## Merged finding WR3-12 · Keep the hazardous-waste register, manifest and Form 4 return

Plating, painting, chemical and pharma plants hold hazardous-waste authorisation from the SPCB. They must record every kg of spent oil, sludge and contaminated containers generated, stored and sent to a TSDF or recycler (Form 3), raise a manifest per consignment (Form 10), and file the Form 4 annual return by 30 June. These quantities come from production and stores, and the plan tracks none of them. Penalties apply for wrong or late returns.

**Scope:** Add a hazardous-waste category on items (HW schedule category code), receipts into a HW store from production / maintenance (reason codes), a disposal dispatch to an authorised party with manifest number and vehicle, a Form 3-shaped register, and a Form 4-shaped annual extract (generated, stored, sent, closing) per authorisation. Storage-time warning against the authorisation limit.

**Acceptance:**
- 200 kg spent oil generated over the year and 180 kg dispatched on 2 manifests produce a Form 4 extract showing closing stock of 20 kg.
- A dispatch without a manifest number is refused.
- The register reconciles to the ledger.

**Evidence:** https://www.myndsolution.com/complete-guide-to-hazardous-waste-compliance-in-india-rules-authorisation-and-disposal-requirements/ (practitioner); filed Form 4 example https://www.dfpcl.com/uploads/2020/01/Form-4-DFPCL-HW-Annual-Return-2018-19-30.06.19.pdf. Plan: P4-08 covers EPR for batteries / e-waste / tyres / plastic only; grep `hazardous waste|SPCB|manifest.*TSDF` in issues → none.

**Global setting:** `WAREHOUSE_IN_HAZARDOUS_WASTE_ENABLED` default=false alternatives=true
