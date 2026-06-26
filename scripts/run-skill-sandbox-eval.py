#!/usr/bin/env python3
"""Deterministic sandbox checks for the adaptive control-plane skill suite."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADAPTIVE = ROOT / "skills" / "adaptive-dev-workflow"
WORKFLOW = ROOT / "skills" / "workflow-control-plane"
CONTEXT = ROOT / "skills" / "context-grounding"
SPECFLOW = ROOT / "skills" / "specflow"
DELIVERY = ROOT / "skills" / "delivery-verification"
KNOWLEDGE = ROOT / "skills" / "knowledge-promotion"
TECHNICAL_DESIGN = ROOT / "skills" / "technical-design"
PROJECT_HARNESS = ROOT / "skills" / "project-harness-init"
SUPERPOWERS_ADAPTER = ROOT / "skills" / "superpowers-adapter"
SEED = ROOT / "evals" / "seed-cases.yaml"
FAILURES = ROOT / "evals" / "failure-cases.yaml"
WORKFLOW_E2E = ROOT / "scripts" / "run-workflow-e2e-eval.py"
FRESH_AGENT_ROUTE_EVAL = ROOT / "scripts" / "run-fresh-agent-route-eval.py"


REQUIRED_SKILLS = [ADAPTIVE, WORKFLOW, CONTEXT, SPECFLOW, TECHNICAL_DESIGN, DELIVERY, KNOWLEDGE, PROJECT_HARNESS, SUPERPOWERS_ADAPTER]
REQUIRED_WORKFLOW_SCHEMAS = [
    "workflow-manifest.schema.json",
    "strategy.schema.json",
    "route-decision.schema.json",
    "resolved-strategy.schema.json",
    "transition-request.schema.json",
    "transition-result.schema.json",
]
REQUIRED_DELIVERY_SCHEMAS = [
    "evidence-manifest.schema.json",
    "verifier-registry.schema.json",
]
REQUIRED_ADAPTIVE_SECTIONS = [
    "## Output",
    "## Classification",
    "## Capability Detection",
    "## Procedure",
    "## Delegation Map",
    "## Never",
    "## Validation",
]
REQUIRED_CASE_FIELDS = [
    "id",
    "prompt",
    "expected_classification",
    "expected_routing",
    "expected_claim_requested",
    "expected_no",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def assert_contains(path: Path, required: list[str]) -> None:
    text = read(path)
    missing = [item for item in required if item not in text]
    if missing:
        fail(f"{path.relative_to(ROOT)} missing: {', '.join(missing)}")


def line_count(path: Path) -> int:
    return len(read(path).splitlines())


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


def top_level_keys(block: str) -> set[str]:
    keys = set()
    for line in block.splitlines():
        match = re.match(r"\s+(?:-\s+)?([A-Za-z_][A-Za-z0-9_]*):", line)
        if match:
            keys.add(match.group(1))
    return keys


def scalar_value(block: str, key: str) -> str:
    match = re.search(rf"^\s+(?:-\s+)?{re.escape(key)}:\s*(.+)$", block, re.M)
    return match.group(1).strip().strip('"') if match else ""


def validate_seed_cases() -> tuple[int, dict[str, int]]:
    blocks = parse_case_blocks(SEED)
    if not blocks:
        fail("evals/seed-cases.yaml has no cases")
    strategies: dict[str, int] = {}
    for block in blocks:
        case_id = scalar_value(block, "id") or "<unknown>"
        missing = [field for field in REQUIRED_CASE_FIELDS if field not in top_level_keys(block)]
        if missing:
            fail(f"seed case {case_id} missing fields: {', '.join(missing)}")
        strategy = scalar_value(block, "strategy_id")
        if not strategy:
            fail(f"seed case {case_id} missing expected_routing.strategy_id")
        strategies[strategy] = strategies.get(strategy, 0) + 1
    return len(blocks), strategies


def validate_failure_cases() -> int:
    blocks = parse_case_blocks(FAILURES)
    if not blocks:
        fail("evals/failure-cases.yaml has no cases")
    for block in blocks:
        case_id = scalar_value(block, "id") or "<unknown>"
        missing = [field for field in ["id", "prompt", "expected_behavior", "failure_class", "impact", "status"] if field not in top_level_keys(block)]
        if missing:
            fail(f"failure case {case_id} missing fields: {', '.join(missing)}")
    return len(blocks)


def run(args: list[str]) -> str:
    result = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if result.returncode != 0:
        print(result.stdout)
        fail("command failed: " + " ".join(args))
    return result.stdout


def run_fresh_agent_route_eval() -> bool:
    if os.environ.get("RUN_FRESH_AGENT_ROUTE_EVAL") != "1":
        return False
    run([sys.executable, str(FRESH_AGENT_ROUTE_EVAL), "--repeat", "1", "--case", "tiny-readme-command", "--case", "package-handoff", "--case", "complex-frontend-context-pack"])
    return True


def main() -> int:
    for skill_dir in REQUIRED_SKILLS:
        read(skill_dir / "SKILL.md")
        read(skill_dir / "agents" / "openai.yaml")

    assert_contains(ADAPTIVE / "SKILL.md", REQUIRED_ADAPTIVE_SECTIONS)
    assert_contains(ADAPTIVE / "SKILL.md", ["route_decision.json", "workflow-control-plane", "Do not write or mutate", "context-grounding", "delivery-verification"])
    for forbidden in ["## Artifact Graph", "## Verifier-Signed Claims", "## Technical Design Gate", "route_card:", "evidence_card:", "artifact_state:", "delivery_claim:", "claim_ceiling:"]:
        if forbidden in read(ADAPTIVE / "SKILL.md"):
            fail(f"adaptive SKILL.md still contains old control-plane marker: {forbidden}")

    for schema in REQUIRED_WORKFLOW_SCHEMAS:
        read(WORKFLOW / "schemas" / schema)
    for schema in REQUIRED_DELIVERY_SCHEMAS:
        read(DELIVERY / "schemas" / schema)
    read(DELIVERY / "references" / "verifier-registry.json")
    for script in ["validate_json_artifact.py", "validate_workflow_manifest.py", "validate_artifact_graph.py", "validate_strategy_registry.py", "resolve_strategy.py", "init_workflow.py", "transition_workflow.py", "resume_workflow.py", "inspect_workflow.py"]:
        read(WORKFLOW / "scripts" / script)
    for reference in ["state-machine.md", "error-codes.md", "rule-ownership.md", "strategy-registry.md"]:
        read(WORKFLOW / "references" / reference)

    read(CONTEXT / "scripts" / "validate_context_pack_static.py")
    read(CONTEXT / "scripts" / "validate_context_freshness.py")
    read(CONTEXT / "scripts" / "validate_context_runtime_audit.py")
    read(CONTEXT / "scripts" / "run_context_sufficiency_eval.py")
    read(DELIVERY / "scripts" / "validate_evidence_manifest.py")
    read(TECHNICAL_DESIGN / "references" / "design-contract.md")
    read(TECHNICAL_DESIGN / "references" / "documentation-topology.md")
    read(TECHNICAL_DESIGN / "references" / "design-review.md")
    read(TECHNICAL_DESIGN / "references" / "spec-system-adapters.md")
    read(KNOWLEDGE / "scripts" / "capture_learning_candidate.py")
    read(KNOWLEDGE / "scripts" / "validate_learning_candidate.py")

    skill_lines = line_count(ADAPTIVE / "SKILL.md")
    if skill_lines > 170:
        fail(f"adaptive SKILL.md is too heavy for the router: {skill_lines} lines")

    seed_count, strategy_counts = validate_seed_cases()
    failure_count = validate_failure_cases()
    run([sys.executable, str(WORKFLOW / "scripts" / "validate_strategy_registry.py")])
    run([sys.executable, str(WORKFLOW_E2E)])
    fresh_agent_ran = run_fresh_agent_route_eval()

    print("Sandbox eval passed")
    print(f"- adaptive SKILL.md lines: {skill_lines}")
    print(f"- skill packages: {len(REQUIRED_SKILLS)}")
    print(f"- seed cases: {seed_count}")
    print(f"- failure cases: {failure_count}")
    print("- workflow e2e: pass")
    print("- fresh agent route eval: pass" if fresh_agent_ran else "- fresh agent route eval: skipped (set RUN_FRESH_AGENT_ROUTE_EVAL=1)")
    print("- strategy coverage:")
    for strategy, count in sorted(strategy_counts.items()):
        print(f"  - {strategy}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
