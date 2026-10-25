# R33 run decisions — DECISION RULE (user, 2026-10-25)

Every open question the R33 run settled without the owner, per `classic/.claude/tasks/DECISION-RULE-WAREHOUSE.md`.
One row per question. Full reasoning and sources are in the issue comment named in the last column.

| Date | Issue | Question | Decision | Setting (key · default) | Record |
|---|---|---|---|---|---|
| 2026-10-25 | #33 P1-03 G7 | Item save refuses an HSN not in the tax master (F-R32CA-025): when, and switchable? | Refuse on create / HSN change / type now purchasable-saleable only; blank passes; import rows same; reversal exempt; longest-prefix HSN, SAC for `99*` | `warehouse.item.hsn_must_resolve` · `true` (V500602, base) | #33 `R32 DECISION — #33 G7` |
| 2026-10-25 | #110 P0-14 D1 | How the example adapter consumes a hold through the port | Port carries a consumed-hold reference (b) — filed as a P0-08 #71 follow-up; P0-14 builds reserve + release + subscribe now | no setting — single answer | #110 `R32 DECISION — #110 D1–D3` |
| 2026-10-25 | #110 P0-14 D2 | Which movement carries the consumption | The fixture's own reversal (one movement type) | no setting — single answer | #110 |
| 2026-10-25 | #110 P0-14 D3 | IN_PROCESS subscription by migration or API | Seeded by the fixture's V525020 migration; fixture ArchitectureInvariantsTest allows that INSERT only | no setting — single answer | #110 |
| 2026-10-25 | #28 P3-05 F1 | Does the ASN drive pre-allocation? | Build ASN-line → demand pre-allocation claims, converted to a cross-dock plan at GRN post (contract `RQP-DIV-02` FIX-CODE) | `warehouse.receiving.asn_pre_allocation_enabled` · `true` (warehouse band; `false` = receipt-backed cross-dock only) | #28 `R32 DECISION — #28 F1` |
| 2026-10-25 | #29 P2-03 D1 | Source of a lot's supplier for mass hold | Union: posted GRN supplier ∪ current lot SUPPLIER party | no setting — single answer | #29 `R32 DECISION — #29 D1–D4` |
| 2026-10-25 | #29 P2-03 D2 | Which date the range filters | Matching posted receipt's `received_at`; `whb_lots.receipt_date` only for lots with no receipt | no setting — single answer | #29 |
| 2026-10-25 | #29 P2-03 D3 | Scopes accepting a selector | LOT and ITEM; others 422 `HOLD_SELECTOR_SCOPE_UNSUPPORTED` | no setting — single answer | #29 |
| 2026-10-25 | #29 P2-03 D4 | Preview or resolve at submit | Preview (`GET /holds/mass/subjects`), then the unchanged `POST /mass` | no setting — single answer (additive) | #29 |
| 2026-10-25 | #606 W72 G6 | Receipt with no source row / no supplier: suspect or not? | Two legitimate answers → setting | `warehouse.receiving.unlisted_source_treatment` · `NOT_SUSPECT` (warehouse band) | #606 `PRE-BUILD FUNCTIONAL REVIEW — #606` |
| 2026-10-25 | #606 W72 | Target status / scope / flag default | New `SUSPECT` stock status + disposition; all items; `is_authorised_source` DEFAULT true | no setting — single answer | #606 |
| 2026-10-25 | #14 P3-02 D1–D7 | Putaway capacity enforcement shape | Five FBL-GRD-14 measures; mode read at Complete and stored; missing measure skipped and audited; per-location advisory lock; own WARN reason; `409 LOCATION_CAPACITY_EXCEEDED` | `warehouse.putaway.capacity_enforcement` · `BLOCK` (per-site override `whb_warehouses.putaway_capacity_enforcement`, NULL = inherit) | #14 `PRE-BUILD FUNCTIONAL REVIEW — #14` |
| 2026-10-25 | #53 P2-07 | Settings switch for the supersession-inclusive availability view? | No — opt-in parameter + default-off filter leave today's screens unchanged | no setting — single answer | #53 `PRE-BUILD FUNCTIONAL REVIEW — #53` |
