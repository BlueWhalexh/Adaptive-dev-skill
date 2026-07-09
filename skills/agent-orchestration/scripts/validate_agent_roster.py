#!/usr/bin/env python3
"""Validate agent_roster.json."""

from __future__ import annotations

import argparse
from pathlib import Path

from _json_contract import load_json, validate_contract


SKILL_DIR = Path(__file__).resolve().parents[1]
SCHEMA = SKILL_DIR / "schemas" / "agent-roster.schema.json"


def validate(path: Path) -> list[str]:
    errors = validate_contract(load_json(path), SCHEMA)
    roster = load_json(path)
    seen: set[str] = set()
    roles: set[str] = set()
    for agent in roster.get("agents", []):
        agent_id = agent.get("agent_id", "")
        if agent_id in seen:
            errors.append(f"duplicate agent_id: {agent_id}")
        seen.add(agent_id)
        roles.add(agent.get("role", ""))
        if agent.get("max_parallel_work_orders", 0) < 1:
            errors.append(f"{agent_id}: max_parallel_work_orders must be >= 1")
    if not roles:
        errors.append("agent roster must contain at least one role")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("agent_roster")
    args = parser.parse_args()
    errors = validate(Path(args.agent_roster))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"Agent roster valid: {args.agent_roster}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
