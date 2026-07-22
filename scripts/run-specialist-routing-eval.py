#!/usr/bin/env python3
"""Fresh-agent eval for lightweight brainstorming and TDD activation."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals" / "specialist-routing-cases.json"

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["brainstorming", "tdd", "design_document", "independent_review", "reason"],
    "properties": {
        "brainstorming": {"type": "boolean"},
        "tdd": {"type": "boolean"},
        "design_document": {"type": "boolean"},
        "independent_review": {"type": "boolean"},
        "reason": {"type": "string"},
    },
}


def load_cases() -> dict[str, dict[str, Any]]:
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    return {case["id"]: case for case in payload["cases"]}


def prompt_for(case: dict[str, Any]) -> str:
    return f"""You are a fresh routing evaluator. Do not edit files or implement the task.

Read:
- examples/AGENTS.md
- skills/brainstorming/SKILL.md
- skills/test-driven-development/SKILL.md

Decide whether this current slice should activate brainstorming, activate the full TDD skill, create a design document, or use one independent read-only reviewer. A task can add focused tests without activating the full TDD skill. Do not infer ceremony from parent-project risk.

Task:
{case['prompt']}

Return only the requested JSON.
"""


def run_agent(case: dict[str, Any], codex_bin: str, model: str | None, timeout: int) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="specialist-routing-eval-") as tmp:
        tmp_path = Path(tmp)
        schema = tmp_path / "schema.json"
        output = tmp_path / "output.json"
        schema.write_text(json.dumps(OUTPUT_SCHEMA), encoding="utf-8")
        cmd = [
            codex_bin,
            "exec",
            "--ephemeral",
            "--sandbox",
            "read-only",
            "-C",
            str(ROOT),
            "--output-schema",
            str(schema),
            "--output-last-message",
            str(output),
        ]
        if model:
            cmd.extend(["--model", model])
        cmd.append(prompt_for(case))
        result = subprocess.run(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stdout)
        return json.loads(output.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", action="append", dest="case_ids")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--model")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    cases = load_cases()
    selected = args.case_ids or list(cases)
    unknown = [case_id for case_id in selected if case_id not in cases]
    if unknown:
        raise SystemExit(f"unknown cases: {', '.join(unknown)}")

    failed = 0
    keys = ["brainstorming", "tdd", "design_document", "independent_review"]
    for case_id in selected:
        case = cases[case_id]
        for run in range(1, args.repeat + 1):
            actual = run_agent(case, args.codex_bin, args.model, args.timeout)
            failures = [f"{key}: expected {case[key]!r}, got {actual.get(key)!r}" for key in keys if actual.get(key) != case[key]]
            status = "PASS" if not failures else "FAIL"
            print(json.dumps({"case": case_id, "run": run, "status": status, "actual": actual, "failures": failures}, ensure_ascii=False), flush=True)
            failed += bool(failures)
    print(f"SUMMARY: runs={len(selected) * args.repeat} failed={failed}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
