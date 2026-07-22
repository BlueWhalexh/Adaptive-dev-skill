#!/usr/bin/env python3
"""Validate work_order.json, optionally against roster/context packet."""

from __future__ import annotations

import argparse
from pathlib import Path

from _json_contract import load_json, validate_contract


SKILL_DIR = Path(__file__).resolve().parents[1]
SCHEMA = SKILL_DIR / "schemas" / "work-order.schema.json"
FRESH_CONTEXT_CARRIERS = {"subagent", "separate_session", "external"}
REVIEW_ROLES = {"spec_reviewer", "technical_design_reviewer", "plan_reviewer", "code_reviewer", "test_strategy_reviewer", "evidence_reviewer", "security_data_reviewer", "verifier"}


def validate(path: Path, *, roster_path: Path | None = None, context_packet_path: Path | None = None) -> list[str]:
    order = load_json(path)
    errors = validate_contract(order, SCHEMA)
    if not order.get("objective", "").strip():
        errors.append("objective must be non-empty")
    if order.get("expected_result_schema") != "work-result.schema.json":
        errors.append("expected_result_schema must be work-result.schema.json")
    execution_carrier = order.get("execution_carrier")
    context_isolation = order.get("context_isolation")
    workspace_policy = order.get("workspace_policy")
    role = order.get("role", "")
    if context_isolation == "fresh_context" and execution_carrier not in FRESH_CONTEXT_CARRIERS:
        errors.append("fresh_context requires execution_carrier subagent, separate_session, or external")
    if execution_carrier == "main_session" and context_isolation not in {"none", "role_contract_only"}:
        errors.append("main_session work orders cannot claim fresh_context isolation")
    if workspace_policy == "shared_writer" and execution_carrier != "main_session":
        errors.append("non-main execution carriers must not use shared_writer; use isolated_worktree for write work")
    if workspace_policy == "isolated_worktree" and not order.get("worktree_ref"):
        errors.append("isolated_worktree requires worktree_ref")
    if workspace_policy in {"shared_writer", "isolated_worktree"} and not order.get("merge_owner"):
        errors.append("writer workspace policies require merge_owner")
    if role in REVIEW_ROLES and workspace_policy != "shared_readonly":
        errors.append(f"review/verifier role must use shared_readonly workspace_policy: {role}")

    if context_packet_path:
        packet = load_json(context_packet_path)
        if packet["coordination_id"] != order["coordination_id"]:
            errors.append("context packet coordination_id must match work order")
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
