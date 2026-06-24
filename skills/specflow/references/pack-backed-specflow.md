# Pack-Backed SpecFlow

Use when L2/L3 work has unclear current truth, complex UI/workflow, data/security risk, or multiple implementation paths.

Inputs:

- Approved Analysis Pack.
- Ready Context Manifest.
- User intent and constraints.

Output:

- `spec` artifact that references the context manifest id.
- Acceptance criteria mapped to evidence plan ids.
- Explicit non-goals and deferred work.

Do not read arbitrary repo context after the pack is approved unless the Context Manifest is updated.
