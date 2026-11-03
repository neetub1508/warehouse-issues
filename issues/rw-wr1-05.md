TITLE: [Warehouse] [Finding] Real-world WR1-05 · Check BIS Standard Mark and licence on receipt of QCO-notified items
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-india
issue: 725
---
Part of #8 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #566, #579, #641 · Source: real-world gap check 2026-11-03, lane WR1 · Merges WR5-03

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Once an item is under a Quality Control Order, storing, selling or using non-certified goods is an offence under the BIS Act, punishable with imprisonment and fine. The law names storage explicitly, so a warehouse is directly exposed. Factories buying steel, chemicals, electricals, fasteners, toys and similar items must verify the ISI mark and the supplier's valid BIS licence at receipt. The plan has no way to flag a notified item or block receipt without proof.

## Scope

Item attribute `bis_qco_applicable` + IS number + QCO effective date. Supplier-item BIS licence (CM/L number, valid-until) on the supplier source. At GRN, for a notified item: licence present and valid on the receipt date, and a "Standard Mark seen" check per line. Otherwise the stock lands in QUARANTINE with reason `BIS_NONCOMPLIANT`, under the setting. An expiry alert for supplier licences. A report of non-compliant receipts.

## Acceptance

- Receiving a QCO item from a supplier whose licence expired yesterday puts it in QUARANTINE (or refuses it under BLOCK) with the reason shown.
- A valid licence plus a ticked mark check lets the GRN proceed normally.
- A licence expiring within 30 days raises an alert to purchase.
- An item whose QCO effective date is after the receipt date is not checked.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

BIS Act 2016 s.17 prohibition covers manufacture, import, distribution, sale, hire, lease, storage and exhibition for sale, with up to 2 years' imprisonment ([BIS QCO guidance](https://www.bis.gov.in/wp-content/uploads/2021/08/Guidance-Document-on-Quality-Control-Orders-QCOs-1.pdf), [Lakshmikumaran](https://cn.lakshmisri.com/insights/articles/ensuring-compliance-enforcement-and-search-seizure-powers-of-the-bureau-of-indian-standards)). Plan: grep of `BIS|ISI mark|QCO|Quality Control Order` in issues, FRD and contracts has no hit.

## Global setting

`WAREHOUSE_INDIA_BIS_QCO_RECEIPT_POLICY` default=QUARANTINE alternatives=BLOCK,WARN

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Merged finding WR5-03 · Gate BIS QCO goods on a valid Standard Mark licence at receipt and despatch

For goods under a Quality Control Order, storing, distributing or selling without the Standard Mark under a valid BIS licence is an offence (s.17 / s.29(3), up to 2 years). BIS raids warehouses and seizes such stock. A trader or 3PL needs the system to stop non-certified QCO stock entering available stock, and to hold stock whose manufacturer's licence lapsed.

**Scope:** A dated QCO code list (IS number, scheme ISI or CRS, effective from / to, revoking notification). Item to QCO assignment, dated. Manufacturer licence / R-number per supplier × item with validity. At GRN, a QCO item from a supplier with no valid licence on the receipt date goes to a hold `BIS_UNCERTIFIED`, not AVAILABLE. Despatch and channel publish of held stock are refused. A revoked QCO stops the gate from its revocation date.

**Acceptance:**
- A GRN of a QCO item with an expired manufacturer licence lands in hold BIS_UNCERTIFIED
- Despatch of that stock is refused with the IS number and licence named
- An item whose QCO was revoked yesterday receives normally today
- Report: QCO stock by licence status and site

**Evidence:** [BIS QCO guidance](https://www.bis.gov.in/wp-content/uploads/2021/08/Guidance-Document-on-Quality-Control-Orders-QCOs-1.pdf); [seizure report](https://morungexpress.com/bis-raids-largest-warehouse-in-south-india-seizes-articles-valued-at-rs-25-crore). QCOs are added and revoked often (chemicals revoked 2025, cotton bales rescinded 9-6-2026, [Agile](https://www.agileregulatory.com/latest-updates/government-rescinds-cotton-bales-quality-control-order-2023-what-this-means-for-the-textile-industry)). Grep `QCO|Quality Control Order|ISI mark|Standard Mark|CM/L` (case-sensitive) = 0 tasks.

**Global setting:** `WAREHOUSE_BIS_QCO_GATE` default=HOLD alternatives=HOLD|WARN|OFF
