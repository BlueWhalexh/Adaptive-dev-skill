---
name: adaptive-dev-workflow
description: Use when software implementation, fixes, refactors, design, planning, verification, code review, PR review, plan/evidence review, workflow routing, gate selection, skill orchestration, right-sized evidence, test/evidence matrix selection, project harness init, project skill learning, AGENTS.md/docs/agent-team decisions, quality-feedback recovery, or complex delivery handoff decisions are needed. 当用户要开发、修复、重构、规划、验证、项目初始化、测试矩阵、交付验收、项目 skill 沉淀、AGENTS.md/docs/agent team 管理、质量反馈恢复或 AI coding workflow routing 时使用。
---

# Adaptive Dev Workflow

## Overview

把这个 skill 当成软件开发任务的 control plane：把用户请求路由成范围清晰、实现可控、review 可执行、验证有证据的工作流。默认选择能保护正确性的最小流程；只有风险、模糊度、影响面或交付成本要求时才增加 gate。

核心原则：生产级 AI coding 是 harness engineering。关键不是堆流程，而是拿到 current truth，限制 action space，定义 executable evidence，并在合适位置加入 review loop。

本 skill 只负责协调和路由。它会选择 gate、保护 scope、决定是否调用 supporting skills；它不能稀释或重写更强执行 skill 的内部纪律。

Control-plane split:

```text
SDD/specs = development contract; Superpowers = execution discipline; Project skills = project SOP; Evidence/eval = reality check; Knowledge promotion = durable learning.
```

## Language And Trigger Convention

正文以中文为主，保留稳定英文锚点：skill `name`、gate names、workflow names、scripts、YAML/schema fields、evidence labels、route names。不要全文中英双语；使用中文解释 + 英文结构词 + 双语 `description` + 中英 eval prompts。

## Dependency Check

开发任务开始前，检查有哪些 supporting skills 可用，只调用当前风险真正需要的 gate：

- `define-goal`：目标模糊、成功标准不清。
- `brainstorming` / `superpowers:brainstorming`：需求发现、设计、UX、关键取舍。
- `writing-plans` / `superpowers:writing-plans`：Medium/Large 的分阶段实现。
- `test-driven-development` / `superpowers:test-driven-development`：有行为风险、可自动化 regression、核心逻辑/API/权限/数据/状态机变更。
- `systematic-debugging` / `superpowers:systematic-debugging`：失败、回归、原因不明的异常行为。
- `verification-before-completion` / `superpowers:verification-before-completion`：非平凡完成声明之前。
- `subagent-driven-development` / `superpowers:subagent-driven-development`：已有 written plan，任务可独立拆分，并适合 subagent 支持；使用它的 per-task spec compliance 和 code quality review loop。
- `executing-plans` / `superpowers:executing-plans`：subagent 不可用，或用户选择 inline execution。
- `requesting-code-review` / `superpowers:requesting-code-review`：高风险或大范围变更。
- `using-git-worktrees` / `superpowers:using-git-worktrees`：dirty worktree 或需要隔离。
- `finishing-a-development-branch` / `superpowers:finishing-a-development-branch`：plan-backed development 已实现、review、验证后，准备 merge/release handoff。
- `frontend-design`：明显的 UI 创建或重设计。
- `openai-docs`：当前 OpenAI API 或 Codex 产品事实。
- `openspec-workflow`：repo 已使用 OpenSpec 且依赖可用。
- `project-harness-init`：新项目、first MVP vertical slice、Large work 缺 current-truth docs、需要 AGENTS.md/docs/spec/plan/evidence/agent team/project skill 初始化。

Tiny 或机械改动不要强制 TDD。先定义能证明 claim 的最小 validator。低风险 supporting skill 不可用时，用 plain workflow 保留相同 gate 意图并简短说明 fallback。TDD、debugging、OpenSpec、security review、completion verification 这类高风险 gate 缺失时，要说明缺失能力，并暂停或征求是否接受更弱替代。

## Hard Gate Inheritance

本 skill 只判断 gate 是否需要；一旦路由到 supporting skill，就继承该 skill 的更强标准，不能降级。

- Debug route 或原因不明的失败 -> 使用 `systematic-debugging` / `superpowers:systematic-debugging`；root-cause investigation 前不要猜修复。
- TDD route -> 使用 `test-driven-development` / `superpowers:test-driven-development`；行为可自动化时，valid Red evidence 前不要改 production behavior。
- Plan/spec gate -> 使用 `writing-plans` / `superpowers:writing-plans` 或 `openspec-workflow`；不要用随手 summary 替代它们的方法。
- Plan execution gate -> written plan 有独立任务且 subagent 可用时，优先 `subagent-driven-development` / `superpowers:subagent-driven-development`；只有 subagent 不可用或用户选择 inline execution 时才用 `executing-plans` / `superpowers:executing-plans`。
- Completion gate -> 非平凡工作使用 `verification-before-completion` / `superpowers:verification-before-completion`；没有 fresh verification evidence 不要声称完成。
- Review gate -> 高风险或大范围工作使用 `requesting-code-review` / `superpowers:requesting-code-review` 或 isolated review pass；不要让实现者自审替代隔离 review。
- Branch finishing gate -> plan-backed development 已实现、review、验证后使用 `finishing-a-development-branch` / `superpowers:finishing-a-development-branch`。

Tiny 任务仍需要 fresh evidence，但如果没有非平凡行为变化，明确 focused validator 就可以满足 completion gate。行为风险任务跳过更强 gate 时，必须说明为什么不现实、使用什么 alternate validator、它证明什么、还剩什么未证明。

## Route To Workflow Map

使用原生 supporting skills 作为 execution engine。本 skill 选择 route 和 gates，不复刻它们的内部流程。

| Route | Native Workflow | Required Gates | Conditional Gates |
| --- | --- | --- | --- |
| Tiny | No Superpowers main chain | focused validator, diff/scope check | none unless command semantics or links changed |
| Small | Local workflow; call native skill only when triggered | focused validator, self-review | `test-driven-development` for automatable behavior; `systematic-debugging` for unclear cause |
| Debug | `systematic-debugging` | reproduce/root cause before fix, regression evidence | `test-driven-development` after root cause if adding regression guard |
| Medium | Superpowers subset | discovery, evidence plan, focused tests, phase smoke when chain matters | `brainstorming`, `writing-plans`, TDD, `requesting-code-review` |
| Large | Superpowers main chain | spec/design, `writing-plans`, plan execution, independent review, system verification | `subagent-driven-development` when tasks are independent; `executing-plans` when subagents are unavailable; TDD/debug/security/docs gates as risk requires |
| OpenSpec | `openspec-workflow` lifecycle | delegate spec/change lifecycle to OpenSpec | use Superpowers for implementation execution when the OpenSpec plan calls for it |

不要把 Large 理解成“加载所有 skill”。Large 的意思是进入完整 engineering lifecycle，然后只调用实际风险需要的 native sub-skills。

## First Move

不要从模糊请求直接开始 coding。先分类任务，并判断是否必须问问题。

只有缺失信息会改变结果、验证、风险、public API、data model、security posture 或 user-visible behavior 时，才问一个简短问题。否则给出具体 objective 并继续；当所选流程需要 gate 时再请求确认。

Minimum objective:

```text
Outcome: what will be true when done
Scope: files/modules/features in and out
Current truth: docs/specs/code paths that define the existing system
Evidence: command, test, UI check, screenshot, diff review, or acceptance condition proving completion
Stop condition: when to pause for user judgment
```

Tiny 任务的 current truth 可以很小，例如被修改文件、现有命令、README/config 片段。
## Route And Evidence Cards
非 Tiny 任务在 implementation 前先写一个短 `route_card` 和 `evidence_card`，可以放在计划、spec、PR 描述或最终回复草稿里。Tiny 任务可以内联成一句话，但仍要明确 evidence。
```yaml
route_card:
  route: Tiny | Small | Debug | Medium | Large | OpenSpec
  risk_type:
  changed_surfaces: []
  required_gates: []
  delegated_skills: []
  loaded_references: []
  stop_gates: []
evidence_card:
  claim_ceiling: Dev Done | Integration Done | Handoff Done
  pre_implementation:
  post_implementation:
  chain:
  handoff:
  review:
  gaps:
```
Task exit 和 final claim 必须回看这两张卡：如果实际 evidence 弱于 `claim_ceiling`，降低 claim；如果触发了未执行的 required gate，先补 gate 或声明 gap。可用时运行 `scripts/validate_workflow_cards.py` 检查结构。

## Process Selection

只选择一个 process level。非平凡任务用一两句话说明为什么这么分级。

| Level | Use When | Flow |
| --- | --- | --- |
| Tiny | 文本/docs/non-runtime config、typo、单点明显修复且没有 runtime 影响面 | objective -> edit -> focused verification |
| Small | 单文件、窄范围可复现 bugfix，或行为清晰的 runtime-default config 变更 | objective -> inspect existing pattern -> select gates -> delegate TDD/debug if triggered -> implement -> verify -> self-review |
| Debug | CI/test failure、production-like regression、不可复现失败、原因不明且影响面未知 | objective -> route to systematic-debugging -> reproduce/root cause -> minimal fix -> regression/focused validator -> verify |
| Medium | 1-3 个模块、新行为/API、存在有意义边界条件 | objective -> discovery -> route to brainstorming/plan/TDD as triggered -> execute plan with review gate when needed -> phase smoke/E2E |
| Large | 跨模块 feature、migration、data model 变更、安全风险、关键/跨服务 user workflow 且有 data/security/state/rollback 风险 | discovery -> route to spec/plan workflow -> execute plan with subagent review when available -> system verification |
| OpenSpec | Repo 已有 OpenSpec 且 required workflow skills 可用 | delegate lifecycle to `openspec-workflow` |

避免 accidental heavyweight process：简单修复不需要完整 spec。也避免 accidental lightweight process：高风险变更不能只靠 happy-path check。

Small vs Debug：症状窄、可复现、owner 明确时用 Small；需要读 logs/CI/production 行为或 root cause 未知时用 Debug。普通 1-3 模块 UI/API feature 默认是 Medium，除非触发 critical、cross-service、data-sensitive、rollback-sensitive 等升级条件。

## Escalation Triggers

出现以下情况时升级 process level：

- Acceptance criteria 不清且影响结果/风险；或存在 misleading completion claim 的验证缺口。
- Public API、auth、permissions、security、secrets、payments、PII、data model 变更。
- Runtime/deploy/env/availability/performance/configuration blast radius，或 cross-service/migration/recovery/concurrency/state-machine 风险。
- 多模块、架构边界未知、可能存在 docs drift。

## Review-Only Mode

用户要求 review code、PR、plan、docs、evidence 或本 skill 时，除非明确要求修改，否则不要编辑。

流程：current truth -> classify risk -> inspect artifact -> 按严重程度报告 findings -> 建议最小安全改动 -> 说明未验证范围。

Review findings 要区分 correctness、scope、evidence gaps、security、maintainability、docs drift、completion-claim risk。

Review test/evidence adequacy 时读取 `references/evidence-and-validation.md`。除非 PR 是 Large/new-project work 或修改 docs/spec harness，否则不要加载 `complex-project-harness.md`。

## Human Decision Gates

以下情况先暂停并请求用户确认：

- 改变 goal、scope、public API、data model、security posture 或 user-facing behavior。
- 安装依赖、联网、写 workspace 外部、启动长运行服务、运行破坏性命令。
- 在有真实取舍的 architecture approaches 之间做选择，或 Medium/Large 从 design/spec 进入 implementation。
- 接受已知 verification gap 作为可交付。

objective 和 approved plan 清楚后，不要每个机械步骤都暂停。继续完成 implementation、verification、review。

## Documentation Gate

先判断是否需要文档。文档的作用是减少未来 action space，不是装饰。

Large work、新项目、first MVP vertical slice、multi-agent handoff、缺失 project memory、repo 没有可靠 current-truth docs 时，在 planning 前优先路由到 `project-harness-init`。如果该 skill 不可用，再读取 `references/complex-project-harness.md` 作为 fallback。Tiny/Small 不要加载它，除非任务本身就是创建、修复或 review docs/spec harness。

已有 repo 文档结构时沿用现有约定。当前代码和 canonical docs 优先于过期/reference docs。文档不在 scope 时说明原因。
## Project Harness Init Gate (项目初始化 / 项目脚手架)

只在 repo 需要 durable project scaffolding 时使用，不要用于普通编辑。满足任一条件时使用 `project-harness-init`：

- 新 repo、新 product area，或 repo 内第一个严肃 feature。
- First MVP vertical slice 需要变成可复用 development loop。
- Large work 需要 specs、current-truth docs、agent team roles 或 repeatable evidence。
- 用户希望项目维护 AGENTS.md、docs、project skills、evals 或 agent team。

`project-harness-init` 是唯一 scaffold source of truth，负责创建或修复 `AGENTS.md`、`.agent/agents.md`、Goal Loop Mode prompt、project skill、knowledge candidates、evals、`docs/architecture.md`、`docs/adr`、`docs/specs/<feature-id>`、`docs/plans/<feature-id>.md`、`docs/evidence/<feature-id>.md`。如果该 skill 不可用，才读取 `references/complex-project-harness.md` 作为概念 fallback，并手动保持同样边界；不要运行本 skill 内的旧 scaffold。除非 docs/spec harness 就是任务本身，永远不要为 Tiny/Small 创建完整 harness。

Harness 初始化本身的 `claim_ceiling` 是 `Dev Done`：它只证明项目协作基座、spec/plan/evidence 模板和 agent roles 已创建/验证。不要把初始化说成 `Integration Done`，除非真实 MVP 或系统链路已经实现并通过 integration/smoke/E2E 证据。

## Project Skill Learning Gate (项目 skill 沉淀 / 项目 SOP)

项目学习应在 task exit 自动发生，但 promotion 必须受控。

满足以下情况时读取 `references/project-skill-lifecycle.md`：

- First MVP vertical slice 或 delivery chain 刚刚成功。
- 用户提供了项目特定 process、architecture、command、testing、delivery knowledge。
- 同类项目特定 lesson 出现两次。
- 用户希望以后类似任务减少手动提示。

Task exit 时，如果 lesson 可复用，捕获 project-local learning candidate。优先使用 `scripts/capture_learning_candidate.py`。不要把 raw lessons 直接追加到 global `AGENTS.md` 或本通用 skill。只有通过 evidence、scope、no-secret check 和 destination review 后才 promotion。

## Quality Feedback Gate (质量反馈 / 不满意升级)

用户表达 correctness、深度、docs、tests、delivery、over-process、under-process 或 missed context 方面的不满意时，把它视为 workflow evidence。

用户说结果不完整、粗糙、不生产级、过度设计、测试不足、不符合预期，或反复纠正 route/evidence/docs choices 时，读取 `references/quality-feedback-loop.md`。

继续 implementation 前先分类 failure：

```text
spec gap, grounding gap, route gap, evidence gap, review gap, handoff gap, or project-memory gap
```

第一次出现：用 explicit evidence 修复。相同 failure class 第二次出现：升级 gate 或 process level。第三次出现：进入 recovery mode，重置 objective/evidence/review plan，并捕获 failure case 或 project learning candidate。

## Agent Team Gate (agent 团队 / reviewer roles)

复杂工作使用结构化 reviewer/subagent roles，不要每次临时写 prompt。

满足以下情况时读取 `references/agent-team.md`：

- 初始化 project harness。
- Large/complex work 需要 design、plan、evidence、security/data 或 knowledge review roles。
- 用户要求为项目定义 agent team。
- 重复 review gap 说明需要 durable role。

优先使用项目内 `.agent/agents.md` 保存可复用 role contracts。Tiny 任务不要使用 agent team，因为协调成本超过收益。Review agents 默认只读，除非任务明确授予 scoped writes。

## Production Handoff Gate

当工作交付 SDK、runtime、package、CLI、MCP server、plugin、Docker image、artifact branch、onboarding docs、external-provider integration、credential-packaged artifact，或声称 "import-ready"、"drop-in"、"production-ready" 时，读取 `references/production-handoff-gate.md`。

普通 app feature、internal-only refactor、没有 consumer-facing delivery surface 的 Tiny/Small 不要加载它。

## Test And Verification Strategy (测试矩阵 / 验收证据)

实现前先定义 evidence。好的 evidence 会约束行为，让未来 agent 理解系统，而不是只增加 pass count。用户不需要自己判断什么场景跑什么测试；由 agent 根据 changed surface 选择 evidence。

当 route/evidence choice 模糊、review evidence adequacy、planning Medium/Large、质量反馈提到 testing，或修改本 skill 时，读取 `references/evidence-and-validation.md`。明显 Tiny/Small 且 validator 清楚时不要加载它。

非平凡工作要显式写 evidence plan：risk type、pre-implementation evidence、post-implementation evidence、chain evidence、handoff evidence，以及当前 evidence 允许的最高 completion claim。

### Evidence Ladder

用能抓住主要失败模式的最小 evidence set：

- Tiny/mechanical：diff review；只有 command/link semantics 变化时检查命令或链接。
- Small bug/behavior：reproduction evidence 或 focused validator；可行时自动化 regression。
- Medium feature/API/UI：focused tests；模块链路或用户链路重要时加 phase smoke/E2E。
- Large/high-risk：staged tests、independent review、system verification、docs handoff。

### Red Evidence And Alternate Validators

- 每个任务都要先定义 evidence，但不是每个任务都需要 Red。
- changed behavior 能以合理成本捕获时，路由到 TDD，尤其是 automatable bugs、core logic、API contracts、permissions、data、state-machine behavior。
- 有效 Red 必须在当前代码上因预期原因失败。如果选中了 TDD skill，遵循该 skill，不用本摘要替代。
- Tiny/mechanical、visual-only、测试环境不可用、或自动化成本高于风险时，使用 alternate validator。
- "no TDD" 绝不等于 "no evidence"。必须说明 validator 证明什么、还剩什么未证明。

### Cadence

每个 task 运行 focused tests 或 explicit validator；task exit 时运行相关 build/lint/type checks、检查 touched files、做 consistency check；Medium phase 加覆盖 user-visible/system-visible chain 的 smoke/E2E；最终完成前跑当前环境内最高信号 suite。检查太贵或不可用时，说明 substitute evidence 和 remaining risk。

好的测试来自 acceptance criteria，不测 private implementation details。优先 real code 和 realistic fixtures；只 mock 外部边界或慢/不稳定依赖。测试名应编码 state、trigger、expected behavior 和 failure impact。

## Task Exit Gate

每个 implementation task 退出前检查：

```text
Scope: diff only touches expected files and modules
Spec consistency: behavior still matches approved objective/spec/current truth
Docs consistency: affected docs are updated or explicitly not needed
Tests: focused validator run and result recorded
Build/static checks: relevant checks run or gap explained
Review: correctness, boundaries, security, and maintainability inspected
Project learning: candidate captured or explicitly not needed for MVP/repeated project lessons
```

Medium 和 Large 工作应尽量加入 independent review pass。written plan 有独立任务时，优先 `subagent-driven-development`，让每个 task 先做 spec compliance review，再做 code quality review。临时高风险工作使用 `requesting-code-review` 或 focused isolated reviewer。Review 关注 correctness、regressions、security、missing tests、docs drift、scope creep，不做风格偏好争论。

## Context And Delegation

当 side task 会淹没主上下文时，使用 read-only subagents 或 separate threads：大代码库探索、独立 review、大范围 test-gap analysis、security audit。不要委派 implementation 或并行 code changes，除非用户/工具明确允许且 scope 隔离。若 selected skill 提供 reviewer templates，使用该模板，不要自造 prompt。委派时只传最小完整上下文：goal、scope、current truth sources、constraints、expected output、what not to change。

项目有 `.agent/agents.md` 时，复用其中的 role contracts。Tiny 任务不要使用 subagents。不要让 subagents 发明缺失的 product requirements。

## Automation Gate

如果某条规则每次都要发生且可确定性检查，优先用 hook、CI check、script 或 lint rule，而不是继续加 prompt text。Skills 和 instruction files 负责 judgment；hooks 和 CI 负责 mechanics enforcement。

Examples: 重复 format/lint/test commands -> hook/CI；secret 或 PII 阻断 -> pre-tool/pre-commit/CI；稳定 PR review checklist -> `AGENTS.md` 引用的 review instruction file；重复 multi-step judgment workflow -> skill。

## Completion Contract

没有 evidence 不要声称完成。最终回复按需包含：changed files、verification evidence 及其证明内容、user-visible outcome、agent-readable/system outcome、backend capability outcome、integration-chain changes、remaining gaps、review points。

Tiny 任务可压缩成 `Changed`、`Verified`、`Gap`，但仍要明确 evidence 和 residual risk。

## Skill Validation

修改本 skill 或任何 workflow router / skill orchestration rule 后，用 pressure scenarios 验证，而不是凭直觉：

- Static checks：frontmatter、`openai.yaml`、duplicate skill versions、key sections。
- Route dry-run：Tiny/Small/Medium/Large/debug prompts 的 route、evidence、gates 是否符合预期。
- Major changes：让 fresh subagent 只用这个 `SKILL.md` 路由 cases。
- 同类 misroute 出现两次：更新能阻止它的最小规则。

真实开发暴露 route、evidence、review 或 handoff failure 且发生在本 skill repo 时，先把 minimal case 记录到 `evals/failure-cases.yaml`，再改规则。一次失败记录 evidence；重复失败才 justify minimal patch；机械重复失败应变成 hooks、scripts 或 CI，而不是更多 prompt text。

不要把项目特定 lessons 加进本通用 skill。它们应先进入 project learning candidates，再 promotion 到 repo 的 `AGENTS.md`、`.agent/skills/<project-domain>`、docs、scripts、hooks 或 CI。

## NEVER

- NEVER 用更软的本地 summary 替代已选中的 TDD/debug/OpenSpec/verification skill；本 skill 只路由 gate，不能削弱 gate。
- NEVER 让 implementer self-review 替代 plan-backed、Medium、Large 或 high-risk 工作的 isolated review gate。
- NEVER 把 Tiny/Small 任务膨胀成完整 docs/spec harness，除非 docs harness 就是任务。
- NEVER 用 happy-path evidence 交付 risky API、data、auth、permission、runtime 或 cross-service changes。
- NEVER 在 code 或 canonical docs 不一致时，把 dated specs、chat history、reference docs 当 current truth。
- NEVER 把 mock-only evidence 说成 integration chain 已证明，除非明确 mocked boundary 和 remaining risk。
- NEVER 没有 fresh evidence 就声称完成，也不要用 "should pass" 掩盖 verification gaps。
- NEVER 在没有 current-truth docs/spec surface 或用户明确接受 gap 的情况下启动 Large/new-project work。
- NEVER 在没有 delivery contract 和 fresh consumer evidence 的情况下声称 artifact、SDK、runtime 或 integration production-ready，除非用户接受该 gap。
- NEVER 让用户质量不满意重复出现却不分类 failure，也不改变 gate、evidence 或 project memory。
- NEVER 把 raw project lessons 直接 promotion 到 global `AGENTS.md` 或本通用 skill。
