# Final instruction and coverage verification

2026-09-11. This verifies requirements/task instructions, not runtime implementation or the installation of a Claude skill. No `.claude` skill folder was present in this repository. CLAUDE.md now points to the existing authorities and task format.

All 35 amended task source files retain their metadata, parent/module/migrations/screens header, Scope, Requirements closed, Scenarios closed, Closes, Traps and Acceptance sections. Solutions stay in Scope, and verifiable outcomes stay in Acceptance. Shared settings implementation belongs to P0-15/P1-20; consumers validate only their own affected workflow. Later-version capabilities remain later-version work, and historical rejected tax-engine prose does not become active build scope.

The existing design checker verifies all 143 tasks against the implementation plan, one phase parent per task, exactly one task owner per functional requirement, valid scenario/finding/screen references and non-conflicting migration allocation. The existing [reconciliation inventory](REQUIREMENTS-SOLUTION-RECONCILIATION.md) covers 203 original Markdown files and 152 open issues. These are structural/traceability checks, not a guarantee that no future runtime defect or new business requirement will arise.

Finalize with the existing requirement decisions and defaults. Customer credentials, company setup and validated optional providers remain installation inputs. Do not ask a human to repeat adopted decisions, create duplicate configuration infrastructure, or implement speculative choices. Run task-specific behavior tests plus existing required checks in the implementation checkout before declaring software complete.
