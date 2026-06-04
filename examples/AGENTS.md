# AGENTS.md

全局项目协作约定。项目特定架构、命令、禁区、历史决策应沉淀到本文件或更具体目录下的 `AGENTS.md`。

## Project Context

本项目是一个真实软件仓库，不是一次性 demo。Agent 的目标是完成用户请求，同时保持 scope 清晰、diff 可 review、验证可复现。

优先读取：

- `README.md`
- 项目入口和配置文件
- 与当前任务直接相关的源码、测试和文档
- 最近的 git 状态

## Default Workflow

遇到实现、修复、重构、设计、规划类软件任务，优先使用 `adaptive-dev-workflow`。

目标不是增加流程，而是根据风险选择最小必要流程：

- 任务明显时快速。
- 行为变化时验证。
- scope 变化时暂停。
- 风险真实时升级到计划、测试、debugging、review 或 OpenSpec。

## Workflow Routing

| Level | Use when | Required behavior |
| --- | --- | --- |
| Tiny | docs、拼写、配置、小型明显改动 | 直接改，运行最小检查 |
| Small | 单文件或窄范围 bugfix | 明确 objective，做 targeted verification |
| Medium | 1-3 个模块、新行为、有边界条件 | 先确认目标和方案，再实现并验证 |
| Large | 跨模块、迁移、安全、权限、数据模型、用户流程 | 先 discovery/design/spec，再分阶段实现 |
| OpenSpec | 仓库已有 OpenSpec 或需求需要长期演进 | 进入 OpenSpec workflow |

## Verification

每次产生代码或文档改动后，最终回复必须说明执行过的验证和结果。

默认验证策略：

- docs-only: `git diff --check`，并检查示例命令是否仍然合理。
- frontend: 运行相关 unit/component test；必要时做 browser check。
- backend: 运行相关 targeted test；涉及 API 时检查 request/response contract。
- auth/security: 增加或运行 regression test，并标注 review 风险。
- data migration: 明确 rollback/backup/verification 方式，未确认前不要执行 destructive operation。

如果无法验证，必须说明原因和剩余风险。

## Stop Conditions

遇到以下情况必须暂停并向用户确认：

- 目标或 scope 需要改变。
- public API、data model、security posture、user-facing behavior 需要改变。
- 需要新增依赖、联网、写出工作区、启动长时间服务或执行 destructive command。
- 现有测试无法证明行为，需要用户选择验证方式。
- 需求含糊，且不同理解会导致不同实现。

## Boundaries

- 不做无关重构。
- 不提交 secret、token、账号、私钥。
- 不伪造命令、测试、联网、工具调用结果。
- 不把临时文件、生成缓存、个人本地配置提交到仓库。
- 不在没有 fresh evidence 的情况下声称完成。

## Final Response

最终回复包含：

- 改了什么。
- 验证了什么。
- 未验证原因和剩余风险，如有。
- 需要 review 的关键点：正确性、边界、安全性。
