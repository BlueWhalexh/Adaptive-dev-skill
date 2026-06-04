# Agent MD 写法指南

`AGENTS.md`、`CLAUDE.md`、`GEMINI.md` 这类文件，本质上是 agent 的项目级操作系统。它们不应该只写一堆“请保持代码质量”的抽象口号，也不应该把所有规则堆成一个不可执行 checklist。

更有效的写法是：把项目事实、任务路由、验证策略、停止条件写清楚，让 agent 能在运行时判断下一步该走什么流程。

## 一个好的 Agent MD 应该回答什么

1. **这个项目是什么**
   agent 需要快速知道产品、模块边界、主要用户流程和不可破坏的行为。

2. **什么任务走什么流程**
   docs-only、配置、小 bug、新功能、跨模块改动、安全/权限/数据迁移，应该分别使用什么 workflow level。

3. **怎么验证**
   每类改动对应哪些命令、测试、UI 检查或人工 review 标准。

4. **什么时候必须停下来**
   当目标、scope、API、数据模型、安全姿态、用户可见行为或依赖发生变化时，agent 不能继续猜。

5. **什么不要做**
   不做无关重构，不伪造验证，不写 secret，不绕过测试，不把临时文件提交进仓库。

## 推荐结构

```md
# AGENTS.md

## Project Context

用 3-6 句话说明项目是什么、主要模块和关键约束。

## Default Workflow

所有实现、修复、重构、设计、规划类任务优先使用 `adaptive-dev-workflow`。
根据风险选择 Tiny / Small / Medium / Large / OpenSpec。

## Workflow Routing

- Tiny: 文档、拼写、简单配置、单个明显改动。
- Small: 单文件或窄范围 bugfix，行为清楚。
- Medium: 1-3 个模块、新行为、有边界条件。
- Large: 跨模块、迁移、权限、安全、数据模型、用户可见流程。
- OpenSpec: 已有 OpenSpec，或需要长期演进的复杂能力。

## Verification

- docs-only: `git diff --check`，并检查链接/示例命令。
- frontend: 相关 unit/component test，必要时 browser check。
- backend: 相关 test，必要时 integration check。
- security/auth/data: 增加 regression test，并标注 review 风险。

## Stop Conditions

如果需要改变 public API、data model、security posture、user-facing behavior、依赖或 scope，先暂停并向用户确认。

## Boundaries

- 不做无关重构。
- 不提交 secret、token、账号信息。
- 不声称完成，除非刚运行过能证明完成的验证。
```

## 写法原则

### 1. 少写愿望，多写路由

弱：

```md
请写高质量代码，注意测试。
```

强：

```md
行为变更必须先定义验证方式。Small 任务至少运行相关 targeted test；Medium/Large 任务需要计划和验收证据。
```

### 2. 少写抽象标准，多写项目事实

弱：

```md
遵守项目最佳实践。
```

强：

```md
后端入口在 `backend/`，前端入口在 `frontend/`。认证逻辑只能在 `auth/` 边界内修改；如需改变 session 语义，必须暂停确认。
```

### 3. 少写“尽量”，多写停止条件

弱：

```md
尽量不要扩大 scope。
```

强：

```md
如果实现需要修改请求/响应结构、数据库 schema、权限语义或用户可见流程，停止编码并说明原因。
```

### 4. 验证命令要可执行

弱：

```md
运行测试。
```

强：

```md
后端改动运行 `npm run test:backend`；前端组件改动运行相关 component test；无法运行时说明原因和剩余风险。
```

## 和 Adaptive Dev Workflow 的关系

Agent MD 提供项目事实和边界，Adaptive Dev Workflow 负责运行时路由。

```text
AGENTS.md / CLAUDE.md
  -> 项目事实、禁区、验证命令、停止条件

adaptive-dev-workflow
  -> 根据任务风险选择 Tiny / Small / Medium / Large / OpenSpec
  -> 动态调用 goal、planning、TDD、debugging、verification、review
```

这两者组合后，agent 才不会只“知道规则”，而是能把规则用于当前任务。
