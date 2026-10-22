# Verification evidence and limits

## Baseline

- classic commit: `0cdf3d34741581b5bf4a96e7c736e89e2b7c4daa`.
- warehouse-issues design commit: `7b96725eb5850748cd94b2a784466cb16728a55d`.
- Current source inventory: 3,823 production Java files; 487 Java test files; 235 controllers; 225 frontend pages; eight frontend test files across four warehouse modules. These counts are not coverage percentages.
- 411 catalogue rows; 187 have explicit Java test references in the lexical map. Missing references do not establish missing coverage; references do not establish execution.

## Fresh isolated backend gate — PASS

Command: `shared/scripts/ci-gate.sh --committed --out /tmp/warehouse-only-audit-2026-10-01/ci ratchets warehouse`.

| Module | Reported tests | Failures/errors | Skips |
|---|---:|---:|---:|
| warehouse-base | 2,121 | 0 / 0 | 2 |
| warehouse | 2,611 | 0 / 0 | 0 |
| adapter example fixture | 25 | 0 / 0 | 0 |
| warehouse-3pl | 347 | 0 / 0 | 0 |
| warehouse-india | 345 | 0 / 0 | 0 |
| Total | 5,449 | 0 / 0 | 2 |

The two skips are import-handler “no frozen field” assumptions. Source was archived at the commit and tested in a disposable Docker container. The gate excludes `**/*IntegrationTest.java`; many such tests also require `TESTCONTAINERS_ENABLED=true`. This result does not establish DB concurrency, costing integration, rebuild or storage-billing integration. Older local reports are superseded for the tests freshly run.

## Fresh frontend gate — FAIL

Command: `shared/scripts/ci-gate.sh --committed --out /tmp/warehouse-only-audit-2026-10-01/ci frontend`.

Global run: 930 suites, 39 failed; 38,091 tests, 223 failed, six skipped, 37,862 passed. This script treats that broad run as non-blocking; unrelated module failures are not warehouse defects.

Warehouse blocking run: eight suites, four failed; 3,568 tests, 54 failed, 3,514 passed.

| Failed suite | Failed assertions | Interpretation |
|---|---:|---|
| whGridFilterParity | 45 | Scanner misses one-line filter scope syntax and generic forwarding helpers; demonstrated false positives, remaining assertions require triage. |
| whbRegistryLabelFallback | 6 | Seed parser tests, vocabulary classification and label assertions fail; repair parser before asserting all labels are missing. |
| warehouseMobileDecisionGate | 1 | Common literals intersect unrelated mobile domains; native warehouse mobile is deliberately absent. |
| warehouseRegistryOpenness | 2 | Lexical domain collisions, including a legitimate closed job scope; review actual field semantics. |

Passing suites: whbGridFilterParity, warehouseLocales, warehouseBaseLocales, warehouseIndiaLocales. No TypeScript build/typecheck or complete browser acceptance was newly executed. The detailed warehouse failure output is included under `evidence/`.

## Read-only deployed health observations

Backend and PostgreSQL reported healthy; frontend reported unhealthy. Docker's localhost check resolved IPv6 `::1` and connection failed. IPv4 root page returned HTTP 200. **The exact IPv4 `/api/health` endpoint returned HTTP 503** with `Health check failed: environment is not defined`. The current route logs an undeclared `environment` variable. These are two distinct issues; root-page success does not make the health endpoint healthy. No container restart or configuration change was made.

## Research and inspection limits

Reviewed all issue bodies/comment collections, adopted scope/design documents, warehouse contracts/runbooks, source inventories and targeted paths. Historical review comments are evidence of a reported obligation, not proof of current behavior. No live business write, full browser workflow, physical device test, provider call, restore drill, penetration test or benchmark was performed. No claim of zero undiscovered defects is possible from this audit.

Public competitor documentation was used only to check execution-market expectations; links appear in README. Competitor marketing is not evidence of our implementation or of private competitor architecture.
