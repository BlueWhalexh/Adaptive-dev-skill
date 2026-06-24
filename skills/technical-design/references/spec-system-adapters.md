# Spec System Adapters

READ when choosing where the technical design lives.

`technical_design` is a semantic artifact type, not a required filename.

| Spec system | Canonical technical design surface |
| --- | --- |
| OpenSpec | `openspec/changes/<change>/design.md` |
| repo_native | Existing repo ADR/design/proposal path |
| fallback / Superpowers | `docs/superpowers/designs/YYYY-MM-DD-<feature>-technical-design.md` |
| Spec Kit-like | Technical plan + research/data-model/contracts may jointly satisfy the semantic role |

Rules:

- Reuse the canonical surface if one exists.
- Do not create a fallback design beside OpenSpec `design.md`.
- Control plane references the canonical path through `technical_design.path` and `design_control.artifact_id`.
