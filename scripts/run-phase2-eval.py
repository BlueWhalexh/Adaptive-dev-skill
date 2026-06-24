#!/usr/bin/env python3
"""Run Phase 2 evals and write a comparison report."""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "evals" / "reports"


def run(args: list[str], *, require_escalated_note: bool = False) -> tuple[int, str]:
    result = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if require_escalated_note and result.returncode != 0:
        output = result.stdout + "\nNOTE: fresh-agent eval may require unsandboxed Codex state/app-server access."
        return result.returncode, output
    return result.returncode, result.stdout


def section(title: str, command: list[str], code: int, output: str) -> str:
    return f"""## {title}

Command:

```sh
{' '.join(command)}
```

Exit code: `{code}`

Output:

```text
{output.strip()}
```
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat", type=int, default=3, help="fresh-agent repetitions")
    parser.add_argument("--skip-fresh", action="store_true", help="skip codex exec fresh-agent route eval")
    args = parser.parse_args()

    commands: list[tuple[str, list[str], bool]] = [
        ("Deterministic Sandbox", [sys.executable, "scripts/run-skill-sandbox-eval.py"], False),
        ("Workflow E2E", [sys.executable, "scripts/run-workflow-e2e-eval.py"], False),
        ("Handoff Fresh Consumer", [sys.executable, "scripts/run-handoff-fresh-consumer-eval.py"], False),
    ]
    if not args.skip_fresh:
        commands.append(("Full Fresh-Agent Route Eval", [sys.executable, "scripts/run-fresh-agent-route-eval.py", "--repeat", str(args.repeat), "--all"], True))

    report_parts = [
        "# Phase 2 Harness + Technical Design Eval",
        "",
        f"Date: {dt.date.today().isoformat()}",
        "",
        "Scope: project-harness-init technical design surface, full route eval, and old/new comparison notes.",
        "",
    ]

    failed = False
    for title, command, fresh in commands:
        code, output = run(command, require_escalated_note=fresh)
        report_parts.append(section(title, command, code, output))
        if code != 0:
            failed = True

    report_parts.append("""## Comparison Notes

- Previous control plane added `workflow_manifest.json`, strategy registry, artifact graph, and verifier-signed claims.
- Phase 2 adds a project-harness surface for Product Spec -> Technical Design -> Implementation Plan.
- Expected improvement: high-risk project initialization no longer collapses product spec and architecture decisions into one fallback design file.
- Guardrail: L0/L1 routing remains unchanged; technical design is only required by strategy/design_control.
""")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"{dt.date.today().isoformat()}-phase2-harness-technical-design-eval.md"
    report_path.write_text("\n".join(report_parts).rstrip() + "\n", encoding="utf-8")
    print(f"Phase 2 eval report: {report_path}")
    if failed:
        print("Phase 2 eval failed; inspect report for details.")
        return 1
    print("Phase 2 eval passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
