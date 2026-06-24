#!/usr/bin/env python3
"""Validate learning_candidate.json."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ADAPTIVE_SCRIPTS = ROOT / "skills" / "adaptive-dev-workflow" / "scripts"
ADAPTIVE_SCHEMAS = ROOT / "skills" / "adaptive-dev-workflow" / "schemas"
sys.path.insert(0, str(ADAPTIVE_SCRIPTS))

from validate_json_artifact import load_json, validate_instance  # noqa: E402


SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,80}$")


def validate(path: Path) -> list[str]:
    candidate = load_json(path)
    schema = load_json(ADAPTIVE_SCHEMAS / "learning-candidate.schema.json")
    errors = validate_instance(candidate, schema)
    if errors:
        return errors
    if not SAFE_ID.match(candidate["id"]):
        errors.append(f"unsafe learning candidate id: {candidate['id']}")
    if candidate["promotion_target"] == "general_skill" and candidate["status"] == "promoted":
        errors.append("general_skill promotion requires separate skill eval before status=promoted")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate")
    args = parser.parse_args()

    errors = validate(Path(args.candidate))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"Learning candidate valid: {args.candidate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
