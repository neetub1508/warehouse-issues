# Warehouse findings W72–W73: implementation order and dependency register

Scope: W72–W73 in warehouse-issues only. Dependency meanings, waves and the release rule are those of [FINDINGS-DEPENDENCIES-2026-10-01.md](FINDINGS-DEPENDENCIES-2026-10-01.md); they are not restated.

## Order

User order 2026-10-23: **P7 first**, then the rest. W73's scanners read files `P7` removes or renames, so it runs after `P7`. W72 touches no `P7` file and can start once its scope decision is recorded.

| Finding / issue | Wave | Start handoffs | Completion evidence | Setup, decision or external prerequisite |
|---|---|---|---|---|
| [W72 / #606](https://github.com/neetub1508/warehouse-issues/issues/606) | 2 | None identified | Task acceptance / applicable handoffs | Product decision first: does `OD-17`'s GS1 deferral (#121) extend to counterfeit control (`FR-455`)? Build it, or record the deferral and amend the FRD. |
| [W73 / #607](https://github.com/neetub1508/warehouse-issues/issues/607) | 0 | Reopened `HelpButton` items #17, #130, #71 (baseline only) | Task acceptance / applicable handoffs | Runs after `P7` (#545). Set the ratchet baseline after the three reopened `HelpButton` items land, or at today's count and ratchet down. |

Maintain this register whenever dependencies change.
