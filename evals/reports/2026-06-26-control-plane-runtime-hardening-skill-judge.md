# Skill Evaluation Report: Adaptive Dev Workflow Runtime Hardening

## Summary

- **Total Score**: 116/120 (96.7%)
- **Grade**: A
- **Pattern**: Navigation + Process runtime
- **Knowledge Ratio**: E:A:R = 88:10:2
- **Verdict**: Production-grade workflow runtime shape; this revision improves runtime trust boundaries rather than adding more methodology text.

## Dimension Scores

| Dimension | Score | Max | Notes |
| --- | ---: | ---: | --- |
| D1: Knowledge Delta | 20 | 20 | Captures non-obvious AI coding runtime invariants: facts vs policy, capability reports, route revision, verifier attestations. |
| D2: Mindset vs Mechanics | 14 | 15 | Strong control-plane thinking; still relies on scripts rather than a full event-sourced runtime. |
| D3: Anti-Pattern Quality | 15 | 15 | Old route cards, self-claims, stale transitions, ontology mixing, and over-process paths are explicit negatives. |
| D4: Specification Compliance | 15 | 15 | Skill frontmatter remains valid; router is 132 lines and narrow. |
| D5: Progressive Disclosure | 14 | 15 | Small router plus references/scripts; references now use the new transition contract. |
| D6: Freedom Calibration | 15 | 15 | Fragile runtime semantics are code/schema-first; task methodology remains in narrow skills/Superpowers. |
| D7: Pattern Recognition | 9 | 10 | Matches official skill composition and Superpowers-style narrow responsibilities. |
| D8: Practical Usability | 14 | 15 | Deterministic evals are strong; full three-repeat fresh-agent eval remains a heavier optional check. |

## What Improved

1. `route_decision.json` now separates ontology cleanly:
   - `work_intent`: implement/debug/review/design/verify/research/handoff
   - `delivery_shape`: none/doc_only/local_change/feature/mvp/spike
   - `change_types`: docs/visual/bugfix/feature/api_contract/migration/refactor

2. Capability detection moved out of the LLM router:
   - New `capability-report.schema.json`
   - New `detect_capabilities.py`
   - Resolver rejects missing required capabilities with `CAPABILITY_MISSING`.

3. Grounding can safely force re-routing:
   - New `route-facts-delta.schema.json`
   - New `apply_route_facts_delta.py`
   - Risk/scope/profile/change-type upgrades are versioned into a new route decision.

4. Transition contract is now runtime-safe:
   - `transition_id`
   - `expected_manifest_revision`
   - `stage_id`
   - `producer`
   - `artifact_changes`
   - idempotent duplicate transition handling
   - stale transition rejection

5. Claims use verifier-issued attestations:
   - `claims.validated[]` now requires `attestation`
   - Attestation binds workflow, claim type, strategy, evidence digest, verifier id/version, and result.
   - Delivery wording avoids implying cryptographic signatures.

## Verified

- `PYTHONPYCACHEPREFIX=/private/tmp/adaptive-skill-pycache python3 -m py_compile scripts/*.py skills/*/scripts/*.py`
- `python3 scripts/run-workflow-e2e-eval.py`
- `python3 scripts/run-skill-sandbox-eval.py`
- `python3 scripts/run-fresh-agent-route-eval.py --repeat 1 --case package-handoff`
- `python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/adaptive-dev-workflow`
- `python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/workflow-control-plane`
- `python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/delivery-verification`
- `git diff --check`

## Remaining Risks

- Fresh-agent eval was run on targeted cases, not full `--repeat 3 --all`.
- Transition idempotency is deterministic but not backed by a real file lock or append-only event log yet.
- Capability detection is intentionally simple; real repos may need provider-specific probes.
- Attestation is structured trust metadata, not cryptographic signing.

## Top 3 Next Improvements

1. Add an append-only `workflow_events.jsonl` and optional lock file for true concurrent writer protection.
2. Expand fresh-agent eval to full three-repeat route stability before the next major release.
3. Add provider-specific capability probes for OpenSpec, repo-native docs, Superpowers version, and project harness version.
