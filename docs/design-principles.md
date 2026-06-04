# Design Principles

## 1. Process Is A Risk Control

The workflow level should be chosen from ambiguity, blast radius, behavior risk, and verification cost. Process is useful only when it reduces real risk.

## 2. Scope Must Be Explicit

Before coding, the agent should know what outcome is expected, what files or behaviors are in scope, what is out of scope, and what should trigger a pause.

## 3. Verification Comes Before Completion Claims

The final answer should name the command or check that was run and what happened. A confident statement without fresh evidence is not an engineering result.

## 4. Human Gates Belong At Decision Points

The agent should not ask for permission after every edit. It should pause when a decision changes the goal, public API, data model, security posture, user-facing behavior, dependency graph, or scope.

## 5. Compose Specialized Workflows

Adaptive Dev Workflow coordinates other workflows instead of duplicating them. Planning, TDD, debugging, OpenSpec, and review workflows are useful when the task calls for them.

## 6. Follow The Repository

Read the project structure first. Use existing patterns, helpers, tests, and conventions. Avoid unrelated refactors.
