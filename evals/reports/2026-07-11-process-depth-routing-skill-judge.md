# Process Depth Routing Skill Judge Report

## Summary

- **Total Score**: 113/120 (94.2%)
- **Grade**: A
- **Pattern**: Navigation router + deterministic control-plane tool
- **Knowledge Ratio**: E:A:R = 78:18:4
- **Verdict**: 已形成可执行的 `direct / selective / lifecycle` 分层；Superpowers 从安装即默认接管改为 Registry 明确选择，项目 SOP 只有具备完整证据时才能降低流程深度。

## Dimension Scores

| Dimension | Score | Max | Notes |
| --- | ---: | ---: | --- |
| D1: Knowledge Delta | 18 | 20 | 项目 SOP readiness、pattern familiarity、process depth 和 manifest policy 是非通用的控制面知识。 |
| D2: Mindset + Procedures | 14 | 15 | 风险、成熟度、模式熟悉度和证据强度被分离；脚本负责脆弱的解析与校验。 |
| D3: Anti-Pattern Quality | 14 | 15 | 禁止安装即全流程、partial SOP 降级、direct manifest 和 high-uncertainty fast route，并有负向 eval。 |
| D4: Specification Compliance | 15 | 15 | Frontmatter 有效，WHAT/WHEN/中英文触发词完整，breaking schemas 已提升版本。 |
| D5: Progressive Disclosure | 14 | 15 | Router 149 行、control plane 95 行、adapter 46 行；详细策略、schema、mapping 位于 references/scripts。 |
| D6: Freedom Calibration | 15 | 15 | L0/known L1 高自由低流程；resolver/schema/claim 等脆弱边界由确定性脚本约束。 |
| D7: Pattern Recognition | 9 | 10 | 符合 Navigation + Tool pattern；控制面套件本身仍比单一官方 Skill 更复杂。 |
| D8: Practical Usability | 14 | 15 | 有真实 resolver、manifest 拒绝、capability detection、negative eval 和 fresh-agent route eval。 |

## Verified Behavior

Deterministic E2E 已证明：

- Ready SOP + known L1 -> `sop-guided-change / direct / local / no manifest`。
- Ready SOP + known L2 -> `sop-guided-iteration / selective / local`，只列出当前任务需要的 native skills。
- Partial SOP + 同一 L2 -> `spec-driven-feature / lifecycle / local`。
- High uncertainty + ready SOP -> 不允许 SOP fast route。
- Debug -> `root-cause-debug / selective / local`，只选择 `superpowers:systematic-debugging` 等窄 skill。
- L3 migration -> `migration-critical / lifecycle / superpowers`。
- Direct route 初始化 `workflow_manifest.json` 会失败。
- Resolver 把未来方法写入 `skill_plan`，`required_skills` 只暴露 current stage；transition 后才激活下一 stage 的 skill。

Fresh-agent semantic eval 独立运行结果：

- `tiny-readme-command`: `L0 / quick-change / direct`，通过。
- `sop-guided-small-fix`: `L1 / sop-guided-change / direct`，通过。
- `sop-guided-existing-project`: `L2 / sop-guided-iteration / selective`，通过。
- `large-permission-model`: `L3 / migration-critical / lifecycle`，通过。

初始 SOP case 因包含 API mapper 被 fresh agent 判为 `api_contract` 并升级 full lifecycle；修正 case 为纯前端状态链路后通过。该过程证明 public contract hard trigger 没有被 SOP maturity 覆盖。

初始 L1 SOP case 曾把项目成熟度误写成 `required_spec_system=repo_native`；Router contract 已收紧为 required constraints 只能来自用户显式要求，修复后 fresh-agent 通过。

## Remaining Risks

1. 当前只证明了路由与边界正确，没有完成 old/new token、wall time、tool calls 的量化，因此“更省 token/时间”仍是高可信推断，不是已测结论。
2. `project_sop=ready` 依赖标准路径：`AGENTS.md`、`.agent/.agents skills`、testing contract。非标准项目需要扩展 detector 或显式 capability artifact。
3. 当前用户环境仍同时暴露 `.agents/skills`、legacy `~/.codex/superpowers/skills` 和 cached namespaced skills。仓库路由已避免默认调用，但 broad frontmatter 仍可能绕过 Router；需要单独做 discovery 去重或 implicit policy 配置。

## Decision

保留本次改造。它降低了 routine work 被完整 Superpowers 流程接管的概率，同时没有降低 API/auth/security/data/migration/handoff 和 high-uncertainty 任务的 gate。下一阶段应做相同任务集的 old/new token/time 对照，而不是继续增加流程文字。
