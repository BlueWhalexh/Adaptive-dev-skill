# Orchestration Patterns

## Sequential

Use when multiple roles are valuable but outputs depend on one another. Start only the next role that has a ready input:

```text
maker -> optional checker -> next maker
```

Do not instantiate a complete lifecycle team. Reuse accepted artifacts and skip roles whose work already exists.

## Continuous Batch

Default for several related low-risk edits after direction is clear:

```text
one scoped context packet
  -> main implementer handles several low-risk Tasks
  -> focused signal per Task
  -> one batch checkpoint
  -> optional boundary reviewer
  -> one commit and progress result
```

Task checkboxes remain progress tracking. They do not imply one work order, fresh agent, reviewer, fixer, report, or commit each.

## Maker / Checker

Use when an independent checker is required by project policy. A single checker does not require loading the full orchestration skill or creating machine contracts.

```text
producer work_order
  -> producer work_result
  -> reviewer context_packet
  -> reviewer work_order
  -> review result
```

The reviewer context packet should include the produced artifact, source inputs, and acceptance/evidence policy. It should not include the producer's full chat.

## Parallel Work

Use only when writers own disjoint files and write state. Parallel read-only review is also safe when review surfaces are independent:

```text
code_reviewer
security_reviewer
test_reviewer
docs_reviewer
```

Each gets a separate minimal packet. The orchestrator merges outputs once; it does not stream every role log into the main context.

## Runtime Carrier

`agent-orchestration` does not start workers by itself. Each `work_order.json` must say which carrier will execute it:

| Carrier | Meaning | Isolation claim |
| --- | --- | --- |
| `main_session` | Current Codex session executes the role | `none` or `role_contract_only`; never `fresh_context` |
| `subagent` | Fresh subagent executes the role | May claim `fresh_context` if only packet/order are provided |
| `separate_session` | Separate Codex/Claude/Gemini session executes the role | May claim `fresh_context` if only packet/order are provided |
| `human` | Human reviewer/implementer executes the role | Do not assume model context isolation |
| `external` | External worker or CI/verifier executes the role | May claim `fresh_context` when inputs are packet/order only |

Use `main_session` for lightweight coordination and local tasks. Use `subagent` or `separate_session` when reviewer/verifier independence matters.

## Workspace Policy

`workspace_policy` describes file-system write isolation, not context isolation:

| Policy | Use when |
| --- | --- |
| `shared_readonly` | Review, spec/design critique, evidence inspection, or any role that should not mutate code |
| `shared_writer` | Main session performs a sequential write task and owns integration |
| `isolated_worktree` | Any non-main carrier writes code, or multiple write tasks can run in parallel |

Rules:

- `fresh_context` requires `execution_carrier=subagent`, `separate_session`, or `external`.
- `main_session` cannot claim `fresh_context`.
- Non-main carriers cannot use `shared_writer`; give them an isolated worktree.
- `isolated_worktree` requires `worktree_ref` and `merge_owner`.
- Review/verifier roles use `shared_readonly`.

## Repair Boundary

When a role returns `blocked`, `failed`, or `needs_human`:

1. Keep actionable diagnosis and repair in the current owner when possible.
2. Stop dependent work only when the missing input truly blocks it; independent work may continue.
3. Escalate only product decisions, unsafe operations, or blockers with no executable next step.
4. Refresh only packets affected by changed inputs or decisions.

For review findings, fix Critical/Major or material contract findings and run at most one delta re-review. Minor non-contract findings may be fixed without restarting the full maker/checker chain.
