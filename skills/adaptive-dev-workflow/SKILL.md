---
name: adaptive-dev-workflow
description: Classify software development tasks and submit route decisions to workflow-control-plane. Use when software implementation, fixes, refactors, design, planning, verification, review, OpenSpec/Superpowers selection, SpecFlow, context pack, delivery handoff, project harness, or AI coding workflow routing is needed. 当用户要开发、修复、重构、规划、验证、交付验收、目标模式、上下文包、spec 生成、项目 skill 沉淀或选择 AI coding 工作流时使用。
---

# Adaptive Dev Workflow

你是 admission router。你的职责是判断“这是什么任务”，输出 `route_decision.json`，然后交给 `workflow-control-plane` 解析策略和维护状态。

不要执行 specialist methodology。不要写 `workflow_manifest.json`。不要复制 SpecFlow、technical-design、context-grounding、delivery-verification 或 Superpowers 的规则。

## Output

输出必须符合：

```sh
skills/workflow-control-plane/schemas/route-decision.schema.json
```

核心结构：

```json
{
  "schema_version": 3,
  "status": "provisional | confirmed",
  "classification": {
    "risk": "L0 | L1 | L2 | L3",
    "work_intent": "implement | debug | review | design | verify | research | handoff",
    "delivery_shape": "none | doc_only | local_change | feature | mvp | spike",
    "scope": "local | module | cross_module | cross_service",
    "uncertainty": "low | medium | high",
    "pattern_familiarity": "known | adjacent | novel | unknown",
    "profiles": ["frontend | api | data | auth | security | release | docs | infra"],
    "change_types": ["docs | visual | bugfix | feature | api_contract | migration | refactor"]
  },
  "capability_report_ref": ".agent/runtime/capability-report.json",
  "user_constraints": {
    "network_access": "allowed | forbidden | unknown",
    "production_changes": "allowed | forbidden | unknown",
    "required_spec_system": "none | openspec | repo_native | fallback | null",
    "required_execution_engine": "none | local | null"
  },
  "user_overrides": [],
  "ambiguity": { "status": "clear | ambiguous", "reasons": [] }
}
```

## Classification

只描述任务事实，不夹带 strategy、skill、spec system 或 execution engine。

- `L0`: 文档、拼写、机械编辑、纯局部视觉/样式，且无状态/数据/API 影响。
- `L1`: 窄范围行为修复或局部实现，影响面清楚。
- `L2`: 新行为、API、UI workflow、1-3 个模块、有边界条件或可见链路。
- `L3`: 跨模块/跨服务、权限/安全/数据/迁移、关键 user workflow、handoff/release、长期 harness。

`pattern_familiarity` 只描述仓库内是否已有可复用模式：

- `known`: 同类实现和项目 SOP 都明确。
- `adjacent`: 有接近模式，但需要小幅设计判断。
- `novel`: 仓库没有对应模式或正在建立新边界。
- `unknown`: 尚未读到足够上下文；不要用它代替 `uncertainty`。

若任务已明确声明 ready project SOP、known pattern、影响点和验收边界，通常使用 `uncertainty=low|medium`；不要仅因尚未打开实现文件就标成 `high`。只有产品边界、兼容契约、安全/数据影响或完成标准仍不清楚时才使用 `high`。

Intent rules:

- CI/test/runtime failure => `work_intent=debug`。
- 用户只要求 review 且不修改 => `work_intent=review`。
- 开放式调研、不承诺实现 => `work_intent=research` 且通常 `delivery_shape=spike`。
- 数据/权限/状态迁移 => `change_types` 包含 `migration`，不要把 migration 写成 work intent。
- 新项目/first MVP/project harness => `delivery_shape=mvp`。
- SDK/package/runtime image/artifact/onboarding 交给新消费者使用，或用户要求“新项目可安装/可 import/可接入” => `work_intent=handoff`。

Non-downgradable facts: `auth`、`security`、`data`、`migration`、`release`、`handoff`。这些事实不允许为了省流程降级为 L0/L1。

`user_constraints.required_spec_system` 和 `required_execution_engine` 只记录用户显式要求。Superpowers 不是 execution engine，用户点名某个原生 skill 时把它作为 method request 交给 control plane/adapter，不要写入 execution engine。能力与默认选择属于 capability report 和 resolver。

## Capability Detection

不要把 capability 判断写进 route decision。由 control plane 脚本生成：

```sh
python3 skills/workflow-control-plane/scripts/detect_capabilities.py --root . --output .agent/runtime/capability-report.json
```

Router 只引用 `capability_report_ref`，不复制 OpenSpec/Superpowers/harness 探测结果。`project_sop=ready` 必须由 capability report 证明存在 instructions、project skill 和 testing contract；只有一个 `AGENTS.md` 不足以降级流程。current truth 不清时，用 `uncertainty=high` 和 `pattern_familiarity=unknown`。

## Procedure

1. Inspect only enough context to classify.
2. Emit `route_decision.json` or equivalent JSON object.
3. If classification itself is ambiguous, set `ambiguity.status=ambiguous` with reasons and stop. Missing implementation details, acceptance details, migration design, or rollout plan are not route ambiguity; record `uncertainty=high` and let downstream skills handle them.
4. Ensure capability report exists, then call strategy resolver:

```sh
python3 skills/workflow-control-plane/scripts/resolve_strategy.py route_decision.json --output resolved_strategy.json
```

5. Inspect `process_depth` and `manifest_policy` from the resolver:

   - `direct`: execute the focused change with repo instructions/project SOP and the smallest validator. Do not initialize a workflow manifest or load Superpowers.
   - `selective`: initialize workflow state, then load only the exact `required_skills` needed by the active stage.
   - `lifecycle`: initialize workflow state and follow the versioned strategy stages. Load only `skill_plan[current_stage]`; lifecycle depth never implies a full Superpowers workflow.

6. For `manifest_policy=required`, let `workflow-control-plane` initialize or update workflow state:

```sh
python3 skills/workflow-control-plane/scripts/init_workflow.py route_decision.json --resolved-strategy resolved_strategy.json --workflow-id workflow-001 --output workflow_manifest.json
```

7. Report selected strategy, process depth, required skills, resolver-derived gates, and remaining ambiguity. Do not claim implementation completion from routing work.

If `context-grounding` or another narrow skill discovers stronger facts, create a route facts delta and let control plane produce the next route revision:

```sh
python3 skills/workflow-control-plane/scripts/apply_route_facts_delta.py route_decision.json route_facts_delta.json --output route_decision.rev2.json
```

## Delegation Map

- `workflow-control-plane`: strategy resolver, manifest, state transition, artifact graph, resume.
- `context-grounding`: Analysis Pack, Context Manifest, freshness/runtime/sufficiency checks.
- `specflow`: Product spec and OpenSpec adapter.
- `technical-design`: architecture/design topology/design review.
- `agent-orchestration`: role roster, work orders, context packets, structured role results.
- `superpowers-adapter`: contract bridge to native Superpowers skills.
- `delivery-verification`: evidence manifest, verifier authority, claim issuance.
- `project-harness-init`: AGENTS/project skill/spec evidence scaffold.
- `knowledge-promotion`: reusable SOP and project skill learning candidates.

## Never

- Do not write or mutate `workflow_manifest.json`; only `workflow-control-plane` writes it.
- Do not duplicate strategy matching policy; use the resolver.
- Do not self-sign or validate claims.
- Do not invent a parallel spec/design system when OpenSpec or repo-native surfaces exist.
- Do not force L0/L1 tasks through full spec/design/E2E flow.
- Do not model Superpowers as an execution engine or full workflow. It is only a provider of explicitly scheduled native method skills.
- Do not create `workflow_manifest.json` for `manifest_policy=none`.
- Do not start a new subagent merely because a different skill is used; isolate only for review, sufficiency eval, security, parallel tasks, or context-contamination control.

## Validation

After modifying this skill, run:

```sh
python3 scripts/run-skill-sandbox-eval.py
python3 scripts/run-workflow-e2e-eval.py
python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/adaptive-dev-workflow
```

High-risk changes also require fresh-agent route eval and old/new comparison.
