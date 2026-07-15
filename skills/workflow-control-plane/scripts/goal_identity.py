#!/usr/bin/env python3
"""Build a stable identity for exact workflow resume matching."""

from __future__ import annotations

import argparse
import hashlib
import json
import re


SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,80}$")


def normalize_summary(value: str) -> str:
    return " ".join(value.split()).strip().casefold()


def build_goal_identity(goal_id: str, summary: str) -> dict[str, str]:
    if not SAFE_ID.fullmatch(goal_id):
        raise ValueError("goal_id must be a safe stable id")
    normalized = normalize_summary(summary)
    if not normalized:
        raise ValueError("goal_summary must be non-empty")
    canonical = json.dumps(
        {"goal_id": goal_id, "normalized_summary": normalized},
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return {
        "goal_id": goal_id,
        "summary": " ".join(summary.split()).strip(),
        "fingerprint": "sha256:" + hashlib.sha256(canonical).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--goal-id", required=True)
    parser.add_argument("--goal-summary", required=True)
    args = parser.parse_args()
    try:
        identity = build_goal_identity(args.goal_id, args.goal_summary)
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 1
    print(json.dumps(identity, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
