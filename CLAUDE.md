# Working with the warehouse requirements repository

This repository contains requirements and source Markdown for the backlog, not application implementation. These instructions preserve the existing workflow; they do not install a Claude skill or replace instructions in an implementation checkout.

## Read and follow the existing authority

Read docs/DECISIONS.md first, then issues/README.md and the assigned issues/p*.md. Follow its Requirements closed, Scenarios closed, Closes and Traps references. DECISIONS owns precedence; docs/GLOBAL-SETTINGS-DECISIONS.md is its adopted amendment, not a second decision hierarchy. DATA-MODEL owns schema/migration allocations; BUILD-SPEC-SCREENS owns screen contracts. Historical rejected/superseded sections are evidence, not active build scope.

Preserve TITLE/LABELS/issue metadata, the Part of/Module/Migrations/Screens header, and the existing Scope, Requirements closed, Scenarios closed, Closes, Traps and Acceptance sections. Put a solution in Scope and verifiable outcomes in Acceptance. Edit source Markdown first. GitHub bodies must be rendered with the existing placeholder rules and synchronized only for changed issues after checking for concurrent edits; never overwrite unrelated issues. Do not create duplicates or reopen closed duplicate issues.

Run `python3 tools/check-design-set.py --summary` after requirements/task changes. Verify affected GitHub issue bodies match their rendered source. The checker validates structure and traceability, not working software.

## Implementation discipline

Work one assigned task at a time, in its declared module and version. Preserve existing identifiers, migrations, permissions, task ownership and history. Do not implement later-version features just because a document mentions them. Do not delete requirements or replace the established task format.

Use the documented default without asking the human to choose again. Offer only the alternatives explicitly allowed by the settings catalogue, through the existing settings page. Setup data such as company currency, credentials and provider accounts remains customer input; missing input blocks only the operation that needs it. Ask one concrete question only if there is a material contradiction with no authoritative resolution or a genuinely new business requirement. Do not guess secrets, financial facts or statutory rules.

Reuse existing services, settings storage, permissions, provider ports and audit facilities. Implement shared settings validation and UI once in its owning task; consumers read the effective value and enforce their own workflow guard. Do not create a second configuration engine, generic policy DSL, new microservice, extra approval workflow, or provider adapter for a hypothetical future customer. Disabled later-version capability requires a clear refusal, not an early implementation. Keep mandatory integrity and access checks.

Test the task's own acceptance cases and directly affected integration/refusal/retry paths. Shared settings tests belong to the settings owner; consuming tasks prove their own setting-dependent behavior rather than rebuilding that suite. Keep existing required checks. Record what changed, validation performed and actual remaining dependencies; an open implementation issue is not closed merely because its specification is complete.
