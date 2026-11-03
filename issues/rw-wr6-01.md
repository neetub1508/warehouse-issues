TITLE: [Warehouse] [Finding] Real-world WR6-01 · Generate challans and e-way bills for client stock under the client's GSTIN
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-india
issue: 751
---
Part of #8 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **blocker** · Finding type **MISSING-TASK** · Related: #68, #48, #684 · Source: real-world gap check 2026-11-03, lane WR6

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

When a 3PL ships client goods, the supplier in law is the client, registered at that warehouse. A challan or e-way bill showing the 3PL's own GSTIN as consignor names the wrong supplier. At a roadside check the goods can be detained, and the client's GSTR-1 will not match the e-way bill.

## Scope

Add an owner-aware consignor resolution on challan and e-way bill. For `owner_type` = 3PL client, the bill-from is the client's GSTIN registered at the warehouse's state (from `wh3_client_gst_registrations`, read through a base SPI, never a whin→wh3 edge). Dispatch-from is the warehouse address, and the transaction type is Bill-From/Dispatch-From. Support three generation modes. Refuse a challan/EWB on the operator GSTIN for non-OWN stock.

## Acceptance

- Shipping client X's stock from site S produces an EWB payload with fromGstin = X's GSTIN for S's state, and dispatch-from = S's address.
- With no active registration of X covering S, the request is refused (422 CLIENT_REGISTRATION_MISSING) and nothing is sent.
- OWN stock still uses the operator's GSTIN profile (regression).
- In mode CLIENT_GENERATES, the dispatch accepts an evidence EWB number against the client GSTIN and validates it, without calling the gateway.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

The client is the supplier from that place (CBIC letter dt 25-09-2025, https://taxguru.in/goods-and-service-tax/cbic-clarifies-place-supply-rules-goods-stored-third-party-warehouses.html). The portal's Bill-From/Dispatch-From type exists for exactly this case: https://www.zoho.com/in/books/kb/e-invoicing/transaction-type-in-eway-bills.html. Plan and code: `WhinGstinProfile` has only `company_id` (the operator), and `WhinDeliveryChallanService.java:207` reads "The recipient is our OWN site: its registered branch's current GSTIN". Grepping `client.{0,30}e-way|on behalf of the client` across issues/ and INDIA pack returns nothing. Only p4-10:123 touches this, and it says "client's GSTIN is never confused with the warehouse's own", with no consignor rule.

## Global setting

`WAREHOUSE_3PL_CLIENT_EWAY_MODE` default=CLIENT_GENERATES_EVIDENCE alternatives=OPERATOR_VIA_CLIENT_CREDENTIALS, OPERATOR_PART_B_AS_TRANSPORTER

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#68
