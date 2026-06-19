#!/usr/bin/env python3
"""Lightweight sandbox checks for adaptive-dev-workflow skill changes.

This intentionally avoids third-party YAML dependencies. It checks that the
skill package keeps its routing/evidence scaffolding discoverable and that eval
case files contain the fields needed for manual or subagent-based forward tests.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "adaptive-dev-workflow"
SKILL = SKILL_DIR / "SKILL.md"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"
EVIDENCE = SKILL_DIR / "references" / "evidence-and-validation.md"
HANDOFF = SKILL_DIR / "references" / "production-handoff-gate.md"
SEED = ROOT / "evals" / "seed-cases.yaml"
FAILURES = ROOT / "evals" / "failure-cases.yaml"


REQUIRED_SKILL_SECTIONS = [
    "## Route To Workflow Map",
    "## Process Selection",
    "## Production Handoff Gate",
    "## Test And Verification Strategy",
    "## Task Exit Gate",
    "## Skill Validation",
]

REQUIRED_EVIDENCE_SECTIONS = [
    "## Evidence Matrix",
    "## Evidence Plan Shape",
    "## Completion Claim Levels",
    "## Skill Iteration Protocol",
    "## Eval Case Schema",
    "## Failure Classes",
]

REQUIRED_CASE_FIELDS = [
    "id",
    "prompt",
    "expected_route",
    "risk_type",
    "expected_gates",
    "expected_evidence",
    "claim_ceiling",
    "expected_no",
]

CLAIM_LEVELS = {"Dev Done", "Integration Done", "Handoff Done"}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def line_count(path: Path) -> int:
    return len(read(path).splitlines())


def assert_contains(path: Path, required: list[str]) -> None:
    text = read(path)
    missing = [item for item in required if item not in text]
    if missing:
        fail(f"{path.relative_to(ROOT)} missing sections: {', '.join(missing)}")


def parse_case_blocks(path: Path) -> list[str]:
    text = read(path)
    blocks = []
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


def scalar_value(block: str, key: str) -> str | None:
    match = re.search(rf"^\s+(?:-\s+)?{re.escape(key)}:\s*(.+)$", block, re.M)
    if not match:
        return None
    return match.group(1).strip().strip('"')


def validate_seed_cases() -> tuple[int, dict[str, int]]:
    blocks = parse_case_blocks(SEED)
    if not blocks:
        fail("evals/seed-cases.yaml has no cases")

    route_counts: dict[str, int] = {}
    for block in blocks:
        case_id = scalar_value(block, "id") or "<unknown>"
        keys = top_level_keys(block)
        missing = [field for field in REQUIRED_CASE_FIELDS if field not in keys]
        if missing:
            fail(f"seed case {case_id} missing fields: {', '.join(missing)}")

        claim = scalar_value(block, "claim_ceiling")
        if claim not in CLAIM_LEVELS:
            fail(f"seed case {case_id} has invalid claim_ceiling: {claim}")

        route = scalar_value(block, "expected_route") or "unknown"
        route_counts[route] = route_counts.get(route, 0) + 1

    return len(blocks), route_counts


def validate_failure_cases() -> int:
    text = read(FAILURES)
    if "template:" not in text:
        fail("evals/failure-cases.yaml missing template")
    blocks = parse_case_blocks(FAILURES)
    for block in blocks:
        case_id = scalar_value(block, "id") or "<unknown>"
        for field in ["id", "prompt", "expected_route", "actual_route", "failure_class", "impact", "status"]:
            if field not in top_level_keys(block):
                fail(f"failure case {case_id} missing field: {field}")
    return len(blocks)


def main() -> int:
    assert_contains(SKILL, REQUIRED_SKILL_SECTIONS)
    assert_contains(EVIDENCE, REQUIRED_EVIDENCE_SECTIONS)
    assert_contains(HANDOFF, ["## Delivery Contract", "## Handoff Exit Gate"])
    read(OPENAI_YAML)

    skill_lines = line_count(SKILL)
    if skill_lines > 320:
        fail(f"SKILL.md is getting heavy for a router skill: {skill_lines} lines")

    seed_count, route_counts = validate_seed_cases()
    failure_count = validate_failure_cases()

    print("Sandbox eval passed")
    print(f"- SKILL.md lines: {skill_lines}")
    print(f"- seed cases: {seed_count}")
    print(f"- failure cases captured: {failure_count}")
    print("- route coverage:")
    for route, count in sorted(route_counts.items()):
        print(f"  - {route}: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
