#!/usr/bin/env python3
"""Deterministic contract checks for the outcome-first Adaptive skill."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "adaptive-dev-workflow" / "SKILL.md"
OPENAI_YAML = ROOT / "skills" / "adaptive-dev-workflow" / "agents" / "openai.yaml"
CASES = ROOT / "evals" / "outcome-cases.json"
LIGHTWEIGHT_GUIDE = ROOT / "skills" / "adaptive-dev-workflow" / "references" / "lightweight-sdd-and-testing.md"
LIGHTWEIGHT_CASES = ROOT / "evals" / "lightweight-dev-cases.json"

HEAVY_SKILLS = [
    "workflow-control-plane",
    "context-grounding",
    "specflow",
    "technical-design",
    "delivery-verification",
    "project-harness-init",
    "knowledge-promotion",
    "superpowers-adapter",
    "change-aware-testing",
]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    skill = read(SKILL)
    lines = skill.splitlines()
    if len(lines) > 170:
        fail(f"SKILL.md exceeds 170 lines: {len(lines)}")

    required = [
        "## Activation Gate",
        "## Four Laws",
        "Outcome Before Process",
        "Current Slice, Not Parent Risk",
        "Evidence Proportional to the Claim",
        "Budget the Process",
        "## Outcome Modes",
        "## Human Judgment Boundary",
        "## Progress Contract",
    ]
    for marker in required:
        if marker not in skill:
            fail(f"missing marker: {marker}")

    forbidden = [
        "route_decision.json",
        "workflow_manifest.json` 的唯一",
        "detect_capabilities.py",
        "resolve_strategy.py",
        "Tiny / Small / Medium / Large",
    ]
    for marker in forbidden:
        if marker in skill:
            fail(f"legacy control-plane marker remains: {marker}")

    if "references/lightweight-sdd-and-testing.md" not in skill:
        fail("lightweight SDD/testing reference is not conditionally routed")
    guide = read(LIGHTWEIGHT_GUIDE)
    for marker in [
        "canonical ready Spec",
        "不要默认生成 Spec、Design、Plan 三件套",
        "E2E 与 unit 是互补关系",
        "不要求每个任务机械执行 Test First 或 RED",
        "Coverage 用于发现空白和观察趋势",
    ]:
        if marker not in guide:
            fail(f"lightweight guide missing contract: {marker}")
    lightweight_cases = json.loads(read(LIGHTWEIGHT_CASES)).get("cases", [])
    if len(lightweight_cases) < 9:
        fail("expected at least 9 lightweight SDD/testing behavior cases")
    if not (ROOT / "scripts" / "run-fresh-lightweight-dev-eval.py").exists():
        fail("missing fresh lightweight behavior evaluator")

    if "allow_implicit_invocation: true" not in read(OPENAI_YAML):
        fail("adaptive must remain discoverable for its narrow trigger")
    for name in HEAVY_SKILLS:
        policy = read(ROOT / "skills" / name / "agents" / "openai.yaml")
        if "allow_implicit_invocation: false" not in policy:
            fail(f"heavy skill remains implicitly invocable: {name}")
    team_policy = read(ROOT / "skills" / "agent-orchestration" / "agents" / "openai.yaml")
    if "allow_implicit_invocation: true" not in team_policy:
        fail("agent-orchestration must remain discoverable for its narrow multi-role trigger")

    payload = json.loads(read(CASES))
    cases = payload.get("cases", [])
    if len(cases) < 10:
        fail("expected at least 10 outcome scenarios")
    ids = set()
    modes = set()
    activation = {True: 0, False: 0}
    for case in cases:
        missing = [key for key in ["id", "prompt", "activate", "mode", "max_new_subagents", "forbidden_skills"] if key not in case]
        if missing:
            fail(f"case missing fields {missing}: {case.get('id', '<unknown>')}")
        if case["id"] in ids:
            fail(f"duplicate case id: {case['id']}")
        ids.add(case["id"])
        modes.add(case["mode"])
        activation[case["activate"]] += 1
        if case["max_new_subagents"] > 1:
            fail(f"ordinary case permits agent fan-out: {case['id']}")
    if modes != {"bypass", "prove", "improve", "harden"}:
        fail(f"outcome mode coverage incomplete: {sorted(modes)}")
    if min(activation.values()) < 4:
        fail(f"positive/negative activation coverage is unbalanced: {activation}")

    print(f"PASS: outcome-first contract; skill_lines={len(lines)} cases={len(cases)} activation={activation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
