#!/usr/bin/env python3
"""Fresh-agent behavior eval for lightweight SDD and testing decisions."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals" / "lightweight-dev-cases.json"

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "spec_artifact",
        "technical_design_needed",
        "failure_evidence",
        "validator_scope",
        "evidence_layers",
        "max_new_documents",
        "claim_ceiling",
        "reason",
    ],
    "properties": {
        "spec_artifact": {"type": "string", "enum": ["none", "requirement_note", "canonical_spec", "reuse_existing"]},
        "technical_design_needed": {"type": "boolean"},
        "failure_evidence": {"type": "string", "enum": ["required", "preferred", "alternate"]},
        "validator_scope": {"type": "string", "enum": ["focused", "changed_scope", "milestone", "release"]},
        "evidence_layers": {
            "type": "array",
            "items": {"type": "string", "enum": ["static", "unit", "integration", "e2e", "visual", "fresh_consumer", "real_external", "acceptance"]},
        },
        "max_new_documents": {"type": "integer", "minimum": 0, "maximum": 3},
        "claim_ceiling": {"type": "string", "enum": ["proxy_only", "local_change", "integration", "basic_usable", "handoff"]},
        "reason": {"type": "string"},
    },
}


def load_cases() -> dict[str, dict[str, Any]]:
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    return {case["id"]: case for case in payload["cases"]}


def prompt_for(case: dict[str, Any]) -> str:
    return f"""You are a fresh evaluator. Do not edit files or implement the task.

Read these contracts:
- skills/adaptive-dev-workflow/SKILL.md
- skills/adaptive-dev-workflow/references/lightweight-sdd-and-testing.md

Decide the minimum documentation and evidence for this current slice. Do not infer release requirements from parent-project risk. `failure_evidence=preferred` means obtain failing evidence first when reasonable; `alternate` means no mechanical RED. `claim_ceiling=proxy_only` means current proxy evidence cannot sign a product capability claim.

User task:
{case['prompt']}

Return only the requested JSON. Keep the decision minimal and do not propose extra workflow artifacts.
"""


def run_agent(case: dict[str, Any], codex_bin: str, model: str | None, timeout: int) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="adaptive-lightweight-eval-") as tmp:
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
        result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, check=False)
        if result.returncode != 0:
            raise RuntimeError(result.stdout)
        return json.loads(output.read_text(encoding="utf-8"))


def evaluate(case: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for key in ["spec_artifact", "technical_design_needed", "failure_evidence", "validator_scope", "claim_ceiling"]:
        if actual.get(key) != case[key]:
            failures.append(f"{key}: expected {case[key]!r}, got {actual.get(key)!r}")
    if actual.get("max_new_documents", 99) > case["max_new_documents"]:
        failures.append(f"max_new_documents exceeds {case['max_new_documents']}: {actual.get('max_new_documents')}")
    layers = set(actual.get("evidence_layers", []))
    for layer in case.get("required_layers", []):
        if layer not in layers:
            failures.append(f"missing evidence layer: {layer}")
    for layer in case.get("forbidden_layers", []):
        if layer in layers:
            failures.append(f"forbidden evidence layer: {layer}")
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
            status = "PASS" if not failures else "FAIL"
            print(json.dumps({"case": case_id, "run": run, "status": status, "actual": actual, "failures": failures}, ensure_ascii=False), flush=True)
            failed += bool(failures)
    print(f"SUMMARY: runs={len(selected) * args.repeat} failed={failed}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
