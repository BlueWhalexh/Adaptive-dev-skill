#!/usr/bin/env python3
"""Validate context manifest freshness against the current repo."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_SCRIPTS = ROOT / "skills" / "workflow-control-plane" / "scripts"
sys.path.insert(0, str(WORKFLOW_SCRIPTS))

from validate_json_artifact import load_json  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def current_commit(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "working-tree"


def validate(path: Path, repo_root: Path, *, allow_working_tree: bool = False) -> list[str]:
    manifest = load_json(path)
    errors: list[str] = []
    commit = current_commit(repo_root)
    if manifest["repo_commit"] != commit and not allow_working_tree:
        errors.append(f"repo_commit is stale: manifest={manifest['repo_commit']} current={commit}")

    for item in manifest["context_files"]:
        file_path = repo_root / item["path"]
        if not file_path.exists():
            errors.append(f"context file missing: {item['path']}")
            continue
        actual = sha256(file_path)
        if actual != item["sha256"]:
            errors.append(f"context file hash stale: {item['path']}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--allow-working-tree", action="store_true")
    args = parser.parse_args()

    errors = validate(Path(args.manifest), Path(args.repo_root), allow_working_tree=args.allow_working_tree)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"Context freshness validation passed: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
