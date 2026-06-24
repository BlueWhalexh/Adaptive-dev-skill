---
name: context-grounding
description: Use when a development task needs Analysis Pack, Context Manifest, context slicing, runtime audit, freshness checks, or sufficiency eval before implementation. 当任务需要深度阅读、上下文裁剪、Analysis Pack、Context Pack、allowed paths、freshness、runtime audit 或验证上下文是否足够时使用。
---

# Context Grounding

目标：让 Coding Agent 只吃足够且可追踪的上下文，而不是重新从长仓库里自由探索。

## Outputs

- `Analysis Pack`: 人读分析，说明 Problem、Entry Points、Current Flow、Similar Patterns、Context Slice、Risks、Task Plan、Evidence Plan。
- `context_manifest.json`: 机器校验契约，记录 repo commit、spec version、allowed/forbidden paths、文件 hash、runtime audit。

## Required References

- `references/analysis-pack.md`: 写 Analysis Pack。
- `references/context-manifest-contract.md`: 写 `context_manifest.json`。
- `references/runtime-audit.md`: 检查实际读取范围。
- `references/sufficiency-eval.md`: fresh Plan Agent sufficiency eval。

## Validation

```sh
python3 skills/context-grounding/scripts/validate_context_pack_static.py context_manifest.json
python3 skills/context-grounding/scripts/validate_context_freshness.py context_manifest.json --repo-root .
python3 skills/context-grounding/scripts/validate_context_runtime_audit.py context_manifest.json
python3 skills/context-grounding/scripts/run_context_sufficiency_eval.py context_manifest.json --spec spec.md
```

## Exit Gate

只有当 static、freshness、runtime audit、sufficiency 四类检查都有结论时，Context Pack 才能标记为 `ready`。若任一检查不可运行，必须把 gap 写入 workflow manifest 或 evidence manifest。
