# Scenario Routing

## Bypass

普通 bugfix、明确功能、文档、样式、纯 Review 和局部重构不需要 Outcome Guard。直接读取必要上下文、修改、运行与声明相称的验证。

## Prove

适用于新 AI/LLM/Agent/检索链路或未知产品方向。

1. 固定目标与不可违反边界。
2. 建立 Minimum Real Slice。
3. 选择 3-8 个代表场景，包括至少一个关键失败边界。
4. 先运行真实链路，再决定是否值得 harden。

允许 lightweight intent/design notes；禁止为了未来发布先建设完整状态机、全量观测和多层 Review。

## Improve

适用于链路可运行但质量不稳定。

1. 跑小型固定矩阵。
2. 按共同根因聚类，不按单题修补。
3. 每轮改变一个 behavioral lever。
4. 重跑受影响矩阵并保留 old/new 结果。
5. 达到 Basic Usable 即停止扩张。

## Harden

只有 Basic Usable 已有证据时进入。按已观察到的风险补恢复、幂等、并发、可观测、性能和回归保护。不要为假设风险建设没有消费方的机制。

## Exit To Delivery

发布取舍批准后退出 Outcome Guard。准备合并、部署或交接时，再由项目交付流程或 `delivery-verification` 集中执行完整 acceptance、系统/E2E、real external/fresh consumer、rollback 和独立 Review。

## Priority Order

```text
P0 core path cannot run / security or data hazard
P1 representative user scenario fails
P2 minimum observability required to diagnose P1
P3 reliability and maintainability
P4 process, report, Skill, and artifact polish
```

P2-P4 不得阻塞 P0/P1，除非不处理就无法安全运行或无法判断结果。
