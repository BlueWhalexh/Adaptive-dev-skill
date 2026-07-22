#!/usr/bin/env python3
"""Validate context_packet.json."""

from __future__ import annotations

import argparse
from pathlib import Path

from _json_contract import load_json, validate_contract


SKILL_DIR = Path(__file__).resolve().parents[1]
SCHEMA = SKILL_DIR / "schemas" / "context-packet.schema.json"


def validate(path: Path) -> list[str]:
    packet = load_json(path)
    errors = validate_contract(packet, SCHEMA)
    if not packet.get("purpose", "").strip():
        errors.append("purpose must be non-empty")
    if not packet.get("instructions"):
        errors.append("instructions must state how the role should use this context")
    if "full chat" in " ".join(packet.get("instructions", []) + packet.get("omissions", [])).lower():
        errors.append("context packet must not include or request full chat history")
    if packet.get("packet_kind") == "review":
        contract = packet.get("review_contract")
        if not contract:
            errors.append("reviewer context requires review_contract")
        else:
            for key in ["acceptance_refs", "target_refs", "evidence_refs"]:
                refs = contract.get(key, [])
                if not refs or any(not isinstance(ref, str) or not ref.strip() for ref in refs):
                    errors.append(f"review_contract {key} must contain non-empty refs")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("context_packet")
    args = parser.parse_args()
    errors = validate(Path(args.context_packet))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"Context packet valid: {args.context_packet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
