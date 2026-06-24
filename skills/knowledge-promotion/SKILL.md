---
name: knowledge-promotion
description: Use when repeated project knowledge, user corrections, quality dissatisfaction, SOP patterns, project skill updates, AGENTS.md updates, templates, or eval cases should be captured and promoted. 当需要沉淀项目经验、踩坑、用户反馈、项目 skill、AGENTS.md、模板、测试夹具或自动迭代 skill 时使用。
---

# Knowledge Promotion

目标：把开发中的重复解释和质量反馈转成可 review、可验证、可提升的 learning candidate，而不是直接把临时经验写进全局 skill。

## Trigger

- 用户连续两次指出同类质量问题。
- 项目内出现可复用 SOP、模板、测试夹具或 reviewer 角色。
- MVP vertical slice 成功后，需要沉淀项目领域 skill。
- Evidence/Context/Spec 中出现重复 gap。

## Candidate Flow

1. Capture `learning_candidate.json`。
2. Validate schema。
3. 人或 isolated reviewer 判断 promotion target。
4. 只把稳定、项目相关的内容写入项目 `AGENTS.md` 或项目 skill。
5. 为通用 skill 只保留可泛化规则。

## Validation

```sh
python3 skills/knowledge-promotion/scripts/validate_learning_candidate.py learning_candidate.json
```
