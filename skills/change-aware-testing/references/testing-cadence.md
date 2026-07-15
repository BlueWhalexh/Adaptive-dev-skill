# Testing Cadence

READ when deciding how often to test, whether an incremental result is sufficient, or when to expand verification.

## Evidence Levels

| Cadence | Trigger | Default scope | What it proves |
| --- | --- | --- | --- |
| `inner-loop` | implementation edit | affected unit/regression tests | the current diff satisfies its focused signal |
| `checkpoint` | batch, risk boundary, or milestone ready for review | affected module, integration boundary, relevant static checks | the reviewable batch works with nearby dependencies |
| `completion` | request `dev_done`/`integration_done`/`handoff_done` | acceptance-driven evidence matrix | only the claim level authorized by delivery-verification |
| CI/release | merge, release, scheduled regression, explicit project policy | project-defined broad/full suite | repository-wide regression signal for that pipeline |

Full-suite frequency belongs to project policy and CI, not to every coding task.

A Plan Task is not automatically a checkpoint. Consecutive low-risk Tasks with shared context should reuse one recorded base and checkpoint once. Break the batch when changed surfaces cross a material contract, security/data boundary, external side effect, architecture decision, or failure makes the original plan unreliable.

## Selection Rules

1. Derive changed files from a recorded task-start commit plus staged, unstaged, and untracked changes.
2. Use repository-owned impact rules. Prefer build-system dependency graphs or test selectors when the project already has them.
3. Run the smallest set that covers each changed impact domain.
4. Escalate when a changed file can fan out beyond a mapped domain.
5. Preserve evidence labels: focused, module, integration, E2E, system, fresh consumer, and real external are not interchangeable.

## Global-impact Examples

Treat these as candidates for `global_triggers`; projects decide exact paths:

- dependency manifests and lockfiles
- compiler, test runner, workspace, build, or CI configuration
- shared test fixtures and test bootstrap
- public schemas, protocol definitions, code generators, migrations
- authentication, authorization, security policy, shared middleware
- common libraries imported by many modules

An inner-loop hit should return `checkpoint_required`. It should not automatically start a 20-minute suite without an explicit checkpoint decision.

## Example Impact Map

```json
{
  "schema_version": 1,
  "global_triggers": [
    {
      "id": "shared-tooling",
      "globs": ["pyproject.toml", "package-lock.json", "tests/conftest.py"]
    }
  ],
  "rules": [
    {
      "id": "orders",
      "source_globs": ["src/orders/**"],
      "test_globs": ["tests/orders/**"],
      "commands": {
        "inner_loop": [["python3", "-m", "pytest", "{tests}", "-q"]],
        "checkpoint": [["python3", "-m", "pytest", "tests/orders", "-q"]],
        "completion": [["python3", "-m", "pytest", "tests/orders", "-q"]]
      }
    }
  ],
  "fallback_commands": {
    "checkpoint": [["python3", "-m", "pytest", "tests", "-q"]],
    "completion": [["python3", "-m", "pytest", "tests", "-q"]]
  }
}
```

`{tests}` expands into tracked test files matching the selected rule. Commands are argv arrays and are executed without a shell.

## Completion Policy

- L0 docs/mechanical: diff review and format/link/command check as applicable.
- L1 local behavior: affected regression/unit tests plus nearby static/build check when relevant.
- L2 feature/cross-module: focused signals during Tasks; module/integration/acceptance chain once per batch or completion.
- L3 migration/security/handoff: focused signals during Tasks; negative, rollback, system, fresh consumer, or real external evidence at defined risk boundaries and completion.

Do not use a broad unit suite as a substitute for the evidence type actually required by the acceptance criteria.
