#!/usr/bin/env python3
"""Validate context runtime audit events."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_SCRIPTS = ROOT / "skills" / "workflow-control-plane" / "scripts"
sys.path.insert(0, str(WORKFLOW_SCRIPTS))

from validate_json_artifact import load_json  # noqa: E402


def validate(path: Path) -> list[str]:
    manifest = load_json(path)
    errors: list[str] = []
    for event in manifest["runtime_audit"]["read_events"]:
        if event["within_allowed_paths"]:
            continue
        if not event["pack_updated_before_use"]:
            errors.append(f"read outside allowed_paths without prior pack update: {event['path']}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    args = parser.parse_args()

    errors = validate(Path(args.manifest))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"Context runtime audit passed: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
