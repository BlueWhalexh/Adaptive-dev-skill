#!/usr/bin/env python3
"""Validate that a project AI coding harness has the required contracts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


FORBIDDEN_LOCAL_PATH_MARKERS = [
    "/Users/",
    "/private/tmp/",
    "/tmp/",
    "/var/folders/",
]

CLAIM_LEVELS = {"Dev Done", "Integration Done", "Handoff Done"}
EVIDENCE_TYPES = {"unit", "mock", "fake", "integration", "e2e", "real external", "fresh consumer", "manual"}


def slug(value: str) -> str:
    cleaned: list[str] = []
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
        elif char in {"-", "_", " ", "."}:
            cleaned.append("-")
    result = "".join(cleaned).strip("-")
    while "--" in result:
        result = result.replace("--", "-")
    return result or "project"


def read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return path.read_text(encoding="utf-8")


def require_file(errors: list[str], path: Path) -> None:
    if not path.exists():
        errors.append(f"missing {path}")


def require_contains(errors: list[str], path: Path, needles: list[str]) -> None:
    try:
        text = read(path)
    except FileNotFoundError:
        errors.append(f"missing {path}")
        return
    missing = [needle for needle in needles if needle not in text]
    if missing:
        errors.append(f"{path} missing: {', '.join(missing)}")


def require_no_local_paths(errors: list[str], root: Path) -> None:
    scan_roots = [
        root / "AGENTS.md",
        root / ".agent",
        root / "docs",
    ]
    for scan_root in scan_roots:
        paths = [scan_root] if scan_root.is_file() else sorted(scan_root.rglob("*"))
        for path in paths:
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            found = [marker for marker in FORBIDDEN_LOCAL_PATH_MARKERS if marker in text]
            if found:
                errors.append(f"{path} contains local-only path marker(s): {', '.join(found)}")


def require_acceptance_shape(errors: list[str], path: Path) -> None:
    try:
        lines = read(path).splitlines()
    except FileNotFoundError:
        errors.append(f"missing {path}")
        return

    claim = None
    ids = 0
    evidence_types: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("claim_ceiling:"):
            claim = stripped.split(":", 1)[1].strip().strip('"')
        elif stripped.startswith("- id:"):
            ids += 1
        elif stripped.startswith("type:"):
            evidence_types.append(stripped.split(":", 1)[1].strip().strip('"'))

    if claim not in CLAIM_LEVELS:
        errors.append(f"{path} has invalid claim_ceiling: {claim}")
    if ids < 1:
        errors.append(f"{path} must contain at least one acceptance item with '- id:'")
    invalid_types = [item for item in evidence_types if item not in EVIDENCE_TYPES]
    if invalid_types:
        errors.append(f"{path} has invalid evidence type(s): {', '.join(invalid_types)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--feature-id", default="first-mvp", help="Feature id to validate")
    parser.add_argument("--project-skill", default="project-domain", help="Project skill folder name")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    feature = slug(args.feature_id)
    project_skill = slug(args.project_skill)
    spec_dir = root / "docs" / "specs" / feature
    errors: list[str] = []

    for path in [
        root / "AGENTS.md",
        root / ".gitignore",
        root / ".agent" / "agents.md",
        root / ".agent" / "goal-loop-mode.md",
        root / ".agent" / "knowledge" / "candidates" / ".gitkeep",
        root / ".agent" / "skills" / project_skill / "SKILL.md",
        root / "docs" / "architecture.md",
        spec_dir / "spec.md",
        spec_dir / "design.md",
        spec_dir / "acceptance.yaml",
        root / "docs" / "plans" / f"{feature}.md",
        root / "docs" / "evidence" / f"{feature}.md",
    ]:
        require_file(errors, path)

    require_contains(errors, spec_dir / "spec.md", [
        "## Intent",
        "## Scope",
        "## Non-goals",
        "## Current Truth",
        "## Delivery Verification",
        "## Acceptance Criteria",
        "## Stop / Continue Conditions",
    ])
    require_contains(errors, root / ".gitignore", [
        ".env",
        ".env.*",
        ".agent/runs/*",
        "!.agent/runs/.gitkeep",
    ])
    require_contains(errors, spec_dir / "acceptance.yaml", [
        "feature_id:",
        "claim_ceiling:",
        "acceptance:",
        "evidence:",
        "type:",
        "stop_conditions:",
        "continue_conditions:",
    ])
    require_acceptance_shape(errors, spec_dir / "acceptance.yaml")
    require_contains(errors, root / "docs" / "evidence" / f"{feature}.md", [
        "## Claim Ceiling",
        "## Validators",
        "## Red / Reproduction Evidence",
        "## Green / Final Evidence",
        "## Deferred / Accepted Gaps",
    ])
    require_contains(errors, root / ".agent" / "agents.md", [
        "repo-grounder",
        "spec-reviewer",
        "plan-reviewer",
        "evidence-reviewer",
        "security-data-reviewer",
    ])
    require_contains(errors, root / ".agent" / "goal-loop-mode.md", [
        "进入 Goal Loop Mode",
        "acceptance criteria",
        "claim ceiling",
        "continue / stop / ask human",
    ])
    require_no_local_paths(errors, root)

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    print("Project harness valid")
    print(f"- root: {root}")
    print(f"- feature: {feature}")
    print(f"- project skill: {project_skill}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
