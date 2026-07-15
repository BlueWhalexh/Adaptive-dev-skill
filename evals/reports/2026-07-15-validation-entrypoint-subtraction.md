# Validation Entrypoint Subtraction

日期：2026-07-15

## 问题

顶层 `run-skill-sandbox-eval.py` 已执行 workflow、change-aware testing、agent orchestration；workflow E2E 内又执行 handoff fresh consumer。但部分 skill 和 Phase 2 runner 在聚合测试之后再次调用相同 child eval，增加时间而不增加覆盖。

## 减法

- Adaptive skill maintenance：`sandbox + workflow E2E + quick_validate` 改为 `sandbox + quick_validate`。
- Agent Orchestration 局部修改：保留 `focused E2E + quick_validate`，不递归调用 suite sandbox。
- Phase 2 deterministic：只调用一次 sandbox；fresh-agent semantic route eval 仍作为独立层保留。
- Sandbox 增加 anti-duplication 负例，防止三个入口重新引入已聚合的 child eval。

## 效果

- Phase 2 deterministic 顶层命令：3 -> 1。
- Workflow E2E 调用：2 -> 1。
- Handoff fresh consumer 调用：3 -> 1。
- 本机本轮观测：聚合 sandbox 约 `9.1s`；被删除的重复 workflow/handoff 约 `6.3s + 1.9s`，估算 deterministic 路径约 `17.3s -> 9.1s`。
- 覆盖不变：sandbox 输出确认 workflow、change-aware testing、agent orchestration、handoff 均通过。

## 审计

- Skill Judge：`113/120`，不低于前一版本。
- Release blocker：0。
- 未删除 fresh-agent semantic eval、负向测试、claim gate 或真实 fresh-consumer 验证。

## 后续候选

`focused-change`、`root-cause-debug`、`sop-guided-iteration` 仍包含若干仅表达方法步骤的 stage。可以通过 stage batching 或带迁移映射的 Strategy major change 减少 transition，但必须先做在途 manifest 兼容设计和 old/new outcome eval；本轮不直接删除，以免用更少步骤换来更弱结果。
