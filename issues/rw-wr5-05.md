TITLE: [Warehouse] [Finding] Real-world WR5-05 · Hold plastic-packaging weight per SKU and EPR registration on labels
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-india
issue: 746
---
Part of #8 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #55, #573, #33 · Source: real-world gap check 2026-11-03, lane WR5

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Plastic EPR is owed on the weight of packaging by category, not on the product's count. One `epr_category` per item cannot give a producer or brand owner the kilograms of rigid, flexible or multilayer plastic placed on the market. Since 1 July 2025 the pack must also carry the PIBO's registration number by barcode, QR or printed number. Batteries may show the EPR number by QR from Feb 2025.

## Scope

Per item × packaging level, a packaging composition (plastic category, grams per unit). The EPR return aggregates despatched units × grams by category, with exports separable. The company's CPCB registration number per regime and role (producer, importer, brand owner) goes into the label `declaration` block, with an optional QR payload. Items with no composition are named, as P4-08 already does for categories.

## Acceptance

- Despatch of 1,000 units carrying 20 g Cat-I and 5 g Cat-III gives 20 kg and 5 kg on the return
- A retail label prints the registration number or QR once the regime registration is set
- Exported despatches show in a separate column

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

[Lexplosion, PWM Amendment 2025](https://lexplosion.in/amendments-to-the-plastic-waste-management-rules-2016-notified-pibos-directed-to-provide-specified-information-in-a-barcode-or-quick-response-code-printed-on-the-plastic-packaging-w-e-f-01-07-25/); [BWM Amendment 2025](https://www.corporateprofessionals.com/regulatoryupdate/battery-waste-management-amendment-rules-2025/). Grep `packaging weight|plastic weight|registration number.{0,40}(epr|cpcb)` = 0. P4-08 says "nothing new is captured".

## Global setting

`WAREHOUSE_EPR_EXCLUDE_EXPORTS` default=true alternatives=false

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#55
