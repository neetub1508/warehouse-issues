# R29 — functional review (Claude + GPT dual engine), area TRADE-SALES

**Date** 2026-10-22 · **Reviewer** functional-reviewer, pre-build audit mode · **Dispositions** recorded in the area FRD §"R29 dispositions"

## Summary (≤200 words)

I did not write `/private/tmp/claude-501/-Users-bbhushan-work-git-workspace-classic/53f0e57a-69c7-42b1-a5aa-daa8c13be89a/scratchpad/FR-REVIEW-TRADE-SALES.md`. My agent definition forbids writing report files. The full report follows below so you can save it as is.

**Findings: 29 in total (16 High, 10 Medium, 3 Low). The sales flow does not work end to end as specified.**

Top 5:
1. **F1:** a BLANKET or OPEN SO cannot be approved. `createDemand` sends demand lines whose ordered quantity is the sum of firm lines, which is 0. Core's `chk_wh_demand_order_lines_ordered CHECK (ordered_quantity > 0)` refuses that, and p8-02 never relaxes the CHECK (p8-01 does on the PO side).
2. **F2:** one SO maps to one core demand order, but the core header ships as a whole and then goes `SHIPPED`, then `DELIVERED` (terminal). Releases after the first full shipment cannot be made.
3. **F3:** an SRA can never close. It waits for core RMA `CLOSED`, but core RMAs end in `MATCHED`, `EXPIRED` or `CANCELLED`.
4. **F8:** the zero-level `SQ` rule has no conditions. Rule conditions only have to be a subset of document conditions, so this rule also matches below-floor quotations, and `SYSTEM` approves them.
5. **F4:** an `EXPIRED` quotation can be neither won nor lost, so its enquiry stays `QUOTED` forever.

**Mirror asymmetries: 18.**

**Refusals:** credit limit, invoices, debit/credit notes and tax are clean. FX leaks into value tiles and reports that add up different currencies (F24).

Engines: Claude + GPT (gpt-6.1-sol, medium) — 11 both · 10 Claude only · 8 GPT only · 0 dropped

---

# Functional conformance — warehouse-trade sales side (P9), pre-build
Contract: trade-sales-enquiry-quotation, trade-sales-order, trade-sales-return-authorisation, trade-order-amendment, trade-approval-matrix, trade-rate-contract, trade-counterparty-evaluation, po-schedule-port (all v0, 2026-10-22) | Mode: audit (pre-build design; no trade code exists)
Files reviewed: 30 design files (FRD-TRADE, 10 trade contracts, po-schedule-port, p9-01..14, 11-EPIC-p9, p8-02, p8-15) and 5 core code files, read to settle questions about the ports | File set: derived from workflow
Design repo: `/Users/bbhushan/work/git/workspace/warehouse-issues` @ e14159a. Core code: `/Users/bbhushan/work/git/workspace/classic/warehouse/backend`.
Engines: Claude + GPT (gpt-6.1-sol, medium) — 11 both · 10 Claude only · 8 GPT only · 0 dropped

## Verdict
**29 findings: 16 High, 10 Medium, 3 Low. 18 mirror asymmetries.** The sales flow (enquiry → SO → dispatch → return) does not work end to end as specified. Three core facts break "one trade SO ↔ one core demand order":
- the demand-line quantity CHECK;
- the demand header ladder, which ships the whole order and then goes terminal;
- the core RMA ladder, which has no `CLOSED` status.

All paths below are relative to the design repo unless marked `classic:`.

## Status reachability
| Entity / status | In contract T1 | Inbound | Outbound | Verdict |
|---|---|---|---|---|
| Enquiry `OPEN` | yes | TSQ-T1-01 | quote / regret / cancel | ok |
| Enquiry `QUOTED` | yes | first `SENT` | outcome only when every line has one | **dead end** (F4, F5) |
| Enquiry `WON`/`PARTIALLY_WON`/`LOST` | yes | TSQ-T4-01 | terminal | partial lines never resolve (F5) |
| Quotation `EXPIRED` | yes | TSQ-T3-02 | revise only | **cannot be won or lost** (F4) |
| Quotation `APPROVED` (not sent) | yes | TAM | send only, no cancel | weak exit |
| SO `ACKNOWLEDGED` | FRD only | FR-606 / WH-SC-556 | — | **conflicts with `ISSUED`** (F6) |
| SO `ISSUED` | yes | TSO-T1-06 | releases / close | no re-acknowledgement after amendment (F10) |
| SO `APPROVED` (BLANKET/OPEN) | yes | TSO-T1-04 | — | **unreachable: the core CHECK refuses the port call** (F1) |
| Dispatch release `CLOSED` | prose only | **none** | — | **unreachable** (F7) |
| Dispatch release `DRAFT` | yes | T1-07/-09, SRA | release only | **no cancel** (F7) |
| SRA `PARTIALLY_RECEIVED` / `RECEIVED` | yes | RMA projection | close needs RMA `CLOSED` | **dead end** (F3) |
| Core demand order after first full ship | core | `SHIPPED` → `DELIVERED` | terminal | later releases unreachable (F2) |

## Findings

### F1 — Rank 1 (High): BLANKET and OPEN SOs cannot be approved, because the core demand-line CHECK refuses zero-firm lines
- Contract row: TSO-T1-04, TSO-T4-01, FR-605
- Source: Claude
- Evidence:
  - `docs/contracts/trade-sales-order.contract.md:67` sends BLANKET lines as `FORECAST` and OPEN lines with no schedule.
  - `issues/p8-02.md:25` makes demand-line `ordered_quantity` the sum of firm schedule lines, so it is 0 at approval.
  - classic: `V510040__Create_wh_demand_orders_and_lines.sql:319` has `CHECK (ordered_quantity > 0)`.
  - The PO side relaxes the same CHECK (`po-schedule-port.contract.md:26`); p8-02 does not.
- What a user experiences: approving a BLANKET or OPEN SO rolls back with a DB error. The SO stays `SUBMITTED`.
- Fix: p8-02 must make `wh_demand_order_lines.ordered_quantity` nullable or ≥ 0 for port-owned lines, replacing the CHECK (mirroring p8-01). Add it as a POS-GRD row.

### F2 — Rank 1 (High): one demand order per SO conflicts with the core header ladder, which ships the whole order and then goes terminal
- Contract row: TSO-T4-01/-02, FRD §5 M18, POS-T1-11
- Source: Claude
- Evidence:
  - classic: `WhDemandOrderService.java:892-905` ships only when every line is fully accounted, then sets the header to `SHIPPED`.
  - classic: `WhDemandOrder.java:101,386-394` makes `DELIVERED` terminal.
  - `issues/p8-02.md:41` says the ladder does not change.
  - `po-schedule-port.contract.md:73` releases only onto a non-terminal demand order.
- What a user experiences: a 12-month BLANKET ships its first release and the core order goes `SHIPPED` → `DELIVERED`. Every later dispatch release is refused, or it lands on a terminal order.
- Fix: p8-02 must define how the header ladder behaves for schedule-driven orders. Options: the header rolls up from the schedule lines and is never terminal while open or forecast lines remain, or one core demand order per release (then the M18 symmetry claim changes). Record the choice as an `OD`.

### F3 — Rank 1 (High): an SRA can never close
- Contract row: TSR-T1-05, TSR-T4-01, POS-T1-22
- Source: Both
- Evidence:
  - `trade-sales-return-authorisation.contract.md:60` requires core RMA `CLOSED` / `EXPIRED`.
  - classic: `WhRma.java:53-64` shows core RMA statuses are only OPEN, APPROVED, MATCHED, EXPIRED and CANCELLED.
  - `po-schedule-port.contract.md:167` publishes `MATCHED` / `EXPIRED`.
  - `:50` sends `PARTIALLY_RECEIVED` to close, but `:60` accepts only `RECEIVED` or `APPROVED`.
- What a user experiences: a matched return stays `RECEIVED` forever. A partial receipt followed by expiry has no exit at all.
- Fix: map `MATCHED` / `EXPIRED` / `CANCELLED` to SRA transitions, and add `PARTIALLY_RECEIVED` to TSR-T1-05's From list.

### F4 — Rank 1 (High): an expired quotation can be neither won nor lost, so its enquiry stays QUOTED
- Contract row: TSQ-T1-08/-09/-10, TSQ-GRD-05, TSQ-T3-02, TSQ-T2-05
- Source: Both
- Evidence:
  - `trade-sales-enquiry-quotation.contract.md:86` allows a win when the customer's PO date is within validity.
  - But `:74` (won) and `:75` (lost) accept only `SENT`, and `:114` sets `EXPIRED`.
  - `:73` allows revising `EXPIRED`, but T2 `:105` limits revise to `SENT`.
  - `:58-59`: the enquiry leaves `QUOTED` only through outcomes.
- What a user experiences: a customer PO that arrives after the expiry job cannot be recorded as won. An unanswered quote can never be marked lost. The enquiry, the hit rate and `ENQUIRY_CONVERSION` all stay open.
- Fix: allow Won (with the PO-date evidence) and Lost from `EXPIRED`. Add an enquiry close/lost path from `QUOTED`. Align T1 and T2.

### F5 — Rank 1 (High): partly quoted or partly won enquiries cannot resolve their remaining lines
- Contract row: M6, TSQ-T1-02/-09/-10, TSQ-T4-01
- Source: GPT
- Evidence:
  - `docs/frd/FRD-TRADE.md:270` promises partial quoting and partial winning.
  - `trade-sales-enquiry-quotation.contract.md:67` allows a quote only from an `OPEN` enquiry.
  - `:74` makes a per-line win set the whole quotation `WON`.
  - `:121` needs every line to have an outcome.
- What a user experiences: lines that were not quoted, or not won, have no path to quote, lose or regret.
- Fix: add per-line outcomes, and allow quoting and regretting remaining lines from `QUOTED`.

### F6 — Rank 1 (High): the SO acknowledgement has two incompatible target states
- Contract row: TSO §1.1, TSO-T1-06, FR-606
- Source: Both
- Evidence:
  - `FRD-TRADE.md:233` and `:483` (WH-SC-556) say `ACKNOWLEDGED`.
  - `trade-sales-order.contract.md:54-58` excludes it, and `:69` / `issues/p9-10.md:15` say `ISSUED`.
- What a user experiences: the scenario and the lifecycle cannot both pass. Filters and tiles depend on which document the builder follows.
- Fix: choose `ISSUED` and amend FR-606 and WH-SC-556.

### F7 — Rank 1 (High): dispatch release `CLOSED` is unreachable, and a `DRAFT` release cannot be cancelled
- Contract row: TSO §1.1, TSO-T1-10, TSR-T1-05
- Source: Claude
- Evidence:
  - `trade-sales-order.contract.md:57` says "CLOSED (core demand order shipped / closed)". With one demand order per SO this can never be true per release, and there is no T1 row for it.
  - `:73` allows cancel only from `RELEASED`.
  - `trade-sales-return-authorisation.contract.md:60` needs a replacement release to exist or be declined, and a declined `DRAFT` cannot be cancelled.
  - Purchase twin: `trade-purchase-order.contract.md:101` carries the same stale wording.
- What a user experiences: releases never close. Draft releases, including replacement drafts, pile up with no exit.
- Fix: add a T1 row that closes a release when its firmed schedule lines are `SHIPPED`/`CANCELLED`. Add a `DRAFT` → `CANCELLED` row.

### F8 — Rank 2 (High): the zero-level SQ rule approves below-floor and over-discount quotations automatically
- Contract row: TAM-GRD-01, TAM-T1-04, TSQ-T1-04
- Source: Both
- Evidence:
  - `trade-approval-matrix.contract.md:73` matches a rule when its conditions are a subset of the document's, and the empty set matches anything.
  - `:61`: a zero-level match is approved by `SYSTEM`.
  - `issues/p9-08.md:13-14` intends the rule only for quotations with no condition.
  - `issues/p9-03.md:25-27` says no `SQ` default is seeded at all, which contradicts p9-08.
- What a user experiences: unless an install adds a more specific rule, a below-floor quote is approved by the system instead of being refused.
- Fix: give rules an "exact / no conditions" flag (or a rule matches only when the document has no condition beyond the rule's). Reconcile the seeding between p9-03 and p9-08.

### F9 — Rank 2 (High): the ambiguity guard misses equally specific rules on different dimensions
- Contract row: TAM-GRD-01/-05, FR-548
- Source: GPT
- Evidence: `FRD-TRADE.md:125` refuses ties. `trade-approval-matrix.contract.md:73` ranks rules by how many dimensions they fill, but `:77` refuses overlaps only when the dimension set is identical.
- What a user experiences: a site rule and a department rule tie. Which approver chain is used is not defined.
- Fix: refuse any intersecting scope with equal specificity at save, or define a precedence order.

### F10 — Rank 3 (High): an amended SO cannot be re-acknowledged
- Contract row: TOA-T4-03, TSO-T1-06
- Source: Both
- Evidence: `trade-order-amendment.contract.md:105` resets the SO acknowledgement to `PENDING`. The SO has no `ack_status` field (`trade-sales-order.contract.md:29-37`), and `:69` sends only from `APPROVED`.
- What a user experiences: no button re-issues the amended acknowledgement.
- Fix: add `ack_status` per version, plus a *Re-send acknowledgement* action from `ISSUED`.

### F11 — Rank 3 (High): ATP has no owner, so WS-305 and the at-risk rule have no source
- Contract row: TSO-T4-03, TSO-T3-02
- Source: Claude
- Evidence:
  - `issues/p9-09.md:49` and `FRD-TRADE.md:577` say the ATP query bean is owed by p8-02.
  - `issues/p8-02.md:22` scopes no ATP bean.
- What a user experiences: the ATP and shortfall columns and the "released, ATP short" at-risk check cannot be built.
- Fix: add the ATP bean to p8-02's scope and to the po-schedule-port contract.

### F12 — Rank 3 (Medium): Withdraw has no screen entry on sales documents
- Contract row: TAM-T1-09, TSO-T1-03
- Source: GPT
- Evidence: `trade-sales-order.contract.md:66` has UI "—". The action lists at `trade-sales-enquiry-quotation.contract.md:139` and `trade-sales-return-authorisation.contract.md:112` omit it. The PO lists it at `trade-purchase-order.contract.md:182`.
- What a user experiences: a maker cannot pull back a submitted sales document.
- Fix: add Withdraw to the T5 actions of the SO, the quotation, the SRA and the SO amendment.

### F13 — Rank 3 (Medium): send and acknowledge need templates that arrive only in p9-14
- Contract row: TSQ-T1-06, TSO-T1-06
- Source: GPT
- Evidence: `issues/p9-02.md:36` and `issues/p9-14.md:53,56` deliver the templates last. `issues/p9-08.md:28` and `issues/p9-10.md:29` must pass scenarios that need a sent quotation or acknowledgement.
- What a user experiences: p9-08 and p9-10 cannot meet their acceptance criteria.
- Fix: seed minimal templates in the consuming task, or move those acceptance items to p9-14.

### F14 — Rank 4 (High): FIXED SO lines can be allocated before any dispatch release
- Contract row: TSO-T1-04/-08/-09, POS-T3-03
- Source: GPT
- Evidence: `trade-sales-order.contract.md:67` sends FIXED lines as `FIRM` at approval. `po-schedule-port.contract.md:118` makes in-horizon firm lines allocatable. Yet `:20`, `:71` and `:124` say a release is what firms FIXED schedule lines.
- What a user experiences: core picks FIXED orders before the planner releases them. Release accounting is undefined.
- Fix: send FIXED lines as `FORECAST` and let releases firm them, or exclude FIXED from dispatch releases.

### F15 — Rank 4 (High): the demand port cannot firm or un-firm a single schedule line
- Contract row: TSO-T1-08/-10, TSO-T4-02, POS-T1-11/-12
- Source: Both
- Evidence:
  - The PO side has "Firm it" (`po-schedule-port.contract.md:65`). The demand side only adds schedule lines (`:73`) or amends and cancels whole lines (`:74`).
  - `trade-sales-order.contract.md:73` needs firm → `FORECAST` on cancel, and uses `cancelLine` (the whole item line) for one OPEN call-off. FIXED cancel is undefined.
- What a user experiences: MRP sees released quantity twice (the new `FIRM` line plus the leftover `FORECAST`). Cancelling one call-off cancels the others on the same line.
- Fix: add demand-port operations to firm, un-firm and cancel a schedule line, keyed by schedule-line id and `release_ref`.

### F16 — Rank 4 (High): replacement releases are refused by the normal release guards
- Contract row: TSR-T4-02, TSO-GRD-06, TSO-T3-03
- Source: Both
- Evidence:
  - `trade-sales-return-authorisation.contract.md:102` drafts a replacement release on the original SO.
  - `trade-sales-order.contract.md:87` caps a release at the open schedule quantity, which is 0 after shipment.
  - `:116`: auto-close does not wait for open SRAs, so the SO may already be terminal.
- What a user experiences: a `REPLACE` return cannot be shipped.
- Fix: exempt releases flagged `is_replacement`, bound them by received SRA quantity, keep the SO open while an SRA is open, and add a `FIRM` line through the port.

### F17 — Rank 4 (High): dispatch releases have no approval and do not consume rate-contract ceilings
- Contract row: M18/M20, TSO-T1-08, TRC-T4-01
- Source: Both
- Evidence:
  - The PO release goes through approval (`trade-purchase-order.contract.md:97-99`). The SO release goes straight from DRAFT to RELEASED (`trade-sales-order.contract.md:71`).
  - FR-548 (`FRD-TRADE.md:125`) lists no `SO_RELEASE` approval, although `issues/p9-02.md:34` seeds an `SO_RELEASE` series.
  - TSO-T1-04 consumes the contract ceiling for FIXED only, while `trade-rate-contract.contract.md:121` requires release quantities to be consumed for OPEN/BLANKET.
- What a user experiences: sales rate-contract ceilings are never enforced on OPEN or BLANKET SOs.
- Fix: add consumption to TSO-T1-08 and its reversal to T1-10. Either add an `SO_RELEASE` approval or write the refusal into M18.

### F18 — Rank 4 (Medium): SO guards miss three purchase twins
- Contract row: TPO-GRD-05/-10/-11 compared with TSO-GRD-*
- Source: Both
- Evidence: `trade-purchase-order.contract.md:113,118-119` has these guards; `trade-sales-order.contract.md:82-93` has no equivalent. The missing guards:
  - TPO-GRD-11: re-check the price at approval;
  - TPO-GRD-10: no edit while an approval or amendment is open;
  - TPO-GRD-05: item active and sellable, UoM convertible.
- What a user experiences: an SO can be approved at a rate from an expired or changed sales contract, or with a UoM that cannot be converted.
- Fix: add TSO twins of all three guards.

### F19 — Rank 4 (Medium): a pending customer-schedule amendment stops dispatch
- Contract row: TOA-GRD-01/-04, TSO-T1-12, TSO-GRD-07
- Source: Claude
- Evidence:
  - `trade-order-amendment.contract.md:68`: only one open amendment is allowed per order.
  - `trade-order-amendment.contract.md:71` and `trade-sales-order.contract.md:88` refuse releases while an amendment is open.
- What a user experiences: while a weekly customer schedule waits for approval, no line it touches can be dispatched, and next week's import is refused with 409.
- Fix: refuse releases only on schedule lines the amendment changes, and let a newer import replace a `DRAFT` schedule amendment.

### F20 — Rank 4 (Medium): SO cancel and short-close lack port effects, and SO auto-close depends on an undefined "complete"
- Contract row: TSO-T1-05/-11, TSO-T3-03
- Source: Claude
- Evidence:
  - `trade-sales-order.contract.md:68` says "planned demand withdrawn" but names no port operation, and there is no T4 row (the PO has `trade-purchase-order.contract.md:169`).
  - `:116` mirrors TPO-T3-03, which needs fulfilment `COMPLETE` with an under-tolerance (`trade-purchase-order.contract.md:167`). The SO has no tolerances.
  - TSO-OPEN-02 (`:164`) is still open.
- What a user experiences: auto-close and short-close behaviour is unspecified.
- Fix: add a TSO-T4 row for `cancelDemand` / `cancelLine`, SO tolerances (or "complete = shipped ≥ qty"), and close TSO-OPEN-02 in p8-02.

### F21 — Rank 4 (Medium): the core RMA is created `OPEN`, and trade's own guard then blocks core from approving it
- Contract row: TSR-T4-03, POS-T1-20, POS-GRD-22
- Source: Claude
- Evidence: `trade-sales-return-authorisation.contract.md:101` sends `initialStatus:'OPEN'`. `issues/p9-13.md:12` and `po-schedule-port.contract.md:175` refuse manual changes to trade-created RMAs. The PO side creates its core document `APPROVED`. Receipt still works from `OPEN` (classic: `WhRmaService.java:250-251`).
- What a user experiences: core screens show the RMA as unapproved forever.
- Fix: pass `initialStatus:'APPROVED'` with the trade approver.

### F22 — Rank 4 (High): price-list overlap and precedence are undefined
- Contract row: TRC-GRD-02, TRC-T4-04
- Source: GPT
- Evidence: `trade-rate-contract.contract.md:33-35` and `:86` key the overlap check on the counterparty, which a price list does not have. `:124` does not choose between several matching lists.
- What a user experiences: two overlapping general or category price lists give different prices, and nothing says which one wins.
- Fix: make price-list applicability unique per date, or give price lists an explicit priority.

### F23 — Rank 4 (Medium): a future-dated termination or supersession removes prices early
- Contract row: TRC-T1-07/-09
- Source: GPT
- Evidence: `trade-rate-contract.contract.md:77,79` change the status immediately, while resolution at `:122` uses only approved, active contracts.
- What a user experiences: approving a termination dated next month stops today's price.
- Fix: resolve by effective dates, or schedule the status change.

### F24 — Rank 6 (Medium): FX dependency in value tiles and reports
- Contract row: TRD-06, TSQ §5.3, TSO §5
- Source: Both
- Evidence: `FRD-TRADE.md:527` says documents of different currencies are never summed. Yet the open-value tile (`trade-sales-order.contract.md:133`) and the quoted, won and lost values (`trade-sales-enquiry-quotation.contract.md:143-145`) have no currency dimension. The open SO register and dispatch backlog are in the same position.
- What a user experiences: INR and USD amounts are added together as if they were one currency.
- Fix: split every monetary aggregate, tile and export by currency.

### F25 — Rank 6 (Medium): the port contract lacks rows for demand and RMA operations the trade side relies on
- Contract row: POS-T1-10..-12, §8a
- Source: Claude
- Evidence:
  - `po-schedule-port.contract.md:72-75,128,165-167` has no rows for `cancelDemand`, `getFulfilmentPosition` or `getRmaPosition`.
  - It has no DemandOrderChangeGuard guard row (the PO side has `:88`), no idempotency key for demand releases, and no `demand_order.cancelled` / `demand_order.amended` events.
  - The tasks do list them (`issues/p8-02.md:22`, `issues/p8-15.md:29`).
- Fix: add the missing POS rows.

### F26 — Rank 6 (Medium): customer quotation charges have a table but no fields or screen
- Contract row: M8, TSQ §0
- Source: GPT
- Evidence: `trade-sales-enquiry-quotation.contract.md:23` names the table, but `:33-38` (fields) and `:135-140` (screen) say nothing about charges.
- Fix: specify the charge fields and carry them through to the won SO, or remove the table.

### F27 — Rank 6 (Low): the purchase release print has no sales twin and no written refusal
- Contract row: M32
- Source: Both
- Evidence: `issues/p9-14.md:18-22` has `SCHEDULE_RELEASE` for purchase and no dispatch-release kind.
- Fix: add a print, or write the refusal into M32.

### F28 — Rank 7 (Low): release numbering conflicts
- Source: Claude
- Evidence: `issues/p9-02.md:33-34` seeds `PO_RELEASE` and `SO_RELEASE` number series. `trade-sales-order.contract.md:35` and `trade-purchase-order.contract.md:47` number releases `<order>-Dnn` / `-Rnn`.
- Fix: pick one scheme.

### F29 — Rank 7 (Low): customer rating has no scenarios, and the sales firm-zone setting is unnamed
- Source: Claude
- Evidence:
  - WH-SC-547..549 are all purchase scenarios (`FRD-TRADE.md:469-471`).
  - `trade-order-amendment.contract.md:108` counts volatility only for `CUSTOMER_SCHEDULE` origin.
  - FR-611 uses a firm zone without naming a setting (`firm_zone_days` is the purchase one).
- Fix: add sales-rating scenarios and name the sales firm-zone setting.

## Mirror asymmetries (18)
| # | Purchase vs sales | Source |
|---|---|---|
| MA-01 | Release approval `PO_RELEASE` has no sales twin (F17) | Both |
| MA-02 | A PO release cancel has no T1 row (sales has TSO-T1-10) | Claude |
| MA-03 | Ack ladder / `ack_status` / re-ack missing on sales (F6, F10) | Both |
| MA-04 | TSO T2 is one line of prose against TPO's 11 rows | Claude |
| MA-05 | TPO-GRD-05/-10/-11 have no sales twins (F18) | Both |
| MA-06 | Tolerances and the definition of fulfilment `COMPLETE` are missing on sales (F20) | Claude |
| MA-07 | No contract-ceiling consumption on SO releases (F17) | Both |
| MA-08 | No sales release-list screen (twin of WS-294); WS-305/306 have no grid ids, scopes or exports; `wht_so_commitment_followups` has no `:export` | Claude |
| MA-09 | No T4 row for SO cancel / short-close (F20) | Claude |
| MA-10 | No twin of TPO-T3-04 (ack overdue), i.e. no "ack not sent" alert | Claude |
| MA-11 | No release print twin (F27) | Both |
| MA-12 | No sales-rating or sales self-approval scenarios (F29) | Claude |
| MA-13 | The schedule-adherence report has no dispatch-adherence twin | Claude |
| MA-14 | Demand-port rows are thinner than the PO-port rows (F15, F25) | Claude |
| MA-15 | Withdraw missing on sales screens (F12) | GPT |
| MA-16 | Quotation charges less specified than vendor quotation charges (F26) | GPT |
| MA-17 | FIXED orders: PO has no release, SO does (F14) | GPT |
| MA-18 | M6 partial conversion not modelled on sales (F5) | GPT |

## Refusals (credit, invoice, debit/credit note, tax, FX)
- **Clean:**
  - credit (`FRD-TRADE.md:553`, `trade-sales-order.contract.md:101`, `issues/p9-09.md:37`);
  - invoice (`trade-sales-order.contract.md:102`);
  - debit/credit notes (`trade-sales-return-authorisation.contract.md:76`; `CREDIT` only stamps a marker);
  - tax (`FRD-TRADE.md:527`).
- **Not clean:** FX leaks into aggregates (F24).
- **Doc defect:** FRD §1, §3 and §4 cite the refusals as "§10 R1–R5", but §10 holds the open decisions and the refusals are §11 (`FRD-TRADE.md:51,98-100,114-115,246`).

## Dropped after verification
- None.

## Remediation backlog
None of the rows needs a migration or a shared-registry change.

| Finding | Files to touch | Parity apply-to | Contract |
|---|---|---|---|
| F1, F2 | `issues/p8-02.md`, `docs/contracts/po-schedule-port.contract.md`, `trade-sales-order.contract.md` | PO port (p8-01) as reference | POS-GRD new; TSO-T4-01 |
| F3, F21 | `trade-sales-return-authorisation.contract.md`, `issues/p8-15.md`, `issues/p9-13.md` | — | TSR-T1-05, TSR-T4-03 |
| F4, F5 | `trade-sales-enquiry-quotation.contract.md`, `issues/p9-08.md`, `FRD-TRADE.md` | PR partial conversion | TSQ T1/T2/T4 |
| F6, F10 | `FRD-TRADE.md`, `trade-sales-order.contract.md`, `trade-order-amendment.contract.md`, `issues/p9-10.md` | PO ack reset | TSO §1.1, T1-06 |
| F7, F15 | `trade-sales-order.contract.md`, `trade-purchase-order.contract.md`, `po-schedule-port.contract.md`, `issues/p8-02.md` | PO release close/cancel | TSO-T1 new rows; POS demand rows |
| F8, F9 | `trade-approval-matrix.contract.md`, `issues/p9-03.md`, `issues/p9-08.md` | every document type | TAM-GRD-01/-05 |
| F11, F25 | `issues/p8-02.md`, `issues/p8-15.md`, `po-schedule-port.contract.md` | — | POS rows |
| F12, F13 | sales contracts T5; `issues/p9-02.md`, `issues/p9-08.md`, `issues/p9-10.md`, `issues/p9-14.md` | purchase screens and prints | T5 |
| F14, F16, F17, F19, F20 | `trade-sales-order.contract.md`, `trade-rate-contract.contract.md`, `trade-order-amendment.contract.md`, `trade-sales-return-authorisation.contract.md`, `issues/p9-09.md` | PO release / consumption | TSO-T1/GRD/T4 |
| F18 | `trade-sales-order.contract.md` | TPO-GRD-05/-10/-11 | TSO-GRD new |
| F22, F23 | `trade-rate-contract.contract.md`, `issues/p9-06.md` | purchase RC | TRC-GRD-02, T1-07/-09 |
| F24 | sales and purchase T5 sections, `issues/p9-14.md` | every monetary tile | T5 |
| F26–F29 | `trade-sales-enquiry-quotation.contract.md`, `issues/p9-14.md`, `issues/p9-02.md`, `trade-counterparty-evaluation.contract.md`, `FRD-TRADE.md` | — | M32, TCE |

## Parity (C10)
- Mobile: none. The contracts say `none` because of the user rule of 2026-09-11 (`FRD-TRADE.md:568`, R16).
- Sibling modules: single-module (warehouse-trade). The fixes for F1, F2, F15, F21 and F25 belong to core `warehouse` (p8-02, p8-15).

## Contract quality
- TSO §1.1 and §2 are written as prose ("identical to / mirror of TPO"), so neither SO status nor action × role × state can be checked row by row.
- TSO-OPEN-02 (picked-not-shipped per schedule line) blocks TSO-GRD-08/-11.
- The SRA has no expiry field, yet TSR-T4-03 sends `expiryDate`.
- Who receives the dispatch-planner notifications (TSO-T3-01) is not defined.

## Referred to standards reviewer
- None.