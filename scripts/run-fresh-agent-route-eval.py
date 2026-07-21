#!/usr/bin/env python3
"""Run fresh Codex semantic evals for outcome-first activation and routing."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals" / "outcome-cases.json"

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["activate", "mode", "current_outcome", "immediate_action", "allowed_skills", "forbidden_actions", "max_new_subagents", "human_decision_needed", "reason"],
    "properties": {
        "activate": {"type": "boolean"},
        "mode": {"type": "string", "enum": ["bypass", "prove", "improve", "harden"]},
        "current_outcome": {"type": "string"},
        "immediate_action": {"type": "string"},
        "allowed_skills": {"type": "array", "items": {"type": "string"}},
        "forbidden_actions": {"type": "array", "items": {"type": "string"}},
        "max_new_subagents": {"type": "integer", "minimum": 0, "maximum": 4},
        "human_decision_needed": {"type": "boolean"},
        "reason": {"type": "string"},
    },
}


def load_cases() -> dict[str, dict[str, Any]]:
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    return {case["id"]: case for case in payload["cases"]}


def prompt_for(case: dict[str, Any]) -> str:
    return f"""You are a fresh evaluator. Do not implement or edit files.

Read `skills/adaptive-dev-workflow/SKILL.md` and decide whether it should activate for the user task. Apply the Activation Gate strictly. A specialist skill can be allowed without activating Adaptive. Do not invent workflow manifests, Specs, plans, or agent teams.

User task:
{case['prompt']}

Return only the requested JSON. `immediate_action` must describe the next concrete action, not a generic process. Keep skill names exact. For bypass tasks, use mode=bypass and activate=false.
"""


def run_agent(case: dict[str, Any], codex_bin: str, model: str | None, timeout: int) -> tuple[dict[str, Any], dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="adaptive-outcome-eval-") as tmp:
        tmp_path = Path(tmp)
        schema = tmp_path / "schema.json"
        output = tmp_path / "output.json"
        schema.write_text(json.dumps(OUTPUT_SCHEMA), encoding="utf-8")
        cmd = [codex_bin, "exec", "--ephemeral", "--sandbox", "read-only", "-C", str(ROOT), "--output-schema", str(schema), "--output-last-message", str(output)]
        if model:
            cmd.extend(["--model", model])
        cmd.append(prompt_for(case))
        result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)
        if result.returncode != 0:
            raise RuntimeError(result.stdout)
        actual = json.loads(output.read_text(encoding="utf-8"))
        usage = {}
        for line in result.stdout.splitlines():
            if line.startswith("usage:"):
                try:
                    usage = json.loads(line.removeprefix("usage:").strip())
                except json.JSONDecodeError:
                    pass
        return actual, usage


def evaluate(case: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for key in ["activate", "mode"]:
        if actual.get(key) != case[key]:
            failures.append(f"{key}: expected {case[key]!r}, got {actual.get(key)!r}")
    if actual.get("max_new_subagents", 99) > case["max_new_subagents"]:
        failures.append(f"max_new_subagents exceeds {case['max_new_subagents']}: {actual.get('max_new_subagents')}")
    allowed = {item.lower() for item in actual.get("allowed_skills", [])}
    for skill in case.get("allowed_skills", []):
        if skill.lower() not in allowed:
            failures.append(f"missing allowed skill: {skill}")
    combined = " ".join([actual.get("current_outcome", ""), actual.get("immediate_action", ""), actual.get("reason", ""), *actual.get("forbidden_actions", [])]).lower()
    for concept in case.get("required_concepts", []):
        aliases = concept if isinstance(concept, list) else [concept]
        if not any(alias.lower() in combined for alias in aliases):
            failures.append(f"missing required concept: {' | '.join(aliases)}")
    for skill in case.get("forbidden_skills", []):
        if skill.lower() in allowed:
            failures.append(f"forbidden skill allowed: {skill}")
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
            actual, usage = run_agent(cases[case_id], args.codex_bin, args.model, args.timeout)
            failures = evaluate(cases[case_id], actual)
            status = "PASS" if not failures else "FAIL"
            print(
                json.dumps(
                    {"case": case_id, "run": run, "status": status, "actual": actual, "failures": failures, "usage": usage},
                    ensure_ascii=False,
                ),
                flush=True,
            )
            failed += bool(failures)
    print(f"SUMMARY: runs={len(selected) * args.repeat} failed={failed}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
