# Workflow State Machine

`workflow-control-plane` is the sole writer of `workflow_manifest.json`.

## States

- `intake`: route decision is not resolved yet.
- `routed`: strategy is resolved and manifest has been initialized.
- `active`: at least one strategy stage is in progress or completed.
- `blocked`: execution cannot continue autonomously because it needs human/external input, a missing capability, or a decision across an irreversible or security-sensitive boundary. Ordinary repairable findings stay `active`.
- `review_ready`: implementation/evidence is ready for delivery review.
- `closed`: validated claim and remaining gaps have been recorded.

## Stage Ownership

Stages are owned by the selected strategy file in `references/strategies/*.json`.
Do not invent global stages such as `SPEC_READY` or `CONTEXT_READY`.

## Writer Rule

Specialist skills must not edit `workflow_manifest.json` directly. They return a revision-checked `transition_request.json`:

```json
{
  "schema_version": 1,
  "workflow_id": "workflow-001",
  "transition_id": "tr-042",
  "expected_manifest_revision": 12,
  "stage_id": "technical_design",
  "producer": { "skill": "technical-design", "version": "1.0.0" },
  "status": "completed",
  "artifact_changes": [],
  "evidence_refs": [],
  "claim_requests": [],
  "discovered_facts": {},
  "error": null
}
```

Then run `scripts/transition_workflow.py`.

Only workflow-control-plane computes downstream stale propagation and advances the strategy stage.

## Review Repair Rule

`max_review_passes` limits repeated Review inside one review cycle; it is not a Goal Mode stop condition. `changes_requested` returns an `active` workflow to the Strategy gate's explicit `repair_stage`, preserves `finding_refs`, and emits `repair_required`. When the bounded pass count is reached, the pass counter resets for the next repaired diff/evidence cycle.

Use `blocked` only when autonomous repair cannot proceed: `human_required`, missing capability or external state, irreversible-risk decision, unresolved permission/security ambiguity, or no executable repair path. Do not block merely because two Review passes found issues.

## Resume Rule

Before resuming interrupted work, run:

```sh
python3 skills/workflow-control-plane/scripts/resume_workflow.py workflow_manifest.json
```

Continue from `resume.resume_from_stage` only after validation passes.
