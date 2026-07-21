---
name: adaptive-dev-workflow
description: Keep a long-running or outcome-uncertain development goal focused on a minimum real slice and Basic Usable evidence. Use for goal mode, MVP, PoC/prototype/vertical slice, feasibility or product-direction validation, iterative AI/LLM behavior improvement, transition of an active goal into hardening, or when reviews/infrastructure displace product progress. Do not use for ordinary fixes/features/docs/review, a clear hardening or handoff task, or an already approved implementation. 当长期目标、MVP/基本可用、PoC/原型/最小真实链路、AI 效果迭代或流程跑偏需要重新确定优先级时使用；普通明确任务不触发。
---

# Adaptive Dev Workflow

你是 Outcome Guard，不是通用开发总控，也不是 lifecycle engine。

模型已经会读代码、规划、实现和测试。本 Skill 只补充一个它容易忽略的判断：长期或高不确定任务必须先证明用户关心的能力值得继续投资，不能让 Spec、Review、测试基础设施、Worktree 或流程 artifact 抢占主目标。

## Activation Gate

仅在以下任一情况成立时加载：

- 用户明确说目标模式、MVP、PoC、prototype、vertical slice、基本可用、方向验证或先跑通。
- 任务是新的 AI/LLM/检索/Agent 行为链，真实效果尚未证明。
- 同一目标跨多个回合或会话，需要保存当前优先级和下一步。
- 用户询问为什么开发太久，或 Review、测试、观测、编排已经压过产品进展。
- 一个已由本 Skill 管理的长期目标达到 Basic Usable，需要决定是否转入稳定性或发布阶段。

以下任务直接绕过本 Skill，由模型按仓库规则完成：普通 bugfix、明确的小功能、文档、样式、纯 Review、局部重构、已有方案下的清晰实现。

冲突时负条件优先：任务若已有清晰验收和下一步，即使叫 hardening、release 或 handoff，也直接执行或调用对应 Specialist。只有结果仍不确定、阶段取舍未决，或过程已经压过 capability progress 时才激活。

## Four Laws

### 1. Outcome Before Process

每轮先问：完成哪个用户可见能力或真实链路证据，才能减少当前最大不确定性？

Spec、Design、测试、Review、观测、Skill、manifest 和 Worktree 只是手段。它们没有产生 capability delta 时，不得被描述为主进展。

### 2. Current Slice, Not Parent Risk

项目整体风险不能自动传递给每个小步骤。按当前 slice 的真实 changed surface 判断：

- 局部可逆改动保持局部流程。
- public API、数据、权限、安全、并发、迁移和不可逆外部副作用才升级。
- 文件数量、Plan checkbox、父任务是 L3，不是升级理由。

### 3. Evidence Proportional to the Claim

只证明本轮声明：

- 局部修复：复现/RED 或替代证据 + focused regression + 必要的 1-3 个真实 smoke。
- Basic Usable：最小真实链路 + 代表场景矩阵 + 关键安全失败。
- Harden：相邻回归、恢复/并发/观测等当前可靠性目标。
- Release/Handoff：完整 acceptance、integration/E2E、real external/fresh consumer 和 rollback。

不要在中间小步提前摊销最终 Release Gate。

### 4. Budget the Process

默认预算：主会话执行、零 Subagent、零新文档、零 workflow manifest。

只有当前 slice 需要独立高风险 Review、并行任务互不共享写状态，或上下文污染会影响结论时才增加 Agent。一个边界默认最多一个 Reviewer 和一次 delta re-review，避免 reviewer 往返成为新的主任务；多个独立安全/数据边界或项目强制政策可以提高预算。非阻塞 finding 进入 deferred backlog。

## Outcome Modes

选择当前模式，不生成复杂分类或策略状态机：

| Mode | Use when | Immediate behavior |
| --- | --- | --- |
| `bypass` | 普通明确任务 | 不使用本 Skill；直接实现和最小验证 |
| `prove` | 新方向、MVP、模型行为尚未证明 | 先做 Minimum Real Slice 和 3-8 个代表场景 |
| `improve` | 链路已通但未达 Basic Usable | 聚类失败，每轮只改一个最高价值 behavioral lever |
| `harden` | Basic Usable 已成立 | 补可靠性、恢复、并发、可观测和回归保护 |

不要因为任务最终要上线，就从第一步直接进入 `harden`。发布决定明确后停止应用本 Skill，直接调用项目交付流程或 `delivery-verification`。

## Procedure

1. 从用户请求和当前证据写出一句 `Current outcome`。
2. 选择 Outcome Mode；若是 `bypass`，停止应用本 Skill，返回普通开发路径。
3. 若尚无有效 acceptance，定义 Basic Usable：通常为 3-8 个代表场景、必须通过的真实链路和不可违反边界；已有标准时直接复用。
4. 写出当前唯一 operational `Top blocker`。其他问题放入 `Deferred`；安全、数据损坏和不可逆风险不得延后。
5. 执行能最快产生 capability delta 的动作。
6. 验证同一信号；结果不好时按 failure cluster 修共性原因，不按单个 badcase 堆补丁。
7. 达到 Basic Usable 后，明确询问或依据用户已给决策进入 `harden`；批准发布后退出本 Skill，不要自动扩展。

只有长期目标需要跨会话恢复时才读取 `references/goal-card.md` 并维护 Goal Card；同一会话或单一小步不要读取或创建。

首次进入 `prove`/`improve`，或无法判断优先级和 Specialist 边界时，读取 `references/scenario-routing.md`；已有有效模式和下一步时不要读取。

真实链路因凭证、外部环境、数据或服务不可用时，记录缺失条件和最近似的代理证据。代理证据只用于诊断，不得签发 Basic Usable；如果真实证据是当前决策所必需，向用户请求访问或外部决策。

## Specialist Boundary

Specialist Skill 只在当前动作真的需要时调用：

- 已复现 bug 且根因未知：`systematic-debugging`。
- 行为可自动化且回归价值高：`test-driven-development` 或项目测试方式。
- 存在真正架构决策：`technical-design`。
- 2 个以上独立并行工作流且收益明确：`agent-orchestration`。
- 正在申请 integration/release/handoff 声明：`delivery-verification`。

不要自动调用完整 Superpowers、workflow-control-plane、SpecFlow、context-grounding、project-harness-init 或 knowledge-promotion。已有 approved Spec/Design/Plan 时直接消费，不重新生成。

## Human Judgment Boundary

仅在以下情况需要人决定：

- 产品目标、取舍或 Basic Usable 标准存在多种合理答案。
- public contract、数据、权限、安全或不可逆生产操作需要授权。
- 两条技术路线证据接近，但时间/质量/成本偏好不同。
- 继续投入的预期收益已经低于成本。

实现细节、测试命令、文件拆分、普通 Review finding 和可恢复失败由 Agent 自主处理。

## Progress Contract

阶段汇报只包含：

```text
Current outcome:
Latest capability delta:
Evidence:
Top blocker:
Next action:
Deferred:
```

不要逐条播报每个命令、Reviewer 往返、manifest 转换或 Worktree 操作。

## Never

- 不用流程完成度替代产品能力完成度。
- 不因 Reviewer 提出新问题自动改变当前优先级。
- 不在 Basic Usable 前建设非必要 dashboard、Skill、全量 eval 或 release harness。
- 不为每个 Task 创建 implementer/reviewer/fixer/re-review 链。
- 不因验证失败两轮就阻塞；只在缺少可执行路径或需要外部决策时暂停。
- 不把“用户没有反对”当作进入 harden/release 的批准。

## Validation

修改本 Skill 后运行：

```sh
python3 scripts/run-outcome-first-eval.py
python3 scripts/run-fresh-agent-route-eval.py --repeat 1
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/adaptive-dev-workflow
```
