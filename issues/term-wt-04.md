TITLE: [Warehouse] [Finding] Terminology WT-04 · Say "Supplier" consistently and fix counterparty and owner labels
LABELS: task,warehouse,gap-terminology,phase-p1,warehouse-base
issue: 799
---
Part of #4 · Module **`warehouse-base`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **BUILT-CHANGE** · Related: none · Source: terminology review 2026-11-03, lane WT

## Why this task exists

The UI says "Supplier" everywhere except in four seeded labels: "Return to vendor" (disposition, demand type, return type), "Vendor Rejection" and "Vendor approval pending". A buyer reading a quality register sees two words and wonders whether they mean two parties.
- One code, `CLIENT_3PL`, is "Third-party client" as an owner type but "Third-party logistics client" as a counterparty role.
- "Owner" is both the stock owner (51 grids) and the person who owns a CAPA action.

## Scope

Labels only, in seeded `name` plus i18n en/fr/hi.
- **Vendor wording:**
  - The RTV disposition and the VENDOR_RETURN demand type become "Return to supplier".
  - The VENDOR return type becomes "Return to supplier".
  - "Vendor Rejection" becomes "Supplier Rejection".
  - VENDOR_APPROVAL_PENDING becomes "Supplier approval pending".
- **CLIENT_3PL:** "3PL client" in both lists.
- **CAPA owner:** the CAPA `ownerName` becomes "Action Owner".
- **Counterparty column:** the 11 `counterpartyName` columns use the role word the screen implies (Supplier, Customer, Carrier) or "Party". Never two words for the same column on one screen.

Unchanged: the codes RTV, VENDOR, VENDOR_RETURN and VENDOR_APPROVAL_PENDING. The industry name "Approved Vendor List (AVL)" is out of scope here; see WT-10.

## Acceptance

- `grep -i vendor` over warehouse-base, warehouse and warehouse-india en i18n and seeded names returns only code identifiers and "Approved Vendor List".
- The owner-type and counterparty-role grids both show "3PL client" for `CLIENT_3PL`.
- The CAPA grid column reads "Action Owner".

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

- **Vendor seeds:** `B/resources/db/migration/V500010__…:151` VENDOR_RETURN "Return to vendor", :360 RTV "Return to vendor". `w` en `qualityRegister.tabs.vendorRejection`, `returnReceipt.returnTypes.VENDOR`.
- **CLIENT_3PL:** `V500007:147` "Third-party client" vs `V500011:129` "Third-party logistics client".
- **CAPA owner:** `W/resources/db/migration/V511550__…:313` `wh_capa_actions.ownerName`.
- **Real-world source:** supplier and vendor are interchangeable, so the product should pick one (https://docs.frappe.io/erpnext/user/manual/en/item).
