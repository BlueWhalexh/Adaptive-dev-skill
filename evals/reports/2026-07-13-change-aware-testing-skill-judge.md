# Skill Judge Report: change-aware-testing

## Summary

- Total: 110/120 (91.7%)
- Grade: A
- Pattern: Process + Tool
- Knowledge ratio: E:A:R = 76:19:5
- Verdict: 该 skill 把“每次全量测试”替换为可执行的 cadence、显式影响映射和保守升级机制，职责边界清楚，可以进入生产试用。

## Dimension Scores

| Dimension | Score | Max | Notes |
| --- | ---: | ---: | --- |
| Knowledge Delta | 18 | 20 | 明确区分 inner-loop/checkpoint/completion，并处理 global-impact 与 unmapped diff。 |
| Mindset + Procedures | 14 | 15 | 先计划、再检查、后执行；测试选择与 claim 签发分离。 |
| Anti-Pattern Quality | 14 | 15 | 明确禁止 false full-suite claim、静默 unmapped、只看文件名忽略公共依赖。 |
| Specification Compliance | 15 | 15 | frontmatter 同时覆盖 WHAT、WHEN、中文/英文关键词。 |
| Progressive Disclosure | 13 | 15 | SKILL.md 89 行，cadence 细节放 reference；还可进一步明确何时不加载 reference。 |
| Freedom Calibration | 14 | 15 | fragile selection 使用确定性 JSON/script；项目影响域保持配置自由。 |
| Pattern Recognition | 9 | 10 | 符合窄 skill + deterministic tool 模式。 |
| Practical Usability | 13 | 15 | 临时 Git 仓库 eval 覆盖 focused、global、unmapped、clean；首次建立 impact map 仍需项目判断。 |

## Critical Issues

无阻断项。

## Residual Risks

1. `test-impact-map.json` 的正确性仍由项目维护；映射缺失会阻断，但映射错误可能低估依赖扩散。
2. 当前脚本使用显式 glob 影响域，还未对接 Bazel/Nx/Turborepo/Pants 等原生 dependency graph。
3. 脚本证明测试选择和命令执行，不证明具体项目的 acceptance/e2e/real external 已完成；这些仍由 `delivery-verification` 约束。

## Recommended Next Improvements

1. 在真实项目试运行后，再决定是否让 `project-harness-init` 生成 impact map 草稿，避免现在过早猜测项目结构。
2. 为使用 monorepo 原生 affected-test 命令的项目增加 adapter，而不是把依赖图重写进本脚本。
3. 收集“映射命中但仍漏测”的 escaped-defect 案例，达到重复阈值后再增加 global trigger 或规则。
