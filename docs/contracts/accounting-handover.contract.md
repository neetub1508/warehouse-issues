# Functional Contract — Accounting handover: envelope → queue → Stock-to-GL reconciliation

> **What this is.** The functional truth for the warehouse ↔ accounting seam as `P2-18`
> (warehouse-issues#128) completes it: which movements hand over, what one envelope carries, how the
> movement's `handover_id` and `posting_status` follow the envelope, how a rejected handover is worked
> from a **named queue with an owner and an ageing clock** (never a swallowed exception), how the
> install switches between `STANDALONE` and `INTEGRATED`, and what WS-219 Stock-to-GL Reconciliation
> shows. Every row cites its source id so a later gate can check a diff against the row.
>
> **What this is not.** It does not restate `DECISIONS.md`, `DATA-MODEL.md`, the port contract or the
> screen spec — a row points at them. It does not define the accounting side: the receiving columns on
> the accounting source-document port and its de-duplication are the `accounting` repository's
> (`OD-1`, `RF-005`), and that repository is **not edited from here**. It does not cover coding
> standards. Where two sources disagree, the row says so and points at §9; it never picks one silently.
>
> **Status.** **DERIVED 2026-09-19 and ratified 2026-09-19 (v1) by the user, with the 13 `AHO-OPEN-*` rows kept OPEN; P2-18 builds STANDALONE only (OD-1), and FR-244 moves to P1-17, which is built before P2-18.** Derived by `functional-reviewer` in derive
> mode from the design set at `a424481` and from what is already built in `classic`: `P0-12`'s seam
> (`V500042`; code contract `classic` `warehouse-base/docs/contracts/accounting-handover.contract.md`,
> rows `ACC-*`, last amended at `fa1329c83a`), `P2-22`'s queue overlay (`V501071`), `P2-17`'s
> value-only movements and `P1-20`'s `warehouse.accounting.mode` setting (`V511200`). A row marked
> **BUILT** is read off code; **TO BUILD** is `P2-18`'s obligation; **TBD** is a cell no source
> answers; **EXTERNAL** is another repository's work. `AHO-OPEN-nn` points at §9. **Nothing in §9 is
> answered here** — each open row names its sources and waits for a person.

---

## 0. Identity

| | |
|---|---|
| **Workflow** | A posting-relevant movement takes ledger effect → the single writer calls the emitter in the same transaction → **one** envelope `PENDING` and the movement's `posting_status = PENDING` → the dispatcher hands it to the installed sink → `POSTED` / `REJECTED` / `DISCARDED` → a rejection is worked on WS-052 (Retry, Void) → the period's values are reconciled on WS-219 against the GL control-account balance read through `GlBalanceProvider` |
| **Module** | `warehouse-base` (`ai.warehousebase`: the seam, the queue, the `GlBalanceProvider` port — declared, never implemented there) + `warehouse` (`ai.warehouse`: WS-219, an `app` report, BUILD-SPEC §1 row WS-219) |
| **Domain baseline** | `docs/DECISIONS.md` `D-6`, `D-7`, `OD-1` (**RESOLVED 2026-09-11**, §3), `OD-16`, `L-8`, `L-9`, `L-13`, `L-14` · `docs/GLOBAL-SETTINGS-DECISIONS.md` `warehouse.accounting.mode`, `CONFIG-CASE-07`, `CONFIG-CASE-10` · `docs/DATA-MODEL.md` §2.1.11 (`whb_accounting_handovers`), §7 note 4 (report grid identifiers) · `docs/BUILD-SPEC-SCREENS.md` WS-051, WS-052, §7 WS-219, §10.2 · `docs/SCENARIO-CATALOGUE.md` `WH-SC-049`, `WH-SC-128`, `WH-SC-156`…`WH-SC-159`, `WH-SC-162`, `WH-SC-163`, `WH-SC-166` · `docs/GAP-REGISTER-R3.md` `RC-001`, `RC-002`, `RC-006`, `RF-005` · `docs/GAP-REGISTER-R4.md` `RJ-011` · `RL-002`, `RG-001`, `RG-005`, `IRR-41` |
| **Owning task bodies** | `issues/p2-18.md` (this workflow). Built predecessors it must not break: `issues/p0-12.md` (seam, WS-051, WS-052), `issues/p2-22.md` (queue owner, age, alert), `issues/p2-17.md` (value-only movements), `issues/p1-20.md` (the mode setting and its capability gate). Hand-offs in: `P0-12`'s `OPEN-03`…`OPEN-07` (§9) |
| **Primary table(s)** | `whb_accounting_handovers`, `whb_gl_posting_rules` (`V500042`; `alert_raised_at` `V501071`); writes `whb_stock_movements.posting_status` and `.handover_id` (`V500030`, `IRR-41`) through one writer. WS-219 reads `whb_stock_movements`, `whb_stock_movement_lines`, `whb_stock_periods` and `whb_accounting_handovers`; it owns **no table** (`DATA-MODEL.md` §7 note 4). **`P2-18` writes no DDL** (p2-18 Scope) |
| **Status columns** | `whb_accounting_handovers.status` — DB `CHECK` on `PENDING`, `SENT`, `POSTED`, `REJECTED`, `BLOCKED`, `DISCARDED`, `VOIDED` (`V500042`, line 185). `whb_stock_movements.posting_status` — `VARCHAR(20) NOT NULL DEFAULT 'NOT_APPLICABLE'`, **no `CHECK`** (`V500030`, line 244); vocabulary `NOT_APPLICABLE`/`PENDING`/`POSTED`/`REJECTED`/`BLOCKED`/`DISCARDED` (`movement-post-reverse.contract.md` §1.1 note). `FR-232` and `D-6` still list four values (`AHO-OPEN-12`) |
| **Permission resources** | `whb_accounting_handovers:view` · `:export` · `:retry` · `:void` (`V500042`; `:void` also `P0-15`'s `V501000`) · `whb_gl_posting_rules:view` · `:create` · `:edit` · `:export` · WS-219: `wh_rpt_stock_to_gl:view` · `:export` — **TBD, not seeded anywhere** (§10.1's `<table>:action` shape read onto the grid identifier, as `P2-05` did for `wh_rpt_expiry`; `AHO-OPEN-09`) |
| **Routes** | web: `/warehouse/platform/handovers` (WS-052, API `/warehouse/platform/handovers`, **BUILT**), `/warehouse/masters/gl-posting-rules` (WS-051, **BUILT**), `/warehouse/reports/stock-to-gl` (WS-219, **TO BUILD**), drill target `/warehouse/reports/movement-register` (WS-209, `P2-20`'s, **not built**) · **mobile: none** — a finance-desk report and queue; stated as a decision (p2-18 Scope *Mobile*, `FR-218`) and by the user scope rule of 2026-09-11 (warehouse ships no mobile app) |
| **Requirement source** | `issues/p2-18.md` at `warehouse-issues` `main` `a424481` |
| **Contract status** | `RATIFIED v1 — 2026-09-19` (13 OPEN rows kept OPEN) |
| **Contract version** | `v0 — 2026-09-19` |

### Acceptance checks

| # | The requester expects… (`p2-18.md` Acceptance) | Delivered by | State |
|---|---|---|---|
| A1 | `CONFIG-CASE-07`: enabling `INTEGRATED` without the capability is refused with the missing-capability list; disabling with work pending pauses delivery and keeps every envelope | `AHO-GRD-01`, `AHO-GRD-02`, `AHO-T1-11` | BUILT (`WhbAccountingMode`, `P1-20`) |
| A2 | `CONFIG-CASE-10`: a zero-bailment movement has no valued envelope; a duplicate acknowledgement neither resends nor re-costs | `AHO-ENV-05`, `AHO-T1-05`, `AHO-GRD-10` | BUILT |
| A3 | The adapter installing the sink declares `enable.warehouse.accounting_sink=true`; boot fails when the declared capability and the installed sink disagree | `AHO-GRD-02` | BUILT in base (`WhbAccountingMode` `@PostConstruct`); the adapter itself is `AHO-OPEN-01` |
| A4 | One despatch produces **one** envelope through accounting's existing port, with the classification quad and the warehouse's values (`WH-SC-156`) | `AHO-T1-01`, `AHO-ENV-01`…`-08` | BUILT for the quad and values; `duty_status`, lot/serial identity and `exchange_rate` are **not in `WhbAccountingEnvelopeV1`** (`AHO-ENV-03`, `AHO-OPEN-02`) |
| A5 | No `acc_*` reference and no `ai.accounting*` import under `ai.warehouse*`, enforced by a build-failing test (`WH-SC-162`) | `AHO-UNR-01` | BUILT (`WhbAccountingSeamContractTest`) |
| A6 | A rejection sets `posting_status = REJECTED`, fills code and message, and appears on a queue **with an owner and an age** (`WH-SC-158`) | `AHO-T1-05`, `AHO-X-01`, `AHO-T3-04`, §5.1 | BUILT (`P0-12`, `P2-22`); the owner's meaning is `AHO-OPEN-08` |
| A7 | A retry with the same key posts nothing and returns the original | `AHO-GRD-03`, `AHO-T1-06` | warehouse half BUILT; the consumer's row count is EXTERNAL (`AHO-OPEN-01`) |
| A8 | `owner_type != OWN` hands over quantity and custody only, `ZERO_BAILMENT`, no value (`L-14`) | `AHO-ENV-05`, `AHO-ENV-06` | BUILT, but the two sources disagree on whether a custody envelope is emitted at all (`AHO-OPEN-03`) |
| A9 | WS-219's five-term identity balances per site, owner and item group; the variance drills to the movements (`WH-SC-159`) | `AHO-RPT-01`…`-06`, §5.2 | TO BUILD |
| A10 | On Mode A the report renders, with an explained empty GL column | `AHO-RPT-04` | TO BUILD |
| A11 | Opening stock appears as `OPENING_BALANCE` movements, not an unexplained opening figure (`WH-SC-049`) | `AHO-RPT-02` | TO BUILD; bucket mapping `AHO-OPEN-05` |
| A12 | The inter-branch transfer stores **two** numbers, with elimination data (`FR-244`) | `AHO-X-06` | **blocked** — `wh_transfer_orders` does not exist; `P1-17` is sequenced after `P2-18` (`AHO-OPEN-06`) |
| A13 | The envelope's `branch` is the site's `REGISTERED` branch at `occurred_at`, inside the hash (`RG-001`) | `AHO-ENV-04` | BUILT |
| A14 | Every handover carries `envelope_version`, covered by the hash (`RL-002`) | `AHO-ENV-01` | BUILT |
| A15 | `REJECTED → VOIDED` needs `:void`, approver ≠ requester, only for a reversed or `NOT_APPLICABLE` movement; `VOIDED` does not block close; reversing a never-posted movement voids both (`RJ-011`) | `AHO-T1-07`, `AHO-T1-08`, `AHO-GRD-05`…`-07`, `AHO-X-02` | BUILT for "reversed"; the `NOT_APPLICABLE` branch has no transition (`AHO-OPEN-04`) |
| A16 | WS-219 carries `ownerName`, `itemCategoryName`, `glControlAccountBalance` from a `GlBalanceProvider` declared in base with no implementation there; Mode A reads *"no accounting module installed"* (`RC-002`) | `AHO-RPT-03`, `AHO-RPT-04`, `AHO-UNR-06` | TO BUILD; BUILD-SPEC §7 row not yet amended (`AHO-OPEN-10`) |
| A17 | `difference` drills to WS-209 filtered to period × site × owner × item group (`RC-002`) | `AHO-RPT-05` | TO BUILD; WS-209 is unbuilt and has no period or item-group filter (`AHO-OPEN-07`) |
| A18 | WS-219 names `posting_date` as its clock on screen and in the footer (`RC-001`) | `AHO-RPT-01` | TO BUILD |
| A19 | An AVCO issue whose extended value is not `round(quantity × unit_cost, 4)` arrives with the warehouse's value to the paisa; each line's `movement_date` is the `posting_date` (`RF-005`) | `AHO-ENV-07`, `AHO-UNR-03` | warehouse half BUILT (value travels as stored text); the receiving columns are EXTERNAL (`AHO-OPEN-01`) |
| A20 | The export of a filtered, sorted WS-219 reproduces that filter and sort (`FR-400`, `P2-29`) | §5.2 *Export* | TO BUILD |

---

## 1. T1 — State machine

The lifecycle belongs to the **handover row**; the movement mirrors it in `posting_status`. The stock
movement itself is never changed by any outcome here (`WH-SC-158`: *"the physical truth is not
reversed because a downstream ledger declined it"*).

### 1.1 Status inventory — `whb_accounting_handovers.status`

| Status | Movement `posting_status` | Reachable via | Exits via | Kind | Blocks stock-period close |
|---|---|---|---|---|---|
| *(no row)* | `NOT_APPLICABLE` | default; `STANDALONE` post; non-financial type; all lines `ZERO_BAILMENT` | `AHO-T1-01` (only when `INTEGRATED`) | — | no |
| `PENDING` | `PENDING` | `AHO-T1-01`, `-02`, `-04`, `-06` | `AHO-T1-03`; `AHO-T1-08` | active | **yes** |
| `SENT` | `PENDING` | `AHO-T1-03` | `AHO-T1-04`, `-05`; stale re-claim `AHO-T3-02` | active | **yes** |
| `POSTED` | `POSTED` | `AHO-T1-05` | none | **terminal** | no |
| `REJECTED` | `REJECTED` | `AHO-T1-05` | `AHO-T1-06`, `-07` | active — **the rejected-handover queue** | **yes** |
| `BLOCKED` | `BLOCKED` | `AHO-T1-01` (reversal of an in-flight original); `AHO-T1-08` | `AHO-T1-02`, `-07` | active | **yes** |
| `DISCARDED` | `DISCARDED` | `AHO-T1-05` | none | **terminal** — the counterpart declined for good | no |
| `VOIDED` | `NOT_APPLICABLE` | `AHO-T1-07`, `-08` | none | **terminal**, never deleted (`RJ-011`) | no |

`SUPERSEDED` is not in the `CHECK` and no v1 transition reaches it (`P0-12` `DEC-02`, `RJ-004`).
`DATA-MODEL.md` §2.1.11 lists five of the seven built statuses and none of the `BLOCKED`/`VOIDED`
companion columns (`AHO-OPEN-12`).

### 1.2 Transitions

| ID | From | Event / action | To | Guard (service, first) | Actor (permission) | Side effects | Reason required | UI entry point |
|---|---|---|---|---|---|---|---|---|
| AHO-T1-01 | *(no row)* | Emit. `WhbAccountingHandoverEmitter.emit(movementId, occurredAt, actorId)` inside the writer's posting transaction, after every accepted non-replayed post and when an approval takes effect (`MPR-T4-08`) | `PENDING`; `BLOCKED` when the original is in flight; born `VOIDED` under `AHO-T1-08` | `AHO-GRD-01` (INTEGRATED); movement type `is_financial`; `approval_status` null or `APPROVED`; not every line `ZERO_BAILMENT` (`AHO-ENV-05`); no row yet for (`movement_id`, `occurred_at`) — else the existing id is returned | system (the posting actor is stamped `created_by` = requester) | `AHO-X-01` (`handover_id`, `posting_status`); payload, `payload_hash`, key, `envelope_version` stored. **One envelope per movement** (`FR-233`, `WH-SC-156`). BUILT (`ACC-T1-01`) | no | none — a side effect of every post (WS-040, the port, document screens) |
| AHO-T1-02 | `BLOCKED` | Release: the original's `POSTED` acknowledgement, or the release sweep (`AHO-T3-03`) | `PENDING` | row still `BLOCKED` **and** predecessor `POSTED`, both re-checked in the one `UPDATE` | system | `AHO-X-01` (`BLOCKED` → `PENDING`). BUILT (`ACC-T1-02`) | no | none |
| AHO-T1-03 | `PENDING` | Dispatcher claim (`AHO-T3-01`) | `SENT` | `FOR UPDATE SKIP LOCKED`; INTEGRATED | system | `attempt_count` +1, `last_attempt_at` = now. BUILT (`ACC-T1-03`) | no | none |
| AHO-T1-04 | `SENT` | The sink throws (transport failure) | `PENDING` | row still `SENT` | system | due again with the **same** key and payload. BUILT (`ACC-T1-04`) | no | none |
| AHO-T1-05 | `SENT` | The sink's acknowledgement | `POSTED` / `REJECTED` / `DISCARDED` | row still `SENT` (a late duplicate acknowledgement is inert, `CONFIG-CASE-10`); `AHO-GRD-10`; a stored payload that does not parse at its version → `REJECTED ENVELOPE_UNREADABLE` unsent; a reversed original with no live reversal envelope → `REJECTED REVERSAL_NOT_HANDED_OVER` unsent (`AHO-GRD-08`) | system (the sink) | `AHO-X-01`; `POSTED` stores `external_document_ref`, clears rejection fields and releases successors (`AHO-T1-02`); `REJECTED` stores `rejection_code` + `rejection_message` and joins the queue and its alert episode (`AHO-T3-04`). **The stock movement is untouched** (`WH-SC-158`). BUILT (`ACC-T1-05`) | no | none; the outcome shows on WS-052 and WS-041 *Handover* tab |
| AHO-T1-06 | `REJECTED` | **Retry** | `PENDING` | `AHO-GRD-04` (version), `AHO-GRD-09` (status `REJECTED`), `AHO-GRD-08` (reversal closed), `AHO-GRD-11` (INTEGRATED) | `whb_accounting_handovers:retry` | same key, same stored payload (**never re-resolves posting rules**, `RG-005`); last rejection kept; `AHO-X-01`; audit `WHB_ACCOUNTING_HANDOVER_RETRIED`. BUILT (`ACC-T1-06`) | no | WS-052 row action **Retry** |
| AHO-T1-07 | `REJECTED` / `BLOCKED` | **Void** | `VOIDED` | `AHO-GRD-04`, `AHO-GRD-05`, `AHO-GRD-06`, `AHO-GRD-07`, `AHO-GRD-09` | `whb_accounting_handovers:void`, **approver ≠ requester** (`FR-408`) | `voided_at`, `voided_by`, `void_reason` stamped; movement → `NOT_APPLICABLE`; every `BLOCKED` successor voided with it; leaves the queue count, the age and the alert (`AHO-T3-04`); audit `WHB_ACCOUNTING_HANDOVER_VOIDED`. BUILT (`ACC-T1-07`) | **yes** — `reason`, 5–1000 characters | WS-052 row action **Void** (own modal) |
| AHO-T1-08 | original `PENDING` / `REJECTED` / `BLOCKED` | Reversal of a movement whose envelope never posted (`RJ-011`) | original `VOIDED`; the reversal's envelope born `VOIDED` | a reversing actor exists; the original is still unsent (a row just claimed makes the reversal `BLOCKED` instead) | **system void** — not an approval, so no `:void` and no `AHO-GRD-05` | both movements → `NOT_APPLICABLE`; `voided_by` = the reversing actor; `void_reason` names both movements. **No second envelope enters the queue** (p2-18 Scope). BUILT (`ACC-T1-08`) | no | none — WS-040 *Reverse* causes it |
| AHO-T1-09 | *(no row)* | Reversal of a movement posted while `STANDALONE`, posted after the switch to `INTEGRATED` | `PENDING` (no predecessor) | as `AHO-T1-01` | system | dispatched like any envelope although accounting never received the original. BUILT as stated; **whether it should emit at all is `AHO-OPEN-11`** (`P0-12` `OPEN-05`) | no | none |
| AHO-T1-10 | a reversal's envelope `REJECTED` | The counterpart refuses the reversal envelope | stays `REJECTED` until Retry succeeds or the counterpart answers `DISCARDED` | Void refused by design — the reversal cannot itself be reversed (`MPR-T2-04`), so `AHO-GRD-06` never passes | system / `:retry` | a rejection caused by the stored payload (a wrong rule) has **no warehouse-side exit** (`AHO-OPEN-11`, `P0-12` `OPEN-06`). BUILT (`ACC-T1-10`) | no | WS-052 **Retry** only |
| AHO-T1-11 | any | Mode switch — `warehouse.accounting.mode`, or the sink bean appearing / disappearing | unchanged rows | `AHO-GRD-01`, `AHO-GRD-02` | install configuration (`P1-20` settings screen) | **INTEGRATED → STANDALONE:** new posts stay `NOT_APPLICABLE`; `PENDING`/`SENT`/`REJECTED`/`BLOCKED` rows **are kept for reconciliation** and keep blocking close; dispatch and release pause; Retry refused (`AHO-GRD-11`); Void stays available. **STANDALONE → INTEGRATED:** nothing back-fills movements posted while standalone (`CONFIG-CASE-07`, `GLOBAL-SETTINGS-DECISIONS.md` `warehouse.accounting.mode`). BUILT (`ACC-T1-09`) | no | Admin settings, Warehouse tab |

### 1.3 Guards — the predicate, the refusal, and where it lands

Every WS-052 verb answers in the house envelope `{ "error", "details": { "errors": { "<field>": "<message>" } } }`.
The DB `CHECK`s on `whb_accounting_handovers` are the backstop only.

| ID | Predicate (must hold to proceed) | Refusal: HTTP · code · field | Message shape | DB backstop | Source |
|---|---|---|---|---|---|
| AHO-GRD-01 | **INTEGRATED** = setting `warehouse.accounting.mode = INTEGRATED` **and** exactly one `WhbAccountingHandoverSink` bean. Absent or unknown setting = `STANDALONE` (default). A setting row written straight into the DB as `INTEGRATED` with no sink runs `STANDALONE`, warned — **stock posting is never blocked by a missing capability** | none at post: nothing is queued and `posting_status` keeps `NOT_APPLICABLE` | log warning names the setting | — | `OD-1` (RESOLVED 2026-09-11), `D-7`, `CONFIG-CASE-07`; `WhbAccountingMode` (`ACC-GRD-02`) |
| AHO-GRD-02 | Activation: `INTEGRATED` is saved only when the capability `enable.warehouse.accounting_sink` is declared; the declaration and the installed sink are **one fact**, reconciled once at boot | settings save refused with the missing-capability list (`P1-20`); **boot fails** (`IllegalStateException`) when declaration and sink disagree in either direction | names the property and the bean | — | p2-18 Acceptance (`P1-20` C6 fix 2), `V511200` `valueCapabilities`, `CONFIG-CASE-07` |
| AHO-GRD-03 | **Idempotent by construction.** Key = `WHB-ACC:<source_system>:<movement idempotency_key>` — derived, **never minted** (`L-9`); every attempt sends the stored payload and key unchanged; the sink de-duplicates on the key and a repeat returns the original acknowledgement and posts nothing | — | — | `uk(idempotency_key)`; `uk(movement_id, occurred_at)` | `L-9`, `FR-233`, p2-18 Traps; `ACC-GRD-01` |
| AHO-GRD-04 | Optimistic version on Retry and Void (`?version=`); both verbs lock the original handover row, then the row acted on | `400` · `version` | stale-version message | `@Version` | `ACC-GRD-08` |
| AHO-GRD-05 | Void approver ≠ requester (`created_by`), for the row and every `BLOCKED` successor voided with it | `422 HANDOVER_VOID_BY_REQUESTER` | names the requester | — | `FR-408`, `RJ-011`; `ACC-GRD-03` |
| AHO-GRD-06 | Void of `REJECTED`: the movement `is_reversed`. **The "or reclassified `NOT_APPLICABLE`" branch of `RJ-011` has no v1 transition and is not built** | `422 HANDOVER_VOID_MOVEMENT_STANDS` | names the movement | — | `RJ-011`, `ACC-GRD-04`; `AHO-OPEN-04` |
| AHO-GRD-07 | Void of `BLOCKED`: the predecessor is `REJECTED`, `DISCARDED` or `VOIDED`; void reason 5–1000 characters, trimmed | `422 HANDOVER_VOID_PREDECESSOR_IN_FLIGHT`; `400` · `reason` | — | `VOIDED` ⇔ `voided_at` ⇔ `voided_by` ⇔ `void_reason` `CHECK` | `ACC-GRD-05`, `ACC-GRD-06` |
| AHO-GRD-08 | An original never posts once its movement was reversed (with ledger effect) and **no live reversal envelope** exists | Retry: `422 HANDOVER_RETRY_REVERSAL_CLOSED`; dispatch: recorded `REJECTED REVERSAL_NOT_HANDED_OVER`, unsent | names the key; asks the voider to confirm with accounting first | — | `RJ-011`; `ACC-GRD-10` |
| AHO-GRD-09 | Only `REJECTED` is retryable; only `REJECTED`/`BLOCKED` is voidable | `409 HANDOVER_NOT_RETRYABLE` / `409 HANDOVER_NOT_VOIDABLE` | names the current status | — | `ACC-GRD-09` |
| AHO-GRD-10 | An acknowledgement the `CHECK`s cannot hold (`POSTED` without a reference; `REJECTED`/`DISCARDED` without code or message; no outcome) is recorded `REJECTED ACKNOWLEDGEMENT_INVALID`, **never dropped**; an over-long code or reference is cut to its column, the message kept whole | — (system) | — | `POSTED` ⇒ `external_document_ref`; `REJECTED`/`DISCARDED` ⇒ `rejection_code` + `rejection_message` | `FR-248` (*"not in a swallowed exception"*); `ACC-GRD-07` |
| AHO-GRD-11 | Retry only while INTEGRATED | `409 HANDOVER_DELIVERY_PAUSED` | — | — | `RJ-004`; `ACC-GRD-11` |
| AHO-GRD-12 | A receiver that sees an `envelope_version` it does not accept **rejects** the handover; it never guesses | lands as `REJECTED` with the receiver's code (`AHO-T1-05`) | the receiver's message | — | `RL-002`, p2-18 Scope |
| AHO-GRD-13 | WS-219 export and grid read the same filter map and sort key (`getEntitiesForExport` consumes both) | — | — | — | `FR-400`, `P2-29` Rule 1; p2-18 Acceptance |

### 1.4 Transitions that must be unreachable

| ID | Forbidden | What makes it unreachable | Source |
|---|---|---|---|
| AHO-UNR-01 | Any class under `ai.warehouse*` naming an `acc_*` table, importing an `ai.accounting*` type, or a warehouse POM depending on accounting | `WhbAccountingSeamContractTest` scans `warehouse-base`, `warehouse` and `warehouse-adapter-example` sources, migrations and POMs, and fails the build | `D-6`, `FR-231`, `WH-SC-162` |
| AHO-UNR-02 | Warehouse writing a journal, an `acc_*` row, or any account-determination result into accounting | the only exit is `WhbAccountingHandoverSink.deliver`; `AHO-UNR-01` | `D-6`, `FR-248` |
| AHO-UNR-03 | Re-costing on either side: the envelope's `extendedValue` recomputed from `quantity × unitCost` | warehouse sends the stored decimal text (`AHO-ENV-07`); the receiving rule is EXTERNAL (`RF-005`'s fourth `OD-1` edit) | `FR-233`, `FR-446` falsifier 2, `WH-SC-157` |
| AHO-UNR-04 | A rejection reversing, editing or blocking the stock movement | no transition in §1.2 writes a movement column other than `posting_status`/`handover_id`, both on `I-2`'s allowlist | `WH-SC-158`, `MPR-T4-08`, `MPR-OPEN-06` |
| AHO-UNR-05 | A second envelope for one movement; a new key on Retry | `uk(movement_id, occurred_at)`, `uk(idempotency_key)`; Retry resends the stored row | `FR-233`, `L-9` |
| AHO-UNR-06 | A `GlBalanceProvider` implementation inside `warehouse-base` or `warehouse` | the port is declared in `warehouse-base` with **no implementation there**; the implementation lives only in the accounting-facing adapter (`AHO-OPEN-01`). Enforcement test: **TBD** | `RC-002`, `FR-357` precedent |
| AHO-UNR-07 | A valued line for non-own stock (`owner_type` not posting to our GL, or `cost_basis = ZERO_BAILMENT`) | factory: `valued` ⇔ `postsToOurGl` ∧ `costBasis ≠ ZERO_BAILMENT`; writer `chk_whb_sml_bailment_not_valued` | `L-14`, `FR-112` |
| AHO-UNR-08 | A server-side re-hash after enrichment: `payload_hash` computed over anything but the canonical envelope | the codec owns its mapper (properties alphabetical, unknown components refused) and hashes the stored text | `WH-SC-166`, p2-18 Traps |
| AHO-UNR-09 | A `JSONB` payload | `payload TEXT` + `payload_hash` | p2-18 Traps, `DATA-MODEL.md` §2.1.11 |
| AHO-UNR-10 | A zero rendered where WS-219 has no GL balance | the cell carries the provider reason, never `0` or blank | p2-18 Traps (*"never a zero that reads as a reconciled balance"*) |

---

## 2. T2 — Action × role × state

Columns are the §1.1 statuses. `✓` offered, `—` not offered, `n/a` not applicable.

| ID | Action | Permission | PENDING | SENT | POSTED | REJECTED | BLOCKED | DISCARDED | VOIDED | Extra condition |
|---|---|---|---|---|---|---|---|---|---|---|
| AHO-T2-01 | View WS-052 grid, statistics, vocabularies, payload | `whb_accounting_handovers:view` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | AUDITOR holds `:view` only (`P0-12` §7) |
| AHO-T2-02 | Retry | `whb_accounting_handovers:retry` | — | — | — | ✓ | — | — | — | INTEGRATED; `AHO-GRD-08` |
| AHO-T2-03 | Void | `whb_accounting_handovers:void` | — | — | — | ✓ | ✓ | — | — | approver ≠ requester; `AHO-GRD-06`/`-07` |
| AHO-T2-04 | Export WS-052 | `whb_accounting_handovers:export` or `ADMIN` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| AHO-T2-05 | View movement (routes to WS-041) | `whb_stock_movements:view` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| AHO-T2-06 | Run WS-219 | `wh_rpt_stock_to_gl:view` (**TBD**, `AHO-OPEN-09`) | n/a | n/a | n/a | n/a | n/a | n/a | n/a | site tier (`:view:all` / `:view:branch`) per the `P2-05` precedent — **TBD** |
| AHO-T2-07 | Export WS-219 | `wh_rpt_stock_to_gl:export` or `ADMIN` (**TBD**) | n/a | n/a | n/a | n/a | n/a | n/a | n/a | — |
| AHO-T2-08 | Drill `difference` to WS-209 | WS-209's `:view` (`P2-20`) | n/a | n/a | n/a | n/a | n/a | n/a | n/a | the drill carries period × site × owner × item group |
| AHO-T2-09 | Switch `warehouse.accounting.mode` | the admin-settings permission (`P1-20`) | n/a | n/a | n/a | n/a | n/a | n/a | n/a | `AHO-GRD-02` |
| AHO-T2-10 | Edit or delete a handover | **none exists** | — | — | — | — | — | — | — | no edit, no delete (BUILD-SPEC WS-052) |
| AHO-T2-11 | Any write, as an auditor | — | — | — | — | — | — | — | — | read-only |

---

## 3. T3 — Time-driven rules & notifications

| ID | Rule | Trigger (clock / field) | What it changes | Who is notified | Channel | Job class | Notify-once? |
|---|---|---|---|---|---|---|---|
| AHO-T3-01 | Dispatch due envelopes, oldest `occurred_at` first; a transport failure is retried next pass, no backoff, no cap | `warehouse.accounting.handover.dispatch.cron` (`0 * * * * *`), batch `…dispatch.batch-size` (100) | `PENDING` → `SENT` → outcome | — | — | `WhbAccountingHandoverScheduler` → `WhbAccountingHandoverDispatcher` (BUILT) | — |
| AHO-T3-02 | A `SENT` row with no outcome after the stale window is due again | `warehouse.accounting.handover.sent-stale-minutes` (15) | re-claim | — | — | as T3-01 | — |
| AHO-T3-03 | Release sweep: frees `BLOCKED` rows whose original is `POSTED`; INTEGRATED only | same cron and batch | `BLOCKED` → `PENDING` | — | — | as T3-01 | — |
| AHO-T3-04 | **The ageing clock and the queue alert.** `ageDays` = whole UTC days from `created_at` to the injected clock, computed on read, null once `POSTED`/`DISCARDED`/`VOIDED` (`RJ-012`). Each pass counts install-wide `REJECTED`; at or above the threshold with no active episode it raises **once** and stamps `alert_raised_at`; below it every stamp clears and the episode resolves | `warehouse.accounting.handover.queue-alert.cron` (`0 */5 * * * *`); `admin_settings` `warehouse.accounting.handover.rejected_queue_threshold` (10, 1–10000, `V501071`) | `alert_raised_at` only — **nothing is retried or voided automatically** | every ACTIVE holder of `whb_accounting_handovers:retry` | in-app notification + `error` and `security` log lines | job `WHB_ACCOUNTING_HANDOVER_QUEUE_ALERT` (BUILT, `P2-22`) | **yes** — one per episode |
| AHO-T3-05 | WS-219 reads `posting_date`, the accounting clock (`L-13`), never `occurred_at`, and names it on screen and in the footer | every run | — | — | — | the report query (TO BUILD) | — |

Scan for untracked dated obligations: *expire / overdue / aging / SLA / auto-close* — the only ageing
rule is `AHO-T3-04`. A `REJECTED` row never expires and is never auto-voided. `FR-398`'s health signal
*"handovers stuck pending"* is WS-223's, v1.1 (`P3`), not this workflow's. The **accounting-side close
blocking on pending handovers** (`WH-SC-163`) has no warehouse job and no named read surface
(`AHO-OPEN-13`).

---

## 4. T4 — Cross-entity effects

| ID | When this happens | Then this other record must change | Enforced in |
|---|---|---|---|
| AHO-X-01 | Any handover status change | `whb_stock_movements.posting_status` follows: `PENDING`/`SENT` → `PENDING`; `BLOCKED` → `BLOCKED`; `POSTED` → `POSTED`; `REJECTED` → `REJECTED`; `DISCARDED` → `DISCARDED`; `VOIDED` → `NOT_APPLICABLE`. `handover_id` is set at emit. **One writer** (`WhbAccountingHandoverRepository.markMovementPosting`); no JPA entity maps `posting_status`. BUILT | `ACC-X-01`; `I-2` allowlist |
| AHO-X-02 | A stock period's close pre-check runs | counts handovers whose **movement's `period_id`** is that period and whose status is `PENDING`, `SENT`, `REJECTED` or `BLOCKED`; `POSTED`, `DISCARDED`, `VOIDED` do not block. Soft close warns and lists; hard close refuses (`MPR-OPEN-16`). The blocker links to WS-052. BUILT | `WhbPeriodCloseChecker` `PENDING_HANDOVER`; `ACC-X-02`; `WH-SC-163`, `L-8` |
| AHO-X-03 | A reversal posts | the reversal's own envelope links to the original through `predecessor_handover_id`; `BLOCKED` while the original is in flight; both voided when the original never posted (`AHO-T1-08`) | emitter (BUILT) |
| AHO-X-04 | A handover is `REJECTED` | the row joins the queue episode (`AHO-T3-04`); **the stock movement does not change** | dispatcher (BUILT) |
| AHO-X-05 | WS-219 runs | reads only; `glControlAccountBalance` comes **only** from `GlBalanceProvider` — the one read across the seam; nothing is written | report query + port (TO BUILD) |
| AHO-X-06 | An inter-branch transfer posts | the handover carries **two numbers** — transfer price (tax document) and cost (what follows the goods) — plus the unrealised-profit elimination data; the challan half is `P2-IN-03` | **blocked**: the columns are `P1-17`'s and `wh_transfer_orders` does not exist in `classic` (`AHO-OPEN-06`) |
| AHO-X-07 | A receipt, purchase or consignment movement is reported at a period end | cut-off answered by `invoice_matched` on the receipt (`V510014`), `ownership_transfer_point` on the purchase document (`V510011`) and the receipt (`V510014`), and `owner_id` for consignment — **no new column** | read by WS-219 / the envelope: **TBD** which of the two carries them (`AHO-OPEN-05`); `FR-242`, `WH-SC-128` |
| AHO-X-08 | Opening stock is loaded (`P2-19`) | it posts as `OPENING_BALANCE` movements against the `OPENING_BALANCE` virtual location (`V500013`, types seeded by `V510090`), creating the first cost layers, and each hands over like any posting-relevant movement | writer + emitter; `FR-249`, `WH-SC-049`. The virtual location code is `OPENING_BALANCE` in code; `WH-SC-049` says `VIRT-OPENING` (`AHO-OPEN-12`) |
| AHO-X-09 | A value-only movement posts (`P2-17`: `LANDED_COST_APPLY`, `COST_ADJUSTMENT`, `REVALUATION`, `WRITE_DOWN`, direction `VALUE`, `is_financial = true`) | one envelope with zero-quantity lines carrying the value (`L-15`) | emitter (BUILT path; `P2-17`) |

---

## 5. T5 — Screen contract (web only — see §0)

### 5.1 `/warehouse/platform/handovers` — WS-052 Accounting Handover Queue (the rejected-handover queue) — BUILT

| | |
|---|---|
| **Type** | list + transition modals (reference: **Service Vehicle**); no add, no edit |
| **Grid identifier** | `whb_accounting_handovers` · filter scope `WAREHOUSE_ACCOUNTING_HANDOVER` |
| **Queue name** | *Accounting Handover Queue*; the `REJECTED` filter view is the named rejected-handover queue (`FR-232`, `WH-SC-158`) |
| **Owner** | `requestedByName` (`created_by`, the posting actor) — grid and export column since `P2-22` (`DEC-07` D1). Whether a requester is the "named owner" `FR-232` means is `AHO-OPEN-08` |
| **Ageing clock** | `ageDays` (`AHO-T3-04`), grid and export column, neither sortable nor filterable |
| **Columns** | BUILD-SPEC WS-052: `movementSequenceNo`, `occurredAt`, `companyName`, `envelopeKind`, `idempotencyKey`, `status`, `attemptCount`, `lastAttemptAt`, `rejectionCode`, `rejectionMessage`, `externalDocumentRef`; plus `requestedByName`, `ageDays` (`V501071`). BUILD-SPEC's `status` cell lists four values; the built ladder has seven (`AHO-OPEN-12`) |
| **Filters** | `status` multiselect (default `PENDING`,`REJECTED`), `companyId`, `envelopeKind`, `rejectionCode`, `occurredFrom`/`occurredTo` |
| **Statistics tiles** | filter-aware, uncached: total and one per status |
| **Row actions** | **Retry** → `AHO-T2-02` · **Void** → `AHO-T2-03` (own modal, reason) · **View payload** (read-only `TEXT`) · **View movement** (WS-041) |
| **Export columns** | the grid columns incl. `requestedByName` and `ageDays`; ledger-style, no `createdByName`/`updatedByName` |
| **Display labels** | envelope-kind and rejection-code labels are raw codes until the adapter's vocabulary is settled (`P0-12` `OPEN-03`, owned here — `AHO-OPEN-12`) |
| **Mobile counterpart** | none (§0) |

### 5.2 `/warehouse/reports/stock-to-gl` — WS-219 Stock-to-GL Reconciliation — TO BUILD

| | |
|---|---|
| **Type** | report grid (BUILD-SPEC §7): real grid, no add/edit, ledger-style, filter-aware uncached statistics (`FR-395`) |
| **Grid identifier** | `wh_rpt_stock_to_gl` · filter scope `WAREHOUSE_RPT_STOCK_TO_GL`. `grid_column_definitions`, `filter_definitions`, `grid_preferences` and permission rows need a migration — `p2-18.md` line 5 says **Migrations none** (`AHO-OPEN-09`) |
| **Grain** | period × company × site × **owner** × **item group** (`FR-247`, `RC-002`). Value columns only for owners that post to our GL; `ownerTypeCode` column and an `ownerType` filter defaulting to `OWN` (`RC-006` — §7 preamble not yet amended, `AHO-OPEN-10`) |
| **Clock** | `posting_date` (`RC-001`, `L-13`), named on screen and in the footer (`AHO-T3-05`) |
| **Columns** | BUILD-SPEC §7: `periodCode`, `companyName`, `warehouseName`, `openingValue`, `receiptsValue`, `adjustmentsValue`, `revaluationsValue`, `issuesValue`, `closingValue`, `handedOverValue`, `pendingValue`, `rejectedValue`, `difference`; **plus** (`RC-002`, p2-18) `ownerName`, `itemCategoryName`, `glControlAccountBalance` |
| **Filters** | `companyId` → `warehouseId` → `periodId` · `postingDateFrom`/`postingDateTo` (`dateOnly`) · `differenceOnly` boolean · **plus** `ownerId`, `itemCategoryId` (`RC-002`) and `ownerType` (`RC-006`). All must be in `COMMON_FILTER_CONFIGS.WAREHOUSE_RPT_STOCK_TO_GL` |
| **Statistics tiles** | **TBD** — no source names them (`AHO-OPEN-10`) |
| **Row actions** | **Drill** on `difference` → WS-209 filtered to period × site × owner × item group (`AHO-RPT-05`) |
| **Empty state** | **TBD** (`emptyMessage` not specified; `AHO-OPEN-10`) |
| **Export** | Yes. Columns = the visible columns; ledger-style, no audit columns; reproduces the grid's filter and sort (`AHO-GRD-13`). Scale: `PP-6` — the 10,000-row cap and held transaction; streaming path is `P2-29`'s (`WhbStreamingExportService`) |
| **Mobile counterpart** | none (BUILD-SPEC §7 *Mobile*: every report but WS-208/WS-221 is `none`) |

| ID | Rule | Source |
|---|---|---|
| AHO-RPT-01 | Per row: `openingValue + receiptsValue + adjustmentsValue + revaluationsValue − issuesValue = closingValue`, on `posting_date`, per site × owner × item group | `FR-247`, `WH-SC-159`, `RC-001` |
| AHO-RPT-02 | Opening stock is visible **as `OPENING_BALANCE` movements** inside the period that holds them, never as an unexplained opening figure; the first period's `openingValue` is therefore zero | `FR-249`, `WH-SC-049`, p2-18 Acceptance. Which bucket carries them: `AHO-OPEN-05` |
| AHO-RPT-03 | `glControlAccountBalance` has **one** source: `GlBalanceProvider`, a port interface declared in `warehouse-base` with no implementation there, implemented in the accounting-facing adapter. The provider's signature and grain are **TBD** (`AHO-OPEN-07`) | `RC-002`, p2-18 Round-3 fold (1) |
| AHO-RPT-04 | **Mode A** (no provider bean): the report renders and does not fail; the GL cell carries the provider reason *"no accounting module installed"*, never blank, never zero; `difference` is not presented as reconciled | `RC-002`, p2-18 Traps, `WH-SC-159` (*"A variance of ₹0.00 is stated explicitly rather than shown as a blank"*) |
| AHO-RPT-05 | `difference` drills through to WS-209 filtered to period × site × owner × item group, listing the offending movements | `FR-247`, `RC-002` |
| AHO-RPT-06 | `handedOverValue`, `pendingValue`, `rejectedValue` split the period's valued movements by their handover status; `NOT_APPLICABLE` movements (posted `STANDALONE`) are **TBD** (`AHO-OPEN-07`) | BUILD-SPEC §7 WS-219 |
| AHO-RPT-07 | Every value is `DECIMAL(19,4)` and every per-unit cost `DECIMAL(19,6)`, serialised as strings; the frontend does no arithmetic | p2-18 Traps (`T-13`), CLAUDE.md rule 8 |

### 5.3 `/warehouse/masters/gl-posting-rules` — WS-051 GL Posting Rules — BUILT, read here

The envelope carries the rule's result when one resolves (`postingRuleId`, `debitAccountRef`,
`creditAccountRef`) beside the classification quad; no rule resolving is not a refusal (`ACC-ENV-05`).
**This conflicts with `p2-18.md` Traps and `WH-SC-156`**, which say warehouse holds classification only
and no account codes (`AHO-OPEN-02`). This contract records the built behaviour and does not choose.

### 5.4 The envelope — `WhbAccountingEnvelopeV1`, stored verbatim as `payload TEXT`

| ID | Rule | State | Source |
|---|---|---|---|
| AHO-ENV-01 | `envelope_version` `SMALLINT NOT NULL`, inside the hash; v1 is frozen — a new field is a v2 record and a new codec branch, never an edit of v1 | BUILT | `RL-002`, `ACC-ENV-01` |
| AHO-ENV-02 | Header: kind, key, `movementId`, `occurredAt`, `postingDate`, `sequenceNo`, company, site, branch, movement type, reason, source system / document type / id / no, the movement's own key, `reversalOfMovementId` | BUILT | `FR-233`, `ACC-ENV-03` |
| AHO-ENV-03 | Per line (`FR-233`): `owner_type` ✓, quantity ✓, base UoM ✓, unit cost ✓, extended value ✓, `cost_basis` ✓, currency ✓ — **`duty_status` ✗, lot identity ✗, serial identity ✗, `exchange_rate` ✗** are not components of `WhbAccountingEnvelopeV1.Line` | **gap** | `FR-233`, `WH-SC-156`, `RF-005`; `AHO-OPEN-02` |
| AHO-ENV-04 | `branchId`/`branchCode` = the site's `REGISTERED` branch **at `occurred_at`**, frozen in the hash; never the user's branch nor a `SERVING` branch; null when none held | BUILT | `RG-001`, `ACC-ENV-06` |
| AHO-ENV-05 | A movement **every line of which** is `ZERO_BAILMENT` emits **no envelope**; `posting_status` stays `NOT_APPLICABLE` | BUILT | `RF-005`, `CONFIG-CASE-10`, `ACC-ENV-04` |
| AHO-ENV-06 | Otherwise a line is valued iff its owner type `posts_to_our_gl` and `cost_basis ≠ ZERO_BAILMENT`; an unvalued line carries quantity, UoM and custody only; no valued line ⇒ kind `STOCK_CUSTODY`, else `STOCK_MOVEMENT` | BUILT | `L-14`, `ACC-ENV-04`; `AHO-OPEN-03` |
| AHO-ENV-07 | Decimals travel as the stored text; `extendedValue` is authoritative and is not `round(quantity × unitCost, 4)` recomputed anywhere | BUILT (warehouse half) | `RF-005`, `FR-446`, `WH-SC-157` |
| AHO-ENV-08 | Each line carries the classification quad — movement type, effective reason, the item's `STOCKING` category **at `occurred_at`**, owner type | BUILT | `FR-246`, `RG-005`, `ACC-ENV-05` |
| AHO-ENV-09 | The adapter maps a warehouse handover onto the port's `movements[]`, each line's `movement_date` = the envelope's `postingDate`, never `occurredAt` | EXTERNAL (adapter) | `RF-005`, `L-13` |
| AHO-ENV-10 | `payload_hash` is SHA-256 over the canonical envelope, before any server-side enrichment | BUILT | `WH-SC-166`, `ACC-ENV-02` |

---

## 6. Out of scope (explicit decisions)

| Baseline item | Decision | Reason | Revisit |
|---|---|---|---|
| The accounting-side receiving columns (`extended_value`, `currency_code`, `exchange_rate`, `cost_basis` on the source-document movements) and the third install state | **not warehouse's** | `OD-1` RESOLVED 2026-09-11: an external integration dependency; `RF-005`'s fourth reciprocal edit. `/Users/bbhushan/work/git/workspace/accounting` is not edited from this batch | when accounting schedules it |
| The movement post/reverse lifecycle | `movement-post-reverse.contract.md` | this contract reads `MPR-T4-08` only | — |
| Stock period ladder | `P0-07` | this contract supplies the pending-handover count (`AHO-X-02`) | — |
| Goods-in-transit claims side | `P5-16` | p2-18 Scope | — |
| The challan half of the transfer's two numbers | `P2-IN-03` | p2-18 Scope | — |
| The opening-balance batch and tie-out | `P2-19` | this contract owns the rule and the envelope only | — |
| Streaming export for WS-219 at 100,000 rows | `P2-29` | `PP-6` | when `P2-29` subclasses it |
| Mobile screens | not built | user scope rule 2026-09-11; `FR-218` | only if the user reverses the rule |
| `all_activity_history` | warehouse stays out | `T-14`; warehouse owns `whb_activity_history` | — |

---

## 7. Amendments

| Date | Row IDs affected | Change | Found by |
|---|---|---|---|
| 2026-09-19 | all | v0 derived from the design set at `a424481` and from `classic` (`P0-12`, `P2-22`, `P2-17`, `P1-20` code); unratified | `functional-reviewer`, derive mode |
| 2026-09-19 | all | v1 ratified by the user: OPEN rows kept OPEN; STANDALONE scope for P2-18; WS-219 migration V511065 claimed (AHO-OPEN-09); FR-244 two numbers built with P1-17 ahead of P2-18 (AHO-OPEN-06) | driver, on the user's ruling |

---

## 8. Invariants and scenarios this workflow must not break

| Invariant | Rows that carry it | Scenarios that prove it |
|---|---|---|
| `D-6` warehouse owns quantity and cost, accounting the ledger; no foreign writer | `AHO-UNR-01`…`-03`, `AHO-ENV-07` | `WH-SC-156`, `WH-SC-157`, `WH-SC-162` |
| `D-7` standalone is the reference configuration | `AHO-GRD-01`, `AHO-GRD-02`, `AHO-T1-11` | `CONFIG-CASE-07` |
| `L-8` period-bound; the close sees open handovers | `AHO-X-02` | `WH-SC-163` |
| `L-9` idempotent ingestion | `AHO-GRD-03`, `AHO-UNR-05` | `WH-SC-166` |
| `L-13` three timestamps — `posting_date` is the accounting clock | `AHO-T3-05`, `AHO-ENV-09`, `AHO-RPT-01` | `WH-SC-159` |
| `L-14` non-own never valued | `AHO-ENV-05`, `AHO-ENV-06`, `AHO-UNR-07` | `CONFIG-CASE-10` |
| `L-15` value conservation (value-only envelopes) | `AHO-X-09` | `WH-SC-034` |
| `IRR-41` `handover_id` + `posting_status` on every movement | `AHO-X-01` | `WH-SC-158` |
| `RJ-011` void, not only retry | `AHO-T1-07`, `AHO-T1-08`, `AHO-GRD-05`…`-07` | `WH-SC-158` |
| Other scenarios in scope | cut-off, opening balance | `WH-SC-128`, `WH-SC-049` |

---

## 9. Open rows — contradictions between sources, and holes no source fills (all OPEN)

| ID | Question | Source A | Source B | Rows | Status |
|---|---|---|---|---|---|
| AHO-OPEN-01 | **Where does the accounting-facing adapter live, and does `P2-18` build it?** It implements `WhbAccountingHandoverSink` and `GlBalanceProvider`, declares `enable.warehouse.accounting_sink=true`, and must import both sides — so it cannot sit under `ai.warehouse*` (`AHO-UNR-01`). No module in CLAUDE.md's band table and no design-set row names it. Without it `INTEGRATED` is unreachable on this install and `WH-SC-156`/`-157` and "retry twice posts once by the consumer's row count" cannot be proven here | p2-18 Acceptance (the adapter declares the property); `RC-002` (*"implemented in the accounting-facing adapter"*) | `OD-1` resolution (*"reciprocal work in another repository remains an external integration dependency"*); batch rule: do not edit the `accounting` repository | T1-11, GRD-02, RPT-03, UNR-06, A3, A7 | **OPEN** |
| AHO-OPEN-02 | **What the envelope must carry, and in which version.** `FR-233`/`WH-SC-156` require per-line `duty_status`, lot and serial identity; `RF-005` requires `exchange_rate`; none is in `WhbAccountingEnvelopeV1`, which `RL-002` freezes — so adding them means a v2. Separately, v1 carries `debitAccountRef`/`creditAccountRef` from `whb_gl_posting_rules`, which p2-18 Traps (*"if a builder finds themselves typing an account code, `D-6` has been misread"*) and `WH-SC-156` (*"no chart of accounts and no posting-rule table anywhere in warehouse"*) forbid, while BUILD-SPEC WS-051 and `P0-12` `DEC-01` (`O-002`) specify them. And under `OD-16` stored values are company base currency — which rate the envelope's `exchange_rate` carries is unstated | `FR-233`, `RF-005`, p2-18 Traps, `WH-SC-156` | `WhbAccountingEnvelopeV1`; BUILD-SPEC WS-051 columns; `P0-12` `DEC-01`; `OD-16` | ENV-03, §5.3, A4 | **OPEN** |
| AHO-OPEN-03 | **Does a non-own movement emit a custody envelope, or nothing?** | `L-14`/`D-6` (*"handed over for quantity and custody reporting only"*); p2-18 Acceptance (*"hand over quantity and custody only, with `cost_basis = ZERO_BAILMENT`"*) | `RF-005` (*"`ZERO_BAILMENT` suppresses the envelope entirely"*); built `AHO-ENV-05` — an all-`ZERO_BAILMENT` movement emits nothing, and a `STOCK_CUSTODY` envelope only arises when an owner type has `posts_to_our_gl = false` with a non-`ZERO_BAILMENT` basis | ENV-05, ENV-06, A8 | **OPEN** |
| AHO-OPEN-04 | **Reclassification to `NOT_APPLICABLE`** — `RJ-011` and BUILD-SPEC WS-052 name it as a Void precondition; no v1 transition writes it, so the branch was removed (`P0-12` `OPEN-04`, owned here). Define the transition or strike the branch from the design set | `RJ-011`, `p2-18.md` Scope and Acceptance, BUILD-SPEC WS-052 | built `ACC-GRD-04`; batch ruling *"the contract wins"* (P2-22 D4) | GRD-06, A15 | **OPEN** |
| AHO-OPEN-05 | **The five-term bucket mapping.** Which movement types (by `direction` `IN`/`OUT`/`INTERNAL`/`VALUE`, or by another flag) fall into receipts, adjustments, revaluations and issues; where `OPENING_BALANCE`, transfers (depart/arrive/in-transit), `OWNER_CHANGE` and `STATUS_CHANGE` land; and whether the cut-off columns (`invoice_matched`, `ownership_transfer_point`, `owner_id`) appear on WS-219, on the envelope, or on neither | `FR-247` names the five terms only | no source maps types to terms | RPT-01, RPT-02, X-07, A11 | **OPEN** |
| AHO-OPEN-06 | **The transfer's two numbers** (`FR-244`) cannot be built: `wh_transfer_orders` does not exist in `classic`, and `P1-17`, which owns the columns, is sequenced after `P2-18` (batch driver ruling on `P2-02`) | p2-18 Scope (*"this task owns the first truth"*) | `IMPLEMENTATION-PLAN.md` §8.2; `P1-17` not built | X-06, A12 | **OPEN** |
| AHO-OPEN-07 | **WS-219's `GlBalanceProvider` contract and `difference`.** (a) Signature and grain: a GL control account is keyed by account, not by site × owner × item group, so which grain can the provider answer and how a site/owner/group row is compared to it. (b) The formula for `difference` — `RC-002` says the built column compared warehouse to its own handover outbox and must compare to the ledger; BUILD-SPEC still lists `handedOverValue`/`pendingValue`/`rejectedValue`. (c) How `NOT_APPLICABLE` value (posted `STANDALONE`) is shown. (d) Whether the GL column shows when a provider is installed but the mode is `STANDALONE`. (e) WS-209, the drill target, is unbuilt (`P2-20`) and has no `periodId` or item-group filter | `RC-002`, `FR-247` | BUILD-SPEC §7 WS-209, WS-219 rows | RPT-03…RPT-06, A16, A17 | **OPEN** |
| AHO-OPEN-08 | **Who is the queue's "named owner".** Built: `requestedByName` = the posting actor (`P2-22` D1), alert recipients = holders of `:retry`. `FR-232`/p2-18 Traps ask for *"a named owner column"* — a requester who may be a floor operator is not necessarily a worker of the queue; there is no assign verb (cf. WS-043's `:assign`) | `FR-232`, p2-18 Traps, `WH-SC-158` | `P2-22` `DEC-07` D1, D3 | §5.1, A6 | **OPEN** (settled by `P2-22` D1 as built; confirm) |
| AHO-OPEN-09 | **WS-219's migration and permissions.** The report needs grid, filter, preference, menu and permission rows (`wh_rpt_stock_to_gl:view`/`:export`, site tiers per `P1-18`); `p2-18.md` line 5 says *Migrations none*. The batch rule is to claim the next free number in the `warehouse` grid band `V511065`–`V511139` (`P2-29`'s sub-allocation) and record it on line 5 and `DATA-MODEL.md` §7.2 | `DATA-MODEL.md` §7 note 4; `P2-05` precedent (`V511060`) | `p2-18.md` header line 5 | T2-06, T2-07, §5.2 | **OPEN** |
| AHO-OPEN-10 | **BUILD-SPEC §7 WS-219 is not amended** for `RC-002` (owner/group columns and filters, `glControlAccountBalance`), `RC-001` (the `Clock` column) or `RC-006` (`ownerTypeCode`, `ownerType` default `OWN`); its statistics tiles and empty state are unspecified; `PORT-AND-ADAPTER-CONTRACT.md` §4 has no `GlBalanceProvider` line (`RC-002` asks for one) | `GAP-REGISTER-R3.md` `RC-001`, `RC-002`, `RC-006` | BUILD-SPEC §7 row WS-219 | §5.2, A16 | **OPEN** |
| AHO-OPEN-11 | **`P0-12` hand-offs `OPEN-05`, `OPEN-06`, `OPEN-07`.** (05) Should a reversal of a movement posted while `STANDALONE` emit at all? Recommendation on record: emit nothing, decided with the switch runbook because opening balances may already carry that stock. (06) A reversal envelope `REJECTED` for what it carries has no warehouse exit; recommendation on record: the adapter answers `DISCARDED` after an accounting-side correction. (07) A `SENT` original rejected `REVERSAL_NOT_HANDED_OVER` may already have posted; whether the missing reversal envelope is back-filled at the switch | `p2-18.md` *Hand-off from P0-12* | `P0-12` §9 | T1-09, T1-10, GRD-08 | **OPEN** |
| AHO-OPEN-12 | **Design-set drift to reconcile**: `FR-232` and `D-6` list four `posting_status` values (built: six); `DATA-MODEL.md` §2.1.11 lists five handover statuses (built: seven) and omits `predecessor_handover_id` and the voided trio; BUILD-SPEC WS-052's `status` cell lists four; `envelope_kind`'s vocabulary is not enumerated in `DATA-MODEL.md` (`RF-005` asks for it) and its display labels are raw codes (`P0-12` `OPEN-03`); `FR-233` still carries the `⛔ OD-1` blocker mark though `OD-1` is RESOLVED; `WH-SC-049` names `VIRT-OPENING` where code seeds `OPENING_BALANCE`; `p2-18.md` *Blocked on* still reads as an open `OD-1` block; p2-18 cites `FR-398` (v1.1 health signals) for the Mode-A provider reason, which is `FR-357`'s shape | the design set | `classic` code | §1.1, §5.1, ENV-03, X-08 | **OPEN** |
| AHO-OPEN-13 | **How the accounting close "sees the pending handovers"** (`WH-SC-163`, `FR-251`). Warehouse exposes no read for it, and accounting may not read `whb_*` without a seam of its own. Is it a second port (a pending-count provider in the adapter), or accounting's own record of what it has not acknowledged? | `WH-SC-163`, `FR-251` | no source | X-02, §3 | **OPEN** |

<!-- Ratify with /functional-contract. A derived contract proves nothing until a human has ratified it. -->
