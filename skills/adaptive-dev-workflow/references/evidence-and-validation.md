# Evidence And Skill Validation Reference

Use this only when route/evidence choice is ambiguous, when planning Medium or
Large work, or when changing `adaptive-dev-workflow`.

## Evidence Matrix

| Task Type | Minimal Evidence | Escalate When |
| --- | --- | --- |
| Typo / README / comment | Diff review; markdown/lint only if useful | Command semantics, links, or user workflow changes |
| Config change | Parse, dry-run, or relevant command | Runtime, permission, deploy, or environment risk exists |
| Pure logic | Unit/table-driven test | Complex boundaries or historical bugs exist |
| Bugfix | Reproduction command or failing test | Regression can be automated |
| API/service contract | Request/response/auth/error integration test | Public API, compatibility, or permission changes |
| UI behavior | Component/browser/manual screenshot evidence | Key user flow or fragile layout |
| Data model/migration | Schema/migration/backward compatibility check | Production data, rollback, or compatibility risk |
| Security/permission | Negative test and boundary check | Auth, PII, secrets, payment, or privilege boundary |
| Cross-service workflow | Phase smoke/E2E | User-visible or system-critical chain changes |

## Skill Validation Protocol

Validate the skill itself with behavior evals, not intuition.

1. Static validation: frontmatter, `openai.yaml`, duplicate versions, and key sections.
2. Route dry run: Tiny/Small/Medium/Large/debug prompts route as expected.
3. Blind subagent eval: a fresh subagent routes cases using only `SKILL.md`.
4. Developer/auditor simulation: one session executes, another audits output,
   evidence, route choice, docs, and completion claims.

## Eval Case Schema

```yaml
- id: tiny-readme-command
  prompt: "README 里把 npm 改成 pnpm"
  expected_route: Tiny
  expected_gates:
    - focused verification
  expected_delegate_skill: []
  expected_docs: []
  expected_evidence:
    - diff review
    - command/link check only if command semantics matter
  expected_no:
    - no TDD
    - no design doc
    - no subagent review
  actual_route:
  actual_gates:
  actual_delegate_skill:
  actual_docs:
  actual_evidence:
  pass:
  observed_failure:
  skill_change_needed:
```

## Seed Cases

| ID | Prompt | Expected Route | Key Judgment |
| --- | --- | --- | --- |
| `tiny-readme-command` | "README 里把 npm 改成 pnpm" | Tiny | No Red; check diff and command semantics only |
| `tiny-css-spacing` | "把按钮间距调大 4px" | Tiny/Small | Visual evidence; no unit test by default |
| `small-login-bug` | "修登录按钮点击没反应" | Small | Reproduce or focused validator; regression if automatable |
| `small-config-risk` | "改一下超时配置默认值" | Small | Blast radius may require smoke/integration |
| `medium-order-filter` | "订单页加状态筛选" | Medium | UX/API boundary, test plan, phase smoke |
| `medium-api-contract` | "给导出接口加 format 参数" | Medium | Contract/error/compatibility tests |
| `large-permission-model` | "把用户权限模型从 role 改成 policy" | Large | Spec, migration, security review, E2E |
| `debug-ci` | "CI 挂了修一下" | Debug | Use systematic debugging; read logs and reproduce first |
| `docs-architecture-drift` | "把 runtime 架构文档同步到当前实现" | Small/Medium docs | Read code and canonical docs; avoid narrative-only edits |
| `openai-api-upgrade` | "升级 OpenAI API 调用到最新模型" | Medium + openai-docs | Official docs, narrow change, API-shape verification |

## Failure Classes

| Failure | Example | Severity |
| --- | --- | --- |
| Over-process | README edit requires Red-Green, design doc, and E2E | P2 |
| Under-process | Permission model rewrite ships with unit tests only | P0 |
| Gate dilution | TDD route uses a local softer summary instead of the selected TDD skill | P0 |
| Evidence mismatch | Visual UI change reports only test pass counts | P1 |
| Docs drift | Public API changes without current-truth docs/spec update | P1 |
| Missing harness | Large/new-project work starts without current-truth docs or an explicit accepted gap | P1 |
| Completion overclaim | "Done" without fresh evidence or stated gaps | P0 |
| Skill ambiguity | Evaluators disagree on the same route repeatedly | P1 |

## Change Rule

- Same failure twice: add the smallest trigger or escalation rule.
- Same failure three times: adjust the flow or evidence ladder.
- Mechanical failure: prefer hook, CI, script, or lint rule.
- Project-specific lesson: put it in repo `AGENTS.md` or docs, not this skill.
