# Goal Identity 与 Test Impact Map 增强评测

日期：2026-07-15

## 变更

- 修复 `spec-driven-feature` 的 resolver -> init producer/consumer 契约：初始化阶段尚无 Plan 时允许 embedded design 未绑定，Plan 出现后两个 validator 都强制 `embedded_in`。
- managed workflow 初始化和 v5 migration 写入规范化 `goal_identity`；自动 resume 必须精确匹配 goal id/fingerprint，旧 manifest 只能显式 `--allow-unbound` 人工检查。
- 新增保守的 test-impact-map candidate 生成器，支持 Python、Go、Jest/Vitest；默认不覆盖 canonical map，`--update` 保留人工规则并合并新 trigger globs，`--promote` 才生效。

## 验证

- `run-workflow-e2e-eval.py`：通过。覆盖 spec-driven init、匹配/变更/缺失/tampered Goal Identity、v5 migration identity、embedded binding。
- `run-change-aware-testing-eval.py`：通过。覆盖 candidate generation、focused selection、人工规则保留、同 ID trigger glob merge、已有 map 防覆盖、unsupported project fail-fast。
- `run-skill-sandbox-eval.py`：17 seed cases、42 failure cases，通过。
- fresh-agent route：`tiny-readme-command`、`specflow-intent-to-spec`、`large-permission-model` 各 1 轮，通过。首次运行因 sandbox 无法写 Codex state DB 失败，提升到正常本机权限后通过。
- Skill Creator quick validation：受影响的 3 个 skill 均通过。

## Skill Judge

- 首轮：`107/120`，发现 migration identity、trigger merge、artifact graph 一致性三项问题。
- 修复后：`113/120 (Grade A)`，比上一版 `111/120` 提高 2 分，release blocker 为 0。

## 边界

- 自动生成的 impact map 是候选，不宣称能推导隐式依赖；项目 Review 和 checkpoint fallback 仍是正确性边界。
- Goal fingerprint 对 goal id 和批准的 goal/scope 文本做规范化，不替代产品层面的 scope 判断。
- 本轮没有重跑真实 L3 benchmark；新增逻辑只发生在 init/resume 或 map bootstrap，不进入每 Task 热路径。
