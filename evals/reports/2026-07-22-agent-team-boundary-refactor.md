# Agent Team Boundary Refactor Eval

## Result

- Skill Judge initial: `105/120 (B)`.
- Skill Judge after reference, trigger, and reviewer-contract fixes: `108/120 (A)`.
- Metadata-only trigger eval: `6/6 passed`.
- Loaded-skill collaboration eval: `6/6 passed`; corrected two invalid expected fixtures and reran them twice.
- Deterministic orchestration E2E: passed, including missing/blank reviewer input negatives.
- Adaptive outcome contract: passed (`145` lines, `16` cases, activation `8/8`).
- `quick_validate.py`: Adaptive and Agent Orchestration both valid.

## Behavioral Boundary

| Scenario | Expected behavior |
| --- | --- |
| README or local reversible fix | One writer, focused validation, no orchestration, no independent reviewer |
| High-risk implementation | One maker plus one independent read-only checker; no orchestration skill or reviewer worktree |
| Two independent writers | Agent Orchestration may activate with isolated ownership |
| Three or more coordinated roles/sessions | Agent Orchestration activates when handoff management adds value |
| Shared schema/write state | Team may coordinate, but writers execute sequentially |
| Long-goal milestone already implemented | One independent checker, zero active writers, no full team |

## Closed Findings

1. Replaced implicit `workflow_manifest.json` coupling with `coordination_id` and optional `artifact_index.json`.
2. Added conditional loading routes for all references.
3. Added metadata-only trigger eval and included it in the Skill validation gate.
4. Narrowed frontmatter to exclude one maker plus one checker.
5. Added explicit `packet_kind` and machine-enforced reviewer acceptance, target, and evidence refs.
6. Kept Reviewer/Verifier read-only and worktree-free; concurrent writers still require isolated ownership.

## Residual Limits

- Metadata-only eval measures whether the frontmatter is discriminative; host-level Skill loading is still controlled by the Codex runtime.
- The Skill cannot guarantee persistent Agent reuse or prompt-cache savings. It controls role contracts and context projection, not runtime implementation.
- Worktree cleanup remains an orchestrator responsibility because automatic deletion must inspect unmerged changes.
