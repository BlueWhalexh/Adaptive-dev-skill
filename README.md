# Adaptive Dev Skill

Adaptive Dev Skill 不是所有软件任务的总控工作流。它只解决一种前沿模型仍容易犯的错误：长期或高不确定目标被 Spec、Review、测试基础设施、Subagent 和 Worktree 吞没，真实能力迟迟没有跑通。

当前默认产品只有一个轻量 Outcome Guard：

```text
Goal
  -> Minimum Real Slice
  -> Basic Usable evidence
  -> outcome iteration
  -> hardening
  -> release / handoff
```

普通 bugfix、明确功能、文档、样式和纯 Review 不需要调用它。

## Four Laws

1. **Outcome Before Process**：流程 artifact 不是 capability delta。
2. **Current Slice, Not Parent Risk**：项目是 L3，不代表每个局部修改都走 L3。
3. **Evidence Proportional to the Claim**：中间小步不提前承担 Release Gate。
4. **Budget the Process**：默认零 Subagent、零新文档、零 manifest；只在真实边界增加。

## When To Use

使用 `$adaptive-dev-workflow`：

- 新 AI/LLM/Agent/检索链路尚未证明方向可行。
- 用户要求目标模式、MVP、Basic Usable、先跑通或持续迭代。
- 长任务已经被 Review、观测、测试或编排带偏。
- Basic Usable 已成立，准备进入 hardening 或 release。

不要使用：

- 普通明确任务。
- 已知 bug 的局部修复。
- 文档、视觉调整、纯代码 Review。
- 只需直接调用 `technical-design`、`systematic-debugging` 或 `skill-creator` 的专门任务。

## Outcome Modes

| Mode | Purpose |
| --- | --- |
| `bypass` | 普通任务绕过 Adaptive |
| `prove` | 用 Minimum Real Slice 证明方向可行 |
| `improve` | 用小矩阵和 failure cluster 迭代到 Basic Usable |
| `harden` | 在已可用基础上补可靠性、恢复、并发和观测 |
| `release` | 执行完整交付、fresh consumer、real external 和 rollback 验收 |

## Install

默认只安装 Outcome Guard：

```sh
mkdir -p "$HOME/.codex/skills/adaptive-dev-workflow"
rsync -a skills/adaptive-dev-workflow/ "$HOME/.codex/skills/adaptive-dev-workflow/"
```

如果同时使用 Claude Code：

```sh
mkdir -p "$HOME/.agents/skills/adaptive-dev-workflow"
rsync -a skills/adaptive-dev-workflow/ "$HOME/.agents/skills/adaptive-dev-workflow/"
```

不建议在全局 `AGENTS.md` 中规定“所有开发任务必须使用 Adaptive”。Skill 的双语 description 已覆盖窄触发场景。

可选的一行全局规则：

```md
- 仅在长期目标、MVP/Basic Usable、AI 行为效果迭代或流程明显跑偏时使用 `adaptive-dev-workflow`；普通开发任务直接执行，不创建 workflow manifest。
```

## Optional Specialist Skills

仓库仍保留以下窄 Skill，供用户显式安装和调用：

| Skill | Explicit use |
| --- | --- |
| `brainstorming` | 产品、交互、架构或 public contract 存在会改变结果的未决选择；明确的小功能和字段扩展不调用 |
| `test-driven-development` | 高回归价值、可自动化的行为切片；按切片集中一轮 RED/GREEN，不为每个断言重复 |
| `change-aware-testing` | 项目确实需要按 diff 选择测试 |
| `technical-design` | 存在真实架构/契约/迁移设计决策 |
| `delivery-verification` | 申请 integration/release/handoff 声明 |
| `agent-orchestration` | 2 个独立 writer、3 个以上角色/会话，或明确要求 orchestrator；单 maker + checker 不加载 |
| `project-harness-init` | 用户明确要求初始化项目 harness |
| `knowledge-promotion` | 用户明确要求沉淀已验证项目经验 |

`workflow-control-plane`、`context-grounding`、`specflow` 和 `superpowers-adapter` 作为兼容/高级组件保留，但默认不安装、不隐式调用。已有项目确实依赖 canonical manifest 时可以显式使用。

原生 `superpowers:brainstorming` 和 `superpowers:test-driven-development` 的默认触发范围过宽，不属于推荐安装集合；使用本仓库的轻量同名 Skill。其他 Superpowers Skill 仍可按当前动作选择性使用。

## AGENTS.md Boundary

`AGENTS.md` 应保存项目事实、真实命令和不可违反边界，不应复制一套通用开发方法论。

推荐保留：

- 项目入口和事实源。
- 架构/安全/数据边界。
- 可执行的测试和启动命令。
- 需要人决定的不可逆操作。

推荐删除：

- 所有开发任务强制路由 Adaptive。
- 按文件数量暂停。
- 每个 Task 强制 TDD、独立 Reviewer、Worktree 和 commit。
- 把项目最大风险继承给所有后续小步。

## Validation

Deterministic：

```sh
python3 scripts/run-skill-sandbox-eval.py
```

Fresh-agent semantic eval：

```sh
python3 scripts/run-fresh-agent-route-eval.py --repeat 1
python3 scripts/run-specialist-routing-eval.py --repeat 1
```

测试集包含真实生产场景的抽象版本：Query Basic Usable、Import Minimum Real Slice、process drift、局部 CAS bug、前端修复、文档事实核对、权限设计和 package handoff。

## Historical Components

2026-07-22 之前的 control-plane schema、strategy registry、artifact graph 和 eval report 仍保留，用于已有项目兼容和研究。它们不再代表默认使用方式。

完整生产轨迹分析见 `docs/research/`。
