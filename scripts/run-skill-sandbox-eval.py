#!/usr/bin/env python3
"""Deterministic sandbox checks for the adaptive control-plane skill suite."""

from __future__ import annotations

import os
import json
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
AGENT_ORCHESTRATION = ROOT / "skills" / "agent-orchestration"
CHANGE_AWARE_TESTING = ROOT / "skills" / "change-aware-testing"
SEED = ROOT / "evals" / "seed-cases.yaml"
FAILURES = ROOT / "evals" / "failure-cases.yaml"
WORKFLOW_E2E = ROOT / "scripts" / "run-workflow-e2e-eval.py"
AGENT_ORCHESTRATION_E2E = ROOT / "scripts" / "run-agent-orchestration-e2e-eval.py"
FRESH_AGENT_ROUTE_EVAL = ROOT / "scripts" / "run-fresh-agent-route-eval.py"
CHANGE_AWARE_TESTING_EVAL = ROOT / "scripts" / "run-change-aware-testing-eval.py"


REQUIRED_SKILLS = [ADAPTIVE, WORKFLOW, CONTEXT, SPECFLOW, TECHNICAL_DESIGN, DELIVERY, KNOWLEDGE, PROJECT_HARNESS, SUPERPOWERS_ADAPTER, AGENT_ORCHESTRATION, CHANGE_AWARE_TESTING]
REQUIRED_WORKFLOW_SCHEMAS = [
    "workflow-manifest.schema.json",
    "execution-policy.schema.json",
    "strategy.schema.json",
    "route-decision.schema.json",
    "resolved-strategy.schema.json",
    "transition-request.schema.json",
    "transition-result.schema.json",
    "capability-report.schema.json",
    "route-facts-delta.schema.json",
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
    for script in ["validate_json_artifact.py", "validate_workflow_manifest.py", "validate_artifact_graph.py", "validate_strategy_registry.py", "detect_capabilities.py", "apply_route_facts_delta.py", "resolve_strategy.py", "goal_identity.py", "init_workflow.py", "transition_workflow.py", "resume_workflow.py", "migrate_workflow_manifest_v5.py", "inspect_workflow.py"]:
        read(WORKFLOW / "scripts" / script)
    for reference in ["state-machine.md", "error-codes.md", "rule-ownership.md", "strategy-registry.md", "batch-execution.md"]:
        read(WORKFLOW / "references" / reference)

    forbidden_default_methods = {
        "superpowers:subagent-driven-development",
        "superpowers:executing-plans",
        "superpowers:verification-before-completion",
        "superpowers:requesting-code-review",
    }
    continuous_batches = 0
    for strategy_path in sorted((WORKFLOW / "references" / "strategies").glob("*.json")):
        strategy = json.loads(read(strategy_path))
        policy = strategy["execution_policy"]
        scheduled = {skill for skills in strategy["stage_skills"].values() for skill in skills}
        scheduled.update(skill for rule in strategy.get("conditional_skills", []) for skill in rule["skills"])
        forbidden = sorted(scheduled.intersection(forbidden_default_methods))
        if forbidden:
            fail(f"{strategy_path.name} schedules heavyweight default methods: {', '.join(forbidden)}")
        if policy["unit"] == "continuous_batch":
            continuous_batches += 1
            if policy["task_risk"] != "local" or policy["task_exit"] != "focused_signal" or policy["commit"] != "batch":
                fail(f"{strategy_path.name} violates continuous batch cadence")
        if strategy["process_depth"] != "direct" and policy["manifest_updates"] != "stage_only":
            fail(f"{strategy_path.name} permits non-stage manifest updates")
        if policy["max_review_passes"] > 2:
            fail(f"{strategy_path.name} permits unbounded review loops")
    if continuous_batches < 4:
        fail("expected L2/L3 execution strategies to use continuous batches")

    for skill in REQUIRED_SKILLS:
        if "allow_implicit_invocation: true" not in read(skill / "agents" / "openai.yaml"):
            fail(f"skill must remain available to automatic stage dispatch: {skill.name}")

    harness_source = read(PROJECT_HARNESS / "scripts" / "init_project_harness.py")
    if "REQUIRED SUB-SKILL" in harness_source:
        fail("project harness still forces a heavyweight task-by-task execution chain")
    if "Continuous Batch Execution" not in harness_source:
        fail("project harness does not generate the batch execution contract")

    read(CONTEXT / "scripts" / "validate_context_pack_static.py")
    read(CONTEXT / "scripts" / "validate_context_freshness.py")
    read(CONTEXT / "scripts" / "validate_context_runtime_audit.py")
    read(CONTEXT / "scripts" / "run_context_sufficiency_eval.py")
    read(DELIVERY / "scripts" / "validate_evidence_manifest.py")
    read(CHANGE_AWARE_TESTING / "schemas" / "test-impact-map.schema.json")
    read(CHANGE_AWARE_TESTING / "scripts" / "generate_test_impact_map.py")
    read(CHANGE_AWARE_TESTING / "references" / "testing-cadence.md")
    read(CHANGE_AWARE_TESTING / "scripts" / "run_changed_tests.py")
    read(TECHNICAL_DESIGN / "references" / "design-contract.md")
    read(TECHNICAL_DESIGN / "references" / "documentation-topology.md")
    read(TECHNICAL_DESIGN / "references" / "design-review.md")
    read(TECHNICAL_DESIGN / "references" / "spec-system-adapters.md")
    read(KNOWLEDGE / "scripts" / "capture_learning_candidate.py")
    read(KNOWLEDGE / "scripts" / "validate_learning_candidate.py")
    for schema in ["agent-roster.schema.json", "context-packet.schema.json", "work-order.schema.json", "work-result.schema.json"]:
        read(AGENT_ORCHESTRATION / "schemas" / schema)
    for script in ["build_context_packet.py", "create_work_order.py", "validate_agent_roster.py", "validate_context_packet.py", "validate_work_order.py", "validate_work_result.py", "summarize_progress.py"]:
        read(AGENT_ORCHESTRATION / "scripts" / script)
    for reference in ["role-contracts.md", "context-projection.md", "orchestration-patterns.md"]:
        read(AGENT_ORCHESTRATION / "references" / reference)

    skill_lines = line_count(ADAPTIVE / "SKILL.md")
    if skill_lines > 170:
        fail(f"adaptive SKILL.md is too heavy for the router: {skill_lines} lines")

    adaptive_validation = read(ADAPTIVE / "SKILL.md")
    if "python3 scripts/run-workflow-e2e-eval.py" in adaptive_validation:
        fail("adaptive validation duplicates workflow E2E already owned by the sandbox aggregator")
    orchestration_validation = read(AGENT_ORCHESTRATION / "SKILL.md")
    if "python3 scripts/run-skill-sandbox-eval.py" in orchestration_validation:
        fail("agent-orchestration focused validation recursively invokes the suite aggregator")
    phase2_runner = read(ROOT / "scripts" / "run-phase2-eval.py")
    for duplicate in ["scripts/run-workflow-e2e-eval.py", "scripts/run-handoff-fresh-consumer-eval.py"]:
        if duplicate in phase2_runner:
            fail(f"phase2 runner duplicates child eval already covered by sandbox: {duplicate}")

    seed_count, strategy_counts = validate_seed_cases()
    failure_count = validate_failure_cases()
    run([sys.executable, str(WORKFLOW / "scripts" / "validate_strategy_registry.py")])
    run([sys.executable, str(CHANGE_AWARE_TESTING_EVAL)])
    run([sys.executable, str(WORKFLOW_E2E)])
    run([sys.executable, str(AGENT_ORCHESTRATION_E2E)])
    fresh_agent_ran = run_fresh_agent_route_eval()

    print("Sandbox eval passed")
    print(f"- adaptive SKILL.md lines: {skill_lines}")
    print(f"- skill packages: {len(REQUIRED_SKILLS)}")
    print(f"- seed cases: {seed_count}")
    print(f"- failure cases: {failure_count}")
    print("- workflow e2e: pass")
    print("- change-aware testing eval: pass")
    print("- agent orchestration e2e: pass")
    print("- fresh agent route eval: pass" if fresh_agent_ran else "- fresh agent route eval: skipped (set RUN_FRESH_AGENT_ROUTE_EVAL=1)")
    print("- strategy coverage:")
    for strategy, count in sorted(strategy_counts.items()):
        print(f"  - {strategy}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
