#!/usr/bin/env python3
"""Validate work_order.json, optionally against roster/context packet."""

from __future__ import annotations

import argparse
from pathlib import Path

from _json_contract import load_json, validate_contract


SKILL_DIR = Path(__file__).resolve().parents[1]
SCHEMA = SKILL_DIR / "schemas" / "work-order.schema.json"


def validate(path: Path, *, roster_path: Path | None = None, context_packet_path: Path | None = None) -> list[str]:
    order = load_json(path)
    errors = validate_contract(order, SCHEMA)
    if not order.get("objective", "").strip():
        errors.append("objective must be non-empty")
    if order["expected_result_schema"] != "work-result.schema.json":
        errors.append("expected_result_schema must be work-result.schema.json")

    if context_packet_path:
        packet = load_json(context_packet_path)
        if packet["workflow_id"] != order["workflow_id"]:
            errors.append("context packet workflow_id must match work order")
        if packet["role"] != order["role"]:
            errors.append("context packet role must match work order")

    if roster_path:
        roster = load_json(roster_path)
        active_roles = {agent["role"] for agent in roster.get("agents", []) if agent["status"] == "active"}
        if order["role"] not in active_roles:
            errors.append(f"work order role has no active roster agent: {order['role']}")
        assigned = order.get("assigned_agent_id")
        if assigned:
            matched = [agent for agent in roster.get("agents", []) if agent["agent_id"] == assigned and agent["role"] == order["role"] and agent["status"] == "active"]
            if not matched:
                errors.append(f"assigned_agent_id is not active for role {order['role']}: {assigned}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_order")
    parser.add_argument("--agent-roster")
    parser.add_argument("--context-packet")
    args = parser.parse_args()
    errors = validate(
        Path(args.work_order),
        roster_path=Path(args.agent_roster) if args.agent_roster else None,
        context_packet_path=Path(args.context_packet) if args.context_packet else None,
    )
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"Work order valid: {args.work_order}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
