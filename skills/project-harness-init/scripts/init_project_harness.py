#!/usr/bin/env python3
"""Create a project AI coding harness without overwriting existing files."""

from __future__ import annotations

import argparse
from pathlib import Path


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


def write_if_missing(path: Path, content: str, force: bool, dry_run: bool) -> str:
    if path.exists() and not force:
        return f"skip existing {path}"
    if dry_run:
        action = "would overwrite" if path.exists() else "would write"
        return f"{action} {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    return f"{'overwrite' if path.exists() and force else 'write'} {path}"


def ensure_lines(path: Path, content: str, force: bool, dry_run: bool) -> str:
    if force or not path.exists():
        return write_if_missing(path, content, force, dry_run)

    existing = path.read_text(encoding="utf-8")
    existing_lines = set(existing.splitlines())
    required = [line for line in content.rstrip().splitlines() if line]
    missing = [line for line in required if line not in existing_lines]
    if not missing:
        return f"skip existing {path}"
    if dry_run:
        return f"would append missing lines to {path}: {', '.join(missing)}"

    suffix = "\n" if existing.endswith("\n") else "\n\n"
    path.write_text(existing + suffix + "# project-harness-init guards\n" + "\n".join(missing) + "\n", encoding="utf-8")
    return f"append missing lines to {path}: {', '.join(missing)}"


def touch_if_missing(path: Path, dry_run: bool) -> str:
    if path.exists():
        return f"skip existing {path}"
    if dry_run:
        return f"would touch {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")
    return f"touch {path}"


def gitignore() -> str:
    return """.env
.env.*
!.env.example

.DS_Store

node_modules/
dist/
build/
coverage/

.agent/runs/*
!.agent/runs/.gitkeep
"""


def agents_md() -> str:
    return """# AGENTS.md

项目级 AI coding 协作规则。保持精简；详细 SOP 放到 `.agent/skills/`，当前事实放到 `docs/`。

## 默认流程

- 先读取当前代码、`docs/architecture.md`、相关 spec/plan/evidence，再判断方案。
- 非 Tiny 任务必须先写清 Outcome / Scope / Current Truth / Evidence / Stop Condition。
- 不能没有 fresh verification 就声称完成。
- 不能把 mock-only evidence 描述成真实链路。
- 涉及 public API、data model、auth/permission/security、migration、external side effect 时必须暂停确认。

## 项目记忆

- 使用 `.agent/agents.md` 定义 reviewer/subagent roles。
- 使用 `.agent/goal-loop-mode.md` 交接目标模式任务。
- 使用 `.agent/knowledge/candidates/` 保存未晋升的项目经验。
- 使用 `.agent/skills/<project-domain>/` 保存项目特定 SOP。

## 安全

- 不要把 secrets、tokens、cookies、private logs、生产数据或个人本地路径写入 docs、skills、fixtures、snapshots 或 agent memory。
"""


def agent_team_md() -> str:
    return """# Project Agent Team

## Rules

- Reviewer agents 默认只读；只有任务明确授权时才允许 scoped writes。
- Agents 必须返回 evidence、file paths、uncertainty 和 claim limits。
- Main agent 负责最终 integration 和 completion claims。
- 不要把缺失的 product requirements 交给 subagent 猜。

## Roles

| Role | Trigger | Inputs | Output | Must Not |
| --- | --- | --- | --- | --- |
| repo-grounder | 新区域或 docs 可能过期 | Goal, paths, docs | Current truth map, docs drift, risks | Edit files |
| spec-reviewer | Medium/Large design | Spec, design, acceptance | Gaps, ambiguity, missing delivery verification | Redesign silently |
| plan-reviewer | Before plan execution | Plan, code map | Missing tasks, sequencing risk, missing gates | Implement |
| test-strategy-reviewer | Evidence choice unclear | Spec, changed surfaces | Required validators, claim ceiling | Demand heavy tests for Tiny tasks |
| evidence-reviewer | Before completion | Diff, evidence, final claim | Claim ceiling, gaps, mock/fake/real labels | Accept mock as real |
| security-data-reviewer | Auth/data/secrets/migrations | Spec, diff, threat areas | Boundary risks, negative cases, rollback | Guess compliance |
| knowledge-curator | After MVP or repeated lesson | Candidate, evidence, scope | Promote/reject destination | Write policy directly |
"""


def goal_loop_mode_md() -> str:
    return """# Goal Loop Mode

复制下面 prompt 交给下一个 agent，使其持续迭代到目标达成或遇到人工决策点。

```text
进入 Goal Loop Mode。

目标：
<最终业务/工程目标>

范围：
- In scope:
- Out of scope:

Current Truth：
先读取代码、AGENTS.md、docs/architecture.md、当前 spec/plan/evidence。
如果文档和代码冲突，以代码和 fresh verification 为准，并记录 docs drift。

交付标准：
你不能只完成代码改动。必须给出：
1. acceptance criteria
2. evidence matrix
3. 每项 evidence 的类型：unit / mock / fake / integration / e2e / real external / fresh consumer / manual
4. claim ceiling：Dev Done / Integration Done / Handoff Done
5. 未验证 gap 和风险

Loop 规则：
持续迭代直到所有 acceptance criteria 通过，或者遇到必须人工决策的 blocker。
每轮执行：
1. 选择下一个最小任务
2. 说明预期 evidence
3. 实现或修复
4. 运行 focused validator
5. 更新 evidence
6. 做 diff/scope review
7. 必要时调用 reviewer subagent
8. 判断 continue / stop / ask human

必须暂停：
- public API / data model / permission / security posture 需要改变
- acceptance 或 claim ceiling 需要降低
- 连续两轮验证失败仍无法定位
- 发现 docs/current truth 冲突会影响方案
- 需要真实凭证、生产副作用、破坏性命令或外部写操作

禁止：
- 不允许用 mock-only evidence 声称真实链路打通
- 不允许没有 fresh verification 就说完成
- 不允许 spec 里没有交付验证
- 不允许 reviewer 审自己刚写的实现
- 不允许把项目经验直接写进全局规则；先进入 project learning candidate
```
"""


def project_skill(project_skill: str) -> str:
    return f"""---
name: {project_skill}
description: Project-specific development SOP, architecture context, testing conventions, delivery gotchas, and reusable lessons for this repository. Use when working in this repo after adaptive routing selects project-local context. 当在本项目内开发、修复、重构、测试、交付、沉淀项目经验或需要项目 SOP / architecture / testing context 时使用。
---

# {project_skill}

本 skill 只保存项目特定上下文和 SOP。TDD、debugging、planning、review、verification discipline 仍交给通用执行 skill。

## Current Truth

- 触碰 architecture、contracts、runtime、state、ownership boundaries 时，读取 `references/architecture.md`。
- 选择项目特定 validator / test command / fake-vs-real boundary 时，读取 `references/testing.md`。
- 处理 delivery / onboarding / artifact handoff 时，读取 `references/delivery.md`。
- 遇到重复 pitfall、项目 SOP 或历史经验时，读取 `references/lessons.md`。

## NEVER

- NEVER put secrets, private logs, credentials, cookies, tokens, or local-only paths in this skill.
- NEVER duplicate generic TDD/debug/planning/review workflows here.
- NEVER treat unverified lessons as stable policy.
"""


def repo_architecture_md(feature_label: str, feature_slug: str, project_skill_slug: str) -> str:
    return f"""# Architecture

Current verified architecture facts. Historical decisions belong in `docs/adr/`.

## Current Truth

- This repo has been initialized with an AI coding harness.
- `{feature_label}` is represented by `docs/specs/{feature_slug}/`, `docs/plans/{feature_slug}.md`, and `docs/evidence/{feature_slug}.md`.
- Product runtime, framework, service entrypoints, database schema, API/UI surface, test commands, CI, and deployment targets are not established by this harness.

## Boundaries

- Harness files live in `AGENTS.md`, `.agent/`, `.gitignore`, and `docs/`.
- Project-specific SOP lives in `.agent/skills/{project_skill_slug}/`.
- Future product code must define its own architecture, commands, validators, and ownership boundaries before claiming business delivery.

## Open Decisions

- Product technology stack.
- Product workflow and data model.
- API/UI surface.
- Persistence, concurrency, permissions, deployment, and integration boundaries.
"""


def project_architecture_context(feature_label: str, feature_slug: str, project_skill_slug: str) -> str:
    return f"""# Project Architecture Context

## Current Truth

- Current durable harness entrypoints:
  - `AGENTS.md`
  - `.agent/goal-loop-mode.md`
  - `.agent/agents.md`
  - `.agent/skills/{project_skill_slug}/SKILL.md`
  - `docs/specs/{feature_slug}/spec.md`
  - `docs/specs/{feature_slug}/design.md`
  - `docs/specs/{feature_slug}/acceptance.yaml`
  - `docs/plans/{feature_slug}.md`
  - `docs/evidence/{feature_slug}.md`
- `{feature_label}` product implementation is not proven by harness validation.

## Module Boundaries

- Harness: `AGENTS.md`, `.agent/`, `.gitignore`, `docs/`.
- Project skill: `.agent/skills/{project_skill_slug}/`.
- Product modules: future implementation must document chosen boundaries before coding.

## Contracts / Runtime / State

- No runtime contract is implied by this harness.
- Future public API, persistence, auth, permissions, state machine, external provider, or deployment changes require spec/design updates first.

## Invariants

- Do not treat harness readiness as product readiness.
- Do not introduce product boilerplate before the product spec/design accepts a stack and validator strategy.
- Keep project docs repo-relative; do not store secrets or local-only paths.
"""


def project_testing_context(feature_label: str, project_skill_slug: str) -> str:
    return f"""# Project Testing Context

## Commands

- Harness validation:
  - `python3 <skill-dir>/scripts/validate_project_harness.py --root <repo> --feature-id "{feature_label}" --project-skill {project_skill_slug}`
- Local path hygiene:
  - `rg -n "<local-temp-path>|<home-dir>|<workspace-slug>" AGENTS.md .agent docs`
- Product test commands: not defined yet.

## Fixtures

- No product fixtures are defined by this harness.
- Do not add fixture data until the product data model and test strategy are approved.

## Mock / Fake / Real Boundaries

- Current evidence is manual/harness validation only.
- Mock/fake/integration/e2e/real external evidence is not applicable until product code and runtime boundaries exist.
- Future reports must label fake workflows separately from real persistence, external providers, or production-like chains.

## Evidence Notes

- Current claim ceiling: Dev Done for harness readiness.
- Future product work must update the feature evidence file after each meaningful validator run.
- Passing harness validation does not prove business behavior.
"""


def project_delivery_context(feature_label: str, feature_slug: str) -> str:
    return f"""# Project Delivery Context

## Artifacts

- Current deliverable is a project harness only.
- No package, service, image, build artifact, SDK, CLI, or deployable app exists because of this initialization alone.

## Consumer Path

- Goal Loop handoff path: `.agent/goal-loop-mode.md`.
- Feature contract path: `docs/specs/{feature_slug}/`.
- Execution/evidence path: `docs/plans/{feature_slug}.md` and `docs/evidence/{feature_slug}.md`.

## External Providers

- None configured by this harness.
- Future external provider work requires explicit credentials handling and real/fake evidence separation.

## Secrets / Auth

- Do not write tokens, cookies, credentials, private logs, production data, or local-only paths into docs, fixtures, snapshots, artifacts, or project skill files.
- Use ignored env files or the project-approved secret mechanism when future product code needs credentials.

## Handoff Evidence

- Current handoff evidence is harness validator output and scope review.
- Any future Handoff Done claim requires a fresh consumer path or equivalent onboarding/artifact verification.
"""


def spec_md(feature_label: str, feature_slug: str, project_skill_slug: str) -> str:
    return f"""# Spec: {feature_label}

## Intent

Establish a first vertical slice delivery contract for `{feature_label}` so future agents can enter Goal Loop Mode: align product behavior, implementation boundaries, verification evidence, and stop conditions before writing product code.

## Scope

In scope:

- Maintain the feature contract: spec, design, acceptance matrix, plan, and evidence file.
- Require future implementation to read `AGENTS.md`, `docs/architecture.md`, this spec, design, plan, and evidence before coding.
- Keep product stack, API/UI shape, storage, and deployment decisions explicit instead of implied by the harness.

Out of scope:

- Creating runtime, package manager, framework, database, API, UI, or deployment boilerplate during harness initialization.
- Initializing git or changing repo-external state.
- Claiming `{feature_label}` product functionality is delivered.

## Non-goals

- Do not decide final architecture, data model, authentication, permissions, or production deployment in this harness template.
- Do not create fake product behavior to satisfy acceptance.
- Do not promote unverified lessons into stable SOP.

## Current Truth

- Harness entrypoints:
  - `AGENTS.md`
  - `.agent/goal-loop-mode.md`
  - `.agent/agents.md`
  - `.agent/skills/{project_skill_slug}/SKILL.md`
  - `docs/architecture.md`
  - `docs/specs/{feature_slug}/acceptance.yaml`
  - `docs/plans/{feature_slug}.md`
  - `docs/evidence/{feature_slug}.md`
- Product code, runtime entrypoints, dependencies, tests, and database schema are not proven by this harness.
- If future code and docs conflict, code plus fresh verification wins; record docs drift.

## Behavior

- Trigger: user provides a concrete `{feature_label}` product goal or asks to enter Goal Loop Mode.
- Expected: agent first completes product-level spec/design/acceptance, then implements the smallest vertical slice and updates evidence after each meaningful validator.
- Error / edge: if implementation requires public API, data model, auth/permission/security, external side effects, production dependencies, or claim ceiling changes, stop and ask human.
- Empty state: before product implementation, validation can prove harness readiness only.

## Delivery Verification

- Evidence matrix: `docs/specs/{feature_slug}/acceptance.yaml` and `docs/evidence/{feature_slug}.md` must list validator, type, proves, and gaps.
- Claim ceiling: harness initialization can reach only Dev Done for harness readiness. Product functionality remains Not Started until product validators exist.
- Fresh consumer / real external: not required for harness readiness; required later only if the future claim needs Handoff Done or real integration evidence.
- Human-accepted gaps: technology stack, business workflow, data model, API/UI surface, persistence, and deployment remain undecided until the product spec is completed.

## Acceptance Criteria

- [ ] AC-1: Project harness entrypoints exist: `AGENTS.md`, `.agent/goal-loop-mode.md`, `.agent/agents.md`, project skill, spec, plan, and evidence.
- [ ] AC-2: Feature docs use repo-relative paths or `<skill-dir>/<repo>` placeholders, not machine-specific absolute paths.
- [ ] AC-3: Project-harness validator passes and evidence distinguishes validator type, claim ceiling, and gaps.
- [ ] AC-4: Before product implementation, product acceptance criteria and design decisions are reviewed.

## Stop / Continue Conditions

Continue:

- Continue only within harness docs, project skill, agent roles, goal prompt, and evidence until product spec is approved.
- Future agent may use Goal Loop Mode to complete product spec before implementation.

Stop and ask human:

- Choosing technology stack, storage, API/UI surface, deployment, or external provider.
- Changing public API, data model, auth/permission/security, production dependency, or external protocol.
- Raising claim ceiling from Dev Done to Integration Done or Handoff Done.
"""


def design_md(feature_label: str) -> str:
    return f"""# Design: {feature_label}

## Current Truth

- This design currently covers harness initialization only.
- Product architecture, runtime, data model, API/UI, test suite, CI, and deployment targets are undecided.

## Options

- Option A: Generate only empty templates.
- Option B: Generate a minimal harness and seed `{feature_label}` with objective, evidence, claim ceiling, and stop conditions.
- Option C: Create product stack and demo implementation now.

## Decision

- Choose Option B for harness initialization.
- Defer product stack and implementation until product-level spec/design/acceptance are reviewed.

## Tradeoffs

- Benefit: future agents get stable entrypoints, acceptance files, evidence records, and reviewer roles.
- Cost: no business functionality can be claimed from initialization alone.
- Risk: future agents may confuse harness readiness with product readiness unless claim ceiling stays explicit.

## Data / API / Security Impact

- No product data model, API, permission, auth, production dependency, or external side effect is changed by harness initialization.
- Future data/API/security changes require explicit spec/design updates before implementation.

## Rollout / Rollback

- Rollout: commit harness files only.
- Rollback: revise or remove harness files before product work starts; there is no runtime or migration impact.

## Open Questions

- What is the smallest user workflow for `{feature_label}`?
- What data and state transitions must be modeled?
- What UI/API surface is required?
- Which validators are required for Dev Done, Integration Done, and Handoff Done?
"""


def acceptance_yaml(feature_label: str, feature_slug: str, project_skill_slug: str) -> str:
    return f"""feature_id: {feature_slug}
claim_ceiling: Dev Done
acceptance:
  - id: AC-1
    behavior: "Project harness entrypoints exist for Goal Loop Mode and future {feature_label} work."
    evidence:
      validator: "python3 <skill-dir>/scripts/validate_project_harness.py --root <repo> --feature-id \\"{feature_label}\\" --project-skill {project_skill_slug}"
      type: manual
      proves: "Required harness files, feature docs, and project skill are present."
      gaps: "Does not prove any {feature_label} product behavior."
  - id: AC-2
    behavior: "Generated project docs avoid machine-specific absolute paths."
    evidence:
      validator: "rg -n \\"<local-temp-path>|<home-dir>|<workspace-slug>\\" AGENTS.md .agent docs"
      type: manual
      proves: "No known local-only paths are embedded in generated harness docs."
      gaps: "Pattern scan is not a full secret scanner."
  - id: AC-3
    behavior: "Evidence record states claim ceiling and distinguishes harness readiness from product readiness."
    evidence:
      validator: "manual review of docs/evidence/{feature_slug}.md"
      type: manual
      proves: "Completion claims are bounded to harness Dev Done."
      gaps: "Future product implementation needs its own validators."
non_goals:
  - "Do not implement product code during harness initialization."
  - "Do not initialize git unless explicitly requested."
  - "Do not create framework, package, database, API, UI, or deployment boilerplate."
stop_conditions:
  - "A future step requires choosing product architecture or technology stack."
  - "A future step changes public API, data model, auth, permission, security posture, external protocol, or production dependency."
  - "Claim ceiling needs to be raised beyond Dev Done."
continue_conditions:
  - "Edits remain limited to harness docs, project skill, agent roles, goal prompt, and evidence."
  - "Validation can be done with repo-local file checks and project-harness validator."
"""


def plan_md(feature_label: str, feature_slug: str) -> str:
    return f"""# Plan: {feature_label}

## Approved Spec

- `docs/specs/{feature_slug}/spec.md`
- `docs/specs/{feature_slug}/design.md`
- `docs/specs/{feature_slug}/acceptance.yaml`

## Task Table

| Task | Scope | Gate | Evidence | Done |
| --- | --- | --- | --- | --- |
| 1 | Inspect existing repo conventions | Project Harness Init Gate | `rg --files -uu`; docs/agent file review | pending |
| 2 | Create missing harness files only | project-harness-init script | dry-run then create with feature id `{feature_label}` | pending |
| 3 | Validate harness and local-path hygiene | focused validator | project-harness validator; local path scan | pending |
| 4 | Complete product-level spec/design/acceptance before implementation | spec-reviewer / plan-reviewer | reviewed product acceptance and evidence plan | not started |
| 5 | Future product implementation | adaptive route + Superpowers gates as needed | future tests/integration/e2e evidence | not started |

## Review Points

- Correctness: harness distinguishes `{feature_label}` product readiness from harness readiness.
- Boundary: no product code, git init, runtime, dependency, database, UI/API, or deploy boilerplate unless explicitly requested.
- Evidence: validator type and claim ceiling are explicit; mock/fake/real external are not conflated.
- Safety: docs and project skill must not contain secrets, local-only paths, credentials, private logs, or production data.

## Risks / Gaps

- Product requirements are intentionally incomplete until a product-level spec is approved.
- Current claim ceiling is Dev Done for harness readiness only.
- No automated product tests exist until product code and test commands exist.
"""


def evidence_md(feature_label: str, feature_slug: str, project_skill_slug: str) -> str:
    return f"""# Evidence: {feature_label}

## Claim Ceiling

Dev Done for project harness readiness.

`{feature_label}` product functionality is Not Started.

## Validators

| Validator | Type | Result | Proves | Gaps |
| --- | --- | --- | --- | --- |
| `python3 <skill-dir>/scripts/init_project_harness.py --root <repo> --feature-id "{feature_label}" --project-skill {project_skill_slug} --dry-run` | manual | pending | Planned file set is harness-only before writes. | Dry-run alone does not prove final content quality. |
| `python3 <skill-dir>/scripts/validate_project_harness.py --root <repo> --feature-id "{feature_label}" --project-skill {project_skill_slug}` | manual | pending | Required harness structure, feature docs, acceptance, and project skill exist. | Validator checks structure/contracts, not business correctness. |
| Local path scan using machine-specific patterns | manual | pending | Generated docs do not contain known machine-specific absolute paths. | Not a full secret scan. |

## Red / Reproduction Evidence

- Record whether the repo lacked required harness files before initialization.

## Green / Final Evidence

- Record validator output after initialization.

## Review Evidence

- Scope review should confirm no product code, framework boilerplate, dependency installation, database schema, UI/API, deployment artifact, or git initialization was created unless explicitly requested.

## Deferred / Accepted Gaps

- Product requirements, design decisions, data/API boundaries, runtime validators, and delivery evidence are deferred to a future Goal Loop Mode task.
- No Integration Done or Handoff Done claim is made by harness initialization.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--feature-id", help="Optional feature id for docs/specs/<feature-id>")
    parser.add_argument("--project-skill", default="project-domain", help="Project skill folder name")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    project_skill_slug = slug(args.project_skill)
    feature_label = args.feature_id or "First MVP"
    feature_slug = slug(feature_label)
    actions: list[str] = []

    actions.append(write_if_missing(root / "AGENTS.md", agents_md(), args.force, args.dry_run))
    actions.append(ensure_lines(root / ".gitignore", gitignore(), args.force, args.dry_run))
    actions.append(write_if_missing(root / ".agent" / "agents.md", agent_team_md(), args.force, args.dry_run))
    actions.append(write_if_missing(root / ".agent" / "goal-loop-mode.md", goal_loop_mode_md(), args.force, args.dry_run))
    actions.append(write_if_missing(root / ".agent" / "evals" / "seed-cases.yaml", "cases: []\n", args.force, args.dry_run))
    actions.append(touch_if_missing(root / ".agent" / "knowledge" / "candidates" / ".gitkeep", args.dry_run))
    actions.append(touch_if_missing(root / ".agent" / "runs" / ".gitkeep", args.dry_run))

    skill_root = root / ".agent" / "skills" / project_skill_slug
    actions.append(write_if_missing(skill_root / "SKILL.md", project_skill(project_skill_slug), args.force, args.dry_run))
    actions.append(write_if_missing(skill_root / "references" / "architecture.md", project_architecture_context(feature_label, feature_slug, project_skill_slug), args.force, args.dry_run))
    actions.append(write_if_missing(skill_root / "references" / "testing.md", project_testing_context(feature_label, project_skill_slug), args.force, args.dry_run))
    actions.append(write_if_missing(skill_root / "references" / "delivery.md", project_delivery_context(feature_label, feature_slug), args.force, args.dry_run))
    actions.append(write_if_missing(skill_root / "references" / "lessons.md", "# Project Lessons\n\nOnly promote lessons after evidence, scope, and destination review.\n\n## Promoted Lessons\n\n## Rejected / Expired Lessons\n", args.force, args.dry_run))

    actions.append(write_if_missing(root / "docs" / "architecture.md", repo_architecture_md(feature_label, feature_slug, project_skill_slug), args.force, args.dry_run))
    actions.append(touch_if_missing(root / "docs" / "adr" / ".gitkeep", args.dry_run))
    actions.append(touch_if_missing(root / "docs" / "specs" / "archived" / ".gitkeep", args.dry_run))

    spec_dir = root / "docs" / "specs" / feature_slug
    actions.append(write_if_missing(spec_dir / "spec.md", spec_md(feature_label, feature_slug, project_skill_slug), args.force, args.dry_run))
    actions.append(write_if_missing(spec_dir / "design.md", design_md(feature_label), args.force, args.dry_run))
    actions.append(write_if_missing(spec_dir / "acceptance.yaml", acceptance_yaml(feature_label, feature_slug, project_skill_slug), args.force, args.dry_run))
    actions.append(touch_if_missing(spec_dir / "changes" / ".gitkeep", args.dry_run))
    actions.append(write_if_missing(root / "docs" / "plans" / f"{feature_slug}.md", plan_md(feature_label, feature_slug), args.force, args.dry_run))
    actions.append(write_if_missing(root / "docs" / "evidence" / f"{feature_slug}.md", evidence_md(feature_label, feature_slug, project_skill_slug), args.force, args.dry_run))

    for action in actions:
        print(action)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
