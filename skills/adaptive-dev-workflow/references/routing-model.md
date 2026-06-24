# Routing Model

READ when classification, routing, or strategy selection is unclear.

## Contract

Classification records task facts. Routing records execution choices. Do not mix them.

```json
{
  "classification": {
    "risk": "L0",
    "mode": "implement",
    "scope": "local",
    "uncertainty": "low",
    "profiles": ["docs"]
  },
  "routing": {
    "spec_system": "none",
    "execution_engine": "local",
    "strategy_id": "quick-change",
    "required_skills": []
  }
}
```

## Risk

| Risk | Meaning | Default strategy |
| --- | --- | --- |
| L0 | docs/mechanical/local no-runtime work | `quick-change` |
| L1 | narrow behavior or local bugfix | `focused-change` |
| L2 | new behavior/API/UI workflow or 1-3 modules | `spec-driven-feature` |
| L3 | cross-module/service, security, data, migration, delivery, MVP loop | `complex-real-slice` or `migration-critical` |

## Mode Overrides

| Mode | Strategy |
| --- | --- |
| `debug` | `root-cause-debug` |
| `review` | `review-only` |
| `spike` | `spike` |
| `migration` | `migration-critical` |
| `mvp` | `complex-real-slice` |

SpecFlow/context-stage rule:

- Concrete feature + "先用 SpecFlow 产出 spec" => `mode=implement`, `strategy_id=spec-driven-feature`, `execution_engine=none`, `required_skills=["specflow"]`.
- Concrete complex feature + "先梳理上下文/验收方式/不要改代码" => `mode=implement`, `strategy_id=complex-real-slice`, `execution_engine=none`, `required_skills` starts with `context-grounding`.
- Open-ended "调查/给几个方案/不知道做不做" => `mode=spike`, `strategy_id=spike`.
- `mode=spike` uses `execution_engine=none`; it may produce analysis/evidence artifacts but does not execute implementation.

L0 visual micro-change rule:

- Pure CSS spacing/color/copy changes with no state, data, API, permission, or workflow impact stay `risk=L0`, `strategy_id=quick-change`, `design_control=none/none`.

Hard design trigger rule:

- Public API or compatibility contract changes, including adding request/response parameters such as export `format`, use `strategy_id=complex-real-slice`, `design_control=standalone/independent`, and require `context-grounding`, `specflow`, `technical-design`, and `delivery-verification`.

Project harness init rule:

- Goal Loop Mode, AGENTS.md, agent team, project skill, or project harness initialization is `risk=L3`, `mode=mvp`, `strategy_id=complex-real-slice`, and requires `project-harness-init`, `technical-design`, `delivery-verification`, and `knowledge-promotion`; add `context-grounding`/`specflow` when OpenSpec is absent or current truth is unclear.

Permission/auth migration rule:

```json
{
  "classification": {
    "risk": "L3",
    "mode": "migration",
    "scope": "cross_module",
    "uncertainty": "high",
    "profiles": ["auth", "security", "data"]
  },
  "routing": {
    "spec_system": "fallback",
    "execution_engine": "superpowers",
    "strategy_id": "migration-critical",
    "required_skills": ["context-grounding", "specflow", "delivery-verification"]
  }
}
```

Generic CI failure prompt:

```json
{
  "classification": {
    "risk": "L2",
    "mode": "debug",
    "scope": "cross_module",
    "uncertainty": "high",
    "profiles": ["infra"]
  },
  "routing": {
    "spec_system": "none",
    "execution_engine": "superpowers",
    "strategy_id": "root-cause-debug",
    "required_skills": ["superpowers:systematic-debugging"]
  }
}
```

## Routing Decisions

- `spec_system=openspec`: repo already has OpenSpec or product behavior must enter OpenSpec proposal/spec/tasks.
- `spec_system=repo_native`: repo has a stronger native spec/ADR/plan process.
- `spec_system=fallback`: use Superpowers-compatible fallback spec/plan files.
- `execution_engine=superpowers`: implementation should use native Superpowers skills such as TDD, writing plans, systematic debugging, code review, or executing plans.
- `execution_engine=local`: small local work can be handled directly with focused verification.
- `execution_engine=none`: review-only, spec-only, or planning-only task.

## Design Control

Set `design_control` from selected strategy:

| Strategy | design_policy | design_review |
| --- | --- | --- |
| `quick-change` | `none` | `none` |
| `focused-change` | `embedded` | `self` |
| `root-cause-debug` | `embedded` | `self` |
| `spec-driven-feature` | `embedded` | `self` |
| `complex-real-slice` | `standalone` | `independent` |
| `migration-critical` | `standalone` | `human` |
| `spike` | `none` | `independent` |
| `review-only` | `none` | `independent` |

Escalate to a standalone technical design when a task introduces a new responsibility boundary, cross-module/service flow, public API/event contract, data model/migration, auth/security/privacy boundary, state machine, concurrency/idempotency/recovery behavior, external integration, runtime/observability concern, or several viable technical approaches with material tradeoffs.

## Anti-Patterns

- Do not output `Tiny`, `Small`, `Medium`, `Large`, `OpenSpec`, or `Debug` as a route.
- Do not call OpenSpec a strategy. It is a spec system.
- Do not call Superpowers a strategy. It is an execution engine.
- Do not request `dev_done` for analysis/spec/plan-only work.
- Do not request any delivery claim during a route-only eval or before evidence exists.
- Do not create duplicate fallback technical design when OpenSpec/repo-native already has a canonical design document.
