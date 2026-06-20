#!/usr/bin/env python3
"""Run deterministic end-to-end workflow checks in a temporary repo."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARNESS_INIT = ROOT / "skills" / "project-harness-init" / "scripts" / "init_project_harness.py"
HARNESS_VALIDATE = ROOT / "skills" / "project-harness-init" / "scripts" / "validate_project_harness.py"
EVIDENCE_VALIDATE = ROOT / "skills" / "adaptive-dev-workflow" / "scripts" / "validate_evidence_manifest.py"
CARDS_VALIDATE = ROOT / "skills" / "adaptive-dev-workflow" / "scripts" / "validate_workflow_cards.py"
HANDOFF_FRESH_CONSUMER = ROOT / "scripts" / "run-handoff-fresh-consumer-eval.py"


def run(args: list[str], *, expect_ok: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if expect_ok and result.returncode != 0:
        raise SystemExit("command failed:\n" + " ".join(args) + "\n" + result.stdout)
    if not expect_ok and result.returncode == 0:
        raise SystemExit("command unexpectedly passed:\n" + " ".join(args) + "\n" + result.stdout)
    return result


def write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def evidence_manifest(claim: str, evidence_type: str, result: str = "pass") -> str:
    return f"""feature_id: workflow-e2e
commit_sha: working-tree
claim_ceiling: {claim}
changed_surfaces:
  - workflow
acceptance:
  - id: AC-1
    evidence: V-1
validators:
  - name: V-1
    command_or_method: "simulated validator"
    type: {evidence_type}
    result: {result}
    proves: "The selected evidence type supports the claim under test."
    gaps: "Synthetic manifest only; product behavior is not tested."
deferred:
  - "No product runtime in workflow eval."
review_focus:
  - "Claim ceiling and evidence type consistency."
"""


def workflow_cards(route: str, claim: str, chain: str, handoff: str) -> str:
    return f"""route_card:
  route: {route}
  risk_type: delivery
  changed_surfaces: ["SDK/package"]
  required_gates: ["delivery contract", "fresh consumer verification"]
  delegated_skills: []
  loaded_references: ["production-handoff-gate.md", "evidence-and-validation.md"]
  stop_gates: ["public API change", "accepted evidence gap"]
evidence_card:
  claim_ceiling: {claim}
  pre_implementation: "delivery contract"
  post_implementation: "build/install validator"
  chain: "{chain}"
  handoff: "{handoff}"
  review: "evidence reviewer"
  gaps: "No real product package in synthetic eval."
"""


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="adaptive-workflow-e2e-") as tmp:
        root = Path(tmp)
        target = root / "repo"
        feature = "Billing MVP"
        project_skill = "billing"

        run([
            sys.executable,
            str(HARNESS_INIT),
            "--root",
            str(target),
            "--feature-id",
            feature,
            "--project-skill",
            project_skill,
        ])
        run([
            sys.executable,
            str(HARNESS_VALIDATE),
            "--root",
            str(target),
            "--feature-id",
            feature,
            "--project-skill",
            project_skill,
        ])

        cards_ok = write(root / "cards-ok.yaml", workflow_cards(
            "Medium/Large",
            "Handoff Done",
            "integration smoke passed",
            "fresh consumer installed artifact from onboarding path",
        ))
        cards_bad = write(root / "cards-bad.yaml", workflow_cards(
            "Medium",
            "Handoff Done",
            "integration smoke passed",
            "none",
        ))
        cards_artifact_only_bad = write(root / "cards-artifact-only-bad.yaml", workflow_cards(
            "Medium/Large",
            "Handoff Done",
            "integration smoke passed",
            "artifact and onboarding path documented",
        ))
        run([sys.executable, str(CARDS_VALIDATE), str(cards_ok)])
        run([sys.executable, str(CARDS_VALIDATE), str(cards_bad)], expect_ok=False)
        run([sys.executable, str(CARDS_VALIDATE), str(cards_artifact_only_bad)], expect_ok=False)

        dev_ok = write(root / "dev-ok.yaml", evidence_manifest("Dev Done", "manual"))
        integration_bad = write(root / "integration-bad.yaml", evidence_manifest("Integration Done", "mock"))
        integration_ok = write(root / "integration-ok.yaml", evidence_manifest("Integration Done", "integration"))
        handoff_bad = write(root / "handoff-bad.yaml", evidence_manifest("Handoff Done", "integration"))
        handoff_ok = write(root / "handoff-ok.yaml", evidence_manifest("Handoff Done", "fresh consumer"))

        run([sys.executable, str(EVIDENCE_VALIDATE), str(dev_ok)])
        run([sys.executable, str(EVIDENCE_VALIDATE), str(integration_bad)], expect_ok=False)
        run([sys.executable, str(EVIDENCE_VALIDATE), str(integration_ok)])
        run([sys.executable, str(EVIDENCE_VALIDATE), str(handoff_bad)], expect_ok=False)
        run([sys.executable, str(EVIDENCE_VALIDATE), str(handoff_ok)])
        run([sys.executable, str(HANDOFF_FRESH_CONSUMER)])

    print("Workflow E2E eval passed")
    print("- project harness init + validate: pass")
    print("- route/evidence card positive + negative checks: pass")
    print("- evidence manifest claim ceiling checks: pass")
    print("- handoff fresh consumer artifact install/import: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
