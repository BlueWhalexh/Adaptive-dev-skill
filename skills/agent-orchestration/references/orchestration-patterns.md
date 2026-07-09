# Orchestration Patterns

## Sequential

Use when each stage depends on an approved upstream artifact:

```text
context_researcher -> spec_writer -> spec_reviewer -> technical_designer -> plan_writer -> implementer -> code_reviewer -> verifier
```

## Maker / Checker

Use for high-impact spec, design, review, security, data, migration, and handoff work.

```text
producer work_order
  -> producer work_result
  -> reviewer context_packet
  -> reviewer work_order
  -> review result
```

The reviewer context packet should include the produced artifact, source inputs, and acceptance/evidence policy. It should not include the producer's full chat.

## Parallel Review

Use when review surfaces are independent:

```text
code_reviewer
security_reviewer
test_reviewer
docs_reviewer
```

Each gets a separate context packet. The orchestrator merges findings into a single progress summary and only advances when required gates pass.

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

## Repair Loop

When a role returns `blocked`, `failed`, or `needs_human`:

1. Do not assign downstream work orders.
2. Summarize blocker and missing artifact.
3. If new risk facts were discovered, submit a route facts delta to `workflow-control-plane`.
4. Rebuild context packet after manifest revision changes.
