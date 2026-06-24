# Skill-Judge Report: Documentation Topology Extension

Date: 2026-06-24

Scope:

- `adaptive-dev-workflow`
- `technical-design`
- `workflow-manifest.schema.json`
- route/e2e evals for `documentation_topology`

## Summary

- **Total Score**: 113/120
- **Grade**: A
- **Pattern**: Process + Navigation hybrid
- **Knowledge Ratio**: E:A:R ~= 81:15:4
- **Verdict**: 这次改动提升了大切片文档分层判断能力，同时没有把小切片拖进重流程；主 router 增加 8 行，仍保持轻量。

## What Changed

Added `design_control.documentation_topology`:

```text
compact
single_file_design
split_design_workspace
```

This makes the control plane decide not only whether a technical design exists, but also how large the spec/design/plan documentation surface should be.

## Dimension Scores

| Dimension | Score | Max | Notes |
| --- | ---: | ---: | --- |
| D1: Knowledge Delta | 19 | 20 | Captures a real production lesson: spec generation does not automatically imply correct design workspace size. |
| D2: Mindset + Procedures | 14 | 15 | Adds a clear slice-size decision model and repo/OpenSpec/Superpowers path adapters. |
| D3: Anti-Pattern Quality | 14 | 15 | Adds explicit anti-patterns: no split docs for tiny changes, no swollen spec for large slices, no duplicate OpenSpec docs. |
| D4: Specification Compliance | 15 | 15 | Frontmatter remains valid; technical-design description now includes topology triggers. |
| D5: Progressive Disclosure | 14 | 15 | Main skill remains 227 lines; detailed topology rules live in `technical-design/references/documentation-topology.md`. |
| D6: Freedom Calibration | 14 | 15 | Low freedom in schema/validator, medium freedom in routing judgment. |
| D7: Pattern Recognition | 9 | 10 | Still follows Process + Navigation hybrid. |
| D8: Practical Usability | 14 | 15 | Deterministic and fresh-agent evals now assert topology behavior. |

## Effect Compared With Previous Version

Improved:

- Large feature work now has an explicit `split_design_workspace` path instead of relying on reviewer memory.
- Small work keeps `compact`, protecting L0/L1 from over-process.
- Standalone design now has two shapes: `single_file_design` and `split_design_workspace`.
- `workflow_manifest.json` can reject invalid combinations such as standalone + compact or split workspace + embedded design.

Cost:

- `adaptive-dev-workflow/SKILL.md` grew from 219 to 227 lines.
- Fresh-agent eval output schema is stricter because it must include `documentation_topology`.

Net result:

```text
Positive. The added control improves routing quality more than it increases context cost.
```

## Validation Evidence

Deterministic:

```text
PASS py_compile
PASS scripts/run-skill-sandbox-eval.py
  - adaptive SKILL.md lines: 227
  - seed cases: 15
  - failure cases: 14
PASS scripts/run-workflow-e2e-eval.py
PASS quick_validate.py for all 7 skill packages
PASS git diff --check
```

Fresh-agent semantic route eval:

```text
PASS tiny-readme-command: L0 / quick-change / none
PASS medium-api-contract: L2 / complex-real-slice / none
PASS large-feature-doc-topology: L3 / complex-real-slice / none
PASS project-harness-init-goal-loop: L3 / complex-real-slice / none
```

Important distinction:

- The fresh-agent route eval validates semantic routing and topology selection.
- It does not prove any concrete project handoff or real external integration.

## Remaining Risks

- `repo_native` vs `fallback` may vary when the user names repo-native paths but the actual repo does not already contain a native docs convention. The eval allows this only where topology is the core assertion.
- `split_design_workspace` should not create files by itself unless the selected spec system and repo convention are clear.
- The next useful improvement is a formal hard/soft assertion model in `seed-cases.yaml` instead of `|`-based accepted ranges.

## Decision

Keep the change.

It captures a reusable expert rule:

```text
Small slices need compact notes.
Medium slices need one technical design.
Large slices need a split design workspace.
```

This belongs in `adaptive-dev-workflow` + `technical-design`, not as a new global skill.
