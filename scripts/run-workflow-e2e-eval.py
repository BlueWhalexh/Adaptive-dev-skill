#!/usr/bin/env python3
"""Run deterministic end-to-end checks for the control-plane artifacts."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "skills" / "workflow-control-plane"
CONTEXT = ROOT / "skills" / "context-grounding"
DELIVERY = ROOT / "skills" / "delivery-verification"
KNOWLEDGE = ROOT / "skills" / "knowledge-promotion"
HARNESS_INIT = ROOT / "skills" / "project-harness-init" / "scripts" / "init_project_harness.py"
HARNESS_VALIDATE = ROOT / "skills" / "project-harness-init" / "scripts" / "validate_project_harness.py"
HANDOFF_FRESH_CONSUMER = ROOT / "scripts" / "run-handoff-fresh-consumer-eval.py"
EVIDENCE_BINDING = {"spec_digest": "", "contract_path": "acceptance-contract.json", "contract_digest": ""}


def run(args: list[str], *, expect_ok: bool = True, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if expect_ok and result.returncode != 0:
        raise SystemExit("command failed:\n" + " ".join(args) + "\n" + result.stdout)
    if not expect_ok and result.returncode == 0:
        raise SystemExit("command unexpectedly passed:\n" + " ".join(args) + "\n" + result.stdout)
    return result


def write_json(path: Path, value: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def write_text(path: Path, value: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    return path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def route_decision() -> dict[str, Any]:
    return {
        "schema_version": 3,
        "status": "provisional",
        "classification": {
            "risk": "L3",
            "work_intent": "implement",
            "delivery_shape": "mvp",
            "scope": "cross_module",
            "uncertainty": "high",
            "pattern_familiarity": "novel",
            "profiles": ["auth", "security", "data"],
            "change_types": ["migration"],
        },
        "capability_report_ref": "capability-report.json",
        "user_constraints": {
            "network_access": "unknown",
            "production_changes": "forbidden",
            "required_spec_system": None,
            "required_execution_engine": None,
        },
        "user_overrides": [],
        "ambiguity": {"status": "clear", "reasons": []},
    }


def capability_report() -> dict[str, Any]:
    return {
        "schema_version": 3,
        "repo_revision": "e2e",
        "spec_systems": [
            {"id": "openspec", "status": "available", "evidence": ["openspec/config.yaml"]},
            {"id": "fallback", "status": "available", "evidence": ["workflow fallback"]},
        ],
        "execution_engines": [
            {"id": "local", "status": "available", "version": "builtin"},
        ],
        "method_providers": [
            {"id": "superpowers-native", "status": "available", "version": "unknown", "evidence": ["eval"]},
        ],
        "project_harness": {"status": "present", "version": "2", "evidence": ["AGENTS.md"]},
        "project_sop": {
            "status": "partial",
            "evidence": ["AGENTS.md"],
            "signals": {"instructions": ["AGENTS.md"], "project_skills": [], "test_contracts": []},
        },
    }


def route_facts_delta() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "source": "context-grounding",
        "discovered_facts": {
            "risk_floor": "L3",
            "scope": "cross_service",
            "add_profiles": ["auth", "security"],
            "add_change_types": ["migration"],
        },
        "reason_codes": ["AUTH_BOUNDARY_DISCOVERED", "CROSS_SERVICE_STATE_CHANGE"],
    }


def complex_skill_plan() -> dict[str, list[str]]:
    return {
        "ground": [],
        "context_pack_review": ["context-grounding"],
        "pack_backed_specflow": ["specflow"],
        "spec_review": ["agent-orchestration"],
        "technical_design": ["technical-design"],
        "design_review": ["agent-orchestration"],
        "minimum_real_slice_plan": ["superpowers:writing-plans"],
        "slice_execution": ["change-aware-testing"],
        "architecture_checkpoint": ["agent-orchestration"],
        "remaining_slice_execution": ["change-aware-testing"],
        "system_verification": ["change-aware-testing", "delivery-verification"],
        "delivery_review": ["agent-orchestration"],
    }


def spec_feature_skill_plan() -> dict[str, list[str]]:
    return {
        "ground": [],
        "context_pack_if_needed": ["context-grounding"],
        "pack_backed_specflow": ["specflow"],
        "spec_review": [],
        "embedded_design": ["technical-design"],
        "plan": ["superpowers:writing-plans"],
        "implementation": ["change-aware-testing"],
        "focused_and_chain_verification": ["change-aware-testing", "delivery-verification"],
        "review": [],
        "close": [],
    }


def workflow_manifest(*, requested: str = "integration_done", validated_claim: str = "integration_done") -> dict[str, Any]:
    return {
        "schema_version": 6,
        "skill_suite_version": "2026-06-24",
        "run_id": "run-control-plane-e2e",
        "manifest_revision": 1,
        "strategy_version": "2.2",
        "workflow_state": "review_ready",
        "classification": {
            "risk": "L3",
            "mode": "implement",
            "scope": "cross_module",
            "uncertainty": "high",
            "pattern_familiarity": "novel",
            "profiles": ["frontend", "api"],
        },
        "routing": {
            "process_depth": "lifecycle",
            "manifest_policy": "required",
            "spec_system": "fallback",
            "execution_engine": "local",
            "execution_policy": {"unit": "continuous_batch", "task_risk": "local", "task_exit": "focused_signal", "checkpoint": "milestone", "review": "boundary_strict", "commit": "batch", "manifest_updates": "stage_only", "max_review_passes": 2},
            "strategy_id": "complex-real-slice",
            "required_skills": ["agent-orchestration"],
            "skill_plan": complex_skill_plan(),
            "capability_report_ref": "capability-report.json",
        },
        "selected_strategy": "complex-real-slice",
        "current_stage": "delivery_review",
        "resume": {
            "checkpoint_id": "cp-delivery-review",
            "resume_from_stage": "delivery_review",
            "last_validated_artifact_ids": ["ap-001", "ctx-001", "spec-001", "td-001", "plan-001", "task-001", "impl-001", "ev-001"],
            "blocked_reason": "",
        },
        "design_control": {
            "policy": "standalone",
            "review": "independent",
            "documentation_topology": "split_design_workspace",
            "triggers": ["cross_service_flow"],
            "artifact_id": "td-001",
            "approval": {
                "status": "approved",
                "reviewer": "design-reviewer",
                "reviewer_kind": "agent",
                "evidence_ids": ["DR-001"],
            },
        },
        "review_control": {
            "stage_id": "",
            "passes_completed": 0,
            "last_severity": "none",
            "decision": "pending",
            "next_action": "none",
            "repair_stage": "",
            "finding_refs": [],
        },
        "artifacts": [
            {
                "id": "ap-001",
                "type": "analysis_pack",
                "status": "approved",
                "version": 1,
                "producer": "context-grounding",
                "depends_on": [],
                "covers_acceptance": ["AC-1"],
                "path": "docs/analysis/ap-001.md",
            },
            {
                "id": "ctx-001",
                "type": "context_manifest",
                "status": "ready",
                "version": 1,
                "producer": "context-grounding",
                "depends_on": ["ap-001"],
                "covers_acceptance": ["AC-1"],
                "path": "docs/context/ctx-001.json",
            },
            {
                "id": "spec-001",
                "type": "spec",
                "status": "approved",
                "version": 1,
                "producer": "specflow",
                "depends_on": ["ap-001"],
                "covers_acceptance": ["AC-1"],
                "path": "docs/superpowers/specs/2026-06-23-feature-spec.md",
            },
            {
                "id": "acceptance-001",
                "type": "acceptance_contract",
                "status": "approved",
                "version": 1,
                "producer": "specflow",
                "semantic_owner": "spec-review",
                "depends_on": ["spec-001"],
                "covers_acceptance": ["AC-1"],
                "path": "acceptance-contract.json",
            },
            {
                "id": "td-001",
                "type": "technical_design",
                "status": "approved",
                "version": 1,
                "producer": "technical-design",
                "depends_on": ["spec-001", "ap-001", "ctx-001"],
                "covers_acceptance": ["AC-1"],
                "path": "docs/superpowers/designs/2026-06-23-feature-technical-design.md",
            },
            {
                "id": "plan-001",
                "type": "plan",
                "status": "approved",
                "version": 1,
                "producer": "superpowers:writing-plans",
                "depends_on": ["td-001"],
                "covers_acceptance": ["AC-1"],
                "path": "docs/superpowers/plans/2026-06-23-feature.md",
            },
            {
                "id": "task-001",
                "type": "task_packet",
                "status": "ready",
                "version": 1,
                "producer": "workflow-control-plane",
                "depends_on": ["plan-001", "ctx-001"],
                "covers_acceptance": ["AC-1"],
                "path": "docs/tasks/task-001.json",
            },
            {
                "id": "impl-001",
                "type": "implementation",
                "status": "ready",
                "version": 1,
                "producer": "coding-agent",
                "depends_on": ["task-001"],
                "covers_acceptance": ["AC-1"],
                "path": "src/orders/implementation.ts",
            },
            {
                "id": "ev-001",
                "type": "evidence_manifest",
                "status": "ready",
                "version": 1,
                "producer": "delivery-verification",
                "depends_on": ["impl-001", "acceptance-001"],
                "covers_acceptance": ["AC-1"],
                "path": "docs/evidence/ev-001.json",
            },
        ],
        "claims": {
            "requested": requested,
            "validated": [
                {
                    "claim": validated_claim,
                    "status": "validated",
                    "verifier": "evidence-manifest-validator",
                    "evidence_ids": ["V-001"],
                    "attested_at": "2026-06-23T00:00:00Z",
                    "attestation": {
                        "workflow_id": "run-control-plane-e2e",
                        "claim_type": validated_claim,
                        "commit_sha": "abc123",
                        "strategy_id": "complex-real-slice",
                        "strategy_version": "2.2",
                        "registry_digest": "sha256:registry",
                        "evidence_manifest_path": "evidence-manifest.json",
                        "evidence_manifest_digest": "sha256:evidence",
                        "spec_digest": "sha256:spec-e2e",
                        "acceptance_contract_path": "acceptance-contract.json",
                        "acceptance_contract_digest": "sha256:acceptance-contract",
                        "verifier_id": "evidence-manifest-validator",
                        "verifier_version": "1.0.0",
                        "result": "pass",
                    },
                }
            ],
        },
        "transition_log": [],
    }


def evidence_manifest(claim: str, evidence_type: str, result: str = "pass") -> dict[str, Any]:
    return {
        "evidence_manifest_id": "ev-001",
        "acceptance_contract_path": EVIDENCE_BINDING["contract_path"],
        "acceptance_contract_digest": EVIDENCE_BINDING["contract_digest"],
        "spec_digest": EVIDENCE_BINDING["spec_digest"],
        "required_acceptance_ids": ["AC-1"],
        "claim_requested": claim,
        "acceptance_coverage": [{"acceptance_id": "AC-1", "validator_ids": ["V-001"]}],
        "validators": [
            {
                "id": "V-001",
                "type": evidence_type,
                "result": result,
                "command_or_method": "synthetic validator",
                "proves": "claim evidence level under test",
                "gaps": "synthetic deterministic eval",
            }
        ],
        "deferred": [],
        "review_focus": ["claim/evidence consistency"],
    }


def context_manifest(repo_root: Path, file_path: Path) -> dict[str, Any]:
    rel = file_path.relative_to(repo_root).as_posix()
    head = run(["git", "rev-parse", "HEAD"], cwd=ROOT).stdout.strip()
    return {
        "context_manifest_id": "ctx-001",
        "repo_commit": head,
        "spec_version": "spec-001-v1",
        "allowed_paths": [rel],
        "forbidden_paths": ["secrets/**"],
        "context_files": [{"path": rel, "sha256": sha256(file_path), "reason": "entry point"}],
        "runtime_audit": {"read_events": [{"path": rel, "within_allowed_paths": True, "pack_updated_before_use": True}]},
    }


def assert_harness_paths(target: Path, feature_slug: str) -> None:
    if not sorted((target / "docs" / "superpowers" / "specs").glob(f"*-{feature_slug}-spec.md")):
        raise SystemExit("project harness did not create Superpowers fallback product spec file")
    if not sorted((target / "docs" / "superpowers" / "designs").glob(f"*-{feature_slug}-technical-design.md")):
        raise SystemExit("project harness did not create Superpowers fallback technical design file")
    if not sorted((target / "docs" / "superpowers" / "plans").glob(f"*-{feature_slug}.md")):
        raise SystemExit("project harness did not create Superpowers fallback plan file")
    if sorted((target / "docs" / "superpowers" / "specs").glob(f"*-{feature_slug}-design.md")):
        raise SystemExit("project harness unexpectedly created legacy mixed spec/design file")
    if (target / "docs" / "specs").exists() or (target / "docs" / "plans").exists():
        raise SystemExit("project harness unexpectedly created legacy docs/specs or docs/plans")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="adaptive-workflow-e2e-") as tmp:
        root = Path(tmp)
        evidence_spec_path = write_text(root / "approved-evidence-spec.md", "# Approved Evidence Spec\n")
        evidence_spec_digest = "sha256:" + sha256(evidence_spec_path)
        evidence_contract_path = write_json(root / "acceptance-contract.json", {
            "schema_version": 1,
            "spec_path": "approved-evidence-spec.md",
            "spec_digest": evidence_spec_digest,
            "required_acceptance_ids": ["AC-1"],
        })
        EVIDENCE_BINDING.update({
            "spec_digest": evidence_spec_digest,
            "contract_digest": "sha256:" + sha256(evidence_contract_path),
        })
        repo = root / "repo"
        feature = "Billing MVP"
        run([sys.executable, str(HARNESS_INIT), "--root", str(repo), "--feature-id", feature, "--project-skill", "billing"])
        run([sys.executable, str(HARNESS_VALIDATE), "--root", str(repo), "--feature-id", feature, "--project-skill", "billing"])
        assert_harness_paths(repo, "billing-mvp")
        detected_capability_path = root / "detected-capability-report.json"
        run([sys.executable, str(WORKFLOW / "scripts" / "detect_capabilities.py"), "--root", str(repo), "--output", str(detected_capability_path)])
        detected_capability = json.loads(detected_capability_path.read_text(encoding="utf-8"))
        if detected_capability["project_sop"]["status"] != "ready":
            raise SystemExit("initialized project harness was not detected as a ready project SOP")

        source_file = write_text(repo / "src" / "orders" / "implementation.ts", "export const ok = true;\n")
        spec_file = write_text(repo / "docs" / "superpowers" / "specs" / "2026-06-23-feature-spec.md", "# Spec\n")

        write_json(root / "capability-report.json", capability_report())
        route_path = write_json(root / "route-decision.json", route_decision())
        ready_capability = capability_report()
        ready_capability["project_sop"] = {
            "status": "ready",
            "evidence": ["AGENTS.md", ".agent/skills/orders/SKILL.md", ".agent/skills/orders/references/testing.md"],
            "signals": {
                "instructions": ["AGENTS.md"],
                "project_skills": [".agent/skills/orders/SKILL.md"],
                "test_contracts": [".agent/skills/orders/references/testing.md"],
            },
        }
        write_json(root / "capability-ready-sop.json", ready_capability)

        sop_iteration = route_decision()
        sop_iteration["capability_report_ref"] = "capability-ready-sop.json"
        sop_iteration["classification"].update({
            "risk": "L2",
            "work_intent": "implement",
            "delivery_shape": "feature",
            "scope": "module",
            "uncertainty": "low",
            "pattern_familiarity": "known",
            "profiles": ["frontend"],
            "change_types": ["feature"],
        })
        sop_iteration_path = write_json(root / "route-sop-iteration.json", sop_iteration)
        sop_iteration_resolved_path = root / "resolved-sop-iteration.json"

        high_uncertainty_sop = json.loads(json.dumps(sop_iteration))
        high_uncertainty_sop["classification"]["uncertainty"] = "high"
        high_uncertainty_sop_path = write_json(root / "route-high-uncertainty-sop.json", high_uncertainty_sop)
        high_uncertainty_sop_resolved_path = root / "resolved-high-uncertainty-sop.json"

        sop_change = json.loads(json.dumps(sop_iteration))
        sop_change["classification"].update({"risk": "L1", "delivery_shape": "local_change", "scope": "local", "change_types": ["bugfix"]})
        sop_change_path = write_json(root / "route-sop-change.json", sop_change)
        sop_change_resolved_path = root / "resolved-sop-change.json"

        partial_iteration = json.loads(json.dumps(sop_iteration))
        partial_iteration["capability_report_ref"] = "capability-report.json"
        partial_iteration_path = write_json(root / "route-partial-sop-iteration.json", partial_iteration)
        partial_iteration_resolved_path = root / "resolved-partial-sop-iteration.json"

        debug_route = json.loads(json.dumps(partial_iteration))
        debug_route["classification"].update({"work_intent": "debug", "uncertainty": "high", "pattern_familiarity": "unknown", "change_types": ["bugfix"]})
        debug_route_path = write_json(root / "route-debug-selective.json", debug_route)
        debug_resolved_path = root / "resolved-debug-selective.json"

        direct_route = json.loads(json.dumps(partial_iteration))
        direct_route["classification"].update({
            "risk": "L0",
            "delivery_shape": "doc_only",
            "scope": "local",
            "uncertainty": "low",
            "pattern_familiarity": "known",
            "profiles": ["docs"],
            "change_types": ["docs"],
        })
        direct_route_path = write_json(root / "route-direct.json", direct_route)
        direct_resolved_path = root / "resolved-direct.json"
        resolved_path = root / "resolved-strategy.json"
        initialized_manifest = root / "workflow-initialized.json"
        transition_path = write_json(root / "transition-request.json", {
            "schema_version": 1,
            "workflow_id": "workflow-e2e-migration",
            "transition_id": "tr-ground-001",
            "expected_manifest_revision": 1,
            "stage_id": "ground",
            "producer": {"skill": "context-grounding", "version": "1.0.0"},
            "status": "completed",
            "artifact_changes": [],
            "evidence_refs": [],
            "claim_requests": [],
            "discovered_facts": {},
            "error": None,
        })
        old_transition_path = write_json(root / "transition-request-old-bad.json", {
            "schema_version": 1,
            "workflow_id": "workflow-e2e-migration",
            "from_stage": "ground",
            "to_stage": "data_and_rollback_spec",
            "exit": {
                "status": "completed",
                "produced_artifacts": [],
                "updated_artifacts": [],
                "invalidated_artifacts": [],
                "evidence_refs": [],
                "claim_requests": [],
                "next_recommendation": "specflow",
                "error_code": "",
            },
        })
        stale_transition_path = write_json(root / "transition-request-stale-bad.json", {
            "schema_version": 1,
            "workflow_id": "workflow-e2e-migration",
            "transition_id": "tr-ground-stale",
            "expected_manifest_revision": 0,
            "stage_id": "ground",
            "producer": {"skill": "context-grounding", "version": "1.0.0"},
            "status": "completed",
            "artifact_changes": [],
            "evidence_refs": [],
            "claim_requests": [],
            "discovered_facts": {},
            "error": None,
        })
        capability_missing = capability_report()
        capability_missing["spec_systems"] = [{"id": "fallback", "status": "available", "evidence": ["workflow fallback"]}]
        write_json(root / "capability-missing-openspec.json", capability_missing)
        required_openspec_route = route_decision()
        required_openspec_route["capability_report_ref"] = "capability-missing-openspec.json"
        required_openspec_route["user_constraints"]["required_spec_system"] = "openspec"
        required_openspec_path = write_json(root / "route-required-openspec-bad.json", required_openspec_route)
        forbidden_superpowers_engine_route = route_decision()
        forbidden_superpowers_engine_route["user_constraints"]["required_execution_engine"] = "superpowers"
        forbidden_superpowers_engine_path = write_json(root / "route-superpowers-engine-bad.json", forbidden_superpowers_engine_route)
        capability_without_methods = capability_report()
        capability_without_methods["method_providers"] = [{"id": "superpowers-native", "status": "missing", "version": "unknown", "evidence": []}]
        write_json(root / "capability-without-methods.json", capability_without_methods)
        local_only_route = route_decision()
        local_only_route["capability_report_ref"] = "capability-without-methods.json"
        local_only_route_path = write_json(root / "route-local-only-migration.json", local_only_route)
        local_only_resolved_path = root / "resolved-local-only-migration.json"
        delta_path = write_json(root / "route-facts-delta.json", route_facts_delta())
        rerouted_path = root / "route-decision-v2.json"
        run([sys.executable, str(WORKFLOW / "scripts" / "resolve_strategy.py"), str(route_path), "--output", str(resolved_path)])
        resolved = json.loads(resolved_path.read_text(encoding="utf-8"))
        if resolved["strategy_id"] != "migration-critical" or resolved["process_depth"] != "lifecycle" or resolved["execution_engine"] != "local":
            raise SystemExit("critical migration did not retain local lifecycle execution ownership")
        run([sys.executable, str(WORKFLOW / "scripts" / "resolve_strategy.py"), str(local_only_route_path), "--output", str(local_only_resolved_path)])
        local_only_resolved = json.loads(local_only_resolved_path.read_text(encoding="utf-8"))
        if any(skill.startswith("superpowers:") for skills in local_only_resolved["skill_plan"].values() for skill in skills):
            raise SystemExit("missing method provider did not remove Superpowers native skills")

        run([sys.executable, str(WORKFLOW / "scripts" / "resolve_strategy.py"), str(sop_iteration_path), "--output", str(sop_iteration_resolved_path)])
        sop_iteration_resolved = json.loads(sop_iteration_resolved_path.read_text(encoding="utf-8"))
        expected_iteration_skills = {"change-aware-testing", "delivery-verification"}
        planned_iteration_skills = {skill for skills in sop_iteration_resolved["skill_plan"].values() for skill in skills}
        if (
            sop_iteration_resolved["strategy_id"] != "sop-guided-iteration"
            or sop_iteration_resolved["process_depth"] != "selective"
            or sop_iteration_resolved["execution_engine"] != "local"
            or sop_iteration_resolved["required_skills"]
            or not expected_iteration_skills.issubset(planned_iteration_skills)
        ):
            raise SystemExit("ready project SOP did not select the expected selective native-skill route")

        run([sys.executable, str(WORKFLOW / "scripts" / "resolve_strategy.py"), str(high_uncertainty_sop_path), "--output", str(high_uncertainty_sop_resolved_path)])
        high_uncertainty_resolved = json.loads(high_uncertainty_sop_resolved_path.read_text(encoding="utf-8"))
        if high_uncertainty_resolved["strategy_id"] != "spec-driven-feature":
            raise SystemExit("high uncertainty incorrectly used SOP-guided fast routing")

        run([sys.executable, str(WORKFLOW / "scripts" / "resolve_strategy.py"), str(sop_change_path), "--output", str(sop_change_resolved_path)])
        sop_change_resolved = json.loads(sop_change_resolved_path.read_text(encoding="utf-8"))
        if sop_change_resolved["strategy_id"] != "sop-guided-change" or sop_change_resolved["manifest_policy"] != "none" or sop_change_resolved["required_skills"]:
            raise SystemExit("known L1 project SOP change did not use the direct route")

        run([sys.executable, str(WORKFLOW / "scripts" / "resolve_strategy.py"), str(partial_iteration_path), "--output", str(partial_iteration_resolved_path)])
        partial_iteration_resolved = json.loads(partial_iteration_resolved_path.read_text(encoding="utf-8"))
        if partial_iteration_resolved["strategy_id"] != "spec-driven-feature" or partial_iteration_resolved["execution_engine"] != "local":
            raise SystemExit("partial project SOP incorrectly triggered SOP-guided routing")

        run([sys.executable, str(WORKFLOW / "scripts" / "resolve_strategy.py"), str(debug_route_path), "--output", str(debug_resolved_path)])
        debug_resolved = json.loads(debug_resolved_path.read_text(encoding="utf-8"))
        if debug_resolved["strategy_id"] != "root-cause-debug" or debug_resolved["execution_engine"] != "local" or "superpowers:systematic-debugging" not in debug_resolved["required_skills"]:
            raise SystemExit("debug route did not select only the native systematic-debugging method")

        run([sys.executable, str(WORKFLOW / "scripts" / "resolve_strategy.py"), str(direct_route_path), "--output", str(direct_resolved_path)])
        run([sys.executable, str(WORKFLOW / "scripts" / "init_workflow.py"), str(direct_route_path), "--resolved-strategy", str(direct_resolved_path), "--output", str(root / "direct-manifest-bad.json")], expect_ok=False)
        run([sys.executable, str(WORKFLOW / "scripts" / "resolve_strategy.py"), str(required_openspec_path)], expect_ok=False)
        run([sys.executable, str(WORKFLOW / "scripts" / "resolve_strategy.py"), str(forbidden_superpowers_engine_path)], expect_ok=False)
        run([sys.executable, str(WORKFLOW / "scripts" / "apply_route_facts_delta.py"), str(route_path), str(delta_path), "--output", str(rerouted_path)])
        rerouted = json.loads(rerouted_path.read_text(encoding="utf-8"))
        if rerouted["classification"]["risk"] != "L3" or rerouted["classification"]["scope"] != "cross_service":
            raise SystemExit("route facts delta did not upgrade risk/scope")
        run([sys.executable, str(WORKFLOW / "scripts" / "init_workflow.py"), str(route_path), "--resolved-strategy", str(resolved_path), "--workflow-id", "workflow-e2e-migration", "--output", str(initialized_manifest)])
        run([sys.executable, str(WORKFLOW / "scripts" / "inspect_workflow.py"), str(initialized_manifest), "--validate"])
        run([sys.executable, str(WORKFLOW / "scripts" / "transition_workflow.py"), str(initialized_manifest), str(old_transition_path)], expect_ok=False)
        run([sys.executable, str(WORKFLOW / "scripts" / "transition_workflow.py"), str(initialized_manifest), str(stale_transition_path)], expect_ok=False)
        run([sys.executable, str(WORKFLOW / "scripts" / "transition_workflow.py"), str(initialized_manifest), str(transition_path)])
        run([sys.executable, str(WORKFLOW / "scripts" / "transition_workflow.py"), str(initialized_manifest), str(transition_path)])
        advanced_manifest = json.loads(initialized_manifest.read_text(encoding="utf-8"))
        if advanced_manifest["current_stage"] != "data_and_rollback_spec" or advanced_manifest["routing"]["required_skills"] != ["specflow"]:
            raise SystemExit("stage transition did not activate only the next stage skills")

        wf_ok = write_json(root / "workflow-ok.json", workflow_manifest())
        wf_handoff_ok = workflow_manifest(requested="handoff_done", validated_claim="handoff_done")
        wf_handoff_ok["claims"]["validated"][0]["verifier"] = "fresh-consumer-verifier"
        wf_handoff_ok["claims"]["validated"][0]["attestation"]["claim_type"] = "handoff_done"
        wf_handoff_ok["claims"]["validated"][0]["attestation"]["verifier_id"] = "fresh-consumer-verifier"
        wf_handoff_ok_path = write_json(root / "workflow-handoff-ok.json", wf_handoff_ok)
        wf_old_route_bad = write_json(root / "workflow-old-route-bad.json", {"route": "Medium/Large + harness", **workflow_manifest()})
        wf_spec_only_bad = workflow_manifest(requested="dev_done", validated_claim="dev_done")
        wf_spec_only_bad["artifacts"] = [item for item in wf_spec_only_bad["artifacts"] if item["type"] in {"analysis_pack", "spec", "plan"}]
        wf_spec_only_bad["claims"]["validated"] = []
        wf_spec_only_bad["resume"]["last_validated_artifact_ids"] = ["ap-001", "spec-001", "plan-001"]
        wf_spec_only_bad_path = write_json(root / "workflow-spec-only-bad.json", wf_spec_only_bad)
        wf_self_signed_bad = workflow_manifest()
        wf_self_signed_bad["claims"]["validated"][0]["verifier"] = "agent"
        wf_self_signed_bad_path = write_json(root / "workflow-self-signed-bad.json", wf_self_signed_bad)
        wf_unknown_verifier_bad = workflow_manifest()
        wf_unknown_verifier_bad["claims"]["validated"][0]["verifier"] = "unregistered-verifier"
        wf_unknown_verifier_bad_path = write_json(root / "workflow-unknown-verifier-bad.json", wf_unknown_verifier_bad)
        wf_handoff_wrong_verifier_bad = workflow_manifest(requested="handoff_done", validated_claim="handoff_done")
        wf_handoff_wrong_verifier_bad["claims"]["validated"][0]["verifier"] = "evidence-manifest-validator"
        wf_handoff_wrong_verifier_bad_path = write_json(root / "workflow-handoff-wrong-verifier-bad.json", wf_handoff_wrong_verifier_bad)
        wf_strategy_version_bad = workflow_manifest()
        wf_strategy_version_bad["strategy_version"] = "9.9"
        wf_strategy_version_bad_path = write_json(root / "workflow-strategy-version-bad.json", wf_strategy_version_bad)
        wf_stage_bad = workflow_manifest()
        wf_stage_bad["current_stage"] = "GLOBAL_SPEC_READY"
        wf_stage_bad_path = write_json(root / "workflow-stage-bad.json", wf_stage_bad)
        wf_resume_bad = workflow_manifest()
        wf_resume_bad["resume"]["last_validated_artifact_ids"] = ["missing-artifact"]
        wf_resume_bad_path = write_json(root / "workflow-resume-bad.json", wf_resume_bad)
        wf_profile_mix_bad = workflow_manifest()
        wf_profile_mix_bad["classification"]["profiles"] = ["superpowers"]
        wf_profile_mix_bad_path = write_json(root / "workflow-profile-mix-bad.json", wf_profile_mix_bad)
        wf_superpowers_engine_bad = workflow_manifest()
        wf_superpowers_engine_bad["routing"]["execution_engine"] = "superpowers"
        wf_superpowers_engine_bad_path = write_json(root / "workflow-superpowers-engine-bad.json", wf_superpowers_engine_bad)
        wf_preload_bad = workflow_manifest()
        wf_preload_bad["routing"]["required_skills"].append("superpowers:executing-plans")
        wf_preload_bad_path = write_json(root / "workflow-future-stage-preload-bad.json", wf_preload_bad)
        wf_plan_missing_spec_bad = workflow_manifest()
        for item in wf_plan_missing_spec_bad["artifacts"]:
            if item["type"] == "plan":
                item["depends_on"] = []
        wf_plan_missing_spec_bad_path = write_json(root / "workflow-plan-missing-spec-bad.json", wf_plan_missing_spec_bad)
        wf_design_missing_spec_bad = workflow_manifest()
        for item in wf_design_missing_spec_bad["artifacts"]:
            if item["type"] == "technical_design":
                item["depends_on"] = ["ap-001", "ctx-001"]
        wf_design_missing_spec_bad_path = write_json(root / "workflow-design-missing-spec-bad.json", wf_design_missing_spec_bad)
        wf_embedded_bad = workflow_manifest()
        wf_embedded_bad["selected_strategy"] = "spec-driven-feature"
        wf_embedded_bad["routing"]["strategy_id"] = "spec-driven-feature"
        wf_embedded_bad["strategy_version"] = "2.1"
        wf_embedded_bad["current_stage"] = "plan"
        wf_embedded_bad["routing"]["skill_plan"] = spec_feature_skill_plan()
        wf_embedded_bad["routing"]["execution_policy"] = {"unit": "continuous_batch", "task_risk": "local", "task_exit": "focused_signal", "checkpoint": "batch", "review": "batch_risk", "commit": "batch", "manifest_updates": "stage_only", "max_review_passes": 2}
        wf_embedded_bad["routing"]["required_skills"] = ["superpowers:writing-plans"]
        wf_embedded_bad["resume"]["resume_from_stage"] = "plan"
        wf_embedded_bad["resume"]["last_validated_artifact_ids"] = ["ap-001", "ctx-001", "spec-001", "plan-001"]
        wf_embedded_bad["classification"]["risk"] = "L2"
        wf_embedded_bad["classification"]["scope"] = "module"
        wf_embedded_bad["design_control"] = {
            "policy": "embedded",
            "review": "self",
            "documentation_topology": "compact",
            "triggers": [],
            "embedded_in": "plan-001",
            "section_ref": "",
            "approval": {
                "status": "approved",
                "reviewer": "superpowers:writing-plans",
                "reviewer_kind": "agent",
                "evidence_ids": [],
            },
        }
        wf_embedded_bad["artifacts"] = [item for item in wf_embedded_bad["artifacts"] if item["type"] != "technical_design"]
        for item in wf_embedded_bad["artifacts"]:
            if item["type"] == "plan":
                item["depends_on"] = ["spec-001"]
        wf_embedded_bad_path = write_json(root / "workflow-embedded-missing-section-bad.json", wf_embedded_bad)
        wf_compact_standalone_bad = workflow_manifest()
        wf_compact_standalone_bad["design_control"]["documentation_topology"] = "compact"
        wf_compact_standalone_bad_path = write_json(root / "workflow-compact-standalone-bad.json", wf_compact_standalone_bad)
        wf_split_embedded_bad = workflow_manifest()
        wf_split_embedded_bad["selected_strategy"] = "spec-driven-feature"
        wf_split_embedded_bad["routing"]["strategy_id"] = "spec-driven-feature"
        wf_split_embedded_bad["strategy_version"] = "2.1"
        wf_split_embedded_bad["current_stage"] = "plan"
        wf_split_embedded_bad["routing"]["skill_plan"] = spec_feature_skill_plan()
        wf_split_embedded_bad["routing"]["execution_policy"] = {"unit": "continuous_batch", "task_risk": "local", "task_exit": "focused_signal", "checkpoint": "batch", "review": "batch_risk", "commit": "batch", "manifest_updates": "stage_only", "max_review_passes": 2}
        wf_split_embedded_bad["routing"]["required_skills"] = ["superpowers:writing-plans"]
        wf_split_embedded_bad["resume"]["resume_from_stage"] = "plan"
        wf_split_embedded_bad["resume"]["last_validated_artifact_ids"] = ["ap-001", "ctx-001", "spec-001", "plan-001"]
        wf_split_embedded_bad["classification"]["risk"] = "L2"
        wf_split_embedded_bad["classification"]["scope"] = "module"
        wf_split_embedded_bad["design_control"] = {
            "policy": "embedded",
            "review": "self",
            "documentation_topology": "split_design_workspace",
            "triggers": [],
            "embedded_in": "plan-001",
            "section_ref": "docs/superpowers/plans/2026-06-23-feature.md#technical-design",
            "approval": {
                "status": "approved",
                "reviewer": "superpowers:writing-plans",
                "reviewer_kind": "agent",
                "evidence_ids": [],
            },
        }
        wf_split_embedded_bad["artifacts"] = [item for item in wf_split_embedded_bad["artifacts"] if item["type"] != "technical_design"]
        for item in wf_split_embedded_bad["artifacts"]:
            if item["type"] == "plan":
                item["depends_on"] = ["spec-001"]
        wf_split_embedded_bad_path = write_json(root / "workflow-split-embedded-bad.json", wf_split_embedded_bad)
        wf_stale_bad = workflow_manifest()
        for item in wf_stale_bad["artifacts"]:
            if item["id"] == "spec-001":
                item["status"] = "stale"
        wf_stale_bad_path = write_json(root / "workflow-stale-bad.json", wf_stale_bad)

        review_runtime = workflow_manifest()
        review_runtime["claims"] = {"requested": "none", "validated": []}
        review_manifest = write_json(root / "workflow-review-runtime.json", review_runtime)
        review_request_base = {
            "schema_version": 1,
            "workflow_id": "run-control-plane-e2e",
            "transition_id": "tr-review-001",
            "expected_manifest_revision": 1,
            "stage_id": "delivery_review",
            "producer": {"skill": "agent-orchestration", "version": "1.0.0", "actor_id": "reviewer-1"},
            "status": "completed",
            "artifact_changes": [],
            "evidence_refs": ["review-001"],
            "claim_requests": [],
            "discovered_facts": {},
            "error": None,
        }
        review_missing_path = write_json(root / "review-result-missing-bad.json", review_request_base)
        review_major_approved = json.loads(json.dumps(review_request_base))
        review_major_approved["transition_id"] = "tr-review-major-approved"
        review_major_approved["review_result"] = {"pass_number": 1, "max_severity": "major", "decision": "approved", "reviewer_id": "reviewer-1", "reviewed_producer_ids": ["coding-agent"], "finding_refs": ["finding-major-001"]}
        review_major_approved_path = write_json(root / "review-major-approved-bad.json", review_major_approved)
        review_self_approved = json.loads(json.dumps(review_request_base))
        review_self_approved["transition_id"] = "tr-review-self-approved"
        review_self_approved["producer"]["actor_id"] = "coding-agent"
        review_self_approved["review_result"] = {"pass_number": 1, "max_severity": "none", "decision": "approved", "reviewer_id": "coding-agent", "reviewed_producer_ids": ["coding-agent"], "finding_refs": []}
        review_self_approved_path = write_json(root / "review-self-approved-bad.json", review_self_approved)
        review_empty_findings = json.loads(json.dumps(review_request_base))
        review_empty_findings["transition_id"] = "tr-review-empty-findings"
        review_empty_findings["review_result"] = {"pass_number": 1, "max_severity": "major", "decision": "changes_requested", "reviewer_id": "reviewer-1", "reviewed_producer_ids": ["coding-agent"], "finding_refs": []}
        review_empty_findings_path = write_json(root / "review-empty-findings-bad.json", review_empty_findings)
        review_changes_one = json.loads(json.dumps(review_request_base))
        review_changes_one["transition_id"] = "tr-review-changes-1"
        review_changes_one["review_result"] = {"pass_number": 1, "max_severity": "major", "decision": "changes_requested", "reviewer_id": "reviewer-1", "reviewed_producer_ids": ["coding-agent"], "finding_refs": ["finding-major-001"]}
        review_changes_one_path = write_json(root / "review-changes-1.json", review_changes_one)
        review_changes_two = json.loads(json.dumps(review_request_base))
        review_changes_two["transition_id"] = "tr-review-changes-2"
        review_changes_two["expected_manifest_revision"] = 4
        review_changes_two["review_result"] = {"pass_number": 2, "max_severity": "major", "decision": "changes_requested", "reviewer_id": "reviewer-1", "reviewed_producer_ids": ["coding-agent"], "finding_refs": ["finding-major-002"]}
        review_changes_two_path = write_json(root / "review-changes-2.json", review_changes_two)
        review_human_manifest = write_json(root / "workflow-review-human.json", workflow_manifest())
        review_human = json.loads(json.dumps(review_request_base))
        review_human["transition_id"] = "tr-review-human-required"
        review_human["review_result"] = {"pass_number": 1, "max_severity": "critical", "decision": "human_required", "reviewer_id": "reviewer-1", "reviewed_producer_ids": ["coding-agent"], "finding_refs": ["finding-human-001"]}
        review_human_path = write_json(root / "review-human-required.json", review_human)
        repair_request = json.loads(json.dumps(review_request_base))
        repair_request.update({
            "transition_id": "tr-review-repair-1",
            "expected_manifest_revision": 2,
            "stage_id": "remaining_slice_execution",
        })
        repair_request["producer"] = {"skill": "change-aware-testing", "version": "1.0.0", "actor_id": "coding-agent"}
        repair_request["review_result"] = None
        repair_request["evidence_refs"] = ["repair-001"]
        repaired_implementation = next(item for item in review_runtime["artifacts"] if item["id"] == "impl-001")
        repaired_implementation = {**repaired_implementation, "version": 2, "digest": "sha256:impl-repair-001"}
        repair_request["artifact_changes"] = [{"change_type": "content_changed", "artifact": repaired_implementation}]
        repair_request_path = write_json(root / "review-repair-1.json", repair_request)
        empty_repair_request = json.loads(json.dumps(repair_request))
        empty_repair_request["transition_id"] = "tr-review-empty-repair"
        empty_repair_request["artifact_changes"] = []
        empty_repair_request_path = write_json(root / "review-empty-repair-bad.json", empty_repair_request)
        repair_human_required = json.loads(json.dumps(empty_repair_request))
        repair_human_required["transition_id"] = "tr-review-repair-human-required"
        repair_human_required["status"] = "human_required"
        repair_human_required["error"] = {"code": "EXTERNAL_DECISION_REQUIRED", "message": "repair needs a human decision"}
        repair_human_required_path = write_json(root / "review-repair-human-required.json", repair_human_required)
        repaired_system_gate = json.loads(json.dumps(review_request_base))
        repaired_system_gate.update({
            "transition_id": "tr-review-system-1",
            "expected_manifest_revision": 3,
            "stage_id": "system_verification",
        })
        repaired_system_gate["producer"] = {"skill": "delivery-verification", "version": "1.0.0"}
        repaired_system_gate["review_result"] = None
        repaired_system_gate["evidence_refs"] = ["system-after-repair-001"]
        repaired_system_gate_path = write_json(root / "review-system-1.json", repaired_system_gate)

        system_gate_manifest = workflow_manifest()
        system_gate_manifest["current_stage"] = "system_verification"
        system_gate_manifest["resume"]["resume_from_stage"] = "system_verification"
        system_gate_manifest["routing"]["required_skills"] = ["change-aware-testing", "delivery-verification"]
        system_gate_manifest_path = write_json(root / "workflow-system-gate.json", system_gate_manifest)
        system_gate_empty = json.loads(json.dumps(review_request_base))
        system_gate_empty.update({"transition_id": "tr-system-empty", "stage_id": "system_verification"})
        system_gate_empty["producer"] = {"skill": "delivery-verification", "version": "1.0.0"}
        system_gate_empty["evidence_refs"] = []
        system_gate_empty_path = write_json(root / "system-gate-empty-bad.json", system_gate_empty)

        migration_negative_manifest = workflow_manifest()
        migration_negative_manifest["selected_strategy"] = "migration-critical"
        migration_negative_manifest["current_stage"] = "negative_tests"
        migration_negative_manifest_path = write_json(root / "workflow-migration-negative-gate.json", migration_negative_manifest)
        migration_negative_empty = json.loads(json.dumps(system_gate_empty))
        migration_negative_empty.update({"transition_id": "tr-migration-negative-empty", "stage_id": "negative_tests"})
        migration_negative_empty["producer"] = {"skill": "change-aware-testing", "version": "1.0.0"}
        migration_negative_empty_path = write_json(root / "migration-negative-empty-bad.json", migration_negative_empty)

        l2_review_manifest = workflow_manifest()
        l2_review_manifest["selected_strategy"] = "spec-driven-feature"
        l2_review_manifest["current_stage"] = "review"
        l2_review_manifest_path = write_json(root / "workflow-l2-review-gate.json", l2_review_manifest)
        l2_review_empty = json.loads(json.dumps(system_gate_empty))
        l2_review_empty.update({"transition_id": "tr-l2-review-empty", "stage_id": "review"})
        l2_review_empty["producer"] = {"skill": "local-executor", "version": "1.0.0", "actor_id": "coding-agent"}
        l2_review_empty_path = write_json(root / "l2-review-empty-bad.json", l2_review_empty)

        old_unsigned = workflow_manifest()
        old_unsigned["schema_version"] = 5
        old_unsigned["strategy_version"] = "1.3"
        old_unsigned["claims"] = {"requested": "none", "validated": []}
        old_unsigned.pop("review_control")
        old_unsigned["routing"].pop("execution_policy")
        old_unsigned["routing"]["skill_plan"]["slice_execution"] = ["superpowers:executing-plans", "change-aware-testing"]
        old_unsigned["routing"]["skill_plan"]["delivery_review"] = ["superpowers:requesting-code-review"]
        old_unsigned["routing"]["required_skills"] = ["superpowers:requesting-code-review"]
        old_unsigned_path = write_json(root / "workflow-v1-unsigned.json", old_unsigned)
        migrated_manifest_path = root / "workflow-v2-migrated.json"
        old_signed = json.loads(json.dumps(old_unsigned))
        old_signed["claims"] = workflow_manifest()["claims"]
        old_signed_path = write_json(root / "workflow-v1-signed-bad.json", old_signed)
        old_review_blocked = json.loads(json.dumps(old_unsigned))
        old_review_blocked["workflow_state"] = "blocked"
        old_review_blocked["current_stage"] = "delivery_review"
        old_review_blocked["resume"]["resume_from_stage"] = "delivery_review"
        old_review_blocked["resume"]["blocked_reason"] = "REVIEW_LIMIT_REACHED"
        old_review_blocked["review_control"] = {"stage_id": "delivery_review", "passes_completed": 2, "last_severity": "major", "decision": "human_required"}
        old_review_blocked_path = write_json(root / "workflow-v5-review-limit-blocked.json", old_review_blocked)
        recovered_review_path = root / "workflow-v6-review-recovered.json"
        old_external_blocked = json.loads(json.dumps(old_unsigned))
        old_external_blocked["workflow_state"] = "blocked"
        old_external_blocked["resume"]["blocked_reason"] = "CAPABILITY_MISSING"
        old_external_blocked_path = write_json(root / "workflow-v5-external-blocked.json", old_external_blocked)
        preserved_external_path = root / "workflow-v6-external-blocked.json"

        manifest_validator = WORKFLOW / "scripts" / "validate_workflow_manifest.py"
        graph_validator = WORKFLOW / "scripts" / "validate_artifact_graph.py"
        run([sys.executable, str(manifest_validator), str(wf_ok)])
        run([sys.executable, str(graph_validator), str(wf_ok)])
        run([sys.executable, str(manifest_validator), str(wf_handoff_ok_path)])
        run([sys.executable, str(graph_validator), str(wf_handoff_ok_path)])
        run([sys.executable, str(manifest_validator), str(wf_old_route_bad)], expect_ok=False)
        run([sys.executable, str(manifest_validator), str(wf_spec_only_bad_path)], expect_ok=False)
        run([sys.executable, str(manifest_validator), str(wf_self_signed_bad_path)], expect_ok=False)
        run([sys.executable, str(manifest_validator), str(wf_unknown_verifier_bad_path)], expect_ok=False)
        run([sys.executable, str(manifest_validator), str(wf_handoff_wrong_verifier_bad_path)], expect_ok=False)
        run([sys.executable, str(manifest_validator), str(wf_strategy_version_bad_path)], expect_ok=False)
        run([sys.executable, str(manifest_validator), str(wf_stage_bad_path)], expect_ok=False)
        run([sys.executable, str(manifest_validator), str(wf_resume_bad_path)], expect_ok=False)
        run([sys.executable, str(manifest_validator), str(wf_profile_mix_bad_path)], expect_ok=False)
        run([sys.executable, str(manifest_validator), str(wf_superpowers_engine_bad_path)], expect_ok=False)
        run([sys.executable, str(manifest_validator), str(wf_preload_bad_path)], expect_ok=False)
        run([sys.executable, str(graph_validator), str(wf_plan_missing_spec_bad_path)], expect_ok=False)
        run([sys.executable, str(graph_validator), str(wf_design_missing_spec_bad_path)], expect_ok=False)
        run([sys.executable, str(manifest_validator), str(wf_embedded_bad_path)], expect_ok=False)
        run([sys.executable, str(manifest_validator), str(wf_compact_standalone_bad_path)], expect_ok=False)
        run([sys.executable, str(manifest_validator), str(wf_split_embedded_bad_path)], expect_ok=False)
        run([sys.executable, str(graph_validator), str(wf_stale_bad_path)], expect_ok=False)
        transition_script = WORKFLOW / "scripts" / "transition_workflow.py"
        run([sys.executable, str(transition_script), str(review_manifest), str(review_missing_path)], expect_ok=False)
        run([sys.executable, str(transition_script), str(review_manifest), str(review_major_approved_path)], expect_ok=False)
        run([sys.executable, str(transition_script), str(review_manifest), str(review_self_approved_path)], expect_ok=False)
        run([sys.executable, str(transition_script), str(review_manifest), str(review_empty_findings_path)], expect_ok=False)
        run([sys.executable, str(transition_script), str(system_gate_manifest_path), str(system_gate_empty_path)], expect_ok=False)
        run([sys.executable, str(transition_script), str(migration_negative_manifest_path), str(migration_negative_empty_path)], expect_ok=False)
        run([sys.executable, str(transition_script), str(l2_review_manifest_path), str(l2_review_empty_path)], expect_ok=False)
        run([sys.executable, str(transition_script), str(review_manifest), str(review_changes_one_path)])
        first_repair = json.loads(review_manifest.read_text(encoding="utf-8"))
        if first_repair["workflow_state"] != "active" or first_repair["current_stage"] != "remaining_slice_execution":
            raise SystemExit("first review findings did not return workflow to its repair stage")
        repair_impasse_manifest = write_json(root / "workflow-repair-human-required.json", first_repair)
        run([sys.executable, str(transition_script), str(repair_impasse_manifest), str(repair_human_required_path)])
        repair_impasse = json.loads(repair_impasse_manifest.read_text(encoding="utf-8"))
        if repair_impasse["workflow_state"] != "blocked" or repair_impasse["resume"]["blocked_reason"] != "EXTERNAL_DECISION_REQUIRED":
            raise SystemExit("repair-stage human impasse was rejected instead of becoming a true blocker")
        run([sys.executable, str(transition_script), str(review_manifest), str(empty_repair_request_path)], expect_ok=False)
        run([sys.executable, str(transition_script), str(review_manifest), str(repair_request_path)])
        run([sys.executable, str(transition_script), str(review_manifest), str(repaired_system_gate_path)])
        second_review_result = run([sys.executable, str(transition_script), str(review_manifest), str(review_changes_two_path)])
        if json.loads(second_review_result.stdout)["status"] != "repair_required":
            raise SystemExit("review changes did not emit repair_required")
        duplicate_review_result = run([sys.executable, str(transition_script), str(review_manifest), str(review_changes_two_path)])
        duplicate_payload = json.loads(duplicate_review_result.stdout)
        if duplicate_payload["status"] != "repair_required" or duplicate_payload["current_stage"] != "remaining_slice_execution":
            raise SystemExit("duplicate repair transition did not return its original result")
        review_repair_cycle = json.loads(review_manifest.read_text(encoding="utf-8"))
        if review_repair_cycle["workflow_state"] != "active" or review_repair_cycle["current_stage"] != "remaining_slice_execution":
            raise SystemExit("review pass limit blocked Goal Mode instead of returning to repair")
        if review_repair_cycle["resume"]["blocked_reason"] or review_repair_cycle["review_control"]["passes_completed"] != 0:
            raise SystemExit("review repair cycle was not reset after the bounded second pass")
        if review_repair_cycle["review_control"]["finding_refs"] != ["finding-major-002"]:
            raise SystemExit("latest review findings were not preserved for the repair cycle")
        run([sys.executable, str(transition_script), str(review_human_manifest), str(review_human_path)])
        review_human_blocked = json.loads(review_human_manifest.read_text(encoding="utf-8"))
        if review_human_blocked["workflow_state"] != "blocked" or review_human_blocked["resume"]["blocked_reason"] != "REVIEW_HUMAN_REQUIRED":
            raise SystemExit("human-required review did not retain the true blocking boundary")
        migrate_script = WORKFLOW / "scripts" / "migrate_workflow_manifest_v5.py"
        run([sys.executable, str(migrate_script), str(old_unsigned_path), "--output", str(migrated_manifest_path)])
        migrated_manifest = json.loads(migrated_manifest_path.read_text(encoding="utf-8"))
        migrated_methods = {skill for skills in migrated_manifest["routing"]["skill_plan"].values() for skill in skills}
        if migrated_manifest["strategy_version"] != "2.2" or "superpowers:executing-plans" in migrated_methods:
            raise SystemExit("manifest migration retained legacy execution ceremony")
        if migrated_manifest["schema_version"] != 6:
            raise SystemExit("v5 manifest migration did not upgrade schema_version to 6")
        recovered_review = run([sys.executable, str(migrate_script), str(old_review_blocked_path), "--output", str(recovered_review_path)])
        recovered_manifest = json.loads(recovered_review_path.read_text(encoding="utf-8"))
        if recovered_manifest["workflow_state"] != "active" or recovered_manifest["current_stage"] != "delivery_review" or recovered_manifest["resume"]["blocked_reason"]:
            raise SystemExit("legacy REVIEW_LIMIT_REACHED workflow was not reactivated at its review stage")
        if "regenerate findings" not in recovered_review.stdout:
            raise SystemExit("legacy review recovery did not disclose missing historical findings")
        run([sys.executable, str(migrate_script), str(old_external_blocked_path), "--output", str(preserved_external_path)])
        preserved_external = json.loads(preserved_external_path.read_text(encoding="utf-8"))
        if preserved_external["workflow_state"] != "blocked" or preserved_external["resume"]["blocked_reason"] != "CAPABILITY_MISSING":
            raise SystemExit("v5 migration cleared a genuine external blocker")
        run([sys.executable, str(migrate_script), str(old_signed_path), "--output", str(root / "signed-migration-bad.json")], expect_ok=False)
        signed_digest = sha256(old_signed_path)
        run([sys.executable, str(migrate_script), str(old_signed_path), "--output", str(old_signed_path)], expect_ok=False)
        if sha256(old_signed_path) != signed_digest:
            raise SystemExit("failed in-place migration modified the source manifest")

        evidence_validator = DELIVERY / "scripts" / "validate_evidence_manifest.py"
        evidence_root_args = ["--repo-root", str(root)]
        run([sys.executable, str(evidence_validator), str(write_json(root / "evidence-integration-ok.json", evidence_manifest("integration_done", "integration"))), *evidence_root_args])
        run([sys.executable, str(evidence_validator), str(write_json(root / "evidence-broken-bad.json", evidence_manifest("dev_done", "manual", "broken"))), *evidence_root_args], expect_ok=False)
        run([sys.executable, str(evidence_validator), str(write_json(root / "evidence-integration-mock-bad.json", evidence_manifest("integration_done", "mock"))), *evidence_root_args], expect_ok=False)
        run([sys.executable, str(evidence_validator), str(write_json(root / "evidence-handoff-integration-bad.json", evidence_manifest("handoff_done", "integration"))), *evidence_root_args], expect_ok=False)
        run([sys.executable, str(evidence_validator), str(write_json(root / "evidence-handoff-ok.json", evidence_manifest("handoff_done", "fresh_consumer"))), *evidence_root_args])
        false_claim = evidence_manifest("handoff_done", "system", "fail")
        false_claim["validators"].append({
            "id": "V-002",
            "type": "fresh_consumer",
            "result": "pass",
            "command_or_method": "unrelated fresh consumer probe",
            "proves": "a different path works",
            "gaps": "does not cover AC-1",
        })
        run([sys.executable, str(evidence_validator), str(write_json(root / "evidence-unrelated-pass-false-claim-bad.json", false_claim)), *evidence_root_args], expect_ok=False)
        incomplete_acceptance = evidence_manifest("integration_done", "integration")
        incomplete_acceptance["required_acceptance_ids"] = ["AC-1", "AC-2"]
        run([sys.executable, str(evidence_validator), str(write_json(root / "evidence-incomplete-acceptance-bad.json", incomplete_acceptance)), *evidence_root_args], expect_ok=False)
        full_contract_path = write_json(root / "acceptance-contract-full.json", {
            "schema_version": 1,
            "spec_path": "approved-evidence-spec.md",
            "spec_digest": evidence_spec_digest,
            "required_acceptance_ids": ["AC-1", "AC-2"],
        })
        jointly_reduced = evidence_manifest("integration_done", "integration")
        jointly_reduced["acceptance_contract_path"] = "acceptance-contract-full.json"
        jointly_reduced["acceptance_contract_digest"] = "sha256:" + sha256(full_contract_path)
        run([sys.executable, str(evidence_validator), str(write_json(root / "evidence-jointly-reduced-acceptance-bad.json", jointly_reduced)), *evidence_root_args], expect_ok=False)

        close_without_claim = workflow_manifest()
        close_without_claim["claims"]["validated"] = []
        close_without_claim_path = write_json(root / "workflow-close-without-claim-bad.json", close_without_claim)
        close_review = json.loads(json.dumps(review_request_base))
        close_review["transition_id"] = "tr-close-without-claim"
        close_review["review_result"] = {"pass_number": 1, "max_severity": "none", "decision": "approved", "reviewer_id": "reviewer-1", "reviewed_producer_ids": ["coding-agent"], "finding_refs": []}
        close_review_path = write_json(root / "close-without-claim-request.json", close_review)
        run([sys.executable, str(transition_script), str(close_without_claim_path), str(close_review_path)], expect_ok=False)

        for strategy_id, version, final_stage in [
            ("migration-critical", "2.1", "close"),
            ("spec-driven-feature", "2.1", "close"),
        ]:
            managed_no_claim = workflow_manifest()
            managed_no_claim["selected_strategy"] = strategy_id
            managed_no_claim["strategy_version"] = version
            managed_no_claim["current_stage"] = final_stage
            managed_no_claim["claims"] = {"requested": "none", "validated": []}
            managed_no_claim_path = write_json(root / f"{strategy_id}-close-without-claim-bad.json", managed_no_claim)
            managed_close_request = json.loads(json.dumps(close_review))
            managed_close_request["transition_id"] = f"tr-{strategy_id}-close-without-claim"
            managed_close_request["stage_id"] = final_stage
            managed_close_request["producer"] = {"skill": "local-executor", "version": "1.0.0"}
            managed_close_request["review_result"] = None
            managed_close_path = write_json(root / f"{strategy_id}-close-without-claim-request.json", managed_close_request)
            run([sys.executable, str(transition_script), str(managed_no_claim_path), str(managed_close_path)], expect_ok=False)

        claim_repo = root / "claim-repo"
        claim_repo.mkdir()
        close_runtime = workflow_manifest()
        close_runtime["claims"]["validated"] = []
        close_runtime["current_stage"] = "system_verification"
        close_runtime["workflow_state"] = "active"
        close_runtime["routing"]["required_skills"] = ["change-aware-testing", "delivery-verification"]
        close_runtime["resume"]["checkpoint_id"] = "cp-system-verification"
        close_runtime["resume"]["resume_from_stage"] = "system_verification"
        approved_spec_path = write_text(claim_repo / "docs/superpowers/specs/2026-06-23-feature-spec.md", "# Approved Spec\n")
        approved_spec_digest = "sha256:" + sha256(approved_spec_path)
        for artifact in close_runtime["artifacts"]:
            if artifact["type"] == "spec":
                artifact["digest"] = approved_spec_digest
        close_runtime_path = write_json(claim_repo / ".agent/runtime/workflow-close-runtime.json", close_runtime)
        close_evidence = evidence_manifest("integration_done", "integration")
        close_evidence["spec_digest"] = approved_spec_digest
        close_contract_path = write_json(claim_repo / ".agent/runtime/acceptance-contract.json", {
            "schema_version": 1,
            "spec_path": "docs/superpowers/specs/2026-06-23-feature-spec.md",
            "spec_digest": approved_spec_digest,
            "required_acceptance_ids": ["AC-1", "AC-2"],
        })
        close_evidence["acceptance_contract_path"] = ".agent/runtime/acceptance-contract.json"
        close_evidence["acceptance_contract_digest"] = "sha256:" + sha256(close_contract_path)
        close_evidence["required_acceptance_ids"] = ["AC-1", "AC-2"]
        close_evidence["acceptance_coverage"].append({"acceptance_id": "AC-2", "validator_ids": ["V-001"]})
        for artifact in close_runtime["artifacts"]:
            if artifact["type"] == "acceptance_contract":
                artifact["path"] = ".agent/runtime/acceptance-contract.json"
                artifact["digest"] = close_evidence["acceptance_contract_digest"]
                artifact["covers_acceptance"] = ["AC-1", "AC-2"]
        write_json(close_runtime_path, close_runtime)
        close_evidence_path = write_json(claim_repo / ".agent/runtime/evidence-close-integration.json", close_evidence)
        disallowed_type_evidence = json.loads(json.dumps(close_evidence))
        disallowed_type_evidence["validators"][0]["type"] = "real_external"
        disallowed_type_evidence_path = write_json(claim_repo / ".agent/runtime/evidence-disallowed-type.json", disallowed_type_evidence)
        mixed_evidence = json.loads(json.dumps(close_evidence))
        mixed_evidence["validators"].append({
            "id": "V-UNIT",
            "type": "unit",
            "result": "pass",
            "command_or_method": "unit-only evidence",
            "proves": "focused behavior",
            "gaps": "does not prove integration",
        })
        mixed_evidence["acceptance_coverage"][0]["validator_ids"].append("V-UNIT")
        mixed_evidence_path = write_json(claim_repo / ".agent/runtime/evidence-mixed-types.json", mixed_evidence)
        reduced_contract_path = write_json(claim_repo / ".agent/runtime/acceptance-contract-reduced.json", {
            "schema_version": 1,
            "spec_path": "docs/superpowers/specs/2026-06-23-feature-spec.md",
            "spec_digest": approved_spec_digest,
            "required_acceptance_ids": ["AC-1"],
        })
        reduced_evidence = json.loads(json.dumps(close_evidence))
        reduced_evidence["acceptance_contract_path"] = ".agent/runtime/acceptance-contract-reduced.json"
        reduced_evidence["acceptance_contract_digest"] = "sha256:" + sha256(reduced_contract_path)
        reduced_evidence["required_acceptance_ids"] = ["AC-1"]
        reduced_evidence["acceptance_coverage"] = [reduced_evidence["acceptance_coverage"][0]]
        reduced_evidence_path = write_json(claim_repo / ".agent/runtime/evidence-reduced-contract.json", reduced_evidence)
        run(["git", "init", "-q"], cwd=claim_repo)
        run(["git", "add", "--all"], cwd=claim_repo)
        run(["git", "-c", "user.name=Workflow E2E", "-c", "user.email=e2e@example.invalid", "commit", "-q", "-m", "claim fixture"], cwd=claim_repo)
        attestation_path = claim_repo / ".agent/runtime/claim-attestation.json"
        issue_attestation = DELIVERY / "scripts" / "issue_claim_attestation.py"
        run([
            sys.executable,
            str(issue_attestation),
            str(reduced_evidence_path),
            str(close_runtime_path),
            "--verifier",
            "evidence-manifest-validator",
            "--repo-root",
            str(claim_repo),
            "--output",
            str(root / "reduced-contract-attestation-bad.json"),
        ], expect_ok=False)
        run([sys.executable, str(issue_attestation), str(close_evidence_path), str(close_runtime_path), "--verifier", "evidence-manifest-validator", "--repo-root", str(claim_repo), "--output", str(attestation_path)])
        system_close_request = {
            "schema_version": 1,
            "workflow_id": "run-control-plane-e2e",
            "transition_id": "tr-close-system",
            "expected_manifest_revision": 1,
            "stage_id": "system_verification",
            "producer": {"skill": "delivery-verification", "version": "1.0.0", "actor_id": "verifier-1"},
            "status": "completed",
            "artifact_changes": [],
            "evidence_refs": ["V-001"],
            "claim_requests": ["integration_done"],
            "claim_attestations": [json.loads(attestation_path.read_text(encoding="utf-8"))],
            "discovered_facts": {},
            "error": None,
        }
        dirty_product_path = write_text(claim_repo / "src/uncommitted-change.py", "changed = True\n")
        dirty_product_request_path = write_json(root / "dirty-product-attestation-request.json", system_close_request)
        run([sys.executable, str(transition_script), str(close_runtime_path), str(dirty_product_request_path), "--repo-root", str(claim_repo)], expect_ok=False)
        dirty_product_path.unlink()
        disallowed_type_request = json.loads(json.dumps(system_close_request))
        disallowed_type_request["transition_id"] = "tr-disallowed-evidence-type"
        disallowed_signed = disallowed_type_request["claim_attestations"][0]
        disallowed_signed["attestation"]["evidence_manifest_path"] = ".agent/runtime/evidence-disallowed-type.json"
        disallowed_signed["attestation"]["evidence_manifest_digest"] = "sha256:" + sha256(disallowed_type_evidence_path)
        disallowed_type_path = write_json(root / "disallowed-evidence-type-request.json", disallowed_type_request)
        run([sys.executable, str(transition_script), str(close_runtime_path), str(disallowed_type_path), "--repo-root", str(claim_repo)], expect_ok=False)
        insufficient_type_request = json.loads(json.dumps(system_close_request))
        insufficient_type_request["transition_id"] = "tr-allowed-but-insufficient-signed-type"
        insufficient_signed = insufficient_type_request["claim_attestations"][0]
        insufficient_signed["evidence_ids"] = ["V-UNIT"]
        insufficient_signed["attestation"]["evidence_manifest_path"] = ".agent/runtime/evidence-mixed-types.json"
        insufficient_signed["attestation"]["evidence_manifest_digest"] = "sha256:" + sha256(mixed_evidence_path)
        insufficient_type_path = write_json(root / "allowed-but-insufficient-signed-type-request.json", insufficient_type_request)
        run([sys.executable, str(transition_script), str(close_runtime_path), str(insufficient_type_path), "--repo-root", str(claim_repo)], expect_ok=False)
        write_text(claim_repo / "head-change.txt", "new committed state\n")
        run(["git", "add", "--all"], cwd=claim_repo)
        run(["git", "-c", "user.name=Workflow E2E", "-c", "user.email=e2e@example.invalid", "commit", "-q", "-m", "advance head"], cwd=claim_repo)
        stale_head_request_path = write_json(root / "stale-head-attestation-request.json", system_close_request)
        run([sys.executable, str(transition_script), str(close_runtime_path), str(stale_head_request_path), "--repo-root", str(claim_repo)], expect_ok=False)
        run([sys.executable, str(issue_attestation), str(close_evidence_path), str(close_runtime_path), "--verifier", "evidence-manifest-validator", "--repo-root", str(claim_repo), "--output", str(attestation_path)])
        system_close_request["claim_attestations"] = [json.loads(attestation_path.read_text(encoding="utf-8"))]
        system_close_request_path = write_json(claim_repo / ".agent/runtime/close-system-request.json", system_close_request)
        for label, mutate in {
            "commit": lambda value: value["attestation"].__setitem__("commit_sha", "not-a-commit"),
            "registry": lambda value: value["attestation"].__setitem__("registry_digest", "sha256:fake"),
            "evidence": lambda value: value["attestation"].__setitem__("evidence_manifest_digest", "sha256:fake"),
            "evidence-id": lambda value: value.__setitem__("evidence_ids", ["V-NOT-FOUND"]),
        }.items():
            forged_request = json.loads(json.dumps(system_close_request))
            forged_request["transition_id"] = "tr-forged-" + label
            mutate(forged_request["claim_attestations"][0])
            forged_path = write_json(claim_repo / ".agent/runtime" / ("forged-" + label + "-request.json"), forged_request)
            run([sys.executable, str(transition_script), str(close_runtime_path), str(forged_path), "--repo-root", str(claim_repo)], expect_ok=False)
        if json.loads(close_runtime_path.read_text(encoding="utf-8"))["manifest_revision"] != 1:
            raise SystemExit("rejected forged attestation mutated workflow manifest")
        run([sys.executable, str(transition_script), str(close_runtime_path), str(system_close_request_path), "--repo-root", str(claim_repo)])
        final_close_review = json.loads(json.dumps(close_review))
        final_close_review["transition_id"] = "tr-close-final-review"
        final_close_review["expected_manifest_revision"] = 2
        final_close_review_path = write_json(claim_repo / ".agent/runtime/close-final-review-request.json", final_close_review)
        run([sys.executable, str(transition_script), str(close_runtime_path), str(final_close_review_path), "--repo-root", str(claim_repo)])
        closed_runtime = json.loads(close_runtime_path.read_text(encoding="utf-8"))
        if closed_runtime["workflow_state"] != "closed" or closed_runtime["current_stage"] != "delivery_review":
            raise SystemExit("validated L3 workflow did not close at its final delivery review")

        ctx_ok = write_json(root / "context-ok.json", context_manifest(repo, source_file))
        ctx_broad = context_manifest(repo, source_file)
        ctx_broad["allowed_paths"] = ["src/**"]
        ctx_broad["context_files"][0]["path"] = "src/orders/implementation.ts"
        ctx_broad_path = write_json(root / "context-broad-bad.json", ctx_broad)
        ctx_audit = context_manifest(repo, source_file)
        ctx_audit["runtime_audit"]["read_events"].append({"path": "src/other.ts", "within_allowed_paths": False, "pack_updated_before_use": False})
        ctx_audit_path = write_json(root / "context-audit-bad.json", ctx_audit)
        run([sys.executable, str(CONTEXT / "scripts" / "validate_context_pack_static.py"), str(ctx_ok)])
        run([sys.executable, str(CONTEXT / "scripts" / "validate_context_freshness.py"), str(ctx_ok), "--repo-root", str(repo), "--allow-working-tree"])
        run([sys.executable, str(CONTEXT / "scripts" / "validate_context_runtime_audit.py"), str(ctx_ok)])
        run([sys.executable, str(CONTEXT / "scripts" / "run_context_sufficiency_eval.py"), str(ctx_ok), "--spec", str(spec_file)])
        run([sys.executable, str(CONTEXT / "scripts" / "validate_context_pack_static.py"), str(ctx_broad_path)], expect_ok=False)
        run([sys.executable, str(CONTEXT / "scripts" / "validate_context_runtime_audit.py"), str(ctx_audit_path)], expect_ok=False)

        learning_ok = write_json(root / "learning-ok.json", {
            "id": "good-pattern",
            "source": "workflow-e2e",
            "problem": "Repeated context drift",
            "pattern": "Use context manifest runtime audit",
            "promotion_target": "project_skill",
            "status": "candidate",
        })
        learning_bad = write_json(root / "learning-bad.json", {
            "id": "../../ESCAPE",
            "source": "workflow-e2e",
            "problem": "Path traversal",
            "pattern": "Unsafe id",
            "promotion_target": "project_skill",
            "status": "candidate",
        })
        run([sys.executable, str(KNOWLEDGE / "scripts" / "validate_learning_candidate.py"), str(learning_ok)])
        run([sys.executable, str(KNOWLEDGE / "scripts" / "validate_learning_candidate.py"), str(learning_bad)], expect_ok=False)

        run([sys.executable, str(WORKFLOW / "scripts" / "validate_strategy_registry.py")])
        forbidden_registry = root / "strategies-forbidden-method"
        shutil.copytree(WORKFLOW / "references" / "strategies", forbidden_registry)
        forbidden_complex_path = forbidden_registry / "complex-real-slice.json"
        forbidden_complex = json.loads(forbidden_complex_path.read_text(encoding="utf-8"))
        forbidden_complex["stage_skills"]["slice_execution"].append("superpowers:executing-plans")
        write_json(forbidden_complex_path, forbidden_complex)
        run([sys.executable, str(WORKFLOW / "scripts" / "validate_strategy_registry.py"), "--root", str(forbidden_registry)], expect_ok=False)
        unbounded_registry = root / "strategies-unbounded-review"
        shutil.copytree(WORKFLOW / "references" / "strategies", unbounded_registry)
        unbounded_complex_path = unbounded_registry / "complex-real-slice.json"
        unbounded_complex = json.loads(unbounded_complex_path.read_text(encoding="utf-8"))
        unbounded_complex["execution_policy"]["max_review_passes"] = 3
        write_json(unbounded_complex_path, unbounded_complex)
        run([sys.executable, str(WORKFLOW / "scripts" / "validate_strategy_registry.py"), "--root", str(unbounded_registry)], expect_ok=False)
        ungated_registry = root / "strategies-ungated-review"
        shutil.copytree(WORKFLOW / "references" / "strategies", ungated_registry)
        ungated_feature_path = ungated_registry / "spec-driven-feature.json"
        ungated_feature = json.loads(ungated_feature_path.read_text(encoding="utf-8"))
        ungated_feature["stage_gates"].pop("review")
        write_json(ungated_feature_path, ungated_feature)
        run([sys.executable, str(WORKFLOW / "scripts" / "validate_strategy_registry.py"), "--root", str(ungated_registry)], expect_ok=False)
        invalid_repair_registry = root / "strategies-invalid-repair-stage"
        shutil.copytree(WORKFLOW / "references" / "strategies", invalid_repair_registry)
        invalid_repair_path = invalid_repair_registry / "spec-driven-feature.json"
        invalid_repair = json.loads(invalid_repair_path.read_text(encoding="utf-8"))
        invalid_repair["stage_gates"]["review"]["repair_stage"] = "close"
        write_json(invalid_repair_path, invalid_repair)
        run([sys.executable, str(WORKFLOW / "scripts" / "validate_strategy_registry.py"), "--root", str(invalid_repair_registry)], expect_ok=False)
        missing_close_claim_registry = root / "strategies-missing-close-claim"
        shutil.copytree(WORKFLOW / "references" / "strategies", missing_close_claim_registry)
        missing_close_claim_path = missing_close_claim_registry / "migration-critical.json"
        missing_close_claim = json.loads(missing_close_claim_path.read_text(encoding="utf-8"))
        missing_close_claim.pop("minimum_close_claim")
        write_json(missing_close_claim_path, missing_close_claim)
        run([sys.executable, str(WORKFLOW / "scripts" / "validate_strategy_registry.py"), "--root", str(missing_close_claim_registry)], expect_ok=False)
        excessive_close_claim_registry = root / "strategies-excessive-close-claim"
        shutil.copytree(WORKFLOW / "references" / "strategies", excessive_close_claim_registry)
        excessive_close_claim_path = excessive_close_claim_registry / "focused-change.json"
        excessive_close_claim = json.loads(excessive_close_claim_path.read_text(encoding="utf-8"))
        excessive_close_claim["minimum_close_claim"] = "integration_done"
        write_json(excessive_close_claim_path, excessive_close_claim)
        run([sys.executable, str(WORKFLOW / "scripts" / "validate_strategy_registry.py"), "--root", str(excessive_close_claim_registry)], expect_ok=False)
        run([sys.executable, str(HANDOFF_FRESH_CONSUMER)])

    print("Workflow E2E eval passed")
    print("- project harness init + validate: pass")
    print("- route decision -> capability report -> strategy resolver -> init/transition: pass")
    print("- project SOP maturity detection + direct/selective/lifecycle routing: pass")
    print("- stage-scoped skill_plan lazy activation: pass")
    print("- local lifecycle ownership + optional Superpowers method provider: pass")
    print("- route facts delta, capability-missing, stale/duplicate transition checks: pass")
    print("- workflow manifest + artifact graph positive/negative checks: pass")
    print("- version/stage/resume/verifier false-claim checks: pass")
    print("- review producer/identity/evidence, repair-cycle, and true-block runtime checks: pass")
    print("- high-risk stage evidence gates: pass")
    print("- atomic unsigned manifest migration + signed-claim refusal: pass")
    print("- heavyweight default method + unbounded review registry negatives: pass")
    print("- managed review gate coverage + repair-stage negatives: pass")
    print("- managed close claims + canonical acceptance contract negatives: pass")
    print("- JSON evidence manifest claim checks: pass")
    print("- context static/freshness/runtime/sufficiency checks: pass")
    print("- learning candidate path-safety checks: pass")
    print("- handoff fresh consumer artifact install/import: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
