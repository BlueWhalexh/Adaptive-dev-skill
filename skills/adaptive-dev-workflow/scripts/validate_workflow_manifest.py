#!/usr/bin/env python3
"""Validate workflow_manifest.json structure and claim boundaries."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from validate_json_artifact import load_json, validate_instance


SKILL_DIR = Path(__file__).resolve().parents[1]
SCHEMA = SKILL_DIR / "schemas" / "workflow-manifest.schema.json"
VERIFIER_SCHEMA = SKILL_DIR / "schemas" / "verifier-registry.schema.json"
VERIFIER_REGISTRY = SKILL_DIR / "references" / "verifier-registry.json"
STRATEGIES = SKILL_DIR / "references" / "strategies"
FORBIDDEN_TOP_LEVEL = {
    "route",
    "route_card",
    "evidence_card",
    "artifact_state",
    "delivery_claim",
    "claim_ceiling",
}
SELF_VERIFIERS = {"agent", "implementer", "self", "coding-agent", "developer"}
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,80}$")
VERSION = re.compile(r"^\d+\.\d+(?:\.\d+)?$")
CLAIM_RANK = {"none": 0, "dev_done": 1, "integration_done": 2, "handoff_done": 3}
ROUTING_TOKENS = {
    "openspec",
    "repo_native",
    "fallback",
    "superpowers",
    "quick-change",
    "focused-change",
    "root-cause-debug",
    "spec-driven-feature",
    "complex-real-slice",
    "migration-critical",
    "spike",
    "review-only",
}
HARD_DESIGN_TRIGGERS = {
    "new_boundary",
    "cross_module_flow",
    "cross_service_flow",
    "public_api",
    "event_contract",
    "data_model",
    "migration",
    "auth_permission_security",
    "secrets_pii_payments",
    "state_machine",
    "concurrency_idempotency_recovery",
    "external_integration",
    "runtime_operability_performance_observability",
    "multiple_viable_approaches",
}


def safe_path(value: str) -> bool:
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def load_strategy(strategy_id: str) -> tuple[dict, str | None]:
    if not SAFE_ID.match(strategy_id):
        return {}, f"strategy id is unsafe: {strategy_id}"
    path = STRATEGIES / f"{strategy_id}.json"
    if not path.exists():
        return {}, f"unknown strategy: {strategy_id}"
    return load_json(path), None


def load_verifiers() -> tuple[dict[str, dict], list[str]]:
    registry = load_json(VERIFIER_REGISTRY)
    schema = load_json(VERIFIER_SCHEMA)
    errors = validate_instance(registry, schema)
    by_id: dict[str, dict] = {}
    for verifier in registry.get("verifiers", []):
        verifier_id = str(verifier.get("id", "")).strip()
        if verifier_id in by_id:
            errors.append(f"duplicate verifier id: {verifier_id}")
        by_id[verifier_id] = verifier
        if not SAFE_ID.match(verifier_id):
            errors.append(f"verifier id is unsafe: {verifier_id}")
    return by_id, errors


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    manifest = load_json(path)
    schema = load_json(SCHEMA)
    errors.extend(validate_instance(manifest, schema))
    if errors:
        return errors

    for key in FORBIDDEN_TOP_LEVEL:
        if key in manifest:
            errors.append(f"forbidden old control-plane field: {key}")

    if not SAFE_ID.match(manifest["run_id"]):
        errors.append(f"run_id is unsafe: {manifest['run_id']}")
    if not VERSION.match(manifest["strategy_version"]):
        errors.append(f"strategy_version must be semver-like major.minor[.patch]: {manifest['strategy_version']}")
    if not manifest["skill_suite_version"].strip():
        errors.append("skill_suite_version must be non-empty")

    classification = manifest["classification"]
    mixed_profiles = sorted(set(classification["profiles"]) & ROUTING_TOKENS)
    if mixed_profiles:
        errors.append("classification.profiles must not contain routing/strategy tokens: " + ", ".join(mixed_profiles))

    routing = manifest["routing"]
    if routing["strategy_id"] != manifest["selected_strategy"]:
        errors.append("routing.strategy_id must match selected_strategy")
    strategy, strategy_error = load_strategy(manifest["selected_strategy"])
    if strategy_error:
        errors.append(strategy_error)
    if strategy:
        if manifest["strategy_version"] != strategy["version"]:
            errors.append(f"strategy_version must match registry version {strategy['version']}")
        if manifest["current_stage"] not in strategy["stages"]:
            errors.append(f"current_stage {manifest['current_stage']!r} is not in selected strategy stages")
        if classification["risk"] not in strategy["risk"]:
            errors.append(f"classification.risk {classification['risk']} is not allowed by selected strategy")
        if classification["mode"] not in strategy["modes"]:
            errors.append(f"classification.mode {classification['mode']} is not allowed by selected strategy")
        design = manifest["design_control"]
        if design["policy"] != strategy["design_policy"]:
            errors.append(f"design_control.policy must match selected strategy: expected {strategy['design_policy']}")
        if design["review"] != strategy["design_review"]:
            errors.append(f"design_control.review must match selected strategy: expected {strategy['design_review']}")

    resume = manifest["resume"]
    if not SAFE_ID.match(resume["checkpoint_id"]):
        errors.append(f"resume.checkpoint_id is unsafe: {resume['checkpoint_id']}")
    if strategy and resume["resume_from_stage"] not in strategy["stages"]:
        errors.append(f"resume.resume_from_stage {resume['resume_from_stage']!r} is not in selected strategy stages")

    artifact_types = [artifact["type"] for artifact in manifest["artifacts"]]
    artifact_ids = {artifact["id"] for artifact in manifest["artifacts"]}
    for artifact_id in resume["last_validated_artifact_ids"]:
        if artifact_id not in artifact_ids:
            errors.append(f"resume references missing artifact id: {artifact_id}")
    for artifact in manifest["artifacts"]:
        if not SAFE_ID.match(artifact["id"]):
            errors.append(f"artifact id is unsafe: {artifact['id']}")
        if not safe_path(artifact["path"]):
            errors.append(f"artifact path must be relative and stay inside repo: {artifact['path']}")

    design = manifest["design_control"]
    approval = design["approval"]
    topology = design["documentation_topology"]
    if design["policy"] == "none":
        for forbidden in ["artifact_id", "embedded_in", "section_ref"]:
            if design.get(forbidden):
                errors.append(f"design_control.{forbidden} must be empty when policy is none")
        if topology != "compact":
            errors.append("design policy none requires documentation_topology=compact")
    if design["policy"] == "embedded":
        if topology != "compact":
            errors.append("embedded design requires documentation_topology=compact")
        if not design.get("embedded_in"):
            errors.append("embedded design requires design_control.embedded_in")
        elif design["embedded_in"] not in artifact_ids:
            errors.append(f"embedded design references missing plan artifact: {design['embedded_in']}")
        if not design.get("section_ref"):
            errors.append("embedded design requires non-empty design_control.section_ref")
    if design["policy"] == "standalone":
        if topology == "compact":
            errors.append("standalone design requires single_file_design or split_design_workspace topology")
        artifact_id = design.get("artifact_id")
        if not artifact_id:
            errors.append("standalone design requires design_control.artifact_id")
        elif artifact_id not in artifact_ids:
            errors.append(f"standalone design references missing technical_design artifact: {artifact_id}")
    if topology == "split_design_workspace" and design["policy"] != "standalone":
        errors.append("split_design_workspace requires standalone technical design")

    if design["review"] == "none" and approval["status"] != "approved":
        errors.append("design review none still requires an approved no-op approval record")
    if design["review"] != "none" and approval["status"] != "approved":
        errors.append("design review must be approved before downstream planning")
    if design["review"] == "independent":
        producer = ""
        artifact_id = design.get("artifact_id") or design.get("embedded_in")
        for artifact in manifest["artifacts"]:
            if artifact["id"] == artifact_id:
                producer = artifact["producer"]
                break
        if approval["reviewer_kind"] != "agent":
            errors.append("independent design review requires reviewer_kind=agent")
        if producer and approval["reviewer"].strip().lower() == producer.strip().lower():
            errors.append("independent design reviewer cannot equal artifact producer")
    if design["review"] == "human" and approval["reviewer_kind"] != "human":
        errors.append("human design review requires reviewer_kind=human")

    hard_triggered = bool(set(design["triggers"]) & HARD_DESIGN_TRIGGERS)
    high_risk_implementation = manifest["classification"]["risk"] == "L3" and manifest["classification"]["mode"] not in {"review", "spike"}
    if (hard_triggered or high_risk_implementation or manifest["classification"]["mode"] == "migration") and design["policy"] != "standalone":
        errors.append("L3, migration, or hard design triggers require standalone technical design")

    requested = manifest["claims"]["requested"]
    if strategy and CLAIM_RANK[requested] > CLAIM_RANK[strategy["max_claim_request"]]:
        errors.append(f"{manifest['selected_strategy']} cannot request {requested}; max is {strategy['max_claim_request']}")
    if requested != "none" and not any(kind in artifact_types for kind in ["implementation", "evidence_manifest", "task_packet"]):
        errors.append(f"{requested} cannot be requested by analysis/spec/plan artifacts alone")

    verifiers, verifier_errors = load_verifiers()
    errors.extend(verifier_errors)
    for signed in manifest["claims"]["validated"]:
        verifier = signed["verifier"].strip().lower()
        if verifier in SELF_VERIFIERS:
            errors.append(f"validated claim cannot be self-signed by {signed['verifier']!r}")
        if signed["verifier"] not in verifiers:
            errors.append(f"unknown claim verifier: {signed['verifier']}")
        else:
            verifier_record = verifiers[signed["verifier"]]
            if verifier_record["trust_level"] == "blocked":
                errors.append(f"claim verifier is blocked: {signed['verifier']}")
            if signed["claim"] not in verifier_record["allowed_claims"]:
                errors.append(f"verifier {signed['verifier']} cannot sign {signed['claim']}")
        if strategy and CLAIM_RANK[signed["claim"]] > CLAIM_RANK[strategy["max_claim_request"]]:
            errors.append(f"{manifest['selected_strategy']} cannot validate {signed['claim']}; max is {strategy['max_claim_request']}")
        if signed["status"] == "validated" and not signed["evidence_ids"]:
            errors.append(f"validated {signed['claim']} requires evidence_ids")
        if signed["claim"] in {"integration_done", "handoff_done"} and "evidence_manifest" not in artifact_types:
            errors.append(f"{signed['claim']} requires an evidence_manifest artifact")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="workflow_manifest.json path")
    args = parser.parse_args()

    errors = validate(Path(args.manifest))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"Workflow manifest valid: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
