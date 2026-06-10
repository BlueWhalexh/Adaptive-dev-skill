---
name: adaptive-dev-workflow
description: Use when a user asks to implement, fix, refactor, design, plan, verify, or review software work and scope, risk, tests, docs, or evidence need right-sizing.
---

# Adaptive Dev Workflow

## Overview

Use this as the coordinator for turning a software request into scoped, implemented, reviewed, and verified work. Pick the smallest workflow that protects correctness; add process only when risk, ambiguity, blast radius, or handoff cost justifies it.

Core principle: production AI coding is harness engineering: current truth, bounded action space, executable evidence, and review loops.

This skill coordinates other skills when available. Do not duplicate their full instructions.

## Dependency Check

Before development work, check which supporting skills are available and invoke
only the gates justified by the task:

- `define-goal`: fuzzy intent or unclear success criteria.
- `brainstorming` / `superpowers:brainstorming`: requirement discovery, design, UX, or meaningful tradeoffs.
- `writing-plans` / `superpowers:writing-plans`: medium/large staged implementation.
- `test-driven-development` / `superpowers:test-driven-development`: meaningful behavior risk, automatable regression, core logic/API/permissions/data/state-machine changes.
- `systematic-debugging`: failures, regressions, or unexplained behavior.
- `verification-before-completion`: before any completion claim.
- `requesting-code-review`: high-risk or broad changes.
- `using-git-worktrees`: dirty worktree or isolation need.
- `frontend-design`: substantial UI creation or redesign.
- `openai-docs`: current OpenAI API or Codex product facts.
- `openspec-workflow`: repo already uses OpenSpec and required dependencies are available.

For Tiny or mechanical changes, do not force TDD. Define the smallest validator that proves the claim. If a preferred skill is unavailable, keep the same gate in plain workflow form and state the fallback briefly.

## First Move

Do not start coding from a vague request. Classify the task and decide whether a question is required.

Ask one concise question only when the missing detail changes outcome, validation, risk, public API, data model, security posture, or user-visible behavior. Otherwise propose a concrete objective and continue or ask for confirmation when the selected process level requires a gate.

Minimum objective:

```text
Outcome: what will be true when done
Scope: files/modules/features in and out
Current truth: docs/specs/code paths that define the existing system
Evidence: command, test, UI check, screenshot, diff review, or acceptance condition proving completion
Stop condition: when to pause for user judgment
```

For Tiny tasks, current truth can be as small as the touched file, existing
command, or current README/config snippet.

## Process Selection

Choose exactly one process level. Explain the choice in one or two sentences when the task is non-trivial.

| Level | Use When | Flow |
| --- | --- | --- |
| Tiny | Text/docs/config change, typo, single obvious fix with no runtime blast radius | objective -> edit -> focused verification |
| Small | Single-file or narrow bugfix with clear behavior | objective -> inspect existing pattern -> failing evidence or focused validator -> implement -> verify -> self-review |
| Debug | CI/test failure, regression, production-like failure, or unexplained behavior | objective -> collect logs/current truth -> reproduce -> isolate root cause -> minimal fix -> regression/focused validator -> verify |
| Medium | 1-3 modules, new behavior/API, meaningful edge cases | objective -> discovery -> design approval -> short plan -> TDD or explicit validator -> task gates -> phase smoke/E2E -> review |
| Large | Cross-module feature, migration, data model change, security risk, user-facing workflow | discovery -> current-truth docs -> design/spec -> staged plan -> incremental implementation -> independent review -> system verification |
| OpenSpec | Repo already has OpenSpec and required workflow skills are available | delegate lifecycle to `openspec-workflow` |

Avoid accidental heavyweight process: a simple fix should not require a full spec. Avoid accidental lightweight process: a risky change should not ship with only a happy-path check.

## Escalation Triggers

Upgrade the process level when any of these appear:

- Unclear acceptance criteria that changes outcome or risk.
- Public API, auth, permissions, security, secrets, payments, PII, or data model changes.
- Runtime, deploy, environment, availability, performance, or configuration blast-radius risk.
- Cross-service workflow, migration, recovery path, concurrency, or state-machine behavior.
- Multiple modules, unknown architecture boundary, or likely docs drift.
- Verification gap that would make a completion claim misleading.

## Review-Only Mode

When the user asks to review code, a PR, a plan, docs, evidence, or this skill itself, do not edit unless explicitly asked.

Flow: current truth -> classify risk -> inspect artifact -> report findings by severity -> suggest the smallest safe changes -> state what was not validated.

Review findings should distinguish correctness, scope, evidence gaps, security, maintainability, docs drift, and completion-claim risk.

## Human Decision Gates

Pause for user confirmation before:

- Changing the goal, scope, public API, data model, security posture, or user-facing behavior.
- Installing dependencies, using network access, writing outside the workspace, starting long-running services, or running destructive commands.
- Choosing between architecture approaches with real tradeoffs.
- Proceeding from design/spec into implementation for medium or large work.
- Accepting a known verification gap as shippable.

Do not pause for every mechanical step once the objective and approved plan are clear. Continue through implementation, verification, and review.

## Documentation Gate

Decide whether documentation is needed before implementation. Documentation should reduce future action space, not decorate the work.

- `AGENTS.md` / `CLAUDE.md`: durable repo rules, commands, gotchas, review expectations.
- `docs/canonical/`: current truth for architecture, contracts, state machines, ownership, invariants.
- `docs/specs/design/`: approved design and tradeoffs for Medium/Large work.
- `docs/specs/plans/`: staged implementation tasks and evidence per task.
- `docs/specs/changes/`: dated requirement deltas after approval.
- `docs/reference/`: historical or external background; never current truth.
- Tests: executable behavior docs for behavior changes or regressions.
- Final/PR summary: delivery handoff; compress for Tiny.

Use these paths when the repo follows this convention; otherwise follow the existing repo documentation structure. Prefer current code and canonical docs over dated/reference docs when they conflict. If docs are out of scope, state why.

## Test And Verification Strategy

Define the evidence before implementation. Good tests constrain behavior and make future agents understand the system, not just increase pass counts. For detailed examples and the skill validation protocol, read `references/evidence-and-validation.md` when route/evidence choice is ambiguous, when planning Medium/Large work, or when changing this skill.

### Evidence Ladder

Use the smallest evidence set that can catch the likely failure:

- Tiny/mechanical: diff review plus command/link check only if semantics matter.
- Small bug/behavior: reproduction evidence or focused validator; automate regression when feasible.
- Medium feature/API/UI: focused tests plus phase smoke/E2E when a chain matters.
- Large/high-risk: staged tests, independent review, system verification, and docs handoff.

### TDD And Alternate Validators

- Use TDD by default when the project has a suitable test harness and the changed behavior can be captured at reasonable cost, especially for automatable bugs, core logic, API contracts, permissions, data, and state-machine behavior.
- Prefer TDD for Small behavior changes and important refactors in tested modules.
- Use an alternate validator for Tiny/mechanical changes, visual-only checks, unavailable test environments, or cases where automation would be more expensive than the risk.
- Never use "no TDD" as "no evidence"; always state what the validator proves and what remains unproven.

### Cadence

- Every task: run focused tests or the explicit validator for the changed behavior.
- Every task exit: run relevant build/lint/type checks when the stack supports them, inspect touched files, and do a consistency check.
- Every medium feature phase: run a smoke or E2E check that exercises the user-visible or system-visible chain.
- Before final completion: run the highest-signal relevant suite available within time and environment constraints.
- If a check is too expensive or unavailable, state the substitute evidence and the remaining risk.

Good tests cover behavior from acceptance criteria, not private implementation details. Prefer real code and realistic fixtures; mock only external boundaries or slow/non-deterministic dependencies. Name tests so they encode state, trigger, expected behavior, and what failure would block.

## Task Exit Gate

For each implementation task, check:

```text
Scope: diff only touches expected files and modules
Spec consistency: behavior still matches approved objective/spec/current truth
Docs consistency: affected docs are updated or explicitly not needed
Tests: focused validator run and result recorded
Build/static checks: relevant checks run or gap explained
Review: correctness, boundaries, security, and maintainability inspected
```

Medium and large work should also include an independent review pass when available, preferably via a fresh subagent or separate thread. The review should focus on correctness, regressions, security, missing tests, docs drift, and scope creep, not style preferences.

## Context And Delegation

Use read-only subagents or separate threads when a side task would flood the main context: large codebase exploration, independent review, broad test-gap analysis, or security audit. Do not delegate implementation or parallel code changes unless the user/tooling explicitly allows it and the scope is isolated. When delegating, pass minimum complete context: goal, scope, current truth sources, constraints, expected output, and what not to change.

Do not use subagents for tiny tasks where coordination overhead exceeds value. Do not let subagents invent missing product requirements.

## Automation Gate

If a rule must happen every time and can be checked deterministically, prefer a hook, CI check, script, or lint rule over more prompt text. Skills and instruction files guide judgment; hooks and CI enforce mechanics.

Examples:

- Repeated format/lint/test commands -> hook or CI.
- Secret or PII blocking -> pre-tool/pre-commit/CI check.
- Stable PR review checklist -> review instruction file referenced from `AGENTS.md`.
- Repeated multi-step judgment workflow -> skill.

## Completion Contract

Never claim completion without evidence. Final responses should include the fields that apply: changed files, verification evidence and what it proves, user-visible outcome, agent-readable/system outcome, backend capability outcome if relevant, integration-chain changes, remaining gaps, and review points.

For Tiny tasks, compress to `Changed`, `Verified`, and `Gap` while keeping evidence and residual risk explicit.

## Skill Validation

After changing this skill, validate it with pressure scenarios instead of intuition:

- Run static checks: frontmatter, `openai.yaml`, duplicate skill versions, key sections.
- Dry-run Tiny/Small/Medium/Large/debug prompts and compare route, evidence, and gates.
- For major changes, ask a fresh subagent to route cases using only this `SKILL.md`.
- If the same misroute appears twice, update the smallest rule that prevents it.

Do not add project-specific lessons here; put them in the repo's `AGENTS.md` or docs.

## Common Mistakes

- Too heavy: full spec/TDD/E2E for a tiny diff.
- Too light: happy-path check for risky behavior, API, data, auth, or cross-service changes.
- Too vague: many questions at once, docs as narrative, or pass/fail counts without what they prove.
- Too trusting: self-review only for broad work, sub-skill owns lifecycle, or completion without fresh evidence.
