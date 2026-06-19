#!/usr/bin/env python3
"""Create the smallest adaptive project harness without overwriting files."""

from __future__ import annotations

import argparse
from pathlib import Path


def write_if_missing(path: Path, content: str, force: bool, dry_run: bool) -> str:
    if path.exists() and not force:
        return f"skip existing {path}"
    if dry_run:
        return f"would write {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    return f"write {path}"


def touch_if_missing(path: Path, dry_run: bool) -> str:
    if path.exists():
        return f"skip existing {path}"
    if dry_run:
        return f"would touch {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")
    return f"touch {path}"


def slug(value: str) -> str:
    cleaned = []
    for char in value.lower():
        if char.isalnum():
            cleaned.append(char)
        elif char in {"-", "_", " ", "."}:
            cleaned.append("-")
    result = "".join(cleaned).strip("-")
    while "--" in result:
        result = result.replace("--", "-")
    return result or "project-domain"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project root to initialize")
    parser.add_argument("--feature-id", help="Optional docs/specs/<feature-id> scaffold")
    parser.add_argument("--project-skill", default="project-domain", help="Project skill folder name")
    parser.add_argument("--force", action="store_true", help="Overwrite existing scaffold files")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    project_skill = slug(args.project_skill)
    actions: list[str] = []

    actions.append(write_if_missing(root / "AGENTS.md", """# AGENTS.md

项目级 agent 协作规则。保持精简；详细 SOP 放到 `.agent/skills/`，当前架构事实放到 `docs/`。

- Follow existing architecture, commands, style, and test harness.
- 使用 `.agent/agents.md` 维护可复用 reviewer/subagent roles。
- 使用 `.agent/knowledge/candidates/` 保存未晋升的项目经验。
- 不要把 secrets、credentials、raw logs、个人本地路径或一次性假设写入 agent memory 文件。
""", args.force, args.dry_run))

    actions.append(write_if_missing(root / ".agent" / "agents.md", """# Project Agent Team

## Rules

- Review agents 默认只读；只有任务明确授权时才允许 scoped writes。
- Agents 必须返回 evidence、file paths、uncertainty 和 claim limits。
- Main agent 负责最终 integration 和 completion claims。
- 不要把缺失的 product requirements 交给 subagent 猜。

## Roles

| Role | Trigger | Inputs | Output | Must Not |
| --- | --- | --- | --- | --- |
| repo-grounder | 新区域或 docs 可能过期 | Goal, paths, docs | Current truth map, risks | Edit files |
| spec-reviewer | Medium/Large design | Spec, acceptance | Gaps, ambiguity, risk | Redesign silently |
| plan-reviewer | Before plan execution | Plan, code map | Missing tasks/gates | Implement |
| evidence-reviewer | Before completion | Diff, evidence | Claim ceiling, gaps | Accept mock as real |
| security-data-reviewer | Auth/data/secrets | Diff, threat areas | Boundary risks | Guess compliance |
| knowledge-curator | Task exit | Candidate, evidence | Promote/reject advice | Write policy directly |
""", args.force, args.dry_run))

    actions.append(write_if_missing(root / ".agent" / "evals" / "seed-cases.yaml", """# Project-specific adaptive eval cases.
# 添加 raw prompts、expected route、required evidence 和 observed failures。
cases: []
""", args.force, args.dry_run))

    actions.append(touch_if_missing(root / ".agent" / "knowledge" / "candidates" / ".gitkeep", args.dry_run))
    actions.append(touch_if_missing(root / ".agent" / "runs" / ".gitkeep", args.dry_run))

    skill_root = root / ".agent" / "skills" / project_skill
    actions.append(write_if_missing(skill_root / "SKILL.md", f"""---
name: {project_skill}
description: Project-specific development SOP, architecture context, testing conventions, delivery gotchas, and reusable lessons for this repository. Use when working in this repo after general adaptive routing selects project-local context. 当在本项目内开发、修复、重构、测试、交付、沉淀项目经验或需要项目 SOP / architecture / testing context 时使用。
---

# {project_skill}

本 skill 只保存项目特定上下文和 SOP。TDD、debugging、planning、review、verification discipline 仍交给 Superpowers / adaptive 路由的执行 skill。

## Current Truth

- 触碰 architecture、contracts、runtime、state、ownership boundaries 时，读取 `references/architecture.md`。
- 选择项目特定 validator / test command / fake-vs-real boundary 时，读取 `references/testing.md`。
- 遇到重复 pitfall、项目 SOP 或历史经验时，读取 `references/lessons.md`。

## Trigger Hints

- 新功能、bugfix、refactor 需要项目架构约束。
- 测试矩阵需要项目真实命令、fixture、mock/fake/real 边界。
- 交付、onboarding、SDK/package/runtime handoff 需要项目特定步骤。
- 用户指出“这个项目之前不是这样做的”或重复补充项目经验。

## NEVER

- NEVER put secrets, private logs, credentials, cookies, tokens, or local-only paths in this skill.
- NEVER duplicate generic coding advice or Superpowers workflows here.
- NEVER treat unverified lessons as stable policy.
""", args.force, args.dry_run))

    actions.append(write_if_missing(skill_root / "references" / "architecture.md", """# Project Architecture Context

记录当前已经验证的 architecture facts。优先链接 canonical repo docs 和 code paths，不要只写聊天记忆。

## Current Truth

## Module Boundaries

## Contracts / Runtime / State

## Invariants
""", args.force, args.dry_run))
    actions.append(write_if_missing(skill_root / "references" / "testing.md", """# Project Testing Context

记录项目特定 test commands、fixtures、fake-vs-real boundaries 和 validator caveats。

## Commands

## Fixtures

## Mock / Fake / Real Boundaries

## Evidence Notes
""", args.force, args.dry_run))
    actions.append(write_if_missing(skill_root / "references" / "lessons.md", """# Project Lessons

只从 `.agent/knowledge/candidates/` 晋升重复出现、已有 evidence、scope 清晰的经验。

## Promoted Lessons

## Rejected / Expired Lessons
""", args.force, args.dry_run))

    actions.append(write_if_missing(root / "docs" / "architecture.md", """# Architecture

当前已验证的架构事实，供 humans 和 agents 共同使用。历史方案和取舍放到 ADR。
""", args.force, args.dry_run))
    actions.append(touch_if_missing(root / "docs" / "adr" / ".gitkeep", args.dry_run))
    actions.append(touch_if_missing(root / "docs" / "specs" / "archived" / ".gitkeep", args.dry_run))

    if args.feature_id:
        feature_slug = slug(args.feature_id)
        spec_dir = root / "docs" / "specs" / feature_slug
        plan_path = root / "docs" / "plans" / f"{feature_slug}.md"
        evidence_path = root / "docs" / "evidence" / f"{feature_slug}.md"
        actions.append(write_if_missing(spec_dir / "spec.md", """# Spec

## Intent
目标 / 用户价值

## Scope
范围

## Non-goals
非目标

## Acceptance
验收标准
""", args.force, args.dry_run))
        actions.append(write_if_missing(spec_dir / "design.md", """# Design

## Current Truth
当前事实

## Options
方案选项

## Decision
决策

## Risks
风险
""", args.force, args.dry_run))
        actions.append(touch_if_missing(spec_dir / "changes" / ".gitkeep", args.dry_run))
        actions.append(write_if_missing(plan_path, """# Plan

| Task | Scope | Gate | Evidence | Done |
| --- | --- | --- | --- | --- |
""", args.force, args.dry_run))
        actions.append(write_if_missing(spec_dir / "acceptance.yaml", """acceptance: []
non_goals: []
claim_ceiling: Dev Done
""", args.force, args.dry_run))
        actions.append(write_if_missing(evidence_path, """# Evidence

## Commit

## Acceptance

## Validators

| Validator | Type | Result | Proves | Gaps |
| --- | --- | --- | --- | --- |
|  | unit / mock / fake / integration / e2e / real external / fresh consumer / manual |  |  |  |

## Results

## Gaps

## Claim Ceiling
""", args.force, args.dry_run))

    for action in actions:
        print(action)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
