# Skill-Judge Report: Adaptive Dev Skill Control Plane Suite

Date: 2026-06-24

Scope:

- `adaptive-dev-workflow`
- `context-grounding`
- `specflow`
- `technical-design`
- `delivery-verification`
- `knowledge-promotion`
- `project-harness-init`

## Summary

- **Total Score**: 111/120
- **Grade**: A
- **Pattern**: Process + Navigation hybrid
- **Knowledge Ratio**: E:A:R ~= 78:17:5
- **Verdict**: 这套 skill 已从单一流程提示词升级为可验证的 AI coding 控制面，适合作为项目级开发路由和高风险交付护栏；主要剩余优化点是更强的 anti-pattern 压缩、fresh-agent eval 成本和更系统的真实项目 holdout。

## What This Skill Suite Is

当前套件不是一个“大而全开发 prompt”，而是一个小型控制面：

```text
Router
-> Strategy Registry
-> Context Grounding
-> SpecFlow / OpenSpec adapter
-> Technical Design Gate
-> Superpowers execution discipline
-> Delivery Verification
-> Knowledge Promotion
```

核心设计：

- `adaptive-dev-workflow` 只负责 classification、routing、strategy selection、artifact graph、claim request，不重写 TDD/debug/planning/review 细节。
- `OpenSpec` 是 `spec_system`，不是 route。
- `Superpowers` 是 `execution_engine`，不是 route。
- `project-harness-init` 是 local scaffold engine；后续产品实现计划执行时才进入 Superpowers。
- L0/L1 保持轻量；L2/L3、debug、migration、handoff、auth/data/security/API/state-machine 进入对应窄 skill。
- Product Spec、Technical Design、Implementation Plan 明确分层，不混成一份文档。
- Agent 只能 request claim；validated claim 必须由 evidence verifier 签发。
- 机器校验 artifact 使用 JSON/schema；Markdown 只做人读说明。
- 人读文档默认中文；字段、路径、命令、validator type、skill 名称和错误原文保留英文。

## Dimension Scores

| Dimension | Score | Max | Notes |
| --- | ---: | ---: | --- |
| D1: Knowledge Delta | 18 | 20 | 控制面、artifact graph、claim signing、context runtime audit、project harness learning 都是高价值专家知识；少量 routing reminders 属于 activation。 |
| D2: Mindset + Procedures | 14 | 15 | 有清晰的工程判断框架，也有 validator/schema/script；仍可继续压缩常识性 workflow 句子。 |
| D3: Anti-Pattern Quality | 13 | 15 | Stop gates、deprecated artifacts、no mock-as-real、no duplicate spec system 都具体；窄 skill 可补更多 `NEVER ... because ...`。 |
| D4: Specification Compliance | 15 | 15 | frontmatter 合法，description 覆盖中英文触发词和关键场景。 |
| D5: Progressive Disclosure | 14 | 15 | 主 skill 219 行，重内容拆到 references/scripts/schemas；可再补少量 Do NOT load guidance。 |
| D6: Freedom Calibration | 14 | 15 | JSON/schema/claim/evidence 低自由度，routing/strategy 保留判断空间；project harness engine 已收紧为 local。 |
| D7: Pattern Recognition | 9 | 10 | 符合 Process + Navigation hybrid；不是纯 Tool skill。 |
| D8: Practical Usability | 14 | 15 | 有 deterministic eval、fresh-agent eval、real project scaffold validation；真实业务 handoff 仍需在具体项目内验证。 |

## Critical Issues

No release-blocking issue found.

重要但非阻塞的问题：

- Fresh-agent semantic eval 耗时高，当前没有并行执行和 token/time/tool-call 自动采集。
- Full fresh-agent run 会暴露合理字段波动；seed 需要区分 hard assertions 与 acceptable ranges。
- `technical-design` 和 `knowledge-promotion` 可继续增强 anti-pattern list，减少 reviewer 主观解释空间。
- Real external handoff 仍不是本仓库能证明的事情，必须在具体 SDK/runtime/project 中用 fresh consumer 或 real external evidence 验证。

## Validation Evidence

Deterministic checks:

```text
PASS env PYTHONPYCACHEPREFIX=/private/tmp/adaptive-skill-pycache python3 -m py_compile scripts/*.py skills/*/scripts/*.py
PASS python3 scripts/run-skill-sandbox-eval.py
PASS python3 scripts/run-workflow-e2e-eval.py
PASS python3 scripts/run-handoff-fresh-consumer-eval.py
PASS python3 scripts/run-phase2-eval.py --skip-fresh
PASS quick_validate.py for all 7 skill packages
```

Fresh-agent semantic route eval:

```text
Initial full run after harness engine clarification:
- 12/14 cases passed directly.
- medium-api-contract failed only on non-core acceptable fields: uncertainty low|medium and scope module|cross_module.
- large-permission-model failed because seed had been accidentally changed to local; actual output correctly used superpowers.

After seed correction:
- PASS medium-api-contract: 3/3
- PASS large-permission-model: 3/3

Earlier harness-specific rerun:
- PASS project-harness-init-goal-loop: 3/3
- PASS openspec-project-harness-init: 3/3
```

Effective route findings:

- High-risk strategy recall: pass for permission migration, data migration, package handoff, complex context pack, project harness init, and OpenSpec harness init.
- Completion overclaim: 0 observed; route-only cases consistently request `claims.requested=none`.
- L0/L1 over-process: 0 observed for README edit, CSS micro-change, and review-only cases.
- Wrong downstream skill: 0 observed after seed correction.

Real project scaffold validation:

```text
PASS Superpowers fallback real-repo copy
- root: /private/tmp/adaptive-real-project-check-20260624
- feature: agent-sdk-mvp
- project skill: adaptive-dev-project
- spec system: superpowers
- produced AGENTS.md, .agent/agents.md, .agent/goal-loop-mode.md, project skill,
  docs/architecture.md, docs/superpowers/specs, docs/superpowers/designs,
  docs/superpowers/plans, and docs/evidence.

PASS OpenSpec marker real-repo copy
- root: /private/tmp/adaptive-real-project-openspec-check-20260624
- feature: agent-sdk-mvp
- project skill: adaptive-dev-project
- spec system: openspec
- produced harness/project-skill/evidence only.
- did not generate duplicate docs/superpowers/specs/designs/plans.
```

## Top 3 Improvements

1. **Split hard vs soft eval assertions.** Keep strategy, required skills, claim, design policy as hard assertions; treat uncertainty/scope as acceptable ranges when multiple expert readings are valid.
2. **Parallelize fresh-agent route eval.** The test is useful but slow. Add concurrency, per-case duration, and optional retry classification for model/tool timeouts.
3. **Strengthen narrow-skill anti-patterns.** Add compact `NEVER ... because ...` lists to `technical-design`, `knowledge-promotion`, and `project-harness-init`.

## Decision

Adopt current candidate.

It improves the previous workflow by:

- reducing the main router from a large monolith into a skill suite,
- making technical design a first-class artifact,
- separating spec/design/plan/evidence,
- preventing self-signed completion claims,
- preserving light flow for L0/L1,
- giving project harness init a stable local execution engine,
- and adding concrete eval coverage for deterministic, semantic, and real-repo scaffold paths.
