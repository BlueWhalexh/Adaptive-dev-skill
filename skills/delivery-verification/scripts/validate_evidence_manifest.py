#!/usr/bin/env python3
"""Validate JSON evidence_manifest and requested claim level."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_SCRIPTS = ROOT / "skills" / "workflow-control-plane" / "scripts"
DELIVERY_SCHEMAS = ROOT / "skills" / "delivery-verification" / "schemas"
sys.path.insert(0, str(WORKFLOW_SCRIPTS))

from validate_json_artifact import load_json, validate_instance  # noqa: E402


CLAIM_REQUIRED_TYPES = {
    "none": set(),
    "dev_done": {
        "unit",
        "manual",
        "diff_review",
        "build",
        "lint",
        "typecheck",
        "integration",
        "e2e",
        "system",
        "fresh_consumer",
        "real_external",
    },
    "integration_done": {"integration", "e2e", "system", "fresh_consumer", "real_external"},
    "handoff_done": {"fresh_consumer", "real_external"},
}


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def validate(path: Path, repo_root: Path | None = None) -> list[str]:
    manifest = load_json(path)
    schema = load_json(DELIVERY_SCHEMAS / "evidence-manifest.schema.json")
    errors = validate_instance(manifest, schema)
    if errors:
        return errors

    validators = manifest["validators"]
    validators_by_id = {item["id"]: item for item in validators}
    if len(validators_by_id) != len(validators):
        errors.append("validator ids must be unique")
    acceptance_ids = [item["acceptance_id"] for item in manifest["acceptance_coverage"]]
    if len(set(acceptance_ids)) != len(acceptance_ids):
        errors.append("acceptance ids must be unique")
    required_acceptance_ids = manifest["required_acceptance_ids"]
    if len(set(required_acceptance_ids)) != len(required_acceptance_ids):
        errors.append("required acceptance ids must be unique")
    if set(acceptance_ids) != set(required_acceptance_ids):
        missing = sorted(set(required_acceptance_ids) - set(acceptance_ids))
        unexpected = sorted(set(acceptance_ids) - set(required_acceptance_ids))
        errors.append(f"acceptance coverage must exactly match required ids; missing={missing}, unexpected={unexpected}")

    covered_passing_types: set[str] = set()
    requested = manifest["claim_requested"]

    if requested != "none":
        if repo_root is None:
            errors.append(f"{requested} requires --repo-root to validate the acceptance contract")
        else:
            contract_path = (repo_root / manifest["acceptance_contract_path"]).resolve()
            try:
                contract_path.relative_to(repo_root.resolve())
                contract = load_json(contract_path)
                errors.extend(validate_instance(contract, load_json(DELIVERY_SCHEMAS / "acceptance-contract.schema.json")))
                if sha256(contract_path) != manifest["acceptance_contract_digest"]:
                    errors.append("acceptance contract digest mismatch")
                if contract["spec_digest"] != manifest["spec_digest"]:
                    errors.append("evidence Spec digest does not match acceptance contract")
                if set(contract["required_acceptance_ids"]) != set(required_acceptance_ids):
                    errors.append("required acceptance ids do not match acceptance contract")
                spec_path = (repo_root / contract["spec_path"]).resolve()
                spec_path.relative_to(repo_root.resolve())
                if sha256(spec_path) != contract["spec_digest"]:
                    errors.append("approved Spec file digest does not match acceptance contract")
            except (KeyError, OSError, ValueError) as exc:
                errors.append(f"invalid acceptance contract binding: {exc}")

    for coverage in manifest["acceptance_coverage"]:
        refs = coverage["validator_ids"]
        if not refs:
            errors.append(f"acceptance {coverage['acceptance_id']} must reference at least one validator")
            continue
        missing = [item for item in refs if item not in validators_by_id]
        if missing:
            errors.append(f"acceptance {coverage['acceptance_id']} references unknown validators: {', '.join(missing)}")
            continue
        passing = [validators_by_id[item] for item in refs if validators_by_id[item]["result"] == "pass"]
        if not passing:
            errors.append(f"acceptance {coverage['acceptance_id']} has no passing referenced validator")
            continue
        covered_passing_types.update(item["type"] for item in passing)

    if requested != "none":
        allowed = CLAIM_REQUIRED_TYPES[requested]
        if not covered_passing_types.intersection(allowed):
            errors.append(
                f"{requested} requires covered passing evidence type in {sorted(allowed)}; "
                f"got {sorted(covered_passing_types)}"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="evidence_manifest.json")
    parser.add_argument("--repo-root", help="repository root containing the acceptance contract")
    args = parser.parse_args()

    errors = validate(Path(args.manifest), Path(args.repo_root).resolve() if args.repo_root else None)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"Evidence manifest valid: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
