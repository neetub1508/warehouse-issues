TITLE: [Warehouse] [Finding] Real-world WR4-01 · Generate the e-way bill for invoiced sales, not only for challans
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-india
issue: 738
---
Part of #8 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **blocker** · Finding type **PLANNED-WRONG** · Related: #147, #82, #649, #174 · Source: real-world gap check 2026-11-03, lane WR4

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Most outward movements are sales on a tax invoice. Above ₹50,000 the goods cannot leave the gate without EWB Part A that carries the invoice number. The decided owner (`warehouse.accounting.eway_bill_owner` = `WAREHOUSE_INDIA`, "as built") points at a module that only files EWBs for delivery challans. So with the default setting no module raises an EWB for a sale: the truck is either stopped at the gate or moves illegally. A truck caught without an EWB is detained, with a penalty of 200% of the tax. In practice Tally, ERPNext and SAP all raise the EWB from the sales invoice (or from the delivery note once it is invoiced).

## Scope


- Add a `SHIPMENT_INVOICE` source to warehouse-india EWB generation. It runs after `INVOICE_ACKNOWLEDGED` (invoice no./date, IRN if any). The from-block comes from the site, bill-to/ship-to from the frozen invoice addresses, lines from the shipped lines, and transport details from the handover/LR.
- Order of steps: approved despatch → invoice (and IRN) → EWB Part A → Part B → gate-out. When the GSTIN uses e-invoicing, accept an EWB already generated with the IRN and record it instead of filing again.
- Ownership by document class. Challan movements always belong to warehouse-india. For invoice-backed movements the existing setting decides, and the system refuses to file a second EWB for the same invoice.
- Bill-to/ship-to and dispatch-from variants (s.10(1)(b)) carried from the invoice.

## Acceptance

- A ₹2,00,000 inter-state invoiced shipment cannot gate out until an EWB that cites the invoice number is in `PART_B_UPDATED`
- An invoice whose IRN response already carried an EWB number is linked, not filed again
- Owner = `ACCOUNTING` → warehouse-india refuses to generate for an invoiced shipment and names the owner; challans are still generated
- A bill-to-ship-to sale carries both GSTIN/address blocks on the EWB

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

[EWBR] r.138(1); [GC57] s.129 penalty. Code: `WhinEwayBillService.java:97 SOURCE_DOCUMENT_TYPE = "DELIVERY_CHALLAN"` is the only source. Plan: p8-23.md:97 sets the default to `WAREHOUSE_INDIA`; acc #232 seeds the key and has accounting refuse. The p2in-04 movement table (lines 78-88) has no "sale on tax invoice" row. p9-20.md:33 expects an "e-way bill ref (india read through core)" on the invoice request, but nothing produces it.

## Global setting

`warehouse.accounting.eway_bill_owner` default=WAREHOUSE_INDIA (keep it, but scope it to invoice-backed movements) alternatives=ACCOUNTING

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#649, neetub1508/accounting#188
