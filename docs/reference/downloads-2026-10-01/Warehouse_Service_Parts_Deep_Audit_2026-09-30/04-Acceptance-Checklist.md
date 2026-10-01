# Detailed acceptance and failure-case checklist

Research date: 2026-09-30. **These are proposed acceptance cases, not executed tests and not a list of proven defects.** They translate the research into reviewable implementation criteria. Gate letters and gap IDs refer to [the gap register](02-Warehouse-Gaps.md).

Each case should eventually record owner, test fixture, expected result, evidence link, build/version and disposition. Advanced capabilities may be explicitly out of initial scope; do not mark them passed merely because they are deferred. These cases reduce foreseeable rework but cannot guarantee discovery of every future issue.

## Identity, scope and master data

Gate: **A**. Related gaps: **G09, G11–G13, G34, G46**.

- [ ] **AC001** — Same SKU code under two owners stays distinct through import, forecast, export and acceptance.
- [ ] **AC002** — External item rename changes display mapping without creating duplicate demand history.
- [ ] **AC003** — Merged or retired master IDs remain resolvable in sealed historical runs.
- [ ] **AC004** — New item and site can be planned with no ledger movement and an explicit initial-stock assumption.
- [ ] **AC005** — Site activation and retirement mid-horizon include only the correct periods.
- [ ] **AC006** — Customer/contract criticality overrides generic classification only under documented precedence.
- [ ] **AC007** — Invalid supplier-site association blocks that source without hiding other eligible sources.
- [ ] **AC008** — Effective date boundaries use one stated inclusive/exclusive convention, including adjacent records.
- [ ] **AC009** — Unknown external identifiers are quarantined and visible; they are never silently assigned to a default owner.
- [ ] **AC010** — Cross-company transfer needs an authorized business path; geographic proximity alone does not permit it.

## Demand capture and data quality

Gate: **A**. Related gaps: **G01–G03, G10, G24**.

- [ ] **AC011** — A zero-demand day with a complete feed differs from a missing feed day.
- [ ] **AC012** — Redelivery of a source event cannot increment demand twice.
- [ ] **AC013** — Partial fill with a substitute retains requested quantity/item and actual fulfilled quantity/item.
- [ ] **AC014** — Cancellation, return and commercial credit note follow distinct demand-adjustment rules.
- [ ] **AC015** — Late correction supports both corrected-history and as-known training views.
- [ ] **AC016** — Lost-sale import reconciles with later converted orders rather than counting both unintentionally.
- [ ] **AC017** — Warranty consumption can feed physical service demand while remaining excluded from a commercial-sales stream.
- [ ] **AC018** — Internal transfer demand does not duplicate customer demand at the network level.
- [ ] **AC019** — Outlier cleaning retains raw facts, reason, algorithm version and reversible adjustment.
- [ ] **AC020** — Negative quantities, implausible spikes, gaps and duplicate source IDs generate actionable validation results.

## Units, condition and stock eligibility

Gate: **A**. Related gaps: **G13, G16, G34**.

- [ ] **AC021** — Fractional purchase packs convert to base units using frozen line factors and valid indivisibility rules.
- [ ] **AC022** — Supersession ratios have explicit direction and consistent behavior across reciprocal import formats.
- [ ] **AC023** — Quarantined, damaged, expired and blocked stock cannot satisfy serviceable demand unless explicitly eligible.
- [ ] **AC024** — Owner-dedicated stock cannot be pooled into another owner’s recommended supply.
- [ ] **AC025** — Reserved stock and the underlying order are not subtracted twice.
- [ ] **AC026** — Virtual counterparty locations contribute no physical on-hand supply.
- [ ] **AC027** — Lot expiry before expected consumption excludes the affected quantity from usable future stock.
- [ ] **AC028** — Serial applicability or life remaining can invalidate an otherwise interchangeable part.
- [ ] **AC029** — Snapshot omission of zero rows is distinguished from an incomplete extraction.
- [ ] **AC030** — Current on-hand, ATP, transit and projected balance are labeled and independently reconcilable.

## Procurement, receipts and lead time

Gate: **A/B**. Related gaps: **G06–G09, G29, G35**.

- [ ] **AC031** — One PO line received in three lots produces correct remaining dated supply after each receipt.
- [ ] **AC032** — Rejected quantity and QC release delay affect expected serviceable stock.
- [ ] **AC033** — First receipt and final complete receipt generate distinct lead-time measures.
- [ ] **AC034** — Open late orders remain visible in reliability analysis instead of disappearing from completed-order averages.
- [ ] **AC035** — Emergency/VOR lead time is separated from routine procurement behavior.
- [ ] **AC036** — MOQ and order multiple resolve at the correct supplier/site/effective date.
- [ ] **AC037** — An overdue unconfirmed PO is not assumed to arrive today without a stated rule.
- [ ] **AC038** — Currency, price breaks and landed-cost estimates carry validity and source.
- [ ] **AC039** — Capacity allocated to multiple items does not exceed a shared supplier limit.
- [ ] **AC040** — An unavailable on-order provider is reported as unknown supply, not authoritative zero.

## Forecasting and model evaluation

Gate: **B**. Related gaps: **G25–G28**.

- [ ] **AC041** — All-zero, single-event, short-history and sparse-history series have finite documented fallbacks.
- [ ] **AC042** — Missing periods are not converted to zeros during training without a stated completeness rule.
- [ ] **AC043** — Training at each historical origin excludes later corrections and future master information.
- [ ] **AC044** — Seasonal model eligibility has a minimum evidence rule and a baseline comparison.
- [ ] **AC045** — Zero-denominator percentage errors return defined values/status rather than NaN or misleading zero.
- [ ] **AC046** — Model switching requires the configured improvement and preserves selection history.
- [ ] **AC047** — Manual forecast overrides retain baseline and final values for value-added analysis.
- [ ] **AC048** — Occurrence and size parameters in intermittent models are separately traceable.
- [ ] **AC049** — Forecast aggregation/disaggregation conserves totals after rounding and handles zero-share/new children.
- [ ] **AC050** — Uncertainty calibration and service/inventory outcomes are measured at relevant lead-time horizons.

## Inventory policy and constraints

Gate: **B**. Related gaps: **G04–G05, G25, G27–G30**.

- [ ] **AC051** — Unit fill, line fill, cycle service and response-time targets are not treated as interchangeable percentages.
- [ ] **AC052** — Manual critical minimum, no-stock and calculated stock policy have explicit precedence.
- [ ] **AC053** — An expired override triggers the declared effective-policy/recalculation transition.
- [ ] **AC054** — Missing cost prevents cost-based optimization or selects a visibly disclosed alternative objective.
- [ ] **AC055** — Conflicting hard budget, MOQ and critical-minimum constraints yield an infeasibility explanation.
- [ ] **AC056** — Classification thresholds handle ties, no-demand items and changed cost basis deterministically.
- [ ] **AC057** — Lead-time variability and review period are represented in the selected policy method.
- [ ] **AC058** — Safety stock is not double-counted when min/max/order-up-to fields are published.
- [ ] **AC059** — Policy rounding cannot violate stock availability, MOQ or an indivisible unit rule.
- [ ] **AC060** — A network result is not labeled multi-echelon optimization merely because several independent sites were calculated.

## Network, location and transfer

Gate: **B**. Related gaps: **G12–G14, G29, G35, G39**.

- [ ] **AC061** — Planning nodes, warehouses, bins and service territories have distinct identities/roles.
- [ ] **AC062** — A lane change mid-horizon affects future routing but preserves already dispatched transit.
- [ ] **AC063** — Supply graph cycles are rejected or explicitly supported with bounded computation.
- [ ] **AC064** — Two destination proposals cannot reserve the same donor surplus.
- [ ] **AC065** — Donor protection uses its own approved demand/service policy and outstanding commitments.
- [ ] **AC066** — Transit appears once across source, in-transit and destination state transitions.
- [ ] **AC067** — Cross-border, handling, dispatch and receive delays are modeled separately where relevant.
- [ ] **AC068** — Supplier and site holidays apply in their own calendars and timezones.
- [ ] **AC069** — Service-territory reassignment does not silently move physical stock or historical demand.
- [ ] **AC070** — Internal bin replenishment produces a supported warehouse task distinct from an inter-site transfer.

## Supersession, BOM and lifecycle

Gate: **A/D**. Related gaps: **G10–G11, G31–G34**.

- [ ] **AC071** — A→B does not imply B→A interchange without permission.
- [ ] **AC072** — Physical interchange, demand merge and future purchasing successor are separately configurable.
- [ ] **AC073** — A future successor cannot be ordered/fulfilled early unless its source/availability rules allow it.
- [ ] **AC074** — A chain containing a cycle or overlapping incompatible edges produces a clear validation error.
- [ ] **AC075** — An old item’s remaining stock can be depleted without relabeling historic transactions.
- [ ] **AC076** — BOM changes preserve configuration applicability and avoid assembly/component double-counting.
- [ ] **AC077** — Last order date, last delivery date and support-end date are represented independently.
- [ ] **AC078** — Last-time-buy profiles/analogs show evidence quality, approval and demand-decay assumptions.
- [ ] **AC079** — Central and regional last-buy plans do not both purchase the same requirement.
- [ ] **AC080** — New-product initial provisioning is distinguishable from an ordinary historical forecast.

## Repair, cores and installed base

Gate: **D**. Related gaps: **G31–G33**.

- [ ] **AC081** — Expected returned cores and physically received cores cannot simultaneously create duplicate supply.
- [ ] **AC082** — Return loss, no-fault-found rate, repair yield and scrap are distinct parameters.
- [ ] **AC083** — Inspection delay and repair processing delay affect the usable-supply date.
- [ ] **AC084** — Repair capacity and purchase capacity can constrain different actions independently.
- [ ] **AC085** — Repair-versus-buy compares permitted options, cost basis and service date.
- [ ] **AC086** — Serial compatibility and life remaining constrain repair/reuse when the customer requires them.
- [ ] **AC087** — Installed-base exposure ends on retirement and starts on the valid commissioning date.
- [ ] **AC088** — Incomplete telemetry does not imply zero utilization or zero failures.
- [ ] **AC089** — Host failure rate versus calculated rate follows explicit provenance/evidence thresholds.
- [ ] **AC090** — Equipment uptime is measured from equipment/service evidence, not inferred from warehouse fill rate.

## Historical state and simulation

Gate: **A/B**. Related gaps: **G16–G20, G45**.

- [ ] **AC091** — Corrected history and as-known history are separately selectable and labeled.
- [ ] **AC092** — Source cutoff and business date appear on every run and exported result.
- [ ] **AC093** — A concurrent movement between snapshot cursor capture and scan is counted once after replay.
- [ ] **AC094** — All run inputs include immutable master, network, calendar and policy versions.
- [ ] **AC095** — Identical manifest/model/seed reruns meet the declared deterministic tolerance.
- [ ] **AC096** — Synthetic initial inventory and warm-up assumptions are visible in comparisons.
- [ ] **AC097** — Pause/resume uses the original input versions; input changes require a fork/new run.
- [ ] **AC098** — Abort and restart have explicit cleanup and audit behavior.
- [ ] **AC099** — Historical evaluation can use later demand as outcome without leaking it into historical decisions.
- [ ] **AC100** — Simulation cannot publish orders, notify suppliers, post accounting or alter live policies.

## Recommendation approval and execution

Gate: **A/C**. Related gaps: **G22–G23, G29–G30**.

- [ ] **AC101** — Approval carries the exact recommendation version and authorized edits.
- [ ] **AC102** — A newer manual policy override makes a conflicting old recommendation stale.
- [ ] **AC103** — Identical retry after lost acknowledgment returns the original execution document.
- [ ] **AC104** — Reuse of an idempotency key with a different payload is refused.
- [ ] **AC105** — Concurrent acceptance validates donor stock/budget/capacity at the point of execution.
- [ ] **AC106** — Partial batch acceptance is reported per line with recoverable state.
- [ ] **AC107** — Approval, command acceptance, supplier acknowledgment, dispatch and receipt are distinct milestones.
- [ ] **AC108** — A second planning run sees previously accepted supply and avoids duplicate orders.
- [ ] **AC109** — Rejected recommendations preserve reason and distinguish temporary suppression from policy change.
- [ ] **AC110** — Cancellation after dispatch invokes a business exception rather than rewriting execution history.

## Orchestration and recovery

Gate: **B/C**. Related gaps: **G14–G15, G21–G23**.

- [ ] **AC111** — Overlapping scopes cannot publish contradictory policies simultaneously.
- [ ] **AC112** — A worker with an expired lease cannot publish after another worker takes over.
- [ ] **AC113** — Step retry resumes from durable state without duplicate business effects.
- [ ] **AC114** — Invalid-data failure differs from transient infrastructure failure and has a suitable recovery path.
- [ ] **AC115** — Scheduler behavior is defined for daylight-saving repeated/skipped times.
- [ ] **AC116** — Missed runs follow an explicit catch-up/coalescing rule.
- [ ] **AC117** — Manual run has defined interaction with the next scheduled run.
- [ ] **AC118** — Cancel/pause requests stop at safe checkpoints and disclose any already committed output.
- [ ] **AC119** — A kill switch prevents new automatic release immediately and shows pending reconciliation.
- [ ] **AC120** — Recovery after database restore does not reissue already executed procurement.

## Security, permissions and audit

Gate: **A/C**. Related gaps: **G13, G20, G40, G47**.

- [ ] **AC121** — Company/site/owner grants apply to forecast rows, scenario copies and exported files.
- [ ] **AC122** — Cost permission masking remains effective in explanations and aggregate dashboards.
- [ ] **AC123** — Scheduled report recipients receive only data within their own effective permissions.
- [ ] **AC124** — Copying or sharing a scenario cannot widen the creator’s or recipient’s access.
- [ ] **AC125** — Approval and release rights are separated according to configured governance.
- [ ] **AC126** — Background workers use scoped service identities and do not inherit arbitrary planner privileges.
- [ ] **AC127** — Immutable audit links actor, reason, input version, approval and execution result.
- [ ] **AC128** — Credentials and sensitive source payloads do not appear in model logs or explanations.
- [ ] **AC129** — Any AI assistant uses authorized retrieval and normal command approval checks.
- [ ] **AC130** — Deletion/retention handling removes required data without falsely claiming old runs remain reproducible.

## Planner workflow and explanations

Gate: **B**. Related gaps: **G04, G23, G41–G42**.

- [ ] **AC131** — Each recommendation shows stock, demand, supply, target and constraint contributions.
- [ ] **AC132** — Planner can distinguish unavailable data, no forecast and a true zero forecast.
- [ ] **AC133** — Bulk edits preview scope and conflicts before applying authorized changes.
- [ ] **AC134** — Override form requires reason and shows duration/expiry and impacted downstream outputs.
- [ ] **AC135** — Acknowledging an exception does not mark the underlying condition resolved.
- [ ] **AC136** — Repeated identical conditions are grouped while material changes remain visible.
- [ ] **AC137** — Baseline/scenario comparison uses matching scopes, costs and time windows.
- [ ] **AC138** — Export retains units, timezone, version, assumptions and filter scope.
- [ ] **AC139** — Automation screen shows active level, allowed actions, caps and last complete data cutoff.
- [ ] **AC140** — No explanation invents causal certainty or hides an infeasible/approximate result.

## KPIs, reconciliation and pilot evaluation

Gate: **A/B**. Related gaps: **G18–G19, G27, G36, G46**.

- [ ] **AC141** — Historic stock reconciles opening balance plus all relevant movements, including stock older than one year.
- [ ] **AC142** — Quantity/value reconciliation distinguishes timing variance from actual mismatch.
- [ ] **AC143** — Fill-rate denominators handle split lines, cancellations, substitutions and unfilled demand explicitly.
- [ ] **AC144** — Turns/days-supply/obsolescence metrics state cost basis and observation window.
- [ ] **AC145** — Pilot compares against existing manual/min-max baseline on the same scope.
- [ ] **AC146** — Stockout censoring and missing demand are disclosed when interpreting forecast performance.
- [ ] **AC147** — Actual service benefit and inventory change are reported with sufficient observation period and uncertainty.
- [ ] **AC148** — Planner workload, approval time and exception volume are measured alongside stock KPIs.
- [ ] **AC149** — Accounting-integrated mode reconciles with its actual provider and GL interface.
- [ ] **AC150** — Benefits claimed in sales material are traceable to measured customer evidence rather than vendor percentages.

## Performance, migration and commercial readiness

Gate: **A/B/C**. Related gaps: **G36–G38, G43–G48**.

- [ ] **AC151** — Benchmark records active pairs, history size, supply lines, chain depth, concurrency and hardware.
- [ ] **AC152** — Planning batch does not hold long stock-ledger write locks or violate the agreed execution latency budget.
- [ ] **AC153** — Backfill/import is restartable, rejects malformed data and reconciles before activation.
- [ ] **AC154** — Model/schema upgrade runs old/new versions against a retained manifest before promotion.
- [ ] **AC155** — Additive migration preserves execution consumers and historic interpretation.
- [ ] **AC156** — Storage, event and model retention costs are measured against customer pricing assumptions.
- [ ] **AC157** — Customer export includes documented identities, units, versions and open workflow state.
- [ ] **AC158** — Onboarding identifies source owner, data readiness, cutover plan and support responsibility.
- [ ] **AC159** — Published scale/features match measured deployment and purchased/enabled modules.
- [ ] **AC160** — Production readiness includes CI, restore, permissions and representative warehouse execution evidence.

## Tracking

Total: **160 proposed acceptance cases** across 16 areas. Record failures against existing issues where applicable; create new backlog items only after checking duplicates and adopted design decisions. No GitHub issues were created or edited by this research task.
