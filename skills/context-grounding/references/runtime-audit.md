# Runtime Audit

Runtime audit records what the implementation session actually read.

Rules:

- Reads inside `allowed_paths` are valid.
- Reads outside `allowed_paths` require updating the context manifest before using that information.
- Reads matching `forbidden_paths` fail unless the user explicitly approved and the manifest was updated.
- The audit is about context discipline; it is not a substitute for code review.
