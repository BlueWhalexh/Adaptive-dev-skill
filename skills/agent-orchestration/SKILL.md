---
name: agent-orchestration
description: Coordinate role-based AI agents through agent rosters, work orders, context packets, artifact refs, and structured result contracts. Use when a software workflow needs multiple roles such as context researcher, spec writer, spec reviewer, technical designer, implementer, code reviewer, tester, verifier, or when the user wants an orchestrator to manage progress without manually copying context between sessions. 当需要多 Agent 协作、角色隔离、上下文投影、work order、artifact 驱动交接、进度监管或避免人工搬运上下文时使用。
---

# Agent Orchestration

目标：让 orchestrator 管状态和上下文投影，不亲自写 spec、代码、review 或 verification。Agent 之间不传聊天记录，只通过 workflow state、artifact refs、context packet 和 structured result 协作。

## Responsibilities

- Create and validate `agent_roster.json`.
- Build role-scoped `context_packet.json` from workflow/artifact state.
- Create `work_order.json` for a specific role and stage.
- Validate `work_result.json` before handing it to `workflow-control-plane`.
- Summarize progress, blockers, and missing role outputs.

## Never

- Do not pass full conversation history as role context.
- Do not let role agents mutate `workflow_manifest.json` directly.
- Do not let a producer approve its own spec/design/review output.
- Do not treat role output as a delivery claim; `delivery-verification` owns claim attestations.
- Do not spawn agents merely because a role exists; use roles only when isolation, maker/checker, or parallelism adds value.

## Contracts

Canonical JSON contracts:

- `schemas/agent-roster.schema.json`: available roles, agent ids, capabilities, limits.
- `schemas/context-packet.schema.json`: role-scoped artifact refs, allowed paths, omissions, instructions.
- `schemas/work-order.schema.json`: objective, role, stage, context packet ref, expected output.
- `schemas/work-result.schema.json`: structured role output, produced artifacts, facts, blockers.

Use scripts rather than hand-writing contracts when possible:

```sh
python3 skills/agent-orchestration/scripts/build_context_packet.py workflow_manifest.json --role spec_reviewer --context-packet-id CP-001 --output context_packet.json --include-artifact spec-001
python3 skills/agent-orchestration/scripts/create_work_order.py --workflow-id WF-001 --role spec_reviewer --stage-id spec_review --context-packet context_packet.json --objective "Review draft spec" --output work_order.json
python3 skills/agent-orchestration/scripts/validate_work_result.py work_result.json --work-order work_order.json
python3 skills/agent-orchestration/scripts/summarize_progress.py --work-orders .agent/runs/WF-001/work_orders --results .agent/runs/WF-001/results
```

## Role Flow

1. Read `workflow_manifest.json` and strategy stage from `workflow-control-plane`.
2. Select a role from `agent_roster.json`; if none exists, create a minimal roster first.
3. Build the smallest context packet for that role. Include artifact refs and explicit omissions.
4. Create one work order with one objective and one output contract.
5. Give the role agent only the work order and context packet, not the whole chat.
6. Validate the work result. Convert accepted outputs into a `transition_request.json` for `workflow-control-plane`.

## References

- `references/role-contracts.md`: standard role boundaries and anti-patterns.
- `references/context-projection.md`: how to decide included/omitted context.
- `references/orchestration-patterns.md`: sequential, maker/checker, and parallel review patterns.

Read only the reference needed for the current orchestration decision.

## Validation

After modifying this skill, run:

```sh
python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/agent-orchestration
python3 scripts/run-agent-orchestration-e2e-eval.py
python3 scripts/run-skill-sandbox-eval.py
```
