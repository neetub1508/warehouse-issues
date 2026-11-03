TITLE: [Warehouse] [Finding] Real-world WR1-02 · Raise the India challan and e-way bill for goods going back to the supplier
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-india
issue: 723
---
Part of #8 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #568, #93, #140, #147, #565 · Source: real-world gap check 2026-11-03, lane WR1

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Rejected lots (RTV), refused excess and dock rejects leave the factory on a truck. Moving goods without a challan or invoice and an e-way bill exposes the consignment to detention and penalty in transit. The plan's India documents cover transfers and sales only, so the stores manager has to cut a manual challan outside the system, and the stock and GST trails then disagree.

## Scope

A delivery-challan source `SUPPLIER_RETURN` (and `GRN_REFUSAL` for refused excess / dock reject on the same vehicle) with taxability basis `RETURN_TO_SUPPLIER` or `TAX_INVOICE_BY_ACCOUNTING`. EWB Part-A/B from it with the right sub-type. The supplier-return dispatch (and the inward entry's gate-out when refused quantity leaves) is guarded by the existing e-way/challan dispatch gate (FR-195), as for transfers. The challan number is carried on the debit-note proposal (#174).

## Acceptance

- Dispatching an approved supplier return of ₹80,000 inter-state, with India enabled, is refused until a challan and EWB exist. Once they exist it dispatches.
- Refused excess on an inward entry blocks gate-out until a `GRN_REFUSAL` challan is issued, or the user records the supplier's own document number with a reason.
- The challan prints the original supplier invoice number / date and the GRN.
- The debit-note proposal envelope names the challan.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

Practitioners say return movements need a Rule 55 delivery challan (or a recipient tax invoice) and an EWB ([caclubindia](https://www.caclubindia.com/forum/return-of-material-416621.asp), [taxclue](https://www.taxclue.in/blog/rule-55-delivery-challan-five-situations)). This is practitioner practice; no CBIC circular was found. Plan: `whin_delivery_challans` source types are transfer and demand order (`V541149:84`). `SUPPLIER_RETURN` does not occur in `classic/warehouse-india/backend/src/main` (grep: 0 files). GTE-T4-06 lists refused excess as "leaving with the vehicle" as a read model only. RQP-GRD-41 supplier return `DISPATCHED` has no India guard.

## Global setting

`WAREHOUSE_INDIA_SUPPLIER_RETURN_DOCUMENT` default=DELIVERY_CHALLAN alternatives=TAX_INVOICE_BY_ACCOUNTING,NONE

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#147, #140
