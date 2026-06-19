# Quality Feedback Loop

READ when: the user expresses dissatisfaction with output quality, says the work is incomplete or not aligned, repeatedly corrects route/test/docs choices, or asks the skill to learn from development failures.

DO NOT READ for ordinary review comments that are narrow and already actionable.

## Contents

- Trigger Signals
- Recovery Routing
- Failure Case
- Escalation Rules
- Repair Loop
- Skill Or Project Learning
- NEVER

## Trigger Signals

Treat these as quality feedback, not just conversation sentiment:

- "quality is not good", "too rough", "not complete", "missed the point"
- "you did not consider enough", "process is wrong", "verification is not enough"
- "this is over-engineered", "this is too heavy", "you skipped tests"
- "not production-level", "not deliverable", "mock is not real"
- Repeated user corrections about docs, tests, architecture, handoff, or route choice.

## Recovery Routing

On quality dissatisfaction, first classify the failure:

| Failure Type | Symptom | Immediate Action |
| --- | --- | --- |
| Spec gap | Agent solved the wrong or incomplete problem | Restate objective, scope, acceptance, non-goals |
| Grounding gap | Agent missed current code/docs/runtime truth | Re-read current truth before more edits |
| Route gap | Process was too heavy or too light | Re-route and record expected route |
| Evidence gap | Claim exceeded tests/evidence | Build evidence matrix and lower claim ceiling |
| Review gap | Self-review missed risks | Add isolated reviewer or `requesting-code-review` |
| Handoff gap | Output worked only in producer context | Use production handoff gate |
| Project memory gap | User had to repeat project-specific knowledge | Capture learning candidate |

Do not continue adding implementation until the failure class is identified.

## Failure Case

When the same failure could recur, capture a minimal case:

```yaml
id:
date:
raw_user_signal:
task_summary:
expected_behavior:
actual_behavior:
failure_type: spec | grounding | route | evidence | review | handoff | project_memory
impact: low | medium | high
root_cause:
missed_gate:
required_change:
candidate_destination: adaptive-skill | project-skill | AGENTS.md | docs | script | ci | none
status: captured | promoted | rejected
```

Use project-local `.agent/evals/failure-cases.yaml` for project failures. Use this skill's `evals/failure-cases.yaml` only when the failure is general to adaptive routing.

## Escalation Rules

| Signal | Action |
| --- | --- |
| First dissatisfaction | Re-ground, classify failure, repair with explicit evidence |
| Same failure class twice | Upgrade one process level or add the missing gate for this task |
| Same failure class three times | Enter Recovery Mode; stop implementation until spec/evidence/review plan is reset |
| Evidence-related dissatisfaction | Build or update an evidence matrix before more code |
| Docs/architecture dissatisfaction | Load `complex-project-harness.md` and repair current-truth docs |
| Delivery/handoff dissatisfaction | Load `production-handoff-gate.md` |
| Project-memory dissatisfaction | Load `project-skill-lifecycle.md` and capture a candidate |

## Repair Loop

Bound repair loops to avoid thrashing:

```text
1. Acknowledge the concrete gap without over-apologizing.
2. Identify the failure class.
3. Re-state the corrected objective and claim ceiling.
4. Select the new gate or supporting skill.
5. Repair the smallest scope that addresses the failure.
6. Run the evidence that would have caught the issue.
7. Capture a candidate only if the lesson is reusable.
```

If two repair loops fail to resolve the same issue, pause and ask for a human decision or narrower scope.

## Skill Or Project Learning

Choose the learning target carefully:

| Root Cause | Learning Target |
| --- | --- |
| General adaptive misroute | update this skill's eval case and smallest routing rule |
| Project-specific missing command or SOP | project skill candidate |
| Stable repo invariant | `AGENTS.md` or nested `AGENTS.md` candidate |
| Mechanical repeated failure | script/hook/CI |
| One-off misunderstanding | no durable rule; repair only |

## NEVER

- NEVER treat user dissatisfaction as only style preference when it mentions tests, docs, delivery, architecture, or correctness.
- NEVER patch more code before classifying a serious quality failure.
- NEVER hide a lowered claim ceiling.
- NEVER convert a single subjective preference into global skill policy.
- NEVER let repeated dissatisfaction proceed without recording a failure case or changing the gate.
