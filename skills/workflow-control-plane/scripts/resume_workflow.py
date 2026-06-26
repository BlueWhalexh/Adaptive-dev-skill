#!/usr/bin/env python3
"""Validate workflow_manifest.json and print the resume checkpoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_json_artifact import load_json
from validate_workflow_manifest import validate as validate_workflow_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="workflow_manifest.json path")
    args = parser.parse_args()

    path = Path(args.manifest)
    errors = validate_workflow_manifest(path)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    manifest = load_json(path)
    print(json.dumps({
        "workflow_id": manifest["run_id"],
        "strategy_id": manifest["selected_strategy"],
        "strategy_version": manifest["strategy_version"],
        "workflow_state": manifest["workflow_state"],
        "resume": manifest["resume"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
