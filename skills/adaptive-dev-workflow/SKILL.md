---
name: adaptive-dev-workflow
description: Classify a new or materially changed software-development goal and submit its route decision to workflow-control-plane. Use at task intake when risk, strategy, SpecFlow/OpenSpec, context grounding, handoff, harness, or downstream skill selection must be decided; do not use for ordinary continuation when an active workflow manifest already selects the current stage skill. 当新开发目标进入、范围或风险实质变化、需要选择开发策略/Spec/上下文/交付流程时使用；已有 active workflow 的普通续作直接恢复当前 stage，不重复触发本 skill。
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
- 只要求把 raw intent 生成 draft spec/design、明确禁止实现，且尚未发现不可降级事实时，按当前 artifact 交付风险通常为 `L2 + delivery_shape=doc_only`。不要因为需求名含“workflow/审核流/平台”就提前继承未来实现的 L3 风险；后续 grounding 发现 auth/security/data/cross-service/handoff 再升级。

Non-downgradable facts: `auth`、`security`、`data`、`migration`、`release`、`handoff`。这些事实不允许为了省流程降级为 L0/L1。

`user_constraints.required_spec_system` 和 `required_execution_engine` 只记录用户显式要求。Superpowers 不是 execution engine，不要写入 execution engine；adaptive 只执行 Strategy 当前 stage 已调度的原生 method。能力与默认选择属于 capability report 和 resolver。

## Capability Detection

不要把 capability 判断写进 route decision。由 control plane 脚本生成：

```sh
python3 skills/workflow-control-plane/scripts/detect_capabilities.py --root . --output .agent/runtime/capability-report.json
```

Router 只引用 `capability_report_ref`，不复制 OpenSpec/Superpowers/harness 探测结果。`project_sop=ready` 必须由 capability report 证明存在 instructions、project skill 和 testing contract；只有一个 `AGENTS.md` 不足以降级流程。current truth 不清时，用 `uncertainty=high` 和 `pattern_familiarity=unknown`。

## Procedure

1. Resume first for continuation work. Inspect the canonical single-run path `.agent/runtime/workflow_manifest.json` and multi-run path `.agent/runs/*/workflow_manifest.json` only when the request or repository indicates an interrupted/ongoing run. Resume without re-routing only when exactly one candidate matches the same goal/scope, is `active` or `review_ready`, and passes both workflow and artifact-graph validation:

```sh
python3 skills/workflow-control-plane/scripts/resume_workflow.py <workflow_manifest.json> \
  --goal-id <stable-issue-or-goal-id> --goal-summary "<current goal and scope>"
python3 skills/workflow-control-plane/scripts/validate_artifact_graph.py <workflow_manifest.json>
```

   Continue from `resume.resume_from_stage`; do not regenerate approved, fresh Spec/Design/Plan artifacts. Multiple candidates, stale artifacts, a changed goal, incompatible strategy version, `blocked`, or `closed` means do not auto-resume.
2. If no compatible run exists, inspect only enough context to classify.
3. Emit `route_decision.json` or equivalent JSON object.
4. If classification itself is ambiguous, set `ambiguity.status=ambiguous` with reasons and stop. Missing implementation details, acceptance details, migration design, or rollout plan are not route ambiguity; record `uncertainty=high` and let downstream skills handle them.
5. Ensure capability report exists, then call strategy resolver:

```sh
python3 skills/workflow-control-plane/scripts/resolve_strategy.py route_decision.json --output resolved_strategy.json
```

6. Inspect `process_depth` and `manifest_policy` from the resolver:

   - `direct`: execute the focused change with repo instructions/project SOP and the smallest validator. For behavior changes, use `change-aware-testing` in inner-loop mode instead of repeatedly running the full unit suite. Do not initialize a workflow manifest or load Superpowers.
   - `selective`: initialize workflow state, then load only the exact `required_skills` needed by the active stage.
   - `lifecycle`: initialize workflow state and follow the versioned strategy stages. Load only `skill_plan[current_stage]`; lifecycle depth never implies a full Superpowers workflow or L3 ceremony for every Task.

   For implementation, obey `execution_policy`: parent risk controls final gates; Tasks use local risk. `continuous_batch` runs one focused signal per Task, then adjacent regression, Review, commit, report, and any manifest transition once per batch/milestone.

7. For `manifest_policy=required`, let `workflow-control-plane` initialize workflow state only when step 1 did not resume an existing run:

```sh
python3 skills/workflow-control-plane/scripts/init_workflow.py route_decision.json \
  --resolved-strategy resolved_strategy.json --workflow-id workflow-001 \
  --goal-id <stable-issue-or-goal-id> --goal-summary "<approved goal and scope>" \
  --output workflow_manifest.json
```

8. Report whether the run was resumed or newly routed, selected strategy, process depth, required skills, resolver-derived gates, and remaining ambiguity. Do not claim implementation completion from routing work.

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
- `change-aware-testing`: diff-based test selection, inner-loop/checkpoint/completion cadence, broad-test escalation.
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
- Do not treat Plan checkboxes as mandatory subagent, Review, commit, report, artifact package, or workflow-state boundaries.

## Validation

After modifying this skill, run:

```sh
python3 scripts/run-skill-sandbox-eval.py
python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/adaptive-dev-workflow
```

`run-skill-sandbox-eval.py` 已聚合 workflow、change-aware testing 和 orchestration E2E；不要再重复运行这些 child eval。High-risk changes also require fresh-agent route eval and old/new comparison.
