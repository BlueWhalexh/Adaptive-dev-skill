#!/usr/bin/env python3
"""Create a learning_candidate.json file in a reviewable location."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,80}$")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True)
    parser.add_argument("--out-dir", default=".agent/knowledge/candidates")
    parser.add_argument("--source", required=True)
    parser.add_argument("--problem", required=True)
    parser.add_argument("--pattern", required=True)
    parser.add_argument("--promotion-target", default="project_skill")
    args = parser.parse_args()

    if not SAFE_ID.match(args.id):
        raise SystemExit(f"unsafe id: {args.id}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{args.id}.json"
    data = {
        "id": args.id,
        "source": args.source,
        "problem": args.problem,
        "pattern": args.pattern,
        "promotion_target": args.promotion_target,
        "status": "candidate",
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
