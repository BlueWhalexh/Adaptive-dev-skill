# Project Agent Team Manifest

READ when: new project harness is initialized, Large/complex work needs multiple reviewer roles, the user asks to define an agent team, or a repo needs durable subagent/reviewer responsibilities.

DO NOT READ for Tiny/Small tasks or when a project already has a stronger team/role convention.

## Contents

- Purpose
- File Location
- Minimal Manifest
- Role Contracts
- Suggested Roles
- Invocation Rules
- Maintenance Rules
- NEVER

## Purpose

`AGENTS.md` tells agents what rules to follow. The project agent team manifest tells the main agent which specialist roles exist, what they review, and what evidence they must return.

This keeps subagent usage structured without hard-coding ad hoc prompts in every task.

## File Location

Prefer:

```text
.agent/agents.md
```

Use existing project conventions if present. Keep this separate from root `AGENTS.md` so always-loaded policy stays short.

## Minimal Manifest

```md
# Project Agent Team

## Rules

- Agents are read-only unless a task explicitly grants write scope.
- Agents must return evidence, file paths, and uncertainty; no broad rewrites.
- Agents must not invent product requirements.
- The main agent owns final integration and claims.

## Roles

| Role | Trigger | Inputs | Output | Must Not |
| --- | --- | --- | --- | --- |
| repo-grounder | New area or stale docs | Goal, paths, docs | Current truth map, risks | Edit files |
| spec-reviewer | Medium/Large design | Spec, acceptance | Gaps, ambiguity, risk | Redesign silently |
| plan-reviewer | Before plan execution | Plan, code map | Missing tasks/gates | Implement |
| evidence-reviewer | Before completion | Diff, evidence | Claim ceiling, gaps | Accept mock as real |
| security-reviewer | Auth/data/secrets | Diff, threat areas | Boundary risks | Guess compliance |
| knowledge-curator | Task exit | Candidate, evidence | Promote/reject advice | Write policy directly |
```

## Role Contracts

Each role should define:

```text
Trigger: when to use this role
Inputs: minimum context to provide
Output: required format
Allowed actions: read-only or scoped writes
Must not: forbidden behavior
Evidence: what counts as a useful result
```

Keep roles small. A role that reviews everything will review nothing well.

## Suggested Roles

| Role | Use When | Output |
| --- | --- | --- |
| `repo-grounder` | Unknown area, new project, docs drift | Current truth, file map, known constraints |
| `spec-reviewer` | Spec/acceptance before Medium/Large work | Ambiguity, missing non-goals, risky assumptions |
| `design-reviewer` | Architecture tradeoff or public contract | Option risks, compatibility, rollback |
| `plan-reviewer` | Before staged implementation | Missing tasks, sequencing risk, gates |
| `task-reviewer` | After a focused implementation task | Correctness, tests, scope creep |
| `evidence-reviewer` | Before completion or handoff | Evidence quality, mock/real labels, claim ceiling |
| `security-data-reviewer` | Auth, permission, PII, secrets, migrations | Negative cases, data safety, rollback |
| `knowledge-curator` | After MVP or repeated lesson | Candidate quality and destination |

## Invocation Rules

- L0/Tiny: no team role by default.
- L1/Small: use a role only when cause or validation is unclear.
- L2/Medium: use at least one isolated review for plan or evidence when risk is meaningful.
- L3/Large: use separate review for design/plan/evidence; add security/data role when relevant.
- Delivery handoff: use evidence reviewer and fresh consumer when the claim requires it.

Pass only the minimum complete context: goal, scope, current truth sources, constraints, expected output, and what not to change.

## Maintenance Rules

- Update `.agent/agents.md` only when a role is reused or a review gap recurs.
- Keep project team roles scoped to the repo.
- Retire roles that are unused or duplicate another role.
- Do not copy this entire reference into project manifests; generate the smallest useful team.

## NEVER

- NEVER use a subagent as a substitute for missing acceptance criteria.
- NEVER let a reviewer approve its own implementation.
- NEVER give broad write access to a reviewer role by default.
- NEVER create roles for Tiny tasks just because the team manifest exists.
- NEVER put secrets or private production data in subagent prompts.
