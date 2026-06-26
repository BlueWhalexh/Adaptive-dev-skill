---
name: delivery-verification
description: Use when validating evidence manifests, deciding dev_done/integration_done/handoff_done claims, preventing completion overclaim, or requiring fresh consumer / real external verification. 当任务需要证据矩阵、交付验收、claim 签发、fresh consumer、real external、E2E/integration/system 证据或防止假完成时使用。
---

# Delivery Verification

目标：只让 verifier 根据证据签发 claim。实现者可以请求 claim，但不能自己签发 validated claim。

## Evidence Manifest

Canonical input 是 JSON：

```json
{
  "evidence_manifest_id": "ev-001",
  "claim_requested": "integration_done",
  "acceptance_coverage": [],
  "validators": [],
  "deferred": [],
  "review_focus": []
}
```

## Claim Rules

- `dev_done`: 至少一个 passing focused validator，可为 unit、manual、diff_review、build、lint、typecheck、integration、e2e、system、fresh_consumer、real_external。
- `integration_done`: 至少一个 passing `integration`、`e2e`、`system`、`fresh_consumer` 或 `real_external` validator。
- `handoff_done`: 至少一个 passing `fresh_consumer` 或 `real_external` validator。

`mock`、`fake`、`static` 证据不能单独支撑 `integration_done` 或 `handoff_done`。

`references/verifier-registry.json` 是 verifier authority 的 canonical registry。`workflow-control-plane` 可以读取它来拒绝不可信 claim，但不要在别的 skill 中复制 claim 规则。

## Validation

```sh
python3 skills/delivery-verification/scripts/validate_evidence_manifest.py evidence_manifest.json
```

通过后，adaptive workflow 才能记录 `claims.validated[]`。
