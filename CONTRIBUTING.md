# Contributing

感谢你帮助改进 Adaptive Dev Workflow。

这个项目刻意保持小而清晰。贡献应该让 workflow 更清楚、更容易安装，或者在真实仓库中更有用；不要把它扩成一个巨大 checklist。

## 适合的贡献

- 特定 agent 工具的安装说明。
- 更清晰的 workflow-level 决策规则。
- 克制、真实的 before/after 示例。
- scope 清楚且没有夸大结论的 case study。
- Codex、Claude Code、Gemini CLI 等工具的兼容说明。
- 能减少歧义的 skill 文案改进。

## 请避免

- 没有证据的 productivity claims。
- 虚假的 benchmarks、用户或 star 数。
- 不改变 workflow 行为的宽泛宣言。
- 给 Tiny 和 Small 任务增加仪式感。
- 让其他 agent CLI 无法使用的强工具绑定说明。

## Review 标准

PR 应重点检查：

- 正确性：workflow instruction 是否准确表达了它要表达的意思？
- 边界：它是否保持 adaptive，而不是变成僵硬流程？
- 安全性：它是否阻止 agent 默默做高风险决策？
- 可用性：开发者是否能直接复制说明并开始使用？

## Development

当前项目没有 build step。提交 PR 前请运行：

```sh
python3 scripts/run-skill-sandbox-eval.py
python3 scripts/run-workflow-e2e-eval.py
python3 scripts/run-handoff-fresh-consumer-eval.py
python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/adaptive-dev-workflow
python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/project-harness-init
git diff --check
```

如果修改了路由语义，再运行 fresh agent 语义路由 eval：

```sh
python3 scripts/run-fresh-agent-route-eval.py --case tiny-readme-command --case package-handoff --case project-harness-init-goal-loop
```

这个命令会启动 fresh `codex exec` sessions，可能消耗模型调用或需要本机审批，所以不放进默认 deterministic 检查。

如果本机没有 Codex skill-creator helper，至少运行 sandbox eval、workflow E2E eval、fresh consumer handoff eval 和 `git diff --check`。同时扫描文档，确认没有 placeholders、夸大表述，或假设不可用工具的安装说明。
