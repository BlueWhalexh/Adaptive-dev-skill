# Technical Design Review

READ when reviewing or approving a technical design.

## Review Checks

- Spec alignment: design implements every acceptance criterion and does not add unauthorized scope.
- Current truth: changed surfaces and existing constraints are cited from approved Analysis Pack / Context Manifest / repo docs.
- Boundary clarity: ownership, module/service boundaries, public contracts and state transitions are explicit.
- Failure behavior: retry, idempotency, recovery, rollback and observability are concrete enough to test.
- Security/data: auth, permission, privacy, secrets, migration and compatibility risks are addressed when relevant.
- Evidence mapping: each material design mechanism has a planned validator type.
- Plan readiness: a Plan Agent can write tasks from the design without inventing architecture.

## Reviewer Separation

- `self`: only acceptable for embedded low-risk design.
- `independent`: reviewer must not equal the artifact producer.
- `human`: approval must be marked with `reviewer_kind=human`.

Return findings first. Do not silently rewrite the design unless asked.
