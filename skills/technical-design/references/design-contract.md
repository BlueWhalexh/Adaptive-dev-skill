# Technical Design Contract

READ before generating standalone technical design.

Human-facing prose follows the project language. In this repo, write Chinese-first prose unless local instructions say otherwise; keep paths, schema keys, commands, code identifiers, validator types and error text in English.

## Required Sections

1. Inputs and source-of-truth references.
2. Design goals and constraints.
3. Current-to-target architecture delta.
4. Options considered and decision rationale.
5. Architecture and responsibility boundaries.
6. API, event, schema, storage and state contracts.
7. Control flow and data flow.
8. Error, retry, recovery, concurrency and idempotency.
9. Security, privacy and permissions.
10. Performance, operability and observability.
11. Compatibility, migration, feature flag and rollback.
12. Acceptance-to-design-to-evidence mapping.
13. Open decisions and stop conditions.

## Approval Rules

- A design with blocking open decisions is not approved.
- A design that changes auth/security/data/migration/public contract needs independent or human review.
- A design does not request delivery claims. It only unlocks implementation planning.
