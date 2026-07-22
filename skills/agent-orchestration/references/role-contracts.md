# Role Contracts

Use these roles as boundaries, not as mandatory runtime workers. Create a work order only when the role adds isolation, maker/checker separation, or parallel throughput. Runtime isolation is controlled by `execution_carrier`, `context_isolation`, and `workspace_policy` in the work order.

| Role | Input | Output | Never |
| --- | --- | --- | --- |
| `context_researcher` | User goal, repo entry points, existing docs | Focused findings, relevant refs, risks | Implement broad code |
| `spec_writer` | Intent, approved Analysis Pack | Draft spec | Approve own spec |
| `spec_reviewer` | Draft spec, Analysis Pack, acceptance policy | Spec review report | Rewrite product silently |
| `technical_designer` | Approved spec, Context Manifest, architecture constraints | Technical design artifact | Write implementation task DAG |
| `plan_writer` | Approved spec/design, accepted constraints | Implementation plan or task packets | Invent missing product behavior |
| `implementer` | Accepted objective, relevant context, coding constraints | Patch/diff and focused evidence | Change accepted product or architecture boundaries silently |
| `code_reviewer` | Diff, spec, design, evidence summary | Review findings | Trust implementer narrative as sole evidence |
| `tester` | Acceptance criteria, changed files, test strategy | Test report, evidence refs | Claim real external success from mock/fake only |
| `verifier` | Acceptance, raw evidence, requested claim | Supported/unsupported result and evidence gaps | Infer real behavior from maker narrative |

## Maker / Checker

- A producer cannot be the checker for the same artifact.
- Spec/design/code review should receive artifact refs and evidence, not the producer's full private chain-of-thought or chat history.
- Human approval is required when the result changes an accepted product decision, public contract, data/auth/security boundary, irreversible production action, or migration policy.

## Role Naming

Use stable snake_case role ids in JSON contracts. Human-facing labels can be Chinese, but schema fields and role ids stay English.
