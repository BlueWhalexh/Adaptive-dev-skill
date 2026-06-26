# Rule Ownership Map

Rules have exactly one owner. Other skills may reference a rule id, but should not duplicate the full rule text.

| Rule id | Owner | Enforcement |
| --- | --- | --- |
| `ROUTE-FACTS-ONLY` | `adaptive-dev-workflow` | `route-decision.schema.json` |
| `CAPABILITY-REPORT-AUTHORITY` | `workflow-control-plane` | `detect_capabilities.py`, `capability-report.schema.json` |
| `ROUTE-FACTS-DELTA` | `workflow-control-plane` | `apply_route_facts_delta.py`, `route-facts-delta.schema.json` |
| `STRATEGY-REGISTRY-AUTHORITY` | `workflow-control-plane` | `resolve_strategy.py`, `validate_strategy_registry.py` |
| `MANIFEST-SOLE-WRITER` | `workflow-control-plane` | `init_workflow.py`, `transition_workflow.py` |
| `TRANSITION-REVISION-GUARD` | `workflow-control-plane` | `transition-request.schema.json`, `transition_workflow.py` |
| `STAGE-FROM-STRATEGY` | `workflow-control-plane` | `validate_workflow_manifest.py` |
| `RESUME-CHECKPOINT-VALID` | `workflow-control-plane` | `resume_workflow.py`, `validate_workflow_manifest.py` |
| `ARTIFACT-STALE-PROPAGATES` | `workflow-control-plane` | `validate_artifact_graph.py` |
| `CLAIM-NO-SELF-SIGN` | `delivery-verification` | `validate_evidence_manifest.py`, verifier registry |
| `CLAIM-VERIFIER-AUTHORITY` | `delivery-verification` | `verifier-registry.json`, workflow manifest validator |
| `CONTEXT-RUNTIME-AUDIT` | `context-grounding` | `validate_context_runtime_audit.py` |
| `DESIGN-DOC-TOPOLOGY` | `technical-design` | `documentation-topology.md`, workflow manifest validator |
| `PROJECT-HARNESS-IDEMPOTENT` | `project-harness-init` | `validate_project_harness.py` |
| `KNOWLEDGE-PROMOTION-CANDIDATE` | `knowledge-promotion` | `validate_learning_candidate.py` |

When adding a new MUST/NEVER rule, update this map and add a deterministic test.
