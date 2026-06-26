# Workflow State Machine

`workflow-control-plane` is the sole writer of `workflow_manifest.json`.

## States

- `intake`: route decision is not resolved yet.
- `routed`: strategy is resolved and manifest has been initialized.
- `active`: at least one strategy stage is in progress or completed.
- `blocked`: execution cannot continue without repair, missing capability, or human input.
- `review_ready`: implementation/evidence is ready for delivery review.
- `closed`: validated claim and remaining gaps have been recorded.

## Stage Ownership

Stages are owned by the selected strategy file in `references/strategies/*.json`.
Do not invent global stages such as `SPEC_READY` or `CONTEXT_READY`.

## Writer Rule

Specialist skills must not edit `workflow_manifest.json` directly. They return a transition exit payload:

```json
{
  "status": "completed",
  "produced_artifacts": [],
  "updated_artifacts": [],
  "invalidated_artifacts": [],
  "evidence_refs": [],
  "claim_requests": [],
  "next_recommendation": "",
  "error_code": ""
}
```

Then run `scripts/transition_workflow.py`.

## Resume Rule

Before resuming interrupted work, run:

```sh
python3 skills/workflow-control-plane/scripts/resume_workflow.py workflow_manifest.json
```

Continue from `resume.resume_from_stage` only after validation passes.
