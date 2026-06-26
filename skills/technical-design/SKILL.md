---
name: technical-design
description: Use after an approved product spec and before implementation planning when a task needs none/embedded/standalone technical design, documentation topology, split design workspace, architecture boundaries, API/event/data/state contracts, security/migration/rollback/observability decisions, OpenSpec design.md reuse, design review, or design approval. 当 spec 已确认但还需要技术设计、文档分层、拆分 design workspace、架构边界、契约、状态/数据流、安全迁移回滚、可观测性、设计审查或 adaptive-dev-workflow 路由到 technical-design 时使用。
---

# Technical Design

你负责 Product Spec 之后、Implementation Plan 之前的技术设计。不要重写产品目标，不要拆 implementation task DAG，不要写生产代码。

## Inputs

必须先有：

- approved `spec` artifact，或用户明确要求 review existing design。
- `design_control.policy`: `none | embedded | standalone`。
- `design_control.documentation_topology`: `compact | single_file_design | split_design_workspace`。
- `design_control.review`: `none | self | independent | human`。
- L2/L3 standalone 需要 fresh Analysis Pack / Context Manifest 或 repo-native current-truth artifact。

缺少 current truth 时，回到 `context-grounding`；缺少 product goal/acceptance 时，回到 `specflow`。

## Output Modes

- `none`: 不创建 design artifact；topology 必须是 `compact`，可输出 reason。
- `embedded`: 在 implementation plan 中加入 compact `Technical Design` section，并通过 `workflow-control-plane` transition request 返回 `embedded_in` 和 `section_ref`。
- `standalone`: 生成或更新 canonical `technical_design` artifact；通过 transition request 让 manifest 的 `design_control.artifact_id` 指向它。大切片使用 `split_design_workspace`。

OpenSpec/repo-native/Kiro-like 项目已有 canonical design surface 时复用原路径。OpenSpec 默认复用 `openspec/changes/<change>/design.md`。不要为了 fallback 再生成第二套设计文档。

## Workflow

1. Verify inputs: approved spec、fresh current truth、strategy policy、review policy。
2. Identify hard triggers: API/event/data/auth/security/state/migration/concurrency/external/runtime/multi-option。
3. Select documentation topology using `references/documentation-topology.md`。
4. Select canonical design path using `references/spec-system-adapters.md`。
5. Write current-to-target architecture delta, boundaries, contracts, flows, failure/recovery, security, migration, observability, rollback。
6. Map acceptance -> design mechanism -> planned evidence。
7. Record open decisions and stop conditions. Blocking decisions prevent `approved` status。
8. Apply maker/checker: independent reviewer cannot be the producer; human review is required when policy says `human`。
9. Return only approved/ready design artifact metadata to adaptive; do not request `dev_done`。

## Required References

- Read `references/design-contract.md` before generating a standalone design.
- Read `references/documentation-topology.md` when topology is not `compact`, when standalone design is required, or when the slice size is unclear.
- Read `references/design-review.md` before approving or reviewing a design.
- Read `references/spec-system-adapters.md` when choosing a canonical design path.

## Exit Gate

Before handing off to `writing-plans`, the design must state what it proves, which documentation topology was chosen, and what remains undecided. For standalone design, the artifact must be approved and referenced by `design_control.artifact_id`; for embedded design, the plan must expose a stable `section_ref`.
