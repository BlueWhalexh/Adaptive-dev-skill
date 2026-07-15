#!/usr/bin/env python3
"""Apply a transition_request.json to workflow_manifest.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from validate_json_artifact import load_json, validate_instance
from validate_workflow_manifest import load_strategy, validate as validate_workflow_manifest


SKILL_DIR = Path(__file__).resolve().parents[1]
DELIVERY_DIR = SKILL_DIR.parent / "delivery-verification"
sys.path.insert(0, str(DELIVERY_DIR / "scripts"))
from validate_evidence_manifest import CLAIM_REQUIRED_TYPES, validate as validate_evidence_manifest  # noqa: E402

REQUEST_SCHEMA = SKILL_DIR / "schemas" / "transition-request.schema.json"
RESULT_SCHEMA = SKILL_DIR / "schemas" / "transition-result.schema.json"
VERIFIER_REGISTRY = DELIVERY_DIR / "references" / "verifier-registry.json"
CLAIM_RANK = {"none": 0, "dev_done": 1, "integration_done": 2, "handoff_done": 3}


def result(workflow_id: str, status: str, current_stage: str, workflow_state: str, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    value = {
        "schema_version": 2,
        "workflow_id": workflow_id,
        "status": status,
        "current_stage": current_stage,
        "workflow_state": workflow_state,
        "errors": errors,
        "warnings": warnings,
    }
    schema_errors = validate_instance(value, load_json(RESULT_SCHEMA))
    if schema_errors:
        raise SystemExit("FAIL: invalid transition result: " + "; ".join(schema_errors))
    return value


def next_stage(strategy: dict[str, Any], current_stage: str) -> str:
    stages = strategy["stages"]
    index = stages.index(current_stage)
    return stages[index + 1] if index + 1 < len(stages) else current_stage


def propagate_stale(artifacts: list[dict[str, Any]], changed_ids: set[str]) -> None:
    by_id = {artifact["id"]: artifact for artifact in artifacts}
    reverse: dict[str, list[str]] = defaultdict(list)
    for artifact in artifacts:
        for dep_id in artifact["depends_on"]:
            if dep_id in by_id:
                reverse[dep_id].append(artifact["id"])

    queue: deque[str] = deque(changed_ids)
    seen: set[str] = set()
    while queue:
        source = queue.popleft()
        for downstream_id in reverse[source]:
            if downstream_id in seen:
                continue
            seen.add(downstream_id)
            downstream = by_id[downstream_id]
            if downstream["status"] not in {"missing", "rejected"}:
                downstream["status"] = "stale"
            queue.append(downstream_id)


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def validate_claim_attestation(signed: dict[str, Any], manifest: dict[str, Any], repo_root: Path) -> list[str]:
    errors: list[str] = []
    attestation = signed["attestation"]
    evidence_path = (repo_root / attestation["evidence_manifest_path"]).resolve()
    try:
        evidence_path.relative_to(repo_root.resolve())
    except ValueError:
        return ["CLAIM_ATTESTATION_INVALID: evidence path escapes repo root"]
    if not evidence_path.is_file():
        return ["CLAIM_ATTESTATION_INVALID: evidence manifest file is missing"]
    if sha256(evidence_path) != attestation["evidence_manifest_digest"]:
        errors.append("CLAIM_ATTESTATION_INVALID: evidence manifest digest mismatch")
    errors.extend(f"CLAIM_ATTESTATION_INVALID: {item}" for item in validate_evidence_manifest(evidence_path, repo_root))
    evidence = load_json(evidence_path)
    if evidence.get("claim_requested") != signed["claim"]:
        errors.append("CLAIM_ATTESTATION_INVALID: evidence claim mismatch")
    if evidence.get("spec_digest") != attestation["spec_digest"]:
        errors.append("CLAIM_ATTESTATION_INVALID: evidence Spec digest mismatch")

    passing_ids = {
        item["id"] for item in evidence.get("validators", []) if item.get("result") == "pass"
    }
    covered_ids = {
        validator_id
        for coverage in evidence.get("acceptance_coverage", [])
        for validator_id in coverage.get("validator_ids", [])
    }
    if not set(signed["evidence_ids"]).issubset(passing_ids & covered_ids):
        errors.append("CLAIM_ATTESTATION_INVALID: signed evidence ids are not covered passing validators")

    if sha256(VERIFIER_REGISTRY) != attestation["registry_digest"]:
        errors.append("CLAIM_ATTESTATION_INVALID: verifier registry digest mismatch")
    registry = load_json(VERIFIER_REGISTRY)
    verifier = next((item for item in registry["verifiers"] if item["id"] == signed["verifier"]), None)
    if not verifier or signed["claim"] not in verifier["allowed_claims"] or verifier["trust_level"] == "blocked":
        errors.append("CLAIM_ATTESTATION_INVALID: verifier is not authorized for claim")
    else:
        validators_by_id = {item["id"]: item for item in evidence.get("validators", [])}
        signed_types = {validators_by_id[item]["type"] for item in signed["evidence_ids"] if item in validators_by_id}
        if not signed_types or not signed_types.issubset(set(verifier["allowed_evidence_types"])):
            errors.append("CLAIM_ATTESTATION_INVALID: verifier is not authorized for signed evidence types")
        if not signed_types.intersection(CLAIM_REQUIRED_TYPES[signed["claim"]]):
            errors.append("CLAIM_ATTESTATION_INVALID: signed evidence types do not satisfy the claim level")

    spec_artifacts = [item for item in manifest["artifacts"] if item["type"] == "spec" and item["status"] in {"ready", "approved"}]
    if len(spec_artifacts) != 1:
        errors.append("CLAIM_ATTESTATION_INVALID: exactly one active Spec artifact is required")
    else:
        spec_path = (repo_root / spec_artifacts[0]["path"]).resolve()
        try:
            spec_path.relative_to(repo_root.resolve())
            actual_spec_digest = sha256(spec_path)
        except (ValueError, OSError):
            actual_spec_digest = ""
        if not actual_spec_digest or actual_spec_digest != attestation["spec_digest"] or spec_artifacts[0].get("digest") != actual_spec_digest:
            errors.append("CLAIM_ATTESTATION_INVALID: approved Spec file digest mismatch")

    contract_artifacts = [
        item for item in manifest["artifacts"]
        if item["type"] == "acceptance_contract" and item["status"] == "approved"
    ]
    if len(contract_artifacts) != 1:
        errors.append("CLAIM_ATTESTATION_INVALID: exactly one approved acceptance contract artifact is required")
    else:
        contract_artifact = contract_artifacts[0]
        contract_path = (repo_root / contract_artifact["path"]).resolve()
        try:
            contract_path.relative_to(repo_root.resolve())
            actual_contract_digest = sha256(contract_path)
            contract = load_json(contract_path)
        except (ValueError, OSError):
            actual_contract_digest = ""
            contract = {}
        if (
            contract_artifact.get("producer") != "specflow"
            or contract_artifact.get("semantic_owner") != "spec-review"
            or contract_artifact.get("digest") != actual_contract_digest
            or evidence.get("acceptance_contract_path") != contract_artifact.get("path")
            or evidence.get("acceptance_contract_digest") != actual_contract_digest
            or attestation.get("acceptance_contract_path") != contract_artifact.get("path")
            or attestation.get("acceptance_contract_digest") != actual_contract_digest
            or set(contract_artifact.get("covers_acceptance", [])) != set(contract.get("required_acceptance_ids", []))
        ):
            errors.append("CLAIM_ATTESTATION_INVALID: acceptance contract is not the canonical Spec-review artifact")

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if head.returncode or head.stdout.strip() != attestation["commit_sha"]:
        errors.append("CLAIM_ATTESTATION_INVALID: commit SHA does not match repo HEAD")
    status = subprocess.run(["git", "status", "--porcelain"], cwd=repo_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if status.returncode:
        errors.append("CLAIM_ATTESTATION_INVALID: cannot inspect worktree state")
    else:
        allowed_control_paths = {
            attestation["evidence_manifest_path"],
            evidence.get("acceptance_contract_path", ""),
        }
        dirty_product_paths = []
        for line in status.stdout.splitlines():
            relative = line[3:].split(" -> ")[-1]
            if not relative.startswith(".agent/") and relative not in allowed_control_paths:
                dirty_product_paths.append(relative)
        if dirty_product_paths:
            errors.append(f"CLAIM_ATTESTATION_INVALID: product worktree changed after attestation: {sorted(dirty_product_paths)}")
    return errors


def apply_transition(manifest: dict[str, Any], request: dict[str, Any], repo_root: Path | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    errors = validate_instance(request, load_json(REQUEST_SCHEMA))
    if errors:
        return manifest, result(request.get("workflow_id", ""), "rejected", manifest.get("current_stage", ""), manifest.get("workflow_state", "blocked"), errors, [])
    if request["workflow_id"] != manifest["run_id"]:
        return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["RESUME_CONFLICT: workflow_id mismatch"], [])
    for item in manifest.get("transition_log", []):
        if item["transition_id"] == request["transition_id"]:
            return manifest, result(
                request["workflow_id"],
                item.get("result_status", "applied"),
                item.get("result_stage", manifest["current_stage"]),
                item.get("result_workflow_state", manifest["workflow_state"]),
                [],
                ["duplicate transition_id returned its original result idempotently"],
            )
    if request["expected_manifest_revision"] != manifest["manifest_revision"]:
        return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["RESUME_CONFLICT: manifest revision mismatch"], [])
    if request["stage_id"] != manifest["current_stage"]:
        return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["RESUME_CONFLICT: stage_id mismatch"], [])

    strategy, strategy_error = load_strategy(manifest["selected_strategy"])
    if strategy_error:
        return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], [strategy_error], [])

    review = request.get("review_result")
    review_control = dict(manifest["review_control"])
    stage_gate = strategy.get("stage_gates", {}).get(manifest["current_stage"])
    review_mode = (stage_gate or {}).get("review_mode", "none")
    if request["status"] == "completed" and stage_gate:
        if request["producer"]["skill"] not in stage_gate["allowed_producers"]:
            return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["STAGE_PRODUCER_UNAUTHORIZED: producer is not allowed by strategy stage gate"], [])
        if len(request["evidence_refs"]) < stage_gate["min_evidence_refs"]:
            return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["STAGE_EVIDENCE_REQUIRED: stage gate evidence is missing"], [])
    if review_mode != "none" and request["status"] == "completed":
        if review is None:
            return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["REVIEW_RESULT_REQUIRED: review stage completion requires review_result"], [])
        actor_id = request["producer"].get("actor_id", "")
        if not actor_id or actor_id != review["reviewer_id"]:
            return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["REVIEWER_IDENTITY_INVALID: producer actor_id must match reviewer_id"], [])
        artifact_producers = {item["producer"] for item in manifest["artifacts"]}
        if not artifact_producers.intersection(review["reviewed_producer_ids"]):
            return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["REVIEW_SCOPE_INVALID: reviewed producer is not present in artifact graph"], [])
        if review_mode in {"independent", "human"} and actor_id in review["reviewed_producer_ids"]:
            return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["REVIEW_INDEPENDENCE_REQUIRED: reviewer also produced the reviewed work"], [])
        prior_passes = review_control["passes_completed"] if review_control["stage_id"] == manifest["current_stage"] else 0
        expected_pass = prior_passes + 1
        if review["pass_number"] != expected_pass:
            return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], [f"REVIEW_PASS_CONFLICT: expected pass {expected_pass}"], [])
        if review["decision"] == "approved" and review["max_severity"] in {"major", "critical"}:
            return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["REVIEW_APPROVAL_INVALID: unresolved Major/Critical finding"], [])
        if review["decision"] in {"changes_requested", "human_required"} and not review["finding_refs"]:
            return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["REVIEW_FINDINGS_REQUIRED: non-approved review must reference at least one finding"], [])
    elif review is not None:
        return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["REVIEW_RESULT_UNEXPECTED: strategy stage gate does not require review"], [])

    updated = dict(manifest)
    artifacts = [dict(item) for item in manifest["artifacts"]]
    by_id = {item["id"]: item for item in artifacts}
    changed_ids: set[str] = set()

    for change in request["artifact_changes"]:
        artifact = change["artifact"]
        artifact_id = artifact["id"]
        old_digest = by_id.get(artifact_id, {}).get("digest")
        new_digest = artifact.get("digest")
        if artifact_id in by_id:
            by_id[artifact_id].update(artifact)
        else:
            artifacts.append(artifact)
            by_id[artifact_id] = artifact
        if change["change_type"] == "content_changed" and (old_digest != new_digest or old_digest is None):
            changed_ids.add(artifact_id)
    if changed_ids:
        propagate_stale(artifacts, changed_ids)
    repair_pending = (
        review_control.get("next_action") == "repair_required"
        and manifest["current_stage"] == review_control.get("repair_stage")
    )
    if repair_pending and request["status"] == "completed" and not changed_ids:
        return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["REPAIR_PROGRESS_REQUIRED: repair stage must submit a content_changed artifact with a new digest"], [])

    claim_invalidated = any(
        by_id[item]["type"] in {"spec", "acceptance_contract", "technical_design", "plan", "implementation", "evidence_manifest"}
        for item in changed_ids
    )
    requested = "none" if claim_invalidated else manifest["claims"]["requested"]
    for claim in request["claim_requests"]:
        if CLAIM_RANK[claim] > CLAIM_RANK[requested]:
            requested = claim

    validated = [] if claim_invalidated else list(manifest["claims"]["validated"])
    attestations = request.get("claim_attestations", [])
    if attestations and request["producer"]["skill"] != "delivery-verification":
        return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["CLAIM_ATTESTATION_UNAUTHORIZED: only delivery-verification may submit attestations"], [])
    for signed in attestations:
        attestation = signed["attestation"]
        claim = signed["claim"]
        if (
            signed["status"] != "validated"
            or attestation["result"] != "pass"
            or attestation["workflow_id"] != manifest["run_id"]
            or attestation["claim_type"] != claim
            or attestation["strategy_id"] != manifest["selected_strategy"]
            or attestation["strategy_version"] != manifest["strategy_version"]
            or attestation["verifier_id"] != signed["verifier"]
        ):
            return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["CLAIM_ATTESTATION_INVALID: attestation does not match the active workflow"], [])
        if repo_root is None:
            return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["CLAIM_ATTESTATION_INVALID: --repo-root is required"], [])
        attestation_errors = validate_claim_attestation(signed, manifest, repo_root)
        if attestation_errors:
            return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], attestation_errors, [])
        if CLAIM_RANK[claim] > CLAIM_RANK[requested]:
            return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["CLAIM_ATTESTATION_UNREQUESTED: attestation exceeds the requested claim"], [])
        validated = [item for item in validated if item["claim"] != claim]
        validated.append(signed)

    state = "active"
    blocked_reason = ""
    transition_status = "applied"
    target_stage = next_stage(strategy, manifest["current_stage"]) if request["status"] == "completed" else manifest["current_stage"]
    if review is not None:
        review_control = {
            "stage_id": manifest["current_stage"],
            "passes_completed": review["pass_number"],
            "last_severity": review["max_severity"],
            "decision": review["decision"],
            "next_action": "none",
            "repair_stage": "",
            "finding_refs": review["finding_refs"],
        }
        if review["decision"] == "changes_requested":
            repair_stage = stage_gate["repair_stage"]
            target_stage = repair_stage
            transition_status = "repair_required"
            review_control["next_action"] = "repair_required"
            review_control["repair_stage"] = repair_stage
            if review["pass_number"] >= strategy["execution_policy"]["max_review_passes"]:
                review_control["passes_completed"] = 0
        elif review["decision"] == "human_required":
            target_stage = manifest["current_stage"]
            state = "blocked"
            blocked_reason = "REVIEW_HUMAN_REQUIRED"
            transition_status = "blocked"
            review_control["next_action"] = "human_required"
    if request["status"] in {"blocked", "failed", "human_required"}:
        state = "blocked"
        blocked_reason = (request["error"] or {}).get("code") or request["status"]
        transition_status = "blocked"

    is_final_completion = (
        request["status"] == "completed"
        and transition_status == "applied"
        and manifest["current_stage"] == strategy["stages"][-1]
    )
    if is_final_completion and state != "blocked":
        minimum_claim = strategy.get("minimum_close_claim", "none")
        if manifest["classification"]["mode"] == "handoff" and CLAIM_RANK[strategy["max_claim_request"]] >= CLAIM_RANK["handoff_done"]:
            minimum_claim = "handoff_done"
        required_claim = requested if CLAIM_RANK[requested] >= CLAIM_RANK[minimum_claim] else minimum_claim
        if required_claim != "none" and repo_root is None:
            return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["CLAIM_ATTESTATION_REQUIRED: final claim validation requires --repo-root"], [])
        for signed in validated:
            if signed["status"] == "validated" and repo_root is not None:
                final_errors = validate_claim_attestation(signed, manifest, repo_root)
                if final_errors:
                    return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], final_errors, [])
        claim_satisfied = required_claim == "none" or any(
            item["status"] == "validated" and CLAIM_RANK[item["claim"]] >= CLAIM_RANK[required_claim]
            for item in validated
        )
        if not claim_satisfied:
            return manifest, result(request["workflow_id"], "rejected", manifest["current_stage"], manifest["workflow_state"], ["CLAIM_ATTESTATION_REQUIRED: final stage cannot close without the requested validated claim"], [])
        state = "closed"

    updated["artifacts"] = artifacts
    updated["current_stage"] = target_stage
    updated["routing"] = {
        **manifest["routing"],
        "required_skills": manifest["routing"]["skill_plan"].get(target_stage, []),
    }
    updated["workflow_state"] = state
    updated["manifest_revision"] = manifest["manifest_revision"] + 1
    updated["resume"] = {
        "checkpoint_id": f"cp-{target_stage}",
        "resume_from_stage": target_stage,
        "last_validated_artifact_ids": [item["id"] for item in artifacts if item["status"] in {"ready", "approved"}],
        "blocked_reason": blocked_reason,
    }
    updated["claims"] = {"requested": requested, "validated": validated}
    updated["review_control"] = review_control
    updated["transition_log"] = manifest.get("transition_log", []) + [{
        "transition_id": request["transition_id"],
        "stage_id": request["stage_id"],
        "status": request["status"],
        "producer_skill": request["producer"]["skill"],
        "producer_actor_id": request["producer"].get("actor_id", ""),
        "evidence_refs": request["evidence_refs"],
        "review_decision": (review or {}).get("decision", ""),
        "result_status": transition_status,
        "result_stage": target_stage,
        "result_workflow_state": state,
    }]
    return updated, result(request["workflow_id"], transition_status, target_stage, state, [], [])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="workflow_manifest.json path")
    parser.add_argument("transition_request", help="transition_request.json path")
    parser.add_argument("--output", help="output manifest path; defaults to in-place")
    parser.add_argument("--result", help="optional transition_result.json path")
    parser.add_argument("--repo-root", help="Git worktree root; required when submitting claim attestations")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    manifest = load_json(manifest_path)
    request = load_json(Path(args.transition_request))
    repo_root = Path(args.repo_root).resolve() if args.repo_root else None
    updated, transition_result = apply_transition(manifest, request, repo_root)
    if transition_result["status"] == "rejected":
        print(json.dumps(transition_result, ensure_ascii=False, indent=2))
        return 1

    output = Path(args.output) if args.output else manifest_path
    pending = output.with_name(output.name + ".pending")
    pending.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    errors = validate_workflow_manifest(pending)
    if errors:
        pending.unlink(missing_ok=True)
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    pending.replace(output)
    if args.result:
        Path(args.result).write_text(json.dumps(transition_result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(transition_result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
