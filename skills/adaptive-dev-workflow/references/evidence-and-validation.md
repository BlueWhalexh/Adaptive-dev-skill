# Evidence And Skill Validation Reference

READ when: route/evidence choice is ambiguous, review/test evidence adequacy is the task, planning Medium/Large work, or changing `adaptive-dev-workflow`.

DO NOT READ for obvious Tiny/Small tasks when the validator is clear from `SKILL.md`.

## Contents

- Evidence Matrix
- Evidence Selection Algorithm
- Evidence Plan Shape
- Route And Evidence Cards
- Completion Claim Levels
- Evidence Manifest
- Skill Validation Protocol
- Skill Iteration Protocol
- Eval Case Schema
- Seed Cases
- Failure Classes
- Change Rule

## Evidence Matrix

Choose tests from the changed risk surface. Do not ask the user to pick a test taxonomy unless a product or release tradeoff is needed.

| Changed Surface | Required Evidence | Escalate Evidence When | Claim Ceiling Without Escalation |
| --- | --- | --- | --- |
| Text/docs/comment | Diff review; render/link/command check only if semantics matter | README command, onboarding, API docs, or user workflow changes | Dev Done |
| Config/defaults | Parse, dry-run, or relevant command | Runtime, deploy, permission, env, or availability blast radius exists | Dev Done |
| Pure logic | Unit/table-driven test around behavior | Historical bugs, many boundaries, or algorithmic edge cases | Dev Done |
| Bugfix | Reproduction, failing test, or focused validator before fix | Regression can be automated or bug is user-visible | Dev Done unless regression/chain proves more |
| UI behavior/layout | Component/browser/manual screenshot evidence | Key flow, fragile responsive layout, accessibility, or visual regression risk | Integration Done only with browser/flow evidence |
| API/service contract | Request/response/auth/error compatibility test | Public API, compatibility, permissions, client SDK, or cross-service use | Integration Done |
| Data model/migration | Schema/migration/backward compatibility check | Production data, rollback, backfill, compatibility, or retention risk | Integration Done only with migration evidence |
| Auth/security/permission | Negative test and boundary check | PII, secrets, payment, privilege escalation, or tenant boundary | Integration Done only with negative evidence |
| State machine/workflow | Transition tests for state, trigger, and expected result | Concurrency, idempotency, retry, rollback, or critical workflow | Integration Done |
| External integration | Fake/contract test with boundary labelled | Real provider promised, sandbox available, or handoff depends on provider | Handoff Done only with real/sandbox evidence |
| SDK/package/image/CLI | Build/install or invocation from artifact | Consumer will use without producer context | Handoff Done only with fresh consumer |
| Release/handoff | Evidence manifest and documented run path | Production-ready/import-ready/drop-in/onboarding claim | Handoff Done only with delivery gate |

## Evidence Selection Algorithm

Use this before implementation for non-trivial work:

```text
1. Identify changed surfaces: docs, config, logic, UI, API, data, auth, state, integration, delivery.
2. For each surface, select the required evidence from the matrix.
3. If behavior is automatable at reasonable cost, prefer Red or reproduction before implementation.
4. If modules or user flows must connect, add chain evidence: integration, smoke, browser, or E2E.
5. If another consumer must use the output, add handoff evidence: artifact, fresh consumer, onboarding, or real external chain.
6. If auth/data/security is touched, add negative evidence and review.
7. Set the completion claim ceiling to the weakest required evidence that actually ran.
```

Evidence can be lighter than the matrix only when the task risk is lower than normal and the remaining gap is stated. Evidence must be heavier when the user-visible claim is stronger than the code change.

## Evidence Plan Shape

Choose evidence from the risk being changed, not from a generic test taxonomy.

For non-trivial work, record:

```text
Risk type: logic, UI, API, data, permission, workflow, delivery, or external integration
Pre-implementation evidence: Red/reproduction, or explicit alternate validator
Post-implementation evidence: focused validator plus relevant build/lint/type checks
Chain evidence: integration, smoke, or E2E only when modules or user flows must connect
Handoff evidence: fresh consumer or real external call only when delivery claims require it
Claim ceiling: Dev Done, Integration Done, or Handoff Done
```

## Route And Evidence Cards

Use cards before implementation for non-Tiny work and before final claims for any task where the evidence could be misread.

```yaml
route_card:
  route: Tiny | Small | Debug | Medium | Large | OpenSpec
  risk_type: logic | UI | API | data | permission | workflow | delivery | external integration
  changed_surfaces: []
  required_gates: []
  delegated_skills: []
  loaded_references: []
  stop_gates: []
evidence_card:
  claim_ceiling: Dev Done | Integration Done | Handoff Done
  pre_implementation:
  post_implementation:
  chain:
  handoff:
  review:
  gaps:
```

Run `scripts/validate_workflow_cards.py <file>` when a card is written to disk. The card is not the evidence itself; it is the contract that prevents route drift and completion overclaim.

## Completion Claim Levels

| Claim | Required Evidence | Do Not Claim When |
| --- | --- | --- |
| Dev Done | Focused validator and relevant static/build checks pass, with gaps stated | Only design/spec was written, or checks were not run |
| Integration Done | The changed modules or user-visible chain pass integration, smoke, E2E, or equivalent chain evidence | Only isolated unit/mock tests passed |
| Handoff Done | A fresh consumer, tested artifact, onboarding path, or promised real external chain works under the delivery contract | Only producer-side tests passed, or local env/cache/source paths were required but not declared |

## Evidence Manifest

Use a lightweight manifest for Medium/Large work, delivery handoff, or any task where the user asks "how do we know it is done?"

```yaml
feature_id:
commit_sha:
claim_ceiling: Dev Done | Integration Done | Handoff Done
changed_surfaces: []
acceptance:
  - id:
    evidence:
validators:
  - name:
    command_or_method:
    type: unit | mock | fake | integration | e2e | real external | fresh consumer | manual
    result:
    proves:
    gaps:
deferred:
review_focus:
```

Use `scripts/validate_evidence_manifest.py` when available to catch missing fields before completion. The validator requires final `result` values by default and rejects `Integration Done` without integration/e2e/real/fresh-consumer evidence and `Handoff Done` without fresh-consumer or real-external evidence. Use `--allow-pending` only for draft review, not completion.

## Skill Validation Protocol

Validate the skill itself with behavior evals, not intuition.

1. Static validation: frontmatter, `openai.yaml`, duplicate versions, and key sections.
2. Route dry run: Tiny/Small/Medium/Large/debug prompts route as expected.
3. Blind subagent eval: a fresh subagent routes cases using only `SKILL.md`.
4. Developer/auditor simulation: one session executes, another audits output,
   evidence, route choice, docs, and completion claims.
5. Workflow E2E eval: initialize a temp harness, validate cards, and verify claim ceilings fail for mock-only integration or non-fresh handoff evidence.
6. Fresh agent semantic route eval: run `scripts/run-fresh-agent-route-eval.py`
   for representative seed cases when routing semantics change. This starts
   fresh `codex exec` sessions, gives only the raw task prompt plus the local
   skill path, and compares the returned route/evidence JSON to seed-case
   expectations without leaking expected answers.
7. Handoff fresh consumer eval: run
   `scripts/run-handoff-fresh-consumer-eval.py` or the default workflow E2E to
   prove a package-like artifact can be installed and imported from a clean
   consumer environment without producer source paths or network.

Fresh consumer evidence proves artifact/onboarding mechanics. It does not prove
provider correctness, credentials, latency, permissions, or real external
behavior. If the delivery claim depends on an external provider or platform,
the concrete project still needs real external or sandbox-provider evidence.

When working in this skill repository, use `evals/seed-cases.yaml` for stable
regression scenarios and `evals/failure-cases.yaml` for real cases captured
during development. A failure case should include the raw prompt, expected
behavior, actual behavior, evidence gap, impact, and proposed minimal rule, if
any.

## Skill Iteration Protocol

Do not self-modify the skill from a single anecdote.

| Signal | Action |
| --- | --- |
| One observed failure | Capture the case and classify the failure; do not change rules yet unless severity is P0 and general |
| Same failure class twice | Add the smallest trigger, evidence rule, or reference example that prevents it |
| Same failure class three times | Adjust the route map, evidence ladder, or handoff gate |
| Mechanical repeat failure | Prefer hook, script, lint rule, or CI check over more prompt text |
| Project-specific lesson | Put it in the repo `AGENTS.md` or docs, not this general skill |

Before accepting a skill patch, run static validation, the sandbox eval script,
workflow E2E, route dry-runs for seed cases, and an independent review or
skill-judge pass when the patch changes routing semantics. When a patch changes
route selection, project harness behavior, or handoff claims, add fresh agent
semantic route eval if the local model/CLI is available.

## Eval Case Schema

```yaml
- id: tiny-readme-command
  prompt: "README 里把 npm 改成 pnpm"
  expected_route: Tiny
  expected_cards:
    route_card: inline_ok
    evidence_card: inline_ok
  expected_gates:
    - focused verification
  expected_delegate_skill: []
  expected_docs: []
  expected_evidence:
    - diff review
    - command/link check only if command semantics matter
  claim_ceiling: Dev Done
  expected_no:
    - no TDD
    - no design doc
    - no subagent review
  actual_route:
  actual_gates:
  actual_delegate_skill:
  actual_docs:
  actual_evidence:
  pass:
  observed_failure:
  skill_change_needed:
```

## Seed Cases

| ID | Prompt | Expected Route | Key Judgment |
| --- | --- | --- | --- |
| `tiny-readme-command` | "README 里把 npm 改成 pnpm" | Tiny | No Red; check diff and command semantics only |
| `tiny-css-spacing` | "把按钮间距调大 4px" | Tiny/Small | Visual evidence; no unit test by default |
| `small-login-bug` | "修登录按钮点击没反应" | Small | Reproduce or focused validator; regression if automatable |
| `small-config-risk` | "改一下超时配置默认值" | Small | Blast radius may require smoke/integration |
| `medium-order-filter` | "订单页加状态筛选" | Medium | UX/API boundary, test plan, phase smoke |
| `medium-api-contract` | "给导出接口加 format 参数" | Medium | Contract/error/compatibility tests |
| `large-permission-model` | "把用户权限模型从 role 改成 policy" | Large | Spec, migration, security review, E2E |
| `debug-ci` | "CI 挂了修一下" | Debug | Use systematic debugging; read logs and reproduce first |
| `docs-architecture-drift` | "把 runtime 架构文档同步到当前实现" | Small/Medium docs | Read code and canonical docs; avoid narrative-only edits |
| `openai-api-upgrade` | "升级 OpenAI API 调用到最新模型" | Medium + openai-docs | Official docs, narrow change, API-shape verification |
| `tiny-readme-command-en` | "Change the README install command from npm to pnpm" | Tiny | No Red; verify diff and command semantics only |
| `project-init-mvp-zh` | "新项目先做一个最小可用链路，后续要持续开发并沉淀项目 skill" | Medium/Large + harness | Read complex-project-harness and project-skill lifecycle; propose lean init |
| `project-init-mvp-en` | "Start a new project with an MVP vertical slice and keep reusable project SOPs for future work" | Medium/Large + harness | Lean harness init, project skill candidate path, evidence manifest |
| `quality-feedback-mock-zh` | "你这个测试不真实，mock 冒充了真实链路" | Quality feedback + evidence review | Classify evidence gap, lower claim ceiling, select real/fresh-consumer evidence when promised |
| `quality-feedback-mock-en` | "This verification is not real; mocks are being claimed as an integration path" | Quality feedback + evidence review | Separate mock/fake/integration/real evidence and repair claim ceiling |
| `agent-team-zh` | "给这个项目定义一个 agent 团队，review spec、plan 和 evidence" | Agent team + harness | Read agent-team reference; use `.agent/agents.md`, roles read-only by default |
| `agent-team-en` | "Define a project agent team for spec, plan, evidence, and security review" | Agent team + harness | Create/use project-local role contracts, not ad hoc prompts |
| `mvp-learning-zh` | "MVP 跑通了，以后同类任务别总让我重复说明这些项目经验" | Project skill learning | Capture learning candidate; do not directly append raw lessons to global AGENTS.md |

## Failure Classes

| Failure | Example | Severity |
| --- | --- | --- |
| Over-process | README edit requires Red-Green, design doc, and E2E | P2 |
| Under-process | Permission model rewrite ships with unit tests only | P0 |
| Gate dilution | TDD route uses a local softer summary instead of the selected TDD skill | P0 |
| Evidence mismatch | Visual UI change reports only test pass counts | P1 |
| Docs drift | Public API changes without current-truth docs/spec update | P1 |
| Missing harness | Large/new-project work starts without current-truth docs or an explicit accepted gap | P1 |
| Completion overclaim | "Done" without fresh evidence or stated gaps | P0 |
| Skill ambiguity | Evaluators disagree on the same route repeatedly | P1 |

## Change Rule

- Same failure twice: add the smallest trigger or escalation rule.
- Same failure three times: adjust the flow or evidence ladder.
- Mechanical failure: prefer hook, CI, script, or lint rule.
- Project-specific lesson: put it in repo `AGENTS.md` or docs, not this skill.
