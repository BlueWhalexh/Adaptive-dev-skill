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

## Repair Loop

When a role returns `blocked`, `failed`, or `needs_human`:

1. Do not assign downstream work orders.
2. Summarize blocker and missing artifact.
3. If new risk facts were discovered, submit a route facts delta to `workflow-control-plane`.
4. Rebuild context packet after manifest revision changes.
