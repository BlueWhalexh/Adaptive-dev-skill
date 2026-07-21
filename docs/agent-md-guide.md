# Agent MD 写法指南

`AGENTS.md` 是项目地图和不可违反边界，不是通用开发 SOP，也不是 Skill 调度器。

## 应该写什么

1. 项目是什么，入口和 current truth 在哪里。
2. 架构、权限、数据、安全和生产边界。
3. 可执行的构建、测试、启动和验证命令。
4. 哪些不可逆决策需要人批准。
5. 项目独有、反复验证过的开发约束。

## 不应该写什么

- 所有开发任务默认加载某个 workflow Skill。
- Tiny/Small/Medium/Large 的通用教程。
- 每个 Task 强制 Spec、TDD、Reviewer、Worktree、commit 或全量测试。
- “超过 N 个文件必须暂停”这类与语义风险无关的代理指标。
- 可以由 lint、test、typecheck 或脚本机械执行的规则。

## 与 Adaptive 的关系

Adaptive 只在长期目标、MVP/Basic Usable、AI 行为效果迭代或流程明显跑偏时使用。普通任务依赖模型原生工程判断和项目事实，不经过全局 Router。

可选规则：

```md
- 仅在长期目标、MVP/Basic Usable、AI 行为迭代或流程跑偏时使用 `adaptive-dev-workflow`；普通开发直接执行。
```

如果项目已经有稳定的领域 Skill，直接按领域 Skill 执行，不要先经过 Adaptive 再转发。

## 风险表达

描述真实语义边界：

```md
- 修改 session token 结构、授权判定或权限继承前必须人工确认。
- migration 必须提供 rollback 和数据校验。
- 生产发布只能使用项目 release command，不得手工改线上数据。
```

不要使用文件数、目录数或预计天数代替风险。

## 验证表达

写项目命令，不写“请充分测试”：

```md
- 前端组件改动：`npm run test:web -- <target>`。
- API contract 改动：运行 contract test 和一个真实 HTTP smoke。
- Release：运行 `./scripts/release-verify.sh`。
```

验证强度与当前声明匹配。局部修复不提前承担最终 Release Gate。
