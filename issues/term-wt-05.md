TITLE: [Warehouse] [Finding] Terminology WT-05 · Correct fr/hi meaning drift and untranslated warehouse strings
LABELS: task,warehouse,gap-terminology,phase-p1,warehouse-base
issue: 800
---
Part of #4 · Module **`warehouse-base`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **BUILT-CHANGE** · Related: #139 · Source: terminology review 2026-11-03, lane WT

## Why this task exists

The worst case is Stock on Hand. The fr and hi menus say "available stock" (*Stock disponible*, उपलब्ध स्टॉक), but on-hand and available are different numbers in this ledger (available = on hand − reservations). A Hindi user opening "available stock" sees on-hand and over-promises. Other problems:
- Hindi uses two words for "item": आइटम in 235 strings and वस्तु in 142. The Items section is आइटम and the Items page under it is वस्तुएँ.
- French menus and fields lose their accents (*Categorie*, *Designation*, *Tracabilite*, *Anciennete du stock*).
- STOCK is the adjective *Stocké*.
- Some fr strings are still English ("No goods receipts found").
- 66 menu rows differ from their page title only in fr or hi.

## Scope

i18n fr/hi values and `menu_translations` rows only. No key deleted, and en is unchanged except where WT-01 to WT-04 change it.
- **Stock on Hand:** fr *Stock en magasin*, hi "हाथ में स्टॉक", on both menu and page.
- **Hindi item noun:** one word, "वस्तु", for Item in every warehouse namespace. Keep "आइटम" only where it is part of a code name.
- **French accents:** restored across all warehouse menu translations and fields.
- **STOCK:** fr label aligned with WT-01.
- **Untranslated strings:** every fr/hi value still identical to en is translated, except proper nouns and acronyms (GRN, LPN, HSN, GSTIN, ASN).
- **Menu vs page:** each of the 66 pairs is aligned to one translation.

## Acceptance

- A script comparing `menu_translations` to page `title` keys for all warehouse menus reports 0 mismatches in fr and hi.
- In hi, `item.*`, `itemType.*` and `itemCategory.*` titles and the Items menus all use वस्तु.
- In fr and hi, the Stock on Hand menu and page say on-hand, not available.
- A script listing fr/hi values equal to en (excluding the acronym allowlist) returns 0.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

- **Stock on Hand:** `W/resources/db/migration/V511066__…:281-282` fr 'Stock disponible', hi 'उपलब्ध स्टॉक'.
- **French accents and adjective:** `wb` fr:1476 "Designation", fr:1478 "Categorie", fr:829 STOCK "Stocké".
- **Untranslated fr:** `w` fr:1114 "No goods receipts found".
- **Hindi item noun:** hi `item.title`="वस्तुएँ" vs `itemType.title`="आइटम प्रकार".
- **Menu vs page drift:** listed in CODE-TERMS §2 I-4, M-10, M-13 and M-14 (the 66-row list is `cmp.txt` in the same scratchpad).
- **Real-world source:** the CRA-1 and CARO wording "receipts, issues and balances" and "physical verification" (https://bcajonline.org/journal/caro-2020-series-new-clauses-and-modifications-inventories-and-other-current-assets/).
