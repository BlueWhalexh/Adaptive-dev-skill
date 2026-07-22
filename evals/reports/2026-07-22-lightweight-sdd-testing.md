# Lightweight SDD and Testing Eval

日期：2026-07-22

## Change

- 全局与项目示例 `AGENTS.md` 增加轻量 SDD、测试证据分层和非机械 RED 边界。
- Adaptive 主 Skill 只增加 conditional reference，保持 narrow Outcome Guard。
- 新增 7 个 fresh-agent behavior cases，校验文档深度、Design gate、failure evidence、validator scope、evidence layers、文档预算和 claim ceiling。

## Behavior Results

最终 fresh behavior eval：`7/7 PASS`。

覆盖：

- README 机械修改：零 Spec、focused static/acceptance、alternate validator。
- 可自动化局部 bug：零 Spec、优先 failing evidence、focused unit。
- 已有 approved OpenSpec：直接复用、零新文档、unit + integration。
- 验收漂移：仅一份 requirement note，并回到 acceptance 收尾。
- public contract / migration design：canonical Spec + Technical Design，不能宣称实现完成。
- 纯视觉间距：零 Spec、visual alternate validator，不机械 RED。
- mock/fake 通过：claim ceiling 仍为 proxy only，需 real external + acceptance 才能声明 Basic Usable。

原 Outcome Guard 隔离回归也通过：Tiny、已复现 bug 和明确 hardening 均 bypass；目标模式选择 `improve`，不新建 Spec/Design 或 Agent Team。

## Skill Judge

| Review | Score | Verdict |
| --- | ---: | --- |
| 初审 | 109/120, A | 唯一 High：新增规则只有 marker test |
| 行为 eval 后复核 | 116/120, A | APPROVE, release-ready |

最终无 Blocking、High 或 Medium。两个 Low 留作后续：case schema 可增加 duplicate/enum 自检；fresh prompt 可进一步减少 answer cue。

## Verification

```text
run-outcome-first-eval.py: PASS, 148 lines, 16 cases, positive/negative 8/8
run-fresh-lightweight-dev-eval.py: 7/7 PASS
selected route eval: 4/4 PASS after semantic alias correction
quick_validate.py: Skill is valid
git diff --check: PASS
```
