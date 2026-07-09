#!/usr/bin/env python3
"""Run deterministic checks for the agent-orchestration skill."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ORCH = ROOT / "skills" / "agent-orchestration"


def run(args: list[str], *, expect_ok: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if expect_ok and result.returncode != 0:
        raise SystemExit("command failed:\n" + " ".join(args) + "\n" + result.stdout)
    if not expect_ok and result.returncode == 0:
        raise SystemExit("command unexpectedly passed:\n" + " ".join(args) + "\n" + result.stdout)
    return result


def write_json(path: Path, value: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def manifest() -> dict[str, Any]:
    return {
        "schema_version": 3,
        "run_id": "WF-ORCH-001",
        "manifest_revision": 7,
        "current_stage": "spec_review",
        "artifacts": [
            {
                "id": "ap-001",
                "type": "analysis_pack",
                "status": "approved",
                "path": "docs/analysis/ap-001.md",
            },
            {
                "id": "spec-001",
                "type": "spec",
                "status": "ready",
                "path": "docs/specs/spec-001.md",
            },
        ],
    }


def roster() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "workflow_id": "WF-ORCH-001",
        "agents": [
            {
                "agent_id": "agent-spec-reviewer",
                "role": "spec_reviewer",
                "status": "active",
                "capabilities": ["spec review", "acceptance gap analysis"],
                "allowed_artifact_types": ["spec_review_report"],
                "max_parallel_work_orders": 1,
            }
        ],
    }


def work_result() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "work_order_id": "WO-001",
        "workflow_id": "WF-ORCH-001",
        "role": "spec_reviewer",
        "status": "completed",
        "produced_artifacts": [
            {
                "artifact_id": "review-001",
                "type": "spec_review_report",
                "path": "docs/reviews/spec-review-001.json",
                "status": "ready",
            }
        ],
        "discovered_facts": {},
        "evidence_refs": [],
        "claim_requests": [],
        "next_work_order_requests": [],
        "error": None,
        "handoff_notes": "Spec acceptance is reviewable.",
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="agent-orch-e2e-") as tmp:
        root = Path(tmp)
        manifest_path = write_json(root / "workflow_manifest.json", manifest())
        roster_path = write_json(root / "agent_roster.json", roster())
        context_path = root / "context_packet.json"
        order_path = root / "work_order.json"
        result_path = write_json(root / "work_result.json", work_result())

        run([sys.executable, str(ORCH / "scripts" / "validate_agent_roster.py"), str(roster_path)])
        run([
            sys.executable,
            str(ORCH / "scripts" / "build_context_packet.py"),
            str(manifest_path),
            "--role",
            "spec_reviewer",
            "--context-packet-id",
            "CP-001",
            "--include-artifact",
            "ap-001",
            "--include-artifact",
            "spec-001",
            "--allowed-path",
            "docs/specs/spec-001.md",
            "--allowed-path",
            "docs/analysis/ap-001.md",
            "--forbidden-path",
            "src/**",
            "--instruction",
            "Review goals, non-goals, acceptance, evidence plan, and drift risk.",
            "--output",
            str(context_path),
        ])
        run([
            sys.executable,
            str(ORCH / "scripts" / "create_work_order.py"),
            "--workflow-id",
            "WF-ORCH-001",
            "--work-order-id",
            "WO-001",
            "--role",
            "spec_reviewer",
            "--stage-id",
            "spec_review",
            "--context-packet",
            str(context_path),
            "--agent-roster",
            str(roster_path),
            "--objective",
            "Review the draft spec without editing production code.",
            "--output-artifact-type",
            "spec_review_report",
            "--output-artifact-path",
            "docs/reviews/spec-review-001.json",
            "--output",
            str(order_path),
        ])
        run([sys.executable, str(ORCH / "scripts" / "validate_work_result.py"), str(result_path), "--work-order", str(order_path)])

        bad_context = json.loads(context_path.read_text(encoding="utf-8"))
        bad_context["instructions"] = ["Read the full chat history and continue."]
        bad_context_path = write_json(root / "bad_context_packet.json", bad_context)
        run([sys.executable, str(ORCH / "scripts" / "validate_context_packet.py"), str(bad_context_path)], expect_ok=False)

        bad_result = work_result()
        bad_result["produced_artifacts"][0]["type"] = "implementation"
        bad_result_path = write_json(root / "bad_work_result.json", bad_result)
        run([sys.executable, str(ORCH / "scripts" / "validate_work_result.py"), str(bad_result_path), "--work-order", str(order_path)], expect_ok=False)

        orders_dir = root / "work_orders"
        results_dir = root / "results"
        write_json(orders_dir / "WO-001.json", json.loads(order_path.read_text(encoding="utf-8")))
        write_json(results_dir / "WO-001.json", work_result())
        run([sys.executable, str(ORCH / "scripts" / "summarize_progress.py"), "--work-orders", str(orders_dir), "--results", str(results_dir)])

    print("Agent orchestration E2E eval passed")
    print("- roster/context/work-order/result positive flow: pass")
    print("- full-chat context negative check: pass")
    print("- wrong result artifact type negative check: pass")
    print("- progress summary: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
