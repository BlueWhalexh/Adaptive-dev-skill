# Agent Team Roles

READ when creating `.agent/agents.md` or repairing weak project subagent/reviewer behavior.

## Rules

Project agents are role contracts, not personalities. Keep roles read-only by default. The main agent owns integration and completion claims.

Each role must return:

```text
Findings by severity
Evidence checked
Files/docs inspected
Uncertainty
Claim limit
Recommended next action
```

## Default Roles

| Role | Trigger | Inputs | Output | Must Not |
| --- | --- | --- | --- | --- |
| `repo-grounder` | New area, stale docs, unclear architecture | Goal, paths, docs | Current truth map, docs drift, risks | Edit files |
| `spec-reviewer` | Before Medium/Large implementation | Spec, design, acceptance | Missing goals, non-goals, behavior, delivery verification | Rewrite product silently |
| `plan-reviewer` | Before plan execution | Plan, code map, constraints | Missing tasks, sequencing risk, missing gates | Implement |
| `test-strategy-reviewer` | Evidence matrix unclear | Spec, changed surfaces, test commands | Required validators and claim ceiling | Demand heavy tests for Tiny tasks |
| `evidence-reviewer` | Before completion or handoff | Diff, evidence, final claim | Claim ceiling, gaps, mock/fake/real labels | Accept mock as real |
| `security-data-reviewer` | Auth, permission, PII, secrets, migrations | Spec, diff, data/security surfaces | Negative cases, data safety, rollback | Guess compliance |
| `knowledge-curator` | After MVP or repeated lesson | Candidate, evidence, scope | Promote/reject destination | Write policy directly |

## Invocation Guidelines

| Work type | Reviewer usage |
| --- | --- |
| Tiny | No reviewer by default |
| Small | Reviewer only when cause or validation is unclear |
| Medium | Use one focused reviewer for spec/plan/evidence when risk is meaningful |
| Large | Use separate design/plan/evidence review; add security/data review when relevant |
| Handoff | Use evidence reviewer and fresh consumer when the claim requires it |

## Prompt Shape

```text
Role: <role>
Goal:
Scope:
Current truth sources:
Artifacts to inspect:
Constraints:
Expected output:
Must not:
```

Pass only the minimum complete context. Do not include private secrets or production data.

## Maintenance

- Add a role only after it is reused or a review gap repeats.
- Retire unused roles.
- Keep `.agent/agents.md` short; put long examples in project skill references.
- Do not let roles duplicate TDD/debug/planning workflows owned by stronger skills.
