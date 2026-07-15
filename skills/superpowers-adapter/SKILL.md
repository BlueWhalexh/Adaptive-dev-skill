---
name: superpowers-adapter
description: Bridge approved adaptive workflow artifacts into one exact native Superpowers skill without copying its methodology. Use only when workflow-control-plane lists a specific superpowers:* method for the active stage and its output must map back to that stage. 当 control plane 为当前阶段明确选择某个 Superpowers 原生 skill 时使用；不提供完整 Superpowers 工作流。
---

# Superpowers Adapter

你负责契约转换，不负责重写 Superpowers 方法论。

## Role

- Map approved adaptive artifacts into the correct native Superpowers skill input.
- Preserve native Superpowers ownership when a specific method is explicitly selected. Default batch execution, review cadence, and claim verification remain owned by adaptive strategies.
- Convert Superpowers outputs into `workflow-control-plane` transition requests.

## Never

- Do not copy or summarize full Superpowers procedures into this skill.
- Do not load the whole Superpowers chain for a selective route; invoke only the exact `superpowers:*` skill selected for the active stage.
- Do not turn lifecycle depth into a multi-skill Superpowers workflow.
- Do not map an approved plan to `executing-plans` automatically. Plan execution defaults to the Registry's `execution_policy`.
- Do not invoke `subagent-driven-development`, `requesting-code-review`, or `verification-before-completion` as per-Task ceremony.
- Do not mutate `workflow_manifest.json` directly.
- Do not treat Superpowers local/unit evidence as `handoff_done`.

## Mapping

Use `references/superpowers-mapping.md` before calling a Superpowers execution skill.

General mapping. Apply only the row required by the current stage; do not preload other rows:

- Missing or unclear implementation approach -> `superpowers:brainstorming`.
- Approved spec but no implementation plan -> `superpowers:writing-plans`.
- Written plan ready for execution -> use Registry batch policy; adaptive strategies do not schedule `superpowers:executing-plans`.
- Feature/bugfix where strict test-first behavior has clear value -> `superpowers:test-driven-development`; ordinary focused validation uses `change-aware-testing`.
- Failure or unknown cause -> `superpowers:systematic-debugging`.
- Significant high-risk boundary review -> use Strategy `agent-orchestration` gate.
- Completion claim -> `delivery-verification`.

## Exit

After the Superpowers step, return a transition request for:

```sh
python3 skills/workflow-control-plane/scripts/transition_workflow.py workflow_manifest.json transition_request.json
```

The transition request must include produced/updated artifacts, evidence refs, claim requests, and any error code. Let `workflow-control-plane` decide whether the stage can advance.
