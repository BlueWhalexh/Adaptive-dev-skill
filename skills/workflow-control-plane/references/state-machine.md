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
  "claim_attestations": [],
  "discovered_facts": {},
  "error": null
}
```

Then run `scripts/transition_workflow.py`.

Only workflow-control-plane computes downstream stale propagation and advances the strategy stage.

需要 delivery claim 的 lifecycle strategy 将 Spec review 批准的 `acceptance_contract` 登记为 canonical artifact：`producer=specflow`、`semantic_owner=spec-review`、依赖 approved `spec`。Evidence 和 attestation 必须引用该 artifact 的固定 path/digest；替代 companion 或删减 acceptance 集合均拒绝。

`delivery-verification` 可在 transition request 中提交由证据清单生成的 `claim_attestations`。最终 stage 只有在 requested claim 已被有效 attestation 覆盖时才能进入 `closed`；实现者或其他 specialist 不能提交签发结果。

Knowledge Promotion 是关闭后的条件动作：仅在重复纠偏、稳定 SOP 或明确学习信号出现时运行，不属于 L3 交付链的强制 stage。

## Review Repair Rule

`max_review_passes` limits repeated Review inside one review cycle; it is not a Goal Mode stop condition. `changes_requested` returns an `active` workflow to the Strategy gate's explicit `repair_stage`, preserves `finding_refs`, and emits `repair_required`. When the bounded pass count is reached, the pass counter resets for the next repaired diff/evidence cycle.

Use `blocked` only when autonomous repair cannot proceed: `human_required`, missing capability or external state, irreversible-risk decision, unresolved permission/security ambiguity, or no executable repair path. Do not block merely because two Review passes found issues.

## Goal Identity Rule

新建 managed workflow 时必须提供稳定的 `goal_id` 和包含批准 scope 的 `goal_summary`。Control plane 规范化后保存 SHA-256 fingerprint。自动 resume 必须重新提供相同 identity；缺失 identity、复用 goal id 但 scope 已变、多个匹配 run 都不能自动恢复。`--allow-unbound` 只用于人工检查旧 manifest，不是自动执行入口。

## Resume Rule

Single-run projects use `.agent/runtime/workflow_manifest.json`; concurrent or historical runs use `.agent/runs/<run-id>/workflow_manifest.json`. A caller must inspect both locations and auto-resume only one compatible active candidate. Multiple compatible candidates require explicit selection.

Before resuming interrupted work, run:

```sh
python3 skills/workflow-control-plane/scripts/resume_workflow.py workflow_manifest.json \
  --goal-id <stable-issue-or-goal-id> --goal-summary "<current goal and scope>"
```

Continue from `resume.resume_from_stage` only after validation passes.
