# Goal Loop Mode

READ when generating `.agent/goal-loop-mode.md` or handing work to another agent that should iterate toward a target instead of doing one-off turns.

## Purpose

Goal Loop Mode lets the human decide direction and drift, while the agent owns iteration within clear boundaries. It prevents one-round delivery by binding the goal to acceptance, evidence, review, and stop conditions.

## Prompt Template

```text
进入 Goal Loop Mode。

目标：
<最终业务/工程目标>

范围：
- In scope:
- Out of scope:

Current Truth：
先读取代码、AGENTS.md、docs/architecture.md、当前 spec/plan/evidence。
如果文档和代码冲突，以代码和 fresh verification 为准，并记录 docs drift。

交付标准：
你不能只完成代码改动。必须给出：
1. acceptance criteria
2. evidence matrix
3. 每项 evidence 的类型：unit / mock / fake / integration / e2e / real external / fresh consumer / manual
4. claim ceiling：Dev Done / Integration Done / Handoff Done
5. 未验证 gap 和风险

Loop 规则：
持续迭代直到所有 acceptance criteria 通过，或者遇到必须人工决策的 blocker。
每轮执行：
1. 选择下一个最小任务
2. 说明预期 evidence
3. 实现或修复
4. 运行 focused validator
5. 更新 evidence
6. 做 diff/scope review
7. 必要时调用 reviewer subagent
8. 判断 continue / stop / ask human

必须暂停：
- public API / data model / permission / security posture 需要改变
- acceptance 或 claim ceiling 需要降低
- 连续两轮验证失败仍无法定位
- 发现 docs/current truth 冲突会影响方案
- 需要真实凭证、生产副作用、破坏性命令或外部写操作

禁止：
- 不允许用 mock-only evidence 声称真实链路打通
- 不允许没有 fresh verification 就说完成
- 不允许 spec 里没有交付验证
- 不允许 reviewer 审自己刚写的实现
- 不允许把项目经验直接写进全局规则；先进入 project learning candidate
```

## Claim Ceiling

| Claim | Minimum evidence |
| --- | --- |
| Dev Done | Focused validator + relevant static/build checks + gaps stated |
| Integration Done | Changed modules or user/system chain pass integration/smoke/E2E |
| Handoff Done | Fresh consumer, tested artifact, onboarding path, or promised real external chain works |

Do not let the final claim exceed the weakest evidence that actually ran.

## Good Loop Behavior

- Keep tasks small enough to review.
- Update evidence after each task, not only at the end.
- Use reviewer agents for design/plan/evidence/security when risk justifies it.
- Promote project lessons only after evidence and scope are clear.
- Prefer scripts/hooks/CI for repeated mechanical checks.

## Bad Loop Behavior

- Continuing implementation after a serious evidence gap without resetting the plan.
- Treating an outdated spec as current truth when code disagrees.
- Expanding scope because the agent found adjacent improvements.
- Asking the user to choose test types that the agent can determine from changed surfaces.
- Marking done because tests pass while acceptance remains unverified.
