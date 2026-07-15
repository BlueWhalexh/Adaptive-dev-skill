#!/usr/bin/env python3
"""Print a compact status summary for workflow_manifest.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_json_artifact import load_json
from validate_workflow_manifest import validate as validate_workflow_manifest


def summarize(manifest: dict) -> dict:
    artifacts = manifest["artifacts"]
    return {
        "run_id": manifest["run_id"],
        "goal_identity": manifest.get("goal_identity"),
        "workflow_state": manifest["workflow_state"],
        "strategy": f"{manifest['selected_strategy']}@{manifest['strategy_version']}",
        "current_stage": manifest["current_stage"],
        "resume_from_stage": manifest["resume"]["resume_from_stage"],
        "artifact_counts": {
            status: sum(1 for artifact in artifacts if artifact["status"] == status)
            for status in ["missing", "draft", "ready", "approved", "stale", "rejected"]
        },
        "claim_requested": manifest["claims"]["requested"],
        "validated_claims": [item["claim"] for item in manifest["claims"]["validated"] if item["status"] == "validated"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="workflow_manifest.json path")
    parser.add_argument("--validate", action="store_true", help="validate before printing")
    args = parser.parse_args()

    path = Path(args.manifest)
    if args.validate:
        errors = validate_workflow_manifest(path)
        if errors:
            for error in errors:
                print(f"FAIL: {error}")
            return 1
    print(json.dumps(summarize(load_json(path)), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
