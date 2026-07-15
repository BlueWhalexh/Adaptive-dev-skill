# Goal Loop Review Repair

## 目标

修复“连续两轮 Review 仍有问题就阻塞”的错误语义。Review pass 上限只限制单个 bounded Review cycle，不应终止 Goal Mode。

## 最终行为

- `changes_requested`：workflow 保持 `active`，按 Strategy-owned `repair_stage` 返回修复，并保留 `finding_refs`。
- 达到 `max_review_passes`：重置 pass 计数，修复后的 diff/evidence 开启新 cycle，不产生 `REVIEW_LIMIT_REACHED`。
- Repair stage 完成：必须提交具有新 digest 的 `content_changed` artifact，空修复被拒绝。
- `human_required` / 显式 blocker：仍可进入 `blocked`，不受 repair progress gate 干扰。
- 重复 `transition_id`：返回原始 result status/stage/state。
- Manifest 升至 v6，transition result 升至 v2；受影响 Strategy 升至 v2.1。
- 旧 v5 `REVIEW_LIMIT_REACHED` workflow 迁回 active Review 以重新生成 findings；其他真实 blocker 原样保留。

## 验证

- `python3 scripts/run-workflow-e2e-eval.py`：通过。
- `python3 scripts/run-skill-sandbox-eval.py`：通过，17 seed cases、42 failure cases。
- `python3 skills/workflow-control-plane/scripts/validate_strategy_registry.py`：通过。
- `quick_validate.py skills/workflow-control-plane`：通过。
- `quick_validate.py skills/project-harness-init`：通过。
- `git diff --check`：通过。

E2E 覆盖：两轮 Review 后继续 repair、空 findings、空 repair、不同 findings、幂等重试、repair pending 时人工阻塞、v5→v6 恢复、真实外部 blocker 保留。

## Skill Judge

- 初审：100/120，发现 schema version、幂等、空修复和旧 workflow 迁移问题。
- 修复后复审：106/120，发现 repair progress gate 错误拦截 `human_required`。
- 最终限定复核：111/120，Grade A，无 release blocker。

## 剩余边界

Deterministic E2E 证明控制面语义与负向约束；未运行真实外部服务。Fresh-agent route eval 不针对本次 Review runtime 变更，未重复执行。
