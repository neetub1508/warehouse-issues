TITLE: [Warehouse] [Finding] Real-world WR4-06 · Model delivery exceptions: refused, partly accepted, re-attempt
LABELS: task,warehouse,gap-real-world,phase-p2
issue: 743
---
Part of #5 · Module **`warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #73, #87, #553, #551, #590, #123 · Source: real-world gap check 2026-11-03, lane WR4

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

B2B deliveries regularly fail:
- The customer refuses the whole truck (wrong item, no PO, unloading closed).
- The customer accepts with POD remarks ("4 cartons short, 2 damaged").
- The carrier re-attempts the next day.
Today a shipment can only be `DISPATCHED` or `DELIVERED`, and P7-03 deleted the refusal reasons along with NDR. So a refused truck reads "delivered" or stays dispatched for ever. The invoice is not reversed, and the customer is billed for goods never received. There is also no outbound carrier-claim trail for transit shortage, which is the basis for both the credit note and the claim on the transporter or insurer.

## Scope


- Shipment states `DELIVERY_FAILED` (reason, re-attempt date) and `REFUSED`, and `DELIVERED` with per-line accepted / short / damaged quantities taken from POD remarks.
- `REFUSED` or short quantity opens the return path (return receipt with `return_type` = refused delivery, P2-12) and an `INVOICE_ADJUSTMENT` proposal to accounting. That proposal is a credit note, or an IRN cancellation if still within 24 h.
- An outbound carrier claim with counterparty carrier or insurer, LR remark, and declaration link (WR4-05 (#742)).
- Optional dispatch-advice e-mail (step 12) carries LR, vehicle, EWB and cartons so the customer can check on arrival.
- Re-seed refusal reasons under a B2B context (not the removed NDR flow).

## Acceptance

- A refused shipment cannot be confirmed delivered; it shows `REFUSED` and creates an expected return
- Delivery confirmed with 4 short cartons records the accepted quantity, proposes a credit note for 4, and opens a carrier claim draft
- A failed attempt with a re-attempt date keeps the EWB extension prompt active (if expiring)
- Billed-vs-delivered reports use the accepted quantity

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

p2-10.md:91 (`DISPATCHED → DELIVERED` only); code `V5…` migration line 287 lists `DISPATCHED, DELIVERED, CANCELLED`; p7-03.md:83 deletes `CUSTOMER_REFUSED`. WR7-03(d) covers only the return challan/EWB, and WR1-06 (#726) only inbound claims. Rule 138 needs a fresh EWB for the return leg [EWBR].

## Depends on

#73, #87
