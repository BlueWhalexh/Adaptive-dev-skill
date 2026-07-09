# Context Projection

Context projection decides what a role gets from shared workflow state. It should be repeatable and minimal.

## Include

- Artifact refs needed to perform the role's objective.
- The current strategy stage and relevant acceptance criteria.
- Allowed paths and explicit forbidden paths.
- Constraints that affect the role's output.
- Evidence gaps the role must address.

## Omit

- Full conversation history.
- Other agents' private reasoning.
- Unrelated repo files.
- Downstream implementation details when the role is spec/design review.
- Secrets, tokens, local-only paths, private logs.

## Projection Rules

1. Start from `workflow_manifest.json` and artifact graph.
2. Pick only artifacts named in the work order dependencies or needed by role contract.
3. Add `omissions[]` explaining important context intentionally withheld.
4. Use `allowed_paths[]` as a reviewable boundary, not as a claim that the role cannot discover new facts.
5. If a role discovers new risk, return `discovered_facts`; do not silently expand scope.

## Anti-Patterns

- "Here is the whole chat, continue from there."
- Giving implementer review findings before it has produced a patch, causing it to optimize for review wording rather than requirements.
- Giving reviewer implementer's self-justification without the diff, spec, and evidence.
- Letting context packets age without a manifest revision.
