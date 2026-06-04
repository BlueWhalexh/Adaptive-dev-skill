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
find . -name '*.md' -o -name '*.yaml'
git diff --check
```

同时扫描文档，确认没有 placeholders、夸大表述，或假设不可用工具的安装说明。
