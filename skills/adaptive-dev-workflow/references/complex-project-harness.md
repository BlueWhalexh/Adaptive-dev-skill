# Complex Project Harness

READ when: Large work, new projects, multi-agent handoff, or repos without reliable current-truth docs.

DO NOT READ for Tiny/Small implementation tasks unless the task is specifically to create, repair, or review the repo's docs/spec harness.

This reference defines the default documentation surface when the repo has no stronger convention. If the repo already uses OpenSpec, follow `openspec-workflow`; use this only to map missing current-truth docs or repo memory around that lifecycle.

## Contents

- Trigger
- Project Harness Init Gate
- Default Layout
- Surface Contracts
- Spec Template
- Plan Template
- Change Note Template
- ADR Template
- Harness Exit Gate
- NEVER

## Trigger

Read this before planning when any condition is true:

- New project or repo bootstrap.
- Large route: cross-module feature, migration, auth/security, data model, public API, user workflow, or cross-service change.
- Multi-agent or multi-session handoff is expected.
- Current truth is scattered across chat history, old specs, stale README, or tribal knowledge.
- The change needs rollout, rollback, compatibility, ownership, or operational recovery.
- The user wants the repo to learn from a first MVP or define a durable agent team.

Do not create the full harness when:

- The task is Tiny/Small and docs structure is not the deliverable.
- A repo has an existing docs/spec convention that already covers the needed surfaces.
- The user explicitly wants a throwaway prototype and accepts the verification/documentation gap.

## Project Harness Init Gate

Initialize the smallest harness that will make the next agent more accurate. Do not create a full enterprise docs tree by default.

Before initializing, state:

```text
Why init is needed: new project, Large work, MVP vertical slice, docs drift, or repeated project memory gap
Existing convention: what docs/AGENTS/skills/specs already exist
Proposed surfaces: only the missing files needed now
Human gate: broad docs or policy files require approval before creation
```

Prefer the standalone `project-harness-init` skill when available. This reference is a conceptual fallback only; it is not a second scaffold implementation. If the standalone skill is unavailable, create missing files manually with the same overwrite, evidence, and local-path hygiene boundaries.

## Default Layout

Use existing repo conventions first. If none exist, propose this lean layout and get approval before creating broad docs:

```text
.
├── AGENTS.md
├── .agent/
│   ├── agents.md
│   ├── knowledge/
│   │   └── candidates/
│   ├── evals/
│   └── runs/
├── .agent/skills/<project-domain>/
│   ├── SKILL.md
│   └── references/
│       ├── architecture.md
│       ├── testing.md
│       └── lessons.md
├── docs/
│   ├── architecture.md
│   ├── adr/
│   ├── specs/
│   │   ├── <feature-id>/
│   │   │   ├── spec.md
│   │   │   ├── design.md
│   │   │   ├── acceptance.yaml
│   │   │   └── changes/
│   │   └── archived/
│   ├── plans/
│   │   └── <feature-id>.md
│   └── evidence/
│       └── <feature-id>.md
```

Use an expanded docs tree only when the repo needs separate canonical surfaces:

```text
docs/
├── canonical/
│   ├── architecture.md
│   ├── contracts.md
│   ├── data-model.md
│   └── runtime.md
├── decisions/
└── runbooks/
└── tests/
```

## Surface Contracts

| Surface | Contract | Never Use For |
| --- | --- | --- |
| `AGENTS.md` / `CLAUDE.md` | Durable agent rules, commands, forbidden actions, review expectations | Feature-specific design detail |
| `.agent/agents.md` | Project agent team roles, reviewer contracts, subagent invocation rules | Always-loaded policy or product requirements |
| `.agent/skills/<project-domain>/SKILL.md` | Repeated project SOP and local context routing | Generic Superpowers/TDD/debug procedures |
| `.agent/knowledge/candidates/` | Unpromoted lessons with evidence and proposed destination | Stable policy |
| `.agent/evals/` | Project route/evidence/failure cases | Implementation scratch notes |
| `docs/architecture.md` or `docs/canonical/architecture.md` | Current module boundaries, ownership, data/control flow, invariants | Historical proposals |
| `docs/canonical/contracts.md` | Public API, events, schemas, auth/error compatibility | Temporary implementation notes |
| `docs/canonical/data-model.md` | Entities, persistence, migrations, compatibility and rollback constraints | ORM tutorial content |
| `docs/canonical/runtime.md` | Services, config, env vars, deployment, observability, recovery | Local-only developer notes |
| `docs/specs/<feature-id>/spec.md` | Intent, scope, non-goals, user/system behavior, acceptance | Implementation diary |
| `docs/specs/<feature-id>/design.md` | Approved design, tradeoffs, architecture impact | Current truth after implementation diverges |
| `docs/specs/<feature-id>/acceptance.yaml` | Machine-readable acceptance and claim ceiling | Narrative design detail |
| `docs/specs/<feature-id>/changes/` | Approved spec deltas after initial approval | Replacing the current spec |
| `docs/specs/archived/` | Completed, abandoned, or superseded specs | Active work |
| `docs/plans/<feature-id>.md` | Staged implementation tasks, owners, gates, evidence, done criteria | Product rationale without executable tasks |
| `docs/evidence/<feature-id>.md` | Fresh evidence, claim ceiling, gaps | Marketing completion summary |
| `docs/adr/` or `docs/decisions/` | ADRs for durable architecture decisions and reversibility | Every minor coding choice |
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

Use under `docs/specs/<feature-id>/changes/` when requirements change after a spec/plan was approved:

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
Spec: `docs/specs/<feature-id>/spec.md` covers goals, non-goals, scope, behavior, compatibility, data/security/runtime impact
Plan: `docs/plans/<feature-id>.md` tasks have gates, delegate skills, evidence, done criteria
Agent team: `.agent/agents.md` exists or is explicitly unnecessary for this scope
Project learning: candidate/project-skill path exists or is explicitly unnecessary
Human gate: unresolved product/API/data/security decisions are approved or blocked
Docs scope: full harness is justified; Tiny/Small work was not inflated
```

## NEVER

- NEVER create the full docs tree for a Tiny/Small task unless the docs harness is the task.
- NEVER treat dated specs, change notes, or chat history as current truth when canonical docs or code disagree.
- NEVER proceed with Large/new-project implementation when current truth is missing unless the user explicitly accepts the gap.
- NEVER replace `writing-plans`, `test-driven-development`, `systematic-debugging`, or `openspec-workflow`; this file defines docs surfaces, not their internal discipline.
- NEVER leave a spec silent on API, data, security, or rollout impact. Write "none" with evidence when not affected.
- NEVER let `.agent/agents.md` become a dumping ground for prompts; keep reusable role contracts only.
