# Superpowers Mapping

This adapter only maps contracts. The native Superpowers skill remains the owner of its methodology.

Invoke only the exact mapped row selected for the active stage. A lifecycle may use different native methods at different times, but each call remains independent; there is no full Superpowers execution mode.

| Workflow situation | Native Superpowers skill | Input artifact |
| --- | --- | --- |
| Implementation approach is unclear | `superpowers:brainstorming` | route decision, approved spec, constraints |
| Multi-step implementation needed | `superpowers:writing-plans` | approved spec, approved/embedded technical design, evidence plan |
| Written plan ready | `superpowers:executing-plans` | approved implementation plan |
| Feature/bugfix behavior is automatable | `superpowers:test-driven-development` | acceptance criteria, focused validator target |
| Bug/test/CI failure | `superpowers:systematic-debugging` | failure signal, reproduction, logs |
| Major diff needs maker/checker | `superpowers:requesting-code-review` | diff summary, acceptance, evidence manifest |
| Completion claim is about to be made | `superpowers:verification-before-completion` | commands run, evidence ids, remaining gaps |

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
