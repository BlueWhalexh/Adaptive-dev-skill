#!/usr/bin/env python3
"""Create a deterministic capability_report.json for strategy resolution."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from validate_json_artifact import load_json, validate_instance


SKILL_DIR = Path(__file__).resolve().parents[1]
SCHEMA = SKILL_DIR / "schemas" / "capability-report.schema.json"


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def git_revision(root: Path) -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def detect(root: Path) -> dict[str, Any]:
    openspec_evidence = [path for path in [root / "openspec" / "config.yaml", root / "openspec" / "changes"] if path.exists()]
    repo_native_evidence = [path for path in [root / "docs" / "superpowers" / "specs", root / "docs" / "superpowers" / "plans"] if path.exists()]
    harness_evidence = [path for path in [root / "AGENTS.md", root / ".agent"] if path.exists()]
    superpowers_path = Path.home() / ".codex" / "superpowers" / "skills"
    report = {
        "schema_version": 1,
        "repo_revision": git_revision(root),
        "spec_systems": [
            {"id": "openspec", "status": "available" if openspec_evidence else "missing", "evidence": [rel(path, root) for path in openspec_evidence]},
            {"id": "repo_native", "status": "available" if repo_native_evidence else "missing", "evidence": [rel(path, root) for path in repo_native_evidence]},
            {"id": "fallback", "status": "available", "evidence": ["workflow-control-plane fallback"]},
        ],
        "execution_engines": [
            {"id": "local", "status": "available", "version": "builtin"},
            {"id": "superpowers", "status": "available" if superpowers_path.exists() else "missing", "version": "unknown"},
        ],
        "project_harness": {
            "status": "present" if harness_evidence else "missing",
            "version": "unknown",
            "evidence": [rel(path, root) for path in harness_evidence],
        },
    }
    errors = validate_instance(report, load_json(SCHEMA))
    if errors:
        raise SystemExit("FAIL: invalid capability report: " + "; ".join(errors))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root to inspect")
    parser.add_argument("--output", required=True, help="capability_report.json path")
    args = parser.parse_args()

    report = detect(Path(args.root).resolve())
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Capability report written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
