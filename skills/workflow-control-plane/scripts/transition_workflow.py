#!/usr/bin/env python3
"""Apply a transition_request.json to workflow_manifest.json."""

from __future__ import annotations

import argparse
import json
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


def apply_transition(manifest: dict[str, Any], request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    errors = validate_instance(request, load_json(REQUEST_SCHEMA))
    if errors:
        return manifest, result(request.get("workflow_id", ""), "rejected", manifest.get("current_stage", ""), manifest.get("workflow_state", "blocked"), errors, [])
    if request["workflow_id"] != manifest["run_id"]:
        return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["RESUME_CONFLICT: workflow_id mismatch"], [])
    if request["from_stage"] != manifest["current_stage"]:
        return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["RESUME_CONFLICT: from_stage mismatch"], [])

    strategy, strategy_error = load_strategy(manifest["selected_strategy"])
    if strategy_error:
        return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], [strategy_error], [])
    if request["to_stage"] not in strategy["stages"]:
        return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["INVALID_STAGE: to_stage not in selected strategy"], [])

    updated = dict(manifest)
    artifacts = [dict(item) for item in manifest["artifacts"]]
    by_id = {item["id"]: item for item in artifacts}
    exit_payload = request["exit"]
    warnings: list[str] = []

    for artifact_id in exit_payload["invalidated_artifacts"]:
        if artifact_id in by_id:
            by_id[artifact_id]["status"] = "stale"
        else:
            warnings.append(f"unknown invalidated artifact ignored: {artifact_id}")
    for artifact in exit_payload["updated_artifacts"]:
        if artifact.get("id") not in by_id:
            warnings.append(f"updated artifact did not exist; adding: {artifact.get('id')}")
            artifacts.append(artifact)
        else:
            by_id[artifact["id"]].update(artifact)
    for artifact in exit_payload["produced_artifacts"]:
        if artifact.get("id") in by_id:
            warnings.append(f"produced artifact replaced existing id: {artifact.get('id')}")
            by_id[artifact["id"]].update(artifact)
        else:
            artifacts.append(artifact)

    requested = manifest["claims"]["requested"]
    for claim in exit_payload["claim_requests"]:
        if CLAIM_RANK[claim] > CLAIM_RANK[requested]:
            requested = claim

    state = "active"
    blocked_reason = ""
    transition_status = "applied"
    if exit_payload["status"] in {"blocked", "failed", "human_required"}:
        state = "blocked"
        blocked_reason = exit_payload["error_code"] or exit_payload["status"]
        transition_status = "blocked"

    updated["artifacts"] = artifacts
    updated["current_stage"] = request["to_stage"]
    updated["workflow_state"] = state
    updated["resume"] = {
        "checkpoint_id": f"cp-{request['to_stage']}",
        "resume_from_stage": request["to_stage"],
        "last_validated_artifact_ids": [item["id"] for item in artifacts if item["status"] in {"ready", "approved"}],
        "blocked_reason": blocked_reason,
    }
    updated["claims"] = {**manifest["claims"], "requested": requested}
    return updated, result(request["workflow_id"], transition_status, request["to_stage"], state, [], warnings)


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
