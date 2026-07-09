#!/usr/bin/env python3
"""Create a role-scoped work_order.json."""

from __future__ import annotations

import argparse
from pathlib import Path

from _json_contract import load_json, write_json
from validate_work_order import validate


def choose_agent(roster_path: Path | None, role: str) -> str | None:
    if not roster_path:
        return None
    roster = load_json(roster_path)
    for agent in roster.get("agents", []):
        if agent["role"] == role and agent["status"] == "active":
            return agent["agent_id"]
    return None


def build(args: argparse.Namespace) -> dict:
    packet = load_json(Path(args.context_packet))
    if packet["role"] != args.role:
        raise SystemExit("FAIL: context packet role does not match requested role")
    if packet["workflow_id"] != args.workflow_id:
        raise SystemExit("FAIL: context packet workflow_id does not match requested workflow_id")
    assigned = choose_agent(Path(args.agent_roster) if args.agent_roster else None, args.role)
    order = {
        "schema_version": 1,
        "work_order_id": args.work_order_id,
        "workflow_id": args.workflow_id,
        "role": args.role,
        "objective": args.objective,
        "stage_id": args.stage_id,
        "status": "assigned" if assigned else "queued",
        "context_packet_ref": packet["context_packet_id"],
        "execution_carrier": args.execution_carrier,
        "context_isolation": args.context_isolation,
        "workspace_policy": args.workspace_policy,
        "input_artifacts": [artifact["artifact_id"] for artifact in packet.get("artifact_refs", [])],
        "output_contract": {
            "artifact_type": args.output_artifact_type,
            "schema_ref": args.output_schema_ref,
            "path": args.output_artifact_path,
        },
        "forbidden_actions": args.forbidden_action,
        "expected_result_schema": "work-result.schema.json",
        "dependencies": args.dependency,
    }
    if assigned:
        order["assigned_agent_id"] = assigned
    if args.worktree_ref:
        order["worktree_ref"] = args.worktree_ref
    if args.merge_owner:
        order["merge_owner"] = args.merge_owner
    return order


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow-id", required=True)
    parser.add_argument("--work-order-id", default="WO-001")
    parser.add_argument("--role", required=True)
    parser.add_argument("--stage-id", required=True)
    parser.add_argument("--context-packet", required=True)
    parser.add_argument("--agent-roster")
    parser.add_argument("--execution-carrier", choices=["main_session", "subagent", "separate_session", "human", "external"], default="main_session")
    parser.add_argument("--context-isolation", choices=["none", "role_contract_only", "fresh_context"], default="role_contract_only")
    parser.add_argument("--workspace-policy", choices=["shared_readonly", "shared_writer", "isolated_worktree"], default="shared_readonly")
    parser.add_argument("--worktree-ref", default="")
    parser.add_argument("--merge-owner", default="main_agent")
    parser.add_argument("--objective", required=True)
    parser.add_argument("--output-artifact-type", required=True)
    parser.add_argument("--output-schema-ref", default="")
    parser.add_argument("--output-artifact-path", required=True)
    parser.add_argument("--forbidden-action", action="append", default=["Do not mutate workflow_manifest.json directly.", "Do not use full chat history as context."])
    parser.add_argument("--dependency", action="append", default=[])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    order = build(args)
    output = Path(args.output)
    write_json(output, order)
    errors = validate(output, roster_path=Path(args.agent_roster) if args.agent_roster else None, context_packet_path=Path(args.context_packet))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"Work order written: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
