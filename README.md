# Adaptive Dev Workflow

**不是再写一个 prompt，而是给 AI coding 一个自适应工程系统。**

Adaptive Dev Workflow 是面向 Codex、Claude Code、Gemini CLI 等 agentic coding 工具的轻量 SDD coordinator。它帮助 AI coding agent 判断什么时候快速推进，什么时候进入 spec-driven flow，什么时候调用 planning / TDD / debugging / verification / review skills，以及什么时候必须停下来让人决策。

它不是一个“神奇 prompt”。它是一个把现有 agent skills、项目级 AGENTS.md / CLAUDE.md 规则、验证门控组合起来的 workflow router。

任务明确时快速。风险真实时谨慎。

## SDD 驱动时代已经来了

过去的 AI coding 很像即时聊天：你提出一个需求，agent 直接开始改代码。它快，但上下文、边界和验收标准经常只存在于对话里。一旦会话变长、项目变复杂、多人协作或多 agent 接力，问题就会出现：需求漂移、计划漂移、实现漂移，最后 reviewer 只能从 diff 里倒推 agent 到底理解了什么。

SDD，也就是 Spec-Driven Development，正在成为 AI coding 的关键方向。它的核心不是“写很多文档”，而是把 intent、requirements、boundaries、acceptance criteria 变成 agent 和人都能反复读取的 source of truth。代码不再是 agent 猜出来的第一产物，而是围绕 spec、tests、review gates 被生成、修改和验证的结果。

但完整 SDD 也有成本：

- 写 spec 需要时间。
- spec 会过期，需要维护。
- 小任务不值得启动完整 spec lifecycle。
- 复杂框架可能要求额外目录、命令、状态机和 review 流程。
- 普通开发者只是想让 agent 不乱改仓库，不一定想先引入一套重型工程体系。

Adaptive Dev Workflow 的切入点就是这里：**用 SDD 的思想治理 agent，但不把每个任务都变成完整 SDD 项目。**

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

## 为什么不直接用现有 skills

现在已经有很多很好用的 agent skills 或 workflow：

- `define-goal`：把模糊需求变成可验证目标。
- `brainstorming`：探索需求、方案和设计取舍。
- `writing-plans`：把设计拆成可执行计划。
- `test-driven-development`：用 TDD 约束行为变更。
- `systematic-debugging`：避免凭感觉修 bug。
- `verification-before-completion`：禁止没有证据就声称完成。
- `requesting-code-review`：在高风险改动后引入 review。
- `OpenSpec` / spec workflow：为复杂项目提供完整 spec lifecycle。

问题是：这些 skill 本身都很有用，但**直接让用户或 agent 手动选择它们，成本太高**。

常见失败方式：

- 小任务被套上过重流程，token 和时间浪费明显。
- 大任务被当成普通 patch，缺少 design、test 和 review gate。
- agent 忘记调用某个关键 skill，比如修 bug 时跳过 debugging，收尾时跳过 verification。
- 用户不知道什么时候该用 OpenSpec，什么时候只需要一个轻量 objective。
- 项目级 `AGENTS.md` / `CLAUDE.md` 写了很多规则，但没有一个 runtime decision model，agent 仍然不知道下一步该走哪个流程。

Adaptive Dev Workflow 不是替代这些 skill，而是给它们加一个入口层：先判断任务风险，再选择需要的最小 skill 组合。

## 我做了哪些扩展

这个项目在现有 skills 之上增加了四层东西：

1. **Workflow router**
   先把任务分成 Tiny / Small / Medium / Large / OpenSpec，再决定是否需要 goal、brainstorming、plan、TDD、debugging、verification 或 review。

2. **Cost-aware process**
   不为了“看起来专业”启动完整流程。README typo 走 Tiny；单点 bug 走 Small；跨模块、用户可见、数据模型、安全相关改动才进入 Medium/Large 或 OpenSpec。

3. **Human decision gates**
   agent 不应该每一步都问人，但必须在改变目标、scope、public API、data model、security posture、user-facing behavior、依赖或架构路线时暂停。

4. **Agent MD optimization**
   `AGENTS.md`、`CLAUDE.md`、`GEMINI.md` 这类 agent memory 文件不应该只是规则堆叠。它们应该告诉 agent：
   - 什么任务必须进入 adaptive workflow。
   - 哪些目录、命令、验证方式是项目事实。
   - 哪些行为是禁区，比如无关重构、跳过验证、写入 secret。
   - scope 变化时应该停下来，而不是继续“帮忙”。
   - docs-only、配置、业务逻辑、权限、安全任务分别用什么验证标准。

也就是说，这个项目不是“又一个 skill 文件”，而是把 skill、SDD 思想和 agent memory 组织成一个可落地的工程入口。

## Agent MD 应该怎么写

`AGENTS.md` / `CLAUDE.md` 最重要的价值不是提醒 agent “写高质量代码”，而是把项目里的判断标准变成可执行路由：

- **任务路由：** 哪些任务走 Tiny / Small / Medium / Large / OpenSpec。
- **项目事实：** 入口、模块边界、测试命令、禁区、部署方式。
- **验证策略：** docs-only、frontend、backend、auth/security、data migration 分别如何证明完成。
- **停止条件：** 什么时候 agent 不能继续猜，必须让人决策。

弱写法：

```md
请保持代码质量，注意测试，不要乱改。
```

强写法：

```md
行为变更必须先定义验证方式。
Small 任务至少运行相关 targeted test。
如果需要改变 public API、data model、security posture 或 user-facing behavior，停止编码并向用户确认。
```

可复制模板：

- [examples/AGENTS.md](examples/AGENTS.md)：适合 Codex / 通用 agent 的项目级规则模板。
- [examples/CLAUDE.md](examples/CLAUDE.md)：适合 Claude Code 的项目级规则模板。
- [docs/agent-md-guide.md](docs/agent-md-guide.md)：详细写法指南和反例/正例。

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

这个 skill 是 SDD-lite coordinator，不替代专业流程；它在需要时路由到它们。

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

## 与普通 prompt、checklist、重型 SDD 的区别

| 方式 | 优点 | 问题 | Adaptive Dev Workflow 的做法 |
| --- | --- | --- | --- |
| 普通 prompt | 轻、快、容易复制 | 没有稳定门控，agent 容易继续猜 | 把“何时停下、何时验证、何时升级流程”写成系统规则 |
| Checklist | 明确、好 review | 对所有任务一视同仁，容易变成仪式 | 根据风险选择最小必要 checklist |
| 单个 skill | 专项能力强 | 用户要知道何时调用哪个 skill | 用 router 统一入口 |
| 重型 SDD / OpenSpec | 适合复杂项目和长期演进 | 对小任务成本高，维护 spec 也有负担 | 只有 Medium/Large/OpenSpec 才升级 |
| AGENTS.md / CLAUDE.md 规则堆 | 持久、项目级 | 容易变成静态约束，缺少运行时决策 | 把 agent md 变成流程路由和验证策略 |

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
├── examples/                       # copyable prompts and Agent MD templates
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

## 背景阅读

- [SpecDD](https://specdd.ai/)：把 intent、requirements、boundaries、completion criteria 作为人和 agent 的 shared source of truth。
- [Spec-Driven Development with AI Agents](https://www.xcapit.com/en/blog/spec-driven-development-ai-agents)：介绍 spec 作为系统行为 single source of truth 的 SDD 视角。
- [OpenAI Codex AGENTS.md docs](https://github.com/openai/codex/blob/main/docs/agents_md.md)：Codex 对 `AGENTS.md` 作用域和层级指令的说明。
- [Anthropic Claude Code memory docs](https://docs.anthropic.com/zh-CN/docs/claude-code/memory)：`CLAUDE.md` 作为项目共享指令和跨会话记忆的说明。
