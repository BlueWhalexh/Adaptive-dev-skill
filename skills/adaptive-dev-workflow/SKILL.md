---
name: adaptive-dev-workflow
description: Use when software implementation, fixes, refactors, design, planning, verification, review, workflow routing, OpenSpec/Superpowers selection, SpecFlow, context pack, evidence matrix, verifier-signed claims, or project AI coding harness decisions are needed. 当用户要开发、修复、重构、规划、验证、交付验收、目标模式、上下文包、spec 生成、项目 skill 沉淀或选择 AI coding 工作流时使用。
---

# Adaptive Dev Workflow

你是控制面 router，不是所有工程细节的拥有者。你的职责是把任务拆成稳定的 `classification`、`routing`、`strategy`、`technical design gate`、`artifact graph` 和 `verifier-signed claim`，再按需调用窄 skill。

## Core Model

单次任务使用一个 `workflow_manifest.json` 作为机器可校验契约。Markdown 只做人读说明，不作为 validator 的 canonical input。

人读文档默认使用用户/团队语言。当前全局约定为中文时，spec、plan、evidence、architecture、AGENTS.md、project skill、review notes 等人读文档使用中文为主；保留英文的文件名、JSON/schema 字段、代码标识、命令、错误原文、validator type、skill 名称和必要英文锚点。不要因为模板字段是英文就把整篇文档写成英文。

```json
{
  "workflow_state": "intake | routed | active | blocked | review_ready | closed",
  "classification": {},
  "routing": {},
  "selected_strategy": "focused-change",
  "current_stage": "ground",
  "design_control": {
    "documentation_topology": "compact | single_file_design | split_design_workspace"
  },
  "artifacts": [],
  "claims": { "requested": "none", "validated": [] }
}
```

不要再生成 `route_card`、`evidence_card`、`artifact_state`、`delivery_claim` 或 `claim_ceiling`。

## Classification

`classification` 只描述任务事实，不夹带执行选择：

- `risk`: `L0 | L1 | L2 | L3`
- `mode`: `implement | debug | review | spike | mvp | migration`
- `scope`: `local | module | cross_module | cross_service`
- `uncertainty`: `low | medium | high`
- `profiles`: `frontend | api | data | auth | security | release | docs | delivery | infra`

风险口径：

- `L0`: 文档、拼写、机械编辑、纯视觉/样式微调且无状态/数据/API影响。
- `L1`: 窄范围行为修复或局部实现，影响面清楚。
- `L2`: 新行为、API、UI workflow、1-3 个模块、有边界条件或可见链路。
- `L3`: 跨模块/跨服务、权限/安全/数据/迁移、关键 user workflow、handoff/release、长期 harness。

Special routes: CI/test failure => `risk=L2`, `mode=debug`, `strategy_id=root-cause-debug`; spec/context-only concrete feature => implement/mvp stage with `execution_engine=none`; open-ended research => `mode=spike`.
Migrations in permission/auth/data/state => `risk=L3`, `mode=migration`, `strategy_id=migration-critical`, requiring `context-grounding`, `specflow`, `technical-design`, `delivery-verification`.
Public API/compatibility contract changes such as export `format` => L2 hard design trigger, `strategy_id=complex-real-slice`, `design_control=standalone/independent`, same four required skills.
Project harness / Goal Loop / AGENTS / agent team / project skill init => `risk=L3`, `mode=mvp`, `strategy_id=complex-real-slice`, `execution_engine=local`, requiring `project-harness-init`, `technical-design`, `delivery-verification`, `knowledge-promotion`; add context/spec skills unless OpenSpec already owns them. This local engine only covers scaffold/harness generation. Use `superpowers` later when executing the product implementation plan.

L2/L3 SpecFlow that changes runtime architecture, delivery contract, public API, data/auth/security model, project priority, or implementation engine must use an isolated spec-writer or spec-reviewer pass before marking the spec `ready`. The main agent must not treat its own draft as approved without explicit user confirmation.

## Routing

`routing` 描述执行选择：

- `spec_system`: `none | openspec | repo_native | fallback`
- `execution_engine`: `none | local | superpowers`
- `strategy_id`: 从 `references/strategy-registry.md` 选择。
- `required_skills`: 只列真正需要调用的窄 skill。

`OpenSpec` 和 `Superpowers` 不是 route；它们分别是 `spec_system` 和 `execution_engine`。`debug`、`review`、`mvp`、`migration` 是 `mode`，不是复杂度等级。

## Strategy Selection

先读 `references/routing-model.md`；当 strategy 或 stage 不确定时，再读 `references/strategy-registry.md` 和对应 strategy 文件。

默认映射：

- `quick-change`: `L0`，文档/机械/纯局部，不需要复杂 gate。
- `focused-change`: `L1` 实现或窄 bugfix。
- `root-cause-debug`: `mode=debug` 或原因未知的失败。
- `spec-driven-feature`: `L2` 普通产品/行为/UI 变更，需要 spec、embedded design 与 plan。
- `complex-real-slice`: `L2` hard design trigger 或 `L3` 新项目/复杂 workflow/first MVP/handoff，要求 `technical-design` 和 `delivery-verification`。
- `migration-critical`: `mode=migration`、数据/权限/外部协议/回滚风险，要求 `technical-design`、human review 和 rollback evidence。
- `spike`: `mode=spike` 或高不确定探索，产出 decision/evidence，不直接承诺交付。
- `review-only`: `mode=review` 或用户明确只审不改。

每个 strategy 自己拥有 stages。主控只记录 `selected_strategy` 和 `current_stage`，不要维护全局复杂状态机。

## Narrow Skill Delegation

按需调用，不要一次性加载全部：

- `context-grounding`: current truth 不清、L2/L3、复杂前端/链路、多模态、需要 Context Pack。
- `specflow`: intent 未变成可执行 spec，或用户要求先写 spec。OpenSpec repo 走 adapter，不生成第二套 product spec。
- `technical-design`: approved product spec 之后、implementation planning 之前，生成或审阅目标架构、边界、契约、状态/数据流、文档拓扑、错误恢复、安全、迁移、可观测性、回滚和设计批准。它不写 implementation plan，不写生产代码。
- `delivery-verification`: evidence manifest、claim 验证、handoff/fresh consumer/real external。
- `knowledge-promotion`: 发现可复用 SOP、重复踩坑、多次质量反馈、项目 skill 候选。
- `project-harness-init`: 新项目、first MVP vertical slice、缺 AGENTS.md/spec/evidence/agent team/project skill、或需要 Goal Loop Mode。
- `superpowers:*`: 作为 execution engine 的原生纪律。TDD、debug、writing-plans、requesting-code-review 等不在本 skill 里重写。

For `mode=spike` and review/spec/context-only stages, use `execution_engine=none` until implementation begins.

For high-impact SpecFlow, use maker/checker separation: one pass drafts the spec, another isolated reviewer checks goals, non-goals, acceptance, evidence, compatibility, and implementation executability. If no isolated reviewer is available, mark the spec `draft` or `ready_for_user_review`, not `approved`.

## Technical Design Gate

Product Spec、Technical Design、Implementation Plan 不能混成一份文档：

- `spec`: 做什么、为什么、范围、验收。
- `technical_design`: 目标系统怎么设计，包含架构 delta、边界、契约、数据/控制流、错误恢复、安全、迁移、可观测性和回滚。
- `plan`: 按什么阶段、依赖、文件、验证和 review gate 落地。

按 selected strategy 设置 `design_control`：

- `none`: L0 或 review/spec/context-only，不创建 design artifact。
- `embedded`: L1/L2 普通变更，在 plan 中保留 compact technical-design section，并在 manifest 写 `embedded_in` 和 `section_ref`。
- `standalone`: L2 hard trigger、L3、migration、public API、data/auth/security、状态机、跨服务、外部集成、runtime/operability 或多方案重大取舍，必须有 approved `technical_design` artifact，plan 依赖它。

设置 `design_control.documentation_topology`：

- `compact`: 小切片，约 `<5` 文件、单一模块、`<3` 天；不要拆多层 docs，design notes 放进 spec 或 plan。
- `single_file_design`: 普通 standalone design；一份 canonical technical design 足够。
- `split_design_workspace`: 大切片、Feature 级、多模块、多 phase、`>1` 周、长期 MVP 或迁移；拆成 spec/acceptance、design overview/parts、plan、ADR。

OpenSpec/repo-native 已有 canonical design surface 时复用原路径，例如 OpenSpec `design.md`；不要生成第二套 fallback design。

## Artifact Graph

Artifacts 独立于 `workflow_state`：

```json
{
  "id": "ctx-001",
  "type": "analysis_pack | context_manifest | spec | technical_design | plan | task_packet | evidence_manifest | learning_candidate | implementation | decision_record",
  "status": "missing | draft | ready | approved | stale | rejected",
  "version": 1,
  "producer": "context-grounding",
  "depends_on": [],
  "covers_acceptance": [],
  "path": "..."
}
```

Graph 规则：

- `spec` 依赖 approved `analysis_pack`，除非 manifest 明确 `lightweight_exception: true`。
- standalone `technical_design` 依赖 approved `spec`、approved `analysis_pack` 和 ready/approved `context_manifest`。
- standalone `plan` 依赖 approved `technical_design`；embedded `plan` 依赖 approved `spec` 并声明 `section_ref`。
- `task_packet` 依赖 approved `plan` 和 ready/approved `context_manifest`。
- `validated_claim` 依赖 passing `evidence_manifest`。
- upstream artifact 变 `stale` 时，下游 artifact 传递闭包都必须变 `stale` 或 `rejected`。

写入或修改 manifest 后运行：

```sh
python3 skills/adaptive-dev-workflow/scripts/validate_workflow_manifest.py workflow_manifest.json
python3 skills/adaptive-dev-workflow/scripts/validate_artifact_graph.py workflow_manifest.json
```

## Verifier-Signed Claims

Agent 可以请求 claim，但不能自己签发 validated claim。

```json
{
  "claims": {
    "requested": "none | dev_done | integration_done | handoff_done",
    "validated": [
      {
        "claim": "integration_done",
        "status": "validated | rejected | blocked",
        "verifier": "evidence-manifest-validator",
        "evidence_ids": ["V-001"],
        "signed_at": "2026-06-23T00:00:00Z"
      }
    ]
  }
}
```

Claim 口径：

- `dev_done`: implementation artifact + focused validator。
- `integration_done`: integration/e2e/system evidence。
- `handoff_done`: fresh consumer 或 real external evidence。

During route-only, review-only, spec-only, or analysis-only work, set `claims.requested` to `none`. Analysis Pack、SpecFlow、Plan 只能产生 artifact，不能产生 validated delivery claim。最终回复必须说明 requested claim、validated claim、evidence ids 和 remaining gaps。

## Context Runtime Rule

L2/L3 或复杂任务必须把 Context Pack 分成四类验证：

- Static validation: grounding、completeness、minimality、allowed/forbidden paths。
- Freshness validation: repo commit、file hash、spec version 是否过期。
- Runtime audit: 实际读取文件是否超出 `allowed_paths`，扩展前是否更新 pack。
- Sufficiency eval: fresh Plan Agent 只读 Spec + Context Pack 是否能产出计划。

## Work Cadence

1. Classify task facts.
2. Select routing and strategy.
3. Create or update `workflow_manifest.json` when task不是纯 L0 口头答复。
4. Set `design_control` from selected strategy.
5. Load only required narrow skill/reference.
6. Produce/approve required artifacts: Analysis/Context -> Spec -> Technical Design with chosen documentation topology when required -> Plan -> Task Packet.
7. Execute through selected engine.
8. Run evidence validator and artifact graph validator.
9. Request verifier-signed claim.
10. Capture learning candidate when重复解释、质量不满、SOP 可复用或项目 skill 需要更新。

## Stop Gates

暂停并说明：

- `L3` 没有 approved spec/plan/context manifest，却要开始实现。
- standalone design required but missing approved `technical_design` or independent/human approval.
- 权限、安全、数据、迁移、外部协议、生产依赖变化但没有 evidence plan。
- handoff/release claim 没有 fresh consumer 或 real external verifier。
- Context Pack runtime audit 发现越界读取且未更新 pack。
- 用户连续两次对同类质量问题不满意，需要进入 `knowledge-promotion` 或 project skill 修复。

## Validation
修改本 skill 后至少运行：

```sh
python3 scripts/run-skill-sandbox-eval.py
python3 scripts/run-workflow-e2e-eval.py
python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/adaptive-dev-workflow
```

高风险改动还要运行 fresh-agent route eval 与 old/new comparison。
