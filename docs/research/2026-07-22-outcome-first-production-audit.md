# Adaptive 生产轨迹审计与 Outcome Guard 设计

日期：2026-07-22

## 结论

旧版 `adaptive-dev-workflow` 作为“所有开发任务的 admission router”已经没有继续默认存在的必要。它把模型本来能完成的规划、实现和验证重新包成控制面，并通过 `AGENTS.md`、隐式 Skill、workflow manifest、计划和交接 prompt 多次固化，最终形成流程自我延续。

仍有价值的不是完整 Router，而是一条更窄的能力：在长期、高不确定或 AI 行为效果任务中，防止工程流程抢占用户结果。因此保留同名兼容入口，但职责改为 **Outcome Guard**：只决定当前应 `prove`、`improve` 还是 `harden`，普通任务直接 `bypass`；发布取舍明确后退出 Guard，由交付流程接管。

这不是降低质量。它把质量门从“每一步都执行完整仪式”改成“证据与当前声明匹配”，并保留权限、数据、安全、public contract、迁移和 release/handoff 的强验证。

## 调研方法

### 生产对话样本

审计了 `spt-ai-workflow` 项目下多个长短任务的最近轨迹，重点统计 agent 启动、review 角色、实现角色、压缩次数和用户纠偏。数字是轨迹事件计数，不是账单 token，也不应被解释成精确并发数。

| 场景 | 抽样规模 | 观察到的 Agent 行为 | 主要结果 |
| --- | ---: | --- | --- |
| Query stable-open | 最近 80 turns；扩大样本 150 turns | 79 次 subagent start，41 review；扩大样本 189 个唯一 subagent，其中 88 review、25 implementation | Review 远多于能力验证；多次 compaction |
| Import orchestrator | 最近 80 turns；扩大样本 | 427 次 subagent start，其中 183 review、89 implementation；扩大样本 529 个唯一 subagent，其中 242 review | 最严重的 review factory；核心导入链路被控制面和可靠性建设挤压 |
| Import hardening | 最近 80 turns | 20 个 subagent，18 个 review | 已进入 hardening，但 reviewer 占比仍异常 |
| Original Query | 最近 80 turns | 126 次 compaction，约 1833 次文件触达事件 | 即使没有显式 subagent，也因上下文和范围过大持续变重 |
| Graph MVP | 19 turns | 7 个 reviewer | MVP 阶段仍过早进入密集 review |
| Frontend UX | 9 turns | 0 subagent | focused 修改和 browser evidence 顺利完成 |
| Review-only | 2 turns | 0 subagent | 窄任务不需要总控流程也能正确完成 |

### 用户纠偏信号

长任务中反复出现以下明确反馈：

- “优先保证基本可用”。
- “不要过度 review”。
- “时间花在刀刃上”。
- “开发这么久还在第一步”。
- “先跑通一次核心链路，再做工程可靠性建设”。
- “优先应该是保证导入链路没问题，其他工程保证基于这个基础”。

问题不是 Agent 没听见。Agent 多次复述并同意这些原则，但下一轮又被既有 Plan、manifest、review finding、项目规则和交接 prompt 拉回旧流程。这说明根因是 **policy persistence**，不是单轮 prompt 不够明确。

## 痛点模型

### P1. Premature Hardening

最小真实链路尚未证明，就建设完整 eval、观测、恢复、并发、交付和知识沉淀。结果是工程资产增加，但用户仍看不到可用结果。

### P2. Control-plane Inversion

workflow state、artifact graph、review ledger 和 task evidence 从支持开发变成开发本身。Agent 用“流程已推进”替代“能力已提升”。

### P3. Parent Risk Inheritance

因为总项目是 L3，后续文档修订、局部 bug、schema 小改也继承 L3 仪式。文件数、父任务等级和 Plan checkbox 被错误用作当前 slice 风险代理。

### P4. Review Capture

每个 Task 创建 implementer、spec reviewer、quality reviewer、fixer、re-review。Minor finding 也改变主优先级，最终出现 reviewer 数量远高于实现和真实场景验证。

### P5. Verification Inflation

局部改动在每个 Task 后运行相邻甚至全量回归，把最终 release gate 提前摊销到所有中间步骤。测试本身没有错，错误是测试范围和本轮 claim 不匹配。

### P6. Context And Workspace Entropy

大量 fresh subagent、compaction、worktree 和 handoff artifact 增加搬运与清理成本。隔离只有在输入被裁剪、并行价值明确时才成立；“fresh agent per task”不自动等于高效。

## Skill 调用审计

| Skill / 机制 | 合理场景 | 生产中的误用 | 新边界 |
| --- | --- | --- | --- |
| `adaptive-dev-workflow` | 长期目标、MVP、AI 行为效果、process drift | 所有实现/修复/设计默认 admission | 仅 Outcome Guard；普通任务 bypass |
| `workflow-control-plane` | 真正需要跨进程恢复的外部 orchestrator | 成熟计划续作仍维护 manifest 和 stage 仪式 | 默认关闭隐式触发，仅显式 legacy/runtime 场景 |
| `subagent-driven-development` | 独立任务多、上下文可封包、审查收益高 | 文档和每个小 Task 都 fresh implementer + 双 review | 不再默认调用；最多一个边界 reviewer |
| `writing-plans` / `specflow` | 尚无 approved 方案且真实存在范围/契约不确定性 | 已有 Spec/Plan 后重复生成或复审 | 直接消费已有 artifact；只补缺失决策 |
| `test-driven-development` | 可自动化行为回归、核心逻辑和高风险边界 | 纯文档、机械改动或已有明确 validator 也走完整 RED | 按当前行为与回归价值调用 |
| `change-aware-testing` | 大仓库无法人工可靠选择 affected tests | 每个小步都引入额外 test-routing 控制面 | 默认关闭隐式触发；优先项目原生命令 |
| `agent-orchestration` | 2 个以上真正独立工作流 | 把角色模板当作默认开发团队 | 默认关闭；共享写状态或顺序依赖时不并行 |
| `knowledge-promotion` | 模式已重复验证且用户要求沉淀 | Basic Usable 前就创建项目 Skill/知识流程 | 后处理、显式触发，不是默认交付阶段 |
| `delivery-verification` | integration/release/handoff claim | 中间 Task 提前承担完整交付门 | 只在申请相应 claim 时调用 |

## 什么能由 Skill 解决

可以写入 Skill 的内容必须满足：跨项目稳定、模型容易系统性忽略、可用 eval 判断对错。

本次保留四条：

1. **Outcome Before Process**：每轮先产生用户可见 capability delta。
2. **Current Slice, Not Parent Risk**：按当前 changed surface 判断风险。
3. **Evidence Proportional to the Claim**：局部、Basic Usable、Harden、Release 分别验证。
4. **Budget the Process**：默认零 subagent、零新文档、零 manifest；有明确收益才增加。

这些规则能直接对抗生产轨迹中的稳定失败模式，又不会替模型重写通用软件工程知识。

## 什么不应由 Skill 解决

以下内容需要项目事实、工具或人的价值判断，不应继续塞进全局 Skill：

- 具体业务的 Basic Usable 门槛：由产品目标和代表场景决定。
- public API、权限、数据和不可逆生产决策：需要人授权。
- 项目测试映射：优先写成项目命令、测试选择脚本或 CI，而不是自然语言路由。
- Worktree 创建、租约、回收：应由 orchestrator/runtime 管理生命周期。
- 跨会话调度、重试、并发和恢复：这是 Symphony 一类运行时问题，不是 SKILL.md 问题。
- 自动修改 `AGENTS.md`：只能基于重复、已验证、项目特有的事实提出小 diff；不得把一次纠偏自动升级为永久规则。

## GitHub 与官方实现对照

### OpenAI Harness Engineering

OpenAI 把短 `AGENTS.md` 当目录，把结构化 `docs/` 当事实源，并通过应用可观测性、浏览器能力和真实工具让 Agent 自己验证。关键启发是提高环境的 legibility 和可执行反馈，而不是增加通用流程文字。来源：[Harness engineering](https://openai.com/index/harness-engineering/)。

### Anthropic Agent Skills

官方明确把上下文视为公共资源，默认模型已经足够聪明；Skill 应简洁、渐进加载，并用至少三个真实场景测试。每增加一个 Skill 都有上下文成本，因此窄触发和关闭无关隐式 Skill 是必要优化。来源：[Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)、[Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)。

### Superpowers

Superpowers 的强项是职责清晰的窄 Skill，以及在 approved design + 独立 tasks 前提下执行严格 RED/GREEN、fresh subagent 和双 review。其完整链本来就是高纪律方法论，不是所有生产续作的最低成本默认值。来源：[obra/superpowers](https://github.com/obra/superpowers)、[subagent-driven-development](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md)。

### OpenAI Symphony

Symphony 把 issue polling、唯一调度状态、workspace、重试、恢复和观测放在独立 orchestrator runtime，并明确自己不是通用 workflow engine。它说明 worktree 清理和多会话恢复需要代码化生命周期，不应依赖开发 Skill 自觉。来源：[openai/symphony SPEC](https://github.com/openai/symphony/blob/main/SPEC.md)。

### Microsoft AGENTS.md Generator

Microsoft 的生成 Skill 聚焦真实 build/test 命令、项目结构和边界，并明确不覆盖已有 `AGENTS.md`。这支持“项目事实地图”定位，不支持把全局 SDD 写入每个项目。来源：[wiki-agents-md](https://github.com/microsoft/skills/blob/main/.github/plugins/deep-wiki/skills/wiki-agents-md/SKILL.md)。

### Lattice

Lattice 的独特点是 repo-local、可版本化、可审计的 Spec/Plan/Review/Verify 和 evidence pipeline，适合团队需要合规、恢复和趋势分析的场景。它不是所有个人开发任务的默认方法：把它全量套到尚未证明的 MVP，会重现当前痛点。来源：[zdolphin07-dotcom/lattice](https://github.com/zdolphin07-dotcom/lattice)。

## 交付设计

### 默认链路

```text
普通明确任务
  -> 模型原生执行
  -> focused validator
  -> 完成

长期/高不确定目标
  -> Outcome Guard
  -> prove: Minimum Real Slice
  -> improve: failure cluster + one behavioral lever
  -> Basic Usable decision
  -> harden: reliability objectives
  -> release approved
  -> exit Outcome Guard
  -> delivery verification
```

### 过程预算

| 当前动作 | 默认预算 |
| --- | --- |
| bypass / prove / improve 的单一 slice | 0 subagent、0 新文档、0 manifest |
| 独立高风险边界 review | 1 reviewer、最多 1 次 delta re-review |
| 2 个以上真正独立工作流 | 按需并行；不得共享写状态 |
| 跨会话目标 | 一个短 Goal Card；同会话不创建 |
| release/handoff | 按项目交付契约增加 evidence，不继承到之前每个 Task |

### 阶段汇报

```text
Current outcome:
Latest capability delta:
Evidence:
Top blocker:
Next action:
Deferred:
```

这六项足以让人判断方向，不再要求用户阅读每个 reviewer、manifest 和 worktree 事件。

## AGENTS.md 决策

不需要把完整使用方式写进全局 `AGENTS.md`，更不能继续写“所有开发任务优先使用 Adaptive”。Skill frontmatter 负责窄触发。

可选只保留一行：

```md
- 仅在长期目标、MVP/Basic Usable、AI 行为效果迭代或流程明显跑偏时使用 `adaptive-dev-workflow`；普通开发任务直接执行，不创建 workflow manifest。
```

项目 `AGENTS.md` 只写真实入口、架构/安全/数据边界、可执行命令和需要人的不可逆决策。不要按文件数暂停，不要默认每个 Task 使用 Spec、TDD、Reviewer、Worktree 或全量测试。

## 风险与后续边界

- Outcome Guard 不能替代产品对 Basic Usable 的最终判断。
- fresh-agent route eval 只能证明语义选择，不等于真实项目 outcome 改善。
- 真正效果需要在后续 Query/Import 任务记录 time-to-first-real-evidence、review/implementation ratio、subagent 数、compaction 数和 Basic Usable pass rate。
- 如果新版本仍反复把非阻塞 finding 提到 Top blocker，应先修触发/优先级规则；不要重新加入完整 lifecycle。
