# Maker / Checker Boundary

仅在 `SKILL.md` 的独立 Review Gate 命中时读取。

## Required

以下任一情况需要未参与产出的 checker：

- public API、权限/认证、安全、数据模型/迁移。
- 状态机、并发/幂等、不可逆外部副作用。
- 长期或跨模块目标的技术设计批准、里程碑或最终交付声明。
- 用户或项目明确要求独立 Review。

实现 Agent 的 self-review 是前置检查，不能替代这些场景的 checker。

## Not Required

- 文档事实修订、样式和机械修改。
- 局部可逆 bugfix，且 focused regression 已覆盖目标行为。
- 已批准方案中的普通小切片，没有触及上述高风险边界。

## Reviewer Packet

只提供：

- 当前 acceptance 和 non-goals。
- 相关 canonical facts 或已批准 Spec/Design。
- 本次 diff 或待审 artifact。
- focused validation evidence 和已知 gap。

不要提供完整实现对话、实现者的自我辩护或无关仓库上下文。Reviewer 默认只读，不创建 worktree。

## Verdict

Reviewer 输出：

```text
verdict: approved | changes_requested | human_required
findings: severity + evidence + affected acceptance
residual_risk:
```

- Blocking/High：修复后只审 delta，默认最多一次。
- Minor/建议：进入 Deferred，不改变当前 Top blocker。
- 新发现的独立安全/数据边界：可以增加 Reviewer 或升级人工判断。

同一实现者不得签发 required checker 的 `approved`。
