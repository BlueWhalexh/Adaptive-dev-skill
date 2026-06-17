# Production Handoff Gate

READ when: work delivers an SDK, runtime, package, CLI, MCP server, plugin, Docker image, artifact branch, onboarding path, external-provider integration, credential-packaged artifact, or claims like "import-ready", "drop-in", or "production-ready".

DO NOT READ for ordinary app features, internal-only refactors, or Tiny/Small changes that do not create a consumer-facing delivery surface.

## Contents

- Trigger
- Delivery Contract
- Evidence Matrix
- Fresh Consumer Verification
- Secret And Auth Gate
- Artifact Recovery
- Handoff Exit Gate
- NEVER

## Trigger

Use this gate when the user or repo expects another consumer to use the output without the current agent's local context.

Typical signals:

- Wheel, npm package, Go module, Docker image, binary, plugin, MCP server, or artifact branch.
- Onboarding docs that claim a new user can install, import, run, or deploy.
- External providers, real credentials, runtime auth, config services, or environment-dependent behavior.
- Multi-language consumers, fresh worktree consumers, CI consumers, or clean container consumers.
- A completion claim stronger than "code changed", such as "ready to integrate" or "production-ready".

## Delivery Contract

Write this before implementation or before claiming delivery:

```text
Consumer: who will use this output
Artifact: source, package, image, binary, branch, docs, or service endpoint
Entry point: import, CLI, HTTP, MCP, runtime adapter, or deployment path
Install/run path: exact steps a fresh consumer follows
Allowed dependencies: registry, source checkout, env vars, cache, SSH, config service
Forbidden dependencies: host-only env, local cache, unpublished source path, implicit credentials
Required platforms: languages, OS, container, runtime, or external providers
Deferred scope: what is explicitly not delivered
```

If any field is unknown and affects validation, pause for user judgment.

## Evidence Matrix

Track evidence by capability, not by conversation summary:

| Capability | Artifact / Provider | Auth Source | Dependency | Evidence Type | Status | Gap |
| --- | --- | --- | --- | --- | --- | --- |
| import package | wheel / npm / module | none | clean venv/container | fresh consumer | pass/fail | ... |
| provider call | external API / MCP | runtime secret | network + provider account | real external | pass/fail | ... |
| fallback behavior | cache / mock / fake | none | test fixture | fake/mock/unit | pass/fail | not real chain |

Evidence type must distinguish unit/mock, fake, integration, E2E, clean consumer, real external call, and manual inspection.

## Fresh Consumer Verification

For delivery claims, run at least one verification from outside the producer context when feasible:

- Fresh virtual environment, worktree, container, or language consumer.
- No implicit source path imports unless the delivery contract allows source checkout.
- No host-only env, SSH agent, cache, or unpublished artifact unless explicitly allowed.
- Follow onboarding docs exactly; record deviations as docs gaps.
- Prefer subagents as read-only consumers when isolation helps: artifact reviewer, fresh Python/Go/JS consumer, docs/onboarding reviewer, secret/auth reviewer.

If fresh consumer verification is too expensive or blocked, state what was substituted and what remains unproven.

## Secret And Auth Gate

Escalate before packaging when credentials or auth configuration might enter artifacts.

State:

```text
Secret location: where credentials live
Artifact exposure: whether secret/config appears in package, image, branch, logs, or docs
Runtime override path: how consumers provide credentials safely
Rotation story: how credentials can be replaced without rebuilding unsafe artifacts
Scan result: command/tool/manual inspection used to check exposure
```

Never build tokens into long-lived artifacts unless the user explicitly approves the exposure and rotation model.

## Artifact Recovery

Before production-ready claims, verify the delivery can be reconstructed:

- Build command or packaging command is recorded.
- Artifact version, tag, branch, or checksum is identifiable.
- Consumer install path does not require hidden local state.
- Rollback or previous version path is known when production users are affected.
- Docs point to the artifact that was actually tested.

## Handoff Exit Gate

Before claiming delivery:

```text
Delivery contract: complete or gaps accepted
Evidence matrix: current, with mock/fake/real/fresh-consumer labels
Fresh consumer: passed or gap stated
Real external chain: passed when promised, or explicitly deferred
Secret/auth: exposure and override path reviewed
Artifact recovery: rebuild/install/rollback path recorded
Docs/onboarding: matches the tested path
```

## NEVER

- NEVER call an artifact production-ready because producer-side tests passed.
- NEVER hide fake, cache, mock, or fallback evidence behind real-integration language.
- NEVER let fresh consumers depend on the producer's local env, cache, SSH, or source path unless the contract says so.
- NEVER package credentials without stating exposure, override, rotation, and scan evidence.
- NEVER claim onboarding works unless a clean consumer followed the documented path or the gap is explicit.
