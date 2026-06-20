# Harness Contract

READ when creating or repairing project docs/spec/plan/evidence structure.

DO NOT READ for ordinary implementation tasks after the harness already exists.

## Purpose

The harness turns repeated human guidance into durable project surfaces:

- `AGENTS.md` for always-loaded project rules.
- `.gitignore` for local env files and agent run artifacts.
- `.agent/agents.md` for reusable reviewer/subagent role contracts.
- `.agent/goal-loop-mode.md` for the reusable target-mode prompt.
- `.agent/skills/<project-domain>/` for project-specific SOP and lessons.
- `docs/architecture.md` for current truth.
- `docs/specs/<feature-id>/` for approved intent, design, acceptance, and changes.
- `docs/plans/<feature-id>.md` for staged execution.
- `docs/evidence/<feature-id>.md` for validators, results, gaps, and claim ceiling.

## Spec Contract

`docs/specs/<feature-id>/spec.md` must include:

```md
# Spec

## Intent
What outcome should become true?

## Scope
In-scope modules, users, APIs, workflows, docs, and operational surfaces.

## Non-goals
Adjacent work explicitly out of scope.

## Current Truth
Code paths, docs, runtime facts, existing contracts, and known constraints.

## Behavior
State, trigger, expected behavior, error behavior, empty/edge states.

## Delivery Verification
What evidence must exist before the goal can be called done?

## Acceptance Criteria
Observable checks tied to evidence.

## Stop / Continue Conditions
What can the agent keep iterating on, and what requires human decision?
```

## Design Contract

`docs/specs/<feature-id>/design.md` must include:

```md
# Design

## Current Truth

## Options

## Decision

## Tradeoffs

## Data / API / Security Impact

## Rollout / Rollback

## Open Questions
```

## Acceptance Contract

`docs/specs/<feature-id>/acceptance.yaml` must include machine-readable fields:

```yaml
feature_id:
claim_ceiling: Dev Done
acceptance:
  - id:
    behavior:
    evidence:
      validator:
      type: unit | mock | fake | integration | e2e | real external | fresh consumer | manual
      proves:
      gaps:
non_goals: []
stop_conditions: []
continue_conditions: []
```

Use `Dev Done` unless the spec explicitly requires integration or handoff evidence.
Harness creation alone must stay at `Dev Done`; integration or handoff claims
belong to implemented product behavior, a fresh consumer, or a real external
chain, not to scaffold validation.

## Plan Contract

`docs/plans/<feature-id>.md` must include:

```md
# Plan

## Approved Spec
Link to spec/design/acceptance.

## Task Table
| Task | Scope | Gate | Evidence | Done |
| --- | --- | --- | --- | --- |

## Review Points

## Risks / Gaps
```

## Evidence Contract

`docs/evidence/<feature-id>.md` must include:

```md
# Evidence

## Claim Ceiling
Dev Done / Integration Done / Handoff Done

## Validators
| Validator | Type | Result | Proves | Gaps |
| --- | --- | --- | --- | --- |

## Red / Reproduction Evidence

## Green / Final Evidence

## Review Evidence

## Deferred / Accepted Gaps
```

Use portable validators in generated docs. Prefer repo-relative commands and placeholders:

```text
python3 <skill-dir>/scripts/validate_project_harness.py --root <repo> --feature-id <feature-id> --project-skill <domain>
```

Do not write machine-specific paths such as `/Users/<name>/...`, `/private/tmp/...`, or `/tmp/...` into project docs, project skills, or agent memory.

## Current Truth Routing

When future agents need context:

| Need | Read |
| --- | --- |
| Repo-wide rules | `AGENTS.md` |
| Local env / run artifact guard | `.gitignore` |
| Reviewer roles | `.agent/agents.md` |
| Goal loop handoff | `.agent/goal-loop-mode.md` |
| Architecture facts | `docs/architecture.md` |
| Feature intent | `docs/specs/<feature-id>/spec.md` |
| Approved design | `docs/specs/<feature-id>/design.md` |
| Machine-readable acceptance | `docs/specs/<feature-id>/acceptance.yaml` |
| Execution plan | `docs/plans/<feature-id>.md` |
| Verification result | `docs/evidence/<feature-id>.md` |
| Project SOP | `.agent/skills/<project-domain>/SKILL.md` |

If docs and code disagree, treat code and fresh verification as current truth, then record docs drift.

## Exit Gate

Before saying initialization is complete:

```text
Required files created or intentionally skipped
Existing project convention respected
`.gitignore` protects local env files and `.agent/runs`
Spec has delivery verification
Acceptance has claim ceiling
Plan has per-task evidence
Evidence file distinguishes validator types
Agent roles are read-only by default
Project skill exists and does not duplicate generic TDD/debug/planning
No secrets or local-only paths were written
Validation script passed or gaps are stated
```
