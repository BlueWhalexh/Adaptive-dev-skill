#!/usr/bin/env python3
"""Static validation for context_manifest.json."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ADAPTIVE_SCRIPTS = ROOT / "skills" / "adaptive-dev-workflow" / "scripts"
ADAPTIVE_SCHEMAS = ROOT / "skills" / "adaptive-dev-workflow" / "schemas"
sys.path.insert(0, str(ADAPTIVE_SCRIPTS))

from validate_json_artifact import load_json, validate_instance  # noqa: E402


BROAD_PATTERNS = {"src/**", "app/**", "packages/**", "**/*", "."}


def validate(path: Path, *, allow_broad: bool = False) -> list[str]:
    manifest = load_json(path)
    schema = load_json(ADAPTIVE_SCHEMAS / "context-manifest.schema.json")
    errors = validate_instance(manifest, schema)
    if errors:
        return errors

    allowed = manifest["allowed_paths"]
    forbidden = set(manifest["forbidden_paths"])
    files = manifest["context_files"]

    if not allowed:
        errors.append("allowed_paths cannot be empty")
    if not files:
        errors.append("context_files cannot be empty")
    if not allow_broad:
        broad = [item for item in allowed if item in BROAD_PATTERNS or item.endswith("/**")]
        if broad:
            errors.append("ordinary context slice cannot use broad paths: " + ", ".join(broad))

    allowed_set = set(allowed)
    for item in files:
        path_value = item["path"]
        if path_value in forbidden:
            errors.append(f"context file is explicitly forbidden: {path_value}")
        if path_value not in allowed_set and not any(path_value.startswith(prefix.rstrip("*")) for prefix in allowed if prefix.endswith("*")):
            errors.append(f"context file is outside allowed_paths: {path_value}")
        if len(item["sha256"]) < 32:
            errors.append(f"context file hash looks invalid: {path_value}")
        if not item["reason"].strip():
            errors.append(f"context file reason is empty: {path_value}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument("--allow-broad", action="store_true", help="Allow broad architecture-scan context paths")
    args = parser.parse_args()

    errors = validate(Path(args.manifest), allow_broad=args.allow_broad)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"Context static validation passed: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
