#!/usr/bin/env python3
"""Validate strategy manifests in references/strategies."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from validate_json_artifact import load_json, validate_instance


SKILL_DIR = Path(__file__).resolve().parents[1]
SCHEMA = SKILL_DIR / "schemas" / "strategy.schema.json"
POLICY_SCHEMA = SKILL_DIR / "schemas" / "execution-policy.schema.json"
STRATEGIES = SKILL_DIR / "references" / "strategies"
REQUIRED_IDS = {
    "quick-change",
    "focused-change",
    "sop-guided-change",
    "sop-guided-iteration",
    "root-cause-debug",
    "spec-driven-feature",
    "complex-real-slice",
    "migration-critical",
    "spike",
    "review-only",
}
KNOWN_ARTIFACTS = {
    "analysis_pack",
    "context_manifest",
    "spec",
    "technical_design",
    "plan",
    "task_packet",
    "evidence_manifest",
    "learning_candidate",
    "implementation",
    "decision_record",
}
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,80}$")
VERSION = re.compile(r"^\d+\.\d+(?:\.\d+)?$")
FORBIDDEN_DEFAULT_SKILLS = {
    "superpowers:subagent-driven-development",
    "superpowers:executing-plans",
    "superpowers:verification-before-completion",
    "superpowers:requesting-code-review",
}


def validate(root: Path = STRATEGIES) -> list[str]:
    errors: list[str] = []
    schema = load_json(SCHEMA)
    policy_schema = load_json(POLICY_SCHEMA)
    found: set[str] = set()
    for path in sorted(root.glob("*.json")):
        strategy = load_json(path)
        errors.extend(f"{path.name}: {error}" for error in validate_instance(strategy, schema))
        errors.extend(f"{path.name}.execution_policy: {error}" for error in validate_instance(strategy.get("execution_policy"), policy_schema))
        strategy_id = strategy.get("id")
        if strategy_id != path.stem:
            errors.append(f"{path.name}: strategy id must match file stem")
        if strategy_id in found:
            errors.append(f"duplicate strategy id: {strategy_id}")
        found.add(strategy_id)
        if not SAFE_ID.match(str(strategy_id)):
            errors.append(f"{strategy_id}: strategy id is unsafe")
        if not VERSION.match(str(strategy.get("version", ""))):
            errors.append(f"{strategy_id}: version must be semver-like major.minor[.patch]")
        if not strategy.get("stages"):
            errors.append(f"{strategy_id}: stages cannot be empty")
        if len(strategy.get("stages", [])) != len(set(strategy.get("stages", []))):
            errors.append(f"{strategy_id}: stages must be unique")
        for stage in strategy.get("stages", []):
            if not SAFE_ID.match(str(stage)):
                errors.append(f"{strategy_id}: stage id is unsafe: {stage}")
        for field in ["risk", "modes", "required_artifacts"]:
            values = strategy.get(field, [])
            if len(values) != len(set(values)):
                errors.append(f"{strategy_id}: {field} must not contain duplicates")
        if strategy.get("process_depth") == "direct" and strategy.get("manifest_policy") != "none":
            errors.append(f"{strategy_id}: direct process depth must use manifest_policy=none")
        if strategy.get("process_depth") != "direct" and strategy.get("manifest_policy") != "required":
            errors.append(f"{strategy_id}: selective/lifecycle process depth must require a manifest")
        policy = strategy.get("execution_policy", {})
        if strategy.get("process_depth") == "direct" and policy.get("manifest_updates") != "none":
            errors.append(f"{strategy_id}: direct strategy must not update workflow manifest")
        if strategy.get("process_depth") != "direct" and policy.get("manifest_updates") != "stage_only":
            errors.append(f"{strategy_id}: managed strategy may update workflow manifest only at stage boundaries")
        if policy.get("unit") == "continuous_batch":
            if policy.get("task_exit") != "focused_signal":
                errors.append(f"{strategy_id}: continuous batch requires focused task exit signals")
            if policy.get("checkpoint") not in {"batch", "milestone"}:
                errors.append(f"{strategy_id}: continuous batch checkpoint must be batch or milestone")
            if policy.get("commit") != "batch":
                errors.append(f"{strategy_id}: continuous batch must commit at batch boundaries")
        stages = set(strategy.get("stages", []))
        stage_gates = strategy.get("stage_gates", {})
        unknown_stage_gate_keys = sorted(set(stage_gates) - stages)
        if unknown_stage_gate_keys:
            errors.append(f"{strategy_id}: stage_gates references unknown stages: {', '.join(unknown_stage_gate_keys)}")
        managed_review_stages = {stage for stage in stages if stage == "review" or stage.endswith("_review")}
        if strategy.get("process_depth") != "direct":
            missing_review_gates = sorted(managed_review_stages - set(stage_gates))
            if missing_review_gates:
                errors.append(f"{strategy_id}: managed review stages require stage_gates: {', '.join(missing_review_gates)}")
        for stage, gate in stage_gates.items():
            required_gate_fields = {"allowed_producers", "min_evidence_refs", "review_mode"}
            if gate.get("review_mode") != "none":
                required_gate_fields.add("repair_stage")
            if set(gate) != required_gate_fields:
                errors.append(f"{strategy_id}: stage_gates.{stage} must contain exactly {', '.join(sorted(required_gate_fields))}")
                continue
            if not gate["allowed_producers"] or len(gate["allowed_producers"]) != len(set(gate["allowed_producers"])):
                errors.append(f"{strategy_id}: stage_gates.{stage}.allowed_producers must be non-empty and unique")
            if not isinstance(gate["min_evidence_refs"], int) or isinstance(gate["min_evidence_refs"], bool) or gate["min_evidence_refs"] < 0:
                errors.append(f"{strategy_id}: stage_gates.{stage}.min_evidence_refs must be a non-negative integer")
            if gate["review_mode"] not in {"none", "self", "independent", "human"}:
                errors.append(f"{strategy_id}: stage_gates.{stage}.review_mode is invalid")
            repair_stage = gate.get("repair_stage")
            if repair_stage:
                if repair_stage not in stages:
                    errors.append(f"{strategy_id}: stage_gates.{stage}.repair_stage is not a strategy stage")
                elif strategy["stages"].index(repair_stage) >= strategy["stages"].index(stage):
                    errors.append(f"{strategy_id}: stage_gates.{stage}.repair_stage must precede the review stage")
        stage_skills = strategy.get("stage_skills", {})
        unknown_stage_skill_keys = sorted(set(stage_skills) - stages)
        if unknown_stage_skill_keys:
            errors.append(f"{strategy_id}: stage_skills references unknown stages: {', '.join(unknown_stage_skill_keys)}")
        for stage, skills in stage_skills.items():
            if len(skills) != len(set(skills)):
                errors.append(f"{strategy_id}: stage_skills.{stage} must not contain duplicates")
            forbidden = sorted(set(skills).intersection(FORBIDDEN_DEFAULT_SKILLS))
            if forbidden:
                errors.append(f"{strategy_id}: default strategy must not schedule heavyweight orchestration skills: {', '.join(forbidden)}")
        for stage, gate in stage_gates.items():
            scheduled = set(stage_skills.get(stage, []))
            unsupported = sorted(set(gate.get("allowed_producers", [])) - scheduled - {"human-reviewer", "local-executor"})
            if unsupported:
                errors.append(f"{strategy_id}: stage_gates.{stage} allows unscheduled producers: {', '.join(unsupported)}")
        for rule in strategy.get("conditional_skills", []):
            if not any(rule.get(field) for field in ["change_types", "delivery_shapes", "project_harness_statuses"]):
                errors.append(f"{strategy_id}: conditional skill rule needs at least one routing condition")
            unknown_rule_stages = sorted(set(rule.get("stages", [])) - stages)
            if unknown_rule_stages:
                errors.append(f"{strategy_id}: conditional_skills references unknown stages: {', '.join(unknown_rule_stages)}")
            for field in ["stages", "change_types", "delivery_shapes", "project_harness_statuses", "skills"]:
                values = rule.get(field, [])
                if len(values) != len(set(values)):
                    errors.append(f"{strategy_id}: conditional_skills.{field} must not contain duplicates")
            forbidden = sorted(set(rule.get("skills", [])).intersection(FORBIDDEN_DEFAULT_SKILLS))
            if forbidden:
                errors.append(f"{strategy_id}: conditional rules must not schedule heavyweight orchestration skills: {', '.join(forbidden)}")
        unknown_artifacts = sorted(set(strategy.get("required_artifacts", [])) - KNOWN_ARTIFACTS)
        if unknown_artifacts:
            errors.append(f"{strategy_id}: unknown required_artifacts: {', '.join(unknown_artifacts)}")
        if strategy.get("design_policy") == "standalone" and "technical_design" not in strategy.get("required_artifacts", []):
            errors.append(f"{strategy_id}: standalone design requires technical_design artifact")
        if strategy_id == "quick-change" and strategy.get("design_policy") == "standalone":
            errors.append("quick-change must not require standalone technical design")
        if strategy_id == "complex-real-slice":
            if strategy.get("design_policy") != "standalone":
                errors.append("complex-real-slice must use standalone technical design")
            if strategy.get("design_review") not in {"independent", "human"}:
                errors.append("complex-real-slice requires independent or human design review")
            if set(stage_skills.get("system_verification", [])) != {"change-aware-testing", "delivery-verification"}:
                errors.append("complex-real-slice system verification requires test execution and claim verification")
            if stage_skills.get("delivery_review") != ["agent-orchestration"]:
                errors.append("complex-real-slice delivery boundary requires isolated orchestration")
        if strategy_id == "migration-critical":
            if strategy.get("design_policy") != "standalone" or strategy.get("design_review") != "human":
                errors.append("migration-critical must use standalone technical design with human review")
            if stage_skills.get("negative_tests") != ["change-aware-testing"]:
                errors.append("migration-critical negative test stage requires change-aware-testing")
            if set(stage_skills.get("system_verification", [])) != {"change-aware-testing", "delivery-verification"}:
                errors.append("migration-critical system verification requires test execution and claim verification")
            if stage_skills.get("rollback_review") != ["agent-orchestration"]:
                errors.append("migration-critical rollback boundary requires isolated orchestration")
        if strategy_id == "spike":
            if "decision_record" not in strategy.get("required_artifacts", []):
                errors.append("spike requires decision_record artifact")
            if "implementation" in strategy.get("required_artifacts", []):
                errors.append("spike must not require implementation as design output")

    missing = sorted(REQUIRED_IDS - found)
    if missing:
        errors.append("missing strategy ids: " + ", ".join(missing))
    extra = sorted(found - REQUIRED_IDS)
    if extra:
        errors.append("unexpected strategy ids: " + ", ".join(extra))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(STRATEGIES), help="strategy manifest directory")
    args = parser.parse_args()

    errors = validate(Path(args.root))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"Strategy registry valid: {args.root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
