# Adaptive Dev Skill

Adaptive Dev Skill 是一组面向 Codex / Claude Code / Gemini CLI 的 AI coding workflow skills。它的目标不是把所有流程写进一个大 prompt，而是提供一个小型 workflow runtime：

```text
Admission Router + Workflow Control Plane + Narrow Skills + Verifier-signed Claims + Eval Harness
```

核心判断：

- 轻任务保持快：`direct` 路由不创建 workflow manifest，也不加载 Superpowers。
- 成熟项目复用 SOP：已知模式走 project skill 与固定 validator，只按需调用单个原生 Superpowers skill。
- 高风险任务保持稳：权限、数据、API、迁移、handoff 不允许只靠 happy path 或口头完成。
- 复杂任务先固定 current truth：用 Analysis Pack / Context Manifest 裁剪上下文，再写 spec、technical design 和 plan。
- 开发循环跑增量测试：按 diff 选择受影响测试，task/slice checkpoint 再扩大；全量 suite 留给显式 CI/release/project policy 或 global-impact 变更。
- 交付声明由证据签发：实现者只能 request claim，不能 self-sign validated claim。
- 中文团队的人读项目文档默认中文；文件名、路径、schema keys、命令、validator types、skill names 和工具报错保留英文。

## Skill Suite

| Skill | Responsibility |
| --- | --- |
| `adaptive-dev-workflow` | Admission router：分类任务事实、检测能力、输出 `route_decision.json` |
| `workflow-control-plane` | Strategy resolver、`workflow_manifest.json` 单点写入、状态迁移、resume、artifact graph、claim ceiling |
| `context-grounding` | Analysis Pack、Context Manifest、static/freshness/runtime/sufficiency 验证 |
| `specflow` | 把 intent 或 Analysis Pack 转成 reviewed spec artifact；OpenSpec repo 走 adapter |
| `technical-design` | 在 approved spec 和 implementation plan 之间生成/审查 technical design、设计边界、契约、回滚和 approval |
| `agent-orchestration` | 生成 role roster、context packet、work order 和 structured role result，支持多 Agent 角色隔离协作 |
| `change-aware-testing` | 根据 task diff 选择增量测试，管理 inner-loop/checkpoint/completion cadence 和 broad-test escalation |
| `superpowers-adapter` | 把 approved artifacts 转换给 Superpowers 原生 skills，并把输出映射回 transition request |
| `delivery-verification` | JSON evidence manifest、claim level、fresh consumer / real external / integration 证据验证 |
| `knowledge-promotion` | 把重复 SOP、踩坑、用户反馈沉淀为 learning candidate，再进入项目 skill / AGENTS.md |
| `project-harness-init` | 初始化项目级 harness：AGENTS.md、agent team、Goal Loop Mode、spec/technical design/plan/evidence 结构、项目 skill |

Superpowers 仍然是执行纪律，不被重写。普通 `direct/selective` 默认不加载 Superpowers，Debug 只调用 `systematic-debugging`；L2/L3 lifecycle 也只在当前 stage 调用一个明确的原生 skill，不存在完整 Superpowers 执行链路。

## Control Plane Model

`adaptive-dev-workflow` 只输出 `route_decision.json`。`workflow-control-plane` 根据 route decision 解析 strategy，并且是 `workflow_manifest.json` 的唯一 writer。机器校验 artifact 使用 JSON，Markdown 只做人读说明。

Route decision:

```json
{
  "schema_version": 3,
  "status": "provisional",
  "classification": {
    "risk": "L2",
    "work_intent": "implement",
    "delivery_shape": "feature",
    "scope": "module",
    "uncertainty": "medium",
    "pattern_familiarity": "novel",
    "profiles": ["api"],
    "change_types": ["api_contract"]
  },
  "capability_report_ref": ".agent/runtime/capability-report.json",
  "user_constraints": {
    "network_access": "unknown",
    "production_changes": "forbidden",
    "required_spec_system": null,
    "required_execution_engine": null
  },
  "user_overrides": [],
  "ambiguity": { "status": "clear", "reasons": [] }
}
```

Resolved strategy:

```json
{
  "schema_version": 3,
  "strategy_id": "spec-driven-feature",
  "strategy_version": "1.0",
  "process_depth": "lifecycle",
  "manifest_policy": "required",
  "spec_system": "fallback",
  "execution_engine": "local",
  "required_skills": [],
  "skill_plan": {
    "ground": [],
    "context_pack_if_needed": ["context-grounding"],
    "pack_backed_specflow": ["specflow"],
    "embedded_design": ["technical-design"],
    "plan": ["superpowers:writing-plans"],
    "focused_and_chain_verification": ["delivery-verification"]
  },
  "design_control": {
    "policy": "embedded",
    "review": "self",
    "documentation_topology": "compact",
    "triggers": []
  },
  "gates": {
    "human_design_approval_required": false,
    "isolated_review_required": false,
    "integration_evidence_required": true
  },
  "capability_report_ref": ".agent/runtime/capability-report.json",
  "reason": "L2 implement -> lifecycle; project_sop=missing, pattern=novel"
}
```

Deprecated and intentionally unsupported as canonical artifacts:

- `route_card`
- `evidence_card`
- `artifact_state`
- `delivery_claim`
- `claim_ceiling`

## Classification And Routing

Classification describes task facts in `route_decision.json`:

- `risk`: `L0 | L1 | L2 | L3`
- `work_intent`: `implement | debug | review | design | verify | research | handoff`
- `delivery_shape`: `none | doc_only | local_change | feature | mvp | spike`
- `scope`: `local | module | cross_module | cross_service`
- `uncertainty`: `low | medium | high`
- `pattern_familiarity`: `known | adjacent | novel | unknown`
- `profiles`: `frontend | api | data | auth | security | release | docs | infra`
- `change_types`: `docs | visual | bugfix | feature | api_contract | migration | refactor`

Routing describes execution choices after `workflow-control-plane` resolves the strategy:

- `spec_system`: `none | openspec | repo_native | fallback`
- `process_depth`: `direct | selective | lifecycle`
- `manifest_policy`: `none | required`
- `execution_engine`: `none | local`
- `method_provider`: capability report 中的 `superpowers-native`，仅提供 stage-scoped method skill
- `strategy_id`: selected strategy
- `required_skills`: 当前 stage 才允许加载的 narrow skills
- `skill_plan`: 后续 stage 到 skill 的延迟加载计划

`OpenSpec` 是 spec system。`Superpowers` 不是 execution engine，只是原生 method skill provider。项目 SOP 是否可复用由 capability report 单独证明。

## Strategies

Strategy manifests live in `skills/workflow-control-plane/references/strategies/*.json`.

| Strategy | Depth | Use when |
| --- | --- | --- |
| `quick-change` | direct | L0 docs/mechanical/local work |
| `sop-guided-change` | direct | Ready project SOP 中的 L1 known pattern |
| `focused-change` | selective | 其他 L1 implementation/bugfix；默认不加载 Superpowers |
| `sop-guided-iteration` | selective | Ready project SOP 中的非关键 L2 known/adjacent pattern；使用项目 SOP 与 evidence gate |
| `root-cause-debug` | selective | debug mode，按需只调用 systematic-debugging |
| `spec-driven-feature` | lifecycle/local | 缺少成熟 SOP 或 novel 的 L2 feature |
| `complex-real-slice` | lifecycle | L3、first MVP、handoff、关键边界；按 stage 选择方法 |
| `migration-critical` | lifecycle | data/auth/security/migration/public protocol；按 stage 选择方法 |
| `spike` | selective | bounded research，无 delivery claim |
| `review-only` | direct | review without edits |

The strategy owns stages. `direct` 不创建 manifest；`selective/lifecycle` 由 `workflow-control-plane` 记录 `selected_strategy` 和 `current_stage`。检测到 Superpowers 已安装本身不会改变 process depth。实现阶段由 `change-aware-testing` 运行受影响测试，`delivery-verification` 只负责根据 evidence 签发 claim，两者职责不混合。

Project harness initialization is a local scaffold operation. Later stages may call one exact Superpowers native skill when scheduled, but project implementation remains owned by the workflow runtime.

## Documentation Topology

`design_control.documentation_topology` decides how many document layers the slice needs:

| Topology | Use when | Shape |
| --- | --- | --- |
| `compact` | Small slice: `<5` files, one module, `<3` days | design notes inside spec or plan |
| `single_file_design` | Standalone design is required but one design doc is enough | one canonical technical design artifact |
| `split_design_workspace` | Large feature, multi-module, multi-phase, `>1` week, first MVP, migration, or repo-native split-doc request | spec/acceptance, design overview/parts, plan, ADR |

For OpenSpec, reuse `proposal.md`, `design.md`, and `tasks.md`. For Superpowers fallback, use `docs/superpowers/specs`, `docs/superpowers/designs`, and `docs/superpowers/plans`. For repo-native large slices, use `docs/specs/<feature>/`, `docs/design/<feature>/`, `docs/plans/<feature>.md`, and `docs/adr/`.

## Artifact Graph

Artifacts are independent from workflow state:

```json
{
  "id": "ctx-001",
  "type": "context_manifest",
  "status": "ready",
  "version": 1,
  "producer": "context-grounding",
  "depends_on": ["ap-001"],
  "covers_acceptance": ["AC-1"],
  "path": "docs/context/ctx-001.json"
}
Graph rules:

- `spec` depends on approved `analysis_pack`, unless there is a declared lightweight exception.
- embedded `plan` depends on approved `spec` and declares a stable technical design section.
- standalone `technical_design` depends on approved `spec`, approved `analysis_pack`, and ready/approved `context_manifest`.
- standalone `plan` depends on approved `technical_design`.
- `task_packet` depends on approved `plan` and ready/approved `context_manifest`.
- validated claims require ready/approved `evidence_manifest`.
- stale upstream artifacts force downstream artifacts to become `stale` or `rejected`.

## Claims

Agents request claims; verifiers sign claims.

| Claim | Evidence requirement |
| --- | --- |
| `dev_done` | implementation artifact plus focused passing validator |
| `integration_done` | passing integration/e2e/system/fresh-consumer/real-external evidence |
| `handoff_done` | passing fresh consumer or real external evidence |

Analysis Pack, SpecFlow, and Plan artifacts cannot by themselves request or validate delivery completion.

For L2/L3 SpecFlow that changes runtime architecture, delivery contracts, public API, data/auth/security model, project priority, or implementation engine, use maker/checker separation: a spec writer drafts, an isolated spec reviewer checks, and the user or project approval flow decides whether the spec is approved.

## Context Pack Verification

`context-grounding` splits context validation into four checks:

- Static validation: completeness, minimality, allowed/forbidden paths.
- Freshness validation: repo commit and file hash freshness.
- Runtime audit: actual reads stay inside allowed paths or update the pack first.
- Sufficiency eval: fresh plan agent can plan from Spec + Context Pack without reading the repo.

This is the main guard against complex tasks drifting back into “read everything and improvise”.

## Install

```sh
git clone https://github.com/BlueWhalexh/Adaptive-dev-skill.git
cd Adaptive-dev-skill
for skill in adaptive-dev-workflow workflow-control-plane context-grounding specflow technical-design agent-orchestration change-aware-testing superpowers-adapter delivery-verification knowledge-promotion project-harness-init; do
  mkdir -p "$HOME/.codex/skills/$skill"
  rsync -a "skills/$skill/" "$HOME/.codex/skills/$skill/"
done
```

Optional `.agents` install:

```sh
for skill in adaptive-dev-workflow workflow-control-plane context-grounding specflow technical-design agent-orchestration change-aware-testing superpowers-adapter delivery-verification knowledge-promotion project-harness-init; do
  mkdir -p "$HOME/.agents/skills/$skill"
  rsync -a "skills/$skill/" "$HOME/.agents/skills/$skill/"
done
```

## Use

Direct:

```text
Use $adaptive-dev-workflow.
给导出接口加 format 参数，保持旧客户端兼容，并说明怎么验证。
```

Recommended project `AGENTS.md` line:

```md
For implementation, fix, refactor, design, planning, verification, review, or handoff tasks, use adaptive-dev-workflow to classify task facts and let workflow-control-plane resolve strategy. Direct routes use project SOP and focused validation without a workflow manifest. Selective/lifecycle routes create or update workflow_manifest.json and load only the skills required by the active stage. Use change-aware-testing for diff-based inner-loop tests and expand at checkpoints instead of running the full unit suite after every task. Request verifier-signed claims only through delivery-verification after evidence.
Human-facing docs default to Chinese; keep commands, paths, schema keys, validator types, skill names, and tool errors in English.
```

Complex project start:

```text
Use $project-harness-init.
Initialize this repo for Goal Loop Mode with OpenSpec-first spec routing, Superpowers fallback specs/plans when OpenSpec is absent, docs/evidence, AGENTS.md, agent team roles, and a project-local skill.
```

## Eval And Validation

Deterministic checks:

```sh
PYTHONPYCACHEPREFIX=/private/tmp/adaptive-skill-pycache python3 -m py_compile scripts/*.py skills/*/scripts/*.py
python3 scripts/run-skill-sandbox-eval.py
python3 scripts/run-workflow-e2e-eval.py
python3 scripts/run-agent-orchestration-e2e-eval.py
python3 scripts/run-change-aware-testing-eval.py
python3 scripts/run-handoff-fresh-consumer-eval.py
python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/adaptive-dev-workflow
python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/workflow-control-plane
python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/context-grounding
python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/specflow
python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/technical-design
python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/agent-orchestration
python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/change-aware-testing
python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/superpowers-adapter
python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/delivery-verification
python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/knowledge-promotion
python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/project-harness-init
git diff --check
```

Fresh semantic route eval:

```sh
python3 scripts/run-fresh-agent-route-eval.py --repeat 3 --case tiny-readme-command
python3 scripts/run-fresh-agent-route-eval.py --repeat 3 --case sop-guided-existing-project
python3 scripts/run-fresh-agent-route-eval.py --repeat 3 --case sop-guided-small-fix
python3 scripts/run-fresh-agent-route-eval.py --repeat 3 --case debug-ci
python3 scripts/run-fresh-agent-route-eval.py --repeat 3 --case specflow-intent-to-spec
python3 scripts/run-fresh-agent-route-eval.py --repeat 3 --case complex-frontend-context-pack
python3 scripts/run-fresh-agent-route-eval.py --repeat 3 --case package-handoff
python3 scripts/run-fresh-agent-route-eval.py --repeat 3 --case large-permission-model
python3 scripts/run-fresh-agent-route-eval.py --repeat 3 --case review-only-no-edit
python3 scripts/run-fresh-agent-route-eval.py --repeat 3 --case spike-unknown-architecture
python3 scripts/run-fresh-agent-route-eval.py --repeat 3 --case migration-critical-data
```

The deterministic E2E checks verify JSON schema parsing, artifact graph rules, evidence claim rules, context validation, learning candidate path safety, project harness init, and fresh consumer package handoff. Real external handoff still belongs to each concrete project.

## Repository Layout

```text
skills/
  adaptive-dev-workflow/
    SKILL.md
    schemas/
    scripts/
    references/
      routing-model.md
      strategy-registry.md
      strategies/*.json
  context-grounding/
  specflow/
  technical-design/
  agent-orchestration/
  change-aware-testing/
  delivery-verification/
  knowledge-promotion/
  project-harness-init/
scripts/
evals/
docs/
examples/
```

## Design Sources

- OpenAI Codex skills: concise skills with progressive disclosure.
- OpenAI Codex AGENTS.md: durable project rules should live near the project.
- Superpowers: execution discipline such as TDD, systematic debugging, writing plans, and review.
- OpenSpec: preferred product behavior spec lifecycle when the repo already uses it.

## Contributing

Good changes should improve measured behavior, not just add wording. Compare with old versions or no-skill baselines using seed cases, failure cases, deterministic validators, fresh-agent route evals, and human review notes.
