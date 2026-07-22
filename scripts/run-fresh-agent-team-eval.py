#!/usr/bin/env python3
"""Run fresh Codex semantic evals for Agent Team activation and review boundaries."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals" / "agent-team-cases.json"

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["use_orchestration_skill", "execution_pattern", "independent_reviewer_required", "max_active_writers", "reviewer_worktree", "context_policy", "reason"],
    "properties": {
        "use_orchestration_skill": {"type": "boolean"},
        "execution_pattern": {"type": "string", "enum": ["direct", "maker_checker", "sequential_team", "parallel_team"]},
        "independent_reviewer_required": {"type": "boolean"},
        "max_active_writers": {"type": "integer", "minimum": 0, "maximum": 3},
        "reviewer_worktree": {"type": "boolean"},
        "context_policy": {"type": "string", "enum": ["direct_task_context", "minimal_packet"]},
        "reason": {"type": "string"},
    },
}


def load_cases() -> dict[str, dict[str, Any]]:
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    return {case["id"]: case for case in payload["cases"]}


def prompt_for(case: dict[str, Any]) -> str:
    return f"""You are a fresh evaluator. Do not implement or edit files.

Read `skills/agent-orchestration/SKILL.md` and `skills/adaptive-dev-workflow/references/maker-checker.md`. Decide the smallest safe collaboration pattern for the task. Distinguish invoking the orchestration skill from directly creating one read-only checker. Do not create a team merely because review is required.

User task:
{case['prompt']}

Return only the requested JSON. Count only concurrent writers in `max_active_writers`; a read-only reviewer never needs a worktree. Use `minimal_packet` whenever another agent/session is created.
"""


def run_agent(case: dict[str, Any], codex_bin: str, model: str | None, timeout: int) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="agent-team-eval-") as tmp:
        root = Path(tmp)
        schema = root / "schema.json"
        output = root / "output.json"
        schema.write_text(json.dumps(OUTPUT_SCHEMA), encoding="utf-8")
        cmd = [codex_bin, "exec", "--ephemeral", "--sandbox", "read-only", "-C", str(ROOT), "--output-schema", str(schema), "--output-last-message", str(output)]
        if model:
            cmd.extend(["--model", model])
        cmd.append(prompt_for(case))
        result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)
        if result.returncode != 0:
            raise RuntimeError(result.stdout)
        return json.loads(output.read_text(encoding="utf-8"))


def evaluate(case: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for key in ["use_orchestration_skill", "execution_pattern", "independent_reviewer_required", "max_active_writers", "reviewer_worktree"]:
        if actual.get(key) != case[key]:
            failures.append(f"{key}: expected {case[key]!r}, got {actual.get(key)!r}")
    expected_context = "minimal_packet" if case["execution_pattern"] != "direct" else "direct_task_context"
    if actual.get("context_policy") != expected_context:
        failures.append(f"context_policy: expected {expected_context!r}, got {actual.get('context_policy')!r}")
    return failures


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
    for case_id in selected:
        for run in range(1, args.repeat + 1):
            actual = run_agent(cases[case_id], args.codex_bin, args.model, args.timeout)
            failures = evaluate(cases[case_id], actual)
            print(json.dumps({"case": case_id, "run": run, "status": "PASS" if not failures else "FAIL", "actual": actual, "failures": failures}, ensure_ascii=False), flush=True)
            failed += bool(failures)
    print(f"SUMMARY: runs={len(selected) * args.repeat} failed={failed}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
