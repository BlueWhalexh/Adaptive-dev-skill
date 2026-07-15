#!/usr/bin/env python3
"""Create workflow_manifest.json from route_decision and resolved_strategy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from resolve_strategy import resolve
from goal_identity import build_goal_identity
from validate_json_artifact import load_json, validate_instance
from validate_workflow_manifest import validate as validate_workflow_manifest


SKILL_DIR = Path(__file__).resolve().parents[1]
RESOLVED_SCHEMA = SKILL_DIR / "schemas" / "resolved-strategy.schema.json"
POLICY_SCHEMA = SKILL_DIR / "schemas" / "execution-policy.schema.json"


def approval_record(review: str) -> dict[str, Any]:
    if review == "none":
        return {"status": "approved", "reviewer": "workflow-control-plane", "reviewer_kind": "agent", "evidence_ids": []}
    if review == "human":
        return {"status": "pending", "reviewer": "human", "reviewer_kind": "human", "evidence_ids": []}
    return {"status": "pending", "reviewer": f"{review}-reviewer", "reviewer_kind": "agent", "evidence_ids": []}


def build_manifest(route: dict[str, Any], resolved: dict[str, Any], workflow_id: str, goal_id: str, goal_summary: str) -> dict[str, Any]:
    if resolved["manifest_policy"] == "none":
        raise ValueError("DIRECT_ROUTE_NO_MANIFEST: execute the direct route without workflow_manifest.json")
    classification = route["classification"]
    first_stage = "ground"
    strategy_path = SKILL_DIR / "references" / "strategies" / f"{resolved['strategy_id']}.json"
    if strategy_path.exists():
        strategy = load_json(strategy_path)
        first_stage = strategy["stages"][0]

    design = resolved["design_control"]
    return {
        "schema_version": 6,
        "skill_suite_version": "2026-07-15",
        "run_id": workflow_id,
        "goal_identity": build_goal_identity(goal_id, goal_summary),
        "manifest_revision": 1,
        "strategy_version": resolved["strategy_version"],
        "workflow_state": "routed",
        "classification": {
            "risk": classification["risk"],
            "mode": classification["work_intent"],
            "scope": classification["scope"],
            "uncertainty": classification["uncertainty"],
            "pattern_familiarity": classification["pattern_familiarity"],
            "profiles": classification["profiles"],
        },
        "routing": {
            "process_depth": resolved["process_depth"],
            "manifest_policy": resolved["manifest_policy"],
            "spec_system": resolved["spec_system"],
            "execution_engine": resolved["execution_engine"],
            "execution_policy": resolved["execution_policy"],
            "strategy_id": resolved["strategy_id"],
            "required_skills": resolved["required_skills"],
            "skill_plan": resolved["skill_plan"],
            "capability_report_ref": resolved["capability_report_ref"],
        },
        "selected_strategy": resolved["strategy_id"],
        "current_stage": first_stage,
        "resume": {
            "checkpoint_id": "cp-init",
            "resume_from_stage": first_stage,
            "last_validated_artifact_ids": [],
            "blocked_reason": "",
        },
        "design_control": {
            "policy": design["policy"],
            "review": design["review"],
            "documentation_topology": design["documentation_topology"],
            "triggers": design["triggers"],
            "approval": approval_record(design["review"]),
        },
        "review_control": {
            "stage_id": "",
            "passes_completed": 0,
            "last_severity": "none",
            "decision": "pending",
            "next_action": "none",
            "repair_stage": "",
            "finding_refs": [],
        },
        "artifacts": [],
        "claims": {"requested": "none", "validated": []},
        "transition_log": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("route_decision", help="route_decision.json path")
    parser.add_argument("--resolved-strategy", help="optional resolved_strategy.json path")
    parser.add_argument("--workflow-id", default="workflow-001", help="safe workflow/run id")
    parser.add_argument("--goal-id", help="stable issue/goal id required for managed workflows")
    parser.add_argument("--goal-summary", help="stable goal statement used for exact resume matching")
    parser.add_argument("--output", required=True, help="workflow_manifest.json path")
    args = parser.parse_args()

    route = load_json(Path(args.route_decision))
    resolved = load_json(Path(args.resolved_strategy)) if args.resolved_strategy else resolve(route, Path(args.route_decision).parent)
    resolved_errors = validate_instance(resolved, load_json(RESOLVED_SCHEMA))
    if "execution_policy" in resolved:
        resolved_errors.extend(validate_instance(resolved["execution_policy"], load_json(POLICY_SCHEMA), "$.execution_policy"))
    if resolved_errors:
        for error in resolved_errors:
            print(f"FAIL: {error}")
        return 1

    try:
        if resolved["manifest_policy"] != "none" and (not args.goal_id or not args.goal_summary):
            raise ValueError("GOAL_IDENTITY_REQUIRED: managed workflows require --goal-id and --goal-summary")
        manifest = build_manifest(route, resolved, args.workflow_id, args.goal_id or args.workflow_id, args.goal_summary or "direct route")
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 1
    output = Path(args.output)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    errors = validate_workflow_manifest(output)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"Workflow initialized: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
