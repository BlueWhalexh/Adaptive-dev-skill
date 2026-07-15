#!/usr/bin/env python3
"""Create a project AI coding harness without overwriting existing files."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path


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

## 语言

- 人读文档默认中文，包括 spec、plan、evidence、architecture、project skill 和 review notes。
- 文件名、路径、命令、JSON/schema 字段、validator type、skill 名称和工具报错保留英文。

## 默认流程

- 先读取当前代码、`docs/architecture.md`、相关 spec/technical design/plan/evidence，再判断方案。
- 非 L0/L1 任务必须先写清目标、范围、当前事实、证据和停止条件；已有 READY artifact 未发生实质变化时直接复用，不重复生成或复审。
- Plan checkbox 只跟踪进度，不自动成为 subagent、Review、commit、report 或 workflow manifest 边界。
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
    return """# 项目 Agent 团队

## 规则

- Reviewer agents 默认只读；只有任务明确授权时才允许 scoped writes。
- Agents 必须返回 evidence、file paths、uncertainty 和 claim limits。
- Main agent 负责最终 integration 和 completion claims。
- 不要把缺失的 product requirements 交给 subagent 猜。
- 连续低风险 Tasks 默认由同一 implementer 按 batch 执行；每 Task 只跑 focused signal，batch 再统一做 adjacent regression、Review、commit 和汇报。
- 只有高风险边界、独立并行工作或上下文污染风险才创建 fresh subagent / separate session。

## 角色

| Role | Trigger | Inputs | Output | Must Not |
| --- | --- | --- | --- | --- |
| repo-grounder | 新区域或 docs 可能过期 | Goal, paths, docs | Current truth map, docs drift, risks | Edit files |
| spec-reviewer | New or materially changed product contract | Spec, acceptance | Gaps, ambiguity, missing delivery verification | Rewrite product silently |
| technical-design-writer | Approved spec before planning | Spec, current truth, constraints | Technical design draft, contracts, risks, evidence mapping | Write implementation plan/code |
| technical-design-reviewer | Standalone design required | Technical design, spec, context | Design findings, missing boundaries, review decision | Review own design |
| plan-reviewer | New/changed high-impact plan or uncertain sequencing | Plan, code map | Missing tasks, sequencing risk, missing gates | Implement |
| test-strategy-reviewer | Evidence choice unclear | Spec, changed surfaces | Required validators, claim ceiling | Demand heavy tests for Tiny tasks |
| evidence-reviewer | Integration/handoff claim or material evidence gap | Diff, evidence, final claim | Claim ceiling, gaps, mock/fake/real labels | Accept mock as real |
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
先读取代码、AGENTS.md、docs/architecture.md、当前 spec/technical design/plan/evidence。
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
执行节奏：
1. 复用已批准 spec/design/plan，按 Task 局部风险组建连续低风险 batch
2. 每个 Task 只定义并运行 focused signal；文档/机械改动使用最小 validator
3. batch 内更新 Plan checkbox 和简短失败记录，不重复创建 work order、artifact package、manifest transition、commit 或 report
4. batch/milestone 统一运行 adjacent regression、diff/scope review、commit 和进度汇报
5. 仅在 contract/auth/security/data/migration/concurrency/external side effect/architecture/claim 边界调用独立 reviewer
6. Critical/Major 或契约变化修复后最多做一次 delta re-review；Minor 不重启完整 Review loop
7. 判断 continue / stop / ask human

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
- 不允许高风险任务跳过 approved technical design
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

## 语言

- 人读项目文档默认中文。
- 命令、路径、validator type、schema 字段和报错原文保留英文。

## 当前事实

- 触碰 architecture、contracts、runtime、state、ownership boundaries 时，读取 `references/architecture.md`。
- 选择项目特定 validator / test command / fake-vs-real boundary 时，读取 `references/testing.md`。
- 处理 delivery / onboarding / artifact handoff 时，读取 `references/delivery.md`。
- 遇到重复 pitfall、项目 SOP 或历史经验时，读取 `references/lessons.md`。

## 禁止

- NEVER 把 secrets、private logs、credentials、cookies、tokens 或 local-only paths 写进本 skill。
- NEVER 在这里重复通用 TDD/debug/planning/review workflows。
- NEVER 把未验证 lessons 当成 stable policy。
"""


def repo_architecture_md(feature_label: str, feature_slug: str, project_skill_slug: str, spec_system: str, spec_path: str, design_path: str, plan_path: str) -> str:
    return f"""# 架构

当前已验证的架构事实。历史决策放在 `docs/adr/`。

## 语言

人读说明默认中文；路径、命令、schema 字段和 validator type 保留英文。

## 当前事实

- 这个仓库已初始化 AI coding harness。
- Product spec system: `{spec_system}`.
- `{feature_label}` 当前由 `{spec_path}`、`{design_path}`、`{plan_path}` 和 `docs/evidence/{feature_slug}.md` 表示。
- 本 harness 不建立产品 runtime、framework、service entrypoint、database schema、API/UI surface、test commands、CI 或 deployment target。

## 边界

- Harness 文件位于 `AGENTS.md`、`.agent/`、`.gitignore` 和 `docs/`。
- 项目特定 SOP 位于 `.agent/skills/{project_skill_slug}/`。
- 后续产品代码在声称业务交付前，必须定义自己的架构、命令、validators 和 ownership boundaries。

## 待决策

- 产品技术栈。
- 产品 workflow 和 data model。
- API/UI surface。
- persistence、concurrency、permissions、deployment 和 integration boundaries。
"""


def project_architecture_context(feature_label: str, feature_slug: str, project_skill_slug: str, spec_system: str, spec_path: str, design_path: str, plan_path: str) -> str:
    return f"""# 项目架构上下文

## 当前事实

- 当前 durable harness entrypoints:
  - `AGENTS.md`
  - `.agent/goal-loop-mode.md`
  - `.agent/agents.md`
  - `.agent/skills/{project_skill_slug}/SKILL.md`
  - Product spec system: `{spec_system}`
  - `{spec_path}`
  - `{design_path}`
  - `{plan_path}`
  - `docs/evidence/{feature_slug}.md`
- `{feature_label}` 的产品实现尚未被 harness validation 证明。

## 模块边界

- Harness: `AGENTS.md`, `.agent/`, `.gitignore`, `docs/`.
- Project skill: `.agent/skills/{project_skill_slug}/`.
- Product modules: 后续实现前必须先记录选择的边界。

## Contracts / Runtime / State 约束

- 本 harness 不暗示任何 runtime contract。
- 后续 public API、persistence、auth、permissions、state machine、external provider 或 deployment 变化，必须先更新 product spec 和 technical design。

## 不变量

- 不要把 harness ready 当成 product ready。
- 产品 spec/design 接受技术栈和 validator strategy 前，不要引入 product boilerplate。
- 项目 docs 保持 repo-relative；不要存 secrets 或 local-only paths。
"""


def project_testing_context(feature_label: str, project_skill_slug: str, spec_system: str) -> str:
    return f"""# 项目测试上下文

## 命令

- Harness validation:
  - `python3 <skill-dir>/scripts/validate_project_harness.py --root <repo> --feature-id "{feature_label}" --project-skill {project_skill_slug} --spec-system {spec_system}`
- Local path hygiene:
  - `rg -n "<local-temp-path>|<home-dir>|<workspace-slug>" AGENTS.md .agent docs`
- Product test commands: not defined yet.

## 测试夹具

- 本 harness 不定义 product fixtures。
- product data model 和 test strategy 被批准前，不要添加 fixture data。

## Mock / Fake / Real 边界

- 当前 evidence 仅为 manual/harness validation。
- product code 和 runtime boundaries 存在前，不适用 mock/fake/integration/e2e/real external evidence。
- 后续报告必须把 fake workflow 和 real persistence、external providers、production-like chains 分开标注。

## Evidence 备注

- 当前 claim 上限：Dev Done for harness readiness。
- 后续 product work 每次有 meaningful validator run 后，必须更新 feature evidence 文件。
- harness validation 通过不证明业务行为。
"""


def project_delivery_context(feature_label: str, feature_slug: str, spec_system: str, spec_path: str, design_path: str, plan_path: str) -> str:
    return f"""# 项目交付上下文

## 产物

- 当前 deliverable 只有 project harness。
- 单独初始化不会产生 package、service、image、build artifact、SDK、CLI 或 deployable app。

## Consumer 路径

- Goal Loop handoff path: `.agent/goal-loop-mode.md`.
- Product spec system: `{spec_system}`.
- Feature contract path: `{spec_path}`.
- Technical design path: `{design_path}`.
- Execution/evidence path: `{plan_path}` and `docs/evidence/{feature_slug}.md`.

## External Providers

- 本 harness 不配置 external providers。
- 后续 external provider 工作需要明确 credentials handling，并区分 real/fake evidence。

## Secrets / Auth

- 不要把 tokens、cookies、credentials、private logs、production data 或 local-only paths 写入 docs、fixtures、snapshots、artifacts 或 project skill files。
- 后续 product code 需要 credentials 时，使用 ignored env files 或项目批准的 secret 机制。

## Handoff Evidence

- 当前 handoff evidence 是 harness validator output 和 scope review。
- 后续任何 Handoff Done claim 都需要 fresh consumer path 或等价 onboarding/artifact verification。
"""


def spec_md(feature_label: str, feature_slug: str, project_skill_slug: str, spec_path: str, design_path: str, plan_path: str) -> str:
    return f"""# {feature_label} 产品规格

> 人读文档默认中文；路径、命令、schema 字段、validator type、skill 名称和工具报错保留英文。

## 意图

为 `{feature_label}` 建立 first vertical slice product contract，使后续 agent 在进入 Goal Loop Mode 前先对齐产品目标、范围、行为、验收和交付验证，而不是直接写 product code。

## 范围

In scope:

- 维护 feature contract：product spec、technical design、implementation plan 和 evidence file。
- 要求后续实现前读取 `AGENTS.md`、`docs/architecture.md`、本 spec/technical design/plan/evidence。
- 明确 product stack、API/UI shape、storage 和 deployment decisions；不要让 harness 隐式决定它们。

Out of scope:

- 在 harness 初始化期间创建 runtime、package manager、framework、database、API、UI 或 deployment boilerplate。
- 初始化 git 或改变 repo-external state。
- 声称 `{feature_label}` 产品功能已经交付。

## 非目标

- 不在本 harness template 中决定最终 architecture、data model、authentication、permissions 或 production deployment。
- 不创建 fake product behavior 来满足 acceptance。
- 不把未验证经验晋升为 stable SOP。

## 当前事实

- Harness entrypoints:
  - `AGENTS.md`
  - `.agent/goal-loop-mode.md`
  - `.agent/agents.md`
  - `.agent/skills/{project_skill_slug}/SKILL.md`
  - `docs/architecture.md`
  - `{spec_path}`
  - `{design_path}`
  - `{plan_path}`
  - `docs/evidence/{feature_slug}.md`
- Product code、runtime entrypoints、dependencies、tests 和 database schema 不由本 harness 证明。
- 如果后续 code 和 docs 冲突，以 code + fresh verification 为准，并记录 docs drift。

## 行为

- Trigger：用户提供具体 `{feature_label}` 产品目标，或要求进入 Goal Loop Mode。
- Expected：agent 先完成 product-level spec/design/acceptance，再实现最小 vertical slice，并在每次 meaningful validator 后更新 evidence。
- Error / edge：如果实现需要改变 public API、data model、auth/permission/security、external side effects、production dependencies 或 claim 上限，停止并询问人类。
- Empty state：产品实现前，validation 只能证明 harness readiness。

## 交付验证

- Evidence matrix：本 Superpowers-compatible spec 和 `docs/evidence/{feature_slug}.md` 必须列出 validator、type、proves 和 gaps。
- Claim 上限：harness initialization 只能达到 Dev Done for harness readiness。product functionality 在 product validators 存在前仍是 Not Started。
- Fresh consumer / real external：harness readiness 不需要；只有未来 claim 需要 Handoff Done 或 real integration evidence 时才需要。
- Human-accepted gaps：technology stack、business workflow、data model、API/UI surface、persistence 和 deployment 在 product spec 完成前保持未决。

## 验收标准

- [ ] AC-1: Project harness entrypoints exist: `AGENTS.md`, `.agent/goal-loop-mode.md`, `.agent/agents.md`, project skill, spec, plan, and evidence.
- [ ] AC-2: Feature docs use repo-relative paths or `<skill-dir>/<repo>` placeholders, not machine-specific absolute paths.
- [ ] AC-3: Project-harness validator passes and evidence distinguishes validator type, claim ceiling, and gaps.
- [ ] AC-4: Before product implementation, product acceptance criteria and technical design decisions are reviewed.

## 技术设计入口

- Technical design owner: `{design_path}`.
- 本 product spec 不承载架构决策、模块边界、API/data/state contracts、migration、observability 或 rollback 细节。
- 后续 public API、data/auth/security、state machine、cross-service、external integration 或 runtime 变化必须先批准 technical design。

## 未决问题

- `{feature_label}` 的最小 user workflow 是什么？
- 需要建模哪些 data 和 state transitions？
- 需要什么 UI/API surface？
- Dev Done、Integration Done、Handoff Done 分别需要哪些 validators？

## 停止 / 继续条件

Continue:

- product spec 被批准前，只在 harness docs、project skill、agent roles、goal prompt 和 evidence 范围内继续。
- 后续 agent 可以使用 Goal Loop Mode 在实现前完成 product spec。

Stop and ask human:

- 选择 technology stack、storage、API/UI surface、deployment 或 external provider。
- 改变 public API、data model、auth/permission/security、production dependency 或 external protocol。
- 将 claim 上限从 Dev Done 提升到 Integration Done 或 Handoff Done。
"""


def technical_design_md(feature_label: str, spec_path: str, design_path: str, plan_path: str) -> str:
    return f"""# {feature_label} 技术设计

> 人读文档默认中文；路径、命令、schema 字段、validator type、skill 名称和工具报错保留英文。

## 输入与事实来源

- Product spec: `{spec_path}`
- Technical design: `{design_path}`
- Implementation plan: `{plan_path}`
- Current truth: `docs/architecture.md` and repo code.

## 设计目标

- 为 `{feature_label}` 的 first vertical slice 固化架构边界、技术契约、风险和验证方式。
- 在 plan 执行前明确哪些决策已批准、哪些必须暂停询问人类。

## 当前到目标架构 Delta

- 当前：仅初始化 harness，尚未证明 product runtime。
- 目标：后续实现前补齐 product architecture、contracts、state/data flow、validators 和 rollback plan。

## 边界与职责

- Product Spec 只定义目标、范围、行为和验收。
- Technical Design 定义架构、边界、契约、数据/控制流、failure/recovery/security/migration/observability/rollback。
- Implementation Plan 只定义执行顺序、任务、文件、验证和 review gate。

## 契约

- Public API / event / schema / storage / state contracts: pending product decision.
- Any contract change requires design review before implementation.

## 控制流 / 数据流

- Pending product workflow.
- Do not infer data flow from harness files.

## 错误 / 重试 / 恢复 / 并发 / 幂等

- Pending product runtime decision.
- If needed, define retry, idempotency, recovery and rollback before plan execution.

## 安全 / 隐私 / 权限

- Harness initialization writes no secrets and changes no auth/permission boundary.
- Future auth, PII, secrets or security posture changes require explicit review.

## 性能 / 可运维 / 可观测性

- Pending product runtime decision.
- Future delivery must define logs/metrics/traces or equivalent observability where relevant.

## 兼容性 / 迁移 / 回滚

- Harness files can be edited or removed before product work starts.
- No runtime migration exists yet.

## 验收到设计到证据

| Acceptance | Design mechanism | Planned evidence |
| --- | --- | --- |
| Harness entrypoints exist | Deterministic scaffold | `validate_project_harness.py` |
| Product implementation does not start early | Stop gates in spec/design/plan | Scope review |
| No false handoff claim | Evidence file claim ceiling | Evidence review |

## 设计 Review

- Status: ready_for_user_review.
- Reviewer: pending.
- Blocking decisions: product technology stack, workflow, data model, API/UI surface, persistence, deployment.
"""


def plan_md(feature_label: str, spec_path: str, design_path: str) -> str:
    return f"""# {feature_label} 实施计划

> **Execution policy:** Use Continuous Batch Execution. Plan checkboxes track progress; they are not mandatory subagent, Review, commit, report, artifact package, or workflow-state boundaries. Do not create an isolated execution ceremony for each checkbox.

**目标：** 建立 project harness，并为后续 first vertical slice implementation 做准备。

**架构：** 本 plan 只覆盖 harness initialization。Product architecture 必须在 approved technical design 后执行。

**技术栈：** harness initialization 不选择技术栈。

---

## 已批准 Spec

- `{spec_path}`

## 已批准 Technical Design

- `{design_path}`

## 任务表

| 任务 | 范围 | Gate | Evidence | Done |
| --- | --- | --- | --- | --- |
| 1 | 检查现有 repo convention | Project Harness Init Gate | `rg --files -uu`; docs/agent file review | pending |
| 2 | 只创建缺失 harness files | project-harness-init script | dry-run 后按 `{feature_label}` 创建 | pending |
| 3 | 验证 harness 和 local-path hygiene | focused validator | project-harness validator; local path scan | pending |
| 4 | 实现前完成 product-level spec/design/acceptance | spec-reviewer / technical-design-reviewer / plan-reviewer | reviewed product acceptance, technical design, and evidence plan | not started |
| 5 | 后续 product implementation | adaptive route + Superpowers gates as needed | future tests/integration/e2e evidence | not started |

## 批次执行

- 每个 Task 按 changed surface 和 uncertainty 重新判断局部风险；父级风险只控制最终交付 gate。
- 连续低风险 Tasks 合并为 batch：每 Task 跑 focused signal，batch 末统一跑 adjacent regression、Review、commit 和汇报。
- 高风险边界或 completion claim 才启用独立严格 Review；Minor finding 不触发无限复审。

## Review 重点

- Correctness：harness 区分 `{feature_label}` product readiness 和 harness readiness。
- Boundary：除非明确要求，不创建 product code、git init、runtime、dependency、database、UI/API 或 deploy boilerplate。
- Evidence：validator type 和 claim 上限明确；mock/fake/real external 不混淆。
- Safety：docs 和 project skill 不能包含 secrets、local-only paths、credentials、private logs 或 production data。

## 风险 / 缺口

- product-level spec 被批准前，Product requirements 有意保持不完整。
- 当前 claim 上限只是 Dev Done for harness readiness。
- product code 和 test commands 存在前，没有 automated product tests。
"""


def evidence_md(feature_label: str, feature_slug: str, project_skill_slug: str, spec_system: str, spec_path: str, design_path: str, plan_path: str) -> str:
    return f"""# 证据：{feature_label}

## 产品规格系统

`{spec_system}`

Feature contract owner：`{spec_path}`

Technical design owner：`{design_path}`

Execution plan owner：`{plan_path}`

## Claim 上限

Dev Done for project harness readiness.

`{feature_label}` product functionality is Not Started.

## Validators

| Validator | Type | Result | Proves | Gaps |
| --- | --- | --- | --- | --- |
| `python3 <skill-dir>/scripts/init_project_harness.py --root <repo> --feature-id "{feature_label}" --project-skill {project_skill_slug} --spec-system {spec_system} --dry-run` | manual | pending | Planned file set is harness-only before writes. | Dry-run alone does not prove final content quality. |
| `python3 <skill-dir>/scripts/validate_project_harness.py --root <repo> --feature-id "{feature_label}" --project-skill {project_skill_slug} --spec-system {spec_system}` | manual | pending | Required harness structure, spec-system routing, evidence, and project skill exist. | Validator checks structure/contracts, not business correctness. |
| Local path scan using machine-specific patterns | manual | pending | Generated docs do not contain known machine-specific absolute paths. | Not a full secret scan. |

## Red / 复现证据

- 记录初始化前 repo 是否缺少 required harness files。

## Green / 最终证据

- 记录初始化后的 validator output。

## Review 证据

- Scope review 应确认：除非明确要求，否则未创建 product code、framework boilerplate、dependency installation、database schema、UI/API、deployment artifact 或 git initialization。

## Deferred / 已接受缺口

- Product requirements、design decisions、data/API boundaries、runtime validators 和 delivery evidence 推迟到未来 Goal Loop Mode 任务。
- harness initialization 不声明 Integration Done 或 Handoff Done。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--feature-id", help="Optional feature id for evidence and fallback spec/plan files")
    parser.add_argument("--project-skill", default="project-domain", help="Project skill folder name")
    parser.add_argument(
        "--spec-system",
        choices=["auto", "superpowers", "openspec"],
        default="auto",
        help="Product spec system. auto uses OpenSpec when explicit OpenSpec markers exist, otherwise Superpowers docs.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    project_skill_slug = slug(args.project_skill)
    feature_label = args.feature_id or "First MVP"
    feature_slug = slug(feature_label)
    today = date.today().isoformat()
    spec_system = resolve_spec_system(root, args.spec_system)
    if spec_system == "openspec":
        spec_path = "OpenSpec changes/<change-id>/{proposal.md,specs/}"
        design_path = "OpenSpec changes/<change-id>/design.md"
        plan_path = "OpenSpec changes/<change-id>/tasks.md; Superpowers writing-plans may derive detailed plans during implementation"
    else:
        spec_path = f"docs/superpowers/specs/{today}-{feature_slug}-spec.md"
        design_path = f"docs/superpowers/designs/{today}-{feature_slug}-technical-design.md"
        plan_path = f"docs/superpowers/plans/{today}-{feature_slug}.md"
    actions: list[str] = []
    actions.append(f"spec-system {spec_system}")

    actions.append(write_if_missing(root / "AGENTS.md", agents_md(), args.force, args.dry_run))
    actions.append(ensure_lines(root / ".gitignore", gitignore(), args.force, args.dry_run))
    actions.append(write_if_missing(root / ".agent" / "agents.md", agent_team_md(), args.force, args.dry_run))
    actions.append(write_if_missing(root / ".agent" / "goal-loop-mode.md", goal_loop_mode_md(), args.force, args.dry_run))
    actions.append(write_if_missing(root / ".agent" / "evals" / "seed-cases.yaml", "cases: []\n", args.force, args.dry_run))
    actions.append(touch_if_missing(root / ".agent" / "knowledge" / "candidates" / ".gitkeep", args.dry_run))
    actions.append(touch_if_missing(root / ".agent" / "runs" / ".gitkeep", args.dry_run))

    skill_root = root / ".agent" / "skills" / project_skill_slug
    actions.append(write_if_missing(skill_root / "SKILL.md", project_skill(project_skill_slug), args.force, args.dry_run))
    actions.append(write_if_missing(skill_root / "references" / "architecture.md", project_architecture_context(feature_label, feature_slug, project_skill_slug, spec_system, spec_path, design_path, plan_path), args.force, args.dry_run))
    actions.append(write_if_missing(skill_root / "references" / "testing.md", project_testing_context(feature_label, project_skill_slug, spec_system), args.force, args.dry_run))
    actions.append(write_if_missing(skill_root / "references" / "delivery.md", project_delivery_context(feature_label, feature_slug, spec_system, spec_path, design_path, plan_path), args.force, args.dry_run))
    actions.append(write_if_missing(skill_root / "references" / "lessons.md", "# 项目经验\n\n只有经过 evidence、scope 和 destination review 后，才能晋升 lessons。\n\n## 已晋升经验\n\n## 已拒绝 / 已过期经验\n", args.force, args.dry_run))

    actions.append(write_if_missing(root / "docs" / "architecture.md", repo_architecture_md(feature_label, feature_slug, project_skill_slug, spec_system, spec_path, design_path, plan_path), args.force, args.dry_run))
    actions.append(touch_if_missing(root / "docs" / "adr" / ".gitkeep", args.dry_run))
    if spec_system == "superpowers":
        actions.append(write_if_missing(root / spec_path, spec_md(feature_label, feature_slug, project_skill_slug, spec_path, design_path, plan_path), args.force, args.dry_run))
        actions.append(write_if_missing(root / design_path, technical_design_md(feature_label, spec_path, design_path, plan_path), args.force, args.dry_run))
        actions.append(write_if_missing(root / plan_path, plan_md(feature_label, spec_path, design_path), args.force, args.dry_run))
    actions.append(write_if_missing(root / "docs" / "evidence" / f"{feature_slug}.md", evidence_md(feature_label, feature_slug, project_skill_slug, spec_system, spec_path, design_path, plan_path), args.force, args.dry_run))

    for action in actions:
        print(action)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
