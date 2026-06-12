# Complex Project Harness

Use this only for Large work, new projects, multi-agent handoff, or repos without reliable current-truth docs. Do not load for Tiny/Small implementation tasks unless the task is specifically to create, repair, or review the repo's docs/spec harness.

This reference defines the default documentation surface when the repo has no stronger convention. If the repo already uses OpenSpec, follow `openspec-workflow`; use this only to map missing current-truth docs or repo memory around that lifecycle.

## Trigger

Read this before planning when any condition is true:

- New project or repo bootstrap.
- Large route: cross-module feature, migration, auth/security, data model, public API, user workflow, or cross-service change.
- Multi-agent or multi-session handoff is expected.
- Current truth is scattered across chat history, old specs, stale README, or tribal knowledge.
- The change needs rollout, rollback, compatibility, ownership, or operational recovery.

Do not create the full harness when:

- The task is Tiny/Small and docs structure is not the deliverable.
- A repo has an existing docs/spec convention that already covers the needed surfaces.
- The user explicitly wants a throwaway prototype and accepts the verification/documentation gap.

## Default Layout

Use existing repo conventions first. If none exist, propose this minimal layout and get approval before creating broad docs:

```text
.
├── AGENTS.md
├── docs/
│   ├── canonical/
│   │   ├── architecture.md
│   │   ├── contracts.md
│   │   ├── data-model.md
│   │   └── runtime.md
│   ├── specs/
│   │   ├── design/
│   │   │   └── YYYY-MM-DD-feature-name.md
│   │   ├── plans/
│   │   │   └── YYYY-MM-DD-feature-name.md
│   │   └── changes/
│   │       └── YYYY-MM-DD-change-note.md
│   ├── decisions/
│   │   └── ADR-0001-title.md
│   └── runbooks/
│       └── verification.md
└── tests/
```

## Surface Contracts

| Surface | Contract | Never Use For |
| --- | --- | --- |
| `AGENTS.md` / `CLAUDE.md` | Durable agent rules, commands, forbidden actions, review expectations | Feature-specific design detail |
| `docs/canonical/architecture.md` | Current module boundaries, ownership, data/control flow, invariants | Historical proposals |
| `docs/canonical/contracts.md` | Public API, events, schemas, auth/error compatibility | Temporary implementation notes |
| `docs/canonical/data-model.md` | Entities, persistence, migrations, compatibility and rollback constraints | ORM tutorial content |
| `docs/canonical/runtime.md` | Services, config, env vars, deployment, observability, recovery | Local-only developer notes |
| `docs/specs/design/` | Approved problem framing, goals, non-goals, options, tradeoffs | Current truth after implementation diverges |
| `docs/specs/plans/` | Staged implementation tasks, owners, gates, evidence, done criteria | Product rationale without executable tasks |
| `docs/specs/changes/` | Dated approved requirement deltas after design approval | Replacing canonical docs |
| `docs/decisions/` | ADRs for durable architecture decisions and reversibility | Every minor coding choice |
| `docs/runbooks/` | Repeatable operational verification, rollback, recovery | Narrative summaries |
| `tests/` | Executable behavior contracts and regressions | Private implementation trivia |

## Spec Template

Use this for Medium/Large design docs when no stronger spec template exists:

```md
# Feature / Change Name

## Problem
What user/system problem is being solved?

## Goals
Observable outcomes that must become true.

## Non-goals
Tempting adjacent work that is explicitly out of scope.

## Current Truth
Code paths, canonical docs, runtime facts, contracts, and known constraints.

## Scope
In-scope modules, out-of-scope modules, ownership boundaries.

## User / System Behavior
State, trigger, expected behavior, error behavior, empty/edge states.

## API / Contract Changes
Request/response/event/schema/auth/error compatibility. State "none" explicitly if unchanged.

## Data Model / Migration
Schema, backfill, compatibility, rollback, data safety. State "none" explicitly if unchanged.

## Security / Permission Impact
Auth, PII, secrets, payment, privilege boundaries, negative cases. State "none" explicitly if unchanged.

## Rollout / Rollback
Flags, deployment order, migration order, recovery path, observability.

## Test Strategy
TDD gates, focused tests, integration/E2E/smoke checks, manual evidence, known gaps.

## Acceptance Criteria
Checklist tied to observable behavior and evidence.

## Open Questions
Questions that block implementation or require user/product decision.
```

## Plan Template

Use this after design approval. If `writing-plans` or `openspec-workflow` is available, follow that skill's method and use this as the expected information surface, not a replacement.

```md
# Implementation Plan

## Approved Spec
Link to design/spec and approved change notes.

## Constraints
Scope limits, no-touch areas, compatibility, security, runtime constraints.

## Tasks
| Task | Files/Modules | Gate | Delegate Skill | Evidence | Done Criteria |
| --- | --- | --- | --- | --- | --- |
| 1 | ... | TDD / Debug / Review / Docs | superpowers:test-driven-development | failing test -> passing test | ... |

## Verification Matrix
| Risk | Check | Command / Method | Required Before |
| --- | --- | --- | --- |

## Review Checklist
Correctness, boundaries, security, data, docs drift, evidence, completion claims.

## Remaining Risks
Known gaps, accepted tradeoffs, follow-ups, owner.
```

## Change Note Template

Use when requirements change after a spec/plan was approved:

```md
# YYYY-MM-DD Change Note

## Previous Decision
What was approved?

## New Information
What changed and where did it come from?

## Impact
Scope, API, data, security, runtime, tests, docs, timeline.

## Decision
Approved change and who/what approved it.

## Required Updates
Spec, plan, canonical docs, tests, runbooks.
```

## ADR Template

Use ADRs only for durable architecture decisions that future agents should not reopen casually:

```md
# ADR-0001 Title

## Status
Proposed / Accepted / Superseded

## Context
Forces, constraints, current truth.

## Decision
What we chose.

## Consequences
Benefits, costs, risks, migration/reversal path.

## Alternatives Considered
Options rejected and why.
```

## Harness Exit Gate

Before implementation starts for Large/new-project work, verify:

```text
Current truth: canonical docs exist or missing surfaces are explicitly listed
Spec: goals, non-goals, scope, behavior, compatibility, data/security/runtime impact
Plan: tasks have gates, delegate skills, evidence, done criteria
Human gate: unresolved product/API/data/security decisions are approved or blocked
Docs scope: full harness is justified; Tiny/Small work was not inflated
```

## NEVER

- NEVER create the full docs tree for a Tiny/Small task unless the docs harness is the task.
- NEVER treat dated specs, change notes, or chat history as current truth when canonical docs or code disagree.
- NEVER proceed with Large/new-project implementation when current truth is missing unless the user explicitly accepts the gap.
- NEVER replace `writing-plans`, `test-driven-development`, `systematic-debugging`, or `openspec-workflow`; this file defines docs surfaces, not their internal discipline.
- NEVER leave a spec silent on API, data, security, or rollout impact. Write "none" with evidence when not affected.
