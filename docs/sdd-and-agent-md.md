# SDD、Skills 和 Agent MD

Adaptive Dev Workflow 的定位不是替代 SDD，而是把 SDD 的核心思想压缩成适合日常 agent coding 的入口系统。

## SDD 驱动是什么

SDD 是 Spec-Driven Development。它强调先明确 spec，再让实现围绕 spec 展开。对 AI coding 来说，spec 的价值尤其明显：它把 intent、requirements、boundaries 和 acceptance criteria 从一次性对话中提取出来，变成人和 agent 都能反复读取的 source of truth。

这能解决几个 AI coding 的结构性问题：

- agent 不再只根据最近几轮对话猜需求。
- reviewer 可以用 spec 对照 diff。
- 多轮会话或多 agent 接力时，目标不容易丢失。
- tests、docs 和实现可以围绕同一份意图校准。

## SDD 的成本

完整 SDD 不适合所有任务。

它通常需要：

- 维护 spec 文件。
- 定义 proposal、design、tasks、implementation、review 等阶段。
- 让 agent 和人都遵守状态转换。
- 在实现发现新约束时更新 spec。
- 为不同模块维护不同粒度的上下文。

这对复杂功能、长期项目和高风险改动很有价值。但对 README typo、单点配置修复、窄范围 bugfix 来说，完整 SDD 会制造不必要成本。

## 现有 skills 为什么还不够

单个 skill 解决的是局部动作：

- `define-goal` 解决目标定义。
- `brainstorming` 解决需求探索。
- `writing-plans` 解决计划拆解。
- `test-driven-development` 解决行为约束。
- `systematic-debugging` 解决 bug 定位。
- `verification-before-completion` 解决完成前证据。
- `requesting-code-review` 解决高风险 review。
- `OpenSpec` 解决完整 spec lifecycle。

但真实开发的难点是：当前任务到底该调用哪些 skill，调用到什么程度，什么时候停下来。

如果没有 router，agent 很容易：

- 对小任务过度流程化。
- 对大任务过度乐观。
- 忘记关键 gate。
- 在 scope 变化时继续写代码。
- 把项目级规则当成背景噪音。

## Adaptive Dev Workflow 的扩展

Adaptive Dev Workflow 把这些能力组织成一个决策层：

```text
task risk -> workflow level -> skill composition -> verification evidence
```

它扩展了三件事：

- **流程分级：** Tiny / Small / Medium / Large / OpenSpec。
- **动态升级：** 任务变复杂时升级到 planning、TDD、debugging、review 或 OpenSpec。
- **停止条件：** 当目标、scope、API、安全、数据模型或用户行为要改变时，让 agent 停下来。

它的目标不是让 agent 更自由，而是让 agent 在关键点别继续猜。

## AGENTS.md / CLAUDE.md 怎么优化

`AGENTS.md`、`CLAUDE.md`、`GEMINI.md` 这类文件是 agent 的项目级记忆。它们不应该只写“请保持代码质量”这种宽泛句子，也不应该塞满几十条互相竞争的 checklist。

更有效的写法是把它们组织成四类信息：

1. **任务路由**
   哪些任务必须进入 `adaptive-dev-workflow`，哪些任务可以 Tiny 处理，哪些任务必须升级到 OpenSpec 或 review。

2. **项目事实**
   入口、架构边界、关键目录、常用测试命令、禁区、部署方式。

3. **验证策略**
   docs-only、frontend、backend、security、data migration 分别如何验证。

4. **停止条件**
   什么情况下 agent 不能继续猜，必须向用户确认。

一个好的 agent md 不是让 agent “更听话”，而是让 agent 在正确的时刻知道下一步该用什么流程。

可复制模板见：

- [`examples/AGENTS.md`](../examples/AGENTS.md)
- [`examples/CLAUDE.md`](../examples/CLAUDE.md)
- [`docs/agent-md-guide.md`](./agent-md-guide.md)
