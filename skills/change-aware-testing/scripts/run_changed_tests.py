#!/usr/bin/env python3
"""Plan or execute changed-file-aware tests from a repository-owned impact map."""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


MODES = {"inner-loop": "inner_loop", "checkpoint": "checkpoint", "completion": "completion"}


class SelectionError(RuntimeError):
    pass


def git(root: Path, *args: str, ok_codes: tuple[int, ...] = (0,)) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode not in ok_codes:
        raise SelectionError(result.stderr.strip() or "git command failed")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def changed_files(root: Path, base: str | None, include_untracked: bool) -> list[str]:
    paths: set[str] = set()
    if base:
        git(root, "rev-parse", "--verify", f"{base}^{{commit}}")
        paths.update(git(root, "diff", "--name-only", "--diff-filter=ACMR", f"{base}...HEAD"))
    paths.update(git(root, "diff", "--name-only", "--diff-filter=ACMR", "--cached"))
    paths.update(git(root, "diff", "--name-only", "--diff-filter=ACMR"))
    if include_untracked:
        paths.update(git(root, "ls-files", "--others", "--exclude-standard"))
    return sorted(paths)


def matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def load_config(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SelectionError(f"missing impact map: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SelectionError(f"invalid JSON in impact map: {exc}") from exc
    validate_config(value)
    return value


def validate_commands(value: Any, location: str) -> None:
    if not isinstance(value, list):
        raise SelectionError(f"{location} must be a list of argv arrays")
    for index, command in enumerate(value):
        if not isinstance(command, list) or not command or not all(isinstance(token, str) for token in command):
            raise SelectionError(f"{location}[{index}] must be a non-empty argv array")


def validate_config(value: Any) -> None:
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise SelectionError("impact map must be an object with schema_version=1")
    allowed = {"schema_version", "global_triggers", "rules", "fallback_commands"}
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise SelectionError("impact map has unknown fields: " + ", ".join(unknown))
    for key in ("global_triggers", "rules"):
        if not isinstance(value.get(key), list):
            raise SelectionError(f"impact map field {key} must be a list")
    if not value["rules"]:
        raise SelectionError("impact map rules cannot be empty")

    ids: set[str] = set()
    for group_name in ("global_triggers", "rules"):
        for index, item in enumerate(value[group_name]):
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                raise SelectionError(f"{group_name}[{index}] needs a string id")
            if item["id"] in ids:
                raise SelectionError(f"duplicate impact id: {item['id']}")
            ids.add(item["id"])
            required_globs = ("globs",) if group_name == "global_triggers" else ("source_globs", "test_globs")
            for field in required_globs:
                patterns = item.get(field)
                if not isinstance(patterns, list) or not patterns or not all(isinstance(pattern, str) and pattern for pattern in patterns):
                    raise SelectionError(f"{group_name}[{index}].{field} must be a non-empty string list")
            if group_name == "rules":
                commands = item.get("commands")
                if not isinstance(commands, dict):
                    raise SelectionError(f"rules[{index}].commands must be an object")
                for cadence in MODES.values():
                    validate_commands(commands.get(cadence), f"rules[{index}].commands.{cadence}")

    fallback = value.get("fallback_commands")
    if not isinstance(fallback, dict):
        raise SelectionError("fallback_commands must be an object")
    for cadence in ("checkpoint", "completion"):
        validate_commands(fallback.get(cadence), f"fallback_commands.{cadence}")


def tracked_files(root: Path) -> list[str]:
    return sorted(set(git(root, "ls-files")) | set(git(root, "ls-files", "--others", "--exclude-standard")))


def expand_command(command: list[str], tests: list[str]) -> list[str] | None:
    expanded: list[str] = []
    for token in command:
        if token == "{tests}":
            if not tests:
                return None
            expanded.extend(tests)
        else:
            expanded.append(token)
    return expanded


def unique_commands(commands: list[list[str]]) -> list[list[str]]:
    seen: set[tuple[str, ...]] = set()
    result: list[list[str]] = []
    for command in commands:
        key = tuple(command)
        if key not in seen:
            seen.add(key)
            result.append(command)
    return result


def build_plan(root: Path, config: dict[str, Any], changed: list[str], mode: str, base: str | None) -> dict[str, Any]:
    mode_key = MODES[mode]
    all_files = tracked_files(root)
    global_hits: list[dict[str, Any]] = []
    for trigger in config["global_triggers"]:
        hit_paths = [path for path in changed if matches(path, trigger["globs"])]
        if hit_paths:
            global_hits.append({"id": trigger["id"], "paths": hit_paths})

    matched_rules: list[str] = []
    selected_tests: set[str] = set()
    selected_commands: list[list[str]] = []
    for rule in config["rules"]:
        if not any(matches(path, rule["source_globs"] + rule["test_globs"]) for path in changed):
            continue
        matched_rules.append(rule["id"])
        rule_tests = sorted(path for path in all_files if matches(path, rule["test_globs"]))
        selected_tests.update(rule_tests)
        for command in rule["commands"].get(mode_key, []):
            expanded = expand_command(command, rule_tests)
            if expanded:
                selected_commands.append(expanded)

    requires_broad = bool(global_hits)
    status = "ready"
    reasons: list[str] = []
    if not changed:
        status = "no_changes"
        reasons.append("No changed files were found for the selected task boundary.")
    elif global_hits:
        fallback_mode = "checkpoint" if mode == "inner-loop" else mode_key
        selected_commands = [list(command) for command in config["fallback_commands"].get(fallback_mode, [])]
        if mode == "inner-loop":
            status = "checkpoint_required"
            reasons.append("Global-impact files changed; defer broad fallback to an explicit checkpoint.")
        elif not selected_commands:
            status = "unmapped"
            reasons.append(f"No fallback command is configured for {fallback_mode}.")
    elif not matched_rules or not selected_commands:
        if mode == "completion":
            selected_commands = [list(command) for command in config["fallback_commands"].get("completion", [])]
            requires_broad = bool(selected_commands)
        if not selected_commands:
            status = "unmapped"
            reasons.append("Changed files are not covered by a rule with an executable command.")

    return {
        "schema_version": 1,
        "mode": mode,
        "base": base,
        "status": status,
        "changed_files": changed,
        "global_hits": global_hits,
        "matched_rules": matched_rules,
        "selected_tests": sorted(selected_tests),
        "commands": unique_commands(selected_commands),
        "requires_broad": requires_broad,
        "reasons": reasons,
        "execution": {"status": "not_run", "results": []},
    }


def execute_plan(root: Path, plan: dict[str, Any], allow_broad: bool) -> int:
    if plan["status"] in {"no_changes", "unmapped"}:
        plan["execution"]["status"] = "blocked"
        return 3
    if plan["status"] == "checkpoint_required" and not allow_broad:
        plan["execution"]["status"] = "blocked"
        plan["reasons"].append("Re-run in checkpoint mode or pass --allow-broad explicitly.")
        return 4
    results: list[dict[str, Any]] = []
    for command in plan["commands"]:
        result = subprocess.run(command, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        results.append({"command": command, "returncode": result.returncode, "output": result.stdout})
        if result.returncode != 0:
            plan["execution"] = {"status": "fail", "results": results}
            return result.returncode or 1
    plan["execution"] = {"status": "pass", "results": results}
    return 0


def write_result(plan: dict[str, Any], output: Path | None) -> None:
    rendered = json.dumps(plan, ensure_ascii=False, indent=2) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--base", help="task-start commit used for committed branch diff")
    parser.add_argument("--mode", choices=sorted(MODES), default="inner-loop")
    parser.add_argument("--config", default=".agent/test-impact-map.json")
    parser.add_argument("--output", help="write JSON plan/result to this path")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--allow-broad", action="store_true", help="allow broad fallback during inner-loop escalation")
    parser.add_argument("--no-untracked", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.output) if args.output else None
    if output and not output.is_absolute():
        output = root / output
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = root / config_path

    try:
        changed = changed_files(root, args.base, not args.no_untracked)
        plan = build_plan(root, load_config(config_path), changed, args.mode, args.base)
    except SelectionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2

    exit_code = execute_plan(root, plan, args.allow_broad) if args.execute else (3 if plan["status"] == "unmapped" else 0)
    write_result(plan, output)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
