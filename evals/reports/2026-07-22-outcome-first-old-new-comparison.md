# Outcome-first Old/New Comparison

日期：2026-07-22
Baseline：`5d847e7`

## 设计差异

| Metric | Old | Candidate |
| --- | ---: | ---: |
| `SKILL.md` lines | 169 | 143 |
| 隐式可调用 suite skills | 11 | 1 |
| 默认机器 artifact | `route_decision.json`、capability report；selective/lifecycle 还需 manifest | 0 |
| 默认 control-plane commands | capability detection、resolver、resume/init workflow | 0 |
| Outcome modes | L0-L3 + process depth + strategy | bypass/prove/improve/harden |
| Clear bugfix/docs/review | 仍先经过 admission description | 明确 bypass |
| Clear handoff | L3 + handoff route | 直接 `delivery-verification` |
| Subagent budget | 下游 strategy 决定 | 默认 0；一个边界最多 1 reviewer |

`SKILL.md` 的行数只减少约 15%，但默认副作用从“分类并进入控制面”变为“普通任务零动作”。这是本次减法的主要价值。

## 生产基线

旧流程实际运行轨迹显示：

- Query stable-open 最近 80 turns 出现 79 次 subagent start，其中 41 次 review。
- Import orchestrator 最近 80 turns 出现 427 次 subagent start，其中 183 次 review、89 次 implementation。
- Import hardening 20 个 subagent 中 18 个是 review。
- 无 subagent 的 focused frontend 任务在 9 turns 内完成并得到 browser evidence。

这些数字是对话轨迹事件，不是账单 token。它们证明旧规则在长目标里会被 Plan、manifest、handoff prompt 和项目规则持续放大。

## Candidate Semantic Eval

`evals/outcome-cases.json` 包含 16 个生产抽象场景，正负触发各 8 个：

- bypass：README、前端局部修复、文档事实核对、已知 CAS bug、清晰 hardening、清晰 handoff、权限设计、显式项目 Skill。
- activate：新 Query 链路、Query Basic Usable、process drift、Import Minimum Real Slice、长期目标 hardening 排序、外部证据阻塞、跨会话恢复、发布 go/no-go。

所有 16 个场景至少经过一次 fresh Codex 语义执行。关键场景额外进行两轮稳定性测试：

| Case | Runs | Behavior result |
| --- | ---: | --- |
| known CAS bug | 2 | 2/2 bypass，0 subagent |
| Query Basic Usable | 2 | 2/2 improve，先 failure cluster |
| process drift | 2 | 2/2 prove，真实查询优先 |
| hardening priority | 2 | 2/2 harden，0 subagent |
| external evidence blocked | 2 | 2/2 prove，要求凭证且禁止 mock claim |

稳定性批次的 activation、mode、subagent budget 和 immediate action 为 10/10 语义一致。初始 harness 有 3 次同义词误报（`暂缓`、`禁止` 未被字面 assertion 接受）；扩充 aliases 后两个代表场景重跑 `2/2` 通过。Skill 未为迎合断言增加文字。

## 结论

Candidate 已证明：

- 普通任务不会拉起控制面。
- 长目标仍能守住 Basic Usable 和真实证据。
- clear hardening/handoff 不会因关键词误触发。
- 缺少真实外部条件时不会用 mock 冒充完成。
- 同一关键场景跨运行模式稳定。

尚未证明：在下一次真实 Query/Import 开发中，time-to-first-real-evidence 和最终 Basic Usable pass rate 一定提高。该 outcome 指标必须由后续项目轨迹验证，不能由 route eval 代替。
