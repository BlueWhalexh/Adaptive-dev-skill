# Control Plane Refactor Comparison

Date: 2026-06-23

## Summary

This report compares the pre-refactor baseline at `/private/tmp/adaptive-skill-baseline-current/` with the current candidate worktree.

The candidate replaces the old route-card model with:

```text
Router + Strategy Registry + Artifact Graph + Verifier-signed Claims + Eval Harness
```

## Baseline

Command:

```sh
python3 scripts/run-skill-sandbox-eval.py
python3 scripts/run-workflow-e2e-eval.py
```

Observed:

- Sandbox eval: pass.
- Workflow E2E eval: pass.
- `adaptive-dev-workflow/SKILL.md`: 317 lines.
- Seed cases: 11.
- Failure cases: 7.
- Model protected: `Tiny/Small/Debug/Medium/Large/OpenSpec`, `route_card`, `evidence_card`, `claim_ceiling`.

## Candidate

Commands:

```sh
PYTHONPYCACHEPREFIX=/private/tmp/adaptive-skill-pycache python3 -m py_compile scripts/*.py skills/*/scripts/*.py
python3 scripts/run-skill-sandbox-eval.py
python3 scripts/run-workflow-e2e-eval.py
python3 scripts/run-handoff-fresh-consumer-eval.py
```

Observed:

- Sandbox eval: pass.
- Workflow E2E eval: pass.
- Fresh consumer handoff eval: pass.
- `adaptive-dev-workflow/SKILL.md`: 194 lines.
- Skill packages: 6.
- Seed cases: 14.
- Failure cases: 8.
- Model protected: `classification/routing`, strategy registry, JSON workflow manifest, artifact graph, JSON evidence manifest, context static/freshness/runtime/sufficiency checks, learning candidate path safety.

## Fresh-Agent Route Eval

All listed cases were run with `--repeat 3` using fresh `codex exec --ephemeral --sandbox read-only` sessions.

Passed groups:

```sh
python3 scripts/run-fresh-agent-route-eval.py --repeat 3 --case tiny-readme-command --case debug-ci
python3 scripts/run-fresh-agent-route-eval.py --repeat 3 --case specflow-intent-to-spec --case complex-frontend-context-pack
python3 scripts/run-fresh-agent-route-eval.py --repeat 3 --case large-permission-model --case spike-unknown-architecture --case migration-critical-data
python3 scripts/run-fresh-agent-route-eval.py --repeat 3 --case package-handoff --case review-only-no-edit
```

Result:

- High-risk strategy recall: pass for package handoff, permission migration, complex context pack, spike payment architecture, and data migration.
- Completion overclaim: 0; route-only evals consistently request `claims.requested=none`.
- Wrong downstream strategy: 0 after correcting SpecFlow/context-stage and migration/spike boundaries.
- L0/L1 complex over-trigger: 0 for README and review-only cases.

## Skill-Judge Review

Manual application of `skill-judge` criteria:

| Dimension | Score | Max | Notes |
| --- | ---: | ---: | --- |
| Knowledge Delta | 18 | 20 | Strong expert control-plane concepts; minimal generic coding advice remains. |
| Mindset + Procedures | 14 | 15 | Good split between decision model and exact validators. |
| Anti-Patterns | 13 | 15 | Stop gates and deprecations are concrete; narrow skills could add more explicit NEVER lists later. |
| Specification Compliance | 15 | 15 | Valid frontmatter; descriptions include English/Chinese triggers. |
| Progressive Disclosure | 14 | 15 | Main skill is 194 lines and delegates to narrow skills; references are no longer stale. |
| Freedom Calibration | 14 | 15 | Low freedom for JSON artifacts, medium freedom for routing judgment. |
| Pattern Recognition | 9 | 10 | Follows Process + Navigation hybrid. |
| Practical Usability | 14 | 15 | Deterministic validators and fresh-agent evals make behavior testable. |

Total: 111/120, Grade A.

## Remaining Risks

- Fresh-agent eval is semantic and slow; the script now supports repeat and grouping, but not parallel execution.
- Fresh route eval validates strategy and claim behavior; real external handoff still must be proven in the concrete project.
- `project-harness-init` is still compatible with the previous harness surface and should be separately slimmed if it grows further.

## Decision

Adopt the candidate. It reduces main-router size, removes deprecated card validators, improves artifact verifiability, and strengthens high-risk route recall without forcing heavy process onto L0/L1 tasks.
