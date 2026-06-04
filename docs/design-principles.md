# Design Principles

## 1. Process 是 risk control

Workflow level 应该由需求模糊度、blast radius、行为风险和验证成本决定。流程只有在降低真实风险时才有价值。

## 2. Scope 必须显式

开始编码前，agent 应该知道期望 outcome、哪些文件或行为在 scope 内、哪些不在 scope 内，以及什么情况需要暂停。

## 3. Completion claim 前必须验证

最终回复应该说明运行了什么命令或检查，以及结果是什么。没有 fresh evidence 的自信陈述不是工程结果。

## 4. Human gate 应放在决策点

agent 不应该每改一行都询问许可。它应该在决策会改变目标、public API、data model、security posture、user-facing behavior、dependency graph 或 scope 时暂停。

## 5. 组合专业 workflow

Adaptive Dev Workflow 负责协调，而不是复制其他 workflow。Planning、TDD、debugging、OpenSpec 和 review workflow 只在任务需要时使用。

## 6. 跟随仓库

先读项目结构。使用现有 patterns、helpers、tests 和 conventions。避免无关重构。
