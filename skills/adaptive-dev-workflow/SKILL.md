---
name: adaptive-dev-workflow
description: Use when a user asks to implement, fix, refactor, design, or plan software work and wants Codex to confirm requirements first, choose a right-sized process, then proceed toward verified development with human decision gates.
---

# Adaptive Dev Workflow

## Overview

Use this as the coordinator for turning a fuzzy software request into confirmed, implemented, and verified work. Choose the smallest process that protects correctness; add or replace steps only when the project risk justifies it.

This skill coordinates other skills when available. Do not duplicate their full instructions.

## Dependency Check

Before starting development work, check which supporting skills are available in the current session:

- Prefer `define-goal` for turning fuzzy intent into measurable success criteria.
- Prefer `brainstorming` or `superpowers:brainstorming` for requirement discovery and design approval.
- Prefer `writing-plans` or `superpowers:writing-plans` for medium and large implementation plans.
- Prefer `test-driven-development` or `superpowers:test-driven-development` for behavior changes, bug fixes, and refactors.
- Prefer `systematic-debugging` for failures, regressions, or unexplained behavior.
- Prefer `verification-before-completion` for final evidence before claiming completion.
- Prefer `requesting-code-review` for high-risk or broad changes.
- Prefer `openspec-workflow` only when the repository uses OpenSpec and its required `opsx:*` dependencies are available.

If a preferred skill is unavailable, keep the same gate in plain workflow form and state the fallback briefly.

## First Move

Do not start coding from a vague request. First classify the request and decide whether a question is required.

Ask one concise question only when a missing detail changes the outcome, validation, or risk. Otherwise, propose a concrete objective and ask for confirmation.

Minimum objective format:

```text
Outcome: what will be true when done
Scope: files/modules/features in and out
Evidence: command, test, UI check, or acceptance condition proving completion
Stop condition: when to pause for user judgment
```

## Process Selection

Choose one process level. Explain the choice in one or two sentences when the task is non-trivial.

| Level | Use When | Flow |
| --- | --- | --- |
| Tiny | Text/docs/config change, typo, single obvious fix | confirm target -> edit -> verify |
| Small | Single-file or narrow bugfix with clear behavior | objective -> minimal question if needed -> implement with focused test/check -> verify |
| Medium | 1-3 modules, new API/feature behavior, meaningful edge cases | objective -> brainstorming/design approval -> short plan -> TDD or smallest verifiable implementation -> verify |
| Large | Cross-module feature, migration, data model change, security risk, user-facing workflow | objective -> discovery -> design/spec -> detailed plan -> staged implementation -> review -> verification |
| OpenSpec | Repo already has OpenSpec and `opsx:*` skills are available | delegate lifecycle to `openspec-workflow` |

## Human Decision Gates

Pause for user confirmation before:

- Changing the goal, scope, public API, data model, security posture, or user-facing behavior.
- Installing dependencies, using network access, writing outside the workspace, starting long-running services, or running destructive commands.
- Choosing between architecture approaches with real tradeoffs.
- Proceeding from design/spec into implementation for medium or large work.

Do not pause for every mechanical step once the objective and plan are approved. Continue through implementation and verification.

## Dynamic Additions and Replacements

Add or replace workflow steps based on project needs:

- Add `systematic-debugging` when behavior is failing or unexplained.
- Add `using-git-worktrees` when the current repo is dirty or the change needs isolation.
- Add `dispatching-parallel-agents` or subagents only when the user explicitly allows delegation or parallel agents.
- Add `frontend-design` for substantial UI creation or redesign.
- Add `openai-docs` when current OpenAI API/product facts matter.
- Add `security-threat-model` or security review skills when auth, permissions, secrets, payments, or sensitive data are involved.
- Replace the local design/spec step with `openspec-workflow` when OpenSpec is active and dependencies are installed.

## Execution Rules

- Read the project structure and relevant code before proposing implementation.
- Prefer existing project conventions and helpers.
- Keep changes scoped to the approved objective.
- Use TDD when feasible for behavior changes: failing evidence first, implementation second, passing evidence last.
- When TDD is impractical, define an explicit alternate validator before implementation.
- Record verification commands and outcomes before claiming completion.
- In final responses, include changed files, verification evidence, and review points for correctness, boundaries, and safety.

## Scale Examples

- Tiny: "改一下 README 里的命令" -> confirm target if ambiguous, edit, show diff/verification.
- Small: "修复登录按钮点击没反应" -> reproduce or inspect, add focused test/check if possible, fix, verify.
- Medium: "给订单页增加筛选" -> confirm fields and UX, propose approach, plan, implement, run UI/API checks.
- Large: "重做权限系统" -> discovery, spec, staged plan, tests, review, migration/rollback discussion.

## Common Mistakes

- Treating every request as a full formal spec. Use the smallest sufficient process.
- Treating every request as a quick patch. Risk should determine gates.
- Asking many questions at once. Ask the next decision-changing question only.
- Letting a sub-skill decide the entire lifecycle. Return to this skill after each major gate.
- Claiming completion without evidence. No evidence means not done.
