# Documentation Topology

Use this to decide how many document layers a change needs. The goal is to prevent small work from becoming ceremony and large work from hiding architecture inside a swollen spec.

## Decision

| Topology | Use when | Shape |
| --- | --- | --- |
| `compact` | `<5` files, one module, `<3` days, low architectural novelty | design notes inside spec or plan |
| `single_file_design` | standalone technical design is required, but one document can hold the boundaries and contracts | one canonical technical design artifact |
| `split_design_workspace` | multi-module, multi-phase, `>1` week, first MVP vertical slice, migration, platform handoff, or several design parts with different owners | separate product spec, acceptance, design overview/parts, plan, ADR |

## Paths

Prefer the repo's native system.

OpenSpec:

```text
openspec/changes/<change-id>/proposal.md
openspec/changes/<change-id>/design.md
openspec/changes/<change-id>/tasks.md
```

Superpowers fallback:

```text
docs/superpowers/specs/YYYY-MM-DD-<feature>-spec.md
docs/superpowers/designs/YYYY-MM-DD-<feature>-technical-design.md
docs/superpowers/plans/YYYY-MM-DD-<feature>.md
```

Repo-native large slice:

```text
docs/specs/<feature>/prd.md
docs/specs/<feature>/spec.md
docs/specs/<feature>/acceptance.md
docs/design/<feature>/overview.md
docs/design/<feature>/01-<part>.md
docs/plans/<feature>.md
docs/adr/
```

## Anti-Patterns

- NEVER create `split_design_workspace` for typo, README, CSS spacing, or one-file local fixes; it adds process without reducing risk.
- NEVER keep adding sections to a single spec after ownership, APIs, state/data flow, rollout, and rollback become separate review concerns; split the workspace instead.
- NEVER generate repo-native `docs/specs/...` when OpenSpec already owns the product spec. Reuse OpenSpec and put detailed engineering plans in the repo's accepted planning surface.
