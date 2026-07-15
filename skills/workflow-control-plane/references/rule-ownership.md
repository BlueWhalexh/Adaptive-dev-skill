# Rule Ownership Map

Rules have exactly one owner. Other skills may reference a rule id, but should not duplicate the full rule text.

| Rule id | Owner | Enforcement |
| --- | --- | --- |
| `ROUTE-FACTS-ONLY` | `adaptive-dev-workflow` | `route-decision.schema.json` |
| `CAPABILITY-REPORT-AUTHORITY` | `workflow-control-plane` | `detect_capabilities.py`, `capability-report.schema.json` |
| `ROUTE-FACTS-DELTA` | `workflow-control-plane` | `apply_route_facts_delta.py`, `route-facts-delta.schema.json` |
| `STRATEGY-REGISTRY-AUTHORITY` | `workflow-control-plane` | `resolve_strategy.py`, `validate_strategy_registry.py` |
| `EXECUTION-CADENCE-AUTHORITY` | `workflow-control-plane` | strategy `execution_policy`, `validate_strategy_registry.py` |
| `TASK-RISK-IS-LOCAL` | `workflow-control-plane` | `batch-execution.md`, sandbox negative evals |
| `MANIFEST-SOLE-WRITER` | `workflow-control-plane` | `init_workflow.py`, `transition_workflow.py` |
| `MANIFEST-MAJOR-MIGRATION` | `workflow-control-plane` | `migrate_workflow_manifest_v5.py` |
| `TRANSITION-REVISION-GUARD` | `workflow-control-plane` | `transition-request.schema.json`, `transition_workflow.py` |
| `STAGE-FROM-STRATEGY` | `workflow-control-plane` | `validate_workflow_manifest.py` |
| `STAGE-COMPLETION-GATE` | `workflow-control-plane` | strategy `stage_gates`, `transition_workflow.py` |
| `RESUME-CHECKPOINT-VALID` | `workflow-control-plane` | `resume_workflow.py`, `validate_workflow_manifest.py` |
| `REVIEW-BOUNDED-REPAIR` | `workflow-control-plane` | `transition_workflow.py`, `review_control` |
| `ARTIFACT-STALE-PROPAGATES` | `workflow-control-plane` | `validate_artifact_graph.py` |
| `CLAIM-NO-SELF-SIGN` | `delivery-verification` | `validate_evidence_manifest.py`, verifier registry |
| `CLAIM-VERIFIER-AUTHORITY` | `delivery-verification` | `verifier-registry.json`, workflow manifest validator |
| `CONTEXT-RUNTIME-AUDIT` | `context-grounding` | `validate_context_runtime_audit.py` |
| `DESIGN-DOC-TOPOLOGY` | `technical-design` | `documentation-topology.md`, workflow manifest validator |
| `PROJECT-HARNESS-IDEMPOTENT` | `project-harness-init` | `validate_project_harness.py` |
| `SPECIALIST-STAGE-ONLY` | `adaptive-dev-workflow` | active-stage `required_skills`, fresh stage-dispatch eval |
| `KNOWLEDGE-PROMOTION-CANDIDATE` | `knowledge-promotion` | `validate_learning_candidate.py` |

When adding a new MUST/NEVER rule, update this map and add a deterministic test.
