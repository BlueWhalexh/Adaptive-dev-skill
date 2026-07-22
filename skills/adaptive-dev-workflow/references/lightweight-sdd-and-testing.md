# Lightweight SDD and Testing

仅在当前动作需要决定文档深度或验证层级时读取。目标是降低歧义和 false green，不是增加固定阶段。

## Lightweight SDD Decision

| 当前情况 | 最小产物 | 不要做 |
| --- | --- | --- |
| 目标、边界、验收在当前对话已清楚 | 直接实现；必要时留一句 acceptance | 为形式补 Spec/Design/Plan |
| 普通行为改动，但验收容易漂移 | 一个短 requirement note | 拆多份重复文档 |
| 多模块、多阶段或跨会话，目标/非目标需要固定 | 一个 canonical ready Spec | 同时维护另一套“更完整”的 Spec |
| 存在真实架构、public contract、数据迁移或关键取舍 | 在 Spec 之外增加 Technical Design | 因文件多或工期长自动拆 Design |

仓库原生 OpenSpec、ADR、RFC 或需求系统优先。已有有效事实源时直接消费，不迁移、不复制。
不要默认生成 Spec、Design、Plan 三件套；每个 artifact 都必须消除当前真实歧义，否则不创建。
短 requirement note 至少固定本轮 goal、non-goals 和 acceptance；实现后的证据必须回到该 acceptance，而不只报告测试为绿。
只要当前 slice 新建或批准 requirement note、canonical Spec 或 Technical Design，evidence plan 必须显式包含 `acceptance`；static/unit evidence 不能替代它。设计阶段的 acceptance 只证明目标、边界和技术取舍已获准，不得抬高产品 capability claim。

需要新建 canonical Spec 时，至少包含：

```yaml
status: draft | ready | done
goal: 用户可见结果
non_goals: 本次明确不做什么
acceptance: 可观察、可验证的完成条件
constraints: 不可违反的产品或工程边界
evidence: 每项 acceptance 由什么证明
```

- `draft`：仍在讨论，不允许据此宣称范围已确认。
- `ready`：足以实施；人只需在存在真实产品或架构取舍时批准。
- `done`：acceptance 已有对应证据；不是“代码写完”的别名。
- 优先用 frontmatter 表示状态，避免仅为改名移动文件；仓库已有命名状态机时遵循仓库规范。

## Evidence Layers

| Evidence | 主要证明 | 不能单独证明 | 建议频率 |
| --- | --- | --- | --- |
| Static / build / type / lint | 结构、类型和静态约束 | 业务行为正确 | changed scope 需要时 |
| Unit | 核心逻辑、边界条件、失败定位 | 模块接线和真实用户链路 | 每个相关 slice |
| Integration | 模块、存储、协议或依赖协作 | 端到端用户结果 | 改动跨边界时 |
| E2E | 关键用户流程可走通 | 所有分支正确、根因定位 | 里程碑和关键流程 |
| Fresh consumer | 干净消费者能按交付说明完成接入 | 外部服务真实可用 | handoff claim 需要时 |
| Real external | 真实外部系统、凭证和协议链路可用 | 新消费者能独立完成接入 | external claim 需要时 |
| Acceptance | 结果符合用户目标与明确标准 | 内部覆盖充分 | Basic Usable、里程碑、交付 |

E2E 与 unit 是互补关系：E2E 证明链路，unit 约束逻辑并快速定位。Fresh consumer 与 real external 也不是等价证据，按交付声明二选一或组合。不要用全量 E2E 代替局部回归，也不要把 mock/fake 描述成真实链路。

## Failure-Sensitive Testing

不要求每个任务机械执行 Test First 或 RED。先问：这次能否以合理成本证明 validator 对目标失败敏感？

优先在修改前保留 failing evidence：

- 可自动化复现的 bug。
- 核心业务规则和有意义的边界条件。
- 权限、认证、状态机、数据转换和幂等行为。
- 容易复发且已有稳定测试入口的行为。

有效 failing evidence 必须因目标旧行为失败。测试原本就绿、只验证 mock、断言与 acceptance 无关，或失败来自环境噪声，都不算有效 RED。

以下情况先定义 alternate validator 即可：

- 文档、文案、机械重命名和局部样式。
- 视觉结果更适合 screenshot 或人工 acceptance。
- 测试环境不可用，或自动化成本明显高于当前风险。
- 已有 focused regression 能直接覆盖相同 contract。

## Test Quality Guard

测试至少回答 state、trigger、expected behavior。按风险补 negative/edge case，并警惕：

- 只有 happy path。
- 只断言“不报错”或状态码，不断言业务结果。
- mock 掉真正需要验证的边界。
- 为追求 coverage 添加不影响失败率的测试。
- 修改测试来迁就错误实现，却未修改 acceptance。

Coverage 用于发现空白和观察趋势，默认不是统一阻断阈值。优先检查 changed behavior 是否有有效证据；安全关键仓库或项目既有 gate 除外。

## Cadence

```text
每次局部改动：focused validator
每个行为 slice：相关 unit，跨边界时加 integration
Basic Usable / 里程碑：代表场景 + 最小真实链路 + acceptance
Release / Handoff：项目完整 gate + E2E/real external/fresh consumer + rollback
```

只运行能改变当前决策的最小证据集。失败时先定位证据层和共性原因，不通过机械扩大测试范围制造进展感。

## Source

- 实践启发：[从 Vibe Coding 到 AI 原生研发团队：一套能落地的工程实践](https://mp.weixin.qq.com/s/DrIpzHm777Zd8klcyAICBA)。本参考只吸收 testing evidence 与 lightweight SDD 的决策原则，未采用逐任务三阶段确认等重流程。
