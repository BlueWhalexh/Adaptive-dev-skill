# Error Codes

Use these stable error codes in transition results and user-facing summaries.

| Code | Meaning | Required action |
| --- | --- | --- |
| `ROUTE_AMBIGUOUS` | Route decision has conflicting or insufficient facts. | Ask user or inspect only enough current truth to resolve classification. |
| `CAPABILITY_MISSING` | Required spec system, execution engine, or project harness is unavailable. | Repair harness or downgrade only with explicit user approval. |
| `CONTEXT_GAP` | Context Pack is incomplete, stale, or too broad. | Return to `context-grounding`. |
| `SPEC_GAP` | Product goal, non-goal, or acceptance is missing. | Return to `specflow` or OpenSpec adapter. |
| `DESIGN_GAP` | Required technical design is missing, stale, or unapproved. | Return to `technical-design`. |
| `PLAN_GAP` | Implementation plan cannot be derived from approved artifacts. | Return to planning adapter. |
| `ARTIFACT_STALE` | Upstream artifact changed and downstream artifacts must be stale/rejected. | Invalidate downstream artifacts and rerun required stages. |
| `EVIDENCE_INSUFFICIENT` | Evidence does not prove requested claim. | Return to `delivery-verification` or implementation repair. |
| `CLAIM_NOT_ALLOWED` | Requested claim exceeds strategy ceiling or verifier authority. | Lower claim or gather stronger evidence. |
| `RESUME_CONFLICT` | Resume checkpoint does not match manifest state or transition request. | Inspect manifest and decide whether to restart or repair. |
| `HUMAN_APPROVAL_REQUIRED` | Strategy requires human approval. | Stop and request approval. |
