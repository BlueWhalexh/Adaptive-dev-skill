# Adaptive Dev Workflow

**用最轻的流程，保护真正重要的正确性。**

Adaptive Dev Workflow 是一个面向 Codex、Claude Code、Gemini CLI 等 agentic coding 工具的小型系统。它帮助 AI coding agent 判断什么时候快速推进，什么时候停下来确认需求，什么时候写计划，什么时候补测试，以及什么时候必须先验证再声称完成。

它不是一个“神奇 prompt”。它是一个面向真实软件开发的 workflow router。

任务明确时快速。风险真实时谨慎。

## 它解决什么问题

Agent coding 常见的失控方式很固定：

- agent 还没理解需求就开始写代码。
- 一个小修复被扩成大重构。
- agent 改了用户从未要求改变的行为。
- 因为“看起来很明显”，测试和验证被跳过。
- 最终回复声称完成，但没有 fresh evidence。
- 仓库变得比原问题更难 review。

这不只是模型能力问题，也是流程问题。

人类工程师不会对所有任务使用同一种流程。改一个错别字不需要 design doc；重做权限系统也不该像改错别字一样处理。Agentic coding 需要同样的判断力，但 agent 往往会滑向两个极端：纯 vibe coding，或者僵硬的重流程。

Adaptive Dev Workflow 给 agent 一个决策模型：根据风险选择最小必要工程流程。

## 这是什么

Adaptive Dev Workflow 是一个可复用 skill，用风险门控来协调开发任务：

- 需求模糊时先明确目标。
- 将任务分类为 Tiny、Small、Medium、Large 或 OpenSpec。
- 只有风险需要时才引入计划。
- 行为变更使用 TDD 或显式验证方式。
- 遇到无法解释的失败时引入 debugging discipline。
- 声称完成前必须有 fresh verification。
- scope 变化必须经过 human decision gate。

目标不是增加流程。目标是减少失控。

## 为什么不是直接 vibe code

Vibe coding 适合探索、原型和低风险一次性工作。但当输出要进入真实仓库时，它会变得昂贵。

真正的问题不是 agent 写代码，而是 agent 在写代码时默默做了产品、架构、风险和验证决策，而这些决策本来应该被显式暴露出来。

Adaptive Dev Workflow 要求 agent 在最容易伤害质量的节点停下来：

- 目标到底是什么？
- 哪些在 scope 内，哪些不在？
- 什么证据能证明完成？
- 这是单行改动，还是跨模块改动？
- 这个任务需要计划、测试、debugger，还是 review gate？

这样既保留 agentic coding 的速度，又补上真正必要的工程护栏。

## Adaptive system 如何工作

这个 skill 是协调器，不替代专业流程；它在需要时路由到它们。

```text
用户请求
  -> 明确目标
  -> 分类风险和 scope
  -> 选择 workflow level
  -> 只加入当前任务需要的 gate
  -> 在 scope 内实现
  -> 用 fresh evidence 验证
  -> 汇报改动、验证和 review 重点
```

关键是决策步骤：agent 会根据 blast radius、需求模糊度、行为风险和验证成本选择流程。

## Workflow levels

| Level | 适用场景 | 典型流程 |
| --- | --- | --- |
| Tiny | 文本、文档、配置、错别字、单个明显改动 | 确认目标 -> 编辑 -> 验证 |
| Small | 行为明确的窄范围修复 | objective -> focused implementation -> focused check |
| Medium | 1-3 个模块、新行为、有边界条件 | objective -> design/plan -> test or validator -> verify |
| Large | 跨模块功能、迁移、安全、数据模型、用户流程 | discovery -> design/spec -> staged plan -> implementation -> review -> verification |
| OpenSpec | 仓库已经使用 OpenSpec | 交给仓库的 OpenSpec workflow |

这个系统刻意保持 adaptive。它不应该强迫 README typo 走 design doc，也不应该允许 agent 无计划重写 auth flow。

## 安装

推荐仓库命名：

```text
adaptive-dev-workflow
```

当前仓库将 skill 源码放在：

```text
skills/adaptive-dev-workflow/
```

### Codex

复制或 symlink 到 Codex skills 目录：

```sh
mkdir -p ~/.codex/skills
cp -R skills/adaptive-dev-workflow ~/.codex/skills/adaptive-dev-workflow
```

然后让 Codex 使用它：

```text
Use $adaptive-dev-workflow to implement this change with the smallest process that protects correctness.
```

### Claude Code 或其他 Agent CLI

如果你的 agent 支持 local skills，把同一个目录复制到对应工具的 skill 目录。如果不支持，可以将 `skills/adaptive-dev-workflow/SKILL.md` 的内容放入项目级 instructions 或 agent memory，作为 workflow policy。

### 项目级使用

团队使用时，最实用的方式是在项目级 agent instructions 中引用：

```text
For implementation, fix, refactor, design, or planning tasks, use adaptive-dev-workflow.
Choose Tiny/Small/Medium/Large based on ambiguity, blast radius, and verification risk.
Do not claim completion without fresh verification evidence.
```

## 使用方式

当你希望 agent 做软件工作，但不想过度计划，也不想自由发挥时使用它。

示例：

```text
Use $adaptive-dev-workflow.
Add pagination to the repository list page. Keep the existing API shape unless a change is necessary.
Verify with the relevant frontend tests and a browser check.
```

文档小改：

```text
Use $adaptive-dev-workflow.
Fix the install command in README.md and verify the markdown still has no broken local links.
```

风险较高的后端改动：

```text
Use $adaptive-dev-workflow.
Refactor token refresh handling. Preserve current session semantics, add regression coverage, and stop if the API contract needs to change.
```

## 示例场景

| 请求 | 期望行为 |
| --- | --- |
| "Fix this typo in CONTRIBUTING.md" | Tiny flow，不引入重计划 |
| "Add one validation rule to a form" | Small flow，做 targeted check |
| "Add filters to an order page" | Medium flow，确认字段和验证方式 |
| "Rework permissions for admin users" | Large flow，设计/spec 和明确 review gates |
| "Investigate why tests are flaky" | 先加入 systematic debugging，再修复 |

## Case study：控制一个小功能的 scope drift

这是一个 illustrative before/after，用来说明常见 agent-coding failure mode。它不是 benchmark claim。

### Before：纯 vibe coding

请求：

```text
Add a status filter to the issues page.
```

常见 agent 行为：

- 添加 filter UI。
- 改 query parameters。
- 重写一部分 table state。
- 顺手改 unrelated styling。
- 不确认有哪些 status。
- 不验证 empty-state behavior。
- 根据“代码已改”直接报告完成。

Review 结果：

- happy path 可能可用。
- scope 比请求更大。
- reviewer 必须检查无关改动。
- 缺失的边界条件稍后才暴露。

### After：Adaptive Dev Workflow

agent 会先框定任务：

```text
Outcome: issues page can filter by existing issue status.
Scope: status filter UI, query state, and data request only; no table redesign.
Evidence: targeted frontend test or browser check covering active filter and empty state.
Stop condition: pause if the backend API does not already support status filtering.
```

然后根据现有代码选择 Small 或 Medium。如果 backend 已支持该参数，任务保持窄范围。如果不支持，agent 会在扩展到 backend 工作前停下来。

Review 结果：

- surprise edits 更少。
- acceptance criteria 更清晰。
- 验证和行为绑定。
- scope 变化时，agent 有明确理由暂停。

## Why this works

Adaptive Dev Workflow 有效，是因为它把流程当作 risk control，而不是仪式。

设计原则：

- **Right-sized process:** 使用能保护正确性的最小流程。
- **Explicit scope:** 编码前暴露隐藏假设。
- **Human decision gates:** 当 agent 可能改变目标、API、安全姿态或用户可见行为时暂停。
- **Fresh evidence:** 没有运行能证明完成的检查，就不能声称完成。
- **Composable discipline:** 只在有用时调用 planning、TDD、debugging、OpenSpec 或 review workflow。
- **Repo empathy:** 先读项目，沿用既有约定。

这个系统在 agent 最容易破坏代码库的边界处保持保守。

## 它不是什么

Adaptive Dev Workflow 不是：

- 生成代码正确性的保证。
- human review 的替代品。
- 已验证的 productivity benchmark。
- 每个任务都必须使用的重型 spec 流程。
- 能让模糊需求自动安全的 prompt。
- tests、CI 或 observability 的替代品。

它最适合真实代码库：reviewability、scope control 和 verification 都重要的场景。

它不太适合一次性原型、正确性不重要的实验，或者已经有成熟 agent workflow 且具备等价 gate 的团队。

## 仓库结构

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

贡献应保留核心思想：adaptive discipline，而不是 fixed ceremony。

有价值的贡献包括：

- 更清晰的特定 agent 工具安装路径。
- 不夸大的真实 case study。
- 更清晰的 workflow level 决策规则。
- 展示 skill 何时应该暂停并询问的示例。
- Codex、Claude Code、Gemini CLI 等工具的兼容说明。

请避免把项目变成万能 AI coding 宣言或巨大 checklist。价值在于选择“仍能保护正确性的最小流程”。
