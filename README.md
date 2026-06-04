# Adaptive Dev Workflow

**Use the lightest process that still protects correctness.**

Adaptive Dev Workflow is a small system for agentic coding tools such as Codex, Claude Code, and Gemini CLI. It helps an AI coding agent decide when to move fast, when to stop and clarify, when to plan, when to test, and when to verify before it claims the work is done.

It is not a magic prompt. It is a workflow router for software work.

Fast when the task is obvious. Careful when the risk is real.

## The Problem

Agent coding often fails in predictable ways:

- The agent starts coding before it understands the request.
- A tiny fix turns into a broad refactor.
- The agent changes behavior that was never in scope.
- Tests are skipped because the change "looks obvious".
- The final answer says the work is complete without fresh evidence.
- The repo ends up harder to review than the original problem.

This is not only a model-quality problem. It is a process problem.

Human engineers do not use the same process for every task. A typo fix does not need a design doc. A permissions migration should not be handled like a typo fix. Agentic coding needs the same judgment, but agents tend to default either to pure vibe coding or to rigid ceremony.

Adaptive Dev Workflow gives the agent a decision model for choosing the smallest useful engineering process.

## What This Is

Adaptive Dev Workflow is a reusable skill that coordinates development work through risk-based gates:

- clarify the objective when the request is vague
- classify the task as Tiny, Small, Medium, Large, or OpenSpec
- use planning only when the risk justifies it
- use TDD or explicit validation for behavior changes
- add debugging discipline when behavior is unexplained
- require fresh verification before completion claims
- keep scope changes behind human decision gates

The goal is not more process. The goal is less chaos.

## Why Not Just Vibe Code?

Vibe coding is useful for exploration, prototypes, and low-risk throwaway work. It becomes expensive when the output lands in a real repository.

The failure mode is not that the agent writes code. The failure mode is that the agent writes code while silently making product, architecture, risk, and verification decisions that should have been explicit.

Adaptive Dev Workflow asks the agent to stop at the points where silent decisions usually damage quality:

- What exactly is the desired outcome?
- What is in scope and out of scope?
- What evidence proves the work?
- Is this a one-line edit or a cross-module change?
- Does the task need a plan, a test, a debugger, or a review gate?

This keeps the speed of agentic coding while adding the engineering guardrails that matter.

## How The Adaptive System Works

The skill acts as a coordinator. It does not replace specialized workflows; it routes to them when they are needed.

```text
User request
  -> define the objective
  -> classify risk and scope
  -> choose the workflow level
  -> add only the gates needed for that level
  -> implement within scope
  -> verify with fresh evidence
  -> report changes, checks, and review points
```

The important part is the decision step. The agent is instructed to choose process based on blast radius, ambiguity, behavior risk, and verification needs.

## Workflow Levels

| Level | Use when | Typical flow |
| --- | --- | --- |
| Tiny | Text, docs, config, typo, or one obvious edit | confirm target -> edit -> verify |
| Small | Narrow fix with clear expected behavior | objective -> focused implementation -> focused check |
| Medium | 1-3 modules, new behavior, meaningful edge cases | objective -> design/plan -> test or validator -> verify |
| Large | Cross-module feature, migration, security, data model, user-facing workflow | discovery -> design/spec -> staged plan -> implementation -> review -> verification |
| OpenSpec | Repo already uses OpenSpec | delegate the lifecycle to the repo's OpenSpec workflow |

The system is intentionally adaptive. It should not force a design doc for a README typo, and it should not let an agent rewrite an auth flow without a plan.

## Install

Recommended repository name:

```text
adaptive-dev-workflow
```

This repo currently ships the skill source under:

```text
skills/adaptive-dev-workflow/
```

### Codex

Copy or symlink the skill into your Codex skills directory:

```sh
mkdir -p ~/.codex/skills
cp -R skills/adaptive-dev-workflow ~/.codex/skills/adaptive-dev-workflow
```

Then ask Codex to use it:

```text
Use $adaptive-dev-workflow to implement this change with the smallest process that protects correctness.
```

### Claude Code or Other Agent CLIs

If your agent supports local skills, copy the same folder into that tool's skill location. If it does not, paste the contents of `skills/adaptive-dev-workflow/SKILL.md` into your project instructions or agent memory as a workflow policy.

### Project-Level Use

For teams, the most practical setup is to reference the workflow from your project-level agent instructions:

```text
For implementation, fix, refactor, design, or planning tasks, use adaptive-dev-workflow.
Choose Tiny/Small/Medium/Large based on ambiguity, blast radius, and verification risk.
Do not claim completion without fresh verification evidence.
```

## Usage

Use it when you want the agent to do software work without either over-planning or freewheeling.

Example:

```text
Use $adaptive-dev-workflow.
Add pagination to the repository list page. Keep the existing API shape unless a change is necessary.
Verify with the relevant frontend tests and a browser check.
```

For a tiny docs edit:

```text
Use $adaptive-dev-workflow.
Fix the install command in README.md and verify the markdown still has no broken local links.
```

For a risky backend change:

```text
Use $adaptive-dev-workflow.
Refactor token refresh handling. Preserve current session semantics, add regression coverage, and stop if the API contract needs to change.
```

## Example Scenarios

| Request | Expected behavior |
| --- | --- |
| "Fix this typo in CONTRIBUTING.md" | Tiny flow, no heavy plan |
| "Add one validation rule to a form" | Small flow, targeted check |
| "Add filters to an order page" | Medium flow, clarify fields and verification |
| "Rework permissions for admin users" | Large flow, design/spec and explicit review gates |
| "Investigate why tests are flaky" | Add systematic debugging before fixes |

## Case Study: Scope Control On A Small Feature

This is an illustrative before/after based on a common agent-coding failure mode. It is not a benchmark claim.

### Before: Pure Vibe Coding

Request:

```text
Add a status filter to the issues page.
```

Likely agent behavior:

- adds the filter UI
- changes query parameters
- rewrites part of the table state
- updates unrelated styling
- does not ask which statuses exist
- does not verify empty-state behavior
- reports completion based on code changes

Review result:

- behavior may work for the happy path
- scope is larger than requested
- reviewers must inspect unrelated changes
- missing edge cases are discovered later

### After: Adaptive Dev Workflow

The agent first frames the work:

```text
Outcome: issues page can filter by existing issue status.
Scope: status filter UI, query state, and data request only; no table redesign.
Evidence: targeted frontend test or browser check covering active filter and empty state.
Stop condition: pause if the backend API does not already support status filtering.
```

Then it chooses a Small or Medium workflow depending on the existing code. If the API already supports the parameter, the task stays narrow. If not, the agent stops before expanding scope into backend work.

Review result:

- fewer surprise edits
- clearer acceptance criteria
- verification is tied to behavior
- the agent has an explicit reason to pause when scope changes

## Why This Works

Adaptive Dev Workflow works because it treats process as a risk control, not a ritual.

Design principles:

- **Right-sized process:** use the smallest workflow that protects correctness.
- **Explicit scope:** make hidden assumptions visible before coding.
- **Human decision gates:** pause when the agent would otherwise change goals, APIs, security posture, or user-facing behavior.
- **Fresh evidence:** do not claim completion without running the check that proves it.
- **Composable discipline:** delegate to planning, TDD, debugging, OpenSpec, or review workflows only when those workflows are useful.
- **Repo empathy:** read the project first and follow existing conventions.

The system is deliberately conservative at the edges where agents are most likely to damage a codebase.

## What It Is Not

Adaptive Dev Workflow is not:

- a guarantee that generated code is correct
- a replacement for human review
- a benchmarked productivity claim
- a heavyweight spec process for every task
- a prompt that makes vague requirements safe
- a substitute for tests, CI, or observability

It is best for real codebases where reviewability, scope control, and verification matter.

It is less useful for throwaway prototypes, experiments where correctness is not important, or teams that already have a mature agent workflow with equivalent gates.

## Repository Structure

```text
.
├── skills/adaptive-dev-workflow/   # installable skill source
├── docs/                           # manifesto, principles, case study
├── examples/                       # copyable prompts and scenarios
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Contributing

Contributions should preserve the core idea: adaptive discipline over fixed ceremony.

Useful contributions include:

- clearer installation paths for specific agent tools
- real-world case studies without inflated claims
- sharper decision rules for workflow levels
- examples that show when the skill should stop and ask
- compatibility notes for Codex, Claude Code, Gemini CLI, and similar tools

Please avoid turning the project into a universal AI coding manifesto or a giant checklist. The value is in choosing the smallest process that still protects correctness.
