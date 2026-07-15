---
name: change-aware-testing
description: Select and run changed-file-aware tests for software development loops, checkpoints, and completion gates. Use when a task should avoid repeatedly running the full unit suite, needs diff-based test impact selection, test cadence decisions, or must escalate from focused tests to broader verification. 当开发任务需要按 diff 跑增量测试、选择受影响单测、控制测试频率、避免每个 task 全量测试或判断何时升级为模块/全量验证时使用。
---

# Change-aware Testing

目标：开发循环只跑能覆盖当前 diff 的最小可靠测试集，同时避免把“少跑测试”误报成“已完整验证”。

## Cadence

- `inner-loop`: 每个有行为含义的 Task 运行一个 focused signal；纯文档/机械改动使用最小替代 validator。
- `checkpoint`: 连续低风险 Task 组成的 batch、风险边界或 milestone 完成后，运行受影响模块和必要链路一次。
- `completion`: 请求 delivery claim 前，按风险、acceptance 和 claim 扩大验证；不等于机械运行整个仓库的所有单测。

完整规则见 `references/testing-cadence.md`。不要用本 skill 替代 `delivery-verification`；本 skill 选择和运行测试，后者判断证据能签发什么 claim。

## Required Setup

项目在 `.agent/test-impact-map.json` 维护显式映射，契约见：

```sh
skills/change-aware-testing/schemas/test-impact-map.schema.json
```

映射至少说明：

- 哪些 source/test globs 属于同一个影响域。
- 每个 cadence 的命令。
- 哪些共享文件属于 `global_triggers`。
- checkpoint/completion 无法局部映射时使用什么 fallback。

没有可信映射时不要猜测“增量测试已覆盖”。先使用项目原生命令做一次保守验证，再补齐映射。

常见 Python、Go、Jest/Vitest 项目可先生成保守 candidate；默认不会覆盖 canonical map：

```sh
python3 skills/change-aware-testing/scripts/generate_test_impact_map.py --root .
```

Review candidate 后使用 `--promote`。已有人工维护的 map 使用 `--update --promote`：现有规则优先，脚本只补充新的规则和 fallback。无法可靠识别项目结构时脚本必须失败，不生成“看起来可用”的空映射。

先用 `test -f .agent/test-impact-map.json` 检测映射。文件不存在时不要读取它、不要运行选择器，也不要把缺失本身制造成一次失败命令；直接按项目 testing contract / 原生命令降级，并记录 `mapping=missing`。

## Procedure

1. 修改前记录 batch 起点（单改动策略则是 change 起点）：

```sh
git rev-parse HEAD
```

2. 修改后先生成测试计划，不立即执行：

```sh
python3 skills/change-aware-testing/scripts/run_changed_tests.py \
  --root . \
  --base <task-start-sha> \
  --mode inner-loop \
  --output .agent/runtime/changed-tests.json
```

3. 检查 `status`、`changed_files`、`matched_rules`、`selected_tests`、`commands` 和 `requires_broad`。
4. 计划可信时执行同一选择：

```sh
python3 skills/change-aware-testing/scripts/run_changed_tests.py \
  --root . \
  --base <task-start-sha> \
  --mode inner-loop \
  --execute \
  --output .agent/runtime/changed-tests.json
```

5. batch/milestone 完成时改用 `--mode checkpoint`。不要在每个 Plan Task 后重复 checkpoint。请求完成声明前使用 `--mode completion`，并把结果写入 evidence manifest。

## Escalation

- `status=unmapped`: 当前 diff 没有可信映射。停止完成声明，补 map 或运行保守的模块验证。
- `status=checkpoint_required`: diff 命中 shared config、lockfile、公共 fixture、schema、migration、auth/security boundary 等 global trigger。不要在 inner loop 自动启动昂贵命令；进入 checkpoint 后执行 fallback。
- `requires_broad=true`: 必须说明扩大到什么范围以及原因。只有显式 `--allow-broad` 才允许在 inner loop 执行 fallback。
- 测试选择器本身失败、映射过期或命令不存在：按“未验证”处理，不得当作 pass。

## Never

- 不要把“changed tests passed”描述成 full suite passed。
- 不要只看修改文件名就忽略公共依赖、测试配置、生成器和跨模块契约。
- 不要因为 L2/L3 就在每个 implementation task 后跑全量测试；在 checkpoint/completion 扩大即可。
- 不要在每个 Task 后重复 adjacent regression、静态检查、Review 和 commit；这些属于 batch/checkpoint。
- 不要为了省时间跳过 acceptance 对应 validator、regression guard 或 handoff 的 fresh consumer/real external 证据。
- 不要在 map 未命中时静默返回成功。

## Validation

修改本 skill 后运行：

```sh
python3 scripts/run-change-aware-testing-eval.py
python3 /Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/change-aware-testing
```
