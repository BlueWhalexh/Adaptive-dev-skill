#!/usr/bin/env python3
"""Validate a structured evidence manifest before completion claims.

The validator intentionally uses only the Python standard library. It supports
plain YAML-like manifests and Markdown files containing a fenced yaml block.
It is not a general YAML parser; it checks the workflow contract fields this
skill relies on.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


CLAIM_LEVELS = {"Dev Done", "Integration Done", "Handoff Done"}
EVIDENCE_TYPES = {
    "unit",
    "mock",
    "fake",
    "integration",
    "e2e",
    "real external",
    "fresh consumer",
    "manual",
}
TOP_LEVEL_REQUIRED = [
    "feature_id",
    "commit_sha",
    "claim_ceiling",
    "changed_surfaces",
    "acceptance",
    "validators",
    "deferred",
    "review_focus",
]
VALIDATOR_REQUIRED = ["name", "command_or_method", "type", "result", "proves", "gaps"]
ACCEPTANCE_REQUIRED = ["id", "evidence"]
PENDING_VALUES = {"", "pending", "todo", "tbd", "not run", "not_run"}
PASS_MARKERS = ("pass", "passed", "ok", "success", "succeeded", "exit 0", "green")
CLAIM_REQUIRED_TYPES = {
    "Dev Done": EVIDENCE_TYPES,
    "Integration Done": {"integration", "e2e", "real external", "fresh consumer"},
    "Handoff Done": {"fresh consumer", "real external"},
}


def normalize(value: str | None) -> str:
    if value is None:
        return ""
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]
    return value.strip()


def extract_structured_text(raw: str) -> str:
    if re.search(r"(?m)^claim_ceiling\s*:", raw) and re.search(r"(?m)^validators\s*:", raw):
        return raw

    for match in re.finditer(r"```(?:yaml|yml)?\s*\n(.*?)\n```", raw, re.S | re.I):
        block = match.group(1)
        if "claim_ceiling:" in block and "validators:" in block:
            return block
    raise ValueError("no structured evidence manifest found; provide YAML or a fenced yaml block")


def top_level_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}\s*:\s*(.*)$", text)
    return normalize(match.group(1)) if match else None


def top_level_exists(text: str, key: str) -> bool:
    return re.search(rf"(?m)^{re.escape(key)}\s*:", text) is not None


def section_text(text: str, section: str) -> str:
    match = re.search(rf"(?m)^{re.escape(section)}\s*:\s*(.*)$", text)
    if not match:
        return ""

    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if re.match(rf"^{re.escape(section)}\s*:", line):
            start = index
            break
    if start is None:
        return ""

    collected: list[str] = []
    first_line_tail = re.sub(rf"^{re.escape(section)}\s*:\s*", "", lines[start]).strip()
    if first_line_tail:
        collected.append(first_line_tail)

    for line in lines[start + 1 :]:
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*:", line):
            break
        collected.append(line)
    return "\n".join(collected)


def list_items(section: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    for line in section.splitlines():
        if re.match(r"\s*-\s+", line):
            if current:
                items.append("\n".join(current))
            current = [line]
        elif current:
            current.append(line)
    if current:
        items.append("\n".join(current))
    return items


def block_value(block: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s*(?:-\s*)?{re.escape(key)}\s*:\s*(.*)$", block)
    return normalize(match.group(1)) if match else None


def block_has_key(block: str, key: str) -> bool:
    return re.search(rf"(?m)^\s*(?:-\s*)?{re.escape(key)}\s*:", block) is not None


def is_passing_result(value: str) -> bool:
    low = value.lower()
    if any(marker in low for marker in ("fail", "error", "block", "skip", "pending", "not run", "not pass")):
        return False
    return any(marker in low for marker in PASS_MARKERS)


def validate(path: Path, allow_pending: bool) -> list[str]:
    errors: list[str] = []
    try:
        text = extract_structured_text(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [str(exc)]

    missing_top = [key for key in TOP_LEVEL_REQUIRED if not top_level_exists(text, key)]
    if missing_top:
        errors.append("missing top-level fields: " + ", ".join(missing_top))

    claim = top_level_value(text, "claim_ceiling")
    if claim not in CLAIM_LEVELS:
        errors.append(f"invalid claim_ceiling: {claim or '<empty>'}")

    acceptance_items = list_items(section_text(text, "acceptance"))
    if not acceptance_items:
        errors.append("acceptance must contain at least one item")
    for item in acceptance_items:
        item_id = block_value(item, "id") or "<unknown>"
        missing = [key for key in ACCEPTANCE_REQUIRED if not block_has_key(item, key)]
        if missing:
            errors.append(f"acceptance {item_id} missing fields: {', '.join(missing)}")

    validator_items = list_items(section_text(text, "validators"))
    if not validator_items:
        errors.append("validators must contain at least one item")

    passing_types: set[str] = set()
    for item in validator_items:
        name = block_value(item, "name") or "<unknown>"
        missing = [key for key in VALIDATOR_REQUIRED if not block_has_key(item, key)]
        if missing:
            errors.append(f"validator {name} missing fields: {', '.join(missing)}")
            continue

        evidence_type = (block_value(item, "type") or "").lower()
        if evidence_type not in EVIDENCE_TYPES:
            errors.append(f"validator {name} has invalid type: {evidence_type or '<empty>'}")

        result = (block_value(item, "result") or "").lower()
        if result in PENDING_VALUES and not allow_pending:
            errors.append(f"validator {name} result is not final: {result or '<empty>'}")
        if evidence_type in EVIDENCE_TYPES and is_passing_result(result):
            passing_types.add(evidence_type)

    if claim in CLAIM_REQUIRED_TYPES:
        required_types = CLAIM_REQUIRED_TYPES[claim]
        if not passing_types:
            errors.append(f"{claim} requires at least one passing validator")
        elif not passing_types.intersection(required_types):
            allowed = ", ".join(sorted(required_types))
            actual = ", ".join(sorted(passing_types))
            errors.append(f"{claim} cannot be supported by evidence types [{actual}]; requires one of [{allowed}]")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="Path to evidence manifest yaml or Markdown with fenced yaml")
    parser.add_argument("--allow-pending", action="store_true", help="Allow pending validator results for draft review")
    args = parser.parse_args()

    path = Path(args.manifest)
    if not path.exists():
        raise SystemExit(f"missing evidence manifest: {path}")

    errors = validate(path, args.allow_pending)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    print(f"Evidence manifest valid: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
