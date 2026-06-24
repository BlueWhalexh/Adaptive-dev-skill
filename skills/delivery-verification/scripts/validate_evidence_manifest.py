#!/usr/bin/env python3
"""Validate JSON evidence_manifest and requested claim level."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ADAPTIVE_SCRIPTS = ROOT / "skills" / "adaptive-dev-workflow" / "scripts"
ADAPTIVE_SCHEMAS = ROOT / "skills" / "adaptive-dev-workflow" / "schemas"
sys.path.insert(0, str(ADAPTIVE_SCRIPTS))

from validate_json_artifact import load_json, validate_instance  # noqa: E402


CLAIM_REQUIRED_TYPES = {
    "none": set(),
    "dev_done": {
        "unit",
        "manual",
        "diff_review",
        "build",
        "lint",
        "typecheck",
        "integration",
        "e2e",
        "system",
        "fresh_consumer",
        "real_external",
    },
    "integration_done": {"integration", "e2e", "system", "fresh_consumer", "real_external"},
    "handoff_done": {"fresh_consumer", "real_external"},
}


def validate(path: Path) -> list[str]:
    manifest = load_json(path)
    schema = load_json(ADAPTIVE_SCHEMAS / "evidence-manifest.schema.json")
    errors = validate_instance(manifest, schema)
    if errors:
        return errors

    validators = manifest["validators"]
    validator_ids = {item["id"] for item in validators}
    passing_types = {item["type"] for item in validators if item["result"] == "pass"}
    requested = manifest["claim_requested"]

    if requested != "none":
        allowed = CLAIM_REQUIRED_TYPES[requested]
        if not passing_types.intersection(allowed):
            errors.append(f"{requested} requires passing evidence type in {sorted(allowed)}; got {sorted(passing_types)}")

    for coverage in manifest["acceptance_coverage"]:
        missing = [item for item in coverage["validator_ids"] if item not in validator_ids]
        if missing:
            errors.append(f"acceptance {coverage['acceptance_id']} references unknown validators: {', '.join(missing)}")

    if requested in {"integration_done", "handoff_done"} and not manifest["acceptance_coverage"]:
        errors.append(f"{requested} requires acceptance_coverage")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="evidence_manifest.json")
    args = parser.parse_args()

    errors = validate(Path(args.manifest))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"Evidence manifest valid: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
