#!/usr/bin/env python3
"""Run deterministic end-to-end checks for the control-plane artifacts."""

from __future__ import annotations

import hashlib
import json
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
        "schema_version": 1,
        "status": "provisional",
        "classification": {
            "risk": "L3",
            "work_intent": "implement",
            "delivery_shape": "mvp",
            "scope": "cross_module",
            "uncertainty": "high",
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
        "schema_version": 1,
        "repo_revision": "e2e",
        "spec_systems": [
            {"id": "openspec", "status": "available", "evidence": ["openspec/config.yaml"]},
            {"id": "fallback", "status": "available", "evidence": ["workflow fallback"]},
        ],
        "execution_engines": [
            {"id": "local", "status": "available", "version": "builtin"},
            {"id": "superpowers", "status": "available", "version": "unknown"},
        ],
        "project_harness": {"status": "present", "version": "2", "evidence": ["AGENTS.md"]},
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


def workflow_manifest(*, requested: str = "integration_done", validated_claim: str = "integration_done") -> dict[str, Any]:
    return {
        "schema_version": 3,
        "skill_suite_version": "2026-06-24",
        "run_id": "run-control-plane-e2e",
        "manifest_revision": 1,
        "strategy_version": "1.0",
        "workflow_state": "review_ready",
        "classification": {
            "risk": "L3",
            "mode": "implement",
            "scope": "cross_module",
            "uncertainty": "high",
            "profiles": ["frontend", "api"],
        },
        "routing": {
            "spec_system": "fallback",
            "execution_engine": "superpowers",
            "strategy_id": "complex-real-slice",
            "required_skills": ["context-grounding", "specflow", "technical-design", "delivery-verification"],
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
                "depends_on": ["impl-001"],
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
                        "strategy_version": "1.0",
                        "registry_digest": "sha256:registry",
                        "evidence_manifest_digest": "sha256:evidence",
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
        repo = root / "repo"
        feature = "Billing MVP"
        run([sys.executable, str(HARNESS_INIT), "--root", str(repo), "--feature-id", feature, "--project-skill", "billing"])
        run([sys.executable, str(HARNESS_VALIDATE), "--root", str(repo), "--feature-id", feature, "--project-skill", "billing"])
        assert_harness_paths(repo, "billing-mvp")

        source_file = write_text(repo / "src" / "orders" / "implementation.ts", "export const ok = true;\n")
        spec_file = write_text(repo / "docs" / "superpowers" / "specs" / "2026-06-23-feature-spec.md", "# Spec\n")

        write_json(root / "capability-report.json", capability_report())
        route_path = write_json(root / "route-decision.json", route_decision())
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
        capability_missing["execution_engines"] = [{"id": "local", "status": "available", "version": "builtin"}]
        write_json(root / "capability-missing-superpowers.json", capability_missing)
        required_superpowers_route = route_decision()
        required_superpowers_route["capability_report_ref"] = "capability-missing-superpowers.json"
        required_superpowers_route["user_constraints"]["required_execution_engine"] = "superpowers"
        required_superpowers_path = write_json(root / "route-required-superpowers-bad.json", required_superpowers_route)
        delta_path = write_json(root / "route-facts-delta.json", route_facts_delta())
        rerouted_path = root / "route-decision-v2.json"
        run([sys.executable, str(WORKFLOW / "scripts" / "resolve_strategy.py"), str(route_path), "--output", str(resolved_path)])
        run([sys.executable, str(WORKFLOW / "scripts" / "resolve_strategy.py"), str(required_superpowers_path)], expect_ok=False)
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
        wf_embedded_bad["current_stage"] = "plan"
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
        wf_split_embedded_bad["current_stage"] = "plan"
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
        run([sys.executable, str(graph_validator), str(wf_plan_missing_spec_bad_path)], expect_ok=False)
        run([sys.executable, str(graph_validator), str(wf_design_missing_spec_bad_path)], expect_ok=False)
        run([sys.executable, str(manifest_validator), str(wf_embedded_bad_path)], expect_ok=False)
        run([sys.executable, str(manifest_validator), str(wf_compact_standalone_bad_path)], expect_ok=False)
        run([sys.executable, str(manifest_validator), str(wf_split_embedded_bad_path)], expect_ok=False)
        run([sys.executable, str(graph_validator), str(wf_stale_bad_path)], expect_ok=False)

        evidence_validator = DELIVERY / "scripts" / "validate_evidence_manifest.py"
        run([sys.executable, str(evidence_validator), str(write_json(root / "evidence-integration-ok.json", evidence_manifest("integration_done", "integration")))])
        run([sys.executable, str(evidence_validator), str(write_json(root / "evidence-broken-bad.json", evidence_manifest("dev_done", "manual", "broken")))], expect_ok=False)
        run([sys.executable, str(evidence_validator), str(write_json(root / "evidence-integration-mock-bad.json", evidence_manifest("integration_done", "mock")))], expect_ok=False)
        run([sys.executable, str(evidence_validator), str(write_json(root / "evidence-handoff-integration-bad.json", evidence_manifest("handoff_done", "integration")))], expect_ok=False)
        run([sys.executable, str(evidence_validator), str(write_json(root / "evidence-handoff-ok.json", evidence_manifest("handoff_done", "fresh_consumer")))])

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
        run([sys.executable, str(HANDOFF_FRESH_CONSUMER)])

    print("Workflow E2E eval passed")
    print("- project harness init + validate: pass")
    print("- route decision -> capability report -> strategy resolver -> init/transition: pass")
    print("- route facts delta, capability-missing, stale/duplicate transition checks: pass")
    print("- workflow manifest + artifact graph positive/negative checks: pass")
    print("- version/stage/resume/verifier false-claim checks: pass")
    print("- JSON evidence manifest claim checks: pass")
    print("- context static/freshness/runtime/sufficiency checks: pass")
    print("- learning candidate path-safety checks: pass")
    print("- handoff fresh consumer artifact install/import: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
