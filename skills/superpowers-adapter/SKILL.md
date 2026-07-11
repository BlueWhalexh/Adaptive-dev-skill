---
name: superpowers-adapter
description: Bridge approved adaptive workflow artifacts into exact native Superpowers skills without copying their methodology. Use when workflow-control-plane selects full execution_engine=superpowers or lists a specific superpowers:* skill for the active stage, and when outputs must be mapped back to workflow transition results. 当 adaptive 工作流明确选择完整 Superpowers 执行，或当前阶段只需调用某个指定的 Superpowers 原生 skill 时使用。
---

# Superpowers Adapter

你负责契约转换，不负责重写 Superpowers 方法论。

## Role

- Map approved adaptive artifacts into the correct native Superpowers skill input.
- Preserve Superpowers ownership of TDD, systematic debugging, writing plans, executing plans, requesting review, and verification-before-completion.
- Convert Superpowers outputs into `workflow-control-plane` transition requests.

## Never

- Do not copy or summarize full Superpowers procedures into this skill.
- Do not load the whole Superpowers chain for a selective route; invoke only the exact `superpowers:*` skill selected for the active stage.
- Do not bypass native Superpowers stages when `execution_engine=superpowers` and `process_depth=lifecycle`.
- Do not mutate `workflow_manifest.json` directly.
- Do not treat Superpowers local/unit evidence as `handoff_done`.

## Mapping

Use `references/superpowers-mapping.md` before calling a Superpowers execution skill.

General mapping. Apply only the row required by the current stage; do not preload other rows:

- Missing or unclear implementation approach -> `superpowers:brainstorming`.
- Approved spec but no implementation plan -> `superpowers:writing-plans`.
- Written plan ready for execution -> `superpowers:executing-plans`.
- Feature/bugfix where behavior can be tested -> `superpowers:test-driven-development`.
- Failure or unknown cause -> `superpowers:systematic-debugging`.
- Significant diff ready for independent review -> `superpowers:requesting-code-review`.
- Before completion claim -> `superpowers:verification-before-completion`.

## Exit

After the Superpowers step, return a transition request for:

```sh
python3 skills/workflow-control-plane/scripts/transition_workflow.py workflow_manifest.json transition_request.json
```

The transition request must include produced/updated artifacts, evidence refs, claim requests, and any error code. Let `workflow-control-plane` decide whether the stage can advance.
