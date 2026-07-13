#!/usr/bin/env python3
"""Deterministic eval for changed-file-aware test selection and escalation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "skills" / "change-aware-testing" / "scripts" / "run_changed_tests.py"


def run(args: list[str], *, cwd: Path, expect: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if result.returncode != expect:
        raise SystemExit(
            f"unexpected exit {result.returncode}, wanted {expect}: {' '.join(args)}\n{result.stdout}"
        )
    return result


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def config() -> dict[str, Any]:
    marker = "from pathlib import Path; Path('focused.marker').write_text('|'.join(__import__('sys').argv[1:]))"
    broad = "from pathlib import Path; Path('broad.marker').write_text('ok')"
    return {
        "schema_version": 1,
        "global_triggers": [{"id": "shared-tooling", "globs": ["pyproject.toml"]}],
        "rules": [
            {
                "id": "orders",
                "source_globs": ["src/orders/**"],
                "test_globs": ["tests/orders/**"],
                "commands": {
                    "inner_loop": [[sys.executable, "-c", marker, "{tests}"]],
                    "checkpoint": [[sys.executable, "-c", marker, "{tests}"]],
                    "completion": [[sys.executable, "-c", marker, "{tests}"]],
                },
            }
        ],
        "fallback_commands": {
            "checkpoint": [[sys.executable, "-c", broad]],
            "completion": [[sys.executable, "-c", broad]],
        },
    }


def init_repo(root: Path) -> None:
    run(["git", "init", "-q"], cwd=root)
    run(["git", "config", "user.email", "eval@example.com"], cwd=root)
    run(["git", "config", "user.name", "Eval"], cwd=root)
    write(root / "src/orders/service.py", "VALUE = 1\n")
    write(root / "src/users/service.py", "VALUE = 1\n")
    write(root / "tests/orders/test_service.py", "def test_order(): pass\n")
    write(root / "tests/users/test_service.py", "def test_user(): pass\n")
    write(root / "pyproject.toml", "[tool.pytest.ini_options]\n")
    write(root / ".agent/test-impact-map.json", json.dumps(config(), indent=2) + "\n")
    run(["git", "add", "."], cwd=root)
    run(["git", "commit", "-qm", "baseline"], cwd=root)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="change-aware-testing-") as temp:
        repo = Path(temp)
        init_repo(repo)
        write(repo / "src/orders/service.py", "VALUE = 2\n")

        plan_path = repo / "plan.json"
        run(
            [sys.executable, str(RUNNER), "--root", str(repo), "--mode", "inner-loop", "--output", str(plan_path)],
            cwd=repo,
        )
        plan = read_json(plan_path)
        if plan["status"] != "ready" or plan["matched_rules"] != ["orders"]:
            raise SystemExit(f"focused selection failed: {plan}")
        if plan["selected_tests"] != ["tests/orders/test_service.py"]:
            raise SystemExit(f"unaffected test leaked into selection: {plan['selected_tests']}")

        run(
            [sys.executable, str(RUNNER), "--root", str(repo), "--mode", "inner-loop", "--execute", "--output", str(plan_path)],
            cwd=repo,
        )
        if read_json(plan_path)["execution"]["status"] != "pass":
            raise SystemExit("focused execution did not pass")
        if (repo / "focused.marker").read_text(encoding="utf-8") != "tests/orders/test_service.py":
            raise SystemExit("focused command did not receive only the affected tests")

        run(["git", "add", "src/orders/service.py"], cwd=repo)
        run(["git", "commit", "-qm", "focused change"], cwd=repo)
        write(repo / "pyproject.toml", "[tool.pytest.ini_options]\naddopts = '-q'\n")
        run(
            [sys.executable, str(RUNNER), "--root", str(repo), "--mode", "inner-loop", "--execute", "--output", str(plan_path)],
            cwd=repo,
            expect=4,
        )
        escalated = read_json(plan_path)
        if escalated["status"] != "checkpoint_required" or not escalated["requires_broad"]:
            raise SystemExit(f"global-impact change did not escalate: {escalated}")

        run(
            [sys.executable, str(RUNNER), "--root", str(repo), "--mode", "checkpoint", "--execute", "--output", str(plan_path)],
            cwd=repo,
        )
        if not (repo / "broad.marker").exists():
            raise SystemExit("checkpoint fallback did not execute")

    with tempfile.TemporaryDirectory(prefix="change-aware-testing-unmapped-") as temp:
        repo = Path(temp)
        init_repo(repo)
        write(repo / "src/unknown/service.py", "VALUE = 1\n")
        plan_path = repo / "plan.json"
        run(
            [sys.executable, str(RUNNER), "--root", str(repo), "--mode", "inner-loop", "--output", str(plan_path)],
            cwd=repo,
            expect=3,
        )
        if read_json(plan_path)["status"] != "unmapped":
            raise SystemExit("unmapped diff did not block incremental coverage")

    with tempfile.TemporaryDirectory(prefix="change-aware-testing-clean-") as temp:
        repo = Path(temp)
        init_repo(repo)
        plan_path = repo / "plan.json"
        run(
            [sys.executable, str(RUNNER), "--root", str(repo), "--mode", "inner-loop", "--output", str(plan_path)],
            cwd=repo,
        )
        if read_json(plan_path)["status"] != "no_changes":
            raise SystemExit("clean task boundary did not report no_changes")

    print("Change-aware testing eval passed")
    print("- affected test selection: pass")
    print("- unrelated test exclusion: pass")
    print("- inner-loop broad-test guard: pass")
    print("- checkpoint fallback: pass")
    print("- unmapped diff guard: pass")
    print("- clean task boundary: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
