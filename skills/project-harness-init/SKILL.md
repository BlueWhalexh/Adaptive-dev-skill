---
name: project-harness-init
description: "Initialize or repair a project AI coding harness: AGENTS.md, OpenSpec-first or Superpowers-fallback spec/design/plan routing, docs/evidence, Goal Loop Mode prompt, agent team roles, project-local skill, learning candidates, and delivery verification templates. Use when starting a new repo/product area, first MVP vertical slice, Large feature lacking current-truth docs, repeated user explanations, weak project agents, missing spec/technical-design/plan/evidence contracts, or when adaptive-dev-workflow routes to project harness initialization. 当需要项目初始化、目标模式、OpenSpec 优先或 Superpowers fallback 的 spec/technical design/plan/evidence、项目 agent 团队、项目 skill、AGENTS.md、交付验证或 Loop Engineering 基座时使用。"
---

# Project Harness Init

## Overview

Use this skill to create the smallest durable project harness that lets an agent work in Goal Loop Mode without repeatedly asking the user for the same engineering rules. It initializes current-truth docs, spec/design/plan routing, evidence records, reviewer roles, project-local skill memory, and a reusable goal prompt.

This skill is not the general development router. `adaptive-dev-workflow` decides whether initialization is warranted; this skill builds or repairs the project harness once that decision is made.

Human-facing generated docs default to Chinese when the user/team language is Chinese. Keep file paths, JSON/schema fields, commands, validator types, skill names, and error strings in English. Do not let fallback Superpowers/OpenSpec terminology make the whole generated document English.

## Route Boundary

Use this skill when any of these are true:

- New repo, new product area, or first serious MVP vertical slice.
- Large work is blocked by missing current-truth docs, spec, technical design, plan, evidence, or agent role contracts.
- The user says they keep repeating project decisions, verification expectations, or agent coordination rules.
- Existing spec has goals/non-goals but no delivery verification, claim ceiling, or stop/continue condition.
- Project subagents/reviewers are weak because role contracts are ad hoc or missing.
- `adaptive-dev-workflow` selects `Project Harness Init Gate`.

Do not use this skill for Tiny/Small edits, one-off docs cleanup, or ordinary feature work when the repo already has a working harness.

## First Decision

Before creating files, inspect the target repo and decide:

```text
Existing convention: what docs/spec/agent files already exist?
Harness gap: docs, spec, plan, evidence, AGENTS.md, agent team, project skill, or goal prompt?
Feature scope: optional feature id for the first spec/design/plan/evidence set
Project domain: project skill folder name
Spec system: OpenSpec when explicit OpenSpec markers exist, otherwise Superpowers fallback
Write policy: create only missing files unless the user explicitly approves overwrite
```

If an existing repo has a stronger convention, follow it. Do not force this layout unless the repo has no useful convention or the user asks to standardize.

## Creation Flow

Prefer `scripts/init_project_harness.py` for deterministic scaffold creation.

Use:

```bash
python3 <skill-dir>/scripts/init_project_harness.py --root <repo> --feature-id <feature-id> --project-skill <domain> --spec-system auto
```

Default generated layout:

```text
AGENTS.md
.gitignore
.agent/
  agents.md
  goal-loop-mode.md
  knowledge/candidates/
  evals/seed-cases.yaml
  runs/
  skills/<project-domain>/
    SKILL.md
    references/
      architecture.md
      testing.md
      delivery.md
      lessons.md
docs/
  architecture.md
  adr/
  superpowers/              # only when OpenSpec is not the product spec system
    specs/YYYY-MM-DD-<feature-id>-spec.md
    designs/YYYY-MM-DD-<feature-id>-technical-design.md
    plans/YYYY-MM-DD-<feature-id>.md
  evidence/<feature-id>.md
```

Use `--dry-run` first when the repo already has docs or agent files. Use `--force` only with explicit user approval.

`--spec-system auto` detects explicit OpenSpec markers (`openspec/`, `.openspec/`, `openspec.yaml`, or `open-spec.yaml`). In OpenSpec mode, this skill does not create product spec/design/plan files; it records that product specs and technical design are owned by OpenSpec change artifacts and keeps `docs/evidence/<feature-id>.md` as the evidence surface. Use `--spec-system superpowers` only when the repo does not use OpenSpec or the user asks for the lightweight fallback.

## Contracts

Read only the needed reference:

- `references/harness-contract.md`: spec-system selection, OpenSpec handoff, Superpowers fallback spec/design/plan, evidence structure, and acceptance fields.
- `references/goal-loop-mode.md`: reusable target-mode prompt and loop contract.
- `references/agent-team-roles.md`: project reviewer/subagent role contracts.

After creating or repairing files, run:

```bash
python3 <skill-dir>/scripts/validate_project_harness.py --root <repo> --feature-id <feature-id> --project-skill <domain> --spec-system auto
```

When recording validators inside generated project docs, use repo-relative commands or placeholders such as `<skill-dir>` and `<repo>`. Do not paste machine-specific paths.

## Output Contract

Report:

```text
Created/updated files
Existing files skipped
Chosen docs convention
Chosen spec system
Feature id and project skill name
Goal Loop prompt path
Agent team roles path
Validation command and result
Remaining gaps or decisions needed
```

Do not claim the project is production-ready. This skill creates the harness for future work; delivery readiness still depends on implementation evidence and `production-handoff` style verification.

For harness initialization alone, the completion claim ceiling is `Dev Done`.
Do not claim `Integration Done` unless the requested work also implemented a
real MVP/system chain and that chain passed integration, smoke, or E2E
verification outside the scaffold validator.

## Integration

Use this skill with the broader method:

```text
adaptive-dev-workflow = decide route and whether harness init is needed
project-harness-init = create project docs/agent/evidence/goal-loop scaffolding and choose spec-system routing
OpenSpec = own product change specs when available
Superpowers = provide optional stage-scoped debugging/planning/TDD/review methods and fallback spec/plan shapes when OpenSpec is absent
project-local skill = capture project-specific SOP and lessons
evidence/reviewer loop = keep completion claims honest
```

## NEVER

- NEVER initialize a full harness for Tiny/Small tasks.
- NEVER overwrite existing project docs, AGENTS.md, or project skill files without explicit approval.
- NEVER run `git init`, create package/deploy boilerplate, or add product code unless the user explicitly asks.
- NEVER create a second product spec/design/plan surface when OpenSpec is already the repo's spec system.
- NEVER create fallback specs without delivery verification, claim ceiling, and stop/continue condition.
- NEVER let project agent roles invent product requirements.
- NEVER promote raw lessons directly into global `AGENTS.md` or this general skill.
- NEVER store secrets, credentials, private logs, local-only paths, or tokens in generated agent memory.
