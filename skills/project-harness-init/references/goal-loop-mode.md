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
先读取代码、AGENTS.md、docs/architecture.md、当前 spec/technical design/plan/evidence。
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
执行节奏：
1. 复用 approved artifacts，按 Task 局部风险组建连续低风险 batch
2. 每 Task 运行 focused signal；文档/机械改动使用最小 validator
3. batch 内只更新 Plan checkbox 和必要失败记录
4. batch/milestone 统一运行 adjacent regression、diff/scope review、commit 和汇报
5. 只在高风险边界调用独立 reviewer；Critical/Major 修复后最多一次 delta re-review，仍有问题则保留 findings 并进入新的修复 cycle
6. 判断 continue / stop / ask human

必须暂停：
- public API / data model / permission / security posture 需要改变
- acceptance 或 claim ceiling 需要降低
- 验证失败且不存在可执行的诊断/修复路径，需要人工决策或外部能力
- 发现 docs/current truth 冲突会影响方案
- 需要真实凭证、生产副作用、破坏性命令或外部写操作

禁止：
- 不允许用 mock-only evidence 声称真实链路打通
- 不允许没有 fresh verification 就说完成
- 不允许 spec 里没有交付验证
- 不允许高风险任务跳过 approved technical design
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
- Capture each Task's focused signal, then update the durable evidence summary once per batch/milestone.
- Use reviewer agents for new or materially changed design/plan/evidence/security boundaries when risk justifies it.
- Reuse approved artifacts; do not re-review them merely because the next Task started.
- Treat review-pass limits as a bounded Review cycle, not a stop condition; unresolved findings return to repair and the next repaired diff/evidence starts another bounded cycle.
- Promote project lessons only after evidence and scope are clear.
- Prefer scripts/hooks/CI for repeated mechanical checks.

## Bad Loop Behavior

- Continuing implementation after a serious evidence gap without resetting the plan.
- Treating an outdated spec as current truth when code disagrees.
- Expanding scope because the agent found adjacent improvements.
- Asking the user to choose test types that the agent can determine from changed surfaces.
- Marking done because tests pass while acceptance remains unverified.
