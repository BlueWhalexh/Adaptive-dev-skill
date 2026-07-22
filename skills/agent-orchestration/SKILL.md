---
name: agent-orchestration
description: Coordinate a small role-based Agent Team with minimal context packets, bounded parallelism, and explicit workspace ownership. Use when two or more independent writers can run safely, three or more roles/sessions need coordinated handoffs, or the user explicitly asks for an orchestrator without manually moving context. Do not use for an ordinary single implementation, one isolated reviewer, or one maker followed by one checker. 当两个独立 writer、三个以上角色/会话或用户明确要求 orchestrator 时使用；普通任务和单 maker + 单 checker 不触发。
---

# Agent Orchestration

你管理的是逻辑 Agent Team，不是永久会话池，也不是 workflow control plane。

稳定复用角色定义，按需创建执行实例。Orchestrator 负责目标、ownership、上下文投影、进度和集成；Maker、Reviewer、Verifier 只完成自己的 work order。不要把完整聊天记录交给所有角色。

## Activation Gate

仅在以下任一情况成立时使用：

- 两个以上独立 writer 可以并行，且不共享文件或写状态。
- Spec/Design/实现/验证需要多个角色跨会话交接。
- 用户明确要求 Agent Team、独立会话或 orchestrator 代替人工搬运上下文。
- 单个上下文已经污染，需要由独立 Agent 重新判断多个 artifact。

以下情况不使用：普通单任务、只有一个独立 Reviewer、强顺序依赖、共享文件频繁修改、并行收益低于准备和合并成本。

## Team Model

角色是稳定契约，执行 Agent 是临时 carrier：

| Role | Owns | Must not own |
| --- | --- | --- |
| Orchestrator | outcome、任务边界、context packet、集成、预算 | 代替角色产出并自批 |
| Maker | 一个明确 artifact 或文件域 | 批准自己的高风险产出 |
| Reviewer | acceptance、diff、边界、副作用检查 | 写实现代码、扩大 scope |
| Verifier | 运行独立 evidence、判断 claim 支持度 | 用 maker 总结替代命令结果 |

领域角色可以替换 Maker，例如 Spec Writer、Technical Designer、Frontend Writer。不要因为角色表存在就启动所有角色。

## Default Budget

- 一个 milestone 默认 `1 writer + 1 optional reviewer`。
- 最多同时运行 3 个 writer；增加前必须证明文件域和写状态独立。
- 一个风险边界默认一次 Review；Blocking/High 修复后一次 delta re-review。
- Verifier 只在证据必须与实现上下文隔离，或申请 integration/release/handoff claim 时独立创建。
- 不创建常驻 Agent 来“节省上下文”。运行时是否复用缓存由宿主决定；Skill 只保证每次投影最小必要上下文。

## Context Packet

每个 work order 只包含：

```text
objective
acceptance_and_non_goals
owned_paths_or_artifacts
read_only_context_refs
known_decisions
validator
expected_result
forbidden_scope
```

Reviewer 额外接收 diff 和 evidence，但不接收完整实现对话。缺少事实时先向 Orchestrator 请求一个明确 context delta，不自行遍历无关仓库。

## Workspace Policy

- 只读 Reviewer/Verifier 使用当前仓库视图，不创建 worktree。
- 并发 writer 必须有互斥文件域；需要写代码时使用独立 worktree 或宿主提供的隔离 workspace。
- 单 writer 顺序实现可以在干净目标分支就地执行。
- Orchestrator 是 worktree lifecycle owner：记录路径和分支，在合并、放弃或过期后安全回收；含未合并改动的 worktree 不自动删除。

## Procedure

1. 写一句 shared outcome 和当前 acceptance。
2. 判断是单 reviewer、顺序 handoff，还是值得并行的多个 writer。
3. 为每个真正需要的角色分配唯一 objective 和 ownership。
4. 投影最小 context packet；不复制整个聊天和完整仓库说明。
5. 启动所需 carrier，并限制它只返回 result、evidence、blocker 和 context request。
6. Orchestrator 校验输出、处理冲突并运行一次集成验证。
7. 只汇报 capability delta、blocking findings、剩余风险和下一步；不汇报每个 Agent 的过程日志。

普通单 reviewer 可以直接执行步骤 4-6，不创建 roster、JSON manifest 或 orchestration artifact。

## Optional Machine Contracts

跨进程 runner 确实需要机器交接时，才使用本 Skill 的 `schemas/` 和 `scripts/` 创建 `agent_roster.json`、`context_packet.json`、`work_order.json`、`work_result.json`。这些 artifact 是 carrier contract，不要求 `workflow_manifest.json` 或 `workflow-control-plane`。

## Conditional References

- 分配领域角色时读 `references/role-contracts.md`。
- 生成跨会话 packet 时读 `references/context-projection.md`。
- 选择顺序/并行、carrier 或 worktree 时读 `references/orchestration-patterns.md`。
- 普通单 checker 不读这些 references，直接使用 Reviewer 最小输入。

## Never

- 不让 Maker 批准自己的 required Review。
- 不为每个 Task 创建 implementer/reviewer/fixer/re-review 链。
- 不把“不同角色”误解为“必须创建不同 Agent”。
- 不让多个 writer 并发修改共享文件、schema 或数据库状态。
- 不把完整聊天历史 fork 给所有 Agent。
- 不让 Reviewer 的 Minor finding 自动抢占当前 outcome。
- 不让只读角色创建永久分支或 worktree。

## Validation

```sh
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/agent-orchestration
python3 scripts/run-agent-orchestration-e2e-eval.py
python3 scripts/run-fresh-agent-team-trigger-eval.py
```
