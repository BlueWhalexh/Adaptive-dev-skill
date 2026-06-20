#!/usr/bin/env python3
"""Run fresh Codex semantic route evals against adaptive-dev-workflow.

This is intentionally separate from the deterministic sandbox eval because it
starts fresh agent sessions and may take time, model quota, or local approval.

Examples:
  python3 scripts/run-fresh-agent-route-eval.py
  python3 scripts/run-fresh-agent-route-eval.py --case package-handoff --case project-harness-init-goal-loop
  python3 scripts/run-fresh-agent-route-eval.py --all
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "evals" / "seed-cases.yaml"
DEFAULT_CASES = [
    "tiny-readme-command",
    "medium-api-contract",
    "package-handoff",
    "project-harness-init-goal-loop",
]


SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "route",
        "risk_type",
        "claim_ceiling",
        "required_gates",
        "delegated_skills",
        "needs_project_harness",
        "handoff_required",
        "reason",
    ],
    "properties": {
        "route": {"type": "string"},
        "risk_type": {"type": "string"},
        "claim_ceiling": {"type": "string"},
        "required_gates": {"type": "array", "items": {"type": "string"}},
        "delegated_skills": {"type": "array", "items": {"type": "string"}},
        "needs_project_harness": {"type": "boolean"},
        "handoff_required": {"type": "boolean"},
        "reason": {"type": "string"},
    },
}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def parse_case_blocks(path: Path) -> list[str]:
    text = read(path)
    blocks: list[str] = []
    current: list[str] = []
    in_cases = False
    for line in text.splitlines():
        if line.startswith("cases:"):
            in_cases = True
            continue
        if in_cases and line.startswith("template:"):
            break
        if not in_cases:
            continue
        if re.match(r"\s+- id:", line):
            if current:
                blocks.append("\n".join(current))
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks


def scalar_value(block: str, key: str) -> str:
    match = re.search(rf"^\s+(?:-\s+)?{re.escape(key)}:\s*(.+)$", block, re.M)
    if not match:
        return ""
    return match.group(1).strip().strip('"')


def load_cases() -> dict[str, dict[str, str]]:
    cases: dict[str, dict[str, str]] = {}
    for block in parse_case_blocks(SEED):
        case_id = scalar_value(block, "id")
        if not case_id:
            continue
        cases[case_id] = {
            "id": case_id,
            "prompt": scalar_value(block, "prompt"),
            "expected_route": scalar_value(block, "expected_route"),
            "risk_type": scalar_value(block, "risk_type"),
            "claim_ceiling": scalar_value(block, "claim_ceiling"),
        }
    return cases


def prompt_for(case: dict[str, str]) -> str:
    return f"""You are a fresh semantic evaluator for the local adaptive-dev-workflow skill.

Do not edit files. Do not implement the task. Do not run project tests.

Read `skills/adaptive-dev-workflow/SKILL.md` in this repository. If that skill
directly tells you to read a reference for this kind of task, read only the
needed reference. Classify the user task according to the skill.

User task:
{case["prompt"]}

Return only JSON with these fields:
- route: Tiny, Small, Debug, Medium, Large, OpenSpec, or a compact combined route when the skill requires it
- risk_type
- claim_ceiling: Dev Done, Integration Done, or Handoff Done
- required_gates: array of short gate names
- delegated_skills: array of skill names, empty when none
- needs_project_harness: boolean
- handoff_required: boolean
- reason: one short sentence
"""


def extract_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if not stripped:
        fail("fresh agent returned empty output")
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", stripped, re.S)
        if not match:
            fail("fresh agent output did not contain JSON:\n" + stripped)
        value = json.loads(match.group(0))
    if not isinstance(value, dict):
        fail("fresh agent JSON output is not an object")
    return value


def run_fresh_agent(case: dict[str, str], *, codex_bin: str, model: str | None) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="adaptive-fresh-route-") as tmp:
        tmp_path = Path(tmp)
        schema_path = tmp_path / "route-schema.json"
        output_path = tmp_path / "last-message.json"
        schema_path.write_text(json.dumps(SCHEMA), encoding="utf-8")

        cmd = [
            codex_bin,
            "exec",
            "--ephemeral",
            "--sandbox",
            "read-only",
            "-C",
            str(ROOT),
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(output_path),
        ]
        if model:
            cmd.extend(["--model", model])
        cmd.append(prompt_for(case))

        result = subprocess.run(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError("fresh agent command failed:\n" + " ".join(cmd[:-1]) + "\n" + result.stdout)
        output = output_path.read_text(encoding="utf-8") if output_path.exists() else result.stdout
        return extract_json(output)


def normalize_route(route: Any) -> str:
    return str(route or "").strip().lower().replace(" ", "")


def route_matches(expected: str, actual: Any) -> bool:
    expected_norm = normalize_route(expected)
    actual_norm = normalize_route(actual)
    if not actual_norm:
        return False

    if "+harness" in expected_norm:
        return "medium" in actual_norm or "large" in actual_norm

    if expected_norm == "medium/large":
        return "medium" in actual_norm or "large" in actual_norm

    if expected_norm == "tiny/small":
        return actual_norm in {"tiny", "small", "tiny/small"}

    return actual_norm == expected_norm


def contains_any(values: list[str], needles: list[str]) -> bool:
    haystack = " | ".join(str(value).lower() for value in values)
    return any(needle in haystack for needle in needles)


def validate_result(case: dict[str, str], actual: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    case_id = case["id"]
    route = normalize_route(actual.get("route"))
    if not route_matches(case["expected_route"], actual.get("route")):
        errors.append(f"route expected {case['expected_route']!r}, got {actual.get('route')!r}")

    claim = str(actual.get("claim_ceiling") or "").strip()
    if claim != case["claim_ceiling"]:
        errors.append(f"claim_ceiling expected {case['claim_ceiling']!r}, got {claim!r}")

    gates = [str(item) for item in actual.get("required_gates") or []]
    delegated = [str(item) for item in actual.get("delegated_skills") or []]

    if case_id == "debug-ci":
        if route != "debug" and not contains_any(delegated, ["systematic-debugging", "debug"]):
            errors.append("debug case did not route to Debug or systematic-debugging")

    if "handoff" in case_id or case["claim_ceiling"] == "Handoff Done":
        if actual.get("handoff_required") is not True:
            errors.append("handoff_required should be true for delivery handoff")
        if not contains_any(gates, ["fresh consumer", "delivery", "handoff"]):
            errors.append("handoff case missing delivery/fresh-consumer gate")

    if "harness" in case["expected_route"].lower() or "harness" in case_id:
        if actual.get("needs_project_harness") is not True and not contains_any(delegated, ["project-harness-init"]):
            errors.append("harness case did not require project harness or delegate project-harness-init")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", action="append", dest="cases", help="seed case id to run; repeatable")
    parser.add_argument("--all", action="store_true", help="run all seed cases")
    parser.add_argument("--codex-bin", default="codex", help="codex executable path")
    parser.add_argument("--model", default=None, help="optional model override passed to codex exec")
    args = parser.parse_args()

    cases = load_cases()
    selected_ids = list(cases) if args.all else (args.cases or DEFAULT_CASES)
    missing = [case_id for case_id in selected_ids if case_id not in cases]
    if missing:
        fail("unknown seed cases: " + ", ".join(missing))

    failures: list[str] = []
    for case_id in selected_ids:
        case = cases[case_id]
        try:
            actual = run_fresh_agent(case, codex_bin=args.codex_bin, model=args.model)
            errors = validate_result(case, actual)
        except Exception as exc:  # noqa: BLE001 - eval runner should report any model/tool failure.
            actual = {}
            errors = [str(exc)]

        if errors:
            failures.append(case_id)
            print(f"FAIL {case_id}")
            for error in errors:
                print(f"  - {error}")
            if actual:
                print("  actual:", json.dumps(actual, ensure_ascii=False, sort_keys=True))
        else:
            print(f"PASS {case_id}: {actual.get('route')} / {actual.get('claim_ceiling')}")

    if failures:
        print(f"Fresh agent route eval failed: {len(failures)}/{len(selected_ids)} cases")
        return 1

    print(f"Fresh agent route eval passed: {len(selected_ids)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
