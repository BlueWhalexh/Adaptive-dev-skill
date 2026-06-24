---
name: specflow
description: Use when raw intent must be turned into a reviewed spec before implementation, including OpenSpec adapter, pack-backed spec generation, lightweight spec generation, acceptance criteria, non-goals, and evidence plan. 当用户要求先写 spec、意图还没变成目标/边界/验收/测试，或 adaptive-dev-workflow 路由到 SpecFlow 时使用。
---

# SpecFlow

SpecFlow 是 spec 生成过程，不是整个项目执行过程。它把 intent 或 Analysis Pack 转换成可审阅的 spec artifact。

## Modes

- `pack-backed-specflow`: L2/L3 或 current truth 不清；输入为 approved Analysis Pack + Context Manifest。
- `lightweight-specflow`: L1/L2 且上下文清楚；允许直接从 intent 写轻量 spec。
- `openspec-adapter`: repo 使用 OpenSpec 时，输出到 OpenSpec proposal/spec/tasks，不生成第二套 product spec。

## Output

产出一个 `spec` artifact，通常包含：

- Intent: 目标、非目标、约束。
- Current Truth: 当前行为和相关入口。
- Proposed Behavior: 改什么，不改什么。
- Acceptance Criteria: 可验证完成条件。
- Compatibility: API、数据、权限、状态、迁移影响。
- Evidence Plan: unit/integration/e2e/real external/fresh consumer 怎么选。
- Change Notes: 需要用户确认的风险和取舍。

## Maker / Checker Gate

L2/L3 SpecFlow 不允许主 agent 自写自批。当 spec 会改变 runtime architecture、delivery contract、public API、data/auth/security model、project priority、implementation engine，或会成为后续 plan/implementation 的主依据时，使用 maker/checker：

1. `spec-writer` pass：把 intent / Analysis Pack 转成 draft spec。
2. `spec-reviewer` pass：独立检查目标、非目标、边界、兼容性、验收标准、Evidence Plan、Stop/Continue 条件和实现可执行性。
3. Main agent：整合 review 结果，列出需要用户确认的决策。

如果没有启动 isolated spec-writer / spec-reviewer，只能把 spec 标记为 `draft` 或 `ready_for_user_review`。只有用户确认或 isolated reviewer 通过后，才能标记为 `ready`；`approved` 必须来自用户或项目既有 spec approval 流程。

## Exit Gate

SpecFlow 不写生产代码，不请求 `dev_done`。它只能把 `spec` 标记为 `draft/ready/approved`，然后回到 adaptive strategy 的 plan 或 implementation stage。
