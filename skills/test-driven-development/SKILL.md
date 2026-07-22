---
name: test-driven-development
description: Use for automatable behavior changes with meaningful regression risk when failing evidence would materially improve correctness, especially core logic, state transitions, permissions, contracts, and reproducible bugs. Do not use as a mandatory workflow for docs, visual/mechanical edits, simple wiring, low-risk metadata additions, or every assertion in an already covered slice. 当可自动化行为具有明显回归风险且失败证据能提升正确性时使用；不为文档、视觉、机械接线、低风险字段扩展或每个断言机械触发。
---

# Failure-Sensitive TDD

TDD 的目的，是证明 validator 能抓住目标行为，不是为每个文件或断言执行一次仪式。

## Activation Gate

优先使用：

- 可稳定复现的 bug。
- 核心业务逻辑、状态机、权限、安全边界或 public contract。
- 边界条件多、回归代价高、适合自动化的行为变更。

默认不加载：

- 文档、样式、静态 markup、机械重命名和配置接线。
- 低风险 metadata/front matter 字段扩展。
- 已有 focused regression 能直接证明的小修。
- 自动化成本高于当前风险的临时探索或真实 UI 细节。

这些任务仍需 explicit validator，但不要求 RED。

## Behavior-Slice Cycle

1. 定义一个可观察行为切片及其 focused validator。
2. 若旧行为尚无失败证据，以最小测试或复现证明它因预期原因失败。
3. 一次补齐该切片最重要的正常、边界和失败断言；不要为每条 assertion 重启 RED/GREEN。
4. 做最小实现，使同一 focused validator 通过。
5. 自查 diff；仅在跨模块边界变化时升级到 changed-scope validation。

现有失败测试或真实复现已经准确覆盖目标时，直接把它作为 RED，不复制新测试。测试意外 Green、只验证 mock 或因环境错误失败时，不算有效 RED。

## Proportionality

- 一个行为切片通常只需要一轮 RED → GREEN。
- 实现过程中发现新的独立高风险行为，才开启下一轮。
- helper 提取、错误文案、额外编码断言等可在同一切片补充并统一重跑，不逐项播报。
- Release/E2E/real external 属于交付验证，不由本 Skill 自动触发。

## Completion

说明失败证据证明了什么、focused validator 结果和未覆盖风险。不要因为单元测试通过而声明真实浏览器、integration 或 handoff 已完成。
