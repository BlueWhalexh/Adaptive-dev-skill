# Harness Contract

READ when creating or repairing project docs/spec/design/plan/evidence structure.

DO NOT READ for ordinary implementation tasks after the harness already exists.

## Purpose

The harness turns repeated human guidance into durable project surfaces:

- `AGENTS.md` for always-loaded project rules.
- `.gitignore` for local env files and agent run artifacts.
- `.agent/agents.md` for reusable reviewer/subagent role contracts.
- `.agent/goal-loop-mode.md` for the reusable target-mode prompt.
- `.agent/skills/<project-domain>/` for project-specific SOP and lessons.
- `docs/architecture.md` for current truth.
- OpenSpec change artifacts for product/behavior specs when the repo uses OpenSpec.
- `docs/superpowers/specs/YYYY-MM-DD-<feature-id>-spec.md`, `docs/superpowers/designs/YYYY-MM-DD-<feature-id>-technical-design.md`, and `docs/superpowers/plans/YYYY-MM-DD-<feature-id>.md` only as the lightweight fallback when OpenSpec is absent.
- `docs/evidence/<feature-id>.md` for validators, results, gaps, and claim ceiling.

## Language Contract

Generated human-facing docs must default to Chinese when the user/team language is Chinese. Keep these tokens in English:

- file paths and filenames
- JSON/schema keys
- commands and flags
- validator types such as `unit`, `integration`, `fresh_consumer`
- skill names such as `adaptive-dev-workflow` and `superpowers:writing-plans`
- error messages copied from tools

Do not translate machine contracts, but do not write the surrounding explanation in English by default.

## Spec System Decision

Use this order:

1. Existing repo convention wins.
2. If explicit OpenSpec markers exist (`openspec/`, `.openspec/`, `openspec.yaml`, or `open-spec.yaml`), product/behavior specs belong to OpenSpec.
3. Otherwise use the Superpowers-compatible fallback paths.

Harness initialization must not create two product spec/design systems. OpenSpec mode creates harness, project memory, agent roles, architecture docs, and evidence; it does not create product `proposal.md`, `design.md`, `specs/`, or `tasks.md`. Those belong to `openspec-workflow`.

## OpenSpec Contract

When `spec_system = openspec`, generated docs must point future agents to:

```text
OpenSpec changes/<change-id>/{proposal.md,design.md,specs/,tasks.md}
```

Product spec requirements:

- `proposal.md`: motivation, scope, non-goals, rollout/rollback constraints.
- `design.md`: technical decisions, alternatives, data/API/security/runtime impact.
- `specs/`: delta specs with acceptance scenarios.
- `tasks.md`: implementation task source for later Superpowers planning/execution.

The harness must still create `docs/evidence/<feature-id>.md` with `## Product Spec System`, validator types, claim ceiling, gaps, and stop/continue conditions. Evidence does not move into OpenSpec because completion claims need fresh validator results, not only approved requirements.

## Superpowers Fallback Spec Contract

`docs/superpowers/specs/YYYY-MM-DD-<feature-id>-spec.md` must include product contract fields:

```md
# <Feature> 产品规格

> 人读说明默认中文；命令、路径、schema 字段、validator type 保留英文。

## 意图
What outcome should become true?

## 范围
In-scope modules, users, APIs, workflows, docs, and operational surfaces.

## 非目标
Adjacent work explicitly out of scope.

## 当前事实
Code paths, docs, runtime facts, existing contracts, and known constraints.

## 行为
State, trigger, expected behavior, error behavior, empty/edge states.

## 交付验证
What evidence must exist before the goal can be called done?

## 验收标准
Observable checks tied to evidence.

## 技术设计入口

Link to `docs/superpowers/designs/YYYY-MM-DD-<feature-id>-technical-design.md`.

## 停止 / 继续条件
What can the agent keep iterating on, and what requires human decision?
```

Use `Dev Done` unless the spec explicitly requires integration or handoff evidence.
Harness creation alone must stay at `Dev Done`; integration or handoff claims
belong to implemented product behavior, a fresh consumer, or a real external
chain, not to scaffold validation.

## Superpowers Fallback Technical Design Contract

`docs/superpowers/designs/YYYY-MM-DD-<feature-id>-technical-design.md` must include technical design fields:

```md
# <Feature> 技术设计

## 输入与事实来源

## 设计目标

## 当前到目标架构 Delta

## 边界与职责

## 契约

## 控制流 / 数据流

## 错误 / 重试 / 恢复 / 并发 / 幂等

## 安全 / 隐私 / 权限

## 性能 / 可运维 / 可观测性

## 兼容性 / 迁移 / 回滚

## 验收到设计到证据

## 设计 Review

## 未决问题

## 停止 / 继续条件
What can the agent keep iterating on, and what requires human decision?
```

The technical design is the only fallback surface for architecture delta, contracts, data/control flow, security, migration, observability and rollback. Do not hide these decisions in the implementation plan.

## Superpowers Fallback Plan Contract

`docs/superpowers/plans/YYYY-MM-DD-<feature-id>.md` must follow the Superpowers `writing-plans` shape:

```md
# <Feature> 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ...

**Architecture:** ...

**Tech Stack:** ...

---

## 已批准 Spec
Link to `docs/superpowers/specs/YYYY-MM-DD-<feature-id>-spec.md`.

## 已批准 Technical Design
Link to `docs/superpowers/designs/YYYY-MM-DD-<feature-id>-technical-design.md`.

## 任务表
| Task | Scope | Gate | Evidence | Done |
| --- | --- | --- | --- | --- |

## Review 重点

## 风险 / 缺口
```

## Evidence Contract

`docs/evidence/<feature-id>.md` must include:

```md
# 证据

## 产品规格系统
openspec / superpowers

## Claim 上限
Dev Done / Integration Done / Handoff Done

## Validators
| Validator | Type | Result | Proves | Gaps |
| --- | --- | --- | --- | --- |

## Red / 复现证据

## Green / 最终证据

## Review 证据

## Deferred / 已接受缺口
```

Use portable validators in generated docs. Prefer repo-relative commands and placeholders:

```text
python3 <skill-dir>/scripts/validate_project_harness.py --root <repo> --feature-id <feature-id> --project-skill <domain> --spec-system auto
```

Do not write machine-specific paths such as `/Users/<name>/...`, `/private/tmp/...`, or `/tmp/...` into project docs, project skills, or agent memory.

## Current Truth Routing

When future agents need context:

| Need | Read |
| --- | --- |
| Repo-wide rules | `AGENTS.md` |
| Local env / run artifact guard | `.gitignore` |
| Reviewer roles | `.agent/agents.md` |
| Goal loop handoff | `.agent/goal-loop-mode.md` |
| Architecture facts | `docs/architecture.md` |
| Feature intent | OpenSpec `changes/<change-id>/{proposal.md,specs/}` when OpenSpec applies; otherwise `docs/superpowers/specs/YYYY-MM-DD-<feature-id>-spec.md` |
| Technical design | OpenSpec `changes/<change-id>/design.md` when OpenSpec applies; otherwise `docs/superpowers/designs/YYYY-MM-DD-<feature-id>-technical-design.md` |
| Execution plan | OpenSpec `changes/<change-id>/tasks.md` plus Superpowers planning when OpenSpec applies; otherwise `docs/superpowers/plans/YYYY-MM-DD-<feature-id>.md` |
| Verification result | `docs/evidence/<feature-id>.md` |
| Project SOP | `.agent/skills/<project-domain>/SKILL.md` |

If docs and code disagree, treat code and fresh verification as current truth, then record docs drift.

## Exit Gate

Before saying initialization is complete:

```text
Required files created or intentionally skipped
Existing project convention respected
`.gitignore` protects local env files and `.agent/runs`
Spec system chosen and recorded
OpenSpec mode does not create fallback product specs/plans
Fallback spec has delivery verification
Fallback spec states acceptance and claim ceiling
Fallback plan uses Superpowers implementation-plan shape and has per-task evidence
Evidence file distinguishes validator types
Agent roles are read-only by default
Project skill exists and does not duplicate generic TDD/debug/planning
No secrets or local-only paths were written
Validation script passed or gaps are stated
```
