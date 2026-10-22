# R29 — functional review (Claude + GPT dual engine), area TRADE-PURCHASE

**Date** 2026-10-22 · **Reviewer** functional-reviewer, pre-build audit mode · **Dispositions** recorded in the area FRD §"R29 dispositions"

**Summary (≤200 words)**

I did not write `/private/tmp/claude-501/-Users-bbhushan-work-git-workspace-classic/53f0e57a-69c7-42b1-a5aa-daa8c13be89a/scratchpad/FR-REVIEW-TRADE-PURCHASE.md`. My agent definition bars me from writing report files, so the full report follows below this summary. Save it from here if you need it on disk.

There are **30 findings**: 5 rank-1 (dead-end or unreachable state), 7 rank-2 (permission / maker–checker), 1 rank-3, 12 rank-4, 2 rank-5, 1 rank-6 and 2 rank-7. Severity: 13 High · 12 Medium · 5 Low.

Top 5:
1. **F1** A BLANKET PO can never be created in core. Before the first release the ordered quantity is 0, which the core rule `IS NULL OR > 0` refuses (`po-schedule-port.contract.md:82`, `:26`).
2. **F2** RFQ and comparative statement dead-end. A rejected statement leaves the RFQ stuck in `EVALUATION`, and an RFQ cannot be cancelled once bids are closed (`trade-rfq-award.contract.md:70`, `:79`, `:86`).
3. **F6** Trade approvers are never given the core port authority `warehouse:orders:port` or `wh_purchase_orders:create/edit`, so every PO approval rolls back (`po-schedule-port.contract.md:28`).
4. **F7** An OPEN PO with no ceiling carries no approval value, and its releases are zero-level, so it is an unbounded commitment (`trade-purchase-order.contract.md:91`).
5. **F14** Release-date pricing (`AT_RELEASE`) cannot reach core: the release call carries no price (`trade-purchase-order.contract.md:165`).

Engines: Claude + GPT (gpt-6.1-sol, medium) — 11 both · 14 Claude only · 5 GPT only · 0 dropped

---

# Functional conformance — TRADE-PURCHASE (P9, `warehouse-trade`, purchase side + shared approval / amendment / evaluation)
Contract: `docs/contracts/trade-{approval-matrix,purchase-requisition,rfq-award,rate-contract,purchase-order,order-amendment,counterparty-evaluation}.contract.md` + `po-schedule-port.contract.md` (all `derived v0 — 2026-10-22`)   |   Mode: audit (pre-build, specification only — no trade code exists)
Files reviewed: 27   |   File set: derived from workflow (FRD-TRADE, FRD-STORES greps, R27 §1, 8 contracts, issues p9-01…07, p9-10…14, 11-EPIC-p9, MODULE-INTEGRATION §2, p8-01/03/04 greps)
Engines: Claude + GPT (gpt-6.1-sol, medium) — 11 both · 14 Claude only · 5 GPT only · 0 dropped

Paths are relative to `/Users/bbhushan/work/git/workspace/warehouse-issues/`. No GitHub issue number was given, so acceptance criteria were taken from FRD-TRADE §4/§7 and the task bodies.

## Verdict
**30 findings.** Every client purchase step is specified (R27 §1 steps 1–3: PR, quotation, FIXED / OPEN / BLANKET with an item × qty × date schedule). So is every standard-practice row: consolidation, RFQ to N suppliers, comparative statement with L1, award reason, rate contract with slabs and validity, releases, amendment and versions, approval matrix, acknowledgement, expediting, short-close, vendor rating and the approved vendor list (AVL) (FRD-TRADE §3 C1–C22).

Several specified ladders still cannot complete, and four core-port seams contradict the trade contract:
- BLANKET create
- validity versus receipt
- release-date (`AT_RELEASE`) price
- deliver-to amendment

Three maker–checker paths are weaker than FR-549:
- AVL approval
- delegation
- the unbounded OPEN PO

**Accounting: clean.** Nothing commits accounting. Refusals are explicit (FRD-TRADE §1 `:49`, §11 R1–R5 `:553-557`; TPO §6 `:203-205`), and `ArchitectureInvariantsTest` (c) forbids `whb_` writes (`issues/p9-01.md:34`). The one indirect risk is in F14: a release-date price that never reaches core would leave core's goods-receipt (GRN) valuation at the old rate.

**Bootstrap: covers the 22 applicable MODULE-INTEGRATION touchpoints**, with rows 23–27 (mobile) correctly marked not applicable. Gaps are in F6 and F30.

## Status reachability
| Status | In CHECK | In contract T1 | Inbound transition | Outbound | UI reachable | Verdict |
|---|---|---|---|---|---|---|
| Approval request PENDING / APPROVED / REJECTED / RETURNED / WITHDRAWN | none by design (D-10) | TAM §1.1 | TAM-T1-03/-04 | T1-05…-09 | WS-285 | identity / rule gaps F7–F12 |
| PR DRAFT → SUBMITTED → APPROVED | none | TPR §1.1 | T1-01/-02/-03 | allocation / cancel | WS-286/287 | ok, except handoff path F13 |
| PR PARTIALLY_ORDERED / ORDERED / CLOSED | none | yes | TPR-T4-01, T1-10 | T1-10 only from ORDERED | system | **dead-end**: all lines closed short with no allocation (F5) |
| PR line `IN_RFQ` (scenario WH-SC-500) | — | **absent** | — | — | — | F29 |
| RFQ ISSUED / BIDS_CLOSED / EVALUATION | none | yes | T1-03/-05, CS submit | CS only; cancel only DRAFT/ISSUED | WS-288 | **dead-end** (F2) |
| Comparative statement (CS) REJECTED | none | yes | approval | none | — | **dead-end** (F2) |
| Vendor quotation (VQ) EXPIRED | none | yes | TRA-T3-03 | revise allowed only from SUBMITTED | — | **dead-end** vs WH-SC-514 (F3) |
| Rate contract APPROVED / TERMINATED / SUPERSEDED | none | yes | approval / T1-07 / T1-09 | early terminal (F15) | WS-291 | F15 |
| PO DRAFT … ACKNOWLEDGED | none | yes | T1-01…-11 | release / amend / short-close / cancel | WS-292/293 | ok |
| PO APPROVED (BLANKET) | — | yes | T1-04 + port create | — | — | **unreachable in core** (F1) |
| PO CLOSED | none | yes | T3-03 | terminal | system | core PO stays open (F22) |
| Release DRAFT / SUBMITTED / RELEASED | none | yes | T1-08/-09/-10 | — | WS-294 | REJECTED / CANCELLED have no transition (F4) |
| Release CLOSED | none | yes | "core release PO closed" | — | — | **trigger impossible** with one core PO per agreement (F4) |
| Acknowledgement PENDING / ACCEPTED / ACCEPTED_WITH_CHANGES / REJECTED | none | yes | T1-11, TOA-T4-03 | — | Ack tab | ok (port drift noted in Contract quality) |
| Amendment DRAFT → APPLIED / REJECTED / CANCELLED | none | yes | TOA-T1-01…-05 | — | WS-296 | withdraw path not listed (Contract quality) |
| Profile BLOCK_PENDING / UNBLOCK_PENDING | none | yes | TCE-T1-02/-03 | through the approval engine | WS-285 | approve authority missing (F11) |
| AVL approval_state PENDING → APPROVED | none | yes | TCE-T1-04 | no reject path | WS-282 | maker–checker not tied to the engine (F10) |
| Evaluation run DRAFT → PUBLISHED → SUPERSEDED | none | yes | TCE-T1-06/-07 | discard | WS-297 | ok |

## Findings

### F1 — Unreachable: an approved BLANKET cannot create its all-FORECAST core PO — High
- Contract row: TPO-T4-01, POS-GRD-02
- Source: Both
- Evidence: `docs/contracts/trade-purchase-order.contract.md:164` sends the whole schedule as `FORECAST`. `docs/contracts/po-schedule-port.contract.md:82` sets "BLANKET_RELEASE: ordered = Σ firm", which is 0 at creation. `:26` defines CHECK `ordered_quantity IS NULL OR > 0`.
- What a user experiences: the approver approves a BLANKET and the port refuses it, so the approval rolls back. WH-SC-529…531 cannot run.
- Fix: in POS-GRD-02, make ordered_quantity `NULL` while Σ firm = 0 (or carry the agreed quantity in `agreement_qty`). Align the CHECK and the create command.

### F2 — Dead-end: a rejected comparative statement and a closed-bid RFQ have no exit — High
- Contract row: TRA-T1-04, -10, -11; TAM-T4-02
- Source: Both
- Evidence: `docs/contracts/trade-rfq-award.contract.md:70` lists CS REJECTED with no exit. `:86` puts the RFQ in `EVALUATION`. `:85` allows Prepare only from BIDS_CLOSED or ISSUED. `:79` allows cancel only from DRAFT/ISSUED and only when "no CS submitted". An RFQ in BIDS_CLOSED with zero responses can leave only through an approved empty statement.
- What a user experiences: after a rejected award, the RFQ stays in EVALUATION forever, and no second statement can be prepared or the RFQ cancelled.
- Fix: define CS reject/return effects on the RFQ (back to BIDS_CLOSED). Allow a new statement after rejection. Allow cancel from BIDS_CLOSED and EVALUATION, with a reason.

### F3 — Dead-end: an expired quotation cannot be extended, although WH-SC-514 requires it — High
- Contract row: TRA-T1-08, TRA-GRD-09, TRA-T3-03, TRA-T4-02
- Source: Both
- Evidence: `docs/contracts/trade-rfq-award.contract.md:130` marks quotations EXPIRED. `:83` allows Revise only from SUBMITTED. `:137` marks only a DRAFT statement stale. `docs/frd/FRD-TRADE.md:411` captures the extension as version 3 and lets the award proceed.
- What a user experiences: the validity-extension recovery cannot be done. If it were done, the pending award would still point at the superseded version-2 line.
- Fix: allow Revise from EXPIRED. On a revision while the statement is SUBMITTED, return the approval request and refresh the statement.

### F4 — Release ladder incomplete: cancel, reject recovery and close — High
- Contract row: TPO-T1-08…-12, TPO-T3-03, T5.3
- Source: Both (Claude adds the released_quantity revert)
- Evidence:
  - `docs/contracts/trade-purchase-order.contract.md:83` lists REJECTED and CANCELLED with no transitions.
  - `:191` offers Cancel on WS-294, and the permission `wht_po_releases:cancel` is declared at `:26`, but no T1 row or port call implements it.
  - `:98` updates `released_quantity` at submit and nothing reverts it on rejection.
  - `:101` closes on "core release PO closed", but there is one core PO per agreement (`:37`).
  - `:156` auto-close needs "no release open".
- What a user experiences: a rejected release permanently consumes schedule quantity. A received release never closes, so the agreement never auto-closes.
- Fix: add release cancel (calling `cancelScheduleLine` for unreceived firm lines) and reject-revert rows. Derive release CLOSED from its own core schedule lines (`release_ref`).

### F5 — Dead-end: a PR whose every line is closed short with no allocation never closes — Medium
- Contract row: TPR-T1-09, -10
- Source: Both
- Evidence: `docs/contracts/trade-purchase-requisition.contract.md:60` (ORDERED needs ≥ 1 allocation), `:77` (close-short), `:78` (CLOSED only from ORDERED).
- What a user experiences: the PR sits in APPROVED with zero open quantity and stays on the "APPROVED (open)" tile.
- Fix: make the header CLOSED when every line is terminal, whatever its allocation.

### F6 — Actor mismatch: trade approvers and SYSTEM are never granted the core port authority — High
- Contract row: TPO-T4-01/-02, TAM-T1-04, POS-T2-04
- Source: Claude
- Evidence: `docs/contracts/po-schedule-port.contract.md:28`: "the port runs as the calling user and requires `wh_purchase_orders:create`/`:edit` plus … `warehouse:orders:port`". No p9 task seeds or bundles these. `grep "orders:port" issues/p9-*.md` returns nothing, and `issues/p9-07.md:28` covers trade permissions only. Zero-level releases are approved by SYSTEM at submit (`issues/p9-03.md:25-27`).
- What a user experiences: a purchase manager with full trade rights approves a PO, the port refuses, and the approval rolls back (WH-SC-524 fails).
- Fix: state the port principal: a service principal, or the trade approver plus a seeded grant. Seed `warehouse:orders:port` and the core verbs into the trade bundles in V551070, with `permission_dependencies`.

### F7 — Weaker control: an OPEN PO with no ceiling is approved with no value and released with no checker — High
- Contract row: TPO-T1-02, TAM-GRD-01, p9-03 zero-level PO_RELEASE
- Source: Claude
- Evidence: `docs/contracts/trade-purchase-order.contract.md:91` ("ceiling value (OPEN; quantity-band rule when no ceiling value)"). An OPEN line has quantity NULL (`:39`), so neither value nor quantity exists to band on. `docs/contracts/trade-approval-matrix.contract.md:73` matches `value ∈ [from,to)`. `issues/p9-03.md:25-27` seeds PO_RELEASE as zero-level for every release. The rule's "within an approved agreement" qualifier is not a matchable condition (`docs/frd/FRD-TRADE.md:127`).
- What a user experiences: the PO either cannot be approved under value-banded rules, or matches a band-less rule at the lowest level. The buyer then calls off unlimited value with no second person.
- Fix: require a ceiling value on OPEN, or route OPEN without a ceiling to a mandatory condition (for example `open_unbounded`). Give PO_RELEASE a value band above which it needs a level.

### F8 — Privilege escalation: an administrator can delegate another approver's authority to themselves — High
- Contract row: TAM-T1-10, TAM-GRD-07
- Source: Claude
- Evidence: `docs/contracts/trade-approval-matrix.contract.md:67` ("`wht_approval_rules:edit` for others"); `:79` refuses only delegate = the approver.
- What a user experiences: a rules administrator records "pm1 → me" and approves pm1's level on pm1's behalf.
- Fix: refuse a delegation whose delegate is the recording user, unless the recorder is the principal. Make delegations to a non-member a maker–checker action, and record who recorded it.

### F9 — Guard gap: a principal can act twice through a delegate — High
- Contract row: TAM-GRD-03
- Source: GPT
- Evidence: `docs/contracts/trade-approval-matrix.contract.md:75` checks only the *actor* for earlier action. `docs/frd/FRD-TRADE.md:126` says anyone who acted at an earlier level cannot act again.
- What a user experiences: pm1 approves level 1, then pm1's delegate approves level 2 as pm1.
- Fix: apply the maker check and the earlier-action check to both the actor and the on-behalf-of principal.

### F10 — Maker–checker missing on AVL changes — High
- Contract row: TCE-T1-04
- Source: Claude
- Evidence: `docs/contracts/trade-counterparty-evaluation.contract.md:81` uses `:create`/`:edit` → `:approve` with no approval-engine reference and no `403`. FR-544 (`docs/frd/FRD-TRADE.md:116`) requires maker–checker, and FR-548 lists `AVL` as an approval document type (`:125`). There is also no reject path.
- What a user experiences: one user holding create + approve puts a supplier on the AVL and approves it.
- Fix: route AVL changes through the approval engine with doc type `AVL` and `403 TRADE_APPROVAL_SELF`; add a reject path.

### F11 — Actor mismatch: `PROFILE_BLOCK` approval has no approve permission — High
- Contract row: TCE-T1-02/-03, TAM-T2-03
- Source: GPT
- Evidence: `docs/contracts/trade-counterparty-evaluation.contract.md:23` (profile verbs `view/create/edit/export/block`, no `approve`); `docs/contracts/trade-approval-matrix.contract.md:25`, `:96` (`wht_<doc>:approve` is the authority); `issues/p9-02.md:39-41`.
- What a user experiences: nobody can approve a block or unblock, so WH-SC-484 cannot complete.
- Fix: add `wht_supplier_profiles:approve` and `wht_customer_profiles:approve`, map PROFILE_BLOCK per side, and seed dependencies.

### F12 — Guard gap: equally specific overlapping rules are not refused — Medium
- Contract row: TAM-GRD-01/-05
- Source: GPT
- Evidence: `docs/contracts/trade-approval-matrix.contract.md:73` (specificity = count of dimensions); `:77` (refused only for an *identical* dimension set); `docs/frd/FRD-TRADE.md:125` ("ties are refused at rule save").
- What a user experiences: a site rule and a department rule with equal specificity both match one PO, and the engine picks one arbitrarily.
- Fix: refuse at save any two intersecting rules with equal specificity, and add a refusal for a tie found at runtime.

### F13 — Missing entry point: the core-initiated PR hand-off has no contract row and returns an unissued number — Medium
- Contract row: TPR-T1-02, FR-528, FR-547
- Source: Claude
- Evidence:
  - `issues/p9-04.md:20-22`: the `PurchaseRequisitionHandoff.raise` bean "creates a PR line … and returns the PR number".
  - `docs/frd/FRD-TRADE.md:119`: drafts are never numbered.
  - `docs/contracts/trade-purchase-requisition.contract.md:70`: the only UI path is WS-287 *Import shortages*. The T5 section (`:136`) puts *Import shortages* on WS-286 instead.
- What a user experiences: a stores user's *Send to purchasing* on a material requisition (MR) creates a PR whose state, maker, permission and number are undefined. The core link shows nothing.
- Fix: add a T1 row: hand-off creates a DRAFT PR or appends to an open one; name the maker; return the draft id/reference; status through the bean. Fix the WS-286/WS-287 placement.

### F14 — Cross-entity: release-date (`AT_RELEASE`) prices cannot reach core — High
- Contract row: TRC-T4-03, TPO-T4-02, POS-T1-06
- Source: Both (Claude adds the expired/terminated case)
- Evidence:
  - `docs/contracts/trade-purchase-order.contract.md:49`: a release line has its own `unit_price`.
  - `:165`: `releaseSchedule` carries line, date, qty and kind only.
  - `docs/contracts/po-schedule-port.contract.md:56`: no price on a schedule line.
  - `:69`: amend changes the *line* rate only.
  - `docs/contracts/trade-rate-contract.contract.md:77`: a terminated contract keeps the "agreement rate", which contradicts `AT_RELEASE` (`:123`).
- What a user experiences: two releases at ₹285 and ₹280 are received in core at one line price, so the GRN valuation is wrong. A release after the contract expires has no defined price.
- Fix: add a price per schedule line, or a firm-time price, to the port and to `wh_purchase_order_schedule_lines`, and use it in GRN valuation. Define `AT_RELEASE` pricing after expiry or termination.

### F15 — Guard conflict: core refuses receipts after `valid_to` that trade promises to accept — High
- Contract row: POS-GRD-06, POS-T3-02, FR-578, FR-585
- Source: Both
- Evidence: `docs/frd/FRD-TRADE.md:175` ("open released quantities continue to be received") and `:182`; `docs/contracts/po-schedule-port.contract.md:86` ("receipt after `valid_to` refuses") and `:117`.
- What a user experiences: a truck carrying a valid, already-released quantity is refused at the GRN one day after validity ends.
- Fix: separate "last release date" from "last receipt date" in POS-GRD-06, so firm open quantity stays receivable.

### F16 — Guard gap: a mixed-currency split award has no valid approval value — Medium
- Contract row: TRA-T1-11, TAM-GRD-01
- Source: GPT
- Evidence: `docs/contracts/trade-rfq-award.contract.md:86` (Σ awarded × landed price); `:108`, `:136` (currencies are not summed or ranked together); `docs/frd/FRD-TRADE.md:527`.
- What a user experiences: an award split across INR and USD cannot be submitted without summing currencies.
- Fix: refuse a mixed-currency statement submission, or open one approval request per currency with atomic completion.

### F17 — Guard gap: release guards are incomplete at submit and at approval — High
- Contract row: TPO-T1-09, -10, -13, -05; TOA-GRD-04
- Source: Both (GPT: approval-time recheck and pending ceiling; Claude: amendment lock)
- Evidence:
  - `docs/contracts/trade-purchase-order.contract.md:99`: approval checks idempotency only, so validity, ceiling, AVL and blocking are not re-checked. Pending releases are not reserved against the ceiling (`:115`).
  - `:98`: BLANKET release omits TOA-GRD-04, which the OPEN release at `:97` includes.
  - `:102` short-close and `:94` cancel also omit it, although `docs/contracts/trade-order-amendment.contract.md:71` refuses releases and short-close while an amendment is open.
- What a user experiences: concurrent pending releases exceed the ceiling. A BLANKET line is released while an amendment is changing it.
- Fix: re-check all release guards under a lock at approval and reserve pending quantity. Add TOA-GRD-04 to T1-09, T1-13 and T1-05.

### F18 — Cross-entity: cancelling a PR does not free its converted MRP / replenishment suggestion — Medium
- Contract row: TPR-T4-02, POS-T1-33, POS-GRD-32
- Source: GPT
- Evidence: `docs/contracts/po-schedule-port.contract.md:187` (markConverted persists CONVERTED) and `:194` (converted once); `docs/contracts/trade-purchase-requisition.contract.md:123` ("on cancel it is free again", read-side join, no core write).
- What a user experiences: the cancelled PR's suggestion stays CONVERTED in core and can never be raised again.
- Fix: add a port `unmarkConverted`/`releaseConversion` operation called on PR-line cancel, or state that cancel keeps the conversion and give a recovery route.

### F19 — Guard conflict: a free-of-charge OPEN line passes trade and is refused by core — Low
- Contract row: TPO-GRD-03, POS-GRD-02
- Source: Both
- Evidence: `docs/contracts/trade-purchase-order.contract.md:111` (0 allowed with the free-of-charge flag); `docs/contracts/po-schedule-port.contract.md:82` (OPEN `unit_price > 0`).
- What a user experiences: approval fails at the port.
- Fix: refuse free-of-charge on OPEN in trade at submit, or relax core with the flag carried in the payload.

### F20 — Rate-contract termination, supersession and amendment have no complete ladder — High
- Contract row: TRC-T1-05, -07, -09, TRC-UNR-03
- Source: Both (GPT: early effect; Claude: undefined approval and amendment entity)
- Evidence:
  - `docs/contracts/trade-rate-contract.contract.md:77`: future-dated termination goes straight to TERMINATED, "approval … termination condition", with no pending state. FR-574 requires approval (`docs/frd/FRD-TRADE.md:166`), and FR-548 has no termination doc type or condition (`:125`).
  - `:79`: SUPERSEDED takes effect at the successor's approval.
  - `:96`: a terminated contract prices nothing.
  - `issues/p9-06.md:13-14` adds `wht_rate_contract_amendments` and an `amendment` condition that are absent from the contract, from FRD §8 (`:508`) and from FR-548.
- What a user experiences: approving next quarter's termination or successor stops today's pricing. A single `:cancel` holder terminates the contract with no checker.
- Fix: add termination and amendment documents with states and approval-engine doc types or conditions. Make TERMINATED/SUPERSEDED effective by date (a resolver predicate or a T3 job).

### F21 — Weaker control: cancelling an approved or issued PO needs no approval, while short-close does — Medium
- Contract row: TPO-T1-05, TPO-T1-13, FR-548
- Source: Claude
- Evidence: `docs/contracts/trade-purchase-order.contract.md:94` (cancel from APPROVED/ISSUED/ACKNOWLEDGED, `:cancel` only) versus `:102` (short-close through the approval engine `PO_SHORT_CLOSE`); `docs/frd/FRD-TRADE.md:125` (no `PO_CANCEL`).
- What a user experiences: one buyer withdraws a commitment already sent to the supplier with no second person.
- Fix: add a `PO_CANCEL` approval doc type (zero-level seedable) for any status after APPROVED.

### F22 — Cross-entity: auto-close never closes the core PO — Medium
- Contract row: TPO-T3-03, POS-T3-02
- Source: Claude
- Evidence: `docs/contracts/trade-purchase-order.contract.md:156` (only `CLOSED` changes, no port call); `docs/contracts/po-schedule-port.contract.md:117` ("close is explicit").
- What a user experiences: the trade PO is CLOSED while its OPEN/BLANKET core PO stays open on WS-072 and in the gate-entry PO picker.
- Fix: the T3-03 job calls `closeOrder` in the same transaction.

### F23 — Cross-entity: supplier-return `REPLACE` reinstatement bypasses the amendment and version engine and has no path on a closed PO — Medium
- Contract row: TPO-T4-07, FR-613
- Source: Claude
- Evidence: `docs/contracts/trade-purchase-order.contract.md:170`; `issues/p9-13.md:14` (the event handler calls `amendOrder` directly); `docs/contracts/trade-order-amendment.contract.md:68`, `:103` (version + 1 only through an amendment); TPO-T3-03 `:156` closes a fully received PO before the QC reject returns.
- What a user experiences: core `revision_no` moves while the trade `version_no` does not. A replacement for a PO that has already auto-closed fails at the port.
- Fix: define reinstatement as a system amendment (origin `SUPPLIER_RETURN`), and state the behaviour on CLOSED, SHORT_CLOSED and open-amendment POs. Hold auto-close while a QC hold or open supplier return exists.

### F24 — Guard conflict: a deliver-to amendment is immutable in core — Medium
- Contract row: TOA change_type `DELIVER_TO`, POS-GRD-09
- Source: Claude
- Evidence: `docs/contracts/trade-order-amendment.contract.md:30`; `docs/contracts/po-schedule-port.contract.md:89` ("never changes … site").
- What a user experiences: the amendment passes trade approval and is refused at apply.
- Fix: limit `DELIVER_TO` to the location within the same site, or remove it from the amendable list.

### F25 — Cross-entity: award to an OPEN PO target moves PR allocations onto a line with no quantity — Low
- Contract row: TRA-T4-04
- Source: Claude
- Evidence: `docs/contracts/trade-rfq-award.contract.md:139` (only RATE_CONTRACT releases all allocations); `docs/contracts/trade-purchase-order.contract.md:39` (OPEN qty null).
- What a user experiences: the PR line shows as ordered against a PO that orders nothing.
- Fix: treat OPEN_PO like RATE_CONTRACT (release the allocations), or allocate against releases.

### F26 — Time rules with recipients but no notification mechanism — Medium
- Contract row: TAM-T3-01, TPR-T3-01/-02, TRA-T3-01, TRC-T3-01/-03, TPO-T3-01…-05, TCE-T3-01…-04, TPR-T1-04/-05/-09
- Source: Claude
- Evidence: every T3 table names recipients ("Notified" column, for example `docs/contracts/trade-purchase-order.contract.md:152`). There is no channel, template or registry in any p9 task: `grep -il notification issues/p9-*.md docs/frd/FRD-TRADE.md` finds nothing, and TAM `:135` defers to "a notification module". FR-560's "notified at each conversion" (`docs/frd/FRD-TRADE.md:142`) has no row in TPR-T4-01.
- What a user experiences: the jobs run and nobody is told.
- Fix: name the platform notification or e-mail-template mechanism and seed the templates per task; add the conversion notification.

### F27 — Expediting and OTIF cover only released lines, so FIXED POs and unreleased past-due BLANKET lines go unexpedited — Medium
- Contract row: TPO-T3-02, TPO-T3-01, TCE `DELIVERY_OTIF`
- Source: Claude
- Evidence: `docs/contracts/trade-purchase-order.contract.md:155` ("open released schedule qty"); WS-295 keys on `releaseNumber` (`:195`); FIXED lines go FIRM at approval with no release (`:164`); `docs/contracts/trade-counterparty-evaluation.contract.md:49`. No rule covers a PLANNED or PROPOSED line whose date passes without a release.
- What a user experiences: an overdue FIXED PO never appears on WS-295 or in vendor OTIF.
- Fix: define "released" to include FIXED firm lines, and add a T3 row for unreleased schedule lines past their date.

### F28 — Screen contracts incomplete — Medium
- Contract row: T5 sections; FR-555, FR-597, FR-616, FR-619
- Source: Both
- Evidence:
  - `docs/contracts/trade-rfq-award.contract.md:150-159`: WS-289 has no tiles; WS-290 has no columns, filters or tiles.
  - `docs/contracts/trade-purchase-requisition.contract.md:139-145`: WS-287 has no filter scope, tiles or grid_preferences.
  - `docs/contracts/trade-purchase-order.contract.md:187-197`: WS-294/WS-295 have no scope, tiles or export; WS-294 has no manual Release action although T1-09 needs one.
  - TPO `:178-180`: no grade column on WS-292 (FR-597).
  - `docs/contracts/trade-approval-matrix.contract.md:127`: no value filter (FR-555 `:132`).
  - `docs/contracts/trade-counterparty-evaluation.contract.md:143-147`: WS-282/283/297/310/311 are column stubs.
  - `issues/p9-14.md:221-224`: 7 reports with no per-report columns or filters.
- What a user experiences: these screens cannot be built or reviewed to FR-616.
- Fix: complete columns, filters and scope, five tiles, actions with state + permission gates, and export for each screen.

### F29 — State inventory drift: PR line `IN_RFQ` — Low
- Contract row: TPR §1.1
- Source: Claude
- Evidence: `docs/frd/FRD-TRADE.md:392` ("PR lines `IN_RFQ`-allocated") versus `docs/contracts/trade-purchase-requisition.contract.md:63` (OPEN / PARTIALLY_ORDERED / ORDERED only). Allocation to an RFQ line therefore reads as ORDERED.
- What a user experiences: the requester sees "ordered" while the line is only out for quotation.
- Fix: add `IN_RFQ` (or `SOURCING`) to the inventory, or reword WH-SC-500.

### F30 — Bootstrap inconsistencies — Low
- Contract row: FR-540, p9-01
- Source: Claude
- Evidence:
  - `issues/p9-01.md:77` seeds `whb_source_systems` in V551000, while `docs/frd/FRD-TRADE.md:504` seeds it in V550011.
  - `issues/p9-01.md:24`: `@PostConstruct` checks only the core module bean, while FRD `:502` says "port beans are checked at start-up".
  - V550000 does not assert `btree_gist`, which p9-02 and p9-06 need for EXCLUDE.
- What a user experiences: a duplicate seed owner, or a late failure at the first EXCLUDE migration.
- Fix: settle the single seed owner; assert the port beans and `btree_gist` in p9-01.

## Dropped after verification
- None. The GPT leg's own "no finding" notes are verifications, not findings: dependency loading, the acknowledgement port, mobile and accounting. I agree with all four. The acknowledgement drift is recorded under Contract quality.

## Remediation backlog
All rows are pre-build specification edits. Migrations named are the already-assigned task blocks; no new version is allocated.

| Finding | Files to touch | Migration | Shared registries | Parity apply-to | Contract |
|---|---|---|---|---|---|
| F1 | po-schedule-port.contract.md → FRD-STORES.md → issues/p8-01.md → trade-purchase-order.contract.md | V510400 (planned) | none | SO BLANKET → demand FORECAST (POS-T1-11) | POS-GRD-02, TPO-T4-01 |
| F2 | trade-rfq-award.contract.md → issues/p9-05.md | none | i18n action labels | sales quotation REJECTED path (trade-sales-enquiry-quotation) | TRA T1 rows for CS reject/return and RFQ cancel |
| F3 | trade-rfq-award.contract.md → FRD-TRADE §7 → p9-05 | none | none | customer quotation versions | TRA-T1-08, TRA-T4-02 |
| F4 | trade-purchase-order.contract.md → p9-07 | V550060 | `wht_po_releases:cancel` dependency | SO dispatch release (trade-sales-order) | TPO release T1/T4 rows |
| F5 | trade-purchase-requisition.contract.md → p9-04 | none | none | enquiry header close | TPR-T1-10 |
| F6 | po-schedule-port.contract.md → trade-purchase-order.contract.md → p9-07, p9-09 | V551070, V551090 | `permission_dependencies`; role bundles | demand-order port (p9-09) | TPO T2 port-principal row |
| F7 | trade-purchase-order.contract.md → trade-approval-matrix.contract.md → p9-03, p9-07 | V550020 seed | none | OPEN SO / dispatch release | TPO-T1-02, TAM condition |
| F8 | trade-approval-matrix.contract.md → p9-03 | V550020 | none | shared engine | TAM-T1-10, TAM-GRD-07 |
| F9 | trade-approval-matrix.contract.md → p9-03 | V550020 (`on_behalf_of` checks) | none | shared engine | TAM-GRD-03 |
| F10 | trade-counterparty-evaluation.contract.md → p9-02 | V551020 | approval doc type AVL | customer item ref approval | TCE-T1-04 |
| F11 | trade-counterparty-evaluation.contract.md → p9-02 | V551020 | `permission_dependencies` | customer profile | TCE §0/T2 |
| F12 | trade-approval-matrix.contract.md → p9-03 | none | none | shared engine | TAM-GRD-05 |
| F13 | trade-purchase-requisition.contract.md → FRD-STORES FR-528 → p9-04 | none | none | none (no sales twin, M5) | new TPR-T1 hand-off row |
| F14 | po-schedule-port.contract.md → trade-rate-contract.contract.md → trade-purchase-order.contract.md → p8-01, p9-06, p9-07 | V510400, V550060 | none | SO AT_RELEASE pricing | POS-T1-06, TRC-T4-03, TPO-T4-02 |
| F15 | po-schedule-port.contract.md → FRD-STORES → FRD-TRADE FR-578 | V510400 | none | demand-order validity | POS-GRD-06, POS-T3-02 |
| F16 | trade-rfq-award.contract.md → trade-approval-matrix.contract.md → p9-05 | none | none | none | TRA-T1-11 |
| F17 | trade-purchase-order.contract.md → p9-07, p9-10 | V550060 if reservation columns are added | none | SO dispatch release, SO short-close | TPO-T1-05/-09/-10/-13 |
| F18 | po-schedule-port.contract.md §8b → p8-16 → trade-purchase-requisition.contract.md → p9-04 | none | none | MFG consumers of `getSuggestionStatus` | POS-T1-3x, TPR-T4-02 |
| F19 | trade-purchase-order.contract.md → po-schedule-port.contract.md | none | none | SO free-of-charge | TPO-GRD-03, POS-GRD-02 |
| F20 | trade-rate-contract.contract.md → FRD-TRADE FR-548 §8 → p9-06 | V550050 | approval doc types / conditions | sales RC, price list | TRC-T1-05/-07/-09, T3 |
| F21 | trade-purchase-order.contract.md → FRD-TRADE FR-548 → p9-03, p9-07 | V550020 seed | none | SO cancel (FR-609) | TPO-T1-05 |
| F22 | trade-purchase-order.contract.md → p9-10 | none | none | SO auto-close → `cancelDemand`/close | TPO-T3-03 |
| F23 | trade-purchase-order.contract.md → trade-order-amendment.contract.md → p9-13 | V550100 (origin value) | none | SRA `REPLACE` release | TPO-T4-07, TOA origin |
| F24 | trade-order-amendment.contract.md | none | none | SO ship-to amendment | TOA change types |
| F25 | trade-rfq-award.contract.md → p9-05 | none | none | quotation win → OPEN SO | TRA-T4-04 |
| F26 | every purchase contract T3 → p9-03…p9-12 | per task `…1` block | notification templates registry | sales T3 rows | T3 "Notified" columns |
| F27 | trade-purchase-order.contract.md → trade-counterparty-evaluation.contract.md → p9-10, p9-12 | none | none | delivery commitments (WS-306) | TPO-T3-02, new T3 row |
| F28 | rfq-award, purchase-requisition, purchase-order, approval-matrix, counterparty-evaluation T5 → p9-02/03/04/05/07/10/12/14 | V5510n1 blocks | `filterUtils.ts` scopes; `CacheConfiguration.java` `statistics.wht*`; WarehouseTradeSafeTranslation | sales screens WS-298…309 | T5 per screen |
| F29 | trade-purchase-requisition.contract.md or FRD-TRADE §7 | none | none | none | TPR §1.1 |
| F30 | issues/p9-01.md → FRD-TRADE §8 | V550000, V550011 / V551000 | none | none | none |

## Parity (C10)
- Mobile: none. The contracts say "mobile: none" because of the user rule of 2026-09-11 (`docs/frd/FRD-TRADE.md:303`, `:568`).
- Siblings sharing this pattern:
  - The sales twin in the same module (FRD-TRADE §5 M1–M33) needs the same fix for F1–F4, F7, F14, F17, F21–F24 and F26–F28; the "Parity apply-to" column above gives the row for each.
  - Core `warehouse` (p8-01, p8-02, p8-16) owns the port side of F1, F14, F15, F18 and F24.
  - No dealer, automotive, accessories, services, insurance or assets sibling carries this workflow.

## In code, not in contract
- `wht_comparative_statements:award` permission (`docs/contracts/trade-rfq-award.contract.md:24`) is used by no T2 row: add it to TRA-T2 or remove it.
- `wht_rate_contract_amendments` plus the `amendment` condition (`issues/p9-06.md:13-14`) are not in TRC or FRD §8: add the TRC amendment ladder (F20).
- Price-row denormalised columns and `is_effective` (`issues/p9-06.md:11-12`) versus the contract's undefined `WHERE (status_active)` (`docs/contracts/trade-rate-contract.contract.md:33-35`): update the contract to the task's form.
- `PurchaseRequisitionHandoff` and `SuggestionConversionOwner` beans (`issues/p9-04.md:20-23`) have no TPR T1 rows (F13).

## Contract quality
- `TPO-T1-11` (`:100`) says core `acknowledged_at` is set through the port; `TPO-T4-05` (`:168`) says it is not. Keep T4-05.
- The PR / PO / rate-contract REJECTED status is editable and resubmittable (it behaves like a return), while an amendment REJECTED is terminal. FR-551's reject/return distinction is applied inconsistently.
- The maker identity for system-drafted documents is undefined: award targets drafted inside the statement approver's transaction (TRA-T4-03), drafts from acknowledgement changes, and hand-off PRs. The statement approver may become the PO "maker" and be barred from approving it.
- The amendment withdraw path (TAM-T1-09) is not listed in TOA T1. Negative-delta banding and the deterministic union of levels are unspecified (`docs/contracts/trade-order-amendment.contract.md:59`).
- TAM-OPEN-01 (role membership resolved at action time) is still only proposed.
- Core and trade both send overdue digests to the buyer (POS-T3-01 and TPO-T3-02): a duplicate notification.
- Validity uses inclusive dates, while price rows are half-open; the end-date conversion is not stated (`docs/contracts/trade-rate-contract.contract.md:33`).
- Could not verify: C3's four implementation links, C5's `@PreAuthorize`, and C8's `filter_definitions` and `getForManagement` forwarding. No trade code exists; re-run in conformance mode per task.
- Deliberate exclusions: the sales contracts (read for parity only), STORES workflows outside the ports, and runtime build/test.

## Referred to standards reviewer
- None (specification review; no code).