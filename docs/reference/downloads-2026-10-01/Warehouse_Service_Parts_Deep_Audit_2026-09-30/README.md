# Warehouse foundation and service-parts planning research

**Date:** 30 September 2026  
**Purpose:** strengthen the existing warehouse before introducing service-parts planning for small and midsize customers. Use PTC Servigistics and other vendors as references; select practical capabilities rather than promise full enterprise parity.

## Main conclusions

1. **Keep the warehouse execution foundation.** Stock/owner identities, transactional outbox, daily stock snapshots, calendars, procurement and replenishment provide useful starting points.
2. **Fix the data contracts first.** Monthly demand totals, aggregate on-order quantities and mutable stock policies alone cannot support reliable historical replay, time-phased supply or safe automated policy publication.
3. **Resolve source/site and supersession behavior.** The supplier-site issue was closed as a duplicate; current supplier-source code does not prove site-specific preferences. Demand merging and requested-versus-fulfilled lineage need explicit end-to-end validation.
4. **Separate calculation from execution.** Versioned runs should produce explainable recommendations; approved recommendations enter the warehouse through idempotent, authorized APIs with current-state checks.
5. **Start with advisory planning for the intended customer.** Add bounded automatic release after data reconciliation, baseline comparison and recovery evidence. Reserve advanced repair, asset and network methods for validated demand.

## Read the pack

| File | What it contains |
|---|---|
| [01 — Competitor reference](01-Competitor-Reference.md) | 37 sections on PTC, eight other vendors, implementation details, methods and evidence limits |
| [02 — Warehouse gaps](02-Warehouse-Gaps.md) | 48 numbered gaps/decisions with status, owner, gate, evidence and acceptance criteria |
| [03 — Architecture and contracts](03-Planning-Architecture-and-Contracts.md) | Proposed architecture, 20 design decisions, input/run/publication contracts, historical state and automation |
| [04 — Acceptance checklist](04-Acceptance-Checklist.md) | 160 proposed acceptance cases across 16 areas; none represented as executed tests |
| [05 — Sources and issue coverage](05-Sources-and-Issue-Coverage.md) | Source/version register, all 45 open issues and remaining validation work |

## Your specific PTC questions

- **Snowflake:** confirmed in the documented PAI Advanced analytics path. This is not evidence that it is PTC’s stock ledger or universal optimization engine. See file 01 §§3–4 and the [PTC installation guide](https://trne-prod.ptcmanaged.com/servigistics_help/en/PTC_Servigistics_Help_Center/install/install_planning_advanced_snowflake.html).
- **Going back in time / manual state:** distinguish a manual base-date run, saved snapshot, modeling instance and historical simulator. The remembered phrase “manual state” remains unconfirmed. See file 01 §§6–10.
- **AutoPilot:** documented configurable batch processes and scheduling. Our equivalent needs durable steps, recovery and controlled publishing, with separate permissions for automatic execution. See file 01 §§5–7 and file 03 §7.
- **Location:** planning nodes, coverage territories, lanes and warehouse bins are different concepts. Preserve execution identities while introducing effective-dated planning relationships. See file 01 §21 and file 03 §3.

## Capability comparison at a glance

This is an evidence-based orientation, not a complete commercial feature matrix. A vendor absent from a row may still offer that capability.

| Capability | Competitor references documented in file 01 | Existing warehouse position | Recommended response |
|---|---|---|---|
| Physical stock and execution | Competitors integrate with execution systems; Baxter also emphasizes execution workflow | Substantial existing execution foundation | Reuse; validate current release blockers |
| Demand forecasting | PTC method catalog; ToolsGroup probabilistic demand; Smart planning | Monthly demand/lost-sales recording, no verified SPI runtime | Add source facts and validated baseline/intermittent models |
| Stock policies | PTC service/cost trade-offs; Smart policy analysis; Netstock replenishment visibility | Manual policy fields and threshold replenishment; #99 open | One calculated-policy owner, versioned overrides |
| Network optimization | PTC network/MEO; Syncron network; ToolsGroup network inventory | Sister-surplus heuristic and transfer execution | Effective network/lane model first; joint optimizer later |
| Supersession | PTC chains; SAP/Oracle planning interactions; Netstock import ratios | Base supersession and partial requested-item support; #168 open | Validate directional applicability, merge semantics and conversions |
| Dated supply | PTC time-phased planning and capacity | PO line dates exist; aggregate on-order contract | Publish detailed dated commitments |
| Historical scenarios | PTC snapshots/modeling/simulator | Daily stock snapshots exist; no established full planning manifest | Preserve all run inputs and as-known state |
| Automation | PTC AutoPilot; vendor execution integration | Jobs, events and retry infrastructure | Planning DAG and safe recommendation acceptance |
| Repair/installed base | PTC, Baxter, Oracle | Planning integration not established; prior adapters intentionally removed/deferred | Optional gated data contracts and capability |
| Lifecycle/last buy | PTC lifecycle profiles; Baxter lifecycle | Future planning scope | Support-horizon/risk model when needed |
| Analytics | PTC PAI/Snowflake; multiple vendor dashboards | Existing warehouse reports/KPIs | Versioned planning read models; scale infrastructure by evidence |

## Scope and confidence

This pack reviews public technical documentation, selected current vendor pages, local source and warehouse GitHub issues. PTC technical help identifies **13.1.0.5**; individual release notes and the August 2025 SaaS description have their own versions. Other-vendor material ranges from technical documentation to marketing; that distinction is retained in the reference file.

It is a broad, detailed planning baseline, **not a claim that every proprietary vendor feature or every repository path was exhaustively verified**. Hidden algorithms, complete current API contracts, tenant internals and commercial terms require vendor evidence. No runtime test suite, benchmark, deployment or penetration test was performed. Open issues are reported dependencies, not newly reproduced defects.

The eight additional vendors are **Syncron, Baxter Planning, ToolsGroup, Smart Software, Netstock, SAP, Oracle and Lokad**. Exact comparative pricing, market share and exclusive midmarket positioning were not established. Avoid the earlier assumptions that PTC only serves large customers, every alternative exceeds a particular price, or competitors lack execution integration.

## What changed from the earlier comparison

The earlier Downloads comparison remains available. This pack expands it and corrects the supplier-site implementation assumption, distinguishes existing snapshots/jobs from missing planning semantics, and replaces broad competitor claims with source-qualified findings. It also identifies revisions needed in the existing `docs/spi` drafts. Repository files, user edits and GitHub issues were left unchanged.

## Immediate work order

1. Adopt the data/time/identity and policy-authority decisions in file 03.
2. Reconcile the existing issues linked in file 02 and verify supplier-site scope against current code.
3. Implement ingestion completeness, event/snapshot reconciliation and source-level demand/supply projections.
4. Run baseline policy/forecast calculations in isolated shadow mode with explanations.
5. Prove reviewed write-back, concurrency and recovery; then consider bounded automation.

Treat the gap register as an input to backlog refinement. Resolve duplicates and existing adopted decisions before creating implementation issues.
