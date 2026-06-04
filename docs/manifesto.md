# Manifesto：Less Chaos, Better Quality

Agentic coding 很强，是因为它压缩了实现时间。它也有风险，因为它同样会压缩“误解需求”和“破坏仓库”之间的时间。

答案不是让每个任务都变慢。答案是让 agent 根据真实风险选择合适的流程。

## 原则

使用能保护正确性的最轻流程。

这意味着：

- 对明确、低风险改动快速推进。
- 在需求模糊时先确认再实现。
- 当改动影响多个部件时写计划。
- 对行为变更使用测试或显式 validator。
- 在扩大 scope 前暂停。
- 在声称完成前验证。

## 为什么 agents 会漂移

Agents 很容易漂移，因为它们被优化为继续推进。一个有帮助的 assistant 想要取得进展，而进展经常看起来像“继续写代码”。

但在真实软件工作中，进展也包括：在 acceptance criteria 不清楚时拒绝编码；意识到一个“小改动”其实需要 API 决策；在安全敏感改动变成猜测前停下来。

Adaptive Dev Workflow 给 agent 在这些节点暂停的许可。

## The System, not a prompt

Prompt 说：“小心一点。”

Checklist 说：“把这些都做一遍。”

System 说：“根据当前情况选择正确的 gate。”

Adaptive Dev Workflow 是一个 system，因为它会路由任务：

- Tiny 任务不应该继承仪式。
- 风险任务不应该被当作 quick patch。
- Debugging 应该使用 debugging discipline。
- Completion 应该要求 fresh evidence。

结果不是官僚化。结果是更少隐藏决策。
