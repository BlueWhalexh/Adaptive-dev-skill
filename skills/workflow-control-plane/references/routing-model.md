# Routing Model

`adaptive-dev-workflow` owns classification facts. `workflow-control-plane` owns deterministic strategy resolution.

## Contract

Adaptive emits:

```json
{
  "schema_version": 1,
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

Then resolve:

```sh
python3 skills/workflow-control-plane/scripts/resolve_strategy.py route_decision.json --output resolved_strategy.json
```

## Ownership

- Router owns task facts only.
- Strategy registry owns policy and stage requirements.
- Resolver owns deterministic matching and conflict rejection.
- Workflow-control-plane owns manifest lifecycle.

## Resolution Rules

- `work_intent=review` -> `review-only`.
- `work_intent=research` or `delivery_shape=spike` -> `spike`.
- `work_intent=debug` -> `root-cause-debug`.
- `change_types` contains `migration` -> `migration-critical`.
- `risk=L0` -> `quick-change`.
- `risk=L1` + ready project SOP + known pattern + non-high uncertainty -> `sop-guided-change`.
- Other `risk=L1` -> `focused-change`.
- `risk=L3` -> `complex-real-slice` unless migration.
- `risk=L2` with API contract, auth/security/data/release profile or handoff intent -> `complex-real-slice`.
- Ready project SOP + known/adjacent, non-high uncertainty, non-critical `risk=L2` change -> `sop-guided-iteration`.
- Other `risk=L2` behavior changes -> `spec-driven-feature`.

## Capability Rules

- L0/L1/review/spike/debug usually use `spec_system=none`.
- L2/L3 implementation prefers `openspec`, then `repo_native`, then `fallback`.
- `process_depth=direct` skips workflow manifest creation.
- `process_depth=selective` loads only exact native skills selected by the strategy.
- `process_depth=lifecycle` runs spec/design/plan/execute/verify stages.
- `execution_engine` is `local` for implementation/debug/migration. Superpowers availability appears only as `method_providers=superpowers-native` and may add exact stage skills.
- `execution_engine=none` for review-only and spike.
- `execution_engine=local` is the default for direct and selective implementation/debug work.
- `project_sop=ready` requires instructions, a project skill, and a testing contract. Partial harness evidence must not trigger SOP-guided routing.

## Ambiguity

If the route decision has `ambiguity.status=ambiguous`, resolver rejects with `ROUTE_AMBIGUOUS`. Do not guess silently.

## Anti-Patterns

- Do not put `OpenSpec`, `Superpowers`, or strategy ids in classification fields.
- Do not put `migration`, `mvp`, or `spike` in work intent; use `change_types` and `delivery_shape`.
- Do not let router hand-code the strategy matrix.
- Do not downgrade `auth`, `security`, `data`, `migration`, `release`, or `handoff` risk without explicit user approval.
