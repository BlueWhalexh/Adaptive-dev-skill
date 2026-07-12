# No Full Superpowers Design

## Decision

删除 `execution_engine=superpowers`。复杂度只决定 workflow stages、artifact graph、review 和 evidence gates，不决定执行所有权。

```text
workflow-control-plane = execution owner
Superpowers            = optional method provider
skill_plan[stage]       = only activation authority
```

## Resulting Policy

| Strategy | Execution | Default Superpowers methods |
| --- | --- | --- |
| `quick-change` / `sop-guided-change` | direct local | none |
| `focused-change` / `sop-guided-iteration` | selective local | none |
| `root-cause-debug` | selective local | `systematic-debugging` at failure capture |
| `spec-driven-feature` | lifecycle local | `writing-plans` at plan stage |
| `complex-real-slice` | lifecycle local | exact plan/execute/review/verification method at its owning stage |
| `migration-critical` | lifecycle local | exact plan/execute/review/verification method at its owning stage |

Complex and migration workflows may use several native methods over time, but never delegate the whole workflow to Superpowers and never preload future-stage skills.

## Contract Changes

- `route_decision` schema v3: `required_execution_engine` only accepts `none|local|null`.
- `capability_report` schema v3: Superpowers moves from `execution_engines` to `method_providers=superpowers-native`.
- `resolved_strategy` schema v3: `execution_engine` only accepts `none|local`.
- `workflow_manifest` schema v5: `execution_engine` only accepts `none|local`.
- Strategy Registry: every strategy uses `local|none`; complex/migration versions advance to 1.2.

## Safety Boundaries

- Missing `superpowers-native` removes every `superpowers:*` entry from `skill_plan`; local lifecycle remains executable.
- A route or manifest containing `execution_engine=superpowers` is rejected.
- `required_skills` must equal `skill_plan[current_stage]`.
- Auth/security/data/migration/handoff tasks retain lifecycle, standalone design, review, rollback and evidence gates.

## Validation

- Deterministic workflow E2E: pass, including provider-present/provider-missing paths and rejection of `execution_engine=superpowers` in route/manifest.
- Sandbox suite: 17 route cases, 34 negative cases, workflow and agent-orchestration E2E pass.
- Fresh-agent semantic case `large-permission-model`: `L3 / migration-critical`, resolved with local lifecycle ownership; pass.

## Remaining Environment Risk

Global skill discovery still exposes duplicate broad Superpowers skills from `.agents/skills`, legacy `~/.codex/superpowers/skills`, and cached namespaced sources. Repository routing no longer selects a full workflow, but a broad third-party frontmatter may still trigger independently. Discovery deduplication is a separate environment change and should be measured in a new Codex task after restart.
