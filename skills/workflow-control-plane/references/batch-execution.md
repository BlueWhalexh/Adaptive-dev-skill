# Continuous Batch Execution

READ when `execution_policy.unit=continuous_batch`.

## Core Rule

The route's L2/L3 risk sets final delivery gates. Reclassify each Plan Task locally. Do not copy parent risk into every Task.

Build a batch from consecutive Tasks that share context, ownership, and rollback surface. Stop the batch before a material boundary: public contract, auth/security, data migration, concurrency/idempotency, external side effect, architecture change, or a new unknown.

## Cadence

Within a batch:

1. Select the next Task and its focused signal.
2. Implement the smallest coherent change.
3. Run only that focused signal; RED is required only when automatable behavior or regression value justifies it.
4. Mark the Plan item and keep a short failure note if needed.
5. Continue without a new work order, artifact package, manifest transition, commit, adjacent suite, report, or independent review.

At a batch or milestone checkpoint:

1. Run affected-module and adjacent regression once.
2. Review the combined diff for scope, contracts, side effects, and acceptance coverage once.
3. Request independent review only when `review=batch_risk|boundary_strict` and the changed surface justifies it.
4. Fix Critical/Major or contract-changing findings, then run at most one delta re-review. Minor non-contract findings do not restart the full loop.
5. Commit and summarize once.
6. Update `workflow_manifest.json` only if the Strategy stage advances.

Record one compact checkpoint entry in the progress/evidence surface:

```text
batch_id; task_ids; changed_surfaces; boundary_flags; focused_signals; checkpoint_evidence; review_decision; remaining_gaps
```

This makes task-local risk auditable without creating a new artifact package for every Task.

Review-stage transitions must submit `review_result {pass_number, max_severity, decision}`. The control plane rejects approval with unresolved Major/Critical findings. `changes_requested` returns to the Strategy gate's `repair_stage`; a second pass with findings resets the bounded review cycle but remains `active`. Only a real human/external/capability/risk impasse may become `blocked`.

At completion, use `delivery-verification` for acceptance, integration/E2E/system, fresh consumer, real external, and claim signing. A broad unit suite is not a substitute for the required evidence type.

## Agent Use

Use a fresh reviewer or isolated worktree only for independent high-risk review, parallel work without shared state, or material context-contamination risk. Do not create an implementer/reviewer/fixer chain for every low-risk Task.
