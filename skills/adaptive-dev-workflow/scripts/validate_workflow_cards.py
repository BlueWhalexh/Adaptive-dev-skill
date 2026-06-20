#!/usr/bin/env python3
"""Validate route_card and evidence_card workflow contracts."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROUTES = {
    "Tiny",
    "Small",
    "Debug",
    "Medium",
    "Large",
    "OpenSpec",
    "Tiny/Small",
    "Medium/Large",
    "Medium/Large + harness",
}
CLAIM_LEVELS = {"Dev Done", "Integration Done", "Handoff Done"}
ROUTE_FIELDS = [
    "route",
    "risk_type",
    "changed_surfaces",
    "required_gates",
    "delegated_skills",
    "loaded_references",
    "stop_gates",
]
EVIDENCE_FIELDS = [
    "claim_ceiling",
    "pre_implementation",
    "post_implementation",
    "chain",
    "handoff",
    "review",
    "gaps",
]


def normalize(value: str | None) -> str:
    if value is None:
        return ""
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]
    return value.strip()


def extract_structured_text(raw: str) -> str:
    if "route_card:" in raw and "evidence_card:" in raw:
        return raw
    for match in re.finditer(r"```(?:yaml|yml)?\s*\n(.*?)\n```", raw, re.S | re.I):
        block = match.group(1)
        if "route_card:" in block and "evidence_card:" in block:
            return block
    raise ValueError("no route_card/evidence_card block found")


def section_text(text: str, section: str) -> str:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if re.match(rf"^{re.escape(section)}\s*:", line):
            start = index
            break
    if start is None:
        return ""
    collected: list[str] = []
    for line in lines[start + 1 :]:
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*:", line):
            break
        collected.append(line)
    return "\n".join(collected)


def section_has_key(section: str, key: str) -> bool:
    return re.search(rf"(?m)^\s+{re.escape(key)}\s*:", section) is not None


def section_value(section: str, key: str) -> str:
    match = re.search(rf"(?m)^\s+{re.escape(key)}\s*:\s*(.*)$", section)
    return normalize(match.group(1)) if match else ""


def value_is_empty(value: str) -> bool:
    return value.lower() in {"", "[]", "none", "null", "n/a", "not applicable"}


def validate(path: Path) -> list[str]:
    try:
        text = extract_structured_text(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [str(exc)]

    errors: list[str] = []
    route = section_text(text, "route_card")
    evidence = section_text(text, "evidence_card")
    if not route:
        errors.append("missing route_card")
    if not evidence:
        errors.append("missing evidence_card")
    if errors:
        return errors

    missing_route = [key for key in ROUTE_FIELDS if not section_has_key(route, key)]
    missing_evidence = [key for key in EVIDENCE_FIELDS if not section_has_key(evidence, key)]
    if missing_route:
        errors.append("route_card missing fields: " + ", ".join(missing_route))
    if missing_evidence:
        errors.append("evidence_card missing fields: " + ", ".join(missing_evidence))

    route_value = section_value(route, "route")
    if route_value and route_value not in ROUTES:
        errors.append(f"invalid route_card.route: {route_value}")

    claim = section_value(evidence, "claim_ceiling")
    if claim and claim not in CLAIM_LEVELS:
        errors.append(f"invalid evidence_card.claim_ceiling: {claim}")

    for key in ["changed_surfaces", "required_gates", "stop_gates"]:
        value = section_value(route, key)
        if value_is_empty(value):
            errors.append(f"route_card.{key} must state a value, even if minimal")

    if route_value not in {"Tiny", ""} and value_is_empty(section_value(evidence, "post_implementation")):
        errors.append("non-Tiny route requires post_implementation evidence")

    if claim == "Integration Done":
        chain = section_value(evidence, "chain").lower()
        if not any(token in chain for token in ["integration", "e2e", "smoke", "browser", "system"]):
            errors.append("Integration Done requires chain evidence in evidence_card.chain")

    if claim == "Handoff Done":
        handoff = section_value(evidence, "handoff").lower()
        if not any(token in handoff for token in ["fresh consumer", "real external"]):
            errors.append("Handoff Done requires fresh consumer or real external evidence in evidence_card.handoff")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cards", help="Path to yaml or Markdown containing route_card/evidence_card")
    args = parser.parse_args()

    path = Path(args.cards)
    if not path.exists():
        raise SystemExit(f"missing workflow cards: {path}")

    errors = validate(path)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    print(f"Workflow cards valid: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
