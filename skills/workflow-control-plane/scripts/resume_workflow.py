#!/usr/bin/env python3
"""Validate workflow_manifest.json and print the resume checkpoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_json_artifact import load_json
from validate_workflow_manifest import validate as validate_workflow_manifest
from goal_identity import build_goal_identity


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="workflow_manifest.json path")
    parser.add_argument("--goal-id")
    parser.add_argument("--goal-summary")
    parser.add_argument("--allow-unbound", action="store_true", help="manually inspect a legacy manifest without exact goal matching")
    args = parser.parse_args()

    path = Path(args.manifest)
    errors = validate_workflow_manifest(path)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    manifest = load_json(path)
    if bool(args.goal_id) != bool(args.goal_summary):
        print("FAIL: --goal-id and --goal-summary must be provided together")
        return 1
    if args.goal_id and args.goal_summary:
        try:
            expected = build_goal_identity(args.goal_id, args.goal_summary)
        except ValueError as exc:
            print(f"FAIL: {exc}")
            return 1
        actual = manifest.get("goal_identity") or {}
        if actual.get("goal_id") != expected["goal_id"] or actual.get("fingerprint") != expected["fingerprint"]:
            print("FAIL: GOAL_IDENTITY_MISMATCH: manifest belongs to a different goal or materially changed scope")
            return 1
    elif not args.allow_unbound:
        print("FAIL: exact goal identity is required for automatic resume; use --allow-unbound only for manual legacy inspection")
        return 1
    if manifest["workflow_state"] not in {"active", "review_ready"} and not args.allow_unbound:
        print(f"FAIL: workflow_state={manifest['workflow_state']} is not auto-resumable")
        return 1
    print(json.dumps({
        "workflow_id": manifest["run_id"],
        "strategy_id": manifest["selected_strategy"],
        "strategy_version": manifest["strategy_version"],
        "workflow_state": manifest["workflow_state"],
        "goal_identity": manifest.get("goal_identity"),
        "resume": manifest["resume"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
