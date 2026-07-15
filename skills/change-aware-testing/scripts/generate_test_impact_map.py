#!/usr/bin/env python3
"""Generate a conservative candidate test-impact map from repository conventions."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from run_changed_tests import SelectionError, load_config, validate_config


def tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        raise SelectionError(result.stderr.strip() or "cannot list repository files")
    return sorted({line.strip() for line in result.stdout.splitlines() if line.strip()})


def safe_id(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-.")
    return normalized[:72] or "root"


def command_set(command: list[str]) -> dict[str, list[list[str]]]:
    return {"inner_loop": [command], "checkpoint": [command], "completion": [command]}


def python_rules(files: list[str]) -> tuple[list[dict[str, Any]], list[list[str]]]:
    source_modules = sorted({path.split("/")[1] for path in files if path.startswith("src/") and path.endswith(".py") and len(path.split("/")) > 2})
    rules: list[dict[str, Any]] = []
    all_tests = [path for path in files if path.startswith("tests/") and path.endswith(".py")]
    if any(path.startswith("src/") and path.count("/") == 1 and path.endswith(".py") for path in files) and all_tests:
        rules.append({
            "id": "python-src-root",
            "source_globs": ["src/*.py"],
            "test_globs": ["tests/**"],
            "commands": command_set(["python3", "-m", "pytest", "{tests}", "-q"]),
        })
    for module in source_modules:
        mirrored = [path for path in all_tests if path.startswith(f"tests/{module}/") or Path(path).name.startswith(f"test_{module}")]
        test_globs = [f"tests/{module}/**", f"tests/test_{module}*.py"] if mirrored else ["tests/**"]
        rules.append({
            "id": f"python-{safe_id(module)}",
            "source_globs": [f"src/{module}/**"],
            "test_globs": test_globs,
            "commands": command_set(["python3", "-m", "pytest", "{tests}", "-q"]),
        })
    fallback = [["python3", "-m", "pytest", "tests", "-q"]] if rules and all_tests else []
    return rules, fallback


def go_rules(files: list[str]) -> tuple[list[dict[str, Any]], list[list[str]]]:
    packages = sorted({str(Path(path).parent) for path in files if path.endswith("_test.go")})
    rules = []
    for package in packages:
        prefix = "" if package == "." else package + "/"
        command = ["go", "test", "." if package == "." else f"./{package}"]
        rules.append({
            "id": f"go-{safe_id(package)}",
            "source_globs": [f"{prefix}*.go"],
            "test_globs": [f"{prefix}*_test.go"],
            "commands": command_set(command),
        })
    return rules, [["go", "test", "./..."]] if rules else []


def node_rules(root: Path, files: list[str]) -> tuple[list[dict[str, Any]], list[list[str]]]:
    package_path = root / "package.json"
    if not package_path.is_file():
        return [], []
    try:
        package = json.loads(package_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [], []
    dependencies = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
    if not ({"jest", "vitest"} & set(dependencies)) or "test" not in package.get("scripts", {}):
        return [], []
    test_files = [path for path in files if re.search(r"(^tests?/|\.(test|spec)\.[cm]?[jt]sx?$)", path)]
    source_files = [path for path in files if path.startswith("src/") and re.search(r"\.[cm]?[jt]sx?$", path)]
    if not source_files or not test_files:
        return [], []
    if (root / "pnpm-lock.yaml").is_file():
        runner = ["pnpm", "test", "--"]
    elif (root / "yarn.lock").is_file():
        runner = ["yarn", "test", "--"]
    else:
        runner = ["npm", "test", "--"]
    command = [*runner, "{tests}"]
    rule = {
        "id": "node-src",
        "source_globs": ["src/**"],
        "test_globs": ["tests/**", "test/**", "src/**/*.test.*", "src/**/*.spec.*"],
        "commands": command_set(command),
    }
    return [rule], [[*runner]]


def unique_commands(commands: list[list[str]]) -> list[list[str]]:
    return [list(value) for value in dict.fromkeys(tuple(command) for command in commands)]


def generated_map(root: Path) -> dict[str, Any]:
    files = tracked_files(root)
    rules: list[dict[str, Any]] = []
    fallback: list[list[str]] = []
    for detector in (python_rules, go_rules):
        detected_rules, detected_fallback = detector(files)
        rules.extend(detected_rules)
        fallback.extend(detected_fallback)
    node_detected, node_fallback = node_rules(root, files)
    rules.extend(node_detected)
    fallback.extend(node_fallback)
    if not rules:
        raise SelectionError("no supported Python, Go, Jest, or Vitest test structure was detected")
    global_candidates = [
        "pyproject.toml", "pytest.ini", "tox.ini", "go.mod", "go.sum", "package.json",
        "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "tests/conftest.py",
    ]
    present_globals = [path for path in global_candidates if path in files]
    return {
        "schema_version": 1,
        "global_triggers": ([{"id": "generated-shared-tooling", "globs": present_globals}] if present_globals else []),
        "rules": rules,
        "fallback_commands": {
            "checkpoint": unique_commands(fallback),
            "completion": unique_commands(fallback),
        },
    }


def merge_maps(existing: dict[str, Any], generated: dict[str, Any]) -> dict[str, Any]:
    merged = json.loads(json.dumps(existing))
    triggers_by_id = {item["id"]: item for item in merged["global_triggers"]}
    for trigger in generated["global_triggers"]:
        current = triggers_by_id.get(trigger["id"])
        if current is None:
            merged["global_triggers"].append(trigger)
            triggers_by_id[trigger["id"]] = trigger
        else:
            current["globs"] = list(dict.fromkeys([*current["globs"], *trigger["globs"]]))
    known_rule_ids = {item["id"] for item in merged["rules"]}
    merged["rules"].extend(item for item in generated["rules"] if item["id"] not in known_rule_ids)
    for cadence in ("checkpoint", "completion"):
        merged["fallback_commands"][cadence] = unique_commands([
            *merged["fallback_commands"][cadence],
            *generated["fallback_commands"][cadence],
        ])
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default=".agent/test-impact-map.candidate.json")
    parser.add_argument("--update", action="store_true", help="merge with the canonical map while preserving existing rules")
    parser.add_argument("--promote", action="store_true", help="write the validated result to .agent/test-impact-map.json")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    canonical = root / ".agent/test-impact-map.json"
    output = canonical if args.promote else root / args.output
    try:
        candidate = generated_map(root)
        if args.update:
            candidate = merge_maps(load_config(canonical), candidate)
        elif args.promote and canonical.exists():
            raise SelectionError("canonical map exists; use --update --promote to preserve reviewed rules")
        validate_config(candidate)
    except (OSError, SelectionError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Candidate test impact map written: {output}")
    if not args.promote:
        print("Review the candidate, then rerun with --promote (and --update when a canonical map exists).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
