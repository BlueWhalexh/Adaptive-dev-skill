# Superpowers Mapping

This adapter only maps contracts. The native Superpowers skill remains the owner of its methodology.

Invoke only the exact mapped row selected for the active stage. A lifecycle may use different native methods at different times, but each call remains independent; there is no full Superpowers execution mode.

| Workflow situation | Native Superpowers skill | Input artifact |
| --- | --- | --- |
| Product, architecture, UX, or public-contract decision remains consequentially unresolved | `superpowers:brainstorming` | unresolved decision, constraints, relevant facts |
| Multi-step implementation needed | `superpowers:writing-plans` | approved spec, approved/embedded technical design, evidence plan |
| Strategy explicitly requires strict test-first behavior for a high-regression behavior slice | `superpowers:test-driven-development` | acceptance criteria, behavior slice, focused validator target |
| Bug/test/CI failure | `superpowers:systematic-debugging` | failure signal, reproduction, logs |

An approved Plan normally executes through `execution_policy=single_change|continuous_batch`. Do not infer a native Superpowers execution chain from plan existence, lifecycle depth, or parent risk.

## Output Contract

Return a `transition_request.json` with:

```json
{
  "schema_version": 1,
  "workflow_id": "workflow-001",
  "transition_id": "tr-superpowers-001",
  "expected_manifest_revision": 12,
  "stage_id": "slice_execution",
  "producer": { "skill": "superpowers-adapter", "version": "1.0.0" },
  "status": "completed",
  "artifact_changes": [],
  "evidence_refs": [],
  "claim_requests": [],
  "discovered_facts": {},
  "error": null
}
```

If Superpowers evidence is only unit/mock/fake, do not request `integration_done` or `handoff_done`.
