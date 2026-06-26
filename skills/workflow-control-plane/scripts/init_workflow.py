#!/usr/bin/env python3
"""Create workflow_manifest.json from route_decision and resolved_strategy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from resolve_strategy import resolve
from validate_json_artifact import load_json, validate_instance
from validate_workflow_manifest import validate as validate_workflow_manifest


SKILL_DIR = Path(__file__).resolve().parents[1]
RESOLVED_SCHEMA = SKILL_DIR / "schemas" / "resolved-strategy.schema.json"


def approval_record(review: str) -> dict[str, Any]:
    if review == "none":
        return {"status": "approved", "reviewer": "workflow-control-plane", "reviewer_kind": "agent", "evidence_ids": []}
    if review == "human":
        return {"status": "pending", "reviewer": "human", "reviewer_kind": "human", "evidence_ids": []}
    return {"status": "pending", "reviewer": f"{review}-reviewer", "reviewer_kind": "agent", "evidence_ids": []}


def build_manifest(route: dict[str, Any], resolved: dict[str, Any], workflow_id: str) -> dict[str, Any]:
    classification = route["classification"]
    first_stage = "ground"
    strategy_path = SKILL_DIR / "references" / "strategies" / f"{resolved['strategy_id']}.json"
    if strategy_path.exists():
        strategy = load_json(strategy_path)
        first_stage = strategy["stages"][0]

    design = resolved["design_control"]
    return {
        "schema_version": 3,
        "skill_suite_version": "2026-06-26",
        "run_id": workflow_id,
        "manifest_revision": 1,
        "strategy_version": resolved["strategy_version"],
        "workflow_state": "routed",
        "classification": {
            "risk": classification["risk"],
            "mode": classification["work_intent"],
            "scope": classification["scope"],
            "uncertainty": classification["uncertainty"],
            "profiles": classification["profiles"],
        },
        "routing": {
            "spec_system": resolved["spec_system"],
            "execution_engine": resolved["execution_engine"],
            "strategy_id": resolved["strategy_id"],
            "required_skills": resolved["required_skills"],
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
        "artifacts": [],
        "claims": {"requested": "none", "validated": []},
        "transition_log": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("route_decision", help="route_decision.json path")
    parser.add_argument("--resolved-strategy", help="optional resolved_strategy.json path")
    parser.add_argument("--workflow-id", default="workflow-001", help="safe workflow/run id")
    parser.add_argument("--output", required=True, help="workflow_manifest.json path")
    args = parser.parse_args()

    route = load_json(Path(args.route_decision))
    resolved = load_json(Path(args.resolved_strategy)) if args.resolved_strategy else resolve(route, Path(args.route_decision).parent)
    resolved_errors = validate_instance(resolved, load_json(RESOLVED_SCHEMA))
    if resolved_errors:
        for error in resolved_errors:
            print(f"FAIL: {error}")
        return 1

    manifest = build_manifest(route, resolved, args.workflow_id)
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
