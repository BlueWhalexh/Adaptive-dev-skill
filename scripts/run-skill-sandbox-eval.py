#!/usr/bin/env python3
"""Default eval entrypoint for the lightweight Adaptive skill."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str]) -> None:
    result = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    print(result.stdout, end="")
    if result.returncode:
        raise SystemExit(result.returncode)


def main() -> int:
    run([sys.executable, "scripts/run-outcome-first-eval.py"])
    run([
        sys.executable,
        "/Users/didi/.codex/skills/.system/skill-creator/scripts/quick_validate.py",
        "skills/adaptive-dev-workflow",
    ])
    print("PASS: default Adaptive sandbox eval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
