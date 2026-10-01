# Warehouse execution-flow acceptance matrix

These are required acceptance targets for the selected package, **not newly executed PASS claims**. Existing implementation and earlier issue evidence can satisfy a row only with an identifiable current result.

| Flow | Findings | Evidence required to close |
|---|---|---|
| Install and activate | W32 W39 W40 | Clean standalone install, optional-module activation, upgrade, seed/role/menu health; no missing-bean failure. |
| Site/owner/item setup | W04 W05 W44 W45 W71 | Create masters and required associations through UI; effective dates, invalid setups and per-site sourcing behave consistently. |
| Import and opening stock | W41 W42 W43 W51 W55 | Validate/apply/retry/reverse, duplicates, large batches, role handoff and independent quantity/value tie-out. |
| Purchase and receipt | W03 W08 W35 W71 | Partial/over/foreign-currency receipt, duplicate submission, lot/serial/UOM and receipt evidence. |
| QC and putaway | W02 W44 W50 | Accept/reject/quarantine, optional-zone rule, capacity, stock status and concurrent completion. |
| Locations and ad hoc moves | W14 W50 | Scoped bin movement with lot/serial/LPN identity and balanced ledger; reversal and capacity refusal. |
| Reservation and allocation | W34 W49 W50 | Concurrent orders cannot over-allocate; expiry, hold, cancellation and supersession preserve requested/fulfilled lineage. |
| Pick and operational replenishment | W15 W16 W17 W18 W65 | Short pick raises task; source shortage, priority, partial workflow and eligible operator are explicit. |
| Pack and evidence | W13 W38 | Correct carton/LPN identity, seal/reopen policy, evidence cannot disappear, reprints do not duplicate stock. |
| Dispatch and carrier lifecycle | W47 W63 | One dispatch, usable tracking number, delayed/duplicate callback, delivery, cancel/void and charges reconcile. |
| Returns and RMA | W08 W12 W68 | Expired RMA, matching origin, partial return, QC outcome, cost lineage and weighing behavior. |
| Inter-site transfers | W08 W49 W50 | Dispatch/in-transit/partial receipt/loss/reversal, narrow receiving permissions and source valuation preserved. |
| Counts and adjustment | W34 W50 | Blind counts, concurrent movement, recount, approval, variance and reversal with independent ledger check. |
| Expiry/holds/recall | W21 W31 W50 | Site-date boundaries, hold/release precedence, lot/serial traceability and scheduled-job retry. |
| Valuation and period close | W01 W06 W07 W08 W09 W22 | Old surviving stock, backdated events, FIFO/average, rounding, policy changes and period refusal. |
| Reports/export/search | W24 W25 W26 W27 W28 W29 W31 W57 W60 W61 | UI/filter/export parity, literal wildcard input, timezone dates, cost masking and scoped scheduled delivery. |
| Tasks and continuity | W19 W20 W65 W66 | Claim races, active eligible assignment, completion signaling, blocked alerts and controlled paper catch-up. |
| Permissions and evidence | W13 W49 W71 | Cross-site/owner direct IDs, exports, attachments, public links, revoked grants and cost visibility. |
| Backup and incident recovery | W33 W52 W54 | Isolated restore of DB and objects, ledger/hash/value tie-out, outbox reconciliation and measured recovery time. |
| Performance and topology | W22 W23 W41 W53 | Reference data size and concurrency; report load, imports, replica routing, DB locks and resource limits. |
| 3PL billing/client lifecycle | W48 W64 | Full independent bill, rates/storage days, retries, credits, offboarding and client isolation. |
| India optional workflows | W45 W47 W69 W70 | Provider sandbox, document issuance/print history, concurrent cancel/dispatch, ambiguous response and dates. |
| Barcode and supported web UX | W36 W37 W38 W56 W67 | Real browser/scanner/printer network, keyboard use, error recovery, readable labels and truthful GS1 limits. |
| Release gates | W34 W35 W36 W39 W60 W61 W62 | Backend plus actual database tests, repaired frontend gate, type/build checks and complete operator journeys. |

## Closure discipline

For each applicable finding, record an owner, supported configuration, commit, fixture/data scale, role, executed steps, expected/actual result and evidence link. Separate code repair from runtime verification. Accept a limitation only when the customer/package explicitly allows it. A closed issue, matching class name or green architecture test alone is insufficient.
