# Sufficiency Eval

Sufficiency eval asks whether a fresh Plan Agent can produce a useful plan using only the Spec and Context Pack.

Minimum deterministic check:

- Context manifest has at least one concrete allowed path.
- Context manifest has file hashes for each context file.
- Spec input exists.
- No broad wildcard such as `src/**` is used as the normal slice.

Fresh semantic eval can be added by running an isolated agent with repository access disabled.
