#!/usr/bin/env python3
"""Deterministic sufficiency check for Spec + Context Pack."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ADAPTIVE_SCRIPTS = ROOT / "skills" / "adaptive-dev-workflow" / "scripts"
sys.path.insert(0, str(ADAPTIVE_SCRIPTS))

from validate_json_artifact import load_json  # noqa: E402


def validate(manifest_path: Path, spec_path: Path | None) -> list[str]:
    manifest = load_json(manifest_path)
    errors: list[str] = []
    if spec_path and not spec_path.exists():
        errors.append(f"spec input missing: {spec_path}")
    if not manifest["allowed_paths"]:
        errors.append("fresh plan agent would have no allowed_paths")
    if not manifest["context_files"]:
        errors.append("fresh plan agent would have no file slices")
    if any(path.endswith("/**") for path in manifest["allowed_paths"]):
        errors.append("fresh plan agent would receive broad wildcard context, not a precise slice")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument("--spec", default=None)
    args = parser.parse_args()

    errors = validate(Path(args.manifest), Path(args.spec) if args.spec else None)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"Context sufficiency eval passed: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
