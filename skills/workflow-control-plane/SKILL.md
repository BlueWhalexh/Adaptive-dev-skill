---
name: workflow-control-plane
description: Owns workflow runtime state for adaptive AI coding tasks. Use when resolving route decisions, selecting versioned strategies, creating/updating workflow_manifest.json, validating artifact graphs, resuming interrupted workflows, applying specialist skill transition results, or enforcing strategy/stage/claim/state contracts. 当需要策略解析、workflow_manifest 单点写入、状态迁移、resume、artifact graph、stale 传播、claim ceiling 或工作流状态检查时使用。
---

# Workflow Control Plane

你是 workflow runtime state 的唯一 owner。不要写 spec、design、implementation plan、TDD/debug 方法；这些属于窄 skill 或 Superpowers。

## Responsibilities

- Resolve `route_decision.json` into a versioned strategy.
- Resolve `process_depth=direct|selective|lifecycle` from Registry policy and project SOP evidence.
- Create and update `workflow_manifest.json`.
- Validate strategy version, stage, resume checkpoint, artifact graph, and claim ceiling.
- Apply specialist skill exit contracts through deterministic scripts.
- Expose only current-stage `required_skills`; keep future methods in `skill_plan` until their stage becomes active.
- Reject ambiguous routes, stale artifacts, invalid transitions, and untrusted claims.

## Never

- Do not let `adaptive-dev-workflow` or specialist skills mutate `workflow_manifest.json` directly.
- Do not duplicate SpecFlow, technical-design, context-grounding, delivery-verification, or Superpowers methodology.
- Do not invent global stages; every stage must come from `references/strategies/<strategy>.json`.
- Do not accept a claim signer or claim level that violates `delivery-verification` verifier authority.
- Do not initialize a manifest when the resolved strategy says `manifest_policy=none`.
- Do not model or select full Superpowers execution. Superpowers is a method provider; only current-stage native skills may be activated.
- Do not turn Plan tasks into manifest transitions. Only stage boundaries may update managed workflow state.
- Do not infer per-task review, commit, report, or adjacent regression from parent L2/L3 risk; obey `execution_policy`.

## Inputs

`adaptive-dev-workflow` emits `route_decision.json` using `schemas/route-decision.schema.json`. Capability detection is a deterministic report, not router judgment:

```sh
python3 skills/workflow-control-plane/scripts/detect_capabilities.py --root . --output .agent/runtime/capability-report.json
```

Specialist skills return revision-checked transition requests using `schemas/transition-request.schema.json`. They may produce artifact changes, evidence refs, claim requests, and discovered facts, but the control plane writes the manifest and computes stale propagation.

`direct` routes stop before manifest initialization. `selective` and `lifecycle` routes load only the exact skills selected for the active stage. Lifecycle depth changes artifact/review/evidence gates, not execution ownership.

## Core Commands

Resolve route:

```sh
python3 skills/workflow-control-plane/scripts/resolve_strategy.py route_decision.json --output resolved_strategy.json
```

Initialize workflow:

```sh
python3 skills/workflow-control-plane/scripts/init_workflow.py route_decision.json \
  --resolved-strategy resolved_strategy.json --workflow-id workflow-001 \
  --goal-id <stable-issue-or-goal-id> --goal-summary "<approved goal and scope>" \
  --output workflow_manifest.json
```

Apply stage result:

```sh
python3 skills/workflow-control-plane/scripts/transition_workflow.py workflow_manifest.json transition_request.json
```

Apply discovered route facts after grounding:

```sh
python3 skills/workflow-control-plane/scripts/apply_route_facts_delta.py route_decision.json route_facts_delta.json --output route_decision.v2.json
```

Resume interrupted work:

```sh
python3 skills/workflow-control-plane/scripts/resume_workflow.py workflow_manifest.json \
  --goal-id <stable-issue-or-goal-id> --goal-summary "<current goal and scope>"
```

Migrate an unsigned in-flight v5 manifest after a Strategy major-version change:

```sh
python3 skills/workflow-control-plane/scripts/migrate_workflow_manifest_v5.py old_workflow_manifest.json \
  --goal-id <stable-issue-or-goal-id> --goal-summary "<approved goal and scope>" \
  --output workflow_manifest.json
```

Signed claims are never rewritten; archive or re-verify those workflows.

Inspect status:

```sh
python3 skills/workflow-control-plane/scripts/inspect_workflow.py workflow_manifest.json --validate
```

## Validation

Before claiming workflow state is valid, run:

```sh
python3 skills/workflow-control-plane/scripts/validate_workflow_manifest.py workflow_manifest.json
python3 skills/workflow-control-plane/scripts/validate_artifact_graph.py workflow_manifest.json
python3 skills/workflow-control-plane/scripts/validate_strategy_registry.py
```

## References

- `references/state-machine.md`: state and resume rules.
- `references/error-codes.md`: stable error codes.
- `references/rule-ownership.md`: single owner for each MUST/NEVER rule.
- `references/strategy-registry.md` and `references/strategies/*.json`: strategy authority.
- `references/batch-execution.md`: task-local risk, continuous batches, checkpoint and review cadence.

Only read the references needed for the current operation.
