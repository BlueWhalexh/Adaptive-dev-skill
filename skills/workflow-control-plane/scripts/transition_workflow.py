#!/usr/bin/env python3
"""Apply a transition_request.json to workflow_manifest.json."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from validate_json_artifact import load_json, validate_instance
from validate_workflow_manifest import load_strategy, validate as validate_workflow_manifest


SKILL_DIR = Path(__file__).resolve().parents[1]
REQUEST_SCHEMA = SKILL_DIR / "schemas" / "transition-request.schema.json"
RESULT_SCHEMA = SKILL_DIR / "schemas" / "transition-result.schema.json"
CLAIM_RANK = {"none": 0, "dev_done": 1, "integration_done": 2, "handoff_done": 3}


def result(workflow_id: str, status: str, current_stage: str, workflow_state: str, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    value = {
        "schema_version": 1,
        "workflow_id": workflow_id,
        "status": status,
        "current_stage": current_stage,
        "workflow_state": workflow_state,
        "errors": errors,
        "warnings": warnings,
    }
    schema_errors = validate_instance(value, load_json(RESULT_SCHEMA))
    if schema_errors:
        raise SystemExit("FAIL: invalid transition result: " + "; ".join(schema_errors))
    return value


def next_stage(strategy: dict[str, Any], current_stage: str) -> str:
    stages = strategy["stages"]
    index = stages.index(current_stage)
    return stages[index + 1] if index + 1 < len(stages) else current_stage


def propagate_stale(artifacts: list[dict[str, Any]], changed_ids: set[str]) -> None:
    by_id = {artifact["id"]: artifact for artifact in artifacts}
    reverse: dict[str, list[str]] = defaultdict(list)
    for artifact in artifacts:
        for dep_id in artifact["depends_on"]:
            if dep_id in by_id:
                reverse[dep_id].append(artifact["id"])

    queue: deque[str] = deque(changed_ids)
    seen: set[str] = set()
    while queue:
        source = queue.popleft()
        for downstream_id in reverse[source]:
            if downstream_id in seen:
                continue
            seen.add(downstream_id)
            downstream = by_id[downstream_id]
            if downstream["status"] not in {"missing", "rejected"}:
                downstream["status"] = "stale"
            queue.append(downstream_id)


def apply_transition(manifest: dict[str, Any], request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    errors = validate_instance(request, load_json(REQUEST_SCHEMA))
    if errors:
        return manifest, result(request.get("workflow_id", ""), "rejected", manifest.get("current_stage", ""), manifest.get("workflow_state", "blocked"), errors, [])
    if request["workflow_id"] != manifest["run_id"]:
        return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["RESUME_CONFLICT: workflow_id mismatch"], [])
    for item in manifest.get("transition_log", []):
        if item["transition_id"] == request["transition_id"]:
            return manifest, result(request["workflow_id"], "applied", manifest["current_stage"], manifest["workflow_state"], [], ["duplicate transition_id ignored idempotently"])
    if request["expected_manifest_revision"] != manifest["manifest_revision"]:
        return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["RESUME_CONFLICT: manifest revision mismatch"], [])
    if request["stage_id"] != manifest["current_stage"]:
        return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["RESUME_CONFLICT: stage_id mismatch"], [])

    strategy, strategy_error = load_strategy(manifest["selected_strategy"])
    if strategy_error:
        return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], [strategy_error], [])

    updated = dict(manifest)
    artifacts = [dict(item) for item in manifest["artifacts"]]
    by_id = {item["id"]: item for item in artifacts}
    changed_ids: set[str] = set()

    for change in request["artifact_changes"]:
        artifact = change["artifact"]
        artifact_id = artifact["id"]
        old_digest = by_id.get(artifact_id, {}).get("digest")
        new_digest = artifact.get("digest")
        if artifact_id in by_id:
            by_id[artifact_id].update(artifact)
        else:
            artifacts.append(artifact)
            by_id[artifact_id] = artifact
        if change["change_type"] == "content_changed" and (old_digest != new_digest or old_digest is None):
            changed_ids.add(artifact_id)
    if changed_ids:
        propagate_stale(artifacts, changed_ids)

    requested = manifest["claims"]["requested"]
    for claim in request["claim_requests"]:
        if CLAIM_RANK[claim] > CLAIM_RANK[requested]:
            requested = claim

    state = "active"
    blocked_reason = ""
    transition_status = "applied"
    target_stage = next_stage(strategy, manifest["current_stage"]) if request["status"] == "completed" else manifest["current_stage"]
    if request["status"] in {"blocked", "failed", "human_required"}:
        state = "blocked"
        blocked_reason = (request["error"] or {}).get("code") or request["status"]
        transition_status = "blocked"

    updated["artifacts"] = artifacts
    updated["current_stage"] = target_stage
    updated["routing"] = {
        **manifest["routing"],
        "required_skills": manifest["routing"]["skill_plan"].get(target_stage, []),
    }
    updated["workflow_state"] = state
    updated["manifest_revision"] = manifest["manifest_revision"] + 1
    updated["resume"] = {
        "checkpoint_id": f"cp-{target_stage}",
        "resume_from_stage": target_stage,
        "last_validated_artifact_ids": [item["id"] for item in artifacts if item["status"] in {"ready", "approved"}],
        "blocked_reason": blocked_reason,
    }
    updated["claims"] = {**manifest["claims"], "requested": requested}
    updated["transition_log"] = manifest.get("transition_log", []) + [{"transition_id": request["transition_id"], "stage_id": request["stage_id"], "status": request["status"]}]
    return updated, result(request["workflow_id"], transition_status, target_stage, state, [], [])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="workflow_manifest.json path")
    parser.add_argument("transition_request", help="transition_request.json path")
    parser.add_argument("--output", help="output manifest path; defaults to in-place")
    parser.add_argument("--result", help="optional transition_result.json path")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    manifest = load_json(manifest_path)
    request = load_json(Path(args.transition_request))
    updated, transition_result = apply_transition(manifest, request)
    if transition_result["status"] == "rejected":
        print(json.dumps(transition_result, ensure_ascii=False, indent=2))
        return 1

    output = Path(args.output) if args.output else manifest_path
    output.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    errors = validate_workflow_manifest(output)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    if args.result:
        Path(args.result).write_text(json.dumps(transition_result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(transition_result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
