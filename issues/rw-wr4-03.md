TITLE: [Warehouse] [Finding] Real-world WR4-03 · Carry the GTA tax character of freight from transporter to bill
LABELS: task,warehouse,gap-real-world,phase-p5
issue: 740
---
Part of #10 · Module **`warehouse (carrier master) + accounting-adapter-warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #73, #39, #131 · Source: real-world gap check 2026-11-03, lane WR4

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Most factory outward freight goes by a goods transport agency that issues an LR. The tax on that freight follows the GTA's own choice:
- Reverse charge at 5%: the company pays and self-invoices, unless the GTA filed Annexure V.
- Forward charge at 5% without ITC, or 18% with ITC.
Without the GTA's status on the carrier, and the freight amount and payer on the shipment, accounting cannot tell whether an RCM liability arises. The usual result is RCM missed in GSTR-3B, which means interest and loss of the matching ITC, or tax paid twice. A 3PL that issues its own LR is itself a GTA and must charge GTA tax on the freight it bills (#39), but the plan gives freight no GST character.

## Scope


- Carrier master gains `is_gta`, a GTA tax option (`RCM_5` / `FCM_5` / `FCM_18`) with effective-from FY, and the Annexure V/VI reference.
- Shipment/handover gains freight amount, payer (consignor / consignee / third party) and whether an LR was issued.
- The handover event to accounting carries these. Accounting decides RCM vs forward charge (reference neetub1508/accounting#47).
- 3PL freight billing (#39) marks freight lines as a GTA supply when the 3PL issued the LR.

## Acceptance

- A ₹12,000 freight on an LR from a GTA with no Annexure V reaches accounting flagged RCM 5%
- The same GTA after an Annexure V option effective 1 Apr 2027 is flagged forward charge for shipments from that date only
- Freight on a to-pay LR (consignee pays) raises no RCM for the consignor
- A 3PL client invoice line for LR-based freight carries the GTA character

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

[GC56] Q60 (5% no ITC or 18% with ITC, after 22 Sep 2025); [GTA-A5] (Annexure V by 31 March of the preceding FY, sticky; Annexure VI to revert). Grep `GTA|goods transport agency` in warehouse-issues/issues = 0, and `gh issue list -R neetub1508/accounting --search "goods transport agency"` = 0. p3-09.md:20 records `lrNumber`, freight terms and declared value only.

## Depends on

#73, neetub1508/accounting#47
