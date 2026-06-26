#!/usr/bin/env python3
"""Run fresh Codex semantic route evals against adaptive-dev-workflow."""

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
RESOLVER = ROOT / "skills" / "workflow-control-plane" / "scripts" / "resolve_strategy.py"
DEFAULT_CASES = [
    "tiny-readme-command",
    "debug-ci",
    "specflow-intent-to-spec",
    "complex-frontend-context-pack",
    "large-feature-doc-topology",
    "package-handoff",
    "large-permission-model",
    "review-only-no-edit",
    "spike-unknown-architecture",
    "migration-critical-data",
]


OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "status", "classification", "capability_report_ref", "user_constraints", "user_overrides", "ambiguity", "reason"],
    "properties": {
        "schema_version": {"type": "integer"},
        "status": {"type": "string"},
        "classification": {
            "type": "object",
            "additionalProperties": False,
            "required": ["risk", "work_intent", "delivery_shape", "scope", "uncertainty", "profiles", "change_types"],
            "properties": {
                "risk": {"type": "string"},
                "work_intent": {"type": "string"},
                "delivery_shape": {"type": "string"},
                "scope": {"type": "string"},
                "uncertainty": {"type": "string"},
                "profiles": {"type": "array", "items": {"type": "string"}},
                "change_types": {"type": "array", "items": {"type": "string"}},
            },
        },
        "capability_report_ref": {"type": "string"},
        "user_constraints": {
            "type": "object",
            "additionalProperties": False,
            "required": ["network_access", "production_changes", "required_spec_system", "required_execution_engine"],
            "properties": {
                "network_access": {"type": "string"},
                "production_changes": {"type": "string"},
                "required_spec_system": {"type": ["string", "null"]},
                "required_execution_engine": {"type": ["string", "null"]},
            },
        },
        "user_overrides": {"type": "array", "items": {"type": "string"}},
        "ambiguity": {
            "type": "object",
            "additionalProperties": False,
            "required": ["status", "reasons"],
            "properties": {
                "status": {"type": "string"},
                "reasons": {"type": "array", "items": {"type": "string"}},
            },
        },
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
    return match.group(1).strip().strip('"') if match else ""


def list_value(block: str, key: str) -> list[str]:
    raw = scalar_value(block, key)
    if raw.startswith("[") and raw.endswith("]"):
        return [item.strip().strip('"').strip("'") for item in raw[1:-1].split(",") if item.strip()]
    values: list[str] = []
    match = re.search(rf"^\s+{re.escape(key)}:\s*\n((?:\s+- .+\n?)+)", block, re.M)
    if match:
        values = [line.split("-", 1)[1].strip().strip('"') for line in match.group(1).splitlines()]
    return values


def load_cases() -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}
    for block in parse_case_blocks(SEED):
        case_id = scalar_value(block, "id")
        if not case_id:
            continue
        cases[case_id] = {
            "id": case_id,
            "prompt": scalar_value(block, "prompt"),
            "classification": {
                "risk": scalar_value(block, "risk"),
                "mode": scalar_value(block, "mode"),
                "scope": scalar_value(block, "scope"),
                "uncertainty": scalar_value(block, "uncertainty"),
                "profiles": list_value(block, "profiles"),
            },
            "routing": {
                "spec_system": scalar_value(block, "spec_system"),
                "execution_engine": scalar_value(block, "execution_engine"),
                "strategy_id": scalar_value(block, "strategy_id"),
                "required_skills": list_value(block, "required_skills"),
            },
            "design_control": {
                "policy": scalar_value(block, "policy"),
                "review": scalar_value(block, "review"),
                "documentation_topology": scalar_value(block, "documentation_topology"),
            },
            "claim_requested": scalar_value(block, "expected_claim_requested"),
        }
    return cases


def prompt_for(case: dict[str, Any]) -> str:
    return f"""You are a fresh semantic evaluator for the local adaptive-dev-workflow skill.

Do not edit files. Do not implement the task. Do not run project tests.

Read `skills/adaptive-dev-workflow/SKILL.md` in this repository. Do not edit
files. Classify the user task according to the skill and emit the route decision
only; do not resolve the strategy yourself.

Evaluator instructions such as "do not edit files" are not user overrides.
For this eval, set `capability_report_ref` to `capability-report.json`.
Assume the deterministic capability report says `local`, `superpowers`, and
`fallback` are available, while OpenSpec/repo-native/project harness are unknown
unless the user task explicitly says otherwise.

Do not set `ambiguity.status=ambiguous` only because implementation details,
acceptance details, migration rollout, or exact tests are missing. Use
`uncertainty=high` for those gaps. Use ambiguity only when you cannot classify
the task facts or capabilities conflict.

User task:
{case["prompt"]}

Return only JSON with:
- schema_version: 1
- status: provisional or confirmed
- classification: risk, work_intent, delivery_shape, scope, uncertainty, profiles, change_types
- capability_report_ref
- user_constraints: network_access, production_changes, required_spec_system, required_execution_engine
- user_overrides
- ambiguity: status and reasons
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


def run_fresh_agent(case: dict[str, Any], *, codex_bin: str, model: str | None, timeout_seconds: int) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="adaptive-fresh-route-") as tmp:
        tmp_path = Path(tmp)
        schema_path = tmp_path / "route-schema.json"
        output_path = tmp_path / "last-message.json"
        schema_path.write_text(json.dumps(OUTPUT_SCHEMA), encoding="utf-8")

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

        result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, timeout=timeout_seconds)
        if result.returncode != 0:
            raise RuntimeError("fresh agent command failed:\n" + " ".join(cmd[:-1]) + "\n" + result.stdout)
        output = output_path.read_text(encoding="utf-8") if output_path.exists() else result.stdout
        return extract_json(output)


def normalize(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "_")


def expected_options(value: str) -> set[str]:
    return {normalize(part) for part in str(value).split("|") if part.strip()}


def value_matches(expected: str, actual: Any) -> bool:
    options = expected_options(expected)
    return normalize(actual) in options if options else normalize(actual) == normalize(expected)


def contains_all(actual: list[Any], expected: list[str]) -> bool:
    actual_norm = {normalize(item) for item in actual}
    return all(normalize(item) in actual_norm for item in expected)


def canonical_expected(expected: str, actual: Any) -> str:
    return normalize(expected) if value_matches(expected, actual) else normalize(actual)


def capability_report() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "repo_revision": "fresh-route-eval",
        "spec_systems": [{"id": "fallback", "status": "available", "evidence": ["eval"]}],
        "execution_engines": [
            {"id": "local", "status": "available", "version": "builtin"},
            {"id": "superpowers", "status": "available", "version": "unknown"},
        ],
        "project_harness": {"status": "unknown", "version": "unknown", "evidence": []},
    }


def resolve_route(actual: dict[str, Any]) -> dict[str, Any]:
    route = {key: actual[key] for key in ["schema_version", "status", "classification", "capability_report_ref", "user_constraints", "user_overrides", "ambiguity"]}
    with tempfile.TemporaryDirectory(prefix="adaptive-resolve-route-") as tmp:
        route_path = Path(tmp) / "route.json"
        (Path(tmp) / "capability-report.json").write_text(json.dumps(capability_report(), ensure_ascii=False), encoding="utf-8")
        route_path.write_text(json.dumps(route, ensure_ascii=False), encoding="utf-8")
        result = subprocess.run([sys.executable, str(RESOLVER), str(route_path)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        if result.returncode != 0:
            raise RuntimeError("strategy resolver failed:\n" + result.stdout)
        return extract_json(result.stdout)


def stable_key(case: dict[str, Any], actual: dict[str, Any], resolved: dict[str, Any]) -> dict[str, Any]:
    classification = actual.get("classification") or {}
    return {
        "risk": canonical_expected(case["classification"]["risk"], classification.get("risk")),
        "mode": canonical_expected(case["classification"]["mode"], classification.get("work_intent")),
        "scope": canonical_expected(case["classification"]["scope"], classification.get("scope")),
        "uncertainty": canonical_expected(case["classification"]["uncertainty"], classification.get("uncertainty")),
        "spec_system": canonical_expected(case["routing"]["spec_system"], resolved.get("spec_system")),
        "execution_engine": canonical_expected(case["routing"]["execution_engine"], resolved.get("execution_engine")),
        "strategy_id": canonical_expected(case["routing"]["strategy_id"], resolved.get("strategy_id")),
        "design_policy": canonical_expected(case["design_control"]["policy"], (resolved.get("design_control") or {}).get("policy")),
        "design_review": canonical_expected(case["design_control"]["review"], (resolved.get("design_control") or {}).get("review")),
        "documentation_topology": canonical_expected(case["design_control"]["documentation_topology"], (resolved.get("design_control") or {}).get("documentation_topology")),
        "claim": canonical_expected(case["claim_requested"], "none"),
    }


def validate_result(case: dict[str, Any], actual: dict[str, Any], resolved: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ["risk", "mode", "scope", "uncertainty"]:
        actual_field = "work_intent" if field == "mode" else field
        got = actual.get("classification", {}).get(actual_field)
        want = case["classification"][field]
        if not value_matches(want, got):
            errors.append(f"classification.{actual_field} expected {want!r}, got {normalize(got)!r}")
    if not contains_all(actual.get("classification", {}).get("profiles") or [], case["classification"]["profiles"]):
        errors.append(f"classification.profiles missing expected {case['classification']['profiles']!r}")

    for field in ["spec_system", "execution_engine", "strategy_id"]:
        got = resolved.get(field)
        want = case["routing"][field]
        if not value_matches(want, got):
            errors.append(f"routing.{field} expected {want!r}, got {normalize(got)!r}")
    if not contains_all(resolved.get("required_skills") or [], case["routing"]["required_skills"]):
        errors.append(f"routing.required_skills missing expected {case['routing']['required_skills']!r}")

    for field in ["policy", "review", "documentation_topology"]:
        got = (resolved.get("design_control") or {}).get(field)
        want = case["design_control"][field]
        if not value_matches(want, got):
            errors.append(f"design_control.{field} expected {want!r}, got {normalize(got)!r}")

    got_claim = "none"
    want_claim = normalize(case["claim_requested"])
    if not value_matches(case["claim_requested"], got_claim):
        errors.append(f"claims.requested expected {want_claim!r}, got {got_claim!r}")

    if case["classification"]["risk"] in {"L2", "L3"} and resolved.get("strategy_id") == "quick-change":
        errors.append("L2/L3 must not route to quick-change")
    if case["classification"]["risk"] in {"L0", "L1"} and resolved.get("strategy_id") == "complex-real-slice":
        errors.append("L0/L1 must not trigger complex-real-slice")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", action="append", dest="cases", help="seed case id to run; repeatable")
    parser.add_argument("--all", action="store_true", help="run all seed cases")
    parser.add_argument("--repeat", type=int, default=1, help="fresh-agent repetitions per case")
    parser.add_argument("--codex-bin", default="codex", help="codex executable path")
    parser.add_argument("--model", default=None, help="optional model override")
    parser.add_argument("--timeout-seconds", type=int, default=300, help="timeout per fresh Codex invocation")
    args = parser.parse_args()

    cases = load_cases()
    selected_ids = list(cases) if args.all else (args.cases or DEFAULT_CASES)
    missing = [case_id for case_id in selected_ids if case_id not in cases]
    if missing:
        fail("unknown seed cases: " + ", ".join(missing))

    failures: list[str] = []
    for case_id in selected_ids:
        case = cases[case_id]
        stable_results: list[dict[str, Any]] = []
        case_errors: list[str] = []
        actuals: list[dict[str, Any]] = []
        for run_index in range(args.repeat):
            try:
                actual = run_fresh_agent(case, codex_bin=args.codex_bin, model=args.model, timeout_seconds=args.timeout_seconds)
                resolved = resolve_route(actual)
                actuals.append(actual)
                case_errors.extend(f"run {run_index + 1}: {error}" for error in validate_result(case, actual, resolved))
                stable_results.append(stable_key(case, actual, resolved))
            except Exception as exc:  # noqa: BLE001 - eval runner reports model/tool failures.
                case_errors.append(f"run {run_index + 1}: {exc}")

        if len({json.dumps(item, sort_keys=True, ensure_ascii=False) for item in stable_results}) > 1:
            case_errors.append("classification/routing/claim variance across repetitions")

        if case_errors:
            failures.append(case_id)
            print(f"FAIL {case_id}", flush=True)
            for error in case_errors:
                print(f"  - {error}", flush=True)
            if actuals:
                print("  last actual:", json.dumps(actuals[-1], ensure_ascii=False, sort_keys=True), flush=True)
        else:
            last = actuals[-1]
            resolved = resolve_route(last)
            print(f"PASS {case_id}: {last['classification']['risk']} / {resolved['strategy_id']} / none", flush=True)

    if failures:
        print(f"Fresh agent route eval failed: {len(failures)}/{len(selected_ids)} cases", flush=True)
        return 1
    print(f"Fresh agent route eval passed: {len(selected_ids)} cases x {args.repeat} repeat", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
