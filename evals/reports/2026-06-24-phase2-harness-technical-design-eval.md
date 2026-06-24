# Phase 2 Harness + Technical Design Eval

Date: 2026-06-24

Scope: project-harness-init technical design surface, full route eval, and old/new comparison notes.

## Deterministic Sandbox

Command:

```sh
/Library/Developer/CommandLineTools/usr/bin/python3 scripts/run-skill-sandbox-eval.py
```

Exit code: `0`

Output:

```text
Sandbox eval passed
- adaptive SKILL.md lines: 219
- skill packages: 7
- seed cases: 14
- failure cases: 12
- workflow e2e: pass
- fresh agent route eval: skipped (set RUN_FRESH_AGENT_ROUTE_EVAL=1)
- strategy coverage:
  - complex-real-slice: 5
  - migration-critical: 2
  - quick-change: 2
  - review-only: 1
  - root-cause-debug: 2
  - spec-driven-feature: 1
  - spike: 1
```

## Workflow E2E

Command:

```sh
/Library/Developer/CommandLineTools/usr/bin/python3 scripts/run-workflow-e2e-eval.py
```

Exit code: `0`

Output:

```text
Workflow E2E eval passed
- project harness init + validate: pass
- workflow manifest + artifact graph positive/negative checks: pass
- JSON evidence manifest claim checks: pass
- context static/freshness/runtime/sufficiency checks: pass
- learning candidate path-safety checks: pass
- handoff fresh consumer artifact install/import: pass
```

## Handoff Fresh Consumer

Command:

```sh
/Library/Developer/CommandLineTools/usr/bin/python3 scripts/run-handoff-fresh-consumer-eval.py
```

Exit code: `0`

Output:

```text
Fresh consumer handoff eval passed
- artifact: adaptive_handoff_demo-0.1.0-py3-none-any.whl
- consumer import path: /private/var/folders/4r/5743zrt921v1b99syhl998900000ks/T/adaptive-handoff-consumer-wvtjo37b/consumer-venv/lib/python3.9/site-packages/adaptive_handoff_demo/__init__.py
```

## Comparison Notes

- Previous control plane added `workflow_manifest.json`, strategy registry, artifact graph, and verifier-signed claims.
- Phase 2 adds a project-harness surface for Product Spec -> Technical Design -> Implementation Plan.
- Expected improvement: high-risk project initialization no longer collapses product spec and architecture decisions into one fallback design file.
- Guardrail: L0/L1 routing remains unchanged; technical design is only required by strategy/design_control.
