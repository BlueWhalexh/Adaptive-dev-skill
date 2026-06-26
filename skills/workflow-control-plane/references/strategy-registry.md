# Strategy Registry

READ when selecting strategy stages or auditing whether the downstream skills are correct.

Machine-readable strategy manifests live in `references/strategies/*.json` and are validated by:

```sh
python3 skills/workflow-control-plane/scripts/validate_strategy_registry.py
```

## Strategies

| Strategy | Use When | Design | Typical skills |
| --- | --- | --- |
| `quick-change` | L0 docs/mechanical change | none/none | none |
| `focused-change` | L1 local implementation or narrow bugfix | embedded/self | TDD when automatable, verification-before-completion |
| `root-cause-debug` | debug mode or unknown failure | embedded/self | systematic-debugging |
| `spec-driven-feature` | L2 behavior/API/UI feature | embedded/self | context-grounding if needed, specflow, technical-design, writing-plans, TDD |
| `complex-real-slice` | L3 complex feature/MVP/handoff chain | standalone/independent | context-grounding, specflow, technical-design, project-harness-init, delivery-verification, review |
| `migration-critical` | data/auth/security/migration/public protocol | standalone/human | context-grounding, specflow/OpenSpec, technical-design, delivery-verification, security/data review |
| `spike` | high uncertainty exploration | none/independent decision record | context-grounding, decision evidence, no delivery claim |
| `review-only` | code/spec/design/plan/evidence review | none/independent | no implementation, verifier focus |

## Stage Ownership

The selected strategy owns stages. The adaptive router only records `selected_strategy` and `current_stage`.

## Claim Rule

Strategies may request claims, but only `delivery-verification` or another named verifier signs validated claims.
