#!/usr/bin/env python3
"""Capture a project learning candidate as a small YAML file."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


def q(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--id", help="Candidate id; defaults to timestamp")
    parser.add_argument("--kind", required=True, choices=[
        "sop", "gotcha", "architecture", "testing", "command", "review", "delivery", "quality"
    ])
    parser.add_argument("--statement", required=True)
    parser.add_argument("--trigger", required=True)
    parser.add_argument("--action", required=True)
    parser.add_argument("--source-task", required=True)
    parser.add_argument("--evidence", action="append", default=[], help="Validator or evidence line")
    parser.add_argument("--scope-path", action="append", default=[])
    parser.add_argument("--confidence", default="medium", choices=["low", "medium", "high"])
    parser.add_argument("--risk", default="medium", choices=["low", "medium", "high"])
    parser.add_argument("--destination", default="project-skill", choices=[
        "project-skill", "AGENTS.md", "docs", "script", "ci", "adr", "reference"
    ])
    parser.add_argument("--occurrences", type=int, default=1)
    parser.add_argument("--expires-at", default="")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    now = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    candidate_id = args.id or f"KC-{now}"
    path = root / ".agent" / "knowledge" / "candidates" / f"{candidate_id}.yaml"
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing candidate: {path}")

    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"id: {q(candidate_id)}",
        f"kind: {q(args.kind)}",
        f"statement: {q(args.statement)}",
        "scope:",
        "  paths:",
    ]
    if args.scope_path:
        lines.extend([f"    - {q(item)}" for item in args.scope_path])
    else:
        lines.append("    []")
    lines.extend([
        f"trigger: {q(args.trigger)}",
        f"action: {q(args.action)}",
        "source:",
        f"  task: {q(args.source_task)}",
        "  commit: \"\"",
        "evidence:",
        "  validators:",
    ])
    if args.evidence:
        lines.extend([f"    - {q(item)}" for item in args.evidence])
    else:
        lines.append("    []")
    lines.extend([
        "  result: \"\"",
        f"occurrences: {args.occurrences}",
        f"confidence: {q(args.confidence)}",
        f"risk: {q(args.risk)}",
        f"proposed_destination: {q(args.destination)}",
        f"last_verified_at: {q(dt.date.today().isoformat())}",
        f"expires_at: {q(args.expires_at)}",
        "status: candidate",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
