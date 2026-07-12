# Strategy Registry

READ when selecting strategy stages or auditing whether the downstream skills are correct.

Machine-readable strategy manifests live in `references/strategies/*.json` and are validated by:

```sh
python3 skills/workflow-control-plane/scripts/validate_strategy_registry.py
```

## Strategies

| Strategy | Use When | Depth | Design | Typical skills |
| --- | --- | --- | --- | --- |
| `quick-change` | L0 docs/mechanical change | direct | none/none | none |
| `sop-guided-change` | L1 known pattern with ready project SOP | direct | none/self | project SOP validator |
| `focused-change` | Other L1 local implementation or narrow bugfix | selective | embedded/self | focused evidence, no default Superpowers |
| `sop-guided-iteration` | Non-critical L2 known/adjacent pattern with ready project SOP | selective | embedded/independent | project SOP and delivery-verification |
| `root-cause-debug` | debug mode or unknown failure | selective | embedded/self | systematic-debugging |
| `spec-driven-feature` | Novel L2 behavior/UI feature | lifecycle/local | embedded/self | specflow, technical-design, writing-plans, delivery verification |
| `complex-real-slice` | L3 complex feature/MVP/handoff chain | lifecycle | standalone/independent | context, spec, design, execution, verification, review |
| `migration-critical` | data/auth/security/migration/public protocol | lifecycle | standalone/human | context, spec/design, staged execution, rollback review |
| `spike` | high uncertainty exploration | selective | none/independent decision record | context-grounding, no delivery claim |
| `review-only` | code/spec/design/plan/evidence review | direct | none/independent | no implementation |

## Stage Ownership

The selected strategy owns stages. The adaptive router only records `selected_strategy` and `current_stage`.

Each strategy also owns `stage_skills`. The resolver emits a complete `skill_plan`, while `required_skills` contains only the current stage entry. `transition_workflow.py` replaces `required_skills` when the stage advances; names scheduled for future stages are not instructions to preload those skills.

## Claim Rule

Strategies may request claims, but only `delivery-verification` or another named verifier signs validated claims.
