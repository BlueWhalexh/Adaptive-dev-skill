# Contributing

Thanks for helping improve Adaptive Dev Workflow.

This project is intentionally small. Contributions should make the workflow clearer, easier to install, or more useful in real repositories without turning it into a giant checklist.

## Good Contributions

- installation notes for specific agent tools
- sharper workflow-level decision rules
- realistic before/after examples
- case studies with clear scope and no inflated claims
- compatibility notes for Codex, Claude Code, Gemini CLI, and similar tools
- improvements to the skill text that reduce ambiguity

## Please Avoid

- productivity claims without evidence
- fake benchmarks, fake users, or fake star counts
- broad manifestos that do not change how the workflow operates
- adding ceremony to Tiny and Small tasks
- tool-specific instructions that break use in other agent CLIs

## Review Criteria

Pull requests should be reviewed for:

- correctness: does the workflow instruction mean what it says?
- boundaries: does it keep the system adaptive rather than rigid?
- safety: does it prevent agents from making hidden high-risk decisions?
- usability: can a developer copy the instruction and use it immediately?

## Development

There is no build step for the current project. Before opening a pull request, run:

```sh
find . -name '*.md' -o -name '*.yaml'
git diff --check
```

Also scan the docs for placeholders, exaggerated claims, and install instructions that assume unavailable tooling.
