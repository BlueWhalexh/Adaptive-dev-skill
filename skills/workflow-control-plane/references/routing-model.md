# Routing Model

`adaptive-dev-workflow` owns classification facts. `workflow-control-plane` owns deterministic strategy resolution.

## Contract

Adaptive emits:

```json
{
  "schema_version": 1,
  "classification": {
    "risk": "L2",
    "intent_mode": "implement",
    "delivery_shape": "feature",
    "scope": "module",
    "uncertainty": "medium",
    "profiles": ["api"],
    "change_types": ["api_contract"]
  },
  "capabilities": {
    "spec_systems": ["fallback"],
    "execution_engines": ["superpowers"],
    "project_harness": "present"
  },
  "constraints": {
    "human_design_approval_required": false,
    "isolated_review_required": true
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

- `intent_mode=review` -> `review-only`.
- `intent_mode=spike` -> `spike`.
- `intent_mode=debug` -> `root-cause-debug`.
- `intent_mode=migration` or `change_types` contains `migration` -> `migration-critical`.
- `risk=L0` -> `quick-change`.
- `risk=L1` -> `focused-change`.
- `risk=L3` -> `complex-real-slice` unless migration.
- `risk=L2` with API contract, auth/security/data/delivery/release profile -> `complex-real-slice`.
- Other `risk=L2` behavior changes -> `spec-driven-feature`.

## Capability Rules

- L0/L1/review/spike/debug usually use `spec_system=none`.
- L2/L3 implementation prefers `openspec`, then `repo_native`, then `fallback`.
- `execution_engine=superpowers` when available for L2/L3 implementation/debug/migration.
- `execution_engine=none` for review-only and spike.
- `execution_engine=local` for L0 fast path when available.

## Ambiguity

If the route decision has `ambiguity.status=ambiguous`, resolver rejects with `ROUTE_AMBIGUOUS`. Do not guess silently.

## Anti-Patterns

- Do not put `OpenSpec`, `Superpowers`, or strategy ids in classification fields.
- Do not let router hand-code the strategy matrix.
- Do not downgrade `auth`, `security`, `data`, `migration`, `release`, or `delivery` risk without explicit user approval.
