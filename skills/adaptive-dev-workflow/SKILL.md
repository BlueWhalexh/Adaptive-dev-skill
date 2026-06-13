---
name: adaptive-dev-workflow
description: Use when software implementation, fixes, refactors, design, planning, verification, code review, PR review, plan/evidence review, workflow routing, gate selection, skill orchestration, right-sized evidence, or complex project harness decisions are needed.
---

# Adaptive Dev Workflow

## Overview

Use this as the router for turning a software request into scoped, implemented, reviewed, and verified work. Pick the smallest workflow that protects correctness; add gates only when risk, ambiguity, blast radius, or handoff cost justifies them.

Core principle: production AI coding is harness engineering: current truth, bounded action space, executable evidence, and review loops.

This skill coordinates other skills when available. It selects gates and preserves scope; it must not dilute or reimplement the internal discipline of stronger execution skills.

## Dependency Check

Before development work, check which supporting skills are available and invoke
only the gates justified by the task:

- `define-goal`: fuzzy intent or unclear success criteria.
- `brainstorming` / `superpowers:brainstorming`: requirement discovery, design, UX, or meaningful tradeoffs.
- `writing-plans` / `superpowers:writing-plans`: medium/large staged implementation.
- `test-driven-development` / `superpowers:test-driven-development`: meaningful behavior risk, automatable regression, core logic/API/permissions/data/state-machine changes.
- `systematic-debugging` / `superpowers:systematic-debugging`: failures, regressions, or unexplained behavior.
- `verification-before-completion` / `superpowers:verification-before-completion`: before non-trivial completion claims.
- `subagent-driven-development` / `superpowers:subagent-driven-development`: executing a written plan with independent tasks and subagent support; use its per-task spec compliance and code quality review loops.
- `requesting-code-review` / `superpowers:requesting-code-review`: high-risk or broad changes.
- `using-git-worktrees` / `superpowers:using-git-worktrees`: dirty worktree or isolation need.
- `frontend-design`: substantial UI creation or redesign.
- `openai-docs`: current OpenAI API or Codex product facts.
- `openspec-workflow`: repo already uses OpenSpec and required dependencies are available.

For Tiny or mechanical changes, do not force TDD. Define the smallest validator that proves the claim. If a low-risk supporting skill is unavailable, keep the same gate intent in plain workflow form and state the fallback briefly. For high-risk gates such as TDD, debugging, OpenSpec, security review, or completion verification, state the missing capability and pause or ask for approval before using a weaker substitute.

## Hard Gate Inheritance

This skill decides whether a gate is justified; it does not lower that gate's standard. Once routed to a supporting skill, follow that skill's stronger rules.

- Debug route or unexplained failure -> use `systematic-debugging` / `superpowers:systematic-debugging`; do not propose or apply fixes before root-cause investigation.
- TDD route -> use `test-driven-development` / `superpowers:test-driven-development`; no production behavior change before valid Red evidence when the behavior is automatable.
- Plan/spec gate -> use `writing-plans` / `superpowers:writing-plans` or `openspec-workflow` when available; do not replace their plan/spec method with an ad hoc summary.
- Plan execution gate -> when a written plan has independent tasks and subagents are available, use `subagent-driven-development` / `superpowers:subagent-driven-development`; use `executing-plans` / `superpowers:executing-plans` only when subagents are unavailable or the user chooses inline execution.
- Completion gate -> use `verification-before-completion` / `superpowers:verification-before-completion` for non-trivial work; do not claim success without fresh verification evidence.
- Review gate -> use `requesting-code-review` / `superpowers:requesting-code-review` or an isolated review pass for high-risk/broad work; do not self-approve broad changes as complete.

Tiny tasks still need fresh evidence, but their completion gate can be satisfied by the explicit focused validator when no non-trivial behavior changed.

If you skip a stronger gate for behavior-risk work, state why it is impractical, which alternate validator will be used, what it proves, and what remains unproven.

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
| Tiny | Text/docs/non-runtime config change, typo, single obvious fix with no runtime blast radius | objective -> edit -> focused verification |
| Small | Single-file, narrow reproducible bugfix, or runtime-default config change with clear behavior | objective -> inspect existing pattern -> select gates -> delegate TDD/debug if triggered -> implement -> verify -> self-review |
| Debug | CI/test failure, production-like regression, unreproducible failure, or unexplained behavior with unknown blast radius | objective -> route to systematic-debugging -> reproduce/root cause -> minimal fix -> regression/focused validator -> verify |
| Medium | 1-3 modules, new behavior/API, meaningful edge cases | objective -> discovery -> route to brainstorming/plan/TDD as triggered -> execute plan with review gate when needed -> phase smoke/E2E |
| Large | Cross-module feature, migration, data model change, security risk, or critical/cross-service user-facing workflow with data/security/state/rollback risk | discovery -> route to spec/plan workflow -> execute plan with subagent review when available -> system verification |
| OpenSpec | Repo already has OpenSpec and required workflow skills are available | delegate lifecycle to `openspec-workflow` |

Avoid accidental heavyweight process: a simple fix should not require a full spec. Avoid accidental lightweight process: a risky change should not ship with only a happy-path check.

Small vs Debug: use Small when the symptom is narrow, reproducible, and has an obvious local owner; use Debug when logs/CI/production behavior must be investigated or root cause is unknown. Ordinary 1-3 module UI/API features stay Medium unless an escalation trigger makes the workflow critical, cross-service, data-sensitive, or rollback-sensitive.

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

When reviewing test or evidence adequacy, read `references/evidence-and-validation.md`; do not load `complex-project-harness.md` unless the PR is Large/new-project work or changes the docs/spec harness.

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

For Large work, new projects, multi-agent handoff, or repos without reliable current-truth docs, read `references/complex-project-harness.md` before planning. Do not load it for Tiny/Small tasks unless the task is specifically to create or repair the repo's docs/spec harness.

Use the repo's existing docs structure when it exists. Prefer current code and canonical docs over dated/reference docs when they conflict. If docs are out of scope, state why.

## Test And Verification Strategy

Define the evidence before implementation. Good evidence constrains behavior and makes future agents understand the system, not just increase pass counts. For detailed examples and the skill validation protocol, read `references/evidence-and-validation.md` when route/evidence choice is ambiguous, when reviewing evidence adequacy, when planning Medium/Large work, or when changing this skill. Do not load it for obvious Tiny/Small tasks where the validator is clear.

### Evidence Ladder

Use the smallest evidence set that can catch the likely failure:

- Tiny/mechanical: diff review plus command/link check only if semantics matter.
- Small bug/behavior: reproduction evidence or focused validator; automate regression when feasible.
- Medium feature/API/UI: focused tests plus phase smoke/E2E when a chain matters.
- Large/high-risk: staged tests, independent review, system verification, and docs handoff.

### Red Evidence And Alternate Validators

- Every task must define evidence before implementation, but not every task needs Red.
- Route to TDD when changed behavior can be captured at reasonable cost, especially automatable bugs, core logic, API contracts, permissions, data, and state-machine behavior.
- A valid Red must fail on the current code for the expected reason. If the selected TDD skill is available, follow it instead of this summary.
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

Medium and large work should also include an independent review pass when available. For written plans with independent tasks, prefer `subagent-driven-development` so each task gets spec compliance review before code quality review. For ad-hoc high-risk work, use `requesting-code-review` or a focused isolated reviewer. The review should focus on correctness, regressions, security, missing tests, docs drift, and scope creep, not style preferences.

## Context And Delegation

Use read-only subagents or separate threads when a side task would flood the main context: large codebase exploration, independent review, broad test-gap analysis, or security audit. Do not delegate implementation or parallel code changes unless the user/tooling explicitly allows it and the scope is isolated. When a selected skill provides reviewer templates, use that skill's template instead of inventing an ad hoc reviewer prompt. When delegating, pass minimum complete context: goal, scope, current truth sources, constraints, expected output, and what not to change.

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

After changing this skill or any workflow router / skill orchestration rule, validate it with pressure scenarios instead of intuition:

- Run static checks: frontmatter, `openai.yaml`, duplicate skill versions, key sections.
- Dry-run Tiny/Small/Medium/Large/debug prompts and compare route, evidence, and gates.
- For major changes, ask a fresh subagent to route cases using only this `SKILL.md`.
- If the same misroute appears twice, update the smallest rule that prevents it.

Do not add project-specific lessons here; put them in the repo's `AGENTS.md` or docs.

## NEVER

- NEVER replace a selected TDD/debug/OpenSpec/verification skill with a softer local summary; this skill routes gates, it does not weaken them.
- NEVER let implementer self-review replace a selected isolated review gate for plan-backed, Medium, Large, or high-risk work.
- NEVER treat a Tiny/Small task as a full docs/spec harness unless the docs harness is the task.
- NEVER ship risky API, data, auth, permission, runtime, or cross-service changes with only happy-path evidence.
- NEVER treat dated specs, chat history, or reference docs as current truth when code or canonical docs disagree.
- NEVER accept mock-only evidence as proof of an integration chain unless the mocked boundary and remaining risk are stated.
- NEVER claim completion without fresh evidence, and never hide verification gaps behind "should pass" language.
- NEVER let Large/new-project work start without current-truth docs/spec surface or an explicit user-approved exception.
