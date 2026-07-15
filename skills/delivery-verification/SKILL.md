---
name: delivery-verification
description: Use when validating evidence manifests, deciding dev_done/integration_done/handoff_done claims, issuing verifier attestations, preventing completion overclaim, or requiring fresh consumer / real external verification. 当任务需要证据矩阵、交付验收、claim attestation、fresh consumer、real external、E2E/integration/system 证据或防止假完成时使用。
---

# Delivery Verification

目标：只让 verifier 根据证据出具 attestation。实现者可以请求 claim，但不能自己生成 validated claim。

## Evidence Manifest

Canonical input 是 JSON：

```json
{
  "evidence_manifest_id": "ev-001",
  "acceptance_contract_path": "docs/evidence/acceptance-contract.json",
  "acceptance_contract_digest": "sha256:<acceptance-contract>",
  "spec_digest": "sha256:<approved-spec>",
  "required_acceptance_ids": ["AC-1"],
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

每条 acceptance 必须引用至少一个 passing validator。claim 所需的证据类型必须来自 acceptance 实际引用的 passing validator；未被 acceptance coverage 引用的全局 PASS 不能签发 claim。

`required_acceptance_ids` 必须来自 `acceptance-contract.json`，且与 `acceptance_coverage` 完全相等；不得只挑选已通过的 acceptance。该 contract 必须是 Spec review 已批准并登记进 artifact graph 的 canonical artifact：`producer=specflow`、`semantic_owner=spec-review`，同时绑定 approved Spec path/digest 和完整 acceptance 集合。validator 必须从 repo root 重算两层 digest，不能相信 evidence 自报或实现者另建的 companion。

`references/verifier-registry.json` 是 verifier authority 的 canonical registry。`workflow-control-plane` 可以读取它来拒绝不可信 claim，但不要在别的 skill 中复制 claim 规则。

## Validation

```sh
python3 skills/delivery-verification/scripts/validate_evidence_manifest.py evidence_manifest.json --repo-root .
```

通过后生成 attestation：

```sh
python3 skills/delivery-verification/scripts/issue_claim_attestation.py \
  evidence_manifest.json workflow_manifest.json \
  --verifier evidence-manifest-validator --repo-root . \
  --output claim_attestation.json
```

把该 JSON 放入 transition request 的 `claim_attestations[]`。只有 `workflow-control-plane` 能记录 `claims.validated[]`。

本地 attestation 是可重复校验的 evidence binding，不是密码学身份认证：签发要求 clean Git HEAD，并绑定 approved Spec、完整 acceptance、真实 evidence 文件和 verifier registry。面对不可信执行者或 prompt injection，必须由隔离 CI/外部 verifier 持有签名密钥或发布权限；不要把本地 producer 字符串当安全身份。
