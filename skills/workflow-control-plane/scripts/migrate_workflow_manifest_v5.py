#!/usr/bin/env python3
"""Migrate an unsigned in-flight v5 manifest to the current strategy contract."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from validate_json_artifact import load_json
from validate_workflow_manifest import load_strategy, validate
from goal_identity import build_goal_identity


FORBIDDEN_LEGACY_METHODS = {
    "superpowers:subagent-driven-development",
    "superpowers:executing-plans",
    "superpowers:verification-before-completion",
    "superpowers:requesting-code-review",
    "superpowers:test-driven-development",
}


def migrate(manifest: dict, goal_id: str, goal_summary: str) -> dict:
    if manifest.get("schema_version") != 5:
        raise ValueError("only workflow manifest schema_version=5 is supported")
    if manifest.get("claims", {}).get("validated"):
        raise ValueError("signed claims cannot be rewritten; archive or re-verify the workflow")
    strategy, error = load_strategy(manifest.get("selected_strategy", ""))
    if error:
        raise ValueError(error)
    stage = manifest.get("current_stage")
    if stage not in strategy["stages"]:
        raise ValueError(f"current stage {stage!r} does not exist in current strategy")

    old_plan = manifest.get("routing", {}).get("skill_plan", {})
    skill_plan: dict[str, list[str]] = {}
    for stage_id in strategy["stages"]:
        skills = list(strategy.get("stage_skills", {}).get(stage_id, []))
        for legacy_skill in old_plan.get(stage_id, []):
            if legacy_skill == "project-harness-init" and legacy_skill not in skills:
                skills.append(legacy_skill)
        skill_plan[stage_id] = [skill for skill in dict.fromkeys(skills) if skill not in FORBIDDEN_LEGACY_METHODS]

    migrated = dict(manifest)
    migrated["schema_version"] = 6
    migrated["goal_identity"] = build_goal_identity(goal_id, goal_summary)
    migrated["strategy_version"] = strategy["version"]
    migrated["skill_suite_version"] = "2026-07-15"
    migrated["routing"] = {
        **manifest["routing"],
        "process_depth": strategy["process_depth"],
        "manifest_policy": strategy["manifest_policy"],
        "execution_engine": strategy["execution_engine"],
        "execution_policy": strategy["execution_policy"],
        "skill_plan": skill_plan,
        "required_skills": skill_plan[stage],
    }
    migrated["review_control"] = {
        "stage_id": "",
        "passes_completed": 0,
        "last_severity": "none",
        "decision": "pending",
        "next_action": "none",
        "repair_stage": "",
        "finding_refs": [],
    }
    recovered_review_limit = manifest.get("workflow_state") == "blocked" and manifest.get("resume", {}).get("blocked_reason") == "REVIEW_LIMIT_REACHED"
    if recovered_review_limit:
        review_stage = manifest.get("review_control", {}).get("stage_id") or stage
        if review_stage not in strategy.get("stage_gates", {}) or strategy["stage_gates"][review_stage].get("review_mode") == "none":
            raise ValueError("legacy REVIEW_LIMIT_REACHED manifest has no recoverable review stage")
        stage = review_stage
        migrated["current_stage"] = stage
        migrated["workflow_state"] = "active"
        migrated["routing"]["required_skills"] = skill_plan[stage]
    migrated["manifest_revision"] = int(manifest.get("manifest_revision", 0)) + 1
    blocked_reason = "" if recovered_review_limit else manifest["resume"].get("blocked_reason", "")
    migrated["resume"] = {**manifest["resume"], "checkpoint_id": f"cp-{stage}", "resume_from_stage": stage, "blocked_reason": blocked_reason}
    return migrated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument("--output", required=True)
    parser.add_argument("--goal-id", required=True, help="stable goal id for exact resume matching")
    parser.add_argument("--goal-summary", required=True, help="approved goal and scope for exact resume matching")
    args = parser.parse_args()
    try:
        source = load_json(Path(args.manifest))
        recovered_review_limit = source.get("workflow_state") == "blocked" and source.get("resume", {}).get("blocked_reason") == "REVIEW_LIMIT_REACHED"
        migrated = migrate(source, args.goal_id, args.goal_summary)
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 1
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output.parent, prefix=f".{output.name}.", suffix=".tmp", delete=False) as handle:
            handle.write(json.dumps(migrated, ensure_ascii=False, indent=2) + "\n")
            temp_path = Path(handle.name)
        errors = validate(temp_path)
        if errors:
            for error in errors:
                print(f"FAIL: {error}")
            return 1
        os.replace(temp_path, output)
        temp_path = None
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
    print(f"Workflow manifest migrated: {output}")
    if recovered_review_limit:
        print("WARNING: legacy review findings were not persisted; workflow reactivated at the review stage to regenerate findings before repair")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
