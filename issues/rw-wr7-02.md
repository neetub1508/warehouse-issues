TITLE: [Warehouse] [Finding] Real-world WR7-02 · Let dispatch proceed without Part B for in-state hauls up to 50 km
LABELS: task,warehouse,gap-real-world,phase-p2,warehouse-india
issue: 763
---
Part of #5 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **PLANNED-WRONG** · Related: #147, #82 · Source: real-world gap check 2026-11-03, lane WR7

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

A factory handing goods to a transporter's local hub, or a godown 30 km away in the same State, legally needs no vehicle details on the e-way bill. Our gate blocks the truck until someone invents a Part B, so either the gate is bypassed or wrong data is filed. A weighbridge trip under a challan needs no e-way bill at all.

## Scope

The dispatch guard accepts Part A only when the movement is intra-state, `distance_km ≤` the dated threshold, and the consignee leg is a transporter location (a transporter counterparty role or a transport-hub address). The gate pass records "Part B exempt, r.138(3)". Add a `WEIGHBRIDGE` movement purpose that needs only a challan within the dated distance. Both limits are seed rows, not constants.

## Acceptance

- Intra-state, 42 km, to the transporter's hub: the gate pass issues without Part B and prints the exemption
- Intra-state, 60 km: refused, naming Part B
- Inter-state at any distance: refused without Part B
- A weighbridge round trip within 20 km issues on a challan with no e-way bill

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

[R138] r.138(3) proviso exempts Part B "where the goods are transported for a distance of up to fifty kilometers within the State" from the consignor to the transporter, and the reverse. r.138(14) exempts the weighbridge trip of up to 20 km with a challan. Code: `WhinEwayBillDispatchGuard.java:119-121` refuses unless `PART_B_FILED`. #147 WH-SC-210 asserts the refusal. grep `fifty|50 ?km` in the design set = 0.

## Depends on

#147
