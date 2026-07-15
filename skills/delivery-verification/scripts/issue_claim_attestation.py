#!/usr/bin/env python3
"""Issue a workflow-bound claim attestation from validated evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_SCRIPTS = ROOT / "skills" / "workflow-control-plane" / "scripts"
REGISTRY = ROOT / "skills" / "delivery-verification" / "references" / "verifier-registry.json"
sys.path.insert(0, str(WORKFLOW_SCRIPTS))

from validate_json_artifact import load_json  # noqa: E402
from validate_workflow_manifest import validate as validate_workflow  # noqa: E402

from validate_evidence_manifest import CLAIM_REQUIRED_TYPES, validate as validate_evidence  # noqa: E402


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def relative_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"path must stay inside repo root: {path}") from exc


def clean_git_head(root: Path) -> str:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    status = subprocess.run(["git", "status", "--porcelain"], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if head.returncode or status.returncode:
        raise ValueError("repo root must be a Git worktree")
    if status.stdout.strip():
        raise ValueError("claim attestation requires a clean Git worktree")
    return head.stdout.strip()


def covered_passing(manifest: dict) -> list[dict]:
    by_id = {item["id"]: item for item in manifest["validators"]}
    ids = {
        validator_id
        for coverage in manifest["acceptance_coverage"]
        for validator_id in coverage["validator_ids"]
    }
    return [by_id[item] for item in ids if item in by_id and by_id[item]["result"] == "pass"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence_manifest")
    parser.add_argument("workflow_manifest")
    parser.add_argument("--verifier", required=True)
    parser.add_argument("--verifier-version", default="1.0.0")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    evidence_path = Path(args.evidence_manifest)
    workflow_path = Path(args.workflow_manifest)
    repo_root = Path(args.repo_root).resolve()
    errors = validate_evidence(evidence_path, repo_root) + validate_workflow(workflow_path)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    evidence = load_json(evidence_path)
    workflow = load_json(workflow_path)
    claim = evidence["claim_requested"]
    if claim == "none" or claim != workflow["claims"]["requested"]:
        print("FAIL: evidence claim must match the workflow requested claim")
        return 1

    registry = load_json(REGISTRY)
    verifier = next((item for item in registry["verifiers"] if item["id"] == args.verifier), None)
    if not verifier or verifier["trust_level"] == "blocked" or claim not in verifier["allowed_claims"]:
        print("FAIL: verifier is not authorized for the requested claim")
        return 1
    passing = covered_passing(evidence)
    eligible = [
        item for item in passing
        if item["type"] in verifier["allowed_evidence_types"]
        and item["type"] in CLAIM_REQUIRED_TYPES[claim]
    ]
    if not eligible:
        print("FAIL: verifier authority does not cover the acceptance-linked passing evidence")
        return 1

    spec_artifacts = [
        item for item in workflow["artifacts"]
        if item["type"] == "spec" and item["status"] in {"ready", "approved"}
    ]
    if len(spec_artifacts) != 1:
        print("FAIL: attestation requires exactly one ready/approved spec artifact")
        return 1
    contract_artifacts = [
        item for item in workflow["artifacts"]
        if item["type"] == "acceptance_contract" and item["status"] == "approved"
    ]
    if len(contract_artifacts) != 1:
        print("FAIL: attestation requires exactly one approved acceptance contract artifact")
        return 1
    try:
        evidence_relative = relative_path(evidence_path, repo_root)
        spec_path = repo_root / spec_artifacts[0]["path"]
        spec_digest = digest(spec_path)
        if evidence["spec_digest"] != spec_digest or spec_artifacts[0].get("digest") != spec_digest:
            print("FAIL: evidence/spec artifact digest does not match the approved Spec file")
            return 1
        contract_artifact = contract_artifacts[0]
        contract_path = repo_root / contract_artifact["path"]
        contract_digest = digest(contract_path)
        contract = load_json(contract_path)
        if (
            contract_artifact.get("producer") != "specflow"
            or contract_artifact.get("semantic_owner") != "spec-review"
            or contract_artifact.get("digest") != contract_digest
            or evidence["acceptance_contract_path"] != contract_artifact["path"]
            or evidence["acceptance_contract_digest"] != contract_digest
            or set(contract_artifact.get("covers_acceptance", [])) != set(contract["required_acceptance_ids"])
        ):
            print("FAIL: evidence must bind the approved Spec-review acceptance contract artifact")
            return 1
        commit_sha = clean_git_head(repo_root)
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1

    signed = {
        "claim": claim,
        "status": "validated",
        "verifier": args.verifier,
        "evidence_ids": sorted(item["id"] for item in eligible),
        "attested_at": datetime.now(timezone.utc).isoformat(),
        "attestation": {
            "workflow_id": workflow["run_id"],
            "claim_type": claim,
            "commit_sha": commit_sha,
            "strategy_id": workflow["selected_strategy"],
            "strategy_version": workflow["strategy_version"],
            "registry_digest": digest(REGISTRY),
            "evidence_manifest_path": evidence_relative,
            "evidence_manifest_digest": digest(evidence_path),
            "spec_digest": spec_digest,
            "acceptance_contract_path": contract_artifact["path"],
            "acceptance_contract_digest": contract_digest,
            "verifier_id": args.verifier,
            "verifier_version": args.verifier_version,
            "result": "pass",
        },
    }
    Path(args.output).write_text(json.dumps(signed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Claim attestation issued: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
