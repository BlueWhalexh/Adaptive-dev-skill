# Real-Project Benchmark, Skill Judge, and Lattice Review

日期：2026-07-15

## 结论

本次使用同一个真实可运行仓库、同一提交、同一份已批准 Spec/Technical Design/Plan，分别让 fresh Codex 按 parent workflow contract 和 candidate workflow contract 完成同一项 L2 工程任务。

结果不能证明 candidate 在 L2 场景降本：candidate 使用了更多命令、tokens 和 wall time，但也提供了更强的 CLI fake smoke、第五个测试和兼容性 delta review。两组最终实现均通过各自 focused verifier。

实验同时发现一个共同的 High 缺陷：`spec-driven-feature` resolver 输出 `design_control.policy=embedded`，但 `init_workflow.py` 生成的初始 manifest 没有 validator 要求的 `embedded_in/section_ref`，导致标准 resolver -> init 组合不可运行。现有 deterministic E2E 未覆盖该 producer-consumer 组合。

隔离 Skill Judge 最终评分：`101/120`，Grade B。continuous-batch 的结构设计仍应保留，但在修复 manifest contract 并完成分层 benchmark 前，不应宣称 production-ready 或普遍降本。

## 实验设计

代码基线：`fae88af3ef4e53232d42a2e4488a46d59d87058d`。

- old：目标代码保持 `fae88af`，只把 `adaptive-dev-workflow`、`workflow-control-plane`、`change-aware-testing` 恢复到 parent `ab048a7` contract。
- new：完整使用 `fae88af` candidate contract。
- 两边使用完全相同的批准文档和执行 prompt。
- 任务：为 `scripts/run-fresh-agent-route-eval.py` 增加 `--jobs`、稳定顺序并发、每 case timing、原子 JSON report 和 deterministic tests。
- 两边均由独立 `codex exec --ephemeral --ignore-user-config` fresh session 实际读代码、编辑、测试和 Review。
- 首次 old run 因 Codex 网络/MCP 初始化失败而中止，不计入对照数据；成功 run 使用相同 CLI 配置。

该任务最终被两边都判为 `L2 / spec-driven-feature`。它是单模块、五个共享上下文 Task，不是 L3，因此主要用于验证“candidate 是否会给普通 L2 增加额外成本”，不能替代 L3 continuous-batch benchmark。

## 原始数据

| 指标 | old | new | 判断 |
| --- | ---: | ---: | --- |
| wall time | 约 274s | 约 361s | new +31.8% |
| command executions | 13 | 18 | new +38.5% |
| failed command executions | 1 | 5 | new 的失败包含预期 RED、sandbox pycache 和 manifest contract |
| input tokens | 926,255 | 1,284,904 | new +38.7% |
| cached input tokens | 862,208 | 1,215,232 | 两边多数输入命中 cache |
| uncached input tokens | 64,047 | 69,672 | new +8.8% |
| output tokens | 10,648 | 13,127 | new +23.3% |
| reasoning output tokens | 1,961 | 3,045 | new +55.3% |
| command groups containing tests | 2 | 6 | new 验证更强，但成本更高 |
| subagents | 0 | 0 | 两边都没有过度创建 subagent |
| work orders | 0 | 0 | 两边都保持轻量 |
| review packages | 1 | 0 | candidate 删除了 package ceremony |
| self-review passes | 1 | 2 | new 首轮发现 stdout compatibility，delta 后批准 |
| commits | 0 | 0 | temp worktree git metadata 不可写，均被环境阻塞 |

### old evidence

- 4 个 deterministic tests 通过：串行、并发顺序、失败报告、非法 jobs。
- Python compile 通过。
- 注入式 fake route-eval smoke 通过。
- evidence manifest validator 与 `git diff --check` 通过。
- 生成 1 个 review package、1 个 combined self-review。

### new evidence

- 5 个 deterministic tests 通过。
- 新增真实 subprocess -> fake Codex executable -> resolver -> stdout -> JSON report system smoke。
- Python compile、strategy registry、evidence manifest、`git diff --check` 通过。
- `run-skill-sandbox-eval.py` deterministic surface 通过。
- combined self-review 首轮发现 PASS risk 大小写兼容问题；修复后 delta review 通过。

## 如何解释结果

不能得出“减法无效”。parent 在该 L2 strategy 中本来就没有调度完整 `subagent-driven-development`，因此 candidate 没有可删除的主要 L3 ceremony。candidate 的新增成本主要来自更强测试和 delta review。

可以得出的结论：

1. candidate 没有在这个 L2 case 创建 subagent、work order 或 review package，路由方向正确。
2. candidate 仍会因 RED、sandbox fallback、compatibility delta review 产生更多轮命令；`continuous_batch` 不自动等于更低 token。
3. 效率结论必须按 L0/L1/L2-SOP/L2-novel/L3-feature/L3-migration 分层，且保持 acceptance/evidence strength 相同。
4. 下一次最关键 benchmark 是一个真实 L3、6-10 Tasks、含两个明确 boundary milestone 的同任务重复对照。

## 新发现的 Runtime 缺陷

`spec-driven-feature` 使用 embedded design policy。resolver 输出的是最终设计拓扑政策，但 init/validator 把它当成“当前已经存在 embedded plan binding”：

```text
resolve_strategy.py
  -> policy=embedded, no embedded_in/section_ref
init_workflow.py
  -> copies design_control
validate_workflow_manifest.py
  -> requires embedded_in + existing plan artifact + section_ref
  -> FAIL before plan stage exists
```

建议把 policy 与 binding state 分离：初始阶段允许 `binding_status=pending`，plan/design transition 后再要求 `embedded_in/section_ref`。同时增加所有 `manifest_policy=required` Strategy 的参数化 producer-consumer E2E：

```text
route fixture -> resolver output -> init_workflow -> manifest validator -> artifact graph
```

## Skill Judge

隔离 fresh Codex 完整读取本地 `skill-judge` 和 11-Skill suite 后给出：

| Dimension | Score |
| --- | ---: |
| Knowledge Delta | 18/20 |
| Mindset + Procedures | 14/15 |
| Anti-Pattern Quality | 13/15 |
| Specification Compliance | 15/15 |
| Progressive Disclosure | 13/15 |
| Freedom Calibration | 11/15 |
| Pattern Recognition | 9/10 |
| Practical Usability | 8/15 |
| Total | 101/120, Grade B |

主要扣分全部集中在 runtime composition 和 outcome：静态设计接近 A，但标准 L2 lifecycle 初始化断裂；生产效率也没有被多仓库、多场景对照证明。

## Lattice 独立研究

Lattice 不是建议合入 Adaptive 的依赖。本次研究目标只是理解它解决了什么问题。

### 它做了什么

Lattice 是安装进业务仓库的 repo-local AI Coding control plane。它把框架代码、项目资产和运行状态分离：

```text
lattice/kernel/          可升级的命令和 gates
lattice/context/         项目知识与外部约束
lattice/specs/<id>/      spec/plan/review/verify
lattice/state/           eval runs, outcomes, loops, promotions
prismspec/skills/        分阶段窄 Skills
```

根 Skill 只有 59 行，主要调用 `guide.sh --json`，再路由到 specification/planning/implementation/review/verification 等 PrismSpec Skill。确定性部分由 Bash/yq gates 执行，语义工作交给 Agent。

### 亮点

1. **Repo-local durability**：对话中的 intent、context、review 和 verify 变成可版本化项目资产，下一位 Agent 可以从文件恢复。
2. **Framework/project ownership split**：kernel 可以升级，manifest/context/specs 由项目持有，降低升级覆盖业务知识的风险。
3. **Command-backed evidence**：build/lint/test、AC coverage、drift、compliance 进入结构化 eval JSON，不依赖 Agent 总结宣称完成。
4. **Post-delivery outcome link**：可以把 review finding、rework、escaped defect、incident 和 success 重新关联到 eval run。这是 Adaptive 当前缺少的长期质量观测能力。
5. **Knowledge governance**：失败先生成 learn draft，经 approve/reject 后再 promotion，避免自动污染长期知识。
6. **Vendor-neutral adapter**：不接管 IDE/模型 runtime，可供 Claude Code、Cursor、Aider、Superpowers 或其他 Agent 使用。

### 适用场景

- 团队同时使用多个 AI Coding Agent，需要统一仓库内交付契约。
- 长周期 Feature 或多人/多会话交接，需要从磁盘恢复进度和依据。
- CI 需要结构化 AC coverage、drift 和 evidence history。
- SDK、平台或合规敏感项目，需要追踪“当时为什么允许交付”。
- 团队希望把 escaped defect 和返工反馈沉淀为可治理项目知识。

### 不适用或收益较低的场景

- 个人仓库的 Tiny/Small 修改。
- 已有成熟 CI、Spec、ADR、test mapping 和项目 SOP，只缺轻量 Agent 路由。
- 不愿在仓库维护 `spec.md/plan.md/review.md/verify.md` 四类资产的团队。
- 需要真正 multi-agent scheduling、lease、workspace isolation 的系统；Lattice 主要是文件控制面，不是 Agent runtime。

### 关键边界

- PrismSpec Implementation 默认仍描述 per-Task brief/report/review-package/ledger 和 subagent review，可能在高频迭代中偏重。
- 自带 skill eval 是结构与关键词碰撞检查，不是 fresh-agent semantic/outcome eval。
- Go 示例只运行 `pipeline.sh --only=ac-coverage`，review verdict 由脚本参数直接写入；它证明 gate 可运行，不证明独立 Agent Reviewer 或完整真实 pipeline。
- Lattice 的价值应理解为 repo-local governance/evidence product，而不是“更强的编码模型”或“更好的 multi-agent runtime”。

## 最终决策

- 保留 current continuous-batch 方向，但不宣称已经普遍降本。
- 在修复 resolver -> init embedded design contract 前，不发布 production-ready 结论。
- 不合入 Lattice；将其作为 repo-local governance 和 post-delivery outcome 的参考实现。
- 下一轮先修真实组合缺陷，再做 L3 分层 benchmark，而不是继续增加工作流文字。
