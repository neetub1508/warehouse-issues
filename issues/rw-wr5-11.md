TITLE: [Warehouse] [Finding] Real-world WR5-11 · Produce the monthly stock-insurance declaration per insured location
LABELS: task,warehouse,gap-real-world,phase-p3
issue: 750
---
Part of #7 · Module **`warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **MISSING-TASK** · Related: #136, #690 · Source: real-world gap check 2026-11-03, lane WR5

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Most SME stock is insured on a declaration or floater policy that needs a monthly value per insured location. A late declaration defaults to the full sum insured. Value above the sum insured is uninsured, and the average clause cuts any claim. Accounts now builds this by hand from the godown statement, and nothing warns when a godown's stock exceeds its cover.

## Scope

Policy master (insurer, policy no., type DECLARATION / FLOATER / FIXED, period, sum insured per location or group, declaration basis such as the highest or month-end value at cost). A monthly declaration generated from the as-at valuation (#136), including or excluding consigned-in and 3PL client stock as the policy says, frozen when sent. An alert when location value exceeds the sum insured.

## Acceptance

- The October declaration for godown A equals the WS-211 value at the declared basis and is frozen once sent
- Stock above the sum insured raises one alert naming the location and the shortfall
- 3PL client-owned stock is excluded by default

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

[GI Council, fire insurance](https://www.gicouncil.in/insurance-education/types-of-insurance/fire/); [BimaKavach](https://www.bimakavach.com/blog/what-is-the-impact-damage-in-fire-insurance-what-is-the-stock-declaration-policy/) (practitioner). Grep `declaration polic|insurance declar|sum insured` = 0. #690 covers only 3PL client custody value.

## Global setting

`WAREHOUSE_INSURANCE_DECLARATION_BASIS` default=MONTH_END_COST alternatives=HIGHEST_IN_MONTH_COST|MONTH_END_NRV

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#136
