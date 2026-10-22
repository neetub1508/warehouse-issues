I did not write the scratchpad BATCH-PATTERN.md: this agent runs read-only and can't create files, so the full findings are below. Paths are relative to `/Users/bbhushan/work/git/workspace/classic/.claude/` unless absolute.

**1. Batch file structure**
- **Skeleton**, in order (`commands/create-batch.md:95-145`):
  - title and sources
  - "Do not start until <PREV>" line
  - `## MANDATORY JOB TEXT` (copied byte for byte from `tasks/BATCH-STANDARD-PARITY-TEXT.md:9-13`), placed directly above the DRIVER PROMPT
  - DRIVER PROMPT
  - STANDING RULES
  - DEFINITION OF DONE
  - CLOSE COMMENT TEMPLATE (business persona)
  - BLOCKED BY (OD table)
  - PHASE EXIT CRITERION (quoted from the epic)
  - WAVES
  - close-out wave
  - OUT OF SCOPE
  - PARALLELISM
  - PROGRESS
  - `## NEXT`
- **Newer header block** at the top of the file: pipeline always, `ci-gate` manual, integration run in a separate session (`tasks/BATCH-WAREHOUSE-P4.md:3-10`, `tasks/BATCH-ACCOUNTING-P1.md:3-25`).
- **Task line**: `- [ ] **<ID> · #<issue> · [P:lane]|[S]|[B]** — title`, then module and migrations, then `>` notes. Agents append `DONE <date> <SHA/migrations/gates>` notes and stamps under the line (`tasks/BATCH-WAREHOUSE-P4.md:323-338`). Lane markers are defined at `commands/create-batch.md:151-170`.
- **Gates**:
  - Per-task loop: build, then reviewer and functional-reviewer in one message, then tester (driver-serialized), then one fix agent, then a scoped re-verify (`tasks/BATCH-DISPATCH-RULE.md:20-27`).
  - `ci-gate` is never run by the loop; close comments say "ci-gate: not run (on request)" (`tasks/BATCH-DISPATCH-RULE.md:96-114`, `commands/run-batch.md:25-29`).
  - Dual engine: functional-reviewer starts a GPT leg first with `scripts/functional-review-codex.sh start <key>`, does its own review blind, collects with `... wait <key>`, then merges as a verified union. The header line reads `Engines: Claude + GPT …` (`agents/functional-reviewer.md:67-116`).
- **Close**: tick, commit, close the issue with the template (`commands/run-batch.md:35-37`). The driver confirms the SHA with `git show --stat` first (`tasks/BATCH-DISPATCH-RULE.md:192-198`). Gate reports go on the issue as comments, not into files (`:146-172`).
- **Job text**: pasted word for word at the top of every agent prompt; a prompt without it is a defective dispatch (`tasks/BATCH-DISPATCH-RULE.md:36-41`).

**2. Lanes and the shared-registry barrier**
- **S1–S6 are pipeline stages, not lanes** (`tasks/BATCH-DISPATCH-RULE.md:53-60`): S1 PRE-REVIEW, S2 BUILD, S3 VERIFY, S4 FIX, S5 TEST, S6 CLOSE.
- **Rounds** (`:62-94`): each round is one message with up to 4×S1, `--parallel N`×S2 (default 3, file-disjoint lanes), and all pending S3/S4. A PIPELINE table in NOTES tracks each task's stage.
- **Lanes** are `[P:<slug>]` tasks within one wave; a wave is a hard barrier (`commands/run-batch.md:149-208`).
- **Lane briefs**: `tasks/LANE-BRIEF-WAREHOUSE-P4.md:35-48` (hard constraint, commit by name, RETURN block). Also `tasks/LANE-BRIEF-WAREHOUSE-P5.md:39-57` and `tasks/LANE-BRIEF-ACCOUNTING-P1-W3.md:22-27`.
- **Barrier**: lanes may not edit `filterUtils.ts`, `CacheConfiguration.java` or `*SafeTranslation.tsx`; they RETURN the exact lines. One writer applies them in lane order at the end of the wave, under `/tmp/claude-stack.lock`, which also serializes migrations, tester and Docker (`tasks/BATCH-WAREHOUSE-P4.md:35-45,490-507`). A worked example is at `tasks/reports/warehouse-p5-W5/barrier.md`. At `--parallel 1`, agents edit these files directly (`commands/run-batch.md:107-114`).
- **Worktrees vs main**: lanes work on the main checkout. `git worktree list` shows only `main`. The rule is `git pull --no-rebase` and commit by name, never `add -A` or stash (`tasks/LANE-BRIEF-WAREHOUSE-P4.md:41-43`). No worktree isolation is specified (`.claude/worktrees/` exists but is unused by these batches).

**3. Pre-build functional review — yes, before and after**
- S1 posts a `PRE-BUILD FUNCTIONAL REVIEW` gap report (G1..Gn) on the issue. S2 builds exactly those items. S3 proves them closed (`tasks/BATCH-DISPATCH-RULE.md:55-57,79-85`).
- Accounting stamps (`S1 PRE-REVIEW done`, `FR-SWEEP`, `SPEC DECISIONS`) tell the loop to skip S1 (`tasks/BATCH-ACCOUNTING-P1.md:10-24,234-235`).

**4. Issues created before a batch**
- The design repo holds `issues/*.md`, each with front matter `TITLE:`, `LABELS:` and `issue: NN`.
- `issues/create-issues.sh` files the issues and writes `CREATED.md`; `--sync` pushes bodies and `--check` exits non-zero on drift (`/Users/bbhushan/work/git/workspace/accounting/issues/create-issues.sh:1-30,47-63`).
- Labels are taken from `LABELS:` (e.g. `task,accounting,phase-p1,accounting-base`) and created by `ensure_labels`. Repos are `neetub1508/accounting` and `neetub1508/warehouse-issues`; warehouse also has `--file-tbd`.
- Issue numbers reach the batch file through the `#NN` in each task line, read from `CREATED.md` (`commands/create-batch.md:25-27,202-205`).
- Accounting example: `accounting/issues/fr-p0-01.md` (`issue: 177`) feeds the line `FR-P0-01 · #177` in `tasks/BATCH-ACCOUNTING-FR-GAPS.md:9-20`.
- Ad-hoc UI-QA defects are filed with `gh issue create --repo neetub1508/accounting` (`tasks/BATCH-ACCOUNTING-UI-QA.md:151`).

**5. Accounting vs warehouse differences**

| | Accounting | Warehouse |
|---|---|---|
| Source of truth | Read the task file AND the GitHub issue and reconcile them (`BATCH-ACCOUNTING-P1.md:72-77`) | The `.md` file wins (`BATCH-WAREHOUSE-P4.md:83-84`) |
| Money type | `DECIMAL(19,4)` (`BATCH-ACCOUNTING-P1.md:100`) | Lane brief says `DECIMAL(15,2)` unless DATA-MODEL states a type |
| Gate rule | Rule 13 names only reviewer + tester (`BATCH-ACCOUNTING-P1.md:111`) | Rule 12: reviewer + functional-reviewer, then tester (`BATCH-WAREHOUSE-P4.md:105`) |
| Pre-review | Already done (S1 stamps); FR-GAPS batch runs first | S1 runs normally |
| Migration numbers | Pre-allocated, but FR-GAPS takes the next free number at build time (`BATCH-ACCOUNTING-FR-GAPS.md:20`) | Pre-allocated, banded |
| Concurrency | `--parallel 4` (`BATCH-ACCOUNTING-P1.md:443`) | `--parallel 3` |
| Mobile | None | None |
| Persona | Finance manager | Storekeeper |
| Decisions | `BATCH-ACCOUNTING-DECISIONS.md` | — |
| `## NEXT` | Missing in P1 (FR-GAPS has one) | Present |

**6. Loop usage**
- There is no `/loop` usage anywhere in these files.
- The "loop" is `/run-batch`'s own loop: never stop on a blocker, mark it `[!]` and continue, then follow `## NEXT` (`commands/run-batch.md:18-44`). Resume with `/clear` then `--from <ID>` (`:125-133`).
- Multi-session runs record "MACHINE B-C1 … CLAIM/CHECKPOINT" lines in NOTES (`tasks/BATCH-ACCOUNTING-FR-GAPS.md:90-143`).