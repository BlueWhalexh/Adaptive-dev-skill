# L3 Resume-first Real Project Benchmark

日期：2026-07-15

## 结论

对已经拥有 approved Spec / Technical Design / Plan、ready project SOP 和 active workflow manifest 的 L3 续作，`adaptive-dev-workflow` 不应重新执行 admission。正确入口是：

```text
workflow-control-plane resume
  -> validate manifest / artifact graph
  -> load routing.required_skills[current_stage]
  -> continue execution
```

在相同 Python SDK fixture 上，old、current、none 和优化后的 current-resume 都通过同一个父级 independent verifier。优化后的 current-resume 相对 old 显著减少了可观察流程操作和 token；它没有删除 Spec、Design、系统验证或 handoff gate，只避免重复加载已完成的控制面。

## Fixture 与验收

- 任务：8 个已批准的 L3 SDK 剩余任务，包含 config migration、POSIX permissions、Bearer auth、stdlib HTTP、public API、wheel handoff。
- 不可修改输入：AGENTS、project SOP、approved docs、tests、independent verifier。
- 父级 verifier：unit tests、wheel build、fresh venv install/import、legacy migration、loopback fake HTTP auth、secret scan。
- Evidence level：fake integration + fresh consumer。
- 不包含：real external provider / production call。

Raw reports：

- `/private/tmp/l3-benchmark-real-20260715-v3/report.json`
- `/private/tmp/l3-benchmark-real-20260715-v4-current-resume/report.json`

## 真实执行结果

| Mode | Verifier | Wall time | Input | Uncached input | Output | Commands | Test commands | Review events |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| old (`ab048a7`) | PASS | 256.2s | 713,241 | 47,897 | 8,765 | 14 | 11 | 5 |
| current，重复加载 admission | PASS | 286.5s | 581,735 | 88,423 | 7,978 | 11 | 8 | 4 |
| none，独立无 workflow contract | PASS | 223.3s | 314,967 | 31,319 | 6,474 | 9 | 5 | 1 |
| current-resume，按 stage 懒加载 | PASS | 207.0s | 410,093 | 34,029 | 7,206 | 9 | 7 | 3 |

current-resume 相对 old：

- wall time：-19.2%
- total input：-42.5%
- uncached input：-29.0%
- output：-17.8%
- commands：-35.7%
- test commands：-36.4%
- review events：-40.0%

current-resume 相对 none 仍增加约 30.2% total input、2 次 test command 和 2 次 Review event。这个成本用于 manifest resume、changed-test cadence 和边界 Review；本轮没有证明它在该单一 fixture 上提高 verifier pass rate，因为四组均 PASS。

## 采用的减法

1. Adaptive frontmatter 收窄为新目标 intake / material reroute；active manifest 普通续作不重复触发。
2. 续作先检查 `.agent/runtime/workflow_manifest.json` 或 `.agent/runs/<id>/workflow_manifest.json`，只恢复唯一兼容的 active run。
3. 只加载 `routing.required_skills` 指定的当前 stage skill。
4. `learning_capture` 从 L3 强制交付链移除，改为 close 后按学习信号触发。
5. 缺失 test-impact-map 时直接降级到项目 testing contract，不制造一次无价值失败命令。

## 保留的 Gates

- approved Spec 与完整 acceptance 集合
- standalone Technical Design 与独立 design review
- boundary checkpoint
- system verification
- independent delivery review
- fresh consumer / real external handoff ceiling
- verifier evidence binding 后才能 `closed`

## Integrity 修复

- 每个 acceptance 必须引用 passing validator。
- coverage 必须与 Spec review 已批准的 canonical `acceptance_contract` 完全一致；替代或删减 companion 会被拒绝。
- lifecycle implementation strategy 明确声明 `minimum_close_claim`；`migration-critical` 与 `spec-driven-feature` 无 `integration_done` attestation 不能关闭。
- attestation 绑定 clean Git HEAD、Spec digest、acceptance contract、evidence file digest、registry digest 和 evidence IDs。
- verifier 签入的 evidence type 不仅要在 authority allow-list 内，还必须达到 requested claim 的最低证据等级。
- control plane 在 transition 时重新读取并验证绑定文件；被拒绝的 transition 不再先写坏 manifest。
- 本地 attestation 是 cooperative evidence binding，不宣称密码学 signer identity；不可信执行环境必须使用隔离 CI/外部 signer。

## 回归验证

- deterministic sandbox：17 个 seed cases、42 个 failure cases，通过。
- workflow E2E：包含 managed no-claim close、allowed-but-insufficient evidence、删减 acceptance contract、stale HEAD、dirty product worktree、forged digest/ID 等负例，通过。
- fresh-agent route：`tiny-readme-command`、`package-handoff`、`large-permission-model` 各 1 轮，classification/strategy/claim 均符合预期。
- Skill Creator `quick_validate`：`adaptive-dev-workflow`、`workflow-control-plane`、`delivery-verification`、`change-aware-testing` 均通过。

## Skill Judge

- 改造中间审计：`106/120 (B)`，发现 3 个 release blocker。
- 修复后复核：`111/120`，达到旧版本基线，3 个 blocker 均消除，release blocker 为 0。
- 未为追分增加运行时阶段；剩余扣分主要来自单 fixture/单次 benchmark、local cooperative attestation 信任模型，以及尚未单独覆盖的 `spec-driven-feature resolver -> manifest init` producer-consumer 组合。

## 作废运行

- v1：verifier 在 src-layout unit tests 前缺少 `PYTHONPATH=src`，所有组会发生环境性假失败。
- v2：Skill Judge 发现 attestation binding 和 none baseline 隔离缺陷，候选尚不可发布。

以上运行不进入性能比较。

## 局限

- 每种 mode 只有一次真实执行，不能证明统计显著性或跨模型稳定性。
- Codex 内层 sandbox 禁止 loopback bind；Agent 的内部 verifier 因此 blocked。父级 runner 在外层重新执行并 PASS。
- 当前结论只支持“续作流程更轻且本 fixture 质量未回退”，不支持“所有 L3 都更快”或“优于无 Skill 的普遍质量收益”。
