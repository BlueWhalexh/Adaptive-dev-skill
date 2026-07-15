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
| `spec-reviewer` | New or materially changed product contract | Product spec, acceptance | Missing goals, non-goals, behavior, delivery verification | Rewrite product silently |
| `technical-design-writer` | Approved spec before planning | Spec, current truth, constraints | Technical design draft, contracts, risks, evidence mapping | Write implementation plan/code |
| `technical-design-reviewer` | Standalone design required | Technical design, spec, context | Design findings, missing boundaries, review decision | Review own design |
| `plan-reviewer` | New/changed high-impact plan or uncertain sequencing | Plan, code map, constraints | Missing tasks, sequencing risk, missing gates | Implement |
| `test-strategy-reviewer` | Evidence matrix unclear | Spec, changed surfaces, test commands | Required validators and claim ceiling | Demand heavy tests for Tiny tasks |
| `evidence-reviewer` | Integration/handoff claim or material evidence gap | Diff, evidence, final claim | Claim ceiling, gaps, mock/fake/real labels | Accept mock as real |
| `security-data-reviewer` | Auth, permission, PII, secrets, migrations | Spec, diff, data/security surfaces | Negative cases, data safety, rollback | Guess compliance |
| `knowledge-curator` | After MVP or repeated lesson | Candidate, evidence, scope | Promote/reject destination | Write policy directly |

## Invocation Guidelines

| Work type | Reviewer usage |
| --- | --- |
| Tiny | No reviewer by default |
| Small | Reviewer only when cause or validation is unclear |
| Medium | Use one focused reviewer for spec/design/plan/evidence when risk is meaningful |
| Large | Review new/changed high-impact artifacts and material boundaries; do not add a reviewer per implementation Task |
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

For continuous low-risk batches, keep one implementer context and use one checkpoint. Critical/Major or contract-changing findings receive at most one delta re-review; Minor non-contract findings do not restart the full review chain.

## Maintenance

- Add a role only after it is reused or a review gap repeats.
- Retire unused roles.
- Keep `.agent/agents.md` short; put long examples in project skill references.
- Do not let roles duplicate TDD/debug/planning workflows owned by stronger skills.
