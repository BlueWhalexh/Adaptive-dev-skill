---
name: brainstorming
description: Use only when implementation is blocked by unresolved product intent, UX behavior, architecture, public contract, or consequential trade-offs with multiple reasonable answers. Do not use for acceptance-defined local features, bug fixes, metadata/field additions, mechanical changes, or an already approved design. 当产品目标、交互、架构或公共契约存在真实未决选择时使用；验收明确的局部功能、修复、字段扩展和已有方案实现不触发。
---

# Focused Brainstorming

本 Skill 只解决“必须先做决定才能正确实现”的问题，不是所有开发任务的前置仪式。

## Activation Gate

仅在存在至少一个未解决且会显著改变结果的决策时使用：

- 产品目标、用户体验或非目标有多种合理解释。
- 架构、public contract、数据/权限边界存在真实取舍。
- 选择不同方案会明显改变兼容性、成本、风险或不可逆后果。

以下情况直接实现，不加载本 Skill：

- 用户已给出明确 acceptance、目标路径和边界。
- 局部功能、bugfix、metadata/front matter/字段扩展或机械接线。
- 只剩文件名、helper、测试位置等可恢复实现选择。
- 已有 approved Spec、Design、Plan 或项目 SOP。

不要把“需要读代码确认实现方式”误判为产品设计不明确。先探索代码；模型可自主解决的工程细节不请求人工审批。

## Procedure

1. 用一句话写出唯一未决决策及其影响。
2. 只收集回答该决策所需的项目事实。
3. 给出 2-3 个真正不同的方案、关键取舍和推荐项。
4. 仅对产品、contract、安全、数据或不可逆取舍请求批准。
5. 决策确定后立即退出，由普通实现流程继续。

一个小歧义最多问一个阻塞问题。若合理默认值可从仓库约定、现有模式或 acceptance 推导，直接采用并说明，不等待确认。

## Documentation Boundary

- 当前对话能够稳定表达决定时，不创建文档。
- 只有决定需要跨会话、跨团队或约束 public contract 时，才更新现有 canonical requirement/design。
- 不默认创建 Spec、Plan、task list 或单独 commit。
- 不因为调用本 Skill 自动调用 `writing-plans`。

## Exit

输出已确定的 decision、约束和仍需人工决定的内容。没有真实未决决策时，明确返回 `bypass`，不得增加流程。
