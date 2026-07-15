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

OPEN_SPEC_MARKERS = [
    "openspec",
    ".openspec",
    "open-spec",
    "openspec.yaml",
    "openspec.yml",
    "open-spec.yaml",
    "open-spec.yml",
]


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


def has_openspec(root: Path) -> bool:
    return any((root / marker).exists() for marker in OPEN_SPEC_MARKERS)


def resolve_spec_system(root: Path, requested: str) -> str:
    if requested != "auto":
        return requested
    return "openspec" if has_openspec(root) else "superpowers"


def read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return path.read_text(encoding="utf-8")


def require_file(errors: list[str], path: Path) -> None:
    if not path.exists():
        errors.append(f"missing {path}")


def require_dated_file(errors: list[str], directory: Path, pattern: str, label: str) -> Path | None:
    if not directory.exists():
        errors.append(f"missing {directory}")
        return None
    candidates = sorted(directory.glob(pattern))
    if not candidates:
        errors.append(f"missing {label}: expected {directory / pattern}")
        return None
    return candidates[-1]


def require_contains(errors: list[str], path: Path, needles: list[str]) -> None:
    try:
        text = read(path)
    except FileNotFoundError:
        errors.append(f"missing {path}")
        return
    missing = [needle for needle in needles if needle not in text]
    if missing:
        errors.append(f"{path} missing: {', '.join(missing)}")


def require_absent(errors: list[str], path: Path, needles: list[str]) -> None:
    try:
        text = read(path)
    except FileNotFoundError:
        errors.append(f"missing {path}")
        return
    present = [needle for needle in needles if needle in text]
    if present:
        errors.append(f"{path} contains forbidden text: {', '.join(present)}")


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--feature-id", default="first-mvp", help="Feature id to validate")
    parser.add_argument("--project-skill", default="project-domain", help="Project skill folder name")
    parser.add_argument(
        "--spec-system",
        choices=["auto", "superpowers", "openspec"],
        default="auto",
        help="Product spec system to validate. auto detects explicit OpenSpec markers.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    feature = slug(args.feature_id)
    project_skill = slug(args.project_skill)
    spec_system = resolve_spec_system(root, args.spec_system)
    errors: list[str] = []
    spec_path = None
    design_path = None
    plan_path = None
    if spec_system == "superpowers":
        spec_path = require_dated_file(
            errors,
            root / "docs" / "superpowers" / "specs",
            f"*-{feature}-spec.md",
            "Superpowers product spec file",
        )
        design_path = require_dated_file(
            errors,
            root / "docs" / "superpowers" / "designs",
            f"*-{feature}-technical-design.md",
            "Superpowers technical design file",
        )
        plan_path = require_dated_file(
            errors,
            root / "docs" / "superpowers" / "plans",
            f"*-{feature}.md",
            "Superpowers implementation plan file",
        )

    for path in [
        root / "AGENTS.md",
        root / ".gitignore",
        root / ".agent" / "agents.md",
        root / ".agent" / "goal-loop-mode.md",
        root / ".agent" / "knowledge" / "candidates" / ".gitkeep",
        root / ".agent" / "skills" / project_skill / "SKILL.md",
        root / "docs" / "architecture.md",
        root / "docs" / "evidence" / f"{feature}.md",
    ]:
        require_file(errors, path)

    if spec_path:
        require_contains(errors, spec_path, [
            "## 意图",
            "## 范围",
            "## 非目标",
            "## 当前事实",
            "## 交付验证",
            "## 验收标准",
            "## 技术设计入口",
            "Technical design owner",
            "## 停止 / 继续条件",
        ])
    if design_path:
        require_contains(errors, design_path, [
            "## 输入与事实来源",
            "## 设计目标",
            "## 当前到目标架构 Delta",
            "## 边界与职责",
            "## 契约",
            "## 控制流 / 数据流",
            "## 错误 / 重试 / 恢复 / 并发 / 幂等",
            "## 安全 / 隐私 / 权限",
            "## 验收到设计到证据",
            "## 设计 Review",
        ])
    if plan_path:
        require_contains(errors, plan_path, [
            "实施计划",
            "Continuous Batch Execution",
            "## 已批准 Spec",
            "## 已批准 Technical Design",
            "## 任务表",
            "## 批次执行",
            "## Review 重点",
            "## 风险 / 缺口",
        ])
        require_absent(errors, plan_path, ["REQUIRED SUB-SKILL", "task-by-task", "superpowers:subagent-driven-development"])
    if spec_system == "openspec":
        require_contains(errors, root / "docs" / "architecture.md", [
            "Product spec system: `openspec`",
            "OpenSpec changes/<change-id>",
            "design.md",
        ])
    require_contains(errors, root / ".gitignore", [
        ".env",
        ".env.*",
        ".agent/runs/*",
        "!.agent/runs/.gitkeep",
    ])
    require_contains(errors, root / "docs" / "evidence" / f"{feature}.md", [
        "## 产品规格系统",
        f"`{spec_system}`",
        "## Claim 上限",
        "## Validators",
        "## Red / 复现证据",
        "## Green / 最终证据",
        "## Deferred / 已接受缺口",
    ])
    require_contains(errors, root / ".agent" / "agents.md", [
        "repo-grounder",
        "spec-reviewer",
        "technical-design-writer",
        "technical-design-reviewer",
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
    print(f"- spec system: {spec_system}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
