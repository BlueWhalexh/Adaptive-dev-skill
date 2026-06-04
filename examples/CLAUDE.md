# CLAUDE.md

This project uses Adaptive Dev Workflow for agentic development.

## Operating Rule

For implementation, fix, refactor, design, and planning tasks, use `adaptive-dev-workflow`.

Choose the lightest process that still protects correctness:

- Tiny for docs, typos, config, and obvious one-step edits.
- Small for narrow fixes with clear behavior.
- Medium for new behavior, 1-3 modules, or meaningful edge cases.
- Large for cross-module work, migration, auth, security, data model, or user-facing workflows.
- OpenSpec when this repository already has an OpenSpec lifecycle or the change needs durable specification.

## Project Facts

Before changing files:

- Read `README.md`.
- Inspect the relevant source, tests, and configuration.
- Check current git status.
- Follow existing patterns before introducing new abstractions.

## Verification

Do not claim completion without fresh evidence.

Use the narrowest verification that proves the claim:

- docs-only: run `git diff --check`.
- frontend: run relevant component/unit tests and use a browser check when UI behavior matters.
- backend: run relevant targeted tests and verify API contracts when affected.
- security/auth/data: add or run regression coverage and call out review risk.

If verification cannot be run, state why and what risk remains.

## Stop Conditions

Stop and ask before continuing if the work requires changing:

- goal or scope
- public API
- data model
- security posture
- user-facing behavior
- dependencies
- deployment or runtime assumptions

Also stop before destructive operations, secret handling, or network-dependent setup that was not already approved.

## Boundaries

- Do not perform unrelated refactors.
- Do not commit secrets or local-only files.
- Do not invent benchmark, user, test, or command results.
- Do not keep coding through ambiguity when the ambiguity changes the implementation.

## Final Report

Final responses should include:

- changed files or behavior
- verification commands and results
- known gaps or remaining risk
- review focus: correctness, boundaries, safety
