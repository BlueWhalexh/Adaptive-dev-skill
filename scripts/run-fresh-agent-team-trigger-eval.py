#!/usr/bin/env python3
"""Evaluate Agent Team activation from frontmatter metadata only."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals" / "agent-team-cases.json"
SKILL = ROOT / "skills" / "agent-orchestration" / "SKILL.md"

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["activate", "reason"],
    "properties": {
        "activate": {"type": "boolean"},
        "reason": {"type": "string"},
    },
}


def description() -> str:
    lines = SKILL.read_text(encoding="utf-8").splitlines()
    return next(line.removeprefix("description: ") for line in lines if line.startswith("description: "))


def load_cases() -> dict[str, dict[str, Any]]:
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    return {case["id"]: case for case in payload["cases"]}


def run_agent(case: dict[str, Any], codex_bin: str, timeout: int) -> dict[str, Any]:
    prompt = f"""You are evaluating skill discovery from metadata only. Do not read repository files or use tools.

Available skill metadata:
name: agent-orchestration
description: {description()}

User task:
{case['prompt']}

Should this skill be activated? Apply both positive and negative trigger clauses. Return only JSON.
"""
    with tempfile.TemporaryDirectory(prefix="agent-team-trigger-") as tmp:
        root = Path(tmp)
        schema = root / "schema.json"
        output = root / "output.json"
        schema.write_text(json.dumps(OUTPUT_SCHEMA), encoding="utf-8")
        cmd = [codex_bin, "exec", "--ephemeral", "--sandbox", "read-only", "-C", str(ROOT), "--output-schema", str(schema), "--output-last-message", str(output), prompt]
        result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)
        if result.returncode != 0:
            raise RuntimeError(result.stdout)
        return json.loads(output.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", dest="case_ids")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    cases = load_cases()
    selected = args.case_ids or list(cases)
    failed = 0
    for case_id in selected:
        case = cases[case_id]
        for run in range(1, args.repeat + 1):
            actual = run_agent(case, args.codex_bin, args.timeout)
            expected = case["use_orchestration_skill"]
            failures = [] if actual.get("activate") == expected else [f"activate: expected {expected}, got {actual.get('activate')}"]
            failed += bool(failures)
            print(json.dumps({"case": case_id, "run": run, "status": "PASS" if not failures else "FAIL", "actual": actual, "failures": failures}, ensure_ascii=False), flush=True)
    print(f"SUMMARY: runs={len(selected) * args.repeat} failed={failed}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
