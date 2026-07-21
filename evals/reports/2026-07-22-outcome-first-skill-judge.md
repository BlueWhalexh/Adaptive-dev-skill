# Outcome-first Adaptive Skill Judge

日期：2026-07-22

## 结果

| 版本 | 分数 | 等级 | 结论 |
| --- | ---: | --- | --- |
| 第一版 Outcome Guard | 104/120 | B | 方向正确；触发冲突、引用加载和外部证据降级仍有缺口 |
| 修复后 | 112/120 | A | 六项缺陷关闭，无阻断项 |

最终维度：

| Dimension | Score |
| --- | ---: |
| D1 Knowledge Delta | 18/20 |
| D2 Mindset + Procedures | 14/15 |
| D3 Anti-Pattern Quality | 13/15 |
| D4 Specification Compliance | 15/15 |
| D5 Progressive Disclosure | 15/15 |
| D6 Freedom Calibration | 14/15 |
| D7 Pattern Recognition | 9/10 |
| D8 Practical Usability | 14/15 |

## 修复项

1. 正负触发冲突改为负条件优先；清晰 hardening/handoff 直接执行。
2. Goal Card 和 Scenario Routing 增加明确的读取与不读取条件。
3. 外部真实证据不可用时，proxy 只用于诊断，不得声明 Basic Usable。
4. `bypass` 改为停止应用 Outcome Guard，而非含混的“停止加载”。
5. validation 路径改用 `${CODEX_HOME:-$HOME/.codex}`。
6. 删除空心 `release` mode；批准发布后退出 Guard，由 delivery flow 接管。

## 有意省略

Judge 明确认定以下缺失不是缺陷：通用 lifecycle orchestration、默认 manifest、强制多 Agent、全量 Spec/TDD/E2E、完整 release 状态。这些内容与窄 Outcome Guard 的定位冲突。

Judge 通过独立 `codex exec --ephemeral --sandbox read-only` 会话运行；最终报告保存在本次评测输出，并由本摘要记录核心分数与结论。
