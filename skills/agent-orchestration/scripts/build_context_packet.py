#!/usr/bin/env python3
"""Build a role-scoped context_packet.json from a small artifact index."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from _json_contract import load_json, write_json
from validate_context_packet import validate


def artifact_ref(artifact: dict[str, Any]) -> dict[str, str]:
    return {
        "artifact_id": artifact["id"],
        "type": artifact["type"],
        "path": artifact["path"],
        "status": artifact["status"],
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    index_path = Path(args.artifact_index)
    index = load_json(index_path)
    by_id = {artifact["id"]: artifact for artifact in index.get("artifacts", [])}
    missing = [artifact_id for artifact_id in args.include_artifact if artifact_id not in by_id]
    if missing:
        raise SystemExit("FAIL: unknown artifact ids: " + ", ".join(missing))
    packet = {
        "schema_version": 1,
        "context_packet_id": args.context_packet_id,
        "coordination_id": index["coordination_id"],
        "packet_kind": args.packet_kind,
        "role": args.role,
        "purpose": args.purpose,
        "artifact_refs": [artifact_ref(by_id[artifact_id]) for artifact_id in args.include_artifact],
        "allowed_paths": args.allowed_path,
        "forbidden_paths": args.forbidden_path,
        "instructions": args.instruction,
        "omissions": args.omission,
        "created_from": {
            "artifact_index": index_path.as_posix(),
            "index_revision": index.get("index_revision", 1),
        },
    }
    if args.review_acceptance_ref or args.review_target_ref or args.review_evidence_ref:
        packet["review_contract"] = {
            "acceptance_refs": args.review_acceptance_ref,
            "target_refs": args.review_target_ref,
            "evidence_refs": args.review_evidence_ref,
        }
    return packet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_index")
    parser.add_argument("--role", required=True)
    parser.add_argument("--packet-kind", choices=["task", "review", "verification"], default="task")
    parser.add_argument("--context-packet-id", required=True)
    parser.add_argument("--purpose", default="Provide role-scoped context for the assigned work order.")
    parser.add_argument("--include-artifact", action="append", default=[])
    parser.add_argument("--allowed-path", action="append", default=[])
    parser.add_argument("--forbidden-path", action="append", default=[])
    parser.add_argument("--instruction", action="append", default=["Use only the provided artifact refs and paths needed for this role."])
    parser.add_argument("--omission", action="append", default=["Full conversation history intentionally omitted."])
    parser.add_argument("--review-acceptance-ref", action="append", default=[])
    parser.add_argument("--review-target-ref", action="append", default=[])
    parser.add_argument("--review-evidence-ref", action="append", default=[])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    packet = build(args)
    output = Path(args.output)
    write_json(output, packet)
    errors = validate(output)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"Context packet written: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
