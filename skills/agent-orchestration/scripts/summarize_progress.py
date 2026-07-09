#!/usr/bin/env python3
"""Summarize work order and work result progress."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _json_contract import load_json


def read_json_dir(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [load_json(item) for item in sorted(path.glob("*.json"))]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-orders", required=True)
    parser.add_argument("--results", required=True)
    args = parser.parse_args()

    orders = read_json_dir(Path(args.work_orders))
    results = read_json_dir(Path(args.results))
    results_by_order = {result["work_order_id"]: result for result in results}
    summary = {
        "schema_version": 1,
        "work_orders_total": len(orders),
        "results_total": len(results),
        "by_status": {},
        "blocked": [],
        "missing_results": [],
    }
    for order in orders:
        result = results_by_order.get(order["work_order_id"])
        status = result["status"] if result else "missing_result"
        summary["by_status"][status] = summary["by_status"].get(status, 0) + 1
        if not result:
            summary["missing_results"].append(order["work_order_id"])
        elif status in {"blocked", "failed", "needs_human"}:
            summary["blocked"].append({"work_order_id": order["work_order_id"], "error": result.get("error")})
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if summary["blocked"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
