#!/usr/bin/env python3
"""Validate work_result.json, optionally against its work order."""

from __future__ import annotations

import argparse
from pathlib import Path

from _json_contract import load_json, validate_contract


SKILL_DIR = Path(__file__).resolve().parents[1]
SCHEMA = SKILL_DIR / "schemas" / "work-result.schema.json"


def validate(path: Path, *, work_order_path: Path | None = None) -> list[str]:
    result = load_json(path)
    errors = validate_contract(result, SCHEMA)
    if result["status"] in {"blocked", "failed", "needs_human"} and not result.get("error"):
        errors.append(f"{result['status']} result requires error code/message")
    if result["status"] == "completed" and result.get("error") is not None:
        errors.append("completed result must not include error")
    if work_order_path:
        order = load_json(work_order_path)
        for key in ["coordination_id", "work_order_id", "role"]:
            if result[key] != order[key]:
                errors.append(f"work result {key} must match work order")
        expected_type = order["output_contract"]["artifact_type"]
        produced_types = {artifact["type"] for artifact in result.get("produced_artifacts", [])}
        if result["status"] == "completed" and expected_type not in produced_types:
            errors.append(f"completed result must produce expected artifact_type {expected_type!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_result")
    parser.add_argument("--work-order")
    args = parser.parse_args()
    errors = validate(Path(args.work_result), work_order_path=Path(args.work_order) if args.work_order else None)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"Work result valid: {args.work_result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
