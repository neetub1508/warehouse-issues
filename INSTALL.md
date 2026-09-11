# First-day warehouse setup and acceptance

Adopted preimplementation operator workflow. P0-16 owns completion; this is not a claim that software exists.

1. Install platform and warehouse-base; add warehouse for operational screens. Apply only installed modules' assigned migrations. Seed settings idempotently from [the adopted catalogue](docs/GLOBAL-SETTINGS-DECISIONS.md). Optional adapters remain disabled.
2. Create/select the customer company, base currency and business timezone using existing company setup. Reject missing currency/timezone before stock posting. Do not guess INR or the server timezone.
3. Assign warehouse operational roles and branch scope through existing permissions. Separate approver from operator. Confirm a scoped user cannot list another owner's/site's stock.
4. Create the site with one effective registered branch, serving associations as needed, and physical locations. Provision its required virtual locations idempotently, including VALUE_OFFSET. Transit child locations are created per transfer under the source site; never invent an unrestricted shared transit warehouse.
5. Create current and next non-overlapping company stock periods in the company timezone, with explicit dates and open state. Preview existing periods; never duplicate, reopen or overlap them when setup is rerun.
6. Create UoMs/conversions, item types/categories, items, owners, counterparties, lots/serial rules, numbering and effective policies. Default negative stock BLOCK, over-receipt tolerance zero, valuation method weighted average unless an explicit supported FIFO policy is selected. Required identifiers/capabilities must validate before activation.
7. Import opening stock through the existing opening-stock document and single writer. Preview and approve under the existing workflow, retain source references/idempotency keys, and reconcile by owner/item/site and value. Repeating a batch must not double inventory.
8. Execute receipt → QC where applicable → putaway → reserve → pick → dispatch → return, then a count/adjustment and a transfer with receipt. Check ledger balance, reservation release, role refusals, stock-period lock and replay. No provider is required for stock-only standalone operations.
9. Test document printing with internal Code-128 LPN scan round-trip. Set tax/accounting modes explicitly for financial-document workflows; missing provider/evidence must block only the operation requiring it. Enable optional modules after their readiness cases pass.
10. Re-run setup and prove no duplicate seeds/periods, changed historical costs or reopened documents. Demonstrate failed-job recovery, configuration audit and rollback-by-new-revision. Record the existing numbered scenarios and CONFIG-CASE results in the implementation PR.

When a step fails, show the missing field/capability or dependency and link to its existing setup screen. Keep completed setup intact and allow authorized retry. Never compensate by deleting ledger/history or silently weakening a guard.
