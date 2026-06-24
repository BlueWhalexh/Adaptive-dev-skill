#!/usr/bin/env python3
"""Validate strategy manifests in references/strategies."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from validate_json_artifact import load_json, validate_instance


SKILL_DIR = Path(__file__).resolve().parents[1]
SCHEMA = SKILL_DIR / "schemas" / "strategy.schema.json"
STRATEGIES = SKILL_DIR / "references" / "strategies"
REQUIRED_IDS = {
    "quick-change",
    "focused-change",
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


def validate(root: Path = STRATEGIES) -> list[str]:
    errors: list[str] = []
    schema = load_json(SCHEMA)
    found: set[str] = set()
    for path in sorted(root.glob("*.json")):
        strategy = load_json(path)
        errors.extend(f"{path.name}: {error}" for error in validate_instance(strategy, schema))
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
        for field in ["risk", "modes", "required_artifacts", "required_skills"]:
            values = strategy.get(field, [])
            if len(values) != len(set(values)):
                errors.append(f"{strategy_id}: {field} must not contain duplicates")
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
        if strategy_id == "migration-critical":
            if strategy.get("design_policy") != "standalone" or strategy.get("design_review") != "human":
                errors.append("migration-critical must use standalone technical design with human review")
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
