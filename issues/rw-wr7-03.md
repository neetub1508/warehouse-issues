TITLE: [Warehouse] [Finding] Real-world WR7-03 · Handle inbound e-way bills: verify at gate, accept/reject, consignee-generated, returns
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-india
issue: 764
---
Part of #8 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #147, #82 · Source: real-world gap check 2026-11-03, lane WR7 · Merges WR1-03

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

The plan treats the e-way bill as outbound only. In practice:
- Our GSTIN is the recipient on every supplier's bill, and a bill we do not reject within 72 hours is deemed accepted. Short, wrong or never-arrived goods then sit in GSTR-2B as if received.
- When we buy scrap or loose material from unregistered sellers, the law makes us generate the bill. This is now routine for metal, plastic and tyre scrap and e-waste under the 1 Nov 2026 RCM regime.
- A customer who refuses delivery sends the truck back, and that return leg needs its own challan and bill.

## Scope


- (a) Gate-in for an inward purchase checks the supplier's EWB number against the expected vehicle, GSTIN, value and validity (through the provider when one is configured, manually otherwise). A mismatch raises a named exception and does not block unloading.
- (b) A worklist of EWBs raised against our GSTINs with a 72-hour countdown. Accept or reject per bill, with a reason. A GRN short or rejection is offered as a reject reason.
- (c) A GRN from an unregistered supplier above the threshold generates the EWB as consignee, before the vehicle moves when we arrange transport.
- (d) A customer-refused or RTO return creates a return challan and EWB with the original invoice referenced.

## Acceptance

- An inward gate entry whose EWB vehicle differs from the arriving vehicle raises `EWB_VEHICLE_MISMATCH`
- An EWB against our GSTIN with no GRN 60 hours after generation appears as "reject window closing"
- A ₹80,000 plastic-scrap purchase from an unregistered seller dated 2 Nov 2026 cannot be received without a consignee-generated EWB number
- A refused delivery returns stock only on a return challan carrying its own EWB

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

[R138] r.138(1) (recipient generates where the supplier is unregistered), r.138(12) (72 h deemed acceptance), r.138A (documents on the vehicle). [NOV26] gives the RCM scope. Plan: FR-516 stores `e-way bill no.` on the GRN bill row only. The gate-entry contract GTE-T1-01 has no EWB validation. grep `recipient.*generat|consignee.*generat` = 0, `72 h|reject.*recipient` = 0.

## Global setting

`WAREHOUSE_INDIA_INBOUND_EWB_CHECK` default=WARN alternatives=BLOCK,OFF

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#147

## Merged finding WR1-03 · Check the supplier's e-way bill at the gate and record its rejection

The gate captures the e-way bill number but never checks that it is still valid, so expired-EWB arrivals pass unnoticed. When goods are turned back or refused, the recipient should reject the EWB on the portal within 72 hours. If it does not, the EWB is deemed accepted, and the department's data then shows an inward supply that never happened, which surfaces at ITC reconciliation.

**Scope:** On an inward entry, optional EWB valid-until (entered, or fetched through the existing India gateway when configured) with an "expired on arrival" warning. On turn-back, or on a GRN with refusal ≥ the whole line, open a task "Reject EWB on portal" with a 72 h deadline from generation. Record evidence of the portal rejection (reference, time) as on IMD-T1-08b. A register of inward EWBs not acted on.

**Acceptance:**
- An inward entry with valid-until in the past shows the warning and records who overrode it.
- Turning back an entry with an EWB number creates the task due at generation + 72 h. Recording the portal reference closes it.
- The overdue-task tile lists tasks past their deadline.

**Evidence:** Accept or reject within validity or 72 h, whichever is earlier; deemed accepted otherwise ([GST Council PIB](https://gstcouncil.gov.in/sites/default/files/2024-10/22.26th_gst_press_information_bureau.pdf), [Tally](https://tallysolutions.com/gst/how-to-track-reject-eway-bills/)). Validity: 1 day / 200 km (Rule 138(10)) ([cleartax](https://cleartax.in/s/gst-eway-bill-validity-distance)). Plan: FR-508 / FR-516 / GTE-T1-01 store `eway_bill_no` only. `72 hours` has 0 hits in the design set. GTE-T1-03 turn-back does nothing else.

**Global setting:** `WAREHOUSE_INDIA_INWARD_EWB_EXPIRED_POLICY` default=WARN alternatives=BLOCK,OFF
