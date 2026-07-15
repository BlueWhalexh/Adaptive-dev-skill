# Continuous Batch Subtractive Refactor Eval

日期：2026-07-15

## 结论

本次重构将复杂任务的默认执行单位从“每个 Plan Task 一套执行/Review/验证仪式”改为：

```text
父级风险控制最终 gate
→ Task 按 changed surface 判断局部风险
→ 连续低风险 Task 组成 batch
→ 每 Task focused signal
→ batch/milestone 才做 adjacent regression、Review、commit、report
→ 高风险 boundary 使用机器化 stage gate
```

没有恢复完整 Superpowers workflow。Registry 仍可按 stage 使用 `writing-plans`、`systematic-debugging` 等窄方法；默认实现阶段不再调度 `executing-plans`、`subagent-driven-development`、`requesting-code-review` 或 `verification-before-completion`。

## Old / New

| Surface | Before | Candidate |
| --- | --- | --- |
| L2/L3 implementation unit | Plan Task / slice，容易被执行为逐 Task ceremony | `continuous_batch` |
| Task exit | focused + adjacent/full expansion + Review/commit/report 容易叠加 | focused signal only |
| Checkpoint | task/slice | batch/milestone |
| Complex/Migration default heavyweight method refs | 9 refs（含 executing/review/verification/TDD） | 0 refs；仅保留 stage-scoped planning/debug methods |
| Review loop | 文字约束，无 runtime 上限 | `review_result` + producer/actor/evidence/maker-checker + max 2；未解决 Major/Critical 自动 blocked |
| High-risk stage | stage 名存在但可空 evidence 推进 | Registry `stage_gates` 强制 allowed producer、minimum evidence、review mode |
| Strategy policy schema | 三处复制 | `execution-policy.schema.json` canonical contract |
| In-flight v1 manifest | 2.0 后不可恢复 | unsigned 原子迁移；signed claim 拒绝重写并要求 re-verify |
| Specialist dispatch | 一度尝试 implicit=false，但无 programmatic dispatcher | 恢复 implicit=true；仍由 active-stage `required_skills` 控制 progressive disclosure |

## Sandbox Results

Deterministic suite：

- 11 个 skill `quick_validate`：pass。
- Python `py_compile`：pass。
- `run-skill-sandbox-eval.py`：pass，17 seed cases，42 failure cases。
- Workflow E2E：route/resolver/manifest/artifact graph/claim/context/handoff 均 pass。
- 新增 runtime negatives：unauthorized/self review、空 high-risk evidence、unresolved Major 第二轮、legacy heavyweight method、unbounded review、signed migration、in-place migration failure 均被拒绝。
- `run-change-aware-testing-eval.py`：pass。
- `run-agent-orchestration-e2e-eval.py`：pass。
- `git diff --check`：pass。

Fresh Codex route eval：

- `tiny-readme-command`：`L0 / quick-change`，pass。
- `package-handoff`：`L3 / complex-real-slice`，pass。
- `migration-critical-data`：`L3 / migration-critical`，pass；fixture 接受 `module|cross_module`，因为两者不改变高风险 Strategy。
- `specflow-intent-to-spec`：首次暴露 draft spec 被过早判 L3；补充“当前 artifact 风险”规则后为 `L2 / spec-driven-feature`，pass。

Fresh execution behavior simulation：

- 已批准 spec/design/plan + 5 个同模块低风险 Task：fresh agent 推导为一个 batch，每 Task focused signal，batch 一次 regression/Review/commit/report，不逐 Task 建 subagent/work order。
- L3 migration 8 Tasks：fresh agent将辅助 Task 合并，把 schema、migration execution、migrated-state verification、rollback、claim 分成 boundary milestones；没有丢 negative/rollback/system evidence。

## Skill Judge History

第一轮：`87/120`。发现 v1 manifest 不可恢复、高风险 gate 减过头、Review 上限不可执行、负向测试只声明不执行等问题。

第二轮：`89/120`。确认前一批修复，但发现 specialist implicit=false 会切断自动链路、review authority 可伪造、high-risk stage 可空 evidence 推进、未实现的 explicit Superpowers override 被写进 contract。

第二轮 delta：`102/120`。上述四项已解决；剩余一个 High 是部分 L2 managed review stage 未配置 gate，另有一处 adaptive method-request 残留。

对应修复：

- 恢复 specialist implicit invocation。
- 新增 Strategy-owned `stage_gates`。
- Review transition 绑定 producer skill、actor id、evidence refs、reviewed producer ids 和 finding refs。
- 删除 adaptive 对 explicit Superpowers method override 的未实现承诺。
- failure case status 区分 deterministic/runtime/fresh behavior eval，不再一律写 `covered`。
- manifest migration 改为临时文件验证后 `os.replace`。
- 为 `focused-change.self_review`、`sop-guided-iteration.independent_review`、`spec-driven-feature.spec_review/review` 补齐 gate；Registry 会拒绝任何新的 non-direct review stage 漏 gate。
- 删除 adaptive method-request 残留，并增加 empty L2 review transition 与 ungated Registry 负向测试。

最终未再开启第三轮完整 Judge，避免 Review 自身失控；以一次定向 E2E delta 验证收尾。当前没有已知 Critical/High，残余风险是 reviewer identity 仍属于本地 contract 信任模型，不是外部签名身份系统。

## External Evidence

- [GPT-5.6 release](https://openai.com/index/gpt-5-6/) 表明新模型在 long-horizon coding 与工具协调上更强，并强调按需求使用更高 compute；这支持“默认轻、困难边界再升级”，而不是每个 Task 固定最高仪式。
- [Harness engineering](https://openai.com/index/harness-engineering/) 强调短 AGENTS 作为地图、中央约束与局部自治、最小 blocking merge gates；这支持 Registry/stage gate 中央化，同时让 batch 内 agent 自主执行。
- [Codex long-running work whitepaper](https://cdn.openai.com/pdf/8a9f00cf-d379-4e20-b06f-dd7ba5196a11/OAI_WhitePaper_Codex-maxxing26.pdf) 强调目标应具有可验证 success criteria；因此本次减掉的是重复流程，不是 acceptance/evidence/claim gate。
- Reddit 的 [GPT-5.6 practical tips](https://www.reddit.com/r/codex/comments/1uw2i2l/practical_tips_after_using_gpt56_for_a_day/) 与 [token cost discussion](https://www.reddit.com/r/codex/comments/1uti25e/gpt_56_sol_is_a_token_furnace_and_im_on_the_200/) 仅作为早期用户体验：skill 过度触发和高 effort 成本值得关注，但不作为规范性依据。

## Remaining Evidence Gap

本次证明了 route、runtime gate 和 fresh-agent 行为方向，尚未得到真实生产项目的 wall-clock、token、tool-call、返工次数 old/new 同任务对照。下一步应在一个有 READY spec/design/plan 的真实项目中记录 3 个连续 batch，再与旧版逐 Task 执行历史比较。
